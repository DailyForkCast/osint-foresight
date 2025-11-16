# V25 COMPREHENSIVE AUDIT - ACTION ITEMS

## CRITICAL ISSUES (Need Immediate Fixing)

### 1. Regional_Summary - Region Codes Are Mixed Up ❌
**Current State:**
- Row 2: Shows "EUR" (should be "AF")
- Row 3: Shows "WHA" (should be "EAP")
- Row 4: Shows "EAP" (should be "EUR")
- Row 5: Shows "AF" (should be "NEA")
- Row 6: Shows "NEA" (should be "SCA")
- Row 7: Shows "SCA" (should be "WHA")

**Action:** Fix manually in Excel - change column A values in rows 2-7 to correct region codes

---

### 2. Country_Dashboard - Country Name Lookup Has #REF! Error ❌
**Location:** Cell D2
**Current Formula:** `=IFERROR(INDEX(#REF!,MATCH(B2,#REF!,0)),"")`
**Problem:** References missing T_Country_Regions table

**Action:** Can fix programmatically OR manually

---

### 3. Portfolio_Dashboard - Column Headers Don't Match Formulas ❌
**Current Headers (Row 10):**
- Column J: Shows "ULO"
- Column K: Shows "ULO %"
- Column L: Shows "Days Left"

**Actual Formulas Show:**
- Column J: Total_Spent
- Column K: Total_ULO
- Column L: ULO_Percent
- Column M: Days_Remaining

**Action:** Fix column headers manually in row 10

---

### 4. Missing Tables ❌
**Tables Not Found:**
- `T_Country_Regions` (should be in Country_Regions sheet)
- `T_Country_PM_Assignments` (should be in Country_PM_Assignments sheet)

**Impact:**
- Country_Dashboard country name lookup broken (uses T_Country_Regions)
- Any PM assignment lookups won't work

**Action:** Need to create these tables

---

## MISSING FORMULAS (Need Adding)

### 5. Master_Projects Missing Column Z Formula ⚠️
**Column:** Z (Total_Spent)
**Expected Formula:** `=SUMIF(Country_Budgets!$B$2:...,B2,Country_Budgets!$I$2:...)`

**Action:** Add formula to sum spent amounts from Country_Budgets

---

### 6. Master_Projects Missing Column J Formula ⚠️
**Column:** J (Days_Remaining)
**Expected Formula:** `=IF(OR(I2="",E2=""),"",IF(E2="Completed","Complete",INT(I2-TODAY())))`

**Action:** Add formula to calculate days until Project_End_Date

---

## MANUAL WORK REQUIRED

### 7. Stakeholders Section - Manual Entry Required ℹ️
**Location:** Spotlight_PMWorkspace rows 33-42
**Status:** Cleared (no formulas, ready for manual entry)
**Reason:** Complex AGGREGATE formulas had #REF! errors due to table name mismatch

**How to Use:**
1. Select project in B2
2. Manually enter stakeholder details in rows 33-42:
   - Column A: Name
   - Column E: Organization
   - Column G: Role
   - Column H: Email
   - Column I: Engagement Level

---

### 8. Data Validation Dropdowns Not Added ℹ️
**Config_Lists sheet ready with headers:**
- A: Status
- B: Priority
- C: Stage
- D: Country_Code
- E: Country
- F: Region

**Dropdowns Needed:**
1. **Master_Projects:**
   - Column E: Project_Status → Config_Lists!A:A
   - Column F: Project_Priority → Config_Lists!B:B
   - Column N: NCE_Eligible → Yes, No
   - Column O: NCE_Status → None, NCE 1 Requested, NCE 1 Approved, NCE 1 Denied, NCE 2 Requested, NCE 2 Approved, NCE 2 Denied

2. **Country_Budgets:**
   - Column D: Country_Code → Config_Lists!D:D

3. **Spotlight_PMWorkspace:**
   - Cell B2: Project_Unique_ID → T_Master_Projects[Project_Unique_ID]

**Action:** Add manually in Excel using Data > Data Validation

---

### 9. Stakeholder Categorization Note ℹ️
**Location:** Stakeholders sheet
**Status:** Not added (would break table if done programmatically)

**Suggested Note Text (add in cell J1 or K1):**
```
STAKEHOLDER CATEGORIZATION GUIDE:

Government Officials: Gov agency contacts, embassy staff, ministry officials
Implementing Partners: Contractors, grantees, vendors executing project work
Internal Team: DOS staff, project managers, technical advisors
Beneficiaries: End users, communities, target populations
Oversight: Congress, GAO, OIG, monitoring entities

Stakeholder_ID Format: ProjectID-STK-001, ProjectID-STK-002, etc.
```

**Action:** Add manually in Excel - type in cell J1, format with yellow background, wrap text

---

## WHAT'S WORKING WELL ✅

### Formulas Present and Working:
1. **Control Sheet** - All metrics formulas working
2. **Master_Projects** - Most formulas present:
   - POP_Days_Remaining ✅
   - Total_Proposed ✅
   - Total_Allocation ✅
   - Total_Obligated ✅
   - Total_ULO ✅
   - ULO_Percent ✅
   - Countries (array formula) ✅
   - Country_Count ✅

3. **Country_Budgets** - Formulas working:
   - Budget_ID auto-generation ✅
   - Country_Code lookup ✅
   - ULO calculation ✅
   - ULO_Percent ✅
   - Budget_Status ✅

4. **Portfolio_Dashboard** - All formulas present and working ✅
   - Auto-incrementing with ROW()
   - Blank row handling (no zeros displayed)
   - All 13 columns have formulas

5. **Spotlight_PMWorkspace** - Most sections working:
   - Award Number / NCE fields ✅
   - POP dates ✅
   - Project details ✅
   - Financial summary ✅
   - Deliverables ✅
   - Documents ✅
   - Audiences ✅
   - Technologies ✅

6. **Country_Dashboard** - Project list filtering working ✅
7. **Regional_Summary** - Formulas working (just need to fix region codes) ✅

### Tables Present and Working:
- T_Master_Projects ✅
- T_Country_Budgets ✅
- T_Stakeholders ✅
- T_Project_Deliverables ✅
- T_Project_Audiences ✅
- T_Project_Technologies ✅
- T_Project_Documents ✅

---

## PRIORITY ORDER

### PRIORITY 1 - Critical Fixes (Can Do Programmatically):
1. Fix Regional_Summary region codes
2. Add missing Master_Projects formulas (columns J, Z)
3. Create T_Country_Regions table
4. Fix Country_Dashboard D2 formula
5. Fix Portfolio_Dashboard column headers

### PRIORITY 2 - Manual Work:
6. Add data validation dropdowns
7. Add stakeholder categorization note
8. Create T_Country_PM_Assignments table if needed
9. Populate Config_Lists with values

### PRIORITY 3 - Optional Enhancements:
10. Add stakeholder formulas back (if desired)
11. Add more data validation rules
12. Add conditional formatting for status indicators

---

## NEXT STEPS

**Option A - I Can Fix Priority 1 Items:**
Create v26 with:
- Correct region codes in Regional_Summary
- Missing formulas in Master_Projects
- T_Country_Regions table created
- Fixed Country_Dashboard country lookup
- Corrected Portfolio_Dashboard headers

**Option B - You Fix Manually:**
Open v25 and make the corrections yourself using this guide

**Option C - Hybrid:**
I fix the programmatic issues (Priority 1), you handle the manual work (Priority 2-3)

Which approach would you prefer?
