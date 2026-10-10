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
2. **Equilibrium & Dealing Range Protocol**:
   - **Buy (Long) Setups**: Strictly restricted to the **Discount Zone (<= 50% Equilibrium)** or verified Demand Base Reversals (Rule 74). Buying in the upper Premium Resistance zone while making Lower Highs is 100% STRICTLY FORBIDDEN (Anti-Ceiling Trap - Rules 12 & 56).
   - **Sell (Short) Setups**: Strictly restricted to the **Premium Zone (>= 50% Equilibrium)** or verified Supply Base Reversals (Rule 74). Selling in the lower Discount Support zone while making Higher Lows is 100% STRICTLY FORBIDDEN (Anti-Floor Trap - Rules 12 & 56).
   - **Sinhala Translation (සිංහල පරිවර්තනය)**: Buy Setups ලබා දිය යුත්තේ Discount Zone (Equilibrium එකෙන් පහළ) හෝ තහවුරු වූ Demand Base එකකින් පමණි. වෙළඳපල Range එකේ උඩම Premium Resistance කලාපය තුළ Lower Highs සාදන විට Buy කිරීම 100% ක්ම තහනම් වේ (Rules 12 & 56). Sell Setups ලබා දිය යුත්තේ Premium Zone (Equilibrium එකෙන් ඉහළ) හෝ Supply Base එකකින් පමණි.
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

## 6. 80% Minimum Confirmation Rate Constraint
The bot must strictly enforce the following confidence scoring boundaries:
1. **Confidence Score Calculation:** Calculate a strategy confidence score out of 100% based on 9 weighted confluences:
   - Trend Alignment (1H/15m/1m): 20%
   - Liquidity Pool Sweep / Mitigation: 10%
   - 1m Rejection Wick (Wick >= 35%): 10%
   - LTF Shift/MSS Choch: 10%
   - Wait for Pullback / Limit Entry: 10%
   - RSI Momentum Check: 10%
   - M1 Liquidity Sweep (Major Wick Sweep): 10%
   - Displacement CHoCH (Strong Body Close): 10%
   - 1M FVG + OB Confluence (Coinciding FVG/OB): 10%
2. **80% Minimum Filter:** Only deliver trade setups that achieve a confidence score of 80% or higher.
3. **Low-Confidence Entry Lockout:** If confidence is below 80%, the bot must suppress and lockout the setup, returning "No Entry (Confidence < 80%)" to prevent low-probability trades and shield the user from unnecessary stop losses. Display this confirmation percentage on the frontend page next to the Entry Price Area card.

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
> It must sequentially check and match every parameter against the Falcon Rules (HTF Daily Bias, ERL/IRL zone, Daily Open vector relation, active Silver Bullet window, wick sweep, tight SL, close TP targets, news lockout, and confidence rating >= 80%) at least three separate times in its reasoning sequence.
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
> 1. **Live Candle MSS Analysis:** The bot must dynamically analyze a broad visible range of the last 200 candles on the selected timeframe to identify recent Swing High breaks (Bullish MSS) or Swing Low breaks (Bearish MSS) (මෑතකදී දිස්වන පුළුල් ඉටිපන්දම් 200 ක පරාසයක්).
> 2. **Daily Bias Override:** If a bearish structural shift (Bearish MSS) or bearish momentum is detected, the setup direction and daily bias must be automatically overridden to BEARISH (Sell Limit setups). If a bullish structural shift (Bullish MSS) or bullish momentum is detected, it must be overridden to BULLISH (Buy Limit setups), regardless of the manual frontend input dropdown setting. This prevents counter-market entries and shields the user from entering buy setups during rapid market crashes or sell setups during rapid market pumps.

## 14. Trading Masterguide 3M's Institutional PO3 Reversal Protocol (New Rule)
> [!IMPORTANT]
> **TRADING MASTERGUIDE 3M'S PO3 & DUAL ENTRY RULES:**
> 1. **3M's AMD Phases Check:** The system (Step 12) must verify the structural alignment of the PO3 AMD framework (Accumulation -> Manipulation wick sweep above/below open -> Distribution expansion).
> 2. **Dual Entry Models:** Entry confirmations must dynamically track both the **1st Entry Model** (pullback to the 50% consequent encroachment or boundary of the FVG/BISI) and the **2nd Entry Model** (pullback to the Rejection Block wick sweep zone), keeping stop loss extremely tight past the manipulation low/high to optimize high reward-to-risk (minimum 1:5 to 1:13.5+ RR targets).
> 3. **Setup Direction Classification:** A **Bullish setup (Buy Limit)** is defined when a downward manipulation sweeps the Lows/SSL followed by a Bullish MSS (Swing High break with displacement). A **Bearish setup (Sell Limit)** is defined when an upward manipulation sweeps the Highs/BSL followed by a Bearish MSS (Swing Low break with displacement).

## 15. Trading Masterguide SMC Market Structure Mapping Protocol (New Rule)
> [!IMPORTANT]
> **SMC TOP-DOWN STRUCTURE MAPPING RULES:**
> 1. **1H Timeframe:** Previous High/Low (PDH/PDL) defines Key Levels. Break of Structure (BOS) determines Macro Market Direction (BULLISH or BEARISH).
> 2. **15M Timeframe:** Change of Character (CH/CHoCH) and Liquidity Sweep confirms buyers/sellers dominance. Marks 15M Order Block (Demand/Supply Zone).
> 3. **1M Timeframe:** Inducement (IDM) and its Sweep confirms final continuation.
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):** 1H Timeframe එකෙහි PDH/PDL මඟින් Key Levels සලකුණු කර Macro Market Direction (Bullish/Bearish) තීරණය කරන අතර, 15M හි CH/CHoCH සහ Sweep මඟින් Order Block එක සලකුණු කරයි. 1M හි Inducement Sweep මඟින් අඛණ්ඩතාව තහවුරු කරයි.

## 16. Multi-Timeframe POI Reversal & 1m Markup/Markdown Precedence Protocol (Updated Master Rule)
> [!IMPORTANT]
> **1M TIMEFRAME STRUCTURE & MARKUP/MARKDOWN PRECEDENCE RULES:**
> 1. **1m Markup / Markdown Precedence Over HTF Bias:**
>    - When the 1-minute (1m) chart demonstrates an active **Markup Phase** (consecutive Higher Lows breaking local swing highs off a Demand Base), the 1m Bullish trend takes 100% absolute precedence over any lagging 1H/15m Bearish bias. 
>    - **Shorting / Sell Limits during an active 1m Higher Lows expansion is STRICTLY LOCKED OUT (`No Entry (Anti-Counter-Markup Lock)`).** The system MUST search ONLY for Buy Limit setups at the 1m Demand FVG.
>    - Conversely, when the 1m chart demonstrates an active **Markdown Phase** (consecutive Lower Highs breaking local swing lows off a Supply Base), Buying during an active 1m Lower Highs dump is STRICTLY LOCKED OUT (`No Entry (Anti-Counter-Markdown Lock)`). The system MUST search ONLY for Sell Limit setups at the 1m Supply FVG.
> 2. **Step 2 (Micro Confirmation & Limit Entry Placement):**
>    - Within the active 1m structure, place limit orders strictly at the unmitigated 1m FVG / OB boundary with the **Rule 62 0.04% spread buffer**.
>    - **Stop Loss:** Placed strictly outside the 1m swing extreme incorporating the **Rule 19/25/43 0.10% safe buffer**.
>    - **Take Profit:** Target the next structural liquidity extreme within the dynamic 1:2.0 to 1:4.0 RR boundary (Rule 72).
> 3. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - 1-Minute Chart එකෙහි Demand Base එකකින් පසු එක දිගට Higher Lows සාදමින් මිල ඉහළ යන විට (Markup Phase), 1H හෝ 15M Bearish Bias එක කුමක් වුවත්, 1-Minute Bullish Trend එකට 100% ක පූර්ණ ප්‍රමුඛතාවය හිමිවේ. **එවැනි අවස්ථාවලදී SELL දීම 100% ක්ම තහනම් වන අතර (Hard-Blocked), 1m Demand FVG එකෙන් 'BUY LIMIT' පමණක් ලබා දිය යුතුය.**
>    - මිල එක දිගට Lower Highs සාදමින් පහළට කඩා වැටෙන විට (Markdown Phase), BUY දීම 100% ක්ම තහනම් වන අතර, 1m Supply FVG එකෙන් 'SELL LIMIT' පමණක් ලබා දිය යුතුය.

## 17. Counter-Bias Invalidation Protocol before Mitigation (New Rule)
> [!IMPORTANT]
> **COUNTER-BIAS INVALIDATION PROTOCOL BEFORE MITIGATION:**
> 1. **Immediate Invalidation before Mitigation:** If a pending trade setup is logged but has not yet reached the entry price (pullback mitigation has not occurred), the system monitors for invalidation.
> 2. **Timeframe Isolation:** The invalidation check evaluates ONLY the trade's HTF trend filter (e.g., checking 15m trend for 1m scalp entries, and 1H trend for 15m entries) to allow normal 1m pullbacks without false invalidation. 3m charts are ignored.
> 3. **Stop Loss Breach Lock:** The trade is immediately invalidated if the current price breaches the stop loss/manipulation extreme before execution.
> 4. **Journal State Update:** The status in the trade history must transition automatically to `INVALIDATED` and be locked out of execution to prevent stop-loss hits from counter-momentum.

## 18. RSI Momentum Confirmation Protocol (New Rule)
> [!IMPORTANT]
> **RSI MOMENTUM CONFIRMATION RULES:**
> 1. **Live RSI Calculation:** The bot calculates a 14-period Relative Strength Index (RSI) using the closes of a broad visible range of the last 200 candles on the active timeframe (මෑතකදී දිස්වන පුළුල් ඉටිපන්දම් 200 ක පරාසයක්).
> 2. **Momentum Alignment Check**:
>    - **Buy setup (Uptrend):** Allowed ONLY when RSI is not overbought (RSI <= 65), verifying room for upward expansion.
>    - **Sell setup (Downtrend):** Allowed ONLY when RSI is not oversold (RSI >= 35), verifying room for downward expansion.
>    - **Strict Lockout:** If RSI is overbought during a buy pullback or oversold during a sell pullback, the setup is locked out (`No Entry`) to protect against momentum depletion.

## 19. Swing Extreme Stop-Loss Protection Protocol (New Rule)
> [!IMPORTANT]
> **SWING EXTREME STOP-LOSS PROTECTION RULES:**
> 1. **No Inner-Range Stop Losses:** The Stop Loss (SL) of any trade setup must strictly be placed outside the Swing Extreme boundaries to prevent manipulation wicks from prematurely triggering the SL before structural reversal.
> 2. **Safety Buffer Calculation**:
>    - **Buy setup (Long):** The SL must be calculated at `swing_low * 0.999` (a minimum of 0.1% safety buffer below the validated Swing Low extreme).
>    - **Sell setup (Short):** The SL must be calculated at `swing_high * 1.001` (a minimum of 0.1% safety buffer above the validated Swing High extreme).
> 3. **Manual Entry Logging Validation:** If the user manually edits the Stop Loss to be inside the swing extreme range during trade logging or edit operations (e.g. SL higher than swing_low for buys, or SL lower than swing_high for sells), the backend must reject the modification with a validation error to prevent arbitrary SL placement.

## 20. Fixed Range Volume Profile (FRVP) Confluence Protocol (New Rule)
> [!IMPORTANT]
> **FRVP CONFLUENCE RULES:**
> 1. **Programmatic Volume Profile Calculation:** The system calculates a 24-bin volume profile using the high, low, and volume of a broad visible range of the last 200 candles on the active timeframe (මෑතකදී දිස්වන පුළුල් ඉටිපන්දම් 200 ක පරාසයක්).
> 2. **High Volume Node (HVN) Alignment Check:**
>    - The recommended Limit Entry price must reside within a 0.5% tolerance threshold of a programmatically calculated High Volume Node (HVN) to verify support/resistance density.
>    - Setups that do not align with a high-density volume zone should flag a warning on the checklist tree to alert the user of potential low-volume breakout risk.

## 21. High-Velocity Execution & Dynamic Target Optimization Protocol (New Rule)
> [!IMPORTANT]
> **HIGH-VELOCITY EXECUTION & DYNAMIC TARGET OPTIMIZATION RULES:**
> 1. **5-8 Minutes Expected Entry Fill:** The analysis engine recommends entry prices in close proximity to the current market price so that setups are typically filled/triggered within **5 to 8 minutes** of logging. No hard timeout invalidation should be applied to pending trades.
> 2. **10-15 Minutes Expected Target Fill:** Take Profit targets are configured within a tight range to ensure they can typically be hit within **10 to 15 minutes** of running execution. No hard timeout closure or forced resolve should be applied to running trades.
> 3. **Dynamic 1:2 to 1:4 Risk-to-Reward Target Allocation:** Instead of a fixed 1:4 or 1:3 target, the Take Profit target must reside strictly between **1:2.0 and 1:4.0** RR. The analysis engine must dynamically identify the nearest minor reversal swing extreme or FVG/OB boundary within this 1:2.0 to 1:4.0 RR range to use as the Take Profit target, maximizing target probability while meeting minimum RR requirements. If no local reversal extreme is identified in range, a default 1:3.0 RR target is applied.

## 22. Strict TCS Rule Integrity & Non-Bypass Lockout (TCS Rule 11)
> [!IMPORTANT]
> **STRICT TCS NON-BYPASS LOCKOUT:**
> 1. Under no circumstances should the TCS analysis engine, background scanners, or execution trackers bypass or compromise any of the 10 active TCS rules. 
> 2. If even a single TCS confirmation or parameter check fails, the setup must be immediately suppressed and locked out of execution (returning "No Entry"). No overrides are allowed.
> 3. **Sinhala Translation (සිංහල පරිවර්තනය):** මෙම TCS රීතිවලින් පරිබාහිරව හෝ කිසිදු රීතියක් මඟහැර (bypass) කිසිදු අයුරකින් ඇතුළත් වීම් (entries) නිර්දේශ කිරීම හෝ සිදු කිරීම නොකළ යුතුය. එක් නීතියක් හෝ අසාර්ථක වුවහොත් එම setup එක වහාම අවලංගු කර lockout කළ යුතුය.

## 23. High-Velocity Breakaway FVG & Closest Zone Execution Protocol (Updated & Merged)
> [!IMPORTANT]
> **CLOSEST BREAKAWAY FVG & HIGH-VELOCITY SCALPING RULES:**
> 1. **1m/3m/5m Scalping Zone Prioritization:** For high-velocity 1-minute, 3-minute, and 5-minute scalping setups, the system must strictly prioritize the **Closest Unmitigated Fair Value Gap (FVG) or Order Block** located within 0.08% to 0.20% of current market price (incorporating the 0.04% Rule 62 proximity buffer). Deep 61.8%–78.6% Fibonacci retracements are strictly bypassed for fast scalping to prevent missed breakout momentum trades.
> 2. **5-8 Minute Guaranteed Fast Fill:** Placing the entry at the closest breakaway FVG ensures orders are touched and filled within 5 to 8 minutes on shallow pullbacks, strictly catching momentum waves with 1:2, 1:3, and 1:4 RR targets.
> 3. **HTF Dealing Range Retracements (15m/1H):** Deep 50.0%–78.6% Golden Zone retracements are strictly reserved for higher timeframes (15m / 1H macro swings) and slow market consolidation phases.
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):** 1-Minute / 3-Minute අධිවේගී Scalping වෙළඳාම් සඳහා, 61.8% ක ගැඹුරු Fibonacci මට්ටම් වලට මිල එනතුරු බලා නොසිට, වත්මන් මිලට ආසන්නයෙන්ම (0.08% - 0.20% දුරින්) හැදෙන **ආසන්නතම 1m FVG / Order Block සීමාවෙන් 0.04% Buffer එක සහිතව කෙළින්ම Entry එක ලබා දිය යුතුය**. එමඟින් විනාඩි 5-8 කදී Order එක fill වී Trade එක miss වීම 100% ක්ම වැළකේ. ගැඹුරු 61.8% Fibonacci මට්ටම් භාවිත කරන්නේ 15m සහ 1H Macro Swings සඳහා පමණි.

## 24. Volume Profile POC Retest Alignment Protocol (New Rule)
> [!IMPORTANT]
> **VOLUME PROFILE POC ALIGNMENT RULES:**
> 1. **Retest of High Density Zone:** The entry price must reside near the Point of Control (POC) or a programmatically calculated High Volume Node (HVN) area (within a 0.5% tolerance threshold) to verify strong support/resistance density.
> 2. **Avoid Low Volume Areas:** Setups residing in low volume gaps must be flagged as high risk on the checklist.

## 25. SMC OB/FVG Mitigation Stop-Loss Buffer Protection (New Rule)
> [!IMPORTANT]
> **SMC OB/FVG STOP-LOSS BUFFER RULES:**
> 1. **Protection Against Stop-Hunts:** If an unmitigated Order Block (OB) or Fair Value Gap (FVG) is located directly at or near the Swing Extreme boundary where the Stop Loss (SL) is to be placed, the Stop Loss must strictly be placed past the outer boundary of the OB/FVG (whichever is further) with an additional safe buffer. This prevents market sweeps and wicks from prematurely triggering the SL at the FVG/OB edge before reversing.
> 2. **Stop Loss Buffer Calculation:**
>    - **Buy setup (Long):** Place the Stop Loss at `min(swing_low, ob_low, fvg_low) * 0.999` (0.1% buffer below the lowest boundary of the Swing Low, OB, or FVG).
>    - **Sell setup (Short):** Place the Stop Loss at `max(swing_high, ob_high, fvg_high) * 1.001` (0.1% buffer above the highest boundary of the Swing High, OB, or FVG).
> 3. **Sinhala Translation (සිංහල පරිවර්තනය):** Stop Loss (SL) එක සැමවිටම Swing Extreme හෝ අදාළ OB/FVG සීමාවෙන් ඔබ්බට (outer boundary) තැබිය යුතුය. මිලදී ගැනීමේදී (Buy) OB/FVG අවම සීමාවට 0.1% ක් පහළින්ද (`min * 0.999`), විකිණීමේදී (Sell) OB/FVG උපරිම සීමාවට 0.1% ක් ඉහළින්ද (`max * 1.001`) SL එක තැබීමෙන්, වෙළඳපොල wick sweep එකකින් SL එක වැදීම (stop-hunt) වළක්වයි.

## 26. Reversal Execution & Mandatory CHoCH Protocol (New Rule)
> [!IMPORTANT]
> **REVERSAL EXECUTION & MANDATORY CHOCH RULES:**
> 1. **CHoCH/MSS is Strictly Mandatory:** A Market Structure Shift (MSS) or Change of Character (CHoCH) is strictly MANDATORY to execute any reversal trade setup. Under no circumstances should a reversal entry be advised without a confirmed CHoCH/MSS (a clear breakout close of the recent swing high/low with a strong displacement candle body). If no validated CHoCH/MSS has occurred, the setup is considered invalid and must be locked out.
> 2. **Reversal Layouts Mapping:**
>    - **For Bearish Reversal (Sell Limit Setup):** Upward manipulation sweeps BSL/Highs ($) -> Bearish CHoCH/MSS (Swing Low breakout close to the downside) -> Pullback to supply OB/FVG -> Sell Limit order.
>    - **For Bullish Reversal (Buy Limit Setup):** Downward manipulation sweeps SSL/Lows ($) -> Bullish CHoCH/MSS (Swing High breakout close to the upside) -> Pullback to demand OB/FVG -> Buy Limit order.
> 3. **Sinhala Translation (සිංහල පරිවර්තනය):** වෙළඳපල ප්‍රවණතාවය ආපසු හැරීමේදී (Reversal) CHoCH හෝ MSS එකක් නිල වශයෙන් සනාථ වීම (displaced candle close එකක් මඟින්) අනිවාර්ය වේ. CHoCH/MSS එකක් නොමැතිව කිසිදු අයුරකින් ඇතුල්වීමක් (Entry) නිර්දේශ නොකළ යුතුය:
>    - Bearish Reversal (Sell Limit): උඩින් ඇති Highs ($) sweep වී, Bearish CHoCH/MSS එකක් (Swing Low breakout) ඇතිවීමෙන් පසු Pullback එකකදී Sell Limit එන්ට්‍රිය ලබාදෙයි.
>    - Bullish Reversal (Buy Limit): පහළින් ඇති Lows ($) sweep වී, Bullish CHoCH/MSS එකක් (Swing High breakout) ඇතිවීමෙන් පසු Pullback එකකදී Buy Limit එන්ට්‍රිය ලබාදෙයි.

## 27. SMC MentorFX Multi-PDF Structural Layout Integration Protocol (New Rule)
> [!IMPORTANT]
> **SMC MENTORFX MULTI-PDF INTEGRATION RULES:**
> 1. **7 Guides Alignment:** All trade setups must align strictly with the structural patterns demonstrated in the 7 SMC MentorFX PDF guides (consisting of 1 previous PDF and 6 current PDFs).
> 2. **Bullish Entry/Reversal Layout:** Traces Swing Low Sweep ($) -> CHoCH/MSS upside -> Pullback to sweep Inducement (IDM) -> Tap unmitigated Bullish OB (Top Edge) -> Buy Limit entry.
> 3. **Bearish Entry/Reversal Layout:** Traces Swing High Sweep ($) -> CHoCH/MSS downside -> Pullback to sweep Inducement (IDM) -> Tap unmitigated Bearish OB (Bottom Edge) -> Sell Limit entry.
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):** සියලුම වෙළඳ සෙටප්ස් ඔබ ලබා දුන් PDF මාර්ගෝපදේශ 7 හි දැක්වෙන රටාවන්ට (BOS, CH, Inducement sweeps, and OB retests) අනුකූලව සිදු විය යුතුය.

## 28. FVG/OB First-Tapped Boundary Entry Protocol (New Rule)
> [!IMPORTANT]
> **FVG/OB BOUNDARY ENTRY RULES:**
> 1. **Outer Boundary Entry Placement:** When the market pulls back to tap an unmitigated Fair Value Gap (FVG) or Order Block (OB) zone, there is a high probability of immediate reversal upon first contact. Therefore, the recommended Limit Entry price must be placed exactly at the outer boundary/edge of the zone (the top edge for Buy setups, and the bottom edge for Sell setups) where the market first enters the zone.
> 2. **No Middle/50% Placements:** Do not place the entry price at the 50% consequent encroachment or mean threshold by default, to ensure that the order is successfully filled before the market reverses.
> 3. **Sinhala Translation (සිංහල පරිවර්තනය):** FVG/OB කලාපයේ (zone) මිල ස්පර්ශ කර (tap කර) වහාම ආපසු හැරීමට ඇති ඉඩකඩ වැඩි බැවින්, ඇතුල්වීමේ මිල (Entry Price) කලාපය මැදින් (50% level) නොතබා, වෙළඳපල මිල පැමිණෙන දිශාවේ ඇති කලාපයේ පළමු සීමාවෙහි (outer boundary / edge - Buy සෙටප් සඳහා ඉහළ සීමාවේ සහ Sell සෙටප් සඳහා පහළ සීමාවේ) තැබිය යුතුය.

## 29. Gemini API Billing & Request Protection Protocol (New Rule)
> [!IMPORTANT]
> **GEMINI API BILLING PROTECTION RULES:**
> 1. **Manual Trigger Only:** The Gemini AI API must ONLY be triggered during manual, on-demand UI "Scan Market" or "Run Analysis" / "Search" operations initiated explicitly by the user.
> 2. **Zero Background Usage:** Any background tracking loop, watchlist monitoring loop, price check loop, or status-polling loop must NEVER call the Gemini API directly, and must calculate parameters programmatically and locally in Python to guarantee 100% free and credit-safe operation.
> 3. **Bypassing / Blocking Violating Requests:** If any request attempts to call Google AI services automatically in the background, it must be intercepted and served locally using fallback mock responses.
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):** Gemini API එක ක්‍රියාත්මක විය යුත්තේ පරිශීලකයා විසින් මැනුවල් ලෙස සිදු කරන සෙවීම් වලදී ("Search" හෝ "Run Analysis" ක්ලික් කළ විට) පමණි. පසුබිමින් ධාවනය වන අනෙකුත් සියලුම ක්‍රියාවලීන් (trackers, polling loops) දේශීයව (locally in Python) ක්‍රියාත්මක විය යුතු අතර, අනවශ්‍ය ලෙස Google Gemini API එක කැඳවීම සහ ක්‍රෙඩිට්ස් භාවිතය තහනම් වේ.

## 30. SMC Sniper Limit Order Entry & Patient Execution Protocol (New Rule)
> [!IMPORTANT]
> **SMC SNIPER LIMIT ENTRY & PATIENT EXECUTION RULES:**
> 1. **High-Confirmation Sniper Entry:** The bot must focus strictly on identifying and delivering high-confirmation Limit Entry prices at key FVG/OB boundaries, where the price is expected to tap and reverse immediately with maximum probability.
> 2. **Pullback Patience & Minimum Distance Buffer:** The bot must never advise immediate market execution or shallow limit entries close to the current price (within 0.05%). The entry price must strictly have a minimum distance of 0.1% to 0.5% from the current market price (the last candle's close) at the deepest, most significant unmitigated FVG/OB boundary in the pullback leg. This ensures it is a true pending pullback entry, giving the user at least 5 minutes to place the limit order before it triggers. If no unmitigated FVG/OB boundary exists within this 0.1% to 0.5% buffer, the setup is considered invalid (is_valid = false) and must be locked out.
> 3. **Absolute Stop Loss Protection:** To prevent waiting orders from getting stopped out prematurely by manipulation wicks, the Stop Loss must strictly be placed past the absolute Swing Extreme (Strong High/Low) with the programmatic 0.1% buffer (Rule 19 & 25).
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):** වත්මන් වෙළඳපල මිලට ආසන්න නොගැඹුරු (shallow) ඇතුල්වීම් හෝ ක්ෂණික වෙළඳපල ඇණවුම් (market orders) නිර්දේශ කිරීම තහනම් වේ. ඇතුල්වීමේ මිල සැමවිටම වත්මන් මිලට වඩා 0.1% - 0.5% අතර පරතරයකින් පිහිටි ප්‍රධාන unmitigated FVG/OB සීමාවක තිබිය යුතුය. එමඟින් ඇණවුම ක්‍රියාත්මක වීමට පෙර පරිශීලකයාට ලිමිට් ඕඩරය සැකසීමට අවම වශයෙන් විනාඩි 5 ක කාලයක් ලැබේ. මෙම සීමාවන් නොමැති නම් සෙටප් එක අවලංගු කළ යුතුය. Stop Loss එක සැමවිටම swing extreme එකෙන් පිටත 0.1% ක බෆරයක් සහිතව තැබිය යුතුය.

## 31. SMC EQL/EQH Liquidity Sweep & HTF Zone Stop Loss Protection Protocol (New Rule)
> [!IMPORTANT]
> **SMC EQL/EQH LIQUIDITY & HTF OB RETEST PROTECTION RULES:**
> 1. **EQL/EQH Stop Loss Prohibited:** The system must never place the Stop Loss (SL) directly below/above an active **Equal Lows (EQL)** or **Equal Highs (EQH)** retail liquidity pool. Retail liquidity pools are high-probability targets for institutional stop-hunts and sweeps.
> 2. **HTF Zone & Strong Low Protection:** If an unmitigated Higher Timeframe (HTF) Demand/Supply zone (such as 15m/1H Order Block) or a confirmed **Strong Low / Strong High** extreme lies underneath/above the EQL/EQH pool, the Stop Loss must strictly be placed past the outer boundary of that HTF zone or Strong Extreme with the 0.1% safety buffer.
> 3. **Maximum Risk Range Lockout:** If placing the SL past the HTF zone or Strong Low/High violates the maximum allowed risk range (0.85% for Crypto, 0.15% for traditional Forex/Gold), the setup must be immediately invalidated (`is_valid = false`) and suppressed to shield the user from entering high-risk, wide SL setups.
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):** වෙළඳ සෙටප් එකක Stop Loss (SL) එක කිසිසේත්ම Equal Lows (EQL) හෝ Equal Highs (EQH) මට්ටමකට ආසන්නව නොතැබිය යුතුය. මන්ද මාකට් එක හැමවෙලේම EQL/EQH වලට යටින් ඇති orders sweep කිරීමට නැඹුරු වේ. ඊට පහළින් Strong Low හෝ HTF Demand zone එකක් තිබේ නම්, SL එක එම ශක්තිමත් මට්ටමට වඩා 0.1% ක් පහළින් තැබිය යුතුය. මෙම ආරක්ෂිත SL මට්ටම දැමූ පසු SL පරාසය Crypto සඳහා 0.85% සීමාව ඉක්මවයි නම්, එම සෙටප් එක අවලංගු කළ යුතුය.

## 32. Selected Timeframe Breakout & FVG Retracement Strategy (New Rule)
> [!IMPORTANT]
> **SELECTED TIMEFRAME SMC STRATEGY RULES:**
> 1. **Rule 1: Market Bias & Direction Detection:** Establish market direction strictly on the selected timeframe structure (e.g., 1m or 15m). Do NOT use moving averages or indicators. Ignore trends on other timeframes.
>    - BULLISH BIAS (BUY ONLY): Market is making HH/HL with upward structural breaks (BOS). Look ONLY for Buy opportunities on this timeframe.
>    - BEARISH BIAS (SELL ONLY): Market is making LH/LL with downward structural breaks (BOS). Look ONLY for Sell opportunities on this timeframe.
> 2. **Rule 2: Setup & Rejection Zone:**
>    - Identify unmitigated broken structures (BOS), FVG, or Order Blocks (OB) in line with the Bias, and key swing high/low liquidity zones strictly on the selected timeframe.
>    - Wait for the price to retrace into the FVG/OB. Observe a Liquidity Sweep (wick sweep without body close breakout) showing rejection/weakness.
>    - Draw a Rectangle Zone from the closing price of that rejection candle to its absolute wick extreme (high/low).
> 3. **Rule 3: Execution & Entry Criteria:**
>    - Monitor confirmation patterns (MSS, Engulfing/Morning Star, or Marubozu candle close) strictly on the selected timeframe.
>    - **FOR A BUY ENTRY (Buy Limit):** Price must enter the Rectangle Zone.
>      * Entry Method A (Breakout): Trigger when a candle breaks and CLOSES completely (body close) above the top of the Rectangle.
>      * Entry Method B (Retracement): Wait for price to retrace to the 50% level of the FVG and enter upon confirmation.
>    - **FOR A SELL ENTRY (Sell Limit):** Price must enter the Rectangle Zone.
>      * Entry Method A (Breakout): Trigger when a candle breaks and CLOSES completely (body close) below the bottom of the Rectangle.
>      * Entry Method B (Retracement): Wait for price to retrace to the 50% level of the FVG and enter upon confirmation.
> 4. **Rule 4: Risk Management (SL & TP):**
>    - **STOP LOSS (SL):** Place SL slightly past the nearest major swing extreme low (for BUY) or swing high (for SELL) with the 0.1% buffer (using the python override). Keep SL extremely tight.
>    - **TAKE PROFIT (TP):** Target key structural levels or aim for high Risk-to-Reward (RR) ratios of 3:1, 4:1, or 5:1.
> 5. **Sinhala Translation (සිංහල පරිවර්තනය):** 
>    - Market Bias සහ Setup එක තීරණය කරන්නේ පරිශීලකයා තෝරාගත් (select කළ) timeframe එකෙහි ව්‍යුහය (HH/HL/BOS) මඟින් පමණි. වෙනත් කාල රාමු වල ට්‍රෙන්ඩ්ස් මෙයට බල නොපායි.
>    - මිල FVG/OB එකකට පැමිණ wick sweep එකක් (rejection) සිදුකළ විට, එම ඉටිපන්දමේ body close මට්ටමේ සිට wick extreme එක දක්වා Rectangle එකක් අඳින්න. 
>    - එම Rectangle කලාපයට මිල ඇතුල් වූ විට:
>      * Buy සෙටප් සඳහා: ඉටිපන්දමක් Rectangle එකෙන් ඉහළින් body close එකක් දීමෙන් (Method A) හෝ FVG එකෙහි 50% මට්ටමට pullback වීමෙන් (Method B) ඇතුල්වීම් සිදුකරයි.
>      * Sell සෙටප් සඳහා: ඉටිපන්දමක් Rectangle එකෙන් පහළින් body close එකක් දීමෙන් (Method A) හෝ FVG එකෙහි 50% මට්ටමට pullback වීමෙන් (Method B) ඇතුල්වීම් සිදුකරයි.
>    - Stop Loss එක local swing low/high එකට පිටතින් ඉතාමත් තදින් (tight SL) තැබිය යුතුය. TP ඉලක්කය 3:1, 4:1, හෝ 5:1 RR විය යුතුය.

## 33. LuxAlgo Smart Money Concepts (SMC) Indicator Alignment Protocol (New Rule)
> [!IMPORTANT]
> **LUXALGO SMC INDICATOR ALIGNMENT RULES:**
> 1. **Visual Indicator Matching:** The bot's background scan, local programmatics, and Gemini AI analysis must strictly model and emulate the LuxAlgo Smart Money Concepts indicator settings shown on the TradingView screen.
> 2. **Structural Element Checks:** Detect and trace:
>    - Break of Structure (BOS) and Change of Character (CHoCH / MSS) shifts.
>    - Order Blocks (OB) - Demand (Bullish) and Supply (Bearish) zones.
>    - Equal Highs (EQH) and Equal Lows (EQL) retail liquidity pools.
>    - Strong Highs / Strong Lows and Weak Highs / Weak Lows swing extremes.
>    - Fair Value Gaps (FVG) and Liquidity Voids.
> 3. **Bilingual Requirement:** Ensure that all analytical confluences and setups clearly mention LuxAlgo SMC alignment in reasoning text and Sinhala translations.
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):** පද්ධතියේ SMC විශ්ලේෂණය TradingView හි ඇති **LuxAlgo Smart Money Concepts** indicator එකෙහි රටාවන්ට (BOS, CHoCH/MSS, EQL, EQH, Order Blocks, FVGs, Strong/Weak Highs/Lows) 100% ක්ම අනුකූලව සිදු විය යුතුය. එමඟින් බොට් එකෙහි trade setups චාර්ට් එකෙහි ඇසට පෙනෙන මට්ටම් සමඟ සම්පූර්ණයෙන්ම ගැලපේ.

## 34. Proximity Spread Buffer Protocol (New Rule)
> [!IMPORTANT]
> **PROXIMITY SPREAD BUFFER RULES:**
> 1. **Entry Spread Buffer Adjustment:** To prevent missing limit entry orders by a fraction of a pip/cent due to spread and institutional front-running near FVG/OB boundaries, the calculated Limit Entry price must be adjusted slightly closer to the current market price by adding a **0.04% proximity spread buffer**.
> 2. **Buffer Calculations**:
>    - **Buy Limit (Long Setup):** The Limit Entry price must be adjusted upwards: `entry_price = entry_price * 1.0004`.
>    - **Sell Limit (Short Setup):** The Limit Entry price must be adjusted downwards: `entry_price = entry_price * 0.9996`.
> 3. **Rule Enforcement:** This buffer must be programmatically applied to all calculated/fallback limit entries, ensuring higher execution fill rates on shallow pullbacks.
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):** FVG/OB සීමාවන්ට මිල ළඟා වී, spread එක හෝ front-running හේතුවෙන් ලිමිට් ඇණවුම් ක්‍රියාත්මක නොවී හැරී යාම (missed entries) වැළැක්වීම සඳහා, ගණනය කරන ලද Limit Entry මිල සැමවිටම වත්මන් මිලට 0.04% ක් ආසන්න වන සේ බෆරයක් (Spread Buffer) තබා සැකසිය යුතුය:
>    - Buy Limit: ඇතුල්වීමේ මිල 0.04% ක් ඉහළට සකසයි (`entry * 1.0004`).
>    - Sell Limit: ඇතුල්වීමේ මිල 0.04% ක් පහළට සකසයි (`entry * 0.9996`).

## 35. Proactive Console Error & Server Maintenance Protocol (New Rule)
> [!IMPORTANT]
> **PROACTIVE ERROR RESOLUTION & SERVER MONITORING:**
> 1. **Zero Console Errors Policy:** The bot must ensure the frontend dashboard displays zero console errors, hydration mismatches, or network fetch errors. 
> 2. **Auto-Resolution of Server Conflicts:** If any port conflicts, webpack build cache corruption, or server dropouts occur, the bot must proactively detect them, kill competing tasks (such as duplicate Node.js or Uvicorn processes), clear stale caches (`.next`), and restart the server environment to ensure 100% online availability.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** බ්‍රවුසරයෙහි කිසිදු console error එකක්, hydration mismatch එකක් හෝ fetch error එකක් පෙන්වීමට ඉඩ නොතැබිය යුතුය. යම් හෙයකින් සර්වර් එකෙහි port conflict එකක් හෝ cache බිඳ වැටීමක් සිදු වුවහොත්, වහාම පැරණි ක්‍රියාවලීන් (processes) kill කර, `.next` cache එක මකා දමා සර්වර් එක නැවත පණ ගැන්විය යුතුය.

## 36. Closest Valid FVG/OB Zone Selection Protocol (New Rule)
> [!IMPORTANT]
> **CLOSEST VALID ZONE SELECTION RULES:**
> 1. **Closest Zone Selection Over Deepest:** Within the 0.35% threshold distance filter, when multiple valid unmitigated Fair Value Gaps (FVG) or Order Blocks (OB) are identified below/above the midpoint, the bot must strictly select the candidate zone **closest to the current market price** (the highest price for Buy setups, and the lowest price for Sell setups). This overrides the deepest zone/pullback selection logic to maximize order trigger probability on high-momentum trends.
> 2. **Rule Enforcement:**
>    - **Bullish (Buy Limit Setup):** Select the candidate with the maximum price within the close candidates: `max(close_candidates, key=lambda x: x[0])`.
>    - **Bearish (Sell Limit Setup):** Select the candidate with the minimum price within the close candidates: `min(close_candidates, key=lambda x: x[0])`.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** වත්මන් මිලට ආසන්නතම වලංගු කලාපය (closest FVG/OB zone) තෝරා ගැනීමේ ඇල්ගොරිතමය අනිවාර්යයෙන්ම ක්‍රියාත්මක කළ යුතුය. වත්මන් මිලට 0.35% සීමාව තුළ වලංගු කලාප කිහිපයක් ඇති විට, ගැඹුරුම කලාපය වෙනුවට සැමවිටම වත්මන් මිලට ආසන්නතම කලාපය (Buy setups සඳහා වැඩිම මිල සහිත සහ Sell setups සඳහා අවම මිල සහිත) තෝරාගත යුතුය.

## 37. Strict 15m Trend Alignment Filter (New Rule)
> [!IMPORTANT]
> **STRICT 15M TREND ALIGNMENT RULES:**
> 1. **Anti-Counter-Trend Lockout:** To eliminate high-risk counter-trend losses on the 1-minute chart, when the active execution timeframe is set to 1m, any generated trade setups must strictly align with the 15-minute timeframe trend. 
> 2. **Rule Enforcement:**
>    - A **Buy Limit Setup** is allowed ONLY if the active 15m trend is `BULLISH`. If the 15m trend is `BEARISH`, the setup must be immediately invalidated (`No Entry (15m Trend Mismatch Lockout)`).
>    - A **Sell Limit Setup** is allowed ONLY if the active 15m trend is `BEARISH`. If the 15m trend is `BULLISH`, the setup must be immediately invalidated (`No Entry (15m Trend Mismatch Lockout)`).
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** 1m කාලරාමුවෙහි සිදුවන පාඩු අවම කරගැනීම සඳහා, වත්මන් 1m setup දිශාව 15m කාලරාමුවේ ප්‍රධාන ප්‍රවණතාවය (trend) සමඟ 100% ක්ම ගැලපිය යුතුය. 15m trend එක Bearish නම් Buy setups ද, 15m trend එක Bullish නම් Sell setups ද සම්පූර්ණයෙන්ම අවහිර කර lockout කළ යුතුය.

## 38. 90% Minimum Confidence Score Limit (New Rule)
> [!IMPORTANT]
> **90% MINIMUM CONFIDENCE LIMIT RULES:**
> 1. **Confidence Score Threshold Increase:** The minimum strategy confidence score required to validate and execute any trade setup is increased from 80% to **90%**.
> 2. **Rule Enforcement:** If the programmatically calculated confluence rating is less than 90%, the bot must suppress the setup and return `No Entry (Confidence < 90%)` to prevent execution of lower-probability setups.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** වෙළඳ සෙටප් එකක් වලංගු කිරීම සඳහා අවශ්‍ය අවම Confluence අගය 80% සිට **90%** දක්වා ඉහළ නංවා ඇත. Confluence අගය 90% ට වඩා අඩු සෙටප්ස් ඩෑෂ්බෝඩ් එකෙහි `No Entry (Confidence < 90%)` ලෙස අවහිර කළ යුතුය.

## 39. Major Structural Swing Stop Loss Protocol (New Rule)
> [!IMPORTANT]
> **MAJOR STRUCTURAL SWING STOP-LOSS RULES:**
> 1. **Major Swing Selection Over Minor Wicks:** When timeframe is set to 1m (scalping mode), the Stop Loss must strictly be placed past the true Major Structural Swing Extreme, not a minor inner wick. The system automatically scans for a major extreme by requiring a minimum of a 15-candle window on BOTH sides of the peak/valley (e.g., the highest point in a 31-candle window). This filters out weak inner pullbacks during dumps/pumps.
> 2. **Tight Safety Buffer (0.05%):** Place the SL past this major swing extreme at major_swing_low * 0.9995 (for Buys) or major_swing_high * 1.0005 (for Sells) to keep risk range extremely tight while protecting from stop-hunts.
> 3. **0.25% Risk Capping:** Max allowed risk range is capped strictly at 0.25% to force the optimized entry price closer to the SL level, generating a high-probability close-proximity 1:3/1:4 RR Take Profit target.
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** 1m කාලරාමුවෙහි Scalp setups සඳහා, Stop Loss (SL) එක තබන්නේ කුඩා Wicks වලට නොව 15-candle window එකක් මඟින් තහවුරු කරන ලද **ප්‍රධාන Structural Swing Extreme** සීමාවට 0.05% ක කුඩා බෆරයක් සහිතවය. තවද, උපරිම අවදානම (Risk Range) 0.25% දක්වා සීමා කිරීම මඟින් එන්ට්‍රිය SL එකට ආසන්න කර TP ඉලක්කය ඉතා ආසන්නයට රැගෙන එයි.

## 40. 1500-Candle Multi-Timeframe Key Level Scanner (New Rule)
> [!IMPORTANT]
> **1500-CANDLE KEY LEVEL SCANNER RULES:**
> 1. **1500-Candle Lookback Scan:** When analyzing any trade setup on the selected timeframe, the system must scan up to the last 1500 historical candles (මෑතකදී දිස්වන පුළුල් ඉටිදැම් 1500 ක පරාසයක්) chronologically to map structure, swings (highs/lows), equal extremes (EQH/EQL), and unmitigated FVG/OB zones.
> 2. **Proximity Alignment Check:** Reconfirm that the entry price aligns with the closest valid FVG or OB zone (Rule 36) or major structural level within this deep historical lookback, with the stop loss set safely outside the local/HTF swing extreme to produce a high-precision sniper setup.
> 3. **Expected Fill Time:** Ensure the entry price is configured close enough to the current price so that it is filled within 5 to 8 minutes.
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** මෙම රීතිය මඟින් සක්‍රීය කාලරාමුවේ පසුගිය ඉටිපන්දම් 1500 ක පරාසයක් විශ්ලේෂණය කර, එහි ඇති සියලුම Swing High/Low, OB, FVG, සහ EQH/EQL මට්ටම් හඳුනාගෙන, ඇතුල්වීමේ මිලට ආසන්නතම මට්ටම ගලපනු ලබයි.

## 41. Opposing HTF POI Dynamic RR Lockout Protocol (New Rule)
> [!IMPORTANT]
> **OPPOSING HTF POI DYNAMIC RR RULES:**
> 1. **Opposing POI Check:** For any 1m scalp setup, the system must automatically scan the 15m and 1h timeframes for unmitigated opposing POIs (Demand zones/OB/FVG for Bearish Sell setups, or Supply zones/OB/FVG for Bullish Buy setups).
> 2. **Dynamic Risk-to-Reward (RR) Filter (1:2.0 Threshold):** If a major opposing HTF POI is located near the entry price, the system must measure the Risk-to-Reward (RR) distance from the Entry Price to the opposing POI against the Stop Loss. If this space provides a 1:2.0 RR or higher, the setup is VALID, and the Take Profit must be dynamically placed directly before the opposing POI.
> 3. **Lockout Condition:** Only if the available space to the opposing POI yields less than a 1:2.0 RR should the setup be invalidated (No Entry (Opposing HTF POI Lock)).
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** 1m scalp setups වලදී, ප්‍රතිවිරුද්ධ HTF කලාපයක් (Demand/Supply zone) පිහිටා ඇති දුර ප්‍රමාණය Stop Loss එකට සාපේක්ෂව 1:2.0 (Risk-to-Reward) අගයකට වඩා අඩුවෙන් පවතී නම් පමණක් මිල හැරී යාමේ අවදානම ඉහළ බැවින් එම setup එක වහාම අවලංගු කර No Entry (Opposing HTF POI Lock) ලෙස සටහන් කළ යුතුය. RR එක 1:2.0 ට වඩා වැඩි නම්, Take Profit එක අදාළ කලාපයට පෙර සකසා Entry එක ලබා දිය යුතුය.

## 42. 15m Confirmation / Rejection Block Entry (New Rule)
> [!IMPORTANT]
> **15M CONFIRMATION ENTRY RULES:**
> 1. **2nd Entry Model Enforcement:** When timeframe is set to 15m, the entry calculation must strictly follow the 2nd Entry Model (Confirmation Entry) rather than placing early limit orders.
> 2. **Rejection Block Entry Level:** Place the Limit Entry exactly at the Rejection Block sweep boundary (Buy at `recent_sl_low * 1.0004` (sweep low + 0.04% buffer); Sell at `recent_sl_high * 0.9996` (sweep high - 0.04% buffer)) to catch the retest of the swept zone.
> 3. **Tight Safety Buffer (0.05%):** Place the SL strictly past the new swing extreme with a tight 0.05% buffer (Buy SL is `recent_sl_low * 0.9995`; Sell SL is `recent_sl_high * 1.0005`) to prevent stop-hunts after the sweep.
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** 15m setups වලදී, ඇතුල්වීම සිදු කරන්නේ 2nd Entry Model (Confirmation Entry) ක්‍රමයටය. එනම්, එන්ට්‍රිය තබන්නේ Rejection Block (රීතියානුකූලව සිදුවන wick sweep කෙළවර) සීමාවෙහි වන අතර, Stop Loss (SL) එක තබන්නේ 0.05% ක ඉතා තද බෆරයක් සහිතව නවතම sweep සීමාවට එපිටිනි.

## 43. Minimum Stop-Loss Distance Protocol (New Rule)
> [!IMPORTANT]
> **MINIMUM STOP-LOSS DISTANCE RULES:**
> 1. **Minimum Distance Cap (0.10%):** To prevent stop-hunts caused by spreads or micro-wicks on ultra-narrow structures, the calculated Stop Loss level must strictly be placed at a minimum distance of **0.10%** from the entry price.
> 2. **Buffer Adjustment:** If the swing extreme is closer than 0.10% of the asset price (e.g. 0.029% risk), the Stop Loss is dynamically adjusted to this minimum safe distance (Buy SL <= `entry_price * 0.9990`; Sell SL >= `entry_price * 1.0010`).
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** ඉතාමත් කුඩා පරාසයන්හිදී සිදුවන spread stop-hunts වැළැක්වීම සඳහා, Stop Loss (SL) එක සැමවිටම ඇතුල්වීමේ මිලට වඩා අවම වශයෙන් **0.10%** ක දුරකින් (Buy SL: `entry_price * 0.9990` හෝ ඊට අඩු; Sell SL: `entry_price * 1.0010` හෝ ඊට වැඩි) පිහිටිය යුතුය.## 44. Deepest Unmitigated Zone Stop-Loss Coverage Protocol (New Rule)
> [!IMPORTANT]
> **DEEPEST UNMITIGATED ZONE STOP-LOSS COVERAGE RULES:**
> 1. **Complete Pullback Leg Scan:** When scanning for unmitigated FVG/OB zones to determine the safe Stop Loss boundary, the scanner search range is expanded to **1.5%** of the entry price to detect any active unmitigated zones in the deep pullback leg.
> 2. **Deepest Zone Protection:** The Stop Loss must be calculated safely below/above the deepest unmitigated boundary detected in this 1.5% range (Buy SL is `min(swing_low, deepest_zone_bottom) * 0.9995`; Sell SL is `max(swing_high, deepest_zone_top) * 1.0005`).
> 3. **Dynamic Entry Optimization:** If this safe Stop Loss yields a risk distance greater than the strict **0.25%** max risk cap, the engine must dynamically push the Entry Price down/up to cap the risk distance strictly at **0.25%** relative to that deep Stop Loss.
> 4. **Lockout Enforcement:** If the optimized entry price exceeds the strict **0.35%** limit distance from the current price, the trade setup is immediately blocked as `No Entry (Pullback Distance Too Far)` to prevent stop-hunts on deep pullbacks.
> 5. **Bilingual Requirement (සිංහල පරිවර්තනය):** මෙම රීතිය මඟින් ඇතුල්වීමේ මිලෙහි සිට 1.5% ක් ගැඹුරට යන තෙක් ඇති සියලුම unmitigated FVG/OB මට්ටම් පරිලෝකනය කර, සැබෑ ගැඹුරුම සීමාවට එපිටින් Stop Loss (SL) එක තබයි. එහිදී අවදානම (risk) 0.25% සීමාව ඉක්මවන්නේ නම්, ඇතුල්වීමේ මිල ස්වයංක්‍රීයව වෙනස් කරන අතර, එය වත්මන් මිලට වඩා 0.35% සීමාව ඉක්මවා ඈත් වන්නේ නම් සෙටප් එක සම්පූර්ණයෙන්ම අවහිර (lockout) කරයි.


## 45. Multi-Timeframe POI Reversal & 5m Confirmation Protocol (New Rule)
> [!IMPORTANT]
> **MTF POI REVERSAL & 5M CONFIRMATION RULES:**
> 1. **Bypass 15m Trend Alignment:** The requirement that the 15-minute trend must align in the same direction is completely removed. Reversals off key levels are permitted regardless of the macro 15m trend.
> 2. **15m POI Mitigation Verification:** The setup must reside inside or have mitigated a valid 15-minute Order Block/FVG zone (or swept daily liquidity PDL/SSL or PDH/BSL).
> 3. **5m Trend/Momentum Alignment:** 
>    - **Buy setup (Long):** 1m trend must be BULLISH, and the 5m trend must be BULLISH (confirming reversal structure shift inside the zone).
>    - **Sell setup (Short):** 1m trend must be BEARISH, and the 5m trend must be BEARISH.
> 4. **5m Mismatch Lockout:** If the 5m trend/momentum does not align with the 1m setup direction, the setup is suppressed and locked out, returning `No Entry (5m Trend Mismatch)`.
> 5. **Bilingual Requirement (සිංහල පරිවර්තනය):** 15-Minute ප්‍රවණතාවය (trend) සමපාත වීමේ අවශ්‍යතාවය සම්පූර්ණයෙන්ම ඉවත් කර ඇත. 1m එන්ට්‍රියක් ගැනීමට නම්, මිල 15m Order Block/FVG කලාපයක් ස්පර්ශ කර තිබීම (mitigation) සහ 5-Minute ප්‍රවණතාවය (trend) 1m සෙටප් එකේ දිශාවටම (Buy සඳහා BULLISH, Sell සඳහා BEARISH) සමපාත වීම අනිවාර්ය වේ. 5m ප්‍රවණතාවය පටහැනි වුවහොත්, සෙටප් එක වහාම අවහිර කර `No Entry (5m Trend Mismatch)` ලෙස සටහන් කරයි.

## 46. Ultra-Tight 1m Stop-Loss Optimization Protocol (New Rule)
> [!IMPORTANT]
> **TIGHT SL FIX RULES:**
> 1. **0.15% Local Boundary Restraint:** When calculating the Stop Loss for 1-minute (1m) scalp setups, the system must NOT scan for deep historical unmitigated FVG/OB zones (like 1.5% away). It must ONLY consider local FVG/OB boundaries that reside within **0.15%** of the entry price (`0.0015` distance threshold) to ensure the Stop Loss remains tightly coupled to the local 1m structure.
> 2. **Protection Against Wide SL Rejection:** By keeping the Stop Loss incredibly tight, the calculated Risk Percentage remains extremely low, preventing the Entry Price from being artificially pushed away (optimized) and preventing the setup from being locked out by the 5-8 minute proximity threshold.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** 1m scalp එන්ට්‍රි සඳහා Stop Loss (SL) එක ගණනය කිරීමේදී ඈතින් පවතින ගැඹුරු කලාප සෙවීම වෙනුවට, ඇතුල්වීමේ මිලට 0.15% ක් පමණ ආසන්නයෙන් ඇති (local) 1m Swing ලක්ෂ්‍යය හෝ FVG එක පමණක් සැලකිල්ලට ගනී.

## 47. Dynamic Market Execution Upgrade Protocol (New Rule)
> [!IMPORTANT]
> **MARKET EXECUTION UPGRADE RULES:**
> 1. **Dynamic Risk-Based Market Entry:** If all 9 confluences are met, the system calculates the immediate natural risk percentage from the **Current Market Price** to the **Safe Stop Loss** (`|Current Price - SL| / Current Price`).
> 2. **Instant Execution Bypass (Bypass Rule 12):** If this immediate risk percentage is less than or equal to the maximum allowed risk cap (0.25% for 1m, 0.22% for other timeframes), the system must instantly upgrade the setup to a **Market Execution** (`Market Buy at {price}` or `Market Sell at {price}`).
> 3. **Pullback Distance Lock Bypass:** If the risk from the current price exceeds the maximum 0.25% cap, the system optimizes the Limit Order entry price. If this optimized Limit Order falls > 0.50% away from the current market price, the system must NOT lock out the trade with `No Entry (Pullback Distance Too Far)`. Instead, it must revert the setup to a **Market Execution** at the current market price, provided that a **1:2 Risk-to-Reward (RR)** ratio is still structurally achievable before hitting any opposing HTF POI.
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** වත්මන් වෙළඳපල මිලේ සිට Stop Loss එක දක්වා ඇති අවදානම (Risk) 0.25% ක උපරිම සීමාවට වඩා අඩු නම්, Limit එන්ට්‍රියක් ලැබෙන තෙක් බලා නොසිට වහාම Market Execution එකක් ලබා දෙයි. එසේම, ගණනය කළ Limit එන්ට්‍රිය 0.50% කට වඩා ඈතින් පිහිටයි නම්, සෙටප් එක අවහිර නොකර, වත්මන් මිලේ සිට 1:2 RR එකක් ලබාගත හැකිදැයි පරීක්ෂා කර Market Execution එකක් ලබා දීමට පද්ධතිය ක්‍රියා කරයි.

## 48. Inducement & EQH/EQL Sweep Filter Protocol (New Rule)
> [!IMPORTANT]
> **INDUCEMENT & LIQUIDITY TRAP PREVENTION RULES:**
> 1. **Mandatory HTF POI Mitigation:** The AI and background scanners must NEVER validate a 1-minute (1m) CHoCH (Market Structure Shift) if the price has not recently tapped into or mitigated a strong 15-minute (15m) or 1-Hour (1H) Order Block / Fair Value Gap (POI). Any 1m CHoCH forming in the middle of a range without HTF support must be classified as an "Inducement Trap" and ignored.
> 2. **EQH / EQL Avoidance:** Before validating a setup, the system must check for nearby Equal Highs (EQH) or Equal Lows (EQL). If the calculated Stop Loss resides exactly at or just inside an un-swept EQH/EQL liquidity pool, the setup must be locked out to prevent stop-hunts.
> 3. **Sweep Execution Requirement:** The system must wait for the EQH/EQL to be cleanly swept. The entry should only be taken from the very first valid 1m CHoCH that forms *after* the sweep, ensuring the Stop Loss is placed safely outside the newly formed extreme (which has already taken the liquidity).
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** 1m චාර්ට් එකේ හැදෙන CHoCH එකක් පිළිගත යුත්තේ එය 15m/1H කලාපයක් ස්පර්ශ කිරීමෙන් පසුව හැදුනොත් පමණි. එසේම, Stop Loss එක ආසන්නයේ EQH (Equal Highs) හෝ EQL (Equal Lows) ඇත්නම්, එම සෙටප් එක ප්‍රතික්ෂේප කර, මිල විසින් එම EQH/EQL ලක්ෂ්‍යය කඩාගෙන ගොස් (Sweep කර) හැදෙන ඊළඟ CHoCH එකෙන් පමණක් එන්ට්‍රිය ලබා දිය යුතුය.

## 49. Watchlist Sync & Race-Condition Prevention Protocol (New Rule)
> [!IMPORTANT]
> **RACE-CONDITION PREVENTION RULES:**
> 1. **No Automatic Sync Loop:** The frontend must never automatically sync the watchlist back to the database backend upon every periodic polling update. The automatic React `useEffect` synchronization on monitored array changes is strictly forbidden.
> 2. **Direct Manual-Only Sync:** List updates to backend SQLite databases (POST `/api/watchlist/smc` and `/api/watchlist/tcs`) must ONLY be triggered by manual user actions (clicking the track button or manual removal).
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** Polling loop එක මඟින් දත්ත ලබා ගන්නා විට (GET), වෙබ් පිටුව මඟින් නැවත database එකට POST කිරීම (sync කිරීම) සම්පූර්ණයෙන්ම තහනම් වේ. Database එක යාවත්කාලීන විය යුත්තේ මැනුවල් ලෙස කාසියක් එකතු කරන විට හෝ මකන විට පමණි.

## 50. Programmatic Local Scanner Verification Protocol (New Rule)
> [!IMPORTANT]
> **PROGRAMMATIC SCANNER RULES:**
> 1. **No Mock Fallback Data:** The background live scanner loop must run actual programmatic indicator validations (RSI, news, swing extremes, Fibonacci Golden ratio, and Rule 41 opposing POI checks) locally in Python. Returning mock data or fixed confluences when `local_only=True` is passed is strictly prohibited.
> 2. **Exact Sync Alignment:** The local programmatic results must evaluate the exact same parameters as manual scans to ensure 100% agreement between manual searches and watchlist monitoring status.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** පසුබිම් ස්කෑනරය ක්‍රියාත්මක වන විට කිසිදු විටෙක ව්‍යාජ උපස්ථ දත්ත (mock data) ලෝඩ් නොකළ යුතුය. එය මැනුවල් සර්ච් එකෙහිදී සිදුවන සියලුම Python ගණනය කිරීම් එලෙසින්ම සිදු කළ යුතුය.

## 51. Instant Watchlist Deletion upon Telegram Alert Confirmation (New Rule)
> [!IMPORTANT]
> **TELEGRAM ALERT WATCHLIST DELETION RULES:**
> 1. **Instant Removal:** Once a watchlist setup is confirmed ($\ge 90\%$ confidence) and the Telegram alert is sent, the backend scanner must immediately remove the coin from the SQLite database preferences.
> 2. **Anti-Spam Restriction:** Deleting the coin instantly from the active list prevents the bot from generating multiple duplicate Telegram alerts when the price oscillates.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** සෙටප් එක තහවුරු වී ටෙලිග්‍රෑම් පණිවිඩය ගිය සැනින්, නැවත නැවත ඇලර්ට් යෑම වැළැක්වීම සඳහා අදාළ කාසිය වහාම database එකෙන් සහ ඩෑෂ්බෝඩ් එකෙන් ඉවත් කළ යුතුය.

## 52. Closest Unmitigated Zone Entry Protocol (New Rule)
> [!IMPORTANT]
> **CLOSEST ZONE PRIORITIZATION RULES:**
> 1. **Prioritize Closest Zone:** When determining the structural limit entry price, the system must scan visible candles for unmitigated FVG or OB zones. If multiple zones exist, it must strictly prioritize the unmitigated zone (whether FVG or OB) that is closest to the current market price.
> 2. **Mitigation Retest Level:** The entry price should be placed at the boundary of this closest unmitigated zone (the top edge for Buy setups, or bottom edge for Sell setups) rather than forcing entries at the deepest swing extremes, preventing missed trades.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** ලිමිට් ඇණවුමක් තැබීමේදී, වත්මන් මිලට ආසන්නයෙන්ම පවතින unmitigated FVG හෝ OB සීමාව හඳුනාගෙන, ඇතුල්වීමේ මිල (Entry price) සැමවිටම එම ආසන්නතම සීමාවෙහි සැකසිය යුතුය. වෙළඳපල හැරී යාමකදී (pullback) සාමාන්‍යයෙන් ආසන්නතම Fair Value Gap (FVG) එක ස්පර්ශ කරන බැවින්, දුරින් ඇති මට්ටම් වෙනුවට ළඟම ඇති කලාපයට ප්‍රමුඛතාවය දිය යුතුය.

## 53. Strict Anti-Counter-BOS Trend Lock Protocol (New Rule)
> [!IMPORTANT]
> **ANTI-COUNTER-BOS TREND LOCK RULES:**
> 1. **No Trading Against Active BOS:** If the active timeframe structure shows a confirmed Bullish Break of Structure (BOS) sequence or Bullish CHoCH (Higher Highs and Higher Lows), all Sell / Short setups are 100% strictly forbidden and locked out (`is_valid = false`, returning `No Entry (Anti-Counter-BOS Lock)`).
> 2. **Bearish BOS Restriction:** If the active structure shows a confirmed Bearish Break of Structure (BOS) sequence or Bearish CHoCH (Lower Lows and Lower Highs), all Buy / Long setups are 100% strictly forbidden and locked out (`is_valid = false`, returning `No Entry (Anti-Counter-BOS Lock)`).
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** සක්‍රීය චාර්ට් එකෙහි Break of Structure (BOS) ප්‍රවණතාවයට පටහැනිව කිසිදු Trade එකක් නිර්දේශ කිරීම සම්පූර්ණයෙන්ම තහනම් වේ. චාර්ට් එකෙහි Bullish BOS (ඉහළට කැඩීම්) සලකුණු වන්නේ නම් Sell setups ද, Bearish BOS (පහළට කැඩීම්) සලකුණු වන්නේ නම් Buy setups ද ස්වයංක්‍රීයව අවහිර කර `No Entry (Anti-Counter-BOS Lock)` ලෙස සටහන් කළ යුතුය.

## 54. Unswept Liquidity Magnet & EQH/EQL Proximity Filter Protocol (New Rule)
> [!IMPORTANT]
> **UNSWEPT LIQUIDITY MAGNET & EQH/EQL FILTER RULES:**
> 1. **Draw on Liquidity (DOL) Magnet Protection:** The system must scan for unswept Equal Highs (EQH) or Buy-Side Liquidity pools located within 0.1% to 0.6% directly above current price. If unswept Equal Highs exist above, Short / Sell entries are strictly prohibited because the algorithm will naturally pull price upwards to sweep those highs first.
> 2. **Equal Lows (EQL) Magnet Protection:** The system must scan for unswept Equal Lows (EQL) or Sell-Side Liquidity pools located within 0.1% to 0.6% directly below current price. If unswept Equal Lows exist below, Long / Buy entries are strictly prohibited because the market will naturally sweep those lows first.
> 3. **Reversal Timing:** Reversal trade setups are ONLY permissible AFTER the respective liquidity pool (EQH or EQL) has been cleanly swept by a manipulation wick.
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** වත්මන් මිලට 0.1% - 0.6% අතර ආසන්නයෙන් ඉහළින් නොකැඩුණු Equal Highs (EQH) හෝ පහළින් Equal Lows (EQL) පවතී නම්, වෙළඳපල චුම්භකයක් මෙන් එම මට්ටම් Sweep කිරීමට ඇදී යන බැවින්, ඊට විරුද්ධව Trades ගැනීම තහනම් වේ. Reversal එකක් ගත යුත්තේ එම Highs/Lows සීමාවන් සම්පූර්ණයෙන්ම Sweep වීමෙන් පසුව පමණි.

## 55. Institutional Inducement (IDM) Retest & Order Flow Confluence Protocol (New Rule)
> [!IMPORTANT]
> **INSTITUTIONAL INDUCEMENT (IDM) RETEST RULES (MENTORFX GUIDES):**
> 1. **Inducement Trap Recognition:** In an active Bullish trend, minor red pullback candles are classified as Inducement (IDM) traps created by market makers to bait retail sellers. The system must NEVER trigger a Sell setup on an uptrend pullback.
> 2. **Mitigation Retest Execution:** The system must wait for the Inducement low to be swept, and advise a **Buy Limit (Long)** entry when price mitigates the underlying Demand Order Block / Fair Value Gap (FVG), targeting the unswept external swing high.
> 3. **Bearish Inducement Mirror:** In an active Bearish trend, minor green pullback candles are classified as Inducement traps. The system must wait for the Inducement high to be swept and advise a **Sell Limit (Short)** entry at the Supply Order Block / FVG, targeting the external swing low.
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** ඔබගේ SMC MentorFX PDF මාර්ගෝපදේශ 2 හි සඳහන් පරිදි, Uptrend එකකදී පහළට එන කුඩා Pullback යනු විකුණුම්කරුවන් කොටු කරගන්නා Inducement (IDM) උගුල් වේ. එවැනි අවස්ථාවලදී කිසිවිටෙක Sell නොකර, එම Inducement එක Sweep වී පහළ ඇති Demand Order Block / FVG එක ස්පර්ශ වූ පසු සුපිරි **Buy Limit (Long)** එන්ට්‍රියක් ලබා ගත යුතුය. Downtrend එකකදී ඊට ප්‍රතිවිරුද්ධව ක්‍රියා කළ යුතුය.

## 56. Equal Extremes (EQH / EQL) Liquidity Target Protocol (New Rule)
> [!IMPORTANT]
> **EQUAL EXTREMES LIQUIDITY TARGET RULES:**
> 1. **Equal Highs as Targets Only:** When Equal Highs (EQH - 2 or more wicks at the same horizontal price level) are detected, they must strictly be used as the **Take Profit Target for Buy / Long setups**. Entering Short / Sell setups at Equal Highs is 100% strictly forbidden because institutional market makers intentionally hunt and sweep Equal Highs.
> 2. **Equal Lows as Targets Only:** When Equal Lows (EQL - 2 or more wicks at the same horizontal price level) are detected, they must strictly be used as the **Take Profit Target for Sell / Short setups**. Entering Long / Buy setups at Equal Lows is 100% strictly forbidden.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** චාර්ට් එකෙහි එකම මට්ටමේ Wicks කිහිපයක් සහිත Equal Highs (EQH) හෝ Equal Lows (EQL) පවතින විට, ඒවා සැමවිටම භාවිතා කළ යුත්තේ **Take Profit ඉලක්කයන් (TP Targets)** ලෙස පමණි. Equal Highs අසලදී කිසිවිටෙක Sell නොකළ යුතු අතර, Equal Lows අසලදී කිසිවිටෙක Buy නොකළ යුතුය.

## 57. Post-Sweep V-Shape Expansion & Directional Lock Protocol (New Rule)
> [!IMPORTANT]
> **POST-SWEEP V-SHAPE EXPANSION RULES:**
> 1. **Directional Expansion Lock:** When price sweeps a major session extreme (session low/high) and forms an aggressive V-shaped displacement candle with a confirmed CHoCH, the market is in an **Institutional Expansion Leg**.
> 2. **Anti-Reversal Lockout:** During this post-sweep expansion phase, all counter-trend setups in the opposing direction are strictly locked out (`is_valid = false`, returning `No Entry (Post-Sweep Expansion Lock)`).
> 3. **Expansion Trend Following:** The system must strictly wait for a pullback to the nearest unmitigated Order Block / FVG and advise entries strictly aligned with the expansion direction (Buying dips after low sweep, Selling rallies after high sweep).
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** මිල ප්‍රධාන Session Lows (පහළ සීමාවන්) Sweep කර Bullish CHoCH එකක් දුන් පසු, වෙළඳපල ක්ෂණිකව ඉහළට Expansion (Pump) වන බැවින්, Sell Trade ගැනීම සම්පූර්ණයෙන්ම තහනම් වේ. එවිට කළ යුත්තේ පහළට එන Pullback එකකදී Demand Order Block එකෙන් **Buy Limit** එකක් ගෙන ඉහළට යන expansion එකෙන් ලාභ ගැනීමයි.

## 58. Higher Low (HL) / Lower High (LH) Structural Validation & Strict 1:2, 1:3, 1:4 RR Allocation Protocol (New Rule)
> [!IMPORTANT]
> **HL/LH VALIDATION & STRICT 1:2, 1:3, 1:4 RR RULES:**
> 1. **Higher Low Uptrend Confirmation:** In a Bullish trend, pullbacks that hold above the previous swing low are validated as **Higher Lows (HL)**. Entries must be placed at the Demand Order Block / FVG with the Stop Loss placed safely 0.1% below that Higher Low.
> 2. **Lower High Downtrend Confirmation:** In a Bearish trend, pullbacks that hold below the previous swing high are validated as **Lower Highs (LH)**. Entries must be placed at the Supply Order Block / FVG with the Stop Loss placed safely 0.1% above that Lower High.
> 3. **Strict 1:2, 1:3, 1:4 Take Profit Ratio Allocation:** All setups must strictly allocate dynamic Take Profit targets according to the institutional 3-tier boundary:
>    - **TP1 (Conservative / Partial Take Profit):** Exactly **1:2.0 Risk-to-Reward (RR)**.
>    - **TP2 (Primary Target / Structural Target):** Exactly **1:3.0 Risk-to-Reward (RR)**.
>    - **TP3 (Extended Runner / Liquidity Sweep):** Exactly **1:4.0 Risk-to-Reward (RR)**.
>    - Targets beyond 1:4.0 RR (such as 1:5.0) are strictly prohibited for 10–15 minute high-velocity scalping.
>    - **TP Target Lock (Strict):** Under no circumstances should the system calculate or output TP targets of 1:5.0+ RR. Every valid setup must strictly output TP1 at 1:2.0 RR, TP2 at 1:3.0 RR, and TP3 at 1:4.0 RR.
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** Uptrend එකකදී පෙර Low එකට වඩා ඉහළින් හැදෙන Higher Lows (HL) මඟින්ද, Downtrend එකකදී පෙර High එකට වඩා පහළින් හැදෙන Lower Highs (LH) මඟින්ද සුපිරි තහවුරු කිරීමක් ලබා දෙයි. Take Profit ඉලක්ක දැඩිව **1:2.0 (TP1), 1:3.0 (TP2), සහ 1:4.0 (TP3)** ලෙස පමණක් ගණනය කළ යුතු අතර, විනාඩි 10-15 Scalping සඳහා 1:5 හෝ ඊට වැඩි ඈත ඉලක්ක තැබීම තහනම් වේ.

## 59. Active Demand / Supply Order Block Proximity Lock Protocol (New Rule)
> [!IMPORTANT]
> **DEMAND / SUPPLY PROXIMITY LOCK RULES:**
> 1. **Demand Zone Anti-Sell Lock:** If price has mitigated or bounced off an unmitigated **Demand Order Block (Blue Zone)** within the last 20 candles, all Sell / Short setups are 100% strictly forbidden and locked out (`is_valid = false`, returning `No Entry (Demand Zone Active - Buy Only)`).
> 2. **Supply Zone Anti-Buy Lock:** If price has mitigated or bounced off an unmitigated **Supply Order Block (Red Zone)** within the last 20 candles, all Buy / Long setups are 100% strictly forbidden and locked out (`is_valid = false`, returning `No Entry (Supply Zone Active - Sell Only)`).
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** මිල මෑතකදී නිල් පැහැති Demand Order Block එකක වැදී (bounce වී) ඉහළට ගමන් කරන්නේ නම්, Sell Trade ගැනීම 100% ක් තහනම් වේ (`No Entry (Demand Zone Active - Buy Only)`). මිල රතු පැහැති Supply Order Block එකක වැදී පහළට ගමන් කරන්නේ නම්, Buy Trade ගැනීම 100% ක් තහනම් වේ.

## 60. Consecutive Higher Lows (HL) / Lower Highs (LH) Trend Lockout Protocol (New Rule)
> [!IMPORTANT]
> **CONSECUTIVE HL/LH TREND LOCKOUT RULES:**
> 1. **3-Consecutive Higher Lows Lock:** If 3 or more consecutive Higher Lows are detected in the active timeframe lookback (e.g. Low 1 < Low 2 < Low 3), the market is in an undeniable **Institutional Markup Phase**. All Sell setups must be auto-suppressed and locked out (`is_valid = false`, returning `No Entry (Consecutive Higher Lows - Buy Only)`).
> 2. **3-Consecutive Lower Highs Lock:** If 3 or more consecutive Lower Highs are detected in the lookback (e.g. High 1 > High 2 > High 3), the market is in an undeniable **Institutional Markdown Phase**. All Buy setups must be auto-suppressed and locked out (`is_valid = false`, returning `No Entry (Consecutive Lower Highs - Sell Only)`).
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** චාර්ට් එකෙහි එක දිගට Higher Lows 3ක් හෝ ඊට වැඩි ගණනක් පඩිපෙළක් මෙන් ඉහළට සෑදෙන්නේ නම්, මාකට් එකේ Top එක අල්ලන්න ගොස් Sell කිරීම සම්පූර්ණයෙන්ම තහනම් වේ. එවිට ලබා දෙන්නේ Buy Trade පමණි.

## 61. Pre-Expansion Base Compression Breakout Protocol (New Rule)
> [!IMPORTANT]
> **PRE-EXPANSION BASE COMPRESSION RULES:**
> 1. **Accumulation Base Recognition:** When price moves sideways in a tight range for 15+ candles directly sitting above a Demand Zone or below a Supply Zone, the algorithm classifies this as **Pre-Expansion Base Compression (PO3 Accumulation)**.
> 2. **Base Limit Execution:** The system must place the Limit Order directly at the base support (for Buys) or base resistance (for Sells) with Stop Loss placed safely 0.1% beyond the base extreme, capturing the explosive 1:2, 1:3, and 1:4 RR expansion wave.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** Demand Zone එකක් උඩ මිල කැන්ඩල් 15කට වඩා එකම සීමාවක පැත්තට ගමන් කරන්නේ නම් (Consolidation), එය දැවැන්ත පිපිරීමකට (Explosion) පෙර සිදුවන Accumulation එකක් බැවින්, ඊට විරුද්ධව Sell නොකර එහි Support මට්ටමෙන් සුපිරි **Buy Limit** එකක් ලබා දෙයි.

## 62. Institutional Sniper Entry & Mitigation Front-Run Buffer Protocol (New Rule)
> [!IMPORTANT]
> **SNIPER ENTRY & MITIGATION FRONT-RUN BUFFER RULES:**
> 1. **Zone Outer Edge Alignment:** The calculated Limit Entry price must strictly target the outer mitigation boundary or the 50% Consequent Encroachment (Mean Threshold) of the key Fair Value Gap (FVG) or Order Block (OB).
> 2. **0.04% Proximity Spread Buffer (Guaranteed Touch):** To guarantee that the price physically touches and fills the pending Limit Order before reversing away (eliminating the issue of missing entries by a fraction of a pip due to front-running and spread), the recommended Limit Entry price must incorporate a **0.04% proximity spread buffer**:
>    - **Buy Limit Entry:** Placed at `target_boundary * 1.0004` (shifted 0.04% closer to current price).
>    - **Sell Limit Entry:** Placed at `target_boundary * 0.9996` (shifted 0.04% closer to current price).
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** Limit Order එකක් දමන විට, මිල හරියටම එම Entry Point එක touch කර (ස්පර්ශ කර) ආපසු හැරී යන බව සහතික කිරීම සඳහා, 0.04% ක Proximity Spread Buffer එකක් ඇතුළත් කළ යුතුය (Buy Limit එක 0.04% ක් ඉහළටද, Sell Limit එක 0.04% ක් පහළටද තබා Entry එක miss වීම 100% ක්ම වළක්වයි).

## 63. LuxAlgo Strong Low / Weak High Directional Lock Protocol (New Rule)
> [!IMPORTANT]
> **STRONG LOW / WEAK HIGH DIRECTIONAL LOCK RULES:**
> 1. **Strong Low Directional Lock:** When LuxAlgo prints or confirms a **`Strong Low`** in the active timeframe lookback, the market bias is **HARD-LOCKED TO BUY (LONG) ONLY**. All Sell / Short setups are 100% strictly forbidden and locked out (`is_valid = false`, returning `No Entry (Strong Low Active - Buy Only)`).
> 2. **Weak High as Take Profit Target Only:** In an active Uptrend, a **`weak High`** is an institutional liquidity magnet designed to be swept and broken. The system must STRICTLY use the Weak High as the **Take Profit target for Buy setups**, and is 100% strictly prohibited from using the Weak High as an area to enter a Short or place a Stop Loss.
> 3. **Strong High Directional Lock:** When LuxAlgo confirms a **`Strong High`**, the market bias is **HARD-LOCKED TO SELL (SHORT) ONLY**. All Buy setups are 100% strictly forbidden and locked out. The Take Profit must target the **`Weak Low`**.
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):** LuxAlgo Indicator එකෙහි **`Strong Low`** එකක් සලකුණු වී ඇති විට, මාකට් එක උඩට යන බව ආයතනිකව තහවුරු වී ඇති බැවින්, Sell Trade ගැනීම 100% ක් තහනම් වේ. එවිට **`weak High`** (දුර්වල High) එක භාවිතා කළ යුත්තේ **Buy Trade එකක Take Profit Target එකක් ලෙස පමණි**. කිසිවිටෙක Weak High එකක් මත Stop Loss තබා Sell නොකළ යුතුය.

## 64. Active Demand Zone Anti-Short Hard-Lock (New Rule)
> [!IMPORTANT]
> **DEMAND ZONE ANTI-SHORT HARD-LOCK RULES:**
> 1. **Blue Demand Box Defense:** If price has touched, wicked into, or bounced off an active **Demand Zone (Blue Box)** within the last 30 candles, **SHORTING IS 100% FORBIDDEN IN THE SYSTEM**.
> 2. **Buy-From-Demand Exclusivity:** When price is at or near Demand, the system exclusively calculates **Buy Limit (Long)** entries at the Demand boundary, placing Stop Loss safely below the Strong Low.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** මිල නිල් පැහැති Demand Zone එකක් උඩ තිබෙන විට හෝ එහි වැදී bounce වී ඇති විට, ආයතනික ගැනුම්කරුවන් වෙළඳපල මිලදී ගන්නා බැවින්, **Sell Trade ලබා දීම පද්ධතියෙන් 100% ක්ම Hard-Lock කර තහනම් කර ඇත**. එවිට ලැබෙන්නේ Demand එකෙන් ඉහළට යන Buy Limit පමණි.

## 65. Absolute Ban on "Picking the Top" (Anti-Counter-Expansion Protocol) (New Rule)
> [!IMPORTANT]
> **ABSOLUTE BAN ON PICKING TOPS RULES:**
> 1. **No Counter-Trend Predictions:** The AI and backend engine are **STRICTLY PROHIBITED from predicting a market top or shorting an active Bullish BOS sequence**.
> 2. **Mandatory Bearish CHoCH Requirement:** A Bearish Reversal setup is ONLY permissible IF AND ONLY IF price sweeps the external high, breaks and closes below the last Higher Low with a confirmed **Bearish CHoCH displacement candle body**, AND prints a fresh **Supply Zone (Red Box)**. Without this verified structural shift, Shorting is 100% blocked.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):** මාකට් එක එක දිගට උඩට යද්දී 'Top එක අල්ලන්න' සිතා Sell දැමීම පද්ධතියෙන් සම්පූර්ණයෙන්ම තහනම් කර ඇත. Reversal Sell Trade එකක් ලබා දිය හැක්කේ, මිල ඉහළට ගොස් පෙර Higher Low එක කඩාගෙන පහළට ගොස් **Bearish CHoCH එකක් සහ රතු Supply Zone එකක් නිර්මාණය කළහොත් පමණි**.

## 67. Master Major/Minor Structure, BPR (Balanced Price Range) & HTF-to-LTF 5-Step Execution Protocol (New Rule)
> [!IMPORTANT]
> **MASTER MAJOR/MINOR STRUCTURE, BPR & 5-STEP EXECUTION RULES:**
> 1. **Major vs. Minor Structure Identification:**
>    - **Major Structure:** Represents the primary macro highway (Higher Highs & Higher Lows for Uptrend; Lower Highs & Lower Lows for Downtrend).
>    - **Minor Structure:** Internal corrective waves/pullbacks within the major trend leg.
>    - **Avoid Minor Trap:** Never mistake a Minor CHoCH for a full trend reversal. A valid macro reversal strictly requires breaking the **Major Swing Low/High with a Thick Candle Body Close**.
> 2. **BPR (Balanced Price Range) & High-Accuracy V/A Formations:**
>    - **Definition:** Formed when an FVG created in one direction is immediately overlapped and covered by an opposite FVG in the reverse direction.
>    - **High Probability Shapes:** Bullish BPR formed in an aggressive **'V' Shape** and Bearish BPR formed in an **'A' Shape** possess the highest statistical accuracy. The system prioritizes entries mitigating these BPR zones.
> 3. **5-Step HTF-to-LTF Alignment Execution Model (1H paired with 5m/1m):**
>    - **Step 1 (HTF Structure):** Identify 1-Hour (1H) Market Structure (Bullish or Bearish).
>    - **Step 2 (HTF Zone):** Mark the active 1-Hour Fair Value Gap (HTF FVG) or Key POI.
>    - **Step 3 (Zone Tap & Timeframe Shift):** When price reaches and mitigates the 1H FVG, switch to the Lower Timeframe (5-Minute or 1-Minute).
>    - **Step 4 (LTF CHoCH Confirmation):** Wait for a confirmed **LTF CHoCH (Change of Character)** where the last Higher Low / Lower High is broken by a **Thick Candle Body Close** (not a mere wick).
>    - **Step 5 (Sniper Limit Entry):** Take the Limit Entry directly at the newly formed **LTF FVG / BPR boundary** (with Rule 62 0.04% proximity buffer).
> 4. **Execution Parameters:**
>    - **Stop Loss:** Placed safely beyond the entry swing extreme with the 0.10% safety buffer.
>    - **Take Profit:** Target the nearest local Major High/Low or dynamic **1:2.0 (TP1), 1:3.0 (TP2), and 1:4.0 (TP3) RR** ratios.
> 5. **Bilingual Requirement (සිංහල පරිවර්තනය):**
>    - **1. Major සහ Minor Structure:** Major Structure යනු ප්‍රධාන ගමන් මාර්ගයයි (HH/HL හෝ LH/LL). Minor Structure යනු ඒ තුළ සිදුවන කුඩා තරංග (Waves/Pullbacks) වේ. Minor CHoCH එකක් දැක සම්පූර්ණ Trend එක හැරුණා යැයි නොසිතිය යුතුය. සැබෑ Reversal එකකට Major Low/High එක Thick Body Candle එකකින් බිඳිය යුතුය.
>    - **2. BPR (Balanced Price Range):** එක් පැත්තකට හැදුණු FVG එකක් ඊට විරුද්ධ පැත්තට හැදෙන FVG එකකින් ආවරණය වීම BPR එකකි. 'V' Shape හෝ 'A' Shape BPR වල නිරවද්‍යතාවය (Accuracy) උපරිම වේ.
>    - **3. පියවර 5ක Entry ක්‍රියාවලිය (1H සමඟ 5m/1m):**
>      * පියවර 1: 1-Hour Chart එකෙන් ප්‍රධාන Market Structure (Bullish/Bearish) හඳුනාගන්න.
>      * පියවර 2: 1-Hour FVG / Key Zone එක Mark කරගන්න.
>      * පියවර 3: මිල 1H FVG එකට පැමිණි පසු 5-Minute / 1-Minute චාර්ට් එකට මාරු වන්න.
>      * පියවර 4: කුඩා Timeframe එකේ අවසන් Low/High එක Thick Candle Body එකකින් කඩාගෙන යන **CHoCH එකක්** හැදෙන තුරු සිටින්න.
>      * පියවර 5: CHoCH එකෙන් පසු හැදෙන **LTF FVG / BPR එකෙන් 0.04% Buffer එක සහිතව Limit Entry එක ලබා ගන්න**.
>      * Stop Loss: Swing Extreme එකට එපිටින් 0.1% buffer එක සහිතව.
>      * Target: ළඟම Major High/Low හෝ 1:2, 1:3, 1:4 RR ඉලක්ක.

## 68. Stale Setup Auto-Expiry (15m Max Limit) & Macro Crash Lockout Protocol (New Rule)
> [!IMPORTANT]
> **STALE SETUP EXPIRY & MACRO CRASH LOCKOUT RULES:**
> 1. **15-Minute Strict Setup Expiration:** All 1-minute scalping trade setups are strictly valid for a maximum window of **15 minutes** from generation time. If the pending limit order is not touched and filled within 15 minutes, the setup is deemed **STALE & EXPIRED**. The trader must immediately cancel the pending limit order on Binance to avoid entering an expired setup under altered market conditions.
> 2. **Macro Crash Anti-Long Hard-Lock:** If the Higher Timeframe (15m / 1H) is in an active crash / downtrend sequence (making consecutive Lower Highs and Lower Lows), all Buy (Long) scalp setups are **100% HARD-BLOCKED**, even if minor 1m green rejection wicks appear. The system exclusively issues **Sell (Short) Limit orders** at the Lower High Breakaway FVGs until an institutional 1H Demand zone with Thick Body Bullish CHoCH is verified.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):**
>    - **1. විනාඩි 15න් Setup එක කල් ඉකුත් වීම (Auto-Expiry):** දෙන සෑම 1-Minute Scalp Setup එකක්ම වලංගු වන්නේ විනාඩි 15ක උපරිම කාලයකට පමණි. විනාඩි 15ක් ඇතුළත Order එක Fill නොවුණහොත්, එම Trade එක කල් ඉකුත් වූ (Stale) එකක් බැවින් වහාම Binance එකෙන් Cancel කළ යුතුය. පැයකට පසු පැරණි Setup වලට Trade දැමීමෙන් වළකින්න.
>    - **2. Downtrend Crash වලදී Buy සම්පූර්ණයෙන්ම තහනම් කිරීම:** 15m හෝ 1H Chart එක එක දිගට පහළට කඩා වැටෙන විට (Downtrend), කුඩා 1-Minute කොළ ඉටිපන්දම් වලට Buy ගැනීම 100% ක් තහනම් කර ඇත. එවැනි අවස්ථාවලදී පද්ධතිය ලබා දෙන්නේ **පහළට බහින Trend එක දිගේ යන Sell (Short) Limit පමණි**.

## 69. Bidirectional Macro Trend Lockout & 5-15 Minute Fast Fill Execution Protocol (New Rule)
> [!IMPORTANT]
> **BIDIRECTIONAL TREND LOCKOUT & 5-15 MINUTE FAST FILL RULES:**
> 1. **Bidirectional Trend Anti-Counter Lock:**
>    - **In Macro Uptrend (15m/1H making Higher Highs / Higher Lows):** All Sell (Short) setups are **100% HARD-BLOCKED**. The system exclusively calculates **Buy Limit (Long)** entries off Demand / Higher Low FVGs.
>    - **In Macro Downtrend (15m/1H making Lower Highs / Lower Lows):** All Buy (Long) setups are **100% HARD-BLOCKED**. The system exclusively calculates **Sell Limit (Short)** entries off Supply / Lower High FVGs.
> 2. **Guaranteed 5 to 15-Minute Fast Entry Fill:**
>    - The calculated Limit Entry price must strictly target the **Closest Unmitigated 1m Breakaway FVG / Order Block boundary** located within **0.08% to 0.20%** of current market price (incorporating the 0.04% Rule 62 buffer).
>    - This guarantees that orders are physically touched and filled within **5 to 8 minutes (max 10-15 minutes)**, completely eliminating long multi-hour waiting periods.
> 3. **Ultra-Tight Stop Loss & Strict RR Targets:**
## 70. The Falcon Golden Sniper Model (The Perfect Ethereum Master Blueprint) (New Rule)
> [!IMPORTANT]
> **THE GOLDEN SNIPER ENTRY BLUEPRINT (THE ETHEREUM 10:23 MASTER PATTERN):**
> 1. **The 4-Step Golden Sequence:**
>    - **Step 1 (Base Defense):** Price taps a verified **Blue Demand Box** and establishes an institutional **Strong Low**.
>    - **Step 2 (Displacement Shift):** A strong green expansion candle prints a **Bullish CHoCH** breaking the last Lower High with a **Thick Candle Body Close**.
>    - **Step 3 (Breakaway FVG Entry):** The Limit Entry is calculated at the top boundary of the newly formed **1-Minute Breakaway FVG** with the **0.04% Rule 62 proximity buffer** (guaranteeing fill within 5-15 mins).
>    - **Step 4 (Stop Loss & Target Alignment):** Stop Loss is placed strictly **0.10% below the Blue Demand Box / Strong Low** (`min(low, demand_box) * 0.9990`), and Take Profit is placed directly at the **Weak High** / local Equal Highs (delivering strict 1:2.0, 1:3.0, 1:4.0 RR with zero drawdown).
> 2. **Bearish Mirror Model:**
>    - Price taps a Red Supply Box establishing a **Strong High** -> Thick Body Bearish CHoCH -> Sell Limit at 1m Breakaway FVG (with 0.04% buffer) -> SL 0.10% above Supply Box -> TP at the **Weak Low** (1:3.0 RR).
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):**
>    - **පරිපූර්ණ රන් ආදර්ශය (The Golden Sniper Template):** මෙම Ethereum (ETH) Chart එකෙහි සිදුවූ ආකාරයට:
>      1. මිල නිල් පැහැති Demand Zone එකේ වැදී **Strong Low** එක තහවුරු කරයි.
>      2. Thick Candle Body එකකින් **Bullish CHoCH** එකක් සාදයි.
>      3. CHoCH එකෙන් පසු හැදෙන **1m Breakaway FVG එකෙන් 0.04% Buffer එක සහිතව Limit Entry එක ලබා දෙයි** (විනාඩි 5-15 න් Fill වේ).
>      4. Stop Loss එක Demand Box එකට එපිටින් **0.10% Buffer එක සහිතව තබන අතර, Take Profit එක කෙළින්ම Weak High එක ඉලක්ක කරයි**.
>      5. මෙම ආකෘතිය (Model) පද්ධතියේ ප්‍රමුඛතම ස්ථිර Entry Blueprint එක ලෙස සදාකාලිකව ක්‍රියාත්මක වේ!

## 71. Selected Execution Timeframe Precision Anchor Protocol (New Rule)
> [!IMPORTANT]
> **SELECTED EXECUTION TIMEFRAME ANCHOR RULES:**
> 1. **Timeframe Selection as the Final Anchor:**
>    - Whichever timeframe is selected in the **"EXECUTION TIMEFRAME"** dropdown (e.g., `1m`, `3m`, `5m`, `15m`), that timeframe serves as the **Exclusive Final Entry Execution Anchor**.
>    - Even if Higher Timeframes (1H / 15m / 5m) are referenced for Macro Bias and Key POIs, the final **Liquidity Sweep, Displacement CHoCH, Breakaway FVG / BPR, Limit Entry price, Stop Loss, and Take Profit MUST BE CAUGHT AND EXECUTED STRICTLY ON THE CANDLES OF THE SELECTED TIMEFRAME** (e.g., 1-Minute candles when `1m (Scalp Entry)` is selected).
> 2. **No Timeframe Mixing in Final Entry:**
>    - When `1m (Scalp Entry)` is selected, the engine must NEVER wait for a 15m candle close or 5m FVG to enter; it must immediately trigger off the active **1-minute Breakaway FVG** with the 0.04% buffer for ultra-fast 5-15 minute execution.
>    - When `15m (Primary Structure)` is selected, the entry is anchored strictly to the 15-minute FVG/OB.
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):**
>    - **තෝරාගත් Timeframe එක මත පමණක් Entry එක ගැනීම:** ඔබ Dropdown එකෙන් තෝරන Timeframe එක කුමක්ද (උදා: `1m (Scalp Entry)` නම්):
>      - 1H සහ 15m මඟින් Macro Bias එක සහ Key POIs බැලුවද, **අවසාන Trade Entry එක, CHoCH එක, Breakaway FVG එක, Stop Loss එක සහ Take Profit එක ගණනය කර catch කරගත යුත්තේ ඔබ තේරූ 1-Minute Timeframe එකේ Candles වලින් පමණි!**
>      - 1-Minute තෝරා ඇති විට 5m හෝ 15m Candle Closes එනතුරු බලා නොසිට, **1-Minute Chart එකේ හැදෙන ආසන්නතම 1m FVG එකෙන්ම 0.04% Buffer එක සහිතව Entry එක ලබා දිය යුතුය**.

## 72. Structural Confirmation Target & Minimum 1:2.0 RR Hard-Filter Protocol (New Rule)
> [!IMPORTANT]
> **DYNAMIC STRUCTURAL CONFIRMATION TARGET & 1:2.0 MINIMUM RR RULES:**
> 1. **No Blind/Fixed 1:4.0 RR Forcing:**
>    - The system must never force a rigid, arbitrary 1:4.0 RR target onto a market structure if the natural liquidity or opposing Point of Interest (POI) terminates earlier.
>    - The Take Profit must be dynamically set **strictly at the confirmed structural terminus** (the Weak High / Equal Highs / Supply Zone for Buys; the Weak Low / Equal Lows / Demand Zone for Sells).
> 2. **Minimum 1:2.0 RR Hard Lockout Filter:**
>    - Before approving any trade setup, the engine must measure the exact distance between the Entry Price and the confirmed Structural Target against the Stop Loss risk:
>      - **If Confirmed Reward / Risk < 1:2.0:** The setup is **100% HARD-BLOCKED and LOCKED OUT** (`is_valid = false`, `No Entry (Confirmed RR < 1:2.0)`). It is strictly forbidden to enter low-reward trades with insufficient runway.
>      - **If Confirmed Reward / Risk >= 1:2.0:** The trade is approved, and the primary Take Profit target is set **EXACTLY at that confirmed structural level** (e.g. 1:2.20 RR, 1:2.80 RR, 1:3.40 RR).
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):**
>    - **තහවුරු වූ Structural Target එක සහ අවම 1:2.0 RR නීතිය:**
>      - කිසිවිටෙක අන්ධ ලෙස 1:4.0 RR බලෙන් නොතබා, **මිල ගමන් කිරීමට තහවුරු වූ සැබෑ ආයතනික ඉලක්කය (Weak High / Equal Highs / Opposing POI) වෙත Take Profit එක තැබිය යුතුය**.
>      - එම තහවුරු වූ ඉලක්කයට ඇති දුර **1:2.0 RR අනුපාතයට වඩා අඩු නම්, එම Trade එක 100% ක්ම Lockout කර අවලංගු කළ යුතුය (`No Entry (Confirmed RR < 1:2.0)`)**.
>      - තහවුරු වූ දුර **1:2.0 RR හෝ ඊට වැඩි නම් පමණක් Trade එක ලබා දිය යුතුය**.

## 73. Strict Falcon Rule Integrity & Non-Bypass Absolute Enforcement Protocol (New Master Rule)
> [!IMPORTANT]
> **MASTER NON-BYPASS MANDATE & CONSTITUTIONAL INTEGRITY RULES:**
> 1. **Zero-Bypass Principle:**
>    - Under NO circumstances may the AI engine, programmatic scanners, or background trackers bypass, bend, or ignore any of the 72 Falcon Rules.
>    - If even a single condition fails (e.g., Bearish CHoCH active under Rule 13/58, missing 0.10% SL buffer under Rule 25/69, confirmed RR < 1:2.0 under Rule 72, or Resistance/Support trap under Rule 12/56), the setup MUST be immediately suppressed with `is_valid = false` and returned as `No Entry`.
> 2. **Timeframe Precedence Hard-Lock:**
>    - Macro Market Structure (15m/1H) ALWAYS overrides LTF (1m/3m) noise. A 1m bounce during a 15m/1H Downtrend is STRICTLY treated as a Lower High Pullback to Sell, never a Buy setup.
> 3. **Mathematical Verification Supremacy:**
>    - The system must never rely on AI imagination or arbitrary numbers. All Entry, SL (0.10% buffer past Demand/Supply box), and Take Profit (confirmed structural target) levels must be mathematically verified in Python before reaching the frontend.
> 4. **Bilingual Requirement (සිංහල පරිවර්තනය):**
>    - **නීති කඩකිරීම් හෝ මඟහැරීම් 100% ක්ම තහනම් කිරීමේ ප්‍රධාන ප්‍රඥප්තිය:**
>      - කිසිදු හේතුවක් මත හෝ තත්ත්වයක් යටතේ නීති 1 සිට 72 දක්වා වූ කිසිදු නීතියක් මඟහැර (bypass) කිසිදු Trade Setup එකක් ලබා දීම 100% ක්ම තහනම් වේ.
>      - එක් නීතියක් හෝ අසාර්ථක වුවහොත් (උදා: Bearish CHoCH එකක් තිබියදී Buy සෙවීම, SL Buffer එක නොමැති වීම, RR < 1:2.0 වීම), එම Setup එක වහාම අවලංගු කර `No Entry` ලෙස ලබා දිය යුතුය.
>      - 15m සහ 1H Macro Trend එක 1-Minute Micro Noise එකට වඩා ඉහළින් ක්‍රියාත්මක වන අතර, සියලුම Entry, SL, සහ TP අගයන් Python ගණිත සමීකරණ මඟින් තහවුරු විය යුතුය.

## 74. Major Demand Base Sweep & PO3 Instant Reversal Protocol (New Master Rule)
> [!IMPORTANT]
> **MAJOR DEMAND/SUPPLY BASE SWEEP & PO3 REVERSAL RULES:**
> 1. **Demand Base / Double Bottom Liquidity Sweep Detection:**
>    - When price sweeps or tests the Major Session Lows / Double Bottom (within 0.15% of the 200-candle absolute low) and immediately prints a 1-minute Bullish CHoCH with strong green displacement:
>      - The old Bearish Macro trend is **IMMEDIATELY OVERRIDDEN AND TERMINATED**.
>      - The execution bias instantly switches to **BULLISH (Buy Limit at the 1m Demand FVG)** to catch the PO3 Distribution expansion.
>      - Stop Loss is placed strictly below the Double Bottom low with the 0.10% safe buffer (Rule 25 & 69).
>      - Take Profit is targeted directly at the upper Equal Highs / Weak Highs for a minimum 1:2.0 to 1:4.0 RR winner.
> 2. **Supply Base / Double Top Liquidity Sweep Detection:**
>    - When price sweeps or tests the Major Session Highs / Double Top (within 0.15% of the 200-candle absolute high) and immediately prints a 1-minute Bearish CHoCH with strong red displacement:
>      - The old Bullish Macro trend is **IMMEDIATELY OVERRIDDEN AND TERMINATED**.
>      - The execution bias instantly switches to **BEARISH (Sell Limit at the 1m Supply FVG)** to catch the PO3 Distribution downward expansion.
>      - Stop Loss is placed strictly above the Double Top high with the 0.10% safe buffer (Rule 25 & 69).
> 3. **Bilingual Requirement (සිංහල පරිවර්තනය):**
>    - **ප්‍රධාන Demand Base Sweep සහ PO3 Reversal නීතිය:**
>      - මිල ප්‍රධාන Session Lows / Double Bottom එකක් (පසුගිය ඉටිපන්දම් 200 ක අවම සීමාව) Sweep කර, 1-Minute Chart එකෙහි Bullish CHoCH කොළ ඉටිපන්දමක් සෑදූ සැනින්:
>        - පරණ Macro Bearish Trend එක ක්ෂණිකව අවලංගු වී, **Direction එක 'BULLISH' ලෙස මාරු විය යුතුය!**
>        - පද්ධතිය Sell දීම සම්පූර්ණයෙන්ම නවතා, **1m Demand FVG එකෙන් Buy Limit එක ලබා දී ඉහළ Equal Highs වෙත Take Profit එක ලබා දිය යුතුය**.
## 75. Adaptive Scalp SL & Fresh Displacement Anchor Architecture (New Master Rule)
> [!IMPORTANT]
> **ADAPTIVE SCALP SL & FRESH DISPLACEMENT ANCHOR RULES:**
> 1. **Displacement Origin Anchoring:**
>    - Stop Loss for 1m/3m scalping setups must NEVER be placed at distant 60-candle peaks that inflate risk beyond 0.35%.
>    - Instead, anchor SL strictly outside the fresh 15-candle displacement origin / manipulation sweep wick with a 0.10% safe buffer.
> 2. **0.25% Tight Scalp Risk Cap:**
>    - Total SL risk distance is capped between 0.18% and 0.28% of the entry price.
>    - This guarantees Take Profit 1:2.0 to 1:4.0 targets require only a 0.40% to 0.75% price move, enabling trades to complete within 10 to 25 minutes.
> 3. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - **Adaptive Scalp SL සහ Fresh Displacement Anchor නීතිය:**
>      - 1-Minute Scalping සඳහා Stop Loss එක ඈත ඉටිපන්දම් 60 කඳු මුදුන් වල නොතබා, FVG සහ Displacement හැදුණු ආසන්නතම ඉටිපන්දම් 15 ක Fresh Manipulation Wick එකට යන්තම් 0.10% ක් එපිටින් 0.18% - 0.25% ක Tight Risk Cap එකකින් තැබිය යුතුය. එවිට Judas Wick වලින් SL කැපීම වැළකී, විනාඩි 10-25 කින් 1:3 RR TP එකට පහසුවෙන් ළඟා විය හැක.

## 76. 15M Institutional BOS Continuation & Trend Momentum Mandate (New Master Rule)
> [!IMPORTANT]
> **15M INSTITUTIONAL BOS CONTINUATION & TREND MOMENTUM RULES:**
> 1. **15M BOS Continuation Requirement:**
>    - Trade setups must align with the active 15M Break of Structure (BOS).
>    - If 15M confirmed Bullish BOS (breaking prior 15m swing highs), only Buy Limits at 1m Demand FVGs are permitted. Selling is 100% hard-blocked (Rule 53 Anti-Counter-BOS Lock).
>    - If 15M confirmed Bearish BOS (breaking prior 15m swing lows), only Sell Limits at 1m Supply FVGs are permitted. Buying is 100% hard-blocked (Rule 53 Anti-Counter-BOS Lock).
> 2. **Anti-Micro-CHoCH Trap Filter:**
>    - Minor 1m/5m pullbacks or counter-wicks must never be mistaken for macro reversals without confirmed 15M BOS/CHoCH.
> 3. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - **15-Minute සැබෑ BOS Continuation සහ Trend Momentum නීතිය:**
>      - 1m/5m බොරු CHoCH හෝ කුඩා Pullback වලට නොරැවටී, 15-Minute චාර්ට් එකෙහි සැබෑ BOS (Break of Structure) එකක් සාදා ඇති දිශාවට පමණක් Trades ලබා දිය යුතුය.
>      - 15m Bullish BOS එකක් පවතින විට Sell කිරීම 100% ක්ම තහනම් වන අතර, 15m Bearish BOS එකක් පවතින විට Buy කිරීම 100% ක්ම තහනම් වේ.

## 77. Dynamic +1.0R Break-Even Position Protection Protocol (New Master Rule)
> [!IMPORTANT]
> **DYNAMIC +1.0R BREAK-EVEN POSITION PROTECTION RULES:**
> 1. **Zero-Risk Lockout at +1.0R:**
>    - When price moves in favor of the active position and reaches the +1.0R target level (equal to 1x the initial SL risk distance), the system mandates immediately shifting the Stop Loss to the Entry Price (Break-Even).
>    - This fully protects the user against downside risk and sudden market reversals.
> 2. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - **+1.0R Break-Even Position Protection නීතිය:**
>      - මිල ගනුදෙනුවේ වාසියට ගමන් කර +1.0R ලාභ මට්ටමට ළඟා වූ වහාම, Stop Loss එක Entry Price වෙත ගෙනැවිත් (Break-Even) වෙළඳාම 100% ක්ම අවදානම් රහිත (Zero-Risk) බවට පත් කළ යුතුය.

## 78. 3-State Multi-Timeframe Machine Architecture (1H Direction Hard-Lock → 15M POI Wait → 5M Sweep/MSS Trigger) (New Master Rule)
> [!IMPORTANT]
> **3-STATE MULTI-TIMEFRAME MACHINE ARCHITECTURE RULES:**
> 1. **State 0: 1H Direction Filter (Hard-Lock):**
>    - If 1H is in an Uptrend (BULLISH) -> System is strictly BUY_ONLY. Selling/Shorting is 100% Hard-Blocked (`No Entry (Anti-Counter-BOS Lock - Buy Only)`). Under NO circumstances should any minor 5M pullback or CHoCH flip the trend to BEARISH.
>    - If 1H is in a Downtrend (BEARISH) -> System is strictly SELL_ONLY. Buying/Longing is 100% Hard-Blocked (`No Entry (Anti-Counter-BOS Lock - Sell Only)`). Under NO circumstances should any minor 5M bounce or CHoCH flip the trend to BULLISH.
> 2. **State 1: 15M Key POI (Point of Interest) Detection:**
>    - Do not buy at the top (Ceiling Trap) or sell at the bottom (Floor Trap).
>    - If BUY_ONLY: Identify the nearest 15M/5M Unmitigated Demand Zone (FVG or Order Block below price). Trigger remains INACTIVE (Awaiting Retrace) until price retraces into the Demand POI.
>    - If SELL_ONLY: Identify the nearest 15M/5M Unmitigated Supply Zone (FVG or Order Block above price). Trigger remains INACTIVE (Awaiting Retrace) until price retraces into the Supply POI.
> 3. **State 2: 5M Execution Engine (The Trigger):**
>    - Activates ONLY after price enters/taps the 15M POI:
>      - **Liquidity Sweep Wick:** Sweep of a recent 5M swing extreme with sharp rejection wick (Wick-to-Body ratio >= 1.5:1 or wick >= 35%).
>      - **Strong MSS Body Close:** Thick body candle close breaking the recent swing extreme (Choch / Displacement shift).
>      - **Valid FVG Formation:** Unmitigated Fair Value Gap created by the displacement move.
> 4. **Sniper Buffers and Targets:**
>    - **Buy Limit Entry:** `FVG_Top * 1.0004` (+0.04% spread buffer, Rule 34 & 62).
>    - **Sell Limit Entry:** `FVG_Bottom * 0.9996` (-0.04% spread buffer, Rule 34 & 62).
>    - **Stop Loss:** Outside the Sweep Low/High extreme with 0.10% safe buffer (`Sweep_Low * 0.9990` for Longs, `Sweep_High * 1.0010` for Shorts, Rule 19 & 25).
>    - **Targets:** TP1 at 1:1 Break-Even trigger, TP2 at strict 1:2.0 RR target.
>    - **Confidence Filter:** Strict >= 80% minimum confirmation threshold.
> 5. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - **1H Direction Hard-Lock → 15M POI Retrace → 5M Sweep/MSS Trigger ත්‍රිත්ව කාලරාමු පද්ධති නීතිය:**
>      - **පියවර 1 (State 0 - 1H Direction Hard-Lock):** 1H එක BULLISH නම් පද්ධතිය BUY_ONLY පමණක් වේ. 5M කුඩා Red Candle එකක් හෝ False CHoCH එකක් ආ පමණින් Trend එක Bearish වලට මාරු නොවිය යුතුය. SELL දීම 100% ක්ම තහනම්ය (Hard-Blocked). 1H එක BEARISH නම් පද්ධතිය SELL_ONLY පමණක් වේ. කිසිම හේතුවක් මත BUY නොදේ.
>      - **පියවර 2 (State 1 - 15M POI Retrace):** මිල උඩම මුදුනේදී (Ceiling Trap) Buy කිරීම හෝ පතුලේදී (Floor Trap) Sell කිරීම නැවැත්වීම. 15M/5M Demand/Supply FVG හෝ Order Block එක වෙත මිල Retrace වන තුරු රැඳී සිටීම.
>      - **පියවර 3 (State 2 - 5M Execution Engine):** මිල POI එක තුළට පැමිණි පසු Liquidity Sweep Wick (Wick-to-Body >= 1.5:1), Strong MSS Body Close, සහ Valid FVG තහවුරු කර ගැනීම.
>      - **පියවර 4 (Sniper Buffers & SL):** Buy Limit එක +0.04% Buffer (FVG_Top * 1.0004), Sell Limit එක -0.04% Buffer (FVG_Bottom * 0.9996), SL එක Sweep Extreme එකට ඔබ්බෙන් 0.10% Buffer සහිතව තැබීම (Sweep_Low * 0.9990 / Sweep_High * 1.0010), සහ අවම 80% Confidence එකක් තිබීම අනිවාර්ය වේ.

## 79. Dual-Model Dynamic Scalping Architecture (Breakaway Continuation & Premium Reversal Protocol) (New Master Rule)
> [!IMPORTANT]
> **DUAL-MODEL DYNAMIC SCALPING ARCHITECTURE RULES:**
> 1. **Model 1: Breakaway Continuation Buy Model:**
>    - In active markup momentum where price breaks local swing highs (5M BOS), the system strictly bypasses the distant 24-hour macro 50% Equilibrium requirement to prevent hours of missed trades.
>    - The active dealing range dynamically resets to the current 5M impulse leg (last 20-30 candles = 1.5 - 2.5 hours).
>    - Buy Limit is placed at the fresh 5M Demand Breakaway FVG with the +0.04% spread buffer (`FVG_Top * 1.0004`, Rule 34 & 62).
>    - Stop Loss is anchored strictly below the local Higher Low extreme with 0.10% safe buffer (`Local_Low * 0.9990`, Rule 19 & 25).
>    - Targets: TP1 at 1:1 Break-Even trigger, TP2 at strict 1:2.0 RR target (Rule 21 & 72).
> 2. **Model 2: Premium Reversal Short Model (Sell the Drop to Equilibrium):**
>    - When price sweeps the Highs (BSL / Equal Highs sweep with rejection wick) inside the Premium Zone, and confirms a 5M CHoCH displacement (candle body close below previous local low):
>    - The system does NOT sit idle waiting for price to drop to 50%!
>    - Instead, it immediately issues a **SELL LIMIT at the fresh 5M Supply FVG** with -0.04% spread buffer (`FVG_Bottom * 0.9996`, Rule 34 & 62).
>    - Stop Loss is anchored strictly above the sweep high extreme with 0.10% safe buffer (`Sweep_High * 1.0010`, Rule 19 & 25).
>    - Take Profit targets the downward drop into the 50% Equilibrium / Demand Base at strict 1:2.0 RR (Rule 21 & 72).
> 3. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - **Breakaway Continuation සහ Premium Reversal ද්විත්ව මාදිලි අධිවේගී Scalping නීතිය (Rule 79):**
>      - **මාදිලිය 1 (Breakaway Continuation Buy):** මිල අලුත් Highs හදමින් ඉහළ යන ප්‍රබල Uptrend එකකදී, මුළු දවසෙම 50% ගැඹුරු Equilibrium එනකම් පැය ගණන් බලා නොසිට, පසුගිය පැය 1-2 ක Local Wave එකේ හැදුණු ආසන්නතම 5M Breakaway FVG එකෙන් +0.04% Buffer සහිතව BUY LIMIT ලබා දේ. Local Low එකෙන් 0.10% පිටත ආරක්ෂිත SL සහ 1:2.0 RR TP සහිතයි.
>      - **මාදිලිය 2 (Premium Reversal Short):** මිල Premium උඩම මුදුනේදී High Sweep කර 5M CHoCH එකක් දුන් විට, මිල පහළ 50% ට වැටෙන තුරු නිකන් බලා නොසිට, එම පහළට වැටෙන ගමනෙන් ලාභ ගැනීමට Supply FVG එකෙන් -0.04% Buffer සහිතව SELL LIMIT ලබා දේ. Sweep High එකෙන් 0.10% පිටත ආරක්ෂිත SL සහ පහළ 50% Equilibrium වෙත 1:2.0 RR TP සහිතයි.

## 80. Dynamic LTF Structure Shift Precedence & Anti-Falling-Knife Mandate (New Master Rule)
> [!IMPORTANT]
> **DYNAMIC LTF STRUCTURE SHIFT PRECEDENCE & ANTI-FALLING-KNIFE RULES:**
> 1. **15M/5M CHoCH Precedence over 1H Bias:**
>    - High-timeframe (1H) candles take up to 60 minutes to close. Structural turns and distribution always originate on lower timeframes (5M and 15M).
>    - Regardless of whether the 1H trend appears "Bullish", if price sweeps the highs in the Premium zone and prints a confirmed Bearish CHoCH (candle body close breaking a 15M/5M swing low with displacement), the 15M/5M Bearish Shift takes 100% absolute precedence over the lagging 1H bias.
>    - Buying is 100% strictly forbidden (`No Entry (Anti-Falling-Knife & CHoCH Precedence Lock)`). The system flips bias dynamically to BEARISH and seeks SELL LIMIT entries at the fresh Supply FVG.
>    - Symmetrically, if 1H appears Bearish but price sweeps lows and prints a confirmed Bullish CHoCH (candle body close breaking 15M/5M swing high with displacement), Selling is 100% strictly forbidden. The system flips bias dynamically to BULLISH and seeks BUY LIMIT entries at the fresh Demand FVG.
> 2. **Anti-Falling-Knife Protection (Markdown / Markup Wave Lock):**
>    - During consecutive Lower Highs (active Markdown wave), buying is strictly prohibited even if price is in deep discount. Catching falling knives is 100% locked out.
>    - A BUY setup is authorized ONLY after a strong green displacement candle closes cleanly above the prior candle's high, breaking the Lower Highs wave.
>    - Symmetrically, during consecutive Higher Lows (active Markup wave), shorting is strictly prohibited until a red displacement candle breaks the sequence.
> 3. **Limit Orders Only & Wait for Pullback:**
>    - Market order execution upon detecting CHoCH is strictly forbidden.
>    - Entry is placed as a Limit Order at the fresh FVG boundary or 50% Mean Threshold of the Order Block with the 0.04% Rule 62 spread buffer.
>    - If price runs without pulling back to the limit order, the trade is skipped safely with 0% capital loss.
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - **15M/5M Structure Shift (CHoCH) ප්‍රමුඛතාවය සහ Anti-Falling-Knife නීතිය (Rule 80):**
>      - **1. 1H එකට වඩා 15M/5M Structure Shift (CHoCH) එකට ප්‍රමුඛතාවය:** 1H ඉටිපන්දමක් Close වීමට පැයක් ගතවන අතර, වෙළඳපල මුලින්ම හැරෙන්නේ 5M සහ 15M වලිනි. 1H කොතරම් Bullish යැයි පෙනුණද, මුදුනේදී Highs Sweep වී 15M හෝ 5M හි Swing Low එකක් පහළට කැඩුණොත් (Bearish CHoCH), එතැන් පටන් BUY කිරීම 100% ක්ම තහනම් වේ. පද්ධතිය ස්වයංක්‍රීයව BEARISH තත්ත්වයට හැරී Supply FVG වෙතින් SELL LIMIT පමණක් සොයයි. (පතුලේදී Low Sweep වී Bullish CHoCH වූ විට Sell සම්පූර්ණයෙන්ම තහනම් කර BUY LIMIT පමණක් සොයයි).
>      - **2. පහළට කඩා වැටෙන රැල්ලකදී (Lower Highs Markdown) Buy නොකිරීම:** ඉටිපන්දම් එක දිගට Lower Highs සාදමින් පහළට බසින විට මිල කොතෙක් අඩු (Discount) වුවද BUY නොකරයි (Falling Knife Trap Lockout). කොළ පැහැති ශක්තිමත් ඉටිපන්දමකින් කලින් ඉටිපන්දමේ High එක උඩින් Close වී (Displacement) Lower Highs රැල්ල කැඩෙන තුරු Buy නොදේ.
>      - **3. Market Order නැතිව Limit Order Retrace එනතුරු රැඳී සිටීම:** CHoCH වූ විගස Market Order වලින් නොපැන, FVG එක සීමාවේ 0.04% Buffer සහිතව Limit Order එකක් දමා මිල එතැනට Retrace වන තුරු රැඳී සිටිය යුතුය. Retrace නොවී ගියහොත් Trade එක අතහැර මුදල් 100% ආරක්ෂා කරයි.

## 81. True Structural Swing Protection & Pullback Re-Entry Protocol (New Master Rule)
> [!IMPORTANT]
> **TRUE STRUCTURAL SWING PROTECTION & PULLBACK RE-ENTRY RULES:**
> 1. **Anti-Micro-Wick Flip Mandate:**
>    - 2-3 consecutive 5M pullback candles (micro wicks making slightly lower highs / lower lows) must **NEVER flip the trend bias from BULLISH to BEARISH**.
>    - A trend bias can ONLY flip if the genuine Structural Swing Low (the validated Stop Loss level) is breached with a confirmed displacement candle body close below that swing extreme.
> 2. **Uptrend Pullback Re-Entry Mandate:**
>    - In an active Uptrend, price pulling back into Demand/Discount POI/FVG above the structural swing low is strictly evaluated for **BUY Re-Entry (Second Chance Entry)** opportunities.
>    - Counter-trend SELLING during an uptrend pullback is 100% STRICTLY FORBIDDEN and HARD-LOCKED (`No Entry (Anti-Counter-Uptrend Sell Lock)`).
>    - Symmetrically, during a confirmed Downtrend, relief rallies into Supply/Premium POI/FVG below the structural swing high are strictly evaluated for **SELL Re-Entry** opportunities. Counter-trend BUYING is 100% strictly forbidden.
> 3. **Active Trade Directional Lockout:**
>    - When an alert is active on a symbol and price remains within the trade boundaries (above Stop Loss for Long, or below Stop Loss for Short), opposing trade alerts on that coin are 100% HARD-BLOCKED.
>    - The system will never issue a Sell alert on a coin while a Long position is live and running above its Stop Loss.
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - **සැබෑ Structural Swing Extreme ආරක්ෂාව සහ Pullback Re-Entry නීතිය (Rule 81):**
>      - **1. ඉටිපන්දම් 3 ක Micro Wicks බලා Trend එක වෙනස් කිරීම සම්පූර්ණයෙන්ම නැවැත්වීම:** 5M ඉටිපන්දම් 2-3 ක් පහළට ආ පමණින් Trend එක BEARISH ලෙස Flip නොවිය යුතුය. Trend එක Flip විය හැක්කේ සැබෑ Structural Swing Low එක (අපේ SL මට්ටම) Displacement Candle Body එකකින් පහළට කැඩී ගියහොත් පමණි.
>      - **2. Uptrend Pullback එකකදී Sell නොව "BUY Re-Entry" පමණක් සෙවීම:** Buy Trend එකක් යන විට මිල පහළ බසින්නේ Sell කිරීමට නොව, Discount එකෙන් අඩු මිලට තවත් Buy එකක් (BUY Re-Entry) ගැනීමටයි. එබැවින් Swing Low එකට ඉහළින් සිදුවන Pullbacks වලදී SELL දීම 100% ක්ම තහනම් වන අතර සෙවිය යුත්තේ Buy Limit පමණි.
>      - **3. සක්‍රීය Trade එකක් පවතින විට ප්‍රතිවිරුද්ධ Signals 100% Block කිරීම:** යම් Coin එකක Long Trade එකක් ලබාදී මිල තවමත් Stop Loss එකට වඩා ඉහළින් ඇති තාක්, එම Coin එකට කිසිදු හේතුවක් මත SELL Alert ලබා නොදේ. එකම කාසියේ Buy දී තිබියදී Sell දී පරිශීලකයා අතරමං කිරීම 100% ක්ම වළක්වා ඇත.

## 82. 15M Institutional Structure Anchor & Early Invalidation Protection Protocol (New Master Rule)
> [!IMPORTANT]
> **15M INSTITUTIONAL STRUCTURE ANCHOR & EARLY INVALIDATION RULES:**
> 1. **15M Candlestick Body Close Precedence (15M Chart Anchor):**
>    - Macro Market Structure, Directional Bias, and Reversal are strictly determined by **15M Candlestick Body Closes**.
>    - 5M micro noise or wicks cannot reverse the 15M trend. The system strictly maps `candles_15m` to detect genuine Swing High breaks (Bullish BOS/CHoCH) or Swing Low breaks (Bearish BOS/CHoCH).
> 2. **Anti-Blind-SL Hunting (Early Structural Invalidation):**
>    - Traders DO NOT have to blindly sit and wait to "eat a full Stop Loss" if the trade structure is broken!
>    - If a 15M candle body closes beyond the structural anchor (below the 15M swing low for Longs, or above the 15M swing high for Shorts), the setup is immediately declared **`STRUCTURALLY INVALIDATED`**.
>    - An instant Invalidation Alert is sent to Telegram, instructing the trader to exit/cut the position early with minimal loss, protecting capital before price drops to the distant full SL.
> 3. **Dynamic +1.0R Break-Even Protection (Rule 77):**
>    - Upon price reaching +1.0R (TP1), Stop Loss is immediately shifted to entry price, eliminating all downside risk (Risk = 0.00%).
>    - Invalidation alerts automatically instruct moving SL to BE at +1.0R.
> 4. **Deep Discount FVG Limit Entry (Anti-Ceiling Trap):**
>    - Entries are strictly limit orders placed at the 15M/5M Discount FVG with the +0.04% Rule 62 buffer, preventing market chasing at the ceiling of pumps.
> 5. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - **15M ආයතනික Structure Anchor සහ Early Invalidation ආරක්ෂණ නීතිය (Rule 82):**
>      - **1. 15M ඉටිපන්දම් Body Close මඟින් පමණක් Market Structure තීරණය කිරීම:** වෙළඳපල Trend එක සහ Reversal එක තීරණය වන්නේ 15M ඉටිපන්දමක Body එක Close වීම මත පමණි. 5M කුඩා wicks හෝ noise මඟින් 15M Trend එක වෙනස් නොවේ.
>      - **2. Early Structural Invalidation (සම්පූර්ණ SL වැදීම වැළැක්වීම):** Trend එක කැඩී ගියහොත් සම්පූර්ණ Stop Loss එක වදින තෙක් බලා සිටීමට අවශ්‍ය නැත. 15M ඉටිපන්දමක Body එක අපේ Structural Support/Resistance මට්ටම කඩාගෙන Close වූ වහාම Trade එක 'INVALIDATED' ලෙස සලකා, Telegram එකට Alert එකක් යවා අවම අලාභයකින් Exit වීමට උපදෙස් දේ.
>      - **3. +1.0R Break-Even ආරක්ෂාව:** TP1 (+1.0R) ළඟා වූ විගස Stop Loss එක Entry මිලට ගෙන ගොස් අවදානම 0% ක් කරයි.
>      - **4. Ceiling Chasing වැළැක්වීම:** මිල උඩට ගිය පසු Market Orders වලින් නොපැන, 15M/5M Discount FVG එකට Limit Order එකක් දමා අඩු අවදානමකින් ඇතුල් විය යුතුය.

## 83. 15M 24-Hour Sequential Market Structure & CHoCH/BOS Foundation Protocol (Primary Foundation Step / මූලික පියවර 1)
> [!IMPORTANT]
> **15M 24-HOUR SEQUENTIAL MARKET STRUCTURE & CHOCH/BOS FOUNDATION RULES (PRIMARY FOUNDATION STEP):**
> 1. **Mandatory 24-Hour 15M Lookback Window (පැය 24 ක ඉටිපන්දම් 96 අනිවාර්යයෙන්ම විශ්ලේෂණය කිරීම):**
>    - Analysis must evaluate exactly 24 hours of price action backwards from the current candle on the 15-Minute timeframe (24 hours = exactly 96 candles of 15m).
> 2. **Chronological Sequential Mapping of all HH, HL, LL, LH (සියලුම Swings එකක් නෑර මාක් කර ගැනීම):**
>    - Chronologically from the start of the 24-hour window (candle -96) moving forward to the present candle, every single swing high and swing low must be clearly identified and sequentially mapped without skipping any.
> 3. **Bearish CHoCH Transition Verification for SELL / LL_LH Sequence (HH/HL සිට LL/LH වෙත මාරුවීමේදී CHoCH තහවුරු කිරීම):**
>    - If the 24-hour period began with HH/HL (Uptrend), and at the current analysis point the market is forming LL/LH (Downtrend), this transition is ONLY recognized as valid institutional structure if a confirmed Bearish CHoCH was formed prior to the LL/LH sequence. That CHoCH serves as mandatory confirmation.
> 4. **Bullish CHoCH Transition Verification for BUY / HH_HL Sequence (LL/LH සිට HH/HL වෙත මාරුවීමේදී CHoCH තහවුරු කිරීම):**
>    - Symmetrically for BUY setups: If the 24-hour period began with LL/LH (Downtrend), and at the current analysis point the market is forming HH/HL (Uptrend), this transition is ONLY recognized as valid institutional structure if a confirmed Bullish CHoCH was formed prior to the HH/HL sequence.
> 5. **Strictly 15-Minute Timeframe (15M කාලරාමුව පමණක් භාවිත කිරීම):**
>    - All structural evaluations are locked strictly to the 15-minute timeframe.
> 6. **Direction Dictated by Nearest Active Sequence (ළඟම ඇති ව්‍යුහයට අනුකූලව පමණක් Entry ලබා ගැනීම):**
>    - Backward from the present candle, examine the nearest active validated sequence:
>      - If LL/LH sequence -> SELL ENTRY ONLY (Buy is 100% hard-locked: `No Entry (Rule 83 Foundation Lock - 15M LL/LH Downtrend)`).
>      - If HH/HL sequence -> BUY ENTRY ONLY (Sell is 100% hard-locked: `No Entry (Rule 83 Foundation Lock - 15M HH/HL Uptrend)`).
> 7. **BOS Continuation Requirement (BOS Continue වී තිබීම අනිවාර්යයි):**
>    - In the active sequence, subsequent swing extremes must demonstrate confirmed Break of Structure (BOS) continuation in the trend direction.
> 8. **Mandatory 24-Hour Scope (පැය 24 ක කාල පරාසය අනිවාර්ය කිරීම):**
>    - 24-hour institutional context across Asian, London, and New York sessions is mandatory.
> 9. **15M Supreme Authority (වෙනත් කිසිම කාලරාමුවකින් Market Structure තහවුරු කිරීම තහනම්ය):**
>    - 15-minute chart is the sole and ultimate authority for market structure determination. Lower timeframes (1M, 3M, 5M) cannot override or contradict 15M structure.
> 10. **Candle Body Close Mandate (Wick Sweep vs Body Close Discretion):**
>     - For CHoCH (points 3 & 4) and BOS (point 7) to be verified, a 15M candlestick BODY must close beyond the swing extreme. A mere wick beyond the swing extreme is classified strictly as a Liquidity Sweep, NOT a structural break.
> 11. **Primary Foundation Step (මූලික පියවර):**
>     - This 10-point protocol is the bot's PRIMARY FOUNDATION STEP ("මූලික පියවර") in every trade analysis. No entry can be generated or evaluated without passing this foundation first.
> 12. **Sinhala Translation (සිංහල පරිවර්තනය):**
>     - **15M පැය 24 ආයතනික Market Structure සහ අනුක්‍රමික CHoCH/BOS මූලික පදනම් නීතිය (මූලික පියවර - Rule 83):**
>       - **1. පැය 24 ක ඉටිපන්දම් 96 ක අනිවාර්ය විශ්ලේෂණය:** විශ්ලේෂණය කරන මොහොතේ සිට ආපස්සට පැය 24 ක කාලය (15M ඉටිපන්දම් 96) අනිවාර්යයෙන්ම පරීක්ෂා කළ යුතුය.
>       - **2. සියලුම HH, HL, LL, LH එකක් නෑර මාක් කිරීම:** පැය 24 ආරම්භක ඉටිපන්දමේ සිට ඉදිරියට වත්මන් මොහොත දක්වා සියලුම Swing Highs සහ Swing Lows එකක් නෑර අනුක්‍රමිකව ලකුණු කළ යුතුය.
>       - **3. SELL සඳහා Bearish CHoCH තහවුරු කිරීම:** පැය 24 ආරම්භයේදී HH/HL (Uptrend) තිබී වත්මන් මොහොතේ LL/LH හැදෙන්නේ නම්, LL/LH වලට පෙර අනිවාර්යයෙන්ම Bearish CHoCH එකක් නිර්මාණය වී තහවුරු විය යුතුය.
>       - **4. BUY සඳහා Bullish CHoCH තහවුරු කිරීම:** පැය 24 ආරම්භයේදී LL/LH (Downtrend) තිබී වත්මන් මොහොතේ HH/HL හැදෙන්නේ නම්, HH/HL වලට පෙර අනිවාර්යයෙන්ම Bullish CHoCH එකක් නිර්මාණය වී තහවුරු විය යුතුය.
>       - **5. විනාඩි 15 කාලරාමුවෙන් පමණක් බැලීම:** මෙම සියලුම ව්‍යුහයන් පරීක්ෂා කරන්නේ 15-Minute චාර්ට් එකෙන් පමණි.
>       - **6. ළඟම ව්‍යුහය අනුව Entry ලබා ගැනීම:** වත්මන් මොහොතට ආසන්නතම ව්‍යුහය LL/LH නම් SELL පමණක්ද, HH/HL නම් BUY පමණක්ද ලබා ගනී. විරුද්ධ පැත්තට trade දැමීම 100% තහනම්ය.
>       - **7. BOS Continue වී තිබීම:** අදාළ ව්‍යුහය තුළ Break of Structure (BOS) අඛණ්ඩව ඉදිරියට ගමන් කර තිබිය යුතුය.
>       - **8. පැය 24 අනිවාර්ය කිරීම:** සම්පූර්ණ දවසේ Session Liquidity ආවරණය වන පරිදි පැය 24 ම පරීක්ෂා කෙරේ.
>       - **9. 15M ප්‍රමුඛතාවය:** Market Structure තහවුරු කිරීම 15M එකෙන් පමණක් කළ යුතු අතර වෙනත් කිසිදු Timeframe එකකින් Market Structure තීරණය කිරීම තහනම්ය.
>       - **10. Candle Body Close අනිවාර්ය කිරීම:** CHoCH සහ BOS තහවුරු වීමට නම් 15M Candlestick Body එකක්ම Extreme එකෙන් එපිටට Close විය යුතුය. Wick එකක් පමණක් ගියහොත් එය Liquidity Sweep එකක් පමණි.

## 84. Triple-Timeframe Triad Alignment & IDM Protocol (HTF 1H + ITF 15M + LTF 3M/1M Foundation)
> [!IMPORTANT]
> **TRIPLE-TIMEFRAME TRIAD ALIGNMENT & IDM PROTOCOL RULES (PRIMARY FOUNDATION STEP):**
> 1. **1H Higher Time Frame (HTF) — Trend & Bias (50 – 100 Candles):**
>    - Primary Objective: Determine overall macro market direction and key structural boundaries.
>    - Sequential Mapping: Sequentially map all Swing Highs and Swing Lows using Break of Structure (BOS).
>    - BOS Candlestick Body Close Mandate: BOS is valid ONLY when a candle BODY closes cleanly above the previous Swing High (Uptrend) or below the previous Swing Low (Downtrend). Wicks breaking prior swings do NOT count as BOS (treated strictly as liquidity sweeps).
>    - Active Direction: Determined strictly by the nearest active structure to current market price:
>      - If recent sequence is HH, HL -> Macro Bias is BULLISH (BUY SETUPS ONLY).
>      - If recent sequence is LL, LH -> Macro Bias is BEARISH (SELL SETUPS ONLY).
>    - Transition Lockout: If a 1H CHoCH transition is actively forming without confirmed structural follow-through, all trade entries are temporarily locked to prevent counter-trend traps.
> 2. **15M Intermediate Time Frame (ITF) — Structure, IDM & POI (40 – 80 Candles):**
>    - Primary Objective: Pinpoint high-probability Points of Interest (POI), Inducement (IDM), and Dealing Range.
>    - True 15M CHoCH: Candle body close breaking the last Higher Low (Bearish CHoCH) or Lower High (Bullish CHoCH).
>    - Valid Inducement (IDM) Engine:
>      - Bullish Market (HL -> HH move): Look at the closest internal swing point to the HH. Inspect that swing's highest candle; if its lower wick is broken by a subsequent candle body, that level is marked as a Valid IDM. Price must retrace to sweep this IDM before continuing upward.
>      - Bearish Market (LH -> LL move): Look at the closest internal swing point to the LL. Inspect that swing's lowest candle; if its upper wick is broken by a subsequent candle body, that level is marked as a Valid IDM. Price must retrace to sweep this IDM before continuing downward.
>    - 5-Criteria Valid Order Block (OB): Must satisfy all 5 confluences: (1) BOS, (2) Originates at Swing Point, (3) Liquidity Hunt (Sweep), (4) Imbalance (FVG), (5) Unmitigated.
>    - Fibonacci Golden Rule (0.618 – 0.66 Retracement):
>      - Bullish: Measured from swing HL to HH. Golden Pocket = 0.618 to 0.66 retracement zone.
>      - Bearish: Measured from swing LH to LL. Golden Pocket = 0.618 to 0.66 retracement zone.
>      - Prime Institutional POI: When a valid 15M Order Block aligns within or overlaps the 0.618 – 0.66 Golden Pocket, it is marked as the Highest-Probability POI.
> 3. **1M / 3M Lower Time Frame (LTF) — Trigger & Execution (20 – 40 Candles):**
>    - Primary Objective: Sniper execution with minimal risk and maximum Risk-to-Reward.
>    - POI Tap & Micro Confirmation: Once price enters the 15M Golden POI, evaluate the 1M or 3M chart for Micro Liquidity Sweep + Micro CHoCH.
>    - **Mandatory Post-CHoCH Confirmation Gate (No Immediate Raw CHoCH Entries):**
>      - A trade MUST NEVER be entered immediately on the raw CHoCH candle!
>      - Bullish Setup: After Bullish CHoCH, the engine MUST wait for the subsequent pullback to print a confirmed **Higher Low (HL)**!
>      - Bearish Setup: After Bearish CHoCH, the engine MUST wait for the subsequent pullback to print a confirmed **Lower High (LH)**!
>      - Once the first confirmed HL (Buy) or LH (Sell) forms, place a **Limit Order** at the micro FVG / OB boundary with the Rule 62 0.04% spread buffer.
>    - Tight Stop Loss (SL): Placed outside the manipulation extreme incorporating the Rule 19 0.10% safe buffer (`swing_low * 0.9990` for Buy, `swing_high * 1.0010` for Sell) + 1.5x ATR.
>    - Dynamic Take Profit (TP): 1:2.0 to 1:4.0 RR targeting structural liquidity, with +1.0R Break-Even position protection (Rule 77).
> 4. **100% Triad Alignment Mandate (Zero-Bypass Lockout):**
>    - All three timeframes MUST agree simultaneously:
>      - 1H Bullish + 15M Bullish + 1M/3M Bullish -> **BUY LIMIT ONLY**
>      - 1H Bearish + 15M Bearish + 1M/3M Bearish -> **SELL LIMIT ONLY**
>    - If any single timeframe disagrees (e.g., 1H is Bullish, 15M is Bullish, but 1M/3M is in a downward pullback and hasn't formed the post-CHoCH HL yet), the trade is **100% HARD-LOCKED** (`No Entry (Rule 84 Triad Alignment Lock)`).
> 5. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - **1H HTF + 15M ITF + 1M/3M LTF ත්‍රිත්ව කාලරාමු සහ IDM මූලික පදනම් නීතිය (Rule 84):**
>      - **1. 1H Higher Time Frame (HTF) — Trend & Bias (ඉටිපන්දම් 50 - 100):** සමස්ත වෙළඳපල දිශාව තීරණය කිරීම. BOS තහවුරු විය යුත්තේ Candle Body Close එකකින් පමණි (Wick කැඩීම BOS නොවේ). ආසන්නතම ව්‍යුහය HH/HL නම් BUY පමණක්ද, LL/LH නම් SELL පමණක්ද අවසර ලබයි.
>      - **2. 15M Analysis Time Frame (ITF) — Structure & IDM (ඉටිපන්දම් 40 - 80):** 
>        - 15M CHoCH: Up trend හි HL කැඩීම Bearish CHoCH ද, Down trend හි LH කැඩීම Bullish CHoCH ද වේ.
>        - Valid Inducement (IDM): Bullish වෙළඳපලක HL සිට HH දක්වා යාමේදී HH ට ආසන්නතම Swing point එකේ ඉහළම කැන්ඩ්ල් එකේ පහළම wick එක candle body එකකින් කැඩී තිබීම Valid IDM වේ. Bearish වෙළඳපලක LL ට ආසන්නතම swing point එකේ පහළම කැන්ඩ්ල් එකේ ඉහළම wick එක candle body එකකින් කැඩී තිබීම Valid IDM වේ. මිල මෙම IDM Sweep කර නැවත හැරී එයි.
>        - Valid Order Block: BOS, Swing Point, Liquidity Hunt, Imbalance (FVG), Unmitigated යන කරුණු 5 ම සම්පූර්ණ විය යුතුය.
>        - Fibonacci Golden Zone (0.618 - 0.66): HL සිට HH දක්වා (Buy) හෝ LH සිට LL දක්වා (Sell) Fibonacci දැමූ විට 0.618 - 0.66 Golden Zone එක සහ Valid OB එක එකට හමුවන තැන Highest-Probability POI වේ.
>      - **3. 1M / 3M Entry Time Frame (LTF) — Trigger & Confirmation (ඉටිපන්දම් 20 - 40):** 15M Golden POI එකට මිල පැමිණි පසු Micro Sweep සහ CHoCH බලයි. **නමුත් CHoCH හැදුණු සැනින් Trade දෙන්නේ නැත!** Buy සඳහා CHoCH පසු පළමු Higher Low (HL) එක සාදන තෙක්ද, Sell සඳහා Lower High (LH) සාදන තෙක්ද බලා සිටිය යුතුය. ඉන්පසු 0.04% Buffer එක සහිතව 1M/3M FVG/OB වෙතින් Limit Order එක ලබාදේ. Tight SL සහ 1:2.0 සිට 1:4.0 RR ඉලක්ක සහිතව +1.0R Break-Even ලබාදේ.
>      - **4. ත්‍රිත්ව කාලරාමු 100% සමාන වීමේ නීතිය (Triad Alignment):** 1H, 15M සහ 1M/3M යන කාලරාමු 3 ම එකම දිශාවකට (තුනම Bullish හෝ තුනම Bearish) තිබිය යුතුය. එකක් හෝ නොගැලපේ නම් Trade එක 100% ක් Lock විය යුතුය.
> 
## 26. Falcon Master 7-Step Execution Protocol (Ultimate Hard-Locked Edition - Rules 85 to 91)
> [!IMPORTANT]
> **THE FALCON MASTER 7-STEP EXECUTION PROTOCOL (ULTIMATE HARD-LOCKED EDITION - RULES 85-91):**
> The Falcon Engine's real-time market execution is strictly locked into an integrated sequential 7-Step Pipeline (with zero isolated rules, total 91 rules) enforced by 5 Impenetrable Hard Locks:
> 
> 1. **Step 1 (Rule 85): Pre-Flight Safety & 15M Macro Direction Anchor:**
>    - USD High-Impact News lockout active (+/- 60 minutes before/after news release). All new trade setups are 100% suspended during this window.
>    - 15M Timeframe determines macro direction: 15M Bullish (HH/HL sequence) -> BUY ONLY lock; 15M Bearish (LL/LH sequence) -> SELL ONLY lock. Counter-trend trading against 15M macro trend is 100% strictly forbidden.
>    - **[HARD LOCK 1 - Anti-Momentum Filter]:** Prior to issuing any setup, the bot must check price velocity approaching our POI. If massive momentum candles (e.g. huge adverse Bullish/Bearish candles with body > 2.0x average candle size) smash into the POI without deceleration, the setup is 100% REJECTED and discarded (`No Entry (Hard Lock 1: Anti-Momentum POI Breach Lock)`). Zero catching of falling knives or runaway momentum candles!
> 
> 2. **Step 2 (Rule 86): Setup Direction & 5M Breaker Block Detection:**
>    - Determine the setup path based on 15M/5M market structure, giving primary priority to the **5M Breaker Block**:
>      - Bullish Market: A prior Bearish Order Block broken aggressively upward with a displacement candle body is marked as a **5M Bullish Breaker Block**.
>      - Bearish Market: A prior Bullish Order Block broken aggressively downward with a displacement candle body is marked as a **5M Bearish Breaker Block**.
>    - This filters out hidden institutional traps and failed order blocks.
> 
> 3. **Step 3 (Rule 87): Deep Base Rule & 35% Zone (Unmitigated POI):**
>    - The identified 5M Breaker Block must reside within the Golden Zone (Equilibrium 50% and Fib 0.618 - 0.66).
>    - BUY setups must originate strictly inside the bottom 35% Discount Base of the Dealing Range.
>    - SELL setups must originate strictly inside the top 35% Premium Base of the Dealing Range.
>    - Late-cycle mid-range trades (35% - 65%) are 100% strictly locked out (`No Entry (Anti-Late-Cycle Lock)`).
> 
> 4. **Step 4 (Rule 88): Major ERL Sweep & Alert-Only Protocol (Patience Gate):**
>    - Major External Range Liquidity (ERL) must be swept (BUY: PDL or Asian Low; SELL: PDH or Asian High).
>    - Retrace into 5M Breaker Block: Price must retrace cleanly inside the 5M Breaker Block.
>    - **[HARD LOCK 2 - Alert-Only Entry Block]:** When price arrives at the 5M Breaker Block, the bot MUST NOT issue any Entry / Limit Order signal (Zero Blind Limits!). Instead, the bot MUST ONLY issue an alert: `"POI Reached - Waiting for 3M CHoCH"`. Premature entries at Step 4 are 100% strictly forbidden.
> 
> 5. **Step 5 (Rule 89): LTF Confirmation (3M Timeframe Lock) & Post-CHoCH FVG Verification:**
>    - Once price reaches the 5M Breaker Block, switch to the 3M timeframe for confirmation.
>    - **[HARD LOCK 3 - Strict 3M Data Feed]:** The Execution Engine is strictly locked to the **3-Minute (3M) Timeframe only**. Generating execution signals from 1m data is 100% FORBIDDEN and HARD-BLOCKED.
>    - **[HARD LOCK 4 - Post-CHoCH FVG Verification]:** Require a clean candle BODY CLOSE Market Structure Shift (3M MSS/CHoCH) accompanied by high relative volume (RVOL >= 1.35x). Crucially, AFTER the 3M CHoCH break occurs, a brand new **3M FVG (Fair Value Gap)** MUST be formed and verified by the bot. If no new 3M FVG exists post-CHoCH, NO trade signal can be given. Fake wick-only CHoCH breaks are rejected.
> 
> 6. **Step 6 (Rule 90): Unicorn Setup Engine & Clear Sky Runway (Limit Entry):**
>    - All confirmations must pass before releasing the final Trade Signal.
>    - **[HARD LOCK 5 - Dynamic Limit Placement]:** The Limit Order price MUST be placed strictly on the newly formed **3M FVG** (from Step 5), NOT on the old 5M zone! Use 0.04% Spread Buffer (`* 1.0004` for Buy, `* 0.9996` for Sell).
>    - **Clear Sky Runway:** The entry must have at least 1.5R to 2.0R unobstructed clear runway to the nearest opposing wall.
> 
> 7. **Step 7 (Rule 91): Multi-Stage Risk Management & Logical Exit:**
>    - Stop Loss (SL) anchored outside the newest 3M Swing Extreme with a 0.10% safety buffer (`* 0.9990` for Buy, `* 1.0010` for Sell).
>    - TP1: 1:2.0 Risk-to-Reward ratio (50% partial close).
>    - Break-Even (BE): When profit reaches +1.0R, immediately move SL to Entry (Zero-Risk).
>    - TP2 Runner: Anchored to the nearest major 5M target (5M HH/LL or Supply/Demand zone) targeting 1:3.0R to 1:4.0R.
> 
> 8. **Sinhala Translation (සිංහල පරිවර්තනය):**
>    - **පියවර 1 (නීතිය 85): ආර්ථික පුවත් පෙරහන සහ 15M ප්‍රධාන දිශාව තීරණය කිරීම:** USD High-Impact පුවත් නිකුත් වීමට පෙර සහ පසු විනාඩි 60 තුළ ට්‍රේඩ් කිරීම සම්පූර්ණයෙන්ම අත්හිටුවයි. 15M Timeframe එකෙන් ප්‍රධාන දිශාව (Bullish -> BUY ONLY, Bearish -> SELL ONLY) තීරණය කර Counter-trend සම්පූර්ණයෙන්ම තහනම් කරයි.
>      - **[HARD LOCK 1 - Anti-Momentum Filter]:** විශාල Momentum Candles මඟින් අපගේ කලාපය (POI) කඩාගෙන මිල කඩා වැටෙන්නේ/නගින්නේ නම්, එම අවස්ථාවේදී අදාළ Setup එක 100% ක් ප්‍රතික්ෂේප කර අතහැර දමයි.
>    - **පියවර 2 (නීතිය 86): Setup දිශාව සහ 5M Breaker Block එක හඳුනාගැනීම:** 15M/5M Market Structure මත පදනම්ව 5M Breaker Block හඳුනාගනී (Displacement සහිතව කැඩී ගිය Failed OB එක Breaker Block එක ලෙස සලකුණු කරයි).
>    - **පියවර 3 (නීතිය 87): Deep Base නීතිය සහ 35% කලාපය (Unmitigated POI) තහවුරු කිරීම:** 5M Breaker Block එක Golden Zone (Eq 50% සහ Fib 0.618–0.66) තුළ පිහිටිය යුතුය. Buy සෙටප් Dealing Range හි පහළම 35% Discount Base එක තුළද, Sell සෙටප් ඉහළම 35% Premium Base එක තුළද පිහිටිය යුතුය (Mid-Range Trading තහනම්ය).
>    - **පියවර 4 (නීතිය 88): ERL Sweep වීම සහ Alert-Only Protocol (Patience Gate):** ප්‍රධාන ERL (PDL/PDH හෝ Asian Low/High) Sweep විය යුතුය. මිල 5M Breaker Block කලාපය ඇතුළටම පැමිණිය යුතුය.
>      - **[HARD LOCK 2 - Alert-Only Entry Block]:** මිල 5M කලාපයට පැමිණි පමණින් කිසිදු Entry / Limit Order එකක් නොදෙයි (Zero Blind Limits). ඒ වෙනුවට "POI Reached - Waiting for 3M CHoCH" යනුවෙන් Alert එකක් පමණක් නිකුත් කරයි.
>    - **පියවර 5 (නීතිය 89): කුඩා කාලරාමුවේ Confirmation එක (3M Timeframe Lock):**
>      - **[HARD LOCK 3 - Strict 3M Data Feed]:** Execution Engine එක අනිවාර්යයෙන්ම 3-Minute (3M) Timeframe එකට පමණක් ලොක් කර ඇත. 1m Data භාවිතයෙන් සිග්නල් දීම 100% ක් තහනම් කර ඇත.
>      - **[HARD LOCK 4 - Post-CHoCH FVG Verification]:** 3M Chart එකේ Candle Body Close MSS/CHoCH සිදුවිය යුතු අතර, එම Shift එකෙන් පසු අලුතින්ම 3M FVG එකක් සෑදී ඇති බව තහවුරු විය යුතුය. අලුත් 3M FVG එකක් නැතිනම් සිග්නල් ලබා නොදෙයි.
>    - **පියවර 6 (නීතිය 90): Unicorn Setup එන්ජිම සහ Clear Sky Target එක (Entry එක ලබා දීම):**
>      - **[HARD LOCK 5 - Dynamic Limit Placement]:** Limit Order එක තබන්නේ පැරණි 5M කලාපයේ නොව, අලුතින් හැදුණු 3M FVG කලාපය මත 0.04% Spread Buffer එකක් සහිතවය. අවම 1.5R - 2.0R Clear Sky Runway එකක් තිබිය යුතුය.
>    - **පියවර 7 (නීතිය 91): බහු-අදියර අවදානම් කළමනාකරණය (Risk Management):** 3M Swing Extreme පිටතින් 0.10% Buffer සහිත SL. 1:2.0 RR හිදී TP1 50% ලාභය ලබාගනී (Partial Close). +1.0R ලාභයේදී SL එක Entry මිලට ගෙන යයි (Break-Even). TP2 Runner ඉලක්කය 5M HH/LL හෝ Supply/Demand කලාපය (1:3.0R - 1:4.0R).

