"""Generate synthetic data for the CEA worked example.

Produces two files deterministically with seed 42:
  - data/interventions.csv: 8 education interventions with parameter estimates
  - data/simulated_unit_data.csv: TaRL RCT unit-level data (N=500)
"""

from pathlib import Path

import numpy as np
import pandas as pd

_SEED = 42
_ROOT = Path(__file__).resolve().parent.parent.parent
_OUT_DIR = _ROOT / "data"


def generate_interventions_csv() -> None:
    interventions = [
        {
            "name": "Teaching at the Right Level (TaRL)",
            "effect_sd": 0.18,
            "effect_se": 0.06,
            "cost_est": 4.00,
            "cost_low": 3.20,
            "cost_high": 4.80,
            "cost_imputed": True,
            "fixed_cost": 500,
            "variable_cost_per_participant": 3.60,
            "compliance_rate": 0.85,
            "n_studies": 4,
            "duration_years": 2,
            "annual_decay_rate": 0.80,
            "discount_rate": 0.03,
        },
        {
            "name": "Structured pedagogy",
            "effect_sd": 0.12,
            "effect_se": 0.05,
            "cost_est": 8.00,
            "cost_low": 6.40,
            "cost_high": 9.60,
            "cost_imputed": True,
            "fixed_cost": 1200,
            "variable_cost_per_participant": 7.20,
            "compliance_rate": 0.90,
            "n_studies": 3,
            "duration_years": 2,
            "annual_decay_rate": 0.75,
            "discount_rate": 0.03,
        },
        {
            "name": "Computer-assisted learning (CAL)",
            "effect_sd": 0.14,
            "effect_se": 0.07,
            "cost_est": 12.00,
            "cost_low": 9.60,
            "cost_high": 14.40,
            "cost_imputed": True,
            "fixed_cost": 3000,
            "variable_cost_per_participant": 9.00,
            "compliance_rate": 0.75,
            "n_studies": 2,
            "duration_years": 3,
            "annual_decay_rate": 0.70,
            "discount_rate": 0.03,
        },
        {
            "name": "School meals",
            "effect_sd": 0.09,
            "effect_se": 0.04,
            "cost_est": 15.00,
            "cost_low": 12.00,
            "cost_high": 18.00,
            "cost_imputed": True,
            "fixed_cost": 800,
            "variable_cost_per_participant": 14.50,
            "compliance_rate": 0.95,
            "n_studies": 5,
            "duration_years": 1,
            "annual_decay_rate": 0.50,
            "discount_rate": 0.03,
        },
        {
            "name": "Early childhood development (ECD)",
            "effect_sd": 0.22,
            "effect_se": 0.08,
            "cost_est": 25.00,
            "cost_low": 20.00,
            "cost_high": 30.00,
            "cost_imputed": True,
            "fixed_cost": 2000,
            "variable_cost_per_participant": 22.00,
            "compliance_rate": 0.80,
            "n_studies": 3,
            "duration_years": 10,
            "annual_decay_rate": 0.90,
            "discount_rate": 0.03,
        },
        {
            "name": "Teacher performance pay",
            "effect_sd": 0.10,
            "effect_se": 0.06,
            "cost_est": 18.00,
            "cost_low": 14.40,
            "cost_high": 21.60,
            "cost_imputed": True,
            "fixed_cost": 5000,
            "variable_cost_per_participant": 17.00,
            "compliance_rate": 1.00,
            "n_studies": 2,
            "duration_years": 2,
            "annual_decay_rate": 0.65,
            "discount_rate": 0.03,
        },
        {
            "name": "Conditional cash transfer (CCT)",
            "effect_sd": 0.07,
            "effect_se": 0.03,
            "cost_est": 22.00,
            "cost_low": 17.60,
            "cost_high": 26.40,
            "cost_imputed": True,
            "fixed_cost": 1500,
            "variable_cost_per_participant": 19.00,
            "compliance_rate": 0.70,
            "n_studies": 6,
            "duration_years": 3,
            "annual_decay_rate": 0.60,
            "discount_rate": 0.03,
        },
        {
            "name": "Deworming",
            "effect_sd": 0.05,
            "effect_se": 0.04,
            "cost_est": 2.00,
            "cost_low": 1.60,
            "cost_high": 2.40,
            "cost_imputed": True,
            "fixed_cost": 300,
            "variable_cost_per_participant": 1.80,
            "compliance_rate": 0.95,
            "n_studies": 3,
            "duration_years": 1,
            "annual_decay_rate": 0.40,
            "discount_rate": 0.03,
        },
    ]

    columns = [
        "name",
        "effect_sd",
        "effect_se",
        "cost_est",
        "cost_low",
        "cost_high",
        "cost_imputed",
        "fixed_cost",
        "variable_cost_per_participant",
        "compliance_rate",
        "n_studies",
        "duration_years",
        "annual_decay_rate",
        "discount_rate",
    ]
    df = pd.DataFrame(interventions, columns=columns)
    path = _OUT_DIR / "interventions.csv"
    df.to_csv(path, index=False)
    print(f"Wrote {path}")


def generate_simulated_unit_data_csv() -> None:
    rng = np.random.default_rng(_SEED)
    n_treatment = 250
    n_control = 250
    n_total = n_treatment + n_control

    treatment = np.concatenate(
        [np.ones(n_treatment, dtype=int), np.zeros(n_control, dtype=int)]
    )
    baseline_mean = 50
    baseline_sd = 15
    effect_score = 2.7  # 0.18 SD * 15

    baseline = rng.normal(baseline_mean, baseline_sd, n_total)
    noise = rng.normal(0, baseline_sd, n_total)
    endline = baseline + treatment * effect_score + noise

    df = pd.DataFrame(
        {
            "student_id": np.arange(1, n_total + 1),
            "treatment": treatment,
            "baseline_score": np.round(baseline, 2),
            "endline_score": np.round(endline, 2),
        }
    )
    path = _OUT_DIR / "simulated_unit_data.csv"
    df.to_csv(path, index=False)
    print(f"Wrote {path}")


if __name__ == "__main__":
    generate_interventions_csv()
    generate_simulated_unit_data_csv()
