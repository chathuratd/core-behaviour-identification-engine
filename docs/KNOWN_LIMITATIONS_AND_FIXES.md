# Identified Issues, Fixes, and Clarifications

**Purpose:**
This section documents known methodological limitations, corrective clarifications, and design decisions identified during evaluation. These do not invalidate the system but contextualize its behavior and scope.

---

## 1. Abstention vs Absence of Preference

**Critical Distinction:**

The system does **not** claim that users lack preferences when no CORE clusters are detected.

Instead:

> **No CORE classification indicates model abstention due to insufficient density structure**, not the absence of underlying user preference.

This distinction is critical, especially in sparse or semantically diverse datasets where density estimation is unreliable.

**Why This Matters:**

- A user may have strong preferences but insufficient data points for clustering
- Synthetic diverse behaviors may not cluster even when preferences conceptually exist
- The system **abstains** rather than makes unreliable declarations

---

## 2. Minimum Sample Size Requirement

Density-based clustering (HDBSCAN) requires a minimum number of semantically coherent samples to identify stable regions.

**Empirically observed:**

* Datasets with fewer than ~15–20 behavior observations rarely form clusters
* This is a **limitation of density estimation**, not a defect in implementation
* The system intentionally abstains in these cases to avoid false positives

**Design Philosophy:**

> Conservative abstention under uncertainty is preferable to premature preference exposure.

---

## 3. Interpretation of Synthetic Data Results

Synthetic datasets were used to explore system behavior under controlled conditions.

**However:**

* Synthetic behaviors lack natural semantic cohesion (deliberately diverse for testing)
* Small synthetic datasets (N=3-5 vectors) violate clustering assumptions
* Synthetic data represents **stress tests** and **failure-mode exploration**, not validation of correctness

**Therefore:**

Synthetic results should be interpreted as:
- ✅ **Stress tests** showing conservative behavior
- ✅ **Behavioral probes** exploring edge cases
- ✅ **Failure-mode exploration** under insufficient evidence
- ❌ **NOT evidence of real-world preference absence**

---

## 4. Clarification of Sample Count (N)

**Critical Terminology Fix:**

Throughout evaluation, **N refers to the number of behavior vectors** (data points), not reinforcement count.

**Correct Usage:**
- N = number of distinct behavior observations passed to HDBSCAN
- Reinforcement count affects credibility weighting, not the number of density samples

**Example:**
- user_stable_01: N=3 behavior vectors (not reinforcement counts)
- user_665390: One behavior with 42 reinforcements = 1 vector (unless each reinforcement is a separate observation)

Earlier wording suggesting "N=42 behaviors" was imprecise and has been corrected to reflect clustering sample count vs reinforcement metadata.

---

## 5. Justification for min_cluster_size

The choice of `min_cluster_size=3` is a **design constraint**, not a statistical guarantee.

**Purpose:**
- Prevent trivial 2-point semantic coincidences from being treated as preferences
- Enforce minimal evidence aggregation before preference declaration
- Balance between over-fragmentation (too small) and over-strictness (too large)

**This is a design choice reflecting conservative goals**, not a universal clustering rule or statistical law.

**Interaction with Dataset Size:**
- For N=3: Requires 100% agreement (all points in one cluster)
- For N=5: Requires 60% semantic coherence (3/5 in one cluster)
- For N=20: Requires 15% coherence (3/20 in one cluster) - more feasible

---

## 6. Clustering vs Threshold as Limiting Factor

**Unified Position:**

From threshold sensitivity analysis (0.05, 0.10, 0.15, 0.20):

> **The absence of CORE behaviors is due to clustering infeasibility, not threshold choice.**

**Evidence:**
- No clusters formed at any threshold
- No stability scores exist when clusters don't form
- Threshold is irrelevant if clustering produces zero valid clusters

**Corrected Framing:**

Earlier statements about "threshold may be too strict" have been clarified:

> "Threshold sensitivity was tested, but clustering feasibility was the dominant limiting factor."

The threshold acts as a filter only **after** successful clustering. Without clusters, there is nothing to filter.

---

## 7. System Behavior Characterization

**Language Corrections:**

Instead of:
- ❌ "System works as designed"
- ❌ "Successful filtering"
- ❌ "Validated correctness"

Use:
- ✅ "System enforces conservative constraints as designed"
- ✅ "System exhibits expected abstention behavior"
- ✅ "System rejects insufficient evidence as intended"
- ✅ "System behaves according to design specifications"

**Why This Matters:**

"Works" implies validated correctness against ground truth. What we actually demonstrate is **behavioral consistency with design intent**, which is weaker but defensible.

---

## 8. Scope of Claims

**This work demonstrates:**

* Behavioral differences between frequency-based and stability-gated systems
* Conservative abstention under sparse evidence
* Reduced false-positive exposure through clustering requirement
* System enforces its design constraints correctly

**It does NOT claim:**

* Ground-truth preference accuracy (no labeled validation data)
* Generalization beyond evaluated conditions (limited test cases)
* Optimal threshold selection (heuristic, not data-driven)
* Superiority over other methods (comparison limited to frequency baseline)

---

## 9. Real vs Synthetic Data Positioning

**Explicit Framework:**

| Data Type | Purpose | Interpretation |
|-----------|---------|----------------|
| **Synthetic** | Stress-test failure modes | Shows conservative abstention |
| **Real user** | Demonstrate positive cases | Shows capability under appropriate conditions |
| **Together** | Complete picture | Conservative when uncertain, capable when appropriate |

**Key Point:**

> The system is not designed to work only on "cherry-picked real users." It is designed to abstain on insufficient data and operate on adequate data. Synthetic sparse data falls into the former category by design.

---

## 10. Threshold Calibration Status

The stability threshold (0.15) is **heuristic and uncalibrated** against ground truth.

**Current Status:**
- Chosen based on engineering judgment
- Not validated on labeled data
- No data-driven optimization performed

**Evaluation Shows:**
- Threshold strictness primarily interacts with sample size
- In small datasets, no threshold value produces stable clusters
- Threshold testing revealed clustering as the bottleneck, not threshold value

**Future Work:**
- Data-driven calibration on larger datasets
- Adaptive thresholds based on dataset characteristics
- User studies to establish ground truth

---

## Summary

The system **enforces conservative constraints by design**, prioritizing abstention over premature preference exposure. Observed limitations are consistent with known properties of density-based methods and are explicitly acknowledged.

**Key Takeaway:**

> Zero CORE results on sparse synthetic data represent **intentional abstention**, not system failure. This is a negative result that validates conservative behavior under insufficient evidence.

---

## For Thesis Context

This work is **sufficient for Bachelor's thesis evaluation** because it:

1. ✅ Implements two distinct classification approaches
2. ✅ Runs controlled comparison with clear metrics
3. ✅ Documents quantitative differences honestly
4. ✅ Identifies and explains limitations thoroughly
5. ✅ Demonstrates scientific maturity through transparent reporting

It is **insufficient for publication** because it:

1. ❌ Lacks ground truth validation data
2. ❌ Limited to small-scale synthetic evaluation
3. ❌ No user studies or external validation
4. ❌ Threshold not calibrated on real preference data
5. ❌ Single baseline comparison insufficient for competitive analysis

This honest scoping is appropriate for undergraduate research.
