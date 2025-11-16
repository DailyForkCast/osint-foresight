# OpenAlex Data Quality Audit

**Date:** 2025-10-11 18:05
**Issue:** High-speed processing collecting massive false positives
**Status:** PROCESSING STOPPED for quality review

---

## Critical Finding: FALSE POSITIVE RATE IS EXTREMELY HIGH

### Sample Database Analysis (17 works from initial sample)

**Distribution:**
- Semiconductors: 11 works
- Neuroscience: 3 works
- Smart_City: 1 work
- Quantum: 1 work
- AI: 1 work

### Manual Review of "Semiconductor" Works:

#### ❌ FALSE POSITIVE #1:
**Title:** "Comparative Genomic Analysis and BTEX Degradation Pathways of a Thermotolerant Cupriavidus cauae PHS"
**Field:** Biology/Genomics/Environmental Science
**Why Matched:** Unknown - possibly "microorganism" misidentified?
**Should Be:** REJECTED - not semiconductor technology

#### ❌ FALSE POSITIVE #2:
**Title:** "Simple physical model of collagen fibrillogenesis based on diffusion limited aggregation"
**Field:** Biology/Protein Science
**Why Matched:** Unknown - possibly "rod-like" or technical language?
**Should Be:** REJECTED - not semiconductor technology

#### ❌ FALSE POSITIVE #3:
**Title:** "A solid support for affinity chromatography that covalently binds thiol groups via a cleavable connection"
**Field:** Chemistry/Laboratory Techniques
**Why Matched:** Unknown - possibly "solid" + technical terms?
**Should Be:** REJECTED - not semiconductor technology

#### ❌ FALSE POSITIVE #4:
**Title:** "Are gram-negative bacteria a contraindication to selective preservation of infected prosthetic arterial grafts"
**Field:** Medicine/Surgery
**Why Matched:** Unknown - completely unrelated!
**Should Be:** REJECTED - not semiconductor technology

#### ❌ FALSE POSITIVE #5:
**Title:** "Automated diffraction tomography for the structure elucidation of twinned, sub-micrometer crystals"
**Field:** Crystallography
**Why Matched:** Possibly "sub-micrometer" triggered match?
**Should Be:** MAYBE - crystallography can relate to materials science, but not semiconductor manufacturing

---

## Root Cause Analysis

### Problem 1: Keywords Too Broad

**Current "Semiconductors" Keywords:**
```python
'Semiconductors': [
    'semiconductor', 'silicon', 'chip', 'transistor', 'mosfet',
    'integrated circuit', 'wafer', 'lithography', 'etching',
    'doping', 'cmos', 'gaas', 'gan', 'sic', 'wide bandgap',
    'euv', 'finfet', 'gate-all-around', 'chiplet', '3nm', '5nm'
]
```

**Issues:**
1. **"silicon"** - matches biology papers about "silicon" in organisms, silica chemistry
2. **"chip"** - matches "microchip", but also "potato chip" processing, "chip" in genetics context
3. **General technical terms** - match across many scientific fields

### Problem 2: No Context Checking

Current matching:
```python
def matches_technology(text, technology_keywords):
    if not text:
        return False
    text_lower = text.lower()
    for keyword in technology_keywords:
        if keyword.lower() in text_lower:  # SIMPLE SUBSTRING MATCH!
            return True
    return False
```

**This is TOO SIMPLE:**
- No word boundary checking
- No context requirements
- No negative filters
- No field/topic validation

### Problem 3: Ignoring OpenAlex Metadata

OpenAlex provides:
- **topics** - hierarchical topic classifications
- **concepts** - field-of-study concepts
- **primary_location.source** - journal/conference names
- **type** - work type (journal article, dissertation, etc.)

**We're not using ANY of this!** We're only looking at title + abstract text.

---

## Impact Assessment

### Full Processing Status (when stopped):
- **File 251/971** processed (26%)
- **AI: 10,000/10,000** - COMPLETE
- **Semiconductors: 10,000/10,000** - COMPLETE (but likely 90%+ false positives!)
- **Quantum: 231/10,000** - in progress

**Estimated False Positive Rate:**
- Based on sample: **80-90% of "semiconductor" matches are incorrect**
- If applied to 10,000 "semiconductor" works: **8,000-9,000 are garbage**

**This would severely pollute the master database!**

---

## Recommended Fixes

### Fix 1: Use OpenAlex Topics for Filtering

OpenAlex has hierarchical topics. Examples:
- "Electrical engineering" → "Semiconductor technology"
- "Materials science" → "Thin films"
- "Computer science" → "VLSI design"

**Recommendation:** Match keywords PLUS require relevant OpenAlex topic

### Fix 2: Improve Keyword Matching

**Current:** Simple substring match
**Recommended:**
- Word boundary matching (whole words only)
- Context requirements (e.g., "silicon wafer" not just "silicon")
- Negative filters (exclude biology, medicine journals)

### Fix 3: Journal/Source Filtering

**Add positive filter for relevant journals:**
- IEEE Transactions on Electron Devices
- IEEE Transactions on Semiconductor Manufacturing
- Journal of Applied Physics
- Solid-State Electronics
- etc.

**Add negative filter for irrelevant journals:**
- Exclude: biology, medicine, agriculture journals

### Fix 4: Multi-Stage Validation

```python
def validate_work(work, tech_keywords):
    # Stage 1: Quick keyword screen
    text = f"{title} {abstract}"
    if not keyword_matches(text, tech_keywords):
        return False

    # Stage 2: Check OpenAlex topics
    topics = work.get('topics', [])
    if not has_relevant_topic(topics, tech_name):
        return False

    # Stage 3: Check journal/source
    source = work.get('primary_location', {}).get('source', {})
    source_name = source.get('display_name', '')
    if is_excluded_source(source_name):
        return False

    return True
```

---

## Action Plan

### Immediate Actions:
1. ✅ **STOP current full processing** - avoid polluting database further
2. ⏳ **Analyze OpenAlex topic taxonomy** - understand their classification system
3. ⏳ **Review sample of correctly classified works** - learn patterns
4. ⏳ **Redesign matching algorithm** - multi-stage validation
5. ⏳ **Test on sample** - validate precision/recall
6. ⏳ **Clear database and restart** - with improved algorithm

### Testing Strategy:
1. **Gold standard sample:** Manually identify 50 TRUE semiconductor papers
2. **Negative sample:** Manually identify 50 clearly NON-semiconductor papers
3. **Test precision:** How many true positives vs false positives?
4. **Test recall:** Are we catching the gold standard papers?
5. **Iterate until:** Precision > 90%, Recall > 80%

---

## Lessons Learned

1. **Speed ≠ Quality** - Processing 10K works in minutes means nothing if 90% are wrong
2. **Simple keywords don't work** - Scientific literature is too diverse
3. **Use provided metadata** - OpenAlex has rich classifications we ignored
4. **Validate early** - Should have checked quality after first 100 works, not 20,000
5. **Domain expertise matters** - Need to understand what makes a paper "semiconductor research"

---

## Next Steps

**DO NOT resume full processing until:**
1. Matching algorithm is redesigned
2. Tested on validation set
3. Achieving acceptable precision/recall

**Estimated time to fix:** 1-2 hours for redesign + testing

**Current database:** Should be CLEARED and restarted with new algorithm

---

**Status:** ⚠️ PROCESSING PAUSED - QUALITY ISSUES UNDER REVIEW
**Recommendation:** DO NOT USE current "semiconductor" data - 80-90% false positive rate
