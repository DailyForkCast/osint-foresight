#!/usr/bin/env python3
"""
Automated RSS Feed Monitor for China Technology Intelligence
Monitors think tanks and tech news sources for China-related content
"""

import feedparser
import sqlite3
import requests
from pathlib import Path
from datetime import datetime, timedelta
import json
import time
import hashlib
from urllib.parse import urljoin

class AutomatedRSSMonitor:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/rss_monitoring")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # RSS feed sources
        self.feeds = {
            'think_tanks': {
                'CSIS': 'https://www.csis.org/rss.xml',
                'Brookings': 'https://www.brookings.edu/feed/',
                'Council on Foreign Relations': 'https://www.cfr.org/rss.xml',
                'Atlantic Council': 'https://www.atlanticcouncil.org/feed/',
                'Carnegie Endowment': 'https://carnegieendowment.org/rss/',
                'RAND Corporation': 'https://www.rand.org/rss.xml',
                'Heritage Foundation': 'https://www.heritage.org/rss.xml',
                'Center for Strategic Studies': 'https://www.csis.org/programs/china-power-project/rss.xml'
            },
            'tech_news': {
                'TechCrunch': 'https://techcrunch.com/feed/',
                'Wired': 'https://www.wired.com/feed/',
                'MIT Technology Review': 'https://www.technologyreview.com/rss/',
                'IEEE Spectrum': 'https://spectrum.ieee.org/rss',
                'Ars Technica': 'https://feeds.arstechnica.com/arstechnica/index',
                'The Verge': 'https://www.theverge.com/rss/index.xml'
            },
            'security': {
                'Defense News': 'https://www.defensenews.com/rss/',
                'Breaking Defense': 'https://breakingdefense.com/feed/',
                'War on the Rocks': 'https://warontherocks.com/feed/',
                'Small Wars Journal': 'https://smallwarsjournal.com/rss.xml'
            }
        }

        # China-related keywords
        self.china_keywords = [
            'china', 'chinese', 'beijing', 'prc', 'huawei', 'tencent', 'alibaba',
            'military-civil fusion', 'mcf', 'belt and road', 'bri', 'xinjiang',
            'taiwan', 'hong kong', 'south china sea', 'quantum computing',
            'artificial intelligence', 'semiconductors', 'rare earth',
            'technology transfer', 'dual-use', 'hypersonic', '5g', 'tiktok'
        ]

        self.init_database()

    def init_database(self):
        """Initialize SQLite database for RSS monitoring"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Create tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rss_feeds (
                feed_id TEXT PRIMARY KEY,
                feed_name TEXT,
                feed_url TEXT,
                category TEXT,
                last_checked DATETIME,
                total_items INTEGER DEFAULT 0,
                china_items INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS rss_items (
                item_id TEXT PRIMARY KEY,
                feed_id TEXT,
                title TEXT,
                description TEXT,
                link TEXT,
                pub_date DATETIME,
                content TEXT,
                china_relevance_score INTEGER,
                keywords_matched TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES rss_feeds (feed_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS china_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT,
                alert_level TEXT,
                alert_reason TEXT,
                keywords TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES rss_items (item_id)
            )
        """)

        conn.commit()
        conn.close()

    def calculate_china_relevance(self, text):
        """Calculate relevance score for China-related content"""
        if not text:
            return 0, []

        text_lower = text.lower()
        matched_keywords = []
        score = 0

        for keyword in self.china_keywords:
            if keyword in text_lower:
                matched_keywords.append(keyword)
                # Higher scores for specific keywords
                if keyword in ['military-civil fusion', 'mcf', 'technology transfer', 'dual-use']:
                    score += 10
                elif keyword in ['quantum computing', 'artificial intelligence', 'semiconductors']:
                    score += 8
                elif keyword in ['huawei', 'tencent', 'alibaba', 'tiktok']:
                    score += 6
                else:
                    score += 3

        return score, matched_keywords

    def fetch_feed(self, feed_name, feed_url, category):
        """Fetch and process RSS feed"""
        print(f"Fetching {feed_name}...")

        try:
            # Set user agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            # Use requests with headers, then parse with feedparser
            response = requests.get(feed_url, headers=headers, timeout=30)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if not feed.entries:
                print(f"No entries found for {feed_name}")
                return 0, 0

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            # Update feed record
            feed_id = hashlib.md5(feed_url.encode()).hexdigest()
            cur.execute("""
                INSERT OR REPLACE INTO rss_feeds
                (feed_id, feed_name, feed_url, category, last_checked, total_items)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (feed_id, feed_name, feed_url, category, datetime.now(), len(feed.entries)))

            china_items = 0
            new_items = 0

            for entry in feed.entries:
                # Create unique item ID
                item_content = f"{entry.title}{entry.link}"
                item_id = hashlib.md5(item_content.encode()).hexdigest()

                # Check if item already exists
                cur.execute("SELECT item_id FROM rss_items WHERE item_id = ?", (item_id,))
                if cur.fetchone():
                    continue

                # Combine title and description for analysis
                full_text = f"{entry.title} {getattr(entry, 'description', '')} {getattr(entry, 'summary', '')}"

                # Calculate China relevance
                relevance_score, matched_keywords = self.calculate_china_relevance(full_text)

                # Parse publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])

                # Insert item
                cur.execute("""
                    INSERT INTO rss_items
                    (item_id, feed_id, title, description, link, pub_date,
                     china_relevance_score, keywords_matched)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_id, feed_id, entry.title,
                    getattr(entry, 'description', ''),
                    entry.link, pub_date, relevance_score,
                    ','.join(matched_keywords)
                ))

                new_items += 1

                # Create alert for high relevance items
                if relevance_score >= 15:
                    alert_level = 'HIGH' if relevance_score >= 25 else 'MEDIUM'
                    cur.execute("""
                        INSERT INTO china_alerts
                        (item_id, alert_level, alert_reason, keywords)
                        VALUES (?, ?, ?, ?)
                    """, (
                        item_id, alert_level,
                        f"High China relevance score: {relevance_score}",
                        ','.join(matched_keywords)
                    ))

                if relevance_score > 0:
                    china_items += 1

            # Update china_items count
            cur.execute("""
                UPDATE rss_feeds SET china_items = ? WHERE feed_id = ?
            """, (china_items, feed_id))

            conn.commit()
            conn.close()

            print(f"  {feed_name}: {new_items} new items, {china_items} China-related")
            return new_items, china_items

        except Exception as e:
            print(f"Error fetching {feed_name}: {str(e)}")
            return 0, 0

    def monitor_all_feeds(self):
        """Monitor all RSS feeds"""
        print("Starting RSS monitoring sweep...")

        total_new = 0
        total_china = 0

        for category, feeds in self.feeds.items():
            print(f"\nProcessing {category.upper()} feeds:")

            for feed_name, feed_url in feeds.items():
                new_items, china_items = self.fetch_feed(feed_name, feed_url, category)
                total_new += new_items
                total_china += china_items

                # Small delay to be respectful
                time.sleep(2)

        print(f"\nMonitoring complete: {total_new} new items, {total_china} China-related")

        # Generate alerts summary
        self.generate_alerts_summary()

        return total_new, total_china

    def generate_alerts_summary(self):
        """Generate summary of recent alerts"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Get recent high-priority alerts
        cur.execute("""
            SELECT a.alert_level, r.title, r.link, r.china_relevance_score,
                   r.keywords_matched, f.feed_name, a.created_at
            FROM china_alerts a
            JOIN rss_items r ON a.item_id = r.item_id
            JOIN rss_feeds f ON r.feed_id = f.feed_id
            WHERE a.created_at >= datetime('now', '-24 hours')
            ORDER BY r.china_relevance_score DESC, a.created_at DESC
        """)

        alerts = cur.fetchall()

        if alerts:
            alert_summary = f"""# RSS Intelligence Alerts
Generated: {datetime.now().isoformat()}

## High-Priority China Intelligence ({len(alerts)} alerts)

"""
            for alert in alerts:
                alert_level, title, link, score, keywords, feed_name, created_at = alert
                alert_summary += f"""### {alert_level} ALERT - Score: {score}
**Source**: {feed_name}
**Title**: {title}
**Keywords**: {keywords}
**Link**: {link}
**Detected**: {created_at}

---

"""

            # Save alert summary
            alert_file = self.output_dir / f"rss_alerts_{datetime.now().strftime('%Y%m%d')}.md"
            alert_file.write_text(alert_summary, encoding='utf-8')
            print(f"Alert summary saved: {alert_file}")

        # Generate daily statistics
        cur.execute("""
            SELECT f.category, COUNT(r.item_id) as total_items,
                   SUM(CASE WHEN r.china_relevance_score > 0 THEN 1 ELSE 0 END) as china_items,
                   AVG(r.china_relevance_score) as avg_score
            FROM rss_feeds f
            LEFT JOIN rss_items r ON f.feed_id = r.feed_id
            WHERE r.created_at >= datetime('now', '-24 hours')
            GROUP BY f.category
        """)

        stats = cur.fetchall()

        stats_summary = f"""# RSS Monitoring Statistics
Generated: {datetime.now().isoformat()}

## 24-Hour Summary by Category

"""
        for category, total, china, avg_score in stats:
            percentage = (china / total * 100) if total > 0 else 0
            stats_summary += f"""### {category.upper()}
- Total Items: {total}
- China-Related: {china} ({percentage:.1f}%)
- Average Relevance Score: {avg_score:.1f}

"""

        stats_file = self.output_dir / f"rss_stats_{datetime.now().strftime('%Y%m%d')}.md"
        stats_file.write_text(stats_summary, encoding='utf-8')

        conn.close()

    def get_top_stories(self, hours=24, min_score=10):
        """Get top China-related stories from last N hours"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT r.title, r.link, r.china_relevance_score, r.keywords_matched,
                   f.feed_name, r.pub_date
            FROM rss_items r
            JOIN rss_feeds f ON r.feed_id = f.feed_id
            WHERE r.china_relevance_score >= ?
              AND r.created_at >= datetime('now', '-{} hours')
            ORDER BY r.china_relevance_score DESC
            LIMIT 20
        """.format(hours), (min_score,))

        stories = cur.fetchall()
        conn.close()

        return stories

def main():
    monitor = AutomatedRSSMonitor()

    # Run monitoring sweep
    new_items, china_items = monitor.monitor_all_feeds()

    # Get top stories
    top_stories = monitor.get_top_stories()

    print(f"\nTop China Stories (last 24 hours):")
    for i, story in enumerate(top_stories[:10], 1):
        title, link, score, keywords, source, pub_date = story
        print(f"{i}. [{score}] {title[:80]}...")
        print(f"   Source: {source} | Keywords: {keywords}")

    print(f"\nRSS monitoring complete. Check output directory for detailed reports.")

if __name__ == "__main__":
    main()
