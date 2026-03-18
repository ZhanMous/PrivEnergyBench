from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path("/home/yanshi")
OUT_DIR = ROOT / "PrivEnergyBench/docs/redrawn_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EMB_CSV = ROOT / "EmbodiedSNNPrototype/outputs/plasticity_compare_retuned_v3/benchmark_runs.csv"
NEURO_BASELINE = ROOT / "Neuro-Symbiosis/outputs/quick/benchmark/baseline_summary.csv"
NEURO_COUPLING = ROOT / "Neuro-Symbiosis/outputs/coupling/coupling_data.csv"
NEURO_DP = ROOT / "Neuro-Symbiosis/outputs/quick/dp_sweep/dp_sweep_summary.csv"
MED_TRAIN = ROOT / "MedSparseSNN/outputs/csv/training_summary_dermamnist_final_compare.csv"
MED_MIA = ROOT / "MedSparseSNN/outputs/csv/mia_results_dermamnist_final_compare.csv"
PE_AGG = ROOT / "PrivEnergyBench/outputs/default/aggregate_summary.csv"

plt.rcParams.update(
    {
        "font.size": 14,
        "axes.titlesize": 20,
        "axes.labelsize": 16,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
        "legend.fontsize": 12,
        "figure.dpi": 180,
    }
)

MODE_COLORS = {
    "structured": "#3B82F6",
    "fixed_readout": "#8B5CF6",
    "plastic_readout": "#059669",
    "plastic": "#059669",
}


def _save(fig, name: str):
    fig.tight_layout()
    path = OUT_DIR / name
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return path


def _parse_pm(value: str) -> tuple[float, float]:
    s = str(value).strip()
    m = re.match(r"\s*([0-9]*\.?[0-9]+)\s*±\s*([0-9]*\.?[0-9]+)", s)
    if m:
        return float(m.group(1)), float(m.group(2))
    try:
        return float(s), 0.0
    except ValueError:
        return np.nan, np.nan


def draw_embodied():
    df = pd.read_csv(EMB_CSV)

    mode_stats = (
        df.groupby("mode", as_index=False)
        .agg(
            objective_mean=("objective", "mean"),
            objective_std=("objective", "std"),
            food_mean=("food_eaten", "mean"),
            energy_mean=("energy_proxy", "mean"),
        )
        .fillna(0.0)
    )

    fig, ax = plt.subplots(figsize=(12, 7))
    x = np.arange(len(mode_stats))
    colors = [MODE_COLORS.get(m, "#334155") for m in mode_stats["mode"]]
    ax.bar(x, mode_stats["objective_mean"], yerr=mode_stats["objective_std"], capsize=6, color=colors)
    ax.set_xticks(x)
    ax.set_xticklabels(mode_stats["mode"], rotation=10)
    ax.set_ylabel("objective (mean)")
    ax.set_title("EmbodiedSNN: Objective by Mode (mean ± std)")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, "emb_objective_by_mode_redraw.png")

    fig, ax = plt.subplots(figsize=(12, 7))
    for _, row in mode_stats.iterrows():
        mode = row["mode"]
        ax.scatter(
            row["energy_mean"],
            row["food_mean"],
            s=230,
            color=MODE_COLORS.get(mode, "#334155"),
            edgecolor="white",
            linewidth=1.2,
            label=mode,
        )
        ax.text(row["energy_mean"] * 1.002, row["food_mean"] * 1.002, mode, fontsize=12)
    ax.set_xlabel("energy_proxy (lower is better)")
    ax.set_ylabel("food_eaten (higher is better)")
    ax.set_title("EmbodiedSNN: Reward-Cost Trade-off")
    ax.grid(alpha=0.25)
    ax.legend(loc="best")
    _save(fig, "emb_food_vs_energy_redraw.png")

    heat = (
        df.groupby(["hunger_drive", "neural_noise_std"], as_index=False)["food_eaten"]
        .mean()
        .pivot(index="hunger_drive", columns="neural_noise_std", values="food_eaten")
        .sort_index()
    )
    fig, ax = plt.subplots(figsize=(12, 7))
    im = ax.imshow(heat.values, aspect="auto", cmap="YlGnBu")
    ax.set_xticks(np.arange(len(heat.columns)))
    ax.set_xticklabels([f"{c:.2f}" for c in heat.columns])
    ax.set_yticks(np.arange(len(heat.index)))
    ax.set_yticklabels([f"{i:.2f}" for i in heat.index])
    ax.set_xlabel("neural_noise_std")
    ax.set_ylabel("hunger_drive")
    ax.set_title("EmbodiedSNN: Mean Food Eaten Heatmap")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("food_eaten")
    _save(fig, "emb_food_heatmap_redraw.png")

    focus = mode_stats[mode_stats["mode"].isin(["structured", "fixed_readout", "plastic_readout", "plastic"])]
    if not focus.empty:
        fig, ax = plt.subplots(figsize=(12, 7))
        x = np.arange(len(focus))
        ax.bar(
            x,
            focus["objective_mean"],
            yerr=focus["objective_std"],
            capsize=6,
            color=[MODE_COLORS.get(m, "#334155") for m in focus["mode"]],
        )
        ax.set_xticks(x)
        ax.set_xticklabels(focus["mode"], rotation=8)
        ax.set_ylabel("objective (mean)")
        ax.set_title("EmbodiedSNN: Fixed vs Plastic Readout")
        ax.grid(axis="y", alpha=0.25)
        _save(fig, "emb_fixed_vs_plastic_redraw.png")


def draw_neuro():
    baseline = pd.read_csv(NEURO_BASELINE)
    fig, ax = plt.subplots(figsize=(12, 7))
    cmap = {"snn": "#0EA5E9", "transformer": "#F59E0B", "hybrid": "#10B981"}
    for _, row in baseline.iterrows():
        model = row["model"]
        x = row["energy_mj"]
        y = row["val_acc"]
        privacy = 1.0 - row["mia_auc"]
        ax.scatter(x, y, s=260, color=cmap.get(model, "#334155"), edgecolor="white", linewidth=1.2)
        ax.text(x * 1.01, y + 0.0015, f"{model} (1-AUC={privacy:.3f})", fontsize=12)
    ax.set_xlabel("energy_mj")
    ax.set_ylabel("val_acc")
    ax.set_title("Neuro-Symbiosis: Baseline Pareto View")
    ax.grid(alpha=0.25)
    _save(fig, "neuro_baseline_pareto_redraw.png")

    coupling = pd.read_csv(NEURO_COUPLING)
    fig, ax = plt.subplots(figsize=(12, 7))
    sc = ax.scatter(
        coupling["threshold"],
        coupling["beta"],
        c=coupling["energy_mj"],
        s=120,
        cmap="viridis",
        alpha=0.9,
        edgecolor="white",
        linewidth=0.4,
    )
    ax.set_xlabel("threshold")
    ax.set_ylabel("beta")
    ax.set_title("Neuro Coupling: Energy Landscape")
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("energy_mj")
    _save(fig, "neuro_coupling_energy_landscape_redraw.png")

    fig, ax = plt.subplots(figsize=(12, 7))
    for beta, sub in coupling.groupby("beta"):
        sorted_sub = sub.sort_values("threshold")
        ax.plot(sorted_sub["threshold"], sorted_sub["energy_mj"], marker="o", linewidth=2.2, label=f"beta={beta}")
    ax.set_xlabel("threshold")
    ax.set_ylabel("energy_mj")
    ax.set_title("Neuro Coupling: Threshold vs Energy by Beta")
    ax.grid(alpha=0.25)
    ax.legend(ncol=3, fontsize=10)
    _save(fig, "neuro_coupling_threshold_energy_lines_redraw.png")

    dp = pd.read_csv(NEURO_DP)
    fig, ax1 = plt.subplots(figsize=(12, 7))
    dp_sorted = dp.sort_values("epsilon")
    l1 = ax1.plot(dp_sorted["epsilon"], dp_sorted["val_acc"], color="#0EA5E9", marker="o", linewidth=2.4, label="val_acc")
    ax1.set_xlabel("epsilon")
    ax1.set_ylabel("val_acc", color="#0EA5E9")
    ax1.tick_params(axis="y", labelcolor="#0EA5E9")
    ax2 = ax1.twinx()
    l2 = ax2.plot(dp_sorted["epsilon"], dp_sorted["energy_mj"], color="#F59E0B", marker="s", linewidth=2.2, label="energy_mj")
    ax2.set_ylabel("energy_mj", color="#F59E0B")
    ax2.tick_params(axis="y", labelcolor="#F59E0B")
    ax1.set_title("Neuro DP Sweep: Accuracy-Energy vs Privacy Budget")
    lines = l1 + l2
    labels = [ln.get_label() for ln in lines]
    ax1.legend(lines, labels, loc="best")
    _save(fig, "neuro_dp_tradeoff_redraw.png")


def _split_pm_col(df: pd.DataFrame, col: str, out_mean: str, out_std: str):
    means = []
    stds = []
    for v in df[col].astype(str):
        m, s = _parse_pm(v)
        means.append(m)
        stds.append(s)
    df[out_mean] = means
    df[out_std] = stds


def draw_med():
    train = pd.read_csv(MED_TRAIN)
    _split_pm_col(train, "val_acc", "val_acc_mean", "val_acc_std")
    _split_pm_col(train, "test_acc", "test_acc_mean", "test_acc_std")
    _split_pm_col(train, "power", "power_mean", "power_std")
    _split_pm_col(train, "latency", "latency_mean", "latency_std")

    x = np.arange(len(train))
    width = 0.38
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(x - width / 2, train["val_acc_mean"], width, yerr=train["val_acc_std"], capsize=6, label="val_acc", color="#0EA5E9")
    ax.bar(x + width / 2, train["test_acc_mean"], width, yerr=train["test_acc_std"], capsize=6, label="test_acc", color="#10B981")
    ax.set_xticks(x)
    ax.set_xticklabels(train["model"])
    ax.set_ylabel("accuracy (%)")
    ax.set_title("MedSparseSNN: Validation/Test Accuracy")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    _save(fig, "med_performance_redraw.png")

    fig, ax = plt.subplots(figsize=(12, 7))
    for _, row in train.iterrows():
        ax.scatter(
            row["latency_mean"],
            row["power_mean"],
            s=260,
            edgecolor="white",
            linewidth=1.2,
            label=row["model"],
        )
        ax.text(row["latency_mean"] + 0.004, row["power_mean"] + 0.25, row["model"], fontsize=12)
    ax.set_xlabel("latency (ms/sample)")
    ax.set_ylabel("power (W)")
    ax.set_title("MedSparseSNN: Power-Latency Trade-off")
    ax.grid(alpha=0.25)
    _save(fig, "med_power_latency_redraw.png")

    mia = pd.read_csv(MED_MIA)
    _split_pm_col(mia, "auc", "auc_mean", "auc_std")
    _split_pm_col(mia, "accuracy", "acc_mean", "acc_std")
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(mia["model"], mia["auc_mean"], yerr=mia["auc_std"], capsize=6, color=["#0EA5E9", "#8B5CF6", "#F59E0B"])
    ax.set_ylim(0.45, 0.52)
    ax.set_ylabel("MIA AUC")
    ax.set_title("MedSparseSNN: Membership Inference AUC")
    ax.grid(axis="y", alpha=0.25)
    _save(fig, "med_mia_auc_redraw.png")

    fig, ax = plt.subplots(figsize=(12, 7))
    width = 0.38
    x = np.arange(len(mia))
    ax.bar(x - width / 2, mia["auc_mean"], width, yerr=mia["auc_std"], capsize=6, color="#14B8A6", label="MIA AUC")
    ax.bar(x + width / 2, mia["acc_mean"], width, yerr=mia["acc_std"], capsize=6, color="#F97316", label="MIA Accuracy")
    ax.set_xticks(x)
    ax.set_xticklabels(mia["model"])
    ax.set_ylim(0.45, 0.55)
    ax.set_ylabel("attack metric")
    ax.set_title("MedSparseSNN: MIA AUC vs Attack Accuracy")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    _save(fig, "med_mia_auc_accuracy_redraw.png")

    fig, ax = plt.subplots(figsize=(12, 7))
    scatter = ax.scatter(train["latency_mean"], train["test_acc_mean"], c=train["power_mean"], s=300, cmap="plasma", edgecolor="white", linewidth=1.2)
    for _, row in train.iterrows():
        ax.text(row["latency_mean"] + 0.003, row["test_acc_mean"] + 0.15, row["model"], fontsize=12)
    ax.set_xlabel("latency (ms/sample)")
    ax.set_ylabel("test_acc (%)")
    ax.set_title("MedSparseSNN: Accuracy-Latency with Power Coloring")
    ax.grid(alpha=0.25)
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("power (W)")
    _save(fig, "med_cross_tradeoff_redraw.png")


def draw_privenergy():
    agg = pd.read_csv(PE_AGG)
    fig, ax = plt.subplots(figsize=(12, 7))
    for _, row in agg.iterrows():
        model = row["model"]
        x = row["energy_mj_mean"]
        y = row["val_acc_mean"]
        risk = row["mia_auc_mean"]
        ax.scatter(x, y, s=280, edgecolor="white", linewidth=1.2)
        ax.text(x * 1.01, y + 0.0015, f"{model} (AUC={risk:.3f})", fontsize=12)
    ax.set_xlabel("energy_mj_mean")
    ax.set_ylabel("val_acc_mean")
    ax.set_title("PrivEnergyBench: Pareto Frontier (Aggregated)")
    ax.grid(alpha=0.25)
    _save(fig, "privenergy_pareto_redraw.png")


def main():
    draw_embodied()
    draw_neuro()
    draw_med()
    draw_privenergy()
    print(f"saved figures to: {OUT_DIR}")


if __name__ == "__main__":
    main()
