"""Flask web application for the Investment Backtester."""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import traceback

from backtester_standalone import (
    Backtester, Comparator, Strategies, Portfolio,
    create_sample_assets
)
from real_data import load_real_data, YahooFinanceDataProvider
from portfolio_optimizer import PortfolioOptimizer, calculate_returns_from_prices
from monte_carlo import PortfolioMonteCarloSimulator, calculate_rolling_metrics
from src.assets import AssetType


app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_asset_type_options():
    """Get available asset types."""
    return [
        {'value': 'STOCK', 'label': 'Stock'},
        {'value': 'BOND', 'label': 'Bond'},
        {'value': 'CRYPTO', 'label': 'Cryptocurrency'},
        {'value': 'COMMODITY', 'label': 'Commodity'},
    ]


def get_strategy_options():
    """Get available strategies."""
    return [
        {
            'id': 'buy_hold_single',
            'name': 'Buy & Hold (Single Asset)',
            'params': [
                {'name': 'symbol', 'type': 'text', 'label': 'Symbol', 'value': ''}
            ]
        },
        {
            'id': 'balanced',
            'name': 'Balanced Portfolio',
            'params': [
                {'name': 'allocation_json', 'type': 'text', 'label': 'JSON Allocation', 'value': '{"VTI": 0.5, "BND": 0.5}'}
            ]
        },
        {
            'id': 'momentum',
            'name': 'Momentum Strategy',
            'params': [
                {'name': 'short_window', 'type': 'number', 'label': 'Short MA Window', 'value': '20'},
                {'name': 'long_window', 'type': 'number', 'label': 'Long MA Window', 'value': '50'}
            ]
        },
        {
            'id': 'rebalance',
            'name': 'Rebalancing Strategy',
            'params': [
                {'name': 'allocation_json', 'type': 'text', 'label': 'JSON Allocation', 'value': '{"VTI": 0.5, "BND": 0.5}'},
                {'name': 'frequency', 'type': 'number', 'label': 'Rebalance Days', 'value': '63'}
            ]
        },
        {
            'id': 'rsi_oversold',
            'name': 'RSI Oversold Strategy',
            'params': [
                {'name': 'symbol', 'type': 'text', 'label': 'Symbol', 'value': ''},
                {'name': 'rsi_period', 'type': 'number', 'label': 'RSI Period', 'value': '14'},
                {'name': 'oversold_level', 'type': 'number', 'label': 'Oversold Level', 'value': '30'},
                {'name': 'allocation', 'type': 'number', 'label': 'Allocation %', 'value': '1.0'}
            ]
        },
        {
            'id': 'macd',
            'name': 'MACD Crossover Strategy',
            'params': [
                {'name': 'symbol', 'type': 'text', 'label': 'Symbol', 'value': ''},
                {'name': 'fast', 'type': 'number', 'label': 'Fast EMA', 'value': '12'},
                {'name': 'slow', 'type': 'number', 'label': 'Slow EMA', 'value': '26'},
                {'name': 'signal', 'type': 'number', 'label': 'Signal Line', 'value': '9'},
                {'name': 'allocation', 'type': 'number', 'label': 'Allocation %', 'value': '1.0'}
            ]
        },
        {
            'id': 'bollinger',
            'name': 'Bollinger Bands Strategy',
            'params': [
                {'name': 'symbol', 'type': 'text', 'label': 'Symbol', 'value': ''},
                {'name': 'period', 'type': 'number', 'label': 'Period', 'value': '20'},
                {'name': 'num_std', 'type': 'number', 'label': 'Standard Deviations', 'value': '2.0'},
                {'name': 'allocation', 'type': 'number', 'label': 'Allocation %', 'value': '1.0'}
            ]
        },
    ]


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/api/asset-types')
def api_asset_types():
    """Get available asset types."""
    return jsonify(get_asset_type_options())


@app.route('/api/strategies')
def api_strategies():
    """Get available strategies."""
    return jsonify(get_strategy_options())


@app.route('/api/symbols-autocomplete')
def api_symbols_autocomplete():
    """Get autocomplete suggestions for stock symbols."""
    query = request.args.get('q', '').upper()
    
    # Common stock symbols to suggest
    all_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK.B',
        'JNJ', 'V', 'JPM', 'WMT', 'PG', 'MA', 'HD', 'DIS', 'MCD', 'NFLX', 'INTC',
        'BA', 'CSCO', 'PEP', 'KO', 'MO', 'ABT', 'ABBV', 'MMC', 'RSG', 'ADBE',
        'CME', 'CRM', 'SBUX', 'HON', 'PYPL', 'COST', 'AMGN', 'BKNG', 'LLY',
        'AXP', 'QCOM', 'ISRG', 'AMAT', 'LOW', 'ASML', 'VRTX', 'AMD', 'NOW',
        'BND', 'VTI', 'VOO', 'AGG', 'SPLG', 'VTSAX', 'VBTLX', 'SCHB', 'SCHF',
        'SPY', 'QQQ', 'IWM', 'EEM', 'GLD', 'USO', 'TLT', 'VXUS'
    ]
    
    # Filter symbols based on query
    if query:
        suggestions = [s for s in all_symbols if s.startswith(query)]
    else:
        suggestions = all_symbols[:20]  # Return first 20 if no query
    
    return jsonify({'suggestions': suggestions[:15]})  # Limit to 15 results


@app.route('/api/validate-symbols', methods=['POST'])
def api_validate_symbols():
    """Validate if symbols are valid (exist in Yahoo Finance)."""
    try:
        data = request.json
        symbols = [s.strip().upper() for s in data.get('symbols', '')]
        symbols = [s for s in symbols if s]  # Remove empty strings
        
        if not symbols:
            return jsonify({'valid': False, 'error': 'No symbols provided'})
        
        # Try to load data for the symbols
        try:
            from datetime import timedelta
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            loaded_symbols = []
            missing_symbols = []
            
            for symbol in symbols:
                asset = YahooFinanceDataProvider.fetch_stock_data(
                    symbol, 
                    start_date, 
                    end_date,
                    max_retries=1,
                    verbose=False
                )
                if asset:
                    loaded_symbols.append(symbol)
                else:
                    missing_symbols.append(symbol)
            
            if not loaded_symbols:
                return jsonify({'valid': False, 'error': 'No valid symbols found'})
            
            return jsonify({
                'valid': True,
                'loaded_symbols': loaded_symbols,
                'missing_symbols': missing_symbols,
                'error': f'Could not load data for: {", ".join(missing_symbols)}' if missing_symbols else None
            })
        except Exception as e:
            return jsonify({'valid': False, 'error': f'Data validation failed: {str(e)}'})
    except Exception as e:
        return jsonify({'valid': False, 'error': f'Validation error: {str(e)}'})




@app.route('/api/load-real-data', methods=['POST'])
def api_load_real_data():
    """Load real data from Yahoo Finance."""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        num_days = data.get('num_days', 252)
        
        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols provided'}), 400
        
        print(f"\n{'='*60}")
        print(f"Loading real data for: {', '.join(symbols)}")
        print(f"{'='*60}")
        
        # Convert to asset type dict
        symbol_dict = {s: AssetType.STOCK for s in symbols}
        
        # Load data with retry logic
        assets = load_real_data(symbol_dict, num_days)
        
        if not assets:
            print("\n⚠ Failed to load real data, falling back to sample data...")
            # Fallback to sample data
            assets = create_sample_assets()
            return jsonify({
                'success': True,
                'assets': list(assets.keys()),
                'message': f'Yahoo Finance unavailable. Using sample data ({len(assets)} assets)',
                'warning': 'Using sample data instead of real data'
            })
        
        print(f"\n✓ Successfully loaded real data for {len(assets)} symbols")
        return jsonify({
            'success': True,
            'assets': list(assets.keys()),
            'message': f'Loaded real data for {len(assets)} assets from Yahoo Finance'
        })
        
    except Exception as e:
        traceback.print_exc()
        print(f"\n✗ Error: {str(e)}")
        print("Falling back to sample data...")
        try:
            # Fallback to sample data
            assets = create_sample_assets()
            return jsonify({
                'success': True,
                'assets': list(assets.keys()),
                'message': f'Error loading real data. Using sample data ({len(assets)} assets)',
                'warning': f'Error: {str(e)}'
            })
        except:
            return jsonify({'success': False, 'error': f'Failed to load data: {str(e)}'}), 500


@app.route('/api/backtest', methods=['POST'])
def api_backtest():
    """Run a backtest."""
    try:
        data = request.json
        use_real_data = data.get('use_real_data', False)
        symbols = data.get('symbols', [])
        strategy_id = data.get('strategy_id')
        strategy_params = data.get('strategy_params', {})
        initial_capital = float(data.get('initial_capital', 100000))
        num_days = int(data.get('num_days', 252))
        
        # Load assets
        if use_real_data and symbols:
            symbol_dict = {s: AssetType.STOCK for s in symbols}
            assets = load_real_data(symbol_dict, num_days)
            if not assets:
                return jsonify({'success': False, 'error': 'Failed to load real data'}), 500
        else:
            assets = create_sample_assets(num_days=num_days)
        
        # Create backtester
        backtester = Backtester(assets)
        
        # Get strategy function
        strategy_func = _get_strategy_func(strategy_id, strategy_params, assets)
        if not strategy_func:
            return jsonify({'success': False, 'error': 'Invalid strategy'}), 400
        
        # Run backtest
        result = backtester.run(
            strategy_func=strategy_func,
            initial_capital=initial_capital,
            strategy_name=f"Strategy: {strategy_id}"
        )
        
        # Format results
        return jsonify({
            'success': True,
            'result': {
                'strategy_name': result.strategy_name,
                'initial_capital': result.initial_capital,
                'final_value': round(result.final_value, 2),
                'total_return': round(result.total_return * 100, 2),
                'annual_return': round(result.annual_return * 100, 2),
                'max_drawdown': round(result.max_drawdown * 100, 2),
                'sharpe_ratio': round(result.sharpe_ratio, 2),
                'start_date': result.start_date,
                'end_date': result.end_date,
                'snapshots': [
                    {
                        'date': snap.date,
                        'value': round(snap.total_value, 2),
                        'returns': round(snap.returns * 100, 2)
                    }
                    for snap in result.snapshots[::max(1, len(result.snapshots)//50)]  # Sample every Nth day
                ]
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def api_compare():
    """Compare multiple strategies."""
    try:
        data = request.json
        use_real_data = data.get('use_real_data', False)
        symbols = data.get('symbols', [])
        strategies = data.get('strategies', [])
        initial_capital = float(data.get('initial_capital', 100000))
        num_days = int(data.get('num_days', 252))
        
        print(f"[COMPARE] Received {len(strategies)} strategies")
        print(f"[COMPARE] Symbols: {symbols}")
        
        if not strategies:
            return jsonify({'success': False, 'error': 'No strategies provided'}), 400
        
        # Load assets
        if use_real_data and symbols:
            symbol_dict = {s: AssetType.STOCK for s in symbols}
            assets = load_real_data(symbol_dict, num_days)
            if not assets:
                return jsonify({'success': False, 'error': 'Failed to load real data'}), 500
            print(f"[COMPARE] Loaded {len(assets)} assets from Yahoo Finance")
        else:
            assets = create_sample_assets(num_days=num_days)
            print(f"[COMPARE] Created {len(assets)} sample assets")
        
        backtester = Backtester(assets)
        results = []
        comparison_rows = []
        
        # Run each strategy
        for i, strategy_def in enumerate(strategies):
            strategy_id = strategy_def.get('strategy_id')
            strategy_params = strategy_def.get('params', {})
            strategy_name = strategy_def.get('name', strategy_id)
            
            print(f"[COMPARE] Strategy {i+1}: {strategy_name} (id={strategy_id})")
            
            strategy_func = _get_strategy_func(strategy_id, strategy_params, assets)
            if not strategy_func:
                print(f"[COMPARE] WARNING: Could not create strategy function for {strategy_id}")
                continue
            
            print(f"[COMPARE] Running strategy: {strategy_name}")
            result = backtester.run(
                strategy_func=strategy_func,
                initial_capital=initial_capital,
                strategy_name=strategy_name
            )
            results.append(result)
            
            # Build comparison row with snapshots for chart
            # Sample snapshots for chart display (max 50 data points)
            sampled_snapshots = result.snapshots[::max(1, len(result.snapshots)//50)]
            
            print(f"[COMPARE] Snapshots: {len(result.snapshots)} total, {len(sampled_snapshots)} sampled")
            
            comparison_rows.append({
                'name': result.strategy_name,
                'initial': round(result.initial_capital, 2),
                'final': round(result.final_value, 2),
                'return': round(result.total_return * 100, 2),
                'annual': round(result.annual_return * 100, 2),
                'max_dd': round(result.max_drawdown * 100, 2),
                'sharpe': round(result.sharpe_ratio, 2),
                'snapshots': [
                    {
                        'date': snap.date,
                        'value': round(snap.total_value, 2),
                        'returns': round(snap.returns * 100, 2)
                    }
                    for snap in sampled_snapshots
                ]
            })
        
        if not results:
            print("[COMPARE] ERROR: No results generated")
            return jsonify({'success': False, 'error': 'No successful backtests'}), 500
        
        print(f"[COMPARE] SUCCESS: Generated {len(comparison_rows)} comparison results")
        
        return jsonify({
            'success': True,
            'results': comparison_rows,
            'best_return': max(results, key=lambda r: r.total_return).strategy_name,
            'best_sharpe': max(results, key=lambda r: r.sharpe_ratio).strategy_name,
            'best_dd': min(results, key=lambda r: r.max_drawdown).strategy_name
        })
        
    except Exception as e:
        print(f"[COMPARE] EXCEPTION: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/default-symbols')
def api_default_symbols():
    """Get default symbols."""
    return jsonify({
        'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
        'descriptions': {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet (Google)',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'BND': 'Bond ETF',
        }
    })


# ============================================================================
# STRATEGY BUILDERS
# ============================================================================

def _get_strategy_func(strategy_id, params, assets):
    """Build strategy function from ID and parameters."""
    try:
        if strategy_id == 'buy_hold_single':
            symbol = params.get('symbol', 'AAPL')
            return Strategies.buy_and_hold(symbol)
        
        elif strategy_id == 'balanced':
            allocation_json = params.get('allocation_json', '{}')
            allocation = json.loads(allocation_json)
            return Strategies.balanced_portfolio(allocation)
        
        elif strategy_id == 'momentum':
            short_window = int(params.get('short_window', 20))
            long_window = int(params.get('long_window', 50))
            return Strategies.momentum_strategy(short_window, long_window)
        
        elif strategy_id == 'rebalance':
            allocation_json = params.get('allocation_json', '{}')
            allocation = json.loads(allocation_json)
            frequency = int(params.get('frequency', 63))
            return Strategies.rebalance_strategy(allocation, frequency)
        
        elif strategy_id == 'rsi_oversold':
            symbol = params.get('symbol', '')
            if not symbol:
                print("RSI strategy: No symbol provided")
                return None
            rsi_period = int(params.get('rsi_period', 14))
            oversold_level = int(params.get('oversold_level', 30))
            allocation = float(params.get('allocation', 1.0))
            return Strategies.rsi_oversold_strategy(symbol, rsi_period, oversold_level, allocation)
        
        elif strategy_id == 'macd':
            symbol = params.get('symbol', '')
            if not symbol:
                print("MACD strategy: No symbol provided")
                return None
            fast = int(params.get('fast', 12))
            slow = int(params.get('slow', 26))
            signal = int(params.get('signal', 9))
            allocation = float(params.get('allocation', 1.0))
            return Strategies.macd_strategy(symbol, fast, slow, signal, allocation)
        
        elif strategy_id == 'bollinger':
            symbol = params.get('symbol', '')
            if not symbol:
                print("Bollinger Bands strategy: No symbol provided")
                return None
            period = int(params.get('period', 20))
            num_std = float(params.get('num_std', 2.0))
            allocation = float(params.get('allocation', 1.0))
            return Strategies.bollinger_bands_strategy(symbol, period, num_std, allocation)
        
        print(f"Unknown strategy: {strategy_id}")
        return None
    except Exception as e:
        print(f"Error building strategy {strategy_id}: {e}")
        traceback.print_exc()
        return None


# ============================================================================
# PORTFOLIO OPTIMIZATION ENDPOINTS
# ============================================================================

@app.route('/api/optimize-portfolio', methods=['POST'])
def api_optimize_portfolio():
    """Optimize portfolio using Modern Portfolio Theory."""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        optimization_type = data.get('type', 'sharpe')  # 'sharpe' or 'minvar'
        
        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols provided'}), 400
        
        print(f"\n{'='*60}")
        print(f"Optimizing portfolio for: {', '.join(symbols)}")
        print(f"Optimization type: {optimization_type}")
        print(f"{'='*60}")
        
        # Load real data
        symbol_dict = {s: AssetType.STOCK for s in symbols}
        assets = load_real_data(symbol_dict, num_days=252)
        
        if len(assets) < len(symbols):
            return jsonify({
                'success': False,
                'error': f'Could not load data for all symbols. Got {len(assets)}/{len(symbols)}'
            }), 500
        
        # Extract price data
        assets_prices = {}
        for symbol in symbols:
            if symbol in assets:
                assets_prices[symbol] = assets[symbol].price_data.prices
        
        # Create optimizer
        returns_dict = {}
        for symbol, prices in assets_prices.items():
            returns_dict[symbol] = calculate_returns_from_prices(prices)
        
        optimizer = PortfolioOptimizer(returns_dict)
        
        # Optimize
        if optimization_type == 'minvar':
            result = optimizer.optimize_min_variance()
        else:
            result = optimizer.optimize_max_sharpe()
        
        # Get asset statistics and correlations
        asset_stats = optimizer.get_asset_statistics()
        correlation = optimizer.get_correlation_matrix()
        
        print(f"\n✓ Optimization complete!")
        print(f"Expected return: {result.expected_return*100:.2f}%")
        print(f"Volatility: {result.volatility*100:.2f}%")
        print(f"Sharpe ratio: {result.sharpe_ratio:.2f}")
        
        return jsonify({
            'success': True,
            'weights': result.weights,
            'expected_return': result.expected_return,
            'volatility': result.volatility,
            'sharpe_ratio': result.sharpe_ratio,
            'asset_stats': asset_stats,
            'correlation': correlation,
            'message': f'Optimal portfolio found with Sharpe ratio {result.sharpe_ratio:.2f}'
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/efficient-frontier', methods=['POST'])
def api_efficient_frontier():
    """Calculate efficient frontier for given assets."""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        num_points = data.get('num_points', 50)
        
        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols provided'}), 400
        
        print(f"\n{'='*60}")
        print(f"Calculating efficient frontier for: {', '.join(symbols)}")
        print(f"Number of points: {num_points}")
        print(f"{'='*60}")
        
        # Load real data
        symbol_dict = {s: AssetType.STOCK for s in symbols}
        assets = load_real_data(symbol_dict, num_days=252)
        
        if len(assets) < len(symbols):
            return jsonify({
                'success': False,
                'error': f'Could not load data for all symbols'
            }), 500
        
        # Extract price data
        assets_prices = {}
        for symbol in symbols:
            if symbol in assets:
                assets_prices[symbol] = assets[symbol].price_data.prices
        
        # Create optimizer
        returns_dict = {}
        for symbol, prices in assets_prices.items():
            returns_dict[symbol] = calculate_returns_from_prices(prices)
        
        optimizer = PortfolioOptimizer(returns_dict)
        
        # Calculate frontier
        frontier = optimizer.efficient_frontier(num_points=num_points)
        
        # Format for JSON
        frontier_data = []
        for vol, ret, weights in frontier:
            frontier_data.append({
                'volatility': vol,
                'return': ret,
                'weights': weights
            })
        
        # Get optimal portfolios
        max_sharpe = optimizer.optimize_max_sharpe()
        min_var = optimizer.optimize_min_variance()
        
        print(f"\n✓ Efficient frontier calculated!")
        print(f"Points on frontier: {len(frontier_data)}")
        
        return jsonify({
            'success': True,
            'frontier': frontier_data,
            'max_sharpe': {
                'volatility': max_sharpe.volatility,
                'return': max_sharpe.expected_return,
                'weights': max_sharpe.weights,
                'sharpe_ratio': max_sharpe.sharpe_ratio
            },
            'min_variance': {
                'volatility': min_var.volatility,
                'return': min_var.expected_return,
                'weights': min_var.weights,
                'sharpe_ratio': min_var.sharpe_ratio
            },
            'message': f'Efficient frontier with {len(frontier_data)} points calculated'
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/monte-carlo', methods=['POST'])
def api_monte_carlo():
    """Run Monte Carlo simulation on portfolio."""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        num_simulations = int(data.get('num_simulations', 1000))
        num_days = int(data.get('num_days', 252))
        initial_value = float(data.get('initial_value', 100000))
        
        if not symbols:
            return jsonify({'success': False, 'error': 'No symbols provided'}), 400
        
        # Load real data
        symbol_dict = {s: AssetType.STOCK for s in symbols}
        assets = load_real_data(symbol_dict, num_days=num_days+50)
        
        if len(assets) < len(symbols):
            return jsonify({
                'success': False,
                'error': f'Could not load data for all symbols. Got {len(assets)}/{len(symbols)}'
            }), 500
        
        # Extract price data and calculate returns
        returns_dict = {}
        for symbol in symbols:
            if symbol in assets:
                prices = assets[symbol].price_data.prices
                returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                returns_dict[symbol] = returns
        
        # Equal weight allocation
        weights = {symbol: 1.0 / len(symbols) for symbol in symbols}
        
        # Run simulation
        simulator = PortfolioMonteCarloSimulator(returns_dict, weights)
        results = simulator.simulate(num_simulations=num_simulations, 
                                    days=num_days, 
                                    initial_value=initial_value)
        
        print(f"\n✓ Monte Carlo simulation completed: {num_simulations} runs")
        
        return jsonify(results)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rolling-metrics', methods=['POST'])
def api_rolling_metrics():
    """Calculate rolling Sharpe, returns, and volatility."""
    try:
        data = request.json
        snapshots = data.get('snapshots', [])
        window = int(data.get('window', 20))
        
        if not snapshots:
            return jsonify({'success': False, 'error': 'No snapshots provided'}), 400
        
        results = calculate_rolling_metrics(snapshots, window=window)
        
        return jsonify({
            'success': True,
            'rolling_sharpe': results['rolling_sharpe'],
            'rolling_returns': results['rolling_returns'],
            'rolling_volatility': results['rolling_volatility'],
            'rolling_dates': results['rolling_dates'],
            'window': results['window'],
            'message': f'Calculated rolling metrics with {window}-day window'
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*80)
    print("INVESTMENT BACKTESTER WEB APPLICATION")
    print("="*80)
    print("\nStarting Flask server on http://localhost:5000")
    print("\nFeatures:")
    print("  [OK] Web interface for backtesting")
    print("  [OK] Real data from Yahoo Finance")
    print("  [OK] Multiple strategy comparison")
    print("  [OK] Custom parameters")
    print("\nTip: Use Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    app.run(debug=False, port=5000, use_reloader=False)
