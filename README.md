# Investment Backtester MVP

A simple but functional investment backtester supporting multiple asset types and strategy comparison.

## Quick Start

```bash
# Option 1: Standalone (easiest - no setup needed)
python backtester_standalone.py

# Option 2: Modular structure
python examples/example_backtest.py

# Option 3: Windows batch file
run_backtester.bat
```

## Features

- ✅ **Multiple Asset Types**: Stocks, Bonds, Crypto, Commodities
- ✅ **7+ Trading Strategies**: Buy & Hold, Balanced, Momentum, Rebalancing, etc.
- ✅ **Performance Metrics**: Returns, Annual Return, Max Drawdown, Sharpe Ratio
- ✅ **Strategy Comparison**: Compare multiple strategies side-by-side
- ✅ **Portfolio Tracking**: Monitor positions, value, and performance over time
- ✅ **Zero Dependencies**: Uses only Python standard library
- ✅ **Extensible**: Easy to add custom strategies and assets

## Project Structure

```
backtester/
├── backtester_standalone.py    # ⭐ Self-contained (easiest to use)
├── run_backtester.bat          # Windows batch runner
├── requirements.txt            # Python dependencies (none needed!)
├── GUIDE.md                    # Comprehensive user guide
├── QUICK_REFERENCE.py          # Copy-paste examples
│
├── src/                        # Modular structure (optional)
│   ├── __init__.py
│   ├── assets.py              # Asset class definitions
│   ├── backtester.py          # Core backtesting engine
│   ├── data_generator.py      # Price data generation
│   └── strategies.py          # Trading strategy implementations
│
├── examples/
│   └── example_backtest.py    # Full example with 7 strategies
│
└── data/                      # (For user's custom data)
```

## Usage

### Basic Buy & Hold

```python
from src.data_generator import create_sample_assets
from src.backtester import Backtester
from src.strategies import Strategies

# Create assets
assets = create_sample_assets()

# Create backtester
backtester = Backtester(assets)

# Run strategy
result = backtester.run(
    strategy_func=Strategies.buy_and_hold("TECH"),
    initial_capital=100000,
    strategy_name="My Strategy"
)

print(f"Total Return: {result.total_return*100:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
```

### Balanced Portfolio

```python
result = backtester.run(
    strategy_func=Strategies.balanced_portfolio({
        "TECH": 0.3,
        "DIVIDEND": 0.3,
        "BOND": 0.4
    }),
    initial_capital=100000,
    strategy_name="60/40 Portfolio"
)
```

### Compare Strategies

```python
from src.backtester import Comparator

results = [result1, result2, result3]
comparator = Comparator(results)

print(comparator.summary())
best = comparator.get_best("total_return")
```

## Available Strategies

1. **buy_and_hold(symbol, percent_allocation)** - Single asset buy & hold
2. **balanced_portfolio(allocations)** - Static allocation to multiple assets
3. **momentum_strategy(short_window, long_window)** - Moving average crossover
4. **rebalance_strategy(allocations, frequency)** - Periodic rebalancing
5. **stock_bond_allocation(stock_allocation, rebalance)** - Traditional allocation

## Asset Types

- **STOCK**: Tech and dividend stocks with different volatility profiles
- **BOND**: Conservative fixed-income investment
- **CRYPTO**: Highly volatile alternative asset
- **COMMODITY**: Commodity price movements

## Performance Metrics

- **Total Return**: Overall profit/loss percentage
- **Annual Return**: Annualized return (for strategies > 1 year)
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return (annualized)

## Running Examples

```bash
cd backtester
python examples/example_backtest.py
```

## What's Included

### Asset Types
- **STOCK (TECH)**: High volatility growth stock
- **STOCK (DIVIDEND)**: Lower volatility dividend stock  
- **BOND**: Conservative fixed-income
- **CRYPTO**: High volatility cryptocurrency
- **COMMODITY**: Commodity price movements

### Pre-Built Strategies
1. **buy_and_hold(symbol)** - Single asset buy & hold
2. **balanced_portfolio(allocations)** - Static multi-asset allocation
3. **momentum_strategy(short_window, long_window)** - Moving average crossover
4. **rebalance_strategy(allocations, frequency)** - Periodic rebalancing
5. **stock_bond_allocation(stock_pct, rebalance)** - Traditional 60/40 style
6. Plus custom strategy support!

### Performance Metrics
- **Total Return**: Overall profit percentage
- **Annual Return**: Annualized compound return
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return metric

## Documentation

- **README.md** - Overview (this file)
- **GUIDE.md** - Comprehensive user guide with examples
- **QUICK_REFERENCE.py** - Copy-paste code snippets
- **Code Comments** - Detailed inline documentation

## Limitations

- No transaction costs/slippage
- No dividend reinvestment
- Simple daily execution
- No margin/leverage
- No options/derivatives

## Extension Ideas

- Add real market data (Yahoo Finance, Alpha Vantage)
- Transaction costs and commissions
- More complex indicators (RSI, MACD, Bollinger Bands)
- Parameter optimization (grid search)
- Walk-forward backtesting
- Monte Carlo simulations
- Web UI dashboard
- Export to CSV/Excel
