# Part 2: Data Models & Schemas

**Document:** SYSTEM_DOC_2_DATA_MODELS.md  
**Version:** 1.0  
**Date:** January 3, 2026

[← Back to Part 1](SYSTEM_DOC_1_OVERVIEW.md) | [Back to Master Index](SYSTEM_DOCUMENTATION_MASTER.md) | [Next: Part 3 - Algorithms →](SYSTEM_DOC_3_ALGORITHMS.md)

---

## Table of Contents

1. [Data Model Philosophy](#1-data-model-philosophy)
2. [Input Data Structures](#2-input-data-structures)
3. [Internal Processing Structures](#3-internal-processing-structures)
4. [Output Data Structures](#4-output-data-structures)
5. [Database Schemas](#5-database-schemas)
6. [Data Flow & Transformations](#6-data-flow--transformations)
7. [Quality Metrics Explained](#7-quality-metrics-explained)

---

## 1. Data Model Philosophy

### 1.1 Cluster-Centric Design

**Key Principle:** Clusters are the primary entity, not individual behaviors

**Rationale:**
- Individual behavior observations are raw signals
- Clusters represent semantic concepts
- Preferences emerge at cluster level, not observation level

**Implication:**
```python
# OLD: Behavior-centric
for behavior in behaviors:
    if behavior.count >= 5:
        mark_as_CORE(behavior)

# NEW: Cluster-centric  
clusters = cluster_behaviors(behaviors)
for cluster in clusters:
    if cluster.stability >= 0.15:
        mark_cluster_as_CORE(cluster)
```

### 1.2 Immutable Observations

**Principle:** Never discard observations, even if classified as NOISE

**Rationale:**
- Future clustering runs may reclassify
- Historical tracking requires complete record
- Debugging needs full data trail

**Implementation:**
- All observations stored in database
- Classification is metadata, not deletion
- NOISE status is reversible

### 1.3 Separation of Concerns

**Three Data Layers:**

1. **Storage Layer:** Raw observations as stored (Qdrant + MongoDB)
2. **Processing Layer:** Intermediate structures during analysis (clusters, labels)
3. **Output Layer:** Filtered results for consumption (only CORE)

---

## 2. Input Data Structures

### 2.1 BehaviorObservation

**Purpose:** Single instance of observed user behavior

**Schema:**
```python
class BehaviorObservation(BaseModel):
    # Identity
    observation_id: str          # Unique identifier (e.g., "obs_3ccbf2b2")
    user_id: str                 # User this belongs to
    
    # Content
    behavior_text: str           # Human-readable description
    embedding: List[float]       # 1536-dim vector (Azure OpenAI)
    
    # Quality Metrics (0.0 - 1.0)
    credibility: float           # Trustworthiness of observation
    clarity_score: float         # How explicit the behavior is
    extraction_confidence: float # LLM's certainty in extraction
    
    # Temporal Context
    timestamp: int               # Unix timestamp (when observed)
    prompt_id: str               # Which prompt triggered this
    session_id: Optional[str]    # Session context
    
    # Legacy/Optional
    decay_rate: float = 0.01     # Temporal decay parameter
    bw: Optional[float]          # Behavior Weight (calculated)
    abw: Optional[float]         # Adjusted Behavior Weight (calculated)
```

**Field Explanations:**

| Field | Range | Purpose | Source |
|-------|-------|---------|--------|
| `observation_id` | string | Unique identifier | Generated (UUID) |
| `behavior_text` | string | Human-readable description | LLM extraction |
| `embedding` | float[1536] | Semantic vector | Azure OpenAI API |
| `credibility` | 0.0-1.0 | Observation quality | Composite score |
| `clarity_score` | 0.0-1.0 | Explicitness measure | LLM confidence |
| `extraction_confidence` | 0.0-1.0 | Extraction certainty | LLM output |
| `timestamp` | int (Unix) | Observation time | Interaction log |
| `prompt_id` | string | Triggering prompt | Interaction log |

**Example:**
```json
{
  "observation_id": "obs_3ccbf2b2",
  "user_id": "user_665390",
  "behavior_text": "prefers step-by-step tutorials",
  "embedding": [0.123, -0.456, ..., 0.789],
  "credibility": 0.87,
  "clarity_score": 0.92,
  "extraction_confidence": 0.85,
  "timestamp": 1735905234,
  "prompt_id": "prompt_42",
  "session_id": "session_7732",
  "decay_rate": 0.01
}
```

### 2.2 PromptModel

**Purpose:** User interaction that triggered behavior observation

**Schema:**
```python
class PromptModel(BaseModel):
    prompt_id: str               # Unique identifier
    user_id: str                 # User who issued prompt
    prompt_text: str             # Actual user query/request
    timestamp: int               # When prompt was issued
    session_id: Optional[str]    # Session context
    tokens: Optional[float]      # Token count (if relevant)
```

**Relationship:**
- One prompt can trigger multiple behavior observations
- prompt_id links observations back to triggering interaction

**Example:**
```json
{
  "prompt_id": "prompt_42",
  "user_id": "user_665390",
  "prompt_text": "Show me how to implement a binary search tree",
  "timestamp": 1735905234,
  "session_id": "session_7732",
  "tokens": 12.0
}
```

### 2.3 Quality Metrics Deep Dive

#### Credibility (0.0 - 1.0)

**Definition:** Trustworthiness of the behavior observation

**Components:**
- Extraction confidence: How certain was the LLM?
- Source reliability: Was this from primary interaction or inferred?
- Context clarity: Was the user intent clear?

**Typical Values:**
- `0.9-1.0`: Direct, explicit user statement
- `0.7-0.9`: Clear inference from interaction pattern
- `0.5-0.7`: Weak signal, possible preference
- `< 0.5`: Noisy observation, low confidence

**Usage in System:**
- Does NOT affect clustering (density estimation unweighted)
- Does affect INSUFFICIENT_EVIDENCE vs NOISE classification
- Threshold: 0.5 (below = NOISE candidate)

#### Clarity Score (0.0 - 1.0)

**Definition:** How explicit and unambiguous the behavior statement is

**High Clarity Examples:**
- "User explicitly prefers dark mode" (0.95)
- "User always chooses Python over JavaScript" (0.90)

**Low Clarity Examples:**
- "User might prefer visual learning" (0.45)
- "Possibly interested in web development" (0.40)

**Purpose:** Helps identify weak/ambiguous signals

#### Extraction Confidence (0.0 - 1.0)

**Definition:** LLM's self-reported confidence in behavior extraction

**Interpretation:**
- High confidence: LLM found clear evidence in interaction
- Low confidence: LLM uncertain, possibly hallucinating

**Note:** This is the LLM's confidence, not ground truth

---

## 3. Internal Processing Structures

### 3.1 ClusterResult

**Purpose:** Output from HDBSCAN clustering algorithm

**Schema:**
```python
class ClusterResult(BaseModel):
    cluster_stabilities: Dict[int, float]  # {cluster_label: stability_score}
    clusters: Dict[int, List[str]]         # {cluster_label: [observation_ids]}
    labels: List[int]                      # Cluster label per observation (-1 = noise)
    noise_behaviors: List[str]             # observation_ids classified as noise
    num_clusters: int                      # Count of valid clusters (excludes -1)
```

**Field Explanations:**

**`cluster_stabilities`**: Dictionary mapping cluster labels to their stability scores
- Example: `{0: 0.85, 1: 0.23, 2: 0.67}`
- Stability range: 0.0 (ephemeral) to 1.0 (highly stable)
- Source: HDBSCAN's `cluster_persistence_` attribute

**`clusters`**: Dictionary grouping observation IDs by cluster
- Example: `{0: ["obs_1", "obs_2", "obs_3"], 1: ["obs_4", "obs_5"]}`
- Does not include noise points (label = -1)

**`labels`**: Array of cluster assignments
- Length = number of input observations
- Values: 0, 1, 2, ... (cluster labels) or -1 (noise)
- Example: `[0, 0, -1, 1, 0, 1, -1]` 
  - obs_0, obs_1, obs_4 → cluster 0
  - obs_3, obs_5 → cluster 1
  - obs_2, obs_6 → noise

**`noise_behaviors`**: List of observation IDs classified as noise
- Example: `["obs_2", "obs_6"]`
- These are isolated points, not part of any dense region

**Example:**
```json
{
  "cluster_stabilities": {
    "0": 0.856,
    "1": 0.234
  },
  "clusters": {
    "0": ["obs_1", "obs_2", "obs_3"],
    "1": ["obs_4", "obs_5"]
  },
  "labels": [0, 0, -1, 1, 0, 1, -1],
  "noise_behaviors": ["obs_2", "obs_6"],
  "num_clusters": 2
}
```

### 3.2 BehaviorClassification

**Purpose:** Final classification state for each observation

**Schema:**
```python
class BehaviorClassification(BaseModel):
    observation_id: str
    behavior_description: str
    status: EpistemicState         # CORE, INSUFFICIENT_EVIDENCE, or NOISE
    cluster_id: Optional[int]      # Which cluster (if any)
    cluster_stability: Optional[float]  # Stability of parent cluster
    confidence: float              # Normalized stability
    credibility: float             # Quality score
    classification_reason: str     # Human-readable explanation
```

**Example:**
```json
{
  "observation_id": "obs_1",
  "behavior_description": "prefers step-by-step tutorials",
  "status": "CORE",
  "cluster_id": 0,
  "cluster_stability": 0.856,
  "confidence": 0.856,
  "credibility": 0.87,
  "classification_reason": "Stable cluster (0.856 >= 0.15) with high credibility (0.87)"
}
```

### 3.3 EpistemicState Enum

**Purpose:** Three-state classification of behaviors

**Values:**

```python
class EpistemicState(str, Enum):
    CORE = "CORE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOISE = "NOISE"
```

**Decision Tree:**
```
Is behavior in a cluster?
├─ NO → Check credibility
│      ├─ credibility >= 0.5 → INSUFFICIENT_EVIDENCE
│      └─ credibility < 0.5 → NOISE
│
└─ YES → Check cluster stability
       ├─ stability >= 0.15 → Check credibility
       │                       ├─ credibility >= 0.5 → CORE
       │                       └─ credibility < 0.5 → INSUFFICIENT_EVIDENCE
       └─ stability < 0.15 → Check credibility
                              ├─ credibility >= 0.5 → INSUFFICIENT_EVIDENCE
                              └─ credibility < 0.5 → NOISE
```

**State Meanings:**

**CORE:**
- High cluster stability (≥ 0.15)
- High credibility (≥ 0.5)
- **Action:** Expose to LLMs and user-facing features
- **Interpretation:** Robust, validated preference

**INSUFFICIENT_EVIDENCE:**
- Either stable but low credibility, OR credible but unstable
- **Action:** Retain in database, do NOT expose
- **Interpretation:** Uncertain signal, needs more data

**NOISE:**
- Low stability AND low credibility
- **Action:** Mark for exclusion (but keep in database)
- **Interpretation:** Likely spurious observation

---

## 4. Output Data Structures

### 4.1 BehaviorCluster

**Purpose:** Primary output entity representing a semantic preference cluster

**Schema:**
```python
class BehaviorCluster(BaseModel):
    cluster_id: str                      # e.g., "cluster_0"
    user_id: str
    
    # Member Observations
    observation_ids: List[str]           # All observations in cluster
    observations: List[BehaviorObservation]  # Full observation data
    cluster_size: int                    # len(observations)
    
    # Semantic Representation
    canonical_label: str                 # Best representative text
    cluster_name: Optional[str]          # LLM-generated name
    wording_variations: List[str]        # Different phrasings
    
    # Quality Metrics
    cluster_strength: float              # Legacy composite score
    confidence: float                    # = cluster_stability (0.0-1.0)
    cluster_stability: float             # HDBSCAN persistence score
    epistemic_state: EpistemicState      # CORE/INSUFFICIENT_EVIDENCE/NOISE
    
    # Temporal Context
    first_seen: int                      # Earliest observation timestamp
    last_seen: int                       # Latest observation timestamp
    days_active: float                   # Duration in days
    all_timestamps: List[int]            # All observation times
    all_prompt_ids: List[str]            # All triggering prompts
    
    # Classification
    tier: TierEnum                       # PRIMARY/SECONDARY/NOISE (legacy)
    
    # Metadata
    created_at: int                      # Cluster formation time
    updated_at: int                      # Last modification time
```

**Key Fields Explained:**

**`canonical_label`**: Most representative behavior text
- Selection: Longest, clearest, or most frequent phrasing
- Purpose: UI display and human readability
- Example: "prefers step-by-step tutorials with code examples"

**`cluster_stability`**: HDBSCAN persistence score
- **This is the confidence metric** (not a composite score)
- Range: 0.0 (unstable) to 1.0 (highly stable)
- Threshold: 0.15 for CORE classification

**`epistemic_state`**: Classification status
- Only CORE behaviors are exposed downstream
- INSUFFICIENT_EVIDENCE retained but hidden
- NOISE marked but not deleted

**Example:**
```json
{
  "cluster_id": "cluster_0",
  "user_id": "user_665390",
  "observation_ids": ["obs_1", "obs_2", "obs_3"],
  "cluster_size": 3,
  "canonical_label": "prefers step-by-step tutorials",
  "cluster_name": "Sequential Learning Preference",
  "wording_variations": [
    "prefers step-by-step tutorials",
    "likes structured guides",
    "wants ordered instructions"
  ],
  "cluster_strength": 2.87,
  "confidence": 0.856,
  "cluster_stability": 0.856,
  "epistemic_state": "CORE",
  "first_seen": 1735900000,
  "last_seen": 1735990000,
  "days_active": 1.04,
  "all_timestamps": [1735900000, 1735945000, 1735990000],
  "all_prompt_ids": ["prompt_10", "prompt_25", "prompt_42"],
  "tier": "PRIMARY",
  "created_at": 1735900000,
  "updated_at": 1735990000
}
```

### 4.2 CoreBehaviorProfile

**Purpose:** Complete user preference profile for downstream consumption

**Schema:**
```python
class CoreBehaviorProfile(BaseModel):
    user_id: str
    generated_at: int                          # Unix timestamp
    behavior_clusters: List[BehaviorCluster]   # Primary data structure
    archetype: Optional[str]                   # User type (if classified)
    statistics: ProfileStatistics              # Metadata
```

**Filtering Logic:**
- **Only includes clusters with `epistemic_state == CORE`**
- INSUFFICIENT_EVIDENCE and NOISE clusters excluded
- If all clusters filtered → empty profile (abstention)

**Example:**
```json
{
  "user_id": "user_665390",
  "generated_at": 1736000000,
  "behavior_clusters": [
    {
      "cluster_id": "cluster_0",
      "epistemic_state": "CORE",
      "canonical_label": "prefers step-by-step tutorials",
      "confidence": 0.856,
      ...
    }
  ],
  "archetype": "Sequential Learner",
  "statistics": {
    "total_behaviors_analyzed": 42,
    "clusters_formed": 8,
    "total_prompts_analyzed": 120,
    "analysis_time_span_days": 30.5
  }
}
```

---

## 5. Database Schemas

### 5.1 Qdrant Collection: `behaviors`

**Purpose:** Vector storage for semantic similarity search

**Schema:**
```
Collection Name: behaviors

Point Structure:
{
  id: str,                    # observation_id
  vector: float[1536],        # embedding
  payload: {
    user_id: str,
    behavior_text: str,
    credibility: float,
    clarity_score: float,
    extraction_confidence: float,
    timestamp: int,
    prompt_id: str,
    session_id: str (optional),
    decay_rate: float
  }
}
```

**Indexing:**
- Vector index: HNSW for fast approximate nearest neighbor search
- Payload filters: user_id (for per-user queries)

**Query Pattern:**
```python
# Retrieve all behaviors for a user
results = qdrant_client.scroll(
    collection_name="behaviors",
    scroll_filter=Filter(
        must=[
            FieldCondition(
                key="user_id",
                match=MatchValue(value=user_id)
            )
        ]
    ),
    with_vectors=True,
    with_payload=True,
    limit=1000
)
```

### 5.2 MongoDB Collection: `behavior_clusters`

**Purpose:** Store cluster metadata and classifications

**Schema:**
```javascript
{
  _id: ObjectId,
  cluster_id: String,           // e.g., "cluster_0"
  user_id: String,
  observation_ids: [String],    // Array of obs IDs
  canonical_label: String,
  cluster_name: String,
  cluster_stability: Number,
  epistemic_state: String,      // "CORE", "INSUFFICIENT_EVIDENCE", "NOISE"
  confidence: Number,
  tier: String,
  first_seen: Number,
  last_seen: Number,
  days_active: Number,
  all_prompt_ids: [String],
  all_timestamps: [Number],
  wording_variations: [String],
  created_at: Number,
  updated_at: Number
}
```

**Indexes:**
- `user_id`: For user-specific queries
- `epistemic_state`: For filtering CORE behaviors
- `cluster_stability`: For sorting by confidence

**Query Pattern:**
```python
# Get all CORE clusters for a user
core_clusters = mongo_db.behavior_clusters.find({
    "user_id": user_id,
    "epistemic_state": "CORE"
})
```

### 5.3 MongoDB Collection: `behavior_observations`

**Purpose:** Store raw observations with metadata

**Schema:**
```javascript
{
  _id: ObjectId,
  observation_id: String,
  user_id: String,
  behavior_text: String,
  credibility: Number,
  clarity_score: Number,
  extraction_confidence: Number,
  timestamp: Number,
  prompt_id: String,
  session_id: String (optional),
  decay_rate: Number,
  cluster_id: String (optional),  // Assigned after clustering
  classification: String (optional)  // CORE, INSUFFICIENT_EVIDENCE, NOISE
}
```

---

## 6. Data Flow & Transformations

### 6.1 End-to-End Data Flow

```
[1] USER INTERACTION
    ↓
    User Query: "Show me a Python tutorial"
    
[2] BEHAVIOR EXTRACTION (External LLM)
    ↓
    Extracted: "User prefers Python programming tutorials"
    Generated Embedding: [0.123, -0.456, ...]
    Quality Scores: {credibility: 0.85, clarity: 0.90}
    
[3] STORAGE (Qdrant + MongoDB)
    ↓
    Qdrant: Store vector + payload
    MongoDB: Store full observation metadata
    
[4] CLUSTERING (CBIE Analysis)
    ↓
    Input: N observations with embeddings
    HDBSCAN: Identify dense regions
    Output: Clusters with stability scores
    
[5] CLASSIFICATION
    ↓
    Apply stability threshold (0.15)
    Apply credibility gates (0.5)
    Assign: CORE / INSUFFICIENT_EVIDENCE / NOISE
    
[6] OUTPUT GENERATION
    ↓
    Filter: Only CORE clusters
    Format: CoreBehaviorProfile
    
[7] DOWNSTREAM CONSUMPTION
    ↓
    LLMs: Receive CORE preferences for context
    UI: Display user preference summary
```

### 6.2 Key Transformations

#### Transformation 1: Observations → Clusters

```
INPUT:
  obs_1: "prefers step-by-step tutorials"
  obs_2: "likes structured guides"
  obs_3: "wants ordered instructions"
  obs_4: "prefers dark mode"

CLUSTERING:
  cluster_0: [obs_1, obs_2, obs_3]  (stability: 0.85)
  cluster_1: [obs_4]                (stability: 0.12)

OUTPUT:
  cluster_0: canonical_label = "prefers step-by-step tutorials"
  cluster_1: canonical_label = "prefers dark mode"
```

#### Transformation 2: Stability → Confidence

```
cluster.stability = 0.856  (HDBSCAN output)
              ↓
cluster.confidence = 0.856  (direct mapping, normalized 0-1)
```

**Note:** Confidence = Stability (1:1 mapping in current system)

#### Transformation 3: Classification → Output Filtering

```
INPUT (All clusters):
  cluster_0: {epistemic_state: CORE, stability: 0.85}
  cluster_1: {epistemic_state: INSUFFICIENT_EVIDENCE, stability: 0.12}
  cluster_2: {epistemic_state: NOISE, stability: 0.05}

OUTPUT (CoreBehaviorProfile.behavior_clusters):
  [cluster_0]  # Only CORE included

HIDDEN (Not exposed):
  [cluster_1, cluster_2]  # Retained in database
```

---

## 7. Quality Metrics Explained

### 7.1 Observation-Level Metrics

| Metric | Range | Meaning | Impact |
|--------|-------|---------|--------|
| Credibility | 0.0-1.0 | Overall trustworthiness | Classification (INSUFF vs NOISE) |
| Clarity Score | 0.0-1.0 | Statement explicitness | Influences credibility |
| Extraction Confidence | 0.0-1.0 | LLM certainty | Influences credibility |

### 7.2 Cluster-Level Metrics

| Metric | Range | Meaning | Impact |
|--------|-------|---------|--------|
| Cluster Stability | 0.0-1.0 | HDBSCAN persistence | Primary classification gate |
| Confidence | 0.0-1.0 | = Stability (in current system) | Output confidence score |
| Cluster Strength | Variable | Legacy composite score | Deprecated (use stability) |
| Mean Credibility | 0.0-1.0 | Average of member credibilities | Secondary classification gate |

### 7.3 Threshold Values

| Threshold | Value | Purpose |
|-----------|-------|---------|
| Stability Threshold | 0.15 | CORE vs INSUFFICIENT_EVIDENCE split |
| Credibility Threshold | 0.5 | INSUFFICIENT_EVIDENCE vs NOISE split |
| min_cluster_size | 3 | Minimum points for cluster formation |

---

## Summary

### Data Model Hierarchy

```
BehaviorObservation (raw signal)
    ↓ [clustering]
BehaviorCluster (semantic group)
    ↓ [classification]
CoreBehaviorProfile (filtered output)
    ↓ [consumption]
LLM Context / UI Display
```

### Key Takeaways

1. **Clusters are primary:** Individual observations are just signals
2. **Immutable storage:** Never delete observations, classification is metadata
3. **Three-state output:** CORE / INSUFFICIENT_EVIDENCE / NOISE
4. **Confidence = Stability:** Direct 1:1 mapping from HDBSCAN persistence
5. **Filtering on output:** Database stores all, API exposes only CORE

---

[← Back to Part 1](SYSTEM_DOC_1_OVERVIEW.md) | [Back to Master Index](SYSTEM_DOCUMENTATION_MASTER.md) | [Next: Part 3 - Algorithms →](SYSTEM_DOC_3_ALGORITHMS.md)
