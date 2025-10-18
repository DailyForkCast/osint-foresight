#!/usr/bin/env python3
"""
USPTO China Patent Search using the new API v1
"""

import requests
import json
from datetime import datetime
import os

# API configuration
API_KEY = "uahgtefkrhncejbsftgtsoseszhhdp"
BASE_URL = "https://api.uspto.gov/api/v1"

def search_uspto_datasets():
    """Search for available patent datasets"""

    print("=" * 60)
    print("USPTO Dataset Search")
    print("=" * 60)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
    }

    # Get available datasets
    url = f"{BASE_URL}/datasets/products/search?latest=true"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('count', 0)} datasets\n")

            # Look for patent-related datasets
            patent_datasets = []
            for product in data.get('bulkDataProductBag', []):
                if 'Patent' in str(product.get('productLabelArrayText', [])):
                    patent_datasets.append({
                        'id': product['productIdentifier'],
                        'title': product['productTitleText'],
                        'description': product['productDescriptionText'][:100],
                        'from_date': product.get('productFromDate'),
                        'to_date': product.get('productToDate'),
                        'file_count': product.get('productFileTotalQuantity', 0)
                    })

            print(f"Patent-related datasets: {len(patent_datasets)}\n")

            for ds in patent_datasets[:5]:  # Show first 5
                print(f"Dataset: {ds['id']}")
                print(f"  Title: {ds['title']}")
                print(f"  Description: {ds['description']}...")
                print(f"  Date range: {ds['from_date']} to {ds['to_date']}")
                print(f"  Files: {ds['file_count']}")
                print()

            return patent_datasets

        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error accessing USPTO API: {e}")

    return []

def download_patent_data(dataset_id, year=2024):
    """Download patent data for a specific dataset and year"""

    print(f"\nDownloading {dataset_id} data for {year}...")

    headers = {
        'Accept': 'application/json',
        'x-api-key': API_KEY
    }

    # Get files for this dataset
    url = f"{BASE_URL}/datasets/products/files/{dataset_id}/{year}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            if 'fileDataBag' in data:
                files = data['fileDataBag']
                print(f"Found {len(files)} files for {year}")

                # Save file list
                output_dir = f"F:/OSINT_DATA/USPTO_Patents/{dataset_id}"
                os.makedirs(output_dir, exist_ok=True)

                output_file = f"{output_dir}/file_list_{year}.json"
                with open(output_file, 'w') as f:
                    json.dump(files, f, indent=2)

                print(f"File list saved to: {output_file}")

                # Show sample files
                for file_info in files[:3]:
                    print(f"  - {file_info.get('fileName')} ({file_info.get('fileSize', 0)/1024/1024:.1f} MB)")

                return files

        elif response.status_code == 404:
            print(f"No data found for {year}")
        else:
            print(f"Error: {response.status_code}")

    except Exception as e:
        print(f"Error downloading data: {e}")

    return []

def search_china_patents():
    """Search for China-related patents in USPTO"""

    print("\n" + "=" * 60)
    print("Searching for China-related Patents")
    print("=" * 60)

    # First, get available datasets
    datasets = search_uspto_datasets()

    # Try to get recent patent grant data
    if datasets:
        # Look for patent grant dataset
        grant_datasets = [d for d in datasets if 'Grant' in d['title']]

        if grant_datasets:
            dataset_id = grant_datasets[0]['id']
            print(f"\nUsing dataset: {dataset_id}")

            # Try to download recent data
            for year in [2024, 2023, 2022]:
                files = download_patent_data(dataset_id, year)
                if files:
                    break

    # Save summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'datasets_found': len(datasets),
        'api_status': 'connected',
        'api_key': API_KEY[:10] + '...',
        'note': 'USPTO API v1 is for bulk data downloads. Patent search requires different endpoint.'
    }

    summary_file = f"F:/OSINT_DATA/USPTO_Patents/china_search_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(summary_file), exist_ok=True)

    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary saved to: {summary_file}")

    print("\nNOTE: This API provides bulk patent data downloads.")
    print("For patent search, consider using:")
    print("  1. PatentsView API (https://patentsview.org/apis)")
    print("  2. USPTO Patent Full-Text Search (https://ppubs.uspto.gov/pubwebapp/)")
    print("  3. Google Patents (via BigQuery)")

if __name__ == "__main__":
    search_china_patents()
