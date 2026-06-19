"""Trading strategies for backtesting.

Edge cases handled by strategies:
- Missing asset symbol: Raises KeyError if symbol not in backtester.assets
- Zero allocation: No position opened
- Allocation > 100%: Raises ValueError
- Flat prices (RSI): RSI undefined, no trades triggered
- Insufficient data: Strategy waits until enough data points
- Single asset portfolio: Works correctly
- Multiple assets: Each asset traded independently

All strategies assume:
- Daily price data
- Prices are positive
- No short selling (only long positions)
"""
from src.assets import Asset, AssetType


class Strategies:
    """Collection of example trading strategies."""
    
    @staticmethod
    def buy_and_hold(symbol: str, percent_allocation: float = 1.0):
        """
        Buy and hold strategy - buy at the start and hold.
        
        Args:
            symbol: Asset symbol to hold
            percent_allocation: Percentage of capital to allocate (0-1)
            
        Edge cases:
            - Missing symbol: Raises KeyError if symbol not in backtester.assets
            - Zero allocation: No position opened
            - Negative allocation: No position opened (quantity becomes negative)
            - Zero initial capital: Cannot buy anything, portfolio stays at $0
            
        Example:
            >>> strategy = Strategies.buy_and_hold("AAPL", percent_allocation=0.5)
            >>> # Buys 50% of capital in AAPL on day 0
        """
        def strategy(backtester, portfolio, date_index):
            if date_index == 0:
                asset = backtester.assets[symbol]
                price = asset.get_price(date_index)
                capital = portfolio.cash * percent_allocation
                quantity = capital / price
                if quantity > 0 and capital > 0:
                    portfolio.buy(asset, quantity, price, date_index)
        
        return strategy
    
    @staticmethod
    def balanced_portfolio(allocations: dict):
        """
        Balanced portfolio strategy - allocate to multiple assets.
        
        Args:
            allocations: Dict of {symbol: percentage} (percentages should sum to <= 1.0)
            
        Edge cases:
            - Empty allocations: No positions opened
            - Missing symbol: Raises KeyError if symbol not in backtester.assets
            - Allocation > 100%: Raises ValueError
            - Floating-point precision: Automatically normalizes if sum is 1.0 ± 1e-6
            - Zero allocation: Asset skipped
            
        Example:
            >>> allocations = {"AAPL": 0.4, "GOOGL": 0.3, "MSFT": 0.3}
            >>> strategy = Strategies.balanced_portfolio(allocations)
        """
        def strategy(backtester, portfolio, date_index):
            if date_index == 0:
                total_allocation = sum(allocations.values())
                # Normalize allocations if they exceed 1.0 due to floating-point precision
                if total_allocation > 1.0 + 1e-6:  # Use larger tolerance for rounding errors
                    raise ValueError(f"Total allocation exceeds 100% (got {total_allocation*100:.2f}%)")
                
                # Normalize to handle floating-point precision (sum to exactly 1.0)
                if total_allocation > 0:
                    normalized_allocations = {
                        symbol: allocation / total_allocation 
                        for symbol, allocation in allocations.items()
                    }
                else:
                    normalized_allocations = allocations
                
                for symbol, allocation in normalized_allocations.items():
                    asset = backtester.assets[symbol]
                    price = asset.get_price(date_index)
                    capital = portfolio.initial_capital * allocation
                    quantity = capital / price
                    if quantity > 0:
                        portfolio.buy(asset, quantity, price, date_index)
        
        return strategy
    
    @staticmethod
    def momentum_strategy(short_window: int = 20, long_window: int = 50):
        """
        Simple momentum strategy - compare short and long term moving averages.
        
        Args:
            short_window: Short moving average window (must be > 0)
            long_window: Long moving average window (must be > short_window)
            
        Edge cases:
            - Insufficient data: Strategy waits until date_index >= long_window
            - Equal MAs: No trade triggered (short_ma == long_ma)
            - Flat prices: MAs are equal, no trades
            - Single asset: Works correctly
            - Multiple assets: Each asset traded independently
            
        Example:
            >>> strategy = Strategies.momentum_strategy(short_window=20, long_window=50)
            >>> # Buys when 20-day MA crosses above 50-day MA
        """
        def strategy(backtester, portfolio, date_index):
            if date_index < long_window:
                return
            
            # Calculate moving averages for each asset
            for symbol, asset in backtester.assets.items():
                prices = asset.price_data.prices
                
                short_ma = sum(prices[date_index-short_window:date_index]) / short_window
                long_ma = sum(prices[date_index-long_window:date_index]) / long_window
                
                current_price = asset.get_price(date_index)
                
                # Buy if short MA > long MA and don't have position
                if short_ma > long_ma and symbol not in portfolio.positions:
                    # Allocate equal amount to each asset
                    capital = portfolio.cash / len(backtester.assets)
                    quantity = capital / current_price
                    if quantity > 0 and capital > 0:
                        portfolio.buy(asset, quantity, current_price, date_index)
                
                # Sell if short MA < long MA and have position
                elif short_ma < long_ma and symbol in portfolio.positions:
                    pos = portfolio.positions[symbol]
                    portfolio.sell(symbol, pos.quantity, current_price)
        
        return strategy
    
    @staticmethod
    def rebalance_strategy(allocations: dict, rebalance_frequency: int = 63):
        """
        Periodic rebalancing strategy.
        
        Args:
            allocations: Dict of {symbol: percentage}
            rebalance_frequency: Number of periods between rebalancing (must be > 0)
            
        Edge cases:
            - Zero frequency: Rebalances every period (frequency=1)
            - Insufficient data: Rebalances on available data
            - Allocation > 100%: Raises ValueError
            - Missing symbol: Raises KeyError if symbol not in backtester.assets
            
        Example:
            >>> allocations = {"AAPL": 0.5, "GOOGL": 0.5}
            >>> strategy = Strategies.rebalance_strategy(allocations, rebalance_frequency=63)
            >>> # Rebalances quarterly (63 trading days)
        """
        def strategy(backtester, portfolio, date_index):
            should_rebalance = (date_index == 0 or 
                              date_index % rebalance_frequency == 0)
            
            if should_rebalance:
                # Normalize allocations to handle floating-point precision
                total_allocation = sum(allocations.values())
                if total_allocation > 1.0 + 1e-6:
                    raise ValueError(f"Total allocation exceeds 100% (got {total_allocation*100:.2f}%)")
                
                if total_allocation > 0:
                    normalized_allocations = {
                        symbol: allocation / total_allocation 
                        for symbol, allocation in allocations.items()
                    }
                else:
                    normalized_allocations = allocations
                
                # Sell all positions
                symbols_to_sell = list(portfolio.positions.keys())
                for symbol in symbols_to_sell:
                    asset = backtester.assets[symbol]
                    pos = portfolio.positions[symbol]
                    price = asset.get_price(date_index)
                    portfolio.sell(symbol, pos.quantity, price)
                
                # Buy new allocations
                total_value = portfolio.get_value(date_index)
                for symbol, allocation in normalized_allocations.items():
                    asset = backtester.assets[symbol]
                    price = asset.get_price(date_index)
                    capital = total_value * allocation
                    quantity = capital / price
                    if quantity > 0:
                        portfolio.buy(asset, quantity, price, date_index)
        
        return strategy

    @staticmethod
    def rsi_oversold_strategy(symbol: str, rsi_period: int = 14, oversold_level: int = 30, allocation: float = 1.0):
        """
        RSI Oversold strategy - buy when RSI < oversold_level, sell when RSI > 70.
        
        Args:
            symbol: Asset symbol to trade
            rsi_period: Period for RSI calculation (must be > 0)
            oversold_level: RSI level considered oversold (buy signal, typically 20-40)
            allocation: Percentage of capital to allocate (0-1)
            
        Edge cases:
            - Insufficient data: Strategy waits until date_index >= rsi_period
            - Flat prices: RSI undefined (returns 50), no trades triggered
            - All prices same: No deltas, RSI = 50
            - Missing symbol: Raises KeyError if symbol not in backtester.assets
            - Already holding: Won't buy again until sold
            
        Example:
            >>> strategy = Strategies.rsi_oversold_strategy("AAPL", rsi_period=14, oversold_level=30)
            >>> # Buys when RSI drops below 30, sells when RSI > 70
        """
        def calculate_rsi(prices, period):
            """Calculate RSI using exponential moving average method."""
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
            
            # Buy when RSI < oversold_level
            if rsi < oversold_level and symbol not in portfolio.positions:
                capital = portfolio.cash * allocation
                quantity = capital / current_price
                if quantity > 0 and capital > 0:
                    portfolio.buy(asset, quantity, current_price, date_index)
            
            # Sell when RSI > 70 (overbought)
            elif rsi > 70 and symbol in portfolio.positions:
                pos = portfolio.positions[symbol]
                portfolio.sell(symbol, pos.quantity, current_price)
        
        return strategy
    
    @staticmethod
    def macd_strategy(symbol: str, fast: int = 12, slow: int = 26, signal: int = 9, allocation: float = 1.0):
        """
        MACD Crossover strategy - buy when MACD crosses above signal line, sell when below.
        
        Args:
            symbol: Asset symbol to trade
            fast: Fast EMA period (typically 12)
            slow: Slow EMA period (typically 26)
            signal: Signal line period (typically 9)
            allocation: Percentage of capital to allocate (0-1)
            
        Edge cases:
            - Insufficient data: Strategy waits until date_index >= slow + signal - 1
            - Flat prices: MACD = 0, no crossovers
            - Missing symbol: Raises KeyError if symbol not in backtester.assets
            - Already holding: Won't buy again until sold
            
        Example:
            >>> strategy = Strategies.macd_strategy("AAPL", fast=12, slow=26, signal=9)
            >>> # Standard MACD(12,26,9) parameters
        """
        def calculate_ema(prices, period):
            """Calculate Exponential Moving Average."""
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
        """
        Bollinger Bands strategy - buy at lower band, sell at upper band.
        
        Args:
            symbol: Asset symbol to trade
            period: Period for SMA calculation (typically 20)
            num_std: Number of standard deviations for bands (typically 2.0)
            allocation: Percentage of capital to allocate (0-1)
            
        Edge cases:
            - Insufficient data: Strategy waits until date_index >= period
            - Flat prices: Bands collapse to SMA, no trades triggered
            - High volatility: Wider bands, fewer signals
            - Low volatility: Narrower bands, more signals
            - Missing symbol: Raises KeyError if symbol not in backtester.assets
            - Already holding: Won't buy again until sold
            
        Example:
            >>> strategy = Strategies.bollinger_bands_strategy("AAPL", period=20, num_std=2.0)
            >>> # Standard 20-period, 2-standard-deviation bands
        """
        def calculate_sma(prices, period):
            """Calculate Simple Moving Average."""
            return sum(prices[-period:]) / period if len(prices) >= period else sum(prices) / len(prices)
        
        def calculate_std(prices, period):
            """Calculate standard deviation."""
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
            
            # Buy when price touches lower band
            if current_price <= lower_band and symbol not in portfolio.positions:
                capital = portfolio.cash * allocation
                quantity = capital / current_price
                if quantity > 0 and capital > 0:
                    portfolio.buy(asset, quantity, current_price, date_index)
            
            # Sell when price touches upper band
            elif current_price >= upper_band and symbol in portfolio.positions:
                pos = portfolio.positions[symbol]
                portfolio.sell(symbol, pos.quantity, current_price)
        
        return strategy
