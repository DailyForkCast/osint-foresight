#!/usr/bin/env python3
"""
Set up BigQuery datasets for OSINT Foresight Analysis
"""
import subprocess
import json
import sys

def run_gcloud_command(cmd):
    """Run a gcloud command and return the output"""
    gcloud_path = r"C:\Users\mrear\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud"
    full_cmd = f'"{gcloud_path}" {cmd}'
    
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
        return result.stdout
    except Exception as e:
        print(f"Failed to run command: {e}")
        return None

def create_dataset_with_gcloud():
    """Create BigQuery dataset using gcloud CLI"""
    project_id = "osint-foresight-2025"
    
    # Create the datasets using bq command through gcloud
    datasets = [
        {
            "name": "main_analysis",
            "description": "Main OSINT Foresight analysis dataset",
            "location": "US"
        },
        {
            "name": "patent_analysis", 
            "description": "Patent data analysis and results",
            "location": "US"
        },
        {
            "name": "country_reports",
            "description": "Country-specific analysis results",
            "location": "US"
        }
    ]
    
    print(f"Creating BigQuery datasets in project: {project_id}")
    print("-" * 60)
    
    for dataset in datasets:
        dataset_id = f"{project_id}.{dataset['name']}"
        
        # Use gcloud to run bq commands
        bq_cmd = f'alpha bq datasets create {dataset["name"]} --location={dataset["location"]} --description="{dataset["description"]}"'
        
        print(f"\nCreating dataset: {dataset['name']}")
        print(f"  Description: {dataset['description']}")
        print(f"  Location: {dataset['location']}")
        
        result = run_gcloud_command(bq_cmd)
        
        if result is not None:
            print(f"  ✓ Dataset created successfully")
        else:
            # Try alternate method using direct API call
            api_cmd = f"""alpha bq operations create --project={project_id} --dataset={dataset["name"]} --location={dataset["location"]}"""
            result = run_gcloud_command(api_cmd)
            if result:
                print(f"  ✓ Dataset created via API")
            else:
                print(f"  ✗ Failed to create dataset")
    
    print("\n" + "-" * 60)
    print("Setup complete!")
    print(f"\nAccess your datasets at:")
    print(f"https://console.cloud.google.com/bigquery?project={project_id}")

def main():
    # First verify we're authenticated and have the right project
    project_check = run_gcloud_command("config get-value project")
    if project_check and "osint-foresight-2025" in project_check:
        print(f"✓ Using project: osint-foresight-2025\n")
        create_dataset_with_gcloud()
    else:
        print("Error: Please ensure gcloud is configured with project osint-foresight-2025")
        sys.exit(1)

if __name__ == "__main__":
    main()