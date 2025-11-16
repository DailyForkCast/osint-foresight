# Tracker v8 - Quick Start Guide

## 🚀 Open the Tracker

**File:** `2025-10-26-Tracker-v8.xlsx`

---

## ✅ 5-Minute Setup Checklist

### **Step 1: Mark Your Countries** (2 minutes)
1. Open **Country_Budgets** sheet
2. For each row, check column C "My_Country"
3. Set to **TRUE** for countries you manage
4. Set to **FALSE** for countries managed by others

### **Step 2: Enter Spent Amounts** (2 minutes)
1. Still in **Country_Budgets** sheet
2. Column H "Spent_Amount" - enter how much has been spent
3. If unknown, leave at $0 for now
4. Watch column I "ULO" update automatically!

### **Step 3: Verify Calculations** (1 minute)
1. Go to **Master_Projects** sheet
2. Look at column AD "My_Countries_Count"
3. Should show how many countries you marked as TRUE
4. Look at column P "Total_ULO"
5. Should only include YOUR countries

---

## 📊 What the Columns Mean

### **Master_Projects - Key Columns:**
- **AA (Proposed_Amount):** For proposed projects only - how much you're asking for
- **AB (Total_Spent):** How much YOU'VE spent (from YOUR countries only)
- **P (Total_ULO):** Obligated - Spent = Money committed but not yet spent
- **Q (ULO%):** What % of obligated funds are still available
- **Z (Project_Manager):** Who's responsible (you can add multiple: "Smith, Jones")
- **AD (My_Countries_Count):** How many of the project's countries are yours

### **Country_Budgets - Key Columns:**
- **C (My_Country):** TRUE = yours, FALSE = someone else's
- **G (Obligated_Amount):** Money formally committed for this country
- **H (Spent_Amount):** Money actually spent (YOU ENTER THIS)
- **I (ULO):** Auto-calculates: Obligated - Spent
- **J (ULO%):** Auto-calculates: ULO / Obligated

---

## 🎯 Common Tasks

### **Add a New Project:**
1. Go to **Master_Projects**
2. Add new row
3. Enter: Unique_ID, Project_Name, Status, Priority, etc.
4. If Status = "Proposed": Fill column AA (Proposed_Amount)
5. If Status = "Active": Fill columns N-O (Allocation, Obligated)
6. Enter Project_Manager in column Z

### **Add Countries to a Project:**
1. Go to **Country_Budgets**
2. Add new row
3. Select Project_ID (column B) from dropdown
4. Select Country_Code (column D) from dropdown
5. **My_Country (column C) defaults to TRUE** - change if needed
6. Enter amounts in columns F-H (Allocated, Obligated, Spent)

### **Mark a Project as Proposed:**
1. Set Status = "Proposed"
2. Text becomes _italic_ automatically
3. Enter Proposed_Amount (column AA)
4. Leave Allocated/Obligated/Spent blank
5. Project excluded from calculations

### **Archive a Project:**
1. Set Status = "Archived"
2. Text becomes gray automatically
3. Project excluded from calculations
4. Data stays visible for reference

---

## 🔍 Quick Tests

### **Test 1: Country Ownership Works**
1. Find a country with My_Country = FALSE
2. Note the Total_ULO in Master_Projects
3. Change My_Country to TRUE
4. Watch Total_ULO increase!

### **Test 2: ULO Calculation Works**
1. Pick any country budget
2. Note current ULO value
3. Increase Spent_Amount by $10,000
4. Watch ULO decrease by $10,000!

### **Test 3: Proposed Project Excluded**
1. Create new project with Status = "Proposed"
2. Check Portfolio_Dashboard
3. Should NOT appear in calculations
4. Text should be _italic_

---

## ❓ Quick Answers

**Q: What's ULO?**
A: Unliquidated Obligations = Money you've committed but haven't spent yet

**Q: What's the difference between Allocated and Obligated?**
A: Allocated = approved but can't touch yet | Obligated = formally committed, can spend

**Q: Why don't my totals match what I see in Country_Budgets?**
A: Master_Projects totals ONLY include countries where My_Country = TRUE

**Q: What if a project has multiple Project Managers?**
A: Enter comma-separated: "Smith, Jones, Lee"

**Q: Can I change My_Country later?**
A: Yes! Change it anytime. Master_Projects will recalculate automatically.

---

## 🎨 Visual Guide

**Proposed Projects:** _Look like this (italic)_

**Archived Projects:** Look like this (gray)

**Spend Health:**
- 🟢 = Good (80%+ funds remaining)
- 🟡 = Caution (50-80% funds remaining)
- 🔴 = Alert (<50% funds remaining)

---

## 📞 Issues?

**Project Spotlight not loading?**
- Make sure cell B2 contains a valid Project ID (e.g., "PRJ-001")
- Open file and let Excel recalculate

**Countries not showing in dropdown?**
- Check **Country_Regions** sheet - should have 78 countries
- Check **Config_Lists** sheet - column D should have country codes

**Formulas showing #REF! or #VALUE!?**
- Close and reopen Excel
- Let it recalculate
- If persists, let me know which cell

---

## 📋 Status Categories

Use these in the Status dropdown:
- **Active** - Currently working on it
- **CN Stage** - Contract negotiation
- **Proposed** - Not yet approved (italic, excluded from calcs)
- **Archived** - Done and archived (gray, excluded from calcs)
- **Not Started** - Approved but not yet begun
- **In Progress** - Underway
- **On Hold** - Temporarily suspended
- **Completed** - Successfully finished
- **Cancelled** - Project cancelled

---

## 🎉 You're Ready!

**Quick wins completed:**
- ✅ Project Spotlight fixed
- ✅ Status categories expanded
- ✅ Country list cleaned (78 relevant countries)
- ✅ Financial tracking system implemented
- ✅ Country ownership tracking
- ✅ Proper ULO calculations

**Start using it and let me know what you think!**

---

**Need help?** Just ask!

**Want to enhance it?** We can add:
- Document linking
- Country-specific dashboard
- Visual overhaul
- More features from your notes
