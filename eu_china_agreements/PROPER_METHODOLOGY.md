# Proper Methodology for Finding Real EU-China Agreements

## Stop Using Common Crawl
Common Crawl is inappropriate for diplomatic research. It's 90%+ noise.

## Start With Official Sources

### 1. EU Official Databases
- **EUR-Lex**: EU law and treaties database
  - https://eur-lex.europa.eu/
  - Search: "China" AND "agreement"

- **European Commission Treaties Office**
  - Official bilateral agreements repository
  - Filter by: China, date range 1990-2024

- **EU Delegation to China**
  - https://www.eeas.europa.eu/delegations/china_en
  - Official announcements of agreements

### 2. Chinese Government Sources
- **Ministry of Foreign Affairs**
  - Country-specific sections for each EU member
  - Belt and Road Portal (official BRI agreements)

- **Ministry of Commerce (MOFCOM)**
  - Trade agreements database
  - Investment treaties

### 3. Member State Sources
For each EU country, check:
- Foreign Ministry websites
- Trade Ministry databases
- Embassy websites in Beijing
- Chamber of Commerce announcements

### 4. Sister Cities (Proper Method)
- **Sister Cities International** database
- **EU-China Municipal Cooperation** program
- Individual city government websites
- NOT random web crawls

### 5. University Partnerships
- **Erasmus+ database**
- **China Scholarship Council** partnerships
- University international offices
- **Confucius Institute** agreements

## Verification Protocol

### Step 1: Identify Official Source
✓ Government website (.gov, .eu, official .cn)
✓ International organization
✓ Recognized news outlet
✗ Random commercial sites
✗ Blogs, forums, social media

### Step 2: Find Actual Agreement
✓ PDF of signed document
✓ Official announcement with details
✓ Press release from both parties
✗ Vague mentions
✗ URLs with keywords only

### Step 3: Extract Key Data
- **Parties**: Specific entities (not just countries)
- **Date**: When signed
- **Type**: MOU, Treaty, Partnership, etc.
- **Status**: Active, completed, cancelled
- **Scope**: What it covers
- **Duration**: Time period

### Step 4: Cross-Verify
- Check both EU and Chinese sources
- Confirm details match
- Look for implementation evidence

## Database Structure for Real Agreements

```json
{
  "agreement_id": "EU-CN-2019-001",
  "title": "Official agreement title",
  "parties": {
    "eu_party": "Specific entity/country",
    "china_party": "Specific entity"
  },
  "date_signed": "2019-03-23",
  "type": "MOU|Treaty|Partnership",
  "status": "Active|Completed|Cancelled",
  "source": {
    "url": "Official announcement URL",
    "pdf": "Link to signed document",
    "verified": true,
    "verification_date": "2024-09-28"
  },
  "scope": "Brief description",
  "duration": "2019-2024"
}
```

## Realistic Expectations

### What We Can Actually Find
- Major government-to-government agreements (dozens, not thousands)
- Official BRI participation (handful of EU countries)
- Documented sister city partnerships (hundreds, not thousands)
- University agreements with paperwork (hundreds)

### What We Won't Find
- Thousands of agreements from URL patterns
- Secret or unannounced deals
- Agreements from commercial websites
- Valid data from spam sites

## Manual Review Process

### Phase 1: Official Sources Only
1. EUR-Lex database search
2. Chinese MOFCOM database
3. Each EU member's foreign ministry
4. Cross-reference findings

### Phase 2: Document Collection
1. Download actual agreement PDFs
2. Save official announcements
3. Archive press releases
4. Create source documentation

### Phase 3: Data Entry
1. Manual entry into structured database
2. Include all verification details
3. Note any conflicts/discrepancies
4. Mark verification status

## Time Estimate for Proper Research

- **EU-level agreements**: 1-2 days
- **27 member states**: 2-3 weeks (manual review)
- **Sister cities verification**: 1 week
- **University partnerships**: 1 week
- **BRI projects**: 3-4 days

**Total**: ~1 month of careful manual research

## Why This Approach Works

1. **Sources are authoritative** - No spam or false positives
2. **Agreements are real** - Actual documents, not URL patterns
3. **Data is verifiable** - Can be fact-checked
4. **Quality over quantity** - 100 real > 10,000 fake
5. **Legally meaningful** - Actual binding agreements

## Conclusion

Proper diplomatic research requires:
- Official sources
- Manual verification
- Document evidence
- Structured data entry
- Quality control

It cannot be automated through pattern matching on web crawls.

---

*This is the correct methodology. The Common Crawl approach was fundamentally flawed.*