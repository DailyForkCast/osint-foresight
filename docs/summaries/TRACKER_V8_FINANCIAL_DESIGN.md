# Tracker v8 - Financial Tracking Design
**Purpose:** Implement sophisticated financial tracking with project lifecycle and country ownership

---

## SCHEMA CHANGES

### **Master_Projects** - New/Modified Columns:

| Column | Description | Formula/Type | Notes |
|--------|-------------|--------------|-------|
| **Proposed_Amount** | Initial funding request | Number | For Proposed projects only |
| Total_Allocation | Approved funding | Number | Manual entry |
| Total_Obligated | Formally committed funds | Number | Manual entry |
| **Total_Spent** | *NEW* | `=SUMIFS(Country_Budgets[Spent_Amount], Country_Budgets[Unique_ID], [@Unique_ID], Country_Budgets[My_Country], TRUE)` | Sum only MY countries |
| **Total_ULO** | *CHANGED* | `=IF([@Total_Obligated]=0, 0, [@Total_Obligated]-[@Total_Spent])` | Obligated - Spent |
| **ULO_Percent** | *CHANGED* | `=IF([@Total_Obligated]=0, 0, [@Total_ULO]/[@Total_Obligated])` | ULO / Obligated |
| **Include_In_Calcs** | *NEW* | `=NOT(OR([@Status]="Proposed", [@Status]="Archived"))` | TRUE if should calculate |

### **Country_Budgets** - New/Modified Columns:

| Column | Description | Formula/Type | Notes |
|--------|-------------|--------------|-------|
| **My_Country** | *NEW* | TRUE/FALSE | Checkbox - Is this my responsibility? |
| Allocated_Amount | Approved for this country | Number | Manual entry |
| Obligated_Amount | Committed for this country | Number | Manual entry |
| **Spent_Amount** | *NEW* | Number | Manual entry |
| **ULO** | *CHANGED* | `=IF([Obligated_Amount]=0, 0, [Obligated_Amount]-[Spent_Amount])` | Obligated - Spent |
| **ULO_Percent** | *CHANGED* | `=IF([Obligated_Amount]=0, 0, [ULO]/[Obligated_Amount])` | ULO / Obligated |
| **Spend_Health** | Status indicator | `=IF([ULO_Percent]>0.8,"🟢",IF([ULO_Percent]>0.5,"🟡","🔴"))` | Green/Yellow/Red |

### **Portfolio_Dashboard** - New Columns:

| Column | Description | Formula | Notes |
|--------|-------------|---------|-------|
| **My_Countries_Count** | *NEW* | `=COUNTIFS(Country_Budgets[Unique_ID], [ProjectID], Country_Budgets[My_Country], TRUE)` | How many are mine |
| **Total_Countries_Count** | *NEW* | `=COUNTIF(Country_Budgets[Unique_ID], [ProjectID])` | How many total |
| **Project_Manager** | *NEW* | Text | From Master_Projects |
| **FAR_Notes** | *NEW* | Text | Fund changes notes |

---

## CALCULATION LOGIC

### **What Gets Included in Rollups:**

```
Include if:
  - Status IN (Active, CN Stage, In Progress, On Hold, Completed)
  AND
  - Country_Budgets.My_Country = TRUE

Exclude if:
  - Status = Proposed (no funds allocated yet)
  - Status = Archived (project completed, archived)
  - Country_Budgets.My_Country = FALSE (not my responsibility)
```

### **ULO Calculation Trigger:**

```
IF Obligated_Amount > 0:
  ULO = Obligated - Spent
  ULO% = ULO / Obligated
ELSE:
  ULO = 0
  ULO% = 0
  Display: "Not Yet Obligated"
```

---

## USER INTERFACE

### **Master_Projects View:**
```
Unique_ID | Project_Name | Status | Proposed_Amount | Total_Allocation | Total_Obligated | Total_Spent | Total_ULO | ULO% | My_Countries
PRJ-001   | Digital...   | Active | -              | $2,000,000       | $1,500,000      | $800,000    | $700,000  | 47%  | 3/5
PRJ-002   | Cyber...     | CN Stage | -            | $1,000,000       | $0              | $0          | $0        | -    | 2/4
PRJ-003   | New Init...  | Proposed | $500,000     | -                | -               | -           | -         | -    | -
```

### **Country_Budgets View:**
```
Project_ID | Country | My_Country | Allocated | Obligated | Spent   | ULO     | ULO% | Health
PRJ-001    | DE      | ✓          | $500,000  | $350,000  | $180,000| $170,000| 49%  | 🟡
PRJ-001    | FR      | ✓          | $300,000  | $195,000  | $95,000 | $100,000| 51%  | 🟡
PRJ-001    | IT      |            | $400,000  | $280,000  | $140,000| $140,000| 50%  | 🟡
PRJ-002    | PL      | ✓          | $250,000  | $0        | $0      | $0      | -    | -
```

### **Portfolio_Dashboard View:**
```
Project | Status  | PM      | My Countries | Total $ (Mine) | Obligated (Mine) | ULO (Mine) | ULO% | FAR Notes
Digital | Active  | Smith   | 3 of 5      | $800,000       | $545,000         | $270,000   | 49%  | NCE +$200K
Cyber   | CN Stage| Jones   | 2 of 4      | $500,000       | $0               | $0         | -    | Initial award
```

---

## IMPLEMENTATION STEPS

### **Step 1: Add New Columns (Structural)**
1. Master_Projects: Add Proposed_Amount, Total_Spent, Include_In_Calcs
2. Country_Budgets: Add My_Country (TRUE/FALSE), Spent_Amount
3. Portfolio_Dashboard: Add My_Countries_Count, Total_Countries_Count, Project_Manager, FAR_Notes

### **Step 2: Update Formulas (Calculation Logic)**
1. Master_Projects:
   - Total_Spent: `=SUMIFS(Country_Budgets[Spent_Amount], Country_Budgets[Unique_ID], [@Unique_ID], Country_Budgets[My_Country], TRUE)`
   - Total_Obligated: `=SUMIFS(Country_Budgets[Obligated_Amount], Country_Budgets[Unique_ID], [@Unique_ID], Country_Budgets[My_Country], TRUE)`
   - Total_ULO: `=[@Total_Obligated]-[@Total_Spent]`
   - ULO_Percent: `=IF([@Total_Obligated]=0, 0, [@Total_ULO]/[@Total_Obligated])`

2. Country_Budgets:
   - ULO: `=E2-F2` (where E=Obligated, F=Spent)
   - ULO_Percent: `=IF(E2=0, 0, G2/E2)` (where G=ULO)

3. Portfolio_Dashboard:
   - Only include rows where Master_Projects[Include_In_Calcs] = TRUE

### **Step 3: Update Conditional Formatting**
1. Add visual indicators for:
   - Proposed projects (gray/italic)
   - My Countries vs All Countries (bold for mine)
   - ULO health (green/yellow/red)

### **Step 4: Create "My Portfolio" View**
- Filtered view showing only projects with at least one "My Country"
- Summary dashboard showing MY totals only

---

## VALIDATION RULES

### **Data Entry Validation:**
1. **Proposed_Amount**: Only allow entry if Status = "Proposed"
2. **Allocated/Obligated/Spent**: Only allow if Status ≠ "Proposed"
3. **Logical checks:**
   - Spent ≤ Obligated
   - Obligated ≤ Allocated
   - If Status = "Proposed", Allocated/Obligated/Spent must be 0

### **Formula Protection:**
1. Calculated columns (ULO, ULO%, totals) should be locked
2. Manual entry columns (Allocated, Obligated, Spent, My_Country) should be unlocked

---

## REPORTING VIEWS

### **View 1: My Active Portfolio**
- Filter: Status IN (Active, In Progress, CN Stage, On Hold)
- Filter: Has at least one My_Country = TRUE
- Columns: Project, Status, My Countries Count, Obligated (Mine), Spent (Mine), ULO (Mine), ULO%

### **View 2: Proposed Projects**
- Filter: Status = "Proposed"
- Columns: Project, Proposed_Amount, Countries, PM, Description

### **View 3: All Projects (Reference)**
- No filter
- Shows all projects, all countries
- My Countries highlighted/bolded

---

## EXAMPLES

### **Example 1: Proposed Project**
```
Project: Infrastructure Modernization
Status: Proposed
Proposed_Amount: $750,000
Total_Allocation: -
Total_Obligated: -
Total_Spent: -
Total_ULO: -
Include_In_Calcs: FALSE
Display: "Proposal: $750,000 requested"
```

### **Example 2: Active Project with Mixed Ownership**
```
Project: Digital Transformation
Status: Active
Countries:
  - Germany (My_Country: TRUE) - Obligated: $350K, Spent: $180K, ULO: $170K
  - France (My_Country: TRUE) - Obligated: $195K, Spent: $95K, ULO: $100K
  - Italy (My_Country: FALSE) - Obligated: $280K, Spent: $140K, ULO: $140K
  - Poland (My_Country: FALSE) - Obligated: $120K, Spent: $60K, ULO: $60K

Master_Projects Rollup (MY COUNTRIES ONLY):
  Total_Obligated: $545,000 (Germany + France only)
  Total_Spent: $275,000
  Total_ULO: $270,000
  ULO%: 49.5%
```

### **Example 3: CN Stage (Not Yet Obligated)**
```
Project: Cybersecurity Enhancement
Status: CN Stage
Total_Allocation: $1,000,000
Total_Obligated: $0
Total_Spent: $0
Total_ULO: $0
Display: "Approved: $1M allocated, awaiting obligation"
```

---

## QUESTIONS TO CONFIRM

1. **Proposed_Amount display:** Should it show in Portfolio Dashboard with special formatting?
2. **My_Country default:** When adding new country to budget, default to TRUE or FALSE?
3. **Archive behavior:** When Status → Archived, keep data visible or hide from main views?
4. **Spent tracking:** Manual entry or integrate with external system?
5. **Multiple PMs:** If project has multiple PMs, how to display? Comma-separated list?

---

## MIGRATION PLAN

### **Existing Data:**
1. Current "ULO" values are wrong (Allocated - Obligated)
2. Need to:
   - Add "Spent_Amount" column → Set to 0 for all existing records
   - Recalculate ULO = Obligated - Spent = Obligated - 0 = Obligated (initially)
   - User must fill in actual Spent amounts

### **User Action Required:**
1. For each project, mark My_Country = TRUE for countries you manage
2. Fill in Spent_Amount for each country budget
3. For Proposed projects, enter Proposed_Amount

---

**Ready to implement? Or do you want to adjust the design first?**
