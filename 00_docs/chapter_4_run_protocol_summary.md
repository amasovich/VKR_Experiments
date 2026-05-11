# Протокол выполнения экспериментальной части Главы 4

Дата подготовки: 2026-05-11.

Документ фиксирует, какие данные были получены и какие артефакты используются для написания практической части ВКР. Измерения на стенде завершены; дальнейшие действия относятся к обработке данных и оформлению выводов.

## Объекты сравнения

| Объект | Источник RawLogs | Состав финальной серии |
|---|---|---|
| HW PLC Siemens S7-1200 | `raw_logs\hw_plc_s7_1200` | 5 режимов x 5 повторов x 1000 строк |
| VPLC MASC/MAX Automation | `raw_logs\vplc_internal` | 5 режимов x 5 повторов x 1000 строк |

Технические VPLC status-прогоны из `raw_logs\vplc_status` не используются как источник финальных `Tper/Jper/deadline_miss`, потому что финальная серия VPLC получена через внутренний ST timing `_milliseconds_from_start_` и ring log.

## Режимы

| Режим | T0, ms | Deadline, ms | Load level | Load passes |
|---|---:|---:|---:|---:|
| L0_IDLE_10_20 | 10 | 20 | 0 | 0 |
| L1_LIGHT_10_20 | 10 | 20 | 1 | 32 |
| L2_MEDIUM_25_35 | 25 | 35 | 2 | 128 |
| L3_HIGH_75_100 | 75 | 100 | 3 | 512 |
| L3_STRESS_75_80 | 75 | 80 | 3 | 512 |

Для каждого режима выполнено по 5 повторов. Размер одного повтора: 1000 строк RawLogs.

## Цепочка артефактов

1. Первичные данные:
   `raw_logs\hw_plc_s7_1200`, `raw_logs\vplc_internal`.
2. Базовая обработка:
   `processed_tables\hw_plc_s7_1200`, `processed_tables\vplc_internal`.
3. Сравнительные таблицы:
   `processed_tables\comparison`.
4. Статусы по калиброванному профилю порогов:
   `configs\mode_thresholds.yaml`, `processed_tables\comparison\threshold_status.csv`.
5. SummaryCards:
   `summary_cards\hw_plc_s7_1200`, `summary_cards\vplc_internal`, `summary_cards\comparison`.
6. Графики:
   `summary_cards\figures`.

Полный индекс файлов приведён в `00_docs\chapter_4_artifact_index.md`.

## Контроль воспроизводимости

Обработка выполнялась скриптами:

- `scripts\python\process_cycle_rawlogs.py`;
- `scripts\python\build_comparison_tables.py`;
- `scripts\python\assign_mode_status.py`;
- `scripts\python\generate_summary_cards.py`;
- `scripts\python\generate_chapter4_figures.py`.

RawLogs вручную не изменялись. Все агрегированные таблицы и графики формируются из сохранённых CSV.

## Статус

Практический съём на HW PLC и VPLC закрыт. Профиль порогов GREEN/YELLOW/RED зафиксирован в `configs\mode_thresholds.yaml` со статусом `calibrated_for_vkr_chapter_4` для класса умеренно критичного циклического контура управления / технологической автоматики без функций ПАЗ/SIL.
