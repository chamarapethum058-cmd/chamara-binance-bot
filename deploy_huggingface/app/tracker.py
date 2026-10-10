import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional
from app.market import get_candles
from app.services import AIService
from app.database import SessionLocal
from app.models import PreferenceModel
from app.precision_scalp import get_dynamic_precision

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
    """Fetch ultra-fresh real-time live ticker price (0-delay) using multi-exchange edge mirrors."""
    try:
        import urllib.request
        sym = standardize_symbol(symbol)
        clean = sym.replace(".P", "").upper().strip()
        gate_pair = clean.replace("USDT", "_USDT") if "USDT" in clean else f"{clean}_USDT"

        # Multi-exchange real-time live price mirrors (Binance Futures USDT-M Perpetual Top Priority):
        endpoints = [
            ("Binance Futures", f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={clean}", "binance"),
            ("Binance Futures 1000x", f"https://fapi.binance.com/fapi/v1/ticker/price?symbol=1000{clean}", "binance"),
            ("Binance Vision (CloudFront Edge)", f"https://data-api.binance.vision/api/v3/ticker/price?symbol={clean}", "binance"),
            ("Binance Spot", f"https://api.binance.com/api/v3/ticker/price?symbol={clean}", "binance"),
            ("Bybit Linear", f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={clean}", "bybit"),
            ("MEXC Spot", f"https://api.mexc.com/api/v3/ticker/price?symbol={clean}", "mexc"),
            ("Bybit Spot", f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={clean}", "bybit"),
            ("Gate.io", f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={gate_pair}", "gateio")
        ]

        for name, url, fmt in endpoints:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "FalconSMC/2.0"})
                with urllib.request.urlopen(req, timeout=1.8) as resp:
                    data = json.loads(resp.read().decode())
                    if fmt in ["binance", "mexc"]:
                        p = data.get("price")
                        if p and float(p) > 0:
                            return float(p)
                    elif fmt == "bybit":
                        if isinstance(data, dict) and "result" in data and "list" in data["result"]:
                            lst = data["result"]["list"]
                            if lst and "lastPrice" in lst[0] and float(lst[0]["lastPrice"]) > 0:
                                return float(lst[0]["lastPrice"])
                    elif fmt == "gateio":
                        if isinstance(data, list) and len(data) > 0 and data[0].get("last"):
                            val = float(data[0]["last"])
                            if val > 0:
                                return val
            except Exception:
                continue

        # If fast ticker endpoints fail, fallback to 1m candle from verified live sources
        candles = get_candles(sym, "1m", limit=1)
        if candles:
            return float(candles[-1]["close"])
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
                        session_c = get_candles(sym, "5m", limit=48)
                        if session_c:
                            tracker["req_payload"]["dealing_range_high"] = max(c["high"] for c in session_c)
                            tracker["req_payload"]["dealing_range_low"] = min(c["low"] for c in session_c)
                        else:
                            tracker["req_payload"]["dealing_range_high"] = daily_candles[-1]["high"]
                            tracker["req_payload"]["dealing_range_low"] = daily_candles[-1]["low"]
                except Exception as dex:
                    logger.error(f"Error fetching dynamic daily levels for {symbol}: {dex}")

                # Run strategy analysis
                try:
                    result = await AIService.calculate_programmatic_silver_bullet(
                        tracker["req_payload"],
                        current_price=(new_price or tracker["req_payload"].get("current_price") or 0.0),
                        local_only=True
                    )
                    tracker["last_result"] = result
                    
                    # Count confluences dynamically
                    steps_confirmed = 0
                    for i in range(1, 17):
                        if i == 7:
                            continue
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
                    is_entry_active = ("Buy" in entry_area or "Sell" in entry_area) and not ("No Entry" in entry_area or "Awaiting" in entry_area)
                    
                    is_locked = result.get("counter_trend_locked", False)
                    is_valid = result.get("is_valid", False)
                    conf = result.get("confidence", 0)
                    
                    if is_entry_active and not is_locked and is_valid and conf >= 80 and steps_confirmed >= 10:
                        tracker["status"] = "ENTRY READY"
                        if not tracker.get("notified"):
                            from app.telegram_service import TelegramService
                            from app.chart_service import ChartService
                            
                            is_long = "BUY" in entry_area.upper()
                            dir_mode = "LONG" if is_long else "SHORT"
                            import re
                            dollar_match = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)", str(entry_area))
                            if dollar_match:
                                calc_entry = float(dollar_match.group(1))
                            else:
                                matches = re.findall(r"\d+(?:\.\d+)?", str(entry_area))
                                calc_entry = float(matches[0]) if matches else tracker['current_price']
                            prec = get_dynamic_precision(calc_entry)
                            calc_sl = float(result.get("stop_loss_level")) if result.get("stop_loss_level") else (calc_entry * 0.9970 if is_long else calc_entry * 1.0030)
                            risk = abs(calc_entry - calc_sl)
                            if calc_entry > 0 and (risk / calc_entry) < 0.0020:
                                calc_sl = round(calc_entry * (0.9970 if is_long else 1.0030), prec)
                                risk = abs(calc_entry - calc_sl)
                            calc_tp1 = float(result.get("tp1_target") or result.get("breakeven_trigger")) if (result.get("tp1_target") or result.get("breakeven_trigger")) else (calc_entry + 1.50 * risk if is_long else calc_entry - 1.50 * risk)
                            calc_tp2 = float(result.get("tp2_target") or result.get("liquidity_target")) if (result.get("tp2_target") or result.get("liquidity_target")) else (calc_entry + 2.50 * risk if is_long else calc_entry - 2.50 * risk)
                            
                            caption, reply_markup = TelegramService.build_trade_alert(
                                symbol=symbol,
                                direction=dir_mode,
                                entry_price=calc_entry,
                                stop_loss=calc_sl,
                                tp1=calc_tp1,
                                tp2=calc_tp2,
                                confidence=conf,
                                trend_1h=result.get("trend_1h")
                            )
                            
                            tf_loop = tracker["req_payload"].get("timeframe", "5m")
                            chart_candles = get_candles(sym, tf_loop, limit=60)
                            chart_bytes = ChartService.generate_smc_chart(
                                symbol=symbol,
                                timeframe=tf_loop,
                                klines=chart_candles or [],
                                entry=calc_entry,
                                sl=calc_sl,
                                tp1=calc_tp1,
                                tp2=calc_tp2,
                                direction=dir_mode
                            )
                            
                            if chart_bytes:
                                asyncio.create_task(TelegramService.send_photo(chart_bytes, caption, symbol=symbol, reply_markup=reply_markup))
                            else:
                                asyncio.create_task(TelegramService.send_message(caption, symbol=symbol, reply_markup=reply_markup))
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

DEFAULT_SMC_MONITORED_COINS = [
    {"symbol": "BTCUSDT.P", "timeframe": "3m"},
    {"symbol": "SOLUSDT.P", "timeframe": "3m"},
    {"symbol": "ETHUSDT.P", "timeframe": "3m"},
    {"symbol": "BNBUSDT.P", "timeframe": "3m"},
    {"symbol": "XRPUSDT.P", "timeframe": "3m"},
    {"symbol": "DOGEUSDT.P", "timeframe": "3m"},
    {"symbol": "SUIUSDT.P", "timeframe": "3m"},
    {"symbol": "APTUSDT.P", "timeframe": "3m"},
    {"symbol": "AVAXUSDT.P", "timeframe": "3m"},
    {"symbol": "LINKUSDT.P", "timeframe": "3m"},
    {"symbol": "ARBUSDT.P", "timeframe": "3m"},
    {"symbol": "OPUSDT.P", "timeframe": "3m"},
    {"symbol": "NEARUSDT.P", "timeframe": "3m"},
    {"symbol": "INJUSDT.P", "timeframe": "3m"},
    {"symbol": "UNIUSDT.P", "timeframe": "3m"},
    {"symbol": "ONDOUSDT.P", "timeframe": "3m"},
    {"symbol": "ENAUSDT.P", "timeframe": "3m"},
    {"symbol": "TAOUSDT.P", "timeframe": "3m"},
    {"symbol": "ATOMUSDT.P", "timeframe": "3m"},
    {"symbol": "XLMUSDT.P", "timeframe": "3m"},
    {"symbol": "POLUSDT.P", "timeframe": "3m"},
    {"symbol": "ADAUSDT.P", "timeframe": "3m"},
    {"symbol": "TRXUSDT.P", "timeframe": "3m"},
    {"symbol": "BCHUSDT.P", "timeframe": "3m"},
    {"symbol": "LTCUSDT.P", "timeframe": "3m"},
    {"symbol": "DOTUSDT.P", "timeframe": "3m"},
    {"symbol": "SEIUSDT.P", "timeframe": "3m"},
    {"symbol": "FTMUSDT.P", "timeframe": "3m"},
    {"symbol": "TIAUSDT.P", "timeframe": "3m"},
    {"symbol": "STRKUSDT.P", "timeframe": "3m"},
    {"symbol": "KASUSDT.P", "timeframe": "3m"},
    {"symbol": "ALGOUSDT.P", "timeframe": "3m"},
    {"symbol": "ICPUSDT.P", "timeframe": "3m"},
    {"symbol": "HBARUSDT.P", "timeframe": "3m"},
    {"symbol": "EGLDUSDT.P", "timeframe": "3m"},
    {"symbol": "FLOWUSDT.P", "timeframe": "3m"},
    {"symbol": "KAVAUSDT.P", "timeframe": "3m"},
    {"symbol": "ZECUSDT.P", "timeframe": "3m"},
    {"symbol": "ETCUSDT.P", "timeframe": "3m"},
    {"symbol": "NEOUSDT.P", "timeframe": "3m"},
    {"symbol": "CFXUSDT.P", "timeframe": "3m"},
    {"symbol": "AAVEUSDT.P", "timeframe": "3m"},
    {"symbol": "MKRUSDT.P", "timeframe": "3m"},
    {"symbol": "CRVUSDT.P", "timeframe": "3m"},
    {"symbol": "LDOUSDT.P", "timeframe": "3m"},
    {"symbol": "PENDLEUSDT.P", "timeframe": "3m"},
    {"symbol": "SNXUSDT.P", "timeframe": "3m"},
    {"symbol": "COMPUSDT.P", "timeframe": "3m"},
    {"symbol": "SUSHIUSDT.P", "timeframe": "3m"},
    {"symbol": "1INCHUSDT.P", "timeframe": "3m"},
    {"symbol": "RUNEUSDT.P", "timeframe": "3m"},
    {"symbol": "JUPUSDT.P", "timeframe": "3m"},
    {"symbol": "DYDXUSDT.P", "timeframe": "3m"},
    {"symbol": "CAKEUSDT.P", "timeframe": "3m"},
    {"symbol": "RAYUSDT.P", "timeframe": "3m"},
    {"symbol": "FETUSDT.P", "timeframe": "3m"},
    {"symbol": "RENDERUSDT.P", "timeframe": "3m"},
    {"symbol": "WLDUSDT.P", "timeframe": "3m"},
    {"symbol": "GRTUSDT.P", "timeframe": "3m"},
    {"symbol": "FILUSDT.P", "timeframe": "3m"},
    {"symbol": "ARUSDT.P", "timeframe": "3m"},
    {"symbol": "THETAUSDT.P", "timeframe": "3m"},
    {"symbol": "AKTUSDT.P", "timeframe": "3m"},
    {"symbol": "IOUSDT.P", "timeframe": "3m"},
    {"symbol": "ARKMUSDT.P", "timeframe": "3m"},
    {"symbol": "IMXUSDT.P", "timeframe": "3m"},
    {"symbol": "GALAUSDT.P", "timeframe": "3m"},
    {"symbol": "SANDUSDT.P", "timeframe": "3m"},
    {"symbol": "MANAUSDT.P", "timeframe": "3m"},
    {"symbol": "AXSUSDT.P", "timeframe": "3m"},
    {"symbol": "BEAMXUSDT.P", "timeframe": "3m"},
    {"symbol": "NOTUSDT.P", "timeframe": "3m"},
    {"symbol": "PIXELUSDT.P", "timeframe": "3m"},
    {"symbol": "YGGUSDT.P", "timeframe": "3m"},
    {"symbol": "ENJUSDT.P", "timeframe": "3m"},
    {"symbol": "1000SHIBUSDT.P", "timeframe": "3m"},
    {"symbol": "1000PEPEUSDT.P", "timeframe": "3m"},
    {"symbol": "WIFUSDT.P", "timeframe": "3m"},
    {"symbol": "1000BONKUSDT.P", "timeframe": "3m"},
    {"symbol": "1000FLOKIUSDT.P", "timeframe": "3m"},
    {"symbol": "BOMEUSDT.P", "timeframe": "3m"},
    {"symbol": "POPCATUSDT.P", "timeframe": "3m"},
    {"symbol": "MEWUSDT.P", "timeframe": "3m"},
    {"symbol": "MEMEUSDT.P", "timeframe": "3m"},
    {"symbol": "NEIROUSDT.P", "timeframe": "3m"},
    {"symbol": "1000SATSUSDT.P", "timeframe": "3m"},
    {"symbol": "PYTHUSDT.P", "timeframe": "3m"},
    {"symbol": "WUSDT.P", "timeframe": "3m"},
    {"symbol": "AXLUSDT.P", "timeframe": "3m"},
    {"symbol": "QNTUSDT.P", "timeframe": "3m"},
    {"symbol": "CHZUSDT.P", "timeframe": "3m"},
    {"symbol": "ENSUSDT.P", "timeframe": "3m"},
    {"symbol": "STORJUSDT.P", "timeframe": "3m"},
    {"symbol": "ANKRUSDT.P", "timeframe": "3m"},
    {"symbol": "JASMYUSDT.P", "timeframe": "3m"},
    {"symbol": "CKBUSDT.P", "timeframe": "3m"},
    {"symbol": "ORDIUSDT.P", "timeframe": "3m"},
    {"symbol": "MOVRUSDT.P", "timeframe": "3m"},
    {"symbol": "VETUSDT.P", "timeframe": "3m"},
    {"symbol": "IOTAUSDT.P", "timeframe": "3m"},
    {"symbol": "ROSEUSDT.P", "timeframe": "3m"},
    {"symbol": "DEEPUSDT.P", "timeframe": "3m"},
    {"symbol": "STXUSDT.P", "timeframe": "3m"},
    {"symbol": "GMXUSDT.P", "timeframe": "3m"},
    {"symbol": "PEOPLEUSDT.P", "timeframe": "3m"},
    {"symbol": "LPTUSDT.P", "timeframe": "3m"},
    {"symbol": "BLURUSDT.P", "timeframe": "3m"},
    {"symbol": "ETHFIUSDT.P", "timeframe": "3m"},
    {"symbol": "MANTAUSDT.P", "timeframe": "3m"},
    {"symbol": "METISUSDT.P", "timeframe": "3m"},
    {"symbol": "ZROUSDT.P", "timeframe": "3m"},
    {"symbol": "SSVUSDT.P", "timeframe": "3m"},
    {"symbol": "COTIUSDT.P", "timeframe": "3m"},
    {"symbol": "IDUSDT.P", "timeframe": "3m"},
    {"symbol": "HIGHUSDT.P", "timeframe": "3m"},
    {"symbol": "DYMUSDT.P", "timeframe": "3m"},
    {"symbol": "ALTUSDT.P", "timeframe": "3m"},
    {"symbol": "BBUSDT.P", "timeframe": "3m"},
    {"symbol": "REZUSDT.P", "timeframe": "3m"},
    {"symbol": "PORTALUSDT.P", "timeframe": "3m"},
    {"symbol": "XAIUSDT.P", "timeframe": "3m"},
    {"symbol": "MAGICUSDT.P", "timeframe": "3m"},
    {"symbol": "CELOUSDT.P", "timeframe": "3m"},
    {"symbol": "ONEUSDT.P", "timeframe": "3m"},
    {"symbol": "RVNUSDT.P", "timeframe": "3m"},
    {"symbol": "DUSKUSDT.P", "timeframe": "3m"},
    {"symbol": "AGLDUSDT.P", "timeframe": "3m"},
    {"symbol": "HOOKUSDT.P", "timeframe": "3m"},
    {"symbol": "EDUUSDT.P", "timeframe": "3m"},
    {"symbol": "LISTAUSDT.P", "timeframe": "3m"},
    {"symbol": "SKLUSDT.P", "timeframe": "3m"},
    {"symbol": "CTSIUSDT.P", "timeframe": "3m"},
]

_smc_notified_timestamps: dict[str, float] = {}
# Active trade position memory (Rule 81: Directional Protection & Anti-Opposing Alert Mandate)
_active_trade_positions: dict[str, dict] = {}

_db_lock = asyncio.Lock()

async def update_single_coin_in_db(symbol: str, timeframe: str, update_dict: dict):
    """Update a single coin's analysis results immediately in SQLite preferences with async lock."""
    async with _db_lock:
        db = SessionLocal()
        try:
            pref = db.query(PreferenceModel).filter(PreferenceModel.key == "smc_monitored_coins").first()
            if pref and pref.value:
                coins = json.loads(pref.value)
                k_target = f"{symbol}_{timeframe}"
                changed = False
                for c in coins:
                    k = f"{c.get('symbol')}_{c.get('timeframe', '3m')}"
                    if k == k_target:
                        c.update(update_dict)
                        changed = True
                        break
                if changed:
                    pref.value = json.dumps(coins)
                    db.commit()
        except Exception as e:
            logger.error(f"Error updating single coin {symbol} in DB: {e}")
        finally:
            db.close()

async def analyze_single_coin_task(coin: dict, semaphore: asyncio.Semaphore):
    """Analyze a single coin and immediately commit results to DB."""
    async with semaphore:
        symbol = coin.get("symbol")
        if not symbol:
            return
            
        sym = standardize_symbol(symbol)
        timeframe = coin.get("timeframe", "3m")
        now_ts = time.time()
        
        try:
            # Fetch latest price non-blocking
            price = await asyncio.to_thread(get_current_price, sym)
            if price is None:
                return
                
            # Rule 81 Position Lifecycle Check: Check if active trade resolved (SL or TP hit or 2h timeout)
            active_pos = _active_trade_positions.get(symbol)
            active_pos_dir = active_pos.get("direction") if active_pos else None
            if active_pos:
                pos_dir = active_pos.get("direction")
                pos_sl = float(active_pos.get("stop_loss", 0.0))
                pos_tp2 = float(active_pos.get("tp2", 0.0))
                alert_age = now_ts - active_pos.get("alert_time", now_ts)
                
                # Step 7 Rapid Scalp Exit Engine: 30-Minute Max Hold / Flat Time-Stop (1800 seconds / 10 3M Candles)
                if alert_age > 1800:
                    logger.info(f"Step 7 Precision Scalp: {symbol} 30-minute flat time-stop expired ({alert_age:.0f}s). Closing trade.")
                    from app.telegram_service import TelegramService
                    ts_msg = (
                        f"⏱️ <b>Precision Scalp Time-Stop Alert: #{symbol}</b>\n\n"
                        f"Trade duration reached 30 minutes ({alert_age/60:.0f}m / 10 3M candles).\n"
                        f"Current Price: {price:.4f}\n"
                        f"<b>Action:</b> Close trade at market now. Flat/stagnant momentum detected.\n\n"
                        f"<b>සිංහල උපදෙස් (පියවර 7: විනාඩි 30 Time-Stop):</b>\n"
                        f"විනාඩි 30 ක් (3M ඉටිපන්දම් 10ක්) ගත වී ඇති අතර චලනය මන්දගාමී බැවින් වෙළඳාම Market Price එකෙන් Close කර අවසන් කරන්න."
                    )
                    asyncio.create_task(TelegramService.send_message(ts_msg, symbol=symbol))
                    del _active_trade_positions[symbol]
                    active_pos = None
                    active_pos_dir = None
                # Check Stop Loss breach (Step 6 Micro-Wick SL 0.25%-0.65% Hard-Cap)
                elif pos_dir == "LONG" and price <= pos_sl:
                    logger.info(f"Step 6 Micro-Wick SL: {symbol} active LONG touched SL ({price} <= {pos_sl}). Clearing position.")
                    from app.telegram_service import TelegramService
                    sl_msg = (
                        f"🛑 <b>Precision Scalp Stop Loss Alert: #{symbol}</b>\n\n"
                        f"Price touched Micro-Wick Stop Loss at {price:.4f} (SL: {pos_sl:.4f}).\n"
                        f"0.15% safe buffer protected capital within strict 0.25%-0.65% hard-cap.\n\n"
                        f"<b>සිංහල සටහන (පියවර 6: Micro-Wick SL):</b>\n"
                        f"මිල Stop Loss මට්ටම ({pos_sl:.4f}) ස්පර්ශ විය. 0.15% Buffer සහිත Micro-Wick SL එක මඟින් අවදානම 0.65% ට අඩුවෙන් ආරක්ෂා විය."
                    )
                    asyncio.create_task(TelegramService.send_message(sl_msg, symbol=symbol))
                    del _active_trade_positions[symbol]
                    active_pos = None
                    active_pos_dir = None
                elif pos_dir == "SHORT" and price >= pos_sl:
                    logger.info(f"Step 6 Micro-Wick SL: {symbol} active SHORT touched SL ({price} >= {pos_sl}). Clearing position.")
                    from app.telegram_service import TelegramService
                    sl_msg = (
                        f"🛑 <b>Precision Scalp Stop Loss Alert: #{symbol}</b>\n\n"
                        f"Price touched Micro-Wick Stop Loss at {price:.4f} (SL: {pos_sl:.4f}).\n"
                        f"0.15% safe buffer protected capital within strict 0.25%-0.65% hard-cap.\n\n"
                        f"<b>සිංහල සටහන (පියවර 6: Micro-Wick SL):</b>\n"
                        f"මිල Stop Loss මට්ටම ({pos_sl:.4f}) ස්පර්ශ විය. 0.15% Buffer සහිත Micro-Wick SL එක මඟින් අවදානම 0.65% ට අඩුවෙන් ආරක්ෂා විය."
                    )
                    asyncio.create_task(TelegramService.send_message(sl_msg, symbol=symbol))
                    del _active_trade_positions[symbol]
                    active_pos = None
                    active_pos_dir = None
                # Check Take Profit 2 (Step 7: 1:2.20R - 1:2.50R Full Target, Close Remaining 40%)
                elif pos_dir == "LONG" and pos_tp2 > 0 and price >= pos_tp2:
                    logger.info(f"Step 7 Precision Scalp: {symbol} active LONG hit TP2 Final Target ({price} >= {pos_tp2}). Clearing position.")
                    from app.telegram_service import TelegramService
                    tp_msg = (
                        f"🎉 <b>Precision Scalp Final TP2 Alert: #{symbol} (1:2.50R Achieved!)</b>\n\n"
                        f"🚀 <b>Price reached Full Target (TP2) at {price:.4f}!</b>\n"
                        f"<b>Action:</b> Close remaining 40% of position and bank total profits.\n\n"
                        f"<b>සිංහල උපදෙස් (පියවර 7: TP 2 1:2.50R අවසන් ඉලක්කය):</b>\n"
                        f"මිල සාර්ථකව 1:2.50R ඉලක්කයට (TP2: {pos_tp2:.4f}) ළඟා විය! ඉතිරි 40% Close කර සම්පූර්ණ ලාභය ලබා ගන්න."
                    )
                    asyncio.create_task(TelegramService.send_message(tp_msg, symbol=symbol))
                    del _active_trade_positions[symbol]
                    active_pos = None
                    active_pos_dir = None
                elif pos_dir == "SHORT" and pos_tp2 > 0 and price <= pos_tp2:
                    logger.info(f"Step 7 Precision Scalp: {symbol} active SHORT hit TP2 Final Target ({price} <= {pos_tp2}). Clearing position.")
                    from app.telegram_service import TelegramService
                    tp_msg = (
                        f"🎉 <b>Precision Scalp Final TP2 Alert: #{symbol} (1:2.50R Achieved!)</b>\n\n"
                        f"🚀 <b>Price reached Full Target (TP2) at {price:.4f}!</b>\n"
                        f"<b>Action:</b> Close remaining 40% of position and bank total profits.\n\n"
                        f"<b>සිංහල උපදෙස් (පියවර 7: TP 2 1:2.50R අවසන් ඉලක්කය):</b>\n"
                        f"මිල සාර්ථකව 1:2.50R ඉලක්කයට (TP2: {pos_tp2:.4f}) ළඟා විය! ඉතිරි 40% Close කර සම්පූර්ණ ලාභය ලබා ගන්න."
                    )
                    asyncio.create_task(TelegramService.send_message(tp_msg, symbol=symbol))
                    del _active_trade_positions[symbol]
                    active_pos = None
                    active_pos_dir = None

            # Fetch multi-timeframe candles non-blocking:
            # 15M (100 candles), 5M (500 candles), 3M (500 candles), 1H (100 candles)
            candles_15m = await asyncio.to_thread(get_candles, sym, "15m", 100)
            candles_5m = await asyncio.to_thread(get_candles, sym, "5m", 500)
            candles = await asyncio.to_thread(get_candles, sym, timeframe, 500)
            candles_1h = await asyncio.to_thread(get_candles, sym, "1h", 100)

            # Step 7: TP 1 at 1:1.50R (Close 60% of position)
            if active_pos and not active_pos.get("tp1_notified"):
                pos_dir = active_pos.get("direction")
                pos_entry = float(active_pos.get("entry_price", 0.0))
                pos_tp1 = float(active_pos.get("tp1", 0.0))
                is_tp1_hit = (pos_dir == "LONG" and pos_tp1 > 0 and price >= pos_tp1) or (pos_dir == "SHORT" and pos_tp1 > 0 and price <= pos_tp1)
                if is_tp1_hit:
                    active_pos["tp1_notified"] = True
                    active_pos["breakeven_notified"] = True
                    active_pos["stop_loss"] = pos_entry
                    from app.telegram_service import TelegramService
                    tp1_msg = (
                        f"🎯 <b>Precision Scalp TP 1 Partial Alert: #{symbol} (1:1.50R Achieved!)</b>\n\n"
                        f"Price reached TP 1 at {price:.4f}.\n"
                        f"<b>Action:</b> Close 60% of position to lock in profit! Stop Loss moved to Entry ({pos_entry:.4f}) for a 100% ZERO-RISK trade.\n\n"
                        f"<b>සිංහල උපදෙස් (පියවර 7: TP 1 - 60% ලාභය):</b>\n"
                        f"මිල TP 1 (1:1.50R) මට්ටමට ({pos_tp1:.4f}) ළඟා විය. Position එකෙන් 60% ක් ලාභ ලබා ගන්න. Stop Loss එක Entry ({pos_entry:.4f}) වෙත ගෙන ගොස් Zero-Risk කර ඉතිරි 40% TP 2 දක්වා තබන්න."
                    )
                    asyncio.create_task(TelegramService.send_message(tp1_msg, symbol=symbol))

            # Step 7: Break-Even at +0.80R Profit (Zero-Risk Trade)
            if active_pos and not active_pos.get("breakeven_notified"):
                pos_dir = active_pos.get("direction")
                pos_entry = float(active_pos.get("entry_price", 0.0))
                pos_be = float(active_pos.get("be_trigger", 0.0))
                
                is_be_hit = (pos_dir == "LONG" and pos_be > 0 and price >= pos_be) or (pos_dir == "SHORT" and pos_be > 0 and price <= pos_be)
                if is_be_hit:
                    active_pos["breakeven_notified"] = True
                    active_pos["stop_loss"] = pos_entry
                    from app.telegram_service import TelegramService
                    be_msg = (
                        f"🛡️ <b>Precision Scalp Break-Even Alert: #{symbol} (+0.80R Achieved)</b>\n\n"
                        f"Price reached +0.80R at {price:.4f}.\n"
                        f"<b>Action:</b> Move Stop Loss to Entry ({pos_entry:.4f}) immediately! Trade is now 100% RISK-FREE.\n\n"
                        f"<b>සිංහල උපදෙස් (පියවර 7: Break-Even +0.80R):</b>\n"
                        f"මිල +0.80R ලාභ මට්ටමට ({price:.4f}) ළඟා විය. ඔබගේ Stop Loss එක Entry මිලට ({pos_entry:.4f}) ගෙන යන්න (Break-Even). දැන් වෙළඳාමේ අවදානම 0% කි."
                    )
                    asyncio.create_task(TelegramService.send_message(be_msg, symbol=symbol))

            # Micro Counter-CHoCH Early Invalidation & Exit Guard (Capital Preservation)
            # If active position is running and 1m structure breaks against the trade, dispatch an immediate Early Exit warning!
            if active_pos and not active_pos.get("early_exit_notified"):
                pos_dir = active_pos.get("direction")
                if candles and len(candles) >= 15:
                    last_5 = candles[-5:]
                    prior_swing_low = min(float(c["low"]) for c in candles[-15:-5])
                    prior_swing_high = max(float(c["high"]) for c in candles[-15:-5])
                    
                    has_counter_choch = False
                    if pos_dir == "LONG":
                        has_counter_choch = any(float(c["close"]) < prior_swing_low for c in last_5)
                    elif pos_dir == "SHORT":
                        has_counter_choch = any(float(c["close"]) > prior_swing_high for c in last_5)
                        
                    if has_counter_choch:
                        active_pos["early_exit_notified"] = True
                        from app.telegram_service import TelegramService
                        exit_msg = (
                            f"🚨 <b>Falcon Micro Counter-CHoCH Early Exit Alert: #{symbol}</b>\n\n"
                            f"⚠️ <b>Adverse Micro Counter-CHoCH detected on 3m chart!</b>\n"
                            f"Current Price: {price:.4f} | Direction: {pos_dir}\n"
                            f"<b>Action:</b> Close trade at market now to preserve capital! Cutting loss early at ~0.15% prevents hitting full Stop Loss.\n\n"
                            f"<b>සිංහල අනතුරු ඇඟවීම (Early Invalidation Guard):</b>\n"
                            f"3-Minute Chart එකෙහි වෙළඳාමට ප්‍රතිවිරුද්ධ CHoCH එකක් (Structure Break) හමු විය! සම්පූර්ණ Stop Loss එක වදින තුරු නොසිට, දැන්ම සුළු Loss එකකින් (0.1%-0.2%) වෙළඳාමෙන් Exit වන්න."
                        )
                        asyncio.create_task(TelegramService.send_message(exit_msg, symbol=symbol))
                        logger.warning(f"Early Exit dispatched for {symbol} ({pos_dir}) due to counter-CHoCH at {price}")

            # Fetch daily levels non-blocking
            sym = standardize_symbol(symbol)
            daily_candles = await asyncio.to_thread(get_candles, sym, "1d", 2)
            try:
                daily_open = float(daily_candles[-1]["open"]) if daily_candles else price
                pdh = float(daily_candles[-2]["high"]) if len(daily_candles) >= 2 else price * 1.01
                pdl = float(daily_candles[-2]["low"]) if len(daily_candles) >= 2 else price * 0.99
            except Exception as dex:
                logger.error(f"Error fetching daily levels for {symbol} in SMC tracker: {dex}")
                daily_open = price
                pdh = price * 1.01
                pdl = price * 0.99

            coin_key = f"{symbol}_{timeframe}"
            last_notified = _smc_notified_timestamps.get(coin_key, 0)
            
            payload = {
                "symbol": symbol,
                "timeframe": timeframe,
                "current_price": price,
                "pdh": pdh,
                "pdl": pdl,
                "daily_open": daily_open
            }
            
            from app.services import AIService
            result = await AIService.calculate_programmatic_smc(payload, local_only=True)
            
            pipeline = result.get("pipeline", {})
            current_phase = result.get("current_phase") or pipeline.get("current_phase", 1)
            current_phase_name_si = result.get("current_phase_name_si") or pipeline.get("current_phase_name_si", "")
            current_phase_name_en = result.get("current_phase_name_en") or pipeline.get("current_phase_name_en", "")
            pipeline_progress_pct = result.get("pipeline_progress_pct") or pipeline.get("pipeline_progress_pct", 0)
            is_pipeline_ready = bool(result.get("is_pipeline_ready", False))
            step_7_passed = bool(pipeline.get("step_7_passed", False) or (current_phase == 7 and result.get("is_valid", False)))
            confidence = result.get("confidence", 0)

            t15m_val = str(result.get("trend_15m") or "NEUTRAL").upper().strip()
            t5m_val = str(result.get("trend_5m") or "NEUTRAL").upper().strip()
            t1h_val = str(result.get("trend_1h") or "NEUTRAL").upper().strip()
            entry_price = str(result.get("entry_price_area") or "")
            is_long = "BUY" in entry_price.upper() or "LONG" in str(result.get("direction", "")).upper()
            dir_mode = "LONG" if is_long else "SHORT"

            news_locked = bool(result.get("news_lockout_active", False))
            active_news_ev = str(result.get("active_news_event") or "USD High-Impact News")

            # Determine 8-gate hard-locked pipeline status & Falcon live state
            retr_disp = str(result.get("retracement_status_display") or "").strip()
            market_regime = str(result.get("market_regime") or "TRENDING EXPANSION ✅")
            wave_cnt = int(result.get("wave_count") or 1)
            wave_label = str(result.get("wave_label") or f"Wave {wave_cnt}")
            active_tier_name = str(result.get("active_tier") or "Tier 1: 3M FVG")
            
            if active_pos:
                pos_dir = active_pos.get("direction")
                if pos_dir != dir_mode:
                    status = f"🔒 Position Running ({pos_dir})"
                else:
                    status = f"🚀 Running to Targets ({pos_dir})"
            elif current_phase == 0 or ("CHOPPY" in market_regime.upper() and t15m_val not in ["BULLISH", "BEARISH"]):
                status = "Gate 0: Market Choppy / Range Blocked 🛑"
                entry_price = "No Entry (ADX < 14 / Squeeze Locked)"
            elif news_locked:
                status = "Gate 1: Macro Wait / News Lockout"
                entry_price = f"No Entry (USD News Lockout: {active_news_ev})"
            elif current_phase == 1:
                status = f"Gate 1: Macro Wait / 15M Anchor ({t15m_val})"
            elif current_phase == 2 or wave_cnt > 4 or "5+" in wave_label:
                status = f"Gate 2: {wave_label} Exhaustion - Blocked 🛑" if (wave_cnt > 4 or "5+" in wave_label) else f"Gate 2: {wave_label} Active"
            elif current_phase == 3:
                status = retr_disp if retr_disp else f"Gate 3: Retrace to 3-Tier Cascade ({active_tier_name})"
            elif current_phase == 4:
                status = "Gate 4: Awaiting Volume RVOL >= 1.35x Rebound 📊"
            elif current_phase == 5:
                status = retr_disp if retr_disp else "Gate 5: 2-Candle Reversal Confirmation..."
            elif current_phase == 6:
                status = "Gate 6: Micro-Wick SL Armed (0.25%-0.65%) 🛡️"
            elif result.get("is_valid", False) and step_7_passed:
                status = f"🎯 SMC Confirmed 2-Candle Market Execution! Triggering {'Long' if is_long else 'Short'} Scalp 📌"
            elif t15m_val in ["BULLISH", "BEARISH"]:
                status = f"Gate 1: Macro Wait / 15M Anchor ({t15m_val})"
            else:
                status = "Gate 0: Market Choppy / Range Blocked 🛑"

            is_supreme_entry = bool(result.get("is_valid", False) and step_7_passed and not active_pos and not news_locked and wave_cnt <= 4)

            # Absolute Execution Guard: Current Candle Color Lock (Stop runaway counter-trend trades)
            curr_c_3m = candles[-1] if (candles and len(candles) > 0) else None
            if curr_c_3m:
                c_open_v = float(curr_c_3m["open"])
                c_close_v = float(curr_c_3m["close"])
                if is_long and c_close_v <= c_open_v:
                    is_supreme_entry = False
                    status = "⏳ Current 3M Candle is Red (Dumping) — Long Aborted (Anti-Counter-Dump Lock)"
                elif not is_long and c_close_v >= c_open_v:
                    is_supreme_entry = False
                    status = "⏳ Current 3M Candle is Green (Pumping) — Short Aborted (Anti-Counter-Pump Lock)"

            if not is_supreme_entry and "Triggering" in status:
                status = retr_disp if retr_disp else "Gate 5: Awaiting 2-Candle Confirmation..."

            calc_entry = 0.0
            calc_sl = 0.0
            calc_tp1 = 0.0
            calc_tp2 = 0.0
            calc_be = 0.0

            if is_supreme_entry:
                prec = get_dynamic_precision(price)
                # Gate 5: 2-Candle Closed State Machine Execution Entry
                res_entry = result.get("entry_price")
                calc_entry = round(float(res_entry), prec) if (res_entry and float(res_entry) > 0) else round(float(price), prec)
                
                # Gate 6: Micro-Wick Stop Loss Buffer (0.25%-0.65% Hard-Cap)
                res_sl = result.get("stop_loss_level")
                if res_sl and float(res_sl) > 0:
                    calc_sl = round(float(res_sl), prec)
                else:
                    calc_sl = round(calc_entry * (0.9960 if is_long else 1.0040), prec)

                # Ensure SL is strictly on correct side
                if is_long and calc_sl >= calc_entry:
                    calc_sl = round(calc_entry * 0.9960, prec)
                elif not is_long and calc_sl <= calc_entry:
                    calc_sl = round(calc_entry * 1.0040, prec)

                r_dist = abs(calc_entry - calc_sl)
                if r_dist == 0 or (calc_entry > 0 and (r_dist / calc_entry) < 0.0020):
                    r_dist = calc_entry * 0.0035
                    calc_sl = round(calc_entry + (-r_dist if is_long else r_dist), prec)

                # Gate 7: Rapid Scalp Exits (BE +0.80R, Fixed 1:2.0R TP)
                res_tp1 = result.get("tp1_target")
                res_tp2 = result.get("tp2_target")
                res_be = result.get("breakeven_trigger")

                calc_tp1 = round(float(res_tp1), prec) if (res_tp1 and float(res_tp1) > 0) else round(calc_entry + (1.50 * r_dist if is_long else -1.50 * r_dist), prec)
                calc_tp2 = round(float(res_tp2), prec) if (res_tp2 and float(res_tp2) > 0) else round(calc_entry + (2.00 * r_dist if is_long else -2.00 * r_dist), prec)
                calc_be = round(float(res_be), prec) if (res_be and float(res_be) > 0) else round(calc_entry + (0.80 * r_dist if is_long else -0.80 * r_dist), prec)

                # Overwrite checks for SHORT / LONG to prevent identical/inverted targets
                if is_long:
                    if calc_tp1 <= calc_entry or calc_tp2 <= calc_tp1 or calc_be <= calc_entry:
                        calc_tp1 = round(calc_entry + (1.50 * r_dist), prec)
                        calc_tp2 = round(calc_entry + (2.00 * r_dist), prec)
                        calc_be = round(calc_entry + (0.80 * r_dist), prec)
                else:
                    if calc_tp1 >= calc_entry or calc_tp2 >= calc_tp1 or calc_be >= calc_entry:
                        calc_tp1 = round(calc_entry - (1.50 * r_dist), prec)
                        calc_tp2 = round(calc_entry - (2.00 * r_dist), prec)
                        calc_be = round(calc_entry - (0.80 * r_dist), prec)

                # Final Execution Alignment Check (15M Trend & 5M Market Structure Sync):
                if (is_long and (t15m_val != "BULLISH" or t5m_val != "BULLISH")) or (not is_long and (t15m_val != "BEARISH" or t5m_val != "BEARISH")):
                    logger.warning(f"15M/5M Bias check failed for {symbol}: 15M={t15m_val}, 5M={t5m_val} opposes {dir_mode}. Alert BLOCKED!")
                    is_supreme_entry = False
                    status = f"🔒 15M/5M Structure Lock ({t15m_val}/{t5m_val})"

                # 30-minute cooldown to guarantee ONLY ONE alert is sent per entry setup
                if is_supreme_entry and (now_ts - last_notified) > 1800:
                    from app.telegram_service import TelegramService
                    from app.chart_service import ChartService
                    
                    bias_15m_5m_str = f"{t15m_val} / {t5m_val}"
                    caption, reply_markup = TelegramService.build_trade_alert(
                        symbol=symbol,
                        direction=dir_mode,
                        entry_price=calc_entry,
                        stop_loss=calc_sl,
                        tp1=calc_tp1,
                        tp2=calc_tp2,
                        confidence=confidence,
                        setup_path=result.get("setup_path"),
                        setup_route=result.get("setup_route"),
                        setup_model=result.get("setup_model"),
                        be_trigger=calc_be,
                        trend_1h=bias_15m_5m_str
                    )
                    
                    chart_bytes = ChartService.generate_smc_chart(
                        symbol=symbol,
                        timeframe=timeframe,
                        klines=candles[-60:] if candles else [],
                        entry=calc_entry,
                        sl=calc_sl,
                        tp1=calc_tp1,
                        tp2=calc_tp2,
                        direction=dir_mode,
                        key_levels={"15M PDH": pdh, "15M PDL": pdl}
                    )
                    
                    # Guaranteed Telegram delivery: try photo with chart, fallback to text message
                    sent_success = False
                    if chart_bytes:
                        try:
                            sent_success = await TelegramService.send_photo(chart_bytes, caption, symbol=symbol, reply_markup=reply_markup)
                        except Exception as p_err:
                            logger.error(f"Error in send_photo for {symbol}: {p_err}")
                            sent_success = False
                    
                    if not sent_success:
                        try:
                            sent_success = await TelegramService.send_message(caption, symbol=symbol, reply_markup=reply_markup)
                        except Exception as m_err:
                            logger.error(f"Error in fallback send_message for {symbol}: {m_err}")
                            sent_success = False

                    if sent_success:
                        _smc_notified_timestamps[coin_key] = now_ts
                        # Register active trade position in memory (Rule 81 & Rule 91)
                        _active_trade_positions[symbol] = {
                            "direction": dir_mode,
                            "entry_price": calc_entry,
                            "stop_loss": calc_sl,
                            "tp1": calc_tp1,
                            "tp2": calc_tp2,
                            "be_trigger": calc_be,
                            "alert_time": now_ts
                        }
                        status = f"🎯 Local {'HL' if is_long else 'LH'} Confirmed! Triggering {'Long' if is_long else 'Short'} Scalp 📌"
                        logger.info(f"✅ Telegram supreme trade alert for {symbol} confirmed and dispatched successfully.")
                    else:
                        status = f"🎯 Local {'HL' if is_long else 'LH'} Confirmed! Triggering {'Long' if is_long else 'Short'} Scalp (Dispatch Pending)"
                        logger.warning(f"⚠️ Telegram dispatch failed for {symbol}. Will retry on next candle cycle.")
                    
            # Update single coin in DB IMMEDIATELY!
            update_data = {
                "status": status,
                "confidence": confidence,
                "is_valid": is_supreme_entry,
                "entryPrice": str(calc_entry) if is_supreme_entry else None,
                "stopLoss": round(calc_sl, 4) if (is_supreme_entry and calc_sl) else None,
                "takeProfit": round(calc_tp2, 4) if (is_supreme_entry and calc_tp2) else None,
                "takeProfit1": round(calc_tp1, 4) if (is_supreme_entry and calc_tp1) else None,
                "breakevenTrigger": round(calc_be, 4) if (is_supreme_entry and calc_be) else None,
                "currentPrice": price,
                "current_phase": current_phase,
                "current_phase_name_si": current_phase_name_si,
                "current_phase_name_en": current_phase_name_en,
                "pipeline_progress_pct": pipeline_progress_pct,
                "is_pipeline_ready": is_pipeline_ready,
                "trend_1h": t1h_val,
                "trend_15m": t15m_val,
                "trend_5m": t5m_val,
                "market_regime": market_regime,
                "adx_14": result.get("adx_14"),
                "is_bb_squeeze": result.get("is_bb_squeeze"),
                "wave_count": result.get("wave_count"),
                "wave_label": result.get("wave_label"),
                "fib_level": result.get("fib_level"),
                "setup_path": result.get("setup_path"),
                "setup_route": result.get("setup_route"),
                "setup_model": result.get("setup_model"),
                "active_tier": result.get("active_tier"),
                "active_tier_level": result.get("active_tier_level"),
                "last_result": result
            }
            await update_single_coin_in_db(symbol, timeframe, update_data)
            logger.info(f"Updated live SMC scan for {symbol}: {confidence}% ({status})")
            
        except Exception as e:
            logger.error(f"Error scanning coin {symbol}: {e}")

async def run_smc_tracker_loop():
    logger.info("SMC Background Tracker Loop Started with Deduplication Engine & Live Concurrent Execution.")
    semaphore = asyncio.Semaphore(8)
    
    # Clean stale historical statuses on first startup loop and seed default coins if empty
    try:
        db_init = SessionLocal()
        pref_init = db_init.query(PreferenceModel).filter(PreferenceModel.key == "smc_monitored_coins").first()
        if pref_init and pref_init.value:
            init_coins = json.loads(pref_init.value)
            dirty = False
            for ic in init_coins:
                if ic.get("status") in ["ENTRY CONFIRMED (Notified)", "ENTRY READY"]:
                    ic["status"] = "MONITORING"
                    ic["is_valid"] = False
                    ic["stopLoss"] = None
                    ic["takeProfit"] = None
                    ic["breakevenTrigger"] = None
                    dirty = True
            if dirty:
                pref_init.value = json.dumps(init_coins)
                db_init.commit()
                logger.info("Cleaned stale historical coin statuses and targets on startup.")
        else:
            # Auto-seed default 21 coins if missing
            pref_init = PreferenceModel(key="smc_monitored_coins", value=json.dumps(DEFAULT_SMC_MONITORED_COINS))
            db_init.add(pref_init)
            db_init.commit()
            logger.info("Seeded default 21 Binance coins into smc_monitored_coins preference.")
        db_init.close()
    except Exception as iex:
        logger.error(f"Error resetting initial coin statuses on startup: {iex}")
    
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

            if not monitored_coins:
                monitored_coins = DEFAULT_SMC_MONITORED_COINS

            # Record tracker heartbeat in DB
            try:
                db_hb = SessionLocal()
                hb_pref = db_hb.query(PreferenceModel).filter(PreferenceModel.key == "tracker_heartbeat").first()
                if hb_pref:
                    hb_pref.value = str(time.time())
                else:
                    db_hb.add(PreferenceModel(key="tracker_heartbeat", value=str(time.time())))
                db_hb.commit()
                db_hb.close()
            except Exception as hbe:
                logger.error(f"Error saving tracker heartbeat: {hbe}")

            if monitored_coins:
                # Scan gently in batches of 3 coins with 0.5s pause to eliminate socket and rate-limit spikes
                for i in range(0, len(monitored_coins), 3):
                    chunk = monitored_coins[i:i+3]
                    tasks = [analyze_single_coin_task(coin, semaphore) for coin in chunk]
                    await asyncio.gather(*tasks, return_exceptions=True)
                    await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error in SMC tracker loop: {e}", exc_info=True)
            
        await asyncio.sleep(8)

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
        # Read monitored coins from DB preferences
        db = SessionLocal()
        try:
            from app.models import PreferenceModel
            pref = db.query(PreferenceModel).filter(PreferenceModel.key == "tcs_monitored_coins").first()
            watchlist = json.loads(pref.value) if pref and pref.value else []
        except Exception as pe:
            logger.error(f"Error reading tcs_monitored_coins preference: {pe}")
            watchlist = []
        finally:
            db.close()
            
        if watchlist:
            coins_to_delete = set()
            updated_any = False
            
            for coin in list(watchlist):
                symbol = coin.get("symbol", "").upper()
                if not symbol:
                    continue
                    
                # Fetch live price
                try:
                    price = await asyncio.to_thread(get_current_price, symbol)
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
                    tcs_notified_symbols[key] = True
                    await TelegramService.send_message(msg, symbol=symbol)
                    coins_to_delete.add(f"{symbol}_{entry_price}")
                    updated_any = True
                    
            # Write updated watchlist back to SQLite preferences safely (fetching latest DB state first)
            if updated_any:
                db = SessionLocal()
                try:
                    pref = db.query(PreferenceModel).filter(PreferenceModel.key == "tcs_monitored_coins").first()
                    if pref and pref.value:
                        current_db_coins = json.loads(pref.value)
                        updated_list = []
                        db_changed = False
                        for db_coin in current_db_coins:
                            coin_sym = db_coin.get("symbol", "").upper()
                            coin_entry = db_coin.get("entryPrice")
                            del_key = f"{coin_sym}_{coin_entry}"
                            if del_key in coins_to_delete:
                                db_changed = True
                                continue # Delete from DB
                            updated_list.append(db_coin)
                            
                        if db_changed:
                            pref.value = json.dumps(updated_list)
                            db.commit()
                except Exception as se:
                    logger.error(f"Error saving updated tcs_monitored_coins in tracker: {se}")
                finally:
                    db.close()
                    
        await asyncio.sleep(10)

def start_tcs_tracker():
    global tcs_tracker_task
    if tcs_tracker_task is None or tcs_tracker_task.done():
        tcs_tracker_task = asyncio.create_task(run_tcs_tracker_loop())

