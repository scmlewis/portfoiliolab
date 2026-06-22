"""Tests for Portfolio Optimizer and Monte Carlo Simulator."""
import sys
import os
import pytest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portfolio_optimizer import PortfolioOptimizer, calculate_returns_from_prices
from monte_carlo import PortfolioMonteCarloSimulator, calculate_rolling_metrics


# ============================================================================
# CALCULATE RETURNS
# ============================================================================

class TestCalculateReturns:
    def test_basic(self):
        prices = [100, 105, 110, 108, 115]
        returns = calculate_returns_from_prices(prices)
        assert len(returns) == len(prices) - 1

    def test_values(self):
        prices = [100, 105, 110, 108, 115]
        returns = calculate_returns_from_prices(prices)
        expected = [0.05, 0.0476, -0.0182, 0.0648]
        for actual, exp in zip(returns, expected):
            assert abs(actual - exp) < 0.001

    def test_single_price(self):
        returns = calculate_returns_from_prices([100])
        assert returns == []

    def test_two_prices(self):
        returns = calculate_returns_from_prices([100, 110])
        assert len(returns) == 1
        assert abs(returns[0] - 0.10) < 0.001


# ============================================================================
# PORTFOLIO OPTIMIZER
# ============================================================================

class TestPortfolioOptimizer:
    @pytest.fixture
    def optimizer(self):
        np.random.seed(42)
        returns_a = np.random.normal(0.001, 0.02, 252).tolist()
        returns_b = np.random.normal(0.0005, 0.015, 252).tolist()
        return PortfolioOptimizer({"STOCK_A": returns_a, "STOCK_B": returns_b})

    def test_max_sharpe_weights_sum_to_one(self, optimizer):
        result = optimizer.optimize_max_sharpe()
        assert abs(sum(result.weights.values()) - 1.0) < 0.001

    def test_max_sharpe_has_required_fields(self, optimizer):
        result = optimizer.optimize_max_sharpe()
        assert 'STOCK_A' in result.weights
        assert 'STOCK_B' in result.weights
        assert isinstance(result.expected_return, float)
        assert isinstance(result.volatility, float)
        assert isinstance(result.sharpe_ratio, float)

    def test_min_variance_weights_sum_to_one(self, optimizer):
        result = optimizer.optimize_min_variance()
        assert abs(sum(result.weights.values()) - 1.0) < 0.001

    def test_min_variance_lower_volatility(self, optimizer):
        sharpe = optimizer.optimize_max_sharpe()
        minvar = optimizer.optimize_min_variance()
        assert minvar.volatility <= sharpe.volatility

    def test_efficient_frontier(self, optimizer):
        frontier = optimizer.efficient_frontier(num_points=10)
        assert len(frontier) == 10
        for point in frontier:
            if hasattr(point, 'weights'):
                assert abs(sum(point.weights.values()) - 1.0) < 0.01
            elif isinstance(point, tuple) and len(point) >= 2:
                weights = point[1]
                if isinstance(weights, dict):
                    assert abs(sum(weights.values()) - 1.0) < 0.01

    def test_correlation_matrix(self, optimizer):
        corr = optimizer.get_correlation_matrix()
        assert 'STOCK_A' in corr
        assert 'STOCK_B' in corr
        assert abs(corr['STOCK_A']['STOCK_B'] - corr['STOCK_B']['STOCK_A']) < 0.001

    def test_asset_statistics(self, optimizer):
        stats = optimizer.get_asset_statistics()
        assert 'STOCK_A' in stats
        assert 'STOCK_B' in stats
        for sym in ['STOCK_A', 'STOCK_B']:
            assert 'return' in stats[sym]
            assert 'volatility' in stats[sym]
            assert stats[sym]['volatility'] > 0


# ============================================================================
# MONTE CARLO SIMULATOR
# ============================================================================

class TestMonteCarloSimulator:
    @pytest.fixture
    def simulator(self):
        np.random.seed(42)
        returns_a = np.random.normal(0.001, 0.02, 252).tolist()
        returns_b = np.random.normal(0.0005, 0.015, 252).tolist()
        return PortfolioMonteCarloSimulator(
            {"STOCK_A": returns_a, "STOCK_B": returns_b},
            {"STOCK_A": 0.6, "STOCK_B": 0.4}
        )

    def test_basic_simulation(self, simulator):
        results = simulator.simulate(num_simulations=100, days=30, initial_value=100000)
        assert 'num_simulations' in results
        assert 'statistics' in results
        assert results['num_simulations'] == 100

    def test_statistics_structure(self, simulator):
        results = simulator.simulate(num_simulations=100, days=30, initial_value=100000)
        stats = results['statistics']
        assert 'mean_final_value' in stats
        assert 'median_final_value' in stats

    def test_final_values_count(self, simulator):
        results = simulator.simulate(num_simulations=50, days=30, initial_value=100000)
        assert len(results['final_values']) == 50

    def test_percentile_keys(self, simulator):
        results = simulator.simulate(num_simulations=100, days=30, initial_value=100000)
        pcts = results.get('percentile_final_values', results.get('percentiles', {}))
        assert len(pcts) > 0

    def test_simulation_paths(self, simulator):
        results = simulator.simulate(num_simulations=10, days=30, initial_value=100000)
        if 'simulations' in results:
            assert len(results['simulations']) == 10
            for sim in results['simulations']:
                assert len(sim['values']) == 30


# ============================================================================
# ROLLING METRICS
# ============================================================================

class TestRollingMetrics:
    def test_basic(self):
        np.random.seed(42)
        snapshots = []
        value = 100000
        for i in range(50):
            value *= (1 + np.random.normal(0.001, 0.01))
            snapshots.append({'date': f'2024-01-{i+1:02d}', 'value': value, 'returns': 0.001})

        results = calculate_rolling_metrics(snapshots, window=20)
        assert 'rolling_sharpe' in results
        assert 'rolling_returns' in results
        assert 'rolling_volatility' in results
        assert 'window' in results
        assert results['window'] == 20

    def test_output_lengths(self):
        np.random.seed(42)
        snapshots = []
        value = 100000
        for i in range(60):
            value *= (1 + np.random.normal(0.001, 0.01))
            snapshots.append({'date': f'2024-01-{i+1:02d}', 'value': value, 'returns': 0.001})

        results = calculate_rolling_metrics(snapshots, window=20)
        assert len(results['rolling_sharpe']) > 0
        assert len(results['rolling_returns']) > 0
        assert len(results['rolling_volatility']) > 0
        assert len(results['rolling_sharpe']) == len(results['rolling_returns'])
        assert len(results['rolling_returns']) == len(results['rolling_volatility'])

    def test_all_volatilities_positive(self):
        np.random.seed(42)
        snapshots = []
        value = 100000
        for i in range(50):
            value *= (1 + np.random.normal(0.001, 0.01))
            snapshots.append({'date': f'2024-01-{i+1:02d}', 'value': value, 'returns': 0.001})

        results = calculate_rolling_metrics(snapshots, window=20)
        for v in results['rolling_volatility']:
            assert v >= 0
