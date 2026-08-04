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
> 2. **Pullback Patience over Lockouts:** The user places pending Limit Orders on their exchange and waits patiently for the market to reach and trigger them. Therefore, the bot must NEVER suppress, lock out, or invalidate setups because they are "too close to the market price" or because the Swing Extreme is wide (which results in a wider SL and TP). All valid structural setups must be displayed.
> 3. **Absolute Stop Loss Protection:** To prevent waiting orders from getting stopped out prematurely by manipulation wicks, the Stop Loss must strictly be placed past the absolute Swing Extreme (Strong High/Low) with the programmatic 0.1% buffer (Rule 19 & 25).
> 4. **Sinhala Translation (සිංහල පරිවර්තනය):** පරිශීලකයා විසින් Limit Orders යොදා වෙළඳපල මිල එම මට්ටමට පැමිණෙන තෙක් ඉවසීමෙන් බලා සිටීමට සූදානම් බැවින්, ඇතුල්වීමේ මිල වත්මන් මිලට ආසන්න වීම හෝ Swing Low/High පරාසය පළල් වීම මත පදනම්ව සෙටප් අවහිර නොකළ යුතුය. ඇතුල්වීම සැමවිටම FVG/OB සීමාවේදී Sniper Entry එකක් ලෙස සකසා, Stop Loss එක සැමවිටම swing extreme එකෙන් පිටත 0.1% ක බෆරයක් සහිතව තැබිය යුතුය.

