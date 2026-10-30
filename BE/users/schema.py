from typing import Optional
from pydantic import EmailStr, BaseModel
from users.model import Tier
from uuid import UUID


class SignupRequest(BaseModel):
    email: EmailStr
    phone_number: str
    name: str
    password: str
    restaurant_id: UUID


class LoginRequest(BaseModel):
    email: str
    password: str


class ResetPasswordRequest(BaseModel):
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone_number: str
    restaurant_id: UUID
    tier: Tier
    message_count: int
    is_subscribed: bool
    # Only meaningful for FREE-tier users; None for paid tiers (see users/routers.py).
    daily_messages_remaining: Optional[int] = None

