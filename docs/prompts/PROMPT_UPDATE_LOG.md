# Prompt Update Log

## Version 3.8 / 1.8 Updates (2025-09-14)

### Major Enhancements

#### 1. Department-Level Granularity
- Added `dept_registry.json` for canonical department naming
- New `phase07_sub8_dept_collab_pairs.json` for department-to-department collaborations
- Algorithm for resolving departments from multiple sources (ORCID, affiliations, web scraping)
- Fallback to org-level if department cannot be resolved (never drop edges)

#### 2. US-Country Overlap Analysis
- **Supply Chain**: `phase04_sub8_us_country_supply_overlap.json`
  - Maps country entities in US defense programs (F-35, GCAP, NGJ, etc.)
  - Tracks export controls (ITAR/EAR/dual-use)
  - Identifies single-source risks

- **Equity & Control**: `phase06_sub8_us_equity_links.json`
  - US ownership percentages
  - Control rights (board, veto, information)
  - Investment rounds and acquisition tracking

- **Standards Participation**: `phase07_sub7_us_country_standards_roles.json`
  - Joint participation in standards bodies
  - Role weighting (member, rapporteur, editor)
  - Working group level tracking

#### 3. Enhanced NATO Integration
- Expanded STANAG compliance tracking
- NDPP alignment assessment
- Minilateral format tracking (JEF, V4, NORDEFCO, B9)
- Framework nation responsibilities

#### 4. Critical Phase Emphasis
- Added validation checks for often-missed phases:
  - Phase 9 (PRC/MCF Posture)
  - Phase 10 (Red Team)
  - Phase 12 (Extended Analysis)
- Automated validation function to ensure completeness

#### 5. Evidence & Citation Standards
- Strict requirement for exact document URLs (no homepages)
- Mandatory accessed_date in YYYY-MM-DD format
- Archive links for critical/paywalled sources
- Multi-source validation for all claims

### Key Data Structures

#### Department Registry
```json
{
  "org_ror": "https://ror.org/...",
  "dept_name": "Department Name",
  "aka": ["Alternative names"],
  "dept_id": "org:dept:subdept",
  "dept_url": "https://..."
}
```

#### Supply Chain Overlap
```json
{
  "us_prime_or_tier": "prime|tier1|tier2",
  "program": "F-35|GCAP|etc",
  "country_entity_ror": "...",
  "component": "specific part",
  "export_flag": "ITAR|EAR|dual-use|none",
  "single_source_risk": true/false
}
```

#### Department Collaboration
```json
{
  "org_a_ror": "...",
  "dept_a_id": "org:dept | null",
  "org_b_ror": "...",
  "dept_b_id": "org:dept | null",
  "outputs": {"pubs": N, "projects": M},
  "evidence": [...]
}
```

### Migration Notes

1. **For ChatGPT Users**: Update from v3.7 to v3.8
   - New sub-phase artifacts required
   - Department registry mandatory
   - Enhanced validation checklist

2. **For Claude Code Users**: Update from v1.7 to v1.8
   - New data collection functions
   - Department resolution algorithm
   - Multi-source validation requirements

### Country-Neutral Implementation

All new features are designed to work with any target country:
- Replace "Italy" with `{{COUNTRY}}` in prompts
- Use ISO country codes consistently
- Maintain bilateral analysis capability (Country-US, Country-China, etc.)
- Support for non-NATO countries with appropriate toggles

### Validation Checklist

Before declaring analysis complete:
- [ ] All 14 phases (0-13) present
- [ ] Department registry created
- [ ] US overlap artifacts (if toggle enabled)
- [ ] NATO artifacts (if toggle enabled)
- [ ] All evidence URLs are exact documents
- [ ] All sources have accessed_date
- [ ] Critical phases 9, 10, 12 included
- [ ] Executive brief synthesizes all phases

---

## Previous Versions

- **v3.7 / v1.7**: NATO integration, quality controls (archived)
- **v3.6 / v1.6**: Base NATO framework
- **v3.5 / v1.5**: US involvement toggles
- **v3.4 / v1.4**: MCF assessment framework
- **v3.3 / v1.3**: Phase renumbering (0-13)

---

*All previous versions archived in `docs/prompts/archive/`*
