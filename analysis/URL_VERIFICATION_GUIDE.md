# Policy Document URL Verification Guide

## Overview
Manual verification of 98 policy document URLs to find direct PDF download links.

**CSV File:** `policy_urls_verification_20251028_172819.csv`

---

## Document Breakdown by Country

| Country | Count | Priority | Notes |
|---------|-------|----------|-------|
| EU      | 23    | HIGH     | EUR-Lex URLs - standard structure |
| GB      | 11    | HIGH     | gov.uk - usually has PDF versions |
| DE      | 9     | HIGH     | Major economy, mixed formats |
| FR      | 9     | HIGH     | Major economy, mixed formats |
| CH      | 4     | MEDIUM   | Swiss federal sites |
| IT      | 4     | MEDIUM   | Italian government portals |
| SE      | 4     | MEDIUM   | Swedish government sites |
| AT      | 3     | LOW      | Austrian federal sites |
| CZ      | 3     | LOW      | Czech government sites |
| DK      | 3     | LOW      | Danish government sites |
| ES      | 3     | LOW      | Spanish government sites |
| FI      | 3     | LOW      | Finnish government sites |
| IE      | 3     | LOW      | Irish government sites |
| NL      | 3     | LOW      | Dutch government sites |
| NO      | 3     | LOW      | Norwegian government sites |
| PT      | 3     | LOW      | Portuguese government sites |
| RO      | 3     | LOW      | Romanian government sites |
| BE      | 2     | LOW      | Belgian federal sites |
| PL      | 2     | LOW      | Polish government sites |

**Total:** 98 documents

---

## URL Types and How to Find PDFs

### 1. EUR-Lex (EU Official Journal)
**Example:** `https://eur-lex.europa.eu/eli/reg/2024/1689/oj`

**How to find PDF:**
1. Visit the URL
2. Look for "Download" dropdown or button
3. Select "PDF" format
4. Copy the direct PDF URL (usually ends with `.pdf` or has `/pdf` in path)

**Common EUR-Lex PDF pattern:**
- Add `/pdf` to end of URL
- Example: `https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32024R1689`

### 2. European Commission Digital Strategy
**Example:** `https://digital-strategy.ec.europa.eu/en/library/...`

**How to find PDF:**
1. Scroll down the page
2. Look for "Download" section or "Documents" section
3. Find PDF link (usually in sidebar or bottom of page)
4. Copy direct URL to PDF file

### 3. UK Government (gov.uk)
**Example:** `https://www.gov.uk/government/publications/national-ai-strategy`

**How to find PDF:**
1. Page will show document details
2. Look for "Documents" section
3. Usually has PDF and HTML versions listed
4. Right-click PDF link → Copy link address
5. URL format: `https://assets.publishing.service.gov.uk/.../*.pdf`

### 4. German Government (.bund.de, .bmbf.de, .bmwk.de)
**Example:** `https://www.bmbf.de/bmbf/en/research/...`

**How to find PDF:**
1. Look for download icon or "PDF" link on page
2. May be in sidebar or at bottom
3. Sometimes says "Download Publication" (Publikation herunterladen)
4. Direct PDF URLs usually have `.pdf` extension

### 5. French Government (.gouv.fr)
**Example:** `https://www.gouvernement.fr/en/national-strategy-for-artificial-intelligence-ia-2-0`

**How to find PDF:**
1. Scroll to find "Download" or "Télécharger" link
2. May have multiple language versions
3. Copy English PDF URL if available, French if not

### 6. Other National Sites
**General approach:**
1. Visit landing page
2. Look for: "Download", "PDF", "Publication", "Document"
3. Check footer, sidebar, or inline download buttons
4. If no PDF exists, note "HTML only" in notes column

---

## Common Issues and Solutions

### Issue 1: No Direct PDF Available
**Solution:** Note "HTML only" in notes column, leave verified_pdf_url blank

### Issue 2: PDF Behind Login/Paywall
**Solution:** Note "requires login" in notes column, leave verified_pdf_url blank

### Issue 3: URL Returns 404
**Solution:**
1. Try searching for document title on government portal
2. If found, update with new URL
3. If not found, note "404 - document removed" in notes column

### Issue 4: Multiple PDFs (e.g., Summary + Full Version)
**Solution:** Choose the **full version**, note in notes column: "Full version selected"

### Issue 5: Multiple Languages
**Solution:** Prefer **English** if available, otherwise **original language**

### Issue 6: URL Points to Portal/Database
**Solution:** Note "portal - requires manual search" in notes column

---

## Workflow Recommendations

### Phase 1: Quick Wins (30 minutes)
Focus on EUR-Lex (23 documents) - most standardized structure

### Phase 2: Major Countries (45 minutes)
UK (11), Germany (9), France (9) - total 29 documents

### Phase 3: Remaining Countries (45 minutes)
All others (46 documents)

**Total estimated time:** ~2 hours

---

## Quality Checks

For each verified URL, confirm:
- [ ] URL ends with `.pdf` OR opens PDF in browser
- [ ] File size > 100 KB (not a placeholder/error page)
- [ ] Document title roughly matches what we're looking for
- [ ] Language is English or original national language

---

## After Verification

Once CSV is updated with verified URLs:

```bash
python scripts/utilities/import_verified_policy_urls.py
```

This will:
1. Read the updated CSV
2. Show preview of changes
3. Ask for confirmation
4. Update database with verified URLs

Then run document processor:
```bash
python scripts/processors/policy_document_processor.py
```

This will download and extract text from all documents with verified URLs.

---

## Tips for Efficiency

1. **Open CSV in Excel** - easier to edit than text editor
2. **Use browser's "Inspect Element"** to find exact PDF URLs if download button triggers JavaScript
3. **Test 2-3 URLs** before bulk work to ensure format is correct
4. **Save CSV frequently** to avoid losing progress
5. **Mark progress** - add "DONE" in notes column as you verify each section

---

## Sample Verified Entries

```csv
eu_policy_7c3e2b8a1234,EU,regulation,Regulation (EU) 2024/1689 on Artificial Intelligence (AI Act),European Parliament and Council,2024-07-12,https://eur-lex.europa.eu/eli/reg/2024/1689/oj,https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32024R1689,Full regulation PDF,NO

gb_policy_a1b2c3d4e5f6,GB,strategy,National AI Strategy,UK Government,2021-09-22,https://www.gov.uk/government/publications/national-ai-strategy,https://assets.publishing.service.gov.uk/media/614db4d1e90e077a2cbdf3c4/National_AI_Strategy.pdf,Full strategy document,NO

de_policy_f1e2d3c4b5a6,DE,strategy,Artificial Intelligence Strategy,German Federal Government,2020-12-01,https://www.ki-strategie-deutschland.de/home.html,https://www.ki-strategie-deutschland.de/files/downloads/Nationale_KI-Strategie_engl.pdf,English version,NO
```

---

**Status:** Ready for manual verification
**Next Step:** Open CSV in Excel and start with EUR-Lex documents (quickest wins)
