#!/usr/bin/env python3
"""
Enhanced MCF Think Tank Data Collector
Collects Military-Civil Fusion intelligence from various think tank sources
"""

import sqlite3
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import time
import hashlib
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcf_collection.log'),
        logging.StreamHandler()
    ]
)

class EnhancedMCFCollector:
    """Collect MCF intelligence from think tank sources"""

    def __init__(self, db_path: str = "F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        # Statistics
        self.stats = {
            "urls_attempted": 0,
            "documents_collected": 0,
            "entities_extracted": 0,
            "errors": []
        }

        # Enhanced MCF keywords and patterns
        self.mcf_keywords = [
            'military-civil fusion', 'civil-military integration', '军民融合',
            'dual-use', 'dual use technology', 'technology transfer',
            'china', 'chinese', 'pla', 'peoples liberation army',
            'huawei', 'zte', 'hikvision', 'dahua', 'bytedance', 'tiktok',
            'artificial intelligence', 'quantum computing', 'hypersonic',
            'semiconductor', '5g', '6g', 'surveillance', 'export control',
            'beijing', 'xi jinping', 'made in china 2025', 'belt and road',
            'strategic competition', 'decoupling', 'supply chain'
        ]

        # Entity patterns
        self.entity_patterns = {
            'companies': ['huawei', 'zte', 'alibaba', 'tencent', 'baidu', 'xiaomi',
                         'bytedance', 'hikvision', 'dahua', 'smic', 'bgi', 'dji'],
            'technologies': ['ai', '5g', '6g', 'quantum', 'semiconductor', 'biotech',
                           'hypersonic', 'space', 'cyber', 'robotics', 'blockchain'],
            'organizations': ['pla', 'cas', 'mss', 'miit', 'ndrc', 'sastind'],
            'programs': ['made in china 2025', 'belt and road', 'bri', 'mcf']
        }

    def calculate_relevance(self, text: str, url: str = "") -> float:
        """Calculate MCF relevance score"""
        text_lower = text.lower()
        url_lower = url.lower()

        # Keyword matching
        keyword_score = sum(1 for kw in self.mcf_keywords if kw in text_lower)
        keyword_score = min(keyword_score / 10, 1.0)  # Normalize

        # URL relevance
        url_score = 0.3 if any(term in url_lower for term in ['china', 'mcf', 'military', 'defense']) else 0

        # Length bonus (longer documents likely more comprehensive)
        length_score = min(len(text) / 10000, 0.3)

        return min(keyword_score + url_score + length_score, 1.0)

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract relevant entities from text"""
        text_lower = text.lower()
        entities = {}

        for entity_type, patterns in self.entity_patterns.items():
            found = []
            for pattern in patterns:
                if pattern in text_lower:
                    found.append(pattern.upper())
            if found:
                entities[entity_type] = list(set(found))

        return entities

    def collect_from_url(self, url: str, source_name: str) -> bool:
        """Collect and store document from URL"""
        try:
            self.stats["urls_attempted"] += 1

            # Check if already collected
            self.cursor.execute("SELECT doc_id FROM mcf_documents WHERE url = ?", (url,))
            if self.cursor.fetchone():
                logging.info(f"Already collected: {url}")
                return False

            # Fetch content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Parse content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove scripts and styles
            for element in soup(['script', 'style', 'meta', 'link']):
                element.decompose()

            # Extract text
            text = soup.get_text(separator=' ', strip=True)

            # Get title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else url.split('/')[-1]

            # Calculate relevance
            relevance = self.calculate_relevance(text, url)

            # Skip if low relevance
            if relevance < 0.2:
                logging.info(f"Skipping low relevance ({relevance:.2f}): {title_text[:60]}")
                return False

            # Extract entities
            entities = self.extract_entities(text)

            # Generate doc_id
            doc_id = hashlib.md5(url.encode()).hexdigest()[:16]

            # Store document
            self.cursor.execute("""
            INSERT OR REPLACE INTO mcf_documents (
                doc_id, title, url, source, collection_date,
                content, relevance_score, technology_areas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                title_text[:500],
                url,
                source_name,
                datetime.now().isoformat(),
                text[:100000],  # Limit content size
                relevance,
                json.dumps(entities.get('technologies', []))
            ))

            # Store entities
            for entity_type, entity_list in entities.items():
                for entity_name in entity_list:
                    self.cursor.execute("""
                    INSERT OR IGNORE INTO mcf_entities (name, entity_type)
                    VALUES (?, ?)
                    """, (entity_name, entity_type))

                    # Get entity_id
                    self.cursor.execute(
                        "SELECT entity_id FROM mcf_entities WHERE name = ? AND entity_type = ?",
                        (entity_name, entity_type)
                    )
                    entity_id = self.cursor.fetchone()[0]

                    # Link to document
                    self.cursor.execute("""
                    INSERT OR REPLACE INTO mcf_document_entities (doc_id, entity_id)
                    VALUES (?, ?)
                    """, (doc_id, entity_id))

                    self.stats["entities_extracted"] += 1

            self.conn.commit()
            self.stats["documents_collected"] += 1

            logging.info(f"[OK] Collected: {title_text[:60]}... (Relevance: {relevance:.2f})")
            return True

        except Exception as e:
            error_msg = f"Failed {url}: {str(e)}"
            logging.error(error_msg)
            self.stats["errors"].append(error_msg)
            return False

    def collect_think_tank_sources(self):
        """Collect from major think tank sources"""

        sources = {
            # US Government & Military
            "state_dept": [
                "https://www.state.gov/military-civil-fusion-and-the-peoples-republic-of-china/",
                "https://www.state.gov/chinas-predatory-economic-and-security-practices/"
            ],

            # Major Think Tanks
            "csis": [
                "https://www.csis.org/analysis/chinas-new-strategy-waging-microchip-tech-war",
                "https://www.csis.org/programs/china-power-project",
                "https://www.csis.org/analysis/surveying-chinas-digital-silk-road"
            ],

            "brookings": [
                "https://www.brookings.edu/articles/us-china-technology-competition/",
                "https://www.brookings.edu/articles/racing-toward-zero-chinas-export-controls/"
            ],

            "cfr": [
                "https://www.cfr.org/backgrounder/made-china-2025-threat-global-trade",
                "https://www.cfr.org/article/us-china-tech-cold-war-deepens"
            ],

            "rand": [
                "https://www.rand.org/pubs/research_reports/RRA869-3.html",
                "https://www.rand.org/topics/china-military.html",
                "https://www.rand.org/pubs/tools/TL389.html"
            ],

            "heritage": [
                "https://www.heritage.org/asia/commentary/chinas-military-civil-fusion-strategy-should-raise-red-flags",
                "https://www.heritage.org/defense/report/chinas-defense-mobilization-model-the-new-peoples-war"
            ],

            "hudson": [
                "https://www.hudson.org/national-security-defense/chinas-military-civil-fusion-strategy",
                "https://www.hudson.org/research/china"
            ],

            "aei": [
                "https://www.aei.org/research-products/report/broken-engagement-the-strategy-behind-chinas-technological-rise/",
                "https://www.aei.org/china/"
            ],

            "carnegie": [
                "https://carnegieendowment.org/research/2025/01/china-digital-silk-road-investments",
                "https://carnegieendowment.org/programs/china"
            ],

            "atlantic_council": [
                "https://www.atlanticcouncil.org/programs/scowcroft-center-for-strategy-and-security/global-china-hub/",
                "https://www.atlanticcouncil.org/in-depth-research-reports/report/china-plan/"
            ],

            # Technology & Innovation
            "itif": [
                "https://itif.org/publications/2025/01/21/wake-up-america-china-is-overtaking-us-in-innovation-capacity/",
                "https://itif.org/publications/2025/01/13/chinas-quest-for-semiconductor-independence/"
            ],

            # Academic & Research
            "cnas": [
                "https://www.cnas.org/research/china",
                "https://www.cnas.org/publications/reports/dangerous-synergies"
            ],

            # Asia-Pacific Focus
            "jamestown": [
                "https://jamestown.org/programs/cb/",
                "https://jamestown.org/program/military-civil-fusion/"
            ]
        }

        logging.info(f"Starting collection from {sum(len(urls) for urls in sources.values())} URLs...")

        for source, urls in sources.items():
            logging.info(f"\nCollecting from {source}...")
            for url in urls:
                if self.collect_from_url(url, source):
                    time.sleep(2)  # Rate limiting
                else:
                    time.sleep(1)

        logging.info("\nCollection complete!")

    def generate_report(self):
        """Generate collection report"""

        # Get database statistics
        self.cursor.execute("SELECT COUNT(*) FROM mcf_documents")
        total_docs = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM mcf_entities")
        total_entities = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM mcf_document_entities")
        total_relationships = self.cursor.fetchone()[0]

        # Top entities
        self.cursor.execute("""
        SELECT e.name, e.entity_type, COUNT(de.doc_id) as mentions
        FROM mcf_entities e
        JOIN mcf_document_entities de ON e.entity_id = de.entity_id
        GROUP BY e.entity_id
        ORDER BY mentions DESC
        LIMIT 10
        """)
        top_entities = self.cursor.fetchall()

        # Top sources
        self.cursor.execute("""
        SELECT source, COUNT(*) as doc_count, AVG(relevance_score) as avg_relevance
        FROM mcf_documents
        GROUP BY source
        ORDER BY doc_count DESC
        """)
        sources = self.cursor.fetchall()

        report = f"""
MCF Collection Report
====================
Collection Time: {datetime.now().isoformat()}
Database: {self.db_path}

Collection Statistics:
- URLs Attempted: {self.stats['urls_attempted']}
- Documents Collected: {self.stats['documents_collected']}
- Entities Extracted: {self.stats['entities_extracted']}
- Errors: {len(self.stats['errors'])}

Database Totals:
- Total Documents: {total_docs}
- Total Entities: {total_entities}
- Total Relationships: {total_relationships}

Top Entities by Mentions:
"""
        for name, entity_type, mentions in top_entities:
            report += f"  - {name} ({entity_type}): {mentions} mentions\n"

        report += "\nDocuments by Source:\n"
        for source, count, relevance in sources:
            report += f"  - {source}: {count} docs, {relevance:.2f} avg relevance\n"

        if self.stats['errors']:
            report += "\nErrors:\n"
            for error in self.stats['errors'][:10]:
                report += f"  - {error}\n"

        return report

    def run(self):
        """Execute collection process"""
        try:
            logging.info("Starting Enhanced MCF Collection")
            logging.info(f"Database: {self.db_path}")

            # Collect from sources
            self.collect_think_tank_sources()

            # Generate and save report
            report = self.generate_report()
            print(report)

            # Save report to file
            report_file = Path("mcf_collection_report.txt")
            with open(report_file, 'w') as f:
                f.write(report)

            logging.info(f"\nReport saved to {report_file}")

        except Exception as e:
            logging.error(f"Fatal error: {e}")
            raise
        finally:
            self.conn.close()

def main():
    """Main execution function"""
    collector = EnhancedMCFCollector()
    collector.run()

if __name__ == "__main__":
    main()
