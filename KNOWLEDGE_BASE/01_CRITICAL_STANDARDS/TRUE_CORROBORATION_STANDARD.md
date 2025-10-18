# True Corroboration Standard
**Version:** 1.0
**Date:** 2025-09-19
**Critical Principle:** Different evidence types, not echo chambers

---

## 🎯 THE ECHO CHAMBER PROBLEM

**WRONG:** Reuters reports → NY Times cites Reuters → Washington Post cites Reuters → "Three sources!"
**RIGHT:** Reuters reports → SEC filing confirms → Patent shows same model → Three different evidence types

---

## 📊 TRUE CORROBORATION FRAMEWORK

### What Corroboration IS and ISN'T

```yaml
NOT_CORROBORATION:
  media_echo_chamber:
    - Reuters reports claim
    - NY Times cites Reuters
    - WSJ quotes same Reuters article
    - Bloomberg references Reuters story
    reality: "ONE source repeated four times"

  citation_cascade:
    - Blog A makes claim
    - Blog B cites Blog A
    - News site cites Blog B
    - Wikipedia cites news site
    reality: "Telephone game, not verification"

  press_release_propagation:
    - Company issues press release
    - Trade publications republish
    - News outlets report on release
    - Analysts quote the news
    reality: "Single source (company) amplified"

TRUE_CORROBORATION:
  independent_evidence:
    - Reuters: "Leonardo trains Chinese technicians"
    - SEC filing: "Revenue from training services in China: $50M"
    - Patent filing: "Training simulator patent filed in Beijing"
    - LinkedIn: "5 profiles showing Leonardo trainer positions in Shanghai"
    - Customs data: "Simulator equipment exported to China"
    reality: "FIVE different evidence types confirming training"

  documentary_variety:
    - News report: Claims technology transfer
    - Government registry: Joint venture registered
    - Financial statement: Revenue from JV disclosed
    - Technical publication: Papers co-authored
    - Conference presentation: Technology demonstrated
    reality: "Multiple independent data streams"
```

---

## 🔍 CORROBORATION SEARCH MATRIX

### For EVERY Single-Source Claim

```yaml
CLAIM: "Leonardo provides helicopter maintenance training in China"
SOURCE: Reuters article, March 2023

CORROBORATION_SEARCH_REQUIREMENTS:

  1_FINANCIAL_EVIDENCE:
    search:
      - SEC Edgar: Leonardo revenue breakdowns
      - Annual reports: Training services income
      - Investor presentations: China operations
      - Financial analysts: Coverage reports
    looking_for: "Revenue from Chinese training contracts"
    if_found: "Corroborates business relationship"

  2_LEGAL_DOCUMENTATION:
    search:
      - Contract databases: Government contracts
      - Corporate registries: Joint ventures
      - Court filings: Any disputes
      - Regulatory filings: Export licenses
    looking_for: "Training agreement documentation"
    if_found: "Confirms formal arrangement"

  3_TECHNICAL_EVIDENCE:
    search:
      - Patent databases: Training systems/simulators
      - Technical standards: Certification requirements
      - Product documentation: Model numbers/specifications
      - Maintenance manuals: Publicly available guides
    looking_for: "Same helicopter model confirmed"
    if_found: "Verifies technical overlap"

  4_HUMAN_EVIDENCE:
    search:
      - LinkedIn: Employee profiles
      - Conference attendee lists: Participation
      - Academic papers: Co-authorship
      - Professional associations: Membership
    looking_for: "Individuals involved in training"
    if_found: "Confirms human component"

  5_PHYSICAL_EVIDENCE:
    search:
      - Satellite imagery: Training facilities
      - Shipping records: Equipment transfers
      - Customs data: Import/export records
      - Aviation registries: Aircraft registrations
    looking_for: "Physical presence/movement"
    if_found: "Proves material reality"

  6_REGULATORY_TRACES:
    search:
      - Export control: License applications
      - Aviation authorities: Certifications
      - Safety boards: Incident reports
      - Environmental: Facility permits
    looking_for: "Regulatory footprint"
    if_found: "Shows official oversight"

DOCUMENTATION_REQUIRED:
  if_corroboration_found:
    - List each independent source type
    - Explain what each confirms
    - Note remaining gaps

  if_no_corroboration_found:
    - Document search attempts
    - List databases checked
    - Note: "[CORROBORATION SOUGHT: Not found in SEC, patents, customs]"
    - Include anyway if critical
    - Mark: "[SINGLE SOURCE: No corroboration found despite search]"
```

---

## 📋 CORROBORATION HIERARCHY

### Tier 1: Best Corroboration (Different Authority Types)
```yaml
GOLD_STANDARD:
  combination:
    - Government registry (legal entity)
    - Financial filing (revenue/costs)
    - Technical documentation (specifications)
    - Physical evidence (satellite/shipping)

  example:
    - CLAIM: "Siemens operates chip fab in China"
    - Corporate registry: "Siemens Semiconductor (Shanghai) Co Ltd"
    - SEC filing: "$500M capital investment in Shanghai facility"
    - Patent filing: "14nm process patents filed in China"
    - Satellite: "300,000 sq ft facility visible at coordinates"

  marking: "[CORROBORATED: Registry + SEC + Patents + Imagery]"
```

### Tier 2: Good Corroboration (Multiple Independent Sources)
```yaml
SOLID_CONFIRMATION:
  combination:
    - Primary source (original report)
    - Financial indicator (revenue/investment)
    - Human evidence (LinkedIn/conferences)

  example:
    - CLAIM: "German engineers work at Chinese aerospace company"
    - News report: "Lufthansa Technik partnership with COMAC"
    - LinkedIn: "15 profiles showing LHT→COMAC moves"
    - Conference: "Joint presentation at Paris Air Show"

  marking: "[PARTIALLY CORROBORATED: News + LinkedIn + Conference]"
```

### Tier 3: Weak Corroboration (Same Type Sources)
```yaml
LIMITED_CONFIRMATION:
  combination:
    - Multiple news sources (with independent reporting)
    - Or multiple human sources (different platforms)
    - Or multiple technical sources (different databases)

  example:
    - CLAIM: "Technology demonstration at conference"
    - Twitter: "Attendee photos of demonstration"
    - LinkedIn: "Different attendee confirms"
    - Conference website: "Agenda shows session"

  marking: "[WEAKLY CORROBORATED: Multiple attendee reports only]"
```

### Tier 4: No Corroboration
```yaml
SINGLE_SOURCE:
  reality:
    - One source only
    - Echoes don't count
    - Searched for corroboration
    - None found

  marking: "[SINGLE SOURCE: No corroboration found]"
  action: Include if critical, mark transparently
```

---

## 🔄 CORROBORATION SEARCH PROTOCOL

### Required Steps for Single-Source Claims

```python
def seek_true_corroboration(claim, original_source):
    """
    MANDATORY: Attempt to corroborate from different evidence types
    """

    # Step 1: Identify claim components
    components = {
        "who": extract_entities(claim),      # Companies, people
        "what": extract_technology(claim),   # Specific tech
        "where": extract_location(claim),    # Country, facility
        "when": extract_timeframe(claim),    # Date range
        "how": extract_mechanism(claim)      # Method of transfer
    }

    # Step 2: Search different evidence types
    searches = {
        "financial": search_financial_records(components),
        "legal": search_legal_documents(components),
        "technical": search_technical_databases(components),
        "human": search_professional_networks(components),
        "physical": search_physical_evidence(components),
        "regulatory": search_regulatory_filings(components)
    }

    # Step 3: Evaluate what was found
    corroboration = []
    for evidence_type, results in searches.items():
        if results:
            # Check if truly independent
            if not is_echo_of_original(results, original_source):
                corroboration.append({
                    "type": evidence_type,
                    "source": results.source,
                    "what_confirms": results.confirmation,
                    "strength": evaluate_strength(results)
                })

    # Step 4: Document the search
    return {
        "corroboration_found": corroboration,
        "searches_attempted": list(searches.keys()),
        "original_source": original_source,
        "marking": generate_marking(corroboration)
    }

def is_echo_of_original(new_source, original):
    """
    Critical: Detect echo chamber
    """
    echo_indicators = [
        new_source.cites(original),
        new_source.quotes(original),
        new_source.published_after(original) and same_claims(original),
        new_source.is_aggregator(),
        new_source.is_reprint()
    ]

    return any(echo_indicators)
```

---

## 📝 DOCUMENTATION REQUIREMENTS

### For Every Finding Based on Single Source

```markdown
## Finding: Leonardo Helicopter Training in China

**Claim:** Leonardo provides maintenance training for AW139 helicopters to Chinese technicians

**Original Source:**
- [1] Reuters. "Leonardo expands China helicopter services." 2023-03-15. [Tier 2]

**Corroboration Attempted:**
- ✓ **Financial:** Searched SEC EDGAR for Leonardo revenue breakdowns
  - Found: 2023 Annual Report shows "Services - Asia Pacific: €450M" but no China breakdown
  - Gap: Country-level service revenue not disclosed

- ✓ **Technical:** Searched patent databases for training systems
  - Found: CN104123854B - "Helicopter maintenance training simulator" filed by Leonardo
  - Confirms: Training capability exists

- ✓ **Human:** Searched LinkedIn for Leonardo trainers in China
  - Found: 3 profiles with "Leonardo Helicopters Training Instructor - Shanghai"
  - Confirms: Human presence for training

- ✗ **Legal:** Searched for training contracts
  - Not found: No public contracts available
  - Gap: Commercial contracts not public

- ✗ **Physical:** Searched for training facility
  - Not found: No specific facility identified
  - Gap: May use customer facilities

**Corroboration Result:**
[PARTIALLY CORROBORATED: Patent + LinkedIn confirm training capability, financial data suggestive but not specific]

**Confidence Adjusted:**
From 30% (single source) to 45% (partial corroboration from patents and human evidence)

**Remaining Gaps:**
- Contract documentation
- Facility location
- Training curriculum
- Number of technicians trained
```

---

## ⚠️ CRITICAL DISTINCTIONS

### Echo Chamber Examples (NOT Corroboration)

```yaml
EXAMPLE_1_MEDIA_ECHO:
  monday: "Reuters: China acquires German semiconductor technology"
  tuesday: "NYT: China obtains chip tech from Germany, according to Reuters"
  wednesday: "FT: Reports suggest China acquired German semiconductor capabilities"
  thursday: "WSJ: German chip technology reportedly transferred to China"

  reality: ONE claim, ZERO corroboration
  marking: "[MEDIA ECHO: Single Reuters claim repeated]"

EXAMPLE_2_WIKIPEDIA_CASCADE:
  origin: "Company press release"
  step_1: "Trade publication quotes press release"
  step_2: "Wikipedia cites trade publication"
  step_3: "News article cites Wikipedia"
  step_4: "Analyst report cites news article"

  reality: Company claim laundered through citations
  marking: "[CITATION CASCADE: Origin is single press release]"
```

### True Corroboration Examples

```yaml
EXAMPLE_1_MULTIPLE_EVIDENCE_TYPES:
  claim: "Siemens transfers turbine technology to China"

  evidence_1: "Reuters reports technology transfer deal"
  evidence_2: "German export license #DE2023-4521 for turbine components"
  evidence_3: "Chinese patent CN298347234 lists Siemens as inventor"
  evidence_4: "Satellite shows turbine facility construction at coordinates"

  reality: FOUR independent evidence types confirm
  marking: "[CORROBORATED: News + License + Patent + Imagery]"

EXAMPLE_2_DOCUMENTARY_VARIETY:
  claim: "German university collaborates with Chinese military institution"

  evidence_1: "University website lists partnership"
  evidence_2: "Joint research papers in IEEE database"
  evidence_3: "EU project funding records show joint grant"
  evidence_4: "Conference registration shows co-attendance"

  reality: Multiple independent documentation streams
  marking: "[CORROBORATED: University + Papers + Funding + Conference]"
```

---

## 🎯 IMPLEMENTATION CHECKLIST

### When You Have a Single Source:

1. **Identify the claim components**
   - [ ] Who (entities)
   - [ ] What (technology)
   - [ ] Where (location)
   - [ ] When (timeframe)
   - [ ] How (mechanism)

2. **Search for different evidence types**
   - [ ] Financial records
   - [ ] Legal documents
   - [ ] Technical databases
   - [ ] Human networks
   - [ ] Physical evidence
   - [ ] Regulatory filings

3. **Check for echo chamber**
   - [ ] Is new source citing original?
   - [ ] Published after original?
   - [ ] Same claims exactly?
   - [ ] Just an aggregator?

4. **Document the search**
   - [ ] What was searched
   - [ ] What was found
   - [ ] What wasn't found
   - [ ] Why gaps exist

5. **Adjust confidence accordingly**
   - [ ] No corroboration: Stay at 30%
   - [ ] Weak corroboration: Up to 40%
   - [ ] Partial corroboration: Up to 50%
   - [ ] Strong corroboration: Up to 70%

6. **Mark transparently**
   - [ ] [SINGLE SOURCE: description]
   - [ ] [CORROBORATION SOUGHT: databases checked]
   - [ ] [PARTIALLY CORROBORATED: what confirmed]
   - [ ] [ECHO CHAMBER: if detected]

---

## 🔴 RED FLAGS

- Multiple news stories all published same day → Check for common source
- All sources quote each other → Citation circle
- Only evidence is press releases → Company controlling narrative
- All sources are aggregators → No original reporting
- Timeline too perfect → Check for coordinated release

## 🟢 GREEN FLAGS

- Different evidence types align
- Financial data supports claims
- Technical documentation matches
- Timeline makes sense across sources
- Physical evidence visible
- Regulatory footprint exists

---

## 💡 REMEMBER

**One Reuters article cited by 20 newspapers = ONE source**

**One Reuters article + one patent + one SEC filing = THREE sources**

**Different evidence types > Multiple citations**

**True corroboration requires independence**

---

*Stop counting echoes. Start finding evidence.*
