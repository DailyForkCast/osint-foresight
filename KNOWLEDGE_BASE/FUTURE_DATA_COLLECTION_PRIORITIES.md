# Future Data Collection Priorities
**Date:** 2025-11-08
**Basis:** Real gaps identified during EU-China quantum collaboration analysis
**Principle:** Driven by actual work questions, not speculative "comprehensive coverage"

---

## TIER 1: CRITICAL GAPS (Identified from Quantum Analysis)

### 1. National Research Council Funding

**Gap:** We have EU-level funding (CORDIS) but not national-level research funding

**Needed:**
- **Germany:** DFG (Deutsche Forschungsgemeinschaft) - grants database
- **France:** ANR (Agence Nationale de la Recherche) - funded projects
- **Netherlands:** NWO (Nederlandse Organisatie voor Wetenschappelijk Onderzoek)
- **UK:** UKRI (UK Research and Innovation) - grants data
- **Italy:** MIUR research funding
- **Spain:** AEI (Agencia Estatal de Investigación)

**Collection Method:**
- Most have public databases/APIs
- Structured grant data (PI, institution, amount, dates)
- Searchable by keyword and institution

**Estimated Effort:** 2-4 weeks
**Value:** HIGH - fills major gap in government-funded collaboration

---

### 2. European Patent Office (EPO) - EU-China Quantum Patents

**Gap:** We have USPTO (US patents) but not EPO (European patents)

**Needed:**
- EPO patent database
- Quantum-related patents (IPC/CPC codes)
- EU inventor + Chinese assignee combinations
- Joint EU-China patent filings

**Collection Method:**
- EPO Open Patent Services API
- Bulk download available
- Similar structure to USPTO

**Estimated Effort:** 1-2 weeks
**Value:** HIGH - shows commercialization and technology transfer

---

### 3. Chinese Quantum Companies & Investment in EU

**Gap:** GLEIF shows EU companies but not Chinese ownership/investment amounts

**Needed:**
- Crunchbase/PitchBook-style investment data
- Chinese VC investments in EU quantum startups
- M&A activity (Chinese acquisition of EU quantum firms)
- Joint venture structures

**Collection Method:**
- Free alternatives: Companies House (UK), Handelsregister (DE) filings
- PitchBook data (may require subscription)
- SEC 13D/13G filings (Chinese investment in US-listed EU firms)
- News monitoring for quantum investment announcements

**Estimated Effort:** 3-4 weeks
**Value:** MODERATE-HIGH - private sector blind spot

---

### 4. Bilateral Science & Technology Agreements

**Gap:** No data on government-to-government quantum agreements

**Needed:**
- China-Germany S&T cooperation agreements
- China-France quantum collaboration MoUs
- China-Netherlands bilateral research programs
- China-EU quantum flagship participation (if any)

**Collection Method:**
- Government ministry websites (scraping)
- Treaty databases (UN, national foreign ministry sites)
- Press releases and official announcements
- Parliamentary documents/hearings

**Estimated Effort:** 2-3 weeks
**Value:** HIGH - shows formal government-level collaboration

---

## TIER 2: IMPORTANT BUT SECONDARY

### 5. Conference Proceedings & Presentations

**Gap:** Publications show collaborations, but not conference participation

**Needed:**
- Major quantum conferences (attendance, co-presentations)
- IEEE Quantum Week
- APS March Meeting (quantum sessions)
- European Quantum Electronics Conference

**Collection Method:**
- Conference proceeding databases
- Program committee memberships
- Co-author analysis from conference papers

**Estimated Effort:** 1-2 weeks
**Value:** MODERATE - shows informal networks

---

### 6. Quantum Technology Startups Database

**Gap:** GLEIF only has established companies with LEI

**Needed:**
- EU quantum startup ecosystem
- Founder backgrounds (Chinese diaspora?)
- Funding sources
- Technology focus areas

**Collection Method:**
- Dealroom.co (European startups)
- AngelList / Crunchbase
- National quantum technology hubs
- EU Quantum Flagship participant lists

**Estimated Effort:** 1-2 weeks
**Value:** MODERATE - startup exposure assessment

---

### 7. Chinese Quantum Policy Documents

**Gap:** You mentioned wanting MCF and Five Year Plans

**Needed:**
- 14th & 15th Five Year Plan quantum sections
- Made in China 2025 quantum targets
- MCF quantum technology priorities
- National Medium- and Long-Term Program for Science and Technology Development

**Collection Method:**
- CSET translations (Georgetown)
- ChinaFile policy database
- Official Chinese government portals (english.gov.cn)
- Academic analyses and translations

**Estimated Effort:** 1 week (mostly collection/reading)
**Value:** MODERATE - provides context for Chinese strategy

---

### 8. Research Mobility & Talent Flow

**Gap:** Publications show collaboration but not researcher exchanges

**Needed:**
- Chinese quantum researchers at EU institutions
- EU researchers at Chinese quantum labs
- Joint PhD programs
- Visiting scholar programs

**Collection Method:**
- University staff directories (web scraping)
- LinkedIn profiles (quantum researchers with EU + China experience)
- Visa data (where available)
- University exchange program announcements

**Estimated Effort:** 2-3 weeks
**Value:** MODERATE-HIGH - human intelligence network mapping

---

## TIER 3: NICE TO HAVE

### 9. Defense & Intelligence Quantum Programs

**Gap:** Classified programs by definition not in open sources

**Needed:**
- Declassified program information
- Budget line items (where public)
- Defense contractor quantum work
- Export control enforcement cases

**Collection Method:**
- USAspending (defense quantum contracts) - already have
- EU defense procurement (EDA database if accessible)
- Freedom of Information requests (FOIA)
- Academic papers citing defense funding

**Estimated Effort:** Ongoing monitoring
**Value:** LOW (mostly classified, limited OSINT availability)

---

### 10. Social Media & Informal Networks

**Gap:** Formal collaboration captured, informal networks invisible

**Needed:**
- Twitter/X quantum researcher networks
- LinkedIn professional connections
- ResearchGate collaborations
- WeChat academic groups (if accessible)

**Collection Method:**
- Social network analysis tools
- API scraping (where permitted)
- Public profile analysis

**Estimated Effort:** 2-4 weeks
**Value:** LOW-MODERATE (privacy concerns, data quality issues)

---

## IMPLEMENTATION STRATEGY

### Principle: **Work-Driven, Not Speculation**

**DON'T:** Build all of this because it might be useful someday

**DO:** When you get a work question, check:
1. Can I answer with existing data?
2. If no, which Tier 1 source would help?
3. Collect ONLY that source
4. Validate it works for the question
5. Then consider next source based on next question

### Example Workflow:

**Work Question:** "Which EU quantum companies have Chinese investment?"

**Check existing:** GLEIF has companies but not investment data ✗

**Consult priority list:** Tier 1 #3 - Chinese investment tracking

**Collect:** Companies House UK filings, German Handelsregister for quantum companies

**Validate:** Answer the work question

**Iterate:** If helpful, expand to more countries. If not helpful, try different source.

---

## CURRENT STATUS

### What You Have (Validated):
✅ CORDIS - EU research funding
✅ OpenAlex - Academic publications
✅ ArXiv - Quantum preprints
✅ GLEIF - EU companies
✅ USPTO - US patents
✅ BIS Entity List - Export controls

### What You Need Next (Based on Real Gap):
🎯 **Priority 1:** National research council data (Tier 1 #1)
   → Fills government funding gap you just hit

🎯 **Priority 2:** EPO patents (Tier 1 #2)
   → Complements USPTO, shows EU-specific IP transfer

🎯 **Priority 3:** Chinese investment data (Tier 1 #3)
   → Private sector gap

**Don't collect all at once.** Collect when needed for specific work questions.

---

## ANTI-PATTERNS TO AVOID

❌ **"Let me collect all Tier 1 sources before using the system"**
✅ **"I'll add Tier 1 #1 (DFG) because my next work question needs German funding data"**

❌ **"I should have comprehensive coverage of all funding sources"**
✅ **"I'll add sources when I hit gaps answering real questions"**

❌ **"MCF documents might be useful someday"**
✅ **"I need MCF quantum priorities to map against this EU collaboration network"**

---

## VALIDATION CHECKPOINT

**Before collecting ANY new data source, ask:**

1. **Do I have a specific work question that needs this?** (Not "might need" - NEED)
2. **Did I exhaust existing data first?** (Tried all queries, confirmed it's not there)
3. **Will this source actually answer the question?** (Not just add context)
4. **Can I validate it's useful within 1 week?** (Test with small sample first)

**If all 4 answers are YES → Collect**
**If any answer is NO → Wait for different question or find different source**

---

## ESTIMATED TOTAL EFFORT

**If you collected everything on this list:** 20-30 weeks (6-8 months full-time)

**If you collect based on work questions:** 1-2 sources per month as needed (sustainable)

**Recommendation:** Work-driven collection, not comprehensive build-out

---

**Last Updated:** 2025-11-08
**Next Review:** After completing 3-5 more work analyses (identify patterns in gaps)
