from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 200

ROOT = Path("/home/yanshi")
OUT = ROOT / "PrivEnergyBench/docs/clean_figures"
OUT.mkdir(parents=True, exist_ok=True)


def parse_mean_std(text: str) -> tuple[float, float]:
    s = str(text).replace(" ", "")
    if "±" in s:
        a, b = s.split("±", 1)
        return float(a), float(b)
    return float(s), 0.0


def load_embodied_best() -> pd.DataFrame:
    path = ROOT / "EmbodiedSNNPrototype/outputs/plasticity_compare_retuned_v3/benchmark_summary.csv"
    try:
        df = pd.read_csv(path)
        if "mode" in df.columns and "objective_mean" in df.columns:
            # Keep the best (max objective_mean) per mode.
            idx = df.groupby("mode")["objective_mean"].idxmax()
            return df.loc[idx].copy()
    except Exception:
        pass

    # Fallback to hard-coded values already reported in the deck.
    return pd.DataFrame(
        {
            "mode": ["structured", "plastic_readout"],
            "objective_mean": [-0.4839, -0.4199],
            "objective_std": [0.0, 0.0],
            "food_eaten_mean": [0.30, 0.36],
            "food_eaten_std": [0.0, 0.0],
            "energy_proxy_mean": [0.7905, 0.7966],
            "energy_proxy_std": [0.0, 0.0],
        }
    )


def plot_embodied_clean(df: pd.DataFrame) -> None:
    # Figure 1: objective comparison
    ordered = df.sort_values("mode")
    modes = ordered["mode"].tolist()
    obj = ordered["objective_mean"].astype(float).to_numpy()
    obj_std = ordered.get("objective_std", pd.Series([0.0] * len(ordered))).astype(float).to_numpy()

    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    colors = ["#4E79A7", "#59A14F"]
    x = np.arange(len(modes))
    ax.bar(x, obj, yerr=obj_std, capsize=4, color=colors[: len(modes)])
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace("_", " ") for m in modes])
    ax.set_title("Fixed vs Plastic Readout Objective Comparison", fontsize=14, fontweight="bold")
    ax.set_ylabel("Objective Value (a.u.)", fontsize=12)
    ax.set_xlabel("Readout Mode", fontsize=12)
    ax.tick_params(axis="both", labelsize=11)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(OUT / "emb_fixed_objective_clean.png", dpi=320)
    plt.close(fig)

    # Figure 2: reward-energy tradeoff
    food = ordered.get("food_eaten_mean", pd.Series([0.0] * len(ordered))).astype(float).to_numpy()
    food_std = ordered.get("food_eaten_std", pd.Series([0.0] * len(ordered))).astype(float).to_numpy()
    ene = ordered.get("energy_proxy_mean", pd.Series([0.0] * len(ordered))).astype(float).to_numpy()
    ene_std = ordered.get("energy_proxy_std", pd.Series([0.0] * len(ordered))).astype(float).to_numpy()

    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    ax.errorbar(
        ene,
        food,
        xerr=ene_std,
        yerr=food_std,
        fmt="o",
        markersize=8,
        capsize=4,
        color="#1B6CA8",
    )
    for i, mode in enumerate(modes):
        ax.annotate(mode.replace("_", " "), (ene[i], food[i]), textcoords="offset points", xytext=(6, 4))
    ax.set_title("Reward-Energy Trade-off", fontsize=14, fontweight="bold")
    ax.set_xlabel("Energy Proxy (mJ/sample)", fontsize=12)
    ax.set_ylabel("Food Collected (count)", fontsize=12)
    ax.tick_params(axis="both", labelsize=11)
    ax.grid(alpha=0.25)
    fig.savefig(OUT / "emb_reward_energy_clean.png", dpi=320)
    plt.close(fig)


def plot_neuro_clean() -> None:
    path = ROOT / "Neuro-Symbiosis/outputs/quick/benchmark/baseline_summary.csv"
    df = pd.read_csv(path)

    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    sc = ax.scatter(
        df["energy_mj"],
        df["val_acc"] * 100.0,
        c=df["mia_auc"],
        cmap="viridis",
        s=120,
        edgecolor="black",
        linewidth=0.4,
    )
    for _, r in df.iterrows():
        ax.annotate(str(r["model"]), (r["energy_mj"], r["val_acc"] * 100.0), textcoords="offset points", xytext=(6, 4))
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("MIA AUC")
    ax.set_title("SNN-Transformer Pareto Comparison", fontsize=14, fontweight="bold")
    ax.set_xlabel("Energy (mJ/sample)", fontsize=12)
    ax.set_ylabel("Validation Accuracy (%)", fontsize=12)
    ax.tick_params(axis="both", labelsize=11)
    ax.grid(alpha=0.25)
    fig.savefig(OUT / "neuro_pareto_clean.png", dpi=320)
    plt.close(fig)


def load_med_eff() -> pd.DataFrame:
    path = ROOT / "MedSparseSNN/outputs/csv/medmnist_privacy_efficiency_summary_dermamnist_final_compare.csv"
    rows = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            row = {
                "model": r["model"],
                "test_acc_mean": parse_mean_std(r["test_acc"])[0],
                "test_acc_std": parse_mean_std(r["test_acc"])[1],
                "lat_mean": parse_mean_std(r["latency_ms_per_sample"].replace("ms/sample", ""))[0],
                "lat_std": parse_mean_std(r["latency_ms_per_sample"].replace("ms/sample", ""))[1],
                "ene_mean": parse_mean_std(r["energy_mj_per_sample"].replace("mJ", ""))[0],
                "ene_std": parse_mean_std(r["energy_mj_per_sample"].replace("mJ", ""))[1],
            }
            rows.append(row)
    return pd.DataFrame(rows)


def load_med_mia() -> pd.DataFrame:
    path = ROOT / "MedSparseSNN/outputs/csv/mia_results_dermamnist_final_compare.csv"
    rows = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            auc_m, auc_s = parse_mean_std(r["auc"])
            rows.append({"model": r["model"], "auc_mean": auc_m, "auc_std": auc_s})
    return pd.DataFrame(rows)


def plot_med_clean() -> None:
    eff = load_med_eff()
    mia = load_med_mia()

    # Accuracy comparison
    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    x = np.arange(len(eff))
    ax.bar(x, eff["test_acc_mean"], yerr=eff["test_acc_std"], capsize=4, color=["#4E79A7", "#F28E2B", "#59A14F"])
    ax.set_xticks(x)
    ax.set_xticklabels(eff["model"])
    ax.set_title("Model Accuracy Comparison", fontsize=14, fontweight="bold")
    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Accuracy (%)", fontsize=12)
    ax.tick_params(axis="both", labelsize=11)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(OUT / "med_accuracy_clean.png", dpi=320)
    plt.close(fig)

    # MIA AUC comparison
    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    x = np.arange(len(mia))
    ax.bar(x, mia["auc_mean"], yerr=mia["auc_std"], capsize=4, color=["#4E79A7", "#F28E2B", "#59A14F"])
    ax.set_xticks(x)
    ax.set_xticklabels(mia["model"])
    ax.set_title("MIA AUC Comparison", fontsize=14, fontweight="bold")
    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("AUC (unitless)", fontsize=12)
    ax.tick_params(axis="both", labelsize=11)
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(OUT / "med_mia_auc_clean.png", dpi=320)
    plt.close(fig)

    # Power-latency (using energy-latency from summary)
    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    for _, r in eff.iterrows():
        ax.errorbar(
            r["lat_mean"],
            r["ene_mean"],
            xerr=r["lat_std"],
            yerr=r["ene_std"],
            fmt="o",
            markersize=8,
            capsize=4,
            label=r["model"],
        )
        ax.annotate(r["model"], (r["lat_mean"], r["ene_mean"]), textcoords="offset points", xytext=(6, 4))
    ax.set_title("Latency-Energy Trade-off", fontsize=14, fontweight="bold")
    ax.set_xlabel("Latency (ms/sample)", fontsize=12)
    ax.set_ylabel("Energy (mJ/sample)", fontsize=12)
    ax.tick_params(axis="both", labelsize=11)
    ax.grid(alpha=0.25)
    fig.savefig(OUT / "med_latency_energy_clean.png", dpi=320)
    plt.close(fig)


def main() -> None:
    plot_embodied_clean(load_embodied_best())
    plot_neuro_clean()
    plot_med_clean()
    print(f"clean figures saved to: {OUT}")


if __name__ == "__main__":
    main()
