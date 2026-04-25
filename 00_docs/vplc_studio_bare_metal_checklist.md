# Чек-лист проверки VPLC Studio и минимального проекта

Документ уточняет ближайший рабочий шаг после проверки VPLC / VPLC Server в Linux CLI-режиме.

Цель: проверить штатный bare-metal workflow `VPLC Studio на ENG_NODE -> VPLC_HOST` до реализации контейнерного профиля Podman.

## 0. Предварительные условия

- [x] `VPLC_HOST` доступен по SSH: `ssh vkr@192.168.10.20`.
- [x] VPLC установлен на `VPLC_HOST`: версия 2.10.0.
- [x] VPLC Server установлен на `VPLC_HOST`: версия 2.7.0.
- [x] `ENG_NODE <-> VPLC_HOST` проверено ping.
- [x] Wi-Fi на `VPLC_HOST` используется только как временный сервисный канал и не должен участвовать в измерениях.

Примечание: VPLC Server установлен и проверен, но для первого baseline-контура измерений не включается. Первичная проверка Studio выполняется напрямую с VPLC runtime на `192.168.10.20:1234`; VPLC Server остаётся остановленным, если не потребуется явно.

## 1. Подготовить сетевой режим VPLC_HOST

Статус: [x] выполнено по проверкам 2026-04-25.

Перед функциональной проверкой нужно понять, какой IP видит VPLC:

```bash
vplc config
ip -br addr
ip route
```

Если VPLC показывает Wi-Fi IP `192.168.31.109`, перед рабочей проверкой нужно отключить временный Wi-Fi и повторно проверить конфигурацию.

Фактическая проверка 2026-04-25:

```text
wlo1: DOWN
enp2s0: 192.168.10.20/24
ip route: 192.168.10.0/24 dev enp2s0
vplc config: IP = 127.0.0.1
ss: VPLC listens on 0.0.0.0:1234
```

Вывод: поле IP в `vplc config` не блокирует сетевое подключение, так как порт VPLC слушает все интерфейсы (`0.0.0.0:1234`).

Ожидаемый стендовый адрес:

```text
VPLC_HOST: 192.168.10.20/24
```

## 2. Проверить сервисы и порты VPLC на mini-PC

Статус: [x] выполнено по проверкам 2026-04-25.

```bash
systemctl list-unit-files | grep -i vplc
systemctl list-units --type=service --state=running | grep -i vplc
ss -tulpn | grep -E '1234|4840|vplc'
vplc config
vplc status
vplc-server config
vplc-server status
```

Фактическая проверка 2026-04-25:

```text
VPLC:        0.0.0.0:1234, доступен с ENG_NODE
VPLC Server: порт 50530 не слушает, сервер остановлен
```

С `ENG_NODE`:

```powershell
Test-NetConnection 192.168.10.20 -Port 1234   # TcpTestSucceeded: True
Test-NetConnection 192.168.10.20 -Port 50530  # TcpTestSucceeded: False
```

## 3. Подготовить VPLC Studio на ENG_NODE

- [x] Найти установщик или portable-версию VPLC Studio.
- [x] Зафиксировать версию VPLC Studio.
- [x] Проверить запуск VPLC Studio на Windows.
- [x] Зафиксировать путь установки или запуска.

Установщик найден:

```text
D:\HOME_BASE\HOME_BASE\ВКР_МИФИ\00 - Ресёрч\02_Источники ВКР\MAX Automation\vplc-studio-setup.exe
```

Фактическая проверка 2026-04-25:

```text
VPLC Studio: 4.1.3 beta
Дата сборки: 09.04.2026 19:27:38
Скриншоты: screenshots\VPLC Studio\01.png, screenshots\VPLC Studio\02.png
```

Замечание: после запуска в строке состояния Studio отображает `ВПЛК: 127.0.0.1:1234`, поэтому подключение к удалённому `VPLC_HOST` ещё не выполнено.

## 4. Проверить подключение Studio к VPLC_HOST

Статус: [x] выполнено по скриншотам и CLI-проверке 2026-04-25.

В VPLC Studio:

- [x] добавить или найти локальный VPLC;
- [x] выбрать режим `Локальная сеть`;
- [x] указать адрес `192.168.10.20`;
- [x] указать порт `1234`;
- [x] проверить подключение.

На `VPLC_HOST` после подключения проверить:

```bash
vplc config
vplc status
ss -tulpn | grep -E '1234|vplc'
```

Фактическая проверка 2026-04-25:

```text
VPLC Studio: соединение с ВПЛК установлено
VPLC endpoint: 192.168.10.20:1234
VPLC version: 2.10.0
Program state: stopped
Active local connections: 1
Screenshots: screenshots\VPLC Studio\03.png ... screenshots\VPLC Studio\08.png
```

Примечание: `vplc config` на `VPLC_HOST` продолжает показывать IP `127.0.0.1`, но это не мешает подключению, так как VPLC слушает `0.0.0.0:1234`, а Studio успешно подключается к `192.168.10.20:1234`.

## 5. Создать минимальный тестовый проект VPLC

Статус: [x] выполнено по скриншотам и файлу проекта 2026-04-25.

Минимальный проект должен быть простым и проверяемым:

- [x] один счётчик или таймер;
- [x] один периодический элемент логики;
- [x] имя проекта латиницей;
- [x] без облачного хаба;
- [x] без внешних I/O на первом шаге;
- [ ] одна булева переменная.

Фактический проект:

```text
project file: vplc\masc_vplc\vkr_minimal_vplc_test\vkr_minimal_vplc_test.vplc
project name in Studio: vkr_minimal_vplc_tes
project description: vkr_minimal_vplc_test
project version: 1.0.1
cycle duration: 100 ms
dump interval: 10 cycles
dump saving: enabled
stop on error: enabled
Modbus TCP port: 1502
external variable: cycle_counter, UDINT / DWORD
cyclic ST task: cycle_counter := cycle_counter + 1;
```

Примечание: имя проекта сохранилось как `vkr_minimal_vplc_tes`, без последней буквы `t`. Для следующих проектов лучше использовать более короткое имя, например `vkr_vplc_min`.

Перед созданием проекта нужно свериться с документацией Studio по разделам:

- `Язык ST -> Синтаксис и лексика`;
- `Язык ST -> Типы данных`;
- `Язык ST -> Операторы`;
- `Язык ST -> Управляющие конструкции`;
- `Язык ST -> Встроенные функции`;
- `Организация программы`;
- `Примеры программ`.

Фиксация ревизии документации: `vplc/masc_vplc/st_language_review_2026-04-25.md`.

## 6. Загрузить и запустить проект

В VPLC Studio:

- [x] собрать проект;
- [x] загрузить проект на `VPLC_HOST`;
- [x] запустить выполнение.

На `VPLC_HOST` проверить:

```bash
vplc status
vplc config
```

Фиксировать:

- [x] имя программы;
- [x] версию программы, если отображается;
- [x] дату сборки, если отображается;
- [x] размер программы;
- [x] количество тегов;
- [x] длительность цикла;
- [x] состояние программы.

Фактические результаты:

```text
program status: running
program name: vkr_minimal_vplc_tes
program version: 1.0.1
program IDE build: 4.1.3
program build date: 25.04.2026 18:50:45
program size: 24.57 Kb
program cycle: about 0.056 ms / 100 ms
tags: 1
monitoring value example: cycle_counter = 1986
```

## 7. Артефакты после проверки

После успешной проверки сохранить:

- [x] снимок `vplc status`;
- [x] снимок `vplc config`;
- [x] сведения о VPLC Studio;
- [x] краткое описание минимального проекта;
- [x] скриншоты VPLC Studio, если они полезны;
- [x] обновление `configs/stand_manifest_initial.yaml`;
- [x] обновление `00_docs/stage_4_0_log.md`.

Рекомендуемые файлы:

```text
vplc/masc_vplc/studio_check_2026-04-25.md
vplc/masc_vplc/minimal_project_check_2026-04-25.md
configs/vplc_host_config_snapshot_2026-04-25_after_studio_test.txt
```

## 8. Критерий завершения

Шаг считается выполненным, если:

- [x] VPLC Studio подключается к `VPLC_HOST`;
- [x] минимальный проект создан;
- [x] проект загружен на VPLC;
- [x] программа запускается;
- [x] `vplc status` отражает загруженную программу;
- [x] результаты зафиксированы в артефактах.
