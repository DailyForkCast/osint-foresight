# ASPI Data Accessibility Report

**Generated:** 2025-10-11
**Investigation Target:** ASPI China Tech Map and related ASPI data sources
**Request:** Determine downloadable data from https://chinatechmap.aspi.org.au/#/data/

---

## Executive Summary

ASPI (Australian Strategic Policy Institute) maintains several valuable intelligence databases for China technology tracking, but **public bulk data access is limited**. Websites employ anti-scraping protections (HTTP 403/429), and no documented APIs or bulk export functionality exists for the main tools. Data access requires either:
1. Manual interaction with web interfaces
2. Direct contact with ASPI for bulk data requests
3. Downloading published PDF reports

---

## ASPI Data Sources Identified

### 1. China Tech Map
**URL:** https://chinatechmap.aspi.org.au/
**Status:** Active, automated access blocked (HTTP 403)

**Dataset Scope:**
- **3,800+ global entries** tracking Chinese tech company expansion
- **38,000+ total data points** (15 categories per entry)
- **26,000+ datapoints** geo-locating 2,500+ overseas presence points
- **23 companies and organizations** tracked

**Data Categories:**
- 5G relationships
- 'Smart cities' and 'public security' solutions
- Surveillance relationships
- Research and university partnerships
- Submarine cables
- Terrestrial cables
- Significant telecommunications and ICT projects
- Foreign investment

**Sectors Covered:**
- Telecommunications
- Technology
- Internet
- Biotechnology
- AI
- Surveillance
- E-commerce
- Finance
- Big data
- Cloud computing
- Smart city
- Social media

**Data Access:**
- ❌ No documented bulk download/export
- ❌ No public API
- ✅ Interactive web interface (manual use)
- ❓ Unknown if export feature exists in web UI (couldn't test due to 403)

---

### 2. Critical Technology Tracker
**URL:** https://techtracker.aspi.org.au/
**Status:** Active, partial automated access

**Dataset Scope:**
- **64 critical technologies** tracked
- **21 years of data** (2003-2023)
- Country comparison capabilities
- Research talent flow analysis

**Technology Categories:**
- Advanced information & communication technologies
- AI technologies
- Biotechnology
- Energy & environment
- Quantum technologies
- Defense technologies
- Manufacturing technologies
- Sensing technologies

**Data Access:**
- ❌ No documented API
- ❌ No bulk export functionality found
- ✅ Interactive comparison interface
- ✅ PDF reports downloadable from S3
- 📧 Data partnerships: [email protected]

---

### 3. China Defence Universities Tracker
**URL:** https://unitracker.aspi.org.au/
**Status:** Active, automated access blocked (HTTP 429)

**Dataset Scope:**
- University-defense research relationships
- Seven Sons universities tracking
- Research partnerships and collaborations

**Data Access:**
- ❌ Rate limited for automated access
- ❓ Unknown export capabilities

---

### 4. Xinjiang Data Project
**URL:** https://xjdp.aspi.org.au/data/
**Status:** Active, automated access blocked (HTTP 403)

**Dataset Scope:**
- Xinjiang detention facilities mapping
- Surveillance infrastructure
- Population monitoring systems

**Data Access:**
- ✅ Dedicated "Data & charts" download section exists
- ❌ Could not access due to 403 blocking
- 💡 Most likely to have CSV/Excel exports based on page structure

---

## Downloadable Resources

### PDF Reports (Confirmed Accessible)

**China Tech Map Series:**
- Location: `https://ad-aspi.s3.amazonaws.com/` (various reports)
- Access: ✅ Direct download via S3 URLs
- Format: PDF

**Critical Technology Tracker Reports:**
- Primary Report (2023): `ad-aspi.s3.ap-southeast-2.amazonaws.com/2023-03/ASPIs%20Critical%20Technology%20Tracker_0.pdf`
- Two-Decade Report (2024): `ad-aspi.s3.ap-southeast-2.amazonaws.com/2024-08/ASPIs%20two-decade%20Critical%20Technology%20Tracker_1.pdf`
- Appendix: `ad-aspi.s3.ap-southeast-2.amazonaws.com/2023-03/PB69-CriticalTechTracker-Appendix-1.1_0.pdf`
- Access: ✅ Direct download
- Format: PDF

---

## Anti-Scraping Protections

ASPI implements multiple access controls:

1. **HTTP 403 Forbidden:** Blocks most automated fetches
2. **HTTP 429 Rate Limiting:** Throttles repeated requests
3. **No robots.txt guidance:** No crawling permissions defined
4. **Interactive JavaScript interfaces:** Data loaded dynamically

---

## Recommendations

### For Immediate Use:

**Option 1: Manual Data Collection**
- Visit https://chinatechmap.aspi.org.au/ manually
- Test if web UI has export/download button (not visible to automated tools)
- Document available export formats

**Option 2: PDF Report Analysis**
- Download accessible PDF reports from S3
- Extract structured data from reports using PyMuPDF
- Build custom database from report findings

**Option 3: Contact ASPI Directly**
- Email: [email protected]
- Request: Bulk data access for research/analysis
- Mention: Government or academic partnership opportunities

### For Integration with OSINT Foresight:

**Priority 1: Xinjiang Data Project Download**
- Manually visit https://xjdp.aspi.org.au/data/
- Download available CSV/Excel files
- Import into osint_master.db

**Priority 2: Critical Technology Tracker PDF Processing**
- Download 2024 two-decade report
- Extract technology leadership rankings
- Cross-reference with USPTO, OpenAlex data

**Priority 3: Manual China Tech Map Export**
- If web UI allows CSV export, download manually
- Process 3,800+ entries for integration
- Add to Phase 0 data sources

**Priority 4: Request Bulk Access**
- Contact ASPI for researcher/government data access
- Negotiate automated API or bulk dumps
- Establish ongoing data partnership

---

## Technical Feasibility Assessment

| Data Source | Bulk Download | API Access | Manual Export | PDF Reports | Integration Priority |
|-------------|---------------|------------|---------------|-------------|---------------------|
| China Tech Map | ❌ Not found | ❌ No | ❓ Unknown | ✅ Yes | HIGH |
| Critical Tech Tracker | ❌ No | ❌ No | ❌ No | ✅ Yes | MEDIUM |
| Defence Universities Tracker | ❌ No | ❌ No | ❓ Unknown | ❓ Unknown | HIGH |
| Xinjiang Data Project | ✅ Likely | ❌ No | ✅ Yes | ✅ Yes | LOW |

---

## Integration Status

**Current Status:** NOT INTEGRATED
**Blocking Issues:**
1. No automated bulk download available
2. Anti-scraping protections prevent direct extraction
3. Unknown if web UI export features exist

**Next Steps:**
1. ✅ Manual browser test of China Tech Map export functionality
2. 📧 Contact ASPI for bulk data access
3. 📄 Process available PDF reports
4. 🔄 Consider web automation with Selenium (if legally permitted)

**Estimated Manual Effort:**
- China Tech Map manual export: 30 minutes
- Xinjiang Data download: 15 minutes
- PDF report processing: 2-3 hours
- Total: ~4 hours for initial data acquisition

---

## Legal and Ethical Considerations

- **Terms of Service:** Should be reviewed before any automated access
- **Research Use:** ASPI data intended for research, policy analysis
- **Attribution:** All ASPI data must be properly cited
- **Automation:** Web scraping may violate ToS; contact ASPI for permission

---

## Conclusion

**Can we download ASPI China Tech Map data?**

**Short Answer:** Not through automated means. Manual export or ASPI partnership required.

**Best Path Forward:**
1. Manually test chinatechmap.aspi.org.au for export button
2. Download Xinjiang Data Project datasets manually
3. Contact [email protected] for bulk access to China Tech Map
4. Process PDF reports in interim

**Value Proposition:**
- 3,800+ Chinese tech company global presence entries
- Validates and enriches existing OSINT data (TED, USPTO, OpenAlex)
- Cross-references Seven Sons universities already in BIS Entity List
- Provides surveillance/smart city technology mappings

**Recommendation:** HIGH PRIORITY for manual acquisition, MEDIUM PRIORITY for immediate automated integration (not feasible without ASPI cooperation).
