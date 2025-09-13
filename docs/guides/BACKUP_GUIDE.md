# OSINT Foresight Backup Guide

## Overview
Complete backup solution for the OSINT Foresight project with automated backups to external drive (F:).

## Backup Structure

```
F:\OSINT_Backups\
├── project\           # Current project mirror
├── archives\          # Weekly timestamped archives
└── openalex\         # OpenAlex data (future)
```

## Components

### 1. Main Backup Script: `simple_backup.py`
- **Purpose**: Incremental backup with smart file detection
- **Features**:
  - Skips unchanged files (compares timestamps)
  - Excludes large/regeneratable files
  - Creates weekly archives (Mondays)
  - Tracks backup statistics

### 2. Quick Backup: `backup_project.bat`
- **Purpose**: One-click manual backup
- **Usage**: Double-click to run backup immediately

### 3. Automated Backup: Task Scheduler
- **Schedule**: 
  - Daily at 9:00 PM
  - On system logon (5 min delay)
- **Setup**: Run `setup_automated_backup.bat` as Administrator

## What Gets Backed Up

### Included:
- All Python scripts (*.py)
- Documentation (*.md)
- Configuration files (*.yaml, *.yml, *.json)
- Source code (src/*)
- Scripts (scripts/*)
- Reports (reports/*)
- Processed data (data/processed/*)
- Queries (queries/*)

### Excluded:
- Python cache (__pycache__)
- Git objects (.git/objects)
- Virtual environments (venv, env)
- Raw data (data/raw/) - can be re-downloaded
- Large JSON files (out/SK/cordis_data/)
- Temporary files (*.tmp, *.log)

## Manual Backup Commands

```bash
# Run backup now
python simple_backup.py

# Or use the batch file
backup_project.bat

# Restore from backup
python simple_backup.py restore

# Run scheduled task manually
schtasks /run /tn "OSINT Foresight Backup"
```

## Monitoring Backups

### Check Last Backup
Look at `F:\OSINT_Backups\project\backup_info.json`:
```json
{
  "last_backup": "20250912_210000",
  "files_copied": 245,
  "files_skipped": 89,
  "total_size_mb": 45.2
}
```

### Check Scheduled Task Status
```cmd
schtasks /query /tn "OSINT Foresight Backup" /v
```

## Restore Procedures

### Full Restore
```bash
cd "C:\Projects\OSINT - Foresight"
python simple_backup.py restore
```

### Selective Restore
1. Navigate to `F:\OSINT_Backups\project\`
2. Copy specific files/folders back manually
3. Preserve file timestamps with copy options

### Restore from Archive
1. Find archive in `F:\OSINT_Backups\archives\`
2. Extract to temporary location
3. Run restore script or copy manually

## Storage Management

### Current Usage
- Project size: ~200 MB (excluding raw data)
- Backup size: ~50 MB (compressed, excludes unnecessary files)
- Weekly archives: ~20 MB each (zipped)

### Retention Policy
- Current backup: Always kept updated
- Weekly archives: Keep last 4 weeks
- Monthly archives: Keep last 3 months

### Cleanup Old Archives
```python
import os
from pathlib import Path
from datetime import datetime, timedelta

archive_dir = Path("F:/OSINT_Backups/archives")
cutoff_date = datetime.now() - timedelta(days=30)

for archive in archive_dir.glob("backup_*.zip"):
    # Parse timestamp from filename
    timestamp_str = archive.stem.replace("backup_", "")
    file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
    
    if file_date < cutoff_date:
        print(f"Removing old archive: {archive.name}")
        archive.unlink()
```

## Google Cloud Backup (Future)

Once billing is enabled on the GCS project:

1. Enable billing at: https://console.cloud.google.com/billing
2. Run `backup_manager.py` for GCS sync
3. Access backups at: `gs://osint-foresight-2025-backups/`

## Troubleshooting

### Backup Takes Too Long
- Check for large files in project
- Review exclude patterns in `simple_backup.py`
- Consider increasing exclusions

### Task Scheduler Not Running
1. Check Windows Event Viewer
2. Verify Python path in task
3. Run `setup_automated_backup.bat` as Administrator

### Drive Full
- Clean old archives
- Move OpenAlex data to separate partition
- Compress archives more aggressively

## Best Practices

1. **Test Restore Regularly**: Monthly restore test recommended
2. **Monitor Backup Logs**: Check `backup_info.json` weekly
3. **Verify Archives**: Test archive integrity quarterly
4. **Update Exclusions**: Add new large files to exclude list
5. **Document Changes**: Update this guide when modifying backup strategy

## Emergency Recovery

If both local and backup are corrupted:
1. Check Git repository for code
2. Re-pull data from sources (OpenAlex, CrossRef, etc.)
3. Re-run analysis pipeline
4. Restore reports from any exported versions

---

**Last Updated**: September 12, 2025
**Backup Version**: 1.0
**Contact**: OSINT Foresight Team