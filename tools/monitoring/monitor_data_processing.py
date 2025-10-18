#!/usr/bin/env python3
"""
Monitor USPTO and ESTAT data processing progress
Provides real-time status updates and statistics
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class ProcessingMonitor:
    def __init__(self):
        self.base_dir = Path("C:/Projects/OSINT - Foresight")
        self.progress_file = self.base_dir / "data" / "processing_progress.json"
        self.summary_file = self.base_dir / "data" / "processing_summary.json"
        self.output_dir = Path("F:/DECOMPRESSED_DATA")
        self.processed_dir = Path("F:/PROCESSED_DATA")

    def load_progress(self) -> Dict[str, Any]:
        """Load current processing progress"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return None

    def calculate_disk_usage(self) -> Dict[str, float]:
        """Calculate disk usage for output directories"""
        usage = {}

        for dir_name, dir_path in [
            ('uspto_output', self.output_dir / "uspto_data"),
            ('estat_output', self.output_dir / "estat_data"),
            ('processed', self.processed_dir)
        ]:
            if dir_path.exists():
                total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                usage[dir_name] = total_size / 1e9  # Convert to GB
            else:
                usage[dir_name] = 0

        return usage

    def format_time_elapsed(self, start_time: str) -> str:
        """Format time elapsed since start"""
        if not start_time:
            return "N/A"

        try:
            start = datetime.fromisoformat(start_time)
            elapsed = datetime.now() - start
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except:
            return "N/A"

    def display_progress(self, progress: Dict[str, Any]):
        """Display formatted progress information"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print("=" * 70)
        print("USPTO & ESTAT DATA PROCESSING MONITOR")
        print("=" * 70)
        print(f"Last Update: {progress.get('last_update', 'N/A')}")
        print()

        # USPTO Progress
        uspto = progress.get('uspto', {})
        print("USPTO DATA PROCESSING:")
        print(f"  Processed: {len(uspto.get('processed', []))} files")
        print(f"  Failed: {len(uspto.get('failed', []))} files")

        if uspto.get('stats'):
            total_size = sum(s['size'] for s in uspto['stats'].values()) / 1e9
            total_extracted = sum(s.get('extracted_files', 0) for s in uspto['stats'].values())
            print(f"  Total Size Processed: {total_size:.2f} GB")
            print(f"  Total Files Extracted: {total_extracted}")

        if uspto.get('failed'):
            print("\n  Recent Failures:")
            for failure in uspto['failed'][-3:]:  # Show last 3 failures
                print(f"    - {failure['file']}: {failure['error'][:50]}...")

        print()

        # ESTAT Progress
        estat = progress.get('estat', {})
        print("ESTAT DATA PROCESSING:")
        print(f"  Processed: {len(estat.get('processed', []))} files")
        print(f"  Failed: {len(estat.get('failed', []))} files")

        if estat.get('stats'):
            total_size = sum(s.get('size', 0) for s in estat['stats'].values()) / 1e6
            total_extracted = sum(s.get('extracted_files', 0) for s in estat['stats'].values())
            print(f"  Total Size Processed: {total_size:.2f} MB")
            print(f"  Total Files Extracted: {total_extracted}")

        print()

        # Disk Usage
        usage = self.calculate_disk_usage()
        print("DISK USAGE:")
        print(f"  USPTO Output: {usage['uspto_output']:.2f} GB")
        print(f"  ESTAT Output: {usage['estat_output']:.2f} GB")
        print(f"  Processed Data: {usage['processed']:.2f} GB")
        print(f"  Total: {sum(usage.values()):.2f} GB")

        print()

        # Recent activity
        if uspto.get('processed'):
            print("RECENT ACTIVITY:")
            recent_files = []

            # Get recent USPTO files
            for file in uspto['processed'][-3:]:
                if file in uspto.get('stats', {}):
                    stats = uspto['stats'][file]
                    recent_files.append((stats.get('timestamp', ''), 'USPTO', file))

            # Get recent ESTAT files
            for file in estat.get('processed', [])[-3:]:
                if file in estat.get('stats', {}):
                    stats = estat['stats'][file]
                    recent_files.append((stats.get('timestamp', ''), 'ESTAT', file))

            # Sort by timestamp and show most recent
            recent_files.sort(key=lambda x: x[0], reverse=True)
            for timestamp, source, filename in recent_files[:5]:
                if timestamp:
                    time_str = datetime.fromisoformat(timestamp).strftime('%H:%M:%S')
                    print(f"  [{time_str}] {source}: {filename}")

    def monitor_continuous(self, refresh_interval: int = 5):
        """Continuously monitor progress"""
        print("Starting continuous monitoring...")
        print(f"Refreshing every {refresh_interval} seconds")
        print("Press Ctrl+C to stop")
        print()

        try:
            while True:
                progress = self.load_progress()

                if progress:
                    self.display_progress(progress)
                else:
                    print("No progress data found. Waiting for processing to start...")

                time.sleep(refresh_interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")

    def generate_report(self):
        """Generate a detailed report"""
        progress = self.load_progress()

        if not progress:
            print("No progress data available.")
            return

        report_file = self.base_dir / "data" / f"processing_report_{datetime.now():%Y%m%d_%H%M%S}.txt"

        with open(report_file, 'w') as f:
            f.write("USPTO & ESTAT DATA PROCESSING REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
            f.write(f"Last Update: {progress.get('last_update', 'N/A')}\n\n")

            # USPTO Section
            f.write("USPTO DATA:\n")
            f.write("-" * 40 + "\n")
            uspto = progress.get('uspto', {})
            f.write(f"Processed Files: {len(uspto.get('processed', []))}\n")
            f.write(f"Failed Files: {len(uspto.get('failed', []))}\n\n")

            if uspto.get('processed'):
                f.write("Processed Files:\n")
                for file in uspto['processed']:
                    f.write(f"  - {file}\n")
                    if file in uspto.get('stats', {}):
                        stats = uspto['stats'][file]
                        f.write(f"    Size: {stats['size'] / 1e9:.2f} GB\n")
                        f.write(f"    Extracted: {stats.get('extracted_files', 0)} files\n")

            if uspto.get('failed'):
                f.write("\nFailed Files:\n")
                for failure in uspto['failed']:
                    f.write(f"  - {failure['file']}\n")
                    f.write(f"    Error: {failure['error']}\n")
                    f.write(f"    Time: {failure['timestamp']}\n")

            f.write("\n")

            # ESTAT Section
            f.write("ESTAT DATA:\n")
            f.write("-" * 40 + "\n")
            estat = progress.get('estat', {})
            f.write(f"Processed Files: {len(estat.get('processed', []))}\n")
            f.write(f"Failed Files: {len(estat.get('failed', []))}\n\n")

            if estat.get('processed'):
                f.write("Processed Files:\n")
                for file in estat['processed']:
                    f.write(f"  - {file}\n")

            # Disk Usage
            f.write("\nDISK USAGE:\n")
            f.write("-" * 40 + "\n")
            usage = self.calculate_disk_usage()
            for name, size in usage.items():
                f.write(f"{name}: {size:.2f} GB\n")
            f.write(f"Total: {sum(usage.values()):.2f} GB\n")

        print(f"Report saved to: {report_file}")
        return report_file


def main():
    """Main entry point"""
    monitor = ProcessingMonitor()

    print("USPTO & ESTAT Data Processing Monitor")
    print("=" * 40)
    print("1. Show current status")
    print("2. Continuous monitoring")
    print("3. Generate report")
    print("4. Exit")
    print()

    choice = input("Select option (1-4): ")

    if choice == '1':
        progress = monitor.load_progress()
        if progress:
            monitor.display_progress(progress)
        else:
            print("No progress data found.")

    elif choice == '2':
        interval = input("Refresh interval in seconds (default 5): ")
        interval = int(interval) if interval.isdigit() else 5
        monitor.monitor_continuous(interval)

    elif choice == '3':
        monitor.generate_report()

    elif choice == '4':
        print("Exiting...")

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()
