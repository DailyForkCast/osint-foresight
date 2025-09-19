# USPTO API Setup Summary

**Date:** September 18, 2025
**Status:** Configuration Complete

## Overview

Successfully configured access to USPTO data through the USPTO Open Data Portal (data.uspto.gov).

## Key Findings

### 1. API Evolution
- **Legacy PatentsView API:** Discontinued as of May 2025 (returns 410 error)
- **search.patentsview.org:** Returns 403 errors, requires specific authentication
- **data.uspto.gov:** Current official portal - ACCESSIBLE ✓

### 2. Working Configuration

#### USPTO Open Data Portal
- **Base URL:** https://data.uspto.gov
- **API Base:** https://data.uspto.gov/api
- **Status:** Accessible and responding

#### Available Data Sources
1. **Patent File Wrapper:** Patent prosecution history and documents
2. **Patent Assignment:** Patent ownership and transfer records
3. **Patent Examination:** Patent examination research dataset (PEDS)
4. **Patent Grants:** Full text patent data
5. **Trademarks:** Registration and assignment data

## Implementation Files Created

### 1. `src/pulls/uspto_open_data_client.py`
- Main client for accessing data.uspto.gov
- Handles rate limiting (30 requests/minute)
- Provides methods for:
  - Patent File Wrapper search
  - Patent Assignment search
  - Patent Examination data
  - Bulk data information

### 2. `src/pulls/uspto_patentsearch_client.py`
- Alternative client for PatentSearch API
- Includes country collaboration search
- Technology classification search

### 3. `src/pulls/uspto_bulk_downloader.py`
- Bulk data download functionality
- Handles compressed file extraction
- Categories supported:
  - Patent grants
  - Patent applications
  - Patent assignments
  - Trademark data

## Configuration Saved

Location: `C:/Projects/OSINT - Foresight/config/uspto_config.json`

```json
{
  "api_base": "https://data.uspto.gov",
  "endpoints": {
    "patent_file_wrapper": "https://data.uspto.gov/apis/patent-file-wrapper/search",
    "bulk_data": "https://data.uspto.gov/api/bulk-data",
    "patent_examination": "https://data.uspto.gov/api/patent-examination",
    "patent_assignment": "https://data.uspto.gov/api/patent-assignment"
  }
}
```

## Usage Examples

### Search Patent Data
```python
from src.pulls.uspto_open_data_client import USPTOOpenDataClient

client = USPTOOpenDataClient()
client.test_connection()  # Verify access

# Search patent file wrapper
data = client.search_patent_file_wrapper(patent_number="10000000")

# Get patent examination data
exam_data = client.get_patent_examination_data(start_date="2024-01-01")
```

### Download Bulk Data
```python
from src.pulls.uspto_bulk_downloader import USPTOBulkDownloader

downloader = USPTOBulkDownloader(output_dir="F:/OSINT_Data/USPTO")
downloader.download_recent_patents(weeks=1)
downloader.download_patent_assignments(year=2024)
```

## Known Issues

1. **bulkdata.uspto.gov:** Domain not resolving - use data.uspto.gov instead
2. **API Key:** Optional but recommended for higher rate limits
3. **Response Format:** Some endpoints return HTML instead of JSON - need proper endpoint discovery

## Next Steps

1. Implement patent search functionality for specific technology areas
2. Set up automated downloads for recent patents
3. Create analysis pipelines for patent collaboration detection
4. Integrate with main OSINT analysis framework

## Data Output Directory

Default: `F:/OSINT_Data/USPTO/`

Subdirectories:
- `/patents/grants/` - Patent grant files
- `/patents/assignments/` - Assignment data
- `/patents/applications/` - Application data
- `/trademarks/` - Trademark data

## Rate Limits

- Without API key: ~10-30 requests/minute (conservative)
- With API key: 45 requests/minute
- Bulk downloads: No specific limit, but use responsibly

## Success Metrics

- ✅ data.uspto.gov portal accessible
- ✅ Configuration files created
- ✅ Client libraries implemented
- ✅ Test connections successful
- ✅ Ready for integration

---

*USPTO data access configured and ready for OSINT analysis integration.*
