# Integration Guide for OSINT Foresight Improvements

## Quick Start

### 1. Install Dependencies
```bash
pip install aiohttp pyyaml pandas
```

### 2. Update Configuration Files

#### API Credentials (.env)
```bash
# European Patent Office
EPO_CLIENT_ID=your_client_id
EPO_CLIENT_SECRET=your_client_secret

# EU Portals
CORDIS_API_KEY=your_cordis_key
TED_API_KEY=your_ted_key

# Google BigQuery
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### 3. Import New Utilities

#### In Your Data Collection Scripts:
```python
# Add rate limiting to API calls
from src.utils.rate_limiter import RateLimiter, RateLimitConfig

config = RateLimitConfig(
    calls_per_second=10,
    burst_limit=20,
    daily_limit=100000
)
limiter = RateLimiter(config)

async def fetch_data():
    await limiter.acquire()
    # Your API call here
```

#### In Your Data Processing Scripts:
```python
# Standardize dates and confidence scores
from src.utils.standardization import (
    standardize_date,
    standardize_confidence,
    standardize_org_id
)

# Convert any date format to ISO 8601
clean_date = standardize_date("March 15, 2024")  # Returns: "2024-03-15"

# Normalize confidence scores
confidence = standardize_confidence("High")  # Returns: {"score": 0.85, "label": "High"}

# Standardize organization IDs
org_id = standardize_org_id("https://ror.org/02j61yw88", "ROR")  # Returns: "ROR:02j61yw88"
```

#### In Your Regional Analysis:
```python
# Get appropriate data sources for any country
from src.utils.regional_adapter import RegionalAdapter

adapter = RegionalAdapter()
sources = adapter.get_data_sources("SK", "procurement")
# Returns prioritized list of procurement sources for Slovakia

# Remove region-specific terminology
neutral_text = adapter.standardize_terminology(
    "The Horizon Europe project received TED tender"
)
# Returns: "The research framework programme project received public procurement notice"
```

### 4. Use Transaction-Safe Hub Operations

#### Promote Hubs Safely:
```bash
# Validate without making changes
make validate_promotion COUNTRY=SK

# Promote with automatic rollback on failure
make promote_hubs_safe COUNTRY=SK

# Rollback if needed
make rollback_promotion COUNTRY=SK
```

### 5. Validate Your Data

#### Check JSON Schema Compliance:
```python
import json
from jsonschema import validate

# Load schemas
with open('config/artifact_schemas.json') as f:
    schemas = json.load(f)

# Validate your data
phase_data = {"institutions": [...]}
validate(phase_data, schemas['schemas']['phase05_institutions'])
```

## Common Patterns

### Pattern 1: Rate-Limited API Collection
```python
async def collect_with_rate_limit(urls):
    config = RateLimitConfig(calls_per_second=5)
    limiter = RateLimiter(config)

    async def fetch(url):
        await limiter.acquire()
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    tasks = [fetch(url) for url in urls]
    return await asyncio.gather(*tasks)
```

### Pattern 2: Standardized Data Pipeline
```python
def process_record(raw_record):
    return {
        'id': standardize_org_id(raw_record.get('org_id')),
        'date': standardize_date(raw_record.get('date')),
        'confidence': standardize_confidence(raw_record.get('score')),
        'name': raw_record.get('name', '').strip()
    }

# Process all records with standardization
clean_data = [process_record(r) for r in raw_data]
```

### Pattern 3: Regional Source Selection
```python
def get_best_sources(country, source_type, count=3):
    adapter = RegionalAdapter()
    sources = adapter.get_data_sources(country, source_type)

    # Filter for free sources first
    free = [s for s in sources if not s.requires_auth]

    if len(free) >= count:
        return free[:count]

    # Add authenticated sources if needed
    return sources[:count]
```

## Troubleshooting

### Issue: Rate limit errors
**Solution**: Adjust rate limits in config/api_specifications.yaml

### Issue: Schema validation fails
**Solution**: Check against config/artifact_schemas.json definitions

### Issue: Hub promotion fails
**Solution**: Check logs, use validate_promotion first

### Issue: Dates not standardizing
**Solution**: Add pattern to DateStandardizer.PATTERNS

### Issue: Regional sources missing
**Solution**: Update config/data_sources_regional.yaml

## Best Practices

1. **Always validate before production**: Use schema validation
2. **Test rate limits**: Start conservative, increase gradually
3. **Backup before hub changes**: Automatic but verify
4. **Use regional adapter**: Don't hardcode sources
5. **Standardize early**: Clean data at ingestion
6. **Monitor API quotas**: Log rate limit usage
7. **Document exceptions**: When standardization fails

## Performance Tips

- Batch API calls to maximize rate limit efficiency
- Cache standardized values to avoid reprocessing
- Use async/await for concurrent API calls
- Pre-compile regex patterns for standardization
- Load schemas once, validate many times

---

For questions or issues, see the review artifacts in:
`artifacts/_review/CLAUDE_REVIEW/`
