import requests
import datetime
from typing import List, Dict, Any

# Binance API base URL (public, no auth needed for price data)
BASE_URL = "https://api.binance.com/api/v3"

def _timestamp_to_ny(dt: datetime.datetime) -> datetime.datetime:
    """Convert a UTC datetime to New York time (handling DST)."""
    import pytz
    utc = pytz.utc
    ny = pytz.timezone('America/New_York')
    return dt.replace(tzinfo=utc).astimezone(ny)

def get_candles(symbol: str, interval: str, limit: int = 500) -> List[Dict[str, Any]]:
    """Fetch recent candle data from Binance.

    Args:
        symbol: Trading pair symbol, e.g., "BTCUSDT".
        interval: Binance interval string ("1m", "5m", "1h", etc.).
        limit: Number of candles to retrieve (max 1000).
    Returns:
        List of candle dicts with keys: open, high, low, close, volume, close_time.
    """
    url = f"{BASE_URL}/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    candles = []
    for c in data:
        candles.append({
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5]),
            "close_time": datetime.datetime.utcfromtimestamp(c[6] / 1000),
        })
    return candles

def is_erl(price: float, erp_threshold: float = 0.01) -> bool:
    """Placeholder: determine if price is in External Range Liquidity.
    In a real system this would compare against recent swing extremes.
    """
    return price % erp_threshold < erp_threshold / 2

def is_irl(price: float, irp_threshold: float = 0.01) -> bool:
    """Placeholder: determine if price is in Internal Range Liquidity.
    """
    return not is_erl(price, erp_threshold=irp_threshold)
