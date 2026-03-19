from __future__ import annotations

import random

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def resolve_device(name: str) -> torch.device:
    if name == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def train_model(model: nn.Module, train_loader: DataLoader, cfg: dict, device: torch.device) -> list[dict[str, float]]:
    tcfg = cfg["train"]
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(tcfg["lr"]),
        weight_decay=float(tcfg["weight_decay"]),
    )
    criterion = nn.CrossEntropyLoss()
    history: list[dict[str, float]] = []

    model.train()
    for epoch in range(int(tcfg["epochs"])):
        total_loss = 0.0
        total_count = 0
        for x, y in train_loader:
            x = x.to(device)
            y = y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item()) * y.shape[0]
            total_count += int(y.shape[0])

        history.append({
            "epoch": float(epoch + 1),
            "train_loss": total_loss / max(total_count, 1),
        })
    return history


def collect_predictions(model: nn.Module, loader: DataLoader, device: torch.device) -> dict[str, np.ndarray | float]:
    criterion = nn.CrossEntropyLoss()
    model.eval()
    logits_list = []
    labels_list = []
    inputs_list = []
    total_loss = 0.0
    total_count = 0

    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            logits = model(x)
            loss = criterion(logits, y)
            total_loss += float(loss.item()) * y.shape[0]
            total_count += int(y.shape[0])
            logits_list.append(logits.cpu())
            labels_list.append(y.cpu())
            inputs_list.append(x.cpu())

    logits = torch.cat(logits_list, dim=0)
    labels = torch.cat(labels_list, dim=0)
    inputs = torch.cat(inputs_list, dim=0)
    probs = torch.softmax(logits, dim=1).numpy()
    pred = probs.argmax(axis=1)
    labels_np = labels.numpy()
    acc = float((pred == labels_np).mean())

    return {
        "loss": total_loss / max(total_count, 1),
        "acc": acc,
        "probs": probs,
        "labels": labels_np,
        "inputs": inputs.numpy(),
    }
