"""Command line entry point. Paper trading only.

Examples:
    python -m trading_bot backtest --synthetic
    python -m trading_bot backtest --csv prices.csv --fast 10 --slow 40
    python -m trading_bot signal --csv prices.csv
"""

from __future__ import annotations

import argparse
import sys

from .backtest import run_backtest
from .data import Bar, load_csv, synthetic
from .strategy import sma_crossover_targets


def _load(args: argparse.Namespace) -> list[Bar]:
    if args.csv:
        return load_csv(args.csv)
    return synthetic()


def _cmd_backtest(args: argparse.Namespace) -> int:
    bars = _load(args)
    result = run_backtest(
        bars,
        fast=args.fast,
        slow=args.slow,
        cash=args.cash,
        fee_rate=args.fee,
    )
    print(f"Bars:            {len(bars)} ({bars[0].date} to {bars[-1].date})")
    print(f"Strategy:        SMA crossover {args.fast}/{args.slow}, fee {args.fee:.2%}")
    print(f"Start equity:    {result.start_equity:,.2f}")
    print(f"End equity:      {result.end_equity:,.2f}")
    print(f"Strategy return: {result.total_return:+.2%}")
    print(f"Buy & hold:      {result.buy_hold_return:+.2%}")
    print(f"Max drawdown:    {result.max_drawdown:.2%}")
    print(f"Trades:          {result.num_trades}")
    if args.show_trades:
        for t in result.trades:
            print(f"  {t.when}  {t.side:4}  {t.shares:12.4f} @ {t.price:10.4f}  fee {t.fee:.2f}")
    print("\nPaper trading only. Past performance does not predict future results.")
    return 0


def _cmd_signal(args: argparse.Namespace) -> int:
    bars = _load(args)
    targets = sma_crossover_targets([b.close for b in bars], args.fast, args.slow)
    last = bars[-1]
    if len(targets) > 1 and targets[-1] != targets[-2]:
        action = "BUY at next open" if targets[-1] == 1 else "SELL at next open"
    else:
        action = "no change"
    position = "long" if targets[-1] == 1 else "flat"
    print(f"As of {last.date} (close {last.close:.4f}): target position = {position}")
    print(f"Action on the next bar: {action}")
    print("Paper trading only. This is not financial advice.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trading_bot", description="Paper-trading bot (SMA crossover).")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_data_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--csv", help="daily OHLCV CSV (date,open,high,low,close,volume)")
        p.add_argument("--synthetic", action="store_true", help="use generated test data (default if no --csv)")
        p.add_argument("--fast", type=int, default=20, help="fast SMA window (default 20)")
        p.add_argument("--slow", type=int, default=50, help="slow SMA window (default 50)")

    bt = sub.add_parser("backtest", help="simulate the strategy on historical data")
    add_data_args(bt)
    bt.add_argument("--cash", type=float, default=10_000.0, help="starting cash (default 10000)")
    bt.add_argument("--fee", type=float, default=0.001, help="fee per trade as a fraction (default 0.001)")
    bt.add_argument("--show-trades", action="store_true", help="print every simulated trade")
    bt.set_defaults(func=_cmd_backtest)

    sig = sub.add_parser("signal", help="show what the strategy wants to do next")
    add_data_args(sig)
    sig.set_defaults(func=_cmd_signal)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
