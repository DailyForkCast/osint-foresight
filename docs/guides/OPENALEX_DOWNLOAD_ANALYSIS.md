# OpenAlex Download Analysis

## Current Status

Based on your download output:
```
Completed 287.7 GiB/~297.0 GiB (7.4 MiB/s) with ~17 file(s) remaining (calculating...)
```

### Progress Summary
- **Downloaded**: 287.7 GiB of ~297.0 GiB
- **Percentage Complete**: ~96.9%
- **Remaining**: ~9.3 GiB
- **Files Remaining**: ~17 files
- **Current Speed**: 7.4 MiB/s
- **Estimated Time to Complete**: ~21 minutes (at current speed)

### What's Happening

You're downloading the OpenAlex "works" dataset for August 14, 2025. The download appears to be:
1. **Nearly complete** (96.9% done)
2. **Still actively downloading** (showing current transfers)
3. **Working on the final batch** of files

The files being downloaded are:
- Individual parts of the works dataset (part_002.gz, part_003.gz, etc.)
- Each part is compressed (`.gz` format)
- Target location: `F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\`

## Why It Shows Both Complete and Ongoing

This is normal AWS S3 sync behavior:
1. **Progress bar** shows overall completion (287.7/297.0 GiB)
2. **File list** shows currently transferring files
3. **"~17 files remaining"** indicates it's in the final batch
4. **"calculating..."** means it's dynamically updating the count

## Recommendations

### Immediate Actions
1. **Let it complete** - You're 96.9% done, only ~21 minutes remaining
2. **Monitor for completion** - Watch for "Completed 297.0 GiB/297.0 GiB"
3. **Don't interrupt** - Interrupting now would require re-checking all files

### After Completion
1. **Verify integrity**:
   ```bash
   # Count downloaded files
   find F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\ -name "*.gz" | wc -l

   # Check total size
   du -sh F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\
   ```

2. **Check for any failed transfers**:
   ```bash
   # AWS CLI will report any failures at the end
   # Look for lines like "failed: s3://..."
   ```

3. **Document the download**:
   ```bash
   # Create a manifest
   ls -la F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\ > openalex_manifest.txt
   ```

## Understanding OpenAlex Data Structure

### Works Dataset
- **What it contains**: Academic papers, preprints, datasets, etc.
- **Update frequency**: Daily snapshots
- **Size**: ~300GB compressed per snapshot
- **Format**: JSONL (JSON Lines) compressed with gzip

### File Organization
```
openalex/
└── data/
    └── works/
        └── updated_date=YYYY-MM-DD/
            ├── part_000.gz
            ├── part_001.gz
            ├── part_002.gz
            └── ... (typically 100-200 parts)
```

### Next Downloads to Consider
After completing the works dataset, you might want:
1. **Authors** dataset (~30GB)
2. **Institutions** dataset (~5GB)
3. **Concepts** dataset (~2GB)
4. **Venues** dataset (~1GB)
5. **Publishers** dataset (~500MB)

## Storage Considerations

### Current Usage
- **Downloaded**: 287.7 GiB for one day's snapshot
- **Uncompressed size**: ~1.2-1.5 TB (compression ratio ~4-5x)

### Planning for Multiple Dates
If downloading multiple dates:
- Each date = ~300GB compressed
- 30 days = ~9TB compressed
- Consider incremental updates instead of full snapshots

## Optimization Tips

### For Future Downloads
1. **Use parallel transfers**:
   ```bash
   aws s3 sync s3://openalex/ F:\OSINT_Backups\openalex\ --cli-write-timeout 0 --cli-read-timeout 0 --concurrent-requests 10
   ```

2. **Download only updates**:
   ```bash
   # After initial download, use --size-only flag
   aws s3 sync s3://openalex/ F:\OSINT_Backups\openalex\ --size-only
   ```

3. **Filter by date range**:
   ```bash
   # Download only recent updates
   aws s3 sync s3://openalex/data/works/ F:\OSINT_Backups\openalex\data\works\ --exclude "*" --include "*updated_date=2025-08*"
   ```

## Processing the Data

Once downloaded, you'll need to:
1. **Decompress files** (selectively, as needed)
2. **Parse JSONL format**
3. **Filter for your countries of interest**
4. **Extract relevant fields**

### Sample Processing Script
```python
import gzip
import json
from pathlib import Path

def process_openalex_part(filepath):
    """Process a single OpenAlex part file"""
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        for line in f:
            work = json.loads(line)
            # Filter for your criteria
            if has_relevant_affiliation(work):
                yield extract_relevant_fields(work)

def has_relevant_affiliation(work):
    """Check if work has affiliations from countries of interest"""
    countries = ['AT', 'SK', 'PT', 'IE']  # Your target countries
    for authorship in work.get('authorships', []):
        for institution in authorship.get('institutions', []):
            if institution.get('country_code') in countries:
                return True
    return False
```

## Summary

Your download is **nearly complete** and proceeding normally. The mixed messages (both complete and ongoing) are standard for large S3 transfers. Let it finish the remaining 17 files (~9.3 GiB), then verify the download and plan your data processing strategy.
