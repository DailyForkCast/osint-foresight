# UN Comtrade Automated Collection System
**Complete Guide to Automated Trade Data Collection**

## Overview

This automated system collects strategic technology trade data from the UN Comtrade API using the free tier (100 requests/hour, 10,000/day). The system implements the 3-phase collection strategy with:

- **Automatic rate limiting** (respects free tier limits)
- **Checkpoint/resume** (can pause and resume at any time)
- **Error handling** (automatic retries, handles API errors)
- **Progress tracking** (detailed logging and status reporting)
- **Database storage** (SQLite with deduplication)

**Total collection time:** 16-24 hours over 3 months
**Total cost:** $0 (free tier only)
**Expected data:** 500K-2.5M trade records

---

## Quick Start

### 1. Test API Access (5 minutes)

Before starting collection, verify API access:

```bash
cd C:/Projects/OSINT-Foresight/scripts
python comtrade_test_api.py
```

This will run 5 test requests and confirm the API is working.

### 2. Start Phase 1 Collection (6-8 hours)

Once testing succeeds, start Phase 1:

```bash
python comtrade_run_phase.py 1
```

This will collect **core technology trade data** (semiconductors, telecom, computing).

### 3. Monitor Progress

In another terminal, check status anytime:

```bash
python comtrade_status.py
```

Shows:
- Current phase and progress
- Records collected
- Estimated time remaining
- Top commodities and country pairs

### 4. Resume if Interrupted

If collection stops (computer restart, etc.), simply resume:

```bash
python comtrade_run_phase.py resume
```

The system remembers where it left off and continues.

---

## Files Created

### Core Scripts

**`comtrade_collector_automated.py`**
- Main collection engine
- Handles rate limiting, checkpointing, database storage
- ~600 lines, fully documented
- Location: `C:/Projects/OSINT-Foresight/scripts/`

**`comtrade_run_phase.py`**
- Simple runner to start specific phases
- Usage: `python comtrade_run_phase.py [1|2|3a|3b|all|resume]`

**`comtrade_status.py`**
- Status checker and progress monitor
- Shows database stats, phase progress, time estimates

**`comtrade_test_api.py`**
- API test script (run before starting collection)
- Tests 5 sample requests to verify API access

### Reference Documents

**`UN_COMTRADE_COLLECTION_PHASES.md`**
- Complete 3-phase plan reference
- All HS codes, country pairs, years
- Progress tracking checklists
- Database schema

**`UN_COMTRADE_FREE_TIER_STRATEGY.md`** (analysis directory)
- Detailed strategy document
- Rate limit analysis
- Prioritization methodology
- Full Python implementation

---

## Phase Details

### Phase 1: Core Technologies (This Month)
**Duration:** 6-8 hours
**HS Codes:** 20 (semiconductors, telecom, computing, materials)
**Years:** 2023, 2024, 2025
**Country Pairs:** 10 (20 directional flows)
**Requests:** 1,200
**Expected:** 60K-300K records

**To run:**
```bash
python comtrade_run_phase.py 1
```

### Phase 2: Strategic Expansion (Next Month)
**Duration:** 4-6 hours
**HS Codes:** 15 (aerospace, batteries, manufacturing, biotech)
**Years:** 2023, 2024, 2025
**Country Pairs:** 16 (32 flows, adds France, Italy, Taiwan)
**Requests:** 1,440
**Expected:** 70K-350K records

**To run:**
```bash
python comtrade_run_phase.py 2
```

### Phase 3A: Remaining Codes (Quarter 3)
**Duration:** 3-4 hours
**HS Codes:** 15 (robotics, chemicals, optics)
**Years:** 2023, 2024, 2025
**Country Pairs:** 28 (56 flows, adds UK, Spain, Poland, etc.)
**Requests:** 2,520
**Expected:** 100K-500K records

**To run:**
```bash
python comtrade_run_phase.py 3a
```

### Phase 3B: Historical Data (Quarter 3)
**Duration:** 6-10 hours
**HS Codes:** All 50 codes
**Years:** 2018, 2020, 2022 (historical)
**Country Pairs:** 28 (56 flows)
**Requests:** 8,400
**Expected:** 400K-2M records

**To run:**
```bash
python comtrade_run_phase.py 3b
```

---

## Usage Examples

### Run All Phases Automatically
```bash
python comtrade_run_phase.py all
```
This will run all phases in sequence. Takes 16-24 hours total, but spreads over multiple days due to rate limits.

### Resume from Checkpoint
```bash
python comtrade_run_phase.py resume
```
Picks up where you left off. Safe to interrupt at any time.

### Check Status While Running
```bash
# In another terminal
python comtrade_status.py
```

### Run in Background (Windows)
```bash
# Start in background
start /B python comtrade_run_phase.py 1 > comtrade.log 2>&1

# Check log
tail -f comtrade.log
```

### Run in Background (Linux/Mac)
```bash
# Start in background
nohup python comtrade_run_phase.py 1 > comtrade.log 2>&1 &

# Check log
tail -f comtrade.log
```

---

## Database Schema

Collection creates `comtrade_data` table in `F:/OSINT_WAREHOUSE/osint_master.db`:

```sql
CREATE TABLE comtrade_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    reporter_code TEXT NOT NULL,           -- CHN, USA, DEU, etc.
    reporter_name TEXT,
    partner_code TEXT NOT NULL,            -- Trading partner
    partner_name TEXT,
    commodity_code TEXT NOT NULL,          -- 6-digit HS code
    commodity_description TEXT,
    flow_code TEXT,                        -- Import/Export
    flow_description TEXT,
    trade_value_usd REAL,                  -- USD value
    quantity REAL,                         -- Quantity
    quantity_unit TEXT,                    -- kg, units, etc.
    net_weight_kg REAL,                    -- Net weight
    collected_date TEXT NOT NULL,          -- Collection timestamp
    UNIQUE(year, reporter_code, partner_code, commodity_code, flow_code)
);
```

**Indexes created automatically:**
- `idx_comtrade_year` - Query by year
- `idx_comtrade_reporter` - Query by reporter
- `idx_comtrade_partner` - Query by partner
- `idx_comtrade_commodity` - Query by HS code
- `idx_comtrade_year_commodity` - Combined year + HS code

---

## Sample Queries

### China's semiconductor imports from Netherlands
```sql
SELECT
    year,
    commodity_code,
    commodity_description,
    SUM(trade_value_usd) as total_value_usd,
    SUM(quantity) as total_quantity
FROM comtrade_data
WHERE reporter_code = 'CN'
AND partner_code = 'NL'
AND commodity_code LIKE '8542%'  -- Semiconductors
GROUP BY year, commodity_code
ORDER BY year DESC, total_value_usd DESC;
```

### US-China trade in 5G equipment over time
```sql
SELECT
    year,
    reporter_code,
    partner_code,
    SUM(trade_value_usd) as total_value
FROM comtrade_data
WHERE (
    (reporter_code = 'CN' AND partner_code = 'US')
    OR (reporter_code = 'US' AND partner_code = 'CN')
)
AND commodity_code = '851762'  -- 5G equipment
GROUP BY year, reporter_code, partner_code
ORDER BY year DESC;
```

### Top 10 technology commodities by trade value
```sql
SELECT
    commodity_code,
    commodity_description,
    COUNT(*) as record_count,
    SUM(trade_value_usd) as total_value
FROM comtrade_data
WHERE year >= 2023
GROUP BY commodity_code
ORDER BY total_value DESC
LIMIT 10;
```

---

## Rate Limiting Details

**Free Tier Limits:**
- 100 requests per hour
- 10,000 requests per day
- Resets at midnight UTC

**System Behavior:**
- Uses 90 requests/hour (leaves 10 request buffer)
- 2-second polite delay between requests
- Automatic waiting when approaching limits
- Tracks hourly and daily counters
- Handles 429 (rate limited) responses

**Time Estimates:**
- 90 requests/hour = effective rate
- 1,200 requests (Phase 1) ÷ 90 = ~13.3 hours
- System spreads requests over multiple hours/days

---

## Checkpoint System

**Location:** `C:/Projects/OSINT-Foresight/data/comtrade_checkpoint.json`

**Contents:**
```json
{
  "current_phase": 1,
  "completed_requests": [
    "CN|US|854231|2024",
    "US|CN|854231|2024",
    ...
  ],
  "last_updated": "2025-11-01T10:30:00"
}
```

**Features:**
- Saves progress every 10 requests
- Prevents duplicate API calls
- Enables safe interruption/resumption
- Tracks completed request IDs

**To reset (start over):**
```bash
rm C:/Projects/OSINT-Foresight/data/comtrade_checkpoint.json
```

---

## Logging

**Location:** `C:/Projects/OSINT-Foresight/logs/comtrade_collection.log`

**Log Format:**
```
2025-11-01 10:30:15 - INFO - Requesting: CN -> US, HS 854231, 2024
2025-11-01 10:30:17 - INFO -   Stored 45 records
2025-11-01 10:30:22 - INFO - Phase 1 Progress: 50/1200 (4.2%)
2025-11-01 10:30:22 - INFO -   Records collected: 2,345
```

**Log includes:**
- Each request made (reporter, partner, HS code, year)
- Records stored per request
- Progress updates every 50 requests
- Error messages with retry attempts
- Rate limit warnings
- Phase completion summaries

---

## Error Handling

### Network Errors
- **Timeout (30s):** Automatic retry up to 3 times with exponential backoff
- **Connection errors:** Retry with 10-second delay

### API Errors
- **HTTP 429 (Rate Limited):** Wait 60 seconds, retry
- **HTTP 404 (No Data):** Log and skip (not an error)
- **HTTP 500 (Server Error):** Retry up to 3 times

### Database Errors
- **Lock errors:** Wait and retry
- **Duplicate records:** Silently ignored (UNIQUE constraint)

### Interruption Handling
- **Ctrl+C:** Saves checkpoint, graceful shutdown
- **Power loss:** Checkpoint saved every 10 requests
- **Resume:** Skips already-collected data

---

## Troubleshooting

### "Database is locked"
The database is in WAL mode, but if you see lock errors:
```bash
# Check for other processes using database
lsof F:/OSINT_WAREHOUSE/osint_master.db  # Linux/Mac
handle F:/OSINT_WAREHOUSE/osint_master.db  # Windows
```

### "Rate limited (429)"
You've exceeded free tier limits. System will wait automatically, or:
```bash
# Check checkpoint to see when you can resume
python comtrade_status.py
```

### "Connection timeout"
Check internet connection, try again:
```bash
python comtrade_test_api.py
```

### Progress seems slow
This is normal! Free tier limits mean:
- 90 requests per hour maximum
- Phase 1 (1,200 requests) takes ~13 hours
- System spreads collection over days to respect limits

### Checkpoint corrupted
Reset and restart:
```bash
rm C:/Projects/OSINT-Foresight/data/comtrade_checkpoint.json
python comtrade_run_phase.py resume
```

---

## Best Practices

### 1. Test First
Always run `comtrade_test_api.py` before starting a long collection.

### 2. Monitor Progress
Run `comtrade_status.py` periodically to check progress.

### 3. Run in Background
For long phases, run in background and monitor log file.

### 4. Spread Over Time
Don't rush. System is designed to run over weeks:
- Phase 1: Week 1-2
- Phase 2: Week 3-4
- Phase 3: Month 2-3

### 5. Verify Data
After each phase, check database:
```bash
python comtrade_status.py
```

### 6. Backup Database
Before starting new phase:
```bash
cp F:/OSINT_WAREHOUSE/osint_master.db F:/OSINT_WAREHOUSE/osint_master_backup_$(date +%Y%m%d).db
```

---

## Advanced Usage

### Collect Specific Subset
Edit `comtrade_collector_automated.py` to define custom HS codes/country pairs:

```python
CUSTOM_HS_CODES = ['854231', '854232']  # Just processors and memory
CUSTOM_PAIRS = [('CN', 'US'), ('US', 'CN')]  # Just US-China
CUSTOM_YEARS = [2024, 2025]  # Just recent years

# Then run custom collection
collector = ComtradeCollector()
collector._connect_db()
for hs_code in CUSTOM_HS_CODES:
    for year in CUSTOM_YEARS:
        for reporter, partner in CUSTOM_PAIRS:
            collector.collect_request(reporter, partner, hs_code, year)
```

### Parallel Collection (Advanced)
To speed up collection, run multiple phases in parallel:

```bash
# Terminal 1: Phase 1
python comtrade_run_phase.py 1

# Terminal 2: Phase 2 (different HS codes, no conflicts)
python comtrade_run_phase.py 2
```

**WARNING:** This will hit rate limits faster. Only use if you have premium access or understand the risks.

---

## Expected Results

### Phase 1 Complete
- 60K-300K trade records
- Semiconductors, telecom, computing data
- China bilateral trade with 10 major partners
- Can answer: "Is China increasing chip imports from Netherlands?"

### Phase 2 Complete
- 130K+ total records
- Adds aerospace, batteries, manufacturing
- Expanded to 16 country pairs
- Can track Chinese EV battery supply chain

### Phase 3 Complete
- 500K-2.5M total records
- Complete 50-code technology database
- 6-year trend analysis (2018-2025)
- Pre/post trade war comparison
- COVID impact quantified

---

## Support and Documentation

**Reference Documents:**
- `UN_COMTRADE_COLLECTION_PHASES.md` - Phase plan details
- `UN_COMTRADE_FREE_TIER_STRATEGY.md` - Strategy analysis
- `COMTRADE_AUTOMATION_GUIDE.md` - This file

**UN Comtrade Documentation:**
- API Docs: https://comtradeapi.un.org/
- FAQ: https://unstats.un.org/wiki/display/comtrade/New+Comtrade+FAQ

**HS Code Reference:**
- https://www.trade.gov/harmonized-system-hs-codes
- https://www.foreign-trade.com/reference/hscode.htm

**Country Codes (ISO 3166-1 alpha-3):**
- CHN = China, USA = United States, DEU = Germany
- JPN = Japan, KOR = South Korea, NLD = Netherlands
- Full list in `UN_COMTRADE_COLLECTION_PHASES.md`

---

## System Status

**Status:** READY FOR DEPLOYMENT
**Next Action:** Run `python comtrade_test_api.py` to verify API access
**First Collection:** Phase 1 (6-8 hours, this month)
**Completion Target:** January 2026 (all phases complete)

---

**Document Version:** 1.0
**Date:** 2025-11-01
**Author:** Claude Code (Automated System)
