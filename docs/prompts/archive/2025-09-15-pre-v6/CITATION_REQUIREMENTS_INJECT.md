# CRITICAL CITATION REQUIREMENTS - INJECT INTO ALL PROMPTS

## ⚠️ MANDATORY CITATION STANDARDS ⚠️

**THIS SECTION MUST BE INCLUDED IN EVERY PROMPT FOR ChatGPT AND Claude Code**

---

### 🔴 CRITICAL REQUIREMENTS FOR ALL CITATIONS

1. **EXACT URL REQUIREMENT**
   - ❌ **NEVER** cite just a domain: `www.nytimes.com`
   - ❌ **NEVER** cite just a homepage: `https://www.nytimes.com`
   - ✅ **ALWAYS** cite the exact article/document: `https://www.nytimes.com/2025/09/13/us/politics/probationary-employees-firing-illegal.html`

2. **ACCESSED DATE REQUIREMENT**
   - **EVERY** citation MUST include `accessed_date` in format: `YYYY-MM-DD`
   - Example: `Accessed: 2025-09-13`
   - This tracks WHEN we retrieved the information

3. **CITATION FORMAT**
   ```
   Author. (Publication Date). Title. Publication.
   Retrieved [Accessed Date], from [EXACT URL TO DOCUMENT]
   ```

### 📋 REQUIRED FIELDS FOR EVERY SOURCE

```json
{
  "exact_url": "[FULL URL to specific document/article/page]",
  "title": "[Exact title of document]",
  "accessed_date": "YYYY-MM-DD",
  "author": "[Author name(s)]",
  "publication": "[Publication name]",
  "publication_date": "YYYY-MM-DD",
  "archive_url": "[Wayback Machine or archive.today link]"
}
```

### ❌ EXAMPLES OF INCORRECT CITATIONS

```
WRONG: "See New York Times website"
WRONG: "Available at: www.nytimes.com"
WRONG: "Source: https://www.nytimes.com"
WRONG: "EU legislation website"
WRONG: "Government portal"
```

### ✅ EXAMPLES OF CORRECT CITATIONS

```
Savage, C. (2025, September 13). Mass Firing of Probationary Federal Employees Was Illegal, Judge Rules.
The New York Times. Retrieved 2025-09-13, from
https://www.nytimes.com/2025/09/13/us/politics/probationary-employees-firing-illegal.html

DPCM n.131. (2020, October 21). Regolamento in materia di perimetro di sicurezza nazionale cibernetica.
Gazzetta Ufficiale Serie Generale n.261. Retrieved 2025-09-13, from
https://www.gazzettaufficiale.it/eli/id/2020/10/21/20G00150/sg

Regulation (EU) 2022/868. (2022, May 30). European High Performance Computing.
Official Journal L 151/1. Retrieved 2025-09-13, from
https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R0868
```

### 🎯 SPECIFIC INSTRUCTIONS BY SOURCE TYPE

#### News Articles
- URL must point to the specific article
- Include author name(s)
- Use exact headline as title
- Archive important/paywalled articles

#### Government Documents
- Link to the specific document/law/regulation
- NOT the ministry homepage
- Include official gazette references
- Note document numbers/codes

#### Academic Papers
- Prefer DOI links when available
- Include arXiv IDs for preprints
- Link to open access versions when possible
- Include all authors

#### EU/Legal Documents
- Use CELEX numbers for EU law
- Link to specific legal text
- Include Official Journal references
- Note consolidated versions

### 🔍 VALIDATION CHECKLIST

Before submitting ANY citation, verify:
- [ ] URL links to SPECIFIC document (not homepage)
- [ ] accessed_date is included (YYYY-MM-DD format)
- [ ] Title is exact (not paraphrased)
- [ ] Author is included (if available)
- [ ] Publication date is included
- [ ] Archive link created for important sources

### 💾 DATA COLLECTION REQUIREMENTS

When collecting data, ALWAYS store:
```python
{
    "source_url": "https://example.com/specific/article.html",  # EXACT URL
    "source_title": "Exact Article Title",
    "accessed_date": "2025-09-13",  # WHEN we accessed it
    "extraction_date": "2025-09-13",  # WHEN we extracted data
    "verification_date": "2025-09-14",  # WHEN we verified it
    "archive_url": "https://web.archive.org/...",  # Archive link
    "confidence_score": 0.95  # Based on source reliability
}
```

### 🚨 ERROR MESSAGES TO PREVENT

```
ERROR: Citation must include EXACT URL to specific document.
ERROR: URL points to homepage, not specific document.
ERROR: Missing accessed_date field (required for all citations).
ERROR: Date format must be YYYY-MM-DD.
```

### 📝 PROMPT INJECTION TEMPLATE

```markdown
[Insert at the beginning of EVERY data collection prompt]

CRITICAL: ALL citations MUST include:
1. EXACT URL to specific document (NOT homepage/domain)
2. accessed_date in YYYY-MM-DD format
3. Document title (exact, not paraphrased)

Example:
❌ WRONG: www.nytimes.com
✅ RIGHT: https://www.nytimes.com/2025/09/13/section/exact-article.html

Store accessed_date with EVERY source!
```

### 🔄 FOR AUTOMATED SYSTEMS

```python
# Validation function to include in all scrapers/collectors
def validate_citation(citation):
    errors = []

    # Check URL is specific
    if not citation.get('exact_url') or citation['exact_url'].endswith(('.com/', '.org/', '.gov/')):
        errors.append("URL must point to specific document, not homepage")

    # Check accessed_date exists
    if not citation.get('accessed_date'):
        errors.append("accessed_date is REQUIRED")

    # Validate date format
    if citation.get('accessed_date') and not re.match(r'^\d{4}-\d{2}-\d{2}$', citation['accessed_date']):
        errors.append("accessed_date must be YYYY-MM-DD format")

    return len(errors) == 0, errors
```

---

## IMPLEMENTATION NOTES

1. **For ChatGPT:** Include the citation requirements section at the TOP of every prompt
2. **For Claude Code:** Add validation checks to all data collection scripts
3. **For Manual Entry:** Use the validation checklist before saving
4. **For APIs:** Store accessed_date with every API response

## ENFORCEMENT

- Citations without exact URLs will be REJECTED
- Missing accessed_date will trigger validation ERROR
- Homepage-only links will be flagged for correction
- All phases must comply with these standards

---

**Remember:** The credibility of our analysis depends on traceable, verifiable sources. Every citation must point to the EXACT document we're referencing, and we must track WHEN we accessed it.
