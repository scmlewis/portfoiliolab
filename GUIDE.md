# Investment Backtester MVP - User Guide

## Quick Start

### Option 1: Standalone Script (Easiest)
```bash
python backtester_standalone.py
```

This is a single self-contained Python file with all code needed. No dependencies!

### Option 2: Modular Structure
```bash
python examples/example_backtest.py
```

This uses the organized module structure in the `src/` directory.

---

## Features

✅ **Multiple Asset Types**: Stocks, Bonds, Crypto, Commodities
✅ **7+ Trading Strategies**: Buy & Hold, Balanced, Momentum, Rebalancing, etc.
✅ **Performance Metrics**: Returns, Drawdown, Sharpe Ratio
✅ **Strategy Comparison**: Compare multiple strategies side-by-side
✅ **No External Dependencies**: Uses only Python stdlib
✅ **Extensible**: Easy to add new assets and strategies

---

## Core Concepts

### 1. Assets
Each asset has a symbol, type, and price history:
```python
TECH = Asset(
    symbol="TECH",
    asset_type=AssetType.STOCK,
    price_data=PriceData(dates=[...], prices=[...])
)
```

Available asset types:
- `STOCK`: Equity investments (tech, dividend)
- `BOND`: Fixed income securities
- `CRYPTO`: Cryptocurrencies
- `COMMODITY`: Commodity prices

### 2. Portfolio
A collection of positions with cash:
```python
portfolio = Portfolio(initial_capital=100000)
portfolio.buy(asset, quantity=100, price=50.0, date_index=0)
portfolio.sell("SYMBOL", quantity=50, price=55.0)
```

### 3. Strategies
Functions that make trading decisions:
```python
def my_strategy(backtester, portfolio, date_index):
    # Make trading decisions here
    pass
```

### 4. Backtester
Runs a strategy over historical data:
```python
backtester = Backtester(assets)
result = backtester.run(
    strategy_func=my_strategy,
    initial_capital=100000,
    strategy_name="My Strategy"
)
```

### 5. Results & Comparison
Get metrics and compare strategies:
```python
comparator = Comparator([result1, result2, result3])
print(comparator.summary())
best = comparator.get_best("sharpe")
```

---

## Available Strategies

### 1. Buy & Hold
Hold a single asset for the entire period.
```python
Strategies.buy_and_hold("TECH")
```

### 2. Balanced Portfolio
Static allocation across multiple assets.
```python
Strategies.balanced_portfolio({
    "TECH": 0.3,
    "DIVIDEND": 0.3,
    "BOND": 0.4
})
```

### 3. Momentum Strategy
Buy assets with upward momentum (short MA > long MA).
```python
Strategies.momentum_strategy(short_window=20, long_window=50)
```

### 4. Rebalancing Strategy
Periodically rebalance to target allocations.
```python
Strategies.rebalance_strategy({
    "TECH": 0.4,
    "BOND": 0.6
}, rebalance_frequency=63)  # Quarterly
```

---

## Example: Basic Backtest

```python
from backtester_standalone import *

# Create sample data
assets = create_sample_assets()

# Create backtester
backtester = Backtester(assets)

# Run a strategy
result = backtester.run(
    strategy_func=Strategies.buy_and_hold("TECH"),
    initial_capital=100000,
    strategy_name="Tech Only"
)

# Print results
print(f"Final Value: ${result.final_value:,.0f}")
print(f"Total Return: {result.total_return*100:.2f}%")
print(f"Annual Return: {result.annual_return*100:.2f}%")
print(f"Max Drawdown: {result.max_drawdown*100:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
```

---

## Example: Strategy Comparison

```python
# Create multiple strategies
result1 = backtester.run(
    Strategies.buy_and_hold("TECH"),
    100000,
    "TECH Only"
)

result2 = backtester.run(
    Strategies.balanced_portfolio({"TECH": 0.5, "BOND": 0.5}),
    100000,
    "50/50 Mix"
)

result3 = backtester.run(
    Strategies.momentum_strategy(),
    100000,
    "Momentum"
)

# Compare
comparator = Comparator([result1, result2, result3])
print(comparator.summary())

# Find best by different metrics
print(f"Best Total Return: {comparator.get_best('total_return').strategy_name}")
print(f"Best Risk-Adjusted: {comparator.get_best('sharpe').strategy_name}")
print(f"Best Downside: {comparator.get_best('max_drawdown').strategy_name}")
```

---

## Performance Metrics Explained

### Total Return
```
(Final Value - Initial Capital) / Initial Capital
```
Simple percentage gain/loss over the entire period.

### Annual Return
Annualized compound return (assuming 252 trading days/year).

### Max Drawdown
Largest peak-to-trough decline during the backtest.
```
(Peak Value - Trough Value) / Peak Value
```
Lower is better. Indicates downside risk.

### Sharpe Ratio
Risk-adjusted return. Formula:
```
Sharpe = (Annual Return - Risk Free Rate) / Annual Volatility
```
Higher is better. Accounts for both returns and volatility.

---

## Project Structure

```
backtester/
├── backtester_standalone.py    # Self-contained version (easiest)
├── run_backtester.bat          # Windows batch runner
├── requirements.txt            # Python dependencies (none!)
├── README.md                   # This file
│
├── src/                        # Modular version
│   ├── __init__.py
│   ├── assets.py              # Asset definitions
│   ├── backtester.py          # Core engine
│   ├── data_generator.py      # Sample data
│   └── strategies.py          # Trading strategies
│
├── examples/
│   └── example_backtest.py    # Full example
│
└── data/                      # (For user data)
```

---

## Creating Custom Assets

```python
from src.assets import Asset, AssetType, PriceData

# Create price data
dates = ["2023-01-01", "2023-01-02", "2023-01-03", ...]
prices = [100.0, 101.5, 99.8, ...]

# Create asset
my_asset = Asset(
    symbol="MYSTOCK",
    asset_type=AssetType.STOCK,
    price_data=PriceData(dates=dates, prices=prices)
)
```

---

## Creating Custom Strategies

```python
def my_custom_strategy(backtester, portfolio, date_index):
    """
    Custom strategy function.
    
    Args:
        backtester: Backtester instance with access to assets
        portfolio: Current portfolio to execute trades on
        date_index: Current index in the price series (0 = start)
    """
    
    # Example: Buy TECH if it's on day 0
    if date_index == 0:
        asset = backtester.assets["TECH"]
        price = asset.get_price(date_index)
        
        # Buy 100 shares
        portfolio.buy(asset, quantity=100, price=price, date_index=date_index)
    
    # Example: Sell on day 100
    elif date_index == 100:
        portfolio.sell("TECH", quantity=100, price=backtester.assets["TECH"].get_price(date_index))

# Use it
result = backtester.run(my_custom_strategy, 100000, "My Strategy")
```

---

## Data Sources & Extensions

### Using Real Data
Replace the sample generator with real price data:

```python
import pandas as pd

# Load real data
df = pd.read_csv('stock_prices.csv')

# Create asset
real_asset = Asset(
    symbol="AAPL",
    asset_type=AssetType.STOCK,
    price_data=PriceData(
        dates=df['Date'].tolist(),
        prices=df['Close'].tolist()
    )
)

# Use in backtester
assets = {"AAPL": real_asset, ...}
backtester = Backtester(assets)
```

### Common Data Sources
- **Yahoo Finance**: Use `yfinance` library
- **Alpha Vantage**: Free API for stocks
- **CoinGecko**: Free crypto data
- **Quandl**: Commodities and alternatives
- **CSV Files**: Import from local files

---

## Common Use Cases

### 1. Test Buy & Hold vs Active Trading
```python
buy_hold = backtester.run(Strategies.buy_and_hold("TECH"), 100000)
momentum = backtester.run(Strategies.momentum_strategy(), 100000)
Comparator([buy_hold, momentum]).summary()
```

### 2. Find Optimal Allocation
```python
results = []
for stock_pct in [0.3, 0.5, 0.7, 0.9]:
    result = backtester.run(
        Strategies.balanced_portfolio({
            "TECH": stock_pct/2,
            "BOND": stock_pct/2,
            "DIVIDEND": (1-stock_pct)/3,
            "COMMODITY": (1-stock_pct)/3
        }),
        100000,
        f"Stocks {stock_pct*100:.0f}%"
    )
    results.append(result)

Comparator(results).summary()
```

### 3. Backtest During Different Periods
```python
# Bull market
bull_result = backtester.run(strategy, 100000, "2021-2023")

# Bear market  
bear_result = backtester.run(strategy, 100000, "2022-2023")

# Different risk environments
Comparator([bull_result, bear_result]).summary()
```

---

## Troubleshooting

### "Module not found" error
Make sure you're in the correct directory:
```bash
cd /path/to/backtester
python examples/example_backtest.py
```

### Strategy not executing trades
Check that:
1. Asset symbol matches exactly (case-sensitive)
2. Date index is in valid range
3. Sufficient cash for purchase
4. Quantity > 0

### Results look unusual
- Check if dates align across all assets
- Verify price data makes sense
- Print intermediate values for debugging

---

## Limitations & Future Work

**Current Limitations:**
- No transaction costs or slippage
- No dividend/interest calculations  
- Simple daily execution (no intra-day)
- No margin/leverage support
- No options or derivatives

**Planned Enhancements:**
- [ ] Transaction costs and commissions
- [ ] Dividend reinvestment
- [ ] Risk management rules
- [ ] More technical indicators
- [ ] Parameter optimization/walk-forward
- [ ] Monte Carlo simulations
- [ ] Visualization with matplotlib
- [ ] Export to CSV/Excel
- [ ] Web UI for easy testing

---

## Support & Contributing

This is an MVP. For issues or improvements:
1. Check the code comments
2. Review the example usage
3. Extend with your own strategies
4. Share improvements!

---

**Happy backtesting!** 📈
