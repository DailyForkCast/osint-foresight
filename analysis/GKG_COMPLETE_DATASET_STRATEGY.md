# GKG Complete Dataset Collection Strategy

**Date**: November 5, 2025
**Status**: 3-day pilot COMPLETE, ready to expand

---

## Pilot Collection Results (3 Peak Days)

### ✅ COMPLETED SUCCESSFULLY

**Dates Collected:**
1. Feb 3, 2020: 60,709 China records
2. Jan 31, 2020: 66,135 China records
3. Sept 2, 2025: 41,456 China records

**Totals:**
- **168,300 China-related GKG records**
- 287 files processed (96 files × 3 days, 1 error)
- 1.3 GB downloaded (temporary, deleted after filtering)
- ~550 MB added to database (permanent)
- **Cost: $0.00**
- **Time: ~15 minutes total**

**Performance Metrics:**
- 32.7% filter efficiency (168K of 515K total records)
- ~56,000 China records per day average
- ~3-5 minutes per day collection time
- ~180 MB database growth per day

**Error Rate:** 0.3% (1 file had oversized field, skipped)

---

## Complete Dataset Options

### Your Existing Events Coverage

From your osint_master.db:
- **2,115 unique days** with China events (Jan 5, 2020 → Nov 5, 2025)
- **8.47M total GDELT events** collected
- 99.2% calendar coverage over 2,132 days

### Option 1: All High-Value Days (Top 100)

**What:** Collect GKG for 100 days with highest China event counts

**Coverage:** Top 100 peak activity days across 2020-2025

**Benefits:**
- Captures major events, crises, policy announcements
- Concentrated intelligence from high-activity periods
- Manageable size

**Metrics:**
- Records: ~5.6M China-related GKG records
- Storage: ~18 GB database growth
- Time: ~5 hours (unattended, can run overnight)
- Cost: **$0.00**

**Dates:** See `analysis/gkg_targeted_collection_strategy.json` (already identified)

---

### Option 2: Monthly Strategic Sampling (140 days)

**What:** 2 days per month (highest activity days) across entire period

**Coverage:** Representative sample from every month (Jan 2020 → Nov 2025)

**Benefits:**
- Longitudinal view of China coverage trends
- Identifies policy shifts and narrative changes
- Good for time-series analysis

**Metrics:**
- Records: ~7.8M China-related GKG records
- Storage: ~26 GB database growth
- Time: ~7 hours
- Cost: **$0.00**

---

### Option 3: Recent Year (365 days)

**What:** Complete GKG for last 365 days (Nov 2024 → Nov 2025)

**Coverage:** All days in most recent year

**Benefits:**
- Current intelligence, most relevant
- Complete temporal coverage for recent period
- Best for current analysis needs

**Metrics:**
- Records: ~20M China-related GKG records
- Storage: ~66 GB database growth
- Time: ~18-20 hours (run overnight)
- Cost: **$0.00**

---

### Option 4: Complete Dataset (2,115 days)

**What:** GKG for ALL days with China events

**Coverage:** Full backfill (Jan 2020 → Nov 2025)

**Benefits:**
- Complete historical intelligence
- No gaps in coverage
- Maximum analytical value

**Metrics:**
- Records: ~118M China-related GKG records
- Storage: ~390 GB database growth
- Time: ~106 hours (~4.5 days continuous)
- Cost: **$0.00**

**Considerations:**
- Long runtime (recommend breaking into chunks)
- Significant storage (but you have 5.2 TB available)
- Historical data value depends on research questions

---

## Recommended Approach

### Phase 1: Top 100 Days (RECOMMENDED START)

**Rationale:**
- Builds on successful 3-day pilot
- Captures highest-value intelligence
- Quick to complete (~5 hours)
- Validates approach at scale

**Command:**
```bash
# Get top 100 date list from analysis file
python scripts/collectors/gdelt_gkg_free_collector.py \
  --dates $(cat analysis/top_100_dates.txt)
```

**Expected Outcome:**
- 5.6M China-related GKG records
- Keyword search on major events/crises
- Foundation for expansion decision

---

### Phase 2: Expand Based on Value

After Phase 1, assess:

**If GKG highly valuable:**
- Proceed to Option 3 (Recent year) or Option 4 (Complete)

**If GKG moderately valuable:**
- Expand to Option 2 (Monthly sampling)

**If GKG low value:**
- Stop at Phase 1 (Top 100 days)

---

## Automation Options

### Option A: Run Complete Collection Overnight

Set up unattended collection:

```bash
# Schedule complete dataset collection
nohup python scripts/collectors/gdelt_gkg_free_collector.py \
  --dates $(python get_all_event_dates.py) \
  > logs/gkg_full_collection.log 2>&1 &
```

**Time:** 4.5 days continuous (or break into chunks)

### Option B: Incremental Daily Collection

Collect GKG for new days as events are collected:

```bash
# Add to daily cron/scheduled task
python scripts/collectors/gdelt_gkg_free_collector.py \
  --dates $(date +%Y%m%d)
```

**Time:** ~3-5 minutes per day
**Benefit:** Always current, no backfill needed

### Option C: Parallel Collection

Run multiple collectors for different date ranges:

```bash
# Terminal 1: 2020 data
python scripts/collectors/gdelt_gkg_free_collector.py --dates $(get_dates_2020.py)

# Terminal 2: 2021 data
python scripts/collectors/gdelt_gkg_free_collector.py --dates $(get_dates_2021.py)

# Terminal 3: 2022 data
# etc.
```

**Time:** Reduces wall-clock time by ~5x
**Benefit:** Complete dataset in ~1 day instead of 4.5

---

## Storage Planning

**Current Database:** 37.6 GB

**Growth Estimates:**

| Option | New Records | Storage Growth | Final DB Size |
|--------|-------------|----------------|---------------|
| Top 100 days | 5.6M | 18 GB | 55.6 GB |
| Monthly sample | 7.8M | 26 GB | 63.6 GB |
| Recent year | 20M | 66 GB | 103.6 GB |
| Complete | 118M | 390 GB | 427.6 GB |

**Available Space:** 5.2 TB (5,222 GB)

**Conclusion:** Storage is NOT a constraint for any option

---

## Cost Comparison

**Free Download (Current Approach):**
- Cost per day: $0.00
- Total cost for complete dataset: **$0.00**
- Labor: Automated, minimal oversight needed

**BigQuery (Alternative):**
- Cost per day: $8.86
- Top 100 days: $886.00
- Complete dataset: $18,731.48

**Savings:** $18,731.48 by using free download approach

---

## Next Steps

**Immediate Decision Needed:**

Which option do you want to proceed with?

1. **Top 100 days** (~5 hours, 5.6M records) - RECOMMENDED
2. **Monthly sampling** (~7 hours, 7.8M records)
3. **Recent year** (~20 hours, 20M records)
4. **Complete dataset** (~4.5 days, 118M records)

**To Execute Option 1 (Top 100):**

```bash
# I'll create the script to run this
cd "C:/Projects/OSINT-Foresight"
python collect_top_100_gkg.py
```

---

## What This Enables

Once collected, you'll be able to search GKG by:

**Themes:**
- "quantum research"
- "semiconductor supply chain"
- "university partnerships"
- "military technology"
- "5G infrastructure"
- "artificial intelligence"
- "rare earth minerals"

**Organizations:**
- Specific universities (e.g., "Tsinghua University")
- Companies (e.g., "Huawei", "SMIC", "CATL")
- Government entities
- Research institutions

**Cross-Reference:**
- Link GKG themes to specific GDELT events
- Track narrative shifts over time
- Identify coordinated coverage patterns
- Analyze sentiment on specific topics

**Example Query:**
```sql
SELECT DISTINCT
    g.themes,
    g.organizations,
    g.tone,
    e.event_date,
    e.actor1_name,
    e.actor2_name
FROM gdelt_gkg g
JOIN gdelt_events e ON DATE(g.publish_date/1000000) = DATE(e.event_date/1000000)
WHERE g.themes LIKE '%QUANTUM%'
AND g.organizations LIKE '%UNIVERSITY%'
AND e.actor1_country_code = 'CHN'
ORDER BY e.event_date DESC;
```

---

**AWAITING YOUR DECISION** on collection scope.
