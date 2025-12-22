"""Asset types for the backtester."""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List


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
