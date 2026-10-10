import io
import math
import logging
import datetime
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

def _get_font(size: int, bold: bool = False):
    font_names = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()

def _format_price(val: float, ref_price: float) -> str:
    if ref_price < 0.0001:
        return f"{val:.7f}"
    elif ref_price < 0.01:
        return f"{val:.6f}"
    elif ref_price < 1.0:
        return f"{val:.4f}"
    elif ref_price < 100.0:
        return f"{val:.3f}"
    else:
        return f"{val:.2f}"

class ChartService:
    @staticmethod
    def _generate_with_pil(
        symbol: str,
        timeframe: str,
        candles: List[Dict[str, Any]],
        entry: float,
        sl: float,
        tp1: float,
        tp2: float,
        direction: str = "LONG",
        tp3: Optional[float] = None,
        key_levels: Optional[Dict[str, float]] = None
    ) -> Optional[bytes]:
        """
        Ultra-realistic TradingView Candlestick Chart Generator with Long/Short Position Tool.
        Replicates exact TradingView light theme, candlesticks, position tool shading, labels, and watermarks.
        """
        try:
            width = 1000
            height = 1100
            im = Image.new("RGBA", (width, height), (255, 255, 255, 255))
            draw = ImageDraw.Draw(im)

            font_header_sm = _get_font(12, bold=False)
            font_header_title = _get_font(14, bold=True)
            font_header_ohlc = _get_font(12, bold=False)
            font_watermark_lg = _get_font(34, bold=True)
            font_watermark_sm = _get_font(20, bold=True)
            font_badge = _get_font(12, bold=True)
            font_card_title = _get_font(12, bold=True)
            font_card_sub = _get_font(12, bold=False)
            font_academy = _get_font(13, bold=True)
            font_axis = _get_font(11, bold=False)
            font_axis_badge = _get_font(11, bold=True)

            left_m = 40
            right_m = 135
            top_m = 90
            vol_h = 130
            time_h = 40
            bottom_m = vol_h + time_h
            chart_w = width - left_m - right_m
            chart_h = height - top_m - bottom_m
            vol_top = top_m + chart_h

            clean_sym = symbol.replace("BINANCE:", "").replace("USDT.P", "").replace("USDT", "").replace("/", "").upper()
            is_long = "BUY" in direction.upper() or "LONG" in direction.upper()

            # Ensure valid trade parameters
            entry = float(entry)
            sl = float(sl)
            tp1 = float(tp1) if tp1 else (entry + abs(entry - sl) * 1.5 if is_long else entry - abs(entry - sl) * 1.5)
            tp2 = float(tp2) if tp2 else (entry + abs(entry - sl) * 3.0 if is_long else entry - abs(entry - sl) * 3.0)

            # Prevent zero or inverted SL crashes
            if abs(entry - sl) < 1e-8:
                sl = entry * 0.997 if is_long else entry * 1.003

            recent = [dict(c) for c in (candles[-45:] if len(candles) >= 45 else candles)]
            if recent:
                recent[-1]["close"] = entry
                recent[-1]["high"] = max(float(recent[-1].get("high", entry)), entry)
                recent[-1]["low"] = min(float(recent[-1].get("low", entry)), entry)
            highs = [float(c["high"]) for c in recent if float(c.get("high", 0)) > 0]
            lows = [float(c["low"]) for c in recent if float(c.get("low", 0)) > 0]
            trade_prices = [p for p in [entry, sl, tp1, tp2] if p and p > 0]
            all_p = highs + lows + trade_prices
            raw_min = min(all_p) if all_p else entry * 0.99
            raw_max = max(all_p) if all_p else entry * 1.01
            p_span = max(raw_max - raw_min, entry * 0.005)

            # 15% top & bottom padding so candles & trade levels have breathing room
            min_p = raw_min - (p_span * 0.15)
            max_p = raw_max + (p_span * 0.15)
            price_rng = max(max_p - min_p, 1e-8)

            def y_px(p: float) -> int:
                return int(top_m + chart_h - ((p - min_p) / price_rng) * chart_h)

            # Top Header
            now_str = datetime.datetime.now().strftime("%b %d, %Y %H:%M UTC+5:30")
            draw.text((left_m, 15), f"FalconSMC created with TradingView.com, {now_str}", fill="#787B86", font=font_header_sm)
            draw.text((left_m, 36), f"{clean_sym} / TetherUS PERPETUAL CONTRACT • {timeframe} • Binance", fill="#131722", font=font_header_title)

            last_c = recent[-1] if recent else {"open": entry, "high": entry, "low": entry, "close": entry}
            c_open = float(last_c.get("open", entry))
            c_high = float(last_c.get("high", entry))
            c_low = float(last_c.get("low", entry))
            c_close = float(last_c.get("close", entry))
            diff = c_close - c_open
            diff_pct = (diff / c_open * 100) if c_open > 0 else 0
            diff_sign = "+" if diff >= 0 else ""
            diff_col = "#089981" if diff >= 0 else "#F23645"

            o_str = _format_price(c_open, entry)
            h_str = _format_price(c_high, entry)
            l_str = _format_price(c_low, entry)
            cl_str = _format_price(c_close, entry)
            d_str = _format_price(diff, entry)

            draw.text((left_m, 60), f"O: {o_str}  H: {h_str}  L: {l_str}  C: {cl_str}  ", fill="#787B86", font=font_header_ohlc)
            ohlc_w = draw.textlength(f"O: {o_str}  H: {h_str}  L: {l_str}  C: {cl_str}  ", font=font_header_ohlc)
            draw.text((left_m + ohlc_w, 60), f"{diff_sign}{d_str} ({diff_sign}{diff_pct:.2f}%)", fill=diff_col, font=font_header_ohlc)

            # Grid Lines
            for i in range(8):
                py = top_m + int(chart_h * (i / 7.0))
                draw.line([(left_m, py), (width - right_m, py)], fill="#F0F3F6", width=1)
                tick_val = max_p - (i / 7.0) * price_rng
                draw.text((width - right_m + 8, py - 6), _format_price(tick_val, entry), fill="#787B86", font=font_axis)

            for i in range(6):
                vx = left_m + int(chart_w * (i / 5.0))
                draw.line([(vx, top_m), (vx, vol_top + vol_h)], fill="#F0F3F6", width=1)

            # Center Watermark
            wm_text1 = f"{clean_sym}USDT.P, {timeframe}"
            wm_text2 = f"{clean_sym} / TetherUS PERPETUAL CONTRACT"
            wm1_w = draw.textlength(wm_text1, font=font_watermark_lg)
            wm2_w = draw.textlength(wm_text2, font=font_watermark_sm)
            wm_cx = left_m + (chart_w // 2)
            wm_cy = top_m + (chart_h // 2)
            draw.text((wm_cx - (wm1_w // 2), wm_cy - 30), wm_text1, fill="#F1F3F6", font=font_watermark_lg)
            draw.text((wm_cx - (wm2_w // 2), wm_cy + 15), wm_text2, fill="#F4F6F8", font=font_watermark_sm)

            # Slot allocation: past candles occupy left, position tool projects 16 bars to the right
            n_candles = len(recent)
            total_slots = n_candles + 16
            slot_w = chart_w / max(total_slots, 25)
            candle_w = max(4, int(slot_w * 0.7))

            xs = []
            closes_px = []
            for idx, c in enumerate(recent):
                cx = left_m + int(idx * slot_w) + int(slot_w // 2)
                xs.append(cx)
                op = y_px(float(c.get("open", entry)))
                cp = y_px(float(c.get("close", entry)))
                hp = y_px(float(c.get("high", entry)))
                lp = y_px(float(c.get("low", entry)))
                closes_px.append(cp)

                col = "#089981" if float(c.get("close", entry)) >= float(c.get("open", entry)) else "#F23645"
                draw.line([(cx, hp), (cx, lp)], fill=col, width=1)
                top_y = min(op, cp)
                bot_y = max(op, cp)
                if bot_y == top_y:
                    bot_y += 1
                draw.rectangle([cx - (candle_w // 2), top_y, cx + (candle_w // 2), bot_y], fill=col, outline=col)

            # Smooth EMA Lines (Blue 9 EMA and Orange 21 EMA)
            if len(closes_px) >= 5:
                b_pts = [(xs[i], sum(closes_px[max(0, i-4):i+1]) / len(closes_px[max(0, i-4):i+1])) for i in range(len(closes_px))]
                o_pts = [(xs[i], sum(closes_px[max(0, i-11):i+1]) / len(closes_px[max(0, i-11):i+1])) for i in range(len(closes_px))]
                for i in range(len(b_pts) - 1):
                    draw.line([b_pts[i], b_pts[i+1]], fill="#2962FF", width=2)
                    draw.line([o_pts[i], o_pts[i+1]], fill="#FF9800", width=2)

            # Dotted Swing Levels on chart
            if len(recent) >= 10:
                local_low = min(float(c.get("low", entry)) for c in recent[-15:])
                local_high = max(float(c.get("high", entry)) for c in recent[-15:])
                ly = y_px(local_low)
                hy = y_px(local_high)
                for dx in range(left_m, int(left_m + chart_w * 0.4), 8):
                    draw.line([(dx, ly), (dx + 4, ly)], fill="#089981", width=1)
                    draw.line([(dx, hy), (dx + 4, hy)], fill="#089981", width=1)

            # ==========================================
            # TRADINGVIEW LONG / SHORT POSITION TOOL
            # ==========================================
            pos_x1 = xs[-1] if xs else (left_m + int(chart_w * 0.6))
            pos_x2 = width - right_m - 10

            ey = y_px(entry)
            sly = y_px(sl)
            tp1y = y_px(tp1)
            tp2y = y_px(tp2)

            overlay = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            ov_draw = ImageDraw.Draw(overlay)

            if is_long:
                top_green, bot_green = min(ey, tp2y), max(ey, tp2y)
                top_red, bot_red = min(ey, sly), max(ey, sly)
                ov_draw.rectangle([pos_x1, top_green, pos_x2, bot_green], fill=(8, 153, 129, 45), outline=(8, 153, 129, 255), width=2)
                ov_draw.rectangle([pos_x1, top_red, pos_x2, bot_red], fill=(242, 54, 69, 45), outline=(242, 54, 69, 255), width=2)
            else:
                top_red, bot_red = min(ey, sly), max(ey, sly)
                top_green, bot_green = min(ey, tp2y), max(ey, tp2y)
                ov_draw.rectangle([pos_x1, top_red, pos_x2, bot_red], fill=(242, 54, 69, 45), outline=(242, 54, 69, 255), width=2)
                ov_draw.rectangle([pos_x1, top_green, pos_x2, bot_green], fill=(8, 153, 129, 45), outline=(8, 153, 129, 255), width=2)

            im = Image.alpha_composite(im, overlay)
            draw = ImageDraw.Draw(im)

            # Corner anchor handles
            for hx in [pos_x1, pos_x2]:
                for hy in [ey, sly, tp2y]:
                    draw.rectangle([hx - 4, hy - 4, hx + 4, hy + 4], fill="#FFFFFF", outline="#2962FF", width=1)

            # Intermediate TP1 Dotted Line
            for dx in range(pos_x1, pos_x2, 6):
                draw.line([(dx, tp1y), (dx + 3, tp1y)], fill="#089981", width=1)

            # Entry Blue Line
            draw.line([(pos_x1, ey), (pos_x2, ey)], fill="#2962FF", width=2)

            # Badges on Position Tool Lines
            b_x = pos_x1 + 10
            tp2_lbl = f"TP2 (1:2): {_format_price(tp2, entry)}"
            tp2_w = draw.textlength(tp2_lbl, font=font_badge)
            tp2_box_top = (tp2y - 18) if is_long else tp2y
            draw.rectangle([b_x, tp2_box_top, b_x + tp2_w + 14, tp2_box_top + 18], fill="#FFFFFF", outline="#089981", width=1)
            draw.text((b_x + 7, tp2_box_top + 2), tp2_lbl, fill="#089981", font=font_badge)

            tp1_lbl = f"TP1 (1:1): {_format_price(tp1, entry)}"
            tp1_w = draw.textlength(tp1_lbl, font=font_badge)
            draw.rectangle([b_x, tp1y - 18, b_x + tp1_w + 14, tp1y], fill="#FFFFFF", outline="#089981", width=1)
            draw.text((b_x + 7, tp1y - 16), tp1_lbl, fill="#089981", font=font_badge)

            entry_lbl = f"ENTRY: {_format_price(entry, entry)}"
            entry_w = draw.textlength(entry_lbl, font=font_badge)
            draw.rectangle([b_x, ey + 2, b_x + entry_w + 14, ey + 20], fill="#FFFFFF", outline="#2962FF", width=1)
            draw.text((b_x + 7, ey + 4), entry_lbl, fill="#2962FF", font=font_badge)

            sl_lbl = f"STOP LOSS: {_format_price(sl, entry)}"
            sl_w = draw.textlength(sl_lbl, font=font_badge)
            sl_box_top = sly if is_long else (sly - 18)
            draw.rectangle([b_x, sl_box_top, b_x + sl_w + 14, sl_box_top + 18], fill="#FFFFFF", outline="#F23645", width=1)
            draw.text((b_x + 7, sl_box_top + 2), sl_lbl, fill="#F23645", font=font_badge)

            # Target card inside Green Zone
            target_pct = (abs(tp2 - entry) / entry * 100) if entry > 0 else 0.0
            risk_val = abs(entry - sl)
            reward_val = abs(tp2 - entry)
            rr_ratio = (reward_val / risk_val) if risk_val > 0 else 2.0

            card_w = 210
            card_h = 38
            card_x = pos_x1 + ((pos_x2 - pos_x1) // 2) - (card_w // 2)
            card_y = (top_green + bot_green) // 2 - (card_h // 2)
            draw.rectangle([card_x, card_y, card_x + card_w, card_y + card_h], fill="#FFFFFF", outline="#A3D4C4", width=1)
            sign_t = "+" if is_long else "-"
            draw.text((card_x + 12, card_y + 4), f"Target: {_format_price(tp2, entry)} ({sign_t}{target_pct:.2f}%)", fill="#089981", font=font_card_title)
            draw.text((card_x + 12, card_y + 20), f"Risk/Reward: {rr_ratio:.2f}", fill="#2E3138", font=font_card_sub)

            # Watermark text inside Red Zone
            acad_line1 = "FALCON INSTITUTIONAL SMC"
            acad_line2 = "ACADEMY (PVT) LTD"
            acad_cx = pos_x1 + ((pos_x2 - pos_x1) // 2)
            mid_red_y = (top_red + bot_red) // 2
            draw.text((acad_cx - (draw.textlength(acad_line1, font=font_academy) // 2), mid_red_y - 16), acad_line1, fill="#EF5350", font=font_academy)
            draw.text((acad_cx - (draw.textlength(acad_line2, font=font_academy) // 2), mid_red_y + 2), acad_line2, fill="#EF5350", font=font_academy)

            # ==========================================
            # RIGHT PRICE SCALE ACTIVE PANEL & BADGES
            # ==========================================
            axis_x = width - right_m
            draw.line([(axis_x, top_m), (axis_x, vol_top + vol_h)], fill="#E0E3EB", width=1)

            # TP2 Active Badge (Green)
            draw.rectangle([axis_x, tp2y - 9, width - 15, tp2y + 9], fill="#089981")
            draw.text((axis_x + 6, tp2y - 6), _format_price(tp2, entry), fill="#FFFFFF", font=font_axis_badge)

            # Entry Active Badge (Blue with countdown timer 02:14)
            draw.rectangle([axis_x, ey - 9, width - 15, ey + 9], fill="#2962FF")
            draw.text((axis_x + 6, ey - 6), f"{_format_price(entry, entry)}  02:14", fill="#FFFFFF", font=font_axis_badge)

            # Stop Loss Active Badge (Red)
            draw.rectangle([axis_x, sly - 9, width - 15, sly + 9], fill="#F23645")
            draw.text((axis_x + 6, sly - 6), _format_price(sl, entry), fill="#FFFFFF", font=font_axis_badge)

            # ==========================================
            # BOTTOM VOLUME PANEL
            # ==========================================
            draw.line([(left_m, vol_top), (width - right_m, vol_top)], fill="#E0E3EB", width=1)

            vols = [float(c.get("volume", c.get("vol", 1000))) for c in recent]
            max_vol = max(vols) if vols else 1.0
            if max_vol <= 0:
                max_vol = 1.0

            for idx, c in enumerate(recent):
                cx = xs[idx]
                v_val = float(c.get("volume", c.get("vol", 1000)))
                v_h = int((v_val / max_vol) * (vol_h - 25))
                vy = vol_top + vol_h - v_h - 5

                col = "#A7D7C5" if float(c.get("close", entry)) >= float(c.get("open", entry)) else "#F8B4B8"
                half_w = max(2, candle_w // 2)
                draw.rectangle([cx - half_w, vy, cx + half_w, vol_top + vol_h - 5], fill=col)

            # Volume Axis Scale
            draw.text((axis_x + 8, vol_top + 15), f"{int(max_vol):,}", fill="#787B86", font=font_axis)
            draw.text((axis_x + 8, vol_top + 50), f"{int(max_vol * 0.5):,}", fill="#787B86", font=font_axis)
            draw.text((axis_x + 8, vol_top + 85), f"{int(max_vol * 0.2):,}", fill="#787B86", font=font_axis)

            # Time Axis Ticks
            time_y = vol_top + vol_h + 8
            draw.line([(left_m, vol_top + vol_h), (width - right_m, vol_top + vol_h)], fill="#E0E3EB", width=1)
            t_step = max(len(recent) // 6, 1)
            for i in range(0, len(recent), t_step):
                if i < len(xs):
                    tx = xs[i]
                    c_time = recent[i].get("time") or recent[i].get("close_time") or datetime.datetime.now()
                    if isinstance(c_time, (int, float)):
                        c_time = datetime.datetime.fromtimestamp(c_time / 1000 if c_time > 1e11 else c_time)
                    t_str = c_time.strftime("%H:%M") if hasattr(c_time, "strftime") else "00:00"
                    draw.text((tx - 15, time_y), t_str, fill="#787B86", font=font_axis)

            # Footer Branding
            draw.text((left_m, height - 25), "17 TradingView", fill="#131722", font=font_card_title)

            buf = io.BytesIO()
            im.convert("RGB").save(buf, format="PNG", optimize=True)
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Error in PIL TradingView chart rendering for {symbol}: {e}", exc_info=True)
            return None

    @classmethod
    def generate_smc_chart(
        cls,
        symbol: str,
        timeframe: str,
        klines: List[Any],
        entry: float,
        sl: float,
        tp1: float,
        tp2: float,
        direction: str = "LONG",
        tp3: Optional[float] = None,
        tp4: Optional[float] = None,
        tp5: Optional[float] = None,
        key_levels: Optional[Dict[str, float]] = None
    ) -> Optional[bytes]:
        """
        Generate an ultra-realistic TradingView screenshot replica matching user specifications.
        """
        recent = klines[-60:] if len(klines) >= 60 else klines
        if not recent:
            return None

        candles = []
        for k in recent:
            if isinstance(k, dict):
                t = k.get("close_time") or k.get("time") or datetime.datetime.now()
                if isinstance(t, (int, float)):
                    t = datetime.datetime.fromtimestamp(t / 1000.0 if t > 1e11 else t)
                candles.append({
                    "time": t if isinstance(t, datetime.datetime) else datetime.datetime.now(),
                    "open": float(k.get("open", 0)),
                    "high": float(k.get("high", 0)),
                    "low": float(k.get("low", 0)),
                    "close": float(k.get("close", 0)),
                    "volume": float(k.get("volume", k.get("vol", 1000))),
                })
            elif isinstance(k, (list, tuple)) and len(k) >= 6:
                ts = int(k[0])
                dt = datetime.datetime.fromtimestamp(ts / 1000.0 if ts > 1e11 else ts)
                candles.append({
                    "time": dt,
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                })

        if not candles:
            return None

        return cls._generate_with_pil(
            symbol=symbol,
            timeframe=timeframe,
            candles=candles,
            entry=entry,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            direction=direction,
            tp3=tp3,
            key_levels=key_levels
        )
