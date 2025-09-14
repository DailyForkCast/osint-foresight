#!/usr/bin/env python3
"""
Create BigQuery datasets for OSINT Foresight using Google Cloud Python client
"""

import os
import sys

# Authentication will use Application Default Credentials
# Already configured via: gcloud auth application-default login

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import Conflict
except ImportError:
    print("Installing google-cloud-bigquery...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-cloud-bigquery"])
    from google.cloud import bigquery
    from google.cloud.exceptions import Conflict

def create_datasets():
    """Create BigQuery datasets for OSINT Foresight analysis"""

    # Initialize client with project
    project_id = "osint-foresight-2025"
    client = bigquery.Client(project=project_id)

    # Define datasets to create
    datasets = [
        {
            "dataset_id": "main_analysis",
            "description": "Main OSINT Foresight analysis dataset for multi-country technology assessment",
            "location": "US"
        },
        {
            "dataset_id": "patent_analysis",
            "description": "Patent data analysis including Google Patents queries and results",
            "location": "US"
        },
        {
            "dataset_id": "country_reports",
            "description": "Country-specific analysis results and aggregated metrics",
            "location": "US"
        },
        {
            "dataset_id": "raw_data",
            "description": "Raw data imports from various sources (CORDIS, CrossRef, etc.)",
            "location": "US"
        },
        {
            "dataset_id": "processed_data",
            "description": "Processed and normalized data ready for analysis",
            "location": "US"
        }
    ]

    print(f"Creating BigQuery datasets in project: {project_id}")
    print("=" * 60)

    created_count = 0
    for ds_config in datasets:
        dataset_id = f"{project_id}.{ds_config['dataset_id']}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.description = ds_config["description"]
        dataset.location = ds_config["location"]

        try:
            dataset = client.create_dataset(dataset, timeout=30)
            print(f"[OK] Created dataset: {ds_config['dataset_id']}")
            print(f"  Description: {ds_config['description']}")
            print(f"  Location: {ds_config['location']}")
            created_count += 1
        except Conflict:
            print(f"[EXISTS] Dataset {ds_config['dataset_id']} already exists")
        except Exception as e:
            print(f"[ERROR] Error creating {ds_config['dataset_id']}: {e}")

        print()

    print("=" * 60)
    print(f"Setup complete! Created {created_count} new datasets.")
    print(f"\nAccess your BigQuery workspace at:")
    print(f"https://console.cloud.google.com/bigquery?project={project_id}")

    # List all datasets
    print(f"\nAvailable datasets in {project_id}:")
    datasets = list(client.list_datasets())
    if datasets:
        for dataset in datasets:
            print(f"  - {dataset.dataset_id}")
    else:
        print("  No datasets found (may take a moment to appear)")

    return created_count

if __name__ == "__main__":
    try:
        create_datasets()
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're authenticated: gcloud auth application-default login")
        print("2. Verify project is set: gcloud config set project osint-foresight-2025")
        sys.exit(1)
