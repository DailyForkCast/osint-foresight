#!/usr/bin/env python3
"""
View the OSINT Processing Dashboard
Displays current status of all data processing operations
"""

import sqlite3
import os
import time
from datetime import datetime
from pathlib import Path
import json

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_processing_status():
    """Get current processing status from database"""
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source, status, started, completed,
                   records_processed, errors, last_error, updated_at
            FROM processing_status
            ORDER BY source
        """)
        
        results = cursor.fetchall()
        conn.close()
        return results
    except:
        return []

def get_database_stats():
    """Get database statistics"""
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Get table count
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        stats['tables'] = cursor.fetchone()[0]
        
        # Get total records in key tables
        cursor.execute("SELECT COUNT(*) FROM china_entities")
        stats['china_entities'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts")
        stats['ted_contracts'] = cursor.fetchone()[0]
        
        # Get database size
        cursor.execute("SELECT page_count * page_size / (1024*1024) FROM pragma_page_count(), pragma_page_size()")
        stats['size_mb'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    except:
        return {}

def format_number(n):
    """Format number with commas"""
    if n is None:
        return "0"
    return f"{n:,}"

def create_dashboard():
    """Create the dashboard display"""
    clear_screen()
    
    # Header
    print("="*80)
    print("                    OSINT FORESIGHT - PROCESSING DASHBOARD")
    print("="*80)
    print(f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n")
    
    # Database Stats
    db_stats = get_database_stats()
    if db_stats:
        print("DATABASE STATUS")
        print("-"*40)
        print(f"Primary Database: osint_master.db ({db_stats.get('size_mb', 0):.1f} MB)")
        print(f"Tables: {db_stats.get('tables', 0)}")
        print(f"China Entities: {format_number(db_stats.get('china_entities', 0))}")
        print(f"TED Contracts: {format_number(db_stats.get('ted_contracts', 0))}")
        print("\n")
    
    # Processing Status
    print("DATA SOURCE PROCESSING STATUS")
    print("-"*80)
    print("Source        Status      Started              Records     Errors  Progress")
    print("-"*80)
    
    statuses = get_processing_status()
    
    if not statuses:
        # Default status if no processing has been run
        sources = [
            ('OpenAlex', 'pending', None, None, 0, 0, None, None),
            ('OpenAIRE', 'pending', None, None, 0, 0, None, None),
            ('TED', 'pending', None, None, 0, 0, None, None),
            ('USAspending', 'pending', None, None, 0, 0, None, None)
        ]
    else:
        sources = statuses
    
    total_records = 0
    total_errors = 0
    
    for source, status, started, completed, records, errors, last_error, updated in sources:
        records = records or 0
        errors = errors or 0
        total_records += records
        total_errors += errors
        
        # Status icon
        status_icon = {
            'pending': '[ ]',
            'running': '[>]',
            'completed': '[OK]',
            'failed': '[X]'
        }.get(status, '[?]')
        
        # Format started time
        if started:
            try:
                start_dt = datetime.fromisoformat(started)
                started_str = start_dt.strftime('%m/%d %H:%M')
            except:
                started_str = 'Unknown'
        else:
            started_str = '-'
        
        # Progress bar
        if status == 'completed':
            progress = '[##########] 100%'
        elif status == 'running':
            progress = '[####------] 40%'
        elif status == 'failed':
            progress = '[ERROR]'
        else:
            progress = '[----------] 0%'
        
        print(f"{source:<12}  {status_icon} {status:<9} {started_str:<15} {records:>10,}  {errors:>6}  {progress}")
    
    print("-"*80)
    print(f"{'TOTALS':<37} {total_records:>10,}  {total_errors:>6}")
    print("\n")
    
    # OpenAlex specific stats
    openalex_checkpoint = Path("C:/Projects/OSINT - Foresight/data/processed/openalex_multicountry_temporal/processing_checkpoint.json")
    if openalex_checkpoint.exists():
        with open(openalex_checkpoint, 'r') as f:
            data = json.load(f)
            stats = data.get('stats', {})
            
            print("OPENALEX DETAILED STATISTICS")
            print("-"*40)
            print(f"Total Papers Analyzed: {format_number(stats.get('total_papers', 0))}")
            print(f"China Collaborations: {format_number(stats.get('papers_with_china', 0))}")
            print(f"Countries Tracked: {len(stats.get('country_collaborations', {}))}")
            print(f"Files Processed: {stats.get('files_processed', 0)}/970")
            
            # Top collaborating countries
            country_collab = stats.get('country_collaborations', {})
            if country_collab:
                top_5 = sorted(country_collab.items(), key=lambda x: x[1], reverse=True)[:5]
                print("\nTop 5 Collaborating Countries:")
                for country, count in top_5:
                    print(f"  {country}: {format_number(count)}")
    
    print("\n")
    print("="*80)
    print("Commands:")
    print("  [R] Refresh     [S] Start Processing     [Q] Quit")
    print("  [1] View OpenAlex Details    [2] View TED Details")
    print("  [3] View OpenAIRE Details    [4] View USAspending Details")
    print("="*80)

def view_openalex_details():
    """View detailed OpenAlex statistics"""
    clear_screen()
    print("="*80)
    print("                         OPENALEX PROCESSING DETAILS")
    print("="*80)
    print("\n")
    
    checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/processed/openalex_multicountry_temporal/processing_checkpoint.json")
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
            
            print(f"Last Update: {data.get('timestamp', 'Unknown')}")
            print(f"Last File: {data.get('last_processed_file', 'None')}")
            print("\n")
            
            stats = data.get('stats', {})
            print("PROCESSING STATISTICS")
            print("-"*40)
            print(f"Total Papers: {format_number(stats.get('total_papers', 0))}")
            print(f"China Papers: {format_number(stats.get('papers_with_china', 0))}")
            print(f"Percentage: {stats.get('papers_with_china', 0) / max(stats.get('total_papers', 1), 1) * 100:.2f}%")
            print(f"Files Processed: {stats.get('files_processed', 0)}")
            print(f"Errors: {stats.get('errors', 0)}")
            print("\n")
            
            # Technology breakdown
            tech_collab = stats.get('technology_collaborations', {})
            if tech_collab:
                print("TECHNOLOGY AREAS")
                print("-"*40)
                for tech, countries in tech_collab.items():
                    total = sum(countries.values())
                    print(f"{tech}: {total} collaborations")
            print("\n")
            
            # Time period analysis
            period_collab = stats.get('period_collaborations', {})
            if period_collab:
                print("TIME PERIOD ANALYSIS")
                print("-"*40)
                for period, countries in period_collab.items():
                    total = sum(countries.values())
                    print(f"{period}: {format_number(total)} collaborations")
    else:
        print("No OpenAlex processing data found.")
    
    print("\nPress Enter to return to main dashboard...")
    input()

def view_ted_details():
    """View detailed TED statistics"""
    clear_screen()
    print("="*80)
    print("                          TED PROCUREMENT DETAILS")
    print("="*80)
    print("\n")
    
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get TED statistics
    cursor.execute("""
        SELECT COUNT(*) as total,
               COUNT(DISTINCT vendor_name) as vendors,
               SUM(contract_value) as value,
               MIN(award_date) as earliest,
               MAX(award_date) as latest
        FROM ted_china_contracts
    """)
    
    result = cursor.fetchone()
    if result and result[0] > 0:
        total, vendors, value, earliest, latest = result
        print("CONTRACT STATISTICS")
        print("-"*40)
        print(f"Total Contracts: {format_number(total)}")
        print(f"Unique Vendors: {format_number(vendors)}")
        print(f"Total Value: EUR {format_number(value)}")
        print(f"Date Range: {earliest} to {latest}")
        print("\n")
        
        # Top vendors
        cursor.execute("""
            SELECT vendor_name, COUNT(*) as contracts, SUM(contract_value) as total
            FROM ted_china_contracts
            GROUP BY vendor_name
            ORDER BY total DESC
            LIMIT 10
        """)
        
        print("TOP 10 CHINESE VENDORS BY VALUE")
        print("-"*40)
        for vendor, contracts, total in cursor.fetchall():
            print(f"{vendor[:40]:<40} {contracts:>5} contracts, EUR {format_number(total)}")
        print("\n")
        
        # By country
        cursor.execute("""
            SELECT buyer_country, COUNT(*) as count, SUM(contract_value) as value
            FROM ted_china_contracts
            GROUP BY buyer_country
            ORDER BY value DESC
            LIMIT 10
        """)
        
        print("TOP BUYER COUNTRIES")
        print("-"*40)
        for country, count, value in cursor.fetchall():
            if country:
                print(f"{country}: {count} contracts, EUR {format_number(value)}")
    else:
        print("No TED data processed yet.")
    
    conn.close()
    print("\nPress Enter to return to main dashboard...")
    input()

def main():
    """Main dashboard loop"""
    while True:
        create_dashboard()
        
        # Get user input (with timeout for auto-refresh)
        import select
        import sys
        
        # On Windows, use a simpler approach
        if os.name == 'nt':
            import msvcrt
            import time
            
            start_time = time.time()
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    break
                if time.time() - start_time > 10:  # Auto-refresh every 10 seconds
                    key = 'r'
                    break
                time.sleep(0.1)
        else:
            # Unix/Linux
            key = input().lower()
        
        if key == 'q':
            print("\nExiting dashboard...")
            break
        elif key == 's':
            print("\nTo start processing, run:")
            print("  python scripts/orchestrate_concurrent_processing.py")
            print("\nPress Enter to continue...")
            input()
        elif key == '1':
            view_openalex_details()
        elif key == '2':
            view_ted_details()
        elif key == '3':
            print("\nOpenAIRE details not yet implemented.")
            print("Press Enter to continue...")
            input()
        elif key == '4':
            print("\nUSAspending details not yet implemented.")
            print("Press Enter to continue...")
            input()
        # 'r' or auto-refresh will just loop

if __name__ == "__main__":
    print("Starting OSINT Processing Dashboard...")
    print("This dashboard auto-refreshes every 10 seconds.")
    print("Press 'Q' to quit at any time.\n")
    time.sleep(2)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDashboard closed.")
