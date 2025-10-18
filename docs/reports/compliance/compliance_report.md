# Playbook Compliance Report

Generated: 2025-09-24T18:33:37.494637


## Phase 0 Compliance Checklist

### Required Artifacts:
- [✅] inventory_manifest.json with SHA256 hashes
- [✅] OS-level verification (dir /s or ls -lR)
- [✅] 10 random file paths with size + first 2KB hex dump
- [✅] parse_failure_triage classification
- [✅] phase0_verification_report.md

### Required Validations:
- [✅] Manifest reconciles with OS totals
- [✅] SHA256 hashes computed
- [✅] Hex dumps generated
- [✅] Go/No-Go gate decision

**Compliance: 100.0%**

---

## Phase 1 Compliance Checklist

### Required Artifacts:
- [✅] content_profile.json per-file
- [✅] Database introspection with table/row counts
- [✅] Stratified sampling N=20 per dataset
- [✅] Sample packs in samples/<dataset>/
- [✅] Delta logging vs previous run

### Required Validations:
- [✅] 3 proofs for any 'XX GB analyzed' claim
- [✅] Parse success rates documented
- [✅] Schema inference completed
- [✅] Row counts verified

**Compliance: 100.0%**

---

## Phase 2 Compliance Checklist

### Required Artifacts:
- [✅] Canonical field definitions
- [✅] joinability_matrix.csv
- [✅] data_quality_scorecards.json (0-100)
- [✅] 10 random successful joins per high-viability pair

### Required Validations:
- [✅] All sources mapped to canonical fields
- [✅] Joinability scores computed
- [✅] Quality metrics 0-100 scale
- [✅] Join examples documented

**Compliance: 100.0%**

---

## Phase 3 Compliance Checklist

### Required Artifacts:
- [✅] china_dictionary.json with sources
- [✅] variant_coverage_matrix.csv
- [✅] Evidence packs for Huawei, COSCO
- [✅] Control group benchmarks
- [✅] Cross-script normalization logs

### Required Validations:
- [✅] All variant types tested
- [✅] False positive/negative rates
- [✅] Null justification notes
- [✅] Coverage metrics

**Compliance: 100.0%**

---

## Phase 4 Compliance Checklist

### Required Artifacts:
- [✅] Temporal views (monthly/yearly)
- [✅] Geographic views (ISO, EU buckets)
- [✅] Technology taxonomy mapping
- [✅] Export SQL/code with row counts
- [✅] Reconciliation tables
- [✅] Error bars/confidence intervals

### Required Validations:
- [✅] Temporal coverage 2000-present
- [✅] All EU countries mapped
- [✅] Reconciliation deltas <5%
- [✅] Bias notes documented

**Compliance: 100.0%**

---

## Phase 5 Compliance Checklist

### Required Artifacts:
- [✅] Entity registry with >70% alias coverage
- [✅] Entity timelines merged across sources
- [✅] 10 entity provenance packs (≥3 sources)
- [✅] Precision/recall scores
- [✅] Mismatch reports

### Required Validations:
- [✅] NER recall >70%
- [✅] Entity deduplication
- [✅] Cross-source verification
- [✅] Timeline consistency

**Compliance: 100.0%**

---

## Phase 6 Compliance Checklist

### Required Artifacts:
- [✅] Automated readiness scores
- [✅] run.json for every step
- [✅] Compliance checklist
- [✅] Access control implementation
- [✅] Retention clocks

### Required Validations:
- [✅] All quality gates defined
- [✅] Monitoring active
- [✅] Governance documented
- [✅] Break-glass appendix

**Compliance: 100.0%**

---
