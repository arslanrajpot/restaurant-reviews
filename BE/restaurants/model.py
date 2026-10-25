import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from database import Base
from sqlalchemy.dialects.postgresql import UUID
import datetime
from sqlalchemy.orm import relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from users.model import User

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_name = Column(String, unique=True, nullable=False)
    average_price = Column(String, nullable=True)
    total_rating = Column(Float, default=0.0, nullable=True)
    restaurant_location = Column(String, nullable=True)
    neighbourhood = Column(String, nullable=True)
    hours_of_operation = Column(String, nullable=True)
    cuisine = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    overall_rating = Column(Float, default=0, nullable=True)
    food_rating = Column(Float, default=0, nullable=True)
    service_rating = Column(Float, default=0, nullable=True)
    five_stars = Column(Integer, default=0, nullable=True)
    four_stars = Column(Integer, default=0, nullable=True)
    three_stars = Column(Integer, default=0, nullable=True)
    two_stars = Column(Integer, default=0, nullable=True)
    one_stars = Column(Integer, default=0, nullable=True)
    total_review_counts = Column(Integer, default=0, nullable=True)
    ambience_rating = Column(Float, default=0, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=True)


class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = Column(String, nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    thumbs = Column(Integer, nullable=False) 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)