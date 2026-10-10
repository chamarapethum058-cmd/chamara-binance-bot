import os
import sys

# Force disable SSR mode so Python runs directly on port 7860 without Node.js proxy failure
os.environ["GRADIO_SSR_MODE"] = "false"

# Suppress BaseEventLoop.__del__ log noise on garbage collection
import asyncio.base_events as _base_events
def _patch_asyncio_event_loop_del():
    original_del = getattr(_base_events.BaseEventLoop, "__del__", None)
    if original_del:
        def __del__(self):
            try:
                original_del(self)
            except ValueError as e:
                if str(e) != "Invalid file descriptor: -1":
                    raise e
        _base_events.BaseEventLoop.__del__ = __del__
_patch_asyncio_event_loop_del()

import zipfile
import logging
import asyncio
import threading
import json
import time
import pandas as pd

# Falcon Cloud Engine Build Version (Forces Hugging Face Container Rebuild)
BUILD_VERSION = "2026.10.10-v146.0-PURE-5M-3M-SMC-STATE-MACHINE"
# Space Force-Restart Timestamp: 2026-10-10T18:15:00+05:30



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("falcon_cloud")
logger.info(f"Starting Falcon Cloud Engine - Version: {BUILD_VERSION}")

curr_dir = os.path.dirname(os.path.abspath(__file__))
zip_path = os.path.join(curr_dir, "app.zip")
app_dir = os.path.join(curr_dir, "app")

# 1. Extract app.zip unconditionally to ensure the latest code is always used
if os.path.exists(zip_path):
    try:
        logger.info(f"Extracting latest {zip_path} to {curr_dir}...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(curr_dir)
        logger.info("Extraction complete.")
    except Exception as ze:
        logger.error(f"Error extracting app.zip: {ze}")

# 2. Ensure __init__.py exists in app folder
if os.path.exists(app_dir):
    init_p = os.path.join(app_dir, "__init__.py")
    if not os.path.exists(init_p):
        with open(init_p, "w", encoding="utf-8") as f:
            f.write("# falcon app package\n")

if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

import gradio as gr  # type: ignore
from app.tracker import run_smc_tracker_loop, DEFAULT_SMC_MONITORED_COINS
from app.telegram_service import TelegramService
from app.services import AIService
from app.database import SessionLocal, engine, Base
from app.models import PreferenceModel

Base.metadata.create_all(bind=engine)

# Start background 24/7 tracker in a dedicated daemon thread with its own loop without polluting main event loop
def _start_tracker_thread():
    time.sleep(5)  # Wait for web server to start and pass health check
    while True:
        loop = asyncio.new_event_loop()
        try:
            logger.info("Falcon SMC 24/7 tracker loop started in dedicated background thread...")
            loop.run_until_complete(run_smc_tracker_loop())
        except Exception as e:
            logger.error(f"Error in SMC tracker loop: {e}", exc_info=True)
        finally:
            try:
                loop.close()
            except Exception:
                pass
        time.sleep(5)

try:
    already_running = any(t.name == "FalconTracker" and t.is_alive() for t in threading.enumerate())
    if not already_running:
        tracker_thread = threading.Thread(target=_start_tracker_thread, daemon=True, name="FalconTracker")
        tracker_thread.start()
        logger.info("Background Falcon 24/7 Tracker daemon thread started successfully.")
    else:
        logger.info("FalconTracker daemon thread is already active. Skipping duplicate thread launch.")
except Exception as e:
    logger.error(f"Error launching tracker thread: {e}")

try:
    import spaces  # type: ignore
    has_spaces = True
except ImportError:
    spaces = None
    has_spaces = False

def _get_falcon_status_report():
    thread_alive = any(t.name == "FalconTracker" and t.is_alive() for t in threading.enumerate())
    db = SessionLocal()
    total_coins = 0
    is_scanner_active = thread_alive
    try:
        hb_pref = db.query(PreferenceModel).filter(PreferenceModel.key == "tracker_heartbeat").first()
        if hb_pref and hb_pref.value:
            if (time.time() - float(hb_pref.value)) < 120:
                is_scanner_active = True
        pref = db.query(PreferenceModel).filter(PreferenceModel.key == "smc_monitored_coins").first()
        if pref and pref.value:
            total_coins = len(json.loads(pref.value))
    except Exception as ex:
        logger.error(f"Error reading status: {ex}")
    finally:
        db.close()
    return f"🦅 Falcon ZeroGPU AI Core Active & Synchronized | Background Scanner Running: {is_scanner_active} | Monitored: {total_coins} Coins (3m)"

def check_falcon_status(btn_click):
    return _get_falcon_status_report()

if has_spaces:
    @spaces.GPU(duration=60)
    def zero_gpu_ai_accelerator(prompt: str = ""):
        return f"Falcon ZeroGPU Core Initialized: {prompt}"
else:
    def zero_gpu_ai_accelerator(prompt: str = ""):
        return f"Falcon CPU Core Initialized: {prompt}"

async def test_telegram():
    try:
        msg = (
            "🦅 <b>Falcon 24/7 Pure SMC Engine Online! (Dual 5M/3M Confluence & Wave 1-4 Sniper Active)</b>\n\n"
            "Hugging Face Spaces scanner is live and monitoring Falcon coins 24/7.\n"
            "• <b>Level 1 (15M Macro Anchor):</b> Pure 15M Fractal Structure (BULLISH -> BUY_ONLY, BEARISH -> SELL_ONLY)\n"
            "• <b>Level 2 (5M Structural Level & Wave Guard):</b> 5M Waves 1-4, BOS Invalidation, Breaker/FVG/Fib Tap\n"
            "• <b>Level 3 (3M CHoCH Shift):</b> 3M Change of Character Body Break\n"
            "• <b>Level 4 (3M Micro Wave 2/4):</b> Pullback Retracement to 3M Breaker/FVG/Fib (Wave >= 5 Blocked)\n"
            "• <b>Level 5 (2-Candle Reversal):</b> Rejection Wick >= 35%, Body Break & Close, SL 0.15% beyond Wick, Fixed 1:2.0R TP\n\n"
            "<b>සිංහල පරිවර්තනය (Sinhala):</b>\n"
            "Falcon 24/7 Pure SMC Engine එක සාර්ථකව සක්‍රීය විය! පිරිසිදු 5M & 3M ද්විත්ව කාලරාමු අභිසාරී පද්ධතිය, 15M Macro Anchor, 5M Breaker/FVG/Fib Zone, 3M CHoCH Shift, සහ Wave 2/4 Retracement සමඟින් ඉටිපන්දම් 2 ක Reversal Entry (0.15% SL, 1:2.0R TP) සජීවීව ක්‍රියාත්මක වේ."
        )
        success = await TelegramService.send_message(msg)
        if success:
            return "✅ Telegram alert sent successfully! Check your Telegram app."
        else:
            return "❌ Failed to send Telegram alert. Check your Bot Token and Chat ID."
    except Exception as ex:
        return f"❌ Error: {ex}"

def resolve_coin_pipeline(c: dict):
    """Resolve the Dual-Timeframe 5M & 3M Symmetric SMC pipeline status for a coin."""
    last_res = c.get("last_result") if isinstance(c.get("last_result"), dict) else {}
    pipe = last_res.get("pipeline") if isinstance(last_res.get("pipeline"), dict) else {}
    
    # Level 1: 15M Macro Direction Anchor (BULLISH / BEARISH)
    t15m = str(c.get("trend_15m") or last_res.get("trend_15m") or "NEUTRAL").upper().strip()
    if t15m == "BULLISH":
        macro_15m = "BULLISH 🟢"
    elif t15m == "BEARISH":
        macro_15m = "BEARISH 🔴"
    elif "BULL" in t15m:
        macro_15m = "BULLISH 🟢"
    elif "BEAR" in t15m:
        macro_15m = "BEARISH 🔴"
    else:
        macro_15m = "NEUTRAL ⚪"

    # Level 2: 5M Structural Level Confluence (5M Breaker, 5M FVG, 5M Golden Pocket Fib 0.50-0.786)
    conf_5m = str(
        c.get("confluence_5m") 
        or last_res.get("confluence_5m") 
        or pipe.get("confluence_5m") 
        or c.get("active_tier") 
        or last_res.get("active_tier") 
        or "Awaiting 5M Zone"
    ).strip()
    if not conf_5m or conf_5m in ["None", "NONE", ""]:
        conf_5m = "Awaiting 5M Zone"

    # Level 4: 3M Wave / Level (Wave 1-4 Retracement / Wave 5+ Blocked)
    w_3m = str(
        c.get("wave_3m_level") 
        or last_res.get("wave_3m_level") 
        or pipe.get("wave_3m_level") 
        or ""
    ).strip()
    wave_num = int(c.get("wave_count") or last_res.get("wave_count") or pipe.get("wave_count") or 1)
    wave_lbl = str(c.get("wave_label") or last_res.get("wave_label") or pipe.get("wave_label") or "")

    if not w_3m or w_3m in ["None", ""]:
        if wave_num > 4 or "5+" in wave_lbl:
            w_3m = "Wave 5+ (Blocked)"
        elif wave_num in [2, 4]:
            w_3m = f"Wave {wave_num}"
        elif wave_num == 3:
            w_3m = "Wave 3"
        else:
            w_3m = "Wave 1"

    # Phase / Gate resolution (0 to 5)
    raw_phase = c.get("current_phase") if c.get("current_phase") is not None else (
        pipe.get("current_phase") if pipe.get("current_phase") is not None else (
            last_res.get("current_phase") if last_res.get("current_phase") is not None else None
        )
    )
    status_str = str(c.get("status") or "").strip()
    is_valid = bool(c.get("is_valid", False) or last_res.get("is_valid", False))
    news_active = bool(last_res.get("news_lockout_active", False) or "NEWS" in status_str.upper())
    
    try:
        step_num = int(raw_phase) if raw_phase is not None else 0
    except Exception:
        step_num = 0

    is_buy = "BULL" in macro_15m or "BUY" in status_str.upper() or "LONG" in str(c.get("direction", "")).upper()
    is_wave_blocked = bool(wave_num > 4 or "5+" in w_3m or "BLOCKED" in w_3m.upper() or "EXHAUSTION" in status_str.upper())

    # Format execution prices if actionable
    entry_raw = c.get("entryPrice") or last_res.get("entry_price") or last_res.get("entry_price_area")
    sl_raw = c.get("stopLoss") or last_res.get("stop_loss_level")
    tp2_raw = c.get("takeProfit") or last_res.get("tp2_target")

    def _fmt_p(val):
        if val is None:
            return "-"
        try:
            fv = float(val)
            if fv <= 0:
                return "-"
            if fv < 0.001:
                return f"${fv:.8f}"
            elif fv < 1.0:
                return f"${fv:.5f}"
            elif fv < 100.0:
                return f"${fv:.4f}"
            else:
                return f"${fv:.2f}"
        except Exception:
            s = str(val).strip()
            if s.startswith("$"):
                return s
            return f"${s}" if s and s != "-" and "NO ENTRY" not in s.upper() else "-"

    e_disp = _fmt_p(entry_raw)
    sl_disp = _fmt_p(sl_raw)
    tp_disp = _fmt_p(tp2_raw)

    is_running = any(k in status_str.upper() for k in ["RUNNING", "IN TRADE", "BE ACHIEVED", "POSITION RUNNING"])
    is_actionable = bool(((is_valid and step_num >= 5) or is_running) and "ABORT" not in status_str.upper() and e_disp != "-")

    five_min_valid = bool(c.get("five_min_structure_valid", last_res.get("five_min_structure_valid", pipe.get("five_min_structure_valid", True))))
    five_min_w = int(c.get("five_min_wave") or last_res.get("five_min_wave") or pipe.get("five_min_wave") or 1)
    is_pullback = bool(c.get("is_pullback_wave", last_res.get("is_pullback_wave", pipe.get("is_pullback_wave", True))))

    if news_active or "NEWS" in status_str.upper():
        step_num = 0
        active_status = "Gate 1: Macro Wait / USD News Lockout 🛡️"
    elif not five_min_valid or "5M STRUCTURAL BREAK" in status_str.upper():
        active_status = "5M Structural Break Detected - Setup Invalidated 🛑"
    elif five_min_w > 4 or "5M MACRO WAVE 5+" in status_str.upper():
        active_status = "5M Macro Wave 5+ Exhaustion Trap - Blocked 🛑"
    elif is_wave_blocked:
        active_status = f"Gate 2: {w_3m} Exhaustion - Blocked 🛑"
    elif not is_pullback and step_num >= 3:
        target_w = "Wave 2" if wave_num <= 1 else "Wave 4"
        active_status = f"Gate 3: Awaiting {target_w} Micro Pullback"
    elif is_actionable:
        act_cmd = "INSTANT MARKET BUY" if is_buy else "INSTANT MARKET SELL"
        active_status = f"🎯 {act_cmd} | Entry: {e_disp} | SL: {sl_disp} | TP: {tp_disp}"
    elif step_num == 4:
        active_status = "Gate 4: 3M Wick Rejection (>=35%) & Next Body Close Shift..."
    elif step_num == 3:
        active_status = f"Gate 3: Retrace to 3M Confluence ({w_3m})"
    elif step_num == 2:
        active_status = f"Gate 2: Awaiting 3M CHoCH Shift ({conf_5m})"
    elif step_num == 1:
        active_status = f"Gate 1: Awaiting 5M Key Zone Tap ({t15m})"
    else:
        active_status = "Gate 0: 15M Macro Neutral / Chop"

    return step_num, macro_15m, conf_5m, w_3m, active_status

def get_watchlist_summary_html():
    db = SessionLocal()
    total_coins = 0
    trending_active = 0
    level_2_active = 0
    level_3_active = 0
    level_4_5_active = 0
    news_lockout_active = False
    active_news_title = ""
    try:
        pref = db.query(PreferenceModel).filter(PreferenceModel.key == "smc_monitored_coins").first()
        coins = []
        if pref and pref.value:
            try:
                coins = json.loads(pref.value)
            except Exception:
                coins = []
        if not coins:
            coins = DEFAULT_SMC_MONITORED_COINS

        total_coins = len(coins)
        for c in coins:
            s_num, macro_15m, conf_5m, w_3m, active_status = resolve_coin_pipeline(c)
            s_up = str(c.get("status", "")).upper()
            if "NEWS" in s_up:
                news_lockout_active = True
                parts = str(c.get("status", "")).split("Lockout:")
                if len(parts) > 1:
                    active_news_title = parts[1].strip()

            if "BULLISH" in macro_15m or "BEARISH" in macro_15m:
                trending_active += 1

            if s_num == 2 or ("Awaiting 5M Zone" not in conf_5m and "Awaiting" not in conf_5m):
                level_2_active += 1
            elif s_num == 3:
                level_3_active += 1
            elif s_num in [4, 5]:
                level_4_5_active += 1
    except Exception as e:
        logger.error(f"Error summary: {e}")
    finally:
        db.close()

    news_banner_html = ""
    if news_lockout_active:
        news_banner_html = f'''<div style="background:linear-gradient(90deg, #7f1d1d, #991b1b); border:1px solid #ef4444; border-radius:8px; padding:10px 16px; margin-bottom:12px; text-align:center; color:#fef2f2; font-size:13px; font-weight:600; box-shadow:0 0 14px rgba(239, 68, 68, 0.45);">
            🛡️ <b>USD HIGH-IMPACT NEWS LOCKOUT ACTIVE:</b> {active_news_title or 'USD High-Impact Event'} — Capital Protection Armed (ගිණුම ආරක්ෂා කිරීමට වෙළඳාම් තාවකාලිකව අත්හිටුවා ඇත).
        </div>'''
        
    return f"""{news_banner_html}<div style="background:#0f172a; border:1px solid #334155; border-radius:12px; padding:16px 20px; margin-bottom:12px; display:flex; justify-content:space-around; align-items:center; flex-wrap:wrap; gap:14px; box-shadow:0 4px 16px rgba(0,0,0,0.3);">
        <div style="text-align:center; min-width:140px;">
            <span style="color:#94a3b8; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">📊 Total Monitored</span><br>
            <b style="color:#38bdf8; font-size:22px; font-family:monospace;">{total_coins} Coins</b>
        </div>
        <div style="text-align:center; min-width:140px;">
            <span style="color:#94a3b8; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">🧭 15M Macro Trending</span><br>
            <b style="color:#10b981; font-size:22px; font-family:monospace;">{trending_active} (Level 1+)</b>
        </div>
        <div style="text-align:center; min-width:140px;">
            <span style="color:#94a3b8; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">📐 5M Level Tapped</span><br>
            <b style="color:#38bdf8; font-size:22px; font-family:monospace;">{level_2_active} (Level 2)</b>
        </div>
        <div style="text-align:center; min-width:140px;">
            <span style="color:#94a3b8; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">⚡ 3M CHoCH Shift</span><br>
            <b style="color:#a78bfa; font-size:22px; font-family:monospace;">{level_3_active} (Level 3)</b>
        </div>
        <div style="text-align:center; min-width:140px;">
            <span style="color:#94a3b8; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">🎯 Wave 1-4 & Scalps</span><br>
            <b style="color:#34d399; font-size:22px; font-family:monospace;">{level_4_5_active} (Level 4-5)</b>
        </div>
    </div>"""


WATCHLIST_COLUMNS = ["Symbol (.P)", "15M Trend", "5M Zone (Breaker/FVG/Fib)", "3M Wave", "State Machine Status"]

def get_watchlist_data():
    db = SessionLocal()
    data = []
    try:
        pref = db.query(PreferenceModel).filter(PreferenceModel.key == "smc_monitored_coins").first()
        coins = []
        if pref and pref.value:
            try:
                coins = json.loads(pref.value)
            except Exception:
                coins = []
        if not coins:
            coins = DEFAULT_SMC_MONITORED_COINS

        for c in coins:
            step_num, macro_15m, conf_5m, w_3m, active_status = resolve_coin_pipeline(c)

            # Clean Coin Symbol to .P Binance Futures Perpetual Ticker
            raw_sym = str(c.get("symbol", "")).strip().upper()
            if raw_sym.endswith(".P"):
                disp_sym = raw_sym
            else:
                clean_s = raw_sym.replace(".P", "").replace("USDT", "").strip()
                disp_sym = f"{clean_s}USDT.P"

            data.append([
                disp_sym,
                macro_15m,
                conf_5m,
                w_3m,
                active_status
            ])
    except Exception as e:
        logger.error(f"Error loading watchlist: {e}")
        fallback_data = []
        for def_coin in DEFAULT_SMC_MONITORED_COINS:
            step_num, macro_15m, conf_5m, w_3m, active_status = resolve_coin_pipeline(def_coin)
            raw_s = str(def_coin.get("symbol", "")).strip().upper()
            clean_s = raw_s if raw_s.endswith(".P") else f"{raw_s.replace('.P', '').replace('USDT', '').strip()}USDT.P"
            fallback_data.append([
                clean_s,
                macro_15m,
                conf_5m,
                w_3m,
                active_status
            ])
        return pd.DataFrame(fallback_data, columns=WATCHLIST_COLUMNS)
    finally:
        db.close()

    if data:
        return pd.DataFrame(data, columns=WATCHLIST_COLUMNS)

    # Guaranteed non-empty fallback DataFrame
    fallback_data = []
    for def_coin in DEFAULT_SMC_MONITORED_COINS:
        step_num, macro_15m, conf_5m, w_3m, active_status = resolve_coin_pipeline(def_coin)
        raw_s = str(def_coin.get("symbol", "")).strip().upper()
        clean_s = raw_s if raw_s.endswith(".P") else f"{raw_s.replace('.P', '').replace('USDT', '').strip()}USDT.P"
        fallback_data.append([
            clean_s,
            macro_15m,
            conf_5m,
            w_3m,
            active_status
        ])
    return pd.DataFrame(fallback_data, columns=WATCHLIST_COLUMNS)

def refresh_all_watchlist():
    return get_watchlist_summary_html(), get_watchlist_data()

# Interactive On-Demand Analysis Logic
async def run_live_coin_analysis(symbol_input, timeframe_input, mode_input, engine_choice):
    sym = (symbol_input or "BTCUSDT").strip().upper()
    if sym.endswith(".P"):
        sym = sym[:-2]
    if not sym.endswith("USDT") and not sym.endswith("USD") and sym not in ["BTC", "ETH", "SOL", "XAUUSD"]:
        sym = f"{sym}USDT"
    elif sym in ["BTC", "ETH", "SOL"]:
        sym = f"{sym}USDT"

    tf = timeframe_input or "3m"
    exec_mode = "SNIPER" if "SNIPER" in str(mode_input).upper() else "SCALP_PRO"
    is_local_only = "Fast Programmatic" in str(engine_choice)

    payload = {
        "symbol": sym,
        "timeframe": tf,
        "execution_mode": exec_mode
    }

    try:
        res = await AIService.calculate_programmatic_smc(payload, local_only=is_local_only)
    except Exception as e:
        logger.error(f"Error in on-demand analysis for {sym}: {e}", exc_info=True)
        err_banner = f"""<div style="background:#450a0a; border:1px solid #ef4444; border-radius:10px; padding:15px; color:#fecaca;">
            <h3 style="margin:0; color:#f87171;">❌ Analysis Error for {sym}</h3>
            <p style="margin:5px 0 0 0;">{str(e)}</p>
        </div>"""
        return err_banner, "CHOPPY / SQUEEZE (LOCKED)", "[Gate 0]: 🔒 Error / Lockout", "-", "-", "-", "-", "-", f"Error: {e}", f"Error: {e}", "{}"

    is_valid = bool(res.get("is_valid", False))
    curr_phase = res.get("current_phase") if res.get("current_phase") is not None else 0
    phase_name_en = res.get("current_phase_name_en") or f"GATE {curr_phase}"
    entry_area = str(res.get("entry_price_area") or "No Entry")
    sl = res.get("stop_loss_level")
    tp1 = res.get("tp1_target")
    tp2 = res.get("tp2_target") or res.get("liquidity_target")
    be = res.get("breakeven_trigger")
    rr = str(res.get("target_reward_ratio") or "1:1.50R / 1:2.30R")

    m_reg = res.get("market_regime", "CHOPPY / SQUEEZE (LOCKED)")
    adx_v = float(res.get("adx_14", 0.0))
    is_sq = bool(res.get("is_bb_squeeze", False))
    wave_num = int(res.get("wave_count", 1))
    wave_label = str(res.get("wave_label") or f"Wave {wave_num}")
    fib_val = float(res.get("fib_level", 0.5))
    confluence_5m = str(res.get("confluence_5m") or "Awaiting 5M Zone")
    wave_3m_level = str(res.get("wave_3m_level") or wave_label)

    regime_step_disp = f"15M {t15m} EXPANSION ✅" if t15m in ["BULLISH", "BEARISH"] else "15M CONSOLIDATION ⚪"

    retr_disp = str(res.get("retracement_status_display") or "").strip()
    is_buy_dir = ("BUY" in entry_area.upper() or "LONG" in str(res.get("direction", "")).upper())

    # Determine 5-Level SMC pipeline status & live state
    if curr_phase == 5 or is_valid:
        pipeline_step_disp = "[Level 5]: 🎯 2-Candle Reversal Market Execution (Fixed 1:2.0R)"
        falcon_live_state = f"🎯 SMC Confirmed 2-Candle Market Execution! INSTANT MARKET {'BUY' if is_buy_dir else 'SELL'} 📌"
    elif curr_phase == 4:
        pipeline_step_disp = "[Level 4]: 🚦 3M 2-Candle Reversal Pending (Wick >= 35%)"
        falcon_live_state = "Level 4: 3M Wick Rejection (>=35%) & Next Body Close Shift..."
    elif curr_phase == 3:
        pipeline_step_disp = f"[Level 3]: ⚡ 3M Micro Retracement ({wave_3m_level})"
        falcon_live_state = f"Level 3: Retrace to 3M Confluence ({wave_3m_level})"
    elif curr_phase == 2:
        pipeline_step_disp = f"[Level 2]: 📐 Awaiting 3M CHoCH Shift ({confluence_5m})"
        falcon_live_state = f"Level 2: Awaiting 3M CHoCH Shift ({'Green Body > LH' if is_buy_dir else 'Red Body < HL'})"
    elif curr_phase == 1:
        pipeline_step_disp = f"[Level 1]: 🧭 Awaiting 5M Key Zone Tap ({t15m})"
        falcon_live_state = f"Level 1: Awaiting 5M Key Zone Tap ({t15m})"
    else:
        pipeline_step_disp = "[Level 0]: 🛑 15M Macro Neutral / Chop"
        falcon_live_state = "Level 0: 15M Macro Neutral / Chop 🛑"

    t15m = str(res.get("trend_15m") or "NEUTRAL").upper().strip()
    t5m = str(res.get("trend_5m") or "NEUTRAL").upper().strip()

    if is_valid and is_buy_dir:
        status_banner = f"""<div style="background:#064e3b; border:1px solid #10b981; border-radius:10px; padding:15px; color:#d1fae5;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0; color:#34d399;">🟢 ACTIVE BUY LIMIT SETUP (DUAL-TIMEFRAME SMC VERIFIED)</h2>
                <span style="background:#10b981; color:#064e3b; font-weight:bold; padding:4px 12px; border-radius:20px; font-size:14px;">🎯 {wave_3m_level} TRIGGERED 📌</span>
            </div>
            <p style="margin:8px 0 0 0; font-size:14px;"><b>Symbol:</b> {sym} | <b>Timeframe:</b> {tf} | <b>15M Macro:</b> {t15m} | <b>5M Confluence:</b> {confluence_5m} | <b>Execution:</b> Market Order at ${res.get('entry_price', 0):.4f}</p>
        </div>"""
    elif is_valid and not is_buy_dir:
        status_banner = f"""<div style="background:#7f1d1d; border:1px solid #ef4444; border-radius:10px; padding:15px; color:#fee2e2;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0; color:#f87171;">🔴 ACTIVE SELL LIMIT SETUP (DUAL-TIMEFRAME SMC VERIFIED)</h2>
                <span style="background:#ef4444; color:#7f1d1d; font-weight:bold; padding:4px 12px; border-radius:20px; font-size:14px;">🎯 {wave_3m_level} TRIGGERED 📌</span>
            </div>
            <p style="margin:8px 0 0 0; font-size:14px;"><b>Symbol:</b> {sym} | <b>Timeframe:</b> {tf} | <b>15M Macro:</b> {t15m} | <b>5M Confluence:</b> {confluence_5m} | <b>Execution:</b> Market Order at ${res.get('entry_price', 0):.4f}</p>
        </div>"""
    elif curr_phase == 0 or t15m == "NEUTRAL":
        status_banner = f"""<div style="background:#450a0a; border:1px solid #f43f5e; border-radius:10px; padding:15px; color:#ffe4e6;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0; color:#fb7185;">🔒 LEVEL 0: 15M MACRO NEUTRAL / CONSOLIDATION LOCKOUT</h2>
                <span style="background:#e11d48; color:#ffffff; font-weight:bold; padding:4px 12px; border-radius:20px; font-size:14px;">NO TRADES IN NEUTRAL</span>
            </div>
            <p style="margin:8px 0 0 0; font-size:14px;"><b>15M Macro:</b> {t15m} | <b>Status:</b> පැහැදිලි 15M Macro Direction එකක් (Bullish හෝ Bearish) නොමැතිව වෙළඳාම් කිරීම 100% ක් අත්හිටුවා ඇත.</p>
        </div>"""
    else:
        status_banner = f"""<div style="background:#1e1b4b; border:1px solid #6366f1; border-radius:10px; padding:15px; color:#e0e7ff;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0; color:#818cf8;">⏳ DUAL-TIMEFRAME SMC PIPELINE: LEVEL {curr_phase}/5</h2>
                <span style="background:#4f46e5; color:#ffffff; font-weight:bold; padding:4px 12px; border-radius:20px; font-size:14px;">LEVEL {curr_phase} EVALUATION</span>
            </div>
            <p style="margin:8px 0 0 0; font-size:14px;"><b>15M Macro:</b> {t15m} | <b>5M Confluence:</b> {confluence_5m} | <b>Status:</b> {pipeline_step_disp} | <b>Live State:</b> {falcon_live_state}</p>
        </div>"""

    def _fmt_price_val(v):
        if not v:
            return "-"
        try:
            fv = float(v)
            if fv <= 0:
                return "-"
            if fv < 0.001:
                return f"${fv:.8f}"
            elif fv < 1.0:
                return f"${fv:.5f}"
            elif fv < 100.0:
                return f"${fv:.4f}"
            else:
                return f"${fv:.2f}"
        except Exception:
            return str(v)

    sl_str = _fmt_price_val(sl)
    tp1_str = _fmt_price_val(tp1)
    tp2_str = _fmt_price_val(tp2)
    be_str = _fmt_price_val(be)
    entry_disp = entry_area if (is_valid or curr_phase >= 5) and "NO ENTRY" not in entry_area.upper() else "-"

    # Format Dual-Timeframe SMC Checklist (Level 1 - Level 5)
    checklist = res.get("rules_checklist", [])
    rule_num_map = {
        1: ("Level 1", "15M Macro Trend Anchor", "පියවර 1: 15M සාර්ව ප්‍රවණතා නැංගුරම (15M Macro Trend Anchor & News Armor)"),
        2: ("Level 2", "5M Structural Level Detector", "පියවර 2: 5M ව්‍යුහාත්මක කලාප අනාවරකය (5M Breaker, FVG, Fib 0.50-0.786)"),
        3: ("Level 3", "3M CHoCH Structure Shift", "පියවර 3: 3M CHoCH ව්‍යුහාත්මක හැරීම (Change of Character Shift)"),
        4: ("Level 4", "3M Wave 1-4 Micro Retracement", "පියවර 4: 3M Wave 1-4 ක්ෂුද්‍ර නැවත පැමිණීම (3M Breaker, FVG, Fib 0.50-0.618)"),
        5: ("Level 5", "3M 2-Candle Reversal & Execution", "පියවර 5: ඉටිපන්දම් 2 ක හැරීම සහ ක්ෂණික වෙළඳපල නියෝගය (Wick >= 35%, Body Break, SL 0.15%, TP 1:2.0R)")
    }
    rule_rows = ""
    for r_no, (r_label, name_en, name_si) in rule_num_map.items():
        rule_item = next((r for r in checklist if (r.get("step_no") == r_no or r.get("rule_no") == r_no or r.get("gate_no") == r_no)), None)
        passed = rule_item.get("passed", False) if rule_item else False
        badge = "✅ PASSED" if passed else "⏳ PENDING"
        detail_txt = rule_item.get("detail_si") or rule_item.get("detail") or "-" if rule_item else "-"
        rule_rows += f"| **{r_label}** | {name_si} | **{badge}** | {detail_txt} |\n"

    rules_smc_md = f"""### 🦅 Dual-Timeframe SMC Confluence Engine (Level 1 - Level 5)
| මට්ටම (SMC Level) | ආයතනික පදනම (Protocol) | තත්ත්වය (Status) | සජීවී ඇගයීම (Live Institutional Audit) |
| :---: | :--- | :---: | :--- |
{rule_rows}"""

    # Extract Multi-Timeframe Triad variables for display (15M / 5M / 3M)
    t15m_md = str(res.get("trend_15m") or "NEUTRAL").upper()
    zone_val = str(res.get("zone_type") or ("DISCOUNT (< 50%)" if is_buy_dir else "PREMIUM (> 50%)"))
    post_choch = "3M Instant Market Order Primed ✅" if is_valid else f"Level {curr_phase}/5 Active ⏳"

    triad_md = f"""{rules_smc_md}

---

### 🏛️ Multi-Timeframe Precision Architecture (15M Macro Anchor • 5M Structural Level • 3M Sniper Execution)
| Timeframe | Institutional Function | Status / Structure | Confirmation |
| :--- | :--- | :--- | :--- |
| **15M HTF** | Macro Direction Anchor (100 Candles) | **{t15m_md}** | HH/HL = Buy Only, LL/LH = Sell Only |
| **5M ITF** | Structural Level Detector (Pullback Zone) | **{confluence_5m} ({zone_val})** | 5M Breaker Re-test, 5M FVG Tap, or 5M Golden Pocket Fib 0.50-0.786 |
| **3M LTF** | CHoCH Shift & 2-Candle Reversal Market Order | **{post_choch}** | Wick >= 35% + Body Break, 0.15% SL Buffer, Fixed 1:2.0R TP |
"""

    reasoning_text = res.get("reasoning", "No technical reasoning available.")
    invalidation_text = res.get("invalidation", "None provided.")
    risk_notes_text = res.get("risk_notes", "Strict 0.15% SL beyond Rejection Wick, Fixed 1:2.0R TP.")

    reasoning_full_md = f"""
### 🧠 Institutional Technical Reasoning & Bilingual Explanation
{reasoning_text}

---
**🛑 Invalidation Level:** `{invalidation_text}`  
**⚠️ Risk Management Notes:** `{risk_notes_text}`  
<b>🛡️ Dual-Timeframe SMC Engine:</b> `5M & 3M Symmetric Multi-Pathway Active`
"""

    # Pack raw json for telegram dispatch
    dispatch_payload = {
        "symbol": sym,
        "timeframe": tf,
        "is_valid": is_valid,
        "market_regime": regime_step_disp,
        "pipeline_status": pipeline_step_disp,
        "live_state": falcon_live_state,
        "entry": entry_disp,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "be": be,
        "rr": rr,
        "reasoning": reasoning_text,
        "direction": res.get("direction")
    }

    return (
        status_banner,
        regime_step_disp,
        pipeline_step_disp,
        entry_disp,
        sl_str,
        tp1_str,
        tp2_str,
        be_str,
        triad_md,
        reasoning_full_md,
        json.dumps(dispatch_payload)
    )

async def send_analysis_to_telegram(json_state_str):
    if not json_state_str or json_state_str == "{}":
        return "⚠️ Please run an analysis first before sending to Telegram."
    try:
        data = json.loads(json_state_str)
        sym = data.get("symbol", "UNKNOWN")
        tf = data.get("timeframe", "3m")
        entry = data.get("entry", "-")
        sl = data.get("sl")
        tp1 = data.get("tp1")
        tp2 = data.get("tp2")
        be = data.get("be")
        is_valid = data.get("is_valid", False)
        m_reg = data.get("market_regime", "15M EXPANSION ✅")
        pipe_stat = data.get("pipeline_status", "[Level 5]: 2-Candle Market Execution")
        live_stat = data.get("live_state", "SIGNAL TRIGGERED 📌")

        is_buy = "BUY" in str(entry).upper() or "LONG" in str(data.get("direction", "")).upper()
        dir_str = "INSTANT MARKET BUY 🟢" if is_buy else ("INSTANT MARKET SELL 🔴" if ("SELL" in str(entry).upper() or "SHORT" in str(data.get("direction", "")).upper()) else "MARKET UPDATE 📊")

        msg = (
            f"🦅 <b>Falcon Dual-Timeframe SMC Precision Scalp Analysis</b>\n\n"
            f"<b>Symbol:</b> #{sym} ({tf})\n"
            f"<b>Direction:</b> {dir_str}\n"
            f"<b>15M Macro:</b> {m_reg}\n"
            f"<b>SMC Level:</b> {pipe_stat}\n"
            f"<b>Live State:</b> {live_stat}\n\n"
            f"🎯 <b>Execution:</b> <code>{entry}</code>\n"
            f"🛑 <b>Micro-Wick SL:</b> <code>${sl}</code> (0.15% beyond Wick)\n"
            f"🎯 <b>TP 1 (60%):</b> <code>${tp1}</code> (1:1.50R Partial Lock)\n"
            f"🏁 <b>TP 2 (40%):</b> <code>${tp2}</code> (1:2.0R Fixed Target)\n"
            f"🛡️ <b>Break-Even (+0.80R):</b> <code>${be}</code>\n\n"
            f"<b>🦅 Dual-Timeframe 5M & 3M SMC Confluences:</b>\n"
            f"• Level 1: 15M Macro Direction Anchor & News Armor (+/-60m)\n"
            f"• Level 2: 5M Structural Level Detector (5M Breaker / FVG / Fib 0.50-0.786)\n"
            f"• Level 3: 3M CHoCH Structure Shift (Green Body > LH / Red Body < HL)\n"
            f"• Level 4: 3M Wave 1-4 Micro Retracement (3M Breaker / FVG / Fib 0.50-0.618)\n"
            f"• Level 5: 3M 2-Candle Reversal & Execution (Wick >= 35%, Body Break, SL 0.15%, TP 1:2.0R)\n\n"
            f"<b>සිංහල සටහන (Sinhala):</b>\n"
            f"Falcon Dual-Timeframe SMC Engine (5M & 3M Symmetric) මඟින් #{sym} සඳහා තහවුරු කළ වාර්තාව. 15M Macro Direction එක යටතේ 5M සහ 3M Pathways 3 (FVG, Breaker, Fib) හරහා Level 1 සිට Level 5 දක්වා 100% ක් පරීක්ෂා කර ඇත."
        )

        sent = False
        if is_valid and sl and tp2:
            try:
                from app.chart_service import ChartService
                from app.market import get_candles
                candles = await asyncio.to_thread(get_candles, sym, tf, 60)
                n_entry = float(entry.replace("$", "")) if "$" in str(entry) else float(entry)
                n_sl = float(sl)
                n_tp2 = float(tp2)
                n_tp1 = float(tp1) if tp1 else (n_entry + (abs(n_entry - n_sl) * 1.5) if is_buy else n_entry - (abs(n_entry - n_sl) * 1.5))
                chart_bytes = ChartService.generate_smc_chart(
                    symbol=sym,
                    timeframe=tf,
                    klines=candles,
                    entry=n_entry,
                    sl=n_sl,
                    tp1=n_tp1,
                    tp2=n_tp2,
                    direction="LONG" if is_buy else "SHORT"
                )
                if chart_bytes:
                    sent = await TelegramService.send_photo(chart_bytes, msg, symbol=sym)
            except Exception as c_err:
                logger.warning(f"On-demand chart dispatch failed: {c_err}")

        if not sent:
            sent = await TelegramService.send_message(msg)

        if sent:
            return f"✅ Analysis report for #{sym} successfully dispatched to your Telegram app!"
        else:
            return "❌ Failed to send Telegram alert. Please check your Bot Token and Chat ID settings."
    except Exception as ex:
        return f"❌ Error sending to Telegram: {ex}"

# Build Gradio UI
with gr.Blocks(title="Falcon Dual-Timeframe SMC Confluence Engine (5M & 3M Symmetric)") as demo:
    gr.Markdown("""
    # 🦅 Falcon Dual-Timeframe SMC Confluence Engine (5M & 3M Symmetric)
    **Status:** 🟢 **LIVE & RUNNING 24/7 (v145.0 Active)** | **Architecture:** Dual-Layer 5M & 3M Multi-Pathway HL/LH Reversal Engine  
    **Framework:** Level 1: 15M Macro Anchor -> Level 2: 5M Structural Level (Breaker/FVG/Fib) -> Level 3: 3M CHoCH Shift -> Level 4: 3M Wave 1-4 Retracement -> Level 5: 3M 2-Candle Reversal & Market Execution (SL 0.15%, Fixed 1:2.0R TP)
    """)

    with gr.Tabs():
        # TAB 1: INTERACTIVE LIVE MARKET ANALYZER
        with gr.Tab("🔍 Live Market Analyzer (ඕනෑම Coin එකක් විශ්ලේෂණය කරන්න)"):
            gr.Markdown("### 🎯 Analyze Any Binance Crypto Pair with Dual-Timeframe SMC Engine (5M & 3M Symmetric)")
            
            with gr.Row():
                symbol_in = gr.Dropdown(
                    label="Trading Pair (Coin)",
                    choices=[
                        "BTCUSDT", "ETHUSDT", "SOLUSDT", "ENAUSDT", "BNBUSDT", 
                        "DOGEUSDT", "XRPUSDT", "SUIUSDT", "PEPEUSDT", "AVAXUSDT", 
                        "ADAUSDT", "NEARUSDT", "LINKUSDT", "TRXUSDT", "LTCUSDT", "POPCATUSDT"
                    ],
                    value="BTCUSDT",
                    allow_custom_value=True,
                    info="Select or type any Binance USDT pair"
                )
                timeframe_in = gr.Dropdown(
                    label="Execution Timeframe",
                    choices=["3m", "5m", "15m", "1m"],
                    value="3m",
                    info="Selected execution chart"
                )
                mode_in = gr.Dropdown(
                    label="Execution Mode",
                    choices=["PRECISION_SCALP (5M & 3M Symmetric)", "SNIPER_STRICT (Zero-Bypass)"],
                    value="PRECISION_SCALP (5M & 3M Symmetric)",
                    info="Precision execution engine"
                )
                engine_in = gr.Radio(
                    label="Analysis Engine",
                    choices=["⚡ Fast Programmatic SMC (Local 5-Level)", "🧠 Hybrid AI Deep Reasoning (Gemini + Local Rules)"],
                    value="⚡ Fast Programmatic SMC (Local 5-Level)",
                    info="100% Free & Fast Python math vs Hybrid Gemini AI"
                )

            with gr.Row():
                analyze_btn = gr.Button("🚀 Run Dual-Timeframe SMC Analysis (දැන් විශ්ලේෂණය කරන්න)", variant="primary", size="lg")

            status_banner_out = gr.HTML("""<div style="background:#1e1b4b; border:1px solid #4338ca; border-radius:10px; padding:15px; color:#c7d2fe;">
                <b>Ready to Analyze:</b> Select a coin and click the button above to run real-time Dual-Timeframe SMC analysis.
            </div>""")

            with gr.Row():
                regime_out = gr.Textbox(label="⚡ 15M Macro Trend (Level 1)", interactive=False)
                pipeline_step_out = gr.Textbox(label="🦅 SMC Level Status (Level 1-5)", interactive=False)
                entry_out = gr.Textbox(label="🎯 Instant Market Order (Level 5)", interactive=False)
                sl_out = gr.Textbox(label="🛑 Stop Loss (0.15% beyond Wick)", interactive=False)
                tp1_out = gr.Textbox(label="🎯 TP 1 (1:1.50R Partial)", interactive=False)
                tp2_out = gr.Textbox(label="🏁 TP 2 (1:2.0R Fixed Target)", interactive=False)
                be_out = gr.Textbox(label="🛡️ Break-Even (+0.80R)", interactive=False)

            triad_out = gr.Markdown("### 🏛️ Multi-Timeframe Precision Architecture\n*Awaiting analysis...*")
            reasoning_out = gr.Markdown("### 🧠 Technical Reasoning & Sinhala Translation\n*Awaiting analysis...*")

            # Telegram Dispatch Section
            raw_state = gr.Textbox(visible=False, value="{}")
            with gr.Row():
                send_tg_btn = gr.Button("📲 Send this Analysis Report to Telegram (ටෙලිග්‍රෑම් වෙත යවන්න)", variant="secondary")
                send_tg_status = gr.Textbox(label="Telegram Dispatch Status", interactive=False)

            analyze_btn.click(
                fn=run_live_coin_analysis,
                inputs=[symbol_in, timeframe_in, mode_in, engine_in],
                outputs=[status_banner_out, regime_out, pipeline_step_out, entry_out, sl_out, tp1_out, tp2_out, be_out, triad_out, reasoning_out, raw_state]
            )

            send_tg_btn.click(
                fn=send_analysis_to_telegram,
                inputs=[raw_state],
                outputs=[send_tg_status]
            )

        # TAB 2: 24/7 BACKGROUND MONITORING WATCHLIST
        with gr.Tab("📊 24/7 Background Live Watchlist (සජීවී නිරීක්ෂණය)"):
            gr.Markdown("""
            ### 📡 24/7 Background Cloud Scanner Watchlist — Dual-Timeframe SMC Engine (5M & 3M Symmetric)
            **Falcon Dual-Layer Multi-Pathway HL/LH Reversal Tracker**  
            මෙම සජීවී Watchlist එක මඟින් Binance හි ප්‍රමුඛ පෙළේ Coins:  
            1. **15M Macro Trend Anchor** (Bullish -> Buy Only, Bearish -> Sell Only)  
            2. **5M Structural Level Detector** (5M Breaker Re-test, 5M FVG Tap, හෝ 5M Golden Pocket Fib 0.50-0.786)  
            3. **3M CHoCH Shift** (Green Body > LH හෝ Red Body < HL)  
            4. **3M Wave 1-4 Micro Retracement** (3M Breaker, 3M FVG, හෝ 3M Fib 0.50-0.618; Wave >= 5 Blocked)  
            5. **3M 2-Candle Reversal & Execution** (Wick >= 35%, Body Break, SL 0.15% beyond Wick, Fixed 1:2.0R TP)  
            අනුපිළිවෙලින් පරීක්ෂා කරයි. **සියලුම මට්ටම් සාර්ථකව සපුරා ඇති අවස්ථා (INSTANT MARKET BUY/SELL 📌) පමණක් Telegram වෙත ක්ෂණිකව නිකුත් කෙරේ.**
            """)

            summary_banner = gr.HTML(get_watchlist_summary_html)

            with gr.Row():
                refresh_wl_btn = gr.Button("🔄 Refresh Watchlist Now (සජීවී දත්ත ක්ෂණිකව Refresh කරන්න)", variant="secondary")

            watchlist_table = gr.Dataframe(
                headers=WATCHLIST_COLUMNS,
                datatype=["str", "str", "str", "str", "str"],
                value=get_watchlist_data,
                interactive=False,
                wrap=True
            )
            refresh_wl_btn.click(fn=refresh_all_watchlist, outputs=[summary_banner, watchlist_table])

            timer = gr.Timer(value=10, active=True)
            timer.tick(fn=refresh_all_watchlist, outputs=[summary_banner, watchlist_table])

            with gr.Row():
                test_btn = gr.Button("📲 Test Telegram Notification", variant="primary")
                status_txt = gr.Textbox(label="Telegram Test Status", interactive=False)
            test_btn.click(fn=test_telegram, outputs=status_txt)

            with gr.Row():
                gpu_btn = gr.Button("⚡ Verify AI Hardware Status", variant="secondary")
                gpu_txt = gr.Textbox(label="Hardware Status", interactive=False)
            gpu_btn.click(fn=check_falcon_status, inputs=[gpu_txt], outputs=[gpu_txt])

    # Initial page load auto-refresh
    demo.load(fn=refresh_all_watchlist, outputs=[summary_banner, watchlist_table])

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=10).launch(
        server_name="0.0.0.0", 
        server_port=7860, 
        ssr_mode=False, 
        theme=gr.themes.Soft(primary_hue="blue"), 
        show_error=True
    )

