#!/usr/bin/env python3
"""
Set up BigQuery tables for OSINT Foresight data import
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import Conflict
except ImportError:
    print("Installing google-cloud-bigquery...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-cloud-bigquery"])
    from google.cloud import bigquery
    from google.cloud.exceptions import Conflict

# Define table schemas based on your data structure
TABLE_SCHEMAS = {
    "processed_data": {
        "relationships": [
            bigquery.SchemaField("sector", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("subsector", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("counterpart_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("counterpart_country", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("collab_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("year", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("weight", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("project_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
        ],
        "signals": [
            bigquery.SchemaField("window", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("signal_summary", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("likely_driver", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("event_count", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("peak_date", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("severity", "STRING", mode="NULLABLE"),
        ],
        "standards_roles": [
            bigquery.SchemaField("wg", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("role", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("person_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("org_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("sector_hint", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("standard_body", "STRING", mode="NULLABLE"),
        ],
        "institutions": [
            bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("org_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("is_lab", "BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField("accreditation_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("scope", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("website", "STRING", mode="NULLABLE"),
        ],
        "mechanism_incidents": [
            bigquery.SchemaField("sector", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("mechanism_family", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("year", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("severity", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
        ],
        "sanctions_hits": [
            bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("list_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("date_added", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("reason", "STRING", mode="NULLABLE"),
        ],
        "cer_master": [
            bigquery.SchemaField("raw_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("canon_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("entity_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("confidence", "FLOAT", mode="NULLABLE"),
        ],
    },
    "country_reports": {
        "phase_metrics": [
            bigquery.SchemaField("country", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("phase", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("phase_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("metric_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("metric_value", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("metric_unit", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("date_calculated", "TIMESTAMP", mode="NULLABLE"),
        ],
        "sector_scores": [
            bigquery.SchemaField("country", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sector", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("intensity", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("momentum_15_18", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("momentum_19_22", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("momentum_23_25", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("top_counterpart", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("consortium_skew", "BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField("prc_exposure", "FLOAT", mode="NULLABLE"),
        ],
    }
}

def create_tables(project_id: str = "osint-foresight-2025"):
    """Create BigQuery tables with appropriate schemas"""
    
    client = bigquery.Client(project=project_id)
    created_tables = []
    existing_tables = []
    
    print(f"Creating BigQuery tables in project: {project_id}")
    print("=" * 60)
    
    for dataset_name, tables in TABLE_SCHEMAS.items():
        dataset_id = f"{project_id}.{dataset_name}"
        
        print(f"\nDataset: {dataset_name}")
        print("-" * 40)
        
        for table_name, schema in tables.items():
            table_id = f"{dataset_id}.{table_name}"
            table = bigquery.Table(table_id, schema=schema)
            
            try:
                table = client.create_table(table)
                print(f"  [OK] Created table: {table_name}")
                created_tables.append(table_id)
            except Conflict:
                print(f"  [EXISTS] Table {table_name} already exists")
                existing_tables.append(table_id)
            except Exception as e:
                print(f"  [ERROR] Failed to create {table_name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"Summary: Created {len(created_tables)} new tables, {len(existing_tables)} already existed")
    
    return created_tables, existing_tables

def load_data_from_csv(
    client: bigquery.Client,
    table_id: str,
    csv_path: Path,
    skip_header: bool = True
) -> bool:
    """Load data from CSV file into BigQuery table"""
    
    if not csv_path.exists():
        print(f"  [SKIP] File not found: {csv_path}")
        return False
    
    # Check if file is empty or too small
    if csv_path.stat().st_size < 10:
        print(f"  [SKIP] File is empty: {csv_path}")
        return False
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1 if skip_header else 0,
        autodetect=False,  # Use predefined schema
        write_disposition="WRITE_TRUNCATE",  # Replace existing data
    )
    
    # Handle TSV files
    if csv_path.suffix.lower() == '.tsv':
        job_config.field_delimiter = '\t'
    
    try:
        with open(csv_path, "rb") as source_file:
            job = client.load_table_from_file(
                source_file, table_id, job_config=job_config
            )
        
        job.result()  # Wait for the job to complete
        print(f"  [LOADED] {csv_path.name} -> {table_id.split('.')[-1]}")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to load {csv_path.name}: {e}")
        return False

def load_country_data(country: str, project_id: str = "osint-foresight-2025"):
    """Load processed data for a specific country into BigQuery"""
    
    client = bigquery.Client(project=project_id)
    base_path = Path("data/processed") / f"country={country}"
    
    if not base_path.exists():
        print(f"No data found for country: {country}")
        return
    
    print(f"\nLoading data for country: {country}")
    print("=" * 60)
    
    # Map local files to BigQuery tables
    file_mappings = {
        "relationships.csv": f"{project_id}.processed_data.relationships_{country}",
        "signals.csv": f"{project_id}.processed_data.signals_{country}",
        "standards_roles.tsv": f"{project_id}.processed_data.standards_roles_{country}",
        "institutions.csv": f"{project_id}.processed_data.institutions_{country}",
        "mechanism_incidents.tsv": f"{project_id}.processed_data.mechanism_incidents_{country}",
        "sanctions_hits.csv": f"{project_id}.processed_data.sanctions_hits_{country}",
        "cer_master.csv": f"{project_id}.processed_data.cer_master_{country}",
        "partners_cerlite.csv": f"{project_id}.processed_data.partners_cerlite_{country}",
    }
    
    loaded_count = 0
    for file_name, table_id in file_mappings.items():
        file_path = base_path / file_name
        
        # Create table with country suffix if it doesn't exist
        base_table_name = file_name.replace('.csv', '').replace('.tsv', '')
        if base_table_name in TABLE_SCHEMAS.get("processed_data", {}):
            schema = TABLE_SCHEMAS["processed_data"][base_table_name]
            
            # Add country field to schema
            schema_with_country = [
                bigquery.SchemaField("_country", "STRING", mode="REQUIRED", default_value_expression=f'"{country}"')
            ] + schema
            
            table = bigquery.Table(table_id, schema=schema_with_country)
            try:
                client.create_table(table)
                print(f"  [OK] Created country table: {table_id.split('.')[-1]}")
            except Conflict:
                pass  # Table exists
            
            # Load data
            if file_path.exists():
                if load_data_from_csv(client, table_id, file_path):
                    loaded_count += 1
    
    print(f"\nLoaded {loaded_count} files for {country}")

def main():
    """Main function to set up tables and optionally load data"""
    
    project_id = "osint-foresight-2025"
    
    # Create base tables
    created, existing = create_tables(project_id)
    
    # Check for available country data
    data_dir = Path("data/processed")
    if data_dir.exists():
        countries = []
        for country_dir in data_dir.glob("country=*"):
            country_code = country_dir.name.split("=")[1]
            countries.append(country_code)
        
        if countries:
            print(f"\nFound data for countries: {', '.join(countries)}")
            
            response = input("\nLoad data for these countries? (y/n): ")
            if response.lower() == 'y':
                for country in countries:
                    load_country_data(country, project_id)
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print(f"\nAccess your data at:")
    print(f"https://console.cloud.google.com/bigquery?project={project_id}")
    
    # Show sample queries
    print("\nSample BigQuery queries to get started:")
    print("-" * 40)
    print("""
1. View relationships for Austria:
   SELECT * FROM `osint-foresight-2025.processed_data.relationships_AT` LIMIT 100

2. Sector intensity analysis:
   SELECT sector, COUNT(*) as edge_count, 
          COUNTIF(year BETWEEN 2023 AND 2025) as recent_edges
   FROM `osint-foresight-2025.processed_data.relationships_AT`
   GROUP BY sector
   ORDER BY edge_count DESC

3. Top international partners:
   SELECT counterpart_country, COUNT(*) as collaborations
   FROM `osint-foresight-2025.processed_data.relationships_AT`
   WHERE counterpart_country IS NOT NULL
   GROUP BY counterpart_country
   ORDER BY collaborations DESC
   LIMIT 10
""")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)