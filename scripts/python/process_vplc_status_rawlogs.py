#!/usr/bin/env python3
"""Process VPLC status TECH CSV files into cycle_exec metric tables.

The input rows are produced by scripts/linux/collect_vplc_status_rawlogs.sh.
They contain runtime-reported cycle_exec_ms from `vplc status`; this script does
not treat cycle_exec_ms as Tper.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Iterable


RUN_COLUMNS = [
    "object",
    "mode_id",
    "series_id",
    "run_id",
    "rows_total",
    "rows_valid",
    "rows_excluded",
    "t0_ms",
    "deadline_threshold_ms",
    "load_level",
    "load_passes",
    "cycle_exec_min_ms",
    "cycle_exec_max_ms",
    "cycle_exec_mean_ms",
    "cycle_exec_median_ms",
    "cycle_exec_q95_ms",
    "cycle_exec_q99_ms",
    "cycle_exec_q999_ms",
    "cycle_exec_over_threshold_count",
    "Rover_exec",
    "Lburst_exec",
    "quality_flags",
    "program_statuses",
    "notes",
    "source_file",
]

MODE_COLUMNS = [
    "object",
    "mode_id",
    "run_count",
    "rows_valid_total",
    "t0_ms",
    "deadline_threshold_ms",
    "load_level",
    "load_passes",
    "cycle_exec_min_ms",
    "cycle_exec_max_ms",
    "cycle_exec_mean_of_runs_ms",
    "cycle_exec_median_of_runs_ms",
    "cycle_exec_q95_max_of_runs_ms",
    "cycle_exec_q99_max_of_runs_ms",
    "cycle_exec_q999_max_of_runs_ms",
    "cycle_exec_over_threshold_total",
    "Rover_exec_total",
    "Lburst_exec_max",
    "run_ids",
]


@dataclass
class RunMetrics:
    row: dict[str, str]
    object_name: str
    mode_id: str
    run_id: str
    rows_valid: int
    over_count: int
    lburst: int
    min_value: float
    max_value: float
    mean_value: float
    median_value: float
    q95: float
    q99: float
    q999: float


def fmt(value: float | int | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.9f}".rstrip("0").rstrip(".")
    return str(value)


def quantile_nearest_rank(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    rank = math.ceil(q * len(ordered))
    rank = max(1, min(rank, len(ordered)))
    return ordered[rank - 1]


def longest_burst(flags: Iterable[int]) -> int:
    best = 0
    current = 0
    for flag in flags:
        if flag:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def compact_counts(values: Iterable[str]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        counts[value or "<empty>"] += 1
    return ";".join(f"{key}:{counts[key]}" for key in sorted(counts))


def parse_float(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def process_file(path: Path) -> RunMetrics:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise ValueError(f"{path}: empty VPLC status CSV")

    for index, row in enumerate(rows):
        if None in row:
            raise ValueError(f"{path}: invalid CSV shape at row {index}; extra columns: {row[None]!r}")

    valid_rows = [
        row
        for row in rows
        if row.get("quality_flag") == "technical_check"
        and row.get("timestamp_source") == "host_log"
        and row.get("cycle_exec_ms")
    ]
    values = [float(row["cycle_exec_ms"]) for row in valid_rows]
    first = rows[0]
    threshold = parse_float(first.get("deadline_threshold_ms", ""))
    over_flags = [1 if threshold is not None and value > threshold else 0 for value in values]
    over_count = sum(over_flags)
    rows_valid = len(valid_rows)

    run_row = {
        "object": first.get("object", ""),
        "mode_id": first.get("mode_id", ""),
        "series_id": first.get("series_id", ""),
        "run_id": first.get("run_id", ""),
        "rows_total": fmt(len(rows)),
        "rows_valid": fmt(rows_valid),
        "rows_excluded": fmt(len(rows) - rows_valid),
        "t0_ms": first.get("t0_ms", ""),
        "deadline_threshold_ms": first.get("deadline_threshold_ms", ""),
        "load_level": first.get("load_level", ""),
        "load_passes": first.get("load_passes", ""),
        "cycle_exec_min_ms": fmt(min(values) if values else None),
        "cycle_exec_max_ms": fmt(max(values) if values else None),
        "cycle_exec_mean_ms": fmt(mean(values) if values else None),
        "cycle_exec_median_ms": fmt(median(values) if values else None),
        "cycle_exec_q95_ms": fmt(quantile_nearest_rank(values, 0.95)),
        "cycle_exec_q99_ms": fmt(quantile_nearest_rank(values, 0.99)),
        "cycle_exec_q999_ms": fmt(quantile_nearest_rank(values, 0.999)),
        "cycle_exec_over_threshold_count": fmt(over_count),
        "Rover_exec": fmt(over_count / rows_valid if rows_valid else math.nan),
        "Lburst_exec": fmt(longest_burst(over_flags)),
        "quality_flags": compact_counts(row.get("quality_flag", "") for row in rows),
        "program_statuses": compact_counts(row.get("program_status", "") for row in rows),
        "notes": compact_counts(row.get("notes", "") for row in rows if row.get("notes", "")),
        "source_file": str(path),
    }

    return RunMetrics(
        row=run_row,
        object_name=run_row["object"],
        mode_id=run_row["mode_id"],
        run_id=run_row["run_id"],
        rows_valid=rows_valid,
        over_count=over_count,
        lburst=longest_burst(over_flags),
        min_value=min(values) if values else math.nan,
        max_value=max(values) if values else math.nan,
        mean_value=mean(values) if values else math.nan,
        median_value=median(values) if values else math.nan,
        q95=quantile_nearest_rank(values, 0.95),
        q99=quantile_nearest_rank(values, 0.99),
        q999=quantile_nearest_rank(values, 0.999),
    )


def mode_rows(run_metrics: list[RunMetrics]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[RunMetrics]] = defaultdict(list)
    for item in run_metrics:
        grouped[(item.object_name, item.mode_id)].append(item)

    output = []
    for (object_name, mode_id), items in sorted(grouped.items()):
        first = items[0].row
        rows_valid_total = sum(item.rows_valid for item in items)
        over_total = sum(item.over_count for item in items)
        output.append(
            {
                "object": object_name,
                "mode_id": mode_id,
                "run_count": fmt(len(items)),
                "rows_valid_total": fmt(rows_valid_total),
                "t0_ms": first["t0_ms"],
                "deadline_threshold_ms": first["deadline_threshold_ms"],
                "load_level": first["load_level"],
                "load_passes": first["load_passes"],
                "cycle_exec_min_ms": fmt(min(item.min_value for item in items)),
                "cycle_exec_max_ms": fmt(max(item.max_value for item in items)),
                "cycle_exec_mean_of_runs_ms": fmt(mean(item.mean_value for item in items)),
                "cycle_exec_median_of_runs_ms": fmt(median(item.median_value for item in items)),
                "cycle_exec_q95_max_of_runs_ms": fmt(max(item.q95 for item in items)),
                "cycle_exec_q99_max_of_runs_ms": fmt(max(item.q99 for item in items)),
                "cycle_exec_q999_max_of_runs_ms": fmt(max(item.q999 for item in items)),
                "cycle_exec_over_threshold_total": fmt(over_total),
                "Rover_exec_total": fmt(over_total / rows_valid_total if rows_valid_total else math.nan),
                "Lburst_exec_max": fmt(max(item.lburst for item in items)),
                "run_ids": ";".join(sorted(item.run_id for item in items)),
            }
        )
    return output


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Process VPLC status TECH CSV into cycle_exec tables.")
    parser.add_argument("--input-root", type=Path, default=Path("raw_logs/vplc_status"))
    parser.add_argument("--output-root", type=Path, default=Path("processed_tables/vplc_status"))
    parser.add_argument("--pattern", default="*.csv")
    args = parser.parse_args()

    files = sorted(args.input_root.rglob(args.pattern))
    if not files:
        raise SystemExit(f"No VPLC status CSV files found under {args.input_root}")

    runs = [process_file(path) for path in files]
    run_rows = [item.row for item in sorted(runs, key=lambda item: item.run_id)]
    modes = mode_rows(runs)

    run_path = args.output_root / "run_metrics.csv"
    mode_path = args.output_root / "mode_metrics.csv"
    write_csv(run_path, RUN_COLUMNS, run_rows)
    write_csv(mode_path, MODE_COLUMNS, modes)

    print(f"processed VPLC status runs: {len(run_rows)} -> {run_path}")
    print(f"processed VPLC status modes: {len(modes)} -> {mode_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
