export type MethodType =
  | 'GET'
  | 'POST'
  | 'PUT'
  | 'DELETE'
  | 'OPTIONS'
  | 'HEAD'
  | 'PATCH';

export type SignupType = {
    email: string,
    password: string,
    name: string,
    phone_number: string,
    restaurant_id: string,
}


export type RestaurantResponseType = {
    id: string;
    name: string;
    location?: string;
}

export type ChangePasswordType = {
    old_password: string;
    new_password: string;
}

export type UserDataType = {
    id: string;
    name: string;
    email: string;
    phone_number: string;
    restaurant_id: string;
    tier: string;
    message_count: number;
    is_subscribed: boolean;
}

export type LoginResponse = {
    access_token: string;
    token_type: string;
}

export type RestaurantDataResponse = {
    restaurant_id: string;
    restaurant_name: string;
    overall_rating: number
    total_review_counts: number
    five_stars: number
    four_stars: number
    three_stars: number
    two_stars: number
    one_stars: number
    cuisine: string
}


export type SearchRestaurantResponse = {
    success: boolean;
    message: string;
    restaurant_id: string;
    restaurant_name: string;
    main_restaurant_stored: boolean;
    rag_data_stored: boolean;
    competitors_found: number;
    total_reviews_captured: number;
}

export type FeedbackType = {
    user: string;
    question: string;
    answer: string;
    thumbs: number;
}

export type FeedbackResponse = {
    success: boolean;
    message?: string;
}

export type FAQNode = {
    id: number;
    title: string;
    children?: FAQNode[];
}

export type ChatMessageResponse = {
    response: string;
    status_code: number;
    remaining_messages: number;
    used_faq_id?: number;
    children?: FAQNode[];
}

