# SummaryCard: VPLC_L3_STRESS_75_80

## Паспорт режима

- Объект: `vPLC_container`
- Источник обработанных данных: `vplc_internal`
- T0: `75 ms`
- Deadline: `80 ms`
- Load level: `3`
- Load passes: `512`
- Повторов: `5`
- Валидных строк всего: `5000`

## Ключевые KPI

| KPI | Значение |
|---|---:|
| median(Tper) | 75 ms |
| Q99(Tper) | 97 ms |
| Q99.9(Tper) | 98 ms |
| Rmiss | 0.0234 |
| Lburst | 1 |

## Статус

- Статус: `RED`
- Причины статуса: `q99_above_yellow;q999_above_yellow`
- Профиль порогов: `calibrated_for_vkr_chapter_4`

## Ссылки на артефакты

- Processed mode metrics: `processed_tables\vplc_internal\mode_metrics.csv`
- Processed run metrics: `processed_tables\vplc_internal\run_metrics.csv`
- Extended run metrics: `processed_tables\vplc_internal\run_metrics_extended.csv`
- RawLogs: `raw_logs\vplc_internal\VPLC_L3_STRESS_75_80`

## Примечание

Карточка сформирована автоматически по обработанным данным. Статус GREEN/YELLOW/RED рассчитан по калиброванному профилю `configs\mode_thresholds.yaml` для класса умеренно критичного циклического контура управления без функций ПАЗ/SIL.

Для stress-режима статус RED трактуется как достижение или пересечение границы устойчивости при намеренно жёстком deadline, а не как ошибка постановки эксперимента.
