#!/usr/bin/env python3
"""
Load country data into BigQuery tables
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from setup_bigquery_tables import load_country_data

def main():
    """Load all available country data"""

    project_id = "osint-foresight-2025"
    data_dir = Path("data/processed")

    if not data_dir.exists():
        print("No data/processed directory found")
        return

    # Find all countries with data
    countries = []
    for country_dir in data_dir.glob("country=*"):
        country_code = country_dir.name.split("=")[1]
        countries.append(country_code)

    if not countries:
        print("No country data found")
        return

    print(f"Loading data for countries: {', '.join(countries)}")
    print("=" * 60)

    for country in countries:
        try:
            load_country_data(country, project_id)
        except Exception as e:
            print(f"Error loading data for {country}: {e}")
            continue

    print("\n" + "=" * 60)
    print("Data loading complete!")
    print(f"\nAccess your data at:")
    print(f"https://console.cloud.google.com/bigquery?project={project_id}")

    # Show sample queries specific to loaded countries
    if "AT" in countries:
        print("\nSample queries for Austria (AT):")
        print("-" * 40)
        print("""
SELECT sector, COUNT(*) as relationships,
       COUNTIF(year >= 2023) as recent_activity
FROM `osint-foresight-2025.processed_data.relationships_AT`
GROUP BY sector
ORDER BY relationships DESC
LIMIT 10;

-- Top PRC partners
SELECT counterpart_name, COUNT(*) as collaborations
FROM `osint-foresight-2025.processed_data.relationships_AT`
WHERE counterpart_country = 'CN'
GROUP BY counterpart_name
ORDER BY collaborations DESC
LIMIT 10;
""")

if __name__ == "__main__":
    main()
