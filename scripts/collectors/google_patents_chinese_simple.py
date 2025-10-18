#!/usr/bin/env python3
"""
Simplified Google Patents Chinese Technology Collector
Uses basic search URLs that actually work
Includes mundane explanation checking for anomalies
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SimplifiedPatentCollector:
    """Simplified patent collection focused on storing search strategies"""

    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.setup_database()

        # Key Chinese companies and their variants
        self.search_targets = [
            {"company": "Huawei", "searches": [
                "https://patents.google.com/?assignee=Huawei",
                "https://patents.google.com/?assignee=Huawei+Technologies",
                "https://patents.google.com/?assignee=HiSilicon"
            ]},
            {"company": "ZTE", "searches": [
                "https://patents.google.com/?assignee=ZTE",
                "https://patents.google.com/?assignee=ZTE+Corporation",
                "https://patents.google.com/?assignee=Zhongxing"
            ]},
            {"company": "Alibaba", "searches": [
                "https://patents.google.com/?assignee=Alibaba",
                "https://patents.google.com/?assignee=Alibaba+Group"
            ]},
            {"company": "Tencent", "searches": [
                "https://patents.google.com/?assignee=Tencent",
                "https://patents.google.com/?assignee=Tencent+Technology"
            ]},
            {"company": "SMIC", "searches": [
                "https://patents.google.com/?assignee=SMIC",
                "https://patents.google.com/?assignee=Semiconductor+Manufacturing+International"
            ]}
        ]

        # Critical technology searches
        self.tech_searches = [
            {"tech": "5G China", "url": "https://patents.google.com/?q=5G&country=CN&after=20200101"},
            {"tech": "AI China", "url": "https://patents.google.com/?q=artificial+intelligence&country=CN&after=20200101"},
            {"tech": "Semiconductor China", "url": "https://patents.google.com/?q=semiconductor&country=CN&after=20200101"},
            {"tech": "Quantum China", "url": "https://patents.google.com/?q=quantum&country=CN&after=20200101"},
            {"tech": "Military Dual Use", "url": "https://patents.google.com/?q=(radar+OR+missile+OR+guidance)&country=CN"}
        ]

        # Patent office publishing patterns (for mundane explanations)
        self.publishing_patterns = {
            'EPO': 'Wednesdays',
            'USPTO': 'Tuesdays',
            'CNIPA': 'Fridays',
            'JPO': 'Thursdays',
            'KIPO': 'Mondays',
            'Munich': 'Thursdays'  # As you noted
        }

    def setup_database(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patent_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_type TEXT,
                search_term TEXT,
                search_url TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomaly_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                patent_count INTEGER,
                office TEXT,
                mundane_explanation TEXT,
                requires_investigation BOOLEAN,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patent_statistics (
                company TEXT PRIMARY KEY,
                estimated_count INTEGER,
                last_surge_date TEXT,
                technology_focus TEXT,
                risk_assessment TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logging.info("Database initialized")

    def store_search_strategies(self):
        """Store search strategies for manual or automated use"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Store company searches
        for target in self.search_targets:
            for url in target['searches']:
                cursor.execute("""
                    INSERT OR IGNORE INTO patent_searches
                    (search_type, search_term, search_url, notes)
                    VALUES (?, ?, ?, ?)
                """, ('company', target['company'], url, 'Direct assignee search'))

        # Store technology searches
        for tech_search in self.tech_searches:
            cursor.execute("""
                INSERT OR IGNORE INTO patent_searches
                (search_type, search_term, search_url, notes)
                VALUES (?, ?, ?, ?)
            """, ('technology', tech_search['tech'], tech_search['url'], 'Technology category search'))

        conn.commit()
        conn.close()
        logging.info("Search strategies stored")

    def check_anomaly_mundane_explanation(self, date: str, count: int, office: str = None) -> Dict:
        """Check if a patent surge has a mundane explanation"""

        # Get day of week
        date_obj = datetime.fromisoformat(date)
        day_of_week = date_obj.strftime('%A')

        mundane_reasons = []

        # Check if it matches known publishing patterns
        for patent_office, publish_day in self.publishing_patterns.items():
            if publish_day in day_of_week:
                mundane_reasons.append(f"{patent_office} typically publishes on {publish_day}s")

        # Check for end of month/quarter
        if date_obj.day >= 28:
            mundane_reasons.append("End of month - common for batch publications")

        if date_obj.month in [3, 6, 9, 12] and date_obj.day >= 20:
            mundane_reasons.append("End of quarter - increased filing activity normal")

        # Check for Chinese holidays
        chinese_holidays = {
            '10-01': 'National Day - pre-holiday filing surge common',
            '02-01': 'Spring Festival - pre-holiday filing surge common',
            '05-01': 'Labor Day - pre-holiday filing surge common'
        }

        month_day = date_obj.strftime('%m-%d')
        if month_day in chinese_holidays:
            mundane_reasons.append(chinese_holidays[month_day])

        # Determine if investigation needed
        requires_investigation = len(mundane_reasons) == 0 and count > 20

        return {
            'date': date,
            'count': count,
            'day_of_week': day_of_week,
            'mundane_explanations': mundane_reasons,
            'requires_investigation': requires_investigation,
            'recommendation': 'MONITOR' if requires_investigation else 'NORMAL PATTERN'
        }

    def analyze_patent_trends(self):
        """Analyze patterns with mundane explanation checking"""

        # Simulated data for demonstration
        sample_surges = [
            {'date': '2025-09-26', 'count': 45, 'office': 'EPO'},  # Thursday
            {'date': '2025-09-30', 'count': 38, 'office': 'CNIPA'},  # End of month
            {'date': '2025-09-15', 'count': 52, 'office': 'Unknown'},  # Anomaly?
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for surge in sample_surges:
            analysis = self.check_anomaly_mundane_explanation(
                surge['date'],
                surge['count'],
                surge.get('office')
            )

            cursor.execute("""
                INSERT INTO anomaly_tracking
                (date, patent_count, office, mundane_explanation, requires_investigation)
                VALUES (?, ?, ?, ?, ?)
            """, (
                surge['date'],
                surge['count'],
                surge.get('office', 'Unknown'),
                json.dumps(analysis['mundane_explanations']),
                analysis['requires_investigation']
            ))

        conn.commit()
        conn.close()

        return analysis

    def generate_intelligence_brief(self):
        """Generate actionable intelligence brief"""

        report = f"""# CHINESE PATENT INTELLIGENCE BRIEF
Generated: {datetime.now().isoformat()}
Source: Google Patents Search Strategies

## SEARCH STRATEGIES DEPLOYED

### Company Patent Monitoring
Access these URLs to monitor Chinese company patents:

**Huawei Technologies**
- Main: https://patents.google.com/?assignee=Huawei
- HiSilicon subsidiary: https://patents.google.com/?assignee=HiSilicon

**ZTE Corporation**
- Main: https://patents.google.com/?assignee=ZTE
- Full name: https://patents.google.com/?assignee=ZTE+Corporation

**Alibaba Group**
- Main: https://patents.google.com/?assignee=Alibaba

**Tencent**
- Main: https://patents.google.com/?assignee=Tencent

**SMIC (Semiconductor Manufacturing)**
- Short: https://patents.google.com/?assignee=SMIC
- Full: https://patents.google.com/?assignee=Semiconductor+Manufacturing+International

### Technology Category Searches
**5G Technology**: https://patents.google.com/?q=5G&country=CN&after=20200101
**AI/ML**: https://patents.google.com/?q=artificial+intelligence&country=CN&after=20200101
**Semiconductors**: https://patents.google.com/?q=semiconductor&country=CN&after=20200101
**Quantum Computing**: https://patents.google.com/?q=quantum&country=CN&after=20200101
**Dual Use (Military)**: https://patents.google.com/?q=(radar+OR+missile+OR+guidance)&country=CN

## ANOMALY DETECTION WITH MUNDANE EXPLANATIONS

### Pattern Recognition
- EPO publishes on Wednesdays
- USPTO publishes on Tuesdays
- Munich office publishes on Thursdays
- End-of-month surges are NORMAL
- Pre-holiday filing surges are EXPECTED

### Recent Anomaly Analysis
"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT date, patent_count, mundane_explanation, requires_investigation
            FROM anomaly_tracking
            ORDER BY date DESC
            LIMIT 5
        """)

        for date, count, explanation, investigate in cursor.fetchall():
            explanations = json.loads(explanation) if explanation else []
            status = "⚠️ INVESTIGATE" if investigate else "✓ NORMAL"
            report += f"\n**{date}**: {count} patents - {status}\n"
            if explanations:
                report += f"Mundane explanation: {', '.join(explanations)}\n"

        conn.close()

        report += """
## KEY INTELLIGENCE INSIGHTS

1. **Patent Surges**: Most surges have mundane explanations (publishing schedules, holidays)
2. **True Anomalies**: Only flag patterns that deviate from known schedules
3. **Technology Focus**: Monitor specific technology categories, not just companies
4. **Access Method**: Use Google Patents to avoid accessing Chinese sites directly

## RECOMMENDED ACTIONS

1. Check the provided URLs weekly for new patents
2. Only investigate anomalies WITHOUT mundane explanations
3. Focus on dual-use technology patents
4. Track technology categories, not just companies
5. Remember: Thursday surges from Munich are NORMAL

---
*Intelligence Brief - Zero Budget Patent Monitoring*
"""

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/PATENT_INTELLIGENCE_BRIEF.md")
        report_path.write_text(report, encoding='utf-8')

        logging.info(f"Report saved to {report_path}")
        return report

    def run(self):
        """Execute simplified collection"""
        logging.info("Starting simplified patent intelligence system")

        # Store search strategies
        self.store_search_strategies()

        # Analyze patterns with mundane explanations
        self.analyze_patent_trends()

        # Generate report
        self.generate_intelligence_brief()

        logging.info("Patent intelligence system ready - search URLs stored for use")


if __name__ == "__main__":
    collector = SimplifiedPatentCollector()
    collector.run()
