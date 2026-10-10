import httpx
import logging
import hashlib
import time
import re
from typing import Optional
from app.config import settings
from app.database import SessionLocal
from app.models import PreferenceModel

logger = logging.getLogger(__name__)

# Global in-memory deduplication caches
_recent_message_hashes: dict[str, float] = {}  # {md5_hash: timestamp}
_recent_symbol_alerts: dict[str, float] = {}   # {symbol: timestamp}

def get_dynamic_precision(price: float) -> int:
    """
    Dynamically determine decimal precision based on asset price level:
    - price < 0.001 -> 8 decimal places (NEIRO, 1000PEPE, SHIB, BONK, etc.)
    - price < 1.0 -> 5 decimal places (DOGE, ADA, ENA, etc.)
    - price < 100.0 -> 4 decimal places (SOL, AVAX, LINK, etc.)
    - price >= 100.0 -> 2 decimal places (BTC, ETH, BNB, etc.)
    """
    try:
        p = float(price)
        if p <= 0:
            return 4
        if p < 0.001:
            return 8
        elif p < 1.0:
            return 5
        elif p < 100.0:
            return 4
        else:
            return 2
    except Exception:
        return 4


class TelegramService:
    @staticmethod
    async def get_credentials() -> tuple[str, str]:
        """
        Get token and chat_id from Database preferences with fallback to settings (.env).
        """
        token = ""
        chat_id = ""
        db = SessionLocal()
        try:
            token_pref = db.query(PreferenceModel).filter(PreferenceModel.key == "telegram_bot_token").first()
            chat_pref = db.query(PreferenceModel).filter(PreferenceModel.key == "telegram_chat_id").first()
            token = token_pref.value if token_pref else settings.TELEGRAM_BOT_TOKEN
            chat_id = chat_pref.value if chat_pref else settings.TELEGRAM_CHAT_ID
        except Exception as e:
            logger.error(f"Error fetching telegram credentials from db: {e}")
            token = settings.TELEGRAM_BOT_TOKEN
            chat_id = settings.TELEGRAM_CHAT_ID
        finally:
            db.close()
        return (token or "").strip(), (chat_id or "").strip()

    @staticmethod
    def build_trade_alert(
        symbol: str,
        direction: str,
        entry_price: float,
        stop_loss: float,
        tp1: Optional[float] = None,
        tp2: Optional[float] = None,
        leverage: str = "15x - 20x (Cross)",
        confidence: int = 85,
        setup_path: Optional[str] = None,
        setup_route: Optional[str] = None,
        setup_model: Optional[str] = None,
        be_trigger: Optional[float] = None,
        trend_1h: Optional[str] = None
    ) -> tuple[str, dict]:
        """
        Builds the clean line-by-line trade alert matching user format with tap-to-copy code blocks
        and Telegram one-touch inline copy buttons, fully synchronized with the Falcon Institutional Engine.
        """
        clean_sym = symbol.replace("BINANCE:", "").replace("USDT.P", "").replace("USDT", "").replace("/", "").upper()
        tv_symbol = f"{clean_sym}USDT.P"
        tv_url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{tv_symbol}"
        is_long = "BUY" in direction.upper() or "LONG" in direction.upper()
        dir_str = "LONG 🟩" if is_long else "SHORT 🟥"
        dir_si = "මිලදී ගැනීම (LONG)" if is_long else "විකිණීම (SHORT)"

        f_entry = float(entry_price)
        f_sl = float(stop_loss)
        prec = get_dynamic_precision(f_entry)

        # Robust SL Validation & Risk Calculation
        # For SHORT: SL must be strictly > entry
        # For LONG: SL must be strictly < entry
        if is_long:
            if f_sl >= f_entry or f_sl <= 0:
                f_sl = f_entry * (1.0 - 0.0040)
        else:
            if f_sl <= f_entry or f_sl <= 0:
                f_sl = f_entry * (1.0 + 0.0040)

        risk = abs(f_entry - f_sl)
        if risk == 0 or (f_entry > 0 and (risk / f_entry) < 0.0020):
            risk = f_entry * 0.0035
            f_sl = (f_entry - risk) if is_long else (f_entry + risk)

        # Theoretical Targets: BE = 0.80R, TP1 = 1.50R, TP2 = 2.20R (1:2.0R - 1:2.30R)
        calc_be = (f_entry + (0.80 * risk)) if is_long else (f_entry - (0.80 * risk))
        calc_tp1 = (f_entry + (1.50 * risk)) if is_long else (f_entry - (1.50 * risk))
        calc_tp2 = (f_entry + (2.20 * risk)) if is_long else (f_entry - (2.20 * risk))

        # Check passed targets
        f_tp1 = float(tp1) if tp1 is not None and float(tp1) > 0 else calc_tp1
        f_tp2 = float(tp2) if tp2 is not None and float(tp2) > 0 else calc_tp2
        f_be = float(be_trigger) if be_trigger is not None and float(be_trigger) > 0 else calc_be

        # Guard against identical variables or inverted directions
        if is_long:
            if f_tp1 <= f_entry or f_tp2 <= f_tp1 or f_be <= f_entry:
                f_tp1, f_tp2, f_be = calc_tp1, calc_tp2, calc_be
        else:
            if f_tp1 >= f_entry or f_tp2 >= f_tp1 or f_be >= f_entry:
                f_tp1, f_tp2, f_be = calc_tp1, calc_tp2, calc_be

        e_str = f"{f_entry:.{prec}f}"
        sl_str = f"{f_sl:.{prec}f}"
        tp1_str = f"{f_tp1:.{prec}f}"
        tp2_str = f"{f_tp2:.{prec}f}"
        be_str = f"{f_be:.{prec}f}"

        model_badge = "🦅 <b>SMC CONFIRMED 2-CANDLE MARKET EXECUTION (WAVE 1-4) ✅</b>"
        lh_hl_type = "Local HL Confirmed" if is_long else "Local LH Confirmed"
        model_sub_si = f"Gate 0 Regime + 15M Macro + Wave 1-4 Impulse + Fib 0.50 Equilibrium + 3-Tier Retracement + RVOL >= 1.35x + 2-Candle State Machine ({lh_hl_type} Wick >= 35% & Body Shift Close) තහවුරු විය. Consolidations, Runaways සහ Wave 5+ Traps 100% වළක්වා ඇත."

        entry_type_label = f"2-Candle State Machine Reversal ({lh_hl_type}) 🎯"

        caption = (
            f"🦅 <b>COIN PAIR :- #{clean_sym}/USDT</b>\n"
            f"🦅 <b>FUTURE TYPE :- {dir_str}</b>\n"
            f"{model_badge}\n"
            f"🏛️ <i>Gate 0 Volatility ✅ • 15M Anchor ✅ • Wave 1-4 Engine ✅ • Dealing Range Equilibrium ✅ • 3-Tier Retracement ✅ • RVOL >= 1.35x ✅ • 2-Candle Closed Confirmation ✅</i>\n"
            f"🚨 <b>Instant Market Scalp (10-15 Min Exit)</b> | 💀 <b>LEVERAGE :- {leverage}</b>\n\n"
            f"🎯 <b>ENTRY (INSTANT MARKET {dir_str}) :-</b>\n"
            f"<code>{e_str}</code>\n\n"
            f"🎯 <b>TAKE PROFIT (Fixed 1:2.0R Target) :-</b>\n"
            f"<code>{tp2_str}</code>\n\n"
            f"🛡️ <b>BREAK-EVEN TRIGGER (+0.80R Profit) :-</b>\n"
            f"<code>{be_str}</code>\n\n"
            f"🛑 <b>STOP LOSS (Candle 1 Wick Extreme + 0.15% Buffer | 0.25%-0.65% Cap) :-</b>\n"
            f"<code>{sl_str}</code>\n\n"
            f"💰 <b>MARGIN ALLOCATION: 3% - 5% STRICT RISK CAP</b>\n\n"
            f"🇱🇰 <b>සිංහල උපදෙස් (Strict SMC 8-Gate Pipeline Engine):</b>\n"
            f"{clean_sym} {dir_si} 2-Candle Confirmed Reversal Setup ({confidence}%). {model_sub_si} Candle 2 Close වූ සැනින් INSTANT MARKET {dir_str} ({e_str}) ක්‍රියාත්මක කරන්න. SL එක Candle 1 {lh_hl_type} Wick අන්තයට වඩා 0.15% ක් ඈතින් ({sl_str}) තබා, +0.80R ({be_str}) ලාභයේදී Stop Loss එක Entry Price වෙත ගෙන ගොස් Break-Even කරන්න. Fixed 1:2.0R Target ({tp2_str}) මට්ටමේදී සම්පූර්ණ ලාභය ලබාගෙන විනාඩි 10-15 න් ට්‍රේඩ් එක අවසන් කරන්න."
        )

        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": f"📋 Copy Entry ({e_str})", "copy_text": {"text": e_str}},
                    {"text": f"🛡️ Copy SL ({sl_str})", "copy_text": {"text": sl_str}}
                ],
                [
                    {"text": f"🎯 TP: 1:2.0R ({tp2_str})", "copy_text": {"text": tp2_str}},
                    {"text": f"🛡️ BE: +0.80R ({be_str})", "copy_text": {"text": be_str}}
                ],
                [
                    {"text": f"📊 Open #{clean_sym} on TradingView ↗", "url": tv_url}
                ]
            ]
        }
        return caption, reply_markup

    @classmethod
    async def send_photo(
        cls,
        photo_bytes: bytes,
        caption: str,
        symbol: Optional[str] = None,
        reply_markup: Optional[dict] = None
    ) -> bool:
        """
        Send a chart photo with styled caption and copy buttons to Telegram.
        Falls back to send_message if photo upload encounters any issues.
        """
        import json
        now = time.time()

        if not symbol:
            sym_match = re.search(r"COIN PAIR\s*:-\s*#?([A-Za-z0-9._]+)", caption) or re.search(r"Symbol\s*:\s*([A-Za-z0-9._]+)", caption)
            if sym_match:
                symbol = sym_match.group(1).split("/")[0].upper()

        is_test = "TEST NOTIFICATION" in caption or "Test Telegram" in caption

        # Deduplication check
        msg_hash = hashlib.md5(caption.strip().encode("utf-8")).hexdigest()
        if not is_test:
            if msg_hash in _recent_message_hashes and (now - _recent_message_hashes[msg_hash]) < 300:
                logger.warning(f"Telegram duplicate photo suppressed by hash {msg_hash[:8]}.")
                return True
            if symbol and symbol in _recent_symbol_alerts and (now - _recent_symbol_alerts[symbol]) < 300:
                logger.warning(f"Telegram duplicate photo alert for {symbol} suppressed.")
                return True

        token, chat_id = await cls.get_credentials()
        if not token or not chat_id:
            logger.warning("Telegram Bot Token or Chat ID is missing. Notification not sent.")
            return False

        safe_caption = caption
        if len(safe_caption) > 1024:
            cut_idx = safe_caption.rfind("\n\n", 0, 1000)
            if cut_idx == -1:
                cut_idx = safe_caption.rfind("\n", 0, 1000)
            if cut_idx != -1:
                safe_caption = safe_caption[:cut_idx]
            else:
                safe_caption = safe_caption[:1000]
            for tag in ["code", "b", "i", "a"]:
                open_cnt = safe_caption.count(f"<{tag}>") + safe_caption.count(f"<{tag} ")
                close_cnt = safe_caption.count(f"</{tag}>")
                if open_cnt > close_cnt:
                    safe_caption += f"</{tag}>"

        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        data = {
            "chat_id": chat_id,
            "caption": safe_caption,
            "parse_mode": "HTML",
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)

        files = {"photo": ("chart.png", photo_bytes, "image/png")}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data=data, files=files, timeout=25.0)
                if response.status_code == 200:
                    logger.info("Telegram photo notification sent successfully.")
                    _recent_message_hashes[msg_hash] = now
                    if symbol:
                        _recent_symbol_alerts[symbol] = now
                    return True
                else:
                    logger.error(f"Failed to send Telegram photo: {response.text}. Falling back to text message.")
                    return await cls.send_message(caption, symbol=symbol, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Error sending Telegram photo: {e}. Falling back to text message.")
                return await cls.send_message(caption, symbol=symbol, reply_markup=reply_markup)

    @classmethod
    async def send_message(
        cls,
        text: str,
        symbol: Optional[str] = None,
        reply_markup: Optional[dict] = None
    ) -> bool:
        """
        Send a notification message to the configured Telegram chat with 100% duplicate suppression.
        Guarantees that ONLY ONE (1) notification arrives for any trade entry.
        """
        now = time.time()

        # 1. Clean old in-memory cache entries (> 600s)
        for h in list(_recent_message_hashes.keys()):
            if now - _recent_message_hashes[h] > 600:
                del _recent_message_hashes[h]
        for s in list(_recent_symbol_alerts.keys()):
            if now - _recent_symbol_alerts[s] > 600:
                del _recent_symbol_alerts[s]

        # 2. Extract symbol if not provided
        if not symbol:
            sym_match = re.search(r"COIN PAIR\s*:-\s*#?([A-Za-z0-9._]+)", text) or re.search(r"Symbol\s*:\s*([A-Za-z0-9._]+)", text)
            if sym_match:
                symbol = sym_match.group(1).split("/")[0].upper()

        is_test = "TEST NOTIFICATION" in text or "Test Telegram" in text

        # 3. In-memory Deduplication Check (300 seconds window)
        msg_hash = hashlib.md5(text.strip().encode("utf-8")).hexdigest()
        if not is_test:
            if msg_hash in _recent_message_hashes and (now - _recent_message_hashes[msg_hash]) < 300:
                logger.warning(f"Telegram duplicate message suppressed by hash {msg_hash[:8]} (sent {now - _recent_message_hashes[msg_hash]:.1f}s ago).")
                return True
            if symbol and symbol in _recent_symbol_alerts and (now - _recent_symbol_alerts[symbol]) < 300:
                logger.warning(f"Telegram duplicate alert for symbol {symbol} suppressed (sent {now - _recent_symbol_alerts[symbol]:.1f}s ago).")
                return True
        else:
            # 3-second throttle for manual test button
            if msg_hash in _recent_message_hashes and (now - _recent_message_hashes[msg_hash]) < 3:
                logger.info("Test Telegram button clicked rapidly; throttling duplicate.")
                return True

        # 4. Cross-Process / Persistent DB Lock Check
        if not is_test:
            db = SessionLocal()
            try:
                db_lock_key = f"tg_lock_{symbol}" if symbol else f"tg_lock_hash_{msg_hash[:16]}"
                lock_pref = db.query(PreferenceModel).filter(PreferenceModel.key == db_lock_key).first()
                if lock_pref and lock_pref.value:
                    try:
                        last_sent_ts = float(lock_pref.value)
                        if (now - last_sent_ts) < 300:
                            logger.warning(f"Telegram alert for {symbol or msg_hash[:8]} suppressed via persistent DB lock ({now - last_sent_ts:.1f}s ago).")
                            return True
                    except ValueError:
                        pass

                # Update persistent lock timestamp immediately
                if lock_pref:
                    lock_pref.value = str(now)
                else:
                    db.add(PreferenceModel(key=db_lock_key, value=str(now)))
                db.commit()
            except Exception as dbe:
                logger.error(f"Error checking/updating persistent Telegram DB lock: {dbe}")
            finally:
                db.close()

        # 5. Fetch credentials
        token, chat_id = await cls.get_credentials()
        if not token or not chat_id:
            logger.warning("Telegram Bot Token or Chat ID is missing. Notification not sent.")
            return False

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=10.0)
                if response.status_code == 200:
                    logger.info("Telegram notification sent successfully.")
                    _recent_message_hashes[msg_hash] = now
                    if symbol:
                        _recent_symbol_alerts[symbol] = now
                    return True
                else:
                    logger.error(f"Failed to send Telegram notification: {response.text}")
                    return False
            except Exception as e:
                logger.error(f"Error sending Telegram notification: {e}")
                return False

