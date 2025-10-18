# Fabrication Prevention Guide
**Last Updated:** 2025-09-21
**Status:** ACTIVE MONITORING - 258 High Severity Issues Detected

---

## 🚨 Current Alert Status
**WARNING:** Fabrication checker found **258 high severity issues** in project documentation.
- Most common: Numbers 222, 168 appearing without verification markers
- Run `python scripts/fabrication_checker.py` for current status

## 📋 Prevention Protocol

### 1. ALWAYS Mark Your Data

Every number, statistic, or claim MUST have one of these markers:

| Marker | Use Case | Example |
|--------|----------|---------|
| `[VERIFIED DATA]` | Actual data from sources | `[VERIFIED DATA] 68 Germany-China collaborations (source: OpenAlex sample)` |
| `[HYPOTHETICAL EXAMPLE]` | Teaching scenarios | `[HYPOTHETICAL EXAMPLE] If we found 4,500 contracts...` |
| `[ILLUSTRATIVE ONLY]` | Demonstration values | `[ILLUSTRATIVE ONLY] penetration_rate = 12.3%` |
| `[PROJECTION - NOT VERIFIED]` | Future estimates | `[PROJECTION - NOT VERIFIED] Could reach 10,000 by 2027` |
| `[EVIDENCE GAP: detail]` | Missing data | `[EVIDENCE GAP: Financial data unavailable]` |

### 2. NEVER Mix Real and Hypothetical

❌ **WRONG:**
```markdown
We found 222 contracts in Italy. If we extrapolate to all EU countries,
we might find 4,500 contracts total.
```

✅ **CORRECT:**
```markdown
[VERIFIED DATA] 222 contracts in Italy (source: TED processing)

[HYPOTHETICAL EXAMPLE] If similar patterns exist across EU,
theoretical total could be XXX contracts (NOT VERIFIED)
```

### 3. Known Fabrication Triggers

These numbers have been wrongly used as "facts" - avoid or mark carefully:
- **€12B, 12 billion** - Fabricated EU-China trade figure
- **4,500 contracts** - Hypothetical TED projection
- **100,000-500,000** - Made-up collaboration range
- **168, 222** - Real but often misused numbers

### 4. Regular Checks

#### Automated Checking
```bash
# Run manual check
python scripts/fabrication_checker.py

# Schedule regular checks (every 12 hours)
python scripts/schedule_fabrication_checks.py

# View latest report
cat docs/reports/FABRICATION_CHECK_REPORT.md
```

#### Windows Task Scheduler Setup
1. Open Task Scheduler
2. Create Basic Task
3. Name: "OSINT Fabrication Check"
4. Trigger: Daily, repeat every 12 hours
5. Action: Start program
6. Program: `C:\Projects\OSINT - Foresight\scripts\schedule_fabrication_checks.bat`

#### Manual Review Checklist
Before any commit or major documentation update:
- [ ] Run fabrication checker
- [ ] Review HIGH severity issues
- [ ] Add missing markers
- [ ] Separate mixed real/hypothetical sections
- [ ] Verify all specific numbers have sources

## 🔍 Detection Patterns

The fabrication checker looks for:

### High Risk Patterns
- Numbers without `[VERIFIED DATA]` markers
- Known fabricated values (€12B, 4,500, etc.)
- Mixed verified and hypothetical in same paragraph

### Medium Risk Patterns
- Large numbers (1,000+) without verification
- Currency amounts without sources
- Percentages without attribution
- Future projections without `[PROJECTION]` marker
- Suspiciously precise decimals (e.g., 123.45%)

## 📊 Historical Tracking

View fabrication check history:
```bash
# See all historical checks
cat docs/reports/fabrication_check_history.jsonl | jq .

# Count violations over time
cat docs/reports/fabrication_check_history.jsonl | jq '.violations | length'
```

## 🚦 Threshold Limits

Current acceptable thresholds (configured in `schedule_fabrication_checks.py`):
- **High Severity:** 0 (zero tolerance)
- **Medium Severity:** 50
- **Total Issues:** 100

Exceeding these triggers alerts and blocks.

## 💡 Best Practices

### DO:
- ✅ Mark every number with appropriate tag
- ✅ Keep real and hypothetical in separate sections
- ✅ Include source file/path for verified data
- ✅ Use obvious placeholders (XXX, [NUMBER]) for examples
- ✅ Run checker before commits
- ✅ Question suspiciously round numbers

### DON'T:
- ❌ State "expected" without `[PROJECTION]` marker
- ❌ Mix real data with illustrative scenarios
- ❌ Extrapolate from single country to EU totals
- ❌ Use realistic-looking numbers in examples
- ❌ Trust numbers without verification
- ❌ Assume patterns mean conspiracy

## 🔧 Troubleshooting

### Common False Positives
- Dates (2024, 2025) - Usually okay if in temporal context
- Version numbers (9.4, 9.5) - Generally acceptable
- Code line numbers - Ignored in code blocks
- Page numbers in citations - Add `p.` prefix

### If You Find Fabrication
1. **Don't panic** - Mark it immediately
2. **Trace the source** - Where did it come from?
3. **Fix all occurrences** - Search entire project
4. **Update the checker** - Add to known patterns if recurring
5. **Document lessons** - Update this guide

## 📈 Current Statistics

As of last check:
- Files checked: 210
- High severity issues: 258
- Most common: Unmarked "222" and "168"
- Spread: 29 files contain known fabrications

## 🎯 Goal

**Zero high-severity fabrication issues** in all documentation.

Regular checks ensure we maintain evidence-based analysis and prevent illustrative examples from becoming "facts."

---

## Quick Reference Card

```markdown
[VERIFIED DATA] 123 items (source: file.json)      ✅
[HYPOTHETICAL EXAMPLE] If we found 999...          ✅
[ILLUSTRATIVE ONLY] rate = XXX                     ✅
[PROJECTION - NOT VERIFIED] Could be 456           ✅
[EVIDENCE GAP: Missing financial data]             ✅

We found 123 contracts                             ❌ (needs marker)
Expected to find 456                               ❌ (needs projection marker)
Approximately 789 cases                            ❌ (needs source or marker)
```

---

*Run `python scripts/fabrication_checker.py` to check current status*
