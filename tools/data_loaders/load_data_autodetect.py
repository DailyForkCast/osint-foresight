#!/usr/bin/env python3
"""
Load country data into BigQuery with auto-detected schemas
"""
import csv
from pathlib import Path
from typing import List

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import Conflict
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-cloud-bigquery"])
    from google.cloud import bigquery
    from google.cloud.exceptions import Conflict

def detect_delimiter(file_path: Path) -> str:
    """Detect if file is CSV or TSV"""
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if '\t' in first_line:
            return '\t'
        return ','

def get_headers(file_path: Path) -> List[str]:
    """Get headers from CSV/TSV file"""
    delimiter = detect_delimiter(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter)
        headers = next(reader)
        return [h.strip() for h in headers]

def load_file_to_bigquery(
    project_id: str,
    dataset_id: str,
    table_name: str,
    file_path: Path,
    country: str
) -> bool:
    """Load a file to BigQuery with auto-detected schema"""
    
    client = bigquery.Client(project=project_id)
    
    # Check file exists and is not empty
    if not file_path.exists():
        print(f"  [SKIP] File not found: {file_path}")
        return False
    
    if file_path.stat().st_size < 10:
        print(f"  [SKIP] File is empty: {file_path}")
        return False
    
    # Detect delimiter
    delimiter = detect_delimiter(file_path)
    
    # Configure load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        field_delimiter=delimiter,
        autodetect=True,  # Let BigQuery detect the schema
        write_disposition="WRITE_TRUNCATE",  # Replace existing data
        max_bad_records=10,  # Allow some bad records
        ignore_unknown_values=True,  # Ignore extra columns
    )
    
    # Full table ID
    table_id = f"{project_id}.{dataset_id}.{table_name}_{country}"
    
    try:
        # Load the file
        with open(file_path, "rb") as source_file:
            job = client.load_table_from_file(
                source_file, table_id, job_config=job_config
            )
        
        # Wait for job to complete
        job.result()
        
        # Get table info
        table = client.get_table(table_id)
        print(f"  [OK] Loaded {file_path.name} -> {table_name}_{country}")
        print(f"       Rows: {table.num_rows}, Columns: {len(table.schema)}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "Not found: Table" in error_msg:
            # Table doesn't exist, create it first
            try:
                # Create empty table with autodetect
                table = bigquery.Table(table_id)
                table = client.create_table(table)
                print(f"  [OK] Created table: {table_name}_{country}")
                
                # Try loading again
                with open(file_path, "rb") as source_file:
                    job = client.load_table_from_file(
                        source_file, table_id, job_config=job_config
                    )
                job.result()
                
                table = client.get_table(table_id)
                print(f"  [OK] Loaded {file_path.name}")
                print(f"       Rows: {table.num_rows}, Columns: {len(table.schema)}")
                return True
                
            except Exception as e2:
                print(f"  [ERROR] Failed to create/load: {e2}")
                return False
        else:
            print(f"  [ERROR] Failed to load: {e}")
            return False

def load_country_data(country: str, project_id: str = "osint-foresight-2025"):
    """Load all data files for a country"""
    
    print(f"\nLoading data for country: {country}")
    print("=" * 60)
    
    base_path = Path("data/processed") / f"country={country}"
    
    if not base_path.exists():
        print(f"No data found for {country}")
        return
    
    # List all CSV and TSV files
    files = list(base_path.glob("*.csv")) + list(base_path.glob("*.tsv"))
    
    loaded_count = 0
    for file_path in files:
        # Get table name from file name
        table_name = file_path.stem.replace("-", "_").replace(" ", "_")
        
        # Skip temporary or backup files
        if table_name.startswith("~") or table_name.startswith("."):
            continue
        
        # Load to BigQuery
        if load_file_to_bigquery(
            project_id,
            "processed_data",
            table_name,
            file_path,
            country
        ):
            loaded_count += 1
    
    print(f"\nSuccessfully loaded {loaded_count} files for {country}")
    
    return loaded_count

def main():
    """Main function"""
    
    project_id = "osint-foresight-2025"
    
    # Find all countries with data
    data_dir = Path("data/processed")
    if not data_dir.exists():
        print("No data/processed directory found")
        return
    
    countries = []
    for country_dir in data_dir.glob("country=*"):
        country_code = country_dir.name.split("=")[1]
        countries.append(country_code)
    
    if not countries:
        print("No country data found")
        return
    
    print(f"Found countries: {', '.join(countries)}")
    print("=" * 60)
    
    total_loaded = 0
    for country in countries:
        count = load_country_data(country, project_id)
        if count:
            total_loaded += count
    
    print("\n" + "=" * 60)
    print(f"Data loading complete! Loaded {total_loaded} total files.")
    print(f"\nAccess your data at:")
    print(f"https://console.cloud.google.com/bigquery?project={project_id}")
    
    # Show example queries
    print("\nExample BigQuery queries:")
    print("-" * 40)
    
    if "AT" in countries:
        print("""
-- View Austria relationships
SELECT * FROM `osint-foresight-2025.processed_data.relationships_AT` 
LIMIT 100;

-- Sector analysis
SELECT sector, COUNT(*) as count
FROM `osint-foresight-2025.processed_data.relationships_AT`
WHERE sector IS NOT NULL
GROUP BY sector
ORDER BY count DESC;

-- International collaboration
SELECT counterpart_country, COUNT(*) as collaborations
FROM `osint-foresight-2025.processed_data.relationships_AT`
WHERE counterpart_country IS NOT NULL
GROUP BY counterpart_country
ORDER BY collaborations DESC
LIMIT 20;
""")

if __name__ == "__main__":
    main()