# The Lens API Application Guide

## Important: API Access Requires Application

The Lens API is not immediately available after registration. You must apply for access and be approved.

## Application Process

### Step 1: Create Account First
1. Register at https://www.lens.org
2. Verify your email
3. Sign in to your account

### Step 2: Apply for API Access
1. Once signed in, navigate to API section
2. Select the APIs you need:
   - **Scholarly API** - 70+ metadata fields, interoperable with DOI, PubMed, OpenAlex
   - **Patent API** - 120+ metadata fields, 105 jurisdictions
   - **PatSeq Bulk Data** - Genetic sequences in patents
3. Click "Request Access" for each

### Step 3: Complete Application Form

**Key Information to Provide:**

#### Use Case Description (for OSINT Foresight Project)
```
Project: OSINT Foresight - Technology Transfer Risk Assessment
Purpose: Analyzing technology transfer patterns between Italy and China,
focusing on dual-use technologies and supply chain vulnerabilities.

Specific needs:
- Track patent filings by Italian companies with Chinese connections
- Identify scholarly research cited in patents (patent-to-science linkage)
- Map collaboration networks between Italian and Chinese institutions
- Monitor technology emergence and knowledge flows

Non-commercial research use for strategic intelligence assessment.
```

#### Organization Type
- Government research / Strategic analysis
- Non-commercial use
- Academic/research purpose

#### Data Requirements
- Patent search with Italy/China filters
- Scholarly works cited in patents
- Bulk export up to 50,000 records
- Cross-referencing with EU funding (CORDIS)

### Step 4: Request 14-Day Trial
- All API users entitled to 14-day trial
- Mention this explicitly in application
- Use trial to validate data suitability

### Step 5: While Waiting for Approval

#### Use Web Interface Features (Available Now)
1. **Manual Searches:**
   - Search for Leonardo patents
   - Italy-China collaborations
   - Export up to 50,000 records via web

2. **Create Collections:**
   - Save important patent sets
   - Set up email alerts
   - Monitor new filings

3. **Example Searches to Run:**
```
Leonardo patents:
applicant.name:"Leonardo" OR applicant.name:"Leonardo S.p.A"

Italy-China collaborations:
(inventor.country:IT AND applicant.country:CN) OR
(inventor.country:CN AND applicant.country:IT)

Dual-use technologies:
cpc.symbol:H04L* AND (applicant.country:IT OR inventor.country:IT)
```

## Expected Timeline

- **Application submission:** Immediate
- **Confirmation email:** Within 24 hours
- **Evaluation period:** 2-5 business days
- **Trial access:** Upon approval
- **Full access decision:** After 14-day trial

## Alternative Actions While Waiting

### 1. Use Web Export Feature
- Can export 50,000 records without API
- CSV, JSON, RIS formats available
- Create collections and export

### 2. Set Up Infrastructure
```python
# Prepare environment variables in .env.local
LENS_API_TOKEN=pending_approval
LENS_API_TYPE=trial  # or full
LENS_RATE_LIMIT=50000  # monthly for scholarly
```

### 3. Prepare Search Queries
```python
# Key searches for Italy analysis
queries = {
    "leonardo_global": {
        "applicant": "Leonardo",
        "date_from": "2015-01-01"
    },
    "italy_china_collab": {
        "inventor_country": "IT",
        "applicant_country": "CN"
    },
    "politecnico_patents": {
        "applicant": "Politecnico di Milano",
        "date_from": "2018-01-01"
    }
}
```

## Application Tips

### DO Emphasize:
- Non-commercial research purpose
- Government/strategic intelligence needs
- Technology transfer risk assessment
- Italy-China focus (specific, not broad)
- Integration with existing OSINT tools

### DON'T:
- Mention commercial use
- Request excessive data volumes initially
- Be vague about purpose
- Forget to request 14-day trial

## Backup Plan if Not Approved

### Continue Using:
1. **Web interface** - Still powerful with 50K export
2. **Google Patents BigQuery** - Already have access
3. **Espacenet** - Web searching
4. **OECD databases** - Statistical data

### The Lens Web Features (No API Needed):
- Advanced search with filters
- Export 50,000 records per batch
- Create and share collections
- Set up email alerts
- View patent families
- Access PatCite (citation tracking)

## Contact for Questions

If application pending too long:
- Email: support@lens.org
- Mention: Government research project
- Reference: Technology transfer assessment

## Once Approved

### Update Configuration:
```bash
# Add to .env.local
LENS_API_TOKEN=your_actual_token_here
LENS_API_TIER=trial  # or professional
```

### Test API Access:
```python
python scripts/lens_api_client.py
```

### Priority Data Collections:
1. Leonardo complete patent portfolio
2. Italy-China collaboration patents (2015-2025)
3. Politecnico di Milano patents
4. Patents citing Italian research papers
5. Chinese companies citing Italian patents

---

## Summary Actions

### Immediate (Today):
1. ✅ Create Lens account
2. ✅ Apply for API access (Scholarly + Patent)
3. ✅ Request 14-day trial explicitly
4. ✅ Start using web interface for searches

### This Week:
1. Export first dataset via web (no API needed)
2. Create patent collections
3. Set up email alerts
4. Await API approval

### Upon Approval:
1. Add token to .env.local
2. Run lens_api_client.py
3. Bulk export priority datasets
4. Integrate with existing pipeline

---

*Remember: The web interface alone provides significant value even without API access*
