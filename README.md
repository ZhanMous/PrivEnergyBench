# PrivEnergyBench

PrivEnergyBench is a lightweight benchmarking toolkit for PyTorch classifiers that reports three axes together:

- utility: accuracy and loss
- privacy: membership inference attack metrics
- efficiency: latency and energy proxy

The project is designed as a compact, interview-friendly engineering artifact: one command produces a benchmark summary, a Pareto plot, and a Markdown report.

## Quickstart

```bash
cd /home/yanshi/PrivEnergyBench
pip install -r requirements.txt
pip install -e .
python -m privenergybench.cli --config configs/default.yaml
```

## What it does

1. Builds a synthetic classification dataset.
2. Trains one or more PyTorch classifiers.
3. Evaluates validation accuracy.
4. Runs a confidence-based membership inference attack.
5. Measures latency and estimates energy.
6. Writes:
- `summary.csv`
- `benchmark_report.md`
- `pareto.png`

## Default models

- `linear`
- `mlp`

## Output example

Outputs are written under the configured directory, by default `outputs/default`.
