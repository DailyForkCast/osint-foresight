# Fix Three Issues - Quick Guide
**1. Add PM to Project_Spotlight | 2. Add Missing Countries | 3. Rename Spend Columns**

---

## ISSUE 1: Add Project Manager to Project_Spotlight

### Where to Add It

**Location:** Project_Spotlight sheet, in the header section

**Suggested location:** Row 4, between existing summary fields

### Implementation

**Cell C4:**
```
Project Manager:
```

**Cell D4:**
```
=XLOOKUP($B$2,Master_Projects[Unique_ID],Master_Projects[Project_Manager],"No PM Assigned")
```

Or without XLOOKUP:
```
=IFERROR(INDEX(Master_Projects[Project_Manager],MATCH($B$2,Master_Projects[Unique_ID],0)),"No PM Assigned")
```

**Alternative Location:** Add as row in the summary box

Current summary box is B5:F14. You could add:
- **B4:** "Project Manager:"
- **C4:** Formula to lookup PM

---

## ISSUE 2: Add Missing Countries

### Countries to Add

Missing from Country_Regions (98 total, should be 101):
1. **MU** - Mauritius (AF - Africa)
2. **NA** - Namibia (AF - Africa)
3. **OM** - Oman (NEA - Near East Asia)

**Moldova (MD) exists** but might have data issue - check if it's in Config_Lists

### Step-by-Step Addition

#### Add to Country_Regions Sheet

1. Go to **Country_Regions** sheet
2. Find last row with data (should be around row 99)
3. Add these rows:

| Country_Code | Country_Name | Region |
|-------------|-------------|--------|
| MU | Mauritius | AF |
| NA | Namibia | AF |
| OM | Oman | NEA |

**Specific cells:**

**Row 100:**
- A100: `MU`
- B100: `Mauritius`
- C100: `AF`

**Row 101:**
- A101: `NA`
- B101: `Namibia`
- C101: `AF`

**Row 102:**
- A102: `OM`
- B102: `Oman`
- C102: `NEA`

#### Add to Config_Lists Sheet

1. Go to **Config_Lists** sheet
2. Find last row in Country section (columns D, E, F)
3. Add same three countries:

**Row 102:**
- D102: `MU`
- E102: `Mauritius`
- F102: `AF`

**Row 103:**
- D103: `NA`
- E103: `Namibia`
- F103: `AF`

**Row 104:**
- D104: `OM`
- E104: `Oman`
- F104: `NEA`

#### Fix Moldova (if not in Config_Lists)

Check if Moldova is in Config_Lists:
1. Go to Config_Lists
2. Search column D for "MD"
3. If missing, add it:

| Country_Code | Country_Name | Region |
|-------------|-------------|--------|
| MD | Moldova | EUR |

---

## ISSUE 3: Rename Spend Columns

### Current Structure (to change):

You want to add Spent_Amount and rename the following columns:

**Current plan was:**
- J: Spent_Amount
- K: Unliquidated
- L: Spend_Rate

**Your preference:**
- J: Spent_Amount (keep this)
- K: **ULO** (instead of "Unliquidated")
- L: **ULO_%** (instead of "Spend_Rate")

### Important Note on Terminology

**Traditional meanings:**
- **ULO** = Unobligated (Allocated - Obligated) ← You already have this in column G
- **Unliquidated** = Obligated - Spent ← What column K will calculate

**Your naming:**
- Column K will calculate "Obligated - Spent" but be labeled "ULO"
- This might cause confusion since you have another "ULO" in column G

**Recommendation:** Consider these alternatives to avoid confusion:

**Option A: Use your naming (as requested)**
- G: ULO (Unobligated = Allocated - Obligated)
- H: ULO_Percent
- K: ULO (Unliquidated = Obligated - Spent) ← **Same name, different meaning**
- L: ULO_%

**Option B: Clarify with different names**
- G: Unobligated (or UBO for Unobligated)
- H: Unobligated_%
- K: ULO (Unliquidated = Obligated - Spent)
- L: ULO_%

**Option C: Use full names**
- G: Unobligated
- H: Unobligated_%
- K: Unliquidated
- L: Unliquidated_%

**I'll give you formulas for your requested naming (Option A), but note the column naming issue.**

### Implementation (Your Requested Names)

**J1:** `Spent_Amount`

**K1:** `ULO`

**L1:** `ULO_%`

**Formulas:**

**K2:**
```
=F2-J2
```
(Obligated minus Spent = Unliquidated obligations)

**L2:**
```
=IF(F2=0,0,K2/F2)
```
Format as Percentage

**Copy down:** K2:L2 to K3:L5000

### Final Column Structure

| Col | Header | Formula | Meaning |
|-----|--------|---------|---------|
| E | Allocated_Amount | [Data] | Total budget |
| F | Obligated_Amount | [Data] | Committed |
| G | ULO | =E2-F2 | **Un**obligated |
| H | ULO_Percent | =IF(E2=0,0,G2/E2) | % Unobligated |
| I | Spend_Health | =H2 | Health metric |
| J | Spent_Amount | [Data] | Actually paid |
| K | ULO | =F2-J2 | **Un**liquidated |
| L | ULO_% | =IF(F2=0,0,K2/F2) | % Unliquidated |

**Note:** Columns G and K both labeled "ULO" but measure different things.

---

## COMPLETE IMPLEMENTATION CHECKLIST

### ✓ Task 1: Add PM to Project_Spotlight (2 minutes)

- [ ] Go to Project_Spotlight
- [ ] Cell C4: Type "Project Manager:"
- [ ] Cell D4: `=IFERROR(INDEX(Master_Projects[Project_Manager],MATCH($B$2,Master_Projects[Unique_ID],0)),"")`

### ✓ Task 2: Add Missing Countries (5 minutes)

**Country_Regions:**
- [ ] Row 100: MU | Mauritius | AF
- [ ] Row 101: NA | Namibia | AF
- [ ] Row 102: OM | Oman | NEA

**Config_Lists:**
- [ ] Row 102: MU | Mauritius | AF
- [ ] Row 103: NA | Namibia | AF
- [ ] Row 104: OM | Oman | NEA
- [ ] Check MD (Moldova) exists in Config_Lists

### ✓ Task 3: Add Spend Columns (3 minutes)

**Country_Budgets:**
- [ ] J1: `Spent_Amount`
- [ ] K1: `ULO`
- [ ] L1: `ULO_%`
- [ ] K2: `=F2-J2`
- [ ] L2: `=IF(F2=0,0,K2/F2)`
- [ ] Copy K2:L2 down to all rows
- [ ] Format L as percentage

---

## QUICK COPY-PASTE FORMULAS

### Project_Spotlight D4 (PM):
```
=IFERROR(INDEX(Master_Projects[Project_Manager],MATCH($B$2,Master_Projects[Unique_ID],0)),"")
```

### Country_Budgets K2 (ULO - Unliquidated):
```
=F2-J2
```

### Country_Budgets L2 (ULO_%):
```
=IF(F2=0,0,K2/F2)
```

---

## TESTING

After making changes:

1. **Project_Spotlight** - Select a project in B2, check PM shows in D4
2. **Country_Regions** - Check new countries appear (should be 101 total now)
3. **Config_Lists** - Verify dropdowns include new countries
4. **Country_Budgets** - Enter spent amount in J2, check K2 and L2 calculate

---

## REGION CODES REFERENCE

For the new countries:
- **AF** = Africa (Mauritius, Namibia)
- **NEA** = Near East Asia (Oman)
- **EUR** = Europe (Moldova - if you need to re-add it)

All 6 regions:
- EUR = Europe
- WHA = Western Hemisphere
- EAP = East Asia Pacific
- AF = Africa
- NEA = Near East Asia
- SCA = South Central Asia

---

## MOLDOVA TROUBLESHOOTING

If Moldova isn't loading correctly:

1. Check **Country_Regions** - should have MD | Moldova | EUR
2. Check **Config_Lists** - should have MD | Moldova | EUR in columns D, E, F
3. If missing from Config_Lists, dropdowns won't work
4. Named range "List_CountryCodes" should include MD

---

**Which issue do you want me to help you implement first?**
1. Add PM to Project_Spotlight (quickest)
2. Add missing countries (important for completeness)
3. Add spend columns (most complex)
