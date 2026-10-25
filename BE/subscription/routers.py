from fastapi import APIRouter, Request, HTTPException, Header, Depends
import stripe
from config_project.config import settings
from users.repository import update_user_tier
from users.model import Tier, User
from subscription.repository import create_or_update_subscription, get_subscription_by_user_id, update_subscription_status, update_subscription_end_date, get_expired_subscriptions
from users.utils import get_current_user
from datetime import datetime
from config_project.information_gathering.utils import send_email, get_payment_failed_email_content, get_tier_from_price_id


router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/create-checkout-session")
async def create_checkout_session(request: Request, current_user: User = Depends(get_current_user)):
    data = await request.json()
    try:
        mode = 'subscription'
        
        session_data = {
            'payment_method_types': ['card'],
            'mode': mode,
            'metadata': {
                'customer_email': current_user.email
            },
            'line_items': [{
                'price': data['price_id'],
                'quantity': 1,
            }],
            'success_url': data['success_url'] + '?session_id={CHECKOUT_SESSION_ID}',   
            'cancel_url': data['cancel_url'],
        }
        
        # Add subscription-specific metadata for subscription mode
        if mode == 'subscription':
            session_data['subscription_data'] = {
                'metadata': {
                    'customer_email': current_user.email
                }
            } 
        
        session = stripe.checkout.Session.create(**session_data)
        return {
            "url": session.url,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
            subscription_id = sub_item_details.get("subscription")

            pricing = line.get("pricing") or {}
            price_details = pricing.get("price_details") or {}
            price_id = price_details.get("price")

            amount = invoice.get("amount_paid")
            
            payment_settings = invoice.get("payment_settings", {})
            payment_method_types = payment_settings.get("payment_method_types", [])
            payment_method = payment_method_types[0] if payment_method_types else None

            customer_email = line.get("metadata", {}).get("customer_email")

            if not customer_email and subscription_id:
                subscription = stripe.Subscription.retrieve(subscription_id)
                customer_email = subscription.get("metadata", {}).get("customer_email")

            if not all([customer_email, subscription_id, price_id]):
                print(f"[WARNING] Missing required data: email={customer_email}, subscription_id={subscription_id}, price_id={price_id}")
                return

            try:
                price_obj = stripe.Price.retrieve(price_id)
                interval = price_obj.get("recurring", {}).get("interval")
            except Exception as e:
                interval = None
            
            period_end_timestamp = line.get("period", {}).get("end")
            period_end = datetime.fromtimestamp(period_end_timestamp) if period_end_timestamp else None
            
            tier = get_tier_from_price_id(price_id)

            # set status from Stripe
            try:
                stripe_subscription = stripe.Subscription.retrieve(subscription_id)
                status = stripe_subscription.get("status", "active")
            except Exception as e:
                print(f"[ERROR] Failed to retrieve Stripe subscription: {e}")
                status = None

            update_user_tier(customer_email, tier, is_subscribed=True)
            print(f"[INFO] User tier updated: {customer_email} -> {tier.value}")

            create_or_update_subscription(
                user_email=customer_email,
                stripe_subscription_id=subscription_id,
                status=status,
                payment_method=payment_method,
                amount=amount,
                interval=interval,
                period_end=period_end
            )
            print(f"[INFO] Subscription renewal saved for {customer_email}")

        except Exception as e:
            print(f"[ERROR] Failed to process invoice.payment_succeeded: {e}")
    
    # Handle payment failures and retries
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        subscription_id = invoice.get('subscription')
        customer_email = None

        if subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(subscription_id)
                customer_email = subscription.get('metadata', {}).get('customer_email')
                if customer_email:
                    update_user_tier(customer_email, Tier.FREE, is_subscribed=False)
                    
                    subject, message = get_payment_failed_email_content(customer_email)
                    try:
                        send_email(customer_email, subject, message)
                    except Exception as e:
                        print(f"Failed to send payment failure email: {e}")
                else:
                    print(f"[WARNING] Missing customer_email for payment failure")
            except Exception as e:
                print(f"Error handling payment failure: {e}")
        else:
            customer_email = invoice.get('metadata', {}).get('customer_email')
            if customer_email:
                update_user_tier(customer_email, Tier.FREE, is_subscribed=False)
                subject, message = get_payment_failed_email_content(customer_email)
                try:
                    send_email(customer_email, subject, message)
                except Exception as e:
                    print(f"Failed to send payment failure email: {e}")
            else:
                print(f"[WARNING] No subscription_id or customer_email in metadata found in invoice")
                
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        customer_email = subscription.get('metadata', {}).get('customer_email')
        
        # Check if subscription was cancelled
        if subscription.get('cancel_at_period_end') and subscription.get('canceled_at'):
            if customer_email:
                cancel_at = subscription.get('cancel_at', 0)
                end_date = datetime.fromtimestamp(cancel_at)
                
                update_subscription_end_date(customer_email, end_date)
                print(f"[INFO] Subscription cancelled for {customer_email} - end date stored: {end_date}")
            else:
                print(f"[WARNING] Missing customer_email for subscription cancellation")
                
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_email = subscription.get('metadata', {}).get('customer_email')
        
        if customer_email:
            update_user_tier(customer_email, Tier.FREE, is_subscribed=False)
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
        
        if subscription.status == "cancelled":
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

