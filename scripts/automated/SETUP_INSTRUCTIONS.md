# Daily GDELT Collection - Setup Instructions

**Goal:** Automatically collect GDELT events every day at 2am

---

## Quick Setup (Run as Administrator)

### Option 1: PowerShell (Recommended)

1. **Right-click PowerShell and select "Run as Administrator"**

2. **Run setup script:**
   ```powershell
   cd C:\Projects\OSINT-Foresight
   .\scripts\automated\setup_daily_collection.ps1
   ```

3. **Verify task was created:**
   ```powershell
   Get-ScheduledTask -TaskName "GDELT_Daily_Collection"
   ```

---

### Option 2: Manual Setup (Task Scheduler GUI)

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type: `taskschd.msc`
   - Press Enter

2. **Create Basic Task**
   - Click "Create Basic Task" in right panel
   - Name: `GDELT_Daily_Collection`
   - Description: `Daily GDELT event collection - collects previous day's China-related events`
   - Click Next

3. **Trigger**
   - Select: "Daily"
   - Click Next
   - Start: Tomorrow's date
   - Time: `02:00:00`
   - Recur every: `1` days
   - Click Next

4. **Action**
   - Select: "Start a program"
   - Click Next
   - Program/script: `C:\Projects\OSINT-Foresight\scripts\automated\run_daily_collection.bat`
   - Click Next

5. **Finish**
   - Check "Open the Properties dialog"
   - Click Finish

6. **Properties Settings**
   - General tab:
     - Check "Run whether user is logged on or not"
     - Check "Run with highest privileges"
   - Settings tab:
     - Check "Run task as soon as possible after a scheduled start is missed"
     - Check "If the task fails, restart every: 1 hour"
     - Uncheck "Stop the task if it runs longer than: 3 days"
   - Click OK

---

## Test the Setup

### Run manually to test:

```powershell
# Start the task now (as admin)
Start-ScheduledTask -TaskName "GDELT_Daily_Collection"

# Wait 2-3 minutes, then check log
Get-Content C:\Projects\OSINT-Foresight\logs\daily_gdelt_*.log -Tail 50
```

---

## What Gets Collected

**Every day at 2am:**
- Collects **previous day's** China-related events from GDELT
- Example: On Nov 3 at 2am, collects Nov 2 events
- Uses V2 collector (pagination, validation, checkpointing)
- Stores in: `F:/OSINT_WAREHOUSE/osint_master.db`

**Expected volume:**
- ~100,000-150,000 events per day
- ~3-5 minutes collection time
- ~200-300 MB per day

---

## Monitoring

### Check if task is scheduled:
```powershell
Get-ScheduledTask -TaskName "GDELT_Daily_Collection" | Select-Object State, NextRunTime
```

### View recent logs:
```powershell
# View today's log
Get-Content C:\Projects\OSINT-Foresight\logs\daily_gdelt_20251102.log

# View last 50 lines of latest log
Get-Content C:\Projects\OSINT-Foresight\logs\daily_gdelt_*.log -Tail 50

# Watch live (updates as task runs)
Get-Content C:\Projects\OSINT-Foresight\logs\daily_gdelt_*.log -Wait -Tail 10
```

### Check database growth:
```powershell
# Quick database stats
python -c "import sqlite3; db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db'); print(f'Total events: {db.execute(\"SELECT COUNT(*) FROM gdelt_events\").fetchone()[0]:,}')"
```

---

## Email Notifications (Optional)

To get email notifications on success/failure:

1. **Install SendGrid package:**
   ```bash
   pip install sendgrid
   ```

2. **Get SendGrid API key:**
   - Sign up at https://sendgrid.com (free tier: 100 emails/day)
   - Create API key
   - Set environment variable: `SENDGRID_API_KEY=your_key_here`

3. **Edit `daily_gdelt_collection.py`:**
   - Uncomment lines 31-47 (email notification code)
   - Update `to_emails` to your email address

4. **Test:**
   ```powershell
   Start-ScheduledTask -TaskName "GDELT_Daily_Collection"
   # Check email in ~5 minutes
   ```

---

## Troubleshooting

### Task not running?
```powershell
# Check task status
Get-ScheduledTask -TaskName "GDELT_Daily_Collection" | Select-Object State, LastRunTime, LastTaskResult

# View task history
Get-ScheduledTaskInfo -TaskName "GDELT_Daily_Collection"

# Check Windows Event Viewer
# Event Viewer > Windows Logs > Application
# Look for "Task Scheduler" source
```

### Collection failing?
```bash
# Test manually
cd C:\Projects\OSINT-Foresight
python scripts/automated/daily_gdelt_collection.py

# Check BigQuery credentials
gcloud auth application-default login

# Verify database access
python -c "import sqlite3; db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db'); print('OK')"
```

### Out of disk space?
```powershell
# Check F: drive space
Get-PSDrive F | Select-Object Used, Free

# Archive old data if needed
# (Create archive script if this becomes an issue)
```

---

## Maintenance

### Pause daily collection:
```powershell
Disable-ScheduledTask -TaskName "GDELT_Daily_Collection"
```

### Resume daily collection:
```powershell
Enable-ScheduledTask -TaskName "GDELT_Daily_Collection"
```

### Update collection script:
- Edit: `scripts/automated/daily_gdelt_collection.py`
- No need to recreate scheduled task

### Remove daily collection:
```powershell
Unregister-ScheduledTask -TaskName "GDELT_Daily_Collection" -Confirm:$false
```

---

## Log Retention

**Current:** Logs kept forever (one log file per day)

**Recommended:** Clean up logs older than 90 days

**Create cleanup script** (optional):
```powershell
# Delete logs older than 90 days
Get-ChildItem C:\Projects\OSINT-Foresight\logs\daily_gdelt_*.log |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-90) } |
    Remove-Item
```

Add to scheduled task if desired.

---

## Summary

**What you'll get:**
- ✅ Automatic daily collection at 2am
- ✅ Full China event coverage (ALL countries)
- ✅ Complete provenance tracking
- ✅ Indexed database for fast queries
- ✅ Resume capability (checkpoints)
- ✅ Validation on every collection
- ✅ Daily logs for monitoring

**Next run:** Tomorrow at 2am (collects today's events)

**Manual test:** `Start-ScheduledTask -TaskName "GDELT_Daily_Collection"`
