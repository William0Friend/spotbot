from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class SubmissionBase(BaseModel):
    content_type: str
    content_text: Optional[str] = None
    content_url: Optional[str] = None
    file_path: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    user_id: Optional[uuid.UUID] = None

class SubmissionResponse(SubmissionBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubmissionWithResult(SubmissionResponse):
    detection_result: Optional[dict] = None
