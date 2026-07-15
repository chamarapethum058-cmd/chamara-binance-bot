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
                
                # Run strategy analysis
                try:
                    result = await AIService.calculate_programmatic_silver_bullet(
                        tracker["req_payload"],
                        current_price=(new_price or tracker["req_payload"].get("current_price") or 0.0)
                    )
                    tracker["last_result"] = result
                    
                    # Count confluences out of 12 steps
                    steps_confirmed = 0
                    for i in range(1, 13):
                        # Count sb_step_x_time_window_ok, etc.
                        key_name = f"sb_step_{i}_time_window_ok"
                        if i == 2:
                            key_name = "sb_step_2_liquidity_sweep_ok"
                        elif i == 3:
                            key_name = "sb_step_3_displacement_mss_ok"
                        elif i == 4:
                            key_name = "sb_step_4_fvg_bpr_ok"
                        elif i == 5:
                            key_name = "sb_step_5_entry_exec_ok"
                        elif i == 6:
                            key_name = "sb_step_6_risk_mgmt_ok"
                        elif i == 7:
                            key_name = "sb_step_7_london_asian_sweep_ok"
                        elif i == 8:
                            key_name = "sb_step_8_htf_pd_mitigation_ok"
                        elif i == 9:
                            key_name = "sb_step_9_ltf_choch_ok"
                        elif i == 10:
                            key_name = "sb_step_10_fvg_limit_ok"
                        elif i == 11:
                            key_name = "sb_step_11_equilibrium_ok"
                        elif i == 12:
                            key_name = "sb_step_12_po3_align_ok"
                            
                        if result.get(key_name):
                            steps_confirmed += 1
                    
                    tracker["confluences"] = steps_confirmed
                    tracker["confidence"] = result.get("confidence", 0)
                    tracker["current_price"] = new_price or tracker["req_payload"].get("current_price") or 0.0
                    
                    # Determine status
                    if steps_confirmed >= 10:
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
