import os
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from sqlalchemy import create_engine
load_dotenv()

# Create Base class for models to inherit from
Base = declarative_base()

# Create engine and session
engine = create_engine(os.getenv("POSTGRES_CONNECTION_URI", ""))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
