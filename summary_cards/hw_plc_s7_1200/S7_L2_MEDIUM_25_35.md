# SummaryCard: S7_L2_MEDIUM_25_35

## Паспорт режима

- Объект: `HW_PLC`
- Источник обработанных данных: `hw_plc_s7_1200`
- T0: `25 ms`
- Deadline: `35 ms`
- Load level: `2`
- Load passes: `128`
- Повторов: `5`
- Валидных строк всего: `5000`

## Ключевые KPI

| KPI | Значение |
|---|---:|
| median(Tper) | 18.059 ms |
| Q99(Tper) | 24.819 ms |
| Q99.9(Tper) | 25.464 ms |
| Rmiss | 0 |
| Lburst | 0 |

## Статус

- Статус: `GREEN`
- Причины статуса: `all_green_criteria_met`
- Профиль порогов: `calibrated_for_vkr_chapter_4`

## Ссылки на артефакты

- Processed mode metrics: `processed_tables\hw_plc_s7_1200\mode_metrics.csv`
- Processed run metrics: `processed_tables\hw_plc_s7_1200\run_metrics.csv`
- Extended run metrics: `processed_tables\hw_plc_s7_1200\run_metrics_extended.csv`
- RawLogs: `raw_logs\hw_plc_s7_1200\S7_L2_MEDIUM_25_35`

## Примечание

Карточка сформирована автоматически по обработанным данным. Статус GREEN/YELLOW/RED рассчитан по калиброванному профилю `configs\mode_thresholds.yaml` для класса умеренно критичного циклического контура управления без функций ПАЗ/SIL.
