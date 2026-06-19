"""Sample data generator for backtesting."""
import random
from datetime import datetime, timedelta
from typing import Dict, List
from src.assets import Asset, AssetType, PriceData


def generate_price_series(
    start_price: float,
    num_periods: int,
    daily_return_mean: float = 0.0003,
    daily_return_std: float = 0.015,
    seed: int = None
) -> List[float]:
    """
    Generate a price series using geometric Brownian motion.
    
    Args:
        start_price: Starting price
        num_periods: Number of periods
        daily_return_mean: Mean daily return
        daily_return_std: Standard deviation of daily return
        seed: Random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)
    
    prices = [start_price]
    for _ in range(num_periods - 1):
        daily_return = random.gauss(daily_return_mean, daily_return_std)
        new_price = prices[-1] * (1 + daily_return)
        prices.append(max(new_price, 0.01))  # Ensure positive price
    
    return prices


def create_sample_assets(start_date: str = "2023-01-01", num_days: int = 252) -> Dict[str, Asset]:
    """Create sample assets with simulated price data."""
    # Generate dates
    dates = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    for i in range(num_days):
        # Skip weekends
        while current_date.weekday() >= 5:
            current_date += timedelta(days=1)
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    assets = {}
    
    # Stock - Tech company (higher volatility)
    assets["TECH"] = Asset(
        symbol="TECH",
        asset_type=AssetType.STOCK,
        price_data=PriceData(
            dates=dates,
            prices=generate_price_series(100, len(dates), 0.0005, 0.02, seed=42)
        )
    )
    
    # Stock - Dividend company (lower volatility)
    assets["DIVIDEND"] = Asset(
        symbol="DIVIDEND",
        asset_type=AssetType.STOCK,
        price_data=PriceData(
            dates=dates,
            prices=generate_price_series(100, len(dates), 0.0002, 0.012, seed=43)
        )
    )
    
    # Bond - Conservative investment
    assets["BOND"] = Asset(
        symbol="BOND",
        asset_type=AssetType.BOND,
        price_data=PriceData(
            dates=dates,
            prices=generate_price_series(100, len(dates), 0.00005, 0.005, seed=44)
        )
    )
    
    # Crypto - Highly volatile
    assets["CRYPTO"] = Asset(
        symbol="CRYPTO",
        asset_type=AssetType.CRYPTO,
        price_data=PriceData(
            dates=dates,
            prices=generate_price_series(100, len(dates), 0.0008, 0.035, seed=45)
        )
    )
    
    # Commodity - Moderate volatility
    assets["COMMODITY"] = Asset(
        symbol="COMMODITY",
        asset_type=AssetType.COMMODITY,
        price_data=PriceData(
            dates=dates,
            prices=generate_price_series(100, len(dates), 0.0001, 0.018, seed=46)
        )
    )
    
    return assets
