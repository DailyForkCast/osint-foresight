#!/usr/bin/env python3
"""
Quick MCF Collector - Simple working collector to populate the database
"""

import requests
import sqlite3
import json
from datetime import datetime
from bs4 import BeautifulSoup
import time

class QuickMCFCollector:
    """Simple working MCF collector"""

    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_research.db"

    def collect_from_url(self, url, source_name="manual"):
        """Collect a single URL"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract text
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=' ', strip=True)

            # Calculate relevance (simple keyword matching)
            mcf_keywords = ['china', 'military', 'fusion', 'technology', 'defense', 'pla',
                           'dual-use', 'dual use', 'huawei', 'export control']

            text_lower = text.lower()
            score = sum(1 for kw in mcf_keywords if kw in text_lower) / len(mcf_keywords)

            # Get title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else url

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO mcf_documents
                (url, title, content, relevance_score, collector, collection_timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                url,
                title_text,
                text[:50000],  # Limit content size
                score,
                source_name,
                datetime.now().isoformat(),
                json.dumps({'source': source_name})
            ))

            conn.commit()
            conn.close()

            print(f"[OK] Collected: {title_text[:60]}... (Score: {score:.2f})")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to collect {url}: {e}")
            return False

    def collect_mcf_sources(self):
        """Collect from known good MCF sources"""

        # URLs that are known to work and have MCF content - Updated 2025
        mcf_urls = [
            # RAND - these work
            "https://www.rand.org/pubs/research_reports/RRA869-3.html",
            "https://www.rand.org/topics/china-military.html",

            # War on the Rocks - updated URLs
            "https://warontherocks.com/2025/01/the-false-promise-of-u-s-china-decoupling/",

            # Brookings - working URLs
            "https://www.brookings.edu/articles/us-china-technology-competition/",

            # CNAS - updated
            "https://www.cnas.org/research/china",

            # Atlantic Council
            "https://www.atlanticcouncil.org/programs/scowcroft-center-for-strategy-and-security/global-china-hub/",

            # CSIS
            "https://www.csis.org/programs/china-power-project",
            "https://www.csis.org/analysis/surveying-chinas-digital-silk-road",

            # Foreign Affairs
            "https://www.foreignaffairs.com/china",

            # MIT Tech Review
            "https://www.technologyreview.com/topic/china/",

            # Asia Society Policy Institute
            "https://asiasociety.org/policy-institute/topics/china"
        ]

        collected = 0
        for url in mcf_urls:
            if self.collect_from_url(url, source_name="mcf_sources"):
                collected += 1
                time.sleep(2)  # Rate limiting

        print(f"\nCollected {collected}/{len(mcf_urls)} documents")
        return collected

def main():
    collector = QuickMCFCollector()
    print("Starting MCF collection from known sources...")
    print("-" * 50)

    collected = collector.collect_mcf_sources()

    print("-" * 50)
    print(f"Collection complete: {collected} documents added to database")
    print(f"Database: F:/OSINT_WAREHOUSE/osint_research.db")

if __name__ == "__main__":
    main()
