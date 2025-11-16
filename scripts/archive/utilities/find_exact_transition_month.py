#!/usr/bin/env python3
"""
Find exact month when TED transitioned from Era 2 to Era 3
Check Feb-June 2024 to narrow down the transition
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import tarfile
import json

class ExactTransitionFinder:
    """Find exact month of format transition"""

    def __init__(self):
        self.source_dir = Path("F:/TED_Data/monthly")

    def get_test_periods(self):
        """Months to check around transition"""
        return ['2024_02', '2024_03', '2024_04', '2024_05', '2024_06']

    def check_month_format(self, period: str):
        """Check what format(s) exist in a month"""
        pattern = f"TED_monthly_{period}.tar.gz"
        archives = list(self.source_dir.rglob(pattern))

        if not archives:
            return None

        archive = archives[0]
        temp_dir = Path("C:/Projects/OSINT - Foresight/data/temp/month_check")
        temp_dir.mkdir(parents=True, exist_ok=True)

        formats = {'era2': 0, 'era3': 0}

        try:
            with tarfile.open(archive, 'r:gz', errorlevel=0) as outer_tar:
                # Sample 10 inner archives
                inner_archives = [m for m in outer_tar.getmembers() if m.name.endswith('.tar.gz')][:10]

                for inner_member in inner_archives:
                    try:
                        outer_tar.extract(inner_member, temp_dir)
                        inner_path = temp_dir / inner_member.name

                        with tarfile.open(inner_path, 'r:gz', errorlevel=0) as inner_tar:
                            xml_members = [m for m in inner_tar.getmembers() if m.name.endswith('.xml')][:1]

                            if xml_members:
                                inner_tar.extract(xml_members[0], temp_dir)
                                xml_path = temp_dir / xml_members[0].name

                                tree = ET.parse(xml_path)
                                root = tree.getroot()
                                namespace = root.tag.split('}')[0][1:] if '}' in root.tag else None

                                if namespace and 'ubl:schema:xsd' in namespace:
                                    formats['era3'] += 1
                                elif namespace and 'resource/schema/ted' in namespace:
                                    formats['era2'] += 1

                                xml_path.unlink()

                        inner_path.unlink()

                    except Exception:
                        continue

        except Exception as e:
            print(f"Error checking {period}: {e}")
            return None

        finally:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

        return formats

    def run(self):
        """Run analysis"""
        print("="*80)
        print("FINDING EXACT TRANSITION MONTH")
        print("="*80)

        results = []

        for period in self.get_test_periods():
            print(f"\n[{period}] ", end='', flush=True)
            formats = self.check_month_format(period)

            if not formats:
                print("No archive found")
                continue

            print(f"Era2: {formats['era2']} | Era3: {formats['era3']}")

            results.append({
                'period': period,
                'era2_count': formats['era2'],
                'era3_count': formats['era3']
            })

            # If we find transition month, report it
            if formats['era2'] > 0 and formats['era3'] > 0:
                print(f"  [TRANSITION MONTH DETECTED]")
            elif formats['era3'] > 0 and formats['era2'] == 0:
                print(f"  [POST-TRANSITION - All Era 3]")
            elif formats['era2'] > 0 and formats['era3'] == 0:
                print(f"  [PRE-TRANSITION - All Era 2]")

        # Summary
        print(f"\n{'='*80}")
        print("SUMMARY:")
        for r in results:
            status = ""
            if r['era2_count'] > 0 and r['era3_count'] > 0:
                status = "[TRANSITION MONTH]"
            elif r['era3_count'] > 0:
                status = "[ERA 3]"
            elif r['era2_count'] > 0:
                status = "[ERA 2]"

            print(f"{r['period']}: Era2={r['era2_count']}, Era3={r['era3_count']} {status}")


if __name__ == '__main__':
    finder = ExactTransitionFinder()
    finder.run()
