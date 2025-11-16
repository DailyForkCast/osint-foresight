# Data Gaps Tracker

**Purpose:** Document known gaps between verified data and claimed/aggregate data
**Last Updated:** 2025-10-25

---

## Active Data Gaps

### GAP-001: Huawei ICT Academies in Europe

**Status:** OPEN
**Priority:** MEDIUM
**Identified:** 2025-10-25

**Summary:**
Huawei claims 200+ ICT Academies across Europe. We have verified only 30 specific institutions, leaving ~170 academies unidentified.

**Details:**
```
VERIFIED:  30 specific university partnerships
CLAIMED:   200+ ICT Academies (Huawei corporate reports)
GAP:       ~170 academies not individually identified
```

**Source of Claim:**
- Huawei ICT Academy Program 2.0 announcement (2020)
- Huawei European talent ecosystem blog (2023): https://e.huawei.com/en/blogs/industries/insights/2023/huawei-s-european-talent-ecosystem
- Multiple consistent references across years

**Confidence in Claim:** 70%
- Claim is consistent across multiple years and sources
- Huawei has institutional incentive to report accurately (credibility with partners)
- Some potential inflation for marketing purposes
- Our 30 verified partnerships are likely the flagship/most strategic relationships
- Gap likely represents smaller engagements (guest lectures, competitions, internships)

**Strategic Assessment:**
- **High-value targets already captured:** Major research centers (Surrey 5GIC, EURECOM), government-backed partnerships (Ireland), curriculum-embedded programs (Alicante)
- **Gap likely represents:** Lower-impact activities, regional/smaller universities, informal arrangements
- **Intelligence value of gap:** LOW-MEDIUM - Would provide complete picture but flagship relationships already documented

**Collection Priority:** MEDIUM
Rationale: Completeness is valuable but not critical. Strategic partnerships already captured.

**Recommended Collection Methods:**
1. **Huawei ICT Competition participant lists** (Priority: HIGH)
   - Annual global competition publishes participating institutions
   - Source: https://www.huawei.com/minisite/ict-competition-2024-2025-global/en/
   - Accessibility: Public

2. **Freedom of Information requests to education ministries** (Priority: MEDIUM)
   - Request: "List of universities with Huawei partnerships/agreements"
   - Target countries: Germany, France, Italy (likely high counts)
   - Timeline: 3-6 months per request

3. **University partnership database surveys** (Priority: MEDIUM)
   - Systematic survey of European universities
   - Ask: "Do you have active Huawei partnerships?"
   - Resource intensive but comprehensive

4. **Individual university website audits** (Priority: LOW)
   - Crawl university partnership pages for "Huawei" mentions
   - Automated but may miss undisclosed partnerships
   - Good for verification of identified institutions

**Estimated Resources:**
- ICT Competition analysis: 2-3 hours
- FOI requests: 20-30 hours (drafting, following up)
- Systematic survey: 40+ hours
- Website audits: 10-15 hours (with automation)

**Decision:** Recommend ICT Competition analysis as quick win. Other methods defer to lower priority.

---

### GAP-002: CEIAS Country Coverage

**Status:** OPEN
**Priority:** LOW
**Identified:** 2025-10-25

**Summary:**
CEIAS academic tracker covers 10 European countries. 3-4 additional Central/Eastern European countries likely have CEIAS data not yet found.

**Details:**
```
VERIFIED:  10 countries with CEIAS reports
POTENTIAL: 13-14 CEE countries in CEIAS geographic focus
GAP:       3-4 countries may have reports not yet located
```

**Countries with CEIAS Reports (Verified):**
- Slovakia, Romania, Czech Republic, Poland, Hungary
- Slovenia, Bulgaria, Croatia, Greece, Austria

**Potential Missing Countries:**
- Estonia (searched, no report found)
- Latvia (searched, only public opinion survey found)
- Lithuania (event data exists, no systematic country report)
- Serbia (general coverage, no dedicated academic tracker report)

**Confidence in Gap:** 60%
- CEIAS may simply not have covered these countries
- Baltic states have smaller academic sectors (fewer partnerships)
- Serbia may be covered in broader Balkans analysis

**Collection Priority:** LOW
Rationale: Major CEE countries already covered. Baltic states likely have limited China academic engagement.

**Recommended Actions:**
1. Contact CEIAS directly to inquire about additional country reports
2. If Baltic state coverage important, commission custom research
3. Monitor CEIAS publications for new country reports

---

### GAP-003: Bilateral Investment Data

**Status:** OPEN
**Priority:** HIGH
**Identified:** 2025-10-25

**Summary:**
`bilateral_investments` table is completely empty (0 records). Cannot track FDI flows, M&A transactions, or portfolio investments by country.

**Details:**
```
VERIFIED:  0 investment records
NEEDED:    FDI database by country/sector/year
GAP:       Complete absence of investment tracking
```

**Impact:**
- Cannot correlate investments with diplomatic events
- Cannot track pre/post-BRI investment patterns
- Cannot assess economic interdependence by country
- Missing critical component of bilateral relationship assessment

**Data Sources Available:**
1. **Rhodium Group MERICS China Investment Database** (subscription required)
2. **AidData Global Chinese Development Finance Dataset** (free, partial coverage)
3. **National statistics offices** (FDI data, variable quality)
4. **OECD FDI database** (aggregate level)
5. **Dealogic M&A database** (subscription required)

**Collection Priority:** HIGH
Rationale: Investment data is critical for comprehensive bilateral assessment. Major gap in current framework.

**Recommended Approach:**
1. Start with AidData (already have some data in database)
2. Supplement with OECD aggregate data (free, good quality)
3. Consider Rhodium Group subscription if budget allows
4. National statistics as backstop for specific countries

**Estimated Resources:**
- AidData integration: 5-10 hours
- OECD data integration: 8-12 hours
- Per-country national statistics: 2-3 hours each

---

### GAP-004: Diplomatic Posts Data

**Status:** OPEN
**Priority:** MEDIUM
**Identified:** 2025-10-25

**Summary:**
`diplomatic_posts` table is empty (0 records). Cannot track embassy/consulate locations, staffing levels, or diplomatic presence by country.

**Details:**
```
VERIFIED:  0 diplomatic post records
NEEDED:    Embassy/consulate database with staffing levels
GAP:       Complete absence of diplomatic infrastructure data
```

**Impact:**
- Cannot assess diplomatic engagement level by country
- Cannot track diplomatic infrastructure growth over time
- Missing indicator of bilateral relationship priority

**Data Sources:**
1. **Chinese Ministry of Foreign Affairs** (official embassy list)
2. **Europa World database** (subscription, comprehensive)
3. **CIA World Factbook** (free, limited detail)
4. **Individual country foreign ministry databases**

**Collection Priority:** MEDIUM
Rationale: Useful for relationship assessment but not critical for current use cases.

**Recommended Approach:**
- Start with MFA official list (free, authoritative)
- Supplement with Wikipedia (surprisingly comprehensive for embassies)
- Add staffing data opportunistically (harder to find)

---

### GAP-005: Technology Domain Classification

**Status:** OPEN
**Priority:** HIGH
**Identified:** 2025-10-25

**Summary:**
6,344 OpenAlex entities have no technology domain classification. Cannot filter by strategic technology areas (quantum, AI, semiconductors, etc.).

**Details:**
```
ENTITIES:  6,344 OpenAlex institutions/organizations
CLASSIFIED: 0 with technology domain tags
GAP:       100% of entities lack tech domain classification
```

**Impact:**
- Cannot query: "Show quantum computing institutions with China partnerships"
- Cannot assess technology transfer risk by domain
- Cannot prioritize monitoring by strategic technology area

**Classification Sources:**
1. **OpenAlex Topics/Concepts** (via API, authoritative)
2. **ASPI Tech Domains** (manual mapping to entities)
3. **Microsoft Academic Graph** (if OpenAlex mapping available)
4. **Manual curation** (for top 100-200 strategic institutions)

**Collection Priority:** HIGH
Rationale: This is Tier 1 task. Critical for strategic technology risk assessment.

**Recommended Approach:**
1. Use OpenAlex API to fetch topics for each entity
2. Map topics to 10-15 strategic tech domains
3. Store in new `technology_domain` column
4. Manual review for PLA-affiliated institutions

**Estimated Resources:**
- API integration: 8-10 hours
- Topic-to-domain mapping: 4-6 hours
- Manual curation (top 100): 6-8 hours
- **Total:** 18-24 hours

**Status:** This is next priority Tier 1 task after linkage ETLs.

---

## Closed Data Gaps

### GAP-CLOSED-001: Major EU Country Coverage

**Status:** CLOSED
**Closed Date:** 2025-10-25
**Original Priority:** CRITICAL

**Summary:**
Missing 4 major EU economies (Spain, Finland, Ireland, Portugal) from bilateral_countries table.

**Resolution:**
- Added all 4 countries with complete metadata
- Imported 6 Confucius Institutes
- Imported 2 academic partnerships
- Added 1 major Huawei partnership (Spain - Alicante)

**Lessons Learned:**
- Geographic gaps should be addressed early (foundational data)
- CEIAS did not cover all EU countries (Finland, Ireland, Portugal)
- Had to supplement with direct country research

---

## Gap Prioritization Matrix

| Gap ID | Description | Priority | Effort | Impact | Status |
|--------|-------------|----------|--------|--------|--------|
| GAP-005 | Tech domain classification | HIGH | Medium (20h) | High | Open |
| GAP-003 | Bilateral investments | HIGH | High (40h+) | High | Open |
| GAP-001 | Huawei academies (170) | MEDIUM | Medium (25h) | Medium | Open |
| GAP-004 | Diplomatic posts | MEDIUM | Low (10h) | Medium | Open |
| GAP-002 | CEIAS countries (3-4) | LOW | Medium (15h) | Low | Open |

**Recommendation:** Address in order of Priority × Impact / Effort ratio
1. GAP-005 (Tech classification) - Highest ROI
2. GAP-003 (Investments) - Critical but high effort
3. GAP-004 (Diplomatic posts) - Quick win
4. GAP-001 (Huawei) - Completeness only
5. GAP-002 (CEIAS) - Defer until new reports published

---

## Gap Reporting Template

When identifying a new data gap, document using this template:

```markdown
### GAP-XXX: [Title]

**Status:** OPEN
**Priority:** [CRITICAL/HIGH/MEDIUM/LOW]
**Identified:** [Date]

**Summary:**
[One paragraph describing the gap]

**Details:**
VERIFIED:  [What we have]
CLAIMED:   [What is claimed/needed]
GAP:       [Quantification of gap]

**Source of Claim:** [If applicable]
**Confidence in Claim:** [Percentage and reasoning]

**Impact:**
[Bullet list of what we cannot do because of this gap]

**Data Sources Available:**
[Numbered list of potential sources]

**Collection Priority:** [HIGH/MEDIUM/LOW]
**Rationale:** [Why this priority level]

**Recommended Approach:**
[Step-by-step collection plan]

**Estimated Resources:**
[Time/cost estimates]
```

---

*Tracker maintained as living document*
*Review quarterly for new gaps and priority changes*
*Last review: 2025-10-25*
