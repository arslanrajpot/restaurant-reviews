from fastapi import HTTPException
from restaurants import repository
from restaurants.schema import RestaurantResponse, RestaurantDataCaptureResponse, RestaurantLocationResponse
from config_project.information_gathering.search_restaurant import search_restaurant_for_api
from rag_embeddings.pinecone_embeddings import PineconeEmbeddings
from concurrent.futures import ThreadPoolExecutor, as_completed
from config_project.information_gathering.utils import store_competitor_data
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_restaurant_name():
    """
    Get the restaurant name from the database.
    """
    data = repository.get_restaurant_names()
    if not data:
        raise HTTPException(status_code=404, detail="Restaurant not found.")
    return data


def get_restaurant(id: UUID):
    """
    Get the restaurant data from the database.
    """
    data = repository.get_restaurant_data(id)
    if not data:
        raise HTTPException(status_code=404, detail="Restaurant not found.")
    return RestaurantResponse(
        restaurant_id=data.id,
        restaurant_name=data.restaurant_name,
        cuisine=data.cuisine.split(",")[0] if data.cuisine else "",
        overall_rating=data.overall_rating or 0,
        total_review_counts=data.total_review_counts or 0,
        five_stars=data.five_stars or 0,
        four_stars=data.four_stars or 0,
        three_stars=data.three_stars or 0,
        two_stars=data.two_stars or 0,
        one_stars=data.one_stars or 0,
    )


def get_restaurant_location_service(id: UUID) -> RestaurantLocationResponse:
    """Get restaurant location by restaurant ID"""
    try:
        logger.info(f"Service: Fetching location for restaurant id: {id}")

        # Get the location using repository function
        location = repository.get_restaurant_location(id)

        if location is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        # Return the response model
        return RestaurantLocationResponse(location=location)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def capture_restaurant_data(restaurant_name: str, location: str) -> RestaurantDataCaptureResponse:
    """
    Capture restaurant data, store in database and RAG system.
    """
    try:
        # First check if restaurant exists in database
        existing_restaurant = repository.get_existing_restaurant(restaurant_name, location)
        
        if existing_restaurant:
            return RestaurantDataCaptureResponse(
                success=True,
                message=f"Restaurant '{restaurant_name}' already exists in database",
                restaurant_id=existing_restaurant.id,
                restaurant_name=restaurant_name,
                main_restaurant_stored=True,
                total_reviews_captured=existing_restaurant.total_review_counts
            )

        # If not in database, proceed with API search
        main_restaurant_data, competitors_data, all_reviews_data = search_restaurant_for_api(restaurant_name, location)

        if not main_restaurant_data:
            return RestaurantDataCaptureResponse(
                success=False,
                message="Restaurant not found",
                competitors_found=0,
                total_reviews_captured=0
            )

        # Get main restaurant reviews 
        main_reviews = all_reviews_data.get('main_restaurant', [])

        # Store main restaurant in database 
        stored_restaurant = repository.create_restaurant_from_search(main_restaurant_data, main_reviews)

        # Initialize Pinecone uploader
        pinecone_uploader = PineconeEmbeddings()
        total_rag_uploads = 0

        # Upload main restaurant data to RAG
        main_rag_count = pinecone_uploader.upload_search_data(main_restaurant_data, main_reviews)
        total_rag_uploads += main_rag_count

        # Store and upload competitors data
        competitors_uploaded = 0
        if competitors_data:
            print(f" Storing {len(competitors_data)} competitors in parallel...")

            with ThreadPoolExecutor(max_workers=4) as executor:
                # Prepare data for parallel processing
                competitor_tasks = [(competitor, all_reviews_data) for competitor in competitors_data]

                # Submit all tasks
                future_to_competitor = {
                    executor.submit(store_competitor_data, task, pinecone_uploader): task[0]
                    for task in competitor_tasks
                }

                # Collect results
                for future in as_completed(future_to_competitor):
                    try:
                        stored_count, rag_count = future.result()
                        competitors_uploaded += stored_count
                        total_rag_uploads += rag_count
                    except Exception as e:
                        print(f" Error in parallel storage: {str(e)}")

            print(f"Storage complete: {competitors_uploaded} competitors stored")

        total_reviews = sum(len(reviews) for reviews in all_reviews_data.values())

        return RestaurantDataCaptureResponse(
            success=True,
            message=f"Successfully captured data for {restaurant_name}",
            restaurant_id=stored_restaurant.id,
            restaurant_name=restaurant_name,
            main_restaurant_stored=True,
            rag_data_stored=total_rag_uploads > 0,
            competitors_found=competitors_uploaded,
            total_reviews_captured=total_reviews
        )

    except Exception as e:
        print(f"Error in capture_restaurant_data: {str(e)}")
        return RestaurantDataCaptureResponse(
            success=False,
            message=f"Error capturing data: {str(e)}",
            competitors_found=0,
            total_reviews_captured=0
        )


def fetch_restaurant_context(restaurant_id: str) -> str:
    # You can replace this with an actual DB call
    restaurant = repository.get_restaurant_data(restaurant_id)

    if not restaurant:
        return "No specific restaurant context available."

    return (
        f"Restaurant Name: {restaurant.restaurant_name}\n"
        f"Location: {restaurant.restaurant_location}\n"
        f"Cuisine: {restaurant.cuisine}\n"
        f"Rating: {restaurant.overall_rating} stars\n"
        f"Neighbourhood: {restaurant.neighbourhood}\n"
        f"Average Price: {restaurant.average_price}"
    )


def get_user_feedback_context(user_id: str):
    """
    Get user feedback history for context building
    """
    feedback_history = repository.get_user_feedback_history(user_id)
    if not feedback_history:
        return ""
    
    liked = []
    disliked = []
    
    for feedback in feedback_history:
        if feedback.thumbs == 1:
            liked.append(f"Q: {feedback.question} A: {feedback.answer}, Thumbs: {feedback.thumbs}")
        else: 
            disliked.append(f"Q: {feedback.question} A: {feedback.answer}, Thumbs: {feedback.thumbs}")
    
    context = ""
    if liked:
        context += f"User previously liked these Q&As: {liked[:10]}. \n"
    if disliked:
        context += f"User previously disliked these Q&As: {disliked[:10]}. \n"
    
    return context
