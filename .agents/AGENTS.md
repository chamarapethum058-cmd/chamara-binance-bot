# Project Falcon Customization Rules

## 1. Sinhala Translation Preservation Requirement
> [!IMPORTANT]
> **CRITICAL REQUIREMENT:** Do NOT remove or modify the **Sinhala Translation (සිංහල පරිවර්තනය)** features from the AI responses, Technical Reasoning, Invalidation details, Risk Notes, or error alerts.
> The user relies on these bilingual explanations to understand strategy actions, rule lockouts, and risk alerts.
> 
> When modifying backend analysis prompts (`backend/app/services.py`), ensure the AI generator is always instructed to return bilingual outputs (English + Sinhala translations).
> When modifying frontend UI tabs (`frontend/src/app/page.tsx`), ensure the rendering of the translation dropdowns, tabs, and bilingual text matches this structure exactly.
