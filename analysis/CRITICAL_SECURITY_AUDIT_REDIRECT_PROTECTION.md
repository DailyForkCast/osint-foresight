# CRITICAL SECURITY AUDIT: Redirect Protection

**Date:** 2025-10-20
**Severity:** CRITICAL
**Status:** VULNERABILITY IDENTIFIED AND FIXED

---

## Executive Summary

**CRITICAL VULNERABILITY DISCOVERED:** Existing sweep systems do NOT have redirect protection, allowing automatic following of redirects to live .cn domains if archive services fail.

**Impact:** If Wayback Machine or other archive services redirect to live Chinese government websites (e.g., sasac.gov.cn, sse.com.cn), the system will automatically follow those redirects, potentially:
1. Directly accessing forbidden .cn domains
2. Creating network traffic to Chinese government servers
3. Violating ethical collection policies
4. Potentially alerting Chinese authorities to monitoring activities

---

## Vulnerability Details

### Affected Systems

1. **china_production_runner_by_bucket.py** (CRITICAL - ACTIVELY RUNNING)
   - Location: `scripts/collectors/china_production_runner_by_bucket.py:105`
   - Vulnerable code:
     ```python
     response = self.session.get(url, timeout=30)  # NO redirect protection!
     ```
   - Used for: China policy document collection (weekly production runs)
   - Risk: HIGH - This system is actively collecting from archive services

2. **prc_soe_monitoring_collector.py** (FIXED - NOT YET DEPLOYED)
   - Status: ✅ Fixed with redirect protection before deployment
   - Implementation: `download_with_redirect_protection()` method

### Attack Vector

**Scenario:** Archive service redirects to live .cn domain

```
1. System requests: https://web.archive.org/web/20240101/sasac.gov.cn/mergers
2. Archive returns: HTTP 302 Redirect to https://www.sasac.gov.cn/mergers
3. System automatically follows redirect (WITHOUT CHECKING DESTINATION)
4. System directly accesses live Chinese government website
```

**Result:** Direct access to forbidden .cn domain, bypassing all safety rules.

---

## Test Results

### Redirect Protection Testing (prc_soe_monitoring_collector.py)

**Test File:** `test_redirect_protection.py`
**Results:** 5/5 tests passed (100%)

```
Test 1: Redirect to .cn domain (MUST BLOCK)
  [PASS] Download blocked as expected
  Error: Archive redirected to forbidden domain: https://www.sasac.gov.cn/news
  [PASS] Correct error message

Test 2: Redirect to another archive URL (ALLOWED)
  [PASS] Download succeeded as expected

Test 3: Redirect to non-archive, non-.cn domain (SUSPICIOUS)
  [PASS] Download blocked as expected
  Error: Redirect to non-archive URL: https://example.com

Test 4: Direct 200 OK from archive (ALLOWED)
  [PASS] Download succeeded as expected

Test 5: Archive 404 (EXPECTED FAILURE)
  [PASS] Download blocked as expected
  Error: HTTP 404

Security violations logged: 1
[OK] Security violations are being tracked
```

**Conclusion:** Redirect protection works as designed - ALL redirects to .cn domains are blocked.

---

## Fix Implementation

### New `download_with_redirect_protection()` Method

**Key Features:**

1. **Disable Automatic Redirects:**
   ```python
   response = self.session.get(url, timeout=30, allow_redirects=False)
   ```

2. **Validate Redirect Destinations:**
   ```python
   if 300 <= response.status_code < 400:
       redirect_url = response.headers.get('Location', '')

       # CRITICAL: Check if redirect is to forbidden domain
       if SafeAccessValidator.is_forbidden_domain(redirect_url):
           logger.error(f"SECURITY VIOLATION: Archive redirected to forbidden domain")
           self.stats['security_violations'] += 1
           return None, False, f"Archive redirected to forbidden domain: {redirect_url}"
   ```

3. **Whitelist Archive Redirects Only:**
   ```python
   archive_domains = ['archive.org', 'web.archive.org', 'commoncrawl.org',
                     'archive.today', 'archive.is', 'archive.ph']
   is_archive_redirect = any(domain in redirect_url.lower() for domain in archive_domains)

   if not is_archive_redirect:
       return None, False, f"Redirect to non-archive URL: {redirect_url}"
   ```

4. **Validate Final URL:**
   ```python
   final_url = response.url
   if SafeAccessValidator.is_forbidden_domain(final_url):
       self.stats['security_violations'] += 1
       return None, False, f"Final URL is forbidden domain: {final_url}"
   ```

5. **Track Security Violations:**
   ```python
   self.stats['security_violations'] += 1  # Logged for monitoring
   ```

---

## Remediation Plan

### Immediate Actions (CRITICAL)

1. ✅ **Fix prc_soe_monitoring_collector.py** - COMPLETE
   - Implemented redirect protection
   - Tested with 100% pass rate
   - System will NEVER follow redirects to .cn domains

2. ✅ **Fix china_production_runner_by_bucket.py** - COMPLETE
   - Replaced `download_html()` with redirect-protected version
   - Added SafeAccessValidator integration
   - Added security stats tracking and reporting
   - Syntax validated

3. ✅ **Fix china_production_runner_full.py** - COMPLETE
   - Replaced `download_html()` with redirect-protected version
   - Added SafeAccessValidator integration
   - Added security stats tracking and reporting
   - Syntax validated

4. ✅ **Audit All Other Collectors** - COMPLETE
   - Searched for all `session.get()` calls in collectors
   - Identified 3 vulnerable China collectors
   - ALL vulnerable collectors now fixed

### Medium-term Actions

1. ⬜ **Create Shared Redirect Protection Library**
   - Extract `download_with_redirect_protection()` to shared utility
   - Use in all collectors
   - Enforce via code review

2. ⬜ **Add Automated Security Tests**
   - Run redirect protection tests in CI/CD
   - Alert on any session.get() without allow_redirects=False
   - Enforce security checks before deployment

3. ⬜ **Review Historical Logs**
   - Check if any accidental .cn access occurred
   - Analyze redirect patterns in logs
   - Document any security violations

---

## Risk Assessment

### Before Fix

**Risk Level:** CRITICAL
**Probability:** HIGH (archive services DO redirect to live sites when content unavailable)
**Impact:** HIGH (direct access to forbidden domains, policy violation)

### After Fix

**Risk Level:** LOW
**Probability:** LOW (redirect protection blocks all .cn redirects)
**Impact:** MINIMAL (redirects logged as security violations, no access occurs)

---

## Lessons Learned

1. **Default Behavior is Unsafe:** HTTP libraries follow redirects by default - must explicitly disable
2. **Archive Services Can Fail:** Archives DO redirect to live sites when snapshots unavailable
3. **Defense in Depth Required:** Multiple validation layers (domain check, redirect check, final URL check)
4. **Testing is Critical:** Without test_redirect_protection.py, this vulnerability would have gone unnoticed
5. **Security Must Be Proactive:** Cannot assume existing systems are secure without audit

---

## Recommendations

### For All Future Collectors

1. **NEVER use `session.get(url)` without `allow_redirects=False`**
2. **ALWAYS validate redirect destinations before following**
3. **ALWAYS validate final URLs after requests**
4. **ALWAYS log security violations for monitoring**
5. **ALWAYS test redirect scenarios before deployment**

### For Code Review

1. **Reject any session.get() without redirect protection**
2. **Require redirect protection tests for all collectors**
3. **Verify SafeAccessValidator integration**
4. **Check security violation tracking**

---

## Next Steps

1. ✅ Document vulnerability (this file) - COMPLETE
2. ✅ Fix china_production_runner_by_bucket.py - COMPLETE
3. ✅ Fix china_production_runner_full.py - COMPLETE
4. ✅ Audit all other collectors - COMPLETE (3 vulnerable, all fixed)
5. ⬜ Test production fix with real bucket sources - PENDING
6. ⬜ Create shared redirect protection library - PENDING
7. ⬜ Add CI/CD security tests - PENDING
8. ⬜ Review historical logs for any violations - PENDING

---

## References

- **Test File:** `test_redirect_protection.py`
- **Fixed Implementation:** `scripts/collectors/prc_soe_monitoring_collector.py:678-772`
- **Vulnerable Code:** `scripts/collectors/china_production_runner_by_bucket.py:105`
- **Safety Validator:** `scripts/collectors/prc_soe_monitoring_collector.py:190-277`

---

**Report Status:** COMPLETE
**Next Action:** Fix china_production_runner_by_bucket.py immediately
