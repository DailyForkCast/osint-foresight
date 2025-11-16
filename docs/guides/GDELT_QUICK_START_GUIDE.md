# GDELT Quick Start Guide
**Created:** 2025-11-01
**Status:** Ready for Use
**Estimated Time:** 30 minutes for initial test, 4-6 hours for full implementation

---

## 🚀 Quick Start (5 Minutes)

### **Test Collection - Last 7 Days**

```bash
# Collect last week of China-related events
python scripts/collectors/gdelt_bigquery_collector.py --mode recent_week
```

**What this does:**
- Queries GDELT BigQuery for last 7 days of China-related events
- Creates 3 database tables: `gdelt_events`, `gdelt_mentions`, `gdelt_gkg`
- Inserts events into `F:/OSINT_WAREHOUSE/osint_master.db`
- Generates report in `analysis/gdelt_collection_report_YYYYMMDD_HHMMSS.json`

**Expected output:**
```
INFO - Connecting to master database: F:\OSINT_WAREHOUSE\osint_master.db
INFO - Creating GDELT tables...
INFO - BigQuery client initialized successfully
INFO - Collecting recent week: 20251025 to 20251101
INFO - Querying BigQuery for events: 20251025 to 20251101
INFO - Retrieved 1,234 events from BigQuery
INFO - Inserted 1,234 events into database
INFO - Collection complete. Events collected: 1,234
```

---

## 📊 Collection Modes

### **1. Recent Week (Recommended for testing)**
```bash
python scripts/collectors/gdelt_bigquery_collector.py --mode recent_week
```
- Collects last 7 days
- ~500-2,000 events expected
- Takes ~2-3 minutes

### **2. Recent Month**
```bash
python scripts/collectors/gdelt_bigquery_collector.py --mode recent_month
```
- Collects last 30 days
- ~2,000-10,000 events expected
- Takes ~5-10 minutes

### **3. Full Year**
```bash
python scripts/collectors/gdelt_bigquery_collector.py --mode year --year 2024
```
- Collects entire year of data
- ~50,000-200,000 events expected
- Takes ~30-60 minutes
- **WARNING:** May hit BigQuery free tier limit (1TB/month)

### **4. Custom Date Range**
```bash
# Collect specific date range
python scripts/collectors/gdelt_bigquery_collector.py \
    --mode custom \
    --start-date 20240101 \
    --end-date 20241231
```

---

## 🔧 Setup Requirements

### **Option A: Use Application Default Credentials (Easiest)**

1. **Install Google Cloud SDK** (if not installed):
   ```bash
   # Already installed at: C:\Users\mrear\AppData\Local\Google\Cloud SDK\

   # Set default project
   gcloud config set project osint-foresight-2025

   # Authenticate
   gcloud auth application-default login
   ```

2. **Verify access to GDELT**:
   ```bash
   # Test BigQuery access
   bq query --nouse_legacy_sql \
     'SELECT COUNT(*) as total FROM `gdelt-bq.gdeltv2.events` WHERE SQLDATE = 20251101 LIMIT 1'
   ```

3. **Run collector** (no credentials file needed):
   ```bash
   python scripts/collectors/gdelt_bigquery_collector.py --mode recent_week
   ```

---

### **Option B: Use Service Account (More Secure)**

1. **Create service account** (one-time setup):
   ```bash
   # Create service account
   gcloud iam service-accounts create gdelt-collector \
       --description="GDELT data collection" \
       --display-name="GDELT Collector"

   # Grant BigQuery user role
   gcloud projects add-iam-policy-binding osint-foresight-2025 \
       --member="serviceAccount:gdelt-collector@osint-foresight-2025.iam.gserviceaccount.com" \
       --role="roles/bigquery.user"

   # Create key file
   gcloud iam service-accounts keys create gdelt-credentials.json \
       --iam-account=gdelt-collector@osint-foresight-2025.iam.gserviceaccount.com
   ```

2. **Run with credentials**:
   ```bash
   python scripts/collectors/gdelt_bigquery_collector.py \
       --mode recent_week \
       --credentials gdelt-credentials.json
   ```

---

## 📊 Database Schema

### **Table: gdelt_events**
```sql
-- Core event data (who did what to whom)
SELECT
    event_date,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    event_code,
    goldstein_scale,  -- -10 (very negative) to +10 (very positive)
    avg_tone,         -- Document tone
    num_mentions,     -- Media coverage intensity
    source_url
FROM gdelt_events
WHERE actor1_country_code = 'CHN'
   OR actor2_country_code = 'CHN'
ORDER BY event_date DESC
LIMIT 10;
```

### **Table: gdelt_mentions**
```sql
-- Media coverage frequency
SELECT
    event_date,
    mention_source_name,
    COUNT(*) as mention_count
FROM gdelt_mentions m
JOIN gdelt_events e ON m.globaleventid = e.globaleventid
WHERE e.actor1_country_code = 'CHN'
GROUP BY event_date, mention_source_name
ORDER BY mention_count DESC;
```

### **Table: gdelt_gkg**
```sql
-- Global Knowledge Graph (themes, sentiment)
-- NOTE: Not yet implemented in v1, coming in future version
```

---

## 🔍 Example Queries

### **1. China-US Events by Type**
```sql
SELECT
    event_code,
    COUNT(*) as event_count,
    AVG(goldstein_scale) as avg_impact,
    AVG(avg_tone) as avg_tone,
    AVG(num_mentions) as avg_coverage
FROM gdelt_events
WHERE (actor1_country_code = 'CHN' AND actor2_country_code = 'USA')
   OR (actor1_country_code = 'USA' AND actor2_country_code = 'CHN')
  AND sqldate >= 20240101
GROUP BY event_code
ORDER BY event_count DESC
LIMIT 20;
```

### **2. Technology Partnerships (Positive Events)**
```sql
SELECT
    event_date,
    actor1_name,
    actor2_name,
    event_code,
    goldstein_scale,
    num_mentions,
    source_url
FROM gdelt_events
WHERE actor1_country_code = 'CHN'
  AND goldstein_scale > 5.0  -- Positive events
  AND event_code IN ('042', '043', '045')  -- Cooperation codes
  AND sqldate >= 20240101
ORDER BY goldstein_scale DESC, num_mentions DESC
LIMIT 50;
```

### **3. Regulatory Actions (Negative Events)**
```sql
SELECT
    event_date,
    actor1_name,
    actor2_name,
    event_code,
    goldstein_scale,
    avg_tone,
    num_mentions,
    source_url
FROM gdelt_events
WHERE actor1_country_code = 'CHN'
  AND goldstein_scale < -5.0  -- Negative events
  AND event_code LIKE '1%'  -- Coercive actions
  AND sqldate >= 20240101
ORDER BY goldstein_scale ASC, num_mentions DESC
LIMIT 50;
```

### **4. Media Coverage Intensity**
```sql
SELECT
    event_date,
    actor1_name,
    actor2_name,
    num_mentions,
    num_sources,
    num_articles,
    avg_tone,
    source_url
FROM gdelt_events
WHERE actor1_country_code = 'CHN'
  AND num_mentions > 100  -- High coverage events
  AND sqldate >= 20240101
ORDER BY num_mentions DESC
LIMIT 20;
```

---

## 📈 Understanding GDELT Data

### **Event Codes** (CAMEO Taxonomy)
- `01-05`: Make statement (verbal cooperation)
- `06-09`: Appeal, express intent
- `10-13`: Demand, disapprove
- `14-17`: Protest, threaten
- `18-20`: Use force

### **Goldstein Scale**
- **+10.0:** Very positive (peace treaty, major agreement)
- **+5.0:** Positive (cooperation, aid)
- **0.0:** Neutral
- **-5.0:** Negative (criticism, sanctions)
- **-10.0:** Very negative (military attack, war)

### **Tone**
- Calculated from all words in article
- Range: -100 (very negative) to +100 (very positive)
- Typical range: -10 to +10

### **Coverage Metrics**
- **num_mentions:** How many times event mentioned
- **num_sources:** How many unique sources
- **num_articles:** How many distinct articles

---

## 🎯 Recommended Collection Strategy

### **Phase 1: Recent Data (Week 1)**
```bash
# Collect last month for baseline
python scripts/collectors/gdelt_bigquery_collector.py --mode recent_month
```
- **Time:** ~10 minutes
- **Records:** ~5,000-10,000 events
- **Purpose:** Establish current baseline

### **Phase 2: Historical Backfill (Week 2-3)**
```bash
# Collect 2024 data
python scripts/collectors/gdelt_bigquery_collector.py --mode year --year 2024

# Collect 2023 data
python scripts/collectors/gdelt_bigquery_collector.py --mode year --year 2023
```
- **Time:** ~1-2 hours total
- **Records:** ~200,000-500,000 events
- **Purpose:** Historical trend analysis

### **Phase 3: Key Historical Years (Week 4)**
```bash
# Trade war start
python scripts/collectors/gdelt_bigquery_collector.py \
    --mode custom --start-date 20180101 --end-date 20181231

# COVID year
python scripts/collectors/gdelt_bigquery_collector.py \
    --mode custom --start-date 20200101 --end-date 20201231

# Belt and Road launch
python scripts/collectors/gdelt_bigquery_collector.py \
    --mode custom --start-date 20130101 --end-date 20131231
```

### **Phase 4: Automated Updates (Ongoing)**
```bash
# Set up weekly cron job
# Run every Monday at 9 AM to collect previous week
0 9 * * 1 cd /c/Projects/OSINT-Foresight && python scripts/collectors/gdelt_bigquery_collector.py --mode recent_week
```

---

## 💰 BigQuery Costs

### **Free Tier:**
- **1 TB of queries per month** - FREE
- First 10 GB storage per month - FREE

### **Typical Usage:**
| Collection | Query Size | Records | Cost |
|------------|-----------|---------|------|
| 1 week | ~1 MB | 500-2,000 | FREE |
| 1 month | ~5 MB | 2K-10K | FREE |
| 1 year | ~100 MB | 50K-200K | FREE |
| 10 years | ~1 GB | 500K-2M | FREE |

**You can collect 10+ years of data and stay within free tier!**

---

## ⚠️ Troubleshooting

### **Error: "BigQuery client not initialized"**
**Solution:**
```bash
# Re-authenticate
gcloud auth application-default login

# Verify project
gcloud config get-value project
```

### **Error: "google.cloud.bigquery not found"**
**Solution:**
```bash
pip install google-cloud-bigquery
```

### **Error: "Permission denied"**
**Solution:**
```bash
# Grant yourself BigQuery User role
gcloud projects add-iam-policy-binding osint-foresight-2025 \
    --member="user:YOUR_EMAIL@gmail.com" \
    --role="roles/bigquery.user"
```

### **Too many results (hitting limits)**
**Solution:**
```bash
# Use smaller date ranges
python scripts/collectors/gdelt_bigquery_collector.py \
    --mode custom --start-date 20240101 --end-date 20240131  # Just January
```

---

## 📝 Next Steps After Collection

### **1. Validate Data**
```sql
-- Check collection stats
SELECT
    COUNT(*) as total_events,
    COUNT(DISTINCT actor1_country_code) as unique_actor1_countries,
    COUNT(DISTINCT actor2_country_code) as unique_actor2_countries,
    MIN(sqldate) as earliest_date,
    MAX(sqldate) as latest_date,
    AVG(goldstein_scale) as avg_impact,
    AVG(avg_tone) as avg_tone
FROM gdelt_events;
```

### **2. Cross-Reference with Existing Data**
```sql
-- Find events matching TED contracts
SELECT
    g.event_date,
    g.actor1_name,
    g.actor2_name,
    g.source_url,
    t.contract_title
FROM gdelt_events g
JOIN ted_contracts t
    ON DATE(g.event_date) = DATE(t.contract_award_date)
WHERE g.actor1_country_code = 'CHN'
  AND t.chinese_entity_detected = 1;
```

### **3. Generate Intelligence Reports**
```bash
# Use existing analysis scripts
python scripts/analysis/generate_china_timeline.py --source gdelt --year 2024
```

---

## 🎓 Learning Resources

**GDELT Documentation:**
- https://www.gdeltproject.org/
- https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/

**BigQuery GDELT:**
- https://console.cloud.google.com/marketplace/product/gdelt-bq/gdelt-2-0

**CAMEO Event Codes:**
- https://www.gdeltproject.org/data/documentation/CAMEO.Manual.1.1b3.pdf

---

**Status:** READY FOR USE
**Next Action:** Run test collection with `--mode recent_week`
**Expected Time:** 2-3 minutes for test, 4-6 hours for full historical backfill
