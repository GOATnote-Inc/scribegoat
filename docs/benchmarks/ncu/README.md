# Healthcare AI Nsight Dataset (H100 · CUDA 13.0.2)

This folder distills Nsight Compute profiling data captured from the GOAT Scribe MONAI inference benchmark on an NVIDIA H100 PCIe system. The goal is to provide a transparent, reproducible reference for:

1. **Healthcare AI startups** – understand where Hopper cycles are spent when running a Torch/MONAI imaging model inside a clinical note generation service.
2. **GPU kernel researchers** – inspect Triton, cuBLASLt, and CUTLASS kernels that dominate the workload and quantify warp stall behaviour.
3. **NVIDIA MONAI, Clara, and Healthcare AI teams** – share a sanitized dataset for optimization, documentation, and community engagement.

## Workload & Software Stack

| Component | Version / Notes |
|-----------|-----------------|
| GPU | NVIDIA H100 PCIe (driver 580.105.08) |
| CUDA Toolkit | 13.0.2 (Update 2) |
| PyTorch | 2.10.0.dev20251110+cu130 |
| MONAI | 1.5.1.dev (weekly) |
| CUTLASS | 4.3.0 |
| FlashAttention | 3.0.1 |
| Nsight Compute CLI | 2025.3.1 |
| Benchmark script | `scripts/monai_h100_benchmark.py --mode optimized` |

The benchmark runs a 3D MONAI UNet forward pass (batch 1, patch 96³) compiled with `torch.compile` and autocast FP16. Nsight Compute is invoked with full-metric replay, yielding the `ncu_monai_opt.ncu-rep` report that underpins the dataset below.

## What’s Inside

```
docs/benchmarks/ncu/
├── LICENSE                     # Apache 2.0 notice for dataset reuse
├── METADATA.json               # Machine-readable provenance fields
├── README.md                   # Dataset guide (this file)
├── monai_h100_summary.csv      # Baseline release summary (Nov 10 2025)
├── plots/                      # Baseline release visualisations
└── latest/                     # Rolling Nsight drops (Nov 12 2025 run included)
    ├── ncu_monai_opt_latest.ncu-rep
    ├── monai_h100_summary.csv
    └── plots/
        ├── roofline_tensor_vs_bandwidth.png
        ├── sm_occupancy.png
        └── warp_stall_breakdown.png
```

### `monai_h100_summary.csv`
The CSV aggregates 56 kernels seen across Nsight’s replay passes. For each kernel we record:

- `time_ms` and `time_share_pct` – execution time at the GPU domain (nanosecond totals scaled to milliseconds).
- `tensor_core_active_pct_mean` – average tensor pipeline utilisation relative to peak.
- `occupancy_pct_mean` – average SM warp occupancy.
- `dram_gbps_mean`, `dram_read_gb_total`, `dram_write_gb_total` – effective memory throughput.
- `l2_throughput_pct_mean` – L2 throughput as % of peak sustained.
- `stall_*_ratio` columns – average warp stall reasons reported by Nsight (`ratio = stall warps / issued warps`).

Identifying information (hostnames, PIDs, filesystem paths) is stripped; only kernel symbol strings shipped with NVIDIA libraries remain.

The Nov 12 2025 refresh in `latest/monai_h100_summary.csv` uses the same schema and is generated from `ncu_monai_opt_latest.ncu-rep` (torch.compile + AMP).

### Key Takeaways

- **Two kernels dominate runtime**: an `at::vectorized_elementwise_kernel` accounts for ~80% of GPU time, followed by `vol2col` + `vol2im` data movers. These are PyTorch utility kernels, not tensor-core heavy operators.
- **Tensor core activity is low (≃0.46% weighted)** because most passes manipulate tensors (scatter/gather, col2im) rather than performing GEMM/conv math. Hopper’s tensor pipelines are underutilised in this configuration.
- **SM occupancy remains high (~73% weighted), but warp stalls are governed by the long-scoreboard path and memory dependencies**—highlighting opportunities for layout fusion or Triton-based tiling.
- **Memory traffic skews toward reads** (`dram_read_gb_total` ≫ writes) driven by vol2col patterns; L2 throughput averages 4–5% of peak, so there is headroom for locality improvements.

The plots in `plots/` visualise these trends:

- `roofline_tensor_vs_bandwidth.png` – Tensor utilisation vs. DRAM throughput for the top 10 kernels (bubble size = time share, colour = occupancy).
- `warp_stall_breakdown.png` – Normalised stall composition per kernel (long scoreboard + memory waits dominate).
- `sm_occupancy.png` – Average SM occupancy by kernel symbol.

## Reproducing & Extending

1. **Generate a fresh report**
   ```bash
   export NGC_API_KEY="<rotated nvapi-*>"
   python scripts/monai_h100_benchmark.py --mode optimized --runs 10 --warmup 3 --patch-size 96
   sudo /usr/local/cuda-13.0/bin/ncu --target-processes all \
        --set full --export ncu_monai_opt --force-overwrite \
        python scripts/monai_h100_benchmark.py --mode optimized --runs 10 --warmup 3 --patch-size 96
   # For quicker sanity sweeps, append `--set roofline -c 1` to the ncu command
   ```
   (Run Nsight as root or relax GPU counter permissions per [ERR_NVGPUCTRPERM](https://developer.nvidia.com/ERR_NVGPUCTRPERM)).

2. **Convert to CSV & regenerate artefacts**
   ```bash
   /usr/local/cuda-13.0/bin/ncu --import ncu_monai_opt.ncu-rep --csv --page raw > /tmp/ncu_raw.csv
   python scripts/process_ncu_report.py  # optional helper; otherwise use the inline logic from this repo
   ```

3. **Compare future GPUs**
   Use `scripts/compare_ncu.py` (see below) to diff multiple `monai_h100_summary.csv` files (e.g., H100 vs. L4 vs. B200) and emit JSON deltas for automated reporting.

## Optional Helper – `scripts/compare_ncu.py`
This utility accepts two or more Nsight summary CSVs and prints kernel-wise diffs for key metrics.

```bash
python scripts/compare_ncu.py docs/benchmarks/ncu/monai_h100_summary.csv <path-to-other-summary.csv>
```

Outputs include time share deltas, tensor-core utilisation changes, and stall ratio differences, making it easy to spot regressions or wins after kernel rewrites.

## Contributing

- Share alternative profiling runs (different batch sizes, MONAI networks, or TensorRT-LLM deployments) via pull request.
- Add new visualisations (roofline vs. shared-memory bandwidth, Triton kernel deep dives, occupancy vs. register pressure).
- File issues with suggestions for better sanitisation, metric coverage, or narrative clarity.

Together we can build a canonical benchmark suite for clinical AI workloads, accelerate Hopper/Blackwell adoption, and give healthcare startups the telemetry they need to operate safely and fast.
