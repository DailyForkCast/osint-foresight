# OSINT Foresight - Master Documentation Index
**Last Updated**: October 17, 2025
**Version**: 1.0
**Purpose**: Comprehensive navigation guide to all project documentation

---

## Quick Start

**New to the project?** Start here:
1. 📖 [README.md](../README.md) - Project overview and data sources
2. 🏗️ [PROJECT_ARCHITECTURE](04_PROJECT_ARCHITECTURE/) - System architecture
3. 📜 [SCRIPTS_INVENTORY.md](../docs/SCRIPTS_INVENTORY.md) - All 878 scripts documented
4. 📋 [ARCHIVAL_POLICY.md](ARCHIVAL_POLICY.md) - Documentation lifecycle management

**Need current statistics?** Check:
- 📊 [DATABASE_CURRENT_STATUS.md](../analysis/DATABASE_CURRENT_STATUS.md) - Real-time database stats
- 📈 [PROCESSING_STATUS_REPORT.md](../data/processing_status_report.md) - Data processing status

---

## Tier 1: Critical Documentation

These files are the primary reference points for the project and are **NEVER archived**.

### Project Foundation
| Document | Location | Purpose |
|----------|----------|---------|
| **README.md** | `/README.md` | Project overview, data sources, quick start |
| **CLAUDE_CODE_MASTER_V9.8_COMPLETE.md** | `/docs/prompts/active/master/` | Complete AI assistant instructions |
| **UNIFIED_DATA_INFRASTRUCTURE_INVENTORY_MULTICOUNTRY.md** | `/docs/` | Comprehensive data infrastructure inventory |
| **SCRIPTS_INVENTORY.md** | `/docs/` | Complete inventory of all 878 scripts |

### Current Status Files
| Document | Location | Purpose |
|----------|----------|---------|
| **DATABASE_CURRENT_STATUS.md** | `/analysis/` | Real-time database statistics (23 GB, 218 tables, 101.3M records) |
| **processing_status.json** | `/data/` | Current processing status across all data sources |

### Policy & Standards
| Document | Location | Purpose |
|----------|----------|---------|
| **ARCHIVAL_POLICY.md** | `/KNOWLEDGE_BASE/` | Documentation archival procedures and retention policies |
| **DOCUMENTATION_REMEDIATION_COMPLETION_REPORT.md** | `/KNOWLEDGE_BASE/` | Phase 1+2 documentation update results |

---

## Tier 2: Architecture Documentation

Core technical architecture files that define system structure. Protected from archival.

### Database Architecture
| Document | Location | Purpose |
|----------|----------|---------|
| **DATABASE_CONSOLIDATION_REPORT.md** | `/KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE/` | 27→3 database consolidation report |
| **CONSOLIDATION_COMPLETE_SUMMARY.md** | `/KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE/` | Complete consolidation summary with benefits |
| **FINAL_CONSOLIDATION_REPORT.md** | `/KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE/` | Final report with next steps and locations |
| **SESSION_SUMMARY_20250929.md** | `/KNOWLEDGE_BASE/` | Historical session summary from major consolidation |

### System Design
| Document | Location | Purpose |
|----------|----------|---------|
| **INTEGRATION_ROADMAP.md** | `/database/` | Database integration roadmap and ETL pipeline |
| **schema.sql** | `/database/` | Complete database schema definition |
| **entity_schema.sql** | `/database/` | Entity relationship schema |

---

## Tier 3: Data Source Documentation

### OpenAlex Research Collaboration
| Document | Location | Purpose | Status |
|----------|----------|---------|--------|
| **OPENALEX_COVERAGE_ANALYSIS.md** | `/analysis/` | Coverage analysis across 81 countries | Active |
| **OPENALEX_V5_COMPLETION_SUMMARY.md** | `/analysis/` | Version 5 completion report | Active |
| **OPENALEX_V5_VALIDATION_REPORT.json** | `/analysis/` | Validation results for v5 processor | Active |
| **openalex_concurrent_partitions.json** | `/config/` | Concurrent processing configuration | Active |
| **openalex_technology_keywords_v5.json** | `/config/` | Technology detection keywords | Active |

### TED EU Procurement
| Document | Location | Purpose | Status |
|----------|----------|---------|--------|
| **TED_FINAL_COMPREHENSIVE_REPORT.md** | `/analysis/` | Complete TED analysis summary | Active |
| **TED_PROCESSING_COMPLETE_REPORT.md** | `/analysis/` | Processing status and statistics | Active |
| **TED_FORMAT_TIMELINE_REPORT.md** | `/analysis/` | TED format evolution (2006-2025) | Active |
| **TED_CHINESE_CONTRACTORS_FINAL_REPORT.json** | `/analysis/` | Chinese contractor detection results | Active |
| **UBL_INTEGRATION_COMPLETE_20251013.md** | `/analysis/` | UBL/eForms parser integration | Active |

### USPTO Patents
| Document | Location | Purpose | Status |
|----------|----------|---------|--------|
| **USPTO_FINAL_COMPREHENSIVE_REPORT_2011_2025.md** | `/analysis/` | Complete USPTO analysis (577,197 patents) | Active |
| **USPTO_PATENT_DETECTION_METHODOLOGY.md** | `/analysis/` | Chinese patent detection methodology | Active |
| **USPTO_CPC_STRATEGIC_TECHNOLOGIES_CHINESE.json** | `/analysis/` | Strategic tech classification results | Active |
| **USPTO_ANALYSIS_COMPLETE_SUMMARY.md** | `/analysis/` | Analysis completion summary | Active |

### USAspending Federal Contracts
| Document | Location | Purpose | Status |
|----------|----------|---------|--------|
| **USASPENDING_COMPREHENSIVE_ANALYSIS_FRAMEWORK.md** | `/analysis/` | Comprehensive analysis methodology | Active |
| **USASPENDING_COMPLETE_SCHEMA.md** | `/analysis/` | Complete schema documentation | Active |
| **USASPENDING_VALIDATION_FINAL_SUMMARY.md** | `/analysis/` | Validation results summary | Active |
| **usaspending_china_analysis.json** | `/analysis/` | China-linked contract analysis | Active |

### arXiv Research Papers
| Document | Location | Purpose | Status |
|----------|----------|---------|--------|
| **KAGGLE_ARXIV_PROCESSING_COMPLETE.md** | `/analysis/` | Kaggle arXiv processing completion report | Active |
| **KAGGLE_ARXIV_ANALYSIS_SUITE.md** | `/analysis/` | Analysis suite documentation | Active |
| **ARXIV_INTEGRATION_COMPLETE.md** | `/analysis/` | Integration completion summary | Active |
| **ARXIV_DATA_ACCESS_GUIDE.md** | `/docs/` | Data access and query guide | Active |

### Other Data Sources
| Document | Location | Purpose | Status |
|----------|----------|---------|--------|
| **GLEIF_DATA_ANALYSIS_AND_RECOMMENDATIONS.md** | `/analysis/` | GLEIF entity analysis (3.1M entities) | Active |
| **ASPI_DATA_ACCESSIBILITY_REPORT.md** | `/analysis/` | ASPI China Tech Map accessibility | Active |
| **ETO_DATASETS_DEPLOYMENT_COMPLETE.md** | `/analysis/` | ETO datasets deployment summary | Active |
| **GITHUB_INTEGRATION_SUMMARY.md** | `/analysis/` | GitHub organizational activity tracking | Active |

---

## Tier 4: Methodology & Frameworks

### Detection & Validation
| Document | Location | Purpose |
|----------|----------|---------|
| **CHINESE_ENTITY_DETECTION_GUIDE.md** | `/analysis/` | Comprehensive detection methodology |
| **IMPORTANCE_TIER_FRAMEWORK.md** | `/docs/` | Importance tier classification system |
| **enhanced_detection_framework.json** | `/config/` | Detection framework configuration |
| **detection_schema.json** | `/config/` | Detection schema specification |

### Technology Assessment
| Document | Location | Purpose |
|----------|----------|---------|
| **TECHNOLOGY_FORESIGHT_METHODOLOGY.md** | `/docs/` | Technology foresight assessment methodology |
| **FINAL_COMMODITY_PATTERNS.md** | `/analysis/` | Dual-use commodity pattern analysis |
| **expanded_commodity_patterns.json** | `/analysis/` | Expanded pattern matching rules |

### Validation & Quality
| Document | Location | Purpose |
|----------|----------|---------|
| **master_prompt_v98_compliance.py** | `/src/core/` | Master prompt compliance validation |
| **enhanced_validation_v3_complete.py** | `/src/core/` | Enhanced validation framework v3 |
| **unified_validation_manager.py** | `/src/core/` | Unified validation management system |

---

## Tier 5: Analysis Reports

### Strategic Analysis
| Document | Location | Purpose |
|----------|----------|---------|
| **CHINA_EUROPE_INTERACTIONS.md** | `/analysis/` | China-Europe interaction analysis |
| **FINAL_EU_CHINA_PROCUREMENT_REPORT.md** | `/analysis/` | EU-China procurement comprehensive report |
| **strategic_dependencies.json** | `/analysis/` | Strategic dependency analysis |
| **country_expansion_status.json** | `/analysis/` | 81-country expansion status |

### Cross-Source Intelligence
| Document | Location | Purpose |
|----------|----------|---------|
| **CROSS_SOURCE_INTELLIGENCE_REPORT_20250930.md** | `/analysis/` | Multi-source intelligence fusion |
| **ENTITY_CROSS_REFERENCE_REPORT.md** | `/analysis/` | Cross-source entity matching |
| **FINAL_COMPREHENSIVE_INTELLIGENCE_REPORT.md** | `/analysis/` | Comprehensive intelligence summary |

### Data Quality
| Document | Location | Purpose |
|----------|----------|---------|
| **DATA_VALIDATION_REPORT.md** | `/analysis/` | Data validation results |
| **DATA_REALITY_CHECK.md** | `/analysis/` | Data quality reality check |
| **VALIDATION_REPORT.md** | `/analysis/` | Comprehensive validation report |
| **data_validation_results.json** | `/analysis/` | Validation results data |

---

## Tier 6: Session Summaries

### Recent Sessions (Active)
| Document | Location | Date | Topic |
|----------|----------|------|-------|
| **SESSION_SUMMARY_20251016_OPTION_B_COMPLETE.md** | `/analysis/` | 2025-10-16 | Option B implementation completion |
| **SESSION_SUMMARY_SHORT_TERM_PROGRESS.md** | `/analysis/` | 2025-10-11 | Short-term progress update |
| **SESSION_SUMMARY_20251011.md** | `/analysis/` | 2025-10-11 | Multi-source processing |
| **SESSION_SUMMARY_20251010.md** | `/analysis/` | 2025-10-10 | Next 10 moves planning |

### Historical Sessions (Archive after 90 days)
Session summaries older than 90 days are automatically moved to `KNOWLEDGE_BASE/archive/YYYY-MM/`.

---

## Tier 7: Configuration Files

### Core Configuration
| Document | Location | Purpose |
|----------|----------|---------|
| **expanded_countries.json** | `/config/` | 81-country expansion configuration |
| **country_specific_data_sources.json** | `/config/` | Data sources by country |
| **phase2_config.json** | `/config/` | Phase 2 processing configuration |
| **intake_schedule.json** | `/config/` | Data intake scheduling |

### Detection Configuration
| Document | Location | Purpose |
|----------|----------|---------|
| **china_geographic_comprehensive.json** | `/config/` | Chinese geographic entities |
| **prc_identifiers.json** | `/data/` | PRC entity identifiers |
| **prc_soe_database.json** | `/data/` | PRC state-owned enterprises |
| **chinese_entities_enhanced.json** | `/data/` | Enhanced Chinese entity database |

---

## Specialized Documentation

### Data Source Guides
| Document | Location | Purpose |
|----------|----------|---------|
| **COMPLETE_LANGUAGE_SUPPORT.md** | `/docs/` | Multi-language support documentation |
| **MANUAL_PATENTSVIEW_DOWNLOAD_GUIDE.md** | `/docs/` | PatentsView data download guide |
| **PATENTSVIEW_SETUP_GUIDE.md** | `/docs/` | PatentsView setup instructions |
| **US_GOV_COLLECTION_MASTER_PLAN.md** | `/docs/` | US government data collection plan |

### Technical Guides
| Document | Location | Purpose |
|----------|----------|---------|
| **NULL_DATA_HANDLING_FINAL_REPORT.md** | `/docs/` | Null data handling methodology |
| **PLACEHOLDER_LOGIC_EXPLANATION.md** | `/docs/` | Placeholder detection logic |
| **PROJECT_ORGANIZATION_SUMMARY.md** | `/docs/` | Project structure and organization |

### Collector-Specific
| Document | Location | Purpose |
|----------|----------|---------|
| **ETO_DATASETS_GUIDE.md** | `/scripts/collectors/` | ETO datasets collection guide |
| **ETO_DATABASE_INTEGRATION_COMPLETE.md** | `/scripts/collectors/` | ETO database integration report |

---

## Archive Documentation

### Archive Locations
| Archive | Location | Contents |
|---------|----------|----------|
| **KNOWLEDGE_BASE Archive** | `/KNOWLEDGE_BASE/archive/` | Session summaries, temporary docs, superseded guides |
| **Analysis Archive** | `/analysis/archive/` | Test outputs, checkpoints, superseded analysis reports |

### Archive Management
| Document | Location | Purpose |
|----------|----------|---------|
| **ARCHIVAL_POLICY.md** | `/KNOWLEDGE_BASE/` | Complete archival policy and procedures |
| **archive_old_docs.py** | `/` | Automated archival script |
| **archive/README.md** | `/KNOWLEDGE_BASE/archive/` | KNOWLEDGE_BASE archive documentation |
| **archive/README.md** | `/analysis/archive/` | Analysis archive documentation |
| **ARCHIVE_INDEX.md** | `/[archive]/YYYY-MM/` | Monthly archive index (auto-generated) |

---

## Automation Scripts

### Documentation Management
| Script | Location | Purpose |
|--------|----------|---------|
| **archive_old_docs.py** | `/` | Archive documentation >90 days old |
| **validate_documentation.py** | `/scripts/` | Validate documentation health (future) |
| **compress_archives.py** | `/scripts/` | Compress archives >180 days old (future) |

### Data Processing
| Script | Location | Purpose |
|--------|----------|---------|
| **audit_database.py** | `/` | Database audit and statistics |
| **check_processing_status.py** | `/scripts/` | Check processing status |
| **monitor_[source]_progress.py** | `/scripts/` | Monitor data source processing |

For complete scripts inventory, see [SCRIPTS_INVENTORY.md](../docs/SCRIPTS_INVENTORY.md) (878 scripts documented).

---

## Document Status Indicators

### Activity Status
- **✅ Active**: Currently maintained, <90 days old or protected
- **📦 Archival Pending**: >90 days old, will be archived soon
- **🗄️ Archived**: Moved to archive directory
- **🔒 Protected**: Never archived (Tier 1+2)

### Update Status
- **Current**: Statistics reflect true project state (as of 2025-10-17)
- **Historical**: Accurate for its time but superseded by newer analysis
- **Superseded**: Replaced by newer comprehensive report

---

## Navigation Tips

### Finding Specific Topics

**Database Statistics**: Start with DATABASE_CURRENT_STATUS.md for real-time stats

**Data Source Analysis**: Check Tier 3 section for source-specific reports

**Methodology**: See Tier 4 for detection, validation, and assessment frameworks

**Recent Activity**: Check Tier 6 Session Summaries for recent work

**Configuration**: See Tier 7 for all configuration files

**Scripts**: Use SCRIPTS_INVENTORY.md to find operational scripts

### Search Patterns

**By Data Source**: Search for source name (openalex, ted, uspto, usaspending, arxiv)

**By Technology**: Search in analysis/ directory for technology-specific reports

**By Country**: Use country_expansion_status.json or search for country codes

**By Date**: Use YYYY-MM-DD format, check session summaries first

### Common Questions

**Q: Where are current database statistics?**
A: analysis/DATABASE_CURRENT_STATUS.md (23 GB, 218 tables, 101.3M records)

**Q: How many scripts exist?**
A: 878 scripts documented in docs/SCRIPTS_INVENTORY.md

**Q: Where are USPTO patent statistics?**
A: analysis/USPTO_FINAL_COMPREHENSIVE_REPORT_2011_2025.md (577,197 patents)

**Q: How does archival work?**
A: See KNOWLEDGE_BASE/ARCHIVAL_POLICY.md for complete policy

**Q: Where are old files?**
A: Check KNOWLEDGE_BASE/archive/ or analysis/archive/ by month

---

## Document Maintenance

### Regular Updates (Automated)
- **Database Statistics**: Updated weekly via audit_database.py
- **Processing Status**: Updated continuously by processing scripts
- **Archive Indexes**: Updated weekly by archive_old_docs.py

### Quarterly Reviews
- Review all Tier 1+2 files for accuracy
- Update statistics if significant changes
- Verify archive structure and indexes
- Update this index with new major documents

### Annual Reviews
- Comprehensive documentation audit
- Archive policy effectiveness review
- Update retention thresholds if needed
- Consolidate session summaries

---

## Version History

### Version 1.0 (2025-10-17)
- Initial creation as part of Phase 3 documentation remediation
- Documented all Tier 1-7 documentation
- Established navigation structure
- Integrated with ARCHIVAL_POLICY.md

---

## Related Documentation

- **ARCHIVAL_POLICY.md**: Complete archival procedures and retention policies
- **SCRIPTS_INVENTORY.md**: All 878 scripts organized and categorized
- **DOCUMENTATION_REMEDIATION_COMPLETION_REPORT.md**: Phase 1+2 update results
- **README.md**: Project overview and quick start

---

## Contact

For questions about documentation organization or archival:
1. Review this index first
2. Check ARCHIVAL_POLICY.md for archival questions
3. Review SCRIPTS_INVENTORY.md for script-related questions
4. Check archive README.md files for archived content

---

**Index Status**: ✅ CURRENT (as of 2025-10-17)
**Total Documents Indexed**: 100+ files across 7 tiers
**Coverage**: Complete for all Tier 1-4 documentation
**Next Update**: Quarterly review (January 2026)

---

*This index is automatically protected from archival and serves as the primary navigation guide for all OSINT Foresight project documentation.*
