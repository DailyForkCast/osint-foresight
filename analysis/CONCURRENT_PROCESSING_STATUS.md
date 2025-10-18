# Concurrent Processing Status
Generated: 2025-09-29 21:10

## Current Status

### OpenAlex Processing
- **Status**: RUNNING (Process ID: 028230)
- **Progress**: 800+ of 971 files processed
- **Data Source**: F:/OSINT_Backups/openalex/data/works (363GB)
- **What we're finding**: China-Europe academic collaborations
- **Processing rate**: ~100 files per minute

### TED Extraction
- **Status**: RUNNING (Process ID: be4a5d)
- **Progress**: Processing archive 2 of 139
- **Data Source**: F:/TED_Data/monthly/ (139 archives, ~30GB)
- **Structure**: Double-nested archives (tar.gz inside tar.gz)
- **Current**: Found 20 inner archives in TED_monthly_2024_12.tar.gz
- **Issue**: First archive (2024_08) was corrupted

## Data Discovery

### OpenAlex (Full Dataset Confirmed!)
We DO have the complete OpenAlex dataset:
- 422GB total in F:/OSINT_Backups/openalex/
- 2,938 compressed files
- 363GB of academic works data
- Contains: authors, institutions, works, concepts, domains, funders, etc.

### TED Archives
- 139 monthly archives (2006-2024)
- Each contains ~20 inner archives
- Each inner archive contains thousands of XML procurement notices
- Focus: EU public procurement with China connections

## Expected Outputs

1. **OpenAlex**: China-Europe collaboration database with:
   - Work IDs, titles, years
   - Institution names and countries
   - Research domains
   - DOIs for validation

2. **TED**: EU procurement contracts involving Chinese entities:
   - Contract values
   - Buyer/contractor details
   - CPV codes (procurement categories)
   - Temporal patterns

## Processing Strategy

Running both in parallel maximizes efficiency:
- OpenAlex: CPU-bound (JSON parsing)
- TED: I/O-bound (archive extraction)
- No resource contention

## Next Steps

1. Let both processes complete (est. 30-60 minutes)
2. Validate extracted data
3. Cross-reference findings
4. Generate comprehensive China-Europe interaction report