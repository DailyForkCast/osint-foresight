# UN Comtrade Data Availability Issue

**Date**: November 1, 2025
**Status**: Phase 1 Collection Running - Zero Data Retrieved

## Issue Summary

UN Comtrade API is accessible and responding correctly (HTTP 200), but returning "No data" (HTTP 404) for all technology trade queries tested.

## API Endpoint Tested

```
https://comtradeapi.un.org/data/v1/get/C/A/HS/{year}/{reporter}/{partner}/{commodity_code}
```

## Test Results

All queries across multiple configurations returned HTTP 404 "No data":

### Sample Queries (All Failed)
1. **China → US: Processors/CPUs (2024)**
   - URL: `https://comtradeapi.un.org/data/v1/get/C/A/HS/2024/CN/US/854231`
   - Result: HTTP 404 - No data

2. **US → China: Processors/CPUs (2024)**
   - URL: `https://comtradeapi.un.org/data/v1/get/C/A/HS/2024/US/CN/854231`
   - Result: HTTP 404 - No data

3. **China → Germany: 5G Equipment (2023)**
   - URL: `https://comtradeapi.un.org/data/v1/get/C/A/HS/2023/CN/DE/851762`
   - Result: HTTP 404 - No data

4. **Netherlands → China: Semiconductor Equipment (2023)**
   - URL: `https://comtradeapi.un.org/data/v1/get/C/A/HS/2023/NL/CN/901380`
   - Result: HTTP 404 - No data

5. **China → US: Lithium-ion Batteries (2024)**
   - URL: `https://comtradeapi.un.org/data/v1/get/C/A/HS/2024/CN/US/850760`
   - Result: HTTP 404 - No data

## Phase 1 Collection Status

**Currently Running**:
- Technology: 19 HS codes
- Years: 2022, 2023, 2024
- Country pairs: 10 (CN-US, US-CN, CN-DE, DE-CN, CN-JP, JP-CN, CN-KR, KR-CN, CN-NL, NL-CN)
- Total requests: 570
- Estimated time: 6-8 hours
- **Results so far**: 0 records (all "No data")

## Possible Causes

### 1. **Free Tier Limitations**
UN Comtrade may restrict:
- Detailed commodity codes (6-digit HS codes) to premium subscribers
- Recent years (2023-2024 data) to premium subscribers
- Bilateral trade pairs
- Query volume/frequency

### 2. **API Access Level**
The free/public API may only provide:
- Aggregated data (total trade, not by commodity)
- Older historical data (pre-2020)
- Limited country coverage
- Summary statistics only

### 3. **Data Reporting Lag**
- 2024 data may not yet be available (countries report with delay)
- 2023 data may be incomplete
- Specific HS codes may not be reported by all countries

### 4. **API Version/Endpoint**
- May be using wrong API version (v1 vs v2)
- Bulk download API may be separate from query API
- Different endpoint for premium data

## Recommendations

### Short-term (Week 1)
1. ✅ Let Phase 1 collection complete to confirm zero data across all 570 queries
2. Check if any historical data (2020-2022) is available
3. Test aggregated queries (total trade, not commodity-specific)

### Medium-term (Week 2-3)
4. **Investigate UN Comtrade subscription tiers**
   - Free tier capabilities: https://comtradeapi.un.org/
   - Premium tier pricing and features
   - Academic/research access programs

5. **Alternative: Bulk Download**
   - UN Comtrade provides CSV bulk downloads
   - May have more data than API
   - Check: https://comtradeplus.un.org/

6. **Alternative: Eurostat COMEXT**
   - EU trade data (more detailed for EU countries)
   - Already explored: F:/OSINT_Data/Trade_Facilities/eurostat_comext_bulk/
   - Status: Downloaded bulk files (7z archives)

### Long-term (Month 2+)
7. **Premium Subscription Evaluation**
   - If critical for analysis, evaluate cost vs. value
   - Compare with alternative sources (national customs agencies)

8. **National Sources**
   - US: USITC DataWeb (free, detailed)
   - China: General Administration of Customs (limited English access)
   - EU: Eurostat (comprehensive, free)
   - Japan: Trade Statistics of Japan (free)

## Current Workaround

**Using Eurostat COMEXT instead**:
- Location: `F:/OSINT_Data/Trade_Facilities/eurostat_comext_bulk/`
- Coverage: All EU27 trade with China
- Format: 7z compressed CSV files
- Status: Downloaded, needs extraction and processing

## Action Items

- [ ] Complete Phase 1 collection (confirm zero data)
- [ ] Document final results
- [ ] Investigate UN Comtrade subscription requirements
- [ ] Process Eurostat COMEXT bulk files as alternative
- [ ] Test US USITC DataWeb for US-China bilateral trade

## References

- UN Comtrade API: https://comtradeapi.un.org/
- UN Comtrade Plus (new interface): https://comtradeplus.un.org/
- Eurostat COMEXT: https://ec.europa.eu/eurostat/web/international-trade-in-goods/data/focus-on-comext
- USITC DataWeb: https://dataweb.usitc.gov/

---

**Last Updated**: November 1, 2025, 21:57 UTC
**Phase 1 Collection**: Running in background (Bash ID: 8edcda)
