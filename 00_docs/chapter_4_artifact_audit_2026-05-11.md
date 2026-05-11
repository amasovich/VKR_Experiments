# Контрольный аудит артефактов Главы 4

Дата проверки: 2026-05-11.

Назначение: проверить полноту пакета артефактов перед коммитом и дальнейшим переносом материалов в текст ВКР.

## Результат проверки

Общий статус: пакет артефактов Главы 4 готов к фиксации.

## Проверка первичных данных

| Источник | Ожидалось | Найдено | Статус |
|---|---:|---:|---|
| `raw_logs\hw_plc_s7_1200\S7_L*` | 25 CSV | 25 CSV | OK |
| `raw_logs\vplc_internal\VPLC_L*` | 25 CSV | 25 CSV | OK |

В `raw_logs\vplc_internal` дополнительно присутствует TECH-папка `VPLC_TECH_CYCLE100_T0_10_D20`. Она не входит в финальную обработку и не мешает, потому что финальные VPLC RawLogs выбираются по шаблону `VPLC_L*`.

## Проверка обработанных таблиц

| Таблица | Количество строк | Статус |
|---|---:|---|
| `processed_tables\comparison\mode_summary.csv` | 10 | OK |
| `processed_tables\comparison\s7_vs_vplc_pair_comparison.csv` | 5 | OK |
| `processed_tables\comparison\s7_vs_vplc_pair_delta.csv` | 5 | OK |
| `processed_tables\comparison\repeatability_metrics.csv` | 60 | OK |
| `processed_tables\comparison\baseline_stress_comparison.csv` | 40 | OK |
| `processed_tables\comparison\data_quality_summary.csv` | 50 | OK |
| `processed_tables\comparison\threshold_status.csv` | 10 | OK |

Профиль порогов в `threshold_status.csv`: `calibrated_for_vkr_chapter_4`.

## Проверка ссылок

Проверены ссылки из:

- `00_docs\chapter_4_handoff.md`;
- `00_docs\chapter_4_artifact_index.md`.

Найдено проверяемых ссылок:

- `chapter_4_handoff.md`: 24;
- `chapter_4_artifact_index.md`: 45.

Отсутствующих файлов по проверяемым ссылкам не найдено.

## Проверка SummaryCards

| Каталог | Ожидалось | Найдено | Статус |
|---|---:|---:|---|
| `summary_cards\hw_plc_s7_1200` | 5 | 5 | OK |
| `summary_cards\vplc_internal` | 5 | 5 | OK |
| `summary_cards\comparison` | 5 | 5 | OK |

Карточки используют профиль `calibrated_for_vkr_chapter_4`.

## Проверка графиков

| Файл | Назначение | Статус |
|---|---|---|
| `fig_4_1_tper_quantiles_by_mode.png` | Q99/Q99.9 `Tper` по режимам с deadline | OK |
| `fig_4_2_deadline_miss_rate_by_mode.png` | доля `deadline_miss` по режимам | OK |
| `fig_4_3_q99_repeatability_by_run.png` | повторяемость `Q99(Tper)` по 5 прогонам | OK |
| `fig_4_4_stress_tper_timeseries_r01.png` | временной ряд `Tper` в stress-режиме | OK |
| `fig_4_5_stress_tper_ecdf_r01.png` | ECDF `Tper` в stress-режиме | OK |
| `fig_4_6_vplc_minus_s7_quantile_delta.png` | дельта `Q99/Q99.9` VPLC - HW PLC | OK |
| `fig_4_7_threshold_status_heatmap.png` | матрица GREEN/YELLOW/RED по критериям | OK |
| `fig_4_8_data_quality_excluded_rows.png` | исключённые строки RawLogs | OK |
| `fig_4_9_tper_boxplot_all_modes.png` | boxplot `Tper` по всем финальным режимам | OK |
| `fig_4_10_high_tper_timeseries_r01.png` | временной ряд `Tper` для рабочего high-load режима | OK |

Манифест графиков: `summary_cards\figures\figures_manifest.csv`.

## Дополнительно найдено по качеству данных

Всего исключённых строк: 74.

Исключения относятся к VPLC-режимам `VPLC_L0_IDLE_10_20`, `VPLC_L1_LIGHT_10_20` и частично `VPLC_L2_MEDIUM_25_35`; причина отражена как `timing_invalid`. Эти строки исключены из KPI и отражены в `data_quality_summary.csv` и графике `fig_4_8_data_quality_excluded_rows.png`.

## Вывод

Для написания Главы 4 ничего критического не отсутствует. Пакет покрывает:

- финальные RawLogs;
- обработанные KPI;
- сравнение S7/VPLC;
- повторяемость;
- baseline/stress;
- качество данных;
- шкалу GREEN/YELLOW/RED;
- SummaryCards;
- графики;
- handoff и текстовые артефакты интерпретации.

Следующий практический шаг: сделать коммит пакета артефактов Главы 4.
