"""
Pydantic Schemas for AI Detector Service

Request/response models for the AI detector microservice.

Why Pydantic:
- Automatic validation: Type checking, required fields, constraints
- JSON serialization: Automatic to/from JSON conversion
- OpenAPI docs: FastAPI auto-generates API documentation from these schemas
- Editor support: Type hints enable autocomplete in IDEs

These schemas define the contract between backend API and AI detector service.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any

class AnalysisRequest(BaseModel):
    """
    Request model for AI detection analysis.
    
    Attributes:
        content_type: Type of content to analyze
        content_text: Direct text input (for content_type='text')
        content_url: URL to fetch content (for images/videos/urls)
    
    Validation:
        - content_type is required
        - Must provide either content_text OR content_url (not both)
    
    Example:
        ```json
        {
          "content_type": "text",
          "content_text": "Certainly! It's worth noting..."
        }
        ```
    """
    content_type: str = Field(
        ..., 
        description="Content type: 'text', 'image', 'video', or 'url'",
        examples=["text", "image", "video", "url"]
    )
    content_text: Optional[str] = Field(
        None,
        description="Direct text content to analyze (for content_type='text')",
        examples=["Certainly! It's worth noting that..."]
    )
    content_url: Optional[str] = Field(
        None,
        description="URL of content to fetch and analyze",
        examples=["https://example.com/image.jpg"]
    )

class AnalysisResponse(BaseModel):
    """
    Response model for AI detection results.
    
    Two-tier confidence system:
    - confidence_score: Overall AI probability (0-100%)
    - model_confidence: Specific model probability (0-100%, ≤ confidence_score)
    
    Attributes:
        is_ai_generated: Boolean decision (true if confidence ≥ 40%)
        confidence_score: Overall AI probability (0-100)
        confidence_label: Human-readable label (Very Low/Low/Moderate/High/Very High)
        detected_model: Most likely AI model (gpt/claude/gemini/llama/mistral)
        model_confidence: Model-specific probability (≤ confidence_score)
        analysis_details: Full scoring breakdown with pattern matches
    
    Example:
        ```json
        {
          "is_ai_generated": true,
          "confidence_score": 45.2,
          "confidence_label": "Moderate",
          "detected_model": "gpt",
          "model_confidence": 42.0,
          "analysis_details": {
            "method": "multi_factor_pattern_analysis_v2",
            "matched_patterns_sample": ["gpt: — (3x)"]
          }
        }
        ```
    """
    # Pydantic v2 config: protected_namespaces=() fixes warning about 'model_' prefix
    model_config = ConfigDict(protected_namespaces=())
    
    is_ai_generated: Optional[bool] = Field(
        None,
        description="Boolean decision: true if confidence ≥ 40%, false otherwise"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall AI generation probability (0-100%)"
    )
    confidence_label: Optional[str] = Field(
        None,
        description="Human-readable confidence level",
        examples=["Very Low", "Low", "Moderate", "High", "Very High"]
    )
    detected_model: Optional[str] = Field(
        None,
        description="Most likely AI model that generated content",
        examples=["gpt", "claude", "gemini", "llama", "mistral"]
    )
    model_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Confidence this specific model created it (≤ confidence_score)"
    )
    analysis_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed scoring breakdown with pattern matches and factors"
    )
