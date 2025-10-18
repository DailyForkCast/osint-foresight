# MCF Intelligence Harvesting - Implementation Roadmap

## Mission Statement

Implement a comprehensive Military-Civil Fusion (MCF) intelligence harvesting system across 50 verified sources, with provenance tracking and entity extraction capabilities.

## Phase 1: Foundation (Days 1-7)

### Day 1-2: Core MCF Sources
**Objective:** Establish baseline MCF intelligence flow

#### Priority Targets
1. **State Department MCF Page**
   - URL: https://www.state.gov/military-civil-fusion/
   - Extract: Risk advisories, due diligence frameworks
   - Provenance: Advisory numbers, bureau attribution

2. **NDU CSCMA**
   - URL: https://digitalcommons.ndu.edu/cscma-allpubs/
   - Extract: China Strategic Perspectives series
   - Provenance: Series IDs, author affiliations

3. **CASI**
   - URL: https://www.airuniversity.af.edu/CASI/
   - Extract: PLA translations, aerospace analysis
   - Provenance: Original document references

#### Implementation Tasks
- [ ] Set up base harvester with MCF keyword weighting
- [ ] Implement PDF extraction for government reports
- [ ] Create entity extraction pipeline
- [ ] Initialize provenance database

### Day 3-4: High-Value Think Tanks
**Objective:** Capture think tank MCF analysis

#### Targets
1. **ASPI** - Critical Technology Tracker
2. **MERICS** - Industrial policy tracking
3. **Jamestown** - China Brief
4. **CSET** - Talent Program Tracker
5. **USCC** - Annual reports, hearings

#### Implementation Tasks
- [ ] Custom extractor for ASPI datasets
- [ ] MERICS API integration
- [ ] Jamestown article parser
- [ ] CSET dataset versioning
- [ ] USCC testimony extraction

### Day 5-7: Provenance System
**Objective:** Full provenance tracking operational

#### Components
1. Document versioning system
2. Entity relationship mapping
3. Citation network builder
4. Source credibility scoring

#### Deliverables
- [ ] Provenance API endpoints live
- [ ] Entity database populated
- [ ] First MCF intelligence report

## Phase 2: Expansion (Days 8-14)

### Day 8-10: Technology Pathways
**Focus:** Dual-use technology transfer mechanisms

#### Source Priority
1. **RAND** - Defense technology analysis
2. **CSIS** - ChinaPower project
3. **Carnegie** - Tech standards
4. **Wilson Center** - Talent flows
5. **Atlantic Council** - Sanctions analysis

#### Key Extractions
- Technology transfer cases
- Joint laboratory agreements
- Talent program participants
- Standards manipulation instances

### Day 11-12: Supply Chain Mapping
**Focus:** Defense industrial base connections

#### Priority Entities
- AVIC (Aviation Industry Corporation)
- AECC (Aero Engine Corporation)
- NORINCO (Ordnance Industries)
- CETC (Electronics Technology)
- CSSC/CSIC (Shipbuilding)

#### Mapping Tasks
- [ ] Entity subsidiary trees
- [ ] Cross-ownership networks
- [ ] Joint venture identification
- [ ] Supply chain vulnerabilities

### Day 13-14: Export Control Intelligence
**Focus:** Sanctions and control circumvention

#### Sources
- **FDD** - Sanctions tracking
- **RUSI** - Export control analysis
- **CNAS** - Technology competition
- **State/BIS** - Entity lists

#### Deliverables
- [ ] Entity list changelog
- [ ] Circumvention pattern analysis
- [ ] Shell company identification

## Phase 3: Advanced Capabilities (Days 15-21)

### Day 15-17: Regional Perspectives
**Objective:** Multi-national MCF viewpoints

#### European Sources
- **FOI** (Sweden) - Technical capabilities
- **NUPI** (Norway) - Arctic dual-use
- **IFRI** (France) - Space/defense
- **IAI** (Italy) - Industrial cooperation
- **CEIAS** (Slovakia) - CEE investments

#### Asia-Pacific Sources
- **NBR** - Regional perspectives
- **East-West Center** - Pacific dynamics
- **Pacific Forum** - Security implications

### Day 18-19: Special Collections
**Focus:** Unique datasets and trackers

#### Priority Datasets
1. ASPI Critical Technology Tracker
2. CSET Chinese Talent Program Tracker
3. MERICS China Corporate Database
4. USCC Annual Report Tech Chapters
5. DoD China Military Power Report

#### Collection Requirements
- [ ] Automated dataset updates
- [ ] Version control system
- [ ] Change detection alerts
- [ ] API integration where available

### Day 20-21: Intelligence Products
**Objective:** Operational intelligence delivery

#### Product Types
1. **Daily MCF Brief**
   - New advisories/warnings
   - Entity list changes
   - Technology transfer incidents

2. **Weekly Analysis**
   - Pattern identification
   - Emerging entities
   - Policy shifts

3. **Monthly Strategic Assessment**
   - Trend analysis
   - Capability assessments
   - Risk evaluation

## Phase 4: Operationalization (Days 22-30)

### Day 22-24: Automation & Monitoring
**Objective:** Fully automated collection pipeline

#### Automation Targets
- RSS feed monitoring
- PDF report detection
- Entity mention alerts
- Keyword trend analysis
- Source update notifications

#### Monitoring Dashboard
- Real-time collection status
- Source health metrics
- Entity mention frequency
- MCF relevance scoring
- Provenance completeness

### Day 25-27: Quality Assurance
**Objective:** Ensure intelligence accuracy

#### QA Processes
1. **Source Verification**
   - Cross-reference multiple sources
   - Track citation networks
   - Verify entity relationships

2. **Entity Validation**
   - Name normalization
   - Alias resolution
   - Subsidiary mapping

3. **Temporal Analysis**
   - Timeline construction
   - Event correlation
   - Pattern detection

### Day 28-30: System Optimization
**Objective:** Performance and scalability

#### Optimization Areas
- Database query performance
- Deduplication efficiency
- Storage compression
- API response times
- Search indexing

## Key Performance Indicators (KPIs)

### Collection Metrics
- Sources monitored: 50/50
- Daily articles processed: >500
- MCF-relevant content: >20%
- Entity mentions tracked: >1000/day
- Provenance completeness: >90%

### Quality Metrics
- False positive rate: <5%
- Entity resolution accuracy: >95%
- Duplicate detection: >98%
- Citation capture rate: >85%
- Translation accuracy: >90%

### Operational Metrics
- System uptime: >99%
- Processing latency: <5 min
- Storage efficiency: >60%
- API response time: <200ms
- Alert delivery time: <10 min

## Risk Mitigation

### Technical Risks
1. **Source Access Changes**
   - Mitigation: Multiple fallback methods
   - Monitor robots.txt changes
   - Maintain mirror sites list

2. **Rate Limiting**
   - Mitigation: Distributed collection
   - Implement exponential backoff
   - Rotate user agents

3. **Content Format Changes**
   - Mitigation: Flexible parsers
   - Regular extraction testing
   - Manual fallback procedures

### Operational Risks
1. **Information Overload**
   - Mitigation: Smart filtering
   - Relevance scoring
   - Tiered alerting

2. **Entity Confusion**
   - Mitigation: Robust disambiguation
   - Human-in-the-loop validation
   - Confidence scoring

## Success Criteria

### Week 1
- [ ] Core MCF sources operational
- [ ] Provenance system active
- [ ] First intelligence report delivered

### Week 2
- [ ] All priority sources integrated
- [ ] Entity database >1000 entries
- [ ] Export control tracking live

### Week 3
- [ ] Regional sources integrated
- [ ] Special datasets automated
- [ ] Intelligence products operational

### Week 4
- [ ] Full automation achieved
- [ ] QA processes validated
- [ ] System optimized for scale

## Resource Requirements

### Technical Infrastructure
- Storage: 1TB minimum
- Processing: 8 cores, 32GB RAM
- Network: 100Mbps+ bandwidth
- Database: PostgreSQL with full-text search
- Cache: Redis for deduplication

### Tools & Libraries
- Python 3.9+
- BeautifulSoup4, lxml
- PyPDF2, pdfplumber
- spaCy for NER
- Elasticsearch for search
- Apache Airflow for orchestration

### Human Resources
- Lead Developer: Full-time
- Data Engineer: 50%
- Intelligence Analyst: 25%
- QA Specialist: 25%

## Deliverables Schedule

### Week 1 Deliverables
1. MCF Source Configuration (JSON)
2. Provenance Database Schema
3. Initial Intelligence Report
4. Entity Extraction Pipeline

### Week 2 Deliverables
1. Expanded Source Coverage Report
2. Entity Relationship Graph
3. Export Control Tracker
4. Technology Transfer Database

### Week 3 Deliverables
1. Regional Analysis Framework
2. Dataset Integration Report
3. Automated Intelligence Products
4. API Documentation

### Week 4 Deliverables
1. Full System Documentation
2. Performance Benchmarks
3. QA Validation Report
4. Operational Handbook

## Long-term Maintenance

### Daily Tasks
- Monitor collection pipeline
- Review high-priority alerts
- Update entity database
- Generate daily brief

### Weekly Tasks
- Source health check
- Entity validation review
- Performance optimization
- Intelligence product generation

### Monthly Tasks
- Comprehensive source audit
- Entity database cleanup
- System performance review
- Strategic assessment publication

### Annual Tasks
- Major report integration (DoD CMPR, USCC)
- Source portfolio review
- Technology stack upgrade
- Methodology documentation update

---

*Implementation Roadmap v1.0*
*Incorporates MCF crosswalk from 40 think tanks + 9 government sources*
*Estimated Timeline: 30 days to full operational capability*
*Last Updated: 2025-09-19*
