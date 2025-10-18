# GLEIF LEI Data Collection

**Last Updated:** 2025-09-21
**Location:** `F:\OSINT_Data\GLEIF\`
**Database:** `F:\OSINT_Data\GLEIF\databases\gleif_analysis_20250921.db`

## Overview
Global Legal Entity Identifier (LEI) data from GLEIF providing comprehensive corporate registration and ownership relationship information.

## Data Statistics
- **Total LEI Records:** 3.07 million
- **Chinese Entities (CN/HK/MO/TW):** 1,750
- **Relationship Records:** 599,574
- **Reporting Exceptions:** 5.46 million
- **Total Data Size:** ~525MB

## Datasets Downloaded

### 1. LEI Records (Level 1) - 448.6MB
- **Content:** Basic entity information ("who is who")
- **Records:** 3,067,073
- **Format:** ZIP containing XML/JSON
- **URL:** `https://leidata.gleif.org/api/v1/concatenated-files/lei2/get/38981/zip`
- **Fields:**
  - Legal name
  - Registration address
  - Country
  - Entity status
  - Registration/expiry dates

### 2. Relationship Records (Level 2) - 31.93MB
- **Content:** Ownership relationships ("who owns whom")
- **Records:** 599,574
- **Format:** ZIP containing XML/JSON
- **URL:** `https://leidata.gleif.org/api/v1/concatenated-files/rr/get/38984/zip`
- **Relationship Types:**
  - IS_DIRECTLY_CONSOLIDATED_BY (direct parent)
  - IS_ULTIMATELY_CONSOLIDATED_BY (ultimate parent)
  - IS_INTERNATIONAL_BRANCH_OF

### 3. Reporting Exceptions - 41.85MB
- **Content:** Entities unable to report parent relationships
- **Records:** 5,456,691
- **Format:** ZIP containing XML/JSON
- **URL:** `https://leidata.gleif.org/api/v1/concatenated-files/repex/get/38987/zip`

### 4. BIC-LEI Mapping (August 2025)
- **Content:** Mapping between BIC codes and LEIs
- **Source:** GLEIF-SWIFT collaboration
- **Use:** Cross-reference financial institutions

## Chinese Entity Distribution
- **Mainland China (CN):** ~10,000 entities searched
- **Hong Kong (HK):** ~10,000 entities searched
- **Macau (MO):** Limited entities
- **Taiwan (TW):** ~900 entities
- **Total Identified:** 1,750 with complete data

## Database Schema

### Core Tables
```sql
-- Entity information
lei_entities (
    lei TEXT PRIMARY KEY,
    legal_name TEXT,
    country TEXT,
    entity_status TEXT,
    registration_date TEXT,
    last_update TEXT,
    is_chinese INTEGER,
    raw_data TEXT
)

-- Ownership relationships
ownership_relationships (
    parent_lei TEXT,
    child_lei TEXT,
    relationship_type TEXT,
    ownership_percentage REAL,
    start_date TEXT,
    end_date TEXT
)

-- Identifier mappings
identifier_mappings (
    lei TEXT,
    identifier_type TEXT (BIC/ISIN),
    identifier_value TEXT
)

-- Chinese ownership analysis
chinese_ownership_analysis (
    lei TEXT,
    direct_chinese_ownership REAL,
    ultimate_chinese_ownership REAL,
    chinese_parent_chain TEXT
)
```

## API Access Configuration
- **Base URL:** `https://api.gleif.org/api/v1`
- **Rate Limit:** 60 requests per minute
- **No authentication required**
- **Supports:** Filters, full-text search, relationship queries

## Data Quality Features
- **Golden Copy:** Validated by GLEIF
- **Update Frequency:** 3 times daily
- **Data Formats:** CDF 2.1 (Common Data File)
- **Validation:** XML schema validated

## Access Methods

### Direct File Access
```python
# LEI Records
F:/OSINT_Data/GLEIF/bulk_data/lei_records/20250921-gleif-goldencopy-lei2-golden-copy.xml

# Relationship Records
F:/OSINT_Data/GLEIF/bulk_data/relationships/20250921-gleif-goldencopy-rr-golden-copy.xml
```

### SQLite Database
```sql
-- Find Chinese entities
SELECT * FROM lei_entities WHERE country IN ('CN', 'HK', 'MO', 'TW');

-- Get ownership trees
SELECT * FROM ownership_relationships
WHERE parent_lei IN (SELECT lei FROM lei_entities WHERE is_chinese = 1);
```

### Python Access
```python
import sqlite3
conn = sqlite3.connect('F:/OSINT_Data/GLEIF/databases/gleif_analysis_20250921.db')
```

## Ownership Tree Structure
```json
{
  "lei": "254900EXAMPLE",
  "direct_parents": [
    {"lei": "parent_lei", "percentage": 100.0}
  ],
  "ultimate_parents": [
    {"lei": "ultimate_lei", "percentage": 100.0}
  ],
  "subsidiaries": []
}
```

## Update Process
1. Daily concatenated files available at 00:30, 08:30, 16:30 CET
2. Delta files show only changes
3. Full refresh recommended weekly

## Script Locations
- Download script: `C:\Projects\OSINT - Foresight\scripts\download_gleif_lei.py`
- Chinese entities: `F:\OSINT_Data\GLEIF\processed\chinese_entities\`
- Ownership trees: `F:\OSINT_Data\GLEIF\processed\ownership_trees\`

## Key Use Cases
- Corporate structure mapping
- Parent-subsidiary relationship analysis
- Cross-border ownership tracking
- Financial institution identification (via BIC)
- Regulatory compliance verification
