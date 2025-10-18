#!/usr/bin/env python3
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

        print(f"\nChecking for new contracts...")
        count = self.check_new_contracts(since_days=7)

        print(f"Found {count} new China-related contracts")

        if count > 0:
            # Generate report
            report = self.generate_alert_report()
            print(report)

            # Save findings
            csv_file, json_file = self.save_findings()
            print(f"\nFindings saved to:")
            print(f"  - {csv_file}")
            print(f"  - {json_file}")

            # Check for critical alerts
            critical_count = len([f for f in self.findings if f['risk_level'] == 'CRITICAL'])
            if critical_count > 0:
                print(f"\n[ALERT] {critical_count} CRITICAL risk contracts detected!")
                print("Immediate review recommended")

        print("\nMonitoring complete")


if __name__ == "__main__":
    monitor = ChinaMonitor()
    monitor.run_monitoring()
