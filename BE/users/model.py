import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Boolean, Enum, ForeignKey, Integer, Date
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

# Remove TYPE_CHECKING import and Restaurant import
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from restaurants.model import Restaurant


class Tier(enum.Enum):
    FREE = "FREE"
    PRO = "PRO"
    PREMIUM = "PREMIUM"


class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(BaseModel):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    phone_number = Column(String, unique=True)
    name = Column(String)
    password = Column(String)
    is_verified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    tier = Column(Enum(Tier), default=Tier.FREE, nullable=False)
    restaurant_id = Column(UUID(as_uuid=True), default=None)
    is_subscribed = Column(Boolean, default=False, nullable=False)
    subscription = relationship("Subscription", back_populates="user", uselist=False)

    message_count = Column(Integer, default=0)

    # FREE-tier daily quota: reset lazily to 0 whenever daily_message_reset_date
    # is not today (see users/repository.py reserve_free_daily_message).
    daily_message_count = Column(Integer, default=0, nullable=False)
    daily_message_reset_date = Column(Date, nullable=True)

    # Remove Restaurant relationship - comment these out for now
    # restaurant_id = Column(UUID(as_uuid=True), ForeignKey('restaurants.id'), nullable=True)
    # restaurant = relationship("Restaurant", back_populates="partners")
