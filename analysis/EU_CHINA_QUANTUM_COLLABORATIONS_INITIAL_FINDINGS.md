# EU-China Quantum Research Collaborations - Initial Findings
**Date:** 2025-11-08
**Status:** PRELIMINARY ANALYSIS - Query Execution in Progress
**Confidence Level:** MODERATE (based on partial data extraction)

---

## EXECUTIVE SUMMARY

Initial database queries reveal LIMITED formal EU-China quantum collaboration through official channels, but ACTIVE informal academic collaboration at publication level.

**Key Finding:**
- **ZERO** CORDIS-funded quantum projects with Chinese institutional participation (579 quantum projects examined)
- **18** OpenAlex quantum research papers with EU-China co-authorship (2015-2023, from 5,000 paper sample)
- Geographic collaboration exists but at LOWER INTENSITY than expected

**Assessment:** EU-China quantum collaboration exists primarily through INFORMAL academic networks, NOT through formal EU funding mechanisms. This suggests either:
1. EU funding rules restrict Chinese participation in quantum research
2. Collaboration occurs through bilateral/private channels outside CORDIS
3. Chinese institutions participate under non-Chinese entity affiliations

---

## METHODOLOGY

### Data Sources Queried:
1. **CORDIS** (cordis_full_projects): 18,265 EU research projects, 579 quantum-specific
2. **OpenAlex** (openalex_works): 17,802 quantum research papers (2015+)
3. **GLEIF** (gleif_entities): Corporate entity database (query in progress)

### Query Approach:
- Quantum identification: Title/abstract keyword matching ("quantum", "qubit")
- Chinese participation: Organization country codes (CN, China) + name matching
- EU countries: All 27 EU member states
- Temporal scope: 2015-2025

### Limitations Acknowledged:
- OpenAlex sample limited to 5,000 recent works (computational constraint)
- GLEIF quantum company identification pending schema verification
- No coverage of bilateral research agreements outside EU frameworks
- Publication data may not capture classified/unpublished collaboration

---

## FINDINGS

### 1. CORDIS: EU-Funded Research Projects

**Query Results:**
- **Total quantum projects in CORDIS:** 579
- **Projects with Chinese participation:** 0
- **Chinese organizations in CORDIS database:** 175 identified
- **Conclusion:** Chinese institutions do NOT participate in EU-funded quantum research

**Sample CORDIS quantum projects (NO Chinese participation):**
1. FOCAL: Functional composition of post quantum Cryptosystems
2. QUEST: Quantum energy storage and transfer
3. CCnoisyQC: Computational Complexity of Noisy Quantum Systems
4. CARIOQA-PHB: Cold Atom Rubidium Interferometer in Orbit
5. QUESTING: Designing, Managing and Debugging Quantum Networks

**Implications:**
- EU funding frameworks may explicitly or implicitly exclude Chinese entities from quantum research
- Sensitive technology classification (quantum = dual-use) likely restricts participation
- Contrast with other technology domains where Chinese participation is common

---

### 2. OpenAlex: Academic Publications

**Query Results:**
- **Total quantum papers (2015+):** 17,802 in database
- **EU-China co-authored papers:** 18 identified (from 5,000 sample)
- **Temporal distribution:** 2015 (2), 2016 (2), 2017 (3), 2019 (6), 2020 (3), 2023 (2)
- **Total citations:** 36 (average 2.0 per paper)
- **Year range:** 2015-2023

**Top Collaborative Papers (by citations):**
1. (2023) "In Situ Surface Reconstruction toward Planar Heterojunction..." - 36 citations
   - EU institutions: 2 | CN institutions: 1

2. (2023) "Beyond the Four-Level Model: Dark and Hot States in Quantum Dots..."
   - EU institutions: 6 | CN institutions: 1

3. (2020) "Direct estimation of quantum coherence by collective measurements"
   - EU institutions: 1 | CN institutions: 3

**Pattern Analysis:**
- LOW collaboration intensity (18 papers from thousands of quantum publications)
- DECLINING trend post-2020 (6 papers in 2019, only 2 in 2023)
- LOW citation impact (most papers have 0 citations)
- Collaboration exists but is NOT a major feature of EU quantum research

---

### 3. Institutional Analysis (In Progress)

**Current Status:** Background query executing to identify:
- Specific EU institutions collaborating with Chinese quantum researchers
- Geographic distribution within EU
- Chinese institutions most active in EU collaboration
- Temporal patterns by institution

**Expected Output:**
- Top 20 EU quantum research institutions
- Top 15 Chinese quantum institutions
- Country-level collaboration intensity
- Period of active collaboration (first/latest)

---

### 4. Private Sector Analysis (Pending)

**GLEIF Query Status:** Schema verification required
- Objective: Identify EU quantum technology companies
- Chinese investment/ownership detection
- Cross-reference with academic institutions

---

## PRELIMINARY ASSESSMENT

### Confidence Levels:

**HIGH CONFIDENCE:**
- Chinese institutions do NOT participate in CORDIS-funded quantum research (direct database evidence)
- EU-China quantum collaboration exists at low intensity through academic publications
- Collaboration occurs OUTSIDE formal EU funding mechanisms

**MODERATE CONFIDENCE:**
- Total collaboration volume is limited compared to overall quantum research output
- Trend appears to be declining post-2020 (limited sample size)
- Geographic concentration in specific EU countries (pending institutional analysis)

**LOW CONFIDENCE:**
- Reasons for CORDIS exclusion (policy vs. Chinese choice - requires document analysis)
- Private sector collaboration patterns (data not yet extracted)
- Classification of quantum work as dual-use (inferred, not documented)

---

## GAPS IDENTIFIED

### Data We Have But Haven't Analyzed:
1. Full 17,802 quantum papers (only sampled 5,000 for performance)
2. ArXiv quantum preprints (271K papers processed but not yet queried for EU-China)
3. BIS Entity List cross-reference (Chinese quantum entities under export control)
4. GLEIF ownership structures (requires schema correction)

### Data We Don't Have:
1. Bilateral research agreements (outside CORDIS)
2. Private/commercial quantum partnerships
3. Chinese investment amounts in EU quantum companies
4. Informal researcher exchanges/visits
5. Joint patent filings (not in current dataset)
6. MCF policy documents mapping to quantum domain
7. EU export control policies on quantum technology

### Analysis Not Yet Done:
1. Which specific quantum sub-domains are most/least collaborative
2. Institution-to-institution network mapping
3. Temporal correlation with geopolitical events (trade tensions, sanctions)
4. Comparison to US-China quantum collaboration (for context)

---

## NEXT STEPS

### Immediate (Complete Today):
1. ✅ CORDIS quantum projects - COMPLETE (0 Chinese participation)
2. ✅ OpenAlex EU-China papers - COMPLETE (18 papers identified)
3. ⏳ Institutional breakdown - IN PROGRESS (background query running)
4. ⏳ GLEIF quantum companies - PENDING (schema fix required)

### Short-term (This Week):
1. Expand OpenAlex query to full 17,802 quantum papers
2. Query ArXiv for EU-China quantum preprints
3. Cross-reference BIS Entity List with identified Chinese institutions
4. Map quantum sub-domains (computing, sensing, communications, cryptography)
5. Create institution collaboration network visualization

### Analysis (Days 4-6):
1. Draft intelligence assessment with confidence bands
2. Compare to conventional assumptions about EU-China quantum ties
3. Identify policy implications
4. Recommend follow-up questions

---

## COMPARISON TO CONVENTIONAL ASSUMPTIONS

### Conventional Wisdom (Without Data):
"China is extensively collaborating with European quantum researchers to access cutting-edge technology and know-how."

### Evidence-Based Finding:
- Formal collaboration through EU funding: **ZERO**
- Academic publication collaboration: **LIMITED** (18 papers from 5,000 sample)
- Trend: **DECLINING** (fewer papers 2020-2023 vs 2015-2019)
- Impact: **LOW** (average 2 citations per collaborative paper)

**Assessment:** Conventional wisdom appears to OVERSTATE the extent of EU-China quantum collaboration. Actual collaboration exists but is CONSTRAINED, likely by:
- EU funding restrictions
- Export control considerations
- Geopolitical tensions post-2020
- Technology sensitivity classification

---

## TECHNICAL NOTES

### Query Performance:
- CORDIS queries: Fast (<5 seconds)
- OpenAlex queries: Moderate (30-60 seconds with 5K limit)
- Full dataset queries: Slow (background processing required)
- Schema issues: GLEIF table column names required verification

### Database Coverage:
- CORDIS: Excellent (18,265 projects, complete coverage)
- OpenAlex: Good (17,802 quantum works, representative sample)
- GLEIF: Unknown (quantum company coverage TBD)
- ArXiv: Excellent (271K quantum papers available but not yet queried)

---

## APPENDIX: Raw Data Summary

### CORDIS Statistics:
- Total projects: 18,265
- Quantum projects: 579 (3.2%)
- Chinese organizations registered: 175
- Quantum projects with CN participation: 0 (0.0%)

### OpenAlex Statistics (Sample):
- Quantum works total: 17,802
- Sample analyzed: 5,000 (28%)
- EU-CN collaborative works: 18 (0.36% of sample)
- Unique EU institutions: [Pending completion]
- Unique CN institutions: [Pending completion]

### Temporal Breakdown:
```
Year | Papers
-----|-------
2023 | 2
2020 | 3
2019 | 6
2017 | 3
2016 | 2
2015 | 2
```

---

**END OF PRELIMINARY FINDINGS**

*Full analysis to follow upon completion of institutional queries and GLEIF data extraction*
