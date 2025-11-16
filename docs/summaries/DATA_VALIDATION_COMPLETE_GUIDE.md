# Complete Data Validation Guide
**For Tracker v6/v6.1**

All data validation rules that should be applied across the workbook.

---

## HOW TO ADD DATA VALIDATION IN EXCEL

1. Select the cell(s) you want to validate
2. Go to **Data tab → Data Validation**
3. In the dialog:
   - **Allow:** List (for dropdowns)
   - **Source:** Type the formula or range shown below
4. Click OK

---

## NAMED RANGES (Already Defined - Use These)

These are already in the workbook. Reference them with `=NamedRange` in validation:

| Named Range | Points To | Items |
|-------------|-----------|-------|
| `List_Status` | Config_Lists!$A$2:$A$10 | 6 status values |
| `List_Priority` | Config_Lists!$B$2:$B$6 | 4 priority values |
| `List_CountryCodes` | T_Config_Lists[Country_Code] | 101 countries |
| `L_NCE_Status` | Config_Lists!$G$2:$G$4 | 3 NCE status values |

---

## 1. PROJECT_SPOTLIGHT SHEET

### B2 - Project Selection (CRITICAL - THIS IS THE MISSING ONE)

**Cell:** `B2`

**Type:** List

**Source:** `=Master_Projects[Unique_ID]`

**Purpose:** Dropdown to select which project to display

**How to add:**
1. Click cell B2
2. Data → Data Validation
3. Allow: List
4. Source: `=Master_Projects[Unique_ID]`
5. OK

---

## 2. MASTER_PROJECTS SHEET

### E2:E1000 - Status

**Cells:** `E2:E1000` (entire Status column)

**Type:** List

**Source:** `=List_Status`

**Values:** Not Started, Planning, In Progress, On Hold, Completed, Cancelled

---

### F2:F1000 - Priority

**Cells:** `F2:F1000` (entire Priority column)

**Type:** List

**Source:** `=List_Priority`

**Values:** Critical, High, Medium, Low

---

### X2:X1000 - NCE_Status

**Cells:** `X2:X1000` (entire NCE_Status column)

**Type:** List

**Source:** `=L_NCE_Status`

**Values:** Eligible, Not Eligible, In Review

---

## 3. COUNTRY_BUDGETS SHEET

### C2:C5000 - Country_Code

**Cells:** `C2:C5000` (entire Country_Code column)

**Type:** List

**Source:** `=List_CountryCodes`

**Purpose:** Dropdown with all 101 country codes (US, DE, FR, etc.)

---

### B2:B5000 - Unique_ID (Project ID)

**Cells:** `B2:B5000` (entire Unique_ID column)

**Type:** List

**Source:** `=Master_Projects[Unique_ID]`

**Purpose:** Link budget to a project

---

## 4. MILESTONES SHEET

### C2:C5000 - Unique_ID (Project ID)

**Cells:** `C2:C5000` (entire Unique_ID column)

**Type:** List

**Source:** `=Master_Projects[Unique_ID]`

**Purpose:** Link milestone to a project

---

### E2:E5000 - Status

**Cells:** `E2:E5000` (entire Status column)

**Type:** List

**Source:** `=List_Status`

---

### F2:F5000 - Phase

**Cells:** `F2:F5000` (entire Phase column)

**Type:** List

**Source:** `=Config_Lists!$C$2:$C$5`

**Values:** Planning, Execution, Monitoring, Closeout

---

### G2:G5000 - Priority

**Cells:** `G2:G5000` (entire Priority column)

**Type:** List

**Source:** `=List_Priority`

---

## 5. EVENTS SHEET

### C2:C2000 - Unique_ID (Project ID)

**Cells:** `C2:C2000` (entire Unique_ID column)

**Type:** List

**Source:** `=Master_Projects[Unique_ID]`

**Purpose:** Link event to a project

---

### F2:F2000 - Status

**Cells:** `F2:F2000` (entire Status column)

**Type:** List

**Source:** `=List_Status`

---

## 6. STAKEHOLDERS SHEET

### C2:C1000 - Title/Role

**Cells:** `C2:C1000` (entire Title column)

**Type:** List (optional)

**Source:** You could create a list in Config_Lists, or leave free-text

**Common values:** Project Manager, Technical Lead, Finance Officer, Analyst, etc.

---

### F2:F1000 - Location_Country

**Cells:** `F2:F1000` (entire Location_Country column)

**Type:** List

**Source:** `=List_CountryCodes`

**Purpose:** Country where stakeholder is located

---

### K2:K1000 - Stakeholder_Type

**Cells:** `K2:K1000` (entire Stakeholder_Type column)

**Type:** List

**Source:** Create list in Config_Lists or use: `Internal,External,Partner,Contractor,Government`

---

## 7. RISK_REGISTER SHEET

### B2:B2000 - Unique_ID (Project ID)

**Cells:** `B2:B2000` (entire Unique_ID column)

**Type:** List

**Source:** `=Master_Projects[Unique_ID]`

---

### E2:E2000 - Status

**Cells:** `E2:E2000` (entire Status column)

**Type:** List

**Source:** `=List_Status`

---

### F2:F2000 - Priority

**Cells:** `F2:F2000` (entire Priority column)

**Type:** List

**Source:** `=List_Priority`

---

## 8. DECISION_LOG SHEET

### B2:B2000 - Unique_ID (Project ID)

**Cells:** `B2:B2000` (entire Unique_ID column)

**Type:** List

**Source:** `=Master_Projects[Unique_ID]`

---

### E2:E2000 - Status

**Cells:** `E2:E2000` (entire Status column)

**Type:** List

**Source:** `=List_Status`

---

## 9. PROJECT_AUDIENCES SHEET

### A2:A1000 - Project_ID

**Cells:** `A2:A1000` (entire Project_ID column)

**Type:** List

**Source:** `=Master_Projects[Unique_ID]`

---

## 10. PROJECT_TECHNOLOGIES SHEET

### A2:A1000 - Project_ID

**Cells:** `A2:A1000` (entire Project_ID column)

**Type:** List

**Source:** `=Master_Projects[Unique_ID]`

---

## 11. PROJECT_DELIVERABLES SHEET

### A2:A2000 - Project_ID

**Cells:** `A2:A2000` (entire Project_ID column)

**Type:** List

**Source:** `=Master_Projects[Unique_ID]`

---

### D2:D2000 - Status

**Cells:** `D2:D2000` (entire Status column)

**Type:** List

**Source:** `=List_Status`

---

## QUICK REFERENCE TABLE

| Sheet | Column | Validation Source |
|-------|--------|------------------|
| **Project_Spotlight** | **B2** | **=Master_Projects[Unique_ID]** ← MOST IMPORTANT |
| Master_Projects | E (Status) | =List_Status |
| Master_Projects | F (Priority) | =List_Priority |
| Master_Projects | X (NCE_Status) | =L_NCE_Status |
| Country_Budgets | B (Unique_ID) | =Master_Projects[Unique_ID] |
| Country_Budgets | C (Country_Code) | =List_CountryCodes |
| Milestones | C (Unique_ID) | =Master_Projects[Unique_ID] |
| Milestones | E (Status) | =List_Status |
| Milestones | F (Phase) | =Config_Lists!$C$2:$C$5 |
| Milestones | G (Priority) | =List_Priority |
| Events | C (Unique_ID) | =Master_Projects[Unique_ID] |
| Events | F (Status) | =List_Status |
| Stakeholders | F (Location_Country) | =List_CountryCodes |
| Risk_Register | B (Unique_ID) | =Master_Projects[Unique_ID] |
| Risk_Register | E (Status) | =List_Status |
| Risk_Register | F (Priority) | =List_Priority |
| Decision_Log | B (Unique_ID) | =Master_Projects[Unique_ID] |
| Decision_Log | E (Status) | =List_Status |
| Project_Audiences | A (Project_ID) | =Master_Projects[Unique_ID] |
| Project_Technologies | A (Project_ID) | =Master_Projects[Unique_ID] |
| Project_Deliverables | A (Project_ID) | =Master_Projects[Unique_ID] |
| Project_Deliverables | D (Status) | =List_Status |

---

## PRIORITY ORDER (If you're short on time)

1. **Project_Spotlight B2** ← DO THIS FIRST (critical for your FILTER formulas)
2. Master_Projects E, F, X
3. Country_Budgets B, C
4. All Project_ID columns in data sheets
5. All Status columns
6. All Priority columns

---

## CONFIG_LISTS SHEET REFERENCE

Here's what's available in Config_Lists:

| Column | Header | Range for Validation | Count |
|--------|--------|---------------------|-------|
| A | Status | Config_Lists!$A$2:$A$10 | 6 items |
| B | Priority | Config_Lists!$B$2:$B$6 | 4 items |
| C | Phase | Config_Lists!$C$2:$C$5 | 4 items |
| D | Country_Code | T_Config_Lists[Country_Code] | 101 items |
| E | Country_Name | (reference only) | 101 items |
| F | Region | (reference only) | 101 items |
| G | NCE_Status | Config_Lists!$G$2:$G$4 | 3 items |

---

## BULK APPLY METHOD (Faster)

Instead of doing one cell at a time, you can select entire columns:

**Example: Apply validation to ALL projects in Master_Projects Status column:**

1. Click column header **E** (selects entire column)
2. Or select `E2:E1000` specifically
3. Data → Data Validation
4. Allow: List
5. Source: `=List_Status`
6. OK

This applies to all cells at once!

---

## TESTING

After adding validations, test:

1. **Project_Spotlight B2** - Should show dropdown with all project IDs
2. Click any cell with validation - should show dropdown arrow
3. Try to type invalid data - should reject it

---

## IF VALIDATION ISN'T WORKING

**Symptom:** No dropdown appears

**Possible causes:**
1. Cell is locked and sheet is protected → Unprotect sheet
2. Named range doesn't exist → Check Formulas → Name Manager
3. Typo in validation source → Double-check spelling
4. Source range is empty → Check Config_Lists has data

**To check named ranges:**
1. Formulas tab → Name Manager
2. Look for List_Status, List_Priority, etc.
3. If missing, create them pointing to Config_Lists columns

---

## NOTES

- Named ranges automatically created from Config_Lists table
- Use table references (e.g., `Master_Projects[Unique_ID]`) - they auto-expand
- Apply validation to large ranges (E2:E1000) to accommodate growth
- Data validation doesn't prevent copy/paste - it's just a helper UI

