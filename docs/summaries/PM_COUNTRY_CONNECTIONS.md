# Project Manager Country Connections
**Connecting PMs to Countries (No Duplicates)**

---

## THE PROBLEM

- **Master_Projects** has Project_Manager (column Z)
- **Country_Budgets** has countries per project
- **Country_PM_Assignments** exists but shows "TBD" for all PMs
- **Need:** Show which PM is responsible for which countries, with each PM listed only ONCE

---

## THE SOLUTION: Two Approaches

### **Approach 1: Update Country_PM_Assignments (Country → PM)**
Shows which PM(s) manage projects in each country

### **Approach 2: Create PM_Summary Sheet (PM → Countries)**
Shows each PM once with all their countries listed

**Recommendation:** Do BOTH - they serve different purposes

---

## APPROACH 1: Country_PM_Assignments Sheet

### Current Structure:
```
A: Country_Code
B: Country_Name
C: Region
D: Project_Manager (currently "TBD")
E: PM_Email
F: PM_Phone
G: Notes
```

### Formula to Populate Column D (Project_Manager)

The challenge: A country might have multiple projects with different PMs.

**Solution options:**

#### Option A: Show First PM Found (Simple)

**D2 formula:**
```
=IFERROR(INDEX(Master_Projects[Project_Manager],MATCH(1,(Country_Budgets[Country_Code]=A2)*ISNUMBER(MATCH(Country_Budgets[Unique_ID],Master_Projects[Unique_ID],0)),0)),"No PM Assigned")
```

**Note:** This is an array formula. In Excel, press **Ctrl+Shift+Enter** after typing it.

#### Option B: Show All PMs (Comma Separated) - Excel 365 Only

If you have Excel 365, use TEXTJOIN:

**D2 formula:**
```
=IFERROR(TEXTJOIN(", ",TRUE,IF(Country_Budgets[Country_Code]=A2,XLOOKUP(Country_Budgets[Unique_ID],Master_Projects[Unique_ID],Master_Projects[Project_Manager],""),"")), "No PM Assigned")
```

**Note:** Array formula - press **Ctrl+Shift+Enter**

#### Option C: Simplest Approach - Use Helper Column

This avoids complex array formulas:

**Add new column H: "Primary_Project"**

**H2:**
```
=IFERROR(INDEX(Country_Budgets[Unique_ID],MATCH(A2,Country_Budgets[Country_Code],0)),"")
```

**Then D2:**
```
=IFERROR(XLOOKUP(H2,Master_Projects[Unique_ID],Master_Projects[Project_Manager],"No PM"),"No PM")
```

Or without XLOOKUP:
```
=IFERROR(INDEX(Master_Projects[Project_Manager],MATCH(H2,Master_Projects[Unique_ID],0)),"No PM")
```

**Copy both down to row 99**

---

## APPROACH 2: PM_Summary Sheet (RECOMMENDED)

Create a NEW sheet that shows **each PM once** with all their countries.

### Create New Sheet: "PM_Summary"

**Step 1: Create the sheet**
1. Right-click on sheet tabs
2. Insert → Worksheet
3. Name it "PM_Summary"

**Step 2: Add headers**

```
A1: Project_Manager
B1: Countries
C1: Country_Count
D1: Total_Projects
E1: Email
F1: Phone
```

**Step 3: Get unique PM list**

In Excel 365, use UNIQUE function:

**A2:**
```
=SORT(UNIQUE(FILTER(Master_Projects[Project_Manager],Master_Projects[Project_Manager]<>"")))
```

**For older Excel:** Manually type PM names in column A (Amy, Bob, Carol, etc.)

**Step 4: Aggregate countries for each PM**

**B2 - Countries (comma separated):**

**Excel 365:**
```
=TEXTJOIN(", ", TRUE, UNIQUE(IF(ISNUMBER(MATCH(Country_Budgets[Unique_ID],IF(Master_Projects[Project_Manager]=A2,Master_Projects[Unique_ID],""),0)),Country_Budgets[Country_Code],"")))
```
Press **Ctrl+Shift+Enter**

**Simpler alternative (works in all Excel):**

Use Power Query or pivot table (see below)

**C2 - Country Count:**
```
=LEN(B2)-LEN(SUBSTITUTE(B2,",",""))+1
```

**D2 - Total Projects:**
```
=COUNTIF(Master_Projects[Project_Manager],A2)
```

**E2 - Email:**
```
=IFERROR(INDEX(Master_Projects[Implementer_POC_Email],MATCH(A2,Master_Projects[Project_Manager],0)),"")
```

**F2 - Phone:**
```
=IFERROR(INDEX(Master_Projects[Implementer_POC_Phone],MATCH(A2,Master_Projects[Project_Manager],0)),"")
```

---

## APPROACH 3: Using Power Query (NO FORMULAS - EASIER)

This is the BEST approach if you're not comfortable with complex formulas:

### Step 1: Create PM → Country mapping

1. Go to **Data** tab → **Get Data** → **From Other Sources** → **Blank Query**
2. Click **Advanced Editor**
3. Paste this code:

```powerquery
let
    Source = Excel.CurrentWorkbook(){[Name="Country_Budgets"]}[Content],
    Projects = Excel.CurrentWorkbook(){[Name="Master_Projects"]}[Content],
    Merged = Table.NestedJoin(Source, {"Unique_ID"}, Projects, {"Unique_ID"}, "Projects", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Merged, "Projects", {"Project_Manager"}, {"Project_Manager"}),
    Grouped = Table.Group(Expanded, {"Project_Manager"}, {
        {"Countries", each Text.Combine([Country_Code], ", "), type text},
        {"Country_Count", each List.Count(List.Distinct([Country_Code])), type number}
    }),
    Filtered = Table.SelectRows(Grouped, each ([Project_Manager] <> null and [Project_Manager] <> ""))
in
    Filtered
```

4. Click **Close & Load**
5. Power Query creates the PM_Summary table automatically!

### Step 2: Refresh data

When you update projects or countries:
1. Right-click the query table
2. Click **Refresh**

---

## QUICK IMPLEMENTATION GUIDE

### **If you have Excel 365:**

1. **Create PM_Summary sheet**
2. Add headers in row 1
3. **A2:** `=SORT(UNIQUE(Master_Projects[Project_Manager]))`
4. **C2:** `=COUNTIF(Master_Projects[Project_Manager],A2)` (copy down)
5. **B2:** Use the TEXTJOIN formula above (or manually type countries)

### **If you have older Excel:**

1. **Option 1:** Use Power Query (recommended - works in Excel 2010+)
2. **Option 2:** Manually create PM_Summary with these columns:
   - Type PM names manually in column A
   - Use COUNTIF in column C for project counts
   - Manually type their countries in column B (e.g., "AT, BE, DE")

---

## EXAMPLE OUTPUT

### PM_Summary Sheet:

| Project_Manager | Countries | Country_Count | Total_Projects |
|----------------|-----------|---------------|----------------|
| Amy Johnson | AT, BE, NL | 3 | 2 |
| Bob Smith | US, CA, MX | 3 | 4 |
| Carol Lee | DE, FR, IT | 3 | 1 |

**Each PM appears only ONCE** ✓

---

## CONNECTING TO OTHER SHEETS

### Add PM info to Country_Budgets

**Country_Budgets** - Add column after Country_Name:

**New Column D: Project_Manager**

**D2 formula:**
```
=XLOOKUP(B2,Master_Projects[Unique_ID],Master_Projects[Project_Manager],"No PM")
```

Or without XLOOKUP:
```
=IFERROR(INDEX(Master_Projects[Project_Manager],MATCH(B2,Master_Projects[Unique_ID],0)),"No PM")
```

Now Country_Budgets shows which PM manages each country-project combination.

---

## RECOMMENDED IMPLEMENTATION PLAN

### Step 1: Add PM to Country_Budgets (5 minutes)
1. Open v6
2. Go to Country_Budgets
3. Insert column after Country_Name
4. Header: "Project_Manager"
5. Formula: `=XLOOKUP(B2,Master_Projects[Unique_ID],Master_Projects[Project_Manager],"")`
6. Copy down

### Step 2: Create PM_Summary Sheet (10 minutes)
1. Create new sheet "PM_Summary"
2. Use Power Query method (easiest) OR
3. Use formulas if you have Excel 365

### Step 3: Update Country_PM_Assignments (5 minutes)
1. Go to Country_PM_Assignments
2. Update column D with formula from Approach 1, Option C

---

## WHAT EACH SHEET WILL SHOW

| Sheet | View | Shows |
|-------|------|-------|
| **Master_Projects** | Project view | Each project and its PM |
| **Country_Budgets** | Country-Project view | Each country-project combo with PM |
| **Country_PM_Assignments** | Country view | Each country with its PM(s) |
| **PM_Summary** | PM view | **Each PM once** with all countries |

---

## PRIORITY

**Do This First:**
1. Add PM column to Country_Budgets (most useful day-to-day)
2. Create PM_Summary sheet with Power Query or simple manual entry

**Do This Later:**
3. Update Country_PM_Assignments formulas

---

## NOTES

- PM_Summary ensures **no duplicate PM names** (what you requested)
- Country_Budgets shows PM per country-project combination
- If a country has projects from multiple PMs, you'll see multiple rows in Country_Budgets
- PM_Summary aggregates all of each PM's countries into one row

**Which approach do you want to start with?**
1. Power Query (easiest, no formulas)
2. Excel 365 formulas (if you have it)
3. Simple manual PM_Summary (type names and countries manually)
