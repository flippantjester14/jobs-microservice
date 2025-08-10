import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# For production with 6k requests/minute, need connection pooling
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://scheduler:password@localhost:5432/scheduler_db"
)

# Connection pool settings for scalability
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Number of connections to keep persistently
    max_overflow=30,     # Additional connections when pool is full
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections after 1 hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()