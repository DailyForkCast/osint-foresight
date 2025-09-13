# Phase Renumbering Guide - OSINT Foresight Project

## Overview
We have renumbered all phases in the OSINT Foresight project to create a more logical, sequential numbering system from 0-13.

## Phase Number Mapping

| Old Phase | New Phase | Description |
|-----------|-----------|-------------|
| X | 0 | Definitions & Taxonomy |
| 0 | 1 | Setup & Configuration |
| 1 | 2 | Indicators & Data Sources |
| 2 | 3 | Technology Landscape |
| 2S | 4 | Supply Chain Security |
| 3 | 5 | Institutions & Accredited Labs |
| 4 | 6 | Funding & Instruments |
| 5 | 7 | International Links & Collaboration |
| 6 | 8 | Risk Assessment & Best Practice |
| 7C | 9 | PRC Interest & MCF Acquisition |
| 7R | 10 | Red Team Review & Assumption Check |
| 8 | 11 | Foresight & Early Warning |
| 9 | 12 | Extended Foresight (Slovakia-specific) |
| 10 | 13 | Closeout |

## Key Changes Made

### 1. Python Analysis Scripts
All scripts in `src/analysis/` have been renamed:
- `phase2_landscape.py` → `phase3_landscape.py`
- `phase2s_supply_chain.py` → `phase4_supply_chain.py`
- `phase3_institutions.py` → `phase5_institutions.py`
- `phase4_funders.py` → `phase6_funders.py`
- `phase5_links.py` → `phase7_links.py`
- `phase6_risk.py` → `phase8_risk.py`
- `phase7c_posture.py` → `phase9_posture.py`
- `phase8_foresight.py` → `phase11_foresight.py`

### 2. Report File Names
When generating reports, use the new phase numbers:
- `phase-0_taxonomy.md` (was phase-X)
- `phase-1_setup.md` (was phase-0)
- `phase-2_indicators.md` (was phase-1)
- `phase-3_landscape.md` (was phase-2)
- `phase-4_supply_chain.md` (was phase-2s)
- `phase-5_institutions.md` (was phase-3)
- `phase-6_funders.md` (was phase-4)
- `phase-7_links.md` (was phase-5)
- `phase-8_risk.md` (was phase-6)
- `phase-9_posture.md` (was phase-7c)
- `phase-10_redteam.md` (was phase-7r)
- `phase-11_foresight.md` (was phase-8)

### 3. Makefile Commands
The Makefile has been updated. Use:
- `make build-phase-4 COUNTRY=AT` (was build-phase-2s)
- All `build` and `build-all` commands now use the new phase numbers

### 4. Data Files
Data files in `data/processed/country=*/` follow the new numbering:
- `p7c_*.tsv` files → `p9_*.tsv`
- `p7r_*.tsv` files → `p10_*.tsv`
- `p8_*.tsv` files → `p11_*.tsv`
- `phase5_*.tsv` files → `phase7_*.tsv`
- `phase6_*.tsv` files → `phase8_*.tsv`

### 5. Configuration
- `config/models.yaml`: Changed `phase7c:` to `phase9:`

## Important Notes for ChatGPT

1. **When referencing phases**, always use the NEW phase numbers (0-13)

2. **When running Python scripts**, use the new names:
   ```bash
   python -m src.analysis.phase3_landscape --country AT  # Technology Landscape
   python -m src.analysis.phase4_supply_chain --country AT  # Supply Chain Security
   ```

3. **When creating new reports**, follow the new naming convention:
   ```
   reports/country=XX/phase-N_name.md
   ```
   Where N is the new phase number (0-13)

4. **Phase progression** is now strictly sequential:
   - Phase 0: Foundation (Taxonomy)
   - Phases 1-2: Setup and Data Gathering
   - Phases 3-8: Core Analysis
   - Phases 9-10: Security and Validation
   - Phase 11: Foresight and Predictions
   - Phases 12-13: Extended Analysis and Closeout

5. **Special phases**:
   - Phase 4 (Supply Chain) runs parallel to Phase 3 (Landscape)
   - Phase 9 (PRC/China focus) and Phase 10 (Red Team) are security assessments
   - Phases 12-13 are optional/extended phases

## Quick Reference
When you see references to old phase numbers in documentation or prompts, convert them:
- "Phase X" → "Phase 0"
- "Phase 2S" → "Phase 4"
- "Phase 7C" → "Phase 9"
- "Phase 7R" → "Phase 10"
- All other phases: add 1 to phases 0-1, add 2 to old phases 2-8

## Workflow Remains the Same
The actual analysis workflow and dependencies between phases remain unchanged. Only the numbering has been updated for clarity and logical progression.