# OpenSanctions Data Collection

**Last Updated:** 2025-09-21
**Location:** `F:\OSINT_Data\OpenSanctions\`
**Database:** `F:\OSINT_Data\OpenSanctions\processed\sanctions.db`

## Overview
Comprehensive global sanctions data collection focused on identifying Chinese-affiliated entities across multiple international sanctions regimes.

## Data Statistics
- **Total Entities:** 183,766
- **Chinese/Hong Kong Entities:** 7,177
- **Total Data Size:** 376MB
- **Collection Date:** 2025-09-21

## Datasets Downloaded

### 1. US OFAC SDN (135MB)
- **Source:** US Office of Foreign Assets Control - Specially Designated Nationals
- **Chinese Entities:** 1,220
- **Files:** entities.ftm.json, targets.simple.csv, targets.nested.json
- **Programs:** Iran, North Korea, Russia, Global Magnitsky, Cyber

### 2. EU Financial Sanctions File (36MB)
- **Source:** European Union Consolidated Financial Sanctions
- **Chinese Entities:** 39
- **Files:** entities.ftm.json, targets.simple.csv, targets.nested.json

### 3. UK HM Treasury (37MB)
- **Source:** UK Her Majesty's Treasury Consolidated List
- **Files:** entities.ftm.json, targets.simple.csv, targets.nested.json

### 4. Swiss SECO (48MB)
- **Source:** Switzerland State Secretariat for Economic Affairs
- **Files:** entities.ftm.json, targets.simple.csv, targets.nested.json

### 5. Australian DFAT (20MB)
- **Source:** Australian Department of Foreign Affairs and Trade
- **Files:** entities.ftm.json, targets.simple.csv, targets.nested.json

### 6. UN Security Council (7.3MB)
- **Source:** United Nations Security Council Consolidated List
- **Files:** entities.ftm.json, targets.simple.csv, targets.nested.json

### 7. US BIS Denied Parties (5.3MB)
- **Source:** US Bureau of Industry and Security
- **Files:** entities.ftm.json, targets.simple.csv, source.xls

### 8. Japan MOF (23MB)
- **Source:** Japan Ministry of Finance
- **Files:** entities.ftm.json, targets.simple.csv

### 9. Asian Development Bank (2.5MB)
- **Source:** ADB Debarred Entities
- **Files:** entities.ftm.json, targets.simple.csv

### 10. US Trade CSL
- **Source:** US Consolidated Screening List
- **Files:** entities.ftm.json, targets.simple.csv

### 11. World Bank Debarred (2.5MB)
- **Source:** World Bank Listing of Ineligible Firms
- **Files:** entities.ftm.json, targets.simple.csv

## Database Schema

### Main Tables
- `chinese_entities` - All identified Chinese/HK/MO entities
- `sanctions_programs` - Sanctions program details
- `entity_identifiers` - Various identifiers (IMO, BIC, etc.)
- `addresses` - Entity addresses
- `relationships` - Entity relationships

## Chinese Entity Identification Criteria
- Country codes: CN, HK, MO, TW
- Address containing: China, Beijing, Shanghai, Shenzhen, Hong Kong, Macau
- Chinese company suffixes: 有限公司, 股份有限公司, 集团
- Nationality/jurisdiction indicators

## Access Methods

### SQLite Database
```sql
-- Example: Find all Chinese entities
SELECT * FROM chinese_entities;

-- Example: Find entities by sanctions program
SELECT * FROM chinese_entities WHERE sanctions_program LIKE '%IRAN%';
```

### Python Access
```python
import sqlite3
conn = sqlite3.connect('F:/OSINT_Data/OpenSanctions/processed/sanctions.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM chinese_entities")
```

## Update Frequency
- OpenSanctions updates daily
- Recommend weekly refresh for active investigations

## Data Formats
- JSON (Follow the Money format)
- CSV (simplified format)
- SQLite database (processed)

## Script Location
`C:\Projects\OSINT - Foresight\scripts\download_opensanctions.py`
