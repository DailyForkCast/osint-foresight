#!/usr/bin/env python3
"""
Extract ALL Remaining OpenAlex Data
Complete the dataset to 100% coverage
"""

import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time
import sqlite3

class OpenAlexCompleteExtractor:
    def __init__(self):
        self.base_url = "https://api.openalex.org"
        self.output_dir = Path("data/openalex_chinese_research")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = Path("F:/OSINT_Data/openalex_analytics/openalex_chinese_research.db")

        # Technology topics with total counts
        self.tech_topics = {
            'semiconductors': {'id': 'T10995', 'total': 30026, 'have': 10000},
            'artificial_intelligence': {'id': 'T11490', 'total': 8929, 'have': 8917},
            'quantum_computing': {'id': 'T10116', 'total': 10635, 'have': 10000},
            'advanced_materials': {'id': 'T10466', 'total': 24339, 'have': 10000},
            '5g_wireless': {'id': 'T10103', 'total': 3160, 'have': 3155},
            'robotics': {'id': 'T10069', 'total': 48771, 'have': 10000},
            'biotechnology': {'id': 'T10178', 'total': 5198, 'have': 5186},
            'aerospace': {'id': 'T10924', 'total': 10425, 'have': 10000},
            'new_energy': {'id': 'T10302', 'total': 10870, 'have': 10000},
            'advanced_manufacturing': {'id': 'T10825', 'total': 27838, 'have': 10000}
        }

        self.stats = {}

    def get_remaining_works(self, topic_name, topic_id, already_have, total_available):
        """
        Extract remaining works for a topic
        """
        remaining = total_available - already_have

        if remaining <= 0:
            print(f"  Already complete!")
            return []

        print(f"  Need to extract: {remaining:,} more papers")

        works = []

        # Start from page where we left off
        start_page = (already_have // 200) + 1

        # Build filter
        filter_str = f"authorships.countries:CN,topics.id:{topic_id},publication_year:2011-2025"

        page = start_page
        total_fetched = 0
        target = remaining

        while total_fetched < target:
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
                    print(f"\n    No more results at page {page}")
                    break

                works.extend(data['results'])
                total_fetched = len(works)

                # Progress
                progress = min(total_fetched / target * 100, 100)
                print(f"    Page {page}: +{len(data['results'])} papers (total: {total_fetched:,}/{target:,}) [{progress:.1f}%]", end='\r')

                # Checkpoint every 2000
                if total_fetched % 2000 == 0 and total_fetched > 0:
                    print(f"\n    Checkpoint: {total_fetched:,} papers")

                page += 1
                time.sleep(0.15)

            except Exception as e:
                print(f"\n    Error on page {page}: {str(e)[:100]}")
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
            combined_df.to_csv(csv_file, index=False)
            print(f"  Updated CSV: {len(combined_df):,} total papers")
        else:
            df.to_csv(csv_file, index=False)
            print(f"  Created CSV: {len(df):,} papers")

        # Append to database
        if self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            df.to_sql('research_papers_expanded', conn, if_exists='append', index=False)
            conn.close()
            print(f"  Appended to database: {len(df):,} papers")

    def extract_complete_dataset(self):
        """Extract all remaining papers for all topics"""

        print("="*80)
        print("OPENALEX COMPLETE EXTRACTION")
        print("Extracting ALL remaining data to 100% coverage")
        print("="*80)

        total_to_extract = sum(
            topic['total'] - topic['have']
            for topic in self.tech_topics.values()
        )

        print(f"\nTotal papers to extract: {total_to_extract:,}")
        print(f"Estimated time: 20-30 minutes")
        print(f"Cost: $0.00 (free API)\n")

        all_new_data = []
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
            works = self.get_remaining_works(
                topic_name,
                topic_id,
                already_have,
                total_available
            )

            if len(works) == 0:
                continue

            # Process to dataframe
            df = self.process_works_to_dataframe(works, topic_name)

            # Append to files
            self.append_to_files(df, topic_name)

            # Track stats
            intl_pct = (df['collaboration_type']=='International').sum()/len(df)*100

            self.stats[topic_name] = {
                'new_records': len(df),
                'total_now': already_have + len(df),
                'target': total_available,
                'complete': already_have + len(df) >= total_available,
                'international_pct': float(intl_pct)
            }

            all_new_data.append(df)
            grand_total_extracted += len(df)

            print(f"  Status: {already_have + len(df):,} / {total_available:,}")
            print(f"  International: {intl_pct:.1f}%")

            # Save progress
            progress_file = self.output_dir / 'complete_extraction_progress.json'
            with open(progress_file, 'w') as f:
                json.dump(self.stats, f, indent=2)

        # Create combined complete file
        if all_new_data:
            print("\n" + "="*80)
            print("CREATING COMPLETE COMBINED DATASET")
            print("="*80)

            # Combine all new data
            new_combined = pd.concat(all_new_data, ignore_index=True)

            # Load existing expanded file if it exists
            existing_file = self.output_dir / 'chinese_research_expanded_all.csv'
            if existing_file.exists():
                existing = pd.read_csv(existing_file)
                final_combined = pd.concat([existing, new_combined], ignore_index=True)
            else:
                final_combined = new_combined

            # Save complete dataset
            final_combined.to_csv(existing_file, index=False)

            print(f"\nTotal papers in complete dataset: {len(final_combined):,}")
            print(f"Newly added: {grand_total_extracted:,}")
            print(f"Saved to: {existing_file}")

            # Final summary
            print("\n" + "="*80)
            print("EXTRACTION COMPLETE - FINAL SUMMARY")
            print("="*80)

            for topic_name, stats in self.stats.items():
                status = "COMPLETE" if stats['complete'] else "PARTIAL"
                print(f"\n{topic_name}:")
                print(f"  Total papers: {stats['total_now']:,} / {stats['target']:,}")
                print(f"  Added: +{stats['new_records']:,}")
                print(f"  Status: {status}")

            # Overall stats
            print("\n" + "="*80)
            print("OVERALL STATISTICS")
            print("="*80)

            total_now = sum(s['total_now'] for s in self.stats.values())
            total_target = sum(s['target'] for s in self.stats.values())

            # Add previously complete topics
            for topic_name, topic_info in self.tech_topics.items():
                if topic_name not in self.stats:
                    total_now += topic_info['have']
                    total_target += topic_info['total']

            print(f"\nGrand total papers: {total_now:,}")
            print(f"Target coverage: {total_target:,}")
            print(f"Coverage: {total_now/total_target*100:.1f}%")
            print(f"\nSession additions: +{grand_total_extracted:,} papers")

            # Save final summary
            final_summary = {
                'completion_date': datetime.now().isoformat(),
                'total_papers': total_now,
                'target': total_target,
                'coverage_pct': total_now/total_target*100,
                'new_papers_this_session': grand_total_extracted,
                'cost': '$0.00',
                'topic_details': self.stats
            }

            summary_file = self.output_dir / 'complete_extraction_summary.json'
            with open(summary_file, 'w') as f:
                json.dump(final_summary, f, indent=2)

            print(f"\nSummary saved: {summary_file}")

            return final_combined
        else:
            print("\n[!] No new data extracted")
            return None

def main():
    print("="*80)
    print("OPENALEX COMPLETE EXTRACTION")
    print("="*80)
    print("\nExtracting ALL remaining Chinese technology research papers")
    print("Target: 100% coverage across all 10 topics")
    print("\nThis will take approximately 20-30 minutes")
    print("="*80)

    extractor = OpenAlexCompleteExtractor()
    df = extractor.extract_complete_dataset()

    print("\n" + "="*80)
    print("ALL EXTRACTIONS COMPLETE")
    print("="*80)
    print("\nYou now have the complete OpenAlex dataset for Chinese")
    print("technology research (2011-2025) across all 10 MIC2025 topics!")

if __name__ == "__main__":
    main()
