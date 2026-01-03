# Part 5: API & Integration Layer

**Version:** 1.0  
**Last Updated:** January 3, 2026  
**Part of:** [Comprehensive System Documentation](SYSTEM_DOCUMENTATION_MASTER.md)

---

## Table of Contents
1. [API Overview](#api-overview)
2. [REST Endpoints](#rest-endpoints)
3. [Request/Response Schemas](#requestresponse-schemas)
4. [LLM Context Integration](#llm-context-integration)
5. [Error Handling](#error-handling)
6. [Integration Patterns](#integration-patterns)
7. [API Usage Examples](#api-usage-examples)

---

## API Overview

### Architecture

The CBIE system exposes a RESTful API built with FastAPI:

```
┌─────────────────────────────────────────────┐
│         FastAPI Application Layer           │
│  - Request validation (Pydantic)            │
│  - Route handlers (async)                   │
│  - Error middleware                         │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│Analysis │ │Retrieval│ │Context  │
│Pipeline │ │Service  │ │Service  │
└─────────┘ └─────────┘ └─────────┘
```

### Core Endpoints (5 Total)

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/analyze-behaviors-from-storage` | POST | Analyze behaviors from Qdrant/MongoDB | Production |
| `/analyze-behaviors-cluster-centric` | POST | Direct analysis with provided data | Testing |
| `/get-user-profile/{user_id}` | GET | Retrieve stored profile | Production |
| `/list-core-behaviors/{user_id}` | GET | List canonical CORE behaviors | Production |
| `/generate-llm-context/{user_id}` | GET | Generate LLM context for user | Production |

### Design Principles

1. **Async-first:** All endpoints use async/await for I/O operations
2. **Schema validation:** Pydantic models enforce request/response structure
3. **Embedding exclusion:** Embeddings stripped from responses (reduce payload)
4. **Error transparency:** Detailed HTTP status codes and error messages
5. **Idempotency:** Analysis endpoints can be called repeatedly safely

---

## REST Endpoints

### 1. Analyze Behaviors from Storage (PRIMARY ENDPOINT)

**Purpose:** Normal production workflow - fetch data from storage and analyze

**Endpoint:**
```
POST /api/v1/analyze-behaviors-from-storage?user_id={user_id}
```

**Query Parameters:**
- `user_id` (string, required): User identifier

**Response Schema:** `CoreBehaviorProfile`

**Workflow:**
1. Fetch behaviors from Qdrant (with embeddings)
2. Fetch prompts from MongoDB
3. Calculate behavior weights (BW, ABW)
4. Perform HDBSCAN clustering
5. Classify clusters (CORE/INSUFFICIENT_EVIDENCE/NOISE)
6. Generate archetype (if data sufficient)
7. Store profile in MongoDB
8. Return complete profile

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-behaviors-from-storage?user_id=user_665390" \
  -H "Content-Type: application/json"
```

**Example Response:**
```json
{
  "user_id": "user_665390",
  "behavior_clusters": [
    {
      "cluster_id": "cluster_1_user_665390",
      "canonical_label": "prefers visual learning materials",
      "cluster_name": "Visual Learning Preference",
      "epistemic_state": "CORE",
      "tier": "PRIMARY",
      "cluster_strength": 2.347,
      "confidence": 0.82,
      "cluster_stability": 0.85,
      "cluster_size": 8,
      "observations": [
        {
          "observation_id": "obs_001",
          "behavior_text": "likes diagrams and flowcharts",
          "credibility": 0.95,
          "clarity_score": 0.88,
          "extraction_confidence": 0.92,
          "timestamp": 1704240000
        }
      ],
      "wording_variations": [
        "likes diagrams and flowcharts",
        "prefers visual examples",
        "wants graphical representations"
      ],
      "all_prompt_ids": ["prompt_001", "prompt_002", "prompt_003"],
      "first_seen": 1704240000,
      "last_seen": 1704326400,
      "days_active": 1,
      "recency_score": 0.95
    }
  ],
  "statistics": {
    "total_observations": 42,
    "core_clusters": 1,
    "insufficient_evidence_clusters": 2,
    "noise_observations": 5,
    "analysis_timestamp": 1704326400
  },
  "archetype": {
    "archetype_name": "Visual Learner",
    "description": "User who strongly prefers visual learning materials...",
    "confidence_level": "HIGH"
  }
}
```

**Error Responses:**
- `404 Not Found`: No data found for user_id
- `500 Internal Server Error`: Analysis pipeline failure

---

### 2. Get User Profile

**Purpose:** Retrieve existing profile without re-analysis

**Endpoint:**
```
GET /api/v1/get-user-profile/{user_id}
```

**Path Parameters:**
- `user_id` (string, required): User identifier

**Response Schema:** `CoreBehaviorProfile` (embeddings stripped)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/get-user-profile/user_665390"
```

**Key Features:**
- Embeddings automatically removed from response (performance)
- Returns cached analysis results
- Fast retrieval (no computation)

**Use Cases:**
- Frontend display of user profile
- Quick profile checks
- Historical profile retrieval

---

### 3. List Core Behaviors

**Purpose:** Get canonical CORE behaviors for LLM context or UI display

**Endpoint:**
```
GET /api/v1/list-core-behaviors/{user_id}
```

**Path Parameters:**
- `user_id` (string, required): User identifier

**Response Schema:** `ListCoreBehaviorsResponse`

**Example Response:**
```json
{
  "user_id": "user_665390",
  "canonical_behaviors": [
    {
      "cluster_id": "cluster_1_user_665390",
      "canonical_label": "prefers visual learning materials",
      "cluster_name": "Visual Learning Preference",
      "tier": "PRIMARY",
      "cluster_strength": 2.347,
      "confidence": 0.82,
      "cluster_stability": 0.85,
      "observed_count": 8
    },
    {
      "cluster_id": "cluster_2_user_665390",
      "canonical_label": "needs detailed explanations",
      "cluster_name": "Explanation Depth Preference",
      "tier": "SECONDARY",
      "cluster_strength": 1.823,
      "confidence": 0.67,
      "cluster_stability": 0.72,
      "observed_count": 5
    }
  ]
}
```

**Filtering Logic:**
- **Only CORE epistemic state** (INSUFFICIENT_EVIDENCE and NOISE excluded)
- No embeddings included
- Ordered by tier (PRIMARY → SECONDARY)

**Use Cases:**
- LLM context generation (inject into prompts)
- UI behavior list display
- Downstream system integration

---

### 4. Generate LLM Context

**Purpose:** Generate formatted context for LLM prompt injection

**Endpoint:**
```
GET /api/v1/generate-llm-context/{user_id}
```

**Path Parameters:**
- `user_id` (string, required): User identifier

**Query Parameters:**
- `include_archetype` (boolean, optional, default=true): Include archetype description
- `include_statistics` (boolean, optional, default=false): Include analysis stats
- `format` (string, optional, default="structured"): Output format (structured|narrative|json)

**Response Schema:** `LLMContextResponse`

**Example Response (Structured Format):**
```json
{
  "user_id": "user_665390",
  "context_text": "# User Preference Profile\n\n## Core Behaviors (HIGH CONFIDENCE)\n- prefers visual learning materials (confidence: 0.82, observed: 8 times)\n- needs detailed explanations (confidence: 0.67, observed: 5 times)\n\n## User Archetype\n**Visual Learner** - User who strongly prefers visual learning materials including diagrams, flowcharts, and graphical representations...\n\n## Interaction Guidelines\n- Always include visual aids when explaining concepts\n- Provide diagrams alongside text explanations\n- Use flowcharts for process descriptions\n",
  "format": "structured",
  "core_behavior_count": 2,
  "context_length": 487,
  "generated_at": 1704326400
}
```

**Format Options:**

**Structured (default):**
```markdown
# User Preference Profile

## Core Behaviors (HIGH CONFIDENCE)
- prefers visual learning materials (confidence: 0.82)
- needs detailed explanations (confidence: 0.67)

## User Archetype
**Visual Learner** - [description]

## Interaction Guidelines
- [actionable recommendations]
```

**Narrative:**
```
This user consistently prefers visual learning materials and 
needs detailed explanations. They are classified as a Visual 
Learner archetype. When interacting, always include diagrams 
and flowcharts alongside text explanations.
```

**JSON:**
```json
{
  "behaviors": [...],
  "archetype": {...},
  "guidelines": [...]
}
```

**Use Cases:**
- Inject into ChatGPT system message
- Personalize LLM responses
- Context-aware AI assistance

---

### 5. Analyze Behaviors (Cluster-Centric)

**Purpose:** Testing endpoint for direct analysis with provided data

**Endpoint:**
```
POST /api/v1/analyze-behaviors-cluster-centric
```

**Request Body Schema:** `AnalyzeBehaviorsRequest`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-behaviors-cluster-centric" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_01",
    "behaviors": [
      {
        "observation_id": "obs_001",
        "behavior_text": "likes step-by-step guides",
        "credibility": 0.95,
        "clarity_score": 0.88,
        "extraction_confidence": 0.92,
        "timestamp": 1704240000,
        "embedding": null
      },
      {
        "observation_id": "obs_002",
        "behavior_text": "prefers sequential instructions",
        "credibility": 0.93,
        "clarity_score": 0.85,
        "extraction_confidence": 0.90,
        "timestamp": 1704243600,
        "embedding": null
      }
    ],
    "prompts": [
      {
        "prompt_id": "prompt_001",
        "prompt_text": "How do I learn Python?",
        "behavior_ids": ["obs_001"],
        "timestamp": 1704240000
      },
      {
        "prompt_id": "prompt_002",
        "prompt_text": "Teach me data structures",
        "behavior_ids": ["obs_002"],
        "timestamp": 1704243600
      }
    ],
    "generate_archetype": false
  }'
```

**Workflow:**
1. Accept behaviors and prompts in request body
2. Generate embeddings if not provided
3. Run cluster analysis pipeline
4. Return profile (no database storage)

**Use Cases:**
- Development testing
- One-off analyses
- Batch processing external data

---

## Request/Response Schemas

### Core Schemas

#### BehaviorObservation
```python
{
  "observation_id": str,         # Unique identifier
  "behavior_text": str,          # Natural language description
  "credibility": float,          # 0.0-1.0
  "clarity_score": float,        # 0.0-1.0
  "extraction_confidence": float,# 0.0-1.0
  "timestamp": int,              # Unix timestamp
  "embedding": List[float] | None # Optional, auto-generated if missing
}
```

#### BehaviorCluster
```python
{
  "cluster_id": str,
  "canonical_label": str,
  "cluster_name": str,
  "epistemic_state": str,        # CORE | INSUFFICIENT_EVIDENCE | NOISE
  "tier": str,                   # PRIMARY | SECONDARY | NOISE
  "cluster_strength": float,
  "confidence": float,           # Stability-based
  "cluster_stability": float,    # HDBSCAN stability score
  "cluster_size": int,
  "observations": List[BehaviorObservation],
  "wording_variations": List[str],
  "all_prompt_ids": List[str],
  "first_seen": int,
  "last_seen": int,
  "days_active": int,
  "recency_score": float
}
```

#### CoreBehaviorProfile
```python
{
  "user_id": str,
  "behavior_clusters": List[BehaviorCluster],
  "statistics": {
    "total_observations": int,
    "core_clusters": int,
    "insufficient_evidence_clusters": int,
    "noise_observations": int,
    "analysis_timestamp": int
  },
  "archetype": {
    "archetype_name": str,
    "description": str,
    "confidence_level": str  # HIGH | MEDIUM | LOW
  } | None
}
```

### Validation Rules

**Credibility/Confidence/Scores:**
- Range: 0.0 to 1.0
- Precision: 2 decimal places
- Validation: Pydantic `Field(ge=0.0, le=1.0)`

**Timestamps:**
- Unix timestamp (seconds since epoch)
- Integer type
- Example: 1704326400 = January 4, 2024 00:00:00 UTC

**Text Fields:**
- Max length: 1000 characters for behavior_text
- No empty strings (min_length=1)
- UTF-8 encoding

---

## LLM Context Integration

### Context Generation Service

Located in `src/services/llm_context_service.py`:

```python
def generate_llm_context(
    user_id: str,
    include_archetype: bool = True,
    include_statistics: bool = False,
    format: str = "structured"
) -> str:
    """Generate formatted context for LLM prompt injection"""
```

### Integration Pattern

**1. Fetch Context:**
```bash
GET /api/v1/generate-llm-context/user_665390?format=structured
```

**2. Inject into LLM Prompt:**
```python
# Example: ChatGPT API integration
system_message = f"""
You are a helpful AI assistant. Use the following user preference 
profile to personalize your responses:

{context_text}

Always respect these preferences in your interactions.
"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_query}
    ]
)
```

### Context Format Comparison

| Format | Length | Use Case | Token Efficiency |
|--------|--------|----------|------------------|
| structured | Medium | General LLM injection | High |
| narrative | Short | Context-aware responses | Very High |
| json | Long | Programmatic parsing | Low |

**Recommendation:** Use `structured` for ChatGPT system messages, `narrative` for token-limited models.

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | Success | Request processed successfully |
| 404 | Not Found | User ID not in database, no profile exists |
| 422 | Validation Error | Invalid request schema, missing required fields |
| 500 | Internal Error | Pipeline failure, database connection error |

### Error Response Schema

```json
{
  "detail": "No profile found for user user_999",
  "status_code": 404,
  "error_type": "UserNotFound"
}
```

### Common Error Scenarios

**1. User Not Found (404)**
```json
{
  "detail": "No profile found for user user_999"
}
```

**Solution:** Ensure user has been analyzed first using `/analyze-behaviors-from-storage`

**2. No Behaviors in Database (404)**
```json
{
  "detail": "No behaviors found for user user_665390 in Qdrant"
}
```

**Solution:** Check that behaviors were stored in Qdrant before analysis

**3. Invalid Request Schema (422)**
```json
{
  "detail": [
    {
      "loc": ["body", "behaviors", 0, "credibility"],
      "msg": "ensure this value is greater than or equal to 0.0",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**Solution:** Validate request body against Pydantic schema

**4. Pipeline Failure (500)**
```json
{
  "detail": "Analysis failed: Embedding service unavailable"
}
```

**Solution:** Check Azure OpenAI service status, verify API keys

### Error Handling Best Practices

**In API Routes:**
```python
try:
    profile = await cluster_analysis_pipeline.analyze_behaviors_from_storage(
        user_id=user_id,
        generate_archetype=True
    )
    return profile
except ValueError as e:
    # User data not found
    raise HTTPException(status_code=404, detail=str(e))
except Exception as e:
    # Unexpected error
    logger.error(f"Pipeline failure: {e}")
    raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
```

---

## Integration Patterns

### Pattern 1: Batch User Analysis

**Scenario:** Analyze multiple users sequentially

```python
import requests

users = ["user_001", "user_002", "user_003"]
base_url = "http://localhost:8000/api/v1"

for user_id in users:
    response = requests.post(
        f"{base_url}/analyze-behaviors-from-storage",
        params={"user_id": user_id}
    )
    
    if response.status_code == 200:
        profile = response.json()
        print(f"✓ {user_id}: {len(profile['behavior_clusters'])} CORE clusters")
    elif response.status_code == 404:
        print(f"✗ {user_id}: No data found")
    else:
        print(f"✗ {user_id}: Error {response.status_code}")
```

### Pattern 2: LLM Context Caching

**Scenario:** Cache context to avoid repeated API calls

```python
from functools import lru_cache
import requests

@lru_cache(maxsize=128)
def get_user_context(user_id: str) -> str:
    """Cached context retrieval"""
    response = requests.get(
        f"http://localhost:8000/api/v1/generate-llm-context/{user_id}",
        params={"format": "structured"}
    )
    return response.json()["context_text"]

# Use in LLM integration
context = get_user_context("user_665390")
```

### Pattern 3: Real-time Profile Updates

**Scenario:** Re-analyze after new behaviors added

```python
# 1. Add new behaviors to Qdrant
qdrant_client.upsert(
    collection_name="behaviors",
    points=[...]
)

# 2. Trigger re-analysis
response = requests.post(
    f"{base_url}/analyze-behaviors-from-storage",
    params={"user_id": user_id}
)

# 3. Fetch updated context
context_response = requests.get(
    f"{base_url}/generate-llm-context/{user_id}"
)
```

### Pattern 4: Frontend Integration

**Scenario:** React/Vue frontend displaying user profile

```javascript
// Fetch profile
const response = await fetch(
  `http://localhost:8000/api/v1/get-user-profile/${userId}`
);
const profile = await response.json();

// Display CORE behaviors
const coreClusters = profile.behavior_clusters.filter(
  cluster => cluster.epistemic_state === "CORE"
);

coreClusters.forEach(cluster => {
  console.log(
    `${cluster.canonical_label} (confidence: ${cluster.confidence})`
  );
});
```

---

## API Usage Examples

### Example 1: Complete Analysis Workflow

```python
import requests
import json

base_url = "http://localhost:8000/api/v1"
user_id = "user_665390"

# Step 1: Analyze behaviors from storage
print("Step 1: Analyzing behaviors...")
analysis_response = requests.post(
    f"{base_url}/analyze-behaviors-from-storage",
    params={"user_id": user_id}
)

if analysis_response.status_code == 200:
    profile = analysis_response.json()
    core_count = profile["statistics"]["core_clusters"]
    print(f"✓ Analysis complete: {core_count} CORE clusters")
else:
    print(f"✗ Analysis failed: {analysis_response.status_code}")
    exit(1)

# Step 2: List canonical behaviors
print("\nStep 2: Fetching canonical behaviors...")
behaviors_response = requests.get(
    f"{base_url}/list-core-behaviors/{user_id}"
)

if behaviors_response.status_code == 200:
    behaviors_data = behaviors_response.json()
    for behavior in behaviors_data["canonical_behaviors"]:
        print(f"  - {behavior['canonical_label']}")
        print(f"    Confidence: {behavior['confidence']:.2f}")
        print(f"    Observed: {behavior['observed_count']} times")
else:
    print(f"✗ Failed to fetch behaviors: {behaviors_response.status_code}")

# Step 3: Generate LLM context
print("\nStep 3: Generating LLM context...")
context_response = requests.get(
    f"{base_url}/generate-llm-context/{user_id}",
    params={"format": "structured", "include_archetype": True}
)

if context_response.status_code == 200:
    context_data = context_response.json()
    print("✓ Context generated:")
    print(context_data["context_text"][:200] + "...")
else:
    print(f"✗ Failed to generate context: {context_response.status_code}")
```

### Example 2: PowerShell Testing

```powershell
# Analyze user
$response = Invoke-WebRequest `
  -Uri "http://localhost:8000/api/v1/analyze-behaviors-from-storage?user_id=user_665390" `
  -Method POST

$profile = $response.Content | ConvertFrom-Json

# Display results
Write-Host "Core Clusters: $($profile.statistics.core_clusters)"
Write-Host "Total Observations: $($profile.statistics.total_observations)"

# List behaviors
$profile.behavior_clusters | Where-Object { $_.epistemic_state -eq "CORE" } | ForEach-Object {
    Write-Host "  - $($_.canonical_label) (confidence: $($_.confidence))"
}
```

### Example 3: Python Async Client

```python
import asyncio
import aiohttp

async def analyze_user(user_id: str):
    """Async analysis client"""
    base_url = "http://localhost:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        # Analyze
        async with session.post(
            f"{base_url}/analyze-behaviors-from-storage",
            params={"user_id": user_id}
        ) as response:
            if response.status == 200:
                profile = await response.json()
                return profile
            else:
                return None

# Run async
profile = asyncio.run(analyze_user("user_665390"))
```

---

## Performance Considerations

### Response Time Benchmarks

| Endpoint | Typical Time | Notes |
|----------|--------------|-------|
| `/analyze-behaviors-from-storage` | 2-5 seconds | Depends on N (observation count) |
| `/get-user-profile` | 50-200ms | Database retrieval only |
| `/list-core-behaviors` | 50-200ms | Filtered retrieval |
| `/generate-llm-context` | 100-300ms | Text formatting |

### Optimization Tips

**1. Use `/get-user-profile` for retrieval**
- Don't re-analyze unless data changed
- Cache profiles on frontend

**2. Batch analysis off-peak**
- Analyze multiple users during low-traffic periods
- Use async clients for parallel requests

**3. Strip embeddings**
- API automatically removes embeddings from responses
- Reduces payload size by 80-90%

**4. Cache LLM context**
- Context changes infrequently
- Cache on application server for 24 hours

---

## Security Considerations

### Authentication (Not Implemented)

Current system has **no authentication** - designed for internal research use.

**For production deployment, add:**
- API key authentication
- JWT token validation
- Rate limiting
- User permission checks

### Input Validation

- All requests validated via Pydantic schemas
- SQL injection: Not applicable (using MongoDB/Qdrant)
- XSS: Escaped in text fields
- Max payload size: 10MB (configurable)

### Data Privacy

- No PII logging in standard logs
- Embeddings not exposed in API responses
- User IDs should be anonymized in production

---

## Next Steps

For API integration, see:
- [Part 4: System Components](SYSTEM_DOC_4_COMPONENTS.md) - Service layer architecture
- [Part 6: Evaluation Framework](SYSTEM_DOC_6_EVALUATION.md) - System validation
- API testing examples in `tests/test_api.py`

---

**Navigation:**
- [← Part 4: Components](SYSTEM_DOC_4_COMPONENTS.md)
- [↑ Master Index](SYSTEM_DOCUMENTATION_MASTER.md)
- [→ Part 6: Evaluation](SYSTEM_DOC_6_EVALUATION.md)
