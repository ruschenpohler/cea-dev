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


def plot_ranking_shift(
    shift_df: pd.DataFrame,
    figsize: tuple[float, float] = (14, 5),
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    df = shift_df.copy()
    n = len(df)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, sharey=True)

    y_positions = list(reversed(range(n)))
    names = list(reversed(df["name"].values))
    ce_p1 = list(reversed(df["ce_display_p1"].values))
    ce_p2 = list(reversed(df["ce_display_p2"].values))

    quartile_idx = pd.cut(np.arange(n), bins=4, labels=False)
    colors = [_QUARTILE_COLORS[int(q)] for q in quartile_idx]

    bars1 = ax1.barh(y_positions, ce_p1, color=colors, edgecolor="white")
    ax1.set_yticks(y_positions)
    ax1.set_yticklabels(names)
    ax1.set_xlabel("Cost per 0.1 SD (USD)")
    ax1.set_xscale("log")
    ax1.set_title("Phase 1 — Unadjusted")
    ax1.invert_yaxis()
    for bar, value in zip(bars1, ce_p1):
        ax1.text(
            value * 1.02,
            bar.get_y() + bar.get_height() / 2,
            f"${value:.2f}",
            va="center",
            fontsize=8,
        )

    bars2 = ax2.barh(y_positions, ce_p2, color=colors, edgecolor="white")
    ax2.set_xlabel("Cost per 0.1 SD (USD)")
    ax2.set_xscale("log")
    ax2.set_title("Phase 2 — Time-Adjusted")
    ax2.invert_yaxis()
    for bar, value in zip(bars2, ce_p2):
        ax2.text(
            value * 1.02,
            bar.get_y() + bar.get_height() / 2,
            f"${value:.2f}",
            va="center",
            fontsize=8,
        )

    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, color=c, label=label)
        for c, label in zip(_QUARTILE_COLORS, _QUARTILE_LABELS)
    ]
    ax1.legend(handles=legend_handles, loc="lower right", fontsize=7)

    fig.suptitle(
        "League Table: Before vs. After Time Adjustment", fontsize=13, fontweight="bold"
    )
    sns.despine()
    fig.tight_layout()
    return fig, (ax1, ax2)
