# Archive: Pre-v9.8 Prompts
**Date Archived:** 2025-09-21
**Reason:** Superseded by v9.8 with complete QA patch integration

## Archived Files

### 1. CHATGPT_MASTER_PROMPT_V9.6_SEQUENTIAL.md
- **Version:** 9.6
- **Status:** Superseded by v9.8
- **Description:** ChatGPT master prompt with phase 0-14 schemas

### 2. CLAUDE_CODE_MASTER_V9.7_SEQUENTIAL.md
- **Version:** 9.7 (labeled as 9.6 in file)
- **Status:** Superseded by v9.8
- **Description:** Claude Code Python implementation framework

### 3. CLAUDE_CODE_V9.7_ENHANCEMENTS.md
- **Version:** 9.7 enhancements
- **Status:** Integrated into v9.8
- **Description:** QA patch enhancements that were separate, now integrated

## What Changed in v9.8

### Major Enhancements
- ✅ All QA patches for phases 0-14 fully integrated
- ✅ Complete phase schemas with all required fields
- ✅ Universal validation rules enforced
- ✅ Enhanced classes for translation, negative evidence, NPKT
- ✅ Operator checklists for all 15 phases
- ✅ Leonardo Standard with scoring system
- ✅ Quality gates with 90-100% thresholds

### Critical Requirements Added
- Mandatory `as_of` timestamps on every entry
- Alternative explanations required for all claims
- Translation safeguards with back-translation
- Negative evidence logging for specific phases
- ≥3 alternative hypotheses/indicators where required
- No averaging of conflicting assessments
- Cross-phase consistency checking

## Current Active Versions
- **ChatGPT:** CHATGPT_MASTER_PROMPT_V9.8_COMPLETE.md (if created)
- **Claude Code:** CLAUDE_CODE_MASTER_V9.8_COMPLETE.md

---
*These files are archived for reference. Use v9.8 for all new work.*
