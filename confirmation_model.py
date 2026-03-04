from typing import Dict, Any

from logger import get_logger

log = get_logger(__name__)

class ConfirmationModel:
    """
    Implements Stage 3 of the CBIE Methodology: The Confirmation Model.
    Uses a Heuristic Weighted Score (justified by AHP) to combine frequency,
    consistency, and trend into a final decision.
    """
    
    def __init__(self):
        # AHP-derived weights (Example weights, would be derived formally in the actual research)
        # Adding 'credibility' based on input dataset
        self.weights = {
            'consistency': 0.35,
            'credibility': 0.30,
            'frequency': 0.25,
            'trend': 0.10
        }
        
        # Thresholds for classification
        self.threshold_stable = 0.70
        self.threshold_emerging = 0.40
        self.threshold_archive = 0.15

    def calculate_core_score(self, consistency_score: float, trend_score: float, frequency: int, max_frequency: int, credibility_score: float = 0.5) -> float:
        """
        Computes the final Heuristic Weighted Score.
        
        consistency_score: 0.0 (perfect) to 1.0 (inconsistent). We invert this for scoring.
        trend_score: -1.0 (decreasing) to 1.0 (increasing). We normalize this.
        frequency: raw count.
        max_frequency: max count across all clusters for normalization.
        credibility_score: 0.0 to 1.0, provided by BAC.
        """
        # 1. Normalize Consistency (higher is better)
        norm_consistency = 1.0 - consistency_score
        
        # 2. Normalize Frequency (0.0 to 1.0)
        norm_frequency = frequency / max_frequency if max_frequency > 0 else 0.0
        
        # 3. Normalize Trend (-1.0 to 1.0 -> 0.0 to 1.0)
        norm_trend = (trend_score + 1.0) / 2.0
        
        # 4. Credibility is already 0.0 to 1.0
        norm_credibility = credibility_score
        
        # Calculate weighted sum
        final_score = (
            (norm_consistency * self.weights['consistency']) +
            (norm_frequency * self.weights['frequency']) +
            (norm_trend * self.weights['trend']) +
            (norm_credibility * self.weights['credibility'])
        )
        log.debug(
            "Core score calculated",
            extra={
                "stage": "CONFIRMATION",
                "norm_consistency": round(norm_consistency, 4),
                "norm_frequency": round(norm_frequency, 4),
                "norm_credibility": round(norm_credibility, 4),
                "norm_trend": round(norm_trend, 4),
                "core_score": round(final_score, 4),
            }
        )
        return final_score

    def determine_status(self, score: float, is_fact: bool = False) -> str:
        """
        Classifies the topic. Absolute facts skip score validation.
        """
        if is_fact:
            return "Stable Fact"
            
        if score >= self.threshold_stable:
            status = "Stable"
        elif score >= self.threshold_emerging:
            status = "Emerging"
        elif score >= self.threshold_archive:
            status = "Noise"
        else:
            status = "ARCHIVED_CORE"
        
        log.debug("Status determined", extra={"stage": "CONFIRMATION", "core_score": round(score, 4), "status": status})
        return status
