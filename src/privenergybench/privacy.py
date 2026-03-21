from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.neural_network import MLPClassifier


def confidence_membership_inference(train_probs: np.ndarray, val_probs: np.ndarray) -> dict[str, float]:
    train_conf = train_probs.max(axis=1)
    val_conf = val_probs.max(axis=1)

    scores = np.concatenate([train_conf, val_conf])
    labels = np.concatenate([
        np.ones(train_conf.shape[0], dtype=np.int64),
        np.zeros(val_conf.shape[0], dtype=np.int64),
    ])

    auc = float(roc_auc_score(labels, scores))

    thresholds = np.unique(np.quantile(scores, np.linspace(0.0, 1.0, 101)))
    best_acc = 0.0
    best_threshold = float(thresholds[0])
    for threshold in thresholds:
        pred = (scores >= threshold).astype(np.int64)
        acc = float((pred == labels).mean())
        if acc > best_acc:
            best_acc = acc
            best_threshold = float(threshold)

    return {
        "mia_auc": auc,
        "mia_acc": best_acc,
        "mia_threshold": best_threshold,
        "train_conf_mean": float(train_conf.mean()),
        "val_conf_mean": float(val_conf.mean()),
    }


def _safe_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    if len(np.unique(y_true)) < 2:
        return 0.5
    return float(roc_auc_score(y_true, y_score))


def _attribute_inference(
    train_probs: np.ndarray,
    train_attrs: np.ndarray,
    val_probs: np.ndarray,
    val_attrs: np.ndarray,
    seed: int,
) -> dict[str, float]:
    """Infer private sensitive attribute from model outputs.
    
    Uses only output probabilities and one-hot labels, not private attributes.
    But in privacy audit, we assume attrs could be inferred from outputs.
    """
    n_classes = int(train_probs.shape[1])
    x_train = train_probs  # Use only model outputs as features
    x_val = val_probs

    lr = LogisticRegression(max_iter=500, random_state=seed)
    lr.fit(x_train, train_attrs)
    lr_probs = lr.predict_proba(x_val)[:, 1]

    mlp = MLPClassifier(hidden_layer_sizes=(32,), max_iter=300, random_state=seed)
    mlp.fit(x_train, train_attrs)
    mlp_probs = mlp.predict_proba(x_val)[:, 1]

    lr_auc = _safe_auc(val_attrs, lr_probs)
    mlp_auc = _safe_auc(val_attrs, mlp_probs)
    return {
        "attr_auc": float(max(lr_auc, mlp_auc)),
        "attr_auc_logreg": float(lr_auc),
        "attr_auc_mlp": float(mlp_auc),
        "sensitive_attribute_rule": "feature_sum_threshold",
    }


def _inversion_attack(
    model: torch.nn.Module,
    val_probs: np.ndarray,
    val_inputs: np.ndarray,
    device: torch.device,
    steps: int = 60,
    lr: float = 0.08,
    l2_weight: float = 1e-3,
    max_samples: int = 64,
) -> dict[str, float]:
    n = min(max_samples, int(val_inputs.shape[0]))
    if n <= 0:
        return {
            "inversion_risk": 0.0,
            "inversion_nrmse": 1.0,
            "inversion_mse": 0.0,
            "num_inverted": 0,
        }

    x_true = torch.tensor(val_inputs[:n], dtype=torch.float32, device=device)
    target_probs = torch.tensor(val_probs[:n], dtype=torch.float32, device=device)
    x_hat = torch.randn_like(x_true, requires_grad=True)
    opt = torch.optim.Adam([x_hat], lr=lr)

    model.eval()
    for _ in range(steps):
        logits = model(x_hat)
        log_probs = F.log_softmax(logits, dim=1)
        kl = F.kl_div(log_probs, target_probs, reduction="batchmean")
        l2 = torch.mean(x_hat.pow(2))
        loss = kl + l2_weight * l2
        opt.zero_grad()
        loss.backward()
        opt.step()

    with torch.no_grad():
        mse = float(torch.mean((x_hat - x_true).pow(2)).item())
        denom = float(torch.var(x_true).item() + 1e-8)
        nrmse = float(mse / denom)
        risk = float(np.clip(1.0 / (1.0 + nrmse), 0.0, 1.0))
    return {
        "inversion_risk": risk,
        "inversion_nrmse": nrmse,
        "inversion_mse": mse,
        "num_inverted": int(n),
    }


def _plot_radar(mia_auc: float, attr_auc: float, inversion_risk: float, out_path: str | Path) -> None:
    labels = ["MIA", "Attribute", "Inversion"]
    mia_risk = float(np.clip(2.0 * (mia_auc - 0.5), 0.0, 1.0))
    attr_risk = float(np.clip(2.0 * (attr_auc - 0.5), 0.0, 1.0))
    values = [mia_risk, attr_risk, inversion_risk]
    values = values + [values[0]]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles = angles + [angles[0]]

    fig = plt.figure(figsize=(5.2, 5.0))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_title("Privacy Risk Radar")
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def privacy_multi_attack(
    model: torch.nn.Module,
    train_probs: np.ndarray,
    train_labels: np.ndarray,
    train_inputs: np.ndarray,
    train_attrs: np.ndarray,
    val_probs: np.ndarray,
    val_labels: np.ndarray,
    val_inputs: np.ndarray,
    val_attrs: np.ndarray,
    device: torch.device,
    out_dir: str | Path,
    seed: int,
) -> dict[str, float]:
    mia = confidence_membership_inference(train_probs, val_probs)
    attr = _attribute_inference(train_probs, train_attrs, val_probs, val_attrs, seed)
    inversion = _inversion_attack(model, val_probs, val_inputs, device)

    radar_path = Path(out_dir) / "privacy_radar.png"
    _plot_radar(mia["mia_auc"], attr["attr_auc"], inversion["inversion_risk"], radar_path)

    return {
        **mia,
        **attr,
        **inversion,
        "privacy_radar": str(radar_path),
    }
