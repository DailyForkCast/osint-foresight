# Manual Verification Protocol for EU-China Agreements
## ZERO FABRICATION - COMPLETE VERIFICATION - MANDATORY DOCUMENTATION

---

## 📋 Verification Workflow Overview

Every discovered agreement URL from Common Crawl **MUST** be manually verified before use.

### Verification Status Levels:
- **PENDING**: Initial state, awaiting verification
- **VERIFIED**: Agreement confirmed to exist with documented evidence
- **REJECTED**: Cannot verify or false positive
- **PARTIAL**: Some information verified, needs additional confirmation

---

## ✅ Step-by-Step Verification Process

### Step 1: Access Original URL

```markdown
## Verification Record

**Record ID**: [SHA256 hash of URL]
**Source URL**: [Original URL from Common Crawl]
**Common Crawl Date**: [When page was crawled]
**WARC Location**: [File:Offset for raw content]

### 1. URL Accessibility Check
- [ ] URL currently accessible
- [ ] Redirects to: [New URL if redirected]
- [ ] Error code if not accessible: [404, 403, etc.]
- [ ] Archive.org fallback URL: [Wayback Machine link]
```

### Step 2: Content Verification

```markdown
### 2. Content Verification
- [ ] Page contains agreement information
- [ ] Agreement type confirmed:
  - [ ] Sister city partnership
  - [ ] University cooperation
  - [ ] Government MoU
  - [ ] Economic agreement
  - [ ] Cultural exchange
  - [ ] Other: [Specify]

### Agreement Details Found:
**Title (English)**: [Exact title if available]
**Title (Native)**: [Original language title]
**Parties**:
  - EU Party: [City/University/Agency name]
  - Chinese Party: [Corresponding entity]
**Date Signed**: [YYYY-MM-DD if available]
**Date Effective**: [YYYY-MM-DD if different]
**Status**: [Active/Terminated/Suspended/Unknown]
```

### Step 3: Evidence Documentation

```markdown
### 3. Evidence Documentation
**Primary Source Type**:
- [ ] Official government website
- [ ] Municipal portal
- [ ] University website
- [ ] Press release
- [ ] Legal document (PDF)
- [ ] News article
- [ ] Other: [Specify]

**Key Quote/Excerpt**:
```
[Paste relevant text that confirms agreement]
```

**Screenshot Saved**: [Filename with timestamp]
**PDF Downloaded**: [Filename if applicable]
```

### Step 4: Cross-Reference Validation

```markdown
### 4. Cross-Reference Check
**Secondary Sources Found**:
1. [URL of corroborating source]
2. [Additional source if available]

**Official Registry Check**:
- [ ] EUR-Lex: [Document number if found]
- [ ] Sister Cities International: [Listing confirmed Y/N]
- [ ] Government gazette: [Publication reference]
```

### Step 5: Final Verification Decision

```markdown
### 5. Verification Decision
**Status**: [VERIFIED/REJECTED/PARTIAL]
**Confidence Level**: [High/Medium/Low]
**Verified By**: [Researcher name]
**Verification Date**: [YYYY-MM-DD HH:MM]

**Notes**:
[Any additional context, concerns, or observations]

**Citation for Verified Agreement**:
```
[Generate proper citation including Common Crawl source and verification]
```
```

---

## 📊 Verification Tracking Template

### Excel/CSV Format for Batch Verification

```csv
record_id,source_url,crawl_date,verification_status,agreement_type,eu_party,chinese_party,date_signed,current_status,verified_by,verification_date,confidence_level,notes,citation
abc123,https://example.gov/sister-city,2024-02-15,PENDING,,,,,,,,,,
def456,https://uni.edu/partnerships,2024-02-15,PENDING,,,,,,,,,,
```

### SQL Table for Database Tracking

```sql
CREATE TABLE agreement_verifications (
    record_id VARCHAR(64) PRIMARY KEY,
    source_url TEXT NOT NULL,
    crawl_date DATE,
    warc_location TEXT,

    -- Verification fields
    verification_status ENUM('PENDING', 'VERIFIED', 'REJECTED', 'PARTIAL'),
    verification_date TIMESTAMP,
    verified_by VARCHAR(100),
    confidence_level ENUM('HIGH', 'MEDIUM', 'LOW'),

    -- Agreement details
    agreement_type VARCHAR(50),
    agreement_title_en TEXT,
    agreement_title_native TEXT,
    eu_party VARCHAR(255),
    chinese_party VARCHAR(255),
    date_signed DATE,
    date_effective DATE,
    current_status VARCHAR(50),

    -- Evidence
    primary_source_type VARCHAR(50),
    key_excerpt TEXT,
    screenshot_file VARCHAR(255),
    pdf_file VARCHAR(255),
    secondary_sources TEXT,

    -- Metadata
    notes TEXT,
    citation TEXT,
    common_crawl_citation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 🔍 Verification Best Practices

### DO:
✅ **Save evidence** - Screenshots, PDFs, excerpts
✅ **Check multiple sources** - Verify from 2+ independent sources
✅ **Document everything** - Even failed verifications provide data
✅ **Use Archive.org** - For URLs no longer accessible
✅ **Record exact quotes** - Copy key text confirming agreement
✅ **Note discrepancies** - Different dates, names, status

### DON'T:
❌ **Assume or infer** - Only record what's explicitly stated
❌ **Skip documentation** - Every check needs evidence
❌ **Mark as verified without proof** - Partial is better than false verification
❌ **Ignore context** - Check if agreement is current or historical
❌ **Fabricate missing data** - Leave fields blank rather than guess

---

## 📝 Verification Report Template

### Daily Verification Summary

```markdown
# Verification Report - [Date]

## Summary Statistics
- Total URLs reviewed: X
- Verified agreements: X
- Rejected/False positives: X
- Partial verifications: X
- Pending review: X

## Verified Agreements by Type
- Sister Cities: X
- University Partnerships: X
- Government Agreements: X
- Economic Cooperation: X
- Cultural Exchange: X

## Key Findings
1. [Notable agreement discovered]
2. [Pattern or trend observed]
3. [Challenges encountered]

## Quality Metrics
- Average confidence level: [High/Medium/Low]
- Secondary source confirmation rate: X%
- Screenshot/PDF documentation rate: X%

## Next Steps
- Priority URLs for tomorrow: [List]
- Needs additional research: [List]
- Requires FOIA/official request: [List]
```

---

## 🔒 Data Integrity Requirements

### Every Verified Agreement Must Have:

1. **Original Common Crawl Citation**
```
Common Crawl Foundation. (2024). Web crawl data from [URL].
Dataset: CC-MAIN-2024-10. WARC: [Filename], Offset: [Number].
Retrieved: [Date]. Available at: https://commoncrawl.org/
```

2. **Verification Citation**
```
Verified by [Name] on [Date]. Original source: [URL].
Accessed: [Date]. Status: [Active/Historical].
Secondary verification: [Source if applicable].
```

3. **Combined Citation for Use**
```
[Agreement Title]. ([Year signed]). [Parties].
Source: [Original URL], verified [Date].
Via Common Crawl Foundation dataset CC-MAIN-2024-10.
Status as of [Date]: [Current status].
```

---

## ⚠️ Critical Reminders

### ZERO FABRICATION PROTOCOL:
- **Empty fields are acceptable** - Better than guessing
- **"Unknown" is valid** - For unverifiable information
- **Partial verification is useful** - Document what you can confirm
- **Failed verifications are data** - Shows what doesn't exist

### VERIFICATION HIERARCHY:
1. **Official government sources** - Highest confidence
2. **Municipal/institutional websites** - High confidence
3. **Press releases/news** - Medium confidence
4. **Third-party databases** - Requires additional verification

### DOCUMENTATION REQUIREMENTS:
- **Every URL checked** must have a record (even if rejected)
- **Every verification** needs evidence (screenshot/excerpt)
- **Every agreement** requires citation with Common Crawl attribution
- **Every session** needs summary report

---

## 📊 Expected Verification Outcomes

Based on Common Crawl results, expect:

### Verification Success Rates:
- **Sister Cities**: 60-70% verifiable (municipal sites generally stable)
- **University Partnerships**: 50-60% verifiable (academic sites change frequently)
- **Government Agreements**: 70-80% verifiable (official sources well-maintained)
- **Overall**: 50-70% of URLs should yield verified agreements

### Common Rejection Reasons:
- Generic page about China (not specific agreement)
- News article mentioning agreement (not official source)
- Page no longer exists (but may be in Archive.org)
- Conference or event page (not formal agreement)
- Planning/proposal stage (not signed agreement)

### Time Estimates:
- **Basic verification**: 5-10 minutes per URL
- **Complex verification**: 15-30 minutes (multiple sources needed)
- **Batch of 100 URLs**: 2-3 days for thorough verification

---

## ✅ Verification Complete Checklist

Before marking an agreement as VERIFIED:

- [ ] Original URL checked (or Archive.org)
- [ ] Agreement text/details found
- [ ] Parties clearly identified
- [ ] Date confirmed (signed or effective)
- [ ] Current status determined
- [ ] Screenshot/PDF saved
- [ ] Secondary source found (if possible)
- [ ] Citation prepared
- [ ] Common Crawl attribution included
- [ ] Evidence documented in tracking system

**Remember: It's better to mark as PARTIAL or REJECTED than to fabricate or assume information.**
