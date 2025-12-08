"""
AI Content Detection API Endpoint

This module provides the main detection endpoint that accepts content (text, image URLs, video URLs)
and returns AI generation analysis with confidence scores.

Architecture:
- Backend API receives request → stores submission → calls AI detector microservice
- AI detector runs analysis → returns results → backend stores in database
- Separation allows scaling detector independently from API

Deployment: Hostinger VPS → DigitalOcean (when scaling)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import httpx
from app.core.database import get_db
from app.core.config import settings
from app.models.submission import Submission
from app.models.detection_result import DetectionResult
from app.schemas.detection import DetectionRequest, DetectionResponse

router = APIRouter()

@router.post("/", response_model=DetectionResponse)
async def detect_content(
    request: DetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze content to detect AI generation and identify which model created it.
    
    This is the main detection endpoint - accepts multiple content types and returns
    two-tier confidence scores: (1) is it AI? (2) which AI made it?
    
    **Supported Content Types:**
    - `text`: Direct text analysis (GPT, Claude, Gemini, Llama, Mistral patterns)
    - `image`: Image URL analysis (DALL-E, Midjourney, Stable Diffusion tells)
    - `video`: Video URL analysis (Sora, Runway, Pika detection)
    - `url`: Fetch and analyze webpage content
    
    **How it works:**
    1. Store submission in database (audit trail)
    2. Forward to AI detector microservice (port 8001)
    3. AI detector runs multi-factor analysis (pattern matching, ML, metadata)
    4. Store detection result with full analysis breakdown
    5. Return comprehensive result to frontend
    
    **Confidence Scoring:**
    - Overall confidence: 0-100% probability content is AI-generated
    - Model confidence: 0-100% probability specific model created it (≤ overall)
    - Threshold: 40% = "is_ai_generated: true"
    
    Args:
        request: DetectionRequest with content_type and content (text or URL)
        db: Database session (injected by FastAPI)
        
    Returns:
        DetectionResponse with:
        - submission_id: UUID for tracking
        - is_ai_generated: bool (true if confidence ≥ 40%)
        - confidence_score: float (0-100)
        - detected_model: str (gpt/claude/gemini/llama/mistral or null)
        - model_confidence: float (0-100, but ≤ confidence_score)
        - analysis_details: dict with full scoring breakdown
        
    Raises:
        HTTPException 500: If AI detector service is unavailable or errors
        HTTPException 422: If request validation fails (auto-handled by FastAPI)
        
    Example:
        ```bash
        curl -X POST http://localhost:8000/api/v1/detect/ \\
          -H "Content-Type: application/json" \\
          -d '{
            "content_type": "text",
            "content_text": "Certainly! It'\''s worth noting..."
          }'
        ```
        
        Response:
        ```json
        {
          "submission_id": "uuid-here",
          "is_ai_generated": true,
          "confidence_score": 45.2,
          "detected_model": "gpt",
          "model_confidence": 42.0
        }
        ```
    
    OpenAPI Tags: Detection
    """
    
    # === STEP 1: Store Submission ===
    # Why: Audit trail for all detection requests, even if analysis fails
    # This allows tracking usage, debugging, and potential re-analysis
    submission = Submission(
        content_type=request.content_type,
        content_text=request.content_text,
        content_url=request.content_url
    )
    db.add(submission)
    db.commit()  # Commit now to get ID for foreign key relationship
    db.refresh(submission)  # Reload to get generated ID and timestamps
    
    try:
        # === STEP 2: Call AI Detector Microservice ===
        # Why separate service: AI detection is compute-intensive, can scale independently
        # Timeout 30s: Complex analysis can take time (ML models, metadata extraction)
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Forward request to AI detector microservice
            # URL comes from config: http://ai-detector:8001 (Docker network) or localhost:8001 (dev)
            response = await client.post(
                f"{settings.AI_DETECTOR_URL}/analyze",
                json={
                    "content_type": request.content_type,
                    "content_text": request.content_text,
                    "content_url": request.content_url
                }
            )
            
            # Handle detector service errors
            # Common causes: service down, timeout, invalid input
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"AI detector service error: {response.text}"
                )
            
            result_data = response.json()
        
        # === STEP 3: Store Detection Result ===
        # Why: Persistent storage allows history tracking, re-training, analytics
        # Links to submission via foreign key (cascade delete configured)
        detection_result = DetectionResult(
            submission_id=submission.id,
            is_ai_generated=result_data.get("is_ai_generated"),
            confidence_score=result_data.get("confidence_score", 0),
            detected_model=result_data.get("detected_model"),
            model_confidence=result_data.get("model_confidence"),
            analysis_details=result_data.get("analysis_details")
        )
        db.add(detection_result)
        db.commit()
        db.refresh(detection_result)
        
        return DetectionResponse(
            submission_id=submission.id,
            content_type=request.content_type,
            is_ai_generated=detection_result.is_ai_generated,
            confidence_score=float(detection_result.confidence_score),
            confidence_label=result_data.get("confidence_label"),
            detected_model=detection_result.detected_model,
            model_confidence=float(detection_result.model_confidence) if detection_result.model_confidence else None,
            analysis_details=detection_result.analysis_details,
            message="Analysis complete"
        )
        
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI detector service unavailable: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing detection: {str(e)}"
        )

@router.get("/test")
async def test_detector():
    """Test if AI detector service is available"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.AI_DETECTOR_URL}/health")
            return {
                "status": "connected",
                "detector_status": response.json()
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI detector service unavailable: {str(e)}"
        )
