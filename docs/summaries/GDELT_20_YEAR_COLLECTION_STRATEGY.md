# GDELT 20-Year Historical Data Collection Strategy

**Project:** OSINT-Foresight
**Coverage:** 2005-2025 (20 years of China-Europe events)
**Created:** 2025-11-01
**Status:** PRODUCTION READY - Phased Execution Plan

---

## Executive Summary

**Goal:** Backfill 20 years of China-Europe events to enable historical analysis, trend detection, and validation of existing findings (e.g., Lithuania 2021 crisis).

**Approach:** Phased collection prioritizing critical periods and high-value years, with incremental validation at each phase.

**Total Volume Estimate:** ~14 million China-related events (2005-2025)
**Storage Required:** ~300GB compressed, ~1TB uncompressed
**Collection Time:** 40-60 hours over 2-3 weeks (phased)

---

## Strategic Rationale

### Why 20 Years (2005-2025)?

**2005 Start Date Justification:**
1. **China joins WTO (2001)** - trade integration begins
2. **EU-China Strategic Partnership (2003)** - formalized engagement
3. **2005-2008:** Critical period of European tech transfer to China
4. **GDELT data quality:** Excellent coverage from 2005 onwards
5. **Cross-reference alignment:** Your OpenAlex data starts ~2000, overlaps well

**Historical Coverage Enables:**
- ✅ Validate Lithuania 2021 crisis (-89.3% research drop)
- ✅ Track Belt & Road Initiative impact (2013-2025)
- ✅ Quantify trade war effects (2018-2020)
- ✅ Map COVID impact on EU-China relations (2020-2021)
- ✅ Measure decoupling trends (2022-2025)
- ✅ Baseline normal relations vs crisis periods

---

## Volume Estimates

### Methodology

Based on current collection (10,033 events in 2 days = 5,000 events/day):

```
Daily average: 5,000 events
Annual estimate: 5,000 × 365 = 1.825M events/year
20 years: 1.825M × 20 = 36.5M events
```

**Adjustment for historical growth:**
- 2005-2010: Lower volume (~500k/year) - less news digitization
- 2011-2015: Medium volume (~1M/year) - social media era
- 2016-2020: High volume (~1.5M/year) - increased coverage
- 2021-2025: Very high volume (~2M/year) - current levels

**Realistic Estimate:** ~14 million events over 20 years

### Storage Requirements

**Per Event:**
- Avg event size: ~2KB (33 fields + provenance)
- 14M events × 2KB = 28GB raw data

**With Indexes:**
- Database with indexes: ~100GB
- Compressed backups: ~30GB
- Total working space: ~150GB

**Recommendation:** Allocate 300GB for safety margin

---

## Phased Collection Plan

### Overview

Collect in **4 phases**, prioritizing critical periods first:

| Phase | Period | Priority | Events Est. | Time | Value |
|-------|--------|----------|-------------|------|-------|
| **Phase 1** | 2020-2025 (6y) | 🔴 CRITICAL | ~10M | 12-15h | Lithuania crisis, COVID, decoupling |
| **Phase 2** | 2013-2019 (7y) | 🟠 HIGH | ~8M | 10-12h | Belt & Road launch, trade war |
| **Phase 3** | 2008-2012 (5y) | 🟡 MEDIUM | ~5M | 6-8h | Financial crisis, EU debt crisis |
| **Phase 4** | 2005-2007 (3y) | 🟢 LOW | ~1.5M | 3-4h | Baseline establishment |
| **TOTAL** | 2005-2025 (21y) | - | ~24.5M | 31-39h | Complete historical record |

**Total Time:** 31-39 hours over 2-3 weeks

---

## Phase 1: Recent History (2020-2025) - CRITICAL

### Coverage: 2020-01-01 to 2025-11-01 (6 years)

**Priority:** 🔴 CRITICAL - Validate existing findings

**Key Events to Capture:**
- **2020:** COVID-19 pandemic, "Wolf Warrior" diplomacy
- **2021:** Lithuania Taiwan office crisis (validate -89.3% drop)
- **2022:** Ukraine war impact on EU-China relations
- **2023:** Decoupling accelerates, chip restrictions
- **2024-2025:** Current baseline (already have Nov 2025)

**Estimated Volume:** 10 million events
**Collection Time:** 12-15 hours (6 years × 2-2.5 hours/year)
**Storage:** ~100GB

### Execution Plan

**Step 1: Collect by Year (6 collections)**

```bash
# 2020
python scripts/collectors/gdelt_bigquery_collector.py --mode year --year 2020

# 2021 (Lithuania crisis year - HIGH PRIORITY)
python scripts/collectors/gdelt_bigquery_collector.py --mode year --year 2021

# 2022
python scripts/collectors/gdelt_bigquery_collector.py --mode year --year 2022

# 2023
python scripts/collectors/gdelt_bigquery_collector.py --mode year --year 2023

# 2024
python scripts/collectors/gdelt_bigquery_collector.py --mode year --year 2024

# 2025 (Jan-Nov)
python scripts/collectors/gdelt_bigquery_collector.py --mode custom --start-date 20250101 --end-date 20251101
```

**Step 2: Validate Lithuania 2021 Crisis**

```sql
-- Query Lithuania-China events 2020 vs 2021
SELECT
    SUBSTR(event_date, 1, 4) as year,
    COUNT(*) as events,
    AVG(avg_tone) as avg_sentiment
FROM gdelt_events
WHERE (actor1_country_code = 'LTU' AND actor2_country_code = 'CHN')
   OR (actor1_country_code = 'CHN' AND actor2_country_code = 'LTU')
  AND event_date BETWEEN '20200101' AND '20211231'
GROUP BY year;
```

**Expected Result:**
- 2020: Normal relations, positive sentiment
- 2021: Dramatic drop in events, very negative sentiment
- **Validates** OpenAlex -89.3% research drop

---

## Phase 2: Belt & Road Era (2013-2019) - HIGH PRIORITY

### Coverage: 2013-01-01 to 2019-12-31 (7 years)

**Priority:** 🟠 HIGH - Critical policy inflection point

**Key Events to Capture:**
- **2013:** Xi Jinping announces Belt & Road Initiative (BRI)
- **2014-2016:** BRI expansion across Europe (16+1 framework)
- **2017:** First BRI Forum in Beijing
- **2018-2019:** US-China trade war begins, EU reactions

**Estimated Volume:** 8 million events
**Collection Time:** 10-12 hours
**Storage:** ~80GB

### Execution Plan

```bash
# Collect 2013-2019 in annual batches
for year in {2013..2019}; do
    python scripts/collectors/gdelt_bigquery_collector.py --mode year --year $year
    echo "Completed year $year"
    sleep 60  # Pause between years
done
```

### Validation Queries

**BRI Announcement Impact:**
```sql
-- Sentiment shift 2012 vs 2014
SELECT
    SUBSTR(event_date, 1, 4) as year,
    COUNT(*) as events,
    AVG(avg_tone) as avg_sentiment
FROM gdelt_events
WHERE actor1_country_code = 'CHN'
  AND actor2_country_code IN ('ITA','GRC','PRT','HUN','POL')  -- BRI targets
  AND event_date BETWEEN '20120101' AND '20151231'
GROUP BY year;
```

**Expected Result:** Sentiment improvement 2013-2014 as BRI launched

---

## Phase 3: Pre-BRI Baseline (2008-2012) - MEDIUM PRIORITY

### Coverage: 2008-01-01 to 2012-12-31 (5 years)

**Priority:** 🟡 MEDIUM - Establish pre-BRI baseline

**Key Events to Capture:**
- **2008:** Beijing Olympics, financial crisis
- **2009-2010:** European debt crisis
- **2011:** Libya intervention (China abstains at UN)
- **2012:** Xi Jinping assumes power

**Estimated Volume:** 5 million events
**Collection Time:** 6-8 hours
**Storage:** ~50GB

### Execution Plan

```bash
# Collect 2008-2012
for year in {2008..2012}; do
    python scripts/collectors/gdelt_bigquery_collector.py --mode year --year $year
done
```

**Value:** Establishes "normal" EU-China relations baseline before BRI

---

## Phase 4: WTO Era (2005-2007) - LOW PRIORITY

### Coverage: 2005-01-01 to 2007-12-31 (3 years)

**Priority:** 🟢 LOW - Historical context only

**Key Events:**
- **2005:** China joins WTO (2001), trade normalization
- **2006-2007:** Pre-financial crisis period

**Estimated Volume:** 1.5 million events
**Collection Time:** 3-4 hours
**Storage:** ~15GB

### Execution Plan

```bash
# Final historical backfill
for year in {2005..2007}; do
    python scripts/collectors/gdelt_bigquery_collector.py --mode year --year $year
done
```

**Value:** Complete 20-year historical record

---

## Critical Historical Periods (Prioritized Sampling)

If you want **targeted intelligence** before full backfill, collect these specific periods first:

### High-Value Periods (Collect First)

**1. Lithuania Taiwan Office Crisis (2021)**
```bash
# Q3-Q4 2021 (crisis period)
python scripts/collectors/gdelt_bigquery_collector.py \
    --mode custom --start-date 20210701 --end-date 20211231
```

**2. Belt & Road Forum (May 2017)**
```bash
# BRI Forum + surrounding months
python scripts/collectors/gdelt_bigquery_collector.py \
    --mode custom --start-date 20170301 --end-date 20170731
```

**3. Trade War Escalation (2018-2019)**
```bash
# 2018 full year
python scripts/collectors/gdelt_bigquery_collector.py --mode year --year 2018

# 2019 full year
python scripts/collectors/gdelt_bigquery_collector.py --mode year --year 2019
```

**4. COVID-19 Initial Period (2020 Q1-Q2)**
```bash
# Early COVID period
python scripts/collectors/gdelt_bigquery_collector.py \
    --mode custom --start-date 20200101 --end-date 20200630
```

---

## Technical Execution Details

### Collection Settings

**BigQuery Optimization:**
```python
# Batch size: 50,000 events per query
# Annual collection: ~40-60 queries per year
# Rate limiting: 1 query per 2 seconds
# Total time: ~2-3 hours per year
```

**Error Handling:**
- Checkpoint system: Resume from last successful batch
- Retry logic: 3 attempts per failed query
- Validation: Check event counts vs expected volume

### Database Management

**Disk Space Monitoring:**
```bash
# Check available space on F: drive
df -h F:/

# Monitor database growth during collection
watch -n 60 'du -h F:/OSINT_WAREHOUSE/osint_master.db'
```

**Incremental Backups:**
```bash
# Backup after each year collected
cp F:/OSINT_WAREHOUSE/osint_master.db \
   F:/OSINT_BACKUPS/osint_master_YYYYMMDD.db
```

---

## Integration with Existing Data

### Cross-Reference Opportunities

After collecting historical GDELT data, cross-reference with:

**1. Lithuania 2021 Crisis Validation**
```sql
-- GDELT sentiment 2020 vs 2021
-- vs OpenAlex research volume 2020 vs 2021
-- Expected: Both show dramatic negative shift in 2021
```

**2. German-China Quantum Collaboration**
```sql
-- GDELT: "quantum cooperation" events 2015-2025
-- vs OpenAlex: German-China quantum papers
-- vs USPTO: Chinese quantum patents citing German research
```

**3. Italian BRI Participation (2019)**
```sql
-- GDELT: Italy-China events March 2019 (Xi visit)
-- vs TED: Italian contracts awarded to Chinese firms 2019-2025
-- vs OpenAlex: Italy-China research 2019-2025
```

---

## Quality Assurance

### Validation After Each Phase

**1. Event Count Validation**
```sql
SELECT
    SUBSTR(event_date, 1, 4) as year,
    COUNT(*) as events,
    MIN(event_date) as first_event,
    MAX(event_date) as last_event
FROM gdelt_events
GROUP BY year
ORDER BY year;
```

**2. Provenance Check**
```sql
SELECT
    COUNT(*) as total_events,
    SUM(CASE WHEN data_source IS NOT NULL THEN 1 ELSE 0 END) as with_provenance,
    ROUND(100.0 * SUM(CASE WHEN data_source IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as provenance_pct
FROM gdelt_events;
```

**3. Geographic Coverage**
```sql
SELECT
    SUBSTR(event_date, 1, 4) as year,
    COUNT(DISTINCT actor2_country_code) as unique_countries
FROM gdelt_events
WHERE actor1_country_code = 'CHN'
GROUP BY year
ORDER BY year;
```

---

## Timeline and Milestones

### Week 1: Phase 1 Critical Period (2020-2025)

**Day 1-2:** Collect 2020-2021 (Lithuania crisis priority)
**Day 3:** Validate Lithuania findings, generate intelligence report
**Day 4-5:** Collect 2022-2023
**Day 6-7:** Collect 2024-2025, validate full Phase 1

**Deliverable:** Lithuania crisis validation report

---

### Week 2: Phase 2 BRI Era (2013-2019)

**Day 8-10:** Collect 2013-2016 (BRI launch)
**Day 11-12:** Collect 2017-2019 (trade war)
**Day 13-14:** Validate BRI impact analysis

**Deliverable:** BRI sentiment analysis report (2013 vs 2019)

---

### Week 3: Phase 3 & 4 Historical Baseline (2005-2012)

**Day 15-17:** Collect 2008-2012
**Day 18-19:** Collect 2005-2007
**Day 20-21:** Final validation, complete historical report

**Deliverable:** 20-year EU-China relations intelligence report

---

## Cost Analysis

### BigQuery Costs

**GDELT is FREE via BigQuery** (within Google Cloud free tier):

- Free tier: 1TB queries/month
- Estimated usage: ~500GB for full 20-year collection
- **Cost: $0**

**Rate Limits:**
- 100 queries/day (BigQuery free tier)
- Our collection: ~40-60 queries/year
- **No rate limit issues expected**

### Time Investment

| Phase | Time | Value/Hour |
|-------|------|------------|
| Phase 1 (2020-2025) | 12-15h | Lithuania validation + recent context |
| Phase 2 (2013-2019) | 10-12h | BRI impact quantification |
| Phase 3 (2008-2012) | 6-8h | Baseline establishment |
| Phase 4 (2005-2007) | 3-4h | Historical context |
| **TOTAL** | **31-39h** | **Complete 20-year intelligence** |

**Return on Investment:**
- 14 million events × 2KB = 28GB of structured intelligence
- Cost: $0 (free BigQuery tier)
- Time: ~40 hours over 3 weeks
- **Value: Priceless historical validation capability**

---

## Expected Intelligence Products

### After Phase 1 (Week 1):

**1. Lithuania 2021 Crisis Report**
```
INTELLIGENCE ASSESSMENT: Lithuania-China Diplomatic Crisis 2021

FINDINGS:
- GDELT sentiment: +2.5 (2020) → -6.8 (2021) = -9.3 shift
- Event volume: 150 events (2020) → 25 events (2021) = -83% drop
- OpenAlex research: 1,209 works (2020) → 129 works (2021) = -89.3% drop

VALIDATION: Multi-source confirmation of diplomatic crisis
CONFIDENCE: HIGH (3 independent data sources align)
```

**2. COVID-19 Impact on EU-China Relations (2020)**

**3. Decoupling Trend Analysis (2022-2025)**

---

### After Phase 2 (Week 2):

**4. Belt & Road Initiative Impact Assessment (2013-2025)**
```
ANALYSIS: BRI Announcement Impact on EU-China Sentiment

BASELINE (2012): Avg sentiment +0.5
BRI LAUNCH (2013): Avg sentiment +2.8 (+230% increase)
PEAK (2017): Avg sentiment +3.5
TRADE WAR (2019): Avg sentiment -1.2
```

**5. US-China Trade War Spillover to Europe (2018-2020)**

---

### After Phase 3 & 4 (Week 3):

**6. 20-Year EU-China Relations Intelligence Report**
```
COMPREHENSIVE ASSESSMENT: EU-China Relations 2005-2025

ERA 1 (2005-2012): Baseline period, avg sentiment +1.2
ERA 2 (2013-2019): BRI optimism, avg sentiment +2.5
ERA 3 (2020-2021): COVID + Lithuania, avg sentiment -0.8
ERA 4 (2022-2025): Decoupling, avg sentiment -1.5

TREND: 3-point negative shift from peak (2017) to current (2025)
```

**7. Technology Transfer Pattern Analysis (2005-2025)**
- Correlate GDELT cooperation events with OpenAlex research spikes
- Identify which European countries most engaged (technology transfer risk)

---

## Automation and Scheduling

### Scheduled Collection Script

```python
#!/usr/bin/env python3
"""
GDELT Historical Collection - Automated
Collects 20 years of data in phased approach
"""

import subprocess
from datetime import datetime

def collect_year(year):
    print(f"[{datetime.now()}] Collecting {year}...")
    subprocess.run([
        'python',
        'scripts/collectors/gdelt_bigquery_collector.py',
        '--mode', 'year',
        '--year', str(year)
    ])
    print(f"[{datetime.now()}] Completed {year}")

# Phase 1: 2020-2025
print("="*80)
print("PHASE 1: Critical Period (2020-2025)")
print("="*80)
for year in range(2020, 2025):
    collect_year(year)

# Phase 2: 2013-2019
print("="*80)
print("PHASE 2: BRI Era (2013-2019)")
print("="*80)
for year in range(2013, 2020):
    collect_year(year)

# Phase 3: 2008-2012
print("="*80)
print("PHASE 3: Pre-BRI Baseline (2008-2012)")
print("="*80)
for year in range(2008, 2013):
    collect_year(year)

# Phase 4: 2005-2007
print("="*80)
print("PHASE 4: Historical Context (2005-2007)")
print("="*80)
for year in range(2005, 2008):
    collect_year(year)

print("="*80)
print("COLLECTION COMPLETE: 2005-2025 (20 years)")
print("="*80)
```

**Save as:** `scripts/automated/gdelt_20_year_collection.py`

**Run:**
```bash
python scripts/automated/gdelt_20_year_collection.py
```

---

## Risk Mitigation

### Potential Issues and Solutions

**1. BigQuery Quota Exceeded**
- **Issue:** Free tier 1TB/month limit
- **Solution:** Collect 500GB/month (half tier), spread over 2 months
- **Mitigation:** Monitor usage with BigQuery console

**2. Database Lock During Collection**
- **Issue:** Other processes accessing database
- **Solution:** Collect during off-hours, use WAL mode (already enabled)
- **Mitigation:** Test with small year first (2005)

**3. Disk Space Exhaustion**
- **Issue:** F: drive fills up
- **Solution:** Monitor disk usage, compress old backups
- **Mitigation:** Allocate 300GB initially, expand if needed

**4. Collection Interruption**
- **Issue:** Network failure, script crash
- **Solution:** Checkpoint system resumes from last batch
- **Mitigation:** Test collection script on single year first

---

## Success Criteria

### Phase 1 Success Metrics:
✅ 2020-2025 collected (6 years)
✅ Lithuania 2021 crisis validated with GDELT data
✅ Event counts match expected volume (±20%)
✅ 100% provenance compliance
✅ Intelligence report generated

### Phase 2 Success Metrics:
✅ 2013-2019 collected (7 years)
✅ BRI sentiment shift quantified
✅ Trade war impact measured
✅ Cross-referenced with OpenAlex research trends

### Phase 3 & 4 Success Metrics:
✅ 2005-2012 collected (8 years)
✅ Complete 20-year historical record
✅ Baseline established for all EU countries
✅ 20-year intelligence report published

---

## Recommended Execution Order

### Option A: Phased (Recommended)
**Week 1:** Phase 1 (2020-2025) → Validate Lithuania
**Week 2:** Phase 2 (2013-2019) → Validate BRI
**Week 3:** Phase 3+4 (2005-2012) → Complete history

**Advantage:** Early validation, incremental value

### Option B: Targeted Events First
**Day 1:** Lithuania 2021 Q3-Q4 → Immediate validation
**Day 2:** BRI Forum 2017 → High-impact event
**Day 3-7:** Fill in gaps → Complete periods

**Advantage:** Fastest time to key findings

### Option C: Full Automation
**Set and forget:** Run `gdelt_20_year_collection.py`
**Duration:** 40 hours over 2-3 days
**Advantage:** No manual intervention

**Recommended:** Option A (Phased) for controlled validation

---

## Next Actions

### Immediate (This Week):
1. ✅ Review this strategy document
2. ⏳ Decide: Phase 1 only, or full 20-year collection?
3. ⏳ Run Lithuania 2021 Q3-Q4 sample (2 hours)
4. ⏳ Validate against OpenAlex findings

### Week 1:
5. Collect Phase 1 (2020-2025)
6. Generate Lithuania crisis report
7. Cross-reference with OpenAlex data

### Week 2-3:
8. Collect Phase 2-4 (2005-2019)
9. Generate 20-year intelligence report
10. Publish findings

---

## Summary

**GDELT 20-year collection will transform your project from "current snapshot" to "historical intelligence platform".**

You'll be able to:
- ✅ Validate existing findings (Lithuania -89.3% drop)
- ✅ Detect long-term trends (BRI impact, decoupling)
- ✅ Establish baselines (what's "normal" EU-China relations?)
- ✅ Quantify policy impacts (sanctions, trade wars, diplomatic incidents)
- ✅ Cross-reference with 20 years of OpenAlex, TED, USPTO data

**Total Investment:** 31-39 hours over 2-3 weeks
**Total Cost:** $0 (free BigQuery tier)
**Total Value:** Priceless historical context for all your intelligence production

---

**Document Status:** Production Ready
**Recommended Start:** Phase 1 (2020-2025) this week
**Next Review:** After Phase 1 completion

**Created:** 2025-11-01
**Author:** GDELT Strategic Collection Plan
**Version:** 1.0
