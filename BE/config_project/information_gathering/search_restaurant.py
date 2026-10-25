import requests
import time
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

load_dotenv()

SERP_API_KEY = os.getenv("SERPAPI_API_KEY")
# Seconds to wait for SerpAPI before giving up, so a slow call can't hang a request forever
REQUEST_TIMEOUT_SECONDS = 30

# API Call Tracking (thread-safe)
api_usage_stats = {
    'total_calls': 0,
    'call_1_main_restaurant_and_competitors': 0,
    'call_2_all_competitor_details': 0,
    'start_time': None,
    'lock': threading.Lock()
}


def track_api_call(call_description):
    """Track API calls with descriptions"""
    with api_usage_stats['lock']:
        api_usage_stats['total_calls'] += 1
        if api_usage_stats['start_time'] is None:
            api_usage_stats['start_time'] = time.time()

    return api_usage_stats['total_calls']


def create_competitor_search_query(cuisine_types, location):
    """Create an optimized search query to find competitors using main restaurant's cuisine type"""
    query_parts = []

    if cuisine_types:
        main_cuisine = str(cuisine_types[0])
        query_parts.append(main_cuisine)

    # Add restaurants to find similar establishments
    if not any('restaurant' in part.lower() for part in query_parts):
        query_parts.append("restaurants")

    # Add location
    if location:
        query_parts.append(f"near {location}")

    query = " ".join(query_parts) if query_parts else None
    return query

def get_single_competitor_details(competitor, location):
    """Get detailed information for a single competitor """
    competitor_name = competitor['name']

    location_parts = location.split(',') if location else []
    general_location = location_parts[-2].strip() if len(location_parts) >= 2 else location

    search_query = f'"{competitor_name}"'
    if general_location:
        search_query += f" {general_location}"

    detailed_params = {
        "engine": "google_maps",
        "q": search_query,
        "type": "search",
        "api_key": SERP_API_KEY
    }

    try:
        track_api_call(f"Competitor details: {competitor_name}")
        response = requests.get("https://serpapi.com/search", params=detailed_params, timeout=REQUEST_TIMEOUT_SECONDS)
        detailed_data = response.json()

        if "place_results" in detailed_data:
            competitor['detailed_data'] = detailed_data["place_results"]
            competitor['place_id'] = detailed_data["place_results"].get('place_id')
            print(f"✅ Got details for {competitor_name} (place_id: {competitor['place_id']})")
            return competitor
        elif "local_results" in detailed_data and detailed_data["local_results"]:
            competitor['detailed_data'] = detailed_data["local_results"][0]
            competitor['place_id'] = detailed_data["local_results"][0].get('place_id')
            print(f"✅ Got details for {competitor_name} (place_id: {competitor['place_id']})")
            return competitor
        else:
            print(f" Could not get detailed data for {competitor_name}")
            return competitor

    except Exception as e:
        print(f" Error getting details for {competitor_name}: {str(e)}")
        return competitor


def get_all_competitor_details_parallel(competitors_list, location):
    """Get detailed information for all competitors in parallel"""
    print(f"\n🔄 PARALLEL PROCESSING: {len(competitors_list)} COMPETITOR DETAILS")
    print("=" * 60)

    # Use ThreadPoolExecutor for parallel API calls
    with ThreadPoolExecutor(max_workers=5) as executor:  # Limit to 5 concurrent requests
        # Submit all tasks
        future_to_competitor = {
            executor.submit(get_single_competitor_details, competitor, location): competitor
            for competitor in competitors_list
        }

        # Collect results as they complete
        for future in as_completed(future_to_competitor):
            try:
                result = future.result()
                # Display basic info if we got detailed data
                if result.get('detailed_data'):
                    display_restaurant_basic_info(result['detailed_data'], is_main=False)
            except Exception as e:
                print(f" Error processing competitor: {str(e)}")


def get_single_competitor_reviews(competitor):
    """Get reviews for a single competitor (thread-safe)"""
    competitor_name = competitor['name']
    competitor_place_id = competitor.get('place_id')

    if not competitor_place_id:
        print(f" No place_id for {competitor_name}")
        return competitor_name, []

    try:
        print(f"🔄 Fetching reviews for {competitor_name}...")
        reviews = get_exactly_50_reviews(competitor_place_id, competitor_name)
        if reviews:
            print(f"✅ Got {len(reviews)} reviews for {competitor_name}")
            return competitor_name, reviews
        else:
            print(f" No reviews found for {competitor_name}")
            return competitor_name, []
    except Exception as e:
        print(f" Error getting reviews for {competitor_name}: {str(e)}")
        return competitor_name, []


def get_all_competitor_reviews_parallel(competitors_list):
    """Get reviews for all competitors in parallel"""
    print(f"\n🔄 PARALLEL PROCESSING: COMPETITOR REVIEWS")
    print("=" * 60)
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_competitor = {
            executor.submit(get_single_competitor_reviews, competitor): competitor
            for competitor in competitors_list if competitor.get('place_id')
        }

        # Collect results as they complete
        for future in as_completed(future_to_competitor):
            try:
                competitor_name, reviews = future.result()
                if reviews:
                    # Display reviews
                    display_50_reviews(reviews, competitor_name, is_main=False)
            except Exception as e:
                print(f" Error processing competitor reviews: {str(e)}")


def get_exactly_50_reviews(place_id, restaurant_name):
    """Get exactly 50 reviews using pagination"""
    if not place_id:
        return None

    all_reviews = []
    next_page_token = None
    page_count = 0
    target_reviews = 50

    while len(all_reviews) < target_reviews:
        page_count += 1
        track_api_call(f"Reviews page {page_count} for {restaurant_name}")

        params = {
            "engine": "google_maps_reviews",
            "place_id": place_id,
            "api_key": SERP_API_KEY
        }

        # Only add num parameter if we have a next_page_token (not on first page)
        if next_page_token:
            params["next_page_token"] = next_page_token
            params["num"] = 20

        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            data = response.json()

            # Check for errors
            if "error" in data:
                print(f"API Error: {data['error']}")
                break

            reviews = data.get("reviews", [])
            if reviews:
                remaining_needed = target_reviews - len(all_reviews)
                reviews_to_add = reviews[:remaining_needed]
                all_reviews.extend(reviews_to_add)

                if len(all_reviews) >= target_reviews:
                    break

                # Check for next page
                pagination_info = data.get("serpapi_pagination", {})
                next_page_token = pagination_info.get("next_page_token")

                if not next_page_token:
                    break

                time.sleep(0.1)  # Reduced sleep for faster processing
            else:
                # Try alternative approach
                if "place_results" in data and "user_reviews" in data["place_results"]:
                    user_reviews = data["place_results"]["user_reviews"]
                    if "most_relevant" in user_reviews:
                        reviews = user_reviews["most_relevant"]
                        if reviews:
                            remaining_needed = target_reviews - len(all_reviews)
                            reviews_to_add = reviews[:remaining_needed]
                            all_reviews.extend(reviews_to_add)
                # This response has no pagination token, so requesting again would return the same reviews
                break
        except Exception as e:
            print(f"Error fetching page {page_count}: {str(e)}")
            break
    return all_reviews if all_reviews else None


def display_restaurant_basic_info(restaurant_data, is_main=True):
    """Display basic restaurant information without reviews"""
    header = "🏠 MAIN RESTAURANT INFORMATION" if is_main else "🏆 COMPETITOR INFORMATION"
    print(f"\n{header}")
    print("=" * 60)

    name = restaurant_data.get('title', 'N/A')
    rating = restaurant_data.get('rating', 'N/A')
    price = restaurant_data.get('price', 'N/A')
    address = restaurant_data.get('address', 'N/A')
    reviews_count = restaurant_data.get('reviews', 'N/A')
    cuisine_types = restaurant_data.get('type', [])
    cuisine = ", ".join(cuisine_types) if cuisine_types else 'N/A'

    print(f"Restaurant: {name}")
    print(f"Rating: {rating}/5")
    print(f"Total Reviews: {reviews_count}")
    print(f"Price Range: {price}")
    print(f"Cuisine: {cuisine}")
    print(f"Address: {address}")


def display_50_reviews(reviews, restaurant_name, is_main=True):
    """Display 50 reviews in a clean format"""
    review_type = "MAIN RESTAURANT" if is_main else "COMPETITOR"
    print(f"\n{review_type} REVIEWS: {restaurant_name}")
    print(f"📊 Displaying {len(reviews)} reviews")
    print("-" * 60)

    for i, review in enumerate(reviews, 1):
        reviewer_name = review.get('user', {}).get('name', 'Anonymous')
        rating = review.get('rating', 'N/A')
        date = review.get('date', 'N/A')
        snippet = review.get('snippet', 'No review text')

        print(f"\n--- Review #{i} ---")
        print(f"Reviewer: {reviewer_name}")
        print(f"Rating: {rating}/5")
        print(f"Date: {date}")

        # Truncate long reviews
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."
        print(f"Review: {snippet}")

    print(f"\n✅ Displayed all {len(reviews)} reviews for {restaurant_name}")


def get_all_competitor_details_only(competitors_list, location):
    """ORIGINAL SEQUENTIAL VERSION - kept for backward compatibility"""
    print(f"\nCOMPETITOR DETAILS - {len(competitors_list)} RESTAURANTS")
    print("=" * 60)

    for i, competitor in enumerate(competitors_list, 1):
        competitor_name = competitor['name']

        location_parts = location.split(',') if location else []
        general_location = location_parts[-2].strip() if len(location_parts) >= 2 else location

        search_query = f'"{competitor_name}"'
        if general_location:
            search_query += f" {general_location}"

        detailed_params = {
            "engine": "google_maps",
            "q": search_query,
            "type": "search",
            "api_key": SERP_API_KEY
        }

        print(f"\n--- Competitor #{i}: {competitor_name} ---")

        try:
            response = requests.get("https://serpapi.com/search", params=detailed_params, timeout=REQUEST_TIMEOUT_SECONDS)
            detailed_data = response.json()

            if "place_results" in detailed_data:
                display_restaurant_basic_info(detailed_data["place_results"], is_main=False)
                competitor['place_id'] = detailed_data["place_results"].get('place_id')
                print(f" Got place_id: {competitor['place_id']}")
            elif "local_results" in detailed_data and detailed_data["local_results"]:
                display_restaurant_basic_info(detailed_data["local_results"][0], is_main=False)
                competitor['place_id'] = detailed_data["local_results"][0].get('place_id')
                print(f"Got place_id from local_results: {competitor['place_id']}")
            else:
                print(f"Could not get detailed data for {competitor_name}")

        except Exception as e:
            print(f"Error getting details for {competitor_name}: {str(e)}")


def display_three_call_summary():
    """Display summary"""
    end_time = time.time()
    total_time = end_time - api_usage_stats['start_time'] if api_usage_stats['start_time'] else 0

    print(f"\n" + "=" * 70)
    print("PARALLEL RESTAURANT ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"⚡ Total API calls used: {api_usage_stats['total_calls']}")
    print(f"🚀 Call #1: Main restaurant + main reviews + competitors")
    print(f"🚀 Call #2: All competitor details (PARALLEL)")
    print(f"🚀 Calls #3+: All competitor reviews (PARALLEL)")
    print(f"Target: 50 reviews per restaurant")
    print(f"⏱️ Total execution time: {total_time:.2f} seconds")
    print("=" * 70)


def search_restaurant_for_api(restaurant_name, location=""):
    """
    UPDATED: Search restaurant with PARALLEL processing for API usage.
    Returns: (main_restaurant_data, competitors_data, all_reviews_data)
    """

    # ===== API CALL #1: Main restaurant + Main restaurant reviews + Competitors =====
    track_api_call("Main restaurant + reviews + competitors discovery")

    main_params = {
        "engine": "google_maps",
        "q": f"{restaurant_name} {location}",
        "type": "search",
        "api_key": SERP_API_KEY
    }

    main_response = requests.get("https://serpapi.com/search", params=main_params, timeout=REQUEST_TIMEOUT_SECONDS)
    main_data = main_response.json()

    main_restaurant = None
    competitors_list = []
    all_reviews_data = {}

    # Process main restaurant data
    if "place_results" in main_data:
        main_restaurant = main_data["place_results"]

        # Get competitors using restaurant's cuisine and location
        cuisine_types = main_restaurant.get('type', [])
        location_for_search = main_restaurant.get('address', location)

        if location_for_search:
            competitor_query = create_competitor_search_query(cuisine_types, location_for_search)
            if competitor_query:
                competitor_params = {
                    "engine": "google_maps",
                    "q": competitor_query,
                    "type": "search",
                    "api_key": SERP_API_KEY
                }

                competitor_response = requests.get("https://serpapi.com/search", params=competitor_params, timeout=REQUEST_TIMEOUT_SECONDS)
                competitor_data = competitor_response.json()

                if "local_results" in competitor_data:
                    for result in competitor_data["local_results"][:5]:
                        if result.get("title") != restaurant_name:
                            competitors_list.append({
                                'name': result.get("title", "Unknown"),
                                'place_id': result.get("place_id"),
                                'basic_data': result
                            })

    elif "local_results" in main_data and main_data["local_results"]:
        main_restaurant = main_data["local_results"][0]

        # Get competitors using main restaurant's cuisine and location
        cuisine_types = main_restaurant.get('type', [])
        location_for_search = main_restaurant.get('address', location)

        if location_for_search:
            competitor_query = create_competitor_search_query(cuisine_types, location_for_search)
            if competitor_query:
                competitor_params = {
                    "engine": "google_maps",
                    "q": competitor_query,
                    "type": "search",
                    "api_key": SERP_API_KEY
                }

                competitor_response = requests.get("https://serpapi.com/search", params=competitor_params, timeout=REQUEST_TIMEOUT_SECONDS)
                competitor_data = competitor_response.json()

                if "local_results" in competitor_data:
                    for result in competitor_data["local_results"][:5]:
                        if result.get("title") != restaurant_name:
                            competitors_list.append({
                                'name': result.get("title", "Unknown"),
                                'place_id': result.get("place_id"),
                                'basic_data': result
                            })

    if not main_restaurant:
        print("No restaurant data found")
        return None, [], {}

    display_restaurant_basic_info(main_restaurant, is_main=True)

    # Get 50 reviews for main restaurant immediately in Call #1
    main_place_id = main_restaurant.get('place_id')

    main_reviews = []
    if main_place_id:
        print(f"\n FETCHING 50 REVIEWS FOR MAIN RESTAURANT...")
        main_reviews = get_exactly_50_reviews(main_place_id, restaurant_name)
        if main_reviews:
            display_50_reviews(main_reviews, restaurant_name, is_main=True)
            all_reviews_data['main_restaurant'] = main_reviews
        else:
            print(f"Could not fetch reviews for main restaurant")

    # ===== PARALLEL PROCESSING: Get ALL competitor details =====
    print(f"\n PARALLEL PROCESSING: All competitor detailed information")
    track_api_call(f"Detailed data for all {len(competitors_list)} competitors")

    if competitors_list:
        get_all_competitor_details_parallel(competitors_list, location)

    # ===== PARALLEL PROCESSING: Get comprehensive reviews for ALL competitors =====
    print(f"\n PARALLEL PROCESSING: Comprehensive reviews for all competitors")

    if competitors_list:
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            future_to_competitor = {
                executor.submit(get_single_competitor_reviews, competitor): competitor
                for competitor in competitors_list if competitor.get('place_id')
            }

            # Collect results as they complete
            for future in as_completed(future_to_competitor):
                try:
                    competitor_name, reviews = future.result()
                    if reviews:
                        all_reviews_data[competitor_name] = reviews
                        display_50_reviews(reviews, competitor_name, is_main=False)
                except Exception as e:
                    print(f"Error processing competitor reviews: {str(e)}")

    display_three_call_summary()

    return main_restaurant, competitors_list, all_reviews_data
