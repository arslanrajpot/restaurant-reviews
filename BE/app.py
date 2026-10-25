import os
import time
from jose import jwt, JWTError
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from config_project.config import settings
from users.model import User
from users.routers import router as users_router
from restaurants.routers import router as restaurant_router
from ai_assistants.restaurant_reviews import RestaurantAssistant
from users.utils import get_current_user
from restaurants.services import get_user_feedback_context
from subscription.routers import router as stripe_router
from users.repository import decrement_message_count, update_user_tier
from scheduler import start_scheduler, stop_scheduler
from users.model import Tier
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
    allow_origins=["*"],  # Allows all origins
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

# Setup simple chat model without Chainlit
chat_model = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.7,
)

# Simple in-memory storage for chat history
chat_history = []

class ChatResponse(BaseModel):
    content: str
    author: Optional[str] = "assistant"

class ChatHistory(BaseModel):
    messages: List[Dict]


class ChatRequest(BaseModel):
    message: str
    is_specific: Optional[bool] = False
    faq_id: Optional[int] = None


security = HTTPBearer()
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

# async def authorize_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token = credentials.credentials
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload  # user info
#     except JWTError:
#         raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/")
async def root():
    return {"message": "Welcome to the Restaurant Review Assistant API"}

@app.post("/chat/start")
async def start_chat(current_user: User = Depends(get_current_user)):
    global chat_history
    chat_history = []
    return {"message": "Chat session started. You can now send messages."}

@app.post("/chat/message")
async def send_message(input: ChatRequest, current_user: User = Depends(get_current_user)):
    global chat_history
    
    if current_user.message_count <= 0:
        update_user_tier(current_user.email, Tier.FREE, is_subscribed=False)
        return {"response": "Your message limit is reached, please purchase a plan.", "status_code": 403}

    try:
        chat_history.append({"content": input.message, "author": "user"})
        feedback_context = get_user_feedback_context(str(current_user.id))
        restaurant_assistant = RestaurantAssistant(restaurant_id=current_user.restaurant_id, user_feedback_context=feedback_context)
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

        chat_history.append({"content": response, "author": "assistant"})

        # Attach children for UI if this was an FAQ-specific question
        children = None
        if input.is_specific and input.faq_id:
            try:
                db = SessionLocal()
                node = get_faq_by_id(db, input.faq_id)
                if node and node.children:
                    children = [{"id": c.id, "title": c.title} for c in node.children]
            finally:
                db.close()

        remaining_messages = decrement_message_count(current_user.id)
        return {"response": response, "status_code": 200, "remaining_messages": remaining_messages, "used_faq_id": input.faq_id if input.is_specific else None, "children": children}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history", response_model=ChatHistory)
async def get_chat_history(current_user: User = Depends(get_current_user)):
    return ChatHistory(messages=chat_history)

@app.post("/admin/check-expired-subscriptions")
async def manual_check_expired_subscriptions():
    """Manual endpoint to trigger expired subscriptions check (for testing)"""
    from scheduler import check_expired_subscriptions_job
    await check_expired_subscriptions_job()
    return {"message": "Manual expired subscriptions check completed"}


