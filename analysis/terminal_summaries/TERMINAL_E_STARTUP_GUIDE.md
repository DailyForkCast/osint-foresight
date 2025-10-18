# 🎯 TERMINAL E STARTUP GUIDE
## Strategic Gap EU Countries Collection

**Your Assignment:** Terminal E - Strategic Gap Countries
**Countries:** AT (Austria), BG (Bulgaria), GR (Greece), IE (Ireland), PT (Portugal)
**Mission:** Complete EU coverage for critical missing members with China exposure

---

## 📚 ESSENTIAL READING FIRST

1. **Master Warehouse Guide:** `C:/Projects/OSINT - Foresight/MASTER_SQL_WAREHOUSE_GUIDE.md`
   - CRITICAL: Follow exact schema specifications
   - Warehouse location: `F:/OSINT_WAREHOUSE/osint_research.db`
   - Use standardized China detection functions

2. **Terminal A Success Document:** `C:/Projects/OSINT - Foresight/TERMINAL_A_SUMMARY.md`
   - Learn from proven methodology
   - Critical OpenAIRE API fix documented
   - 14.2% China collaboration rate achieved

3. **Terminal Coordination Guide:** `C:/Projects/OSINT - Foresight/KNOWLEDGE_BASE/05_TECHNICAL_GUIDES/TERMINAL_COORDINATION_GUIDE.md`
   - Standard operating procedures
   - Quality control metrics
   - Integration patterns

---

## 🚀 YOUR IMMEDIATE TASKS

### 1. Create Terminal E Collector Script
Base it on: `scripts/terminal_a_eu_major_collector.py`

**Critical Changes Needed:**
```python
# Your countries (alphabetized)
self.countries = ['AT', 'BG', 'GR', 'IE', 'PT']

# OpenAIRE API fix (MUST INCLUDE):
for result_id, result_content in data['results'].items():
    # result_content is string, not object
    china_score = self.detect_china_involvement(result_content)
```

### 2. Priority Intelligence Targets (Alphabetized)

**Austria (AT):**
- Central European technology hub
- Research collaborations via universities
- Industrial partnerships

**Bulgaria (BG):**
- Black Sea access
- Energy corridor
- Nuclear power cooperation

**Greece (GR) - HIGHEST PRIORITY:**
- Piraeus Port (COSCO Chinese operation)
- Belt & Road Initiative member
- Energy infrastructure investments
- Documented Piraeus Port COSCO operation

**Ireland (IE):**
- Tech multinationals hub
- Pharmaceutical research
- Data centers

**Portugal (PT):**
- Atlantic gateway strategic position
- Energy sector (EDP sold stake to China)
- Golden visa program participants

---

## 💾 DATA SOURCES AVAILABLE

### Already Collected (Use These):
1. **CORDIS Projects:** `C:/Projects/OSINT - Foresight/data/raw/source=cordis/`
   - Filter by your countries
   - Filter by country codes for actual data

2. **OpenAlex Academic:** `F:/OSINT_Backups/openalex/data/`
   - 422GB available
   - Use institution country filters

3. **TED Procurement:** `F:/TED_Data/monthly/`
   - Search for Chinese vendors in your countries
   - Huawei, ZTE, CRRC key targets

4. **Fresh Intelligence (Sept 22):**
   - GLEIF: `F:/OSINT_Data/GLEIF/` (1,750 Chinese entities)
   - OpenSanctions: `F:/OSINT_Data/OpenSanctions/` (2,293 Chinese entities)

### APIs to Attempt:
1. **OpenAIRE** (currently rate-limited but structure fixed)
2. **CORDIS** (working well)
3. **Patent databases** (if authentication available)

---

## 📊 WAREHOUSE INTEGRATION

### Database Connection:
```python
import sqlite3
warehouse_path = "F:/OSINT_WAREHOUSE/osint_research.db"
conn = sqlite3.connect(warehouse_path)
```

### Required Tables:
- `core_f_collaboration` - Research collaborations
- `core_f_publication` - Academic papers
- `core_f_procurement` - Government contracts
- `core_dim_organization` - Entity information
- `research_session` - Your session logging

### Integration Pattern:
```python
# Always use INSERT OR REPLACE
conn.execute("""
    INSERT OR REPLACE INTO core_f_collaboration (
        collab_id, project_name, has_chinese_partner,
        china_collaboration_score, source_system, confidence_score
    ) VALUES (?, ?, ?, ?, ?, ?)
""", (id, name, has_china, china_score, 'Terminal_E', 0.95))
```

---

## 📝 DOCUMENTATION REQUIREMENTS

### 1. Create Your Summary Document:
`C:/Projects/OSINT - Foresight/TERMINAL_E_SUMMARY.md`

Include:
- Countries processed
- China collaboration rates per country
- Key findings (especially Greece/Piraeus)
- Problems encountered
- Recommendations

### 2. Update Master README:
`C:/Projects/OSINT - Foresight/README.md`

Add Terminal E section showing:
- Completion status
- Key metrics
- Fresh intelligence gathered

### 3. Log Sessions:
Every collection must be logged in `research_session` table

---

## 🎯 SUCCESS METRICS

### Minimum Targets:
- **China Detection Rate:** >5% (Terminal A achieved 14.2%)
- **Greece Special Focus:** Piraeus Port COSCO operation documented
- **Data Quality:** 95% confidence scores
- **Zero Fabrication:** Full source traceability

### Expected Outputs:
- Actual data collection only - no fabricated minimums
- Complete warehouse integration following schema
- Full documentation with source verification
- Zero fabrication policy enforced

---

## ⚠️ CRITICAL WARNINGS

1. **OpenAIRE API:** Returns dict not list - use fixed parsing
2. **Rate Limiting:** 1-2 second delays between API calls
3. **Greece Priority:** Focus extra effort on Greek-China connections
4. **Schema Compliance:** Follow warehouse guide exactly

---

## 🚀 QUICK START COMMANDS

```bash
# 1. Navigate to project
cd "C:/Projects/OSINT - Foresight"

# 2. Create your collector script
cp scripts/terminal_a_eu_major_collector.py scripts/terminal_e_gap_collector.py

# 3. Edit countries list and run
python scripts/terminal_e_gap_collector.py

# 4. Monitor warehouse
python -c "import sqlite3; conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_research.db'); cursor = conn.execute('SELECT source_system, COUNT(*) FROM core_f_collaboration GROUP BY source_system'); print(cursor.fetchall())"
```

---

## 📞 COORDINATION

- Terminal A: ✅ Complete (Major EU)
- Terminal B: 🔄 Eastern Europe
- Terminal C: 🔄 Nordic/Baltic
- Terminal D: 🔄 Smaller EU
- **Terminal E:** 🎯 Your mission - Strategic gaps
- Terminal F: Next phase - Non-EU strategic

Your Terminal E collection fills critical intelligence gaps, especially Greece's Belt & Road participation and Portugal's energy connections. Focus on quality over quantity, particularly for Greece's Piraeus port operations.

**START WITH GREECE** - Document the COSCO Piraeus Port operation and other verifiable China connections.
