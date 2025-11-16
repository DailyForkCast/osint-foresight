# National Company Registries - Collection Strategy
**Date:** September 30, 2025
**Status:** Planning → Implementation
**Priority:** HIGH

---

## 🎯 Strategic Objective

Collect comprehensive company registry data from 17 high-priority countries (81 total) to identify China-connected entities across Europe and strategic partners.

---

## 📊 Priority Tier 1: IMMEDIATE (UK, Germany, France, Italy)

### 1. **United Kingdom - Companies House** ✅ READY TO IMPLEMENT

**Data Source:** https://download.companieshouse.gov.uk/

**Access Method:** FREE bulk downloads (no API key required)

**Available Data:**
- **Basic Company Data** - Free downloadable CSV snapshots
  - Updated monthly (within 5 working days of month end)
  - September 2025 snapshot available now
  - Split into multiple ZIP files for ease of download
  - Format: CSV

- **PSC Data** (People with Significant Control)
  - September 2025 snapshot available
  - Available as one large file or smaller multiple files
  - Critical for identifying beneficial ownership

- **Accounts Data** - XBRL format
  - Daily or monthly files available
  - Last 12 months of accounts data

**Real-time API:** Companies House Public Data API
- Streaming API for real-time changes
- REST API for live company lookups

**Implementation:** ✅ **START IMMEDIATELY**
- Download September 2025 basic company data snapshot
- Download PSC data for ownership intelligence
- Process with v3 validator (English language)
- Focus: China-connected UK entities

**Estimated Data Size:** ~10-20GB (all companies)
**Expected Output:** 1,000-10,000 China-connected UK entities

**Priority:** **CRITICAL - UK strategic importance**

---

### 2. **Germany - Handelsregister** ⚠️ REQUIRES PAID API

**Official Source:** https://www.unternehmensregister.de/
- **NO official API access** (German government doesn't provide direct API)

**Third-Party API Options:**

**Option A: handelsregister.ai** ⭐ RECOMMENDED
- URL: https://handelsregister.ai/en
- Access: REST API
- Update frequency: Daily
- Coverage: Entire German Commercial Register
- Data: Shareholders, executives, addresses, court details, documents
- Types: HRA, HRB, GnR, PR, VR, GsR
- **Cost:** Unknown (contact for pricing)

**Option B: Apify Handelsregister API**
- URL: https://apify.com/radeance/handelsregister-api
- Pricing: Pay-per-event (no monthly fees)
- Real-time access to Handelsregister.de
- Data: Shareholders, executives, addresses, court details, documents

**Option C: OpenRegisters**
- URL: https://www.openregisters.com/handelsregister-api
- Structured, reliable, fast API access
- Real-time data

**Implementation Strategy:**
1. **Phase 1:** Contact handelsregister.ai for pricing (free trial if available)
2. **Phase 2:** If cost-prohibitive, use web scraping (legal, public data)
3. **Phase 3:** Focus on specific companies from OpenAlex/Patents data (targeted approach)

**Estimated Records:** 3-5 million companies
**Expected Output:** 500-2,000 China-connected German entities

**Priority:** HIGH (Germany = largest EU economy, strategic tech sector)

---

### 3. **France - INPI (Institut National de la Propriété Industrielle)** ✅ FREE API

**Data Source:** https://data.inpi.fr/

**Access Method:** FREE API access (account required)

**Available Data:**
- **RNE (National Business Register)** - Replaces RNCS, RM, RAA
  - Legal identity data for all French companies
  - Update frequency: **Daily**

- **Additional Data:**
  - Trademarks: Weekly updates
  - Patents: Weekly updates
  - Designs: Bi-weekly updates

**API Types:**
- RNE (Business Registry) API
- Trademarks API
- Patents API
- Designs API

**Access Process:**
1. Create account on https://data.inpi.fr/
2. Login → Personal space → "My API / SFTP access"
3. Request access to desired content
4. Free access granted

**Data Coverage:**
- Legal information
- Technical information
- Commercial information
- Financial information

**Implementation:** ✅ **START AFTER UK**
- Register for INPI Data account
- Request API access (RNE + Patents)
- Integrate with v3 validator (French language supported)
- Cross-reference with TED procurement data

**Estimated Records:** 4-5 million companies
**Expected Output:** 800-3,000 China-connected French entities

**Priority:** HIGH (France = major EU economy, strategic industries)

---

### 4. **Italy - Camera di Commercio** ⚠️ FRAGMENTED

**Official Source:** Multiple regional Chambers of Commerce
- **NO centralized national API**

**Access Options:**

**Option A: Infocamere (official IT services provider)**
- URL: https://www.infocamere.it/
- Centralized database for all Italian Chambers of Commerce
- **Requires:** Business subscription (likely paid)

**Option B: OpenCorporates**
- URL: https://opencorporates.com/
- Aggregates Italian company data
- API access available (free tier + paid)

**Option C: Targeted web scraping**
- Focus on companies from OpenAlex/Patents data
- Verify specific entities rather than bulk collection

**Implementation Strategy:**
1. **Phase 1:** Use OpenCorporates free tier for initial testing
2. **Phase 2:** Identify high-value entities from existing data (OpenAlex, Patents)
3. **Phase 3:** Targeted data collection (not bulk)

**Estimated Records:** 6+ million companies
**Expected Output:** 300-1,000 China-connected Italian entities

**Priority:** MEDIUM-HIGH (Italy important but data access challenging)

---

## 📊 Priority Tier 2: SHORT-TERM (Poland, Czech Republic, Netherlands, Spain)

### 5. **Poland - Krajowy Rejestr Sądowy (KRS)**

**Official Source:** https://ekrs.ms.gov.pl/
- Central Register and Information on Business (CEIDG)
- National Court Register (KRS)

**Access:** Web interface, possible API (investigation needed)
**Language:** Polish (v3 validator supports Polish)
**Implementation:** After Tier 1 complete

---

### 6. **Czech Republic - Obchodní rejstřík**

**Official Source:** https://or.justice.cz/
- Commercial Register (Obchodní rejstřík)

**Access:** Public web interface
**Language:** Czech (v3 validator supports Czech)
**Implementation:** After Tier 1 complete

---

### 7. **Netherlands - Kamer van Koophandel (KvK)**

**Official Source:** https://www.kvk.nl/
- Chamber of Commerce (Kamer van Koophandel)

**Access:** API available (KvK API)
**Language:** Dutch (v3 validator supports Dutch)
**Implementation:** After Tier 1 complete

---

### 8. **Spain - Registro Mercantil**

**Official Source:** https://www.rmc.es/
- Commercial Registry

**Access:** Regional registries, possible central access
**Language:** Spanish (v3 validator supports Spanish)
**Implementation:** After Tier 1 complete

---

## 📊 Priority Tier 3: MEDIUM-TERM (Nordics, Baltics, Balkans)

### 9-17. **Additional Countries**

**Nordic:**
- Sweden: Bolagsverket
- Denmark: Erhvervsstyrelsen
- Finland: Kaupparekisteri
- Norway: Brønnøysundregistrene

**Baltics:**
- Estonia: Äriregister (E-Business Register)
- Latvia: Uzņēmumu reģistrs
- Lithuania: Juridinių asmenų registras

**Balkans:**
- Croatia: Sudski registar
- Slovenia: AJPES

---

## 🎯 Implementation Roadmap

### **Week 1 (October 1-7, 2025):**
1. ✅ **UK Companies House** - Download & Process
   - Basic Company Data (September 2025 snapshot)
   - PSC Data (beneficial ownership)
   - Process with v3 validator
   - Expected output: 1,000-10,000 entities

### **Week 2 (October 8-14, 2025):**
2. ✅ **France INPI** - Register & Collect
   - Create INPI Data account
   - Request API access (RNE + Patents)
   - Begin systematic collection
   - Expected output: 800-3,000 entities

### **Week 3 (October 15-21, 2025):**
3. ⚠️ **Germany Handelsregister** - Evaluate & Decide
   - Contact handelsregister.ai for pricing
   - Evaluate cost vs. targeted approach
   - Begin collection (API or targeted scraping)
   - Expected output: 500-2,000 entities

### **Week 4 (October 22-31, 2025):**
4. ⚠️ **Italy Camera di Commercio** - Targeted Collection
   - Test OpenCorporates free tier
   - Identify high-value targets from existing data
   - Targeted collection of priority entities
   - Expected output: 300-1,000 entities

### **November 2025:**
- Tier 2 countries (Poland, Czech Republic, Netherlands, Spain)
- Expected output: 1,000-4,000 additional entities

### **December 2025:**
- Tier 3 countries (Nordics, Baltics, Balkans)
- Expected output: 500-2,000 additional entities

---

## 💰 Budget Considerations

### **FREE Sources:**
- ✅ UK Companies House (full bulk download)
- ✅ France INPI (API access)
- ⚠️ Italy OpenCorporates (free tier, limited)

### **PAID Sources (TBD):**
- ⚠️ Germany Handelsregister APIs (pricing unknown)
- ⚠️ Italy Infocamere (likely paid)
- ⚠️ OpenCorporates Pro (if needed for Italy/others)

### **Zero-Budget Alternatives:**
- Web scraping (legal, public data)
- Targeted collection (high-value entities only)
- OpenCorporates free tier + targeted manual lookup

---

## 🔧 Technical Integration

### **Processing Pipeline:**
1. **Data Collection** → Download/API retrieval
2. **Validation** → v3 validator (40 languages)
3. **Entity Extraction** → China connection detection
4. **Cross-Reference** → Match with OpenAlex, Patents, TED, USAspending
5. **Intelligence Analysis** → Risk scoring, network mapping
6. **Storage** → SQLite/JSON with full provenance

### **Tools & Scripts:**
- `scripts/collect_companies_house.py` (create)
- `scripts/collect_inpi_france.py` (create)
- `scripts/collect_handelsregister.py` (create)
- Existing: `src/core/enhanced_validation_v3_complete.py` (40 languages)

---

## 📈 Expected Total Output

**Tier 1 (UK, Germany, France, Italy):**
- Companies screened: 20-30 million
- China-connected entities: 2,600-13,000

**Tier 2 (Poland, CZ, NL, Spain):**
- Companies screened: 8-12 million
- China-connected entities: 1,000-4,000

**Tier 3 (Nordics, Baltics, Balkans):**
- Companies screened: 4-6 million
- China-connected entities: 500-2,000

**TOTAL (17 countries):**
- Companies screened: 32-48 million
- China-connected entities: 4,100-19,000

---

## ✅ Success Metrics

1. **Coverage:** 17+ countries within 2 months
2. **Data Quality:** v3 validation (40 languages)
3. **Cross-Reference:** Match rate >20% with existing datasets
4. **Provenance:** 100% traceable to source
5. **Intelligence Value:** Identify hidden ownership structures, supply chain risks

---

**Next Action:** Begin UK Companies House collection immediately (free, comprehensive, strategic value)
