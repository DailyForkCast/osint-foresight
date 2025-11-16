# Lens.org API Setup Instructions

**Goal**: Validate remaining 10 entities using Chinese patents from Lens.org

---

## Step 1: Get Your API Token (You're Here!)

1. ✅ You have a Lens.org account
2. 🔄 Get your API token:
   - Go to: https://www.lens.org/lens/user/subscriptions
   - Click "Request" or "Generate Token"
   - Copy the token (it will look like: `eyJ0eXAiOiJKV1QiLCJhbGc...`)

---

## Step 2: Add Token to .env File

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your token
# Replace 'your_lens_api_token_here' with your actual token
```

Your `.env` file should look like:
```
LENS_API_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGc...your_actual_token_here
```

**IMPORTANT**:
- Don't commit `.env` to git (it's already in .gitignore)
- Keep your token secret

---

## Step 3: Install Required Python Package

```bash
# Install python-dotenv if not already installed
pip install python-dotenv
```

---

## Step 4: Run Basic API Test

```bash
python test_lens_api.py
```

**Expected output:**
```
================================================================================
LENS.ORG API TEST
================================================================================

Test 1: Checking API connectivity...
SUCCESS: API connection working!
Status: 200

Test 2: Searching for CATL (Contemporary Amperex) Chinese patents...

Found 637 Chinese patents for Contemporary Amperex

Sample patents:
1. CN115332571A (2022-11-11)
   Battery cell, battery, power consumption device and method for manufacturing...

SUCCESS: Chinese patent search working!

Test 3: Checking API quota...

================================================================================
API TEST COMPLETE
================================================================================
```

**If you see errors:**
- `401 Unauthorized`: Check your API token is correct
- `Connection failed`: Check internet connection
- `No module named 'dotenv'`: Run `pip install python-dotenv`

---

## Step 5: Test All 10 Non-Validated Entities

```bash
python test_lens_entities.py
```

This will search for Chinese patents for:
- CCTC
- CSTC
- China Cargo Airlines
- China Shipping Group
- CloudWalk
- GTCOM
- Geosun
- JOUAV
- Quectel
- Sinotrans

**Expected runtime**: 2-5 minutes (includes rate limiting delays)

**Expected output:**
```
Searching: CloudWalk
--------------------------------------------------------------------------------
  [FOUND] 'CloudWalk': 45 Chinese patents
  [FOUND] 'Cloudwalk Technology': 45 Chinese patents

  BEST MATCH: 'CloudWalk' with 45 patents
  Sample patents:
    - CN112560737A: Face recognition method, device, electronic equipment and sto...
    - CN112528863A: Living body detection method, living body detection device, e...

...

================================================================================
SUMMARY
================================================================================

Entities tested: 10
Entities found: 5
New validation rate projection: 91.9%

NEWLY VALIDATABLE:
  - CloudWalk: 45 patents via 'CloudWalk'
  - GTCOM: 23 patents via 'Global Tone Communication'
  - Quectel: 156 patents via 'Quectel'
  ...
```

---

## Step 6: Integrate Results into Database

Once we confirm which entities have Chinese patents:

```bash
# This will be created after we see the results
python integrate_lens_patents.py
```

This will:
1. Add Chinese patent counts to our database
2. Update validation status
3. Re-calculate validation rate
4. Generate final report

---

## Expected Impact

| Scenario | Entities Found | New Validation | Status |
|----------|----------------|----------------|--------|
| Best case | 5-6 entities | 57-58/62 (92-94%) | ✅ Exceeds 90% target! |
| Good case | 3-4 entities | 55-56/62 (89-90%) | ✅ Reaches 90% target |
| Moderate | 1-2 entities | 53-54/62 (85-87%) | ⚠️ Need Semantic Scholar too |

---

## Troubleshooting

### Issue: Rate Limit (HTTP 429)
```
Solution: Script automatically waits 60 seconds and retries
If persistent: Reduce batch size or add longer delays
```

### Issue: No Results Found
```
Possible reasons:
1. Entity may not file Chinese patents
2. Filed under different name/romanization
3. Recently founded (patents not yet published)

Next step: Try Semantic Scholar for research papers
```

### Issue: Token Expired
```
Solution: Generate new token at https://www.lens.org/lens/user/subscriptions
Update .env file with new token
```

---

## API Rate Limits (Free Tier)

- **Requests per day**: Varies by account type
- **Requests per minute**: ~10-20 (unofficial)
- **Results per query**: Up to 1000

Our script is conservative:
- 0.5 second delay between requests
- Handles 429 errors gracefully
- Should stay well within limits

---

## Next Steps After Lens.org

If we still need more entities to reach 90%:

1. **Semantic Scholar API** (no token needed for basic use)
   ```bash
   python test_semantic_scholar.py
   ```

2. **Google Patents manual checks** (for verification)

3. **Accept realistic limits** (some entities may not be publicly validatable)

---

## Files Created

- ✅ `.env.example` - Template for environment variables
- ✅ `test_lens_api.py` - Basic API connectivity test
- ✅ `test_lens_entities.py` - Search all 10 entities
- ⏳ `integrate_lens_patents.py` - Will create after seeing results
- ⏳ `validate_with_lens_data.py` - Final validation with Lens data

---

## Support

**Lens.org Documentation**: https://docs.api.lens.org/
**API Status**: https://status.lens.org/
**Support**: support@lens.org

**Project Status**: Ready to test as soon as you have the API token!

---

**Ready?** Once you have your token, just:
1. Add it to `.env`
2. Run `python test_lens_api.py`
3. If successful, run `python test_lens_entities.py`
4. Share the results!
