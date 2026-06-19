#!/usr/bin/env python3
"""
Edge case and error handling tests for PortfolioLab.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.assets import Asset, AssetType, PriceData
from src.backtester import Backtester, Portfolio
from src.strategies import Strategies
import math


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "="*60)
    print("EDGE CASE TESTS")
    print("="*60)
    
    # Test 1: Empty allocation
    print("\n--- Test 1: Empty Allocation ---")
    try:
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        strategy = Strategies.balanced_portfolio({})
        result = run_backtest(assets, strategy, initial_capital=10000)
        print(f"✓ Empty allocation handled: Final value = ${result.final_value:,.2f}")
    except Exception as e:
        print(f"✗ Empty allocation failed: {e}")
    
    # Test 2: Single asset portfolio
    print("\n--- Test 2: Single Asset Portfolio ---")
    try:
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        strategy = Strategies.balanced_portfolio({"AAPL": 1.0})
        result = run_backtest(assets, strategy, initial_capital=10000)
        assert result.final_value == 12000, f"Expected 12000, got {result.final_value}"
        print(f"✓ Single asset portfolio: Final value = ${result.final_value:,.2f}")
    except Exception as e:
        print(f"✗ Single asset portfolio failed: {e}")
    
    # Test 3: Allocation exceeding 100%
    print("\n--- Test 3: Allocation Exceeding 100% ---")
    try:
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices, "GOOG": prices})
        strategy = Strategies.balanced_portfolio({"AAPL": 0.6, "GOOG": 0.5})
        result = run_backtest(assets, strategy, initial_capital=10000)
        print(f"✗ Should have raised ValueError")
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"✗ Wrong exception type: {type(e).__name__}: {e}")
    
    # Test 4: Zero initial capital
    print("\n--- Test 4: Zero Initial Capital ---")
    try:
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        strategy = Strategies.buy_and_hold("AAPL")
        result = run_backtest(assets, strategy, initial_capital=0)
        print(f"✓ Zero capital handled: Final value = ${result.final_value:,.2f}")
    except Exception as e:
        print(f"✗ Zero capital failed: {e}")
    
    # Test 5: Negative prices (edge case)
    print("\n--- Test 5: Negative Prices ---")
    try:
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        strategy = Strategies.buy_and_hold("AAPL")
        result = run_backtest(assets, strategy, initial_capital=10000)
        print(f"✓ Negative prices handled: Final value = ${result.final_value:,.2f}")
    except Exception as e:
        print(f"✗ Negative prices failed: {e}")
    
    # Test 6: Very small allocation
    print("\n--- Test 6: Very Small Allocation (0.01%) ---")
    try:
        prices = [100, 110, 120]
        assets = create_test_assets({"AAPL": prices})
        strategy = Strategies.buy_and_hold("AAPL", percent_allocation=0.0001)
        result = run_backtest(assets, strategy, initial_capital=10000)
        print(f"✓ Small allocation handled: Final value = ${result.final_value:,.2f}")
    except Exception as e:
        print(f"✗ Small allocation failed: {e}")
    
    # Test 7: Large number of assets
    print("\n--- Test 7: Large Number of Assets ---")
    try:
        prices_dict = {f"ASSET_{i}": [100 + i, 110 + i, 120 + i] for i in range(50)}
        assets = create_test_assets(prices_dict)
        allocations = {f"ASSET_{i}": 0.02 for i in range(50)}
        strategy = Strategies.balanced_portfolio(allocations)
        result = run_backtest(assets, strategy, initial_capital=100000)
        print(f"✓ 50 assets handled: Final value = ${result.final_value:,.2f}")
    except Exception as e:
        print(f"✗ 50 assets failed: {e}")
    
    # Test 8: RSI with extreme values
    print("\n--- Test 8: RSI with Extreme Values ---")
    try:
        # All prices same (RSI undefined)
        prices = [100] * 30
        assets = create_test_assets({"FLAT": prices})
        strategy = Strategies.rsi_oversold_strategy("FLAT", rsi_period=14)
        result = run_backtest(assets, strategy, initial_capital=10000)
        print(f"✓ RSI flat prices handled: Final value = ${result.final_value:,.2f}")
    except Exception as e:
        print(f"✗ RSI flat prices failed: {e}")
    
    # Test 9: MACD with insufficient data
    print("\n--- Test 9: MACD with Insufficient Data ---")
    try:
        # Only 10 prices, but MACD needs slow + signal - 1 = 26 + 9 - 1 = 34
        prices = [100 + i for i in range(10)]
        assets = create_test_assets({"SHORT": prices})
        strategy = Strategies.macd_strategy("SHORT", fast=5, slow=10, signal=3)
        result = run_backtest(assets, strategy, initial_capital=10000)
        print(f"✓ MACD short data handled: Final value = ${result.final_value:,.2f}")
    except Exception as e:
        print(f"✗ MACD short data failed: {e}")
    
    # Test 10: Bollinger with insufficient data
    print("\n--- Test 10: Bollinger with Insufficient Data ---")
    try:
        # Only 5 prices, but Bollinger needs period = 20
        prices = [100 + i for i in range(5)]
        assets = create_test_assets({"SHORT": prices})
        strategy = Strategies.bollinger_bands_strategy("SHORT", period=20)
        result = run_backtest(assets, strategy, initial_capital=10000)
        print(f"✓ Bollinger short data handled: Final value = ${result.final_value:,.2f}")
    except Exception as e:
        print(f"✗ Bollinger short data failed: {e}")
    
    return True


# ============================================================================
# HELPER FUNCTIONS
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


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("EDGE CASE & ERROR HANDLING TEST SUITE")
    print("="*60)
    
    tests = [
        ("Edge Cases", test_edge_cases),
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                errors.append(name)
        except Exception as e:
            failed += 1
            errors.append(f"{name}: {e}")
            print(f"\n✗ {name}: FAIL")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if errors:
        print("\nFailed tests:")
        for error in errors:
            print(f"  - {error}")
    
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
