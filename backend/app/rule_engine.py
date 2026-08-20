import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RuleEngine:
    """
    Centralized Rule Engine for Project Falcon.
    Validates all trade setups against the Master Rules to prevent hidden lockouts 
    and ensure 100% adherence to risk management guidelines.
    """

    @staticmethod
    def validate_setup(result: Dict[str, Any], timeframe: str, active_trend: str, trend_15m: str = None, trend_5m: str = None, strategy_model: str = "double_mitigation") -> Dict[str, Any]:
        """
        Runs all Master Rules in sequence. If a rule fails, it modifies the result in-place 
        to lock out the trade and provides the exact rule reasoning in both English and Sinhala.
        """
        if not result.get("is_valid"):
            return result  # Already invalid, no need to override

        # Rule 16: Timeframe Structure Check (Trend Mismatch)
        result = RuleEngine._validate_trend_alignment(result, timeframe, active_trend)
        if not result.get("is_valid"):
            return result

        # Rule 37: Strict 15m Trend Alignment Filter for 1m Scalps
        if timeframe == "1m" and strategy_model != "poi_reversal" and trend_15m:
            entry_area = str(result.get("entry_price_area") or "")
            t15m_upper = trend_15m.upper().strip()
            if t15m_upper == "BEARISH" and ("Buy" in entry_area or result.get("daily_bias") == "BULLISH"):
                result["entry_price_area"] = "No Entry (15m Trend Mismatch Lockout)"
                result["is_valid"] = False
                result["confidence"] = 0
                reason_eng = "The 15m Higher Timeframe trend is BEARISH. Entering Buy setups against the 15m trend is strictly locked out (Rule 37)."
                reason_sin = "15-Minute ප්‍රධාන ප්‍රවණතාවය (trend) BEARISH වේ. ප්‍රධාන ප්‍රවණතාවයට ප්‍රතිවිරුද්ධව Buy setups ලබා ගැනීම රීති 37 (Rule 37) අනුව සම්පූර්ණයෙන්ම තහනම් වේ."
                result["reasoning"] = f"{reason_eng}\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\n{reason_sin}"
                result["invalidation"] = "N/A"
                result["risk_notes"] = "N/A"
                return result
            elif t15m_upper == "BULLISH" and ("Sell" in entry_area or result.get("daily_bias") == "BEARISH"):
                result["entry_price_area"] = "No Entry (15m Trend Mismatch Lockout)"
                result["is_valid"] = False
                result["confidence"] = 0
                reason_eng = "The 15m Higher Timeframe trend is BULLISH. Entering Sell setups against the 15m trend is strictly locked out (Rule 37)."
                reason_sin = "15-Minute ප්‍රධාන ප්‍රවණතාවය (trend) BULLISH වේ. ප්‍රධාන ප්‍රවණතාවයට ප්‍රතිවිරුද්ධව Sell setups ලබා ගැනීම රීති 37 (Rule 37) අනුව සම්පූර්ණයෙන්ම තහනම් වේ."
                result["reasoning"] = f"{reason_eng}\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\n{reason_sin}"
                result["invalidation"] = "N/A"
                result["risk_notes"] = "N/A"
                return result

        # Rule 45: Multi-Timeframe POI Reversal & 5m Confirmation Protocol
        if strategy_model == "poi_reversal" and timeframe == "1m" and trend_5m:
            entry_area = str(result.get("entry_price_area") or "")
            t5m_upper = trend_5m.upper().strip()
            if ("Buy" in entry_area or result.get("daily_bias") == "BULLISH") and t5m_upper != "BULLISH":
                result["entry_price_area"] = "No Entry (5m Trend Mismatch)"
                result["is_valid"] = False
                result["confidence"] = 0
                reason_eng = f"The 5-Minute trend/momentum is {t5m_upper}, which does not align with the 1-Minute Bullish setup. Blocked per Rule 45."
                reason_sin = f"5-Minute ප්‍රවණතාවය (trend) {t5m_upper} වේ. 1m Bullish සෙටප් එක සමඟ 5-Minute ප්‍රවණතාවය සමපාත නොවන බැවින් ඇතුල්වීම් රීති 45 (Rule 45) අනුව අවහිර කර ඇත."
                result["reasoning"] = f"{reason_eng}\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\n{reason_sin}"
                result["invalidation"] = "N/A"
                result["risk_notes"] = "N/A"
                return result
            elif ("Sell" in entry_area or result.get("daily_bias") == "BEARISH") and t5m_upper != "BEARISH":
                result["entry_price_area"] = "No Entry (5m Trend Mismatch)"
                result["is_valid"] = False
                result["confidence"] = 0
                reason_eng = f"The 5-Minute trend/momentum is {t5m_upper}, which does not align with the 1-Minute Bearish setup. Blocked per Rule 45."
                reason_sin = f"5-Minute ප්‍රවණතාවය (trend) {t5m_upper} වේ. 1m Bearish සෙටප් එක සමඟ 5-Minute ප්‍රවණතාවය සමපාත නොවන බැවින් ඇතුල්වීම් රීති 45 (Rule 45) අනුව අවහිර කර ඇත."
                result["reasoning"] = f"{reason_eng}\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\n{reason_sin}"
                result["invalidation"] = "N/A"
                result["risk_notes"] = "N/A"
                return result
            
        return result

    @staticmethod
    def _validate_trend_alignment(result: Dict[str, Any], timeframe: str, active_trend: str) -> Dict[str, Any]:
        """
        Rule 16: If 1m trend is BULLISH -> Search for Buy Limit setups only.
        """
        entry_area = str(result.get("entry_price_area") or "")
        tf_label = "1-Minute" if timeframe == "1m" else "15-Minute" if timeframe == "15m" else "1-Hour"

        if active_trend == "BULLISH" and "Sell" in entry_area:
            result["entry_price_area"] = "No Entry (Trend Mismatch - Buy Only)"
            result["is_valid"] = False
            result["confidence"] = 0
            reason_eng = f"The selected {tf_label} trend is BULLISH. Sell setups are prohibited in this trend state."
            reason_sin = f"තෝරාගත් {tf_label} ප්‍රවණතාවය BULLISH වේ. මෙම ප්‍රවණතා තත්ත්වය තුළ Sell setups ලබා ගැනීම තහනම් වේ."
            result["reasoning"] = f"{reason_eng}\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\n{reason_sin}"
            result["invalidation"] = "N/A"
            result["risk_notes"] = "N/A"
        elif active_trend == "BEARISH" and "Buy" in entry_area:
            result["entry_price_area"] = "No Entry (Trend Mismatch - Sell Only)"
            result["is_valid"] = False
            result["confidence"] = 0
            reason_eng = f"The selected {tf_label} trend is BEARISH. Buy setups are prohibited in this trend state."
            reason_sin = f"තෝරාගත් {tf_label} ප්‍රවණතාවය BEARISH වේ. මෙම ප්‍රවණතා තත්ත්වය තුළ Buy setups ලබා ගැනීම තහනම් වේ."
            result["reasoning"] = f"{reason_eng}\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\n{reason_sin}"
            result["invalidation"] = "N/A"
            result["risk_notes"] = "N/A"
            
        return result
