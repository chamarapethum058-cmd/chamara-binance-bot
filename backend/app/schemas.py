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

