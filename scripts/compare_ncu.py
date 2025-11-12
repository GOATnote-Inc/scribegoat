#!/usr/bin/env python3
"""Compare Nsight Compute summary CSVs and report deltas in JSON."""
import argparse
import json
from pathlib import Path

import pandas as pd

KEY_METRICS = [
    "time_share_pct",
    "time_ms",
    "tensor_core_active_pct_mean",
    "occupancy_pct_mean",
    "dram_gbps_mean",
    "l2_throughput_pct_mean",
]

STALL_PREFIX = "stall_"


def load_summary(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "kernel_name" not in df.columns:
        raise ValueError(f"Missing kernel_name column in {path}")
    return df


def compare_frames(ref: pd.DataFrame, other: pd.DataFrame, ref_label: str, other_label: str) -> dict:
    merged = ref.merge(other, on="kernel_name", suffixes=(f"_{ref_label}", f"_{other_label}"))
    comparison = {}
    for _, row in merged.iterrows():
        kernel = row["kernel_name"]
        entry = {}
        for metric in KEY_METRICS:
            a = row.get(f"{metric}_{ref_label}")
            b = row.get(f"{metric}_{other_label}")
            if pd.notna(a) and pd.notna(b):
                entry[metric] = {
                    ref_label: float(a),
                    other_label: float(b),
                    "delta": float(b - a),
                    "delta_pct": float(((b - a) / a * 100) if a else float("inf")),
                }
        stall_cols = [c for c in row.index if c.startswith(STALL_PREFIX) and c.endswith(f"_{ref_label}")]
        stall_metrics = {}
        for sc in stall_cols:
            metric_name = sc.replace(f"_{ref_label}", "")
            a = row[sc]
            b = row.get(f"{metric_name}_{other_label}")
            if pd.notna(a) and pd.notna(b):
                stall_metrics[metric_name] = {
                    ref_label: float(a),
                    other_label: float(b),
                    "delta": float(b - a),
                }
        if stall_metrics:
            entry["stall_ratios"] = stall_metrics
        comparison[kernel] = entry
    return comparison


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("primary", type=Path, help="Reference Nsight summary CSV")
    parser.add_argument("others", nargs="+", type=Path, help="One or more CSVs to compare against the reference")
    parser.add_argument("--top", type=int, default=10, help="Limit comparisons to kernels with top-N time share in the reference")
    args = parser.parse_args()

    ref_df = load_summary(args.primary).copy()
    ref_df = ref_df.sort_values("time_share_pct", ascending=False)
    if args.top > 0:
        keep = ref_df.head(args.top)["kernel_name"].tolist()
        ref_df = ref_df[ref_df["kernel_name"].isin(keep)]

    output = {"reference": args.primary.name, "comparisons": []}

    for other_path in args.others:
        other_df = load_summary(other_path)
        merged = compare_frames(ref_df, other_df, "ref", other_path.stem)
        output["comparisons"].append({
            "against": other_path.name,
            "kernels": merged,
        })

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
