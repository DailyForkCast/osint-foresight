# Prompt Archive System Documentation

## Overview
This directory uses an automated archive system to manage prompt files and prevent clutter while preserving important work.

## How It Works

### Automatic Archiving
- Files older than **72 hours** are automatically moved to the `archive/` folder
- Archive script: `archive_prompts.py`
- Configuration: `.prompt-archive-config`

### Protected Files (Never Archived)
The following files are permanently excluded from archiving:
- `Master_Prompt_vNext_Claude_Updates_FINAL.md` - Current master prompt
- `Deep_Research_Phase_Prompts.docx` - Phase templates
- All country-specific Deep Research prompts (Austria, Belgium, etc.)

### Archive Structure
```
docs/prompts/
├── archive/                     # Auto-archived files
│   ├── 20250906_filename.md    # Date-prefixed archived files
│   └── prompt_archive.log      # Archive operation log
├── .prompt-archive-config       # Configuration & exclusions
├── archive_prompts.py           # Archive script
└── [active prompt files]        # Current working prompts
```

## Usage

### Manual Archive Run
```bash
# Dry run (preview what would be archived)
python archive_prompts.py --dry-run

# Archive old files
python archive_prompts.py

# Force archive all eligible files (ignore age)
python archive_prompts.py --force
```

### Automatic Scheduling (Windows)
Create a scheduled task to run daily:
```powershell
# Create scheduled task (run as administrator)
schtasks /create /tn "PromptArchiver" /tr "python C:\Projects\OSINT - Foresight\docs\prompts\archive_prompts.py" /sc daily /st 02:00
```

### Automatic Scheduling (Linux/Mac)
Add to crontab:
```bash
# Edit crontab
crontab -e

# Add daily run at 2 AM
0 2 * * * cd /path/to/OSINT-Foresight/docs/prompts && python archive_prompts.py
```

## Configuration

### Modify Archive Settings
Edit `.prompt-archive-config`:
```ini
# Change archive threshold (default: 72 hours)
ARCHIVE_AFTER_HOURS=72

# Change archive folder name
ARCHIVE_FOLDER=archive

# Add files to exclude (one per line)
my_important_prompt.md
another_keeper.txt
```

## Recovery

### Restore Archived File
```bash
# Move file back from archive
mv archive/20250906_filename.md filename.md
```

### View Archive Log
```bash
# Check what was archived when
cat prompt_archive.log
```

## File Types Archived
- `.md` - Markdown files
- `.txt` - Text files
- `.docx` - Word documents

All other file types are ignored.

## Archive Naming Convention
Files are archived with date prefix:
- Format: `YYYYMMDD_originalname.ext`
- Example: `20250906_old_prompt.md`
- Duplicates: `YYYYMMDD_1_originalname.ext`

## Important Notes

1. **The archive script respects the exclusion list** - Files listed in `.prompt-archive-config` will NEVER be archived
2. **Archives are timestamped** - Original modification date is preserved in filename
3. **Subdirectories are not scanned** - Only files in `docs/prompts/` root are processed
4. **Archive folder is excluded** - Files already in `archive/` are never re-archived
5. **Logs are maintained** - Check `prompt_archive.log` for operation history

## Troubleshooting

### File Not Archiving
- Check if it's in the exclusion list (`.prompt-archive-config`)
- Verify it's older than 72 hours
- Ensure it has valid extension (.md, .txt, .docx)

### File Archived Too Soon
- Check system time/timezone
- Verify file modification date: `ls -la filename`

### Permission Errors
- Ensure write permissions on archive folder
- Close any open files in editors before archiving

## Manual Exclusion
To permanently exclude a file from archiving:
1. Open `.prompt-archive-config`
2. Add the filename on a new line
3. Save the file

Example:
```
# Add this line to .prompt-archive-config
my_permanent_prompt.md
```

---

*Archive system created: 2025-09-09*
*Maintains clean workspace while preserving all historical prompts*
