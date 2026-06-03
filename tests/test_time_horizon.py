import pytest

from cea_dev.core import Intervention, InterventionSet
from cea_dev.time_horizon import (
    DiscountedIntervention,
    DiscountedInterventionSet,
)


def _make_single() -> Intervention:
    return Intervention(
        name="X",
        effect_sd=0.10,
        effect_se=0.02,
        cost_est=5.0,
        cost_low=4.0,
        cost_high=6.0,
        fixed_cost=0.0,
        variable_cost_per_participant=5.0,
        compliance_rate=1.0,
        duration_years=1,
        annual_decay_rate=1.0,
        discount_rate=0.03,
    )


def _make_set() -> InterventionSet:
    return InterventionSet(
        [
            Intervention(
                name="A",
                effect_sd=0.20,
                effect_se=0.05,
                cost_est=4.0,
                cost_low=3.2,
                cost_high=4.8,
                fixed_cost=0.0,
                variable_cost_per_participant=4.0,
                compliance_rate=1.0,
                duration_years=3,
                annual_decay_rate=0.90,
            ),
            Intervention(
                name="B",
                effect_sd=0.10,
                effect_se=0.03,
                cost_est=2.0,
                cost_low=1.6,
                cost_high=2.4,
                fixed_cost=0.0,
                variable_cost_per_participant=2.0,
                compliance_rate=1.0,
                duration_years=1,
                annual_decay_rate=1.0,
            ),
        ]
    )


class TestDiscountedIntervention:
    def test_discounted_effect_recovers_baseline(self):
        iv = _make_single()
        di = DiscountedIntervention(iv)
        assert di.discounted_effect == pytest.approx(iv.effect_sd)

    def test_discounted_effect_exceeds_effect_for_long_duration(self):
        iv = _make_single()
        long = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=5.0,
            cost_low=4.0,
            cost_high=6.0,
            fixed_cost=0.0,
            variable_cost_per_participant=5.0,
            compliance_rate=1.0,
            duration_years=5,
            annual_decay_rate=0.95,
        )
        di_long = DiscountedIntervention(long)
        assert di_long.discounted_effect > iv.effect_sd

    def test_discounted_effect_equals_effect_when_decay_is_zero(self):
        iv = _make_single()
        full_decay = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=5.0,
            cost_low=4.0,
            cost_high=6.0,
            fixed_cost=0.0,
            variable_cost_per_participant=5.0,
            compliance_rate=1.0,
            duration_years=3,
            annual_decay_rate=0.0,
        )
        di = DiscountedIntervention(full_decay)
        assert di.discounted_effect == pytest.approx(iv.effect_sd)

    def test_adjusted_cost_recovers_phase1_when_no_fixed_cost(self):
        iv = _make_single()
        di = DiscountedIntervention(iv)
        assert di.adjusted_cost == pytest.approx(iv.cost_est)

    def test_adjusted_cost_higher_with_low_compliance(self):
        iv = _make_single()
        low_c = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=5.0,
            cost_low=4.0,
            cost_high=6.0,
            fixed_cost=0.0,
            variable_cost_per_participant=5.0,
            compliance_rate=0.70,
        )
        di = DiscountedIntervention(low_c)
        assert di.adjusted_cost > iv.cost_est

    def test_adjusted_cost_includes_fixed_cost_per_beneficiary(self):
        with_fixed = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=5.0,
            cost_low=4.0,
            cost_high=6.0,
            fixed_cost=1000.0,
            variable_cost_per_participant=5.0,
            compliance_rate=1.0,
        )
        di = DiscountedIntervention(with_fixed, n_beneficiaries=1000)
        assert di.adjusted_cost == pytest.approx(1.0 + 5.0)

    def test_effectiveness_accounts_for_time_and_cost(self):
        iv = _make_single()
        base = DiscountedIntervention(iv)

        double_duration = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=5.0,
            cost_low=4.0,
            cost_high=6.0,
            fixed_cost=0.0,
            variable_cost_per_participant=5.0,
            compliance_rate=1.0,
            duration_years=2,
            annual_decay_rate=1.0,
        )
        di = DiscountedIntervention(double_duration)
        assert di.effectiveness > base.effectiveness

    def test_ce_display_roundtrip(self):
        iv = _make_single()
        di = DiscountedIntervention(iv)
        assert di.ce_display == pytest.approx(0.1 / di.effectiveness)


class TestDiscountedInterventionSet:
    def test_league_table_sorted(self):
        iset = _make_set()
        diset = DiscountedInterventionSet.from_intervention_set(iset)
        table = diset.league_table()
        eff = table["effectiveness"].values
        assert all(eff[i] >= eff[i + 1] for i in range(len(eff) - 1))

    def test_league_table_has_columns(self):
        iset = _make_set()
        diset = DiscountedInterventionSet.from_intervention_set(iset)
        table = diset.league_table()
        assert set(table.columns) >= {
            "name",
            "discounted_effect",
            "adjusted_cost",
            "effectiveness",
            "ce_display",
        }

    def test_ranking_shift_has_correct_columns(self):
        iset = _make_set()
        diset = DiscountedInterventionSet.from_intervention_set(iset)
        shift = diset.ranking_shift(iset)
        assert set(shift.columns) >= {
            "name",
            "rank_phase1",
            "rank_phase2",
            "rank_shift",
        }

    def test_ecd_improves_with_long_duration(self):
        ecd = Intervention(
            name="ECD",
            effect_sd=0.22,
            effect_se=0.08,
            cost_est=25.0,
            cost_low=20.0,
            cost_high=30.0,
            fixed_cost=0.0,
            variable_cost_per_participant=25.0,
            compliance_rate=1.0,
            duration_years=10,
            annual_decay_rate=0.90,
        )
        cheap = Intervention(
            name="Cheap Short",
            effect_sd=0.05,
            effect_se=0.02,
            cost_est=2.0,
            cost_low=1.6,
            cost_high=2.4,
            fixed_cost=0.0,
            variable_cost_per_participant=2.0,
            compliance_rate=1.0,
            duration_years=1,
            annual_decay_rate=1.0,
        )
        iset = InterventionSet([ecd, cheap])
        diset = DiscountedInterventionSet.from_intervention_set(iset)

        table = diset.league_table()
        assert table.iloc[0]["name"] == "ECD"

    def test_short_duration_interventions_fall(self):
        long_d = Intervention(
            name="Long",
            effect_sd=0.10,
            effect_se=0.03,
            cost_est=5.0,
            cost_low=4.0,
            cost_high=6.0,
            fixed_cost=0.0,
            variable_cost_per_participant=5.0,
            compliance_rate=1.0,
            duration_years=5,
            annual_decay_rate=0.90,
        )
        short = Intervention(
            name="Short",
            effect_sd=0.15,
            effect_se=0.03,
            cost_est=5.0,
            cost_low=4.0,
            cost_high=6.0,
            fixed_cost=0.0,
            variable_cost_per_participant=5.0,
            compliance_rate=1.0,
            duration_years=1,
            annual_decay_rate=1.0,
        )
        iset = InterventionSet([short, long_d])
        diset = DiscountedInterventionSet.from_intervention_set(iset)

        p1_names = list(iset.league_table()["name"])
        assert p1_names[0] == "Short"

        p2_names = list(diset.league_table()["name"])
        assert p2_names[0] == "Long"
