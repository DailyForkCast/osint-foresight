#!/usr/bin/env python3
"""
TED Format Transition Date Finder
Checks June-July 2024 daily to identify exact date when format changed from Era 2 to Era 3
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import tarfile
from datetime import datetime, timedelta
import json

class TransitionDateFinder:
    """Find exact date when TED switched from R2.0.9 to UBL eForms"""

    def __init__(self):
        self.source_dir = Path("F:/TED_Data/monthly")
        self.results = []

    def get_june_july_2024_dates(self):
        """Generate all dates in June and July 2024"""
        dates = []
        # June 2024
        start = datetime(2024, 6, 1)
        end = datetime(2024, 7, 31)
        current = start
        while current <= end:
            dates.append(current.strftime("%Y_%m"))
            current = datetime(current.year, current.month % 12 + 1, 1)
        return ['2024_06', '2024_07']

    def find_monthly_archive(self, period: str):
        """Find monthly archive for period"""
        pattern = f"TED_monthly_{period}.tar.gz"
        archives = list(self.source_dir.rglob(pattern))
        return archives[0] if archives else None

    def check_format_in_archive(self, archive_path: Path, max_samples=20):
        """Check formats of multiple files in archive to detect transition"""
        temp_dir = Path("C:/Projects/OSINT - Foresight/data/temp/transition_check")
        temp_dir.mkdir(parents=True, exist_ok=True)

        formats_found = []

        try:
            with tarfile.open(archive_path, 'r:gz', errorlevel=0) as outer_tar:
                # Get all inner archives
                inner_archives = [m for m in outer_tar.getmembers() if m.name.endswith('.tar.gz')][:max_samples]

                for inner_member in inner_archives:
                    try:
                        # Extract inner archive
                        outer_tar.extract(inner_member, temp_dir)
                        inner_path = temp_dir / inner_member.name

                        # Extract date from inner archive name (format: YYYYMMDD_NNN_yyyymm.tar.gz)
                        date_part = inner_member.name.split('_')[0]
                        if len(date_part) == 8:
                            day_date = f"{date_part[0:4]}-{date_part[4:6]}-{date_part[6:8]}"
                        else:
                            day_date = "unknown"

                        # Open inner archive
                        with tarfile.open(inner_path, 'r:gz', errorlevel=0) as inner_tar:
                            # Get first XML
                            xml_members = [m for m in inner_tar.getmembers() if m.name.endswith('.xml')][:1]

                            if xml_members:
                                inner_tar.extract(xml_members[0], temp_dir)
                                xml_path = temp_dir / xml_members[0].name

                                # Parse XML to check format
                                tree = ET.parse(xml_path)
                                root = tree.getroot()

                                namespace = root.tag.split('}')[0][1:] if '}' in root.tag else None

                                # Determine format
                                if namespace and 'ubl:schema:xsd' in namespace:
                                    format_type = 'ERA_3_UBL_EFORMS'
                                elif namespace and 'resource/schema/ted' in namespace:
                                    format_type = 'ERA_2_RESOURCE_SCHEMA'
                                elif namespace and 'TED_schema/Export' in namespace:
                                    format_type = 'ERA_1_TED_SCHEMA'
                                else:
                                    format_type = 'UNKNOWN'

                                formats_found.append({
                                    'date': day_date,
                                    'inner_archive': inner_member.name,
                                    'xml_file': xml_members[0].name,
                                    'format': format_type,
                                    'namespace': namespace
                                })

                                print(f"  {day_date}: {format_type}")

                                # Cleanup XML
                                xml_path.unlink()

                        # Cleanup inner archive
                        inner_path.unlink()

                    except Exception as e:
                        print(f"  Error checking {inner_member.name}: {e}")
                        continue

        except Exception as e:
            print(f"Error opening archive: {e}")

        finally:
            # Cleanup
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

        return formats_found

    def run_analysis(self):
        """Run transition date analysis"""
        print("="*80)
        print("TED FORMAT TRANSITION DATE FINDER")
        print("Checking June-July 2024 to find exact format change date")
        print("="*80)

        periods = self.get_june_july_2024_dates()

        for period in periods:
            print(f"\n[{period}]")

            archive = self.find_monthly_archive(period)
            if not archive:
                print(f"  No archive found")
                continue

            print(f"  Archive: {archive.name}")
            print(f"  Checking formats inside (sampling up to 20 daily archives)...")

            formats = self.check_format_in_archive(archive, max_samples=20)

            # Analyze results
            era2_count = sum(1 for f in formats if f['format'] == 'ERA_2_RESOURCE_SCHEMA')
            era3_count = sum(1 for f in formats if f['format'] == 'ERA_3_UBL_EFORMS')

            print(f"\n  Summary:")
            print(f"    Era 2 (Resource Schema): {era2_count} files")
            print(f"    Era 3 (UBL eForms): {era3_count} files")

            if era2_count > 0 and era3_count > 0:
                print(f"    [TRANSITION DETECTED] Both formats present in {period}")
                # Find first Era 3 occurrence
                first_era3 = next((f for f in formats if f['format'] == 'ERA_3_UBL_EFORMS'), None)
                if first_era3:
                    print(f"    First Era 3 file: {first_era3['date']}")
            elif era3_count > 0:
                print(f"    [ERA 3 ONLY] All sampled files are UBL eForms")
            elif era2_count > 0:
                print(f"    [ERA 2 ONLY] All sampled files are Resource Schema")

            self.results.append({
                'period': period,
                'archive': archive.name,
                'formats': formats,
                'era2_count': era2_count,
                'era3_count': era3_count
            })

        # Save results
        output_file = Path("C:/Projects/OSINT - Foresight/analysis/TED_TRANSITION_DATE_ANALYSIS.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*80}")
        print(f"[SUCCESS] Analysis complete: {output_file}")


if __name__ == '__main__':
    finder = TransitionDateFinder()
    finder.run_analysis()
