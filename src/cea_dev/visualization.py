import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

_QUARTILE_LABELS = ["Best Buy", "Good Buy", "Promising", "Weak"]
_QUARTILE_COLORS = ["#0072B2", "#56B4E9", "#E69F00", "#D55E00"]


def plot_league_table(
    league: pd.DataFrame,
    title: str = "Cost-Effectiveness League Table",
    figsize: tuple[float, float] = (9, 5),
) -> tuple[plt.Figure, plt.Axes]:
    df = league.copy()
    n = len(df)

    quartile_idx = pd.cut(
        np.arange(n),
        bins=4,
        labels=False,
    )
    bar_colors = [_QUARTILE_COLORS[int(q)] for q in quartile_idx]

    y_positions = list(reversed(range(n)))
    names = list(reversed(df["name"].values))
    ce_values = list(reversed(df["ce_display"].values))

    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.barh(y_positions, ce_values, color=bar_colors, edgecolor="white")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(names)
    ax.set_xlabel("Cost per 0.1 SD (USD, log scale)")
    ax.set_xscale("log")
    ax.set_title(title)
    ax.invert_yaxis()

    for i, (bar, value) in enumerate(zip(bars, ce_values)):
        ax.text(
            value * 1.02,
            bar.get_y() + bar.get_height() / 2,
            f"${value:.2f}",
            va="center",
            fontsize=9,
        )

    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, color=c, label=label)
        for c, label in zip(_QUARTILE_COLORS, _QUARTILE_LABELS)
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=8)

    sns.despine()
    fig.tight_layout()
    return fig, ax
