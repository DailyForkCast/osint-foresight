# 🌐 TERMINAL F STARTUP GUIDE
## Non-EU Strategic Countries Collection

**Your Assignment:** Terminal F - Associated & Candidate Countries
**Priority Countries:** CH (Switzerland), NO (Norway), RS (Serbia), TR (Turkey), UA (Ukraine)
**Mission:** Capture China's influence in EU periphery and strategic partners

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

---

## 🎯 YOUR STRATEGIC TARGETS (Alphabetized with Priority Notes)

### Switzerland (CH) - FINANCIAL HUB [Priority 4]
**Why Critical:**
- Global financial center
- Research excellence (CERN, ETH)
- Pharma/biotech hub
- Neutral meeting ground

**Intelligence Focus:**
- Financial flows
- Research collaborations
- Pharmaceutical partnerships
- Technology innovation

### Norway (NO) - ENERGY SUPPLIER [Priority 3]
**Why Critical:**
- Critical EU energy supplier
- Arctic gateway
- Advanced technology sector
- Sovereign wealth fund investments

**Intelligence Focus:**
- Energy infrastructure
- Arctic research cooperation
- Maritime technology
- Green energy partnerships

### Serbia (RS) - HIGHEST CHINA EXPOSURE [Priority 1 - START HERE]
**Why Critical:**
- China's primary Balkans hub
- Hesteel Smederevo (largest investment)
- Zijin Mining copper operations
- Highway/railway construction by Chinese firms
- Documented Chinese investments to verify

**Intelligence Focus:**
- Infrastructure projects
- Mining and steel industry
- Technology partnerships
- Financial investments

### Turkey (TR) - EURASIAN BRIDGE [Priority 2]
**Why Critical:**
- Belt & Road Initiative member
- Nuclear power plant cooperation
- Major trade corridor
- Strategic military partnerships

**Intelligence Focus:**
- Energy sector (nuclear, coal)
- Infrastructure (bridges, tunnels)
- Defense industry cooperation
- Technology transfer

### Ukraine (UA) - GEOPOLITICAL PIVOT [Priority 5]
**Why Critical:**
- Motor Sich attempted acquisition
- Agricultural investments
- Pre-war infrastructure projects
- Strategic location

**Intelligence Focus:**
- Historical collaborations (pre-2022)
- Agricultural sector
- Technology partnerships
- Infrastructure projects

---

## 🚀 YOUR IMMEDIATE TASKS

### 1. Create Terminal F Collector Script
Base it on: `scripts/terminal_a_eu_major_collector.py`

**Critical Changes:**
```python
# Your priority countries (alphabetized)
self.countries = ['CH', 'NO', 'RS', 'TR', 'UA']

# Additional non-priority if time permits (alphabetized)
self.additional = ['AL', 'BA', 'GE', 'IS', 'LI', 'MD', 'ME', 'MK', 'XK']

# OpenAIRE API fix (MUST INCLUDE):
for result_id, result_content in data['results'].items():
    china_score = self.detect_china_involvement(result_content)
```

### 2. Special Considerations

**Serbia-Specific Keywords:**
```python
serbia_china_keywords = [
    'Hesteel', 'Smederevo', 'Zijin', 'Bor',
    'CRBC', 'Mihajlo Pupin', 'Shandong Linglong',
    'China Road and Bridge Corporation'
]
```

**Turkey-Specific Keywords:**
```python
turkey_china_keywords = [
    'Akkuyu', 'ICBC Turkey', 'Bank of China Turkey',
    'Huawei Turkey', 'ZTE Turkey', 'BYD', 'Sinosure'
]
```

---

## 💾 DATA SOURCES AVAILABLE

### Use Existing Collections:
1. **CORDIS Projects:** May have limited non-EU data
2. **OpenAlex Academic:** Full coverage for all countries
3. **TED Procurement:** Some non-EU tenders included
4. **GLEIF/OpenSanctions:** Global coverage

### Special Sources for Non-EU:
1. **Serbia:**
   - National statistics office (stat.gov.rs)
   - Development agency (ras.gov.rs)

2. **Turkey:**
   - Investment office (invest.gov.tr)
   - TÜBITAK research council

3. **Norway:**
   - Research Council (forskningsradet.no)
   - Innovation Norway

4. **Switzerland:**
   - SNSF research database
   - Federal statistics

---

## 📊 DATA COLLECTION TARGETS

### Based on Terminal A Results:
- **Terminal A Achievement:** 14.2% China collaboration rate (major EU countries)
- **Baseline Target:** >5% China detection rate (warehouse guide minimum)
- **No predictions** - will measure actual data only
- **Zero fabrication** - only verified findings will be reported

### Known Facts to Document:
- **Serbia:** Hesteel Smederevo steel plant (verified Chinese ownership)
- **Serbia:** Zijin Mining copper operations (verified)
- **Turkey:** Belt & Road Initiative member (documented)
- **All countries:** Focus on verifiable data with full source traceability

---

## 📝 DOCUMENTATION REQUIREMENTS

### 1. Create Your Summary:
`C:/Projects/OSINT - Foresight/TERMINAL_F_SUMMARY.md`

**Special Sections Needed:**
- Serbia deep dive (Hesteel, Zijin details)
- Turkey strategic assessment
- Non-EU vs EU comparison
- Geopolitical implications

### 2. Update Knowledge Base:
Add findings to: `KNOWLEDGE_BASE/07_DATA_SOURCES/`

### 3. Create Strategic Brief:
`C:/Projects/OSINT - Foresight/NON_EU_CHINA_STRATEGIC_BRIEF.md`

---

## ⚠️ SPECIAL WARNINGS

### Data Availability Issues:
- Non-EU countries have less standardized data
- Some APIs won't cover these countries
- May need alternative collection methods

### Political Sensitivities:
- Ukraine data: Focus on pre-2022 period
- Turkey: NATO member but complex China relationship
- Serbia: EU candidate but strong China ties

### Quality Over Quantity:
- Focus on verifiable data
- Each finding must have source documentation
- Document context thoroughly

---

## 🎯 SUCCESS METRICS

### Minimum Targets:
- **Serbia:** Must capture Hesteel, Zijin, infrastructure
- **Turkey:** Energy and infrastructure partnerships
- **Overall Detection Rate:** >10% average
- **Strategic Intelligence:** Quality over quantity

### Bonus Objectives:
- Map Serbia's complete China dependency
- Identify Turkey's technology transfer patterns
- Document Norway's Arctic cooperation
- Track Swiss financial flows
- Historical Ukraine partnerships

---

## 🚀 QUICK START COMMANDS

```bash
# 1. Navigate to project
cd "C:/Projects/OSINT - Foresight"

# 2. Create collector for non-EU
cp scripts/terminal_a_eu_major_collector.py scripts/terminal_f_strategic_collector.py

# 3. Modify for your countries and run
# START WITH SERBIA - highest China exposure

# 4. Check Serbia specifically
python -c "
import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_research.db')
cursor = conn.execute('''
    SELECT COUNT(*), SUM(has_chinese_partner)
    FROM core_f_collaboration
    WHERE source_file LIKE '%RS%' OR source_file LIKE '%Serbia%'
''')
print('Serbia results:', cursor.fetchone())
"
```

---

## 🔍 INTELLIGENCE PRIORITIES

### Immediate Focus:
1. **Serbia's China dependency mapping**
2. **Turkey's strategic technology partnerships**
3. **Norway's energy sector exposure**

### Secondary Analysis:
4. Switzerland's financial connections
5. Ukraine's historical partnerships
6. Smaller Balkans states if time permits

---

## 📊 WAREHOUSE INTEGRATION

Use same schema as EU terminals but with country-specific notes:

```python
# Add geopolitical context in analyst_notes
conn.execute("""
    INSERT INTO research_session (
        session_id, research_question, findings_summary, analyst_notes
    ) VALUES (?, ?, ?, ?)
""", (
    f"terminal_f_serbia_{timestamp}",
    "Serbia-China strategic dependency analysis",
    "Found Hesteel, Zijin, infrastructure projects",
    "CRITICAL: Serbia shows highest China dependency in Europe. Hesteel owns largest steel mill. Zijin controls major copper mines."
))
```

---

Your Terminal F mission is strategically critical as it maps China's influence beyond the EU's formal borders. Serbia is your top priority - it's Europe's most China-dependent country. Turkey second for its Eurasian bridge role. Quality intelligence over quantity - each finding here has major strategic implications.

**START WITH SERBIA** - Document every Chinese investment, partnership, and project. This is where China's European strategy is most visible.
