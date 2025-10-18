# Claude Code Master Prompt v8.0 - Zero Fabrication Engineering
## Technical Implementation with Absolute Evidence Requirements

**Version:** 8.0 ZERO FABRICATION
**Date:** 2025-09-19
**Core Rule:** No Evidence = No Claim = Return INSUFFICIENT_EVIDENCE

---

## 🚨 MANDATORY SYSTEM CONSTRAINTS

```python
# PREPEND TO EVERY TASK
SYSTEM_CONSTRAINTS = """
Do not infer or fabricate numbers, names, or citations.
If uncertain, return INSUFFICIENT_EVIDENCE with missing items.
Every output must include source-anchored evidence.
Copy numbers exactly as written in source.
Do not round or recompute unless showing work.
"""
```

---

## 🔴 HARD RULES - ENFORCED BY CODE

### The Five Non-Negotiables

```python
def validate_output(claim):
    """Enforce zero fabrication rules"""

    # Rule 1: No Evidence → No Claim
    if not claim.has_source():
        return "INSUFFICIENT_EVIDENCE"

    # Rule 2: Never Invent Quantities
    if claim.has_number() and not claim.has_recompute_command():
        return "REJECTED: Number without recompute"

    # Rule 3: Two-Source Rule for Tier A
    if claim.tier == "A" and len(claim.sources) < 2:
        if not claim.has_data_artifact():
            return "REJECTED: Tier A needs 2 sources"

    # Rule 4: Confidence Label Required
    if not claim.confidence or not claim.rationale:
        return "REJECTED: Missing confidence/rationale"

    # Rule 5: Self-Verification Required
    if not claim.self_verified:
        return "REJECTED: Not self-verified"

    return "VALID"
```

---

## 🎯 RISK TIER CLASSIFICATION SYSTEM

```python
class ClaimTier(Enum):
    """Every claim must be classified"""

    TIER_A_CRITICAL = {
        "definition": "Counts, transfers, linkages, briefings",
        "examples": ["78 personnel transfers", "joint patents", "contracts"],
        "requirements": {
            "sources": 2,  # Minimum
            "admiralty_max": "B2",  # No worse than B2
            "provenance": "complete",
            "recompute": "mandatory",
            "ACH": "required"
        }
    }

    TIER_B_SUBSTANTIVE = {
        "definition": "Assessments, trends, inferences",
        "examples": ["improving capability", "likely dual-use"],
        "requirements": {
            "sources": 1,
            "quote": "mandatory",
            "admiralty": "required",
            "alternatives": "considered"
        }
    }

    TIER_C_CONTEXT = {
        "definition": "Background, definitions",
        "examples": ["NATO history", "tech definitions"],
        "requirements": {
            "sources": 1,
            "credible": True,
            "document": "still required"
        }
    }
```

---

## 🔍 INSUFFICIENT_EVIDENCE PROTOCOL

```python
def insufficient_evidence(query, attempts):
    """
    Return when data unavailable
    """
    return {
        "status": "INSUFFICIENT_EVIDENCE",
        "query": query,
        "missing": identify_missing_data(query),
        "searched": attempts.sources_checked,
        "needed": suggest_data_sources(query),
        "confidence": "Cannot assess without data",
        "timestamp": datetime.utcnow().isoformat()
    }

# Example Output:
{
    "status": "INSUFFICIENT_EVIDENCE",
    "missing": "LinkedIn personnel transfer data",
    "searched": ["SEC EDGAR", "USPTO", "Conference records", "News"],
    "needed": "LinkedIn API or manual profile collection",
    "confidence": "Cannot assess without data"
}
```

---

## 📊 DATA PROCESSING WITH VERIFICATION

### Stream Processing Implementation

```python
def process_data_with_verification(dataset, country_code):
    """
    Process with mandatory verification
    """

    results = {
        "claims": [],
        "evidence": [],
        "insufficient": [],
        "removed": [],
        "metadata": {}
    }

    # Process in verifiable chunks
    for batch in chunk_data(dataset, size=1000):

        for record in batch:
            claim = extract_claim(record)

            # Verify before adding
            if not claim.source:
                results["insufficient"].append({
                    "attempted": claim.text,
                    "reason": "No source found"
                })
                continue

            # Add recompute command
            claim.recompute = generate_recompute(record)

            # Self-verify
            if not self_verify(claim):
                results["removed"].append(claim)
                continue

            results["claims"].append(claim)
            results["evidence"].append(claim.evidence)

        # Checkpoint
        save_checkpoint(results)

    return results
```

---

## 📝 PROVENANCE BUNDLE (Without SHA256)

```python
def create_provenance_bundle(source):
    """
    Create verifiable provenance without SHA256
    """

    return {
        "identification": {
            "url": source.url,
            "title": source.title,
            "author": source.author,
            "publisher": source.publisher,
            "unique_id": extract_unique_id(source.url)  # Article ID, DOI, etc.
        },

        "temporal": {
            "accessed": datetime.utcnow().isoformat(),
            "published": source.published_date,
            "modified": source.last_modified,
            "wayback": f"web.archive.org/web/*/{source.url}"
        },

        "content_markers": {
            "word_count": len(source.text.split()),
            "unique_phrases": extract_unique_phrases(source.text),
            "key_numbers": extract_numbers(source.text),
            "exact_quotes": extract_key_quotes(source.text)
        },

        "verification": {
            "search_terms": generate_search_terms(source),
            "database_ids": {
                "factiva": find_factiva_id(source),
                "lexis": find_lexis_id(source),
                "bloomberg": find_bloomberg_id(source)
            }
        },

        "recompute": generate_retrieval_command(source)
    }
```

---

## 🔢 NUMERIC CLAIMS PROCESSING

```python
def process_numeric_claim(text, source):
    """
    Extract and verify numeric claims
    """

    numbers = extract_numbers(text)

    for num in numbers:
        claim = {
            "value": num.value,
            "context": num.surrounding_text,
            "source": source.identification,
            "exact_quote": get_quote_with_number(num, source),
            "calculation_path": None,
            "recompute_command": None,
            "deduplication_keys": None,
            "denominator": None
        }

        # Try to find calculation
        if source.has_data():
            claim["calculation_path"] = trace_calculation(num, source.data)
            claim["recompute_command"] = generate_sql(num, source.data)
            claim["deduplication_keys"] = identify_dedup_keys(source.data)
            claim["denominator"] = find_total_population(num, source.data)

        # If can't verify, mark insufficient
        if not claim["exact_quote"]:
            return insufficient_evidence(
                f"Number {num.value} found but no source quote",
                {"sources_checked": [source.url]}
            )

        return claim
```

---

## 🔄 SELF-VERIFICATION LOOP

```python
def self_verify_output(output):
    """
    Mandatory verification pass
    """

    verification_log = {
        "verified": [],
        "removed": [],
        "modified": [],
        "insufficient": []
    }

    for claim in output["claims"]:

        # Check exact quote exists
        quote = find_supporting_quote(claim, output["evidence"])
        if not quote:
            verification_log["removed"].append({
                "claim": claim.text,
                "reason": "No supporting quote found"
            })
            output["claims"].remove(claim)
            continue

        # Check numbers match exactly
        if has_numbers(claim.text):
            if not numbers_match_source(claim.text, quote):
                verification_log["removed"].append({
                    "claim": claim.text,
                    "reason": "Numbers don't match source"
                })
                output["claims"].remove(claim)
                continue

        # Check tier requirements
        if not meets_tier_requirements(claim):
            verification_log["modified"].append({
                "claim": claim.text,
                "change": "Downgraded tier or marked insufficient"
            })
            claim.confidence = "Low"
            claim.rationale = "Does not meet tier requirements"

        verification_log["verified"].append(claim.id)

    # Add verification summary
    output["verification_summary"] = (
        f"Self-Verification Complete: "
        f"{len(verification_log['verified'])} verified, "
        f"{len(verification_log['removed'])} removed, "
        f"{len(verification_log['modified'])} modified"
    )

    return output, verification_log
```

---

## 🧩 COMPETING HYPOTHESES ANALYSIS

```python
def analyze_competing_hypotheses(claim):
    """
    Required for Tier A claims
    """

    if claim.tier != "A":
        return None

    hypotheses = {
        "H1_primary": {
            "description": claim.hypothesis,
            "evidence_for": [],
            "evidence_against": [],
            "likelihood": 0.0
        },
        "H2_commercial": {
            "description": "Commercial transaction only",
            "evidence_for": [],
            "evidence_against": [],
            "likelihood": 0.0
        },
        "H3_coincidence": {
            "description": "Coincidental timing/correlation",
            "evidence_for": [],
            "evidence_against": [],
            "likelihood": 0.0
        }
    }

    # Evaluate each hypothesis
    for h_name, hypothesis in hypotheses.items():
        hypothesis["evidence_for"] = find_supporting_evidence(hypothesis["description"])
        hypothesis["evidence_against"] = find_contradicting_evidence(hypothesis["description"])
        hypothesis["likelihood"] = calculate_likelihood(
            len(hypothesis["evidence_for"]),
            len(hypothesis["evidence_against"])
        )

    # Normalize likelihoods
    total = sum(h["likelihood"] for h in hypotheses.values())
    for hypothesis in hypotheses.values():
        hypothesis["likelihood"] = hypothesis["likelihood"] / total

    return hypotheses
```

---

## 📁 SUB-PHASE IMPLEMENTATION

```python
class SubPhase:
    """Execute phases in smaller chunks"""

    def __init__(self, phase_number, sub_number):
        self.id = f"{phase_number}.{sub_number}"
        self.max_batch_size = 1000
        self.verification_required = True

    def execute(self, input_data):
        """
        Process sub-phase with gates
        """

        # Pre-check
        if not self.verify_input(input_data):
            return insufficient_evidence(
                f"Sub-phase {self.id} missing required input",
                {"required": self.required_inputs}
            )

        # Process
        results = self.process_batch(input_data)

        # Verify
        results = self.verify_output(results)

        # Gate check
        if not self.passes_gate(results):
            return {
                "status": "FAILED_GATE",
                "sub_phase": self.id,
                "issues": self.gate_issues
            }

        return results

# Example: Phase 2 broken down
PHASE_2_SUBS = [
    SubPhase(2, 1),  # Inventory sources
    SubPhase(2, 2),  # Process academic
    SubPhase(2, 3),  # Process patents
    SubPhase(2, 4),  # Integrate
    SubPhase(2, 5),  # Validate
]
```

---

## 📊 STRUCTURED OUTPUT SCHEMA

```python
def generate_output(claims, evidence):
    """
    Generate compliant output
    """

    output = {
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "model": "claude-3-opus",
            "version": "8.0",
            "retrieval_performed": True,
            "self_verified": False
        },

        "claims": [],
        "evidence": [],
        "alternatives": {},
        "insufficient": [],
        "verification": {}
    }

    # Add claims with full structure
    for claim in claims:
        claim_obj = {
            "id": claim.id,
            "text": claim.text,
            "tier": claim.tier,
            "confidence": claim.confidence,
            "rationale": claim.rationale,
            "admiralty": claim.source_rating
        }

        # Add evidence
        evidence_obj = {
            "claim_id": claim.id,
            "quote": claim.supporting_quote,
            "source": claim.source_name,
            "url": claim.source_url,
            "access_date": claim.accessed,
            "verification": claim.verification_path,
            "recompute": claim.recompute_command
        }

        output["claims"].append(claim_obj)
        output["evidence"].append(evidence_obj)

        # Add ACH for Tier A
        if claim.tier == "A":
            output["alternatives"][claim.id] = analyze_competing_hypotheses(claim)

    # Self-verify
    output, verification_log = self_verify_output(output)
    output["metadata"]["self_verified"] = True
    output["verification"] = verification_log

    return json.dumps(output, indent=2)
```

---

## 🔒 REGRESSION TESTS

```python
# Tests that would have caught "78 transfers"

def test_no_unsourced_numbers():
    """Every number must have source"""
    output = process_claim("78 personnel transfers")
    assert "INSUFFICIENT_EVIDENCE" in output
    assert "source" not in output or output["source"] is not None

def test_recompute_required():
    """Every number needs recompute command"""
    for claim in output["claims"]:
        if has_number(claim["text"]):
            assert claim.get("recompute_command") is not None

def test_tier_a_two_sources():
    """Tier A needs 2 sources"""
    tier_a_claims = [c for c in output["claims"] if c["tier"] == "A"]
    for claim in tier_a_claims:
        evidence = [e for e in output["evidence"] if e["claim_id"] == claim["id"]]
        assert len(evidence) >= 2 or "artifact" in evidence[0]

def test_self_verification_performed():
    """Self-verification must occur"""
    assert output["metadata"]["self_verified"] == True
    assert "verification_summary" in output
```

---

## ⚠️ ERROR HANDLING

```python
def safe_process(func):
    """Wrapper to prevent fabrication on error"""

    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if result is None:
                return insufficient_evidence(
                    f"Function {func.__name__} returned no data",
                    {"args": args, "kwargs": kwargs}
                )
            return result

        except DataNotFoundError as e:
            return insufficient_evidence(str(e), {"function": func.__name__})

        except Exception as e:
            # Log but don't fabricate
            log_error(e)
            return {
                "status": "ERROR",
                "message": str(e),
                "advice": "Cannot proceed without data"
            }

    return wrapper
```

---

## 🎯 SUCCESS METRICS

```python
def validate_output_compliance(output):
    """
    Check if output meets all requirements
    """

    checks = {
        "no_unsourced_claims": all(c.get("source") for c in output["claims"]),
        "numbers_have_recompute": all(
            c.get("recompute_command")
            for c in output["claims"]
            if has_number(c["text"])
        ),
        "tier_a_two_sources": all(
            len([e for e in output["evidence"] if e["claim_id"] == c["id"]]) >= 2
            for c in output["claims"]
            if c["tier"] == "A"
        ),
        "insufficient_used": "INSUFFICIENT_EVIDENCE" in str(output) where appropriate,
        "self_verified": output["metadata"]["self_verified"] == True
    }

    return all(checks.values()), checks
```

---

## 💡 FINAL IMPLEMENTATION NOTES

**Every function must:**
1. Check for data availability first
2. Return INSUFFICIENT_EVIDENCE if no data
3. Include recompute commands
4. Self-verify before returning
5. Use structured output schema

**Never:**
1. Estimate or guess
2. Fill gaps with plausible data
3. Round or approximate
4. Skip verification
5. Proceed without evidence

---

**THE PRIME DIRECTIVE:**

```python
if not evidence:
    return "INSUFFICIENT_EVIDENCE"
else:
    return verified_claim_with_full_provenance
```

**No exceptions. No fabrication. Ever.**
