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
2. **Equilibrium Matrix Calculation**: Bypassed for SMC setups. Do not restrict Long signals in Premium or Short signals in Discount.
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

## 16. Multi-Timeframe POI Reversal & 1m Confirmation Protocol (New Rule)
> [!IMPORTANT]
> **1M TIMEFRAME STRUCTURE EXECUTION RULES:**
> 1. **Step 1 (Bypass Macro Lockout):** The requirement that 1-Hour (1H) and 15-Minute (15M) trends must align is completely removed.
> 2. **Step 2 (1m Structure Determination):** The setup execution direction (daily bias) is determined strictly by the active **1-minute (1m) timeframe structure**:
>    - **BUY Side:** If 1m trend is `BULLISH` -> Search for Buy Limit setups at the 1m OB/FVG.
>    - **SELL Side:** If 1m trend is `BEARISH` -> Search for Sell Limit setups at the 1m OB/FVG.
> 3. **Step 3 (Micro Confirmation & Entry):** Within the 1m structure, search for recent Swing High/Low sweeps (liquidity sweeps), MSS/CHoCH, and FVG/OB confluences to execute the Limit Order entry.
>    - **Stop Loss:** Placed strictly above/below the 1m high/low swing extreme (incorporating the Rule 25 buffer).
>    - **Take Profit:** Target the next local 1m/15m swing extreme (within the dynamic 1:2 to 1:4 RR boundary).
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):** 1H සහ 15M ප්‍රවණතා ගැලපීමේ අවශ්‍යතාවය සම්පූර්ණයෙන්ම ඉවත් කර ඇත. වෙළඳාම් ඇතුළත් කිරීම් (Entries) සිදු කරනු ලබන්නේ සක්‍රීය **1-minute (1m) කාල රාමුවේ ව්‍යුහය (structure)** මත පදනම්වය:
>    - 1m trend එක `BULLISH` නම් -> Buy Limit setups ද,
>    - 1m trend එක `BEARISH` නම් -> Sell Limit setups ද,
>    - 1m චාර්ට් එකෙහි සිදුවන Choch, OB, FVG ආදිය පරීක්ෂා කර ඇතුල්වීම් සිදුකරයි.

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

## 23. Fibonacci Golden & OTE Zone Optimization Protocol (New Rule)
> [!IMPORTANT]
> **FIBONACCI GOLDEN/OTE RETRACEMENT RULES:**
> 1. **Strict Fibonacci Retracement Alignment:** The calculated entry price for any setup must fall strictly within the high-probability Fibonacci retracement Golden Zone or Optimal Trade Entry (OTE) zone (between 50.0% and 88.6% retracement of the active swing dealing range).
> 2. **Automatic Pullback Price Optimization:** If the structural entry price (e.g. from FVG or Order Block) falls outside this 50.0% - 88.6% range (too shallow or too deep), the system must automatically adjust/optimize the recommended entry price to the 61.8% Golden Ratio retracement level of the dealing range to ensure optimal risk-to-reward.
> 3. **Sinhala Translation (සිංහල පරිවර්තනය):** නිර්දේශිත ඇතුල්වීමේ (Entry) මිල සැමවිටම Fibonacci Golden Zone හෝ OTE කලාපය (50.0% - 88.6% retracement) අතර පිහිටිය යුතුය. එයින් පරිබාහිර වුවහොත්, පද්ධතිය ස්වයංක්‍රීයව ඇතුල්වීමේ මිල 61.8% මට්ටමට වෙනස් කරයි.

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

