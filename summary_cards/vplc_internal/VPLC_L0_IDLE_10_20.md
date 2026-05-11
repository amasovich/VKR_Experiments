# SummaryCard: VPLC_L0_IDLE_10_20

## Паспорт режима

- Объект: `vPLC_container`
- Источник обработанных данных: `vplc_internal`
- T0: `10 ms`
- Deadline: `20 ms`
- Load level: `0`
- Load passes: `0`
- Повторов: `5`
- Валидных строк всего: `4970`

## Ключевые KPI

| KPI | Значение |
|---|---:|
| median(Tper) | 10 ms |
| Q99(Tper) | 17 ms |
| Q99.9(Tper) | 27 ms |
| Rmiss | 0.005633803 |
| Lburst | 1 |

## Статус

- Статус: `RED`
- Причины статуса: `q999_above_yellow`
- Профиль порогов: `calibrated_for_vkr_chapter_4`

## Ссылки на артефакты

- Processed mode metrics: `processed_tables\vplc_internal\mode_metrics.csv`
- Processed run metrics: `processed_tables\vplc_internal\run_metrics.csv`
- Extended run metrics: `processed_tables\vplc_internal\run_metrics_extended.csv`
- RawLogs: `raw_logs\vplc_internal\VPLC_L0_IDLE_10_20`

## Примечание

Карточка сформирована автоматически по обработанным данным. Статус GREEN/YELLOW/RED рассчитан по калиброванному профилю `configs\mode_thresholds.yaml` для класса умеренно критичного циклического контура управления без функций ПАЗ/SIL.
