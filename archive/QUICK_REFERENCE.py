#!/usr/bin/env python3
"""
QUICK REFERENCE - Investment Backtester MVP

Copy-paste examples for common use cases
"""

# ============================================================================
# EXAMPLE 1: Simple Buy & Hold
# ============================================================================
from backtester_standalone import *

assets = create_sample_assets()
backtester = Backtester(assets)

result = backtester.run(
    Strategies.buy_and_hold("TECH"),
    initial_capital=100000,
    strategy_name="Tech Only"
)

print(f"Return: {result.total_return*100:.2f}%")
print(f"Sharpe: {result.sharpe_ratio:.2f}")


# ============================================================================
# EXAMPLE 2: Compare 3 Strategies
# ============================================================================
results = [
    backtester.run(Strategies.buy_and_hold("TECH"), 100000, "TECH"),
    backtester.run(Strategies.buy_and_hold("BOND"), 100000, "BOND"),
    backtester.run(
        Strategies.balanced_portfolio({"TECH": 0.5, "BOND": 0.5}),
        100000,
        "50/50"
    ),
]

comparator = Comparator(results)
print(comparator.summary())


# ============================================================================
# EXAMPLE 3: Test Different Allocations
# ============================================================================
allocations_to_test = [
    {"TECH": 0.8, "BOND": 0.2},
    {"TECH": 0.6, "BOND": 0.4},
    {"TECH": 0.4, "BOND": 0.6},
    {"TECH": 0.2, "BOND": 0.8},
]

results = []
for alloc in allocations_to_test:
    result = backtester.run(
        Strategies.balanced_portfolio(alloc),
        100000,
        f"Stocks {alloc['TECH']*100:.0f}%"
    )
    results.append(result)

Comparator(results).summary()


# ============================================================================
# EXAMPLE 4: Momentum vs Buy & Hold
# ============================================================================
bh = backtester.run(Strategies.buy_and_hold("TECH"), 100000, "B&H")
momentum = backtester.run(Strategies.momentum_strategy(), 100000, "Momentum")

print(f"\nBuy & Hold Return: {bh.total_return*100:.2f}%")
print(f"Momentum Return: {momentum.total_return*100:.2f}%")
print(f"Buy & Hold Sharpe: {bh.sharpe_ratio:.2f}")
print(f"Momentum Sharpe: {momentum.sharpe_ratio:.2f}")


# ============================================================================
# EXAMPLE 5: Conservative vs Aggressive with Rebalancing
# ============================================================================
conservative = backtester.run(
    Strategies.rebalance_strategy(
        {"TECH": 0.2, "DIVIDEND": 0.2, "BOND": 0.6},
        rebalance_frequency=63  # Quarterly
    ),
    100000,
    "Conservative"
)

aggressive = backtester.run(
    Strategies.rebalance_strategy(
        {"TECH": 0.45, "DIVIDEND": 0.45, "BOND": 0.1},
        rebalance_frequency=63
    ),
    100000,
    "Aggressive"
)

print(f"\nConservative Return: {conservative.total_return*100:.2f}%")
print(f"Conservative Max DD: {conservative.max_drawdown*100:.2f}%")
print(f"Aggressive Return: {aggressive.total_return*100:.2f}%")
print(f"Aggressive Max DD: {aggressive.max_drawdown*100:.2f}%")


# ============================================================================
# EXAMPLE 6: Custom Strategy
# ============================================================================
def my_strategy(backtester, portfolio, date_index):
    """Buy TECH on day 0, sell half on day 125."""
    if date_index == 0:
        asset = backtester.assets["TECH"]
        price = asset.get_price(0)
        quantity = 50000 / price  # Use half of capital
        portfolio.buy(asset, quantity, price, 0)
    
    elif date_index == 125:
        # Sell half the position
        pos = portfolio.positions.get("TECH")
        if pos:
            price = backtester.assets["TECH"].get_price(date_index)
            portfolio.sell("TECH", pos.quantity / 2, price)

custom = backtester.run(my_strategy, 100000, "Custom")
print(f"\nCustom Strategy Return: {custom.total_return*100:.2f}%")


# ============================================================================
# EXAMPLE 7: Find Best Strategy
# ============================================================================
results = [
    backtester.run(Strategies.buy_and_hold("TECH"), 100000, "TECH"),
    backtester.run(Strategies.buy_and_hold("DIVIDEND"), 100000, "DIV"),
    backtester.run(Strategies.buy_and_hold("BOND"), 100000, "BOND"),
    backtester.run(Strategies.buy_and_hold("CRYPTO"), 100000, "CRYPTO"),
]

comparator = Comparator(results)
print(f"\nBest by Return: {comparator.get_best('total_return').strategy_name}")
print(f"Best by Sharpe: {comparator.get_best('sharpe').strategy_name}")
print(f"Best Downside: {comparator.get_best('max_drawdown').strategy_name}")


# ============================================================================
# EXAMPLE 8: All 5 Assets Equally Weighted
# ============================================================================
equal = backtester.run(
    Strategies.balanced_portfolio({
        "TECH": 0.2,
        "DIVIDEND": 0.2,
        "BOND": 0.2,
        "CRYPTO": 0.2,
        "COMMODITY": 0.2
    }),
    100000,
    "Equal Weight"
)

print(f"\nEqual 5-Asset Return: {equal.total_return*100:.2f}%")


# ============================================================================
# TIPS
# ============================================================================
"""
1. Access portfolio snapshots:
   result.snapshots[0]  # First day
   result.snapshots[-1]  # Last day
   result.snapshots[100].total_value
   result.snapshots[100].returns

2. Check specific metrics:
   result.total_return      # 0.25 = 25%
   result.annual_return     # Annualized
   result.max_drawdown      # -0.15 = -15%
   result.sharpe_ratio      # 1.5

3. Loop through snapshots:
   for snap in result.snapshots:
       print(f"{snap.date}: ${snap.total_value:.0f}")

4. Access strategy names:
   Strategies.buy_and_hold()
   Strategies.balanced_portfolio()
   Strategies.momentum_strategy()
   Strategies.rebalance_strategy()

5. Available assets:
   "TECH" - volatile growth
   "DIVIDEND" - stable income
   "BOND" - conservative
   "CRYPTO" - high volatility
   "COMMODITY" - moderate

6. Generate different periods:
   create_sample_assets(start_date="2023-01-01", num_days=252)
   create_sample_assets(start_date="2022-01-01", num_days=504)
"""
