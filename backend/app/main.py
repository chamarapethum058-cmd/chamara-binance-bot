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
    ChatRequest
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
    # Check if we have any strategies
    if db.query(StrategyModel).count() == 0:
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
        db.refresh(default_smc)
        print("Default SMC strategy populated.")
    
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

