# USASpending China Analysis - Full File Scan Status

## Current Status
**Started:** September 26, 2025, 6:30 PM
**Data Volume:** 660.57 GB across 5 files
**Total Lines:** ~1.24 billion lines

## Scan Configuration
The refined_full_scanner.py is processing EVERY line with the following rules:

### EXCLUDED (U.S. Locations - False Positives)
- China Lake, California (Naval Air Weapons Station)
- China Spring, Texas
- China Grove, North Carolina
- China Beach, China Creek, China Point, China Camp (various U.S. locations)

### INCLUDED (Chinese Activity IN the U.S.)
1. **Chinese Companies Operating in U.S.**
   - Huawei USA, ZTE America
   - TikTok, ByteDance
   - Lenovo, TCL, Haier operations
   - WeChat usage

2. **Chinese Government Presence**
   - Embassy of China
   - Chinese Consulates
   - Government delegations

3. **Chinese Ownership/Investment**
   - Chinese-owned companies
   - Chinese investors
   - Subsidiaries of Chinese firms

4. **Trade & Commerce**
   - Imports from China
   - Exports to China
   - Made in China products
   - Chinese suppliers

5. **Research Collaboration**
   - Chinese universities
   - Chinese researchers
   - Collaborative projects

6. **MCF (Military-Civil Fusion) Entities**
   - NORINCO, AVIC, CASIC, CASC
   - CETC, CSSC, CSIC
   - Nuctech, Hytera
   - Inspur, Sugon
   - iFlytek, SenseTime, Megvii

## Files Being Processed

| File | Size (GB) | Lines | Est. Time | Status |
|------|-----------|-------|-----------|--------|
| 5848.dat | 222.45 | 98.4M | ~37 min | Processing |
| 5801.dat | 134.85 | 249M | ~22 min | Processing |
| 5836.dat | 124.72 | 131M | ~21 min | Processing |
| 5847.dat | 126.50 | 101M | ~21 min | Processing |
| 5862.dat | 52.05 | 663M | ~9 min | Processing |

## Expected Outputs
Each file will produce `smart_scan_[file].json` containing:
- Total China references (excluding U.S. locations)
- Chinese activity specifically IN the U.S.
- MCF entity mentions
- Company mentions with counts
- Location references
- Sample records for verification

## Processing Architecture
- 5 concurrent Python processes (PIDs tracked)
- Each processing entire file, no sampling
- Progress reports every 1M lines or 30 seconds
- Output includes first 10,000 China references for analysis

## Evidence Standards
Per user requirement: "NO FABRICATION NO GUESSWORK"
- Every China reference has line number
- Sample text preserved for verification
- Pattern that matched is recorded
- False positives explicitly counted and excluded

## Monitor Command
```bash
python monitor_china_scans.py  # Running in background
python quick_status.py         # Quick status check
```

## Next Steps
Once all 5 files complete:
1. Compile total China references across all files
2. Categorize Chinese activity IN the U.S.
3. Identify top MCF entities and companies
4. Generate evidence-based report with provenance
5. Store results in PostgreSQL database for queries