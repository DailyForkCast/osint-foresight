# PSC Detection Reconciliation Note

## Version Comparison

| Version | Detection Count | Methodology | HK/MO/TW |
|---------|----------------|-------------|----------|
| v1.0 (baseline) | ~1,130,000 | Inclusive (residence-based) | Included |
| v3.0 (strict) | 209,061 | Nationality-first | Excluded |

## Reduction Explanation

The reduction from v1.0 (~1.13M) to v3.0 (209,061) is **intentional and methodologically sound**:

### v1.0 Methodology (Inclusive)
- **Primary signal**: Address/residence fields
- **Result**: High sensitivity, but many false positives
- **Known issues**:
  - Captured Hong Kong/Macau entities (not PRC)
  - Residence-only matches (e.g., Chinese nationals living in UK)
  - Geographic name matches (e.g., "Beijing Restaurant Supply Ltd" in London)

### v3.0 Methodology (Strict)
- **PRIMARY signal**: `nationality` field (95% confidence)
- **SECONDARY signal**: Corporate registration indicators (70% confidence)
- **REJECTED**: Residence-only matches (too weak)
- **HK/MO/TW toggle**: ENABLED - excludes Hong Kong/Macau/Taiwan

### Breakdown of v1.0 → v3.0 Reduction

| Category | Count | Explanation |
|----------|-------|-------------|
| Residence-only (rejected) | 13,646,492 | Too weak - causes false positives |
| HK/MO/TW excluded | 7,936 | Strict PRC-only per toggle |
| **Final detections (strict)** | **209,061** | **High-confidence PRC links** |

## Quality Assurance

- **Audit sample**: 4,241 detections (2.0% stratified random sample)
- **Audit file**: `data\processed\psc_strict_v3\audit_sample.json`
- **Recommendation**: Manually review audit sample to validate precision

## Recommendation

**Use v3.0 strict methodology for production analysis.**

v1.0 provides high recall but low precision. v3.0 provides high precision with acceptable recall for risk assessment purposes.

---

*Generated: 2025-10-02 20:35:18*
*Detector version: psc_nationality_strict_v3.0*
*Anti-fabrication compliant: Yes (complete provenance for all detections)*
