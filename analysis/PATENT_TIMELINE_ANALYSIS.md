# Patent Timeline Analysis: Application vs. Grant Dates
**Date:** 2025-11-09
**Critical Issue:** Patent processing lag and its impact on causal inference

---

## The Problem You Identified

**Made in China 2025 published:** May 8, 2015

**Your concern:** If we see patents "granted" in 2015-2017, those applications could have been filed BEFORE the policy was published!

**You're absolutely right.** This is a critical temporal issue that can completely invalidate causal claims if not handled correctly.

---

## USPTO Patent Timeline: How It Works

### Standard Patent Processing Timeline

**From application to grant:**

```
Day 0: Patent application filed
  ↓
Month 18: Application published (becomes public)
  ↓
Year 2-3: Patent granted (average)
  ↓
Year 20: Patent expires (if maintained)
```

**Key dates in USPTO records:**

1. **Application Date (Filing Date)** - When inventor submitted application
2. **Publication Date** - When application became public (~18 months later)
3. **Grant Date (Issue Date)** - When patent officially granted
4. **Priority Date** - May be earlier if claiming foreign priority

### Technology-Specific Timelines

**Average time from application to grant (USPTO data):**

| Technology Area | Average Processing Time |
|----------------|------------------------|
| **Semiconductors** | 25-30 months |
| **AI/Software** | 20-24 months |
| **Biotechnology** | 30-36 months |
| **Mechanical** | 24-28 months |
| **Chemistry** | 28-32 months |

**This means:**
- A semiconductor patent granted in **January 2016** was likely applied for in **November 2013**
- A semiconductor patent granted in **December 2017** was likely applied for in **October 2015**

---

## Impact on Made in China 2025 Analysis

### The Critical Timeline

**Made in China 2025 published:** May 8, 2015

**Patents granted 2015-2017 timeline:**

```
Patents granted in 2015:
  Application date: Likely 2012-2013
  → BEFORE MIC2025 ✗ (Cannot be caused by policy)

Patents granted in 2016:
  Application date: Likely 2013-2014
  → BEFORE MIC2025 ✗ (Cannot be caused by policy)

Patents granted in 2017:
  Application date: Likely 2014-2015
  → MIXED (Some before, some after MIC2025)
  → Need to check exact application dates

Patents granted in 2018:
  Application date: Likely 2015-2016
  → AFTER MIC2025 ✓ (Could be policy-influenced)

Patents granted in 2019+:
  Application date: Likely 2016+
  → AFTER MIC2025 ✓ (Could be policy-influenced)
```

### The Correct Date Field to Use

**❌ WRONG: Use grant date**
```sql
-- This is WRONG for causal analysis
SELECT COUNT(*)
FROM patents
WHERE grant_date BETWEEN '2015-01-01' AND '2017-12-31';
```

**Why wrong:** Includes patents applied for before policy existed!

---

**✅ CORRECT: Use application date**
```sql
-- This is CORRECT for causal analysis
SELECT COUNT(*)
FROM patents
WHERE application_date BETWEEN '2015-05-08' AND '2025-12-31';
-- Only patents applied for AFTER MIC2025 published
```

**Why correct:** Only counts patents where the decision to apply could have been influenced by policy.

---

## Revised Causal Analysis Using Application Dates

### Test 1: Immediate Response (0-6 months)

**Question:** Did Chinese companies rush to file patents immediately after MIC2025?

```sql
-- Patents applied for 0-6 months after MIC2025
SELECT
  assignee_country,
  COUNT(*) as patent_applications
FROM patents
WHERE cpc_code LIKE 'H01L%' -- Semiconductors
  AND application_date BETWEEN '2015-05-08' AND '2015-11-08'
GROUP BY assignee_country;

-- Compare to same period previous year (2014)
SELECT
  assignee_country,
  COUNT(*) as patent_applications
FROM patents
WHERE cpc_code LIKE 'H01L%'
  AND application_date BETWEEN '2014-05-08' AND '2014-11-08'
GROUP BY assignee_country;
```

**Interpretation:**

**If Chinese applications spiked 0-6 months post-policy:**
→ **Very strong evidence** of policy response (too fast to be coincidence)

**If no immediate spike:**
→ May take time for policy to translate to applications

---

### Test 2: Sustained Response (1-3 years)

**Question:** Did Chinese applications increase sustainably after policy?

```sql
-- Annual patent applications post-MIC2025
SELECT
  YEAR(application_date) as year,
  assignee_country,
  COUNT(*) as applications
FROM patents
WHERE cpc_code LIKE 'H01L%'
  AND application_date >= '2015-05-08'
GROUP BY YEAR(application_date), assignee_country
ORDER BY year, assignee_country;
```

**Look for:**
- Steady increase 2016, 2017, 2018, 2019, 2020
- Compare to pre-2015 trend
- Compare to other countries

---

### Test 3: Policy Response Latency

**Question:** How long did it take for policy to impact behavior?

**Hypotheses:**

**H1: Immediate response (0-6 months)**
- Companies already working on semiconductors accelerated patent filings
- Suggests policy formalized existing efforts

**H2: Medium-term response (1-2 years)**
- Companies launched new R&D programs in response to policy
- Suggests policy drove new investment

**H3: Long-term response (3-5 years)**
- Policy funded university research → patents emerge later
- Suggests fundamental research pathway

**Test:**
```sql
-- Calculate time-to-response
WITH baseline AS (
  -- Monthly avg applications pre-policy (2010-2015)
  SELECT AVG(monthly_count) as baseline_avg
  FROM (
    SELECT
      YEAR(application_date) || '-' || MONTH(application_date) as month,
      COUNT(*) as monthly_count
    FROM patents
    WHERE assignee_country = 'CN'
      AND cpc_code LIKE 'H01L%'
      AND application_date BETWEEN '2010-01-01' AND '2015-05-07'
    GROUP BY month
  )
),
post_policy AS (
  -- Monthly applications post-policy
  SELECT
    YEAR(application_date) || '-' || MONTH(application_date) as month,
    application_date,
    COUNT(*) as monthly_count
  FROM patents
  WHERE assignee_country = 'CN'
    AND cpc_code LIKE 'H01L%'
    AND application_date >= '2015-05-08'
  GROUP BY month
)

-- Find first month where applications exceed baseline by 50%+
SELECT
  month,
  monthly_count,
  baseline_avg,
  ((monthly_count - baseline_avg) / baseline_avg * 100) as pct_increase,
  DATEDIFF(MONTH, '2015-05-08', MIN(application_date)) as months_after_policy
FROM post_policy
CROSS JOIN baseline
WHERE monthly_count > baseline_avg * 1.5
ORDER BY application_date
LIMIT 1;
```

---

## Priority Date Consideration

### What is Priority Date?

**Scenario:** Chinese company files patent in China first, then files in USPTO later claiming priority

```
Jan 2015: File patent in China (SIPO/CNIPA)
  ↓
May 2015: MIC2025 published
  ↓
Dec 2015: File same patent in USPTO, claiming Jan 2015 priority
```

**Question:** Was this invention conceived before or after MIC2025?

**Answer:** Priority date (Jan 2015) suggests before, but USPTO filing decision (Dec 2015) could be influenced by policy

### How to Handle Priority Claims

**Conservative approach (strictest causality):**
```sql
-- Use priority date if available, otherwise application date
SELECT
  COALESCE(priority_date, application_date) as effective_date,
  COUNT(*) as patents
FROM patents
WHERE assignee_country = 'CN'
  AND cpc_code LIKE 'H01L%'
  AND COALESCE(priority_date, application_date) >= '2015-05-08'
GROUP BY YEAR(effective_date);
```

**Liberal approach (captures decision to file in US):**
```sql
-- Use application date regardless of priority
SELECT
  application_date,
  COUNT(*) as patents
FROM patents
WHERE assignee_country = 'CN'
  AND cpc_code LIKE 'H01L%'
  AND application_date >= '2015-05-08'
GROUP BY YEAR(application_date);
```

**Recommendation:** Report both, acknowledge difference

---

## Continuations and Divisionals

### Problem: Gaming the System?

**Scenario:** File one application before policy, then file multiple "continuation" applications after policy

```
Apr 2015: File parent application (before MIC2025)
  ↓
Jun 2015: File continuation #1 (after MIC2025)
Aug 2015: File continuation #2 (after MIC2025)
Oct 2015: File continuation #3 (after MIC2025)
```

**This inflates post-policy count artificially!**

### How to Detect

```sql
-- Flag continuations and divisionals
SELECT
  patent_number,
  application_date,
  parent_patent_number,
  CASE
    WHEN parent_patent_number IS NOT NULL THEN 'Continuation/Divisional'
    ELSE 'Original'
  END as patent_type
FROM patents
WHERE assignee_country = 'CN'
  AND cpc_code LIKE 'H01L%'
  AND application_date >= '2015-05-08';

-- Count originals vs. continuations
SELECT
  CASE
    WHEN parent_patent_number IS NOT NULL THEN 'Continuation/Divisional'
    ELSE 'Original'
  END as patent_type,
  COUNT(*) as count
FROM patents
WHERE assignee_country = 'CN'
  AND cpc_code LIKE 'H01L%'
  AND application_date >= '2015-05-08'
GROUP BY patent_type;
```

**If 80% are continuations:**
→ **Red flag** - May be gaming metrics, not real innovation

**If <20% are continuations:**
→ Normal level, genuine innovation

---

## International Patent Family Analysis

### Checking for Genuine Innovation vs. Strategic Filing

**Question:** Are Chinese companies filing patents globally, or just in USPTO?

**Genuine innovation pattern:**
```
China files semiconductor patent in:
✓ CNIPA (China) - 2016
✓ USPTO (US) - 2016
✓ EPO (Europe) - 2016
✓ JPO (Japan) - 2016
✓ KIPO (Korea) - 2016

→ Global patent family suggests real technology
→ Company willing to pay fees in multiple jurisdictions
```

**Strategic filing pattern:**
```
China files semiconductor patent in:
✓ USPTO (US) - 2016
✗ EPO - Not filed
✗ JPO - Not filed

→ Only filing in US (key market for restrictions)
→ Possibly defensive patenting, not real innovation
```

### How to Test

```sql
-- Check if Chinese patents are part of international families
SELECT
  p.patent_number,
  p.assignee_name,
  COUNT(DISTINCT f.jurisdiction) as family_size,
  GROUP_CONCAT(DISTINCT f.jurisdiction) as jurisdictions
FROM patents p
LEFT JOIN patent_families f ON p.patent_family_id = f.family_id
WHERE p.assignee_country = 'CN'
  AND p.cpc_code LIKE 'H01L%'
  AND p.application_date >= '2015-05-08'
GROUP BY p.patent_number
HAVING family_size > 1;  -- Filed in multiple countries

-- Average family size comparison
SELECT
  assignee_country,
  AVG(family_size) as avg_family_size
FROM (
  SELECT
    p.assignee_country,
    COUNT(DISTINCT f.jurisdiction) as family_size
  FROM patents p
  LEFT JOIN patent_families f ON p.patent_family_id = f.family_id
  WHERE p.cpc_code LIKE 'H01L%'
    AND p.application_date >= '2015-05-08'
  GROUP BY p.patent_number
)
GROUP BY assignee_country;
```

**If Chinese patents have lower average family size than US/JP/KR:**
→ Possible strategic filing, not genuine innovation

---

## Revised Timeline for Causal Analysis

### Proper Attribution Windows

**Made in China 2025 published:** May 8, 2015

**Analysis periods (using application dates):**

| Period | Application Dates | Can Attribute to MIC2025? | Notes |
|--------|------------------|---------------------------|--------|
| **Pre-policy** | Before May 8, 2015 | ❌ NO | Baseline comparison |
| **Early response** | May 2015 - Dec 2016 | ⚠️ POSSIBLE | Immediate reaction or noise? |
| **Short-term** | 2017-2018 | ✅ YES | Clear policy window |
| **Medium-term** | 2019-2021 | ✅ YES | Sustained policy effect |
| **Long-term** | 2022-2025 | ✅ YES | Mature policy implementation |

### Grant Date Lag Adjustment

**If you only have grant dates, back-calculate application dates:**

```sql
-- Estimate application date from grant date
-- Using average 2.5 year lag for semiconductors

SELECT
  patent_number,
  grant_date,
  DATE_SUB(grant_date, INTERVAL 30 MONTH) as estimated_application_date,
  CASE
    WHEN DATE_SUB(grant_date, INTERVAL 30 MONTH) >= '2015-05-08'
    THEN 'Post-MIC2025'
    ELSE 'Pre-MIC2025'
  END as policy_period
FROM patents
WHERE cpc_code LIKE 'H01L%'
  AND assignee_country = 'CN';
```

**Caveat:** This is approximate. Some patents take 1 year, some take 5 years.

**Better:** Use actual application dates if available in dataset

---

## Data Requirements Checklist

**To properly analyze patent timeline causality, you need:**

- [ ] Application date (filing date) - **CRITICAL**
- [ ] Grant date (issue date) - For understanding lag
- [ ] Priority date - For foreign priority claims
- [ ] Parent patent number - To identify continuations
- [ ] Patent family ID - For international filing analysis
- [ ] CPC codes - For technology classification
- [ ] Assignee country - For geographic analysis
- [ ] Assignee name - For entity-level analysis

**Minimum for basic analysis:**
- Application date
- Grant date
- Assignee country
- Technology classification

---

## Checking Your Data

### Step 1: Determine What Dates You Have

```sql
-- Check what date fields exist
SHOW COLUMNS FROM patents LIKE '%date%';

-- Or
PRAGMA table_info(patents);

-- Look for:
-- - application_date, filing_date, app_date
-- - grant_date, issue_date, publication_date
-- - priority_date
```

### Step 2: Sample Date Values

```sql
-- Look at a few patents to understand date structure
SELECT
  patent_number,
  application_date,
  grant_date,
  priority_date,
  DATEDIFF(grant_date, application_date) as processing_days
FROM patents
WHERE assignee_country = 'CN'
  AND cpc_code LIKE 'H01L%'
LIMIT 10;

-- Calculate average processing time
SELECT
  AVG(DATEDIFF(grant_date, application_date)) / 365.25 as avg_years_to_grant,
  MIN(DATEDIFF(grant_date, application_date)) / 365.25 as min_years,
  MAX(DATEDIFF(grant_date, application_date)) / 365.25 as max_years
FROM patents
WHERE cpc_code LIKE 'H01L%';
```

### Step 3: Validate Timeline Makes Sense

```sql
-- Check for data quality issues
SELECT
  COUNT(*) as total_patents,
  SUM(CASE WHEN application_date IS NULL THEN 1 ELSE 0 END) as missing_app_date,
  SUM(CASE WHEN grant_date IS NULL THEN 1 ELSE 0 END) as missing_grant_date,
  SUM(CASE WHEN grant_date < application_date THEN 1 ELSE 0 END) as invalid_dates
FROM patents;
```

**Red flags:**
- Grant date before application date → Data error
- >50% missing application dates → Must use grant date with adjustment
- Processing time <6 months or >10 years → Outliers, investigate

---

## Proper Claim Formulation (Revised)

### ❌ WRONG (Ignores Timeline):
"Chinese semiconductor patents increased 340% following Made in China 2025 (2015-2025)"

**Problems:**
- Uses which dates? Grant or application?
- 2015 patents couldn't be influenced by May 2015 policy
- Conflates pre-policy and post-policy activity

---

### ✅ CORRECT (Timeline-Aware):
"Chinese semiconductor patent applications (filing date) increased 340% in the five years following Made in China 2025 publication (May 2015 - May 2020, application dates), compared to 50% growth globally and 42% growth in non-priority Chinese sectors. Pre-policy (2010-2015), Chinese semiconductor applications grew 12% annually; post-policy, growth accelerated to 35% annually. Using application dates (not grant dates) ensures attribution to post-policy decisions. Patents granted in 2015-2017 but applied for before May 2015 are excluded from policy-attributed counts."

**Why better:**
- ✓ Specifies application dates, not grant dates
- ✓ Excludes 2015-2017 grants that were pre-policy applications
- ✓ Compares to pre-policy baseline
- ✓ Acknowledges methodology explicitly

---

## Impact on Your "340%" Claim

**Original claim:** "Chinese semiconductor patents increased 340% following Made in China 2025"

**Potential issues:**

**Scenario 1: You used grant dates 2015-2025**
```
Patents granted 2015: Applied for ~2012-2013 (PRE-policy)
Patents granted 2016: Applied for ~2013-2014 (PRE-policy)
Patents granted 2017: Applied for ~2014-2015 (MIXED)

→ You're counting pre-policy patents as post-policy!
→ This inflates the "340%" figure artificially
```

**Scenario 2: You used application dates 2015-2025**
```
Applications filed May 2015 onward: Post-policy ✓
But still includes May-Dec 2015 (only 8 months of Year 1)

→ Comparison should be May 2015 - May 2020 vs. May 2010 - May 2015
→ Or use full years: 2016-2025 vs. 2010-2015
```

---

## Recommended Analysis Approach

### Step 1: Verify Your Date Fields

**Check:**
1. Do you have application dates in your USPTO data?
2. What % of patents have application dates vs. only grant dates?
3. What is the average lag between application and grant?

### Step 2: Re-calculate Using Application Dates

**Conservative approach (recommended):**
```sql
-- Only patents applied for AFTER MIC2025 publication
-- AND at least 6 months after (to allow for awareness/response)

SELECT COUNT(*)
FROM patents
WHERE assignee_country = 'CN'
  AND cpc_code LIKE 'H01L%'
  AND application_date >= '2015-11-08'  -- 6 months post-policy
  AND application_date <= '2025-05-08'; -- 10 years post-policy
```

### Step 3: Compare Multiple Attribution Windows

**Report results for different windows:**

| Attribution Window | Rationale | Patent Count | Growth vs. Baseline |
|-------------------|-----------|--------------|---------------------|
| Immediate (0-6 mo) | Accelerated existing work | X | Y% |
| Short-term (6-24 mo) | Quick response projects | X | Y% |
| Medium-term (2-5 yr) | New R&D programs | X | Y% |
| Long-term (5-10 yr) | Fundamental research | X | Y% |

**This shows:**
- How quickly policy impacts behavior
- Whether effect is sustained or temporary
- More nuanced than single "340%" figure

---

## Next Steps for Your Analysis

**I recommend we:**

1. **Check your USPTO data structure** - What date fields do you actually have?

2. **If you have application dates:** Re-run analysis using those instead of grant dates

3. **If you only have grant dates:** Apply 2.5-year lag adjustment and note uncertainty

4. **Calculate multiple timelines:**
   - Immediate response (0-6 months post-policy)
   - Short-term (6-24 months)
   - Medium-term (2-5 years)
   - Long-term (5-10 years)

5. **Report with appropriate caveats:**
   - Acknowledge date field used
   - Note average processing lag
   - Exclude or flag questionable attribution periods

**Would you like me to check your actual USPTO data to see what date fields you have and re-calculate properly?**

This is exactly the kind of methodological rigor that makes research credible.
