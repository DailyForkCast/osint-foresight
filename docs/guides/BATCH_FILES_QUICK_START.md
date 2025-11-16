# UN Comtrade Batch Files - Quick Start Guide

**Easy Windows automation for UN Comtrade collection**

---

## Main Menu (Easiest!)

**Double-click:** `COMTRADE_MENU.bat`

This opens an interactive menu with all options:
- Test API (run first!)
- Check status
- Start Phase 1
- Start in background
- Setup scheduled task
- View logs
- Open docs

**Recommended:** Use this menu for everything!

---

## Individual Batch Files

If you prefer to run specific tasks directly:

### 1. Test API First

**Double-click:** `TEST_COMTRADE_API.bat`

- Makes 5 test requests
- Takes ~15 seconds
- Verifies API is working
- **Run this first before starting collection!**

### 2. Start Phase 1 Collection

**Double-click:** `START_COMTRADE_PHASE1.bat`

- Runs Phase 1 (Core Technologies)
- Duration: 6-8 hours
- Collects 60K-300K records
- Shows progress in window
- Safe to close window (progress saved)

### 3. Start in Background

**Double-click:** `START_COMTRADE_BACKGROUND.bat`

- Runs collection in background (minimized)
- Resumes from checkpoint automatically
- Window closes immediately
- Collection continues running
- Check status with `CHECK_COMTRADE_STATUS.bat`

### 4. Check Status

**Double-click:** `CHECK_COMTRADE_STATUS.bat`

- Shows current progress
- Records collected
- Current phase
- Time remaining
- Database statistics

### 5. Setup Scheduled Task

**Right-click → Run as Administrator:** `SCHEDULE_DAILY_COLLECTION.bat`

- Creates Windows scheduled task
- Runs daily at 10:00 PM
- Automatically resumes from checkpoint
- Runs in background
- **Requires Administrator privileges**

---

## Usage Examples

### First Time Setup (Recommended)

1. **Double-click:** `COMTRADE_MENU.bat`
2. Choose option `1` - Test API
3. Verify it works
4. Choose option `3` - Start Phase 1
5. Let it run (can close window)
6. Check progress: Run menu again, choose option `2`

### Daily Automated Collection

1. **Right-click → Run as Administrator:** `SCHEDULE_DAILY_COLLECTION.bat`
2. Confirm task creation
3. Collection will now run every day at 10 PM
4. Check progress anytime: Double-click `CHECK_COMTRADE_STATUS.bat`

### Manual Background Collection

1. **Double-click:** `START_COMTRADE_BACKGROUND.bat`
2. Collection starts in background
3. Check status: `CHECK_COMTRADE_STATUS.bat`
4. View logs: `logs\comtrade_collection.log`

---

## File Locations

All batch files are in the main project directory:
```
C:\Projects\OSINT-Foresight\
├── COMTRADE_MENU.bat                    ← Main menu (use this!)
├── TEST_COMTRADE_API.bat                ← Test API
├── START_COMTRADE_PHASE1.bat            ← Run Phase 1
├── START_COMTRADE_BACKGROUND.bat        ← Run in background
├── CHECK_COMTRADE_STATUS.bat            ← Check status
├── SCHEDULE_DAILY_COLLECTION.bat        ← Setup scheduled task
├── COMTRADE_AUTOMATION_GUIDE.md         ← Full documentation
└── UN_COMTRADE_COLLECTION_PHASES.md     ← Phase details
```

---

## Logs and Data

**Logs:** `C:\Projects\OSINT-Foresight\logs\comtrade_collection.log`
- View anytime during collection
- Shows each request made
- Progress updates
- Error messages

**Checkpoint:** `C:\Projects\OSINT-Foresight\data\comtrade_checkpoint.json`
- Saves progress automatically
- Enables resume functionality
- Updated every 10 requests

**Database:** `F:\OSINT_WAREHOUSE\osint_master.db`
- Table: `comtrade_data`
- All collected trade records
- Indexed for fast queries

---

## Common Tasks

### Start Collection for First Time
```
1. Double-click: COMTRADE_MENU.bat
2. Choose option 1 (Test API)
3. Choose option 3 (Start Phase 1)
```

### Check Progress While Running
```
Double-click: CHECK_COMTRADE_STATUS.bat
```

### Resume After Interruption
```
Double-click: START_COMTRADE_BACKGROUND.bat
(Automatically resumes from checkpoint)
```

### Set Up Automatic Daily Collection
```
Right-click: SCHEDULE_DAILY_COLLECTION.bat
Select: Run as Administrator
```

### View Recent Activity
```
1. Double-click: COMTRADE_MENU.bat
2. Choose option 6 (View Log)
(Shows last 50 lines)
```

---

## Scheduled Task Management

After creating the scheduled task with `SCHEDULE_DAILY_COLLECTION.bat`:

**View task:**
- Press `Win+R`
- Type: `taskschd.msc`
- Press Enter
- Look for "ComtradeCollection"

**Disable task temporarily:**
```batch
schtasks /change /tn "ComtradeCollection" /disable
```

**Enable task:**
```batch
schtasks /change /tn "ComtradeCollection" /enable
```

**Delete task:**
```batch
schtasks /delete /tn "ComtradeCollection" /f
```

---

## Troubleshooting

### "Python not found"
- Make sure Python is installed
- Add Python to PATH
- Or edit batch files to use full Python path

### "Permission denied" on scheduled task
- Right-click batch file
- Choose "Run as Administrator"
- Scheduled task creation requires admin rights

### Collection seems stuck
- It's likely waiting for rate limit reset
- Check status: `CHECK_COMTRADE_STATUS.bat`
- View log file to see what's happening
- System makes 90 requests/hour (by design)

### Window closes immediately
- This is normal for background mode
- Collection continues running
- Check status to verify: `CHECK_COMTRADE_STATUS.bat`

---

## Tips

1. **Always test API first** - Run `TEST_COMTRADE_API.bat` before starting
2. **Use the menu** - `COMTRADE_MENU.bat` is the easiest way
3. **Check status regularly** - Monitor progress with status checker
4. **Let it run** - Phase 1 takes 6-8 hours, don't interrupt unnecessarily
5. **Schedule it** - Set up daily task and forget about it
6. **Safe to interrupt** - Progress saved every 10 requests
7. **Resume anytime** - `START_COMTRADE_BACKGROUND.bat` continues where left off

---

## Next Steps

**Immediate:**
1. Double-click `COMTRADE_MENU.bat`
2. Choose option 1 to test API
3. Choose option 3 to start Phase 1

**After Phase 1 completes (6-8 hours):**
1. Check status to verify completion
2. Move to Phase 2 next month
3. Or set up scheduled task to continue automatically

**Long term:**
1. Run Phase 2 in December (4-6 hours)
2. Run Phase 3 in January (6-10 hours)
3. Complete database by end of January

---

**Document Version:** 1.0
**Date:** 2025-11-01
**Status:** Ready to use

**Simplest way to start:** Double-click `COMTRADE_MENU.bat` and choose option 1!
