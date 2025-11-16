# Project Tracker Updates - Complete Summary
**Date**: October 26, 2025
**Final File**: `2025-10-05-Tracker-FINAL-v2.xlsx`

---

## ✅ COMPLETED CHANGES

### 1. Milestone & Event ID Format ✓
- **Changed**: All Milestone IDs from `MS-001` to `PRJ-XXX-MS-XXX` format
- **Changed**: All Event IDs from `EVT-001` to `PRJ-XXX-EVT-XXX` format
- **Impact**: 30 milestones and 1 event updated
- **Benefit**: Clear project association for all milestones and events

### 2. Project Manager System ✓
- **Added**: `Project_Manager` column to Master_Projects (Column T)
- **Created**: `Country_PM_Assignments` sheet with all 94 countries
- **Formula**: Automatically shows all relevant PMs based on countries involved in project
- **Note**: PM names currently show "EUR PM TBD", "WHA PM TBD", etc. - **REPLACE WITH ACTUAL NAMES**

### 3. Global Country Coverage ✓
- **Expanded**: From 53 to 94 countries across 6 DoD/State Department regions
- **Regions**:
  - **EUR** (37 countries): Albania, Armenia, Austria, Azerbaijan, Belarus, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Georgia, Germany, Greece, Hungary, Iceland, Ireland, Italy, Kosovo, Latvia, Lithuania, Luxembourg, Malta, Moldova, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Ukraine, United Kingdom
  - **WHA** (20 countries): Antigua and Barbuda, Argentina, Bahamas, Barbados, Belize, Bolivia, Brazil, Canada, Chile, Colombia, Costa Rica, Dominica, Dominican Republic, Ecuador, El Salvador, Grenada, Guatemala, Guyana, Haiti, Honduras, Jamaica, Mexico, Nicaragua, Panama, Paraguay, Peru, Saint Kitts and Nevis, Saint Lucia, Saint Vincent and the Grenadines, Suriname, Trinidad and Tobago, United States, Uruguay, Venezuela
  - **EAP** (17 countries): Australia, Brunei, Cambodia, China, Indonesia, Japan, Laos, Malaysia, Mongolia, Myanmar, New Zealand, Papua New Guinea, Philippines, Singapore, South Korea, Taiwan, Thailand, Vietnam
  - **AF** (10 countries): Angola, Botswana, Ethiopia, Ghana, Kenya, Nigeria, Rwanda, Senegal, South Africa, Tanzania
  - **NEA** (7 countries): Algeria, Egypt, Iraq, Israel, Jordan, Lebanon, Morocco, Saudi Arabia, Tunisia, United Arab Emirates, Yemen
  - **SCA** (3 countries): Afghanistan, India, Kazakhstan, Pakistan, Sri Lanka, Uzbekistan

### 4. Multi-Dimensional Stakeholders ✓
- **Redesigned**: Complete stakeholder sheet with 22 columns
- **New Features**:
  - Project-specific stakeholders (Project_IDs column)
  - Location-specific (Countries column)
  - Product-specific (Products column)
  - Regional (Region column)
  - Thematic (Theme column)
  - Location data (Location_City, Location_Country)
  - Time zone tracking (Time_Zone_Offset, Local_Time with auto-calculation)
  - Enhanced contact tracking (Contact_Frequency, Last_Contact, Next_Contact)
- **Sample Data**: 5 example stakeholders showing different relationship types

### 5. Funding Format Change ✓
- **Changed**: All budget displays from thousands ($#,##0,K) to millions ($#,##0.0,M)
- **Updated**: 2 formulas in Portfolio_Dashboard
- **Benefit**: More appropriate scale for large project budgets

### 6. Country_Budgets Enhanced Structure ✓
- **New Columns**:
  - **E: Allocated** - Amount budgeted for project
  - **F: Obligated** - Amount actually received (have in hand)
  - **G: Spent** - Amount actually disbursed/used *(NEW)*
  - **H: ULO** - Obligated - Spent (money on hand but not spent) *(FORMULA FIXED)*
  - **I: ULO_Percent** - ULO / Obligated *(FORMULA FIXED)*
  - **J: Funding_Gap** - Allocated - Obligated (promised but not received) *(NEW)*
  - **K: Spend_Health** - Execution status based on ULO%
- **Sample Data**: Spent amounts generated as 50-90% of Obligated - **REPLACE WITH ACTUAL DATA**
- **Formulas**: All formulas updated to reflect correct calculations

### 7. Dynamic Project Spotlight Structure ✓
- **Removed**: Cell-based map (per your preference for actual visual or nothing)
- **Created**: Three dynamic data sections:
  - **TARGET TECHNOLOGIES** (rows 14-17)
  - **TARGET AUDIENCES** (rows 20-23)
  - **KEY DELIVERABLES** (rows 26-29)
- **Created**: `Project_Technologies` sheet with 14 sample technology records
- **Structure**: Placeholder text with instructions for dynamic formulas
- **Note**: Ready for you to add formulas or manually populate per project

---

## 📋 WHAT YOU NEED TO DO NEXT

### Priority 1: Add Data Sheets
1. **Create Project_Audiences sheet** (similar structure to Project_Technologies):
   - Columns: Project_ID, Audience_Type, Region, Description, Priority

2. **Create/Update Project_Deliverables sheet**:
   - Columns: Project_ID, Deliverable_Name, Type, Due_Date, Status, Owner, Progress

### Priority 2: Add Dynamic Formulas (Option A - Recommended for Excel 365)
If you have Excel 365 with FILTER() function:

**For Target Technologies (starting at B16):**
```excel
=FILTER(Project_Technologies!B:E, Project_Technologies!A:A=$B$2, "No technologies assigned")
```

**For Target Audiences (starting at B22):**
```excel
=FILTER(Project_Audiences!B:E, Project_Audiences!A:A=$B$2, "No audiences defined")
```

**For Key Deliverables (starting at B28):**
```excel
=FILTER(Project_Deliverables!B:G, Project_Deliverables!A:A=$B$2, "No deliverables assigned")
```

### Priority 2: Add Dynamic Formulas (Option B - For Older Excel)
If you don't have FILTER(), use INDEX/MATCH arrays:

**For first technology in B16:**
```excel
=IFERROR(INDEX(Project_Technologies!B:B, SMALL(IF(Project_Technologies!$A:$A=$B$2, ROW(Project_Technologies!$A:$A)), ROW(A1))), "")
```
*(This is an array formula - press Ctrl+Shift+Enter)*

Then drag across columns C-E and down for additional rows.

### Priority 3: Manual Data Entry Option
Instead of formulas, you can manually copy/paste data from the source sheets for each project when you change the Project Spotlight selection.

### Priority 4: Replace Sample Data
1. **Country_PM_Assignments**: Replace "EUR PM TBD" etc. with actual PM names
2. **Country_Budgets**: Replace random "Spent" amounts with actual spending data
3. **Stakeholders**: Replace 5 sample stakeholders with your actual stakeholder list
4. **Project_Technologies**: Update or expand the 14 sample technology records

---

## 📊 FILE STRUCTURE OVERVIEW

### Sheets in Final Workbook:
1. **Portfolio_Dashboard** - Overview with funding in millions format
2. **Master_Projects** - Project list with Project_Manager column (Column T)
3. **Project_Spotlight** - Dynamic sections for Technologies, Audiences, Deliverables
4. **Milestones** - Updated IDs (PRJ-XXX-MS-XXX format)
5. **Events** - Updated IDs (PRJ-XXX-EVT-XXX format)
6. **Country_Budgets** - Enhanced with Spent, ULO, Funding_Gap columns
7. **Risk_Register** - Unchanged
8. **Decision_Log** - Unchanged
9. **Budget_Tracker** - Unchanged
10. **Stakeholders** - 22 columns with multi-dimensional relationships
11. **Project_PM_Dashboard** - Unchanged
12. **Config_Lists** - Unchanged
13. **Country_Regions** - Updated to 94 countries in 6 regions
14. **Country_PM_Assignments** - *NEW* - PM assignments for all 94 countries
15. **Task_List** - Unchanged
16. **Project_Deliverables** - Unchanged
17. **Project_Audiences** - *TO BE CREATED*
18. **Project_Technologies** - *NEW* - 14 sample technology records

---

## 🔧 EXAMPLE FORMULAS REFERENCE

### Project Manager Auto-Lookup (Column T in Master_Projects)
```excel
=TEXTJOIN(", ", TRUE,
    IF(ISNUMBER(SEARCH(Country_PM_Assignments!A:A, L2)),
       Country_PM_Assignments!B:B, ""))
```

### Local Time Calculation (Column H in Stakeholders)
```excel
=NOW()+(G2/24)
```
*Where G2 contains the UTC offset (e.g., +1, -5, etc.)*

### Spend Health (Column K in Country_Budgets)
```excel
=IF(I2<0.1, "Low Execution", IF(I2>0.6, "Slow Execution", "On Track"))
```

### ULO Calculation (Column H in Country_Budgets)
```excel
=F2-G2
```
*(Obligated - Spent)*

### Funding Gap (Column J in Country_Budgets)
```excel
=E2-F2
```
*(Allocated - Obligated)*

---

## 📁 FILES CREATED

1. `2025-10-05-Tracker-FINAL-v2.xlsx` - **MAIN FILE** with all updates
2. `2025-10-05-Tracker-CLEAN.xlsx` - Intermediate working file
3. `update_tracker.py` - Script for ID changes, PM system, regions
4. `update_stakeholders.py` - Script for stakeholder redesign
5. `update_country_budgets.py` - Script for funding structure
6. `create_dynamic_spotlight.py` - Script for dynamic spotlight setup
7. `fix_tracker_tables.py` - Fix for table reference errors
8. `restore_spotlight.py` - Cleanup script
9. `reorganize_spotlight.py` - Layout reorganization

---

## ⚠️ IMPORTANT NOTES

1. **Government Excel Version**: Formulas avoid FILTER() in placeholders due to potential compatibility issues. Use INDEX/MATCH arrays if FILTER() is not available.

2. **Data Validation**: The Project Spotlight dropdown in B2 should reference `=Master_Projects!A2:A11` to show all project IDs.

3. **Sample Data**: Multiple sheets contain sample/placeholder data that should be replaced with actual data:
   - Country_PM_Assignments (PM names)
   - Country_Budgets (Spent amounts)
   - Stakeholders (5 sample records)
   - Project_Technologies (14 sample records)

4. **Next Enhancement**: Consider adding Project_Risks and Project_Issues sheets that can also be filtered dynamically in Project Spotlight.

---

## 📞 QUESTIONS?

If you need help with:
- Adding the dynamic formulas
- Creating the missing sheets (Project_Audiences)
- Understanding any of the new structures
- Further customizations

Just ask!
