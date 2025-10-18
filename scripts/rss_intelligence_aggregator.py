#!/usr/bin/env python3
"""
RSS Intelligence Feed Aggregator
Zero-budget real-time intelligence monitoring system
Aggregates China tech intelligence from free RSS feeds
"""

import feedparser
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re
import time
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RSSIntelligenceAggregator:
    """Aggregate China technology intelligence from RSS feeds"""

    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.setup_database()

        # Critical RSS feeds for China tech monitoring
        self.feeds = {
            # Government Sources
            'bis_updates': {
                'url': 'https://www.bis.doc.gov/rss/press_release.xml',
                'category': 'export_control',
                'priority': 'HIGH'
            },
            'treasury_sanctions': {
                'url': 'https://home.treasury.gov/rss/feeds.xml',
                'category': 'sanctions',
                'priority': 'HIGH'
            },
            'fcc_china': {
                'url': 'https://www.fcc.gov/rss',
                'category': 'telecommunications',
                'priority': 'MEDIUM'
            },

            # Think Tanks - China Focus
            'csis_china': {
                'url': 'https://www.csis.org/programs/china-power-project/feed',
                'category': 'analysis',
                'priority': 'HIGH'
            },
            'brookings_china': {
                'url': 'https://www.brookings.edu/topic/china/feed/',
                'category': 'analysis',
                'priority': 'MEDIUM'
            },
            'cfr_china': {
                'url': 'https://www.cfr.org/rss/china/rss.xml',
                'category': 'analysis',
                'priority': 'MEDIUM'
            },
            'rand_china': {
                'url': 'https://www.rand.org/topics/china.xml',
                'category': 'research',
                'priority': 'MEDIUM'
            },
            'heritage_china': {
                'url': 'https://www.heritage.org/rss.xml',
                'category': 'analysis',
                'priority': 'LOW'
            },

            # Technology News
            'techcrunch': {
                'url': 'https://techcrunch.com/feed/',
                'category': 'tech_news',
                'priority': 'LOW'
            },
            'wired_security': {
                'url': 'https://www.wired.com/feed/category/security/latest/rss',
                'category': 'cybersecurity',
                'priority': 'MEDIUM'
            },
            'mit_tech': {
                'url': 'https://www.technologyreview.com/feed/',
                'category': 'tech_research',
                'priority': 'MEDIUM'
            },

            # Patent & Research
            'uspto_patents': {
                'url': 'https://www.uspto.gov/rss/patents.xml',
                'category': 'patents',
                'priority': 'MEDIUM'
            },
            'nature_china': {
                'url': 'https://www.nature.com/natelectron.rss',
                'category': 'research',
                'priority': 'LOW'
            },

            # Financial/Investment
            'sec_filings': {
                'url': 'https://www.sec.gov/rss/litigation/litreleases.xml',
                'category': 'investment',
                'priority': 'MEDIUM'
            },

            # Defense & Security
            'defense_news': {
                'url': 'https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml',
                'category': 'defense',
                'priority': 'MEDIUM'
            },
            'c4isrnet': {
                'url': 'https://www.c4isrnet.com/arc/outboundfeeds/rss/?outputType=xml',
                'category': 'defense_tech',
                'priority': 'MEDIUM'
            }
        }

        # China-related keywords for filtering
        self.china_keywords = [
            'china', 'chinese', 'beijing', 'huawei', 'zte', 'alibaba',
            'tencent', 'baidu', 'xiaomi', 'bytedance', 'tiktok',
            'pla', "people's liberation army", 'xi jinping', 'ccp',
            'belt and road', 'made in china 2025', 'dual use',
            'export control', 'entity list', 'sanctions', 'cfius',
            'taiwan', 'south china sea', 'xinjiang', 'hong kong'
        ]

        # Technology keywords
        self.tech_keywords = [
            'artificial intelligence', 'ai', 'machine learning',
            '5g', '6g', 'semiconductor', 'chip', 'quantum',
            'hypersonic', 'missile', 'satellite', 'space',
            'cyber', 'hack', 'surveillance', 'facial recognition',
            'drone', 'uav', 'autonomous', 'robot',
            'biotech', 'gene', 'crispr', 'virus',
            'nuclear', 'submarine', 'aircraft carrier'
        ]

    def setup_database(self):
        """Initialize database for storing intelligence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rss_items (
                item_id TEXT PRIMARY KEY,
                source TEXT,
                category TEXT,
                priority TEXT,
                title TEXT,
                summary TEXT,
                link TEXT,
                published_date TEXT,
                china_relevance INTEGER,
                tech_relevance INTEGER,
                risk_score INTEGER,
                entities_mentioned TEXT,
                technologies TEXT,
                collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                priority TEXT,
                title TEXT,
                summary TEXT,
                source_items TEXT,
                risk_assessment TEXT,
                recommended_action TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                reviewed INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feed_status (
                feed_name TEXT PRIMARY KEY,
                last_checked DATETIME,
                last_success DATETIME,
                item_count INTEGER,
                error_count INTEGER,
                status TEXT
            )
        """)

        conn.commit()
        conn.close()
        logging.info("RSS intelligence database initialized")

    def generate_item_id(self, item: Dict) -> str:
        """Generate unique ID for RSS item"""
        unique_str = f"{item.get('link', '')}{item.get('title', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def calculate_relevance(self, text: str) -> tuple:
        """Calculate China and tech relevance scores"""
        text_lower = text.lower()

        # China relevance
        china_score = sum(10 for keyword in self.china_keywords if keyword in text_lower)
        china_score = min(china_score, 100)

        # Tech relevance
        tech_score = sum(8 for keyword in self.tech_keywords if keyword in text_lower)
        tech_score = min(tech_score, 100)

        return china_score, tech_score

    def extract_entities(self, text: str) -> List[str]:
        """Extract entity names from text"""
        entities = []

        # Company names
        companies = [
            'Huawei', 'ZTE', 'Alibaba', 'Tencent', 'Baidu',
            'ByteDance', 'TikTok', 'Xiaomi', 'SMIC', 'DJI'
        ]

        for company in companies:
            if company.lower() in text.lower():
                entities.append(company)

        return entities

    def process_feed(self, feed_name: str, feed_info: Dict) -> int:
        """Process a single RSS feed"""
        try:
            logging.info(f"Processing feed: {feed_name}")

            # Parse feed
            feed = feedparser.parse(feed_info['url'])

            if feed.bozo:
                logging.warning(f"Feed parsing issue for {feed_name}: {feed.bozo_exception}")

            items_processed = 0
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for entry in feed.entries:
                # Generate unique ID
                item_id = self.generate_item_id(entry)

                # Check if already processed
                cursor.execute("SELECT 1 FROM rss_items WHERE item_id = ?", (item_id,))
                if cursor.fetchone():
                    continue

                # Extract text for analysis
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                combined_text = f"{title} {summary}"

                # Calculate relevance scores
                china_score, tech_score = self.calculate_relevance(combined_text)

                # Only store if relevant
                if china_score > 0 or tech_score > 20:
                    # Extract entities
                    entities = self.extract_entities(combined_text)

                    # Calculate risk score
                    risk_score = self.calculate_risk_score(
                        china_score, tech_score, feed_info['priority']
                    )

                    # Store in database
                    cursor.execute("""
                        INSERT INTO rss_items (
                            item_id, source, category, priority,
                            title, summary, link, published_date,
                            china_relevance, tech_relevance, risk_score,
                            entities_mentioned, technologies
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item_id, feed_name, feed_info['category'],
                        feed_info['priority'], title, summary,
                        entry.get('link', ''),
                        entry.get('published', datetime.now().isoformat()),
                        china_score, tech_score, risk_score,
                        json.dumps(entities), ''
                    ))

                    items_processed += 1

                    # Check for alerts
                    if risk_score >= 70:
                        self.create_alert(entry, china_score, tech_score, risk_score)

            # Update feed status
            cursor.execute("""
                INSERT OR REPLACE INTO feed_status (
                    feed_name, last_checked, last_success, item_count, status
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                feed_name, datetime.now(), datetime.now(),
                items_processed, 'SUCCESS'
            ))

            conn.commit()
            conn.close()

            logging.info(f"Processed {items_processed} relevant items from {feed_name}")
            return items_processed

        except Exception as e:
            logging.error(f"Error processing {feed_name}: {e}")
            return 0

    def calculate_risk_score(self, china_score: int, tech_score: int, priority: str) -> int:
        """Calculate overall risk score"""
        base_score = (china_score + tech_score) / 2

        # Adjust by source priority
        if priority == 'HIGH':
            base_score *= 1.5
        elif priority == 'MEDIUM':
            base_score *= 1.2

        return min(int(base_score), 100)

    def create_alert(self, item: Dict, china_score: int, tech_score: int, risk_score: int):
        """Create intelligence alert for high-risk items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        alert_type = 'CRITICAL' if risk_score >= 85 else 'HIGH'

        cursor.execute("""
            INSERT INTO intelligence_alerts (
                alert_type, priority, title, summary,
                risk_assessment, recommended_action
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            alert_type, 'HIGH',
            item.get('title', 'Unknown'),
            item.get('summary', '')[:500],
            f"Risk Score: {risk_score}/100 (China: {china_score}, Tech: {tech_score})",
            "Review immediately for strategic implications"
        ))

        conn.commit()
        conn.close()

    def process_all_feeds(self):
        """Process all configured RSS feeds"""
        total_items = 0

        for feed_name, feed_info in self.feeds.items():
            items = self.process_feed(feed_name, feed_info)
            total_items += items
            time.sleep(2)  # Polite delay between feeds

        logging.info(f"Total items processed: {total_items}")
        return total_items

    def generate_daily_intelligence_brief(self):
        """Generate daily intelligence summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get today's high-risk items
        cursor.execute("""
            SELECT source, title, summary, risk_score, china_relevance, tech_relevance
            FROM rss_items
            WHERE risk_score >= 60
            AND DATE(collected_at) = DATE('now')
            ORDER BY risk_score DESC
            LIMIT 20
        """)

        high_risk_items = cursor.fetchall()

        # Get alerts
        cursor.execute("""
            SELECT alert_type, title, risk_assessment
            FROM intelligence_alerts
            WHERE DATE(created_at) = DATE('now')
            AND reviewed = 0
            ORDER BY created_at DESC
        """)

        alerts = cursor.fetchall()

        # Get statistics
        cursor.execute("""
            SELECT COUNT(*) FROM rss_items
            WHERE DATE(collected_at) = DATE('now')
        """)
        total_today = cursor.fetchone()[0]

        conn.close()

        # Generate brief
        brief = f"""# DAILY INTELLIGENCE BRIEF - CHINA TECHNOLOGY RISKS
Generated: {datetime.now().isoformat()}
Source: RSS Intelligence Aggregation Network

## EXECUTIVE SUMMARY

### Collection Statistics
- Items Processed Today: {total_today}
- High Risk Items: {len(high_risk_items)}
- Active Alerts: {len(alerts)}

## CRITICAL ALERTS
"""
        for alert_type, title, assessment in alerts[:5]:
            brief += f"\n### [{alert_type}] {title}\n{assessment}\n"

        brief += "\n## HIGH RISK INTELLIGENCE\n"

        for source, title, summary, risk, china, tech in high_risk_items[:10]:
            brief += f"""
### {title}
- **Source**: {source}
- **Risk Score**: {risk}/100 (China: {china}, Tech: {tech})
- **Summary**: {summary[:200]}...
"""

        brief += """
## COLLECTION SOURCES

Active RSS feeds monitored:
- Government: BIS, Treasury, FCC
- Think Tanks: CSIS, Brookings, RAND, CFR
- Technology: MIT Tech Review, Wired
- Defense: Defense News, C4ISRnet

## NEXT STEPS

1. Review all CRITICAL alerts immediately
2. Investigate high-risk items for strategic implications
3. Cross-reference with other intelligence systems
4. Update entity watchlist based on new mentions

---
*Daily Intelligence Brief - Automated RSS Aggregation*
"""

        # Save brief
        brief_path = Path("C:/Projects/OSINT - Foresight/analysis/DAILY_RSS_INTELLIGENCE_BRIEF.md")
        brief_path.write_text(brief, encoding='utf-8')

        logging.info("Daily intelligence brief generated")
        return brief

    def run_continuous_monitoring(self):
        """Run continuous monitoring (can be scheduled)"""
        while True:
            logging.info("Starting RSS intelligence sweep")

            # Process all feeds
            self.process_all_feeds()

            # Generate brief every 6 hours
            if datetime.now().hour in [6, 12, 18, 0]:
                self.generate_daily_intelligence_brief()

            # Wait 1 hour before next sweep
            logging.info("Waiting 1 hour until next sweep...")
            time.sleep(3600)


if __name__ == "__main__":
    aggregator = RSSIntelligenceAggregator()

    # For testing, just run once
    aggregator.process_all_feeds()
    aggregator.generate_daily_intelligence_brief()

    # For production, uncomment to run continuously:
    # aggregator.run_continuous_monitoring()
