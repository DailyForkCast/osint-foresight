# Conference Scale Criteria - Key Changes Summary
## From Global to Targeted 44-Country Focus

**Version:** 1.0
**Date:** 2025-09-14
**Purpose:** Document the refinement from "30+ countries" to targeted criteria

---

## 🎯 FUNDAMENTAL SHIFT

### OLD Approach (Too Broad)
- **Tier 1:** 30+ countries attending
- **Problem:** Missed critical small meetings
- **Example:** Would prioritize generic trade show over US-Taiwan-China semiconductor workshop

### NEW Approach (Targeted)
- **Tier 1:** 3+ countries if China + Target + US
- **Tier 1:** 8+ countries if in our 44 with China
- **Smart:** Recognizes that WHO matters more than HOW MANY

---

## 📊 CRITICAL INSIGHT

**"A 3-country meeting with US, Netherlands, and China discussing semiconductor equipment is MORE important than a 50-country renewable energy conference."**

---

## 🔄 WHAT CHANGED

### 1. International Scale Threshold
```yaml
OLD:
  tier_1: ">30 countries"
  tier_2: "15-30 countries"
  tier_3: "<15 countries"

NEW:
  tier_1_with_china: "3+ countries (if right mix)"
  tier_1_without_china: "8+ countries from our 44"
  tier_2: "5+ countries"
  tier_3: "3+ countries"
```

### 2. China as Force Multiplier
```yaml
OLD:
  china_presence: "One factor among many"

NEW:
  china_present:
    - 3_countries: "Can be Tier 1"
    - 5_countries: "Likely Tier 1"
    - 8_countries: "Definitely Tier 1"

  china_absent:
    - need_8+_countries: "For Tier 1"
    - need_sensitive_tech: "And cutting edge"
```

### 3. Location Importance
```yaml
OLD:
  location: "Not heavily weighted"

NEW:
  in_our_44_countries: "2x importance multiplier"
  china_in_our_territory: "Automatic elevation"
  bilateral_in_target: "Significant even if small"
```

---

## 💡 PRACTICAL EXAMPLES

### NOW Tier 1 (Weren't Before)

```yaml
newly_critical:

  - event: "Quantum Encryption Workshop"
    countries: 4  # US, UK, China, Canada
    why_now_tier_1: "Standards control by few players"
    old_classification: "Would have been Tier 3 (too small)"

  - event: "Baltic Drone Technology Summit"
    countries: 6  # Estonia, Latvia, Lithuania, Poland, Ukraine, China observer
    why_now_tier_1: "In our territory, China observing sensitive tech"
    old_classification: "Would have been Tier 2 (not enough countries)"

  - event: "ASML Technology Symposium"
    countries: 3  # Netherlands, US, China
    why_now_tier_1: "Critical semiconductor chokepoint"
    old_classification: "Would have been ignored (too small)"
```

### NOW Lower Priority (Were Higher)

```yaml
appropriately_downgraded:

  - event: "Global Climate Summit"
    countries: 195
    why_now_lower: "Not focused on our sensitive technologies"
    new_classification: "Monitor for specific dual-use sessions only"

  - event: "World Economic Forum"
    countries: 100+
    why_now_lower: "Too broad, limited technical content"
    new_classification: "Track specific side meetings only"
```

---

## 📈 IMPACT ON COLLECTION

### Collection Efficiency Improved

```python
def collection_impact():
    """
    How the refined criteria improves our focus
    """

    old_approach = {
        "conferences_monitored": 500,  # Everything international
        "relevant_intelligence": "20%",  # Most was noise
        "missed_critical": "High",  # Small important meetings ignored
    }

    new_approach = {
        "conferences_monitored": 150,  # Focused set
        "relevant_intelligence": "80%",  # Mostly valuable
        "missed_critical": "Low",  # Catches small but important
    }

    improvement = {
        "efficiency": "4x better signal/noise ratio",
        "coverage": "Better capture of critical meetings",
        "resources": "Can go deeper on what matters"
    }
```

---

## 🎯 DECISION RULES

### Quick Classification Guide

```python
def quick_classify(event):
    """
    Rapid classification based on refined criteria
    """

    # INSTANT TIER 1
    if event.has_china and event.has_target_country and event.has_us:
        if event.countries >= 3:
            return "TIER_1"  # Triangle complete

    # TIER 1 WITH SCALE
    if event.countries >= 8:
        if count_our_44(event) >= 5 and event.has_china:
            return "TIER_1"

    # TIER 1 SPECIALIZED
    if event.sensitive_tech and event.china_percentage > 20:
        if event.countries >= 5:
            return "TIER_1"

    # OTHERWISE EVALUATE
    if event.has_china:
        threshold = 3
    else:
        threshold = 8

    if event.relevant_countries >= threshold:
        return "TIER_1"
    elif event.relevant_countries >= threshold * 0.6:
        return "TIER_2"
    else:
        return "TIER_3"
```

---

## ✅ VALIDATION EXAMPLES

### Real Events Reclassified

| Event | Countries | Old Tier | New Tier | Why Changed |
|-------|-----------|----------|----------|-------------|
| Netherlands Semiconductor Workshop | 3 | Ignored | Tier 1 | US-NL-China triangle |
| European Space Conference | 12 | Tier 2 | Tier 1 | 8 from our 44 + China |
| Asia-Pacific AI Summit | 8 | Tier 2 | Tier 1 | China 40% of participants |
| Global Manufacturing Expo | 45 | Tier 1 | Tier 3 | Not sensitive tech |
| ASEAN Tech Conference | 10 | Tier 2 | Tier 3 | Only 2 from our 44 |

---

## 📊 CHINA WEIGHTING IMPACT

### How China Changes Everything

```yaml
without_china:
  3_countries: "Tier 3 - Too small"
  5_countries: "Tier 2 - Modest"
  8_countries: "Tier 1 - IF from our 44"

with_china:
  3_countries: "Tier 1 - IF includes Target + US"
  5_countries: "Tier 1 - IF sensitive tech"
  8_countries: "Tier 1 - Automatically"

china_as_sponsor:
  any_size: "Elevate one tier minimum"

china_delegation_10+:
  any_size: "Warrants deep analysis"
```

---

## 🎯 BOTTOM LINE

### What This Means for Analysis

1. **Stop counting countries** - Start assessing players
2. **Small can be critical** - IF the right combination
3. **China is a multiplier** - Not a requirement
4. **Location matters** - In our 44 gets priority
5. **Technology sensitivity** - Trumps size every time

### Collection Guidance

- **Don't ignore small meetings** with China + Target + US
- **Don't over-collect large events** without relevant players
- **Focus on triangles** not raw attendance
- **Track China percentage** not just presence
- **Watch our 44 countries** not the whole world

---

## REMEMBER

**Quality > Quantity in country participation**

**3 critical countries > 30 irrelevant ones**

**China + Target + US = Always investigate**

**8 from our 44 = New threshold for "international"**

**Adjust collection effort to match true importance, not size**
