# CRITICAL: Additional CAMEO Code Errors Found

**Date:** 2025-11-02
**Status:** 🚨 URGENT - More incorrect codes in production script

---

## Error 3: Code 046 Mislabeled

### What We Have (WRONG):
```python
'046': 'Material cooperation (receive)'
```

### What It Actually Is (CORRECT):
```
046: Engage in negotiation
```

### Evidence from Database:
```
Sample 046 events:
- China-South Korea: FX swap and economic agreement negotiations
- US-China negotiations
- China-North Korea negotiations
- China-Japan negotiations
- Xi Jinping negotiation events
```

### Impact:
- **Query 6** incorrectly groups code 046 with code 045 (Mediate) as "Material cooperation"
- Code 046 is actually HIGH-VALUE: captures partnership negotiations, trade talks, cooperation framework negotiations
- These are pre-agreement negotiations that lead to code 057 (formal agreements)

---

## Error 4: Code 174 Mislabeled

### What We Have (WRONG):
```python
'174': 'Impose economic sanctions'
```

### What It Actually Is (CORRECT):
```
174: Expel or deport individuals
```

### Evidence from Database:
```
Sample 174 events:
- Cuba extraditing Chinese drug trafficker "Brother Wang" to Mexico
- Canadian deportations of Chinese individuals
```

### Impact:
- **Query 3** incorrectly treats code 174 as economic sanctions
- Code 174 is actually MODERATE-VALUE: tracks expelled Chinese diplomats, researchers, executives
- Mixing deportations with sanctions in same query creates misleading intelligence

---

## Missing: The REAL Economic Sanctions Code

### Code 163: Impose embargo, boycott, or sanctions
- **This is the actual code for economic sanctions**
- **188 events available** in current database
- **We are NOT currently using this code!**

### What We're Missing:
- Actual embargo impositions
- Trade sanctions
- Technology export bans
- 5G equipment bans (may be coded as 163, not 172)

---

## Confusion Between Code Types

### Administrative Sanctions (172) vs Economic Sanctions (163/174?)

**Code 172:** Impose administrative sanctions
- Travel bans, visa restrictions
- Regulatory penalties
- Administrative penalties

**Code 163:** Impose embargo, boycott, or sanctions
- **This is the main economic sanctions code**
- Trade embargoes
- Technology bans
- Export controls

**Code 174:** Expel or deport individuals
- **NOT sanctions at all!**
- Deportation of individuals
- Expulsion from country

### Our Current Error:
We're using 172 (admin sanctions) and 174 (deportations) thinking 174 = economic sanctions.
The REAL economic sanctions code is 163, which we're not using!

---

## Code 045 vs 046 Confusion

**Code 045:** Mediate
- Third-party mediation
- Dispute resolution facilitation

**Code 046:** Engage in negotiation
- Direct bilateral/multilateral negotiations
- Partnership talks
- Agreement negotiations

### Our Current Error:
Query 6 groups both as "Material cooperation" but:
- 045 = Mediation (third-party facilitation)
- 046 = Negotiation (direct talks)

These are separate diplomatic activities and should be distinguished.

---

## Required Corrections

### 1. Fix Code 046 Description
```python
# OLD (WRONG)
'046': 'Material cooperation (receive)',

# NEW (CORRECT)
'046': 'Engage in negotiation',
```

### 2. Fix Code 174 Description
```python
# OLD (WRONG)
'174': 'Impose economic sanctions',

# NEW (CORRECT)
'174': 'Expel or deport individuals',
```

### 3. Add Missing Code 163
```python
# ADD THIS CODE
'163': 'Impose embargo, boycott, or sanctions',
```

### 4. Update Query 3 (Sanctions)
```python
# OLD
WHERE event_code IN ('081', '082', '106', '172', '174')

# NEW
WHERE event_code IN ('081', '082', '106', '163', '172')
# Remove 174 (deportations), Add 163 (actual economic sanctions)
```

### 5. Create New Query for Deportations/Expulsions
```python
# NEW QUERY
WHERE event_code = '174'
# Track expelled Chinese diplomats, researchers, executives separately
```

### 6. Update Query 6 (Consult/Negotiate)
```python
# OLD - "Material Cooperation"
WHERE event_code IN ('045', '046')

# OPTION A - Separate Mediation and Negotiation
WHERE event_code = '045'  # Mediation
WHERE event_code = '046'  # Negotiation

# OPTION B - Rename to "Diplomatic Engagement"
WHERE event_code IN ('045', '046')
# But fix labels to distinguish mediation vs negotiation
```

---

## Impact Assessment

### What We're Currently Missing:

1. **188 economic sanctions events** (code 163)
   - Actual embargo impositions
   - Technology export bans
   - Trade sanctions

2. **Proper categorization of 174 events**
   - Expelled Chinese diplomats
   - Deported researchers/executives
   - Extradited individuals

3. **Proper categorization of 046 events**
   - Partnership negotiations
   - Trade negotiation sessions
   - Pre-agreement talks

### What We're Currently Mis-Categorizing:

1. **Query 3 results are mixed:**
   - Includes actual sanctions (172, maybe 163)
   - But ALSO includes deportations (174) which aren't sanctions
   - Misleading intelligence picture

2. **Query 6 results are mixed:**
   - Includes mediation (045)
   - But ALSO includes negotiations (046)
   - Both valuable but different diplomatic activities

---

## Verification Queries

### Test Code 163 (Real Economic Sanctions):
```sql
SELECT event_date, actor1_name, actor2_name, source_url
FROM gdelt_events
WHERE event_code = '163'
AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
AND (actor1_country_code IN (...European countries...)
     OR actor2_country_code IN (...European countries...))
ORDER BY event_date DESC
LIMIT 10;
```

### Expected Results:
- EU imposing sanctions on Chinese entities
- UK technology export bans
- US/European embargoes on Chinese companies
- Trade restrictions and boycotts

---

## Updated Event Code Count

### Before Correction:
- 30 codes total
- Missing 163 (economic sanctions)
- Mislabeling 046 (negotiations)
- Mislabeling 174 (deportations)

### After Correction:
- 31 codes total (adding 163)
- All codes properly labeled
- All queries properly categorized

---

## Recommended Query Structure

### Query 3A: Ease Sanctions
```
Codes: 081, 082
Description: Easing of administrative or economic sanctions
```

### Query 3B: Impose Sanctions (CORRECTED)
```
Codes: 163, 172
Description:
- 163: Impose embargo, boycott, or economic sanctions
- 172: Impose administrative sanctions (travel bans, visa restrictions)
```

### Query 3C: Policy Demands
```
Code: 106
Description: Demand policy change
```

### Query 4A: Legal Actions (existing, keep as-is)
```
Codes: 111, 112, 1125, 115, 116, 173, 1711
```

### Query 4B: Expulsions/Deportations (NEW)
```
Code: 174
Description: Expel or deport individuals
Purpose: Track expelled Chinese diplomats, researchers, executives
```

### Query 6: Diplomatic Engagement (RENAMED from "Material Cooperation")
```
Codes: 045, 046
Description:
- 045: Mediate (third-party facilitation)
- 046: Engage in negotiation (direct talks)
```

---

## Priority

**URGENT - HIGH PRIORITY**

This is the second major code error discovered today (after the 075→057 correction).

**Action Required:**
1. Fix descriptions for codes 046 and 174
2. Add code 163 (economic sanctions)
3. Restructure Query 3 to separate sanctions from deportations
4. Create new query for code 174 (deportations)
5. Re-test all queries with corrections
6. Validate results against source URLs

**Zero Fabrication Protocol:**
We fabricated code meanings again without verification. Must verify ALL remaining codes against official CAMEO documentation before proceeding.

---

## Next Steps

1. ✅ Document error (this file)
2. 📋 Update production script with corrections
3. 📋 Test code 163 query on current dataset
4. 📋 Verify ALL other code descriptions against official CAMEO
5. 📋 Re-run all queries with corrected codes
6. 📋 Update all documentation with correct codes

---

**Status:** Awaiting user approval to proceed with corrections
