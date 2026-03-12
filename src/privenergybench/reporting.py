from __future__ import annotations

import csv
from pathlib import Path


def save_summary_csv(rows: list[dict], path: str | Path) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_markdown_report(rows: list[dict], cfg: dict, path: str | Path) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# PrivEnergyBench Report",
        "",
        f"- Seed: {cfg['seed']}",
        f"- Dataset samples: {cfg['dataset']['n_samples']}",
        f"- Features: {cfg['dataset']['n_features']}",
        f"- Classes: {cfg['dataset']['n_classes']}",
        "",
        "## Summary",
        "",
        "| model | val_acc | mia_auc | latency_ms | energy_mj | params |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} | {row['val_acc']:.4f} | {row['mia_auc']:.4f} | "
            f"{row['latency_ms']:.4f} | {row['energy_mj']:.4f} | {row['num_params']} |"
        )

    best_acc = max(rows, key=lambda row: row["val_acc"]) if rows else None
    best_privacy = min(rows, key=lambda row: row["mia_auc"]) if rows else None
    best_energy = min(rows, key=lambda row: row["energy_mj"]) if rows else None
    if best_acc and best_privacy and best_energy:
        lines.extend([
            "",
            "## Highlights",
            "",
            f"- Highest validation accuracy: {best_acc['model']} ({best_acc['val_acc']:.4f})",
            f"- Lowest MIA AUC: {best_privacy['model']} ({best_privacy['mia_auc']:.4f})",
            f"- Lowest energy proxy: {best_energy['model']} ({best_energy['energy_mj']:.4f} mJ/sample)",
        ])

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_pareto(rows: list[dict], path: str | Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 5))
    for row in rows:
        ax.scatter(row["energy_mj"], row["val_acc"], s=90, label=row["model"])
        ax.annotate(row["model"], (row["energy_mj"], row["val_acc"]), xytext=(6, 6), textcoords="offset points")

    ax.set_xlabel("Energy Proxy (mJ/sample)")
    ax.set_ylabel("Validation Accuracy")
    ax.set_title("PrivEnergyBench Pareto View")
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
