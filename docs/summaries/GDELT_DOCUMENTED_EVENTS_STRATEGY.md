# GDELT Documented Events Strategy
## Focus: Concrete Events, Not Sentiment

**Created:** 2025-11-02
**Purpose:** Track documented agreements, treaties, partnerships, and cooperation events
**Alignment:** Zero Fabrication Protocol - we document what happened, not how people feel about it

---

## Strategic Refocus

**OLD FOCUS (Deprecated):**
- ❌ Sentiment analysis (how media portrays events)
- ❌ Narrative detection (what stories are told)
- ❌ Tone divergence (Chinese vs Western media framing)

**NEW FOCUS (Primary Mission):**
- ✅ **Agreements signed** - bilateral treaties, MOUs, cooperation agreements
- ✅ **Partnerships formed** - joint ventures, academic collaborations, sister cities
- ✅ **Exchanges documented** - official visits, delegations, diplomatic missions
- ✅ **Projects announced** - infrastructure deals, technology transfers, research initiatives
- ✅ **Multilateral actions** - votes at UN, positions at WTO, EU forum participation
- ✅ **Policy decisions** - regulatory changes, sanctions, trade restrictions

**Why This Matters:**
These are **FACTS** that happened on specific dates with specific actors. They are verifiable, reproducible, and align with Zero Fabrication Protocol.

---

## GDELT CAMEO Event Codes for Documented Events

GDELT uses the Conflict and Mediation Event Observations (CAMEO) coding scheme. Here are the codes for **concrete events** (not sentiment):

### High-Priority Event Codes

| Code | Event Type | Examples | Intelligence Value |
|------|------------|----------|-------------------|
| **030** | Express intent to cooperate | "Germany and China agree to pursue quantum partnership" | Early warning of future agreements |
| **031** | Express intent to engage in material cooperation | "Italy signals willingness to join BRI" | Precursor to formal agreements |
| **036** | Express intent to meet or negotiate | "Macron to meet Xi in Beijing next month" | Tracks diplomatic engagement timeline |
| **040** | Consult | "EU-China summit in Brussels" | Formal diplomatic consultations |
| **043** | Engage in diplomatic cooperation | "Poland hosts China trade delegation" | Active cooperation events |
| **045** | Engage in material cooperation | "Germany-China joint research facility opens" | Physical cooperation manifestation |
| **046** | Receive material cooperation | "Greece receives Chinese port investment" | Technology/capital transfer events |
| **050** | Provide aid | "China provides COVID vaccines to Hungary" | Aid/dependency relationships |
| **051** | Cooperate economically | "France-China business forum" | Economic cooperation events |
| **061** | Cooperate on science/technology | "Joint AI research center announced" | **CRITICAL** - Technology transfer |
| **075** | Sign formal agreement | "MOU signed for 5G cooperation" | **HIGHEST VALUE** - Legal commitments |

### Multilateral Event Codes

| Code | Event Type | Examples | Intelligence Value |
|------|------------|----------|-------------------|
| **042** | Make a visit | "Xi visits German auto factory" | Official state/business visits |
| **111** | Praise or endorse | "China supports French climate position at COP" | Diplomatic alignment tracking |
| **120** | Reject | "Poland rejects Huawei 5G bid" | Policy conflicts |
| **130** | Threaten | "China threatens sanctions over Taiwan" | Coercive diplomacy |
| **140** | Protest | "EU protests Chinese human rights record" | Diplomatic tensions |

---

## Query Strategy: Documented Events

### Query 1: Formal Agreements Signed (Code 075)

**Most Important Query** - Captures legally binding agreements:

```sql
SELECT
    event_date,
    actor1_name,
    actor1_country_code,
    actor2_name,
    actor2_country_code,
    action_geo_country_code as location,
    source_url
FROM gdelt_events
WHERE event_code = '075'  -- Sign formal agreement
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT')
    OR actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT')
  )
  AND event_date >= '20200101'
ORDER BY event_date DESC;
```

**What This Captures:**
- Belt & Road Initiative MOUs
- Technology cooperation agreements
- Trade agreements
- Sister city partnerships
- Academic exchange agreements
- Investment treaties

**Intelligence Use:**
Cross-reference agreement dates with:
- TED contract awards (3-6 months after agreement)
- OpenAlex research collaborations (6-12 months after)
- USPTO patent citations (12-24 months after)

---

### Query 2: Science & Technology Cooperation (Code 061)

**Critical for Technology Transfer Tracking:**

```sql
SELECT
    event_date,
    actor1_name,
    actor2_name,
    action_geo_country_code as location,
    source_url
FROM gdelt_events
WHERE event_code = '061'  -- Cooperate on science/technology
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL')
    OR actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL')
  )
  AND event_date >= '20150101'
ORDER BY event_date DESC;
```

**What This Captures:**
- Joint AI research centers
- Quantum computing partnerships
- BCI research collaborations
- Semiconductor joint ventures
- Academic exchange programs

**Cross-Reference Opportunity:**
1. GDELT: "German-China quantum partnership announced" (2024-06-15)
2. OpenAlex: German-China quantum papers spike (2024-09 onwards)
3. USPTO: Chinese quantum patents citing German institutions (2025-01)
4. **Finding:** Technology transfer pathway documented via 3 sources

---

### Query 3: Material Cooperation Events (Code 045-046)

**Tracks Physical Infrastructure/Investment:**

```sql
SELECT
    event_date,
    actor1_name,
    actor2_name,
    CASE
        WHEN event_code = '045' THEN 'Engage in cooperation'
        WHEN event_code = '046' THEN 'Receive cooperation'
    END as cooperation_type,
    action_geo_country_code as location,
    source_url
FROM gdelt_events
WHERE event_code IN ('045', '046')
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('GRC','ITA','PRT','HUN','POL','SRB')  -- BRI targets
    OR actor2_country_code IN ('GRC','ITA','PRT','HUN','POL','SRB')
  )
  AND event_date >= '20130101'  -- BRI era
ORDER BY event_date DESC;
```

**What This Captures:**
- Port investments (Piraeus, Hamburg)
- Railroad construction
- 5G network deployments
- Power plant construction
- Data center installations

---

### Query 4: Official Visits (Code 042)

**Maps Diplomatic Engagement:**

```sql
SELECT
    event_date,
    actor1_name,
    actor1_country_code,
    action_geo_country_code as visit_location,
    source_url
FROM gdelt_events
WHERE event_code = '042'  -- Make a visit
  AND actor1_country_code = 'CHN'
  AND action_geo_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL')
  AND event_date >= '20150101'
ORDER BY event_date DESC;
```

**What This Captures:**
- Xi Jinping European tours
- Premier Li Qiang visits
- Minister-level delegations
- Business delegation trips
- Academic exchange visits

**Intelligence Pattern:**
Official visit → Agreement signed (within days) → Contract award (within months)

---

### Query 5: Economic Cooperation (Code 051)

**Tracks Trade & Investment Events:**

```sql
SELECT
    event_date,
    actor1_name,
    actor2_name,
    action_geo_country_code as location,
    source_url
FROM gdelt_events
WHERE event_code = '051'  -- Cooperate economically
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT')
    OR actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL','NLD','BEL','AUT','GRC','PRT')
  )
  AND event_date >= '20150101'
ORDER BY event_date DESC;
```

**What This Captures:**
- Business forums
- Trade fairs
- Investment summits
- Chamber of commerce events
- Export/import agreements

---

### Query 6: Multilateral Forum Activity

**Tracks UN, WTO, EU Forum Positions:**

```sql
SELECT
    event_date,
    actor1_name,
    actor2_name,
    event_code,
    CASE
        WHEN event_code = '111' THEN 'Praise/Endorse'
        WHEN event_code = '120' THEN 'Reject'
        WHEN event_code = '130' THEN 'Threaten'
        WHEN event_code = '140' THEN 'Protest'
    END as action_type,
    source_url
FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND event_code IN ('111', '120', '130', '140')
  AND (
    actor1_name LIKE '%UNITED NATIONS%'
    OR actor2_name LIKE '%UNITED NATIONS%'
    OR actor1_name LIKE '%WTO%'
    OR actor2_name LIKE '%EUROPEAN UNION%'
    OR source_url LIKE '%united-nations%'
    OR source_url LIKE '%wto.org%'
  )
  AND event_date >= '20200101'
ORDER BY event_date DESC;
```

**What This Captures:**
- China-EU clashes at WTO
- UN Security Council votes
- WHO pandemic response positions
- Climate agreement stances
- Human rights forum conflicts

---

## Priority Collection Targets

### Tier 1: Legal Agreements (Highest Value)

**Event Codes:** 075 (Sign formal agreement)
**Coverage:** 2013-2025 (BRI era to present)
**Expected Volume:** 500-1,000 agreements
**Intelligence Value:** CRITICAL - Legal commitments are hard evidence

**Example Findings:**
- Italy BRI MOU (March 2019)
- Hungary-China university partnerships
- Greek port concession agreements
- Polish 5G infrastructure contracts
- Czech nuclear power agreements

---

### Tier 2: Technology Cooperation (Critical for Mission)

**Event Codes:** 061 (Science/technology cooperation)
**Coverage:** 2015-2025
**Expected Volume:** 2,000-5,000 events
**Intelligence Value:** CRITICAL - Tracks technology transfer

**Example Findings:**
- German-China AI research centers
- French-China nuclear cooperation
- UK-China biotech partnerships
- Dutch-China semiconductor collaboration
- Swedish-China 5G research

---

### Tier 3: Infrastructure & Investment (BRI Tracking)

**Event Codes:** 045, 046 (Material cooperation)
**Coverage:** 2013-2025
**Expected Volume:** 3,000-8,000 events
**Intelligence Value:** HIGH - Physical presence mapping

**Example Findings:**
- Piraeus port expansion (Greece)
- Belgrade-Budapest railway (Hungary-Serbia)
- Portuguese energy investments
- Italian shipyard acquisitions
- Romanian nuclear projects

---

### Tier 4: Diplomatic Engagement (Context Layer)

**Event Codes:** 040 (Consult), 042 (Visit), 043 (Diplomatic cooperation)
**Coverage:** 2015-2025
**Expected Volume:** 10,000-20,000 events
**Intelligence Value:** MEDIUM - Provides timeline context

**Example Findings:**
- Belt & Road Forum attendance
- 16+1 summit meetings
- State visits to Europe
- Minister-level consultations
- Business delegation trips

---

## Cross-Reference Intelligence Framework

### Event Chain Analysis

**Example: Germany-China Quantum Technology Transfer**

**Stage 1: Intent Expression (Code 030)**
- 2023-11-15: "Scholz signals openness to quantum cooperation with China"
- Source: Reuters
- **Action:** Flag for monitoring

**Stage 2: Official Visit (Code 042)**
- 2024-04-10: "German science minister visits Chinese Academy of Sciences"
- Source: Der Spiegel
- **Action:** Cross-reference with OpenAlex German institutions

**Stage 3: Formal Agreement (Code 075)**
- 2024-06-15: "Germany-China quantum research MOU signed in Berlin"
- Source: Xinhua, DW
- **Action:** Record agreement date, monitor for implementation

**Stage 4: Technology Cooperation (Code 061)**
- 2024-09-01: "Joint quantum computing lab opens in Munich"
- Source: Nature News
- **Action:** Cross-reference with USPTO patent filings

**Stage 5: Research Output (OpenAlex)**
- 2024-10-2025-03: 47 new German-China quantum co-authored papers
- Source: OpenAlex database
- **Action:** Identify participating institutions

**Stage 6: Patent Activity (USPTO)**
- 2025-01-2025-06: 12 Chinese quantum patents cite German institutions
- Source: USPTO database
- **Action:** Assess technology transfer extent

**Stage 7: Commercial Application (TED)**
- 2025-08: Chinese quantum firm wins German government contract
- Source: TED procurement database
- **Action:** Generate intelligence report

**INTELLIGENCE PRODUCT:**
```
GERMANY-CHINA QUANTUM TECHNOLOGY TRANSFER PATHWAY (2023-2025)

EVIDENCE CHAIN (7 sources):
1. GDELT: Intent expressed (2023-11-15)
2. GDELT: Official visit (2024-04-10)
3. GDELT: MOU signed (2024-06-15)
4. GDELT: Lab opens (2024-09-01)
5. OpenAlex: 47 joint papers (2024-10 to 2025-03)
6. USPTO: 12 Chinese patents cite German work (2025-01 to 2025-06)
7. TED: Chinese firm wins contract (2025-08)

TIMELINE: 22 months from intent to commercial deployment
TECHNOLOGY FLOW: Germany → China (via academic collaboration)
COMMERCIAL IMPACT: Chinese firm competing in German market
CONFIDENCE: HIGH (7 independent sources corroborate pathway)
```

---

## Implementation Plan

### Phase 1: Historical Agreement Backfill (Week 1)

**Collect:**
- All Code 075 events (formal agreements) 2013-2025
- All Code 061 events (tech cooperation) 2015-2025

**Expected:**
- 1,500-2,000 total agreements
- 2,000-5,000 tech cooperation events

**Deliverable:**
- Database of all EU-China formal agreements
- Timeline visualization of cooperation peaks

---

### Phase 2: Material Cooperation (Week 2)

**Collect:**
- Code 045/046 events (infrastructure) 2013-2025
- Code 051 events (economic cooperation) 2015-2025

**Expected:**
- 5,000-10,000 infrastructure events
- 8,000-15,000 economic cooperation events

**Deliverable:**
- BRI investment timeline by country
- Infrastructure project database

---

### Phase 3: Cross-Reference Integration (Week 3)

**Match GDELT events with:**
- OpenAlex research collaborations
- TED contract awards
- USPTO patent citations
- CORDIS project grants

**Expected:**
- 500-1,000 multi-source validated pathways

**Deliverable:**
- Technology transfer intelligence reports
- Multi-source evidence chains

---

## Query Templates (Production Ready)

### Template 1: All Formal Agreements by Country

```sql
-- Customizable by country and date range
SELECT
    event_date,
    actor1_name,
    actor2_name,
    action_geo_country_code as signed_at,
    source_url
FROM gdelt_events
WHERE event_code = '075'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (actor1_country_code = ? OR actor2_country_code = ?)  -- Country parameter
  AND event_date BETWEEN ? AND ?  -- Date range parameters
ORDER BY event_date DESC;
```

### Template 2: Technology Cooperation Timeline

```sql
-- Track tech cooperation events over time
SELECT
    SUBSTR(event_date, 1, 6) as month,
    COUNT(*) as tech_cooperation_events,
    COUNT(DISTINCT actor1_country_code || actor2_country_code) as unique_partnerships
FROM gdelt_events
WHERE event_code = '061'
  AND (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR')
    OR actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR')
  )
  AND event_date >= '20150101'
GROUP BY month
ORDER BY month;
```

### Template 3: Event Clustering (Agreement → Implementation)

```sql
-- Find agreement clusters (multiple events within 30 days)
SELECT
    e1.event_date as agreement_date,
    e1.actor1_name,
    e1.actor2_name,
    e1.source_url as agreement_source,
    e2.event_date as implementation_date,
    e2.source_url as implementation_source,
    CAST((JULIANDAY(e2.event_date) - JULIANDAY(e1.event_date)) AS INTEGER) as days_between
FROM gdelt_events e1
JOIN gdelt_events e2
  ON (e1.actor1_country_code = e2.actor1_country_code
      AND e1.actor2_country_code = e2.actor2_country_code)
WHERE e1.event_code = '075'  -- Agreement
  AND e2.event_code IN ('045', '046', '061')  -- Implementation
  AND e2.event_date > e1.event_date
  AND JULIANDAY(e2.event_date) - JULIANDAY(e1.event_date) <= 365  -- Within 1 year
  AND (e1.actor1_country_code = 'CHN' OR e1.actor2_country_code = 'CHN')
ORDER BY e1.event_date DESC;
```

---

## Expected Intelligence Products

### 1. EU-China Formal Agreements Database (2013-2025)

**Contents:**
- All signed MOUs, treaties, cooperation agreements
- Sister city partnerships
- Academic exchange agreements
- Technology transfer agreements
- Investment treaties

**Format:** SQLite database with full provenance

---

### 2. Technology Transfer Pathway Reports

**Example Report Structure:**
```
TECHNOLOGY TRANSFER INTELLIGENCE REPORT
Country: Germany
Technology: Quantum Computing
Period: 2023-2025

PATHWAY EVIDENCE:
- GDELT: MOU signed 2024-06-15
- OpenAlex: 47 joint papers 2024-2025
- USPTO: 12 Chinese patents cite German work
- TED: Chinese firm wins contract 2025-08

ASSESSMENT: Confirmed technology transfer pathway
CONFIDENCE: HIGH (4 independent sources)
TIMELINE: 14 months intent to commercialization
```

---

### 3. BRI Infrastructure Timeline

**Contents:**
- All BRI infrastructure announcements
- Port, rail, energy, telecom projects
- Investment amounts (where reported)
- Geographic distribution

**Visualization:** Timeline + map of Chinese infrastructure in Europe

---

### 4. Multilateral Forum Position Tracker

**Contents:**
- China positions at UN, WTO, WHO
- EU-China alignment/conflict votes
- Third-party support patterns
- Diplomatic coalition formation

**Use:** Identify European countries voting with China

---

## Zero Fabrication Compliance

### What We CAN Document:

✅ **Event Date:** When agreement was signed (GDELT source_url verification)
✅ **Actors:** Who signed (actor1_name, actor2_name)
✅ **Event Type:** What kind of agreement (event_code)
✅ **Location:** Where it was signed (action_geo_country_code)
✅ **Source:** Which media reported it (source_url)
✅ **Frequency:** How many cooperation events per country
✅ **Timeline:** When events clustered (multiple agreements in short period)

### What We CANNOT Document:

❌ **Intent:** Why agreement was signed (requires policy documents)
❌ **Effectiveness:** Whether agreement was implemented (requires implementation reports)
❌ **Causation:** Whether visit caused agreement (correlation ≠ causation)
❌ **Coordination:** Whether agreements are coordinated strategy (requires internal documents)
❌ **Sentiment:** How parties feel about agreement (not our focus anymore)

### Proper Phrasing:

**CORRECT:**
- "Germany and China signed quantum cooperation MOU on 2024-06-15" (documented event)
- "47 German-China quantum papers published 2024-2025" (OpenAlex count)
- "12 Chinese patents cite German quantum research" (USPTO data)
- "Events correlate with diplomatic visit on 2024-04-10" (temporal correlation)

**INCORRECT:**
- "Germany transferred quantum technology to China" (assumes causation)
- "Visit led to technology cooperation" (infers intent)
- "Coordinated technology acquisition strategy" (requires internal documents)
- "Agreement was designed to circumvent export controls" (speculates motive)

---

## Next Steps

### Immediate (This Week):

1. ✅ Review this strategy document
2. ⏳ Run Query 1 (Formal Agreements) for 2020-2025
3. ⏳ Generate initial agreements database
4. ⏳ Cross-reference with Lithuania OpenAlex findings

### Week 1:

5. Collect all Code 075 events (agreements) 2013-2025
6. Collect all Code 061 events (tech cooperation) 2015-2025
7. Build EU-China agreements database

### Week 2-3:

8. Add Code 045/046 (infrastructure) events
9. Add Code 051 (economic) events
10. Generate cross-reference intelligence reports

---

## Summary

**NEW PRIMARY MISSION:**
Use GDELT to document **CONCRETE EVENTS** that provide timeline evidence for technology transfer pathways detected in OpenAlex, USPTO, and TED data.

**KEY VALUE:**
- GDELT shows WHEN agreements were signed
- OpenAlex shows WHAT research followed
- USPTO shows WHAT patents resulted
- TED shows WHAT contracts were awarded

**GDELT is your TIMELINE LAYER** - it documents the diplomatic/business events that precede the academic/patent/commercial activities you track in other databases.

**This approach is 100% Zero Fabrication compliant** - we document events that happened on specific dates with named actors and verifiable sources. No sentiment inference, no narrative detection, just facts.

---

**Document Status:** Production Ready
**Next Action:** Run Query 1 to collect all formal agreements 2020-2025
**Estimated Results:** 300-500 agreements ready for cross-reference analysis
