# Config_Lists - Create Two Tables Guide

**Your Structure:**
- Columns A-C: Status, Priority, Stage
- Columns F-H: Country_Code, Country, Region

---

## 📋 **Table 1: T_Config_Lists (Columns A-C)**

### **What It Contains:**
- Status (Active, CN Stage, Proposed, etc.)
- Priority (Critical, High, Medium, Low)
- Stage (Planning, Implementation, Monitoring, Closing)

### **How to Create:**

**Step 1:** Click on cell **A1**

**Step 2:** Select the range **A1:C10** (or wherever your data ends)
- Click A1
- Hold Shift
- Click the last cell with data in column C

**Step 3:** Press **Ctrl+T** (or Insert → Table)

**Step 4:** Check ✓ **My table has headers**

**Step 5:** Click **OK**

**Step 6:** Name the table:
- Click anywhere in the table
- **Table Design** tab → **Table Name** field
- Type: `T_Config_Lists`
- Press Enter

**✅ DONE!** Table 1 created.

---

## 🌍 **Table 2: T_Config_Countries (Columns F-H)**

### **What It Contains:**
- Country_Code (ET, KE, MU, etc.)
- Country (Ethiopia, Kenya, Mauritius, etc.)
- Region (AF, EAP, EUR, NEA, SCA, WHA)

### **How to Create:**

**Step 1:** Click on cell **F1**

**Step 2:** Select the range **F1:H79** (or wherever your data ends)
- Click F1
- Hold Shift
- Click the last cell with data in column H

**Step 3:** Press **Ctrl+T** (or Insert → Table)

**Step 4:** Check ✓ **My table has headers**

**Step 5:** Click **OK**

**Step 6:** Name the table:
- Click anywhere in the table
- **Table Design** tab → **Table Name** field
- Type: `T_Config_Countries`
- Press Enter

**✅ DONE!** Table 2 created.

---

## 🎯 **Table Names Summary**

| Columns | Table Name | Contains |
|---------|------------|----------|
| A-C | `T_Config_Lists` | Status, Priority, Stage |
| F-H | `T_Config_Countries` | Country_Code, Country, Region |

---

## 📊 **Updated Validation Formulas**

Once you've created both tables, use these validation formulas:

### **For Status Dropdowns:**
**OLD:**
```
=Config_Lists!$A$2:$A$20
```

**NEW (Auto-Expand):**
```
=T_Config_Lists[Status]
```

---

### **For Priority Dropdowns:**
**OLD:**
```
=Config_Lists!$B$2:$B$20
```

**NEW (Auto-Expand):**
```
=T_Config_Lists[Priority]
```

---

### **For Stage Dropdowns:**
**NEW (if needed):**
```
=T_Config_Lists[Stage]
```

---

### **For Country Code Dropdowns:**
**OLD:**
```
=Country_Regions!$A$2:$A$79
```

**NEW (Auto-Expand):**
```
=T_Config_Countries[Country_Code]
```

**OR (if you prefer to keep using Country_Regions table):**
```
=T_Country_Regions[Country_Code]
```

---

### **For Country Name Dropdowns:**
**OLD:**
```
=Country_Regions!$B$2:$B$79
```

**NEW (Auto-Expand):**
```
=T_Config_Countries[Country]
```

**OR (if you prefer to keep using Country_Regions table):**
```
=T_Country_Regions[Country_Name]
```

---

## 🤔 **Important Note: Country Data Duplication**

You now have country data in TWO places:
1. **Country_Regions** sheet → `T_Country_Regions` table
2. **Config_Lists** sheet → `T_Config_Countries` table (what you just created)

### **Which One to Use for Validation?**

**Option 1: Use T_Country_Regions (Recommended)**
- ✅ Already exists and works
- ✅ Single source of truth
- ✅ Use: `=T_Country_Regions[Country_Name]`

**Option 2: Use T_Config_Countries**
- ⚠️ Need to keep both in sync
- ⚠️ Duplicate data maintenance
- Use: `=T_Config_Countries[Country]`

**My Recommendation:**
- Keep **T_Config_Countries** for quick reference in Config_Lists
- But use **T_Country_Regions** for actual validation dropdowns
- This way you have ONE source of truth (Country_Regions)

---

## ✅ **Where to Use Each Table**

### **T_Config_Lists[Status]:**
Use in:
- Master_Projects column E (Project_Status)
- Any other Status dropdowns

### **T_Config_Lists[Priority]:**
Use in:
- Master_Projects column F (Project_Priority)
- Calendar_Todo column G (Priority)
- Any other Priority dropdowns

### **T_Country_Regions[Country_Name]:**
Use in:
- Country_Dashboard B2 (Country selector)
- Stakeholders column E (Location_Country)
- Any other Country dropdowns

### **T_Country_Regions[Country_Code]:**
Use in:
- Country_Budgets column D (Country_Code)
- Any other Country Code dropdowns

---

## 🚀 **Quick Start Checklist**

**Create Tables:**
- [ ] Select A1:C10 → Ctrl+T → Name: `T_Config_Lists`
- [ ] Select F1:H79 → Ctrl+T → Name: `T_Config_Countries`

**Update Validation (Optional):**
- [ ] Master_Projects Status: Change to `=T_Config_Lists[Status]`
- [ ] Master_Projects Priority: Change to `=T_Config_Lists[Priority]`
- [ ] Keep Country validations using `=T_Country_Regions[...]`

**Decide:**
- [ ] Keep T_Config_Countries as reference only
- [ ] Use T_Country_Regions for actual validation dropdowns

---

## 💡 **Why Two Tables is Smart**

**Benefits:**
1. ✅ Status/Priority auto-expand independently of Countries
2. ✅ Different row counts (10 vs 70) handled cleanly
3. ✅ Easier to maintain and understand
4. ✅ Can reference specific columns easily

**Perfect setup!** This is exactly how Config_Lists should be organized. 🎯

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Tracker Version:** v51
