## Abhängigkeiten

* ```redis```
* ```python3-redis```
* ```python3-bluez```

## Verwendung
* In ```scan.py``` und ```logger.py``` den Hostname der Redis-Installation angeben.
* ```sudo ./scan.py``` führt den Scan durch und trägt die Ergebnisse in die Redis-Datenbank ein.
* ```./looger.py``` zeigt die Inhalte der Redis-Datenbank in der Konsole an.

## Ausgabe

* 1. Spalte: Dauer des Kontakts
* 2. Spalte: Rolling Proximity Identifier
* 3. Spalte: Anzahl der empfangenen Beacons

![Beispiel-Ausgabe](https://imgur.com/download/fdQfqo9/)
