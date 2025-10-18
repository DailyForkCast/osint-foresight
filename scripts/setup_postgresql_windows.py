#!/usr/bin/env python3
"""
PostgreSQL Setup Helper for Windows
Downloads, configures, and initializes PostgreSQL for USASpending data import
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path
import json
from datetime import datetime

class PostgreSQLSetup:
    def __init__(self):
        self.pg_version = "15.4"
        self.pg_port = 5432
        self.pg_data_dir = Path("C:/PostgreSQL/data")
        self.pg_bin_dir = Path("C:/PostgreSQL/bin")
        self.download_url = "https://get.enterprisedb.com/postgresql/postgresql-15.4-1-windows-x64-binaries.zip"
        self.usaspending_dir = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906")

        self.setup_log = {
            'started': datetime.now().isoformat(),
            'steps_completed': [],
            'errors': [],
            'status': 'in_progress'
        }

    def check_prerequisites(self):
        """Check if PostgreSQL is already installed"""
        print("\n[CHECKING PREREQUISITES]")
        print("-" * 40)

        # Check if PostgreSQL is in PATH
        try:
            result = subprocess.run(['psql', '--version'],
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print(f"PostgreSQL found: {result.stdout.strip()}")
                self.setup_log['steps_completed'].append('postgresql_found')
                return True
        except:
            pass

        # Check common installation paths
        common_paths = [
            "C:\\Program Files\\PostgreSQL",
            "C:\\PostgreSQL",
            "C:\\pgsql"
        ]

        for path in common_paths:
            if Path(path).exists():
                print(f"PostgreSQL directory found at: {path}")
                self.pg_bin_dir = Path(path) / "bin"
                if (self.pg_bin_dir / "psql.exe").exists():
                    print("PostgreSQL binaries confirmed")
                    self.setup_log['steps_completed'].append('postgresql_found')
                    return True

        print("PostgreSQL not found - installation needed")
        return False

    def create_installation_script(self):
        """Create batch script for manual PostgreSQL installation"""
        print("\n[CREATING INSTALLATION SCRIPT]")
        print("-" * 40)

        install_script = """@echo off
echo ============================================
echo PostgreSQL Installation Helper for Windows
echo ============================================
echo.

echo This script will help you install PostgreSQL for USASpending data analysis.
echo.

echo OPTION 1: Download PostgreSQL Installer
echo ----------------------------------------
echo 1. Visit: https://www.postgresql.org/download/windows/
echo 2. Download PostgreSQL 15 installer
echo 3. Run installer with these settings:
echo    - Port: 5432
echo    - Password: postgres (or your choice)
echo    - Data directory: C:\\PostgreSQL\\data
echo.

echo OPTION 2: Use Command Line (if you have chocolatey)
echo -----------------------------------------------------
echo Run: choco install postgresql15
echo.

echo OPTION 3: Use Command Line (if you have winget)
echo ------------------------------------------------
echo Run: winget install PostgreSQL.PostgreSQL
echo.

echo After installation, run: setup_postgresql_windows.py again
echo.
pause
"""

        script_path = Path("C:/Projects/OSINT - Foresight/install_postgresql.bat")
        with open(script_path, 'w') as f:
            f.write(install_script)

        print(f"Installation helper created: {script_path}")
        print("Run this script to see installation options")

        self.setup_log['steps_completed'].append('install_script_created')
        return script_path

    def create_database_scripts(self):
        """Create SQL scripts for USASpending database setup"""
        print("\n[CREATING DATABASE SCRIPTS]")
        print("-" * 40)

        scripts_dir = Path("C:/Projects/OSINT - Foresight/postgres_scripts")
        scripts_dir.mkdir(exist_ok=True)

        # Create database initialization script
        init_sql = """-- USASpending Database Initialization
-- Run this after PostgreSQL is installed

-- Create database
CREATE DATABASE usaspending
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;

-- Connect to database
\\c usaspending;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS rpt;
CREATE SCHEMA IF NOT EXISTS int;

-- Grant permissions
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA raw TO postgres;
GRANT ALL ON SCHEMA rpt TO postgres;
GRANT ALL ON SCHEMA int TO postgres;

-- Set search path
SET search_path TO public, raw, rpt, int;

-- Create status table
CREATE TABLE IF NOT EXISTS import_status (
    table_name VARCHAR(255) PRIMARY KEY,
    rows_imported BIGINT,
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50)
);

COMMENT ON TABLE import_status IS 'Tracks USASpending data import progress';
"""

        with open(scripts_dir / "01_init_database.sql", 'w') as f:
            f.write(init_sql)

        # Create China analysis views
        china_views = """-- China Analysis Views for USASpending Data

-- View 1: China-related vendors
CREATE OR REPLACE VIEW china_vendors AS
SELECT DISTINCT
    recipient_name as vendor_name,
    recipient_country_code as country,
    recipient_state_code as state,
    COUNT(*) as contract_count,
    SUM(total_obligation_amount) as total_amount,
    MIN(action_date) as first_contract,
    MAX(action_date) as last_contract
FROM public.contracts
WHERE LOWER(recipient_country_code) IN ('cn', 'china', 'prc')
   OR LOWER(recipient_name) LIKE '%china%'
   OR LOWER(recipient_name) LIKE '%chinese%'
   OR LOWER(recipient_name) LIKE '%huawei%'
   OR LOWER(recipient_name) LIKE '%zte%'
   OR LOWER(recipient_name) LIKE '%lenovo%'
   OR LOWER(recipient_name) LIKE '%dji%'
GROUP BY recipient_name, recipient_country_code, recipient_state_code;

-- View 2: Agencies with China exposure
CREATE OR REPLACE VIEW agency_china_exposure AS
SELECT
    awarding_agency_name as agency,
    COUNT(DISTINCT contract_award_unique_key) as china_contracts,
    SUM(total_obligation_amount) as total_china_spending,
    COUNT(DISTINCT recipient_name) as unique_china_vendors,
    MAX(action_date) as latest_china_contract
FROM public.contracts
WHERE LOWER(recipient_country_code) IN ('cn', 'china', 'prc')
   OR LOWER(recipient_name) LIKE '%china%'
   OR LOWER(product_or_service_description) LIKE '%made in china%'
GROUP BY awarding_agency_name
ORDER BY total_china_spending DESC;

-- View 3: Critical products from China
CREATE OR REPLACE VIEW critical_china_products AS
SELECT
    product_or_service_code as psc_code,
    naics_code,
    product_or_service_description as description,
    COUNT(*) as contract_count,
    SUM(total_obligation_amount) as total_value,
    STRING_AGG(DISTINCT recipient_name, '; ') as vendors
FROM public.contracts
WHERE (LOWER(product_or_service_description) LIKE '%made in china%'
   OR LOWER(recipient_country_code) IN ('cn', 'china', 'prc'))
   AND (
       product_or_service_code LIKE '58%' -- Communication equipment
       OR product_or_service_code LIKE '59%' -- Electrical equipment
       OR product_or_service_code LIKE '70%' -- IT equipment
       OR naics_code LIKE '334%' -- Computer/Electronic manufacturing
   )
GROUP BY product_or_service_code, naics_code, product_or_service_description
ORDER BY total_value DESC;

-- View 4: China spending timeline
CREATE OR REPLACE VIEW china_spending_timeline AS
SELECT
    DATE_TRUNC('month', action_date) as month,
    COUNT(*) as contracts,
    SUM(total_obligation_amount) as amount,
    COUNT(DISTINCT recipient_name) as unique_vendors,
    COUNT(DISTINCT awarding_agency_name) as unique_agencies
FROM public.contracts
WHERE LOWER(recipient_country_code) IN ('cn', 'china', 'prc')
   OR LOWER(recipient_name) LIKE '%china%'
   OR LOWER(product_or_service_description) LIKE '%china%'
GROUP BY DATE_TRUNC('month', action_date)
ORDER BY month DESC;
"""

        with open(scripts_dir / "02_china_analysis_views.sql", 'w') as f:
            f.write(china_views)

        # Create import script for .dat files
        import_script = """-- Import USASpending .dat files
-- Run this after database initialization

-- Import example for a single table
-- Adjust paths as needed

\\COPY contracts FROM 'F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/contracts.dat'
WITH (FORMAT text, DELIMITER E'\\t', NULL '\\N', ESCAPE '\\', QUOTE E'\\b', ENCODING 'UTF8');

-- Track import
INSERT INTO import_status (table_name, rows_imported, status)
SELECT 'contracts', COUNT(*), 'completed'
FROM contracts;

-- Repeat for other tables as needed
"""

        with open(scripts_dir / "03_import_data.sql", 'w') as f:
            f.write(import_script)

        print(f"Created 3 SQL scripts in {scripts_dir}")
        self.setup_log['steps_completed'].append('sql_scripts_created')

        return scripts_dir

    def create_china_monitoring_script(self):
        """Create automated China pattern monitoring system"""
        print("\n[CREATING MONITORING SYSTEM]")
        print("-" * 40)

        monitor_script = '''#!/usr/bin/env python3
"""
Automated China Pattern Monitoring System
Continuously monitors new data for China-related patterns
"""

import psycopg2
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ChinaMonitor:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'usaspending',
            'user': 'postgres',
            'password': 'postgres'  # Change this
        }

        self.china_patterns = [
            "china", "chinese", "prc", "people's republic",
            "huawei", "zte", "lenovo", "dji", "hikvision",
            "alibaba", "tencent", "baidu", "bytedance",
            "made in china", "manufactured in china"
        ]

        self.alert_thresholds = {
            'high_value': 1000000,  # $1M
            'critical_agency': ['DOD', 'DOE', 'DHS', 'DOS'],
            'sensitive_products': ['5G', 'telecom', 'network', 'surveillance']
        }

        self.findings = []

    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None

    def check_new_contracts(self, since_days=1):
        """Check for new China-related contracts"""
        conn = self.connect_db()
        if not conn:
            return

        cur = conn.cursor()

        # Build pattern matching condition
        pattern_conditions = " OR ".join([
            f"LOWER(recipient_name) LIKE '%{p}%'" for p in self.china_patterns
        ] + [
            f"LOWER(product_or_service_description) LIKE '%{p}%'" for p in self.china_patterns
        ])

        query = f"""
        SELECT
            contract_award_unique_key,
            recipient_name,
            total_obligation_amount,
            awarding_agency_name,
            product_or_service_description,
            action_date
        FROM contracts
        WHERE action_date >= CURRENT_DATE - INTERVAL '{since_days} days'
          AND ({pattern_conditions})
        """

        cur.execute(query)
        results = cur.fetchall()

        for row in results:
            finding = {
                'contract_id': row[0],
                'vendor': row[1],
                'amount': float(row[2]) if row[2] else 0,
                'agency': row[3],
                'description': row[4],
                'date': row[5],
                'risk_level': self.assess_risk(row)
            }
            self.findings.append(finding)

        conn.close()
        return len(results)

    def assess_risk(self, contract_row):
        """Assess risk level of a contract"""
        risk_score = 0
        risk_factors = []

        # High value
        if contract_row[2] and float(contract_row[2]) > self.alert_thresholds['high_value']:
            risk_score += 3
            risk_factors.append('HIGH_VALUE')

        # Critical agency
        if contract_row[3]:
            for agency in self.alert_thresholds['critical_agency']:
                if agency in contract_row[3].upper():
                    risk_score += 2
                    risk_factors.append(f'CRITICAL_AGENCY_{agency}')

        # Sensitive products
        if contract_row[4]:
            desc_lower = contract_row[4].lower()
            for product in self.alert_thresholds['sensitive_products']:
                if product in desc_lower:
                    risk_score += 2
                    risk_factors.append(f'SENSITIVE_{product.upper()}')

        # Determine risk level
        if risk_score >= 5:
            return 'CRITICAL'
        elif risk_score >= 3:
            return 'HIGH'
        elif risk_score >= 1:
            return 'MEDIUM'
        else:
            return 'LOW'

    def generate_alert_report(self):
        """Generate alert report for high-risk findings"""
        if not self.findings:
            return None

        critical = [f for f in self.findings if f['risk_level'] == 'CRITICAL']
        high = [f for f in self.findings if f['risk_level'] == 'HIGH']

        report = f"""
CHINA PATTERN MONITORING ALERT
Generated: {datetime.now().isoformat()}

SUMMARY
-------
Total new China-related contracts: {len(self.findings)}
Critical risk: {len(critical)}
High risk: {len(high)}

CRITICAL ALERTS
---------------
"""

        for finding in critical[:5]:  # Top 5 critical
            report += f"""
Contract: {finding['contract_id']}
Vendor: {finding['vendor']}
Amount: ${finding['amount']:,.2f}
Agency: {finding['agency']}
Description: {finding['description'][:100]}...
Risk Level: {finding['risk_level']}
---
"""

        return report

    def save_findings(self):
        """Save findings to CSV and JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save to CSV
        csv_file = Path(f"china_monitoring_{timestamp}.csv")
        with open(csv_file, 'w', newline='') as f:
            if self.findings:
                writer = csv.DictWriter(f, fieldnames=self.findings[0].keys())
                writer.writeheader()
                writer.writerows(self.findings)

        # Save to JSON
        json_file = Path(f"china_monitoring_{timestamp}.json")
        with open(json_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'findings_count': len(self.findings),
                'findings': self.findings
            }, f, indent=2, default=str)

        return csv_file, json_file

    def run_monitoring(self):
        """Run the monitoring process"""
        print("="*60)
        print("CHINA PATTERN MONITORING SYSTEM")
        print("="*60)

        print(f"\\nChecking for new contracts...")
        count = self.check_new_contracts(since_days=7)

        print(f"Found {count} new China-related contracts")

        if count > 0:
            # Generate report
            report = self.generate_alert_report()
            print(report)

            # Save findings
            csv_file, json_file = self.save_findings()
            print(f"\\nFindings saved to:")
            print(f"  - {csv_file}")
            print(f"  - {json_file}")

            # Check for critical alerts
            critical_count = len([f for f in self.findings if f['risk_level'] == 'CRITICAL'])
            if critical_count > 0:
                print(f"\\n[ALERT] {critical_count} CRITICAL risk contracts detected!")
                print("Immediate review recommended")

        print("\\nMonitoring complete")


if __name__ == "__main__":
    monitor = ChinaMonitor()
    monitor.run_monitoring()
'''

        monitor_path = Path("C:/Projects/OSINT - Foresight/scripts/china_monitor.py")
        with open(monitor_path, 'w') as f:
            f.write(monitor_script)

        # Create scheduled task batch file
        schedule_batch = """@echo off
echo Setting up daily China pattern monitoring...
echo.

REM Create scheduled task to run daily at 7 AM
schtasks /create /tn "ChinaPatternMonitor" /tr "python C:\\Projects\\OSINT - Foresight\\scripts\\china_monitor.py" /sc daily /st 07:00 /f

echo.
echo Scheduled task created successfully!
echo The monitoring script will run daily at 7:00 AM
echo.
echo You can also run it manually anytime with:
echo python "C:\\Projects\\OSINT - Foresight\\scripts\\china_monitor.py"
echo.
pause
"""

        schedule_path = Path("C:/Projects/OSINT - Foresight/schedule_china_monitoring.bat")
        with open(schedule_path, 'w') as f:
            f.write(schedule_batch)

        print(f"Monitoring script created: {monitor_path}")
        print(f"Scheduler created: {schedule_path}")

        self.setup_log['steps_completed'].append('monitoring_system_created')
        return monitor_path

    def save_setup_report(self):
        """Save setup report"""
        self.setup_log['completed'] = datetime.now().isoformat()
        self.setup_log['status'] = 'completed'

        report = f"""# PostgreSQL Setup Report

Generated: {datetime.now().isoformat()}

## Setup Status: {self.setup_log['status']}

## Steps Completed:
{chr(10).join('- ' + step for step in self.setup_log['steps_completed'])}

## Next Steps:

1. **Install PostgreSQL**:
   - Run: install_postgresql.bat
   - Follow the installation instructions

2. **After Installation**:
   - Run this script again to verify installation
   - Execute SQL scripts in postgres_scripts/ folder:
     * 01_init_database.sql
     * 02_china_analysis_views.sql
     * 03_import_data.sql

3. **Set Up Monitoring**:
   - Run: schedule_china_monitoring.bat
   - This will create a daily monitoring task

## Files Created:

- install_postgresql.bat - Installation helper
- postgres_scripts/01_init_database.sql - Database setup
- postgres_scripts/02_china_analysis_views.sql - Analysis views
- postgres_scripts/03_import_data.sql - Data import
- scripts/china_monitor.py - Monitoring system
- schedule_china_monitoring.bat - Task scheduler

## Data Locations:

- USASpending data: {self.usaspending_dir}
- PostgreSQL scripts: C:/Projects/OSINT - Foresight/postgres_scripts/
- Monitoring scripts: C:/Projects/OSINT - Foresight/scripts/
"""

        report_path = Path("C:/Projects/OSINT - Foresight/POSTGRESQL_SETUP_REPORT.md")
        with open(report_path, 'w') as f:
            f.write(report)

        # Save log
        log_path = Path("C:/Projects/OSINT - Foresight/postgresql_setup_log.json")
        with open(log_path, 'w') as f:
            json.dump(self.setup_log, f, indent=2)

        print(f"\nSetup report saved: {report_path}")
        return report_path

    def run(self):
        """Execute the setup process"""
        print("\n" + "="*60)
        print("POSTGRESQL SETUP HELPER")
        print("="*60)

        # Check if already installed
        if not self.check_prerequisites():
            # Create installation helper
            self.create_installation_script()
            print("\n[ACTION REQUIRED]")
            print("PostgreSQL is not installed.")
            print("Please run: install_postgresql.bat")
            print("Then run this script again.")

        # Create database scripts
        self.create_database_scripts()

        # Create monitoring system
        self.create_china_monitoring_script()

        # Save report
        self.save_setup_report()

        print("\n" + "="*60)
        print("SETUP COMPLETE")
        print("="*60)
        print("\nAll scripts and helpers have been created.")
        print("Follow the steps in POSTGRESQL_SETUP_REPORT.md")


if __name__ == "__main__":
    setup = PostgreSQLSetup()
    setup.run()
