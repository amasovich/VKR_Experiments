# Проверка полноты артефактов для Главы 4

Дата проверки: 2026-05-11.

Проверенные документы:

- `00_docs\00 - Крупный план ВКР.md`;
- `00_docs\01 - Оглавление ВКР v1.0.md`;
- `00_docs\chapter_4_artifact_index.md`;
- `00_docs\data_processing_plan_2026-05-10.md`.

## Вывод

Текущий план артефактов хорошо покрывает данные, KPI и сравнительные таблицы, но для полного написания Главы 4 нужно не забыть артефакты, которые подтверждают реализацию, воспроизводимость, валидацию и инженерную интерпретацию.

Глава 4 по оглавлению состоит из восьми смысловых блоков:

1. реализация тестовых проектов и сценариев измерений;
2. автоматизация прогонов и сбор экспериментальных данных;
3. первичная обработка результатов;
4. сравнительный анализ HW PLC и vPLC;
5. анализ причин недетерминизма и нестабильности цикла;
6. валидация корректности и применимости методики;
7. практические рекомендации;
8. ограничения применимости и дальнейшее развитие.

## Что уже закрыто

| Блок Главы 4 | Статус | Артефакты |
|---|---|---|
| 4.1. Реализация тестовых проектов | Частично закрыто | S7 SCL sources, VPLC ST sources, VPLC projects, stage log |
| 4.2. Автоматизация и сбор данных | Закрыто по данным, требуется описательный протокол | конвертеры, RawLogs, scripts, stage log |
| 4.3. Первичная обработка | Закрыто базово | `run_metrics.csv`, `mode_metrics.csv`, `run_metrics_extended.csv` |
| 4.4. Сравнительный анализ | Частично закрыто | `processed_tables\comparison\*.csv`, нужны графики |
| 4.5. Анализ причин | Не закрыто отдельным артефактом | нужны интерпретационные таблицы/заметки |
| 4.6. Валидация методики | Частично закрыто | нужны checklist/quality/limitations |
| 4.7. Практические рекомендации | Не закрыто отдельным артефактом | нужна таблица рекомендаций |
| 4.8. Ограничения и развитие | Частично закрыто | есть заметки, нужен итоговый файл ограничений |

## Недостающие артефакты

### 1. Реализация тестовых проектов

Нужно добавить в индекс:

- `plc\siemens_s7_1200\scl_sources\README.md`;
- `plc\siemens_s7_1200\scl_sources\DB_VKR_S7_Run.scl`;
- `plc\siemens_s7_1200\scl_sources\OB123_VKR_WorkloadCycle.scl`;
- `vplc\masc_vplc\st_sources\README.md`;
- `vplc\masc_vplc\st_sources\VPLC_WorkloadCycle_v0_3_timing_log.st`;
- `vplc\masc_vplc\st_sources\variables_v0_3_timing_log.yaml`;
- `vplc\masc_vplc\vkr_vplc_wl_timing_v03`;
- ключевые скриншоты загрузки/мониторинга из `screenshots\VPLC Studio\04`.

Назначение для текста: раздел 4.1.

### 2. Протокол выполнения прогонов

Нужен компактный файл:

```text
00_docs\chapter_4_run_protocol_summary.md
```

Содержимое:

- порядок S7-прогонов;
- порядок VPLC-прогонов;
- reset/freeze procedure;
- число режимов и повторов;
- почему TECH-прогоны отделены от финальных;
- где лежат RawLogs.

Назначение для текста: раздел 4.2.

### 3. Графики

Нужно подготовить:

```text
summary_cards\figures\tper_quantiles_by_mode.png
summary_cards\figures\tper_boxplot_by_mode.png
summary_cards\figures\deadline_miss_by_mode.png
summary_cards\figures\repeatability_q99_by_run.png
summary_cards\figures\data_quality_rows.png
summary_cards\figures\ecdf_tper_stress.png
summary_cards\figures\tper_timeseries_stress.png
```

Для каждого графика желательно рядом сохранять CSV с исходными данными графика.

Назначение для текста: разделы 4.3 и 4.4.

### 4. Пороги и статусы

Нужны:

```text
configs\mode_thresholds.yaml
processed_tables\comparison\threshold_status.csv
```

Назначение для текста: разделы 4.4 и 4.6.

### 5. SummaryCards

Нужны:

```text
summary_cards\hw_plc_s7_1200\<mode_id>.md
summary_cards\vplc_internal\<mode_id>.md
summary_cards\comparison\<pair_id>.md
```

Назначение для текста: разделы 4.4 и приложения.

### 6. Анализ причин

Нужен файл:

```text
00_docs\chapter_4_cause_interpretation.md
```

Содержимое:

- наблюдаемые признаки: хвосты `Tper`, `deadline_miss`, `Lburst`, `DQ99`, `timing_invalid`;
- вероятные причины;
- ограничения интерпретации;
- что можно утверждать по данным, а что нельзя.

Назначение для текста: раздел 4.5.

### 7. Практические рекомендации

Нужен файл:

```text
00_docs\chapter_4_engineering_recommendations.md
```

Содержимое:

- рекомендации по выбору `T0` и deadline;
- рекомендации по мониторингу;
- рекомендации по VPLC timing source;
- рекомендации по повторяемости и качеству данных;
- что делать перед применением vPLC в более жёстком контуре.

Назначение для текста: раздел 4.7.

### 8. Ограничения применимости

Нужен файл:

```text
00_docs\chapter_4_limitations.md
```

Содержимое:

- измерялись внутренние метрики цикла, а не end-to-end реакция;
- использован один аппаратный PLC и один vPLC-хост;
- нагрузка синтетическая;
- серия по 1000 строк x 5 повторов достаточна для апробации методики, но не заменяет длительные промышленные испытания;
- VPLC status-серия является технической, а финальные выводы строятся на `vplc_internal`.

Назначение для текста: раздел 4.8.

## Рекомендованный следующий порядок

1. Согласовать пороги GREEN/YELLOW/RED.
2. Сформировать `configs\mode_thresholds.yaml` и `threshold_status.csv`.
3. Сгенерировать графики.
4. Сгенерировать SummaryCards.
5. Подготовить `chapter_4_run_protocol_summary.md`.
6. Подготовить интерпретационные файлы:
   - `chapter_4_cause_interpretation.md`;
   - `chapter_4_engineering_recommendations.md`;
   - `chapter_4_limitations.md`.
7. Обновить `chapter_4_artifact_index.md`.

## Итоговая оценка полноты

На текущий момент закрыты данные и вычислительная часть обработки. Для полного пакета Главы 4 ещё нужно закрыть статусную, графическую и интерпретационную части.
