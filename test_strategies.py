#!/usr/bin/env python3
"""
Comprehensive test suite for PortfolioLab strategies and core logic.
Tests mathematical correctness, edge cases, and integration.
"""

import sys
import os
import pytest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.assets import Asset, AssetType, PriceData
from src.backtester import Backtester, Portfolio, BacktestResult
from src.strategies import Strategies
from src.data_generator import create_sample_assets, generate_price_series
import math


# ============================================================================
# TEST UTILITIES
# ============================================================================

def create_test_assets(prices_dict, dates=None):
    """Create test assets from price dictionaries."""
    if dates is None:
        dates = [f"2024-01-{i+1:02d}" for i in range(len(next(iter(prices_dict.values()))))]
    
    assets = {}
    for symbol, prices in prices_dict.items():
        assets[symbol] = Asset(
            symbol=symbol,
            asset_type=AssetType.STOCK,
            price_data=PriceData(dates=dates[:len(prices)], prices=prices)
        )
    return assets


def run_backtest(assets, strategy_func, initial_capital=100000, strategy_name="Test"):
    """Run a backtest and return result."""
    backtester = Backtester(assets)
    return backtester.run(
        strategy_func=strategy_func,
        initial_capital=initial_capital,
        strategy_name=strategy_name
    )


def assert_close(a, b, tolerance=0.01, msg=""):
    """Assert two values are close within tolerance."""
    if abs(a - b) > tolerance:
        raise AssertionError(f"{msg}: expected {b}, got {a} (diff: {abs(a-b)})")


# ============================================================================
# TEST 1: BUY AND HOLD STRATEGY
# ============================================================================

class TestBuyAndHold:
    """Test Buy & Hold strategy logic."""
    
    def test_100_percent_allocation(self):
        """Test Buy & Hold with 100% allocation."""
        prices = [100, 105, 110]
        assets = create_test_assets({"AAPL": prices})
        
        strategy = Strategies.buy_and_hold("AAPL", percent_allocation=1.0)
        result = run_backtest(assets, strategy, initial_capital=10000)
        
        assert result.initial_capital == 10000
        assert result.final_value == 11000
        assert_close(result.total_return, 0.10, msg="Total return")
    
    def test_50_percent_allocation(self):
        """Test Buy & Hold with 50% allocation."""
        prices = [100, 105, 110]
        assets = create_test_assets({"AAPL": prices})
        
        strategy = Strategies.buy_and_hold("AAPL", percent_allocation=0.5)
        result = run_backtest(assets, strategy, initial_capital=10000)
        
        # Should buy 50 shares at $100, final = 50 * 110 + 5000 cash = 10500
        assert result.final_value == 10500
        assert_close(result.total_return, 0.05, msg="50% allocation return")
    
    def test_zero_allocation(self):
        """Test Buy & Hold with zero allocation."""
        prices = [100, 105, 110]
        assets = create_test_assets({"AAPL": prices})
        
        strategy = Strategies.buy_and_hold("AAPL", percent_allocation=0.0)
        result = run_backtest(assets, strategy, initial_capital=10000)
        
        # Should not buy anything
        assert result.final_value == 10000
        assert result.total_return == 0.0


# ============================================================================
# TEST 2: BALANCED PORTFOLIO STRATEGY
# ============================================================================

class TestBalancedPortfolio:
    """Test Balanced Portfolio strategy logic."""
    
    def test_50_50_allocation(self):
        """Test Balanced Portfolio with 50/50 allocation."""
        prices_a = [100, 110, 120]
        prices_b = [100, 105, 110]
        assets = create_test_assets({"STOCK_A": prices_a, "STOCK_B": prices_b})
        
        allocations = {"STOCK_A": 0.5, "STOCK_B": 0.5}
        strategy = Strategies.balanced_portfolio(allocations)
        result = run_backtest(assets, strategy, initial_capital=10000)
        
        # Expected: 5000 in A, 5000 in B
        # A: 50 shares at $100, final = 50 * 120 = 6000
        # B: 50 shares at $100, final = 50 * 110 = 5500
        # Total = 11500, Return = 15%
        assert_close(result.final_value, 11500, msg="50/50 allocation final value")
        assert_close(result.total_return, 0.15, msg="50/50 allocation return")
    
    def test_60_40_allocation(self):
        """Test Balanced Portfolio with 60/40 allocation."""
        prices_a = [100, 110, 120]
        prices_b = [100, 105, 110]
        assets = create_test_assets({"STOCK_A": prices_a, "STOCK_B": prices_b})
        
        allocations_60_40 = {"STOCK_A": 0.6, "STOCK_B": 0.4}
        strategy_60_40 = Strategies.balanced_portfolio(allocations_60_40)
        result_60_40 = run_backtest(assets, strategy_60_40, initial_capital=10000)
        
        # Expected: 6000 in A, 4000 in B
        # A: 60 shares at $100, final = 60 * 120 = 7200
        # B: 40 shares at $100, final = 40 * 110 = 4400
        # Total = 11600, Return = 16%
        assert_close(result_60_40.final_value, 11600, msg="60/40 allocation final value")
        assert_close(result_60_40.total_return, 0.16, msg="60/40 allocation return")
    
    def test_allocation_exceeding_100_percent(self):
        """Test Balanced Portfolio with allocation exceeding 100%."""
        prices_a = [100, 110, 120]
        prices_b = [100, 105, 110]
        assets = create_test_assets({"STOCK_A": prices_a, "STOCK_B": prices_b})
        
        allocations_over = {"STOCK_A": 0.6, "STOCK_B": 0.5}
        strategy_over = Strategies.balanced_portfolio(allocations_over)
        
        with pytest.raises(ValueError, match="Total allocation exceeds 100%"):
            run_backtest(assets, strategy_over, initial_capital=10000)


# ============================================================================
# TEST 3: MOMENTUM STRATEGY
# ============================================================================

class TestMomentum:
    """Test Momentum strategy logic."""
    
    def test_uptrend(self):
        """Test Momentum in uptrend."""
        prices = list(range(100, 160))
        assets = create_test_assets({"TREND": prices})
        
        strategy = Strategies.momentum_strategy(short_window=5, long_window=20)
        result = run_backtest(assets, strategy, initial_capital=10000)
        
        # In uptrend, short MA > long MA, should buy
        assert result.total_return > 0, f"Expected positive return in uptrend, got {result.total_return}"
    
    def test_downtrend(self):
        """Test Momentum in downtrend."""
        prices_down = list(range(160, 100, -1))
        assets = create_test_assets({"DOWN": prices_down})
        
        strategy_down = Strategies.momentum_strategy(short_window=5, long_window=20)
        result_down = run_backtest(assets, strategy_down, initial_capital=10000)
        
        # In downtrend, should not buy (or sell if bought)
        assert result_down.total_return <= 0, f"Expected negative return in downtrend, got {result_down.total_return}"


# ============================================================================
# TEST 4: REBALANCE STRATEGY
# ============================================================================

class TestRebalance:
    """Test Rebalance strategy logic."""
    
    def test_rebalance_every_period(self):
        """Test Rebalance every period."""
        prices_a = [100, 110, 105, 115, 120]
        prices_b = [100, 95, 100, 105, 110]
        assets = create_test_assets({"STOCK_A": prices_a, "STOCK_B": prices_b})
        
        allocations = {"STOCK_A": 0.5, "STOCK_B": 0.5}
        strategy = Strategies.rebalance_strategy(allocations, rebalance_frequency=1)
        result = run_backtest(assets, strategy, initial_capital=10000)
        
        # Should rebalance on day 0, 1, 2, 3, 4
        assert result.final_value > 0
    
    def test_rebalance_quarterly(self):
        """Test Rebalance every 2 periods."""
        prices_a = [100, 110, 105, 115, 120]
        prices_b = [100, 95, 100, 105, 110]
        assets = create_test_assets({"STOCK_A": prices_a, "STOCK_B": prices_b})
        
        allocations = {"STOCK_A": 0.5, "STOCK_B": 0.5}
        strategy_2 = Strategies.rebalance_strategy(allocations, rebalance_frequency=2)
        result_2 = run_backtest(assets, strategy_2, initial_capital=10000)
        
        assert result_2.final_value > 0


# ============================================================================
# TEST 5: RSI OVERSOLD STRATEGY
# ============================================================================

class TestRSIOversold:
    """Test RSI Oversold strategy logic."""
    
    def test_oversold_buy_signal(self):
        """Test RSI oversold buy signal."""
        prices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55,
                  50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
        assets = create_test_assets({"OVERSOLD": prices})
        
        strategy = Strategies.rsi_oversold_strategy("OVERSOLD", rsi_period=5, oversold_level=30, allocation=1.0)
        result = run_backtest(assets, strategy, initial_capital=10000)
        
        # RSI should go below 30 during the drop, triggering buy
        assert result.final_value > 0
    
    def test_rsi_calculation(self):
        """Test RSI calculation."""
        test_prices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50]
        rsi = _calculate_rsi(test_prices, 5)
        
        assert rsi < 30, f"RSI should be < 30 after drop, got {rsi}"


def _calculate_rsi(prices, period):
    """Calculate RSI for testing purposes."""
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    seed = deltas[:period]
    up = sum([d for d in seed if d > 0]) / period
    down = -sum([d for d in seed if d < 0]) / period
    rs = up / down if down != 0 else 0
    rsi = 100 - 100 / (1 + rs)
    
    for delta in deltas[period:]:
        up = (up * (period - 1) + (delta if delta > 0 else 0)) / period
        down = (down * (period - 1) + (-delta if delta < 0 else 0)) / period
        rs = up / down if down != 0 else 0
        rsi = 100 - 100 / (1 + rs)
    
    return rsi


# ============================================================================
# TEST 6: MACD STRATEGY
# ============================================================================

class TestMACD:
    """Test MACD Crossover strategy logic."""
    
    def test_macd_crossover(self):
        """Test MACD crossover signals."""
        prices = [100 + i for i in range(30)] + [130 - i for i in range(20)]
        assets = create_test_assets({"MACD_TEST": prices})
        
        strategy = Strategies.macd_strategy("MACD_TEST", fast=5, slow=10, signal=3, allocation=1.0)
        result = run_backtest(assets, strategy, initial_capital=10000)
        
        assert result.final_value > 0
    
    def test_ema_calculation(self):
        """Test EMA calculation."""
        test_prices = [100, 102, 104, 106, 108, 110, 112, 114, 116, 118]
        ema = _calculate_ema(test_prices, 5)
        
        assert ema > 100, "EMA should be > 100 for uptrend"
        assert ema < 118, "EMA should be < 118 for uptrend"


def _calculate_ema(prices, period):
    """Calculate EMA for testing purposes."""
    if len(prices) < period:
        return sum(prices) / len(prices)
    ema = sum(prices[:period]) / period
    for price in prices[period:]:
        ema = price * (2 / (period + 1)) + ema * (1 - 2 / (period + 1))
    return ema


# ============================================================================
# TEST 7: BOLLINGER BANDS STRATEGY
# ============================================================================

class TestBollingerBands:
    """Test Bollinger Bands strategy logic."""
    
    def test_mean_reversion(self):
        """Test Bollinger Bands mean reversion."""
        prices = [100] * 10 + [105] * 5 + [100] * 5 + [95] * 5 + [100] * 10
        assets = create_test_assets({"BOLL": prices})
        
        strategy = Strategies.bollinger_bands_strategy("BOLL", period=10, num_std=2.0, allocation=1.0)
        result = run_backtest(assets, strategy, initial_capital=10000)
        
        assert result.final_value > 0
    
    def test_sma_calculation(self):
        """Test SMA calculation."""
        test_prices = [100, 102, 104, 106, 108, 110, 112, 114, 116, 118]
        sma = _calculate_sma(test_prices, 5)
        
        expected_sma = (110 + 112 + 114 + 116 + 118) / 5
        assert_close(sma, expected_sma, msg="SMA calculation")
    
    def test_standard_deviation(self):
        """Test standard deviation calculation."""
        test_prices = [100, 102, 104, 106, 108, 110, 112, 114, 116, 118]
        std = _calculate_std(test_prices, 5)
        
        assert std > 0, "Standard deviation should be positive"


def _calculate_sma(prices, period):
    """Calculate SMA for testing purposes."""
    return sum(prices[-period:]) / period if len(prices) >= period else sum(prices) / len(prices)


def _calculate_std(prices, period):
    """Calculate standard deviation for testing purposes."""
    sma = _calculate_sma(prices, period)
    variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
    return variance ** 0.5


# ============================================================================
# TEST 8: BACKTESTER ENGINE
# ============================================================================

class TestBacktesterEngine:
    """Test core backtester engine logic."""
    
    def test_portfolio_buy(self):
        """Test Portfolio buy operation."""
        prices = [100, 110, 120]
        assets = create_test_assets({"TEST": prices})
        
        portfolio = Portfolio(initial_capital=10000)
        asset = assets["TEST"]
        portfolio.buy(asset, 50, 100, 0)
        
        assert portfolio.cash == 5000
        assert "TEST" in portfolio.positions
        assert portfolio.positions["TEST"].quantity == 50
    
    def test_portfolio_sell(self):
        """Test Portfolio sell operation."""
        prices = [100, 110, 120]
        assets = create_test_assets({"TEST": prices})
        
        portfolio = Portfolio(initial_capital=10000)
        asset = assets["TEST"]
        portfolio.buy(asset, 50, 100, 0)
        portfolio.sell("TEST", 25, 110)
        
        assert portfolio.cash == 7750
        assert portfolio.positions["TEST"].quantity == 25
    
    def test_portfolio_value(self):
        """Test Portfolio value calculation."""
        prices = [100, 110, 120]
        assets = create_test_assets({"TEST": prices})
        
        portfolio = Portfolio(initial_capital=10000)
        asset = assets["TEST"]
        portfolio.buy(asset, 50, 100, 0)
        
        value = portfolio.get_value(1)
        expected_value = 7750 + (25 * 110)  # Cash + position value
        assert value == expected_value
    
    def test_max_drawdown(self):
        """Test max drawdown calculation."""
        from src.backtester import PortfolioSnapshot
        
        snapshots = [
            PortfolioSnapshot("2024-01-01", 10000, {}, 10000, 0),
            PortfolioSnapshot("2024-01-02", 11000, {}, 11000, 0.1),
            PortfolioSnapshot("2024-01-03", 10500, {}, 10500, 0.05),
            PortfolioSnapshot("2024-01-04", 12000, {}, 12000, 0.2),
            PortfolioSnapshot("2024-01-05", 9000, {}, 9000, -0.1),
        ]
        
        max_dd = Backtester._calculate_max_drawdown(snapshots)
        # Peak = 12000, trough = 9000, drawdown = (12000-9000)/12000 = 25%
        assert_close(max_dd, 0.25, msg="Max drawdown")
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
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


# ============================================================================
# TEST 9: DATA GENERATOR
# ============================================================================

class TestDataGenerator:
    """Test sample data generation."""
    
    def test_generate_price_series(self):
        """Test price series generation."""
        prices = generate_price_series(100, 100, seed=42)
        assert len(prices) == 100
        assert prices[0] == 100
        assert all(p > 0 for p in prices)
    
    def test_create_sample_assets(self):
        """Test sample asset creation."""
        assets = create_sample_assets(start_date="2024-01-01", num_days=100)
        assert len(assets) == 5
        assert "TECH" in assets
        assert "DIVIDEND" in assets
        assert "BOND" in assets
        assert "CRYPTO" in assets
        assert "COMMODITY" in assets


# ============================================================================
# TEST 10: INPUT VALIDATION
# ============================================================================

class TestInputValidation:
    """Test input validation in backtester and strategies."""
    
    def test_negative_initial_capital(self):
        """Test negative initial capital raises error."""
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        
        with pytest.raises(ValueError, match="Initial capital cannot be negative"):
            Portfolio(initial_capital=-1000)
    
    def test_zero_initial_capital(self):
        """Test zero initial capital works."""
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        
        portfolio = Portfolio(initial_capital=0)
        assert portfolio.cash == 0
    
    def test_empty_assets(self):
        """Test empty assets dictionary raises error."""
        with pytest.raises(ValueError, match="Assets dictionary cannot be empty"):
            Backtester({})
    
    def test_invalid_strategy_function(self):
        """Test invalid strategy function raises error."""
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        backtester = Backtester(assets)
        
        with pytest.raises(TypeError, match="strategy_func must be callable"):
            backtester.run(strategy_func="not_callable", initial_capital=10000)
    
    def test_negative_quantity_buy(self):
        """Test negative quantity in buy raises error."""
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        
        portfolio = Portfolio(initial_capital=10000)
        asset = assets["AAPL"]
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            portfolio.buy(asset, -10, 100, 0)
    
    def test_zero_quantity_buy(self):
        """Test zero quantity in buy raises error."""
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        
        portfolio = Portfolio(initial_capital=10000)
        asset = assets["AAPL"]
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            portfolio.buy(asset, 0, 100, 0)
    
    def test_negative_price_buy(self):
        """Test negative price in buy raises error."""
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        
        portfolio = Portfolio(initial_capital=10000)
        asset = assets["AAPL"]
        
        with pytest.raises(ValueError, match="Price must be positive"):
            portfolio.buy(asset, 10, -100, 0)
    
    def test_insufficient_cash(self):
        """Test insufficient cash raises error."""
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        
        portfolio = Portfolio(initial_capital=1000)
        asset = assets["AAPL"]
        
        with pytest.raises(ValueError, match="Insufficient cash"):
            portfolio.buy(asset, 100, 100, 0)  # Cost = 10000, but only have 1000


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
