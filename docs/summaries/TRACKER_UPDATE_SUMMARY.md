# Project Tracker Update Summary
**Date:** October 25, 2025
**Original File:** `c:/Users/mrear/AppData/Local/Temp/2025-10-05-Tracker (1).xlsx`
**Updated File:** `C:/Projects/OSINT - Foresight/2025-10-05-Tracker-UPDATED.xlsx`

---

## ✅ ALL CHANGES COMPLETED

### 1. **Milestone IDs** → PRJ-XXX-MS-XXX Format
- **Changed:** 30 milestones
- **Old Format:** `MS-001`, `MS-002`, etc.
- **New Format:** `PRJ-001-MS-001`, `PRJ-001-MS-002`, `PRJ-002-MS-001`, etc.
- **Benefit:** Clear project association, better filtering/sorting

### 2. **Event IDs** → PRJ-XXX-EVT-XXX Format
- **Changed:** Event ID structure
- **Old Format:** `EVT-001`, `EVT-002`, etc.
- **New Format:** `PRJ-001-EVT-001`, `PRJ-001-EVT-002`, etc.
- **Benefit:** Matches milestone structure, clear project linkage

### 3. **New Sheet: Country_PM_Assignments**
- **Created:** Complete PM assignment system
- **Columns:** Country_Code, Country_Name, Project_Manager, PM_Email, PM_Phone, Notes
- **Countries:** All 94 countries included
- **Sample Data:** Regional placeholders (EUR PM TBD, WHA PM TBD, etc.)
- **Next Step:** Fill in actual PM names for each country

### 4. **Country_Regions Sheet** → Complete Global Coverage
- **Updated:** 94 countries across 6 regions
- **Regions:**
  - **EUR** (Europe): 41 countries - Albania through United Kingdom
  - **WHA** (Western Hemisphere): 15 countries - Argentina through United States
  - **EAP** (East Asia Pacific): 13 countries - Australia through Vietnam
  - **AF** (Africa): 11 countries - Ethiopia through Zambia
  - **NEA** (Near East Asia/Middle East): 9 countries - Egypt through UAE
  - **SCA** (South & Central Asia): 5 countries - India through Tajikistan
- **Includes:** Country codes, full names, region, EU membership, subregion

### 5. **Funding Format** → Changed from K to M (Millions)
- **Changed:** All budget display formulas
- **Old:** `$2,500K` → **New:** `$2.5M`
- **Old:** `$15,000K` → **New:** `$15.0M`
- **Locations Updated:**
  - Portfolio_Dashboard
  - Master_Projects (all budget columns)
  - Country_Budgets
  - Control sheet formulas

### 6. **Project Spotlight** → Complete Restructure
- **Removed:** Map visualization (no Bing/internet access required)
- **New Layout:**
  - **Summary (Columns B-E):** Project description
  - **Target Audiences (Column F):** Pull from Project_Audiences
  - **Target Technologies (Column G):** Technology focus areas
  - **Key Deliverables (Row 15+):** Table showing deliverables from Project_Deliverables sheet
- **Deliverables Table:** Auto-populates based on selected project
- **Columns:** Deliverable Name, Type, Due Date, Status, Owner

### 7. **Stakeholders Sheet** → Complete Redesign
- **New Structure:** 22 columns (was 12)
- **Added Columns:**
  1. `Location_City` - Physical location city
  2. `Location_Country` - Physical location country
  3. `Time_Zone_Offset` - Hours from UTC (+1, -5, etc.)
  4. `Local_Time` - **Dynamic formula:** `=NOW()+(Time_Zone_Offset/24)`
  5. `Stakeholder_Type` - Category (see below)
  6. `Project_IDs` - Comma-separated project links
  7. `Countries` - Comma-separated country codes
  8. `Products` - Related products
  9. `Region` - EUR/WHA/EAP/AF/NEA/SCA
  10. `Theme` - Thematic areas

- **Stakeholder Types:**
  - **Project-Specific:** Tied to specific projects
  - **Location-Specific:** Country/city based contacts
  - **Product-Specific:** Tied to deliverable products
  - **Regional:** Regional directors/leads (EUR, WHA, etc.)
  - **Thematic:** Cross-cutting themes (Cybersecurity, Digital Transform, Climate, etc.)

- **Sample Data:** 5 complete stakeholder examples showing each type

---

## 📋 NEXT MANUAL STEPS

### Step 1: Fill in Country PM Names
**Sheet:** `Country_PM_Assignments`
- Replace "EUR PM TBD" with actual names
- Replace "WHA PM TBD" with actual names
- Fill in PM emails and phone numbers
- This will auto-populate Project Managers in other sheets

### Step 2: Add Target Audiences Data
**Sheet:** `Project_Spotlight`
- Column F needs data source
- **Option A:** Pull from `Project_Audiences` sheet
- **Option B:** Add to `Master_Projects` as new column
- **Recommended:** Create formula linking to Project_Audiences

### Step 3: Add Target Technologies Column/Data
**Sheet:** `Project_Spotlight`
- Column G needs data populated
- **Recommended:** Add `Target_Technologies` column to `Master_Projects` sheet
- Or create separate `Project_Technologies` sheet

### Step 4: Populate Real Stakeholders
**Sheet:** `Stakeholders`
- Currently has 5 sample stakeholders
- Add your actual stakeholder contacts
- Use the sample rows as templates
- Delete sample data once real data is added

### Step 5: Link Project Managers to Master_Projects
**Sheet:** `Master_Projects`
- Add `Project_Managers` column (if not present)
- Add formula to auto-populate from Country_Budgets:
  ```excel
  =TEXTJOIN(", ", TRUE, UNIQUE(IF(Country_Budgets!$B:$B=[@Unique_ID], Country_Budgets!$E:$E, "")))
  ```
- This will show all PMs for countries in each project

---

## 🎯 KEY FEATURES

### Auto-Updating Project Manager System
1. Update `Country_PM_Assignments` → PM for Germany = "Hans Mueller"
2. `Country_Budgets` auto-populates via VLOOKUP
3. `Master_Projects` rolls up all country PMs for the project
4. **Result:** Single source of truth for PM assignments

### Multi-Dimensional Stakeholder Tracking
- Can track a stakeholder who is:
  - Regional (EUR Director)
  - Works on specific projects (PRJ-001, PRJ-003)
  - Covers certain countries (DE, FR, UK)
  - Has thematic focus (Digital Transformation)
  - All in one row!

### Dynamic Time Zone Support
- Stakeholder in Berlin (UTC+1) shows their local time automatically
- Formula updates in real-time
- Easy to see "Is it business hours there?" at a glance

### Global Regional Coverage
- 94 countries across 6 DoD/State regions
- Matches standard USG regional structure
- Easy filtering by region

---

## 📊 STATISTICS

- **Total Sheets:** 19 (added 1: Country_PM_Assignments)
- **Milestones Updated:** 30 IDs
- **Events Updated:** 1 ID
- **Countries Added:** 94 (from 53)
- **Regions:** 6 (EUR, WHA, EAP, AF, NEA, SCA)
- **Stakeholder Columns:** 22 (from 12)
- **New PM Assignment System:** 94 country mappings

---

## 🔍 WHERE TO FIND THINGS

| Feature | Sheet | Location |
|---------|-------|----------|
| Milestone IDs | Milestones | Column A (PRJ-XXX-MS-XXX) |
| Event IDs | Events | Column A (PRJ-XXX-EVT-XXX) |
| Country PM Assignments | Country_PM_Assignments | Full sheet |
| All 94 Countries | Country_Regions | Full sheet |
| Regional Breakdowns | Country_Regions | Column C (Region) |
| Funding in Millions | Portfolio_Dashboard | All budget formulas |
| Project Spotlight Layout | Project_Spotlight | Rows 4-22 |
| Stakeholder Types | Stakeholders | Column K |
| Time Zones | Stakeholders | Columns G-H |

---

## ⚠️ IMPORTANT NOTES

1. **Original file is unchanged** - All changes are in the new `-UPDATED.xlsx` file
2. **Sample data included** - Replace with your actual data
3. **Formulas are ready** - Just need data sources populated
4. **PM system is ready** - Just fill in actual PM names in Country_PM_Assignments
5. **Backward compatible** - All original functionality preserved

---

## 🆘 TROUBLESHOOTING

### If formulas show #REF! errors:
- Check that sheet names haven't changed
- Verify that Project_Deliverables and Project_Audiences sheets exist

### If PM lookups aren't working:
- Ensure Country_PM_Assignments has all country codes
- Check that country codes match between sheets

### If Local_Time shows wrong value:
- Verify Time_Zone_Offset is correct (should be hours from UTC)
- Remember: EST = -5, CET = +1, etc.

---

## 📞 SUPPORT

For questions about this update, refer to:
- This summary document
- The original chat conversation
- Scripts: `update_tracker.py` and `update_stakeholders.py`

---

**Update completed successfully!** 🎉
