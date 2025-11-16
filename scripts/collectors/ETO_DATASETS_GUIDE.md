# ETO Datasets Collection System

Complete guide for collecting and monitoring Emerging Technology Observatory (ETO) datasets.

## 📊 Available Datasets

### 1. **Country AI Activity Metrics** (Zenodo - Monthly Updates)
- **DOI**: 10.5281/zenodo.13984221
- **Files**: 9 CSV files (publications, patents, companies)
- **Coverage**: National-level AI metrics for research, patents, and investment
- **Use Case**: Track China's AI capabilities vs. other countries

### 2. **Semiconductor Supply Chain** (GitHub - Periodic Updates)
- **Repository**: georgetown-cset/eto-supply-chain
- **Files**: 5 CSV files (inputs, providers, provision, sequence, stages)
- **Coverage**: Advanced logic chip production supply chain
- **Use Case**: Identify China dependencies in semiconductor manufacturing

### 3. **Cross-Border Tech Research Metrics** (Zenodo - Periodic)
- **DOI**: 10.5281/zenodo.14510656
- **Files**: 1 CSV file
- **Coverage**: International collaboration in AI, robotics, cybersecurity
- **Use Case**: Track China-Europe research partnerships

### 4. **Private-Sector AI Indicators** (Zenodo - Periodic)
- **DOI**: 10.5281/zenodo.14194293
- **Files**: 1 CSV file
- **Coverage**: AI activity for hundreds of companies worldwide
- **Use Case**: Monitor Chinese AI companies in private sector

### 5. **AGORA AI Governance Dataset** (Zenodo - Frequent Updates)
- **DOI**: 10.5281/zenodo.14291866
- **Files**: 2 CSV files (documents + metadata)
- **Coverage**: AI laws, regulations, standards, governance documents
- **Use Case**: Track China AI regulation vs. Europe

### 6. **ETO OpenAlex Overlay** (Zenodo - Periodic)
- **DOI**: 10.5281/zenodo.14237445
- **Files**: 1 CSV file
- **Coverage**: Emerging tech subject classifications for OpenAlex
- **Use Case**: Enhanced classification for our existing OpenAlex data (422GB)

---

## 🚀 Quick Start

### Automated Weekly Collection

**1. Run the setup script (once, as Administrator):**
```batch
cd "C:\Projects\OSINT - Foresight\scripts\collectors"
SETUP_ETO_WEEKLY_SCHEDULER.bat
```

This creates a Windows scheduled task that runs **every Sunday at 9:00 PM**.

**2. The system automatically:**
- Checks each dataset for updates
- Downloads new versions when available
- **Auto-imports data into `F:/OSINT_WAREHOUSE/osint_master.db`**
- Tracks versions via checksums
- Saves reports to `F:/ETO_Datasets/QA/`

**3. Manual run (for testing):**
```batch
run_eto_weekly_collection.bat
```

---

## 📁 Directory Structure

```
F:/ETO_Datasets/
├── downloads/                    # Downloaded dataset files
│   ├── country_ai_metrics/
│   │   └── <version>/           # Version-specific directory
│   │       └── *.csv
│   ├── semiconductor_supply_chain/
│   │   └── <commit>/            # Commit-specific directory
│   │       └── *.csv
│   └── ...
├── MERGED/                       # Consolidated outputs (future)
├── QA/                          # Quality assurance reports
│   └── run_report_*.json
├── logs/                        # Collection logs
│   └── eto_collection_*.log
└── STATE/                       # State management
    ├── eto_state.json          # Tracks versions/checksums
    ├── eto_state.lock          # Lock file for concurrent safety
    └── eto_datasets_config.json # Dataset configuration
```

---

## 🔍 How It Works

### Version Tracking

**Zenodo Datasets:**
- Checks version field in Zenodo API response
- Downloads only if version changed
- Stores checksum for each file

**GitHub Datasets:**
- Checks `pushed_at` timestamp for repository
- Downloads if new commits detected
- Stores commit hash for tracking

### Checksum Verification
- SHA256 checksum calculated for each downloaded file
- Stored in state file for integrity verification
- Prevents re-downloading unchanged files

### State Management
- **Lock file** prevents concurrent runs
- **Atomic saves** prevent state corruption
- **Resumable** if interrupted

---

## 📥 Manual Download (Initial Setup)

If you want to manually download the initial datasets:

### 1. Country AI Activity Metrics
```
https://zenodo.org/records/13984221
→ Download all 9 CSV files
→ Save to: F:/ETO_Datasets/downloads/country_ai_metrics/initial/
```

### 2. Semiconductor Supply Chain
```
https://github.com/georgetown-cset/eto-supply-chain/tree/main/data
→ Download 5 CSV files from /data directory
→ Save to: F:/ETO_Datasets/downloads/semiconductor_supply_chain/initial/
```

### 3. Cross-Border Research
```
https://zenodo.org/records/14510656
→ Download CSV file
→ Save to: F:/ETO_Datasets/downloads/cross_border_research/initial/
```

### 4. Private-Sector AI
```
https://zenodo.org/records/14194293
→ Download CSV file
→ Save to: F:/ETO_Datasets/downloads/private_sector_ai/initial/
```

### 5. AGORA AI Governance
```
https://zenodo.org/records/14291866
→ Download 2 CSV files
→ Save to: F:/ETO_Datasets/downloads/agora_ai_governance/initial/
```

### 6. OpenAlex Overlay
```
https://zenodo.org/records/14237445
→ Download CSV file
→ Save to: F:/ETO_Datasets/downloads/openalex_overlay/initial/
```

---

## 💾 Database Integration

**All downloaded ETO datasets are automatically imported into `F:/OSINT_WAREHOUSE/osint_master.db`.**

### Database Tables Created

**Country AI Metrics** (9 tables):
- `eto_country_ai_publications_yearly` - Yearly article counts by country/field
- `eto_country_ai_publications_citations` - Yearly citation counts
- `eto_country_ai_publications_summary` - Total publications per country/field
- `eto_country_ai_patents_applications` - Yearly patent applications
- `eto_country_ai_patents_granted` - Yearly patents granted
- `eto_country_ai_patents_summary` - Total patents per country/field
- `eto_country_ai_companies_disclosed` - Yearly disclosed investments
- `eto_country_ai_companies_estimated` - Yearly estimated investments
- `eto_country_ai_companies_summary` - Total company investments per country/field

**Semiconductor Supply Chain** (5 tables):
- `eto_semiconductor_inputs` - Supply chain inputs (materials, equipment, processes)
- `eto_semiconductor_providers` - Companies providing inputs
- `eto_semiconductor_provision` - Provider-input relationships with market shares
- `eto_semiconductor_sequence` - Process sequence dependencies
- `eto_semiconductor_stages` - Manufacturing stages

**Other Datasets** (5 tables - schemas ready):
- `eto_cross_border_research` - International research collaborations
- `eto_private_sector_ai` - Private company AI metrics
- `eto_agora_documents` - AI governance documents
- `eto_agora_metadata` - Document metadata
- `eto_openalex_overlay` - Emerging tech labels for OpenAlex works

### Sample Queries

**China AI Safety Publications:**
```sql
SELECT year, article_count
FROM eto_country_ai_publications_yearly
WHERE country = 'China (mainland)' AND field = 'AI Safety'
ORDER BY year DESC;
```

**Semiconductor Providers by Country:**
```sql
SELECT country, COUNT(*) as provider_count
FROM eto_semiconductor_providers
GROUP BY country
ORDER BY provider_count DESC;
```

**China vs. US AI Patent Applications:**
```sql
SELECT country, SUM(application_count) as total_patents
FROM eto_country_ai_patents_applications
WHERE country IN ('China (mainland)', 'United States')
GROUP BY country;
```

---

## 🔄 Integration with Existing Data

### OpenAlex Enhancement
The **ETO OpenAlex Overlay** provides emerging tech classifications for your existing 422GB OpenAlex dataset:
- Add tech domain labels to papers
- Improve Phase 2 (Technology Landscape) analysis
- Cross-reference with our 1.44M arXiv tech papers

### Semiconductor Analysis
The **Semiconductor Supply Chain** dataset complements:
- Phase 3 (Supply Chain Analysis)
- Phase 6 (International Links)
- Cross-reference with patent data

### AI Governance
The **AGORA** dataset enhances:
- Phase 8 (China Strategy Assessment)
- Phase 12 (Foresight Analysis)
- Policy brief preparation

---

## 🛠️ Maintenance

### Check Collection Status
```bash
# View latest state
cat "F:/ETO_Datasets/STATE/eto_state.json"

# View latest log
ls -lt "F:/ETO_Datasets/logs/" | head -1

# View latest report
ls -lt "F:/ETO_Datasets/QA/" | head -1
```

### Force Re-Download
If you need to force re-download a dataset:
1. Edit `F:/ETO_Datasets/STATE/eto_state.json`
2. Remove the dataset entry
3. Run collection again

### Modify Schedule
```batch
# Change to different time (e.g., Saturday 10 PM)
schtasks /change /tn "ETO_Weekly_Collection" /st 22:00 /d SAT

# Disable task
schtasks /change /tn "ETO_Weekly_Collection" /disable

# Enable task
schtasks /change /tn "ETO_Weekly_Collection" /enable

# Delete task
schtasks /delete /tn "ETO_Weekly_Collection" /f
```

---

## 📊 Report Outputs

Each collection run generates:

### Run Report (`QA/run_report_*.json`)
```json
{
  "timestamp": "2025-10-16T10:00:00Z",
  "duration_seconds": 45.2,
  "datasets_checked": 6,
  "updates_found": [
    {
      "dataset_id": "country_ai_metrics",
      "name": "Country AI Activity Metrics",
      "files": 9,
      "timestamp": "2025-10-16T10:00:15Z"
    }
  ],
  "files_downloaded": [
    "F:/ETO_Datasets/downloads/country_ai_metrics/v1.2/publications_yearly_articles.csv",
    ...
  ]
}
```

### State File (`STATE/eto_state.json`)
```json
{
  "version": "1.0",
  "last_check": "2025-10-16T10:00:00Z",
  "datasets": {
    "country_ai_metrics": {
      "version": "1.2",
      "modified": "2025-10-15T14:30:00Z",
      "source": "zenodo",
      "doi": "10.5281/zenodo.13984221",
      "files": {
        "publications_yearly_articles.csv": {
          "checksum": "a1b2c3d4...",
          "downloaded": "2025-10-16T10:00:15Z",
          "size": 1234567,
          "path": "F:/ETO_Datasets/downloads/country_ai_metrics/v1.2/publications_yearly_articles.csv"
        }
      }
    }
  }
}
```

---

## 🔗 ETO Website References

- **Main Site**: https://eto.tech
- **Datasets Page**: https://eto.tech/datasets/
- **Documentation**: https://eto.tech/dataset-docs/
- **Terms of Use**: https://eto.tech/tou

---

## 📝 Citation Requirements

When using ETO datasets, cite as:

```
Emerging Technology Observatory, [Dataset Name],
Georgetown University's Center for Security and Emerging Technology.
Available at: https://eto.tech/datasets/
```

---

## ⚠️ Troubleshooting

### Lock File Issues
If collection fails with "Could not acquire lock":
```bash
# Remove stale lock file
rm "F:/ETO_Datasets/STATE/eto_state.lock"
```

### Zenodo API Rate Limits
- ETO collector respects 2-second delays between requests
- If rate limited, wait and retry

### GitHub API Authentication
For higher rate limits, set GitHub token (optional):
```bash
# Set environment variable
set GITHUB_TOKEN=your_token_here
```

### Missing Dependencies
```bash
pip install requests hashlib
```

---

## 🎯 Next Steps

1. **Run initial manual download** (optional - or let automation handle it)
2. **Set up weekly scheduler** (run `SETUP_ETO_WEEKLY_SCHEDULER.bat`)
3. ✅ **Database integration complete** - Data automatically loads into `osint_master.db`
4. **Cross-reference analysis** (future: link ETO data with OpenAlex, patents, etc. in Phase reports)
5. **Fix Private Sector AI dataset** (currently downloading wrong file - need to investigate)

---

## 📋 Known Issues

### Private Sector AI Dataset
- **Issue**: Collector downloads metaval++ software package instead of CSV data
- **Impact**: No private sector AI data imported yet
- **Status**: Investigating correct download URL from Zenodo

### Cross-Border Research Dataset
- **Issue**: Downloads PDF research paper instead of CSV data
- **Impact**: No cross-border research metrics imported yet
- **Status**: Need to verify if CSV exists or extract from PDF

### AGORA & OpenAlex Overlay
- **Status**: Not yet downloaded (will download on next weekly run if available)

---

**Last Updated**: October 17, 2025
**Maintainer**: OSINT Foresight Project
**Status**: ✅ Production Ready - Auto-Import Active
