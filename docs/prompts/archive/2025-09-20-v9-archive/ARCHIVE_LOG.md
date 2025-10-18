# PROMPT ARCHIVE LOG
**Date Archived:** 2025-09-20
**Action:** Consolidated master prompts to v9.2/v9.3 final versions

---

## ARCHIVED PROMPTS

### ChatGPT Master Prompts (Archived)
- `CHATGPT_MASTER_PROMPT_V6_COMPLETE.md` - Original v6 with fabrication issues
- `CHATGPT_MASTER_PROMPT_V7.0_UNIFIED.md` - First unified attempt
- `CHATGPT_MASTER_PROMPT_V7.1_NARRATIVE.md` - Narrative enhancement
- `CHATGPT_MASTER_PROMPT_V8.0_ZERO_FABRICATION.md` - First zero-fabrication version
- `CHATGPT_MASTER_PROMPT_V9.1_ZERO_FABRICATION.md` - Intermediate v9

### Claude Code Master Prompts (Archived)
- `CLAUDE_CODE_MASTER_V6_COMPLETE.md` - Original v6 with issues
- `CLAUDE_CODE_MASTER_V6.1_UPDATED.md` - Minor update to v6
- `CLAUDE_CODE_MASTER_V7.0_UNIFIED.md` - Unified with ChatGPT approach
- `CLAUDE_CODE_MASTER_V8.0_ZERO_FABRICATION.md` - First zero-fabrication version
- `CLAUDE_CODE_MASTER_V9.1_ZERO_FABRICATION.md` - Intermediate v9
- `CLAUDE_CODE_MASTER_V9.2_ENHANCED.md` - Enhanced v9 (superseded by v9.3)

---

## ACTIVE PROMPTS (Kept in active/master)

### Current Production Versions
1. **`CHATGPT_MASTER_PROMPT_V9.2_ENHANCED.md`**
   - Zero-fabrication enforcement
   - INSUFFICIENT_EVIDENCE protocol
   - Enhanced verification requirements
   - Current production version for ChatGPT

2. **`CLAUDE_CODE_MASTER_V9.3_ENFORCEMENT.md`**
   - Strict enforcement mechanisms
   - Automated verification
   - Data-first approach
   - Current production version for Claude Code

---

## ARCHIVE REASON

All versions prior to v9.2/v9.3 have been archived because they:
- Allowed or encouraged fabrication
- Lacked proper verification requirements
- Missing INSUFFICIENT_EVIDENCE protocols
- Did not enforce data-first approaches

The v9.2/v9.3 versions represent a fundamental shift to:
- **Zero tolerance for fabrication**
- **Mandatory verification for all claims**
- **INSUFFICIENT_EVIDENCE as default when no data exists**
- **Enforcement mechanisms built into prompts**

---

## MIGRATION NOTES

### Key Changes from Earlier Versions:
1. Removed all "create plausible" language
2. Added mandatory verification steps
3. Implemented 14-point documentation checklist
4. Required source + line number for every claim
5. Added recompute commands for all numbers

### If Reverting Needed:
All archived prompts are preserved in this directory and can be restored if needed, but this is strongly discouraged as they enable fabrication.

---

*Archived to prevent accidental use of prompts that allow fabrication*
