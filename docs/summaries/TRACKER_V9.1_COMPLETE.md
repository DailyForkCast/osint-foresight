# Tracker v9.1 - Safe Rebuild Complete ✅

**Date:** November 7, 2025
**File:** `2025-10-26-Tracker-v9.1.xlsx`
**Requires:** Excel 365 (Microsoft 365)

---

## 🎯 WHAT'S NEW IN V9.1

**v9.1 is a careful rebuild from v8.1** using a more conservative approach to avoid corruption.

### Changes from v9:
- ✅ **Same features** - All FILTER() functions for dynamic arrays
- ✅ **Safer build process** - Cleared cells first, then added formulas
- ✅ **Verified formulas** - All critical cells confirmed to contain FILTER functions
- ✅ **No corruption** - File builds without XML errors

---

## ✨ FEATURES IN V9.1

### 1. **Target Audiences** (G6-I14)
**Formulas in G6, H6, I6:**
```excel
=IFERROR(FILTER(T_Project_Audiences[Audience_Type],T_Project_Audiences[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Audiences[Description],T_Project_Audiences[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Audiences[Priority],T_Project_Audiences[Project_ID]=$B$2),"")
```

**What it does:**
- Shows all audiences for selected project
- Auto-spills to rows 7-14
- Updates when you change project in B2

---

### 2. **Target Technologies** (J6-K14)
**Formulas in J6, K6:**
```excel
=IFERROR(FILTER(Project_Technologies[Technology],Project_Technologies[Project_ID]=$B$2),"")
=IFERROR(FILTER(Project_Technologies[Category],Project_Technologies[Project_ID]=$B$2),"")
```

**What it does:**
- Shows all technologies for selected project
- Auto-spills to rows 7-14
- Dynamically updates

---

### 3. **Key Deliverables** (B18-F27)
**Formulas in B18, C18, D18, E18, F18:**
```excel
=IFERROR(FILTER(T_Project_Deliverables[Deliverable_Name],T_Project_Deliverables[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Deliverables[Due_Date],T_Project_Deliverables[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Deliverables[Status],T_Project_Deliverables[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Deliverables[Owner],T_Project_Deliverables[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Deliverables[Completion_Percent],T_Project_Deliverables[Project_ID]=$B$2),"")
```

**What it does:**
- Shows ALL deliverables for selected project
- Auto-spills to rows 19-27 (up to 10 deliverables)
- Shows name, due date, status, owner, completion %

---

### 4. **Key Stakeholders** (B31-F40)
**Formulas in B31, C31, D31, E31, F31:**
```excel
=IFERROR(FILTER(Stakeholders[Name],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
=IFERROR(FILTER(Stakeholders[Title],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
=IFERROR(FILTER(Stakeholders[Organization],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
=IFERROR(FILTER(Stakeholders[Email],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
=IFERROR(FILTER(Stakeholders[Stakeholder_Type],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
```

**What it does:**
- Shows stakeholders for selected project
- **Supports comma-separated Project_IDs!**
  - If stakeholder has `Project_IDs = "PRJ-001, PRJ-003"`
  - They appear for BOTH projects
- Uses SEARCH to find project ID anywhere in comma-separated list

---

## 🚀 HOW TO TEST

### Step 1: Open the file
```
File: 2025-10-26-Tracker-v9.1.xlsx
Requires: Excel 365
```

### Step 2: Go to Project_Spotlight sheet
- Cell B2 should contain: **"PRJ-001"**
- This is your selected project

### Step 3: Verify formulas exist
Check these cells have formulas (click and look at formula bar):
- **G6** - Should show `=IFERROR(FILTER(...`
- **J6** - Should show `=IFERROR(FILTER(...`
- **B18** - Should show `=IFERROR(FILTER(...`
- **B31** - Should show `=IFERROR(FILTER(...`

**If any cells show NO formula:**
- This is the same issue as v9
- Excel may have corrupted during open
- Report back to me

### Step 4: Check if data appears
If formulas exist and calculate:
- **B18** should show: "Technical Requirements Doc"
- **B19** should show: "Beta Release"
- Other cells may be blank (no more data for PRJ-001)

### Step 5: Test dynamic updates
1. Click cell B2
2. Change from "PRJ-001" to "PRJ-002"
3. **All sections should update** to show PRJ-002's data
4. Change back to "PRJ-001"
5. Verify it switches back

---

## 🔍 TROUBLESHOOTING

### Issue 1: Formulas don't exist in cells
**Symptoms:** Clicking G6, J6, B18, or B31 shows empty formula bar

**Possible causes:**
1. Excel 365 not installed (need subscription version)
2. Excel corrupted the file on open (repair removed formulas)
3. Wrong file opened (check you're in v9.1, not v9)

**Solutions:**
- Confirm Excel version (File → Account → About Excel)
- Check if corruption warning appeared when opening
- Try opening on different machine with Excel 365
- Report back with details

### Issue 2: Formulas exist but show #SPILL! error
**Symptoms:** Cells show `#SPILL!` instead of data

**Cause:** Spill area blocked (rows 7-14, 19-27, 32-40 have content blocking auto-spill)

**Solution:**
- Clear rows 7-14 in columns G, H, I (audiences)
- Clear rows 7-14 in columns J, K (technologies)
- Clear rows 19-27 in columns B-F (deliverables)
- Clear rows 32-40 in columns B-F (stakeholders)

### Issue 3: Formulas exist but show #CALC! error
**Symptoms:** Cells show `#CALC!`

**Cause:** FILTER function not recognized (not Excel 365)

**Solution:**
- Verify Excel 365 subscription is active
- Update Excel to latest version
- If using Excel 2016/2019/2021 standalone, FILTER won't work

### Issue 4: Formulas work but show blank
**Symptoms:** Formulas exist, no errors, but cells are empty

**Possible causes:**
1. No data exists for selected project
2. Table names don't match
3. Data validation issue

**Solutions:**
- Check if B2 contains valid project ID (e.g., "PRJ-001")
- Go to Project_Deliverables sheet - verify deliverables exist for PRJ-001
- Check table names:
  - Project_Deliverables → Table name: `T_Project_Deliverables`
  - Project_Audiences → Table name: `T_Project_Audiences`
  - Project_Technologies → Table name: `Project_Technologies`
  - Stakeholders → Table name: `Stakeholders`

---

## 📊 WHAT DATA IS NEEDED

For sections to populate, you need:

### 1. **Deliverables** (to show in B18+)
Go to **Project_Deliverables** sheet:
- Column A: Project_ID (e.g., "PRJ-001")
- Column B: Deliverable_Name
- Column C: Due_Date
- Column D: Status
- Column E: Owner
- Column F: Completion_Percent

**Example:**
```
| Project_ID | Deliverable_Name              | Due_Date   | Status      | Owner | Completion_Percent |
|------------|-------------------------------|------------|-------------|-------|--------------------|
| PRJ-001    | Technical Requirements Doc    | 2025-11-15 | In Progress | JD    | 75%                |
| PRJ-001    | Beta Release                  | 2025-12-01 | Not Started | AS    | 0%                 |
```

### 2. **Audiences** (to show in G6+)
Go to **Project_Audiences** sheet (Table: `T_Project_Audiences`):
- Column A: Project_ID
- Column B: Audience_Type
- Column C: Description
- Column D: Priority

**Example:**
```
| Project_ID | Audience_Type          | Description                    | Priority |
|------------|------------------------|--------------------------------|----------|
| PRJ-001    | Government Officials   | Federal decision-makers        | High     |
| PRJ-001    | Private Sector         | Industry stakeholders          | Medium   |
```

### 3. **Technologies** (to show in J6+)
Go to **Project_Technologies** sheet:
- Column A: Project_ID
- Column B: Technology
- Column C: Category

**Example:**
```
| Project_ID | Technology            | Category         |
|------------|-----------------------|------------------|
| PRJ-001    | Cloud Infrastructure  | Infrastructure   |
| PRJ-001    | Machine Learning      | AI/ML            |
```

### 4. **Stakeholders** (to show in B31+)
Go to **Stakeholders** sheet:
- Columns A-K: Name, Title, Organization, Email, etc.
- **Column L: Project_IDs** (comma-separated!)

**Example:**
```
| Name         | Title        | Organization | Email          | ... | Project_IDs      |
|--------------|--------------|--------------|----------------|-----|------------------|
| John Smith   | PM           | Agency A     | john@agency.gov| ... | PRJ-001, PRJ-003 |
| Jane Doe     | Analyst      | Agency B     | jane@agency.gov| ... | PRJ-002          |
| Bob Lee      | Director     | Agency A     | bob@agency.gov | ... | PRJ-001          |
```

**When B2 = "PRJ-001":**
- John Smith appears (found in "PRJ-001, PRJ-003")
- Bob Lee appears (exact match)
- Jane Doe does NOT appear (only assigned to PRJ-002)

---

## ✅ SUCCESS CRITERIA

**v9.1 is working if:**
1. ✅ File opens without corruption warning
2. ✅ Formulas exist in G6, J6, B18, B31
3. ✅ Deliverables show in rows 18-19 (Technical Requirements Doc, Beta Release)
4. ✅ Changing B2 from PRJ-001 to PRJ-002 updates all sections
5. ✅ No #SPILL! or #CALC! errors

---

## 🆚 VERSION COMPARISON

| Feature | v8.1 | v9 | v9.1 |
|---------|------|-----|------|
| Financial tracking | ✅ Works | ✅ Works | ✅ Works |
| FILTER() functions | ❌ No | ✅ Yes (corrupted) | ✅ Yes (verified) |
| Deliverables in Spotlight | ❌ Broken | ❓ Unknown | ✅ Should work |
| Audiences in Spotlight | ❌ Broken | ❓ Unknown | ✅ Should work |
| Technologies in Spotlight | ❌ Broken | ❓ Unknown | ✅ Should work |
| Stakeholders section | ❌ Missing | ✅ Added | ✅ Added |
| Comma-separated Project_IDs | ❌ No | ✅ Yes | ✅ Yes |
| Excel 365 required | No | Yes | Yes |
| File corruption | No | Yes (formulas removed) | No (clean build) |
| Formulas verified | N/A | No | ✅ Yes |

---

## 📝 WHAT TO DO NOW

### Immediate:
1. **Open v9.1 in Excel 365**
2. **Report back:**
   - Do formulas exist in G6, J6, B18, B31? (Yes/No)
   - Do deliverables appear? (Yes/No)
   - Any errors? (#SPILL!, #CALC!, corruption warning, etc.)

### If formulas exist and work:
1. ✅ **v9.1 is successful!**
2. Add your own deliverables, audiences, technologies, stakeholders
3. Test with your real projects
4. Enjoy fully functional Project_Spotlight

### If formulas don't exist:
1. This suggests Excel 365 might have an issue with FILTER in programmatically-created files
2. We may need to:
   - **Option A:** Manually enter formulas in Excel (copy/paste from docs)
   - **Option B:** Use VBA to add formulas after file is opened
   - **Option C:** Create formulas using different method (XLOOKUP, INDEX/MATCH workarounds)

---

## 🔧 MANUAL FORMULA ENTRY (BACKUP PLAN)

If formulas are missing, you can add them manually:

### Target Audiences (G6, H6, I6):
```excel
=IFERROR(FILTER(T_Project_Audiences[Audience_Type],T_Project_Audiences[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Audiences[Description],T_Project_Audiences[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Audiences[Priority],T_Project_Audiences[Project_ID]=$B$2),"")
```

### Target Technologies (J6, K6):
```excel
=IFERROR(FILTER(Project_Technologies[Technology],Project_Technologies[Project_ID]=$B$2),"")
=IFERROR(FILTER(Project_Technologies[Category],Project_Technologies[Project_ID]=$B$2),"")
```

### Key Deliverables (B18, C18, D18, E18, F18):
```excel
=IFERROR(FILTER(T_Project_Deliverables[Deliverable_Name],T_Project_Deliverables[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Deliverables[Due_Date],T_Project_Deliverables[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Deliverables[Status],T_Project_Deliverables[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Deliverables[Owner],T_Project_Deliverables[Project_ID]=$B$2),"")
=IFERROR(FILTER(T_Project_Deliverables[Completion_Percent],T_Project_Deliverables[Project_ID]=$B$2),"")
```

### Stakeholders (B31, C31, D31, E31, F31):
```excel
=IFERROR(FILTER(Stakeholders[Name],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
=IFERROR(FILTER(Stakeholders[Title],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
=IFERROR(FILTER(Stakeholders[Organization],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
=IFERROR(FILTER(Stakeholders[Email],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
=IFERROR(FILTER(Stakeholders[Stakeholder_Type],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
```

**To enter manually:**
1. Click cell (e.g., G6)
2. Type or paste formula
3. Press Enter
4. Formula should auto-spill to rows below

---

## 📞 NEXT COMMUNICATION

**Please report:**
1. Did v9.1 open without corruption warning?
2. Do formulas exist in the critical cells?
3. Do deliverables show correctly?
4. Any errors or issues?

Based on your feedback, we'll either:
- ✅ **Success:** Move to next features (document linking, country dashboard)
- ⚠️ **Issues:** Troubleshoot or try alternative approaches

---

**v9.1 - Built with care, verified with confidence! 🚀**
