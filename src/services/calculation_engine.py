import math
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CalculationEngine:
    """Engine for calculating behavior weights and metrics"""
    
    def __init__(self, alpha: float = 0.35, beta: float = 0.40, gamma: float = 0.25):
        """
        Initialize calculation engine with formula parameters
        
        Args:
            alpha: Weight for credibility (default: 0.35)
            beta: Weight for clarity (default: 0.40)
            gamma: Weight for extraction confidence (default: 0.25)
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.reinforcement_multiplier = 0.01
    
    def calculate_behavior_weight(
        self,
        credibility: float,
        clarity_score: float,
        extraction_confidence: float
    ) -> float:
        """
        Calculate Behavior Weight (BW)
        
        Formula: BW = credibility^α × clarity_score^β × extraction_confidence^γ
        
        Args:
            credibility: Trustworthiness (0-1)
            clarity_score: Explicitness (0-1)
            extraction_confidence: Model confidence (0-1)
            
        Returns:
            float: Behavior Weight
        """
        bw = (
            math.pow(credibility, self.alpha) *
            math.pow(clarity_score, self.beta) *
            math.pow(extraction_confidence, self.gamma)
        )
        
        logger.debug(
            f"BW = {credibility}^{self.alpha} × {clarity_score}^{self.beta} × "
            f"{extraction_confidence}^{self.gamma} = {bw:.6f}"
        )
        
        return bw
    
    def calculate_adjusted_behavior_weight(
        self,
        behavior_weight: float,
        reinforcement_count: int,
        decay_rate: float,
        days_since_last_seen: float
    ) -> float:
        """
        Calculate Adjusted Behavior Weight (ABW)
        
        Formula: ABW = BW × (1 + reinforcement_count × r) × e^(-decay_rate × days_since_last_seen)
        
        Args:
            behavior_weight: Base behavior weight
            reinforcement_count: Number of times behavior repeated
            decay_rate: Temporal decay rate
            days_since_last_seen: Days since last observation
            
        Returns:
            float: Adjusted Behavior Weight
        """
        reinforcement_factor = 1 + (reinforcement_count * self.reinforcement_multiplier)
        temporal_decay = math.exp(-decay_rate * days_since_last_seen)
        
        abw = behavior_weight * reinforcement_factor * temporal_decay
        
        logger.debug(
            f"ABW = {behavior_weight:.6f} × {reinforcement_factor:.6f} × {temporal_decay:.6f} = {abw:.6f}"
        )
        
        return abw
