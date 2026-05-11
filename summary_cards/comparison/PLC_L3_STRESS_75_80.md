# SummaryCard: PLC_L3_STRESS_75_80

## Пара сравнения

- HW PLC режим: `S7_L3_STRESS_75_80`
- VPLC режим: `VPLC_L3_STRESS_75_80`
- T0: `75 ms`
- Deadline: `80 ms`
- Load level: `3`
- Load passes: `512`

## Сравнение KPI

| KPI | HW PLC | VPLC | Delta VPLC-HW | Относительная delta |
|---|---:|---:|---:|---:|
| Q99(Tper), ms | 83.669 | 97 | 13.331 | 15.933021788% |
| Q99.9(Tper), ms | 86.208 | 98 | 11.792 | 13.678544915% |
| Rmiss | 0.0288 | 0.0234 | -0.0054 | н/д |
| Lburst | 1 | 1 | 0 | н/д |
| median(Tper), ms | 73.1045 | 75 | 1.8955 | н/д |

## Ссылки на артефакты

- Pair comparison: `processed_tables\comparison\s7_vs_vplc_pair_comparison.csv`
- Pair deltas: `processed_tables\comparison\s7_vs_vplc_pair_delta.csv`
- Threshold statuses: `processed_tables\comparison\threshold_status.csv`

## Примечание

Карточка фиксирует численное сопоставление. Интерпретация причин и практические рекомендации формируются отдельными артефактами Главы 4.
