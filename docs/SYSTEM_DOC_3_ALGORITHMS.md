# Part 3: Core Algorithms & Processing Logic

**Document:** SYSTEM_DOC_3_ALGORITHMS.md  
**Version:** 1.0  
**Date:** January 3, 2026

[← Back to Part 2](SYSTEM_DOC_2_DATA_MODELS.md) | [Back to Master Index](SYSTEM_DOCUMENTATION_MASTER.md) | [Next: Part 4 - Components →](SYSTEM_DOC_4_COMPONENTS.md)

---

## Table of Contents

1. [Algorithm Overview](#1-algorithm-overview)
2. [HDBSCAN Clustering Algorithm](#2-hdbscan-clustering-algorithm)
3. [Stability Calculation & Extraction](#3-stability-calculation--extraction)
4. [Classification Logic](#4-classification-logic)
5. [Credibility Weighting & Aggregation](#5-credibility-weighting--aggregation)
6. [Confidence Score Calculation](#6-confidence-score-calculation)
7. [Threshold Mechanisms](#7-threshold-mechanisms)
8. [Complete Processing Pipeline](#8-complete-processing-pipeline)

---

## 1. Algorithm Overview

### 1.1 Processing Pipeline

The system implements a **five-stage pipeline**:

```
┌──────────────────────────────────────────────────────────────────┐
│  Stage 1: Data Preparation                                       │
│  - Load behaviors from Qdrant                                    │
│  - Extract embeddings (1536-dim vectors)                         │
│  - Extract credibility scores                                    │
│  - L2 normalize embeddings                                       │
└──────────────────┬───────────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────────┐
│  Stage 2: Density-Based Clustering (HDBSCAN)                     │
│  - Compute mutual reachability distance                          │
│  - Build minimum spanning tree                                   │
│  - Extract cluster hierarchy                                     │
│  - Assign cluster labels                                         │
│  - Calculate cluster persistence (stability)                     │
└──────────────────┬───────────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────────┐
│  Stage 3: Stability Extraction                                   │
│  - Read cluster_persistence_ from HDBSCAN                        │
│  - Map cluster labels to stability scores                        │
│  - Identify noise points (label = -1)                            │
└──────────────────┬───────────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────────┐
│  Stage 4: Classification                                         │
│  - Apply stability threshold (0.15)                              │
│  - Apply credibility threshold (0.5)                             │
│  - Assign EpistemicState (CORE/INSUFFICIENT_EVIDENCE/NOISE)      │
└──────────────────┬───────────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────────┐
│  Stage 5: Output Generation                                      │
│  - Group observations by cluster                                 │
│  - Calculate confidence scores (= stability)                     │
│  - Filter: Keep only CORE clusters                               │
│  - Format as CoreBehaviorProfile                                 │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Algorithmic Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Clustering Algorithm** | HDBSCAN | Handles variable density, automatic parameter selection, provides stability scores |
| **Distance Metric** | Euclidean on L2-normalized vectors | Equivalent to cosine distance, computationally efficient |
| **min_cluster_size** | Adaptive: max(3, 0.2×N) for N<20 | Prevents trivial 2-point clusters while allowing small-dataset clustering |
| **Stability Threshold** | 0.15 (heuristic) | Filters unstable clusters, not calibrated on ground truth |
| **Credibility Threshold** | 0.5 | Separates reliable observations from noise |
| **Confidence Metric** | cluster_stability (1:1 mapping) | Direct use of HDBSCAN persistence, no composite score |

---

## 2. HDBSCAN Clustering Algorithm

### 2.1 Algorithm Overview

**HDBSCAN** = Hierarchical Density-Based Spatial Clustering of Applications with Noise

**Core Idea:** Clusters are regions of higher point density separated by regions of lower density

**Key Properties:**
- Does not require specifying number of clusters (unlike k-means)
- Can identify clusters of varying densities
- Labels outliers as noise (label = -1)
- Provides stability scores for each cluster

### 2.2 Implementation in CBIE

**File:** `src/services/clustering_engine.py`

**Configuration:**
```python
clusterer = HDBSCAN(
    min_cluster_size=adaptive_min_cluster_size,  # 3 or 20% of N
    min_samples=1,                                # Sensitivity to noise
    cluster_selection_epsilon=0.15,               # Merge similar clusters
    metric='euclidean',                           # On L2-normalized vectors
    cluster_selection_method='eom'                # Excess of Mass
)
```

**Parameters Explained:**

**`min_cluster_size`**: Minimum points required to form a cluster
- **Adaptive calculation** (N = number of behavior vectors):
  ```python
  if N < 20:
      min_cluster_size = max(3, int(0.20 * N))  # 20% rule with floor of 3
  else:
      min_cluster_size = max(3, int(log(N)))     # Log-based scaling
  ```
- **Examples:**
  - N=3: min_cluster_size=3 (requires 100% agreement)
  - N=5: min_cluster_size=3 (requires 60% agreement)
  - N=15: min_cluster_size=3 (requires 20% agreement)
  - N=50: min_cluster_size=max(3, 3) = 3
  - N=100: min_cluster_size=max(3, 4) = 4
  - N=1000: min_cluster_size=max(3, 6) = 6

**Why adaptive?**
- Prevents over-clustering in small datasets
- Allows meaningful clustering in larger datasets
- **Trade-off:** Strict on small N (conservative), relaxed on large N (flexible)

**`min_samples`**: Controls noise sensitivity
- Value: 1 (single-linkage style)
- Lower = more points clustered
- Higher = more points labeled as noise
- **Choice:** 1 (permissive, let stability threshold filter)

**`cluster_selection_epsilon`**: Distance threshold for merging clusters
- Value: 0.15
- Clusters closer than epsilon are merged
- **Purpose:** Reduce fragmentation of semantically similar behaviors

**`metric`**: Distance function
- Value: 'euclidean'
- **Context:** Applied to L2-normalized vectors
- **Effect:** Equivalent to cosine similarity (angular distance)

**`cluster_selection_method`**: Algorithm for extracting flat clustering from hierarchy
- Value: 'eom' (Excess of Mass)
- **Alternative:** 'leaf' (less stable)
- **Choice:** EOM provides more stable clusters

### 2.3 Embedding Normalization

**Critical Preprocessing Step:**

```python
# L2 normalize embeddings
X = np.array(embeddings)  # Shape: (N, 1536)
norms = np.linalg.norm(X, axis=1, keepdims=True)  # Shape: (N, 1)
X_normalized = X / (norms + 1e-10)  # Add epsilon for numerical stability
```

**Why normalize?**
1. **Distance equivalence:** Euclidean distance on unit vectors = cosine similarity
   - cos(θ) = (A·B) / (||A|| ||B||)
   - If ||A|| = ||B|| = 1: cos(θ) = A·B
   - Euclidean: sqrt((A-B)·(A-B)) = sqrt(2 - 2cos(θ))

2. **Stability:** Prevents magnitude differences from dominating clustering

3. **Consistency:** Azure OpenAI embeddings not inherently normalized

**Effect:** Clustering based purely on semantic direction, not embedding magnitude

### 2.4 Clustering Process

**Step-by-Step:**

**1. Mutual Reachability Distance**
```
For each point pair (p, q):
  core_distance(p) = distance to k-th nearest neighbor
  core_distance(q) = distance to k-th nearest neighbor
  mutual_reach_dist(p, q) = max(core_distance(p), core_distance(q), dist(p, q))
```

**Purpose:** Reduces impact of noise by expanding distance in sparse regions

**2. Minimum Spanning Tree (MST)**
- Build MST using mutual reachability distances
- Tree connects all points with minimum total edge weight

**3. Cluster Hierarchy**
- Remove edges from MST in increasing distance order
- Track connected components as they split
- Build dendrogram (tree diagram) of splits

**4. Cluster Extraction**
- Use EOM (Excess of Mass) to select stable clusters from hierarchy
- Assign flat cluster labels

**5. Stability Calculation**
- For each cluster: stability = integral of excess mass over lambda (inverse distance)
- Higher stability = cluster persists across wider range of distance thresholds

**Output:**
```python
{
  "labels": [0, 0, -1, 1, 0, 1, -1],  # Cluster assignment per behavior
  "cluster_persistence_": [0.856, 0.234],  # Stability per cluster
  "num_clusters": 2,
  "noise_count": 2
}
```

### 2.5 Cluster Stability (Persistence)

**Definition:** How robust a cluster is across different density thresholds

**Mathematical Intuition:**
- HDBSCAN builds hierarchy of clusters at different distance scales (lambda = 1/distance)
- A cluster exists from lambda_birth to lambda_death
- **Stability = area under the cluster's existence curve**

**Interpretation:**
- **High stability (0.8-1.0):** Cluster exists across wide range of distances → robust semantic pattern
- **Medium stability (0.3-0.7):** Cluster exists but somewhat fragile
- **Low stability (0.0-0.3):** Cluster barely forms, very sensitive to parameters
- **Threshold (0.15):** Below this, cluster considered too unstable to trust

**Example:**
```
Cluster A: Forms at distance 0.1, dies at distance 0.9
  → Exists across wide range → high stability (0.85)

Cluster B: Forms at distance 0.45, dies at distance 0.55
  → Exists in narrow range → low stability (0.12)

Decision:
  Cluster A: stability 0.85 >= 0.15 → CORE candidate
  Cluster B: stability 0.12 < 0.15 → INSUFFICIENT_EVIDENCE or NOISE
```

---

## 3. Stability Calculation & Extraction

### 3.1 Extraction Process

**File:** `src/services/clustering_engine.py` (lines 160-220)

**Code:**
```python
def _extract_cluster_stabilities(
    self, 
    clusterer: HDBSCAN, 
    cluster_labels: np.ndarray
) -> Dict[int, float]:
    """
    Extract stability scores from HDBSCAN cluster_persistence_
    
    Returns:
        Dict mapping cluster_label → stability_score
    """
    cluster_stabilities = {}
    
    # Get unique cluster labels (excluding noise = -1)
    unique_clusters = set(cluster_labels)
    unique_clusters.discard(-1)
    
    # Extract raw stability scores
    if hasattr(clusterer, 'cluster_persistence_'):
        raw_stabilities = clusterer.cluster_persistence_
        logger.debug(f"HDBSCAN stability scores: {raw_stabilities}")
        
        for cluster_label in unique_clusters:
            if cluster_label < len(raw_stabilities):
                stability = float(raw_stabilities[cluster_label])
                cluster_stabilities[cluster_label] = stability
            else:
                # Fallback if index out of bounds
                logger.warning(
                    f"Cluster {cluster_label} exceeds stability array length"
                )
                cluster_stabilities[cluster_label] = 0.5
    else:
        # HDBSCAN didn't generate stability scores
        logger.warning("No cluster_persistence_ attribute found")
        for cluster_label in unique_clusters:
            cluster_stabilities[cluster_label] = 0.5
    
    return cluster_stabilities
```

**Key Points:**

1. **Source:** `clusterer.cluster_persistence_` attribute
   - This is a numpy array with length = number of clusters
   - Index corresponds to cluster label (0, 1, 2, ...)

2. **Mapping:** cluster_label → stability_score
   ```
   cluster_persistence_ = [0.856, 0.234, 0.672]
   →
   {0: 0.856, 1: 0.234, 2: 0.672}
   ```

3. **Edge Cases:**
   - No persistence attribute → fallback to 0.5
   - Index out of bounds → fallback to 0.5
   - Noise points (label=-1) → not included in stabilities dict

4. **Fallback Strategy:**
   - Value: 0.5 (neutral, above INSUFFICIENT_EVIDENCE threshold)
   - Reason: Conservative assumption when data unavailable

### 3.2 Stability Properties

**Range:** 0.0 to 1.0 (theoretically unbounded, practically ≤1.0)

**Distribution in Real Data:**
- **0.0-0.1:** Very weak clusters, likely artifacts
- **0.1-0.3:** Marginal clusters, unstable
- **0.3-0.6:** Moderate stability, reasonable patterns
- **0.6-1.0:** Strong clusters, robust patterns

**Factors Affecting Stability:**
- **Cluster compactness:** Tighter clusters → higher stability
- **Cluster density:** Denser clusters → higher stability
- **Separation from neighbors:** More isolated → higher stability
- **Dataset size:** Larger N → stability values may shift

**Sensitivity:**
- **Sensitive to:** min_cluster_size, min_samples, embedding quality
- **Insensitive to:** small perturbations in member points (by design)

---

## 4. Classification Logic

### 4.1 Three-State Classification Algorithm

**File:** `src/services/cluster_analysis_pipeline.py`

**Pseudocode:**
```
FOR each behavior observation:
    cluster_label = clustering_result.labels[observation_index]
    
    IF cluster_label == -1:  # Noise point
        mean_credibility = credibility[observation]
        IF mean_credibility >= 0.5:
            state = INSUFFICIENT_EVIDENCE  # High quality but isolated
        ELSE:
            state = NOISE  # Low quality and isolated
    ELSE:  # Part of a cluster
        cluster_stability = stability_scores[cluster_label]
        mean_credibility = average(credibility for all cluster members)
        
        IF cluster_stability >= 0.15:  # Stable cluster
            IF mean_credibility >= 0.5:
                state = CORE  # Stable and credible ✓
            ELSE:
                state = INSUFFICIENT_EVIDENCE  # Stable but low credibility
        ELSE:  # Unstable cluster
            IF mean_credibility >= 0.5:
                state = INSUFFICIENT_EVIDENCE  # Credible but unstable
            ELSE:
                state = NOISE  # Unstable and low credibility
    
    RETURN state
```

**Implementation:**
```python
def _classify_behavior(
    self,
    behavior_id: str,
    cluster_label: int,
    cluster_stability: float,
    mean_credibility: float
) -> Tuple[EpistemicState, str]:
    """
    Classify a single behavior based on cluster stability and credibility
    
    Returns:
        (EpistemicState, explanation_string)
    """
    if cluster_label == -1:  # Noise point
        if mean_credibility >= 0.5:
            return (
                EpistemicState.INSUFFICIENT_EVIDENCE,
                f"Isolated point (no cluster) but high credibility ({mean_credibility:.3f})"
            )
        else:
            return (
                EpistemicState.NOISE,
                f"Isolated point with low credibility ({mean_credibility:.3f})"
            )
    else:  # Part of a cluster
        if cluster_stability >= 0.15:  # Stable cluster
            if mean_credibility >= 0.5:
                return (
                    EpistemicState.CORE,
                    f"Stable cluster ({cluster_stability:.3f}) with high credibility ({mean_credibility:.3f})"
                )
            else:
                return (
                    EpistemicState.INSUFFICIENT_EVIDENCE,
                    f"Stable cluster ({cluster_stability:.3f}) but low credibility ({mean_credibility:.3f})"
                )
        else:  # Unstable cluster
            if mean_credibility >= 0.5:
                return (
                    EpistemicState.INSUFFICIENT_EVIDENCE,
                    f"Unstable cluster ({cluster_stability:.3f}) despite high credibility ({mean_credibility:.3f})"
                )
            else:
                return (
                    EpistemicState.NOISE,
                    f"Unstable cluster ({cluster_stability:.3f}) with low credibility ({mean_credibility:.3f})"
                )
```

### 4.2 Decision Tree Visualization

```
                     Behavior Observation
                             │
                             ▼
                   [Is it in a cluster?]
                    /                  \
                  NO                    YES
                  │                      │
                  ▼                      ▼
         [Check credibility]   [Check cluster stability]
            /         \             /              \
    cred≥0.5      cred<0.5    stab≥0.15        stab<0.15
       │             │            │                │
       ▼             ▼            ▼                ▼
  INSUFFICIENT    NOISE   [Check credibility] [Check credibility]
   _EVIDENCE                  /      \            /      \
                        cred≥0.5  cred<0.5  cred≥0.5  cred<0.5
                           │         │         │         │
                           ▼         ▼         ▼         ▼
                         CORE    INSUFF    INSUFF     NOISE
                                 _EVID     _EVID
```

### 4.3 Classification Examples

**Example 1: CORE Behavior**
```python
observation_id = "obs_1"
cluster_label = 0
cluster_stability = 0.856
mean_credibility = 0.87

→ In cluster (0)
→ Stable (0.856 >= 0.15) ✓
→ Credible (0.87 >= 0.5) ✓
→ Classification: CORE
→ Explanation: "Stable cluster (0.856) with high credibility (0.87)"
```

**Example 2: INSUFFICIENT_EVIDENCE (Unstable)**
```python
observation_id = "obs_4"
cluster_label = 1
cluster_stability = 0.12
mean_credibility = 0.82

→ In cluster (1)
→ Unstable (0.12 < 0.15) ✗
→ Credible (0.82 >= 0.5) ✓
→ Classification: INSUFFICIENT_EVIDENCE
→ Explanation: "Unstable cluster (0.12) despite high credibility (0.82)"
```

**Example 3: NOISE (Isolated + Low Credibility)**
```python
observation_id = "obs_7"
cluster_label = -1
mean_credibility = 0.35

→ Not in cluster (-1)
→ Low credibility (0.35 < 0.5) ✗
→ Classification: NOISE
→ Explanation: "Isolated point with low credibility (0.35)"
```

**Example 4: INSUFFICIENT_EVIDENCE (Isolated + High Credibility)**
```python
observation_id = "obs_9"
cluster_label = -1
mean_credibility = 0.75

→ Not in cluster (-1)
→ High credibility (0.75 >= 0.5) ✓
→ Classification: INSUFFICIENT_EVIDENCE
→ Explanation: "Isolated point (no cluster) but high credibility (0.75)"
```

---

## 5. Credibility Weighting & Aggregation

### 5.1 Credibility Calculation

**Source:** Behavior extraction LLM

**Components:**
```python
credibility = (
    extraction_confidence * 0.4 +  # LLM's certainty
    clarity_score * 0.3 +           # Statement explicitness
    source_reliability * 0.3        # Context trust
)
```

**Normalization:** 0.0 to 1.0

**Interpretation:**
- **0.9-1.0:** High-confidence, explicit observation
- **0.7-0.9:** Reliable, clear inference
- **0.5-0.7:** Moderate confidence, some ambiguity
- **0.3-0.5:** Weak signal, uncertain
- **0.0-0.3:** Very low confidence, possible error

### 5.2 Cluster-Level Aggregation

**Method:** Simple arithmetic mean

```python
def calculate_mean_credibility(cluster_members: List[BehaviorObservation]) -> float:
    """Calculate mean credibility across cluster members"""
    credibilities = [obs.credibility for obs in cluster_members]
    return sum(credibilities) / len(credibilities)
```

**Why mean (not weighted)?**
- Simple, interpretable
- Avoids double-weighting (credibility already influenced clustering via sample weights)
- Conservative: One low-credibility member lowers cluster average

**Alternative Approaches (Not Implemented):**
- Weighted mean by observation recency
- Median (more robust to outliers)
- Minimum (most conservative)

### 5.3 Credibility Usage in System

**Stage 1: Clustering** (Limited Impact)
- Credibility passed as `sample_weight` to HDBSCAN
- **Effect:** May influence density estimation (not guaranteed by HDBSCAN implementation)
- **Primary role:** Post-clustering classification

**Stage 2: Classification** (Primary Role)
- Threshold: 0.5
- Determines INSUFFICIENT_EVIDENCE vs NOISE for unstable/isolated points
- Does NOT affect CORE classification (stability is primary gate)

**Stage 3: Output** (Metadata)
- Included in behavior metadata for transparency
- Not used in downstream processing

### 5.4 Known Limitation

**Issue:** Credibility is a post-hoc filter, not integrated into density estimation

**Consequence:** Possible scenarios:
- Dense low-credibility behaviors → promoted to CORE
- Sparse high-credibility signals → suppressed as NOISE

**Mitigation:** Two-stage filtering (clustering + credibility gate) partially compensates

**Future Work:** Credibility-weighted distance metric or sample duplication

---

## 6. Confidence Score Calculation

### 6.1 Current Implementation

**Simple Formula:**
```python
confidence = cluster_stability  # 1:1 mapping
```

**Rationale:**
- Stability is the primary quality metric
- Direct interpretation: stability = confidence
- No composite score complexity

**File:** `src/services/calculation_engine.py`

```python
def calculate_confidence_from_stability(
    self,
    cluster_stability: float,
    temporal_decay_factor: Optional[float] = None
) -> float:
    """
    Calculate confidence score from cluster stability
    
    Args:
        cluster_stability: HDBSCAN persistence score (0.0-1.0)
        temporal_decay_factor: Optional decay multiplier
        
    Returns:
        Confidence score (0.0-1.0)
    """
    confidence = cluster_stability  # Direct mapping
    
    if temporal_decay_factor is not None:
        confidence *= temporal_decay_factor  # Apply decay if provided
    
    # Clamp to valid range
    return max(0.0, min(1.0, confidence))
```

### 6.2 Temporal Decay (Optional)

**Purpose:** Reduce confidence for old observations

**Formula:**
```python
decay_factor = exp(-decay_rate * days_since_observation)
confidence = cluster_stability * decay_factor
```

**Parameters:**
- `decay_rate`: 0.01 (default)
- `days_since_observation`: (current_time - last_seen) / 86400

**Effect:**
- Recent observations (0-30 days): decay_factor ≈ 0.74-1.0
- Old observations (90+ days): decay_factor ≈ 0.41
- Very old (365 days): decay_factor ≈ 0.03

**Current Status:** **Not actively used** (temporal decay disabled by default)

### 6.3 Legacy Composite Score (Deprecated)

**Old Formula (Before Density-First):**
```python
confidence = consistency_score * reinforcement_score

where:
  consistency_score = semantic_similarity_of_cluster_members
  reinforcement_score = normalized_observation_count
```

**Why deprecated?**
- Consistency redundant (clustering already ensures semantic similarity)
- Reinforcement biases toward frequency (contradicts density-first philosophy)
- Stability score is more principled (from HDBSCAN theory)

**Migration:** All code now uses `cluster_stability` as `confidence`

---

## 7. Threshold Mechanisms

### 7.1 Stability Threshold

**Value:** 0.15  
**Type:** Absolute (fixed)  
**Status:** **Heuristic, not calibrated**

**Purpose:** Separate stable clusters from unstable ones

**Justification:**
- Empirical observation: stability <0.15 often indicates fragile clusters
- Conservative choice to minimize false positives
- **Not validated on ground truth data**

**Sensitivity Analysis Results:**
- Tested thresholds: 0.05, 0.10, 0.15, 0.20
- **Finding:** With N=3-5 synthetic data, all thresholds produce 0 CORE behaviors
- **Conclusion:** Clustering infeasibility dominates, threshold secondary

**Future Work:**
- Calibrate on labeled preference data
- Adaptive thresholds based on dataset size
- User-configurable per application

### 7.2 Credibility Threshold

**Value:** 0.5  
**Type:** Absolute (fixed)  
**Purpose:** Separate reliable observations from noisy ones

**Usage:**
- Primary: INSUFFICIENT_EVIDENCE vs NOISE classification
- Secondary: Quality gate for CORE behaviors (though stability is primary)

**Interpretation:**
- ≥0.5: Observation trusted (even if isolated/unstable)
- <0.5: Observation questioned, marked as NOISE

**Rationale:**
- Midpoint of 0-1 range
- Conservative but not overly strict
- No theoretical grounding (pragmatic choice)

### 7.3 min_cluster_size (Clustering Parameter)

**Value:** Adaptive  
**Formula:**
```python
if N < 20:
    min_cluster_size = max(3, int(0.20 * N))
else:
    min_cluster_size = max(3, int(log(N)))
```

**Purpose:** Minimum points to form a cluster

**Justification:**
- **Floor of 3:** Prevents trivial 2-point semantic coincidences
- **20% rule (N<20):** Conservative for small datasets
- **Log scaling (N≥20):** Standard HDBSCAN practice

**Interaction with Dataset Size:**
| N | min_cluster_size | Required Agreement |
|---|------------------|---------------------|
| 3 | 3 | 100% |
| 5 | 3 | 60% |
| 10 | 3 | 30% |
| 20 | 3 | 15% |
| 50 | 3 | 6% |
| 100 | 4 | 4% |

**Critical Insight:**
- Small N (3-5) + min_cluster_size=3 → clustering infeasibility
- **This is intentional:** System abstains on insufficient data

### 7.4 Threshold Interactions

```
Dataset → Clustering (min_cluster_size) → Clusters formed?
                                              │
                          ┌───────────────────┴──────────────────┐
                          │                                      │
                         YES                                     NO
                          │                                      │
                          ▼                                      ▼
              Apply Stability Threshold (0.15)           All → NOISE or
                          │                               INSUFFICIENT_EVIDENCE
                          │                                (abstention)
                  ┌───────┴────────┐
                  │                │
          stable≥0.15         stable<0.15
                  │                │
                  ▼                ▼
        Apply Credibility    Apply Credibility
         Threshold (0.5)     Threshold (0.5)
                  │                │
           ┌──────┴─────┐   ┌──────┴─────┐
           │            │   │            │
       cred≥0.5     cred<0.5  cred≥0.5   cred<0.5
           │            │   │            │
           ▼            ▼   ▼            ▼
         CORE        INSUFF INSUFF     NOISE
                     _EVID  _EVID
```

**Key Takeaway:** Clustering is the **primary gate**. If clustering fails (0 clusters), threshold values are irrelevant.

---

## 8. Complete Processing Pipeline

### 8.1 Step-by-Step Walkthrough

**Input:** User ID ("user_665390")

**Step 1: Load Data**
```python
# Query Qdrant for all user behaviors
behaviors = qdrant_db.get_behaviors(user_id)

# Extract components
embeddings = [b.embedding for b in behaviors]  # (N, 1536)
behavior_ids = [b.observation_id for b in behaviors]
credibilities = [b.credibility for b in behaviors]
```

**Step 2: Normalize Embeddings**
```python
X = np.array(embeddings)
norms = np.linalg.norm(X, axis=1, keepdims=True)
X_normalized = X / (norms + 1e-10)
```

**Step 3: Cluster**
```python
clusterer = HDBSCAN(
    min_cluster_size=max(3, int(0.20 * len(embeddings))),
    min_samples=1,
    cluster_selection_epsilon=0.15,
    metric='euclidean'
)
labels = clusterer.fit_predict(X_normalized)
stabilities = clusterer.cluster_persistence_
```

**Step 4: Extract Cluster Info**
```python
# Map labels to observation IDs
clusters = {}
for obs_id, label in zip(behavior_ids, labels):
    if label != -1:  # Not noise
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(obs_id)

# Map labels to stabilities
cluster_stabilities = {}
for cluster_id, stability in enumerate(stabilities):
    cluster_stabilities[cluster_id] = stability
```

**Step 5: Classify Each Cluster**
```python
classified_clusters = []

for cluster_id, member_ids in clusters.items():
    # Get cluster members
    members = [b for b in behaviors if b.observation_id in member_ids]
    
    # Calculate mean credibility
    mean_cred = sum(m.credibility for m in members) / len(members)
    
    # Get stability
    stability = cluster_stabilities[cluster_id]
    
    # Classify
    if stability >= 0.15:
        if mean_cred >= 0.5:
            state = EpistemicState.CORE
        else:
            state = EpistemicState.INSUFFICIENT_EVIDENCE
    else:
        if mean_cred >= 0.5:
            state = EpistemicState.INSUFFICIENT_EVIDENCE
        else:
            state = EpistemicState.NOISE
    
    cluster_obj = BehaviorCluster(
        cluster_id=f"cluster_{cluster_id}",
        user_id=user_id,
        observation_ids=member_ids,
        cluster_stability=stability,
        epistemic_state=state,
        confidence=stability,  # Direct mapping
        ...
    )
    
    classified_clusters.append(cluster_obj)
```

**Step 6: Filter Output**
```python
# Keep only CORE clusters
core_clusters = [c for c in classified_clusters if c.epistemic_state == EpistemicState.CORE]

# Format as profile
profile = CoreBehaviorProfile(
    user_id=user_id,
    generated_at=int(time.time()),
    behavior_clusters=core_clusters,
    statistics={
        "total_behaviors_analyzed": len(behaviors),
        "clusters_formed": len(clusters),
        ...
    }
)
```

**Output:** CoreBehaviorProfile with only CORE clusters

### 8.2 Example Execution

**Scenario:** user_665390 with 42 behavior observations

**Input:**
```json
[
  {"observation_id": "obs_1", "behavior_text": "prefers step-by-step tutorials", "embedding": [...], "credibility": 0.87},
  {"observation_id": "obs_2", "behavior_text": "likes structured guides", "embedding": [...], "credibility": 0.91},
  {"observation_id": "obs_3", "behavior_text": "wants ordered instructions", "embedding": [...], "credibility": 0.85},
  ...
  {"observation_id": "obs_42", "behavior_text": "prefers Python over JavaScript", "embedding": [...], "credibility": 0.78}
]
```

**Clustering Result:**
```
Cluster 0 (8 members): Sequential learning behaviors
  - Stability: 0.856
  - Mean credibility: 0.88
  
Cluster 1 (5 members): Code example preferences
  - Stability: 0.674
  - Mean credibility: 0.82
  
Cluster 2 (3 members): Python preference
  - Stability: 0.423
  - Mean credibility: 0.75
  
Cluster 3 (4 members): Visual learning
  - Stability: 0.289
  - Mean credibility: 0.79
  
Noise (22 members): Isolated behaviors
```

**Classification:**
```
Cluster 0: stability=0.856 >= 0.15 ✓, credibility=0.88 >= 0.5 ✓ → CORE
Cluster 1: stability=0.674 >= 0.15 ✓, credibility=0.82 >= 0.5 ✓ → CORE
Cluster 2: stability=0.423 >= 0.15 ✓, credibility=0.75 >= 0.5 ✓ → CORE
Cluster 3: stability=0.289 >= 0.15 ✓, credibility=0.79 >= 0.5 ✓ → CORE
Noise: INSUFFICIENT_EVIDENCE (if cred >= 0.5) or NOISE (if cred < 0.5)
```

**Output:**
```json
{
  "user_id": "user_665390",
  "behavior_clusters": [
    {
      "cluster_id": "cluster_0",
      "canonical_label": "prefers step-by-step tutorials",
      "cluster_stability": 0.856,
      "confidence": 0.856,
      "epistemic_state": "CORE",
      "cluster_size": 8
    },
    {
      "cluster_id": "cluster_1",
      "canonical_label": "wants code examples with explanations",
      "cluster_stability": 0.674,
      "confidence": 0.674,
      "epistemic_state": "CORE",
      "cluster_size": 5
    },
    {
      "cluster_id": "cluster_2",
      "canonical_label": "prefers Python programming",
      "cluster_stability": 0.423,
      "confidence": 0.423,
      "epistemic_state": "CORE",
      "cluster_size": 3
    },
    {
      "cluster_id": "cluster_3",
      "canonical_label": "learns best through visual diagrams",
      "cluster_stability": 0.289,
      "confidence": 0.289,
      "epistemic_state": "CORE",
      "cluster_size": 4
    }
  ],
  "statistics": {
    "total_behaviors_analyzed": 42,
    "clusters_formed": 4,
    "total_prompts_analyzed": 100,
    "analysis_time_span_days": 30
  }
}
```

---

## Summary

### Algorithm Pipeline
1. **Load & Normalize** embeddings
2. **Cluster** with HDBSCAN (density-based)
3. **Extract** stability scores
4. **Classify** using stability + credibility thresholds
5. **Filter** to only CORE behaviors

### Key Metrics
- **Cluster Stability:** Primary quality metric (HDBSCAN persistence)
- **Credibility:** Secondary quality gate
- **Confidence:** = Stability (direct 1:1 mapping)

### Thresholds
- **Stability:** 0.15 (heuristic, not calibrated)
- **Credibility:** 0.5 (pragmatic midpoint)
- **min_cluster_size:** Adaptive (3 or 20% of N)

### Critical Insight
**Clustering is the bottleneck:** If HDBSCAN forms 0 clusters, threshold values don't matter → system abstains

---

[← Back to Part 2](SYSTEM_DOC_2_DATA_MODELS.md) | [Back to Master Index](SYSTEM_DOCUMENTATION_MASTER.md) | [Next: Part 4 - Components →](SYSTEM_DOC_4_COMPONENTS.md)
