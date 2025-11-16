#!/usr/bin/env python3
"""
Extract ALL OpenAlex Data Using Year-Based Chunking
Break large topics into year ranges to stay under 10K pagination limit
"""

import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time
import sqlite3

class OpenAlexYearChunkExtractor:
    def __init__(self):
        self.base_url = "https://api.openalex.org"
        self.output_dir = Path("data/openalex_chinese_research")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")

        # Technology topics with their needs
        self.tech_topics = {
            'semiconductors': {'id': 'T10995', 'total': 30026, 'have': 10000, 'remaining': 20026},
            'quantum_computing': {'id': 'T10116', 'total': 10635, 'have': 10000, 'remaining': 635},
            'advanced_materials': {'id': 'T10466', 'total': 24339, 'have': 10000, 'remaining': 14339},
            'robotics': {'id': 'T10069', 'total': 48771, 'have': 10000, 'remaining': 38771},
            'aerospace': {'id': 'T10924', 'total': 10425, 'have': 10000, 'remaining': 425},
            'new_energy': {'id': 'T10302', 'total': 10870, 'have': 10000, 'remaining': 870},
            'advanced_manufacturing': {'id': 'T10825', 'total': 27838, 'have': 10000, 'remaining': 17838}
        }

        self.stats = {}

    def get_year_distribution(self, topic_id):
        """
        Check how many papers exist per year for a topic
        """
        print(f"  Checking year distribution...")

        year_counts = {}

        for year in range(2011, 2026):
            filter_str = f"authorships.countries:CN,topics.id:{topic_id},publication_year:{year}"

            url = f"{self.base_url}/works"
            params = {
                'filter': filter_str,
                'per-page': 1
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                count = data.get('meta', {}).get('count', 0)
                year_counts[year] = count

                time.sleep(0.1)

            except Exception as e:
                print(f"    Error checking year {year}: {str(e)[:50]}")
                year_counts[year] = 0

        return year_counts

    def create_year_chunks(self, year_counts, max_per_chunk=9000):
        """
        Group years into chunks that stay under 10K limit
        """
        chunks = []
        current_chunk = []
        current_total = 0

        for year, count in sorted(year_counts.items()):
            if count == 0:
                continue

            # If adding this year would exceed limit, start new chunk
            if current_total + count > max_per_chunk and current_chunk:
                chunks.append(current_chunk)
                current_chunk = [year]
                current_total = count
            else:
                current_chunk.append(year)
                current_total += count

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def extract_year_range(self, topic_id, years, max_results=10000):
        """
        Extract all papers for a specific year range
        """
        if len(years) == 1:
            year_filter = str(years[0])
        else:
            year_filter = f"{min(years)}-{max(years)}"

        filter_str = f"authorships.countries:CN,topics.id:{topic_id},publication_year:{year_filter}"

        works = []
        page = 1

        while len(works) < max_results:
            url = f"{self.base_url}/works"
            params = {
                'filter': filter_str,
                'per-page': 200,
                'page': page,
                'select': 'id,doi,title,publication_year,publication_date,type,cited_by_count,authorships,topics,primary_topic,abstract_inverted_index'
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'results' not in data or len(data['results']) == 0:
                    break

                works.extend(data['results'])

                print(f"      Years {year_filter}: {len(works):,} papers", end='\r')

                page += 1
                time.sleep(0.15)

            except Exception as e:
                print(f"\n      Error on page {page}: {str(e)[:100]}")
                break

        print(f"      Years {year_filter}: {len(works):,} papers (complete)")
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

    def append_to_database(self, df, topic_name):
        """Append to database, avoiding duplicates"""

        if not self.db_path.exists():
            print(f"  [!] Database not found")
            return 0

        conn = sqlite3.connect(self.db_path)

        # Create temp table with new data
        df.to_sql('temp_new_papers', conn, if_exists='replace', index=False)

        # Insert only new records
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

        return inserted

    def update_csv_file(self, df, topic_name):
        """Update CSV file, avoiding duplicates"""

        csv_file = self.output_dir / f'{topic_name}_expanded.csv'

        if csv_file.exists():
            existing_df = pd.read_csv(csv_file)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            # Remove duplicates
            combined_df = combined_df.drop_duplicates(subset=['openalex_id'], keep='first')
            combined_df.to_csv(csv_file, index=False)
            return len(combined_df)
        else:
            df.to_csv(csv_file, index=False)
            return len(df)

    def extract_topic_complete(self, topic_name, topic_info):
        """
        Extract all remaining data for a topic using year chunking
        """
        topic_id = topic_info['id']
        remaining = topic_info['remaining']

        print(f"\n[{topic_name.upper().replace('_', ' ')}]")
        print(f"  Need to extract: {remaining:,} papers")

        # Get year distribution
        year_counts = self.get_year_distribution(topic_id)

        # Show distribution
        print(f"  Year distribution:")
        for year, count in sorted(year_counts.items()):
            if count > 0:
                print(f"    {year}: {count:,} papers")

        # Create year chunks
        chunks = self.create_year_chunks(year_counts, max_per_chunk=9000)

        print(f"  Split into {len(chunks)} chunks to stay under 10K limit")

        all_works = []

        for i, years in enumerate(chunks, 1):
            print(f"  Chunk {i}/{len(chunks)}: years {min(years)}-{max(years)}")

            works = self.extract_year_range(topic_id, years)
            all_works.extend(works)

            print(f"    Chunk total: {len(works):,} papers")

        if len(all_works) == 0:
            print(f"  No new data extracted")
            return

        print(f"\n  Processing {len(all_works):,} papers...")
        df = self.process_works_to_dataframe(all_works, topic_name)

        # Update database
        print(f"  Updating database...")
        inserted = self.append_to_database(df, topic_name)
        print(f"  Added {inserted:,} new papers to database")

        # Update CSV
        print(f"  Updating CSV...")
        total_csv = self.update_csv_file(df, topic_name)
        print(f"  CSV now has {total_csv:,} total papers")

        self.stats[topic_name] = {
            'extracted': len(all_works),
            'inserted_db': inserted,
            'total_csv': total_csv
        }

    def extract_all_remaining(self):
        """
        Extract all remaining data for all topics
        """

        print("="*80)
        print("OPENALEX YEAR-CHUNKED EXTRACTION")
        print("Breaking large topics into year ranges to bypass 10K limit")
        print("="*80)

        total_remaining = sum(t['remaining'] for t in self.tech_topics.values())
        print(f"\nTotal papers to extract: {total_remaining:,}")
        print(f"Topics to process: {len(self.tech_topics)}")
        print(f"Estimated time: 25-35 minutes")
        print(f"Cost: $0.00 (free API)\n")

        for topic_name, topic_info in self.tech_topics.items():
            try:
                self.extract_topic_complete(topic_name, topic_info)
            except Exception as e:
                print(f"\n  [ERROR] {topic_name}: {str(e)[:200]}")
                continue

        # Final summary
        print("\n" + "="*80)
        print("EXTRACTION COMPLETE")
        print("="*80)

        total_extracted = sum(s['extracted'] for s in self.stats.values())
        total_inserted = sum(s['inserted_db'] for s in self.stats.values())

        print(f"\nTotal papers extracted: {total_extracted:,}")
        print(f"Total new papers in database: {total_inserted:,}")

        for topic, stats in self.stats.items():
            print(f"\n{topic}:")
            print(f"  Extracted: {stats['extracted']:,}")
            print(f"  New in DB: {stats['inserted_db']:,}")
            print(f"  Total in CSV: {stats['total_csv']:,}")

        # Save summary
        summary_file = self.output_dir / 'year_chunk_extraction_summary.json'
        with open(summary_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_extracted': total_extracted,
                'total_inserted': total_inserted,
                'topics': self.stats
            }, f, indent=2)

        print(f"\nSummary saved: {summary_file}")

def main():
    print("="*80)
    print("OPENALEX YEAR-CHUNKED COMPLETE EXTRACTION")
    print("="*80)
    print("\nUsing year-based chunking to efficiently extract all remaining data")
    print("Each chunk stays under 10K records to avoid pagination limits")
    print("="*80)

    extractor = OpenAlexYearChunkExtractor()
    extractor.extract_all_remaining()

    print("\n" + "="*80)
    print("ALL EXTRACTIONS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
