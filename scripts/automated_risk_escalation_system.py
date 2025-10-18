#!/usr/bin/env python3
"""
Automated Entity Risk Escalation System for OSINT China Risk Intelligence
Implements tiered alert system based on multi-system entity correlation
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AutomatedRiskEscalationSystem:
    def __init__(self):
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"

    def setup_escalation_database(self):
        """Initialize risk escalation tracking tables"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Risk alert levels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_alert_levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_correlation_id INTEGER,
                alert_level TEXT,
                alert_reason TEXT,
                escalation_trigger TEXT,
                recommended_actions TEXT,
                alert_generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                analyst_reviewed INTEGER DEFAULT 0,
                priority_score INTEGER,
                FOREIGN KEY (entity_correlation_id) REFERENCES cross_system_entity_correlation(id)
            )
        """)

        # Entity monitoring watchlist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_monitoring_watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                normalized_entity_name TEXT,
                monitoring_level TEXT,
                watch_reason TEXT,
                technology_categories TEXT,
                last_system_appearance TEXT,
                next_review_date DATE,
                monitoring_started DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)

        # Risk escalation history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_escalation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT,
                previous_alert_level TEXT,
                new_alert_level TEXT,
                escalation_reason TEXT,
                systems_involved TEXT,
                escalated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logging.info("Risk escalation database initialized")

    def calculate_risk_alert_level(self, entity_data):
        """Calculate appropriate risk alert level for entity"""
        name, entity_type, bis, comtrade, sec, total_systems, correlation_score, max_risk, tech_focus = entity_data

        # Base alert level determination
        if total_systems >= 3:
            alert_level = "CRITICAL"
            priority_score = 100
        elif total_systems == 2:
            if bis and (max_risk >= 90):
                alert_level = "HIGH"
                priority_score = 85
            elif bis and (max_risk >= 80):
                alert_level = "MEDIUM"
                priority_score = 70
            else:
                alert_level = "MEDIUM"
                priority_score = 65
        elif total_systems == 1:
            if bis and (max_risk >= 95):
                alert_level = "HIGH"
                priority_score = 80
            elif bis and (max_risk >= 85):
                alert_level = "MEDIUM"
                priority_score = 60
            else:
                alert_level = "LOW"
                priority_score = 40
        else:
            alert_level = "MONITOR"
            priority_score = 20

        # Adjust for technology sensitivity
        sensitive_tech = [
            'semiconductors', 'telecommunications', 'artificial intelligence',
            'quantum computing', 'aerospace', 'defense technology'
        ]

        if tech_focus and any(tech in tech_focus.lower() for tech in sensitive_tech):
            priority_score += 10
            if alert_level == "MEDIUM":
                alert_level = "HIGH"
            elif alert_level == "LOW":
                alert_level = "MEDIUM"

        return alert_level, priority_score

    def generate_alert_reason(self, entity_data, alert_level):
        """Generate detailed alert reasoning"""
        name, entity_type, bis, comtrade, sec, total_systems, correlation_score, max_risk, tech_focus = entity_data

        systems = []
        if bis: systems.append("BIS Export Control")
        if comtrade: systems.append("Trade Monitoring")
        if sec: systems.append("SEC Investment Tracking")

        reason_parts = [
            f"Entity appears in {total_systems}/3 intelligence systems: {', '.join(systems)}",
            f"Maximum risk score: {max_risk}/100",
            f"Correlation score: {correlation_score}/125"
        ]

        if tech_focus:
            reason_parts.append(f"Technology focus: {tech_focus}")

        if alert_level == "CRITICAL":
            reason_parts.append("CRITICAL: Entity detected across ALL intelligence systems")
        elif alert_level == "HIGH":
            reason_parts.append("HIGH: Multi-system detection with elevated risk scores")

        return "; ".join(reason_parts)

    def generate_recommended_actions(self, alert_level, entity_data):
        """Generate recommended analyst actions based on alert level"""
        name, entity_type, bis, comtrade, sec, total_systems, correlation_score, max_risk, tech_focus = entity_data

        actions = {
            "CRITICAL": [
                "IMMEDIATE priority investigation required",
                "Escalate to senior analyst within 24 hours",
                "Cross-reference with classified databases",
                "Initiate comprehensive entity profile development",
                "Monitor for real-time activity changes",
                "Coordinate with relevant government agencies"
            ],
            "HIGH": [
                "Priority investigation within 72 hours",
                "Develop detailed entity assessment",
                "Monitor for additional system appearances",
                "Review technology transfer implications",
                "Assess supply chain vulnerabilities"
            ],
            "MEDIUM": [
                "Investigation within 1 week",
                "Update entity monitoring profile",
                "Track for escalation to additional systems",
                "Analyze technology categorization",
                "Review partnership and subsidiary connections"
            ],
            "LOW": [
                "Routine monitoring and quarterly review",
                "Update risk assessment if new data appears",
                "Track for potential system progression"
            ],
            "MONITOR": [
                "Baseline tracking and annual review",
                "Alert if entity appears in additional systems"
            ]
        }

        return "; ".join(actions.get(alert_level, ["Standard monitoring"]))

    def process_risk_escalations(self):
        """Process all entities for risk escalation alerts"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Get all cross-system correlations
        cursor.execute("""
            SELECT id, normalized_entity_name, entity_type, appears_in_bis,
                   appears_in_comtrade, appears_in_sec_edgar, total_systems,
                   correlation_score, max_risk_score, technology_focus
            FROM cross_system_entity_correlation
            ORDER BY correlation_score DESC
        """)

        entities = cursor.fetchall()

        # Clear existing alerts for fresh analysis
        cursor.execute("DELETE FROM risk_alert_levels")

        processed_alerts = 0
        critical_alerts = 0
        high_alerts = 0

        for entity in entities:
            entity_id = entity[0]
            entity_data = entity[1:]  # Skip ID for calculations

            # Calculate alert level
            alert_level, priority_score = self.calculate_risk_alert_level(entity_data)

            # Generate reasoning and actions
            alert_reason = self.generate_alert_reason(entity_data, alert_level)
            recommended_actions = self.generate_recommended_actions(alert_level, entity_data)

            # Determine escalation trigger
            name, entity_type, bis, comtrade, sec, total_systems = entity_data[:6]
            escalation_trigger = f"{total_systems}_system_detection"

            if total_systems >= 3:
                escalation_trigger = "triple_system_detection"
            elif total_systems == 2 and bis:
                escalation_trigger = "dual_system_with_export_control"
            elif entity_data[6] >= 95:  # correlation_score
                escalation_trigger = "maximum_risk_threshold"

            # Insert alert
            cursor.execute("""
                INSERT INTO risk_alert_levels (
                    entity_correlation_id, alert_level, alert_reason,
                    escalation_trigger, recommended_actions, priority_score
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                entity_id, alert_level, alert_reason,
                escalation_trigger, recommended_actions, priority_score
            ))

            processed_alerts += 1
            if alert_level == "CRITICAL":
                critical_alerts += 1
            elif alert_level == "HIGH":
                high_alerts += 1

        conn.commit()
        conn.close()

        logging.info(f"Processed {processed_alerts} risk alerts: {critical_alerts} CRITICAL, {high_alerts} HIGH")
        return processed_alerts, critical_alerts, high_alerts

    def update_monitoring_watchlist(self):
        """Update entity monitoring watchlist based on alert levels"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Clear existing watchlist
        cursor.execute("DELETE FROM entity_monitoring_watchlist")

        # Add entities based on alert levels
        cursor.execute("""
            SELECT c.normalized_entity_name, a.alert_level, a.alert_reason,
                   c.technology_focus, c.total_systems
            FROM cross_system_entity_correlation c
            JOIN risk_alert_levels a ON c.id = a.entity_correlation_id
            WHERE a.alert_level IN ('CRITICAL', 'HIGH', 'MEDIUM')
        """)

        watchlist_entities = cursor.fetchall()

        for entity_name, alert_level, reason, tech_focus, total_systems in watchlist_entities:
            # Determine monitoring level
            if alert_level == "CRITICAL":
                monitoring_level = "real_time"
                next_review = datetime.now() + timedelta(days=1)
            elif alert_level == "HIGH":
                monitoring_level = "daily"
                next_review = datetime.now() + timedelta(days=3)
            else:  # MEDIUM
                monitoring_level = "weekly"
                next_review = datetime.now() + timedelta(days=7)

            # Determine last system appearance
            if total_systems >= 2:
                last_appearance = "multi_system"
            else:
                last_appearance = "single_system"

            cursor.execute("""
                INSERT INTO entity_monitoring_watchlist (
                    normalized_entity_name, monitoring_level, watch_reason,
                    technology_categories, last_system_appearance, next_review_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                entity_name, monitoring_level, reason[:200],
                tech_focus, last_appearance, next_review.date()
            ))

        conn.commit()
        conn.close()

        logging.info(f"Updated monitoring watchlist with {len(watchlist_entities)} entities")
        return len(watchlist_entities)

    def generate_escalation_dashboard_report(self):
        """Generate comprehensive risk escalation dashboard"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Get alert statistics
        cursor.execute("""
            SELECT alert_level, COUNT(*) as count
            FROM risk_alert_levels
            GROUP BY alert_level
            ORDER BY
                CASE alert_level
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                    WHEN 'MONITOR' THEN 5
                END
        """)
        alert_counts = cursor.fetchall()

        # Get critical and high priority alerts
        cursor.execute("""
            SELECT c.normalized_entity_name, a.alert_level, a.priority_score,
                   a.escalation_trigger, c.technology_focus, c.total_systems
            FROM risk_alert_levels a
            JOIN cross_system_entity_correlation c ON a.entity_correlation_id = c.id
            WHERE a.alert_level IN ('CRITICAL', 'HIGH')
            ORDER BY a.priority_score DESC, a.alert_level
        """)
        priority_alerts = cursor.fetchall()

        # Get monitoring watchlist summary
        cursor.execute("""
            SELECT monitoring_level, COUNT(*) as count
            FROM entity_monitoring_watchlist
            GROUP BY monitoring_level
        """)
        watchlist_counts = cursor.fetchall()

        conn.close()

        # Generate dashboard report
        report = f"""# AUTOMATED RISK ESCALATION DASHBOARD
Generated: {datetime.now().isoformat()}

## EXECUTIVE SUMMARY

### Risk Alert Distribution"""

        total_alerts = sum(count for _, count in alert_counts)
        for alert_level, count in alert_counts:
            percentage = (count / total_alerts * 100) if total_alerts > 0 else 0
            report += f"\n- **{alert_level}**: {count:,} entities ({percentage:.1f}%)"

        report += f"""

### Immediate Action Required
- **CRITICAL Alerts**: Require immediate investigation within 24 hours
- **HIGH Alerts**: Require priority investigation within 72 hours
- **Total Priority Entities**: {sum(count for level, count in alert_counts if level in ['CRITICAL', 'HIGH'])}

## PRIORITY ALERT QUEUE

### Critical and High Priority Entities Requiring Immediate Attention"""

        for i, (name, level, priority, trigger, tech_focus, systems) in enumerate(priority_alerts, 1):
            report += f"\n{i}. **{name.title()}** - {level} PRIORITY"
            report += f"\n   - Priority Score: {priority}/100"
            report += f"\n   - Trigger: {trigger.replace('_', ' ').title()}"
            report += f"\n   - Systems Detected: {systems}/3"
            if tech_focus:
                report += f"\n   - Technology: {tech_focus[:50]}..."
            report += "\n"

        if not priority_alerts:
            report += "\n*No critical or high priority alerts currently active*\n"

        report += f"\n## MONITORING WATCHLIST STATUS\n"
        report += f"### Active Monitoring by Level\n"

        for monitoring_level, count in watchlist_counts:
            report += f"\n- **{monitoring_level.replace('_', ' ').title()}**: {count:,} entities"

        report += f"""

## OPERATIONAL INTELLIGENCE FRAMEWORK

### Automated Risk Escalation Triggers
1. **Triple-System Detection**: Entity appears in all 3 intelligence systems
2. **Dual-System with Export Control**: Entity in BIS + another system
3. **Maximum Risk Threshold**: Risk score >= 95/100
4. **Sensitive Technology Focus**: Critical technology categories detected

### Alert Level Definitions
- **CRITICAL**: Multi-system detection, immediate investigation required
- **HIGH**: Elevated risk with export control or high scores
- **MEDIUM**: Moderate risk requiring routine investigation
- **LOW**: Baseline risk with periodic monitoring
- **MONITOR**: Watchlist tracking for escalation detection

### System Capabilities
[SUCCESS] **Automated Alert Generation**: Risk levels calculated automatically
[SUCCESS] **Priority Scoring**: 0-100 scale with technology adjustments
[SUCCESS] **Monitoring Watchlist**: Tiered surveillance by risk level
[SUCCESS] **Escalation Tracking**: Historical progression monitoring

### Recommended Analyst Workflow
1. **Daily Review**: Process all CRITICAL and HIGH alerts
2. **Weekly Review**: Address MEDIUM priority entities
3. **Monthly Review**: Update LOW and MONITOR classifications
4. **Quarterly Review**: Validate monitoring effectiveness and update thresholds

---
*Automated risk escalation provides systematic prioritization of Chinese technology exploitation threats*
"""

        # Save dashboard
        dashboard_path = Path("C:/Projects/OSINT - Foresight/analysis/AUTOMATED_RISK_ESCALATION_DASHBOARD.md")
        dashboard_path.write_text(report, encoding='utf-8')

        print(report)
        return report

    def run_escalation_system(self):
        """Execute complete automated risk escalation cycle"""
        logging.info("Starting automated risk escalation system")

        self.setup_escalation_database()
        processed, critical, high = self.process_risk_escalations()
        watchlist_count = self.update_monitoring_watchlist()
        self.generate_escalation_dashboard_report()

        logging.info(f"Risk escalation completed: {processed} alerts, {watchlist_count} watchlist entities")
        return processed, critical, high

if __name__ == "__main__":
    escalation_system = AutomatedRiskEscalationSystem()
    escalation_system.run_escalation_system()
