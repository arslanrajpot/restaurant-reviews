from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from restaurants.model import Restaurant, UserFeedback
from uuid import UUID
import uuid
import logging

logger = logging.getLogger(__name__)

def get_restaurant_names():
    with SessionLocal() as db:
        result = db.query(Restaurant.id, Restaurant.restaurant_name, Restaurant.restaurant_location).all()
        return [{"id": str(r.id), "name": r.restaurant_name, "location": r.restaurant_location or ""} for r in result]

def get_restaurant_data(id: UUID):
    with SessionLocal() as db:
        restaurant = db.query(Restaurant).filter(Restaurant.id == id).first()
        if restaurant:
            return restaurant
        logger.error(f"Restaurant not found for id: {id}")
        return None

def get_restaurant_location(restaurant_id: UUID):
    """Get restaurant location by restaurant ID"""
    logger.info(f"Fetching location for restaurant id: {restaurant_id}")
    with SessionLocal() as db:
        restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not restaurant:
            logger.warning(f"Restaurant not found for id: {restaurant_id}")
            return None

        location = restaurant.restaurant_location
        if location is None or location.strip().lower() in ['nan', 'null', '']:
            logger.info(f"No valid location found for restaurant id: {restaurant_id}")
            return ""
        return location

def get_user_feedback_history(user_id: str):
    """
    Get user feedback history from database
    """
    with SessionLocal() as db:
        feedback_history = db.query(UserFeedback).filter(
            UserFeedback.user == user_id
        ).order_by(UserFeedback.created_at.desc()).all()
        return feedback_history


def get_existing_restaurant(restaurant_name: str, location: str):
    """
    Check if a restaurant already exists in the database
    """
    with SessionLocal() as db:
        existing_restaurant = db.query(Restaurant).filter(
            Restaurant.restaurant_name == restaurant_name,
            Restaurant.restaurant_location == location
        ).first()
        return existing_restaurant


def create_restaurant_from_search(restaurant_data, reviews_data=None):
    """Create a new restaurant entry from search data with review star counts"""
    restaurant_name = restaurant_data.get('title', restaurant_data.get('name', ''))
    restaurant_location = restaurant_data.get('address', 'NaN')

    with SessionLocal() as db:
        # Check if restaurant already exists (same name at the same address)
        existing = db.query(Restaurant).filter(
            Restaurant.restaurant_name == restaurant_name,
            Restaurant.restaurant_location == restaurant_location,
        ).first()

        if existing:
            return existing

        types = restaurant_data.get('type', [])
        if isinstance(types, str):
            types = [types]
        elif not isinstance(types, list):
            types = []

        cuisine = types[0] if types else 'NaN'
        tags = ', '.join(types) if types else 'NaN'

        hours_data = restaurant_data.get('hours', 'NaN')
        if isinstance(hours_data, list):
            hours_strings = []
            for day_dict in hours_data:
                for day, hours in day_dict.items():
                    hours_strings.append(f"{day.title()}: {hours}")
            hours_of_operation = "; ".join(hours_strings)
        elif isinstance(hours_data, dict):
            hours_strings = [f"{day.title()}: {hours}" for day, hours in hours_data.items()]
            hours_of_operation = "; ".join(hours_strings)
        else:
            hours_of_operation = str(hours_data) if hours_data else 'NaN'

        # Count star ratings from reviews
        five_stars = 0
        four_stars = 0
        three_stars = 0
        two_stars = 0
        one_stars = 0

        if reviews_data:
            for review in reviews_data:
                rating = review.get('rating')
                if rating == 5:
                    five_stars += 1
                elif rating == 4:
                    four_stars += 1
                elif rating == 3:
                    three_stars += 1
                elif rating == 2:
                    two_stars += 1
                elif rating == 1:
                    one_stars += 1

        # Create new restaurant
        new_restaurant = Restaurant(
            id=uuid.uuid4(),
            restaurant_name=restaurant_name,
            average_price=restaurant_data.get('price', 'NaN'),
            total_rating=float(restaurant_data.get('rating', 0)) if restaurant_data.get('rating') else 0.0,
            restaurant_location=restaurant_location,
            neighbourhood='NaN',
            hours_of_operation=hours_of_operation,
            cuisine=cuisine,
            tags=tags,
            overall_rating=float(restaurant_data.get('rating', 0)) if restaurant_data.get('rating') else 0.0,
            five_stars=five_stars,
            four_stars=four_stars,
            three_stars=three_stars,
            two_stars=two_stars,
            one_stars=one_stars,
            total_review_counts=int(restaurant_data.get('reviews', 0)) if restaurant_data.get('reviews') else 0
        )

        db.add(new_restaurant)
        try:
            db.commit()
        except IntegrityError:
            # Stored concurrently by another request/thread; return that row instead
            db.rollback()
            return db.query(Restaurant).filter(
                Restaurant.restaurant_name == restaurant_name,
                Restaurant.restaurant_location == restaurant_location,
            ).first()
        db.refresh(new_restaurant)
        return new_restaurant


def update_restaurant(restaurant_data):
    with SessionLocal() as db:
        for each in restaurant_data:
            restaurant_name = each.get("restaurant_name")
            restaurant = db.query(Restaurant).filter(Restaurant.restaurant_name == restaurant_name).first()
            if restaurant:
                restaurant.overall_rating = each.get("overall_rating", restaurant.overall_rating)
                restaurant.total_rating = each.get("total_rating", restaurant.total_rating)
                restaurant.food_rating = each.get("food_rating", restaurant.food_rating)
                restaurant.service_rating = each.get("service_rating", restaurant.service_rating)
                restaurant.ambience_rating = each.get("ambience_rating", restaurant.ambience_rating)
                restaurant.total_review_counts = each.get("total_review_count", restaurant.total_review_counts)
                restaurant.five_stars = each.get("five_stars", restaurant.five_stars)
                restaurant.four_stars = each.get("four_stars", restaurant.four_stars)
                restaurant.three_stars = each.get("three_stars", restaurant.three_stars)
                restaurant.two_stars = each.get("two_stars", restaurant.two_stars)
                restaurant.one_stars = each.get("one_stars", restaurant.one_stars)
                db.commit()
        return {"message": "Restaurant updated successfully"}


def save_user_feedback(feedback_data, user_id: str):
    """
    Save user thumbs up/down feedback
    """
    with SessionLocal() as db:
        feedback = UserFeedback(
            user=user_id,
            question=feedback_data.question,
            answer=feedback_data.answer,
            thumbs=int(feedback_data.thumbs)
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)

    return {"success": True, "message": "Feedback saved successfully", "id": feedback.id, "user": feedback.user,
            "question": feedback.question, "answer": feedback.answer, "thumbs": feedback.thumbs}
