# SummaryCard: PLC_L3_HIGH_75_100

## Пара сравнения

- HW PLC режим: `S7_L3_HIGH_75_100`
- VPLC режим: `VPLC_L3_HIGH_75_100`
- T0: `75 ms`
- Deadline: `100 ms`
- Load level: `3`
- Load passes: `512`

## Сравнение KPI

| KPI | HW PLC | VPLC | Delta VPLC-HW | Относительная delta |
|---|---:|---:|---:|---:|
| Q99(Tper), ms | 83.569 | 98 | 14.431 | 17.268365064% |
| Q99.9(Tper), ms | 86.721 | 105 | 18.279 | 21.077939599% |
| Rmiss | 0 | 0.0024 | 0.0024 | н/д |
| Lburst | 0 | 1 | 1 | н/д |
| median(Tper), ms | 73.1555 | 75 | 1.8445 | н/д |

## Ссылки на артефакты

- Pair comparison: `processed_tables\comparison\s7_vs_vplc_pair_comparison.csv`
- Pair deltas: `processed_tables\comparison\s7_vs_vplc_pair_delta.csv`
- Threshold statuses: `processed_tables\comparison\threshold_status.csv`

## Примечание

Карточка фиксирует численное сопоставление. Интерпретация причин и практические рекомендации формируются отдельными артефактами Главы 4.
