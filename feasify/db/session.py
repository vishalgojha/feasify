"""Database session management for SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from feasify.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": True} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.API_DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for DB sessions."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Alias for compatibility
get_session = get_db_context

def init_db():
    """Initialize database by creating all tables."""
    from feasify.db.models import Base
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all tables (use with caution!)."""
    from feasify.db.models import Base
    Base.metadata.drop_all(bind=engine)
