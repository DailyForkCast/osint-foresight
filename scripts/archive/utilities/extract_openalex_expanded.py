#!/usr/bin/env python3
"""
Extract Expanded OpenAlex Chinese Research Data
Get 10,000+ papers per topic (vs 200 in initial extraction)
"""

import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time
import sqlite3

class OpenAlexExpandedExtractor:
    def __init__(self):
        self.base_url = "https://api.openalex.org"
        self.output_dir = Path("data/openalex_chinese_research")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")

        # Technology topics matching MIC2025 priorities
        self.tech_topics = {
            'semiconductors': 'T10995',
            'artificial_intelligence': 'T11490',
            'quantum_computing': 'T10116',
            'advanced_materials': 'T10466',
            '5g_wireless': 'T10103',
            'robotics': 'T10069',
            'biotechnology': 'T10178',
            'aerospace': 'T10924',
            'new_energy': 'T10302',
            'advanced_manufacturing': 'T10825'
        }

        self.stats = {}

    def get_works_paginated(self, country_code='CN', topic_id=None,
                           year_start=2011, year_end=2025,
                           per_page=200, max_results=10000):
        """
        Extract works with pagination support
        """
        works = []
        page = 1
        total_fetched = 0

        # Build filter
        filters = [f"authorships.countries:{country_code}"]
        if topic_id:
            filters.append(f"topics.id:{topic_id}")
        filters.append(f"publication_year:{year_start}-{year_end}")

        filter_str = ",".join(filters)

        print(f"  Fetching works with filter: {filter_str}")
        print(f"  Target: {max_results:,} papers")

        while total_fetched < max_results:
            url = f"{self.base_url}/works"
            params = {
                'filter': filter_str,
                'per-page': per_page,
                'page': page,
                'select': 'id,doi,title,publication_year,publication_date,type,cited_by_count,authorships,topics,primary_topic,abstract_inverted_index'
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'results' not in data or len(data['results']) == 0:
                    print(f"\n    No more results at page {page}")
                    break

                works.extend(data['results'])
                total_fetched = len(works)

                # Progress indicator
                progress = min(total_fetched / max_results * 100, 100)
                print(f"    Page {page}: +{len(data['results'])} papers (total: {total_fetched:,}/{max_results:,}) [{progress:.1f}%]", end='\r')

                # Save checkpoint every 2000 records
                if total_fetched % 2000 == 0 and total_fetched > 0:
                    print(f"\n    Checkpoint: {total_fetched:,} papers saved")

                page += 1

                # Respectful delay
                time.sleep(0.15)

            except Exception as e:
                print(f"\n    Error on page {page}: {str(e)[:100]}")
                break

        print(f"\n    Final total: {total_fetched:,} papers")
        return works

    def process_works_to_dataframe(self, works, topic_name):
        """
        Convert works to structured dataframe
        """
        records = []

        for work in works:
            # Extract Chinese institutions and authors
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

            # Get primary topic
            primary_topic = work.get('primary_topic', {})

            # Extract abstract (if available)
            has_abstract = work.get('abstract_inverted_index') is not None

            # Determine collaboration type
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

    def extract_expanded_dataset(self, topic_name, topic_id, max_results=10000):
        """
        Extract expanded dataset for a single topic
        """
        print(f"\n[{topic_name.upper().replace('_', ' ')}]")
        print(f"  Topic ID: {topic_id}")

        works = self.get_works_paginated(
            country_code='CN',
            topic_id=topic_id,
            year_start=2011,
            year_end=2025,
            max_results=max_results
        )

        if len(works) == 0:
            print(f"  No results found")
            return None

        # Process to dataframe
        df = self.process_works_to_dataframe(works, topic_name)

        # Save CSV
        output_file = self.output_dir / f'{topic_name}_expanded.csv'
        df.to_csv(output_file, index=False)

        print(f"  Saved: {output_file}")
        print(f"  Records: {len(df):,}")
        print(f"  Date range: {df['publication_year'].min()}-{df['publication_year'].max()}")
        print(f"  International collaboration: {(df['collaboration_type']=='International').sum():,} papers ({(df['collaboration_type']=='International').sum()/len(df)*100:.1f}%)")

        self.stats[topic_name] = {
            'records': len(df),
            'year_min': int(df['publication_year'].min()),
            'year_max': int(df['publication_year'].max()),
            'avg_citations': float(df['cited_by_count'].mean()),
            'international_pct': float((df['collaboration_type']=='International').sum()/len(df)*100)
        }

        return df

    def append_to_database(self, df, topic_name):
        """
        Append expanded data to existing database
        """
        if not self.db_path.exists():
            print(f"  [!] Database not found at {self.db_path}")
            return

        print(f"  Appending to database...")

        conn = sqlite3.connect(self.db_path)

        # Append to research_papers table
        df.to_sql('research_papers_expanded', conn, if_exists='append', index=False)

        conn.close()

        print(f"  [OK] Appended {len(df):,} records to database")

    def run_expanded_extraction(self, max_results_per_topic=10000):
        """
        Run expanded extraction for all topics
        """
        print("="*80)
        print("OPENALEX EXPANDED EXTRACTION")
        print(f"Target: {max_results_per_topic:,} papers per topic")
        print("="*80)

        all_data = []

        for topic_name, topic_id in self.tech_topics.items():
            df = self.extract_expanded_dataset(topic_name, topic_id, max_results_per_topic)

            if df is not None:
                all_data.append(df)

                # Append to database incrementally
                self.append_to_database(df, topic_name)

                # Save progress
                progress_file = self.output_dir / 'extraction_progress.json'
                with open(progress_file, 'w') as f:
                    json.dump(self.stats, f, indent=2)

        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)

            output_file = self.output_dir / 'chinese_research_expanded_all.csv'
            combined_df.to_csv(output_file, index=False)

            print("\n" + "="*80)
            print("EXTRACTION COMPLETE")
            print("="*80)
            print(f"\nTotal records: {len(combined_df):,}")
            print(f"Output file: {output_file}")

            # Summary statistics
            print("\n" + "="*80)
            print("SUMMARY BY TOPIC")
            print("="*80)

            for topic in self.tech_topics.keys():
                if topic in self.stats:
                    stats = self.stats[topic]
                    print(f"\n{topic}:")
                    print(f"  Records: {stats['records']:,}")
                    print(f"  Year range: {stats['year_min']}-{stats['year_max']}")
                    print(f"  Avg citations: {stats['avg_citations']:.1f}")
                    print(f"  International collab: {stats['international_pct']:.1f}%")

            # Save final summary
            summary = {
                'extraction_date': datetime.now().isoformat(),
                'total_records': len(combined_df),
                'topics': len(self.stats),
                'max_per_topic': max_results_per_topic,
                'topic_stats': self.stats,
                'cost': '$0.00 (free API)'
            }

            summary_file = self.output_dir / 'expanded_extraction_summary.json'
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)

            print(f"\n\nSummary saved: {summary_file}")

            return combined_df
        else:
            print("\n[!] No data extracted")
            return None

def main():
    print("="*80)
    print("OPENALEX EXPANDED EXTRACTION")
    print("="*80)
    print("\nThis will extract up to 10,000 papers per topic (vs 200 initial)")
    print("Estimated time: 15-20 minutes")
    print("Cost: $0.00 (free unlimited API)")

    extractor = OpenAlexExpandedExtractor()

    # Run extraction with 10,000 papers per topic
    df = extractor.run_expanded_extraction(max_results_per_topic=10000)

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Review expanded CSV files in data/openalex_chinese_research/")
    print("2. Check database: F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")
    print("3. Query expanded data:")
    print("   SELECT * FROM research_papers_expanded LIMIT 100;")
    print("\n4. Analyze international collaborations")
    print("5. Cross-reference with patent data")

if __name__ == "__main__":
    main()
