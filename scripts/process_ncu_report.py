#!/usr/bin/env python3
"""Process an Nsight Compute raw CSV export into summary tables and plots."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

STALL_BINS = [
    'smsp__average_warps_issue_stalled_long_scoreboard_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_short_scoreboard_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_lg_throttle_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_tex_throttle_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_sleeping_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_branch_resolving_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_no_instruction_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_membar_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_gmma_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_imc_miss_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_dispatch_stall_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_wait_per_issue_active.ratio',
    'smsp__average_warps_issue_stalled_selected_per_issue_active.ratio'
]

BASE_COLS = [
    'Kernel Name',
    'gpu__time_duration.sum',
    'sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_active',
    'sm__warps_active.avg.pct_of_peak_sustained_active',
    'dram__bytes.sum.per_second',
    'dram__bytes_read.sum',
    'dram__bytes_write.sum',
    'lts__throughput.avg.pct_of_peak_sustained_elapsed'
] + STALL_BINS


def load_raw(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=BASE_COLS, low_memory=False)
    numeric_cols = [c for c in df.columns if c != 'Kernel Name']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    return df


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['time_ms'] = df['gpu__time_duration.sum'] / 1_000_000.0
    df['tensor_core_active_pct'] = df['sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_active']
    df['occupancy_pct'] = df['sm__warps_active.avg.pct_of_peak_sustained_active']
    df['dram_gbps'] = df['dram__bytes.sum.per_second'] / 1e9
    df['dram_read_gb'] = df['dram__bytes_read.sum'] / 1e9
    df['dram_write_gb'] = df['dram__bytes_write.sum'] / 1e9

    agg = {
        'gpu__time_duration.sum': 'sum',
        'time_ms': 'sum',
        'tensor_core_active_pct': 'mean',
        'occupancy_pct': 'mean',
        'dram_gbps': 'mean',
        'dram_read_gb': 'sum',
        'dram_write_gb': 'sum',
        'lts__throughput.avg.pct_of_peak_sustained_elapsed': 'mean'
    }
    for stall in STALL_BINS:
        agg[stall] = 'mean'

    summary = df.groupby('Kernel Name').agg(agg).reset_index()
    summary = summary.rename(columns={
        'Kernel Name': 'kernel_name',
        'gpu__time_duration.sum': 'gpu_time_duration_ns',
        'tensor_core_active_pct': 'tensor_core_active_pct_mean',
        'occupancy_pct': 'occupancy_pct_mean',
        'dram_gbps': 'dram_gbps_mean',
        'dram_read_gb': 'dram_read_gb_total',
        'dram_write_gb': 'dram_write_gb_total',
        'lts__throughput.avg.pct_of_peak_sustained_elapsed': 'l2_throughput_pct_mean'
    })
    summary['time_share_pct'] = summary['time_ms'] / summary['time_ms'].sum() * 100.0

    rename_map = {stall: stall.replace('smsp__average_warps_issue_stalled_', 'stall_').replace('_per_issue_active.ratio', '_ratio') for stall in STALL_BINS}
    summary = summary.rename(columns=rename_map)
    summary = summary.sort_values('time_ms', ascending=False)
    return summary


def save_plots(summary: pd.DataFrame, outdir: Path, top_n: int = 10) -> None:
    plots_dir = outdir / 'plots'
    plots_dir.mkdir(parents=True, exist_ok=True)
    top = summary.head(top_n)

    plt.figure(figsize=(10,6))
    scatter = plt.scatter(top['dram_gbps_mean'], top['tensor_core_active_pct_mean'],
                          s=np.clip(top['time_share_pct'], 1, None)*8,
                          c=top['occupancy_pct_mean'], cmap='viridis')
    for _, row in top.iterrows():
        plt.text(row['dram_gbps_mean'], row['tensor_core_active_pct_mean'], row['kernel_name'][:18], fontsize=7, alpha=0.7)
    plt.colorbar(scatter, label='SM Occupancy (%)')
    plt.xlabel('DRAM Throughput (GB/s)')
    plt.ylabel('Tensor Core Active (% of peak)')
    plt.title('Tensor Utilization vs Memory Throughput')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(plots_dir / 'roofline_tensor_vs_bandwidth.png', dpi=200)
    plt.close()

    stall_cols = [c for c in top.columns if c.startswith('stall_')]
    stall_display = [c for c in stall_cols if any(key in c for key in ['long_scoreboard', 'memory_dependency', 'dispatch', 'tex', 'lg', 'no_instruction', 'wait'])]
    stall_data = top[['kernel_name'] + stall_display].set_index('kernel_name').fillna(0)
    stall_frac = stall_data.div(stall_data.sum(axis=1).replace(0, np.nan), axis=0) * 100
    stall_frac.plot(kind='bar', stacked=True, figsize=(12,6), colormap='tab20')
    plt.ylabel('Warp Stall Composition (%)')
    plt.title('Warp Stall Breakdown (Top Kernels)')
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=7)
    plt.tight_layout()
    plt.savefig(plots_dir / 'warp_stall_breakdown.png', dpi=200)
    plt.close()

    plt.figure(figsize=(10,5))
    plt.bar(top['kernel_name'], top['occupancy_pct_mean'], color='#1f77b4')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('SM Occupancy (%)')
    plt.title('Average SM Occupancy by Kernel')
    plt.tight_layout()
    plt.savefig(plots_dir / 'sm_occupancy.png', dpi=200)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, default=Path('/tmp/ncu_raw.csv'), help='Path to raw CSV exported via ncu --csv --page raw')
    parser.add_argument('--outdir', type=Path, default=Path('docs/benchmarks/ncu'), help='Destination directory')
    parser.add_argument('--metadata', type=Path, default=None, help='Optional JSON file to merge into METADATA.json')
    args = parser.parse_args()

    df = load_raw(args.raw)
    summary = summarise(df)
    args.outdir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.outdir / 'monai_h100_summary.csv', index=False)

    default_meta = {
        "dataset": "GOAT-Scribe-Nsight-HealthcareAI",
        "hardware": "NVIDIA H100",
        "cuda_version": "13.0.2",
        "cutlass_version": "4.3.0",
        "monai_version": "1.5.1",
        "purpose": "Open-source profiling data for clinical AI workloads"
    }
    if args.metadata and args.metadata.exists():
        user_meta = json.loads(args.metadata.read_text())
        default_meta.update(user_meta)
    (args.outdir / 'METADATA.json').write_text(json.dumps(default_meta, indent=2))
    (args.outdir / 'LICENSE').write_text("This dataset is released under the Apache-2.0 license, consistent with the GOAT Scribe repository license.\n")

    save_plots(summary, args.outdir)

    print(f"Wrote summary to {args.outdir / 'monai_h100_summary.csv'}")


if __name__ == '__main__':
    main()
