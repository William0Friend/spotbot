"""
Ensemble Detector - Multi-Method Voting System

Combines multiple detection methods using weighted voting for higher accuracy.

Why ensemble approach:
- No single method is perfect (each has blind spots)
- Combining methods reduces false positives/negatives
- Different methods catch different types of AI generation
- High-trust methods (C2PA, watermarks) can override when confident

Ensemble strategies:
1. Weighted average: Each method contributes based on reliability
2. High-trust override: C2PA/watermark at 85%+ confidence overrides all
3. Confidence calibration: Scale results to account for method biases

Detection method hierarchy (by trust level):
1. Metadata/C2PA (95% weight): Cryptographic proof, highest trust
2. Watermark (85% weight): Invisible watermarks, very reliable
3. ML Classifier (40% weight): Transformer models, good but can be fooled
4. Pattern Attribution (30% weight): Model-specific tells, current MVP
5. Source Matching (20% weight): Plagiarism detection, lowest trust
6. Multimodal (60% weight): Cross-modal analysis (audio+video)

Current implementation:
- Phase 1: Pattern attribution only (MVP)
- Future: Add ML, metadata, watermark detectors incrementally
"""

from typing import List, Dict, Any
from .base_detector import BaseDetector, DetectorResult, DetectionMethod
from .text_detector import TextDetector
from .metadata_detector import MetadataDetector
import logging

logger = logging.getLogger(__name__)

class EnsembleDetector:
    """
    Multi-method ensemble detector using weighted voting.
    
    Combines results from multiple detection methods to produce more
    accurate and robust AI detection.
    
    Detection Pipeline:
    1. Filter applicable detectors (not all methods work on all content types)
    2. Run detectors in parallel (async for speed)
    3. Check for high-trust overrides (C2PA/watermark at 85%+ confidence)
    4. Calculate weighted average of all method confidences
    5. Determine model attribution from best-scoring method
    6. Return two-tier confidence + method breakdown
    
    Two-tier output:
    - Tier 1: Overall AI confidence (weighted combo of all methods)
    - Tier 2: Model attribution (which AI model most likely)
    
    Transparency:
    - method_breakdown: Shows each method's individual result
    - weights: Shows how much each method contributed
    - ensemble_method: "weighted_average" or "high_trust_override"
    
    Example result:
        {
          "is_ai_generated": true,
          "confidence_score": 75.5,
          "detected_model": "gpt",
          "model_confidence": 70.2,
          "analysis_details": {
            "ensemble_method": "weighted_average",
            "methods_used": ["pattern_attribution", "metadata"],
            "method_breakdown": {
              "pattern_attribution": {"confidence": 72, "model": "gpt"},
              "metadata": {"confidence": 85, "model": null}
            },
            "weights": {"pattern_attribution": 0.30, "metadata": 0.95}
          }
        }
    """
    
    def __init__(self):
        # Initialize all detectors
        self.detectors: List[BaseDetector] = [
            TextDetector(),  # Pattern-based (current MVP)
            MetadataDetector(),  # C2PA/EXIF (Phase 3)
            # WatermarkDetector(),  # Phase 3
            # MLDetector(),  # Phase 2
            # SourceMatchDetector(),  # Phase 5
        ]
        
        # Track which detectors are actually implemented
        self.active_detectors = [d for d in self.detectors if hasattr(d, 'detect')]
    
    async def detect(self, content: Any, content_type: str) -> Dict[str, Any]:
        """
        Run ensemble detection across all applicable methods.
        
        Args:
            content: Content to analyze
            content_type: 'text', 'image', 'audio', 'video', 'url'
        
        Returns:
            Combined detection result with two-tier confidence
        """
        logger.info(f"EnsembleDetector: Analyzing {content_type} content")
        
        # Filter detectors that can handle this content type
        applicable_detectors = [
            d for d in self.active_detectors 
            if d.is_applicable(content_type)
        ]
        
        if not applicable_detectors:
            logger.warning(f"No applicable detectors for content_type: {content_type}")
            return self._no_detection_result()
        
        # Run all applicable detectors
        results: List[DetectorResult] = []
        for detector in applicable_detectors:
            try:
                result = await detector.detect(content, content_type)
                results.append(result)
                logger.info(f"{detector.method.value}: confidence={result.confidence}%")
            except Exception as e:
                logger.error(f"Detector {detector.method.value} failed: {e}")
        
        if not results:
            return self._no_detection_result()
        
        # Combine results using weighted ensemble
        combined = self._combine_results(results, applicable_detectors)
        
        return combined
    
    def _combine_results(
        self, 
        results: List[DetectorResult], 
        detectors: List[BaseDetector]
    ) -> Dict[str, Any]:
        """
        Combine detector results using weighted voting.
        
        Strategy:
        1. High-trust methods (C2PA, watermark) override if confident
        2. Otherwise, weighted average of all methods
        3. Model attribution from best-scoring method
        """
        # Check for high-trust overrides
        for result, detector in zip(results, detectors):
            if detector.weight >= 0.85 and result.confidence >= 80:
                logger.info(f"High-trust override from {detector.method.value}")
                return self._format_result(
                    result=result,
                    method_breakdown={detector.method.value: result.to_dict()},
                    override_method=detector.method.value
                )
        
        # Weighted average for Tier 1 (overall AI confidence)
        total_weight = sum(d.weight for d in detectors if d.weight > 0)
        
        if total_weight == 0:
            return self._no_detection_result()
        
        weighted_confidence = sum(
            r.confidence * d.weight 
            for r, d in zip(results, detectors)
            if r.confidence is not None
        ) / total_weight
        
        # Determine Tier 2 (model attribution) from highest-confidence result
        best_result = max(
            (r for r in results if r.detected_model), 
            key=lambda r: r.model_confidence or 0,
            default=None
        )
        
        detected_model = best_result.detected_model if best_result else None
        model_confidence = best_result.model_confidence if best_result else None
        
        # Determine if AI-generated (threshold: 40%)
        is_ai = weighted_confidence >= 40
        
        # Build method breakdown for transparency
        method_breakdown = {
            r.method.value: r.to_dict() 
            for r in results
        }
        
        return {
            "is_ai_generated": is_ai,
            "confidence_score": round(weighted_confidence, 2),
            "confidence_label": self._get_confidence_label(weighted_confidence),
            "detected_model": detected_model,
            "model_confidence": round(model_confidence, 2) if model_confidence else None,
            "analysis_details": {
                "ensemble_method": "weighted_average",
                "methods_used": [r.method.value for r in results],
                "method_breakdown": method_breakdown,
                "weights": {d.method.value: d.weight for d in detectors}
            }
        }
    
    def _format_result(
        self, 
        result: DetectorResult, 
        method_breakdown: Dict[str, Any],
        override_method: str
    ) -> Dict[str, Any]:
        """Format a single detector result as final output"""
        return {
            "is_ai_generated": result.is_ai_generated,
            "confidence_score": round(result.confidence, 2),
            "confidence_label": self._get_confidence_label(result.confidence),
            "detected_model": result.detected_model,
            "model_confidence": round(result.model_confidence, 2) if result.model_confidence else None,
            "analysis_details": {
                "ensemble_method": "high_trust_override",
                "override_by": override_method,
                "method_breakdown": method_breakdown
            }
        }
    
    def _no_detection_result(self) -> Dict[str, Any]:
        """Return result when no detection is possible"""
        return {
            "is_ai_generated": None,
            "confidence_score": 0.0,
            "confidence_label": "Inconclusive",
            "detected_model": None,
            "model_confidence": None,
            "analysis_details": {
                "error": "No applicable detection methods",
                "message": "Unable to analyze this content type"
            }
        }
    
    def _get_confidence_label(self, confidence: float) -> str:
        """Convert confidence score to human-readable label"""
        if confidence >= 80:
            return "Very High"
        elif confidence >= 60:
            return "High"
        elif confidence >= 40:
            return "Moderate"
        elif confidence >= 20:
            return "Low"
        else:
            return "Very Low"
