from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score


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
