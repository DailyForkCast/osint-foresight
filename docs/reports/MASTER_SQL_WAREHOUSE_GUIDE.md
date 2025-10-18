# 🎯 MASTER SQL WAREHOUSE GUIDE FOR ALL CLAUDE CODE INSTANCES

## 📍 CRITICAL PATHS AND LOCATIONS

### Primary Warehouse Database
```
Location: F:/OSINT_WAREHOUSE/osint_research.db
Type: SQLite (portable to PostgreSQL)
Schema: v3 Hybrid (see sql_research_warehouse_playbook_v3_hybrid_complete.md)
```

### Key Directories
```
Project Root: C:/Projects/OSINT - Foresight/
Database Scripts: C:/Projects/OSINT - Foresight/database/
Processing Scripts: C:/Projects/OSINT - Foresight/scripts/
Processed Data: C:/Projects/OSINT - Foresight/data/processed/
Raw Data: F:/OSINT_DATA/ and F:/TED_Data/
```

## 🏗️ WAREHOUSE ARCHITECTURE

### Schema Layers
```sql
-- 1. RAW LAYER (Immutable)
raw_* tables - Original data as received

-- 2. STAGE LAYER (Cleaned)
stage_* tables - Typed and validated

-- 3. CORE LAYER (Conformed)
core_f_* - Facts (collaborations, publications, patents, procurement, trade)
core_dim_* - Dimensions (organizations, persons, products, locations)

-- 4. MARTS LAYER (Subject Areas)
marts_supply - Supply chain intelligence
marts_intel - Intelligence fusion
marts_risk - Risk assessments

-- 5. OPS LAYER (Operations)
ops_quality_* - Data quality monitoring
ops_alert_* - Alert rules and history
ops_false_negative_log - Critical for OpenAIRE fix

-- 6. RESEARCH LAYER (Reproducibility)
research_session - Research tracking (NOT compliance/GDPR)
research_query_log - Query history
research_findings - Documented findings
```

## 📊 CORE TABLES AND THEIR PURPOSE

### 1. core_f_collaboration
**Purpose**: Track research collaborations between entities
**Key Fields**:
- collab_id (PRIMARY KEY)
- has_chinese_partner (BOOLEAN)
- china_collaboration_score (FLOAT 0-1)
- source_system (TEXT)
- confidence_score (FLOAT)

**Insert Example**:
```python
cursor.execute("""
INSERT OR REPLACE INTO core_f_collaboration (
    collab_id, project_name, has_chinese_partner,
    china_collaboration_score, source_system, confidence_score
) VALUES (?, ?, ?, ?, ?, ?)
""", (id, name, has_china, china_score, 'CORDIS', 0.95))
```

### 2. core_f_publication
**Purpose**: Scientific publications and articles
**Key Fields**:
- pub_id (PRIMARY KEY)
- doi (UNIQUE)
- has_chinese_author (BOOLEAN)
- source_system ('OpenAIRE_Keyword' for fixed data)

### 3. core_f_patent
**Purpose**: Patent filings and grants
**Key Fields**:
- patent_id (PRIMARY KEY)
- has_chinese_applicant (BOOLEAN)
- technology_transfer_risk (TEXT: 'HIGH'/'MEDIUM'/'LOW')

### 4. core_f_procurement
**Purpose**: Government and institutional procurement
**Key Fields**:
- award_id (PRIMARY KEY)
- has_chinese_vendor (BOOLEAN)
- supply_chain_risk (TEXT: 'HIGH'/'MEDIUM'/'LOW')

### 5. core_f_trade_flow
**Purpose**: International trade data
**Key Fields**:
- flow_id (PRIMARY KEY)
- involves_china (BOOLEAN)
- is_strategic_product (BOOLEAN)

## 🔧 STANDARD OPERATING PROCEDURES

### For Data Import Tasks

1. **Always Check Existing Data First**:
```python
import sqlite3
conn = sqlite3.connect("F:/OSINT_WAREHOUSE/osint_research.db")
cursor = conn.cursor()

# Check what's already loaded
cursor.execute("""
SELECT source_system, COUNT(*)
FROM core_f_collaboration
GROUP BY source_system
""")
print(cursor.fetchall())
```

2. **Use Standard China Detection**:
```python
def detect_china_involvement(text):
    """Standard China detection function"""
    if not text:
        return 0.0

    text_lower = text.lower()

    # Strong indicators (return 0.9)
    strong = ['china', 'chinese', 'beijing', 'shanghai', 'tsinghua',
              'huawei', 'cas', 'xinjiang', 'tibet']

    for term in strong:
        if term in text_lower:
            return 0.9

    # Medium indicators (return 0.5)
    medium = ['asia', 'sino-', 'prc']
    for term in medium:
        if term in text_lower:
            return 0.5

    return 0.0
```

3. **Always Include Provenance**:
```python
from datetime import datetime

# Every insert should include:
source_system = 'YOUR_SOURCE'  # e.g., 'CORDIS', 'OpenAIRE_Keyword', 'TED_EU'
source_file = 'path/to/file.json'
retrieved_at = datetime.now().isoformat()
confidence_score = 0.95  # Based on data quality
```

### For OpenAIRE Processing (CRITICAL)

**⚠️ NEVER USE**:
```python
# WRONG - Returns 0 results!
params = {'country': 'IT,CN'}  # or 'IT AND CN'
```

**✅ ALWAYS USE**:
```python
# CORRECT - Returns actual results
params = {
    'country': 'IT',
    'keywords': 'China OR Chinese OR Beijing OR Shanghai'
}
```

**Import Script**: Use `scripts/openaire_keyword_collector.py`

### For TED Procurement Processing

```python
# TED data location
ted_path = "F:/TED_Data/monthly/"

# Process XML files for China involvement
import xml.etree.ElementTree as ET

tree = ET.parse(xml_file)
# Look for contractor/vendor elements
# Check against China indicators
```

### For Quality Monitoring

```python
# Always log potential issues
cursor.execute("""
INSERT INTO ops_quality_results (
    rule_id, passed, metric_value, failed_count
) VALUES (?, ?, ?, ?)
""", ('china_detection', True, detection_rate, 0))

# Track false negatives
cursor.execute("""
INSERT INTO ops_false_negative_log (
    source_system, query_method, original_results, corrected_results
) VALUES (?, ?, ?, ?)
""", ('OpenAIRE', 'keyword_fix', 0, actual_count))
```

## 📈 STANDARD QUERIES FOR ANALYSIS

### 1. China Collaboration Overview
```sql
SELECT
    source_system,
    COUNT(*) as total_records,
    SUM(has_chinese_partner) as china_records,
    AVG(china_collaboration_score) as avg_score,
    AVG(confidence_score) as avg_confidence
FROM core_f_collaboration
GROUP BY source_system
ORDER BY china_records DESC;
```

### 2. High-Risk Entities
```sql
SELECT
    entity_id,
    composite_risk_score,
    china_exposure_score
FROM core_risk_scores
WHERE china_exposure_score > 0.7
ORDER BY composite_risk_score DESC
LIMIT 100;
```

### 3. Supply Chain Vulnerabilities
```sql
SELECT
    vendor_name,
    COUNT(*) as contract_count,
    SUM(contract_value) as total_value,
    supply_chain_risk
FROM core_f_procurement
WHERE has_chinese_vendor = 1
GROUP BY vendor_name
ORDER BY total_value DESC;
```

### 4. Technology Transfer Risks
```sql
SELECT
    COUNT(*) as patent_count,
    technology_transfer_risk
FROM core_f_patent
WHERE has_chinese_applicant = 1
GROUP BY technology_transfer_risk;
```

## 🚀 QUICK START FOR NEW TERMINALS

### Terminal 1: Import CORDIS Data
```bash
cd "C:/Projects/OSINT - Foresight/database"
python import_processed_data.py
```

### Terminal 2: Process OpenAIRE (Correctly!)
```bash
cd "C:/Projects/OSINT - Foresight"
python scripts/openaire_keyword_collector.py
```

### Terminal 3: Load TED Procurement
```bash
cd "C:/Projects/OSINT - Foresight/database"
python comprehensive_data_loader.py
```

### Terminal 4: Monitor Progress
```bash
# Watch import progress
watch -n 5 'sqlite3 F:/OSINT_WAREHOUSE/osint_research.db "SELECT source_system, COUNT(*) FROM core_f_collaboration GROUP BY source_system"'
```

## 📋 TASK ASSIGNMENT BY TERMINAL

### Terminal A: EU Data Collection
```python
# Focus on major EU countries
countries = ['IT', 'DE', 'FR', 'ES', 'NL']
collector.collect_all_eu_china(countries)
```

### Terminal B: Eastern Europe Collection
```python
# Focus on Eastern Europe
countries = ['PL', 'CZ', 'HU', 'SK', 'RO']
collector.collect_all_eu_china(countries)
```

### Terminal C: Nordic/Baltic Collection
```python
# Focus on Nordic/Baltic
countries = ['SE', 'DK', 'FI', 'EE', 'LV', 'LT']
collector.collect_all_eu_china(countries)
```

### Terminal D: Smaller EU States
```python
# Focus on smaller states
countries = ['BE', 'LU', 'MT', 'CY', 'SI', 'HR']
collector.collect_all_eu_china(countries)
```

## ⚠️ CRITICAL WARNINGS

1. **OpenAIRE**: NEVER use direct country queries (IT,CN) - ALWAYS use keywords
2. **Duplicates**: Always use INSERT OR REPLACE, not INSERT
3. **China Detection**: Use standardized detection function, not ad-hoc
4. **Confidence**: Document confidence scores based on source quality
5. **Rate Limits**: Add 1-2 second delays between API calls

## 📊 EXPECTED RESULTS

When properly configured, you should see:

- **CORDIS**: 10,000+ projects with 5-10% China involvement
- **OpenAIRE (Keyword)**: 1,000,000+ publications with China
- **TED**: 100,000+ contracts with **3-5% China involvement** (3,047 found in 1.42M XMLs so far)
- **Patents**: 50,000+ with 10-15% China involvement

### TED ACTUAL FINDINGS (2025-09-22)
- **Processed**: 1,423,318 XML files (33 archives)
- **Chinese Contracts Found**: 3,047
- **Coverage**: 2016-2018 complete, 2019-2022 in progress
- **Hit Rate**: ~0.2% (higher than expected)
- **Top Entities**: Huawei, ZTE, Lenovo, DJI, BYD, BOE, Hikvision, CATL

If you're getting 0 or very few China results, CHECK YOUR METHOD!

## 🆘 TROUBLESHOOTING

### Problem: Getting 0 China collaborations
**Solution**: You're using the wrong query method. Use keyword search.

### Problem: Database locked errors
**Solution**: Only one process should write at a time. Use INSERT OR REPLACE.

### Problem: Slow imports
**Solution**: Batch inserts, use transactions:
```python
conn.execute("BEGIN TRANSACTION")
# ... multiple inserts ...
conn.commit()
```

### Problem: Duplicate records
**Solution**: Use unique IDs and INSERT OR REPLACE

## 📞 COORDINATION

All terminals should:
1. Check this guide first
2. Use standardized functions
3. Report to warehouse at `F:/OSINT_WAREHOUSE/osint_research.db`
4. Log issues to `ops_quality_results` table
5. Document false negatives in `ops_false_negative_log`

## 🎯 SUCCESS METRICS

You know you're successful when:
- ✅ China detection rate > 5% for collaborations
- ✅ OpenAIRE returns > 1000 results per country
- ✅ No "0 results" for major countries
- ✅ Confidence scores documented
- ✅ False negative log shows improvements

---

**REMEMBER**: This is a research project focused on identifying China-EU technology collaborations with ZERO FABRICATION and FULL PROVENANCE. Every record must be traceable to its source!
