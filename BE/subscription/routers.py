from fastapi import APIRouter, Request, HTTPException, Header, Depends
import stripe
from config_project.config import settings
from users.repository import update_user_tier
from users.model import Tier, User
from subscription.repository import create_or_update_subscription, get_subscription_by_user_id, get_subscription_by_user_email, update_subscription_status, update_subscription_end_date, get_expired_subscriptions
from users.utils import get_current_user
from datetime import datetime, timezone
from config_project.information_gathering.utils import send_email, get_payment_failed_email_content, get_tier_from_price_id


router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY

# Local "cancelled" (set by /cancel-subscription) plus Stripe's own terminal statuses
ENDED_STATUSES = {"cancelled", "canceled", "incomplete_expired"}

# Used to allow upgrades only (PRO -> PREMIUM)
TIER_RANK = {Tier.FREE: 0, Tier.PRO: 1, Tier.PREMIUM: 2}


def timestamp_to_datetime(timestamp):
    """Stripe timestamps are UTC seconds; None/0 means 'not set'"""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else None


def get_invoice_subscription_id(invoice):
    """Newer Stripe API versions moved invoice.subscription under invoice.parent"""
    parent = invoice.get("parent") or {}
    subscription_details = parent.get("subscription_details") or {}
    return invoice.get("subscription") or subscription_details.get("subscription")


def get_subscription_period_end(subscription):
    """current_period_end lives on the subscription in older API versions and on its items in newer ones"""
    items = (subscription.get("items") or {}).get("data") or []
    return subscription.get("current_period_end") or (items[0].get("current_period_end") if items else None)


def is_current_subscription(customer_email: str, stripe_subscription_id: str) -> bool:
    """
    True if the event's subscription is the one we currently track for this user.
    Events for an older subscription (e.g. one that was cancelled before the user
    resubscribed) must not change the user's tier or end date.
    """
    subscription = get_subscription_by_user_email(customer_email)
    if not subscription or not subscription.stripe_subscription_id or not stripe_subscription_id:
        return True
    return subscription.stripe_subscription_id == stripe_subscription_id


@router.post("/create-checkout-session")
async def create_checkout_session(request: Request, current_user: User = Depends(get_current_user)):
    data = await request.json()
    price_id = data.get("price_id")
    success_url = data.get("success_url")
    cancel_url = data.get("cancel_url")

    if get_tier_from_price_id(price_id) == Tier.FREE:
        raise HTTPException(status_code=400, detail="Invalid plan selected")
    if not settings.is_allowed_redirect(success_url) or not settings.is_allowed_redirect(cancel_url):
        raise HTTPException(status_code=400, detail="Invalid redirect URL")

    existing = get_subscription_by_user_id(current_user.id)
    if (
        current_user.is_subscribed
        and existing
        and existing.stripe_subscription_id
        and existing.status not in ENDED_STATUSES
    ):
        raise HTTPException(
            status_code=400,
            detail="You already have an active subscription. Upgrade it or cancel it before purchasing a new plan.",
        )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            metadata={'customer_email': current_user.email},
            line_items=[{'price': price_id, 'quantity': 1}],
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            subscription_data={'metadata': {'customer_email': current_user.email}},
        )
        return {
            "url": session.url,
        }
    except stripe.error.StripeError as e:
        print(f"[ERROR] Failed to create checkout session: {e}")
        raise HTTPException(status_code=400, detail="Could not start checkout. Please try again.")


@router.post("/change-plan")
async def change_plan(request: Request, current_user: User = Depends(get_current_user)):
    """
    Upgrade the user's existing subscription to a higher plan (e.g. PRO -> PREMIUM).
    The prorated difference is invoiced immediately; the tier and message allowance
    are updated by the invoice.payment_succeeded webhook.
    """
    data = await request.json()
    new_price_id = data.get("price_id")
    new_tier = get_tier_from_price_id(new_price_id)
    if new_tier == Tier.FREE:
        raise HTTPException(status_code=400, detail="Invalid plan selected")

    subscription = get_subscription_by_user_id(current_user.id)
    if (
        not current_user.is_subscribed
        or not subscription
        or not subscription.stripe_subscription_id
        or subscription.status in ENDED_STATUSES
    ):
        raise HTTPException(status_code=400, detail="You don't have an active subscription to upgrade")
    if TIER_RANK[new_tier] <= TIER_RANK.get(current_user.tier, 0):
        raise HTTPException(status_code=400, detail="Only upgrades to a higher plan are supported")

    try:
        stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
        item_id = stripe_subscription["items"]["data"][0]["id"]
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            items=[{"id": item_id, "price": new_price_id}],
            proration_behavior="always_invoice",
            # Fail the request instead of upgrading if the prorated payment is declined
            payment_behavior="error_if_incomplete",
        )
    except stripe.error.CardError as e:
        raise HTTPException(status_code=402, detail=e.user_message or "Your card was declined")
    except stripe.error.StripeError as e:
        print(f"[ERROR] Failed to change plan for {current_user.email}: {e}")
        raise HTTPException(status_code=502, detail="Could not change your plan. Please try again.")

    return {"message": "Your plan has been upgraded. The new message allowance will be available shortly."}


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")
    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        customer_email = None

        try:
            line_items = invoice.get("lines", {}).get("data", [])
            if not line_items:
                print("[WARNING] No line items in invoice")
                return

            line = line_items[0]

            parent = line.get("parent") or {}
            sub_item_details = parent.get("subscription_item_details") or {}
            subscription_id = sub_item_details.get("subscription") or get_invoice_subscription_id(invoice)

            pricing = line.get("pricing") or {}
            price_details = pricing.get("price_details") or {}
            price_id = price_details.get("price")

            amount = invoice.get("amount_paid")

            payment_settings = invoice.get("payment_settings", {})
            payment_method_types = payment_settings.get("payment_method_types", [])
            payment_method = payment_method_types[0] if payment_method_types else None

            customer_email = line.get("metadata", {}).get("customer_email")
            period_end_timestamp = line.get("period", {}).get("end")

            # Read plan, status and period from the subscription itself: after a plan change the
            # first invoice line can be the proration credit for the *old* price
            status = None
            if subscription_id:
                try:
                    stripe_subscription = stripe.Subscription.retrieve(subscription_id)
                    customer_email = customer_email or stripe_subscription.get("metadata", {}).get("customer_email")
                    status = stripe_subscription.get("status", "active")
                    if stripe_subscription.get("cancel_at_period_end") or stripe_subscription.get("cancel_at"):
                        status = "cancelled"
                    sub_items = (stripe_subscription.get("items") or {}).get("data") or []
                    if sub_items:
                        price_id = (sub_items[0].get("price") or {}).get("id") or price_id
                    period_end_timestamp = get_subscription_period_end(stripe_subscription) or period_end_timestamp
                except Exception as e:
                    print(f"[ERROR] Failed to retrieve Stripe subscription: {e}")

            if not all([customer_email, subscription_id, price_id]):
                print(f"[WARNING] Missing required data: email={customer_email}, subscription_id={subscription_id}, price_id={price_id}")
                return

            try:
                price_obj = stripe.Price.retrieve(price_id)
                interval = price_obj.get("recurring", {}).get("interval")
            except Exception as e:
                interval = None

            period_end = timestamp_to_datetime(period_end_timestamp)

            tier = get_tier_from_price_id(price_id)

            update_user_tier(customer_email, tier, is_subscribed=True)
            print(f"[INFO] User tier updated: {customer_email} -> {tier.value}")

            create_or_update_subscription(
                user_email=customer_email,
                stripe_subscription_id=subscription_id,
                status=status or "active",
                payment_method=payment_method,
                amount=amount,
                interval=interval,
                period_end=period_end
            )
            print(f"[INFO] Subscription renewal saved for {customer_email}")

        except Exception as e:
            print(f"[ERROR] Failed to process invoice.payment_succeeded: {e}")

    # Payment failures: Stripe retries automatically, so the user keeps access for now.
    # If all retries fail, Stripe cancels the subscription and customer.subscription.deleted downgrades the user.
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        subscription_id = get_invoice_subscription_id(invoice)
        customer_email = (invoice.get('metadata') or {}).get('customer_email')

        if subscription_id and not customer_email:
            try:
                subscription = stripe.Subscription.retrieve(subscription_id)
                customer_email = subscription.get('metadata', {}).get('customer_email')
            except Exception as e:
                print(f"[ERROR] Failed to retrieve subscription for payment failure: {e}")

        if not customer_email:
            print(f"[WARNING] Missing customer_email for payment failure (subscription_id={subscription_id})")
        elif subscription_id and not is_current_subscription(customer_email, subscription_id):
            print(f"[INFO] Ignoring payment failure for old subscription {subscription_id} ({customer_email})")
        else:
            subject, message = get_payment_failed_email_content(customer_email)
            try:
                send_email(customer_email, subject, message)
            except Exception as e:
                print(f"Failed to send payment failure email: {e}")

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        subscription_id = subscription.get('id')
        customer_email = subscription.get('metadata', {}).get('customer_email')

        if not customer_email:
            print(f"[WARNING] Missing customer_email for subscription update")
        elif not is_current_subscription(customer_email, subscription_id):
            print(f"[INFO] Ignoring update of old subscription {subscription_id} ({customer_email})")
        elif subscription.get('cancel_at_period_end') or subscription.get('cancel_at'):
            # Cancelled from our app or from Stripe (dashboard / customer portal): access ends at period end
            end_date = timestamp_to_datetime(subscription.get('cancel_at') or get_subscription_period_end(subscription))
            existing = get_subscription_by_user_email(customer_email)
            if existing:
                update_subscription_status(existing.user_id, "cancelled")
            if end_date:
                update_subscription_end_date(customer_email, end_date)
            print(f"[INFO] Subscription cancelled for {customer_email} - end date stored: {end_date}")
        else:
            # Not (or no longer) cancelled, e.g. the cancellation was undone: mirror Stripe's status
            existing = get_subscription_by_user_email(customer_email)
            if existing and existing.status == "cancelled":
                update_subscription_status(existing.user_id, subscription.get('status', 'active'))
                update_subscription_end_date(customer_email, timestamp_to_datetime(get_subscription_period_end(subscription)))
                print(f"[INFO] Subscription reactivated for {customer_email}")

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_email = subscription.get('metadata', {}).get('customer_email')

        if customer_email and not is_current_subscription(customer_email, subscription.get('id')):
            print(f"[INFO] Ignoring deletion of old subscription {subscription.get('id')} ({customer_email})")
        elif customer_email:
            update_user_tier(customer_email, Tier.FREE, is_subscribed=False)
            existing = get_subscription_by_user_email(customer_email)
            if existing:
                update_subscription_status(existing.user_id, "canceled")
        else:
            print(f"[WARNING] Missing customer_email for subscription deletion")

@router.get("/success")
async def success(session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id, expand=["subscription"])
        subscription = session.subscription
        response_data = {
            "success": True if subscription.status == "active" and getattr(session, "payment_status", None) == "paid" else False,
            "subscription_status": subscription.status,
            "payment_method": session.payment_method_types[0] if hasattr(session, "payment_method_types") and session.payment_method_types else None,
            "amount": getattr(session, "amount_total", None),
            "payment_status": getattr(session, "payment_status", None)
        }
        return response_data

    except Exception as e:
        return {"success": False, "error": str(e)}
    
@router.get("/billing-details")
async def get_billing_details(current_user: User = Depends(get_current_user)):
    subscription = get_subscription_by_user_id(current_user.id)
    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription")

    try:
        stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
        items = stripe_subscription.get("items", {}).get("data", [])

        customer_id = stripe_subscription["customer"]
        invoices = stripe.Invoice.list(customer=customer_id, limit=100)
        paid_invoices = [inv for inv in invoices["data"] if inv["status"] == "paid"]
        paid_invoices.sort(key=lambda x: x["created"], reverse=True)

        if not paid_invoices:
            return {"latest_paid_invoice": None}

        latest = paid_invoices[0]

        payment_method_details = "-"
        payment_method_id = None

        if latest.get("payment_method"):
            payment_method_id = latest["payment_method"]
        elif stripe_subscription.get("default_payment_method"):
            payment_method_id = stripe_subscription["default_payment_method"]

        if payment_method_id:
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            if payment_method["type"] == "card":
                card = payment_method["card"]
                payment_method_details = f"{card['brand'].title()} •••• {card['last4']}"
            else:
                payment_method_details = payment_method["type"]

        next_billing_date = stripe_subscription.get("current_period_end")
        if not next_billing_date and items and len(items) > 0:
            next_billing_date = items[0].get("current_period_end")

        latest_invoice = {
            "invoice_number": latest.get("number"),
            "amount_paid": latest["amount_paid"],
            "currency": latest["currency"],
            "status": latest["status"],
            "description": latest["lines"]["data"][0]["description"] if latest["lines"]["data"] else None,
            "payment_method": payment_method_details,
            "paid_at": latest["status_transitions"].get("paid_at"),
            "next_billing_date": next_billing_date,
        }
        return {"latest_paid_invoice": latest_invoice}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/cancel-subscription")
async def cancel_subscription(current_user=Depends(get_current_user)):
    try:
        subscription = get_subscription_by_user_id(current_user.id)
        if not subscription or not subscription.stripe_subscription_id:
            raise HTTPException(status_code=404, detail="No active subscription")
        
        if subscription.status in ENDED_STATUSES:
            return {
                "message": "Subscription is already cancelled and will end at the end of the billing period.",
                "status": "already_cancelled",
            }
            
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True  
        )
        update_subscription_status(current_user.id, "cancelled")

        return {
            "message": "Subscription will be canceled at the end of the billing period.",
            "status": "cancelled",
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/subscription/status", response_model=dict)
async def get_subscription_status(current_user=Depends(get_current_user)):
    subscription = get_subscription_by_user_id(current_user.id)
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription")
    return {"status": subscription.status}

