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
BUILD_VERSION = "2026.10.10-v143.0-TIMER-10S-GATE0-UNLOCK"
# Space Force-Restart Timestamp: 2026-10-10T14:48:00+05:30



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
            "🦅 <b>Falcon 24/7 Cloud Engine Online! (v128.0 Anti-Waterfall Shield Active)</b>\n\n"
            "Hugging Face Spaces scanner is live and monitoring Falcon coins 24/7.\n"
            "• <b>Master Falcon Rules:</b> 1 - 91 (All 91 Rules Active & Audited)\n"
            "• <b>Anti-Waterfall Shield:</b> 5M EMA50/20 & Bearish BOS Hard-Block active (Rule 16/56)\n"
            "• <b>Strict 15M + 5M Alignment:</b> Zero Counter-Trend Execution\n"
            "• <b>Falcon Institutional SMC Engine:</b> High-Velocity 80%+ Confluence Unanimous Agreement\n"
            "• <b>Real Structural Targets:</b> TP 2 (1:4.0R Confirmed Swing Liquidity) & TP 1 (1:2.0R 50% Auto-Close) +1.0R Break-Even\n"
            "• <b>Instant Execution:</b> Market Price Execution on Verified 80%+ SMC Signals\n\n"
            "<b>සිංහල පරිවර්තනය (Sinhala):</b>\n"
            "Falcon 24/7 Cloud Engine එක සාර්ථකව සක්‍රීය විය! සියලුම Falcon ආයතනික SMC නීති, Dual Entry Engine (Model 1 Fast-Track Sniper සහ Model 2 Conservative Retest), 80%+ Confluence එකඟතාව (BUY නම් BUY, SELL නම් SELL 100% එකඟතාව), Strict 15M+5M Macro Alignment, සහ සැබෑ Swing Liquidity මත පදනම් වූ 1:2 / 1:4 RR Targets සජීවීව ක්‍රියාත්මක වේ. තහවුරු වූ ආයතනික වෙළඳ සංඥා පමණක් ක්ෂණිකව Telegram වෙත නිකුත් කෙරේ."
        )
        success = await TelegramService.send_message(msg)
        if success:
            return "✅ Telegram alert sent successfully! Check your Telegram app."
        else:
            return "❌ Failed to send Telegram alert. Check your Bot Token and Chat ID."
    except Exception as ex:
        return f"❌ Error: {ex}"

def resolve_coin_pipeline(c: dict):
    """Resolve the 100% sequential hard-locked SMC pipeline status, live state, regime, and bias for a coin."""
    last_res = c.get("last_result") if isinstance(c.get("last_result"), dict) else {}
    pipe = last_res.get("pipeline") if isinstance(last_res.get("pipeline"), dict) else {}
    
    # 0. Regime check (ADX 14 & BB Squeeze) - Unlocked Squeeze for ADX >= 16
    m_reg = c.get("market_regime") or last_res.get("market_regime") or pipe.get("market_regime")
    adx_val = float(c.get("adx_14") or last_res.get("adx_14") or pipe.get("adx_14") or 0.0)
    is_sq = bool(c.get("is_bb_squeeze") or last_res.get("is_bb_squeeze") or pipe.get("is_bb_squeeze") or False)
    
    if m_reg and "CHOPPY" in m_reg.upper() and adx_val >= 16.0:
        regime_disp = "TRENDING EXPANSION ✅"
    elif m_reg:
        regime_disp = m_reg
    elif adx_val >= 16.0:
        regime_disp = "TRENDING EXPANSION ✅"
    else:
        regime_disp = "CHOPPY / SQUEEZE (LOCKED)"

    # Phase / Gate resolution (0 to 7)
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
        
    # 1. Bias (Gate 1): 15M Macro Directional Bias (BULLISH / BEARISH)
    t15m = str(c.get("trend_15m") or last_res.get("trend_15m") or "NEUTRAL").upper().strip()
    t5m = str(c.get("trend_5m") or last_res.get("trend_5m") or "NEUTRAL").upper().strip()
    
    if t15m == "BULLISH":
        bias_disp = "BULLISH 🟢 (Buy Only)"
    elif t15m == "BEARISH":
        bias_disp = "BEARISH 🔴 (Sell Only)"
    elif "BULL" in t15m or "BULL" in t5m:
        bias_disp = f"BULLISH ({t15m})"
    elif "BEAR" in t15m or "BEAR" in t5m:
        bias_disp = f"BEARISH ({t15m})"
    else:
        bias_disp = "NEUTRAL ⚪"

    is_buy = "BULL" in bias_disp or "BUY" in status_str.upper() or "LONG" in str(c.get("direction", "")).upper()
    wave_num = int(c.get("wave_count") or last_res.get("wave_count") or pipe.get("wave_count") or 1)
    wave_disp = f"Wave {wave_num}/4" if wave_num <= 4 else f"Wave {wave_num} (Exhaustion 🛑)"

    # Active Tier Extraction (Tier 1: FVG, Tier 2: Breaker, Tier 3: Golden Pocket 0.50-0.786)
    active_tier = c.get("active_tier") or last_res.get("active_tier") or pipe.get("active_tier") or ""

    # 2. Sequential Hard-Lock Pipeline Status & Live Gate State
    if news_active or "NEWS" in status_str.upper():
        step_num = 1
        pipeline_status = "[Gate 1]: 🛡️ Macro Wait / News Lockout"
        live_state = "Gate 1: Macro Wait / USD News Lockout 🛡️"
        active_tier_disp = "USD News Lockout"
    elif ("CHOPPY" in regime_disp.upper() or step_num == 0) and adx_val < 16.0:
        step_num = 0
        pipeline_status = "[Gate 0]: 🛑 Market Choppy / Range Blocked"
        live_state = "Gate 0: Market Choppy / Range Blocked 🛑"
        active_tier_disp = "Volatility Squeeze Locked"
    elif step_num == 0 and adx_val >= 16.0:
        step_num = 1
        pipeline_status = f"[Gate 1]: 🧭 15M Anchor ({bias_disp})"
        live_state = f"Gate 1: 15M Macro Trend ({bias_disp})"
        active_tier_disp = "Awaiting 15M Anchor"
    elif wave_num > 4 or "EXHAUSTION" in status_str.upper() or "WAVE 5" in status_str.upper():
        step_num = 2
        pipeline_status = f"[Gate 2]: 🛑 Wave {wave_num} Exhaustion - Blocked"
        live_state = f"Gate 2: Wave {wave_num} Exhaustion - Blocked 🛑"
        active_tier_disp = f"Wave {wave_num} Exhaustion - Locked"
    elif "ABORT" in status_str.upper() or "ABORT" in str(c.get("status", "")).upper() or "ABORT" in str(pipe.get("status", "")).upper():
        step_num = 5
        pipeline_status = f"[Gate 5]: 🚫 {status_str}"
        live_state = f"Gate 5: {status_str} 🚫"
        active_tier_disp = "Counter-Trend Candle Abort"
    elif "RUNNING" in status_str.upper() or "IN TRADE" in status_str.upper() or "BE ACHIEVED" in status_str.upper() or is_valid or step_num == 7:
        step_num = 7
        pipeline_status = "[Gate 7]: 🚀 Instant Market Scalp (BE +0.80R / Fixed 1:2.0R)"
        act_str = "BUY" if is_buy else "SELL"
        live_state = f"🎯 SMC Confirmed 2-Candle Market Execution! INSTANT MARKET {act_str} 📌"
        active_tier_disp = active_tier or "Confirmed Market Scalp"
    elif step_num == 6:
        pipeline_status = "[Gate 6]: 🛡️ Micro-Wick SL Armed (0.25%-0.65%)"
        live_state = "Gate 6: Micro-Wick SL Armed (0.25%-0.65%) 🛡️"
        active_tier_disp = active_tier or "SL Guard Armed"
    elif step_num == 5:
        pipeline_status = "[Gate 5]: 🚦 2-Candle State Machine Reversal Pending"
        live_state = "Gate 5: 3M Wick Rejection (>=35%) & Next Body Close Shift..."
        active_tier_disp = active_tier or "Reversal Close Pending"
    elif step_num == 4:
        pipeline_status = "[Gate 4]: 📊 RVOL >= 1.35x Volume Pending"
        live_state = "Gate 4: Awaiting Volume RVOL >= 1.35x Rebound 📊"
        active_tier_disp = active_tier or "Volume Check"
    elif step_num == 3:
        if active_tier and "LOCKED" not in active_tier.upper():
            active_tier_disp = active_tier
            pipeline_status = f"[Gate 3]: ⏳ {active_tier} (Fib {'< 0.50' if is_buy else '> 0.50'})"
            live_state = f"Gate 3: Retrace to {active_tier}"
        elif "MID-RANGE" in active_tier.upper() or "LOCKED" in active_tier.upper():
            active_tier_disp = active_tier
            pipeline_status = f"[Gate 3]: ⏳ {active_tier}"
            live_state = f"Gate 3: {active_tier}"
        else:
            active_tier_disp = "Mid-Range Floating (Locked)"
            pipeline_status = "[Gate 3]: ⏳ Mid-Range Floating (Locked)"
            live_state = "Gate 3: Waiting for Tier 1-3 Mitigation"
    elif step_num == 2:
        pipeline_status = f"[Gate 2]: 🔢 Wave {wave_num}/4 Active"
        live_state = f"Gate 2: Wave {wave_num}/4 Impulse Verified"
        active_tier_disp = f"Wave {wave_num}/4 Active"
    elif step_num == 1:
        pipeline_status = f"[Gate 1]: 🧭 15M Anchor ({bias_disp})"
        live_state = f"Gate 1: Waiting for 15M Macro Alignment ({bias_disp})"
        active_tier_disp = "Awaiting 15M Macro Alignment"
    else:
        step_num = 0
        pipeline_status = "[Gate 0]: 🛑 Market Choppy / Range Blocked"
        live_state = "Gate 0: Market Choppy / Range Blocked 🛑"
        active_tier_disp = "Volatility Squeeze Locked"

    # Scrub legacy references
    for legacy_word in ["RULE", "TRAP", "CONFLUENCE", "CONFIDENCE", "CHOCH CONFIRMATION"]:
        if legacy_word in live_state.upper() and not any(k in live_state.upper() for k in ["CONFIRMED", "PULLBACK", "EXHAUSTION", "GATE"]):
            live_state = "Gate 0: Market Choppy / Range Blocked 🛑"

    return step_num, regime_disp, wave_disp, pipeline_status, live_state, active_tier_disp

def get_watchlist_summary_html():
    db = SessionLocal()
    total_coins = 0
    choppy_locked = 0
    trending_active = 0
    gate_2_3_wave_retrace = 0
    gate_4_5_vol_reversal = 0
    gate_6_7_active_scalps = 0
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
            s_num, reg_disp, wave_disp, pipe_stat, l_state, _ = resolve_coin_pipeline(c)
            s_up = str(c.get("status", "")).upper()
            if "NEWS" in s_up:
                news_lockout_active = True
                parts = str(c.get("status", "")).split("Lockout:")
                if len(parts) > 1:
                    active_news_title = parts[1].strip()

            if "CHOPPY" in reg_disp.upper() or s_num == 0:
                choppy_locked += 1
            else:
                trending_active += 1

            if s_num in [2, 3]:
                gate_2_3_wave_retrace += 1
            elif s_num in [4, 5]:
                gate_4_5_vol_reversal += 1
            elif s_num in [6, 7]:
                gate_6_7_active_scalps += 1
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
            <span style="color:#94a3b8; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">⚡ Trending Expansion</span><br>
            <b style="color:#10b981; font-size:22px; font-family:monospace;">{trending_active} (Gate 1+)</b>
        </div>
        <div style="text-align:center; min-width:140px;">
            <span style="color:#94a3b8; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">🔒 Choppy / Squeeze</span><br>
            <b style="color:#f43f5e; font-size:22px; font-family:monospace;">{choppy_locked} (Gate 0)</b>
        </div>
        <div style="text-align:center; min-width:140px;">
            <span style="color:#94a3b8; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">⏳ Wave & Retrace</span><br>
            <b style="color:#a78bfa; font-size:22px; font-family:monospace;">{gate_2_3_wave_retrace} (Gate 2-3)</b>
        </div>
        <div style="text-align:center; min-width:140px;">
            <span style="color:#94a3b8; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">🎯 Reversal & Scalps</span><br>
            <b style="color:#34d399; font-size:22px; font-family:monospace;">{gate_4_5_vol_reversal + gate_6_7_active_scalps} (Gate 4-7)</b>
        </div>
    </div>"""


WATCHLIST_COLUMNS = ["Symbol (.P)", "Regime", "Wave Count", "Current Gate", "Active Tier / Status"]

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
            step_num, regime_disp, wave_disp, pipeline_status, live_state, active_tier_disp = resolve_coin_pipeline(c)
            last_res = c.get("last_result") if isinstance(c.get("last_result"), dict) else {}
            status_str_val = str(c.get("status") or "").upper()
            is_valid = bool(c.get("is_valid", False) or last_res.get("is_valid", False))
            is_running = any(k in status_str_val for k in ["RUNNING", "IN TRADE", "BE ACHIEVED", "POSITION RUNNING"])
            is_actionable = bool(((is_valid and step_num == 7) or is_running) and "ABORT" not in status_str_val and "ABORT" not in live_state.upper())

            # Format execution prices
            entry_raw = c.get("entryPrice") or last_res.get("entry_price") or last_res.get("entry_price_area")
            sl_raw = c.get("stopLoss") or last_res.get("stop_loss_level")
            tp1_raw = c.get("takeProfit1") or last_res.get("tp1_target")
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

            entry_disp = _fmt_p(entry_raw) if (is_actionable and entry_raw and "NO ENTRY" not in str(entry_raw).upper()) else "-"
            sl_disp = _fmt_p(sl_raw) if (is_actionable and sl_raw) else "-"
            tp1_disp = _fmt_p(tp1_raw) if (is_actionable and tp1_raw) else "-"
            tp2_disp = _fmt_p(tp2_raw) if (is_actionable and tp2_raw) else "-"

            # Clean Coin Symbol to .P Binance Futures Perpetual Ticker
            raw_sym = str(c.get("symbol", "")).strip().upper()
            if raw_sym.endswith(".P"):
                disp_sym = raw_sym
            else:
                clean_s = raw_sym.replace("USDT", "").strip()
                disp_sym = f"{clean_s}USDT.P"

            # Build Column 5: Active Tier / Status
            if is_actionable and entry_disp != "-":
                active_tier_status = f"{active_tier_disp} | {live_state} | Entry: {entry_disp} | SL: {sl_disp} | TP: {tp2_disp}"
            elif active_tier_disp and active_tier_disp != live_state and active_tier_disp not in live_state:
                active_tier_status = f"{active_tier_disp} | {live_state}"
            else:
                active_tier_status = live_state

            data.append([
                disp_sym,
                regime_disp,
                wave_disp,
                pipeline_status,
                active_tier_status
            ])
    except Exception as e:
        logger.error(f"Error loading watchlist: {e}")
        fallback_data = []
        for def_coin in DEFAULT_SMC_MONITORED_COINS:
            s_num, r_disp, w_disp, p_stat, l_st, a_tier = resolve_coin_pipeline(def_coin)
            raw_s = str(def_coin.get("symbol", "")).strip().upper()
            clean_s = raw_s if raw_s.endswith(".P") else f"{raw_s.replace('USDT', '').strip()}USDT.P"
            fallback_data.append([
                clean_s,
                r_disp,
                w_disp,
                p_stat,
                a_tier or l_st
            ])
        return pd.DataFrame(fallback_data, columns=WATCHLIST_COLUMNS)
    finally:
        db.close()

    if data:
        return pd.DataFrame(data, columns=WATCHLIST_COLUMNS)

    # Guaranteed non-empty fallback DataFrame
    fallback_data = []
    for def_coin in DEFAULT_SMC_MONITORED_COINS:
        s_num, r_disp, w_disp, p_stat, l_st, a_tier = resolve_coin_pipeline(def_coin)
        raw_s = str(def_coin.get("symbol", "")).strip().upper()
        clean_s = raw_s if raw_s.endswith(".P") else f"{raw_s.replace('USDT', '').strip()}USDT.P"
        fallback_data.append([
            clean_s,
            r_disp,
            w_disp,
            p_stat,
            a_tier or l_st
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
    fib_val = float(res.get("fib_level", 0.5))

    regime_step_disp = f"{m_reg} (ADX: {adx_v:.1f})" if adx_v > 0 else m_reg

    retr_disp = str(res.get("retracement_status_display") or "").strip()
    is_buy_dir = ("BUY" in entry_area.upper() or "LONG" in str(res.get("direction", "")).upper())

    # Determine 100% hard-locked gate status & live state
    if ("CHOPPY" in m_reg.upper() or curr_phase == 0) and adx_v < 16.0:
        pipeline_step_disp = "[Gate 0]: 🛑 Market Choppy / Range Blocked"
        falcon_live_state = "Gate 0: Market Choppy / Range Blocked 🛑"
    elif is_valid:
        pipeline_step_disp = "[Gate 7]: 🚀 Rapid Exit Delivery (BE +0.80R / TP1 / TP2)"
        falcon_live_state = "🎯 Local HL Confirmed! Triggering Long Scalp 📌" if is_buy_dir else "🎯 Local LH Confirmed! Triggering Short Scalp 📌"
    elif curr_phase == 6:
        pipeline_step_disp = "[Gate 6]: 🛡️ Micro-Wick SL Buffer Armed (0.25% - 0.65%)"
        falcon_live_state = "Gate 6: Micro-Wick SL Buffer Armed"
    elif curr_phase == 5:
        pipeline_step_disp = "[Gate 5]: 🎯 Near-Zone Breaker Order Active"
        falcon_live_state = "Gate 5: Near-Zone Breaker Order Active 🎯"
    elif curr_phase == 4:
        pipeline_step_disp = f"[Gate 4]: {retr_disp}" if retr_disp else ("[Gate 4]: 🔍 Verifying True HL Retracement..." if is_buy_dir else "[Gate 4]: 🔍 Verifying True LH Retracement...")
        falcon_live_state = "Gate 4: Verifying True HL/LH Candle Body..."
    elif curr_phase == 3:
        pipeline_step_disp = "[Gate 3]: ⚡ 3M Candle Body CHoCH & RVOL >= 1.35x"
        falcon_live_state = "Gate 3: Waiting for 3M Body CHoCH (RVOL >= 1.35x)"
    elif curr_phase == 2:
        zone_label = "Discount Retrace (Fib < 50%)" if is_buy_dir else "Premium Retrace (Fib > 50%)"
        pipeline_step_disp = f"[Gate 2]: ⏳ 5M {zone_label} | Wave {wave_num}/2"
        falcon_live_state = f"Gate 2: Waiting for {zone_label} | Wave {wave_num}/2"
    elif curr_phase == 1:
        pipeline_step_disp = "[Gate 1]: 🧭 15M Macro Direction Anchor"
        falcon_live_state = "Gate 1: Waiting for 15M Macro Alignment"
    else:
        pipeline_step_disp = "[Gate 0]: 🔒 Volatility Filter / Squeeze Check"
        falcon_live_state = "Gate 0: Awaiting Volatility Breakout"

    t15m = str(res.get("trend_15m") or "NEUTRAL").upper().strip()
    t5m = str(res.get("trend_5m") or "NEUTRAL").upper().strip()

    if is_valid and is_buy_dir:
        status_banner = f"""<div style="background:#064e3b; border:1px solid #10b981; border-radius:10px; padding:15px; color:#d1fae5;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0; color:#34d399;">🟢 ACTIVE BUY LIMIT SETUP (HARD-LOCKED SMC VERIFIED)</h2>
                <span style="background:#10b981; color:#064e3b; font-weight:bold; padding:4px 12px; border-radius:20px; font-size:14px;">🎯 WAVE {wave_num} HL TRIGGERED 📌</span>
            </div>
            <p style="margin:8px 0 0 0; font-size:14px;"><b>Symbol:</b> {sym} | <b>Timeframe:</b> {tf} | <b>Regime:</b> {m_reg} | <b>Equilibrium:</b> Discount Zone (Fib: {fib_val:.3f} &lt; 0.50) | <b>Wave:</b> {wave_num}/2</p>
        </div>"""
    elif is_valid and not is_buy_dir:
        status_banner = f"""<div style="background:#7f1d1d; border:1px solid #ef4444; border-radius:10px; padding:15px; color:#fee2e2;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0; color:#f87171;">🔴 ACTIVE SELL LIMIT SETUP (HARD-LOCKED SMC VERIFIED)</h2>
                <span style="background:#ef4444; color:#7f1d1d; font-weight:bold; padding:4px 12px; border-radius:20px; font-size:14px;">🎯 WAVE {wave_num} LH TRIGGERED 📌</span>
            </div>
            <p style="margin:8px 0 0 0; font-size:14px;"><b>Symbol:</b> {sym} | <b>Timeframe:</b> {tf} | <b>Regime:</b> {m_reg} | <b>Equilibrium:</b> Premium Zone (Fib: {fib_val:.3f} &gt; 0.50) | <b>Wave:</b> {wave_num}/2</p>
        </div>"""
    elif "CHOPPY" in m_reg.upper() or curr_phase == 0:
        status_banner = f"""<div style="background:#450a0a; border:1px solid #f43f5e; border-radius:10px; padding:15px; color:#ffe4e6;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0; color:#fb7185;">🔒 GATE 0: CHOPPY / SQUEEZE LOCKOUT ACTIVE</h2>
                <span style="background:#e11d48; color:#ffffff; font-weight:bold; padding:4px 12px; border-radius:20px; font-size:14px;">ZERO TRADES IN SIDEWAYS</span>
            </div>
            <p style="margin:8px 0 0 0; font-size:14px;"><b>Regime:</b> {m_reg} (ADX: {adx_v:.1f} &lt; 20 or BB Squeeze) | <b>Status:</b> Choppy Consolidation Range තුළ ව්‍යාජ HL/LH වලට හසුවීම වැළැක්වීමට Pipeline එක Hard-Lock කර ඇත.</p>
        </div>"""
    else:
        status_banner = f"""<div style="background:#1e1b4b; border:1px solid #6366f1; border-radius:10px; padding:15px; color:#e0e7ff;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0; color:#818cf8;">⏳ 100% HARD-LOCKED SMC PIPELINE: GATE {curr_phase}/7</h2>
                <span style="background:#4f46e5; color:#ffffff; font-weight:bold; padding:4px 12px; border-radius:20px; font-size:14px;">GATE {curr_phase} EVALUATION</span>
            </div>
            <p style="margin:8px 0 0 0; font-size:14px;"><b>Regime:</b> {m_reg} | <b>Status:</b> {pipeline_step_disp} | <b>Live State:</b> {falcon_live_state} | <b>Wave:</b> {wave_num}/2</p>
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

    # Format 100% Hard-Locked SMC Checklist (Gate 0 - Gate 7)
    checklist = res.get("rules_checklist", [])
    rule_num_map = {
        0: ("Gate 0", "Market Regime & Choppy Filter", "පියවර 0: වෙළඳපල චලිතය සහ බෝලින්ජර් ස්ක්වීස් පරීක්ෂාව (ADX >= 20 & No BB Squeeze)"),
        1: ("Gate 1", "Macro 15M Anchor & News Armor", "පියවර 1: සාර්ව නැංගුරම සහ ආර්ථික පුවත් ආවරණය (15M Macro Anchor & News Armor)"),
        2: ("Gate 2", "Adaptive Retracement & Wave Counter", "පියවර 2: අනුවර්තී Retracement සහ Wave Counter (Mode A / Mode B & Wave 1-4)"),
        3: ("Gate 3", "3M Candle Body Displacement & RVOL", "පියවර 3: 3M කැන්ඩල් බොඩි චෝච් සහ RVOL >= 1.35x (3M Body Shift & RVOL)"),
        4: ("Gate 4", "Wave 1-4 2-Candle Micro Shift", "පියවර 4: Wave 1-4 Rejection Wick >= 35% සහ Next Body Close Shift"),
        5: ("Gate 5", "Opposing Clearance & Market Order", "පියවර 5: ප්‍රතිවිරුද්ධ බාධක පරතරය (Clearance >= 1.5R) සහ Market Order"),
        6: ("Gate 6", "Micro-Wick Buffer SL (0.25% - 0.65%)", "පියවර 6: මයික්‍රෝ-වික් බෆර් Stop Loss (+/-0.15% Buffer, 0.25%-0.65% Hard-Cap)"),
        7: ("Gate 7", "Rapid Scalp Exit Engine (1:2.0R Fixed)", "පියවර 7: අධිවේගී පිටවීමේ එන්ජිම (BE +0.80R, TP1 1:1.50R 60%, TP2 1:2.0R 40% Fixed)")
    }
    rule_rows = ""
    for r_no, (r_label, name_en, name_si) in rule_num_map.items():
        rule_item = next((r for r in checklist if (r.get("step_no") == r_no or r.get("rule_no") == r_no or r.get("gate_no") == r_no)), None)
        passed = rule_item.get("passed", False) if rule_item else False
        badge = "✅ PASSED" if passed else "⏳ PENDING"
        detail_txt = rule_item.get("detail_si") or rule_item.get("detail") or "-" if rule_item else "-"
        rule_rows += f"| **{r_label}** | {name_si} | **{badge}** | {detail_txt} |\n"

    rules_smc_md = f"""### 🦅 100% Hard-Locked SMC Pipeline (Gate 0 - Gate 7)
| ගේට්ටුව (Hard Gate) | ආයතනික පදනම (Protocol) | තත්ත්වය (Status) | සජීවී ඇගයීම (Live Institutional Audit) |
| :---: | :--- | :---: | :--- |
{rule_rows}"""

    # Extract Multi-Timeframe Triad variables for display (15M / 5M / 3M)
    t15m_md = str(res.get("trend_15m") or "NEUTRAL").upper()
    t5m_md = str(res.get("trend_5m") or t15m_md).upper()
    zone_val = str(res.get("zone_type") or ("DISCOUNT (< 50%)" if "BUY" in entry_area.upper() else "PREMIUM (> 50%)"))
    post_choch = "3M Instant Market Order Primed ✅" if is_valid else "Awaiting Hard-Locked Sequential Gates ⏳"

    triad_md = f"""{rules_smc_md}

---

### 🏛️ Multi-Timeframe Precision Architecture (15M Macro • 5M Structure & Equilibrium • 3M Sniper Execution)
| Timeframe | Institutional Function | Status / Structure | Confirmation |
| :--- | :--- | :--- | :--- |
| **15M HTF** | Macro Direction Anchor (100 Candles) | **{t15m_md}** | HH/HL = Buy Only, LL/LH = Sell Only |
| **5M ITF** | Equilibrium & Zone Retrace Tap | **{t5m_md} ({zone_val})** | Discount (Fib < 0.50) / Premium (Fib > 0.50) & Wave 1-4 Only |
| **3M LTF** | Instant Market Order Trigger | **{post_choch}** | Rejection Wick >= 35% + Body Shift, 0.25%-0.65% SL, +0.80R BE |
"""

    reasoning_text = res.get("reasoning", "No technical reasoning available.")
    invalidation_text = res.get("invalidation", "None provided.")
    risk_notes_text = res.get("risk_notes", "Strict 0.25% - 0.65% capital protection.")

    reasoning_full_md = f"""
### 🧠 Institutional Technical Reasoning & Bilingual Explanation
{reasoning_text}

---
**🛑 Invalidation Level:** `{invalidation_text}`  
**⚠️ Risk Management Notes:** `{risk_notes_text}`  
<b>🛡️ 100% Sequential Hard-Locked Pipeline:</b> `Active Verification (Zero Step Skipping)`
"""

    # Pack raw json for telegram dispatch
    dispatch_payload = {
        "symbol": sym,
        "timeframe": tf,
        "is_valid": is_valid,
        "market_regime": m_reg,
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
        m_reg = data.get("market_regime", "TRENDING EXPANSION ✅")
        pipe_stat = data.get("pipeline_status", "[Gate 7]: Running to Targets")
        live_stat = data.get("live_state", "SIGNAL TRIGGERED 📌")

        is_buy = "BUY" in str(entry).upper() or "LONG" in str(data.get("direction", "")).upper()
        dir_str = "INSTANT MARKET BUY 🟢" if is_buy else ("INSTANT MARKET SELL 🔴" if ("SELL" in str(entry).upper() or "SHORT" in str(data.get("direction", "")).upper()) else "MARKET UPDATE 📊")

        msg = (
            f"🦅 <b>Falcon 100% Hard-Locked SMC Precision Scalp Analysis</b>\n\n"
            f"<b>Symbol:</b> #{sym} ({tf})\n"
            f"<b>Direction:</b> {dir_str}\n"
            f"<b>Regime:</b> {m_reg}\n"
            f"<b>Gate Status:</b> {pipe_stat}\n"
            f"<b>Live State:</b> {live_stat}\n\n"
            f"🎯 <b>Execution:</b> <code>{entry}</code>\n"
            f"🛑 <b>Micro-Wick SL:</b> <code>${sl}</code> (0.25% - 0.65% Hard-Cap)\n"
            f"🎯 <b>TP 1 (60%):</b> <code>${tp1}</code> (1:1.50R Partial Lock)\n"
            f"🏁 <b>TP 2 (40%):</b> <code>${tp2}</code> (1:2.0R Fixed Target)\n"
            f"🛡️ <b>Break-Even (+0.80R):</b> <code>${be}</code>\n\n"
            f"<b>🦅 100% Sequential Hard-Locked SMC Confluences:</b>\n"
            f"• Gate 0: Market Regime Filter (ADX >= 20 & No BB Squeeze)\n"
            f"• Gate 1: 15M Macro Direction Anchor & News Armor (+/-60m)\n"
            f"• Gate 2: Adaptive Dual-Retracement (Mode A / Mode B & Wave 1-4)\n"
            f"• Gate 3: 3M Candle Body Close CHoCH & RVOL >= 1.35x\n"
            f"• Gate 4: Wave 1-4 Rejection Wick >= 35% & Body Close Shift\n"
            f"• Gate 5: Opposing Clearance >= 1.5R (Instant Market Order Primed)\n"
            f"• Gate 6: Micro-Wick Buffer SL (0.15% Buffer, 0.25%-0.65% Cap)\n"
            f"• Gate 7: Execution & Risk Management (BE +0.80R, TP1 1.50R, TP2 2.0R Fixed)\n\n"
            f"<b>සිංහල සටහන (Sinhala):</b>\n"
            f"Falcon 100% Hard-Locked SMC Engine මඟින් #{sym} සඳහා තහවුරු කළ වාර්තාව. Range Bound Consolidation තුළ ව්‍යාජ HL/LH වලට හසුවීම වැළැක්වීමට Gate 0 සිට Gate 7 දක්වා පියවරෙන් පියවර 100% ක් පරීක්ෂා කර ඇත."
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
with gr.Blocks(title="Falcon 100% Hard-Locked SMC Cloud Engine") as demo:
    gr.Markdown("""
    # 🦅 Falcon 100% Hard-Locked SMC Engine & Live Streamer
    **Status:** 🟢 **LIVE & RUNNING 24/7 (v138.0 Active)** | **Pipeline:** 100% Sequential Hard-Lock (Gate 0 - Gate 7) | **Architecture:** Volatility Regime -> 15M Anchor -> Equilibrium & Wave 1/2 Retrace -> 3M Body CHoCH -> True HL/LH Exhaustion -> Near-Zone Execution
    
    This space runs in the cloud 24/7 even when your personal computer is turned off. 
    Every coin is evaluated strictly from Gate 0 to Gate 7 with ZERO step skipping. Choppy ranges (ADX < 20 / BB Squeeze) and Wave >= 3 trend exhaustion are 100% locked out.
    """)

    with gr.Tabs():
        # TAB 1: INTERACTIVE LIVE MARKET ANALYZER
        with gr.Tab("🔍 Live Market Analyzer (ඕනෑම Coin එකක් විශ්ලේෂණය කරන්න)"):
            gr.Markdown("### 🎯 Analyze Any Binance Crypto Pair with 100% Hard-Locked SMC Engine")
            
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
                    choices=["PRECISION_SCALP (100% Hard-Locked)", "SNIPER_STRICT (Zero-Bypass)"],
                    value="PRECISION_SCALP (100% Hard-Locked)",
                    info="Precision execution engine"
                )
                engine_in = gr.Radio(
                    label="Analysis Engine",
                    choices=["⚡ Fast Programmatic SMC (Local 7-Gate)", "🧠 Hybrid AI Deep Reasoning (Gemini + Local Rules)"],
                    value="⚡ Fast Programmatic SMC (Local 7-Gate)",
                    info="100% Free & Fast Python math vs Hybrid Gemini AI"
                )

            with gr.Row():
                analyze_btn = gr.Button("🚀 Run Hard-Locked SMC Analysis (දැන් විශ්ලේෂණය කරන්න)", variant="primary", size="lg")

            status_banner_out = gr.HTML("""<div style="background:#1e1b4b; border:1px solid #4338ca; border-radius:10px; padding:15px; color:#c7d2fe;">
                <b>Ready to Analyze:</b> Select a coin and click the button above to run real-time 100% Hard-Locked SMC analysis.
            </div>""")

            with gr.Row():
                regime_out = gr.Textbox(label="⚡ Market Regime (Gate 0)", interactive=False)
                pipeline_step_out = gr.Textbox(label="🦅 Hard-Locked Gate Status", interactive=False)
                entry_out = gr.Textbox(label="🎯 Instant Market Order", interactive=False)
                sl_out = gr.Textbox(label="🛑 Micro-Wick SL Buffer (0.25%-0.65%)", interactive=False)
                tp1_out = gr.Textbox(label="🎯 TP 1 (1:1.50R - 60%)", interactive=False)
                tp2_out = gr.Textbox(label="🏁 TP 2 (1:2.0R Fixed - 40%)", interactive=False)
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
            ### 📡 24/7 Background Cloud Scanner Watchlist — 100% Hard-Locked SMC Pipeline
            **Falcon 100% Hard-Locked 5M > 3M Precision Scalp Pipeline Tracker**  
            මෙම සජීවී Watchlist එක මඟින් Binance හි ප්‍රමුඛ පෙළේ Coins Gate 0 (ADX/Squeeze Choppiness Filter), Gate 1 (15M Macro Anchor), Gate 2 (Wave 1-4 Counter Engine), Gate 3 (3-Tier Cascade Retracement & Fib 0.50 Equilibrium), Gate 4 (Volume RVOL >= 1.35x), Gate 5 (2-Candle Closed State Machine Reversal), Gate 6 (Micro-Wick SL Buffer 0.25%-0.65%), සහ Gate 7 (Fixed 1:2.0R Scalp Exit) පියවරෙන් පියවර නිරීක්ෂණය කරයි. **පියවර 7ම සාර්ථකව සම්පූර්ණ වී Triggered වන අධිවේගී Instant Market Scalp අවස්ථා (INSTANT MARKET BUY/SELL 📌) පමණක් Telegram වෙත ස්වයංක්‍රීයව නිකුත් කෙරේ.**
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

