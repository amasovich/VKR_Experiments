#!/usr/bin/env python3
"""Decode VPLC dump snapshot files for format validation.

This helper decodes vplc_dump.dat using vplc_dump_dict.dat. It is intended for
TECH probing of VPLC dump/log capture and does not produce experiment RawLogs.
"""

from __future__ import annotations

import argparse
import csv
import json
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class DictEntry:
    name: str
    type_name: str
    size: int


@dataclass
class DecodedValue:
    name: str
    type_name: str
    size: int
    value: Any
    raw_hex: str


def read_c_string(data: bytes, offset: int) -> tuple[str, int]:
    end = data.index(0, offset)
    return data[offset:end].decode("utf-8", errors="replace"), end + 1


def parse_dict(path: Path) -> tuple[str, list[DictEntry]]:
    data = path.read_bytes()
    if len(data) < 8:
        raise ValueError(f"Dictionary file is too short: {path}")

    offset = 8
    entries: list[DictEntry] = []
    while offset < len(data):
        name, offset = read_c_string(data, offset)
        type_name, offset = read_c_string(data, offset)
        if offset >= len(data):
            raise ValueError(f"Missing size byte after {name!r} in {path}")
        size = data[offset]
        offset += 1
        entries.append(DictEntry(name=name, type_name=type_name, size=size))

    return data[:8].hex(), entries


def decode_raw_value(type_name: str, raw: bytes) -> Any:
    if type_name == "float":
        return struct.unpack("<f", raw)[0]
    if type_name == "double":
        return struct.unpack("<d", raw)[0]
    if type_name == "uint32_t":
        return struct.unpack("<I", raw)[0]
    if type_name == "uint16_t":
        return struct.unpack("<H", raw)[0]
    if type_name == "int16_t":
        return struct.unpack("<h", raw)[0]
    if type_name == "uint64_t":
        return struct.unpack("<Q", raw)[0]
    if type_name == "int64_t":
        return struct.unpack("<q", raw)[0]
    if type_name == "bool":
        return bool(raw[0])
    return raw.hex()


def decode_dump(dict_entries: list[DictEntry], dump_path: Path) -> tuple[str, list[DecodedValue]]:
    data = dump_path.read_bytes()
    expected_len = 8 + sum(entry.size for entry in dict_entries)
    if len(data) != expected_len:
        raise ValueError(f"Unexpected dump length for {dump_path}: got {len(data)}, expected {expected_len}")

    offset = 8
    values: list[DecodedValue] = []
    for entry in dict_entries:
        raw = data[offset : offset + entry.size]
        offset += entry.size
        values.append(
            DecodedValue(
                name=entry.name,
                type_name=entry.type_name,
                size=entry.size,
                value=decode_raw_value(entry.type_name, raw),
                raw_hex=raw.hex(),
            )
        )
    return data[:8].hex(), values


def write_csv(path: Path, values: list[DecodedValue]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "type_name", "size", "value", "raw_hex"])
        writer.writeheader()
        for value in values:
            row = asdict(value)
            row["value"] = str(row["value"])
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dict", type=Path, required=True, help="Path to vplc_dump_dict.dat")
    parser.add_argument("--dump", type=Path, required=True, help="Path to vplc_dump.dat or vplc_dump_prev.dat")
    parser.add_argument("--out-csv", type=Path, help="Optional decoded CSV output path")
    parser.add_argument("--out-json", type=Path, help="Optional decoded JSON output path")
    args = parser.parse_args()

    dict_header, entries = parse_dict(args.dict)
    dump_header, values = decode_dump(entries, args.dump)

    result = {
        "source": {
            "dict_path": str(args.dict),
            "dump_path": str(args.dump),
            "dict_header_hex": dict_header,
            "dump_header_hex": dump_header,
            "entry_count": len(values),
        },
        "values": [asdict(value) for value in values],
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.out_csv:
        args.out_csv.parent.mkdir(parents=True, exist_ok=True)
        write_csv(args.out_csv, values)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
