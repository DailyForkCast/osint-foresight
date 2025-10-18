#!/usr/bin/env python3
"""
Show the OSINT Processing Dashboard (non-interactive)
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json

def format_number(n):
    """Format number with commas"""
    if n is None:
        return "0"
    return f"{n:,}"

def show_dashboard():
    """Display the dashboard once"""
    
    print("="*80)
    print("                    OSINT FORESIGHT - PROCESSING DASHBOARD")
    print("="*80)
    print(f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n")
    
    # Database Stats
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get database size and table count
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT page_count * page_size / (1024*1024) FROM pragma_page_count(), pragma_page_size()")
        size_mb = cursor.fetchone()[0]
        
        print("DATABASE STATUS")
        print("-"*40)
        print(f"Primary Database: osint_master.db ({size_mb:.1f} MB)")
        print(f"Tables: {table_count}")
        
        # Try to get entity counts
        try:
            cursor.execute("SELECT COUNT(*) FROM china_entities")
            china_count = cursor.fetchone()[0]
            print(f"China Entities: {format_number(china_count)}")
        except:
            pass
            
        try:
            cursor.execute("SELECT COUNT(*) FROM ted_china_contracts")
            ted_count = cursor.fetchone()[0]
            print(f"TED Contracts: {format_number(ted_count)}")
        except:
            pass
        
        print("\n")
        
        # Processing Status
        print("DATA SOURCE PROCESSING STATUS")
        print("-"*80)
        print("Source        Status      Records     Errors   Last Activity")
        print("-"*80)
        
        try:
            cursor.execute("""
                SELECT source, status, started, completed,
                       records_processed, errors, updated_at
                FROM processing_status
                ORDER BY source
            """)
            
            results = cursor.fetchall()
            total_records = 0
            total_errors = 0
            
            for source, status, started, completed, records, errors, updated in results:
                records = records or 0
                errors = errors or 0
                total_records += records
                total_errors += errors
                
                # Status display
                status_display = {
                    'pending': '[ ] Pending',
                    'running': '[>] Running',
                    'completed': '[OK] Complete',
                    'failed': '[X] Failed'
                }.get(status, '[?] Unknown')
                
                # Last activity
                if completed:
                    last_activity = f"Completed {completed[:10]}"
                elif started:
                    last_activity = f"Started {started[:10]}"
                else:
                    last_activity = "Not started"
                
                print(f"{source:<12}  {status_display:<15} {records:>8,}   {errors:>6}   {last_activity}")
            
            print("-"*80)
            print(f"{'TOTALS':<28} {total_records:>8,}   {total_errors:>6}")
            
        except sqlite3.OperationalError:
            # No processing_status table yet
            print("No processing has been started yet.")
            print("Run: python scripts/orchestrate_concurrent_processing.py")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return
    
    print("\n")
    
    # OpenAlex checkpoint data
    checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/processed/openalex_multicountry_temporal/processing_checkpoint.json")
    if checkpoint_file.exists():
        print("OPENALEX PROCESSING DETAILS")
        print("-"*40)
        
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
            stats = data.get('stats', {})
            
            print(f"Total Papers Analyzed: {format_number(stats.get('total_papers', 0))}")
            print(f"China Collaborations: {format_number(stats.get('papers_with_china', 0))}")
            print(f"Countries Tracked: {len(stats.get('country_collaborations', {}))}")
            print(f"Files Processed: {stats.get('files_processed', 0)}")
            
            # Top countries
            country_collab = stats.get('country_collaborations', {})
            if country_collab:
                top_5 = sorted(country_collab.items(), key=lambda x: x[1], reverse=True)[:5]
                print("\nTop 5 Collaborating Countries:")
                for country, count in top_5:
                    print(f"  {country}: {format_number(count)}")
        print("\n")
    
    # Quick summary
    print("="*80)
    print("QUICK ACCESS:")
    print("  View Dashboard: python scripts/view_dashboard.py")
    print("  Start Processing: python scripts/orchestrate_concurrent_processing.py")
    print("  Check Status: python scripts/check_processing_status.py")
    print("="*80)

if __name__ == "__main__":
    show_dashboard()
