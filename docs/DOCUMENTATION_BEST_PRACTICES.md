# DOCUMENTATION BEST PRACTICES FOR FINDINGS
## Mandatory Requirements for All OSINT Analysis

**Created:** 2025-09-20
**Purpose:** Ensure all findings are properly documented, verifiable, and reproducible

---

## 📚 WHY DOCUMENT FINDINGS

### The Core Problem We Solved
- **Previously:** Created compelling narratives first, then fabricated evidence ("78 personnel transfers")
- **Now:** Process actual data first, document real findings, use INSUFFICIENT_EVIDENCE for gaps

### Documentation Ensures
1. **Traceability** - Every number traces to source file and line
2. **Reproducibility** - Anyone can regenerate findings with provided commands
3. **Accountability** - Cannot hide fabrication in undocumented claims
4. **Transparency** - Coverage gaps explicitly stated
5. **Verifiability** - Third parties can audit our work

---

## 📋 MANDATORY DOCUMENTATION STRUCTURE

Every analysis MUST produce these three documents:

### 1. Executive Summary (`EXECUTIVE_SUMMARY_[TOPIC]_FINDINGS.md`)

**Purpose:** High-level findings for decision makers

**Required Sections:**
```markdown
# Executive Summary: [Topic] Findings
## Evidence-Based Assessment from [Size]GB Dataset Analysis

## THE BOTTOM LINE
**Finding:** [One-sentence summary]
**Evidence:** [3-5 bullet points with specific numbers]

## KEY FINDINGS AT A GLANCE
### 1. SCALE
[Exact numbers with percentages]

### 2. TREND
[Direction with quantification]

### 3. COMPARISON
[Context against baselines]

## DATA CONFIDENCE
### What We Know (High Confidence 0.90):
✅ [Specific verified facts]

### What We Don't Know:
⏸️ [Gaps requiring further analysis]

## VERIFICATION
All data verifiable via:
```bash
# Source: [Database name]
# Location: [File path]
# Commands: [Exact recompute commands]
```
```

### 2. Detailed Findings (`[TOPIC]_DETAILED.md`)

**Purpose:** Complete technical documentation

**Required Elements:**
- Full project/entity lists
- Technology categorizations
- Institution mappings
- Temporal analysis
- Network relationships
- Statistical distributions
- Funding/financial data
- All with source references

### 3. Raw Data Export (`[topic]_data.json`)

**Purpose:** Machine-readable data for verification

**Required Fields:**
```json
{
  "metadata": {
    "source_database": "CORDIS",
    "processing_date": "2025-09-20",
    "total_records": 222,
    "query_parameters": {...},
    "verification_hash": "sha256_here"
  },
  "data": [...],
  "recompute_command": "python script.py --params"
}
```

---

## 🎯 BEST PRACTICES

### 1. Version Control Everything
```bash
# Track all analysis documents
git add analysis/*.md
git commit -m "feat: Document Italy-China findings from CORDIS analysis"

# Include data files (if <100MB)
git add analysis/*_data.json
```

### 2. Include Verification Commands

**Every finding must include its recompute command:**

```markdown
**Finding:** 222 Italy-China collaborative projects
**Verification:**
```bash
# Download CORDIS data
wget https://cordis.europa.eu/data/

# Count H2020 Italy-China projects
jq '.[] | select(.participants[].country == "IT") |
   select(.participants[].country == "CN")' project.json | wc -l
# Result: 168

# Count Horizon Europe
# [Similar command]
# Result: 54

# Total: 168 + 54 = 222
```
```

### 3. Declare Coverage Explicitly

```markdown
## COVERAGE STATEMENT
- ✅ EU Framework Projects: 100% (all CORDIS data processed)
- ✅ Academic Papers: 0.01% (sample of OpenAlex processed)
- ❌ Procurement Contracts: 0% (TED not yet processed)
- ❌ Patents: 0% (USPTO/EPO not connected)
- ❌ Personnel Movement: 0% (LinkedIn ToS prohibits)

**Overall Coverage:** ~25% of publicly available data
```

### 4. Use Standardized Confidence Scale

```markdown
## CONFIDENCE LEVELS
- **0.90-1.00:** Very High (multiple independent sources)
- **0.70-0.89:** High (primary sources verified)
- **0.50-0.69:** Moderate (single source, credible)
- **0.30-0.49:** Low (limited evidence)
- **0.00-0.29:** INSUFFICIENT_EVIDENCE
```

### 5. Document Search Queries

```markdown
## SEARCH METHODOLOGY
### Primary Queries:
1. `"Italy" AND "China" AND "collaboration"`
2. `"Italian companies" AND "Chinese investment"`
3. `"technology transfer" AND "Italy" AND "China"`

### Counterfactual Queries:
1. `"Italy" AND "China" AND "no collaboration"`
2. `"Italy" AND "China" AND "dispute"`
3. `"Italy" AND "China" AND "competition"`

### Null Results:
- Query X returned 0 results (searched on DATE)
```

### 6. Timestamp Everything

```markdown
**Data Collected:** 2025-09-20 14:30 UTC
**Processing Completed:** 2025-09-20 16:45 UTC
**Analysis Generated:** 2025-09-20 17:00 UTC
**Next Update Scheduled:** 2025-09-27
```

---

## 📝 DOCUMENTATION TEMPLATES

### Finding Template

```markdown
### Finding #[N]: [Title]

**Claim:** [Specific claim with number]
**Confidence:** [0.00-1.00]
**Evidence:**
- Source: [Database/File]
- Location: [Path:Line]
- Quote/Data: [Exact text or data]
- Verification: `[command to reproduce]`

**Counterfactual Check:**
- Searched for: [Opposing evidence]
- Result: [What was found]

**Context:**
- Baseline: [Normal rate/amount]
- Significance: [Why this matters]
```

### Gap Documentation Template

```markdown
### Data Gap: [Topic]

**What We Tried:**
1. Searched [database] for [query]
2. Attempted [method]
3. Checked [alternative source]

**Why It Failed:**
- [Specific reason - e.g., "Data not publicly available"]

**What Would Be Needed:**
- [Specific data source or access required]

**Impact on Analysis:**
- [How this gap affects conclusions]

**Status:** INSUFFICIENT_EVIDENCE
```

---

## 📊 AUDIT TRAIL REQUIREMENTS

Every analysis session must generate:

### 1. Search Log (`searches_[date].log`)
```
2025-09-20 14:30:15 | CORDIS | Query: country:IT AND country:CN | Results: 222
2025-09-20 14:31:22 | OpenAlex | Query: institutions.country:IT | Results: 45,234
```

### 2. Processing Log (`processing_[date].log`)
```
2025-09-20 14:35:00 | START | Processing CORDIS H2020 data
2025-09-20 14:36:45 | INFO | Processed 35,389 projects
2025-09-20 14:37:00 | RESULT | Found 168 Italy-China collaborations
```

### 3. Decision Log (`decisions_[date].log`)
```
2025-09-20 14:40:00 | DECISION | Excluded project X - reason: No Italian partner on verification
2025-09-20 14:41:00 | DECISION | Included project Y - both countries confirmed
```

---

## ✅ EXAMPLE OF PROPERLY DOCUMENTED FINDING

From our Italy-China analysis:

```markdown
### Finding: Limited Italy-China EU Research Collaboration

**Claim:** Only 222 projects involve both Italy and China in EU Framework Programs
**Confidence:** 0.95 (Very High)

**Evidence:**
- Source: CORDIS Official EU Database
- Location: `/data/raw/source=cordis/`
- Data: 168 H2020 + 54 Horizon Europe = 222 total
- Verification:
```bash
# Exact commands to reproduce
cd /data/raw/source=cordis/
jq '.[] | select(.participants[].country == "IT") |
   select(.participants[].country == "CN") | .id' h2020/project.json | wc -l
# Result: 168
```

**Counterfactual Check:**
- Searched for: Projects with only one country to verify parser
- Result: 35,167 projects had participants from single countries (parser working correctly)

**Context:**
- Baseline: Italy participates in 9.5% of all EU projects
- China participates in 1.2% of all EU projects
- Statistical expectation: 0.114% overlap if independent
- Actual: 0.41% (3.6x expected, but still very small)

**Coverage:**
- ✅ H2020: 100% of projects analyzed
- ✅ Horizon Europe: 100% of projects analyzed
- ⏸️ Bilateral agreements: Not in CORDIS
- ⏸️ Private sector: No access
```

---

## ❌ COMMON DOCUMENTATION FAILURES TO AVOID

### Numbers Without Context
❌ **WRONG:** "Significant collaboration between Italy and China"
✅ **RIGHT:** "222 joint projects representing 0.41% of EU total"

### Unverifiable Claims
❌ **WRONG:** "Many personnel transfers identified"
✅ **RIGHT:** "INSUFFICIENT_EVIDENCE - LinkedIn data not accessible due to ToS"

### Misleading Trends
❌ **WRONG:** "Growing trend in cooperation"
✅ **RIGHT:** "37.7% decrease from H2020 (168) to Horizon Europe (54)"

### Vague Confidence
❌ **WRONG:** "High confidence" (without number)
✅ **RIGHT:** "Confidence: 0.85 based on complete CORDIS dataset"

### Unsourced Data
❌ **WRONG:** "Data shows..." (without source)
✅ **RIGHT:** "CORDIS project.json lines 15234-15237 show..."

---

## 🔍 ENFORCEMENT CHECKLIST

Before releasing ANY analysis, verify:

- [ ] Executive summary created with key findings
- [ ] Detailed findings document with full data
- [ ] Raw data exported to JSON with metadata
- [ ] All numbers traced to source file and line
- [ ] Recompute commands provided and tested
- [ ] Coverage gaps explicitly stated
- [ ] Confidence scores (0.0-1.0) for all claims
- [ ] Counterfactual searches documented
- [ ] Search queries listed
- [ ] Timestamps on all operations
- [ ] Audit trail files generated
- [ ] Version controlled in git
- [ ] INSUFFICIENT_EVIDENCE used for gaps

**If any item unchecked, analysis is REJECTED.**

---

## 🚀 QUICK REFERENCE

### File Naming Convention
```
analysis/
├── EXECUTIVE_SUMMARY_[TOPIC]_FINDINGS.md
├── [TOPIC]_[NUMBER]_[ENTITY]_DETAILED.md
├── [topic]_data.json
├── searches_[YYYYMMDD].log
├── processing_[YYYYMMDD].log
└── decisions_[YYYYMMDD].log
```

### Git Commit Messages
```bash
# For new findings
git commit -m "feat: Document [topic] findings from [source] analysis"

# For updates
git commit -m "update: Revise [topic] findings with additional [source] data"

# For corrections
git commit -m "fix: Correct [specific error] in [topic] analysis"
```

### Standard Headers
```markdown
**Date:** 2025-09-20
**Author:** [Name/System]
**Sources:** CORDIS, OpenAlex, TED
**Coverage:** [Percentage]
**Confidence:** [0.00-1.00]
**Status:** PRELIMINARY | FINAL | UPDATED
```

---

## 📖 RELATED DOCUMENTS

- `UNIFIED_DATA_INFRASTRUCTURE_INVENTORY.md` - Complete data source inventory
- `IMPLEMENTATION_ENFORCEMENT_CHECKLIST.md` - Mandatory implementation checks
- `EXECUTIVE_SUMMARY_ITALY_CHINA_FINDINGS.md` - Example executive summary
- `ITALY_CHINA_222_PROJECTS_DETAILED.md` - Example detailed findings

---

**Remember:** Every claim must be verifiable. Every number must have a source. Every gap must be acknowledged with INSUFFICIENT_EVIDENCE.

*Document everything. Fabricate nothing.*
