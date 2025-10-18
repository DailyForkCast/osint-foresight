# MCF Collection Implementation Plan
**Date**: 2025-09-22
**Based on**: KNOWLEDGE_BASE/07_DATA_SOURCES/MCF_HARVESTING_STRATEGY.md

## 🎯 **Executive Summary**

This plan implements the MCF Harvesting Strategy to collect Military-Civil Fusion intelligence from 50+ verified sources across 4 phases, integrating with our existing warehouse system.

**Target**: 1,000+ MCF-relevant documents with entity extraction, provenance tracking, and automated scoring.

## 📊 **Implementation Phases**

### **Phase 1: MCF Core Sources (Week 1) - HIGHEST PRIORITY**

#### Tier 1 Sources (Days 1-3)
| Source | MCF Signal | Collection Target | Implementation |
|--------|------------|-------------------|----------------|
| **State Dept** | Risk advisories, due diligence | /military-civil-fusion/ page + MCF reports | `scripts/collectors/state_dept_mcf_collector.py` |
| **NDU CSCMA** | PLA acquisition, doctrine | China Strategic Perspectives series | `scripts/collectors/ndu_cscma_collector.py` |
| **CASI** | PLA aerospace, AVIC/AECC ecosystems | Translation provenance, bilingual docs | `scripts/collectors/casi_aerospace_collector.py` |
| **ASPI** | Company mapping, case studies | Critical Tech Tracker, entity lists | `scripts/collectors/aspi_mcf_collector.py` |
| **USCC** | Economic-security nexus | Annual report MCF sections, hearings | `scripts/collectors/uscc_mcf_collector.py` |

**Expected Output**: 200-300 core MCF documents with highest relevance scores

#### Implementation Tasks (Days 1-3)
1. **Create base MCF collector framework**
2. **Implement MCF keyword weighting system**
3. **Set up entity extraction pipeline**
4. **Deploy Tier 1 source collectors**
5. **Validate results with manual sampling**

### **Phase 2: Technology Pathways (Week 2) - HIGH PRIORITY**

#### Tier 2 Sources (Days 4-7)
| Source | MCF Signal | Collection Target | Implementation |
|--------|------------|-------------------|----------------|
| **CSET Georgetown** | AI metrics, talent flows | Talent Program Tracker integration | `scripts/collectors/cset_talent_collector.py` |
| **MERICS** | MIIT policies, industrial subsidies | Policy trackers, dataset appendices | `scripts/collectors/merics_policy_collector.py` |
| **RAND Corporation** | Defense tech pathways, PLA procurement | MCF-specific reports, scenario analysis | `scripts/collectors/rand_mcf_collector.py` |
| **CSIS** | Case studies, maritime/space dual-use | ChinaPower data, figure images | `scripts/collectors/csis_chinapower_collector.py` |
| **Jamestown Foundation** | PLA/industry snapshots | China Brief articles, analyst bios | `scripts/collectors/jamestown_mcf_collector.py` |

**Expected Output**: 300-400 technology transfer and policy documents

### **Phase 3: Supply Chain Mapping (Week 3) - HIGH PRIORITY**

#### Export Control & Entity Sources (Days 8-10)
| Source | MCF Signal | Collection Target | Implementation |
|--------|------------|-------------------|----------------|
| **Atlantic Council** | Sanctions analysis | Entity tracking reports | `scripts/collectors/atlantic_sanctions_collector.py` |
| **FDD** | Entity tracking | Shell company analysis | `scripts/collectors/fdd_entity_collector.py` |
| **RUSI** | Export control studies | Circumvention case studies | `scripts/collectors/rusi_export_collector.py` |
| **Wilson Center** | Talent flow analysis | Personnel tracking reports | `scripts/collectors/wilson_talent_collector.py` |
| **Carnegie** | Investment patterns | China tech investment analysis | `scripts/collectors/carnegie_investment_collector.py` |

**Expected Output**: 200-250 supply chain and entity mapping documents

### **Phase 4: Regional Integration (Week 4) - MEDIUM PRIORITY**

#### Specialized Regional Sources (Days 11-14)
| Source Category | Sources | MCF Signal | Implementation |
|----------------|---------|------------|----------------|
| **European Tech** | FOI, IAI | Technical capabilities, systems analysis | `scripts/collectors/european_tech_collector.py` |
| **Arctic/Polar** | Arctic Institute, NUPI | Dual-use infrastructure, logistics | `scripts/collectors/arctic_mcf_collector.py` |
| **CEE Analysis** | CEIAS | Central/Eastern Europe investments | `scripts/collectors/ceias_investment_collector.py` |
| **Asia-Pacific** | NBR, CNAS | Regional MCF patterns | `scripts/collectors/apac_mcf_collector.py` |

**Expected Output**: 150-200 regional and specialized MCF documents

## 🔧 **Technical Implementation**

### **MCF Base Collector Framework**

```python
# scripts/collectors/mcf_base_collector.py
class MCFBaseCollector:
    def __init__(self):
        self.mcf_keywords = {
            'direct_mcf': {
                'weight': 5,
                'keywords': ['military civil fusion', 'MCF', '军民融合', 'dual use', 'dual-use']
            },
            'pla_industry': {
                'weight': 4,
                'keywords': ['PLA', 'AVIC', 'AECC', 'NORINCO', 'CETC', 'defense industry']
            },
            'technology_transfer': {
                'weight': 4,
                'keywords': ['technology transfer', 'talent program', 'thousand talents']
            },
            'policy_instruments': {
                'weight': 3,
                'keywords': ['MIIT', 'SASAC', 'guidance funds', 'Made in China 2025']
            },
            'export_controls': {
                'weight': 3,
                'keywords': ['export control', 'BIS', 'entity list', 'sanctions']
            }
        }

    def calculate_mcf_relevance(self, content):
        score = 0
        content_lower = content.lower()

        for category, config in self.mcf_keywords.items():
            for keyword in config['keywords']:
                if keyword.lower() in content_lower:
                    score += config['weight'] * 0.1

        return min(score, 1.0)

    def extract_mcf_entities(self, content):
        entities = {
            'companies': [],
            'institutes': [],
            'programs': [],
            'technologies': []
        }

        # Chinese defense companies
        companies = ['AVIC', 'AECC', 'NORINCO', 'CETC', 'CASIC', 'CSSC', 'CSIC']
        for company in companies:
            if company in content:
                entities['companies'].append(company)

        # Talent programs
        programs = ['Thousand Talents', 'Made in China 2025', 'Belt and Road']
        for program in programs:
            if program.lower() in content.lower():
                entities['programs'].append(program)

        return entities
```

### **Database Schema Extension**

```sql
-- Extend existing warehouse for MCF data
CREATE TABLE mcf_documents (
    id INTEGER PRIMARY KEY,
    source_id VARCHAR(50),
    document_type VARCHAR(50),
    title TEXT,
    url TEXT,
    publication_date DATE,
    mcf_relevance_score FLOAT,
    entities_json TEXT,
    provenance_json TEXT,
    pdf_hash VARCHAR(64),
    html_hash VARCHAR(64),
    collected_date TIMESTAMP
);

CREATE TABLE mcf_entities (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200),
    type VARCHAR(50), -- company, institute, program, technology
    chinese_name VARCHAR(200),
    aliases TEXT,
    first_seen DATE,
    last_updated DATE,
    verification_status VARCHAR(20)
);

CREATE TABLE mcf_relationships (
    id INTEGER PRIMARY KEY,
    entity1_id INTEGER,
    entity2_id INTEGER,
    relationship_type VARCHAR(50), -- subsidiary, partner, supplier
    confidence_score FLOAT,
    source_document_id INTEGER,
    created_date TIMESTAMP
);
```

### **Priority Collection Scripts**

#### 1. State Department MCF Collector
```python
# scripts/collectors/state_dept_mcf_collector.py
def collect_state_dept_mcf():
    base_url = "https://www.state.gov"
    mcf_path = "/military-civil-fusion/"

    # Collect MCF-specific advisories
    # Target: Business advisories, due diligence frameworks
    # Extract: Entity warnings, sector guidance
```

#### 2. ASPI Critical Tech Tracker Integration
```python
# scripts/collectors/aspi_mcf_collector.py
def collect_aspi_mcf_data():
    # Critical Tech Tracker CSV exports
    # Company classification data
    # MCF entity mapping
```

#### 3. CSET Talent Program Tracker
```python
# scripts/collectors/cset_talent_collector.py
def collect_cset_talent_data():
    # Talent flow analysis
    # Program participant tracking
    # Institution mapping
```

## 📅 **Implementation Schedule**

### **Week 1: Core MCF Infrastructure**
- **Day 1**: MCF base collector framework + database schema
- **Day 2**: State Dept + NDU CSCMA collectors
- **Day 3**: CASI + ASPI + USCC collectors
- **Day 4**: Entity extraction pipeline
- **Day 5**: Quality validation + testing

### **Week 2: Technology Transfer Sources**
- **Day 6**: CSET + MERICS collectors
- **Day 7**: RAND + CSIS collectors
- **Day 8**: Jamestown collector
- **Day 9**: Data integration testing
- **Day 10**: Cross-reference validation

### **Week 3: Supply Chain Intelligence**
- **Day 11**: Atlantic Council + FDD collectors
- **Day 12**: RUSI + Wilson Center collectors
- **Day 13**: Carnegie collector
- **Day 14**: Entity relationship mapping
- **Day 15**: Supply chain analysis

### **Week 4: Regional Integration**
- **Day 16**: European sources (FOI, IAI)
- **Day 17**: Arctic sources (Arctic Institute, NUPI)
- **Day 18**: CEE sources (CEIAS)
- **Day 19**: APAC sources (NBR, CNAS)
- **Day 20**: Comprehensive analysis + reporting

## 🎯 **Success Metrics**

### **Quantitative Targets**
- **Total Documents**: 1,000+ MCF-relevant documents
- **High Relevance**: 300+ documents with MCF score >0.7
- **Entity Extraction**: 500+ unique Chinese entities identified
- **Cross-References**: 200+ entity relationships mapped
- **Source Coverage**: 20+ primary MCF sources harvested

### **Quality Indicators**
- **Provenance Tracking**: 100% documents with source metadata
- **Entity Verification**: 95% entities cross-validated across sources
- **Temporal Coverage**: 2020-2025 for current MCF patterns
- **Translation Sources**: Bilingual content preserved with provenance

### **Integration Metrics**
- **Warehouse Integration**: All MCF data in F:/OSINT_WAREHOUSE/
- **Cross-Source Validation**: MCF entities verified across 3+ sources
- **API Functionality**: MCF endpoints operational
- **Search Capability**: Full-text search across MCF corpus

## 🔄 **Continuous Monitoring**

### **Daily Monitoring (Automated)**
- State Dept MCF advisories
- CASI new translations
- Jamestown China Brief (Tue/Fri)

### **Weekly Reviews**
- USCC hearing schedules
- MERICS policy updates
- CSET new datasets

### **Monthly Analysis**
- Entity list changes
- Technology transfer patterns
- Supply chain evolution

### **Annual Milestones**
- DoD China Military Power Report (October)
- USCC Annual Report (November)
- ODNI Threat Assessment (February)

## 🚀 **Immediate Next Steps**

1. **Create MCF base collector framework**
2. **Extend warehouse database schema**
3. **Implement Tier 1 source collectors (State Dept, NDU, CASI, ASPI, USCC)**
4. **Deploy entity extraction pipeline**
5. **Validate collection with manual review**

This implementation plan transforms the MCF Harvesting Strategy into actionable collection tasks, integrating seamlessly with our existing OSINT warehouse infrastructure while providing specialized MCF intelligence capabilities.

---

**Expected Timeline**: 4 weeks for full implementation
**Resource Requirements**: Database extension + 20+ collector scripts
**Output**: Comprehensive MCF intelligence database with entity tracking
