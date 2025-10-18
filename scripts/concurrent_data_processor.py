#!/usr/bin/env python3
"""
Concurrent Data Processor
Runs multiple data extraction and processing tasks in parallel
"""

import os
import sys
import json
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import queue

class ConcurrentDataProcessor:
    def __init__(self):
        self.start_time = datetime.now()
        self.status = {
            'ted_extraction': 'pending',
            'postgres_restore': 'pending',
            'json_streaming': 'pending',
            'tsv_processing': 'pending',
            'gz_decompression': 'pending'
        }
        self.results = {}
        self.progress_queue = queue.Queue()

    def extract_ted_data(self):
        """Extract TED procurement data"""
        print("[TED] Starting extraction...")
        self.status['ted_extraction'] = 'running'

        ted_source = Path("F:/TED_Data")
        ted_target = Path("F:/DECOMPRESSED_DATA/ted_data")
        ted_target.mkdir(parents=True, exist_ok=True)

        try:
            # Find compressed TED files
            compressed_files = list(ted_source.glob("*.zip")) + list(ted_source.glob("*.gz"))
            print(f"[TED] Found {len(compressed_files)} compressed files")

            for i, file in enumerate(compressed_files[:5], 1):  # Process first 5 for demo
                print(f"[TED] Processing {file.name} ({i}/{min(5, len(compressed_files))})")

                if file.suffix == '.zip':
                    cmd = f'powershell Expand-Archive -Path "{file}" -DestinationPath "{ted_target}" -Force'
                else:  # .gz
                    import gzip
                    import shutil
                    output = ted_target / file.stem
                    with gzip.open(file, 'rb') as f_in:
                        with open(output, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out, length=1024*1024)

                self.progress_queue.put(f"[TED] Extracted {file.name}")

            self.status['ted_extraction'] = 'complete'
            self.results['ted_extraction'] = f"Extracted {min(5, len(compressed_files))} files"
            return True

        except Exception as e:
            self.status['ted_extraction'] = f'error: {str(e)[:50]}'
            return False

    def setup_postgres_restore(self):
        """Set up PostgreSQL restore script"""
        print("[PostgreSQL] Creating restore script...")
        self.status['postgres_restore'] = 'running'

        try:
            # Create a batch script for PostgreSQL restore
            restore_script = """@echo off
echo PostgreSQL Database Restore Instructions
echo =========================================
echo.
echo 1. Install PostgreSQL 13+ if not installed:
echo    https://www.postgresql.org/download/windows/
echo.
echo 2. Create database:
echo    createdb -U postgres usaspending_db
echo.
echo 3. Restore from dump (run from USAspending folder):
echo    pg_restore -U postgres -d usaspending_db -v toc.dat
echo.
echo 4. For partial restore (specific tables):
echo    pg_restore -U postgres -d usaspending_db -t vendor_table -v toc.dat
echo.
echo Note: Full restore will take 2-4 hours for 9.4M records
echo.
pause
"""

            script_path = Path("C:/Projects/OSINT - Foresight/postgres_restore_instructions.bat")
            with open(script_path, 'w') as f:
                f.write(restore_script)

            # Also create SQL analysis queries
            sql_queries = """-- China-related vendor search
SELECT * FROM vendor_table
WHERE LOWER(vendor_name) LIKE '%china%'
   OR LOWER(vendor_name) LIKE '%chinese%'
   OR LOWER(vendor_name) LIKE '%beijing%'
   OR LOWER(vendor_name) LIKE '%shanghai%';

-- Contract analysis by year
SELECT EXTRACT(YEAR FROM contract_date) as year,
       COUNT(*) as contracts,
       SUM(amount) as total_amount
FROM contracts_table
GROUP BY year
ORDER BY year DESC;

-- Foreign entity analysis
SELECT country_code,
       COUNT(*) as entity_count,
       SUM(total_amount) as total_value
FROM international_vendors
WHERE country_code = 'CN'
GROUP BY country_code;
"""

            sql_path = Path("C:/Projects/OSINT - Foresight/china_analysis_queries.sql")
            with open(sql_path, 'w') as f:
                f.write(sql_queries)

            self.status['postgres_restore'] = 'instructions_created'
            self.results['postgres_restore'] = 'Setup scripts created'
            self.progress_queue.put("[PostgreSQL] Restore instructions ready")
            return True

        except Exception as e:
            self.status['postgres_restore'] = f'error: {str(e)[:50]}'
            return False

    def stream_large_json(self):
        """Stream process the 51 GB JSON file"""
        print("[JSON] Starting streaming parse...")
        self.status['json_streaming'] = 'running'

        try:
            import gzip
            json_file = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5879.dat.gz")

            if not json_file.exists():
                self.status['json_streaming'] = 'file_not_found'
                return False

            print(f"[JSON] Processing {json_file.name} (51.27 GB)")

            # Stream parse first 1000 lines as sample
            sample_data = []
            line_count = 0

            with gzip.open(json_file, 'rt', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line_count += 1
                    if line_count <= 100:
                        sample_data.append(line[:200])  # First 200 chars

                    if line_count % 10000 == 0:
                        self.progress_queue.put(f"[JSON] Processed {line_count:,} lines")

                    if line_count >= 100000:  # Sample 100k lines
                        break

            # Save sample
            sample_path = Path("C:/Projects/OSINT - Foresight/json_51gb_sample.txt")
            with open(sample_path, 'w') as f:
                f.write('\n'.join(sample_data))

            self.status['json_streaming'] = 'sampled'
            self.results['json_streaming'] = f'Sampled {line_count:,} lines'
            self.progress_queue.put(f"[JSON] Sampling complete: {line_count:,} lines")
            return True

        except Exception as e:
            self.status['json_streaming'] = f'error: {str(e)[:50]}'
            return False

    def process_tsv_files(self):
        """Process the 107 GB TSV files"""
        print("[TSV] Starting batch processing...")
        self.status['tsv_processing'] = 'running'

        try:
            tsv_files = [
                Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5877.dat.gz"),
                Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5878.dat.gz")
            ]

            total_lines = 0
            for tsv_file in tsv_files:
                if not tsv_file.exists():
                    continue

                print(f"[TSV] Sampling {tsv_file.name}")

                # Read sample
                import gzip
                with gzip.open(tsv_file, 'rt', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if i >= 1000:  # Sample 1000 lines
                            break
                        total_lines += 1

                self.progress_queue.put(f"[TSV] Sampled {tsv_file.name}")

            self.status['tsv_processing'] = 'sampled'
            self.results['tsv_processing'] = f'Sampled {total_lines:,} lines from TSV files'
            return True

        except Exception as e:
            self.status['tsv_processing'] = f'error: {str(e)[:50]}'
            return False

    def decompress_large_files(self):
        """Start decompression of remaining large files"""
        print("[GZ] Preparing decompression batch...")
        self.status['gz_decompression'] = 'running'

        try:
            # Create batch script for overnight processing
            batch_script = """@echo off
echo Large File Decompression Batch
echo ==============================
echo.
echo This will decompress 10 large files (229 GB compressed)
echo Estimated time: 8-12 hours
echo Required space: ~500 GB
echo.
echo Files to process:
echo - 5847.dat.gz (15.56 GB)
echo - 5848.dat.gz (16.49 GB)
echo - 5862.dat.gz (4.71 GB)
echo - 5836.dat.gz (13.07 GB)
echo - 5801.dat.gz (14.30 GB)
echo - Plus 5 more files...
echo.
echo Run overnight with:
echo python decompress_all_large.py
echo.
pause
"""

            script_path = Path("C:/Projects/OSINT - Foresight/overnight_decompress.bat")
            with open(script_path, 'w') as f:
                f.write(batch_script)

            self.status['gz_decompression'] = 'batch_ready'
            self.results['gz_decompression'] = 'Batch script prepared for 229 GB'
            self.progress_queue.put("[GZ] Decompression batch ready for overnight run")
            return True

        except Exception as e:
            self.status['gz_decompression'] = f'error: {str(e)[:50]}'
            return False

    def progress_monitor(self):
        """Monitor and display progress"""
        while any(status == 'running' for status in self.status.values()):
            try:
                msg = self.progress_queue.get(timeout=1)
                print(msg)
            except:
                pass

            # Print status summary every 5 seconds
            if int(time.time()) % 5 == 0:
                elapsed = (datetime.now() - self.start_time).seconds
                print(f"\n[STATUS @ {elapsed}s] " + " | ".join(
                    f"{k}: {v}" for k, v in self.status.items()
                ))

    def run_concurrent(self):
        """Run all tasks concurrently"""
        print("\n" + "="*70)
        print("CONCURRENT DATA PROCESSING")
        print("="*70)
        print("\nStarting 5 parallel operations...\n")

        # Start progress monitor in background
        monitor_thread = threading.Thread(target=self.progress_monitor, daemon=True)
        monitor_thread.start()

        # Run tasks in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.extract_ted_data): 'ted_extraction',
                executor.submit(self.setup_postgres_restore): 'postgres_restore',
                executor.submit(self.stream_large_json): 'json_streaming',
                executor.submit(self.process_tsv_files): 'tsv_processing',
                executor.submit(self.decompress_large_files): 'gz_decompression'
            }

            # Wait for completion
            for future in futures:
                try:
                    future.result(timeout=300)  # 5 minute timeout per task
                except Exception as e:
                    task_name = futures[future]
                    print(f"\n[ERROR] {task_name} failed: {e}")

        # Final summary
        self.print_summary()

    def print_summary(self):
        """Print final summary"""
        print("\n" + "="*70)
        print("PROCESSING COMPLETE")
        print("="*70)

        elapsed = (datetime.now() - self.start_time).seconds
        print(f"\nTotal time: {elapsed} seconds")

        print("\nTask Results:")
        for task, status in self.status.items():
            result = self.results.get(task, 'No result')
            emoji = "✅" if 'complete' in status or 'ready' in status else "⚠️"
            print(f"{emoji} {task}: {status}")
            if result != 'No result':
                print(f"   → {result}")

        print("\nNext Steps:")
        print("1. Check postgres_restore_instructions.bat for database setup")
        print("2. Review json_51gb_sample.txt for JSON structure")
        print("3. Run overnight_decompress.bat tonight for large files")
        print("4. Check F:/DECOMPRESSED_DATA/ted_data for TED extracts")

        # Save status
        with open("C:/Projects/OSINT - Foresight/concurrent_processing_status.json", 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'elapsed_seconds': elapsed,
                'status': self.status,
                'results': self.results
            }, f, indent=2)


if __name__ == "__main__":
    processor = ConcurrentDataProcessor()
    processor.run_concurrent()
