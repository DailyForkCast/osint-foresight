#!/usr/bin/env python3
"""
OpenSanctions Data Downloader
Downloads all available sanctions datasets to external drive for analysis
"""

import requests
import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import sqlite3
from collections import defaultdict
import urllib.parse

class OpenSanctionsDownloader:
    def __init__(self, base_path: str = "F:/OSINT_Data/OpenSanctions"):
        self.base_path = Path(base_path)
        self.base_url = "https://data.opensanctions.org/datasets"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research-Bot/1.0 (Academic Research)'
        })

        # Create directory structure
        self.setup_directories()

        # Known dataset structure from your URLs
        self.known_datasets = [
            "us_bis_denied",  # Bureau of Industry and Security Denied Parties List
            "us_ofac_sdn",    # OFAC Specially Designated Nationals
            "gb_hmt_sanctions", # UK HM Treasury sanctions
            "eu_fsf",         # EU Financial Sanctions File
            "ca_dfatd_sema",  # Canada sanctions
            "au_dfat_sanctions", # Australia sanctions
            "un_sc_sanctions", # UN Security Council sanctions
            "ch_seco_sanctions", # Switzerland sanctions
            "jp_mof_sanctions", # Japan sanctions
            "kr_fss_sanctions", # South Korea sanctions
            "sg_mas_sanctions", # Singapore sanctions
            "hk_fsd_sanctions", # Hong Kong sanctions
            "worldbank_debarred", # World Bank debarred entities
            "adb_sanctions",   # Asian Development Bank
            "everypolitician", # Politically Exposed Persons
            "opencorporates",  # Corporate entities
            "us_trade_csl",    # Commerce Consolidated Screening List
            "us_bis_entity_list", # BIS Entity List (very relevant for China)
            "us_bis_unverified_list", # BIS Unverified List
            "us_state_dept_sanctions" # State Department sanctions
        ]

    def setup_directories(self):
        """Create organized directory structure"""
        directories = [
            self.base_path / "raw_data",
            self.base_path / "processed",
            self.base_path / "analysis",
            self.base_path / "china_entities",
            self.base_path / "logs"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        print(f"Created directory structure at {self.base_path}")

    def get_latest_date(self):
        """Get the most recent dataset date"""
        # Use current date as starting point, will discover actual latest date
        return datetime.now().strftime('%Y%m%d')

    def download_file(self, url: str, local_path: Path, description: str = ""):
        """Download a single file with error handling"""
        try:
            print(f"Downloading {description}: {url}")
            response = self.session.get(url, timeout=300)
            response.raise_for_status()

            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content based on file type
            if local_path.suffix.lower() in ['.json', '.txt', '.csv']:
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            else:
                with open(local_path, 'wb') as f:
                    f.write(response.content)

            print(f"  [OK] Saved to {local_path} ({len(response.content):,} bytes)")
            return True

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Failed to download {url}: {e}")
            return False
        except Exception as e:
            print(f"  [ERROR] Error saving {local_path}: {e}")
            return False

    def download_dataset(self, dataset_name: str, date: str):
        """Download all file types for a specific dataset"""
        print(f"\n{'='*60}")
        print(f"Processing dataset: {dataset_name}")
        print(f"{'='*60}")

        # File types available for each dataset
        file_types = [
            "entities.ftm.json",     # FollowTheMoney format entities
            "names.txt",             # Simple name list
            "senzing.json",          # Senzing format
            "source.xls",            # Original source file
            "targets.nested.json",   # Nested target format
            "targets.simple.csv",    # Simple CSV format
            "statistics.json",       # Dataset statistics
            "index.json"            # Dataset index/metadata
        ]

        dataset_dir = self.base_path / "raw_data" / dataset_name
        dataset_dir.mkdir(parents=True, exist_ok=True)

        download_count = 0

        for file_type in file_types:
            url = f"{self.base_url}/{date}/{dataset_name}/{file_type}"
            local_path = dataset_dir / f"{date}_{file_type}"

            if self.download_file(url, local_path, f"{dataset_name}/{file_type}"):
                download_count += 1

            # Small delay between requests
            time.sleep(0.5)

        print(f"Downloaded {download_count}/{len(file_types)} files for {dataset_name}")
        return download_count

    def discover_available_datasets(self):
        """Attempt to discover what datasets are actually available"""
        date = self.get_latest_date()
        available_datasets = []

        print("Discovering available datasets...")

        for dataset in self.known_datasets:
            # Test if dataset exists by trying to download index.json
            test_url = f"{self.base_url}/{date}/{dataset}/index.json"

            try:
                response = self.session.head(test_url, timeout=10)
                if response.status_code == 200:
                    available_datasets.append(dataset)
                    print(f"  [OK] Found: {dataset}")
                else:
                    print(f"  [ERROR] Not found: {dataset} (HTTP {response.status_code})")
            except:
                print(f"  [ERROR] Error checking: {dataset}")

            time.sleep(0.2)  # Rate limiting

        return available_datasets

    def create_sanctions_database(self):
        """Create SQLite database for all sanctions data"""
        db_path = self.base_path / "processed" / "sanctions.db"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create main entities table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            dataset_name TEXT,
            name TEXT,
            entity_type TEXT,
            countries TEXT,
            birth_date TEXT,
            death_date TEXT,
            nationality TEXT,
            address TEXT,
            program TEXT,
            list_date TEXT,
            reason TEXT,
            raw_data TEXT,
            is_chinese_affiliated BOOLEAN DEFAULT 0
        )
        """)

        # Create aliases table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS aliases (
            entity_id TEXT,
            alias_name TEXT,
            alias_type TEXT,
            FOREIGN KEY (entity_id) REFERENCES entities(id)
        )
        """)

        # Create Chinese entities analysis table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chinese_analysis (
            entity_id TEXT PRIMARY KEY,
            confidence_score REAL,
            china_indicators TEXT,
            analysis_date TEXT,
            FOREIGN KEY (entity_id) REFERENCES entities(id)
        )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_dataset ON entities(dataset_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_chinese ON entities(is_chinese_affiliated)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alias_name ON aliases(alias_name)")

        conn.commit()
        conn.close()

        print(f"Created sanctions database: {db_path}")
        return db_path

    def analyze_chinese_entities(self, entity_data):
        """Analyze if an entity is Chinese-affiliated"""
        china_indicators = []
        confidence_score = 0.0

        name = entity_data.get('name', '').lower()
        countries = str(entity_data.get('countries', '')).lower()
        nationality = str(entity_data.get('nationality', '')).lower()
        address = str(entity_data.get('address', '')).lower()

        # Strong indicators (high confidence)
        if 'china' in countries or 'cn' in countries:
            china_indicators.append("Country: China")
            confidence_score += 0.4

        if 'chinese' in nationality or 'china' in nationality:
            china_indicators.append("Nationality: Chinese")
            confidence_score += 0.3

        if any(city in address for city in ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'hong kong']):
            china_indicators.append("Address in major Chinese city")
            confidence_score += 0.3

        # Medium indicators
        chinese_terms = ['ltd', 'limited', 'technology', 'industrial', 'group', 'corp', 'corporation']
        chinese_name_patterns = ['huawei', 'xiaomi', 'tencent', 'alibaba', 'baidu', 'zte', 'lenovo']

        if any(pattern in name for pattern in chinese_name_patterns):
            china_indicators.append("Known Chinese company pattern")
            confidence_score += 0.4

        # PRC, People's Republic references
        if 'people\'s republic' in (name + address + nationality):
            china_indicators.append("People's Republic reference")
            confidence_score += 0.5

        # Common Chinese business suffixes
        if name.endswith(('co ltd', 'co., ltd', '(china)', 'group co')):
            china_indicators.append("Chinese business naming pattern")
            confidence_score += 0.2

        return min(confidence_score, 1.0), china_indicators

    def process_entities_file(self, file_path: Path, dataset_name: str, db_path: Path):
        """Process a single entities file and load into database"""
        if not file_path.exists():
            return 0

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        processed_count = 0
        chinese_count = 0

        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    if 'targets.simple' in file_path.name:
                        # This might be a different format
                        data = json.load(f)
                    else:
                        # Process line by line for large files
                        for line_num, line in enumerate(f, 1):
                            if line.strip():
                                try:
                                    entity = json.loads(line)

                                    # Extract basic info
                                    entity_id = entity.get('id', f"{dataset_name}_{line_num}")
                                    name = entity.get('properties', {}).get('name', ['Unknown'])[0] if entity.get('properties', {}).get('name') else 'Unknown'

                                    # Analyze Chinese affiliation
                                    confidence, indicators = self.analyze_chinese_entities({
                                        'name': name,
                                        'countries': str(entity.get('properties', {}).get('country', [])),
                                        'nationality': str(entity.get('properties', {}).get('nationality', [])),
                                        'address': str(entity.get('properties', {}).get('address', []))
                                    })

                                    is_chinese = confidence > 0.3
                                    if is_chinese:
                                        chinese_count += 1

                                    # Insert entity
                                    cursor.execute("""
                                    INSERT OR REPLACE INTO entities
                                    (id, dataset_name, name, entity_type, countries, nationality,
                                     address, raw_data, is_chinese_affiliated)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        entity_id,
                                        dataset_name,
                                        name,
                                        entity.get('schema', 'Unknown'),
                                        str(entity.get('properties', {}).get('country', [])),
                                        str(entity.get('properties', {}).get('nationality', [])),
                                        str(entity.get('properties', {}).get('address', [])),
                                        json.dumps(entity),
                                        is_chinese
                                    ))

                                    # Insert Chinese analysis if applicable
                                    if is_chinese:
                                        cursor.execute("""
                                        INSERT OR REPLACE INTO chinese_analysis
                                        (entity_id, confidence_score, china_indicators, analysis_date)
                                        VALUES (?, ?, ?, ?)
                                        """, (
                                            entity_id,
                                            confidence,
                                            '; '.join(indicators),
                                            datetime.now().isoformat()
                                        ))

                                    processed_count += 1

                                    if processed_count % 1000 == 0:
                                        print(f"    Processed {processed_count} entities...")
                                        conn.commit()

                                except json.JSONDecodeError:
                                    continue
                                except Exception as e:
                                    print(f"    Error processing entity {line_num}: {e}")
                                    continue

            elif file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
                for idx, row in df.iterrows():
                    # Process CSV data
                    entity_id = f"{dataset_name}_{idx}"
                    name = str(row.get('name', 'Unknown'))

                    confidence, indicators = self.analyze_chinese_entities({
                        'name': name,
                        'countries': str(row.get('countries', '')),
                        'nationality': str(row.get('nationality', '')),
                        'address': str(row.get('address', ''))
                    })

                    is_chinese = confidence > 0.3
                    if is_chinese:
                        chinese_count += 1

                    cursor.execute("""
                    INSERT OR REPLACE INTO entities
                    (id, dataset_name, name, entity_type, is_chinese_affiliated)
                    VALUES (?, ?, ?, ?, ?)
                    """, (entity_id, dataset_name, name, 'CSV_Entity', is_chinese))

                    processed_count += 1

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        finally:
            conn.commit()
            conn.close()

        print(f"    Processed {processed_count} entities, {chinese_count} Chinese-affiliated")
        return processed_count

    def run_full_download(self):
        """Execute complete download and processing pipeline"""
        print("=" * 80)
        print("OpenSanctions Complete Download and Analysis")
        print("=" * 80)

        start_time = datetime.now()

        # Step 1: Discover available datasets
        available_datasets = self.discover_available_datasets()
        print(f"\nFound {len(available_datasets)} available datasets")

        # Step 2: Download all datasets
        date = self.get_latest_date()
        total_downloads = 0

        for dataset in available_datasets:
            downloaded = self.download_dataset(dataset, date)
            total_downloads += downloaded

        # Step 3: Create database
        db_path = self.create_sanctions_database()

        # Step 4: Process all downloaded data
        print(f"\n{'='*60}")
        print("Processing downloaded data into database...")
        print(f"{'='*60}")

        total_entities = 0

        for dataset in available_datasets:
            print(f"\nProcessing {dataset}...")
            dataset_dir = self.base_path / "raw_data" / dataset

            # Process entities files
            for pattern in ["*entities*.json", "*targets*.csv", "*targets*.json"]:
                for file_path in dataset_dir.glob(pattern):
                    entities_count = self.process_entities_file(file_path, dataset, db_path)
                    total_entities += entities_count

        # Step 5: Generate summary report
        self.generate_summary_report(db_path)

        end_time = datetime.now()
        duration = end_time - start_time

        print(f"\n{'='*80}")
        print("DOWNLOAD AND ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"Duration: {duration}")
        print(f"Total files downloaded: {total_downloads}")
        print(f"Total entities processed: {total_entities}")
        print(f"Database created: {db_path}")

    def generate_summary_report(self, db_path: Path):
        """Generate analysis summary of Chinese entities"""
        conn = sqlite3.connect(db_path)

        report_path = self.base_path / "analysis" / f"chinese_entities_report_{datetime.now().strftime('%Y%m%d')}.md"

        # Get statistics
        total_entities = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        chinese_entities = conn.execute("SELECT COUNT(*) FROM entities WHERE is_chinese_affiliated = 1").fetchone()[0]
        datasets_with_chinese = conn.execute("""
            SELECT dataset_name, COUNT(*) as count
            FROM entities
            WHERE is_chinese_affiliated = 1
            GROUP BY dataset_name
            ORDER BY count DESC
        """).fetchall()

        # Top Chinese entities by confidence
        top_entities = conn.execute("""
            SELECT e.name, e.dataset_name, ca.confidence_score, ca.china_indicators
            FROM entities e
            JOIN chinese_analysis ca ON e.id = ca.entity_id
            ORDER BY ca.confidence_score DESC
            LIMIT 50
        """).fetchall()

        # Generate report
        report = f"""# OpenSanctions Chinese Entities Analysis
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics

- **Total entities processed**: {total_entities:,}
- **Chinese-affiliated entities**: {chinese_entities:,} ({chinese_entities/total_entities*100:.2f}%)

## Chinese Entities by Dataset

| Dataset | Chinese Entities | Percentage |
|---------|------------------|------------|
"""

        for dataset, count in datasets_with_chinese:
            dataset_total = conn.execute("SELECT COUNT(*) FROM entities WHERE dataset_name = ?", (dataset,)).fetchone()[0]
            pct = count/dataset_total*100 if dataset_total > 0 else 0
            report += f"| {dataset} | {count:,} | {pct:.2f}% |\n"

        report += f"""

## Top 50 Chinese-Affiliated Entities (by confidence)

| Name | Dataset | Confidence | Indicators |
|------|---------|------------|------------|
"""

        for name, dataset, confidence, indicators in top_entities:
            report += f"| {name} | {dataset} | {confidence:.2f} | {indicators} |\n"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        conn.close()

        print(f"Summary report saved: {report_path}")
        print(f"Chinese entities found: {chinese_entities:,} out of {total_entities:,} total")

if __name__ == "__main__":
    # Initialize with your external drive path
    downloader = OpenSanctionsDownloader("F:/OSINT_Data/OpenSanctions")
    downloader.run_full_download()
