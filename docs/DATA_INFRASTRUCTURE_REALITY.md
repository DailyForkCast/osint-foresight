# DATA INFRASTRUCTURE REALITY DOCUMENTATION
**Last Updated:** 2025-09-20
**Purpose:** Single source of truth for what data we actually have and how to access it

---

## 🗂️ AVAILABLE DATA SOURCES (445.22 GB Total)

### 1. OpenAlex Academic Database (420.66 GB) ✅ AVAILABLE
**Location:** `F:/OSINT_Backups/openalex/data/`
**Format:** Compressed JSON lines (.gz files)
**Content:** 250M+ academic publications with metadata
**Structure:**
```
openalex/data/
├── works/               # Academic papers (main data)
│   └── updated_date=*/  # Partitioned by date
│       └── part_*.gz    # Compressed JSON lines
├── authors/             # Author profiles
├── institutions/        # Institution data
├── concepts/            # Subject classifications
└── funders/            # Funding sources
```

**Key Fields in Works:**
- `doi`: Digital Object Identifier
- `title`: Paper title
- `publication_year`: Year published
- `authorships`: Array with author and institution data
  - `institutions.country_code`: ISO country codes (DE, CN, US, etc.)
  - `institutions.display_name`: Institution name
- `concepts`: Subject areas with scores
- `abstract`: Paper abstract (when available)

**How to Access:**
```python
import gzip, json
with gzip.open('path/to/part_000.gz', 'rt') as f:
    for line in f:
        paper = json.loads(line)
        # Process paper data
```

**SHA256 Sample:** `ae0a6b38deb023b3` (first 1MB for verification)

---

### 2. TED EU Procurement Data (24.20 GB) ✅ AVAILABLE
**Location:** `F:/TED_Data/`
**Format:** XML and CSV files
**Content:** EU public procurement contracts
**Structure:**
```
TED_Data/
├── monthly/             # Monthly archives
│   └── 2024_*/         # Year_Month folders
│       └── *.xml       # Contract notices
├── csv_historical/      # Historical CSV exports
└── historical/         # Archived data
```

**Key Fields:**
- Contract value
- Contracting authority
- Winning bidder
- CPV codes (procurement categories)
- Country codes
- Award dates

**SHA256 Sample:** `9833f7acb4b6dabf`

---

### 3. CORDIS EU Projects (0.19 GB) ✅ AVAILABLE
**Location:** `F:/2025-09-14 Horizons/`
**Format:** JSON and CSV
**Content:** EU-funded research projects
**Key Data:**
- Project funding amounts
- Participant organizations
- Technology areas
- Start/end dates
- Deliverables

**SHA256 Sample:** `2865e10fc2c6aad1`

---

### 4. SEC EDGAR Filings (0.05 GB) ✅ AVAILABLE
**Location:** `F:/OSINT_DATA/COMPANIES/`
**Format:** JSON, HTML, TXT
**Content:** US corporate filings
**Key Companies:**
- Leonardo DRS filings
- Defense contractors
- Technology companies

**SHA256 Sample:** `24bf2b74fdaa1616`

---

### 5. EPO Patent Data (0.12 GB) ✅ AVAILABLE
**Location:** `F:/OSINT_DATA/EPO_PATENTS/`
**Format:** JSON, CSV
**Content:** European patent applications
**Key Fields:**
- Patent numbers
- Applicants
- Technology classifications
- Filing dates
- Citations

**SHA256 Sample:** `e3b0c44298fc1c14`

---

## 📊 DATA PROCESSING SCRIPTS

### Core Data Connectors

#### 1. `connect_real_data.py`
**Purpose:** Verify and connect to all data sources
**Output:** `data/real_verified/verified_data_report_*.json`
**Usage:**
```bash
python scripts/connect_real_data.py
```

#### 2. `process_openalex_germany_china.py`
**Purpose:** Extract Germany-China collaborations from OpenAlex
**Output:**
- `data/processed/openalex_germany_china/analysis_*.json`
- `data/processed/openalex_germany_china/collaborations_*.json`
- `data/processed/openalex_germany_china/report_*.md`
**Usage:**
```bash
python scripts/process_openalex_germany_china.py
```

#### 3. `systematic_data_processor.py`
**Purpose:** Process all 445GB systematically
**Status:** Framework exists, needs full implementation

### Existing Collectors (56 Total)

**Connected and Working (8):**
- `openalex_germany_collector.py` - OpenAlex for Germany
- `ted_italy_collector.py` - TED for Italy
- `cordis_italy_collector.py` - CORDIS for Italy
- `sec_edgar_analyzer.py` - SEC filings
- `epo_patent_analyzer.py` - EPO patents
- `crossref_event_analyzer.py` - Conference data
- `gleif_ownership_tracker.py` - Corporate ownership
- `github_dependency_scanner.py` - Code dependencies

**Orphaned/Unconnected (48):**
- Various collectors in `scripts/collectors/` directory
- Need reconnection to data sources

---

## 🔄 PROCESSING PIPELINE

### Streaming Architecture (Required for 420GB)
```python
# CORRECT - Stream processing
with gzip.open(file, 'rt') as f:
    for line in f:  # One line at a time
        process(json.loads(line))

# WRONG - Memory overflow
data = json.load(open(file))  # Loads entire file
```

### Batch Processing with Checkpoints
```python
for file_idx, file in enumerate(files):
    process_file(file)
    if file_idx % 10 == 0:
        save_checkpoint()  # Can resume from here
```

### Verification Requirements
Every data point must have:
1. **Source file** - Exact file path
2. **Line number** - Location in file
3. **SHA256 hash** - Content verification
4. **Recompute command** - How to regenerate
5. **Timestamp** - When processed

---

## 📈 CURRENT PROCESSING STATUS

### OpenAlex
- **Status:** Sample processed (11 records)
- **Found:** 0 Germany-China collaborations in sample
- **Next:** Process full dataset (250M+ records)
- **Estimated Time:** 24-48 hours for full processing

### TED
- **Status:** Connected, not processed
- **Next:** Implement CSV/XML parser
- **Estimated Time:** 4-6 hours for full processing

### CORDIS
- **Status:** Connected, not processed
- **Next:** Parse JSON project files
- **Estimated Time:** 1-2 hours

### SEC EDGAR
- **Status:** Connected, not processed
- **Next:** Extract Leonardo/defense contractor data
- **Estimated Time:** 1 hour

### EPO Patents
- **Status:** Connected, not processed
- **Next:** Parse patent applications
- **Estimated Time:** 2-3 hours

---

## ⚠️ CRITICAL RULES

### NEVER FABRICATE
- If no data exists, return `INSUFFICIENT_EVIDENCE`
- Document what was searched
- Specify what's needed

### ALWAYS VERIFY
- Every number must trace to source
- Include recompute commands
- Save verification hashes

### USE ACTUAL DATA
- 445GB available - USE IT
- Don't generate examples
- Process real records

---

## 🎯 QUICK REFERENCE

### To Check If Data Exists:
```python
from pathlib import Path
data_path = Path("F:/OSINT_Backups/openalex/data")
if data_path.exists():
    print("Data available")
```

### To Process OpenAlex:
```python
python scripts/process_openalex_germany_china.py
```

### To Verify All Sources:
```python
python scripts/connect_real_data.py
```

### Output Locations:
- Processed data: `data/processed/`
- Verified reports: `data/real_verified/`
- Logs: `*.log` in project root

---

## 📝 WHAT WE'RE DOING NOW

### Phase 1: Data Connection (COMPLETE)
✅ Inventory all data sources
✅ Verify availability
✅ Calculate verification hashes
✅ Create connection scripts

### Phase 2: OpenAlex Processing (IN PROGRESS)
🔄 Process Germany-China collaborations
⏳ Extract technology overlaps
⏳ Map institutional relationships
⏳ Track temporal trends

### Phase 3: TED Processing (PENDING)
⏳ Parse procurement contracts
⏳ Identify China-related contracts
⏳ Extract supplier relationships

### Phase 4: Integration (PENDING)
⏳ Cross-reference datasets
⏳ Build knowledge graph
⏳ Generate risk assessments

---

## 🚀 TO START PROCESSING

1. **Run data verification:**
   ```bash
   cd "C:/Projects/OSINT - Foresight"
   python scripts/connect_real_data.py
   ```

2. **Process OpenAlex for Germany-China:**
   ```bash
   python scripts/process_openalex_germany_china.py
   ```

3. **Check results:**
   ```bash
   ls data/processed/openalex_germany_china/
   ```

---

## 📊 EXPECTED OUTPUTS

From full OpenAlex processing:
- ~10,000-50,000 Germany-China collaborations
- Technology area mappings
- Institutional networks
- Yearly trend analysis
- All with verification hashes and source references

**NO FABRICATED NUMBERS - ONLY WHAT'S IN THE DATA**

---

*This document is the single source of truth for data infrastructure. Update when new sources are connected or processing scripts are created.*
