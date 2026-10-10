"""
🦅 PURE DUAL-TIMEFRAME SMC CONFLUENCE ENGINE (5M & 3M SYMMETRIC)
Author: Falcon Institutional Engine (Clean-Slate Pure Mathematical State Machine)
Description: 100% pure mathematical SMC engine.
             Level 1: 15M Macro Structure Anchor (BULLISH -> BUY_ONLY, BEARISH -> SELL_ONLY).
             Level 2: 5M Structural Level & Wave Guard (Waves 1-4, BOS Invalidation, Breaker/FVG/Fib Tap).
             Level 3: 3M CHoCH (Change of Character Shift).
             Level 4: 3M Micro Wave & 3-Pathway Retracement (Waves 2 & 4 Only, Breaker/FVG/Fib).
             Level 5: 3M 2-Candle Reversal Market Execution (Wick >= 35%, Body Break, SL 0.15%, TP 1:2.0R).
"""

import math
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("pure_smc_engine")

PURE_SMC_STEPS = [
    {
        "step_no": 0,
        "title": "Level 0: Macro Wait / Neutral",
        "title_si": "පියවර 0: සාර්ව රැඳී සිටීම (Neutral Market)",
        "description": "15M Trend is Neutral or USD News Window active."
    },
    {
        "step_no": 1,
        "title": "Level 1: 15M Macro Structure Anchor",
        "title_si": "පියවර 1: 15M සාර්ව ව්‍යුහාත්මක නැංගුරම (15M Macro Structure Anchor)",
        "description": "15M Bullish Structure -> BUY_ONLY. 15M Bearish Structure -> SELL_ONLY. Counter-trend setups 100% Discarded."
    },
    {
        "step_no": 2,
        "title": "Level 2: 5M Structural Level & Wave Guard (Major HL / LH)",
        "title_si": "පියවර 2: 5M ව්‍යුහාත්මක කලාප සහ Wave පරීක්ෂාව (5M Breaker, FVG, Fib 0.50-0.786)",
        "description": "Track 5M Waves 1-4. Wave > 4 Hard Blocked. 5M HL/LH Break Invalidates setup. Price must tap 5M Breaker, FVG, or Fib 0.50-0.786."
    },
    {
        "step_no": 3,
        "title": "Level 3: 3M CHoCH (Change of Character Shift)",
        "title_si": "පියවර 3: 3M CHoCH ව්‍යුහාත්මක හැරීම (Change of Character Shift)",
        "description": "Post 5M Tap: 3M Lower High broken with Green Body close (BUY) or Higher Low broken with Red Body close (SELL)."
    },
    {
        "step_no": 4,
        "title": "Level 4: 3M Micro Wave & 3-Pathway Retracement (Sniper Entry)",
        "title_si": "පියවර 4: 3M Micro Wave 2/4 සහ 3-Pathway නැවත පැමිණීම (Breaker, FVG, Fib 0.50-0.618)",
        "description": "Wave 2 (1st HL/LH) or Wave 4 (2nd HL/LH) pullback taps 3M Breaker, 3M FVG, or 3M Fib 0.50-0.618. Wave >= 5 strictly Blocked."
    },
    {
        "step_no": 5,
        "title": "Level 5: 3M 2-Candle Reversal & Instant Market Execution",
        "title_si": "පියවර 5: ඉටිපන්දම් 2 ක වැසුණු හැරීම සහ ක්ෂණික වෙළඳපල නියෝගය (Wick >= 35%, Body Break, SL 0.15%, TP 1:2.0R)",
        "description": "Candle 1: Rejection Wick Ratio >= 35%. Candle 2: Next Body Break & Close. Color Guard Active. SL 0.15% beyond Wick, Fixed 1:2.0R TP."
    }
]


def get_dynamic_precision(price: float) -> int:
    """
    Dynamically determine decimal precision based on asset price level.
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


class FiveMinStructureResult(tuple):
    """
    Result container for 5M Structure & Wave Check.
    Supports unpacking as (five_min_structure_valid, five_min_wave).
    """
    def __new__(cls, valid: bool, wave: int, wave_label: str = "", has_level: bool = False, confluence: str = "", key_level: float = 0.0, msg: str = "", msg_si: str = ""):
        return super().__new__(cls, (valid, wave))

    def __init__(self, valid: bool, wave: int, wave_label: str = "", has_level: bool = False, confluence: str = "", key_level: float = 0.0, msg: str = "", msg_si: str = ""):
        self.valid = valid
        self.wave = wave
        self.wave_label = wave_label
        self.has_level = has_level
        self.confluence = confluence
        self.key_level = key_level
        self.msg = msg
        self.msg_si = msg_si


class ThreeMinWaveResult(int):
    """
    Result container for 3M Micro Wave Count.
    Behaves as an int so `three_min_wave in [2, 4]` works directly.
    """
    def __new__(cls, wave: int, wave_label: str = ""):
        return super().__new__(cls, wave)

    def __init__(self, wave: int, wave_label: str = ""):
        self.wave = wave
        self.wave_label = wave_label


class TwoCandleExecutionResult(tuple):
    """
    Result container for 2-Candle Execution check.
    Supports unpacking as (is_triggered, rejection_wick_extreme, trigger_entry_price, detail_en, detail_si).
    """
    def __new__(cls, is_triggered: bool, rej_wick_extreme: float, entry_price: float, detail_en: str = "", detail_si: str = ""):
        return super().__new__(cls, (is_triggered, rej_wick_extreme, entry_price, detail_en, detail_si))

    def __init__(self, is_triggered: bool, rej_wick_extreme: float, entry_price: float, detail_en: str = "", detail_si: str = ""):
        self.is_triggered = is_triggered
        self.rej_wick_extreme = rej_wick_extreme
        self.entry_price = entry_price
        self.detail_en = detail_en
        self.detail_si = detail_si


class PureSMCEngine:
    """
    Pure Mathematical Dual-Timeframe SMC State Machine Engine (5M & 3M Symmetric).
    """

    @classmethod
    def evaluate(
        cls,
        symbol: str,
        price: float,
        candles_15m: List[Dict[str, Any]],
        candles_5m: List[Dict[str, Any]],
        candles_3m: List[Dict[str, Any]],
        daily_open: Optional[float] = None,
        pdh: Optional[float] = None,
        pdl: Optional[float] = None,
        asian_high: Optional[float] = None,
        asian_low: Optional[float] = None,
        is_news_locked: bool = False,
        active_news_event: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute full pure SMC evaluation top-down across 15M, 5M, and 3M.
        """
        precision = get_dynamic_precision(price)
        evaluations: List[Dict[str, Any]] = []

        # =========================================================================
        # LEVEL 1: 15M MACRO STRUCTURE ANCHOR (FRACTALS / ZIGZAG)
        # =========================================================================
        news_block = bool(is_news_locked)
        news_ev_str = active_news_event or "USD High-Impact News (CPI/NFP/FOMC)"
        macro_structure, macro_seq, sh_15m, sl_15m = cls.check_15m_macro_structure(candles_15m, price)

        if macro_structure == "BULLISH":
            bias = "BUY_ONLY"
            is_buy_setup = True
            is_sell_setup = False
        elif macro_structure == "BEARISH":
            bias = "SELL_ONLY"
            is_buy_setup = False
            is_sell_setup = True
        else:
            bias = "NEUTRAL"
            is_buy_setup = False
            is_sell_setup = False

        level_1_passed = bool((bias in ["BUY_ONLY", "SELL_ONLY"]) and not news_block)

        if news_block:
            level_1_detail_en = f"Level 1 Blocked: USD High-Impact News Window active ({news_ev_str} +/-60 min). Signal Engine 100% OFF."
            level_1_detail_si = f"Level 1 අවහිරයි: USD ප්‍රධාන ආර්ථික පුවත් අවදානම සක්‍රීයයි ({news_ev_str}). Signal Engine 100% ක් අක්‍රිය කර ඇත."
        elif bias == "NEUTRAL":
            level_1_detail_en = "Level 1 Discarded: 15M Macro Structure is Neutral / Range-bound. No Directional Bias."
            level_1_detail_si = "Level 1 ඉවත් කරන ලදී: 15M Macro Structure එක Neutral/Chop තත්වයේ පවතී. පැහැදිලි Trend එකක් නැත."
        else:
            level_1_detail_en = f"Level 1 Verified: 15M Macro Structure is {macro_structure} ({macro_seq}). Bias locked to {bias}."
            level_1_detail_si = f"Level 1 තහවුරුයි: 15M Macro Structure එක {macro_structure} ({macro_seq}) වේ. අවසර දී ඇත්තේ {bias} පමණි."

        evaluations.append({
            "step_no": 1,
            "rule_no": 1,
            "gate_no": 1,
            "title": "Level 1: 15M Macro Structure Anchor",
            "title_si": "පියවර 1: 15M සාර්ව ව්‍යුහාත්මක නැංගුරම (15M Macro Structure Anchor)",
            "passed": level_1_passed,
            "status": "PASS" if level_1_passed else ("LOCKED" if news_block else "PENDING"),
            "detail": level_1_detail_en,
            "detail_si": level_1_detail_si
        })

        # =========================================================================
        # LEVEL 2: 5M STRUCTURAL SETUP & 3-PATHWAY CONFLUENCE (MAJOR HL / LH)
        # =========================================================================
        five_min_res = cls.check_5m_structure_and_waves(
            candles_5m=candles_5m,
            bias=bias,
            current_price=price
        )
        five_min_structure_valid, five_min_wave = five_min_res
        has_5m_level = five_min_res.has_level
        confluence_5m = five_min_res.confluence
        key_5m_level = five_min_res.key_level

        level_2_passed = False
        level_2_detail_en = ""
        level_2_detail_si = ""

        if not five_min_structure_valid:
            level_2_detail_en = "5M Structural Break Detected - Setup Invalidated 🛑"
            level_2_detail_si = "5M ව්‍යුහාත්මක බිඳවැටීමක් හඳුනාගෙන ඇත - Setup එක සම්පූර්ණයෙන්ම අවලංගුයි 🛑"
        elif five_min_wave > 4:
            level_2_detail_en = "5M Wave 5+ Exhaustion Blocked 🛑"
            level_2_detail_si = "5M Wave 5+ Exhaustion Trap - අවහිර කර ඇත 🛑"
        elif not has_5m_level:
            level_2_detail_en = "Level 2 Locked: Price has not tapped any of the 3 5M pathways (5M Breaker, 5M FVG, or 5M Golden Pocket Fib 0.50-0.786). No Trade."
            level_2_detail_si = "Level 2 අවහිරයි: මිල 5M මට්ටම් 3 න් එකක්වත් (5M Breaker, 5M FVG, හෝ 5M Golden Pocket Fib 0.50-0.786) ස්පර්ශ කර නැත. No Trade."
        else:
            level_2_passed = bool(level_1_passed and has_5m_level)
            level_2_detail_en = f"Level 2 Verified ({confluence_5m}): 5M Major Reversal Zone tapped at ${key_5m_level:.{precision}f} in {'Discount' if is_buy_setup else 'Premium'} (Wave {five_min_wave})."
            level_2_detail_si = f"Level 2 තහවුරුයි ({confluence_5m}): ප්‍රධාන 5M Reversal මට්ටම ${key_5m_level:.{precision}f} හිදී ස්පර්ශ විය (Wave {five_min_wave})."

        evaluations.append({
            "step_no": 2,
            "rule_no": 2,
            "gate_no": 2,
            "title": "Level 2: 5M Structural Level & Wave Guard (Major HL / LH)",
            "title_si": "පියවර 2: 5M ව්‍යුහාත්මක කලාප සහ Wave පරීක්ෂාව (5M Breaker, FVG, Fib 0.50-0.786)",
            "passed": level_2_passed,
            "status": "PASS" if level_2_passed else ("LOCKED" if (not five_min_structure_valid or five_min_wave > 4 or not level_1_passed) else "PENDING"),
            "detail": level_2_detail_en,
            "detail_si": level_2_detail_si
        })

        # =========================================================================
        # LEVEL 3: 3M CHOCH (CHANGE OF CHARACTER SHIFT)
        # =========================================================================
        choch_3m_ok = False
        reversal_sweep_wick = price
        choch_3m_level = price

        if level_2_passed:
            choch_3m_ok, reversal_sweep_wick, choch_3m_level = cls.check_3m_choch(
                candles_3m=candles_3m,
                bias=bias
            )

        level_3_passed = bool(level_2_passed and choch_3m_ok)
        if level_3_passed:
            level_3_detail_en = f"Level 3 Verified: 3M CHoCH Shift confirmed! {'Lower High broken with Green Body close' if is_buy_setup else 'Higher Low broken with Red Body close'} above/below ${choch_3m_level:.{precision}f}."
            level_3_detail_si = f"Level 3 තහවුරුයි: 3M CHoCH Shift එක සාර්ථකයි! {'LH මට්ටම බිඳ Green Body Close' if is_buy_setup else 'HL මට්ටම බිඳ Red Body Close'} (${choch_3m_level:.{precision}f}) තහවුරුයි."
        else:
            level_3_detail_en = f"Level 3 Pending: Awaiting 3M CHoCH Shift ({'Green Body close > LH' if is_buy_setup else 'Red Body close < HL'})."
            level_3_detail_si = f"Level 3 රැඳී සිටී: 3M CHoCH Shift එක බලාපොරොත්තුවෙන් ({'LH බිඳ Green Body' if is_buy_setup else 'HL බිඳ Red Body'})."

        evaluations.append({
            "step_no": 3,
            "rule_no": 3,
            "gate_no": 3,
            "title": "Level 3: 3M CHoCH (Change of Character Shift)",
            "title_si": "පියවර 3: 3M CHoCH ව්‍යුහාත්මක හැරීම (Change of Character Shift)",
            "passed": level_3_passed,
            "status": "PASS" if level_3_passed else ("LOCKED" if not level_2_passed else "PENDING"),
            "detail": level_3_detail_en,
            "detail_si": level_3_detail_si
        })

        # =========================================================================
        # LEVEL 4: 3M MICRO WAVE & 3-PATHWAY RETRACEMENT (SNIPER ENTRY)
        # =========================================================================
        three_min_wave = cls.get_3m_micro_wave_count(
            candles_3m=candles_3m,
            bias=bias,
            current_price=price
        )
        three_min_wave_lbl = getattr(three_min_wave, "wave_label", f"Wave {int(three_min_wave)}")
        wave_ok = bool(three_min_wave <= 4 and "5+" not in three_min_wave_lbl and "BLOCKED" not in three_min_wave_lbl.upper())
        is_pullback_wave = bool(three_min_wave in [2, 4])

        has_3m_micro = False
        confluence_3m = "None"
        level_3m_price = price

        if level_3_passed and wave_ok:
            has_3m_micro, confluence_3m, level_3m_price = cls.check_3m_pathways(
                candles_3m=candles_3m,
                bias=bias,
                current_price=price,
                choch_level=choch_3m_level
            )

        wave_3m_disp = "Wave 5+ (Blocked)" if not wave_ok else (
            f"{three_min_wave_lbl} ({confluence_3m})" if has_3m_micro else str(three_min_wave_lbl)
        )

        level_4_passed = bool(level_3_passed and wave_ok and is_pullback_wave and has_3m_micro)

        if not wave_ok:
            level_4_detail_en = f"Level 4 Blocked: {three_min_wave_lbl} Exhaustion Trap. Waves >= 5 are 100% strictly blocked."
            level_4_detail_si = f"Level 4 අවහිරයි: {three_min_wave_lbl} Exhaustion Trap. Wave >= 5 සඳහා Entries 100% ක් තහනම් වේ."
        elif not is_pullback_wave:
            target_wave = "Wave 2" if three_min_wave <= 1 else "Wave 4"
            level_4_detail_en = f"Level 4 Pending: Currently in {three_min_wave_lbl} Impulse. Awaiting {target_wave} Micro Pullback."
            level_4_detail_si = f"Level 4 රැඳී සිටී: දැනට පවතින්නේ {three_min_wave_lbl} වේගවත් චලනයකයි. {target_wave} Retracement එකක් බලාපොරොත්තුවෙන්."
        elif level_4_passed:
            level_4_detail_en = f"Level 4 Verified ({wave_3m_disp}): 5M & 3M Symmetric Agreement on {three_min_wave_lbl} at ${level_3m_price:.{precision}f}."
            level_4_detail_si = f"Level 4 තහවුරුයි ({wave_3m_disp}): 5M සහ 3M දෙකම {three_min_wave_lbl} මත එකඟ විය (${level_3m_price:.{precision}f})."
        else:
            level_4_detail_en = f"Level 4 Pending: {three_min_wave_lbl} Retracement awaiting tap on 3M Breaker, 3M FVG, or 3M Fib 0.50-0.618."
            level_4_detail_si = f"Level 4 රැඳී සිටී: {three_min_wave_lbl} Retracement 3M Breaker, FVG, හෝ Fib 0.50-0.618 ස්පර්ශය බලාපොරොත්තුවෙන්."

        evaluations.append({
            "step_no": 4,
            "rule_no": 4,
            "gate_no": 4,
            "title": "Level 4: 3M Micro Wave & 3-Pathway Retracement (Sniper Entry)",
            "title_si": "පියවර 4: 3M Micro Wave 2/4 සහ 3-Pathway නැවත පැමිණීම (Breaker, FVG, Fib 0.50-0.618)",
            "passed": level_4_passed,
            "status": "PASS" if level_4_passed else ("LOCKED" if (not wave_ok or not level_3_passed) else "PENDING"),
            "detail": level_4_detail_en,
            "detail_si": level_4_detail_si
        })

        # =========================================================================
        # LEVEL 5: 3M 2-CANDLE REVERSAL & INSTANT MARKET EXECUTION
        # =========================================================================
        is_triggered = False
        rej_wick_ext = price
        trig_entry = price
        trig_en = ""
        trig_si = ""

        if level_4_passed and is_pullback_wave:
            two_cand_res = cls.check_2_candle_execution(
                candles_3m=candles_3m,
                bias=bias,
                current_price=price
            )
            is_triggered, rej_wick_ext, trig_entry, trig_en, trig_si = two_cand_res

        level_5_passed = bool(level_4_passed and is_triggered)
        market_entry_price = trig_entry if level_5_passed else price

        sl_price = 0.0
        risk_pct = 0.0
        if level_5_passed and rej_wick_ext > 0:
            if is_buy_setup:
                sl_price = round(rej_wick_ext * (1.0 - 0.0015), precision)
            else:
                sl_price = round(rej_wick_ext * (1.0 + 0.0015), precision)
            risk_pct = abs(market_entry_price - sl_price) / market_entry_price

        be_trigger = 0.0
        tp1_target = 0.0
        tp2_target = 0.0
        if level_5_passed and sl_price > 0:
            r_val = abs(market_entry_price - sl_price)
            if is_buy_setup:
                be_trigger = round(market_entry_price + (0.80 * r_val), precision)
                tp1_target = round(market_entry_price + (1.50 * r_val), precision)
                tp2_target = round(market_entry_price + (2.00 * r_val), precision)
            else:
                be_trigger = round(market_entry_price - (0.80 * r_val), precision)
                tp1_target = round(market_entry_price - (1.50 * r_val), precision)
                tp2_target = round(market_entry_price - (2.00 * r_val), precision)

        if level_5_passed:
            level_5_detail_en = f"Level 5 Confirmed: {trig_en} Entry=${market_entry_price:.{precision}f}, SL=${sl_price:.{precision}f} (0.15% past wick), TP=${tp2_target:.{precision}f} (Fixed 1:2.0R)."
            level_5_detail_si = f"Level 5 තහවුරුයි: {trig_si} Entry=${market_entry_price:.{precision}f}, SL=${sl_price:.{precision}f} (Wick එකෙන් 0.15% එපිටින්), TP=${tp2_target:.{precision}f} (Fixed 1:2.0R)."
        else:
            level_5_detail_en = f"Level 5 Pending: {trig_en or 'Awaiting 3M Wick Rejection (>=35%) & Next Body Break'}"
            level_5_detail_si = f"Level 5 රැඳී සිටී: {trig_si or '3M Rejection Wick (>=35%) සහ Next Body Break බලාපොරොත්තුවෙන්'}"

        evaluations.append({
            "step_no": 5,
            "rule_no": 5,
            "gate_no": 5,
            "title": "Level 5: 3M 2-Candle Reversal & Instant Market Execution",
            "title_si": "පියවර 5: ඉටිපන්දම් 2 ක වැසුණු හැරීම සහ ක්ෂණික වෙළඳපල නියෝගය (Wick >= 35%, Body Break, SL 0.15%, TP 1:2.0R)",
            "passed": level_5_passed,
            "status": "PASS" if level_5_passed else ("LOCKED" if not level_4_passed else "PENDING"),
            "detail": level_5_detail_en,
            "detail_si": level_5_detail_si
        })

        # =========================================================================
        # DECISION ENGINE & STATE MACHINE STATUS
        # =========================================================================
        passed_count = sum(1 for e in evaluations if e["passed"])
        total_steps = len(evaluations)
        progress_pct = round((passed_count / total_steps) * 100)

        current_phase = 5 if level_5_passed else (
            4 if level_4_passed else (
                3 if level_3_passed else (
                    2 if level_2_passed else (
                        1 if level_1_passed else 0
                    )
                )
            )
        )

        curr_phase_meta = PURE_SMC_STEPS[min(current_phase, len(PURE_SMC_STEPS) - 1)]
        is_ready = bool(level_5_passed and passed_count == 5 and wave_ok and is_pullback_wave and five_min_structure_valid)

        if is_ready:
            confidence = 95
        elif current_phase == 4:
            confidence = 75
        elif current_phase == 3:
            confidence = 55
        elif current_phase == 2:
            confidence = 40
        elif current_phase == 1:
            confidence = 20
        else:
            confidence = 0

        # Construct Actionable / Awaiting / Blocked State Machine Status string
        if is_ready:
            act_str = "BUY" if is_buy_setup else "SELL"
            entry_area_str = f"INSTANT MARKET {act_str} at ${market_entry_price:.{precision}f} (2-Candle Reversal Confirmed)"
            state_status = f"🎯 {wave_3m_disp} Confirmed! INSTANT MARKET {act_str} Scalp 📌"
        elif news_block:
            entry_area_str = "No Entry (USD High-Impact News Lockout)"
            state_status = "Gate 1: Macro Wait / USD News Lockout 🛡️"
        elif not five_min_structure_valid:
            entry_area_str = "No Entry (5M Structural Break Detected - Setup Invalidated 🛑)"
            state_status = "5M Structural Break Detected - Setup Invalidated 🛑"
        elif five_min_wave > 4:
            entry_area_str = "No Entry (5M Wave 5+ Exhaustion Blocked 🛑)"
            state_status = "5M Wave 5+ Exhaustion Blocked 🛑"
        elif not wave_ok or three_min_wave > 4:
            entry_area_str = f"No Entry ({three_min_wave_lbl} Exhaustion Trap - Blocked 🛑)"
            state_status = f"Gate 2: {three_min_wave_lbl} Exhaustion - Blocked 🛑"
        elif current_phase == 0:
            entry_area_str = "No Entry (15M Macro Structure Neutral/Chop)"
            state_status = "Gate 0: 15M Macro Neutral / Chop"
        elif current_phase == 1:
            entry_area_str = f"Awaiting 5M Key Zone Tap ({macro_structure})"
            state_status = f"Gate 1: Awaiting 5M Key Zone Tap ({macro_structure})"
        elif current_phase == 2:
            entry_area_str = f"Awaiting 3M CHoCH Shift ({confluence_5m})"
            state_status = f"Gate 2: Awaiting 3M CHoCH Shift ({confluence_5m})"
        elif not is_pullback_wave:
            target_w = "Wave 2" if three_min_wave <= 1 else "Wave 4"
            entry_area_str = f"Awaiting {target_w} Micro Pullback ({three_min_wave_lbl} Impulse Active)"
            state_status = f"Gate 3: Awaiting {target_w} Micro Pullback"
        elif current_phase == 3:
            entry_area_str = f"Awaiting 3M Micro Confluence Retrace ({three_min_wave_lbl})"
            state_status = f"Gate 3: Retrace to 3M Confluence ({three_min_wave_lbl})"
        elif current_phase == 4:
            entry_area_str = "Awaiting 3M 2-Candle Reversal (Wick >= 35% & Body Break)"
            state_status = "Gate 4: 3M Wick Rejection (>=35%) & Next Body Close Shift..."
        else:
            entry_area_str = "Awaiting Multi-Timeframe Alignment"
            state_status = "Gate 1: Macro Wait / 15M Anchor"

        reasoning_eng = (
            f"🦅 **Pure Dual-Timeframe SMC Engine (5M & 3M Symmetric):**\n"
            f"• **Level 1 (15M Macro Anchor):** 15M Structure: {macro_structure} ({macro_seq}) -> Bias: {bias}.\n"
            f"• **Level 2 (5M Structural Level):** {confluence_5m} at ${key_5m_level:.{precision}f} ({'Discount' if is_buy_setup else 'Premium'}).\n"
            f"• **Level 3 (3M CHoCH Shift):** {'Confirmed' if level_3_passed else 'Pending'} at ${choch_3m_level:.{precision}f}.\n"
            f"• **Level 4 (3M Wave 1-4 Retracement):** {wave_3m_disp} ({'Allowed' if wave_ok else 'Exhaustion Blocked'}).\n"
            f"• **Level 5 (2-Candle Reversal & Execution):** {level_5_detail_en}."
        )

        reasoning_sin = (
            f"🦅 **පිරිසිදු ද්විත්ව කාලරාමු SMC අභිසාරී පද්ධතිය (5M සහ 3M සමමිතික):**\n"
            f"• **පියවර 1 (15M සාර්ව නැංගුරම):** 15M Macro දිශාව {macro_structure} වේ -> අවසරය: {bias}.\n"
            f"• **පියවර 2 (5M ව්‍යුහාත්මක කලාපය):** {confluence_5m} (${key_5m_level:.{precision}f}) ස්පර්ශ විය ({'Discount' if is_buy_setup else 'Premium'}).\n"
            f"• **පියවර 3 (3M CHoCH හැරීම):** {'තහවුරුයි' if level_3_passed else 'බලාපොරොත්තුවෙන්'} (${choch_3m_level:.{precision}f}).\n"
            f"• **පියවර 4 (3M Wave 1-4 ක්ෂුද්‍ර නැවත පැමිණීම):** {wave_3m_disp} ({'සක්‍රීයයි' if wave_ok else 'Wave 5+ අවහිරයි'}).\n"
            f"• **පියවර 5 (ඉටිපන්දම් 2 ක හැරීම සහ නියෝගය):** {level_5_detail_si}."
        )

        pipeline_phases = []
        for e in evaluations:
            pipeline_phases.append({
                "phase": e["step_no"],
                "gate_no": e["gate_no"],
                "name": e["title"],
                "name_si": e["title_si"],
                "passed": e["passed"],
                "status": e["status"],
                "detail": e["detail"],
                "detail_si": e["detail_si"]
            })

        pipeline_dict = {
            "pipeline_name": "PURE DUAL-TIMEFRAME SMC CONFLUENCE ENGINE (5M & 3M SYMMETRIC)",
            "current_phase": current_phase,
            "current_phase_name_en": curr_phase_meta["title"],
            "current_phase_name_si": curr_phase_meta["title_si"],
            "pipeline_progress_pct": progress_pct,
            "is_ready_for_execution": is_ready,
            "phases": pipeline_phases,
            "step_5_passed": level_5_passed,
            "step_7_passed": level_5_passed,
            "trend_15m": macro_structure,
            "bias": bias,
            "confluence_5m": confluence_5m,
            "wave_3m_level": wave_3m_disp,
            "wave_count": int(three_min_wave),
            "wave_label": three_min_wave_lbl,
            "five_min_structure_valid": five_min_structure_valid,
            "five_min_wave": five_min_wave,
            "three_min_wave": int(three_min_wave),
            "is_pullback_wave": is_pullback_wave,
            "key_5m_level": key_5m_level,
            "choch_3m_level": choch_3m_level,
            "reversal_sweep_wick": rej_wick_ext,
            "active_tier": confluence_5m,
            "active_tier_level": key_5m_level,
            "retracement_state": "CONFIRMED" if is_ready else "MONITORING",
            "retracement_status_display": state_status,
            "state_machine_status": state_status
        }

        return {
            "is_valid": is_ready,
            "confidence": confidence,
            "bias": bias,
            "direction": ("LONG" if is_buy_setup else ("SHORT" if is_sell_setup else "NEUTRAL")),
            "daily_bias": macro_structure,
            "trend_15m": macro_structure,
            "trend_5m": macro_structure,
            "trend_3m": ("BULLISH" if is_buy_setup and level_3_passed else ("BEARISH" if is_sell_setup and level_3_passed else "NEUTRAL")),
            "confluence_5m": confluence_5m,
            "wave_3m_level": wave_3m_disp,
            "wave_count": int(three_min_wave),
            "wave_label": three_min_wave_lbl,
            "five_min_structure_valid": five_min_structure_valid,
            "five_min_wave": five_min_wave,
            "three_min_wave": int(three_min_wave),
            "is_pullback_wave": is_pullback_wave,
            "timeframe": "3m",
            "entry_price_area": entry_area_str,
            "entry_price": market_entry_price if is_ready else None,
            "stop_loss_level": sl_price if is_ready else None,
            "tp1_target": tp1_target if is_ready else None,
            "tp2_target": tp2_target if is_ready else None,
            "tp3_target": None,
            "liquidity_target": tp1_target if is_ready else None,
            "breakeven_trigger": be_trigger if is_ready else None,
            "target_reward_ratio": "1:2.0R Fixed Target",
            "risk_pct": risk_pct if is_ready else 0.0,
            "current_phase": current_phase,
            "current_phase_name_en": curr_phase_meta["title"],
            "current_phase_name_si": curr_phase_meta["title_si"],
            "pipeline_progress_pct": progress_pct,
            "is_pipeline_ready": is_ready,
            "state_machine_status": state_status,
            "technical_reasoning": reasoning_eng,
            "technical_reasoning_sinhala": reasoning_sin,
            "reasoning": reasoning_eng,
            "reasoning_sinhala": reasoning_sin,
            "step_evaluations": evaluations,
            "pipeline": pipeline_dict
        }

    # =========================================================================
    # MATHEMATICAL HELPERS (FRACTALS, BOS, FVG, FIB)
    # =========================================================================

    @staticmethod
    def check_15m_macro_structure(
        candles_15m: List[Dict[str, Any]],
        current_price: float = 0.0
    ) -> Tuple[str, str, float, float]:
        """
        LEVEL 1: Pure Fractal / ZigZag Swing Structure Detector on 15M chart.
        Returns: (structure, seq, swing_high, swing_low)
        """
        if not candles_15m or len(candles_15m) < 8:
            return "NEUTRAL", "CONSOLIDATION", 0.0, 0.0

        highs = [float(c["high"]) for c in candles_15m]
        lows = [float(c["low"]) for c in candles_15m]
        closes = [float(c["close"]) for c in candles_15m]

        swing_high = max(highs)
        swing_low = min(lows)

        # Detect Fractal Swing Points (3-bar or 5-bar swing extremes)
        swing_highs = []
        swing_lows = []
        for i in range(2, len(candles_15m) - 2):
            if highs[i] >= highs[i-1] and highs[i] >= highs[i-2] and highs[i] >= highs[i+1] and highs[i] >= highs[i+2]:
                swing_highs.append(highs[i])
            if lows[i] <= lows[i-1] and lows[i] <= lows[i-2] and lows[i] <= lows[i+1] and lows[i] <= lows[i+2]:
                swing_lows.append(lows[i])

        is_hh_hl = False
        is_ll_lh = False
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            if swing_highs[-1] > swing_highs[-2] and swing_lows[-1] >= swing_lows[-2]:
                is_hh_hl = True
            elif swing_highs[-1] <= swing_highs[-2] and swing_lows[-1] < swing_lows[-2]:
                is_ll_lh = True

        current_close = closes[-1]
        mid_level = (swing_high + swing_low) / 2.0

        if is_hh_hl:
            return "BULLISH", "HH_HL", swing_high, swing_low
        elif is_ll_lh:
            return "BEARISH", "LL_LH", swing_high, swing_low
        elif current_close > mid_level and closes[-1] > closes[-5]:
            return "BULLISH", "HH_HL", swing_high, swing_low
        elif current_close < mid_level and closes[-1] < closes[-5]:
            return "BEARISH", "LL_LH", swing_high, swing_low
        else:
            return "NEUTRAL", "RANGE", swing_high, swing_low

    @classmethod
    def check_5m_structure_and_waves(
        cls,
        candles_5m: List[Dict[str, Any]],
        bias: str = "BUY_ONLY",
        current_price: float = 0.0
    ) -> FiveMinStructureResult:
        """
        LEVEL 2: 5M Structural Level & Wave Guard (Major HL / LH).
        - Track 5M Major Waves 1-4.
        - IF 5M Major Waves > 4: RETURN '5M Wave 5+ Exhaustion Blocked 🛑'.
        - IF Bias == 'BUY_ONLY' and 5M Low breaks below previous HL: INVALIDATE SETUP.
        - IF Bias == 'SELL_ONLY' and 5M High breaks above previous LH: INVALIDATE SETUP.
        - 5M 3-PATHWAY TAP:
          * Pathway A (Breaker): Retest of broken 5M swing structure.
          * Pathway B (FVG): Price taps 5M Fair Value Gap.
          * Pathway C (Fib): Price taps 5M Swing Fib 0.50 - 0.786 Discount (BUY) or Premium (SELL).
        """
        if not candles_5m or len(candles_5m) < 8:
            return FiveMinStructureResult(
                valid=False,
                wave=1,
                wave_label="Wave 1",
                has_level=False,
                confluence="Awaiting 5M Zone",
                key_level=0.0,
                msg="5M Structural Break Detected - Setup Invalidated 🛑",
                msg_si="5M ව්‍යුහාත්මක බිඳවැටීමක් හඳුනාගෙන ඇත - Setup එක සම්පූර්ණයෙන්ම අවලංගුයි 🛑"
            )

        highs = [float(c["high"]) for c in candles_5m]
        lows = [float(c["low"]) for c in candles_5m]
        closes = [float(c["close"]) for c in candles_5m]
        curr_p = float(current_price) if current_price > 0 else closes[-1]

        is_buy = (bias == "BUY_ONLY")

        # 1. Track 5M Major Waves 1-4
        five_min_wave, five_min_wave_lbl = cls.get_wave_structure(candles_5m, is_buy=is_buy, current_price=curr_p)

        # 2. Structural Break Invalidation (Bearish BOS on Buy, Bullish BOS on Sell)
        structure_valid = True
        msg = ""
        msg_si = ""

        lookback = min(len(candles_5m), 40)
        recent_highs = highs[-lookback:]
        recent_lows = lows[-lookback:]
        recent_closes = closes[-lookback:]

        prior_highs = recent_highs[:-3] if len(recent_highs) > 5 else recent_highs
        prior_lows = recent_lows[:-3] if len(recent_lows) > 5 else recent_lows

        if is_buy:
            swing_lows = []
            for i in range(2, len(prior_lows) - 2):
                if prior_lows[i] <= min(prior_lows[max(0, i-2):i]) and prior_lows[i] <= min(prior_lows[i+1:min(len(prior_lows), i+3)]):
                    swing_lows.append(prior_lows[i])
            valid_demand_sl = min(swing_lows) if swing_lows else (min(prior_lows) if prior_lows else curr_p * 0.99)
            if any(c_close < valid_demand_sl * 0.9995 for c_close in recent_closes[-3:]) or curr_p < valid_demand_sl * 0.9985:
                structure_valid = False
                msg = "5M Structural Break Detected - Setup Invalidated 🛑"
                msg_si = "5M ව්‍යුහාත්මක බිඳවැටීමක් හඳුනාගෙන ඇත - Setup එක සම්පූර්ණයෙන්ම අවලංගුයි 🛑"
        else:
            swing_highs = []
            for i in range(2, len(prior_highs) - 2):
                if prior_highs[i] >= max(prior_highs[max(0, i-2):i]) and prior_highs[i] >= max(prior_highs[i+1:min(len(prior_highs), i+3)]):
                    swing_highs.append(prior_highs[i])
            valid_supply_sh = max(swing_highs) if swing_highs else (max(prior_highs) if prior_highs else curr_p * 1.01)
            if any(c_close > valid_supply_sh * 1.0005 for c_close in recent_closes[-3:]) or curr_p > valid_supply_sh * 1.0015:
                structure_valid = False
                msg = "5M Structural Break Detected - Setup Invalidated 🛑"
                msg_si = "5M ව්‍යුහාත්මක බිඳවැටීමක් හඳුනාගෙන ඇත - Setup එක සම්පූර්ණයෙන්ම අවලංගුයි 🛑"

        # 3. 5M 3-Pathway Tap Required
        has_lvl, conf_5m, key_lvl = cls.check_5m_pathways(
            candles_5m=candles_5m,
            is_buy=is_buy,
            current_price=curr_p
        )

        if structure_valid and five_min_wave > 4:
            msg = "5M Wave 5+ Exhaustion Blocked 🛑"
            msg_si = "5M Wave 5+ Exhaustion Trap - අවහිර කර ඇත 🛑"

        return FiveMinStructureResult(
            valid=structure_valid,
            wave=five_min_wave,
            wave_label=five_min_wave_lbl,
            has_level=has_lvl,
            confluence=conf_5m,
            key_level=key_lvl,
            msg=msg,
            msg_si=msg_si
        )

    @classmethod
    def check_5m_pathways(
        cls,
        candles_5m: List[Dict[str, Any]],
        is_buy: bool,
        current_price: float
    ) -> Tuple[bool, str, float]:
        """
        LEVEL 2: 5M 3-Pathway Detection:
        - Pathway A (Breaker): Retest of broken 5M swing structure.
        - Pathway B (FVG): Price taps 5M Fair Value Gap.
        - Pathway C (Fib): Price taps 5M Swing Fib 0.50 - 0.786 Discount (BUY) or Premium (SELL).
        """
        if not candles_5m or len(candles_5m) < 8:
            return False, "Awaiting 5M Zone", 0.0

        n = len(candles_5m)
        lookback = min(n, 35)
        recent_5m = candles_5m[-lookback:]
        highs = [float(c["high"]) for c in recent_5m]
        lows = [float(c["low"]) for c in recent_5m]
        curr_p = float(current_price) if current_price > 0 else float(recent_5m[-1]["close"])

        pathway_hits = []
        key_levels = []

        # Pathway A: 5M Breaker Block Re-test
        breaker_tap = False
        breaker_lvl = 0.0
        if is_buy:
            for i in range(2, len(highs) - 5):
                if highs[i] >= max(highs[max(0, i-2):i]) and highs[i] > max(highs[i+1:min(len(highs), i+3)]):
                    cand_sh = highs[i]
                    if any(float(c["close"]) > cand_sh for c in recent_5m[i+1:-2]):
                        if (abs(curr_p - cand_sh) / cand_sh <= 0.0025) or any(abs(float(c["low"]) - cand_sh) / cand_sh <= 0.0025 for c in recent_5m[-6:]):
                            breaker_tap = True
                            breaker_lvl = cand_sh
                            break
        else:
            for i in range(2, len(lows) - 5):
                if lows[i] <= min(lows[max(0, i-2):i]) and lows[i] < min(lows[i+1:min(len(lows), i+3)]):
                    cand_sl = lows[i]
                    if any(float(c["close"]) < cand_sl for c in recent_5m[i+1:-2]):
                        if (abs(curr_p - cand_sl) / cand_sl <= 0.0025) or any(abs(float(c["high"]) - cand_sl) / cand_sl <= 0.0025 for c in recent_5m[-6:]):
                            breaker_tap = True
                            breaker_lvl = cand_sl
                            break

        if breaker_tap:
            pathway_hits.append("5M Breaker")
            key_levels.append(breaker_lvl)

        # Pathway B: 5M Fair Value Gap Tap
        fvg_tap = False
        fvg_lvl = 0.0
        for i in range(len(recent_5m) - 1, max(2, len(recent_5m) - 12), -1):
            c_now = recent_5m[i]
            c_prev2 = recent_5m[i-2]
            if is_buy:
                cur_low = float(c_now["low"])
                p2_high = float(c_prev2["high"])
                if cur_low > p2_high * 1.0001:
                    if (curr_p <= cur_low * 1.0010 and curr_p >= p2_high * 0.9990) or any(float(c["low"]) <= cur_low * 1.0010 and float(c["high"]) >= p2_high * 0.9990 for c in recent_5m[-6:]):
                        fvg_tap = True
                        fvg_lvl = (cur_low + p2_high) / 2.0
                        break
            else:
                cur_high = float(c_now["high"])
                p2_low = float(c_prev2["low"])
                if cur_high < p2_low * 0.9999:
                    if (curr_p >= cur_high * 0.9990 and curr_p <= p2_low * 1.0010) or any(float(c["high"]) >= cur_high * 0.9990 and float(c["low"]) <= p2_low * 1.0010 for c in recent_5m[-6:]):
                        fvg_tap = True
                        fvg_lvl = (cur_high + p2_low) / 2.0
                        break

        if fvg_tap:
            pathway_hits.append("5M FVG")
            key_levels.append(fvg_lvl)

        # Pathway C: 5M Golden Pocket Fib 0.50 - 0.786
        sh_5m = max(highs)
        sl_5m = min(lows)
        span = sh_5m - sl_5m
        if span > 0:
            if is_buy:
                depth = (sh_5m - curr_p) / span
                if 0.50 <= depth <= 0.786 or any(0.50 <= ((sh_5m - float(c["low"])) / span) <= 0.786 for c in recent_5m[-6:]):
                    fib_lvl = sl_5m + (span * 0.382)
                    fib_lbl = f"5M Fib {depth:.2f}" if 0.50 <= depth <= 0.786 else "5M Fib 0.618"
                    pathway_hits.append(fib_lbl)
                    key_levels.append(fib_lvl)
            else:
                depth = (curr_p - sl_5m) / span
                if 0.50 <= depth <= 0.786 or any(0.50 <= ((float(c["high"]) - sl_5m) / span) <= 0.786 for c in recent_5m[-6:]):
                    fib_lvl = sl_5m + (span * 0.618)
                    fib_lbl = f"5M Fib {depth:.2f}" if 0.50 <= depth <= 0.786 else "5M Fib 0.618"
                    pathway_hits.append(fib_lbl)
                    key_levels.append(fib_lvl)

        if pathway_hits:
            confluence_str = " + ".join(pathway_hits)
            best_lvl = key_levels[0] if key_levels else curr_p
            return True, confluence_str, best_lvl
        else:
            return False, "Awaiting 5M Zone", 0.0

    @staticmethod
    def check_3m_choch(
        candles_3m: List[Dict[str, Any]],
        bias: str = "BUY_ONLY"
    ) -> Tuple[bool, float, float]:
        """
        LEVEL 3: 3M CHoCH (Change of Character Structure Shift).
        - BUY: 3M closed green candle body > recent 3M Lower High (Bullish CHoCH).
        - SELL: 3M closed red candle body < recent 3M Higher Low (Bearish CHoCH).
        """
        if not candles_3m or len(candles_3m) < 6:
            return False, 0.0, 0.0

        recent_3m = candles_3m[-18:]
        highs = [float(c["high"]) for c in recent_3m]
        lows = [float(c["low"]) for c in recent_3m]
        is_buy = (bias == "BUY_ONLY")

        if is_buy:
            extreme_low = min(lows)
            mid = max(2, len(recent_3m) - 6)
            prior_highs = [float(c["high"]) for c in recent_3m[:mid]]
            lh_level = max(prior_highs) if prior_highs else highs[0]

            for c in recent_3m[mid:]:
                c_close = float(c["close"])
                c_open = float(c["open"])
                if c_close > lh_level and c_close > c_open:
                    return True, extreme_low, lh_level

            last_c = recent_3m[-1]
            if len(recent_3m) >= 4 and float(last_c["close"]) > float(recent_3m[-3]["high"]) and float(last_c["close"]) > float(last_c["open"]):
                return True, extreme_low, float(recent_3m[-3]["high"])

            return False, extreme_low, lh_level
        else:
            extreme_high = max(highs)
            mid = max(2, len(recent_3m) - 6)
            prior_lows = [float(c["low"]) for c in recent_3m[:mid]]
            hl_level = min(prior_lows) if prior_lows else lows[0]

            for c in recent_3m[mid:]:
                c_close = float(c["close"])
                c_open = float(c["open"])
                if c_close < hl_level and c_close < c_open:
                    return True, extreme_high, hl_level

            last_c = recent_3m[-1]
            if len(recent_3m) >= 4 and float(last_c["close"]) < float(recent_3m[-3]["low"]) and float(last_c["close"]) < float(last_c["open"]):
                return True, extreme_high, float(recent_3m[-3]["low"])

            return False, extreme_high, hl_level

    @classmethod
    def get_3m_micro_wave_count(
        cls,
        candles_3m: List[Dict[str, Any]],
        bias: str = "BUY_ONLY",
        current_price: float = 0.0
    ) -> ThreeMinWaveResult:
        """
        LEVEL 4: 3M Micro Wave Counter (Waves 1 to 5+).
        """
        is_buy = (bias == "BUY_ONLY")
        num, lbl = cls.get_wave_structure(candles_3m, is_buy=is_buy, current_price=current_price)
        return ThreeMinWaveResult(num, lbl)

    @classmethod
    def check_3m_pathways(
        cls,
        candles_3m: List[Dict[str, Any]],
        bias: str = "BUY_ONLY",
        current_price: float = 0.0,
        choch_level: float = 0.0
    ) -> Tuple[bool, str, float]:
        """
        LEVEL 4: 3M 3-Pathway Detection:
        - 3M Breaker Block
        - 3M Fair Value Gap
        - 3M Fib 0.50 - 0.618 Discount/Premium
        """
        if not candles_3m or len(candles_3m) < 6:
            return False, "None", 0.0

        recent_3m = candles_3m[-15:]
        curr_p = float(current_price) if current_price > 0 else float(recent_3m[-1]["close"])
        highs = [float(c["high"]) for c in recent_3m]
        lows = [float(c["low"]) for c in recent_3m]
        is_buy = (bias == "BUY_ONLY")

        m_hits = []
        m_lvls = []

        # 1. 3M Breaker Block Re-test
        breaker_tap_3m = False
        breaker_lvl_3m = 0.0
        if choch_level > 0 and ((abs(curr_p - choch_level) / choch_level <= 0.0025) or any(abs(float(c["low" if is_buy else "high"]) - choch_level) / choch_level <= 0.0025 for c in recent_3m[-5:])):
            breaker_tap_3m = True
            breaker_lvl_3m = choch_level
        else:
            if is_buy:
                for i in range(2, len(highs) - 3):
                    if highs[i] >= max(highs[max(0, i-2):i]) and highs[i] > max(highs[i+1:min(len(highs), i+3)]):
                        cand_sh = highs[i]
                        if any(float(c["close"]) > cand_sh for c in recent_3m[i+1:-1]):
                            if (abs(curr_p - cand_sh) / cand_sh <= 0.0025) or any(abs(float(c["low"]) - cand_sh) / cand_sh <= 0.0025 for c in recent_3m[-5:]):
                                breaker_tap_3m = True
                                breaker_lvl_3m = cand_sh
                                break
            else:
                for i in range(2, len(lows) - 3):
                    if lows[i] <= min(lows[max(0, i-2):i]) and lows[i] < min(lows[i+1:min(len(lows), i+3)]):
                        cand_sl = lows[i]
                        if any(float(c["close"]) < cand_sl for c in recent_3m[i+1:-1]):
                            if (abs(curr_p - cand_sl) / cand_sl <= 0.0025) or any(abs(float(c["high"]) - cand_sl) / cand_sl <= 0.0025 for c in recent_3m[-5:]):
                                breaker_tap_3m = True
                                breaker_lvl_3m = cand_sl
                                break
        if breaker_tap_3m:
            m_hits.append("3M Breaker")
            m_lvls.append(breaker_lvl_3m)

        # 2. 3M FVG Tap
        for i in range(len(recent_3m) - 1, max(2, len(recent_3m) - 8), -1):
            c_now = recent_3m[i]
            c_p2 = recent_3m[i-2]
            if is_buy:
                cur_l = float(c_now["low"])
                p2_h = float(c_p2["high"])
                if cur_l > p2_h * 1.0001:
                    if (curr_p <= cur_l * 1.0010 and curr_p >= p2_h * 0.9990) or any(float(c["low"]) <= cur_l * 1.0010 and float(c["high"]) >= p2_h * 0.9990 for c in recent_3m[-5:]):
                        m_hits.append("3M FVG")
                        m_lvls.append((cur_l + p2_h) / 2.0)
                        break
            else:
                cur_h = float(c_now["high"])
                p2_l = float(c_p2["low"])
                if cur_h < p2_l * 0.9999:
                    if (curr_p >= cur_h * 0.9990 and curr_p <= p2_l * 1.0010) or any(float(c["high"]) >= cur_h * 0.9990 and float(c["low"]) <= p2_l * 1.0010 for c in recent_3m[-5:]):
                        m_hits.append("3M FVG")
                        m_lvls.append((cur_h + p2_l) / 2.0)
                        break

        # 3. 3M Fib 0.50 - 0.618 Golden Pocket
        sh = max(highs)
        sl = min(lows)
        span = sh - sl
        if span > 0:
            depth = ((sh - curr_p) if is_buy else (curr_p - sl)) / span
            if 0.50 <= depth <= 0.618 or any(0.50 <= (((sh - float(c["low"])) if is_buy else (float(c["high"]) - sl)) / span) <= 0.618 for c in recent_3m[-5:]):
                m_hits.append("3M Fib 0.618")
                m_lvls.append(sl + (span * (0.382 if is_buy else 0.618)))

        if m_hits:
            return True, " + ".join(m_hits), (m_lvls[0] if m_lvls else curr_p)
        else:
            return False, "None", 0.0

    @staticmethod
    def check_2_candle_execution(
        candles_3m: List[Dict[str, Any]],
        bias: str = "BUY_ONLY",
        current_price: float = 0.0
    ) -> TwoCandleExecutionResult:
        """
        LEVEL 5: 3M 2-Candle Reversal Confirmation & Instant Market Execution:
        - Candle 1: Closed 3M candle with Rejection Wick Ratio >= 0.35 (Lower wick for BUY, Upper wick for SELL).
        - Candle 2: Closed 3M candle body breaks Candle 1 extreme (C2_Close > C1_High for BUY; C2_Close < C1_Low for SELL).
        - COLOR GUARD: BUY C2 must be GREEN; SELL C2 must be RED.
        - EXECUTION: Instant Market Order on Candle 2 close.
        - SL: Candle 1 Rejection Wick extreme +/- 0.15% buffer.
        - TP: 1:2.0R Fixed Target.
        """
        if not candles_3m or len(candles_3m) < 4:
            return TwoCandleExecutionResult(False, 0.0, 0.0, "Awaiting 3M candle confirmation", "3M ඉටිපන්දම් තහවුරු කිරීම බලාපොරොත්තුවෙන්")

        recent_3m = candles_3m[-10:]
        c_last = recent_3m[-1]
        c_prev = recent_3m[-2]

        last_o = float(c_last["open"])
        last_c = float(c_last["close"])
        last_h = float(c_last["high"])
        last_l = float(c_last["low"])

        prev_o = float(c_prev["open"])
        prev_c = float(c_prev["close"])
        prev_h = float(c_prev["high"])
        prev_l = float(c_prev["low"])

        is_buy = (bias == "BUY_ONLY")

        if is_buy:
            # Color Guard: C2 MUST be GREEN (Close > Open)
            if last_c <= last_o:
                return TwoCandleExecutionResult(False, 0.0, 0.0, "Current 3M candle is RED. Awaiting Green body reversal.", "වත්මන් 3M ඉටිපන්දම රතු පැහැතිය. Green Body Reversal එකක් අවශ්‍යයි.")

            # Model A: Previous Candle 1 had >=35% lower rejection wick, Current Candle 2 broke C1 High
            prev_span = prev_h - prev_l
            if prev_span > 0:
                prev_lower_wick = min(prev_o, prev_c) - prev_l
                prev_wick_ratio = prev_lower_wick / prev_span
                if prev_wick_ratio >= 0.35 and last_c > prev_h and last_c > last_o:
                    return TwoCandleExecutionResult(True, prev_l, last_c, f"2-Candle Reversal Confirmed! Wick={prev_wick_ratio*100:.1f}% >= 35%, Green Body Closed above ${prev_h:.4f}.", f"ඉටිපන්දම් 2 ක Reversal තහවුරුයි! Rejection Wick={prev_wick_ratio*100:.1f}%, Green Body Close තහවුරුයි.")

            # Model B: Instant Candle 1 Breakout with >=45% Rejection Wick
            last_span = last_h - last_l
            if last_span > 0:
                last_lower_wick = min(last_o, last_c) - last_l
                last_wick_ratio = last_lower_wick / last_span
                if last_wick_ratio >= 0.45 and last_c > last_o and len(recent_3m) >= 3 and last_c > float(recent_3m[-3]["high"]):
                    return TwoCandleExecutionResult(True, last_l, last_c, f"Instant 3M Rejection Break Confirmed! Wick={last_wick_ratio*100:.1f}%.", f"ක්ෂණික 3M Rejection Break තහවුරුයි! Wick={last_wick_ratio*100:.1f}%.")

            return TwoCandleExecutionResult(False, 0.0, 0.0, "Awaiting 3M Wick Rejection (>=35%) & Next Green Body Close", "3M Rejection Wick (>=35%) සහ Green Body Close එක බලාපොරොත්තුවෙන්")
        else:
            # Color Guard: C2 MUST be RED (Close < Open)
            if last_c >= last_o:
                return TwoCandleExecutionResult(False, 0.0, 0.0, "Current 3M candle is GREEN. Awaiting Red body reversal.", "වත්මන් 3M ඉටිපන්දම කොළ පැහැතිය. Red Body Reversal එකක් අවශ්‍යයි.")

            # Model A: Previous Candle 1 had >=35% upper rejection wick, Current Candle 2 broke C1 Low
            prev_span = prev_h - prev_l
            if prev_span > 0:
                prev_upper_wick = prev_h - max(prev_o, prev_c)
                prev_wick_ratio = prev_upper_wick / prev_span
                if prev_wick_ratio >= 0.35 and last_c < prev_l and last_c < last_o:
                    return TwoCandleExecutionResult(True, prev_h, last_c, f"2-Candle Reversal Confirmed! Wick={prev_wick_ratio*100:.1f}% >= 35%, Red Body Closed below ${prev_l:.4f}.", f"ඉටිපන්දම් 2 ක Reversal තහවුරුයි! Rejection Wick={prev_wick_ratio*100:.1f}%, Red Body Close තහවුරුයි.")

            # Model B: Instant Candle 1 Breakdown with >=45% Rejection Wick
            last_span = last_h - last_l
            if last_span > 0:
                last_upper_wick = last_h - max(last_o, last_c)
                last_wick_ratio = last_upper_wick / last_span
                if last_wick_ratio >= 0.45 and last_c < last_o and len(recent_3m) >= 3 and last_c < float(recent_3m[-3]["low"]):
                    return TwoCandleExecutionResult(True, last_h, last_c, f"Instant 3M Rejection Break Confirmed! Wick={last_wick_ratio*100:.1f}%.", f"ක්ෂණික 3M Rejection Break තහවුරුයි! Wick={last_wick_ratio*100:.1f}%.")

            return TwoCandleExecutionResult(False, 0.0, 0.0, "Awaiting 3M Wick Rejection (>=35%) & Next Red Body Close", "3M Rejection Wick (>=35%) සහ Red Body Close එක බලාපොරොත්තුවෙන්")

    @staticmethod
    def get_wave_structure(
        candles: List[Dict[str, Any]],
        is_buy: bool,
        current_price: float = 0.0
    ) -> Tuple[int, str]:
        """
        Pure Fractal / Break of Structure BOS Wave Counter.
        Waves:
        - Wave 1: 1st BOS impulse expansion.
        - Wave 2: 1st Pullback (Entry Eligible).
        - Wave 3: 2nd BOS impulse expansion.
        - Wave 4: 2nd Pullback (Entry Eligible).
        - Wave 5+: Exhaustion Block 🛑.
        """
        if not candles or len(candles) < 10:
            return 1, "Wave 1"

        highs = [float(c["high"]) for c in candles]
        lows = [float(c["low"]) for c in candles]
        closes = [float(c["close"]) for c in candles]
        curr_p = float(current_price) if current_price > 0 else closes[-1]

        # 1. Fractal Swing Points
        swing_highs = []
        swing_lows = []
        for i in range(2, len(highs) - 2):
            if highs[i] >= max(highs[i-2:i]) and highs[i] > max(highs[i+1:i+3]):
                swing_highs.append((i, highs[i]))
            if lows[i] <= min(lows[i-2:i]) and lows[i] < min(lows[i+1:i+3]):
                swing_lows.append((i, lows[i]))

        # 2. Count BOS Expansions
        bos_count = 0
        if is_buy and len(swing_highs) >= 2:
            last_broken_sh_idx = -1
            for idx, sh_p in swing_highs:
                if any(closes[k] > sh_p for k in range(idx + 1, len(closes))):
                    if idx > last_broken_sh_idx:
                        bos_count += 1
                        last_broken_sh_idx = idx
        elif not is_buy and len(swing_lows) >= 2:
            last_broken_sl_idx = -1
            for idx, sl_p in swing_lows:
                if any(closes[k] < sl_p for k in range(idx + 1, len(closes))):
                    if idx > last_broken_sl_idx:
                        bos_count += 1
                        last_broken_sl_idx = idx
        else:
            if is_buy and len(swing_highs) >= 2:
                bos_count = sum(1 for i in range(1, len(swing_highs)) if swing_highs[i][1] > swing_highs[i-1][1])
            elif not is_buy and len(swing_lows) >= 2:
                bos_count = sum(1 for i in range(1, len(swing_lows)) if swing_lows[i][1] < swing_lows[i-1][1])

        # 3. Pullback / Retracement Check
        recent_sh = max(highs[-10:]) if len(highs) >= 10 else max(highs)
        recent_sl = min(lows[-10:]) if len(lows) >= 10 else min(lows)
        span = recent_sh - recent_sl
        is_pullback = False
        if span > 0:
            depth = ((recent_sh - curr_p) if is_buy else (curr_p - recent_sl)) / span
            if 0.18 <= depth <= 0.82:
                is_pullback = True

        # 4. Map to exact specification
        if bos_count > 4:
            return 5, "Wave 5+ (Blocked)"
        elif is_pullback:
            w_num = 4 if bos_count >= 2 else 2
            return w_num, f"Wave {w_num}"
        elif bos_count == 2:
            return 3, "Wave 3"
        elif bos_count == 1:
            return 1, "Wave 1"
        elif bos_count in [3, 4]:
            return 5, "Wave 5+ (Blocked)"
        else:
            return 1, "Wave 1"


# Standalone function aliases for direct script integration:
def check_5m_structure_and_waves(df_or_candles_5m: Any, is_buy: Optional[bool] = None, current_price: float = 0.0) -> FiveMinStructureResult:
    candles = df_or_candles_5m.to_dict(orient="records") if hasattr(df_or_candles_5m, "to_dict") else (df_or_candles_5m if isinstance(df_or_candles_5m, list) else [])
    curr_p = float(current_price) if current_price > 0 else (float(candles[-1]["close"]) if candles else 0.0)
    if is_buy is None:
        closes = [float(c["close"]) for c in candles] if candles else [curr_p]
        is_buy = bool(curr_p >= sum(closes[-20:]) / len(closes[-20:])) if len(closes) >= 5 else True
    bias = "BUY_ONLY" if is_buy else "SELL_ONLY"
    return PureSMCEngine.check_5m_structure_and_waves(candles, bias=bias, current_price=curr_p)


def get_3m_micro_wave_count(df_or_candles_3m: Any, is_buy: Optional[bool] = None, current_price: float = 0.0) -> ThreeMinWaveResult:
    candles = df_or_candles_3m.to_dict(orient="records") if hasattr(df_or_candles_3m, "to_dict") else (df_or_candles_3m if isinstance(df_or_candles_3m, list) else [])
    curr_p = float(current_price) if current_price > 0 else (float(candles[-1]["close"]) if candles else 0.0)
    if is_buy is None:
        closes = [float(c["close"]) for c in candles] if candles else [curr_p]
        is_buy = bool(curr_p >= sum(closes[-20:]) / len(closes[-20:])) if len(closes) >= 5 else True
    bias = "BUY_ONLY" if is_buy else "SELL_ONLY"
    return PureSMCEngine.get_3m_micro_wave_count(candles, bias=bias, current_price=curr_p)


def check_2_candle_execution(df_or_candles_3m: Any = None, is_buy: bool = True, current_price: float = 0.0) -> TwoCandleExecutionResult:
    candles = df_or_candles_3m.to_dict(orient="records") if hasattr(df_or_candles_3m, "to_dict") else (df_or_candles_3m if isinstance(df_or_candles_3m, list) else [])
    curr_p = float(current_price) if current_price > 0 else (float(candles[-1]["close"]) if candles else 0.0)
    bias = "BUY_ONLY" if is_buy else "SELL_ONLY"
    return PureSMCEngine.check_2_candle_execution(candles, bias=bias, current_price=curr_p)


# Alias PrecisionScalpPipeline to PureSMCEngine for backwards compatibility
PrecisionScalpPipeline = PureSMCEngine
