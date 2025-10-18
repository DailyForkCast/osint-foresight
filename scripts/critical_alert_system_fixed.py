#!/usr/bin/env python3
"""
Critical Alert System - FIXED VERSION
Real-time alerting for critical OSINT discoveries
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

class CriticalAlertSystem:
    def __init__(self):
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE")
        self.alert_db = self.warehouse_path / "osint_master.db"
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis/alerts")
        self.output_path.mkdir(exist_ok=True)

        self.thresholds = {
            'leonardo_score': 85,
            'patent_surge': 50,
            'mcf_relevance': 70,
            'arctic_chinese': 60,
            'network_centrality': 0.8
        }

        self.setup_alert_database()

    def setup_alert_database(self):
        """Create alert system database"""
        conn = sqlite3.connect(self.alert_db)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                alert_type TEXT,
                severity TEXT,
                entity_name TEXT,
                description TEXT,
                value REAL,
                threshold REAL,
                source_system TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                acknowledged BOOLEAN DEFAULT FALSE
            )
        ''')

        conn.commit()
        conn.close()

    def check_all_systems(self) -> List[Dict]:
        """Check all intelligence systems for critical alerts"""
        print("Checking all systems for critical alerts...")
        alerts = []

        alerts.extend(self.check_leonardo_alerts())
        alerts.extend(self.check_patent_alerts())
        alerts.extend(self.check_mcf_alerts())
        alerts.extend(self.check_arctic_alerts())

        self.store_alerts(alerts)
        self.generate_notifications(alerts)

        return alerts

    def check_leonardo_alerts(self) -> List[Dict]:
        """Check for critical Leonardo scores"""
        alerts = []

        leonardo_db = self.warehouse_path / 'osint_master.db'
        if leonardo_db.exists():
            conn = sqlite3.connect(leonardo_db)
            cur = conn.cursor()

            cur.execute('''
                SELECT entity_name, technology_name, leonardo_composite_score
                FROM technology_assessments
                WHERE leonardo_composite_score > ?
            ''', (self.thresholds['leonardo_score'],))

            for row in cur.fetchall():
                alerts.append({
                    'id': f"leo_{row[0]}_{datetime.now().strftime('%Y%m%d%H%M')}",
                    'type': 'LEONARDO_CRITICAL',
                    'severity': 'CRITICAL',
                    'entity': row[0],
                    'description': f"Critical Leonardo score for {row[1]}",
                    'value': row[2],
                    'threshold': self.thresholds['leonardo_score'],
                    'source': 'Leonardo Scoring System'
                })

            conn.close()

        return alerts

    def check_patent_alerts(self) -> List[Dict]:
        """Check for patent filing surges - FIXED"""
        alerts = []

        patent_db = self.warehouse_path / 'osint_master.db'
        if patent_db.exists():
            conn = sqlite3.connect(patent_db)
            cur = conn.cursor()

            # Check if anomaly_tracking table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='anomaly_tracking'")
            if cur.fetchone():
                # Table exists, query it
                cur.execute('''
                    SELECT date, patent_count, assignee
                    FROM anomaly_tracking
                    WHERE anomaly_flag = 1
                      AND mundane_explanation IS NULL
                ''')

                for row in cur.fetchall():
                    alerts.append({
                        'id': f"pat_{row[2]}_{datetime.now().strftime('%H%M')}",
                        'type': 'PATENT_SURGE',
                        'severity': 'HIGH',
                        'entity': row[2] if row[2] else 'Unknown',
                        'description': f"Unusual patent filing surge: {row[1]} patents",
                        'value': row[1],
                        'threshold': 'Statistical anomaly',
                        'source': 'Patent Monitoring System'
                    })
            else:
                # Use patent_searches instead
                cur.execute('''
                    SELECT COUNT(*) as cnt, search_query
                    FROM patent_searches
                    GROUP BY search_query
                    HAVING cnt > 10
                    LIMIT 5
                ''')

                for row in cur.fetchall():
                    if row[0] > 20:  # Simple threshold
                        alerts.append({
                            'id': f"pat_{row[1][:20]}_{datetime.now().strftime('%H%M')}",
                            'type': 'PATENT_ACTIVITY',
                            'severity': 'MEDIUM',
                            'entity': row[1],
                            'description': f"High patent search activity: {row[0]} searches",
                            'value': row[0],
                            'threshold': 20,
                            'source': 'Patent Monitoring System'
                        })

            conn.close()

        return alerts

    def check_mcf_alerts(self) -> List[Dict]:
        """Check for high MCF relevance"""
        alerts = []

        mcf_db = self.warehouse_path / 'osint_master.db'
        if mcf_db.exists():
            conn = sqlite3.connect(mcf_db)
            cur = conn.cursor()

            cur.execute('''
                SELECT filename, title, mcf_relevance_score
                FROM mcf_reports
                WHERE mcf_relevance_score > ?
            ''', (self.thresholds['mcf_relevance'],))

            for row in cur.fetchall():
                alerts.append({
                    'id': f"mcf_{row[0][:20]}_{datetime.now().strftime('%Y%m%d%H%M')}",
                    'type': 'MCF_HIGH_RELEVANCE',
                    'severity': 'HIGH',
                    'entity': row[1][:50] if row[1] else 'Unknown Report',
                    'description': f"High MCF relevance in {row[0]}",
                    'value': row[2],
                    'threshold': self.thresholds['mcf_relevance'],
                    'source': 'MCF Analysis System'
                })

            conn.close()

        return alerts

    def check_arctic_alerts(self) -> List[Dict]:
        """Check for Chinese Arctic activities"""
        alerts = []

        arctic_db = self.warehouse_path / 'osint_master.db'
        if arctic_db.exists():
            conn = sqlite3.connect(arctic_db)
            cur = conn.cursor()

            cur.execute('''
                SELECT filename, title, chinese_arctic_score
                FROM arctic_reports
                WHERE chinese_arctic_score > ?
            ''', (self.thresholds['arctic_chinese'],))

            for row in cur.fetchall():
                alerts.append({
                    'id': f"arc_{row[0][:20]}_{datetime.now().strftime('%Y%m%d%H%M')}",
                    'type': 'CHINESE_ARCTIC_ACTIVITY',
                    'severity': 'HIGH',
                    'entity': 'Chinese Arctic Operations',
                    'description': f"Significant Chinese Arctic content",
                    'value': row[2],
                    'threshold': self.thresholds['arctic_chinese'],
                    'source': 'Arctic Intelligence System'
                })

            conn.close()

        return alerts

    def store_alerts(self, alerts: List[Dict]):
        """Store alerts in database"""
        conn = sqlite3.connect(self.alert_db)
        cur = conn.cursor()

        for alert in alerts:
            cur.execute('''
                INSERT OR IGNORE INTO alerts
                (alert_id, alert_type, severity, entity_name, description,
                 value, threshold, source_system)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert['id'],
                alert['type'],
                alert['severity'],
                alert['entity'],
                alert['description'],
                alert['value'],
                str(alert['threshold']),
                alert['source']
            ))

        conn.commit()
        conn.close()

    def generate_notifications(self, alerts: List[Dict]):
        """Generate alert notifications"""
        if not alerts:
            print("No alerts generated")
            return

        critical_alerts = [a for a in alerts if a['severity'] == 'CRITICAL']
        high_alerts = [a for a in alerts if a['severity'] == 'HIGH']

        alert_file = self.output_path / f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# CRITICAL ALERT NOTIFICATION
Generated: {datetime.now().isoformat()}

## ALERT SUMMARY
- **CRITICAL Alerts**: {len(critical_alerts)}
- **HIGH Alerts**: {len(high_alerts)}
- **Total Active Alerts**: {len(alerts)}

"""

        if critical_alerts:
            content += "## CRITICAL ALERTS\n\n"
            for alert in critical_alerts:
                content += f"- {alert['type']}: {alert['description']}\n"

        if high_alerts:
            content += "\n## HIGH PRIORITY ALERTS\n\n"
            for alert in high_alerts:
                content += f"- {alert['type']}: {alert['description']}\n"

        content += """
---
*Critical Alert System*
*Personal OSINT Learning Project*
"""

        alert_file.write_text(content)
        print(f"Alert notification saved to {alert_file}")

def main():
    alert_system = CriticalAlertSystem()
    alerts = alert_system.check_all_systems()

    print(f"Alert check complete!")
    print(f"Total alerts: {len(alerts)}")

if __name__ == "__main__":
    main()
