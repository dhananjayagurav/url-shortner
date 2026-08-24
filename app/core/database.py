"""SQLAlchemy engine/session set up. Phase 1: synchronous, simple"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: yields a DB session, closes it after the request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

