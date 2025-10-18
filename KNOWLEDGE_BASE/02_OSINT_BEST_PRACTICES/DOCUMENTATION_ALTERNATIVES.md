# DOCUMENTATION ALTERNATIVES (NO SCREENSHOTS)
**Practical Chain of Custody for AI Systems**
**Date:** 2025-09-19

---

## 📝 WHAT TO DO INSTEAD OF SCREENSHOTS

### 1. FULL TEXT PRESERVATION

```yaml
DOCUMENT_BY_QUOTING:
  capture:
    - Exact text of claim
    - Surrounding context
    - Author/publication
    - Date/timestamp
    - URL/location

  example:
    source: "Reuters"
    url: "reuters.com/article/12345"
    accessed: "2025-09-19 14:00 UTC"
    exact_quote: |
      "Leonardo S.p.A. announced today that it has signed
      a maintenance agreement with Chinese operators for
      civilian AW139 helicopters currently in service."
    context: "Article about Leonardo's Asian expansion"
    author: "John Smith"
    dateline: "ROME, March 15"
```

### 2. WAYBACK MACHINE REFERENCES

```yaml
ARCHIVE_VERIFICATION:
  instead_of_screenshot:
    - Note Wayback Machine URL if available
    - Reference archive.org snapshot date
    - Document Internet Archive link

  format:
    original: "reuters.com/article/12345"
    archived: "web.archive.org/web/20250319/reuters.com/article/12345"
    note: "User can verify via Wayback Machine"
```

### 3. STRUCTURED DATA EXTRACTION

```yaml
KEY_ELEMENTS_DOCUMENTATION:
  who: "Exact entities mentioned"
  what: "Specific claims made"
  where: "Locations specified"
  when: "Dates/timeframes given"
  how: "Methods described"
  why: "Rationale provided"

  example:
    who: "Leonardo S.p.A., Chinese operators"
    what: "Maintenance agreement signed"
    where: "China, Rome (signing location)"
    when: "March 15, 2025"
    how: "Civilian helicopter maintenance training"
    why: "Support existing AW139 fleet in China"
```

### 4. VERIFICATION BREADCRUMBS

```yaml
HOW_TO_VERIFY:
  provide_search_terms:
    - Exact phrases to Google
    - Specific database queries
    - Patent/filing numbers

  example:
    google: '"Leonardo" "AW139" "China" "maintenance agreement" 2025'
    sec_edgar: "Leonardo DRS 10-K China"
    patent_search: "AW139 maintenance simulator CN"
    news_search: "site:reuters.com Leonardo China helicopter"
```

### 5. CONTENT HASHING (When Possible)

```yaml
TEXT_FINGERPRINTING:
  if_full_text_available:
    - Record word count
    - Note unique phrases
    - Document distinctive claims
    - List specific numbers

  example:
    word_count: 847
    unique_phrase: "tri-nation maintenance consortium"
    specific_numbers: "40 helicopters, $50M contract, 2027 completion"
    distinctive: "First Western helicopter OEM in Guangzhou"
```

### 6. CROSS-REFERENCE DOCUMENTATION

```yaml
MULTIPLE_ACCESS_POINTS:
  primary_source: "Reuters article URL"
  also_available:
    - "Factiva database: Doc ID RTS20250315x1234"
    - "LexisNexis: 2025 WLNR 12345678"
    - "Bloomberg Terminal: NSN R1234567890"
    - "Company website: investor relations section"
```

---

## 🔄 UPDATED CHAIN OF CUSTODY

### Replace Screenshot Requirement With:

```yaml
DOCUMENTATION_REQUIREMENTS:
  mandatory:
    1_source_identification:
      - Publication/website name
      - Full URL
      - Access timestamp (UTC)
      - Admiralty rating

    2_content_preservation:
      - Exact quotes of key claims
      - Surrounding context
      - Word count if available
      - Unique identifiers

    3_verification_path:
      - How to find it again
      - Search terms that work
      - Alternative access points
      - Archive.org check

    4_metadata:
      - Author if known
      - Publication date
      - Last modified date
      - Version/revision notes
```

### Example Documentation:

```markdown
## Source Documentation

**Source:** Reuters [B2]
**URL:** https://reuters.com/article/leonardo-china-helicopters-12345
**Accessed:** 2025-09-19 14:00:00 UTC

**Key Claims (Exact Text):**
> "Leonardo S.p.A. has secured a 50 million euro contract to provide
> maintenance training and support for AW139 helicopters operated by
> Chinese civilian operators."

**Context:** Part of larger article about Leonardo's Asian strategy
**Author:** John Smith, Reuters Rome Bureau
**Dateline:** ROME, March 15, 2025
**Word Count:** 847

**Verification Path:**
- Google: "Leonardo AW139 China 50 million euro March 2025"
- Reuters search: "Leonardo China helicopter maintenance"
- Wayback Machine: Check for snapshot around March 15, 2025
- Alternative: Bloomberg (if subscriber): NSN R123ABC

**Unique Identifiers:**
- Contract value: "50 million euro"
- Specific model: "AW139"
- Unusual phrase: "tri-nation support framework"
```

---

## ✅ ADVANTAGES OF TEXT DOCUMENTATION

1. **Searchable** - Can find specific claims later
2. **Verifiable** - Others can check sources
3. **Preservable** - Text doesn't degrade
4. **Legal** - Quotes fall under fair use
5. **Efficient** - Faster than screenshots
6. **Accessible** - Works for all users

---

## 🚫 WHAT NOT TO DO

**DON'T:**
- Paraphrase when you can quote
- Summarize without preserving key claims
- Forget timestamp/URL
- Omit Admiralty rating
- Skip verification paths

**DO:**
- Quote exactly
- Preserve context
- Document everything
- Provide verification methods
- Note what you couldn't access

---

## 🎯 THE GOAL

**Enable someone else to:**
1. Find the same source
2. Verify the claims
3. Check for updates/changes
4. Assess reliability
5. Trace information flow

**Without needing screenshots**

---

*This approach provides better documentation than screenshots alone*
*Text is searchable, preservable, and legally defensible*
