# Netherlands + Semiconductors Sprint - Status

**Date**: 2025-10-10
**Status**: Infrastructure Created, Manual Collection Recommended
**Move**: #6 from Next 10 Moves

---

## Objective

Target Dutch and EU semiconductor resilience, export controls, and ASML-related research:
- Parliamentary reports
- Innovation funding briefs
- Think-tank analyses
- ASML export control policy
- Netherlands-China technology relations

---

## Script Created

**Location**: `scripts/collectors/netherlands_semiconductors_finder.py`

**Target Sources**:
1. Clingendael Institute (Dutch international relations)
2. Rathenau Institute (Dutch technology assessment)
3. European Commission Chips Act documentation

**Keywords**:
- Netherlands: netherlands, dutch, holland, asml, eindhoven, benelux
- Semiconductors: semiconductor, chip, asml, lithography, euv, microchip, fabrication
- Policy: export control, chips act, semiconductor resilience, strategic autonomy
- China: china, chinese, prc, beijing, sino-

---

## Execution Results

**Initial Run**: 0 reports found

**Likely Reasons**:
1. **Dynamic Content**: Many government and think tank sites use JavaScript rendering
2. **Form-Based Search**: Some sites require form submissions that simple GET requests can't access
3. **Authentication**: Some PDFs may be behind login/registration
4. **Structure Changes**: Website HTML structures may have changed since script development

---

## Alternative Approach: Manual Collection

Given web scraping challenges, recommend manual collection for high-value sources:

### Priority Sources (Manual Download)

#### 1. European Commission - Chips Act
**URL**: https://digital-strategy.ec.europa.eu/en/policies/european-chips-act

**Key Documents**:
- European Chips Act Regulation (EU) 2023/1781
- Chips Act Implementation Plan
- State Aid Guidelines for Semiconductors

#### 2. Netherlands Government (Rijksoverheid)
**URL**: https://www.government.nl/topics/export-controls

**Key Documents**:
- ASML export license policy statements
- Netherlands semiconductor strategy
- Dual-use export control annual reports

#### 3. Clingendael Institute
**URL**: https://www.clingendael.org
**Search**: "semiconductors", "asml", "technology china"

**Expected**: Policy briefs on Netherlands-China tech relations

#### 4. Rathenau Institute
**URL**: https://www.rathenau.nl/en
**Search**: "semiconductors", "innovation policy", "technology assessment"

**Expected**: Technology assessment reports on semiconductor strategy

#### 5. Dutch Parliament (Tweede Kamer)
**URL**: https://www.tweedekamer.nl
**Search**: "ASML", "exportcontrole", "halfgeleiders"

**Expected**: Parliamentary debates and reports on ASML export controls

---

## Manual Collection Workflow

### Step 1: Identify Reports
- Visit each priority source
- Search for semiconductor/ASML/China keywords
- Filter for 2015-present
- Verify PDF/DOCX availability

### Step 2: Download and Organize
- Save to `data/external/netherlands_semiconductors/manual/`
- Use naming: `{year}_{publisher}_{title_slug}.pdf`
- Document source URL in accompanying JSON

### Step 3: Process with Existing Tools
```bash
# Use downloader to hash and extract metadata
python scripts/collectors/eu_mcf_report_downloader.py \
  data/external/netherlands_semiconductors/manual_collection.json
```

### Step 4: Import to Database
```bash
python scripts/importers/import_thinktank_reports.py \
  --input data/external/netherlands_semiconductors/downloads
```

---

## Known High-Value Reports

### European Chips Act Official Documents
1. **Regulation (EU) 2023/1781** - European Chips Act
   - Published: 2023-09-21
   - URL: https://eur-lex.europa.eu/eli/reg/2023/1781/oj
   - Status: Manually downloadable

2. **European Chips Act Communication**
   - Published: 2022-02-08
   - Document: COM(2022) 45 final
   - URL: https://ec.europa.eu/commission/presscorner/detail/en/ip_22_729

### Netherlands-China Technology Policy
3. **Clingendael: Dutch-Chinese Tech Relations**
   - Search ongoing
   - Expected reports on export controls and ASML

4. **Rathenau: Technology Assessment**
   - Search ongoing
   - Expected reports on semiconductor innovation policy

---

## Gap Analysis Impact

**Current Gap**: East Asia × Semiconductors (0 reports)

**Target**: 5-10 Netherlands semiconductor policy reports

**Impact**:
- Fill East Asia × Semiconductors gap
- Add Europe × Semiconductors depth
- Document ASML export control evolution
- Track Chips Act implementation

---

## Next Steps

### Immediate
1. Manual download of EU Chips Act regulation
2. Search Clingendael for ASML/China reports
3. Check Rathenau publications archive
4. Search Dutch Parliament for ASML debates

### Medium-Term
1. Enhance scraper with Selenium for JavaScript sites
2. Add form-based search capabilities
3. Implement PDF extraction from embedded viewers
4. Add retry logic with different user agents

---

## Lessons Learned

### Web Scraping Challenges
1. **Government Sites**: Often require complex navigation, forms, or authentication
2. **Think Tanks**: HTML structures vary widely, require site-specific scrapers
3. **PDF Location**: PDFs may be embedded, behind download buttons, or require POST requests
4. **Rate Limiting**: Need to balance speed with avoiding IP blocks

### Effective Alternatives
1. **Manual Collection**: Often faster for small (<20) document sets
2. **API Access**: Some organizations offer APIs (check EC Open Data Portal)
3. **Official Repositories**: EUR-Lex for EU legislation, better structured
4. **Direct Contact**: Email researchers/communications offices for document lists

---

## Move 6 Status

**Status**: ⚠️ INFRASTRUCTURE READY, MANUAL COLLECTION NEEDED

**Completion Criteria**:
- ✅ Finder script created
- ✅ Target sources identified
- ✅ Keywords and filters defined
- ⬜ Reports collected (recommended: manual)
- ⬜ Reports imported to database

**Recommendation**: Proceed to Move 7 (Backfill and Enrich Existing Reports) while manually collecting Netherlands semiconductor reports in parallel.

**Next Move**: #7 - Backfill and Enrich Existing Reports

---

**Created**: 2025-10-10
**Status**: Scraper infrastructure ready, manual collection recommended for high-value sources
