# TED EU PROCUREMENT DATA - COMPLETE PROCESSING PLAN
**Date:** 2025-09-20
**Data Size:** 25GB
**Priority:** HIGHEST
**Focus:** Italy-China procurement relationships and dual-use technology

---

## 📊 DATA OVERVIEW

### Structure:
```
F:/TED_Data/
├── monthly/           # 25GB - Main data (2006-2025)
│   ├── 2006/         # ~1GB per year average
│   ├── ...
│   └── 2025/         # Partial year
├── csv_historical/    # Historical CSV exports
└── historical/        # Archived data
```

### Format:
- **Monthly archives:** `TED_monthly_YYYY_MM.tar.gz` (~200-300MB compressed each)
- **Content:** XML contract notices
- **Years available:** 2006-2025 (20 years)
- **Estimated files:** ~240 monthly archives (20 years × 12 months)

---

## 🎯 SEARCH OBJECTIVES

### Primary Targets:
1. **Italy-China Direct Contracts**
   - Italian government/entities awarding to Chinese companies
   - Chinese entities participating in Italian tenders

2. **Dual-Use Technology Contracts**
   - Telecommunications equipment
   - Semiconductors/electronics
   - Advanced materials
   - Aerospace components
   - Nuclear technology
   - AI/Computing infrastructure

3. **Critical Infrastructure**
   - Energy (especially renewable)
   - Transportation (rail, ports)
   - Telecommunications (5G)
   - Healthcare technology

4. **Key Italian Entities to Track:**
   - Leonardo S.p.A.
   - ENI
   - Enel
   - TIM (Telecom Italia)
   - Italian government ministries
   - Regional governments

5. **Key Chinese Entities to Track:**
   - Huawei
   - ZTE
   - State-owned enterprises
   - CRRC (rail)
   - State Grid Corporation
   - Any company with "China" in name

---

## 🏗️ PROCESSING ARCHITECTURE

### Script: `process_ted_procurement.py`

```python
class TEDProcessor:
    """
    Streaming processor for 25GB TED procurement data
    """

    def __init__(self):
        self.checkpoint_file = "data/processed/ted/checkpoint.json"
        self.output_dir = "data/processed/ted/"
        self.temp_dir = "data/temp/ted_extraction/"

        # Search patterns
        self.italy_patterns = ["Italy", "Italia", "Italian", "IT"]
        self.china_patterns = ["China", "Chinese", "CN", "Huawei", "ZTE"]

        # Technology keywords
        self.tech_keywords = {
            "telecom": ["5G", "telecommunication", "network"],
            "semiconductor": ["chip", "semiconductor", "microelectronics"],
            "nuclear": ["nuclear", "reactor", "uranium"],
            "aerospace": ["satellite", "spacecraft", "aerospace"],
            "ai": ["artificial intelligence", "AI", "machine learning"],
            "renewable": ["solar", "wind", "renewable", "photovoltaic"]
        }

    def process_monthly_archive(self, archive_path):
        """Process single monthly tar.gz file"""
        # 1. Extract to temp directory
        # 2. Parse XML files
        # 3. Search for Italy-China connections
        # 4. Extract contract details
        # 5. Save findings
        # 6. Update checkpoint
        # 7. Clean temp files

    def extract_contract_details(self, xml_content):
        """Extract key fields from TED XML"""
        return {
            "contract_id": "",
            "title": "",
            "contracting_authority": "",
            "country": "",
            "winners": [],
            "value": "",
            "currency": "",
            "cpv_codes": [],  # Common Procurement Vocabulary
            "date": "",
            "description": "",
            "technology_flags": []
        }
```

---

## 📋 IMPLEMENTATION PHASES

### Phase 1: Infrastructure Setup (2 hours)
```python
# 1. Create processing directories
data/processed/ted/
├── contracts/          # Individual contracts
├── summaries/          # Monthly summaries
├── italy_china/       # Filtered results
├── technology/         # Tech-specific findings
└── checkpoint.json    # Resume capability

# 2. Implement checkpoint system
checkpoint = {
    "last_year": 2024,
    "last_month": 1,
    "last_file": "TED_monthly_2024_01.tar.gz",
    "files_processed": [],
    "contracts_found": 0,
    "italy_china_found": 0,
    "processing_time": 0
}

# 3. Setup logging
import logging
logging.basicConfig(
    filename='ted_processing.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
```

### Phase 2: Core Processing Logic (4 hours)
```python
def process_all_ted_data():
    """Main processing function with checkpoint support"""

    # Load checkpoint if exists
    checkpoint = load_checkpoint()

    # Get list of all archives
    archives = get_all_archives()  # ~240 files

    # Resume from checkpoint
    start_index = find_checkpoint_position(checkpoint, archives)

    for archive in archives[start_index:]:
        try:
            # Process with streaming
            process_monthly_archive(archive)

            # Update checkpoint every file
            update_checkpoint(archive)

            # Save intermediate results every 10 files
            if processed_count % 10 == 0:
                save_intermediate_results()

        except Exception as e:
            logging.error(f"Error processing {archive}: {e}")
            continue
```

### Phase 3: Search Implementation (3 hours)
```python
def search_italy_china_connections(contract):
    """Identify Italy-China procurement relationships"""

    findings = {
        "is_italy_china": False,
        "direction": None,  # "IT->CN" or "CN->IT"
        "confidence": 0.0,
        "evidence": []
    }

    # Check contracting authority
    if is_italian(contract["contracting_authority"]):
        # Check winners for Chinese companies
        for winner in contract["winners"]:
            if is_chinese(winner):
                findings["is_italy_china"] = True
                findings["direction"] = "IT->CN"
                findings["evidence"].append(f"Italian authority: {contract['contracting_authority']}")
                findings["evidence"].append(f"Chinese winner: {winner}")

    # Check for technology indicators
    tech_score = calculate_tech_relevance(contract)
    if tech_score > 0.7:
        findings["technology_relevant"] = True
        findings["tech_categories"] = identify_tech_categories(contract)

    return findings
```

### Phase 4: Parallel Processing (2 hours)
```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def parallel_process_ted():
    """Process multiple years in parallel"""

    # Group by year for parallel processing
    years = range(2006, 2026)

    # Use number of cores - 1
    num_workers = multiprocessing.cpu_count() - 1

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for year in years:
            future = executor.submit(process_year, year)
            futures.append(future)

        # Collect results
        for future in futures:
            year_results = future.result()
            merge_results(year_results)
```

---

## 🔄 PROCESSING WORKFLOW

### Step-by-Step Execution:
```bash
# 1. Test with single file first
python process_ted_procurement.py --test --file "F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz"

# 2. Process recent data first (most relevant)
python process_ted_procurement.py --years 2023,2024,2025

# 3. Process historical data
python process_ted_procurement.py --years 2020-2022

# 4. Complete processing
python process_ted_procurement.py --all

# 5. Generate reports
python process_ted_procurement.py --report
```

---

## 📊 EXPECTED OUTPUTS

### 1. Contract Database
```json
{
    "contract_id": "TED-2024-000123",
    "date": "2024-01-15",
    "title": "Supply of telecommunications equipment",
    "contracting_authority": {
        "name": "Ministero delle Infrastrutture",
        "country": "IT"
    },
    "winners": [
        {
            "name": "Huawei Technologies Italia",
            "country": "CN",
            "parent": "Huawei Technologies Co Ltd"
        }
    ],
    "value": 45000000,
    "currency": "EUR",
    "cpv_codes": ["32400000"],
    "technology_categories": ["telecommunications", "5G"],
    "risk_flags": ["dual_use", "critical_infrastructure"]
}
```

### 2. Summary Statistics
```json
{
    "total_contracts": 2500000,
    "italy_contracts": 125000,
    "italy_china_contracts": 342,
    "total_value_italy_china": 1250000000,
    "top_chinese_winners": [...],
    "top_sectors": [...],
    "temporal_trend": {...}
}
```

### 3. Risk Assessment Report
- High-risk technology transfers
- Critical infrastructure dependencies
- Temporal patterns (increase/decrease)
- Geographic distribution

---

## ⏱️ TIME ESTIMATES

### Processing Speed Estimates:
- **Extraction:** ~10 seconds per archive
- **Parsing:** ~100 contracts/second
- **Search:** ~1000 contracts/second
- **Total time:** ~8-10 hours for complete processing

### Optimization Options:
1. **Parallel processing:** Reduce to 2-3 hours with 4 cores
2. **Skip non-relevant years:** Focus on 2018-2025 (post-BRI)
3. **Filter by CPV codes:** Only technology-relevant categories

---

## 🚨 CRITICAL SEARCH PATTERNS

### Must-Find Entities:
```python
CRITICAL_CHINESE_COMPANIES = [
    "Huawei",
    "ZTE",
    "China Railway",
    "CRRC",
    "State Grid",
    "China National Nuclear",
    "China Aerospace",
    "Lenovo",
    "Xiaomi",
    "BYD",
    "CATL"
]

CRITICAL_ITALIAN_ENTITIES = [
    "Leonardo",
    "ENI",
    "Enel",
    "TIM",
    "Ferrovie dello Stato",
    "Autostrade per l'Italia",
    "A2A",
    "Terna"
]

DUAL_USE_CPV_CODES = [
    "32400000",  # Telecommunications
    "31700000",  # Electronic equipment
    "35100000",  # Emergency and security equipment
    "38000000",  # Laboratory equipment
    "30200000",  # Computer equipment
]
```

---

## 📈 VALIDATION APPROACH

### Every Finding Must Have:
1. **Source file:** Exact tar.gz archive
2. **Contract ID:** TED reference number
3. **XML path:** Location within archive
4. **Verification command:**
```bash
tar -xzf [archive] -O [xml_file] | grep -A10 -B10 "China"
```
5. **Confidence score:** Based on name matching accuracy
6. **Recompute ability:** Script to re-extract specific contract

---

## 🎯 IMMEDIATE FIRST STEPS

### Today's Actions:
1. **Create directory structure** (5 minutes)
2. **Write basic extraction script** (30 minutes)
3. **Test on 2024 January data** (10 minutes)
4. **Implement Italy-China search** (1 hour)
5. **Process 2024 completely** (1 hour)
6. **Generate initial findings report** (15 minutes)

### Commands to Run Now:
```bash
# 1. Create directories
mkdir -p data/processed/ted/{contracts,summaries,italy_china,technology}

# 2. Test extraction
tar -tzf "F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz" | head -20

# 3. Count files in archive
tar -tzf "F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz" | wc -l

# 4. Extract and search sample
tar -xzf "F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz" --to-stdout | grep -i "china\|huawei" | head -10
```

---

## ✅ SUCCESS METRICS

The TED processing will be considered successful when:
1. ✓ All 25GB processed (240 archives)
2. ✓ Italy-China contracts identified with full details
3. ✓ Technology categories classified
4. ✓ Temporal patterns analyzed
5. ✓ Risk assessment completed
6. ✓ All findings traceable to source
7. ✓ Checkpoint system enables resumability
8. ✓ Zero fabrication - only actual contracts

---

*This plan provides a complete roadmap for processing all TED data with focus on Italy-China procurement relationships.*
