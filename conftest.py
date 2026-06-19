"""
Pytest configuration and shared fixtures for PortfolioLab tests.
"""

import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.assets import Asset, AssetType, PriceData
from src.backtester import Backtester, Portfolio


@pytest.fixture
def sample_prices():
    """Sample price data for testing."""
    return {
        "AAPL": [100, 105, 110, 115, 120],
        "GOOGL": [100, 95, 90, 85, 80],
        "MSFT": [100, 102, 104, 106, 108],
    }


@pytest.fixture
def sample_assets(sample_prices):
    """Create sample assets from price data."""
    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
    
    assets = {}
    for symbol, prices in sample_prices.items():
        assets[symbol] = Asset(
            symbol=symbol,
            asset_type=AssetType.STOCK,
            price_data=PriceData(dates=dates, prices=prices)
        )
    return assets


@pytest.fixture
def uptrend_prices():
    """Uptrend price series for momentum testing."""
    return [100 + i for i in range(60)]


@pytest.fixture
def downtrend_prices():
    """Downtrend price series for momentum testing."""
    return [160 - i for i in range(60)]


@pytest.fixture
def flat_prices():
    """Flat price series for edge case testing."""
    return [100] * 30


@pytest.fixture
def volatile_prices():
    """Volatile price series for Bollinger testing."""
    import random
    random.seed(42)
    prices = [100]
    for _ in range(49):
        change = random.uniform(-5, 5)
        prices.append(prices[-1] + change)
    return prices


@pytest.fixture
def backtester(sample_assets):
    """Create a backtester with sample assets."""
    return Backtester(sample_assets)


@pytest.fixture
def portfolio():
    """Create a portfolio with initial capital."""
    return Portfolio(initial_capital=100000)
