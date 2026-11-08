# Trading Bot (Paper Trading)

Ein kleiner, abhängigkeitsfreier Trading-Bot in Python (nur Standardbibliothek).
Er enthält:

- **Datenladen** aus CSV-Dateien (Spalten `date,open,high,low,close,volume`) oder synthetische Testdaten
- **Strategie**: SMA-Crossover (long, wenn der schnelle Durchschnitt über dem langsamen liegt, sonst flat)
- **Paper-Broker**: simuliert Orders, Gebühren und Positionen im Speicher
- **Backtest**: Simulation auf historischen Daten mit Rendite, Max Drawdown und Vergleich zu Buy & Hold
- **Signal-Befehl**: zeigt, was die Strategie für den nächsten Handelstag vorsieht

> **Wichtig:** Der Bot handelt nur simuliert. Es gibt keinen Broker-Anschluss und
> keinen Live-Modus. Die Ergebnisse sind keine Anlageberatung, und eine gute
> Backtest-Rendite garantiert keine künftigen Gewinne.

## Schnellstart

```bash
cd trading-bot

# Backtest mit synthetischen Daten (ohne Download)
python3 -m trading_bot backtest --synthetic

# Backtest mit eigenen Kursdaten und Parametern
python3 -m trading_bot backtest --csv prices.csv --fast 10 --slow 40 --show-trades

# Was würde die Strategie als Nächstes tun?
python3 -m trading_bot signal --csv prices.csv

# Tests
python3 -m unittest discover -s tests -v
```

Python 3.10 oder neuer. Keine Installation nötig.

## Kursdaten

Eine CSV mit einer Zeile pro Handelstag, z. B.:

```
date,open,high,low,close,volume
2024-01-02,100.0,101.5,99.2,101.0,1200000
2024-01-03,101.0,102.3,100.4,102.1,980000
```

Kursdaten bekommst du z. B. als CSV-Export von Yahoo Finance, Stooq oder
deinem Broker. Der Bot lädt keine Daten selbst herunter.

## Wie der Backtest rechnet

- Das Signal für Bar *i* wird am **Schlusskurs** von Bar *i* berechnet.
- Die Order wird am **Eröffnungskurs** von Bar *i+1* ausgeführt. So gibt es keinen Blick in die Zukunft.
- Jede Transaktion kostet eine Gebühr (Standard 0,1 %).
- Es wird immer das ganze Kapital investiert oder komplett verkauft. Kein Hebel, keine Leerverkäufe.

## Struktur

```
trading-bot/
  trading_bot/
    data.py       Bar, CSV-Laden, synthetische Daten
    strategy.py   SMA und SMA-Crossover
    broker.py     PaperBroker (Cash, Position, Gebühren)
    backtest.py   run_backtest, Max Drawdown
    cli.py        Kommandozeile
  tests/
    test_bot.py   Unit-Tests
```

## Nächste Schritte, falls du live handeln willst

Ein Live-Betrieb braucht einen Broker-Adapter (z. B. über die API deines Brokers),
eine Anbindung an Echtzeitkurse und Schutzmechanismen wie Positionslimits, Verlustgrenzen
und manuelle Freigabe. Diese Teile sind absichtlich nicht enthalten. Teste jede
Strategie zuerst lange im Paper-Modus.
