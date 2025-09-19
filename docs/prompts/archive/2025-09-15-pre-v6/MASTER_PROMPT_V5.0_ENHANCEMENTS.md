# Master Prompt v5.0 - Procurement, Standards & Evidence Enhancements
## Widely Applicable Upgrades from Italy Deep Dive

**Version:** 5.0 ENHANCED
**Date:** 2025-09-15
**Purpose:** Add procurement tracking, standards participation, evidence integrity
**Scope:** Applicable to all 44 target countries

---

## 🎯 WHAT WE ALREADY HAVE (v4.4)

✅ **Strong Foundation:**
- Conference intelligence (2020-2030)
- Arctic override rules
- Validation frameworks (bombshell, alternatives)
- Failsafe protocols with gap markers
- Department-level granularity attempts
- Evidence requirements with citations

⚠️ **What We're Missing:**
- CAGE/NCAGE codes for US/NATO supplier tracking
- Funding transparency (EU FTS, ownership chains)
- Standards body participation details
- Cloud/compute infrastructure exposure
- Evidence integrity (archiving, hashing)
- Negative evidence tracking

---

## 📦 PROCUREMENT & SUPPLY CHAIN ENHANCEMENTS (Phase 4)

### New Universal Sources (All Countries)
```yaml
us_nato_procurement:
  - SAM.gov: "Award notices, subcontracts"
  - USAspending.gov: "Prime & subaward explorer"
  - Defense.gov: "Contract announcements"
  - CAGE/NCAGE: "Commercial and Government Entity codes"
  - NSPA: "NATO Support & Procurement Agency"
  - NCI Agency: "NATO Communications & Information"
  - FAA/EASA TCDS: "Type Certificate Data Sheets"

eu_procurement:
  - TED: "Tenders Electronic Daily (existing)"
  - EU FTS: "Financial Transparency System"
  - ESA-STAR: "Space procurement (successor to EMITS)"

national_systems:  # Country-specific but pattern applicable
  italy: "CONSIP/MEPA, ANAC, regional platforms"
  germany: "VEMAP, Vergabe24"
  france: "PLACE, BOAMP"
  uk: "Contracts Finder, Find a Tender"
  # Add per country
```

### Enhanced Phase 4 Artifacts
```json
// phase04_sub8_us_country_supply_overlap.json
{
  "supplier_name": "Example Corp",
  "cage_code": "1ABC2",          // NEW: US identifier
  "ncage_code": "F1234",         // NEW: NATO identifier
  "award_notice_url": "https://sam.gov/...",
  "award_id": "W58RGZ-24-C-0001",
  "nato_entity": true,            // NEW: NATO supplier flag
  "plant_address": "Via Example 123, Milano",
  "us_programs": ["F-35", "MH-139"],
  "overlap_assessment": "CRITICAL"
}
```

### CAGE/NCAGE Resolution Pipeline
```python
def resolve_cage_ncage(supplier_name, country):
    """
    Critical for tracking US/NATO supply chain overlaps
    """
    sources = [
        "https://cage.dla.mil",
        "NATO NCAGE lookup",
        "SAM.gov entity search"
    ]

    return {
        "cage": search_cage(supplier_name),
        "ncage": search_ncage(supplier_name, country),
        "programs": link_to_contracts(cage_code),
        "risk": assess_dual_use(programs)
    }
```

---

## 💰 FUNDING & OWNERSHIP TRANSPARENCY (Phase 6)

### Enhanced Ownership Tracking
```yaml
ownership_sources:
  global:
    - GLEIF/LEI: "Legal Entity Identifier relationships"
    - EDGAR: "SEC filings for US parents"
    - OpenCorporates: "Global company registry"

  eu_specific:
    - EU FTS: "Financial Transparency System"
    - Horizon Dashboard: "Research funding"

  national:  # Examples
    - OpenCUP: "Italy project codes"
    - Companies House: "UK ownership"
    - Handelsregister: "German registry"
```

### Enhanced Phase 6 Artifacts
```json
// phase06_sub8_us_equity_links.json
{
  "entity": "Leonardo DRS",
  "lei": "549300EHVF3I5WDCWC03",
  "lei_parent_chain": [          // NEW: Full ownership chain
    {"lei": "parent_lei", "name": "Leonardo SpA", "percent": 100}
  ],
  "ownership_basis": "10-K filing",  // NEW: Evidence type
  "cup_code": "E12F34000000",       // NEW: National project code
  "fts_award_id": "FTS-2024-001",   // NEW: EU funding
  "us_subsidiaries": ["DRS list"],
  "china_exposure": "Via Italian parent"
}
```

---

## 🏛️ INSTITUTIONS & STANDARDS (Phases 3, 5, 7)

### Department Resolution Enhancement
```yaml
department_sources:
  academic:
    - OpenAlex: "author.affiliation.department"
    - ORCID: "Employment records"
    - Crossref: "Affiliation strings"
    - Conference programs: "Committee listings"

  evaluation:  # National systems
    - ANVUR: "Italy VQR/ASN"
    - REF: "UK Research Excellence"
    - ANECA: "Spain evaluation"
    - CNRS: "France sections"
```

### Standards Participation Tracking
```yaml
standards_sources:
  international:
    - ISO/IEC: "Ballot participation"
    - ETSI: "Working group membership"
    - 3GPP: "Meeting attendance"
    - IEEE: "Standards committees"
    - ECSS: "Space standards adoption"

  nato:
    - STANAGs: "Standardization agreements"
    - NATO STO: "Science & Technology Org"
    - CMRE: "Centre for Maritime Research"
```

### Enhanced Phase 7 Artifacts
```json
// phase07_sub7_us_country_standards_roles.json
{
  "standard": "ISO/IEC 27001",
  "working_group": "JTC 1/SC 27",
  "country_role": "P-member",
  "ballot_id": "ISO/IEC DIS 27001.2",  // NEW
  "vote_position": "Approve",           // NEW
  "agenda_url": "https://...",          // NEW
  "committee_members": [
    {"name": "Dr. X", "affiliation": "CNR", "role": "convenor"}
  ],
  "us_alignment": "Compatible",
  "china_position": "Also P-member"
}
```

---

## 🔒 RISK & SECURITY TRACKING (Phase 8-9)

### Enhanced Security Sources
```yaml
security_sources:
  vulnerability_tracking:
    - CVE/NVD: "Vendor-specific vulnerabilities"
    - CISA: "ICS advisories"
    - National CERTs: "Country-specific advisories"

  export_controls:
    - EU Dual-Use: "Regulation 2021/821"
    - Wassenaar: "Arrangement lists"
    - National: "Golden Power, CFIUS, etc."

  audits:
    - National audit offices
    - Parliamentary hearings
    - Court of Auditors reports
```

### Negative Evidence Tracking (NEW)
```json
// phase09_sub12_negative_evidence.json
{
  "claim": "China seeks quantum technology via X",
  "searched_sources": [
    "MIIT announcements",
    "Provincial S&T bulletins",
    "Company reports"
  ],
  "result": "contradiction",  // none|contradiction|partial
  "notes": "Policy states domestic development only",
  "urls": ["archive_links"],
  "confidence_impact": "Downgrade to Medium"
}
```

---

## ☁️ COMPUTE & INFRASTRUCTURE EXPOSURE (Phase 11)

### Cloud & Network Tracking
```yaml
infrastructure_sources:
  compute:
    - EuroHPC: "Supercomputing allocations"
    - PRACE: "Legacy acknowledgments"
    - Cloud providers: "AWS/Azure/GCP regions"

  network:
    - PeeringDB: "AS relationships"
    - RIPEstat: "ASN ownership"
    - Hurricane Electric: "BGP toolkit"

  software:
    - GitHub: "SBOM in releases"
    - Package managers: "Dependency trees"
```

### Enhanced Phase 11 Artifacts
```json
// phase11_sub5_compute_data_exposure.json
{
  "institution": "Research Center X",
  "compute_resources": [
    {
      "type": "HPC",
      "system": "Leonardo @ CINECA",
      "allocation": "10M core-hours",
      "acknowledged_in": ["paper_dois"]
    }
  ],
  "network": {
    "asn": "AS137",                    // NEW
    "provider": "GARR",
    "peering": ["AS174", "AS3356"]
  },
  "cloud_usage": {
    "provider": "AWS",
    "regions": ["eu-south-1"],         // NEW
    "data_residency_note": "GDPR compliant",  // NEW
    "services": ["EC2", "S3"]
  },
  "software_dependencies": {
    "sbom_url": "github.com/.../sbom.json",   // NEW
    "critical_packages": ["tensorflow", "pytorch"]
  }
}
```

---

## 📁 EVIDENCE INTEGRITY PROTOCOL

### Archiving & Verification
```python
def ensure_evidence_integrity(url, content):
    """
    Archive and hash all critical evidence
    """

    # Step 1: Archive
    archive_url = archive_to_wayback(url)
    if not archive_url:
        archive_url = archive_to_perma_cc(url)

    # Step 2: Hash
    content_hash = hashlib.sha256(content.encode()).hexdigest()

    # Step 3: Store
    evidence_record = {
        "original_url": url,
        "archive_url": archive_url,          // NEW
        "content_sha256": content_hash,      // NEW
        "archived_date": datetime.now(),
        "verification_status": "preserved"
    }

    return evidence_record
```

### Enhanced Evidence Master
```csv
ClaimID,Claim,SourceURL,ArchiveURL,ContentSHA256,PubDate,Lang,Corroboration,Probability,Confidence
001,"Leonardo supplies X","https://...","https://web.archive.org/...","a3f2b1...",2024-01-15,EN,Multi,[60,90),High
```

---

## 📊 NEW ARTIFACTS TO ADD

### Cross-Phase Artifacts
```yaml
new_artifacts:
  procurement:
    - cage_ncage_registry.json
    - nato_suppliers.csv
    - award_overlaps.json

  funding:
    - ownership_chains.json
    - fts_grants.csv
    - national_project_codes.json

  standards:
    - ballot_participation.json
    - committee_memberships.csv
    - standards_influence_map.json

  evidence:
    - evidence_archive_log.json
    - negative_evidence.json
    - hash_verification.csv

  infrastructure:
    - compute_allocations.json
    - network_topology.json
    - cloud_exposure.csv
```

---

## 🎯 TOP 5 UNIVERSAL QUICK WINS

1. **CAGE/NCAGE Crosswalk**
   - Map all suppliers to US/NATO programs
   - Persistent identifiers across datasets
   - Critical for dual-use assessment

2. **EU FTS + National Codes**
   - Link EU funding to national projects
   - Expose actual recipients of dual-use funding
   - Track money flows to capabilities

3. **Standards Ballot Tracking**
   - Identify influence in technical standards
   - Map China-US-Target country positions
   - Early warning on technology directions

4. **Evidence Archiving**
   - Wayback/Perma.cc all critical URLs
   - SHA-256 hash for integrity
   - Protection against link rot

5. **Negative Evidence Collection**
   - Document what's NOT found
   - Track contradictions
   - Strengthen confidence calibration

---

## 🔧 IMPLEMENTATION PATCHES

### For ChatGPT Master Prompt
```yaml
Add to Phase 4:
  procurement_enhancement:
    - Include CAGE/NCAGE codes
    - Track NATO suppliers
    - Map award overlaps

Add to Phase 6:
  ownership_tracking:
    - LEI parent chains
    - FTS grant IDs
    - Ownership evidence basis

Add to Phase 9:
  negative_evidence:
    - Track contradictions
    - Document search failures
    - Adjust confidence accordingly
```

### For Claude Code Implementation
```python
# Add to phase functions

def enhance_procurement_tracking(supplier):
    supplier.cage = resolve_cage(supplier.name)
    supplier.ncage = resolve_ncage(supplier.name)
    supplier.nato_programs = link_nato_contracts(supplier.ncage)
    return supplier

def track_negative_evidence(claim):
    sources_checked = comprehensive_search(claim)
    if not found or contradicts:
        log_negative_evidence(claim, sources_checked)
        downgrade_confidence(claim)
    return claim

def ensure_evidence_integrity(url):
    archive = wayback_save(url)
    hash = sha256_content(url)
    store_verification(url, archive, hash)
    return archive
```

---

## ✅ VALIDATION CHECKLIST

### New Requirements:
- [ ] All critical suppliers have CAGE/NCAGE lookup attempted
- [ ] Ownership chains traced via LEI
- [ ] Standards participation documented with ballot IDs
- [ ] Critical evidence archived with hashes
- [ ] Negative evidence tracked systematically
- [ ] Cloud/compute exposure assessed
- [ ] National procurement systems checked

---

## 🎯 BOTTOM LINE

These enhancements add:
1. **Better supply chain tracking** via CAGE/NCAGE
2. **Funding transparency** via FTS and ownership chains
3. **Standards influence** via ballot tracking
4. **Evidence integrity** via archiving and hashing
5. **Confidence calibration** via negative evidence

**All improvements use free/open sources and are applicable across all 44 countries.**

---

*Version 5.0 - Procurement, Standards & Evidence Enhancements*
