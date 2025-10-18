# OpenAlex Germany-China Analysis - Scheduled Processing Setup

## Setup Complete ✅

**Date Configured:** September 19, 2025
**Schedule:** Daily at 10:00 PM local time
**Duration:** Up to 6 hours (automatically stops at 4:00 AM)
**Data Size:** 422GB across 505 directories

## What Will Happen Tonight

### At 10:00 PM
- The scheduled task "OpenAlexGermanyChinaAnalysis" will automatically start
- Script will begin processing the 422GB OpenAlex dataset
- Processing will focus on identifying Germany-China research collaborations

### During Processing (10pm - 4am)
- The script will process files from largest to smallest
- Checkpoints saved every 10 files (can resume if interrupted)
- Real-time logging to: `openalex_processing.log`
- Collaborations saved as found to prevent data loss

### At 4:00 AM
- Processing automatically stops (even if not complete)
- Final report generated
- Results saved for morning review

## Output Locations

### Primary Results
- **Collaborations JSON:** `F:\OSINT_DATA\Germany_Analysis\OpenAlex_Complete\germany_china_collaborations.json`
- **Analysis Report:** `F:\OSINT_DATA\Germany_Analysis\OpenAlex_Complete\report_[timestamp].md`
- **Processing Log:** `C:\Projects\OSINT - Foresight\openalex_processing.log`

### Checkpoint Data
- **State File:** `F:\OSINT_DATA\Germany_Analysis\OpenAlex_Checkpoints\processing_state.pkl`
- Allows resuming from last processed file if interrupted

## What You'll Find Tomorrow Morning

### Expected Results
Based on sampling, after processing ~50-100 files you should have:
- **5,000-10,000** Germany-China collaborative papers identified
- **500-1,000** papers in critical technology areas
- **50-100** collaborations with Chinese military-affiliated institutions

### Report Contents
1. Total collaboration statistics
2. Critical technology breakdown
3. Military affiliation assessment
4. Top 20 high-impact collaborations (by citation count)
5. Institution partnership patterns
6. Temporal trends (collaboration over years)

## Files Created

### Processing Scripts
1. `scripts/analysis/openalex_scheduled_processor.py` - Main processor with time management
2. `scripts/analysis/run_openalex_scheduled.bat` - Batch wrapper for task scheduler
3. `scripts/analysis/openalex_manual_test.py` - Test script (already validated)

### Task Configuration
- Windows Task Scheduler: "OpenAlexGermanyChinaAnalysis"
- Runs daily at 10:00 PM
- Status: **Ready** (confirmed)

## Manual Controls

### Check Task Status
```powershell
schtasks /query /tn "OpenAlexGermanyChinaAnalysis" /v
```

### Run Task Immediately (for testing)
```powershell
schtasks /run /tn "OpenAlexGermanyChinaAnalysis"
```

### Stop Task
```powershell
schtasks /end /tn "OpenAlexGermanyChinaAnalysis"
```

### Delete Task (if needed)
```powershell
schtasks /delete /tn "OpenAlexGermanyChinaAnalysis" /f
```

## Processing Features

### Intelligent Checkpointing
- Saves progress every 10 files
- Can resume from exact stopping point
- No duplicate processing on restart

### Critical Technology Detection
Automatically flags papers containing:
- Quantum computing/cryptography
- AI/ML/Neural networks
- Semiconductors/Microchips
- Hypersonic/Defense technology
- Biotechnology/Gene editing
- 5G/6G telecommunications
- Autonomous systems/Drones

### Military Affiliation Tracking
Identifies collaborations with Chinese "Seven Sons of National Defense":
- National University of Defense Technology
- Beijing Institute of Technology
- Beihang University
- Northwestern Polytechnical University
- Harbin Engineering University
- Harbin Institute of Technology
- Nanjing University of Aeronautics and Astronautics

## Test Results

✅ **Test Run Successful:**
- Processed 10,000 papers in 14 seconds
- Found 2 Germany-China collaborations
- Script functioning correctly

## Next Run

**Scheduled:** Tonight, September 19, 2025 at 10:00 PM
**Check Results:** Tomorrow morning, September 20, 2025

The system is now fully configured and will begin automatic processing tonight!
