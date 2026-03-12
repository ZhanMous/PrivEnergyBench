from __future__ import annotations

import torch
import torch.nn as nn


class LinearClassifier(nn.Module):
    def __init__(self, in_features: int, num_classes: int) -> None:
        super().__init__()
        self.net = nn.Linear(in_features, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class MLPClassifier(nn.Module):
    def __init__(self, in_features: int, hidden_dim: int, num_classes: int, dropout: float) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def build_model(model_type: str, in_features: int, num_classes: int, cfg: dict) -> nn.Module:
    model_type = model_type.lower()
    mcfg = cfg["model"]
    if model_type == "linear":
        return LinearClassifier(in_features, num_classes)
    if model_type == "mlp":
        return MLPClassifier(
            in_features=in_features,
            hidden_dim=int(mcfg.get("hidden_dim", 128)),
            num_classes=num_classes,
            dropout=float(mcfg.get("dropout", 0.1)),
        )
    raise ValueError(f"Unsupported model type: {model_type}")


def count_parameters(model: nn.Module) -> int:
    return int(sum(parameter.numel() for parameter in model.parameters()))
