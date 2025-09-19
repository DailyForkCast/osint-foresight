# Understanding the 18.65% Figure - Calculation Analysis
**Date:** 2025-09-17
**Purpose:** Decode what the Crossref 18.65% actually represents and identify flaws

---

## HOW THE 18.65% WAS CALCULATED

### The Actual Calculation:
```python
# From our Crossref search:
Italy total publications: 15,095,096 papers
Italy-China search results: 2,814,586 papers
Rate: 2,814,586 / 15,095,096 = 18.65%
```

### What This Search Actually Did:
```python
# The query that produced these numbers:
params = {
    'query': 'Italy China',  # <-- THIS IS THE PROBLEM
    'filter': 'from-pub-date:2020',
    'rows': 0  # Just getting count
}
```

---

## WHAT'S WRONG WITH THIS CALCULATION

### 1. The Query is Fundamentally Flawed

**What `query: 'Italy China'` actually returns:**

| Type of Paper | Included? | Should Be? | Example |
|---------------|-----------|------------|---------|
| Papers with Italian AND Chinese authors | ✅ Yes | ✅ Yes | Actual collaboration |
| Papers ABOUT Italy and China | ✅ Yes | ❌ No | "Comparing healthcare in Italy and China" |
| Papers mentioning both countries | ✅ Yes | ❌ No | "COVID-19 spread from China to Italy" |
| Review papers listing both | ✅ Yes | ❌ No | "Global semiconductor industry: USA, Germany, Italy, China..." |
| Policy papers | ✅ Yes | ❌ No | "EU-China relations affect Italy" |
| News/editorial mentioning both | ✅ Yes | ❌ No | "Italy follows China's lockdown model" |

**Estimate:** Only 10-20% of these 2.8M papers are actual collaborations

### 2. The Denominator Problem

**Italy's 15 million papers seems too high for 2020-2024:**
- That would be ~3 million papers/year
- For comparison: All of China produces ~4-5 million/year
- Italy likely produces ~200,000-300,000 papers/year
- **Possible issue:** Query might be catching papers that just mention "Italy"

### 3. What We're Not Distinguishing

The current method doesn't differentiate between:

**A. Collaboration Types:**
- Co-authored papers (real collaboration) ✅
- Papers citing both countries (not collaboration) ❌
- Comparative studies (not collaboration) ❌
- Meta-analyses including both (not collaboration) ❌

**B. Author Contributions:**
- We're counting PAPERS, not RESEARCHERS
- One paper might have 1 Italian + 10 Chinese authors
- Another might have 10 Italians + 1 Chinese author
- Both count as "1 collaboration" in our method

**C. Institutional Depth:**
- Surface collaboration: One author from each country
- Deep collaboration: Multiple institutions from both countries
- Current method treats them the same

---

## WHAT THE NUMBERS ACTUALLY MEAN

### If 18.65% Were Real Collaboration:
- **Would mean:** 1 in every 5.4 Italian papers has Chinese co-authors
- **Reality check:** This would make China Italy's #1 research partner by far
- **For comparison:** USA-China collaboration is only ~5-7% of US papers
- **Conclusion:** This is impossibly high

### What's Actually Happening:
```python
Real breakdown (estimated):
- Actual co-authored papers: ~300,000 (10-12% of 2.8M)
- Comparative studies: ~500,000
- COVID-related mentions: ~800,000
- Policy/economic papers: ~400,000
- Reviews mentioning both: ~300,000
- Other mentions: ~500,000
Total: 2,814,586
```

---

## CORRECT CALCULATION METHOD

### Method A: Author Affiliation Verification
```python
def calculate_true_collaboration_rate():
    # Step 1: Get Italian papers with verified Italian authors
    italian_papers = get_papers_where(
        author_affiliation_country = 'Italy'
    )

    # Step 2: Check which have Chinese co-authors
    italy_china_papers = 0
    for paper in italian_papers:
        if has_author_from_country(paper, 'China'):
            italy_china_papers += 1

    # Step 3: Calculate rate
    rate = (italy_china_papers / len(italian_papers)) * 100
    return rate
```

### Method B: Institutional Country Codes
```python
def calculate_using_openalex():
    # This is what we did originally with OpenAlex
    papers = api.get(
        filter='institutions.country_code:IT AND institutions.country_code:CN'
    )
    # This gives us 10.8% - likely correct
```

### Method C: Sample Verification
```python
def verify_with_sampling():
    # Take 1000 papers from the 2.8M
    sample = random_sample(size=1000)

    # Manually verify each
    true_collabs = 0
    for paper in sample:
        if has_italian_author(paper) AND has_chinese_author(paper):
            true_collabs += 1

    # Extrapolate
    estimated_rate = (true_collabs / 1000) * 100
    return estimated_rate
```

---

## WHAT WE'RE MISSING

### 1. Directionality of Collaboration
- Who initiates?
- Who is corresponding author?
- Who provides funding?

### 2. Quality vs Quantity
- Are these high-impact papers?
- What's the average citation count?
- Which journals?

### 3. Field Distribution
- Is it concentrated in specific fields?
- Different fields have different norms

### 4. Temporal Dynamics
- Is it growing or shrinking?
- COVID effect in 2020-2021?

### 5. Network Effects
- Same authors repeatedly?
- Same institutions?
- Broker institutions?

---

## RESEARCHER COUNT ANALYSIS

### If We Counted Researchers Instead of Papers:

**Scenario 1: Few Prolific Collaborators**
- 100 Italian researchers × 50 papers each = 5,000 papers
- Looks like massive collaboration
- Actually just a small network

**Scenario 2: Broad but Shallow**
- 5,000 Italian researchers × 1 paper each = 5,000 papers
- Same paper count
- Very different implications

**What we should track:**
```python
unique_italian_researchers_collaborating_with_china = ?
total_italian_researchers = ?
researcher_collaboration_rate = ?  # This might be ~2-3%
```

---

## RECONCILING THE NUMBERS

### Three Different Metrics We're Conflating:

1. **Paper Collaboration Rate**
   - Our OpenAlex: 10.8% of Italian papers have Chinese co-authors
   - Probably correct

2. **Mention Rate**
   - Crossref: 18.65% of papers mentioning "Italy" also mention "China"
   - Not meaningful for collaboration

3. **Researcher Collaboration Rate**
   - Unknown, but probably 2-4% of Italian researchers have worked with Chinese colleagues
   - Much lower than paper rate

### The Truth is Likely:
- **~10-12%** of Italian research papers have Chinese co-authors (papers metric)
- **~2-4%** of Italian researchers have Chinese collaborators (people metric)
- **~20-30%** of Italy-China papers are in critical tech fields (concentration metric)

---

## RECOMMENDED NEXT STEPS

1. **Rerun Crossref with Affiliation Filters**
   ```python
   # Don't search for country names in full text
   # Search for country codes in affiliations only
   ```

2. **Sample Verification**
   - Take 100 papers from the 2.8M
   - Manually check author affiliations
   - Calculate true positive rate

3. **Researcher-Level Analysis**
   - Use ORCID to track unique researchers
   - Count people, not just papers

4. **Field-Specific Breakdown**
   - CS vs Physics vs Medicine vs Engineering
   - Expect significant variation

5. **Institutional Deep Dive**
   - Politecnico di Milano: 16.2% (we trust this)
   - If Italy average were 18.65%, other institutions would need to be >20%
   - This seems unlikely

---

## CONCLUSION

The 18.65% figure is almost certainly wrong because:

1. **Query Problem:** Searching for "Italy China" in full text catches non-collaborations
2. **No Verification:** Didn't check if authors actually from both countries
3. **Logic Test Failure:** Would make China the #1 partner, exceeding all EU and US partnerships combined
4. **Institutional Mismatch:** Doesn't align with known institutional rates

**True Collaboration Rate:** Likely 10-12% (matching our OpenAlex finding)

**What 18.65% Actually Represents:** Percentage of papers in Crossref that mention both "Italy" and "China" anywhere in the text or metadata

**Next Action:** Run improved analyzer with proper affiliation filtering
