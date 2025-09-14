#!/usr/bin/env python3
"""
Quick load of key data files to BigQuery
"""
from pathlib import Path

try:
    from google.cloud import bigquery
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-cloud-bigquery"])
    from google.cloud import bigquery

def quick_load():
    """Load the most important files"""

    project_id = "osint-foresight-2025"
    client = bigquery.Client(project=project_id)

    # Key files to load
    files_to_load = [
        ("AT", "relationships.csv", "relationships_AT"),
        ("AT", "signals.csv", "signals_AT"),
        ("AT", "standards_roles.tsv", "standards_roles_AT"),
        ("PT", "relationships.csv", "relationships_PT"),
    ]

    print("Quick loading key data files to BigQuery")
    print("=" * 60)

    for country, filename, table_name in files_to_load:
        file_path = Path(f"data/processed/country={country}/{filename}")

        if not file_path.exists():
            print(f"[SKIP] {country}/{filename} - not found")
            continue

        # Determine delimiter
        delimiter = '\t' if filename.endswith('.tsv') else ','

        # Configure job with autodetect
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            field_delimiter=delimiter,
            autodetect=True,
            write_disposition="WRITE_TRUNCATE",
            create_disposition="CREATE_IF_NEEDED",
            max_bad_records=100,
        )

        table_id = f"{project_id}.processed_data.{table_name}"

        try:
            # Delete existing table if present
            try:
                client.delete_table(table_id)
                print(f"[CLEAN] Removed old {table_name}")
            except:
                pass

            # Load the file
            with open(file_path, "rb") as f:
                job = client.load_table_from_file(f, table_id, job_config=job_config)

            # Wait for completion (with timeout)
            result = job.result(timeout=30)

            # Check results
            table = client.get_table(table_id)
            print(f"[OK] {country}/{filename} -> {table_name}")
            print(f"     {table.num_rows} rows, {len(table.schema)} columns")

        except Exception as e:
            print(f"[ERROR] {country}/{filename}: {str(e)[:100]}")

    print("\n" + "=" * 60)
    print("Quick load complete!")
    print(f"\nView your data at:")
    print(f"https://console.cloud.google.com/bigquery?project={project_id}&ws=!1m4!1m3!3m2!1sosint-foresight-2025!2sprocessed_data")

    print("\nTest queries:")
    print("-" * 40)
    print("""
-- Austria relationships by sector
SELECT sector, COUNT(*) as count
FROM `osint-foresight-2025.processed_data.relationships_AT`
GROUP BY sector
ORDER BY count DESC;

-- View signals
SELECT * FROM `osint-foresight-2025.processed_data.signals_AT`;
""")

if __name__ == "__main__":
    quick_load()
