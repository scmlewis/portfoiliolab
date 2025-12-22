"""Example strategies for backtesting."""
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
        """
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
        """
        Balanced portfolio strategy - allocate to multiple assets.
        
        Args:
            allocations: Dict of {symbol: percentage} (percentages should sum to <= 1.0)
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
                    portfolio.buy(asset, quantity, price, date_index)
        
        return strategy
    
    @staticmethod
    def momentum_strategy(short_window: int = 20, long_window: int = 50):
        """
        Simple momentum strategy - compare short and long term moving averages.
        
        Args:
            short_window: Short moving average window
            long_window: Long moving average window
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
            rebalance_frequency: Number of periods between rebalancing
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
    def stock_bond_allocation(stock_allocation: float = 0.7, rebalance_quarterly: bool = True):
        """
        Traditional stock/bond allocation strategy.
        
        Args:
            stock_allocation: Percentage allocated to stocks (0-1)
            rebalance_quarterly: Whether to rebalance quarterly
        """
        bond_allocation = 1.0 - stock_allocation
        stocks = ["TECH", "DIVIDEND"]
        bonds = ["BOND"]
        
        stock_per = stock_allocation / len(stocks)
        bond_per = bond_allocation / len(bonds)
        
        allocations = {}
        for stock in stocks:
            allocations[stock] = stock_per
        for bond in bonds:
            allocations[bond] = bond_per
        
        rebalance_freq = 63 if rebalance_quarterly else None
        
        if rebalance_freq:
            return Strategies.rebalance_strategy(allocations, rebalance_freq)
        else:
            return Strategies.balanced_portfolio(allocations)
