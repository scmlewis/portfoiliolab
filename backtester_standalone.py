#!/usr/bin/env python3
"""
Investment Backtester MVP - Complete Example

This is a standalone version that includes all necessary code and runs immediately.
Just copy this file and run it with Python to see the backtester in action.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Callable
import random
from datetime import datetime, timedelta


# ============================================================================
# ASSETS MODULE
# ============================================================================

class AssetType(Enum):
    """Supported asset types."""
    STOCK = "stock"
    BOND = "bond"
    CRYPTO = "crypto"
    COMMODITY = "commodity"


@dataclass
class PriceData:
    """Price data for an asset."""
    dates: List[str]
    prices: List[float]
    
    def __post_init__(self):
        if len(self.dates) != len(self.prices):
            raise ValueError("Dates and prices must have the same length")


@dataclass
class Asset:
    """Represents an investment asset."""
    symbol: str
    asset_type: AssetType
    price_data: PriceData
    
    def get_price(self, date_index: int) -> float:
        """Get price at a specific date index."""
        if date_index < 0 or date_index >= len(self.price_data.prices):
            raise IndexError(f"Date index {date_index} out of range")
        return self.price_data.prices[date_index]
    
    def get_return(self, start_index: int, end_index: int) -> float:
        """Calculate return between two dates."""
        start_price = self.get_price(start_index)
        end_price = self.get_price(end_index)
        if start_price == 0:
            return 0
        return (end_price - start_price) / start_price
    
    def __repr__(self):
        return f"Asset({self.symbol}, {self.asset_type.value})"


# ============================================================================
# DATA GENERATOR
# ============================================================================

def generate_price_series(
    start_price: float,
    num_periods: int,
    daily_return_mean: float = 0.0003,
    daily_return_std: float = 0.015,
    seed: int = None
) -> List[float]:
    """Generate a price series using geometric Brownian motion."""
    if seed is not None:
        random.seed(seed)
    
    prices = [start_price]
    for _ in range(num_periods - 1):
        daily_return = random.gauss(daily_return_mean, daily_return_std)
        new_price = prices[-1] * (1 + daily_return)
        prices.append(max(new_price, 0.01))
    
    return prices


def create_sample_assets(start_date: str = "2023-01-01", num_days: int = 252) -> Dict[str, Asset]:
    """Create sample assets with simulated price data."""
    dates = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    for i in range(num_days):
        while current_date.weekday() >= 5:
            current_date += timedelta(days=1)
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    assets = {}
    
    # Stock - Tech company
    assets["TECH"] = Asset(
        symbol="TECH",
        asset_type=AssetType.STOCK,
        price_data=PriceData(
            dates=dates,
            prices=generate_price_series(100, len(dates), 0.0005, 0.02, seed=42)
        )
    )
    
    # Stock - Dividend
    assets["DIVIDEND"] = Asset(
        symbol="DIVIDEND",
        asset_type=AssetType.STOCK,
        price_data=PriceData(
            dates=dates,
            prices=generate_price_series(100, len(dates), 0.0002, 0.012, seed=43)
        )
    )
    
    # Bond
    assets["BOND"] = Asset(
        symbol="BOND",
        asset_type=AssetType.BOND,
        price_data=PriceData(
            dates=dates,
            prices=generate_price_series(100, len(dates), 0.00005, 0.005, seed=44)
        )
    )
    
    # Crypto
    assets["CRYPTO"] = Asset(
        symbol="CRYPTO",
        asset_type=AssetType.CRYPTO,
        price_data=PriceData(
            dates=dates,
            prices=generate_price_series(100, len(dates), 0.0008, 0.035, seed=45)
        )
    )
    
    # Commodity
    assets["COMMODITY"] = Asset(
        symbol="COMMODITY",
        asset_type=AssetType.COMMODITY,
        price_data=PriceData(
            dates=dates,
            prices=generate_price_series(100, len(dates), 0.0001, 0.018, seed=46)
        )
    )
    
    return assets


# ============================================================================
# BACKTESTER ENGINE
# ============================================================================

@dataclass
class Position:
    """Represents a position in an asset."""
    asset: Asset
    quantity: float
    entry_price: float
    entry_date_index: int


@dataclass
class PortfolioSnapshot:
    """A snapshot of portfolio state at a point in time."""
    date: str
    total_value: float
    positions: Dict[str, Tuple[float, float]]
    cash: float
    returns: float


@dataclass
class BacktestResult:
    """Results from a backtest run."""
    strategy_name: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    snapshots: List[PortfolioSnapshot] = field(default_factory=list)


class Portfolio:
    """Manages a portfolio of assets."""
    
    def __init__(self, initial_capital: float):
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions: Dict[str, Position] = {}
    
    def buy(self, asset: Asset, quantity: float, price: float, date_index: int):
        """Buy an asset."""
        cost = quantity * price
        # Allow small floating-point rounding errors (within 0.01)
        if cost > self.cash + 0.01:
            raise ValueError(f"Insufficient cash: need {cost}, have {self.cash}")
        
        self.cash -= cost
        
        if asset.symbol in self.positions:
            pos = self.positions[asset.symbol]
            new_quantity = pos.quantity + quantity
            pos.entry_price = (pos.entry_price * pos.quantity + price * quantity) / new_quantity
            pos.quantity = new_quantity
        else:
            self.positions[asset.symbol] = Position(
                asset=asset,
                quantity=quantity,
                entry_price=price,
                entry_date_index=date_index
            )
    
    def sell(self, symbol: str, quantity: float, price: float):
        """Sell an asset."""
        if symbol not in self.positions:
            raise ValueError(f"No position in {symbol}")
        
        pos = self.positions[symbol]
        if quantity > pos.quantity:
            raise ValueError(f"Insufficient quantity: have {pos.quantity}, want {quantity}")
        
        proceeds = quantity * price
        self.cash += proceeds
        pos.quantity -= quantity
        
        if pos.quantity == 0:
            del self.positions[symbol]
    
    def get_value(self, date_index: int) -> float:
        """Get total portfolio value at a given date."""
        portfolio_value = self.cash
        for pos in self.positions.values():
            price = pos.asset.get_price(date_index)
            portfolio_value += pos.quantity * price
        return portfolio_value
    
    def get_snapshot(self, date: str, date_index: int) -> PortfolioSnapshot:
        """Get a portfolio snapshot at a specific date."""
        total_value = self.get_value(date_index)
        positions_dict = {}
        for symbol, pos in self.positions.items():
            price = pos.asset.get_price(date_index)
            positions_dict[symbol] = (pos.quantity, price)
        
        returns = (total_value - self.initial_capital) / self.initial_capital
        
        return PortfolioSnapshot(
            date=date,
            total_value=total_value,
            positions=positions_dict,
            cash=self.cash,
            returns=returns
        )


class Backtester:
    """Main backtester engine."""
    
    def __init__(self, assets: Dict[str, Asset]):
        self.assets = assets
        first_asset = next(iter(assets.values()))
        self.dates = first_asset.price_data.dates
        self.num_periods = len(self.dates)
    
    def run(self, 
            strategy_func: Callable,
            initial_capital: float,
            strategy_name: str = "Backtest") -> BacktestResult:
        """Run a backtest with a given strategy."""
        portfolio = Portfolio(initial_capital)
        snapshots = []
        
        for date_index in range(self.num_periods):
            strategy_func(self, portfolio, date_index)
            snapshot = portfolio.get_snapshot(self.dates[date_index], date_index)
            snapshots.append(snapshot)
        
        final_value = portfolio.get_value(self.num_periods - 1)
        total_return = (final_value - initial_capital) / initial_capital
        
        days = self.num_periods - 1
        years = days / 252.0
        annual_return = (total_return + 1) ** (1 / years) - 1 if years > 0 else 0
        
        max_drawdown = self._calculate_max_drawdown(snapshots)
        sharpe_ratio = self._calculate_sharpe_ratio(snapshots)
        
        return BacktestResult(
            strategy_name=strategy_name,
            start_date=self.dates[0],
            end_date=self.dates[-1],
            initial_capital=initial_capital,
            final_value=final_value,
            total_return=total_return,
            annual_return=annual_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            snapshots=snapshots
        )
    
    @staticmethod
    def _calculate_max_drawdown(snapshots: List[PortfolioSnapshot]) -> float:
        """Calculate maximum drawdown."""
        if not snapshots:
            return 0
        
        peak = snapshots[0].total_value
        max_dd = 0
        
        for snapshot in snapshots:
            if snapshot.total_value > peak:
                peak = snapshot.total_value
            
            dd = (peak - snapshot.total_value) / peak
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    @staticmethod
    def _calculate_sharpe_ratio(snapshots: List[PortfolioSnapshot], risk_free_rate: float = 0) -> float:
        """Calculate Sharpe ratio."""
        if len(snapshots) < 2:
            return 0
        
        returns = []
        for i in range(1, len(snapshots)):
            prev_value = snapshots[i - 1].total_value
            curr_value = snapshots[i].total_value
            daily_return = (curr_value - prev_value) / prev_value
            returns.append(daily_return)
        
        if not returns:
            return 0
        
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0
        
        annual_return = (snapshots[-1].total_value - snapshots[0].total_value) / snapshots[0].total_value
        annual_std = std_dev * (252 ** 0.5)
        
        sharpe = (annual_return - risk_free_rate) / annual_std if annual_std > 0 else 0
        return sharpe


class Comparator:
    """Compares multiple backtest results."""
    
    def __init__(self, results: List[BacktestResult]):
        self.results = results
    
    def summary(self) -> str:
        """Get a summary comparison of all results."""
        output = "=" * 100 + "\n"
        output += "BACKTEST COMPARISON SUMMARY\n"
        output += "=" * 100 + "\n\n"
        
        output += f"{'Strategy':<20} {'Initial':<12} {'Final':<12} {'Return %':<12} {'Annual %':<12} {'Max DD %':<12} {'Sharpe':<10}\n"
        output += "-" * 100 + "\n"
        
        for result in self.results:
            output += (f"{result.strategy_name:<20} "
                      f"${result.initial_capital:<11,.0f} "
                      f"${result.final_value:<11,.0f} "
                      f"{result.total_return*100:<11.2f}% "
                      f"{result.annual_return*100:<11.2f}% "
                      f"{result.max_drawdown*100:<11.2f}% "
                      f"{result.sharpe_ratio:<9.2f}\n")
        
        output += "=" * 100 + "\n"
        return output
    
    def get_best(self, metric: str = "total_return") -> BacktestResult:
        """Get the best result by a specific metric."""
        metric_map = {
            "total_return": lambda r: r.total_return,
            "annual_return": lambda r: r.annual_return,
            "sharpe": lambda r: r.sharpe_ratio,
            "max_drawdown": lambda r: -r.max_drawdown,
        }
        
        if metric not in metric_map:
            raise ValueError(f"Unknown metric: {metric}")
        
        return max(self.results, key=metric_map[metric])


# ============================================================================
# STRATEGIES
# ============================================================================

class Strategies:
    """Collection of example trading strategies."""
    
    @staticmethod
    def buy_and_hold(symbol: str, percent_allocation: float = 1.0):
        """Buy and hold strategy."""
        def strategy(backtester, portfolio, date_index):
            if date_index == 0:
                asset = backtester.assets[symbol]
                price = asset.get_price(date_index)
                capital = portfolio.cash * percent_allocation
                quantity = capital / price
                portfolio.buy(asset, quantity, price, date_index)
        
        return strategy
    
    @staticmethod
    def balanced_portfolio(allocations: dict):
        """Balanced portfolio strategy."""
        def strategy(backtester, portfolio, date_index):
            if date_index == 0:
                total_allocation = sum(allocations.values())
                if total_allocation > 1.0:
                    raise ValueError("Total allocation exceeds 100%")
                
                for symbol, allocation in allocations.items():
                    asset = backtester.assets[symbol]
                    price = asset.get_price(date_index)
                    capital = portfolio.initial_capital * allocation
                    quantity = capital / price
                    portfolio.buy(asset, quantity, price, date_index)
        
        return strategy
    
    @staticmethod
    def momentum_strategy(short_window: int = 20, long_window: int = 50):
        """Momentum strategy - moving average crossover."""
        def strategy(backtester, portfolio, date_index):
            if date_index < long_window:
                return
            
            for symbol, asset in backtester.assets.items():
                prices = asset.price_data.prices
                
                short_ma = sum(prices[date_index-short_window:date_index]) / short_window
                long_ma = sum(prices[date_index-long_window:date_index]) / long_window
                
                current_price = asset.get_price(date_index)
                
                if short_ma > long_ma and symbol not in portfolio.positions:
                    capital = portfolio.cash / len(backtester.assets)
                    quantity = capital / current_price
                    if quantity > 0 and capital > 0:
                        portfolio.buy(asset, quantity, current_price, date_index)
                
                elif short_ma < long_ma and symbol in portfolio.positions:
                    pos = portfolio.positions[symbol]
                    portfolio.sell(symbol, pos.quantity, current_price)
        
        return strategy
    
    @staticmethod
    def rebalance_strategy(allocations: dict, rebalance_frequency: int = 63):
        """Periodic rebalancing strategy."""
        def strategy(backtester, portfolio, date_index):
            should_rebalance = (date_index == 0 or 
                              date_index % rebalance_frequency == 0)
            
            if should_rebalance:
                symbols_to_sell = list(portfolio.positions.keys())
                for symbol in symbols_to_sell:
                    asset = backtester.assets[symbol]
                    pos = portfolio.positions[symbol]
                    price = asset.get_price(date_index)
                    portfolio.sell(symbol, pos.quantity, price)
                
                total_value = portfolio.get_value(date_index)
                for symbol, allocation in allocations.items():
                    asset = backtester.assets[symbol]
                    price = asset.get_price(date_index)
                    capital = total_value * allocation
                    quantity = capital / price
                    if quantity > 0:
                        portfolio.buy(asset, quantity, price, date_index)
        
        return strategy
    
    @staticmethod
    def rsi_oversold_strategy(symbol: str, rsi_period: int = 14, oversold_level: int = 30, allocation: float = 1.0):
        """RSI Oversold strategy - buy when RSI < oversold_level"""
        def calculate_rsi(prices, period):
            deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            seed = deltas[:period]
            up = sum([d for d in seed if d > 0]) / period
            down = -sum([d for d in seed if d < 0]) / period
            rs = up / down if down != 0 else 0
            rsi = 100 - 100 / (1 + rs)
            
            for delta in deltas[period:]:
                up = (up * (period - 1) + (delta if delta > 0 else 0)) / period
                down = (down * (period - 1) + (-delta if delta < 0 else 0)) / period
                rs = up / down if down != 0 else 0
                rsi = 100 - 100 / (1 + rs)
            
            return rsi
        
        def strategy(backtester, portfolio, date_index):
            if date_index < rsi_period:
                return
            
            asset = backtester.assets[symbol]
            prices = asset.price_data.prices
            rsi = calculate_rsi(prices[:date_index+1], rsi_period)
            current_price = asset.get_price(date_index)
            
            if rsi < oversold_level and symbol not in portfolio.positions:
                capital = portfolio.cash * allocation
                quantity = capital / current_price
                if quantity > 0 and capital > 0:
                    portfolio.buy(asset, quantity, current_price, date_index)
            
            elif rsi > 70 and symbol in portfolio.positions:
                pos = portfolio.positions[symbol]
                portfolio.sell(symbol, pos.quantity, current_price)
        
        return strategy
    
    @staticmethod
    def macd_strategy(symbol: str, fast: int = 12, slow: int = 26, signal: int = 9, allocation: float = 1.0):
        """MACD Crossover strategy"""
        def calculate_ema(prices, period):
            if len(prices) < period:
                return sum(prices) / len(prices)
            ema = sum(prices[:period]) / period
            for price in prices[period:]:
                ema = price * (2 / (period + 1)) + ema * (1 - 2 / (period + 1))
            return ema
        
        def strategy(backtester, portfolio, date_index):
            if date_index < slow + signal - 1:
                return
            
            asset = backtester.assets[symbol]
            prices = asset.price_data.prices[:date_index+1]
            
            # Calculate MACD line (difference between fast and slow EMAs)
            ema_fast = calculate_ema(prices, fast)
            ema_slow = calculate_ema(prices, slow)
            macd = ema_fast - ema_slow
            
            # Calculate MACD signal line (EMA of MACD values)
            # We need to calculate MACD for all previous prices
            macd_values = []
            for i in range(slow, len(prices) + 1):
                fast_ema = calculate_ema(prices[:i], fast)
                slow_ema = calculate_ema(prices[:i], slow)
                macd_values.append(fast_ema - slow_ema)
            
            # Signal line is EMA of MACD values
            signal_line = calculate_ema(macd_values, signal)
            
            current_price = asset.get_price(date_index)
            
            # Buy when MACD crosses above signal line
            if macd > signal_line and symbol not in portfolio.positions:
                capital = portfolio.cash * allocation
                quantity = capital / current_price
                if quantity > 0 and capital > 0:
                    portfolio.buy(asset, quantity, current_price, date_index)
            
            # Sell when MACD crosses below signal line
            elif macd < signal_line and symbol in portfolio.positions:
                pos = portfolio.positions[symbol]
                portfolio.sell(symbol, pos.quantity, current_price)
        
        return strategy
    
    @staticmethod
    def bollinger_bands_strategy(symbol: str, period: int = 20, num_std: float = 2.0, allocation: float = 1.0):
        """Bollinger Bands strategy - buy at lower band, sell at upper band"""
        def calculate_sma(prices, period):
            return sum(prices[-period:]) / period if len(prices) >= period else sum(prices) / len(prices)
        
        def calculate_std(prices, period):
            sma = calculate_sma(prices, period)
            variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
            return variance ** 0.5
        
        def strategy(backtester, portfolio, date_index):
            if date_index < period:
                return
            
            asset = backtester.assets[symbol]
            prices = asset.price_data.prices[:date_index+1]
            
            sma = calculate_sma(prices, period)
            std = calculate_std(prices, period)
            upper_band = sma + (num_std * std)
            lower_band = sma - (num_std * std)
            
            current_price = asset.get_price(date_index)
            
            if current_price <= lower_band and symbol not in portfolio.positions:
                capital = portfolio.cash * allocation
                quantity = capital / current_price
                if quantity > 0 and capital > 0:
                    portfolio.buy(asset, quantity, current_price, date_index)
            
            elif current_price >= upper_band and symbol in portfolio.positions:
                pos = portfolio.positions[symbol]
                portfolio.sell(symbol, pos.quantity, current_price)
        
        return strategy


# ============================================================================
# MAIN EXAMPLE
# ============================================================================

def main():
    """Run example backtests and comparisons."""
    
    print("\n" + "=" * 100)
    print("INVESTMENT BACKTESTER MVP - EXAMPLE")
    print("=" * 100 + "\n")
    
    print("Creating sample assets (stocks, bonds, crypto, commodities)...")
    assets = create_sample_assets(start_date="2023-01-01", num_days=252)
    
    print(f"Assets created: {', '.join(assets.keys())}\n")
    
    backtester = Backtester(assets)
    
    results = []
    
    print("Running: Buy & Hold (TECH only)...")
    result1 = backtester.run(
        strategy_func=Strategies.buy_and_hold("TECH", percent_allocation=1.0),
        initial_capital=100000,
        strategy_name="Buy & Hold TECH"
    )
    results.append(result1)
    
    print("Running: Buy & Hold (DIVIDEND stock)...")
    result2 = backtester.run(
        strategy_func=Strategies.buy_and_hold("DIVIDEND", percent_allocation=1.0),
        initial_capital=100000,
        strategy_name="Buy & Hold DIVIDEND"
    )
    results.append(result2)
    
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
    
    print("Running: Momentum Strategy...")
    result5 = backtester.run(
        strategy_func=Strategies.momentum_strategy(short_window=20, long_window=50),
        initial_capital=100000,
        strategy_name="Momentum (MA 20/50)"
    )
    results.append(result5)
    
    print("Running: Conservative with Quarterly Rebalancing...")
    result6 = backtester.run(
        strategy_func=Strategies.rebalance_strategy({
            "TECH": 0.2,
            "DIVIDEND": 0.2,
            "BOND": 0.6
        }, rebalance_frequency=63),
        initial_capital=100000,
        strategy_name="Conservative Rebalanced"
    )
    results.append(result6)
    
    print("Running: Aggressive with Quarterly Rebalancing...")
    result7 = backtester.run(
        strategy_func=Strategies.rebalance_strategy({
            "TECH": 0.45,
            "DIVIDEND": 0.45,
            "BOND": 0.1
        }, rebalance_frequency=63),
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
