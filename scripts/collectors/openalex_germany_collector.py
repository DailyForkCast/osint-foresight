"""
OpenAlex Germany-China Collaboration Collector
Fetches real academic collaboration data between Germany and China
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import time

def collect_germany_china_collaborations():
    """Fetch Germany-China collaborative publications from OpenAlex"""

    print("[OPENALEX COLLECTOR]")
    print("Fetching Germany-China collaborative publications...")

    # OpenAlex API endpoint - no authentication required!
    base_url = "https://api.openalex.org/works"

    # Filter for papers with both German and Chinese institutions
    params = {
        "filter": "institutions.country_code:DE,institutions.country_code:CN",
        "per-page": 200,  # Get 200 papers
        "sort": "publication_year:desc",  # Most recent first
        "select": "id,title,publication_year,authorships,cited_by_count,concepts"
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        print(f"Found {data['meta']['count']} total Germany-China collaborative papers")

        # Process the results
        collaborations = []
        sensitive_keywords = ["quantum", "artificial intelligence", "ai", "semiconductor",
                            "5g", "6g", "military", "defense", "dual-use", "nuclear",
                            "hypersonic", "laser", "photonic", "cryptography"]

        for work in data.get('results', []):
            # Extract German and Chinese institutions
            german_institutions = set()
            chinese_institutions = set()

            for authorship in work.get('authorships', []):
                for institution in authorship.get('institutions', []):
                    country = institution.get('country_code', '')
                    name = institution.get('display_name', '')

                    if country == 'DE':
                        german_institutions.add(name)
                    elif country == 'CN':
                        chinese_institutions.add(name)

            # Check for sensitive research areas
            title = work.get('title', '').lower()
            concepts = ' '.join([c.get('display_name', '').lower()
                               for c in work.get('concepts', [])])

            is_sensitive = any(keyword in title or keyword in concepts
                             for keyword in sensitive_keywords)

            collaboration = {
                "id": work.get('id'),
                "title": work.get('title'),
                "year": work.get('publication_year'),
                "citations": work.get('cited_by_count', 0),
                "german_institutions": list(german_institutions),
                "chinese_institutions": list(chinese_institutions),
                "sensitive_research": is_sensitive,
                "concepts": [c.get('display_name') for c in work.get('concepts', [])][:5]
            }

            collaborations.append(collaboration)

        # Analyze findings
        sensitive_count = sum(1 for c in collaborations if c['sensitive_research'])

        # Key German institutions collaborating with China
        all_german = []
        for c in collaborations:
            all_german.extend(c['german_institutions'])

        from collections import Counter
        top_german = Counter(all_german).most_common(10)

        # Save results
        output_dir = Path("F:/OSINT_DATA/Germany_Analysis")
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "query": "Germany-China collaborative research",
            "timestamp": datetime.now().isoformat(),
            "total_papers": data['meta']['count'],
            "papers_analyzed": len(collaborations),
            "sensitive_research_count": sensitive_count,
            "sensitive_percentage": round(sensitive_count / len(collaborations) * 100, 2),
            "top_german_institutions": top_german,
            "collaborations": collaborations[:50]  # First 50 for detail
        }

        output_file = output_dir / f"openalex_germany_china_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n[RESULTS]")
        print(f"Total collaborations: {data['meta']['count']}")
        print(f"Papers analyzed: {len(collaborations)}")
        print(f"Sensitive research: {sensitive_count} ({results['sensitive_percentage']}%)")
        print(f"\nTop German institutions collaborating with China:")
        for inst, count in top_german[:5]:
            print(f"  - {inst}: {count} papers")

        print(f"\nFull results saved to: {output_file}")

        return results

    except Exception as e:
        print(f"Error: {e}")
        return None


def collect_cordis_germany_data():
    """Attempt to fetch CORDIS data for Germany"""

    print("\n[CORDIS COLLECTOR]")
    print("Attempting to fetch EU project data...")

    # CORDIS has limited API access, but we can try their data endpoint
    cordis_url = "https://cordis.europa.eu/datalab/datalab-api/projects"

    # Note: CORDIS requires more complex authentication/access
    # For now, document what we would collect

    cordis_plan = {
        "source": "CORDIS - EU Research Projects",
        "note": "Requires registration for API access",
        "data_available": [
            "Horizon Europe projects (2021-2027)",
            "Horizon 2020 projects (2014-2020)",
            "FP7 projects (2007-2013)"
        ],
        "germany_relevant": [
            "German coordinator projects",
            "German participant organizations",
            "Projects with Chinese participation",
            "Dual-use technology projects"
        ],
        "endpoints": {
            "projects": "https://cordis.europa.eu/datalab/datalab-api/projects",
            "organizations": "https://cordis.europa.eu/data/cordis-h2020organizations.csv",
            "search": "https://cordis.europa.eu/search/en"
        }
    }

    output_dir = Path("F:/OSINT_DATA/Germany_Analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"cordis_access_plan_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(cordis_plan, f, indent=2)

    print(f"CORDIS access plan saved to: {output_file}")
    print("Note: Full CORDIS data requires API registration")

    return cordis_plan


if __name__ == "__main__":
    # Collect OpenAlex data - THIS WILL WORK!
    openalex_results = collect_germany_china_collaborations()

    # Document CORDIS access requirements
    cordis_plan = collect_cordis_germany_data()

    print("\n[COLLECTION COMPLETE]")
    print("OpenAlex data successfully collected")
    print("CORDIS requires additional setup")
