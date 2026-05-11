# VPLC workload ST sources

Дата подготовки: 2026-05-09.

## Назначение

Папка содержит черновик VPLC ST-реализации workload v0.2 для зеркального сравнения с Siemens S7-1200:

```text
VPLC_WorkloadCycle_v0_2.st
VPLC_WorkloadCycle_v0_2_numbered.st
variables_v0_2.yaml
```

Файлы не являются результатом экспериментального прогона и не содержат KPI.

## TECH timing probe v0.3

После получения обновлённой документации MAX Automation добавлен отдельный TECH-пробник:

```text
VPLC_TimingProbe_v0_3.st
variables_timing_probe_v0_3.yaml
```

Он проверяет системную переменную `_milliseconds_from_start_ : LREAL` из `v0.5_Функции_MASC_ВПЛК.pdf` и считает `Tper_ms`, `Jper_ms`, `deadline_miss` внутри ST-кода. Это не замена workload v0.2, а короткая проверка, можно ли перейти к VPLC workload v0.3 с внутренним timestamp.

## Workload v0.3 с внутренним timing и кольцевым логом

Для чистого сравнения с Siemens добавлен черновик:

```text
VPLC_WorkloadCycle_v0_3_timing_log.st
variables_v0_3_timing_log.yaml
```

Он совмещает workload v0.2, timing-блок на `_milliseconds_from_start_` и кольцевой лог массивов на 1000 строк. План съёма:

1. Добавить переменные из `variables_v0_3_timing_log.yaml`.
2. Вставить код `VPLC_WorkloadCycle_v0_3_timing_log.st` в основную циклическую ST-задачу.
3. Для режима задать `load_level`, `T0_ms`, `deadline_threshold_ms`.
4. Установить `reset_log_request := TRUE`.
5. Дождаться `buffer_wrapped = TRUE` или `sample_index >= 1000`.
6. Установить `freeze_logging := TRUE`.
7. Скачать `vplc_dump.dat` и `vplc_dump_dict.dat`.
8. Конвертировать dump в RawLogs:

```powershell
.\.venv\Scripts\python.exe scripts\python\convert_vplc_dump_to_rawlogs.py `
  --dict <path-to-vplc_dump_dict.dat> `
  --dump <path-to-vplc_dump.dat> `
  --mode-id VPLC_L3_HIGH_75_100 `
  --series-id SER_20260510_VPLC_L3_HIGH_75_100_S01 `
  --run-id RUN_20260510_VPLC_L3_HIGH_75_100_S01_R01 `
  --t0-ms 75 `
  --deadline-ms 100 `
  --load-level 3 `
  --load-passes 512
```

Результат пишется в `raw_logs\vplc_internal\<ModeId>\`. Эти RawLogs уже содержат `Tper`, `Jper`, `deadline_miss` с `timestamp_source=vplc_internal`.

## Как использовать v0.2 в VPLC Studio

1. Открыть рабочий VPLC-проект или создать копию минимального проекта.
2. Добавить переменные из `variables_v0_2.yaml`.
3. В циклическую ST-задачу вставить код из `VPLC_WorkloadCycle_v0_2.st`.
4. Собрать проект.
5. Загрузить на `VPLC_HOST`.
6. Проверить, что `init_done` стал `TRUE`, а `cycle_counter`, `heartbeat`, `workload_accumulator`, `load_level_effective`, `load_passes_effective` изменяются ожидаемо.

В VPLC Studio может не быть отдельного поля стартового значения для переменной. Для этого в ST-код добавлен однократный блок инициализации по флагу `init_done`. При первом запуске он задаёт рабочие значения по умолчанию: `load_level = 0`, `T0_ms = 10.0`, `deadline_threshold_ms = 20.0`, `load_passes_level1 = 32`, `load_passes_level2 = 128`, `load_passes_level3 = 512`, `max_load_passes = 512`, `heartbeat_divisor_cycles = 100`, `accumulator_modulus = 2147483647`.

## Зафиксированные зеркальные Mode

```text
VPLC_L0_IDLE_10_20    mirrors S7_L0_IDLE_10_20
VPLC_L1_LIGHT_10_20   mirrors S7_L1_LIGHT_10_20
VPLC_L2_MEDIUM_25_35  mirrors S7_L2_MEDIUM_25_35
VPLC_L3_HIGH_75_100   mirrors S7_L3_HIGH_75_100
VPLC_L3_STRESS_75_80  mirrors S7_L3_STRESS_75_80
```

Для каждого VPLC mode должны совпадать:

- `load_level`;
- `load_passes`;
- `T0_ms`;
- `deadline_threshold_ms`;
- число повторов;
- процедура съёма RawLogs.

## Исторический вопрос по RawLogs

До подтверждения `_milliseconds_from_start_` текущий VPLC workload не писал внутренний кольцевой буфер. Рассматривались методы:

1. VPLC internal/status capture: разбор `vplc status`, если значение `Длительность цикла (ms)` можно стабильно снимать как наблюдение.
2. VPLC dump/log capture: включить логирование/дампы переменных и проверить формат файлов `vplc_dump*.dat` или `vplc_logs.txt`.
3. Внешний polling: собирать значения с инженерной машины, но такой метод должен быть помечен `eng_node_poll` и отдельно валидирован.

После подтверждения timing probe v0.3 предпочтительный путь — `VPLC_WorkloadCycle_v0_3_timing_log.st` + dump conversion.

## Ограничение

Если VPLC Studio не примет `ARRAY[0..15]`, используйте `VPLC_WorkloadCycle_v0_2_numbered.st` с переменными `int_state_0...int_state_15` и `bool_state_0...bool_state_15`.

Fallback-файл генерируется командой:

```powershell
.\.venv\Scripts\python.exe scripts\python\generate_vplc_numbered_workload.py
```
