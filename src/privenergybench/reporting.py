from __future__ import annotations

import csv
import html
import json
from pathlib import Path

import numpy as np


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


def aggregate_rows(rows: list[dict]) -> list[dict]:
    if not rows:
        return []

    metrics = [
        "train_loss",
        "train_acc",
        "val_loss",
        "val_acc",
        "mia_auc",
        "mia_acc",
        "attr_auc",
        "inversion_risk",
        "latency_ms",
        "avg_power_w",
        "energy_mj",
    ]
    model_names = sorted({str(row["model"]) for row in rows})
    aggregate = []
    for model_name in model_names:
        subset = [row for row in rows if str(row["model"]) == model_name]
        n = len(subset)
        result = {
            "model": model_name,
            "num_runs": n,
            "num_params": int(subset[0]["num_params"]),
        }
        for metric in metrics:
            values = np.array([float(row[metric]) for row in subset], dtype=float)
            mean = float(values.mean())
            std = float(values.std(ddof=0))
            ci95 = float(1.96 * std / max(n ** 0.5, 1.0))
            result[f"{metric}_mean"] = mean
            result[f"{metric}_std"] = std
            result[f"{metric}_ci95"] = ci95
        aggregate.append(result)
    return aggregate


def save_markdown_report(rows: list[dict], cfg: dict, path: str | Path) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    summary_rows = aggregate_rows(rows)
    seeds = cfg.get("benchmark", {}).get("seeds", [cfg["seed"]])
    lines = [
        "# PrivEnergyBench Report",
        "",
        f"- Seeds: {seeds}",
        f"- Dataset samples: {cfg['dataset']['n_samples']}",
        f"- Features: {cfg['dataset']['n_features']}",
        f"- Classes: {cfg['dataset']['n_classes']}",
        "",
        "## Aggregate Summary",
        "",
        "| model | val_acc(mean±std) | mia_auc(mean±std) | latency_ms | energy_mj | params |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['model']} | {row['val_acc_mean']:.4f}±{row['val_acc_std']:.4f} | {row['mia_auc_mean']:.4f}±{row['mia_auc_std']:.4f} | "
            f"{row['latency_ms_mean']:.4f} | {row['energy_mj_mean']:.4f} | {row['num_params']} |"
        )

    lines.extend([
        "",
        "## Extended Privacy Metrics",
        "",
        "| model | attr_auc(mean±std) | inversion_risk(mean±std) |",
        "|---|---:|---:|",
    ])
    for row in summary_rows:
        lines.append(
            f"| {row['model']} | {row['attr_auc_mean']:.4f}±{row['attr_auc_std']:.4f} | {row['inversion_risk_mean']:.4f}±{row['inversion_risk_std']:.4f} |"
        )

    best_acc = max(summary_rows, key=lambda row: row["val_acc_mean"]) if summary_rows else None
    best_privacy = min(summary_rows, key=lambda row: row["mia_auc_mean"]) if summary_rows else None
    best_energy = min(summary_rows, key=lambda row: row["energy_mj_mean"]) if summary_rows else None
    if best_acc and best_privacy and best_energy:
        lines.extend([
            "",
            "## Highlights",
            "",
            f"- Highest validation accuracy: {best_acc['model']} ({best_acc['val_acc_mean']:.4f})",
            f"- Lowest MIA AUC: {best_privacy['model']} ({best_privacy['mia_auc_mean']:.4f})",
            f"- Lowest energy proxy: {best_energy['model']} ({best_energy['energy_mj_mean']:.4f} mJ/sample)",
        ])

    lines.extend([
        "",
        "## Raw Runs",
        "",
        "| seed | model | val_acc | mia_auc | energy_mj |",
        "|---:|---|---:|---:|---:|",
    ])
    for row in rows:
        lines.append(
            f"| {row['seed']} | {row['model']} | {row['val_acc']:.4f} | {row['mia_auc']:.4f} | {row['energy_mj']:.4f} |"
        )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_html_dashboard(rows: list[dict], cfg: dict, path: str | Path) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    aggregate = aggregate_rows(rows)
    raw_json = html.escape(json.dumps(rows, ensure_ascii=True))
    cards = []
    for row in aggregate:
        cards.append(
            """
            <div class=\"card\">
              <div class=\"label\">{model}</div>
              <div class=\"metric\">Acc {acc:.3f}</div>
              <div class=\"sub\">MIA AUC {mia:.3f}</div>
              <div class=\"sub\">Energy {energy:.4f} mJ</div>
              <div class=\"sub\">95% CI {ci:.4f}</div>
            </div>
            """.format(
                model=html.escape(str(row["model"])),
                acc=row["val_acc_mean"],
                mia=row["mia_auc_mean"],
                energy=row["energy_mj_mean"],
                ci=row["val_acc_ci95"],
            )
        )

    table_rows = []
    for row in aggregate:
        table_rows.append(
            "<tr><td>{model}</td><td>{acc:.4f}±{acc_std:.4f}</td><td>{mia:.4f}±{mia_std:.4f}</td><td>{attr:.4f}±{attr_std:.4f}</td><td>{inv:.4f}±{inv_std:.4f}</td><td>{lat:.4f}</td><td>{energy:.4f}</td><td>{params}</td></tr>".format(
                model=html.escape(str(row["model"])),
                acc=row["val_acc_mean"],
                acc_std=row["val_acc_std"],
                mia=row["mia_auc_mean"],
                mia_std=row["mia_auc_std"],
                attr=row["attr_auc_mean"],
                attr_std=row["attr_auc_std"],
                inv=row["inversion_risk_mean"],
                inv_std=row["inversion_risk_std"],
                lat=row["latency_ms_mean"],
                energy=row["energy_mj_mean"],
                params=row["num_params"],
            )
        )

    page = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>PrivEnergyBench Dashboard</title>
  <style>
    :root {{
      --bg: #f4f0e8;
      --panel: #fffaf2;
      --ink: #1e1d1a;
      --muted: #6c665c;
      --accent: #bf5b04;
      --accent-2: #0f766e;
      --border: #dfd5c7;
    }}
    body {{ margin: 0; font-family: Georgia, 'Times New Roman', serif; background: radial-gradient(circle at top left, #fff8ee, var(--bg)); color: var(--ink); }}
    .wrap {{ max-width: 1080px; margin: 0 auto; padding: 40px 24px 56px; }}
    .hero {{ display: grid; gap: 12px; margin-bottom: 28px; }}
    h1 {{ margin: 0; font-size: 44px; line-height: 1.05; letter-spacing: -0.02em; }}
    .lede {{ max-width: 760px; color: var(--muted); font-size: 18px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 26px 0 34px; }}
    .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 18px; padding: 18px; box-shadow: 0 10px 30px rgba(90, 70, 30, 0.06); }}
    .label {{ font-size: 13px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--accent); margin-bottom: 12px; }}
    .metric {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
    .sub {{ color: var(--muted); margin-bottom: 4px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 18px; padding: 20px; margin-top: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 15px; }}
    th, td {{ text-align: left; padding: 12px 10px; border-bottom: 1px solid var(--border); }}
    th {{ color: var(--accent-2); font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; }}
    .meta {{ color: var(--muted); font-size: 14px; }}
    code {{ white-space: pre-wrap; font-size: 12px; color: #5b5147; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <section class=\"hero\">
      <div class=\"meta\">PrivEnergyBench • utility / privacy / energy</div>
      <h1>Benchmark Dashboard</h1>
      <div class=\"lede\">A compact benchmarking surface for model comparison under three axes. This dashboard summarizes multi-seed accuracy, membership inference risk, latency, and energy proxy from a single run bundle.</div>
      <div class=\"meta\">Seeds: {html.escape(str(cfg.get('benchmark', {}).get('seeds', [cfg['seed']])))}</div>
    </section>
    <section class=\"cards\">{''.join(cards)}</section>
    <section class=\"panel\">
            <h2>Aggregate Table</h2>
      <table>
                <thead><tr><th>Model</th><th>Val Acc</th><th>MIA AUC</th><th>Attr AUC</th><th>Inversion Risk</th><th>Latency ms</th><th>Energy mJ</th><th>Params</th></tr></thead>
        <tbody>{''.join(table_rows)}</tbody>
      </table>
    </section>
    <section class=\"panel\">
      <h2>Raw Run Bundle</h2>
      <code>{raw_json}</code>
    </section>
  </div>
</body>
</html>
"""
    out_path.write_text(page, encoding="utf-8")


def plot_pareto(rows: list[dict], path: str | Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    plot_rows = aggregate_rows(rows)
    fig, ax = plt.subplots(figsize=(7, 5))
    for row in plot_rows:
        ax.scatter(row["energy_mj_mean"], row["val_acc_mean"], s=100, label=row["model"])
        ax.annotate(row["model"], (row["energy_mj_mean"], row["val_acc_mean"]), xytext=(6, 6), textcoords="offset points")

    ax.set_xlabel("Energy Proxy (mJ/sample)")
    ax.set_ylabel("Validation Accuracy")
    ax.set_title("PrivEnergyBench Pareto View")
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
