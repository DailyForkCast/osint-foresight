# Sheet Connections to Add Manually
**For Tracker v6**

These formulas will connect your new sheets (Project_Audiences, Project_Technologies, Project_Deliverables) to Master_Projects and Portfolio_Dashboard.

---

## CURRENT STATUS

✓ **Project_Spotlight** - Already connected to all three sheets (Audiences, Technologies, Deliverables)

✗ **Master_Projects** - Not connected yet (needs count columns)

✗ **Portfolio_Dashboard** - Not connected yet (needs summary statistics)

---

## 1. MASTER_PROJECTS - Add Count Columns

Add these columns after column Z (Project_Manager) to show how many items each project has:

### Column AA: Audience_Count

**Header (AA1):** `Audience_Count`

**Formula (AA2):**
```
=COUNTIF(T_Project_Audiences[Project_ID],B2)
```

**Copy down to:** AA2:AA1000

**What it does:** Counts how many target audiences are defined for this project

---

### Column AB: Technology_Count

**Header (AB1):** `Technology_Count`

**Formula (AB2):**
```
=COUNTIF(Project_Technologies[Project_ID],B2)
```

**Copy down to:** AB2:AB1000

**What it does:** Counts how many technologies are defined for this project

---

### Column AC: Deliverable_Count

**Header (AC1):** `Deliverable_Count`

**Formula (AC2):**
```
=COUNTIF(T_Project_Deliverables[Project_ID],B2)
```

**Copy down to:** AC2:AC1000

**What it does:** Counts total deliverables for this project

---

### Column AD: Deliverable_Completed

**Header (AD1):** `Deliverable_Completed`

**Formula (AD2):**
```
=COUNTIFS(T_Project_Deliverables[Project_ID],B2,T_Project_Deliverables[Status],"Completed")
```

**Copy down to:** AD2:AD1000

**What it does:** Counts how many deliverables are completed

---

### Column AE: Deliverable_Completion_Rate

**Header (AE1):** `Deliverable_Completion_Rate`

**Formula (AE2):**
```
=IF(AC2=0,0,AD2/AC2)
```

**Format:** Percentage (0%)

**Copy down to:** AE2:AE1000

**What it does:** Shows percentage of deliverables completed (e.g., 60%)

---

## 2. PORTFOLIO_DASHBOARD - Add Summary Statistics

Add these new sections to Portfolio_Dashboard to show portfolio-wide statistics:

### New Section: PROJECT DETAILS (below existing project table)

Find an empty area (suggest around row 30) and add:

**Location: A30**

**Add this section:**

```
Row 30: PROJECT DETAILS SUMMARY
Row 31: (blank)
Row 32: Total Target Audiences:        [formula]
Row 33: Total Technologies:            [formula]
Row 34: Total Deliverables:            [formula]
Row 35: Completed Deliverables:        [formula]
Row 36: Deliverable Completion Rate:   [formula]
```

**Formulas:**

**B32 - Total Audiences:**
```
=COUNTA(T_Project_Audiences[Project_ID])
```

**B33 - Total Technologies:**
```
=COUNTA(Project_Technologies[Project_ID])
```

**B34 - Total Deliverables:**
```
=COUNTA(T_Project_Deliverables[Project_ID])
```

**B35 - Completed Deliverables:**
```
=COUNTIF(T_Project_Deliverables[Status],"Completed")
```

**B36 - Completion Rate:**
```
=IF(B34=0,0,B35/B34)
```
Format as percentage.

---

### New Section: TOP TECHNOLOGIES (below Project Details)

**Location: A38**

```
Row 38: TOP TECHNOLOGIES ACROSS PORTFOLIO
Row 39: (blank)
Row 40: Technology               Count
Row 41: [formula]                [formula]
Row 42: [formula]                [formula]
Row 43: [formula]                [formula]
Row 44: [formula]                [formula]
Row 45: [formula]                [formula]
```

**Note:** This requires more complex formulas. Here's a simpler approach:

**A41-A45:** Manually type the top 5 technology names (look at Project_Technologies sheet)

**B41:**
```
=COUNTIF(Project_Technologies[Technology],A41)
```
Copy down to B42:B45

**Alternative:** Just list unique technologies without ranking if you prefer simpler approach.

---

### New Section: DELIVERABLE STATUS BREAKDOWN

**Location: D38**

```
Row 38: DELIVERABLE STATUS
Row 39: (blank)
Row 40: Status              Count
Row 41: Not Started         [formula]
Row 42: In Progress         [formula]
Row 43: Completed           [formula]
Row 44: On Hold             [formula]
```

**D41:**
```
=COUNTIF(T_Project_Deliverables[Status],"Not Started")
```

**D42:**
```
=COUNTIF(T_Project_Deliverables[Status],"In Progress")
```

**D43:**
```
=COUNTIF(T_Project_Deliverables[Status],"Completed")
```

**D44:**
```
=COUNTIF(T_Project_Deliverables[Status],"On Hold")
```

---

## 3. CONTROL SHEET - Add New Calculations

If you want to reference these new counts in Control sheet (for use in formulas elsewhere):

**Find empty cells in Control sheet and add:**

**B27:** Total Audiences
```
=COUNTA(T_Project_Audiences[Project_ID])
```

**B28:** Total Technologies
```
=COUNTA(Project_Technologies[Project_ID])
```

**B29:** Total Deliverables
```
=COUNTA(T_Project_Deliverables[Project_ID])
```

**B30:** Deliverables Completed
```
=COUNTIF(T_Project_Deliverables[Status],"Completed")
```

Then you can reference these in other formulas as `=Control!B27` etc.

---

## IMPLEMENTATION STEPS

### Step 1: Master_Projects (5 minutes)

1. Open v6 in Excel
2. Go to **Master_Projects** sheet
3. Click cell **AA1**
4. Type: `Audience_Count`
5. Click cell **AA2**
6. Type: `=COUNTIF(T_Project_Audiences[Project_ID],B2)`
7. Copy AA2 down to AA11 (or however many projects you have)
8. Repeat for columns AB, AC, AD, AE with their formulas

### Step 2: Portfolio_Dashboard (10 minutes)

1. Go to **Portfolio_Dashboard** sheet
2. Find empty area around row 30
3. Add section headers and formulas as shown above
4. Format cells (bold headers, percentages, etc.)

### Step 3: Test (2 minutes)

1. Go back to **Master_Projects**
2. Check column AA - should show count of audiences for each project
3. Go to **Portfolio_Dashboard**
4. Check new sections - should show totals

---

## QUICK REFERENCE TABLE

| Sheet | Column/Cell | Formula | Purpose |
|-------|------------|---------|---------|
| Master_Projects | AA2 | `=COUNTIF(T_Project_Audiences[Project_ID],B2)` | Audience count |
| Master_Projects | AB2 | `=COUNTIF(Project_Technologies[Project_ID],B2)` | Technology count |
| Master_Projects | AC2 | `=COUNTIF(T_Project_Deliverables[Project_ID],B2)` | Deliverable count |
| Master_Projects | AD2 | `=COUNTIFS(T_Project_Deliverables[Project_ID],B2,T_Project_Deliverables[Status],"Completed")` | Completed deliverables |
| Master_Projects | AE2 | `=IF(AC2=0,0,AD2/AC2)` | Completion % |
| Portfolio_Dashboard | B32 | `=COUNTA(T_Project_Audiences[Project_ID])` | Total audiences |
| Portfolio_Dashboard | B33 | `=COUNTA(Project_Technologies[Project_ID])` | Total technologies |
| Portfolio_Dashboard | B34 | `=COUNTA(T_Project_Deliverables[Project_ID])` | Total deliverables |
| Portfolio_Dashboard | B35 | `=COUNTIF(T_Project_Deliverables[Status],"Completed")` | Completed count |
| Portfolio_Dashboard | B36 | `=IF(B34=0,0,B35/B34)` | Completion rate |

---

## BENEFITS OF THESE CONNECTIONS

Once added, you'll be able to:

1. **In Master_Projects:** See at a glance how many audiences, technologies, and deliverables each project has
2. **In Portfolio_Dashboard:** See portfolio-wide statistics about project scope and progress
3. **Monitor progress:** Track deliverable completion rates across all projects
4. **Identify gaps:** Quickly see which projects are missing audiences/technologies/deliverables

---

## OPTIONAL: Add to Master_Projects Table

If you want these new columns to be part of the Master_Projects Excel Table:

1. Go to Master_Projects sheet
2. Click anywhere in the Master_Projects table
3. Table Design tab → Resize Table
4. Change range to include new columns (e.g., A1:AE1000)
5. Now formulas can reference: `Master_Projects[Audience_Count]`

---

## NOTES

- All formulas use structured references (table column names)
- They will auto-update when you add data to Project_Audiences, Project_Technologies, or Project_Deliverables
- COUNTIF and COUNTIFS are fast even with thousands of rows
- No risk of file corruption - these are simple Excel formulas

---

## PRIORITY

**Do these first:**
1. Master_Projects columns AA, AB, AC (the three count columns)
2. Portfolio_Dashboard B32-B36 (summary statistics)

**Do these later if time:**
3. Master_Projects columns AD, AE (completion tracking)
4. Portfolio_Dashboard technology and status breakdowns
5. Control sheet aggregations

