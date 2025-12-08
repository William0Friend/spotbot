from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import time
import traceback

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router

# Configure logging first, before model imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import all models so SQLAlchemy knows about relationships
# This must be done before Base.metadata.create_all()
from app.models.user import User
from app.models.submission import Submission
from app.models.detection_result import DetectionResult
# Import new models for two-tier confidence system
try:
    from app.models.ai_model_score import AIModelScore, PatternMatch, ConfidenceBreakdown, LinguisticAnalysis
except ImportError:
    # Models not yet available, will be added in migration
    logger.warning("Advanced detection models not yet available")

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

# Initialize rate limiter (like Laravel's throttle)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SpotBot API",
    description="AI Content Detection Platform - Similar to Laravel Telescope for debugging",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG if hasattr(settings, 'DEBUG') else True
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request logging middleware (like Telescope)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 Request: {request.method} {request.url.path}")
    logger.info(f"   Client: {request.client.host if request.client else 'unknown'}")
    logger.info(f"   Headers: {dict(request.headers)}")
    
    try:
        response = await call_next(request)
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(f"📤 Response: {response.status_code} - Duration: {duration:.3f}s")
        
        # Add custom headers for debugging
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-Debug-Mode"] = "enabled"
        
        return response
    
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ Error in request: {str(e)}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
        logger.error(f"   Duration: {duration:.3f}s")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error": str(e),
                "path": str(request.url.path),
                "method": request.method,
                "timestamp": time.time()
            }
        )

# Custom exception handlers (better error debugging)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"⚠️  HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": str(request.url.path),
            "method": request.method,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "body": str(exc.body) if exc.body else None,
            "path": str(request.url.path)
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "SpotBot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "telescope": "Check logs for detailed request/response debugging"
    }

@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "debug_mode": True
    }

@app.get("/debug/routes")
async def debug_routes():
    """List all available routes (like Laravel's route:list)"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return {"routes": routes}

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 SpotBot API starting up...")
    logger.info(f"   Debug mode: ON")
    logger.info(f"   Database: Connected")
    logger.info(f"   Docs: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 SpotBot API shutting down...")
