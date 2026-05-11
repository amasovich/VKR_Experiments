# SummaryCard: PLC_L1_LIGHT_10_20

## Пара сравнения

- HW PLC режим: `S7_L1_LIGHT_10_20`
- VPLC режим: `VPLC_L1_LIGHT_10_20`
- T0: `10 ms`
- Deadline: `20 ms`
- Load level: `1`
- Load passes: `32`

## Сравнение KPI

| KPI | HW PLC | VPLC | Delta VPLC-HW | Относительная delta |
|---|---:|---:|---:|---:|
| Q99(Tper), ms | 7.307 | 23 | 15.693 | 214.766662105% |
| Q99.9(Tper), ms | 7.737 | 30 | 22.263 | 287.747188833% |
| Rmiss | 0 | 0.00624874 | 0.00624874 | н/д |
| Lburst | 0 | 1 | 1 | н/д |
| median(Tper), ms | 4.9615 | 10 | 5.0385 | н/д |

## Ссылки на артефакты

- Pair comparison: `processed_tables\comparison\s7_vs_vplc_pair_comparison.csv`
- Pair deltas: `processed_tables\comparison\s7_vs_vplc_pair_delta.csv`
- Threshold statuses: `processed_tables\comparison\threshold_status.csv`

## Примечание

Карточка фиксирует численное сопоставление. Интерпретация причин и практические рекомендации формируются отдельными артефактами Главы 4.
