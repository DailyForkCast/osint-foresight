# TED Analysis Output Locations Guide
**Where to find all results after processing**

---

## 📂 PRIMARY OUTPUT DIRECTORY

After running the TED analysis, all findings will be in:

```
C:/Projects/OSINT - Foresight/data/processed/ted_multicountry/
```

---

## 🗂️ COMPLETE OUTPUT STRUCTURE

```
data/processed/ted_multicountry/
│
├── 📊 analysis/                              ← START HERE FOR SUMMARY
│   ├── MULTI_COUNTRY_ANALYSIS_REPORT.md     ← Human-readable summary
│   ├── comprehensive_analysis.json          ← Complete analysis data
│   └── CRITICAL_FINDINGS_EXECUTIVE.md       ← Executive brief
│
├── 🌍 by_country/                           ← Country-specific findings
│   ├── IT_china/                           ← Italy-China contracts
│   │   ├── contracts_2024.json
│   │   ├── contracts_2023.json
│   │   └── summary.json
│   ├── DE_china/                           ← Germany-China contracts
│   ├── FR_china/                           ← France-China contracts
│   └── [all 30 countries]/
│
├── 🏢 by_company/                           ← Company-centric view
│   ├── huawei/
│   │   ├── all_contracts.json              ← All Huawei contracts across EU
│   │   ├── countries_present.json          ← Which countries they operate in
│   │   └── risk_assessment.json
│   ├── zte/
│   ├── crrc/
│   └── [all tracked entities]/
│
├── 🏗️ by_sector/                           ← Technology sector analysis
│   ├── telecom/
│   │   ├── all_5g_contracts.json
│   │   └── country_breakdown.json
│   ├── nuclear/
│   ├── rail/
│   └── [all sectors]/
│
├── 🔗 cross_border/                         ← Multi-country patterns
│   ├── subsidiary_networks.json             ← Shell company mappings
│   ├── coordinated_campaigns.json           ← Synchronized activities
│   └── market_division_patterns.json        ← Anti-competitive behavior
│
├── 📈 temporal/                             ← Timeline analysis
│   ├── 2010_2012_baseline.json             ← Pre-BRI period
│   ├── 2013_2016_bri_launch.json           ← Belt & Road start
│   ├── 2017_2019_expansion.json            ← Peak period
│   ├── 2020_2022_covid.json                ← Pandemic period
│   └── 2023_2025_current.json              ← Recent activity
│
├── ⚠️ risk_assessment/                     ← Critical intelligence
│   ├── COUNTRY_RISK_RANKING.json           ← Countries by risk level
│   ├── CRITICAL_INFRASTRUCTURE.json        ← Infrastructure exposure
│   └── IMMEDIATE_THREATS.json              ← Urgent concerns
│
├── 🔍 networks/                            ← Relationship graphs
│   ├── company_network.gexf                ← For Gephi visualization
│   └── country_connections.json            ← Network analysis
│
└── ✓ checkpoint.json                       ← Processing status
```

---

## 📊 KEY FILES TO CHECK FIRST

### 1. 🎯 **Executive Summary**
```
data/processed/ted_multicountry/analysis/MULTI_COUNTRY_ANALYSIS_REPORT.md
```
- Human-readable summary
- Top findings
- Risk rankings
- Critical patterns

### 2. 📈 **Country Risk Ranking**
```
data/processed/ted_multicountry/risk_assessment/COUNTRY_RISK_RANKING.json
```
```json
{
    "highest_risk": [
        {
            "country": "HU",
            "name": "Hungary",
            "china_penetration": "12.3%",
            "critical_contracts": 47,
            "risk_score": 94.5
        }
    ]
}
```

### 3. 🏢 **Company Footprint**
```
data/processed/ted_multicountry/by_company/huawei/all_contracts.json
```
- Every Huawei contract across all EU
- Total value
- Technology areas
- Risk assessment

### 4. 🇮🇹 **Italy-Specific Findings**
```
data/processed/ted_multicountry/by_country/IT_china/
```
- All Italy-China contracts
- Italian authorities awarding to Chinese companies
- Sector breakdown
- Temporal trends

---

## 🔍 HOW TO ACCESS FINDINGS

### Quick Command Line Access:
```bash
# View executive summary
cat data/processed/ted_multicountry/analysis/MULTI_COUNTRY_ANALYSIS_REPORT.md

# Check Italy-China contracts
ls data/processed/ted_multicountry/by_country/IT_china/

# Count total findings
find data/processed/ted_multicountry -name "*.json" -exec grep -c "contract_id" {} \; | paste -sd+ | bc

# View high-risk findings
jq '.critical_findings[]' data/processed/ted_multicountry/risk_assessment/IMMEDIATE_THREATS.json
```

### Python Access:
```python
import json
from pathlib import Path

# Load comprehensive analysis
with open('data/processed/ted_multicountry/analysis/comprehensive_analysis.json') as f:
    analysis = json.load(f)

# Get Italy-specific data
italy_path = Path('data/processed/ted_multicountry/by_country/IT_china')
for contract_file in italy_path.glob('*.json'):
    with open(contract_file) as f:
        contracts = json.load(f)
        print(f"{contract_file.name}: {len(contracts)} contracts")

# Check Huawei footprint
with open('data/processed/ted_multicountry/by_company/huawei/all_contracts.json') as f:
    huawei = json.load(f)
    print(f"Huawei present in {len(huawei['countries'])} EU countries")
```

---

## 📝 UNDERSTANDING THE OUTPUT

### Finding Structure:
Each finding contains:
```json
{
    "contract_id": "TED-2024-000123",
    "authority_country": "IT",
    "contracting_authority": "Ministero delle Infrastrutture",
    "chinese_entity": "huawei",
    "value": 45000000,
    "currency": "EUR",
    "sector": "telecom",
    "technology_categories": ["5G", "telecommunications"],
    "risk_level": "CRITICAL",
    "verification": {
        "source_file": "F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz",
        "xml_file": "2024_01_15/CONTRACT_123.xml",
        "verification_command": "tar -xzf ... | grep ...",
        "extraction_timestamp": "2025-09-20T15:30:00"
    }
}
```

### Summary Statistics:
```json
{
    "italy_statistics": {
        "total_contracts": 125000,
        "china_contracts": 342,
        "penetration_rate": "0.27%",
        "total_value_eur": 1250000000,
        "top_sectors": ["telecom", "rail", "energy"],
        "trend": "increasing",
        "risk_level": "MEDIUM"
    }
}
```

---

## 📈 VISUALIZING FINDINGS

### Excel/CSV Export:
```python
# Convert to CSV for Excel
import pandas as pd

# Load JSON findings
with open('data/processed/ted_multicountry/by_country/IT_china/contracts_2024.json') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Export to CSV
df.to_csv('italy_china_contracts_2024.csv', index=False)
```

### Quick Statistics:
```bash
# Total Italy-China contracts
find data/processed/ted_multicountry/by_country/IT_china -name "*.json" -exec jq '. | length' {} \; | paste -sd+ | bc

# Total value
jq '[.[] | .value] | add' data/processed/ted_multicountry/by_country/IT_china/contracts_2024.json

# Unique Chinese companies
jq -r '.[].chinese_entity' data/processed/ted_multicountry/by_country/IT_china/*.json | sort -u
```

---

## 🚨 CRITICAL FINDINGS LOCATIONS

### Immediate Threats:
```
data/processed/ted_multicountry/risk_assessment/IMMEDIATE_THREATS.json
```
- Critical infrastructure contracts
- Dual-use technology transfers
- High-risk entities

### Subsidiary Networks:
```
data/processed/ted_multicountry/cross_border/subsidiary_networks.json
```
- Shell companies identified
- Parent-subsidiary relationships
- Cross-border operations

### Strategic Patterns:
```
data/processed/ted_multicountry/cross_border/coordinated_campaigns.json
```
- Multi-country synchronized activities
- Market manipulation evidence
- Regional strategies

---

## 📊 MONITORING PROGRESS

### During Processing:
```bash
# Watch progress live
tail -f ted_multicountry_processing.log

# Check checkpoint status
cat data/processed/ted_multicountry/checkpoint.json | jq '.files_processed | length'

# Monitor findings accumulation
watch -n 10 'find data/processed/ted_multicountry -name "*.json" | wc -l'
```

### After Processing:
```bash
# Generate summary
python -c "
import json
from pathlib import Path

checkpoint = json.load(open('data/processed/ted_multicountry/checkpoint.json'))
print(f\"Files processed: {len(checkpoint['files_processed'])}\")
print(f\"Total findings: {checkpoint.get('italy_china_found', 0)}\")

analysis = json.load(open('data/processed/ted_multicountry/analysis/comprehensive_analysis.json'))
print(f\"Countries analyzed: {len(analysis['country_risk_ranking'])}\")
print(f\"Highest risk: {analysis['country_risk_ranking'][0]['name'] if analysis['country_risk_ranking'] else 'N/A'}\")
"
```

---

## 🎯 QUICK REFERENCE

### Finding Italy-China contracts:
```bash
cd data/processed/ted_multicountry/by_country/IT_china/
ls -la
```

### Finding Huawei contracts:
```bash
cd data/processed/ted_multicountry/by_company/huawei/
cat all_contracts.json | jq '. | length'
```

### Finding critical risks:
```bash
cat data/processed/ted_multicountry/risk_assessment/IMMEDIATE_THREATS.json
```

### Finding the main report:
```bash
cat data/processed/ted_multicountry/analysis/MULTI_COUNTRY_ANALYSIS_REPORT.md
```

---

## 💾 BACKUP RECOMMENDATION

After processing completes, backup the entire results directory:
```bash
# Create timestamped backup
tar -czf ted_results_$(date +%Y%m%d_%H%M%S).tar.gz data/processed/ted_multicountry/

# Or copy to backup location
cp -r data/processed/ted_multicountry/ F:/OSINT_Backups/ted_analysis_results/
```

---

*All findings are organized for easy access, with multiple views (by country, by company, by sector) to support different analytical needs. The markdown reports provide human-readable summaries while JSON files contain complete machine-readable data.*
