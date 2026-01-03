# Threshold Sensitivity Analysis Results

**Generated:** 2026-01-03 10:19:37

**Thresholds tested:** 0.05, 0.1, 0.15, 0.2

---

## Summary: CORE Behavior Counts by Threshold

| User | Total Behaviors | 0.05 | 0.10 | 0.15 | 0.20 | Clusters | Max Stability |

|------|----------------|------|------|------|------|----------|---------------|
| user_stable_01 | 3 | 0 | 0 | 0 | 0 | 0 | 0.000 |
| user_large_01 | 5 | 0 | 0 | 0 | 0 | 0 | 0.000 |
| user_mixed_01 | 5 | 0 | 0 | 0 | 0 | 0 | 0.000 |

---

## Detailed Results


### user_stable_01 - Visual Viktor - tight clustering

**Clustering Analysis:**

- Clusters formed: 0
- Cluster sizes: []
- Stability scores: []
- Noise points: 3
- HDBSCAN params: min_cluster_size=N/A, min_samples=N/A

**Classification by Threshold:**


*Threshold: 0.05*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 3

*Threshold: 0.10*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 3

*Threshold: 0.15*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 3

*Threshold: 0.20*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 3

---


### user_large_01 - Dedicated Dana - many interactions

**Clustering Analysis:**

- Clusters formed: 0
- Cluster sizes: []
- Stability scores: []
- Noise points: 5
- HDBSCAN params: min_cluster_size=N/A, min_samples=N/A

**Classification by Threshold:**


*Threshold: 0.05*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 5

*Threshold: 0.10*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 5

*Threshold: 0.15*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 5

*Threshold: 0.20*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 5

---


### user_mixed_01 - Balanced Beth - mixed stability

**Clustering Analysis:**

- Clusters formed: 0
- Cluster sizes: []
- Stability scores: []
- Noise points: 5
- HDBSCAN params: min_cluster_size=N/A, min_samples=N/A

**Classification by Threshold:**


*Threshold: 0.05*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 5

*Threshold: 0.10*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 5

*Threshold: 0.15*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 5

*Threshold: 0.20*
- CORE: 0
- SECONDARY: 0
- INSUFFICIENT: 5

---

## Key Findings

**Total CORE behaviors across all users:**

- Threshold 0.05: 0 CORE behaviors
- Threshold 0.10: 0 CORE behaviors
- Threshold 0.15: 0 CORE behaviors
- Threshold 0.20: 0 CORE behaviors

**Clustering Observations:**
- Users with 0 clusters: 3/3

**Recommendation:**
- Current data produces very low stability scores
- Issue may be: (1) HDBSCAN parameters too strict, (2) embeddings not clusterable, (3) data too small