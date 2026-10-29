from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from urllib.parse import urlparse
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
    
    # Frontend URL, used for email links and as the default allowed CORS / redirect origin
    BASE_URL: str

    # Extra allowed frontend origins, comma separated (e.g. "http://localhost:3000,https://www.example.com")
    CORS_ORIGINS: str = ""
    
    # Gemini Settings
    GOOGLE_API_KEY: str
    
    # Pinecone Settings
    PINECONE_API_KEY: str
    PINECONE_INDEX: str
    
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

    @property
    def allowed_origins(self) -> list[str]:
        origins = [self.BASE_URL] + [o for o in self.CORS_ORIGINS.split(",") if o.strip()]
        result = []
        for origin in origins:
            parsed = urlparse(origin.strip())
            if parsed.scheme and parsed.netloc:
                normalized = f"{parsed.scheme}://{parsed.netloc}"
                if normalized not in result:
                    result.append(normalized)
        return result

    def is_allowed_redirect(self, url: str) -> bool:
        parsed = urlparse(url or "")
        return f"{parsed.scheme}://{parsed.netloc}" in self.allowed_origins

# Create a single instance of Settings
try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {str(e)}")
    raise
