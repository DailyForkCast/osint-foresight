# Bug Fix: Relative Path Handling in Article Link Extraction

## Date
2025-10-15

## Issue
Europe-China Policy Collection system was finding **0 article links** from the CIIS homepage in STAGE 2 (Extract article links from homepage), causing the collection to fail.

## Root Cause
The article link extraction code in `scripts/collectors/europe_china_collector.py:377-385` only handled:
- Absolute paths starting with `/` (e.g., `/yjcg/sspl/`)
- Full URLs starting with `http` (e.g., `http://example.com`)

However, **ALL 80 CIIS links used relative paths starting with `./`** (e.g., `./yjcg/sspl/`, `./yjcg/xslw/`), which were being silently skipped without processing.

## Debug Process
1. Created `debug_link_extraction.py` to analyze CIIS homepage
2. Initial output showed: `total: 100, not_ciis_domain: 20, matched: 0`
3. Added tracking for skipped hrefs
4. Discovered all 80 CIIS links had format `./path/` instead of `/path/` or `http://...`

## Solution
Added handling for relative paths starting with `./`:

```python
elif href.startswith('./'):
    # Handle relative paths like ./yjcg/sspl/ (common in Chinese sites)
    parsed_original = urlparse(homepage_snapshot['original_url'])
    abs_url = f"{parsed_original.scheme}://{parsed_original.netloc}/{href[2:]}"
```

This strips the `./` prefix and constructs an absolute URL from the homepage's scheme and netloc.

## Files Modified
1. `scripts/collectors/europe_china_collector.py` - Lines 383-386 (production code)
2. `debug_link_extraction.py` - Lines 64-66 (debug script)

## Verification
After fix, debug script output:
```
Total links found: 100

Processing Statistics:
  total: 100
  not_ciis_domain: 20
  relative_skipped: 0
  skipped: 16
  matched: 59
  no_match: 5

Matched URLs (59):
  http://www.ciis.org.cn/yjcg/sspl/       # Current Affairs Commentary
  http://www.ciis.org.cn/yjcg/zzybg/      # Publications & Reports
  http://www.ciis.org.cn/yjcg/xslw/       # Academic Papers
  http://www.ciis.org.cn/yjcg/yjbg/       # Research Reports
  ...
```

**Success:** Now finding **59 article links** (was 0)!

## Impact
- CIIS (China Institute of International Studies) articles can now be collected
- Likely affects other Chinese think tanks that use `./` relative paths
- No safety violations - all paths are properly validated before conversion to absolute URLs

## Testing Recommendation
Run full collection test with CIIS to verify STAGE 3 (document extraction with keyword filtering) works correctly with these newly discovered article URLs.

## Technical Notes
- Chinese websites commonly use `./` relative paths in their navigation
- This pattern may appear in other sources (CICIR, CASS, etc.)
- The fix maintains all safety checks (SAFE_MODE_MIRROR_ONLY enforcement)
- Archive URLs are constructed from the original homepage URL's scheme/netloc
