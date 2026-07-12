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
