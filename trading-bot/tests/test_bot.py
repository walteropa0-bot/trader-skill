import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trading_bot.backtest import max_drawdown, run_backtest  # noqa: E402
from trading_bot.broker import PaperBroker  # noqa: E402
from trading_bot.data import Bar, load_csv, synthetic  # noqa: E402
from trading_bot.strategy import sma, sma_crossover_targets  # noqa: E402


def flat_bars(prices, opens=None):
    opens = opens or prices
    start = date(2024, 1, 1)
    return [
        Bar(start + timedelta(days=i), o, p, p, p, 1.0)
        for i, (o, p) in enumerate(zip(opens, prices))
    ]


class StrategyTests(unittest.TestCase):
    def test_sma_values(self):
        self.assertEqual(sma([1, 2, 3, 4], 2), [None, 1.5, 2.5, 3.5])

    def test_targets_do_not_look_ahead(self):
        closes = [10, 10, 10, 10, 10, 20, 20, 20, 20, 20]
        full = sma_crossover_targets(closes, 2, 4)
        for i in range(len(closes)):
            prefix = sma_crossover_targets(closes[: i + 1], 2, 4)
            self.assertEqual(full[i], prefix[-1], f"look-ahead at index {i}")

    def test_fast_must_be_shorter_than_slow(self):
        with self.assertRaises(ValueError):
            sma_crossover_targets([1, 2, 3], 5, 5)


class BrokerTests(unittest.TestCase):
    def test_round_trip_costs_fees(self):
        broker = PaperBroker(cash=1000, fee_rate=0.01)
        d = date(2024, 1, 1)
        broker.buy_all(100, d)
        broker.sell_all(100, d)
        # Buy: 1000 cash buys 1000 / 1.01 worth of shares at 100; sell returns that value minus 1%.
        self.assertAlmostEqual(broker.cash, 1000 / 1.01 * 0.99, places=6)
        self.assertEqual(broker.shares, 0)

    def test_no_double_buy(self):
        broker = PaperBroker(cash=1000, fee_rate=0)
        broker.buy_all(10, date(2024, 1, 1))
        broker.buy_all(10, date(2024, 1, 2))
        self.assertEqual(len(broker.trades), 1)


class BacktestTests(unittest.TestCase):
    def test_flat_market_has_no_return_and_no_trades(self):
        bars = flat_bars([100.0] * 60)
        result = run_backtest(bars, fast=5, slow=10, cash=1000, fee_rate=0.001)
        self.assertEqual(result.num_trades, 0)
        self.assertAlmostEqual(result.total_return, 0.0)

    def test_fill_happens_at_next_open(self):
        # The crossover is seen on the close of bar 10 and must fill at the open of bar 11 (200).
        closes = [100.0] * 10 + [110.0] * 10
        opens = [100.0] * 11 + [200.0] + [110.0] * 8
        bars = flat_bars(closes, opens)
        result = run_backtest(bars, fast=2, slow=5, cash=1000, fee_rate=0)
        self.assertTrue(result.trades)
        self.assertEqual(result.trades[0].side, "BUY")
        self.assertEqual(result.trades[0].price, 200.0)

    def test_max_drawdown(self):
        self.assertAlmostEqual(max_drawdown([100, 150, 75, 120]), 0.5)
        self.assertEqual(max_drawdown([1, 2, 3]), 0.0)

    def test_synthetic_is_reproducible(self):
        self.assertEqual(synthetic(n=50, seed=1), synthetic(n=50, seed=1))
        self.assertNotEqual(synthetic(n=50, seed=1), synthetic(n=50, seed=2))


class CsvTests(unittest.TestCase):
    def test_load_csv_is_case_insensitive_and_sorted(self):
        import tempfile

        content = "Date,Open,High,Low,Close,Volume\n2024-01-02,2,3,1,2.5,100\n2024-01-01,1,2,0.5,1.5,90\n"
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            fh.write(content)
            path = fh.name
        bars = load_csv(path)
        self.assertEqual([b.date for b in bars], [date(2024, 1, 1), date(2024, 1, 2)])
        self.assertEqual(bars[1].close, 2.5)


if __name__ == "__main__":
    unittest.main()
