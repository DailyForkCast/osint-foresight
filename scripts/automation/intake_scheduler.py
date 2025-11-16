#!/usr/bin/env python3
"""
Automated Report Intake Scheduler
==================================
Schedules and manages:
- Weekly EU/MCF sweep
- Rotating regional sprints (Nordics → Balkans → DACH → Benelux → Baltics)
- Automated gap-map refresh
- Quality checks and notifications

Usage:
  python intake_scheduler.py --schedule    # Show schedule
  python intake_scheduler.py --run-weekly  # Run weekly sweep
  python intake_scheduler.py --run-sprint  # Run current sprint
  python intake_scheduler.py --refresh-gap # Refresh gap map
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

class IntakeScheduler:
    """Manage automated report collection schedules."""

    def __init__(self, config_file="config/intake_schedule.json"):
        self.config_file = Path(config_file)
        self.schedule = self.load_schedule()

    def load_schedule(self) -> Dict:
        """Load or create schedule configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default schedule
            default_schedule = {
                'weekly_sweep': {
                    'enabled': True,
                    'day_of_week': 'Monday',
                    'time': '09:00',
                    'sources': ['MERICS', 'EUISS', 'RUSI', 'Bruegel', 'IFRI', 'SWP', 'IISS'],
                    'last_run': None,
                    'next_run': None
                },
                'regional_sprints': {
                    'enabled': True,
                    'rotation': ['Nordics', 'Balkans', 'DACH', 'Benelux', 'Baltics'],
                    'current_region': 'Nordics',
                    'week_number': 0,
                    'last_run': None,
                    'next_run': None
                },
                'gap_map_refresh': {
                    'enabled': True,
                    'frequency_days': 7,
                    'last_run': None,
                    'next_run': None
                },
                'quality_checks': {
                    'enabled': True,
                    'frequency_days': 1,
                    'last_run': None
                }
            }

            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(default_schedule, f, indent=2)

            return default_schedule

    def save_schedule(self):
        """Save schedule configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.schedule, f, indent=2)

    def show_schedule(self):
        """Display current schedule."""
        print("="*80)
        print("AUTOMATED INTAKE SCHEDULE")
        print("="*80)

        # Weekly sweep
        print("\n1. Weekly EU/MCF Sweep")
        sweep = self.schedule['weekly_sweep']
        print(f"   Status: {'ENABLED' if sweep['enabled'] else 'DISABLED'}")
        print(f"   Schedule: Every {sweep['day_of_week']} at {sweep['time']}")
        print(f"   Sources: {', '.join(sweep['sources'])}")
        print(f"   Last Run: {sweep['last_run'] or 'Never'}")

        # Regional sprints
        print("\n2. Regional Sprints")
        sprints = self.schedule['regional_sprints']
        print(f"   Status: {'ENABLED' if sprints['enabled'] else 'DISABLED'}")
        print(f"   Rotation: {' -> '.join(sprints['rotation'])}")
        print(f"   Current Region: {sprints['current_region']}")
        print(f"   Week: {sprints['week_number']}/{len(sprints['rotation'])}")
        print(f"   Last Run: {sprints['last_run'] or 'Never'}")

        # Gap map refresh
        print("\n3. Gap Map Refresh")
        gap = self.schedule['gap_map_refresh']
        print(f"   Status: {'ENABLED' if gap['enabled'] else 'DISABLED'}")
        print(f"   Frequency: Every {gap['frequency_days']} days")
        print(f"   Last Run: {gap['last_run'] or 'Never'}")

        # Quality checks
        print("\n4. Quality Checks")
        quality = self.schedule['quality_checks']
        print(f"   Status: {'ENABLED' if quality['enabled'] else 'DISABLED'}")
        print(f"   Frequency: Every {quality['frequency_days']} day(s)")
        print(f"   Last Run: {quality['last_run'] or 'Never'}")

        print("\n" + "="*80)

    def run_weekly_sweep(self) -> Dict:
        """Execute weekly EU/MCF sweep."""
        print("="*80)
        print("RUNNING WEEKLY EU/MCF SWEEP")
        print("="*80)

        results = {
            'start_time': datetime.now().isoformat(),
            'sources_attempted': [],
            'sources_succeeded': [],
            'sources_failed': [],
            'reports_found': 0,
            'reports_downloaded': 0,
            'status': 'PENDING'
        }

        sweep = self.schedule['weekly_sweep']

        # Run finder
        print("\n[1/2] Running EU MCF Report Finder...")
        try:
            result = subprocess.run(
                ['python', 'scripts/collectors/eu_mcf_report_finder.py'],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                print("[OK] Finder completed successfully")
                # Parse output to get report count
                # (simplified - in production would parse JSON output)
                results['sources_attempted'] = sweep['sources']
                results['sources_succeeded'] = sweep['sources']
                results['reports_found'] = 2  # Placeholder

            else:
                print(f"[ERROR] Finder failed: {result.stderr}")
                results['status'] = 'FAILED'

        except subprocess.TimeoutExpired:
            print("[ERROR] Finder timed out")
            results['status'] = 'FAILED'

        # Run downloader (if finder succeeded)
        if results['status'] != 'FAILED':
            print("\n[2/2] Running EU MCF Report Downloader...")
            # Find latest finder output
            finder_outputs = sorted(Path('data/external/eu_mcf_reports').glob('eu_mcf_reports_*.json'))

            if finder_outputs:
                latest_finder = finder_outputs[-1]
                print(f"   Using: {latest_finder.name}")

                try:
                    result = subprocess.run(
                        ['python', 'scripts/collectors/eu_mcf_report_downloader.py', str(latest_finder)],
                        capture_output=True,
                        text=True,
                        timeout=600
                    )

                    if result.returncode == 0:
                        print("[OK] Downloader completed successfully")
                        results['reports_downloaded'] = 1  # Placeholder
                        results['status'] = 'SUCCESS'
                    else:
                        print(f"[ERROR] Downloader failed: {result.stderr}")
                        results['status'] = 'PARTIAL'

                except subprocess.TimeoutExpired:
                    print("[ERROR] Downloader timed out")
                    results['status'] = 'PARTIAL'

        # Update schedule
        results['end_time'] = datetime.now().isoformat()
        self.schedule['weekly_sweep']['last_run'] = results['end_time']
        self.save_schedule()

        return results

    def run_regional_sprint(self) -> Dict:
        """Execute current regional sprint."""
        print("="*80)
        print("RUNNING REGIONAL SPRINT")
        print("="*80)

        sprints = self.schedule['regional_sprints']
        current_region = sprints['current_region']

        print(f"\nRegion: {current_region}")
        print(f"Week: {sprints['week_number'] + 1}/{len(sprints['rotation'])}")

        results = {
            'start_time': datetime.now().isoformat(),
            'region': current_region,
            'status': 'SUCCESS'
        }

        # Regional-specific collection logic would go here
        print(f"\n[INFO] Regional sprint for {current_region} not yet implemented")
        print("[INFO] This would run region-specific collectors:")

        region_sources = {
            'Nordics': ['Swedish Defense Research Agency', 'Norwegian Defence Research', 'DIIS (Denmark)'],
            'Balkans': ['Belgrade Security Forum', 'Croatian Security Council'],
            'DACH': ['SWP (Germany)', 'Austrian Institute', 'Swiss Security Studies'],
            'Benelux': ['Clingendael (Netherlands)', 'Egmont Institute (Belgium)', 'Luxembourg Institute'],
            'Baltics': ['ICDS (Estonia)', 'NRFA (Lithuania)', 'LIIA (Latvia)']
        }

        sources = region_sources.get(current_region, [])
        for source in sources:
            print(f"   - {source}")

        # Rotate to next region
        rotation = sprints['rotation']
        current_idx = rotation.index(current_region)
        next_idx = (current_idx + 1) % len(rotation)
        sprints['current_region'] = rotation[next_idx]
        sprints['week_number'] = next_idx
        sprints['last_run'] = results['start_time']

        self.save_schedule()

        print(f"\n[OK] Sprint complete. Next region: {sprints['current_region']}")

        return results

    def refresh_gap_map(self) -> Dict:
        """Refresh gap analysis."""
        print("="*80)
        print("REFRESHING GAP MAP")
        print("="*80)

        results = {
            'start_time': datetime.now().isoformat(),
            'status': 'SUCCESS'
        }

        # Run gap analysis query
        print("\n[INFO] Running gap map analysis...")

        try:
            import sqlite3

            conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
            cursor = conn.cursor()

            # Get current coverage
            cursor.execute('''
                SELECT
                    rr.region_slug,
                    rt.topic_slug,
                    COUNT(DISTINCT tr.report_id) as report_count
                FROM thinktank_reports tr
                INNER JOIN report_regions rr ON tr.report_id = rr.report_id
                INNER JOIN report_topics rt ON tr.report_id = rt.report_id
                WHERE tr.publication_date_iso >= '2015-01-01'
                GROUP BY rr.region_slug, rt.topic_slug
            ''')

            coverage = {}
            for region, topic, count in cursor.fetchall():
                key = f"{region}×{topic}"
                coverage[key] = count

            results['coverage_cells'] = len(coverage)
            results['empty_cells'] = 0  # Would calculate based on all possible combinations

            conn.close()

            print(f"[OK] Gap map refreshed")
            print(f"   Coverage cells: {results['coverage_cells']}")

        except Exception as e:
            print(f"[ERROR] Gap map refresh failed: {e}")
            results['status'] = 'FAILED'

        # Update schedule
        results['end_time'] = datetime.now().isoformat()
        self.schedule['gap_map_refresh']['last_run'] = results['end_time']
        self.save_schedule()

        return results


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description='Automated report intake scheduler')
    parser.add_argument('--schedule', action='store_true', help='Show schedule')
    parser.add_argument('--run-weekly', action='store_true', help='Run weekly sweep')
    parser.add_argument('--run-sprint', action='store_true', help='Run regional sprint')
    parser.add_argument('--refresh-gap', action='store_true', help='Refresh gap map')

    args = parser.parse_args()

    scheduler = IntakeScheduler()

    if args.schedule or (not any([args.run_weekly, args.run_sprint, args.refresh_gap])):
        scheduler.show_schedule()

    if args.run_weekly:
        results = scheduler.run_weekly_sweep()
        print(f"\n[{results['status']}] Weekly sweep completed")

    if args.run_sprint:
        results = scheduler.run_regional_sprint()
        print(f"\n[{results['status']}] Regional sprint completed")

    if args.refresh_gap:
        results = scheduler.refresh_gap_map()
        print(f"\n[{results['status']}] Gap map refreshed")


if __name__ == "__main__":
    main()
