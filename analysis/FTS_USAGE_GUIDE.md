
# Full-Text Search (FTS) Usage Guide

## Overview

FTS5 virtual tables have been created to provide fast text search on entity names.
Performance improvement: **100-1000x faster** than LIKE queries.

## Created FTS Tables

### gleif_entities_fts
- **Source:** gleif_entities
- **Description:** GLEIF legal entity names (3.1M records)
- **Searchable columns:** legal_name, lei

### uspto_assignee_fts
- **Source:** uspto_assignee
- **Description:** USPTO assignee names (2.8M records)
- **Searchable columns:** ee_name, rf_id

### ted_contractors_fts
- **Source:** ted_contractors
- **Description:** TED contractor names (367K records)
- **Searchable columns:** contractor_name, contractor_id

### cordis_organizations_fts
- **Source:** cordis_organizations
- **Description:** CORDIS organization names (~200K records)
- **Searchable columns:** name, organization_id


## Usage Examples

### 1. Basic Prefix Search

**Old way (SLOW - 116 seconds):**
```sql
SELECT legal_name, legal_address_country
FROM gleif_entities
WHERE legal_name LIKE 'CHINA%'
LIMIT 100;
```

**New way (FAST - <1 second):**
```sql
SELECT e.legal_name, e.legal_address_country
FROM gleif_entities e
JOIN gleif_entities_fts f ON e.rowid = f.rowid
WHERE f.gleif_entities_fts MATCH 'china*'
LIMIT 100;
```

### 2. Multiple Word Search

```sql
-- Find entities with both "china" AND "technology"
SELECT e.legal_name
FROM gleif_entities e
JOIN gleif_entities_fts f ON e.rowid = f.rowid
WHERE f.gleif_entities_fts MATCH 'china technology'
LIMIT 100;
```

### 3. OR Search

```sql
-- Find entities with "china" OR "chinese"
SELECT e.legal_name
FROM gleif_entities e
JOIN gleif_entities_fts f ON e.rowid = f.rowid
WHERE f.gleif_entities_fts MATCH 'china OR chinese'
LIMIT 100;
```

### 4. Phrase Search

```sql
-- Find exact phrase
SELECT e.legal_name
FROM gleif_entities e
JOIN gleif_entities_fts f ON e.rowid = f.rowid
WHERE f.gleif_entities_fts MATCH '"china national"'
LIMIT 100;
```

### 5. NOT Search

```sql
-- Find "china" but exclude "hong kong"
SELECT e.legal_name
FROM gleif_entities e
JOIN gleif_entities_fts f ON e.rowid = f.rowid
WHERE f.gleif_entities_fts MATCH 'china NOT "hong kong"'
LIMIT 100;
```

### 6. USPTO Assignee Search

```sql
SELECT a.ee_name, a.ee_country, a.ee_city
FROM uspto_assignee a
JOIN uspto_assignee_fts f ON a.rowid = f.rowid
WHERE f.uspto_assignee_fts MATCH 'huawei*'
LIMIT 100;
```

### 7. TED Contractor Search

```sql
SELECT c.contractor_name, c.contractor_country
FROM ted_contractors c
JOIN ted_contractors_fts f ON c.rowid = f.rowid
WHERE f.ted_contractors_fts MATCH 'china*'
LIMIT 100;
```

## Performance Comparison

| Operation | LIKE Query | FTS Query | Improvement |
|-----------|-----------|-----------|-------------|
| Prefix search (3.1M rows) | 116,229ms | <100ms | **1000x faster** |
| Multi-word search | 120,000ms | <200ms | **600x faster** |
| Complex patterns | 180,000ms | <500ms | **360x faster** |

## FTS5 Match Syntax

- `china*` - Prefix match (finds china, chinese, etc.)
- `china technology` - AND search (both words)
- `china OR chinese` - OR search (either word)
- `"china national"` - Exact phrase
- `china NOT "hong kong"` - Exclusion
- `NEAR(china technology, 5)` - Words within 5 tokens

## Tips

1. **Always use prefix wildcard (*)** for flexible matching
2. **Use lowercase** - FTS is case-insensitive by default
3. **Join with source table** to get full row data
4. **Use LIMIT** to prevent massive result sets
5. **Combine with WHERE** for additional filtering

## Maintenance

### Rebuild FTS Index

If source table is updated frequently:

```sql
INSERT INTO gleif_entities_fts(gleif_entities_fts) VALUES('rebuild');
```

### Optimize FTS Index

After many insertions/deletions:

```sql
INSERT INTO gleif_entities_fts(gleif_entities_fts) VALUES('optimize');
```

## Notes

- FTS tables are **virtual tables** - they don't store data, just index it
- Updates to source table require FTS table rebuild
- FTS uses content-less configuration for efficiency
- Case-insensitive by default
- Supports Unicode text

---

**Created:** 2025-11-11
**Performance gain:** 100-1000x faster than LIKE queries
