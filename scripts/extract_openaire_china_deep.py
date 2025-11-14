#!/usr/bin/env python3
"""
Deep extraction of China-related data from OpenAIRE database
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
import re

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OpenAIREChinaExtractor:
    def __init__(self):
        self.source_db = "F:/OSINT_DATA/openaire_production_comprehensive/openaire_production.db"
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.output_file = f"data/processed/openaire_china_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    def extract_china_data(self):
        """Extract all China-related data from OpenAIRE"""

        logging.info("Starting deep extraction of OpenAIRE China data")

        conn_source = sqlite3.connect(self.source_db)
        cursor_source = conn_source.cursor()

        results = {
            'extraction_time': datetime.now().isoformat(),
            'china_collaborations': [],
            'china_research': [],
            'country_statistics': {},
            'top_organizations': {},
            'temporal_patterns': {},
            'research_types': {}
        }

        # 1. Extract China collaborations from collaborations table
        logging.info("Extracting China collaborations...")

        # First check actual column names
        cursor_source.execute("PRAGMA table_info(collaborations)")
        columns = [col[1] for col in cursor_source.fetchall()]

        # Build query with available columns
        if 'countries_list' in columns:
            countries_col = 'countries_list'
        else:
            countries_col = 'partner_countries'  # fallback

        # SECURITY: Validate column name before use in SQL
        safe_col = validate_sql_identifier(countries_col)
        cursor_source.execute(f"""
            SELECT
                id,
                primary_country,
                partner_countries,
                title,
                date_accepted,
                result_type,
                doi,
                num_countries,
                organizations,
                is_china_collaboration,
                {safe_col}
            FROM collaborations
            WHERE
                is_china_collaboration = 1
                OR partner_countries LIKE '%China%'
                OR partner_countries LIKE '%CN%'
                OR organizations LIKE '%China%'
                OR organizations LIKE '%Chinese%'
                OR organizations LIKE '%Beijing%'
                OR organizations LIKE '%Shanghai%'
                OR organizations LIKE '%Tsinghua%'
                OR organizations LIKE '%Peking%'
                OR organizations LIKE '%Fudan%'
                OR organizations LIKE '%Zhejiang%'
            ORDER BY date_accepted DESC
        """)

        collaborations = cursor_source.fetchall()
        logging.info(f"Found {len(collaborations)} China collaborations")

        for collab in collaborations:
            results['china_collaborations'].append({
                'id': collab[0],
                'primary_country': collab[1],
                'partner_countries': collab[2],
                'title': collab[3],
                'date': collab[4],
                'type': collab[5],
                'doi': collab[6],
                'num_countries': collab[7],
                'organizations': collab[8],
                'is_china_collaboration': collab[9],
                'countries_list': collab[10] if len(collab) > 10 else collab[2]
            })

        # 2. Extract China research products
        logging.info("Extracting China research products...")

        cursor_source.execute("""
            SELECT
                id,
                country_code,
                title,
                date_accepted,
                result_type,
                doi,
                processing_batch,
                has_collaboration,
                SUBSTR(raw_data, 1, 500) as raw_data_sample
            FROM research_products
            WHERE
                country_code = 'CN'
                OR title LIKE '%China%'
                OR title LIKE '%Chinese%'
                OR raw_data LIKE '%China%'
                OR raw_data LIKE '%Chinese%'
                OR raw_data LIKE '%Beijing%'
                OR raw_data LIKE '%Shanghai%'
            LIMIT 1000
        """)

        research_products = cursor_source.fetchall()
        logging.info(f"Found {len(research_products)} China research products")

        for product in research_products:
            results['china_research'].append({
                'id': product[0],
                'country_code': product[1],
                'title': product[2],
                'date': product[3],
                'type': product[4],
                'doi': product[5],
                'batch': product[6],
                'has_collaboration': product[7],
                'data_sample': product[8]
            })

        # 3. Get country overview statistics
        logging.info("Extracting country collaboration statistics...")

        cursor_source.execute("""
            SELECT
                country_code,
                country_name,
                total_research_products,
                total_collaborations,
                china_collaborations,
                ROUND(100.0 * china_collaborations / NULLIF(total_collaborations, 0), 2) as china_collab_percentage
            FROM country_overview
            WHERE china_collaborations > 0
            ORDER BY china_collaborations DESC
        """)

        country_stats = cursor_source.fetchall()

        for stat in country_stats:
            results['country_statistics'][stat[0]] = {
                'name': stat[1],
                'total_research': stat[2],
                'total_collaborations': stat[3],
                'china_collaborations': stat[4],
                'china_percentage': stat[5]
            }

        logging.info(f"Found {len(country_stats)} countries with China collaborations")

        # 4. Extract top Chinese organizations
        logging.info("Analyzing Chinese organizations...")

        # Parse organizations from collaborations
        org_counts = {}
        for collab in results['china_collaborations']:
            if collab['organizations']:
                orgs = collab['organizations'].split(';')
                for org in orgs:
                    org = org.strip()
                    if any(keyword in org for keyword in ['China', 'Chinese', 'Beijing', 'Shanghai',
                                                           'Tsinghua', 'Peking', 'Fudan', 'Zhejiang',
                                                           'Academy', 'University']):
                        org_counts[org] = org_counts.get(org, 0) + 1

        # Get top 20 organizations
        top_orgs = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        results['top_organizations'] = dict(top_orgs)

        # 5. Temporal analysis
        logging.info("Analyzing temporal patterns...")

        cursor_source.execute("""
            SELECT
                SUBSTR(date_accepted, 1, 4) as year,
                COUNT(*) as count
            FROM collaborations
            WHERE is_china_collaboration = 1
            AND date_accepted IS NOT NULL
            AND date_accepted != ''
            GROUP BY year
            ORDER BY year DESC
        """)

        temporal_data = cursor_source.fetchall()
        results['temporal_patterns'] = dict(temporal_data)

        # 6. Research type analysis
        logging.info("Analyzing research types...")

        cursor_source.execute("""
            SELECT
                result_type,
                COUNT(*) as count
            FROM collaborations
            WHERE is_china_collaboration = 1
            AND result_type IS NOT NULL
            GROUP BY result_type
            ORDER BY count DESC
        """)

        type_data = cursor_source.fetchall()
        results['research_types'] = dict(type_data)

        conn_source.close()

        # Save to JSON file
        output_path = Path(self.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logging.info(f"Saved extraction to {self.output_file}")

        # Store in master database
        self.store_in_master_db(results)

        return results

    def store_in_master_db(self, results):
        """Store extracted data in master OSINT database"""

        logging.info("Storing in master database...")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Create enhanced OpenAIRE tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openaire_china_collaborations (
                id INTEGER PRIMARY KEY,
                primary_country TEXT,
                partner_countries TEXT,
                title TEXT,
                date_accepted TEXT,
                result_type TEXT,
                doi TEXT,
                num_countries INTEGER,
                organizations TEXT,
                chinese_orgs TEXT,
                risk_indicators TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openaire_chinese_organizations (
                org_name TEXT PRIMARY KEY,
                collaboration_count INTEGER,
                countries TEXT,
                research_types TEXT,
                risk_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openaire_country_china_stats (
                country_code TEXT PRIMARY KEY,
                country_name TEXT,
                total_research INTEGER,
                china_collaborations INTEGER,
                china_percentage REAL,
                top_research_areas TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert collaborations
        for collab in results['china_collaborations']:
            # Extract Chinese organizations
            chinese_orgs = []
            if collab['organizations']:
                orgs = collab['organizations'].split(';')
                for org in orgs:
                    if any(keyword in org for keyword in ['China', 'Chinese', 'Beijing', 'Shanghai']):
                        chinese_orgs.append(org.strip())

            # Determine risk indicators
            risk_indicators = []
            org_text = str(collab['organizations']).lower()
            if 'academy' in org_text and 'sciences' in org_text:
                risk_indicators.append('CAS')
            if 'defense' in org_text or 'military' in org_text:
                risk_indicators.append('DEFENSE')
            if 'nuclear' in org_text or 'atomic' in org_text:
                risk_indicators.append('NUCLEAR')
            if 'aerospace' in org_text or 'space' in org_text:
                risk_indicators.append('AEROSPACE')

            cursor.execute("""
                INSERT OR IGNORE INTO openaire_china_collaborations
                (id, primary_country, partner_countries, title, date_accepted,
                 result_type, doi, num_countries, organizations, chinese_orgs, risk_indicators)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                collab['id'],
                collab['primary_country'],
                collab['partner_countries'],
                collab['title'],
                collab['date'],
                collab['type'],
                collab['doi'],
                collab['num_countries'],
                collab['organizations'],
                ';'.join(chinese_orgs),
                ','.join(risk_indicators)
            ))

        # Insert organizations
        for org_name, count in results['top_organizations'].items():
            # Determine risk level
            risk_level = 'LOW'
            org_lower = org_name.lower()
            if 'academy' in org_lower and 'sciences' in org_lower:
                risk_level = 'HIGH'
            elif 'defense' in org_lower or 'military' in org_lower:
                risk_level = 'CRITICAL'
            elif 'university' in org_lower:
                if any(uni in org_lower for uni in ['tsinghua', 'peking', 'beihang', 'harbin']):
                    risk_level = 'HIGH'
                else:
                    risk_level = 'MEDIUM'

            cursor.execute("""
                INSERT OR REPLACE INTO openaire_chinese_organizations
                (org_name, collaboration_count, risk_level)
                VALUES (?, ?, ?)
            """, (org_name, count, risk_level))

        # Insert country statistics
        for country_code, stats in results['country_statistics'].items():
            cursor.execute("""
                INSERT OR REPLACE INTO openaire_country_china_stats
                (country_code, country_name, total_research, china_collaborations, china_percentage)
                VALUES (?, ?, ?, ?, ?)
            """, (
                country_code,
                stats['name'],
                stats['total_research'],
                stats['china_collaborations'],
                stats['china_percentage']
            ))

        conn.commit()

        # Get final counts
        cursor.execute("SELECT COUNT(*) FROM openaire_china_collaborations")
        collab_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM openaire_chinese_organizations")
        org_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM openaire_country_china_stats")
        country_count = cursor.fetchone()[0]

        conn.close()

        logging.info(f"Stored in master DB: {collab_count} collaborations, {org_count} organizations, {country_count} countries")

        return {
            'collaborations_stored': collab_count,
            'organizations_stored': org_count,
            'countries_stored': country_count
        }

    def generate_summary_report(self, results):
        """Generate a summary report of findings"""

        report = []
        report.append("=" * 80)
        report.append("OPENAIRE CHINA DATA EXTRACTION SUMMARY")
        report.append("=" * 80)

        report.append(f"\nTotal China Collaborations: {len(results['china_collaborations'])}")
        report.append(f"Total China Research Products: {len(results['china_research'])}")
        report.append(f"Countries with China Collaborations: {len(results['country_statistics'])}")

        report.append("\n### Top 10 Countries by China Collaborations:")
        for i, (code, stats) in enumerate(list(results['country_statistics'].items())[:10], 1):
            report.append(f"{i}. {stats['name']} ({code}): {stats['china_collaborations']} collaborations ({stats['china_percentage']}%)")

        report.append("\n### Top 10 Chinese Organizations:")
        for i, (org, count) in enumerate(list(results['top_organizations'].items())[:10], 1):
            report.append(f"{i}. {org}: {count} collaborations")

        report.append("\n### Temporal Trends (Last 5 Years):")
        years = sorted(results['temporal_patterns'].keys(), reverse=True)[:5]
        for year in years:
            report.append(f"  {year}: {results['temporal_patterns'][year]} collaborations")

        report.append("\n### Research Types:")
        for rtype, count in list(results['research_types'].items())[:5]:
            report.append(f"  {rtype}: {count}")

        return "\n".join(report)

if __name__ == "__main__":
    extractor = OpenAIREChinaExtractor()
    results = extractor.extract_china_data()

    # Print summary
    summary = extractor.generate_summary_report(results)
    print(summary)

    print(f"\nExtraction complete. Data saved to {extractor.output_file}")
