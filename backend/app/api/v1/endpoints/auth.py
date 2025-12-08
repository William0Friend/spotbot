"""
Authentication & User Management API

Handles user registration, login, and profile access using JWT tokens.

Security approach:
- Passwords hashed with bcrypt (12 rounds, industry standard)
- JWT tokens for stateless authentication (no server-side sessions needed)
- Token expiry configurable (default 30 min for security)

Why JWT over sessions:
- Stateless: API can scale horizontally without session store
- Mobile-friendly: Easy to use in mobile apps
- Microservices: Token can be validated by any service with secret key
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    Creates new user with hashed password. Email and username must be unique.
    
    Args:
        user_data: UserCreate schema with email, username, password
        db: Database session (injected)
        
    Returns:
        UserResponse with user ID, email, username (no password!)
        
    Raises:
        HTTPException 400: If email or username already exists
        
    Example:
        ```bash
        curl -X POST http://localhost:8000/api/v1/auth/register \\
          -H "Content-Type: application/json" \\
          -d '{
            "email": "user@example.com",
            "username": "testuser",
            "password": "securepass123"
          }'
        ```
        
    Security notes:
    - Password automatically hashed with bcrypt before storage
    - Original password never stored in database
    - Email validation handled by Pydantic EmailStr type
    
    OpenAPI Tags: Authentication
    """
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    # Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(db: Session = Depends(get_db)):
    """Get current user information (placeholder - needs JWT implementation)"""
    # This is a simplified version - in production, decode JWT from header
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="JWT authentication to be implemented"
    )
