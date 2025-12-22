"""
Example: Using Real Data from Yahoo Finance

This example shows how to:
1. Fetch real data from Yahoo Finance
2. Run backtests with real market data
3. Compare different stocks
"""

from real_data import load_real_data, YahooFinanceDataProvider
from backtester_standalone import Backtester, Comparator, Strategies
from src.assets import AssetType


def example_1_simple_stock():
    """Example 1: Backtest a single stock with real data."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Single Stock Backtest (Real Data)")
    print("="*80 + "\n")
    
    # Load AAPL data for the last year
    symbols = {'AAPL': AssetType.STOCK}
    assets = load_real_data(symbols, num_days=252)
    
    if not assets:
        print("Failed to load data")
        return
    
    # Create backtester
    backtester = Backtester(assets)
    
    # Run buy & hold strategy
    result = backtester.run(
        strategy_func=Strategies.buy_and_hold('AAPL'),
        initial_capital=100000,
        strategy_name="AAPL Buy & Hold"
    )
    
    # Print results
    print(f"\nStrategy: {result.strategy_name}")
    print(f"Period: {result.start_date} to {result.end_date}")
    print(f"Initial Capital: ${result.initial_capital:,.2f}")
    print(f"Final Value: ${result.final_value:,.2f}")
    print(f"Total Return: {result.total_return*100:.2f}%")
    print(f"Annual Return: {result.annual_return*100:.2f}%")
    print(f"Max Drawdown: {result.max_drawdown*100:.2f}%")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}\n")


def example_2_compare_stocks():
    """Example 2: Compare different stocks."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Compare Multiple Stocks")
    print("="*80 + "\n")
    
    # Load multiple stocks
    symbols = {
        'AAPL': AssetType.STOCK,
        'MSFT': AssetType.STOCK,
        'GOOGL': AssetType.STOCK
    }
    assets = load_real_data(symbols, num_days=252)
    
    if len(assets) < 2:
        print("Failed to load enough data")
        return
    
    backtester = Backtester(assets)
    results = []
    
    # Test each stock
    for symbol in assets.keys():
        result = backtester.run(
            strategy_func=Strategies.buy_and_hold(symbol),
            initial_capital=100000,
            strategy_name=f"{symbol} Buy & Hold"
        )
        results.append(result)
    
    # Compare
    comparator = Comparator(results)
    print(comparator.summary())


def example_3_stocks_and_bonds():
    """Example 3: Mix stocks and bonds."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Stocks & Bonds Portfolio")
    print("="*80 + "\n")
    
    # Load stocks and bonds
    symbols = {
        'AAPL': AssetType.STOCK,
        'MSFT': AssetType.STOCK,
        'BND': AssetType.BOND,  # Total Bond Market ETF
    }
    assets = load_real_data(symbols, num_days=252)
    
    if not assets:
        print("Failed to load data")
        return
    
    backtester = Backtester(assets)
    results = []
    
    # Test different allocations
    allocations = [
        ('100% Stocks', {'AAPL': 0.5, 'MSFT': 0.5}),
        ('80/20', {'AAPL': 0.4, 'MSFT': 0.4, 'BND': 0.2}),
        ('60/40', {'AAPL': 0.3, 'MSFT': 0.3, 'BND': 0.4}),
        ('40/60', {'AAPL': 0.2, 'MSFT': 0.2, 'BND': 0.6}),
    ]
    
    for name, allocation in allocations:
        result = backtester.run(
            strategy_func=Strategies.balanced_portfolio(allocation),
            initial_capital=100000,
            strategy_name=name
        )
        results.append(result)
    
    # Compare
    comparator = Comparator(results)
    print(comparator.summary())
    
    # Analysis
    print("\nAnalysis:")
    best_return = comparator.get_best('total_return')
    best_sharpe = comparator.get_best('sharpe')
    best_dd = comparator.get_best('max_drawdown')
    
    print(f"  Best Return: {best_return.strategy_name}")
    print(f"  Best Risk-Adjusted: {best_sharpe.strategy_name}")
    print(f"  Most Stable: {best_dd.strategy_name}\n")


def example_4_momentum_real_data():
    """Example 4: Test momentum strategy with real data."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Momentum Strategy with Real Data")
    print("="*80 + "\n")
    
    # Load tech stocks
    symbols = {
        'AAPL': AssetType.STOCK,
        'MSFT': AssetType.STOCK,
        'GOOGL': AssetType.STOCK,
        'NVDA': AssetType.STOCK,
    }
    assets = load_real_data(symbols, num_days=252)
    
    if not assets:
        print("Failed to load data")
        return
    
    backtester = Backtester(assets)
    results = []
    
    # Test different momentum parameters
    params = [
        ('Short 10/50', 10, 50),
        ('Short 20/50', 20, 50),
        ('Short 20/100', 20, 100),
    ]
    
    for name, short, long in params:
        result = backtester.run(
            strategy_func=Strategies.momentum_strategy(short, long),
            initial_capital=100000,
            strategy_name=f"Momentum {name}"
        )
        results.append(result)
    
    # Compare
    comparator = Comparator(results)
    print(comparator.summary())


def example_5_rebalancing_real_data():
    """Example 5: Test rebalancing with real data."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Rebalancing Strategy with Real Data")
    print("="*80 + "\n")
    
    # Load assets
    symbols = {
        'AAPL': AssetType.STOCK,
        'MSFT': AssetType.STOCK,
        'BND': AssetType.BOND,
    }
    assets = load_real_data(symbols, num_days=504)  # 2 years
    
    if not assets:
        print("Failed to load data")
        return
    
    backtester = Backtester(assets)
    results = []
    
    # Test different rebalancing frequencies
    allocation = {'AAPL': 0.3, 'MSFT': 0.3, 'BND': 0.4}
    
    for freq_days in [21, 63, 126]:  # Monthly, Quarterly, Semi-annual
        result = backtester.run(
            strategy_func=Strategies.rebalance_strategy(allocation, freq_days),
            initial_capital=100000,
            strategy_name=f"Rebalance ({freq_days} days)"
        )
        results.append(result)
    
    # Compare
    comparator = Comparator(results)
    print(comparator.summary())


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("INVESTMENT BACKTESTER - REAL DATA EXAMPLES")
    print("="*80)
    print("\nFetching real data from Yahoo Finance...")
    print("(This may take a moment on first run)\n")
    
    try:
        # Run examples
        example_1_simple_stock()
        example_2_compare_stocks()
        example_3_stocks_and_bonds()
        example_4_momentum_real_data()
        example_5_rebalancing_real_data()
        
        print("\n" + "="*80)
        print("✓ All examples completed successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Verify symbols exist on Yahoo Finance")
        print("3. Try again - sometimes the API is slow")
        print("4. Use sample data instead: create_sample_assets()\n")


if __name__ == '__main__':
    main()
