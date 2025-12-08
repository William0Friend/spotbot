from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.submission import Submission
from app.schemas.submission import SubmissionResponse, SubmissionWithResult
import uuid

router = APIRouter()

@router.get("/", response_model=List[SubmissionWithResult])
async def get_submissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all submissions (paginated)"""
    submissions = db.query(Submission).offset(skip).limit(limit).all()
    
    # Convert to response format with detection results
    result = []
    for submission in submissions:
        submission_dict = {
            "id": submission.id,
            "user_id": submission.user_id,
            "content_type": submission.content_type,
            "content_text": submission.content_text,
            "content_url": submission.content_url,
            "file_path": submission.file_path,
            "created_at": submission.created_at,
            "detection_result": None
        }
        
        if submission.detection_result:
            submission_dict["detection_result"] = {
                "is_ai_generated": submission.detection_result.is_ai_generated,
                "confidence_score": float(submission.detection_result.confidence_score),
                "detected_model": submission.detection_result.detected_model,
                "model_confidence": float(submission.detection_result.model_confidence) if submission.detection_result.model_confidence else None
            }
        
        result.append(submission_dict)
    
    return result

@router.get("/{submission_id}", response_model=SubmissionWithResult)
async def get_submission(
    submission_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get a specific submission by ID"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    submission_dict = {
        "id": submission.id,
        "user_id": submission.user_id,
        "content_type": submission.content_type,
        "content_text": submission.content_text,
        "content_url": submission.content_url,
        "file_path": submission.file_path,
        "created_at": submission.created_at,
        "detection_result": None
    }
    
    if submission.detection_result:
        submission_dict["detection_result"] = {
            "is_ai_generated": submission.detection_result.is_ai_generated,
            "confidence_score": float(submission.detection_result.confidence_score),
            "detected_model": submission.detection_result.detected_model,
            "model_confidence": float(submission.detection_result.model_confidence) if submission.detection_result.model_confidence else None,
            "analysis_details": submission.detection_result.analysis_details
        }
    
    return submission_dict
