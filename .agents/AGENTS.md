# Project Falcon Customization Rules

## 1. Sinhala Translation Preservation Requirement
> [!IMPORTANT]
> **CRITICAL REQUIREMENT:** Do NOT remove or modify the **Sinhala Translation (සිංහල පරිවර්තනය)** features from the AI responses, Technical Reasoning, Invalidation details, Risk Notes, or error alerts.
> The user relies on these bilingual explanations to understand strategy actions, rule lockouts, and risk alerts.
> 
> When modifying backend analysis prompts (`backend/app/services.py`), ensure the AI generator is always instructed to return bilingual outputs (English + Sinhala translations).
> When modifying frontend UI tabs (`frontend/src/app/page.tsx`), ensure the rendering of the translation dropdowns, tabs, and bilingual text matches this structure exactly.

## 2. Antigravity Engine Master Specification Rules
The following system instructions must be strictly followed when analyzing, validating, or executing trade setups:
1. **ERL vs IRL tracking protocol**: Lock all analytical evaluations inside a strict External Range Liquidity (ERL) vs Internal Range Liquidity (IRL) tracking protocol.
2. **Equilibrium Matrix Calculation**: Automate a 50% Equilibrium matrix calculation over the mapped dealing range. Invalidate Long signals in Premium and Short signals in Discount.
3. **Rigorous Verification Sequence**: Confirm HTF Daily Bias -> Map PDH/PDL and PWH/PWL magnets -> Validate a PDL/SSL Sweep strictly during London or New York AM Killzones (2AM-5AM / 7AM-10AM NY Time) -> Verify MSS/CISD shift on M15/M5 chart paired with unmitigated FVG/Order Block/Breaker/Mitigation/Rejection array before delivering an actionable entry.
4. **UI checklist tree structure**: The system UI must display a clear structural tree detailing:
   - HTF Trend
   - Daily Open Bias Vector (Above/Below Open)
   - Swept Liquidity Pool (PDL/SSL or PDH/BSL)
   - Mitigated PD Array Type (FVG, OB, Breaker, Mitigation, Rejection)
   - Execution Parameters (Entry Price, Absolute SL, and 1:3 RR Target Output).
5. **Auto-ignore setups**: Discard and auto-ignore any setups that run counter to the active Daily Bias.

## 3. GitHub Push and Save Restriction Protocol
> [!IMPORTANT]
> **STRICT PUSH RESTRICTION:** Never stage, commit, or push any code changes to GitHub automatically or on your own initiative.
> You must ONLY stage, commit, or push changes to GitHub when the user explicitly requests it (e.g. "Save/push to GitHub now"). Keep all code edits strictly local by default unless explicitly instructed otherwise.
## 4. 10-15 Minutes High-Velocity Scalping Constraints
The following execution boundaries must be strictly enforced for all actionable trade setups:
1. **Tight Stop Loss (Tighter SL):** Keep the stop loss very close to the entry price to minimize risk exposure (e.g., maximum of 0.1% to 0.15% of the asset price, or 1.5 - 2.5 points on Gold-like assets). Avoid wide or distant stop losses.
2. **Close Take Profit (Tighter TP):** Set target prices close to the entry price based strictly on 1:2 to 1:4 Risk-to-Reward (RR) ratios. Do not target distant higher timeframe levels (like major PDH/PDL ranges) if they are too far from the entry price and cannot be reasonably filled within a short session.
3. **10-15 Minutes Max Hold Limit:** All setups must be designed as high-velocity scalping entries meant to complete (either hitting SL or TP) within a maximum holding time of 10 to 15 Minutes. Reflect this holding warning in Risk Notes and Sinhala translations.

## 5. Sri Lankan Time-Window Mappings and 1m/3m Chart Confirmation Constraints
The bot must track the following session hours mapped between New York Time and Sri Lankan Time in Step 1 of the checklist, but bypass the lockout to allow execution at any time of day:
1. **London Open Silver Bullet Session:** 03:00 AM - 04:00 AM NY Time / 12:30 PM - 01:30 PM Sri Lankan Time.
2. **NY AM Silver Bullet Session:** 10:00 AM - 11:00 AM NY Time / 07:30 PM - 08:30 PM Sri Lankan Time.
3. **NY PM Silver Bullet Session:** 02:00 PM - 03:00 PM NY Time / 11:30 PM - 12:30 AM Sri Lankan Time.
4. **M1/M3 Timeframe Constraints:** The entry detection and strategy confirmations (Liquidity Sweep, Displacement, MSS/Choch, FVG/BPR, limit order placement) must occur strictly on the selected 1-minute (1m) or 3-minute (3m) chart.
5. **Asian Liquidity Sweep & HTF Array:** Confirm that Asian Session liquidity is swept during the London Open window, and HTF PD Array (PDL, PDH, PWH, PWL, HTF-FVG, HTF-OB, HTF-BB) is mitigated.
6. **Checklist Validation:** All 6 steps must evaluate individually and dynamically in the Validation Tree.

## 6. 70% Minimum Confirmation Rate Constraint
The bot must strictly enforce the following confidence scoring boundaries:
1. **Confidence Score Calculation:** Calculate a strategy confidence score out of 100% based on rule confluences (Trend alignment: 20%, Optimal matrix zone discount/premium: 20%, Daily Open alignment: 15%, Active Silver Bullet window: 15%, Wick Liquidity sweep: 15%, and LTF Shift/MSS with FVG: 15%).
2. **70% Minimum Filter:** Only deliver trade setups that achieve a confidence score of 70% or higher.
3. **Low-Confidence Entry Lockout:** If confidence is below 70%, the bot must suppress and lockout the setup, returning "No Entry (Confidence < 70%)" to prevent low-probability trades and shield the user from unnecessary stop losses. Display this confirmation percentage on the frontend page next to the Entry Price Area card.

## 7. Automated Economic News Lockout Constraint
The bot must strictly enforce the following high-impact news rules:
1. **Economic News Parser:** The backend must dynamically fetch economic calendar events.
2. **USD High-Impact Focus:** Only focus on USD "High" impact news events (such as CPI, NFP, FOMC Interest Rate, PPI, GDP).
3. **Lockout window (+/- 60 Minutes):** If any high-impact USD news is scheduled within 60 minutes before or 60 minutes after the current time, the bot must automatically block all entries, returning "No Entry (High-Impact News Lockout)" to prevent trading during high volatility news spikes.

## 8. Strategy Confidence Preservation Protocol (Lock)
> [!IMPORTANT]
> **STRICT CONFIDENCE RETENTION LOCK:** Do NOT remove, rename, or omit the `"confidence"` parameter from any backend response payload or dictionary (e.g., in `backend/app/services.py` and `schemas.py`). 
> Every backend return block (including lockout, news, poor RR, and neutral states) must explicitly return `"confidence"` (e.g., `conf_score` or `0`).
> The frontend (`frontend/src/app/page.tsx`) must always display the confidence percentage inside the `% CONFIRMED` badge next to the Entry Price Area card, checking safely for null/undefined values to prevent empty labels. 
> Any changes to these constraints require explicit user approval.

## 9. Triple-Verification Strategy Protocol (New Rule)
> [!IMPORTANT]
> **TRIPLE-VERIFICATION LOOP:** Before returning any actionable trade setup, the backend/AI engine must execute a strict triple-verification process.
> It must sequentially check and match every parameter against the Falcon Rules (HTF Daily Bias, ERL/IRL zone, Daily Open vector relation, active Silver Bullet window, wick sweep, tight SL, close TP targets, news lockout, and confidence rating >= 70%) at least three separate times in its reasoning sequence.
> If any check fails in any of the loops, the entry must be immediately suppressed and locked out.

## 10. High-Confluence Market-Price Confirmation Protocol (New Rule)
> [!IMPORTANT]
> **NO ARBITRARY ENTRIES/STOP LOSSES:** The system must never output arbitrary entry or stop loss parameters. 
> If these specific close-proximity confirmations do not exist, the entry must be suppressed and locked out to prevent arbitrary trade execution.

## 11. Programmatic Local Tracker Constraint (New Rule)
> [!IMPORTANT]
> **NO GEMINI API CALLS IN SCANNERS:** The background live scanner loop (`tracker.py`) MUST calculate the 12 setup confluences and confidence score programmatically and locally in Python using live price data.
> Under no circumstances should the background tracker loop make calls to `AIService.analyze_silver_bullet` or call the Gemini AI API, to prevent API rate limits (429/503) and ensure 100% free and reliable monitoring.
> The Gemini AI API must ONLY be triggered during manual, on-demand UI "Scan Market" or "Run Analysis" operations.

## 12. Limit Orders Only & Wait for Pullback Protocol (New Rule)
> [!IMPORTANT]
> **NO MARKET ENTRIES & WAIT FOR PULLBACK:** 
> 1. **Limit Entry Only:** The bot must never advise or execute market orders immediately when Market Structure Shift (MSS/Choch) occurs. Instead, it must strictly calculate and advise a Limit Order entry at the FVG boundary or 50% Mean Threshold of the Order Block.
> 2. **Pullback Mitigation Verification:** Trade setup validation steps (specifically Step 5 and Step 10) must explicitly require waiting for a deeper pullback/mitigation to touch the limit price before executing, reducing stop-loss hits and increasing overall win rate.

## 13. Dynamic Market Structure Bias Auto-Detection Protocol (New Rule)
> [!IMPORTANT]
> **DYNAMIC STRUCTURE BIAS AUTO-DETECTION:**
> 1. **Live Candle MSS Analysis:** The bot must dynamically analyze the last 50 candles on the selected timeframe to identify recent Swing High breaks (Bullish MSS) or Swing Low breaks (Bearish MSS).
> 2. **Daily Bias Override:** If a bearish structural shift (Bearish MSS) or bearish momentum is detected, the setup direction and daily bias must be automatically overridden to BEARISH (Sell Limit setups). If a bullish structural shift (Bullish MSS) or bullish momentum is detected, it must be overridden to BULLISH (Buy Limit setups), regardless of the manual frontend input dropdown setting. This prevents counter-market entries and shields the user from entering buy setups during rapid market crashes or sell setups during rapid market pumps.

## 14. Trading Masterguide 3M's Institutional PO3 Reversal Protocol (New Rule)
> [!IMPORTANT]
> **TRADING MASTERGUIDE 3M'S PO3 & DUAL ENTRY RULES:**
> 1. **3M's AMD Phases Check:** The system (Step 12) must verify the structural alignment of the PO3 AMD framework (Accumulation -> Manipulation wick sweep above/below open -> Distribution expansion).
> 2. **Dual Entry Models:** Entry confirmations must dynamically track both the **1st Entry Model** (pullback to the 50% consequent encroachment or boundary of the FVG/BISI) and the **2nd Entry Model** (pullback to the Rejection Block wick sweep zone), keeping stop loss extremely tight past the manipulation low/high to optimize high reward-to-risk (minimum 1:5 to 1:13.5+ RR targets).
> 3. **Setup Direction Classification:** A **Bullish setup (Buy Limit)** is defined when a downward manipulation sweeps the Lows/SSL followed by a Bullish MSS (Swing High break with displacement). A **Bearish setup (Sell Limit)** is defined when an upward manipulation sweeps the Highs/BSL followed by a Bearish MSS (Swing Low break with displacement).


