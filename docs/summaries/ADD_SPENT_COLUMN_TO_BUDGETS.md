# Add Spent_Amount Column to Country_Budgets
**Complete the Budget Flow: Allocated → Obligated → Spent**

---

## CURRENT STATE

Country_Budgets has:
- ✓ Column E: Allocated_Amount (total budget authorized)
- ✓ Column F: Obligated_Amount (committed/contracted)
- ✓ Column G: ULO (Unobligated = Allocated - Obligated)
- ✓ Column H: ULO_Percent
- ✓ Column I: Spend_Health

**Missing:** Spent_Amount (actual money paid out)

---

## BUDGET FLOW EXPLAINED

```
Allocated_Amount (E)
    ↓
Obligated_Amount (F) ← committed but not yet paid
    ↓
Spent_Amount (NEW) ← actual money disbursed
```

**Key Metrics:**
- **ULO** = Allocated - Obligated (money not yet committed)
- **Unliquidated** = Obligated - Spent (money committed but not yet paid)
- **Spend Rate** = Spent / Allocated (% of total budget actually spent)

---

## SOLUTION: Add 3 New Columns

### Column J: Spent_Amount (NEW)

**Header (J1):** `Spent_Amount`

**J2 (enter actual data):** (Leave blank for now, or enter actual spent amounts)

**Purpose:** Track actual money disbursed

**Data Entry:** Manual entry or import from financial system

---

### Column K: Unliquidated (NEW)

**Header (K1):** `Unliquidated`

**Formula (K2):**
```
=F2-J2
```

**What it calculates:** Money that's been obligated but not yet spent

**Copy down to:** K2:K5000

---

### Column L: Spend_Rate (NEW)

**Header (L1):** `Spend_Rate`

**Formula (L2):**
```
=IF(E2=0,0,J2/E2)
```

**Format:** Percentage (0%)

**What it calculates:** Percentage of allocated budget that's been spent

**Copy down to:** L2:L5000

---

## UPDATED COLUMN STRUCTURE

After adding these columns, Country_Budgets will have:

| Col | Header | Type | Formula/Value |
|-----|--------|------|---------------|
| A | Budget_ID | Formula | =IF(AND(B2<>"",C2<>""),B2&"-"&C2,"") |
| B | Unique_ID | Data | PRJ-001 |
| C | Country_Code | Data | DE |
| D | Country_Name | Formula | Lookup from Country_Regions |
| E | Allocated_Amount | Data | 500000 |
| F | Obligated_Amount | Data | 350000 |
| G | ULO | Formula | =E2-F2 |
| H | ULO_Percent | Formula | =IF(E2=0,0,G2/E2) |
| I | Spend_Health | Formula | =H2 |
| **J** | **Spent_Amount** | **Data** | **250000** |
| **K** | **Unliquidated** | **Formula** | **=F2-J2** |
| **L** | **Spend_Rate** | **Formula** | **=IF(E2=0,0,J2/E2)** |

---

## STEP-BY-STEP IMPLEMENTATION

### Step 1: Add Column Headers (1 minute)

1. Open v6 in Excel
2. Go to **Country_Budgets** sheet
3. Click cell **J1**
4. Type: `Spent_Amount`
5. Click cell **K1**
6. Type: `Unliquidated`
7. Click cell **L1**
8. Type: `Spend_Rate`

---

### Step 2: Add Formulas (2 minutes)

**K2 (Unliquidated):**
```
=F2-J2
```

**L2 (Spend_Rate):**
```
=IF(E2=0,0,J2/E2)
```

**Copy both formulas down:**
1. Select K2:L2
2. Copy (Ctrl+C)
3. Select K2:L5000 (or however many rows you have)
4. Paste (Ctrl+V)

---

### Step 3: Format Columns (1 minute)

**Column J (Spent_Amount):**
- Format as Currency: `$#,##0`

**Column K (Unliquidated):**
- Format as Currency: `$#,##0`

**Column L (Spend_Rate):**
- Format as Percentage: `0.0%`

---

### Step 4: Enter Spent Data (varies)

**Column J needs actual data:**

**Option A:** Enter manually
- Click J2, J3, etc.
- Type actual spent amounts

**Option B:** Enter formula for estimation
If you don't have actual spent data, estimate based on time elapsed:
```
=F2*0.7
```
(Assumes 70% of obligated amount has been spent)

**Option C:** Import from financial system
- Export spent data from your finance system
- Copy/paste into column J

---

## UPDATE MASTER_PROJECTS TOTALS

After adding spent to Country_Budgets, update Master_Projects to aggregate it:

### Add Column after P (Total_ULO)

**New Column Q: Total_Spent**

**Q1 Header:** `Total_Spent`

**Q2 Formula:**
```
=SUMIF(Country_Budgets[Unique_ID],B2,Country_Budgets[Spent_Amount])
```

**Copy down to:** Q2:Q1000

**Format as:** Currency

---

### Shift existing columns

This will shift your existing columns:
- Current Q (ULO_Percent) becomes R
- Current R (Countries) becomes S
- etc.

You'll need to update references in other sheets that point to these columns.

---

## UPDATE CONTROL SHEET

Add spent totals to Control sheet for dashboard use:

Find empty cells (suggest after B18) and add:

**B20:** Total Spent Across Portfolio
```
=SUM(Country_Budgets[Spent_Amount])
```

**B21:** Portfolio Spend Rate
```
=IF(B15=0,0,B20/B15)
```
(Where B15 is your Total_Allocation cell)

**Format B21 as percentage**

---

## UPDATE REGIONAL_SUMMARY

Add spent metrics to Regional_Summary sheet:

### Add new columns after current ones

**Column M: Total_Spent**

**M2 Formula:**
```
=SUMPRODUCT((Country_Regions[Region]=A2)*(ISNUMBER(MATCH(Country_Regions[Country_Code],Country_Budgets[Country_Code],0)))*Country_Budgets[Spent_Amount])
```

**Column N: Spend_Rate**

**N2 Formula:**
```
=IF(F2=0,0,M2/F2)
```

Format as percentage.

---

## EXAMPLE WITH REAL DATA

Before adding Spent:
```
Unique_ID  Country  Allocated  Obligated  ULO
PRJ-001    DE       500,000    350,000    150,000
```

After adding Spent:
```
Unique_ID  Country  Allocated  Obligated  ULO      Spent     Unliquidated  Spend_Rate
PRJ-001    DE       500,000    350,000    150,000  250,000   100,000       50.0%
```

**Interpretation:**
- $500K allocated
- $350K obligated (committed)
- $150K unobligated (not yet committed)
- $250K spent (actual cash out)
- $100K unliquidated (committed but not yet paid)
- 50% spend rate

---

## BENEFITS

After adding these columns:

1. **Track actual spending** - not just commitments
2. **Monitor cash flow** - see unliquidated obligations
3. **Calculate burn rate** - spending velocity
4. **Identify bottlenecks** - high unliquidated = payment delays
5. **Better forecasting** - based on actual spend patterns

---

## PRIORITY IMPLEMENTATION

### Must Do (5 minutes):
1. Add J1, K1, L1 headers
2. Add K2 and L2 formulas, copy down
3. Enter spent data in column J (even if estimates)

### Should Do (10 minutes):
4. Add Total_Spent to Master_Projects
5. Update Control sheet with portfolio spent totals

### Nice to Have (5 minutes):
6. Add spent columns to Regional_Summary

---

## QUICK REFERENCE

| What | Where | Formula |
|------|-------|---------|
| Spent Amount | Country_Budgets J2 | [Manual entry or import] |
| Unliquidated | Country_Budgets K2 | =F2-J2 |
| Spend Rate | Country_Budgets L2 | =IF(E2=0,0,J2/E2) |
| Total Spent | Master_Projects Q2 | =SUMIF(Country_Budgets[Unique_ID],B2,Country_Budgets[Spent_Amount]) |
| Portfolio Spent | Control B20 | =SUM(Country_Budgets[Spent_Amount]) |

---

## NOTES

- Spent_Amount requires actual data from your financial system
- If you don't have spent data yet, you can:
  - Leave column J blank and formulas will show $0
  - Enter estimated percentages (e.g., 70% of obligated)
  - Import later when data is available
- Unliquidated and Spend_Rate will auto-calculate once spent data is entered

---

**Is "Spent_Amount" what you meant by the missing allocated column?** Or did you mean something else?
