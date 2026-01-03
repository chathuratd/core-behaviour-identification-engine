# Density-First Latent Preference Inference System

## Required Fixes for Research-Grade Validity

---

## 0. Purpose of This Document

This document identifies **concrete deficiencies** in the current Density-First Latent Preference Inference System and specifies **exact fixes** required to make it defensible as a research contribution rather than merely a solid engineering artifact.

This is not a roadmap of nice-to-haves. These are **blocking issues** that reviewers *will* attack.

---

## 1. Core Problem: Unjustified Absolute Stability Thresholds

### Current State

* Absolute CORE threshold hard-coded at **0.15**
* Justification is intuitive / empirical-by-feel
* No statistical grounding

### Why This Fails Research Standards

* HDBSCAN stability is **not calibrated** across datasets
* Stability magnitude depends on:

  * embedding geometry
  * density contrast
  * min_cluster_size
  * metric distortions
* Claiming an *absolute* semantic meaning without validation is indefensible

### Required Fix

You must do **at least one** of the following:

#### Fix A — Empirical Calibration (Preferred)

* Collect stability distributions across:

  * many users
  * varying dataset sizes
* Plot:

  * stability vs. cluster size
  * stability vs. human-judged preference coherence
* Select threshold based on:

  * false-positive minimization
  * stability quantiles across populations

#### Fix B — Theoretical Weakening (Minimum Acceptable)

* Reframe 0.15 as:

  * an *engineering heuristic*
  * a *conservative operational gate*
* Explicitly state:

  > “The threshold is not semantically absolute; it enforces a bias toward false negatives.”

**One of these is mandatory.**

---

## 2. Concept–Math Mismatch: “Density-First” Is Currently Rhetorical

### Current State

* Density computed via unweighted HDBSCAN
* Credibility applied **after** clustering
* Sample weights explicitly unsupported

### Why This Is a Problem

You claim:

> “Density as Truth”

But mathematically:

* credibility has **zero influence** on density estimation
* density ≠ evidence strength

This is a philosophy–implementation contradiction.

### Required Fix (Pick One)

#### Fix A — Rename Honestly (Fastest)

Rename the method to something like:

* *Density-Gated Epistemic Preference Inference*
* *Density-Filtered Latent Preference Detection*

And explicitly state:

> “Density estimates are unweighted; credibility is applied as a secondary epistemic filter.”

#### Fix B — Minimal Credibility Integration

Implement **any** mathematically defensible coupling, e.g.:

* duplicate samples proportional to credibility
* credibility-scaled distance metric
* pre-clustering pruning using credibility quantiles

Without this, “density-first” is a semantic overreach.

---

## 3. Small-N Bias Is Unacknowledged Prior, Not a Neutral Property

### Current State

* System intentionally suppresses CORE for N < 20
* Framed as epistemic truth

### Why This Is Dangerous

You are encoding a **prior belief**:

> “Preferences cannot exist without visible density.”

That is a design choice — not a law.

### Required Fix

You must explicitly state:

* this is a **conservative bias**
* optimized for false-positive avoidance
* unsuitable for early preference detection

Suggested wording:

> “The system intentionally sacrifices early recall in favor of stability, imposing a conservative epistemic prior.”

Without this, reviewers will call the system blind by construction.

---

## 4. Credibility Aggregation Is Underspecified and Inconsistent

### Current State

* Mean credibility used
* Logs contradict manual calculation
* Weighting logic unclear

### Why This Undermines Trust

If credibility aggregation is ambiguous:

* classifications become non-reproducible
* results appear arbitrary

### Required Fix

You must:

1. Define credibility aggregation formally
2. Provide explicit formula
3. Ensure logs match computation

Example:

```
mean_credibility = (Σ credibility_i) / |cluster|
```

If additional weighting exists, it **must** be documented.

---

## 5. HDBSCAN Stability Semantics Are Overinterpreted

### Current State

* Stability treated as semantic cohesion
* No discussion of MST-based origin

### Why This Is Incorrect

HDBSCAN stability measures:

* persistence across density thresholds
* not semantic similarity per se

### Required Fix

Add a clarification section:

* explain what stability actually measures
* explicitly limit interpretation

Example:

> “Cluster stability reflects persistence under density variation, which we use as a proxy — not a guarantee — of semantic coherence.”

This prevents overclaiming.

---

## 6. Lack of Baseline Comparisons

### Current State

* No comparison to simpler methods

### Why This Matters

Without baselines, reviewers will ask:

> “Why not just frequency or cosine clustering?”

### Required Fix

Add at least **one** baseline:

* frequency-only preference inference
* centroid cosine similarity clustering

Show where your system:

* suppresses false positives
* behaves differently by design

---

## 7. Overconfident Terminology in Conclusion

### Current State

* Phrases like “principled”, “truth”, “ready”

### Why This Backfires

Your system is conservative and incomplete — which is fine — but your language doesn’t admit that.

### Required Fix

Tone down claims:

* emphasize limitations
* emphasize tradeoffs
* emphasize scope

Replace:

> “Density as Truth”

With:

> “Density as a Conservative Evidence Filter”

---

## 8. Missing Formal Problem Statement

### Current State

* Implicit assumptions scattered across sections

### Required Fix

Add a **formal problem definition**:

* input
* noise model assumption
* output
* optimization goal

Even a simple formalization drastically increases credibility.

---

## 9. Summary: What Must Change Before Research Submission

### Mandatory Fixes

* [ ] Justify or weaken absolute stability thresholds
* [ ] Resolve density–credibility mismatch
* [ ] Explicitly acknowledge conservative bias
* [ ] Formalize credibility aggregation
* [ ] Limit interpretation of HDBSCAN stability

### Strongly Recommended

* [ ] Add baselines
* [ ] Add empirical plots
* [ ] Tighten language

---

## Final Assessment

**Right now**: strong engineering system with good epistemic instincts.

**After fixes**: defensible research contribution about *conservative preference inference under uncertainty*.

If you skip these fixes, the system will look clever but sloppy. If you address them, it will look deliberate and serious.

---

*Status*: Action Required
