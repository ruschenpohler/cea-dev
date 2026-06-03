from dataclasses import MISSING, dataclass, fields

import pandas as pd


@dataclass
class Intervention:
    name: str
    effect_sd: float  # ASSUMPTION A0: effect is known
    effect_se: float
    cost_est: float
    cost_low: float
    cost_high: float
    cost_imputed: bool = False
    fixed_cost: float = 0.0  # ASSUMPTION A1: proportional costs (no fixed)
    variable_cost_per_participant: float = 0.0
    compliance_rate: float = 1.0
    n_studies: int = 1
    duration_years: int = 1  # ASSUMPTION A2: default 1-year horizon
    annual_decay_rate: float = 1.0  # ASSUMPTION A3: no decay by default
    discount_rate: float = 0.03

    @property
    def effectiveness(self) -> float:
        r"""SD per dollar (internal metric). $v_i = \hat{\tau}_i / C_i$"""
        return self.effect_sd / self.cost_est

    @property
    def ce_display(self) -> float:
        r"""Cost per 0.1 SD (display metric). $CE_i^* = 0.1 / v_i$"""
        return 0.1 / self.effectiveness


@dataclass
class InterventionSet:
    interventions: list[Intervention]

    def league_table(self) -> pd.DataFrame:
        df = pd.DataFrame(
            [
                {
                    "name": iv.name,
                    "effect_sd": iv.effect_sd,
                    "cost_est": iv.cost_est,
                    "effectiveness": iv.effectiveness,
                    "ce_display": iv.ce_display,
                }
                for iv in self.interventions
            ]
        )
        df = df.sort_values("effectiveness", ascending=False).reset_index(drop=True)
        df.index = df.index + 1
        df.index.name = "rank"
        return df

    @classmethod
    def from_csv(cls, path: str) -> "InterventionSet":
        df = pd.read_csv(path)
        required = {
            "name",
            "effect_sd",
            "effect_se",
            "cost_est",
            "cost_low",
            "cost_high",
        }
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns in CSV: {missing}")

        interventions = []
        for _, row in df.iterrows():
            kwargs = {
                col: row[col] for col in df.columns if col in _INTERVENTION_FIELDS
            }
            for field_name, field_default in _INTERVENTION_DEFAULTS.items():
                if field_name not in kwargs:
                    kwargs[field_name] = field_default
            interventions.append(Intervention(**kwargs))
        return cls(interventions)


_INTERVENTION_FIELDS = {f.name for f in fields(Intervention) if f.init}

_INTERVENTION_DEFAULTS = {
    f.name: f.default for f in fields(Intervention) if f.default is not MISSING
}
