import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from app.market import get_candles
from app.services import AIService
from app.database import SessionLocal
from app.models import PreferenceModel

logger = logging.getLogger(__name__)

# Global dictionary to hold active tracker states
# Keys: Symbol (e.g. "SOLUSDT")
active_trackers: Dict[str, Dict[str, Any]] = {}
tracker_task: Optional[asyncio.Task] = None
smc_tracker_task: Optional[asyncio.Task] = None

def standardize_symbol(symbol: str) -> str:
    sym = symbol.upper().strip()
    if sym.endswith(".P"):
        sym = sym[:-2]
    if not sym.endswith("USDT") and not sym.endswith("USD") and sym not in ["BTC", "ETH", "SOL", "XAUUSD"]:
        sym = f"{sym}USDT"
    elif sym in ["BTC", "ETH", "SOL"]:
        sym = f"{sym}USDT"
    return sym

def get_current_price(symbol: str) -> Optional[float]:
    try:
        sym = standardize_symbol(symbol)
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
                    sym = standardize_symbol(symbol)
                    
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
                        if not tracker.get("notified"):
                            from app.telegram_service import TelegramService
                            direction_str = "Buy Limit" if "Buy" in entry_area else "Sell Limit"
                            msg = (
                                f"🔔 <b>FALCON ALERT: ENTRY CONFIRMED!</b>\n\n"
                                f"🪙 <b>Symbol:</b> {symbol}\n"
                                f"📈 <b>Strategy:</b> ICT Silver Bullet\n"
                                f"🎯 <b>Setup:</b> {entry_area}\n"
                                f"🔥 <b>Confidence:</b> {tracker.get('confidence', 0)}% ({steps_confirmed}/16 steps met)\n"
                                f"📊 <b>Current Price:</b> ${tracker['current_price']:.4f}\n\n"
                                f"📍 <i>Please check your trading terminal. Setup will invalid if price breaches Stop Loss.</i>\n\n"
                                f"<b>සිංහල පරිවර්තනය (Sinhala):</b>\n"
                                f"ට්‍රේඩ් එන්ට්‍රිය තහවුරු කර ඇත! {symbol} සඳහා {direction_str} ඕඩරය සූදානම්. කරුණාකර ඔබගේ ටර්මිනලය පරීක්ෂා කරන්න."
                            )
                            asyncio.create_task(TelegramService.send_message(msg))
                            tracker["notified"] = True
                    else:
                        tracker["status"] = "RUNNING"
                        tracker["notified"] = False
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

async def run_smc_tracker_loop():
    logger.info("SMC Background Tracker Loop Started.")
    notified_symbols = {}
    
    while True:
        try:
            # Read monitored coins from DB preferences
            db = SessionLocal()
            try:
                pref = db.query(PreferenceModel).filter(PreferenceModel.key == "smc_monitored_coins").first()
                monitored_coins = json.loads(pref.value) if pref and pref.value else []
            except Exception as pe:
                logger.error(f"Error reading smc_monitored_coins preference: {pe}")
                monitored_coins = []
            finally:
                db.close()
                
            # Clean up notified_symbols keys that are no longer in the active watchlist
            active_keys = {f"{coin.get('symbol')}_{coin.get('timeframe')}" for coin in monitored_coins if coin.get("symbol")}
            for key in list(notified_symbols.keys()):
                if key not in active_keys:
                    del notified_symbols[key]

            if monitored_coins:
                for coin in monitored_coins:
                    symbol = coin.get("symbol")
                    if not symbol:
                        continue
                        
                    # Fetch latest price
                    price = get_current_price(symbol)
                    if price is None:
                        continue
                        
                    # Fetch daily open, pdh, pdl to pass into payload
                    try:
                        sym = standardize_symbol(symbol)
                            
                        daily_candles = get_candles(sym, "1d", limit=2)
                        daily_open = daily_candles[-1]["open"] if daily_candles else price
                        pdh = daily_candles[-2]["high"] if len(daily_candles) >= 2 else price * 1.01
                        pdl = daily_candles[-2]["low"] if len(daily_candles) >= 2 else price * 0.99
                    except Exception as dex:
                        logger.error(f"Error fetching daily levels for {symbol} in SMC tracker: {dex}")
                        daily_open = price
                        pdh = price * 1.01
                        pdl = price * 0.99
                        
                    # Calculate confluences programmatically using local logic (Rule 11)
                    payload = {
                        "symbol": symbol,
                        "timeframe": coin.get("timeframe", "1m"),
                        "current_price": price,
                        "pdh": pdh,
                        "pdl": pdl,
                        "daily_open": daily_open
                    }
                    
                    try:
                        result = await AIService.calculate_programmatic_smc(payload, local_only=True)
                        confidence = result.get("confidence", 0)
                        is_valid = result.get("is_valid", False)
                        entry_price = result.get("entry_price_area") or ""
                        stop_loss = result.get("stop_loss_level")
                        take_profit = result.get("tp2_target")
                        
                        # Determine if we should notify
                        key = f"{symbol}_{coin.get('timeframe')}"
                        if is_valid and confidence >= 80:
                            if not notified_symbols.get(key):
                                from app.telegram_service import TelegramService
                                direction_str = "Buy Limit" if "Buy" in entry_price else "Sell Limit"
                                msg = (
                                    f"🔔 <b>SMC ALERT: ENTRY CONFIRMED!</b>\n\n"
                                    f"🪙 <b>Symbol:</b> {symbol} ({coin.get('timeframe')})\n"
                                    f"📈 <b>Strategy:</b> SMC Method\n"
                                    f"🎯 <b>Setup:</b> {entry_price}\n"
                                    f"🔥 <b>Confidence:</b> {confidence}% (Confirmed)\n"
                                    f"🛡️ <b>Stop Loss:</b> ${stop_loss}\n"
                                    f"💰 <b>Take Profit:</b> ${take_profit}\n"
                                    f"📊 <b>Current Price:</b> ${price:.4f}\n\n"
                                    f"📍 <i>Please check your trading terminal. Setup will invalid if price breaches Stop Loss.</i>\n\n"
                                    f"<b>සිංහල පරිවර්තනය (Sinhala):</b>\n"
                                    f"SMC එන්ට්‍රිය තහවුරු කර ඇත! {symbol} සඳහා {direction_str} ඕඩරය සූදානම්. කරුණාකර ඔබගේ ටර්මිනලය පරීක්ෂා කරන්න."
                                )
                                asyncio.create_task(TelegramService.send_message(msg))
                                notified_symbols[key] = True
                        else:
                            # Do not reset notification state to False immediately
                            # This prevents duplicate notification spam when price oscillates
                            pass
                            
                    except Exception as ae:
                        logger.error(f"Error calculating programmatic SMC in tracker for {symbol}: {ae}")
                        
        except Exception as e:
            logger.error(f"Error in SMC tracker loop: {e}")
            
        await asyncio.sleep(10)

def start_smc_tracker():
    global smc_tracker_task
    if smc_tracker_task is None or smc_tracker_task.done():
        smc_tracker_task = asyncio.create_task(run_smc_tracker_loop())

# TCS Watchlist Tracker Loop
tcs_tracker_task = None
tcs_notified_symbols = {}

async def run_tcs_tracker_loop():
    logger.info("Starting background TCS Watchlist Tracker loop...")
    from app.telegram_service import TelegramService
    
    while True:
        db = SessionLocal()
        try:
            from app.models import PreferenceModel
            pref = db.query(PreferenceModel).filter(PreferenceModel.key == "tcs_monitored_coins").first()
            if not pref or not pref.value:
                db.close()
                await asyncio.sleep(10)
                continue
                
            watchlist = json.loads(pref.value)
            if not watchlist:
                db.close()
                await asyncio.sleep(10)
                continue
                
            for coin in watchlist:
                symbol = coin.get("symbol", "").upper()
                if not symbol:
                    continue
                    
                # Fetch live price
                try:
                    price = await fetch_ticker_price(symbol)
                except Exception:
                    price = None
                    
                if price is None:
                    continue
                    
                entry_price_str = coin.get("entryPrice")
                if not entry_price_str:
                    continue
                    
                try:
                    entry_price = float(entry_price_str)
                except ValueError:
                    continue
                    
                htf_trend = coin.get("htfTrend", "BULLISH")
                sl = coin.get("stopLoss", "0")
                tp = coin.get("takeProfit", "0")
                confidence = coin.get("confidence", 100)
                
                # Check for crossing/touching of manual limit entry price
                key = f"tcs_{symbol}_{entry_price}"
                should_notify = False
                if htf_trend == "BULLISH":
                    if price <= entry_price:
                        should_notify = True
                else:
                    if price >= entry_price:
                        should_notify = True
                        
                if should_notify and not tcs_notified_symbols.get(key):
                    msg = (
                        f"🔔 <b>TCS ALERT: LIMIT ENTRY TOUCHED!</b>\n\n"
                        f"🪙 <b>Symbol:</b> {symbol}\n"
                        f"📈 <b>Strategy:</b> TCS IDM Model\n"
                        f"🎯 <b>Target Entry:</b> ${entry_price:.4f}\n"
                        f"📊 <b>Current Price:</b> ${price:.4f}\n"
                        f"🛡️ <b>Stop Loss:</b> ${sl}\n"
                        f"💰 <b>Take Profit:</b> ${tp}\n"
                        f"🔥 <b>Confidence:</b> {confidence}%\n\n"
                        f"📍 <i>Price has touched your manual limit execution level. Please check your exchange/terminal.</i>\n\n"
                        f"<b>සිංහල පරිවර්තනය (Sinhala):</b>\n"
                        f"TCS එන්ට්‍රිය ක්‍රියාත්මක විය! {symbol} සඳහා ඇතුළත් කළ Limit මිල (${entry_price:.4f}) සජීවී මිල සමඟ සමපාත වී ඇත."
                    )
                    asyncio.create_task(TelegramService.send_message(msg))
                    tcs_notified_symbols[key] = True
                    
        except Exception as e:
            logger.error(f"Error in TCS tracker loop: {e}")
        finally:
            db.close()
            
        await asyncio.sleep(10)

def start_tcs_tracker():
    global tcs_tracker_task
    if tcs_tracker_task is None or tcs_tracker_task.done():
        tcs_tracker_task = asyncio.create_task(run_tcs_tracker_loop())

