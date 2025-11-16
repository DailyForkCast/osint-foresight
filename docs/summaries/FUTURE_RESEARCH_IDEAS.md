# Future Research Ideas - Long-Term Projects
**Purpose:** Track potential research directions for future investigation
**Status:** Aspirational / "Someday" projects requiring refinement

---

## 1. China State-Owned Enterprises (SOEs) - Dual-Use Technology Deep-Dive

**Concept:** Comprehensive analysis of Chinese SOEs engaged in dual-use technology development

**Initial Scope Ideas:**
- Identify all major Chinese SOEs in defense/civilian technology sectors
- Map ownership structures (State Council, SASAC, provincial governments, PLA)
- Track global partnerships and joint ventures
- Assess technology transfer risks
- Analyze export patterns and international subsidiaries

**Key Questions to Explore:**
- Which SOEs have both military and civilian technology divisions?
- How do SOEs acquire foreign technology (M&A, partnerships, licensing)?
- What are the linkages between SOEs and PLA/defense sector?
- How have SOEs evolved post-2015 reforms?
- What role do SOEs play in Made in China 2025 / China Standards 2035?

**Potential Data Sources:**
- GLEIF (global corporate structures)
- SASAC (State-owned Assets Supervision and Administration Commission) public filings
- Historical SOE database (already in project: `data/prc_soe_historical_database.json`)
- PRC SOE monitoring system (already implemented in project)
- Wind Database (Chinese financial data)
- Capital IQ / Bloomberg (ownership structures)
- Patent databases (USPTO, EPO, WIPO) - technology development tracking
- Trade data (customs, shipping records) - export patterns

**Complexity Factors:**
- SOE definition varies (central vs. local vs. mixed ownership)
- Frequent reorganizations and mergers
- Opaque ownership structures (shell companies, subsidiaries)
- Data availability challenges (limited English-language sources)

**Refinement Needed:**
1. **Scope boundaries:** Which sectors? (Aerospace, semiconductors, AI, biotech, energy, telecom?)
2. **Time period:** Historical analysis vs. current snapshot?
3. **Geographic focus:** Global footprint vs. specific regions (Europe, US, Asia)?
4. **Deliverable format:** Database? Interactive visualization? Report series?
5. **Use case:** Academic research? Policy analysis? Business intelligence?

**Relevant Existing Project Assets:**
- `data/prc_soe_database.json` - Current SOE database
- `data/prc_soe_historical_database.json` - Historical tracking (v1.0 backup available)
- SOE detection/validation scripts already implemented
- PRC entity identifiers framework in place (`data/prc_identifiers.json`)

**Estimated Effort:** Major project (6-12 months for comprehensive version)

**Priority:** FUTURE / "Someday" (after current country assessments complete)

---

## 2. Technology-Focused Pivots (From Country-by-Country)

**Concept:** Shift from country assessments to technology domain reports

**Potential Domains:**
- Quantum computing: Global collaboration networks, Chinese capabilities
- Semiconductor manufacturing equipment: Beyond ASML ecosystem analysis
- AI/machine learning: Research collaborations, talent flows
- Advanced materials: Graphene, rare earths, next-gen battery tech
- Biotechnology: CRISPR, synthetic biology, genomics

**Approach:** Leverage existing country data, re-index by technology

**Status:** Mentioned in Netherlands v1 report, ready to pivot after multi-country baseline

---

## 3. Subnational Analysis Expansion

**Concept:** Go beyond national-level to regional/provincial analysis

**Focus Areas:**
- Dutch provinces with semiconductor clusters (Eindhoven ecosystem)
- Chinese provincial SOE structures
- Regional innovation policies
- Sister-city agreements and their technology implications

**Status:** Pilot completed for 42 countries, ready for deeper dives

---

## 4. Temporal Network Analysis

**Concept:** Track evolution of partnerships over time

**Questions:**
- When did high-risk partnerships begin?
- Policy impact assessment (did export controls reduce collaborations?)
- Emerging vs. declining collaboration patterns
- Early warning indicators for future risks

**Data:** Already collected, needs time-series processing

---

## 5. Supply Chain Deep-Dive Beyond ASML

**Concept:** Map full Netherlands semiconductor ecosystem

**Companies to Analyze:**
- ASM International (atomic layer deposition)
- NXP Semiconductors (automotive, IoT)
- Philips spin-offs and heritage companies
- Materials suppliers
- Start-up ecosystem (scrappy companies per user's philosophy)

**Expansion:** "From Googles to scrappy start-ups" comprehensive approach

---

## 6. Academic-to-Industry Technology Transfer Tracking

**Concept:** Follow research collaborations from publication to commercialization

**Approach:**
- Track patents emerging from academic collaborations
- Identify start-ups spun out of joint research
- Map researcher movement between academia and industry
- Assess technology maturation timelines

**Challenge:** Long time horizons, complex attribution

---

## Notes for Future Development

**User's Philosophy (Key Guidance):**
- "From the Googles and Microsofts down to the scrappy start-ups"
- Comprehensive understanding from granular to 50,000 feet
- v1 → v2 → v3 iteration approach (ship early, refine continuously)
- Learn by doing, not planning paralysis

**Project Structure Lessons Learned:**
- Always check `data/external/` FIRST before searching elsewhere
- Cookiecutter Data Science structure works well
- Technology-indexed data enables future pivots
- Manual verification critical for high-stakes findings

**Current Project Status (as of Nov 7, 2025):**
- Netherlands v1: Complete (report written, deadline Nov 23)
- ASPI tracker: Integrated (159 institutions)
- WSTS + SIA: Integrated (market context)
- Next countries: Germany, France, Italy (build comparative framework)

---

**Document Status:** Living document - add ideas as they emerge
**Review Frequency:** Quarterly (or when current project phase completes)
**Decision Criteria:** Align with project goals, data availability, effort vs. impact
