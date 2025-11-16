#!/usr/bin/env python3
"""
Extract ALL OpenAlex Data Using Cursor Pagination
Bypass the 10,000 record page limit
"""

import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time
import sqlite3

class OpenAlexCursorExtractor:
    def __init__(self):
        self.base_url = "https://api.openalex.org"
        self.output_dir = Path("data/openalex_chinese_research")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")

        # Technology topics with total counts
        self.tech_topics = {
            'semiconductors': {'id': 'T10995', 'total': 30026, 'have': 10000},
            'artificial_intelligence': {'id': 'T11490', 'total': 8929, 'have': 9046},
            'quantum_computing': {'id': 'T10116', 'total': 10635, 'have': 10000},
            'advanced_materials': {'id': 'T10466', 'total': 24339, 'have': 10000},
            '5g_wireless': {'id': 'T10103', 'total': 3160, 'have': 3315},
            'robotics': {'id': 'T10069', 'total': 48771, 'have': 10000},
            'biotechnology': {'id': 'T10178', 'total': 5198, 'have': 5384},
            'aerospace': {'id': 'T10924', 'total': 10425, 'have': 10000},
            'new_energy': {'id': 'T10302', 'total': 10870, 'have': 10000},
            'advanced_manufacturing': {'id': 'T10825', 'total': 27838, 'have': 10000}
        }

        self.stats = {}

    def get_works_with_cursor(self, topic_name, topic_id, already_have, total_available):
        """
        Extract works using cursor-based pagination (no 10K limit)
        """
        remaining = total_available - already_have

        if remaining <= 0:
            print(f"  Already complete!")
            return []

        print(f"  Need to extract: {remaining:,} more papers")
        print(f"  Using cursor pagination (no page limits)")

        works = []
        cursor = '*'  # Start cursor
        total_fetched = 0
        target = remaining

        # Build filter
        filter_str = f"authorships.countries:CN,topics.id:{topic_id},publication_year:2011-2025"

        # Skip already collected records by using cursor to advance
        # First, we need to skip past what we already have
        print(f"  Skipping first {already_have:,} records...")
        skip_cursor = '*'
        skip_count = 0

        while skip_count < already_have:
            url = f"{self.base_url}/works"
            params = {
                'filter': filter_str,
                'per-page': 200,
                'cursor': skip_cursor,
                'select': 'id'  # Minimal data for skipping
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'results' not in data or len(data['results']) == 0:
                    print(f"\n    Reached end while skipping")
                    return []

                skip_count += len(data['results'])
                skip_cursor = data['meta']['next_cursor']

                if skip_cursor is None:
                    print(f"\n    No more data available")
                    return []

                if skip_count % 2000 == 0:
                    print(f"    Skipped: {skip_count:,}/{already_have:,}", end='\r')

                time.sleep(0.1)

            except Exception as e:
                print(f"\n    Error while skipping: {str(e)[:100]}")
                return []

        print(f"\n  Starting extraction from cursor position {already_have:,}...")
        cursor = skip_cursor

        # Now extract new data
        while total_fetched < target:
            url = f"{self.base_url}/works"
            params = {
                'filter': filter_str,
                'per-page': 200,
                'cursor': cursor,
                'select': 'id,doi,title,publication_year,publication_date,type,cited_by_count,authorships,topics,primary_topic,abstract_inverted_index'
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'results' not in data or len(data['results']) == 0:
                    print(f"\n    No more results")
                    break

                works.extend(data['results'])
                total_fetched = len(works)

                # Get next cursor
                cursor = data['meta'].get('next_cursor')
                if cursor is None:
                    print(f"\n    Reached end of available data")
                    break

                # Progress
                progress = min(total_fetched / target * 100, 100)
                print(f"    Fetched: {total_fetched:,}/{target:,} [{progress:.1f}%]", end='\r')

                # Checkpoint every 2000
                if total_fetched % 2000 == 0 and total_fetched > 0:
                    print(f"\n    Checkpoint: {total_fetched:,} papers")
                    # Save intermediate results
                    if len(works) > 0:
                        df_checkpoint = self.process_works_to_dataframe(works, topic_name)
                        self.append_to_files(df_checkpoint, topic_name)
                        works = []  # Clear memory
                        total_fetched = 0  # Reset for next batch

                time.sleep(0.15)

            except Exception as e:
                print(f"\n    Error: {str(e)[:100]}")
                break

        print(f"\n    Extracted: {total_fetched:,} additional papers")
        return works

    def process_works_to_dataframe(self, works, topic_name):
        """Convert works to dataframe"""
        records = []

        for work in works:
            # Extract institutions and authors
            chinese_institutions = []
            chinese_authors = []
            international_institutions = []
            total_authors = 0

            for authorship in work.get('authorships', []):
                total_authors += 1
                author_name = authorship.get('author', {}).get('display_name', 'Unknown')

                for institution in authorship.get('institutions', []):
                    inst_name = institution.get('display_name', 'Unknown')
                    country = institution.get('country_code', '')

                    if country == 'CN':
                        if inst_name not in chinese_institutions:
                            chinese_institutions.append(inst_name)
                        if author_name not in chinese_authors:
                            chinese_authors.append(author_name)
                    elif country:
                        if inst_name not in international_institutions:
                            international_institutions.append(inst_name)

            primary_topic = work.get('primary_topic', {})
            has_abstract = work.get('abstract_inverted_index') is not None
            has_international = len(international_institutions) > 0
            collaboration_type = 'International' if has_international else 'Domestic'

            record = {
                'openalex_id': work.get('id', '').replace('https://openalex.org/', ''),
                'doi': work.get('doi', '').replace('https://doi.org/', '') if work.get('doi') else None,
                'title': work.get('title', ''),
                'publication_year': work.get('publication_year'),
                'publication_date': work.get('publication_date'),
                'type': work.get('type'),
                'cited_by_count': work.get('cited_by_count', 0),
                'primary_topic_name': primary_topic.get('display_name', ''),
                'primary_topic_score': primary_topic.get('score', 0),
                'technology_category': topic_name,
                'chinese_institutions_count': len(chinese_institutions),
                'chinese_institutions': '; '.join(chinese_institutions[:10]),
                'international_institutions_count': len(international_institutions),
                'international_institutions': '; '.join(international_institutions[:5]),
                'chinese_authors_count': len(chinese_authors),
                'total_authors': total_authors,
                'collaboration_type': collaboration_type,
                'has_abstract': has_abstract
            }

            records.append(record)

        return pd.DataFrame(records)

    def append_to_files(self, df, topic_name):
        """Append to existing CSV and database"""

        # Append to CSV
        csv_file = self.output_dir / f'{topic_name}_expanded.csv'

        if csv_file.exists():
            # Read existing, append new, save
            existing_df = pd.read_csv(csv_file)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            # Remove duplicates based on openalex_id
            combined_df = combined_df.drop_duplicates(subset=['openalex_id'], keep='first')
            combined_df.to_csv(csv_file, index=False)
            print(f"  Updated CSV: {len(combined_df):,} total papers")
        else:
            df.to_csv(csv_file, index=False)
            print(f"  Created CSV: {len(df):,} papers")

        # Append to database
        if self.db_path.exists():
            conn = sqlite3.connect(self.db_path)

            # Create temp table with new data
            df.to_sql('temp_new_papers', conn, if_exists='replace', index=False)

            # Insert only new records (avoid duplicates)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO research_papers_expanded
                SELECT * FROM temp_new_papers
                WHERE openalex_id NOT IN (SELECT openalex_id FROM research_papers_expanded)
            """)
            inserted = cursor.rowcount

            cursor.execute("DROP TABLE temp_new_papers")
            conn.commit()
            conn.close()

            print(f"  Appended to database: {inserted:,} new papers")

    def extract_complete_dataset(self):
        """Extract all remaining papers for all topics"""

        print("="*80)
        print("OPENALEX CURSOR-BASED EXTRACTION")
        print("Bypassing 10K pagination limit using cursors")
        print("="*80)

        # Update totals based on last run
        total_to_extract = sum(
            max(0, topic['total'] - topic['have'])
            for topic in self.tech_topics.values()
        )

        print(f"\nTotal papers to extract: {total_to_extract:,}")
        print(f"Estimated time: 30-45 minutes")
        print(f"Cost: $0.00 (free API)\n")

        grand_total_extracted = 0

        for topic_name, topic_info in self.tech_topics.items():
            topic_id = topic_info['id']
            total_available = topic_info['total']
            already_have = topic_info['have']

            remaining = total_available - already_have

            print(f"\n[{topic_name.upper().replace('_', ' ')}]")
            print(f"  Total available: {total_available:,}")
            print(f"  Already have: {already_have:,}")
            print(f"  Remaining: {remaining:,}")

            if remaining <= 0:
                print(f"  Status: COMPLETE")
                continue

            # Extract remaining works
            works = self.get_works_with_cursor(
                topic_name,
                topic_id,
                already_have,
                total_available
            )

            if len(works) > 0:
                # Process final batch
                df = self.process_works_to_dataframe(works, topic_name)
                self.append_to_files(df, topic_name)
                grand_total_extracted += len(df)

            # Save progress
            progress_file = self.output_dir / 'cursor_extraction_progress.json'
            with open(progress_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'topic': topic_name,
                    'extracted': grand_total_extracted
                }, f, indent=2)

        print("\n" + "="*80)
        print("EXTRACTION COMPLETE")
        print("="*80)
        print(f"\nTotal new papers extracted: {grand_total_extracted:,}")

def main():
    print("="*80)
    print("OPENALEX CURSOR-BASED COMPLETE EXTRACTION")
    print("="*80)
    print("\nUsing cursor pagination to bypass 10K page limit")
    print("This will extract ALL remaining data")
    print("="*80)

    extractor = OpenAlexCursorExtractor()
    extractor.extract_complete_dataset()

    print("\n" + "="*80)
    print("ALL EXTRACTIONS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
