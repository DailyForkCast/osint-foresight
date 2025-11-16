#!/usr/bin/env python3
"""Extract a sample UBL XML file from February 2024 for testing"""

import tarfile
from pathlib import Path

# Find February 2024 archive
source_dir = Path("F:/TED_Data/monthly/2024")
feb_archive = source_dir / "TED_monthly_2024_02.tar.gz"

if not feb_archive.exists():
    print(f"February 2024 archive not found: {feb_archive}")
    exit(1)

# Extract location
sample_dir = Path("C:/Projects/OSINT - Foresight/data/temp/ubl_test_sample")
sample_dir.mkdir(parents=True, exist_ok=True)

print(f"Extracting UBL sample from: {feb_archive.name}")

try:
    # Open outer archive
    with tarfile.open(feb_archive, 'r:gz', errorlevel=0) as outer_tar:
        # Get first inner archive (likely Era 3)
        inner_archives = [m for m in outer_tar.getmembers() if m.name.endswith('.tar.gz')]

        # Try the 10th inner archive (should be Era 3 based on our analysis)
        if len(inner_archives) >= 10:
            inner_member = inner_archives[9]  # 10th archive (80% through month)
            print(f"  Extracting: {inner_member.name}")

            outer_tar.extract(inner_member, sample_dir)
            inner_path = sample_dir / inner_member.name

            # Open inner archive
            with tarfile.open(inner_path, 'r:gz', errorlevel=0) as inner_tar:
                # Extract first 3 XML files
                xml_members = [m for m in inner_tar.getmembers() if m.name.endswith('.xml')][:3]

                for xml_member in xml_members:
                    inner_tar.extract(xml_member, sample_dir)
                    print(f"  [OK] Extracted: {xml_member.name}")

            # Cleanup inner archive
            inner_path.unlink()

            print(f"\n[SUCCESS] Sample files extracted to: {sample_dir}")
            print(f"  Total XML files: {len(xml_members)}")

            # List extracted files
            xml_files = list(sample_dir.glob("**/*.xml"))
            print(f"\nExtracted XML files:")
            for xml_file in xml_files:
                print(f"  - {xml_file}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
