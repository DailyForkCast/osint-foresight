# Critical Fixes Needed for Your Database Schema

## 🔴 Issues Found in Your Adaptation

Your SQLite conversion is excellent, but it uses column names from the template that don't match your actual database. Here are the required fixes:

### 1. **documents table** - Column Name Mismatches

**Template uses:**
```sql
SELECT content, source, created_date FROM documents
```

**Your database has:**
```sql
SELECT content_text, publisher_org, publication_date FROM documents
```

**Fix Required:** Replace all instances in queries:
- `content` → `content_text`
- `source` → `publisher_org`
- `created_date` → `publication_date`

### 2. **document_entities table** - Column Name Mismatch

**Template uses:**
```sql
SELECT entity_name FROM document_entities
```

**Your database has:**
```sql
SELECT entity_text FROM document_entities
```

**Fix Required:** Replace `entity_name` → `entity_text`

### 3. **mcf_entities table** - Structure Completely Different

**Template assumes:**
```sql
SELECT entity_text, entity_type, document_id FROM mcf_entities
```

**Your database has:**
```sql
SELECT name, entity_type, entity_id FROM mcf_entities
-- AND links via mcf_document_entities table!
```

**Fix Required:**
- Use `name` instead of `entity_text`
- Join through `mcf_document_entities` to get document relationships:
```sql
SELECT
    me.name as entity_text,
    me.entity_type,
    mde.doc_id as document_id
FROM mcf_entities me
JOIN mcf_document_entities mde ON me.entity_id = mde.entity_id
```

### 4. **mcf_documents table** - ID field different

**Template uses:**
```sql
SELECT id FROM mcf_documents
```

**Your database has:**
```sql
SELECT doc_id FROM mcf_documents
```

**Fix Required:** Replace `id` → `doc_id`

---

## ✅ Automated Fix Strategy

I recommend creating a query builder helper that automatically uses correct column names:

```python
def build_query(template_query):
    """Convert template queries to use your actual column names"""
    replacements = {
        'documents.content ': 'documents.content_text ',
        'documents.source ': 'documents.publisher_org ',
        'documents.created_date': 'documents.publication_date',
        'd.content ': 'd.content_text ',
        'd.source ': 'd.publisher_org ',
        'd.created_date': 'd.publication_date',
        'entity_name': 'entity_text',  # for document_entities
        'mcf_entities.entity_text': 'mcf_entities.name',
        'mcf_documents.id ': 'mcf_documents.doc_id ',
        'md.id ': 'md.doc_id '
    }

    query = template_query
    for old, new in replacements.items():
        query = query.replace(old, new)

    return query
```

---

## 📊 Schema Verification Queries

Run these to verify your actual schema:

```sql
-- Check documents columns
PRAGMA table_info(documents);

-- Check document_entities columns
PRAGMA table_info(document_entities);

-- Check MCF structure
PRAGMA table_info(mcf_entities);
PRAGMA table_info(mcf_documents);
PRAGMA table_info(mcf_document_entities);

-- Check entity counts
SELECT
    COUNT(*) as total_entities,
    COUNT(DISTINCT entity_text) as unique_entities
FROM document_entities;

SELECT
    COUNT(*) as total_entities,
    COUNT(DISTINCT name) as unique_names
FROM mcf_entities;
```

---

## 🚀 Quick Fix Checklist

- [ ] Update all `content` → `content_text` in queries
- [ ] Update all `source` → `publisher_org` in queries
- [ ] Update all `created_date` → `publication_date` in queries
- [ ] Update document_entities `entity_name` → `entity_text`
- [ ] Fix MCF queries to use `name` and join through `mcf_document_entities`
- [ ] Update mcf_documents `id` → `doc_id`
- [ ] Test each analysis function individually
- [ ] Verify Chinese character detection works (`WHERE content_text LIKE '%中%'`)

---

## 🔧 Files That Need Updates

1. **consensus_tracker_sqlite_v2.py**
   - Line ~50: entity normalization query
   - Line ~100: context extraction query
   - Line ~150: source weighting query

2. **narrative_evolution_sqlite_v2.py**
   - Line ~60: monthly data CTE
   - Line ~100: sentiment analysis CTE
   - All topic queries

3. **entity_networks_sqlite_v2.py**
   - Line ~40: co-occurrence query
   - Line ~200: context lookups

4. **mcf_analysis_sqlite_v2.py**
   - Line ~30: MCF document query (CRITICAL - different schema)
   - Line ~80: MCF entity query (CRITICAL - needs join)
   - Line ~200: technology domain queries
   - Line ~300: exclusive entities query

---

## 💡 Recommendation

Before running the full suite, I suggest:

1. Create a test script that runs just the preflight checks
2. Verify all table/column names are correct
3. Test each analysis function on a LIMIT 10 sample first
4. Check that Chinese detection works correctly
5. Verify entity normalization produces expected results

Would you like me to create corrected versions of the analysis scripts with your actual schema?
