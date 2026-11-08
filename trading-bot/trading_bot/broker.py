"""Paper broker: simulates fills and fees in memory. It never talks to a real exchange."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Trade:
    when: date
    side: str  # "BUY" or "SELL"
    price: float
    shares: float
    fee: float


class PaperBroker:
    """Holds cash and a single position. Each order goes all-in or all-out."""

    def __init__(self, cash: float = 10_000.0, fee_rate: float = 0.001) -> None:
        if cash <= 0:
            raise ValueError("cash must be positive")
        if not 0 <= fee_rate < 1:
            raise ValueError("fee_rate must be in [0, 1)")
        self.cash = cash
        self.fee_rate = fee_rate
        self.shares = 0.0
        self.trades: list[Trade] = []

    def equity(self, price: float) -> float:
        return self.cash + self.shares * price

    def buy_all(self, price: float, when: date) -> None:
        """Spend all cash on shares, paying the fee out of the same cash."""
        if self.shares > 0 or self.cash <= 0:
            return
        shares = self.cash / (price * (1.0 + self.fee_rate))
        fee = shares * price * self.fee_rate
        self.cash -= shares * price + fee
        self.shares += shares
        self.trades.append(Trade(when, "BUY", price, shares, fee))

    def sell_all(self, price: float, when: date) -> None:
        """Sell the whole position and keep proceeds minus the fee."""
        if self.shares <= 0:
            return
        proceeds = self.shares * price
        fee = proceeds * self.fee_rate
        self.cash += proceeds - fee
        self.trades.append(Trade(when, "SELL", price, self.shares, fee))
        self.shares = 0.0
