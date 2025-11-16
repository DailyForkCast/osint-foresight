# v6 to v6.3 - Complete Implementation Guide
**All Manual Changes to Apply to Tracker v6**

---

## OVERVIEW

Starting file: `2025-10-26-Tracker-v6.xlsx`
Save as: `2025-10-26-Tracker-v6.3.xlsx` (when complete)

**Estimated time:** 35-45 minutes
**Difficulty:** Easy (all manual Excel edits)

---

## IMPORTANT: Named Ranges for Data Validation

**Excel Limitation:** Data validation doesn't support table structured references like `Master_Projects[Unique_ID]` directly. You must use **Named Ranges** instead.

### Named Ranges You'll Need:

**Already exist in v6:**
- `List_Status` → Points to status options (works in validation)
- `List_Priority` → Points to priority options (works in validation)
- `List_CountryCodes` → Points to country codes (works in validation)
- `L_NCE_Status` → Points to NCE status options (works in validation)

**Need to CREATE (in Change 1):**
- `List_Project_IDs` → Must point to `=Master_Projects[Unique_ID]`

### The Rule:

✓ **In regular formulas:** Use table references (`Master_Projects[Unique_ID]`) - works perfectly
✗ **In data validation:** Use named ranges (`List_Project_IDs`) - Excel requirement

**Bottom line:** Any time you see `=Master_Projects[Unique_ID]` in a data validation source, it needs to be `=List_Project_IDs` instead. We'll create this named range in Change 1.

---

## TABLE OF CONTENTS

1. [Critical: Add Data Validation to Project_Spotlight](#change-1-add-data-validation-to-project_spotlight)
2. [Add Project Manager to Project_Spotlight](#change-2-add-project-manager-to-project_spotlight)
3. [Auto-populate Implementer POC Email](#change-3-auto-populate-implementer-poc-email)
4. [Add Missing Countries](#change-4-add-missing-countries)
5. [Update Budget Columns (Rename + Add Spent)](#change-5-update-budget-columns)
6. [Connect New Sheets to Master_Projects](#change-6-connect-new-sheets-to-master_projects)
7. [Add PM Summary Sheet (Optional)](#change-7-add-pm-summary-sheet-optional)

---

## CHANGE 1: Add Data Validation to Project_Spotlight
**Priority:** CRITICAL | **Time:** 3 minutes

### Important Note:
Excel data validation doesn't support table structured references directly. We need to create a **Named Range** first.

### Part A: Create Named Range (Do This First)

1. Go to **Formulas** tab → **Name Manager** → **New**
2. In the "New Name" dialog:
   - **Name:** `List_Project_IDs`
   - **Refers to:** `=Master_Projects[Unique_ID]`
3. Click **OK**
4. Click **Close** to exit Name Manager

**What this does:** Creates a named reference that points to the Unique_ID column in Master_Projects table. This auto-expands when you add projects.

### Part B: Add Data Validation to Project_Spotlight

**Location:** Project_Spotlight Sheet, Cell B2

1. Go to **Project_Spotlight** sheet
2. Click cell **B2**
3. Go to **Data** tab → **Data Validation**
4. Settings:
   - **Allow:** List
   - **Source:** `=List_Project_IDs` (use the named range, NOT the table reference)
   - **Ignore blank:** Unchecked
5. Input Message tab (optional):
   - **Title:** Project Selection
   - **Message:** Select a project from the list
6. Click **OK**

### Test:
- Click B2 - should see dropdown arrow
- Click dropdown - should show all project IDs (PRJ-001, PRJ-002, etc.)
- If you get an error, verify the named range was created correctly (Formulas → Name Manager)

---

## CHANGE 2: Add Project Manager to Project_Spotlight
**Priority:** HIGH | **Time:** 2 minutes

### Location: Project_Spotlight Sheet

### Add PM Display

**Option A: Add to Summary Section (Recommended)**

**Cell B4:** (Insert row if needed, or use existing row 4)
```
Project Manager:
```

**Cell C4:**
```
=IFERROR(INDEX(Master_Projects[Project_Manager],MATCH($B$2,Master_Projects[Unique_ID],0)),"No PM Assigned")
```

**Option B: Add Below Project Name**

If you prefer it right after project name in the summary box:

**Cell B5:**
```
PM:
```

**Cell C5:**
```
=IFERROR(INDEX(Master_Projects[Project_Manager],MATCH($B$2,Master_Projects[Unique_ID],0)),"")
```

### Test:
- Select different projects in B2
- PM name should update automatically

---

## CHANGE 3: Auto-populate Implementer POC Email
**Priority:** HIGH | **Time:** 2 minutes

### Location: Master_Projects Sheet

### The Issue:
- Column K: Implementer (organization name)
- Column L: Implementer_POC (person's name)
- Column M: Implementer_POC_Email (currently manual entry)

**Goal:** When you enter a POC name in column L, their email auto-populates in column M from the Stakeholders sheet.

**Note:** Implementer (K) and Project_Manager (Z) are different people/roles.

### Steps:

**M2 Formula:**
```
=IFERROR(XLOOKUP(L2,Stakeholders[Name],Stakeholders[Email],""),"")
```

**Or without XLOOKUP (works in all Excel versions):**
```
=IFERROR(INDEX(Stakeholders[Email],MATCH(L2,Stakeholders[Name],0)),"")
```

**Copy down:** M2 to M1000

### How It Works:
1. You enter POC name in column L (e.g., "John Doe")
2. Formula looks up "John Doe" in Stakeholders sheet
3. Returns their email from Stakeholders[Email] column
4. If person not found in Stakeholders, shows blank

### Prerequisites:
- POC must exist in Stakeholders sheet with their email
- Name in column L must EXACTLY match name in Stakeholders[Name]
- Stakeholders[Email] must have data

### Test:
1. Go to Stakeholders sheet
2. Add a test person:
   - Name: "Test POC"
   - Email: "testpoc@example.com"
3. Go to Master_Projects
4. In any row, column L, type: "Test POC"
5. Column M should auto-populate with: "testpoc@example.com"

### Important Notes:
- **Name matching is case-sensitive**
- If name in L2 doesn't exist in Stakeholders, M2 will be blank
- Update Stakeholders sheet first before entering POC names
- This ensures Implementer POC emails stay current automatically

---

## CHANGE 4: Add Missing Countries
**Priority:** HIGH | **Time:** 5 minutes

### Missing Countries:
- MU - Mauritius (Africa)
- NA - Namibia (Africa)
- OM - Oman (Near East Asia)
- MD - Moldova (check if in Config_Lists)

### Part A: Add to Country_Regions Sheet

1. Go to **Country_Regions** sheet
2. Find last row with data (around row 99)
3. Add these rows:

**Row 100:**
- A100: `MU`
- B100: `Mauritius`
- C100: `AF`

**Row 101:**
- A101: `NA`
- B101: `Namibia`
- C101: `AF`

**Row 102:**
- A102: `OM`
- B102: `Oman`
- C102: `NEA`

### Part B: Add to Config_Lists Sheet

1. Go to **Config_Lists** sheet
2. Scroll to Country section (columns D, E, F)
3. Find last row with country data (around row 101)
4. Add these rows:

**Next available row (likely 102):**
- D: `MU` | E: `Mauritius` | F: `AF`

**Next row (likely 103):**
- D: `NA` | E: `Namibia` | F: `AF`

**Next row (likely 104):**
- D: `OM` | E: `Oman` | F: `NEA`

### Part C: Check Moldova

1. In **Config_Lists**, search column D for "MD"
2. If NOT found, add:
   - D: `MD` | E: `Moldova` | F: `EUR`

### Test:
- Go to any sheet with country dropdowns
- Click dropdown - should now see 101 countries including new ones

---

## CHANGE 5: Update Budget Columns
**Priority:** HIGH | **Time:** 5 minutes

### Location: Country_Budgets Sheet

### Part A: Rename Existing Columns

**G1:** Change from "ULO" to:
```
Unobligated
```

**H1:** Change from "ULO_Percent" to:
```
Unobligated_%
```

*(Formulas in G2 and H2 remain unchanged)*

### Part B: Add New Column Headers

**J1:**
```
Spent_Amount
```

**K1:**
```
ULO
```

**L1:**
```
ULO_%
```

### Part C: Add Formulas

**K2:**
```
=F2-J2
```

**L2:**
```
=IF(F2=0,0,K2/F2)
```

**Copy down:**
1. Select K2:L2
2. Copy (Ctrl+C)
3. Select K2:L5000
4. Paste (Ctrl+V)

### Part D: Format Columns

**Column J (Spent_Amount):**
- Select entire column J
- Format as Currency: `$#,##0`

**Column K (ULO):**
- Select entire column K
- Format as Currency: `$#,##0`

**Column L (ULO_%):**
- Select entire column L
- Format as Percentage: `0.0%`

### Part E: Enter Spent Data (Optional - can do later)

**Column J:** Enter actual spent amounts if you have the data
- Leave blank for now if you don't have it
- Formulas will calculate correctly once data is entered

### Final Column Structure:

| Col | Header | Formula | Meaning |
|-----|--------|---------|---------|
| E | Allocated_Amount | [Data] | Total budget |
| F | Obligated_Amount | [Data] | Committed |
| G | **Unobligated** | =E2-F2 | Not yet committed |
| H | **Unobligated_%** | =IF(E2=0,0,G2/E2) | % not committed |
| I | Spend_Health | =H2 | Health metric |
| J | Spent_Amount | [Data] | Actually paid |
| K | **ULO** | =F2-J2 | Unliquidated (committed not paid) |
| L | **ULO_%** | =IF(F2=0,0,K2/F2) | % unliquidated |

### Test:
1. Enter test data in row 2:
   - E2: 1000000
   - F2: 750000
   - J2: 500000
2. Check calculations:
   - G2 = 250000 (Unobligated)
   - H2 = 25.0%
   - K2 = 250000 (ULO)
   - L2 = 33.3%

---

## CHANGE 6: Connect New Sheets to Master_Projects
**Priority:** MEDIUM | **Time:** 10 minutes

### Location: Master_Projects Sheet

### Add Count Columns After Column Z

**Column AA - Audience_Count:**

**AA1 Header:**
```
Audience_Count
```

**AA2 Formula:**
```
=COUNTIF(T_Project_Audiences[Project_ID],B2)
```

**Copy down:** AA2 to AA1000

---

**Column AB - Technology_Count:**

**AB1 Header:**
```
Technology_Count
```

**AB2 Formula:**
```
=COUNTIF(Project_Technologies[Project_ID],B2)
```

**Copy down:** AB2 to AB1000

---

**Column AC - Deliverable_Count:**

**AC1 Header:**
```
Deliverable_Count
```

**AC2 Formula:**
```
=COUNTIF(T_Project_Deliverables[Project_ID],B2)
```

**Copy down:** AC2 to AC1000

---

**Column AD - Deliverable_Completed:**

**AD1 Header:**
```
Deliverable_Completed
```

**AD2 Formula:**
```
=COUNTIFS(T_Project_Deliverables[Project_ID],B2,T_Project_Deliverables[Status],"Completed")
```

**Copy down:** AD2 to AD1000

---

**Column AE - Deliverable_Completion_Rate:**

**AE1 Header:**
```
Deliverable_Completion_Rate
```

**AE2 Formula:**
```
=IF(AC2=0,0,AD2/AC2)
```

**Format as:** Percentage

**Copy down:** AE2 to AE1000

---

### Add to Portfolio_Dashboard (Optional but Recommended)

### Location: Portfolio_Dashboard Sheet

Find empty area (suggest row 30) and add:

**A30:**
```
PROJECT DETAILS SUMMARY
```

**A32:**
```
Total Target Audiences:
```

**B32:**
```
=COUNTA(T_Project_Audiences[Project_ID])
```

**A33:**
```
Total Technologies:
```

**B33:**
```
=COUNTA(Project_Technologies[Project_ID])
```

**A34:**
```
Total Deliverables:
```

**B34:**
```
=COUNTA(T_Project_Deliverables[Project_ID])
```

**A35:**
```
Completed Deliverables:
```

**B35:**
```
=COUNTIF(T_Project_Deliverables[Status],"Completed")
```

**A36:**
```
Deliverable Completion Rate:
```

**B36:**
```
=IF(B34=0,0,B35/B34)
```

**Format B36 as:** Percentage

### Test:
- Check Master_Projects columns AA-AE show counts
- Check Portfolio_Dashboard shows totals

---

## CHANGE 7: Add PM Summary Sheet (Optional)
**Priority:** LOW | **Time:** 10 minutes

This shows each PM once with all their countries (no duplicates).

### Create New Sheet

1. Right-click on sheet tabs
2. Insert → Worksheet
3. Name it: `PM_Summary`
4. Move it after Master_Projects

### Add Headers

**Row 1:**
- A1: `Project_Manager`
- B1: `Countries`
- C1: `Country_Count`
- D1: `Total_Projects`

**Format row 1:** Bold, fill color

### Add Data

**Option A: Manual Entry (Simplest)**

1. In column A, type each PM's name (one per row)
2. In column B, type their countries separated by commas (e.g., "US, CA, MX")
3. In column C2, add formula:
```
=COUNTIF(Master_Projects[Project_Manager],A2)
```
4. In column D2, manually count countries or use:
```
=LEN(B2)-LEN(SUBSTITUTE(B2,",",""))+1
```

**Option B: Excel 365 Formula (Auto-updates)**

If you have Excel 365:

**A2:**
```
=SORT(UNIQUE(FILTER(Master_Projects[Project_Manager],Master_Projects[Project_Manager]<>"")))
```

**C2:**
```
=COUNTIF(Master_Projects[Project_Manager],A2)
```

**Copy C2 down** for each PM

**B2:** (Manually type countries for now, or leave for later)

### Example Output:

| Project_Manager | Countries | Country_Count | Total_Projects |
|----------------|-----------|---------------|----------------|
| Amy Johnson | AT, BE, NL | 3 | 2 |
| Bob Smith | US, CA, MX | 3 | 4 |

### Test:
- Each PM appears only once
- Country_Count matches number of projects they manage

---

## COMPLETE CHECKLIST

Use this to track your progress:

### Critical (Must Do):
- [ ] 1. Add data validation to Project_Spotlight B2
- [ ] 2. Add Project Manager display to Project_Spotlight
- [ ] 3. Auto-populate Implementer POC Email (Master_Projects column M)
- [ ] 4. Add 3 missing countries to Country_Regions
- [ ] 4b. Add 3 missing countries to Config_Lists
- [ ] 4c. Check Moldova in Config_Lists
- [ ] 5. Rename budget columns (Unobligated)
- [ ] 5b. Add Spent_Amount column (J)
- [ ] 5c. Add ULO formula (K)
- [ ] 5d. Add ULO_% formula (L)

### Important (Should Do):
- [ ] 6. Add Audience_Count to Master_Projects (AA)
- [ ] 6b. Add Technology_Count to Master_Projects (AB)
- [ ] 6c. Add Deliverable_Count to Master_Projects (AC)
- [ ] 6d. Add Deliverable_Completed to Master_Projects (AD)
- [ ] 6e. Add Deliverable_Completion_Rate to Master_Projects (AE)

### Optional (Nice to Have):
- [ ] 6f. Add summary statistics to Portfolio_Dashboard
- [ ] 7. Create PM_Summary sheet

---

## SAVING YOUR WORK

### After Completing Changes:

1. **Review** all changes - test formulas
2. **Save As** → `2025-10-26-Tracker-v6.3.xlsx`
3. **Keep v6** as backup (don't overwrite it)
4. **Test thoroughly:**
   - Project_Spotlight: Select different projects, check data updates
   - Country dropdowns: Verify new countries appear
   - Budget calculations: Check formulas calculate correctly
   - Master_Projects counts: Verify audience/tech/deliverable counts

---

## FORMULA QUICK REFERENCE

Copy-paste ready formulas:

### Project_Spotlight (PM Display):
```
=IFERROR(INDEX(Master_Projects[Project_Manager],MATCH($B$2,Master_Projects[Unique_ID],0)),"")
```

### Country_Budgets:
```
K2: =F2-J2
L2: =IF(F2=0,0,K2/F2)
```

### Master_Projects (POC Email Auto-populate):
```
M2: =IFERROR(INDEX(Stakeholders[Email],MATCH(L2,Stakeholders[Name],0)),"")
```

### Master_Projects (Count Columns):
```
AA2: =COUNTIF(T_Project_Audiences[Project_ID],B2)
AB2: =COUNTIF(Project_Technologies[Project_ID],B2)
AC2: =COUNTIF(T_Project_Deliverables[Project_ID],B2)
AD2: =COUNTIFS(T_Project_Deliverables[Project_ID],B2,T_Project_Deliverables[Status],"Completed")
AE2: =IF(AC2=0,0,AD2/AC2)
```

### Portfolio_Dashboard:
```
B32: =COUNTA(T_Project_Audiences[Project_ID])
B33: =COUNTA(Project_Technologies[Project_ID])
B34: =COUNTA(T_Project_Deliverables[Project_ID])
B35: =COUNTIF(T_Project_Deliverables[Status],"Completed")
B36: =IF(B34=0,0,B35/B34)
```

---

## REGION CODES REFERENCE

For adding countries:

- **AF** = Africa
- **EUR** = Europe
- **WHA** = Western Hemisphere
- **EAP** = East Asia Pacific
- **NEA** = Near East Asia
- **SCA** = South Central Asia

---

## TROUBLESHOOTING

### Data validation not working:
- Check that Master_Projects table exists
- Verify named range List_CountryCodes exists (Formulas → Name Manager)

### Formulas showing #REF! error:
- Check table names are correct (T_Project_Audiences, Project_Technologies, etc.)
- Verify sheet names match exactly

### Country dropdowns don't show new countries:
- Make sure you added to BOTH Country_Regions AND Config_Lists
- Check named range List_CountryCodes includes new rows

### Budget formulas showing wrong values:
- Check that column J (Spent_Amount) has data or is blank (not formulas)
- Verify column references (E, F, J) are correct

---

## AFTER COMPLETION

Once you've made all changes:

1. **Document what you changed** in _SETUP sheet notes section
2. **Test with real data** - enter a few actual values
3. **Share v6.3** with team (if applicable)
4. **Keep v6 as backup** - don't delete it

---

## ESTIMATED TIMELINE

| Task Group | Time | Priority |
|------------|------|----------|
| Changes 1-2 (Validation + PM display) | 3 min | Critical |
| Change 3 (POC Email auto-populate) | 2 min | High |
| Change 4 (Countries) | 5 min | High |
| Change 5 (Budget columns) | 5 min | High |
| Change 6 (Connect sheets) | 10 min | Medium |
| Change 7 (PM Summary) | 10 min | Optional |
| **Total** | **35 min** | |

**With testing:** 45 minutes total

---

## SUMMARY OF BENEFITS

After implementing all changes, you'll have:

✓ **Project_Spotlight** with dropdown and PM display
✓ **Auto-populated POC emails** (no more manual entry)
✓ **101 countries** (instead of 98)
✓ **Clear budget tracking** (Unobligated vs ULO)
✓ **Complete spending visibility** (Allocated → Obligated → Spent)
✓ **Project scope metrics** (audience, technology, deliverable counts)
✓ **PM accountability** (optional PM_Summary sheet)

---

**Ready to start? Begin with Change 1 (data validation) - it's the quickest and most critical!**
