# Country_Budgets - Corrected Column Naming
**Clear separation: Unobligated vs ULO (Unliquidated)**

---

## BUDGET FLOW

```
Allocated_Amount (E)
    ↓
    Unobligated (G) ← Money not yet committed
    ↓
Obligated_Amount (F)
    ↓
    ULO (K) ← Money committed but not yet paid (Unliquidated)
    ↓
Spent_Amount (J)
```

---

## COLUMN CHANGES NEEDED

### Step 1: Rename Column G Header

**Current:** G1 = "ULO"

**Change to:** G1 = "Unobligated"

**Formula in G2:** `=E2-F2` (no change needed)

---

### Step 2: Rename Column H Header

**Current:** H1 = "ULO_Percent"

**Change to:** H1 = "Unobligated_%"

**Formula in H2:** `=IF(E2=0,0,G2/E2)` (no change needed)

---

### Step 3: Add New Column J (Spent_Amount)

**J1:** `Spent_Amount`

**J2:** [Manual data entry or import]

**Purpose:** Actual money disbursed/paid out

---

### Step 4: Add New Column K (ULO - Unliquidated)

**K1:** `ULO`

**K2:**
```
=F2-J2
```

**Purpose:** Obligated minus Spent = Money committed but not yet paid

**Copy down to:** K2:K5000

---

### Step 5: Add New Column L (ULO_%)

**L1:** `ULO_%`

**L2:**
```
=IF(F2=0,0,K2/F2)
```

**Format:** Percentage

**Purpose:** What % of obligated funds are unliquidated

**Copy down to:** L2:L5000

---

## FINAL COLUMN STRUCTURE

| Col | Header | Formula | What It Means |
|-----|--------|---------|---------------|
| A | Budget_ID | =IF(AND(B2<>"",C2<>""),B2&"-"&C2,"") | Unique budget ID |
| B | Unique_ID | [Data] | Project ID |
| C | Country_Code | [Data] | Country code |
| D | Country_Name | [Lookup] | Country full name |
| E | Allocated_Amount | [Data] | Total authorized budget |
| F | Obligated_Amount | [Data] | Money committed/contracted |
| G | **Unobligated** | =E2-F2 | **Money not yet committed** |
| H | **Unobligated_%** | =IF(E2=0,0,G2/E2) | % not yet committed |
| I | Spend_Health | =H2 | Health indicator |
| J | Spent_Amount | [Data] | Money actually paid out |
| K | **ULO** | =F2-J2 | **Money committed but not paid (Unliquidated)** |
| L | **ULO_%** | =IF(F2=0,0,K2/F2) | % of obligations unpaid |

---

## CLEAR DEFINITIONS

### Unobligated (Column G)
- **Formula:** Allocated - Obligated
- **Meaning:** Budget authority that hasn't been committed yet
- **Example:** $500K allocated, $350K obligated = **$150K Unobligated**
- **Good or Bad:** Depends on timing. High early is normal, high late might indicate execution problems

### ULO / Unliquidated (Column K)
- **Formula:** Obligated - Spent
- **Meaning:** Commitments made but not yet paid
- **Example:** $350K obligated, $250K spent = **$100K ULO**
- **Good or Bad:** Some ULO is normal (invoices pending payment). Very high might indicate payment processing delays

---

## EXAMPLE WITH REAL NUMBERS

| Allocated | Obligated | Unobligated | Spent | ULO | Interpretation |
|-----------|-----------|-------------|-------|-----|----------------|
| $500,000 | $350,000 | **$150,000** (30%) | $250,000 | **$100,000** (29%) | $150K still available to commit; $100K committed but awaiting payment |
| $1,000,000 | $900,000 | **$100,000** (10%) | $800,000 | **$100,000** (11%) | Nearly fully committed; normal payment lag |
| $200,000 | $50,000 | **$150,000** (75%) | $40,000 | **$10,000** (20%) | Slow execution - most budget uncommitted |

---

## IMPLEMENTATION STEPS

### Step 1: Rename Existing Columns (1 minute)

1. Open v6 in Excel
2. Go to **Country_Budgets** sheet
3. Click **G1**, change "ULO" to `Unobligated`
4. Click **H1**, change "ULO_Percent" to `Unobligated_%`

### Step 2: Add New Column Headers (1 minute)

5. Click **J1**, type `Spent_Amount`
6. Click **K1**, type `ULO`
7. Click **L1**, type `ULO_%`

### Step 3: Add Formulas (2 minutes)

8. Click **K2**, type `=F2-J2`, press Enter
9. Click **L2**, type `=IF(F2=0,0,K2/F2)`, press Enter
10. Select K2:L2, copy
11. Select K2:L5000, paste

### Step 4: Format Columns (1 minute)

12. Select column J, format as Currency: `$#,##0`
13. Select column K, format as Currency: `$#,##0`
14. Select column L, format as Percentage: `0.0%`

### Step 5: Enter Spent Data (varies)

15. Click J2, enter actual spent amount (or leave blank for now)
16. Repeat for other projects

**Total time:** 5 minutes (plus data entry)

---

## UPDATE MASTER_PROJECTS

After adding these columns to Country_Budgets, update Master_Projects to aggregate:

### Add New Column after P (Total_ULO becomes something else)

**Column Q: Total_Spent**

**Q1:** `Total_Spent`

**Q2:**
```
=SUMIF(Country_Budgets[Unique_ID],B2,Country_Budgets[Spent_Amount])
```

**Column R: Total_Unliquidated**

**R1:** `Total_Unliquidated`

**R2:**
```
=SUMIF(Country_Budgets[Unique_ID],B2,Country_Budgets[ULO])
```

Or calculate directly:
```
=O2-Q2
```
(Total_Obligated - Total_Spent)

**Copy both down to Q2:R1000**

---

## TERMINOLOGY CLARITY

### Budget Terms Explained:

**Allocated/Allocation:**
- Money authorized for the project
- Upper limit of what can be spent
- Set at project start

**Obligated/Obligation:**
- Money committed via contracts, purchase orders
- Legal commitment to pay
- Creates accounts payable

**Spent/Expenditure:**
- Money actually disbursed
- Checks issued, transfers made
- Reduces cash/bank balance

**Unobligated:**
- Allocated but not yet committed
- Still available to contract

**Unliquidated (ULO):**
- Obligated but not yet paid
- Accounts payable
- Will eventually become expenditure

---

## FORMULAS QUICK REFERENCE

| Column | Header | Formula |
|--------|--------|---------|
| G | Unobligated | `=E2-F2` |
| H | Unobligated_% | `=IF(E2=0,0,G2/E2)` |
| J | Spent_Amount | [Data entry] |
| K | ULO | `=F2-J2` |
| L | ULO_% | `=IF(F2=0,0,K2/F2)` |

---

## TESTING

After implementation:

1. Enter test data:
   - E2: 1000000 (Allocated)
   - F2: 750000 (Obligated)
   - J2: 500000 (Spent)

2. Check calculations:
   - G2 should show: 250000 (Unobligated)
   - H2 should show: 25.0% (Unobligated_%)
   - K2 should show: 250000 (ULO)
   - L2 should show: 33.3% (ULO_%)

**Calculation check:**
- Allocated (1,000,000) = Obligated (750,000) + Unobligated (250,000) ✓
- Obligated (750,000) = Spent (500,000) + ULO (250,000) ✓

---

## BENEFITS OF CLEAR NAMING

**Before (confusing):**
- G: ULO ← What does this mean?
- K: ULO ← Same name, different calc? Confusing!

**After (clear):**
- G: Unobligated ← Clearly "not yet committed"
- K: ULO ← Clearly "unliquidated obligations"

Now anyone reading the spreadsheet will understand:
- **Unobligated** = Available to commit
- **ULO** = Committed but not yet paid

---

**This naming follows federal budget terminology standards!**
