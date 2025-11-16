# Project Tracker - Complete TODO Guide
## What's Left to Do - Manual and Automated

**Created:** 2025-11-14
**Current Version:** v45
**Status:** All critical errors fixed ✓

---

## ✅ COMPLETED (v45)

### Automated Fixes
1. ✓ Control E5 #REF! error fixed (Projects/Country calculation)
2. ✓ Country_Dashboard B8 #REF! error fixed (Country PM lookup)
3. ✓ Regional_Summary region names corrected
4. ✓ Country_Dashboard ULO formulas fixed (D5, E5, G6)
5. ✓ Country_Dashboard Project ID blanks fixed
6. ✓ Portfolio_Dashboard all formulas show blanks instead of zeros

---

## 🔴 CRITICAL TASKS (Do These First)

### 1. Add Data Validation to Master_Projects
**Sheet:** Master_Projects
**Why:** Ensures data consistency and prevents errors
**How:**
- Select `Project_Status` column (E2:E201)
  - Data → Data Validation → List
  - Source: `=Config_Lists!$A$2:$A$10`
- Select `Project_Priority` column (F2:F201)
  - Data → Data Validation → List
  - Source: `=Config_Lists!$B$2:$B$5`
- Select `Fiscal_Year` column (A2:A201)
  - Data → Data Validation → List
  - Source: `FY2024,FY2025,FY2026,FY2027,FY2028`

### 2. Add Data Validation to Dashboards
**Sheets:** Country_Dashboard, Spotlight_PMWorkspace
**Why:** Makes dashboards easier to use
**How:**

**Country_Dashboard B2 (Country selector):**
- Select cell B2
- Data → Data Validation → List
- Source: `=Country_Regions[Country_Code]`
- Show dropdown arrow: Yes

**Spotlight_PMWorkspace B2 (Project ID selector):**
- Select cell B2
- Data → Data Validation → List
- Source: `=Master_Projects[Project_Unique_ID]`
- Show dropdown arrow: Yes

### 3. Assign Country Project Managers
**Sheet:** Country_PM_Assignments
**Current Status:** All 78 countries show "TBD"
**Why:** Country_Dashboard B8 will show "TBD" until these are filled
**How:**
- Go to Country_PM_Assignments sheet
- Fill in column D (Project_Manager) for each country
- Fill in column E (PM_Email) for each country
- Optional: Add column G for PM_Phone

---

## 🟡 HIGH PRIORITY TASKS

### 4. Add Conditional Formatting to Portfolio_Dashboard
**Sheet:** Portfolio_Dashboard
**Why:** Visual indicators for at-risk items
**How:**

**ULO % Alert (Column L):**
- Select L11:L20
- Conditional Formatting → New Rule → Format cells based on values
- Red text if value > 0.75 (75%)

**Days Remaining Alert (Column M):**
- Select M11:M20
- Conditional Formatting → New Rule → Format cells based on values
- Red fill if value < 90

**Progress Color Coding (Column E):**
- Select E11:E20
- Conditional Formatting → Color Scales
- Green (100%) → Yellow (50%) → Red (0%)

**Priority Color Coding (Column D):**
- Select D11:D20
- Conditional Formatting → Highlight Cell Rules
- If "Critical" → Red fill
- If "High" → Orange fill
- If "Medium" → Yellow fill
- If "Low" → Green fill

### 5. Add Conditional Formatting to Country_Dashboard
**Sheet:** Country_Dashboard
**Why:** Highlight issues at country level
**How:**

**ULO % Alerts (E5 and G6):**
- Select E5,G6
- Conditional Formatting → New Rule
- Red fill if value > 0.75

**Project Status Colors:**
- Select C12:C31 (Status column)
- Conditional Formatting → Highlight Cell Rules
- If "Active" → Green
- If "On Hold" → Yellow
- If "Completed" → Blue
- If "Cancelled" → Red

### 6. Add More Project Data
**Sheet:** Master_Projects
**Current Status:** Only 2 sample projects
**Why:** Tracker is designed for 200 projects
**How:**
- Add one project per row starting at row 4
- Required columns:
  - A: Fiscal_Year
  - B: Project_Unique_ID (e.g., PRJ-003)
  - C: Project_Name
  - D: Project_Summary
  - E: Project_Status (use dropdown)
  - F: Project_Priority (use dropdown)
  - Others will auto-calculate from formulas

### 7. Add Budget Data
**Sheet:** Country_Budgets
**Current Status:** Only 2 sample entries
**Why:** Dashboards need budget data to calculate totals
**How:**
- For each project, add one row per country
- Required columns:
  - B: Unique_ID (must match Master_Projects)
  - C: My_Country (TRUE for primary country)
  - E: Country_Name (type full name)
  - G: Proposed_Amount
  - H: Allocated_Amount
  - I: Obligated_Amount
  - J: Spent_Amount
- Columns D (Country_Code), K (ULO_Amount), M (ULO_Percent) auto-calculate

---

## 🟢 MEDIUM PRIORITY TASKS

### 8. Add Milestones
**Sheet:** Milestones
**Current Status:** 2 sample milestones
**How:**
- Add major milestones for each project
- Format: `[Project_ID]-MS-[Number]` (e.g., PRJ-001-MS-003)
- Include: Due_Date, Status, Completion_Percent

**Recommended: Convert to Table**
- Select A1:J100
- Insert → Table
- Name: T_Milestones

**Add Conditional Formatting:**
- Overdue: Due_Date < TODAY() and Status ≠ "Complete"
- Upcoming: Due_Date within 30 days

### 9. Add Conditional Formatting to Spotlight
**Sheet:** Spotlight_PMWorkspace
**Why:** Visual PM workspace
**How:**

**Status Indicators:**
- G5 (Status): Color by status
- G6 (Progress): Progress bar or color scale
- J3 (Days Remaining): Red if < 90

**Financial Alerts:**
- H15 (ULO %): Red if > 75%

### 10. Add Events
**Sheet:** Events
**Current Status:** 1 sample event
**How:**
- Add project events (meetings, reviews, presentations)
- Include: Event_Type, Event_Date, Location

**Recommended: Convert to Table**
- Name: T_Events

### 11. Add Stakeholder Data
**Sheet:** Stakeholders
**Current Status:** 1 sample stakeholder
**How:**
- Add key stakeholders
- Link to projects if possible
- Include contact information

### 12. Expand Config_Lists
**Sheet:** Config_Lists
**Why:** More dropdown options
**What to Add:**
- Column G: Document_Types (Contract, Report, Presentation, etc.)
- Column H: Event_Types (Meeting, Review, Training, etc.)
- Column I: Deliverable_Types (Document, Software, Training, etc.)
- Column J: Technology_Categories (Cloud, AI/ML, Security, etc.)

---

## 🔵 LOW PRIORITY ENHANCEMENTS

### 13. Add Charts to Portfolio_Dashboard
**Location:** Right side of Portfolio_Dashboard
**Suggested Charts:**
- Pie chart: Projects by Status
- Bar chart: Projects by Priority
- Line chart: Financial burn rate over time
- Gauge chart: Portfolio ULO %

### 14. Add Deliverables
**Sheet:** Project_Deliverables
**Current Status:** 99 sample deliverables
**How:**
- Review existing deliverables
- Add real deliverables for your projects
- Fix Completion_Percent column (should accept % without adding two zeros)

### 15. Add Project Technologies
**Sheet:** Project_Technologies
**Current Status:** 2 sample entries
**How:**
- Map technologies to projects
- Use for filtering and reporting

### 16. Add Project Audiences
**Sheet:** Project_Audiences
**Current Status:** 2 sample entries
**How:**
- Define target audiences for each project
- Use for impact analysis

### 17. Add Document Links
**Sheet:** Project_Documents
**Current Status:** 1 sample document
**How:**
- Add links to SharePoint/Teams/OneDrive
- Include document metadata

### 18. Add Calendar Tasks
**Sheet:** Calendar_Todo
**Current Status:** Empty (blank template)
**How:**
- Manually add tasks
- Link to projects via Unique_ID
- Set due dates and owners

**Recommended: Convert to Table**
- Name: T_Calendar_Todo

### 19. Protect Formulas
**All Sheets**
**Why:** Prevent accidental deletion
**How:**
- Select cells with formulas
- Format → Protection → Locked
- Review → Protect Sheet
- Uncheck "Format cells" and "Delete rows/columns"
- Leave other options checked

### 20. Add Freeze Panes
**Dashboards**
**Why:** Keep headers visible when scrolling
**How:**
- Portfolio_Dashboard: Freeze at row 11 (Freeze Panes above row 11)
- Country_Dashboard: Freeze at row 12
- Master_Projects: Freeze at row 2
- All data tables: Freeze at row 2

---

## 📊 SHEET-BY-SHEET STATUS

| Sheet | Formulas | Data | Validation | Formatting | Status |
|-------|----------|------|------------|------------|--------|
| Control | ✓ Fixed | Sample | Needed | Needed | 🟡 |
| Master_Projects | ✓ | Minimal | **NEEDED** | **NEEDED** | 🔴 |
| Portfolio_Dashboard | ✓ Fixed | Auto | Minimal | **NEEDED** | 🟡 |
| Country_Dashboard | ✓ Fixed | Auto | **NEEDED** | **NEEDED** | 🔴 |
| Spotlight_PMWorkspace | ✓ | Auto | **NEEDED** | Needed | 🟡 |
| Country_Budgets | ✓ | Minimal | Needed | Needed | 🟡 |
| Country_Regions | ✓ | Complete | ✓ | ✓ | ✅ |
| Config_Lists | ✓ | Basic | ✓ | ✓ | 🟢 |
| Country_PM_Assignments | ✓ | **ALL TBD** | ✓ | ✓ | 🔴 |
| Milestones | Minimal | Minimal | Needed | Needed | 🟢 |
| Events | None | Minimal | Needed | Needed | 🟢 |
| Stakeholders | ✓ | Minimal | Needed | ✓ | 🟢 |
| Regional_Summary | ✓ Fixed | Auto | ✓ | Needed | 🟢 |
| Calendar_Todo | None | Empty | Needed | Needed | 🟢 |
| Project_Deliverables | ✓ | Sample | Needed | Needed | 🟢 |
| Project_Audiences | ✓ | Sample | Needed | ✓ | 🟢 |
| Project_Technologies | ✓ | Sample | Needed | ✓ | 🟢 |
| Project_Documents | ✓ | Minimal | Needed | ✓ | 🟢 |

**Legend:**
- 🔴 Critical - Do Now
- 🟡 High Priority - Do Soon
- 🟢 Medium/Low - Do When Ready
- ✅ Complete - No Action Needed

---

## 🎯 RECOMMENDED WORK ORDER

### Week 1: Critical Setup
1. Add data validation to Master_Projects (Task #1)
2. Add data validation to dashboards (Task #2)
3. Fill in Country PM assignments (Task #3)

### Week 2: Core Data
4. Add 10-20 real projects to Master_Projects (Task #6)
5. Add budget data for those projects (Task #7)
6. Add conditional formatting to Portfolio_Dashboard (Task #4)
7. Add conditional formatting to Country_Dashboard (Task #5)

### Week 3: Enhanced Features
8. Add milestones for all projects (Task #8)
9. Add conditional formatting to Spotlight (Task #9)
10. Add events for key projects (Task #10)

### Week 4: Polish
11. Add stakeholder data (Task #11)
12. Expand Config_Lists (Task #12)
13. Add charts to dashboards (Task #13)

### Ongoing: Maintenance
- Add new projects as they come in
- Update budgets monthly
- Add deliverables as defined
- Link documents as created

---

## 📝 QUICK REFERENCE: DATA VALIDATION SOURCES

Copy these formulas for data validation:

```excel
# Master_Projects Status
=Config_Lists!$A$2:$A$10

# Master_Projects Priority
=Config_Lists!$B$2:$B$5

# Country_Dashboard Country
=Country_Regions[Country_Code]

# Spotlight_PMWorkspace Project ID
=Master_Projects[Project_Unique_ID]

# Country_Budgets Unique_ID
=Master_Projects[Project_Unique_ID]

# Country_Budgets Country_Code
=Country_Regions[Country_Code]

# Fiscal Year (any sheet)
FY2024,FY2025,FY2026,FY2027,FY2028
```

---

## 💡 PRO TIPS

1. **Start Small:** Add 5-10 projects first, test everything, then scale up
2. **Use Filters:** All tables have filter dropdowns - use them!
3. **Country_Dashboard:** Change B2 to switch countries - whole dashboard updates
4. **Spotlight_PMWorkspace:** Change B2 to switch projects - whole workspace updates
5. **ULO Monitoring:** Watch for ULO % > 75% (turns red with conditional formatting)
6. **My_Country Flag:** In Country_Budgets, set My_Country=TRUE for primary country per project
7. **Formula Protection:** Once you add real data, protect sheets to prevent accidental formula deletion
8. **Backup Regularly:** Save versions as you add data (v45, v46, etc.)

---

## 🚀 NEXT STEPS

1. **Review this guide completely**
2. **Start with Critical Tasks (Red items)**
3. **Test each feature as you add it**
4. **Add real data incrementally**
5. **Come back for automated enhancements as needed**

---

## 📞 NEED HELP?

If you want me to automate any of these tasks, just ask! I can:
- Create scripts to add data validation in bulk
- Add conditional formatting automatically
- Generate sample data for testing
- Create charts and visualizations
- Build additional formulas or features

The tracker is now fully functional with all formulas working. Everything else is about filling in your data and adding visual enhancements!
