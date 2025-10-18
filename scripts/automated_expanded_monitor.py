#!/usr/bin/env python3
"""
Automated Monitoring System for Expanded Geographic Scope
Continuous monitoring of China activities across all European countries
Includes UK, Norway, Switzerland, Balkans, Turkey, Armenia, Azerbaijan, Georgia, Iceland
"""

import json
import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import hashlib
import sys
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from core.enhanced_validation_v2 import ExpandedGeographicValidator
except ImportError:
    logging.warning("Could not import enhanced validation - using basic validation")
    ExpandedGeographicValidator = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automated_monitoring.log'),
        logging.StreamHandler()
    ]
)

class ExpandedMonitoringSystem:
    """
    Automated monitoring system for expanded geographic scope
    Tracks China activities across all European countries
    """

    def __init__(self):
        self.base_path = Path("C:/Projects/OSINT - Foresight")
        self.config_file = self.base_path / "config/expanded_countries.json"
        self.db_path = self.base_path / "database/expanded_monitoring.db"

        # Load configuration
        self.load_config()

        # Initialize database
        self.init_database()

        # Initialize validator
        if ExpandedGeographicValidator:
            self.validator = ExpandedGeographicValidator()
        else:
            self.validator = None

        # Monitoring state
        self.monitoring_active = False
        self.last_scan_time = {}

    def load_config(self):
        """Load expanded countries configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logging.info(f"Loaded config: {self.config['total_countries']} countries")
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            sys.exit(1)

    def init_database(self):
        """Initialize monitoring database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                country_code TEXT NOT NULL,
                event_type TEXT NOT NULL,
                source TEXT NOT NULL,
                entity_name TEXT,
                description TEXT,
                confidence REAL,
                severity TEXT,
                data_hash TEXT UNIQUE,
                metadata TEXT
            )
        ''')

        # Countries status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS countries_status (
                country_code TEXT PRIMARY KEY,
                country_name TEXT,
                last_scan TEXT,
                total_events INTEGER DEFAULT 0,
                high_severity_events INTEGER DEFAULT 0,
                monitoring_enabled INTEGER DEFAULT 1,
                special_status TEXT
            )
        ''')

        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                country_code TEXT,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                acknowledged INTEGER DEFAULT 0,
                metadata TEXT
            )
        ''')

        # Data sources status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sources_status (
                source_name TEXT PRIMARY KEY,
                last_check TEXT,
                status TEXT,
                total_records INTEGER,
                new_records_24h INTEGER,
                error_count INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

        logging.info(f"Database initialized: {self.db_path}")

    def get_priority_countries(self) -> List[str]:
        """Get priority countries for monitoring"""
        # Tier 1 + Tier 2 (new countries)
        tier1 = self.config['priority_tiers']['tier_1_high_priority']['countries']
        tier2 = self.config['priority_tiers']['tier_2_expanded_coverage']['countries']

        return tier1 + tier2

    def monitor_data_source(self, source_name: str, source_path: Path) -> Dict:
        """Monitor a specific data source for new records"""

        result = {
            'source': source_name,
            'checked': datetime.now().isoformat(),
            'status': 'unknown',
            'new_records': 0,
            'errors': []
        }

        try:
            if not source_path.exists():
                result['status'] = 'unavailable'
                result['errors'].append(f"Path not found: {source_path}")
                return result

            result['status'] = 'available'

            # Check for new files based on modification time
            cutoff_time = datetime.now() - timedelta(hours=24)
            new_files = []

            if source_path.is_dir():
                for file in source_path.rglob('*'):
                    if file.is_file():
                        mtime = datetime.fromtimestamp(file.stat().st_mtime)
                        if mtime > cutoff_time:
                            new_files.append(str(file))

            result['new_records'] = len(new_files)
            result['status'] = 'active' if new_files else 'idle'

            # Update database
            self._update_source_status(source_name, result)

        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(str(e))
            logging.error(f"Error monitoring {source_name}: {e}")

        return result

    def scan_country(self, country_code: str) -> Dict:
        """Scan a specific country for China activities"""

        result = {
            'country_code': country_code,
            'scan_time': datetime.now().isoformat(),
            'events_found': 0,
            'new_alerts': 0,
            'sources_checked': []
        }

        logging.info(f"Scanning {country_code}...")

        # Check each data source
        data_sources = {
            'openalex': Path("F:/OSINT_Backups/openalex/data/"),
            'ted': Path("F:/TED_Data/monthly/"),
            'usaspending': Path("F:/OSINT_DATA/USAspending/"),
            'cordis': self.base_path / "countries/_global/data/cordis_raw/"
        }

        for source_name, source_path in data_sources.items():
            source_result = self.monitor_data_source(source_name, source_path)
            result['sources_checked'].append(source_result)

            if source_result['new_records'] > 0:
                # Create alert for new data
                self._create_alert(
                    alert_type='new_data',
                    country_code=country_code,
                    severity='info',
                    message=f"New data in {source_name}: {source_result['new_records']} records"
                )
                result['new_alerts'] += 1

        # Update country status
        self._update_country_status(country_code, result)

        return result

    def scan_all_priority_countries(self) -> Dict:
        """Scan all priority countries"""

        priority_countries = self.get_priority_countries()

        summary = {
            'scan_start': datetime.now().isoformat(),
            'countries_scanned': 0,
            'total_events': 0,
            'total_alerts': 0,
            'countries': []
        }

        for country_code in priority_countries:
            try:
                result = self.scan_country(country_code)
                summary['countries_scanned'] += 1
                summary['total_events'] += result['events_found']
                summary['total_alerts'] += result['new_alerts']
                summary['countries'].append(result)

                # Brief pause to avoid overwhelming system
                time.sleep(0.5)

            except Exception as e:
                logging.error(f"Error scanning {country_code}: {e}")

        summary['scan_end'] = datetime.now().isoformat()

        # Save scan summary
        self._save_scan_summary(summary)

        return summary

    def generate_daily_report(self) -> Dict:
        """Generate daily monitoring report"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Events in last 24 hours
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()

        cursor.execute('''
            SELECT country_code, COUNT(*) as event_count,
                   AVG(confidence) as avg_confidence
            FROM monitoring_events
            WHERE timestamp > ?
            GROUP BY country_code
            ORDER BY event_count DESC
        ''', (cutoff,))

        recent_events = [
            {'country': row[0], 'events': row[1], 'avg_confidence': row[2]}
            for row in cursor.fetchall()
        ]

        # Unacknowledged alerts
        cursor.execute('''
            SELECT COUNT(*) FROM alerts
            WHERE acknowledged = 0
        ''')
        unack_alerts = cursor.fetchone()[0]

        # Countries status
        cursor.execute('''
            SELECT country_code, total_events, high_severity_events
            FROM countries_status
            ORDER BY high_severity_events DESC, total_events DESC
            LIMIT 10
        ''')

        top_countries = [
            {'country': row[0], 'total': row[1], 'high_severity': row[2]}
            for row in cursor.fetchall()
        ]

        conn.close()

        report = {
            'report_date': datetime.now().isoformat(),
            'period': '24_hours',
            'recent_activity': recent_events,
            'unacknowledged_alerts': unack_alerts,
            'top_countries': top_countries,
            'monitoring_status': 'active' if self.monitoring_active else 'idle'
        }

        # Save report
        report_path = self.base_path / "analysis/monitoring_reports" / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        logging.info(f"Daily report saved: {report_path}")

        return report

    def _update_source_status(self, source_name: str, status: Dict):
        """Update data source status in database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO data_sources_status
            (source_name, last_check, status, new_records_24h, error_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            source_name,
            status['checked'],
            status['status'],
            status['new_records'],
            len(status['errors'])
        ))

        conn.commit()
        conn.close()

    def _update_country_status(self, country_code: str, scan_result: Dict):
        """Update country monitoring status"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO countries_status
            (country_code, last_scan, total_events)
            VALUES (?, ?, ?)
        ''', (
            country_code,
            scan_result['scan_time'],
            scan_result['events_found']
        ))

        conn.commit()
        conn.close()

    def _create_alert(self, alert_type: str, country_code: str,
                     severity: str, message: str, metadata: Dict = None):
        """Create monitoring alert"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO alerts
            (timestamp, alert_type, country_code, severity, message, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            alert_type,
            country_code,
            severity,
            message,
            json.dumps(metadata) if metadata else None
        ))

        conn.commit()
        conn.close()

        logging.info(f"Alert created: {severity.upper()} - {message}")

    def _save_scan_summary(self, summary: Dict):
        """Save scan summary to file"""

        summary_path = self.base_path / "analysis/monitoring_scans" / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        logging.info(f"Scan summary saved: {summary_path}")

    def run_continuous_monitoring(self, interval_minutes: int = 60):
        """Run continuous monitoring loop"""

        self.monitoring_active = True
        logging.info(f"Starting continuous monitoring (interval: {interval_minutes} min)")

        try:
            while self.monitoring_active:
                logging.info("="*70)
                logging.info("Starting monitoring cycle")

                # Scan priority countries
                summary = self.scan_all_priority_countries()

                logging.info(f"Cycle complete: {summary['countries_scanned']} countries, "
                           f"{summary['total_events']} events, {summary['total_alerts']} alerts")

                # Generate daily report (once per day)
                current_hour = datetime.now().hour
                if current_hour == 6:  # 6 AM
                    self.generate_daily_report()

                # Wait for next cycle
                logging.info(f"Sleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
            self.monitoring_active = False

    def run_single_scan(self):
        """Run single monitoring scan"""

        logging.info("Running single monitoring scan")
        summary = self.scan_all_priority_countries()

        logging.info("Scan complete")
        logging.info(f"  Countries: {summary['countries_scanned']}")
        logging.info(f"  Events: {summary['total_events']}")
        logging.info(f"  Alerts: {summary['total_alerts']}")

        return summary

def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(description='Automated Expanded Monitoring System')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in minutes (default: 60)')
    parser.add_argument('--daily-report', action='store_true',
                       help='Generate daily report')

    args = parser.parse_args()

    monitor = ExpandedMonitoringSystem()

    if args.daily_report:
        report = monitor.generate_daily_report()
        print(json.dumps(report, indent=2))

    elif args.continuous:
        monitor.run_continuous_monitoring(interval_minutes=args.interval)

    else:
        # Single scan
        summary = monitor.run_single_scan()
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()