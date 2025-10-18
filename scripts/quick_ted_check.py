#!/usr/bin/env python3
"""
Quick check of TED archive contents
"""

import tarfile
from pathlib import Path

def check_ted_archive():
    # Pick a sample TED file
    sample = Path("F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz")
    
    print(f"Checking {sample}...\n")
    
    with tarfile.open(sample, 'r:gz') as outer:
        members = outer.getmembers()[:5]
        print(f"Outer archive contains {len(outer.getmembers())} files")
        print("First 5 members:")
        for m in members:
            print(f"  - {m.name} ({m.size:,} bytes)")
        
        # Extract first inner archive to check
        for member in outer.getmembers():
            if member.name.endswith('.tar.gz'):
                print(f"\nChecking inner archive: {member.name}")
                
                # Extract to memory and check
                inner_file = outer.extractfile(member)
                if inner_file:
                    with tarfile.open(fileobj=inner_file, mode='r:gz') as inner:
                        inner_members = inner.getmembers()[:10]
                        print(f"Inner archive contains {len(inner.getmembers())} files")
                        print("First 10 files:")
                        
                        xml_count = 0
                        csv_count = 0
                        other_count = 0
                        
                        for im in inner.getmembers():
                            if im.name.endswith('.xml'):
                                xml_count += 1
                            elif im.name.endswith('.csv'):
                                csv_count += 1
                            else:
                                other_count += 1
                        
                        print(f"\nFile types in inner archive:")
                        print(f"  XML files: {xml_count}")
                        print(f"  CSV files: {csv_count}")
                        print(f"  Other files: {other_count}")
                        
                        # Show sample filenames
                        print("\nSample files:")
                        for im in inner_members:
                            print(f"    - {im.name} ({im.size:,} bytes)")
                        
                        break
                    
if __name__ == "__main__":
    check_ted_archive()
