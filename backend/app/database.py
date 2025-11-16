from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from .config import settings

# Create engine with optimized connection pooling
engine = create_engine(
    settings.database_url,
    # Connection pool settings
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to keep open
    max_overflow=20,  # Max connections beyond pool_size
    pool_pre_ping=True,  # Test connections before using (prevents stale connections)
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Wait up to 30 seconds for a connection
    # Performance settings
    echo=False,  # Disable SQL logging in production
    future=True,  # Use SQLAlchemy 2.0 style
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
