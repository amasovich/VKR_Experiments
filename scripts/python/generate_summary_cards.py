#!/usr/bin/env python3
"""Generate Markdown summary cards for Chapter 4 artifacts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def fmt(value: str) -> str:
    return value if value != "" else "н/д"


def source_folder(source: str) -> str:
    if source == "hw_plc_s7_1200":
        return "hw_plc_s7_1200"
    if source == "vplc_internal":
        return "vplc_internal"
    return source


def mode_card(mode: dict[str, str], status: dict[str, str] | None) -> str:
    status = status or {}
    source = source_folder(mode["source"])
    stress_note = []
    if "STRESS" in mode["mode_id"]:
        stress_note = [
            "",
            "Для stress-режима статус RED трактуется как достижение или пересечение границы устойчивости при намеренно жёстком deadline, а не как ошибка постановки эксперимента.",
        ]
    lines = [
        f"# SummaryCard: {mode['mode_id']}",
        "",
        "## Паспорт режима",
        "",
        f"- Объект: `{mode['object']}`",
        f"- Источник обработанных данных: `{mode['source']}`",
        f"- T0: `{mode['t0_ms']} ms`",
        f"- Deadline: `{mode['deadline_threshold_ms']} ms`",
        f"- Load level: `{mode['load_level']}`",
        f"- Load passes: `{mode['load_passes']}`",
        f"- Повторов: `{mode['run_count']}`",
        f"- Валидных строк всего: `{mode['rows_ok_total']}`",
        "",
        "## Ключевые KPI",
        "",
        "| KPI | Значение |",
        "|---|---:|",
        f"| median(Tper) | {fmt(mode['Tper_median_of_runs_ms'])} ms |",
        f"| Q99(Tper) | {fmt(mode['Tper_q99_max_of_runs_ms'])} ms |",
        f"| Q99.9(Tper) | {fmt(mode['Tper_q999_max_of_runs_ms'])} ms |",
        f"| Rmiss | {fmt(mode['Rmiss_total'])} |",
        f"| Lburst | {fmt(mode['Lburst_max'])} |",
        "",
        "## Статус",
        "",
        f"- Статус: `{fmt(status.get('status', ''))}`",
        f"- Причины статуса: `{fmt(status.get('reasons', ''))}`",
        f"- Профиль порогов: `{fmt(status.get('threshold_profile_status', ''))}`",
        "",
        "## Ссылки на артефакты",
        "",
        f"- Processed mode metrics: `processed_tables\\{source}\\mode_metrics.csv`",
        f"- Processed run metrics: `processed_tables\\{source}\\run_metrics.csv`",
        f"- Extended run metrics: `processed_tables\\{source}\\run_metrics_extended.csv`",
        f"- RawLogs: `raw_logs\\{source}\\{mode['mode_id']}`",
        "",
        "## Примечание",
        "",
        (
            "Карточка сформирована автоматически по обработанным данным. "
            "Статус GREEN/YELLOW/RED рассчитан по калиброванному профилю "
            "`configs\\mode_thresholds.yaml` для класса умеренно критичного "
            "циклического контура управления без функций ПАЗ/SIL."
        ),
        *stress_note,
        "",
    ]
    return "\n".join(lines)


def comparison_card(pair: dict[str, str]) -> str:
    lines = [
        f"# SummaryCard: {pair['comparison_pair_id']}",
        "",
        "## Пара сравнения",
        "",
        f"- HW PLC режим: `{pair['s7_mode_id']}`",
        f"- VPLC режим: `{pair['vplc_mode_id']}`",
        f"- T0: `{pair['t0_ms']} ms`",
        f"- Deadline: `{pair['deadline_threshold_ms']} ms`",
        f"- Load level: `{pair['load_level']}`",
        f"- Load passes: `{pair['load_passes']}`",
        "",
        "## Сравнение KPI",
        "",
        "| KPI | HW PLC | VPLC | Delta VPLC-HW | Относительная delta |",
        "|---|---:|---:|---:|---:|",
        f"| Q99(Tper), ms | {fmt(pair['s7_q99_ms'])} | {fmt(pair['vplc_q99_ms'])} | {fmt(pair['delta_q99_ms'])} | {fmt(pair['relative_delta_q99_pct'])}% |",
        f"| Q99.9(Tper), ms | {fmt(pair['s7_q999_ms'])} | {fmt(pair['vplc_q999_ms'])} | {fmt(pair['delta_q999_ms'])} | {fmt(pair['relative_delta_q999_pct'])}% |",
        f"| Rmiss | {fmt(pair['s7_rmiss'])} | {fmt(pair['vplc_rmiss'])} | {fmt(pair['delta_rmiss'])} | н/д |",
        f"| Lburst | {fmt(pair['s7_lburst'])} | {fmt(pair['vplc_lburst'])} | {fmt(pair['delta_lburst'])} | н/д |",
        f"| median(Tper), ms | {fmt(pair['s7_median_ms'])} | {fmt(pair['vplc_median_ms'])} | {fmt(pair['delta_median_ms'])} | н/д |",
        "",
        "## Ссылки на артефакты",
        "",
        "- Pair comparison: `processed_tables\\comparison\\s7_vs_vplc_pair_comparison.csv`",
        "- Pair deltas: `processed_tables\\comparison\\s7_vs_vplc_pair_delta.csv`",
        "- Threshold statuses: `processed_tables\\comparison\\threshold_status.csv`",
        "",
        "## Примечание",
        "",
        (
            "Карточка фиксирует численное сопоставление. Интерпретация причин "
            "и практические рекомендации формируются отдельными артефактами Главы 4."
        ),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Markdown summary cards for Chapter 4.")
    parser.add_argument("--comparison-root", type=Path, default=Path("processed_tables/comparison"))
    parser.add_argument("--output-root", type=Path, default=Path("summary_cards"))
    args = parser.parse_args()

    modes = read_csv(args.comparison_root / "mode_summary.csv")
    statuses = by_key(read_csv(args.comparison_root / "threshold_status.csv"), "mode_id")
    pairs = read_csv(args.comparison_root / "s7_vs_vplc_pair_comparison.csv")

    mode_count = 0
    for mode in modes:
        source = source_folder(mode["source"])
        path = args.output_root / source / f"{mode['mode_id']}.md"
        write_text(path, mode_card(mode, statuses.get(mode["mode_id"])))
        mode_count += 1

    pair_count = 0
    for pair in pairs:
        path = args.output_root / "comparison" / f"{pair['comparison_pair_id']}.md"
        write_text(path, comparison_card(pair))
        pair_count += 1

    print(f"wrote mode summary cards: {mode_count}")
    print(f"wrote comparison summary cards: {pair_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
