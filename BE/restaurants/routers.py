from fastapi import APIRouter, Depends, HTTPException

from restaurants import services, repository
from restaurants.schema import (
    RestaurantDataCaptureRequest,
    RestaurantDataCaptureResponse,
    RestaurantLocationResponse,
    FeedbackRequest,
)
from users.model import User
from users.utils import get_current_user
from rate_limit import RateLimiter
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Restaurant search is public (used during signup) and triggers paid SerpAPI/Pinecone calls
search_rate_limit = RateLimiter(max_requests=5, window_seconds=60 * 60)


@router.get("/get_all_restaurants_name")
def get_all_restaurants_name():
    """
    Get all restaurant names from the database.
    """
    return services.get_restaurant_name()


@router.get("/get_restaurant_data")
def get_restaurant(current_user: User = Depends(get_current_user)):
    """
    Get restaurant data for the current user.
    """
    return services.get_restaurant(current_user.restaurant_id)

# Get location for a specific restaurant
@router.get("/{id}/location", response_model=RestaurantLocationResponse)
async def get_restaurant_location(id: UUID):
    """Get location for a specific restaurant by ID"""
    logger.info(f"Received location request for id: {id}")

    try:
        # Call the service function which returns RestaurantLocationResponse
        restaurant_location_response = services.get_restaurant_location_service(id)
        return restaurant_location_response

    except HTTPException as e:
        # Re-raise HTTP exceptions as they are
        raise e
    except Exception as e:
        logger.error(f"Internal server error fetching location for id {id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/search_restaurant", response_model=RestaurantDataCaptureResponse, dependencies=[Depends(search_rate_limit)])
async def capture_restaurant_data(
        request: RestaurantDataCaptureRequest,
):
    """
    Capture restaurant data using search functionality and store in both database and RAG system.
    
    """
    try:
        result = services.capture_restaurant_data(
            restaurant_name=request.restaurant_name,
            location=request.location
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error capturing restaurant data: {str(e)}")


@router.post("/feedback")
def save_feedback(request: FeedbackRequest, current_user: User = Depends(get_current_user)):
    """
    Save user thumbs up/down feedback for the authenticated user
    """
    return repository.save_user_feedback(request, user_id=str(current_user.id))