#!/usr/bin/env python3
"""
OSINT CHINA RISK INTELLIGENCE PLATFORM - MASTER CONTROL
Central control system for all intelligence operations
"""

import subprocess
import sys
from pathlib import Path
import logging
from datetime import datetime
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MasterControl:
    """Master control for OSINT platform"""

    def __init__(self):
        self.base_path = Path("C:/Projects/OSINT - Foresight")
        self.scripts_path = self.base_path / "scripts"
        self.analysis_path = self.base_path / "analysis"

        # System components
        self.systems = {
            '1': {
                'name': 'Patent Intelligence (Google Patents)',
                'script': 'collectors/google_patents_chinese_simple.py',
                'output': 'PATENT_INTELLIGENCE_BRIEF.md'
            },
            '2': {
                'name': 'RSS Feed Intelligence',
                'script': 'rss_intelligence_simple.py',
                'output': 'RSS_INTELLIGENCE_SUMMARY.md'
            },
            '3': {
                'name': 'Network Graph Analysis',
                'script': 'networkx_entity_graph.py',
                'output': 'NETWORK_INTELLIGENCE_REPORT.md'
            },
            '4': {
                'name': 'Cross-System Entity Correlation',
                'script': 'cross_system_entity_correlator.py',
                'output': 'CROSS_SYSTEM_ENTITY_CORRELATION_INTELLIGENCE.md'
            },
            '5': {
                'name': 'Risk Escalation System',
                'script': 'automated_risk_escalation_system.py',
                'output': 'AUTOMATED_RISK_ESCALATION_DASHBOARD.md'
            },
            '6': {
                'name': 'Executive Dashboard',
                'script': 'consolidated_intelligence_dashboard.py',
                'output': 'EXECUTIVE_INTELLIGENCE_BRIEF.md'
            }
        }

    def display_menu(self):
        """Display control menu"""
        print("\n" + "="*60)
        print("OSINT CHINA RISK INTELLIGENCE PLATFORM")
        print("Master Control System")
        print("="*60)
        print("\n[SYSTEMS AVAILABLE]")

        for key, system in self.systems.items():
            print(f"  {key}. {system['name']}")

        print("\n[BATCH OPERATIONS]")
        print("  A. Run ALL Systems (Complete Intelligence Cycle)")
        print("  B. Quick Analysis (Patent + RSS + Dashboard)")
        print("  C. Entity Analysis (Correlation + Risk + Network)")

        print("\n[UTILITIES]")
        print("  R. View Recent Reports")
        print("  S. System Status Check")
        print("  T. Setup Scheduled Tasks")
        print("  Q. Quit")

        print("\n" + "="*60)

    def run_system(self, system_key):
        """Run a specific system"""
        if system_key not in self.systems:
            print(f"Invalid system: {system_key}")
            return

        system = self.systems[system_key]
        script_path = self.scripts_path / system['script']

        print(f"\n[RUNNING] {system['name']}...")
        print(f"Script: {script_path}")

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"[SUCCESS] {system['name']} completed")

                # Check for output file
                output_file = self.analysis_path / system['output']
                if output_file.exists():
                    print(f"Report saved: {output_file}")
            else:
                print(f"[ERROR] {system['name']} failed")
                if result.stderr:
                    print(f"Error: {result.stderr[:500]}")

        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {system['name']} took too long")
        except Exception as e:
            print(f"[ERROR] Failed to run {system['name']}: {e}")

    def run_all_systems(self):
        """Run all systems in sequence"""
        print("\n[BATCH] Running complete intelligence cycle...")

        for key in self.systems.keys():
            self.run_system(key)
            print("-" * 40)

        print("\n[COMPLETE] All systems executed")

    def quick_analysis(self):
        """Run quick analysis subset"""
        print("\n[QUICK] Running quick analysis...")

        for key in ['1', '2', '6']:  # Patent, RSS, Dashboard
            self.run_system(key)

        print("\n[COMPLETE] Quick analysis finished")

    def entity_analysis(self):
        """Run entity-focused analysis"""
        print("\n[ENTITY] Running entity analysis...")

        for key in ['4', '5', '3']:  # Correlation, Risk, Network
            self.run_system(key)

        print("\n[COMPLETE] Entity analysis finished")

    def view_reports(self):
        """Display recent reports"""
        print("\n[REPORTS] Recent intelligence reports:\n")

        for system in self.systems.values():
            report_path = self.analysis_path / system['output']
            if report_path.exists():
                modified = datetime.fromtimestamp(report_path.stat().st_mtime)
                size_kb = report_path.stat().st_size / 1024
                print(f"  • {system['output']}")
                print(f"    Modified: {modified.strftime('%Y-%m-%d %H:%M')}")
                print(f"    Size: {size_kb:.1f} KB")
                print()

    def system_status(self):
        """Check system status"""
        print("\n[STATUS] System Health Check\n")

        # Check databases
        databases = [
            ("Master DB", "F:/OSINT_WAREHOUSE/osint_master.db"),
            ("Patent DB", "F:/OSINT_WAREHOUSE/google_patents_china.db"),
            ("RSS DB", "F:/OSINT_WAREHOUSE/rss_intelligence.db"),
            ("Graph DB", "F:/OSINT_WAREHOUSE/entity_graph.db")
        ]

        for name, path in databases:
            db_path = Path(path)
            if db_path.exists():
                size_mb = db_path.stat().st_size / 1024 / 1024
                print(f"  ✓ {name}: {size_mb:.1f} MB")
            else:
                print(f"  ✗ {name}: Not found")

        # Check Python packages
        print("\n[PACKAGES]")
        packages = ['requests', 'beautifulsoup4', 'feedparser', 'networkx', 'matplotlib']

        for package in packages:
            try:
                __import__(package)
                print(f"  ✓ {package}: Installed")
            except ImportError:
                print(f"  ✗ {package}: Missing (run: pip install {package})")

    def setup_scheduled_tasks(self):
        """Setup Windows scheduled tasks"""
        print("\n[SCHEDULER] Setting up automated tasks...")

        setup_script = self.scripts_path / "setup_scheduled_tasks.bat"
        if setup_script.exists():
            print("Run the following command as Administrator:")
            print(f'  "{setup_script}"')
        else:
            print("Scheduler setup script not found")

    def run(self):
        """Main control loop"""
        while True:
            self.display_menu()
            choice = input("\nSelect option: ").strip().upper()

            if choice == 'Q':
                print("\nShutting down OSINT platform...")
                break
            elif choice in self.systems:
                self.run_system(choice)
            elif choice == 'A':
                self.run_all_systems()
            elif choice == 'B':
                self.quick_analysis()
            elif choice == 'C':
                self.entity_analysis()
            elif choice == 'R':
                self.view_reports()
            elif choice == 'S':
                self.system_status()
            elif choice == 'T':
                self.setup_scheduled_tasks()
            else:
                print("\nInvalid option. Please try again.")

            input("\nPress Enter to continue...")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("OSINT CHINA RISK INTELLIGENCE PLATFORM")
    print("Version: 1.0 - Zero Budget Edition")
    print("Status: OPERATIONAL")
    print("="*60)

    control = MasterControl()
    control.run()
