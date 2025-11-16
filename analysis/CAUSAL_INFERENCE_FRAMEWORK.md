# Causal Inference Framework for Policy Impact Analysis
**Date:** 2025-11-09
**Issue:** How to avoid spurious correlation and establish real policy impact

---

## The Problem You Identified

**Weak Claim:** "Chinese semiconductor patents increased 340% following Made in China 2025"

**Your Valid Concern:**
- What if ALL semiconductor patents increased 340% globally during this period?
- What if Chinese patents increased 340% across ALL sectors (not just semiconductors)?
- Then the increase has nothing to do with MIC2025 specifically!

**This is a textbook spurious correlation risk.**

---

## Proper Causal Analysis Framework

### Step 1: Establish Baseline Trends

**Question 1: What happened to global semiconductor patents during the same period?**

**Data you can check (your USPTO database):**

```sql
-- Compare Chinese vs. non-Chinese semiconductor patent growth

-- Chinese semiconductor patents (2015-2025)
SELECT
    YEAR(patent_date) as year,
    COUNT(*) as chinese_semiconductor_patents
FROM uspto_patents
WHERE assignee_country = 'CN'
  AND cpc_code LIKE 'H01L%'  -- Semiconductor CPC codes
  AND patent_date BETWEEN '2015-01-01' AND '2025-12-31'
GROUP BY YEAR(patent_date)
ORDER BY year;

-- ALL semiconductor patents (2015-2025)
SELECT
    YEAR(patent_date) as year,
    COUNT(*) as total_semiconductor_patents
FROM uspto_patents
WHERE cpc_code LIKE 'H01L%'
  AND patent_date BETWEEN '2015-01-01' AND '2025-12-31'
GROUP BY YEAR(patent_date)
ORDER BY year;

-- Other major countries for comparison
SELECT
    assignee_country,
    YEAR(patent_date) as year,
    COUNT(*) as semiconductor_patents
FROM uspto_patents
WHERE cpc_code LIKE 'H01L%'
  AND patent_date BETWEEN '2015-01-01' AND '2025-12-31'
  AND assignee_country IN ('US', 'JP', 'KR', 'TW', 'DE', 'NL')
GROUP BY assignee_country, YEAR(patent_date)
ORDER BY assignee_country, year;
```

**Possible outcomes:**

**Outcome A: Global patents also increased 340%**
```
2015: 10,000 global semiconductor patents
2025: 44,000 global semiconductor patents (+340%)

China: +340%
Everyone else: +340%
```
**Conclusion:** No evidence of MIC2025 impact - just global industry growth

---

**Outcome B: Global patents grew modestly, China grew dramatically**
```
2015: 10,000 global patents (1,000 Chinese)
2025: 15,000 global patents (+50%) (4,400 Chinese, +340%)

China: +340%
Everyone else: +25%
```
**Conclusion:** China's growth significantly exceeds baseline - evidence of policy effect

---

**Outcome C: Other countries DECLINED while China grew**
```
2015: 10,000 global (1,000 Chinese, 9,000 others)
2025: 11,400 global (4,400 Chinese, 7,000 others)

China: +340%
Others: -22%
```
**Conclusion:** Strong evidence - China gaining market share, not just riding global trend

---

### Step 2: Control for Broader Chinese Patent Trends

**Question 2: Did Chinese patents increase 340% in ALL sectors, or just MIC2025 priority sectors?**

**Data check:**

```sql
-- Chinese patent growth by technology sector (2015 vs 2025)

-- MIC2025 priority sectors
WITH priority_sectors AS (
  SELECT 'semiconductors' as sector, 'H01L%' as cpc_pattern
  UNION SELECT 'AI', 'G06N%'
  UNION SELECT 'robotics', 'B25J%'
  UNION SELECT 'aerospace', 'B64%'
  UNION SELECT 'new_materials', 'C01%'
  -- ... other MIC2025 sectors
),
-- Non-priority sectors (control group)
control_sectors AS (
  SELECT 'textiles' as sector, 'D01%' as cpc_pattern
  UNION SELECT 'furniture', 'A47%'
  UNION SELECT 'agriculture', 'A01%'
  -- ... sectors NOT in MIC2025
)

-- Compare growth rates
SELECT
  sector,
  SUM(CASE WHEN YEAR(patent_date) = 2015 THEN 1 ELSE 0 END) as patents_2015,
  SUM(CASE WHEN YEAR(patent_date) = 2025 THEN 1 ELSE 0 END) as patents_2025,
  (SUM(CASE WHEN YEAR(patent_date) = 2025 THEN 1 ELSE 0 END) * 100.0 /
   SUM(CASE WHEN YEAR(patent_date) = 2015 THEN 1 ELSE 0 END)) - 100 as growth_pct
FROM uspto_patents
JOIN priority_sectors ON cpc_code LIKE cpc_pattern
WHERE assignee_country = 'CN'
GROUP BY sector

UNION ALL

SELECT
  sector,
  SUM(CASE WHEN YEAR(patent_date) = 2015 THEN 1 ELSE 0 END) as patents_2015,
  SUM(CASE WHEN YEAR(patent_date) = 2025 THEN 1 ELSE 0 END) as patents_2025,
  (SUM(CASE WHEN YEAR(patent_date) = 2025 THEN 1 ELSE 0 END) * 100.0 /
   SUM(CASE WHEN YEAR(patent_date) = 2015 THEN 1 ELSE 0 END)) - 100 as growth_pct
FROM uspto_patents
JOIN control_sectors ON cpc_code LIKE cpc_pattern
WHERE assignee_country = 'CN'
GROUP BY sector;
```

**Possible outcomes:**

**Outcome A: All Chinese sectors grew 340%**
```
MIC2025 sectors: +340%
Non-MIC2025 sectors: +340%
```
**Conclusion:** General Chinese patent growth, not MIC2025-specific

---

**Outcome B: MIC2025 sectors grew much faster**
```
MIC2025 semiconductors: +340%
MIC2025 AI: +450%
MIC2025 robotics: +280%
Average MIC2025: +356%

Non-MIC2025 textiles: +50%
Non-MIC2025 furniture: +30%
Non-MIC2025 agriculture: +45%
Average non-MIC2025: +42%
```
**Conclusion:** Strong evidence of policy targeting effect

---

### Step 3: Temporal Analysis (Difference-in-Differences)

**Question 3: Was there a CHANGE in growth rate AFTER MIC2025 published (2015)?**

**Approach: Compare pre-2015 vs. post-2015 growth**

```sql
-- Chinese semiconductor patent growth rates
-- Pre-MIC2025: 2010-2015
-- Post-MIC2025: 2015-2020

WITH pre_period AS (
  SELECT
    COUNT(*) as count_2010
  FROM uspto_patents
  WHERE assignee_country = 'CN'
    AND cpc_code LIKE 'H01L%'
    AND YEAR(patent_date) = 2010
),
mid_period AS (
  SELECT
    COUNT(*) as count_2015
  FROM uspto_patents
  WHERE assignee_country = 'CN'
    AND cpc_code LIKE 'H01L%'
    AND YEAR(patent_date) = 2015
),
post_period AS (
  SELECT
    COUNT(*) as count_2020
  FROM uspto_patents
  WHERE assignee_country = 'CN'
    AND cpc_code LIKE 'H01L%'
    AND YEAR(patent_date) = 2020
)

SELECT
  'Pre-MIC2025 (2010-2015)' as period,
  count_2010,
  count_2015,
  ((count_2015 * 100.0 / count_2010) - 100) / 5 as annual_growth_pct
FROM pre_period, mid_period

UNION ALL

SELECT
  'Post-MIC2025 (2015-2020)' as period,
  count_2015,
  count_2020,
  ((count_2020 * 100.0 / count_2015) - 100) / 5 as annual_growth_pct
FROM mid_period, post_period;
```

**Possible outcomes:**

**Outcome A: No acceleration**
```
Pre-MIC2025 (2010-2015): +30% annual growth
Post-MIC2025 (2015-2020): +28% annual growth
```
**Conclusion:** No evidence policy changed trajectory

---

**Outcome B: Clear acceleration**
```
Pre-MIC2025 (2010-2015): +12% annual growth
Post-MIC2025 (2015-2020): +35% annual growth
```
**Conclusion:** Strong evidence of policy-induced acceleration

---

### Step 4: Synthetic Control Method

**Most rigorous approach: Build counterfactual**

**Question: What WOULD have happened to Chinese semiconductor patents if MIC2025 never existed?**

**Method:**
1. Find countries similar to China pre-2015 (similar patent growth, similar economy)
2. Create weighted combination of those countries to match China's pre-2015 trend
3. Project that "synthetic China" forward 2015-2025
4. Compare actual China vs. synthetic China

**Example:**

```python
# Simplified synthetic control
# Find countries that matched China's pre-2015 semiconductor patent trajectory

pre_2015_growth = {
    'CN': [100, 115, 130, 145, 160],  # 2010-2014 indexed to 100
    'KR': [100, 108, 118, 130, 143],  # South Korea
    'TW': [100, 105, 112, 121, 131],  # Taiwan
    'IN': [100, 120, 145, 170, 200],  # India (different trajectory)
    'BR': [100, 103, 107, 110, 115],  # Brazil (different trajectory)
}

# Find best match: Korea + Taiwan combination
# Synthetic China = 0.6 * Korea + 0.4 * Taiwan
# This matches China's pre-2015 trend

# Now project 2015-2025
synthetic_china_2025 = 0.6 * korea_2025 + 0.4 * taiwan_2025
actual_china_2025 = [actual data]

# Compare
if actual_china_2025 >> synthetic_china_2025:
    # Policy likely had effect
```

**This is the GOLD STANDARD for causal inference**

---

## Proper Claim Formulation

### ❌ WEAK CLAIM (Spurious Correlation):
"Chinese semiconductor patents increased 340% following Made in China 2025"

**Problems:**
- No baseline comparison
- No control group
- Implies causation without evidence
- Could be global trend, unrelated to policy

---

### ✅ STRONG CLAIM (Causal Evidence):
"Chinese semiconductor patents increased 340% (2015-2025), compared to 50% growth in global semiconductor patents and 42% growth in non-priority Chinese sectors during the same period. Difference-in-differences analysis shows Chinese semiconductor patent growth accelerated from 12% annually pre-2015 to 35% annually post-2015, while comparable countries (South Korea, Taiwan) showed no acceleration. This pattern is consistent across all 10 Made in China 2025 priority sectors but not present in non-priority sectors, suggesting policy-driven targeted growth."

**Why stronger:**
- Baseline comparison (global growth)
- Control group (non-priority sectors)
- Temporal analysis (pre/post acceleration)
- Comparative analysis (other countries)
- Alternative explanations ruled out

---

## How to Test This With Your Data

### Analysis 1: Quick Sanity Check (30 minutes)

```sql
-- Get the actual numbers

-- 1. Chinese semiconductor patents 2015 vs 2025
SELECT
  '2015' as year,
  COUNT(*) as chinese_semiconductor_patents
FROM uspto_patents
WHERE assignee_country = 'CN'
  AND cpc_code LIKE 'H01L%'
  AND YEAR(patent_date) = 2015

UNION ALL

SELECT
  '2025' as year,
  COUNT(*) as chinese_semiconductor_patents
FROM uspto_patents
WHERE assignee_country = 'CN'
  AND cpc_code LIKE 'H01L%'
  AND YEAR(patent_date) = 2025;

-- 2. Global semiconductor patents (all countries) 2015 vs 2025
SELECT
  '2015' as year,
  COUNT(*) as total_semiconductor_patents
FROM uspto_patents
WHERE cpc_code LIKE 'H01L%'
  AND YEAR(patent_date) = 2015

UNION ALL

SELECT
  '2025' as year,
  COUNT(*) as total_semiconductor_patents
FROM uspto_patents
WHERE cpc_code LIKE 'H01L%'
  AND YEAR(patent_date) = 2025;

-- 3. Calculate China's share
SELECT
  YEAR(patent_date) as year,
  SUM(CASE WHEN assignee_country = 'CN' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as china_share_pct
FROM uspto_patents
WHERE cpc_code LIKE 'H01L%'
  AND YEAR(patent_date) IN (2015, 2025)
GROUP BY YEAR(patent_date);
```

**Decision tree:**

**If China's share INCREASED significantly:**
→ Evidence of policy effect (China gaining market share)

**If China's share STAYED SAME:**
→ No evidence of policy effect (China just riding global wave)

**If China's share DECREASED:**
→ Despite absolute growth, China losing ground to others

---

### Analysis 2: Full Causal Analysis (1 week)

**Step-by-step protocol:**

1. **Baseline trends** (1 day)
   - Global semiconductor patent trends 2010-2025
   - Major countries (US, JP, KR, TW, DE, NL) trends
   - Chinese trends across all technology sectors

2. **Control group analysis** (1 day)
   - Compare MIC2025 priority sectors vs. non-priority sectors
   - Chinese growth rates in each

3. **Temporal analysis** (1 day)
   - Pre-2015 growth rates
   - Post-2015 growth rates
   - Test for acceleration

4. **Difference-in-differences** (2 days)
   - Build statistical model
   - Test significance
   - Calculate policy effect size

5. **Alternative explanations** (1 day)
   - Could it be US-China trade war (defensive patenting)?
   - Could it be 5G/AI boom (general tech growth)?
   - Could it be patent quality decline (gaming the system)?
   - Test each alternative

6. **Report with confidence intervals** (1 day)
   - "Policy effect estimate: +200% to +280% (95% CI)"
   - "Probability policy had positive effect: 98%"

---

## Red Flags to Watch For

### 🚩 Red Flag 1: Cherry-Picked Timeframe
**Bad:** "Patents increased 340% from 2015-2025"
**Why bad:** Did you test 2014-2024? 2016-2026? Or just found the timeframe with biggest number?

**Solution:** Pre-register your analysis period BEFORE running numbers

---

### 🚩 Red Flag 2: Ignoring Patent Quality
**Problem:** China could be filing 1000 low-quality patents vs. US filing 100 high-quality patents

**Solution:** Check:
- Citation rates (are Chinese patents cited by others?)
- Grant rates (what % get approved vs. rejected?)
- Forward citations (do they lead to innovation?)
- Maintenance rates (do companies keep paying fees, or let them lapse?)

```sql
-- Check patent quality indicators
SELECT
  assignee_country,
  AVG(citation_count) as avg_citations,
  AVG(CASE WHEN status = 'granted' THEN 1 ELSE 0 END) as grant_rate
FROM uspto_patents
WHERE cpc_code LIKE 'H01L%'
  AND YEAR(patent_date) BETWEEN 2015 AND 2025
GROUP BY assignee_country;
```

**If Chinese patents have 10x more filings but 1/10th the citations:**
→ Quantity not quality (gaming the metric)

---

### 🚩 Red Flag 3: Ignoring Foreign Collaboration
**Problem:** "Chinese patent" might actually be US company with Chinese subsidiary filing

**Solution:** Check:
- Inventor locations (are inventors actually in China?)
- Co-applicants (joint Chinese-foreign patents?)
- Ultimate parent company (is "Chinese company" really US-owned?)

```sql
-- Check if patents are truly Chinese innovation
SELECT
  COUNT(*) as chinese_assignee_patents,
  SUM(CASE WHEN inventor_country = 'CN' THEN 1 ELSE 0 END) as chinese_inventor_patents,
  SUM(CASE WHEN inventor_country != 'CN' THEN 1 ELSE 0 END) as foreign_inventor_patents
FROM uspto_patents
WHERE assignee_country = 'CN'
  AND cpc_code LIKE 'H01L%'
  AND YEAR(patent_date) BETWEEN 2015 AND 2025;
```

**If 50% of "Chinese patents" have US inventors:**
→ Not pure Chinese innovation, collaborative or acquired

---

## NLP Role in Rigorous Analysis

**NLP can actually HELP you avoid spurious correlations:**

### Use Case 1: Policy Intent Extraction

**From Made in China 2025, extract:**
- SPECIFIC targets: "70% self-sufficiency in semiconductors"
- SPECIFIC technologies: "28nm, 14nm, 7nm process nodes"
- SPECIFIC companies: Which SOEs responsible?

**Then validate:**
- Did patents increase in THOSE SPECIFIC areas?
- Did THOSE SPECIFIC companies file patents?
- Or was it random Chinese companies in unrelated semiconductor areas?

**Precision test:**
```
MIC2025 targets 28nm, 14nm, 7nm nodes specifically
→ Check: Did Chinese patents in 28/14/7nm increase?
→ Or did they increase in unrelated areas (e.g., LED semiconductors)?

If increase matches policy targets precisely: Strong evidence
If increase is generic: Weak evidence
```

---

### Use Case 2: Timeline Precision

**Extract exact policy dates:**
- Made in China 2025: Published May 8, 2015
- Semiconductor fund established: September 2014
- Specific implementation guidelines: Various dates 2015-2017

**Test temporal precision:**
```
Did patent filings increase:
- Immediately after May 2015? (Quick response)
- Gradually over 2015-2020? (Slow implementation)
- Before 2015? (Suggests other cause)

Compare to:
- Other MIC2025 sectors (same timing?)
- Non-MIC2025 sectors (different timing?)
```

---

### Use Case 3: Cross-National Comparison

**NLP on Chinese policy + European policy + US policy:**

**Question:** Did Europe/US respond with counter-policies?

**If yes:**
```
2015: MIC2025 published (China offensive strategy)
2018: US CHIPS Act discussions begin (defensive response)
2020: European Chips Act proposed (defensive response)
2022: US CHIPS Act passed
2023: European Chips Act passed

→ Test: Did US/EU patents ALSO increase 2022-2025?
→ If yes: Global policy race, not just China
→ If no: China unique
```

---

## Recommendation for Your Project

### DO THIS FIRST (Before Making Claims):

**Run the sanity check queries I provided above.**

**Scenario A: Global patents also increased ~300%+**
→ **STOP.** Do NOT claim policy effect.
→ Instead claim: "Global semiconductor patent surge 2015-2025, with China participating proportionally"

**Scenario B: China grew 340%, global grew 50%, China's market share increased**
→ **PROCEED** with full causal analysis
→ This is evidence (but not proof yet) of policy effect

**Scenario C: China grew 340%, but so did Korea, Taiwan, India**
→ **INVESTIGATE** regional trend (Asia-Pacific semiconductor boom?)
→ Not China-specific

---

### THEN: Add Nuance to Claims

**Instead of:**
"Made in China 2025 caused 340% increase in semiconductor patents"

**Say:**
"Following Made in China 2025 publication, Chinese semiconductor patents increased 340% (2015-2025), outpacing global semiconductor patent growth of [X]% during the same period. This acceleration was specific to Made in China 2025 priority sectors and not observed in non-priority sectors, suggesting policy-targeted growth. However, [list alternative explanations: trade war defensive patenting, 5G boom, general Chinese R&D expansion] may also contribute."

**Then in footnote:**
"Causal attribution requires additional analysis including difference-in-differences estimation and synthetic control methods. See Appendix A for full methodology."

---

## Bottom Line

**You're absolutely right to question the claim.**

**The 340% figure is MEANINGLESS without context:**
- What happened globally?
- What happened in other Chinese sectors?
- What happened before vs. after policy?
- What about patent quality, not just quantity?

**Your USPTO database can answer all these questions.**

**Before making ANY causal claims about policy effects, run the validation queries to rule out spurious correlation.**

**This is EXACTLY the kind of rigor that makes your project credible.**
