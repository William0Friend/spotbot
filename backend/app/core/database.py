"""
Database Connection Management

SQLAlchemy setup with connection pooling for PostgreSQL.

Why SQLAlchemy:
- ORM: Write Python instead of SQL (type safety, easier refactoring)
- Migrations: Alembic integration for schema changes
- Relationships: Auto-handles foreign keys, joins, lazy loading
- Connection pooling: Reuse database connections for performance

Connection pool configuration:
- pool_pre_ping: Check connection health before using (handles stale connections)
- pool_size: Number of connections to keep open (10 = handles 10 concurrent requests)
- max_overflow: Extra connections when pool exhausted (10+20=30 max)

Why these pool sizes:
- Small app: 10 connections sufficient for hundreds of requests/second
- Overflow handles traffic spikes without permanent resource consumption
- PostgreSQL default max_connections=100, leave room for other services

Session management:
- SessionLocal creates new session per request (thread-safe)
- get_db() is FastAPI dependency (auto-closes session after request)
- No manual session.close() needed in routes
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine with connection pooling
# Engine is created once at app startup, shared across requests
engine = create_engine(
    settings.DATABASE_URL,
    
    # Check if connection alive before using (prevents "server closed connection" errors)
    pool_pre_ping=True,
    
    # Number of persistent connections to maintain
    # Each concurrent request needs one connection
    pool_size=10,
    
    # Allow temporary connections beyond pool_size during traffic spikes
    # Total max connections: pool_size + max_overflow = 30
    max_overflow=20
)

# Session factory - creates new session per request
# autocommit=False: Explicit commit() required (safer, prevents accidental changes)
# autoflush=False: Don't auto-flush on query (more control over DB operations)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
# All models inherit from this to get SQLAlchemy functionality
Base = declarative_base()

def get_db():
    """
    FastAPI dependency for database sessions.
    
    Creates new session per request, automatically closes after.
    
    Usage in routes:
        ```python
        @router.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
        ```
    
    Why yield pattern:
    - Code before yield: Setup (create session)
    - yield: Return session to route
    - Code after yield: Cleanup (close session)
    - Even if route raises exception, cleanup runs (finally block)
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
