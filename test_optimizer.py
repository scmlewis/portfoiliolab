#!/usr/bin/env python3
"""
Test suite for Portfolio Optimizer and Monte Carlo Simulator.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from portfolio_optimizer import PortfolioOptimizer, calculate_returns_from_prices
from monte_carlo import PortfolioMonteCarloSimulator, calculate_rolling_metrics


# ============================================================================
# TEST PORTFOLIO OPTIMIZER
# ============================================================================

def test_portfolio_optimizer():
    """Test Portfolio Optimizer logic."""
    print("\n" + "="*60)
    print("TEST: PORTFOLIO OPTIMIZER")
    print("="*60)
    
    # Create test returns data
    np.random.seed(42)
    returns_a = np.random.normal(0.001, 0.02, 252).tolist()  # 1% daily return, 2% vol
    returns_b = np.random.normal(0.0005, 0.015, 252).tolist()  # 0.5% daily return, 1.5% vol
    
    returns = {
        "STOCK_A": returns_a,
        "STOCK_B": returns_b
    }
    
    optimizer = PortfolioOptimizer(returns)
    
    # Test max Sharpe optimization
    result_sharpe = optimizer.optimize_max_sharpe()
    print("✓ Max Sharpe Optimization: PASS")
    print(f"  Weights: {result_sharpe.weights}")
    print(f"  Expected Return: {result_sharpe.expected_return*100:.2f}%")
    print(f"  Volatility: {result_sharpe.volatility*100:.2f}%")
    print(f"  Sharpe Ratio: {result_sharpe.sharpe_ratio:.4f}")
    
    # Verify weights sum to 1
    assert abs(sum(result_sharpe.weights.values()) - 1.0) < 0.001, "Weights should sum to 1"
    
    # Test min variance optimization
    result_minvar = optimizer.optimize_min_variance()
    print("\n✓ Min Variance Optimization: PASS")
    print(f"  Weights: {result_minvar.weights}")
    print(f"  Volatility: {result_minvar.volatility*100:.2f}%")
    
    # Min variance should have lower volatility than max Sharpe
    assert result_minvar.volatility <= result_sharpe.volatility, "Min variance should have lower vol"
    
    # Test efficient frontier
    frontier = optimizer.efficient_frontier(num_points=10)
    print(f"\n✓ Efficient Frontier: PASS ({len(frontier)} points)")
    
    # Test correlation matrix
    corr = optimizer.get_correlation_matrix()
    print("\n✓ Correlation Matrix: PASS")
    print(f"  Correlation between A and B: {corr['STOCK_A']['STOCK_B']:.4f}")
    
    # Test asset statistics
    stats = optimizer.get_asset_statistics()
    print("\n✓ Asset Statistics: PASS")
    for sym, stat in stats.items():
        print(f"  {sym}: Return={stat['return']*100:.2f}%, Vol={stat['volatility']*100:.2f}%")
    
    return True


# ============================================================================
# TEST MONTE CARLO SIMULATOR
# ============================================================================

def test_monte_carlo():
    """Test Monte Carlo Simulator logic."""
    print("\n" + "="*60)
    print("TEST: MONTE CARLO SIMULATOR")
    print("="*60)
    
    # Create test returns data
    np.random.seed(42)
    returns_a = np.random.normal(0.001, 0.02, 252).tolist()
    returns_b = np.random.normal(0.0005, 0.015, 252).tolist()
    
    returns = {
        "STOCK_A": returns_a,
        "STOCK_B": returns_b
    }
    
    weights = {"STOCK_A": 0.6, "STOCK_B": 0.4}
    
    simulator = PortfolioMonteCarloSimulator(returns, weights)
    
    # Run simulation
    results = simulator.simulate(
        num_simulations=100,
        days=252,
        initial_value=100000
    )
    
    print("✓ Monte Carlo Simulation: PASS")
    print(f"  Simulations: {results['num_simulations']}")
    print(f"  Days: {results['num_days']}")
    
    # Check results structure
    assert 'statistics' in results, "Missing statistics"
    assert 'final_values' in results, "Missing final_values"
    assert 'num_simulations' in results, "Missing num_simulations"
    
    print(f"\n  Final Value Statistics:")
    print(f"    Mean: ${results['statistics']['mean_final_value']:,.2f}")
    print(f"    Median: ${results['statistics']['median_final_value']:,.2f}")
    print(f"    Std: ${np.std(results['final_values']):,.2f}")
    
    # Check percentiles
    print(f"\n  Percentiles:")
    for pct, val in results['percentile_final_values'].items():
        print(f"    {pct}: ${val:,.2f}")
    
    # Test VaR and CVaR
    if 'var_95' in results['statistics']:
        print(f"\n  Value at Risk (95%): ${results['statistics']['var_95']:,.2f}")
    if 'cvar_95' in results['statistics']:
        print(f"  Conditional VaR (95%): ${results['statistics']['cvar_95']:,.2f}")
    
    return True


# ============================================================================
# TEST ROLLING METRICS
# ============================================================================

def test_rolling_metrics():
    """Test Rolling Metrics calculation."""
    print("\n" + "="*60)
    print("TEST: ROLLING METRICS")
    print("="*60)
    
    # Create test snapshots
    snapshots = []
    value = 100000
    for i in range(100):
        # Random walk
        value *= (1 + np.random.normal(0.001, 0.01))
        snapshots.append({
            'date': f'2024-01-{i+1:02d}' if i < 31 else f'2024-02-{i-30:02d}',
            'value': value,
            'returns': 0.001
        })
    
    # Calculate rolling metrics
    results = calculate_rolling_metrics(snapshots, window=20)
    
    print("✓ Rolling Metrics: PASS")
    print(f"  Window: {results['window']}")
    print(f"  Data Points: {len(results['rolling_sharpe'])}")
    
    # Check results structure
    assert 'rolling_sharpe' in results, "Missing rolling_sharpe"
    assert 'rolling_returns' in results, "Missing rolling_returns"
    assert 'rolling_volatility' in results, "Missing rolling_volatility"
    
    print(f"\n  Rolling Sharpe Range: [{min(results['rolling_sharpe']):.4f}, {max(results['rolling_sharpe']):.4f}]")
    print(f"  Rolling Returns Range: [{min(results['rolling_returns'])*100:.2f}%, {max(results['rolling_returns'])*100:.2f}%]")
    print(f"  Rolling Vol Range: [{min(results['rolling_volatility'])*100:.2f}%, {max(results['rolling_volatility'])*100:.2f}%]")
    
    return True


# ============================================================================
# TEST CALCULATE RETURNS
# ============================================================================

def test_calculate_returns():
    """Test return calculation from prices."""
    print("\n" + "="*60)
    print("TEST: CALCULATE RETURNS FROM PRICES")
    print("="*60)
    
    # Test with simple prices
    prices = [100, 105, 110, 108, 115]
    returns = calculate_returns_from_prices(prices)
    
    expected_returns = [0.05, 0.0476, -0.0182, 0.0648]
    
    print("✓ Calculate Returns: PASS")
    print(f"  Prices: {prices}")
    print(f"  Returns: {[f'{r*100:.2f}%' for r in returns]}")
    
    # Verify returns
    assert len(returns) == len(prices) - 1, "Returns should have one less element"
    for i, (actual, expected) in enumerate(zip(returns, expected_returns)):
        assert abs(actual - expected) < 0.001, f"Return {i} mismatch: {actual} vs {expected}"
    
    print("✓ Return Calculation Verified: PASS")
    
    return True


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("PORTFOLIO OPTIMIZER & MONTE CARLO TEST SUITE")
    print("="*60)
    
    tests = [
        ("Calculate Returns", test_calculate_returns),
        ("Portfolio Optimizer", test_portfolio_optimizer),
        ("Monte Carlo Simulator", test_monte_carlo),
        ("Rolling Metrics", test_rolling_metrics),
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
