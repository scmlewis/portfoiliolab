"""Integration tests - full end-to-end backtest flows."""
import sys
import os
import pytest
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.assets import Asset, AssetType, PriceData
from src.backtester import Backtester, Portfolio, Comparator, BacktestResult
from src.strategies import Strategies


def create_test_assets(prices_dict, dates=None):
    if dates is None:
        dates = [f"2024-01-{i+1:02d}" for i in range(len(next(iter(prices_dict.values()))))]
    assets = {}
    for symbol, prices in prices_dict.items():
        assets[symbol] = Asset(
            symbol=symbol, asset_type=AssetType.STOCK,
            price_data=PriceData(dates=dates[:len(prices)], prices=prices)
        )
    return assets


# ============================================================================
# FULL BACKTEST FLOW
# ============================================================================

class TestFullBacktestFlow:
    def test_buy_hold_end_to_end(self):
        prices = [100, 105, 110, 108, 115]
        assets = create_test_assets({"AAPL": prices})
        strategy = Strategies.buy_and_hold("AAPL", percent_allocation=1.0)
        backtester = Backtester(assets)
        result = backtester.run(strategy, initial_capital=10000, strategy_name="E2E Buy&Hold")

        assert isinstance(result, BacktestResult)
        assert result.strategy_name == "E2E Buy&Hold"
        assert result.initial_capital == 10000
        assert result.final_value == 11500
        assert result.total_return == 0.15
        assert result.start_date == "2024-01-01"
        assert result.end_date == "2024-01-05"
        assert len(result.snapshots) == 5
        assert len(result.trades) == 1
        assert result.trades[0].action == "BUY"
        assert result.trades[0].symbol == "AAPL"

    def test_balanced_portfolio_end_to_end(self):
        prices_a = [100, 110, 120]
        prices_b = [100, 105, 110]
        assets = create_test_assets({"A": prices_a, "B": prices_b})
        allocations = {"A": 0.5, "B": 0.5}
        strategy = Strategies.balanced_portfolio(allocations)
        backtester = Backtester(assets)
        result = backtester.run(strategy, initial_capital=10000)

        assert result.final_value == 11500
        assert result.total_return == 0.15
        assert len(result.trades) == 2  # Two buys on day 0

    def test_momentum_end_to_end(self):
        prices = list(range(100, 160))
        assets = create_test_assets({"TREND": prices})
        strategy = Strategies.momentum_strategy(short_window=5, long_window=20)
        backtester = Backtester(assets)
        result = backtester.run(strategy, initial_capital=10000)

        assert result.final_value > 0
        assert len(result.snapshots) == 60

    def test_rsi_end_to_end(self):
        prices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55,
                  50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
        assets = create_test_assets({"RSI": prices})
        strategy = Strategies.rsi_oversold_strategy("RSI", rsi_period=5, oversold_level=30, allocation=1.0)
        backtester = Backtester(assets)
        result = backtester.run(strategy, initial_capital=10000)

        assert result.final_value > 0

    def test_macd_end_to_end(self):
        prices = [100 + i for i in range(30)] + [130 - i for i in range(20)]
        assets = create_test_assets({"MACD": prices})
        strategy = Strategies.macd_strategy("MACD", fast=5, slow=10, signal=3, allocation=1.0)
        backtester = Backtester(assets)
        result = backtester.run(strategy, initial_capital=10000)

        assert result.final_value > 0

    def test_bollinger_end_to_end(self):
        prices = [100] * 10 + [105] * 5 + [100] * 5 + [95] * 5 + [100] * 10
        assets = create_test_assets({"BOLL": prices})
        strategy = Strategies.bollinger_bands_strategy("BOLL", period=10, num_std=2.0, allocation=1.0)
        backtester = Backtester(assets)
        result = backtester.run(strategy, initial_capital=10000)

        assert result.final_value > 0

    def test_rebalance_end_to_end(self):
        prices_a = [100, 110, 105, 115, 120]
        prices_b = [100, 95, 100, 105, 110]
        assets = create_test_assets({"A": prices_a, "B": prices_b})
        allocations = {"A": 0.5, "B": 0.5}
        strategy = Strategies.rebalance_strategy(allocations, rebalance_frequency=1)
        backtester = Backtester(assets)
        result = backtester.run(strategy, initial_capital=10000)

        assert result.final_value > 0
        assert len(result.trades) > 0  # Multiple rebalance trades


# ============================================================================
# COMPARATOR
# ============================================================================

class TestComparator:
    def test_summary_output(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices, "B": prices})

        r1 = Backtester(assets).run(Strategies.buy_and_hold("A"), 10000, "Strategy A")
        r2 = Backtester(assets).run(Strategies.buy_and_hold("B"), 10000, "Strategy B")

        comp = Comparator([r1, r2])
        summary = comp.summary()
        assert "Strategy A" in summary
        assert "Strategy B" in summary
        assert "BACKTEST COMPARISON SUMMARY" in summary

    def test_get_best_return(self):
        prices_up = [100, 110, 120]
        prices_down = [100, 90, 80]
        assets_up = create_test_assets({"UP": prices_up})
        assets_down = create_test_assets({"DOWN": prices_down})

        r1 = Backtester(assets_up).run(Strategies.buy_and_hold("UP"), 10000, "Up")
        r2 = Backtester(assets_down).run(Strategies.buy_and_hold("DOWN"), 10000, "Down")

        comp = Comparator([r1, r2])
        best = comp.get_best("total_return")
        assert best.strategy_name == "Up"

    def test_get_best_sharpe(self):
        prices_a = [100, 110, 120]
        prices_b = [100, 90, 80]
        assets_a = create_test_assets({"A": prices_a})
        assets_b = create_test_assets({"B": prices_b})

        r1 = Backtester(assets_a).run(Strategies.buy_and_hold("A"), 10000, "Good")
        r2 = Backtester(assets_b).run(Strategies.buy_and_hold("B"), 10000, "Bad")

        comp = Comparator([r1, r2])
        best = comp.get_best("sharpe")
        assert best.strategy_name == "Good"

    def test_get_best_invalid_metric(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        r1 = Backtester(assets).run(Strategies.buy_and_hold("A"), 10000, "Test")
        comp = Comparator([r1])
        with pytest.raises(ValueError, match="Unknown metric"):
            comp.get_best("invalid_metric")


# ============================================================================
# TRADE LOGGING
# ============================================================================

class TestTradeLogging:
    def test_buy_creates_trade(self):
        prices = [100, 110]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        asset = assets["A"]

        portfolio.buy(asset, 50, 100, 0, date="2024-01-01")

        assert len(portfolio.trades) == 1
        t = portfolio.trades[0]
        assert t.date == "2024-01-01"
        assert t.symbol == "A"
        assert t.action == "BUY"
        assert t.quantity == 50
        assert t.price == 100
        assert t.value == 5000

    def test_sell_creates_trade(self):
        prices = [100, 110]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        asset = assets["A"]

        portfolio.buy(asset, 50, 100, 0, date="2024-01-01")
        portfolio.sell("A", 25, 110, date="2024-01-02")

        assert len(portfolio.trades) == 2
        t = portfolio.trades[1]
        assert t.date == "2024-01-02"
        assert t.action == "SELL"
        assert t.quantity == 25
        assert t.price == 110
        assert t.value == 2750

    def test_multiple_buys_averages_entry_price(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        asset = assets["A"]

        portfolio.buy(asset, 30, 100, 0)
        portfolio.buy(asset, 20, 110, 1)

        assert len(portfolio.trades) == 2
        pos = portfolio.positions["A"]
        assert pos.quantity == 50
        expected_avg = (30 * 100 + 20 * 110) / 50
        assert abs(pos.entry_price - expected_avg) < 0.01

    def test_sell_all_removes_position(self):
        prices = [100, 110]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        asset = assets["A"]

        portfolio.buy(asset, 50, 100, 0)
        portfolio.sell("A", 50, 110)

        assert "A" not in portfolio.positions
        assert portfolio.cash == 10000 - 5000 + 5500

    def test_trades_in_result(self):
        prices = [100, 105, 110]
        assets = create_test_assets({"A": prices})
        strategy = Strategies.buy_and_hold("A", percent_allocation=1.0)
        result = Backtester(assets).run(strategy, 10000)

        assert len(result.trades) == 1
        assert result.trades[0].action == "BUY"
        assert result.trades[0].symbol == "A"

    def test_rebalance_multiple_trades(self):
        prices_a = [100, 110, 105, 115, 120]
        prices_b = [100, 95, 100, 105, 110]
        assets = create_test_assets({"A": prices_a, "B": prices_b})
        strategy = Strategies.rebalance_strategy({"A": 0.5, "B": 0.5}, rebalance_frequency=1)
        result = Backtester(assets).run(strategy, 10000)

        assert len(result.trades) >= 2  # At least initial buys + rebalances


# ============================================================================
# PORTFOLIO EDGE CASES
# ============================================================================

class TestPortfolioEdgeCases:
    def test_buy_same_asset_twice_averages_price(self):
        prices = [100, 110]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)

        portfolio.buy(assets["A"], 30, 100, 0)
        portfolio.buy(assets["A"], 20, 120, 1)

        pos = portfolio.positions["A"]
        assert pos.quantity == 50
        expected = (30 * 100 + 20 * 120) / 50
        assert abs(pos.entry_price - expected) < 0.01

    def test_sell_partial_position(self):
        prices = [100, 110]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)

        portfolio.buy(assets["A"], 50, 100, 0)
        portfolio.sell("A", 20, 110)

        assert portfolio.positions["A"].quantity == 30

    def test_get_value_with_positions(self):
        prices = [100, 110]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)

        portfolio.buy(assets["A"], 50, 100, 0)
        value = portfolio.get_value(0)

        assert value == 5000 + 50 * 100  # cash + position

    def test_get_snapshot(self):
        prices = [100, 110]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)

        portfolio.buy(assets["A"], 50, 100, 0)
        snapshot = portfolio.get_snapshot("2024-01-01", 0)

        assert snapshot.date == "2024-01-01"
        assert snapshot.total_value == 10000
        assert "A" in snapshot.positions
