# Tracker v5 - Planned Updates
**Date:** October 26, 2025
**Base File:** `2025-10-26-Tracker-v4.xlsx`
**Target File:** `2025-10-26-Tracker-v5.xlsx`

---

## PLANNED CHANGES FOR v5

### 1. Funding Format: Thousands → Millions ✓ APPROVED
**Location:** Portfolio_Dashboard sheet

**Current Format:**
```excel
=TEXT(Control!B15,"$#,##0,K")
```
Output: `$5,250,K` (represents $5,250,000)

**New Format:**
```excel
=TEXT(Control!B15,"$#,##0.0,M")
```
Output: `$5.3M` (represents $5,300,000)

**Cells to Update:**
- Portfolio_Dashboard, Row 4, Column D (Total Funding)
- Portfolio_Dashboard, Row 4, Column G (At Risk amount) - if using TEXT formula
- Any other cells displaying budget amounts in TEXT format

**Benefits:**
- More appropriate scale for large project budgets
- Industry standard for multi-million dollar portfolios
- Cleaner, more executive-friendly presentation

---

### 2. Regional_Summary Sheet Build-Out ✓ APPROVED
**Location:** Regional_Summary sheet (currently empty)

**Proposed Structure:**

| Column | Header | Description | Formula Example |
|--------|--------|-------------|-----------------|
| A | Region | Region code | EUR, WHA, EAP, AF, NEA, SCA |
| B | Region_Name | Full region name | Europe, Western Hemisphere, etc. |
| C | Active_Projects | Count of projects in region | `=SUMPRODUCT(--(ISNUMBER(SEARCH(A2,Master_Projects!Countries))))` |
| D | Total_Countries | Countries in this region | `=COUNTIF(Country_Regions!Region,A2)` |
| E | Active_Countries | Countries with budgets | `=SUMPRODUCT((Country_Budgets!Country_Code<>"")*(Country_Regions!Region=A2))` |
| F | Total_Allocated | Sum of allocated funds | `=SUMIFS(Country_Budgets!Allocated_Amount,Country_Regions!Region,A2)` |
| G | Total_Obligated | Sum of obligated funds | `=SUMIFS(Country_Budgets!Obligated_Amount,Country_Regions!Region,A2)` |
| H | Total_Spent | Sum of spent funds | `=SUMIFS(Country_Budgets!Spent_Amount,Country_Regions!Region,A2)` |
| I | ULO_Amount | Unobligated amount | `=F2-G2` |
| J | ULO_Percent | Unobligated percentage | `=IF(F2=0,0,I2/F2)` |
| K | Spend_Rate | Spending percentage | `=IF(G2=0,0,H2/G2)` |
| L | Health_Status | Overall health indicator | Based on ULO% and Spend_Rate |

**Data Rows:**
1. EUR - Europe (44 countries)
2. WHA - Western Hemisphere (34 countries)
3. EAP - East Asia Pacific (17 countries)
4. AF - Africa (10 countries)
5. NEA - Near East Asia (11 countries)
6. SCA - South Central Asia (6 countries)

**Region Full Names:**
- EUR: Europe
- WHA: Western Hemisphere
- EAP: East Asia Pacific
- AF: Africa
- NEA: Near East Asia
- SCA: South Central Asia

**Formatting:**
- Header row: Bold, colored background (matching other sheets)
- Currency columns (F-I): Currency format with millions ($#,##0.0,M) OR standard currency
- Percentage columns (J-K): Percentage format (0.0%)
- Freeze top row
- Auto-filter enabled

**Purpose:**
- Executive-level view of portfolio by geographic region
- Quick identification of regional investment patterns
- Regional performance metrics
- Support for geographic portfolio balancing decisions

---

### 3. Project_Spotlight Redesign ✓ APPROVED
**Location:** Project_Spotlight sheet

**Changes:**

#### A. Remove Formula
- Delete: `=TEXT(Control!B15,Project_Spotlight!G5` (and any reference to this)

#### B. Extend Summary Box Vertically
- **Current:** Summary in B5 (or B5:F5)
- **New:** Summary box extended to B5:F14 (10 rows, 5 columns)
- Gives more space for project description and details

#### C. Target Audiences & Technologies (Side by Side Layout)
**Location:** Rows 5-14

**Left Section - Target Audiences (G5:H14):**
- Column G: Audience Type
- Column H: Description
- Column I: Priority (if available in Project_Audiences sheet)

**Right Section - Target Technologies (J5:K14 or I5:K14 depending on audience columns):**
- Technology columns (name, category, status, etc.)
- Exact structure TBD based on Project_Technologies sheet structure

**Key Requirement:**
- Both lists must be **dynamically filtered** to show only items for the selected project in cell B2
- Use FILTER() formula if Excel 365 available, or INDEX/SMALL/IF array formulas for older Excel

**Example Formula (Excel 365):**
```excel
=FILTER(Project_Audiences!B:D, Project_Audiences!A:A=$B$2, "No audiences assigned")
```

**Example Formula (Excel 2016):**
```excel
=IFERROR(INDEX(Project_Audiences!B:B,SMALL(IF(Project_Audiences!$A:$A=$B$2,ROW(Project_Audiences!$A:$A)),ROW(A1))),"")
```

#### D. Key Deliverables Section
**Location:** Starting at Row 17 (or Row 15/16 with spacing row)

**Structure:** 5 columns
- Column B: Deliverable_Name
- Column C: Due_Date
- Column D: Status
- Column E: Owner
- Column F: Notes

**Rows:** Flexible (10-15 rows to accommodate varying numbers of deliverables)

**Key Requirement:**
- Dynamically filtered to show only deliverables for the selected project in cell B2

**Example Formula (Excel 365):**
```excel
=FILTER(Project_Deliverables!B:F, Project_Deliverables!A:A=$B$2, "No deliverables assigned")
```

**Visual Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Rows 1-4: PROJECT SELECTION & BASIC INFO (existing)            │
├─────────────────────────────┬───────────────────────────────────┤
│ Rows 5-14:                  │ Rows 5-14:                        │
│ B-F: SUMMARY BOX            │ G-I: TARGET AUDIENCES             │
│ (Extended)                  │ J-K: TARGET TECHNOLOGIES          │
│                             │ (Both filtered to selected proj)  │
│ [Project description        │                                   │
│  and details]               │ Audiences:                        │
│                             │ Type | Description | Priority     │
│                             │                                   │
│                             │ Technologies:                     │
│                             │ Name | Category | Status          │
└─────────────────────────────┴───────────────────────────────────┘
│ Row 15: (spacing)                                               │
├─────────────────────────────────────────────────────────────────┤
│ Rows 16+: KEY DELIVERABLES HEADER                              │
│ Rows 17+: DELIVERABLES DATA (filtered to selected project)     │
│                                                                 │
│ Name | Due Date | Status | Owner | Notes                       │
│ Tech Req Doc | 01/15/25 | Done | Smith | Final version        │
│ Beta Release | 02/28/25 | Active | Davis | Testing phase      │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Notes:**
- Clear existing content in affected cells
- Preserve existing country budget table if it's above row 5
- Add section headers: "TARGET AUDIENCES", "TARGET TECHNOLOGIES", "KEY DELIVERABLES"
- Apply formatting (bold headers, borders, etc.)
- Test with different project selections to ensure filtering works

---

## IMPLEMENTATION NOTES

**Order of Operations:**
1. Update funding format in Portfolio_Dashboard (thousands → millions)
2. Build out Regional_Summary sheet with structure and formulas
3. Redesign Project_Spotlight layout (summary box, audiences, technologies, deliverables)
4. Test all formulas with current data
5. Verify no formula breaks
6. (Additional items as identified)

**Testing Checklist:**
- [ ] Portfolio_Dashboard displays amounts in millions correctly
- [ ] Regional_Summary formulas calculate correctly for all 6 regions
- [ ] Regional_Summary totals match Control sheet totals
- [ ] Project_Spotlight summary box extends to B5:F14
- [ ] Project_Spotlight audiences filter correctly by selected project
- [ ] Project_Spotlight technologies filter correctly by selected project
- [ ] Project_Spotlight deliverables filter correctly by selected project
- [ ] No #REF! or #VALUE! errors
- [ ] File opens without corruption warnings
- [ ] All existing features still work

**Excel Table Handling:**
- Check if any sheets being modified have Excel Tables
- If yes, remove tables before structural changes
- Recreate tables after modifications
- (Lesson learned from v3 corruption issue)

---

## VERSION HISTORY CONTEXT

| Version | Key Changes |
|---------|-------------|
| v1 | Milestone/Event IDs, PM column, 98 countries (had bugs) |
| v2 | Bug fixes: unhidden rows, table expansion, Calendar_Todo |
| v3 | Table corruption (don't use) |
| v3-FIXED | Proper table handling, Decision/Risk IDs, Stakeholders 22 cols |
| v4 | Categorized Stakeholder IDs, GB→UK, map removal |
| **v5** | **Millions format, Regional_Summary, Project_Spotlight redesign (planned)** |

---

**Status:** PLANNING IN PROGRESS
**Approved Items:** 3
**Pending Items:** TBD (user reviewing for additional items)
**Ready to Execute:** NO (waiting for user to finalize all requirements)
