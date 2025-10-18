#!/usr/bin/env python3
"""
Non-EU European Countries - China Agreements Harvester
Searches for agreements between China and:
- Balkans: Serbia, Albania, North Macedonia, Montenegro, Bosnia, Kosovo
- Nordic: Iceland, Norway
- Others: Switzerland, UK, Turkey
- Caucasus: Armenia, Azerbaijan, Georgia
"""

import boto3
import json
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Load environment variables
load_dotenv('.env.local')

class NonEUEuropeHarvester:
    """Harvest China agreements with non-EU European countries"""

    def __init__(self):
        """Initialize AWS Athena client"""
        self.athena = boto3.client(
            'athena',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )

        self.s3_output = os.getenv('S3_RESULTS_PATH')
        self.database = 'ccindex'

        # Define country groups
        self.country_groups = {
            'balkans': {
                'serbia': ['serbia', 'serbian', 'belgrade', '.rs'],
                'albania': ['albania', 'albanian', 'tirana', '.al'],
                'north_macedonia': ['macedonia', 'macedonian', 'skopje', '.mk'],
                'montenegro': ['montenegro', 'montenegrin', 'podgorica', '.me'],
                'bosnia': ['bosnia', 'bosnian', 'sarajevo', '.ba'],
                'kosovo': ['kosovo', 'kosovar', 'pristina', '.xk']
            },
            'nordic': {
                'iceland': ['iceland', 'icelandic', 'reykjavik', '.is'],
                'norway': ['norway', 'norwegian', 'oslo', '.no']
            },
            'western': {
                'switzerland': ['switzerland', 'swiss', 'bern', 'zurich', '.ch'],
                'uk': ['united kingdom', 'britain', 'british', 'london', '.uk', '.gov.uk']
            },
            'caucasus': {
                'armenia': ['armenia', 'armenian', 'yerevan', '.am'],
                'azerbaijan': ['azerbaijan', 'azerbaijani', 'baku', '.az'],
                'georgia': ['georgia', 'georgian', 'tbilisi', '.ge']
            },
            'turkey': {
                'turkey': ['turkey', 'turkish', 'turkiye', 'ankara', 'istanbul', '.tr']
            }
        }

        # Agreement type keywords
        self.agreement_keywords = {
            'bri': ['belt and road', 'silk road', 'bri', 'belt & road'],
            'investment': ['investment', 'invest', 'fdi', 'capital'],
            'trade': ['trade', 'export', 'import', 'commerce', 'economic'],
            'infrastructure': ['infrastructure', 'railway', 'highway', 'port', 'bridge'],
            'energy': ['energy', 'power', 'renewable', 'solar', 'wind', 'hydropower'],
            'technology': ['technology', 'digital', '5g', 'huawei', 'tech transfer'],
            'sister_city': ['sister city', 'twin city', 'friendship city'],
            'university': ['university', 'academic', 'education', 'research']
        }

        # Results storage
        self.results_dir = Path('athena_results')
        self.results_dir.mkdir(exist_ok=True)

    def execute_query(self, query, query_name):
        """Execute Athena query and return execution ID"""
        try:
            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': self.database},
                ResultConfiguration={'OutputLocation': self.s3_output}
            )
            print(f"Started query '{query_name}': {response['QueryExecutionId']}")
            return response['QueryExecutionId'], query_name
        except Exception as e:
            print(f"Error executing query '{query_name}': {e}")
            return None, query_name

    def wait_for_query(self, query_id):
        """Wait for query to complete"""
        max_attempts = 30
        for attempt in range(max_attempts):
            response = self.athena.get_query_execution(QueryExecutionId=query_id)
            status = response['QueryExecution']['Status']['State']

            if status == 'SUCCEEDED':
                return True
            elif status in ['FAILED', 'CANCELLED']:
                print(f"Query {query_id} failed: {status}")
                return False

            time.sleep(2)

        print(f"Query {query_id} timed out")
        return False

    def get_query_results(self, query_id):
        """Get results from completed query"""
        try:
            response = self.athena.get_query_results(
                QueryExecutionId=query_id,
                MaxResults=100
            )

            results = []
            for row in response['ResultSet']['Rows'][1:]:  # Skip header
                if row['Data']:
                    results.append({
                        'url': row['Data'][0].get('VarCharValue', ''),
                        'domain': row['Data'][1].get('VarCharValue', ''),
                        'crawl_date': row['Data'][2].get('VarCharValue', ''),
                        'path': row['Data'][3].get('VarCharValue', '') if len(row['Data']) > 3 else ''
                    })

            return results
        except Exception as e:
            print(f"Error getting results for {query_id}: {e}")
            return []

    def build_country_query(self, country_name, country_keywords):
        """Build query for specific country"""
        # Create country-specific conditions
        country_conditions = ' OR '.join([f"url LIKE '%{kw}%'" for kw in country_keywords])

        query = f"""
        SELECT DISTINCT
            url,
            url_host_name,
            fetch_time,
            url_path
        FROM ccindex
        WHERE crawl_date = 'CC-MAIN-2024-26'
        AND (
            ({country_conditions})
            AND (
                url LIKE '%china%' OR url LIKE '%chinese%' OR
                url LIKE '%beijing%' OR url LIKE '%shanghai%' OR
                url LIKE '%sino-%' OR url LIKE '%cn-%'
            )
        )
        AND (
            url LIKE '%agreement%' OR url LIKE '%cooperation%' OR
            url LIKE '%partnership%' OR url LIKE '%memorandum%' OR
            url LIKE '%mou%' OR url LIKE '%deal%' OR
            url LIKE '%contract%' OR url LIKE '%investment%' OR
            url LIKE '%belt%road%' OR url LIKE '%bri%' OR
            url LIKE '%sister%city%' OR url LIKE '%university%'
        )
        LIMIT 200
        """
        return query

    def search_balkans(self):
        """Search for Balkans-China agreements"""
        print("\nSearching Balkans-China agreements...")
        queries = []

        for country, keywords in self.country_groups['balkans'].items():
            query = self.build_country_query(country, keywords)
            queries.append((query, f"balkans_{country}"))

        # Special query for 17+1 cooperation mechanism
        cooperation_17_plus_1_query = """
        SELECT DISTINCT
            url,
            url_host_name,
            fetch_time,
            url_path
        FROM ccindex
        WHERE crawl_date = 'CC-MAIN-2024-26'
        AND (
            url LIKE '%17+1%' OR url LIKE '%16+1%' OR
            url LIKE '%ceec%' OR url LIKE '%china-cee%' OR
            url LIKE '%central eastern europe%china%'
        )
        LIMIT 100
        """
        queries.append((cooperation_17_plus_1_query, "17_plus_1_cooperation"))

        return queries

    def search_nordic(self):
        """Search for Nordic non-EU countries-China agreements"""
        print("\nSearching Nordic-China agreements...")
        queries = []

        for country, keywords in self.country_groups['nordic'].items():
            query = self.build_country_query(country, keywords)
            queries.append((query, f"nordic_{country}"))

        # Arctic cooperation query
        arctic_query = """
        SELECT DISTINCT
            url,
            url_host_name,
            fetch_time,
            url_path
        FROM ccindex
        WHERE crawl_date = 'CC-MAIN-2024-26'
        AND (
            (url LIKE '%arctic%' AND url LIKE '%china%') OR
            (url LIKE '%polar silk road%') OR
            (url LIKE '%ice silk road%')
        )
        LIMIT 100
        """
        queries.append((arctic_query, "arctic_cooperation"))

        return queries

    def search_western(self):
        """Search for Switzerland and UK-China agreements"""
        print("\nSearching Switzerland/UK-China agreements...")
        queries = []

        for country, keywords in self.country_groups['western'].items():
            query = self.build_country_query(country, keywords)
            queries.append((query, f"western_{country}"))

        # Financial center cooperation
        financial_query = """
        SELECT DISTINCT
            url,
            url_host_name,
            fetch_time,
            url_path
        FROM ccindex
        WHERE crawl_date = 'CC-MAIN-2024-26'
        AND (
            (url LIKE '%london%' AND url LIKE '%china%' AND url LIKE '%financ%') OR
            (url LIKE '%zurich%' AND url LIKE '%china%' AND url LIKE '%bank%') OR
            (url LIKE '%city of london%' AND url LIKE '%rmb%')
        )
        LIMIT 100
        """
        queries.append((financial_query, "financial_centers"))

        return queries

    def search_caucasus(self):
        """Search for Caucasus-China agreements"""
        print("\nSearching Caucasus-China agreements...")
        queries = []

        for country, keywords in self.country_groups['caucasus'].items():
            query = self.build_country_query(country, keywords)
            queries.append((query, f"caucasus_{country}"))

        # Middle Corridor transport query
        middle_corridor_query = """
        SELECT DISTINCT
            url,
            url_host_name,
            fetch_time,
            url_path
        FROM ccindex
        WHERE crawl_date = 'CC-MAIN-2024-26'
        AND (
            (url LIKE '%middle corridor%' AND url LIKE '%china%') OR
            (url LIKE '%trans-caspian%' AND url LIKE '%china%') OR
            (url LIKE '%caucasus%' AND url LIKE '%belt%road%')
        )
        LIMIT 100
        """
        queries.append((middle_corridor_query, "middle_corridor"))

        return queries

    def search_turkey(self):
        """Search for Turkey-China agreements"""
        print("\nSearching Turkey-China agreements...")
        queries = []

        for country, keywords in self.country_groups['turkey'].items():
            query = self.build_country_query(country, keywords)
            queries.append((query, f"turkey_{country}"))

        # Middle Corridor and specific Turkey projects
        turkey_special_query = """
        SELECT DISTINCT
            url,
            url_host_name,
            fetch_time,
            url_path
        FROM ccindex
        WHERE crawl_date = 'CC-MAIN-2024-26'
        AND (
            (url LIKE '%turkey%' AND url LIKE '%china%' AND url LIKE '%nuclear%') OR
            (url LIKE '%istanbul%' AND url LIKE '%beijing%') OR
            (url LIKE '%baku-tbilisi-kars%' AND url LIKE '%china%') OR
            (url LIKE '%turkey%' AND url LIKE '%huawei%') OR
            (url LIKE '%erdogan%' AND url LIKE '%xi jinping%')
        )
        LIMIT 100
        """
        queries.append((turkey_special_query, "turkey_special_projects"))

        return queries

    def execute_all_searches(self):
        """Execute all search queries concurrently"""
        print("="*80)
        print("NON-EU EUROPE-CHINA AGREEMENTS DISCOVERY")
        print("="*80)
        print(f"Start time: {datetime.now()}")

        all_queries = []

        # Collect all queries
        all_queries.extend(self.search_balkans())
        all_queries.extend(self.search_nordic())
        all_queries.extend(self.search_western())
        all_queries.extend(self.search_caucasus())
        all_queries.extend(self.search_turkey())

        print(f"\nExecuting {len(all_queries)} queries...")

        # Execute queries concurrently
        results_by_region = {
            'balkans': {},
            'nordic': {},
            'western': {},
            'caucasus': {},
            'turkey': {},
            'special_mechanisms': {}
        }

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all queries
            future_to_query = {}
            for query_sql, query_name in all_queries:
                future = executor.submit(self.execute_query, query_sql, query_name)
                future_to_query[future] = (query_sql, query_name)

            # Collect query IDs
            query_ids = {}
            for future in as_completed(future_to_query):
                query_sql, query_name = future_to_query[future]
                query_id, name = future.result()
                if query_id:
                    query_ids[query_id] = query_name

        # Wait for queries to complete and get results
        print("\nWaiting for queries to complete...")
        for query_id, query_name in query_ids.items():
            if self.wait_for_query(query_id):
                results = self.get_query_results(query_id)

                # Categorize results
                if 'balkans' in query_name:
                    results_by_region['balkans'][query_name] = results
                elif 'nordic' in query_name or 'arctic' in query_name:
                    results_by_region['nordic'][query_name] = results
                elif 'western' in query_name or 'financial' in query_name:
                    results_by_region['western'][query_name] = results
                elif 'caucasus' in query_name or 'middle_corridor' in query_name:
                    results_by_region['caucasus'][query_name] = results
                elif 'turkey' in query_name:
                    results_by_region['turkey'][query_name] = results
                elif '17_plus_1' in query_name:
                    results_by_region['special_mechanisms'][query_name] = results

                print(f"  {query_name}: {len(results)} results")

        return results_by_region

    def analyze_results(self, results_by_region):
        """Analyze and categorize discovered agreements"""
        analysis = {
            'summary': {},
            'by_agreement_type': {},
            'key_findings': [],
            'bri_projects': [],
            'sister_cities': []
        }

        total_agreements = 0

        # Process each region
        for region, queries in results_by_region.items():
            region_total = 0
            region_agreements = []

            for query_name, results in queries.items():
                region_total += len(results)
                region_agreements.extend(results)

            analysis['summary'][region] = {
                'total': region_total,
                'queries': len(queries)
            }
            total_agreements += region_total

            # Categorize agreements
            for agreement in region_agreements:
                url = agreement.get('url', '').lower()

                # Check for BRI
                if any(kw in url for kw in self.agreement_keywords['bri']):
                    analysis['bri_projects'].append({
                        'region': region,
                        'url': agreement['url'],
                        'domain': agreement['domain']
                    })

                # Check for sister cities
                if any(kw in url for kw in self.agreement_keywords['sister_city']):
                    analysis['sister_cities'].append({
                        'region': region,
                        'url': agreement['url'],
                        'domain': agreement['domain']
                    })

        analysis['summary']['total'] = total_agreements

        return analysis

    def generate_report(self, results_by_region, analysis):
        """Generate comprehensive report"""
        print("\n" + "="*80)
        print("ANALYSIS RESULTS")
        print("="*80)

        print(f"\nTOTAL AGREEMENTS DISCOVERED: {analysis['summary']['total']}")

        print("\nBY REGION:")
        for region, data in analysis['summary'].items():
            if region != 'total':
                print(f"  {region.upper()}: {data['total']} agreements")

        print(f"\nBRI PROJECTS: {len(analysis['bri_projects'])}")
        if analysis['bri_projects']:
            for proj in analysis['bri_projects'][:5]:
                print(f"  - {proj['region']}: {proj['domain']}")

        print(f"\nSISTER CITIES: {len(analysis['sister_cities'])}")
        if analysis['sister_cities']:
            for city in analysis['sister_cities'][:5]:
                print(f"  - {city['region']}: {city['domain']}")

        # Special findings
        if '17_plus_1_cooperation' in results_by_region.get('special_mechanisms', {}):
            ceec_results = results_by_region['special_mechanisms']['17_plus_1_cooperation']
            if ceec_results:
                print(f"\n17+1 COOPERATION MECHANISM:")
                print(f"  Found {len(ceec_results)} related agreements")

        # Save full results
        output_data = {
            'harvest_date': datetime.now().isoformat(),
            'regions_searched': list(self.country_groups.keys()),
            'countries_searched': {
                region: list(countries.keys())
                for region, countries in self.country_groups.items()
            },
            'results_by_region': {
                region: {
                    query: [
                        {
                            'url': r['url'],
                            'domain': r['domain'],
                            'crawl_date': r['crawl_date']
                        }
                        for r in results
                    ]
                    for query, results in queries.items()
                }
                for region, queries in results_by_region.items()
            },
            'analysis': analysis
        }

        output_file = self.results_dir / f'non_eu_harvest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\nFull results saved to: {output_file}")

        return output_data

def main():
    """Execute non-EU Europe harvesting"""
    harvester = NonEUEuropeHarvester()

    # Execute searches
    results = harvester.execute_all_searches()

    # Analyze results
    analysis = harvester.analyze_results(results)

    # Generate report
    report = harvester.generate_report(results, analysis)

    print("\n" + "="*80)
    print("HARVESTING COMPLETE")
    print("="*80)
    print(f"End time: {datetime.now()}")

if __name__ == "__main__":
    main()
