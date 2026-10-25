from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database Settings
    POSTGRES_CONNECTION_URI: str
    
    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # SMTP Settings
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_PASSWORD: str
    
    # Base URL for email verification links
    BASE_URL: str
    
    # OpenAI Settings
    OPENAI_API_KEY: str
    
    # Pinecone Settings
    PINECONE_API_KEY: str
    PINECONE_INDEX: str
    EMBEDDING_MODEL: str
    
    # Chainlit Settings
    CHAINLIT_AUTH_SECRET: str
    
    # SerpAPI Settings
    SERPAPI_API_KEY: str
    
    # Stripe Settings
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    # Stripe price IDs
    PRO_PRICE_ID: str
    PREMIUM_PRICE_ID: str
    
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in settings

# Create a single instance of Settings
try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {str(e)}")
    raise
