# Quick Start Guide

## 🚀 Get Running in 30 Seconds

### Step 1: Run the Backtester
```bash
python backtester_standalone.py
```

That's it! You should see a comparison of 7 different investment strategies.

### Step 2: Understand the Output

You'll see a table like:
```
Strategy                 Initial      Final        Return %   Sharpe
Buy & Hold TECH         $100,000     $125,430      25.43%     1.55
Balanced 5-Asset        $100,000     $120,500      20.50%     2.31
```

Each row represents a different strategy. Compare them to see:
- **Return %**: How much profit the strategy made
- **Sharpe**: Risk-adjusted return (higher = better risk-reward)

---

## 📚 Next: Copy & Paste Examples

Open `QUICK_REFERENCE.py` and copy any example. Here are the easiest:

### Test Buy & Hold (Single Asset)
```python
from backtester_standalone import *

assets = create_sample_assets()
backtester = Backtester(assets)

result = backtester.run(
    Strategies.buy_and_hold("TECH"),  # Buy & hold TECH stock
    initial_capital=100000,
    strategy_name="My Test"
)

print(f"Profit: {result.total_return*100:.2f}%")
```

### Compare Multiple Strategies
```python
results = [
    backtester.run(Strategies.buy_and_hold("TECH"), 100000, "Just Tech"),
    backtester.run(Strategies.buy_and_hold("BOND"), 100000, "Just Bonds"),
    backtester.run(
        Strategies.balanced_portfolio({"TECH": 0.5, "BOND": 0.5}),
        100000,
        "50/50 Mix"
    ),
]

Comparator(results).summary()
```

---

## 🎯 Available Assets

The backtester includes 5 sample assets:

| Symbol | Type | Volatility | Description |
|--------|------|-----------|-------------|
| TECH | Stock | High | Growth stock - risky but higher returns |
| DIVIDEND | Stock | Medium | Dividend stock - steady returns |
| BOND | Bond | Low | Safe fixed income - stable |
| CRYPTO | Crypto | Very High | Cryptocurrency - volatile |
| COMMODITY | Commodity | Medium | Commodity prices |

---

## 🎲 Available Strategies

### 1. Buy & Hold
Hold one asset for the entire period.
```python
Strategies.buy_and_hold("TECH")
```

### 2. Balanced Portfolio
Split money between multiple assets.
```python
Strategies.balanced_portfolio({
    "TECH": 0.3,        # 30% in tech
    "DIVIDEND": 0.3,    # 30% in dividend stock
    "BOND": 0.4         # 40% in bonds
})
```

### 3. Momentum Strategy
Buy assets that are going up, sell those going down (using moving averages).
```python
Strategies.momentum_strategy(short_window=20, long_window=50)
```

### 4. Rebalancing
Periodically rebalance to target allocations.
```python
Strategies.rebalance_strategy({
    "TECH": 0.4,
    "BOND": 0.6
}, rebalance_frequency=63)  # Rebalance every 63 days
```

---

## 📊 Understanding the Metrics

### Total Return
The overall profit/loss as a percentage.
- 25% = Investment grew from $100k to $125k
- -10% = Investment dropped from $100k to $90k

### Annual Return
The yearly return rate (annualized).
- If 1-year backtest returned 20%, annual return = 20%
- If 6-month backtest returned 10%, annualized = ~20%

### Max Drawdown
The biggest drop from peak to bottom.
- -15% = At worst, portfolio dropped 15% from its peak
- Lower is better (less painful during downturns)

### Sharpe Ratio
Risk-adjusted return. How much return per unit of risk.
- 2.0 = Excellent (good returns, low volatility)
- 1.0 = Good
- 0.5 = Fair
- Higher is better

---

## 🔧 What You Can Do Now

✅ Run the backtester on sample data
✅ Compare 7 pre-built strategies
✅ Create custom allocations
✅ Test momentum strategies
✅ See portfolio snapshots
✅ Calculate 4 key metrics
✅ Export results

---

## 📖 Learn More

- **GUIDE.md** - Detailed user guide with all features
- **QUICK_REFERENCE.py** - 8 copy-paste examples
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **Code Comments** - Inline documentation

---

## ❓ Common Questions

**Q: Can I use real stock data?**
A: Yes! Replace the sample data generator with real prices from Yahoo Finance or similar.

**Q: How do I create my own strategy?**
A: Write a function that takes `(backtester, portfolio, date_index)` and executes trades.

**Q: What if I want more strategies?**
A: Add them to the `Strategies` class or create your own functions.

**Q: Can I change the time period?**
A: Yes: `create_sample_assets(start_date="2023-01-01", num_days=252)`

**Q: Why no transaction costs?**
A: This is an MVP! Add them in your custom strategy functions.

---

## 🎓 Learning Path

**Day 1**: Run the backtester and review the output
**Day 2**: Try 2-3 examples from QUICK_REFERENCE.py
**Day 3**: Create a custom allocation
**Day 4**: Write your own strategy function
**Day 5**: Add real market data

---

## 💡 Pro Tips

1. **Compare strategies**: Use `Comparator()` to find the best
2. **Check snapshots**: Access `result.snapshots` for daily values
3. **Test allocations**: Try different percentages to optimize
4. **Use Sharpe ratio**: Higher Sharpe = better risk-adjusted returns
5. **Consider drawdown**: A strategy with lower max drawdown is "smoother"

---

Enjoy backtesting! Questions? Check the code comments or GUIDE.md. 📈
