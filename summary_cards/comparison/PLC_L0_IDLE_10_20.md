# SummaryCard: PLC_L0_IDLE_10_20

## Пара сравнения

- HW PLC режим: `S7_L0_IDLE_10_20`
- VPLC режим: `VPLC_L0_IDLE_10_20`
- T0: `10 ms`
- Deadline: `20 ms`
- Load level: `0`
- Load passes: `0`

## Сравнение KPI

| KPI | HW PLC | VPLC | Delta VPLC-HW | Относительная delta |
|---|---:|---:|---:|---:|
| Q99(Tper), ms | 1.39 | 17 | 15.61 | 1123.021582734% |
| Q99.9(Tper), ms | 1.733 | 27 | 25.267 | 1457.991921523% |
| Rmiss | 0 | 0.005633803 | 0.005633803 | н/д |
| Lburst | 0 | 1 | 1 | н/д |
| median(Tper), ms | 0.575 | 10 | 9.425 | н/д |

## Ссылки на артефакты

- Pair comparison: `processed_tables\comparison\s7_vs_vplc_pair_comparison.csv`
- Pair deltas: `processed_tables\comparison\s7_vs_vplc_pair_delta.csv`
- Threshold statuses: `processed_tables\comparison\threshold_status.csv`

## Примечание

Карточка фиксирует численное сопоставление. Интерпретация причин и практические рекомендации формируются отдельными артефактами Главы 4.
