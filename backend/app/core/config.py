"""
Application Configuration

Centralized settings management using Pydantic for type safety and validation.

Why Pydantic Settings:
- Type validation: Ensures config values are correct types
- Environment variables: Auto-loads from .env file
- Default values: Sensible defaults for development
- IDE support: Type hints enable autocomplete

Configuration sources (priority order):
1. Environment variables (highest priority)
2. .env file
3. Default values in this file (lowest priority)

Security best practices:
- SECRET_KEY: Generate with `openssl rand -base64 32`
- Never commit secrets to Git (.env in .gitignore)
- Use different secrets per environment (dev/staging/prod)
- Rotate secrets periodically

Deployment:
- Dev: Uses defaults or .env file
- Hostinger: Set environment variables in deployment script
- DigitalOcean: Set via Ansible playbook templates
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    
    Attributes:
        DATABASE_URL: PostgreSQL connection string
        REDIS_URL: Redis connection string
        AI_DETECTOR_URL: AI detector microservice endpoint
        SECRET_KEY: JWT signing secret (CHANGE IN PRODUCTION!)
        ALGORITHM: JWT algorithm (HS256 standard)
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT token lifetime
        ENVIRONMENT: dev/staging/production
        OPENAI_API_KEY: Optional, for future ML features
        ANTHROPIC_API_KEY: Optional, for future ML features
    
    Example .env:
        ```
        DATABASE_URL=postgresql://user:pass@localhost:5432/spotbot
        SECRET_KEY=your-secret-key-here
        ENVIRONMENT=production
        ```
    """
    
    # === Database Configuration ===
    # PostgreSQL connection string
    # Format: postgresql://username:password@host:port/database
    # Docker network: postgres:5432 (service name)
    # Local dev: localhost:5432
    DATABASE_URL: str = "postgresql://spotbot:spotbot_dev_password@localhost:5432/spotbot"
    
    # === Cache Configuration ===
    # Redis for session storage, rate limiting, caching
    # Docker network: redis:6379 (service name)
    # Local dev: localhost:6379
    REDIS_URL: str = "redis://localhost:6379"
    
    # === Microservices ===
    # AI Detector service endpoint
    # Docker network: http://ai-detector:8001 (service name)
    # Local dev: http://localhost:8001
    AI_DETECTOR_URL: str = "http://localhost:8001"
    
    # === Security Configuration ===
    # JWT token signing secret
    # CRITICAL: Change this in production! Generate with: openssl rand -base64 32
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # JWT algorithm (HS256 is standard, symmetric signing)
    ALGORITHM: str = "HS256"
    
    # JWT token expiry in minutes
    # Shorter = more secure (tokens expire quickly)
    # Longer = better UX (less frequent re-login)
    # 30 minutes is good balance for security vs usability
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # === Environment ===
    # Used for conditional behavior (debug logs, error reporting, etc.)
    ENVIRONMENT: str = "development"
    
    # === Optional AI API Keys ===
    # For future features: ML-based detection, training data generation
    # Not required for current pattern-based detection
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    HUGGINGFACE_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
