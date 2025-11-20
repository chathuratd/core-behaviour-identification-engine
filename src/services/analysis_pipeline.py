from typing import Dict, Any
import logging

from src.services.embedding_service import EmbeddingService
from src.services.calculation_engine import CalculationEngine

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """Orchestrates the analysis flow for behavior processing"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.calc_engine = CalculationEngine()
    
    def process_behavior(
        self,
        behavior_text: str,
        credibility: float = 1.0,
        clarity_score: float = 1.0,
        extraction_confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        Process a behavior through the complete pipeline
        
        Steps:
        1. Generate embedding
        2. Calculate behavior weight
        3. Prepare for storage
        
        Args:
            behavior_text: The behavior observation text
            credibility: Credibility score (0-1)
            clarity_score: Clarity score (0-1)
            extraction_confidence: Extraction confidence (0-1)
            
        Returns:
            Dict containing processed behavior data
        """
        logger.info(f"Processing behavior: {behavior_text[:50]}...")
        
        # Step 1: Generate embedding
        embedding = self.embedding_service.get_embedding(behavior_text)
        logger.debug(f"Generated embedding with {len(embedding)} dimensions")
        
        # Step 2: Calculate weight
        behavior_weight = self.calc_engine.calculate_behavior_weight(
            credibility=credibility,
            clarity_score=clarity_score,
            extraction_confidence=extraction_confidence
        )
        logger.debug(f"Calculated behavior weight: {behavior_weight:.6f}")
        
        # Step 3: Prepare result
        result = {
            "behavior_text": behavior_text,
            "embedding": embedding,
            "behavior_weight": behavior_weight,
            "credibility": credibility,
            "clarity_score": clarity_score,
            "extraction_confidence": extraction_confidence
        }
        
        logger.info(f"Behavior processed successfully with weight {behavior_weight:.6f}")
        return result
