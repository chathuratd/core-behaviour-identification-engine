
---

# Research Readiness Gap Analysis & Fix Plan

**Project:** Density-First Latent Preference Inference System
**Purpose:** Convert current implementation into a research-grade contribution
**Status:** Not research-ready (engineering-complete, scientifically incomplete)

---

## 1. Contribution Ambiguity (CRITICAL)

### Problem

The document never clearly states **what is new**.

Right now, reviewers will see:

* Density-based clustering → known
* HDBSCAN persistence → known
* Reject / abstain state → known
* Absolute thresholds → known

Your “contribution” is implied, not defined.

### Why This Fails Research Standards

Research requires **one falsifiable claim**.
You currently have *many reasonable design choices*, but no claim that can be tested or disproven.

### What Must Be Fixed

#### You must add a **Contribution Definition Section** that states ONE of the following (pick one, not all):

**Option A (recommended):**

> A stability-gated abstention framework that prevents false preference inference under sparse behavioral evidence.

**Option B:**

> An empirical demonstration that relative confidence measures systematically overestimate preference certainty in low-density regimes.

**Option C:**

> A density-based reject mechanism for preference inference with improved precision under small-N conditions.

Then explicitly say:

* What existing systems do wrong
* What your system does differently
* What outcome improves

### Required Output

* A section titled **“Research Contribution”**
* One central claim
* One evaluation question tied to that claim

---

## 2. Threshold Arbitrary-ness (CRITICAL)

### Problem

The absolute stability threshold (0.15) is unjustified.

You *say* it’s empirical. It isn’t.

* Single user
* Single run
* No distribution
* No variance
* No sensitivity analysis

This is intuition, not evidence.

### Why This Will Get Rejected

Any reviewer will immediately ask:

> “Why 0.15?”

You have no defensible answer.

### What Must Be Fixed

You must do **at least one** of the following:

#### Fix Option 1: Distributional Calibration (Recommended)

* Collect stability values across:

  * many users
  * many datasets
* Plot stability distributions
* Define CORE as:

  * bottom X% of persistence mass excluded
* Choose threshold based on distribution, not intuition

#### Fix Option 2: Sensitivity Analysis

* Sweep threshold ∈ [0.05, 0.30]
* Measure:

  * false positives
  * abstention rate
* Show that results are *stable* across a range

#### Fix Option 3: Remove Absolute Threshold Claim

* Reframe 0.15 as:

  > “A conservative engineering heuristic”
* Stop claiming epistemic validity

### Required Output

* A **Threshold Justification Section**
* Either a plot, table, or sensitivity narrative
* Explicit admission of limits if heuristic

---

## 3. Misuse of HDBSCAN Stability Semantics (CRITICAL)

### Problem

You treat `cluster_persistence_` as:

* absolute
* comparable
* calibrated

It is none of those.

Persistence depends on:

* min_cluster_size
* min_samples
* distance metric
* data scale

You ignore this dependency.

### Why This Is Dangerous

Your entire epistemic state assignment assumes:

> “0.15 means weak everywhere”

That is false.

### What Must Be Fixed

You must **downgrade the semantic strength** of stability OR normalize it.

#### Required Changes

Add a section titled:

**“Interpretation Limits of HDBSCAN Persistence”**

You must explicitly state:

* Persistence is **relative to a configuration**
* Absolute comparisons are only valid *within controlled settings*

Optional (but strong):

* Normalize persistence by:

  * max persistence in dataset
  * or expected persistence under null (noise-only simulation)

### Required Output

* Clear disclaimer
* Either normalization or scoped validity claim

---

## 4. Credibility Signal Is Structurally Underused (MAJOR)

### Problem

Credibility:

* does NOT influence clustering
* only influences post-hoc labeling

This contradicts your own philosophy.

You are saying:

> “Credibility matters”

Then ignoring it where it matters most.

### Why This Weakens the System

You can get:

* Dense low-credibility junk → promoted
* Sparse high-credibility signal → suppressed

Your epistemic states try to compensate, but that’s reactive, not principled.

### What Must Be Fixed

You must do **one** of the following:

#### Minimal Fix (acceptable)

* Explicitly state:

  > “Credibility is not part of density estimation in this version”
* Reframe system as **two-stage heuristic**

#### Better Fix

* Incorporate credibility via:

  * weighted distance
  * duplication proportional to credibility
  * post-clustering stability reweighting

### Required Output

* A **Credibility Integration Limitations Section**
* Or an actual integration experiment

---

## 5. “Epistemic” Language Without Formalism (MAJOR)

### Problem

You use:

* epistemic
* evidence
* latent truth
* confidence

…but provide **no formal meaning**.

This is philosophical language without mathematical backing.

### Why This Is a Problem

In research, epistemic claims imply:

* uncertainty modeling
* probability
* decision theory

You do none of that.

### What Must Be Fixed

You must **downgrade or formalize**.

#### Option A (Recommended)

Replace language:

* “epistemic state” → “evidence state”
* “epistemic humility” → “conservative filtering”

#### Option B (Harder, better)

Add:

* decision-theoretic framing
* abstention under uncertainty
* selective classification references

### Required Output

* Terminology revision OR formal uncertainty framing
* Citations to selective prediction / abstention literature

---

## 6. Evaluation Is Not Research-Grade (CRITICAL)

### Problem

You evaluated:

* one user
* one dataset
* zero baselines

That’s not evaluation. That’s a demo.

### Why This Is Fatal

A reviewer cannot assess:

* correctness
* robustness
* improvement

### What Must Be Fixed

You need **at least**:

#### Required Experiments

1. **Synthetic Data**

   * Known ground truth clusters
   * Inject noise
   * Measure false CORE detection

2. **Baseline Comparison**

   * Frequency-based confidence
   * Relative confidence without absolute threshold

3. **Ablation**

   * Remove absolute threshold
   * Remove credibility gate
   * Fixed min_cluster_size

4. **Regime Analysis**

   * Small N vs large N

### Required Output

* Evaluation section
* Tables or plots
* Explicit failure cases

---

## 7. Overdocumentation Masking Gaps (MINOR but real)

### Problem

The document is extremely long but avoids:

* formal definitions
* equations
* falsifiable statements

Length is compensating for rigor.

### What Must Be Fixed

* Add formal definitions
* Add pseudo-math
* Reduce narrative repetition

---

## Final Fix Checklist (Non-Negotiable)

To call this **research**, you must:

* [ ] Define ONE clear contribution
* [ ] Justify or downgrade absolute thresholds
* [ ] Clarify limits of HDBSCAN stability
* [ ] Address credibility integration gap
* [ ] Fix epistemic language misuse
* [ ] Add real evaluation with baselines
* [ ] Introduce falsifiable claims

---

## Final Reality Check

Right now:

* You built a **careful system**
* You did **not** yet produce a **scientific result**

That’s not a failure.
But pretending otherwise *would be*.