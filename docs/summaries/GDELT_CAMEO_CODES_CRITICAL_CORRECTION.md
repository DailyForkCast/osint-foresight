# CRITICAL CORRECTION: GDELT CAMEO Event Codes

**Date:** 2025-11-02
**Status:** URGENT - Production queries using incorrect codes
**Impact:** All GDELT queries since implementation using wrong event codes

---

## Critical Errors Identified

### Error 1: Wrong Code for Formal Agreements

**INCORRECT USAGE:**
```python
'075': 'Sign formal agreement'  # WRONG!
```

**CORRECT USAGE:**
```python
'057': 'Sign formal agreement'  # CORRECT
'075': 'Grant asylum'            # What 075 actually means
```

**Impact:**
- Query 1 "Formal Agreements Signed" was searching for asylum grants, not agreements
- All MOUs, treaties, cooperation agreements were MISSED
- Code 057 events exist in our database but we weren't querying them

**Evidence:**
- Official GDELT codes: https://www.gdeltproject.org/data/lookups/CAMEO.eventcodes.txt
- Database verification showed 075 events are asylum-related (Xinjiang refugees, dissidents)
- Database verification showed 057 events are actual agreements (Venezuela-China trade deals)

---

### Error 2: Misunderstanding of Science/Technology Cooperation

**INCORRECT ASSUMPTION:**
```python
'061': 'Science/technology cooperation'  # WRONG INTERPRETATION!
```

**CORRECT UNDERSTANDING:**
```python
'061': 'Cooperate economically'  # What 061 actually means
```

**Key Finding:** CAMEO codes the TYPE of cooperation, not the SUBJECT matter

**How Science/Technology Events Are Actually Coded:**

| Event Type | CAMEO Code | Description |
|------------|------------|-------------|
| Tech trade agreements | 061 | Cooperate economically |
| Research data sharing | 064 | Share intelligence or information |
| Science delegation visits | 042/043 | Make/host a visit |
| Research partnership negotiations | 046 | Engage in negotiation |
| Joint research center MOU | 057 | Sign formal agreement |
| Science funding/grants | 071 | Provide economic aid |

**Why This Matters:**
- Science/tech cooperation is NOT a single code
- Must search across multiple codes based on interaction type
- Code 061 captures commercial/economic tech partnerships (which is valuable!)
- But academic research collaboration may be coded as 064 (information sharing) or 057 (if formalized with MOU)

---

## Verified Correct Codes from Official GDELT Documentation

Source: https://www.gdeltproject.org/data/lookups/CAMEO.eventcodes.txt

### Category 04: CONSULT
```
040	Consult, not specified below
041	Discuss by telephone
042	Make a visit
043	Host a visit
044	Meet at a third location
045	Mediate
046	Engage in negotiation
```

### Category 05: ENGAGE IN DIPLOMATIC COOPERATION
```
050	Engage in diplomatic cooperation, not specified below
051	Praise or endorse
052	Defend verbally
053	Rally support on behalf of
054	Grant diplomatic recognition
055	Apologize
056	Forgive
057	Sign formal agreement  ← THIS IS THE CORRECT CODE FOR AGREEMENTS
```

### Category 06: ENGAGE IN MATERIAL COOPERATION
```
060	Engage in material cooperation, not specified below
061	Cooperate economically
062	Cooperate militarily
063	Engage in judicial cooperation
064	Share intelligence or information
```

### Category 07: PROVIDE AID
```
070	Provide aid, not specified below
071	Provide economic aid
072	Provide military aid
073	Provide humanitarian aid
074	Provide military protection or peacekeeping
075	Grant asylum  ← THIS IS WHAT 075 ACTUALLY MEANS
```

---

## Required Corrections

### 1. Immediate Fix: Update All Query Scripts

**Files to Update:**
- `scripts/analysis/gdelt_documented_events_queries_comprehensive.py`
- `GDELT_DOCUMENTED_EVENTS_STRATEGY.md`
- `GDELT_RECOMMENDED_EVENT_CODES_TO_ADD.md`
- `GDELT_CAMEO_EVENT_CODES_REFERENCE.md`

**Changes Required:**
```python
# OLD (INCORRECT)
EVENT_CODES = [
    '075',  # WRONG: This is "Grant asylum" not "Sign formal agreement"
    '061',  # Correct code but wrong description
    ...
]

# NEW (CORRECT)
EVENT_CODES = [
    '057',  # Sign formal agreement (MOUs, treaties, cooperation agreements)
    '061',  # Cooperate economically (trade deals, commercial partnerships)
    '064',  # Share intelligence or information (research/data sharing)
    ...
]
```

### 2. Revalidation Required

After fixing codes, must:
1. Re-run all queries with correct codes
2. Compare results: How many 057 events vs 075 events?
3. Verify 057 events are actual agreements (check source URLs)
4. Assess what we missed by using wrong code

### 3. Intelligence Gaps to Address

**What We've Been Missing:**
- All formal agreements coded as 057 (MOUs, treaties, cooperation agreements)
- Research/data sharing agreements coded as 064
- Science cooperation that's coded as economic cooperation (061) - we were actually getting these, just mislabeling them

**What We've Been Incorrectly Capturing:**
- Asylum grants (075) thinking they were formal agreements
- Though asylum events (Xinjiang refugees, dissidents) may still have intelligence value

---

## Testing the Correction

### Test Query 1: Compare 057 vs 075 for China-Europe

```sql
-- How many "Sign formal agreement" events (057) do we have?
SELECT COUNT(*) as agreement_count
FROM gdelt_events
WHERE event_code = '057'
AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
AND actor2_country_code IN ('GBR','DEU','FRA','ITA','ESP','POL','NLD','SWE','NOR','FIN','DNK',...);

-- How many "Grant asylum" events (075) were we incorrectly querying?
SELECT COUNT(*) as asylum_count
FROM gdelt_events
WHERE event_code = '075'
AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN');
```

### Test Query 2: Sample 057 Events (Real Agreements)

```sql
SELECT event_date, actor1_name, actor2_name, source_url
FROM gdelt_events
WHERE event_code = '057'
AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
ORDER BY event_date DESC
LIMIT 10;
```

### Test Query 3: Intelligence Sharing Events (064)

```sql
-- Research/data sharing we've been missing
SELECT event_date, actor1_name, actor2_name, source_url
FROM gdelt_events
WHERE event_code = '064'
AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
ORDER BY event_date DESC
LIMIT 10;
```

---

## Lessons Learned

1. **Always verify against primary source documentation**
   - We assumed code meanings without checking official GDELT docs
   - Should have fetched CAMEO.eventcodes.txt file first

2. **Validate with actual data**
   - Should have examined source URLs for sample events early
   - Database verification would have caught this immediately

3. **CAMEO codes TYPE not SUBJECT**
   - Codes represent the nature of interaction (sign agreement, cooperate, threaten)
   - NOT the subject matter (science, economics, military)
   - Subject matter comes from context (actors, source article content)

4. **Zero Fabrication Protocol applies to metadata too**
   - We "fabricated" that 075 = formal agreements without verification
   - Must apply same rigor to data structure as to data content

---

## Next Steps

1. ✓ **Document the error** (this file)
2. **Update all query scripts** with correct codes
3. **Re-run queries** to compare results
4. **Assess intelligence gaps** - what did we miss?
5. **Add code 064** (Share intelligence/information) for research cooperation
6. **Consider keeping 075** (Grant asylum) as separate category - Xinjiang refugee intelligence has value

---

## Recommended Event Code Set (Corrected)

### Critical Codes - Cooperation & Agreements
```
030  Express intent to cooperate
040  Consult
042  Make a visit
043  Host a visit
045  Mediate
046  Engage in negotiation
051  Praise or endorse
057  Sign formal agreement ← CORRECTED
061  Cooperate economically ← Correctly labeled
062  Cooperate militarily
064  Share intelligence or information ← NEW ADDITION
```

### Phase 1 Additions - Aid, Sanctions, Legal (Already Correct)
```
070  Provide aid (general)
071  Provide economic aid (BRI)
072  Provide military aid
0234 Appeal for technical/material aid
081  Ease administrative sanctions
082  Ease economic sanctions
106  Demand policy change
111  Criticize/denounce
112  Accuse (general)
1125 Accuse of espionage
115  Bring lawsuit
116  Find guilty/liable
172  Impose administrative sanctions
173  Arrest/detain/charge
174  Impose economic sanctions
1711 Confiscate property
```

### Optional Addition - Asylum Intelligence
```
075  Grant asylum (Xinjiang refugees, dissidents - has intelligence value)
```

---

**Document Status:** Critical correction identified - immediate action required
**Priority:** HIGH - affects all GDELT intelligence products
**Owner:** Needs immediate review and approval to proceed with corrections
