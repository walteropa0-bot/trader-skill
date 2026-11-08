"""Trading strategies. A strategy turns prices into a target position per bar."""

from __future__ import annotations

from collections.abc import Sequence


def sma(values: Sequence[float], window: int) -> list[float | None]:
    """Simple moving average. Entries before the first full window are None."""
    if window < 1:
        raise ValueError("window must be >= 1")
    out: list[float | None] = [None] * len(values)
    running = 0.0
    for i, value in enumerate(values):
        running += value
        if i >= window:
            running -= values[i - window]
        if i >= window - 1:
            out[i] = running / window
    return out


def sma_crossover_targets(closes: Sequence[float], fast: int = 20, slow: int = 50) -> list[int]:
    """Target position per bar: 1 = be long, 0 = be flat.

    Long while the fast SMA is above the slow SMA, flat otherwise.
    The value at index i uses only closes[0..i], so there is no look-ahead.
    """
    if fast >= slow:
        raise ValueError("fast window must be shorter than slow window")
    fast_ma = sma(closes, fast)
    slow_ma = sma(closes, slow)
    targets: list[int] = []
    state = 0
    for f, s in zip(fast_ma, slow_ma):
        if f is not None and s is not None:
            state = 1 if f > s else 0
        targets.append(state)
    return targets
