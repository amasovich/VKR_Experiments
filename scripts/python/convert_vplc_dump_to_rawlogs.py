#!/usr/bin/env python3
"""Convert VPLC dump ring-buffer arrays to RawLogs CSV.

The converter expects a VPLC workload v0.3 dump that contains arrays named
log_sample_index[0], log_Tper_ms[0], etc. It reads vplc_dump_dict.dat and
vplc_dump.dat, decodes values, sorts rows by log_sample_index, and writes
RawLogs compatible with configs/rawlogs_schema_cycle_v0.yaml.

Raw dump files are treated as immutable source artifacts.
"""

from __future__ import annotations

import argparse
import csv
import re
import struct
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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

ARRAY_RE = re.compile(r"^(?P<base>[A-Za-z_][A-Za-z0-9_]*)\[(?P<idx>\d+)\]$")

LOG_FIELDS = {
    "log_sample_index",
    "log_cycle_counter",
    "log_now_ms",
    "log_Tper_ms",
    "log_Jper_ms",
    "log_deadline_miss",
    "log_timing_valid",
    "log_heartbeat",
    "log_workload_accumulator",
    "log_load_level",
    "log_load_passes",
    "log_error_flag",
    "log_quality_flag",
}

MODE_SPECS = {
    "VPLC_L0_IDLE_10_20": {"load_level": 0, "load_passes": 0, "t0_ms": 10.0, "deadline_threshold_ms": 20.0},
    "VPLC_L1_LIGHT_10_20": {"load_level": 1, "load_passes": 32, "t0_ms": 10.0, "deadline_threshold_ms": 20.0},
    "VPLC_L2_MEDIUM_25_35": {"load_level": 2, "load_passes": 128, "t0_ms": 25.0, "deadline_threshold_ms": 35.0},
    "VPLC_L3_HIGH_75_100": {"load_level": 3, "load_passes": 512, "t0_ms": 75.0, "deadline_threshold_ms": 100.0},
    "VPLC_L3_STRESS_75_80": {"load_level": 3, "load_passes": 512, "t0_ms": 75.0, "deadline_threshold_ms": 80.0},
}


@dataclass
class DictEntry:
    name: str
    type_name: str
    size: int


def read_c_string(data: bytes, offset: int) -> tuple[str, int]:
    end = data.index(0, offset)
    return data[offset:end].decode("utf-8", errors="replace"), end + 1


def parse_dict(path: Path) -> list[DictEntry]:
    data = path.read_bytes()
    offset = 8
    entries: list[DictEntry] = []
    while offset < len(data):
        name, offset = read_c_string(data, offset)
        type_name, offset = read_c_string(data, offset)
        size = data[offset]
        offset += 1
        entries.append(DictEntry(name, type_name, size))
    return entries


def decode_raw_value(type_name: str, raw: bytes) -> Any:
    if type_name == "float":
        return struct.unpack("<f", raw)[0]
    if type_name == "double":
        return struct.unpack("<d", raw)[0]
    if type_name == "uint64_t":
        return struct.unpack("<Q", raw)[0]
    if type_name == "int64_t":
        return struct.unpack("<q", raw)[0]
    if type_name == "uint32_t":
        return struct.unpack("<I", raw)[0]
    if type_name == "int32_t":
        return struct.unpack("<i", raw)[0]
    if type_name == "uint16_t":
        return struct.unpack("<H", raw)[0]
    if type_name == "int16_t":
        return struct.unpack("<h", raw)[0]
    if type_name == "uint8_t":
        return raw[0]
    if type_name == "int8_t":
        return struct.unpack("<b", raw)[0]
    if type_name == "bool":
        return bool(raw[0])
    return raw.hex()


def decode_dump(dict_entries: list[DictEntry], dump_path: Path) -> dict[str, Any]:
    data = dump_path.read_bytes()
    expected_len = 8 + sum(entry.size for entry in dict_entries)
    if len(data) != expected_len:
        raise ValueError(f"Unexpected dump length: got {len(data)}, expected {expected_len}")

    values: dict[str, Any] = {}
    offset = 8
    for entry in dict_entries:
        raw = data[offset : offset + entry.size]
        offset += entry.size
        values[entry.name] = decode_raw_value(entry.type_name, raw)
    return values


def fmt(value: Any) -> str:
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


def quality_from_row(timing_valid: Any, quality_flag: Any) -> str:
    if timing_valid is True and quality_flag == 0:
        return "ok"
    if timing_valid is False and quality_flag == 1:
        return "technical_check"
    return "invalid_row"


def extract_log_rows(values: dict[str, Any]) -> list[dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for name, value in values.items():
        match = ARRAY_RE.match(name)
        if not match:
            continue
        base = match.group("base")
        if base not in LOG_FIELDS:
            continue
        idx = int(match.group("idx"))
        rows.setdefault(idx, {})[base] = value

    complete_rows = []
    for idx, row in rows.items():
        if "log_sample_index" not in row:
            continue
        row["_dump_index"] = idx
        complete_rows.append(row)
    complete_rows.sort(key=lambda row: (row["log_sample_index"], row["_dump_index"]))
    return complete_rows


def validate_mode_args(mode_id: str, t0_ms: float, deadline_ms: float, load_level: int, load_passes: int) -> list[str]:
    notes: list[str] = []
    spec = MODE_SPECS.get(mode_id)
    if not spec:
        notes.append("mode_not_in_converter_table")
        return notes
    checks = [
        ("t0_ms", t0_ms, spec["t0_ms"]),
        ("deadline_threshold_ms", deadline_ms, spec["deadline_threshold_ms"]),
        ("load_level", load_level, spec["load_level"]),
        ("load_passes", load_passes, spec["load_passes"]),
    ]
    for name, actual, expected in checks:
        if actual != expected:
            notes.append(f"{name}_mismatch_actual_{actual}_expected_{expected}")
    return notes


def row_to_csv(
    row: dict[str, Any],
    *,
    run_id: str,
    mode_id: str,
    series_id: str,
    t0_ms: float,
    deadline_ms: float,
    run_notes: list[str],
) -> dict[str, str]:
    timing_valid = row.get("log_timing_valid") is True
    quality_flag = int(row.get("log_quality_flag") or 0)
    quality = quality_from_row(timing_valid, quality_flag)
    notes = list(run_notes)
    if not timing_valid:
        notes.append("timing_invalid")

    return {
        "run_id": run_id,
        "mode_id": mode_id,
        "series_id": series_id,
        "object": "vPLC_container",
        "node_id": "VPLC_HOST",
        "sample_index": fmt(row.get("log_sample_index")),
        "cycle_index": fmt(row.get("log_sample_index")),
        "cycle_counter": fmt(row.get("log_cycle_counter")),
        "ts_observe": "",
        "ts_start": fmt(row.get("log_now_ms")),
        "ts_end": "",
        "timestamp_tick_ns": "",
        "timestamp_source": "vplc_internal",
        "t0_ms": fmt(t0_ms),
        "deadline_threshold_ms": fmt(deadline_ms),
        "Tper": fmt(row.get("log_Tper_ms") if timing_valid else None),
        "Jper": fmt(row.get("log_Jper_ms") if timing_valid else None),
        "deadline_miss": bool_to_int(row.get("log_deadline_miss") if timing_valid else None),
        "heartbeat": bool_to_int(row.get("log_heartbeat")),
        "workload_accumulator": fmt(row.get("log_workload_accumulator")),
        "load_level": fmt(row.get("log_load_level")),
        "load_passes": fmt(row.get("log_load_passes")),
        "error_flag": bool_to_int(row.get("log_error_flag")),
        "quality_flag": quality,
        "notes": "; ".join(note for note in notes if note),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert VPLC v0.3 dump ring log to RawLogs CSV.")
    parser.add_argument("--dict", type=Path, required=True, help="Path to vplc_dump_dict.dat")
    parser.add_argument("--dump", type=Path, required=True, help="Path to vplc_dump.dat")
    parser.add_argument("--output-root", type=Path, default=Path("raw_logs/vplc_internal"))
    parser.add_argument("--mode-id", required=True)
    parser.add_argument("--series-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--t0-ms", type=float, required=True)
    parser.add_argument("--deadline-ms", type=float, required=True)
    parser.add_argument("--load-level", type=int, required=True)
    parser.add_argument("--load-passes", type=int, required=True)
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries = parse_dict(args.dict)
    values = decode_dump(entries, args.dump)
    rows = extract_log_rows(values)
    if not rows:
        raise SystemExit("No log_* array rows found in VPLC dump.")

    notes = validate_mode_args(args.mode_id, args.t0_ms, args.deadline_ms, args.load_level, args.load_passes)

    buffer_wrapped = values.get("buffer_wrapped") is True
    freeze_logging = values.get("freeze_logging") is True
    if not buffer_wrapped:
        if not args.allow_partial:
            raise SystemExit("buffer_wrapped is FALSE. Wait for full buffer or use --allow-partial.")
        notes.append("partial_buffer")
    if not freeze_logging:
        notes.append("freeze_logging_not_true")

    output_path = args.output_root / args.mode_id / f"{args.run_id}.csv"
    if not args.dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    row_to_csv(
                        row,
                        run_id=args.run_id,
                        mode_id=args.mode_id,
                        series_id=args.series_id,
                        t0_ms=args.t0_ms,
                        deadline_ms=args.deadline_ms,
                        run_notes=notes,
                    )
                )

    action = "would write" if args.dry_run else "wrote"
    print(f"{action} {len(rows)} rows -> {output_path} [{'; '.join(notes) or 'ok'}]")
    print(f"source observation UTC: {datetime.now(timezone.utc).isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
