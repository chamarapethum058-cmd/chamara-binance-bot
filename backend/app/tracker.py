import asyncio
import logging
from typing import Dict, Any, List, Optional
from app.market import get_candles
from app.services import AIService

logger = logging.getLogger(__name__)

# Global dictionary to hold active tracker states
# Keys: Symbol (e.g. "SOLUSDT")
active_trackers: Dict[str, Dict[str, Any]] = {}
tracker_task: Optional[asyncio.Task] = None

def get_current_price(symbol: str) -> Optional[float]:
    try:
        # Standardize symbol representation (e.g. SOL -> SOLUSDT)
        sym = symbol.upper()
        if not sym.endswith("USDT") and not sym.endswith("USD") and sym not in ["BTC", "ETH", "SOL", "XAUUSD"]:
            sym = f"{sym}USDT"
        elif sym in ["BTC", "ETH", "SOL"]:
            sym = f"{sym}USDT"
            
        candles = get_candles(sym, "1m", limit=1)
        if candles:
            return candles[-1]["close"]
    except Exception as e:
        logger.error(f"Error fetching current price for {symbol}: {e}")
    return None

async def run_tracker_loop():
    while True:
        try:
            # Create a copy of keys to avoid concurrent modification issues
            symbols = list(active_trackers.keys())
            if not symbols:
                # If no active trackers, we can stop the loop
                break
                
            for symbol in symbols:
                tracker = active_trackers.get(symbol)
                if not tracker:
                    continue
                
                # Fetch latest price
                new_price = get_current_price(symbol)
                if new_price is not None:
                    tracker["req_payload"]["current_price"] = new_price
                
                # Fetch daily candles to extract asset-specific levels
                try:
                    sym = symbol.upper()
                    if not sym.endswith("USDT") and not sym.endswith("USD") and sym not in ["BTC", "ETH", "SOL", "XAUUSD"]:
                        sym = f"{sym}USDT"
                    elif sym in ["BTC", "ETH", "SOL"]:
                        sym = f"{sym}USDT"
                    
                    daily_candles = get_candles(sym, "1d", limit=5)
                    if len(daily_candles) >= 2:
                        tracker["req_payload"]["daily_open"] = daily_candles[-1]["open"]
                        tracker["req_payload"]["pdh"] = daily_candles[-2]["high"]
                        tracker["req_payload"]["pdl"] = daily_candles[-2]["low"]
                        tracker["req_payload"]["dealing_range_high"] = max(c["high"] for c in daily_candles)
                        tracker["req_payload"]["dealing_range_low"] = min(c["low"] for c in daily_candles)
                except Exception as dex:
                    logger.error(f"Error fetching dynamic daily levels for {symbol}: {dex}")

                # Run strategy analysis
                try:
                    result = await AIService.calculate_programmatic_silver_bullet(
                        tracker["req_payload"],
                        current_price=(new_price or tracker["req_payload"].get("current_price") or 0.0)
                    )
                    tracker["last_result"] = result
                    
                    # Count confluences out of 16 steps dynamically
                    steps_confirmed = 0
                    for i in range(1, 17):
                        step_ok = False
                        for k, v in result.items():
                            if k.startswith(f"sb_step_{i}_") and k.endswith("_ok") and v is True:
                                step_ok = True
                                break
                        if step_ok:
                            steps_confirmed += 1
                    
                    tracker["confluences"] = steps_confirmed
                    tracker["confidence"] = result.get("confidence", 0)
                    tracker["current_price"] = new_price or tracker["req_payload"].get("current_price") or 0.0
                    
                    # Determine status: only ENTRY READY if a valid entry is active and not locked
                    entry_area = result.get("entry_price_area") or ""
                    is_entry_active = (
                        "Buy Limit" in entry_area or 
                        "Sell Limit" in entry_area or 
                        "Est. Buy Limit" in entry_area or 
                        "Est. Sell Limit" in entry_area
                    ) and not ("No Entry" in entry_area)
                    
                    is_locked = result.get("counter_trend_locked", False)
                    
                    if is_entry_active and not is_locked and steps_confirmed >= 10:
                        tracker["status"] = "ENTRY READY"
                    else:
                        tracker["status"] = "RUNNING"
                except Exception as ex:
                    logger.error(f"Error analyzing silver bullet in tracker loop for {symbol}: {ex}")
            
        except Exception as e:
            logger.error(f"Error in tracker loop: {e}")
        
        await asyncio.sleep(10)

def start_tracking(symbol: str, req_payload: Dict[str, Any], api_key: Optional[str] = None):
    # Standardize symbol upper
    sym = symbol.upper()
    active_trackers[sym] = {
        "symbol": sym,
        "req_payload": req_payload,
        "status": "RUNNING",
        "confluences": 0,
        "current_price": req_payload.get("current_price") or 0.0,
        "last_result": {},
        "api_key": api_key
    }
    
    global tracker_task
    if tracker_task is None or tracker_task.done():
        tracker_task = asyncio.create_task(run_tracker_loop())

def stop_tracking(symbol: str):
    sym = symbol.upper()
    if sym in active_trackers:
        del active_trackers[sym]

def get_trackers_status() -> List[Dict[str, Any]]:
    res = []
    for sym, tracker in active_trackers.items():
        res.append({
            "symbol": sym,
            "status": tracker["status"],
            "confluences": tracker["confluences"],
            "confidence": tracker.get("confidence", 0),
            "current_price": tracker["current_price"],
            "last_result": tracker["last_result"]
        })
    return res
