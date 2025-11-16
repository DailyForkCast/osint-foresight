# Tracker v8 - Comprehensive Financial Tracking System
**Date:** November 6, 2025
**File:** `2025-10-26-Tracker-v8.xlsx`

---

## 🎯 MAJOR UPGRADE: Sophisticated Financial Tracking

This version implements a **professional-grade financial tracking system** with project lifecycle management, country ownership, and proper ULO calculations.

---

## ✅ WHAT'S NEW IN V8

### **1. Project Lifecycle Tracking**
Track projects through their entire lifecycle with appropriate financial metrics:

- **Proposed** (italicized) → Track "Proposed_Amount" only, excluded from calculations
- **CN Stage** → Track "Allocated" amount, awaiting obligation
- **Active/In Progress** → Full tracking: Allocated, Obligated, Spent, ULO
- **Archived** (grayed out) → Keep data visible but exclude from calculations

### **2. Country Ownership ("My Countries")**
- **My_Country** flag for each country budget (TRUE/FALSE)
- **Default:** TRUE when adding new countries
- **Calculations:** Only include countries where My_Country = TRUE
- **Visibility:** See ALL countries but calculate only YOUR countries

### **3. Proper ULO Calculation**
**OLD (v7):** `ULO = Allocated - Obligated` ❌ (WRONG)

**NEW (v8):** `ULO = Obligated - Spent` ✅ (CORRECT)

- ULO = **Unliquidated Obligations** (money committed but not yet spent)
- ULO% = `ULO / Obligated` (percentage of obligated funds not yet spent)
- Only calculated after funds are obligated (not before)

### **4. Spent Amount Tracking**
- New **Spent_Amount** column in Country_Budgets
- Manual entry (you update as money is spent)
- Rolls up to project totals (MY countries only)

### **5. Enhanced Portfolio Dashboard**
New columns:
- **Project_Manager:** Who's responsible (supports comma-separated list for multiple PMs)
- **My_Countries_Count:** How many countries are yours
- **Total_Countries_Count:** How many countries total
- **FAR_Notes:** Track fund changes (additions, subtractions, NCEs)

### **6. Conditional Formatting**
- **Proposed projects:** Italic text (easy to spot proposals)
- **Archived projects:** Gray text (clearly shows completed/archived)
- **My Countries:** (future enhancement: bold text)

---

## 📊 NEW COLUMNS REFERENCE

### **Master_Projects** (Project-level tracking)

| Column | Description | Type | Notes |
|--------|-------------|------|-------|
| **Proposed_Amount** | Initial funding request | Number | For Status = "Proposed" only |
| Total_Allocation | Approved funding | Number | Manual entry |
| Total_Obligated | Formally committed (MY countries only) | Formula | Auto-calculated |
| **Total_Spent** | Actually spent (MY countries only) | Formula | Auto-calculated |
| Total_ULO | Obligated - Spent | Formula | Auto-calculated |
| ULO_Percent | ULO / Obligated | Formula | Auto-calculated |
| **Project_Manager** | Responsible PM(s) | Text | Comma-separated if multiple |
| **Include_In_Calcs** | Should this project be in calculations? | Formula | FALSE if Proposed or Archived |
| **My_Countries_Count** | How many countries are yours | Formula | Auto-calculated |

### **Country_Budgets** (Country-level tracking)

| Column | Description | Type | Notes |
|--------|-------------|------|-------|
| Budget_ID | Unique ID | Formula | Auto-generated |
| Unique_ID | Project ID | Dropdown | Links to Master_Projects |
| **My_Country** | Is this my responsibility? | TRUE/FALSE | **Default: TRUE** |
| Country_Code | Country code | Dropdown | From country list |
| Country_Name | Full country name | Formula | Auto-looked up |
| Allocated_Amount | Approved for this country | Number | Manual entry |
| Obligated_Amount | Committed for this country | Number | Manual entry |
| **Spent_Amount** | Actually spent | Number | **Manual entry** |
| ULO | Obligated - Spent | Formula | Auto-calculated |
| ULO_Percent | ULO / Obligated | Formula | Auto-calculated |
| Spend_Health | Visual indicator | Formula | 🟢/🟡/🔴 |

### **Portfolio_Dashboard** (Summary view)

| Column | Description | Type | Notes |
|--------|-------------|------|-------|
| **Project_Manager** | Who's responsible | Lookup | From Master_Projects |
| **My_Countries_Count** | Your countries | Formula | Auto-calculated |
| **Total_Countries_Count** | All countries | Formula | Auto-calculated |
| **FAR_Notes** | Fund change notes | Text | Manual - track NCEs, additions, etc. |

---

## 🔢 CALCULATION EXAMPLES

### **Example 1: Active Project with Mixed Ownership**
```
Project: Digital Transformation (PRJ-001)
Status: Active
Project_Manager: Smith

Country Budgets:
┌──────────┬────────────┬────────────┬───────────┬─────────┬─────────┐
│ Country  │ My_Country │ Allocated  │ Obligated │ Spent   │ ULO     │
├──────────┼────────────┼────────────┼───────────┼─────────┼─────────┤
│ Germany  │ ✓ TRUE     │ $500,000   │ $350,000  │ $180,000│ $170,000│
│ France   │ ✗ FALSE    │ $300,000   │ $195,000  │ $95,000 │ $100,000│
│ Italy    │ ✓ TRUE     │ $400,000   │ $280,000  │ $140,000│ $140,000│
└──────────┴────────────┴────────────┴───────────┴─────────┴─────────┘

Master_Projects Rollup (MY COUNTRIES ONLY):
  Total_Obligated: $630,000 (Germany $350K + Italy $280K)
  Total_Spent: $320,000 (Germany $180K + Italy $140K)
  Total_ULO: $310,000 (Obligated - Spent)
  ULO%: 49.2% ($310K / $630K)
  My_Countries_Count: 2 of 3

NOTE: France is excluded from rollup because My_Country = FALSE
```

### **Example 2: Proposed Project**
```
Project: Infrastructure Modernization (PRJ-003)
Status: Proposed
Proposed_Amount: $750,000

Master_Projects Display:
  Total_Allocation: (blank)
  Total_Obligated: (blank)
  Total_Spent: (blank)
  Total_ULO: (blank)
  Include_In_Calcs: FALSE

NOTE: Excluded from Portfolio Dashboard calculations until approved
```

### **Example 3: CN Stage (Not Yet Obligated)**
```
Project: Cybersecurity Enhancement (PRJ-002)
Status: CN Stage
Total_Allocation: $1,000,000
Total_Obligated: $0
Total_Spent: $0
Total_ULO: $0
ULO%: 0%

Display: "Approved: $1M allocated, awaiting obligation"

NOTE: Included in calculations, but ULO shows $0 until obligation occurs
```

---

## 🔧 HOW TO USE

### **For New Projects:**

1. **Add to Master_Projects:**
   - Enter basic info (Name, Status, etc.)
   - If Status = "Proposed": Enter Proposed_Amount
   - If Status ≠ "Proposed": Enter Total_Allocation
   - Enter Project_Manager name(s)

2. **Add Country Budgets:**
   - Click Country_Budgets sheet
   - Add row for each country
   - Select Project_ID from dropdown
   - Select Country_Code from dropdown
   - **My_Country defaults to TRUE** (change to FALSE if not yours)
   - Enter Allocated_Amount, Obligated_Amount
   - Enter Spent_Amount as money is spent

3. **Watch It Calculate:**
   - ULO auto-calculates: Obligated - Spent
   - Master_Projects totals auto-update (YOUR countries only)
   - Portfolio Dashboard refreshes

### **For Existing Projects:**

1. **Mark Your Countries:**
   - Go to Country_Budgets
   - Set My_Country = TRUE for countries you manage
   - Set My_Country = FALSE for others

2. **Enter Spent Amounts:**
   - Update Spent_Amount as money is spent
   - Watch ULO decrease automatically

3. **Track Fund Changes:**
   - Go to Portfolio_Dashboard
   - Add notes in FAR_Notes column
   - Example: "NCE +$200K" or "Initial award $1M"

### **For Proposed Projects:**

1. Set Status = "Proposed"
2. Enter Proposed_Amount
3. Leave Allocated/Obligated/Spent blank
4. When approved, change Status to "Active" or "CN Stage"
5. Move Proposed_Amount to Total_Allocation
6. Clear Proposed_Amount

### **For Archived Projects:**

1. Set Status = "Archived"
2. Row turns gray automatically
3. Excluded from Portfolio Dashboard calculations
4. Data remains visible for reference

---

## 🎨 VISUAL INDICATORS

### **Project Status Formatting:**
- **Proposed:** _Italic text_ (stands out as "not yet approved")
- **Active/In Progress:** Normal text
- **Archived:** Gray text (clearly shows "done")

### **Spend Health:**
- 🟢 **Green:** ULO% > 80% (healthy - most funds still available)
- 🟡 **Yellow:** ULO% 50-80% (caution - funds depleting)
- 🔴 **Red:** ULO% < 50% (alert - most funds spent)

### **Country Ownership:**
- My_Country = TRUE: (future: bold text)
- My_Country = FALSE: Normal text

---

## 📝 WHAT TO TEST

### **Open v8 in Excel and verify:**

1. **Master_Projects Sheet:**
   - [ ] New columns visible: Proposed_Amount, Total_Spent, Project_Manager, My_Countries_Count
   - [ ] PRJ-001 shows Project_Manager = "Smith"
   - [ ] PRJ-002 shows Project_Manager = "Jones"
   - [ ] My_Countries_Count shows correct numbers

2. **Country_Budgets Sheet:**
   - [ ] My_Country column (C) shows TRUE/FALSE
   - [ ] Row 2: My_Country = TRUE
   - [ ] Row 3: My_Country = FALSE
   - [ ] Spent_Amount column (H) shows 0
   - [ ] ULO formula: =G2-H2 (Obligated - Spent)

3. **Portfolio_Dashboard Sheet:**
   - [ ] New columns: Project_Manager, My_Countries_Count, Total_Countries_Count, FAR_Notes
   - [ ] All visible and ready for data

4. **Calculations:**
   - [ ] Change My_Country from FALSE to TRUE on Row 3
   - [ ] Watch Master_Projects totals update
   - [ ] Enter a Spent_Amount (e.g., $50,000)
   - [ ] Watch ULO decrease automatically

5. **Proposed Project Test:**
   - [ ] Add new project with Status = "Proposed"
   - [ ] Enter Proposed_Amount = $500,000
   - [ ] Verify it's excluded from calculations (Include_In_Calcs = FALSE)
   - [ ] Verify text is italic

---

## 🚫 KNOWN LIMITATIONS

1. **Manual Spent Entry:** You must manually enter Spent_Amount as money is spent
2. **No Auto-Sync:** Does not connect to external financial systems
3. **Excel-Only:** Formulas work in Excel 2016+, may have issues in older versions
4. **No History:** Changing My_Country doesn't keep history of previous ownership

---

## 📋 STILL TO DO (Future Enhancements)

From your original notes:

- [ ] **Document linking:** Add ability to link/see documents in Project Spotlight
- [ ] **Country-specific dashboard:** Create dashboard filtered by country
- [ ] **Countries not loading:** Investigate Country_Budgets loading issue
- [ ] **Visual overhaul:** Make tracker more appealing (colors, layout)
- [ ] **Deliverables/Audiences/Products/Technologies:** Refine purpose and structure

---

## 📂 FILES CREATED

1. **2025-10-26-Tracker-v8.xlsx** - Main tracker with financial tracking system
2. **TRACKER_V8_FINANCIAL_DESIGN.md** - Detailed design document
3. **TRACKER_V8_COMPREHENSIVE_SUMMARY.md** - This summary (user guide)
4. **create_tracker_v8_financial_tracking.py** - Implementation script

---

## 🎯 NEXT STEPS

**For You:**
1. Open v8 in Excel
2. Review new columns and structure
3. Mark all your countries (My_Country = TRUE/FALSE)
4. Enter actual Spent amounts for existing projects
5. Test calculations - verify they only include YOUR countries
6. Add FAR_Notes for any fund changes

**For Next Session:**
1. Decide if we tackle visual overhaul next
2. Design country-specific dashboard
3. Build document linking system
4. Or work on something else from your notes

---

## 📊 SUMMARY

**Major Changes:**
- ✅ Proper ULO calculation (Obligated - Spent, not Allocated - Obligated)
- ✅ Country ownership tracking (My Countries vs All Countries)
- ✅ Project lifecycle support (Proposed/Active/Archived)
- ✅ Spent amount tracking
- ✅ Enhanced Portfolio Dashboard
- ✅ Conditional formatting
- ✅ 78 countries (European + your specified regions)

**Key Benefits:**
- **Accuracy:** ULO calculation now correct
- **Flexibility:** Track all countries, calculate only yours
- **Visibility:** See proposed vs active vs archived projects
- **Control:** Know exactly where YOUR funds stand

**Test and let me know:**
- What works great?
- What needs adjustment?
- What should we build next?

---

**Ready to use! 🎉**
