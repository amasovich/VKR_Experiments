# Ревизия prerequisite snapshot перед контейнеризацией VPLC

Дата снимка: 2026-04-27  
Источник: `configs\vplc_host_container_prereq_snapshot_2026-04-27.txt`

## Подтверждённая конфигурация VPLC_HOST

```text
OS: Ubuntu 22.04.5 LTS
Kernel: 5.15.0-119-generic
Podman: 3.4.4
Podman runtime: crun
Podman mode: rootless
Stand interface: enp2s0, 192.168.10.20/24
Wi-Fi: wlo1 DOWN
```

## VPLC runtime

Пакет:

```text
vplc 2.10.0 amd64
```

systemd unit:

```text
/etc/systemd/system/vplc.service
ExecStart=/usr/local/bin/vplc --service
User=vplc
Group=vplc
```

Writable-каталоги штатного сервиса:

```text
/var/lib/vplc
/var/cache/vplc
/var/log/vplc
/run/vplc
```

Сетевой порт:

```text
0.0.0.0:1234/tcp
```

Вывод: для первого контейнерного профиля не требуется запускать systemd внутри контейнера. Достаточно установить пакет `vplc` в образ и запускать `/usr/local/bin/vplc --service` от пользователя `vplc`.

## VPLC Server

Пакет `vplc-server 2.7.0` установлен, systemd-сервис активен, но по CLI сам сервер находится в состоянии `остановлен`, порт `50530` не слушает.

Для пункта 11 VPLC Server не контейнеризируется. Это соответствует DEC-003 и DEC-005.

## Следствие для Containerfile

Принятый первый профиль:

```text
base image: ubuntu:22.04
installed package: vplc_latest_amd64.deb
entrypoint: /usr/local/bin/vplc --service
workdir: /var/log/vplc
network: host
port: 1234/tcp
volumes:
  /var/lib/vplc
  /var/cache/vplc
  /var/log/vplc
```

Перед запуском контейнера bare-metal сервис `vplc.service` должен быть остановлен, иначе будет конфликт порта `1234`.
