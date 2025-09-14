# OpenAlex Download Recovery Guide - Frozen Transfer

## Current Situation
- Download frozen at 287.7 GiB/~297.0 GiB (96.9% complete)
- No progress for 20+ minutes
- ~17 files remaining
- Last seen downloading part_002.gz, part_003.gz, part_004.gz, part_007.gz

## Immediate Actions

### 1. SAFELY INTERRUPT (Ctrl+C)
Press `Ctrl+C` once to gracefully stop the AWS CLI. This is safe because:
- AWS S3 sync is resumable
- Already downloaded files won't be re-downloaded
- No data corruption risk

### 2. CHECK WHAT YOU HAVE
Open a new terminal/command prompt and run:
```bash
# Check how many files were successfully downloaded
dir F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\*.gz | measure

# Or in PowerShell
(Get-ChildItem F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\*.gz).Count

# Check total size on disk
# In Windows Explorer: Right-click the folder → Properties
```

### 3. RESUME THE DOWNLOAD
Run the sync command again with optimized parameters:

```bash
# Resume with timeout and retry settings
aws s3 sync s3://openalex/data/works/updated_date=2025-08-14/ ^
  F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\ ^
  --no-sign-request ^
  --cli-read-timeout 300 ^
  --cli-connect-timeout 60 ^
  --cli-write-timeout 300 ^
  --max-concurrent-requests 5 ^
  --max-bandwidth 50MB/s

# Note: ^ is line continuation for Windows CMD
# For PowerShell use ` instead of ^
```

## Why Downloads Freeze

### Common Causes:
1. **Network congestion** - ISP throttling or routing issues
2. **AWS S3 rate limiting** - Too many concurrent requests
3. **Large file issue** - One particularly large part file
4. **Memory/buffer issue** - System running low on resources
5. **Antivirus interference** - Real-time scanning blocking writes

## Recovery Strategy

### Option A: Resume with Lower Concurrency (RECOMMENDED)
```bash
# More conservative settings
aws s3 sync s3://openalex/data/works/updated_date=2025-08-14/ ^
  F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\ ^
  --no-sign-request ^
  --max-concurrent-requests 2 ^
  --max-bandwidth 25MB/s
```

### Option B: Download Missing Files Individually
First, identify what's missing:
```bash
# List remote files
aws s3 ls s3://openalex/data/works/updated_date=2025-08-14/ --no-sign-request > remote_files.txt

# List local files
dir F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\ /b > local_files.txt

# Compare to find missing files
```

Then download specific missing files:
```bash
# Download individual files
aws s3 cp s3://openalex/data/works/updated_date=2025-08-14/part_002.gz ^
  F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\part_002.gz ^
  --no-sign-request
```

### Option C: Use --exclude/--include Patterns
```bash
# Skip already downloaded files explicitly
aws s3 sync s3://openalex/data/works/updated_date=2025-08-14/ ^
  F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\ ^
  --no-sign-request ^
  --exclude "*" ^
  --include "part_00[2-9].gz" ^
  --include "part_0[1-9]*.gz"
```

## Verification After Recovery

### 1. Count Files
```bash
# Expected: Should see ~100-200 part files
dir F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\part_*.gz | measure
```

### 2. Check File Sizes
```bash
# No file should be 0 bytes
dir F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\*.gz | where {$_.Length -eq 0}
```

### 3. Test Random Files
```python
# Python script to test file integrity
import gzip
import json
from pathlib import Path

def test_gz_files(directory):
    failed = []
    for gz_file in Path(directory).glob("*.gz"):
        try:
            with gzip.open(gz_file, 'rt') as f:
                # Read first line to test
                first_line = f.readline()
                json.loads(first_line)  # Test if valid JSON
            print(f"✓ {gz_file.name}")
        except Exception as e:
            print(f"✗ {gz_file.name}: {e}")
            failed.append(gz_file.name)

    if failed:
        print(f"\nFailed files: {failed}")
        print("Re-download these files")
    else:
        print("\nAll files valid!")

test_gz_files(r"F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14")
```

## Prevention for Future Downloads

### 1. Use a Download Script with Retry Logic
```python
import subprocess
import time

def download_with_retry(s3_path, local_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}")
            result = subprocess.run([
                'aws', 's3', 'sync',
                s3_path, local_path,
                '--no-sign-request',
                '--max-concurrent-requests', '3',
                '--cli-read-timeout', '300'
            ], check=True, timeout=3600)  # 1 hour timeout

            if result.returncode == 0:
                print("Download completed successfully!")
                return True

        except subprocess.TimeoutExpired:
            print(f"Timeout on attempt {attempt + 1}")
            time.sleep(60)  # Wait 1 minute before retry
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            time.sleep(60)

    return False

# Use it
success = download_with_retry(
    's3://openalex/data/works/updated_date=2025-08-14/',
    r'F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14'
)
```

### 2. Download in Batches
```bash
# Download in chunks by file pattern
# First batch: part_000 to part_050
aws s3 sync s3://openalex/data/works/updated_date=2025-08-14/ ^
  F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\ ^
  --no-sign-request ^
  --exclude "*" ^
  --include "part_0[0-4]*.gz" ^
  --include "part_050.gz"

# Second batch: part_051 to part_100
# ... and so on
```

### 3. Monitor System Resources
Before starting large downloads:
- Close unnecessary applications
- Disable antivirus real-time scanning for the target folder
- Ensure sufficient disk space (need ~1.5TB for uncompressed)
- Check network stability with `ping 8.8.8.8 -t`

## Quick Recovery Commands

```bash
# 1. STOP current download
Ctrl+C

# 2. RESUME with better settings
aws s3 sync s3://openalex/data/works/updated_date=2025-08-14/ ^
  F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\ ^
  --no-sign-request ^
  --max-concurrent-requests 2

# 3. VERIFY completion
dir F:\OSINT_Backups\openalex\data\works\updated_date=2025-08-14\*.gz | measure
```

## Summary

Your download is frozen at 96.9% - frustrating but recoverable! The safest approach:
1. **Ctrl+C** to stop
2. **Resume with lower concurrency** (2-3 concurrent requests)
3. **Let AWS S3 sync figure out** what's missing
4. **Verify** file count and integrity after completion

The download WILL resume from where it left off - you won't lose the 287.7 GiB already downloaded!
