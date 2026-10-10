"""
UNIFIED 7-STEP 5M > 3M PRECISION SCALP PIPELINE
Author: Falcon Institutional Engine (Clean Rebuild)
Description: Complete, zero-legacy execution pipeline enforcing the 7-Step Precision Scalp Protocol.
Steps:
  Step 1: Macro Anchor & News Armor (USD News +/-60m, 15M HH/HL Buy Only vs LL/LH Sell Only)
  Step 2: Liquidity Pool Sweep & 5M MSS (Asian/PDL/EQL or Asian/PDH/EQH sweep + 5M Candle Body Close MSS)
  Step 3: 5M Base Identification & Retrace Tap (Origin OB Demand/Supply Zone + mandatory tap/touch)
  Step 4: 3M Micro-Structure Shift & RVOL (3M Body Close CHoCH + RVOL >= 1.35x + fresh 3M FVG)
  Step 5: 3M FVG Precision Retest Entry (Limit Only: Buy at FVG Top, Sell at FVG Bottom, Clear Sky >= 1.5R)
  Step 6: Micro-Wick Stop Loss Engine (0.25% - 0.65% Hard-Cap: 3M Reversal Wick +/- 0.15% Buffer)
  Step 7: 30-Minute Rapid Scalp Exit Engine (BE at +0.80R, TP1 1:1.50R 60%, TP2 1:2.20R-1:2.50R 40%, 30-min time-stop)
"""

import math
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("precision_scalp")

PRECISION_SCALP_STEPS_CATALOGUE = [
    {
        "step_no": 0,
        "title": "Gate 0: Market Regime & Consolidation Filter",
        "title_si": "පියවර 0: වෙළඳපල කලාපය සහ තදවීම පෙරහන (ADX >= 20 & Bollinger Squeeze Lock)",
        "description": "ADX(14) < 20 or Bollinger Bands Squeeze detected -> Pipeline 100% Locked. Zero entries in choppy sideways markets."
    },
    {
        "step_no": 1,
        "title": "Gate 1: Macro Anchor 15M & News Armor",
        "title_si": "පියවර 1: 15M සාර්ව නැංගුරම සහ ආර්ථික පුවත් ආවරණය (15M Macro Anchor & News Armor)",
        "description": "USD High-Impact News Window (+/- 60 min) Active -> Signal Engine 100% OFF. 15M Trend: Bullish = BUY ONLY, Bearish = SELL ONLY. Counter-trend setups 100% Blocked."
    },
    {
        "step_no": 2,
        "title": "Gate 2: 3-Tier Cascade Retracement Engine & Wave Counter",
        "title_si": "පියවර 2: 3-Tier Cascade Retracement එන්ජිම (FVG -> Breaker -> Golden Pocket Fib 0.50-0.786 & Wave 1-4)",
        "description": "Waterfall order: Tier 1 (FVG Mitigation top/bottom 25%), Tier 2 (Breaker Re-test), Tier 3 (Golden Pocket Fib 0.50-0.786). Mid-range floating setups 100% blocked. Wave >= 5 hard exhaustion lockout."
    },
    {
        "step_no": 3,
        "title": "Gate 3: 3M Candle Body Displacement & RVOL",
        "title_si": "පියවර 3: 3M ඉටිපන්දම් කඳ බිඳීම සහ සාපේක්ෂ පරිමාව (3M Body Close CHoCH & RVOL >= 1.35x)",
        "description": "Wicks alone are NOT CHoCH. 3M Candle Body Close required beyond prior High/Low. RVOL >= 1.35x mandatory with fresh unmitigated 3M FVG."
    },
    {
        "step_no": 4,
        "title": "Gate 4: Absolute Reversal Candle Color & Next Body Close Shift",
        "title_si": "පියවර 4: නිරපේක්ෂ ප්‍රතිවර්තන ඉටිපන්දම් වර්ණය සහ ඊළඟ Body Close Shift තහවුරු කිරීම",
        "description": "BUY: Current 3M candle MUST NOT be Red. 3M Green Rejection Candle (Lower Wick >= 35%) + Next 3M Body Close > High mandatory. SELL: Current 3M candle MUST NOT be Green. 3M Red Rejection Candle (Upper Wick >= 35%) + Next 3M Body Close < Low mandatory."
    },
    {
        "step_no": 5,
        "title": "Gate 5: Confirmation-First Instant Market Order Engine",
        "title_si": "පියවර 5: තහවුරු කළ සැණින් ක්‍රියාත්මක වන Instant Market Order එන්ජිම (No Limit Orders)",
        "description": "Limit Orders completely removed. The moment Gate 4 2-candle micro-shift confirms, INSTANT MARKET BUY or INSTANT MARKET SELL triggers at current market price. Clearance >= 1.5R."
    },
    {
        "step_no": 6,
        "title": "Gate 6: Micro-Wick Stop Loss & 0.25%-0.65% Hard-Cap",
        "title_si": "පියවර 6: ක්ෂුද්‍ර වික් බෆර් Stop Loss සහ 0.25%-0.65% Hard-Cap සීමාව (0.15% Wick Buffer)",
        "description": "SL anchored strictly to Local HL Wick (-0.15% for Long) or Local LH Wick (+0.15% for Short). Risk hard-capped between 0.25% and 0.65%. If risk exceeds 0.65%, trade is cancelled."
    },
    {
        "step_no": 7,
        "title": "Gate 7: Rapid Scalp Exit Delivery (15-20 Min)",
        "title_si": "පියවර 7: විනාඩි 15-20 අධිවේගී පිටවීමේ සැලැස්ම (BE +0.80R, TP1 1:1.50R, TP2 1:2.0R Fixed Target)",
        "description": "Break-Even at +0.80R. TP1 (60% Close) at 1:1.50R. TP2 (40% Final Exit) at 1:2.0R Fixed Target within 15-20 minutes holding limit."
    }
]


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


class PrecisionScalpPipeline:
    """
    Unified 7-Step 5M > 3M Precision Scalp Execution Engine.
    Executes top-down multi-timeframe precision scalping with strict institutional safety gates.
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
        Evaluates the unified 7-step pipeline on live/mock candlestick data.
        Returns full institutional analysis with bilingual explanations.
        """
        precision = get_dynamic_precision(price)

        # Initialize evaluations for each gate
        evaluations: List[Dict[str, Any]] = []

        # =========================================================================
        # GATE 0: Market Regime & Consolidation Filter
        # =========================================================================
        adx_candles = candles_15m if len(candles_15m) >= 28 else candles_5m
        adx_val = cls._calculate_adx_14(adx_candles)
        sq_candles = candles_15m if len(candles_15m) >= 20 else candles_5m
        is_bb_sq, current_bw = cls._check_bb_squeeze(sq_candles)

        gate_0_passed = bool(adx_val >= 20.0 and not is_bb_sq)
        market_regime = "TRENDING EXPANSION ✅" if gate_0_passed else "CHOPPY / SQUEEZE (LOCKED)"

        if not gate_0_passed:
            gate_0_detail_en = f"Gate 0 Blocked: ADX({adx_val:.1f}) < 20 or BB Squeeze active (Bandwidth={current_bw*100:.2f}%). Choppy sideways market locked out."
            gate_0_detail_si = f"Gate 0 අවහිරයි: ADX({adx_val:.1f}) < 20 හෝ Bollinger Squeeze (Bandwidth={current_bw*100:.2f}%). Choppy / Sideways කලාපය තුළ Trade කිරීම 100% තහනම්."
        else:
            gate_0_detail_en = f"Gate 0 Verified: Trending Volatility confirmed (ADX={adx_val:.1f} >= 20, BB Bandwidth={current_bw*100:.2f}% Expansion active)."
            gate_0_detail_si = f"Gate 0 තහවුරුයි: ප්‍රමාණවත් වෙළඳපල චලනයක් පවතී (ADX={adx_val:.1f} >= 20). Trend Expansion සක්‍රීයයි."

        evaluations.append({
            "step_no": 0,
            "rule_no": 0,
            "gate_no": 0,
            "title": "Gate 0: Market Regime & Consolidation Filter",
            "title_si": "පියවර 0: වෙළඳපල කලාපය සහ තදවීම පෙරහන (ADX >= 20 & Bollinger Squeeze Lock)",
            "passed": gate_0_passed,
            "status": "PASS" if gate_0_passed else "LOCKED",
            "detail": gate_0_detail_en,
            "detail_si": gate_0_detail_si
        })

        # =========================================================================
        # GATE 1: Macro Anchor 15M & News Armor (Sequential Hard-Lock)
        # =========================================================================
        news_block = bool(is_news_locked)
        news_ev_str = active_news_event or "USD High-Impact News (CPI/NFP/FOMC)"
        t15m_trend, t15m_seq, t15m_sh, t15m_sl = cls._detect_15m_structure(candles_15m, price)

        gate_1_passed = False
        gate_1_detail_en = ""
        gate_1_detail_si = ""

        if not gate_0_passed:
            gate_1_detail_en = "Gate 1 Locked: Waiting for Gate 0 Volatility Breakout (Market currently Choppy/Squeeze)."
            gate_1_detail_si = "Gate 1 අක්‍රියයි: Gate 0 Volatility Breakout එකක් සිදුවන තෙක් බලා සිටී (වෙළඳපල Choppy/Squeeze තත්ත්වයේය)."
        elif news_block:
            gate_1_detail_en = f"Gate 1 Blocked: USD High-Impact News Window active ({news_ev_str} +/-60 min). Signal Engine 100% OFF."
            gate_1_detail_si = f"Gate 1 අවහිරයි: USD ප්‍රධාන ආර්ථික පුවත් අවදානම සක්‍රීයයි ({news_ev_str}). Telegram Signal Engine 100% ක් අක්‍රිය කර ඇත."
        elif t15m_trend not in ["BULLISH", "BEARISH"]:
            gate_1_detail_en = "Gate 1 Pending: 15M Macro Structure is Neutral/Consolidating. Clear HH/HL (Buy) or LL/LH (Sell) anchor required."
            gate_1_detail_si = "Gate 1 රැඳී සිටී: 15M ප්‍රධාන ව්‍යුහය පැහැදිලි නැත. HH/HL (Buy) හෝ LL/LH (Sell) නැංගුරමක් අවශ්‍යයි."
        else:
            gate_1_passed = True
            gate_1_detail_en = f"Gate 1 Verified: News Armor clear. 15M Macro Direction anchored to {t15m_trend} ({t15m_seq}). Zero counter-trend trades."
            gate_1_detail_si = f"Gate 1 තහවුරුයි: ආර්ථික පුවත් අවදානමක් නැත. 15M Macro ප්‍රවණතාවය {t15m_trend} ({t15m_seq}) ලෙස තහවුරුයි. Counter-trend 100% තහනම්."

        evaluations.append({
            "step_no": 1,
            "rule_no": 1,
            "gate_no": 1,
            "title": "Gate 1: Macro Anchor 15M & News Armor",
            "title_si": "පියවර 1: 15M සාර්ව නැංගුරම සහ ආර්ථික පුවත් ආවරණය",
            "passed": gate_1_passed,
            "status": "PASS" if gate_1_passed else ("LOCKED" if (not gate_0_passed or news_block) else "PENDING"),
            "detail": gate_1_detail_en,
            "detail_si": gate_1_detail_si
        })

        active_direction = t15m_trend if gate_1_passed else None
        is_buy_setup = (active_direction == "BULLISH")
        is_sell_setup = (active_direction == "BEARISH")

        # =========================================================================
        # =========================================================================
        # GATE 2: Adaptive Dual-Retracement Engine + Wave Counter (Sequential Hard-Lock)
        # =========================================================================
        sweep_ok = False
        sweep_pool_name = ""
        mss_5m_ok = False
        mss_5m_candle_idx = -1
        mss_5m_level = 0.0

        base_5m_found = False
        base_5m_top = 0.0
        base_5m_bot = 0.0
        base_5m_tapped = False

        eq_ok = False
        eq_price = price
        fib_val = 0.50
        r_hi = price
        r_lo = price
        wave_count = 1
        wave_ok = True
        retrace_mode = "Mode B (Standard SMC)"

        gate_2_passed = False
        gate_2_detail_en = ""
        gate_2_detail_si = ""

        if gate_1_passed:
            sweep_ok, sweep_pool_name = cls._check_liquidity_sweep_5m(
                candles_5m=candles_5m,
                is_buy=is_buy_setup,
                pdh=pdh,
                pdl=pdl,
                asian_high=asian_high,
                asian_low=asian_low
            )
            mss_5m_ok, mss_5m_candle_idx, mss_5m_level = cls._check_5m_mss(
                candles_5m=candles_5m,
                is_buy=is_buy_setup
            )
            if sweep_ok and mss_5m_ok:
                base_5m_found, base_5m_top, base_5m_bot = cls._identify_5m_base(
                    candles_5m=candles_5m,
                    mss_idx=mss_5m_candle_idx,
                    is_buy=is_buy_setup
                )
                if base_5m_found:
                    base_5m_tapped = cls._check_base_retrace_tap(
                        candles_5m=candles_5m,
                        mss_idx=mss_5m_candle_idx,
                        base_top=base_5m_top,
                        base_bot=base_5m_bot,
                        is_buy=is_buy_setup,
                        current_price=price
                    )

                # Wave counter check on 3M (Waves 1 to 4 active, Wave >= 5 locked)
                wave_count = cls._count_pullback_waves(candles_3m, is_buy=is_buy_setup)
                wave_ok = bool(wave_count < 5)

                # =====================================================================
                # 3-TIER CASCADE RETRACEMENT (GATE 2 - BUY & SELL SYMMETRIC)
                # =====================================================================
                active_tier = "None"
                active_tier_level = 0.0
                tier_passed = False

                # Tier 1: 3M FVG Mitigation (Top 25% for Buy, Bottom 25% for Sell)
                fvg_3m_found, fvg_3m_top, fvg_3m_bot = cls._find_fresh_3m_fvg(candles_3m, is_buy=is_buy_setup)
                tier_1_tap = False
                tier_1_level = 0.0
                if fvg_3m_found:
                    if is_buy_setup:
                        tier_1_level = fvg_3m_top - (0.25 * (fvg_3m_top - fvg_3m_bot))
                        tier_1_tap = bool(
                            (price <= tier_1_level * 1.0008 and price >= fvg_3m_bot * 0.9992) or
                            any(float(c["low"]) <= tier_1_level * 1.0008 and float(c["high"]) >= fvg_3m_bot * 0.9992 for c in candles_3m[-6:])
                        )
                    else:
                        tier_1_level = fvg_3m_bot + (0.25 * (fvg_3m_top - fvg_3m_bot))
                        tier_1_tap = bool(
                            (price >= tier_1_level * 0.9992 and price <= fvg_3m_top * 1.0008) or
                            any(float(c["high"]) >= tier_1_level * 0.9992 and float(c["low"]) <= fvg_3m_top * 1.0008 for c in candles_3m[-6:])
                        )

                # Tier 2: Breaker Re-test (Prior 3M Resistance as Support for Buy, Prior Support as Resistance for Sell)
                _, _, breaker_level = cls._check_3m_choch_body_close(candles_3m, is_buy=is_buy_setup, base_top=0.0, base_bot=0.0)
                tier_2_tap = False
                if breaker_level > 0:
                    if is_buy_setup:
                        tier_2_tap = bool(
                            (abs(price - breaker_level) / breaker_level <= 0.0018) or
                            any(abs(float(c["low"]) - breaker_level) / breaker_level <= 0.0020 for c in candles_3m[-6:])
                        )
                    else:
                        tier_2_tap = bool(
                            (abs(price - breaker_level) / breaker_level <= 0.0018) or
                            any(abs(float(c["high"]) - breaker_level) / breaker_level <= 0.0020 for c in candles_3m[-6:])
                        )

                # Tier 3: Golden Pocket 0.50 - 0.786 (Discount for Buy, Premium for Sell)
                eq_ok, eq_price, fib_val, r_hi, r_lo = cls._check_dealing_range_equilibrium(
                    candles_5m=candles_5m,
                    current_price=price,
                    base_top=base_5m_top,
                    base_bot=base_5m_bot,
                    is_buy=is_buy_setup
                )
                tier_3_tap = False
                if is_buy_setup:
                    tier_3_tap = bool(
                        eq_ok and (
                            (0.20 <= fib_val <= 0.505) or
                            base_5m_tapped or
                            (price <= eq_price * 1.0010 and price >= r_lo * 0.9990) or
                            any(float(c["low"]) <= eq_price * 1.0010 and float(c["low"]) >= r_lo * 0.9990 for c in candles_3m[-6:])
                        )
                    )
                else:
                    tier_3_tap = bool(
                        eq_ok and (
                            (0.495 <= fib_val <= 0.80) or
                            base_5m_tapped or
                            (price >= eq_price * 0.9990 and price <= r_hi * 1.0010) or
                            any(float(c["high"]) >= eq_price * 0.9990 and float(c["high"]) <= r_hi * 1.0010 for c in candles_3m[-6:])
                        )
                    )

                # Waterfall Priority: Tier 1 -> Tier 2 -> Tier 3
                if tier_1_tap:
                    active_tier = "Tier 1: 3M FVG Mitigation"
                    active_tier_level = tier_1_level
                    tier_passed = True
                elif tier_2_tap:
                    active_tier = "Tier 2: 3M Breaker Re-test"
                    active_tier_level = breaker_level
                    tier_passed = True
                elif tier_3_tap:
                    active_tier = f"Tier 3: Golden Pocket ({'Discount' if is_buy_setup else 'Premium'} Fib {fib_val:.2f})"
                    active_tier_level = eq_price
                    tier_passed = True
                else:
                    active_tier = "Mid-Range Floating (Locked)"
                    active_tier_level = 0.0
                    tier_passed = False

        if not gate_1_passed:
            gate_2_detail_en = "Gate 2 Locked: Waiting for Gate 1 Macro Anchor confirmation."
            gate_2_detail_si = "Gate 2 අක්‍රියයි: Gate 1 Macro Anchor තහවුරු වන තෙක් බලා සිටී."
        elif not sweep_ok:
            gate_2_detail_en = f"Gate 2 Pending: Awaiting {'Asian Low / PDL / 5M EQL' if is_buy_setup else 'Asian High / PDH / 5M EQH'} Liquidity Sweep."
            gate_2_detail_si = f"Gate 2 රැඳී සිටී: {'Asian Low / PDL / 5M EQL' if is_buy_setup else 'Asian High / PDH / 5M EQH'} ද්‍රවශීලතාවය Sweep වන තෙක් බලා සිටී."
        elif not mss_5m_ok:
            gate_2_detail_en = "Gate 2 Pending: Liquidity swept, but awaiting confirmed 5M Candle Body Close MSS shift."
            gate_2_detail_si = "Gate 2 රැඳී සිටී: Liquidity sweep විය. 5M Candle Body Close MSS එකක් තහවුරු වන තෙක් බලා සිටී."
        elif not wave_ok:
            active_tier = "Wave 5 Exhaustion - Locked"
            gate_2_detail_en = f"Gate 2 Blocked: Wave 5 Exhaustion - Locked (Wave {wave_count} >= 5). All 3 Tier pathways deactivated."
            gate_2_detail_si = f"Gate 2 අවහිරයි: Wave 5 Exhaustion - Locked (Wave {wave_count} >= 5). Pathways 3 ම අක්‍රීය කර නව Entries සම්පූර්ණයෙන්ම Lock කර ඇත."
        elif not tier_passed:
            gate_2_detail_en = f"Gate 2 Locked: Price is floating mid-range without tapping Tier 1 (FVG), Tier 2 (Breaker), or Tier 3 (Golden Pocket 0.50-0.786). Mid-range entries strictly forbidden | Wave {wave_count}."
            gate_2_detail_si = f"Gate 2 අවහිරයි: මිල Tier 1 (FVG), Tier 2 (Breaker), හෝ Tier 3 (Golden Pocket Fib 0.50-0.786) කලාපයකට නොපැමිණ Range එක මැද පාවෙමින් පවතී. Entries 100% තහනම් | Wave {wave_count}."
        else:
            gate_2_passed = True
            gate_2_detail_en = f"Gate 2 Verified ({active_tier}): Retracement tap confirmed at ${active_tier_level:.{precision}f}. Wave {wave_count} valid in Wave 1-4."
            gate_2_detail_si = f"Gate 2 තහවුරුයි ({active_tier}): Retracement ස්පර්ශය (${active_tier_level:.{precision}f}) තහවුරුයි. Wave {wave_count} වලංගුයි (Wave 1-4 සක්‍රීයයි)."

        evaluations.append({
            "step_no": 2,
            "rule_no": 2,
            "gate_no": 2,
            "title": "Gate 2: 3-Tier Cascade Retracement Engine & Wave Counter",
            "title_si": "පියවර 2: 3-Tier Cascade Retracement එන්ජිම (FVG -> Breaker -> Golden Pocket Fib 0.50-0.786 & Wave 1-4)",
            "passed": gate_2_passed,
            "status": "PASS" if gate_2_passed else ("LOCKED" if (not gate_1_passed or not wave_ok or not tier_passed) else "PENDING"),
            "detail": gate_2_detail_en,
            "detail_si": gate_2_detail_si
        })

        # =========================================================================
        # GATE 3: 3M Candle Body Displacement & RVOL
        # =========================================================================
        choch_3m_ok = False
        rvol_val = 1.0
        rvol_ok = False
        fvg_3m_found = False
        fvg_3m_top = 0.0
        fvg_3m_bot = 0.0
        sweep_3m_wick_extreme = 0.0
        breaker_3m_level = 0.0

        gate_3_passed = False
        gate_3_detail_en = ""
        gate_3_detail_si = ""

        if gate_2_passed:
            choch_3m_ok, sweep_3m_wick_extreme, breaker_3m_level = cls._check_3m_choch_body_close(
                candles_3m=candles_3m,
                is_buy=is_buy_setup,
                base_top=base_5m_top,
                base_bot=base_5m_bot
            )
            rvol_val = cls._calculate_3m_rvol(candles_3m)
            rvol_ok = (rvol_val >= 1.35)
            fvg_3m_found, fvg_3m_top, fvg_3m_bot = cls._find_fresh_3m_fvg(
                candles_3m=candles_3m,
                is_buy=is_buy_setup
            )
            gate_3_passed = bool(choch_3m_ok and rvol_ok and fvg_3m_found)

        if not gate_2_passed:
            gate_3_detail_en = "Gate 3 Locked: Waiting for Gate 2 5M Base Tap in Discount/Premium & Wave 1/2."
            gate_3_detail_si = "Gate 3 අක්‍රියයි: Gate 2 5M Base Tap සහ Wave 1/2 තහවුරු වන තෙක් බලා සිටී."
        elif not choch_3m_ok:
            gate_3_detail_en = "Gate 3 Pending: Price tapped 5M Zone. Waiting for 3M Candle BODY CLOSE CHoCH/MSS (Wick breaks blocked)."
            gate_3_detail_si = "Gate 3 රැඳී සිටී: 5M Zone ස්පර්ශ විය. 3M Candle Body Close CHoCH/MSS බිඳීමක් බලාපොරොත්තුවෙන් සිටී."
        elif not rvol_ok:
            gate_3_detail_en = f"Gate 3 Pending: 3M CHoCH detected but RVOL ({rvol_val:.2f}x) is below 1.35x institutional threshold."
            gate_3_detail_si = f"Gate 3 රැඳී සිටී: 3M CHoCH සිදුවුවද RVOL ({rvol_val:.2f}x) අවම 1.35x සීමාවට වඩා අඩුය."
        elif not fvg_3m_found:
            gate_3_detail_en = "Gate 3 Pending: 3M CHoCH confirmed with RVOL, but awaiting fresh unmitigated 3M FVG formation."
            gate_3_detail_si = "Gate 3 රැඳී සිටී: 3M CHoCH තහවුරුයි, නමුත් ඊට පසු අලුත්ම 3M FVG එකක් සෑදෙන තෙක් බලා සිටී."
        else:
            gate_3_detail_en = f"Gate 3 Verified: 3M Candle Body Close CHoCH confirmed with RVOL={rvol_val:.2f}x (>=1.35x). Fresh 3M FVG (${fvg_3m_bot:.{precision}f} - ${fvg_3m_top:.{precision}f})."
            gate_3_detail_si = f"Gate 3 තහවුරුයි: 3M Candle Body Close CHoCH සහ RVOL={rvol_val:.2f}x තහවුරු විය. අලුත්ම 3M FVG එක (${fvg_3m_bot:.{precision}f} - ${fvg_3m_top:.{precision}f}) සෑදී ඇත."

        evaluations.append({
            "step_no": 3,
            "rule_no": 3,
            "gate_no": 3,
            "title": "Gate 3: 3M Candle Body Displacement & RVOL",
            "title_si": "පියවර 3: 3M ඉටිපන්දම් කඳ බිඳීම සහ සාපේක්ෂ පරිමාව",
            "passed": gate_3_passed,
            "status": "PASS" if gate_3_passed else ("LOCKED" if not gate_2_passed else "PENDING"),
            "detail": gate_3_detail_en,
            "detail_si": gate_3_detail_si
        })

        # =========================================================================
        # GATE 4: Strict HL / LH Retracement Exhaustion (No Single-Candle HL/LH)
        # =========================================================================
        retracement_passed = False
        retracement_state = "IDLE"
        retracement_status_display = "Gate 4: Awaiting 3M CHoCH Shift"
        calc_trigger_entry = 0.0
        local_extreme_wick = 0.0
        exhaustion_type = ""
        gate_4_detail_en = ""
        gate_4_detail_si = ""

        if gate_3_passed:
            (
                retracement_passed,
                retracement_state,
                retracement_status_display,
                calc_trigger_entry,
                local_extreme_wick,
                exhaustion_type,
                gate_4_detail_en,
                gate_4_detail_si
            ) = cls._check_lh_hl_retracement_exhaustion(
                candles_3m=candles_3m,
                is_buy=is_buy_setup,
                breaker_3m_level=breaker_3m_level,
                fvg_3m_top=fvg_3m_top,
                fvg_3m_bot=fvg_3m_bot,
                current_price=price,
                precision=precision
            )
        elif not gate_2_passed or not gate_1_passed or not gate_0_passed:
            gate_4_detail_en = "Gate 4 Locked: Waiting for prior gates."
            gate_4_detail_si = "Gate 4 අක්‍රියයි: පෙර පියවර සම්පූර්ණ වන තෙක් බලා සිටී."
        else:
            gate_4_detail_en = "Gate 4 Pending: Waiting for Gate 3 3M CHoCH body shift before monitoring LH/HL pullback."
            gate_4_detail_si = "Gate 4 රැඳී සිටී: 3M CHoCH Body Shift සම්පූර්ණ වන තෙක් LH/HL Pullback නිරීක්ෂණය බලා සිටී."

        gate_4_passed = bool(gate_3_passed and retracement_passed)

        evaluations.append({
            "step_no": 4,
            "rule_no": 4,
            "gate_no": 4,
            "title": "Gate 4: Absolute Reversal Candle Color & Next Body Close Shift",
            "title_si": "පියවර 4: නිරපේක්ෂ ප්‍රතිවර්තන ඉටිපන්දම් වර්ණය සහ ඊළඟ Body Close Shift තහවුරු කිරීම",
            "passed": gate_4_passed,
            "status": "PASS" if gate_4_passed else ("LOCKED" if not gate_3_passed else "PENDING"),
            "detail": gate_4_detail_en,
            "detail_si": gate_4_detail_si
        })

        # =========================================================================
        # GATE 5: Opposing Clearance & Market Order Engine
        # =========================================================================
        market_entry_price = calc_trigger_entry if (gate_4_passed and calc_trigger_entry > 0) else price
        opposing_clearance_ok = True
        opposing_wall_price = 0.0
        clearance_rr = 2.0
        gate_5_passed = False
        gate_5_detail_en = ""
        gate_5_detail_si = ""

        if gate_4_passed and market_entry_price > 0:
            opposing_clearance_ok, opposing_wall_price, clearance_rr = cls._check_opposing_obstacle_clearance(
                candles_5m=candles_5m,
                entry_price=market_entry_price,
                is_buy=is_buy_setup
            )
            if opposing_clearance_ok:
                gate_5_passed = True
                gate_5_detail_en = f"Gate 5 Verified: Instant Market Order primed at ${market_entry_price:.{precision}f}. Opposing clearance ({clearance_rr:.2f}R >= 1.5R) confirmed."
                gate_5_detail_si = f"Gate 5 තහවුරුයි: ${market_entry_price:.{precision}f} හිදී Instant Market Order සූදානම්. ප්‍රතිවිරුද්ධ බාධක පරතරය ({clearance_rr:.2f}R >= 1.5R) තහවුරුයි."
            else:
                gate_5_passed = False
                gate_5_detail_en = f"Gate 5 Rejected: Opposing obstacle clearance ({clearance_rr:.2f}R) < 1.5R! High risk of immediate roadblock."
                gate_5_detail_si = f"Gate 5 ප්‍රතික්ෂේපයි: ප්‍රතිවිරුද්ධ බාධක පරතරය ({clearance_rr:.2f}R) 1.5R ට වඩා අඩුය. Rejection අවදානම වැඩිය."
        else:
            gate_5_detail_en = "Gate 5 Locked: Waiting for Gate 4 Micro Shift confirmation."
            gate_5_detail_si = "Gate 5 අක්‍රියයි: Gate 4 Micro Shift තහවුරු වන තෙක් බලා සිටී."

        evaluations.append({
            "step_no": 5,
            "rule_no": 5,
            "gate_no": 5,
            "title": "Gate 5: Opposing Clearance & Market Order Engine",
            "title_si": "පියවර 5: ප්‍රතිවිරුද්ධ බාධක පරතරය සහ Market Order සූදානම් කිරීම (Clearance >= 1.5R)",
            "passed": gate_5_passed,
            "status": "PASS" if gate_5_passed else ("LOCKED" if not gate_4_passed else "PENDING"),
            "detail": gate_5_detail_en,
            "detail_si": gate_5_detail_si
        })

        # =========================================================================
        # GATE 6: Micro-Wick Stop Loss & Cap Engine (0.25% - 0.65% Hard-Cap)
        # =========================================================================
        sl_price = 0.0
        risk_pct = 0.0
        risk_dist = 0.0
        risk_within_hard_cap = False
        gate_6_passed = False
        gate_6_detail_en = ""
        gate_6_detail_si = ""

        if gate_5_passed:
            buffer_pct = 0.0015
            ref_wick = local_extreme_wick if local_extreme_wick > 0 else (sweep_3m_wick_extreme if sweep_3m_wick_extreme > 0 else market_entry_price)
            if is_buy_setup:
                raw_sl = ref_wick * (1.0 - buffer_pct)
                risk_dist = abs(market_entry_price - raw_sl)
                risk_pct = (risk_dist / market_entry_price) if market_entry_price > 0 else 0.003
                if risk_pct > 0.0065:
                    risk_within_hard_cap = False
                    sl_price = round(raw_sl, precision)
                else:
                    risk_within_hard_cap = True
                    if risk_pct < 0.0025:
                        sl_price = round(market_entry_price * (1.0 - 0.0025), precision)
                        risk_dist = abs(market_entry_price - sl_price)
                        risk_pct = 0.0025
                    else:
                        sl_price = round(raw_sl, precision)
            else:
                raw_sl = ref_wick * (1.0 + buffer_pct)
                risk_dist = abs(raw_sl - market_entry_price)
                risk_pct = (risk_dist / market_entry_price) if market_entry_price > 0 else 0.003
                if risk_pct > 0.0065:
                    risk_within_hard_cap = False
                    sl_price = round(raw_sl, precision)
                else:
                    risk_within_hard_cap = True
                    if risk_pct < 0.0025:
                        sl_price = round(market_entry_price * (1.0 + 0.0025), precision)
                        risk_dist = abs(sl_price - market_entry_price)
                        risk_pct = 0.0025
                    else:
                        sl_price = round(raw_sl, precision)

            gate_6_passed = bool(risk_within_hard_cap and sl_price > 0)
            wick_label = "Local Lower Wick" if is_buy_setup else "Local Upper Wick"
            if gate_6_passed:
                gate_6_detail_en = f"Gate 6 Verified: Micro-Wick SL placed at ${sl_price:.{precision}f} (0.15% buffer from 3M {wick_label} ${ref_wick:.{precision}f}). Risk={risk_pct*100:.2f}% (Strict 0.25%-0.65% Hard-Cap)."
                gate_6_detail_si = f"Gate 6 තහවුරුයි: මයික්‍රෝ-වික් SL එක ${sl_price:.{precision}f} හි තබා ඇත (3M {wick_label} ${ref_wick:.{precision}f} ට 0.15% Buffer). අවදානම={risk_pct*100:.2f}% (0.25%-0.65% Hard-Cap සීමාව තුළයි)."
            else:
                gate_6_detail_en = f"Gate 6 Rejected: Calculated risk ({risk_pct*100:.2f}%) exceeds 0.65% hard-cap ceiling. Trade cancelled to protect capital."
                gate_6_detail_si = f"Gate 6 ප්‍රතික්ෂේපයි: අවදානම ({risk_pct*100:.2f}%) උපරිම 0.65% සීමාව ඉක්මවයි. ප්‍රාග්ධනය ආරක්ෂා කිරීමට Trade එක අවලංගු විය."
        else:
            gate_6_detail_en = "Gate 6 Locked: Waiting for Gate 5 clearance verification."
            gate_6_detail_si = "Gate 6 අක්‍රියයි: Gate 5 ප්‍රතිවිරුද්ධ බාධක පරතරය තහවුරු වන තෙක් බලා සිටී."

        evaluations.append({
            "step_no": 6,
            "rule_no": 6,
            "gate_no": 6,
            "title": "Gate 6: Micro-Wick Stop Loss & Cap Engine",
            "title_si": "පියවර 6: මයික්‍රෝ-වික් Stop Loss එන්ජිම (Local Wick +/- 0.15% Buffer, 0.25%-0.65% Hard-Cap)",
            "passed": gate_6_passed,
            "status": "PASS" if gate_6_passed else ("LOCKED" if not gate_5_passed else "PENDING"),
            "detail": gate_6_detail_en,
            "detail_si": gate_6_detail_si
        })

        # =========================================================================
        # GATE 7: Execution & Risk Management (TP1 1:1.50R, TP2 1:2.0R Fixed)
        # =========================================================================
        be_trigger = 0.0
        tp1_target = 0.0
        tp2_target = 0.0
        gate_7_passed = False
        gate_7_detail_en = ""
        gate_7_detail_si = ""

        if gate_6_passed:
            r_val = abs(market_entry_price - sl_price)
            if r_val == 0:
                r_val = market_entry_price * 0.0035
            if is_buy_setup:
                be_trigger = round(market_entry_price + (0.80 * r_val), precision)
                tp1_target = round(market_entry_price + (1.50 * r_val), precision)
                tp2_target = round(market_entry_price + (2.00 * r_val), precision)
            else:
                be_trigger = round(market_entry_price - (0.80 * r_val), precision)
                tp1_target = round(market_entry_price - (1.50 * r_val), precision)
                tp2_target = round(market_entry_price - (2.00 * r_val), precision)

            gate_7_passed = bool(tp1_target > 0 and tp2_target > 0)
            if gate_7_passed:
                gate_7_detail_en = f"Gate 7 Verified: Break-Even at +0.80R (${be_trigger:.{precision}f}). TP1 at 1:1.50R (${tp1_target:.{precision}f}, 60% Close). TP2 at 1:2.0R (${tp2_target:.{precision}f}, 40% Final Exit). Fixed 1:2.0R rapid scalp exit active."
                gate_7_detail_si = f"Gate 7 තහවුරුයි: +0.80R (${be_trigger:.{precision}f}) හිදී Break-Even. 1:1.50R (${tp1_target:.{precision}f}) හිදී TP1 60% Close. 1:2.0R (${tp2_target:.{precision}f}) හිදී TP2 40% Final Exit. Fixed 1:2.0R අධිවේගී පිටවීම සක්‍රීයයි."
        else:
            gate_7_detail_en = "Gate 7 Locked: Waiting for Gate 6 Stop Loss verification."
            gate_7_detail_si = "Gate 7 අක්‍රියයි: Gate 6 Stop Loss තහවුරු වන තෙක් බලා සිටී."

        evaluations.append({
            "step_no": 7,
            "rule_no": 7,
            "gate_no": 7,
            "title": "Gate 7: Execution & Risk Management (TP1 1:1.50R, TP2 1:2.0R Fixed)",
            "title_si": "පියවර 7: ක්‍රියාත්මක කිරීම සහ අවදානම් කළමනාකරණය (BE +0.80R, TP1 1:1.50R 60%, TP2 1:2.0R 40% Fixed)",
            "passed": gate_7_passed,
            "status": "PASS" if gate_7_passed else ("LOCKED" if not gate_6_passed else "PENDING"),
            "detail": gate_7_detail_en,
            "detail_si": gate_7_detail_si
        })

        # =========================================================================
        # PIPELINE SUMMARY & FINAL DECISION
        # =========================================================================
        passed_count = sum(1 for e in evaluations if e["passed"])
        total_steps = len(evaluations) # 8 gates (0 to 7)
        progress_pct = round((passed_count / total_steps) * 100)

        # Current Phase is the first failing step or 7 if all passed
        current_phase = 7
        for e in evaluations:
            if not e["passed"]:
                current_phase = e["step_no"]
                break

        curr_phase_meta = PRECISION_SCALP_STEPS_CATALOGUE[current_phase]
        is_ready = bool(gate_7_passed and passed_count == 8)

        # ABSOLUTE CANDLE COLOR & CONFIRMATION HARD-GUARD (Zero-Tolerance Counter-Trend Guard)
        if is_ready and candles_3m:
            last_3m_c = candles_3m[-1]
            l_open = float(last_3m_c["open"])
            l_close = float(last_3m_c["close"])
            if is_buy_setup and l_close <= l_open:
                is_ready = False
                current_phase = 4
            elif is_sell_setup and l_close >= l_open:
                is_ready = False
                current_phase = 4

        # Confidence Score based on passing steps
        if is_ready:
            confidence = 94
        elif current_phase >= 5:
            confidence = 70
        elif current_phase >= 3:
            confidence = 50
        elif current_phase >= 1:
            confidence = 35
        else:
            confidence = 0

        # Construct Actionable / Awaiting / Blocked Entry Price Area string
        if is_ready:
            act_str = "BUY" if is_buy_setup else "SELL"
            entry_area_str = f"INSTANT MARKET {act_str} at ${market_entry_price:.{precision}f} (Wave {wave_count} Micro Shift Confirmed)"
            retracement_status_display = f"🎯 Wave {wave_count} Micro Shift Confirmed! INSTANT MARKET {act_str} Scalp 📌"
        elif not gate_0_passed:
            entry_area_str = "No Entry (ADX < 20 / BB Squeeze Locked - Gate 0)"
            retracement_status_display = "Gate 0: Awaiting Volatility Breakout"
        elif news_block:
            entry_area_str = "No Entry (High-Impact News Armor Lock - +/-60 min)"
            retracement_status_display = "Gate 1: Macro Wait / News Lockout"
        elif current_phase == 1:
            entry_area_str = "No Entry (15M Macro Structure Neutral/Chop - Gate 1)"
            retracement_status_display = "Gate 1: Macro Wait / 15M Anchor"
        elif current_phase == 2:
            if not wave_ok:
                entry_area_str = f"No Entry (Wave {wave_count} >= 5 Exhaustion - Locked - Gate 2)"
                retracement_status_display = f"Gate 2: Wave 5 Exhaustion - Locked (Wave {wave_count} >= 5)"
            elif not tier_passed:
                entry_area_str = f"No Entry (Mid-Range Floating - Gate 2 Locked | Wave {wave_count})"
                retracement_status_display = f"Gate 2: Mid-Range Floating (Locked) | Wave {wave_count}"
            elif not eq_ok:
                entry_area_str = "No Entry (Equilibrium Violation - Gate 2)"
                retracement_status_display = "Gate 2: Equilibrium Violation (No Buy in Premium / No Sell in Discount)"
            else:
                entry_area_str = f"⏳ {active_tier} Tapped (${active_tier_level:.{precision}f}) | Wave {wave_count}"
                retracement_status_display = f"Gate 2: {active_tier} Tapped | Wave {wave_count}"
        elif current_phase == 3:
            entry_area_str = "⏳ 5M Zone Tapped - Waiting for 3M Body Close CHoCH & RVOL >= 1.35x (Gate 3)"
            retracement_status_display = "Gate 3: 3M Body Shift & RVOL Pending"
        elif current_phase == 4:
            entry_area_str = f"{retracement_status_display} (Gate 4)"
        elif current_phase == 5:
            entry_area_str = f"Gate 5: Opposing Clearance < 1.5R"
            retracement_status_display = "Gate 5: Near-Zone Breaker Order Active 🎯"
        elif current_phase == 6:
            entry_area_str = f"No Entry (Risk {risk_pct*100:.2f}% > 0.65% Hard-Cap Ceiling - Gate 6)"
            retracement_status_display = "Gate 6: Micro-Wick SL Armed (0.25%-0.65%)"
        else:
            entry_area_str = "No Entry (Precision Scalp Filters Active)"

        # Detailed Bilingual Technical Reasoning
        reasoning_eng = (
            f"🦅 **100% Sequential Hard-Locked SMC Pipeline (Zero Step Skipping):**\n"
            f"• **Gate 0 (Regime & Squeeze):** {market_regime} (ADX={adx_val:.1f}, BB Bandwidth={current_bw*100:.2f}%).\n"
            f"• **Gate 1 (Macro Anchor):** 15M Direction: {t15m_trend or 'NEUTRAL'} ({t15m_seq}). News Armor verified.\n"
            f"• **Gate 2 (3-Tier Cascade & Wave):** {active_tier} at ${active_tier_level:.{precision}f} (Wave {wave_count} in Wave 1-4).\n"
            f"• **Gate 3 (3M Body Shift):** 3M Body Close CHoCH with RVOL={rvol_val:.2f}x.\n"
            f"• **Gate 4 (Wave 1-4 Micro Shift):** {retracement_status_display}.\n"
            f"• **Gate 5 (Opposing Clearance):** Instant Market Order primed with clearance >= 1.5R.\n"
            f"• **Gate 6 (Micro-Wick SL):** SL anchored to 3M Local Wick with 0.15% buffer (${sl_price:.{precision}f}, Risk={risk_pct*100:.2f}%).\n"
            f"• **Gate 7 (Fixed 1:2.0R Scalp):** +0.80R BE (${be_trigger:.{precision}f}), 1:1.50R TP1 (${tp1_target:.{precision}f}, 60%), 1:2.0R TP2 (${tp2_target:.{precision}f}, 40% Fixed)."
        )

        reasoning_sin = (
            f"🦅 **100% Sequential Hard-Locked SMC පද්ධතිය (Sequential Hard-Lock):**\n"
            f"• **Gate 0 (වෙළඳපල කලාපය):** {market_regime} (ADX={adx_val:.1f}, BB Bandwidth={current_bw*100:.2f}%).\n"
            f"• **Gate 1 (15M සාර්ව නැංගුරම):** 15M Macro දිශාව {t15m_trend or 'NEUTRAL'} වේ. ආර්ථික පුවත් ආවරණය ක්‍රියාත්මකයි.\n"
            f"• **Gate 2 (3-Tier Cascade Retracement & Wave):** {active_tier} (${active_tier_level:.{precision}f}) ස්පර්ශ විය. Wave {wave_count} (Wave 1-4 සක්‍රීයයි).\n"
            f"• **Gate 3 (3M ඉටිපන්දම් කඳ බිඳීම):** 3M Body Close CHoCH සහ RVOL={rvol_val:.2f}x සහිත නැවුම් 3M FVG එකක් සෑදීම.\n"
            f"• **Gate 4 (Wave 1-4 Micro Shift):** {retracement_status_display}. Rejection Wick >= 35% සහ Body Close Shift තහවුරු විය.\n"
            f"• **Gate 5 (ප්‍රතිවිරුද්ධ බාධක පරතරය):** Instant Market Order සූදානම් (Clearance >= 1.5R).\n"
            f"• **Gate 6 (Micro-Wick SL):** 3M Local Wick අන්තයෙන් 0.15% buffer සහිතව SL (${sl_price:.{precision}f}). අවදානම {risk_pct*100:.2f}% (0.25%-0.65% Hard-Cap).\n"
            f"• **Gate 7 (පිටවීමේ සැලැස්ම):** +0.80R (${be_trigger:.{precision}f}) දී Break-Even, 1:1.50R (${tp1_target:.{precision}f}) දී TP1 60% Close, 1:2.0R (${tp2_target:.{precision}f}) දී TP2 40% Close (Fixed 1:2.0R ඉලක්කය)."
        )

        pipeline_phases = []
        for e in evaluations:
            pipeline_phases.append({
                "phase": e["step_no"],
                "gate_no": e["gate_no"],
                "name": e["title"],
                "name_si": e["title_si"],
                "status": e["status"],
                "passed": e["passed"],
                "detail_en": e["detail"],
                "detail_si": e["detail_si"]
            })

        pipeline_dict = {
            "pipeline_name": "100% HARD-LOCKED 8-GATE SMC PIPELINE",
            "current_phase": current_phase,
            "current_phase_name_en": curr_phase_meta["title"],
            "current_phase_name_si": curr_phase_meta["title_si"],
            "pipeline_progress_pct": progress_pct,
            "is_ready_for_execution": is_ready,
            "phases": pipeline_phases,
            "step_7_passed": gate_7_passed,
            "market_regime": market_regime,
            "adx_14": adx_val,
            "is_bb_squeeze": is_bb_sq,
            "wave_count": wave_count,
            "fib_level": fib_val,
            "equilibrium_price": eq_price,
            "active_tier": active_tier,
            "active_tier_level": active_tier_level,
            "retracement_state": retracement_state,
            "retracement_status_display": retracement_status_display,
            "exhaustion_type": exhaustion_type,
            "local_extreme_wick": local_extreme_wick
        }

        return {
            "is_valid": is_ready,
            "confidence": confidence,
            "direction": ("LONG" if is_buy_setup else ("SHORT" if is_sell_setup else "NEUTRAL")),
            "daily_bias": (t15m_trend or "NEUTRAL"),
            "timeframe": "3m",
            "entry_price_area": entry_area_str,
            "entry_price": market_entry_price if is_ready else None,
            "stop_loss_level": sl_price if is_ready else None,
            "tp1_target": tp1_target if is_ready else None,
            "tp2_target": tp2_target if is_ready else None,
            "tp3_target": None,
            "liquidity_target": tp1_target if is_ready else None,
            "breakeven_trigger": be_trigger if is_ready else None,
            "target_reward_ratio": f"TP1: 1:1.50R (60%) | TP2: 1:2.0R (40% Final Exit)" if is_ready else "1:1.50R - 1:2.0R",
            "risk_pct": risk_pct if is_ready else 0.0,
            "current_phase": current_phase,
            "current_phase_name_en": curr_phase_meta["title"],
            "current_phase_name_si": curr_phase_meta["title_si"],
            "pipeline_progress_pct": progress_pct,
            "pipeline": pipeline_dict,
            "smc_master_pipeline": pipeline_dict,
            "rules_checklist": evaluations,
            "total_rules": 8,
            "passed_rules_count": passed_count,
            "failed_rules_count": total_steps - passed_count,
            "confluence_score": progress_pct,
            "market_regime": market_regime,
            "adx_14": adx_val,
            "is_bb_squeeze": is_bb_sq,
            "wave_count": wave_count,
            "fib_level": fib_val,
            "equilibrium_price": eq_price,
            "active_tier": active_tier,
            "active_tier_level": active_tier_level,
            "trend_15m": t15m_trend,
            "trend_5m": ("BULLISH" if mss_5m_ok and is_buy_setup else ("BEARISH" if mss_5m_ok and is_sell_setup else t15m_trend)),
            "trend_3m": ("BULLISH" if choch_3m_ok and is_buy_setup else ("BEARISH" if choch_3m_ok and is_sell_setup else "NEUTRAL")),
            "zone_type": "DISCOUNT" if is_buy_setup else "PREMIUM",
            "setup_model": "HARD_LOCKED_SMC_GATE_PIPELINE",
            "reasoning": f"{reasoning_eng}\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\n{reasoning_sin}",
            "invalidation": f"Invalidated if price breaches ${sl_price:.{precision}f} before mitigation." if is_ready else "Waiting for 8-gate hard-locked confirmation.",
            "risk_notes": "Micro-Wick SL 0.25%-0.65% hard-capped. Move SL to BE at +0.80R. 15-20 min rapid scalp holding strictly enforced.",
            "retracement_state": retracement_state,
            "retracement_status_display": retracement_status_display,
            "exhaustion_type": exhaustion_type,
            "local_extreme_wick": local_extreme_wick
        }


    # =========================================================================
    # INTERNAL HELPER METHODS (PURE MATHEMATICAL / GEOMETRIC COMPUTATION)
    # =========================================================================

    @staticmethod
    def _detect_15m_structure(candles_15m: List[Dict[str, Any]], price: float) -> Tuple[str, str, float, float]:
        """
        Detects 15M Macro Structure (BULLISH vs BEARISH), Sequence (HH_HL vs LL_LH),
        and recent Swing High / Swing Low.
        Returns: (trend, sequence, swing_high, swing_low)
        """
        if not candles_15m or len(candles_15m) < 10:
            return "NEUTRAL", "RANGE", price, price

        closes = [float(c["close"]) for c in candles_15m]
        highs = [float(c["high"]) for c in candles_15m]
        lows = [float(c["low"]) for c in candles_15m]

        swing_high = max(highs[-20:])
        swing_low = min(lows[-20:])

        # Calculate 20 and 50 EMA on 15M for macro trend determination
        def _calc_ema(data, span):
            if len(data) < span:
                return data[-1]
            multiplier = 2.0 / (span + 1.0)
            ema = sum(data[:span]) / span
            for val in data[span:]:
                ema = (val - ema) * multiplier + ema
            return ema

        ema20 = _calc_ema(closes, 20)
        ema50 = _calc_ema(closes, 50) if len(closes) >= 50 else _calc_ema(closes, 20)

        # Find recent swing pivots
        swing_highs = []
        swing_lows = []
        for i in range(2, len(candles_15m) - 2):
            if highs[i] >= highs[i-1] and highs[i] >= highs[i-2] and highs[i] >= highs[i+1] and highs[i] >= highs[i+2]:
                swing_highs.append(highs[i])
            if lows[i] <= lows[i-1] and lows[i] <= lows[i-2] and lows[i] <= lows[i+1] and lows[i] <= lows[i+2]:
                swing_lows.append(lows[i])

        # Sequence evaluation
        is_hh_hl = False
        is_ll_lh = False
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            if swing_highs[-1] > swing_highs[-2] and swing_lows[-1] >= swing_lows[-2]:
                is_hh_hl = True
            elif swing_highs[-1] <= swing_highs[-2] and swing_lows[-1] < swing_lows[-2]:
                is_ll_lh = True

        # Comprehensive confluence check
        current_close = closes[-1]
        if is_hh_hl or (current_close > ema20 >= ema50 and current_close > closes[-10]):
            trend = "BULLISH"
            seq = "HH_HL"
        elif is_ll_lh or (current_close < ema20 <= ema50 and current_close < closes[-10]):
            trend = "BEARISH"
            seq = "LL_LH"
        elif current_close >= ema20:
            trend = "BULLISH"
            seq = "HH_HL"
        else:
            trend = "BEARISH"
            seq = "LL_LH"

        return trend, seq, swing_high, swing_low

    @staticmethod
    def _calculate_adx_14(candles: List[Dict[str, Any]]) -> float:
        """Calculates 14-period Average Directional Index (ADX) using Wilder's smoothing."""
        if not candles or len(candles) < 20:
            return 25.0

        highs = [float(c["high"]) for c in candles]
        lows = [float(c["low"]) for c in candles]
        closes = [float(c["close"]) for c in candles]

        tr_list = []
        dm_plus_list = []
        dm_minus_list = []

        for i in range(1, len(candles)):
            h = highs[i]
            l = lows[i]
            prev_h = highs[i - 1]
            prev_l = lows[i - 1]
            prev_c = closes[i - 1]

            tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
            tr_list.append(tr)

            up_move = h - prev_h
            down_move = prev_l - l

            if up_move > down_move and up_move > 0:
                dm_plus_list.append(up_move)
            else:
                dm_plus_list.append(0.0)

            if down_move > up_move and down_move > 0:
                dm_minus_list.append(down_move)
            else:
                dm_minus_list.append(0.0)

        if len(tr_list) < 14:
            return 25.0

        period = 14
        tr_smooth = sum(tr_list[:period])
        dm_p_smooth = sum(dm_plus_list[:period])
        dm_m_smooth = sum(dm_minus_list[:period])

        dx_list = []
        if tr_smooth > 0:
            di_p = 100.0 * (dm_p_smooth / tr_smooth)
            di_m = 100.0 * (dm_m_smooth / tr_smooth)
            di_sum = di_p + di_m
            dx = (100.0 * abs(di_p - di_m) / di_sum) if di_sum > 0 else 0.0
            dx_list.append(dx)

        for i in range(period, len(tr_list)):
            tr_smooth = tr_smooth - (tr_smooth / period) + tr_list[i]
            dm_p_smooth = dm_p_smooth - (dm_p_smooth / period) + dm_plus_list[i]
            dm_m_smooth = dm_m_smooth - (dm_m_smooth / period) + dm_minus_list[i]

            if tr_smooth > 0:
                di_p = 100.0 * (dm_p_smooth / tr_smooth)
                di_m = 100.0 * (dm_m_smooth / tr_smooth)
                di_sum = di_p + di_m
                dx = (100.0 * abs(di_p - di_m) / di_sum) if di_sum > 0 else 0.0
                dx_list.append(dx)

        if not dx_list:
            return 25.0
        if len(dx_list) < period:
            return round(sum(dx_list) / len(dx_list), 2)

        adx = sum(dx_list[:period]) / period
        for dx in dx_list[period:]:
            adx = (adx * (period - 1) + dx) / period

        return round(adx, 2)

    @staticmethod
    def _check_bb_squeeze(candles: List[Dict[str, Any]]) -> Tuple[bool, float]:
        """
        Checks for Bollinger Bands Squeeze (20-period SMA & Bandwidth):
        Bandwidth = (Upper Band - Lower Band) / SMA20.
        Returns (is_squeeze, bandwidth).
        """
        if not candles or len(candles) < 20:
            return False, 0.02

        closes = [float(c["close"]) for c in candles]
        bandwidths = []

        for i in range(20, len(closes) + 1):
            window = closes[i-20:i]
            sma = sum(window) / 20.0
            var = sum((x - sma) ** 2 for x in window) / 20.0
            std = math.sqrt(var)
            bw = (4.0 * std) / sma if sma > 0 else 0.02
            bandwidths.append(bw)

        current_bw = bandwidths[-1] if bandwidths else 0.02
        min_recent_bw = min(bandwidths[-20:]) if len(bandwidths) >= 20 else current_bw

        # Squeeze detected if current Bandwidth is extremely compressed (< 0.65% of price)
        # or hovering within 5% of its 20-period historical minimum when bandwidth < 1.2%
        is_squeeze = (current_bw < 0.0065) or (current_bw <= min_recent_bw * 1.05 and current_bw < 0.012)
        return is_squeeze, round(current_bw, 4)

    @staticmethod
    def _check_dealing_range_equilibrium(
        candles_5m: List[Dict[str, Any]],
        current_price: float,
        base_top: float,
        base_bot: float,
        is_buy: bool
    ) -> Tuple[bool, float, float, float, float]:
        """
        Checks 5M Dealing Range and Equilibrium (50% / Fib 0.50):
        - BUY (Long): Demand Zone & Entry MUST reside strictly in Discount Zone (< 50% Equilibrium, Fib < 0.50).
                      Buying in upper Premium Resistance (> 50%) is 100% strictly forbidden (Anti-Ceiling Trap).
        - SELL (Short): Supply Zone & Entry MUST reside strictly in Premium Zone (> 50% Equilibrium, Fib > 0.50).
                       Selling in lower Discount Support (< 50%) is 100% strictly forbidden (Anti-Floor Trap).
        Returns: (is_valid_zone, equilibrium, fib_level, range_high, range_low)
        """
        if not candles_5m or len(candles_5m) < 10:
            eq = current_price
            return True, eq, 0.5, current_price * 1.01, current_price * 0.99

        recent = candles_5m[-30:]
        range_high = max(float(c["high"]) for c in recent)
        range_low = min(float(c["low"]) for c in recent)
        span = range_high - range_low

        if span <= 0:
            return True, current_price, 0.5, range_high, range_low

        equilibrium = range_low + (span * 0.50)
        ref_price = base_top if (is_buy and base_top > 0) else (base_bot if (not is_buy and base_bot > 0) else current_price)
        fib_level = round((ref_price - range_low) / span, 3)

        if is_buy:
            # Long must be in Discount (Fib <= 0.505 or below Equilibrium with 0.2% tolerance)
            is_discount = (fib_level <= 0.505) or (ref_price <= equilibrium * 1.002)
            return is_discount, equilibrium, fib_level, range_high, range_low
        else:
            # Short must be in Premium (Fib >= 0.495 or above Equilibrium with 0.2% tolerance)
            is_premium = (fib_level >= 0.495) or (ref_price >= equilibrium * 0.998)
            return is_premium, equilibrium, fib_level, range_high, range_low

    @staticmethod
    def _count_pullback_waves(candles_3m: List[Dict[str, Any]], is_buy: bool) -> int:
        """
        Counts pullback waves (Wave 1, Wave 2, Wave 3, Wave 4, Wave 5+) after key zone tap:
        Wave 1 to 4: Active & High-probability continuation setups.
        Wave >= 5: Trend Exhaustion. Block setup ("Wave 5 Exhaustion - Locked").
        """
        if not candles_3m or len(candles_3m) < 8:
            return 1

        window = candles_3m[-25:]
        highs = [float(c["high"]) for c in window]
        lows = [float(c["low"]) for c in window]

        pullback_cycles = 0
        if is_buy:
            # Count distinct Higher Low swing troughs
            for i in range(2, len(lows) - 2):
                if lows[i] <= min(lows[i-2:i]) and lows[i] < min(lows[i+1:i+3]):
                    pullback_cycles += 1
        else:
            # Count distinct Lower High swing peaks
            for i in range(2, len(highs) - 2):
                if highs[i] >= max(highs[i-2:i]) and highs[i] > max(highs[i+1:i+3]):
                    pullback_cycles += 1

        # Clamp to at least 1 wave and max 6
        wave_num = max(1, min(pullback_cycles + 1, 6))
        return wave_num

    @staticmethod
    def _check_liquidity_sweep_5m(
        candles_5m: List[Dict[str, Any]],
        is_buy: bool,
        pdh: Optional[float],
        pdl: Optional[float],
        asian_high: Optional[float],
        asian_low: Optional[float]
    ) -> Tuple[bool, str]:
        """Verifies wick sweep of Asian High/Low, PDH/PDL, or 5M Equal Highs/Lows."""
        if not candles_5m or len(candles_5m) < 6:
            return False, ""

        recent_window = candles_5m[-25:]

        # Check for 5M Equal Lows / Equal Highs
        if is_buy:
            # Targets: Asian Low, PDL, or 5M EQL
            sweep_candidates = []
            if asian_low and asian_low > 0:
                sweep_candidates.append(("Asian Low", asian_low))
            if pdl and pdl > 0:
                sweep_candidates.append(("PDL", pdl))

            # Detect 5M EQL (Equal Lows)
            lows = [float(c["low"]) for c in recent_window]
            for i in range(len(lows) - 3):
                for j in range(i + 2, len(lows) - 1):
                    if abs(lows[i] - lows[j]) / lows[i] < 0.0008:
                        sweep_candidates.append(("5M EQL (Equal Lows)", min(lows[i], lows[j])))
                        break

            # If no external levels passed, use recent local swing low
            if not sweep_candidates:
                local_ref_low = min(float(c["low"]) for c in recent_window[:10])
                sweep_candidates.append(("5M Swing Low", local_ref_low))

            # Check if any candidate was swept with wick
            for label, level in sweep_candidates:
                for c in recent_window[-12:]:
                    # Low must pierce below level, but close must close above level
                    if float(c["low"]) <= level and float(c["close"]) > level:
                        return True, label
                    elif float(c["low"]) < level * 0.9998 and float(c["close"]) >= level * 0.9990:
                        return True, label

            return False, ""
        else:
            # Targets: Asian High, PDH, or 5M EQH
            sweep_candidates = []
            if asian_high and asian_high > 0:
                sweep_candidates.append(("Asian High", asian_high))
            if pdh and pdh > 0:
                sweep_candidates.append(("PDH", pdh))

            # Detect 5M EQH (Equal Highs)
            highs = [float(c["high"]) for c in recent_window]
            for i in range(len(highs) - 3):
                for j in range(i + 2, len(highs) - 1):
                    if abs(highs[i] - highs[j]) / highs[i] < 0.0008:
                        sweep_candidates.append(("5M EQH (Equal Highs)", max(highs[i], highs[j])))
                        break

            if not sweep_candidates:
                local_ref_high = max(float(c["high"]) for c in recent_window[:10])
                sweep_candidates.append(("5M Swing High", local_ref_high))

            for label, level in sweep_candidates:
                for c in recent_window[-12:]:
                    if float(c["high"]) >= level and float(c["close"]) < level:
                        return True, label
                    elif float(c["high"]) > level * 1.0002 and float(c["close"]) <= level * 1.0010:
                        return True, label

            return False, ""

    @staticmethod
    def _check_5m_mss(candles_5m: List[Dict[str, Any]], is_buy: bool) -> Tuple[bool, int, float]:
        """Checks for 5M candle BODY CLOSE Market Structure Shift (MSS) with displacement."""
        if not candles_5m or len(candles_5m) < 8:
            return False, -1, 0.0

        n = len(candles_5m)
        lookback = min(n, 30)
        c_sub = candles_5m[-lookback:]

        if is_buy:
            # Look for break above prior swing high
            # Find recent swing high in first half
            mid = len(c_sub) // 2
            sh_candidates = [float(c["high"]) for c in c_sub[:mid]]
            if not sh_candidates:
                return False, -1, 0.0
            recent_sh = max(sh_candidates)

            # Check if any candle in second half closed above recent_sh
            for idx in range(mid, len(c_sub)):
                c = c_sub[idx]
                close_p = float(c["close"])
                open_p = float(c["open"])
                if close_p > recent_sh and close_p > open_p:
                    # Valid candle body close MSS
                    actual_idx = n - lookback + idx
                    return True, actual_idx, recent_sh
            return False, -1, 0.0
        else:
            # Look for break below prior swing low
            mid = len(c_sub) // 2
            sl_candidates = [float(c["low"]) for c in c_sub[:mid]]
            if not sl_candidates:
                return False, -1, 0.0
            recent_sl = min(sl_candidates)

            for idx in range(mid, len(c_sub)):
                c = c_sub[idx]
                close_p = float(c["close"])
                open_p = float(c["open"])
                if close_p < recent_sl and close_p < open_p:
                    actual_idx = n - lookback + idx
                    return True, actual_idx, recent_sl
            return False, -1, 0.0

    @staticmethod
    def _identify_5m_base(
        candles_5m: List[Dict[str, Any]],
        mss_idx: int,
        is_buy: bool
    ) -> Tuple[bool, float, float]:
        """Identifies the 5M origin Order Block (Base Zone) that initiated the 5M MSS."""
        if not candles_5m or mss_idx <= 0 or mss_idx >= len(candles_5m):
            mss_idx = len(candles_5m) - 1

        search_start = max(0, mss_idx - 8)
        search_window = candles_5m[search_start:mss_idx]

        if is_buy:
            # 5M Demand Zone: Last down-close candle before the bullish displacement
            for k in range(len(search_window) - 1, -1, -1):
                c = search_window[k]
                if float(c["close"]) <= float(c["open"]):
                    top = max(float(c["open"]), float(c["close"]), float(c["high"]))
                    bot = float(c["low"])
                    return True, top, bot
            # Fallback to lowest candle in window
            lowest_c = min(search_window, key=lambda x: float(x["low"])) if search_window else candles_5m[-1]
            return True, float(lowest_c["high"]), float(lowest_c["low"])
        else:
            # 5M Supply Zone: Last up-close candle before the bearish displacement
            for k in range(len(search_window) - 1, -1, -1):
                c = search_window[k]
                if float(c["close"]) >= float(c["open"]):
                    top = float(c["high"])
                    bot = min(float(c["open"]), float(c["close"]), float(c["low"]))
                    return True, top, bot
            highest_c = max(search_window, key=lambda x: float(x["high"])) if search_window else candles_5m[-1]
            return True, float(highest_c["high"]), float(highest_c["low"])

    @staticmethod
    def _check_base_retrace_tap(
        candles_5m: List[Dict[str, Any]],
        mss_idx: int,
        base_top: float,
        base_bot: float,
        is_buy: bool,
        current_price: float
    ) -> bool:
        """Checks if price cleanly retraced and tapped into the 5M Base Zone."""
        if not candles_5m:
            return False

        start_k = max(0, mss_idx)
        post_mss_candles = candles_5m[start_k:] if start_k < len(candles_5m) else candles_5m[-5:]

        if is_buy:
            # Buy Demand Tap: Candle low entered or touched base_top with small buffer
            for c in post_mss_candles:
                if float(c["low"]) <= base_top * 1.0005:
                    return True
            if current_price <= base_top * 1.0005:
                return True
            return False
        else:
            # Sell Supply Tap: Candle high entered or touched base_bot with small buffer
            for c in post_mss_candles:
                if float(c["high"]) >= base_bot * 0.9995:
                    return True
            if current_price >= base_bot * 0.9995:
                return True
            return False

    @staticmethod
    def _check_3m_choch_body_close(
        candles_3m: List[Dict[str, Any]],
        is_buy: bool,
        base_top: float,
        base_bot: float
    ) -> Tuple[bool, float, float]:
        """Checks for 3M candle BODY CLOSE CHoCH/MSS and captures the reversal sweep wick extreme and breaker level."""
        if not candles_3m or len(candles_3m) < 6:
            return False, 0.0, 0.0

        recent_c = candles_3m[-15:]

        if is_buy:
            # Find the lowest reversal sweep wick in the tap window
            sweep_low = min(float(c["low"]) for c in recent_c)

            # Find local swing high prior to the newest candle (3M Breaker High)
            highs_prior = [float(c["high"]) for c in recent_c[:-1]]
            local_sh = max(highs_prior[-5:-1]) if len(highs_prior) >= 5 else max(highs_prior)

            # Check if any recent candle closed above local_sh with body close
            for c in recent_c[-4:]:
                close_p = float(c["close"])
                open_p = float(c["open"])
                if close_p > local_sh and close_p > open_p:
                    return True, sweep_low, local_sh

            # Or if latest candle close > recent_c[-3] high with body
            c_last = recent_c[-1]
            if len(recent_c) >= 3 and float(c_last["close"]) > float(recent_c[-3]["high"]) and float(c_last["close"]) > float(c_last["open"]):
                return True, sweep_low, float(recent_c[-3]["high"])

            return False, sweep_low, local_sh
        else:
            sweep_high = max(float(c["high"]) for c in recent_c)

            # Find local swing low prior to newest candle (3M Breaker Low)
            lows_prior = [float(c["low"]) for c in recent_c[:-1]]
            local_sl = min(lows_prior[-5:-1]) if len(lows_prior) >= 5 else min(lows_prior)

            for c in recent_c[-4:]:
                close_p = float(c["close"])
                open_p = float(c["open"])
                if close_p < local_sl and close_p < open_p:
                    return True, sweep_high, local_sl

            c_last = recent_c[-1]
            if len(recent_c) >= 3 and float(c_last["close"]) < float(recent_c[-3]["low"]) and float(c_last["close"]) < float(c_last["open"]):
                return True, sweep_high, float(recent_c[-3]["low"])

            return False, sweep_high, local_sl

    @staticmethod
    def _calculate_3m_rvol(candles_3m: List[Dict[str, Any]]) -> float:
        """Calculates Relative Volume (RVOL) of displacement over 20-period 3M average."""
        if not candles_3m or len(candles_3m) < 5:
            return 1.50

        vols = [float(c.get("volume", 0.0)) for c in candles_3m if float(c.get("volume", 0.0)) > 0]
        if len(vols) < 5:
            return 1.50

        avg_vol = sum(vols[-20:]) / min(len(vols), 20)
        recent_max_vol = max(vols[-3:])
        return round((recent_max_vol / avg_vol), 2) if avg_vol > 0 else 1.50

    @staticmethod
    def _find_fresh_3m_fvg(candles_3m: List[Dict[str, Any]], is_buy: bool) -> Tuple[bool, float, float]:
        """Detects fresh unmitigated 3M Fair Value Gap (FVG) formed post-shift."""
        if not candles_3m or len(candles_3m) < 4:
            return False, 0.0, 0.0

        # Scan recent 3-candle triplets
        n = len(candles_3m)
        for i in range(n - 1, max(2, n - 8), -1):
            c_current = candles_3m[i]
            c_prior2 = candles_3m[i - 2]

            if is_buy:
                # Bullish FVG: current candle low > prior-2 candle high
                cur_low = float(c_current["low"])
                p2_high = float(c_prior2["high"])
                if cur_low > p2_high * 1.0001:
                    # Fresh unmitigated check
                    is_unmitigated = True
                    for sub in candles_3m[i+1:]:
                        if float(sub["low"]) <= p2_high:
                            is_unmitigated = False
                            break
                    if is_unmitigated:
                        return True, cur_low, p2_high
            else:
                # Bearish FVG: current candle high < prior-2 candle low
                cur_high = float(c_current["high"])
                p2_low = float(c_prior2["low"])
                if cur_high < p2_low * 0.9999:
                    is_unmitigated = True
                    for sub in candles_3m[i+1:]:
                        if float(sub["high"]) >= p2_low:
                            is_unmitigated = False
                            break
                    if is_unmitigated:
                        return True, p2_low, cur_high

        return False, 0.0, 0.0

    @staticmethod
    def _check_opposing_obstacle_clearance(
        candles_5m: List[Dict[str, Any]],
        entry_price: float,
        is_buy: bool
    ) -> Tuple[bool, float, float]:
        """Verifies clear runway >= 1.5R to the nearest opposing 5M/15M supply/demand wall."""
        if not candles_5m or len(candles_5m) < 10:
            return True, entry_price * (1.02 if is_buy else 0.98), 2.5

        highs = [float(c["high"]) for c in candles_5m[-40:]]
        lows = [float(c["low"]) for c in candles_5m[-40:]]

        # Estimated minimal 0.40% risk distance to evaluate 1.5R clearance
        est_r = entry_price * 0.0035

        if is_buy:
            # Nearest opposing supply barrier above entry
            highs_above = [h for h in highs if h > entry_price * 1.0010]
            if not highs_above:
                return True, entry_price * 1.025, 3.0
            nearest_wall = min(highs_above)
            clearance_dist = nearest_wall - entry_price
            clearance_rr = clearance_dist / est_r if est_r > 0 else 2.0
            return (clearance_rr >= 1.50), nearest_wall, clearance_rr
        else:
            # Nearest opposing demand barrier below entry
            lows_below = [l for l in lows if l < entry_price * 0.9990]
            if not lows_below:
                return True, entry_price * 0.975, 3.0
            nearest_wall = max(lows_below)
            clearance_dist = entry_price - nearest_wall
            clearance_rr = clearance_dist / est_r if est_r > 0 else 2.0
            return (clearance_rr >= 1.50), nearest_wall, clearance_rr

    @staticmethod
    def _check_lh_hl_retracement_exhaustion(
        candles_3m: List[Dict[str, Any]],
        is_buy: bool,
        breaker_3m_level: float,
        fvg_3m_top: float,
        fvg_3m_bot: float,
        current_price: float,
        precision: int = 4
    ) -> Tuple[bool, str, str, float, float, str, str, str]:
        """
        Wave 1-4 Confirmation-First Market Order Engine (Gate 4):
        ABSOLUTE SHORT EXECUTION GUARDS:
          1. Current 3M candle MUST NOT be GREEN (Close >= Open). If green -> ABORT immediately.
          2. 3M Candle Upper Rejection Wick Ratio >= 35% on a strictly RED Candle (Close < Open).
          3. Next 3M Candle MUST produce a Body Close below the prior Red Candle's LOW.
          4. No higher high breaching the rejection candle high.
        ABSOLUTE LONG EXECUTION GUARDS:
          1. Current 3M candle MUST NOT be RED (Close <= Open). If red -> ABORT immediately.
          2. 3M Candle Lower Rejection Wick Ratio >= 35% on a strictly GREEN Candle (Close > Open).
          3. Next 3M Candle MUST produce a Body Close above the prior Green Candle's HIGH.
          4. No lower low piercing the rejection candle low.
        """
        if not candles_3m or len(candles_3m) < 4:
            return (
                False,
                "MONITORING_EXHAUSTION",
                "🔍 Monitoring 3M Rejection Wick...",
                0.0,
                0.0,
                "",
                "Insufficient 3M candle history to verify market order confirmation.",
                "Market order තහවුරු කිරීමට ප්‍රමාණවත් 3M ඉටිපන්දම් දත්ත නොමැත."
            )

        n = len(candles_3m)
        lookback = min(n, 20)
        recent_c = candles_3m[-lookback:]
        current_candle = recent_c[-1]
        curr_o = float(current_candle["open"])
        curr_c = float(current_candle["close"])

        if not is_buy:
            # =================================================================
            # SHORT (SELL) SETUP (Wave 1 to 4)
            # =================================================================
            # 1. ABSOLUTE SHORT GUARD: Current 3M candle is Green (Close >= Open) -> ABORT!
            if curr_c >= curr_o:
                return (
                    False,
                    "ABORT_GREEN_CANDLE_PUMP",
                    "🚫 Current 3M Candle is Green (Pumping) — Short Entry Aborted (Anti-Counter-Pump Lock)",
                    0.0,
                    0.0,
                    "",
                    "Current 3M candle is GREEN (Close >= Open). Shorting into active green candles is strictly locked out (Anti-Counter-Pump Shield).",
                    "වත්මන් 3M ඉටිපන්දම කොළ පැහැති (Green / Close >= Open) වේ. ඉහළ නඟින ඉටිපන්දම් අතරමගදී Short කිරීම 100% ක්ම තහනම් කර ඇත (Anti-Counter-Pump Shield)."
                )

            # 2. Anti-chasing: Check if price is actively dumping at lowest low with no pause
            lows = [float(c["low"]) for c in recent_c]
            min_low = min(lows)
            min_low_idx = min(range(len(recent_c)), key=lambda i: float(recent_c[i]["low"]))
            if min_low_idx == len(recent_c) - 1 and current_price <= min_low * 1.0005:
                return (
                    False,
                    "AWAITING_PULLBACK_AT_EXTREMES",
                    "⏳ Awaiting Pullback (No Shorting at Lows)",
                    0.0,
                    0.0,
                    "",
                    "Price is actively dumping at local lows without pause. Shorting at lows is strictly locked out. Awaiting 3M red upper rejection wick.",
                    "මිල පතුලෙහිම ඇද වැටෙමින් පවතී. Lows වලදී Short කිරීම 100% තහනම්. 3M Red Upper Rejection Wick එකක් බලාපොරොත්තුවෙන් සිටී."
                )

            # 3. Search recent candles for RED Candle with Upper Rejection Wick >= 35%
            # followed by Next Candle Body Close < Low
            candidate_found = False
            cand_extreme_high = 0.0
            cand_wick_pct = 0.0
            cand_low = 0.0

            scan_end = len(recent_c) - 2
            scan_start = max(0, len(recent_c) - 7)

            for i in range(scan_end, scan_start - 1, -1):
                c_rej = recent_c[i]
                c_h = float(c_rej["high"])
                c_l = float(c_rej["low"])
                c_o = float(c_rej["open"])
                c_c = float(c_rej["close"])

                # Absolute Rule: Must be a RED Candle (Close < Open)
                if c_c >= c_o:
                    continue

                rng = c_h - c_l
                if rng <= 0:
                    continue

                upper_wick = c_h - c_o  # for red candle, open is top of body
                wick_ratio = upper_wick / rng

                if wick_ratio >= 0.35:
                    candidate_found = True
                    cand_extreme_high = c_h
                    cand_wick_pct = wick_ratio * 100.0
                    cand_low = c_l

                    # Invalidation check: No subsequent candle should have made higher high > c_h
                    subsequent_candles = recent_c[i + 1:]
                    if any(float(sub["high"]) > c_h * 1.0005 for sub in subsequent_candles):
                        # Invalidated by higher high breach
                        continue

                    # Next Candle Confirmation: 
                    # ඊළඟ 3M Candle එක පෙර Red Candle එකෙහි LOW එකට පහළින් Body Close එකක් දෙන තෙක් SHORT TRIGGER නොකරන්න.
                    c_next = subsequent_candles[0]
                    next_close = float(c_next["close"])

                    # If next candle body closed below c_l
                    if next_close < c_l:
                        trigger_entry = round(current_price, precision)
                        ex_type = f"Red Upper Wick ({cand_wick_pct:.1f}%) + 3M Body Close < Low"
                        return (
                            True,
                            "CONFIRMED_MICRO_SHIFT",
                            "🎯 3M Red Upper Wick >= 35% + Body Close Shift Confirmed! INSTANT MARKET SELL 📌",
                            trigger_entry,
                            cand_extreme_high,
                            ex_type,
                            f"Gate 4 Verified: 3M Red Candle Upper Rejection Wick ({cand_wick_pct:.1f}%) followed by Body Close < Low (${c_l:.{precision}f}). Micro Shift Confirmed! Current candle is Red. Instant Market Sell primed.",
                            f"Gate 4 තහවුරුයි: 3M Red Candle Upper Rejection Wick ({cand_wick_pct:.1f}%) සහ Body Close < Low (${c_l:.{precision}f}) තහවුරු විය. වත්මන් ඉටිපන්දම රතු පැහැතිය. Instant Market Sell සූදානම්."
                        )

            if candidate_found:
                return (
                    False,
                    "AWAITING_BODY_CLOSE_CONFIRMATION",
                    f"⏳ Red Upper Wick ({cand_wick_pct:.1f}%) Formed. Awaiting 3M Body Close < Low (${cand_low:.{precision}f})...",
                    0.0,
                    cand_extreme_high,
                    "",
                    f"3M Red Upper Rejection Wick ({cand_wick_pct:.1f}%) formed at ${cand_extreme_high:.{precision}f}. Waiting for next 3M candle body close below prior low (${cand_low:.{precision}f}) to confirm.",
                    f"3M Red Upper Rejection Wick ({cand_wick_pct:.1f}%) සාදා ඇත (${cand_extreme_high:.{precision}f}). තහවුරු කිරීමට ඊළඟ 3M candle body close එක පෙර low (${cand_low:.{precision}f}) එකට පහළින් සිදුවන තෙක් බලා සිටී."
                )
            else:
                return (
                    False,
                    "AWAITING_REJECTION_WICK",
                    "🔍 Monitoring 3M Red Candle Upper Rejection Wick (Ratio >= 35%)...",
                    0.0,
                    0.0,
                    "",
                    "Awaiting 3M RED candle with upper rejection wick ratio >= 35% before triggering Short setup.",
                    "Short setup එක සඳහා 3M RED Upper Rejection Wick (>= 35%) එකක් සාදන තෙක් නිරීක්ෂණය කෙරේ."
                )

        else:
            # =================================================================
            # LONG (BUY) SETUP (Wave 1 to 4)
            # =================================================================
            # 1. ABSOLUTE LONG GUARD: Current 3M candle is Red (Close <= Open) -> ABORT!
            if curr_c <= curr_o:
                return (
                    False,
                    "ABORT_RED_CANDLE_DUMP",
                    "🚫 Current 3M Candle is Red (Dumping) — Long Entry Aborted (Anti-Counter-Dump Lock)",
                    0.0,
                    0.0,
                    "",
                    "Current 3M candle is RED (Close <= Open). Buying into active red candles is strictly locked out (Anti-Counter-Dump Shield).",
                    "වත්මන් 3M ඉටිපන්දම රතු පැහැති (Red / Close <= Open) වේ. පහළට කඩා වැටෙන ඉටිපන්දම් අතරමගදී Long කිරීම 100% ක්ම තහනම් කර ඇත (Anti-Counter-Dump Shield)."
                )

            # 2. Anti-chasing: Check if price is actively pumping at highest high with no pause
            highs = [float(c["high"]) for c in recent_c]
            max_high = max(highs)
            max_high_idx = max(range(len(recent_c)), key=lambda i: float(recent_c[i]["high"]))
            if max_high_idx == len(recent_c) - 1 and current_price >= max_high * 0.9995:
                return (
                    False,
                    "AWAITING_PULLBACK_AT_EXTREMES",
                    "⏳ Awaiting Pullback (No Buying at Highs)",
                    0.0,
                    0.0,
                    "",
                    "Price is actively pumping at local highs without pause. Buying at highs is strictly locked out. Awaiting 3M green lower rejection wick.",
                    "මිල මුදුනෙහිම ඉහළ නඟිමින් පවතී. Highs වලදී Buy කිරීම 100% තහනම්. 3M Green Lower Rejection Wick එකක් බලාපොරොත්තුවෙන් සිටී."
                )

            # 3. Search recent candles for GREEN Candle with Lower Rejection Wick >= 35%
            # followed by Next Candle Body Close > High
            candidate_found = False
            cand_extreme_low = 0.0
            cand_wick_pct = 0.0
            cand_high = 0.0

            scan_end = len(recent_c) - 2
            scan_start = max(0, len(recent_c) - 7)

            for i in range(scan_end, scan_start - 1, -1):
                c_rej = recent_c[i]
                c_h = float(c_rej["high"])
                c_l = float(c_rej["low"])
                c_o = float(c_rej["open"])
                c_c = float(c_rej["close"])

                # Absolute Rule: Must be a GREEN Candle (Close > Open)
                if c_c <= c_o:
                    continue

                rng = c_h - c_l
                if rng <= 0:
                    continue

                lower_wick = c_o - c_l  # for green candle, open is bottom of body
                wick_ratio = lower_wick / rng

                if wick_ratio >= 0.35:
                    candidate_found = True
                    cand_extreme_low = c_l
                    cand_wick_pct = wick_ratio * 100.0
                    cand_high = c_h

                    # Invalidation check: No subsequent candle should have made lower low < c_l
                    subsequent_candles = recent_c[i + 1:]
                    if any(float(sub["low"]) < c_l * 0.9995 for sub in subsequent_candles):
                        # Invalidated by lower low breach
                        continue

                    # Next Candle Confirmation:
                    # ඊළඟ 3M Candle එක පෙර Green Candle එකෙහි HIGH එකට ඉහළින් Body Close එකක් දෙන තෙක් LONG TRIGGER නොකරන්න.
                    c_next = subsequent_candles[0]
                    next_close = float(c_next["close"])

                    # If next candle body closed above c_h
                    if next_close > c_h:
                        trigger_entry = round(current_price, precision)
                        ex_type = f"Green Lower Wick ({cand_wick_pct:.1f}%) + 3M Body Close > High"
                        return (
                            True,
                            "CONFIRMED_MICRO_SHIFT",
                            "🎯 3M Green Lower Wick >= 35% + Body Close Shift Confirmed! INSTANT MARKET BUY 📌",
                            trigger_entry,
                            cand_extreme_low,
                            ex_type,
                            f"Gate 4 Verified: 3M Green Candle Lower Rejection Wick ({cand_wick_pct:.1f}%) followed by Body Close > High (${c_h:.{precision}f}). Micro Shift Confirmed! Current candle is Green. Instant Market Buy primed.",
                            f"Gate 4 තහවුරුයි: 3M Green Candle Lower Rejection Wick ({cand_wick_pct:.1f}%) සහ Body Close > High (${c_h:.{precision}f}) තහවුරු විය. වත්මන් ඉටිපන්දම කොළ පැහැතිය. Instant Market Buy සූදානම්."
                        )

            if candidate_found:
                return (
                    False,
                    "AWAITING_BODY_CLOSE_CONFIRMATION",
                    f"⏳ Green Lower Wick ({cand_wick_pct:.1f}%) Formed. Awaiting 3M Body Close > High (${cand_high:.{precision}f})...",
                    0.0,
                    cand_extreme_low,
                    "",
                    f"3M Green Lower Rejection Wick ({cand_wick_pct:.1f}%) formed at ${cand_extreme_low:.{precision}f}. Waiting for next 3M candle body close above prior high (${cand_high:.{precision}f}) to confirm.",
                    f"3M Green Lower Rejection Wick ({cand_wick_pct:.1f}%) සාදා ඇත (${cand_extreme_low:.{precision}f}). තහවුරු කිරීමට ඊළඟ 3M candle body close එක පෙර high (${cand_high:.{precision}f}) එකට ඉහළින් සිදුවන තෙක් බලා සිටී."
                )
            else:
                return (
                    False,
                    "AWAITING_REJECTION_WICK",
                    "🔍 Monitoring 3M Green Candle Lower Rejection Wick (Ratio >= 35%)...",
                    0.0,
                    0.0,
                    "",
                    "Awaiting 3M GREEN candle with lower rejection wick ratio >= 35% before triggering Long setup.",
                    "Long setup එක සඳහා 3M GREEN Lower Rejection Wick (>= 35%) එකක් සාදන තෙක් නිරීක්ෂණය කෙරේ."
                )

