"""
Base Detector Interface

Abstract base class that all detection methods inherit from.

Why abstract base class:
- Enforces consistent interface across all detectors
- Type safety: Ensures all detectors implement required methods
- Documentation: Clear contract for what each detector must provide
- Testability: Mock detectors easily for testing ensemble logic

Design pattern: Strategy Pattern
- Each detector is a strategy for AI detection
- Ensemble detector uses multiple strategies and combines results
- Easy to add new detection methods without changing existing code

Detection method types (DetectionMethod enum):
1. METADATA: C2PA, EXIF, signed manifests (highest trust)
2. WATERMARK: Invisible watermarks embedded by AI tools
3. ML_CLASSIFIER: Transformer models trained to detect AI text
4. PATTERN_ATTRIBUTION: Model-specific vocabulary/formatting (current MVP)
5. SOURCE_MATCHING: Web search to find if content is copied
6. MULTIMODAL: Cross-modal analysis (audio+video correlation)

All detectors return DetectorResult with:
- confidence: 0-100% AI probability
- is_ai_generated: Boolean decision
- detected_model: Which AI (gpt/claude/etc.)
- method: Which detection method was used
- details: Method-specific metadata
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

class DetectionMethod(Enum):
    """
    Enumeration of available detection methods.
    
    Each method has different strengths, weaknesses, and trust levels.
    
    Methods:
        METADATA: C2PA/EXIF analysis (95% weight, cryptographic proof)
        WATERMARK: Invisible watermark detection (85% weight, very reliable)
        ML_CLASSIFIER: Trained ML models (40% weight, can be fooled)
        PATTERN_ATTRIBUTION: Vocabulary patterns (30% weight, current MVP)
        SOURCE_MATCHING: Plagiarism detection (20% weight, lowest trust)
        MULTIMODAL: Cross-modal analysis (60% weight, audio+video)
    """
    METADATA = "metadata"  # C2PA, EXIF, signed manifests
    WATERMARK = "watermark"  # Invisible watermarks
    ML_CLASSIFIER = "ml_classifier"  # Transformer models
    PATTERN_ATTRIBUTION = "pattern_attribution"  # Model-specific patterns
    SOURCE_MATCHING = "source_matching"  # Web/plagiarism search
    MULTIMODAL = "multimodal"  # Cross-modal audio+video  # Image/audio/video analysis

class DetectorResult:
    """Standard result format for all detectors"""
    
    def __init__(
        self,
        method: DetectionMethod,
        is_ai_generated: Optional[bool],
        confidence: float,  # 0-100
        detected_model: Optional[str] = None,
        model_confidence: Optional[float] = None,
        evidence: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.method = method
        self.is_ai_generated = is_ai_generated
        self.confidence = confidence
        self.detected_model = detected_model
        self.model_confidence = model_confidence
        self.evidence = evidence or {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "method": self.method.value,
            "is_ai_generated": self.is_ai_generated,
            "confidence": round(self.confidence, 2),
            "detected_model": self.detected_model,
            "model_confidence": round(self.model_confidence, 2) if self.model_confidence else None,
            "evidence": self.evidence,
            "metadata": self.metadata
        }

class BaseDetector(ABC):
    """Abstract base class for all detection methods"""
    
    def __init__(self, method: DetectionMethod):
        self.method = method
        self.weight = self._get_default_weight()
    
    def _get_default_weight(self) -> float:
        """Get default weight for this detection method"""
        weights = {
            DetectionMethod.METADATA: 0.95,
            DetectionMethod.WATERMARK: 0.85,
            DetectionMethod.ML_CLASSIFIER: 0.40,
            DetectionMethod.PATTERN_ATTRIBUTION: 0.30,
            DetectionMethod.SOURCE_MATCHING: 0.20,
            DetectionMethod.MULTIMODAL: 0.60,
        }
        return weights.get(self.method, 0.50)
    
    @abstractmethod
    async def detect(self, content: Any, content_type: str) -> DetectorResult:
        """
        Detect if content is AI-generated.
        
        Args:
            content: The content to analyze (text, bytes, URL, etc.)
            content_type: Type of content ('text', 'image', 'audio', 'video', 'url')
        
        Returns:
            DetectorResult with detection results
        """
        pass
    
    @abstractmethod
    def is_applicable(self, content_type: str) -> bool:
        """
        Check if this detector can handle the given content type.
        
        Args:
            content_type: Type of content
        
        Returns:
            True if this detector can analyze this content type
        """
        pass
    
    def set_weight(self, weight: float):
        """Set custom weight for this detector (0-1)"""
        self.weight = max(0.0, min(1.0, weight))
