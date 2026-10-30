from typing import Optional
from sqlalchemy import update, func, or_
from database import SessionLocal
from users.model import User
from datetime import datetime
from users.model import Tier

TIER_MESSAGE_LIMITS = {
    Tier.FREE: 10,
    Tier.PRO: 100,
    Tier.PREMIUM: 350,
}

# FREE-tier users get a small daily allowance instead of drawing from the
# lifetime TIER_MESSAGE_LIMITS pool (see reserve_free_daily_message below).
FREE_DAILY_MESSAGE_LIMIT = 5


def get_user_by_email(email: str):
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
    return user

def get_user_by_id(user_id: str):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
    return user


def get_user_by_phone_number(phone_number: str):
    with SessionLocal() as db:
        user = db.query(User).filter(User.phone_number == phone_number).first()
    return user


def create_user(user_payload: dict) -> User:
    with SessionLocal() as db:
        new_user = User(**user_payload)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    return new_user


def verify_user(user) -> User:
    with SessionLocal() as db:
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def update_password(user, password) -> User:
    with SessionLocal() as db:
        res = db.query(User).filter(User.email == user.email).first()
        if res:
            res.password = password  # Update the password
            db.commit()  # Commit the transaction
            db.refresh(res)  # Refresh the updated user
            return res  # Return the updated user
        else:
            raise ValueError("User not found")  # Handle if user does not exist


def update_user_tier(email: str, new_tier, is_subscribed: bool = False) -> User:
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.tier = new_tier
            user.is_subscribed = is_subscribed
            user.message_count = TIER_MESSAGE_LIMITS.get(new_tier, 0)
            db.commit()
            db.refresh(user)
            return user
        else:
            raise ValueError("User not found")

def reserve_message(user_id) -> Optional[int]:
    """
    Atomically take one message from the user's allowance.
    Returns the remaining count, or None if the user has no messages left.
    """
    with SessionLocal() as db:
        remaining = db.execute(
            update(User)
            .where(User.id == user_id, User.message_count > 0)
            .values(message_count=User.message_count - 1)
            .returning(User.message_count)
        ).scalar_one_or_none()
        db.commit()
    return remaining


def refund_message(user_id) -> None:
    """Give back a message taken by reserve_message when answering failed"""
    with SessionLocal() as db:
        db.execute(
            update(User)
            .where(User.id == user_id)
            .values(message_count=func.coalesce(User.message_count, 0) + 1)
        )
        db.commit()


def reserve_free_daily_message(user_id) -> Optional[int]:
    """
    Atomically take one message from today's FREE-tier allowance, rolling the
    counter over to 0 first if it was last reset on an earlier day.
    Returns the remaining count for today, or None if today's allowance is used up.
    """
    today = datetime.utcnow().date()
    with SessionLocal() as db:
        db.execute(
            update(User)
            .where(
                User.id == user_id,
                or_(User.daily_message_reset_date == None, User.daily_message_reset_date < today),  # noqa: E711
            )
            .values(daily_message_count=0, daily_message_reset_date=today)
        )
        new_count = db.execute(
            update(User)
            .where(User.id == user_id, User.daily_message_count < FREE_DAILY_MESSAGE_LIMIT)
            .values(daily_message_count=User.daily_message_count + 1)
            .returning(User.daily_message_count)
        ).scalar_one_or_none()
        db.commit()
    if new_count is None:
        return None
    return FREE_DAILY_MESSAGE_LIMIT - new_count


def refund_free_daily_message(user_id) -> None:
    """Give back a message taken by reserve_free_daily_message when answering failed"""
    with SessionLocal() as db:
        db.execute(
            update(User)
            .where(User.id == user_id, User.daily_message_count > 0)
            .values(daily_message_count=User.daily_message_count - 1)
        )
        db.commit()
