from database import SessionLocal
from users.model import User
from datetime import datetime
from users.model import Tier

TIER_MESSAGE_LIMITS = {
    Tier.FREE: 0,
    Tier.PRO: 100,
    Tier.PREMIUM: 350,
}


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

def decrement_message_count(user_id: str) -> int:
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.message_count > 0:
            user.message_count -= 1
            db.commit()
            db.refresh(user)
            return user.message_count
        elif user:
            return 0
        else:
            raise ValueError("User not found")


