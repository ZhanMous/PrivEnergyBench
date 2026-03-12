from __future__ import annotations

import time

import numpy as np
import torch
from torch.utils.data import DataLoader


def measure_latency_and_energy(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
    num_batches: int,
    proxy_power_w: float,
) -> dict[str, float]:
    model.eval()
    latencies_ms = []

    with torch.no_grad():
        for batch_idx, (x, _y) in enumerate(loader):
            if batch_idx >= num_batches:
                break
            x = x.to(device)
            if device.type == "cuda":
                torch.cuda.synchronize(device)
            start = time.perf_counter()
            _ = model(x)
            if device.type == "cuda":
                torch.cuda.synchronize(device)
            elapsed_ms = (time.perf_counter() - start) * 1000.0 / max(x.shape[0], 1)
            latencies_ms.append(elapsed_ms)

    avg_latency_ms = float(np.mean(latencies_ms)) if latencies_ms else 0.0
    avg_power_w = float(proxy_power_w)
    energy_mj = avg_power_w * avg_latency_ms
    return {
        "latency_ms": avg_latency_ms,
        "avg_power_w": avg_power_w,
        "energy_mj": energy_mj,
    }
