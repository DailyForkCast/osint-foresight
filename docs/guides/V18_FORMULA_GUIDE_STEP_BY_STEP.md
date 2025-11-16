# V18 FORMULA GUIDE - STEP BY STEP

## Overview
You need to add formulas to 2 sheets:
- **Master_Projects**: 5 formulas (columns N, O, P, Q, R)
- **Country_Budgets**: 2 formulas (columns J, K)

**Time**: ~5 minutes total

---

## PART 1: Master_Projects Formulas

### Step 1: Column N (Total_Proposed)

1. Go to **Master_Projects** sheet
2. Click on cell **N2**
3. Type this formula:
   ```
   =SUMIF(Country_Budgets!$B:$B,A2,Country_Budgets!$F:$F)
   ```
4. Press **Enter**
5. Click on cell **N2** again
6. Hover over the bottom-right corner of the cell until you see a small black **+** (fill handle)
7. Double-click the **+** to auto-fill down to all rows with data
   - OR click and drag down to the last row with project data

---

### Step 2: Column O (Total_Allocation)

1. Click on cell **O2**
2. Type this formula:
   ```
   =SUMIF(Country_Budgets!$B:$B,A2,Country_Budgets!$G:$G)
   ```
3. Press **Enter**
4. Click on **O2** again and double-click the fill handle to copy down

---

### Step 3: Column P (Total_Obligated)

1. Click on cell **P2**
2. Type this formula:
   ```
   =SUMIF(Country_Budgets!$B:$B,A2,Country_Budgets!$H:$H)
   ```
3. Press **Enter**
4. Click on **P2** again and double-click the fill handle to copy down

---

### Step 4: Column Q (Total_ULO)

1. Click on cell **Q2**
2. Type this formula:
   ```
   =SUMIF(Country_Budgets!$B:$B,A2,Country_Budgets!$J:$J)
   ```
3. Press **Enter**
4. Click on **Q2** again and double-click the fill handle to copy down

---

### Step 5: Column R (ULO_Percent) + Format as Percentage

1. Click on cell **R2**
2. Type this formula:
   ```
   =IF(P2>0,Q2/P2,0)
   ```
3. Press **Enter**
4. Click on **R2** again and double-click the fill handle to copy down
5. **Format as percentage**:
   - Select the entire column R (click on the column header "R")
   - Right-click → **Format Cells**
   - Select **Percentage** → **OK**
   - OR use the keyboard shortcut: **Ctrl+Shift+%**

---

## PART 2: Country_Budgets Formulas

### Step 6: Column J (ULO)

1. Go to **Country_Budgets** sheet
2. Click on cell **J2**
3. Type this formula:
   ```
   =H2-I2
   ```
4. Press **Enter**
5. Click on **J2** again and double-click the fill handle to copy down to all rows with data

---

### Step 7: Column K (ULO_Percent) + Format as Percentage

1. Click on cell **K2**
2. Type this formula:
   ```
   =IF(H2>0,J2/H2,0)
   ```
3. Press **Enter**
4. Click on **K2** again and double-click the fill handle to copy down
5. **Format as percentage**:
   - Select the entire column K (click on the column header "K")
   - Right-click → **Format Cells**
   - Select **Percentage** → **OK**
   - OR use the keyboard shortcut: **Ctrl+Shift+%**

---

## ✅ DONE!

You should now have:
- ✅ Budget rollups in Master_Projects (columns N-R)
- ✅ ULO calculations in Country_Budgets (columns J-K)
- ✅ Percentages formatted correctly

---

## Quick Verification

### Check Master_Projects:
- Column N-R should show numbers (not errors)
- Column R should show percentages (like "75%" not "0.75")

### Check Country_Budgets:
- Column J should show the difference between Obligated (H) and Spent (I)
- Column K should show percentages

---

## Tips

**Fill Handle Not Working?**
- If double-click doesn't auto-fill, manually drag down to the last row with data
- You can also: Select the cell with formula → Copy (Ctrl+C) → Select range → Paste (Ctrl+V)

**See #REF! or #VALUE! errors?**
- Double-check you typed the formula exactly as shown
- Make sure you're in the correct cell (N2, O2, P2, etc.)

**Formula shows as text (you see the formula, not the result)?**
- The cell might be formatted as Text
- Re-type the formula and press Enter
- Or: Select cell → Home tab → Number format → General

---

## What These Formulas Do

**Master_Projects Formulas (N-R):**
- Sum up all budget amounts from Country_Budgets that match this project's ID
- Calculate the ULO percentage

**Country_Budgets Formulas (J-K):**
- **J (ULO)**: Unliquidated Obligations = Obligated - Spent
- **K (ULO_Percent)**: What percentage of obligated funds are still unspent

**Note**: Once you add formulas to column J in Country_Budgets, the Master_Projects column Q (Total_ULO) will automatically calculate correctly!
