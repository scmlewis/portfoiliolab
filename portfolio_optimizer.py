"""Portfolio optimization using Modern Portfolio Theory."""

import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')


@dataclass
class OptimizationResult:
    """Result of portfolio optimization."""
    weights: Dict[str, float]  # Optimal weights
    expected_return: float      # Expected annual return
    volatility: float           # Annual volatility
    sharpe_ratio: float         # Sharpe ratio
    min_variance: bool          # Is this min variance portfolio?


class PortfolioOptimizer:
    """Optimize portfolio using Modern Portfolio Theory (Markowitz)."""
    
    def __init__(self, returns: Dict[str, List[float]], risk_free_rate: float = 0.02):
        """
        Initialize optimizer.
        
        Args:
            returns: Dict of {symbol: [daily_returns]}
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.returns = returns
        self.risk_free_rate = risk_free_rate
        self.symbols = list(returns.keys())
        self.n_assets = len(self.symbols)
        
        # Calculate statistics
        self._calculate_statistics()
    
    def _calculate_statistics(self):
        """Calculate mean returns and covariance matrix."""
        # Convert to numpy array
        returns_array = np.array([self.returns[s] for s in self.symbols]).T
        
        # Daily returns to annual (252 trading days)
        self.mean_returns = np.mean(returns_array, axis=0) * 252
        self.cov_matrix = np.cov(returns_array.T) * 252
        
    def _portfolio_return(self, weights: np.ndarray) -> float:
        """Calculate portfolio return."""
        return np.sum(self.mean_returns * weights)
    
    def _portfolio_volatility(self, weights: np.ndarray) -> float:
        """Calculate portfolio volatility."""
        return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
    
    def _portfolio_sharpe(self, weights: np.ndarray) -> float:
        """Calculate portfolio Sharpe ratio (negative for minimization)."""
        ret = self._portfolio_return(weights)
        vol = self._portfolio_volatility(weights)
        
        if vol == 0:
            return 0
        
        return -(ret - self.risk_free_rate) / vol
    
    def _portfolio_variance(self, weights: np.ndarray) -> float:
        """Calculate portfolio variance."""
        return np.dot(weights.T, np.dot(self.cov_matrix, weights))
    
    def optimize_max_sharpe(self) -> OptimizationResult:
        """Find portfolio with maximum Sharpe ratio."""
        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        
        # Bounds: weights between 0 and 1 (no short selling)
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Initial guess: equal weight
        init_guess = np.array([1.0 / self.n_assets] * self.n_assets)
        
        # Optimize
        result = minimize(
            self._portfolio_sharpe,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            # Fallback to equal weight
            weights = init_guess
        else:
            weights = result.x
        
        # Normalize to ensure sum = 1
        weights = weights / np.sum(weights)
        
        # Calculate metrics
        ret = self._portfolio_return(weights)
        vol = self._portfolio_volatility(weights)
        sharpe = (ret - self.risk_free_rate) / vol if vol > 0 else 0
        
        return OptimizationResult(
            weights=dict(zip(self.symbols, weights)),
            expected_return=ret,
            volatility=vol,
            sharpe_ratio=sharpe,
            min_variance=False
        )
    
    def optimize_min_variance(self) -> OptimizationResult:
        """Find minimum variance portfolio."""
        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        
        # Bounds: weights between 0 and 1
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Initial guess: equal weight
        init_guess = np.array([1.0 / self.n_assets] * self.n_assets)
        
        # Optimize
        result = minimize(
            self._portfolio_variance,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            weights = init_guess
        else:
            weights = result.x
        
        # Normalize
        weights = weights / np.sum(weights)
        
        # Calculate metrics
        ret = self._portfolio_return(weights)
        vol = self._portfolio_volatility(weights)
        sharpe = (ret - self.risk_free_rate) / vol if vol > 0 else 0
        
        return OptimizationResult(
            weights=dict(zip(self.symbols, weights)),
            expected_return=ret,
            volatility=vol,
            sharpe_ratio=sharpe,
            min_variance=True
        )
    
    def efficient_frontier(
        self,
        num_points: int = 50,
        target_return: Optional[float] = None
    ) -> List[Tuple[float, float, Dict[str, float]]]:
        """
        Calculate efficient frontier.
        
        Args:
            num_points: Number of points on frontier
            target_return: Optional specific target return
            
        Returns:
            List of (volatility, return, weights) tuples
        """
        if target_return is not None:
            # Find portfolio with specific return
            return [self._target_return_portfolio(target_return)]
        
        # Generate frontier
        min_var = self.optimize_min_variance()
        max_sharpe = self.optimize_max_sharpe()
        
        # Return range from min variance to max return
        min_ret = min_var.expected_return
        max_ret = max_sharpe.expected_return * 1.2  # 20% above max Sharpe return
        
        target_returns = np.linspace(min_ret, max_ret, num_points)
        frontier = []
        
        for target in target_returns:
            try:
                vol, ret, weights = self._target_return_portfolio(target)
                frontier.append((vol, ret, weights))
            except:
                continue
        
        return frontier
    
    def _target_return_portfolio(
        self,
        target_return: float
    ) -> Tuple[float, float, Dict[str, float]]:
        """Find minimum variance portfolio for target return."""
        # Constraints: weights sum to 1, portfolio return = target
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: self._portfolio_return(w) - target_return}
        ]
        
        # Bounds
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Initial guess
        init_guess = np.array([1.0 / self.n_assets] * self.n_assets)
        
        # Optimize
        result = minimize(
            self._portfolio_variance,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            weights = init_guess
        else:
            weights = result.x
        
        weights = weights / np.sum(weights)
        ret = self._portfolio_return(weights)
        vol = self._portfolio_volatility(weights)
        
        return vol, ret, dict(zip(self.symbols, weights))
    
    def get_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Get correlation matrix between assets."""
        # Normalize covariance to correlation
        stds = np.sqrt(np.diag(self.cov_matrix))
        corr = self.cov_matrix / np.outer(stds, stds)
        
        result = {}
        for i, sym1 in enumerate(self.symbols):
            result[sym1] = {}
            for j, sym2 in enumerate(self.symbols):
                result[sym1][sym2] = float(corr[i, j])
        
        return result
    
    def get_asset_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get annual return and volatility for each asset."""
        stds = np.sqrt(np.diag(self.cov_matrix))
        
        result = {}
        for i, sym in enumerate(self.symbols):
            result[sym] = {
                'return': float(self.mean_returns[i]),
                'volatility': float(stds[i])
            }
        
        return result


def calculate_returns_from_prices(prices: List[float]) -> List[float]:
    """Calculate daily returns from prices."""
    prices = np.array(prices)
    returns = np.diff(prices) / prices[:-1]
    return returns.tolist()


def optimize_portfolio(
    assets_data: Dict[str, List[float]],
    optimization_type: str = 'sharpe'
) -> OptimizationResult:
    """
    Convenience function to optimize portfolio.
    
    Args:
        assets_data: Dict of {symbol: [prices]}
        optimization_type: 'sharpe' or 'minvar'
        
    Returns:
        OptimizationResult
    """
    # Calculate returns from prices
    returns = {}
    for symbol, prices in assets_data.items():
        returns[symbol] = calculate_returns_from_prices(prices)
    
    # Optimize
    optimizer = PortfolioOptimizer(returns)
    
    if optimization_type == 'minvar':
        return optimizer.optimize_min_variance()
    else:
        return optimizer.optimize_max_sharpe()
