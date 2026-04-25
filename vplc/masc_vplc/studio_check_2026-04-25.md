# Проверка VPLC Studio с VPLC_HOST

Дата проверки: 2026-04-25.

## Контекст

Проверялся штатный bare-metal workflow до контейнеризации:

```text
ENG_NODE / Windows / VPLC Studio -> VPLC_HOST / Ubuntu / VPLC 2.10.0
```

Проверка выполнялась в стендовом сегменте `192.168.10.0/24`.

## Подтверждённые параметры

```text
VPLC_HOST: 192.168.10.20
VPLC port: 1234
VPLC listen socket: 0.0.0.0:1234
VPLC Studio: 4.1.3 beta
VPLC runtime: 2.10.0
Connection mode: local network
Cloud hub: disabled
VPLC Server: not used in this check
```

## Результат

VPLC Studio успешно подключилась к VPLC runtime на `192.168.10.20:1234`.

По скриншотам подтверждено:

- на вкладке подключения выбран режим `Локальная сеть`;
- указан адрес `192.168.10.20` и порт `1234`;
- в выходных данных Studio есть сообщение `Соединение с ВПЛК установлено`;
- строка состояния Studio показывает `ВПЛК: 192.168.10.20:1234`;
- вкладка статуса отображает `vplc-1`, версию VPLC `2.10.0`, состояние программы `Остановлена`;
- `vplc status` на `VPLC_HOST` показывает 1 активное локальное соединение.

Скриншоты проверки:

```text
screenshots\VPLC Studio\03.png
screenshots\VPLC Studio\04.png
screenshots\VPLC Studio\05.png
screenshots\VPLC Studio\06.png
screenshots\VPLC Studio\07.png
screenshots\VPLC Studio\08.png
```

## Вывод

Сетевое подключение `VPLC Studio -> VPLC_HOST` подтверждено. Следующий шаг - создать минимальный проект VPLC, собрать его, загрузить в VPLC и проверить запуск программы.

Перед созданием проекта нужно использовать встроенную документацию Studio по языку ST: синтаксис, типы данных, операторы, управляющие конструкции, встроенные функции, организация программы и примеры программ.
