# Phase 3 Week 2: Database Integration Roadmap

**Date Started:** 2025-10-13
**Status:** IN PROGRESS
**Goal:** Integrate all data sources into master PostgreSQL database

---

## Progress Overview

### ✅ COMPLETED
1. **Database Schema Design** (`database/schema.sql`)
   - 4 tables: documents, document_topics, document_keywords, document_entities
   - 20+ indexes for performance
   - 4 views for common queries
   - 2 utility functions
   - Full text search support
   - Deduplication via hash_sha256
   - Data quality constraints

2. **Schema V1.1** (from Phase 3 Week 1)
   - UnifiedDocument Pydantic model
   - Security-hardened (100/100 tests passing)
   - Safe Mode support
   - 40 languages, 81 countries

3. **Working Converters** (from Phase 3 Week 1)
   - USGovConverter ✅
   - ThinkTankConverter ✅
   - ChinaConverter ✅

### 🚧 IN PROGRESS
4. **Database Helper Module** - Next up

### ⏳ TODO
5. **OpenAlex Converter** (Priority #1 data source)
6. **USASpending Converter** (Priority #2 data source)
7. **TED Converter** (Priority #3 data source)
8. **ETL Pipeline** with batch import
9. **End-to-end testing**

---

## Architecture

```
┌──────────────────┐
│  Data Sources    │
│  - OpenAlex      │
│  - USASpending   │
│  - TED           │
│  - Patents       │
│  - ThinkTanks    │
│  - China Policy  │
└────────┬─────────┘
         │
         ├─► Source-specific converters
         │   (OpenAlexConverter, USASpendingConverter, etc.)
         │
         ▼
┌──────────────────┐
│ UnifiedDocument  │  ← Pydantic V2 Schema
│   (Validated)    │     (Security-hardened)
└────────┬─────────┘
         │
         ├─► Database Helper Module
         │   (PostgreSQL operations)
         │
         ▼
┌──────────────────┐
│  PostgreSQL DB   │
│  - documents     │
│  - topics        │
│  - keywords      │
│  - entities      │
└──────────────────┘
```

---

## Database Schema Details

### Main Table: `documents`

**Key Fields:**
- `hash_sha256` (VARCHAR(64) UNIQUE) - Primary deduplication key
- `text_hash_sha256` (VARCHAR(64)) - Content-only hash for near-duplicates
- `publisher_country` (CHAR(2)) - ISO 3166-1 alpha-2
- `publication_date` (DATE) - For temporal analysis
- `document_type` (VARCHAR(50)) - policy, report, paper, etc.
- `qa_passed` (BOOLEAN) - Quality assurance flag
- `reliability_weight` (FLOAT 0.0-1.0) - Source quality score
- `extensions` (JSONB) - Source-specific fields

**Indexes:**
- Hash-based (deduplication)
- Date-based (temporal queries)
- Country-based (geographic queries)
- Full-text search (title + content)
- Quality flags (filtering)

**Constraints:**
- Duplicate logic validation
- QA logic validation
- Reliability weight bounds
- Date confidence levels

### Related Tables

**document_topics:**
- Many-to-many relationship
- Supports primary/secondary topics
- Fast topic-based filtering

**document_keywords:**
- Many-to-many relationship
- Extracted keywords per document
- Keyword-based search

**document_entities:**
- Many-to-many relationship
- Named entities (orgs, people, locations)
- Entity-based analysis

---

## Implementation Plan

### Step 1: Database Setup ✅

**File:** `database/schema.sql` (DONE)

**Commands:**
```bash
# Create database
psql -U postgres -c "CREATE DATABASE osint_foresight;"

# Run schema
psql -U postgres -d osint_foresight -f database/schema.sql

# Verify
psql -U postgres -d osint_foresight -c "\dt"
```

### Step 2: Database Helper Module 🚧

**File:** `database/db_helper.py` (IN PROGRESS)

**Features:**
- Connection management
- Insert documents (with deduplication)
- Batch insert (1000s at a time)
- Query by hash
- Query by date range
- Query by country
- Statistics

**Example Usage:**
```python
from database.db_helper import DatabaseHelper

db = DatabaseHelper()
db.insert_document(unified_doc)
db.batch_insert_documents([doc1, doc2, doc3, ...])
```

### Step 3: OpenAlex Converter ⏳

**File:** `scripts/schemas/converters_extended.py`

**Input:** `data/processed/openalex_production/*.json`

**Format:**
```json
{
  "paper_id": "https://openalex.org/W...",
  "title": "...",
  "publication_year": 2023,
  "collaborating_countries": ["US", "CN"],
  "validations": {...}
}
```

**Converter:** OpenAlexConverter → UnifiedDocument

### Step 4: USASpending Converter ⏳

**File:** `scripts/schemas/converters_extended.py`

**Input:** `data/processed/usaspending_production/*.json`

**Format:**
```json
{
  "award_id": "...",
  "recipient_name": "...",
  "award_amount": 1000000,
  "awarding_agency": "..."
}
```

**Converter:** USASpendingConverter → UnifiedDocument

### Step 5: TED Converter ⏳

**File:** `scripts/schemas/converters_extended.py`

**Input:** TED XML archives

**Converter:** TEDConverter → UnifiedDocument

### Step 6: ETL Pipeline ⏳

**File:** `scripts/etl_pipeline.py`

**Features:**
- Parallel processing
- Checkpoint/resume
- Deduplication via hash
- Error handling
- Progress tracking
- Statistics reporting

**Flow:**
```
1. Read source data
2. Convert to UnifiedDocument
3. Validate (Pydantic)
4. Check for duplicates (hash)
5. Insert to database
6. Update related tables (topics, keywords, entities)
7. Log stats
```

### Step 7: End-to-End Testing ⏳

**Test Cases:**
1. Convert 100 OpenAlex docs → DB
2. Convert 100 USASpending contracts → DB
3. Query by country
4. Query by date range
5. Full-text search
6. Duplicate detection
7. Performance benchmarks

---

## Data Source Priority

### Phase 3 Week 2 Focus

**Priority 1: OpenAlex (Research)**
- Volume: 1M+ papers
- Status: Data exists in `data/processed/openalex_production`
- Converter: Need OpenAlexConverter
- Est. Time: 2 hours

**Priority 2: USASpending (Contracts)**
- Volume: 10M+ records
- Status: Data exists in `data/processed/usaspending_production`
- Converter: Need USASpendingConverter
- Est. Time: 2 hours

**Priority 3: TED (EU Procurement)**
- Volume: 1M+ notices
- Status: Data exists in `data/processed/ted_2023_2025`
- Converter: Need TEDConverter
- Est. Time: 3 hours

### Phase 3 Week 3+ (Future)

**Priority 4: Patents**
- USPTO, EPO, WIPO
- Volume: 10M+ patents
- Complex data structure

**Priority 5: Think Tanks**
- Already have ThinkTankConverter
- Just need ETL pipeline

**Priority 6: China Policy**
- Already have ChinaConverter
- Just need ETL pipeline

---

## Performance Targets

### Conversion Speed
- **Target:** 1000 docs/second
- **Bottleneck:** Database inserts (use batch inserts)

### Database Size Estimates
- **OpenAlex:** ~1M docs × 10KB = 10GB
- **USASpending:** ~10M docs × 5KB = 50GB
- **TED:** ~1M docs × 10KB = 10GB
- **Total:** ~100GB (with indexes ~150GB)

### Query Performance
- **By hash:** <1ms (indexed)
- **By date:** <10ms (indexed)
- **By country:** <10ms (indexed)
- **Full-text search:** <100ms (GIN index)
- **Complex queries:** <1s

---

## Database Connection Configuration

### Environment Variables

Create `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=osint_foresight
DB_USER=osint_app
DB_PASSWORD=CHANGE_THIS_PASSWORD
DB_POOL_SIZE=10
```

### Connection Pooling

Use `psycopg2` with connection pooling for performance:
```python
import psycopg2
from psycopg2 import pool

connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
```

---

## Deduplication Strategy

### Primary Strategy: hash_sha256

**Before Insert:**
1. Calculate SHA256 of entire document
2. Check if hash exists in DB
3. If exists → skip (duplicate)
4. If new → insert

**SQL:**
```sql
SELECT id FROM documents WHERE hash_sha256 = $1;
```

### Secondary Strategy: text_hash_sha256

For near-duplicates (same content, different metadata):
1. Calculate SHA256 of content only
2. Find documents with same text_hash
3. Mark as duplicate_detected=True
4. Set duplicate_of to original hash

---

## Quality Assurance

### Document Validation

**At Conversion:**
- Pydantic validation (schema compliance)
- Security checks (Safe Mode, injection, etc.)
- Field completeness

**At Insert:**
- Hash uniqueness
- Date validity
- Country code validity
- Required fields present

**Quality Metrics:**
- % extraction_ok
- % qa_passed
- % verified sources
- Avg reliability_weight

---

## Query Examples

### Basic Queries

```sql
-- All documents from China
SELECT * FROM documents WHERE publisher_country = 'CN';

-- Documents from last 3 years
SELECT * FROM documents WHERE publication_date >= CURRENT_DATE - INTERVAL '3 years';

-- High-quality documents
SELECT * FROM high_quality_documents;

-- Full-text search
SELECT * FROM documents WHERE to_tsvector('english', title || ' ' || content_text) @@ to_tsquery('quantum & computing');
```

### Analytics Queries

```sql
-- Documents by country
SELECT * FROM documents_by_country;

-- Quality metrics
SELECT * FROM data_quality_metrics;

-- Topic distribution
SELECT topic, COUNT(*)
FROM document_topics
GROUP BY topic
ORDER BY COUNT(*) DESC;
```

---

## Security Considerations

### Database Access

- Use separate user for app (`osint_app`)
- Grant only necessary permissions (SELECT, INSERT, UPDATE)
- No DROP or ALTER permissions for app user
- Use connection pooling (prevent DOS)
- Validate all inputs (prevent SQL injection)

### Safe Mode Compliance

- URL validation at schema level
- Blocked domains checked before insert
- Archive URLs preferred for sensitive sources
- Provenance fully tracked

---

## Backup Strategy

### Daily Backups

```bash
# Dump database
pg_dump -U postgres -d osint_foresight -F c -f backup_$(date +%Y%m%d).dump

# Restore
pg_restore -U postgres -d osint_foresight backup_20251013.dump
```

### Incremental Backups

Use WAL archiving for point-in-time recovery

---

## Monitoring

### Metrics to Track

1. **Documents per day** - Ingestion rate
2. **Duplicates detected** - Data quality
3. **Conversion errors** - Pipeline health
4. **DB size growth** - Capacity planning
5. **Query performance** - User experience

### Dashboards

Create views for monitoring:
- Daily ingestion stats
- Quality metrics over time
- Top publishers by country
- Topic trends
- Error rates

---

## Next Immediate Steps

1. ✅ Create database schema (DONE)
2. 🚧 Create database helper module (IN PROGRESS)
3. ⏳ Create OpenAlex converter (NEXT)
4. ⏳ Test with 100 OpenAlex docs
5. ⏳ Create USASpending converter
6. ⏳ Create TED converter
7. ⏳ Build ETL pipeline
8. ⏳ Full integration test

---

## Success Criteria

### Phase 3 Week 2 Complete When:

- [x] Database schema created and tested
- [ ] Database helper module working
- [ ] OpenAlex converter implemented
- [ ] USASpending converter implemented
- [ ] TED converter implemented
- [ ] ETL pipeline functional
- [ ] 1000+ documents imported successfully
- [ ] All queries performing well (<1s)
- [ ] Deduplication working
- [ ] Documentation complete

---

## Timeline Estimate

- **Database Setup:** 1 hour ✅ DONE
- **DB Helper Module:** 2 hours 🚧 IN PROGRESS
- **OpenAlex Converter:** 2 hours ⏳ TODO
- **USASpending Converter:** 2 hours ⏳ TODO
- **TED Converter:** 3 hours ⏳ TODO
- **ETL Pipeline:** 3 hours ⏳ TODO
- **Testing:** 2 hours ⏳ TODO
- **Total:** ~15 hours (2 work days)

---

**Status:** Making excellent progress. Database foundation is solid. Ready for converters and ETL pipeline.

**Last Updated:** 2025-10-13
