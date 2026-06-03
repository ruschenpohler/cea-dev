import pandas as pd
import pytest

from cea_dev.core import Intervention, InterventionSet


def _make_interventions() -> list[Intervention]:
    return [
        Intervention(
            name="A",
            effect_sd=0.20,
            effect_se=0.05,
            cost_est=5.0,
            cost_low=4.0,
            cost_high=6.0,
        ),
        Intervention(
            name="B",
            effect_sd=0.10,
            effect_se=0.03,
            cost_est=2.0,
            cost_low=1.6,
            cost_high=2.4,
        ),
        Intervention(
            name="C",
            effect_sd=0.05,
            effect_se=0.02,
            cost_est=1.0,
            cost_low=0.8,
            cost_high=1.2,
        ),
    ]


class TestIntervention:
    def test_effectiveness_is_sd_per_dollar(self):
        iv = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=2.0,
            cost_low=1.6,
            cost_high=2.4,
        )
        assert iv.effectiveness == pytest.approx(0.05)

    def test_ce_display_inverts_and_scales(self):
        iv = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=2.0,
            cost_low=1.6,
            cost_high=2.4,
        )
        assert iv.ce_display == pytest.approx(2.0)

    def test_ce_display_roundtrip(self):
        iv = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=2.0,
            cost_low=1.6,
            cost_high=2.4,
        )
        assert iv.ce_display == pytest.approx(0.1 / iv.effectiveness)

    def test_higher_cost_worsens_ce(self):
        cheap = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=1.0,
            cost_low=0.8,
            cost_high=1.2,
        )
        expensive = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=2.0,
            cost_low=1.6,
            cost_high=2.4,
        )
        assert cheap.effectiveness > expensive.effectiveness

    def test_larger_effect_improves_ce(self):
        small = Intervention(
            name="X",
            effect_sd=0.05,
            effect_se=0.02,
            cost_est=1.0,
            cost_low=0.8,
            cost_high=1.2,
        )
        large = Intervention(
            name="X",
            effect_sd=0.20,
            effect_se=0.02,
            cost_est=1.0,
            cost_low=0.8,
            cost_high=1.2,
        )
        assert large.effectiveness > small.effectiveness

    def test_compliance_invariance_under_proportional_costs(self):
        a = Intervention(
            name="A",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=2.0,
            cost_low=1.6,
            cost_high=2.4,
            fixed_cost=0.0,
            compliance_rate=1.0,
        )
        b = Intervention(
            name="A",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=2.0,
            cost_low=1.6,
            cost_high=2.4,
            fixed_cost=0.0,
            compliance_rate=0.80,
        )
        assert a.effectiveness == pytest.approx(b.effectiveness)

    def test_default_fields(self):
        iv = Intervention(
            name="X",
            effect_sd=0.10,
            effect_se=0.02,
            cost_est=1.0,
            cost_low=0.8,
            cost_high=1.2,
        )
        assert iv.fixed_cost == 0.0
        assert iv.compliance_rate == 1.0
        assert iv.duration_years == 1
        assert iv.annual_decay_rate == 1.0
        assert iv.discount_rate == 0.03


class TestInterventionSet:
    def test_league_table_sorted_by_effectiveness(self):
        interventions = _make_interventions()
        iset = InterventionSet(interventions)
        table = iset.league_table()
        eff = table["effectiveness"].values
        assert all(eff[i] >= eff[i + 1] for i in range(len(eff) - 1))

    def test_league_table_has_expected_columns(self):
        interventions = _make_interventions()
        iset = InterventionSet(interventions)
        table = iset.league_table()
        assert set(table.columns) >= {
            "name",
            "effect_sd",
            "cost_est",
            "effectiveness",
            "ce_display",
        }

    def test_league_table_rank_starts_at_one(self):
        interventions = _make_interventions()
        iset = InterventionSet(interventions)
        table = iset.league_table()
        assert table.index.name == "rank"
        assert table.index[0] == 1

    def test_roundtrip_from_csv(self, tmp_path):
        interventions = _make_interventions()
        source = InterventionSet(interventions)
        table_before = source.league_table()

        csv_path = tmp_path / "test_interventions.csv"
        df = pd.DataFrame([vars(iv) for iv in interventions])
        df["name"] = df["name"].astype(str)
        df.to_csv(csv_path, index=False)

        loaded = InterventionSet.from_csv(str(csv_path))
        table_after = loaded.league_table()

        pd.testing.assert_frame_equal(
            table_before.reset_index(drop=True),
            table_after.reset_index(drop=True),
        )

    def test_ranking_invariant_to_cost_scaling(self):
        base = _make_interventions()
        iset_base = InterventionSet(base)
        ranks_base = list(iset_base.league_table()["name"])

        factor = 2.5
        scaled = [
            Intervention(
                name=iv.name,
                effect_sd=iv.effect_sd,
                effect_se=iv.effect_se,
                cost_est=iv.cost_est * factor,
                cost_low=iv.cost_low * factor,
                cost_high=iv.cost_high * factor,
            )
            for iv in base
        ]
        iset_scaled = InterventionSet(scaled)
        ranks_scaled = list(iset_scaled.league_table()["name"])

        assert ranks_base == ranks_scaled

    def test_from_csv_missing_columns_raises(self, tmp_path):
        df = pd.DataFrame({"name": ["X"], "effect_sd": [0.1]})
        path = tmp_path / "bad.csv"
        df.to_csv(path, index=False)
        with pytest.raises(ValueError, match="Missing required columns"):
            InterventionSet.from_csv(str(path))
