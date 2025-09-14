# Italy-US Overlap: Immediate Computer-Based Exploitation Tasks

*Generated: 2025-09-14 13:10*
*Location: C:\Projects\OSINT - Foresight*

## PRIORITY 1: DO RIGHT NOW (Next 2 Hours)

### Task 1: FPDS Leonardo DRS Contracts (30 min)
**Platform:** https://www.fpds.gov/ezsearch/fpdsportal
**Action:** Advanced Search
**Query:**
- Vendor Name: "Leonardo DRS"
- Date Range: 01/01/2020 to Present
- Export: CSV with all fields
**Output:** `data/collected/italy_us/leonardo_drs_contracts.csv`
**Value:** Direct visibility into US government revenue streams

### Task 2: SEC EDGAR Leonardo 10-K (20 min)
**URL:** https://www.sec.gov/ix?doc=/Archives/edgar/data/1698027/000169802724000004/drs-20231231.htm
**Extract:**
- Revenue by Customer table (search: "Revenue by Customer")
- Backlog table (search: "Backlog")
- Major Programs list
- Related Party Transactions with Leonardo S.p.A.
**Output:** Copy/paste into `leonardo_drs_10k_extract.txt`
**Value:** $3B+ US defense revenue breakdown

### Task 3: Scopus MIT-Politecnico Papers (45 min)
**Platform:** https://www.scopus.com/search/form.uri
**Query:** `AFFIL(MIT) AND AFFIL("Politecnico di Milano") AND KEY(quantum)`
**Date Range:** 2020-2025
**Export:** CSV with abstracts
**Output:** `mit_politecnico_quantum.csv`
**Value:** Quantum computing collaboration network

### Task 4: SAM.gov Leonardo Clearances (15 min)
**URL:** https://sam.gov/content/entity-information
**Search:** Leonardo DRS, Inc.
**CAGE Code:** 0Z2Y6
**Extract:**
- Facility clearance level
- Active NAICS codes
- Point of contact names
**Output:** `leonardo_sam_profile.txt`

### Task 5: Google Patents Joint IP (30 min)
**URL:** https://patents.google.com
**Queries:**
1. `assignee:"Massachusetts Institute of Technology" inventor:Italy`
2. `assignee:Leonardo assignee:("Boeing" OR "Lockheed")`
3. `assignee:"Politecnico di Milano" inventor:"United States"`
**Export:** Download patent list as CSV
**Output:** `italy_us_patents.csv`

## PRIORITY 2: TODAY (Next 4 Hours)

### LinkedIn Researcher Tracking
**Platform:** LinkedIn (or Sales Navigator if available)
**Searches:**
1. Current: "Leonardo DRS" + Past: "Raytheon OR Lockheed Martin"
2. Current: "MIT" + Past: "Politecnico di Milano"
3. Keywords: "quantum photonics" + Location: "Italy" + Company: "US university"
**Action:** Export profiles to Excel
**Value:** Personnel movement patterns

### USAspending.gov Analysis
**URL:** https://www.usaspending.gov/search
**Recipient Search:** "Leonardo DRS"
**Time Period:** FY2020-FY2025
**Download:** Detailed CSV with sub-awards
**Analysis Focus:** Geographic distribution of work

### ORCID Researcher Movement
**URL:** https://orcid.org/orcid-search/search
**Query:** `past-institution:"MIT" current-institution:"Politecnico"`
**Export:** Researcher list with publication history
**Value:** Brain drain/gain patterns

## QUICK WINS (< 15 min each)

### Immediate Google Searches:
```
site:*.mil "Leonardo DRS"
site:*.gov "Fincantieri Marine Group"
site:mit.edu "Politecnico di Milano"
site:stanford.edu "Sapienza University"
```

### Document Downloads:
- Leonardo Annual Report 2023: https://www.leonardo.com/documents/15646808/0/Annual+Report+2023.pdf
- Fincantieri Investor Presentation: https://www.fincantieri.com/en/investors/
- MIT-Italy Program Report: https://misti.mit.edu/italy

### GitHub Code Search:
- https://github.com/search?q=org:leonardo+quantum
- https://github.com/search?q=MIT+Politecnico+photonics

## AUTOMATION SCRIPTS CREATED

Located in: `C:\Projects\OSINT - Foresight\scripts\exploitation\`

1. **fpds_leonardo_extractor.py** - Generates FPDS.gov queries
2. **mit_politecnico_researcher_mapper.py** - Maps research collaborations
3. **sec_edgar_italian_analyzer.py** - SEC filing analysis
4. **italy_us_master_collector.py** - Master orchestration

## COLLECTION TOOLS READY

1. **Dashboard:** `data/collected/italy_us/collection_dashboard_[timestamp].html`
   - Interactive checklist
   - Direct platform links
   - Progress tracking

2. **Launcher:** `data/collected/italy_us/launch_collection_platforms.bat`
   - Opens all platforms
   - Sequenced by priority

3. **Tracker:** `data/collected/italy_us/collection_tracker_[timestamp].json`
   - Records completion status
   - Notes and blockers

## EXPECTED OUTPUTS

After 2 hours you should have:
- Leonardo DRS complete contract history
- Financial breakdown of Italian entities in US
- Research collaboration network map
- Patent co-invention matrix
- Researcher movement patterns

After 4 hours you should have:
- Complete supply chain overlap mapping
- Department-level collaboration inventory
- Standards body participation matrix
- Equity ownership chains

## NEXT STEPS

1. Run all Priority 1 tasks NOW
2. Save all outputs to `data/collected/italy_us/`
3. Run analysis scripts on collected data
4. Generate intelligence brief
5. Update micro-artifacts in phase files

---

**START HERE:** Open FPDS.gov and search for "Leonardo DRS"

**Time to first intelligence:** 30 minutes
**Time to actionable report:** 2 hours
**Time to complete collection:** 4-6 hours

All tasks designed for single analyst at computer.
No field work or classified access required.
Focus on open source, publicly available data.
