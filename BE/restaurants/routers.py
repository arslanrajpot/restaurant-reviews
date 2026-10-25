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
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


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

@router.post("/search_restaurant", response_model=RestaurantDataCaptureResponse)
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
def save_feedback(request: FeedbackRequest):
    """
    Save user thumbs up/down feedback
    """
    return repository.save_user_feedback(request)