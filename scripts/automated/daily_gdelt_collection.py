#!/usr/bin/env python3
"""
Daily GDELT Collection - Automated
Collects previous day's China-related events at 2am daily

Collection Strategy:
- Collects ALL China events (no geographic filter)
- Uses V2 collector (pagination, validation, checkpointing)
- Stores in F:/OSINT_WAREHOUSE/osint_master.db
- Full provenance tracking
- Email notification on completion/failure (optional)

Zero Fabrication Protocol: ENFORCED
- Only processes actual GDELT data
- Full provenance chain
- Automated validation
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.gdelt_collector_v2 import GDELTCollectorV2

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/daily_gdelt_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

def get_yesterday_date_range():
    """Get yesterday's date range in YYYYMMDD format"""
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y%m%d")
    return (date_str, date_str)

def send_notification(status, stats):
    """
    Send email notification (optional)

    To enable:
    1. pip install sendgrid
    2. Set SENDGRID_API_KEY environment variable
    3. Uncomment code below
    """
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail
    #
    # message = Mail(
    #     from_email='gdelt-collector@osint-foresight.com',
    #     to_emails='mreardon84@gmail.com',
    #     subject=f'GDELT Daily Collection - {status}',
    #     html_content=f'<pre>{json.dumps(stats, indent=2)}</pre>'
    # )
    #
    # try:
    #     sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    #     response = sg.send(message)
    #     logging.info(f"Notification sent: {response.status_code}")
    # except Exception as e:
    #     logging.error(f"Failed to send notification: {e}")

    logging.info(f"Notification (disabled): {status}")

def main():
    """Main daily collection routine"""

    logging.info("=" * 80)
    logging.info("GDELT DAILY COLLECTION - Automated")
    logging.info("=" * 80)

    # Get yesterday's date
    start_date, end_date = get_yesterday_date_range()
    logging.info(f"Collecting: {start_date} (yesterday)")

    # Initialize collector
    checkpoint_file = f"checkpoints/daily_gdelt_{start_date}.json"
    collector = GDELTCollectorV2(checkpoint_file=checkpoint_file)

    try:
        # Connect and setup
        collector.connect()
        collector.create_tables()

        if not collector.setup_bigquery():
            logging.error("BigQuery setup failed")
            send_notification("FAILED", {"error": "BigQuery setup failed"})
            return 1

        # Collect yesterday's data
        logging.info("Starting collection...")
        report = collector.collect_date_range(start_date, end_date)

        if report["status"] == "success":
            # Success
            stats = {
                "date": start_date,
                "status": "SUCCESS",
                "events_queried": report["events_queried"],
                "events_inserted": report["events_inserted"],
                "events_duplicate": report["events_duplicate"],
                "validation": report["validation"]
            }

            logging.info("=" * 80)
            logging.info("COLLECTION COMPLETE")
            logging.info("=" * 80)
            logging.info(f"Date: {start_date}")
            logging.info(f"Events queried: {report['events_queried']:,}")
            logging.info(f"Events inserted: {report['events_inserted']:,}")
            logging.info(f"Duplicates: {report['events_duplicate']:,}")
            logging.info(f"Validation: {'PASSED' if report['validation']['passed'] else 'FAILED'}")
            logging.info("=" * 80)

            send_notification("SUCCESS", stats)
            return 0

        else:
            # Failed
            stats = {
                "date": start_date,
                "status": "FAILED",
                "error": report.get("error", "Unknown error")
            }

            logging.error(f"Collection failed: {report.get('error')}")
            send_notification("FAILED", stats)
            return 1

    except Exception as e:
        logging.error(f"Daily collection error: {e}", exc_info=True)
        send_notification("ERROR", {"error": str(e)})
        return 1

    finally:
        if collector.conn:
            collector.conn.close()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
