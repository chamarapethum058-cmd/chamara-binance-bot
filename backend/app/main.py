from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from .database import engine, Base, get_db
from .models import StrategyModel, AnalysisModel, PreferenceModel, LoggedTradeModel
from .schemas import (
    StrategyCreate, StrategyResponse, 
    AnalysisRequest, AnalysisResponse,
    PreferenceCreate, PreferenceResponse,
    ChatRequest, TranslateRequest,
    SilverBulletRequest, SilverBulletResponse,
    LoggedTradeCreate, LoggedTradeResponse
)
from .services import BinanceService, AIService, NewsService
from .config import settings
from .tracker import start_tracking, stop_tracking, get_trackers_status

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
            description="Ultimate scalp trading specification for multi-timeframe bias and execution assistant (London Open, AM Session, PM Session, and 9:00 AM range sweep mechanics).",
            content="""# ULTIMATE SYSTEM SPECIFICATION DOCUMENT (FINAL PRODUCTION READY)
## ENGINE LOGIC FOR MULTI-TIMEFRAME BIAS & ICT SILVER BULLET ASSISTANT

### 1. ALGORITHMIC CORE & SYSTEM NATURE
*   System Foundation: Inner Circle Trader (ICT) & Smart Money Concepts (SMC) frameworks.
*   Algorithmic Deliverables: The market algorithm moves non-randomly between External Range Liquidity (ERL) and Internal Range Liquidity (IRL). Its mechanics are bounded by:
    1. Hunt Liquidity (Seek & Destroy retail stop losses).
    2. Re-balance Inefficiencies (Fair Valuation Engine via FVGs and Liquidity Voids).
    3. Engineered Liquidity (Generating structural liquidity pools to act as future draws).
    4. Rebalancing Equilibrium (Systematic pricing flow back and forth between Premium and Discount arrays).
*   Dealing Range Formation: After previous Buy-Side Liquidity (BSL) and Sell-Side Liquidity (SSL) are completely taken, the system defines a new active dealing range using the absolute swing high and swing low. Draw an exact 50% Equilibrium Line.
*   System Nature (Scalp Constraints): Setups are high-velocity scalp entries designed to resolve within a maximum holding time of 1 Hour (1H). Risk must be kept tight (Stop Loss: 1.5 - 2.5 points) and target close (1:2 to 1:3 RR targets) to achieve fast execution and quick TP matches near current market price.

---

### 2. DYNAMIC PD-ARRAY MATRIX PROCESSING
The system must automatically calculate the 50% Equilibrium Line across the active dealing range and map the structural hierarchy of the Premium-to-Discount Array List:

*   Premium Zone (Above 50% Line) -> Allowed Setup: Shorts (Sells) Only. Valid PD Arrays: Old High/Low, Rejection Block, Bearish Order Block, Fair Value Gap (FVG/SIBI), Liquidity Void, Bearish Breaker Block, Bearish Mitigation Block.
*   Discount Zone (Below 50% Line) -> Allowed Setup: Buys (Longs) Only. Valid PD Arrays: Bullish Mitigation Block, Bullish Breaker Block, Liquidity Void, Fair Value Gap (FVG/BISI), Bullish Order Block, Rejection Block, Old Low/High.

#### Mechanical Footprint Definitions for Coding:
1.  Order Blocks (OB): Specific candles showing high institutional volume blocks. Sells at highest point of expansion; Buys at lowest point of retracement.
2.  Breaker Blocks: A failed order block broken through aggressively during an MSS, acting as support/resistance inversion.
3.  Mitigation Blocks: Similar to a breaker block but specifically formed during a Failure Swing scenario (price fails to create a higher high or lower low before shifting structure aggressively).
4.  Rejection Blocks: Price zones at the wicks of a swing high/low where liquidity is raided, but candle bodies fail to close.

---

### 3. FRACTAL BIAS & INTRADAY MAGNET TRACKING
*   Proximity Filter: If price is near BSL, the operational bias is Bullish until taken; if near SSL, it is Bearish until cleared.
*   The HTF Pullback Rule (GOLD Case Study): If the Daily structure is Bullish but undergoes a 3-day consecutive bearish pullback (Monday to Wednesday) into a HTF Demand array, track the lower timeframe Fractal Order Flow shift. Once Fractal Order Flow aligns bullishly, Daily Bias locks back to Bullish targeting the PDH (Previous Daily High).
*   Daily Open Vector: Price trading ABOVE Daily Open = Premium Pricing (Filter for Short-Term Bearish reversals). Price trading BELOW Daily Open = Discount Pricing (Filter for High-Probability Buy setups).

---

### 4. THE ICT SILVER BULLET EXECUTION ENGINE

#### A. Strict Silver Bullet Time Ranges (NY Time vs. Local Sri Lankan Time)
The engine must strictly monitor setups only during these three independent operational windows:
1.  London Open Silver Bullet: 03:00 AM - 04:00 AM NY Time (12:30 PM - 01:30 PM Sri Lankan Time).
2.  AM Session Silver Bullet: 10:00 AM - 11:00 AM NY Time (07:30 PM - 08:30 PM Sri Lankan Time) -> Priority Zone: Heavily correlated with NY Stock Exchange open volatility.
3.  PM Session Silver Bullet: 02:00 PM - 03:00 PM NY Time (11:30 PM - 12:30 AM Sri Lankan Time).

#### B. Timeframe Alignment Matrix
*   HTF Anchor: 1-Hour (1H) or 15-Minute (15MIN) structure to identify market context and clear Draw on Liquidity points.
*   LTF Execution: 5-Minute, 3-Minute, or 1-Minute charts (1-Minute chart is the optimal execution layer).

#### C. Normal Scenario Entry Setup Mechanics
*   Step 1: Identify a Liquidity Grab (Stop Hunt) -> Look for a clear sweep of a previous high/low (SSL Sweep or BSL Sweep) with an aggressive move beyond liquidity followed by a strong rejection candle footprint.
*   Step 2: Confirm Market Structure Shift (MSS) -> Price must break a key swing level with strong momentum, confirming smart money directional change.
*   Step 3: Locate an Inefficiency Array -> Locate a Fair Value Gap (BISI for Buy / SIBI for Sell) left inside the displacement leg between the MSS point and the liquidity grab low/high.
*   Step 4: Enter the Trade -> Set a limit order at the midpoint (50% Consequent Encroachment) of the FVG, OR enter at market if price reaches the FVG and shows signs of immediate rejection.

#### D. Advanced Scenario Setup Mechanics (9:00 AM Candlestick Range Filter)
*   *Application Window:* Applied specifically to the 10:00 AM - 11:00 AM NY Silver Bullet Window.
*   *Mechanical Filter:* Map the exact 09:00 AM Candle High and 09:00 AM Candle Low on the 1H chart.
*   Advanced Buy Setup Condition: Price handles execution inside the 10-11 AM window by first driving lower to completely violate/sweep the 09:00 AM Candle Low. This acts as the structural Liquidity Raid. Once MSS/CISD triggers post-sweep, execute the buy setup targeting the 09:00 AM Candle High.
*   Advanced Sell Setup Condition: Price drives higher inside the 10-11 AM window to violate/sweep the 09:00 AM Candle High (Liquidity Raid). Once mss triggers on the LTF, execute the short target matching the 09:00 AM Candle Low.

---

### 5. RISK PROFILE & POSITION METRICS
*   Risk Management Constraints: Never risk more than 1% to 2% per trade (0.5% configuration strongly recommended for funded account safety protocols). Ignore all counter-trend setups.
*   Stop-Loss (SL) Placement Rules:
    *   For Longs: Mechanically place SL below the lowest Swing Low or the last validated Liquidity Point.
    *   For Shorts: Mechanically place SL above the highest Swing High or the last validated Liquidity Point.
    *   *Alternative Local SL:* If structural swing points are too distant, place the SL right below/above the specific FVG candle boundary to optimize risk.
*   Take-Profit (TP) Target Hierarchy:
    *   First TP: Nearest local liquidity pool (Major Equal Highs or Equal Lows).
    *   Second TP: A key higher timeframe liquidity magnet point (PDH/PDL or session highs).
    *   Final TP: Next remaining unfilled FVG (Algorithmic target).
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

# Cache for Gemini status to avoid rate limits
_gemini_status_cache = {"status": "UNKNOWN", "details": "", "timestamp": 0.0}

@app.get("/api/preferences/gemini-status")
async def get_gemini_status(db: Session = Depends(get_db)):
    return {"status": "VALID", "details": "Local engine active. No Gemini API Key required!"}

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
    
    # Invalidate cache if key was updated
    if pref.key == "gemini_api_key":
        global _gemini_status_cache
        _gemini_status_cache["timestamp"] = 0.0 # Force recheck
        
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
    
    # Sanitize float fields
    for field in ["liquidity_target", "stop_loss_level", "equilibrium_price"]:
        val = result.get(field)
        if val is not None:
            if isinstance(val, str):
                val_clean = val.strip().lower()
                if val_clean in ["none", "n/a", "null", ""]:
                    result[field] = None
                else:
                    try:
                        result[field] = float(val)
                    except ValueError:
                        result[field] = None
            else:
                try:
                    result[field] = float(val)
                except (ValueError, TypeError):
                    result[field] = None

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
        mitigated_pd_array_type=result.get("mitigated_pd_array_type"),
        is_advanced_setup=result.get("is_advanced_setup"),
        advanced_setup_status=result.get("advanced_setup_status"),
        
        # Detailed 10-Step Silver Bullet fields
        sb_step_1_time_window_ok=result.get("sb_step_1_time_window_ok"),
        sb_step_1_details=result.get("sb_step_1_details"),
        sb_step_2_liquidity_sweep_ok=result.get("sb_step_2_liquidity_sweep_ok"),
        sb_step_2_details=result.get("sb_step_2_details"),
        sb_step_3_displacement_mss_ok=result.get("sb_step_3_displacement_mss_ok"),
        sb_step_3_details=result.get("sb_step_3_details"),
        sb_step_4_fvg_bpr_ok=result.get("sb_step_4_fvg_bpr_ok"),
        sb_step_4_details=result.get("sb_step_4_details"),
        sb_step_5_entry_exec_ok=result.get("sb_step_5_entry_exec_ok"),
        sb_step_5_details=result.get("sb_step_5_details"),
        sb_step_6_risk_mgmt_ok=result.get("sb_step_6_risk_mgmt_ok"),
        sb_step_6_details=result.get("sb_step_6_details"),
        sb_step_7_london_asian_sweep_ok=result.get("sb_step_7_london_asian_sweep_ok"),
        sb_step_7_details=result.get("sb_step_7_details"),
        sb_step_8_htf_pd_mitigation_ok=result.get("sb_step_8_htf_pd_mitigation_ok"),
        sb_step_8_details=result.get("sb_step_8_details"),
        sb_step_9_ltf_choch_ok=result.get("sb_step_9_ltf_choch_ok"),
        sb_step_9_details=result.get("sb_step_9_details"),
        sb_step_10_fvg_limit_ok=result.get("sb_step_10_fvg_limit_ok"),
        sb_step_10_details=result.get("sb_step_10_details"),
        
        confidence=result.get("confidence"),
        
        # Economic news fields
        news_lockout_active=result.get("news_lockout_active", False),
        active_news_event=result.get("active_news_event"),
        upcoming_news_events=result.get("upcoming_news_events")
    )


@app.post("/api/tracker/start")
async def tracker_start(req: SilverBulletRequest, db: Session = Depends(get_db)):
    pref = db.query(PreferenceModel).filter(PreferenceModel.key == "gemini_api_key").first()
    api_key = pref.value if pref else None
    if not req.symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")
    start_tracking(req.symbol, req.dict(), api_key=api_key)
    return {"status": "SUCCESS", "message": f"Started tracking {req.symbol}"}

@app.post("/api/tracker/stop")
async def tracker_stop(req: dict):
    symbol = req.get("symbol")
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")
    stop_tracking(symbol)
    return {"status": "SUCCESS", "message": f"Stopped tracking {symbol}"}

@app.get("/api/tracker/status")
async def tracker_status():
    return get_trackers_status()



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

async def fetch_current_price_for_symbol(symbol: str) -> float:
    symbol_upper = symbol.upper()
    yahoo_symbol = SYMBOL_MAP.get(symbol_upper)
    if yahoo_symbol:
        try:
            data = await fetch_yahoo_finance(yahoo_symbol)
            return data["current_price"]
        except Exception:
            pass
            
    binance_symbol = symbol_upper
    if not binance_symbol.endswith("USDT") and len(binance_symbol) <= 5:
        binance_symbol = f"{binance_symbol}USDT"
        
    try:
        price = await BinanceService.fetch_ticker_price(binance_symbol)
        return price
    except Exception:
        pass
        
    try:
        data = await fetch_yahoo_finance(f"{symbol_upper}-USD")
        return data["current_price"]
    except Exception:
        try:
            data = await fetch_yahoo_finance(symbol_upper)
            return data["current_price"]
        except Exception:
            return 0.0

@app.post("/api/trades/log", response_model=LoggedTradeResponse)
def log_trade(trade: LoggedTradeCreate, db: Session = Depends(get_db)):
    db_trade = LoggedTradeModel(
        symbol=trade.symbol,
        direction=trade.direction,
        entry_price=trade.entry_price,
        stop_loss=trade.stop_loss,
        take_profit=trade.take_profit,
        status="PENDING"
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.get("/api/trades/history", response_model=List[LoggedTradeResponse])
async def get_trade_history(db: Session = Depends(get_db)):
    trades = db.query(LoggedTradeModel).all()
    for trade in trades:
        if trade.status == "PENDING":
            try:
                current_price = await fetch_current_price_for_symbol(trade.symbol)
                if current_price > 0:
                    if trade.direction == "BULLISH":
                        if current_price >= trade.take_profit:
                            trade.status = "WIN"
                            db.commit()
                        elif current_price <= trade.stop_loss:
                            trade.status = "LOSS"
                            db.commit()
                    elif trade.direction == "BEARISH":
                        if current_price <= trade.take_profit:
                            trade.status = "WIN"
                            db.commit()
                        elif current_price >= trade.stop_loss:
                            trade.status = "LOSS"
                            db.commit()
            except Exception:
                pass
    return trades

@app.post("/api/trades/{trade_id}/status", response_model=LoggedTradeResponse)
def update_trade_status(trade_id: int, status_update: Dict[str, str], db: Session = Depends(get_db)):
    db_trade = db.query(LoggedTradeModel).filter(LoggedTradeModel.id == trade_id).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    new_status = status_update.get("status")
    if new_status in ["PENDING", "WIN", "LOSS"]:
        db_trade.status = new_status
        db.commit()
        db.refresh(db_trade)
@app.post("/api/trades/{trade_id}/update", response_model=LoggedTradeResponse)
def update_logged_trade(trade_id: int, updates: Dict[str, Any], db: Session = Depends(get_db)):
    db_trade = db.query(LoggedTradeModel).filter(LoggedTradeModel.id == trade_id).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    if "take_profit" in updates:
        db_trade.take_profit = float(updates["take_profit"])
    if "stop_loss" in updates:
        db_trade.stop_loss = float(updates["stop_loss"])
    if "entry_price" in updates:
        db_trade.entry_price = float(updates["entry_price"])
    if "status" in updates:
        db_trade.status = updates["status"]
    db.commit()
    db.refresh(db_trade)
    return db_trade



@app.delete("/api/trades/{trade_id}")
def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    db_trade = db.query(LoggedTradeModel).filter(LoggedTradeModel.id == trade_id).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    db.delete(db_trade)
    db.commit()
    return {"message": "Trade deleted successfully"}



