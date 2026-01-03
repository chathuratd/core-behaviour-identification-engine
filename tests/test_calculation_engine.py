import pytest
from src.services.calculation_engine import CalculationEngine
from src.models.schemas import BehaviorObservation


@pytest.fixture
def calc_engine():
    """Fixture for CalculationEngine"""
    return CalculationEngine()


def test_calculate_behavior_metrics(calc_engine):
    """Test behavior metrics calculation (replaces calculate_behavior_weight)"""
    # Create a mock BehaviorObservation
    behavior = BehaviorObservation(
        observation_id="test_obs_1",
        behavior_text="Test behavior",
        credibility=0.9,
        clarity_score=0.8,
        extraction_confidence=0.85,
        timestamp=1730000000,
        prompt_id="test_prompt_1"
    )
    
    metrics = calc_engine.calculate_behavior_metrics(behavior, current_timestamp=1730300000)
    
    assert "bw" in metrics
    assert "abw" in metrics
    assert 0.0 <= metrics["bw"] <= 1.0
    assert 0.0 <= metrics["abw"] <= 1.0
    assert isinstance(metrics["bw"], float)
    assert isinstance(metrics["abw"], float)


def test_calculate_cluster_strength(calc_engine):
    """Test cluster strength calculation"""
    timestamps = [1730000000, 1730100000, 1730200000]
    
    strength = calc_engine.calculate_cluster_strength(
        cluster_size=5,
        mean_abw=0.85,
        timestamps=timestamps,
        current_timestamp=1730300000
    )
    
    assert 0.0 <= strength <= 1.0
    assert isinstance(strength, float)


def test_calculate_confidence_from_stability(calc_engine):
    """Test confidence calculation from cluster stability (density-first approach)"""
    all_stabilities = [0.3, 0.5, 0.7, 0.9, 0.6]
    
    confidence = calc_engine.calculate_confidence_from_stability(
        cluster_stability=0.7,
        cluster_size=5,
        all_stabilities=all_stabilities,
        temporal_span_days=7.0
    )
    
    assert 0.0 <= confidence <= 1.0
    assert isinstance(confidence, float)

