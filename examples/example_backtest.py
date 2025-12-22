"""
Example usage of the investment backtester MVP.

This demonstrates backtesting various strategies with multiple asset types.
"""

import sys
sys.path.insert(0, '/path/to/backtester')  # Adjust as needed

from src.data_generator import create_sample_assets
from src.backtester import Backtester, Comparator
from src.strategies import Strategies


def main():
    """Run example backtests and comparisons."""
    
    print("\n" + "=" * 100)
    print("INVESTMENT BACKTESTER MVP - EXAMPLE")
    print("=" * 100 + "\n")
    
    # Create sample assets with multiple types
    print("Creating sample assets (stocks, bonds, crypto, commodities)...")
    assets = create_sample_assets(start_date="2023-01-01", num_days=252)
    
    print(f"Assets created: {', '.join(assets.keys())}\n")
    
    # Create backtester
    backtester = Backtester(assets)
    
    # Run multiple strategies
    results = []
    
    # Strategy 1: Buy and hold TECH
    print("Running: Buy & Hold (TECH only)...")
    result1 = backtester.run(
        strategy_func=Strategies.buy_and_hold("TECH", percent_allocation=1.0),
        initial_capital=100000,
        strategy_name="Buy & Hold TECH"
    )
    results.append(result1)
    
    # Strategy 2: Buy and hold DIVIDEND
    print("Running: Buy & Hold (DIVIDEND stock)...")
    result2 = backtester.run(
        strategy_func=Strategies.buy_and_hold("DIVIDEND", percent_allocation=1.0),
        initial_capital=100000,
        strategy_name="Buy & Hold DIVIDEND"
    )
    results.append(result2)
    
    # Strategy 3: 60/40 Stocks/Bonds
    print("Running: 60/40 Stock/Bond Portfolio...")
    result3 = backtester.run(
        strategy_func=Strategies.balanced_portfolio({
            "TECH": 0.3,
            "DIVIDEND": 0.3,
            "BOND": 0.4
        }),
        initial_capital=100000,
        strategy_name="60/40 Portfolio"
    )
    results.append(result3)
    
    # Strategy 4: Balanced across all assets
    print("Running: Balanced 5-Asset Portfolio...")
    result4 = backtester.run(
        strategy_func=Strategies.balanced_portfolio({
            "TECH": 0.2,
            "DIVIDEND": 0.2,
            "BOND": 0.2,
            "CRYPTO": 0.2,
            "COMMODITY": 0.2
        }),
        initial_capital=100000,
        strategy_name="Balanced 5-Asset"
    )
    results.append(result4)
    
    # Strategy 5: Momentum strategy
    print("Running: Momentum Strategy...")
    result5 = backtester.run(
        strategy_func=Strategies.momentum_strategy(short_window=20, long_window=50),
        initial_capital=100000,
        strategy_name="Momentum (MA 20/50)"
    )
    results.append(result5)
    
    # Strategy 6: Conservative with rebalancing
    print("Running: Conservative with Quarterly Rebalancing...")
    result6 = backtester.run(
        strategy_func=Strategies.stock_bond_allocation(stock_allocation=0.4, rebalance_quarterly=True),
        initial_capital=100000,
        strategy_name="Conservative Rebalanced"
    )
    results.append(result6)
    
    # Strategy 7: Aggressive with rebalancing
    print("Running: Aggressive with Quarterly Rebalancing...")
    result7 = backtester.run(
        strategy_func=Strategies.stock_bond_allocation(stock_allocation=0.9, rebalance_quarterly=True),
        initial_capital=100000,
        strategy_name="Aggressive Rebalanced"
    )
    results.append(result7)
    
    print("\n✓ All backtests completed!\n")
    
    # Compare results
    comparator = Comparator(results)
    print(comparator.summary())
    
    # Detailed analysis
    print("\nDETAILED ANALYSIS BY METRIC:\n")
    
    print("Best Total Return:")
    best_return = comparator.get_best("total_return")
    print(f"  {best_return.strategy_name}: {best_return.total_return*100:.2f}%\n")
    
    print("Best Annual Return:")
    best_annual = comparator.get_best("annual_return")
    print(f"  {best_annual.strategy_name}: {best_annual.annual_return*100:.2f}%\n")
    
    print("Best Risk-Adjusted Return (Sharpe):")
    best_sharpe = comparator.get_best("sharpe")
    print(f"  {best_sharpe.strategy_name}: {best_sharpe.sharpe_ratio:.2f}\n")
    
    print("Lowest Drawdown (Best):")
    best_dd = comparator.get_best("max_drawdown")
    print(f"  {best_dd.strategy_name}: {best_dd.max_drawdown*100:.2f}%\n")
    
    # Show snapshots for first result
    print("\nSAMPLE PORTFOLIO SNAPSHOTS (First Strategy):\n")
    print(f"{'Date':<12} {'Value':<15} {'Return %':<12} {'Positions'}")
    print("-" * 80)
    
    snapshots = result1.snapshots
    for i in range(0, len(snapshots), max(1, len(snapshots) // 5)):
        snap = snapshots[i]
        positions_str = ", ".join(f"{s}:{q:.1f}" for s, (q, p) in snap.positions.items())
        print(f"{snap.date:<12} ${snap.total_value:<14,.0f} {snap.returns*100:<11.2f}% {positions_str}")
    
    print("\n" + "=" * 100 + "\n")


if __name__ == "__main__":
    main()
