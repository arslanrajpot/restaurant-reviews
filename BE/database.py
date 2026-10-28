import os
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from sqlalchemy import create_engine
load_dotenv()

# Create Base class for models to inherit from
Base = declarative_base()

# Create engine and session
# pool_pre_ping + pool_recycle: Neon (serverless Postgres) silently closes idle
# connections, which otherwise surfaces as "SSL connection has been closed
# unexpectedly" the next time a stale pooled connection is reused.
engine = create_engine(
    os.getenv("POSTGRES_CONNECTION_URI", ""),
    pool_pre_ping=True,
    pool_recycle=280,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
