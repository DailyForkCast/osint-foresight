#!/usr/bin/env python3
"""
Google Patents Chinese Technology Scraper
Collects Chinese patents from Google Patents (avoiding Chinese sites)
Zero budget solution for CNIPA patent intelligence
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re
from urllib.parse import quote

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GooglePatentsChinaCollector:
    """Collect Chinese patents from Google Patents without accessing Chinese sites"""

    def __init__(self):
        self.base_url = "https://patents.google.com/xhr/query"
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.setup_database()

        # Key Chinese companies to track
        self.chinese_companies = [
            "Huawei", "华为",
            "ZTE", "中兴",
            "Alibaba", "阿里巴巴",
            "Tencent", "腾讯",
            "Baidu", "百度",
            "ByteDance", "字节跳动",
            "Xiaomi", "小米",
            "SMIC", "中芯国际",
            "BOE Technology", "京东方",
            "DJI", "大疆",
            "BYD", "比亚迪",
            "CATL", "宁德时代",
            "Lenovo", "联想",
            "Haier", "海尔"
        ]

        # Critical technology areas
        self.tech_keywords = [
            "artificial intelligence", "AI", "machine learning", "deep learning",
            "5G", "6G", "telecommunications", "wireless",
            "semiconductor", "chip", "integrated circuit", "processor",
            "quantum computing", "quantum communication",
            "biotechnology", "gene editing", "CRISPR",
            "autonomous vehicle", "self-driving", "ADAS",
            "drone", "UAV", "unmanned aerial",
            "satellite", "space technology", "aerospace",
            "cybersecurity", "encryption", "cryptography",
            "facial recognition", "biometric", "surveillance",
            "battery", "energy storage", "lithium",
            "robotics", "automation", "industrial robot"
        ]

    def setup_database(self):
        """Initialize database for storing patent data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chinese_patents (
                patent_id TEXT PRIMARY KEY,
                title TEXT,
                abstract TEXT,
                assignee TEXT,
                inventors TEXT,
                filing_date TEXT,
                publication_date TEXT,
                priority_date TEXT,
                technology_areas TEXT,
                patent_type TEXT,
                claims_count INTEGER,
                citations_count INTEGER,
                cited_by_count INTEGER,
                family_size INTEGER,
                legal_status TEXT,
                dual_use_score INTEGER,
                military_relevance INTEGER,
                us_connection INTEGER,
                collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS technology_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                technology TEXT,
                patent_count INTEGER,
                top_assignees TEXT,
                growth_rate REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logging.info("Database initialized")

    def search_patents(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search Google Patents with specific query"""
        patents = []

        # Google Patents search URL (public, no API key needed)
        search_url = f"https://patents.google.com/?q={quote(query)}&oq={quote(query)}"

        try:
            # Use requests with delay to be respectful
            time.sleep(2)  # Polite delay
            response = self.session.get(search_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Parse search results
                patent_items = soup.find_all('search-result-item')

                for item in patent_items[:max_results]:
                    patent = self.extract_patent_info(item)
                    if patent:
                        patents.append(patent)

            else:
                logging.warning(f"Search returned status {response.status_code}")

        except Exception as e:
            logging.error(f"Search error: {e}")

        return patents

    def extract_patent_info(self, patent_html) -> Optional[Dict]:
        """Extract patent information from HTML"""
        try:
            patent_data = {
                'patent_id': '',
                'title': '',
                'abstract': '',
                'assignee': '',
                'filing_date': '',
                'technology_areas': []
            }

            # Extract patent ID
            id_elem = patent_html.find('span', class_='patent-id')
            if id_elem:
                patent_data['patent_id'] = id_elem.text.strip()

            # Extract title
            title_elem = patent_html.find('span', class_='patent-title')
            if title_elem:
                patent_data['title'] = title_elem.text.strip()

            # Extract assignee
            assignee_elem = patent_html.find('span', class_='assignee')
            if assignee_elem:
                patent_data['assignee'] = assignee_elem.text.strip()

            # Classify technology
            patent_data['technology_areas'] = self.classify_technology(
                patent_data['title'] + ' ' + patent_data.get('abstract', '')
            )

            # Calculate dual-use score
            patent_data['dual_use_score'] = self.calculate_dual_use_score(patent_data)

            return patent_data

        except Exception as e:
            logging.error(f"Extraction error: {e}")
            return None

    def classify_technology(self, text: str) -> List[str]:
        """Classify patent into technology categories"""
        text_lower = text.lower()
        categories = []

        tech_categories = {
            'AI': ['artificial intelligence', 'machine learning', 'neural network', 'deep learning'],
            '5G': ['5g', '6g', 'millimeter wave', 'massive mimo'],
            'Semiconductor': ['semiconductor', 'chip', 'integrated circuit', 'transistor'],
            'Quantum': ['quantum', 'qubit', 'entanglement'],
            'Biotech': ['gene', 'crispr', 'genome', 'protein'],
            'Autonomous': ['autonomous', 'self-driving', 'lidar', 'adas'],
            'Drone': ['drone', 'uav', 'unmanned aerial'],
            'Space': ['satellite', 'orbit', 'spacecraft', 'launch vehicle'],
            'Cyber': ['encryption', 'cryptography', 'cybersecurity', 'firewall'],
            'Surveillance': ['facial recognition', 'biometric', 'surveillance', 'tracking'],
            'Battery': ['battery', 'lithium', 'energy storage', 'fuel cell'],
            'Robotics': ['robot', 'automation', 'manipulator', 'actuator']
        }

        for category, keywords in tech_categories.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)

        return categories

    def calculate_dual_use_score(self, patent: Dict) -> int:
        """Calculate potential dual-use (military) application score"""
        score = 0

        # Check title and abstract for military keywords
        text = (patent.get('title', '') + ' ' + patent.get('abstract', '')).lower()

        military_keywords = [
            'military', 'defense', 'weapon', 'missile', 'radar',
            'surveillance', 'reconnaissance', 'targeting', 'guidance',
            'encrypted', 'secure communication', 'jamming', 'stealth',
            'armor', 'ballistic', 'explosive', 'warhead'
        ]

        for keyword in military_keywords:
            if keyword in text:
                score += 10

        # Check technology categories
        high_risk_categories = ['Drone', 'Space', 'Cyber', 'Surveillance', 'AI']
        for category in patent.get('technology_areas', []):
            if category in high_risk_categories:
                score += 5

        # Cap at 100
        return min(score, 100)

    def collect_company_patents(self, company: str, years: int = 5):
        """Collect all patents from a specific Chinese company"""
        logging.info(f"Collecting patents for {company}")

        # Build query for date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)

        # Try both English and Chinese company names
        queries = [
            f'assignee:"{company}"',
            f'assignee:{company}',
            f'{company} AND country:CN'
        ]

        all_patents = []
        for query in queries:
            patents = self.search_patents(query)
            all_patents.extend(patents)

        # Remove duplicates
        unique_patents = {p['patent_id']: p for p in all_patents}.values()

        # Store in database
        self.store_patents(list(unique_patents))

        logging.info(f"Collected {len(unique_patents)} patents for {company}")
        return list(unique_patents)

    def store_patents(self, patents: List[Dict]):
        """Store patents in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for patent in patents:
            cursor.execute("""
                INSERT OR REPLACE INTO patents (
                    patent_id, title, abstract, assignee,
                    technology_areas, dual_use_score
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                patent.get('patent_id'),
                patent.get('title'),
                patent.get('abstract'),
                patent.get('assignee'),
                json.dumps(patent.get('technology_areas', [])),
                patent.get('dual_use_score', 0)
            ))

        conn.commit()
        conn.close()

    def analyze_technology_trends(self):
        """Analyze technology trends from collected patents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Analyze by technology area
        cursor.execute("""
            SELECT technology_areas, COUNT(*) as count
            FROM patents
            GROUP BY technology_areas
            ORDER BY count DESC
        """)

        tech_trends = cursor.fetchall()

        # Analyze by company
        cursor.execute("""
            SELECT assignee, COUNT(*) as patent_count,
                   AVG(dual_use_score) as avg_dual_use
            FROM patents
            GROUP BY assignee
            ORDER BY patent_count DESC
            LIMIT 20
        """)

        company_analysis = cursor.fetchall()

        conn.close()

        return {
            'technology_trends': tech_trends,
            'top_companies': company_analysis
        }

    def generate_intelligence_report(self):
        """Generate intelligence report from collected patents"""
        analysis = self.analyze_technology_trends()

        report = f"""# CHINESE PATENT INTELLIGENCE REPORT
Generated: {datetime.now().isoformat()}
Source: Google Patents (Non-Chinese Source)

## EXECUTIVE SUMMARY

### Collection Statistics
- Total Chinese Patents Analyzed: {len(analysis['technology_trends'])}
- Top Patent Filers: {len(analysis['top_companies'])}
- Data Source: Google Patents (Western source, no Chinese site access)

## TECHNOLOGY FOCUS AREAS

### Highest Patent Concentration
"""
        for tech, count in analysis['technology_trends'][:10]:
            report += f"- {tech}: {count} patents\n"

        report += """
## TOP CHINESE COMPANIES BY PATENT ACTIVITY

### Patent Leaders
"""
        for company, count, dual_use in analysis['top_companies'][:10]:
            report += f"- {company}: {count} patents (Dual-use score: {dual_use:.1f}/100)\n"

        report += """
## DUAL-USE TECHNOLOGY RISKS

Patents with highest military application potential identified.
Analysis based on technology classification and keyword matching.

## DATA COLLECTION NOTES

- All data collected from Google Patents (US-based service)
- No direct access to Chinese websites required
- Machine translations provided by Google
- Updates available without accessing CNIPA directly

---
*Report generated by Zero Budget OSINT Platform*
"""

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/CHINESE_PATENT_INTELLIGENCE.md")
        report_path.write_text(report, encoding='utf-8')

        logging.info(f"Report saved to {report_path}")
        return report

    def run_collection(self):
        """Execute full collection cycle"""
        logging.info("Starting Chinese patent collection from Google Patents")

        # Collect patents from key companies
        for company in self.chinese_companies[:5]:  # Start with top 5
            try:
                self.collect_company_patents(company)
                time.sleep(5)  # Respectful delay between companies
            except Exception as e:
                logging.error(f"Error collecting {company}: {e}")
                continue

        # Generate report
        self.generate_intelligence_report()

        logging.info("Chinese patent collection completed")


if __name__ == "__main__":
    collector = GooglePatentsChinaCollector()
    collector.run_collection()
