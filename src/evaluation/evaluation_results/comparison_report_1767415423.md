# Evaluation Results: Frequency Baseline vs Stability System

**Generated:** 2026-01-03 10:13:43

**Dataset:** 6 synthetic users with controlled characteristics

---

## Summary Table

| User | Description | Frequency CORE | Stability CORE | Agreement |

|------|-------------|----------------|----------------|-----------|
| user_stable_01 | Visual Viktor - tight clustering | 2 | 0 | FREQ OVER-PROMOTES (2 vs 0) |
| user_large_01 | Dedicated Dana - many interactions | 4 | 0 | FREQ OVER-PROMOTES (4 vs 0) |
| user_mixed_01 | Balanced Beth - mixed stability | 3 | 0 | FREQ OVER-PROMOTES (3 vs 0) |
| user_sparse_01 | Scattered Sam - high reinf, low stability | 3 | 0 | FREQ OVER-PROMOTES (3 vs 0) |
| user_research_01 | Academic Alice - dispersed behaviors | 4 | 0 | FREQ OVER-PROMOTES (4 vs 0) |
| user_tiny_01 | Minimal Mike - very few interactions | 1 | 0 | FREQ OVER-PROMOTES (1 vs 0) |

---

## Detailed Results


### user_stable_01 - Visual Viktor - tight clustering

**Frequency Baseline:**

- Total behaviors: 3
- CORE: 2 (≥5 reinforcements)
- SECONDARY: 1 (2-4 reinforcements)
- NOISE: 0 (1 reinforcement)

- **CORE Behaviors:**
  - "learns best with visual examples" (N=8, conf=0.16)
  - "prefers diagrams and flowcharts" (N=6, conf=0.12)

**Stability System:**

- Total behaviors: 3
- CORE: 0 (stability ≥0.15)
- SECONDARY: 0
- Clusters formed: 0


**Agreement:** FREQ OVER-PROMOTES (2 vs 0)

---


### user_large_01 - Dedicated Dana - many interactions

**Frequency Baseline:**

- Total behaviors: 5
- CORE: 4 (≥5 reinforcements)
- SECONDARY: 1 (2-4 reinforcements)
- NOISE: 0 (1 reinforcement)

- **CORE Behaviors:**
  - "likes sequential guides" (N=12, conf=0.24)
  - "wants code samples" (N=5, conf=0.10)
  - "prefers step-by-step instructions" (N=11, conf=0.22)
  - "wants ordered procedures" (N=14, conf=0.28)

**Stability System:**

- Total behaviors: 5
- CORE: 0 (stability ≥0.15)
- SECONDARY: 0
- Clusters formed: 0


**Agreement:** FREQ OVER-PROMOTES (4 vs 0)

---


### user_mixed_01 - Balanced Beth - mixed stability

**Frequency Baseline:**

- Total behaviors: 5
- CORE: 3 (≥5 reinforcements)
- SECONDARY: 2 (2-4 reinforcements)
- NOISE: 0 (1 reinforcement)

- **CORE Behaviors:**
  - "prefers understanding principles first" (N=6, conf=0.12)
  - "prefers hands-on examples" (N=9, conf=0.18)
  - "wants theoretical explanations" (N=7, conf=0.14)

**Stability System:**

- Total behaviors: 5
- CORE: 0 (stability ≥0.15)
- SECONDARY: 0
- Clusters formed: 0


**Agreement:** FREQ OVER-PROMOTES (3 vs 0)

---


### user_sparse_01 - Scattered Sam - high reinf, low stability

**Frequency Baseline:**

- Total behaviors: 5
- CORE: 3 (≥5 reinforcements)
- SECONDARY: 2 (2-4 reinforcements)
- NOISE: 0 (1 reinforcement)

- **CORE Behaviors:**
  - "prefers step-by-step instructions" (N=7, conf=0.14)
  - "prefers quick summaries" (N=5, conf=0.10)
  - "learns by doing" (N=6, conf=0.12)

**Stability System:**

- Total behaviors: 5
- CORE: 0 (stability ≥0.15)
- SECONDARY: 0
- Clusters formed: 0


**Agreement:** FREQ OVER-PROMOTES (3 vs 0)

---


### user_research_01 - Academic Alice - dispersed behaviors

**Frequency Baseline:**

- Total behaviors: 5
- CORE: 4 (≥5 reinforcements)
- SECONDARY: 1 (2-4 reinforcements)
- NOISE: 0 (1 reinforcement)

- **CORE Behaviors:**
  - "asks for technical specifications" (N=6, conf=0.12)
  - "wants detailed documentation" (N=7, conf=0.14)
  - "interested in research citations" (N=7, conf=0.14)
  - "needs architectural overviews" (N=5, conf=0.10)

**Stability System:**

- Total behaviors: 5
- CORE: 0 (stability ≥0.15)
- SECONDARY: 0
- Clusters formed: 0


**Agreement:** FREQ OVER-PROMOTES (4 vs 0)

---


### user_tiny_01 - Minimal Mike - very few interactions

**Frequency Baseline:**

- Total behaviors: 2
- CORE: 1 (≥5 reinforcements)
- SECONDARY: 1 (2-4 reinforcements)
- NOISE: 0 (1 reinforcement)

- **CORE Behaviors:**
  - "likes sequential guides" (N=8, conf=0.16)

**Stability System:**

- Total behaviors: 2
- CORE: 0 (stability ≥0.15)
- SECONDARY: 0
- Clusters formed: 0


**Agreement:** FREQ OVER-PROMOTES (1 vs 0)

---

## Analysis

- **Total CORE behaviors across all users:**
  - Frequency Baseline: 17
  - Stability System: 0
  - Difference: 17

**Key Finding:** Frequency baseline promotes more behaviors to CORE than stability system.
This suggests the stability system is more conservative, filtering out high-reinforcement
behaviors with low semantic clustering stability.
