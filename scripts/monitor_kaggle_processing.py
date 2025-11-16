"""
Real-time monitoring of Kaggle arXiv processing
Shows progress, estimated time remaining, and interim statistics
"""

import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta

PROCESSING_DB = Path("C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db")
EXPECTED_TOTAL = 2_300_000  # Approximate total papers in Kaggle dataset

def monitor_processing():
    """Monitor processing progress with live updates"""

    print("=" * 80)
    print("KAGGLE ARXIV PROCESSING MONITOR")
    print("=" * 80)
    print()

    if not PROCESSING_DB.exists():
        print("[WARN] Processing database not found yet")
        print("Processing may not have started or is still initializing...")
        return

    start_time = datetime.now()
    last_count = 0
    last_check = start_time

    print(f"Monitoring started: {start_time.strftime('%H:%M:%S')}")
    print(f"Database: {PROCESSING_DB}")
    print()

    try:
        while True:
            conn = sqlite3.connect(str(PROCESSING_DB))

            # Get current stats
            papers = conn.execute("SELECT COUNT(*) FROM kaggle_arxiv_papers").fetchone()[0]
            authors = conn.execute("SELECT COUNT(*) FROM kaggle_arxiv_authors").fetchone()[0]
            db_size = PROCESSING_DB.stat().st_size / (1024**2)  # MB

            # Check if complete
            log_count = conn.execute("SELECT COUNT(*) FROM kaggle_arxiv_processing_log").fetchone()[0]

            # Calculate progress
            progress_pct = (papers / EXPECTED_TOTAL) * 100 if EXPECTED_TOTAL > 0 else 0

            # Calculate rate
            now = datetime.now()
            time_elapsed = (now - last_check).total_seconds()

            if time_elapsed > 0 and last_count > 0:
                papers_per_sec = (papers - last_count) / time_elapsed
            else:
                papers_per_sec = 0

            # Estimate time remaining
            if papers_per_sec > 0:
                remaining_papers = EXPECTED_TOTAL - papers
                seconds_remaining = remaining_papers / papers_per_sec
                eta = now + timedelta(seconds=seconds_remaining)
            else:
                eta = None

            # Get technology breakdown (if available)
            try:
                tech_counts = conn.execute("""
                    SELECT technology_domain, COUNT(DISTINCT arxiv_id) as papers
                    FROM kaggle_arxiv_technology
                    GROUP BY technology_domain
                    ORDER BY papers DESC
                    LIMIT 5
                """).fetchall()
            except:
                tech_counts = []

            # Display
            print(f"\r{'=' * 80}", end='')
            print(f"\rStatus at {now.strftime('%H:%M:%S')}")
            print(f"\r  Papers processed: {papers:>10,} / {EXPECTED_TOTAL:,} ({progress_pct:>5.1f}%)")
            print(f"\r  Author records:   {authors:>10,}")
            print(f"\r  Database size:    {db_size:>10.1f} MB")

            if papers_per_sec > 0:
                print(f"\r  Processing rate:  {papers_per_sec:>10,.0f} papers/sec")

            if eta:
                print(f"\r  Estimated ETA:    {eta.strftime('%H:%M:%S')}")
                print(f"\r  Time remaining:   ~{int(seconds_remaining/60)} minutes")

            if tech_counts:
                print(f"\r\n  Top technologies:")
                for tech, count in tech_counts:
                    print(f"\r    {tech:20s}: {count:>8,} papers")

            if log_count > 0:
                # Processing complete!
                log_entry = conn.execute("""
                    SELECT total_papers_processed, processing_time_seconds
                    FROM kaggle_arxiv_processing_log
                    ORDER BY id DESC LIMIT 1
                """).fetchone()

                if log_entry:
                    total, proc_time = log_entry
                    print(f"\r\n{'=' * 80}")
                    print(f"\r[OK] PROCESSING COMPLETE!")
                    print(f"\r  Total papers: {total:,}")
                    print(f"\r  Processing time: {proc_time:.1f} seconds ({proc_time/60:.1f} minutes)")
                    print(f"\r  Avg rate: {total/proc_time:,.0f} papers/second")
                    print(f"\r{'=' * 80}")

                conn.close()
                break

            conn.close()

            # Update for next iteration
            last_count = papers
            last_check = now

            # Wait before next check
            time.sleep(10)  # Check every 10 seconds

    except KeyboardInterrupt:
        print(f"\r\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"\r\n\nError: {e}")

if __name__ == '__main__':
    monitor_processing()
