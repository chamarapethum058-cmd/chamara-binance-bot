import httpx
import json
import logging
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types
from .config import settings

logger = logging.getLogger(__name__)

class BinanceService:
    @staticmethod
    async def fetch_klines(symbol: str, interval: str, limit: int = 100) -> List[List[Any]]:
        """
        Fetch historical candlestick data from Binance public API.
        Response format:
        [
          [
            1499040000000,      // Kline open time
            "0.01634790",       // Open price
            "0.08000000",       // High price
            "0.01575800",       // Low price
            "0.01577100",       // Close price
            "148976.11400000",  // Volume
            1499644799999,      // Kline Close time
            ...
          ]
        ]
        """
        # Binance requires uppercase symbols
        symbol = symbol.upper()
        url = f"{settings.BINANCE_API_URL}/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error fetching klines from Binance: {e}")
                raise Exception(f"Failed to fetch market data from Binance: {str(e)}")

    @staticmethod
    async def fetch_ticker_price(symbol: str) -> float:
        symbol = symbol.upper()
        url = f"{settings.BINANCE_API_URL}/api/v3/ticker/price"
        params = {"symbol": symbol}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=5.0)
                response.raise_for_status()
                data = response.json()
                return float(data.get("price", 0.0))
            except Exception as e:
                logger.error(f"Error fetching ticker price: {e}")
                raise Exception(f"Failed to fetch current price for {symbol}: {str(e)}")

class AIService:
    _cached_news = None
    _last_news_fetch = None

    @classmethod
    async def _fetch_economic_calendar(cls) -> List[Dict[str, Any]]:
        import time
        now = time.time()
        if cls._cached_news is not None and cls._last_news_fetch is not None:
            if now - cls._last_news_fetch < 3600:
                return cls._cached_news
                
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    events = response.json()
                    cls._cached_news = events
                    cls._last_news_fetch = now
                    return events
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
            if cls._cached_news is not None:
                return cls._cached_news
        return []

    @staticmethod
    def _format_klines(klines: List[List[Any]]) -> str:
        """Format klines into a readable string text format for the LLM."""
        formatted = []
        # Take last 30 candles to avoid overflowing LLM context with raw arrays,
        # but enough to analyze trends and structure.
        recent_klines = klines[-30:]
        for idx, k in enumerate(recent_klines):
            open_time = k[0]
            open_p = float(k[1])
            high = float(k[2])
            low = float(k[3])
            close = float(k[4])
            volume = float(k[5])
            formatted.append(
                f"Candle {idx+1} | Open: {open_p:.4f} | High: {high:.4f} | Low: {low:.4f} | Close: {close:.4f} | Vol: {volume:.2f}"
            )
        return "\n".join(formatted)

    @classmethod
    async def analyze_market(
        cls, 
        symbol: str, 
        timeframe: str, 
        klines: List[List[Any]], 
        strategy_content: str,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send market data and strategy guidelines to Gemini to perform technical analysis.
        """
        current_price = float(klines[-1][4]) if klines else 0.0
        formatted_candles = cls._format_klines(klines)
        
        prompt = f"""
You are the AI Brain of Project Falcon, a Personal AI Trading Assistant.
Your core mission is to analyze financial markets using the user's specific trading strategy and act as an analyst and teacher.

CRITICAL RULES:
1. Never execute or automate trades.
2. Never suggest guaranteed profits or make win rate promises.
3. You must only provide analysis, not financial advice.
4. Adhere strictly to the rules of the user's strategy. Do not invent new indicators or run outside analysis.
5. Identify why setup is valid or invalid based on the strategy rules.
6. Provide clear, educational explanations to help the trader learn.
7. You MUST output all explanation fields ("reasoning", "invalidation", "risk_notes") in both English and Sinhala translation. First write the explanation in English, then add a divider line (e.g. "\\n\\n--- \\n\\n**සිංහල පරිවර්තනය (Sinhala Translation):**\\n"), followed by its complete Sinhala translation using Sinhala Unicode characters. Make sure the translation is clear and easy to read.

-----------------------------------------
USER'S TRADING STRATEGY RULES:
{strategy_content}
-----------------------------------------

MARKET METRICS:
- Asset Symbol: {symbol}
- Timeframe Analyzed: {timeframe}
- Current Price: {current_price}

RECENT HISTORICAL CANDLESTICK DATA (Chronological Order, oldest first):
{formatted_candles}

-----------------------------------------
TASK:
Analyze the provided market candlestick data against the User's Trading Strategy.
Determine if there are valid setups (e.g. Trend alignment, BOS/CHOCH, tapping Order Blocks or FVG).
Format your output strictly as a JSON object with the following fields:
1. "signal": Must be one of ["BULLISH", "BEARISH", "NEUTRAL", "NEUTRAL_WAITING"]
2. "confidence": Integer percentage from 0 to 100 representing strength/alignment of indicators.
3. "reasoning": Comprehensive text explaining your technical observations (market structure, trend, key levels, volume) and how they map to the strategy rules. Act as a teacher. This field MUST contain the English text, followed by the Sinhala translation directly underneath (separated by a divider).
4. "invalidation": Clear conditions under which this setup or analysis is considered wrong, along with recommended Stop Loss placement guidelines. This field MUST contain the English text, followed by the Sinhala translation directly underneath (separated by a divider).
5. "risk_notes": Explicit warnings about trading risk, high volatility warnings, and position size suggestions (e.g. keeping risk to 1%). This field MUST contain the English text, followed by the Sinhala translation directly underneath (separated by a divider).

OUTPUT JSON ONLY. Do not wrap in markdown blocks other than clean json formatting.
"""

        # Use passed key if available, otherwise check settings
        active_key = api_key or settings.GEMINI_API_KEY
        if not active_key:
            logger.warning("GEMINI_API_KEY not configured. Falling back to mock technical analysis.")
            return cls._get_mock_analysis(symbol, timeframe, current_price)
            
        try:
            client = genai.Client(api_key=active_key)
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            logger.error(f"Gemini API analysis failed: {e}. Falling back to mock analysis.")
            return cls._get_mock_analysis(symbol, timeframe, current_price)

    @classmethod
    def _get_mock_analysis(cls, symbol: str, timeframe: str, current_price: float) -> Dict[str, Any]:
        """Provides a structured mock analysis if Gemini API key is missing or fails."""
        # Simple rule-based mock logic for demonstration
        signal = "NEUTRAL"
        confidence = 50
        reasoning = (
            f"This is a demonstration analysis for {symbol} on the {timeframe} timeframe. "
            f"Note: To enable full AI Brain reasoning, you need to configure your Gemini API Key in the settings. "
            f"Based on basic candlestick rules, the market is currently consolidating near {current_price}.\n\n"
            f"---\n\n"
            f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
            f"මෙය {timeframe} කාලරාමුව තුළ {symbol} සඳහා ආදර්ශ විශ්ලේෂණයකි. "
            f"සටහන: සම්පූර්ණ AI Brain විශ්ලේෂණය සක්‍රිය කිරීමට, ඔබ settings හි ඔබගේ Gemini API Key එක ඇතුලත් කල යුතුය. "
            f"මූලික candlestick නීතිවලට අනුව, වෙළඳපොළ දැනට {current_price} අසල ඒකාබද්ධ වෙමින් පවතී."
        )
        invalidation = (
            "If price breaks outside the immediate consolidated range, this neutral outlook is invalid.\n\n"
            "---\n\n"
            "**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
            "මිල ආසන්නතම ඒකාබද්ධ පරාසයෙන් පිටතට බිඳී ගියහොත්, මෙම මධ්‍යස්ථ දැක්ම වලංගු නොවේ."
        )
        risk_notes = (
            "Always use a protective stop loss. Never risk more than 1% of your account size.\n\n"
            "---\n\n"
            "**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
            "සැමවිටම ආරක්ෂිත stop loss එකක් භාවිතා කරන්න. කිසිවිටෙක ඔබේ ගිණුමේ ප්‍රමාණයෙන් 1% කට වඩා අවදානමට ලක් නොකරන්න."
        )
        
        return {
            "signal": signal,
            "confidence": confidence,
            "reasoning": reasoning,
            "invalidation": invalidation,
            "risk_notes": risk_notes
        }

    @classmethod
    async def translate_text(
        cls,
        text: str,
        api_key: Optional[str] = None
    ) -> str:
        """
        Translate English technical analysis text to Sinhala.
        """
        active_key = api_key or settings.GEMINI_API_KEY
        if not active_key:
            logger.warning("GEMINI_API_KEY not configured. Cannot translate text.")
            return ""
            
        try:
            client = genai.Client(api_key=active_key)
            prompt = (
                "You are an expert English to Sinhala translator specializing in financial markets and trading terminology. "
                "Translate the following English technical analysis or trading guidance into clear, natural, and accurate Sinhala. "
                "Ensure that terms like Order Block, CHOCH, BOS, or Fair Value Gap are translated naturally or kept as recognizable terms in Sinhala script where appropriate (e.g. 'Order Block (ඕඩර් බ්ලොක්)'). "
                "Do NOT include any introduction, explanations, notes, or quotes. Output ONLY the translated text.\n\n"
                f"Text to translate:\n{text}"
            )
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini translation failed: {e}")
            return ""

    @classmethod
    async def chat_response(
        cls,
        message: str,
        strategy_content: str,
        analysis_context: str,
        chat_history: List[Dict[str, Any]],
        api_key: Optional[str] = None
    ) -> str:
        """
        Engage in chat conversation with Gemini about the trading strategy and current market context.
        """
        active_key = api_key or settings.GEMINI_API_KEY
        if not active_key:
            return (
                "Gemini API key is not configured. Please add your Gemini API Key in the settings "
                "to talk to the AI Trading Assistant."
            )
            
        try:
            client = genai.Client(api_key=active_key)
            
            # Format chat history for prompt or construct system prompt
            system_prompt = f"""
You are the AI Brain of Project Falcon, a Personal AI Trading Assistant.
Your core mission is to help the user analyze financial markets and learn trading based on their strategies.

CRITICAL RULES:
1. Never execute or automate trades.
2. Never suggest guaranteed profits or make win rate promises.
3. You must only provide analysis and education, not financial advice.
4. Adhere strictly to the rules of the user's strategy. Do not invent new indicators or run outside analysis.
5. Provide clear, educational explanations to help the trader learn.
6. Language adaptability: Respond in the same language as the user's message. If the user asks in English, respond in English. If the user asks in Sinhala (including Singlish/transliterated Sinhala), respond in clear, user-friendly Sinhala.

-----------------------------------------
USER'S TRADING STRATEGY RULES:
{strategy_content}
-----------------------------------------

{analysis_context}
"""
            # Build history list in google-genai format
            contents = [
                types.Content(role="user", parts=[types.Part(text=system_prompt)]),
                types.Content(role="model", parts=[types.Part(text="Understood. I am Project Falcon AI Brain. I will follow your guidelines and active strategy rules.")]),
            ]
            for msg in chat_history:
                role = "user" if msg.get("sender") == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=msg.get("text", ""))]))
                
            contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
            
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=contents
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API chat failed: {e}")
            return f"Error contacting AI Brain: {str(e)}"

    @classmethod
    def _get_sb_steps(
        cls,
        kz_valid: bool,
        killzone: str,
        swept_pool: str,
        asian_sweep: bool,
        ltf_shift: bool,
        ltf_trigger: str,
        has_fresh_fvg: bool,
        mit_array: str,
        ct_locked: bool,
        setup_triggered: bool,
        entry_price: float,
        rr_ratio: float,
        conf_score: int,
        timeframe: str = "1m"
    ) -> Dict[str, Any]:
        sb_step_1_time_window_ok = kz_valid
        sb_step_1_details = (
            f"Designated {killzone} Silver Bullet Session active. | වලංගු {killzone} Silver Bullet කාලසීමාව සක්‍රීයයි."
            if kz_valid else
            "Outside of standard Silver Bullet hours (Any-Time active). | සම්මත Silver Bullet කාලසීමාවෙන් බැහැරයි (ඕනෑම වේලාවක සක්‍රීයයි)."
        )
        
        sb_step_2_liquidity_sweep_ok = (swept_pool != "NONE" or asian_sweep)
        sb_step_2_details = (
            f"Liquidity swept on {swept_pool} pool. | {swept_pool} ද්‍රවශීලතාවය sweep වී ඇත."
            if sb_step_2_liquidity_sweep_ok else
            "No liquidity sweep detected. | ද්‍රවශීලතාවය sweep වීමක් සලකුණු වී නොමැත."
        )
        
        sb_step_3_displacement_mss_ok = (ltf_shift or ltf_trigger in ["MSS", "CISD", "CHOCH"])
        sb_step_3_details = (
            f"Displacement shift ({ltf_trigger or 'MSS'}) confirmed with candle body close. | MSS/CISD ව්‍යුහය බිඳවැටීම ඉටිපන්දම් සිරුරින් (Body Close) තහවුරු කර ඇත."
            if sb_step_3_displacement_mss_ok else
            "Awaiting Market Structure Shift (MSS/CISD) body close. | MSS/CISD ඉටිපන්දම් සිරුරකින් (Body Close) තහවුරු වන තෙක් බලාපොරොත්තුවෙන්."
        )
        
        sb_step_4_fvg_bpr_ok = (has_fresh_fvg or mit_array not in ["NONE", "NONE_OB", None])
        if sb_step_4_fvg_bpr_ok:
            sb_step_4_details = f"Fair Value Gap (FVG) or {mit_array or 'OB'} array mapped. | FVG හෝ {mit_array or 'OB'} කලාපයක් හඳුනාගෙන ඇත."
        else:
            sb_step_4_details = "Awaiting fresh FVG or PD array mitigation. | FVG හෝ PD array එකක් හඳුනා ගන්නා තෙක් බලාපොරොත්තුවෙන්."
            
        sb_step_5_entry_exec_ok = (not ct_locked and setup_triggered)
        if sb_step_5_entry_exec_ok:
            sb_step_5_details = f"Entry order ready at FVG 50% CE level ({entry_price:.2f}). | FVG 50% CE ({entry_price:.2f}) මට්ටමේ ලිමිට් ඕඩරය සූදානම්."
        else:
            sb_step_5_details = "Setup locked/pending: Premium zone, above daily open, or news lockout active. | රීති අවහිරය: මිල Premium/Daily Open එකට ඉහළින් හෝ පුවත් අවහිරය සක්‍රීයයි."
            
        sb_step_6_risk_mgmt_ok = (setup_triggered and not ct_locked and rr_ratio >= 2.0 and conf_score >= 90)
        if sb_step_6_risk_mgmt_ok:
            sb_step_6_details = f"Risk management verified: SL at swept boundary, TP set at 1:4.00 RR. | SL සහ TP 1:4.00 RR අනුපාතයකට සකසා ඇත."
        else:
            sb_step_6_details = f"Risk management locked: RR profile insufficient ({rr_ratio:.2f} < 1:2 RR or confidence < 90%). | රීති අවහිරය: RR අනුපාතය හෝ තහවුරු කිරීමේ ප්‍රතිශතය ප්‍රමාණවත් නොවේ."

        # New specific YouTube video rules (Steps 7-10)
        sb_step_7_london_asian_sweep_ok = (swept_pool != "NONE" or asian_sweep)
        if sb_step_7_london_asian_sweep_ok:
            sb_step_7_details = f"Asian session liquidity taken during London Session 3-4 AM window. | Asian Session Liquidity එක London Session (3-4 AM) කාලසීමාව තුළ sweep වී ඇත."
        else:
            sb_step_7_details = f"No Asian session liquidity taken during London Session 3-4 AM. | ආසියානු සෙෂන් ද්‍රවශීලතාවය sweep වී නොමැත."

        sb_step_8_htf_pd_mitigation_ok = (mit_array not in ["NONE", "NONE_OB", None] or swept_pool in ["PDH_BSL", "PDL_SSL"])
        if sb_step_8_htf_pd_mitigation_ok:
            sb_step_8_details = f"HTF PD Array (PDL, PDH, PWH, PWL, HTF-FVG, OB, BB) mitigation confirmed. | HTF PD Array එකක් (PDL, PDH, PWH, PWL, HTF FVG, OB, BB) සාර්ථකව සපුරා ඇත."
        else:
            sb_step_8_details = f"Awaiting HTF PD Array mitigation (PDL, PDH, PWH, PWL, HTF-FVG, OB, BB). | HTF PD Array එකක් කරා මිල පැමිණෙන තෙක් බලාපොරොත්තුවෙන්."

        sb_step_9_ltf_choch_ok = sb_step_3_displacement_mss_ok
        if sb_step_9_ltf_choch_ok:
            sb_step_9_details = f"1 Min Choch (Change of Character) confirmed with candle body close and displacement. | 1 Min Choch (MSS) ව්‍යුහය බිඳවැටීම ඉටිපන්දම් සිරුරින් සහ හොඳ Displacement එකක් සමඟ තහවුරු වී ඇත."
        else:
            sb_step_9_details = f"Awaiting 1 Min Choch (candle body close and displacement) confirmation. | 1 Min Choch එකක් ඉටිපන්දම් සිරුරකින් සහ හොඳ Displacement එකක් සමඟ තහවුරු වන තෙක් බලාපොරොත්තුවෙන්."

        sb_step_10_fvg_limit_ok = sb_step_5_entry_exec_ok
        if sb_step_10_fvg_limit_ok:
            sb_step_10_details = f"Entry order placed at 1 Min FVG 50% Consequent Encroachment ({entry_price:.2f}). | 1 Min FVG 50% CE ({entry_price:.2f}) මට්ටමේ ලිමිට් ඕඩරය සකසා ඇත."
        else:
            sb_step_10_details = f"Awaiting valid entry trigger conditions at 1 Min FVG 50% CE level. | 1 Min FVG 50% CE මට්ටමේ ලිමිට් ඕඩරය සක්‍රීය වීමට කොන්දේසි සපුරා නැත."

        return {
            "sb_step_1_time_window_ok": sb_step_1_time_window_ok,
            "sb_step_1_details": sb_step_1_details,
            "sb_step_2_liquidity_sweep_ok": sb_step_2_liquidity_sweep_ok,
            "sb_step_2_details": sb_step_2_details,
            "sb_step_3_displacement_mss_ok": sb_step_3_displacement_mss_ok,
            "sb_step_3_details": sb_step_3_details,
            "sb_step_4_fvg_bpr_ok": sb_step_4_fvg_bpr_ok,
            "sb_step_4_details": sb_step_4_details,
            "sb_step_5_entry_exec_ok": sb_step_5_entry_exec_ok,
            "sb_step_5_details": sb_step_5_details,
            "sb_step_6_risk_mgmt_ok": sb_step_6_risk_mgmt_ok,
            "sb_step_6_details": sb_step_6_details,
            "sb_step_7_london_asian_sweep_ok": sb_step_7_london_asian_sweep_ok,
            "sb_step_7_details": sb_step_7_details,
            "sb_step_8_htf_pd_mitigation_ok": sb_step_8_htf_pd_mitigation_ok,
            "sb_step_8_details": sb_step_8_details,
            "sb_step_9_ltf_choch_ok": sb_step_9_ltf_choch_ok,
            "sb_step_9_details": sb_step_9_details,
            "sb_step_10_fvg_limit_ok": sb_step_10_fvg_limit_ok,
            "sb_step_10_details": sb_step_10_details
        }

    @classmethod
    async def analyze_silver_bullet(
        cls,
        req: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate market scenario against the ICT Silver Bullet strategy.
        """
        symbol = req.get("symbol") or "XAUUSD"
        timeframe = req.get("timeframe") or "1m"
        scenario_text = req.get("scenario_text") or ""
        htf_trend = req.get("htf_trend") or "UNKNOWN"
        pullback_days = req.get("pullback_days")
        pdh = req.get("pdh")
        pdl = req.get("pdl")
        daily_open = req.get("daily_open")
        daily_close = req.get("daily_close")
        asian_sweep = req.get("asian_sweep")
        demand_mitigation = req.get("demand_mitigation")
        ltf_shift = req.get("ltf_shift")
        current_price = req.get("current_price")
        
        # Advanced strategy inputs
        dealing_range_high = req.get("dealing_range_high")
        dealing_range_low = req.get("dealing_range_low")
        killzone = req.get("killzone") or "NONE"
        discount_pd_array = req.get("discount_pd_array")
        premium_pd_array = req.get("premium_pd_array")
        ltf_trigger = req.get("ltf_trigger") or "NONE"
        has_fresh_fvg = req.get("has_fresh_fvg")
        high_impact_news = req.get("high_impact_news")
        
        # Advanced 9:00 AM Candle parameters
        candle_9am_high = req.get("candle_9am_high")
        candle_9am_low = req.get("candle_9am_low")

        # Fetch news and check lockout
        news_lockout_active = False
        active_news_event = None
        upcoming_news_events = []
        
        try:
            events = await cls._fetch_economic_calendar()
            from datetime import datetime, timezone, timedelta
            now_utc = datetime.now(timezone.utc)
            
            for event in events:
                if event.get("impact") == "High" and event.get("country") == "USD":
                    try:
                        event_dt = datetime.fromisoformat(event["date"])
                        event_utc = event_dt.astimezone(timezone.utc)
                        diff_sec = (event_utc - now_utc).total_seconds()
                        
                        if abs(diff_sec) <= 3600:
                            news_lockout_active = True
                            active_news_event = event.get("title")
                            
                        if -14400 <= diff_sec <= 43200:
                            slst_dt = event_utc.astimezone(timezone(timedelta(hours=5, minutes=30)))
                            upcoming_news_events.append({
                                "title": event.get("title"),
                                "country": event.get("country"),
                                "impact": event.get("impact"),
                                "time_slst": slst_dt.strftime("%I:%M %p"),
                                "time_utc": event_utc.isoformat(),
                                "seconds_remaining": int(diff_sec)
                            })
                    except Exception as ex:
                        logger.error(f"Error parsing news event: {ex}")
            upcoming_news_events.sort(key=lambda x: x["time_utc"])
        except Exception as e:
            logger.error(f"Error evaluating news lockout: {e}")

        if news_lockout_active:
            reasoning = (
                f"No Entry (High-Impact News Lockout): {active_news_event} scheduled within +/- 60 minutes. Trade signals suppressed for risk management.\n\n"
                f"---\n\n"
                f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                f"ප්‍රධාන ආර්ථික පුවත් (High-Impact News) Lockout: {active_news_event} ප්‍රවෘත්තිය නිකුත් වීමට ආසන්න බැවින් අවදානම කළමනාකරණය සඳහා trading සංඥා අත්හිටුවා ඇත."
            )
            return {
                "is_valid": False,
                "status_message": f"No Entry (High-Impact News Lockout: {active_news_event})",
                "market_structure_status": "News Lockout\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nපුවත් අවහිරතාවය",
                "daily_bias": "NEUTRAL",
                "liquidity_target": None,
                "entry_price_area": "No Entry (High-Impact News Lockout)",
                "stop_loss_level": None,
                "target_reward_ratio": None,
                "reasoning": reasoning,
                "invalidation": "High-Impact News Lockout active.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nප්‍රධාන ආර්ථික පුවත් අවහිරතාවය සක්‍රීයයි.",
                "risk_notes": (
                    f"News event: {active_news_event} scheduled today. Per strategy rules, do not execute new positions during high-impact USD events.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"ප්‍රධාන USD පුවත්: {active_news_event} අද දිනට නියමිතයි. උපායමාර්ගික නීති අනුව, ඉහළ උච්චාවචනයක් ඇති පුවත් වේලාවන්හිදී නව positions ලබා නොගන්න."
                ),
                "equilibrium_price": None,
                "zone_type": "NEUTRAL",
                "daily_open_relation": "N/A",
                "killzone_valid": False,
                "counter_trend_locked": False,
                "erl_irl_state": "NONE",
                "swept_liquidity_pool": "NONE",
                "mitigated_pd_array_type": "NONE",
                "is_advanced_setup": False,
                "advanced_setup_status": "NONE",
                "confidence": 0,
                
                "sb_step_1_time_window_ok": False,
                "sb_step_1_details": "Blocked by economic news lockout. | ආර්ථික පුවත් අවහිරතාවය නිසා අවහිර කර ඇත.",
                "sb_step_2_liquidity_sweep_ok": False,
                "sb_step_2_details": "Blocked by economic news lockout. | ආර්ථික පුවත් අවහිරතාවය නිසා අවහිර කර ඇත.",
                "sb_step_3_displacement_mss_ok": False,
                "sb_step_3_details": "Blocked by economic news lockout. | ආර්ථික පුවත් අවහිරතාවය නිසා අවහිර කර ඇත.",
                "sb_step_4_fvg_bpr_ok": False,
                "sb_step_4_details": "Blocked by economic news lockout. | ආර්ථික පුවත් අවහිරතාවය නිසා අවහිර කර ඇත.",
                "sb_step_5_entry_exec_ok": False,
                "sb_step_5_details": "Blocked by economic news lockout. | ආර්ථික පුවත් අවහිරතාවය නිසා අවහිර කර ඇත.",
                "sb_step_6_risk_mgmt_ok": False,
                "sb_step_6_details": "Blocked by economic news lockout. | ආර්ථික පුවත් අවහිරතාවය නිසා අවහිර කර ඇත.",
                "sb_step_7_london_asian_sweep_ok": False,
                "sb_step_7_details": "Blocked by economic news lockout. | ආර්ථික පුවත් අවහිරතාවය නිසා අවහිර කර ඇත.",
                "sb_step_8_htf_pd_mitigation_ok": False,
                "sb_step_8_details": "Blocked by economic news lockout. | ආර්ථික පුවත් අවහිරතාවය නිසා අවහිර කර ඇත.",
                "sb_step_9_ltf_choch_ok": False,
                "sb_step_9_details": "Blocked by economic news lockout. | ආර්ථික පුවත් අවහිරතාවය නිසා අවහිර කර ඇත.",
                "sb_step_10_fvg_limit_ok": False,
                "sb_step_10_details": "Blocked by economic news lockout. | ආර්ථික පුවත් අවහිරතාවය නිසා අවහිර කර ඇත.",
                
                "news_lockout_active": True,
                "active_news_event": active_news_event,
                "upcoming_news_events": upcoming_news_events
            }

        # Programmatic sanity check for incomplete details
        if not scenario_text and (pdh is None or pdl is None):
            return {
                "is_valid": False,
                "status_message": "Please provide the Previous Daily High/Low details or current session structure to determine the setup.",
                "market_structure_status": "Incomplete Data\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nඅසම්පූර්ණ දත්ත",
                "daily_bias": "NEUTRAL",
                "liquidity_target": None,
                "entry_price_area": None,
                "stop_loss_level": None,
                "target_reward_ratio": None,
                "reasoning": "Previous Daily High/Low details are missing.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nපෙර දෛනික උපරිම/අවම විස්තර නොමැත.",
                "invalidation": "Incomplete Data.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nඅසම්පූර්ණ දත්ත.",
                "risk_notes": "Incomplete Data.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nඅසම්පූර්ණ දත්ත.",
                "equilibrium_price": None,
                "zone_type": "N/A",
                "daily_open_relation": "N/A",
                "killzone_valid": False,
                "counter_trend_locked": False,
                "is_advanced_setup": False,
                "advanced_setup_status": "NONE"
            }

        prompt = f"""
You are the AI Brain of Project Falcon, a Personal AI Trading Assistant.
Your task is to analyze the market scenario and price data against the **ICT Silver Bullet Strategy ({symbol})**, which is a **strict scalp trading strategy** targeting lower timeframe (M1/M3/M5) intraday expansions.

-----------------------------------------
STRATEGY RULES:
- Asset: {symbol}
- Core Logic: SMC & ICT Frameworks (Scalp Trading).
- Hunt Liquidity: PDH/PDL sweeps and HTF array mitigation.
- Premium vs. Discount Array Matrix:
  - Equilibrium line is drawn at 50% of the active Dealing Range (High to Low).
  - Premium (> 50% area): Scan ONLY for Shorts (Sells) inside Premium PD Arrays (OB, Breaker, Mitigation Block, Bearish FVG, Liquidity Void, Old Highs).
  - Discount (< 50% area): Scan ONLY for Longs (Buys) inside Discount PD Arrays.
  - BUYS are strictly prohibited in the Premium zone. SELLS are strictly prohibited in the Discount zone. If setup violates this, trigger Counter-Trend Lockout!
- Daily Open Reference Check:
  - Price above Daily Open = short-term premium. Sell setups only.
  - Price below Daily Open = short-term discount. Buy setups only.
- Strict Silver Bullet Time Ranges (NY Time vs. Local Sri Lankan Time):
  1. London Open Silver Bullet: 03:00 AM - 04:00 AM NY Time (12:30 PM - 01:30 PM Sri Lankan Time) -> Mark killzone_valid as true if killzone="LONDON" or "LONDON_SB".
  2. AM Session Silver Bullet: 10:00 AM - 11:00 AM NY Time (07:30 PM - 08:30 PM Sri Lankan Time) -> Mark killzone_valid as true if killzone="NY_AM" or "NY_AM_SB".
  3. PM Session Silver Bullet: 02:00 PM - 03:00 PM NY Time (11:30 PM - 12:30 AM Sri Lankan Time) -> Mark killzone_valid as true if killzone="NY_PM" or "NY_PM_SB".
  Transactions outside these three independent windows are invalid.
- Advanced Scenario Setup Mechanics (9:00 AM Candlestick Range Filter):
  - Applied specifically to the 10:00 AM - 11:00 AM NY AM session.
  - Requires scanning the 09:00 AM Candle High ({candle_9am_high}) and 09:00 AM Candle Low ({candle_9am_low}) on the 1H chart.
  - Advanced Buy Setup: If current_price sweeps below the 09:00 AM Candle Low, trigger a Buy Setup upon lower timeframe shift (MSS/CISD). Target is the 09:00 AM Candle High.
  - Advanced Sell Setup: If current_price sweeps above the 09:00 AM Candle High, trigger a Sell Setup upon lower timeframe shift (MSS/CISD). Target is the 09:00 AM Candle Low.
- Lower Timeframe Reconfirmation: Needs MSS (Market Structure Shift) or CISD (Change in State of Delivery) inside the Killzone on M15/M5 chart, accompanied by a fresh FVG.
- Risk/Macro Protection: Ignore/block setups if high-impact news is active (NFP, CPI, FOMC). Lock out counter-bias setups to protect account.
- Strict 1-Hour Scalp Constraints:
  1. All setups must be high-velocity scalp entries meant to complete within a maximum hold time of 1 Hour (1H).
  2. Tight Stop Loss: Place stop loss very close to the entry price (e.g. 1.5 - 2.5 points for gold-like assets) to minimize risk.
  3. Close Take Profit: Set TP targets close to the entry based strictly on 1:2 to 1:3 RR. Do not target distant levels if they are too far and cannot be filled within 1 hour.
  4. Include a 1-Hour hold time warning in the Risk Notes and their Sinhala translations.

-----------------------------------------
USER INPUT DATA:
- Raw Scenario Text: {scenario_text}
- Structured Form Data:
  * Symbol: {symbol}
  * HTF Trend: {htf_trend}
  * Pullback Days: {pullback_days}
  * Previous Daily High (PDH): {pdh}
  * Previous Daily Low (PDL): {pdl}
  * Daily Open: {daily_open}
  * Daily Close: {daily_close}
  * Asian Session Swept PDL: {asian_sweep}
  * Mitigated 15m/5m Demand Zone: {demand_mitigation}
  * London Session LTF Shift: {ltf_shift}
  * Current Price: {current_price}
  * Dealing Range High: {dealing_range_high}
  * Dealing Range Low: {dealing_range_low}
  * Killzone Session: {killzone}
  * Mitigated Discount PD Array: {discount_pd_array}
  * Mitigated Premium PD Array: {premium_pd_array}
  * LTF Trigger Type: {ltf_trigger}
  * Fresh FVG Formed: {has_fresh_fvg}
  * High Impact News Active: {high_impact_news}
  * 9:00 AM Candle High (1H): {candle_9am_high}
  * 9:00 AM Candle Low (1H): {candle_9am_low}

-----------------------------------------
YOUR TASK:
1. Validate completeness. If high/low prices are missing, set is_valid=false.
2. Calculate the 50% Fibonacci Equilibrium line: (Dealing Range High + Dealing Range Low) / 2.
3. Compare Current Price to the Equilibrium Line. Determine if price is in PREMIUM or DISCOUNT zone.
4. Compare Current Price to Daily Open. Determine if open relation is ABOVE_OPEN or BELOW_OPEN.
5. Check if the Killzone matches one of the three designated windows. Mark killzone_valid as true/false.
6. Verify trend alignment. If Daily Bias is Bullish but the current setup violates Premium/Discount rules (e.g. trying to buy in the Premium Zone, or buying above Daily Open, or counter-bias setups), mark counter_trend_locked as true, keep is_valid as true (so the details render on dashboard), force Daily Bias to NEUTRAL, and trigger Strategy Rule Lockout! Discard and auto-ignore counter-trend setups.
7. Determine the ERL vs IRL tracking state: Set "erl_irl_state" to "ERL_TO_IRL" if price swept PDH/PDL and is retracing into internal FVG/OB arrays. Set to "IRL_TO_ERL" if expanding from discount/premium arrays towards ERL targets. Otherwise "NONE".
8. Identify swept liquidity pool: Set "swept_liquidity_pool" to "PDL_SSL" if PDL/Asian lows were swept, "PDH_BSL" if PDH/Asian highs were swept, "9AM_LOW_SSL" if 9:00 AM low was swept, "9AM_HIGH_BSL" if 9:00 AM high was swept, or "NONE".
9. Identify the mitigated PD Array footprint type: Set "mitigated_pd_array_type" to one of "OB", "BREAKER", "MITIGATION", "REJECTION", "FVG", or "NONE".
10. Check if the 9:00 AM Range filter setup is active (specifically for NY_AM when 9:00 AM high/low are provided). Set "is_advanced_setup" to true, and specify "advanced_setup_status" as "NONE", "9AM_LOW_SWEPT_MSS_PENDING" (if 9:00 AM low swept but no MSS trigger), "9AM_HIGH_SWEPT_MSS_PENDING" (if 9:00 AM high swept but no MSS trigger), or "TRIGGERED" (if swept and MSS trigger is active).
11. Return bilingual explanations (English + Sinhala) for "market_structure_status", "reasoning", "invalidation", and "risk_notes".
12. Enforce minimum Risk-to-Reward (RR) threshold: The reward-to-risk ratio from entry price area to the liquidity target relative to stop loss must be at least 1:2 (2.0). If it is less than 1:2, you MUST invalidate the setup (set is_valid=false), clear all execution parameters (set entry, SL, target to null), and return a status_message stating "Strategy Lockout: Risk-to-Reward ratio is less than 1:2 minimum threshold." and include its Sinhala translation.
13. TRIPLE-VERIFICATION PROTOCOL: You MUST execute a strict sequential check of all setup parameters against the active rules (HTF Daily Bias, ERL/IRL zone, Daily Open vector relation, active Silver Bullet window, wick sweep, tight SL risk, close TP targets, news lockout, and confidence rating >= 90%) at least three separate times in a verification loop before returning a setup. State clearly in your explanations that triple-verification has successfully passed to prevent configuration errors.
14. NO ARBITRARY ENTRY/SL PROTOCOL: You MUST analyze the market structure deeply. Do NOT recommend arbitrary entries or stop losses. Ensure that a valid, close lower-timeframe (1m/3m) confirmation structure (e.g. displacement shift, candle body close MSS, and unmitigated FVG/OB arrays) is active and confirmed in the immediate vicinity of the current price. If such proximity confirmations are missing, you MUST suppress the setup and return is_valid=false or daily_bias=NEUTRAL.



-----------------------------------------
OUTPUT FORMAT:
Return a JSON object with these exact keys:
1. "is_valid": boolean
2. "status_message": string
3. "market_structure_status": string (English + Sinhala translation)
4. "daily_bias": string ("BULLISH", "BEARISH", or "NEUTRAL")
5. "liquidity_target": float or string
6. "entry_price_area": string
7. "stop_loss_level": float or string
8. "target_reward_ratio": string
9. "reasoning": string (English + Sinhala translation)
10. "invalidation": string (English + Sinhala translation)
11. "risk_notes": string (English + Sinhala translation)
12. "equilibrium_price": float (50% dealing range line)
13. "zone_type": string ("PREMIUM", "DISCOUNT", or "EQUILIBRIUM")
14. "daily_open_relation": string ("ABOVE_OPEN" or "BELOW_OPEN")
15. "killzone_valid": boolean
16. "counter_trend_locked": boolean
17. "erl_irl_state": string ("ERL_TO_IRL", "IRL_TO_ERL", or "NONE")
18. "swept_liquidity_pool": string ("PDL_SSL", "PDH_BSL", "9AM_LOW_SSL", "9AM_HIGH_BSL", or "NONE")
19. "mitigated_pd_array_type": string ("OB", "BREAKER", "MITIGATION", "REJECTION", "FVG", or "NONE")
20. "is_advanced_setup": boolean
21. "advanced_setup_status": string

OUTPUT JSON ONLY. Do not wrap in markdown blocks other than clean json formatting.
"""

        active_key = api_key or settings.GEMINI_API_KEY
        if not active_key:
            logger.warning("GEMINI_API_KEY not configured. Falling back to rule-based Silver Bullet analysis.")
            return cls._get_mock_silver_bullet(req, upcoming_news_events=upcoming_news_events)

        try:
            client = genai.Client(api_key=active_key)
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text.strip())
            
            # Calculate strategy confidence score locally based on confluences (out of 100%)
            conf_score = 0
            active_bias = result.get("daily_bias") or "NEUTRAL"
            is_htf_bullish = htf_trend.upper() == "BULLISH" or (pullback_days is not None and pullback_days >= 3)
            
            # 1. HTF Trend / Daily Bias Vector Alignment (20%)
            if (active_bias == "BULLISH" and is_htf_bullish) or (active_bias == "BEARISH" and not is_htf_bullish):
                conf_score += 20
                
            # 2. Optimal Matrix Zone (20%)
            zone = result.get("zone_type") or "N/A"
            if (active_bias == "BULLISH" and zone == "DISCOUNT") or (active_bias == "BEARISH" and zone == "PREMIUM"):
                conf_score += 20
                
            # 3. Daily Open Price Vector Relation (15%)
            open_relation = result.get("daily_open_relation") or "N/A"
            if (active_bias == "BULLISH" and open_relation == "BELOW_OPEN") or (active_bias == "BEARISH" and open_relation == "ABOVE_OPEN"):
                conf_score += 15
                
            # 4. Active Silver Bullet Session Hour (15%)
            if result.get("killzone_valid"):
                conf_score += 15
                
            # 5. Wick Liquidity Sweep (15%)
            swept_pool = result.get("swept_liquidity_pool") or "NONE"
            if swept_pool != "NONE" or asian_sweep:
                conf_score += 15
                
            # 6. LTF trigger (MSS/CISD) with FVG/BPR Unicorn (15%)
            mit_array = result.get("mitigated_pd_array_type") or "NONE"
            if active_bias in ["BULLISH", "BEARISH"] and (ltf_shift or ltf_trigger in ["MSS", "CISD", "CHOCH"]):
                if has_fresh_fvg:
                    conf_score += 15
                elif mit_array not in ["NONE", "NONE_OB", None]:
                    conf_score += 15

            # Save computed confidence score
            result["confidence"] = conf_score
            
            # Parse entry price from entry_price_area string
            entry_price_val = 0.0
            try:
                import re
                entry_match = re.search(r'(\d+(?:\.\d+)?)', result.get("entry_price_area") or "")
                if entry_match:
                    entry_price_val = float(entry_match.group(1))
            except Exception:
                pass
            
            # Parse target reward ratio
            rr_val = 4.0
            try:
                import re
                rr_match = re.search(r'1:(\d+(?:\.\d+)?)', result.get("target_reward_ratio") or "")
                if rr_match:
                    rr_val = float(rr_match.group(1))
            except Exception:
                pass

            # Generate checklist steps
            steps = cls._get_sb_steps(
                kz_valid=result.get("killzone_valid", False),
                killzone=killzone,
                swept_pool=swept_pool,
                asian_sweep=bool(asian_sweep),
                ltf_shift=bool(ltf_shift),
                ltf_trigger=ltf_trigger,
                has_fresh_fvg=bool(has_fresh_fvg),
                mit_array=mit_array,
                ct_locked=result.get("counter_trend_locked", False),
                setup_triggered=result.get("is_valid", False) and result.get("daily_bias") != "NEUTRAL",
                entry_price=entry_price_val or current_price or 0.0,
                rr_ratio=rr_val,
                conf_score=conf_score,
                timeframe=timeframe
            )
            
            # Merge steps into result
            result.update(steps)
            return result
        except Exception as e:
            logger.error(f"Gemini API Silver Bullet analysis failed: {e}. Falling back to mock analysis.")
            return cls._get_mock_silver_bullet(req, upcoming_news_events=upcoming_news_events)

    @classmethod
    def _get_tight_scalp_risk(cls, entry_price: float, symbol: str = "") -> float:
        symbol_upper = symbol.upper()
        if "XAU" in symbol_upper or "GOLD" in symbol_upper:
            return 1.8  # Gold-like assets
        else:
            # Dynamic scaling for all other crypto coins (ETH, BTC, SOL, DOGE etc. at 0.16% of price)
            val = entry_price * 0.0016
            if entry_price > 1000.0:
                return round(val, 2)
            else:
                return round(val, 4)

    @classmethod
    def _get_mock_silver_bullet(cls, req: Dict[str, Any], upcoming_news_events: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Provides a structured mock analysis for Silver Bullet strategy if API key fails."""
        if upcoming_news_events is None:
            upcoming_news_events = []
        symbol = req.get("symbol") or "XAUUSD"
        timeframe = req.get("timeframe") or "1m"
        scenario_text = req.get("scenario_text") or ""
        htf_trend = req.get("htf_trend") or "UNKNOWN"
        pullback_days = req.get("pullback_days")
        pdh = req.get("pdh")
        pdl = req.get("pdl")
        daily_open = req.get("daily_open")
        daily_close = req.get("daily_close")
        asian_sweep = req.get("asian_sweep")
        demand_mitigation = req.get("demand_mitigation")
        ltf_shift = req.get("ltf_shift")
        current_price = req.get("current_price")
        
        is_valid = True
        
        # Advanced strategy inputs
        dealing_range_high = req.get("dealing_range_high")
        dealing_range_low = req.get("dealing_range_low")
        killzone = req.get("killzone") or "NONE"
        discount_pd_array = req.get("discount_pd_array")
        premium_pd_array = req.get("premium_pd_array")
        ltf_trigger = req.get("ltf_trigger") or "NONE"
        has_fresh_fvg = req.get("has_fresh_fvg")
        high_impact_news = req.get("high_impact_news")
        
        candle_9am_high = req.get("candle_9am_high")
        candle_9am_low = req.get("candle_9am_low")

        # Extract levels if text-based scenario is provided instead
        if scenario_text and not pdh and not pdl:
            import re
            pdh_match = re.search(r'(?:pdh|previous daily high)[^\d]*(\d+(?:\.\d+)?)', scenario_text, re.IGNORECASE)
            pdl_match = re.search(r'(?:pdl|previous daily low)[^\d]*(\d+(?:\.\d+)?)', scenario_text, re.IGNORECASE)
            if pdh_match:
                pdh = float(pdh_match.group(1))
            if pdl_match:
                pdl = float(pdl_match.group(1))

        if pdh is None or pdl is None:
            return {
                "is_valid": False,
                "status_message": "Please provide the Previous Daily High/Low details or current session structure to determine the setup.",
                "market_structure_status": "Incomplete Data\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nඅසම්පූර්ණ දත්ත",
                "daily_bias": "NEUTRAL",
                "liquidity_target": None,
                "entry_price_area": None,
                "stop_loss_level": None,
                "target_reward_ratio": None,
                "reasoning": "Missing critical daily price levels (PDH/PDL).\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nඅත්‍යවශ්‍ය දෛනික මිල මට්ටම් (PDH/PDL) නොමැත.",
                "invalidation": "Cannot perform analysis without daily range context.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nදෛනික පරාසය නොමැතිව විශ්ලේෂණය කළ නොහැක.",
                "risk_notes": "Input data incomplete.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nදත්ත අසම්පූර්ණයි.",
                "equilibrium_price": None,
                "zone_type": "N/A",
                "daily_open_relation": "N/A",
                "killzone_valid": False,
                "counter_trend_locked": False,
                "is_advanced_setup": False,
                "advanced_setup_status": "NONE",
                "confidence": 0
            }

        # Calculate Equilibrium line (using dealing range boundaries, fall back to PDH/PDL)
        high_val = dealing_range_high if dealing_range_high is not None else pdh
        low_val = dealing_range_low if dealing_range_low is not None else pdl
        eq_price = (high_val + low_val) / 2.0 if (high_val is not None and low_val is not None) else None

        # Determine Premium/Discount zone
        zone = "N/A"
        if current_price is not None and eq_price is not None:
            if current_price > eq_price:
                zone = "PREMIUM"
            elif current_price < eq_price:
                zone = "DISCOUNT"
            else:
                zone = "EQUILIBRIUM"

        # Determine Daily Open Relation
        open_relation = "N/A"
        if current_price is not None and daily_open is not None:
            if current_price > daily_open:
                open_relation = "ABOVE_OPEN"
            elif current_price < daily_open:
                open_relation = "BELOW_OPEN"

        # Verify strict Silver Bullet killzone windows mapped to Sri Lankan Time (SLST)
        # London SB: 3-4AM NY / 12:30-1:30 PM LK
        # AM Session SB: 10-11AM NY / 7:30-8:30 PM LK
        # PM Session SB: 2-3PM NY / 11:30 PM-12:30 AM LK
        # Strategy confirmations are strictly evaluated on the 1m chart timeframe.
        kz_valid = killzone in ["LONDON", "LONDON_SB", "NY_AM", "NY_AM_SB", "NY_PM", "NY_PM_SB"]

        # Initialize default values to prevent unbound variable errors
        entry_price = current_price or 0.0
        stop_loss = 0.0
        target = 0.0
        rr_ratio = 4.0
        conf_score = 0
        bias = "NEUTRAL"

        # Parse text-based parameters if present
        is_htf_bullish = htf_trend.upper() == "BULLISH" or (pullback_days is not None and pullback_days >= 3)
        if scenario_text:
            text_lower = scenario_text.lower()
            if "bullish" in text_lower or "higher high" in text_lower or "pullback" in text_lower:
                is_htf_bullish = True
            elif "bearish" in text_lower or "lower low" in text_lower:
                is_htf_bullish = False
            if "sweep" in text_lower or "swept" in text_lower:
                asian_sweep = True
            if "mitigate" in text_lower or "mitigation" in text_lower or "demand" in text_lower:
                demand_mitigation = True
            if "shift" in text_lower or "choch" in text_lower or "mss" in text_lower or "displacement" in text_lower:
                ltf_shift = True
            if "london" in text_lower:
                killzone = "LONDON_SB"
            elif "ny am" in text_lower or "ny_am" in text_lower:
                killzone = "NY_AM_SB"
            elif "ny pm" in text_lower or "ny_pm" in text_lower:
                killzone = "NY_PM_SB"
            kz_valid = killzone in ["LONDON", "LONDON_SB", "NY_AM", "NY_AM_SB", "NY_PM", "NY_PM_SB"]

        # Advanced 9:00 AM Candlestick Range Filter
        is_adv = False
        adv_status = "NONE"
        swept_pool = "NONE"
        setup_direction = "NONE" # "BULLISH" (Buy) or "BEARISH" (Sell)
        
        # 9:00 AM Candlestick check applies strictly inside the 10:00 - 11:00 AM NY window
        if killzone in ["NY_AM", "NY_AM_SB"] and candle_9am_high is not None and candle_9am_low is not None:
            is_adv = True
            if current_price is not None:
                if current_price <= candle_9am_low:
                    swept_pool = "9AM_LOW_SSL"
                    setup_direction = "BULLISH"
                    if ltf_trigger in ["MSS", "CISD"] or ltf_shift:
                        adv_status = "TRIGGERED"
                    else:
                        adv_status = "9AM_LOW_SWEPT_MSS_PENDING"
                elif current_price >= candle_9am_high:
                    swept_pool = "9AM_HIGH_BSL"
                    setup_direction = "BEARISH"
                    if ltf_trigger in ["MSS", "CISD"] or ltf_shift:
                        adv_status = "TRIGGERED"
                    else:
                        adv_status = "9AM_HIGH_SWEPT_MSS_PENDING"
        else:
            # Normal Setup Direction derived from HTF bias or sweep details
            if is_htf_bullish:
                setup_direction = "BULLISH"
                if asian_sweep or (current_price is not None and pdl is not None and current_price <= pdl):
                    swept_pool = "PDL_SSL"
            else:
                setup_direction = "BEARISH"
                if asian_sweep or (current_price is not None and pdh is not None and current_price >= pdh):
                    swept_pool = "PDH_BSL"

        # Check counter trend lockout rules:
        # 1. BUYS/Longs are strictly locked in Premium (>50% line) or above Daily Open
        # 2. SELLS/Shorts are strictly locked in Discount (<50% line) or below Daily Open
        # 3. Discard and auto-ignore any setups that run counter to the active Daily Bias (HTF trend)
        ct_locked = False
        
        if setup_direction == "BULLISH":
            if zone == "PREMIUM" or open_relation == "ABOVE_OPEN":
                ct_locked = True
            # Auto-ignore counter trend
            if not is_htf_bullish:
                ct_locked = True
        elif setup_direction == "BEARISH":
            if zone == "DISCOUNT" or open_relation == "BELOW_OPEN":
                ct_locked = True
            # Auto-ignore counter trend
            if is_htf_bullish:
                ct_locked = True

        if high_impact_news:
            ct_locked = True

        # Check execution trigger criteria
        if is_adv:
            setup_triggered = (adv_status == "TRIGGERED") and not ct_locked
        else:
            setup_triggered = (
                (asian_sweep or swept_pool != "NONE") and 
                (demand_mitigation or discount_pd_array or premium_pd_array or zone == ("DISCOUNT" if setup_direction == "BULLISH" else "PREMIUM")) and 
                (ltf_shift or ltf_trigger in ["MSS", "CISD"]) and
                not ct_locked
            )

        # Set mitigated array footprint type
        mit_array = "NONE"
        if setup_direction == "BULLISH":
            if has_fresh_fvg:
                mit_array = "FVG"
            elif discount_pd_array or demand_mitigation:
                mit_array = "OB"
            else:
                mit_array = "OB" # Fallback if setup triggered
        else:
            if has_fresh_fvg:
                mit_array = "FVG"
            elif premium_pd_array:
                mit_array = "OB"
            else:
                mit_array = "OB"

        # State tracking: External (ERL) vs Internal (IRL) range liquidity
        erl_irl = "NONE"
        if swept_pool != "NONE" and setup_triggered:
            # Swept ERL and now rebalancing towards internal FVG/OB arrays
            erl_irl = "ERL_TO_IRL"
        elif setup_triggered and (discount_pd_array or premium_pd_array or has_fresh_fvg):
            # Expanding from mitigated internal array back towards target liquidity (ERL)
            erl_irl = "IRL_TO_ERL"

        if setup_triggered:
            min_risk = cls._get_tight_scalp_risk(current_price or pdl or pdh or 2320.0, symbol)
            
            if is_adv:
                if swept_pool == "9AM_LOW_SSL":
                    entry_price = current_price or ((candle_9am_low or 0.0) + min_risk)
                    stop_loss = entry_price - min_risk
                    target = entry_price + (min_risk * 4.0)
                    bias = "BULLISH"
                else:
                    entry_price = current_price or ((candle_9am_high or 0.0) - min_risk)
                    stop_loss = entry_price + min_risk
                    target = entry_price - (min_risk * 4.0)
                    bias = "BEARISH"
            else:
                if setup_direction == "BULLISH":
                    entry_price = current_price or ((pdl or 0.0) + min_risk)
                    stop_loss = entry_price - min_risk
                    target = entry_price + (min_risk * 4.0)
                    bias = "BULLISH"
                else:
                    entry_price = current_price or ((pdh or 0.0) - min_risk)
                    stop_loss = entry_price + min_risk
                    target = entry_price - (min_risk * 4.0)
                    bias = "BEARISH"
            
            # Calculate strategy confidence score based on confluences (out of 100%)
            conf_score = 0
            
            # 1. HTF Trend / Daily Bias Vector Alignment (20%)
            active_bias = bias if setup_triggered else setup_direction
            if (active_bias == "BULLISH" and is_htf_bullish) or (active_bias == "BEARISH" and not is_htf_bullish):
                conf_score += 20
                
            # 2. Optimal Matrix Zone (20%)
            if (active_bias == "BULLISH" and zone == "DISCOUNT") or (active_bias == "BEARISH" and zone == "PREMIUM"):
                conf_score += 20
                
            # 3. Daily Open Price Vector Relation (15%)
            if (active_bias == "BULLISH" and open_relation == "BELOW_OPEN") or (active_bias == "BEARISH" and open_relation == "ABOVE_OPEN"):
                conf_score += 15
                
            # 4. Active Silver Bullet Session Hour (15%)
            if kz_valid:
                conf_score += 15
                
            # 5. Wick Liquidity Sweep (15%)
            if swept_pool != "NONE" or asian_sweep:
                conf_score += 15
                
            # 6. LTF trigger (MSS/CISD) with FVG/BPR Unicorn (15%)
            if setup_triggered:
                conf_score += 15
            elif is_adv and adv_status in ["9AM_LOW_SWEPT_MSS_PENDING", "9AM_HIGH_SWEPT_MSS_PENDING"]:
                conf_score += 5
            elif swept_pool != "NONE" or asian_sweep:
                conf_score += 5

            # Enforce 90% Minimum Filter lockout
            if conf_score < 90:
                market_structure_status = (
                    f"HTF Trend is {htf_trend}, but strategy confidence is below 90% ({conf_score}%). Setup Locked.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"Trend එක {htf_trend} වුවත්, strategy තහවුරු කිරීමේ ප්‍රතිශතය 90% ට වඩා අඩුය ({conf_score}%). Setup අවහිර කර ඇත."
                )
                
                reasoning = (
                    f"No Entry Triggered because confidence score ({conf_score}%) does not meet the 90% minimum threshold.\n"
                    f"Wait for high-probability setups where all confluences align to yield >= 90% score.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"තහවුරු කිරීමේ ප්‍රතිශතය ({conf_score}%) 90% සීමාවට වඩා අඩු බැවින් entry එක ලබා දී නොමැත.\n"
                    f"90% හෝ ඊට වැඩි සම්භාවිතාවක් ඇති Setup එකක් ලැබෙන තෙක් රැඳී සිටින්න."
                )
                
                invalidation = (
                    f"Setup is locked out due to low confidence rating ({conf_score}%).\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"අඩු තහවුරු කිරීමේ මට්ටම ({conf_score}%) නිසා setup එක වලංගු නොවේ."
                )
                
                risk_notes = (
                    f"Execution locked due to low confidence score ({conf_score}%). Do not enter trades.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"අඩු තහවුරු කිරීමේ මට්ටම ({conf_score}%) නිසා ගනුදෙනුව අවහිර කර ඇත. Trade එකට ඇතුල් නොවන්න."
                )
                
                steps = cls._get_sb_steps(
                    kz_valid=kz_valid,
                    killzone=killzone,
                    swept_pool=swept_pool,
                    asian_sweep=asian_sweep,
                    ltf_shift=ltf_shift,
                    ltf_trigger=ltf_trigger,
                    has_fresh_fvg=has_fresh_fvg,
                    mit_array=mit_array,
                    ct_locked=ct_locked,
                    setup_triggered=setup_triggered,
                    entry_price=entry_price,
                    rr_ratio=rr_ratio,
                    conf_score=conf_score,
                    timeframe=timeframe
                )
                sb_step_1_time_window_ok = steps["sb_step_1_time_window_ok"]
                sb_step_1_details = steps["sb_step_1_details"]
                sb_step_2_liquidity_sweep_ok = steps["sb_step_2_liquidity_sweep_ok"]
                sb_step_2_details = steps["sb_step_2_details"]
                sb_step_3_displacement_mss_ok = steps["sb_step_3_displacement_mss_ok"]
                sb_step_3_details = steps["sb_step_3_details"]
                sb_step_4_fvg_bpr_ok = steps["sb_step_4_fvg_bpr_ok"]
                sb_step_4_details = steps["sb_step_4_details"]
                sb_step_5_entry_exec_ok = steps["sb_step_5_entry_exec_ok"]
                sb_step_5_details = steps["sb_step_5_details"]
                sb_step_6_risk_mgmt_ok = steps["sb_step_6_risk_mgmt_ok"]
                sb_step_6_details = steps["sb_step_6_details"]

                return {
                    "is_valid": True,
                    "status_message": f"Strategy Lockout: Confidence score ({conf_score}%) is below 90% minimum threshold.",
                    "market_structure_status": market_structure_status,
                    "daily_bias": "NEUTRAL",
                    "liquidity_target": None,
                    "entry_price_area": "No Entry (Confidence < 90%)",
                    "stop_loss_level": None,
                    "target_reward_ratio": "N/A",
                    "reasoning": reasoning,
                    "invalidation": invalidation,
                    "risk_notes": risk_notes,
                    "equilibrium_price": eq_price,
                    "zone_type": zone,
                    "daily_open_relation": open_relation,
                    "killzone_valid": kz_valid,
                    "counter_trend_locked": True,
                    "erl_irl_state": "NONE",
                    "swept_liquidity_pool": swept_pool,
                    "mitigated_pd_array_type": mit_array,
                    "is_advanced_setup": is_adv,
                    "advanced_setup_status": adv_status,
                    "sb_step_1_time_window_ok": sb_step_1_time_window_ok,
                    "sb_step_1_details": sb_step_1_details,
                    "sb_step_2_liquidity_sweep_ok": sb_step_2_liquidity_sweep_ok,
                    "sb_step_2_details": sb_step_2_details,
                    "sb_step_3_displacement_mss_ok": sb_step_3_displacement_mss_ok,
                    "sb_step_3_details": sb_step_3_details,
                    "sb_step_4_fvg_bpr_ok": sb_step_4_fvg_bpr_ok,
                    "sb_step_4_details": sb_step_4_details,
                    "sb_step_5_entry_exec_ok": sb_step_5_entry_exec_ok,
                    "sb_step_5_details": sb_step_5_details,
                    "sb_step_6_risk_mgmt_ok": sb_step_6_risk_mgmt_ok,
                    "sb_step_6_details": sb_step_6_details,
                    "sb_step_7_london_asian_sweep_ok": steps["sb_step_7_london_asian_sweep_ok"],
                    "sb_step_7_details": steps["sb_step_7_details"],
                    "sb_step_8_htf_pd_mitigation_ok": steps["sb_step_8_htf_pd_mitigation_ok"],
                    "sb_step_8_details": steps["sb_step_8_details"],
                    "sb_step_9_ltf_choch_ok": steps["sb_step_9_ltf_choch_ok"],
                    "sb_step_9_details": steps["sb_step_9_details"],
                    "sb_step_10_fvg_limit_ok": steps["sb_step_10_fvg_limit_ok"],
                    "sb_step_10_details": steps["sb_step_10_details"],
                    "confidence": conf_score
                }

            # Calculate Risk-to-Reward ratio based on natural target before strict 1:3 RR expansion
            natural_risk = abs(entry_price - stop_loss)
            if bias == "BULLISH":
                natural_target = pdh if pdh is not None else candle_9am_high if candle_9am_high is not None else target
            else:
                natural_target = pdl if pdl is not None else candle_9am_low if candle_9am_low is not None else target
            natural_reward = abs(natural_target - entry_price)
            natural_rr = natural_reward / natural_risk if natural_risk > 0 else 0.0
            
            if natural_rr < 2.0:
                reasons = [f"Risk-to-Reward ratio ({natural_rr:.2f}) is less than 1:2 minimum threshold"]
                reason_str = ", ".join(reasons)
                
                market_structure_status = (
                    f"HTF structure is {htf_trend}, but setup is locked. Setup Locked: True.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"ප්‍රධාන Trend එක {htf_trend} වුවත්, setup එක අවහිර වී ඇත. Setup අවහිර වීම: True."
                )
                
                reasoning = (
                    f"The Daily Bias is NEUTRAL because: Risk-to-Reward ratio ({natural_rr:.2f}) is less than 1:2 minimum threshold.\n"
                    f"Wait for a valid sweep/mitigation inside London, NY AM, or NY PM Silver Bullet windows that offers at least 1:2 RR.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"ගණනය කරන ලද Risk-to-Reward ratio එක ({natural_rr:.2f}) අවම 1:2 සීමාවට වඩා අඩු බැවින් Daily Bias එක මධ්‍යස්ථ (NEUTRAL) වේ.\n"
                    f"වලංගු London, NY AM, හෝ NY PM Silver Bullet window එකක් ඇතුළත අවම 1:2 RR සහිත setup එකක් ලැබෙන තෙක් රැඳී සිටින්න."
                )
                
                invalidation = (
                    f"Setup is invalidated because the logical target does not justify the stop loss size under strict scalp management rules.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"දැඩි scalp කළමනාකරණ රීති යටතේ Stop Loss ප්‍රමාණයට සාපේක්ෂව මෙම ඉලක්කය ප්‍රමාණවත් නොවන බැවින් setup එක වලංගු නොවේ."
                )
                
                risk_notes = (
                    f"Execution locked due to poor Risk-to-Reward profile. Do not enter trades. News Release check: {high_impact_news}.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"අඩු Risk-to-Reward මට්ටම නිසා ගනුදෙනුව අවහිර කර ඇත. Trade එකට ඇතුල් නොවන්න. ප්‍රධාන පුවත්: {high_impact_news}."
                )
                
                steps = cls._get_sb_steps(
                    kz_valid=kz_valid,
                    killzone=killzone,
                    swept_pool=swept_pool,
                    asian_sweep=asian_sweep,
                    ltf_shift=ltf_shift,
                    ltf_trigger=ltf_trigger,
                    has_fresh_fvg=has_fresh_fvg,
                    mit_array=mit_array,
                    ct_locked=ct_locked,
                    setup_triggered=setup_triggered,
                    entry_price=entry_price,
                    rr_ratio=natural_rr,
                    conf_score=conf_score,
                    timeframe=timeframe
                )
                sb_step_1_time_window_ok = steps["sb_step_1_time_window_ok"]
                sb_step_1_details = steps["sb_step_1_details"]
                sb_step_2_liquidity_sweep_ok = steps["sb_step_2_liquidity_sweep_ok"]
                sb_step_2_details = steps["sb_step_2_details"]
                sb_step_3_displacement_mss_ok = steps["sb_step_3_displacement_mss_ok"]
                sb_step_3_details = steps["sb_step_3_details"]
                sb_step_4_fvg_bpr_ok = steps["sb_step_4_fvg_bpr_ok"]
                sb_step_4_details = steps["sb_step_4_details"]
                sb_step_5_entry_exec_ok = steps["sb_step_5_entry_exec_ok"]
                sb_step_5_details = steps["sb_step_5_details"]
                sb_step_6_risk_mgmt_ok = steps["sb_step_6_risk_mgmt_ok"]
                sb_step_6_details = steps["sb_step_6_details"]

                return {
                    "is_valid": True,
                    "status_message": "Strategy Lockout: Risk-to-Reward ratio is less than 1:2 minimum threshold.",
                    "market_structure_status": market_structure_status,
                    "daily_bias": "NEUTRAL",
                    "liquidity_target": None,
                    "entry_price_area": "No Entry Triggered (Poor RR)",
                    "stop_loss_level": None,
                    "target_reward_ratio": "N/A",
                    "reasoning": reasoning,
                    "invalidation": invalidation,
                    "risk_notes": risk_notes,
                    "equilibrium_price": eq_price,
                    "zone_type": zone,
                    "daily_open_relation": open_relation,
                    "killzone_valid": kz_valid,
                    "counter_trend_locked": True,
                    "erl_irl_state": "NONE",
                    "swept_liquidity_pool": swept_pool,
                    "mitigated_pd_array_type": mit_array,
                    "is_advanced_setup": is_adv,
                    "advanced_setup_status": adv_status,
                    
                    # Detailed 6-Step Silver Bullet fields
                    "sb_step_1_time_window_ok": sb_step_1_time_window_ok,
                    "sb_step_1_details": sb_step_1_details,
                    "sb_step_2_liquidity_sweep_ok": sb_step_2_liquidity_sweep_ok,
                    "sb_step_2_details": sb_step_2_details,
                    "sb_step_3_displacement_mss_ok": sb_step_3_displacement_mss_ok,
                    "sb_step_3_details": sb_step_3_details,
                    "sb_step_4_fvg_bpr_ok": sb_step_4_fvg_bpr_ok,
                    "sb_step_4_details": sb_step_4_details,
                    "sb_step_5_entry_exec_ok": sb_step_5_entry_exec_ok,
                    "sb_step_5_details": sb_step_5_details,
                    "sb_step_6_risk_mgmt_ok": sb_step_6_risk_mgmt_ok,
                    "sb_step_6_details": sb_step_6_details,
                    "sb_step_7_london_asian_sweep_ok": steps["sb_step_7_london_asian_sweep_ok"],
                    "sb_step_7_details": steps["sb_step_7_details"],
                    "sb_step_8_htf_pd_mitigation_ok": steps["sb_step_8_htf_pd_mitigation_ok"],
                    "sb_step_8_details": steps["sb_step_8_details"],
                    "sb_step_9_ltf_choch_ok": steps["sb_step_9_ltf_choch_ok"],
                    "sb_step_9_details": steps["sb_step_9_details"],
                    "sb_step_10_fvg_limit_ok": steps["sb_step_10_fvg_limit_ok"],
                    "sb_step_10_details": steps["sb_step_10_details"],
                    "confidence": conf_score
                }
            
            # Recalculate strict 1:4 Risk-to-Reward parameters if needed
            risk = abs(entry_price - stop_loss)
            if risk > 0:
                if bias == "BULLISH":
                    target = entry_price + (risk * 4.0)
                else:
                    target = entry_price - (risk * 4.0)
            
            reward = abs(target - entry_price)
            rr_ratio = reward / risk if risk > 0 else 4.0
            
            action_type = "Buy Limit" if bias == "BULLISH" else "Sell Limit"
            
            if is_valid:
                market_structure_status = (
                    f"HTF structure is {bias}. Price has swept {swept_pool} in a valid execution window. Confirming a valid lower timeframe (M1/M5) scalp trading setup with FVG.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"ප්‍රධාන Trend එක {bias} තියෙන්නේ. මිල {swept_pool} sweep කරලා, වලංගු Silver Bullet window එකක් ඇතුළත පිහිටා ඇත. FVG එකක් සමඟ වලංගු කෙටි කාලීන (scalp) trade setup එකක් සනාථ වී තිබේ."
                )
            
            reasoning = (
                f"1. Daily structure bias locks to {bias}. Price is trading in the optimal matrix zone ({zone}) relative to Equilibrium ({eq_price:.2f}).\n"
                f"2. Daily Open relation is aligned ({open_relation}), confirming institutional discount/premium pricing vectors.\n"
                f"3. Active session is inside the valid Silver Bullet window ({killzone}), with a successful liquidity raid on {swept_pool}.\n"
                f"4. Lower Timeframe trigger ({ltf_trigger or 'MSS'}) confirmed, signaling institutional momentum expansion towards {target:.2f}.\n\n"
                f"---\n\n"
                f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                f"1. ප්‍රධාන දෛනික Bias එක {bias} ලෙස ස්ථිර වී තිබේ. මිල Equilibrium ({eq_price:.2f}) මට්ටමට සාපේක්ෂව කලාපයේ ({zone}) පවතී.\n"
                f"2. Daily Open සබඳතාව ({open_relation}) දෛනික මට්ටම් වලට අනුකූල වේ.\n"
                f"3. ගනුදෙනුව වලංගු Silver Bullet window ({killzone}) ඇතුළත වන අතර, {swept_pool} මට්ටම සාර්ථකව sweep කර ඇත.\n"
                f"4. LTF shift ({ltf_trigger or 'MSS'}) එක fresh FVG සමඟ තහවුරු වී ඇති අතර මිල {target:.2f} ඉලක්කය කරා ගමන් කරයි."
            )
            
            invalidation = (
                f"Setup is invalidated if price breaches the sweep boundary at {stop_loss:.2f} before triggering limit entry, or if macro structure shifts counter-bias.\n\n"
                f"---\n\n"
                f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                f"මිල {stop_loss:.2f} sweep boundary මට්ටමෙන් ඔබ්බට ගියහොත් හෝ macro structure එක වෙනස් වුවහොත් මෙම setup එක වලංගු නොවේ."
            )
            
            risk_notes = (
                f"Scalp trade risk strictly 0.5% - 1.0% maximum per trade. Max holding duration: 10m - 15m. Stop Loss at {stop_loss:.2f}, Target at {target:.2f} (1:{rr_ratio:.2f} RR). High-Impact News: {high_impact_news}.\n\n"
                f"---\n\n"
                f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                f"Scalp trade එකක් බැවින් එක් trade එකකට උපරිම 0.5% - 1.0% ක් පමණක් අවදානමට ලක් කරන්න. උපරිම රඳවා ගැනීමේ කාලය: විනාඩි 10 - 15 (10m - 15m). Stop Loss එක {stop_loss:.2f} මට්ටමේද, Target එක {target:.2f} මට්ටමේද තබන්න (1:{rr_ratio:.2f} RR). ප්‍රධාන පුවත්: {high_impact_news}."
            )
            
            # Define 6-step checklist values
            steps = cls._get_sb_steps(
                kz_valid=kz_valid,
                killzone=killzone,
                swept_pool=swept_pool,
                asian_sweep=asian_sweep,
                ltf_shift=ltf_shift,
                ltf_trigger=ltf_trigger,
                has_fresh_fvg=has_fresh_fvg,
                mit_array=mit_array,
                ct_locked=ct_locked,
                setup_triggered=setup_triggered,
                entry_price=entry_price,
                rr_ratio=rr_ratio,
                conf_score=conf_score,
                timeframe=timeframe
            )
            sb_step_1_time_window_ok = steps["sb_step_1_time_window_ok"]
            sb_step_1_details = steps["sb_step_1_details"]
            sb_step_2_liquidity_sweep_ok = steps["sb_step_2_liquidity_sweep_ok"]
            sb_step_2_details = steps["sb_step_2_details"]
            sb_step_3_displacement_mss_ok = steps["sb_step_3_displacement_mss_ok"]
            sb_step_3_details = steps["sb_step_3_details"]
            sb_step_4_fvg_bpr_ok = steps["sb_step_4_fvg_bpr_ok"]
            sb_step_4_details = steps["sb_step_4_details"]
            sb_step_5_entry_exec_ok = steps["sb_step_5_entry_exec_ok"]
            sb_step_5_details = steps["sb_step_5_details"]
            sb_step_6_risk_mgmt_ok = steps["sb_step_6_risk_mgmt_ok"]
            sb_step_6_details = steps["sb_step_6_details"]

            return {
                "is_valid": True,
                "status_message": "Success",
                "market_structure_status": market_structure_status,
                "daily_bias": bias,
                "liquidity_target": target,
                "entry_price_area": f"{action_type} at {entry_price:.2f}",
                "stop_loss_level": stop_loss,
                "target_reward_ratio": f"1:{rr_ratio:.2f}",
                "reasoning": reasoning,
                "invalidation": invalidation,
                "risk_notes": risk_notes,
                "equilibrium_price": eq_price,
                "zone_type": zone,
                "daily_open_relation": open_relation,
                "killzone_valid": kz_valid,
                "counter_trend_locked": ct_locked,
                "erl_irl_state": erl_irl,
                "swept_liquidity_pool": swept_pool,
                "mitigated_pd_array_type": mit_array,
                "is_advanced_setup": is_adv,
                "advanced_setup_status": adv_status,
                "confidence": conf_score,
                "news_lockout_active": False,
                "active_news_event": None,
                "upcoming_news_events": upcoming_news_events,
                
                # Detailed 6-Step Silver Bullet fields
                "sb_step_1_time_window_ok": sb_step_1_time_window_ok,
                "sb_step_1_details": sb_step_1_details,
                "sb_step_2_liquidity_sweep_ok": sb_step_2_liquidity_sweep_ok,
                "sb_step_2_details": sb_step_2_details,
                "sb_step_3_displacement_mss_ok": sb_step_3_displacement_mss_ok,
                "sb_step_3_details": sb_step_3_details,
                "sb_step_4_fvg_bpr_ok": sb_step_4_fvg_bpr_ok,
                "sb_step_4_details": sb_step_4_details,
                "sb_step_5_entry_exec_ok": sb_step_5_entry_exec_ok,
                "sb_step_5_details": sb_step_5_details,
                "sb_step_6_risk_mgmt_ok": sb_step_6_risk_mgmt_ok,
                "sb_step_6_details": sb_step_6_details,
                "sb_step_7_london_asian_sweep_ok": steps["sb_step_7_london_asian_sweep_ok"],
                "sb_step_7_details": steps["sb_step_7_details"],
                "sb_step_8_htf_pd_mitigation_ok": steps["sb_step_8_htf_pd_mitigation_ok"],
                "sb_step_8_details": steps["sb_step_8_details"],
                "sb_step_9_ltf_choch_ok": steps["sb_step_9_ltf_choch_ok"],
                "sb_step_9_details": steps["sb_step_9_details"],
                "sb_step_10_fvg_limit_ok": steps["sb_step_10_fvg_limit_ok"],
                "sb_step_10_details": steps["sb_step_10_details"]
            }
        else:
            reasons = []
            if not kz_valid:
                reasons.append(f"Outside of valid Silver Bullet session windows (Current: {killzone})")
            if ct_locked:
                if high_impact_news:
                    reasons.append("High-impact news event is currently active")
                else:
                    reasons.append(f"Counter-trend / Counter-bias lockout active (Price: {zone}, Relation: {open_relation}, Daily Bias: {htf_trend})")
            if is_adv:
                if adv_status == "9AM_LOW_SWEPT_MSS_PENDING":
                    reasons.append("9:00 AM Low swept, but lower timeframe MSS structure shift is pending")
                elif adv_status == "9AM_HIGH_SWEPT_MSS_PENDING":
                    reasons.append("9:00 AM High swept, but lower timeframe MSS structure shift is pending")
                else:
                    reasons.append("Waiting for 9:00 AM candle range high/low sweep check")
            else:
                if not asian_sweep and swept_pool == "NONE": reasons.append("No Asian Session / PDL / PDH sweep detected")
                if not (demand_mitigation or discount_pd_array or premium_pd_array): reasons.append("No HTF PD Array mitigation or zone mitigation detected")
                if not (ltf_shift or ltf_trigger in ["MSS", "CISD"]): reasons.append("Lower timeframe structural shift (MSS/CISD) is missing")

            reason_str = ", ".join(reasons)
            
            market_structure_status = (
                f"HTF structure is {htf_trend}, but setup conditions are incomplete or counter-bias. Setup Locked: {ct_locked}.\n\n"
                f"---\n\n"
                f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                f"ප්‍රධාන Trend එක {htf_trend} වුවත්, setup එක සම්පූර්ණ වීමට අවශ්‍ය කොන්දේසි සපුරා නොමැත. Setup අවහිර වීම: {ct_locked}."
            )
            
            reasoning = (
                f"The Daily Bias is NEUTRAL because setup conditions are incomplete or locked: {reason_str}.\n"
                f"Wait for a valid sweep/mitigation inside London, NY AM, or NY PM Silver Bullet windows with a LTF shift (MSS/CISD) aligned with HTF bias.\n\n"
                f"---\n\n"
                f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                f"පහත සඳහන් setup කොන්දේසි සම්පූර්ණ නොවීම හෝ අවහිර වීම නිසා Daily Bias එක මධ්‍යස්ථ (NEUTRAL) වේ: {reason_str}.\n"
                f"වලංගු London, NY AM, හෝ NY PM Silver Bullet window එකක් ඇතුළත sweep/mitigation එකක් සිදුවී, LTF shift (MSS/CISD) එකක් සිදුවන තෙක් රැඳී සිටින්න."
            )
            
            invalidation = (
                f"No active setup to validate yet. Rule lockout state: {ct_locked}.\n\n"
                f"---\n\n"
                f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                f"වලංගු කිරීමට සක්‍රීය setup එකක් තවමත් නොමැත. රීති අවහිර කිරීම් තත්ත්වය: {ct_locked}."
            )
            
            risk_notes = (
                f"Execution locked or neutral. Do not enter trades. News Release check: {high_impact_news}.\n\n"
                f"---\n\n"
                f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                f"ගනුදෙනුව අවහිර කර හෝ මධ්‍යස්ථව ඇත. Trade එකට ඇතුල් නොවන්න. ප්‍රධාන පුවත්: {high_impact_news}."
            )
            
            pot_entry = "No Entry Triggered"
            pot_sl = None
            pot_target = pdh
            pot_rr = "N/A"

            min_risk = cls._get_tight_scalp_risk(current_price or pdl or pdh or 2320.0, symbol)

            if is_adv and adv_status in ["9AM_LOW_SWEPT_MSS_PENDING", "9AM_HIGH_SWEPT_MSS_PENDING"] and candle_9am_high and candle_9am_low:
                if adv_status == "9AM_LOW_SWEPT_MSS_PENDING":
                    pe = current_price or ((candle_9am_low or 0.0) + min_risk)
                    psl = pe - min_risk
                    pt = pe + (min_risk * 4.0)
                    pot_label = "Est. Buy Limit"
                else:
                    pe = current_price or ((candle_9am_high or 0.0) - min_risk)
                    psl = pe + min_risk
                    pt = pe - (min_risk * 4.0)
                    pot_label = "Est. Sell Limit"
                
                risk = abs(pe - psl)
                reward = abs(pt - pe)
                pot_rr_val = reward / risk if risk > 0 else 0.0
                if pot_rr_val < 2.0:
                    pot_entry = "No Entry Triggered (Poor RR)"
                    pot_sl = None
                    pot_target = pdh
                    pot_rr = "N/A"
                    reasons.append(f"Potential setup yields poor Risk-to-Reward ratio ({pot_rr_val:.2f})")
                else:
                    pot_entry = f"{pot_label} at {pe:.2f}"
                    pot_sl = round(psl, 2)
                    pot_target = round(pt, 2)
                    pot_rr = f"1:{pot_rr_val:.2f} (Est.)"
            elif not is_adv and swept_pool != "NONE":
                if setup_direction == "BULLISH":
                    pe = current_price or ((pdl or 0.0) + min_risk)
                    psl = pe - min_risk
                    pt = pe + (min_risk * 4.0)
                    pot_label = "Est. Buy Limit"
                else:
                    pe = current_price or ((pdh or 0.0) - min_risk)
                    psl = pe + min_risk
                    pt = pe - (min_risk * 4.0)
                    pot_label = "Est. Sell Limit"
                
                risk = abs(pe - psl)
                reward = abs(pt - pe)
                pot_rr_val = reward / risk if risk > 0 else 0.0
                if pot_rr_val < 2.0:
                    pot_entry = "No Entry Triggered (Poor RR)"
                    pot_sl = None
                    pot_target = pdh
                    pot_rr = "N/A"
                    reasons.append(f"Potential setup yields poor Risk-to-Reward ratio ({pot_rr_val:.2f})")
                else:
                    pot_entry = f"{pot_label} at {pe:.2f}"
                    pot_sl = round(psl, 2)
                    pot_target = round(pt, 2)
                    pot_rr = f"1:{pot_rr_val:.2f} (Est.)"

            # Calculate potential setup confidence score
            conf_score = 0
            active_bias = setup_direction
            if (active_bias == "BULLISH" and is_htf_bullish) or (active_bias == "BEARISH" and not is_htf_bullish):
                conf_score += 20
            if (active_bias == "BULLISH" and zone == "DISCOUNT") or (active_bias == "BEARISH" and zone == "PREMIUM"):
                conf_score += 20
            if (active_bias == "BULLISH" and open_relation == "BELOW_OPEN") or (active_bias == "BEARISH" and open_relation == "ABOVE_OPEN"):
                conf_score += 15
            if kz_valid:
                conf_score += 15
            if swept_pool != "NONE" or asian_sweep:
                conf_score += 15
            if is_adv and adv_status in ["9AM_LOW_SWEPT_MSS_PENDING", "9AM_HIGH_SWEPT_MSS_PENDING"]:
                conf_score += 5
            elif swept_pool != "NONE" or asian_sweep:
                conf_score += 5

            if conf_score < 90:
                pot_entry = "No Entry (Confidence < 90%)"
                pot_sl = None
                pot_target = None
                pot_rr = "N/A"
                if "Strategy confidence score is below 90%" not in reasons:
                    reasons.append(f"Strategy confidence score ({conf_score}%) is below 90% minimum confluence threshold")

            if reasons:
                reason_str = ", ".join(reasons)
                market_structure_status = (
                    f"HTF structure is {htf_trend}, but setup conditions are incomplete or counter-bias. Setup Locked: {ct_locked}.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"ප්‍රධාන Trend එක {htf_trend} වුවත්, setup එක සම්පූර්ණ වීමට අවශ්‍ය කොන්දේසි සපුරා නොමැත. Setup අවහිර වීම: {ct_locked}."
                )
                
                reasoning = (
                    f"The Daily Bias is NEUTRAL because setup conditions are incomplete or locked: {reason_str}.\n"
                    f"Wait for a valid sweep/mitigation inside London, NY AM, or NY PM Silver Bullet windows with a LTF shift (MSS/CISD) aligned with HTF bias.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"පහත සඳහන් setup කොන්දේසි සම්පූර්ණ නොවීම හෝ අවහිර වීම නිසා Daily Bias එක මධ්‍යස්ථ (NEUTRAL) වේ: {reason_str}.\n"
                    f"වලංගු London, NY AM, හෝ NY PM Silver Bullet window එකක් ඇතුළත sweep/mitigation එකක් සිදුවී, LTF shift (MSS/CISD) එකක් සිදුවන තෙක් රැඳී සිටින්න."
                )

            # Define 6-step checklist values
            steps = cls._get_sb_steps(
                kz_valid=kz_valid,
                killzone=killzone,
                swept_pool=swept_pool,
                asian_sweep=asian_sweep,
                ltf_shift=ltf_shift,
                ltf_trigger=ltf_trigger,
                has_fresh_fvg=has_fresh_fvg,
                mit_array="NONE",
                ct_locked=ct_locked,
                setup_triggered=setup_triggered,
                entry_price=pot_entry if isinstance(pot_entry, (int, float)) else (current_price or 0.0),
                rr_ratio=4.0 if setup_triggered else 0.0,
                conf_score=conf_score,
                timeframe=timeframe
            )
            sb_step_1_time_window_ok = steps["sb_step_1_time_window_ok"]
            sb_step_1_details = steps["sb_step_1_details"]
            sb_step_2_liquidity_sweep_ok = steps["sb_step_2_liquidity_sweep_ok"]
            sb_step_2_details = steps["sb_step_2_details"]
            sb_step_3_displacement_mss_ok = steps["sb_step_3_displacement_mss_ok"]
            sb_step_3_details = steps["sb_step_3_details"]
            sb_step_4_fvg_bpr_ok = steps["sb_step_4_fvg_bpr_ok"]
            sb_step_4_details = steps["sb_step_4_details"]
            sb_step_5_entry_exec_ok = steps["sb_step_5_entry_exec_ok"]
            sb_step_5_details = steps["sb_step_5_details"]
            sb_step_6_risk_mgmt_ok = steps["sb_step_6_risk_mgmt_ok"]
            sb_step_6_details = steps["sb_step_6_details"]

            return {
                "is_valid": True,
                "status_message": "Success",
                "market_structure_status": market_structure_status,
                "daily_bias": "NEUTRAL",
                "liquidity_target": pot_target,
                "entry_price_area": pot_entry,
                "stop_loss_level": pot_sl,
                "target_reward_ratio": pot_rr,
                "reasoning": reasoning,
                "invalidation": invalidation,
                "risk_notes": risk_notes,
                "equilibrium_price": eq_price,
                "zone_type": zone,
                "daily_open_relation": open_relation,
                "killzone_valid": kz_valid,
                "counter_trend_locked": ct_locked,
                "erl_irl_state": "NONE",
                "swept_liquidity_pool": swept_pool,
                "mitigated_pd_array_type": "NONE",
                "is_advanced_setup": is_adv,
                "advanced_setup_status": adv_status,
                "confidence": conf_score,
                "news_lockout_active": False,
                "active_news_event": None,
                "upcoming_news_events": upcoming_news_events,
                
                # Detailed 6-Step Silver Bullet fields
                "sb_step_1_time_window_ok": sb_step_1_time_window_ok,
                "sb_step_1_details": sb_step_1_details,
                "sb_step_2_liquidity_sweep_ok": sb_step_2_liquidity_sweep_ok,
                "sb_step_2_details": sb_step_2_details,
                "sb_step_3_displacement_mss_ok": sb_step_3_displacement_mss_ok,
                "sb_step_3_details": sb_step_3_details,
                "sb_step_4_fvg_bpr_ok": sb_step_4_fvg_bpr_ok,
                "sb_step_4_details": sb_step_4_details,
                "sb_step_5_entry_exec_ok": sb_step_5_entry_exec_ok,
                "sb_step_5_details": sb_step_5_details,
                "sb_step_6_risk_mgmt_ok": sb_step_6_risk_mgmt_ok,
                "sb_step_6_details": sb_step_6_details,
                "sb_step_7_london_asian_sweep_ok": steps["sb_step_7_london_asian_sweep_ok"],
                "sb_step_7_details": steps["sb_step_7_details"],
                "sb_step_8_htf_pd_mitigation_ok": steps["sb_step_8_htf_pd_mitigation_ok"],
                "sb_step_8_details": steps["sb_step_8_details"],
                "sb_step_9_ltf_choch_ok": steps["sb_step_9_ltf_choch_ok"],
                "sb_step_9_details": steps["sb_step_9_details"],
                "sb_step_10_fvg_limit_ok": steps["sb_step_10_fvg_limit_ok"],
                "sb_step_10_details": steps["sb_step_10_details"]
            }


class NewsService:
    @staticmethod
    async def fetch_news() -> List[Dict[str, Any]]:
        """
        Fetch and parse latest cryptocurrency news from Cointelegraph RSS Feed.
        """
        import xml.etree.ElementTree as ET
        import re
        import html
        
        url = "https://cointelegraph.com/rss"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                
                # Parse XML
                root = ET.fromstring(response.content)
                
                news_items = []
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    
                    # Try to get image from enclosure
                    image_url = ""
                    enclosure = item.find('enclosure')
                    if enclosure is not None:
                        image_url = enclosure.attrib.get('url', '')
                        
                    # Fallback to media:content
                    if not image_url:
                        media_content = item.find('{http://search.yahoo.com/mrss/}content')
                        if media_content is not None:
                            image_url = media_content.attrib.get('url', '')
                            
                    # Parse description to strip HTML
                    raw_desc = item.find('description').text if item.find('description') is not None else ""
                    clean_desc = re.sub(r'<[^<]+?>', '', raw_desc)
                    clean_desc = html.unescape(clean_desc).strip()
                    
                    # Fallback image if none found in enclosure but exists in html description
                    if not image_url:
                        # Find any img src in raw_desc
                        img_match = re.search(r'src="([^"]+)"', raw_desc)
                        if img_match:
                            image_url = img_match.group(1)
                            
                    news_items.append({
                        "title": html.unescape(title).strip(),
                        "link": link.strip(),
                        "pubDate": pub_date.strip(),
                        "imageUrl": image_url.strip(),
                        "description": clean_desc
                    })
                return news_items[:15]
            except Exception as e:
                logger.error(f"Error fetching RSS news: {e}")
                # Return static fallback news in case of timeout/network errors
                return [
                    {
                        "title": "Strike launches Bitcoin loans amid bear market",
                        "link": "https://cointelegraph.com",
                        "pubDate": "Wed, 08 Jul 2026 02:40:13 +0000",
                        "imageUrl": "",
                        "description": "The cost of eliminating margin calls and forced liquidations is an interest rate as high as 14.2%."
                    },
                    {
                        "title": "SEC crypto rule changes are high on its 2026 agenda",
                        "link": "https://cointelegraph.com",
                        "pubDate": "Wed, 08 Jul 2026 01:30:00 +0000",
                        "imageUrl": "",
                        "description": "The SEC has outlined its regulatory priorities for the upcoming fiscal year."
                    }
                ]

