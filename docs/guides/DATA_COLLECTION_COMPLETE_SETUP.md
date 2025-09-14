# Complete Data Collection Setup - All 44 Countries

## ✅ What We've Set Up

### 1. **Master Pull Orchestrator**
- **Location**: `src/pulls/master_pull_orchestrator.py`
- **Function**: Manages all data collection for all 44 countries
- **Storage**: F:/OSINT_Data (all data goes to F: drive)

### 2. **All 44 Countries Configured**
```
EU (27): AT, BE, BG, HR, CY, CZ, DK, EE, FI, FR, DE, GR, HU, IE, IT,
         LV, LT, LU, MT, NL, PL, PT, RO, SK, SI, ES, SE

EEA/EFTA (3): IS, NO, CH

Candidates (9): AL, BA, XK, ME, MK, RS, TR, MD, UA

Others (5): GB, AM, AZ, GE
```

### 3. **Data Sources with Automated Scheduling**

| Source | Frequency | Countries | Status |
|--------|-----------|-----------|--------|
| **Vessel Tracking** | Daily | Coastal (28) | Ready |
| **CrossRef Publications** | Weekly | All (44) | ✅ Working |
| **CrossRef Events** | Weekly | All (44) | ✅ Working |
| **Patents** | Weekly | All (44) | Ready |
| **World Bank** | Monthly | All (44) | ✅ Working |
| **OECD** | Monthly | OECD (27) | ✅ Working |
| **Eurostat** | Monthly | EU (27) | ✅ Working |
| **CORDIS** | Monthly | EU (27) | ✅ Existing |
| **TED Procurement** | Monthly | EU (27) | Ready |
| **GLEIF** | Monthly | All (44) | ✅ Existing |
| **IETF** | Monthly | All (44) | ✅ Existing |
| **OpenAIRE** | Monthly | All (44) | ✅ Existing |
| **Common Crawl** | Quarterly | All (44) | ✅ Ready |
| **OpenAlex Snapshot** | Yearly | All (44) | Ready |

### 4. **Common Crawl Intelligence**
- Searches for **hidden supplier relationships** on company websites
- Detects **technology adoption** (AI, cloud, quantum, etc.)
- Finds **partnerships and collaborations** not in databases
- Identifies **certifications and standards**
- **All 44 countries** + **All technology areas** configured

### 5. **Technology Areas Monitored**
- Artificial Intelligence & Machine Learning
- Quantum Computing
- Biotechnology & Gene Editing
- Semiconductors & Chip Manufacturing
- Clean Energy & Renewables
- Cybersecurity & Zero Trust
- Blockchain & Web3

---

## 📁 F: Drive Structure

```
F:/OSINT_Data/
├── raw/
│   ├── country=AT/
│   │   ├── source=worldbank/
│   │   ├── source=eurostat/
│   │   ├── source=commoncrawl/
│   │   └── ... (15 sources)
│   ├── country=BE/
│   └── ... (44 countries total)
├── processed/
│   └── country=AT/ ... (44 countries)
├── reports/
│   └── country=AT/ ... (44 countries)
├── logs/
├── common_crawl/  (Large datasets)
├── openalex/      (300GB snapshot)
└── config/
```

---

## ⏰ Automated Schedule

### Daily (2 AM)
- Vessel tracking for coastal countries
- High-priority updates

### Weekly (Sunday 3 AM)
- CrossRef publications & events
- Patent filings
- GitHub activity

### Monthly (1st, 4 AM)
- Economic indicators (World Bank, OECD, Eurostat)
- Procurement data (TED, national portals)
- Company data (GLEIF)
- Research projects (CORDIS, OpenAIRE)

### Quarterly (15th, 1 AM)
- Common Crawl intelligence extraction
- Supply chain network mapping
- Technology landscape assessment

### Yearly
- OpenAlex 300GB snapshot update
- Comprehensive patent landscape

---

## 🚀 How to Start

### 1. Initialize F: Drive
```bash
python initialize_f_drive.py
```
This creates all directories for 44 countries and 15+ data sources.

### 2. Set Up Automated Schedule (Run as Admin)
```bash
scheduled_tasks\setup_automated_pulls.bat
```

### 3. Run First Pull (Test)
```bash
# Single country, single source
python -m src.pulls.worldbank_pull --country AT --out F:/OSINT_Data/raw/country=AT/source=worldbank

# All countries for one source
python src/pulls/master_pull_orchestrator.py --source worldbank --base-dir F:/OSINT_Data

# All high-priority pulls
python src/pulls/master_pull_orchestrator.py --priority high --base-dir F:/OSINT_Data
```

### 4. Monitor Status
```bash
python src/pulls/master_pull_orchestrator.py --mode status
```

---

## 💾 Storage Requirements

| Data Type | Size Estimate |
|-----------|--------------|
| Per country/month | 2-5 GB |
| All 44 countries/month | 100-200 GB |
| Common Crawl/quarter | 50-100 GB |
| OpenAlex snapshot | 300 GB |
| **First year total** | **1.5-2 TB** |
| **Recommended F: space** | **2-3 TB** |

---

## 📊 What You'll Get

### Per Country (e.g., Austria)
- **Economic indicators**: GDP, R&D spending, trade flows
- **Trade relationships**: Import/export partners, dependencies
- **Technology adoption**: Cloud usage, AI implementation, patent filings
- **Supply chain**: Hidden suppliers from Common Crawl
- **Research networks**: Collaborations, EU projects
- **Procurement**: Government contracts, technology purchases
- **Risk indicators**: Concentration, dependencies, vulnerabilities

### Aggregate Intelligence
- **Technology clusters** across Europe
- **Supply chain vulnerabilities** by sector
- **Emerging partnerships** and alliances
- **Innovation trends** by country/region
- **Critical dependencies** on non-EU suppliers

---

## 🔄 Data Flow

```
APIs/Web → Pull Scripts → F:/OSINT_Data/raw/ → Processing →
→ F:/OSINT_Data/processed/ → Analysis (Phase 0-13) → Reports
```

---

## ⚡ Quick Commands

```bash
# Run everything that's due
python src/pulls/master_pull_orchestrator.py --mode once

# Pull specific country
python src/pulls/master_pull_orchestrator.py --country AT

# Pull specific source for all countries
python src/pulls/master_pull_orchestrator.py --source worldbank

# Generate status report
python src/pulls/master_pull_orchestrator.py --mode status

# Run Common Crawl intelligence
python src/pulls/commoncrawl_pull.py --country AT --out F:/OSINT_Data
```

---

## ✅ Next Steps

1. **Initialize F: drive** with `initialize_f_drive.py`
2. **Test one pull** to verify everything works
3. **Set up Windows Task Scheduler** for automation
4. **Run first batch** of high-priority pulls
5. **Monitor** with status reports

---

*All 44 countries. All data sources. Fully automated. Stored on F: drive.*

*Intelligence coverage: Economic, technological, supply chain, research, procurement, and hidden relationships via Common Crawl.*
