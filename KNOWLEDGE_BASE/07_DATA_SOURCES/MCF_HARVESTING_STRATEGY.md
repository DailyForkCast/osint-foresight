# Military-Civil Fusion (MCF) Harvesting Strategy

## Executive Summary

This document integrates the MCF crosswalk insights with our 50 verified China research sources to create a targeted harvesting strategy for Military-Civil Fusion intelligence.

**Key Focus:** Mapping sources to expected MCF signal types and implementing provenance tracking for maximum intelligence value.

## MCF Signal Categories

### 1. Direct MCF Indicators
- **Keywords:** "military-civil fusion", "MCF", "军民融合", "dual-use", "dual use"
- **Sources:** State Dept, CASI, NDU CSCMA, ASPI, Jamestown
- **Priority:** HIGHEST

### 2. Technology Transfer Pathways
- **Keywords:** "technology transfer", "talent program", "thousand talents", "joint lab"
- **Sources:** CSET (Talent Tracker), Wilson Center, USCC
- **Priority:** HIGH

### 3. Industrial Policy & Subsidies
- **Keywords:** "industrial policy", "subsidies", "state support", "guidance funds", "SOE"
- **Sources:** MERICS, Peterson Institute, USCC, CFR
- **Priority:** HIGH

### 4. Standards & Procurement
- **Keywords:** "standards", "3GPP", "procurement", "MIIT", "SASAC"
- **Sources:** CSIS, Carnegie, MERICS, CSET
- **Priority:** HIGH

### 5. Supply Chain Integration
- **Keywords:** "supply chain", "AVIC", "AECC", "shipbuilding", "space industrial base"
- **Sources:** CSIS, RAND, CASI, Atlantic Council
- **Priority:** MEDIUM

### 6. Export Control Circumvention
- **Keywords:** "export control", "sanctions", "shell company", "front company", "end-use"
- **Sources:** FDD, RUSI, CNAS, State Dept
- **Priority:** HIGH

## Source-Specific MCF Insights

### Tier 1: Primary MCF Sources (Highest Value)

#### NDU CSCMA
- **MCF Signals:** PLA acquisition, doctrine, strategy
- **Harvest Priority:** Series IDs, publication timelines
- **Provenance:** Digital Commons metadata, author affiliations
- **Special Focus:** China Strategic Perspectives series

#### CASI (China Aerospace Studies Institute)
- **MCF Signals:** PLA aerospace, AVIC/AECC ecosystems
- **Harvest Priority:** Translation provenance, bilingual docs
- **Provenance:** Original PLA document references
- **Special Focus:** Industry mapping to defense contractors

#### State Department
- **MCF Signals:** Risk advisories, due diligence frameworks
- **Harvest Priority:** MCF-specific reports, entity warnings
- **Provenance:** Bureau/office attribution, advisory dates
- **URL:** /military-civil-fusion/

#### ASPI
- **MCF Signals:** Company mapping, case studies
- **Harvest Priority:** Critical Tech Tracker data, entity lists
- **Provenance:** Dataset methodology, CSV exports
- **Special Focus:** MCF company identification

#### USCC
- **MCF Signals:** Economic-security nexus, tech chapters
- **Harvest Priority:** Annual report MCF sections, hearing transcripts
- **Provenance:** Witness affiliations, company citations
- **Special Focus:** Entity name extraction

### Tier 2: Strong MCF Coverage

#### MERICS
- **MCF Signals:** MIIT policies, industrial subsidies
- **Harvest Priority:** Policy trackers, dataset appendices
- **Provenance:** Chinese source documents referenced

#### CSET Georgetown
- **MCF Signals:** AI metrics, talent flows
- **Harvest Priority:** Talent Program Tracker, translations
- **Provenance:** Dataset DOIs, Zenodo links

#### RAND Corporation
- **MCF Signals:** Defense tech pathways, PLA procurement
- **Harvest Priority:** Page ranges in long PDFs, scenario analysis
- **Provenance:** Classification markings, sponsor info

#### CSIS
- **MCF Signals:** Case studies, maritime/space dual-use
- **Harvest Priority:** ChinaPower data, figure images
- **Provenance:** Dataset annexes, methodology docs

#### Jamestown Foundation
- **MCF Signals:** PLA/industry snapshots, doctrine updates
- **Harvest Priority:** China Brief articles, analyst bios
- **Provenance:** Author expertise, primary source citations

### Tier 3: Specialized MCF Angles

#### Arctic/Polar (Arctic Institute, NUPI, Wilson Polar)
- **MCF Signals:** Dual-use infrastructure, logistics
- **Focus:** Ports, shipping routes, research stations

#### European Perspectives (FOI, FRS, IAI)
- **MCF Signals:** Technology capabilities, systems analysis
- **Focus:** Signals intelligence, radar, UAV tech

#### Standards & Governance (Carnegie, ITIF, OECD)
- **MCF Signals:** Technical standards manipulation
- **Focus:** 5G/6G standards, AI governance

## Harvesting Implementation

### Phase 1: MCF Core (Week 1)
1. **State Dept MCF page** - Direct MCF framing
2. **NDU CSCMA** - Military strategy docs
3. **CASI** - Aerospace MCF translations
4. **ASPI** - Company mapping datasets
5. **USCC** - Annual report MCF chapters

### Phase 2: Technology Pathways (Week 2)
1. **CSET** - Talent Program Tracker integration
2. **MERICS** - Industrial policy tracking
3. **RAND** - Defense technology analysis
4. **CSIS** - Dual-use case studies
5. **Jamestown** - PLA modernization updates

### Phase 3: Supply Chain Mapping (Week 3)
1. **Atlantic Council** - Sanctions analysis
2. **FDD** - Entity tracking
3. **RUSI** - Export control studies
4. **Wilson Center** - Talent flow analysis
5. **Carnegie** - Investment patterns

### Phase 4: Regional Integration (Week 4)
1. **FOI** - Technical capabilities
2. **Arctic Institute** - Polar infrastructure
3. **CEIAS** - CEE investments
4. **IAI** - European industrial ties
5. **NBR** - Asia-Pacific perspectives

## Provenance Tracking Requirements

### Essential Metadata
```json
{
  "source_id": "ndu_cscma",
  "document_type": "report|brief|testimony|translation",
  "publication_date": "2025-01-15",
  "authors": [{"name": "", "affiliation": ""}],
  "series": "China Strategic Perspectives",
  "report_number": "CSP-15",
  "classification": "unclassified",
  "primary_sources_cited": [],
  "entities_mentioned": [],
  "pdf_hash": "sha256",
  "version": "1.0",
  "language": "en",
  "mcf_relevance_score": 0.95
}
```

### Entity Extraction Priority
1. **Chinese Companies:** AVIC, AECC, NORINCO, CETC, etc.
2. **Research Institutes:** CAS institutes, defense universities
3. **Government Bodies:** MIIT, SASAC, MOST, CMC departments
4. **Programs:** Made in China 2025, talent programs
5. **Technologies:** Specific systems, standards, patents

### Document Versioning
- Track report revisions and updates
- Store both HTML and PDF when available
- Hash documents for deduplication
- Archive landing pages with PDFs

## Enhanced Keyword Weighting for MCF

```python
mcf_keywords = {
    'direct_mcf': {
        'weight': 5,
        'keywords': ['military civil fusion', 'MCF', '军民融合',
                    'dual use', 'dual-use']
    },
    'pla_industry': {
        'weight': 4,
        'keywords': ['PLA', 'AVIC', 'AECC', 'NORINCO', 'CETC',
                    'defense industry', 'defense industrial base']
    },
    'technology_transfer': {
        'weight': 4,
        'keywords': ['technology transfer', 'talent program',
                    'thousand talents', 'joint laboratory']
    },
    'policy_instruments': {
        'weight': 3,
        'keywords': ['MIIT', 'SASAC', 'guidance funds', 'subsidies',
                    'industrial policy', 'Made in China 2025']
    },
    'export_controls': {
        'weight': 3,
        'keywords': ['export control', 'BIS', 'entity list',
                    'sanctions', 'end use', 'end user']
    },
    'standards': {
        'weight': 3,
        'keywords': ['3GPP', 'standards', 'standardization',
                    'technical standards', 'ISO', 'ITU']
    }
}
```

## Special Collection Requirements

### Government Report Cycles
- **October:** DoD China Military Power Report
- **November:** USCC Annual Report
- **February:** ODNI Threat Assessment
- **Quarterly:** State Dept MCF updates

### Dataset Priorities
1. **ASPI Critical Tech Tracker** - Company classifications
2. **CSET Talent Tracker** - Personnel flows
3. **MERICS Company Database** - Industrial mapping
4. **USCC Entity Lists** - Sanctioned organizations

### Translation Sources
- **CASI** - PLA documents
- **CSET** - Policy documents
- **NDU** - Military writings

## Quality Control Metrics

### MCF Relevance Scoring
```python
def calculate_mcf_relevance(content):
    score = 0

    # Direct MCF mentions (highest weight)
    if 'military civil fusion' in content.lower():
        score += 0.5

    # Entity mentions
    mcf_entities = ['AVIC', 'AECC', 'CETC', 'NORINCO']
    for entity in mcf_entities:
        if entity in content:
            score += 0.1

    # Technology categories
    dual_use_tech = ['hypersonic', 'quantum', 'AI', 'semiconductor']
    for tech in dual_use_tech:
        if tech.lower() in content.lower():
            score += 0.05

    return min(score, 1.0)
```

### Validation Checklist
- [ ] MCF keywords detected
- [ ] Entity names extracted
- [ ] Provenance metadata complete
- [ ] PDF and HTML archived
- [ ] Cross-references captured
- [ ] Dataset appendices saved
- [ ] Translation sources noted
- [ ] Author affiliations recorded

## Integration with Existing System

### Database Schema Extension
```sql
ALTER TABLE articles ADD COLUMN mcf_relevance FLOAT;
ALTER TABLE articles ADD COLUMN entities_json TEXT;
ALTER TABLE articles ADD COLUMN provenance_json TEXT;

CREATE TABLE mcf_entities (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200),
    type VARCHAR(50), -- company, institute, program
    chinese_name VARCHAR(200),
    aliases TEXT,
    first_seen DATE,
    last_updated DATE
);

CREATE TABLE document_versions (
    id INTEGER PRIMARY KEY,
    article_id INTEGER,
    version VARCHAR(20),
    pdf_hash VARCHAR(64),
    html_hash VARCHAR(64),
    captured_date TIMESTAMP
);
```

### API Endpoints for MCF Data
```
GET /api/mcf/latest - Recent MCF-relevant content
GET /api/mcf/entities - Entity directory
GET /api/mcf/by-source/{source_id} - MCF content by source
GET /api/mcf/technology/{tech_category} - By technology area
GET /api/mcf/provenance/{doc_id} - Full provenance chain
```

## Monitoring & Alerts

### Daily Monitoring
- State Dept MCF advisories
- CASI new translations
- Jamestown China Brief (Tue/Fri)

### Weekly Reviews
- USCC hearing schedules
- MERICS policy updates
- CSET new datasets

### Monthly Analysis
- Entity list changes
- New talent program participants
- Technology transfer patterns

### Annual Milestones
- DoD CMPR (October)
- USCC Annual Report (November)
- ODNI Assessment (February)

---

*MCF Harvesting Strategy v1.0*
*Incorporates crosswalk insights from 40 think tanks + government sources*
*Last Updated: 2025-09-19*
