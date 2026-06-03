# Feedback Document: cea-dev Implementation Plan

This document consolidates agreed revisions to the implementation plan dated 2026-06-03. Each item states the current approach, the identified limitation, and the precise change to be implemented.

---

## 1. Effect metric and presentation

**Current:** CE ratio defined as cost per effect, with direct bootstrap of the ratio.

**Issue:** Division by effect estimates near zero produces unstable ratios and infinite variance. The education literature standardizes on cost per 0.1 SD, but standard deviations lack direct policy meaning.

**Agreed change:**
- Compute internally as effectiveness = (effect × adjustments) / cost, in SD per dollar.
- Transform to cost per 0.1 SD only for display tables and figures.
- Calculate all uncertainty intervals on the SD-per-dollar scale, then transform. Document that intervals are asymmetric after inversion.
- Retain SD as the core metric. Add a single sentence flagging the need for contextual translation and the difficulty of doing so comparably across settings.

**README location:** Section 3, after CE ratio definition. Include citations to STRIPES (cost per 0.1 SD), STRIPES2, and Dhaliwal et al. 2013 for convention.

**Implementation:** Modify `core.py`, `uncertainty.py`, `psa.py` to store value; add inversion in `visualization.py`.

---

## 2. Cost structure and compliance

**Current:** Assumes total cost scales proportionally with compliance, implying ITT and TOT yield identical CE ratios.

**Issue:** The invariance holds only under zero fixed costs, which is false for most education and training programs.

**Agreed change:**
- Add fields `fixed_cost` and `variable_cost_per_participant` to `interventions.csv`.
- Define adjusted cost = fixed_cost + variable_cost / compliance_rate.
- Keep proportional-cost case as default. Tag in code as `# ASSUMPTION A1: proportional costs`.
- Allow users to supply either ITT effects with full cost or TOT effects with variable cost.

**README location:** Section 4, within adjustment factors.

**Implementation:** Phase 2, `adjustments.py`.

---

## 3. Uncertainty framework

**Current:** Parametric bootstrap presented as primary uncertainty, with PSA and Bayesian as extensions.

**Issue:** The plan implies sampling error dominates. Empirical reporting shows otherwise.

**Agreed change:**
- Core model propagates only sampling uncertainty via parametric draws from reported effect SEs.
- Treat cost uncertainty, discount rates, and external-validity adjustments as deterministic sensitivity parameters in the core.
- Add a README paragraph at the start of Section 5 explaining the limitation.

**README text to insert:**

> The model propagates uncertainty that originates in sampling variation of impact estimates. This choice reflects reporting practice in the underlying literature. Recent randomized evaluations routinely report clustered standard errors but rarely report quantitative uncertainty for costs, discount rates, or external-validity adjustments. Cost data are often not reported at all, or are reported without component detail, which limits comparability. Impact estimates are sensitive to sampling error, and confidence intervals around impacts propagate directly into rankings. An audit of ten high-profile studies published between 2015 and 2023 (Banerjee et al. 2015; Egger et al. 2022; Parker and Vogl 2023; Muralidharan et al. 2019; Alfonsi et al. 2020; Bandiera et al. 2020; Crépon et al. 2015; Olken et al. 2021; Muralidharan et al. 2016; Bruhn et al. 2018), spanning graduation programs, cash transfers, education technology, youth training, and health insurance, found no study that reports a standard error for costs, and only studies with multi-year horizons report a discount rate. For this reason the core model treats non-sampling sources of uncertainty as deterministic sensitivity parameters rather than as distributions.

**Implementation:** Remove non-parametric bootstrap from main flow. Retain one-sentence note on infeasibility due to lack of unit-level data.

---

## 4. Adjustment factors

**Current:** Three independent Beta-distributed factors for external validity, counterfactual, and fidelity.

**Issue:** Independence understates tail risk; bounded [0,1] precludes improvements over original efficacy.

**Agreed change:**
- Retain independence and Beta [0,1] for version 1. Add brief note stating the assumption.
- Document ideal data structure for future correlated modeling: site-level replications with measured fidelity scores and context distance metrics.

**README location:** Section 4, after factor definitions.

---

## 5. Cost uncertainty

**Current:** Hard-coded 30% coefficient of variation.

**Issue:** Arbitrary and undocumented.

**Agreed change:**
- Rename field to `cost_est`.
- Add optional `cost_low` and `cost_high`.
- If bounds missing, impute ±20%.
- Model costs as lognormal fitted to the two quantiles.
- Flag imputed values in data dictionary.

**README text to insert in Section 4:**

> Cost estimates include a point estimate and, where available, low and high bounds from the source study. When bounds are not reported, we impute a symmetric interval of plus or minus 20% around the point estimate. We model costs as lognormal to respect positivity. Imputed intervals are flagged in the data file.

---

## 6. Hierarchical modeling

**Current:** Proposed partial pooling across eight diverse interventions.

**Issue:** Requires pre-specified categories that do not generalize across literatures. Violates exchangeability for programs like graduation or cash-plus.

**Agreed change:**
- Remove hierarchical pooling from core.
- Retain Bayesian module as optional extension, applicable only when multiple independent evaluations of the identical protocol exist.
- Add README discussion of optimizer's curse: rankings based on point estimates favor noisy programs. Report rank probabilities integrated over sampling uncertainty as the primary mitigation.

**Documentation:** Note in feedback that hierarchical approach is undercooked for cross-domain use.

---

## 7. Handling non-positive effects

**Current:** Set CE = NaN when effect ≤ 0, discarding draws.

**Issue:** Biases rank probabilities upward for uncertain interventions.

**Agreed change:**
- For each simulation draw, compute value = effect × adjustments / cost.
- If effect ≤ 0, set value = 0.
- Rank all interventions on value in each draw.
- Report P(best) = proportion of draws with rank 1.
- Report P(harm) = proportion of draws with effect ≤ 0.

**README location:** Section 5, uncertainty outputs.

---

## 8. Time horizon and discounting

**Current:** No explicit time dimension.

**Issue:** Education effects fade; other domains differ.

**Agreed change:**
- Core: assume effect persists for user-specified duration, default 1 year. Discount future benefits at user-specified annual rate, default 3%.
- Extension: exponential decay model. Effective impact = effect0 × Σ_{t=0}^{T-1} rho^t / (1+r)^t. User sets rho based on follow-up evidence.

**README text to insert in Section 5:**

> Effects are assumed to persist for a user-specified duration, with a default of one year. Future benefits are discounted at a user-specified annual rate, with a default of three percent. An extension allows exponential decay of effects over time. The decay parameter determines the share of the initial effect retained each year. Users set the parameter based on available follow-up evidence.

---

## 9. Testing

**Agreed additions:**
- Monotonicity: increasing cost by 10% worsens CE for all interventions.
- Invariance: scaling all costs by constant leaves rankings unchanged.
- Stress: setting all adjustments to 1 recovers unadjusted league table.
- Rank sum: after PSA, sum_k P(rank=k) = 1 for each intervention within tolerance.
- Reproducibility: identical seed produces identical draws.

**Implementation:** `tests/test_core.py`, `test_bootstrap.py`, `test_psa.py`.

---

## 10. Cost reporting

**Current:** Ambiguous about composition.

**Agreed change:**
- Accept reported cost as given.
- Document variation in composition.

**README text to insert in Section 3:**

> We use the cost estimate reported in each source study. Studies vary in the composition of the cost estimate they report, that is, whether they include implementation overheads, volunteer time, household costs, etc. Detailed ingredient lists are rare in published work. Costs are often not reported at all, or are reported without component detail, which limits comparability.

---

## 11. README organization and language

**Agreed changes:**
- Open with decision problem, not taxonomy. Move CEA vs CBA comparison to glossary appendix.
- Maintain technical precision. Lead paragraphs with the claim, follow with explanation. Avoid conversational self-talk and parallel constructions.
- Keep six-notebook structure for guided walkthrough. Add optional single-notebook dashboard as post-hoc deliverable.

---

## Action items for implementation team

1. Refactor core metric to SD per dollar with inversion for display.
2. Add fixed/variable cost fields and compliance adjustment.
3. Remove non-parametric bootstrap; implement parametric-only uncertainty with unconditional probabilities.
4. Implement cost band logic with ±20% default.
5. Implement persistence and discounting parameters.
6. Update README sections 2–5 with the exact paragraphs above.
7. Add tests for monotonicity, invariance, rank sums, and reproducibility.
8. Move hierarchical Bayes to `extensions/` folder, gated behind explicit grouping variable.
