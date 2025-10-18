# MASTER PROMPT V8.0 INTEGRATION GUIDE
**Incorporating ChatGPT's Zero-Fabrication Standard**
**Date:** 2025-09-19
**Priority:** CRITICAL - Implement Immediately

---

## 🚨 MOST CRITICAL ADDITIONS (ANTI-FABRICATION)

### 1. MANDATORY PREFIX FOR EVERY INTERACTION

```yaml
SYSTEM_PREFIX:
  line_1: "Do not infer or fabricate numbers, names, or citations."
  line_2: "If uncertain, output INSUFFICIENT_EVIDENCE with missing items list."
  line_3: "Every paragraph must include source-anchored evidence."
  line_4: "Copy numbers exactly as written in cited source."
  line_5: "Do not round or recompute unless showing work."
```

### 2. INSUFFICIENT_EVIDENCE PROTOCOL

```yaml
WHEN_NO_DATA_EXISTS:
  output_format: |
    INSUFFICIENT_EVIDENCE:
    - Missing: [specific data type]
    - Searched: [databases/sources checked]
    - Needed: [what would answer this]
    - Confidence: Cannot assess without data

  example: |
    INSUFFICIENT_EVIDENCE:
    - Missing: LinkedIn personnel transfer data
    - Searched: SEC filings, USPTO, conference records, Google
    - Needed: LinkedIn API access or manual profile review
    - Confidence: Cannot assess without data
```

### 3. RISK TIER CLASSIFICATION

```yaml
EVERY_CLAIM_MUST_BE_CLASSIFIED:
  tier_A_critical:
    definition: "Specific counts, linkages, briefing material"
    requirements:
      - Two independent sources OR
      - One source + data artifact with checksum
      - Reviewer sign-off
      - Full provenance bundle
    examples: ["78 transfers", "joint patents", "sanctions claims"]

  tier_B_substantive:
    definition: "Assessments, trends, inferences"
    requirements:
      - Source quote verification
      - Admiralty rating
      - Spot review
    examples: ["capability improving", "likely dual-use"]

  tier_C_context:
    definition: "Background, definitions"
    requirements:
      - Single credible source
      - Still documented
    examples: ["NATO founded 1949", "CPU definition"]
```

---

## 🔢 NUMERIC CLAIM REQUIREMENTS

### Every Number Must Have:

```yaml
NUMERIC_EVIDENCE:
  1_exact_source:
    quote: "The exact text containing the number"
    location: "Page/paragraph/cell reference"

  2_calculation_path:
    show: "The SQL/regex/formula used"
    example: "SUM(contracts WHERE vendor='Leonardo')"

  3_recompute_command:
    provide: "Exact command to regenerate"
    example: "grep -c 'China' papers.csv | wc -l"

  4_deduplication:
    keys: "How duplicates were removed"
    example: "Deduped by patent_number + filing_date"

  5_denominator_unit:
    include: "Total population and units"
    example: "67 of 892 total patents (EPO families)"
```

### Example Compliant Output:

```markdown
**Claim:** Leonardo has 67 joint patents with Chinese entities [TIER A]

**Evidence:**
- Quote: "Joint patent applications: 67"
- Source: EPO database export [B1]
- Accessed: 2025-09-19T14:00:00Z
- SHA256: a7b9c2d4e5f6...

**Calculation:**
```sql
SELECT COUNT(DISTINCT patent_family_id)
FROM epo_patents
WHERE applicant_1 LIKE '%Leonardo%'
AND applicant_2 LIKE '%China%'
```

**Recompute:** `psql -d patents -c "SELECT COUNT..." > result.txt`

**Deduplication:** By patent_family_id to avoid counting continuations

**Denominator:** 67 of 4,521 total Leonardo patents (1.48%)

**Confidence:** Moderate (database 6 months old)
**Rationale:** Single authoritative source, needs recent update
```

---

## 🔄 SELF-VERIFICATION REQUIREMENT

### After Every Analysis:

```python
def self_verify_output():
    """
    MANDATORY self-check after drafting
    """

    for claim in output.claims:
        # Can I find the exact quote?
        if not locate_supporting_quote(claim):
            remove_claim(claim)
            log_removal(claim, "No supporting quote found")

        # Is the number exactly copied?
        if has_number(claim):
            if not number_matches_source_exactly(claim):
                remove_claim(claim)
                log_removal(claim, "Number doesn't match source")

        # Are alternatives considered?
        if claim.tier == "A":
            if not has_competing_hypotheses(claim):
                add_requirement(claim, "Need ACH analysis")

    return {
        "verified": len(verified_claims),
        "removed": len(removed_claims),
        "modified": len(modified_claims)
    }
```

### Required Output:
```
Self-Verification Complete:
- 15 claims verified with sources
- 3 claims removed (no supporting evidence)
- 2 claims modified (partial support only)
- 1 claim marked INSUFFICIENT_EVIDENCE
```

---

## 📊 STRUCTURED OUTPUT SCHEMA

### All Outputs Must Follow:

```json
{
  "metadata": {
    "timestamp": "2025-09-19T14:30:00Z",
    "model": "claude-3-opus",
    "retrieval_performed": true,
    "self_verified": true
  },

  "claims": [
    {
      "id": "C001",
      "text": "Leonardo signed 50M euro China contract",
      "tier": "A",
      "confidence": "Low",
      "rationale": "Single source, no corroboration"
    }
  ],

  "evidence": [
    {
      "claim_id": "C001",
      "quote": "Leonardo announced 50 million euro agreement",
      "source": "Reuters",
      "admiralty": "B2",
      "url": "reuters.com/article/123",
      "access_date": "2025-09-19T14:00:00Z",
      "sha256": "b8c9d3e4f5g6...",
      "archive": "web.archive.org/web/..."
    }
  ],

  "alternatives": {
    "claim_id": "C001",
    "hypotheses": [
      {
        "description": "Commercial transaction only",
        "evidence_for": ["Public announcement", "Standard terms"],
        "evidence_against": ["Military end-users"],
        "likelihood": 0.6
      },
      {
        "description": "Technology transfer intent",
        "evidence_for": ["Timing with program"],
        "evidence_against": ["No training mentioned"],
        "likelihood": 0.3
      }
    ]
  },

  "verification": {
    "claims_verified": 1,
    "claims_removed": 0,
    "insufficient_evidence": 0
  }
}
```

---

## ⚠️ TWO-SOURCE RULE FOR TIER A

### High-Impact Claims Requirements:

```yaml
TIER_A_EVIDENCE:
  minimum_requirement:
    EITHER:
      option_1: "Two independent sources"
      option_2: "One source + data artifact"

  independent_means:
    YES:
      - "Reuters + SEC filing"
      - "Patent database + Conference paper"
      - "News + Government registry"

    NO:
      - "Reuters + NYT citing Reuters"
      - "Blog + Wikipedia citing blog"
      - "Press release + News citing release"

  data_artifact:
    definition: "Machine-readable file with checksum"
    examples:
      - "CSV with SHA256 hash"
      - "Database export with verification"
      - "API response with timestamp"
```

---

## 🔒 PROVENANCE BUNDLE REQUIREMENTS

### Every Source Must Include:

```yaml
provenance_bundle:
  mandatory:
    url: "Canonical, de-parameterized"
    access_date: "ISO-8601 UTC (2025-09-19T14:00:00Z)"
    sha256: "Hash of raw content"
    archive_link: "Wayback or Perma.cc"

  source_metadata:
    title: "Document title"
    publisher: "Organization"
    author: "If available"
    date_published: "Original date"
    date_modified: "Last update"
    language: "ISO code"

  processing:
    parser: "Tool + version"
    transform: "Script + args"
    quoted_lines: "Specific evidence used"
    recompute: "Command to regenerate"
```

---

## 🆕 ANTI-CONFABULATION SAFEGUARDS

### System-Level Controls:

```yaml
CONSTRAINTS:
  retrieval_first:
    rule: "No synthesis without retrieval"
    enforce: "Block generation if no sources"

  exact_copying:
    numbers: "Must match source character-for-character"
    names: "No variations or assumptions"
    dates: "Exactly as written"

  regex_locking:
    pattern: "\d+" # Extract only literal digits
    no_reformatting: true
    no_rounding: true

  contradiction_handling:
    rule: "Present both views"
    format: "Source A claims X, Source B claims Y"
    no_averaging: true
```

---

## 📋 IMPLEMENTATION CHECKLIST

### For ChatGPT v8.0:
- [ ] Add anti-confabulation prefix to every interaction
- [ ] Implement INSUFFICIENT_EVIDENCE output
- [ ] Add risk tier classification (A/B/C)
- [ ] Require recompute commands for numbers
- [ ] Add self-verification pass
- [ ] Implement structured JSON output
- [ ] Add SHA256 hashing
- [ ] Require confidence rationales
- [ ] Implement ACH for Tier A claims

### For Claude Code v8.0:
- [ ] Add retrieval-first architecture
- [ ] Implement provenance bundle generation
- [ ] Add deduplication key tracking
- [ ] Create regression test framework
- [ ] Add two-source validation for Tier A
- [ ] Implement structured schema output
- [ ] Add temporal integrity checks
- [ ] Create self-verification loop

---

## 🎯 CRITICAL SUCCESS METRICS

**An output is ONLY valid if:**
1. Every number has a recompute command
2. Every Tier A claim has 2 sources or 1+artifact
3. Every claim has been self-verified
4. INSUFFICIENT_EVIDENCE used when appropriate
5. No fabrication possible

---

## 🔴 REGRESSION TESTS

### Tests That Would Have Caught "78 Transfers":

```python
def test_no_unsourced_numbers():
    """Would have caught: '78 personnel transfers'"""
    for claim in output.claims:
        numbers = extract_numbers(claim.text)
        for num in numbers:
            assert has_exact_source_quote(num)
            assert has_recompute_command(num)
            assert has_sha256_hash(num.source)

def test_insufficient_evidence_used():
    """Would have required: INSUFFICIENT_EVIDENCE output"""
    if not sources_available:
        assert "INSUFFICIENT_EVIDENCE" in output
        assert "Missing:" in output
        assert "Needed:" in output

def test_tier_a_two_sources():
    """Would have required: Second source or artifact"""
    for claim in tier_a_claims:
        assert len(claim.sources) >= 2 or has_artifact(claim)
```

---

**BOTTOM LINE:** These additions would make fabrication technically impossible. Every claim traceable, every number reproducible, every gap acknowledged.

**The "78 transfers" could NEVER happen with these controls.**
