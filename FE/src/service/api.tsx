import {
  MethodType,
  SignupType,
  RestaurantResponseType, ChangePasswordType, UserDataType, LoginResponse, RestaurantDataResponse, SearchRestaurantResponse, FeedbackType, FeedbackResponse, FAQNode, ChatMessageResponse,
} from "@/types/api";

let controller: AbortController;
let signal: AbortSignal;

export const BASE_API_URL =
  process.env.NEXT_PUBLIC_BACKEND_BASE_URL || 'http://localhost:8000/';


const API_END_POINT = {
  LOGIN: 'users/login',
  SIGNUP: 'users/signup/',
  FORGET_PASSWORD: 'users/forget_password',
  RESET_PASSWORD: 'users/reset_password',
  GET_RESTAURANT_NAMES: 'get_all_restaurants_name',
  GET_RESTAURANT_DATA: 'get_restaurant_data',
  CHANGE_PASSWORD: 'users/change-password',
  CHAT_START: 'chat/start',
  CHAT_MESSAGE: 'chat/message',
  PROTECTED: 'users/protected/',
  SEARCH_RESTAURANT: 'search_restaurant',
  FEEDBACK: 'feedback',
  FAQS: 'faqs',
};

const _resetAbortController = () => {
  controller = new AbortController();
  signal = controller.signal;
};

const handleUnauthorized = () => {
  localStorage.removeItem("authToken"); // Remove token
  window.location.href = "/login"; // Redirect to login page
};

// init controller and signal
_resetAbortController();

export const abortPreviousRequests = (): void => {
  controller.abort();

  // replace controller and signal so we have a new unaborted one (otherwise the
  // controller remains aborted and will abort any fetch using its signal immediately)
  _resetAbortController();
};

async function _callAPI(
  endpoint: string,
  method: MethodType = "GET",
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  body?: { [key: string]: any },
  headers?: { [key: string]: string },
  abortable: boolean = false,
  formData?: FormData,
) {
  const authToken = localStorage.getItem("authToken"); // Get the token
  const config: {
    method: string;
    headers: { [key: string]: string };
    body?: string;
    signal?: AbortSignal;
  } = {
    method,
    headers: {
      ...(headers || {}),
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    },
  };
 if (formData) {
    config["headers"]["Access-Control-Allow-Origin"] = "*";
    // @ts-expect-error: FormData type not compatible with expected body string
    config.body = formData;
  } else if (body) {
    config.headers["Content-Type"] = "application/json";
    config["headers"]["Access-Control-Allow-Origin"] = "*";
    config.body = JSON.stringify(body);
  }

  if (abortable) {
    config["signal"] = signal;
  }

  try {
    const response = await fetch(BASE_API_URL + endpoint, config);
    const responseBody = await response.json().catch(() => null);

    if (!response.ok) {
      if (response.status === 401 || (response.status === 403 && responseBody?.detail == "Not authenticated")) {
        handleUnauthorized();
      }
      // Extract meaningful error message if available
      const errorMessage =
        responseBody?.detail || responseBody?.message || responseBody?.error || "An unknown error occurred";
      return Promise.reject({ status: response.status, message: errorMessage });
    }

    return responseBody;
  } catch (err) {
    console.error("API Error:", err);
    return Promise.reject({
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      status: (err as any).status || -1,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      message: (err as any).message || "Network error occurred",
    });
  }
}
export const login = async (email: string, password: string): Promise<LoginResponse> => {
  return _callAPI(API_END_POINT.LOGIN, "POST", { email, password })
    .then((responseData: LoginResponse) => {
      if (responseData.access_token) {
        localStorage.setItem("authToken", responseData.access_token);
      }
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "Login failed");
    });
};

export const signup = async (payload: SignupType): Promise<LoginResponse> => {
  return _callAPI(API_END_POINT.SIGNUP, "POST", payload)
    .then((responseData: LoginResponse) => {
      if (responseData.access_token) {
        localStorage.setItem("authToken", responseData.access_token);
      }
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "signup failed");
    });
};

export const forget_password = async (email: string) => {
  return _callAPI(
    `${API_END_POINT.FORGET_PASSWORD}?email=${encodeURIComponent(email)}`,
    "GET"
  )
    .then((responseData) => {
      return responseData; // Successfully processed response
    })
    .catch((error) => {
      return Promise.reject(error || "An error occurred while processing your request.");
    });
};


export const reset_password = async (access_token: string, password: string) => {
  return _callAPI(
    `${API_END_POINT.RESET_PASSWORD}/${encodeURIComponent(access_token)}`,
    "POST",
      {password}
  )
    .then((responseData) => {
      return responseData; // Successfully processed response
    })
    .catch((error) => {
      return Promise.reject(error || "An error occurred while processing your request.");
    });
};

export const change_password = async ( payload: ChangePasswordType ) => {
  return _callAPI(
    `${API_END_POINT.CHANGE_PASSWORD}`,
    "POST",
      payload
  )
    .then((responseData) => {
      return responseData; // Successfully processed response
    })
    .catch((error) => {
      return Promise.reject(error || "An error occurred while processing your request.");
    });
};


export const get_restaurant_names = async (): Promise<RestaurantResponseType[]> => {
  return _callAPI(
    `${API_END_POINT.GET_RESTAURANT_NAMES}`,
    "GET",
  )
    .then((responseData: RestaurantResponseType[]) => {
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "An error occurred while processing your request.");
    });
};

export const get_restaurant_data = async (): Promise<RestaurantDataResponse> => {
  return _callAPI(
    `${API_END_POINT.GET_RESTAURANT_DATA}`,
    "GET",
  )
    .then((responseData) => {
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "An error occurred while processing your request.");
    });
};

export const get_user_data = async (): Promise<UserDataType> => {
  return _callAPI(
    `${API_END_POINT.PROTECTED}`,
    "GET",
  )
    .then((responseData: UserDataType) => {
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "An error occurred while processing your request.");
    });
};

export const chat_start = async () => {
  return _callAPI(
    `${API_END_POINT.CHAT_START}`,
    "POST",
  )
    .then((responseData) => {
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "An error occurred while processing your request.");
    });
};

export const review_agent = async (user_query: string, is_specific: boolean = false, faq_id?: number): Promise<ChatMessageResponse> => {
  return _callAPI(
    `${API_END_POINT.CHAT_MESSAGE}`,
    "POST",
      is_specific && faq_id ? {"message": user_query, is_specific: true, faq_id} : {"message": user_query}
  )
    .then((responseData: ChatMessageResponse) => {
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "An error occurred while processing your request.");
    });
};


export const search_restaurant = async (name: string, location: string): Promise<RestaurantResponseType> => {
  // Call API without authentication since this is used during signup
  const response = await fetch(BASE_API_URL + API_END_POINT.SEARCH_RESTAURANT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ restaurant_name: name, location }),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    console.error("Search restaurant API error:", {
      status: response.status,
      statusText: response.statusText,
      errorData: errorData
    });
    
    let errorMessage = "Restaurant search failed";
    
    if (errorData) {
      if (typeof errorData === 'string') {
        errorMessage = errorData;
      } else if (errorData.detail) {
        errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
      } else if (errorData.message) {
        errorMessage = typeof errorData.message === 'string' ? errorData.message : JSON.stringify(errorData.message);
      } else {
        errorMessage = JSON.stringify(errorData);
      }
    }
    
    throw new Error(errorMessage);
  }
  
  const responseData: SearchRestaurantResponse = await response.json();
  
  return {
    id: responseData.restaurant_id,
    name: responseData.restaurant_name
  };
};

export const send_feedback = async (feedbackData: FeedbackType): Promise<FeedbackResponse> => {
  return _callAPI(API_END_POINT.FEEDBACK, "POST", feedbackData)
    .then((responseData: FeedbackResponse) => {
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "Failed to send feedback");
    });
};


export const createCheckoutSession = async (priceId: string, successUrl: string, cancelUrl: string) => {
  return _callAPI("stripe/create-checkout-session", "POST", {
    price_id: priceId,
    success_url: successUrl,
    cancel_url: cancelUrl,
  });
};

export const get_billing_details = async () => {
  return _callAPI("stripe/billing-details", "GET")
    .then((responseData) => {
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "Failed to fetch billing details");
    });
};

export const cancel_subscription = async () => {
  return _callAPI("stripe/cancel-subscription", "POST")
    .then((responseData) => {
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "Failed to cancel subscription");
    });
};

export const get_subscription_status = async () => {
  return _callAPI("stripe/subscription/status", "GET")
    .then((responseData) => {
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "Failed to fetch subscription status");
    });
};

export const get_faqs = async (): Promise<FAQNode[]> => {
  return _callAPI(API_END_POINT.FAQS, "GET")
    .then((responseData: FAQNode[]) => {
      return responseData;
    })
    .catch((error) => {
      return Promise.reject(error || "Failed to fetch FAQs");
    });
};