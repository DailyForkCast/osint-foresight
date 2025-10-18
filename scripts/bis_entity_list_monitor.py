#!/usr/bin/env python3
"""
BIS Entity List Automated Monitor and Analyzer
Tracks US export control entities with focus on Chinese technology restrictions
"""

import requests
import pandas as pd
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import time
import re
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BISEntityListMonitor:
    def __init__(self):
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.base_url = "https://www.bis.doc.gov"
        self.entity_list_url = "https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern/entity-list"
        self.denied_persons_url = "https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern/denied-persons-list"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def setup_database(self):
        """Initialize BIS monitoring database tables"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Entity List table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bis_entity_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT,
                alias TEXT,
                address TEXT,
                city TEXT,
                state_province TEXT,
                country TEXT,
                postal_code TEXT,
                federal_register_notice TEXT,
                effective_date TEXT,
                standard_order TEXT,
                license_requirement TEXT,
                license_policy TEXT,
                reason_for_inclusion TEXT,
                china_related INTEGER DEFAULT 0,
                technology_focus TEXT,
                risk_score INTEGER,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_hash TEXT UNIQUE
            )
        """)

        # Denied Persons List table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bis_denied_persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                alias TEXT,
                address TEXT,
                city TEXT,
                state_province TEXT,
                country TEXT,
                postal_code TEXT,
                federal_register_citation TEXT,
                effective_date TEXT,
                expiration_date TEXT,
                action TEXT,
                fr_citation TEXT,
                china_related INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_hash TEXT UNIQUE
            )
        """)

        # Monitoring log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bis_monitoring_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                entity_list_count INTEGER,
                denied_persons_count INTEGER,
                new_entities INTEGER,
                updated_entities INTEGER,
                china_entities INTEGER,
                status TEXT,
                notes TEXT
            )
        """)

        conn.commit()
        conn.close()
        logging.info("BIS database tables initialized")

    def fetch_entity_list_data(self):
        """Fetch current Entity List data from BIS website"""
        logging.info("Fetching BIS Entity List data")

        try:
            # First, get the main page to find download links
            response = self.session.get(self.entity_list_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for Excel/CSV download links
            download_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.csv', 'entity']):
                    if 'entity' in href.lower() or 'list' in href.lower():
                        if not href.startswith('http'):
                            href = self.base_url + href
                        download_links.append(href)
                        logging.info(f"Found potential Entity List download: {href}")

            # Try to download the first promising link
            entity_data = []
            for link in download_links[:3]:  # Try up to 3 links
                try:
                    logging.info(f"Attempting download from: {link}")
                    download_response = self.session.get(link, timeout=60)
                    download_response.raise_for_status()

                    # Save to temporary file and try to read
                    temp_file = Path("temp_entity_list.xlsx")
                    temp_file.write_bytes(download_response.content)

                    # Try to read as Excel
                    try:
                        df = pd.read_excel(temp_file)
                        logging.info(f"Successfully downloaded Entity List: {len(df)} entries")
                        entity_data = df.to_dict('records')
                        temp_file.unlink()  # Clean up
                        break
                    except Exception as e:
                        logging.warning(f"Could not read as Excel: {e}")
                        temp_file.unlink()
                        continue

                except Exception as e:
                    logging.warning(f"Failed to download from {link}: {e}")
                    continue

            if not entity_data:
                # Fallback: scrape from webpage
                logging.info("Attempting to scrape Entity List from webpage")
                entity_data = self.scrape_entity_list_webpage(soup)

            return entity_data

        except Exception as e:
            logging.error(f"Error fetching Entity List: {e}")
            return []

    def scrape_entity_list_webpage(self, soup):
        """Fallback method to scrape entity list from webpage"""
        entities = []

        try:
            # Look for tables or structured data
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:  # Need at least name, address, country
                        entity = {
                            'entity_name': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                            'address': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                            'country': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                            'reason_for_inclusion': cells[-1].get_text(strip=True) if len(cells) > 3 else ''
                        }
                        if entity['entity_name']:
                            entities.append(entity)

            logging.info(f"Scraped {len(entities)} entities from webpage")

        except Exception as e:
            logging.error(f"Error scraping webpage: {e}")

        return entities

    def analyze_china_relevance(self, entity_data):
        """Analyze entities for China relevance and technology focus"""
        china_indicators = ['china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'guangzhou',
                           'hong kong', 'macau', 'taiwan', 'prc', 'peoples republic']

        tech_indicators = ['semiconductor', 'quantum', 'artificial intelligence', 'ai', '5g', '6g',
                          'biotechnology', 'nanotechnology', 'aerospace', 'defense', 'military',
                          'dual-use', 'technology', 'research', 'university', 'institute']

        for entity in entity_data:
            # Check China relevance
            entity_text = ' '.join([
                str(entity.get('entity_name', '')),
                str(entity.get('address', '')),
                str(entity.get('country', '')),
                str(entity.get('reason_for_inclusion', ''))
            ]).lower()

            china_related = 0
            china_score = 0
            for indicator in china_indicators:
                if indicator in entity_text:
                    china_related = 1
                    china_score += 1

            # Check technology focus
            tech_focus = []
            tech_score = 0
            for indicator in tech_indicators:
                if indicator in entity_text:
                    tech_focus.append(indicator)
                    tech_score += 1

            # Calculate risk score
            risk_score = min(100, (china_score * 20) + (tech_score * 10))

            entity['china_related'] = china_related
            entity['technology_focus'] = ', '.join(tech_focus) if tech_focus else None
            entity['risk_score'] = risk_score

        return entity_data

    def store_entity_data(self, entity_data):
        """Store Entity List data in database"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        new_entities = 0
        updated_entities = 0
        china_entities = 0

        for entity in entity_data:
            # Create hash for deduplication
            entity_text = f"{entity.get('entity_name', '')}{entity.get('address', '')}{entity.get('country', '')}"
            data_hash = hashlib.md5(entity_text.encode()).hexdigest()

            # Check if entity exists
            cursor.execute("SELECT id FROM bis_entity_list WHERE data_hash = ?", (data_hash,))
            existing = cursor.fetchone()

            if entity.get('china_related'):
                china_entities += 1

            if not existing:
                # Insert new entity
                cursor.execute("""
                    INSERT INTO bis_entity_list (
                        entity_name, address, country, reason_for_inclusion,
                        china_related, technology_focus, risk_score, data_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity.get('entity_name', ''),
                    entity.get('address', ''),
                    entity.get('country', ''),
                    entity.get('reason_for_inclusion', ''),
                    entity.get('china_related', 0),
                    entity.get('technology_focus'),
                    entity.get('risk_score', 0),
                    data_hash
                ))
                new_entities += 1
            else:
                # Update existing entity
                cursor.execute("""
                    UPDATE bis_entity_list SET
                        china_related = ?, technology_focus = ?, risk_score = ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE data_hash = ?
                """, (
                    entity.get('china_related', 0),
                    entity.get('technology_focus'),
                    entity.get('risk_score', 0),
                    data_hash
                ))
                updated_entities += 1

        # Log monitoring run
        cursor.execute("""
            INSERT INTO bis_monitoring_log (
                entity_list_count, new_entities, updated_entities, china_entities, status
            ) VALUES (?, ?, ?, ?, ?)
        """, (len(entity_data), new_entities, updated_entities, china_entities, 'SUCCESS'))

        conn.commit()
        conn.close()

        logging.info(f"Stored Entity List data: {new_entities} new, {updated_entities} updated, {china_entities} China-related")
        return {'new': new_entities, 'updated': updated_entities, 'china': china_entities}

    def generate_bis_intelligence_report(self):
        """Generate BIS intelligence analysis report"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Get overall statistics
        cursor.execute("SELECT COUNT(*) FROM bis_entity_list")
        total_entities = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM bis_entity_list WHERE china_related = 1")
        china_entities = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM bis_entity_list WHERE technology_focus IS NOT NULL")
        tech_entities = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM bis_entity_list WHERE china_related = 1 AND technology_focus IS NOT NULL")
        china_tech_entities = cursor.fetchone()[0]

        # Get top countries
        cursor.execute("""
            SELECT country, COUNT(*) as count
            FROM bis_entity_list
            GROUP BY country
            ORDER BY count DESC
            LIMIT 10
        """)
        top_countries = cursor.fetchall()

        # Get China-related high-risk entities
        cursor.execute("""
            SELECT entity_name, country, technology_focus, risk_score, reason_for_inclusion
            FROM bis_entity_list
            WHERE china_related = 1
            ORDER BY risk_score DESC
            LIMIT 20
        """)
        high_risk_china = cursor.fetchall()

        # Get technology focus breakdown
        cursor.execute("""
            SELECT technology_focus, COUNT(*) as count
            FROM bis_entity_list
            WHERE technology_focus IS NOT NULL AND technology_focus != ''
            GROUP BY technology_focus
            ORDER BY count DESC
            LIMIT 10
        """)
        tech_focus = cursor.fetchall()

        conn.close()

        # Generate report
        report = f"""# BIS ENTITY LIST INTELLIGENCE REPORT
Generated: {datetime.now().isoformat()}

## EXECUTIVE SUMMARY

### Export Control Intelligence
- **Total Entities Monitored**: {total_entities:,}
- **China-Related Entities**: {china_entities:,} ({china_entities/max(total_entities,1)*100:.1f}%)
- **Technology-Focused Entities**: {tech_entities:,}
- **Chinese Technology Entities**: {china_tech_entities:,}

## GEOGRAPHIC DISTRIBUTION

### Top Countries by Entity Count"""

        for country, count in top_countries:
            percentage = count/max(total_entities,1)*100
            report += f"\n- **{country}**: {count:,} entities ({percentage:.1f}%)"

        report += f"\n\n## HIGH-RISK CHINESE TECHNOLOGY ENTITIES\n"
        report += f"### Top 20 China-Related Entities by Risk Score\n"

        for i, (name, country, tech_focus, risk_score, reason) in enumerate(high_risk_china, 1):
            tech_display = f" - {tech_focus}" if tech_focus else ""
            report += f"\n{i}. **{name}** ({country}){tech_display} - Risk: {risk_score}"
            if reason:
                report += f"\n   - Reason: {reason[:100]}..."

        report += f"\n\n## TECHNOLOGY FOCUS ANALYSIS\n"
        for tech, count in tech_focus:
            report += f"\n- **{tech}**: {count:,} entities"

        report += f"""

## KEY FINDINGS

### Export Control Patterns
1. **Chinese Dominance**: {china_entities:,} entities represent significant portion of Entity List
2. **Technology Concentration**: Focus on {', '.join([t[0].split(',')[0] for t in tech_focus[:3]])}
3. **Risk Distribution**: High-risk entities concentrated in specific technology domains

### Intelligence Value
- Real-time export control violation tracking
- Technology transfer restriction monitoring
- Chinese entity relationship mapping
- Dual-use technology oversight

## OPERATIONAL RECOMMENDATIONS

1. **Daily Monitoring**: Automated checks for Entity List updates
2. **Cross-Reference Analysis**: Link with other datasets (patents, research, investments)
3. **Alert System**: Notifications for new Chinese technology entities
4. **Risk Assessment**: Enhanced scoring based on technology domains

---
*Data sourced from BIS Entity List - Official US Export Control Database*
"""

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/BIS_ENTITY_LIST_INTELLIGENCE.md")
        report_path.write_text(report, encoding='utf-8')

        print(report)
        return report

    def run_monitoring_cycle(self):
        """Execute complete BIS monitoring cycle"""
        logging.info("Starting BIS Entity List monitoring cycle")

        self.setup_database()

        # Fetch and process Entity List
        entity_data = self.fetch_entity_list_data()
        if entity_data:
            analyzed_data = self.analyze_china_relevance(entity_data)
            storage_results = self.store_entity_data(analyzed_data)

            # Generate intelligence report
            self.generate_bis_intelligence_report()

            logging.info("BIS monitoring cycle completed successfully")
            return storage_results
        else:
            logging.error("No Entity List data retrieved")
            return None

if __name__ == "__main__":
    monitor = BISEntityListMonitor()
    monitor.run_monitoring_cycle()
