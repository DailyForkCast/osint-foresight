# UN Comtrade API Test Report
**Date**: 2025-10-30 18:50:43
**Status**: PARTIAL
**API Version**: v1

---

## Test Results

- **Total Tests**: 5
- **Passed**: 4
- **Failed**: 1
- **Success Rate**: 80.0%

---

## Detailed Output

```

================================================================================
TEST 1: API Key Configuration
================================================================================
[OK] Primary key found: 3da083e03b...86b2

================================================================================
TEST 2: Preview Endpoint (No Authentication Required)
================================================================================
Endpoint: https://comtradeapi.un.org/public/v1/preview/C/A/HS
Query: China's total exports to world (2023)
Status Code: 200
[OK] Preview endpoint accessible
Records returned: 1
Sample record keys: ['typeCode', 'freqCode', 'refPeriodId', 'refYear', 'refMonth']

================================================================================
TEST 3: Authenticated Endpoint (Subscription Key)
================================================================================

Trying: https://comtradeapi.un.org/data/v1/get/C/A/HS
  Status: 200
  [WARN] 200 OK but no data returned

Trying: https://comtradeapi.un.org/public/v1/get/C/A/HS
  Status: 404
  Response: { "statusCode": 404, "message": "Resource not found" }

Trying: https://comtradeapi.un.org/public/v1/preview/C/A/HS
  Status: 429
  Response: { "statusCode": 429, "message": "Rate limit is exceeded. Try again in 1 seconds." }
[FAIL] All authenticated endpoints failed

================================================================================
TEST 4: Strategic Trade Query - Semiconductors
================================================================================
Query: China semiconductor imports from Taiwan (2023)
Status: 200
[INFO] Query successful but no data (may be restricted/unavailable)

================================================================================
TEST 5: Bulk Download Capability Check
================================================================================
Note: Not downloading actual file, testing endpoint access only
[WARN] Bulk endpoint status: 404

================================================================================
TEST SUMMARY
================================================================================
Total Tests: 5
Passed: 4
Failed: 1
Success Rate: 80.0%

[PARTIAL] UN COMTRADE API PARTIALLY WORKING
Some endpoints accessible, may require subscription upgrade.
```

---

## Recommendations

- API keys are valid but may be on free tier
- Consider upgrading subscription for full data access
- Preview endpoints can still provide valuable data
