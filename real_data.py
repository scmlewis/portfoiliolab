"""Real data integration with Yahoo Finance with caching and parallel fetching."""

import yfinance as yf
from datetime import datetime, timedelta
from src.assets import Asset, AssetType, PriceData
from typing import Dict, Optional, Tuple
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from cachetools import TTLCache

# Cache: max 200 entries, 10-minute TTL
_cache = TTLCache(maxsize=200, ttl=600)
_cache_lock = threading.Lock()


def _cache_key(symbols: Tuple[str, ...], start_date: str, end_date: str) -> str:
    return f"{ '|'.join(symbols) }|{start_date}|{end_date}"


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
        """Fetch stock data from Yahoo Finance with retry logic."""
        cache_key = f"single|{symbol}|{start_date}|{end_date}"
        with _cache_lock:
            if cache_key in _cache:
                return _cache[cache_key]

        for attempt in range(max_retries):
            try:
                if verbose:
                    print(f"Fetching {symbol} data ({start_date} to {end_date})... attempt {attempt+1}/{max_retries}")

                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date)

                if data.empty:
                    if verbose:
                        print(f"  No data found for {symbol}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    continue

                dates = [date.strftime("%Y-%m-%d") for date in data.index]
                prices = data['Close'].tolist()

                if len(dates) < 10:
                    if verbose:
                        print(f"  Only {len(dates)} days for {symbol}, retrying...")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    continue

                asset = Asset(
                    symbol=symbol,
                    asset_type=asset_type,
                    price_data=PriceData(dates=dates, prices=prices)
                )

                with _cache_lock:
                    _cache[cache_key] = asset

                if verbose:
                    print(f"  {symbol}: {len(dates)} days loaded")
                return asset

            except Exception as e:
                if verbose:
                    print(f"  Error fetching {symbol} (attempt {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)

        if verbose:
            print(f"  Failed to fetch {symbol} after {max_retries} attempts")
        return None

    @staticmethod
    def fetch_multiple_assets(
        symbols: Dict[str, AssetType],
        start_date: str,
        end_date: str
    ) -> Dict[str, Asset]:
        """Fetch multiple assets in parallel from Yahoo Finance."""
        cache_key = _cache_key(tuple(sorted(symbols.keys())), start_date, end_date)
        with _cache_lock:
            if cache_key in _cache:
                return _cache[cache_key]

        assets = {}
        symbol_list = list(symbols.items())

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(
                    YahooFinanceDataProvider.fetch_stock_data,
                    symbol, start_date, end_date, asset_type, 3, False
                ): symbol
                for symbol, asset_type in symbol_list
            }
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    asset = future.result()
                    if asset:
                        assets[symbol] = asset
                except Exception as e:
                    print(f"  Error in parallel fetch for {symbol}: {e}")

        if assets:
            with _cache_lock:
                _cache[cache_key] = assets

        return assets

    @staticmethod
    def get_default_portfolio() -> Dict[str, AssetType]:
        """Get a default portfolio of well-known stocks."""
        return {
            'AAPL': AssetType.STOCK,
            'MSFT': AssetType.STOCK,
            'GOOGL': AssetType.STOCK,
            'AMZN': AssetType.STOCK,
            'TSLA': AssetType.STOCK,
            'BND': AssetType.BOND,
            'BTC-USD': AssetType.CRYPTO,
        }

    @staticmethod
    def get_last_n_days(days: int = 252) -> Tuple[str, str]:
        """Get start and end dates for the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def load_real_data(symbols: Dict[str, AssetType], num_days: int = 252) -> Dict[str, Asset]:
    """Load real market data for given symbols (cached)."""
    start_date, end_date = YahooFinanceDataProvider.get_last_n_days(num_days)
    return YahooFinanceDataProvider.fetch_multiple_assets(symbols, start_date, end_date)


def load_default_portfolio(num_days: int = 252) -> Dict[str, Asset]:
    """Load default portfolio with real data."""
    symbols = YahooFinanceDataProvider.get_default_portfolio()
    return load_real_data(symbols, num_days)
