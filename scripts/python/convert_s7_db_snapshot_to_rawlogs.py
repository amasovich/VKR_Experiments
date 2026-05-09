#!/usr/bin/env python3
"""Convert Siemens S7 DB snapshot source files to RawLogs CSV.

The converter treats TIA-exported DB snapshot files as immutable raw source
artifacts. It does not edit the .db files. It extracts DB_VKR_S7_Run.Log.rows
and writes CSV files that follow configs/rawlogs_schema_cycle_v0.yaml.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


RE_ASSIGN = re.compile(r'^\s*(Config|State|Workload|Diagnostics)\.(\w+)\s*:=\s*(.+);\s*$')
RE_ROW = re.compile(r'^\s*Log\.rows\[(\d+)\]\.(\w+)\s*:=\s*(.+);\s*$')
RE_FILE = re.compile(r'^(S7_.+)_R(\d+)\.db$', re.IGNORECASE)

CSV_COLUMNS = [
    "run_id",
    "mode_id",
    "series_id",
    "object",
    "node_id",
    "sample_index",
    "cycle_index",
    "cycle_counter",
    "ts_observe",
    "ts_start",
    "ts_end",
    "timestamp_tick_ns",
    "timestamp_source",
    "t0_ms",
    "deadline_threshold_ms",
    "Tper",
    "Jper",
    "deadline_miss",
    "heartbeat",
    "workload_accumulator",
    "load_level",
    "load_passes",
    "error_flag",
    "quality_flag",
    "notes",
]

MODE_SPECS = {
    "S7_L0_IDLE_10_20": {"load_level": 0, "load_passes": 0, "t0_ms": 10.0, "deadline_threshold_ms": 20.0},
    "S7_L1_LIGHT_10_20": {"load_level": 1, "load_passes": 32, "t0_ms": 10.0, "deadline_threshold_ms": 20.0},
    "S7_L2_MEDIUM_25_35": {"load_level": 2, "load_passes": 128, "t0_ms": 25.0, "deadline_threshold_ms": 35.0},
    "S7_L3_HIGH_75_100": {"load_level": 3, "load_passes": 512, "t0_ms": 75.0, "deadline_threshold_ms": 100.0},
    "S7_L3_STRESS_75_80": {"load_level": 3, "load_passes": 512, "t0_ms": 75.0, "deadline_threshold_ms": 80.0},
}


@dataclass(frozen=True)
class SnapshotIds:
    mode_id: str
    run_number: int
    series_id: str
    run_id: str


def parse_value(raw: str) -> Any:
    value = raw.strip()
    upper = value.upper()
    if upper == "TRUE":
        return True
    if upper == "FALSE":
        return False

    normalized = value.replace("_", "")
    if re.fullmatch(r"[+-]?\d+", normalized):
        return int(normalized)
    if re.fullmatch(r"[+-]?(\d+(\.\d*)?|\.\d+)([Ee][+-]?\d+)?", normalized):
        return float(normalized)
    return value.strip('"')


def format_number(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        return f"{value:.9f}".rstrip("0").rstrip(".")
    return str(value)


def bool_to_int(value: Any) -> str:
    if value is None:
        return ""
    return "1" if bool(value) else "0"


def quality_from_row(row: dict[str, Any]) -> str:
    if row.get("quality_flag") == 0 and row.get("timing_valid") is True:
        return "ok"
    if row.get("quality_flag") == 1 and row.get("timing_valid") is False:
        return "technical_check"
    return "invalid_row"


def parse_snapshot(path: Path) -> tuple[dict[str, dict[str, Any]], dict[int, dict[str, Any]]]:
    sections: dict[str, dict[str, Any]] = {
        "Config": {},
        "State": {},
        "Workload": {},
        "Diagnostics": {},
    }
    rows: dict[int, dict[str, Any]] = {}

    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            assign = RE_ASSIGN.match(line)
            if assign:
                section, name, raw = assign.groups()
                sections[section][name] = parse_value(raw)
                continue

            row_match = RE_ROW.match(line)
            if row_match:
                idx_raw, field, raw = row_match.groups()
                idx = int(idx_raw)
                rows.setdefault(idx, {})[field] = parse_value(raw)

    return sections, rows


def ids_from_filename(path: Path, run_date: str, series_number: int) -> SnapshotIds:
    match = RE_FILE.match(path.name)
    if not match:
        raise ValueError(f"Unsupported snapshot filename: {path.name}")
    mode_id, run_number_raw = match.groups()
    mode_id = mode_id.upper()
    run_number = int(run_number_raw)
    series_id = f"SER_{run_date}_{mode_id}_S{series_number:02d}"
    run_id = f"RUN_{run_date}_{mode_id}_S{series_number:02d}_R{run_number:02d}"
    return SnapshotIds(mode_id=mode_id, run_number=run_number, series_id=series_id, run_id=run_id)


def expected_note(parts: list[str]) -> str:
    return "; ".join(part for part in parts if part)


def select_rows(
    rows: dict[int, dict[str, Any]],
    state: dict[str, Any],
    *,
    allow_partial: bool,
) -> tuple[list[tuple[int, dict[str, Any]]], list[str]]:
    notes: list[str] = []
    wrapped = state.get("buffer_wrapped") is True
    write_index = int(state.get("write_index") or 0)

    if wrapped:
        selected = [(idx, rows[idx]) for idx in sorted(rows)]
    elif allow_partial:
        selected = [(idx, rows[idx]) for idx in sorted(rows) if idx < write_index]
        notes.append("partial_buffer")
    else:
        raise ValueError(
            "State.buffer_wrapped is FALSE. Re-run after full buffer or use --allow-partial."
        )

    selected.sort(key=lambda item: (item[1].get("sample_index", -1), item[0]))
    return selected, notes


def validate_snapshot(
    ids: SnapshotIds,
    sections: dict[str, dict[str, Any]],
    selected_rows: list[tuple[int, dict[str, Any]]],
) -> list[str]:
    notes: list[str] = []
    config = sections["Config"]
    work = sections["Workload"]
    spec = MODE_SPECS.get(ids.mode_id)
    if spec is None:
        notes.append("mode_not_in_converter_table")
        return notes

    checks = [
        ("t0_ms", config.get("T0_ms"), spec["t0_ms"]),
        ("deadline_threshold_ms", config.get("deadline_threshold_ms"), spec["deadline_threshold_ms"]),
        ("load_level", config.get("load_level"), spec["load_level"]),
        ("load_passes_effective", work.get("load_passes_effective"), spec["load_passes"]),
    ]
    for name, actual, expected in checks:
        if actual != expected:
            notes.append(f"{name}_mismatch_actual_{actual}_expected_{expected}")

    if config.get("freeze_logging") is not True:
        notes.append("freeze_logging_not_true")
    if config.get("reset_log_request") is not False:
        notes.append("reset_log_request_not_false")

    samples = [row.get("sample_index") for _, row in selected_rows if row.get("sample_index") is not None]
    if samples:
        samples_sorted = sorted(samples)
        gaps = [
            (prev, cur)
            for prev, cur in zip(samples_sorted, samples_sorted[1:])
            if cur - prev != 1
        ]
        if gaps:
            notes.append(f"sample_index_gaps_{len(gaps)}")

    return notes


def row_to_csv(
    row: dict[str, Any],
    ids: SnapshotIds,
    config: dict[str, Any],
    run_notes: list[str],
) -> dict[str, str]:
    timing_valid = row.get("timing_valid") is True
    quality = quality_from_row(row)
    row_notes = list(run_notes)
    if not timing_valid:
        row_notes.append("timing_invalid")

    return {
        "run_id": ids.run_id,
        "mode_id": ids.mode_id,
        "series_id": ids.series_id,
        "object": "HW_PLC",
        "node_id": "HW_PLC",
        "sample_index": format_number(row.get("sample_index")),
        "cycle_index": format_number(row.get("sample_index")),
        "cycle_counter": format_number(row.get("cycle_counter")),
        "ts_observe": "",
        "ts_start": "",
        "ts_end": "",
        "timestamp_tick_ns": format_number(row.get("nanosecond_of_second")),
        "timestamp_source": "plc_internal_rd_loc_t_nanosecond",
        "t0_ms": format_number(config.get("T0_ms")),
        "deadline_threshold_ms": format_number(config.get("deadline_threshold_ms")),
        "Tper": format_number(row.get("Tper_ms") if timing_valid else None),
        "Jper": format_number(row.get("Jper_ms") if timing_valid else None),
        "deadline_miss": bool_to_int(row.get("deadline_miss") if timing_valid else None),
        "heartbeat": bool_to_int(row.get("heartbeat")),
        "workload_accumulator": format_number(row.get("workload_accumulator")),
        "load_level": format_number(row.get("load_level")),
        "load_passes": format_number(row.get("load_passes")),
        "error_flag": bool_to_int(row.get("error_flag")),
        "quality_flag": quality,
        "notes": expected_note(row_notes),
    }


def convert_one(
    path: Path,
    output_root: Path,
    *,
    run_date: str,
    series_number: int,
    allow_partial: bool,
    dry_run: bool,
) -> tuple[Path, int, list[str]]:
    ids = ids_from_filename(path, run_date, series_number)
    sections, rows = parse_snapshot(path)
    selected_rows, run_notes = select_rows(rows, sections["State"], allow_partial=allow_partial)
    run_notes.extend(validate_snapshot(ids, sections, selected_rows))

    output_path = output_root / "hw_plc_s7_1200" / ids.mode_id / f"{ids.run_id}.csv"

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for _, row in selected_rows:
                writer.writerow(row_to_csv(row, ids, sections["Config"], run_notes))

    return output_path, len(selected_rows), run_notes


def iter_input_files(input_dir: Path, pattern: str) -> list[Path]:
    return sorted(path for path in input_dir.glob(pattern) if path.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert S7-1200 DB_VKR_S7_Run .db snapshots to RawLogs CSV."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("plc/siemens_s7_1200/for_analize"),
        help="Directory with S7_*.db snapshot files.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("raw_logs"),
        help="RawLogs output root.",
    )
    parser.add_argument(
        "--pattern",
        default="S7_*.db",
        help="Input filename glob. Default excludes earlier analyse calibration files.",
    )
    parser.add_argument(
        "--run-date",
        default=datetime.now().strftime("%Y%m%d"),
        help="Date part for SeriesID/RunID, format YYYYMMDD.",
    )
    parser.add_argument(
        "--series-number",
        type=int,
        default=1,
        help="Series number for SeriesID/RunID.",
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Allow conversion when State.buffer_wrapped is FALSE; uses rows[0..write_index-1].",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and report without writing CSV.",
    )
    args = parser.parse_args()

    input_files = iter_input_files(args.input_dir, args.pattern)
    if not input_files:
        raise SystemExit(f"No input files found in {args.input_dir} with pattern {args.pattern}")

    for path in input_files:
        output_path, row_count, notes = convert_one(
            path,
            args.output_root,
            run_date=args.run_date,
            series_number=args.series_number,
            allow_partial=args.allow_partial,
            dry_run=args.dry_run,
        )
        note_text = expected_note(notes) or "ok"
        action = "would write" if args.dry_run else "wrote"
        print(f"{path.name}: {action} {row_count} rows -> {output_path} [{note_text}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
