"""Real data integration with Yahoo Finance."""

import yfinance as yf
from datetime import datetime, timedelta
from src.assets import Asset, AssetType, PriceData
from typing import Dict, Optional
import time


class YahooFinanceDataProvider:
    """Provides real market data from Yahoo Finance."""
    
    @staticmethod
    def fetch_stock_data(
        symbol: str,
        start_date: str,
        end_date: str,
        asset_type: AssetType = AssetType.STOCK,
        max_retries: int = 3,
        verbose: bool = True
    ) -> Optional[Asset]:
        """
        Fetch stock data from Yahoo Finance with retry logic.
        
        Args:
            symbol: Ticker symbol (e.g., 'AAPL', 'MSFT')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            asset_type: Type of asset
            max_retries: Number of retry attempts
            verbose: Print progress messages
            
        Returns:
            Asset object or None if failed
        """
        for attempt in range(max_retries):
            try:
                if verbose:
                    print(f"Fetching {symbol} data from {start_date} to {end_date}... (attempt {attempt+1}/{max_retries})")
                
                # Download data with timeout
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date)
                
                if data.empty:
                    if verbose:
                        print(f"  ⚠ No data found for {symbol}")
                    time.sleep(1)  # Wait before retry
                    continue
                
                # Extract dates and closing prices
                dates = [date.strftime("%Y-%m-%d") for date in data.index]
                prices = data['Close'].tolist()
                
                # Validate data
                if len(dates) < 10:
                    if verbose:
                        print(f"  ⚠ Only {len(dates)} days of data for {symbol}, retrying...")
                    time.sleep(1)
                    continue
                
                # Create asset
                asset = Asset(
                    symbol=symbol,
                    asset_type=asset_type,
                    price_data=PriceData(dates=dates, prices=prices)
                )
                
                if verbose:
                    print(f"  ✓ {symbol}: {len(dates)} days of data loaded")
                return asset
                
            except Exception as e:
                if verbose:
                    print(f"  ✗ Error fetching {symbol} (attempt {attempt+1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                continue
        
        if verbose:
            print(f"  ✗ Failed to fetch {symbol} after {max_retries} attempts")
        return None
    
    @staticmethod
    def fetch_multiple_assets(
        symbols: Dict[str, AssetType],
        start_date: str,
        end_date: str
    ) -> Dict[str, Asset]:
        """
        Fetch multiple assets from Yahoo Finance.
        
        Args:
            symbols: Dict of {symbol: AssetType}
            start_date: Start date
            end_date: End date
            
        Returns:
            Dict of {symbol: Asset}
        """
        assets = {}
        
        for symbol, asset_type in symbols.items():
            asset = YahooFinanceDataProvider.fetch_stock_data(
                symbol, start_date, end_date, asset_type
            )
            if asset:
                assets[symbol] = asset
        
        return assets
    
    @staticmethod
    def get_default_portfolio() -> Dict[str, AssetType]:
        """Get a default portfolio of well-known stocks."""
        return {
            'AAPL': AssetType.STOCK,      # Apple
            'MSFT': AssetType.STOCK,      # Microsoft
            'GOOGL': AssetType.STOCK,     # Google
            'AMZN': AssetType.STOCK,      # Amazon
            'TSLA': AssetType.STOCK,      # Tesla
            'BND': AssetType.BOND,        # Bond ETF
            'BTC-USD': AssetType.CRYPTO,  # Bitcoin
        }
    
    @staticmethod
    def get_last_n_days(days: int = 252) -> tuple:
        """
        Get start and end dates for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Tuple of (start_date, end_date) as strings
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


# Convenience functions
def load_real_data(symbols: Dict[str, AssetType], num_days: int = 252) -> Dict[str, Asset]:
    """
    Load real market data for given symbols.
    
    Args:
        symbols: Dict of {symbol: AssetType}
        num_days: Number of days of historical data
        
    Returns:
        Dict of {symbol: Asset}
    """
    start_date, end_date = YahooFinanceDataProvider.get_last_n_days(num_days)
    return YahooFinanceDataProvider.fetch_multiple_assets(symbols, start_date, end_date)


def load_default_portfolio(num_days: int = 252) -> Dict[str, Asset]:
    """
    Load default portfolio with real data.
    
    Args:
        num_days: Number of days of historical data
        
    Returns:
        Dict of {symbol: Asset}
    """
    symbols = YahooFinanceDataProvider.get_default_portfolio()
    return load_real_data(symbols, num_days)
