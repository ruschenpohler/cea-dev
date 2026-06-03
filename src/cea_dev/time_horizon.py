"""Time horizon and discounting module.

Phase 2: Relaxes Assumptions A1 (proportional costs), A2 (one-year horizon),
and A3 (no decay). Introduces heterogeneous durations, exponential effect
decay, and fixed/variable cost decomposition.
"""

from dataclasses import dataclass

import pandas as pd

from cea_dev.core import Intervention, InterventionSet

_DEFAULT_BENEFICIARIES = 1000


@dataclass
class DiscountedIntervention:
    """Wraps Intervention with time-adjusted effective effect and adjusted cost."""

    intervention: Intervention
    n_beneficiaries: int = _DEFAULT_BENEFICIARIES

    @property
    def discounted_effect(self) -> float:
        # RELAXING A2, A3: heterogeneous duration and decay
        tau = self.intervention.effect_sd
        rho = self.intervention.annual_decay_rate
        r = self.intervention.discount_rate
        T = self.intervention.duration_years
        return tau * sum(rho**t / (1 + r) ** t for t in range(T))

    @property
    def adjusted_cost(self) -> float:
        # RELAXING A1: non-zero fixed costs
        fixed = self.intervention.fixed_cost
        var = self.intervention.variable_cost_per_participant
        p_c = self.intervention.compliance_rate
        return fixed / self.n_beneficiaries + var / p_c

    @property
    def effectiveness(self) -> float:
        return self.discounted_effect / self.adjusted_cost

    @property
    def ce_display(self) -> float:
        return 0.1 / self.effectiveness


class DiscountedInterventionSet:
    def __init__(
        self,
        interventions: list[DiscountedIntervention],
        n_beneficiaries: int = _DEFAULT_BENEFICIARIES,
    ):
        self.interventions = interventions
        self.n_beneficiaries = n_beneficiaries

    def league_table(self) -> pd.DataFrame:
        df = pd.DataFrame(
            [
                {
                    "name": di.intervention.name,
                    "effect_sd": di.intervention.effect_sd,
                    "discounted_effect": round(di.discounted_effect, 4),
                    "adjusted_cost": round(di.adjusted_cost, 2),
                    "effectiveness": di.effectiveness,
                    "ce_display": di.ce_display,
                }
                for di in self.interventions
            ]
        )
        df = df.sort_values("effectiveness", ascending=False).reset_index(drop=True)
        df.index = df.index + 1
        df.index.name = "rank"
        return df

    def ranking_shift(self, baseline: InterventionSet) -> pd.DataFrame:
        p2 = self.league_table().reset_index()
        p2["rank_phase2"] = p2["rank"]
        p2 = p2[["name", "rank_phase2", "effectiveness", "ce_display"]]
        p2 = p2.rename(
            columns={
                "effectiveness": "effectiveness_p2",
                "ce_display": "ce_display_p2",
            }
        )

        p1 = baseline.league_table().reset_index()
        p1["rank_phase1"] = p1["rank"]
        p1 = p1[["name", "rank_phase1", "effectiveness", "ce_display"]]
        p1 = p1.rename(
            columns={
                "effectiveness": "effectiveness_p1",
                "ce_display": "ce_display_p1",
            }
        )

        merged = p1.merge(p2, on="name")
        merged["rank_shift"] = merged["rank_phase2"] - merged["rank_phase1"]
        merged = merged.sort_values("rank_phase2").reset_index(drop=True)
        merged.index = merged.index + 1
        merged.index.name = "rank"
        return merged[
            [
                "name",
                "rank_phase1",
                "rank_phase2",
                "rank_shift",
                "ce_display_p1",
                "ce_display_p2",
            ]
        ]

    @classmethod
    def from_intervention_set(
        cls,
        intervention_set: InterventionSet,
        n_beneficiaries: int = _DEFAULT_BENEFICIARIES,
    ) -> "DiscountedInterventionSet":
        interventions = [
            DiscountedIntervention(iv, n_beneficiaries=n_beneficiaries)
            for iv in intervention_set.interventions
        ]
        return cls(interventions, n_beneficiaries=n_beneficiaries)
