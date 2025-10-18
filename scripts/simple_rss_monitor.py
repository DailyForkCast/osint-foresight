#!/usr/bin/env python3
"""
Simple RSS Monitor for China Technology Intelligence
Basic working version with verified RSS feeds
"""

import feedparser
import requests
from pathlib import Path
from datetime import datetime
import json
import time

class SimpleRSSMonitor:
    def __init__(self):
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/rss_monitoring")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Verified RSS feeds
        self.feeds = {
            'TechCrunch': 'https://feeds.feedburner.com/TechCrunch',
            'MIT Technology Review': 'https://feeds.technologyreview.com/technology-review-latest/',
            'The Verge': 'https://www.theverge.com/rss/index.xml',
            'Ars Technica': 'https://feeds.arstechnica.com/arstechnica/index/',
            'Brookings Tech Stream': 'https://www.brookings.edu/wp-json/wp/v2/posts?categories=8',
            'CSIS': 'https://csis.org/rss-csis-all.xml'
        }

        # China keywords
        self.china_keywords = [
            'china', 'chinese', 'beijing', 'prc', 'huawei', 'tencent', 'alibaba',
            'military-civil fusion', 'mcf', 'belt and road', 'quantum computing',
            'semiconductors', 'technology transfer', 'dual-use', 'taiwan'
        ]

    def check_china_relevance(self, text):
        """Check if content is China-related"""
        if not text:
            return False, []

        text_lower = text.lower()
        matched_keywords = []

        for keyword in self.china_keywords:
            if keyword in text_lower:
                matched_keywords.append(keyword)

        return len(matched_keywords) > 0, matched_keywords

    def fetch_feed(self, feed_name, feed_url):
        """Fetch RSS feed and analyze content"""
        print(f"Fetching {feed_name}...")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(feed_url, headers=headers, timeout=30)
            response.raise_for_status()

            feed = feedparser.parse(response.content)
            china_items = []

            for entry in feed.entries:
                title = getattr(entry, 'title', '')
                description = getattr(entry, 'description', '')
                summary = getattr(entry, 'summary', '')

                full_text = f"{title} {description} {summary}"

                is_china_related, keywords = self.check_china_relevance(full_text)

                if is_china_related:
                    china_items.append({
                        'title': title,
                        'link': getattr(entry, 'link', ''),
                        'description': description[:200] + "..." if len(description) > 200 else description,
                        'published': getattr(entry, 'published', ''),
                        'keywords': keywords,
                        'source': feed_name
                    })

            print(f"  {feed_name}: {len(china_items)} China-related items found")
            return china_items

        except Exception as e:
            print(f"  Error fetching {feed_name}: {str(e)}")
            return []

    def monitor_feeds(self):
        """Monitor all feeds and generate report"""
        print("Starting RSS monitoring...")

        all_china_items = []

        for feed_name, feed_url in self.feeds.items():
            china_items = self.fetch_feed(feed_name, feed_url)
            all_china_items.extend(china_items)
            time.sleep(2)  # Be respectful

        # Generate report
        report = f"""# RSS China Intelligence Monitor
Generated: {datetime.now().isoformat()}

## Summary
- **Total China-Related Items**: {len(all_china_items)}
- **Sources Monitored**: {len(self.feeds)}
- **Monitoring Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## China-Related News Items

"""

        # Sort by source and add to report
        all_china_items.sort(key=lambda x: x['source'])

        current_source = None
        for item in all_china_items:
            if item['source'] != current_source:
                current_source = item['source']
                report += f"\n### {current_source}\n"

            report += f"""
**{item['title']}**
- Link: {item['link']}
- Keywords: {', '.join(item['keywords'])}
- Description: {item['description']}
- Published: {item['published']}

---
"""

        # Save report
        report_file = self.output_dir / f"rss_china_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.write_text(report, encoding='utf-8')

        # Save raw data
        data_file = self.output_dir / f"rss_china_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'monitoring_date': datetime.now().isoformat(),
                'total_items': len(all_china_items),
                'sources': list(self.feeds.keys()),
                'items': all_china_items
            }, f, indent=2, ensure_ascii=False)

        print(f"\nMonitoring complete!")
        print(f"- Found {len(all_china_items)} China-related items")
        print(f"- Report saved: {report_file}")
        print(f"- Data saved: {data_file}")

        # Show top items
        if all_china_items:
            print(f"\nTop China-related items:")
            for i, item in enumerate(all_china_items[:5], 1):
                print(f"{i}. {item['title'][:60]}... ({item['source']})")

        return all_china_items

def main():
    monitor = SimpleRSSMonitor()
    china_items = monitor.monitor_feeds()

if __name__ == "__main__":
    main()
