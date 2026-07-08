# Project Falcon - Strategy Knowledge Base Specification

This document defines the trading strategy structure used by the AI Trading Assistant. The AI reads this strategy template to understand the rules, indicators, setups, and risk guidelines defined by the user.

---

## Strategy Template Structure

A valid trading strategy must define the following sections:

1. **Strategy Name & Overview**: Clear identification and core concept.
2. **Timeframe & Asset Scope**: Selected symbols and analysis timeframes.
3. **Core Indicators & Tools**: Standard indicators (EMA, RSI, MACD, Volume) or concepts (Smart Money Concepts).
4. **Market Structure Rules**: How trends and structures are defined (e.g., Higher Highs, Lower Lows, BOS, CHOCH).
5. **Entry Conditions (Setups)**: Step-by-step checklist required to consider a setup valid.
6. **Exit & Invalidation Conditions**: Conditions under which a setup is invalidated or closed.
7. **Risk Management Rules**: Max risk per trade, risk-to-reward ratio, and placement of Stop Loss/Take Profit.

---

## Example Strategy: Smart Money Concepts (SMC)

Below is the active strategy template for SMC trading:

### 1. Strategy Overview
* **Name**: SMC (Smart Money Concepts) Structural Analysis
* **Core Concept**: Trading structural breaks (BOS/CHOCH) and institutional footprints (Order Blocks, Fair Value Gaps).

### 2. Timeframe & Asset Scope
* **Assets**: BTC/USDT, ETH/USDT, SOL/USDT.
* **Higher Timeframe (HTF)**: 4-Hour (for overall trend and major POI - Point of Interest).
* **Lower Timeframe (LTF)**: 15-Minute (for entry execution and structural confirmation).

### 3. Key Concepts & Indicators
* **BOS (Break of Structure)**: Continuation of the current market structure.
* **CHOCH (Change of Character)**: First sign of potential trend reversal.
* **FVG (Fair Value Gap)**: 3-candle price imbalance where liquidity is inefficiently filled.
* **Order Block (OB)**: The last opposite candle before a strong structural move.

### 4. Entry Rules (Long Setup)
1. **HTF Alignment**: Price must tap a HTF Bullish Order Block or discount FVG on the 4H chart.
2. **LTF Reversal**: On the 15M chart, wait for a Bullish CHOCH (break of the last swing high that created the low).
3. **POI Identification**: Identify the new 15M Bullish Order Block or 15M FVG created by the CHOCH impulse.
4. **Trigger**: Place a limit entry at the 50% equilibrium level (Mean Threshold) of the 15M Order Block or at the start of the FVG.

### 5. Invalidation & Risk Rules
* **Stop Loss (SL)**: Set strictly below the swing low that initiated the CHOCH.
* **Take Profit (TP)**: First target is the nearest key LTF liquidity pool (swing high); second target is the HTF premium liquidity.
* **Minimum Risk-to-Reward (R:R)**: 1:3.
* **Invalidation Condition**: If price breaks below the swing low before tapping our entry point, the setup is invalid.
* **Risk Limit**: Maximum 1% account size per trade setup.
