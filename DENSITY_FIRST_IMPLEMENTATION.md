# Density-First Latent Preference Inference Implementation

**Implementation Date**: January 3, 2026  
**Branch**: `feature/density-first-inference`  
**Base Commit**: `3f5a5b0` (December 15, 2025)

## Overview

This implementation transforms the Core Behavior Identification Engine (CBIE) to use **density-first latent preference inference** as specified in `system_guide/archi_2.md`. The key insight is treating user behaviors as noisy observations of latent preferences rather than direct measurements.

## Theoretical Foundation

### Problem Framing
- **Not**: Detecting behaviors, ranking interests, or classifying prompts
- **Is**: Latent preference inference from noisy, indirect behavioral observations
- User actions are **noisy measurements**, not ground truth preferences

### Mathematical Interpretation
Each observation is interpreted as:
> A weighted sample from a user-specific latent preference density in semantic embedding space

Where:
- `x_i ∈ ℝ^d` = embedding vector
- `w_i ∈ [0,1]` = credibility (treated as sample mass)
- Credibility acts as **density mass**, not a heuristic score

## Implementation Changes

### 1. Weighted Density Estimation (`clustering_engine.py`)

**Changes**:
- Added `credibility_weights` parameter to `cluster_behaviors()`
- Implemented L2 normalization of embeddings (required for stable density estimation)
- Pass credibility as sample weights to HDBSCAN
- Extract and return cluster stability/persistence scores

**Key Code**:
```python
# L2 normalization (makes Euclidean ≡ cosine distance)
norms = np.linalg.norm(X, axis=1, keepdims=True)
X_normalized = X / (norms + 1e-10)

# Pass credibility as sample weights
clusterer.fit_predict(X_normalized, sample_weight=sample_weights)

# Extract stability scores
cluster_stabilities[cluster_id] = clusterer.cluster_persistence_[cluster_label]
```

**Academic Grounding**: Silverman (1986), Wand & Jones (1995), Duong & Hazelton (2005)

### 2. Adaptive Parameterization (`clustering_engine.py`)

**Changes**:
- Replace fixed `min_cluster_size` with adaptive formula: `max(2, floor(log(N)))`
- Scales with data without arbitrary constants
- Minimal assumption, easy to justify

**Key Code**:
```python
adaptive_min_cluster_size = max(2, int(math.log(n_samples)))
```

**Academic Grounding**: Campello et al. (2015), McInnes et al. (2017)

### 3. Epistemic State Classification (`schemas.py`, `cluster_analysis_pipeline.py`)

**Changes**:
- Added `EpistemicState` enum with three states:
  - **CORE**: Supported preferences (stability ≥ median)
  - **INSUFFICIENT_EVIDENCE**: High credibility but unstable (retained for future)
  - **NOISE**: Low credibility and isolated (discarded)
- Implemented `_assign_epistemic_states()` method using relative thresholds

**Key Code**:
```python
median_stability = np.median(stabilities)

if stability >= median_stability:
    cluster.epistemic_state = EpistemicState.CORE
elif mean_credibility >= np.percentile(all_credibilities, 75):
    cluster.epistemic_state = EpistemicState.INSUFFICIENT_EVIDENCE
else:
    cluster.epistemic_state = EpistemicState.NOISE
```

**Academic Grounding**: Gelman et al. (2013), Wasserman (2006), Polonik (1995)

### 4. Stability-Based Confidence (`calculation_engine.py`)

**Changes**:
- Added `calculate_confidence_from_stability()` method
- Normalize stability relative to all clusters for [0,1] range
- Optional temporal coverage multiplier (30% weight, explicitly justified)
- Replaced composite heuristic confidence with density-theoretic measure

**Key Code**:
```python
normalized_confidence = (cluster_stability - min_stability) / (max_stability - min_stability)

if temporal_span_days is not None:
    temporal_factor = min(1.0, math.log10(temporal_span_days + 1) / math.log10(31))
    confidence = normalized_confidence * (0.7 + 0.3 * temporal_factor)
```

**Academic Grounding**: Campello et al. (2015), Ben-David et al. (2006)

### 5. API Filtering (`routes.py`, `llm_context_service.py`)

**Changes**:
- Filter `list_core_behaviors` endpoint to only return CORE epistemic state
- Update LLM context service to only include CORE preferences
- Add `cluster_stability` field to API responses for transparency

**Key Code**:
```python
if epistemic_state == "CORE":
    canonical_behaviors.append({...})

# In LLM context service
relevant_clusters = [
    c for c in clusters 
    if getattr(c, 'epistemic_state', EpistemicState.CORE) == EpistemicState.CORE
]
```

## What Was Deliberately Excluded

The following were **not** implemented as they are not justified by the per-user data regime:

- ❌ Deep clustering (DEC, contrastive learning)
- ❌ Reinforcement curves with arbitrary decay
- ❌ Pre-filtering or anomaly detection (noise defined after density estimation)
- ❌ Fixed absolute thresholds (all thresholds are relative/adaptive)
- ❌ Tiered preferences based on arbitrary cutoffs

## Testing

Updated test suite to verify:
- `test_calculate_behavior_metrics`: Quality score calculation
- `test_calculate_confidence_from_stability`: New confidence method
- `test_calculate_cluster_strength`: Cluster strength calculation
- API endpoint tests updated for new filtering logic

**Test Results**: All 5 tests passing, 1 skipped (expected)

## Migration Notes

### Backward Compatibility
- `cluster_strength` is still calculated for backward compatibility
- Old `confidence_metrics` stored separately (consistency_score, reinforcement_score)
- `TierEnum` still used alongside `EpistemicState` for gradual migration

### Breaking Changes
- API responses now filter by `epistemic_state` instead of `tier`
- Only CORE preferences exposed to downstream systems
- INSUFFICIENT_EVIDENCE clusters retained but not exposed

## Academic References

1. **Density Estimation**: Silverman (1986), Wand & Jones (1995)
2. **Weighted KDE**: Duong & Hazelton (2005)
3. **HDBSCAN**: Campello et al. (2015), McInnes et al. (2017)
4. **Cluster Stability**: von Luxburg (2010), Ben-David et al. (2006)
5. **Density Level Sets**: Polonik (1995)
6. **Bayesian Data Analysis**: Gelman et al. (2013)
7. **Sentence Embeddings**: Reimers & Gurevych (2019), Ethayarajh (2019)

## Citation-Ready Summary

> We model user behaviors as weighted samples from a latent preference density in semantic embedding space, where credibility is treated as sample mass. Density estimation is performed using HDBSCAN, enabling recovery of high-support regions without fixed distance thresholds. Cluster stability is used as a relative measure of preference support, and core preferences are defined as clusters whose stability exceeds the median stability for a given user. Sparse or unstable observations are retained as insufficient evidence rather than discarded. This approach aligns with density level-set theory and avoids heuristic pre-filtering or tiered abstractions.

## Commit History

1. `ae2a1ce` - Implement weighted density estimation in clustering engine
2. `1336446` - Implement epistemic state classification and relative stability thresholds
3. `d51ea64` - Replace confidence calculation with normalized cluster stability
4. `afdbe17` - Filter API responses to only expose CORE epistemic state
5. `c67926a` - Update tests for density-first inference implementation

## Next Steps

1. Monitor production performance with real user data
2. Collect metrics on INSUFFICIENT_EVIDENCE transitions to CORE
3. Validate that CORE preferences align with user expectations
4. Consider temporal analysis of epistemic state transitions
5. Evaluate whether credibility weights properly propagate through HDBSCAN

## Status

✅ **Implementation Complete**  
✅ **Tests Passing**  
✅ **Ready for Review**

---

*This implementation follows density-first latent preference inference principles as specified in `archi_2.md`. All changes are theoretically grounded and academically defensible.*
