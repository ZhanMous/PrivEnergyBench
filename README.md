# PrivEnergyBench

PrivEnergyBench is a lightweight benchmarking toolkit for PyTorch classifiers that reports three axes together:

- utility: accuracy and loss
- privacy: membership inference attack metrics
- efficiency: latency and energy proxy

The project is designed as a compact, interview-friendly engineering artifact: one command produces benchmark summaries, confidence intervals, a Pareto plot, a Markdown report, and an HTML dashboard.

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
3. Evaluates validation accuracy across one or more seeds.
4. Runs a confidence-based membership inference attack.
5. Measures latency and estimates energy.
6. Writes:
- `summary.csv`
- `aggregate_summary.csv`
- `benchmark_report.md`
- `dashboard.html`
- `pareto.png`

## Default models

- `linear`
- `mlp`
- `cnn1d`
- `transformer`

## Output example

Outputs are written under the configured directory, by default `outputs/default`.

## Default deliverables

The default configuration runs 3 seeds across 4 model families and produces:

- per-run metrics in `summary.csv`
- mean/std/95% CI in `aggregate_summary.csv`
- a human-readable report in `benchmark_report.md`
- a showcase page in `dashboard.html`
- a Pareto-style scatter plot in `pareto.png`

## Interview Materials

The repository also contains ready-to-use materials for resume and interview presentation:

- `docs/project_showcase.html`: self-contained project showcase page
- `docs/resume_pack_zh.md`: Chinese resume/project wording pack
- `docs/tech_onepager_zh.md`: one-page technical brief for presentation or Q&A
- `docs/interview_storyline_zh.md`: three-project interview storyline and speaking script
- `docs/interview_qa_zh.md`: grouped interview Q&A checklist

If you want a quick local demo after running the benchmark, open:

- `outputs/default/dashboard.html`
- `docs/project_showcase.html`
