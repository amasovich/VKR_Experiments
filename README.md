# VKR_Experiments

Репозиторий содержит экспериментальные материалы выпускной квалификационной работы:

**«Методика оценки детерминизма и стабильности цикла управления виртуальных программируемых логических контроллеров в контейнерной среде в сравнении с аппаратными контроллерами»**.

Материалы опубликованы для проверки состава эксперимента, исходных программ контроллеров, первичных данных, обработанных показателей и итоговых сравнительных артефактов.

## Цель эксперимента

Цель практической части - проверить применимость разработанной методики на двух реализациях циклического контура управления:

| Объект | Обозначение в данных | Роль в эксперименте |
|---|---|---|
| Siemens S7-1200 CPU 1215C | `HW_PLC`, `S7_*` | аппаратный PLC, базовая точка сравнения |
| MASC/VPLC MAX Automation на mini-PC | `VPLC_HOST`, `VPLC_*` | виртуальный PLC в контейнерной среде |

Сравнение выполнено по показателям стабильности цикла:

- фактический период цикла `Tper`;
- отклонение периода от заданного значения `Jper`;
- факт превышения deadline `deadline_miss`;
- доля превышений `Rmiss`;
- максимальная серия превышений `Lburst`;
- квантили `Q99(Tper)` и `Q99.9(Tper)`;
- повторяемость результатов между прогонами;
- качество данных и число исключённых строк.

## Режимы измерений

Финальная серия включает 5 сопоставимых режимов для аппаратного PLC и VPLC. Для каждого режима выполнено 5 повторов по 1000 строк RawLogs.

| Режим | T0, ms | Deadline, ms | Load level | Load passes | Назначение |
|---|---:|---:|---:|---:|---|
| `L0_IDLE_10_20` | 10 | 20 | 0 | 0 | базовый холостой режим |
| `L1_LIGHT_10_20` | 10 | 20 | 1 | 32 | лёгкая нагрузка |
| `L2_MEDIUM_25_35` | 25 | 35 | 2 | 128 | средняя нагрузка |
| `L3_HIGH_75_100` | 75 | 100 | 3 | 512 | высокая рабочая нагрузка |
| `L3_STRESS_75_80` | 75 | 80 | 3 | 512 | стресс-режим с ужесточённым deadline |

Стресс-режим используется как проверка границы устойчивости. Его превышения deadline трактуются отдельно от рабочих режимов и не являются ошибкой проведения эксперимента.

## Состав репозитория

| Каталог | Содержимое |
|---|---|
| `00_docs` | документы эксперимента, журнал этапа, индекс артефактов, ограничения и инженерная интерпретация |
| `configs` | конфигурации стенда, матрица режимов, схема RawLogs и профиль порогов |
| `event_journal` | машинно-читаемый журнал событий эксперимента |
| `plc\siemens_s7_1200` | исходные SCL-файлы Siemens, DB snapshots и материалы проверки HW PLC |
| `vplc\masc_vplc` | исходные ST-файлы VPLC, проекты VPLC Studio, dump-снимки и материалы проверки VPLC |
| `raw_logs` | первичные CSV-журналы измерений |
| `processed_tables` | рассчитанные KPI и сравнительные таблицы |
| `summary_cards` | итоговые карточки режимов, сравнительные карточки и графики |
| `scripts\python` | скрипты конвертации, обработки, сравнения, статусов, карточек, графиков и EventJournal |
| `scripts\windows` | PowerShell-скрипты сбора данных и запуска VPLC-прогонов |
| `scripts\linux` | Bash-скрипты для узла VPLC |
| `screenshots` | скриншоты этапов проверки и подтверждения работы VPLC Studio |

## Ключевые артефакты

| Файл | Назначение |
|---|---|
| `00_docs\chapter_4_artifact_index.md` | индекс основных артефактов практической части |
| `00_docs\chapter_4_artifact_audit_2026-05-11.md` | контроль полноты таблиц, графиков и ссылок |
| `00_docs\stage_4_0_log.md` | человекочитаемый журнал выполнения практического этапа |
| `event_journal\event_journal.csv` | машинно-читаемый EventJournal |
| `configs\mode_matrix.yaml` | матрица режимов эксперимента |
| `configs\mode_thresholds.yaml` | профиль GREEN/YELLOW/RED-порогов |
| `00_docs\chapter_4_green_yellow_red_scale.md` | табличное описание инженерной шкалы принятия решения |
| `processed_tables\comparison\mode_summary.csv` | сводка KPI по всем режимам |
| `processed_tables\comparison\s7_vs_vplc_pair_comparison.csv` | парное сравнение S7 и VPLC |
| `processed_tables\comparison\threshold_status.csv` | итоговые статусы GREEN/YELLOW/RED |
| `summary_cards\figures\figures_chapter_4_guide.md` | описание сформированных графиков |

## Первичные данные

Финальные RawLogs находятся в:

```text
raw_logs\hw_plc_s7_1200
raw_logs\vplc_internal
```

Состав финальной серии:

```text
raw_logs\hw_plc_s7_1200\S7_L*      -> 25 CSV
raw_logs\vplc_internal\VPLC_L*     -> 25 CSV
```

Для VPLC также сохранены исходные dump-снимки ring buffer:

```text
vplc\masc_vplc\vkr_vplc_wl_timing_v03\final_dumps_20260510
```

Эти dump-снимки вместе со скриптом `convert_vplc_dump_to_rawlogs.py` позволяют повторно получить VPLC RawLogs. RawLogs рассматриваются как первичные экспериментальные данные и не редактируются вручную.

## Обработанные таблицы

Основные таблицы по каждому объекту:

```text
processed_tables\hw_plc_s7_1200\run_metrics.csv
processed_tables\hw_plc_s7_1200\run_metrics_extended.csv
processed_tables\hw_plc_s7_1200\mode_metrics.csv

processed_tables\vplc_internal\run_metrics.csv
processed_tables\vplc_internal\run_metrics_extended.csv
processed_tables\vplc_internal\mode_metrics.csv
```

Сравнительные таблицы:

```text
processed_tables\comparison\mode_summary.csv
processed_tables\comparison\s7_vs_vplc_pair_comparison.csv
processed_tables\comparison\s7_vs_vplc_pair_delta.csv
processed_tables\comparison\repeatability_metrics.csv
processed_tables\comparison\baseline_stress_comparison.csv
processed_tables\comparison\data_quality_summary.csv
processed_tables\comparison\threshold_status.csv
```

## Графики

Графики расположены в:

```text
summary_cards\figures
```

Их состав и назначение описаны в:

```text
summary_cards\figures\figures_chapter_4_guide.md
summary_cards\figures\figures_manifest.csv
```

Основные графики показывают:

- изменение квантилей `Tper` по режимам;
- долю deadline miss;
- разницу VPLC и S7 по ключевым квантилям;
- итоговые статусы GREEN/YELLOW/RED;
- качество данных;
- временные ряды для режимов `L3_HIGH_75_100` и `L3_STRESS_75_80`.

## Инженерная шкала

Для интерпретации результатов используется профиль:

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

Шкала GREEN/YELLOW/RED применяется как инженерная шкала принятия решения для выбранного класса сценария. Она не является универсальным нормативом для любых промышленных систем.

## Воспроизведение обработки

Команды приведены для Windows PowerShell из корня репозитория.

Расчёт KPI по RawLogs:

```powershell
.\.venv\Scripts\python.exe scripts\python\process_cycle_rawlogs.py --input-root raw_logs\hw_plc_s7_1200 --output-root processed_tables\hw_plc_s7_1200
.\.venv\Scripts\python.exe scripts\python\process_cycle_rawlogs.py --input-root raw_logs\vplc_internal --output-root processed_tables\vplc_internal --pattern "VPLC_L*\*.csv"
```

Формирование сравнительных таблиц:

```powershell
.\.venv\Scripts\python.exe scripts\python\build_comparison_tables.py
```

Присвоение статусов GREEN/YELLOW/RED:

```powershell
.\.venv\Scripts\python.exe scripts\python\assign_mode_status.py
```

Генерация SummaryCards:

```powershell
.\.venv\Scripts\python.exe scripts\python\generate_summary_cards.py
```

Генерация графиков:

```powershell
.\.venv\Scripts\python.exe scripts\python\generate_chapter4_figures.py
```

Генерация EventJournal:

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

## Ограничения интерпретации

Результаты относятся к конкретному стенду, версиям программного обеспечения, исходным программам PLC/VPLC и выбранной матрице режимов. Они не являются универсальной оценкой всех виртуальных PLC или всех задач реального времени.

Подробные ограничения и инженерная интерпретация приведены в:

```text
00_docs\chapter_4_limitations.md
00_docs\chapter_4_cause_interpretation.md
00_docs\chapter_4_engineering_recommendations.md
```
