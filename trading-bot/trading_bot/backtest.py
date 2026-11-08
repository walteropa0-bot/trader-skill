"""Backtest a strategy on historical bars, with fills at the next bar's open."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .broker import PaperBroker, Trade
from .data import Bar
from .strategy import sma_crossover_targets


@dataclass
class BacktestResult:
    start_equity: float
    end_equity: float
    buy_hold_return: float
    max_drawdown: float
    equity_curve: list[tuple[date, float]] = field(default_factory=list)
    trades: list[Trade] = field(default_factory=list)

    @property
    def total_return(self) -> float:
        return self.end_equity / self.start_equity - 1.0

    @property
    def num_trades(self) -> int:
        return len(self.trades)


def max_drawdown(values: list[float]) -> float:
    """Largest peak-to-trough drop, as a positive fraction (0.25 = -25%)."""
    peak = float("-inf")
    worst = 0.0
    for v in values:
        peak = max(peak, v)
        if peak > 0:
            worst = max(worst, (peak - v) / peak)
    return worst


def run_backtest(
    bars: list[Bar],
    fast: int = 20,
    slow: int = 50,
    cash: float = 10_000.0,
    fee_rate: float = 0.001,
) -> BacktestResult:
    """Run the SMA crossover on bars.

    The decision for bar i is made on its close and executed at the open of bar i+1.
    """
    if len(bars) < 2:
        raise ValueError("need at least 2 bars")

    targets = sma_crossover_targets([b.close for b in bars], fast, slow)
    broker = PaperBroker(cash=cash, fee_rate=fee_rate)
    curve: list[tuple[date, float]] = []

    for i, bar in enumerate(bars):
        if i > 0:
            if targets[i - 1] == 1:
                broker.buy_all(bar.open, bar.date)
            else:
                broker.sell_all(bar.open, bar.date)
        curve.append((bar.date, broker.equity(bar.close)))

    values = [v for _, v in curve]
    return BacktestResult(
        start_equity=cash,
        end_equity=values[-1],
        buy_hold_return=bars[-1].close / bars[0].close - 1.0,
        max_drawdown=max_drawdown(values),
        equity_curve=curve,
        trades=list(broker.trades),
    )
