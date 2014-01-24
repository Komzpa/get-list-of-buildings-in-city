get-list-of-buildings-in-city
=============================

Что делает:
    - доставляет список домов/адресов в городе в упрощённом формате XML;
    - приводит названия улиц в формат [улица] [сокращённая статусная часть].

Нужно:
    - postgresql/postgis;
    - furry-sansa с geocoding template

Запустить:
    python get-list-of-buildings-in-city.py

Результат:
    множество файлов "город.xml" с координатами и номерами домов и улиц.

Have fun!