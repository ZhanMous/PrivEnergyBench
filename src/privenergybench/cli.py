from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config, save_json
from .data import build_dataloaders
from .energy import measure_latency_and_energy
from .models import build_model, count_parameters
from .privacy import confidence_membership_inference
from .reporting import plot_pareto, save_markdown_report, save_summary_csv
from .train import collect_predictions, resolve_device, set_seed, train_model


def run_benchmark(config_path: str) -> list[dict]:
    cfg = load_config(config_path)
    seed = int(cfg["seed"])
    set_seed(seed)

    device = resolve_device(str(cfg.get("device", "cpu")))
    train_loader, val_loader, meta = build_dataloaders(cfg, seed)
    out_dir = Path(str(cfg.get("output_dir", "outputs/default")))
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for model_type in list(cfg["benchmark"]["model_types"]):
        model = build_model(
            model_type=model_type,
            in_features=int(meta["n_features"]),
            num_classes=int(meta["n_classes"]),
            cfg=cfg,
        ).to(device)

        history = train_model(model, train_loader, cfg, device)
        train_eval = collect_predictions(model, train_loader, device)
        val_eval = collect_predictions(model, val_loader, device)
        privacy = confidence_membership_inference(train_eval["probs"], val_eval["probs"])
        energy = measure_latency_and_energy(
            model=model,
            loader=val_loader,
            device=device,
            num_batches=int(cfg["energy"].get("num_batches", 50)),
            proxy_power_w=float(cfg["energy"].get("proxy_power_w", 35.0)),
        )

        row = {
            "model": str(model_type),
            "num_params": count_parameters(model),
            "train_loss": float(train_eval["loss"]),
            "train_acc": float(train_eval["acc"]),
            "val_loss": float(val_eval["loss"]),
            "val_acc": float(val_eval["acc"]),
            "mia_auc": float(privacy["mia_auc"]),
            "mia_acc": float(privacy["mia_acc"]),
            "latency_ms": float(energy["latency_ms"]),
            "avg_power_w": float(energy["avg_power_w"]),
            "energy_mj": float(energy["energy_mj"]),
        }
        rows.append(row)
        save_json({"history": history, "metrics": row, "privacy": privacy}, out_dir / f"{model_type}_report.json")

    save_summary_csv(rows, out_dir / "summary.csv")
    save_markdown_report(rows, cfg, out_dir / "benchmark_report.md")
    plot_pareto(rows, out_dir / "pareto.png")
    save_json({"rows": rows, "config": cfg}, out_dir / "benchmark_bundle.json")
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PrivEnergyBench benchmark")
    parser.add_argument("--config", type=str, default="configs/default.yaml")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result_rows = run_benchmark(args.config)
    print("=== Benchmark Summary ===")
    for row in result_rows:
        print(
            f"{row['model']:<10} acc={row['val_acc']:.4f}  mia_auc={row['mia_auc']:.4f}  "
            f"lat={row['latency_ms']:.4f}ms  energy={row['energy_mj']:.4f}mJ"
        )
