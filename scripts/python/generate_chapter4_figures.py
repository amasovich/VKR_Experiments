#!/usr/bin/env python3
"""Generate Chapter 4 figures from processed and raw experimental data."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", str(Path(".matplotlib-cache").resolve()))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402


MODE_ORDER = [
    "L0_IDLE_10_20",
    "L1_LIGHT_10_20",
    "L2_MEDIUM_25_35",
    "L3_HIGH_75_100",
    "L3_STRESS_75_80",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_run_metrics(path: Path, source: str) -> list[dict[str, str]]:
    rows = read_csv(path)
    for row in rows:
        row["source"] = source
    return rows


def as_float(value: str) -> float:
    if value == "":
        return 0.0
    return float(value)


def short_mode(mode_id: str) -> str:
    for suffix in MODE_ORDER:
        if mode_id.endswith(suffix):
            return suffix
    return mode_id


def display_mode(label: str) -> str:
    return label.replace("_", "\n", 1)


def object_label(source: str) -> str:
    if source == "hw_plc_s7_1200":
        return "HW PLC S7-1200"
    if source == "vplc_internal":
        return "VPLC"
    return source


def save_figure(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["figure", "source", "purpose"])
        writer.writeheader()
        writer.writerows(rows)


def grouped_modes(mode_summary: list[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    grouped: dict[str, dict[str, dict[str, str]]] = {}
    for row in mode_summary:
        grouped.setdefault(row["source"], {})[short_mode(row["mode_id"])] = row
    return grouped


def first_run_path(run_rows: list[dict[str, str]], source: str, mode_id: str) -> Path:
    matches = [row for row in run_rows if row["source"] == source and row["mode_id"] == mode_id]
    if not matches:
        raise FileNotFoundError(f"no run row for {source} {mode_id}")
    matches.sort(key=lambda row: row["run_id"])
    return Path(matches[0]["source_file"])


def read_tper_series(path: Path) -> list[float]:
    values: list[float] = []
    for row in read_csv(path):
        if row.get("quality_flag") != "ok":
            continue
        value = row.get("Tper", "")
        if value == "":
            continue
        values.append(float(value))
    return values


def plot_quantiles(mode_summary: list[dict[str, str]], output: Path) -> None:
    grouped = grouped_modes(mode_summary)
    labels = MODE_ORDER
    x = list(range(len(labels)))
    width = 0.2

    fig, ax = plt.subplots(figsize=(11, 5.8))
    series = [
        ("hw_plc_s7_1200", "Tper_q99_max_of_runs_ms", "S7 Q99", -1.5 * width),
        ("hw_plc_s7_1200", "Tper_q999_max_of_runs_ms", "S7 Q99.9", -0.5 * width),
        ("vplc_internal", "Tper_q99_max_of_runs_ms", "VPLC Q99", 0.5 * width),
        ("vplc_internal", "Tper_q999_max_of_runs_ms", "VPLC Q99.9", 1.5 * width),
    ]
    for source, field, name, offset in series:
        values = [as_float(grouped[source][label][field]) for label in labels]
        ax.bar([i + offset for i in x], values, width=width, label=name)

    deadlines = [as_float(grouped["hw_plc_s7_1200"][label]["deadline_threshold_ms"]) for label in labels]
    ax.plot(x, deadlines, color="black", marker="o", linewidth=1.5, label="Deadline")
    ax.set_title("Квантили Tper по режимам")
    ax.set_ylabel("мс")
    ax.set_xticks(x)
    ax.set_xticklabels([display_mode(label) for label in labels], fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncols=3, fontsize=8)
    save_figure(output / "fig_4_1_tper_quantiles_by_mode.png")


def plot_deadline_miss(mode_summary: list[dict[str, str]], output: Path) -> None:
    grouped = grouped_modes(mode_summary)
    labels = MODE_ORDER
    x = list(range(len(labels)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10.5, 5))
    s7 = [as_float(grouped["hw_plc_s7_1200"][label]["Rmiss_total"]) * 100.0 for label in labels]
    vplc = [as_float(grouped["vplc_internal"][label]["Rmiss_total"]) * 100.0 for label in labels]
    ax.bar([i - width / 2 for i in x], s7, width=width, label="HW PLC S7-1200")
    ax.bar([i + width / 2 for i in x], vplc, width=width, label="VPLC")
    ax.set_title("Доля deadline_miss по режимам")
    ax.set_ylabel("% строк")
    ax.set_xticks(x)
    ax.set_xticklabels([display_mode(label) for label in labels], fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    save_figure(output / "fig_4_2_deadline_miss_rate_by_mode.png")


def plot_repeatability(run_rows: list[dict[str, str]], output: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 5.5))
    base_positions = {label: idx for idx, label in enumerate(MODE_ORDER)}
    offsets = {"hw_plc_s7_1200": -0.16, "vplc_internal": 0.16}
    markers = {"hw_plc_s7_1200": "o", "vplc_internal": "s"}

    for source in ["hw_plc_s7_1200", "vplc_internal"]:
        xs: list[float] = []
        ys: list[float] = []
        for row in run_rows:
            if row["source"] != source:
                continue
            mode = short_mode(row["mode_id"])
            if mode not in base_positions:
                continue
            xs.append(base_positions[mode] + offsets[source])
            ys.append(as_float(row["Tper_q99_ms"]))
        ax.scatter(xs, ys, label=object_label(source), marker=markers[source], alpha=0.8)

    ax.set_title("Повторяемость Q99(Tper) по 5 прогонам каждого режима")
    ax.set_ylabel("Q99(Tper), мс")
    ax.set_xticks(list(base_positions.values()))
    ax.set_xticklabels([display_mode(label) for label in MODE_ORDER], fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    save_figure(output / "fig_4_3_q99_repeatability_by_run.png")


def plot_stress_timeseries(run_rows: list[dict[str, str]], output: Path) -> None:
    s7 = read_tper_series(first_run_path(run_rows, "hw_plc_s7_1200", "S7_L3_STRESS_75_80"))
    vplc = read_tper_series(first_run_path(run_rows, "vplc_internal", "VPLC_L3_STRESS_75_80"))
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(range(len(s7)), s7, linewidth=1, label="HW PLC S7-1200 R01")
    ax.plot(range(len(vplc)), vplc, linewidth=1, label="VPLC R01")
    ax.axhline(80, color="black", linewidth=1.2, linestyle="--", label="Deadline 80 ms")
    ax.set_title("Tper во времени: режим L3_STRESS_75_80, повтор R01")
    ax.set_xlabel("sample_index")
    ax.set_ylabel("Tper, мс")
    ax.grid(alpha=0.25)
    ax.legend()
    save_figure(output / "fig_4_4_stress_tper_timeseries_r01.png")


def plot_high_timeseries(run_rows: list[dict[str, str]], output: Path) -> None:
    s7 = read_tper_series(first_run_path(run_rows, "hw_plc_s7_1200", "S7_L3_HIGH_75_100"))
    vplc = read_tper_series(first_run_path(run_rows, "vplc_internal", "VPLC_L3_HIGH_75_100"))
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(range(len(s7)), s7, linewidth=1, label="HW PLC S7-1200 R01")
    ax.plot(range(len(vplc)), vplc, linewidth=1, label="VPLC R01")
    ax.axhline(100, color="black", linewidth=1.2, linestyle="--", label="Deadline 100 ms")
    ax.set_title("Tper во времени: режим L3_HIGH_75_100, повтор R01")
    ax.set_xlabel("sample_index")
    ax.set_ylabel("Tper, мс")
    ax.grid(alpha=0.25)
    ax.legend()
    save_figure(output / "fig_4_10_high_tper_timeseries_r01.png")


def plot_stress_ecdf(run_rows: list[dict[str, str]], output: Path) -> None:
    series = [
        ("HW PLC S7-1200", read_tper_series(first_run_path(run_rows, "hw_plc_s7_1200", "S7_L3_STRESS_75_80"))),
        ("VPLC", read_tper_series(first_run_path(run_rows, "vplc_internal", "VPLC_L3_STRESS_75_80"))),
    ]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    for label, values in series:
        values = sorted(values)
        y = [(idx + 1) / len(values) for idx in range(len(values))]
        ax.plot(values, y, label=label)
    ax.axvline(80, color="black", linewidth=1.2, linestyle="--", label="Deadline 80 ms")
    ax.set_title("ECDF Tper: режим L3_STRESS_75_80, повтор R01")
    ax.set_xlabel("Tper, мс")
    ax.set_ylabel("F(Tper)")
    ax.grid(alpha=0.25)
    ax.legend()
    save_figure(output / "fig_4_5_stress_tper_ecdf_r01.png")


def plot_pair_delta(pair_rows: list[dict[str, str]], output: Path) -> None:
    labels = [short_mode(row["s7_mode_id"]) for row in pair_rows]
    x = list(range(len(labels)))
    width = 0.35
    q99 = [as_float(row["delta_q99_ms"]) for row in pair_rows]
    q999 = [as_float(row["delta_q999_ms"]) for row in pair_rows]

    fig, ax = plt.subplots(figsize=(10.8, 5))
    ax.bar([i - width / 2 for i in x], q99, width=width, label="Delta Q99")
    ax.bar([i + width / 2 for i in x], q999, width=width, label="Delta Q99.9")
    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("Дельта квантилей Tper: VPLC - HW PLC")
    ax.set_ylabel("мс")
    ax.set_xticks(x)
    ax.set_xticklabels([display_mode(label) for label in labels], fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    save_figure(output / "fig_4_6_vplc_minus_s7_quantile_delta.png")


def criterion_status(row: dict[str, str], metric: str) -> int:
    if metric == "Q99":
        value = as_float(row["q99_ms"])
        green = as_float(row["q99_limit_green"])
        yellow = as_float(row["q99_limit_yellow"])
        return 0 if value <= green else 1 if value <= yellow else 2
    if metric == "Q99.9":
        value = as_float(row["q999_ms"])
        green = as_float(row["q999_limit_green"])
        yellow = as_float(row["q999_limit_yellow"])
        return 0 if value <= green else 1 if value <= yellow else 2
    if metric == "Rmiss":
        value = as_float(row["rmiss"])
        green = as_float(row["rmiss_limit_green"])
        yellow = as_float(row["rmiss_limit_yellow"])
        return 0 if value <= green else 1 if value <= yellow else 2
    if metric == "Lburst":
        value = as_float(row["lburst"])
        green = as_float(row["lburst_limit_green"])
        yellow = as_float(row["lburst_limit_yellow"])
        return 0 if value <= green else 1 if value <= yellow else 2
    if metric == "valid_ratio":
        value = as_float(row["valid_ratio_min"])
        green = as_float(row["valid_ratio_green_min"])
        yellow = as_float(row["valid_ratio_yellow_min"])
        return 0 if value >= green else 1 if value >= yellow else 2
    raise ValueError(metric)


def plot_status_heatmap(status_rows: list[dict[str, str]], output: Path) -> None:
    metrics = ["Q99", "Q99.9", "Rmiss", "Lburst", "valid_ratio"]
    rows = sorted(status_rows, key=lambda row: (row["source"], row["mode_id"]))
    matrix = [[criterion_status(row, metric) for metric in metrics] for row in rows]
    labels = [row["mode_id"].replace("S7_", "").replace("VPLC_", "") for row in rows]

    fig, ax = plt.subplots(figsize=(8.8, 6.2))
    cmap = ListedColormap(["#4caf50", "#f9c74f", "#d62828"])
    image = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=2, aspect="auto")
    ax.set_title("Матрица статусов критериев GREEN/YELLOW/RED")
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metrics)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    for y, row_values in enumerate(matrix):
        for x, value in enumerate(row_values):
            ax.text(x, y, ["G", "Y", "R"][value], ha="center", va="center", color="black", fontsize=8)
    cbar = fig.colorbar(image, ax=ax, ticks=[0, 1, 2])
    cbar.ax.set_yticklabels(["GREEN", "YELLOW", "RED"])
    save_figure(output / "fig_4_7_threshold_status_heatmap.png")


def plot_data_quality(data_quality: list[dict[str, str]], output: Path) -> None:
    totals: dict[str, int] = {}
    for row in data_quality:
        totals[row["mode_id"]] = totals.get(row["mode_id"], 0) + int(row["rows_excluded"])

    labels = [f"S7_{label}" for label in MODE_ORDER] + [f"VPLC_{label}" for label in MODE_ORDER]
    values = [totals.get(label, 0) for label in labels]

    fig, ax = plt.subplots(figsize=(11.5, 5))
    colors = ["#4c78a8"] * len(MODE_ORDER) + ["#f58518"] * len(MODE_ORDER)
    ax.bar(range(len(labels)), values, color=colors)
    ax.set_title("Исключённые строки RawLogs по режимам")
    ax.set_ylabel("rows_excluded")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([label.replace("S7_", "S7\n").replace("VPLC_", "VPLC\n") for label in labels], fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    save_figure(output / "fig_4_8_data_quality_excluded_rows.png")


def plot_tper_boxplot(run_rows: list[dict[str, str]], output: Path) -> None:
    series: list[list[float]] = []
    labels: list[str] = []
    for source, prefix in [("hw_plc_s7_1200", "S7"), ("vplc_internal", "VPLC")]:
        for mode in MODE_ORDER:
            mode_id = f"{prefix}_{mode}"
            values: list[float] = []
            for row in run_rows:
                if row["source"] == source and row["mode_id"] == mode_id:
                    values.extend(read_tper_series(Path(row["source_file"])))
            if values:
                series.append(values)
                labels.append(f"{prefix}\n{display_mode(mode)}")

    fig, ax = plt.subplots(figsize=(13, 5.8))
    ax.boxplot(series, showfliers=False)
    ax.set_title("Распределение Tper по всем финальным RawLogs")
    ax.set_ylabel("Tper, мс")
    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels, fontsize=7)
    ax.grid(axis="y", alpha=0.25)
    save_figure(output / "fig_4_9_tper_boxplot_all_modes.png")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Chapter 4 figures.")
    parser.add_argument("--comparison-root", type=Path, default=Path("processed_tables/comparison"))
    parser.add_argument("--hw-run-metrics", type=Path, default=Path("processed_tables/hw_plc_s7_1200/run_metrics.csv"))
    parser.add_argument("--vplc-run-metrics", type=Path, default=Path("processed_tables/vplc_internal/run_metrics.csv"))
    parser.add_argument("--output-root", type=Path, default=Path("summary_cards/figures"))
    args = parser.parse_args()

    mode_summary = read_csv(args.comparison_root / "mode_summary.csv")
    pair_rows = read_csv(args.comparison_root / "s7_vs_vplc_pair_comparison.csv")
    status_rows = read_csv(args.comparison_root / "threshold_status.csv")
    data_quality = read_csv(args.comparison_root / "data_quality_summary.csv")
    run_rows = read_run_metrics(args.hw_run_metrics, "hw_plc_s7_1200")
    run_rows += read_run_metrics(args.vplc_run_metrics, "vplc_internal")

    plot_quantiles(mode_summary, args.output_root)
    plot_deadline_miss(mode_summary, args.output_root)
    plot_repeatability(run_rows, args.output_root)
    plot_stress_timeseries(run_rows, args.output_root)
    plot_high_timeseries(run_rows, args.output_root)
    plot_stress_ecdf(run_rows, args.output_root)
    plot_pair_delta(pair_rows, args.output_root)
    plot_status_heatmap(status_rows, args.output_root)
    plot_data_quality(data_quality, args.output_root)
    plot_tper_boxplot(run_rows, args.output_root)

    manifest_rows = [
        {
            "figure": "fig_4_1_tper_quantiles_by_mode.png",
            "source": "processed_tables\\comparison\\mode_summary.csv",
            "purpose": "Сравнить Q99/Q99.9 Tper с deadline по всем режимам",
        },
        {
            "figure": "fig_4_2_deadline_miss_rate_by_mode.png",
            "source": "processed_tables\\comparison\\mode_summary.csv",
            "purpose": "Показать долю deadline_miss по режимам",
        },
        {
            "figure": "fig_4_3_q99_repeatability_by_run.png",
            "source": "processed_tables\\hw_plc_s7_1200\\run_metrics.csv; processed_tables\\vplc_internal\\run_metrics.csv",
            "purpose": "Показать разброс Q99 между пятью повторами",
        },
        {
            "figure": "fig_4_4_stress_tper_timeseries_r01.png",
            "source": "RawLogs R01 для S7_L3_STRESS_75_80 и VPLC_L3_STRESS_75_80",
            "purpose": "Показать временную форму Tper в stress-режиме",
        },
        {
            "figure": "fig_4_5_stress_tper_ecdf_r01.png",
            "source": "RawLogs R01 для S7_L3_STRESS_75_80 и VPLC_L3_STRESS_75_80",
            "purpose": "Показать распределение Tper в stress-режиме",
        },
        {
            "figure": "fig_4_10_high_tper_timeseries_r01.png",
            "source": "RawLogs R01 для S7_L3_HIGH_75_100 и VPLC_L3_HIGH_75_100",
            "purpose": "Показать временную форму Tper в рабочем high-load режиме с запасом до deadline",
        },
        {
            "figure": "fig_4_6_vplc_minus_s7_quantile_delta.png",
            "source": "processed_tables\\comparison\\s7_vs_vplc_pair_comparison.csv",
            "purpose": "Показать абсолютную дельту Q99/Q99.9 между VPLC и HW PLC",
        },
        {
            "figure": "fig_4_7_threshold_status_heatmap.png",
            "source": "processed_tables\\comparison\\threshold_status.csv",
            "purpose": "Показать, какие критерии дают GREEN/YELLOW/RED по каждому режиму",
        },
        {
            "figure": "fig_4_8_data_quality_excluded_rows.png",
            "source": "processed_tables\\comparison\\data_quality_summary.csv",
            "purpose": "Показать исключённые строки RawLogs и прозрачность качества данных",
        },
        {
            "figure": "fig_4_9_tper_boxplot_all_modes.png",
            "source": "RawLogs финальных режимов S7 и VPLC",
            "purpose": "Показать распределения Tper по всем режимам без выбросов на boxplot",
        },
    ]
    write_manifest(args.output_root / "figures_manifest.csv", manifest_rows)
    print(f"wrote figures -> {args.output_root}")
    print(f"wrote manifest -> {args.output_root / 'figures_manifest.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
