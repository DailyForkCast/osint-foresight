# HOW TO SET UP AUTOMATED SCHEDULING

Since right-click → "Run as administrator" isn't showing for the .bat file, here are other ways:

## Method 1: Command Prompt as Admin (EASIEST)

1. Press `Windows Key + X`
2. Select **"Windows Terminal (Admin)"** or **"Command Prompt (Admin)"**
3. Copy and paste these commands:

```cmd
cd "C:\Projects\OSINT - Foresight\scripts"
setup_scheduled_tasks.bat
```

## Method 2: Create a Shortcut

1. Right-click on `setup_scheduled_tasks.bat`
2. Select "Create shortcut"
3. Right-click the new shortcut
4. Select "Properties"
5. Click "Advanced..."
6. Check "Run as administrator"
7. Click OK, OK
8. Double-click the shortcut

## Method 3: Run Through File Explorer

1. Open File Explorer
2. Navigate to `C:\Projects\OSINT - Foresight\scripts`
3. Hold `Shift` and right-click in empty space
4. Select "Open PowerShell window here as administrator"
5. Type: `.\setup_scheduled_tasks.bat`

## Method 4: Direct Task Scheduler Setup (Manual)

1. Press `Windows Key + R`
2. Type `taskschd.msc` and press Enter
3. Click "Create Basic Task..." in the right panel
4. Follow these steps:

### Task 1: Daily Intelligence
- **Name**: OSINT_Daily_Intelligence
- **Description**: Daily OSINT intelligence collection
- **Trigger**: Daily, Start: 6:00 AM
- **Action**: Start a program
- **Program**: `C:\Projects\OSINT - Foresight\scripts\scheduled_intelligence_runner.bat`
- Check "Open Properties dialog" and click Finish
- In Properties, check "Run with highest privileges"

### Task 2: Weekly Analysis
- **Name**: OSINT_Weekly_Analysis
- **Trigger**: Weekly, Monday, 8:00 AM
- **Action**: Same batch file as above

## Method 5: PowerShell Commands (Copy & Paste)

1. Open PowerShell as Administrator (Windows + X → Windows PowerShell (Admin))
2. Copy and paste these commands:

```powershell
# Daily task at 6 AM
$action = New-ScheduledTaskAction -Execute "C:\Projects\OSINT - Foresight\scripts\scheduled_intelligence_runner.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM
Register-ScheduledTask -TaskName "OSINT_Daily_Intelligence" -Action $action -Trigger $trigger -Description "Daily OSINT intelligence collection"

# Weekly task on Mondays at 8 AM
$trigger2 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8:00AM
Register-ScheduledTask -TaskName "OSINT_Weekly_Analysis" -Action $action -Trigger $trigger2 -Description "Weekly OSINT analysis"

Write-Host "Scheduled tasks created successfully!" -ForegroundColor Green
```

---

## IF YOU DON'T WANT TO DEAL WITH ADMIN/SCHEDULING:

Just use the manual options that work without any admin rights:

### Option A: Double-click to run
- `C:\Projects\OSINT - Foresight\RUN_NOW.bat`

### Option B: Python control panel
- `python MASTER_CONTROL.py`

### Option C: Create your own simple scheduler
Use Windows Task Scheduler with YOUR user account (no admin needed):
1. Open Task Scheduler (no admin)
2. Create Basic Task
3. Set it to run only when you're logged in
4. This works without admin but only runs when you're logged in

---

## To Test If It's Working:

After setting up, you can test immediately:
```cmd
schtasks /run /tn "OSINT_Daily_Intelligence"
```

Or check if tasks exist:
```cmd
schtasks /query | findstr OSINT
```