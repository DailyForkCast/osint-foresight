# Manual Update Instructions for Project Tracker
**To avoid Excel corruption issues, follow these manual steps**

---

## ⚠️ WHY MANUAL UPDATES?

The Excel file contains:
- Excel Tables with structured references
- Complex merged cell regions
- Formulas referencing table columns

Programmatic changes via Python can break these structures. Manual updates preserve the Excel integrity.

---

## 📋 BEFORE YOU START

1. **Make a backup copy** of `2025-10-05-Tracker (1).xlsx`
2. Open the original file in Excel
3. Save it as: `2025-10-05-Tracker-UPDATED.xlsx`
4. Work in the new file

---

## CHANGE 1: Update Milestone IDs Format

### Current: MS-001, MS-002, etc.
### Target: PRJ-001-MS-001, PRJ-002-MS-002, etc.

**Manual Steps:**

1. Open **Milestones** sheet
2. Click on cell A2 (first Milestone_ID)
3. For each milestone, determine its Project_ID from column B
4. Update the ID manually following this pattern:
   - If Project_ID = PRJ-001 and old ID = MS-001, new ID = PRJ-001-MS-001
   - If Project_ID = PRJ-001 and old ID = MS-002, new ID = PRJ-001-MS-002
   - If Project_ID = PRJ-002 and old ID = MS-010, new ID = PRJ-002-MS-010

**Quick Method using Formula:**
1. Insert a temporary column after column A
2. In cell B2 (new temp column), enter: `=C2&"-MS-"&RIGHT(A2,3)`
   - Assuming C2 has the Project_ID
3. Copy this formula down for all rows
4. Copy the results and Paste Special > Values into column A
5. Delete the temporary column

**Estimated time**: 5-10 minutes for ~30 milestones

---

## CHANGE 2: Update Event IDs Format

### Current: EVT-001, EVT-002, etc.
### Target: PRJ-001-EVT-001, PRJ-002-EVT-002, etc.

**Manual Steps:**

1. Open **Events** sheet
2. Same process as Milestones
3. Formula for temp column: `=C2&"-EVT-"&RIGHT(A2,3)`

**Estimated time**: 2-3 minutes for few events

---

## CHANGE 3: Add Project Manager Column to Master_Projects

**Manual Steps:**

1. Open **Master_Projects** sheet
2. Click on column T (or the first empty column after existing data)
3. In cell T1, type: `Project_Manager`
4. Format the header to match other headers (bold, colored fill if applicable)
5. Leave cells T2-T11 empty for now (we'll add formulas in Change 5)

**Estimated time**: 1 minute

---

## CHANGE 4: Expand Country_Regions to 94 Countries

**Manual Steps:**

### Delete old data:
1. Open **Country_Regions** sheet
2. Select all rows with data (except header)
3. Delete the rows
4. Keep just the header row

### Add new regions and countries:

Copy and paste this data starting at row 2:

```
EUR	Albania
EUR	Armenia
EUR	Austria
EUR	Azerbaijan
EUR	Belarus
EUR	Belgium
EUR	Bosnia and Herzegovina
EUR	Bulgaria
EUR	Croatia
EUR	Cyprus
EUR	Czech Republic
EUR	Denmark
EUR	Estonia
EUR	Finland
EUR	France
EUR	Georgia
EUR	Germany
EUR	Greece
EUR	Hungary
EUR	Iceland
EUR	Ireland
EUR	Italy
EUR	Kosovo
EUR	Latvia
EUR	Lithuania
EUR	Luxembourg
EUR	Malta
EUR	Moldova
EUR	Montenegro
EUR	Netherlands
EUR	North Macedonia
EUR	Norway
EUR	Poland
EUR	Portugal
EUR	Romania
EUR	Serbia
EUR	Slovakia
EUR	Slovenia
EUR	Spain
EUR	Sweden
EUR	Switzerland
EUR	Turkey
EUR	Ukraine
EUR	United Kingdom
WHA	Antigua and Barbuda
WHA	Argentina
WHA	Bahamas
WHA	Barbados
WHA	Belize
WHA	Bolivia
WHA	Brazil
WHA	Canada
WHA	Chile
WHA	Colombia
WHA	Costa Rica
WHA	Dominica
WHA	Dominican Republic
WHA	Ecuador
WHA	El Salvador
WHA	Grenada
WHA	Guatemala
WHA	Guyana
WHA	Haiti
WHA	Honduras
WHA	Jamaica
WHA	Mexico
WHA	Nicaragua
WHA	Panama
WHA	Paraguay
WHA	Peru
WHA	Saint Kitts and Nevis
WHA	Saint Lucia
WHA	Saint Vincent and the Grenadines
WHA	Suriname
WHA	Trinidad and Tobago
WHA	United States
WHA	Uruguay
WHA	Venezuela
EAP	Australia
EAP	Brunei
EAP	Cambodia
EAP	China
EAP	Indonesia
EAP	Japan
EAP	Laos
EAP	Malaysia
EAP	Mongolia
EAP	Myanmar
EAP	New Zealand
EAP	Papua New Guinea
EAP	Philippines
EAP	Singapore
EAP	South Korea
EAP	Taiwan
EAP	Thailand
EAP	Vietnam
AF	Angola
AF	Botswana
AF	Ethiopia
AF	Ghana
AF	Kenya
AF	Nigeria
AF	Rwanda
AF	Senegal
AF	South Africa
AF	Tanzania
NEA	Algeria
NEA	Egypt
NEA	Iraq
NEA	Israel
NEA	Jordan
NEA	Lebanon
NEA	Morocco
NEA	Saudi Arabia
NEA	Tunisia
NEA	United Arab Emirates
NEA	Yemen
SCA	Afghanistan
SCA	India
SCA	Kazakhstan
SCA	Pakistan
SCA	Sri Lanka
SCA	Uzbekistan
```

**Estimated time**: 5 minutes (copy/paste)

---

## CHANGE 5: Create Country_PM_Assignments Sheet

**Manual Steps:**

1. Right-click on a sheet tab > Insert > Worksheet
2. Name it: `Country_PM_Assignments`
3. In A1, type: `Country_Code`
4. In B1, type: `Project_Manager`
5. Format headers (bold, colored fill to match other sheets)
6. Copy the country codes from Country_Regions column A
7. Paste into Country_PM_Assignments column A (starting at A2)
8. In column B, add PM names based on region:
   - For EUR countries: Type your EUR PM name
   - For WHA countries: Type your WHA PM name
   - For EAP countries: Type your EAP PM name
   - Etc.

**Quick Method:**
1. After pasting country codes, add this formula in B2: `=VLOOKUP(A2,Country_Regions!A:B,1,FALSE)`
   - This gets the region code
2. Then use Find & Replace to replace:
   - EUR → [Your EUR PM Name]
   - WHA → [Your WHA PM Name]
   - EAP → [Your EAP PM Name]
   - AF → [Your AF PM Name]
   - NEA → [Your NEA PM Name]
   - SCA → [Your SCA PM Name]

**Estimated time**: 10 minutes

---

## CHANGE 6: Add Project Manager Lookup to Master_Projects

**Manual Steps:**

1. Open **Master_Projects** sheet
2. Click on cell T2 (first data row under Project_Manager header)
3. We need to find which PMs are responsible based on countries involved
4. If your Excel has TEXTJOIN (Excel 2019+), use this formula:
   ```excel
   =TEXTJOIN(", ",TRUE,IF(ISNUMBER(SEARCH(Country_PM_Assignments!$A:$A,L2)),Country_PM_Assignments!$B:$B,""))
   ```
   - Press Ctrl+Shift+Enter (array formula)
5. If no TEXTJOIN, use simpler approach:
   ```excel
   =VLOOKUP(LEFT(L2,2),Country_PM_Assignments!A:B,2,FALSE)
   ```
   - This assumes column L has country codes
6. Copy formula down to all project rows

**Alternative - Manual Entry:**
- Just type the PM name for each project based on which countries are involved

**Estimated time**: 5 minutes (formula) or 3 minutes (manual)

---

## CHANGE 7: Update Funding Format from K to M

**Manual Steps:**

1. Open **Portfolio_Dashboard** sheet
2. Find cells with formulas that have `$#,##0,K` format
3. Right-click > Format Cells > Custom
4. Change format string from `$#,##0,K` to `$#,##0.0,M`
5. Check these specific cells (typically budget summary cells)

**Quick Method:**
1. Press Ctrl+H (Find & Replace)
2. Find what: `$#,##0,K`
3. Replace with: `$#,##0.0,M`
4. Click Options > Search: Formulas
5. Replace All

**Estimated time**: 2 minutes

---

## CHANGE 8: Redesign Stakeholders Sheet

**Manual Steps:**

### Add new columns:
1. Open **Stakeholders** sheet
2. After column D (Organization), insert these columns:
   - E: Location_City
   - F: Location_Country
   - G: Time_Zone_Offset
   - H: Local_Time
3. After existing columns, add:
   - Project_IDs (for project-specific stakeholders)
   - Countries (for location-specific)
   - Products (for product-specific)
   - Region (for regional stakeholders)
   - Theme (for thematic stakeholders)

### Complete column list:
```
A: Stakeholder_ID
B: Name
C: Title
D: Organization
E: Location_City
F: Location_Country
G: Time_Zone_Offset
H: Local_Time
I: Email
J: Phone
K: Stakeholder_Type
L: Project_IDs
M: Countries
N: Products
O: Region
P: Theme
Q: Influence_Level
R: Interest_Level
S: Contact_Frequency
T: Last_Contact
U: Next_Contact
V: Notes
```

### Add Local_Time formula:
1. In cell H2, enter: `=NOW()+(G2/24)`
2. Format as Time
3. Copy down for all rows

**Estimated time**: 15 minutes

---

## CHANGE 9: Update Country_Budgets Structure

**Manual Steps:**

### Insert new columns:
1. Open **Country_Budgets** sheet
2. Right-click on column G header > Insert
   - This creates space for "Spent" column
3. In new column G header, type: `Spent`
4. Right-click on column K header > Insert
   - This creates space for "Funding_Gap" column
5. In new column K header, type: `Funding_Gap`

### Update column headers (verify they're in right position):
```
E: Allocated
F: Obligated
G: Spent (NEW)
H: ULO
I: ULO_Percent
J: Funding_Gap (NEW)
K: Spend_Health
```

### Update formulas:
1. **Column H (ULO)** - Change formula to: `=F2-G2`
   - (Obligated - Spent)
2. **Column I (ULO_Percent)** - Change formula to: `=IF(F2=0,0,H2/F2)`
   - Format as Percentage
3. **Column J (Funding_Gap)** - New formula: `=E2-F2`
   - (Allocated - Obligated)
4. **Column K (Spend_Health)** - Update formula to: `=IF(I2<0.1,"Low Execution",IF(I2>0.6,"Slow Execution","On Track"))`

### Add Spent data:
1. In column G, add actual spending amounts (if you have them)
2. Or temporarily use: `=F2*0.7` (70% of obligated as estimate)

**Estimated time**: 10 minutes

---

## CHANGE 10: Create Project_Technologies Sheet

**Manual Steps:**

1. Right-click sheet tab > Insert > Worksheet
2. Name it: `Project_Technologies`
3. Create headers:
   ```
   A: Project_ID
   B: Technology_Area
   C: Priority
   D: Status
   E: Notes
   ```
4. Format headers (bold, colored fill)
5. Add sample data for your projects:
   ```
   PRJ-001	Cloud Computing	High	Active	AWS/Azure
   PRJ-001	AI/ML	High	Active	TensorFlow
   PRJ-002	Cybersecurity	Critical	Active	Zero Trust
   ```

**Estimated time**: 5 minutes

---

## CHANGE 11: Update Project Spotlight (Dynamic Sections)

**Manual Steps:**

### Clear old content:
1. Open **Project_Spotlight** sheet
2. Select rows 14 and below (if they have old map or content)
3. Delete those rows

### Add Target Technologies section:
1. In B14, type: `TARGET TECHNOLOGIES`
2. Format as header (bold, white text, dark blue fill)
3. Merge B14:G14
4. In row 15, add headers:
   - B15: Technology Area
   - C15: Priority
   - D15: Status
   - E15: Notes
5. Format as sub-headers (bold, light blue fill)
6. Leave rows 16-19 blank (for dynamic data or manual entry)

### Add Target Audiences section:
1. In B20, type: `TARGET AUDIENCES`
2. Format and merge B20:G20
3. In row 21, add headers:
   - B21: Audience Type
   - C21: Region
   - D21: Description
   - E21: Priority
4. Leave rows 22-25 blank

### Add Key Deliverables section:
1. In B26, type: `KEY DELIVERABLES`
2. Format and merge B26:G26
3. In row 27, add headers:
   - B27: Deliverable Name
   - C27: Type
   - D27: Due Date
   - E27: Status
   - F27: Owner
   - G27: Progress
4. Leave rows 28-31 blank

### Add instructions:
In B33, add note:
```
INSTRUCTIONS: Data can be:
1. Manually entered for each project, OR
2. Pulled dynamically using formulas (if Excel 365):
   =FILTER(Project_Technologies!B:E, Project_Technologies!A:A=$B$2, "")
```

**Estimated time**: 15 minutes

---

## CHANGE 12: Create Project_Audiences Sheet (Optional but Recommended)

**Manual Steps:**

1. Right-click sheet tab > Insert > Worksheet
2. Name it: `Project_Audiences`
3. Create headers:
   ```
   A: Project_ID
   B: Audience_Type
   C: Region
   D: Description
   E: Priority
   ```
4. Add sample data for your projects

**Estimated time**: 5 minutes

---

## FINAL VERIFICATION CHECKLIST

After making all changes, verify:

- [ ] Milestones sheet: All IDs in format PRJ-XXX-MS-XXX
- [ ] Events sheet: All IDs in format PRJ-XXX-EVT-XXX
- [ ] Master_Projects: Column T has Project_Manager
- [ ] Country_Regions: 94 countries across 6 regions
- [ ] Country_PM_Assignments: New sheet with 94 countries and PM names
- [ ] Stakeholders: 22 columns with multi-dimensional relationships
- [ ] Country_Budgets: Spent and Funding_Gap columns added
- [ ] Portfolio_Dashboard: Funding shows in millions (M not K)
- [ ] Project_Technologies: New sheet created
- [ ] Project_Spotlight: Dynamic sections added (rows 14-31)
- [ ] Project_Audiences: New sheet created (optional)

**Total estimated time**: 1.5 - 2 hours

---

## TIPS FOR SUCCESS

1. **Save frequently** - Save after each major change
2. **Test formulas** - After adding a formula, test it on one row before copying down
3. **Don't delete Tables** - If a sheet has an Excel Table, don't delete the table, just modify data
4. **Backup first** - Keep your original file safe
5. **One change at a time** - Complete each change fully before moving to the next

---

## IF YOU GET STUCK

Some changes are easier than others. Priority order:

**EASY (Do first):**
- Change 3: Add Project Manager column
- Change 4: Update Country_Regions
- Change 7: Update funding format
- Change 10: Create Project_Technologies

**MEDIUM:**
- Change 1: Update Milestone IDs
- Change 2: Update Event IDs
- Change 5: Create Country_PM_Assignments
- Change 11: Update Project Spotlight

**ADVANCED:**
- Change 6: Project Manager lookup formulas
- Change 8: Redesign Stakeholders
- Change 9: Update Country_Budgets

Start with the easy ones to build confidence!
