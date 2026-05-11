# SummaryCard: VPLC_L2_MEDIUM_25_35

## Паспорт режима

- Объект: `vPLC_container`
- Источник обработанных данных: `vplc_internal`
- T0: `25 ms`
- Deadline: `35 ms`
- Load level: `2`
- Load passes: `128`
- Повторов: `5`
- Валидных строк всего: `4995`

## Ключевые KPI

| KPI | Значение |
|---|---:|
| median(Tper) | 25 ms |
| Q99(Tper) | 45 ms |
| Q99.9(Tper) | 54 ms |
| Rmiss | 0.011011011 |
| Lburst | 1 |

## Статус

- Статус: `RED`
- Причины статуса: `q99_above_yellow;q999_above_yellow;rmiss_above_yellow`
- Профиль порогов: `calibrated_for_vkr_chapter_4`

## Ссылки на артефакты

- Processed mode metrics: `processed_tables\vplc_internal\mode_metrics.csv`
- Processed run metrics: `processed_tables\vplc_internal\run_metrics.csv`
- Extended run metrics: `processed_tables\vplc_internal\run_metrics_extended.csv`
- RawLogs: `raw_logs\vplc_internal\VPLC_L2_MEDIUM_25_35`

## Примечание

Карточка сформирована автоматически по обработанным данным. Статус GREEN/YELLOW/RED рассчитан по калиброванному профилю `configs\mode_thresholds.yaml` для класса умеренно критичного циклического контура управления без функций ПАЗ/SIL.
