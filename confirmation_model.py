from typing import Dict, Any

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
        
        return final_score

    def determine_status(self, score: float, is_fact: bool = False) -> str:
        """
        Classifies the topic. Absolute facts skip score validation.
        """
        if is_fact:
            return "Stable Fact"
            
        if score >= self.threshold_stable:
            return "Stable"
        elif score >= self.threshold_emerging:
            return "Emerging"
        elif score >= self.threshold_archive:
            return "Noise"
        else:
            return "ARCHIVED_CORE"
