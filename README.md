# Cost-Effectiveness Analysis in Development Economics

## 1. What is CEA?

Cost-effectiveness analysis (CEA) answers the question: given a fixed budget, which intervention produces the largest total outcome on a particular metric? It compares all kinds of interventions within a single outcome domain and expresses value as _cost per unit of outcome achieved_.

This differs from cost-benefit analysis which compares interventions across outcome domains, often using moral weights, income-doubling equivalents, etc.

---

## 2. The Worked Example: Eight Education Interventions

**Outcome:** Improvement in standardized test scores, measured in standard deviations (SD). The display metric is _cost per 0.1 SD gain per beneficiary_, a comon metric in education research.

The table below illustrates the shape of the data needed. Note that all parameters are synthetics but calibrated to plausible ranges in the education literature.

| Intervention | Effect (SD) | Cost/ben. ($) | Duration (yrs) |
|---|---|---|---|
| Teaching at the Right Level (TaRL) | 0.18 | 4.00 | 2 |
| Structured pedagogy | 0.12 | 8.00 | 2 |
| Computer-assisted learning (CAL) | 0.14 | 12.00 | 3 |
| School meals | 0.09 | 15.00 | 1 |
| Early childhood development (ECD) | 0.22 | 25.00 | 10 |
| Teacher performance pay | 0.10 | 18.00 | 2 |
| Conditional cash transfer (CCT) | 0.07 | 22.00 | 3 |
| Deworming | 0.05 | 2.00 | 1 |

*For the full parameter table with standard errors, compliance rates, and cost bounds use the entrypoint `src/generate_data.py`.*

### What this analysis can and cannot tell you

The cost-effectiveness ratios in this framework are computed from effect estimates and cost figures of the type usually reported in evaluation studies. Effect estimates carry sampling uncertainty; that is, the standard error reflects the fact that the study observed one sample from a population, and a different sample would have produced a different estimate. This uncertainty propagates directly into rankings: an intervention that looks like the best buy from point estimates may not look like the best buy once we account for the fact that its effect estimate is imprecise. We quantify and visualize this throughout.

Three further sources of uncertainty exist but cannot typically be quantified from published data. The first is external validity, whether the effect observed in the study population replicates in the target context, which requires multiple independent replications with documented context variation. The second is the counterfactual, whether the target population would receive a comparable intervention in the absence of the experimentally administrated, which requires data on take-up of comparable programs in the target setting. The third is implementation fidelity at scale; that is, whether the effect holds when moving from a supervised research trial to routine government delivery, which requires paired efficacy and effectiveness evaluations of the same protocol. Published evaluations rarely report the data needed to estimate any of these three factors systematically. The closest existing practice is GiveWell's approach of assigning explicit but judgment-based weights to each. Rankings produced by this framework should be read as conditional on the study estimates: informative about relative cost-effectiveness under the assumption that effects replicate, and a starting point for the harder judgment about whether they will.

---

## 3. The Core Model

```
For the core model code, see: [Notebook 01](cea-dev/notebooks/01_core_model.ipynb))
```

**Internal metric:** effectiveness, defined as SD of learning gain per dollar:

$$v_i = \frac{\hat{\tau}_i}{C_i}$$

where $\hat{\tau}_i$ is the estimated effect in SD and $C_i$ is cost per beneficiary in USD. For display, this is inverted and scaled to cost per 0.1 SD:

$$CE_i^* = \frac{0.1}{v_i} = \frac{0.1 \cdot C_i}{\hat{\tau}_i}$$

Working in $v_i$ throughout avoids numerical instability when $\hat{\tau}_i$ is near zero. All uncertainty intervals are computed on the $v_i$ scale and inverted for display; note that this inversion makes confidence intervals asymmetric in the $CE^*$ display metric, which is correct and should not be adjusted away.

### ITT vs. TOT and cost structure

In a randomized controlled trial (RCT), the intent-to-treat (ITT) estimate $\hat{\tau}_{ITT}$ is the average effect over all individuals offered the intervention, including non-compliers. The treatment-on-the-treated (TOT) estimate $\hat{\tau}_{TOT} = \hat{\tau}_{ITT} / p_c$ isolates the effect on those who actually participated, where $p_c$ is the compliance rate. Under the simplifying assumption that total cost scales proportionally with the number of individuals offered the intervention (**Assumption A1: proportional costs**), the CE ratio is invariant to whether ITT or TOT is used, because the compliance rate cancels. This assumption is relaxed in Section 4.

Invariance holds only when all costs are variable; that is, when total program cost scales proportionally with the number of people offered the intervention. Fixed costs, such as curriculum development, staff training, and platform infrastructure, violate this assumption. When fixed costs are material, low compliance spreads them over fewer effective participants, making the cost per complier higher than the cost per person offered. As a consequence, ITT may understate the true cost of achieving a particular effect. Section 4 relaxes the proportional-cost assumption and shows how the CE ratio changes.

### Cost reporting

We use the cost estimate reported in each source study. Studies vary in what their cost estimates include — implementation overheads, volunteer time, household costs, and amortization of capital expenditure are treated inconsistently across the literature. Costs are often reported without component detail. This limits comparability and is a documented constraint of the framework, not a modeling choice.

### A note on time

The table below assumes that effects persist for exactly one year and do not decay thereafter. ECD and CAL produce their effects over longer horizons; school meals and deworming do not. Section 4 introduces heterogeneous durations and annual decay rates, and the ranking shifts materially.

### Unadjusted effets and costs

| Rank | Intervention | Effect (SD) | Cost ($) | Effectiveness (SD/$) | Cost per 0.1 SD ($) |
|---|---|---|---|---|---|
| 1 | Teaching at the Right Level (TaRL) | 0.18 | 4.00 | 0.0450 | 2.22 |
| 2 | Deworming | 0.05 | 2.00 | 0.0250 | 4.00 |
| 3 | Structured pedagogy | 0.12 | 8.00 | 0.0150 | 6.67 |
| 4 | Computer-assisted learning (CAL) | 0.14 | 12.00 | 0.0117 | 8.57 |
| 5 | Early childhood development (ECD) | 0.22 | 25.00 | 0.0088 | 11.36 |
| 6 | School meals | 0.09 | 15.00 | 0.0060 | 16.67 |
| 7 | Teacher performance pay | 0.10 | 18.00 | 0.0056 | 18.00 |
| 8 | Conditional cash transfer (CCT) | 0.07 | 22.00 | 0.0032 | 31.43 |

*See [notebooks/01_core_model.ipynb](cea-dev/notebooks/01_core_model.ipynb) for the computational version and chart.*

---

## 4. Adjustments: Time Horizon and Discounting [→ notebook 02]

```
For the adjustment model code, see: [Notebook 02](cea-dev/notebooks/02_time_horizon.ipynb))
```

The  unadjusted table assumed three things: all costs are proportional to beneficiaries, effects last exactly one year, and they do not decay. All three are wrong for most real interventions. This section relaxes them.

### The adjustment gap

Published evaluations of development interventions rarely report the data needed to adjust for external validity, counterfactual conditions, or implementation fidelity at scale. Of the adjustments that *can* be implemented from published data, time horizon and discounting are the most consequential — and the most defensible. Cost structure (fixed vs. variable) can also be adjusted when studies report cost components separately, though this is uncommon. (For a full discussion of what cannot be adjusted, see Section 2.)

### Discounted effective effect

The effective discounted effect of intervention $i$ is:

$$\hat{\tau}_i^{eff} = \hat{\tau}_i \cdot \sum_{t=0}^{T_i - 1} \frac{\rho_i^t}{(1+r)^t}$$

where $T_i$ is the duration in years, $\rho_i \in (0,1]$ is the annual retention rate (fraction of the initial effect remaining each year), and $r$ is the annual discount rate (default 0.03). When $\rho_i = 1$ and $T_i = 1$, this reduces to $\hat{\tau}_i$, recovering the unadjusted case.

### Fixed vs. variable costs

Relaxing Assumption A1: adjusted cost is defined as

$$C_i^{adj} = \frac{C_i^{fixed}}{N} + \frac{C_i^{var}}{p_{c,i}}$$

where $N$ is the number of beneficiaries (held constant across interventions for comparability, default $N=1{,}000$) and $p_{c,i}$ is the compliance rate. When $C_i^{fixed} = 0$, this reduces to the proportional-cost case.

### Time-adjusted effects and costs

| Rank | Intervention | Unadjusted CE* ($) | Time-adj. CE* ($) | Rank shift |
|---|---|---|---|---|
| 1 | Teaching at the Right Level (TaRL) | 2.22 | 1.48 | — |
| 2 | Early childhood development (ECD) | 11.36 | 2.29 | ↑3 |
| 3 | Deworming | 4.00 | 4.39 | ↓1 |
| 4 | Structured pedagogy | 6.67 | 4.44 | ↓1 |
| 5 | Computer-assisted learning (CAL) | 8.57 | 5.00 | ↓1 |
| 6 | Teacher performance pay | 18.00 | 13.49 | ↑1 |
| 7 | School meals | 16.67 | 17.85 | ↓1 |
| 8 | Conditional cash transfer (CCT) | 31.43 | 21.29 | — |

*See  [notebooks/02_time_horizon.ipynb](cea-dev/notebooks/02_time_horizon.ipynb) for the computational version and side-by-side chart.*


**Headline result:** ECD moves from 5th to 2nd when its 10-year duration is accounted for. Short-duration interventions with low retention (school meals, deworming) lose ground. TaRL remains first, but the gap narrows.


---

## 5. Uncertainty [→ notebook 03]

*(To be implemented)*

---

## 6. Sensitivity Analysis [→ notebook 04]

*(To be implemented)*

---

## 7. Joint Sensitivity Analysis [→ notebook 05]

*(To be implemented)*

---

## 8. Extension: Bayesian CEA [→ extensions/06_bayesian.ipynb]

*(To be implemented)*

---

## Appendix A: Glossary

- **CEA (cost-effectiveness analysis):** Comparison of interventions within a single outcome domain using cost per unit of outcome.
- **CBA (cost-benefit analysis):** Comparison that monetizes all outcomes and compares benefits to costs.
- **Systematic review:** A structured synthesis of all available evidence on a specific question.
- **Meta-analysis:** A statistical combination of effect estimates from multiple studies.
- **ITT (intent-to-treat):** Effect estimated over all individuals offered the intervention, regardless of compliance.
- **TOT (treatment-on-the-treated):** Effect estimated over individuals who actually received the intervention.
- **P(harm):** Probability that an intervention's true effect is zero or negative.

## Appendix B: Mathematical Details

*(To be implemented)*
