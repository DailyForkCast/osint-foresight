#!/usr/bin/env python3
"""
Extract deeply nested TED files (tar -> subdirs -> tar.gz -> xml)
"""

import tarfile
import gzip
import shutil
from pathlib import Path
import os

class TEDExtractor:
    def __init__(self):
        self.ted_path = Path("F:/DECOMPRESSED_DATA/ted_extracted")
        self.output_path = Path("F:/DECOMPRESSED_DATA/ted_xml")
        self.output_path.mkdir(exist_ok=True)

        self.stats = {
            'tar_files': 0,
            'gz_files': 0,
            'xml_extracted': 0,
            'errors': 0
        }

    def extract_all(self):
        """Extract all nested TED files"""
        print("\n" + "="*70)
        print("DEEP TED EXTRACTION - Getting to the XML files")
        print("="*70)

        # Find all .tar directories
        for tar_dir in self.ted_path.glob("*.tar"):
            if tar_dir.is_dir():
                print(f"\n[Processing {tar_dir.name}]")
                self.stats['tar_files'] += 1

                # Look for subdirectories (like 08, 12, etc.)
                for month_dir in tar_dir.iterdir():
                    if month_dir.is_dir():
                        print(f"  Found month directory: {month_dir.name}")

                        # Find .tar.gz files in the month directory
                        gz_files = list(month_dir.glob("*.tar.gz"))
                        print(f"    Found {len(gz_files)} tar.gz files")

                        # Extract first 3 tar.gz files from each month for demo
                        for gz_file in gz_files[:3]:
                            self.extract_tar_gz(gz_file)

    def extract_tar_gz(self, gz_path):
        """Extract a tar.gz file to get XML"""
        try:
            self.stats['gz_files'] += 1

            # Create output directory for this archive
            output_dir = self.output_path / gz_path.stem
            output_dir.mkdir(exist_ok=True)

            print(f"      Extracting {gz_path.name}...")

            # Extract tar.gz
            with tarfile.open(gz_path, 'r:gz') as tar:
                # Extract only XML files
                xml_members = [m for m in tar.getmembers() if m.name.endswith('.xml')]

                if xml_members:
                    print(f"        Found {len(xml_members)} XML files")

                    # Extract up to 10 XML files from each archive
                    for member in xml_members[:10]:
                        tar.extract(member, path=output_dir)
                        self.stats['xml_extracted'] += 1

                        # Flatten the structure - move XML to main output dir
                        extracted_path = output_dir / member.name
                        if extracted_path.exists():
                            final_path = self.output_path / extracted_path.name
                            shutil.move(str(extracted_path), str(final_path))

                    # Clean up empty subdirectories
                    for subdir in output_dir.iterdir():
                        if subdir.is_dir() and not list(subdir.iterdir()):
                            subdir.rmdir()

                    if not list(output_dir.iterdir()):
                        output_dir.rmdir()
                else:
                    print(f"        No XML files found in {gz_path.name}")

        except Exception as e:
            self.stats['errors'] += 1
            print(f"        ERROR: {str(e)[:50]}")

    def print_summary(self):
        """Print extraction summary"""
        print("\n" + "="*70)
        print("EXTRACTION COMPLETE")
        print("="*70)

        print(f"\nStatistics:")
        print(f"  TAR directories processed: {self.stats['tar_files']}")
        print(f"  TAR.GZ files processed: {self.stats['gz_files']}")
        print(f"  XML files extracted: {self.stats['xml_extracted']}")
        print(f"  Errors encountered: {self.stats['errors']}")

        # Count final XML files
        final_xml = list(self.output_path.glob("*.xml"))
        print(f"\nFinal XML files ready for analysis: {len(final_xml)}")

        if final_xml:
            print("\nSample files extracted:")
            for xml_file in final_xml[:5]:
                size_kb = xml_file.stat().st_size / 1024
                print(f"  - {xml_file.name} ({size_kb:.1f} KB)")

        print(f"\nXML files location: {self.output_path}")

    def run(self):
        """Execute the extraction"""
        self.extract_all()
        self.print_summary()


if __name__ == "__main__":
    extractor = TEDExtractor()
    extractor.run()
