"""Price data: CSV loading and a reproducible synthetic generator for testing."""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


@dataclass(frozen=True)
class Bar:
    """One daily OHLCV bar."""

    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float


def load_csv(path: str | Path) -> list[Bar]:
    """Load daily bars from a CSV file with columns date,open,high,low,close,volume.

    Column names are matched case-insensitively, so Yahoo-style exports work too.
    """
    bars: list[Bar] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError(f"{path} is empty")
        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
        required = {"date", "open", "high", "low", "close"}
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"{path} is missing columns: {sorted(missing)}")
        for row in reader:
            bars.append(
                Bar(
                    date=date.fromisoformat(row["date"].strip()[:10]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row.get("volume") or 0.0),
                )
            )
    bars.sort(key=lambda b: b.date)
    return bars


def synthetic(
    n: int = 750,
    start: date = date(2020, 1, 1),
    start_price: float = 100.0,
    drift: float = 0.0003,
    volatility: float = 0.012,
    seed: int = 42,
) -> list[Bar]:
    """Generate a random-walk price series. Same seed, same data."""
    rng = random.Random(seed)
    bars: list[Bar] = []
    price = start_price
    day = start
    for _ in range(n):
        open_ = price
        close = price * (1.0 + rng.gauss(drift, volatility))
        high = max(open_, close) * (1.0 + abs(rng.gauss(0.0, volatility / 2)))
        low = min(open_, close) * (1.0 - abs(rng.gauss(0.0, volatility / 2)))
        bars.append(
            Bar(
                date=day,
                open=round(open_, 4),
                high=round(high, 4),
                low=round(low, 4),
                close=round(close, 4),
                volume=float(rng.randint(100_000, 1_000_000)),
            )
        )
        price = close
        day += timedelta(days=1)
    return bars
