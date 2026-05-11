# Handoff-пакет для написания Главы 4

Дата подготовки: 2026-05-11.

Назначение: кратко зафиксировать, какие артефакты брать в текст Главы 4, какие таблицы и рисунки вставлять, какие выводы допустимо формулировать по текущим данным.

## 1. Текущий статус

Экспериментальный съём на HW PLC Siemens S7-1200 и VPLC завершён. Дальнейшая работа относится к написанию текста, выбору фрагментов таблиц/рисунков и редактуре формулировок.

Пороговая шкала GREEN/YELLOW/RED зафиксирована:

- профиль: `configs\mode_thresholds.yaml`;
- версия: `1.0`;
- статус: `calibrated_for_vkr_chapter_4`;
- класс сценария: умеренно критичный циклический контур управления / технологической автоматики без функций ПАЗ/SIL.

## 2. Основные артефакты

| Группа | Путь | Как использовать |
|---|---|---|
| Индекс артефактов | `00_docs\chapter_4_artifact_index.md` | карта всех файлов главы |
| EventJournal | `event_journal\event_journal.csv` | машинно-читаемый журнал событий по таблице А.4 методики |
| Протокол выполнения | `00_docs\chapter_4_run_protocol_summary.md` | основа для подраздела о порядке эксперимента |
| Интерпретация | `00_docs\chapter_4_cause_interpretation.md` | основа для анализа результатов |
| Рекомендации | `00_docs\chapter_4_engineering_recommendations.md` | основа для инженерных выводов |
| Ограничения | `00_docs\chapter_4_limitations.md` | основа для подраздела об ограничениях |
| Шкала GREEN/YELLOW/RED | `00_docs\chapter_4_green_yellow_red_scale.md` | вставить или адаптировать как таблицу критериев |
| SummaryCards | `summary_cards\...` | режимные карточки и карточки парного сравнения |
| Графики | `summary_cards\figures` | рисунки для визуализации результата |

## 3. Таблицы для переноса в Главу 4

| Таблица | Источник | Рекомендуемое место |
|---|---|---|
| Матрица режимов | `00_docs\chapter_4_run_protocol_summary.md` или `configs\mode_matrix.yaml` | подраздел с планом эксперимента |
| Сводка KPI по режимам | `processed_tables\comparison\mode_summary.csv` | подраздел результатов |
| Парное сравнение S7/VPLC | `processed_tables\comparison\s7_vs_vplc_pair_comparison.csv` | подраздел сравнения платформ |
| Статусы GREEN/YELLOW/RED | `processed_tables\comparison\threshold_status.csv` | подраздел инженерного решения |
| Качество данных | `processed_tables\comparison\data_quality_summary.csv` | подраздел валидации данных |
| Повторяемость | `processed_tables\comparison\repeatability_metrics.csv` | подраздел устойчивости повторов |

## 4. Рисунки для Главы 4

| Рисунок | Файл | Что показывает |
|---|---|---|
| 4.1 | `summary_cards\figures\fig_4_1_tper_quantiles_by_mode.png` | Q99/Q99.9 `Tper` по режимам с линией deadline |
| 4.2 | `summary_cards\figures\fig_4_2_deadline_miss_rate_by_mode.png` | долю `deadline_miss` по режимам |
| 4.3 | `summary_cards\figures\fig_4_3_q99_repeatability_by_run.png` | повторяемость `Q99(Tper)` по пяти прогонам |
| 4.4 | `summary_cards\figures\fig_4_4_stress_tper_timeseries_r01.png` | временной ряд `Tper` в stress-режиме |
| 4.5 | `summary_cards\figures\fig_4_5_stress_tper_ecdf_r01.png` | ECDF распределения `Tper` в stress-режиме |
| 4.6 | `summary_cards\figures\fig_4_6_vplc_minus_s7_quantile_delta.png` | абсолютную дельту `Q99/Q99.9` между VPLC и HW PLC |
| 4.7 | `summary_cards\figures\fig_4_7_threshold_status_heatmap.png` | матрицу GREEN/YELLOW/RED по критериям и режимам |
| 4.8 | `summary_cards\figures\fig_4_8_data_quality_excluded_rows.png` | исключённые строки RawLogs и качество данных |
| 4.9 | `summary_cards\figures\fig_4_9_tper_boxplot_all_modes.png` | распределения `Tper` по всем финальным режимам |
| 4.10 | `summary_cards\figures\fig_4_10_high_tper_timeseries_r01.png` | временной ряд `Tper` в рабочем high-load режиме |

Манифест рисунков: `summary_cards\figures\figures_manifest.csv`.

Для временных рядов выбраны два режима с одинаковым workload (`load_level = 3`, `load_passes = 512`): `L3_HIGH_75_100` показывает рабочий нагруженный режим с запасом до deadline 100 ms, а `L3_STRESS_75_80` показывает пограничный сценарий при deadline 80 ms. Такая пара лучше раскрывает смысл stress-режима, чем набор всех 50 временных рядов.

## 5. Ключевые численные факты

### HW PLC S7-1200

| Режим | Q99, ms | Q99.9, ms | Rmiss | Lburst | Статус |
|---|---:|---:|---:|---:|---|
| `S7_L0_IDLE_10_20` | 1.39 | 1.733 | 0 | 0 | GREEN |
| `S7_L1_LIGHT_10_20` | 7.307 | 7.737 | 0 | 0 | GREEN |
| `S7_L2_MEDIUM_25_35` | 24.819 | 25.464 | 0 | 0 | GREEN |
| `S7_L3_HIGH_75_100` | 83.569 | 86.721 | 0 | 0 | GREEN |
| `S7_L3_STRESS_75_80` | 83.669 | 86.208 | 0.0288 | 1 | RED |

### VPLC

| Режим | Q99, ms | Q99.9, ms | Rmiss | Lburst | Статус |
|---|---:|---:|---:|---:|---|
| `VPLC_L0_IDLE_10_20` | 17 | 27 | 0.005633803 | 1 | RED |
| `VPLC_L1_LIGHT_10_20` | 23 | 30 | 0.00624874 | 1 | RED |
| `VPLC_L2_MEDIUM_25_35` | 45 | 54 | 0.011011011 | 1 | RED |
| `VPLC_L3_HIGH_75_100` | 98 | 105 | 0.0024 | 1 | YELLOW |
| `VPLC_L3_STRESS_75_80` | 97 | 98 | 0.0234 | 1 | RED |

Важно: для `L3_STRESS_75_80` статус RED трактуется как достижение или пересечение границы устойчивости при намеренно жёстком deadline, а не как ошибка эксперимента.

## 6. Рекомендуемые выводы для текста

1. Методика применена к двум объектам сравнения с зеркальной матрицей режимов: HW PLC S7-1200 и VPLC.
2. Полная цепочка артефактов сохранена: Mode, RawLogs, ProcessedTables, SummaryCards, EventJournal и графики.
3. HW PLC в рабочих режимах L0, L1, L2 и L3_HIGH показал GREEN-статус по калиброванной шкале.
4. VPLC удерживает медиану `Tper` близко к заданному `T0`, но имеет более выраженные хвосты распределения, что отражается в `Q99`, `Q99.9` и `Rmiss`.
5. Для выбранного класса сценария VPLC режим `L3_HIGH_75_100` получил YELLOW, то есть может рассматриваться как потенциально применимый при инженерном контроле и наличии резерва.
6. Stress-режимы подтвердили способность методики выявлять границу устойчивости, а не только фиксировать штатные режимы.

## 7. Формулировки, которых лучше избегать

- Не писать, что VPLC “хуже всегда” или “непригоден вообще”: вывод относится к конкретной версии, стенду, workload и классу сценария.
- Не писать, что RED stress-режима является ошибкой эксперимента: это пограничный сценарий.
- Не делать причинные утверждения как доказанные без профилирования ОС и runtime. Корректно писать “вероятная инженерная интерпретация”.
- Не смешивать техническую серию `raw_logs\vplc_status` с финальными VPLC RawLogs `raw_logs\vplc_internal`.

## 8. Минимальный набор файлов для переноса в текст

```text
00_docs\chapter_4_run_protocol_summary.md
00_docs\chapter_4_cause_interpretation.md
00_docs\chapter_4_engineering_recommendations.md
00_docs\chapter_4_limitations.md
00_docs\chapter_4_green_yellow_red_scale.md
processed_tables\comparison\mode_summary.csv
processed_tables\comparison\s7_vs_vplc_pair_comparison.csv
processed_tables\comparison\threshold_status.csv
summary_cards\comparison\*.md
summary_cards\figures\*.png
```

RawLogs остаются первичными артефактами трассируемости и не редактируются вручную.
