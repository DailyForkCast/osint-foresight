# Manual Updates for 2025-10-26 - Tracker.xlsx
**Customized for your specific file structure**

---

## FILE CURRENT STATE

Your file already has:
- ✅ Project_Audiences sheet (ready to use!)
- ✅ Project_Products sheet (ready to use!)
- ✅ Stakeholders with 12 columns
- ✅ Master_Projects with comprehensive columns (A-Y)
- ⚠️ Country_Regions with 54 countries (needs expansion to 94)
- ⚠️ Milestones with MS-001 format (needs PRJ-XXX-MS-XXX)
- ⚠️ Events with EVT-001 format (needs PRJ-XXX-EVT-XXX)
- ⚠️ Country_Budgets missing Spent and Funding_Gap columns
- ⚠️ Master_Projects missing Project_Manager column

---

## PRIORITY 1: ADD PROJECT MANAGER COLUMN

**Current Master_Projects structure:** Columns A-Y (25 columns)
- Column Y is currently: NCE_Status

**Action:**
1. Open **Master_Projects** sheet
2. Click on column Z (first empty column)
3. In Z1, type: `Project_Manager`
4. Format to match other headers (bold, light blue fill if applicable)
5. Leave Z2-Z11 empty for now

**Time:** 1 minute

---

## PRIORITY 2: EXPAND COUNTRY_REGIONS TO 94 COUNTRIES

**Current:** 54 countries
**Target:** 94 countries across 6 regions

**Action:**
1. Open **Country_Regions** sheet
2. Current headers: Country_Code, Country_Name, Region, EU_Member
3. Select all data rows (row 2 to row 54)
4. Delete all data rows (keep header row 1)
5. Open the file: `94_COUNTRIES_DATA.txt`
6. Copy all country data
7. Paste into Country_Regions starting at A2
8. Add Region column data (see mapping below)
9. EU_Member column can be filled later or left blank

**Region Mapping:**
- EUR countries → Column C: EUR
- WHA countries → Column C: WHA
- EAP countries → Column C: EAP
- AF countries → Column C: AF
- NEA countries → Column C: NEA
- SCA countries → Column C: SCA

**Quick Method for Column C (Region):**
1. In C2, type: EUR (for Albania)
2. Copy EUR down to row 45 (all EUR countries)
3. In C46, type: WHA (for Antigua and Barbuda)
4. Copy WHA down to row 65 (all WHA countries)
5. Continue for EAP, AF, NEA, SCA

**Time:** 10 minutes

---

## PRIORITY 3: UPDATE MILESTONE IDs

**Current format:** MS-001, MS-002, etc.
**Target format:** PRJ-XXX-MS-XXX

**Context:**
- Milestones sheet has 30 milestones (rows 2-31)
- Column A: Milestone_ID
- Column C: Unique_ID (this is the Project_ID)

**Method 1: Formula Helper Column**
1. Open **Milestones** sheet
2. Insert a temporary column after column A
3. In new B2, enter formula: `=C2&"-"&A2`
   - Example: If C2=PRJ-001 and A2=MS-001, result is PRJ-001-MS-001
4. Copy formula down to row 31
5. Copy the results (B2:B31)
6. Select original A2:A31
7. Paste Special > Values
8. Delete the temporary column B

**Method 2: Find & Replace (if all milestones belong to specific projects)**
1. Identify which milestones belong to which project
2. Use Find & Replace:
   - Find: MS-
   - Replace: PRJ-001-MS- (for project 1's milestones)
3. Repeat for each project's milestones

**Method 3: Manual (if only a few milestones)**
1. Click cell A2
2. Look at C2 to see Project_ID (e.g., PRJ-001)
3. Change A2 from MS-001 to PRJ-001-MS-001
4. Repeat for each row

**Time:** 10-15 minutes

---

## PRIORITY 4: UPDATE EVENT IDs

**Current format:** EVT-001
**Target format:** PRJ-XXX-EVT-XXX

**Context:**
- Events sheet has 1 event (row 2)
- Column A: Event_ID
- Column B: Unique_ID (this is the Project_ID)

**Action:**
1. Open **Events** sheet
2. Look at B2 to see the Project_ID (e.g., PRJ-001)
3. Change A2 from EVT-001 to PRJ-001-EVT-001
4. Repeat for any additional events

**Time:** 1-2 minutes

---

## PRIORITY 5: CREATE COUNTRY_PM_ASSIGNMENTS SHEET

**Purpose:** Map each country to its assigned Project Manager

**Action:**
1. Right-click on any sheet tab
2. Insert > Worksheet
3. Rename to: `Country_PM_Assignments`
4. Create headers:
   - A1: Country_Code
   - B1: Project_Manager
5. In A2, copy the country codes from Country_Regions column A
   - Should have 94 country codes (AL, AM, AT, etc.)
6. In column B, add PM names based on region:

**PM Assignment by Region:**
```
EUR countries (AL-GB): [Your EUR PM Name]
WHA countries (AG-VE): [Your WHA PM Name]
EAP countries (AU-VN): [Your EAP PM Name]
AF countries (AO-TZ): [Your AF PM Name]
NEA countries (DZ-YE): [Your NEA PM Name]
SCA countries (AF-UZ): [Your SCA PM Name]
```

**Quick Method:**
1. In B2, use formula: `=VLOOKUP(A2,Country_Regions!A:C,3,FALSE)`
   - This gets the region code
2. Copy down to B95
3. Then use Find & Replace:
   - Replace "EUR" with "Jane Smith" (your EUR PM)
   - Replace "WHA" with "John Doe" (your WHA PM)
   - Etc.

**Time:** 10 minutes

---

## PRIORITY 6: ADD PM LOOKUP FORMULA TO MASTER_PROJECTS

**Purpose:** Show which PM(s) are responsible for each project based on countries

**Action:**
1. Open **Master_Projects** sheet
2. Column Z is Project_Manager (you added in Priority 1)
3. Column R has "Countries" (comma-separated list)
4. In Z2, we need a formula to look up PMs

**Formula Option 1 (if you have Excel 365):**
```excel
=TEXTJOIN(", ",TRUE,UNIQUE(FILTERXML("<t><s>"&SUBSTITUTE(R2,",","</s><s>")&"</s></t>","//s[.!='']")))
```
This is complex - see Option 2 instead.

**Formula Option 2 (simpler, works in all Excel versions):**
```excel
=VLOOKUP(LEFT(R2,2),Country_PM_Assignments!A:B,2,FALSE)
```
This looks up the first country code in column R and returns its PM.

**Formula Option 3 (if you want ALL PMs for all countries):**
Since countries are comma-separated in R2, you may need manual entry or a complex formula.

**Recommended: Manual Entry for Now**
1. For each project (rows 2-11), look at column R (Countries)
2. Determine which region(s) those countries belong to
3. Type the appropriate PM name(s) in column Z
4. Example:
   - If R2 = "Germany, France" → Z2 = "Jane Smith" (EUR PM)
   - If R3 = "Brazil, Argentina" → Z3 = "John Doe" (WHA PM)
   - If R4 = "Germany, Japan" → Z4 = "Jane Smith, Kenji Tanaka" (EUR + EAP PMs)

**Time:** 5 minutes (manual) or 15 minutes (formula)

---

## PRIORITY 7: UPDATE COUNTRY_BUDGETS STRUCTURE

**Current columns:**
- A: Budget_ID
- B: Unique_ID
- C: Country_Code
- D: Country_Name
- E: Allocated_Amount
- F: Obligated_Amount
- G: ULO (currently = E-F, but should be F-Spent)
- H: ULO_Percent
- I: Spend_Health

**Target structure:**
- A: Budget_ID
- B: Unique_ID
- C: Country_Code
- D: Country_Name
- E: Allocated_Amount
- F: Obligated_Amount
- G: **Spent** (NEW)
- H: ULO (formula update)
- I: ULO_Percent (formula update)
- J: **Funding_Gap** (NEW)
- K: Spend_Health

**Action:**

### Step 1: Insert Spent column
1. Open **Country_Budgets** sheet
2. Right-click on column G header (ULO)
3. Click "Insert"
4. This creates a new column G, pushing ULO to column H
5. In G1, type: `Spent`
6. Format to match other headers

### Step 2: Insert Funding_Gap column
1. Right-click on column K header (Spend_Health)
2. Click "Insert"
3. New column K is created
4. In K1, type: `Funding_Gap`
5. Rename old column K (now L) back to: `Spend_Health`

**Wait, this is getting complex with column shifts. Better approach:**

### Alternative: Add columns at the end
1. In column J1, type: `Spent`
2. In column K1, type: `Funding_Gap`
3. Keep current columns A-I as-is for now

### Step 3: Add Spent data
1. In J2, enter actual spending data if you have it
2. OR use estimate: `=F2*0.75` (75% of Obligated)
3. Copy down to row 31

### Step 4: Update ULO formula
1. Click on G2 (ULO column)
2. If current formula is `=E2-F2`, change to: `=F2-J2`
   - This makes ULO = Obligated - Spent (money on hand but not spent)
3. Copy down to row 31

### Step 5: Update ULO_Percent formula
1. Click on H2
2. Formula should be: `=IF(F2=0,0,G2/F2)`
   - ULO_Percent = ULO / Obligated
3. Format as Percentage
4. Copy down to row 31

### Step 6: Add Funding_Gap formula
1. Click on K2
2. Enter formula: `=E2-F2`
   - Funding_Gap = Allocated - Obligated (money promised but not received)
3. Copy down to row 31

### Step 7: Update Spend_Health (if needed)
1. Current formula might reference ULO_Percent
2. Update if necessary to: `=IF(H2<0.1,"Low Execution",IF(H2>0.6,"Slow Execution","On Track"))`

**Time:** 15 minutes

**NOTE:** This change is complex due to column shifts affecting formulas. Consider doing this last and carefully.

---

## PRIORITY 8: UPDATE STAKEHOLDERS (OPTIONAL ENHANCEMENT)

**Current columns:** 12 columns
- Stakeholder_ID, Name, Email, Phone, Organization, Stakeholder_Type, Project_IDs, Role, Contact_Frequency, Last_Contact, Next_Contact, Notes

**Enhancement: Add location and time zone columns**

**Action:**
1. Open **Stakeholders** sheet
2. After column E (Organization), insert 3 new columns:
   - F: Location_City
   - G: Location_Country
   - H: Time_Zone_Offset
3. After column H, insert another column:
   - I: Local_Time
4. In I2, add formula: `=NOW()+(H2/24)`
   - This calculates local time based on UTC offset
5. Format column I as Time format

**New column order:**
A: Stakeholder_ID
B: Name
C: Email
D: Phone
E: Organization
F: Location_City (NEW)
G: Location_Country (NEW)
H: Time_Zone_Offset (NEW - enter like +1, -5, etc.)
I: Local_Time (NEW - auto-calculated)
J: Stakeholder_Type
K: Project_IDs
L: Role
M: Contact_Frequency
N: Last_Contact
O: Next_Contact
P: Notes

**Time:** 10 minutes

---

## PRIORITY 9: CHANGE FUNDING FORMAT FROM K TO M

**Check if needed:** Look at Portfolio_Dashboard and other sheets to see if funding is displayed as thousands (K) or millions (M)

**Action if needed:**
1. Open **Portfolio_Dashboard** sheet
2. Find cells with large dollar amounts
3. Check the number format:
   - Right-click cell > Format Cells > Custom
4. If format shows `$#,##0,K` or similar:
   - Change to: `$#,##0.0,M`
5. Apply to all relevant budget cells
6. Repeat for any other sheets showing budget data

**Quick method:**
1. Press Ctrl+H (Find & Replace)
2. Click Options > Search: Workbook
3. Find what: `,K`
4. Replace with: `.0,M`
5. Replace All

**Time:** 3 minutes

---

## PRIORITY 10: UPDATE PROJECT SPOTLIGHT (ADD PROJECT_TECHNOLOGIES)

**Check current state:**
1. Open **Project_Spotlight** sheet
2. See if there's already a Technologies section

**If NOT present, add it:**

### Create Project_Technologies sheet (if doesn't exist)
1. Right-click sheet tab > Insert > Worksheet
2. Name it: `Project_Technologies`
3. Headers:
   - A: Project_ID
   - B: Technology_Area
   - C: Priority
   - D: Status
   - E: Notes
4. Add sample data:
```
PRJ-001	Cloud Computing	High	Active	AWS/Azure
PRJ-001	AI/ML	High	Active	Machine Learning
PRJ-002	Cybersecurity	Critical	Active	Zero Trust
```

### Add section to Project Spotlight
1. Open **Project_Spotlight** sheet
2. Find the first empty area (likely after existing sections)
3. Create header row:
   - Merge cells B[row]:G[row]
   - Type: TARGET TECHNOLOGIES
   - Format: Bold, white text, dark blue fill (#366092)
4. Next row, add column headers:
   - B: Technology Area
   - C: Priority
   - D: Status
   - E: Notes
   - Format: Bold, light blue fill (#E8F4FD)
5. Leave 4-5 rows blank below for data
6. Add placeholder text in first data row:
   - "[Technologies will appear here - add manually or use FILTER formula]"

**Time:** 10 minutes

---

## FINAL VERIFICATION CHECKLIST

After completing all changes:

[ ] **Master_Projects** - Column Z has "Project_Manager" header
[ ] **Milestones** - All 30 IDs in format PRJ-XXX-MS-XXX
[ ] **Events** - ID in format PRJ-XXX-EVT-XXX
[ ] **Country_Regions** - 94 countries listed with Region codes
[ ] **Country_PM_Assignments** - New sheet created with 94 countries and PM names
[ ] **Country_Budgets** - Columns for Spent and Funding_Gap added
[ ] **Stakeholders** - Location and time zone columns added (if doing Priority 8)
[ ] **Portfolio_Dashboard** - Funding displayed in millions (M) not thousands (K)
[ ] **Project_Technologies** - New sheet created (if not exists)
[ ] **Project_Spotlight** - Technologies section added (if not exists)

**Test:**
1. Open the file - does it open without errors?
2. Check a few formulas - do they calculate correctly?
3. Change project selection in Project_Spotlight - does it work?

---

## RECOMMENDED ORDER OF WORK

**Do in this order to minimize issues:**

1. ✅ Priority 1: Add Project_Manager column (1 min)
2. ✅ Priority 2: Expand Country_Regions (10 min)
3. ✅ Priority 5: Create Country_PM_Assignments (10 min)
4. ✅ Priority 6: Add PM lookup to Master_Projects (5 min)
5. ✅ Priority 3: Update Milestone IDs (15 min)
6. ✅ Priority 4: Update Event IDs (2 min)
7. ✅ Priority 9: Change K to M format (3 min)
8. ⚠️ Priority 7: Update Country_Budgets (15 min) - SAVE BEFORE THIS
9. 📋 Priority 8: Update Stakeholders - OPTIONAL (10 min)
10. 📋 Priority 10: Update Project Spotlight - OPTIONAL (10 min)

**Total time: 1-1.5 hours for required changes**

---

## TIPS FOR SUCCESS

1. **Save frequently** - After every 2-3 changes, save the file
2. **Save before Priority 7** - Country_Budgets changes are the most complex
3. **One sheet at a time** - Complete all changes for one sheet before moving to next
4. **Keep this file open** - Refer back as you work
5. **Don't rush** - Take breaks between major changes

---

## IF SOMETHING BREAKS

If you make a change and the file won't save or shows errors:

1. **Don't save** - Close without saving
2. **Reopen your backup**
3. **Skip that change** or try a different approach
4. **Ask for help** if needed

The most risky change is Priority 7 (Country_Budgets) because it shifts columns and affects formulas. Everything else is relatively safe.

---

## NEED HELP?

Ask about:
- Specific formula syntax
- Which cells to select
- How to format something
- Alternative approaches for tricky changes

Good luck! You've got this! 🎯
