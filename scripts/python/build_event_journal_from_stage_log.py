#!/usr/bin/env python3
"""Build methodical EventJournal CSV from the human-readable stage 4.0 log."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


FIELDNAMES = [
    "time",
    "event",
    "event_type",
    "run_impact",
    "comment",
    "source_doc",
]


def clean_cell(value: str) -> str:
    return value.strip().replace("<br>", "; ")


def split_markdown_row(line: str) -> list[str]:
    return [clean_cell(cell) for cell in line.strip().strip("|").split("|")]


def classify_event_type(action: str, result: str, note: str) -> str:
    text = f"{action} {result} {note}".lower()
    if any(word in text for word in ["ошибка", "error", "заблок", "permission denied"]):
        return "error"
    if any(word in text for word in ["решение", "зафиксировано", "принято"]):
        return "decision"
    if any(word in text for word in ["измер", "прогон", "rawlogs", "съём", "снят", "сформирован csv"]):
        return "measurement"
    if any(word in text for word in ["обработ", "kpi", "summarycards", "график", "threshold", "таблиц"]):
        return "processing"
    if any(word in text for word in ["провер", "валидац", "аудит", "подтвержд"]):
        return "validation"
    if any(word in text for word in ["установ", "настро", "конфигурац", "snapshot", "снимок", "ip "]):
        return "config"
    if any(word in text for word in ["старт", "запущ", "run"]):
        return "start"
    if any(word in text for word in ["stop", "останов"]):
        return "stop"
    return "note"


def classify_impact(result: str, note: str) -> str:
    text = f"{result} {note}".lower()
    if any(word in text for word in ["заблок", "ошибка", "невозможно", "не выполн"]):
        return "blocking"
    if any(word in text for word in ["требует", "частично", "отлож", "чернов", "warning"]):
        return "medium"
    if any(word in text for word in ["не финальный", "техническ", "tech", "не включается"]):
        return "low"
    return "none"


def parse_stage_log(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_journal = False

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "## Журнал выполнения":
            in_journal = True
            continue
        if not in_journal:
            continue
        if not line.startswith("|"):
            continue
        if line.startswith("|---") or line.startswith("| Дата "):
            continue

        cells = split_markdown_row(line)
        if len(cells) != 5:
            continue
        date, step, action, result, note = cells
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            continue

        comment_parts = [
            f"Пункт: {step}",
            f"Результат: {result}",
        ]
        if note:
            comment_parts.append(note)

        rows.append(
            {
                "time": date,
                "event": action,
                "event_type": classify_event_type(action, result, note),
                "run_impact": classify_impact(result, note),
                "comment": " | ".join(comment_parts),
                "source_doc": str(path).replace("/", "\\"),
            }
        )

    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build EventJournal CSV from stage_4_0_log.md.")
    parser.add_argument("--input", type=Path, default=Path("00_docs/stage_4_0_log.md"))
    parser.add_argument("--output", type=Path, default=Path("event_journal/event_journal.csv"))
    args = parser.parse_args()

    rows = parse_stage_log(args.input)
    write_csv(args.output, rows)
    print(f"wrote event journal rows: {len(rows)} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
