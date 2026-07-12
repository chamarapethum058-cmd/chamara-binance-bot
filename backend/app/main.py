from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from .database import engine, Base, get_db
from .models import StrategyModel, AnalysisModel, PreferenceModel
from .schemas import (
    StrategyCreate, StrategyResponse, 
    AnalysisRequest, AnalysisResponse,
    PreferenceCreate, PreferenceResponse,
    ChatRequest, TranslateRequest,
    SilverBulletRequest, SilverBulletResponse
)
from .services import BinanceService, AIService, NewsService
from .config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Falcon Backend", version="1.0.0")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize default strategy if empty
@app.on_event("startup")
def startup_populate():
    db = next(get_db())
    
    # Check if SMC exists, if not seed it
    smc_exists = db.query(StrategyModel).filter(StrategyModel.name == "SMC (Smart Money Concepts)").first()
    if not smc_exists:
        default_smc = StrategyModel(
            name="SMC (Smart Money Concepts)",
            description="Smart Money Concepts strategy analyzing BOS, CHOCH, FVG, and Order Blocks.",
            content="""# Smart Money Concepts (SMC) Strategy

## 1. Timeframes & Scope
- Symbol: BTC/USDT, ETH/USDT, SOL/USDT
- High Timeframe (HTF): 4-Hour (Market Trend / Major Levels)
- Low Timeframe (LTF): 15-Minute (Entry confirmation and setups)

## 2. Core Trading Indicators & Structural Elements
- BOS (Break of Structure): Continuation of the trend.
- CHOCH (Change of Character): Reversal point of the trend.
- FVG (Fair Value Gap): Candlestick imbalances where price was delivered inefficiently.
- Order Blocks (OB): Last opposite candle before a strong structural expansion.

## 3. Entry Rules (Long/Bullish Setup)
1. HTF must be in an overall bullish structure, or tap into a 4H Bullish Order Block / FVG discount zone.
2. Wait for a Bullish CHOCH (break of swing high) on the 15M chart.
3. Identify the 15M Bullish Order Block or FVG that caused the CHOCH.
4. Set limit entry at the open/50% level of that 15M Order Block or at the top of the FVG.

## 4. Exit / Invalidation Rules
- Stop Loss: Placed directly below the swing low that initiated the CHOCH.
- Take Profit: Target the nearest key high (liquidity pool) or 4H premium range.
- Minimum Risk-to-Reward Ratio: 1:3.
- Invalidation: If price breaches below the swing low before our entry is triggered, the setup is invalid.
""",
            is_active=True
        )
        db.add(default_smc)
        db.commit()
        print("Default SMC strategy populated.")
        
    # Check if ICT Silver Bullet exists, if not seed it
    sb_exists = db.query(StrategyModel).filter(StrategyModel.name == "ICT Silver Bullet").first()
    if not sb_exists:
        # Deactivate other strategies to make this one the primary active strategy
        db.query(StrategyModel).update({StrategyModel.is_active: False})
        default_sb = StrategyModel(
            name="ICT Silver Bullet",
            description="Specialized multi-asset trading strategy using Premium/Discount Equilibrium, Daily Open relation, Killzones, and lower timeframe MSS/CISD + FVG confirmations.",
            content="""# ICT Silver Bullet & Liquidity Flow Strategy Spec

## 1. General System Framework
- Target Asset: Multi-Asset Support (e.g., SOL, BTC, GOLD, Forex).
- Core Logic: Smart Money Concepts (SMC) & Inner Circle Trader (ICT) Frameworks.
- System Goal: Automatically identify Daily Bias, filter entries via institutional liquidity arrays, and validate mechanical execution protocols.

## 2. Core Theoretical Modules (The Input Logic)

### Module A: Market Nature & Drivers
Price moves based on the 4 core pillars of price delivery:
1. Hunt Liquidity (Seek & Destroy): Price seeks liquidity pools to trigger stops and fill institutional orders.
2. Re-balance Inefficiencies: Price constantly mitigates unmitigated Fair Value Gaps (FVGs) and Liquidity Voids.
3. Engineered Liquidity: Price builds Buy-Side (BSL) and Sell-Side (SSL) pools (Equal Highs/Lows, Trendline Liquidity).
4. Rebalancing Equilibrium: Price expands/retraces between Premium and Discount matrices within designated dealing ranges.

### Module B: Proximity Logic & Liquidity Magnets
- Rule: Locate nearest major liquidity pools (PDH/PDL, PWH/PWL, or Major Equal Highs/Lows).
- Condition: If price is closer to BSL, active bias remains Bullish until taken. If closer to SSL, active bias remains Bearish until cleared.

### Module C: Premium vs. Discount Array Matrix
- Rule: Map active dealing range using outermost swing high/low. Draw 50% Equilibrium Line.
- Premium (> 50% Area): Search for Short (Sell) setups only. Scan for Premium Arrays: Order Blocks (OB), Breaker Blocks, Mitigation Blocks, Rejection Blocks, Bearish FVGs, Liquidity Voids, or Old Highs.
- Discount (< 50% Area): Search for Long (Buy) setups only. Scan for Discount PD Arrays in reverse.

## 3. Day-Trading Execution Protocols (The Live Analysis Logic)

### Step 1: Determine the Higher Timeframe (HTF) Daily Bias
- Weekly & Daily chart structure (HH/HL = Bullish, LH/LL = Bearish).
- Pullback & Fractal Flow: If Bullish but undergoes short-term pullback (3+ consecutive daily bearish candles down into HTF Demand/Discount Array), track the Fractal Order Flow switch. Once Fractal Order Flow turns bullish inside the demand zone, switch back to a strict Bullish Daily Bias.

### Step 2: Intraday Open & Session Manipulations
- Daily Open Reference Check:
  - Trading ABOVE Daily Open = Short-term premium pricing. Filter for Short setups hitting Premium arrays.
  - Trading BELOW Daily Open = Short-term discount pricing. Filter for Long setups hitting Discount arrays.
- Time-of-Day Filter (Strict Killzone Restrictions):
  - London Killzone: 2:00 AM – 5:00 AM New York (NY) Time.
  - New York AM Killzone: 7:00 AM – 10:00 AM NY Time.
  - Expect stops run/sweep first (Manipulation phase) inside the Killzone before the actual expansion move.

### Step 3: Lower Timeframe (LTF) Reconfirmation & Entry
Drop to M15/M5 inside Killzones after HTF Bias confirms:
- MSS (Market Structure Shift): Price aggressively breaks swing point of pullback leg with candle body close.
- CISD (Change in State of Delivery): Price closes past the open/close body boundaries of the counter-trend candle inside the demand array.
- Entry: Execute Limit Order at the 15-Min / 5-Min Demand Range or fresh FVG formed right at the MSS/CISD point. Ignore counter-bias setups.

## 4. Rigid Risk Profile & Trade Management Rules
- Stop-Loss (SL): Positioned mechanically right below the structural sweep low (clearing PDL/SSL).
- Take-Profit (TP):
  - Option A: Fixed 1:3 to 1:3.3 Risk-to-Reward (RR) ratio.
  - Option B: Target opposing PDH/PDL (Opposing Liquidity Zone).
- Macro Protection: Avoid entries against high-impact news acceleration waves (NFP, CPI, FOMC). Monitor USD Index (USDX) inverse correlation.
""",
            is_active=True
        )
        db.add(default_sb)
        db.commit()
        print("Default ICT Silver Bullet strategy populated.")
    
    # Seed default Gemini API Key from settings if not set in DB
    pref = db.query(PreferenceModel).filter(PreferenceModel.key == "gemini_api_key").first()
    if not pref and settings.GEMINI_API_KEY:
        db_pref = PreferenceModel(key="gemini_api_key", value=settings.GEMINI_API_KEY)
        db.add(db_pref)
        db.commit()
        print("Default Gemini API Key preference seeded from settings (.env).")

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "Project Falcon API"}

# STRATEGY ENDPOINTS
@app.get("/api/strategies", response_model=List[StrategyResponse])
def list_strategies(db: Session = Depends(get_db)):
    return db.query(StrategyModel).all()

@app.post("/api/strategies", response_model=StrategyResponse)
def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    # Check if name exists
    existing = db.query(StrategyModel).filter(StrategyModel.name == strategy.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Strategy with this name already exists"
        )
    
    # If active, deactivate others
    if strategy.is_active:
        db.query(StrategyModel).update({StrategyModel.is_active: False})
        
    db_strategy = StrategyModel(**strategy.dict())
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy

@app.get("/api/strategies/{strategy_id}", response_model=StrategyResponse)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    db_strategy = db.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return db_strategy

@app.put("/api/strategies/{strategy_id}/activate", response_model=StrategyResponse)
def activate_strategy(strategy_id: int, db: Session = Depends(get_db)):
    db_strategy = db.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Deactivate all other strategies
    db.query(StrategyModel).update({StrategyModel.is_active: False})
    
    # Activate selected strategy
    db_strategy.is_active = True
    db.commit()
    db.refresh(db_strategy)
    return db_strategy

@app.delete("/api/strategies/{strategy_id}")
def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    db_strategy = db.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Do not allow deleting the last remaining active strategy
    if db_strategy.is_active:
        next_strat = db.query(StrategyModel).filter(StrategyModel.id != strategy_id).first()
        if next_strat:
            next_strat.is_active = True
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot delete the active strategy when it is the only one."
            )
            
    db.delete(db_strategy)
    db.commit()
    return {"detail": "Strategy deleted successfully"}

# PREFERENCE ENDPOINTS
@app.get("/api/preferences", response_model=List[PreferenceResponse])
def get_preferences(db: Session = Depends(get_db)):
    return db.query(PreferenceModel).all()

@app.post("/api/preferences", response_model=PreferenceResponse)
def set_preference(pref: PreferenceCreate, db: Session = Depends(get_db)):
    db_pref = db.query(PreferenceModel).filter(PreferenceModel.key == pref.key).first()
    if db_pref:
        db_pref.value = pref.value
    else:
        db_pref = PreferenceModel(key=pref.key, value=pref.value)
        db.add(db_pref)
    db.commit()
    db.refresh(db_pref)
    return db_pref

# TRANSLATION ENDPOINTS
@app.post("/api/translate")
async def translate_text_endpoint(req: TranslateRequest, db: Session = Depends(get_db)):
    pref = db.query(PreferenceModel).filter(PreferenceModel.key == "gemini_api_key").first()
    api_key = pref.value if pref else None
    
    translated = await AIService.translate_text(req.text, api_key=api_key)
    return {"translated": translated}

# NEWS ENDPOINTS
@app.get("/api/news")
async def get_crypto_news():
    try:
        return await NewsService.fetch_news()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ANALYSIS ENDPOINTS
@app.get("/api/analysis/history", response_model=List[AnalysisResponse])
def get_analysis_history(db: Session = Depends(get_db)):
    # Return latest analyses first
    return db.query(AnalysisModel).order_by(AnalysisModel.timestamp.desc()).limit(50).all()

@app.post("/api/analysis/trigger", response_model=AnalysisResponse)
async def trigger_analysis(req: AnalysisRequest, db: Session = Depends(get_db)):
    # 1. Retrieve the selected or active strategy
    strategy = None
    if req.custom_strategy_id:
        strategy = db.query(StrategyModel).filter(StrategyModel.id == req.custom_strategy_id).first()
    
    if not strategy:
        strategy = db.query(StrategyModel).filter(StrategyModel.is_active == True).first()
        
    if not strategy:
        raise HTTPException(status_code=400, detail="No active strategy found in database.")
    
    # 2. Fetch live market data from Binance
    try:
        klines = await BinanceService.fetch_klines(symbol=req.symbol, interval=req.timeframe, limit=100)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Market data fetch error: {str(e)}")
    
    # 2.5. Get API Key from DB preferences if exists
    pref = db.query(PreferenceModel).filter(PreferenceModel.key == "gemini_api_key").first()
    api_key = pref.value if pref else None

    # 3. Request analysis from AI Brain
    analysis_result = await AIService.analyze_market(
        symbol=req.symbol,
        timeframe=req.timeframe,
        klines=klines,
        strategy_content=strategy.content,
        api_key=api_key
    )
    
    # 4. Save analysis to history database
    db_analysis = AnalysisModel(
        symbol=req.symbol.upper(),
        timeframe=req.timeframe,
        signal=analysis_result.get("signal", "NEUTRAL"),
        confidence=analysis_result.get("confidence", 50),
        reasoning=analysis_result.get("reasoning", ""),
        invalidation=analysis_result.get("invalidation", ""),
        risk_notes=analysis_result.get("risk_notes", ""),
        chart_data=json.dumps(klines[-30:]) # Save last 30 candles for chart redraw
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return db_analysis


@app.post("/api/chat")
async def chat_with_ai(req: ChatRequest, db: Session = Depends(get_db)):
    # 1. Retrieve the active strategy
    strategy = db.query(StrategyModel).filter(StrategyModel.is_active == True).first()
    strategy_content = strategy.content if strategy else "No active strategy rules configured."
    
    # 2. Retrieve the active analysis context if an analysis_id is provided
    analysis_context = ""
    if req.analysis_id:
        analysis = db.query(AnalysisModel).filter(AnalysisModel.id == req.analysis_id).first()
        if analysis:
            analysis_context = (
                f"Active Analysis Context:\n"
                f"- Symbol: {analysis.symbol}\n"
                f"- Timeframe: {analysis.timeframe}\n"
                f"- Current Signal: {analysis.signal}\n"
                f"- Confidence Level: {analysis.confidence}%\n"
                f"- Reasoning: {analysis.reasoning}\n"
                f"- Invalidation rules: {analysis.invalidation}\n"
                f"- Risk warnings: {analysis.risk_notes}\n"
            )
            
    # 3. Get API Key from DB preferences if exists
    pref = db.query(PreferenceModel).filter(PreferenceModel.key == "gemini_api_key").first()
    api_key = pref.value if pref else None
    
    # 4. Fetch dynamic chat response from Gemini
    response_text = await AIService.chat_response(
        message=req.message,
        strategy_content=strategy_content,
        analysis_context=analysis_context,
        chat_history=req.history or [],
        api_key=api_key
    )
    
    return {"response": response_text}


@app.post("/api/silverbullet/analyze", response_model=SilverBulletResponse)
async def silverbullet_analyze(req: SilverBulletRequest, db: Session = Depends(get_db)):
    # Retrieve Gemini API Key from DB
    pref = db.query(PreferenceModel).filter(PreferenceModel.key == "gemini_api_key").first()
    api_key = pref.value if pref else None
    
    # Run analysis
    result = await AIService.analyze_silver_bullet(req.dict(), api_key=api_key)
    
    # Ensure correct format in response
    return SilverBulletResponse(
        is_valid=result.get("is_valid", False),
        status_message=result.get("status_message") or "Success",
        market_structure_status=result.get("market_structure_status"),
        daily_bias=result.get("daily_bias"),
        liquidity_target=result.get("liquidity_target"),
        entry_price_area=result.get("entry_price_area"),
        stop_loss_level=result.get("stop_loss_level"),
        target_reward_ratio=result.get("target_reward_ratio"),
        reasoning=result.get("reasoning"),
        invalidation=result.get("invalidation"),
        risk_notes=result.get("risk_notes"),
        
        # Advanced strategy computed variables
        equilibrium_price=result.get("equilibrium_price"),
        zone_type=result.get("zone_type"),
        daily_open_relation=result.get("daily_open_relation"),
        killzone_valid=result.get("killzone_valid"),
        counter_trend_locked=result.get("counter_trend_locked"),
        
        # Antigravity Master Spec fields
        erl_irl_state=result.get("erl_irl_state"),
        swept_liquidity_pool=result.get("swept_liquidity_pool"),
        mitigated_pd_array_type=result.get("mitigated_pd_array_type")
    )


import httpx

SYMBOL_MAP = {
    "GOLD": "GC=F",
    "XAUUSD": "GC=F",
    "XAU/USD": "GC=F",
    "EURUSD": "EURUSD=X",
    "EUR/USD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "AUDUSD": "AUDUSD=X",
    "USDJPY": "JPY=X",
}

async def fetch_yahoo_finance(yahoo_symbol: str):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?interval=1d&range=2d"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers, timeout=5.0)
        if res.status_code != 200:
            raise Exception(f"Yahoo Finance returned status {res.status_code}")
        data = res.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            raise Exception("No Yahoo Finance chart result found")
            
        quote = result[0].get("indicators", {}).get("quote", [{}])[0]
        meta = result[0].get("meta", {})
        
        opens = quote.get("open", [])
        highs = quote.get("high", [])
        lows = quote.get("low", [])
        closes = quote.get("close", [])
        
        if not highs or not lows:
            raise Exception("Incomplete quote data from Yahoo Finance")
            
        if len(highs) == 1:
            pdh = float(highs[0]) if highs[0] is not None else 0.0
            pdl = float(lows[0]) if lows[0] is not None else 0.0
            open_val = float(opens[0]) if opens[0] is not None else 0.0
            close_val = float(closes[0]) if closes[0] is not None else 0.0
            curr_price = float(meta.get("regularMarketPrice", close_val))
        else:
            pdh = float(highs[0]) if highs[0] is not None else 0.0
            pdl = float(lows[0]) if lows[0] is not None else 0.0
            open_val = float(opens[0]) if opens[0] is not None else 0.0
            close_val = float(closes[0]) if closes[0] is not None else 0.0
            curr_price = float(meta.get("regularMarketPrice") or closes[1] or close_val)
            
        return {
            "symbol": yahoo_symbol,
            "pdh": pdh,
            "pdl": pdl,
            "open": open_val,
            "close": close_val,
            "current_price": curr_price
        }

@app.get("/api/market/price")
async def get_market_price(symbol: str):
    symbol_upper = symbol.strip().upper()
    if not symbol_upper:
        raise HTTPException(status_code=400, detail="Symbol parameter is required")
        
    # 1. Try Yahoo Finance mapping
    yahoo_symbol = SYMBOL_MAP.get(symbol_upper)
    if yahoo_symbol:
        try:
            return await fetch_yahoo_finance(yahoo_symbol)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch Yahoo Finance: {str(e)}")
            
    # 2. Try Binance (assuming crypto)
    binance_symbol = symbol_upper
    if not binance_symbol.endswith("USDT") and len(binance_symbol) <= 5:
        binance_symbol = f"{binance_symbol}USDT"
        
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={binance_symbol}&interval=1d&limit=2"
            res = await client.get(url, timeout=5.0)
            if res.status_code == 200:
                data = res.json()
                if len(data) >= 2:
                    prev_candle = data[0]
                    curr_candle = data[1]
                    return {
                        "symbol": symbol_upper,
                        "pdh": float(prev_candle[2]),
                        "pdl": float(prev_candle[3]),
                        "open": float(prev_candle[1]),
                        "close": float(prev_candle[4]),
                        "current_price": float(curr_candle[4])
                    }
        except Exception:
            pass
            
        # 3. Fallback: try Yahoo Finance as {symbol}-USD
        try:
            return await fetch_yahoo_finance(f"{symbol_upper}-USD")
        except Exception:
            try:
                return await fetch_yahoo_finance(symbol_upper)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to fetch market data for {symbol}: {str(e)}")


