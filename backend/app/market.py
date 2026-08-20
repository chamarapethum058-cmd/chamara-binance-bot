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
    """Fetch recent candle data from Binance (Spot or Futures).

    Args:
        symbol: Trading pair symbol, e.g., "BTCUSDT".
        interval: Binance interval string ("1m", "5m", "1h", etc.).
        limit: Number of candles to retrieve (can exceed 1000 via pagination).
    Returns:
        List of candle dicts with keys: open, high, low, close, volume, close_time.
    """
    # Normalize symbol for Binance APIs
    binance_symbol = symbol.upper().strip()
    if binance_symbol.endswith(".P"):
        binance_symbol = binance_symbol[:-2]

    # Try Binance Spot first, then fallback to Binance Futures, then to Yahoo Finance
    apis = [
        {"name": "Binance Spot", "url": "https://api.binance.com/api/v3/klines"},
        {"name": "Binance Futures", "url": "https://fapi.binance.com/fapi/v1/klines"}
    ]
    
    data = None
    last_error = None

    for api in apis:
        url = api["url"]
        try:
            if limit <= 1000:
                params = {"symbol": binance_symbol, "interval": interval, "limit": limit}
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
            else:
                # Fetch in chunks using pagination to support Rule 40 (1500-candle lookback)
                params = {"symbol": binance_symbol, "interval": interval, "limit": 1000}
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                data1 = resp.json()
                
                if data1:
                    first_ms = data1[0][0]
                    remaining = limit - len(data1)
                    params = {"symbol": binance_symbol, "interval": interval, "limit": remaining, "endTime": first_ms - 1}
                    resp = requests.get(url, params=params, timeout=10)
                    resp.raise_for_status()
                    data2 = resp.json()
                    data = data2 + data1
                else:
                    data = []
            
            # Successfully fetched data from this API!
            break
        except requests.exceptions.RequestException as e:
            last_error = e
            print(f"{api['name']} API failed ({e}). Trying next fallback...")

    # If both Binance APIs failed, fall back to Yahoo Finance
    if data is None:
        print(f"All Binance APIs failed (last error: {last_error}). Falling back to Yahoo Finance for {symbol} ({interval}).")
        yf_symbol = symbol.upper().strip()
        if yf_symbol.endswith(".P"):
            yf_symbol = yf_symbol[:-2]
        if yf_symbol.endswith("USDT"):
            yf_symbol = yf_symbol[:-4]
        elif yf_symbol.endswith("USD"):
            yf_symbol = yf_symbol[:-3]
        yf_symbol = f"{yf_symbol}-USD"
        
        try:
            yf_range = "5d" if interval == "1m" else "60d"
            yf_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_symbol}?interval={interval}&range={yf_range}"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(yf_url, headers=headers, timeout=10)
            res.raise_for_status()
            yf_data = res.json().get("chart", {}).get("result", [])
            if not yf_data:
                return []
                
            timestamps = yf_data[0].get("timestamp", [])
            quote = yf_data[0].get("indicators", {}).get("quote", [{}])[0]
            opens = quote.get("open", [])
            highs = quote.get("high", [])
            lows = quote.get("low", [])
            closes = quote.get("close", [])
            volumes = quote.get("volume", [])
            
            candles = []
            for i in range(len(timestamps)):
                if opens[i] is None:
                    continue
                candles.append({
                    "open": float(opens[i]),
                    "high": float(highs[i]),
                    "low": float(lows[i]),
                    "close": float(closes[i]),
                    "volume": float(volumes[i]),
                    "close_time": datetime.datetime.utcfromtimestamp(timestamps[i]),
                })
            return candles[-limit:]
        except Exception as e:
            print(f"Yahoo Finance fallback also failed: {e}")
            raise e

    # Parse standard Binance output
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
