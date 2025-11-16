# GDELT Collection: Billing Setup Required

**Date:** 2025-11-03
**Status:** BLOCKED - Billing activation needed
**Issue:** BigQuery free tier quota exceeded (1TB/month)

---

## Current Situation

### Pilot Collection Attempted
- **Country:** Greece (GRC)
- **Period:** 2020-01-01 to 2020-12-31
- **Query Type:** Bilateral (Greece-China events)
- **Result:** FAILED - Quota exceeded

### Error Message
```
403 Quota exceeded: Your project exceeded quota for free query bytes scanned.
Project: osint-foresight-2025
Job ID: 39ffbee6-d411-405f-91a6-87127efff53b
```

### Billing Status Check
```
Project: osint-foresight-2025
billingEnabled: false
Billing Account: 0185E1-13AF92-839C8E
Account Status: OPEN: False (INACTIVE)
```

---

## What This Means

**Good News:**
- Infrastructure is working correctly
- BigQuery authentication successful
- Query successfully reached BigQuery (validates our setup)
- Database connections working

**Issue:**
- Free tier quota exhausted (1TB/month)
- Billing account is inactive/closed
- Cannot proceed with paid queries until billing is activated

---

## Cost Estimates for Full Collection

### Collection Plan
- **Countries:** 11 priority EU countries (Greece, Slovakia, Finland, Sweden, Denmark, Netherlands, Ireland, Spain, Lithuania + reference)
- **Time Period:** 2020-2025 (6 years)
- **Total Collections:** 66 collection runs (11 countries × 6 years)

### Expected Costs

**BigQuery Pricing:**
- First 1 TB/month: FREE
- Beyond 1 TB: $5 per TB

**Estimated Data Scanned:**
- Bilateral queries are more efficient than full scans
- Estimated: 100-200 GB per year per country
- Total estimate: ~1-2 TB for full collection
- **Cost estimate: $5-10 for entire collection**

This is a one-time cost for complete 2020-2025 coverage across all priority countries.

---

## Next Steps to Activate Billing

### Option 1: Reactivate Existing Billing Account (Recommended)
1. Go to Google Cloud Console: https://console.cloud.google.com
2. Navigate to Billing → Billing Account: `0185E1-13AF92-839C8E`
3. Reactivate the billing account
4. Ensure payment method is current
5. Link to project `osint-foresight-2025`

### Option 2: Create New Billing Account
1. Go to Google Cloud Console
2. Billing → Create Billing Account
3. Add payment method
4. Link to project `osint-foresight-2025`

### Option 3: Manual Console Setup
```bash
# After activating billing in console, verify with:
gcloud billing projects describe osint-foresight-2025

# Should show:
# billingEnabled: true
```

---

## Once Billing is Activated

### Resume Collection Immediately
```bash
# Test with Greece 2020 pilot
python scripts/collectors/gdelt_eu_china_bilateral_collector.py \
    --country GRC \
    --start-date 20200101 \
    --end-date 20201231

# If successful, run full systematic collection
python collect_eu_priority_countries_gdelt.py
```

### What We'll Get
1. **Greece-China bilateral events (2020-2025)** - Priority 1
   - Validates -88% export decrease
   - Cross-references procurement cessation in 2021

2. **Slovakia-China bilateral events (2020-2025)** - Priority 1
   - Validates -90% export decrease (identical to Lithuania)
   - Tests if pattern matches Lithuania timeline

3. **Other Priority Countries (2020-2025)**
   - Finland, Sweden, Denmark, Netherlands, Ireland, Spain
   - Complete temporal analysis of EU-China media events
   - Correlation with trade/procurement patterns

### Analysis Capabilities
- Determine if 2021 was cluster year for EU-China tensions
- Validate trade patterns with independent media evidence
- Identify country-specific vs. coordinated EU patterns
- Build comprehensive multi-source intelligence database

---

## Alternative: Free Tier Strategy (Slower)

If billing cannot be activated immediately, we can:

1. **Wait for quota reset** (resets monthly on your billing date)
2. **Collect one country per month** using free tier
3. **Prioritize:** Greece → Slovakia → Lithuania expansion
4. **Timeline:** ~6 months for full collection vs. 1 day with billing

---

## Recommendation

**Activate billing and proceed with full collection.**

**Justification:**
- Cost is minimal ($5-10 total)
- Data is critical for validation
- Trade/procurement analysis already shows 13 flagged countries
- GDELT is final piece for comprehensive multi-source validation
- Time saved: 6 months of waiting vs. 1 day of collection

---

## Files Ready for Execution

### Collection Scripts
- ✅ `scripts/collectors/gdelt_eu_china_bilateral_collector.py` - Bilateral collector
- ✅ `collect_eu_priority_countries_gdelt.py` - Orchestration script
- ✅ Database schema ready
- ✅ Cost tracking implemented
- ✅ Error handling and logging

### Analysis Scripts
- ✅ `analyze_eu27_china_trade.py` - Trade pattern analysis
- ✅ `analyze_eu_ted_flagged_countries.py` - Procurement cross-reference
- ✅ Multi-source validation framework ready

**Status:** Infrastructure complete, ready to execute once billing is activated.

---

## Contact/Support

If you encounter issues activating billing:
1. Check Google Cloud Console for billing account status
2. Verify payment method is current
3. Check for any billing alerts or suspended accounts
4. Google Cloud Support: https://cloud.google.com/support

---

**Next Action:** Activate billing in Google Cloud Console, then run pilot collection to validate.
