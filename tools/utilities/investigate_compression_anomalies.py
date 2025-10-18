#!/usr/bin/env python3
"""
Investigate compression anomalies in USASpending files
Check for parsing errors or incomplete decompression
"""

import gzip
from pathlib import Path
import hashlib

def investigate_files():
    base = "F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/"

    files_to_check = {
        '5801': {'expected_ratio': 3.0, 'actual_ratio': 0.2},  # ANOMALY: Smaller after decompression!
        '5836': {'expected_ratio': 3.0, 'actual_ratio': 9.5},  # Normal
        '5847': {'expected_ratio': 9.5, 'actual_ratio': 6.0},  # Lower than expected
    }

    print("="*70)
    print("COMPRESSION ANOMALY INVESTIGATION")
    print("="*70)

    for filename, ratios in files_to_check.items():
        dat_file = Path(base + filename + '.dat')
        gz_file = Path(base + filename + '.dat.gz')

        print(f"\n[{filename}]")
        print("-"*40)

        # Check file sizes
        if dat_file.exists():
            dat_size = dat_file.stat().st_size
            print(f"  .dat file size: {dat_size/1e9:.2f} GB ({dat_size:,} bytes)")

            # Check if file looks complete (has data at the end)
            with open(dat_file, 'rb') as f:
                # Check beginning
                f.seek(0)
                first_bytes = f.read(100)

                # Check end
                f.seek(max(0, dat_size - 1000))
                last_bytes = f.read(1000)

                # Check for PostgreSQL COPY format markers
                has_pgcopy_header = first_bytes.startswith(b'PGDMP') or first_bytes.startswith(b'PGCOPY')
                has_end_marker = b'\\.' in last_bytes or last_bytes.strip().endswith(b'\\.')

                print(f"  First 50 bytes: {first_bytes[:50]}")
                print(f"  Last 50 bytes: {last_bytes[-50:]}")

                if has_pgcopy_header:
                    print("  [!] PostgreSQL COPY format detected")
                if has_end_marker:
                    print("  [!] PostgreSQL end marker found")

                # Check for NULL bytes (might indicate corruption)
                null_count = first_bytes.count(b'\x00') + last_bytes.count(b'\x00')
                if null_count > 0:
                    print(f"  [WARNING] Found {null_count} NULL bytes - possible corruption")

                # Count lines to estimate records
                print("  Counting lines (first 10MB)...")
                f.seek(0)
                line_count = 0
                bytes_read = 0
                for line in f:
                    line_count += 1
                    bytes_read += len(line)
                    if bytes_read > 10*1024*1024:  # 10MB sample
                        break

                estimated_total_lines = int(line_count * (dat_size / bytes_read))
                print(f"  Lines in first 10MB: {line_count:,}")
                print(f"  Estimated total lines: {estimated_total_lines:,}")
        else:
            print(f"  .dat file NOT FOUND")

        # Check if .gz still exists
        if gz_file.exists():
            gz_size = gz_file.stat().st_size
            print(f"  .gz file size: {gz_size/1e9:.2f} GB")

            if dat_file.exists():
                actual_ratio = dat_size / gz_size
                print(f"  Actual compression ratio: {actual_ratio:.2f}x")
                print(f"  Expected ratio: ~{ratios['expected_ratio']:.1f}x")

                if actual_ratio < 1.0:
                    print("  [CRITICAL] File is SMALLER after decompression!")
                    print("  [ACTION] Need to re-decompress this file")
                elif actual_ratio < 2.0:
                    print("  [WARNING] Low compression ratio - might be incomplete")

            # Test decompress first 1MB to verify it's actually gzipped
            print("  Testing gzip integrity...")
            try:
                with gzip.open(gz_file, 'rb') as f:
                    test_data = f.read(1024*1024)  # Read 1MB
                    print(f"  [OK] Gzip header valid, read {len(test_data):,} bytes")
            except Exception as e:
                print(f"  [ERROR] Gzip read failed: {e}")
        else:
            print(f"  .gz file deleted/missing")

    # Check our decompression scripts for errors
    print("\n" + "="*70)
    print("DECOMPRESSION SCRIPT ANALYSIS")
    print("="*70)

    scripts_to_check = [
        "overnight_decompress.py",
        "smart_overnight_decompress.py",
        "fixed_overnight_decompress.py",
        "scripts/overnight_decompress_enhanced.py"
    ]

    for script_name in scripts_to_check:
        script_path = Path("C:/Projects/OSINT - Foresight") / script_name
        if script_path.exists():
            print(f"\n[{script_name}]")
            with open(script_path, 'r') as f:
                content = f.read()

                # Check for common issues
                issues = []

                # Check if using binary mode
                if "'rb'" not in content and '"rb"' not in content:
                    issues.append("Not opening .gz in binary mode")

                # Check if using gzip.open
                if "gzip.open" not in content:
                    issues.append("Not using gzip.open")

                # Check chunk size
                if "1024*1024" in content or "1024 * 1024" in content:
                    chunk_size = "1MB"
                elif "10*1024*1024" in content:
                    chunk_size = "10MB"
                else:
                    chunk_size = "Unknown"
                print(f"  Chunk size: {chunk_size}")

                # Check if deleting original
                if ".unlink()" in content or "os.remove" in content:
                    print("  [!] Script deletes original .gz files")

                if issues:
                    print(f"  Issues found: {', '.join(issues)}")
                else:
                    print("  No obvious issues found")

if __name__ == "__main__":
    investigate_files()
