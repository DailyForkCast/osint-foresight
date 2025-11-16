# Root Cause Analysis: Why 4 Chinese Sources Found 0 Article Links

## Problem Summary
Qiushi, People's Daily, Xinhua Reference, and PLA Daily all returned 0 article links despite having archived pages with hundreds of links.

## Investigation Steps
1. **Initial hypothesis**: Plain relative paths like `qswp.htm` were being skipped
2. **First fix attempt**: Added handling for plain relative paths (lines 396-405)
3. **Result**: Still 0 links found
4. **Diagnostic**: Inspected actual href values from Qiushi homepage archive

## Root Cause Discovered

**Wayback Machine rewrites ALL hrefs in archived HTML pages!**

Example from Qiushi homepage:
```
Original (on live site): href="zt2024/20szqh/index.htm"
In Wayback archive:      href="https://web.archive.org/web/20250102125229/http://www.qstheory.cn/zt2024/20szqh/index.htm"
```

### Why This Causes 0 Links

Current code flow (lines 385-420):
1. Extract `href` from link: `https://web.archive.org/web/20250102125229/http://www.qstheory.cn/zt2024/20szqh/index.htm`
2. Check `href.startswith('http')` → TRUE
3. Set `abs_url = href` (the full Wayback URL)
4. Check `if base_domain not in parsed_url.hostname`:
   - `base_domain` = `www.qstheory.cn`
   - `parsed_url.hostname` = `web.archive.org`
   - `"www.qstheory.cn" not in "web.archive.org"` → TRUE
5. **SKIP THE LINK** (line 419-420)

### The Fix Required

When encountering a Wayback-rewritten URL, extract the original URL:

```python
# Wayback URL pattern: https://web.archive.org/web/{timestamp}/{original_url}
wayback_pattern = r'https?://web\.archive\.org/web/\d{14}/(.*)'
match = re.match(wayback_pattern, href)
if match:
    original_url = match.group(1)
    # Now process original_url normally
```

## Impact

This bug affects **ALL** sources, not just the 4 Chinese ones. The reason CIIS and a few others worked is likely because they had some links that weren't rewritten (external links, or different URL patterns).

## Next Steps

Modify `extract_article_links` method to:
1. Detect Wayback-rewritten URLs
2. Extract the original URL
3. Then apply existing plain relative path handling
4. Then apply domain filtering and pattern matching
