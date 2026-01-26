
Good. Here is the **clean, unfiltered issue list** — no padding, no reassurance.
This is exactly what is **actually wrong, incomplete, or conceptually inconsistent** in your current CBIE system.

---

## 1. Dual confidence systems (unresolved conflict)

**Issue**

* You compute **two different notions of confidence**:

  * Stability-based confidence (from HDBSCAN)
  * Distance/coherence-based confidence (intra-cluster metrics)
* Only one is used for epistemic decisions, but both are stored and exposed.

**Why it’s a problem**

* Creates conceptual ambiguity: density-first vs similarity-first
* Looks like an incomplete refactor, not an intentional design

**Status**

* ❌ Conceptual inconsistency
* ✅ Acceptable if explicitly framed as “diagnostic vs authoritative”

---

## 2. Epistemic CORE threshold depends on median stability

**Issue**

* CORE classification uses:

  * absolute threshold (0.15)
  * relative threshold (median stability)

**Why it’s a problem**

* Median is unstable with:

  * small number of clusters
  * uniform stability distributions
* Can arbitrarily suppress CORE detection

**Status**

* ❌ Statistically fragile
* ✅ Defensible as conservative inference (must be stated)

---

## 3. Premature CORE detection with very small clusters

**Issue**

* Clusters with as few as **3 observations** can be marked CORE.

**Why it’s a problem**

* Weak empirical support
* Violates intuitive notion of “stable preference”
* Looks suspicious to evaluators

**Root cause**

* No explicit **minimum cluster size** gate

**Status**

* ❌ Missing constraint
* ✅ Acceptable as future optimization

---

## 4. No temporal information in clustering geometry

**Issue**

* Clustering is done purely in embedding space
* Time is only applied **after** clustering

**Why it’s a problem**

* Short-term bursts and long-term habits are treated identically
* Violates “stability over time” claim at clustering stage

**Status**

* ❌ Conceptual gap
* ✅ Acceptable if framed as post-clustering inference

---

## 5. Behavior frequency underutilized

**Issue**

* Frequency only influences:

  * cluster size
  * log-scaled strength
* It does **not** affect clustering itself

**Why it’s a problem**

* Repeated behaviors don’t pull clusters together more strongly
* Weakens density signal

**Status**

* ❌ Incomplete evidence integration
* ✅ Acceptable for MVP

---

## 6. UMAP / 2D visualization can mislead

**Issue**

* 2D projection shown alongside clustering results
* UMAP does not preserve global distances

**Why it’s a problem**

* Visual clusters ≠ actual clusters
* Easy to overinterpret or misrepresent correctness

**Status**

* ❌ High risk if oversold
* ✅ Safe if framed as illustrative only

---

## 7. Canonical labels and cluster names are non-deterministic

**Issue**

* LLM-generated labels can change across runs

**Why it’s a problem**

* Appears unstable to reviewers
* Breaks reproducibility illusion

**Status**

* ❌ Perception risk
* ✅ Acceptable if declared as UI-only interpretation

---

## 8. Archetype generation lacks epistemic safeguards

**Issue**

* Archetype generated from CORE clusters only
* No minimum count or diversity requirement

**Why it’s a problem**

* One dominant cluster can overdefine user
* Archetype may be brittle early on

**Status**

* ❌ Overconfident abstraction
* ✅ Acceptable as exploratory output

---

## 9. No explicit handling of negative or contradictory evidence

**Issue**

* No modeling of:

  * preference abandonment
  * contradiction
  * reversal

**Why it’s a problem**

* System only accumulates evidence
* Cannot unlearn or weaken preferences meaningfully

**Status**

* ❌ Major theoretical limitation
* ✅ Future work (not required now)

---

## 10. Confidence calibration is dataset-dependent

**Issue**

* Confidence values are relative to:

  * current clusters
  * current user history

**Why it’s a problem**

* Cannot compare confidence across users
* No global calibration

**Status**

* ❌ Limits generalization
* ✅ Out of scope for now

---

## 11. Stability score interpretation is opaque

**Issue**

* HDBSCAN stability is used directly
* No normalization or explanation in output

**Why it’s a problem**

* Hard to interpret
* Looks like a magic number

**Status**

* ❌ Explainability gap
* ✅ Fine if hidden from UI

---

## 12. No cross-session reinforcement modeling

**Issue**

* Session boundaries are stored but unused

**Why it’s a problem**

* Repeated behavior in one session ≠ repeated across sessions
* Missed signal for true preference

**Status**

* ❌ Missed evidence dimension
* ✅ Future enhancement

---

## 13. No explicit “cold start” policy

**Issue**

* System treats small datasets the same as mature ones

**Why it’s a problem**

* Early inferences can look arbitrary

**Status**

* ❌ Missing policy
* ✅ Explainable via conservatism framing

---

## 14. Behavior extraction quality assumed, not validated

**Issue**

* Extraction credibility is trusted implicitly

**Why it’s a problem**

* Garbage in → clustered garbage
* No feedback loop

**Status**

* ❌ External dependency risk
* ✅ Out of scope (correctly separated)

---

## Bottom-line classification

### Critical (must be framed explicitly)

* #1 Dual confidence systems
* #2 Median-based CORE threshold
* #6 Visualization interpretation

### Medium (acceptable for 50%)

* #3 Small cluster CORE
* #4 No temporal clustering
* #5 Frequency underuse
* #8 Archetype brittleness

### Future work (safe to defer)

* #9 Negative evidence
* #10 Global calibration
* #12 Session-aware modeling
* #13 Cold start handling

---

If you want next:

* I can compress this into **one clean “Limitations” slide**
* Or give you **defensive answers** for each issue if questioned

Your move.
