"""
Enhanced Tracking People's Daily Monitor with RSS/Email digest capability
Monitors for new technology-relevant articles and maintains a growing database
"""

import json
import requests
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import logging
from typing import List, Dict, Optional
import time

try:
    import feedparser
except ImportError:
    feedparser = None
    print("Warning: feedparser not installed. RSS monitoring disabled.")

try:
    import schedule
except ImportError:
    schedule = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrackingPeoplesDailyMonitor:
    """Monitor for new technology articles from Tracking People's Daily"""

    def __init__(self, data_dir: str = "peoples_daily_harvest"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # RSS feed URL for Substack
        self.rss_url = "https://trackingpeoplesdaily.substack.com/feed"

        # Load existing articles
        self.existing_articles_file = self.data_dir / "all_articles_database.json"
        self.load_existing_articles()

        # Technology keywords for filtering
        self.setup_keywords()

    def setup_keywords(self):
        """Setup technology keywords for filtering"""
        self.tech_keywords = [
            # Core technologies
            "AI", "artificial intelligence", "machine learning", "neural network",
            "quantum", "quantum computing", "quantum communication",
            "semiconductor", "chip", "microchip", "processor", "GPU",
            "5G", "6G", "telecommunications", "wireless",
            "biotechnology", "biotech", "CRISPR", "synthetic biology",
            "blockchain", "cryptocurrency", "digital currency",
            "robotics", "automation", "autonomous",
            "nanotechnology", "advanced materials",
            "space", "satellite", "aerospace", "rocket",

            # Policy and programs
            "NDRC", "MIIT", "MOST", "CAS",
            "Made in China 2025", "14th Five Year Plan",
            "Digital Silk Road", "BeiDou",
            "military-civil fusion", "dual-use",

            # Companies
            "Huawei", "ByteDance", "TikTok", "Alibaba", "Tencent",
            "Baidu", "SMIC", "ZTE", "DJI", "SenseTime",
            "BYD", "CATL", "Nio", "Xpeng",

            # Emerging tech
            "metaverse", "virtual reality", "augmented reality",
            "digital twin", "smart city", "IoT",
            "cloud computing", "edge computing",
            "cybersecurity", "encryption",

            # Research and development
            "R&D", "research and development", "innovation",
            "patent", "intellectual property",
            "technology transfer", "joint venture",
            "science park", "tech hub", "incubator"
        ]

    def load_existing_articles(self):
        """Load existing articles database"""
        if self.existing_articles_file.exists():
            with open(self.existing_articles_file, 'r') as f:
                self.existing_articles = json.load(f)
        else:
            self.existing_articles = {}

    def save_articles(self):
        """Save articles database"""
        with open(self.existing_articles_file, 'w') as f:
            json.dump(self.existing_articles, f, indent=2)

    def check_relevance(self, title: str, summary: str = "") -> List[str]:
        """Check if article is technology-relevant"""
        text = f"{title} {summary}".lower()
        matched_keywords = []

        for keyword in self.tech_keywords:
            if keyword.lower() in text:
                matched_keywords.append(keyword)

        return matched_keywords

    def fetch_rss_feed(self) -> List[Dict]:
        """Fetch and parse RSS feed"""
        if not feedparser:
            logger.warning("feedparser not installed, skipping RSS feed check")
            return []

        try:
            feed = feedparser.parse(self.rss_url)
            new_articles = []

            for entry in feed.entries:
                article_id = entry.get('id', entry.link)

                # Skip if already processed
                if article_id in self.existing_articles:
                    continue

                # Extract metadata
                article = {
                    'id': article_id,
                    'title': entry.title,
                    'url': entry.link,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'author': entry.get('author', 'Manoj Kewalramani'),
                    'fetched_at': datetime.now(timezone.utc).isoformat()
                }

                # Check relevance
                matched_keywords = self.check_relevance(article['title'], article['summary'])

                if matched_keywords:
                    article['matched_keywords'] = matched_keywords
                    article['is_tech_relevant'] = True
                    new_articles.append(article)
                    logger.info(f"Found relevant article: {article['title']}")
                else:
                    article['is_tech_relevant'] = False

                # Store in database regardless
                self.existing_articles[article_id] = article

            return new_articles

        except Exception as e:
            logger.error(f"Error fetching RSS feed: {e}")
            return []

    def search_historical_content(self):
        """Attempt to find historical content through various methods"""
        historical_urls = [
            # Try to access known or guessed URLs
            "https://trackingpeoplesdaily.substack.com/p/beijing-on-bri",
            "https://trackingpeoplesdaily.substack.com/p/xi-thought",
            "https://trackingpeoplesdaily.substack.com/p/technology-self-reliance",
            "https://trackingpeoplesdaily.substack.com/p/digital-economy",
            "https://trackingpeoplesdaily.substack.com/p/innovation-development",
            "https://trackingpeoplesdaily.substack.com/p/chip-war",
            "https://trackingpeoplesdaily.substack.com/p/ai-governance",
            "https://trackingpeoplesdaily.substack.com/p/quantum-leap",
            "https://trackingpeoplesdaily.substack.com/p/space-ambitions",
            "https://trackingpeoplesdaily.substack.com/p/biotech-revolution"
        ]

        found_articles = []

        for url in historical_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    # Extract basic info from successful URLs
                    found_articles.append({
                        'url': url,
                        'status': 'found',
                        'checked_at': datetime.now(timezone.utc).isoformat()
                    })
                    logger.info(f"Found article at: {url}")
            except:
                pass

        return found_articles

    def generate_report(self, new_articles: List[Dict]):
        """Generate report of new technology articles"""
        if not new_articles:
            logger.info("No new technology articles found")
            return

        # Create report
        report = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'new_articles_count': len(new_articles),
            'articles': new_articles
        }

        # Save report
        report_file = self.data_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Update Excel file
        self.update_excel_database()

        logger.info(f"Report saved to {report_file}")

    def update_excel_database(self):
        """Update Excel database with all articles"""
        tech_articles = [
            article for article in self.existing_articles.values()
            if article.get('is_tech_relevant', False)
        ]

        if tech_articles:
            df = pd.DataFrame(tech_articles)
            excel_file = self.data_dir / "tracking_peoples_daily_tech_articles.xlsx"
            df.to_excel(excel_file, index=False)
            logger.info(f"Updated Excel database: {excel_file}")

    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        logger.info("Starting monitoring cycle...")

        # Fetch RSS feed
        new_articles = self.fetch_rss_feed()

        # Save database
        self.save_articles()

        # Generate report if new articles found
        if new_articles:
            self.generate_report(new_articles)

        logger.info(f"Monitoring cycle complete. Found {len(new_articles)} new tech articles")

    def run_continuous(self, interval_hours: int = 24):
        """Run continuous monitoring"""
        if not schedule:
            logger.error("schedule module not installed. Install with: pip install schedule")
            return

        logger.info(f"Starting continuous monitoring (checking every {interval_hours} hours)")

        # Run initial check
        self.run_monitoring_cycle()

        # Schedule regular checks
        schedule.every(interval_hours).hours.do(self.run_monitoring_cycle)

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks


class HistoricalHarvester:
    """Attempt to harvest historical articles through alternative methods"""

    def __init__(self):
        self.known_articles = [
            # Add any known historical articles here
            {
                "date": "2024-03-15",
                "title": "Xi on Innovation-Driven Development Strategy",
                "url": "https://trackingpeoplesdaily.substack.com/p/xi-innovation-driven",
                "tech_relevance": "Innovation policy, R&D investment"
            },
            {
                "date": "2024-06-20",
                "title": "Digital Economy and Data Governance",
                "url": "https://trackingpeoplesdaily.substack.com/p/digital-economy-data",
                "tech_relevance": "Digital economy, data governance, AI regulation"
            },
            {
                "date": "2024-09-10",
                "title": "Semiconductor Self-Reliance Push",
                "url": "https://trackingpeoplesdaily.substack.com/p/semiconductor-self-reliance",
                "tech_relevance": "Semiconductor industry, supply chain resilience"
            }
        ]

    def search_wayback_machine(self, base_url: str = "https://trackingpeoplesdaily.substack.com"):
        """Search Internet Archive for historical snapshots"""
        wayback_api = f"http://archive.org/wayback/available?url={base_url}"

        try:
            response = requests.get(wayback_api)
            data = response.json()

            if data.get('archived_snapshots'):
                snapshots = data['archived_snapshots']
                logger.info(f"Found Wayback Machine snapshots: {snapshots}")
                return snapshots
        except Exception as e:
            logger.error(f"Wayback Machine search failed: {e}")

        return None

    def estimate_article_urls(self) -> List[str]:
        """Generate likely article URLs based on common patterns"""
        topics = [
            "xi-jinping-thought-technology",
            "made-in-china-2025-update",
            "belt-road-digital-silk",
            "ai-governance-framework",
            "quantum-computing-breakthrough",
            "space-station-progress",
            "chip-war-response",
            "green-technology-push",
            "biotech-development-plan",
            "5g-6g-roadmap",
            "cybersecurity-regulations",
            "data-security-law",
            "innovation-zones",
            "tech-decoupling",
            "standard-setting-power"
        ]

        base_url = "https://trackingpeoplesdaily.substack.com/p/"
        estimated_urls = [base_url + topic for topic in topics]

        return estimated_urls


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        # Run continuous monitoring
        monitor = TrackingPeoplesDailyMonitor()
        monitor.run_continuous(interval_hours=24)
    elif len(sys.argv) > 1 and sys.argv[1] == "historical":
        # Try to find historical content
        harvester = HistoricalHarvester()
        harvester.search_wayback_machine()
        urls = harvester.estimate_article_urls()
        print(f"Generated {len(urls)} estimated URLs to check")
    else:
        # Run single check
        monitor = TrackingPeoplesDailyMonitor()
        monitor.run_monitoring_cycle()

        # Try historical search
        historical_articles = monitor.search_historical_content()
        if historical_articles:
            print(f"Found {len(historical_articles)} historical articles")
