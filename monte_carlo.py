"""
Monte Carlo Simulation for Portfolio Risk Analysis
Generates 1000+ portfolio scenarios to assess probability of returns and risk metrics
"""

import numpy as np
from typing import Dict, List, Tuple


class PortfolioMonteCarloSimulator:
    """
    Monte Carlo simulator for portfolio analysis.
    Generates future portfolio scenarios based on historical returns.
    """
    
    def __init__(self, returns_dict: Dict[str, List[float]], weights: Dict[str, float]):
        """
        Initialize Monte Carlo simulator.
        
        Args:
            returns_dict: Dictionary of {symbol: list_of_daily_returns}
            weights: Portfolio weights {symbol: weight}
        """
        self.returns_dict = returns_dict
        self.weights = weights
        self.symbols = list(weights.keys())
        
        # Calculate historical statistics
        self.means = {}
        self.stds = {}
        self.correlation_matrix = None
        
        self._calculate_statistics()
    
    def _calculate_statistics(self):
        """Calculate mean returns and standard deviations"""
        returns_array = []
        
        for symbol in self.symbols:
            returns = np.array(self.returns_dict.get(symbol, []))
            if len(returns) > 0:
                self.means[symbol] = np.mean(returns)
                self.stds[symbol] = np.std(returns)
                returns_array.append(returns)
        
        # Calculate correlation matrix
        if returns_array:
            returns_array = np.column_stack(returns_array)
            self.correlation_matrix = np.corrcoef(returns_array.T)
    
    def simulate(self, num_simulations: int = 1000, 
                 days: int = 252, 
                 initial_value: float = 100000.0) -> Dict:
        """
        Run Monte Carlo simulations.
        
        Args:
            num_simulations: Number of portfolio paths to simulate (default 1000)
            days: Number of days to project forward (default 252 = 1 year)
            initial_value: Starting portfolio value
        
        Returns:
            Dictionary with simulation results and statistics
        """
        simulations = []
        final_values = []
        
        for _ in range(num_simulations):
            portfolio_value = initial_value
            daily_values = [portfolio_value]
            
            for day in range(days):
                # Generate correlated random returns
                random_returns = self._generate_correlated_returns()
                
                # Calculate portfolio return
                portfolio_return = 0
                for symbol, weight in self.weights.items():
                    idx = self.symbols.index(symbol)
                    portfolio_return += weight * random_returns[idx]
                
                # Update portfolio value
                portfolio_value *= (1 + portfolio_return)
                daily_values.append(portfolio_value)
            
            simulations.append(daily_values)
            final_values.append(portfolio_value)
        
        # Convert to numpy for easier analysis
        simulations = np.array(simulations)
        final_values = np.array(final_values)
        
        return self._compile_results(simulations, final_values, initial_value, days)
    
    def _generate_correlated_returns(self) -> np.ndarray:
        """Generate correlated random returns using correlation matrix"""
        if self.correlation_matrix is None:
            # No correlation data, generate independent returns
            returns = []
            for symbol in self.symbols:
                mean = self.means.get(symbol, 0)
                std = self.stds.get(symbol, 0.01)
                returns.append(np.random.normal(mean, std))
            return np.array(returns)
        
        # Generate correlated returns
        num_assets = len(self.symbols)
        independent_normals = np.random.standard_normal(num_assets)
        
        # Cholesky decomposition for correlation
        try:
            cholesky = np.linalg.cholesky(self.correlation_matrix)
            correlated_normals = cholesky @ independent_normals
        except:
            correlated_normals = independent_normals
        
        # Convert to returns using historical means and stds
        returns = []
        for i, symbol in enumerate(self.symbols):
            mean = self.means.get(symbol, 0)
            std = self.stds.get(symbol, 0.01)
            returns.append(mean + std * correlated_normals[i])
        
        return np.array(returns)
    
    def _compile_results(self, simulations: np.ndarray, 
                        final_values: np.ndarray,
                        initial_value: float,
                        days: int) -> Dict:
        """Compile simulation results into statistics"""
        
        # Calculate percentiles
        percentiles = np.percentile(final_values, [1, 5, 10, 25, 50, 75, 90, 95, 99])
        
        # Calculate return percentages
        returns_pct = ((final_values - initial_value) / initial_value) * 100
        
        # Calculate daily portfolio values for percentile paths
        percentile_paths = {}
        for pct in [5, 25, 50, 75, 95]:
            idx = int((pct / 100) * len(final_values))
            percentile_paths[f'p{pct}'] = simulations[np.argsort(final_values)[idx]].tolist()
        
        return {
            'success': True,
            'num_simulations': len(final_values),
            'num_days': days,
            'final_values': final_values.tolist(),
            'returns_pct': returns_pct.tolist(),
            'statistics': {
                'mean_return_pct': float(np.mean(returns_pct)),
                'median_return_pct': float(np.median(returns_pct)),
                'std_return_pct': float(np.std(returns_pct)),
                'mean_final_value': float(np.mean(final_values)),
                'median_final_value': float(np.median(final_values)),
                'min_final_value': float(np.min(final_values)),
                'max_final_value': float(np.max(final_values)),
                'var_95': float(percentiles[1]),  # 5th percentile
                'var_99': float(percentiles[0]),  # 1st percentile
                'cvar_95': float(np.mean(final_values[final_values <= percentiles[1]])),
                'probability_positive_return': float(np.sum(returns_pct > 0) / len(returns_pct) * 100),
            },
            'percentile_final_values': {
                '1st': float(percentiles[0]),
                '5th': float(percentiles[1]),
                '10th': float(percentiles[2]),
                '25th': float(percentiles[3]),
                '50th': float(percentiles[4]),
                '75th': float(percentiles[5]),
                '90th': float(percentiles[6]),
                '95th': float(percentiles[7]),
                '99th': float(percentiles[8]),
            },
            'percentile_paths': percentile_paths,
            'message': f'Ran {len(final_values)} simulations for {days} days'
        }


def calculate_rolling_metrics(snapshots: List[Dict], window: int = 20) -> Dict:
    """
    Calculate rolling Sharpe ratio, returns, and volatility.
    
    Args:
        snapshots: List of {date, value} snapshots
        window: Rolling window size (default 20 days)
    
    Returns:
        Dictionary with rolling metrics
    """
    values = np.array([s['value'] for s in snapshots])
    dates = [s['date'] for s in snapshots]
    
    if len(values) < window:
        return {
            'rolling_sharpe': [],
            'rolling_returns': [],
            'rolling_volatility': [],
            'dates': dates
        }
    
    # Calculate daily returns
    daily_returns = np.diff(values) / values[:-1]
    
    rolling_sharpe = []
    rolling_returns = []
    rolling_volatility = []
    
    for i in range(len(daily_returns) - window + 1):
        window_returns = daily_returns[i:i+window]
        
        # Annualized return
        annual_return = (np.mean(window_returns) * 252) * 100
        rolling_returns.append(annual_return)
        
        # Annualized volatility
        annual_vol = (np.std(window_returns) * np.sqrt(252)) * 100
        rolling_volatility.append(annual_vol)
        
        # Sharpe ratio (assuming 0 risk-free rate)
        if annual_vol > 0:
            sharpe = annual_return / annual_vol
        else:
            sharpe = 0
        rolling_sharpe.append(sharpe)
    
    return {
        'rolling_sharpe': rolling_sharpe,
        'rolling_returns': rolling_returns,
        'rolling_volatility': rolling_volatility,
        'rolling_dates': dates[window-1:],
        'window': window
    }
