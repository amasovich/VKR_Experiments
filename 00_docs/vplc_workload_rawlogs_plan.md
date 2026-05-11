# План VPLC workload и RawLogs

Дата подготовки: 2026-05-09.

## Цель

Подготовить зеркальный VPLC-контур для уже полученных HW PLC S7-1200 RawLogs:

```text
S7_L0_IDLE_10_20    -> VPLC_L0_IDLE_10_20
S7_L1_LIGHT_10_20   -> VPLC_L1_LIGHT_10_20
S7_L2_MEDIUM_25_35  -> VPLC_L2_MEDIUM_25_35
S7_L3_HIGH_75_100   -> VPLC_L3_HIGH_75_100
S7_L3_STRESS_75_80  -> VPLC_L3_STRESS_75_80
```

Сравнительные выводы и summary cards не формируются до появления VPLC RawLogs.

## Подготовленные артефакты

```text
vplc\masc_vplc\st_sources\VPLC_WorkloadCycle_v0_2.st
vplc\masc_vplc\st_sources\VPLC_WorkloadCycle_v0_2_numbered.st
vplc\masc_vplc\st_sources\variables_v0_2.yaml
```

Основной вариант использует `ARRAY[0..15]`. Если VPLC Studio не принимает массивы, используется numbered-вариант.

## Ручная проверка в VPLC Studio

1. Создать копию минимального проекта или новый проект `vkr_vplc_wl`.
2. Добавить переменные из `variables_v0_2.yaml`.
3. В циклическую ST-задачу вставить код `VPLC_WorkloadCycle_v0_2.st`.
4. Если сборка не проходит из-за массивов, заменить код на `VPLC_WorkloadCycle_v0_2_numbered.st` и добавить numbered-переменные.
5. Собрать и загрузить проект на `VPLC_HOST`.
6. Запустить программу.
7. Проверить в мониторинге:
   - `cycle_counter` растёт;
   - `heartbeat` переключается;
   - `workload_accumulator` изменяется;
   - `load_level_effective` соответствует `load_level`;
   - `load_passes_effective` соответствует режиму.

## Режимы

| VPLC ModeID | `cycleDuration` проекта | `load_level` | `load_passes` | `T0_ms` | `deadline_threshold_ms` |
|---|---:|---:|---:|---:|---:|
| `VPLC_L0_IDLE_10_20` | 10 ms | 0 | 0 | 10 | 20 |
| `VPLC_L1_LIGHT_10_20` | 10 ms | 1 | 32 | 10 | 20 |
| `VPLC_L2_MEDIUM_25_35` | 25 ms | 2 | 128 | 25 | 35 |
| `VPLC_L3_HIGH_75_100` | 75 ms | 3 | 512 | 75 | 100 |
| `VPLC_L3_STRESS_75_80` | 75 ms | 3 | 512 | 75 | 80 |

Для финальных VPLC RawLogs `cycleDuration` основного цикла в VPLC Studio должен совпадать с `T0_ms` режима. Проверочный прогон с `cycleDuration=100 ms` сохраняется только как TECH-артефакт и не используется как финальный режим сравнения.

## Метод съёма RawLogs: кандидаты

### Кандидат A: `vplc status`

Снимать строку `Длительность цикла (ms)` через CLI и формировать строки RawLogs с:

```text
timestamp_source = host_log
Tper = observed program cycle duration
quality_flag = technical_check или ok после валидации
```

Ограничение: это не обязательно каждое выполнение цикла, а наблюдение состояния VPLC.

Для TECH-проработки добавлен collector, который должен запускаться на `VPLC_HOST`:

```bash
bash scripts/linux/collect_vplc_status_rawlogs.sh \
  --out /tmp/RUN_20260509_VPLC_L3_HIGH_75_100_S01_R01_TECH.csv \
  --mode-id VPLC_L3_HIGH_75_100 \
  --series-id SER_20260509_VPLC_L3_HIGH_75_100_S01 \
  --run-id RUN_20260509_VPLC_L3_HIGH_75_100_S01_R01_TECH \
  --load-level 3 \
  --load-passes 512 \
  --t0-ms 75 \
  --deadline-ms 100 \
  --samples 60 \
  --interval-sec 1
```

Collector пишет `cycle_exec_ms` и `cycle_nominal_ms` из `vplc status`, оставляет `Tper/Jper/deadline_miss` пустыми и ставит `quality_flag=technical_check`. Такой CSV нужен для проверки автоматизации и динамики runtime status, но не используется для KPI до подтверждения смысла поля `Длительность цикла (ms)`.

Первый запуск `RUN_20260509_VPLC_L3_HIGH_75_100_S01_R01_TECH.csv` выявил локализационную проблему: `date --iso-8601=ns` на `VPLC_HOST` выдал timestamp с запятой в дробной части, что нарушило CSV-разделение. Collector обновлён на UTC-формат `YYYY-MM-DDTHH:MM:SS.NNNNNNNNNZ` через `LC_ALL=C date -u`.

Повторный запуск `RUN_20260509_VPLC_L3_HIGH_75_100_S01_R01B_TECH.csv` дал валидный CSV: 60 строк, 28 колонок, `timestamp_source=host_log`, `quality_flag=technical_check`, `Tper/Jper/deadline_miss` пустые. Для `load_level=3`, `load_passes=512` наблюдались `cycle_exec_ms` около `0.23-0.26 ms` для большинства строк и отдельные выбросы до нескольких миллисекунд. Эти значения фиксируются только как runtime status observation; без ответа производителя они не трактуются как per-cycle `Tper`.

### Кандидат B: dump/log files

Проверить файлы на `VPLC_HOST`:

```text
/var/lib/vplc/vplc_dump.dat
/var/lib/vplc/vplc_dump_dict.dat
/var/log/vplc/vplc_logs.txt
```

И CLI:

```bash
vplc --download-dump "<path>"
vplc --download-log "<path>"
vplc config set --log-changed-values <enabled|disabled>
vplc config set --logged-tags <tag1 tag2 ...>
```

Ограничение: нужно подтвердить формат и наличие времени/частоты записи.

TECH-проверка формата выполняется с инженерной Windows-машины:

```powershell
.\scripts\windows\collect_vplc_dump_log_probe.ps1
```

Скрипт сохраняет read-only probe в `vplc\masc_vplc\dump_log_probe\probe_<YYYYMMDD_HHMMSS>`: manifest со статусом VPLC, конфигом, списком файлов, первыми строками/байтами и доступные для пользователя `vkr` копии dump/log файлов. Эти файлы не считаются RawLogs и используются только для выбора метода съёма.

Результат TECH-probe `probe_20260509_162808`: `vplc_dump_dict.dat` содержит словарь переменных, `vplc_dump.dat` и `vplc_dump_prev.dat` содержат бинарные снимки значений. Дамп декодируется в текущие значения `cycle_counter`, `load_level`, `load_passes_effective`, `workload_accumulator` и других тегов, но не содержит историю строк, timestamp каждой строки или прямое значение `Tper/Jper`. Следовательно, dump/log files пригодны как источник snapshot-состояния workload и валидации тегов, но сами по себе пока не дают полноценный RawLogs-ряд, сопоставимый с Siemens DB ring-buffer.

Для воспроизводимого разбора snapshot добавлен TECH-декодер:

```powershell
.\.venv\Scripts\python.exe scripts\python\decode_vplc_dump_snapshot.py `
  --dict vplc\masc_vplc\dump_log_probe\probe_20260509_162808\downloaded_files\var_lib_vplc_vplc_dump_dict.dat `
  --dump vplc\masc_vplc\dump_log_probe\probe_20260509_162808\downloaded_files\var_lib_vplc_vplc_dump.dat
```

### Кандидат C: внешний polling переменных

Снимать значения через Studio/CLI/доступный протокол и рассчитывать периоды по времени инженерной машины.

Ограничение: такой метод будет `eng_node_poll`; его нельзя смешивать с `plc_internal_rd_loc_t_nanosecond` без явной пометки и валидации.

## Ближайший критерий готовности

VPLC-часть считается готовой к первому RawLogs-прогону, когда:

- workload собирается и запускается;
- подтверждён способ получения `Tper` или наблюдаемого cycle duration;
- для одного TECH-прогона получен CSV по `configs\rawlogs_schema_cycle_v0.yaml`;
- обработчик `scripts\python\process_cycle_rawlogs.py` принимает VPLC CSV без ручной правки.

Для практического съёма без ожидания ответа производителя используется серия `vplc status` по 1000 наблюдений на повтор. Запуск одного повтора с инженерной Windows-машины:

```powershell
.\scripts\windows\run_vplc_status_run.ps1 -ModeId VPLC_L3_HIGH_75_100 -RunNumber 1 -Samples 1000 -IntervalSec 1
```

При настроенном SSH-ключе:

```powershell
.\scripts\windows\run_vplc_status_run.ps1 `
  -ModeId VPLC_L3_HIGH_75_100 `
  -RunNumber 1 `
  -Samples 1000 `
  -IntervalSec 1 `
  -IdentityFile $env:USERPROFILE\.ssh\vkr_vplc_host_ed25519
```

Перед запуском оператор вручную выставляет `load_level` в VPLC Studio согласно выбранному `ModeId`. Скрипт формирует `RunID`, загружает collector на `VPLC_HOST`, выполняет съём и скачивает CSV в `raw_logs\vplc_status\<ModeId>\`.

Обработка VPLC status CSV выполняется отдельно от Siemens `Tper`:

```powershell
.\.venv\Scripts\python.exe scripts\python\process_vplc_status_rawlogs.py `
  --input-root raw_logs\vplc_status `
  --output-root processed_tables\vplc_status
```

Результат: `cycle_exec_*`, `cycle_exec_over_threshold`, `Rover_exec`, `Lburst_exec`. Эти метрики не называются `Tper/Jper`.

## Примечание для Главы 4

Практическое ограничение источника времени VPLC вынесено в отдельный артефакт:

```text
00_docs\chapter_4_vplc_timing_note.md
```

До ответа производителя `cycle_exec_ms` из `vplc status` рассматривается как наблюдаемый runtime-показатель длительности выполнения программы, а не как прямой аналог `Tper`. Методика режимов, повторов, порогов и RawLogs сохраняется; в практической части ВКР явно указывается различие источников времени S7 и VPLC.

С текущими данными сравнение допустимо только как ограниченное практическое сравнение по одинаковым режимам нагрузки:

- S7-1200: `Tper/Jper/deadline_miss` и производные KPI по внутреннему timestamp PLC;
- VPLC: `cycle_exec_*`, `cycle_exec_over_threshold`, `Rover_exec`, `Lburst_exec` по данным `vplc status`.

Прямое сравнение `Tper` S7 с `Tper` VPLC не выполняется, потому что VPLC-значение `Tper` не сформировано. В сравнительных таблицах и выводах `cycle_exec_ms` не подменяет `Tper`, а маркируется как отдельный наблюдаемый runtime-показатель.
