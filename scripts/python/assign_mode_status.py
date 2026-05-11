#!/usr/bin/env python3
"""Assign calibrated GREEN/YELLOW/RED statuses to processed modes.

The threshold file is intentionally external so engineering criteria can be
reviewed without changing code.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


STATUS_COLUMNS = [
    "object",
    "mode_id",
    "source",
    "t0_ms",
    "deadline_threshold_ms",
    "rows_ok_total",
    "run_count",
    "q99_ms",
    "q999_ms",
    "rmiss",
    "lburst",
    "valid_ratio_min",
    "q99_limit_green",
    "q99_limit_yellow",
    "q999_limit_green",
    "q999_limit_yellow",
    "rmiss_limit_green",
    "rmiss_limit_yellow",
    "lburst_limit_green",
    "lburst_limit_yellow",
    "valid_ratio_green_min",
    "valid_ratio_yellow_min",
    "hard_fail",
    "status",
    "reasons",
    "threshold_profile_status",
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


def read_thresholds(path: Path) -> dict:
    # The file has .yaml extension for the project convention, but is kept as
    # JSON-compatible YAML to avoid adding a parser dependency.
    return json.loads(path.read_text(encoding="utf-8"))


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


def merged_rules(config: dict, mode_id: str) -> dict:
    rules = dict(config["defaults"])
    rules.update(config.get("mode_overrides", {}).get(mode_id, {}))
    return rules


def mode_valid_ratio_min(mode_id: str, quality_rows: list[dict[str, str]]) -> float:
    values = [
        parse_float(row.get("valid_ratio"))
        for row in quality_rows
        if row.get("mode_id") == mode_id
    ]
    values = [value for value in values if not math.isnan(value)]
    return min(values) if values else math.nan


def status_for_mode(mode: dict[str, str], valid_ratio_min: float, config: dict) -> dict[str, str]:
    mode_id = mode["mode_id"]
    rules = merged_rules(config, mode_id)
    deadline = parse_float(mode["deadline_threshold_ms"])
    q99 = parse_float(mode["Tper_q99_max_of_runs_ms"])
    q999 = parse_float(mode["Tper_q999_max_of_runs_ms"])
    rmiss = parse_float(mode["Rmiss_total"])
    lburst = parse_float(mode["Lburst_max"])

    q99_green = deadline * parse_float(str(rules["green_q99_factor_of_deadline"]))
    q99_yellow = deadline * parse_float(str(rules["yellow_q99_factor_of_deadline"]))
    q999_green = deadline * parse_float(str(rules["green_q999_factor_of_deadline"]))
    q999_yellow = deadline * parse_float(str(rules["yellow_q999_factor_of_deadline"]))

    hard_fail_reasons: list[str] = []
    if valid_ratio_min < parse_float(str(rules["hard_fail_valid_ratio_min"])):
        hard_fail_reasons.append("valid_ratio_hard_fail")
    if lburst >= parse_float(str(rules["hard_fail_lburst_min"])):
        hard_fail_reasons.append("lburst_hard_fail")
    if rmiss >= parse_float(str(rules["hard_fail_rmiss_min"])):
        hard_fail_reasons.append("rmiss_hard_fail")

    green_reasons: list[str] = []
    if q99 > q99_green:
        green_reasons.append("q99_above_green")
    if q999 > q999_green:
        green_reasons.append("q999_above_green")
    if rmiss > parse_float(str(rules["green_rmiss_max"])):
        green_reasons.append("rmiss_above_green")
    if lburst > parse_float(str(rules["green_lburst_max"])):
        green_reasons.append("lburst_above_green")
    if valid_ratio_min < parse_float(str(rules["green_valid_ratio_min"])):
        green_reasons.append("valid_ratio_below_green")

    yellow_reasons: list[str] = []
    if q99 > q99_yellow:
        yellow_reasons.append("q99_above_yellow")
    if q999 > q999_yellow:
        yellow_reasons.append("q999_above_yellow")
    if rmiss > parse_float(str(rules["yellow_rmiss_max"])):
        yellow_reasons.append("rmiss_above_yellow")
    if lburst > parse_float(str(rules["yellow_lburst_max"])):
        yellow_reasons.append("lburst_above_yellow")
    if valid_ratio_min < parse_float(str(rules["yellow_valid_ratio_min"])):
        yellow_reasons.append("valid_ratio_below_yellow")

    if hard_fail_reasons or yellow_reasons:
        status = "RED"
        reasons = hard_fail_reasons + yellow_reasons
    elif green_reasons:
        status = "YELLOW"
        reasons = green_reasons
    else:
        status = "GREEN"
        reasons = ["all_green_criteria_met"]

    return {
        "object": mode["object"],
        "mode_id": mode_id,
        "source": mode["source"],
        "t0_ms": mode["t0_ms"],
        "deadline_threshold_ms": mode["deadline_threshold_ms"],
        "rows_ok_total": mode["rows_ok_total"],
        "run_count": mode["run_count"],
        "q99_ms": fmt(q99),
        "q999_ms": fmt(q999),
        "rmiss": fmt(rmiss),
        "lburst": fmt(lburst),
        "valid_ratio_min": fmt(valid_ratio_min),
        "q99_limit_green": fmt(q99_green),
        "q99_limit_yellow": fmt(q99_yellow),
        "q999_limit_green": fmt(q999_green),
        "q999_limit_yellow": fmt(q999_yellow),
        "rmiss_limit_green": fmt(parse_float(str(rules["green_rmiss_max"]))),
        "rmiss_limit_yellow": fmt(parse_float(str(rules["yellow_rmiss_max"]))),
        "lburst_limit_green": fmt(parse_float(str(rules["green_lburst_max"]))),
        "lburst_limit_yellow": fmt(parse_float(str(rules["yellow_lburst_max"]))),
        "valid_ratio_green_min": fmt(parse_float(str(rules["green_valid_ratio_min"]))),
        "valid_ratio_yellow_min": fmt(parse_float(str(rules["yellow_valid_ratio_min"]))),
        "hard_fail": "1" if hard_fail_reasons else "0",
        "status": status,
        "reasons": ";".join(reasons),
        "threshold_profile_status": config.get("status", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Assign calibrated GREEN/YELLOW/RED mode statuses.")
    parser.add_argument("--comparison-root", type=Path, default=Path("processed_tables/comparison"))
    parser.add_argument("--thresholds", type=Path, default=Path("configs/mode_thresholds.yaml"))
    parser.add_argument("--output", type=Path, default=Path("processed_tables/comparison/threshold_status.csv"))
    args = parser.parse_args()

    config = read_thresholds(args.thresholds)
    modes = read_csv(args.comparison_root / "mode_summary.csv")
    quality = read_csv(args.comparison_root / "data_quality_summary.csv")

    rows = [
        status_for_mode(mode, mode_valid_ratio_min(mode["mode_id"], quality), config)
        for mode in modes
    ]
    write_csv(args.output, STATUS_COLUMNS, sorted(rows, key=lambda row: (row["source"], row["mode_id"])))
    print(f"wrote threshold statuses: {len(rows)} -> {args.output}")
    print(f"threshold profile status: {config.get('status', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
