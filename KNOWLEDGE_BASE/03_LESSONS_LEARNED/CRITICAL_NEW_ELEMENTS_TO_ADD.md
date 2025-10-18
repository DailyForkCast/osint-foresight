# CRITICAL NEW ELEMENTS FROM CHATGPT'S ZERO-FABRICATION STANDARD
**Elements Not Currently in Our Prompts**
**Date:** 2025-09-19
**Priority:** IMMEDIATE IMPLEMENTATION

---

## 🆕 NEW ELEMENTS WE MUST ADD

### 1. RISK TIER CLASSIFICATION SYSTEM

```yaml
CLAIM_RISK_TIERS:
  tier_A_critical:
    definition: "Counts, transfers, entity linkages, briefing material"
    requirements:
      - Two-source rule MANDATORY
      - Reviewer sign-off required
      - Full provenance bundle
    examples:
      - "78 personnel transfers"
      - "Joint patents count"
      - "Sanctions circumvention claims"

  tier_B_substantive:
    definition: "Policy inferences, capability assessments, trends"
    requirements:
      - Source-quote check
      - Spot review
    examples:
      - "Technology likely dual-use"
      - "Capability improving over time"

  tier_C_context:
    definition: "Definitions, background statements"
    requirements:
      - Single credible source acceptable
      - Still archived
    examples:
      - "NATO founding date"
      - "Technology definitions"
```

### 2. SHA256 HASHING REQUIREMENT

```yaml
FOR_EVERY_SOURCE:
  mandatory_hash:
    what: "SHA256 of raw file (HTML/PDF/CSV)"
    why: "Proves content unchanged"
    how: "Store hash with source"

  example:
    source: "reuters.com/article/123"
    sha256: "a7b9c2d4e5f6..."
    proves: "Content integrity preserved"
```

### 3. RECOMPUTE COMMAND REQUIREMENT

```yaml
FOR_EVERY_NUMBER:
  must_include:
    recompute_command: "Exact CLI/SQL/regex to regenerate"

  examples:
    contracts: "SELECT SUM(value) FROM usaspending WHERE vendor='Leonardo'"
    papers: "grep -c 'China' academic_papers.csv | wc -l"
    patents: "jq '.patents[] | select(.assignee=="Leonardo")' patents.json | wc -l"
```

### 4. INSUFFICIENT_EVIDENCE PROTOCOL

```yaml
WHEN_NO_DATA:
  required_output: "INSUFFICIENT_EVIDENCE"
  must_include:
    - What is missing
    - What was searched
    - What is needed

  format:
    "INSUFFICIENT_EVIDENCE:
    - Missing: LinkedIn data for personnel transfers
    - Searched: SEC, USPTO, conference records
    - Needed: LinkedIn API access or manual collection"
```

### 5. TWO-SOURCE RULE FOR HIGH-IMPACT

```yaml
TIER_A_CLAIMS:
  requirement: ">=2 independent sources OR 1 source + artifact"

  acceptable_combinations:
    option_1: "Reuters + SEC filing"
    option_2: "News report + CSV with checksum"
    option_3: "Patent database + Conference paper"

  not_acceptable:
    - "Reuters + NY Times citing Reuters"
    - "Blog + Wikipedia citing blog"
    - "Press release + News citing release"
```

### 6. CONFIDENCE RATIONALE REQUIREMENT

```yaml
EVERY_CONFIDENCE_LABEL:
  must_have: "One-line rationale"

  examples:
    high: "High: Two filings + EPO dataset (2023-2024), consistent"
    moderate: "Moderate: Single Reuters source + partial LinkedIn data"
    low: "Low: Blog post only, 2019 data, conflicts with recent reports"
```

### 7. ANALYSIS OF COMPETING HYPOTHESES (ACH)

```yaml
FOR_TIER_A_CLAIMS:
  mandatory: "List >=2 plausible alternatives"

  structure:
    hypothesis_1: "Technology transfer deliberate"
    hypothesis_2: "Commercial transaction only"
    hypothesis_3: "Coincidental timing"

  evaluate_each:
    evidence_for: [list]
    evidence_against: [list]
    likelihood: "percentage"
```

### 8. DEDUPLICATION KEYS

```yaml
NUMERIC_CLAIMS:
  must_specify:
    dedup_keys: "How duplicates removed"

  examples:
    patents: "Deduped by patent_number + filing_date"
    personnel: "Deduped by name + ORCID + affiliation + year"
    papers: "Deduped by DOI or title + authors + year"
```

### 9. TEMPORAL INTEGRITY RULES

```yaml
DATE_REQUIREMENTS:
  always_use: "Absolute dates (2024-11-03)"
  never_use: "Recently, last year, currently"

  mark_staleness:
    fresh: "<6 months old"
    stale: "6-24 months old [STALE DATA]"
    ancient: ">24 months [ANCIENT - verify current]"
```

### 10. SELF-VERIFICATION PASS

```yaml
AFTER_DRAFTING:
  mandatory_step: "Self-verify each claim"

  process:
    1. "Re-locate supporting quotes"
    2. "Any miss = delete or retract"
    3. "Report removed claims"

  output:
    "Self-verification complete:
    - 12 claims verified
    - 3 claims removed (no supporting quote)
    - 2 claims modified (partial support only)"
```

### 11. PROVENANCE BUNDLE STRUCTURE

```yaml
EVERY_OUTPUT_REQUIRES:
  provenance_bundle:
    url: "Canonical, de-parameterized"
    access_date: "UTC ISO-8601 format"
    archive_link: "Wayback/Perma.cc"
    sha256: "Hash of raw file"
    source_metadata:
      title: "Article title"
      publisher: "Source organization"
      date_published: "Original date"
      date_modified: "Last update"
      language: "en/de/it/zh"
    parse_spec:
      parser: "Tool name + version"
      mode: "Layout/text extraction"
    transform_log:
      script: "Processing script"
      version: "Script version"
      args: "Arguments used"
      seed: "Random seed if applicable"
    quoted_evidence: "Line numbers/IDs used"
    recompute_command: "How to regenerate"
```

### 12. STRUCTURED OUTPUT SCHEMA

```json
{
  "claims": [
    {
      "text": "Leonardo has 50M euro China contract",
      "risk_tier": "A",
      "confidence": "Moderate",
      "rationale": "Single Reuters source, no corroboration"
    }
  ],
  "evidence": [
    {
      "claim_index": 0,
      "quote": "Leonardo signed 50 million euro agreement",
      "url": "reuters.com/article/123",
      "access_date": "2025-09-19T14:00:00Z",
      "archived_url": "web.archive.org/...",
      "sha256": "a7b9c2d4e5f6..."
    }
  ],
  "provenance": {
    "generator": "Claude",
    "model": "claude-3-opus",
    "retrieval": true,
    "timestamp": "2025-09-19T14:30:00Z"
  }
}
```

### 13. ANTI-CONFABULATION PROMPT PREFIX

```yaml
PREPEND_TO_EVERY_TASK:
  line_1: "Do not infer or fabricate numbers, names, or citations."
  line_2: "If uncertain, say INSUFFICIENT_EVIDENCE."
  line_3: "Every paragraph must include source-anchored evidence."
  line_4: "Copy numbers exactly as written in cited source."
  line_5: "Do not round or recompute unless instructed."
```

### 14. REGRESSION TEST REQUIREMENT

```yaml
AFTER_ANY_ERROR:
  must_add:
    regression_test: "Prevent same failure"

  example:
    error: "Fabricated 78 transfers"
    test: "Check all numbers have source + recompute command"
    runs: "Every CI pipeline execution"
```

### 15. FAIR/PROV-O ALIGNMENT

```yaml
DATA_PRINCIPLES:
  findable: "All data has persistent identifiers"
  accessible: "Retrieval protocols documented"
  interoperable: "Standard formats used"
  reusable: "License and provenance clear"

  provenance_relationships:
    entity: "The data/document"
    activity: "Collection/processing"
    agent: "Person/system responsible"
```

---

## 🔄 INTEGRATION PRIORITY

### IMMEDIATE (Prevents Fabrication):
1. INSUFFICIENT_EVIDENCE protocol
2. Risk tier classification
3. Two-source rule for Tier A
4. Recompute commands
5. Self-verification pass

### HIGH (Ensures Verifiability):
6. SHA256 hashing
7. Provenance bundles
8. Structured output schema
9. Anti-confabulation prefix
10. Deduplication keys

### IMPORTANT (Improves Quality):
11. ACH for major claims
12. Confidence rationales
13. Temporal integrity
14. Regression tests
15. FAIR principles

---

## 🎯 KEY DIFFERENCES FROM OUR CURRENT APPROACH

### ChatGPT's Additions:
- **Risk tiers** (A/B/C) with different requirements
- **SHA256 hashing** for content integrity
- **Recompute commands** for every number
- **INSUFFICIENT_EVIDENCE** as standard output
- **Structured JSON schema** for all outputs
- **Self-verification pass** after drafting
- **Regression testing** after errors

### We Already Have:
- Admiralty ratings
- Alternative hypotheses (but not ACH specifically)
- Corroboration requirements
- Chain of custody (but less structured)
- Confidence levels (but not rationales)

---

## 📝 SAMPLE OUTPUT WITH NEW STANDARDS

```json
{
  "claims": [
    {
      "text": "Leonardo transferred helicopter technology to China",
      "risk_tier": "A",
      "confidence": "Low",
      "rationale": "Single source, no artifact verification"
    }
  ],
  "evidence": [
    {
      "claim_index": 0,
      "quote": "Leonardo signed maintenance agreement for AW139",
      "url": "reuters.com/article/leonardo-china-2025",
      "access_date": "2025-09-19T14:00:00Z",
      "archived_url": "web.archive.org/web/20250919/...",
      "sha256": "b8c9d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0"
    }
  ],
  "competing_hypotheses": {
    "H1_deliberate_transfer": {
      "evidence_for": ["Timing with China heli program"],
      "evidence_against": ["Standard commercial terms"],
      "likelihood": "30%"
    },
    "H2_commercial_only": {
      "evidence_for": ["Public announcement", "Normal pricing"],
      "evidence_against": ["Military end-users"],
      "likelihood": "60%"
    }
  },
  "deduplication": "N/A - single claim",
  "recompute": "grep 'Leonardo.*China.*maintenance' reuters_20250319.txt",
  "provenance": {
    "generator": "Claude",
    "model": "claude-3-opus",
    "retrieval": true,
    "self_verified": true,
    "removed_claims": 0
  }
}
```

---

**BOTTOM LINE:** ChatGPT's standard adds crucial technical rigor we need:
- Tier-based requirements
- Cryptographic verification (SHA256)
- Reproducibility commands
- Structured schemas
- Self-verification loops

These would have prevented the "78 transfers" fabrication completely.
