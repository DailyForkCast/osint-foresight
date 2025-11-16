# BigQuery Quota Weekly Check Setup

## What This Does

Checks BigQuery quota availability every week and optionally resumes patent expansion when quota is available.

## Setup Instructions

### Option 1: Automatic via Task Scheduler (Recommended)

1. Open **Task Scheduler** (search in Start menu)
2. Click **"Create Basic Task"**
3. **Name:** `BigQuery Quota Checker`
4. **Trigger:** Weekly
5. **Day:** Monday (or your preferred day)
6. **Time:** 10:00 AM (or your preferred time)
7. **Action:** Start a program
8. **Program/script:** `C:\Projects\OSINT - Foresight\scripts\check_bigquery_quota.bat`
9. Click **Finish**

### Option 2: Manual Run

Just run when you want to check:
```bash
python "C:\Projects\OSINT - Foresight\scripts\check_bigquery_quota.py"
```

## What It Checks

- Runs a minimal BigQuery test query (uses <1MB of quota)
- If quota available: Prints success message
- If quota exceeded: Logs and exits
- All results logged to: `logs/bigquery_quota_check.log`

## Auto-Resume Patent Expansion (Optional)

To automatically resume patent expansion when quota becomes available:

1. Edit `scripts/check_bigquery_quota.py`
2. Find the section marked `# OPTIONAL: Auto-resume patent expansion`
3. Uncomment the 4 lines of code
4. Save

Now the script will automatically restart patent expansion when quota is available!

## Log File

Check quota check history:
```bash
cat logs/bigquery_quota_check.log
```

Format: `YYYY-MM-DDTHH:MM:SS,STATUS`
- `AVAILABLE` = Quota OK, can resume
- `EXCEEDED` = Still over quota

## Cost Reminder

BigQuery monthly quota resets on the 1st of each month. Free tier is 1TB/month.

Our patent queries need ~39TB total, so:
- Monthly reset gives us 1-2 countries per month
- Full completion would take ~3 years at free tier
- OR enable billing for $244 to complete all 81 countries immediately

**Recommendation:** Just check weekly and collect patents gradually (free).
