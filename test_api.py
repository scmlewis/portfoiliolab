"""Flask API endpoint tests."""
import sys
import os
import pytest
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


# ============================================================================
# STATIC ENDPOINTS
# ============================================================================

class TestStaticEndpoints:
    def test_index(self, client):
        r = client.get('/')
        assert r.status_code == 200

    def test_asset_types(self, client):
        r = client.get('/api/asset-types')
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert 'value' in data[0]
        assert 'label' in data[0]

    def test_strategies(self, client):
        r = client.get('/api/strategies')
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)
        ids = [s['id'] for s in data]
        assert 'buy_hold_single' in ids
        assert 'balanced' in ids
        assert 'momentum' in ids
        for s in data:
            assert 'id' in s
            assert 'name' in s
            assert 'params' in s
            assert isinstance(s['params'], list)

    def test_default_symbols(self, client):
        r = client.get('/api/default-symbols')
        assert r.status_code == 200
        data = r.get_json()
        assert 'symbols' in data
        assert 'descriptions' in data
        assert isinstance(data['symbols'], list)
        assert len(data['symbols']) > 0


# ============================================================================
# SYMBOL AUTOCOMPLETE
# ============================================================================

class TestSymbolAutocomplete:
    def test_empty_query_returns_popular(self, client):
        r = client.get('/api/symbols-autocomplete?q=')
        assert r.status_code == 200
        data = r.get_json()
        assert 'results' in data
        assert len(data['results']) > 0
        for item in data['results']:
            assert 'symbol' in item
            assert 'name' in item
            assert 'category' in item

    def test_no_query_returns_popular(self, client):
        r = client.get('/api/symbols-autocomplete')
        assert r.status_code == 200
        data = r.get_json()
        assert len(data['results']) > 0

    def test_query_by_symbol(self, client):
        r = client.get('/api/symbols-autocomplete?q=AAPL')
        assert r.status_code == 200
        data = r.get_json()
        symbols = [item['symbol'] for item in data['results']]
        assert 'AAPL' in symbols

    def test_query_by_name(self, client):
        r = client.get('/api/symbols-autocomplete?q=apple')
        assert r.status_code == 200
        data = r.get_json()
        symbols = [item['symbol'] for item in data['results']]
        assert 'AAPL' in symbols

    def test_no_results(self, client):
        r = client.get('/api/symbols-autocomplete?q=ZZZZZ_NONEXISTENT')
        assert r.status_code == 200
        data = r.get_json()
        assert data['results'] == []

    def test_max_results_limit(self, client):
        r = client.get('/api/symbols-autocomplete?q=A')
        assert r.status_code == 200
        data = r.get_json()
        assert len(data['results']) <= 20


class TestPopularSymbols:
    def test_returns_popular(self, client):
        r = client.get('/api/popular-symbols')
        assert r.status_code == 200
        data = r.get_json()
        assert 'symbols' in data
        assert len(data['symbols']) > 0
        for item in data['symbols']:
            assert 'symbol' in item
            assert 'name' in item


# ============================================================================
# BACKTEST ENDPOINT
# ============================================================================

class TestBacktestEndpoint:
    def test_missing_body(self, client):
        r = client.post('/api/backtest', content_type='application/json')
        assert r.status_code in (400, 500)

    def test_no_strategy(self, client):
        r = client.post('/api/backtest', json={'symbols': ['AAPL']})
        assert r.status_code == 400

    def test_buy_hold_with_sample_data(self, client):
        r = client.post('/api/backtest', json={
            'symbols': ['TECH'],
            'strategy_id': 'buy_hold_single',
            'strategy_params': {'symbol': 'TECH'},
            'use_real_data': False,
            'initial_capital': 10000,
            'num_days': 30
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data['success'] is True
        result = data['result']
        assert 'strategy_name' in result
        assert 'initial_capital' in result
        assert 'final_value' in result
        assert 'total_return' in result
        assert 'annual_return' in result
        assert 'max_drawdown' in result
        assert 'sharpe_ratio' in result
        assert 'snapshots' in result
        assert 'trades' in result
        assert result['initial_capital'] == 10000
        assert isinstance(result['snapshots'], list)
        assert isinstance(result['trades'], list)

    def test_balanced_with_sample_data(self, client):
        r = client.post('/api/backtest', json={
            'symbols': ['TECH', 'DIVIDEND'],
            'strategy_id': 'balanced',
            'strategy_params': {'allocation_json': '{"TECH": 0.5, "DIVIDEND": 0.5}'},
            'use_real_data': False,
            'initial_capital': 100000,
            'num_days': 30
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data['success'] is True
        assert data['result']['final_value'] > 0

    def test_momentum_with_sample_data(self, client):
        r = client.post('/api/backtest', json={
            'symbols': ['AAPL'],
            'strategy_id': 'momentum',
            'strategy_params': {'short_window': '5', 'long_window': '20'},
            'use_real_data': False,
            'initial_capital': 10000,
            'num_days': 60
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data['success'] is True

    def test_rebalance_with_sample_data(self, client):
        r = client.post('/api/backtest', json={
            'symbols': ['TECH', 'DIVIDEND'],
            'strategy_id': 'rebalance',
            'strategy_params': {'allocation_json': '{"TECH": 0.5, "DIVIDEND": 0.5}', 'frequency': '10'},
            'use_real_data': False,
            'initial_capital': 10000,
            'num_days': 30
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data['success'] is True

    def test_trades_recorded(self, client):
        r = client.post('/api/backtest', json={
            'symbols': ['TECH'],
            'strategy_id': 'buy_hold_single',
            'strategy_params': {'symbol': 'TECH'},
            'use_real_data': False,
            'initial_capital': 10000,
            'num_days': 5
        })
        data = r.get_json()
        assert data['success'] is True
        trades = data['result']['trades']
        assert len(trades) > 0
        for t in trades:
            assert 'date' in t
            assert 'symbol' in t
            assert 'action' in t
            assert 'quantity' in t
            assert 'price' in t
            assert 'value' in t
            assert t['action'] in ('BUY', 'SELL')

    def test_invalid_strategy_id(self, client):
        r = client.post('/api/backtest', json={
            'symbols': ['AAPL'],
            'strategy_id': 'nonexistent',
            'use_real_data': False,
            'initial_capital': 10000
        })
        assert r.status_code == 400

    def test_initial_capital_minimum(self, client):
        r = client.post('/api/backtest', json={
            'symbols': ['TECH'],
            'strategy_id': 'buy_hold_single',
            'strategy_params': {'symbol': 'TECH'},
            'use_real_data': False,
            'initial_capital': 100,
            'num_days': 10
        })
        data = r.get_json()
        if data['success']:
            assert data['result']['initial_capital'] >= 1000


# ============================================================================
# COMPARE ENDPOINT
# ============================================================================

class TestCompareEndpoint:
    def test_missing_body(self, client):
        r = client.post('/api/compare', content_type='application/json')
        assert r.status_code in (400, 500)

    def test_no_strategies(self, client):
        r = client.post('/api/compare', json={'symbols': ['AAPL']})
        assert r.status_code == 400

    def test_compare_two_strategies(self, client):
        r = client.post('/api/compare', json={
            'symbols': ['TECH', 'DIVIDEND'],
            'use_real_data': False,
            'initial_capital': 10000,
            'num_days': 30,
            'strategies': [
                {'strategy_id': 'buy_hold_single', 'name': 'Buy & Hold', 'params': {'symbol': 'TECH'}},
                {'strategy_id': 'balanced', 'name': 'Balanced', 'params': {'allocation_json': '{"TECH":0.5,"DIVIDEND":0.5}'}}
            ]
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data['success'] is True
        assert len(data['results']) == 2
        assert 'best_return' in data
        assert 'best_sharpe' in data
        assert 'best_dd' in data

    def test_compare_with_invalid_strategy_skipped(self, client):
        r = client.post('/api/compare', json={
            'symbols': ['TECH'],
            'use_real_data': False,
            'initial_capital': 10000,
            'num_days': 30,
            'strategies': [
                {'strategy_id': 'buy_hold_single', 'name': 'Buy & Hold', 'params': {'symbol': 'TECH'}},
                {'strategy_id': 'nonexistent', 'name': 'Invalid', 'params': {}}
            ]
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data['success'] is True
        assert len(data['results']) == 1


# ============================================================================
# MONTE CARLO ENDPOINT
# ============================================================================

class TestMonteCarloEndpoint:
    def test_missing_body(self, client):
        r = client.post('/api/monte-carlo', content_type='application/json')
        assert r.status_code in (400, 500)

    def test_no_symbols(self, client):
        r = client.post('/api/monte-carlo', json={'symbols': []})
        assert r.status_code == 400

    def test_basic_simulation(self, client):
        r = client.post('/api/monte-carlo', json={
            'symbols': ['AAPL', 'MSFT'],
            'num_simulations': 100,
            'num_days': 30,
            'initial_value': 100000
        })
        assert r.status_code == 200
        data = r.get_json()
        assert 'num_simulations' in data
        assert 'statistics' in data

    def test_custom_weights(self, client):
        r = client.post('/api/monte-carlo', json={
            'symbols': ['AAPL', 'MSFT'],
            'num_simulations': 100,
            'num_days': 30,
            'initial_value': 100000,
            'weights': {'AAPL': 0.7, 'MSFT': 0.3}
        })
        assert r.status_code == 200
        data = r.get_json()
        assert 'statistics' in data


# ============================================================================
# OPTIMIZATION ENDPOINTS
# ============================================================================

class TestOptimizePortfolio:
    def test_missing_body(self, client):
        r = client.post('/api/optimize-portfolio', content_type='application/json')
        assert r.status_code in (400, 500)

    def test_no_symbols(self, client):
        r = client.post('/api/optimize-portfolio', json={'symbols': []})
        assert r.status_code == 400

    def test_optimize_sharpe(self, client):
        r = client.post('/api/optimize-portfolio', json={
            'symbols': ['AAPL', 'MSFT'],
            'type': 'sharpe'
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data['success'] is True
        assert 'weights' in data
        assert 'expected_return' in data
        assert 'volatility' in data
        assert 'sharpe_ratio' in data
        assert 'asset_stats' in data
        assert 'correlation' in data
        total = sum(data['weights'].values())
        assert abs(total - 1.0) < 0.01

    def test_optimize_minvar(self, client):
        r = client.post('/api/optimize-portfolio', json={
            'symbols': ['AAPL', 'MSFT'],
            'type': 'minvar'
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data['success'] is True


class TestEfficientFrontier:
    def test_missing_body(self, client):
        r = client.post('/api/efficient-frontier', content_type='application/json')
        assert r.status_code in (400, 500)

    def test_basic_frontier(self, client):
        r = client.post('/api/efficient-frontier', json={
            'symbols': ['AAPL', 'MSFT'],
            'num_points': 10
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data['success'] is True
        assert 'frontier' in data
        assert len(data['frontier']) <= 10
