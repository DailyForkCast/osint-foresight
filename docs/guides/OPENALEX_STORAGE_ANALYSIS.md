# OpenAlex Data Storage Analysis

## OpenAlex Dataset Size
- **Total Size Required**: ~300GB
- **Format**: Compressed .gz files for each entity type (works, authors, institutions, sources, concepts)
- **Download Method**: AWS CLI (no AWS account needed)

## Storage Options Analysis

### Option 1: External Hard Drive (RECOMMENDED)
**Pros:**
- One-time cost (~$50-100 for 1-2TB drive)
- Full local access for processing
- No ongoing cloud storage fees
- Can process and extract only needed data

**Approach:**
1. Download to external drive using AWS CLI
2. Process locally to extract relevant countries/fields
3. Upload only processed subsets to BigQuery

**Commands:**
```bash
# Download to external drive (E:\ or similar)
aws s3 sync "s3://openalex" "E:/openalex-snapshot" --no-sign-request

# Later updates (removes deleted files)
aws s3 sync "s3://openalex" "E:/openalex-snapshot" --no-sign-request --delete
```

### Option 2: Google Cloud Storage
**Costs:**
- Storage: ~$6/month for 300GB (Standard tier)
- Data transfer to BigQuery: Free (same region)
- Egress (download): $0.12/GB if downloading back

**Not recommended** for full dataset due to ongoing costs.

### Option 3: Selective Download (BEST APPROACH)
Instead of downloading everything, selectively download only what you need:

1. **Works** - Filter by:
   - Publication year (2015-2025)
   - Author affiliations (AT, SK, IE, PT institutions)
   - Relevant concepts/topics

2. **Authors** - Only those affiliated with target countries
3. **Institutions** - Only target countries
4. **Sources** - Only relevant journals/conferences

## Recommended Approach

### Phase 1: External Drive Setup
```bash
# Install AWS CLI on Windows
pip install awscli

# Create directory on external drive
mkdir E:\openalex-snapshot

# Download specific entity types (start with smaller ones)
aws s3 sync "s3://openalex/data/institutions" "E:/openalex-snapshot/institutions" --no-sign-request
aws s3 sync "s3://openalex/data/sources" "E:/openalex-snapshot/sources" --no-sign-request
```

### Phase 2: Process Locally & Extract Relevant Data
Create Python scripts to:
1. Read compressed files
2. Filter for target countries
3. Extract only needed fields
4. Create smaller country-specific datasets

### Phase 3: Load to BigQuery
Upload only the processed, filtered data (~1-10GB) to BigQuery for analysis.

## BigQuery Storage Limits

### Free Tier:
- **10 GB storage/month free**
- **1 TB queries/month free**

### Your Project Capacity:
- **Storage**: Essentially unlimited (pay-as-you-go)
- **Cost**: $0.02/GB/month for active storage
- **Example**: 10GB filtered data = $0.20/month

## Recommendation

1. **DON'T** upload full 300GB OpenAlex to Google Cloud (would cost ~$6/month)
2. **DO** download to external hard drive ($50-100 one-time)
3. **DO** process locally to extract only relevant data
4. **DO** upload filtered datasets (1-10GB) to BigQuery for analysis

## Sample Processing Script

```python
import gzip
import json
from pathlib import Path

def filter_openalex_works(input_file, output_file, countries=['AT', 'PT', 'IE', 'SK']):
    """Extract works from specific countries"""

    with gzip.open(input_file, 'rt') as infile:
        with gzip.open(output_file, 'wt') as outfile:
            for line in infile:
                work = json.loads(line)

                # Check if any author is from target countries
                for authorship in work.get('authorships', []):
                    institutions = authorship.get('institutions', [])
                    for inst in institutions:
                        country = inst.get('country_code', '')
                        if country in countries:
                            outfile.write(line)
                            break

# Process in chunks
input_path = Path("E:/openalex-snapshot/data/works/")
output_path = Path("C:/Projects/OSINT - Foresight/data/openalex/")

for gz_file in input_path.glob("*.gz"):
    print(f"Processing {gz_file.name}...")
    filter_openalex_works(
        gz_file,
        output_path / f"filtered_{gz_file.name}",
        countries=['AT', 'PT', 'IE', 'SK']
    )
```

## Next Steps

1. **Get external drive** (1-2TB recommended)
2. **Install AWS CLI**: `pip install awscli`
3. **Start with smaller entities** (institutions, sources)
4. **Build filtering pipeline** for relevant data
5. **Upload processed data** to BigQuery

This approach minimizes costs while giving you full access to OpenAlex data!
