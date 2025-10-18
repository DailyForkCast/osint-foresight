# CORDIS Data Repository

## Overview
This folder contains CORDIS (Community Research and Development Information Service) data downloads, including Horizon Europe project information.

## Data Structure

### `/horizon/`
Contains Horizon Europe (2021-2027) project data:
- `cordis-HORIZONprojects-json.zip` - Main project dataset
- Individual JSON files after extraction:
  - `project.json` - Project details
  - `organization.json` - Participating organizations
  - `euroSciVoc.json` - Scientific vocabulary classifications
  - `topics.json` - Call topics
  - `webLink.json` - Project websites
  - `legalBasis.json` - Legal framework references

## Metadata
- **Source**: https://cordis.europa.eu/
- **License**: EU Open Data (Decision 2011/833/EU)
- **Last Updated**: 2025-08-12
- **Format**: JSON with JSON-LD metadata
- **Download URL**: https://cordis.europa.eu/data/cordis-HORIZONprojects-json.zip

## File Placement Instructions

1. **For the ZIP file**:
   Place `cordis-HORIZONprojects-json.zip` in:
   ```
   /data/raw/source=cordis/horizon/cordis-HORIZONprojects-json.zip
   ```

2. **After extraction**:
   Extract contents to:
   ```
   /data/raw/source=cordis/horizon/
   ```

3. **For additional CORDIS datasets** (FP7, H2020, etc.):
   Create parallel folders:
   ```
   /data/raw/source=cordis/fp7/
   /data/raw/source=cordis/h2020/
   ```

## Data Contents (from metadata)
- Horizon Europe projects (RCN, grant agreement numbers)
- Funding program details
- EuroSciVoc category associations
- Legal basis information
- Topics and calls
- Organizations (costs, coordinators, countries, participants)
- Project website links

## Processing Notes
- Data modified: 2025-08-12
- Compression: ZIP format
- Primary format: JSON
- Includes relationship data between entities

## Usage
```python
import json
import zipfile
from pathlib import Path

# Path to CORDIS data
cordis_path = Path("C:/Projects/OSINT - Foresight/data/raw/source=cordis/horizon")
zip_path = cordis_path / "cordis-HORIZONprojects-json.zip"

# Extract if needed
if zip_path.exists():
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(cordis_path)

# Load project data
with open(cordis_path / "project.json", 'r') as f:
    projects = json.load(f)
```

## Citation
```
European Commission. (2025). CORDIS - EU research projects under Horizon Europe (2021-2027).
Retrieved 2025-09-14, from https://cordis.europa.eu/data/cordis-HORIZONprojects-json.zip
```

---
*Created: 2025-09-14*
