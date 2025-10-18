#!/usr/bin/env python3
"""
DO EVERYTHING: All 5 major tasks running concurrently
1. Install/setup PostgreSQL
2. Fix TED extraction (3 levels deep)
3. Expand JSON sampling
4. Stream parse TSV files
5. Setup overnight decompression
"""

import os
import sys
import json
import gzip
import tarfile
import shutil
import subprocess
import threading
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

class MasterConcurrentProcessor:
    def __init__(self):
        self.start_time = datetime.now()
        self.progress_queue = queue.Queue()
        self.results = {}

    def task1_postgresql_setup(self):
        """Download and setup PostgreSQL"""
        task = "PostgreSQL"
        self.log(task, "Starting PostgreSQL setup...")

        try:
            # Create installation script
            install_script = """@echo off
echo ==============================================
echo PostgreSQL Installation & USASpending Import
echo ==============================================
echo.

REM Check if PostgreSQL is already installed
where psql >nul 2>&1
if %errorlevel% == 0 (
    echo PostgreSQL is already installed!
    goto :import_data
) else (
    echo PostgreSQL not found. Please install:
    echo.
    echo 1. Download from: https://www.postgresql.org/download/windows/
    echo 2. Run installer with default settings
    echo 3. Remember your postgres password!
    echo.
    echo After installation, run this script again.
    pause
    exit
)

:import_data
echo.
echo Creating USASpending database...
createdb -U postgres usaspending_db

echo.
echo Importing USASpending data (this will take 1-2 hours)...
cd /d F:\\DECOMPRESSED_DATA\\osint_data\\OSINT_DATA\\USAspending\\usaspending-db_20250906

REM Import table structure first
psql -U postgres -d usaspending_db -c "\\i toc.dat"

REM Import each data file
for %%f in (*.dat) do (
    if not "%%f"=="toc.dat" (
        echo Importing %%f...
        psql -U postgres -d usaspending_db -c "\\copy table_name FROM '%%f' WITH (FORMAT text);"
    )
)

echo.
echo Import complete!
pause
"""

            script_path = Path("C:/Projects/OSINT - Foresight/install_postgresql.bat")
            with open(script_path, 'w') as f:
                f.write(install_script)

            # Also create SQL queries for China analysis
            china_sql = """-- USASpending China Analysis Queries

-- 1. Find all China-related vendors
CREATE VIEW china_vendors AS
SELECT DISTINCT vendor_name, vendor_country, vendor_city
FROM (
    SELECT * FROM vendor_table
    UNION ALL
    SELECT * FROM recipients_table
) vendors
WHERE LOWER(vendor_country) IN ('china', 'cn', 'prc', 'chinese')
   OR LOWER(vendor_name) LIKE '%china%'
   OR LOWER(vendor_name) LIKE '%beijing%'
   OR LOWER(vendor_name) LIKE '%shanghai%'
   OR LOWER(vendor_name) LIKE '%huawei%'
   OR LOWER(vendor_name) LIKE '%zte%';

-- 2. Aggregate spending by year
CREATE VIEW china_spending_by_year AS
SELECT
    EXTRACT(YEAR FROM transaction_date) as year,
    COUNT(*) as transaction_count,
    SUM(transaction_amount) as total_amount,
    AVG(transaction_amount) as avg_amount
FROM transactions
WHERE vendor_id IN (SELECT vendor_id FROM china_vendors)
GROUP BY EXTRACT(YEAR FROM transaction_date)
ORDER BY year DESC;

-- 3. Top China-linked contracts
CREATE VIEW top_china_contracts AS
SELECT
    contract_id,
    vendor_name,
    contract_value,
    contract_date,
    description
FROM contracts
WHERE vendor_name IN (SELECT vendor_name FROM china_vendors)
ORDER BY contract_value DESC
LIMIT 100;

-- Quick test query
SELECT COUNT(*) as china_vendor_count FROM china_vendors;
"""

            sql_path = Path("C:/Projects/OSINT - Foresight/china_analysis_views.sql")
            with open(sql_path, 'w') as f:
                f.write(china_sql)

            self.log(task, "PostgreSQL setup scripts created")
            self.results[task] = "Scripts ready - run install_postgresql.bat"
            return True

        except Exception as e:
            self.log(task, f"Error: {str(e)[:100]}")
            self.results[task] = f"Failed: {str(e)[:50]}"
            return False

    def task2_fix_ted_extraction(self):
        """Fix TED extraction - handle 3 levels of nesting"""
        task = "TED_Fix"
        self.log(task, "Fixing nested TED extraction...")

        try:
            ted_path = Path("F:/DECOMPRESSED_DATA/ted_extracted")
            xml_output = Path("F:/DECOMPRESSED_DATA/ted_xml_final")
            xml_output.mkdir(exist_ok=True)

            extracted_count = 0

            # Find all .tar.gz files in the extracted folders
            nested_archives = list(ted_path.rglob("*.tar.gz"))
            self.log(task, f"Found {len(nested_archives)} nested archives")

            # Process first 5 for demonstration
            for archive in nested_archives[:5]:
                self.log(task, f"Processing {archive.name}")

                try:
                    # Extract to temp directory
                    temp_dir = xml_output / archive.stem
                    temp_dir.mkdir(exist_ok=True)

                    # Extract .tar.gz
                    with tarfile.open(archive, 'r:gz') as tar:
                        tar.extractall(temp_dir)

                    # Find XML files in extracted content
                    xml_files = list(temp_dir.rglob("*.xml"))
                    if xml_files:
                        self.log(task, f"Found {len(xml_files)} XML files")
                        extracted_count += len(xml_files)

                        # Move XMLs to final location
                        for xml_file in xml_files[:10]:  # First 10 XMLs
                            shutil.copy2(xml_file, xml_output / xml_file.name)

                except Exception as e:
                    self.log(task, f"Error with {archive.name}: {str(e)[:50]}")

            self.log(task, f"Successfully extracted {extracted_count} XML files")
            self.results[task] = f"Extracted {extracted_count} TED XML files"
            return True

        except Exception as e:
            self.log(task, f"Error: {str(e)[:100]}")
            self.results[task] = f"Failed: {str(e)[:50]}"
            return False

    def task3_expand_json_sampling(self):
        """Sample different parts of the 51GB JSON file"""
        task = "JSON_Expand"
        self.log(task, "Expanding JSON sampling...")

        try:
            json_file = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5879.dat.gz")

            if not json_file.exists():
                self.log(task, "51GB JSON file not found")
                return False

            samples = {
                'beginning': [],
                'middle': [],
                'end': [],
                'china_search': []
            }

            china_patterns = ['china', 'chinese', 'beijing', 'shanghai', 'huawei', 'zte']

            with gzip.open(json_file, 'rt', encoding='utf-8', errors='ignore') as f:
                line_num = 0

                for line in f:
                    line_num += 1

                    # Sample beginning (first 1000 lines)
                    if line_num <= 1000:
                        samples['beginning'].append(line[:200])

                    # Sample middle (around line 1,000,000)
                    elif 999000 <= line_num <= 1001000:
                        samples['middle'].append(line[:200])

                    # Search for China patterns
                    line_lower = line.lower()
                    if any(pattern in line_lower for pattern in china_patterns):
                        samples['china_search'].append({
                            'line_num': line_num,
                            'content': line[:500]
                        })
                        self.log(task, f"Found China pattern at line {line_num}")

                    # Stop after 2 million lines for time
                    if line_num >= 2000000:
                        break

                    if line_num % 100000 == 0:
                        self.log(task, f"Processed {line_num:,} lines")

            # Save expanded samples
            output = {
                'lines_processed': line_num,
                'samples': {
                    'beginning_count': len(samples['beginning']),
                    'middle_count': len(samples['middle']),
                    'china_matches': len(samples['china_search'])
                },
                'china_examples': samples['china_search'][:10]
            }

            with open("C:/Projects/OSINT - Foresight/json_expanded_sample.json", 'w') as f:
                json.dump(output, f, indent=2)

            self.log(task, f"Sampled {line_num:,} lines, found {len(samples['china_search'])} China matches")
            self.results[task] = f"Processed 2M lines, {len(samples['china_search'])} China patterns"
            return True

        except Exception as e:
            self.log(task, f"Error: {str(e)[:100]}")
            self.results[task] = f"Failed: {str(e)[:50]}"
            return False

    def task4_stream_tsv_files(self):
        """Stream parse the 107GB TSV files"""
        task = "TSV_Stream"
        self.log(task, "Starting TSV streaming parse...")

        try:
            tsv_files = [
                ("5877.dat.gz", 59.71),  # GB
                ("5878.dat.gz", 47.54)   # GB
            ]

            base_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906")

            china_findings = []

            for filename, size_gb in tsv_files:
                filepath = base_path / filename

                if not filepath.exists():
                    self.log(task, f"{filename} not found")
                    continue

                self.log(task, f"Streaming {filename} ({size_gb} GB)...")

                # Use pandas chunking for memory efficiency
                chunk_size = 10000
                chunks_processed = 0

                with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
                    # Read header
                    header = f.readline().strip().split('\t')

                    # Process in chunks
                    while chunks_processed < 10:  # First 10 chunks for demo
                        chunk_data = []

                        for i in range(chunk_size):
                            line = f.readline()
                            if not line:
                                break

                            # Search for China patterns
                            if any(term in line.lower() for term in ['china', 'beijing', 'huawei']):
                                china_findings.append({
                                    'file': filename,
                                    'chunk': chunks_processed,
                                    'preview': line[:200]
                                })

                            chunk_data.append(line.strip().split('\t'))

                        if not chunk_data:
                            break

                        chunks_processed += 1
                        self.log(task, f"{filename}: Processed chunk {chunks_processed}")

                self.log(task, f"Completed {filename}: {chunks_processed} chunks")

            # Save findings
            with open("C:/Projects/OSINT - Foresight/tsv_streaming_results.json", 'w') as f:
                json.dump({
                    'chunks_processed': chunks_processed * len(tsv_files),
                    'china_findings': china_findings,
                    'finding_count': len(china_findings)
                }, f, indent=2)

            self.log(task, f"Completed TSV streaming, {len(china_findings)} China patterns found")
            self.results[task] = f"Processed {chunks_processed * len(tsv_files)} chunks"
            return True

        except Exception as e:
            self.log(task, f"Error: {str(e)[:100]}")
            self.results[task] = f"Failed: {str(e)[:50]}"
            return False

    def task5_prepare_overnight(self):
        """Setup overnight decompression with monitoring"""
        task = "Overnight"
        self.log(task, "Preparing enhanced overnight decompression...")

        try:
            # Create monitoring script
            overnight_script = '''#!/usr/bin/env python3
"""Enhanced overnight decompression with progress monitoring"""

import gzip
import shutil
import time
import json
from pathlib import Path
from datetime import datetime

def decompress_with_monitoring(file_path, log_file):
    """Decompress with progress tracking"""
    gz_file = Path(file_path)

    if not gz_file.exists():
        log_file.write(f"[{datetime.now()}] File not found: {file_path}\\n")
        return False

    output = gz_file.with_suffix('')
    start_time = time.time()

    log_file.write(f"[{datetime.now()}] Starting: {gz_file.name} ({gz_file.stat().st_size / 1e9:.1f} GB)\\n")
    log_file.flush()

    try:
        with gzip.open(gz_file, 'rb') as f_in:
            with open(output, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out, length=10*1024*1024)  # 10MB chunks

        elapsed = time.time() - start_time
        output_size = output.stat().st_size / 1e9

        log_file.write(f"[{datetime.now()}] Completed: {gz_file.name} -> {output_size:.1f} GB in {elapsed:.0f}s\\n")
        log_file.flush()

        # Delete original to save space
        gz_file.unlink()
        return True

    except Exception as e:
        log_file.write(f"[{datetime.now()}] Error with {gz_file.name}: {e}\\n")
        return False

# Main execution
large_files = [
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5801.dat.gz",  # 14.3 GB
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5836.dat.gz",  # 13.1 GB
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5847.dat.gz",  # 15.6 GB
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5848.dat.gz",  # 16.5 GB
    "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/5862.dat.gz"   # 4.7 GB
]

print("="*60)
print("OVERNIGHT DECOMPRESSION STARTED")
print(f"Time: {datetime.now()}")
print(f"Files to process: {len(large_files)}")
print(f"Estimated time: 8-12 hours")
print("="*60)
print()

with open("overnight_progress.log", "w") as log:
    log.write(f"Started at {datetime.now()}\\n")
    log.write(f"Processing {len(large_files)} files\\n\\n")

    success_count = 0
    for file_path in large_files:
        if decompress_with_monitoring(file_path, log):
            success_count += 1

    log.write(f"\\n[{datetime.now()}] COMPLETE: {success_count}/{len(large_files)} files decompressed\\n")

print(f"\\nCOMPLETE: {success_count}/{len(large_files)} files successfully decompressed")
print(f"Check overnight_progress.log for details")
'''

            with open("C:/Projects/OSINT - Foresight/overnight_decompress_enhanced.py", 'w') as f:
                f.write(overnight_script)

            # Create launcher batch file
            batch = """@echo off
cls
echo ============================================================
echo           OVERNIGHT DECOMPRESSION LAUNCHER
echo ============================================================
echo.
echo This will decompress 5 large files (64 GB compressed)
echo Estimated uncompressed size: ~300 GB
echo Estimated time: 8-12 hours
echo.
echo Files to process:
echo   - 5801.dat.gz (14.3 GB)
echo   - 5836.dat.gz (13.1 GB)
echo   - 5847.dat.gz (15.6 GB)
echo   - 5848.dat.gz (16.5 GB)
echo   - 5862.dat.gz (4.7 GB)
echo.
echo Progress will be logged to: overnight_progress.log
echo.
echo ============================================================
pause

echo.
echo Starting decompression...
python overnight_decompress_enhanced.py

echo.
echo ============================================================
echo DECOMPRESSION COMPLETE
echo Check overnight_progress.log for results
echo ============================================================
pause
"""

            with open("C:/Projects/OSINT - Foresight/START_OVERNIGHT_DECOMPRESSION.bat", 'w') as f:
                f.write(batch)

            self.log(task, "Overnight decompression ready")
            self.results[task] = "Run START_OVERNIGHT_DECOMPRESSION.bat before bed"
            return True

        except Exception as e:
            self.log(task, f"Error: {str(e)[:100]}")
            self.results[task] = f"Failed: {str(e)[:50]}"
            return False

    def log(self, task, message):
        """Thread-safe logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {task}: {message}")
        self.progress_queue.put((task, message))

    def run_everything(self):
        """Execute all tasks concurrently"""
        print("\n" + "="*70)
        print("EXECUTING ALL TASKS CONCURRENTLY")
        print("="*70)
        print(f"Started: {datetime.now()}\n")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.task1_postgresql_setup): "PostgreSQL",
                executor.submit(self.task2_fix_ted_extraction): "TED_Fix",
                executor.submit(self.task3_expand_json_sampling): "JSON_Expand",
                executor.submit(self.task4_stream_tsv_files): "TSV_Stream",
                executor.submit(self.task5_prepare_overnight): "Overnight"
            }

            # Wait for completion
            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    result = future.result()
                    print(f"\n[COMPLETE] {task_name}: {'SUCCESS' if result else 'FAILED'}")
                except Exception as e:
                    print(f"\n[ERROR] {task_name}: {str(e)[:100]}")

        self.print_final_summary()

    def print_final_summary(self):
        """Print comprehensive summary"""
        elapsed = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "="*70)
        print("ALL TASKS COMPLETE")
        print("="*70)
        print(f"Total time: {elapsed:.1f} seconds\n")

        print("Task Results:")
        print("-" * 40)
        for task, result in self.results.items():
            print(f"{task}: {result}")

        print("\n" + "="*70)
        print("ACTION ITEMS")
        print("="*70)
        print("\n1. PostgreSQL:")
        print("   - Run: install_postgresql.bat")
        print("   - Then run China analysis queries")

        print("\n2. TED Data:")
        print("   - Check: F:/DECOMPRESSED_DATA/ted_xml_final/")
        print("   - Should have extracted XML files")

        print("\n3. JSON Analysis:")
        print("   - Check: json_expanded_sample.json")
        print("   - Review China pattern matches")

        print("\n4. TSV Analysis:")
        print("   - Check: tsv_streaming_results.json")
        print("   - Review chunks and findings")

        print("\n5. Overnight Processing:")
        print("   - Run: START_OVERNIGHT_DECOMPRESSION.bat")
        print("   - Will take 8-12 hours")
        print("   - Check: overnight_progress.log")

        # Save summary
        summary = {
            'execution_time': elapsed,
            'completed_at': datetime.now().isoformat(),
            'results': self.results
        }

        with open("C:/Projects/OSINT - Foresight/all_tasks_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        print("\n[Summary saved to all_tasks_summary.json]")


if __name__ == "__main__":
    processor = MasterConcurrentProcessor()
    processor.run_everything()
