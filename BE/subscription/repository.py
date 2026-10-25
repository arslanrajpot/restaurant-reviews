from database import SessionLocal
from subscription.model import Subscription
from users.repository import get_user_by_email
import uuid
from datetime import datetime

def create_or_update_subscription(user_email: str, stripe_subscription_id: str, status: str, payment_method: str = None, amount: int = None, interval: str = None, period_end: datetime = None):
    db = SessionLocal()
    try:
        user = get_user_by_email(user_email)
        if not user:
            raise ValueError(f"User with email {user_email} not found")
        subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if subscription:
            subscription.stripe_subscription_id = stripe_subscription_id
            subscription.status = status
            subscription.payment_method = payment_method
            subscription.amount = amount
            subscription.interval = interval
            subscription.end_date = period_end
            db.commit()
            db.refresh(subscription)
            return subscription
        else:
            subscription = Subscription(
                user_id=user.id,
                stripe_subscription_id=stripe_subscription_id,
                status=status,
                payment_method=payment_method,
                amount=amount,
                interval=interval,
                end_date=period_end
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            return subscription
    finally:
        db.close()

def get_subscription_by_user_id(user_id: uuid.UUID):
    db = SessionLocal()
    try:
        return db.query(Subscription).filter(Subscription.user_id == user_id).first()
    finally:
        db.close()

def get_subscription_by_user_email(user_email: str):
    db = SessionLocal()
    try:
        user = get_user_by_email(user_email)
        if not user:
            return None
        return db.query(Subscription).filter(Subscription.user_id == user.id).first()
    finally:
        db.close()        
        
def update_subscription_status(user_id, new_status):
    db = SessionLocal()
    try:
        subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
        if subscription:
            subscription.status = new_status
            db.commit()
            db.refresh(subscription)
            return subscription
        return None
    finally:
        db.close()

def update_subscription_end_date(user_email: str, end_date):
    """Update subscription end date"""
    db = SessionLocal()
    try:
        user = get_user_by_email(user_email)
        if not user:
            return None
        subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if subscription:
            subscription.end_date = end_date
            db.commit()
            db.refresh(subscription)
            return subscription
        return None
    finally:
        db.close()

def get_expired_subscriptions():
    """Get all subscriptions that have passed their end date"""
    db = SessionLocal()
    try:
        current_time = datetime.utcnow()
        return db.query(Subscription).filter(
            Subscription.end_date <= current_time,
            Subscription.status == "cancelled"
        ).all()
    finally:
        db.close()