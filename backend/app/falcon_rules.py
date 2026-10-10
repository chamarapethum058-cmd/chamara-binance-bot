"""
UNIFIED 7-STEP 5M > 3M PRECISION SCALP PIPELINE - CLEAN EXECUTION ADAPTER
Author: Falcon Institutional Engine (Clean Wipe & Total Rewrite)
Description:
    Clean rewrite replacing legacy Rules 1-91 and 1M scripts with the
    Unified 7-Step 5M > 3M Precision Scalp Protocol.
    All execution logic routes directly through PrecisionScalpPipeline.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from app.precision_scalp import (
    PrecisionScalpPipeline,
    PRECISION_SCALP_STEPS_CATALOGUE
)

logger = logging.getLogger("falcon_rules")

class FalconSetupRecord:
    """
    Clean state record for 5M > 3M Precision Scalp setups.
    Tracks state through the 7-Step Institutional Protocol.
    """
    def __init__(
        self,
        setup_id: str,
        symbol: str,
        timeframe: str,
        direction: str,
        macro_bias: str,
        source: str,
        poi_type: str,
        poi_high: float,
        poi_low: float,
        poi_invalidation_level: float,
        creation_time: Optional[float] = None,
        max_setup_age: float = 7200.0
    ):
        self.setup_id = setup_id
        self.symbol = symbol.upper().strip()
        self.timeframe = "3m"
        self.direction = direction.upper().strip()
        self.macro_bias = macro_bias.upper().strip()
        self.source = source
        self.poi_type = poi_type
        self.poi_high = float(poi_high)
        self.poi_low = float(poi_low)
        self.poi_invalidation_level = float(poi_invalidation_level)
        self.creation_time = creation_time or time.time()
        self.max_setup_age = max_setup_age
        self.state = "STEP_3_WAITING_TAP"
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        self.breakeven = None
        self.quality_score = 92

    def is_expired(self, current_time: Optional[float] = None) -> bool:
        now = current_time or time.time()
        return (now - self.creation_time) > self.max_setup_age

    def is_structurally_invalidated(self, current_price: float, current_bias: Optional[str] = None) -> bool:
        if self.direction == "BUY" and current_price < self.poi_invalidation_level:
            return True
        elif self.direction == "SELL" and current_price > self.poi_invalidation_level:
            return True
        return False


_active_falcon_registry: Dict[str, FalconSetupRecord] = {}

def get_falcon_setup_record(symbol: str) -> Optional[FalconSetupRecord]:
    clean_sym = symbol.upper().replace(".P", "").strip()
    return _active_falcon_registry.get(clean_sym)

def register_or_update_falcon_setup(
    symbol: str,
    timeframe: str,
    direction: str,
    macro_bias: str,
    source: str,
    poi_type: str,
    poi_high: float,
    poi_low: float,
    poi_invalidation_level: float,
    current_price: float,
    max_setup_age: float = 7200.0
) -> FalconSetupRecord:
    clean_sym = symbol.upper().replace(".P", "").strip()
    existing = _active_falcon_registry.get(clean_sym)
    if existing:
        if not existing.is_expired() and not existing.is_structurally_invalidated(current_price):
            return existing
    
    rec_id = f"PRECISION_SCALP_{clean_sym}_{int(time.time())}"
    new_rec = FalconSetupRecord(
        setup_id=rec_id,
        symbol=clean_sym,
        timeframe="3m",
        direction=direction,
        macro_bias=macro_bias,
        source=source,
        poi_type=poi_type,
        poi_high=poi_high,
        poi_low=poi_low,
        poi_invalidation_level=poi_invalidation_level,
        max_setup_age=max_setup_age
    )
    _active_falcon_registry[clean_sym] = new_rec
    return new_rec


def evaluate_74_falcon_rules(
    req: Dict[str, Any],
    price: float,
    candles: List[Dict[str, Any]],
    raw_result: Optional[Dict[str, Any]] = None,
    execution_mode: str = "SCALP_PRO"
) -> List[Dict[str, Any]]:
    """
    Clean adapter routing rule evaluation directly through the
    Unified 7-Step 5M > 3M Precision Scalp Pipeline.
    """
    symbol = str(req.get("symbol") or "BTCUSDT").upper()
    candles_15m = req.get("candles_15m") or candles
    candles_5m = req.get("candles_5m") or candles
    candles_3m = req.get("candles_3m") or candles
    daily_open = float(req.get("daily_open") or price)
    pdh = float(req.get("pdh") or price * 1.01)
    pdl = float(req.get("pdl") or price * 0.99)
    asian_high = req.get("asian_high")
    asian_low = req.get("asian_low")

    analysis = PrecisionScalpPipeline.evaluate(
        symbol=symbol,
        price=price,
        candles_15m=candles_15m,
        candles_5m=candles_5m,
        candles_3m=candles_3m,
        daily_open=daily_open,
        pdh=pdh,
        pdl=pdl,
        asian_high=asian_high,
        asian_low=asian_low,
        is_news_locked=bool(raw_result.get("news_lockout_active", False) if raw_result else False),
        active_news_event=raw_result.get("active_news_event") if raw_result else None
    )

    # If raw_result dictionary was provided, enrich it with pipeline fields
    if isinstance(raw_result, dict):
        for k, v in analysis.items():
            if k not in ["rules_checklist"]:
                raw_result[k] = v

    return analysis.get("rules_checklist", [])


def evaluate_smc_master_pipeline(
    checklist: List[Dict[str, Any]],
    raw_result: Dict[str, Any],
    req: Dict[str, Any],
    price: float
) -> Dict[str, Any]:
    """
    Evaluates the institutional execution readiness across the 7 steps.
    """
    if "pipeline" in raw_result and isinstance(raw_result["pipeline"], dict):
        return raw_result["pipeline"]

    passed_count = sum(1 for c in checklist if c.get("passed"))
    total_steps = len(checklist) or 7
    progress = round((passed_count / total_steps) * 100)
    step_7_chk = next((c for c in checklist if c.get("step_no") == 7 or c.get("rule_no") == 7), None)
    step_7_passed = bool(step_7_chk and step_7_chk.get("passed"))

    return {
        "pipeline_name": "UNIFIED 7-STEP 5M > 3M PRECISION SCALP PIPELINE",
        "current_phase": 7 if step_7_passed else (next((c["step_no"] for c in checklist if not c.get("passed")), 1)),
        "current_phase_name_en": "Step 7: 30-Minute Rapid Scalp Exit Engine",
        "current_phase_name_si": "පියවර 7: විනාඩි 30 අධිවේගී පිටවීමේ එන්ජිම",
        "pipeline_progress_pct": progress,
        "is_ready_for_execution": bool(step_7_passed and passed_count == total_steps),
        "step_7_passed": step_7_passed,
        "step_7_direction": raw_result.get("direction", "NEUTRAL"),
        "phases": [
            {
                "phase": c.get("step_no", idx + 1),
                "name": c.get("title", f"Step {idx+1}"),
                "name_si": c.get("title_si", f"පියවර {idx+1}"),
                "status": c.get("status", "PENDING"),
                "passed": c.get("passed", False),
                "detail_en": c.get("detail", ""),
                "detail_si": c.get("detail_si", "")
            }
            for idx, c in enumerate(checklist)
        ]
    }


evaluate_all_falcon_rules = evaluate_74_falcon_rules
