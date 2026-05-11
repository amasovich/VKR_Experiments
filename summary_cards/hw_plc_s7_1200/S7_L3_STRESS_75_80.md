# SummaryCard: S7_L3_STRESS_75_80

## Паспорт режима

- Объект: `HW_PLC`
- Источник обработанных данных: `hw_plc_s7_1200`
- T0: `75 ms`
- Deadline: `80 ms`
- Load level: `3`
- Load passes: `512`
- Повторов: `5`
- Валидных строк всего: `5000`

## Ключевые KPI

| KPI | Значение |
|---|---:|
| median(Tper) | 73.1045 ms |
| Q99(Tper) | 83.669 ms |
| Q99.9(Tper) | 86.208 ms |
| Rmiss | 0.0288 |
| Lburst | 1 |

## Статус

- Статус: `RED`
- Причины статуса: `q99_above_yellow`
- Профиль порогов: `calibrated_for_vkr_chapter_4`

## Ссылки на артефакты

- Processed mode metrics: `processed_tables\hw_plc_s7_1200\mode_metrics.csv`
- Processed run metrics: `processed_tables\hw_plc_s7_1200\run_metrics.csv`
- Extended run metrics: `processed_tables\hw_plc_s7_1200\run_metrics_extended.csv`
- RawLogs: `raw_logs\hw_plc_s7_1200\S7_L3_STRESS_75_80`

## Примечание

Карточка сформирована автоматически по обработанным данным. Статус GREEN/YELLOW/RED рассчитан по калиброванному профилю `configs\mode_thresholds.yaml` для класса умеренно критичного циклического контура управления без функций ПАЗ/SIL.

Для stress-режима статус RED трактуется как достижение или пересечение границы устойчивости при намеренно жёстком deadline, а не как ошибка постановки эксперимента.
