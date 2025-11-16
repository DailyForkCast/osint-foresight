# Sources Tested Analysis - Europe-China Collection

## Date
2025-10-15

## Configuration Overview

**Total sources configured:** 27 sources across 5 buckets

### Bucket Breakdown (Configured)
- **CHINA_SOURCES:** 5 sources (Party-State journals)
- **THINK_TANKS:** 9 sources (Chinese think tanks)
- **ACADEMIA:** 6 sources (University centers)
- **ARCHIVED_MEDIA:** 2 sources (Media archives)
- **OPEN_DATA:** 5 sources (Scholarly datasets)

---

## Test Run Results

**Total sources actually tested:** 10 sources (2 per bucket)

### Sources Tested by Bucket

#### 1. CHINA_SOURCES (2 of 5 tested)
**Tested:**
1. **qiushi_europe** - Qiushi (求是)
   - URL: `http://www.qstheory.cn`
   - Result: ❌ No article links found
   - Keywords: 欧洲, 欧盟, Europe, Arctic, etc.

2. **peoples_daily_europe** - People's Daily (人民日报)
   - URL: `http://paper.people.com.cn`
   - Result: ❌ No article links found
   - Keywords: 欧洲, Europe, 中欧, EU, Arctic, etc.

**Not tested:** xinhua_reference, study_times, pla_daily

---

#### 2. THINK_TANKS (2 of 9 tested)
**Tested:**
1. **ciis** - China Institute of International Studies (中国国际问题研究院)
   - URL: `http://www.ciis.org.cn`
   - Result: ✅ **SUCCESS**
   - Article links found: **10**
   - Documents extracted: **2**
   - Topics: China-Europe relations, US Indo-Pacific strategy
   - Keywords matched: 欧洲, 中欧关系

2. **cicir** - China Institutes of Contemporary International Relations (中国现代国际关系研究院)
   - URL: `http://www.cicir.ac.cn`
   - Result: ❌ No article links found (implied from log)
   - Keywords: 欧洲, Europe, EU, Arctic, technology, security

**Not tested:** cass_europe, drc, cas_thinktank, ams, ndu_inss, ciiss, cac_cyber

---

#### 3. ACADEMIA (2 of 6 tested)
**Tested:**
1. **tsinghua_cistp** - Tsinghua Center for Industrial & Strategic Technology Policy
   - URL: `http://www.sppm.tsinghua.edu.cn`
   - Result: ❌ No article links found
   - Keywords: 欧洲, Europe, S&T policy, innovation, industry

2. **fudan_cees** - Fudan Center for European Studies
   - URL: `http://www.sirpa.fudan.edu.cn`
   - Result: ❌ No article links found
   - Keywords: 欧洲, Europe, EU, China-Europe relations

**Not tested:** pku_iiss, siis, renmin_rdcy, tongji_eu_center

---

#### 4. ARCHIVED_MEDIA (2 of 2 tested) ✓ All tested
**Tested:**
1. **global_times_europe** - Global Times Europe Coverage
   - URL: `http://www.globaltimes.cn`
   - Result: ❌ No article links found (or no keyword matches)
   - Language: English
   - Keywords: Europe, 欧洲, EU, China-Europe, technology

2. **china_daily_europe** - China Daily Europe News
   - URL: `http://www.chinadaily.com.cn/world/europe`
   - Result: ❌ No article links found (or no keyword matches)
   - Language: English
   - Keywords: Europe, 欧洲, EU, China-Europe

**Not tested:** None (all tested)

---

#### 5. OPEN_DATA (2 of 5 tested)
**Tested:**
1. **openalex_eu_china** - OpenAlex Europe-China S&T Collaborations
   - API: `https://api.openalex.org/works`
   - Result: ❌ **ERROR** - 'original_url' (config issue)
   - Note: API sources don't have homepage URLs

2. **crossref_eu_china** - Crossref Europe-China Publications
   - API: `https://api.crossref.org/works`
   - Result: ❌ **ERROR** - 'original_url' (config issue)
   - Note: API sources don't have homepage URLs

**Not tested:** openaire_eu_china, core_eu_china, zenodo_eu_china

---

## Success Rate Analysis

### Overall Statistics
- **Sources configured:** 27
- **Sources tested:** 10 (37%)
- **Successful extractions:** 1 (10% of tested, 4% of configured)
- **No article links found:** 7 (70% of tested)
- **Configuration errors:** 2 (20% of tested)

### By Source Type
| Bucket | Configured | Tested | Success | No Links | Errors |
|--------|-----------|--------|---------|----------|--------|
| CHINA_SOURCES | 5 | 2 | 0 | 2 | 0 |
| THINK_TANKS | 9 | 2 | 1 | 1 | 0 |
| ACADEMIA | 6 | 2 | 0 | 2 | 0 |
| ARCHIVED_MEDIA | 2 | 2 | 0 | 2 | 0 |
| OPEN_DATA | 5 | 2 | 0 | 0 | 2 |
| **TOTALS** | **27** | **10** | **1** | **7** | **2** |

---

## Why Only 10 Sources Were Tested?

The test run appears to have limited processing to **2 sources per bucket** rather than all configured sources. This could be:
1. **Test mode setting** - Limiting sources during development
2. **Rate limiting** - Conservative approach during initial testing
3. **Time limit** - Quick validation run
4. **Configuration parameter** - `max_items_per_source: 1000` or similar

**Evidence:** The report summary shows exactly 2 sources processed per bucket:
```json
"CHINA_SOURCES": {"sources_processed": 2, ...}
"THINK_TANKS": {"sources_processed": 2, ...}
"ACADEMIA": {"sources_processed": 2, ...}
"ARCHIVED_MEDIA": {"sources_processed": 2, ...}
"OPEN_DATA": {"sources_processed": 2, ...}
```

---

## Analysis of "No Article Links Found"

### Possible Reasons for 7 Failed Sources:

1. **Same relative path issue as CIIS** (likely for Chinese sources)
   - qiushi_europe, peoples_daily_europe, cicir may use `./` paths
   - Fix may need verification on these sources

2. **Homepage URL mismatch**
   - Config may have wrong homepage URL for the source
   - Example: Tsinghua CISTP homepage may not be `www.sppm.tsinghua.edu.cn` root

3. **Different site structure**
   - Some sources may not have article links on homepage
   - May need section URLs instead of homepage

4. **Archive availability**
   - Wayback Machine may not have snapshots for these URLs
   - Need to verify archive coverage

5. **Article pattern mismatch**
   - Site may use URL patterns not in our detection list
   - Current patterns: `/article/`, `/research/`, `/xwdt/`, `/yjcg/`, etc.

6. **Language/keyword filtering**
   - Links may exist but not match article patterns
   - May need to expand pattern list for each source

---

## Detailed Look at CIIS Success

**Why CIIS succeeded:**
1. ✓ Homepage had Wayback snapshot (2025-01-02)
2. ✓ Relative path bug was fixed (`./yjcg/sspl/` → `http://www.ciis.org.cn/yjcg/sspl/`)
3. ✓ Article patterns matched (`/xwdt/`, `/yjcg/`, `/sspl/`, `/zzybg/`)
4. ✓ Articles had keyword matches (欧洲, 中欧关系)
5. ✓ Archive snapshots existed for article URLs

**10 article links found:**
- `/xwdt/` - News articles (3 links)
- `/yjcg/sspl/` - Current Affairs Commentary (2 links)
- `/yjcg/zzybg/` - Publications (2 links)
- `/yjcg/yjkt/` - Research section (1 link)
- `/yjcg/gjwtyjsspl/` - International Affairs (1 link)
- Mixed date patterns - `/202412/` (1 link)

**2 documents saved:**
- Both matched Europe-related keywords
- High-quality strategic analysis content
- Proper provenance tracking with SHA256 hashes

---

## Recommendations for Next Testing

### 1. Test Remaining High-Priority Sources
**THINK_TANKS (not yet tested):**
- cass_europe - CASS Institute of European Studies (HIGH priority)
- cas_thinktank - CAS Think Tank (HIGH priority)

**ACADEMIA (not yet tested):**
- pku_iiss - PKU Institute of International & Strategic Studies (HIGH priority)
- siis - Shanghai Institutes for International Studies (HIGH priority)

### 2. Investigate Failed Sources
For the 7 sources with "No article links found":
- Check if they also use `./` relative paths (likely for Chinese sources)
- Verify homepage URLs are correct
- Check Wayback Machine availability manually
- Expand article pattern matching if needed

### 3. Fix OPEN_DATA Errors
- API sources (OpenAlex, Crossref) need different handling
- They don't have `original_url` - use `api_endpoint` instead
- Requires separate API collection logic, not HTML scraping

### 4. Full Production Run
Once fixes are verified:
- Remove 2-sources-per-bucket limit
- Process all 27 configured sources
- Expected result: More sources should succeed with relative path fix

---

## Key Findings

1. **Relative path fix works** - CIIS went from 0 → 10 article links
2. **Similar pattern likely** - Other Chinese sources may have same issue
3. **Limited test scope** - Only 37% of sources tested (10 of 27)
4. **High failure rate** - 70% of tested sources found no links (7 of 10)
5. **Quality over quantity** - The 2 documents extracted are high-quality strategic analysis
6. **Safety maintained** - 100% archive-only access, zero live .cn access

---

## Next Steps

1. **Investigate failed Chinese sources** - Check if qiushi, peoples_daily, cicir use `./` paths
2. **Verify homepage URLs** - Ensure config has correct homepage for each source
3. **Expand article patterns** - Add source-specific URL patterns if needed
4. **Test remaining high-priority sources** - CASS, CAS, PKU, SIIS
5. **Fix OPEN_DATA configuration** - Implement proper API handling
6. **Run full collection** - Test all 27 sources after fixes
