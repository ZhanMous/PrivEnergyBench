from __future__ import annotations

import math

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


class Conv1DClassifier(nn.Module):
    def __init__(self, in_features: int, hidden_dim: int, num_classes: int, dropout: float) -> None:
        super().__init__()
        channels = max(hidden_dim // 4, 16)
        self.features = nn.Sequential(
            nn.Conv1d(1, channels, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.Conv1d(channels, channels * 2, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(16),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(channels * 2 * 16, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.unsqueeze(1)
        return self.classifier(self.features(x))


class TinyTransformerClassifier(nn.Module):
    def __init__(self, in_features: int, hidden_dim: int, num_classes: int, dropout: float, heads: int) -> None:
        super().__init__()
        token_dim = max(4, min(16, hidden_dim // 8))
        seq_len = math.ceil(in_features / token_dim)
        padded_features = seq_len * token_dim
        self.in_features = in_features
        self.token_dim = token_dim
        self.seq_len = seq_len
        self.padded_features = padded_features
        self.input_proj = nn.Linear(token_dim, hidden_dim)
        self.positional = nn.Parameter(torch.zeros(1, seq_len, hidden_dim))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=max(1, heads),
            dim_feedforward=hidden_dim * 2,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=1)
        self.head = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.padded_features > self.in_features:
            pad = self.padded_features - self.in_features
            x = torch.nn.functional.pad(x, (0, pad))
        x = x.view(x.shape[0], self.seq_len, self.token_dim)
        x = self.input_proj(x) + self.positional
        x = self.encoder(x)
        x = x.mean(dim=1)
        return self.head(x)


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
    if model_type == "cnn1d":
        return Conv1DClassifier(
            in_features=in_features,
            hidden_dim=int(mcfg.get("hidden_dim", 128)),
            num_classes=num_classes,
            dropout=float(mcfg.get("dropout", 0.1)),
        )
    if model_type == "transformer":
        return TinyTransformerClassifier(
            in_features=in_features,
            hidden_dim=int(mcfg.get("hidden_dim", 128)),
            num_classes=num_classes,
            dropout=float(mcfg.get("dropout", 0.1)),
            heads=int(mcfg.get("transformer_heads", 4)),
        )
    raise ValueError(f"Unsupported model type: {model_type}")


def count_parameters(model: nn.Module) -> int:
    return int(sum(parameter.numel() for parameter in model.parameters()))
