#!/usr/bin/env python3
"""
Verify PostgreSQL end markers in all USASpending data files
The end marker '\.' indicates complete COPY format data
"""

from pathlib import Path

def verify_markers():
    base_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")

    print("=" * 70)
    print("POSTGRESQL END MARKER VERIFICATION")
    print("=" * 70)

    # Check the 5 large files
    large_files = ['5801', '5836', '5847', '5848', '5862']

    results = []
    for name in large_files:
        dat_file = base_path / f"{name}.dat"

        if dat_file.exists():
            size_gb = dat_file.stat().st_size / 1e9

            # Check last 1KB for end marker
            with open(dat_file, 'rb') as f:
                # Also check first bytes for header
                f.seek(0)
                first_100 = f.read(100)

                # Check end
                f.seek(max(0, dat_file.stat().st_size - 1000))
                last_1000 = f.read(1000)

                # Look for PostgreSQL COPY end marker
                has_end_marker = b'\\.' in last_1000 or last_1000.strip().endswith(b'\\.')

                # Check for PGDMP header (PostgreSQL dump)
                has_pgdmp = first_100.startswith(b'PGDMP')

                result = {
                    'file': name,
                    'size_gb': size_gb,
                    'has_end_marker': has_end_marker,
                    'has_pgdmp': has_pgdmp,
                    'first_50': first_100[:50],
                    'last_50': last_1000[-50:]
                }
                results.append(result)

                # Display result
                status = "COMPLETE" if has_end_marker else "INCOMPLETE/CHECKING"
                marker = "[OK]" if has_end_marker else "[X]"

                print(f"\n{name}.dat ({size_gb:.2f} GB)")
                print(f"  End marker: {marker} {status}")
                print(f"  First 50 bytes: {first_100[:50]}")
                print(f"  Last 50 bytes: {last_1000[-50:]}")

                if has_pgdmp:
                    print("  [!] File has PGDMP header (PostgreSQL dump format)")
        else:
            print(f"\n{name}.dat - NOT FOUND")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("-" * 70)

    complete_files = [r for r in results if r['has_end_marker']]
    incomplete_files = [r for r in results if not r['has_end_marker']]

    print(f"Complete files (with end marker): {len(complete_files)}")
    for r in complete_files:
        print(f"  [OK] {r['file']}.dat - {r['size_gb']:.2f} GB")

    if incomplete_files:
        print(f"\nIncomplete/Processing files: {len(incomplete_files)}")
        for r in incomplete_files:
            print(f"  [X] {r['file']}.dat - {r['size_gb']:.2f} GB")

    # Check if 5801 is still being written
    if '5801' in [r['file'] for r in incomplete_files]:
        print("\nNote: 5801.dat is currently being re-decompressed.")
        print("Run this script again after decompression completes.")

    return results

if __name__ == "__main__":
    verify_markers()
