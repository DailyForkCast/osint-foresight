# Fabrication Check Report
Generated: 2025-09-21T14:44:37.524216

## Summary
- **Files Checked:** 215
- **Total Issues:** 1910
- **High Severity:** 161 [WARNING]
- **Medium Severity:** 1749 [CAUTION]
- **Low Severity:** 0 [NOTE]

## Critical Issues (High Severity)

### C:\Projects\OSINT - Foresight\docs\FABRICATION_ANALYSIS_RESULTS.md:26
- **Type:** KNOWN_FABRICATION
- **Issue:** Contains known fabricated number: €12B
- **Text:** `| **€12B** | Made-up EU-China trade figure | Remove all instances |`
- **Fix:** Remove or mark with [HYPOTHETICAL EXAMPLE]

### C:\Projects\OSINT - Foresight\docs\FABRICATION_ANALYSIS_RESULTS.md:26
- **Type:** KNOWN_FABRICATION
- **Issue:** Contains known fabricated number: 12B
- **Text:** `| **€12B** | Made-up EU-China trade figure | Remove all instances |`
- **Fix:** Remove or mark with [HYPOTHETICAL EXAMPLE]

### C:\Projects\OSINT - Foresight\docs\FABRICATION_ANALYSIS_RESULTS.md:28
- **Type:** KNOWN_FABRICATION
- **Issue:** Contains known fabricated number: 100,000
- **Text:** `| **100,000-500,000** | Invented collaboration range | Remove or mark as example |`
- **Fix:** Remove or mark with [HYPOTHETICAL EXAMPLE]

### C:\Projects\OSINT - Foresight\docs\FABRICATION_ANALYSIS_RESULTS.md:28
- **Type:** KNOWN_FABRICATION
- **Issue:** Contains known fabricated number: 100,000-500,000
- **Text:** `| **100,000-500,000** | Invented collaboration range | Remove or mark as example |`
- **Fix:** Remove or mark with [HYPOTHETICAL EXAMPLE]

### C:\Projects\OSINT - Foresight\docs\FABRICATION_ANALYSIS_RESULTS.md:28
- **Type:** KNOWN_FABRICATION
- **Issue:** Contains known fabricated number: 500,000
- **Text:** `| **100,000-500,000** | Invented collaboration range | Remove or mark as example |`
- **Fix:** Remove or mark with [HYPOTHETICAL EXAMPLE]

### C:\Projects\OSINT - Foresight\docs\FABRICATION_ANALYSIS_RESULTS.md:58
- **Type:** KNOWN_FABRICATION
- **Issue:** Contains known fabricated number: 100,000
- **Text:** `3. Remove or mark actual fabrications (€12B, 4,500, 100,000-500,000)`
- **Fix:** Remove or mark with [HYPOTHETICAL EXAMPLE]

### C:\Projects\OSINT - Foresight\docs\FABRICATION_ANALYSIS_RESULTS.md:58
- **Type:** KNOWN_FABRICATION
- **Issue:** Contains known fabricated number: €12B
- **Text:** `3. Remove or mark actual fabrications (€12B, 4,500, 100,000-500,000)`
- **Fix:** Remove or mark with [HYPOTHETICAL EXAMPLE]

### C:\Projects\OSINT - Foresight\docs\FABRICATION_ANALYSIS_RESULTS.md:58
- **Type:** KNOWN_FABRICATION
- **Issue:** Contains known fabricated number: 100,000-500,000
- **Text:** `3. Remove or mark actual fabrications (€12B, 4,500, 100,000-500,000)`
- **Fix:** Remove or mark with [HYPOTHETICAL EXAMPLE]

### C:\Projects\OSINT - Foresight\docs\FABRICATION_ANALYSIS_RESULTS.md:58
- **Type:** KNOWN_FABRICATION
- **Issue:** Contains known fabricated number: 12B
- **Text:** `3. Remove or mark actual fabrications (€12B, 4,500, 100,000-500,000)`
- **Fix:** Remove or mark with [HYPOTHETICAL EXAMPLE]

### C:\Projects\OSINT - Foresight\docs\FABRICATION_ANALYSIS_RESULTS.md:58
- **Type:** KNOWN_FABRICATION
- **Issue:** Contains known fabricated number: 500,000
- **Text:** `3. Remove or mark actual fabrications (€12B, 4,500, 100,000-500,000)`
- **Fix:** Remove or mark with [HYPOTHETICAL EXAMPLE]

## Emerging Patterns

### PATTERN_RISK
- **Frequency:** 1714 occurrences
- **Spread:** 145 files
- **Examples:** | **Ted** | 24.2GB | ✅ Ready | EU contracts 2006-2, python scripts/process_ted_procurement_multicountr, python scripts/process_ted_procurement_multicountr

### KNOWN_FABRICATION
- **Frequency:** 159 occurrences
- **Spread:** 16 files
- **Examples:** | **€12B** | Made-up EU-China trade figure | Remov, | **€12B** | Made-up EU-China trade figure | Remov, | **100,000-500,000** | Invented collaboration ran

### SUSPICIOUS_PRECISION
- **Frequency:** 35 occurrences
- **Spread:** 9 files
- **Examples:** | OpenAlex | 420.66 GB | 0.5% | 99.5% | 20-30 hour, - Suspiciously precise decimals (e.g., 123.45%), | OpenAlex | 420.66 GB | 3 of 770 large files | 1,

## Recommendations
1. Review all HIGH severity issues immediately
2. Add proper markers to unverified numbers
3. Separate verified and hypothetical data
4. Run this check before any major commits
5. Consider adding to CI/CD pipeline

## Marker Reference
- `[VERIFIED DATA]` - For confirmed numbers from sources
- `[HYPOTHETICAL EXAMPLE]` - For illustrative scenarios
- `[ILLUSTRATIVE ONLY]` - For teaching examples
- `[PROJECTION - NOT VERIFIED]` - For future estimates
- `[EVIDENCE GAP: detail]` - For missing data

---
*Run `python scripts/fabrication_checker.py` for updated report*
