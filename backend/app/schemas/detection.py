from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class DetectionRequest(BaseModel):
    content_type: str  # 'text', 'image', 'video', 'url'
    content_text: Optional[str] = None
    content_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "text",
                "content_text": "This is a sample text to analyze for AI generation."
            }
        }

class DetectionResultResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()
    )
    
    id: uuid.UUID
    submission_id: uuid.UUID
    is_ai_generated: Optional[bool]
    confidence_score: float
    detected_model: Optional[str]
    model_confidence: Optional[float]
    analysis_details: Optional[Dict[str, Any]]
    created_at: datetime

class DetectionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    submission_id: uuid.UUID
    content_type: str
    is_ai_generated: Optional[bool]
    confidence_score: float
    confidence_label: Optional[str] = None  # Added for better UX
    detected_model: Optional[str]
    model_confidence: Optional[float]
    analysis_details: Optional[Dict[str, Any]]
    message: str
