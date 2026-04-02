from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter


ROOT = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
CLEAN = ROOT / "clean"
TABLES = ROOT / "output" / "tables"
FIGS = ROOT / "output" / "figures"


def setup_style() -> None:
    plt.style.use("default")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "axes.edgecolor": "#333333",
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": "#d9d9d9",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.7,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "savefig.bbox": "tight",
            "savefig.dpi": 300,
        }
    )


def pct_formatter(x, _):
    return f"{x:.1f}%"


def load_panel() -> pd.DataFrame:
    return pd.read_csv(CLEAN / "mn_working_paper_analysis_panel_2011_2023.csv")


def save_year_series(panel: pd.DataFrame, column: str, outfile: Path, ylabel: str) -> None:
    series = panel.groupby("year", as_index=False)[column].mean(numeric_only=True)
    fig, ax = plt.subplots(figsize=(5.9, 3.7), constrained_layout=True)
    ax.plot(
        series["year"],
        series[column],
        color="#1f4e79",
        marker="o",
        linewidth=2.2,
        markersize=4.8,
    )
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.set_xticks(series["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.margins(x=0.02)
    if column == "pop_growth_rate":
        ax.yaxis.set_major_formatter(FuncFormatter(pct_formatter))
    fig.savefig(outfile)
    plt.close(fig)


def build_descriptive_figures() -> None:
    panel = load_panel()

    save_year_series(panel, "temp_avg", FIGS / "avg_temp_by_year.png", "Degrees F")
    save_year_series(panel, "pop_growth_rate", FIGS / "avg_pop_growth_by_year.png", "Percent")
    save_year_series(panel, "irs_net_mig_rate", FIGS / "avg_irs_net_mig_rate_by_year.png", "Rate per 1,000")

    county_means = (
        panel.groupby("county_name", as_index=False)[["precip_total", "irs_net_mig_rate"]]
        .mean(numeric_only=True)
        .dropna()
    )
    x = county_means["precip_total"].to_numpy()
    y = county_means["irs_net_mig_rate"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    x_grid = np.linspace(x.min(), x.max(), 200)
    y_grid = slope * x_grid + intercept

    fig, ax = plt.subplots(figsize=(5.9, 3.7), constrained_layout=True)
    ax.scatter(
        x,
        y,
        s=32,
        color="#4c78a8",
        alpha=0.7,
        edgecolor="white",
        linewidth=0.4,
    )
    ax.plot(x_grid, y_grid, color="#8b1e3f", linewidth=2.0)
    ax.set_xlabel("Mean annual precipitation")
    ax.set_ylabel("Mean IRS net migration rate")
    fig.savefig(FIGS / "county_mean_irs_net_mig_vs_precip_lfit.png")
    plt.close(fig)


def build_precip_effect_plot() -> None:
    df = pd.read_csv(TABLES / "working_paper_precip_effects.csv")
    order = [
        "QCEW employment",
        "Permit units",
        "Construction estabs",
        "Construction GDP",
        "Corn yield",
        "Soy yield",
    ]
    labels = {
        "QCEW employment": "Employment",
        "Permit units": "Permit units",
        "Construction estabs": "Construction establishments",
        "Construction GDP": "Construction GDP",
        "Corn yield": "Corn yield",
        "Soy yield": "Soy yield",
    }
    df = df[df["outcome"].isin(order)].copy()
    df["label"] = pd.Categorical(df["outcome"], categories=order, ordered=True)
    df = df.sort_values("label")
    colors = ["#1f4e79", "#1f4e79", "#1f4e79", "#1f4e79", "#5b7f2b", "#5b7f2b"]

    fig, ax = plt.subplots(figsize=(7.1, 4.3), constrained_layout=True)
    ypos = np.arange(len(df))
    ax.axvline(0, color="#8b1e3f", linestyle=(0, (6, 4)), linewidth=1.3)
    for idx, (_, row) in enumerate(df.iterrows()):
        ax.errorbar(
            row["coef"],
            ypos[idx],
            xerr=[[row["coef"] - row["lb"]], [row["ub"] - row["coef"]]],
            fmt="o",
            color=colors[idx],
            ecolor=colors[idx],
            elinewidth=1.6,
            capsize=3,
            markersize=5.5,
        )

    ax.set_yticks(ypos)
    ax.set_yticklabels([labels[x] for x in df["outcome"]])
    ax.set_xlabel("Precipitation coefficient")
    ax.set_ylabel("")
    ax.invert_yaxis()
    ax.set_xlim(df["lb"].min() * 1.08, max(0.00015, df["ub"].max() * 1.25))
    fig.savefig(FIGS / "working_paper_precip_log_outcomes.png")
    plt.close(fig)


def build_nass_persistence_plot() -> None:
    df = pd.read_csv(TABLES / "working_paper_nass_yield_persistence_coeffs.csv")
    spec_order = ["Contemporaneous", "Lag 1", "3-year avg"]
    crops = [("Corn", "#1f4e79"), ("Soy", "#5b7f2b")]

    xmin = df["lb"].min() * 1.08
    xmax = max(0.00006, df["ub"].max() * 1.25)

    fig, axes = plt.subplots(
        1, 2, figsize=(7.4, 3.9), sharex=True, sharey=True, constrained_layout=True
    )
    xticks = [-0.0010, -0.0005, 0.0]
    for ax, (crop, color) in zip(axes, crops):
        sub = df[df["crop"] == crop].copy()
        sub["spec"] = pd.Categorical(sub["spec"], categories=spec_order, ordered=True)
        sub = sub.sort_values("spec")
        ypos = np.arange(len(sub))
        ax.axvline(0, color="#8b1e3f", linestyle=(0, (6, 4)), linewidth=1.2)
        for idx, (_, row) in enumerate(sub.iterrows()):
            ax.errorbar(
                row["coef"],
                ypos[idx],
                xerr=[[row["coef"] - row["lb"]], [row["ub"] - row["coef"]]],
                fmt="o",
                color=color,
                ecolor=color,
                elinewidth=1.5,
                capsize=3,
                markersize=5.5,
            )
        ax.set_title("Soybeans" if crop == "Soy" else crop)
        ax.set_yticks(ypos)
        ax.set_yticklabels(spec_order)
        ax.set_xlim(xmin, xmax)
        ax.set_xticks(xticks)
        ax.invert_yaxis()

    fig.supxlabel("Precipitation coefficient")
    fig.savefig(FIGS / "working_paper_nass_yield_persistence.png")
    plt.close(fig)


def main() -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    setup_style()
    build_descriptive_figures()
    build_precip_effect_plot()
    build_nass_persistence_plot()


if __name__ == "__main__":
    main()
