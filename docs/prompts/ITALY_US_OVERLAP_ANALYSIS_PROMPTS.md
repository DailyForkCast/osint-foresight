# Italy-US Overlap Analysis Prompts with Micro-Artifacts
## Enhanced Phase-Specific Requirements

**Version**: 1.0 (Incorporating Addendum v3.9)
**Date**: 2025-09-14
**Focus**: US-Italy technological and industrial overlaps with department-level granularity

---

## PHASE 04: SUPPLY CHAIN ANALYSIS

### Enhanced Requirements (with US-Italy Overlaps)

#### 4.5.1 US-Italy Supply Chain Overlap Mapping

Create **`phase04_sub8_us_italy_supply_overlap.json`** containing:

```json
[{
  "us_prime_or_tier": "prime|tier1|tier2",
  "program": "e.g., F-35|NGJ|Copernicus|EO/ISR",
  "italy_entity_ror": "https://ror.org/...",
  "italy_site": "plant/campus/lab name (if known)",
  "component": "e.g., blisk, EO sensor, HPC module",
  "export_flag": "ITAR|EAR|EU-dual|none",
  "single_source_risk": true,
  "evidence_urls": ["https://…", "https://…"],
  "last_checked": "2025-09-14"
}]
```

**Critical Programs to Analyze**:
- F-35 (Cameri FACO, Leonardo components)
- NGJ (Next Generation Jammer)
- GCAP/Tempest
- Copernicus/EO satellites
- NATO AWACs upgrades
- Cyber defense systems

**Key Italian Sites**:
- Leonardo: Cameri, Foggia, La Spezia, Turin
- Fincantieri: Trieste, Muggiano, Castellammare
- Thales Alenia Space: Rome, Turin, L'Aquila
- MBDA Italia: La Spezia
- Avio: Colleferro

**Instructions**:
1. Link Italian sites/components to US primes/programs
2. Tag export_flag (ITAR/EAR/EU-dual/none)
3. Mark single_source_risk where applicable
4. Attach exact document URLs
5. If department/site unknown, use org-level with `site=null`

---

## PHASE 06: FUNDING & CONTROL ANALYSIS

### Enhanced Requirements (with US Equity Links)

#### 6.7.1 US Equity and Control Mapping

Create **`phase06_sub8_us_equity_links.json`** containing:

```json
[{
  "italy_entity_lei": "…",
  "italy_entity_ror": "…",
  "ultimate_parent_country": "US",
  "ownership_pct": 0.23,
  "control_rights": ["board","veto","information"],
  "funding_round_or_deal": "Series B|Acquisition|Grant",
  "program": "(if grant/contract)",
  "year": 2024,
  "evidence_urls": ["https://…"],
  "last_checked": "2025-09-14"
}]
```

**Key Areas to Investigate**:
- US private equity in Italian defense/tech
- DARPA/DoD grants to Italian entities
- US VC investments in Italian startups
- Joint ventures with US control rights
- Golden Power reviews involving US entities

**Data Sources**:
- LEI/GLEIF database
- Italian Companies Register (Registro Imprese)
- SEC filings for US parents
- Golden Power notifications
- EU Transparency Register

---

## PHASE 07: LINKS & STANDARDS ANALYSIS

### Enhanced Requirements (with Department-Level Collaboration)

#### 7.1 Department-Level Collaboration Mapping

**Step 1**: Build org↔org edges from OpenAIRE/Crossref/CORDIS

**Step 2**: Enrich to dept↔dept where supported by ≥2 sources:
- Author affiliation department
- ORCID employment record
- Department webpage listing

Create **`phase07_sub8_dept_collab_pairs.json`**:

```json
[{
  "country_a": "IT",
  "org_a_ror": "…",
  "dept_a_id": "sapienza:phys:nuclear | null",
  "country_b": "US",
  "org_b_ror": "…",
  "dept_b_id": "mit:nse | null",
  "domain": "Quantum Sensing",
  "outputs": {"pubs":3,"reports":1,"projects":1,"yrs":[2022,2024]},
  "evidence": [{"type":"paper","doi":"…","url":"…","year":2023}],
  "last_checked": "2025-09-14"
}]
```

**Rule**: If department cannot be resolved, record org↔org first with `dept_*=null`. Do NOT drop the edge.

#### 7.2 Standards Body Participation

Create **`phase07_sub7_us_italy_standards_roles.json`**:

```json
[{
  "body": "ETSI|3GPP|ISO|IEC|NATO-STANAG",
  "wg": "…",
  "role": "member|rapporteur|editor",
  "role_weight": 1,
  "org_it_ror": "…",
  "org_us_ror": "…",
  "dept_id_it": "optional",
  "dept_id_us": "optional",
  "person_orcid": "optional",
  "evidence_url": "https://…",
  "year": 2024
}]
```

**Key Standards Bodies**:
- NATO STANAGs
- ETSI (telecommunications)
- 3GPP (5G/6G)
- ISO/IEC (cybersecurity, AI)
- ECSS (space standards)

---

## DEPARTMENT REGISTRY

Create **`dept_registry.json`** for canonical department names:

```json
[{
  "org_ror": "https://ror.org/...",
  "dept_name": "Department of Nuclear Physics",
  "aka": ["Dip. Fisica Nucleare"],
  "dept_id": "sapienza:phys:nuclear",
  "dept_url": "https://…"
}]
```

---

## CITATION REQUIREMENTS

Place bracketed endnote numbers **immediately after the sentence** they support[1]. Maintain an **Endnotes** section with:
- Exact document URLs (not homepages)
- Accessed dates in YYYY-MM-DD format
- Full document titles

Example:
Italy's participation in the F-35 program includes final assembly at Cameri[1].

[1] Lockheed Martin. (2024). F-35 Global Partnership: Italy. Retrieved 2025-09-14, from https://www.lockheedmartin.com/content/dam/lockheed-martin/aero/documents/F-35/FG19-24749_F35FastFacts10_2024.pdf

---

## DATA COLLECTION PRIORITIES

### High Priority (Immediate)
1. F-35 supply chain mapping (Cameri FACO)
2. Leonardo US contracts and partnerships
3. US equity in Italian defense companies
4. MIT-Politecnico collaborations

### Medium Priority (Near-term)
1. Standards body participation mapping
2. Department-level research collaborations
3. Joint venture control structures
4. Golden Power cases with US entities

### Low Priority (Future Enhancement)
1. Individual researcher networks (ORCID)
2. Patent co-inventorship patterns
3. Conference committee overlaps

---

## QUALITY ASSURANCE

- ✅ Every edge must have evidence URLs
- ✅ Use org-level if dept unknown (don't drop)
- ✅ Tag export controls accurately
- ✅ Include accessed dates for all sources
- ✅ Validate ROR/LEI/ORCID identifiers

---

*Updated with Addendum v3.9 requirements for micro-artifacts and department-level analysis*
