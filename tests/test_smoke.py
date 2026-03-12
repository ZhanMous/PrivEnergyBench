from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from privenergybench.cli import run_benchmark


def test_smoke_benchmark(tmp_path: Path):
    config_path = tmp_path / "smoke.yaml"
    output_dir = tmp_path / "outputs"
    config_path.write_text(
        "\n".join(
            [
                "seed: 7",
                "dataset:",
                "  type: synthetic_classification",
                "  n_samples: 200",
                "  n_features: 24",
                "  n_classes: 3",
                "  train_ratio: 0.8",
                "  class_sep: 1.2",
                "  noise_fraction: 0.01",
                "benchmark:",
                "  model_types: [linear, mlp]",
                "model:",
                "  hidden_dim: 32",
                "  dropout: 0.1",
                "train:",
                "  batch_size: 32",
                "  epochs: 2",
                "  lr: 0.001",
                "  weight_decay: 0.0001",
                "energy:",
                "  num_batches: 5",
                "  proxy_power_w: 20.0",
                "device: cpu",
                f"output_dir: {output_dir.as_posix()}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    rows = run_benchmark(str(config_path))
    assert len(rows) == 2
    assert (output_dir / "summary.csv").exists()
    assert (output_dir / "benchmark_report.md").exists()
    assert all("val_acc" in row for row in rows)
    assert all("mia_auc" in row for row in rows)
