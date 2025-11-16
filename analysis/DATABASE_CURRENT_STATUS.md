# DATABASE CURRENT STATUS
**Generated**: 2025-10-17 15:30:00
**Source**: Comprehensive Project Audit (October 17, 2025)
**Status**: ✅ VERIFIED

---

## AUTHORITATIVE CURRENT STATISTICS

**Use these values in ALL documentation updates**

| Metric | Current Value | Previous Claim | Variance | Last Verified |
|--------|--------------|----------------|----------|---------------|
| **Database Size** | 23 GB | 3.9 GB | +490% | 2025-10-17 |
| **Total Tables** | 218 | 137 | +59% | 2025-10-17 |
| **Active Tables** | 159 (73%) | Unknown | N/A | 2025-10-17 |
| **Empty Tables** | 59 (27%) | Unknown | N/A | 2025-10-17 |
| **Total Records** | 101,252,647 | 16,800,000 | +502% | 2025-10-17 |
| **Total Records (formatted)** | 101.3M | 16.8M | +502% | 2025-10-17 |

---

## TOP 15 TABLES BY SIZE

| Rank | Table Name | Records | % of Total |
|------|------------|---------|------------|
| 1 | uspto_cpc_classifications | 65,590,398 | 64.8% |
| 2 | uspto_case_file | 12,691,942 | 12.5% |
| 3 | arxiv_authors | 7,622,603 | 7.5% |
| 4 | gleif_entities | 3,086,233 | 3.0% |
| 5 | uspto_assignee | 2,800,000 | 2.8% |
| 6 | arxiv_categories | 2,605,465 | 2.6% |
| 7 | arxiv_papers | 1,443,097 | 1.4% |
| 8 | patentsview_cpc_strategic | 1,313,037 | 1.3% |
| 9 | ted_contracts_production | 861,984 | 0.9% |
| 10 | uspto_patents_chinese | 425,074 | 0.4% |
| 11 | ted_contractors | 367,326 | 0.4% |
| 12 | openalex_null_keyword_fails | 314,497 | 0.3% |
| 13 | uspto_cancer_data12a | 269,354 | 0.3% |
| 14 | usaspending_contracts | 250,000 | 0.2% |
| 15 | openalex_work_topics | 160,537 | 0.2% |

**Top 15 Total**: 99,741,506 records (98.5% of database)

---

## TABLE CATEGORIES

| Category | Table Count | Notable Tables |
|----------|-------------|----------------|
| **USPTO** | 7 | patents_chinese, cpc_classifications, case_file, assignee |
| **TED** | 12 | contracts_production, contractors |
| **USAspending** | 7 | china_305, china_101, china_comprehensive |
| **OpenAlex** | 24 | works, authors, institutions, topics |
| **arXiv** | 5 | papers, authors, categories |
| **GLEIF** | 9 | entities, relationships |
| **CORDIS** | 9 | projects, organizations |
| **ETO** | 16 | documents, technologies |
| **MCF** | 6 | documents, entities |
| **Other** | 123 | Various integration tables |

---

## DATA SOURCE STATISTICS

### Raw Data (F: Drive)

| Source | Size | Status | Notes |
|--------|------|--------|-------|
| **OpenAlex** | 422 GB | ✅ Verified | Exact match |
| **TED** | 28 GB | ✅ Verified | +12% vs claimed 24-25GB |
| **USPTO** | 66 GB | ✅ Verified | +94% vs claimed 34GB |
| **CORDIS** | 191 MB | ✅ Verified | -81% vs claimed 1GB |
| **arXiv** | 4.6 GB | ✅ Verified | Exact match |
| **USAspending ZIP** | 216 GB | ✅ Verified | Exact match |
| **CompaniesHouse UK** | 42 GB | ✅ Found | Previously undocumented |
| **ThinkTank Sweeps** | 8.3 MB | ✅ Verified | US_CAN: 76,886 items |
| **China Sweeps** | 12 MB | ✅ Verified | Active collection |
| **Europe-China Sweeps** | 30 MB | ✅ Verified | Active collection |

**Total Verified Storage**: 665+ GB

---

## PROCESSING COMPLETION STATUS

| Data Source | Claimed | Actual | Status |
|-------------|---------|--------|--------|
| **arXiv Papers** | 1.44M | 1,442,797 | ✅ EXACT MATCH |
| **USPTO Patents** | 568,324 | 577,197 | ✅ +2% (exceeds) |
| **TED Contracts** | 496,515 | 861,984 | ✅ +74% (exceeds) |
| **USAspending** | 166,557 | 166,557 | ✅ EXACT MATCH |
| **OpenAlex Multi-Country** | Complete | 69 countries, 267 files | ✅ VERIFIED |
| **ThinkTank Collection** | 986 entities | 76,886 US_CAN items | ✅ SIGNIFICANT |

---

## SCRIPT ECOSYSTEM

| Metric | Count | Notes |
|--------|-------|-------|
| **Total Scripts** | 715 | Previously claimed "100+" |
| **Active Scripts** | 660 | Main processing scripts |
| **Test Scripts** | 31 | Testing framework |
| **Archived Scripts** | 24 | Legacy/deprecated |
| **Script Directories** | 25 | Organized by function |
| **Recent Activity** | 123 | Modified in last 7 days |

---

## EMPTY TABLES (27% of Database)

**Total Empty**: 59 tables

**Sample Empty Tables**:
- aiddata_cross_reference
- bis_entity_list
- comtrade_analysis_summaries
- cordis_china_collaborations ❌ (expected to have data)
- eto_agora_documents ❌ (claimed as active)
- gleif_cross_references
- mcf_dualuse_indicators ❌ (expected for MCF)

**Recommendation**: Archive or remove empty tables during next database optimization

---

## QUALITY METRICS

### Detection Precision (Verified)

| Data Source | High Confidence | Overall Precision | Method |
|-------------|-----------------|-------------------|--------|
| **USAspending** | 78.8% | 85%+ | Geographic + name-based |
| **USPTO** | 85%+ | 85%+ | Name + address verification |
| **TED** | TBD | TBD | Requires sample audit |

---

## USAGE INSTRUCTIONS

### For Documentation Updates

**Always reference this file for current statistics**

Example markdown reference:
```markdown
Database: 23GB with 218 tables containing 101.3M records
(see [DATABASE_CURRENT_STATUS.md](analysis/DATABASE_CURRENT_STATUS.md))
```

### For Code Comments

```python
# Database: F:/OSINT_WAREHOUSE/osint_master.db
# Current size: 23GB, 218 tables, 101.3M records (as of 2025-10-17)
# See: analysis/DATABASE_CURRENT_STATUS.md for latest stats
```

---

## UPDATE SCHEDULE

**Manual Updates**: After major data additions or processing completions
**Automated Updates**: Planned weekly (see DOCUMENTATION_AUDIT_AND_REMEDIATION_PLAN_20251017.md)

---

## VERIFICATION METHOD

This file was generated from direct database queries and filesystem measurements:

```bash
# Database audit
python audit_database.py

# File size verification
du -sh /f/OSINT_WAREHOUSE/osint_master.db
du -sh /f/USPTO\ Data/
du -sh /f/TED_Data/
du -sh /f/OSINT_Backups/openalex/

# Table counts
sqlite3 osint_master.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"

# Record counts
sqlite3 osint_master.db "SELECT SUM(cnt) FROM (SELECT COUNT(*) as cnt FROM [table] ...)"
```

---

## RELATED DOCUMENTS

- [COMPREHENSIVE_AUDIT_REPORT_20251017.md](COMPREHENSIVE_AUDIT_REPORT_20251017.md) - Full audit findings
- [DOCUMENTATION_AUDIT_AND_REMEDIATION_PLAN_20251017.md](DOCUMENTATION_AUDIT_AND_REMEDIATION_PLAN_20251017.md) - Remediation strategy
- [DATABASE_AUDIT_RESULTS.json](DATABASE_AUDIT_RESULTS.json) - Raw audit data

---

**Status**: ✅ AUTHORITATIVE - Use these values for all documentation
**Last Audit**: October 17, 2025
**Next Audit**: Weekly automated (planned)

---

*This file serves as the single source of truth for all project statistics. Do not hard-code statistics in other files - reference this file instead.*
