# Manual Data Validation Guide
## Step-by-Step Instructions for Excel

**Version:** v51
**Date:** 2025-11-14

This guide shows you exactly how to add data validation to your tracker manually in Excel.

---

## 📌 **What is Data Validation?**

Data validation adds **dropdown arrows** to cells so you can select from a list instead of typing. This:
- ✅ Prevents typos
- ✅ Ensures consistency
- ✅ Makes data entry faster
- ✅ Links data across sheets correctly

---

## 🎯 **Priority Guide**

### **🔴 CRITICAL (Do First)**
1. Master_Projects - Status, Priority, Fiscal Year
2. Country_Dashboard - Country dropdown
3. Spotlight_PMWorkspace - Project ID dropdown

### **🟡 HIGH PRIORITY (Do Next)**
4. Country_Budgets - Project ID and Country Code
5. Milestones - Project ID and Status
6. Events - Project ID and Event Type

### **🟢 MEDIUM PRIORITY (Do When Ready)**
7. Project_Deliverables - Project ID, Type, Status
8. Calendar_Todo - Project ID, Status, Priority
9. Stakeholders - Country

---

## 📖 **How to Add Data Validation in Excel**

### **Basic Steps (Same for All)**
1. Select the cell or range
2. Click **Data** tab → **Data Validation**
3. In "Allow" dropdown, select **List**
4. In "Source" field, enter the formula (see below)
5. Check ✓ **In-cell dropdown**
6. Click **OK**

---

# 🔴 **CRITICAL VALIDATIONS**

## **1. MASTER_PROJECTS**

### **Status Dropdown (Column E: Project_Status)**

**Step 1:** Select cells **E2:E201**
- Click on E2, then Shift+Click on E201

**Step 2:** Data → Data Validation → Settings tab

**Step 3:** Configure:
- Allow: **List**
- Source: `=Config_Lists!$A$2:$A$10`
- ✓ In-cell dropdown
- ✓ Ignore blank

**Step 4:** Click OK

**Optional - Error Alert:**
- Error Alert tab
- Title: `Invalid Status`
- Error message: `Please select a valid status from the list`

---

### **Priority Dropdown (Column F: Project_Priority)**

**Step 1:** Select cells **F2:F201**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Config_Lists!$B$2:$B$5`
- ✓ In-cell dropdown
- ✓ Ignore blank

**Optional - Input Message:**
- Input Message tab
- ✓ Show input message when cell is selected
- Title: `Project Priority`
- Input message: `Select: Critical, High, Medium, or Low`

---

### **Fiscal Year Dropdown (Column A: Fiscal_Year)**

**Step 1:** Select cells **A2:A201**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `FY2024,FY2025,FY2026,FY2027,FY2028`
  - Type this exactly, with commas, no spaces
- ✓ In-cell dropdown

---

## **2. COUNTRY_DASHBOARD**

### **Country Dropdown (Cell B2)**

**Step 1:** Click on cell **B2** (just B2, not a range)

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Country_Regions!$B$2:$B$79`
  - This gives you full country NAMES (Germany, France, etc.)
- ✓ In-cell dropdown

**Note:** This allows you to type "Germany" and see all German projects!

**Alternative (if you prefer codes):**
- Source: `=Country_Regions!$A$2:$A$79`
  - This gives you country CODES (DE, FR, etc.)

---

## **3. SPOTLIGHT_PMWORKSPACE**

### **Project ID Dropdown (Cell B2)**

**Step 1:** Click on cell **B2**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Master_Projects!$B$2:$B$201`
- ✓ In-cell dropdown

**Input Message:**
- Title: `Select Project`
- Message: `Choose a project to view its details`

---

# 🟡 **HIGH PRIORITY VALIDATIONS**

## **4. COUNTRY_BUDGETS**

### **Project ID Dropdown (Column B: Unique_ID)**

**Step 1:** Select cells **B2:B1001**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Master_Projects!$B$2:$B$201`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

### **Country Code Dropdown (Column D: Country_Code)**

**NOTE:** This column has a formula that auto-fills. Validation is optional here.

If you want to add it anyway:

**Step 1:** Select cells **D2:D1001**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Country_Regions!$A$2:$A$79`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

## **5. MILESTONES**

### **Project ID Dropdown (Column C: Unique_ID)**

**Step 1:** Select cells **C2:C100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Master_Projects!$B$2:$B$201`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

### **Status Dropdown (Column E: Status)**

**Step 1:** Select cells **E2:E100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `Not Started,In Progress,Complete,On Hold,Cancelled`
  - Type exactly as shown, with commas
- ✓ In-cell dropdown
- ✓ Ignore blank

---

## **6. EVENTS**

### **Project ID Dropdown (Column B: Unique_ID)**

**Step 1:** Select cells **B2:B100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Master_Projects!$B$2:$B$201`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

### **Event Type Dropdown (Column C: Event_Type)**

**Step 1:** Select cells **C2:C100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `Meeting,Review,Presentation,Training,Workshop,Conference,Other`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

# 🟢 **MEDIUM PRIORITY VALIDATIONS**

## **7. PROJECT_DELIVERABLES**

### **Project ID Dropdown (Column A: Project_ID)**

**Step 1:** Select cells **A2:A100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Master_Projects!$B$2:$B$201`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

### **Deliverable Type Dropdown (Column C: Deliverable_Type)**

**Step 1:** Select cells **C2:C100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `Document,Software Release,Report,Presentation,Training,Hardware,Other`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

### **Status Dropdown (Column E: Status)**

**Step 1:** Select cells **E2:E100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `Not Started,In Progress,Completed,On Hold,Cancelled`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

## **8. CALENDAR_TODO**

### **Project ID Dropdown (Column C: Unique_ID)**

**Step 1:** Select cells **C2:C100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Master_Projects!$B$2:$B$201`
- ✓ In-cell dropdown
- ✓ Ignore blank

**Note:** This is optional - tasks don't have to be linked to projects

---

### **Status Dropdown (Column F: Status)**

**Step 1:** Select cells **F2:F100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `Not Started,In Progress,Completed,On Hold,Cancelled`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

### **Priority Dropdown (Column G: Priority)**

**Step 1:** Select cells **G2:G100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Config_Lists!$B$2:$B$5`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

## **9. STAKEHOLDERS**

### **Country Dropdown (Column E: Location_Country)**

**Step 1:** Select cells **E2:E100**

**Step 2:** Data → Data Validation

**Step 3:** Configure:
- Allow: **List**
- Source: `=Country_Regions!$B$2:$B$79`
- ✓ In-cell dropdown
- ✓ Ignore blank

---

# 📋 **QUICK REFERENCE SHEET**

## **Common Validation Sources**

Copy these exactly when setting up validation:

### **Project IDs**
```
=Master_Projects!$B$2:$B$201
```

### **Country Codes**
```
=Country_Regions!$A$2:$A$79
```

### **Country Names**
```
=Country_Regions!$B$2:$B$79
```

### **Status (from Config_Lists)**
```
=Config_Lists!$A$2:$A$10
```

### **Priority (from Config_Lists)**
```
=Config_Lists!$B$2:$B$5
```

### **Fiscal Years (manual list)**
```
FY2024,FY2025,FY2026,FY2027,FY2028
```

### **Milestone/Task Status (manual list)**
```
Not Started,In Progress,Complete,On Hold,Cancelled
```

### **Deliverable Status (manual list)**
```
Not Started,In Progress,Completed,On Hold,Cancelled
```

### **Event Types (manual list)**
```
Meeting,Review,Presentation,Training,Workshop,Conference,Other
```

### **Deliverable Types (manual list)**
```
Document,Software Release,Report,Presentation,Training,Hardware,Other
```

---

# 💡 **PRO TIPS**

## **1. Copy Validation Across Cells**
After adding validation to one cell:
1. Copy the cell (Ctrl+C)
2. Select destination range
3. Paste Special (Ctrl+Alt+V)
4. Select "Validation" only
5. Click OK

## **2. Edit Existing Validation**
1. Select cell with validation
2. Data → Data Validation
3. Modify settings
4. Click OK

## **3. Remove Validation**
1. Select range
2. Data → Data Validation
3. Click "Clear All"
4. Click OK

## **4. See All Validation in a Sheet**
1. Home tab → Find & Select → Data Validation
2. Excel highlights all cells with validation

## **5. Create Named Ranges (Advanced)**
Instead of `=Master_Projects!$B$2:$B$201`, create a named range:
1. Select Master_Projects!B2:B201
2. In Name Box (top left), type: `ProjectIDs`
3. Press Enter
4. Use `=ProjectIDs` in validation source

---

# ⏱️ **TIME ESTIMATES**

| Priority | Sheets | Estimated Time |
|----------|--------|----------------|
| 🔴 Critical | 3 sheets | 10-15 minutes |
| 🟡 High | 3 sheets | 15-20 minutes |
| 🟢 Medium | 3 sheets | 15-20 minutes |
| **Total** | **9 sheets** | **40-55 minutes** |

---

# ✅ **VALIDATION CHECKLIST**

Print this and check off as you complete:

## Critical
- [ ] Master_Projects - Status (E2:E201)
- [ ] Master_Projects - Priority (F2:F201)
- [ ] Master_Projects - Fiscal Year (A2:A201)
- [ ] Country_Dashboard - Country (B2)
- [ ] Spotlight_PMWorkspace - Project ID (B2)

## High Priority
- [ ] Country_Budgets - Project ID (B2:B1001)
- [ ] Country_Budgets - Country Code (D2:D1001) - Optional
- [ ] Milestones - Project ID (C2:C100)
- [ ] Milestones - Status (E2:E100)
- [ ] Events - Project ID (B2:B100)
- [ ] Events - Event Type (C2:C100)

## Medium Priority
- [ ] Project_Deliverables - Project ID (A2:A100)
- [ ] Project_Deliverables - Type (C2:C100)
- [ ] Project_Deliverables - Status (E2:E100)
- [ ] Calendar_Todo - Project ID (C2:C100)
- [ ] Calendar_Todo - Status (F2:F100)
- [ ] Calendar_Todo - Priority (G2:G100)
- [ ] Stakeholders - Country (E2:E100)

---

# 🚀 **START HERE**

**Recommended workflow:**
1. Do **Critical** validations first (15 minutes)
2. Test by entering some data
3. Add **High Priority** when you're ready to use those sheets
4. Add **Medium Priority** as needed

**You don't have to do all at once!** Add validation as you need it.

---

# 📞 **NEED HELP?**

If validation isn't working:
- Make sure the source sheet exists (e.g., Config_Lists, Country_Regions)
- Check that you used `=` for formulas and NO `=` for manual lists
- Verify cell ranges are correct (use $ for absolute references)
- Test with a single cell first, then copy to range

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Tracker Version:** v51
