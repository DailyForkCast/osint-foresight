# GDELT GKG Collection - Zero-Cost Alternative

**Problem**: BigQuery costs $8.86/day even with targeted filtering
**Solution**: Use GDELT's free public data files instead

---

## Option 1: Free Direct Download (RECOMMENDED)

GDELT publishes GKG files for free every 15 minutes:
- **URL**: http://data.gdeltproject.org/gdeltv2/masterfilelist.txt
- **Format**: Tab-separated files, ~5-10 MB per 15-minute snapshot
- **Coverage**: Same data as BigQuery, but requires download + processing

### Cost Comparison

| Approach | 10 Days | 30 Days | 365 Days |
|----------|---------|---------|----------|
| BigQuery | $88.60 | $260.77 | $3,228.48 |
| Free Download | **$0** | **$0** | **$0** |

### Trade-offs

**Pros**:
- Zero cost (bandwidth is negligible)
- Same data as BigQuery
- Full control over filtering
- Can process incrementally

**Cons**:
- More labor-intensive (manual download + processing)
- Slower (download + parse vs instant query)
- Requires storage space (~500 GB for full archive)
- Need to write parser for GKG format

### Effort Estimate
- **Script development**: 2-3 hours (one-time)
- **Processing time**: ~1 hour per 10 days of data
- **Storage needed**: ~50 GB per year of GKG data

---

## Option 2: Hybrid Approach (BEST VALUE)

Use BigQuery for **strategic sampling only**:

### Ultra-Targeted Strategy
Collect GKG for only 3-5 **critical dates**:

1. **Major policy announcements**
   - 14th Five-Year Plan release
   - Technology export control changes
   - Belt & Road forum dates

2. **Crisis events**
   - COVID outbreak (Jan 31, Feb 3, 2020)
   - Taiwan strait tensions
   - Semiconductor sanctions

3. **Recent high-value**
   - Sept 1-2, 2025 (peak activity in our data)
   - Oct 30, 2025 (recent peak)

**Cost**: 3 days × $8.86 = **$26.58**

**Coverage**: ~40,000 China events on peak activity days

**Value**: Tests GKG data quality at minimal cost before committing to free download approach

---

## Option 3: On-Demand Collection

Instead of bulk collection, collect GKG **only when needed** for specific queries:

**Scenario**: User asks "show me quantum research partnerships in 2024"

**Action**:
1. Query events table to find relevant dates (free, local)
2. Collect GKG for only those specific dates (~$9-18)
3. Answer query with enriched data

**Annual cost**: ~$50-100 (sporadic use vs $3,228 for full year)

---

## Recommended Approach

### Phase 1: Proof of Concept ($26.58)
Collect GKG for 3 highest-value days using BigQuery:
- Sept 2, 2025
- Jan 31, 2020
- Feb 3, 2020

**Validates**:
- Data quality and usefulness
- Search capabilities
- Integration with existing events

### Phase 2: If Valuable, Go Free
Build free download processor:
- Parse GDELT GKG files directly
- Filter for China-related content during processing
- Incremental daily updates (new data arrives every 15 min)

**Investment**: 2-3 hours development time
**Ongoing cost**: $0

### Phase 3: Production Mode
- Daily automated collection from free GDELT files
- China-filter applied during ingest
- Same data, zero cost

---

## Technical Details - Free Download

### GKG File Format
```
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.gkg.csv.zip

Example:
http://data.gdeltproject.org/gdeltv2/20251105120000.gkg.csv.zip
```

### Processing Pipeline
1. Download daily GKG files (96 files/day, ~500 MB total)
2. Unzip and filter for China keywords
3. Parse into SQLite (same schema as BigQuery approach)
4. Discard raw files after processing

### Storage Requirements
- **Raw files**: 180 GB/year (can delete after processing)
- **Filtered SQLite**: ~5 GB/year (China-only records)
- **Working space**: 50 GB temporary

---

## Immediate Action

### Recommended: 3-Day Test ($26.58)

```bash
python scripts/collectors/gdelt_gkg_collector.py \
  --dates 20250902,20200131,20200203
```

This collects GKG for the 3 peak activity days to:
- Validate data quality
- Test keyword search capabilities
- Determine if GKG worth the effort

**If useful** → Build free download processor
**If not useful** → Stop here, use events-only search

---

## Cost Savings Summary

| Strategy | Cost | vs Original | Savings |
|----------|------|-------------|---------|
| Original (30 days) | $260.77 | - | - |
| Top 10 days | $88.60 | $260.77 | 66% |
| Top 5 days | $44.30 | $260.77 | 83% |
| **Top 3 days** | **$26.58** | $260.77 | **90%** |
| Free download | $0 | $260.77 | 100% |

---

## Next Steps

**AWAITING APPROVAL** for one of:

1. **$26.58**: 3-day test (RECOMMENDED)
2. **$44.30**: 5-day test
3. **$0**: Build free download processor (3 hours development)
4. **$0**: Skip GKG, use events-only search

Which would you prefer?
