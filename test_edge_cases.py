"""Edge case and error handling tests."""
import sys
import os
import pytest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.assets import Asset, AssetType, PriceData
from src.backtester import Backtester, Portfolio
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


def run_backtest(assets, strategy_func, initial_capital=100000, strategy_name="Test"):
    backtester = Backtester(assets)
    return backtester.run(strategy_func=strategy_func, initial_capital=initial_capital, strategy_name=strategy_name)


# ============================================================================
# PORTFOLIO EDGE CASES
# ============================================================================

class TestPortfolioEdgeCases:
    def test_empty_allocation(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        strategy = Strategies.balanced_portfolio({})
        result = run_backtest(assets, strategy, initial_capital=10000)
        assert result.final_value == 10000
        assert result.total_return == 0.0

    def test_single_asset_portfolio(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        strategy = Strategies.balanced_portfolio({"AAPL": 1.0})
        result = run_backtest(assets, strategy, initial_capital=10000)
        assert result.final_value == 12000

    def test_allocation_exceeding_100_percent(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices, "GOOG": prices})
        strategy = Strategies.balanced_portfolio({"AAPL": 0.6, "GOOG": 0.5})
        with pytest.raises(ValueError, match="Total allocation exceeds 100%"):
            run_backtest(assets, strategy, initial_capital=10000)

    def test_zero_initial_capital(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        strategy = Strategies.buy_and_hold("AAPL")
        result = run_backtest(assets, strategy, initial_capital=0)
        assert result.final_value == 0
        assert result.total_return == 0.0

    def test_very_small_allocation(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        strategy = Strategies.buy_and_hold("AAPL", percent_allocation=0.0001)
        result = run_backtest(assets, strategy, initial_capital=10000)
        assert result.final_value > 0

    def test_50_assets(self):
        prices_dict = {f"ASSET_{i}": [100 + i, 110 + i, 120 + i] for i in range(50)}
        assets = create_test_assets(prices_dict)
        allocations = {f"ASSET_{i}": 0.02 for i in range(50)}
        strategy = Strategies.balanced_portfolio(allocations)
        result = run_backtest(assets, strategy, initial_capital=100000)
        assert result.final_value > 0

    def test_rsi_flat_prices(self):
        prices = [100] * 30
        assets = create_test_assets({"FLAT": prices})
        strategy = Strategies.rsi_oversold_strategy("FLAT", rsi_period=14)
        result = run_backtest(assets, strategy, initial_capital=10000)
        assert result.final_value > 0

    def test_macd_short_data(self):
        prices = [100 + i for i in range(10)]
        assets = create_test_assets({"SHORT": prices})
        strategy = Strategies.macd_strategy("SHORT", fast=5, slow=10, signal=3)
        result = run_backtest(assets, strategy, initial_capital=10000)
        assert result.final_value > 0

    def test_bollinger_short_data(self):
        prices = [100 + i for i in range(5)]
        assets = create_test_assets({"SHORT": prices})
        strategy = Strategies.bollinger_bands_strategy("SHORT", period=20)
        result = run_backtest(assets, strategy, initial_capital=10000)
        assert result.final_value > 0


# ============================================================================
# BACKTESTER EDGE CASES
# ============================================================================

class TestBacktesterEdgeCases:
    def test_empty_assets_raises(self):
        with pytest.raises(ValueError, match="Assets dictionary cannot be empty"):
            Backtester({})

    def test_negative_capital_raises(self):
        with pytest.raises(ValueError, match="Initial capital cannot be negative"):
            Portfolio(initial_capital=-1000)

    def test_invalid_strategy_func_raises(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        backtester = Backtester(assets)
        with pytest.raises(TypeError, match="strategy_func must be callable"):
            backtester.run(strategy_func="not_callable", initial_capital=10000)

    def test_negative_quantity_buy_raises(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        with pytest.raises(ValueError, match="Quantity must be positive"):
            portfolio.buy(assets["A"], -10, 100, 0)

    def test_zero_quantity_buy_raises(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        with pytest.raises(ValueError, match="Quantity must be positive"):
            portfolio.buy(assets["A"], 0, 100, 0)

    def test_negative_price_buy_raises(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        with pytest.raises(ValueError, match="Price must be positive"):
            portfolio.buy(assets["A"], 10, -100, 0)

    def test_insufficient_cash_raises(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=1000)
        with pytest.raises(ValueError, match="Insufficient cash"):
            portfolio.buy(assets["A"], 100, 100, 0)

    def test_sell_nonexistent_symbol_raises(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        with pytest.raises(ValueError, match="No position in"):
            portfolio.sell("NONEXISTENT", 10, 100)

    def test_sell_more_than_owned_raises(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        portfolio.buy(assets["A"], 10, 100, 0)
        with pytest.raises(ValueError, match="Insufficient quantity"):
            portfolio.sell("A", 20, 100)

    def test_negative_quantity_sell_raises(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        portfolio.buy(assets["A"], 10, 100, 0)
        with pytest.raises(ValueError, match="Quantity must be positive"):
            portfolio.sell("A", -5, 100)

    def test_negative_price_sell_raises(self):
        prices = [100, 110, 120]
        assets = create_test_assets({"A": prices})
        portfolio = Portfolio(initial_capital=10000)
        portfolio.buy(assets["A"], 10, 100, 0)
        with pytest.raises(ValueError, match="Price must be positive"):
            portfolio.sell("A", 5, -100)


# ============================================================================
# BACKTESTER METRICS
# ============================================================================

class TestBacktesterMetrics:
    def test_max_drawdown(self):
        from src.backtester import PortfolioSnapshot
        snapshots = [
            PortfolioSnapshot("2024-01-01", 10000, {}, 10000, 0),
            PortfolioSnapshot("2024-01-02", 11000, {}, 11000, 0.1),
            PortfolioSnapshot("2024-01-03", 10500, {}, 10500, 0.05),
            PortfolioSnapshot("2024-01-04", 12000, {}, 12000, 0.2),
            PortfolioSnapshot("2024-01-05", 9000, {}, 9000, -0.1),
        ]
        max_dd = Backtester._calculate_max_drawdown(snapshots)
        assert abs(max_dd - 0.25) < 0.01

    def test_max_drawdown_empty(self):
        assert Backtester._calculate_max_drawdown([]) == 0

    def test_sharpe_ratio(self):
        from src.backtester import PortfolioSnapshot
        snapshots = [
            PortfolioSnapshot("2024-01-01", 10000, {}, 10000, 0),
            PortfolioSnapshot("2024-01-02", 11000, {}, 11000, 0.1),
            PortfolioSnapshot("2024-01-03", 10500, {}, 10500, 0.05),
            PortfolioSnapshot("2024-01-04", 12000, {}, 12000, 0.2),
            PortfolioSnapshot("2024-01-05", 9000, {}, 9000, -0.1),
        ]
        sharpe = Backtester._calculate_sharpe_ratio(snapshots)
        assert isinstance(sharpe, float)

    def test_sharpe_ratio_single_snapshot(self):
        from src.backtester import PortfolioSnapshot
        snapshots = [PortfolioSnapshot("2024-01-01", 10000, {}, 10000, 0)]
        assert Backtester._calculate_sharpe_ratio(snapshots) == 0
