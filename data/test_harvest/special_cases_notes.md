# Special Cases - Think Tank Harvesting Notes

## FOI (Swedish Defence Research Agency)
**Status:** CONFIRMED China content, requires special handling

### Key Findings:
- Site IS accessible (not blocking)
- Has extensive China military/innovation research
- No traditional site structure or search
- Content scattered across individual articles

### Working Paths:
```
/en/foi/reports.html
/en/foi/news-and-pressroom
/en/foi/research
/en/foi/reports/report-summary.html
```

### Sample China Content:
- "Developing an analytical framework and methods for studying China's military power" (2025)
- "Important aspects of China's innovation capacity are being overlooked" (2025)
- Multiple FOI reports (FOI-R--5695--SE, FOI-R--5673--SE, etc.)

### Harvesting Strategy Required:
1. Scrape listing pages for article links
2. Extract all `.html` article URLs
3. Filter for China-related titles
4. Fetch individual articles
5. Parse content from article pages

### TODO:
- Implement custom scraper for FOI listing pages
- Create article link extractor
- Add to harvester with special handling

---

## NUPI (Norwegian Institute of International Affairs)
**Status:** CONFIRMED China content via PDFs

### Evidence:
User provided URLs showing China/Arctic research:
1. https://www.nupi.no/content/pdf_preview/29346/file/NUPI_Report_11_2024_Gasemyr_.pdf
2. https://www.nupi.no/content/pdf_preview/29660/file/NUPI_Policy_Brief_2_BloomHenriksenRowe.pdf
3. https://www.nupi.no/en/news/has-military-activity-in-the-arctic-increased-after-2022

### Content Pattern:
- PDF reports at `/content/pdf_preview/[ID]/file/[filename].pdf`
- News articles at `/en/news/[article-slug]`
- Likely has China content in Arctic/security context

### TODO:
- Investigate NUPI PDF listing pages
- Check for publications API or RSS feed
- Test `/en/publications` or similar paths
- Add PDF extraction capability to harvester

---

## RUSI (Royal United Services Institute)
**Status:** CONFIRMED China content

### Evidence (user-provided URLs):
- "Velvet Glove Iron Fist: Understanding China's Use of State Threats"
- "Critical Minerals and US-China Rivalry in South America"
- "40 Red Hackers Who Shaped China's Cyber Ecosystem"
- AI and National Security PDF at `/AI-and-National-Secuity_final.pdf`

### Working Paths:
- `/explore-our-research/publications`
- `/explore-our-research/publications/commentary`
- `/explore-our-research/publications/external-publications`

### Harvesting Strategy:
- Public content IS available
- May have additional member-only content
- PDFs available at `static.rusi.org`

---

## IAI (Istituto Affari Internazionali)
**Status:** CONFIRMED China/economic security content

### Evidence (user-provided URLs):
- "Tug of War Over Economic Security: Italy's Golden Power"
- "Economic Security National Security: Unacknowledged Deja Vu"
- PDF reports at `/sites/default/files/iaip*.pdf`

### Content Access:
- Direct article URLs work: `/en/pubblicazioni/c05/[article-slug]`
- PDFs at: `/sites/default/files/[filename].pdf`
- Listing pages return 404 but individual articles accessible

### Harvesting Strategy:
- Need to discover article URLs through other means
- Monitor economic security topics (often China-related)
- Extract PDFs from `/sites/default/files/`

---

## General Harvesting Improvements Needed:

1. **PDF Support**: Many think tanks publish reports as PDFs (NUPI, FOI)
2. **Listing Page Scrapers**: For sites without search (FOI)
3. **Multi-language Support**: For European sites
4. **Article Link Extraction**: Parse listing pages for individual articles
5. **Dynamic Content Handling**: Some sites may use JavaScript

## Priority Actions:
1. Implement FOI custom scraper
2. Add PDF extraction for NUPI
3. Create fallback strategies for sites without search
4. Consider Selenium for JavaScript-heavy sites
