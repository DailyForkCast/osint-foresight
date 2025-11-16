# Manual Formula Entry Guide - 5 Minutes to Fix Project_Spotlight

**File to use:** `2025-10-26-Tracker-v8.1.xlsx` (this one works without corruption)
**Time needed:** 5 minutes
**Difficulty:** Easy - just copy and paste

---

## 🎯 WHAT WE'RE DOING

Excel keeps removing FILTER formulas when we add them programmatically. So we'll add them manually instead.

You'll copy formulas from this guide and paste them into Excel. That's it!

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### SETUP (1 minute)

1. **Open:** `2025-10-26-Tracker-v8.1.xlsx` in Excel 365
2. **Go to:** Project_Spotlight sheet
3. **Verify:** Cell B2 contains "PRJ-001"

---

### SECTION 1: TARGET AUDIENCES (1 minute)

**Location:** Rows 6-14, Columns G-I

#### Step 1A: Clear the area
1. Select cells **G6:I14** (click G6, drag to I14)
2. Press **Delete** to clear

#### Step 1B: Add formulas
Click **G6** and paste this formula:
```
=IFERROR(FILTER(T_Project_Audiences[Audience_Type],T_Project_Audiences[Project_ID]=$B$2),"")
```

Click **H6** and paste this formula:
```
=IFERROR(FILTER(T_Project_Audiences[Description],T_Project_Audiences[Project_ID]=$B$2),"")
```

Click **I6** and paste this formula:
```
=IFERROR(FILTER(T_Project_Audiences[Priority],T_Project_Audiences[Project_ID]=$B$2),"")
```

**Result:** If audiences exist for PRJ-001, they'll appear. Otherwise cells stay blank (normal).

---

### SECTION 2: TARGET TECHNOLOGIES (1 minute)

**Location:** Rows 6-14, Columns J-K

#### Step 2A: Clear the area
1. Select cells **J6:K14**
2. Press **Delete**

#### Step 2B: Add formulas
Click **J6** and paste this formula:
```
=IFERROR(FILTER(Project_Technologies[Technology],Project_Technologies[Project_ID]=$B$2),"")
```

Click **K6** and paste this formula:
```
=IFERROR(FILTER(Project_Technologies[Category],Project_Technologies[Project_ID]=$B$2),"")
```

**Result:** If technologies exist for PRJ-001, they'll appear. Otherwise cells stay blank (normal).

---

### SECTION 3: KEY DELIVERABLES (2 minutes)

**Location:** Rows 18-27, Columns B-F

#### Step 3A: Clear the area
1. Select cells **B18:F27**
2. Press **Delete**

#### Step 3B: Add formulas

Click **B18** and paste:
```
=IFERROR(FILTER(T_Project_Deliverables[Deliverable_Name],T_Project_Deliverables[Project_ID]=$B$2),"")
```

Click **C18** and paste:
```
=IFERROR(FILTER(T_Project_Deliverables[Due_Date],T_Project_Deliverables[Project_ID]=$B$2),"")
```

Click **D18** and paste:
```
=IFERROR(FILTER(T_Project_Deliverables[Status],T_Project_Deliverables[Project_ID]=$B$2),"")
```

Click **E18** and paste:
```
=IFERROR(FILTER(T_Project_Deliverables[Owner],T_Project_Deliverables[Project_ID]=$B$2),"")
```

Click **F18** and paste:
```
=IFERROR(FILTER(T_Project_Deliverables[Completion_Percent],T_Project_Deliverables[Project_ID]=$B$2),"")
```

**Result:** You should see:
- B18: "Technical Requirements Doc"
- B19: "Beta Release"
- Other columns populate automatically
- Rows 20-27 stay blank (no more deliverables for PRJ-001)

**If you see #SPILL! error:** Clear rows 19-27 (they're blocking the spill area)

---

### SECTION 4: KEY STAKEHOLDERS (1 minute)

**Location:** Starting at Row 30

#### Step 4A: Add section header
1. Click **B29**
2. Type: `KEY STAKEHOLDERS`
3. **Bold it** (Ctrl+B)
4. Optional: Apply blue fill (Home → Fill Color → Blue)

#### Step 4B: Add column headers
In row 30, add headers:
- **B30:** Name
- **C30:** Title
- **D30:** Organization
- **E30:** Email
- **F30:** Type

**Bold row 30** (select B30:F30, press Ctrl+B)

#### Step 4C: Clear data area
1. Select **B31:F40**
2. Press **Delete**

#### Step 4D: Add formulas

Click **B31** and paste:
```
=IFERROR(FILTER(Stakeholders[Name],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
```

Click **C31** and paste:
```
=IFERROR(FILTER(Stakeholders[Title],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
```

Click **D31** and paste:
```
=IFERROR(FILTER(Stakeholders[Organization],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
```

Click **E31** and paste:
```
=IFERROR(FILTER(Stakeholders[Email],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
```

Click **F31** and paste:
```
=IFERROR(FILTER(Stakeholders[Stakeholder_Type],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
```

**Result:** If stakeholders exist for PRJ-001, they'll appear. Otherwise cells stay blank.

---

### FINAL STEP: SAVE

1. **File → Save As**
2. Save as: `2025-10-26-Tracker-v9.2-MANUAL.xlsx`
3. Done! 🎉

---

## ✅ VERIFICATION

After completing all sections:

### Test 1: Deliverables show up
- B18 = "Technical Requirements Doc" ✅
- B19 = "Beta Release" ✅

### Test 2: Dynamic updates work
1. Click **B2**
2. Change from "PRJ-001" to "PRJ-002"
3. All sections update to show PRJ-002's data
4. Change back to "PRJ-001"
5. Sections update back

### Test 3: No errors
- No #SPILL! errors
- No #CALC! errors
- No #REF! errors

---

## 🚨 TROUBLESHOOTING

### Issue: #SPILL! error
**Cause:** Cells below the formula have content blocking the spill

**Solution:**
- For audiences (G6): Clear G7:I14
- For technologies (J6): Clear J7:K14
- For deliverables (B18): Clear B19:F27
- For stakeholders (B31): Clear B32:F40

### Issue: #CALC! error
**Cause:** FILTER function not recognized (not Excel 365)

**Solution:** Verify you have Excel 365 subscription (not standalone 2016/2019/2021)

### Issue: Formulas show but cells are blank
**Cause:** No data exists for selected project

**Solutions:**
- Check B2 contains valid project (e.g., "PRJ-001")
- Check Project_Deliverables sheet has deliverables for PRJ-001
- Verify table names are correct:
  - `T_Project_Deliverables`
  - `T_Project_Audiences`
  - `Project_Technologies`
  - `Stakeholders`

---

## 📊 WHAT EACH FORMULA DOES

### FILTER() basics:
```excel
=FILTER(what_to_show, condition, if_empty)
```

**Example:**
```excel
=FILTER(T_Project_Deliverables[Deliverable_Name], T_Project_Deliverables[Project_ID]=$B$2, "")
```
- **what_to_show:** Deliverable_Name column
- **condition:** Where Project_ID matches B2 (PRJ-001)
- **if_empty:** Show "" (blank) if no matches

### Auto-spilling:
When FILTER returns multiple results:
- Formula in B18 returns 2 deliverables
- Excel automatically fills B18 = 1st result
- Excel automatically fills B19 = 2nd result
- B20-B27 stay blank (no more results)

You **cannot edit B19-B27** - they're controlled by the B18 formula!

### Stakeholder SEARCH:
```excel
=FILTER(Stakeholders[Name], ISNUMBER(SEARCH($B$2, Stakeholders[Project_IDs])), "")
```

**SEARCH($B$2, Stakeholders[Project_IDs]):**
- Looks for "PRJ-001" in Project_IDs column
- Finds it in "PRJ-001, PRJ-003"
- Returns position (1)

**ISNUMBER(...):**
- If found, returns TRUE
- If not found, returns FALSE

**FILTER(..., TRUE/FALSE):**
- Shows rows where TRUE
- Hides rows where FALSE

This allows comma-separated Project_IDs to work!

---

## 🎯 QUICK REFERENCE - ALL FORMULAS

### Target Audiences:
```
G6: =IFERROR(FILTER(T_Project_Audiences[Audience_Type],T_Project_Audiences[Project_ID]=$B$2),"")
H6: =IFERROR(FILTER(T_Project_Audiences[Description],T_Project_Audiences[Project_ID]=$B$2),"")
I6: =IFERROR(FILTER(T_Project_Audiences[Priority],T_Project_Audiences[Project_ID]=$B$2),"")
```

### Target Technologies:
```
J6: =IFERROR(FILTER(Project_Technologies[Technology],Project_Technologies[Project_ID]=$B$2),"")
K6: =IFERROR(FILTER(Project_Technologies[Category],Project_Technologies[Project_ID]=$B$2),"")
```

### Key Deliverables:
```
B18: =IFERROR(FILTER(T_Project_Deliverables[Deliverable_Name],T_Project_Deliverables[Project_ID]=$B$2),"")
C18: =IFERROR(FILTER(T_Project_Deliverables[Due_Date],T_Project_Deliverables[Project_ID]=$B$2),"")
D18: =IFERROR(FILTER(T_Project_Deliverables[Status],T_Project_Deliverables[Project_ID]=$B$2),"")
E18: =IFERROR(FILTER(T_Project_Deliverables[Owner],T_Project_Deliverables[Project_ID]=$B$2),"")
F18: =IFERROR(FILTER(T_Project_Deliverables[Completion_Percent],T_Project_Deliverables[Project_ID]=$B$2),"")
```

### Key Stakeholders:
```
B31: =IFERROR(FILTER(Stakeholders[Name],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
C31: =IFERROR(FILTER(Stakeholders[Title],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
D31: =IFERROR(FILTER(Stakeholders[Organization],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
E31: =IFERROR(FILTER(Stakeholders[Email],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
F31: =IFERROR(FILTER(Stakeholders[Stakeholder_Type],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
```

---

## ✨ OPTIONAL: VISUAL ENHANCEMENTS

After adding formulas, make it prettier:

### Section Headers:
Apply to cells that say "TARGET AUDIENCES", "TARGET TECHNOLOGIES", "KEY DELIVERABLES", "KEY STAKEHOLDERS":
1. Select header cell
2. **Font:** White (Home → Font Color → White)
3. **Fill:** Blue (Home → Fill Color → Blue, Accent 1, Darker 25%)
4. **Bold:** Ctrl+B
5. **Size:** 11pt

### Column Headers:
Make headers bold (row 5 for audiences/technologies, row 17 for deliverables, row 30 for stakeholders)

---

## 🎉 YOU'RE DONE!

**Time spent:** ~5 minutes
**Result:** Fully functional Project_Spotlight with:
- ✅ Dynamic deliverables filtering
- ✅ Dynamic audiences filtering
- ✅ Dynamic technologies filtering
- ✅ Dynamic stakeholders filtering (with comma-separated Project_IDs!)
- ✅ Auto-spilling results
- ✅ Updates when you change project in B2

**Save as:** `2025-10-26-Tracker-v9.2-MANUAL.xlsx`

**Next:** Start adding your own data and enjoy your tracker!

---

**If you have any issues, let me know which section/cell is giving trouble!**
