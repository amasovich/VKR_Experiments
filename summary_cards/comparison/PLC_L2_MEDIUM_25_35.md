# SummaryCard: PLC_L2_MEDIUM_25_35

## Пара сравнения

- HW PLC режим: `S7_L2_MEDIUM_25_35`
- VPLC режим: `VPLC_L2_MEDIUM_25_35`
- T0: `25 ms`
- Deadline: `35 ms`
- Load level: `2`
- Load passes: `128`

## Сравнение KPI

| KPI | HW PLC | VPLC | Delta VPLC-HW | Относительная delta |
|---|---:|---:|---:|---:|
| Q99(Tper), ms | 24.819 | 45 | 20.181 | 81.312703977% |
| Q99.9(Tper), ms | 25.464 | 54 | 28.536 | 112.064090481% |
| Rmiss | 0 | 0.011011011 | 0.011011011 | н/д |
| Lburst | 0 | 1 | 1 | н/д |
| median(Tper), ms | 18.059 | 25 | 6.941 | н/д |

## Ссылки на артефакты

- Pair comparison: `processed_tables\comparison\s7_vs_vplc_pair_comparison.csv`
- Pair deltas: `processed_tables\comparison\s7_vs_vplc_pair_delta.csv`
- Threshold statuses: `processed_tables\comparison\threshold_status.csv`

## Примечание

Карточка фиксирует численное сопоставление. Интерпретация причин и практические рекомендации формируются отдельными артефактами Главы 4.
