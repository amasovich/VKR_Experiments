# Контейнерный профиль VPLC runtime

Дата начала: 2026-04-27.

## Назначение

Эта папка предназначена для материалов пункта 11 этапа 4.0: реализации профиля запуска VPLC runtime через Podman на `VPLC_HOST`.

Текущий целевой контур:

```text
VPLC_HOST / Ubuntu 22.04.5 / Podman 3.4.4 / VPLC runtime 2.10.0
```

`VPLC Server` не входит в первый baseline-контур. Он установлен и проверен как инфраструктурный компонент, но его контейнеризация отложена отдельным решением.

## Принцип реализации

Контейнерный профиль делается после bare-metal проверки VPLC Studio -> VPLC_HOST. Это уже выполнено: минимальный проект `vkr_minimal_vplc_tes` был собран, загружен в VPLC и запущен.

Перед созданием финального `Containerfile` нужно зафиксировать фактическую структуру установленного VPLC:

- systemd unit `vplc.service`;
- команда запуска runtime внутри сервиса;
- список файлов пакета `vplc`;
- каталоги состояния, дампов, логов и конфигурации;
- порты и процессы при запущенном проекте;
- поведение `vplc config` и `vplc status` после перезагрузки.

Без этой инспекции нельзя корректно решить, запускать ли VPLC в контейнере напрямую как процесс или через systemd/supervisor-обвязку.

## Сбор фактов перед сборкой контейнера

На Windows-хосте из корня репозитория выполнить:

```powershell
.\scripts\windows\collect_vplc_container_prereq_snapshot.ps1
```

Скрипт передаёт на `VPLC_HOST` Linux-скрипт:

```text
scripts\linux\inspect_vplc_runtime_for_container.sh
```

и сохраняет результат в:

```text
configs\vplc_host_container_prereq_snapshot_2026-04-27.txt
```

Если PowerShell запросит подтверждение SSH или пароль пользователя `vkr`, это нормально.

## Загрузка профиля на VPLC_HOST

После анализа prerequisite snapshot загрузить контейнерный профиль на mini-PC:

```powershell
.\scripts\windows\deploy_vplc_container_profile.ps1
```

На `VPLC_HOST` будет создан каталог:

```text
/home/vkr/vplc_container_profile_2026-04-27
```

Скрипт загружает туда:

```text
Containerfile
build_vplc_container_image.sh
run_vplc_container_smoke.sh
```

## План профиля после инспекции

Предварительное инженерное решение:

- контейнеризируется только `vplc`, без `vplc-server`;
- сетевой режим первого профиля: `--network host`, чтобы VPLC был доступен на стендовом адресе `192.168.10.20:1234`;
- перед запуском контейнера bare-metal `vplc.service` должен быть остановлен, иначе будет конфликт порта `1234`;
- volume-каталоги фиксируются только после подтверждения фактических путей состояния VPLC;
- первый тест контейнера должен проверять не экспериментальные KPI, а функциональность: порт, `vplc config`, подключение VPLC Studio и запуск минимального проекта.

## Сборка и первый smoke-test

На `VPLC_HOST`:

```bash
cd ~/vplc_container_profile_2026-04-27
./build_vplc_container_image.sh
```

Если базового образа `ubuntu:22.04` ещё нет локально, Podman попытается скачать его. Для этого можно временно включить Wi-Fi, но перед измерениями Wi-Fi должен быть выключен.

Примечание по совместимости: на `VPLC_HOST` установлен Podman 3.4.4, поэтому в скрипте сборки используется совместимый вызов `podman build -t ...`, без `--pull=missing`.

Примечание по установке `.deb`: post-install скрипт пакета VPLC вызывает `systemctl`. В контейнерном образе systemd не используется, поэтому на время сборки создаётся временная заглушка `/usr/bin/systemctl`, которая удаляется сразу после установки пакета. Сам контейнер запускает VPLC напрямую: `/usr/local/bin/vplc --service`.

Примечание по логам: VPLC пытается писать файл `vplc-logs.txt` в текущую рабочую директорию процесса. Поэтому в образе задан `WORKDIR /var/log/vplc`, который монтируется в volume smoke-test профиля. Для rootless Podman bind-mount каталоги подключаются с опцией `:U`, чтобы пользователь `vplc` внутри контейнера получил права записи.

Перед запуском контейнера нужно остановить bare-metal сервисы, чтобы освободить порт `1234`:

```bash
sudo systemctl stop vplc.service
sudo systemctl stop vplc-server.service
```

Запуск smoke-test контейнера:

```bash
cd ~/vplc_container_profile_2026-04-27
./run_vplc_container_smoke.sh
```

После smoke-test bare-metal сервис можно вернуть:

```bash
podman rm -f vkr-vplc-runtime-smoke
sudo systemctl start vplc.service
sudo systemctl start vplc-server.service
```

## Критерии закрытия пункта 11

Пункт 11 можно считать выполненным, когда зафиксированы:

- снимок фактической структуры VPLC перед контейнеризацией;
- `Containerfile` или эквивалентный Podman-профиль запуска;
- команды сборки и запуска;
- проверка доступности VPLC из `ENG_NODE` на порту `1234`;
- проверка подключения VPLC Studio к контейнерному VPLC;
- карточка проверки контейнерного запуска;
- обновление `stage_4_0_log.md` и `stand_manifest_initial.yaml`.
