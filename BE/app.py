from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from config_project.config import settings
from users.model import User
from users.routers import router as users_router
from restaurants.routers import router as restaurant_router
from ai_assistants.restaurant_reviews import RestaurantAssistant
from users.utils import get_current_user
from restaurants.services import get_user_feedback_context
from subscription.routers import router as stripe_router
from users.repository import reserve_message, refund_message
from scheduler import start_scheduler, stop_scheduler
from faq.routers import router as faq_router
from database import SessionLocal
from faq.services import get_faq_by_id

load_dotenv()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the app starts"""
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler when the app shuts down"""
    stop_scheduler()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # BASE_URL plus CORS_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include users router with prefix
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(restaurant_router, prefix="", tags=["restaurant_reviews"])
# Register the Stripe router
app.include_router(stripe_router, prefix="/stripe", tags=["stripe"])
app.include_router(faq_router)

# In-memory chat history, kept separately for each user (keyed by user id)
chat_histories: Dict[str, List[Dict]] = {}
# How many previous messages are given to the assistant as conversation context
MAX_CONTEXT_MESSAGES = 20
# How many messages are kept per user in memory
MAX_STORED_MESSAGES = 100

class ChatResponse(BaseModel):
    content: str
    author: Optional[str] = "assistant"

class ChatHistory(BaseModel):
    messages: List[Dict]


class ChatRequest(BaseModel):
    message: str
    is_specific: Optional[bool] = False
    faq_id: Optional[int] = None


@app.get("/")
async def root():
    return {"message": "Welcome to the Restaurant Review Assistant API"}

@app.post("/chat/start")
async def start_chat(current_user: User = Depends(get_current_user)):
    chat_histories[str(current_user.id)] = []
    return {"message": "Chat session started. You can now send messages."}

@app.post("/chat/message")
async def send_message(input: ChatRequest, current_user: User = Depends(get_current_user)):
    chat_history = chat_histories.setdefault(str(current_user.id), [])

    # Take one message from the allowance up front (atomic, so parallel requests can't overspend);
    # it is refunded below if answering fails
    remaining_messages = reserve_message(current_user.id)
    if remaining_messages is None:
        if current_user.is_subscribed:
            limit_message = ("You've used all messages for this billing period. "
                             "Upgrade your plan or wait for your next renewal.")
        else:
            limit_message = "Your message limit is reached, please purchase a plan."
        return {"response": limit_message, "status_code": 403}

    try:
        feedback_context = get_user_feedback_context(str(current_user.id))
        restaurant_assistant = RestaurantAssistant(
            restaurant_id=current_user.restaurant_id,
            user_feedback_context=feedback_context,
            history=chat_history[-MAX_CONTEXT_MESSAGES:],
        )
        # Open a DB session only when needed (e.g., for FAQ-specific queries)
        db = None
        try:
            if input.is_specific:
                db = SessionLocal()
            response = await restaurant_assistant.on_message(
                message=input.message,
                is_specific=input.is_specific or False,
                faq_id=input.faq_id,
                db=db
            )
        finally:
            if db is not None:
                db.close()

        chat_history.append({"content": input.message, "author": "user"})
        chat_history.append({"content": response, "author": "assistant"})
        del chat_history[:-MAX_STORED_MESSAGES]

        # Attach children for UI if this was an FAQ-specific question
        children = None
        if input.is_specific and input.faq_id:
            try:
                db = SessionLocal()
                node = get_faq_by_id(db, input.faq_id)
                if node and node.children:
                    children = [{"id": c.id, "title": c.title} for c in node.children if c.is_active]
            finally:
                db.close()

        return {"response": response, "status_code": 200, "remaining_messages": remaining_messages, "used_faq_id": input.faq_id if input.is_specific else None, "children": children}
    
    except Exception as e:
        refund_message(current_user.id)
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Sorry, something went wrong while answering. Your message was not counted.")

@app.get("/chat/history", response_model=ChatHistory)
async def get_chat_history(current_user: User = Depends(get_current_user)):
    return ChatHistory(messages=chat_histories.get(str(current_user.id), []))

@app.post("/admin/check-expired-subscriptions")
async def manual_check_expired_subscriptions(current_user: User = Depends(get_current_user)):
    """Manual endpoint to trigger expired subscriptions check (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    from scheduler import check_expired_subscriptions_job
    await check_expired_subscriptions_job()
    return {"message": "Manual expired subscriptions check completed"}


