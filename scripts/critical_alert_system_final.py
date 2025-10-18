#!/usr/bin/env python3
"""
Critical Alert System - FINAL FIXED VERSION
Real-time alerting for critical OSINT discoveries
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class CriticalAlertSystem:
    def __init__(self):
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE")
        self.alert_db = self.warehouse_path / "osint_master.db"
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis/alerts")
        self.output_path.mkdir(exist_ok=True)

        self.thresholds = {
            'leonardo_score': 85,
            'mcf_relevance': 70,
            'arctic_chinese': 60
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

        # Check MCF relevance
        alerts.extend(self.check_mcf_alerts())

        # Check Arctic-Chinese activities
        alerts.extend(self.check_arctic_alerts())

        # Check patent search activity
        alerts.extend(self.check_patent_activity())

        # Store alerts
        self.store_alerts(alerts)

        # Generate notifications
        self.generate_notifications(alerts)

        return alerts

    def check_leonardo_alerts(self) -> List[Dict]:
        """Check for critical Leonardo scores"""
        alerts = []

        leonardo_db = self.warehouse_path / 'osint_master.db'
        if leonardo_db.exists():
            try:
                conn = sqlite3.connect(leonardo_db)
                cur = conn.cursor()

                cur.execute('''
                    SELECT entity_name, technology_name, leonardo_composite_score
                    FROM technology_assessments
                    WHERE leonardo_composite_score > ?
                ''', (self.thresholds['leonardo_score'],))

                for row in cur.fetchall():
                    alerts.append({
                        'id': f"leo_{row[0][:20]}_{datetime.now().strftime('%Y%m%d%H%M')}",
                        'type': 'LEONARDO_CRITICAL',
                        'severity': 'CRITICAL',
                        'entity': row[0],
                        'description': f"Critical Leonardo score for {row[1]}",
                        'value': row[2],
                        'threshold': self.thresholds['leonardo_score'],
                        'source': 'Leonardo Scoring System'
                    })

                conn.close()
            except Exception as e:
                print(f"Leonardo alert check error: {e}")

        return alerts

    def check_patent_activity(self) -> List[Dict]:
        """Check for unusual patent search activity"""
        alerts = []

        patent_db = self.warehouse_path / 'osint_master.db'
        if patent_db.exists():
            try:
                conn = sqlite3.connect(patent_db)
                cur = conn.cursor()

                # Count searches by term
                cur.execute('''
                    SELECT search_term, COUNT(*) as cnt
                    FROM patent_searches
                    WHERE search_term IS NOT NULL
                    GROUP BY search_term
                    HAVING cnt > 5
                    ORDER BY cnt DESC
                    LIMIT 5
                ''')

                for row in cur.fetchall():
                    if row[1] > 10:  # Alert if more than 10 searches for same term
                        alerts.append({
                            'id': f"pat_{row[0][:20].replace(' ','_')}_{datetime.now().strftime('%H%M')}",
                            'type': 'PATENT_FOCUS_AREA',
                            'severity': 'MEDIUM',
                            'entity': row[0],
                            'description': f"High patent search focus: {row[1]} searches",
                            'value': row[1],
                            'threshold': 10,
                            'source': 'Patent Monitoring System'
                        })

                conn.close()
            except Exception as e:
                print(f"Patent alert check error: {e}")

        return alerts

    def check_mcf_alerts(self) -> List[Dict]:
        """Check for high MCF relevance"""
        alerts = []

        mcf_db = self.warehouse_path / 'osint_master.db'
        if mcf_db.exists():
            try:
                conn = sqlite3.connect(mcf_db)
                cur = conn.cursor()

                cur.execute('''
                    SELECT filename, title, mcf_relevance_score
                    FROM mcf_reports
                    WHERE mcf_relevance_score > ?
                    ORDER BY mcf_relevance_score DESC
                    LIMIT 10
                ''', (self.thresholds['mcf_relevance'],))

                for row in cur.fetchall():
                    alerts.append({
                        'id': f"mcf_{row[0][:20]}_{datetime.now().strftime('%Y%m%d%H%M')}",
                        'type': 'MCF_HIGH_RELEVANCE',
                        'severity': 'HIGH',
                        'entity': row[1][:50] if row[1] else 'Unknown Report',
                        'description': f"High MCF relevance score",
                        'value': row[2],
                        'threshold': self.thresholds['mcf_relevance'],
                        'source': 'MCF Analysis System'
                    })

                conn.close()
            except Exception as e:
                print(f"MCF alert check error: {e}")

        return alerts

    def check_arctic_alerts(self) -> List[Dict]:
        """Check for Chinese Arctic activities"""
        alerts = []

        arctic_db = self.warehouse_path / 'osint_master.db'
        if arctic_db.exists():
            try:
                conn = sqlite3.connect(arctic_db)
                cur = conn.cursor()

                cur.execute('''
                    SELECT filename, title, chinese_arctic_score
                    FROM arctic_reports
                    WHERE chinese_arctic_score > ?
                    ORDER BY chinese_arctic_score DESC
                    LIMIT 10
                ''', (self.thresholds['arctic_chinese'],))

                for row in cur.fetchall():
                    alerts.append({
                        'id': f"arc_{row[0][:20]}_{datetime.now().strftime('%Y%m%d%H%M')}",
                        'type': 'CHINESE_ARCTIC_ACTIVITY',
                        'severity': 'HIGH',
                        'entity': 'Chinese Arctic Operations',
                        'description': f"Significant Chinese Arctic activity detected",
                        'value': row[2],
                        'threshold': self.thresholds['arctic_chinese'],
                        'source': 'Arctic Intelligence System'
                    })

                conn.close()
            except Exception as e:
                print(f"Arctic alert check error: {e}")

        return alerts

    def store_alerts(self, alerts: List[Dict]):
        """Store alerts in database"""
        if not alerts:
            return

        conn = sqlite3.connect(self.alert_db)
        cur = conn.cursor()

        for alert in alerts:
            try:
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
            except Exception as e:
                print(f"Error storing alert {alert['id']}: {e}")

        # Log check history
        critical_count = len([a for a in alerts if a['severity'] == 'CRITICAL'])
        high_count = len([a for a in alerts if a['severity'] == 'HIGH'])

        cur.execute('''
            INSERT INTO alert_history
            (check_id, total_checks, alerts_generated, critical_count, high_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            f"check_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            4,  # Number of systems checked
            len(alerts),
            critical_count,
            high_count
        ))

        conn.commit()
        conn.close()

    def generate_notifications(self, alerts: List[Dict]):
        """Generate alert notifications"""
        if not alerts:
            print("No alerts generated - all systems normal")
            return

        critical_alerts = [a for a in alerts if a['severity'] == 'CRITICAL']
        high_alerts = [a for a in alerts if a['severity'] == 'HIGH']
        medium_alerts = [a for a in alerts if a['severity'] == 'MEDIUM']

        # Create alert file
        alert_file = self.output_path / f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""# CRITICAL ALERT NOTIFICATION
Generated: {datetime.now().isoformat()}
System: Personal OSINT Learning Project

## ALERT SUMMARY
- **CRITICAL Alerts**: {len(critical_alerts)}
- **HIGH Alerts**: {len(high_alerts)}
- **MEDIUM Alerts**: {len(medium_alerts)}
- **Total Active Alerts**: {len(alerts)}

"""

        if critical_alerts:
            content += "## 🚨 CRITICAL ALERTS - IMMEDIATE ACTION REQUIRED\n\n"
            for alert in critical_alerts:
                content += f"""### {alert['type']}
- **Entity**: {alert['entity']}
- **Description**: {alert['description']}
- **Value**: {alert['value']:.1f}
- **Threshold**: {alert['threshold']}
- **Source**: {alert['source']}

"""

        if high_alerts:
            content += "## ⚠️ HIGH PRIORITY ALERTS\n\n"
            for alert in high_alerts:
                content += f"""### {alert['type']}
- **Entity**: {alert['entity']}
- **Description**: {alert['description']}
- **Value**: {alert['value']:.1f}
- **Threshold**: {alert['threshold']}
- **Source**: {alert['source']}

"""

        if medium_alerts:
            content += "## 📊 MEDIUM PRIORITY ALERTS\n\n"
            for alert in medium_alerts:
                content += f"""### {alert['type']}
- **Entity**: {alert['entity']}
- **Description**: {alert['description']}
- **Value**: {alert['value']}
- **Source**: {alert['source']}

"""

        content += """## RECOMMENDED ACTIONS

### Immediate Response
1. Review all CRITICAL alerts for validation
2. Deep-dive on entities with multiple alert types
3. Cross-reference with additional intelligence sources

### Follow-up Actions
1. Enhance monitoring of alerted entities
2. Update threat assessments based on new alerts
3. Generate detailed reports for critical findings

---
*Critical Alert System*
*Personal OSINT Learning Project*
*Automated Intelligence Monitoring*
"""

        alert_file.write_text(content, encoding='utf-8')
        print(f"Alert notification saved to {alert_file}")

        # Sound alert for critical alerts (Windows only)
        if critical_alerts:
            try:
                import winsound
                winsound.Beep(1000, 300)  # 1000Hz for 300ms
            except:
                pass  # Ignore if sound fails

def main():
    alert_system = CriticalAlertSystem()
    alerts = alert_system.check_all_systems()

    print(f"\nAlert check complete!")
    print(f"Total alerts generated: {len(alerts)}")

    critical_count = len([a for a in alerts if a['severity'] == 'CRITICAL'])
    high_count = len([a for a in alerts if a['severity'] == 'HIGH'])
    medium_count = len([a for a in alerts if a['severity'] == 'MEDIUM'])

    if critical_count > 0:
        print(f"⚠️  CRITICAL: {critical_count}")
    if high_count > 0:
        print(f"⚠️  HIGH: {high_count}")
    if medium_count > 0:
        print(f"📊 MEDIUM: {medium_count}")

if __name__ == "__main__":
    main()
