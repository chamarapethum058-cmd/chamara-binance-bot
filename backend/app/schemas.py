from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Strategy schemas
class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    is_active: bool = False

class StrategyCreate(StrategyBase):
    pass

class StrategyResponse(StrategyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Analysis schemas
class AnalysisRequest(BaseModel):
    symbol: str
    timeframe: str
    custom_strategy_id: Optional[int] = None

class AnalysisResponse(BaseModel):
    id: int
    timestamp: datetime
    symbol: str
    timeframe: str
    signal: str
    confidence: int
    reasoning: str
    invalidation: str
    risk_notes: str
    chart_data: Optional[str] = None

    class Config:
        from_attributes = True

# Preference schemas
class PreferenceBase(BaseModel):
    key: str
    value: str

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceResponse(PreferenceBase):
    id: int

    class Config:
        from_attributes = True

# Chat schemas
class ChatRequest(BaseModel):
    message: str
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    analysis_id: Optional[int] = None
    history: Optional[List[dict]] = None


# Translation schemas
class TranslateRequest(BaseModel):
    text: str


# Silver Bullet analysis schemas
class SilverBulletRequest(BaseModel):
    symbol: Optional[str] = None
    scenario_text: Optional[str] = None
    htf_trend: Optional[str] = None
    pullback_days: Optional[int] = None
    pdh: Optional[float] = None
    pdl: Optional[float] = None
    daily_open: Optional[float] = None
    daily_close: Optional[float] = None
    asian_sweep: Optional[bool] = None
    demand_mitigation: Optional[bool] = None
    ltf_shift: Optional[bool] = None
    current_price: Optional[float] = None
    
    # Advanced strategy parameters
    dealing_range_high: Optional[float] = None
    dealing_range_low: Optional[float] = None
    killzone: Optional[str] = None # "LONDON", "NY_AM", "NONE"
    discount_pd_array: Optional[bool] = None
    premium_pd_array: Optional[bool] = None
    ltf_trigger: Optional[str] = None # "MSS", "CISD", "NONE"
    has_fresh_fvg: Optional[bool] = None
    high_impact_news: Optional[bool] = None
    
    # Advanced 9:00 AM Candle Range parameters
    candle_9am_high: Optional[float] = None
    candle_9am_low: Optional[float] = None

class SilverBulletResponse(BaseModel):
    is_valid: bool
    status_message: str
    market_structure_status: Optional[str] = None
    daily_bias: Optional[str] = None
    liquidity_target: Optional[float] = None
    entry_price_area: Optional[str] = None
    stop_loss_level: Optional[float] = None
    target_reward_ratio: Optional[str] = None
    reasoning: Optional[str] = None
    invalidation: Optional[str] = None
    risk_notes: Optional[str] = None
    
    # Advanced computed parameters
    equilibrium_price: Optional[float] = None
    zone_type: Optional[str] = None # "DISCOUNT", "PREMIUM", "EQUILIBRIUM"
    daily_open_relation: Optional[str] = None # "ABOVE_OPEN", "BELOW_OPEN", "N/A"
    killzone_valid: Optional[bool] = None
    counter_trend_locked: Optional[bool] = None
    
    # Antigravity Master Spec fields
    erl_irl_state: Optional[str] = None
    swept_liquidity_pool: Optional[str] = None
    mitigated_pd_array_type: Optional[str] = None
    
    # Advanced 9AM range filter details
    is_advanced_setup: Optional[bool] = None
    advanced_setup_status: Optional[str] = None # "NONE", "9AM_LOW_SWEPT_MSS_PENDING", "9AM_HIGH_SWEPT_MSS_PENDING", "TRIGGERED"



