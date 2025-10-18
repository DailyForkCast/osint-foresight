#!/usr/bin/env python3
"""
Run All Concurrent Data Processing Tasks
Executes multiple data operations in parallel for maximum efficiency
"""

import os
import sys
import json
import tarfile
import gzip
import shutil
import threading
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

class ConcurrentTaskRunner:
    def __init__(self):
        self.start_time = datetime.now()
        self.tasks_status = {}
        self.lock = threading.Lock()

    def update_status(self, task, status):
        """Thread-safe status update"""
        with self.lock:
            self.tasks_status[task] = {
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {task}: {status}")

    def task1_extract_ted_data(self):
        """Extract TED procurement data from tar.gz files"""
        task_name = "TED_EXTRACTION"
        self.update_status(task_name, "Starting...")

        try:
            ted_source = Path("F:/TED_Data/monthly")
            ted_target = Path("F:/DECOMPRESSED_DATA/ted_extracted")
            ted_target.mkdir(parents=True, exist_ok=True)

            # Find all tar.gz files
            tar_files = list(ted_source.rglob("*.tar.gz"))
            self.update_status(task_name, f"Found {len(tar_files)} tar.gz files")

            # Extract first 5 for demonstration
            extracted_count = 0
            for tar_file in tar_files[:5]:
                self.update_status(task_name, f"Extracting {tar_file.name}")

                try:
                    with tarfile.open(tar_file, 'r:gz') as tar:
                        tar.extractall(path=ted_target / tar_file.stem)
                    extracted_count += 1
                except Exception as e:
                    self.update_status(task_name, f"Error with {tar_file.name}: {str(e)[:50]}")

            self.update_status(task_name, f"SUCCESS - Extracted {extracted_count} files")
            return True

        except Exception as e:
            self.update_status(task_name, f"FAILED - {str(e)[:100]}")
            return False

    def task2_create_postgres_scripts(self):
        """Create PostgreSQL restoration scripts and queries"""
        task_name = "POSTGRES_SETUP"
        self.update_status(task_name, "Creating scripts...")

        try:
            scripts_dir = Path("C:/Projects/OSINT - Foresight/postgres_scripts")
            scripts_dir.mkdir(exist_ok=True)

            # Create restore script
            restore_script = """#!/bin/bash
# PostgreSQL USASpending Database Restore

# 1. Create database
createdb -U postgres usaspending

# 2. Restore structure
pg_restore -U postgres -d usaspending -s F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/toc.dat

# 3. Restore data (selective)
for table in vendor contract award; do
    echo "Restoring $table..."
    pg_restore -U postgres -d usaspending -t $table -a F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/toc.dat
done
"""

            with open(scripts_dir / "restore_usaspending.sh", 'w') as f:
                f.write(restore_script)

            # Create China analysis queries
            china_queries = """-- Find China-related vendors
SELECT vendor_name, vendor_country, contract_value, contract_date
FROM vendors
WHERE LOWER(vendor_country) IN ('china', 'cn', 'prc')
   OR LOWER(vendor_name) LIKE '%china%'
   OR LOWER(vendor_name) LIKE '%beijing%'
   OR LOWER(vendor_name) LIKE '%shanghai%';

-- Analyze contracts by year
SELECT EXTRACT(YEAR FROM contract_date) as year,
       COUNT(*) as num_contracts,
       SUM(contract_value) as total_value,
       AVG(contract_value) as avg_value
FROM contracts
WHERE vendor_country = 'CN'
GROUP BY year
ORDER BY year DESC;

-- High-value foreign contracts
SELECT vendor_name, vendor_country,
       SUM(contract_value) as total_value,
       COUNT(*) as num_contracts
FROM contracts
WHERE vendor_country NOT IN ('US', 'USA')
  AND contract_value > 1000000
GROUP BY vendor_name, vendor_country
ORDER BY total_value DESC
LIMIT 100;
"""

            with open(scripts_dir / "china_analysis.sql", 'w') as f:
                f.write(china_queries)

            self.update_status(task_name, "SUCCESS - Scripts created")
            return True

        except Exception as e:
            self.update_status(task_name, f"FAILED - {str(e)[:100]}")
            return False

    def task3_sample_large_json(self):
        """Sample the 51 GB JSON file"""
        task_name = "JSON_SAMPLING"
        self.update_status(task_name, "Starting JSON stream...")

        try:
            json_gz = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5879.dat.gz")

            if not json_gz.exists():
                # Try to find it
                search_path = Path("F:/DECOMPRESSED_DATA")
                found = list(search_path.rglob("5879.dat*"))
                if found:
                    json_gz = found[0]
                    self.update_status(task_name, f"Found at {json_gz}")
                else:
                    self.update_status(task_name, "File not found")
                    return False

            # Sample the file
            sample_lines = []
            line_count = 0

            with gzip.open(json_gz, 'rt', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line_count += 1
                    if line_count <= 1000:
                        sample_lines.append(line[:500])

                    if line_count % 10000 == 0:
                        self.update_status(task_name, f"Processed {line_count:,} lines")

                    if line_count >= 50000:
                        break

            # Save sample
            sample_file = Path("C:/Projects/OSINT - Foresight/json_51gb_sample.json")
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sample_lines))

            self.update_status(task_name, f"SUCCESS - Sampled {line_count:,} lines")
            return True

        except Exception as e:
            self.update_status(task_name, f"FAILED - {str(e)[:100]}")
            return False

    def task4_process_tsv_files(self):
        """Process TSV files in parallel"""
        task_name = "TSV_PROCESSING"
        self.update_status(task_name, "Processing TSV files...")

        try:
            tsv_files = [
                Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5877.dat.gz"),
                Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5878.dat.gz")
            ]

            results = []
            for tsv_file in tsv_files:
                if not tsv_file.exists():
                    self.update_status(task_name, f"{tsv_file.name} not found")
                    continue

                # Sample each file
                self.update_status(task_name, f"Sampling {tsv_file.name}")

                with gzip.open(tsv_file, 'rt', encoding='utf-8', errors='ignore') as f:
                    headers = f.readline().strip().split('\t')
                    sample_rows = []

                    for i, line in enumerate(f):
                        if i >= 100:
                            break
                        sample_rows.append(line.strip().split('\t'))

                    results.append({
                        'file': tsv_file.name,
                        'columns': len(headers),
                        'sample_rows': len(sample_rows)
                    })

            # Save results
            with open("C:/Projects/OSINT - Foresight/tsv_analysis.json", 'w') as f:
                json.dump(results, f, indent=2)

            self.update_status(task_name, f"SUCCESS - Analyzed {len(results)} files")
            return True

        except Exception as e:
            self.update_status(task_name, f"FAILED - {str(e)[:100]}")
            return False

    def task5_prepare_overnight_batch(self):
        """Prepare batch script for overnight decompression"""
        task_name = "BATCH_PREP"
        self.update_status(task_name, "Creating batch scripts...")

        try:
            # Create Python script for overnight processing
            overnight_script = '''#!/usr/bin/env python3
"""Overnight decompression of large files"""

import gzip
import shutil
from pathlib import Path
from datetime import datetime

large_files = [
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5801.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5836.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5847.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat.gz",
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5862.dat.gz"
]

print(f"Starting decompression at {datetime.now()}")

for file_path in large_files:
    gz_file = Path(file_path)
    if gz_file.exists():
        output = gz_file.with_suffix('')
        print(f"Decompressing {gz_file.name} ({gz_file.stat().st_size / 1e9:.1f} GB)...")

        with gzip.open(gz_file, 'rb') as f_in:
            with open(output, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out, length=10*1024*1024)  # 10MB chunks

        print(f"  Done! Output: {output.stat().st_size / 1e9:.1f} GB")
        gz_file.unlink()  # Remove original to save space

print(f"Completed at {datetime.now()}")
'''

            with open("C:/Projects/OSINT - Foresight/overnight_decompress.py", 'w') as f:
                f.write(overnight_script)

            # Create batch file to run it
            batch_file = """@echo off
echo Starting overnight decompression...
echo This will take 8-12 hours
echo.
python overnight_decompress.py > decompression_log.txt 2>&1
echo.
echo Decompression complete! Check decompression_log.txt for details.
pause
"""

            with open("C:/Projects/OSINT - Foresight/run_overnight.bat", 'w') as f:
                f.write(batch_file)

            self.update_status(task_name, "SUCCESS - Overnight scripts ready")
            return True

        except Exception as e:
            self.update_status(task_name, f"FAILED - {str(e)[:100]}")
            return False

    def run_all_tasks(self):
        """Execute all tasks concurrently"""
        print("\n" + "="*70)
        print("CONCURRENT DATA PROCESSING - MAXIMUM EFFICIENCY")
        print("="*70)
        print(f"\nStarting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nRunning 5 tasks in parallel...\n")

        # Create thread pool
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.task1_extract_ted_data): "TED_EXTRACTION",
                executor.submit(self.task2_create_postgres_scripts): "POSTGRES_SETUP",
                executor.submit(self.task3_sample_large_json): "JSON_SAMPLING",
                executor.submit(self.task4_process_tsv_files): "TSV_PROCESSING",
                executor.submit(self.task5_prepare_overnight_batch): "BATCH_PREP"
            }

            # Wait for completion
            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    print(f"\n[ERROR] {task} exception: {e}")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print execution summary"""
        elapsed = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "="*70)
        print("EXECUTION COMPLETE")
        print("="*70)
        print(f"\nTotal time: {elapsed:.1f} seconds")

        print("\nTask Results:")
        print("-" * 40)
        for task, status in self.tasks_status.items():
            status_text = status['status']
            if 'SUCCESS' in status_text:
                symbol = "[OK]"
            elif 'FAILED' in status_text:
                symbol = "[!!]"
            else:
                symbol = "[??]"
            print(f"{symbol} {task}: {status_text}")

        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\n1. TED Data: Check F:/DECOMPRESSED_DATA/ted_extracted/")
        print("2. PostgreSQL: Review postgres_scripts/restore_usaspending.sh")
        print("3. JSON Sample: Check json_51gb_sample.json")
        print("4. TSV Analysis: Review tsv_analysis.json")
        print("5. Overnight: Run 'run_overnight.bat' before bed")

        print("\n6. For immediate China analysis:")
        print("   - Process extracted TED data for EU-China contracts")
        print("   - Search JSON sample for China-related entities")
        print("   - Run SQL queries after PostgreSQL restore")

        # Save status report
        status_report = {
            'execution_time': elapsed,
            'completed_at': datetime.now().isoformat(),
            'tasks': self.tasks_status
        }

        with open("C:/Projects/OSINT - Foresight/concurrent_execution_report.json", 'w') as f:
            json.dump(status_report, f, indent=2)

        print("\n[Status report saved to concurrent_execution_report.json]")


if __name__ == "__main__":
    runner = ConcurrentTaskRunner()
    runner.run_all_tasks()
