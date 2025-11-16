#!/usr/bin/env python3
"""
Extract Chinese Technology Research from OpenAlex
Free API with no rate limits - comprehensive academic publication data
"""

import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time

class OpenAlexExtractor:
    def __init__(self):
        self.base_url = "https://api.openalex.org"
        self.output_dir = Path("data/openalex_chinese_research")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Technology topics matching MIC2025 priorities
        self.tech_topics = {
            'semiconductors': 'T10995',  # Semiconductor devices
            'artificial_intelligence': 'T11490',  # Machine learning
            'quantum_computing': 'T10116',  # Quantum information
            'advanced_materials': 'T10466',  # Materials science
            '5g_wireless': 'T10103',  # Wireless communications
            'robotics': 'T10069',  # Robotics
            'biotechnology': 'T10178',  # Biotechnology
            'aerospace': 'T10924',  # Aerospace engineering
            'new_energy': 'T10302',  # Renewable energy
            'advanced_manufacturing': 'T10825'  # Manufacturing
        }

        self.stats = {}

    def get_works_by_country_and_topic(self, country_code='CN', topic_id=None,
                                       year_start=2011, year_end=2025,
                                       per_page=200, max_results=10000):
        """
        Extract works by country and topic
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

        while total_fetched < max_results:
            url = f"{self.base_url}/works"
            params = {
                'filter': filter_str,
                'per-page': per_page,
                'page': page,
                'select': 'id,doi,title,publication_year,publication_date,type,cited_by_count,authorships,topics,primary_topic'
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'results' not in data or len(data['results']) == 0:
                    break

                works.extend(data['results'])
                total_fetched = len(works)

                print(f"    Page {page}: {len(data['results'])} results (total: {total_fetched})", end='\r')

                # Check if we have more pages
                if 'meta' in data and 'next_cursor' not in data['meta']:
                    break

                page += 1

                # Small delay to be respectful (even though no rate limit)
                time.sleep(0.1)

            except Exception as e:
                print(f"\n    Error on page {page}: {str(e)[:100]}")
                break

        print(f"\n    Total fetched: {total_fetched}")
        return works

    def extract_chinese_research_by_topic(self):
        """
        Extract Chinese research across all technology topics
        """
        print("\n" + "="*80)
        print("EXTRACTING CHINESE TECHNOLOGY RESEARCH - BY TOPIC")
        print("="*80)

        all_topic_data = []

        for topic_name, topic_id in self.tech_topics.items():
            print(f"\n[{topic_name.upper().replace('_', ' ')}]")
            print(f"  Topic ID: {topic_id}")

            works = self.get_works_by_country_and_topic(
                country_code='CN',
                topic_id=topic_id,
                year_start=2011,
                year_end=2025,
                max_results=5000  # Limit per topic
            )

            if len(works) == 0:
                print(f"  No results found")
                continue

            # Process works into structured data
            for work in works:
                # Extract Chinese institutions
                chinese_institutions = []
                chinese_authors = []
                total_authors = 0

                for authorship in work.get('authorships', []):
                    total_authors += 1
                    author_name = authorship.get('author', {}).get('display_name', 'Unknown')

                    for institution in authorship.get('institutions', []):
                        if institution.get('country_code') == 'CN':
                            inst_name = institution.get('display_name', 'Unknown')
                            if inst_name not in chinese_institutions:
                                chinese_institutions.append(inst_name)
                            if author_name not in chinese_authors:
                                chinese_authors.append(author_name)

                # Get primary topic info
                primary_topic = work.get('primary_topic', {})

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
                    'chinese_institutions': '; '.join(chinese_institutions[:5]),  # Top 5
                    'chinese_authors_count': len(chinese_authors),
                    'total_authors': total_authors,
                    'chinese_collaboration_pct': round(len(chinese_authors) / max(total_authors, 1) * 100, 1)
                }

                all_topic_data.append(record)

            print(f"  Processed: {len(works)} works")
            self.stats[topic_name] = len(works)

        # Save combined data
        df = pd.DataFrame(all_topic_data)

        if len(df) > 0:
            output_file = self.output_dir / 'chinese_research_by_topic.csv'
            df.to_csv(output_file, index=False)

            print(f"\n[OK] Saved {len(df):,} records to {output_file}")

            # Summary statistics
            print("\n" + "="*80)
            print("TOPIC COVERAGE SUMMARY")
            print("="*80)

            topic_summary = df.groupby('technology_category').agg({
                'openalex_id': 'count',
                'cited_by_count': ['sum', 'mean'],
                'chinese_institutions_count': 'mean',
                'publication_year': ['min', 'max']
            }).round(1)

            print(topic_summary.to_string())

            return df
        else:
            print("\n[!] No data extracted")
            return None

    def extract_top_chinese_institutions(self):
        """
        Get top Chinese research institutions in technology fields
        """
        print("\n" + "="*80)
        print("EXTRACTING TOP CHINESE RESEARCH INSTITUTIONS")
        print("="*80)

        # Get overall Chinese tech research
        print("\n[FETCHING INSTITUTION DATA]")

        url = f"{self.base_url}/works"
        params = {
            'filter': 'authorships.countries:CN,publication_year:2020-2025',
            'group_by': 'authorships.institutions.id',
            'per-page': 200
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            institutions_data = []

            if 'group_by' in data:
                for group in data['group_by'][:100]:  # Top 100
                    inst_id = group['key'].replace('https://openalex.org/', '') if group['key'] else None

                    if not inst_id or inst_id == 'null':
                        continue

                    # Get institution details
                    inst_url = f"{self.base_url}/institutions/{inst_id}"
                    inst_response = requests.get(inst_url)

                    if inst_response.status_code == 200:
                        inst_data = inst_response.json()

                        record = {
                            'institution_id': inst_id,
                            'institution_name': inst_data.get('display_name', ''),
                            'country': inst_data.get('country_code', ''),
                            'type': inst_data.get('type', ''),
                            'works_count_2020_2025': group['count'],
                            'cited_by_count': inst_data.get('cited_by_count', 0),
                            'h_index': inst_data.get('summary_stats', {}).get('h_index', 0),
                            'i10_index': inst_data.get('summary_stats', {}).get('i10_index', 0),
                            'homepage_url': inst_data.get('homepage_url', '')
                        }

                        institutions_data.append(record)
                        print(f"  Processed: {record['institution_name'][:50]}", end='\r')

                    time.sleep(0.1)  # Be respectful

            df = pd.DataFrame(institutions_data)

            if len(df) > 0:
                output_file = self.output_dir / 'top_chinese_institutions.csv'
                df.to_csv(output_file, index=False)

                print(f"\n[OK] Saved {len(df):,} institutions to {output_file}")

                print("\nTop 10 Institutions by Works Count (2020-2025):")
                print(df.nlargest(10, 'works_count_2020_2025')[
                    ['institution_name', 'works_count_2020_2025', 'h_index']
                ].to_string(index=False))

                return df
            else:
                print("\n[!] No institution data extracted")
                return None

        except Exception as e:
            print(f"\n[!] Error: {str(e)}")
            return None

    def extract_annual_trends(self):
        """
        Extract annual publication trends for Chinese tech research
        """
        print("\n" + "="*80)
        print("EXTRACTING ANNUAL TRENDS")
        print("="*80)

        trends_data = []

        for year in range(2011, 2026):
            print(f"\n[YEAR {year}]")

            for topic_name, topic_id in self.tech_topics.items():
                url = f"{self.base_url}/works"
                params = {
                    'filter': f'authorships.countries:CN,topics.id:{topic_id},publication_year:{year}',
                    'per-page': 1  # We only need count
                }

                try:
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()

                    count = data.get('meta', {}).get('count', 0)

                    record = {
                        'year': year,
                        'technology_category': topic_name,
                        'publication_count': count
                    }

                    trends_data.append(record)
                    print(f"  {topic_name}: {count:,}", end='\r')

                    time.sleep(0.05)

                except Exception as e:
                    print(f"  Error for {topic_name}: {str(e)[:50]}")

        df = pd.DataFrame(trends_data)

        if len(df) > 0:
            output_file = self.output_dir / 'annual_trends_by_topic.csv'
            df.to_csv(output_file, index=False)

            print(f"\n\n[OK] Saved {len(df):,} trend records to {output_file}")

            # Calculate growth rates
            print("\n" + "="*80)
            print("GROWTH ANALYSIS (2011-2025)")
            print("="*80)

            for topic in self.tech_topics.keys():
                topic_data = df[df['technology_category'] == topic]
                if len(topic_data) > 0:
                    early = topic_data[topic_data['year'] <= 2015]['publication_count'].sum()
                    recent = topic_data[topic_data['year'] >= 2020]['publication_count'].sum()

                    if early > 0:
                        growth_pct = round((recent - early) / early * 100, 1)
                        print(f"{topic:30s}: {early:6,} -> {recent:6,} ({growth_pct:+6.1f}%)")

            return df
        else:
            print("\n[!] No trend data extracted")
            return None

    def generate_summary_report(self):
        """
        Generate comprehensive summary report
        """
        print("\n" + "="*80)
        print("GENERATING SUMMARY REPORT")
        print("="*80)

        summary = {
            'extraction_date': datetime.now().isoformat(),
            'source': 'OpenAlex API',
            'api_cost': 0.00,
            'technology_topics': len(self.tech_topics),
            'topics_extracted': self.stats,
            'total_works': sum(self.stats.values())
        }

        output_file = self.output_dir / 'extraction_summary.json'
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n[OK] Summary saved: {output_file}")
        print(f"\nTotal works extracted: {summary['total_works']:,}")
        print(f"Technology topics covered: {summary['technology_topics']}")
        print(f"API cost: $0.00 (free unlimited access)")

        return summary

    def run_complete_extraction(self):
        """
        Run complete extraction workflow
        """
        print("="*80)
        print("OPENALEX CHINESE TECHNOLOGY RESEARCH EXTRACTION")
        print("="*80)

        # Step 1: Extract by topic
        topic_df = self.extract_chinese_research_by_topic()

        # Step 2: Extract top institutions
        institutions_df = self.extract_top_chinese_institutions()

        # Step 3: Extract annual trends
        trends_df = self.extract_annual_trends()

        # Step 4: Generate summary
        summary = self.generate_summary_report()

        print("\n" + "="*80)
        print("EXTRACTION COMPLETE")
        print("="*80)

        print("\nFiles created:")
        print(f"  1. chinese_research_by_topic.csv")
        print(f"  2. top_chinese_institutions.csv")
        print(f"  3. annual_trends_by_topic.csv")
        print(f"  4. extraction_summary.json")

        print(f"\nOutput directory: {self.output_dir}")

        return {
            'topics': topic_df,
            'institutions': institutions_df,
            'trends': trends_df,
            'summary': summary
        }

def main():
    extractor = OpenAlexExtractor()
    results = extractor.run_complete_extraction()

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Review extracted CSV files in data/openalex_chinese_research/")
    print("2. Integrate into database (similar to BigQuery integration)")
    print("3. Cross-reference with patent data for complete picture")
    print("4. Analyze institution-level collaboration networks")

if __name__ == "__main__":
    main()
