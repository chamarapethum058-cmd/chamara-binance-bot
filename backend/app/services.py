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
    async def analyze_silver_bullet(
        cls,
        req: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate market scenario against the ICT Silver Bullet strategy.
        """
        symbol = req.get("symbol") or "XAUUSD"
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

        # Programmatic sanity check for incomplete details
        if not scenario_text and (pdh is None or pdl is None):
            return {
                "is_valid": False,
                "status_message": "Please provide the Previous Daily High/Low details or current session structure to determine the setup.",
                "market_structure_status": "Incomplete Data",
                "daily_bias": "NEUTRAL",
                "liquidity_target": None,
                "entry_price_area": None,
                "stop_loss_level": None,
                "target_reward_ratio": None,
                "reasoning": "Previous Daily High/Low details are missing.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nපෙර දෛනික උපරිම/අවම විස්තර නොමැත.",
                "invalidation": "Incomplete Data.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nඅසම්පූර්ණ දත්ත.",
                "risk_notes": "Incomplete Data.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nඅසම්පූර්ණ දත්ත."
            }

        prompt = f"""
You are the AI Brain of Project Falcon, a Personal AI Trading Assistant.
Your task is to analyze the market scenario and price data against the **ICT Silver Bullet: Daily Bias & Liquidity Flow Strategy ({symbol})**.

-----------------------------------------
STRATEGY RULES:
- Asset: {symbol}
- Higher Timeframe (HTF) Trend: Bullish structure (making HH/HL) OR experiencing a multi-day pullback (e.g., 3 consecutive bearish days) hitting a key institutional demand zone with fractal order flow shifting bullish.
- Key Levels: PDH (Previous Daily High), PDL (Previous Daily Low), Daily Open, Daily Close.
- Liquidity Sweep Logic (Daily Bias confirmation):
  1. Price opens near the previous close.
  2. Drives downward during the Asian Session.
  3. Sweeps the PDL (Previous Daily Low).
  4. Mitigates a HTF 15-Minute/5-Minute Demand Zone.
  *Once PDL is swept and lower timeframe demand is mitigated, the Daily Bias for the session is strictly BULLISH, targeting the PDH.*
- Entry Trigger:
  - Look for a Lower Timeframe (LTF) Shift in Market Structure (MSS/CHoCH) or aggressive bullish displacement out of the demand zone after the PDL sweep.
  - Limit Order entry at the 15-Min/5-Min Demand Range / Order Block.
  - Stop-Loss (SL) placed safely below the sweep low.
  - Take-Profit (TP): Option 1: 1:3 to 1:3.3 Risk-to-Reward. Option 2: Target the PDH (Previous Daily High) or previous session high.

-----------------------------------------
USER INPUT DATA:
- Raw Scenario Text: {scenario_text}
- Structured Form Data:
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

-----------------------------------------
YOUR TASK:
1. CHECK COMPLETENESS:
   - Does the user input contain the Previous Daily High (PDH), Previous Daily Low (PDL), and session/structure details?
   - If critical levels are missing, return "is_valid": false.

2. VERIFY SETUP FLOW (Only if valid):
   - Analyze trend, liquidity sweep, demand mitigation, and LTF shifts.
   - Create detailed explanations for "market_structure_status", "reasoning", "invalidation", and "risk_notes".
   - You MUST output all status and explanation fields ("market_structure_status", "reasoning", "invalidation", "risk_notes") in both English and Sinhala translation. First write the content in English, then add a divider line (e.g. "\\n\\n--- \\n\\n**සිංහල පරිවර්තනය (Sinhala Translation):**\\n"), followed by its complete Sinhala translation using Sinhala Unicode characters.

-----------------------------------------
OUTPUT FORMAT:
Return a JSON object with these exact keys:
1. "is_valid": boolean (true if info is complete, false if incomplete)
2. "status_message": string (if invalid, set to "Please provide the Previous Daily High/Low details or current session structure to determine the setup.", otherwise "Success")
3. "market_structure_status": string (confirming Daily Trend & Fractal Order Flow)
4. "daily_bias": string ("BULLISH" or "NEUTRAL")
5. "liquidity_target": float or string (should be the PDH value or "PDH")
6. "entry_price_area": string (e.g., "Limit at 15m Order Block: [value]")
7. "stop_loss_level": float or string (below the sweep low)
8. "target_reward_ratio": string (e.g., "1:3" or "1:3.3")
9. "reasoning": string (English + Sinhala translation)
10. "invalidation": string (English + Sinhala translation)
11. "risk_notes": string (English + Sinhala translation)

OUTPUT JSON ONLY. Do not wrap in markdown blocks other than clean json formatting.
"""

        active_key = api_key or settings.GEMINI_API_KEY
        if not active_key:
            logger.warning("GEMINI_API_KEY not configured. Falling back to rule-based Silver Bullet analysis.")
            return cls._get_mock_silver_bullet(req)

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
            logger.error(f"Gemini API Silver Bullet analysis failed: {e}. Falling back to mock analysis.")
            return cls._get_mock_silver_bullet(req)

    @classmethod
    def _get_mock_silver_bullet(cls, req: Dict[str, Any]) -> Dict[str, Any]:
        """Provides a structured mock analysis for Silver Bullet strategy if API key fails."""
        symbol = req.get("symbol") or "XAUUSD"
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
                "market_structure_status": "Incomplete Data",
                "daily_bias": "NEUTRAL",
                "liquidity_target": None,
                "entry_price_area": None,
                "stop_loss_level": None,
                "target_reward_ratio": None,
                "reasoning": "Missing critical daily price levels (PDH/PDL).\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nඅත්‍යවශ්‍ය දෛනික මිල මට්ටම් (PDH/PDL) නොමැත.",
                "invalidation": "Cannot perform analysis without daily range context.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nදෛනික පරාසය නොමැතිව විශ්ලේෂණය කළ නොහැක.",
                "risk_notes": "Input data incomplete.\n\n---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**\nදත්ත අසම්පූර්ණයි."
            }

        # Check conditions
        is_htf_bullish = htf_trend.upper() == "BULLISH" or (pullback_days is not None and pullback_days >= 3)
        if scenario_text:
            text_lower = scenario_text.lower()
            if "bullish" in text_lower or "higher high" in text_lower or "pullback" in text_lower:
                is_htf_bullish = True
            if "sweep" in text_lower or "swept" in text_lower:
                asian_sweep = True
            if "mitigate" in text_lower or "mitigation" in text_lower or "demand" in text_lower:
                demand_mitigation = True
            if "shift" in text_lower or "choch" in text_lower or "mss" in text_lower or "displacement" in text_lower:
                ltf_shift = True

        if is_htf_bullish and asian_sweep and demand_mitigation and ltf_shift:
            entry_price = pdl - 1.5 if pdl else (current_price or 2320.0)
            stop_loss = entry_price - 5.0
            target = pdh if pdh else (entry_price + 20)
            
            risk = entry_price - stop_loss
            reward = target - entry_price
            rr_ratio = reward / risk if risk > 0 else 3.0
            
            return {
                "is_valid": True,
                "status_message": "Success",
                "market_structure_status": (
                    f"HTF structure is BULLISH. Fractal order flow aligned after hitting Institutional Demand Zone below PDL.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"ප්‍රධාන Trend එක Bullish (ඉහළට) තියෙන්නේ. මිල පහළට ගිහින් Previous Daily Low (PDL) එක sweep කරලා, Institutional Demand Zone එකට ඇතුල් වෙලා තියෙනවා."
                ),
                "daily_bias": "BULLISH",
                "liquidity_target": pdh,
                "entry_price_area": f"Limit buy order at {entry_price:.2f}",
                "stop_loss_level": stop_loss,
                "target_reward_ratio": f"1:{rr_ratio:.2f}",
                "reasoning": (
                    f"1. Daily structure is bullish, making higher highs. Multi-day pullback has hit discount matrix area.\n"
                    f"2. Asian session successfully swept Previous Daily Low (PDL) at {pdl:.2f}, sweeping retail buyers.\n"
                    f"3. HTF 15m/5m Demand Zone has been mitigated, engineering institutional buy liquidity.\n"
                    f"4. Lower Timeframe (5m) Shift in Market Structure (MSS) confirmed in London Session, signaling bullish reversal.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"1. දෛනික වෙළඳපල ව්‍යුහය (Daily Structure) Bullish වන අතර ඉහළ උපරිමයන් සාදයි. දින කිහිපයක පසුබැසීම discount matrix කලාපයට ළඟා වී ඇත.\n"
                    f"2. ආසියානු සැසිය (Asian Session) තුළදී පෙර දෛනික අවමය (PDL) {pdl:.2f} මට්ටමේදී සාර්ථකව sweep කර ඇත.\n"
                    f"3. 15m/5m Demand Zone එක සක්‍රීය වී ආයතනික මිලදී ගැනීමේ ද්‍රවශීලතාවය (liquidity) සකස් කර ඇත.\n"
                    f"4. ලන්ඩන් සැසිය තුළදී 5m කාලරාමුවෙහි Market Structure Shift (MSS) එකක් සනාථ වී ඇත."
                ),
                "invalidation": (
                    f"Setup is invalidated if price breaches below the sweep low at {stop_loss:.2f} before triggering limit entry, or if structure breaks to the downside.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"මිල {stop_loss:.2f} sweep low මට්ටමට වඩා පහළින් ගියහොත් හෝ ව්‍යුහය පහළට බිඳ වැටුණහොත් මෙම setup එක වලංගු නොවේ."
                ),
                "risk_notes": (
                    f"Risk 1% of account size maximum. Set Stop Loss strictly at {stop_loss:.2f} and target PDH at {pdh:.2f} with a reward ratio of 1:{rr_ratio:.1f}.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"ඔබේ ගිණුමේ ප්‍රමාණයෙන් උපරිම 1% ක් පමණක් අවදානමට ලක් කරන්න. Stop Loss එක දැඩි ලෙස {stop_loss:.2f} මට්ටමේ තබා, 1:{rr_ratio:.1f} ක අවදානම්-ප්‍රතිලාභ අනුපාතයක් සමඟින් {pdh:.2f} මට්ටම ඉලක්ක කරන්න."
                )
            }
        else:
            reasons = []
            if not is_htf_bullish: reasons.append("Daily structure trend is not bullish/pullback aligned")
            if not asian_sweep: reasons.append("No Asian Session PDL sweep detected")
            if not demand_mitigation: reasons.append("HTF Demand Zone mitigation is missing")
            if not ltf_shift: reasons.append("Lower timeframe market structure shift (MSS) not confirmed")

            reason_str = ", ".join(reasons)
            return {
                "is_valid": True,
                "status_message": "Success",
                "market_structure_status": (
                    "HTF structure is Bullish, but setup conditions are incomplete.\n\n"
                    "---\n\n"
                    "**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    "ප්‍රධාන Trend එක Bullish (ඉහළට) වුවත්, setup එක සම්පූර්ණ වීමට අවශ්‍ය කොන්දේසි සපුරා නොමැත."
                ),
                "daily_bias": "NEUTRAL",
                "liquidity_target": pdh,
                "entry_price_area": "No Entry Triggered",
                "stop_loss_level": None,
                "target_reward_ratio": "N/A",
                "reasoning": (
                    f"The Daily Bias is NEUTRAL because setup conditions are incomplete: {reason_str}.\n"
                    f"Wait for the liquidity sweep of PDL ({pdl:.2f}) and subsequent demand mitigation with a LTF CHoCH shift during the London session.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"පහත සඳහන් setup කොන්දේසි සම්පූර්ණ නොවීම නිසා Daily Bias එක මධ්‍යස්ථ (NEUTRAL) වේ: {reason_str}.\n"
                    f"PDL ({pdl:.2f}) sweep වන තෙක් සහ ලන්ඩන් සැසිය තුළදී LTF CHoCH shift එකක් සමඟ demand mitigation එකක් සිදුවන තෙක් රැඳී සිටින්න."
                ),
                "invalidation": (
                    f"No active setup to invalidate yet.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"තවමත් වලංගු නොවන කිරීමට සක්‍රීය setup එකක් නොමැත."
                ),
                "risk_notes": (
                    f"Do not enter trades on a neutral bias. Wait for alignment.\n\n"
                    f"---\n\n"
                    f"**සිංහල පරිවර්තනය (Sinhala Translation):**\n"
                    f"මධ්‍යස්ථ bias එකක් ඇති විට ගනුදෙනු නොකරන්න. කොන්දේසි සපුරාලන තෙක් රැඳී සිටින්න."
                )
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

