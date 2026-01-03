# Part 4: System Components & Implementation

**Document:** SYSTEM_DOC_4_COMPONENTS.md  
**Version:** 1.0  
**Date:** January 3, 2026

[← Back to Part 3](SYSTEM_DOC_3_ALGORITHMS.md) | [Back to Master Index](SYSTEM_DOCUMENTATION_MASTER.md) | [Next: Part 5 - API →](SYSTEM_DOC_5_API.md)

---

## Table of Contents

1. [Component Architecture](#1-component-architecture)
2. [Service Layer Components](#2-service-layer-components)
3. [Database Layer Components](#3-database-layer-components)
4. [Supporting Services](#4-supporting-services)
5. [Component Interactions](#5-component-interactions)
6. [Code Structure](#6-code-structure)

---

## 1. Component Architecture

### 1.1 Layered Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                      │
│  Files: src/api/routes.py                                     │
│  - HTTP endpoints                                             │
│  - Request validation                                         │
│  - Response formatting                                        │
└─────────────────────────┬─────────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────┐
│                    Service Layer (Business Logic)             │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  ClusterAnalysisPipeline (Orchestrator)               │   │
│  │  File: src/services/cluster_analysis_pipeline.py      │   │
│  │  - Main workflow coordination                          │   │
│  │  - Data loading from storage                           │   │
│  │  - Cluster formation & classification                  │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │                                          │
│         ┌───────────┼────────────┬────────────────┐          │
│         │           │            │                │          │
│  ┌──────▼───┐ ┌────▼────┐ ┌─────▼────┐ ┌────────▼───────┐  │
│  │Clustering│ │Calcul-  │ │Embed-    │ │Archetype       │  │
│  │Engine    │ │ation    │ │ding      │ │Service         │  │
│  │          │ │Engine   │ │Service   │ │                │  │
│  └──────────┘ └─────────┘ └──────────┘ └────────────────┘  │
└─────────────────────────┬─────────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────┐
│                    Database Layer (Persistence)               │
│  ┌──────────────────────────┐  ┌──────────────────────────┐  │
│  │  QdrantDatabase          │  │  MongoDatabase           │  │
│  │  - Vector storage        │  │  - Metadata storage      │  │
│  │  - Similarity search     │  │  - Cluster records       │  │
│  └──────────────────────────┘  └──────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Primary Responsibility | Input | Output |
|-----------|----------------------|-------|--------|
| **ClusterAnalysisPipeline** | Orchestrate analysis workflow | user_id | CoreBehaviorProfile |
| **ClusteringEngine** | Density-based clustering | embeddings, behavior_ids | ClusterResult |
| **CalculationEngine** | Metric computation | cluster data | confidence scores |
| **QdrantDatabase** | Vector storage & retrieval | embeddings | behaviors with vectors |
| **MongoDatabase** | Metadata persistence | cluster data | stored records |
| **EmbeddingService** | Generate embeddings | text | 1536-dim vector |
| **ArchetypeService** | User type classification | behavior clusters | archetype label |

---

## 2. Service Layer Components

### 2.1 ClusterAnalysisPipeline

**File:** `src/services/cluster_analysis_pipeline.py` (613 lines)

**Purpose:** Main orchestrator for behavior analysis workflow

**Key Methods:**

#### analyze_behaviors_from_storage()
```python
async def analyze_behaviors_from_storage(
    self,
    user_id: str,
    generate_archetype: bool = True,
    current_timestamp: Optional[int] = None
) -> CoreBehaviorProfile:
    """
    Main entry point: analyze user behaviors from Qdrant storage
    
    Workflow:
    1. Fetch behaviors from Qdrant
    2. Fetch prompts from MongoDB  
    3. Run clustering
    4. Classify clusters
    5. Generate profile
    
    Returns:
        CoreBehaviorProfile with only CORE clusters
    """
```

**Workflow Steps:**

**Step 1: Data Loading**
```python
# Fetch from Qdrant (vectors + metadata)
qdrant_behaviors = self.qdrant.get_embeddings_by_user(user_id)

# Construct BehaviorObservation objects
observations = []
for qb in qdrant_behaviors:
    payload = qb["payload"]
    obs = BehaviorObservation(
        observation_id=payload.get("observation_id"),
        behavior_text=payload.get("behavior_text"),
        embedding=qb["vector"],
        credibility=payload.get("credibility", 0.5),
        ...
    )
    observations.append(obs)
```

**Step 2: Clustering**
```python
# Extract components
embeddings = [obs.embedding for obs in observations]
behavior_ids = [obs.observation_id for obs in observations]
credibilities = [obs.credibility for obs in observations]

# Run HDBSCAN clustering
cluster_result = self.clustering_engine.cluster_behaviors(
    embeddings=embeddings,
    behavior_ids=behavior_ids,
    credibility_weights=credibilities
)
```

**Step 3: Classification**
```python
# Create BehaviorCluster objects
clusters = []
for cluster_label, member_ids in cluster_result["clusters"].items():
    # Get members
    members = [obs for obs in observations if obs.observation_id in member_ids]
    
    # Calculate metrics
    mean_cred = sum(m.credibility for m in members) / len(members)
    stability = cluster_result["cluster_stabilities"][cluster_label]
    
    # Classify
    epistemic_state = self._classify_cluster(stability, mean_cred)
    
    # Create cluster object
    cluster = BehaviorCluster(
        cluster_id=f"cluster_{cluster_label}",
        user_id=user_id,
        observation_ids=member_ids,
        observations=members,
        cluster_stability=stability,
        epistemic_state=epistemic_state,
        confidence=stability,  # Direct mapping
        ...
    )
    clusters.append(cluster)
```

**Step 4: Filtering**
```python
# Keep only CORE clusters
core_clusters = [c for c in clusters if c.epistemic_state == EpistemicState.CORE]

# If no CORE clusters → abstention (empty profile)
if len(core_clusters) == 0:
    logger.info(f"Abstention: No CORE clusters for user {user_id}")
```

**Step 5: Output**
```python
profile = CoreBehaviorProfile(
    user_id=user_id,
    generated_at=current_timestamp or int(time.time()),
    behavior_clusters=core_clusters,  # Only CORE
    archetype=archetype if generate_archetype else None,
    statistics=ProfileStatistics(...)
)
return profile
```

**Key Design Patterns:**
- **Cluster-centric:** Processes clusters as primary entities
- **Abstention-aware:** Returns empty profile if no CORE clusters
- **Storage-driven:** Qdrant is source of truth for vectors
- **Async:** Supports concurrent operations

---

### 2.2 ClusteringEngine

**File:** `src/services/clustering_engine.py` (391 lines)

**Purpose:** HDBSCAN clustering with stability extraction

**Key Methods:**

#### cluster_behaviors()
```python
def cluster_behaviors(
    self,
    embeddings: List[List[float]],
    behavior_ids: List[str],
    credibility_weights: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Cluster behavior embeddings using HDBSCAN
    
    Returns dict with:
    - clusters: {cluster_label: [observation_ids]}
    - cluster_stabilities: {cluster_label: stability_score}
    - labels: [cluster_label_per_observation]
    - noise_behaviors: [isolated_observation_ids]
    - num_clusters: int
    """
```

**Implementation Highlights:**

**Adaptive min_cluster_size:**
```python
n_samples = len(embeddings)
if n_samples < 20:
    adaptive_min_cluster_size = max(3, int(n_samples * 0.20))
else:
    adaptive_min_cluster_size = max(3, int(math.log(n_samples)))
```

**L2 Normalization:**
```python
X = np.array(embeddings)
norms = np.linalg.norm(X, axis=1, keepdims=True)
X_normalized = X / (norms + 1e-10)
```

**Clustering:**
```python
clusterer = HDBSCAN(
    min_cluster_size=adaptive_min_cluster_size,
    min_samples=1,
    cluster_selection_epsilon=0.15,
    metric='euclidean'
)
cluster_labels = clusterer.fit_predict(X_normalized)
```

**Stability Extraction:**
```python
def _extract_cluster_stabilities(self, clusterer, cluster_labels):
    """Extract stability from cluster_persistence_"""
    cluster_stabilities = {}
    unique_clusters = set(cluster_labels) - {-1}
    
    if hasattr(clusterer, 'cluster_persistence_'):
        raw_stabilities = clusterer.cluster_persistence_
        for cluster_label in unique_clusters:
            if cluster_label < len(raw_stabilities):
                stability = float(raw_stabilities[cluster_label])
                cluster_stabilities[cluster_label] = stability
            else:
                cluster_stabilities[cluster_label] = 0.5  # Fallback
    else:
        # No persistence data
        for cluster_label in unique_clusters:
            cluster_stabilities[cluster_label] = 0.5
    
    return cluster_stabilities
```

**Edge Case Handling:**
- **Too few behaviors:** Return empty clusters if N < min_cluster_size
- **No stability data:** Fallback to 0.5
- **Index out of bounds:** Fallback to 0.5

---

### 2.3 CalculationEngine

**File:** `src/services/calculation_engine.py` (331 lines)

**Purpose:** Calculate metrics (confidence, temporal factors)

**Key Methods:**

#### calculate_confidence_from_stability()
```python
def calculate_confidence_from_stability(
    self,
    cluster_stability: float,
    temporal_decay_factor: Optional[float] = None
) -> float:
    """
    Calculate confidence from cluster stability
    
    Current implementation: confidence = stability (1:1 mapping)
    Optional: Apply temporal decay
    """
    confidence = cluster_stability
    
    if temporal_decay_factor is not None:
        confidence *= temporal_decay_factor
    
    return max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
```

#### calculate_behavior_metrics()
```python
def calculate_behavior_metrics(
    self,
    observation: BehaviorObservation,
    current_timestamp: int
) -> Dict[str, float]:
    """
    Calculate metrics for a single observation
    
    Returns:
        - bw: Behavior Weight
        - abw: Adjusted Behavior Weight
        - recency_factor: Temporal decay multiplier
    """
    # Base weight from credibility
    bw = observation.credibility
    
    # Temporal decay
    days_old = (current_timestamp - observation.timestamp) / 86400
    recency_factor = np.exp(-observation.decay_rate * days_old)
    
    # Adjusted weight
    abw = bw * recency_factor
    
    return {
        "bw": bw,
        "abw": abw,
        "recency_factor": recency_factor
    }
```

**Note:** Most metric calculations now happen at cluster level, not observation level

---

## 3. Database Layer Components

### 3.1 QdrantDatabase

**File:** `src/database/qdrant_service.py`

**Purpose:** Vector storage and semantic similarity search

**Key Methods:**

#### get_embeddings_by_user()
```python
def get_embeddings_by_user(
    self,
    user_id: str,
    limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Retrieve all behavior vectors for a user
    
    Returns:
        List of dicts with:
        - id: observation_id
        - vector: embedding (1536-dim)
        - payload: metadata (behavior_text, credibility, etc.)
    """
    results, next_offset = self.client.scroll(
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
        limit=limit
    )
    
    return [
        {
            "id": point.id,
            "vector": point.vector,
            "payload": point.payload
        }
        for point in results
    ]
```

**Collection Schema:**
```python
{
    "collection_name": "behaviors",
    "vector_size": 1536,
    "distance": "Cosine",  # Similarity metric
    "points": [
        {
            "id": "obs_uuid",
            "vector": [0.123, -0.456, ...],  # 1536 dimensions
            "payload": {
                "user_id": str,
                "behavior_text": str,
                "credibility": float,
                "clarity_score": float,
                "extraction_confidence": float,
                "timestamp": int,
                "prompt_id": str,
                ...
            }
        }
    ]
}
```

**Key Operations:**
- `upsert()`: Add/update behavior vectors
- `scroll()`: Retrieve vectors by filter
- `search()`: Semantic similarity search (not used in current pipeline)
- `delete()`: Remove vectors

---

### 3.2 MongoDatabase

**File:** `src/database/mongodb_service.py`

**Purpose:** Metadata storage and structured queries

**Collections:**

**behavior_clusters:**
```javascript
{
  _id: ObjectId,
  cluster_id: String,
  user_id: String,
  observation_ids: [String],
  canonical_label: String,
  cluster_stability: Number,
  epistemic_state: String,  // "CORE", "INSUFFICIENT_EVIDENCE", "NOISE"
  confidence: Number,
  tier: String,
  created_at: Number,
  updated_at: Number,
  ...
}
```

**behavior_observations:**
```javascript
{
  _id: ObjectId,
  observation_id: String,
  user_id: String,
  behavior_text: String,
  credibility: Number,
  timestamp: Number,
  prompt_id: String,
  cluster_id: String (optional),
  classification: String (optional)
}
```

**prompts:**
```javascript
{
  _id: ObjectId,
  prompt_id: String,
  user_id: String,
  prompt_text: String,
  timestamp: Number,
  session_id: String (optional)
}
```

**Key Methods:**
```python
# Get prompts by user
prompts = mongodb.get_prompts_by_user(user_id)

# Store cluster
mongodb.store_cluster(cluster_obj)

# Query CORE clusters
core_clusters = mongodb.find({
    "user_id": user_id,
    "epistemic_state": "CORE"
})
```

---

## 4. Supporting Services

### 4.1 EmbeddingService

**File:** `src/services/embedding_service.py` (122 lines)

**Purpose:** Generate semantic embeddings for text

**Implementation:**
```python
import openai

class EmbeddingService:
    def __init__(self):
        self.client = openai.AsyncAzureOpenAI(...)
        self.model = "text-embedding-3-large"  # 1536 dimensions
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        response = await self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding  # List[float], length 1536
    
    async def generate_embeddings_batch(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        response = await self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]
```

**Model Details:**
- **Model:** Azure OpenAI `text-embedding-3-large`
- **Dimensions:** 1536
- **Normalization:** Not inherently normalized (requires L2 normalization)
- **Usage:** Behavior text → semantic vector

---

### 4.2 ArchetypeService

**File:** `src/services/archetype_service.py` (324 lines)

**Purpose:** Classify users into behavioral archetypes

**Method:**
```python
def identify_archetype(
    self,
    behavior_clusters: List[BehaviorCluster]
) -> Optional[str]:
    """
    Identify user archetype from CORE behavior patterns
    
    Returns archetype label like:
    - "Sequential Learner"
    - "Visual Thinker"
    - "Code-First Developer"
    - None (if patterns unclear)
    """
```

**Implementation:** Rule-based pattern matching on cluster labels

**Status:** Optional feature (can be disabled)

---

## 5. Component Interactions

### 5.1 Analysis Workflow Sequence Diagram

```
User/API → ClusterAnalysisPipeline → QdrantDatabase → MongoDB
             │                          │
             │ 1. get_embeddings        │
             │─────────────────────────▶│
             │◀─────────────────────────│
             │   [behaviors + vectors]  │
             │                          │
             │ 2. get_prompts          │
             │──────────────────────────────────▶
             │◀──────────────────────────────────
             │   [prompts]                       │
             │                                   │
             ▼                                   │
        ClusteringEngine                        │
             │                                   │
             │ 3. cluster_behaviors              │
             │─────────────────────────▶         │
             │◀─────────────────────────         │
             │   [cluster_result]                │
             │                                   │
             ▼                                   │
        Classification Logic                    │
             │                                   │
             │ 4. classify clusters              │
             │   (CORE/INSUFF/NOISE)             │
             │                                   │
             ▼                                   │
        Filter CORE clusters                    │
             │                                   │
             ▼                                   │
        CoreBehaviorProfile                     │
             │                                   │
             │ 5. (optional) store clusters     │
             │───────────────────────────────────▶
             │                                   │
             ▼                                   │
        Return to API                           │
```

### 5.2 Data Flow

```
1. STORAGE RETRIEVAL:
   Qdrant → BehaviorObservation[] (with embeddings)
   MongoDB → PromptModel[]

2. CLUSTERING:
   BehaviorObservation[] → ClusteringEngine
   → ClusterResult {clusters, stabilities, labels}

3. CLASSIFICATION:
   ClusterResult + Observations → Classification Logic
   → BehaviorCluster[] (with epistemic_state)

4. FILTERING:
   BehaviorCluster[] → Filter(epistemic_state == CORE)
   → CoreBehaviorProfile.behavior_clusters

5. OUTPUT:
   CoreBehaviorProfile → API Response
   (Optional) → MongoDB storage
```

---

## 6. Code Structure

### 6.1 Project Organization

```
src/
├── api/
│   └── routes.py                       # FastAPI endpoints
├── models/
│   └── schemas.py                      # Pydantic data models
├── services/
│   ├── cluster_analysis_pipeline.py   # Main orchestrator (613 lines)
│   ├── clustering_engine.py           # HDBSCAN clustering (391 lines)
│   ├── calculation_engine.py          # Metric calculations (331 lines)
│   ├── embedding_service.py           # Azure OpenAI embeddings (122 lines)
│   ├── archetype_service.py           # User archetype detection (324 lines)
│   └── llm_context_service.py         # LLM context generation (268 lines)
├── database/
│   ├── qdrant_service.py              # Vector database
│   └── mongodb_service.py             # Metadata database
├── utils/
│   └── helpers.py                     # Utility functions
└── config.py                          # Configuration settings
```

### 6.2 Key Files

**Core Algorithm:**
- `cluster_analysis_pipeline.py`: Main workflow
- `clustering_engine.py`: HDBSCAN implementation
- `calculation_engine.py`: Metric computation

**Data Layer:**
- `schemas.py`: All data models (318 lines)
- `qdrant_service.py`: Vector operations
- `mongodb_service.py`: Metadata operations

**Integration:**
- `routes.py`: API endpoints
- `config.py`: System configuration

### 6.3 Configuration (config.py)

**Key Parameters:**
```python
# Clustering
min_cluster_size = 3
min_samples = 1
cluster_selection_epsilon = 0.15

# Classification Thresholds
stability_threshold = 0.15
credibility_threshold = 0.5

# Temporal Decay
default_decay_rate = 0.01

# Database
qdrant_url = "http://localhost:6333"
qdrant_collection_name = "behaviors"
mongodb_url = "mongodb://localhost:27017"
mongodb_db_name = "cbie"

# Embedding
embedding_model = "text-embedding-3-large"
embedding_dimensions = 1536
```

---

## Summary

### Component Responsibilities

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **API** | routes.py | HTTP interface |
| **Orchestration** | ClusterAnalysisPipeline | Workflow coordination |
| **Clustering** | ClusteringEngine | HDBSCAN + stability extraction |
| **Metrics** | CalculationEngine | Confidence calculation |
| **Vector Storage** | QdrantDatabase | Embedding persistence |
| **Metadata Storage** | MongoDatabase | Cluster/observation records |
| **Embeddings** | EmbeddingService | Text → vector conversion |
| **Archetypes** | ArchetypeService | User type classification |

### Key Design Patterns

1. **Layered Architecture:** API → Services → Database
2. **Cluster-Centric:** Clusters as primary entities
3. **Abstention-Aware:** Empty output for insufficient evidence
4. **Storage-Driven:** Qdrant as source of truth
5. **Async Support:** Concurrent operations where beneficial

### Code Metrics

- **Total Lines:** ~3,500 (core implementation)
- **Main Pipeline:** 613 lines
- **Clustering Engine:** 391 lines
- **Data Models:** 318 lines
- **Test Coverage:** Core algorithms fully tested

---

[← Back to Part 3](SYSTEM_DOC_3_ALGORITHMS.md) | [Back to Master Index](SYSTEM_DOCUMENTATION_MASTER.md) | [Next: Part 5 - API →](SYSTEM_DOC_5_API.md)
