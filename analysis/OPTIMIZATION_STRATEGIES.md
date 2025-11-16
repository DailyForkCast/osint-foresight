# Query Optimization Strategies for Patent-Policy Cross-Reference

**Problem:** Joining 425k patents with 65.6M CPC classifications is computationally expensive

---

## Strategy 1: Create Materialized View (RECOMMENDED - Fast but upfront cost)

**Create a pre-computed sector mapping table:**

```sql
-- One-time setup (will take 10-15 minutes)
CREATE TABLE IF NOT EXISTS patent_sector_mapping AS
SELECT DISTINCT
    p.application_number,
    p.filing_date,
    CASE
        WHEN c.cpc_full LIKE 'H01L%' THEN 'semiconductors'
        WHEN c.cpc_full LIKE 'G06F%' OR c.cpc_full LIKE 'G06N%' THEN 'ai_computing'
        WHEN c.cpc_full LIKE 'B25J%' THEN 'robotics'
        WHEN c.cpc_full LIKE 'B64C%' OR c.cpc_full LIKE 'B64D%' THEN 'aerospace'
        WHEN c.cpc_full LIKE 'B60L%' OR c.cpc_full LIKE 'H01M%' THEN 'new_energy_vehicles'
        WHEN c.cpc_full LIKE 'A61K%' OR c.cpc_full LIKE 'C12N%' THEN 'biopharmaceuticals'
        ELSE 'other'
    END as sector
FROM uspto_patents_chinese p
JOIN uspto_cpc_classifications c ON p.application_number = c.application_number;

-- Create index
CREATE INDEX idx_sector_mapping ON patent_sector_mapping(sector, filing_date);
```

**Then queries become FAST:**
```sql
-- This will be instant
SELECT sector, COUNT(*)
FROM patent_sector_mapping
WHERE filing_date >= '2015-05-08'
GROUP BY sector;
```

**Pros:** Subsequent queries extremely fast (milliseconds)
**Cons:** One-time setup cost of 10-15 minutes

---

## Strategy 2: Add Targeted Indexes (MODERATE - 5 min setup)

```sql
-- Index on CPC prefix (for LIKE queries)
CREATE INDEX IF NOT EXISTS idx_cpc_prefix ON uspto_cpc_classifications(SUBSTR(cpc_full, 1, 4));

-- Index on application_number (for joins)
CREATE INDEX IF NOT EXISTS idx_cpc_app_num ON uspto_cpc_classifications(application_number);
```

**Pros:** Speeds up existing queries
**Cons:** Doesn't solve fundamental join size issue

---

## Strategy 3: Sample-Based Analysis (FASTEST - Immediate)

**Use 10% random sample for initial testing:**

```python
# Instead of full dataset:
WHERE p.application_number IN (
    SELECT application_number
    FROM uspto_patents_chinese
    WHERE RANDOM() % 10 = 0  -- 10% sample
)
```

**Pros:** Immediate results for testing
**Cons:** Less precise, need to scale up results
**Use case:** Quick hypothesis testing before full run

---

## Strategy 4: Query Simplification (MODERATE - Rewrite queries)

**Instead of complex LIKE patterns, extract CPC class first:**

```python
# Current (slow):
WHERE c.cpc_full LIKE 'H01L%' OR c.cpc_full LIKE 'G06F%' ...

# Optimized (faster):
WHERE SUBSTR(c.cpc_full, 1, 4) IN ('H01L', 'G06F', 'G06N', 'B25J', ...)
```

**Pros:** Faster than LIKE with patterns
**Cons:** Still requires full table scan without materialized view

---

## Strategy 5: Parallel Processing (MODERATE - Split work)

**Process one sector at a time in separate scripts:**

```bash
# Run 10 separate processes, one per MIC2025 sector
python analyze_semiconductors.py &
python analyze_robotics.py &
python analyze_aerospace.py &
...
```

**Pros:** Uses multiple CPU cores
**Cons:** Requires splitting script, managing multiple processes

---

## Recommended Approach: Hybrid

### Phase 1: Quick Test (5 minutes)
- Use 10% sample (Strategy 3)
- Get directional findings immediately
- Validate approach before full run

### Phase 2: Optimization Setup (15 minutes)
- Create materialized view (Strategy 1)
- Add indexes (Strategy 2)
- One-time cost, permanent benefit

### Phase 3: Production Queries (Seconds to minutes)
- Run full analysis on optimized database
- All subsequent queries will be fast

---

## Implementation Priority

**For immediate results (next 5 minutes):**
→ Run sample-based analysis (Strategy 3)

**For production database (next 20 minutes):**
→ Create materialized view (Strategy 1)
→ All future queries will be instant

**Which would you prefer?**
