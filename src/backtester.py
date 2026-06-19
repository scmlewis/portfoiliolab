"""Core backtester engine."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from src.assets import Asset, AssetType


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
    positions: Dict[str, Tuple[float, float]]  # symbol: (quantity, current_price)
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
    """Manages a portfolio of assets.
    
    Edge cases handled:
    - Zero initial capital: Portfolio starts with $0, cannot buy anything
    - Negative capital: Raises ValueError
    - Floating-point precision: Allows 0.01 tolerance for rounding errors
    """
    
    def __init__(self, initial_capital: float):
        if initial_capital < 0:
            raise ValueError(f"Initial capital cannot be negative: {initial_capital}")
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions: Dict[str, Position] = {}
    
    def buy(self, asset: Asset, quantity: float, price: float, date_index: int):
        """Buy an asset.
        
        Args:
            asset: Asset to buy
            quantity: Number of units to buy (must be > 0)
            price: Price per unit (must be > 0)
            date_index: Date index for the trade
            
        Raises:
            ValueError: If quantity or price is invalid, or insufficient cash
        """
        if quantity <= 0:
            raise ValueError(f"Quantity must be positive: {quantity}")
        if price <= 0:
            raise ValueError(f"Price must be positive: {price}")
            
        cost = quantity * price
        # Allow small floating-point rounding errors (within 0.01)
        if cost > self.cash + 0.01:
            raise ValueError(f"Insufficient cash: need {cost:.2f}, have {self.cash:.2f}")
        
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
        """Sell an asset.
        
        Args:
            symbol: Symbol of asset to sell
            quantity: Number of units to sell (must be > 0)
            price: Price per unit (must be > 0)
            
        Raises:
            ValueError: If symbol not found, quantity invalid, or price invalid
        """
        if quantity <= 0:
            raise ValueError(f"Quantity must be positive: {quantity}")
        if price <= 0:
            raise ValueError(f"Price must be positive: {price}")
            
        if symbol not in self.positions:
            raise ValueError(f"No position in {symbol}")
        
        pos = self.positions[symbol]
        if quantity > pos.quantity:
            raise ValueError(f"Insufficient quantity: have {pos.quantity}, want to sell {quantity}")
        
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
    """Main backtester engine.
    
    Edge cases handled:
    - Empty assets dictionary: Raises ValueError
    - Single asset: Works correctly
    - Insufficient data: Returns zero metrics
    - Zero initial capital: Portfolio starts with $0
    """
    
    def __init__(self, assets: Dict[str, Asset]):
        if not assets:
            raise ValueError("Assets dictionary cannot be empty")
        self.assets = assets
        # Get dates from first asset
        first_asset = next(iter(assets.values()))
        self.dates = first_asset.price_data.dates
        self.num_periods = len(self.dates)
    
    def run(self, 
            strategy_func,
            initial_capital: float,
            strategy_name: str = "Backtest") -> BacktestResult:
        """
        Run a backtest with a given strategy.
        
        Args:
            strategy_func: Function that takes (backtester, portfolio, date_index) and executes trades
            initial_capital: Starting capital (must be >= 0)
            strategy_name: Name for this backtest
            
        Returns:
            BacktestResult with all metrics and snapshots
            
        Edge cases:
            - Zero capital: Portfolio starts with $0, cannot buy anything
            - Negative capital: Raises ValueError
            - Invalid strategy function: Raises TypeError
            - Empty assets: Already handled in __init__
        """
        if not callable(strategy_func):
            raise TypeError(f"strategy_func must be callable, got {type(strategy_func)}")
        if initial_capital < 0:
            raise ValueError(f"Initial capital cannot be negative: {initial_capital}")
            
        portfolio = Portfolio(initial_capital)
        snapshots = []
        
        for date_index in range(self.num_periods):
            # Execute strategy
            strategy_func(self, portfolio, date_index)
            
            # Record snapshot
            snapshot = portfolio.get_snapshot(self.dates[date_index], date_index)
            snapshots.append(snapshot)
        
        # Calculate metrics
        final_value = portfolio.get_value(self.num_periods - 1)
        total_return = (final_value - initial_capital) / initial_capital if initial_capital > 0 else 0
        
        # Annual return (assuming daily data)
        days = self.num_periods - 1
        years = days / 252.0
        annual_return = (total_return + 1) ** (1 / years) - 1 if years > 0 and total_return > -1 else 0
        
        # Max drawdown
        max_drawdown = self._calculate_max_drawdown(snapshots)
        
        # Sharpe ratio (assuming risk-free rate = 0)
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
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(snapshots)):
            prev_value = snapshots[i - 1].total_value
            curr_value = snapshots[i].total_value
            daily_return = (curr_value - prev_value) / prev_value
            returns.append(daily_return)
        
        if not returns:
            return 0
        
        # Calculate volatility
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0
        
        # Annualize (252 trading days)
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
        
        # Header
        output += f"{'Strategy':<20} {'Initial':<12} {'Final':<12} {'Return %':<12} {'Annual %':<12} {'Max DD %':<12} {'Sharpe':<10}\n"
        output += "-" * 100 + "\n"
        
        # Results
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
            "max_drawdown": lambda r: -r.max_drawdown,  # Negative because lower is better
        }
        
        if metric not in metric_map:
            raise ValueError(f"Unknown metric: {metric}")
        
        return max(self.results, key=metric_map[metric])
