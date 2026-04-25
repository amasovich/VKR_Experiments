# Проверка минимального проекта VPLC

Дата проверки: 2026-04-25.

## Файлы проекта

```text
vplc\masc_vplc\vkr_minimal_vplc_test\vkr_minimal_vplc_test.vplc
vplc\masc_vplc\vkr_minimal_vplc_test\vkr_minimal_vplc_test.vplc-backup
vplc\masc_vplc\vkr_minimal_vplc_test\vkr_minimal_vplc_test.vplc-shm
vplc\masc_vplc\vkr_minimal_vplc_test\vkr_minimal_vplc_test.vplc-wal
```

Основной файл `.vplc` является SQLite-базой проекта.

## Параметры проекта

Параметры, подтверждённые по скриншоту Studio и структуре `.vplc`:

```text
schema_version: 4.1.3
name: vkr_minimal_vplc_tes
description: vkr_minimal_vplc_test
version: 1.0.1
cycleDuration: 100 ms
dumpInterval: 10 cycles
createDump: true
showLogs: false
stopOnError: true
memorySize: 1024 words
modbusPort: 1502
password: empty
```

Примечание: имя проекта в поле `name` сохранилось как `vkr_minimal_vplc_tes`, без последней буквы `t`. Похоже, поле имени проекта в Studio ограничено по длине. Для дальнейших проектов лучше использовать более короткие имена, например `vkr_vplc_min`.

## Переменные

Создана одна внешняя переменная:

```text
name: cycle_counter
dest: external
type: UDINT
runtime representation: DWORD
```

## Программа

Создана одна циклическая задача:

```text
task: new_task
type: cyclic
language: ST
code: cycle_counter := cycle_counter + 1;
```

## Результат сборки и загрузки

По выходным данным Studio:

```text
Проект собран и готов к загрузке в ВПЛК
Программа ВПЛК загружена, размер: 25160
Программа ВПЛК запущена
Переданы значения всех переменных
```

По статусу Studio:

```text
VPLC endpoint: 192.168.10.20:1234
Program status: running
Program cycle: about 0.056 ms / 100 ms
Tags: 1
Connections: 1 local / 0 cloud
Program name: vkr_minimal_vplc_tes
Program version: 1.0.1
Program IDE build: 4.1.3
Program build date: 25.04.2026 18:50:45
Program size: 24.57 Kb
Dump saving: enabled
Dump archive saving: disabled
External value sending: only changed values
```

В мониторинге внешних переменных подтверждено изменение `cycle_counter`; на скриншоте значение достигло `1986`.

## Скриншоты

```text
screenshots\vkr_minimal_vplc_test\01.png
screenshots\vkr_minimal_vplc_test\02.png
screenshots\vkr_minimal_vplc_test\03.png
screenshots\vkr_minimal_vplc_test\04.png
```

## Вывод

Минимальный ST-проект создан, собран, загружен в VPLC и запущен. Базовый bare-metal workflow `VPLC Studio -> VPLC_HOST -> running ST task` подтверждён.

Следующий технический шаг: снять текстовый snapshot `vplc status`, `vplc config` и, при необходимости, проверить наличие dump-файлов на `VPLC_HOST`.

## CLI snapshot

Текстовый snapshot после запуска проекта сохранён:

```text
configs\vplc_host_config_snapshot_2026-04-25_after_studio_test.txt
```

Snapshot подтверждает:

- `enp2s0` активен с адресом `192.168.10.20/24`;
- `wlo1` отключён;
- VPLC слушает `0.0.0.0:1234`;
- программа VPLC работает;
- имя программы `vkr_minimal_vplc_tes`;
- версия программы `1.0.1`;
- версия IDE сборки программы `4.1.3`;
- дата сборки `25.04.2026, 18:50:45`;
- размер программы `25160`;
- длительность цикла `0.051/100 ms`;
- количество тегов `1`;
- VPLC Server установлен, но остановлен.
