# VKR_Experiments

Репозиторий содержит экспериментальные материалы выпускной квалификационной работы:

**«Методика оценки детерминизма и стабильности цикла управления виртуальных программируемых логических контроллеров в контейнерной среде в сравнении с аппаратными контроллерами»**.

Репозиторий предназначен для воспроизводимого хранения стендовых конфигураций, исходных программ PLC/VPLC, первичных журналов измерений, обработанных таблиц, графиков и итоговых артефактов практической части ВКР.

## Что проверялось

В эксперименте сравнивались два объекта:

| Объект | Обозначение | Назначение |
|---|---|---|
| Siemens S7-1200 CPU 1215C | `HW_PLC` | аппаратный PLC как эталонная точка сравнения |
| MASC/VPLC MAX Automation на mini-PC | `vPLC_container` / `VPLC_HOST` | виртуальный PLC на вычислительном узле |

Сравнение выполнялось по методике оценки детерминизма и стабильности цикла управления. Основной предмет анализа:

- фактический период цикла `Tper`;
- джиттер периода `Jper`;
- пропуск deadline `deadline_miss`;
- доля пропусков `Rmiss`;
- максимальная серия нарушений `Lburst`;
- квантили `Q99(Tper)` и `Q99.9(Tper)`;
- повторяемость между прогонами;
- качество данных и исключённые строки.

## Режимы эксперимента

Финальная матрица включает 5 зеркальных режимов для HW PLC и VPLC:

| Режим | T0, ms | Deadline, ms | Load level | Load passes | Назначение |
|---|---:|---:|---:|---:|---|
| `L0_IDLE_10_20` | 10 | 20 | 0 | 0 | baseline / idle |
| `L1_LIGHT_10_20` | 10 | 20 | 1 | 32 | лёгкая нагрузка |
| `L2_MEDIUM_25_35` | 25 | 35 | 2 | 128 | средняя нагрузка |
| `L3_HIGH_75_100` | 75 | 100 | 3 | 512 | высокая рабочая нагрузка |
| `L3_STRESS_75_80` | 75 | 80 | 3 | 512 | stress-режим / граница устойчивости |

Для каждого режима выполнено 5 повторов по 1000 строк RawLogs.

## Быстрый маршрут по репозиторию

Для проверки результатов Главы 4 начинать лучше с этих файлов:

| Файл | Назначение |
|---|---|
| `00_docs\chapter_4_handoff.md` | краткий пакет передачи артефактов для написания Главы 4 |
| `00_docs\chapter_4_artifact_index.md` | индекс всех ключевых артефактов |
| `00_docs\chapter_4_artifact_audit_2026-05-11.md` | контрольный аудит полноты таблиц, графиков и ссылок |
| `00_docs\chapter_4_green_yellow_red_scale.md` | инженерная шкала GREEN/YELLOW/RED |
| `processed_tables\comparison\mode_summary.csv` | сводка KPI по всем режимам |
| `processed_tables\comparison\s7_vs_vplc_pair_comparison.csv` | парное сравнение HW PLC и VPLC |
| `processed_tables\comparison\threshold_status.csv` | статусы GREEN/YELLOW/RED |
| `summary_cards\figures\figures_chapter_4_guide.md` | описание графиков и рекомендации по вставке в текст |

## Структура каталогов

| Каталог | Содержимое |
|---|---|
| `00_docs` | рабочие документы, решения, журнал этапа 4.0, handoff и пояснения для Главы 4 |
| `configs` | конфигурационные снимки, manifest, матрица режимов, профиль workload, профиль порогов |
| `event_journal` | машинно-читаемый EventJournal по методике |
| `plc\siemens_s7_1200` | материалы Siemens S7-1200, SCL sources, DB snapshots и проверки |
| `vplc\masc_vplc` | материалы MASC/VPLC, ST sources, проекты VPLC Studio, проверки и планы |
| `raw_logs` | первичные журналы измерений |
| `processed_tables` | обработанные таблицы KPI |
| `summary_cards` | итоговые карточки режимов, сравнительные карточки и графики |
| `scripts\python` | скрипты конвертации, обработки, сравнения, статусов, карточек, графиков и EventJournal |
| `scripts\windows` | PowerShell-скрипты запуска и сбора данных |
| `scripts\linux` | Bash-скрипты для узла VPLC |
| `screenshots` | скриншоты проверки VPLC Studio и других этапов |
| `archive` | архивные/исходные справочные материалы, если включены в публикационный набор |

## Первичные данные

Финальные RawLogs находятся в:

```text
raw_logs\hw_plc_s7_1200
raw_logs\vplc_internal
```

Ожидаемый состав финальной серии:

```text
raw_logs\hw_plc_s7_1200\S7_L*      -> 25 CSV
raw_logs\vplc_internal\VPLC_L*     -> 25 CSV
```

Технические VPLC-прогоны, если присутствуют, не входят в финальную обработку и отделены от режимов `VPLC_L*`.

RawLogs являются первичными артефактами трассируемости и не редактируются вручную.

## Обработанные таблицы

Ключевые таблицы:

```text
processed_tables\hw_plc_s7_1200\run_metrics.csv
processed_tables\hw_plc_s7_1200\run_metrics_extended.csv
processed_tables\hw_plc_s7_1200\mode_metrics.csv

processed_tables\vplc_internal\run_metrics.csv
processed_tables\vplc_internal\run_metrics_extended.csv
processed_tables\vplc_internal\mode_metrics.csv

processed_tables\comparison\mode_summary.csv
processed_tables\comparison\s7_vs_vplc_pair_comparison.csv
processed_tables\comparison\s7_vs_vplc_pair_delta.csv
processed_tables\comparison\repeatability_metrics.csv
processed_tables\comparison\baseline_stress_comparison.csv
processed_tables\comparison\data_quality_summary.csv
processed_tables\comparison\threshold_status.csv
```

## Графики

Графики для Главы 4 лежат в:

```text
summary_cards\figures
```

Описание всех графиков:

```text
summary_cards\figures\figures_chapter_4_guide.md
```

Минимальный рекомендуемый набор для основного текста:

1. `fig_4_1_tper_quantiles_by_mode.png`;
2. `fig_4_2_deadline_miss_rate_by_mode.png`;
3. `fig_4_6_vplc_minus_s7_quantile_delta.png`;
4. `fig_4_7_threshold_status_heatmap.png`;
5. `fig_4_8_data_quality_excluded_rows.png`.

Дополнительно для high-load/stress-сравнения:

- `fig_4_10_high_tper_timeseries_r01.png`;
- `fig_4_4_stress_tper_timeseries_r01.png`.

## Инженерная шкала GREEN/YELLOW/RED

Пороговый профиль:

```text
configs\mode_thresholds.yaml
```

Статус профиля:

```text
calibrated_for_vkr_chapter_4
```

Класс сценария:

```text
умеренно критичный циклический контур управления / технологической автоматики без функций ПАЗ/SIL
```

Табличное описание шкалы:

```text
00_docs\chapter_4_green_yellow_red_scale.md
```

Для stress-режима `L3_STRESS_75_80` статус RED трактуется как достижение или пересечение границы устойчивости при намеренно жёстком deadline, а не как ошибка эксперимента.

## EventJournal

Человекочитаемый журнал этапа:

```text
00_docs\stage_4_0_log.md
```

Машинно-читаемый EventJournal по таблице А.4 методики:

```text
event_journal\event_journal.csv
```

EventJournal формируется из журнала этапа 4.0 скриптом:

```powershell
.\.venv\Scripts\python.exe scripts\python\build_event_journal_from_stage_log.py
```

## Воспроизведение обработки

Команды приведены для Windows PowerShell из корня репозитория.

Расчёт KPI по RawLogs:

```powershell
.\.venv\Scripts\python.exe scripts\python\process_cycle_rawlogs.py --input-root raw_logs\hw_plc_s7_1200 --output-root processed_tables\hw_plc_s7_1200
.\.venv\Scripts\python.exe scripts\python\process_cycle_rawlogs.py --input-root raw_logs\vplc_internal --output-root processed_tables\vplc_internal --pattern "VPLC_L*\*.csv"
```

Сравнительные таблицы:

```powershell
.\.venv\Scripts\python.exe scripts\python\build_comparison_tables.py
```

Статусы GREEN/YELLOW/RED:

```powershell
.\.venv\Scripts\python.exe scripts\python\assign_mode_status.py
```

SummaryCards:

```powershell
.\.venv\Scripts\python.exe scripts\python\generate_summary_cards.py
```

Графики:

```powershell
.\.venv\Scripts\python.exe scripts\python\generate_chapter4_figures.py
```

EventJournal:

```powershell
.\.venv\Scripts\python.exe scripts\python\build_event_journal_from_stage_log.py
```

## Основные скрипты

| Скрипт | Назначение |
|---|---|
| `scripts\python\convert_s7_db_snapshot_to_rawlogs.py` | конвертация DB snapshot Siemens в RawLogs |
| `scripts\python\convert_vplc_dump_to_rawlogs.py` | конвертация VPLC dump ring log в RawLogs |
| `scripts\python\process_cycle_rawlogs.py` | расчёт KPI по RawLogs |
| `scripts\python\build_comparison_tables.py` | формирование сравнительных таблиц |
| `scripts\python\assign_mode_status.py` | присвоение GREEN/YELLOW/RED |
| `scripts\python\generate_summary_cards.py` | генерация SummaryCards |
| `scripts\python\generate_chapter4_figures.py` | генерация графиков |
| `scripts\python\build_event_journal_from_stage_log.py` | генерация EventJournal |

## Ограничения

Результаты относятся к конкретному стенду, версии VPLC, workload-программам и выбранной матрице режимов. Они не являются универсальной оценкой всех виртуальных PLC или всех задач реального времени.

Подробные ограничения:

```text
00_docs\chapter_4_limitations.md
```

Инженерная интерпретация:

```text
00_docs\chapter_4_cause_interpretation.md
00_docs\chapter_4_engineering_recommendations.md
```

## Примечание о публикации

Служебные файлы локальной работы, виртуальные окружения Python, временные файлы IDE, кэши и agent-инструкции не являются экспериментальными артефактами и не требуются для проверки результатов.

Основными артефактами воспроизводимости являются:

- `configs`;
- `plc`;
- `vplc`;
- `raw_logs`;
- `processed_tables`;
- `summary_cards`;
- `event_journal`;
- `scripts`;
- `00_docs`.
