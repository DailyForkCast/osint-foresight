# U.S. Government Document Collection - Implementation Status

**Created**: October 11, 2025
**Status**: Foundation Phase Complete, Ready for Collector Development

## What We're Building

Three interconnected automated weekly collection systems for U.S. Government documents:

### 1. Tech Sweep (5-Year Rolling Window)
- **Schedule**: Every Monday 02:00 UTC
- **Runtime**: 2-3 hours
- **Sources**: 20+ government APIs and websites
- **Focus**: Advanced/emerging tech, AI, quantum, semiconductors, space, biotech, cyber
- **Output**: JSON/CSV/SQL + Executive Memo

### 2. China Sweep (15-Year Rolling Window)
- **Schedule**: Every Friday 02:00 UTC
- **Runtime**: 4-6 hours
- **Sources**: Fast-Path (laws/sanctions) + Full Collector (treaties/S&T)
- **Focus**: US-China relations, sanctions, export controls, Entity List, MCF
- **Output**: JSON/CSV/SQL + Executive Memo

### 3. Weekly Automation Framework
- **Orchestration**: Scheduler + runbook executor
- **QA Validation**: 90% URL success, 80% file availability
- **Monitoring**: Metrics dashboard, alerting
- **Archiving**: Historical runs with audit trail

## ✅ Completed (Foundation Phase)

### Architecture & Planning
- [x] Master implementation plan created
- [x] 4-week development timeline
- [x] Success criteria defined (90% URLs, 80% files, <10% duplicates)
- [x] File structure designed
- [x] API integration priority list (4 tiers)

### Database Schema
- [x] `usgov_documents` - Main documents table (30+ fields)
- [x] `usgov_document_topics` - Many-to-many topic relationships
- [x] `usgov_sweep_runs` - Run metadata and QA metrics
- [x] `usgov_source_collections` - Per-source performance tracking
- [x] `usgov_qa_issues` - Issue logging and resolution
- [x] `usgov_controlled_topics` - Controlled vocabulary
- [x] `usgov_controlled_agencies` - Standardized agency codes
- [x] `usgov_dedup_cache` - Deduplication tracking
- [x] Views created for common queries
- [x] Indexes created for performance

### Initialization
- [x] Database initialization script
- [x] Schema SQL file (250+ lines)
- [x] Controlled vocabularies seeded (topics, agencies)

## 🔨 In Progress / Next Steps

### Week 1: Tech Sweep Collector
- [ ] Create base collector framework (`USGovBaseCollector`)
- [ ] Implement file downloader + SHA-256 hasher
- [ ] Build govinfo.gov API collector
- [ ] Build FederalRegister API collector
- [ ] Build GAO scraper
- [ ] Build CRS scraper
- [ ] Implement topic keyword filtering
- [ ] Create deduplication logic
- [ ] Build QA validator
- [ ] Create executive memo generator
- [ ] Run pilot Tech Sweep

### Week 2: China Sweep Collector
- [ ] Build Fast-Path collector (laws/regulations)
- [ ] Integrate congress.gov API
- [ ] Integrate regulations.gov API
- [ ] Integrate OFAC/sanctions APIs
- [ ] Integrate BIS Entity List
- [ ] Build Full Collector (treaties/S&T)
- [ ] Implement China keyword filtering
- [ ] Add country-pair detection
- [ ] Create China-specific memo template
- [ ] Run pilot China Sweep

### Week 3: Automation Framework
- [ ] Build scheduler/orchestrator
- [ ] Create runbook executor
- [ ] Implement pre-run checklist
- [ ] Build QA validation pipeline
- [ ] Create metrics dashboard
- [ ] Implement alerting (email/Slack)
- [ ] Build archive management
- [ ] Test weekly automation

### Week 4: Testing & Deployment
- [ ] Full end-to-end testing
- [ ] Validate QA metrics
- [ ] Performance tuning
- [ ] Documentation completion
- [ ] Deploy to production schedule
- [ ] Monitor first production runs

## Data Sources to Integrate

### Tier 1 (Must Have - Week 1) ✅ Planned
- govinfo.gov API
- FederalRegister.gov API
- GAO.gov (HTML scraping)
- CRS reports (HTML scraping)

### Tier 2 (High Priority - Week 2) ⏳ Planned
- congress.gov API
- regulations.gov API
- whitehouse.gov (RSS + scraping)
- Treasury/OFAC (sanctions)

### Tier 3 (Medium Priority - Week 3) ⏳ Planned
- Commerce/BIS (Entity List)
- State.gov (treaties, fact sheets)
- DoD sites (OSD, DARPA, DIU)
- CISA.gov (advisories)

### Tier 4 (Lower Priority - Week 4) ⏳ Planned
- NIST, NTIA, FCC
- DOE, ARPA-E
- NSF, NASA
- USPTO

## Key Features

### Document Types Covered
- Laws, regulations, rules, notices
- Reports, testimonies, strategies
- White papers, issue papers, nonpapers
- Treaties, MoUs, meeting readouts
- Hearings, committee prints
- Fact sheets, posture statements

### Quality Assurance
- **URL Validation**: HTTP 200/3xx checks
- **Metadata Validation**: Required fields present
- **Enum Validation**: Document types, publisher types
- **Date Validation**: Within collection window
- **Deduplication**: Hash + title similarity
- **File Verification**: SHA-256 hashing

### Topic Coverage

**Technology Areas**:
- AI/ML, quantum, semiconductors
- Space, biotech, advanced materials
- Robotics, cybersecurity, HPC
- Photonics, additive manufacturing
- 5G/6G, telecommunications

**Policy Areas**:
- Export controls (ECCN, EAR, ITAR)
- Supply chain resilience
- International standards
- Critical minerals, rare earths

**China Focus**:
- Sanctions, Entity List, MEU
- Investment restrictions (CFIUS)
- Military-Civil Fusion (MCF)
- S&T cooperation agreements
- Third-country relations

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Valid URLs | ≥90% | TBD | 🔜 |
| Docs with files | ≥80% | TBD | 🔜 |
| Duplicate rate | ≤10% | TBD | 🔜 |
| QA issues | ≤5% | TBD | 🔜 |
| Tech Sweep runtime | ≤3 hrs | TBD | 🔜 |
| China Sweep runtime | ≤6 hrs | TBD | 🔜 |

## File Structure

```
/scripts/collectors/
  ├── init_usgov_database.py ✅ Created
  ├── usgov_base_collector.py ⏳ Next
  ├── sources/
  │   ├── govinfo_collector.py ⏳ Week 1
  │   ├── federalregister_collector.py ⏳ Week 1
  │   ├── gao_collector.py ⏳ Week 1
  │   ├── crs_collector.py ⏳ Week 1
  │   └── [15+ more collectors] ⏳ Weeks 2-4
  ├── downloader.py ⏳ Week 1
  ├── normalizer.py ⏳ Week 1
  ├── deduplicator.py ⏳ Week 1
  └── qa_validator.py ⏳ Week 1

/schema/
  └── usgov_documents_schema.sql ✅ Created

/exports/us_gov_sweep/ ⏳ Auto-created on first run
/exports/us_gov_china/ ⏳ Auto-created on first run

/config/ ⏳ Week 3
  ├── usgov_sources.json
  ├── topic_vocabulary.json
  ├── agency_mappings.json
  └── runbook_schedules.json
```

## Dependencies Required

```python
# Already installed (verify)
requests
beautifulsoup4
lxml
python-dateutil

# May need to install
pip install rapidfuzz  # For fuzzy deduplication
pip install pdfplumber  # For PDF processing
pip install schedule  # For job scheduling
pip install jinja2  # For memo templates
```

## Timeline

- **Week 1** (Oct 14-18): Tech Sweep Collector + Tier 1 APIs
- **Week 2** (Oct 21-25): China Sweep Collector + Tier 2 APIs
- **Week 3** (Oct 28-Nov 1): Automation Framework + Tier 3 APIs
- **Week 4** (Nov 4-8): Testing, Documentation, Deployment

**Target Go-Live Dates**:
- **Tech Sweep**: Monday, October 28, 2025
- **China Sweep**: Friday, November 1, 2025

## Next Immediate Action

**Run database initialization**:
```bash
python scripts/collectors/init_usgov_database.py
```

This will create all tables, indexes, views, and seed the controlled vocabularies.

Then begin building the base collector framework and first API integration (govinfo.gov).

## Questions to Resolve

1. **File Storage**: Keep PDFs in `F:/OSINT_DATA/us_gov_documents/` or elsewhere?
2. **Notification Method**: Email, Slack, or both for weekly summaries?
3. **Archive Retention**: Keep how many weeks of historical runs?
4. **Priority Adjustments**: Should any sources be moved up/down in priority?

## Notes

- This is a **multi-week project** requiring systematic development
- Each collector must be tested independently before integration
- QA validation is critical - must meet 90/80/10/5 targets
- Weekly memos will be auto-generated but should be reviewed
- Consider running pilot sweeps during development for real-world testing

---

**Status as of October 11, 2025**: Foundation complete, ready to begin Week 1 development.
