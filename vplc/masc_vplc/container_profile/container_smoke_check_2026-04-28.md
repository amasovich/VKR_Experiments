# Проверка контейнерного запуска VPLC runtime

Дата проверки: 2026-04-28.

## Цель

Проверить минимальный контейнерный профиль VPLC runtime через Podman до перехода к экспериментальным прогонам.

## Образ

```text
image: localhost/vkr-vplc-runtime:2.10.0
image id: ab5cb36e7c4c1d3a73b05825ce82a344e1796f25d2425333a6522a77c664d8aa
build time: 2026-04-28 18:18:45 UTC
```

## Контейнерный запуск

```text
container: vkr-vplc-runtime-smoke
container id: 209925adca40a58a1807979994d47f6515dc129b930446a73fe87876b480769d
network mode: host
entrypoint: /usr/local/bin/vplc --service
port: 0.0.0.0:1234
```

Перед контейнерным запуском bare-metal сервисы были остановлены:

```bash
sudo systemctl stop vplc.service
sudo systemctl stop vplc-server.service
```

## Сетевое состояние

После удаления временного Wi-Fi netplan-файла:

```text
enp2s0: UP, 192.168.10.20/24
wlo1: DOWN
route: only 192.168.10.0/24 via enp2s0
```

Проверка с `ENG_NODE`:

```powershell
Test-NetConnection 192.168.10.20 -Port 1234
TcpTestSucceeded : True
SourceAddress    : 192.168.10.30
InterfaceAlias   : Ethernet 2
```

## Логи и volume

Первичная ошибка записи `vplc-logs.txt` была устранена за счёт:

- `WORKDIR /var/log/vplc` в `Containerfile`;
- volume mount с опцией `:U` в `run_vplc_container_smoke.sh`.

После повторного запуска ошибка записи в лог отсутствует, файл создан:

```text
~/vplc_container_data/log/vplc_logs.txt
```

## Результат

Контейнерный smoke-test VPLC runtime подтверждён на уровне:

- сборки образа;
- запуска контейнера;
- доступности порта `1234` в стендовом сегменте;
- отключенного Wi-Fi;
- записи лог-файла в volume.

## Проверка VPLC Studio

Проверка выполнена оператором с `ENG_NODE` в VPLC Studio.

По скриншотам подтверждено:

```text
VPLC endpoint: 192.168.10.20:1234
Connection status: connected
Program status: running
Program name: vkr_minimal_vplc_tes
Program version: 1.0.7
IDE build: 4.1.3
Program build date: 28.04.2026 21:33:39
Program size: 24.57 Kb
Tags: 1
Connections: 1 local / 0 cloud
External variable: cycle_counter
```

На скриншоте мониторинга внешних переменных видно изменение `cycle_counter`, что подтверждает выполнение загруженной тестовой ST-программы в контейнерном VPLC runtime.

Скриншоты:

```text
screenshots\VPLC Studio\02\01.png
screenshots\VPLC Studio\02\02.png
screenshots\VPLC Studio\02\03.png
screenshots\VPLC Studio\02\04.png
```

Примечание: оператор упомянул тестовую программу `project_vplc_1.vplc`, но по заголовку VPLC Studio на скриншотах фактически открыт файл `vplc\masc_vplc\vkr_minimal_vplc_test\vkr_minimal_vplc_test.vplc`. Файл `project_vplc_1.vplc` в рабочей папке имеет нулевой размер и не фиксируется как подтверждённый проектный артефакт.

## Итог

Контейнерный профиль VPLC runtime функционально подтверждён:

- контейнерный VPLC доступен из стендовой сети;
- VPLC Studio подключается к контейнерному runtime;
- тестовая программа загружается и запускается;
- мониторинг внешней переменной работает.

Наблюдение из VPLC Studio: во время визуальной smoke-проверки цикл программы отображался около `0.066 / 100 ms`. Это значение фиксируется только как функциональное наблюдение smoke-test и не используется как экспериментальный KPI.

Финальный snapshot контейнерного режима:

```text
configs\vplc_host_container_smoke_snapshot_2026-04-28.txt
```

Snapshot подтверждает:

- bare-metal сервисы `vplc.service` и `vplc-server.service` находятся в состоянии `inactive`;
- контейнер `vkr-vplc-runtime-smoke` запущен из образа `localhost/vkr-vplc-runtime:2.10.0`;
- контейнер работает в режиме `network=host`;
- порт `0.0.0.0:1234` слушает;
- в логах контейнера зафиксированы подключение VPLC Studio, загрузка программы и запуск программы;
- в volume-каталоге сохранены файлы загруженной программы, дампы и `vplc_logs.txt`.
