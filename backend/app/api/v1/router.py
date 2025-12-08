from fastapi import APIRouter
from app.api.v1.endpoints import auth, detection, submissions, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(detection.router, prefix="/detect", tags=["Detection"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
