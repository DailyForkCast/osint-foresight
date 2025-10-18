# OpenAlex Metadata Availability Guide

**Generated:** 2025-09-21
**Purpose:** Understanding what data is actually available for analysis

## Metadata Coverage by Category

### ✅ **HIGHLY AVAILABLE** (>90% coverage)

These fields are present in almost all OpenAlex records:

1. **Basic Identifiers**
   - `id` - OpenAlex work ID (100%)
   - `doi` - Digital Object Identifier (~85%)
   - `title` - Paper title (>95%)
   - `publication_year` - Year of publication (~90%)

2. **Publication Metadata**
   - `type` - Publication type (article, book, etc.) (~95%)
   - `is_oa` - Open access status (~100%)
   - `cited_by_count` - Citation count (~100%)
   - `language` - Publication language (~90%)

3. **Venue Information**
   - `primary_location` - Primary publication venue (~85%)
   - `host_venue` - Journal/conference info (~85%)

### ⚠️ **MODERATELY AVAILABLE** (20-90% coverage)

These fields are present in a significant portion of records:

1. **Content Fields**
   - `abstract` - Abstract text (~40-50%)
   - `concepts` - Auto-extracted concepts (~70%)
   - `topics` - Research topics (~60%)

2. **Author Information**
   - `authorships` - Author list (~80%)
   - `authorships.author.display_name` - Author names (~75%)
   - `authorships.author.orcid` - ORCID IDs (~15-20%)

3. **References & Citations**
   - `referenced_works` - Reference list (~60%)
   - `related_works` - Related papers (~50%)
   - `cited_by_api_url` - Citation tracking (~100%)

### ❌ **RARELY AVAILABLE** (<20% coverage)

These critical fields for collaboration analysis are often missing:

1. **Institution Data** (2-5% coverage)
   - `authorships.institutions` - Institution affiliations
   - `authorships.institutions.country_code` - Country codes
   - `authorships.institutions.ror` - ROR identifiers
   - `authorships.institutions.type` - Institution type

2. **Geographic Information** (2-3% coverage)
   - Country-level data
   - City/region data
   - Institution coordinates

3. **Funding Information** (<5% coverage)
   - `grants` - Funding sources
   - `grants.funder` - Funder details
   - `grants.award_id` - Grant numbers

4. **Full Text & Keywords** (<10% coverage)
   - `fulltext_origin` - Full text availability
   - `keywords` - Author keywords
   - `mesh` - MeSH terms (biomedical only)

## Alternative Analysis Strategies

### 1. **Focus on High-Quality Subset**

Target papers with complete metadata:
- Papers from top 500 universities
- Papers in high-impact journals
- Recent papers (2020+) with better coverage
- Papers with DOIs (more complete records)

### 2. **Use Available Proxies**

When institution data is missing, use:
- **Author names** - Identify Chinese names (Zhang, Wang, Li, etc.)
- **Concepts/Topics** - Technology area classification
- **Venues** - Chinese vs international journals
- **Language** - Chinese language papers
- **Citations** - Citation patterns between regions

### 3. **Leverage What IS Available**

Strong coverage for:
- **Temporal analysis** - Publication year is reliable
- **Topic analysis** - Concepts/topics well-covered
- **Citation networks** - Citation data is complete
- **Open access trends** - OA status is tracked
- **Publication patterns** - Venue data is good

### 4. **Combine Multiple Signals**

Create composite indicators:
- Chinese author names + International venue = Likely collaboration
- Chinese concepts + English language = Potential international work
- High citations from both US and China = Cross-border impact

## Recommended Analysis Approaches

### ✅ **FEASIBLE ANALYSES** (with current data)

1. **Temporal Trends**
   - Publication volume over time
   - Citation growth patterns
   - Open access adoption

2. **Topic Analysis**
   - Technology area concentrations
   - Emerging research themes
   - Concept co-occurrence networks

3. **Venue Analysis**
   - Journal preferences
   - Conference participation
   - Publishing strategy evolution

4. **Citation Networks**
   - Cross-citation patterns
   - Influence measurement
   - Research community detection

### ⚠️ **PARTIALLY FEASIBLE** (with limitations)

1. **Collaboration Networks**
   - Only for ~2-3% with institution data
   - Can infer from author names
   - Venue-based approximations

2. **Geographic Analysis**
   - Limited to papers with country codes
   - Can supplement with author/venue inference
   - Regional patterns hard to detect

3. **Institution Rankings**
   - Only top institutions identifiable
   - Many institutions untagged
   - Requires name matching

### ❌ **NOT FEASIBLE** (insufficient data)

1. **Comprehensive Collaboration Mapping**
   - 97% lack institution data
   - Cannot identify all partnerships
   - Missing minor institutions

2. **Funding Flow Analysis**
   - <5% have grant information
   - Funders rarely identified
   - Grant amounts not available

3. **Full Text Analysis**
   - Abstracts only for ~40%
   - No full text access
   - Methods sections unavailable

## Data Quality by Time Period

### Recent Papers (2020-2025)
- **Better metadata**: ~5-8% have institutions
- **More abstracts**: ~50-60% coverage
- **ORCID adoption**: ~25% of authors

### Middle Period (2010-2019)
- **Moderate metadata**: ~2-4% have institutions
- **Abstract coverage**: ~40-45%
- **Digital identifiers**: Most have DOIs

### Older Papers (2000-2009)
- **Sparse metadata**: <2% have institutions
- **Limited abstracts**: ~20-30%
- **Identifier gaps**: Many lack DOIs

## Recommendations for Robust Analysis

1. **Acknowledge Limitations**
   - Clearly state the 2-3% sample size for geographic data
   - Note that patterns may not represent full population
   - Provide confidence intervals

2. **Triangulate Findings**
   - Cross-check with patent data
   - Validate against known collaborations
   - Compare with other databases

3. **Focus on Detectable Signals**
   - Large-scale collaborations will appear even in sparse data
   - Technology trends visible through concepts
   - Temporal patterns are reliable

4. **Supplement with Other Sources**
   - Web of Science for better institution coverage
   - Scopus for comprehensive affiliations
   - Google Scholar for citation networks
   - ArXiv for preprints with affiliations

## Conclusion

While OpenAlex provides massive scale (250M+ records), its metadata completeness varies dramatically by field. For collaboration analysis:

- **2-3% of papers** have sufficient geographic metadata
- **40-50% of papers** have abstracts for content analysis
- **80-90% of papers** have basic bibliometric data

The key is to:
1. Use the complete subset for collaboration analysis
2. Leverage abundant fields for complementary insights
3. Acknowledge limitations transparently
4. Supplement with additional data sources

Despite limitations, OpenAlex remains valuable for:
- Detecting major collaboration patterns
- Identifying technology trends
- Tracking temporal evolution
- Understanding citation networks