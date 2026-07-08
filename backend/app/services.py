import httpx
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
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
        strategy_content: str
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
3. "reasoning": Comprehensive text explaining your technical observations (market structure, trend, key levels, volume) and how they map to the strategy rules. Act as a teacher.
4. "invalidation": Clear conditions under which this setup or analysis is considered wrong, along with recommended Stop Loss placement guidelines.
5. "risk_notes": Explicit warnings about trading risk, high volatility warnings, and position size suggestions (e.g. keeping risk to 1%).

OUTPUT JSON ONLY. Do not wrap in markdown blocks other than clean json formatting.
"""

        # Check for Gemini API key
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not configured. Falling back to mock technical analysis.")
            return cls._get_mock_analysis(symbol, timeframe, current_price)
            
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Request response in JSON format
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
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
            f"Based on basic candlestick rules, the market is currently consolidating near {current_price}."
        )
        invalidation = "If price breaks outside the immediate consolidated range, this neutral outlook is invalid."
        risk_notes = "Always use a protective stop loss. Never risk more than 1% of your account size."
        
        return {
            "signal": signal,
            "confidence": confidence,
            "reasoning": reasoning,
            "invalidation": invalidation,
            "risk_notes": risk_notes
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

