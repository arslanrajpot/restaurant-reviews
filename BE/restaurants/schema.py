from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class RestaurantResponse(BaseModel):
    restaurant_id: UUID
    restaurant_name: str
    overall_rating: float
    total_review_counts: int
    five_stars: int
    four_stars: int
    three_stars: int
    two_stars: int
    one_stars: int
    cuisine: str


class RestaurantDataCaptureRequest(BaseModel):
    restaurant_name: str
    location: str


class RestaurantDataCaptureResponse(BaseModel):
    success: bool
    message: str
    restaurant_id: Optional[UUID] = None
    restaurant_name: Optional[str] = None
    main_restaurant_stored: bool = False
    rag_data_stored: bool = False
    competitors_found: int = 0
    total_reviews_captured: int = 0


class FeedbackRequest(BaseModel):
    user: str
    question: str
    answer: str
    thumbs: int

class RestaurantLocationResponse(BaseModel):
    location: str