#!/usr/bin/env python3
"""Build comparison tables for Chapter 4 from processed cycle metrics.

The script consumes processed metric CSV files and writes comparison artifacts.
It never modifies RawLogs.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, pstdev


PAIR_COLUMNS = [
    "comparison_pair_id",
    "s7_mode_id",
    "vplc_mode_id",
    "t0_ms",
    "deadline_threshold_ms",
    "load_level",
    "load_passes",
    "s7_rows_ok_total",
    "vplc_rows_ok_total",
    "s7_q99_ms",
    "vplc_q99_ms",
    "delta_q99_ms",
    "relative_delta_q99_pct",
    "s7_q999_ms",
    "vplc_q999_ms",
    "delta_q999_ms",
    "relative_delta_q999_pct",
    "s7_rmiss",
    "vplc_rmiss",
    "delta_rmiss",
    "s7_lburst",
    "vplc_lburst",
    "delta_lburst",
    "s7_median_ms",
    "vplc_median_ms",
    "delta_median_ms",
    "notes",
]

REPEATABILITY_COLUMNS = [
    "object",
    "mode_id",
    "run_count",
    "metric",
    "min",
    "max",
    "mean",
    "median",
    "span",
    "cv",
    "run_values",
]

BASELINE_STRESS_COLUMNS = [
    "object",
    "baseline_mode_id",
    "compared_mode_id",
    "metric",
    "baseline_value",
    "compared_value",
    "delta",
    "relative_delta_pct",
    "interpretation",
]

QUALITY_COLUMNS = [
    "object",
    "mode_id",
    "run_id",
    "rows_total",
    "rows_ok",
    "rows_excluded",
    "valid_ratio",
    "excluded_ratio",
    "quality_flags",
    "notes",
    "source_file",
]

MODE_SUMMARY_COLUMNS = [
    "object",
    "mode_id",
    "run_count",
    "rows_ok_total",
    "t0_ms",
    "deadline_threshold_ms",
    "load_level",
    "load_passes",
    "Tper_median_of_runs_ms",
    "Tper_q99_max_of_runs_ms",
    "Tper_q999_max_of_runs_ms",
    "Rmiss_total",
    "Lburst_max",
    "source",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_float(value: str | None) -> float:
    if value is None or value == "":
        return math.nan
    return float(value)


def fmt(value: float | int | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.9f}".rstrip("0").rstrip(".")
    return str(value)


def relative_delta(new_value: float, reference: float) -> float:
    if math.isnan(new_value) or math.isnan(reference) or reference == 0:
        return math.nan
    return (new_value - reference) / reference * 100.0


def comparison_pair_id(mode_id: str) -> str:
    if mode_id.startswith("S7_"):
        return "PLC_" + mode_id.removeprefix("S7_")
    if mode_id.startswith("VPLC_"):
        return "PLC_" + mode_id.removeprefix("VPLC_")
    return mode_id


def paired_vplc_mode(s7_mode_id: str) -> str:
    return "VPLC_" + s7_mode_id.removeprefix("S7_")


def build_mode_summary(hw_modes: list[dict[str, str]], vplc_modes: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source, items in [("hw_plc_s7_1200", hw_modes), ("vplc_internal", vplc_modes)]:
        for item in items:
            rows.append(
                {
                    "object": item["object"],
                    "mode_id": item["mode_id"],
                    "run_count": item["run_count"],
                    "rows_ok_total": item["rows_ok_total"],
                    "t0_ms": item["t0_ms"],
                    "deadline_threshold_ms": item["deadline_threshold_ms"],
                    "load_level": item["load_level"],
                    "load_passes": item["load_passes"],
                    "Tper_median_of_runs_ms": item["Tper_median_of_runs_ms"],
                    "Tper_q99_max_of_runs_ms": item["Tper_q99_max_of_runs_ms"],
                    "Tper_q999_max_of_runs_ms": item["Tper_q999_max_of_runs_ms"],
                    "Rmiss_total": item["Rmiss_total"],
                    "Lburst_max": item["Lburst_max"],
                    "source": source,
                }
            )
    return sorted(rows, key=lambda row: (row["mode_id"], row["object"]))


def build_pair_comparison(hw_modes: list[dict[str, str]], vplc_modes: list[dict[str, str]]) -> list[dict[str, str]]:
    hw_by_mode = {row["mode_id"]: row for row in hw_modes}
    vplc_by_mode = {row["mode_id"]: row for row in vplc_modes}
    output: list[dict[str, str]] = []

    for s7_mode_id, s7 in sorted(hw_by_mode.items()):
        vplc_mode_id = paired_vplc_mode(s7_mode_id)
        vplc = vplc_by_mode.get(vplc_mode_id)
        if not vplc:
            continue

        s7_q99 = parse_float(s7["Tper_q99_max_of_runs_ms"])
        vplc_q99 = parse_float(vplc["Tper_q99_max_of_runs_ms"])
        s7_q999 = parse_float(s7["Tper_q999_max_of_runs_ms"])
        vplc_q999 = parse_float(vplc["Tper_q999_max_of_runs_ms"])
        s7_rmiss = parse_float(s7["Rmiss_total"])
        vplc_rmiss = parse_float(vplc["Rmiss_total"])
        s7_lburst = parse_float(s7["Lburst_max"])
        vplc_lburst = parse_float(vplc["Lburst_max"])
        s7_median = parse_float(s7["Tper_median_of_runs_ms"])
        vplc_median = parse_float(vplc["Tper_median_of_runs_ms"])

        notes = []
        if s7["t0_ms"] != vplc["t0_ms"] or s7["deadline_threshold_ms"] != vplc["deadline_threshold_ms"]:
            notes.append("mode_parameter_mismatch")
        if s7["load_level"] != vplc["load_level"] or s7["load_passes"] != vplc["load_passes"]:
            notes.append("load_parameter_mismatch")

        output.append(
            {
                "comparison_pair_id": comparison_pair_id(s7_mode_id),
                "s7_mode_id": s7_mode_id,
                "vplc_mode_id": vplc_mode_id,
                "t0_ms": s7["t0_ms"],
                "deadline_threshold_ms": s7["deadline_threshold_ms"],
                "load_level": s7["load_level"],
                "load_passes": s7["load_passes"],
                "s7_rows_ok_total": s7["rows_ok_total"],
                "vplc_rows_ok_total": vplc["rows_ok_total"],
                "s7_q99_ms": fmt(s7_q99),
                "vplc_q99_ms": fmt(vplc_q99),
                "delta_q99_ms": fmt(vplc_q99 - s7_q99),
                "relative_delta_q99_pct": fmt(relative_delta(vplc_q99, s7_q99)),
                "s7_q999_ms": fmt(s7_q999),
                "vplc_q999_ms": fmt(vplc_q999),
                "delta_q999_ms": fmt(vplc_q999 - s7_q999),
                "relative_delta_q999_pct": fmt(relative_delta(vplc_q999, s7_q999)),
                "s7_rmiss": fmt(s7_rmiss),
                "vplc_rmiss": fmt(vplc_rmiss),
                "delta_rmiss": fmt(vplc_rmiss - s7_rmiss),
                "s7_lburst": fmt(s7_lburst),
                "vplc_lburst": fmt(vplc_lburst),
                "delta_lburst": fmt(vplc_lburst - s7_lburst),
                "s7_median_ms": fmt(s7_median),
                "vplc_median_ms": fmt(vplc_median),
                "delta_median_ms": fmt(vplc_median - s7_median),
                "notes": ";".join(notes),
            }
        )
    return output


def stats(values: list[float]) -> dict[str, float]:
    clean = [value for value in values if not math.isnan(value)]
    if not clean:
        return {key: math.nan for key in ["min", "max", "mean", "median", "span", "cv"]}
    avg = mean(clean)
    return {
        "min": min(clean),
        "max": max(clean),
        "mean": avg,
        "median": median(clean),
        "span": max(clean) - min(clean),
        "cv": pstdev(clean) / avg if avg else math.nan,
    }


def build_repeatability(hw_runs: list[dict[str, str]], vplc_runs: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in hw_runs + vplc_runs:
        grouped[(row["object"], row["mode_id"])].append(row)

    metric_columns = {
        "median_Tper": "Tper_median_ms",
        "Q99_Tper": "Tper_q99_ms",
        "Q999_Tper": "Tper_q999_ms",
        "Rmiss": "Rmiss",
        "Lburst": "Lburst",
        "DQ99": "DQ99_ms",
    }
    output: list[dict[str, str]] = []
    for (object_name, mode_id), rows in sorted(grouped.items()):
        for metric_name, column in metric_columns.items():
            values = [parse_float(row.get(column, "")) for row in sorted(rows, key=lambda item: item["run_id"])]
            result = stats(values)
            output.append(
                {
                    "object": object_name,
                    "mode_id": mode_id,
                    "run_count": fmt(len(rows)),
                    "metric": metric_name,
                    "min": fmt(result["min"]),
                    "max": fmt(result["max"]),
                    "mean": fmt(result["mean"]),
                    "median": fmt(result["median"]),
                    "span": fmt(result["span"]),
                    "cv": fmt(result["cv"]),
                    "run_values": ";".join(fmt(value) for value in values),
                }
            )
    return output


def build_baseline_stress(mode_summary: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in mode_summary:
        grouped[row["object"]][row["mode_id"]] = row

    metrics = {
        "median_Tper": "Tper_median_of_runs_ms",
        "Q99_Tper": "Tper_q99_max_of_runs_ms",
        "Q999_Tper": "Tper_q999_max_of_runs_ms",
        "Rmiss": "Rmiss_total",
        "Lburst": "Lburst_max",
    }
    output: list[dict[str, str]] = []
    for object_name, rows_by_mode in sorted(grouped.items()):
        prefix = "S7" if object_name == "HW_PLC" else "VPLC"
        baseline_id = f"{prefix}_L0_IDLE_10_20"
        baseline = rows_by_mode.get(baseline_id)
        if not baseline:
            continue
        for compared_id in sorted(mode_id for mode_id in rows_by_mode if mode_id != baseline_id):
            compared = rows_by_mode[compared_id]
            for metric_name, column in metrics.items():
                base_value = parse_float(baseline.get(column, ""))
                compared_value = parse_float(compared.get(column, ""))
                delta = compared_value - base_value
                rel = relative_delta(compared_value, base_value)
                interpretation = "higher_than_baseline" if delta > 0 else "lower_or_equal_to_baseline"
                output.append(
                    {
                        "object": object_name,
                        "baseline_mode_id": baseline_id,
                        "compared_mode_id": compared_id,
                        "metric": metric_name,
                        "baseline_value": fmt(base_value),
                        "compared_value": fmt(compared_value),
                        "delta": fmt(delta),
                        "relative_delta_pct": fmt(rel),
                        "interpretation": interpretation,
                    }
                )
    return output


def build_quality_summary(hw_runs: list[dict[str, str]], vplc_runs: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in sorted(hw_runs + vplc_runs, key=lambda item: (item["object"], item["mode_id"], item["run_id"])):
        output.append({column: row.get(column, "") for column in QUALITY_COLUMNS})
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Chapter 4 comparison tables.")
    parser.add_argument("--hw-root", type=Path, default=Path("processed_tables/hw_plc_s7_1200"))
    parser.add_argument("--vplc-root", type=Path, default=Path("processed_tables/vplc_internal"))
    parser.add_argument("--output-root", type=Path, default=Path("processed_tables/comparison"))
    args = parser.parse_args()

    hw_modes = read_csv(args.hw_root / "mode_metrics.csv")
    vplc_modes = read_csv(args.vplc_root / "mode_metrics.csv")
    hw_runs = read_csv(args.hw_root / "run_metrics_extended.csv")
    vplc_runs = read_csv(args.vplc_root / "run_metrics_extended.csv")

    mode_summary = build_mode_summary(hw_modes, vplc_modes)
    pair_comparison = build_pair_comparison(hw_modes, vplc_modes)
    repeatability = build_repeatability(hw_runs, vplc_runs)
    baseline_stress = build_baseline_stress(mode_summary)
    quality = build_quality_summary(hw_runs, vplc_runs)

    write_csv(args.output_root / "mode_summary.csv", MODE_SUMMARY_COLUMNS, mode_summary)
    write_csv(args.output_root / "s7_vs_vplc_pair_comparison.csv", PAIR_COLUMNS, pair_comparison)
    write_csv(args.output_root / "s7_vs_vplc_pair_delta.csv", PAIR_COLUMNS, pair_comparison)
    write_csv(args.output_root / "repeatability_metrics.csv", REPEATABILITY_COLUMNS, repeatability)
    write_csv(args.output_root / "baseline_stress_comparison.csv", BASELINE_STRESS_COLUMNS, baseline_stress)
    write_csv(args.output_root / "data_quality_summary.csv", QUALITY_COLUMNS, quality)

    print(f"wrote mode summary: {len(mode_summary)} rows")
    print(f"wrote S7 vs VPLC pairs: {len(pair_comparison)} rows")
    print(f"wrote repeatability: {len(repeatability)} rows")
    print(f"wrote baseline/stress comparisons: {len(baseline_stress)} rows")
    print(f"wrote data quality summary: {len(quality)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
