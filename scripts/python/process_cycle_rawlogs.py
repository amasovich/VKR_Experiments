#!/usr/bin/env python3
"""Process cycle RawLogs into run-level and mode-level metric tables.

This script reads CSV files produced from raw cycle logs and writes derived
tables under processed_tables/. It does not modify raw logs.
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
    "rows_ok",
    "rows_excluded",
    "t0_ms",
    "deadline_threshold_ms",
    "load_level",
    "load_passes",
    "Tper_min_ms",
    "Tper_max_ms",
    "Tper_mean_ms",
    "Tper_median_ms",
    "Tper_q95_ms",
    "Tper_q99_ms",
    "Tper_q999_ms",
    "Jper_min_ms",
    "Jper_max_ms",
    "Jper_mean_ms",
    "deadline_miss_count",
    "Rmiss",
    "Lburst",
    "quality_flags",
    "notes",
    "source_file",
]

RUN_EXTENDED_COLUMNS = RUN_COLUMNS + [
    "window_size_rows",
    "window_count",
    "Q99_window_min_ms",
    "Q99_window_max_ms",
    "DQ99_ms",
    "valid_ratio",
    "excluded_ratio",
    "deadline_margin_q99_ms",
    "deadline_margin_q999_ms",
]

MODE_COLUMNS = [
    "object",
    "mode_id",
    "run_count",
    "rows_ok_total",
    "t0_ms",
    "deadline_threshold_ms",
    "load_level",
    "load_passes",
    "Tper_min_ms",
    "Tper_max_ms",
    "Tper_mean_of_runs_ms",
    "Tper_median_of_runs_ms",
    "Tper_q95_max_of_runs_ms",
    "Tper_q99_max_of_runs_ms",
    "Tper_q999_max_of_runs_ms",
    "deadline_miss_total",
    "Rmiss_total",
    "Lburst_max",
    "run_ids",
]


@dataclass
class RunMetrics:
    row: dict[str, str]
    extended_row: dict[str, str]
    mode_id: str
    object_name: str
    run_id: str
    rows_ok: int
    deadline_miss_count: int
    lburst: int
    tper_min: float
    tper_max: float
    tper_mean: float
    tper_median: float
    tper_q95: float
    tper_q99: float
    tper_q999: float


def parse_float(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


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


def window_quantiles(values: list[float], window_size: int, q: float) -> list[float]:
    if window_size <= 0:
        return []
    return [
        quantile_nearest_rank(values[index : index + window_size], q)
        for index in range(0, len(values), window_size)
        if values[index : index + window_size]
    ]


def process_file(path: Path, window_size: int) -> RunMetrics:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise ValueError(f"{path}: empty RawLogs file")

    valid_rows = [row for row in rows if row.get("quality_flag") == "ok" and row.get("Tper")]
    tper_values = [float(row["Tper"]) for row in valid_rows]
    jper_values = [float(row["Jper"]) for row in valid_rows if row.get("Jper")]
    miss_flags = [1 if row.get("deadline_miss") == "1" else 0 for row in valid_rows]

    first = rows[0]
    rows_ok = len(valid_rows)
    rows_excluded = len(rows) - rows_ok
    miss_count = sum(miss_flags)
    rmiss = miss_count / rows_ok if rows_ok else math.nan
    q99 = quantile_nearest_rank(tper_values, 0.99)
    q999 = quantile_nearest_rank(tper_values, 0.999)
    deadline = parse_float(first.get("deadline_threshold_ms", ""))
    q99_windows = window_quantiles(tper_values, window_size, 0.99)
    q99_window_min = min(q99_windows) if q99_windows else math.nan
    q99_window_max = max(q99_windows) if q99_windows else math.nan

    run_row = {
        "object": first.get("object", ""),
        "mode_id": first.get("mode_id", ""),
        "series_id": first.get("series_id", ""),
        "run_id": first.get("run_id", ""),
        "rows_total": fmt(len(rows)),
        "rows_ok": fmt(rows_ok),
        "rows_excluded": fmt(rows_excluded),
        "t0_ms": first.get("t0_ms", ""),
        "deadline_threshold_ms": first.get("deadline_threshold_ms", ""),
        "load_level": first.get("load_level", ""),
        "load_passes": first.get("load_passes", ""),
        "Tper_min_ms": fmt(min(tper_values) if tper_values else None),
        "Tper_max_ms": fmt(max(tper_values) if tper_values else None),
        "Tper_mean_ms": fmt(mean(tper_values) if tper_values else None),
        "Tper_median_ms": fmt(median(tper_values) if tper_values else None),
        "Tper_q95_ms": fmt(quantile_nearest_rank(tper_values, 0.95)),
        "Tper_q99_ms": fmt(q99),
        "Tper_q999_ms": fmt(q999),
        "Jper_min_ms": fmt(min(jper_values) if jper_values else None),
        "Jper_max_ms": fmt(max(jper_values) if jper_values else None),
        "Jper_mean_ms": fmt(mean(jper_values) if jper_values else None),
        "deadline_miss_count": fmt(miss_count),
        "Rmiss": fmt(rmiss),
        "Lburst": fmt(longest_burst(miss_flags)),
        "quality_flags": compact_counts(row.get("quality_flag", "") for row in rows),
        "notes": compact_counts(row.get("notes", "") for row in rows if row.get("notes", "")),
        "source_file": str(path),
    }
    extended_row = {
        **run_row,
        "window_size_rows": fmt(window_size),
        "window_count": fmt(len(q99_windows)),
        "Q99_window_min_ms": fmt(q99_window_min),
        "Q99_window_max_ms": fmt(q99_window_max),
        "DQ99_ms": fmt(q99_window_max - q99_window_min if q99_windows else None),
        "valid_ratio": fmt(rows_ok / len(rows) if rows else None),
        "excluded_ratio": fmt(rows_excluded / len(rows) if rows else None),
        "deadline_margin_q99_ms": fmt(deadline - q99 if deadline is not None and not math.isnan(q99) else None),
        "deadline_margin_q999_ms": fmt(deadline - q999 if deadline is not None and not math.isnan(q999) else None),
    }

    return RunMetrics(
        row=run_row,
        extended_row=extended_row,
        mode_id=run_row["mode_id"],
        object_name=run_row["object"],
        run_id=run_row["run_id"],
        rows_ok=rows_ok,
        deadline_miss_count=miss_count,
        lburst=longest_burst(miss_flags),
        tper_min=min(tper_values) if tper_values else math.nan,
        tper_max=max(tper_values) if tper_values else math.nan,
        tper_mean=mean(tper_values) if tper_values else math.nan,
        tper_median=median(tper_values) if tper_values else math.nan,
        tper_q95=quantile_nearest_rank(tper_values, 0.95),
        tper_q99=quantile_nearest_rank(tper_values, 0.99),
        tper_q999=quantile_nearest_rank(tper_values, 0.999),
    )


def mode_rows(run_metrics: list[RunMetrics]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[RunMetrics]] = defaultdict(list)
    for item in run_metrics:
        grouped[(item.object_name, item.mode_id)].append(item)

    output = []
    for (object_name, mode_id), items in sorted(grouped.items()):
        first = items[0].row
        rows_ok_total = sum(item.rows_ok for item in items)
        miss_total = sum(item.deadline_miss_count for item in items)
        output.append(
            {
                "object": object_name,
                "mode_id": mode_id,
                "run_count": fmt(len(items)),
                "rows_ok_total": fmt(rows_ok_total),
                "t0_ms": first["t0_ms"],
                "deadline_threshold_ms": first["deadline_threshold_ms"],
                "load_level": first["load_level"],
                "load_passes": first["load_passes"],
                "Tper_min_ms": fmt(min(item.tper_min for item in items)),
                "Tper_max_ms": fmt(max(item.tper_max for item in items)),
                "Tper_mean_of_runs_ms": fmt(mean(item.tper_mean for item in items)),
                "Tper_median_of_runs_ms": fmt(median(item.tper_median for item in items)),
                "Tper_q95_max_of_runs_ms": fmt(max(item.tper_q95 for item in items)),
                "Tper_q99_max_of_runs_ms": fmt(max(item.tper_q99 for item in items)),
                "Tper_q999_max_of_runs_ms": fmt(max(item.tper_q999 for item in items)),
                "deadline_miss_total": fmt(miss_total),
                "Rmiss_total": fmt(miss_total / rows_ok_total if rows_ok_total else math.nan),
                "Lburst_max": fmt(max(item.lburst for item in items)),
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
    parser = argparse.ArgumentParser(description="Process cycle RawLogs into derived metric tables.")
    parser.add_argument("--input-root", type=Path, default=Path("raw_logs/hw_plc_s7_1200"))
    parser.add_argument("--output-root", type=Path, default=Path("processed_tables/hw_plc_s7_1200"))
    parser.add_argument("--pattern", default="*.csv")
    parser.add_argument("--window-size", type=int, default=100)
    args = parser.parse_args()

    files = sorted(args.input_root.rglob(args.pattern))
    if not files:
        raise SystemExit(f"No RawLogs CSV files found under {args.input_root}")

    runs = [process_file(path, args.window_size) for path in files]
    run_rows = [item.row for item in sorted(runs, key=lambda item: item.run_id)]
    run_extended_rows = [item.extended_row for item in sorted(runs, key=lambda item: item.run_id)]
    modes = mode_rows(runs)

    run_path = args.output_root / "run_metrics.csv"
    run_extended_path = args.output_root / "run_metrics_extended.csv"
    mode_path = args.output_root / "mode_metrics.csv"
    write_csv(run_path, RUN_COLUMNS, run_rows)
    write_csv(run_extended_path, RUN_EXTENDED_COLUMNS, run_extended_rows)
    write_csv(mode_path, MODE_COLUMNS, modes)

    print(f"processed runs: {len(run_rows)} -> {run_path}")
    print(f"processed extended runs: {len(run_extended_rows)} -> {run_extended_path}")
    print(f"processed modes: {len(modes)} -> {mode_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
