#!/usr/bin/env python3
"""
Critical Alert System
Real-time alerting for critical OSINT discoveries
"""

import json
import sqlite3
import smtplib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import winsound

class CriticalAlertSystem:
    def __init__(self):
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE")
        self.alert_db = self.warehouse_path / "osint_master.db"
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis/alerts")
        self.output_path.mkdir(exist_ok=True)

        # Alert thresholds
        self.thresholds = {
            'leonardo_score': 85,  # Critical if Leonardo score > 85
            'patent_surge': 50,     # Critical if patent count increases > 50%
            'mcf_relevance': 70,    # Critical if MCF score > 70
            'arctic_chinese': 60,   # Critical if Chinese Arctic score > 60
            'network_centrality': 0.8  # Critical if centrality > 0.8
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

        cur.execute('''
            CREATE TABLE IF NOT EXISTS alert_history (
                check_id TEXT PRIMARY KEY,
                check_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_checks INTEGER,
                alerts_generated INTEGER,
                critical_count INTEGER,
                high_count INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    def check_all_systems(self) -> List[Dict]:
        """Check all intelligence systems for critical alerts"""
        print("Checking all systems for critical alerts...")
        alerts = []

        # Check Leonardo scores
        alerts.extend(self.check_leonardo_alerts())

        # Check patent surges
        alerts.extend(self.check_patent_alerts())

        # Check MCF relevance
        alerts.extend(self.check_mcf_alerts())

        # Check Arctic-Chinese activities
        alerts.extend(self.check_arctic_alerts())

        # Check network centrality
        alerts.extend(self.check_network_alerts())

        # Check predictive indicators
        alerts.extend(self.check_predictive_alerts())

        # Store alerts
        self.store_alerts(alerts)

        # Generate alert notifications
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
                    'id': f"leo_{row[0]}_{row[1]}_{datetime.now().strftime('%Y%m%d%H%M')}",
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
        """Check for patent filing surges"""
        alerts = []

        patent_db = self.warehouse_path / 'osint_master.db'
        if patent_db.exists():
            conn = sqlite3.connect(patent_db)
            cur = conn.cursor()

            # Check for anomalies without mundane explanations
            cur.execute('''
                SELECT date, count, assignee
                FROM anomaly_tracking
                WHERE anomaly_flag = 1
                  AND mundane_explanation IS NULL
            ''')

            for row in cur.fetchall():
                alerts.append({
                    'id': f"pat_{row[2]}_{row[0].replace('-','')}_{datetime.now().strftime('%H%M')}",
                    'type': 'PATENT_SURGE',
                    'severity': 'HIGH',
                    'entity': row[2],
                    'description': f"Unusual patent filing surge: {row[1]} patents",
                    'value': row[1],
                    'threshold': 'Statistical anomaly',
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
                    'entity': row[1][:50],
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
                    'description': f"Significant Chinese Arctic content in {row[1][:50]}",
                    'value': row[2],
                    'threshold': self.thresholds['arctic_chinese'],
                    'source': 'Arctic Intelligence System'
                })

            conn.close()

        return alerts

    def check_network_alerts(self) -> List[Dict]:
        """Check for critical network centrality"""
        alerts = []

        network_db = self.warehouse_path / 'osint_master.db'
        if network_db.exists():
            try:
                conn = sqlite3.connect(network_db)
                cur = conn.cursor()

                # Check if network_clusters table exists with centrality data
                cur.execute('''
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='network_clusters'
                ''')

                if cur.fetchone():
                    cur.execute('''
                        SELECT entity_name, centrality_score
                        FROM network_clusters
                        WHERE centrality_score > ?
                    ''', (self.thresholds['network_centrality'],))

                    for row in cur.fetchall():
                        alerts.append({
                            'id': f"net_{row[0][:20]}_{datetime.now().strftime('%Y%m%d%H%M')}",
                            'type': 'NETWORK_CRITICAL_NODE',
                            'severity': 'CRITICAL',
                            'entity': row[0],
                            'description': f"Critical network position detected",
                            'value': row[1],
                            'threshold': self.thresholds['network_centrality'],
                            'source': 'Network Analysis System'
                        })

                conn.close()
            except Exception as e:
                print(f"Network alert check error: {e}")

        return alerts

    def check_predictive_alerts(self) -> List[Dict]:
        """Check predictive indicators"""
        alerts = []

        predictive_db = self.warehouse_path / 'osint_master.db'
        if predictive_db.exists():
            conn = sqlite3.connect(predictive_db)
            cur = conn.cursor()

            # Get latest critical indicators
            cur.execute('''
                SELECT entity_name, indicator_type, measurement_value
                FROM indicator_measurements
                WHERE status = 'CRITICAL'
                  AND measurement_date = (SELECT MAX(measurement_date) FROM indicator_measurements)
            ''')

            for row in cur.fetchall():
                alerts.append({
                    'id': f"pred_{row[0][:15]}_{row[1][:10]}_{datetime.now().strftime('%H%M')}",
                    'type': 'PREDICTIVE_CRITICAL',
                    'severity': 'CRITICAL',
                    'entity': row[0],
                    'description': f"Critical predictive indicator: {row[1]}",
                    'value': row[2],
                    'threshold': 'Critical threshold exceeded',
                    'source': 'Predictive Indicators System'
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

        # Log check history
        critical_count = len([a for a in alerts if a['severity'] == 'CRITICAL'])
        high_count = len([a for a in alerts if a['severity'] == 'HIGH'])

        cur.execute('''
            INSERT INTO alert_history
            (check_id, total_checks, alerts_generated, critical_count, high_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            f"check_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            6,  # Number of systems checked
            len(alerts),
            critical_count,
            high_count
        ))

        conn.commit()
        conn.close()

    def generate_notifications(self, alerts: List[Dict]):
        """Generate alert notifications"""
        critical_alerts = [a for a in alerts if a['severity'] == 'CRITICAL']
        high_alerts = [a for a in alerts if a['severity'] == 'HIGH']

        if critical_alerts or high_alerts:
            # Create alert file
            alert_file = self.output_path / f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            content = f"""# CRITICAL ALERT NOTIFICATION
Generated: {datetime.now().isoformat()}

## ALERT SUMMARY
- **CRITICAL Alerts**: {len(critical_alerts)}
- **HIGH Alerts**: {len(high_alerts)}
- **Total Active Alerts**: {len(alerts)}

"""

            if critical_alerts:
                content += "## 🚨 CRITICAL ALERTS - IMMEDIATE ACTION REQUIRED\n\n"
                for alert in critical_alerts:
                    content += f"""### {alert['type']}
- **Entity**: {alert['entity']}
- **Description**: {alert['description']}
- **Value**: {alert['value']}
- **Threshold**: {alert['threshold']}
- **Source**: {alert['source']}

"""

            if high_alerts:
                content += "## ⚠️ HIGH PRIORITY ALERTS\n\n"
                for alert in high_alerts:
                    content += f"""### {alert['type']}
- **Entity**: {alert['entity']}
- **Description**: {alert['description']}
- **Value**: {alert['value']}
- **Source**: {alert['source']}

"""

            content += """## RECOMMENDED ACTIONS

### Immediate Response
1. Review all CRITICAL alerts for validation
2. Initiate response protocols for confirmed threats
3. Enhance monitoring of alerted entities

### Follow-up Actions
1. Deep-dive analysis of alert triggers
2. Cross-reference with additional intelligence sources
3. Update threat assessments based on new alerts

---
*Critical Alert System*
*Personal OSINT Learning Project*
"""

            alert_file.write_text(content)
            print(f"Alert notification saved to {alert_file}")

            # Sound alert for critical alerts (Windows only)
            if critical_alerts:
                try:
                    winsound.Beep(1000, 500)  # 1000Hz for 500ms
                except:
                    pass  # Ignore if sound fails

def main():
    alert_system = CriticalAlertSystem()
    alerts = alert_system.check_all_systems()

    print(f"Alert check complete!")
    print(f"Total alerts generated: {len(alerts)}")
    print(f"Critical: {len([a for a in alerts if a['severity'] == 'CRITICAL'])}")
    print(f"High: {len([a for a in alerts if a['severity'] == 'HIGH'])}")

if __name__ == "__main__":
    main()
