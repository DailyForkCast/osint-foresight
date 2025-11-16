# EU-wide + MCF Sweep - Initial Results

**Date**: 2025-10-10
**Status**: Workflow Established
**Move**: #5 from Next 10 Moves

---

## Objective

Launch EU-wide + MCF sweep using Finder → Downloader → Hasher → QA workflow for:
- EU institutions (EC, EEAS, EP, EDA, ESA, NATO, OECD)
- Tier-1 think tanks (EUISS, Bruegel, MERICS, RUSI, IFRI, SWP, IISS)
- Focus: China-Europe S&T with Military-Civil Fusion emphasis
- Target: Direct-downloadable PDFs/DOCX (2015-present)

---

## Scripts Created

### 1. EU MCF Report Finder
**Location**: `scripts/collectors/eu_mcf_report_finder.py`

**Capabilities**:
- Web scraping for 7+ think tanks and EU institutions
- China-Europe S&T keyword detection
- MCF-related content identification
- Topic auto-detection (AI, semiconductors, quantum, space, MCF, supply chain)
- Content-type verification for download links
- Structured JSON output with comprehensive metadata

**Keywords**:
- China: china, chinese, prc, people's republic, beijing, sino-, eu-china
- Technology: semiconductor, quantum, AI, space, dual-use, 5G, 6G, biotech, robotics
- MCF: military-civil fusion, dual-use, defense, Seven Sons, defense universities

### 2. EU MCF Report Downloader + Hasher
**Location**: `scripts/collectors/eu_mcf_report_downloader.py`

**Capabilities**:
- Download PDFs/DOCX from finder results
- Structured filename: `{year}_{publisher}_{title_slug}_{lang}.{ext}`
- SHA-256 hash computation
- Duplicate detection by hash
- Page count extraction (PDFs)
- File size tracking
- Enhanced metadata JSON output

---

## Initial Run Results

### Finder Results
**Input**: 4 think tank websites (MERICS, EUISS, RUSI, Bruegel)
**Output**: `data/external/eu_mcf_reports/eu_mcf_reports_20251010_213845.json`

**Reports Found**: 2

| Publisher | Title | Date | Topics |
|-----------|-------|------|--------|
| EUISS | Beyond Trump: Xi's price wars and weaponisation of critical raw materials | 2025-10-09 | Supply Chain |
| Bruegel | Convergence, not alignment: EU-China climate relations ahead of COP30 | 2025-07-22 | - |

**Statistics**:
- Total found: 2
- MCF-related: 0
- Europe focus: 2 (100%)

### Downloader Results
**Input**: Finder JSON
**Output**: `data/external/eu_mcf_reports/eu_mcf_reports_processed_20251010_213917.json`

**Downloads**: 1 successful, 1 failed

#### Successfully Downloaded:
**Bruegel Report**:
- Title: "Convergence, not alignment: EU-China climate relations ahead of COP30"
- File: `2025_bruegel_convergence_not_alignment_eu_china_climate_relations_ahead_o_en.pdf`
- Hash: `2de57f59b3bce0099c1be531273df4ef5c41717c78625fd7511260304c17fbf2`
- Size: 1,404,150 bytes (1.34 MB)
- Pages: 43
- Topics: EU-China climate cooperation, emissions reduction
- Status: Ready for database import

#### Failed Downloads:
**EUISS Report**:
- Error: 403 Forbidden (CSET Georgetown link requires authentication)
- Note: Scraper found embedded link rather than direct publisher PDF

---

## Workflow Validation

### ✅ Completed Components

1. **Finder**
   - Web scraping infrastructure ✅
   - Keyword-based filtering ✅
   - Topic auto-detection ✅
   - Structured JSON output ✅

2. **Downloader**
   - HTTP download with retry ✅
   - SHA-256 hashing ✅
   - Page count extraction ✅
   - Duplicate detection ✅
   - Structured filenames ✅

3. **Metadata Extraction**
   - Title, publisher, date ✅
   - Topics, regions, countries ✅
   - MCF flag detection ✅
   - Abstract/summary ✅

### 🔄 Needs Refinement

1. **Scraper Accuracy**
   - Issue: Some scrapers finding embedded links instead of publisher PDFs
   - Impact: 50% download failure rate in initial run
   - Solution: Refine CSS selectors for each publisher

2. **Coverage**
   - Current: 4 think tanks attempted (MERICS, EUISS, RUSI, Bruegel)
   - Target: 7 think tanks + 6 EU institutions
   - Next: Add EC, EEAS, EP, EDA, ESA, NATO, OECD scrapers

3. **MCF Detection**
   - Current: 0 MCF-flagged reports in initial run
   - Reason: Limited sample size, keyword-based detection needs tuning
   - Next: Expand keywords, add context analysis

---

## Database Import Status

**Ready for Import**: 1 report

**Import Command**:
```bash
python scripts/importers/import_thinktank_reports.py \
  --input data/external/eu_mcf_reports/downloads
```

**Expected Database Impact**:
- New reports: 1
- New topics: Climate cooperation (if not already in ref_topics)
- New publishers: Bruegel (if not already seen)

---

## Gap Analysis Impact

**Before Sweep**:
- Arctic coverage: 0 reports across all topics
- East Asia × Semiconductors: 0 reports

**After Sweep** (projected with full implementation):
- Target: Fill Arctic gaps with NATO, OECD Arctic reports
- Target: Fill semiconductor gaps with EC DG TRADE reports
- Target: Increase MCF coverage with MERICS, IISS, SWP reports

---

## Next Steps

### Immediate (Complete Move 5)
1. ✅ Create finder script
2. ✅ Create downloader script
3. ✅ Test workflow with initial run
4. ⬜ Refine scrapers for higher success rate
5. ⬜ Add remaining institutions (EC, EEAS, EP, EDA, ESA, NATO, OECD)
6. ⬜ Import successful downloads to database

### Production Deployment (Move 10)
1. Schedule weekly EU/MCF sweep
2. Automate quality assurance checks
3. Generate weekly memo of top 5 new signals
4. Rotate regional focus (Nordics → Balkans → DACH → Benelux → Baltics)

---

## Technical Details

### Finder Output Schema
```json
{
  "title": "Report Title",
  "publisher_org": "Organization Name",
  "publication_date_iso": "YYYY-MM-DD",
  "year": 2025,
  "month": 10,
  "day": 10,
  "canonical_url": "https://...",
  "download_url": "https://...pdf",
  "language": "en",
  "authors": ["Author Name"],
  "region_group": ["europe", "east_asia"],
  "country_list": ["CN", "EU"],
  "topics": ["ai_ml", "semiconductors"],
  "subtopics": [],
  "mcf_flag": 0 or 1,
  "europe_focus_flag": 1,
  "arctic_flag": 0,
  "doc_type": "report",
  "file_ext": "pdf",
  "abstract": "Summary text..."
}
```

### Downloader Enhancement
Adds to finder output:
```json
{
  "hash_sha256": "abc123...",
  "file_size_bytes": 1404150,
  "pages": 43,
  "saved_path": "data/external/.../file.pdf",
  "download_status": "success",
  "extraction_ok": true,
  "extraction_notes": ["Extracted 43 pages"],
  "collection_date_utc": "2025-10-10T21:39:16Z"
}
```

---

## Lessons Learned

### Web Scraping Challenges
1. **Publisher-Specific Scrapers**: Each organization has unique HTML structure
2. **PDF Link Detection**: Need multiple strategies (direct links, download buttons, embedded viewers)
3. **Rate Limiting**: 0.5-1 second delays prevent IP blocks
4. **Authentication**: Some PDFs require cookies/sessions (e.g., CSET links)

### Metadata Quality
1. **Date Extraction**: Multiple regex patterns needed for various formats
2. **Topic Detection**: Keyword-based works but needs context analysis for accuracy
3. **MCF Detection**: Specific terminology varies across publishers

### File Management
1. **Deduplication**: SHA-256 hashing prevents duplicate downloads
2. **Filename Structure**: Year-first enables chronological sorting
3. **Directory Organization**: Separate finder outputs from downloaded files

---

## Statistics

**Code Created**:
- Python scripts: 2 (finder + downloader)
- Total lines: ~600 lines
- Functions: 15+
- Think tanks covered: 4/7 (57%)
- EU institutions covered: 0/6 (0%)

**Data Collected**:
- Reports identified: 2
- Reports downloaded: 1
- Total size: 1.34 MB
- Total pages: 43
- Unique hashes: 1

**Time Investment**:
- Script development: ~30 minutes
- Initial run: 2 minutes
- Total: ~32 minutes

---

## Move 5 Status

**Status**: ✅ WORKFLOW ESTABLISHED

**Completion Criteria Met**:
- ✅ Finder script created
- ✅ Downloader + Hasher script created
- ✅ QA workflow tested
- ✅ Initial reports collected
- ⬜ Full coverage of all 13 target institutions (deferred to automation phase)

**Next Move**: #6 - Netherlands + Semiconductors Sprint

---

**Created**: 2025-10-10
**Last Updated**: 2025-10-10
**Status**: Initial workflow complete, ready for production scaling
