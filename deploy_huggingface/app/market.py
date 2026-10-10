import requests
import datetime
import time
from typing import List, Dict, Any, Optional

# Binance API base URL (public, no auth needed for price data)
BASE_URL = "https://api.binance.com/api/v3"

# Persistent connection pool session for ultra-fast Keep-Alive requests
_session = requests.Session()
_session.headers.update({"User-Agent": "FalconSMC/2.0 (HighVelocityEngine)"})

# In-memory TTL Cache to prevent redundant Binance network requests
# Key: f"{symbol}_{interval}_{limit}", Value: (timestamp, candle_list)
_candles_cache: Dict[str, tuple[float, List[Dict[str, Any]]]] = {}

# Smart TTL Caching map (Phase 1 Market Data):
# 3m -> 10s, 5m -> 15s, 15m -> 30s, 1h -> 60s, 1d -> 180s
_cache_ttl: Dict[str, float] = {
    "1d": 180.0,
    "1w": 180.0,
    "1h": 60.0,
    "4h": 60.0,
    "15m": 30.0,
    "5m": 15.0,
    "3m": 10.0,
    "1m": 10.0,
}

def _timestamp_to_ny(dt: datetime.datetime) -> datetime.datetime:
    """Convert a UTC datetime to New York time (handling DST)."""
    try:
        import pytz
        utc = pytz.utc
        ny = pytz.timezone('America/New_York')
        return dt.replace(tzinfo=utc).astimezone(ny)
    except Exception:
        return dt

def get_candles(symbol: str, interval: str, limit: int = 500) -> List[Dict[str, Any]]:
    """Fetch recent candle data from Binance (Spot or Futures) with TTL caching & connection pooling.

    Args:
        symbol: Trading pair symbol, e.g., "BTCUSDT".
        interval: Binance interval string ("1m", "3m", "5m", "15m", "1h", "1d").
        limit: Number of candles to retrieve.
    Returns:
        List of candle dicts with keys: open, high, low, close, volume, close_time.
    """
    now = time.time()
    cache_key = f"{symbol.upper()}_{interval}_{limit}"

    # Smart TTL Caching (Phase 1 Market Data):
    # 1d candles -> cached for 180s (3 mins)
    # 1h candles -> cached for 60s
    # 15m candles -> cached for 30s
    # 5m candles -> cached for 15s
    # 3m candles -> cached for 10s
    if interval in ["1d", "1w"]:
        ttl = 180.0
    elif interval in ["1h", "4h"]:
        ttl = 60.0
    elif interval == "15m":
        ttl = 30.0
    elif interval == "5m":
        ttl = 15.0
    elif interval == "3m":
        ttl = 10.0
    else:
        ttl = 10.0

    if cache_key in _candles_cache:
        cached_ts, cached_val = _candles_cache[cache_key]
        if (now - cached_ts) < ttl and cached_val:
            return cached_val

    # Normalize symbol for Binance APIs (TradingView Binance Futures Perpetual Lock)
    binance_symbol = symbol.upper().strip()
    if binance_symbol.endswith(".P"):
        binance_symbol = binance_symbol[:-2]

    # Candidate symbol variants for USDT-M Futures (e.g. 1000PEPEUSDT, 1000SHIBUSDT vs PEPEUSDT)
    futures_candidates = [binance_symbol]
    if not binance_symbol.startswith("1000"):
        futures_candidates.append(f"1000{binance_symbol}")

    # Prioritize Binance USDT-M Futures first so price/klines strictly match TradingView .P perpetual contracts
    apis = [
        {"name": "Binance Futures (USDT-M Perpetual)", "url": "https://fapi.binance.com/fapi/v1/klines", "is_futures": True},
        {"name": "Binance Vision (CloudFront Edge)", "url": "https://data-api.binance.vision/api/v3/klines", "is_futures": False},
        {"name": "Binance Spot", "url": "https://api.binance.com/api/v3/klines", "is_futures": False},
        {"name": "MEXC Spot", "url": "https://api.mexc.com/api/v3/klines", "is_futures": False},
        {"name": "Binance US", "url": "https://api.binance.us/api/v3/klines", "is_futures": False}
    ]
    
    data = None
    last_error = None

    for api in apis:
        url = api["url"]
        is_fut = api.get("is_futures", False)
        target_syms = futures_candidates if is_fut else [binance_symbol]
        
        for cur_sym in target_syms:
            try:
                if limit <= 1000:
                    params = {"symbol": cur_sym, "interval": interval, "limit": limit}
                    resp = _session.get(url, params=params, timeout=3.5)
                    resp.raise_for_status()
                    data = resp.json()
                else:
                    params = {"symbol": cur_sym, "interval": interval, "limit": 1000}
                    resp = _session.get(url, params=params, timeout=3.5)
                    resp.raise_for_status()
                    data1 = resp.json()
                    
                    if data1:
                        first_ms = data1[0][0]
                        remaining = limit - len(data1)
                        params = {"symbol": cur_sym, "interval": interval, "limit": remaining, "endTime": first_ms - 1}
                        resp = _session.get(url, params=params, timeout=3.5)
                        resp.raise_for_status()
                        data2 = resp.json()
                        data = data2 + data1
                    else:
                        data = []
                
                # Successfully fetched data!
                if isinstance(data, list) and len(data) >= min(limit, 1):
                    break
                else:
                    data = None
            except Exception as e:
                last_error = e
                data = None
        if data is not None:
            break

    # Fallback to Bybit if Binance APIs failed (crucial for US Cloud like Hugging Face Spaces)
    if data is None:
        try:
            itv_map = {'1m':'1', '3m':'3', '5m':'5', '15m':'15', '1h':'60', '4h':'240', '1d':'D', '1w':'W'}
            b_itv = itv_map.get(interval, '3')
            for category in ['linear', 'spot']:
                try:
                    bybit_url = "https://api.bybit.com/v5/market/kline"
                    b_params = {"category": category, "symbol": binance_symbol, "interval": b_itv, "limit": min(limit, 200)}
                    b_resp = _session.get(bybit_url, params=b_params, timeout=3.0)
                    if b_resp.status_code == 200:
                        b_json = b_resp.json()
                        if b_json.get("retCode") == 0 and b_json.get("result", {}).get("list"):
                            raw_list = b_json["result"]["list"][::-1] # Ascending chronological
                            candles = []
                            for c in raw_list:
                                try:
                                    candles.append({
                                        "open": float(c[1]),
                                        "high": float(c[2]),
                                        "low": float(c[3]),
                                        "close": float(c[4]),
                                        "volume": float(c[5]),
                                        "close_time": datetime.datetime.fromtimestamp(int(c[0])/1000, datetime.timezone.utc),
                                    })
                                except Exception:
                                    continue
                            # Fix: allow single-candle queries when limit=1 requested
                            if len(candles) >= min(limit, 1):
                                _candles_cache[cache_key] = (now, candles)
                                return candles
                except Exception:
                    continue
        except Exception:
            pass

    # If Binance and Bybit failed, fall back to Yahoo Finance
    if data is None:
        try:
            yf_symbol = symbol.upper().strip()
            if yf_symbol.endswith(".P"):
                yf_symbol = yf_symbol[:-2]
            if yf_symbol.endswith("USDT"):
                yf_symbol = yf_symbol[:-4]
            elif yf_symbol.endswith("USD"):
                yf_symbol = yf_symbol[:-3]
            yf_symbol = f"{yf_symbol}-USD"
            
            yf_range = "5d" if interval in ["1m", "3m", "5m"] else "60d"
            yf_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_symbol}?interval={interval}&range={yf_range}"
            res = _session.get(yf_url, timeout=4.0)
            res.raise_for_status()
            yf_data = res.json().get("chart", {}).get("result", [])
            if yf_data:
                timestamps = yf_data[0].get("timestamp", [])
                # Reject stale delayed data for scalping intervals:
                if timestamps and interval in ["1m", "3m", "5m", "15m"]:
                    last_ts = timestamps[-1]
                    if (now - last_ts) > 180:  # Older than 3 minutes = stale delayed data!
                        raise ValueError(f"Yahoo Finance candle data stale by {(now - last_ts)/60:.1f}m for {yf_symbol}")
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
                parsed_candles = candles[-limit:]
                _candles_cache[cache_key] = (now, parsed_candles)
                return parsed_candles
        except Exception as ye:
            # Fall back to returning stale cache if available
            if cache_key in _candles_cache:
                return _candles_cache[cache_key][1]
            return []

    if not data or not isinstance(data, list):
        if cache_key in _candles_cache:
            return _candles_cache[cache_key][1]
        return []

    # Parse standard Binance output
    candles = []
    for c in data:
        try:
            candles.append({
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5]),
                "close_time": datetime.datetime.utcfromtimestamp(c[6] / 1000),
            })
        except (IndexError, ValueError):
            continue

    _candles_cache[cache_key] = (now, candles)
    return candles

def is_erl(price: float, erp_threshold: float = 0.01) -> bool:
    """External Range Liquidity."""
    return price % erp_threshold < erp_threshold / 2

def is_irl(price: float, irp_threshold: float = 0.01) -> bool:
    """Internal Range Liquidity."""
    return not is_erl(price, erp_threshold=irp_threshold)
