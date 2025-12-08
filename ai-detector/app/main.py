from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AnalysisRequest, AnalysisResponse
from app.detectors.text_detector import TextDetector
from app.detectors.image_detector import ImageDetector
from app.detectors.url_detector import URLDetector

app = FastAPI(
    title="SpotBot AI Detector",
    description="ML Service for AI Content Detection",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detectors
text_detector = TextDetector()
image_detector = ImageDetector()
url_detector = URLDetector()

@app.get("/")
async def root():
    return {
        "message": "SpotBot AI Detector Service",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "detectors": {
            "text": "ready",
            "image": "ready",
            "url": "ready"
        }
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    """
    Analyze content to detect if it's AI-generated and identify the model.
    """
    try:
        if request.content_type == "text":
            result = text_detector.analyze(request.content_text)
        
        elif request.content_type == "image":
            if not request.content_url:
                raise HTTPException(status_code=400, detail="Image URL required")
            result = image_detector.analyze(request.content_url)
        
        elif request.content_type == "video":
            # Video detection to be implemented
            result = {
                "is_ai_generated": None,
                "confidence_score": 0.0,
                "detected_model": None,
                "model_confidence": None,
                "analysis_details": {
                    "message": "Video detection not yet implemented",
                    "status": "pending"
                }
            }
        
        elif request.content_type == "url":
            if not request.content_url:
                raise HTTPException(status_code=400, detail="URL required")
            result = url_detector.analyze(request.content_url)
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported content type: {request.content_type}"
            )
        
        return AnalysisResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
