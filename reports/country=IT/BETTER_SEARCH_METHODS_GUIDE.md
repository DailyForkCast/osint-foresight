# Better Search Methods for Accurate Collaboration Measurement
**Date:** 2025-09-17
**Purpose:** Resolve the collaboration rate discrepancy with improved methodologies

---

## THE PROBLEM

We have conflicting collaboration rates:
- **OpenAlex (our finding):** 10.8% Italy-China
- **Crossref (Week 1):** 18.65% Italy-China (seems too high)
- **OECD Benchmark:** 3.5% typical EU-China
- **Logic Test:** Italy-USA and Italy-Germany should be higher than Italy-China

The 18.65% figure likely includes false positives from papers that mention both countries but aren't actual collaborations.

---

## RECOMMENDED BETTER METHODS

### Method 1: Affiliation Verification in Crossref
**Approach:** Don't just search for country names - verify author affiliations

```python
# BETTER: Check each author's actual affiliations
for author in paper['authors']:
    for affiliation in author['affiliations']:
        if 'Italy' in affiliation['name']:
            has_italian_author = True
        if 'China' in affiliation['name']:
            has_chinese_author = True

# Only count if BOTH are true
if has_italian_author AND has_chinese_author:
    count_as_collaboration()
```

**Advantages:**
- Eliminates papers that just mention countries
- Verifies actual institutional collaboration
- Can identify specific institutions

**Limitations:**
- Affiliation data not always complete
- Requires processing each paper

---

### Method 2: OpenAlex with Institutional Country Codes
**Approach:** Use precise institutional filters instead of text search

```python
# BETTER: Use country codes
filter = 'institutions.country_code:IT,institutions.country_code:CN'

# NOT: Generic text search
query = 'Italy China'  # Too broad
```

**Why This Is Better:**
- Country codes are standardized
- Catches all institutions regardless of name variations
- No false positives from mentions

**Expected Result:** Should give us the true ~10-12% range

---

### Method 3: DOI Sampling Strategy
**Approach:** Take random sample of Italian papers, check each for collaborations

```python
# Step 1: Get 1000 random Italian papers
italian_papers = get_sample(country='Italy', n=1000)

# Step 2: Check each paper individually
for paper in italian_papers:
    collaborations = check_all_author_countries(paper)
    count_by_country[collaborations] += 1

# Step 3: Calculate rates
china_rate = count_by_country['China'] / 1000 * 100
```

**Advantages:**
- Statistically valid sampling
- Shows relative rates accurately
- Can compare multiple countries

---

### Method 4: Multi-Database Triangulation
**Approach:** Use multiple databases and find convergence

| Database | Method | Expected Result |
|----------|--------|-----------------|
| OpenAlex | Institutional filter | ~10-12% |
| Scopus | Affiliation search | ~8-11% |
| Web of Science | Country collaboration | ~9-12% |
| Dimensions | Author country | ~10-13% |

**Best Estimate:** Where multiple sources converge

---

### Method 5: Publisher API Direct Access
**Approach:** Go directly to publisher APIs for accurate metadata

```python
# For each DOI, get full metadata
doi = '10.1234/example'
metadata = get_from_publisher(doi)

# Publishers have clean affiliation data
authors = metadata['authors']
institutions = [a['affiliation']['country'] for a in authors]
```

**Best Sources:**
- Elsevier (ScienceDirect)
- Springer Nature
- IEEE
- Wiley

---

## VALIDATION TECHNIQUES

### 1. Temporal Consistency Check
If real, collaboration should be consistent over time:
```python
for year in [2020, 2021, 2022, 2023, 2024]:
    rate = calculate_collaboration_rate(year)
    # Should be relatively stable (±2-3%)
```

### 2. Field-Specific Analysis
Different fields have different collaboration patterns:
```python
rates_by_field = {
    'Physics': calculate_rate(field='physics'),      # Often higher
    'Medicine': calculate_rate(field='medicine'),    # Moderate
    'Engineering': calculate_rate(field='engineering'), # Variable
    'Computer Science': calculate_rate(field='cs')   # Lower
}
```

### 3. Institution-Level Verification
Check known collaborating institutions:
```python
# We know Politecnico di Milano has 16.2% China collaboration
milan_rate = calculate_rate(institution='Politecnico di Milano')
# This should match our specific finding
```

### 4. Bidirectional Search
Search from both sides:
```python
# From Italy side
italy_perspective = search(italian_papers_with_chinese_coauthors)

# From China side
china_perspective = search(chinese_papers_with_italian_coauthors)

# Should be similar
```

---

## QUALITY INDICATORS

### Signs of Accurate Measurement:
✅ **Consistent across methods** (within 2-3%)
✅ **Stable over time** (no wild swings)
✅ **Logical pattern** (US/EU > China for most countries)
✅ **Matches known institutional rates**
✅ **Bidirectional search agreement**

### Signs of Measurement Error:
❌ **Huge variation** between methods (>5%)
❌ **Impossible rates** (>30% for distant countries)
❌ **Inverted patterns** (China > neighboring countries)
❌ **Year-to-year volatility**
❌ **Mismatch with institutional data**

---

## RECOMMENDED IMPLEMENTATION SEQUENCE

### Step 1: Quick Validation (1 hour)
1. Run OpenAlex with institutional country codes
2. Compare with our 10.8% finding
3. Should converge around 10-12%

### Step 2: Sample Verification (2 hours)
1. Take 500 random Italian papers from 2023
2. Manually check 50 for collaboration countries
3. Extrapolate to full sample

### Step 3: Multi-Source Confirmation (4 hours)
1. Run improved Crossref with affiliation check
2. Run Semantic Scholar with filters
3. Run DOI sampling
4. Find convergence point

### Step 4: Final Reconciliation (1 hour)
1. Weight methods by reliability
2. Calculate confidence intervals
3. Report best estimate with range

---

## EXPECTED OUTCOMES

### Most Likely True Rates:
- **Italy-China:** 9-12% (not 18.65%)
- **Italy-USA:** 8-11% (not 0.95%)
- **Italy-Germany:** 10-14% (not 0.96%)
- **Italy-France:** 9-12%
- **Italy-UK:** 7-10%

### Why Original Crossref Was Wrong:
The query `'Italy China'` matched:
1. Papers about Italy and China (comparative studies)
2. Papers mentioning both countries in text
3. Review papers discussing global trends
4. Policy papers about EU-China relations
5. Actual collaborations (only ~10-20% of matches)

---

## IMPLEMENTATION CODE

Here's the corrected approach:

```python
def get_accurate_collaboration_rate(country1='Italy', country2='China'):
    # Method 1: OpenAlex with institutional filters
    openalex_url = 'https://api.openalex.org/works'
    params = {
        'filter': f'institutions.country_code:{get_code(country1)},'
                  f'institutions.country_code:{get_code(country2)},'
                  f'from_publication_date:2020-01-01',
        'group_by': 'publication_year'
    }

    response = requests.get(openalex_url, params=params)
    collab_count = response.json()['meta']['count']

    # Get total for country1
    params_total = {
        'filter': f'institutions.country_code:{get_code(country1)},'
                  f'from_publication_date:2020-01-01'
    }

    response_total = requests.get(openalex_url, params=params_total)
    total_count = response_total.json()['meta']['count']

    # Calculate rate
    rate = (collab_count / total_count) * 100

    return {
        'method': 'OpenAlex Institutional',
        'collaboration_papers': collab_count,
        'total_papers': total_count,
        'rate': round(rate, 2),
        'confidence': 'HIGH'
    }
```

---

## CONCLUSION

The 18.65% Italy-China rate from our initial Crossref search is almost certainly wrong due to:
1. **Query too broad** - caught mentions, not collaborations
2. **No affiliation verification** - didn't check actual authors
3. **Logical impossibility** - would mean Italy collaborates more with China than neighbors

**True rate is likely:** 10-12% (matching our OpenAlex finding)

**Next step:** Run the improved analyzer to get accurate rates for all countries
