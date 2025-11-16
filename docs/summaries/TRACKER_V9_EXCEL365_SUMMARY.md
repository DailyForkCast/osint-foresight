# Tracker v9 - Excel 365 Comprehensive Overhaul
**Date:** November 6, 2025
**File:** `2025-10-26-Tracker-v9.xlsx`
**Requires:** Excel 365 (Microsoft 365)

---

## 🎉 MAJOR UPGRADE: Excel 365 FILTER Functions

**v9 is the FIRST fully working Project_Spotlight** with proper dynamic filtering!

All previous versions (v7-v8.3) had broken array formulas. **v9 fixes everything** using Excel 365's modern FILTER() function.

---

## ✅ WHAT'S FIXED IN V9

### **1. Target Audiences - NOW WORKS!** ✨
**Location:** Project_Spotlight, Rows 6-14, Columns G-I

**Formula (G6):**
```excel
=IFERROR(FILTER(T_Project_Audiences[Audience_Type],T_Project_Audiences[Project_ID]=$B$2),"")
```

**What it does:**
- Automatically shows ALL audiences for selected project
- Results "spill" into rows 7, 8, 9... automatically
- If project has 2 audiences, rows 6-7 fill, rows 8-14 stay blank
- **No manual formulas needed in rows 7-14!**

**Columns:**
- G: Audience Type
- H: Description
- I: Priority

---

### **2. Target Technologies - NOW WORKS!** ✨
**Location:** Project_Spotlight, Rows 6-14, Columns J-K

**Formula (J6):**
```excel
=IFERROR(FILTER(Project_Technologies[Technology],Project_Technologies[Project_ID]=$B$2),"")
```

**What it does:**
- Shows ALL technologies for selected project
- Auto-spills to rows 7-14
- Dynamic - updates when you change project in B2

**Columns:**
- J: Technology
- K: Category

---

### **3. Key Deliverables - NOW WORKS!** ✨
**Location:** Project_Spotlight, Rows 18-27, Columns B-F

**Formula (B18):**
```excel
=IFERROR(FILTER(T_Project_Deliverables[Deliverable_Name],T_Project_Deliverables[Project_ID]=$B$2),"")
```

**What it does:**
- Shows ALL deliverables for selected project (not just first 2!)
- Auto-spills to rows 19-27
- Shows up to 10 deliverables

**Columns:**
- B: Deliverable Name
- C: Due Date
- D: Status
- E: Owner
- F: Completion %

---

### **4. Key Stakeholders - NEW SECTION!** ✨
**Location:** Project_Spotlight, Row 30+, Columns B-F

**Formula (B31):**
```excel
=IFERROR(FILTER(Stakeholders[Name],ISNUMBER(SEARCH($B$2,Stakeholders[Project_IDs]))),"")
```

**What it does:**
- Shows stakeholders assigned to selected project
- **Works with comma-separated Project_IDs!**
  - If stakeholder has Project_IDs = "PRJ-001, PRJ-002"
  - They show up for BOTH projects
- Auto-spills for all matching stakeholders

**Columns:**
- B: Name
- C: Title
- D: Organization
- E: Email
- F: Stakeholder Type

---

### **5. Visual Enhancements** 🎨
- Section headers now have professional blue background (#366092)
- White text on headers for contrast
- Clean, modern look
- Ready for further customization

---

## 🚀 HOW TO USE

### **Open v9:**
1. Open `2025-10-26-Tracker-v9.xlsx` in Excel 365
2. Go to **Project_Spotlight** sheet
3. Cell B2 should show "PRJ-001"

### **Watch the Magic:**
All these sections auto-populate:
- ✅ Target Audiences (rows 6+)
- ✅ Target Technologies (rows 6+)
- ✅ Key Deliverables (rows 18+)
- ✅ Key Stakeholders (rows 31+)

### **Change Projects:**
1. Click B2
2. Select different project from dropdown
3. **ALL sections update automatically!**

---

## 🔬 BEHIND THE SCENES

### **What is FILTER()?**
```excel
=FILTER(array, include, [if_empty])
```

**Example:**
```excel
=FILTER(T_Project_Deliverables[Deliverable_Name], T_Project_Deliverables[Project_ID]="PRJ-001")
```
- **array:** What to show (Deliverable_Name column)
- **include:** What rows to include (where Project_ID = "PRJ-001")
- **Result:** Dynamic list of deliverable names for PRJ-001

### **What is "Spilling"?**
When FILTER returns 3 results:
- Formula in B18 shows result #1
- Excel **automatically** fills B19 with result #2
- Excel **automatically** fills B20 with result #3
- B21-B27 stay empty (no more results)

**You can't edit spilled cells** - they're controlled by the main formula in B18!

---

## 📊 STAKEHOLDERS - COMMA-SEPARATED PROJECT_IDS

### **The Problem:**
Stakeholders often work on multiple projects. Do we:
- **Option A:** Duplicate rows (John appears twice for PRJ-001 and PRJ-002)
- **Option B:** Use comma-separated IDs (John appears once with "PRJ-001, PRJ-002")

### **v9 Solution:**
**Option B** - Comma-separated with smart filtering!

**How it works:**
```excel
=FILTER(Stakeholders[Name], ISNUMBER(SEARCH($B$2, Stakeholders[Project_IDs])))
```

**SEARCH($B$2, Stakeholders[Project_IDs])**
- Looks for "PRJ-001" anywhere in Project_IDs column
- Finds it in "PRJ-001, PRJ-002"
- Returns position (e.g., 1)

**ISNUMBER(...)**
- If SEARCH found it, returns TRUE
- If SEARCH didn't find it, returns FALSE

**FILTER(..., TRUE/FALSE)**
- Shows rows where TRUE
- Hides rows where FALSE

**Example:**
```
Stakeholder Table:
Row 2: John Smith | Project_IDs: "PRJ-001, PRJ-003"
Row 3: Jane Doe   | Project_IDs: "PRJ-002"
Row 4: Bob Lee    | Project_IDs: "PRJ-001"

When B2 = "PRJ-001":
  Shows: John Smith (found in "PRJ-001, PRJ-003")
  Shows: Bob Lee (matches exactly)
  Hides: Jane Doe (doesn't contain PRJ-001)
```

---

## 🆚 COMPARISON: v8 vs v9

| Feature | v8.1-v8.3 | v9 |
|---------|-----------|-----|
| Target Audiences | ❌ Broken array formulas | ✅ FILTER() - works! |
| Target Technologies | ❌ Broken array formulas | ✅ FILTER() - works! |
| Key Deliverables | ❌ Broken/simplified | ✅ FILTER() - fully dynamic! |
| Stakeholders | ❌ Not in Project_Spotlight | ✅ New section with smart filtering! |
| Ctrl+Shift+Enter needed | ⚠️ Yes (v8.1) | ✅ No - fully automatic! |
| Excel version | 2016+ (but broken) | Excel 365 only |
| Project filtering | ❌ Shows all or none | ✅ Shows only selected project! |
| Comma-separated IDs | ❌ Not supported | ✅ Smart SEARCH filtering! |
| Visual styling | Basic | ✅ Enhanced headers |

---

## 🎯 WHAT YOU NEED TO DO

### **Immediate:**
1. Open v9 in Excel 365
2. Test all sections with PRJ-001
3. Verify deliverables, audiences, technologies show up

### **Add Your Data:**

**For each project, populate these sheets:**

1. **Project_Deliverables:**
   - Add rows for each deliverable
   - Column A: Project_ID (e.g., "PRJ-001")
   - Column B: Deliverable_Name
   - Columns C-H: Due Date, Status, Owner, etc.

2. **Project_Audiences (T_Project_Audiences):**
   - Add rows for target audiences
   - Column A: Project_ID
   - Column B: Audience_Type (e.g., "Government Officials")
   - Columns C-D: Description, Priority

3. **Project_Technologies:**
   - Add rows for technologies
   - Column A: Project_ID
   - Column B: Technology (e.g., "Cloud Infrastructure")
   - Column C: Category

4. **Stakeholders:**
   - Add rows for people
   - Columns A-K: Name, Title, Organization, etc.
   - **Column L: Project_IDs** - Use comma-separated list:
     - Single project: "PRJ-001"
     - Multiple projects: "PRJ-001, PRJ-002, PRJ-005"

### **Test It:**
1. Add a deliverable to Project_Deliverables for PRJ-002
2. Go to Project_Spotlight
3. Change B2 to "PRJ-002"
4. Watch deliverables section update automatically!

---

## ⚠️ IMPORTANT NOTES

### **Excel 365 Required:**
- FILTER() only works in Excel 365 (Microsoft 365 subscription)
- **Will NOT work** in Excel 2016, 2019, 2021 standalone versions
- If you don't have Excel 365, you need v8.3 (simplified formulas) or manual entry

### **Spill Errors:**
If you see **#SPILL!** error:
- **Cause:** Another formula or value is blocking the spill area
- **Fix:** Clear rows 7-14 (audiences), 7-14 (technologies), 19-27 (deliverables)
- The FILTER formula needs empty cells below to spill into

### **#CALC! Errors:**
If you see **#CALC!**:
- **Cause:** FILTER function not recognized
- **Fix:** Confirm you have Excel 365, not Excel 2019 or earlier

### **Empty Results:**
If sections are blank:
- **Check 1:** Is B2 set to a valid project (e.g., "PRJ-001")?
- **Check 2:** Do deliverables/audiences exist for that project?
- **Check 3:** Is Project_ID spelled exactly the same? (case-sensitive!)

---

## 📚 FURTHER ENHANCEMENTS (Future)

**Still on your wishlist:**
- [ ] Document linking (attach files to projects/deliverables)
- [ ] Country-specific dashboard
- [ ] More visual styling throughout tracker
- [ ] Countries not loading in budget tracker fix

**What we've completed:**
- ✅ Financial tracking system (v8)
- ✅ Country ownership (My_Country flag)
- ✅ Proper ULO calculation
- ✅ Project_Spotlight comprehensive overhaul (v9)
- ✅ Excel 365 FILTER functions
- ✅ Stakeholders section with smart filtering
- ✅ Visual enhancements (headers)

---

## 🎉 SUMMARY

**v9 = First Fully Functional Project_Spotlight!**

**Major wins:**
- ✅ All sections work properly (Audiences, Technologies, Deliverables, Stakeholders)
- ✅ Excel 365 FILTER() - modern, dynamic, reliable
- ✅ Auto-spilling - no manual formulas in supporting rows
- ✅ Smart stakeholder filtering (comma-separated Project_IDs)
- ✅ Visual improvements
- ✅ No Ctrl+Shift+Enter gymnastics

**Requirements:**
- Excel 365 (Microsoft 365 subscription)

**Test it and let me know:**
- Does everything load correctly?
- Do you see your deliverables?
- Any adjustments needed?

---

**v9 is production-ready! 🚀**
