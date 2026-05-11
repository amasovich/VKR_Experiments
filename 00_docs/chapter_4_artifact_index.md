# Индекс артефактов для Главы 4

Дата формирования: 2026-05-11.

Назначение: рабочий перечень файлов, которые используются при подготовке практической части ВКР после завершения съёма данных на HW PLC S7-1200 и VPLC.

## Первичные данные

| Объект | Каталог | Состав |
|---|---|---|
| HW PLC S7-1200 | `raw_logs\hw_plc_s7_1200` | 25 финальных CSV RawLogs, 5 режимов x 5 повторов |
| VPLC internal timing | `raw_logs\vplc_internal` | 25 финальных CSV RawLogs, 5 режимов x 5 повторов; TECH-прогон хранится отдельно и не включается в финальную обработку |
| VPLC runtime status | `raw_logs\vplc_status` | техническая серия наблюдений `vplc status`, не подменяет финальные `Tper/Jper/deadline_miss` |

## Базовые обработанные таблицы

| Файл | Назначение |
|---|---|
| `processed_tables\hw_plc_s7_1200\run_metrics.csv` | KPI по каждому прогону HW PLC |
| `processed_tables\hw_plc_s7_1200\run_metrics_extended.csv` | расширенные KPI HW PLC: `DQ99`, оконные `Q99`, доли валидных/исключённых строк, запас до deadline |
| `processed_tables\hw_plc_s7_1200\mode_metrics.csv` | агрегирование по режимам HW PLC |
| `processed_tables\vplc_internal\run_metrics.csv` | KPI по каждому прогону VPLC |
| `processed_tables\vplc_internal\run_metrics_extended.csv` | расширенные KPI VPLC: `DQ99`, оконные `Q99`, доли валидных/исключённых строк, запас до deadline |
| `processed_tables\vplc_internal\mode_metrics.csv` | агрегирование по режимам VPLC |

## Сравнительные таблицы

| Файл | Назначение |
|---|---|
| `processed_tables\comparison\mode_summary.csv` | компактная сводка всех 10 режимов: 5 HW PLC и 5 VPLC |
| `processed_tables\comparison\s7_vs_vplc_pair_comparison.csv` | парное сравнение зеркальных режимов S7/VPLC |
| `processed_tables\comparison\s7_vs_vplc_pair_delta.csv` | дельты S7/VPLC по ключевым KPI |
| `processed_tables\comparison\repeatability_metrics.csv` | повторяемость 5 прогонов внутри каждого Mode |
| `processed_tables\comparison\baseline_stress_comparison.csv` | сравнение baseline с нагрузочными и stress-режимами внутри каждого объекта |
| `processed_tables\comparison\data_quality_summary.csv` | качество данных по каждому прогону: валидные/исключённые строки, `quality_flag`, notes |
| `processed_tables\comparison\threshold_status.csv` | оценка GREEN/YELLOW/RED по калиброванному профилю порогов `calibrated_for_vkr_chapter_4` |

## Методические и служебные документы

| Файл | Назначение |
|---|---|
| `00_docs\data_processing_plan_2026-05-10.md` | план обработки данных по методике и перечень недостающих артефактов |
| `00_docs\stage_4_0_log.md` | журнал практического этапа 4.0 |
| `event_journal\event_journal.csv` | машинно-читаемый EventJournal по таблице А.4 методики, сформирован из `stage_4_0_log.md` |
| `00_docs\vplc_workload_rawlogs_plan.md` | план VPLC workload и RawLogs |
| `00_docs\chapter_4_vplc_timing_note.md` | примечание по эволюции способа получения VPLC timing |
| `00_docs\chapter_4_green_yellow_red_scale.md` | зафиксированная инженерная шкала GREEN/YELLOW/RED для Главы 4 |
| `00_docs\chapter_4_handoff.md` | краткий пакет передачи артефактов для написания Главы 4 |
| `00_docs\chapter_4_artifact_audit_2026-05-11.md` | контрольный аудит полноты таблиц, ссылок, SummaryCards и графиков |
| `configs\mode_matrix.yaml` | матрица режимов испытаний |
| `configs\mode_thresholds.yaml` | калиброванный профиль порогов GREEN/YELLOW/RED для Главы 4 |
| `configs\rawlogs_schema_cycle_v0.yaml` | схема RawLogs цикла |

## Скрипты воспроизведения

| Файл | Назначение |
|---|---|
| `scripts\python\process_cycle_rawlogs.py` | расчёт KPI по RawLogs и расширенных KPI |
| `scripts\python\build_event_journal_from_stage_log.py` | формирование `event_journal\event_journal.csv` из журнала этапа 4.0 |
| `scripts\python\build_comparison_tables.py` | формирование сравнительных таблиц для Главы 4 |
| `scripts\python\assign_mode_status.py` | применение калиброванного профиля порогов к режимам |
| `scripts\python\generate_summary_cards.py` | генерация Markdown SummaryCards по режимам и сравнительным парам |
| `scripts\python\generate_chapter4_figures.py` | генерация PNG-графиков для Главы 4 |
| `scripts\python\convert_s7_db_snapshot_to_rawlogs.py` | конвертация Siemens DB snapshot в RawLogs |
| `scripts\python\convert_vplc_dump_to_rawlogs.py` | конвертация VPLC dump ring log в RawLogs |

## Реализация тестовых проектов

| Файл / каталог | Назначение |
|---|---|
| `plc\siemens_s7_1200\scl_sources\README.md` | описание Siemens S7 workload sources |
| `plc\siemens_s7_1200\scl_sources\DB_VKR_S7_Run.scl` | DB Siemens для параметров, состояния и кольцевого лога |
| `plc\siemens_s7_1200\scl_sources\OB123_VKR_WorkloadCycle.scl` | основной cyclic OB Siemens workload |
| `vplc\masc_vplc\st_sources\README.md` | описание VPLC ST sources |
| `vplc\masc_vplc\st_sources\VPLC_WorkloadCycle_v0_3_timing_log.st` | VPLC workload с внутренним timing и ring log |
| `vplc\masc_vplc\st_sources\variables_v0_3_timing_log.yaml` | карта переменных VPLC workload v0.3 |
| `vplc\masc_vplc\vkr_vplc_wl_timing_v03` | VPLC Studio проект финального workload v0.3 |
| `screenshots\VPLC Studio\04` | подтверждение работы VPLC workload v0.3 и заполнения/заморозки ring log |

## SummaryCards

| Каталог | Состав |
|---|---|
| `summary_cards\hw_plc_s7_1200` | 5 карточек режимов HW PLC S7-1200 |
| `summary_cards\vplc_internal` | 5 карточек режимов VPLC с внутренним timing |
| `summary_cards\comparison` | 5 карточек парного сравнения S7/VPLC |

## Графики

| Файл | Назначение |
|---|---|
| `summary_cards\figures\figures_manifest.csv` | перечень графиков, источников данных и назначения |
| `summary_cards\figures\figures_chapter_4_guide.md` | подробное описание графиков, места вставки в Главе 4 и поддерживаемых тезисов |
| `summary_cards\figures\fig_4_1_tper_quantiles_by_mode.png` | Q99/Q99.9 `Tper` по режимам с линией deadline |
| `summary_cards\figures\fig_4_2_deadline_miss_rate_by_mode.png` | доля `deadline_miss` по режимам |
| `summary_cards\figures\fig_4_3_q99_repeatability_by_run.png` | разброс `Q99(Tper)` между пятью повторами |
| `summary_cards\figures\fig_4_4_stress_tper_timeseries_r01.png` | временной ряд `Tper` для stress-режима, повтор R01 |
| `summary_cards\figures\fig_4_5_stress_tper_ecdf_r01.png` | ECDF `Tper` для stress-режима, повтор R01 |
| `summary_cards\figures\fig_4_6_vplc_minus_s7_quantile_delta.png` | дельта `Q99/Q99.9` между VPLC и HW PLC |
| `summary_cards\figures\fig_4_7_threshold_status_heatmap.png` | матрица GREEN/YELLOW/RED по критериям |
| `summary_cards\figures\fig_4_8_data_quality_excluded_rows.png` | исключённые строки RawLogs по режимам |
| `summary_cards\figures\fig_4_9_tper_boxplot_all_modes.png` | boxplot распределений `Tper` по всем финальным режимам |
| `summary_cards\figures\fig_4_10_high_tper_timeseries_r01.png` | временной ряд `Tper` для рабочего high-load режима, повтор R01 |

## Следующие артефакты

Ещё нужно подготовить:

- `00_docs\chapter_4_run_protocol_summary.md`;
- `00_docs\chapter_4_cause_interpretation.md`;
- `00_docs\chapter_4_engineering_recommendations.md`;
- `00_docs\chapter_4_limitations.md`;
