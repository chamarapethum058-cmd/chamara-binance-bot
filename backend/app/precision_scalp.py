"""
🦅 PURE DUAL-TIMEFRAME SMC CONFLUENCE ENGINE (5M & 3M SYMMETRIC)
Exposes the clean-slate mathematical SMC engine from strategy.py.
"""

from app.strategy import (
    PureSMCEngine,
    PrecisionScalpPipeline,
    FiveMinStructureResult,
    ThreeMinWaveResult,
    TwoCandleExecutionResult,
    check_5m_structure_and_waves,
    get_3m_micro_wave_count,
    check_2_candle_execution,
    get_dynamic_precision,
    PURE_SMC_STEPS
)

PRECISION_SCALP_STEPS_CATALOGUE = PURE_SMC_STEPS
