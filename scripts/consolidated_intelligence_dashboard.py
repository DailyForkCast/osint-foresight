#!/usr/bin/env python3
"""
Consolidated Intelligence Dashboard for OSINT China Risk Intelligence
Provides unified overview of all intelligence systems and their outputs
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ConsolidatedIntelligenceDashboard:
    def __init__(self):
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"

    def get_system_statistics(self):
        """Get comprehensive statistics from all intelligence systems"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        stats = {}

        # BIS Entity List statistics
        cursor.execute("SELECT COUNT(*) FROM bis_entity_list_fixed WHERE china_related = 1")
        stats['bis_entities'] = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(risk_score) FROM bis_entity_list_fixed WHERE china_related = 1")
        avg_bis_risk = cursor.fetchone()[0]
        stats['bis_avg_risk'] = round(avg_bis_risk, 1) if avg_bis_risk else 0

        # UN Comtrade statistics
        cursor.execute("SELECT COUNT(*) FROM comtrade_technology_flows_fixed WHERE china_related = 1")
        stats['comtrade_flows'] = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(trade_value_usd) FROM comtrade_technology_flows_fixed WHERE china_related = 1")
        total_trade = cursor.fetchone()[0]
        stats['total_trade_value'] = total_trade / 1000000000 if total_trade else 0  # Convert to billions

        # SEC EDGAR statistics
        cursor.execute("SELECT COUNT(*) FROM sec_edgar_local_analysis WHERE chinese_connection_detected = 1")
        stats['sec_entities'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sec_edgar_chinese_investors")
        stats['chinese_investors'] = cursor.fetchone()[0]

        # Cross-system correlation statistics
        cursor.execute("SELECT COUNT(*) FROM cross_system_entity_correlation")
        stats['total_correlations'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM cross_system_entity_correlation WHERE total_systems >= 2")
        stats['multi_system_entities'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM cross_system_entity_correlation WHERE total_systems = 3")
        stats['triple_system_entities'] = cursor.fetchone()[0]

        # Risk escalation statistics
        cursor.execute("SELECT alert_level, COUNT(*) FROM risk_alert_levels GROUP BY alert_level")
        alert_counts = dict(cursor.fetchall())
        stats['critical_alerts'] = alert_counts.get('CRITICAL', 0)
        stats['high_alerts'] = alert_counts.get('HIGH', 0)
        stats['medium_alerts'] = alert_counts.get('MEDIUM', 0)
        stats['total_alerts'] = sum(alert_counts.values())

        conn.close()
        return stats

    def get_top_priority_entities(self, limit=10):
        """Get highest priority entities across all systems"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.normalized_entity_name, c.entity_type, c.total_systems,
                   c.correlation_score, c.max_risk_score, c.technology_focus,
                   a.alert_level, a.priority_score
            FROM cross_system_entity_correlation c
            LEFT JOIN risk_alert_levels a ON c.id = a.entity_correlation_id
            ORDER BY a.priority_score DESC, c.correlation_score DESC
            LIMIT ?
        """, (limit,))

        entities = cursor.fetchall()
        conn.close()
        return entities

    def get_technology_distribution(self):
        """Get distribution of entities by technology focus"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Get technology categories from cross-system correlations
        cursor.execute("""
            SELECT technology_focus, COUNT(*) as count
            FROM cross_system_entity_correlation
            WHERE technology_focus IS NOT NULL AND technology_focus != ''
            GROUP BY technology_focus
            ORDER BY count DESC
            LIMIT 15
        """)

        tech_data = cursor.fetchall()
        conn.close()

        # Process and normalize technology categories
        tech_distribution = {}
        for tech_focus, count in tech_data:
            # Split on semicolons and commas to handle multiple categories
            categories = []
            for separator in [';', ',']:
                if separator in tech_focus:
                    categories.extend([cat.strip() for cat in tech_focus.split(separator)])
                    break
            else:
                categories = [tech_focus.strip()]

            for category in categories:
                if category:
                    tech_distribution[category] = tech_distribution.get(category, 0) + count

        # Return top 10 technologies
        return sorted(tech_distribution.items(), key=lambda x: x[1], reverse=True)[:10]

    def get_system_coverage_analysis(self):
        """Analyze entity coverage across different intelligence systems"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        coverage = {
            'bis_only': 0,
            'comtrade_only': 0,
            'sec_only': 0,
            'bis_comtrade': 0,
            'bis_sec': 0,
            'comtrade_sec': 0,
            'all_three': 0
        }

        cursor.execute("""
            SELECT appears_in_bis, appears_in_comtrade, appears_in_sec_edgar, COUNT(*)
            FROM cross_system_entity_correlation
            GROUP BY appears_in_bis, appears_in_comtrade, appears_in_sec_edgar
        """)

        for bis, comtrade, sec, count in cursor.fetchall():
            total_systems = bis + comtrade + sec

            if total_systems == 3:
                coverage['all_three'] = count
            elif total_systems == 2:
                if bis and comtrade:
                    coverage['bis_comtrade'] = count
                elif bis and sec:
                    coverage['bis_sec'] = count
                elif comtrade and sec:
                    coverage['comtrade_sec'] = count
            elif total_systems == 1:
                if bis:
                    coverage['bis_only'] = count
                elif comtrade:
                    coverage['comtrade_only'] = count
                elif sec:
                    coverage['sec_only'] = count

        conn.close()
        return coverage

    def get_recent_intelligence_activity(self):
        """Get recent intelligence gathering activity"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        activity = {}

        # Recent correlations
        cursor.execute("""
            SELECT COUNT(*), MAX(first_detected)
            FROM cross_system_entity_correlation
            WHERE first_detected >= date('now', '-7 days')
        """)
        recent_correlations, last_correlation = cursor.fetchone()
        activity['recent_correlations'] = recent_correlations or 0
        activity['last_correlation'] = last_correlation

        # Recent alerts
        cursor.execute("""
            SELECT COUNT(*), MAX(alert_generated_at)
            FROM risk_alert_levels
            WHERE alert_generated_at >= datetime('now', '-7 days')
        """)
        recent_alerts, last_alert = cursor.fetchone()
        activity['recent_alerts'] = recent_alerts or 0
        activity['last_alert'] = last_alert

        # Watchlist updates
        cursor.execute("""
            SELECT COUNT(*), MAX(monitoring_started)
            FROM entity_monitoring_watchlist
            WHERE monitoring_started >= datetime('now', '-7 days')
        """)
        recent_watchlist, last_watchlist = cursor.fetchone()
        activity['recent_watchlist'] = recent_watchlist or 0
        activity['last_watchlist'] = last_watchlist

        conn.close()
        return activity

    def generate_executive_intelligence_brief(self):
        """Generate comprehensive executive intelligence brief"""
        stats = self.get_system_statistics()
        top_entities = self.get_top_priority_entities(15)
        tech_distribution = self.get_technology_distribution()
        coverage = self.get_system_coverage_analysis()
        activity = self.get_recent_intelligence_activity()

        # Calculate key metrics
        coverage_percentage = (stats['multi_system_entities'] / stats['total_correlations'] * 100) if stats['total_correlations'] > 0 else 0
        critical_percentage = (stats['critical_alerts'] / stats['total_alerts'] * 100) if stats['total_alerts'] > 0 else 0

        report = f"""# EXECUTIVE INTELLIGENCE BRIEF - CHINA TECHNOLOGY EXPLOITATION
Generated: {datetime.now().isoformat()}

## STRATEGIC INTELLIGENCE SUMMARY

### Multi-System Intelligence Platform Status
- **Total Chinese Entities Tracked**: {stats['total_correlations']:,}
- **Multi-System Entity Coverage**: {stats['multi_system_entities']:,} entities ({coverage_percentage:.1f}%)
- **Triple-System Critical Entities**: {stats['triple_system_entities']:,}
- **Active Risk Alerts**: {stats['total_alerts']:,} ({stats['critical_alerts']} CRITICAL, {stats['high_alerts']} HIGH)

### Intelligence Collection Overview
- **BIS Export Control Entities**: {stats['bis_entities']:,} (avg risk: {stats['bis_avg_risk']}/100)
- **Technology Trade Flows**: {stats['comtrade_flows']:,} (${stats['total_trade_value']:.1f}B value)
- **SEC Investment Tracking**: {stats['sec_entities']:,} entities, {stats['chinese_investors']:,} investors

## CRITICAL THREAT ENTITIES

### Highest Priority Chinese Technology Exploitation Targets"""

        for i, entity in enumerate(top_entities, 1):
            name, entity_type, systems, correlation_score, risk_score, tech_focus, alert_level, priority = entity

            systems_text = f"{systems}/3 systems"
            alert_text = f" - {alert_level} ALERT" if alert_level else ""

            report += f"\n{i}. **{name.title()}** ({entity_type}){alert_text}"
            report += f"\n   - Systems: {systems_text} | Risk: {risk_score}/100 | Priority: {priority or 'N/A'}/100"
            if tech_focus:
                report += f"\n   - Technology: {tech_focus[:60]}{'...' if len(tech_focus) > 60 else ''}"
            report += "\n"

        report += f"\n## TECHNOLOGY EXPLOITATION PATTERNS\n"
        report += f"### Critical Technology Categories Under Chinese Focus\n"

        for i, (tech, count) in enumerate(tech_distribution, 1):
            report += f"\n{i}. **{tech.title()}**: {count:,} entities"

        report += f"""

## INTELLIGENCE SYSTEM COVERAGE ANALYSIS

### Entity Detection by System Combination
- **Export Control Only (BIS)**: {coverage['bis_only']:,} entities
- **Trade Monitoring Only**: {coverage['comtrade_only']:,} entities
- **Investment Tracking Only (SEC)**: {coverage['sec_only']:,} entities
- **Export Control + Trade**: {coverage['bis_comtrade']:,} entities
- **Export Control + Investment**: {coverage['bis_sec']:,} entities
- **Trade + Investment**: {coverage['comtrade_sec']:,} entities
- **ALL THREE SYSTEMS**: {coverage['all_three']:,} entities [CRITICAL PRIORITY]

### Intelligence Coverage Effectiveness
- **Single-System Detection**: {coverage['bis_only'] + coverage['comtrade_only'] + coverage['sec_only']:,} entities
- **Multi-System Validation**: {stats['multi_system_entities']:,} entities
- **Coverage Success Rate**: {coverage_percentage:.1f}% of entities detected in multiple systems

## RECENT INTELLIGENCE ACTIVITY (7 Days)

### Operational Intelligence Updates
- **New Entity Correlations**: {activity['recent_correlations']:,}
- **New Risk Alerts Generated**: {activity['recent_alerts']:,}
- **Watchlist Updates**: {activity['recent_watchlist']:,}
- **Last System Update**: {activity['last_correlation'] or activity['last_alert'] or 'No recent activity'}

## STRATEGIC INTELLIGENCE ASSESSMENT

### Chinese Technology Exploitation Threat Level: {"CRITICAL" if stats['critical_alerts'] > 0 else "HIGH" if stats['high_alerts'] > 5 else "ELEVATED"}

### Key Intelligence Findings
1. **Multi-System Entity Validation**: {stats['multi_system_entities']:,} entities confirmed across multiple intelligence sources
2. **Export Control Effectiveness**: {stats['bis_entities']:,} Chinese entities under active export restrictions
3. **Investment Infiltration**: {stats['chinese_investors']:,} Chinese investors identified in US markets
4. **Technology Trade Monitoring**: ${stats['total_trade_value']:.1f}B in tracked dual-use technology flows

### Critical Intelligence Gaps Identified
- **Single-System Entities**: {stats['total_correlations'] - stats['multi_system_entities']:,} entities require additional validation
- **Investment Blind Spots**: Potential Chinese investment activity not yet captured in SEC filings
- **Trade Flow Monitoring**: Need for real-time trade data integration
- **Entity Network Mapping**: Subsidiary and partnership relationships require deeper analysis

## RECOMMENDED EXECUTIVE ACTIONS

### Immediate (24-48 Hours)
1. **Review CRITICAL alerts**: {stats['critical_alerts']:,} entities requiring immediate investigation
2. **Validate HIGH priority entities**: {stats['high_alerts']:,} entities needing enhanced scrutiny
3. **Cross-reference triple-system entities** with classified intelligence databases

### Short-term (1-2 Weeks)
1. **Expand multi-system coverage**: Target {stats['total_correlations'] - stats['multi_system_entities']:,} single-system entities for validation
2. **Enhance investment monitoring**: Improve SEC filing analysis depth
3. **Technology focus analysis**: Deep-dive into top {len(tech_distribution)} technology categories

### Strategic (1-3 Months)
1. **Predictive modeling development**: Forecast entity progression between systems
2. **Network analysis implementation**: Map entity relationships and partnerships
3. **Real-time monitoring**: Implement automated alert systems for new entity appearances

---
*Executive Intelligence Brief - China Technology Exploitation Threat Assessment*
*Classification: Unclassified - OSINT Analysis*
*Next Update: Automated daily at 0600 hours*
"""

        # Save executive brief
        brief_path = Path("C:/Projects/OSINT - Foresight/analysis/EXECUTIVE_INTELLIGENCE_BRIEF.md")
        brief_path.write_text(report, encoding='utf-8')

        print(report)
        return report

    def run_dashboard_generation(self):
        """Execute complete dashboard generation"""
        logging.info("Generating consolidated intelligence dashboard")

        self.generate_executive_intelligence_brief()

        logging.info("Consolidated intelligence dashboard completed")

if __name__ == "__main__":
    dashboard = ConsolidatedIntelligenceDashboard()
    dashboard.run_dashboard_generation()
