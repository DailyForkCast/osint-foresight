# BigQuery Available Datasets - Summary
**Date:** 2025-11-12
**Your subscription:** osint-foresight-2025 (paid billing enabled)

---

## Accessible Public Datasets

### 1. Patents (patents-public-data.patents)

**Status:** ACCESSIBLE and actively used
**Size:** 166.9M patents globally, 3+ TB
**Latest update:** February 2025

**Tables available (21 total):**
- `publications` - Main table (166.9M patents)
- `publications_202502` - Latest snapshot (161.6M patents, 2.9 TB)
- Historical snapshots back to 2017

**Data included within publications table:**
- Basic: country_code, filing_date, grant_date, application_number
- Technology: CPC classifications (nested)
- Ownership: assignee_harmonized (companies, universities, individuals)
- People: inventor_harmonized (individual inventors)
- Citations: citation (patent citation network)
- Families: family_id (same invention across jurisdictions)
- Text: title, abstract, claims (full text)

**What we've extracted:**
- Chinese patents: 46.9M (2011-2025)
- Annual time series by technology sector
- 11 MIC2025 priority sectors mapped

**What's still available:**
- Assignees (Huawei, ZTE, Tsinghua University, etc.)
- Citations (innovation quality, technology transfer)
- Inventors (co-invention networks, mobility)
- Patent families (strategic filing patterns)
- Full text (abstracts, claims for NLP)

---

### 2. GitHub Archive (githubarchive.month)

**Status:** ACCESSIBLE
**Coverage:** 178 monthly tables (2011-present)
**Use cases:**
- Open source contribution tracking
- Chinese tech company repositories
- Developer activity patterns
- Technology adoption signals

**Example queries:**
- Huawei, Alibaba, Tencent repository activity
- Chinese developer contributions to strategic projects
- Fork/star patterns for tech assessment

**Cost:** Moderate (~$0.05-0.20 per query depending on scope)

---

### 3. GitHub Repos (bigquery-public-data.github_repos)

**Status:** ACCESSIBLE
**Tables:** 9 tables
**Use cases:**
- Repository metadata
- Commit history analysis
- Programming language usage
- License compliance

---

### 4. Stack Overflow (bigquery-public-data.stackoverflow)

**Status:** ACCESSIBLE
**Tables:** 16 tables
**Coverage:** Questions, answers, users, tags, votes

**Use cases:**
- Technology adoption in China (question patterns)
- Skill development tracking
- Chinese developer activity
- Emerging technology signals

**Example analysis:**
- Questions tagged "semiconductor" from Chinese users
- AI/ML framework adoption over time
- Chinese language vs English question patterns

---

### 5. GDELT (gdelt-bq.gdeltv2)

**Status:** ACCESSIBLE
**Tables:** 62 tables
**Coverage:** Global news events (you already use this)

**Current usage:** EU-China bilateral events
**Additional potential:** Technology news, M&A announcements, policy changes

---

### 6. World Bank Development Indicators (bigquery-public-data.world_bank_wdi)

**Status:** ACCESSIBLE
**Tables:** 6 tables
**Coverage:** Economic indicators by country

**Use cases:**
- R&D spending trends
- GDP context for patent analysis
- Technology infrastructure metrics
- Cross-country comparisons

---

### 7. Python Package Index (bigquery-public-data.pypi)

**Status:** ACCESSIBLE
**Tables:** 3 tables
**Coverage:** Python package downloads, metadata

**Use cases:**
- Chinese AI/ML library adoption (downloads from CN)
- Technology stack analysis
- Dependency tracking for strategic packages

---

### 8. Ethereum Blockchain (bigquery-public-data.crypto_ethereum)

**Status:** ACCESSIBLE
**Tables:** 11 tables
**Use cases:**
- Chinese tech company blockchain activity
- DeFi/Web3 development patterns
- Token launches, NFT activity

---

### 9. GHTorrent (ghtorrent-bq.ght)

**Status:** ACCESSIBLE
**Tables:** 21 tables
**Coverage:** GitHub data mining project

---

### 10. The Met Museum (bigquery-public-data.the_met)

**Status:** ACCESSIBLE
**Relevance:** Low for OSINT-Foresight

---

### 11. NOAA Weather (bigquery-public-data.noaa_gsod)

**Status:** ACCESSIBLE
**Relevance:** Low for current analysis

---

## NOT Available (Checked)

**Research/Academic:**
- Semantic Scholar - Not available
- OpenAlex - Not available
- PubMed - Not available

**Funding:**
- NSF Awards - Not available
- NIH Grants - Not available

**Trade:**
- World Bank International Trade - Not accessible

**Research Papers:**
- COVID-19 Open Research - Not accessible

---

## High-Value Analyses Not Yet Done

### From Patents Dataset (Already Have Access)

**1. Assignee Analysis**
- Huawei patent portfolio evolution (2011-2025)
- ZTE, Xiaomi, ByteDance, Tencent patterns
- Chinese university patenting (Tsinghua, Peking, USTC)
- State-owned enterprise tracking
- Ownership changes (M&A via patent transfers)

**2. Citation Network Analysis**
- Which Chinese patents are highly cited? (quality measure)
- Do Chinese patents cite foreign patents? (technology transfer)
- Citation patterns by sector (semiconductors, AI, quantum)
- Self-citation rates (potential gaming metrics)
- Cross-border knowledge flows

**3. Inventor Network Analysis**
- Co-invention patterns (collaboration networks)
- University-industry collaboration
- International co-inventors (China-US, China-EU)
- Inventor mobility between companies
- Brain drain/gain patterns

**4. Patent Family Analysis**
- Which Chinese inventions filed globally? (strategic importance)
- CNIPA-only vs international filing patterns
- Geographic filing strategies by company
- PCT vs direct national phase

**5. Full Text Analysis**
- Abstract/claim text mining
- Technology convergence detection
- Military-civilian fusion indicators
- Dual-use technology identification

### From GitHub Archive (Newly Available)

**6. Open Source Intelligence**
- Chinese tech company repositories
- Contribution patterns to strategic projects (Linux kernel, AI frameworks)
- Developer hiring signals (new repositories, team growth)
- Technology stack choices

**7. Developer Network Analysis**
- Chinese developers contributing to Western projects
- Western developers contributing to Chinese projects
- Collaboration patterns
- Fork/star networks

### From Stack Overflow (Newly Available)

**8. Technology Adoption Signals**
- Emerging technology questions (quantum, neuromorphic)
- Skill gaps (what Chinese developers asking about)
- Framework adoption (TensorFlow vs PyTorch in China)
- Language patterns (Chinese vs English questions)

### From World Bank WDI (Newly Available)

**9. Economic Context**
- R&D spending vs patent output efficiency
- Technology infrastructure vs innovation
- Cross-country innovation comparisons
- Policy impact assessment

---

## Recommended Next Extractions

**Priority 1: Patent Assignees (Companies/Universities)**
- Extract top 100 Chinese patent assignees (2011-2025)
- Annual time series by assignee
- Sector breakdown
- **Cost estimate:** ~$0.10-0.20
- **Value:** Identify key players, track portfolio growth

**Priority 2: Patent Citations**
- Citation counts for Chinese patents
- Citation patterns (domestic vs international)
- High-impact patent identification
- **Cost estimate:** ~$0.30-0.50
- **Value:** Quality assessment, technology transfer detection

**Priority 3: Inventor Networks**
- Co-inventor patterns
- University-industry collaboration
- International collaboration
- **Cost estimate:** ~$0.20-0.40
- **Value:** Detect collaboration networks, technology transfer

**Priority 4: GitHub Archive - Chinese Tech Companies**
- Huawei, Alibaba, Tencent, ByteDance, Baidu repositories
- Commit patterns, contributor networks
- Technology stack analysis
- **Cost estimate:** ~$0.10-0.30
- **Value:** Real-time development activity tracking

**Priority 5: Stack Overflow - Technology Adoption**
- Chinese developer questions by technology
- Skill development patterns
- Emerging technology interest
- **Cost estimate:** ~$0.05-0.15
- **Value:** Technology adoption signals

---

## Data NOT Available on BigQuery

**Academic Publications:**
- Need alternative sources: OpenAlex API, Semantic Scholar API, Crossref
- Or: Manual downloads from academic databases

**Research Grants/Funding:**
- NSF awards: Use NSF API or data downloads
- NIH grants: Use RePORTER
- European grants: CORDIS API (you already have this)

**Trade Data:**
- UN Comtrade: Via API (you're already registered)
- Not on BigQuery

**Supply Chain Data:**
- No public dataset identified
- Would need commercial data (Bloomberg, FactSet)
- Or: Extract from company filings, news

---

## Summary

**You have BigQuery access to:**
- 166.9M patents globally (47M Chinese)
- GitHub activity (2011-present)
- Stack Overflow (all history)
- GDELT news (you already use)
- World Bank economic indicators
- Python package usage
- Blockchain activity

**Cost so far:** $0.40 total
**Remaining budget:** Effectively unlimited on paid tier

**High-value, low-cost next steps:**
1. Extract patent assignees ($0.20)
2. Extract patent citations ($0.40)
3. Extract inventor networks ($0.30)
4. Query GitHub for tech companies ($0.20)
5. Query Stack Overflow patterns ($0.10)

**Total additional cost:** ~$1.20 for comprehensive expansion

**You do NOT have BigQuery access to:**
- Academic publication databases
- Research funding databases
- Trade data (use APIs instead)
- Supply chain data (not publicly available)
