# План обработки данных для Главы 4

Дата подготовки: 2026-05-10.

Основание: методика и приложения из `00_docs\МИФИ_ВКР_2026_Березняк_В_Н_v5.pdf`, фактически полученные RawLogs HW PLC S7-1200 и VPLC.

## 1. Текущий статус данных

Съём экспериментальных данных завершён для двух объектов:

| Объект | RawLogs | ProcessedTables | Статус |
|---|---|---|---|
| HW PLC S7-1200 | `raw_logs\hw_plc_s7_1200` | `processed_tables\hw_plc_s7_1200` | 25 прогонов, 5 режимов |
| VPLC internal timing | `raw_logs\vplc_internal` | `processed_tables\vplc_internal` | 25 прогонов, 5 режимов |

Дополнительная серия `raw_logs\vplc_status` остаётся техническим наблюдением runtime status и не подменяет финальные `Tper/Jper/deadline_miss`.

## 2. Методические артефакты, которые нужно получить

По приложениям методики для Главы 4 нужно подготовить полный набор артефактов:

| Артефакт | Назначение | Источник / скрипт |
|---|---|---|
| `run_metrics.csv` | KPI одного прогона, аналог таблицы А.7 | уже формируется `process_cycle_rawlogs.py` |
| `mode_metrics.csv` | агрегирование по режиму | уже формируется `process_cycle_rawlogs.py` |
| `repeatability_metrics.csv` | сравнение повторов одного Mode, аналог таблицы А.8 | нужно добавить |
| `pair_comparison.csv` | итоговое сравнение HW PLC vs VPLC, аналог таблицы А.11 | нужно добавить |
| `baseline_stress_comparison.csv` | baseline/stress и light/medium/high сравнение, аналог таблицы А.9 | нужно добавить |
| `threshold_status.csv` | лист присвоения GREEN/YELLOW/RED, аналог таблицы А.14 | нужно добавить после фиксации порогов |
| `summary_cards\...` | итоговые карточки режимов, аналог таблицы А.10 | нужно добавить генератор Markdown |
| `figures\...` | графики для Главы 4 | нужно добавить генератор графиков |
| `chapter_4_artifact_index.md` | индекс всех файлов для переноса в текст ВКР | нужно добавить |

## 3. KPI, которые нужно рассчитывать

Уже рассчитываются:

- `min(Tper)`;
- `max(Tper)`;
- `mean(Tper)`;
- `median(Tper)`;
- `Q95(Tper)`;
- `Q99(Tper)`;
- `Q99.9(Tper)`;
- `Jper_min/max/mean`;
- `deadline_miss_count`;
- `Rmiss`;
- `Lburst`;
- количество валидных и исключённых строк.

Нужно добавить:

- `DQ99` как дрейф `Q99(Tper)` по временным окнам внутри прогона;
- `repeatability` между 5 повторами одного режима;
- относительную деградацию VPLC относительно HW PLC по парным режимам;
- статус по правилам GREEN/YELLOW/RED;
- список предупреждений по качеству данных: `timing_invalid`, исключённые строки, TECH-файлы вне финальной серии.

## 4. План скриптов

### 4.1. Доработать `process_cycle_rawlogs.py`

Цель: оставить текущий вывод совместимым, но добавить расширенный файл:

```text
processed_tables\<object>\run_metrics_extended.csv
```

Добавить поля:

- `window_count`;
- `window_size_rows`;
- `DQ99_ms`;
- `Q99_window_min_ms`;
- `Q99_window_max_ms`;
- `valid_ratio`;
- `excluded_ratio`;
- `deadline_margin_q99_ms = deadline_threshold_ms - Q99(Tper)`;
- `deadline_margin_q999_ms = deadline_threshold_ms - Q99.9(Tper)`.

### 4.2. Создать `scripts\python\build_comparison_tables.py`

Вход:

```text
processed_tables\hw_plc_s7_1200\run_metrics.csv
processed_tables\hw_plc_s7_1200\mode_metrics.csv
processed_tables\vplc_internal\run_metrics.csv
processed_tables\vplc_internal\mode_metrics.csv
configs\mode_matrix.yaml
```

Выход:

```text
processed_tables\comparison\s7_vs_vplc_mode_comparison.csv
processed_tables\comparison\s7_vs_vplc_pair_delta.csv
processed_tables\comparison\repeatability_metrics.csv
processed_tables\comparison\baseline_stress_comparison.csv
processed_tables\comparison\data_quality_summary.csv
```

Минимальные сравнения:

- по каждой паре `S7_*` и `VPLC_*`;
- `Q99(Tper)`, `Q99.9(Tper)`, `Rmiss`, `Lburst`;
- абсолютная разница;
- относительная разница;
- ухудшение/улучшение VPLC относительно HW PLC;
- комментарий о сопоставимости режима.

### 4.3. Создать `scripts\python\assign_mode_status.py`

Цель: сформировать таблицу статусов GREEN/YELLOW/RED.

Вход:

```text
processed_tables\comparison\s7_vs_vplc_mode_comparison.csv
configs\mode_thresholds.yaml
```

Выход:

```text
processed_tables\comparison\threshold_status.csv
```

Пороговый файл нужно создать отдельно, чтобы не зашивать инженерные критерии в код.

Черновой состав `configs\mode_thresholds.yaml`:

- допустимый `Q99`;
- допустимый `Q99.9`;
- допустимый `Rmiss`;
- допустимый `Lburst`;
- допустимая относительная деградация VPLC к HW PLC;
- hard-fail признаки.

### 4.4. Создать `scripts\python\generate_summary_cards.py`

Выход:

```text
summary_cards\hw_plc_s7_1200\<mode_id>.md
summary_cards\vplc_internal\<mode_id>.md
summary_cards\comparison\<pair_id>.md
```

Карточка должна включать:

- `ModeID`;
- объект;
- `T0`;
- `deadline`;
- нагрузку;
- количество повторов;
- ключевые KPI;
- статус;
- интерпретацию;
- ссылки на RawLogs, ProcessedTables и графики.

### 4.5. Создать `scripts\python\generate_chapter4_figures.py`

Выход:

```text
summary_cards\figures\...
```

Формат графиков: PNG + CSV-таблица данных графика.

## 5. Рекомендуемые графики для Главы 4

### 5.1. Сравнение `Tper` по режимам

Тип: grouped bar chart или point chart.

Что показать:

- `median(Tper)`;
- `Q99(Tper)`;
- `Q99.9(Tper)`;
- отдельно HW PLC и VPLC.

Польза: быстро показывает, насколько фактический цикл отличается от номинального и как ведут себя хвосты.

### 5.2. Boxplot / violin plot `Tper` по режимам

Тип: boxplot по всем строкам RawLogs.

Польза: показывает распределение, выбросы и асимметрию лучше, чем одна таблица.

Ограничение: для текста ВКР лучше не перегружать всеми 10 boxplot сразу; можно сделать 5 парных графиков или одну компактную фигуру.

### 5.3. Временной ряд `Tper` внутри одного характерного прогона

Режимы-кандидаты:

- `S7_L3_STRESS_75_80` vs `VPLC_L3_STRESS_75_80`;
- `S7_L0_IDLE_10_20` vs `VPLC_L0_IDLE_10_20`.

Польза: видно, одиночные ли выбросы, есть ли периодические скачки или дрейф.

### 5.4. ECDF / CDF распределения `Tper`

Тип: эмпирическая функция распределения.

Польза: хорошо показывает хвосты и позволяет сравнить S7/VPLC без перегрузки гистограммами.

### 5.5. Deadline miss summary

Тип: bar chart.

Что показать:

- `Rmiss`;
- `deadline_miss_total`;
- `Lburst`.

Польза: напрямую связан с допустимостью режима.

### 5.6. Heatmap статусов режимов

Тип: матрица `Mode x KPI`.

Столбцы:

- `Q99`;
- `Q99.9`;
- `Rmiss`;
- `Lburst`;
- `Repeatability`;
- итоговый статус.

Польза: удобная итоговая иллюстрация для Главы 4.

### 5.7. Repeatability plot

Тип: line/point chart по повторам R01..R05.

Что показать:

- `median(Tper)`;
- `Q99(Tper)`;
- `Q99.9(Tper)`.

Польза: отвечает требованию методики не делать вывод по одному удачному прогону.

### 5.8. Data quality plot

Тип: bar chart по `rows_ok`, `rows_excluded`.

Польза: честно показывает, что VPLC 10/25 ms имел небольшое число `timing_invalid`, а обработка их исключила.

## 6. Рекомендуемый порядок обработки

1. Проверить полноту RawLogs:
   - 5 режимов S7;
   - 5 режимов VPLC;
   - по 5 повторов;
   - по 1000 строк на повтор;
   - TECH-файлы исключены из финальной обработки.

2. Пересчитать базовые `run_metrics.csv` и `mode_metrics.csv` для обоих объектов.

3. Добавить расширенные KPI с `DQ99` и quality summary.

4. Сформировать comparison tables:
   - режим к режиму;
   - baseline/light/medium/high/stress внутри объекта;
   - VPLC относительно HW PLC.

5. Зафиксировать критерии GREEN/YELLOW/RED в `configs\mode_thresholds.yaml`.

6. Сформировать `threshold_status.csv`.

7. Сгенерировать SummaryCards.

8. Сгенерировать графики.

9. Сформировать `chapter_4_artifact_index.md` со списком всех файлов для переноса в ВКР.

10. Зафиксировать событие в `00_docs\stage_4_0_log.md`.

## 7. Вопросы, которые нужно решить перед статусами GREEN/YELLOW/RED

Перед автоматическим присвоением статусов нужно явно согласовать:

1. Какие абсолютные пороги применять к `Q99` и `Q99.9`:
   - как долю от `T0`;
   - или как запас до `deadline_threshold_ms`.

2. Какой `Rmiss` считать допустимым:
   - строго `0`;
   - или допускается малая доля для stress-режима.

3. Как трактовать `timing_invalid`:
   - исключать из KPI, но учитывать в `data_quality_summary`;
   - вводить отдельный hard-fail порог по доле исключённых строк.

4. Нужно ли сравнивать VPLC с HW PLC по относительной деградации, если у HW PLC фактический `Tper` в малых режимах меньше `T0`, а VPLC удерживает период близко к `T0`.

## 8. Минимальный набор для передачи в Главу 4

Минимально достаточный комплект:

```text
processed_tables\hw_plc_s7_1200\run_metrics.csv
processed_tables\hw_plc_s7_1200\mode_metrics.csv
processed_tables\vplc_internal\run_metrics.csv
processed_tables\vplc_internal\mode_metrics.csv
processed_tables\comparison\*.csv
summary_cards\comparison\*.md
summary_cards\figures\*.png
00_docs\stage_4_0_log.md
configs\mode_matrix.yaml
configs\mode_thresholds.yaml
```

RawLogs остаются первичными артефактами трассируемости и не правятся вручную.
