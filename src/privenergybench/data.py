from __future__ import annotations

import numpy as np
import torch
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset


def build_synthetic_dataset(cfg: dict, seed: int) -> tuple[TensorDataset, TensorDataset, dict]:
    dcfg = cfg["dataset"]
    n_samples = int(dcfg["n_samples"])
    n_features = int(dcfg["n_features"])
    n_classes = int(dcfg["n_classes"])

    x, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=max(n_features // 2, n_classes * 2),
        n_redundant=max(n_features // 6, 2),
        n_classes=n_classes,
        n_clusters_per_class=1,
        class_sep=float(dcfg.get("class_sep", 1.5)),
        flip_y=float(dcfg.get("noise_fraction", 0.02)),
        random_state=seed,
    )

    x_train, x_val, y_train, y_val = train_test_split(
        x.astype(np.float32),
        y.astype(np.int64),
        train_size=float(dcfg["train_ratio"]),
        stratify=y,
        random_state=seed,
    )

    # Compute sensitive attribute from feature space (independent of labels).
    attr_cfg = cfg.get("sensitive_attribute", {})
    feature_indices = attr_cfg.get("feature_indices", [0, 1, 2])
    rule = attr_cfg.get("rule", "sum_threshold")
    
    if rule == "sum_threshold":
        x_train_attr_scores = x_train[:, feature_indices].sum(axis=1)
        x_val_attr_scores = x_val[:, feature_indices].sum(axis=1)
        threshold = float(np.median(x_train_attr_scores))
        train_attr = (x_train_attr_scores > threshold).astype(np.int64)
        val_attr = (x_val_attr_scores > threshold).astype(np.int64)
    else:
        train_attr = np.zeros(len(x_train), dtype=np.int64)
        val_attr = np.zeros(len(x_val), dtype=np.int64)

    train_ds = TensorDataset(torch.from_numpy(x_train), torch.from_numpy(y_train), torch.from_numpy(train_attr))
    val_ds = TensorDataset(torch.from_numpy(x_val), torch.from_numpy(y_val), torch.from_numpy(val_attr))
    meta = {
        "n_features": n_features,
        "n_classes": n_classes,
        "train_samples": int(len(train_ds)),
        "val_samples": int(len(val_ds)),
        "sensitive_attribute_rule": f"{rule} (features={feature_indices}, threshold={threshold})",
    }
    return train_ds, val_ds, meta


def build_dataloaders(cfg: dict, seed: int) -> tuple[DataLoader, DataLoader, dict]:
    train_ds, val_ds, meta = build_synthetic_dataset(cfg, seed)
    batch_size = int(cfg["train"]["batch_size"])
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0, generator=generator)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    return train_loader, val_loader, meta
