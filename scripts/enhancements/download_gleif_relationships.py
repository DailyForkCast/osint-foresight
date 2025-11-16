#!/usr/bin/env python3
"""
GLEIF Relationships Downloader
Downloads corporate ownership relationship data from GLEIF
"""

import sqlite3
import requests
import gzip
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GLEIFRelationshipsDownloader:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.download_dir = Path("F:/OSINT_DATA/GLEIF")
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # GLEIF Golden Copy files
        self.sources = {
            'relationships_level1': {
                'url': 'https://goldencopy.gleif.org/api/v2/golden-copies/publishes/rr/golden-copy-rr-latest.json.gz',
                'description': 'Level 1 Relationships (Direct Parents)'
            },
            'relationships_level2': {
                'url': 'https://goldencopy.gleif.org/api/v2/golden-copies/publishes/repex/golden-copy-repex-latest.json.gz',
                'description': 'Level 2 Relationships (Reporting Exceptions)'
            }
        }

    def download_relationships(self, relationship_type: str):
        """Download GLEIF relationship data"""
        logger.info(f"Downloading {relationship_type}...")

        source = self.sources[relationship_type]
        url = source['url']

        try:
            logger.info(f"Fetching from: {url}")
            response = requests.get(url, stream=True, timeout=300)

            if response.status_code == 200:
                # Save compressed file
                gz_file = self.download_dir / f"{relationship_type}.json.gz"
                json_file = self.download_dir / f"{relationship_type}.json"

                with open(gz_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                logger.info(f"Downloaded {gz_file.stat().st_size / (1024**2):.1f} MB")

                # Decompress
                logger.info("Decompressing...")
                with gzip.open(gz_file, 'rb') as f_in:
                    with open(json_file, 'wb') as f_out:
                        f_out.write(f_in.read())

                logger.info(f"Decompressed to {json_file.stat().st_size / (1024**2):.1f} MB")

                # Clean up compressed file
                gz_file.unlink()

                return json_file
            else:
                logger.error(f"Download failed with status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error downloading {relationship_type}: {e}")
            return None

    def parse_relationships(self, json_file: Path, relationship_type: str):
        """Parse GLEIF JSON and extract relationships"""
        logger.info(f"Parsing {json_file}...")

        relationships = []

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                # GLEIF JSON is NDJSON (newline-delimited JSON)
                line_count = 0
                for line in f:
                    line_count += 1

                    if line_count % 10000 == 0:
                        logger.info(f"Processed {line_count:,} relationships...")

                    try:
                        data = json.loads(line)

                        # Extract relationship details
                        relationship = {
                            'relationship_type': relationship_type,
                            'start_lei': data.get('Relationship', {}).get('StartNode', {}).get('NodeID'),
                            'end_lei': data.get('Relationship', {}).get('EndNode', {}).get('NodeID'),
                            'relationship_status': data.get('Registration', {}).get('RegistrationStatus'),
                            'relationship_category': data.get('Relationship', {}).get('RelationshipType'),
                            'relationship_period_start': data.get('Relationship', {}).get('StartDate'),
                            'relationship_period_end': data.get('Relationship', {}).get('EndDate'),
                            'last_update': data.get('Registration', {}).get('LastUpdateDate'),
                            'validation_sources': data.get('Registration', {}).get('ValidationSources'),
                            'data_hash': f"{relationship_type}_{line_count}"
                        }

                        relationships.append(relationship)

                        # Limit to sample for quick testing (remove for full import)
                        if line_count >= 10000:  # Sample 10K relationships
                            logger.info("Sample limit reached (10K relationships)")
                            break

                    except json.JSONDecodeError:
                        continue

                logger.info(f"Parsed {len(relationships):,} relationships")
                return relationships

        except Exception as e:
            logger.error(f"Error parsing relationships: {e}")
            return []

    def populate_database(self, relationships):
        """Populate gleif_relationships table"""
        if not relationships:
            logger.warning("No relationships to populate")
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute('DELETE FROM gleif_relationships')
        logger.info("Cleared existing relationships data")

        # Insert new data
        inserted = 0
        for rel in relationships:
            try:
                cursor.execute("""
                    INSERT INTO gleif_relationships (
                        relationship_type, start_lei, end_lei, relationship_status,
                        relationship_category, relationship_period_start, relationship_period_end,
                        last_update, validation_sources, data_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rel['relationship_type'],
                    rel['start_lei'],
                    rel['end_lei'],
                    rel['relationship_status'],
                    rel['relationship_category'],
                    rel['relationship_period_start'],
                    rel['relationship_period_end'],
                    rel['last_update'],
                    rel['validation_sources'],
                    rel['data_hash']
                ))
                inserted += 1

                if inserted % 1000 == 0:
                    conn.commit()
                    logger.info(f"Inserted {inserted:,} relationships...")

            except Exception as e:
                logger.error(f"Error inserting relationship: {e}")

        conn.commit()
        conn.close()

        logger.info(f"Successfully inserted {inserted:,} relationships")
        return inserted

    def generate_summary(self):
        """Generate summary of relationships"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Get statistics
        total = conn.execute('SELECT COUNT(*) FROM gleif_relationships').fetchone()[0]

        # By type
        by_type = conn.execute("""
            SELECT relationship_type, COUNT(*) as count
            FROM gleif_relationships
            GROUP BY relationship_type
        """).fetchall()

        # By category
        by_category = conn.execute("""
            SELECT relationship_category, COUNT(*) as count
            FROM gleif_relationships
            GROUP BY relationship_category
            ORDER BY count DESC
            LIMIT 10
        """).fetchall()

        # Active vs inactive
        active = conn.execute("""
            SELECT COUNT(*) FROM gleif_relationships
            WHERE relationship_status = 'ACTIVE'
        """).fetchone()[0]

        conn.close()

        logger.info(f"\n{'='*80}")
        logger.info(f"GLEIF Relationships Summary")
        logger.info(f"{'='*80}")
        logger.info(f"Total relationships: {total:,}")
        logger.info(f"Active relationships: {active:,} ({active/total*100 if total > 0 else 0:.1f}%)")
        logger.info(f"\nBy Type:")
        for row in by_type:
            logger.info(f"  {row['relationship_type']}: {row['count']:,}")
        logger.info(f"\nTop 10 Categories:")
        for row in by_category:
            logger.info(f"  {row['relationship_category']}: {row['count']:,}")
        logger.info(f"{'='*80}")

    def run(self):
        """Execute the download and population process"""
        logger.info("Starting GLEIF Relationships download...")

        all_relationships = []

        # Download Level 1 (Direct Parents)
        json_file = self.download_relationships('relationships_level1')
        if json_file and json_file.exists():
            relationships = self.parse_relationships(json_file, 'LEVEL1_DIRECT_PARENT')
            all_relationships.extend(relationships)

        # Note: Level 2 download disabled for now (very large file, sample only for testing)
        # json_file = self.download_relationships('relationships_level2')
        # if json_file and json_file.exists():
        #     relationships = self.parse_relationships(json_file, 'LEVEL2_REPORTING_EXCEPTION')
        #     all_relationships.extend(relationships)

        # Populate database
        if all_relationships:
            inserted = self.populate_database(all_relationships)
            self.generate_summary()
            return inserted
        else:
            logger.error("No relationships data available")
            return 0


if __name__ == "__main__":
    downloader = GLEIFRelationshipsDownloader()
    downloader.run()
