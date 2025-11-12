#!/usr/bin/env python3
"""H100-oriented MONAI UNet benchmark for randomized 3D volumes."""
import argparse
import json
import time
from contextlib import nullcontext

import torch
from monai.networks.nets import UNet


def build_model(device: torch.device) -> torch.nn.Module:
    model = UNet(
        spatial_dims=3,
        in_channels=1,
        out_channels=2,
        channels=(16, 32, 64, 128, 256),
        strides=(2, 2, 2, 2),
        num_res_units=2,
        norm="INSTANCE",
    )
    model.to(device)
    model.eval()
    return model


def generate_input(batch_size: int, patch_size: int, device: torch.device) -> torch.Tensor:
    shape = (batch_size, 1, patch_size, patch_size, patch_size)
    return torch.randn(shape, device=device)


def benchmark(model, input_tensor, runs: int, warmup: int, use_amp: bool) -> float:
    torch.cuda.synchronize()
    with torch.inference_mode():
        for _ in range(warmup):
            with torch.autocast(device_type="cuda", dtype=torch.float16) if use_amp else nullcontext():
                _ = model(input_tensor)
    torch.cuda.synchronize()

    timings = []
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)

    with torch.inference_mode():
        for _ in range(runs):
            with torch.autocast(device_type="cuda", dtype=torch.float16) if use_amp else nullcontext():
                start_event.record()
                _ = model(input_tensor)
                end_event.record()
            torch.cuda.synchronize()
            timings.append(start_event.elapsed_time(end_event))
    return sum(timings) / len(timings)


def main():
    parser = argparse.ArgumentParser(description="MONAI H100 benchmark")
    parser.add_argument("--patch-size", type=int, default=96)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--mode", choices=["baseline", "optimized"], default="baseline")
    parser.add_argument("--compile", action="store_true")
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU not available")

    device = torch.device("cuda")
    model = build_model(device)

    use_compile = args.compile or args.mode == "optimized"
    if use_compile:
        model = torch.compile(model, mode="reduce-overhead", fullgraph=True)

    input_tensor = generate_input(args.batch_size, args.patch_size, device)

    use_amp = args.mode == "optimized"
    avg_ms = benchmark(model, input_tensor, runs=args.runs, warmup=args.warmup, use_amp=use_amp)

    voxel_rate = (args.batch_size / (avg_ms / 1000.0)) * (args.patch_size ** 3)

    payload = {
        "mode": args.mode,
        "compiled": bool(use_compile),
        "amp": bool(use_amp),
        "avg_ms": avg_ms,
        "voxels_per_second": voxel_rate,
        "batch_size": args.batch_size,
        "patch_size": args.patch_size,
        "runs": args.runs,
        "warmup": args.warmup,
        "timestamp": time.time(),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
