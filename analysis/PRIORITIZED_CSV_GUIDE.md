# Prioritized Policy URL Verification Guide

**CSV File:** `policy_urls_PRIORITIZED_20251028_180500.csv`

---

## Overview

This CSV organizes all 98 policy documents by priority for efficient manual verification.

**Status Breakdown:**
- ✅ **2 documents:** Already done (text extracted) → SKIP
- 🔴 **45 documents:** Broken URLs (404/403/timeout) → FIX FIRST
- 🟡 **51 documents:** HTML landing pages → FIND PDF LINKS

---

## CSV Structure

| Column | Description |
|--------|-------------|
| **priority** | Sort key for workflow (0_SKIP, 1_PRIORITY, 2_NEED_PDF, 3_CHECK) |
| **status** | Document status (DONE, BROKEN_URL, HTML_PAGE, UNKNOWN) |
| **document_id** | Unique identifier |
| **country_code** | Country (AT, BE, CH, CZ, DE, DK, ES, EU, FI, FR, GB, etc.) |
| **document_type** | Type (regulation, directive, strategy, law, plan, initiative) |
| **document_title** | Full document title |
| **issuing_body** | Organization that published document |
| **publication_date** | Publication date |
| **current_url** | URL we collected (most are broken or landing pages) |
| **verified_pdf_url** | **← FILL THIS IN** with direct PDF URL |
| **notes** | **← ADD NOTES** (e.g., "HTML only", "not available") |
| **status_detail** | Why this document needs attention |

---

## Priority System

### 0_SKIP (2 documents) - Already Done ✅

**What:** Documents with text already extracted
**Action:** None - skip these entirely

**Examples:**
- Ireland: National Cyber Security Strategy (113,810 chars extracted)
- Italy: National Recovery and Resilience Plan (810,984 chars extracted)

---

### 1_PRIORITY (45 documents) - Broken URLs 🔴

**What:** URLs that returned 404, 403, timeout, or connection errors
**Action:** Search for correct URL using web search

**Breakdown by Error Type:**
- **404 Not Found (19 docs):** Document moved or removed
- **403 Forbidden (18 docs):** Bot protection (France: 9, Sweden: 4, Austria: 2)
- **400 Bad Request (4 docs):** Malformed URLs (Germany: 4)
- **Timeout/Connection (4 docs):** Site issues (Romania: 3, Switzerland: 1)

**Countries Most Affected:**
- 🇫🇷 France: 9 broken (all gouvernement.fr - likely bot protection)
- 🇩🇪 Germany: 6 broken (bmwk.de, bmbf.de, bmi.bund.de)
- 🇸🇪 Sweden: 4 broken (all government.se - bot protection)
- 🇳🇱 Netherlands: 3 broken
- 🇷🇴 Romania: 3 broken (timeouts)

**Search Strategy:**
1. Copy document title
2. Search: `[document title] [country] PDF site:gov.[country]`
3. For EU documents: Try EUR-Lex search
4. If not found: Note "Document not available online"

**Example Entry:**
```
1_PRIORITY,BROKEN_URL,at_policy_b3ef715e0d66,AT,strategy,Artificial Intelligence Mission Austria 2030,...,HTTP 403
```
**Action:** Search for "AIM AT 2030 Austria PDF" → Found at bmk.gv.at

---

### 2_NEED_PDF (51 documents) - HTML Landing Pages 🟡

**What:** URLs work (200 OK) but return HTML landing pages, not PDFs
**Action:** Visit URL, find PDF download link on page

**Common Patterns:**

**EUR-Lex Documents (EU regulations/directives):**
- Landing page shows document details
- Look for "Download" dropdown or "PDF" icon
- Direct PDF URL pattern: `https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:XXXXX`

**UK Government (gov.uk):**
- Document page lists "Documents" section
- PDF usually named `[Document_Name].pdf`
- Direct URL: `https://assets.publishing.service.gov.uk/media/[id]/[filename].pdf`

**German Government (bmwk.de, bmbf.de):**
- Look for "Download" button or PDF icon in sidebar
- Sometimes labeled "Publikation herunterladen"

**Other Government Sites:**
- Scroll page for download section
- Look for PDF icon, "Download", or "Télécharger" link
- Right-click → Copy link address

**Example Entry:**
```
2_NEED_PDF,HTML_PAGE,eu_policy_823ad7048aa3,EU,regulation,Regulation (EU) 2024/1689 on Artificial Intelligence (AI Act),...,Landing page - find PDF download link
```
**Action:** Visit EUR-Lex page → Click "Download PDF" → Copy URL

---

### 3_CHECK (0 documents currently)

**What:** Documents with unknown status (no check data)
**Action:** Manually verify if URL works

---

## Workflow Recommendations

### Step 1: Sort and Organize (2 minutes)
1. Open CSV in Excel or LibreOffice Calc
2. Sort by **priority** column (ascending: 0→1→2→3)
3. Review the 2 DONE entries (0_SKIP) - no action needed

### Step 2: Fix Broken URLs - Quick Wins (30 minutes)
**Focus on EUR-Lex documents first:**
- EU regulations/directives have consistent URL patterns
- Search EUR-Lex directly: https://eur-lex.europa.eu
- Example: AI Act CELEX number → Direct PDF link

**Then major countries:**
- UK (gov.uk): Usually well-archived
- Germany: Search bundesregierung.de or ministry sites
- France: gouvernement.fr has archives (if accessible)

### Step 3: Find PDF Links - Batch Process (45 minutes)
**By document type:**
- Start with EUR-Lex documents (consistent structure)
- Then gov.uk documents (similar layouts)
- Finally other national sites (varied structures)

**Pro Tips:**
- Keep one tab per country to reuse site navigation
- Use browser's PDF viewer to verify before copying URL
- If page has multiple PDFs, choose "Full version" over "Summary"

### Step 4: Mark Unavailable (15 minutes)
For documents you can't find:
- In **notes** column, write: "Not available online" or "Requires login"
- Leave **verified_pdf_url** blank
- These will be skipped during processing

---

## Quality Checks

Before marking a URL as complete:
- [ ] URL ends with `.pdf` OR opens PDF directly in browser
- [ ] File size > 100 KB (not an error page)
- [ ] Document title matches roughly (same topic/strategy)
- [ ] Language is appropriate (English preferred, original language OK)

---

## After Verification Complete

Once you've filled in **verified_pdf_url** column for available documents:

1. **Save the CSV file**

2. **Import verified URLs to database:**
   ```bash
   python scripts/utilities/import_verified_policy_urls.py
   ```

3. **Process all documents:**
   ```bash
   python scripts/processors/policy_document_processor.py
   ```

---

## Progress Tracking

Track your progress by country:

| Country | Total | Status |
|---------|-------|--------|
| EU | 23 | ☐ Not started / ☑ Complete |
| GB | 11 | ☐ Not started / ☑ Complete |
| DE | 9 | ☐ Not started / ☑ Complete |
| FR | 9 | ☐ Not started / ☑ Complete |
| Others | 46 | ☐ Not started / ☑ Complete |

**Tip:** Add "DONE" to **notes** column as you verify each document to track progress.

---

## Common Issues and Solutions

**Issue:** EUR-Lex page doesn't show PDF button
- **Solution:** Look for "Official Journal" section, click "PDF" format

**Issue:** Gov.uk shows "Document withdrawn"
- **Solution:** Look for "Archived" or "Superseded by" link

**Issue:** Government site is in foreign language only
- **Solution:** Use browser translate or look for "EN"/"English" toggle

**Issue:** PDF requires JavaScript to download
- **Solution:** Use browser's Inspect Element → Network tab to capture direct URL

**Issue:** Document behind paywall or registration
- **Solution:** Note "Requires login" in notes column, leave URL blank

---

## Estimated Time

- **Phase 1 (SKIP):** 0 minutes - 2 documents already done
- **Phase 2 (FIX):** 45-60 minutes - 45 broken URLs to search/fix
- **Phase 3 (PDF):** 60-90 minutes - 51 landing pages to navigate

**Total:** ~2-2.5 hours for complete verification

---

**Current Status:** Ready for manual verification
**Next Action:** Open `policy_urls_PRIORITIZED_20251028_180500.csv` and start with 1_PRIORITY items
