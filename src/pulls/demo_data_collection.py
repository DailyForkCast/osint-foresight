#!/usr/bin/env python3
"""
Demo script for collecting data from free public sources
Shows how to get procurement and trade data for OSINT analysis
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def demo_ted_search():
    """Demo: Search TED for Austrian technology contracts"""
    print("\n=== TED (EU Tenders) Demo ===")
    print("Note: TED API requires proper authentication/format")
    print("Manual access: https://ted.europa.eu/en/")
    print("Search for: country:AT AND cpv:72* (IT services)")
    
def demo_national_procurement():
    """Demo: National procurement portals"""
    print("\n=== National Procurement Portals ===")
    
    portals = {
        'Austria': {
            'BBG': 'https://www.bbg.gv.at/',
            'data.gv.at': 'https://www.data.gv.at/'
        },
        'Slovakia': {
            'UVO': 'https://www.uvo.gov.sk/',
            'EVO': 'https://www.evo.gov.sk/'
        },
        'Ireland': {
            'eTenders': 'https://www.etenders.gov.ie/'
        },
        'Portugal': {
            'BASE': 'https://www.base.gov.pt/'
        }
    }
    
    for country, sites in portals.items():
        print(f"\n{country}:")
        for name, url in sites.items():
            print(f"  - {name}: {url}")
    
    print("\nMost portals offer CSV export after manual search")

def demo_worldbank_data():
    """Demo: Get economic indicators from World Bank"""
    print("\n=== World Bank Data API Demo ===")
    
    # GDP for Austria
    indicator = "NY.GDP.MKTP.CD"  # GDP in current USD
    country = "AT"
    
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {
        'format': 'json',
        'per_page': 5,
        'date': '2019:2023'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.ok:
            data = response.json()
            if len(data) > 1 and data[1]:
                print(f"Austria GDP (last 5 years):")
                for record in data[1]:
                    year = record.get('date')
                    value = record.get('value')
                    if value:
                        print(f"  {year}: ${value:,.0f}")
            else:
                print("No data returned")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def demo_openalex_search():
    """Demo: Search OpenAlex for AI research from Austria"""
    print("\n=== OpenAlex API Demo ===")
    
    # Search for AI papers from Austrian institutions
    params = {
        'filter': 'institutions.country_code:AT,concepts.id:C154945302',  # Austria + AI
        'per_page': 5,
        'sort': 'cited_by_count:desc'
    }
    
    url = "https://api.openalex.org/works"
    
    try:
        response = requests.get(url, params=params)
        if response.ok:
            data = response.json()
            results = data.get('results', [])
            print(f"Top AI papers from Austrian institutions:")
            for i, work in enumerate(results[:3], 1):
                title = work.get('title', 'No title')
                year = work.get('publication_year')
                citations = work.get('cited_by_count', 0)
                print(f"{i}. ({year}) {title[:60]}...")
                print(f"   Citations: {citations}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def demo_crossref_events():
    """Demo: Get Crossref Event Data"""
    print("\n=== Crossref Event Data Demo ===")
    
    # Get recent events for a DOI
    doi = "10.1038/nature12373"  # Example high-impact paper
    
    url = f"https://api.eventdata.crossref.org/v1/events"
    params = {
        'obj-id': doi,
        'rows': 5
    }
    
    try:
        response = requests.get(url, params=params)
        if response.ok:
            data = response.json()
            events = data.get('message', {}).get('events', [])
            if events:
                print(f"Recent events for DOI {doi}:")
                for event in events[:3]:
                    source = event.get('source_id', 'unknown')
                    action = event.get('relation_type_id', 'unknown')
                    date = event.get('occurred_at', '')[:10]
                    print(f"  {date}: {action} by {source}")
            else:
                print("No events found")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def demo_epo_patents():
    """Demo: European Patent Office data"""
    print("\n=== EPO Patent Data ===")
    print("EPO OPS API requires registration for API key")
    print("Manual search: https://worldwide.espacenet.com/")
    print("Search example: applicant='Austrian' AND IPC='G06N' (AI patents)")
    
def demo_data_summary():
    """Summary of available data sources"""
    print("\n=== DATA SOURCES SUMMARY ===")
    
    sources = {
        'Fully Automated (API)': [
            'OpenAlex - Research publications',
            'Crossref - Publication metadata',
            'World Bank - Economic indicators',
            'CORDIS - EU projects (existing pull script)',
            'IETF - Standards participation (existing)',
            'GLEIF - Legal entities (existing)'
        ],
        'Semi-Automated (API with limits)': [
            'UN Comtrade - Trade flows (requires subscription)',
            'TED - EU tenders (complex authentication)',
            'EPO OPS - Patents (requires API key)'
        ],
        'Manual Export': [
            'National procurement portals',
            'ITC Trade Map',
            'WIPO Global Brand Database',
            'Accreditation bodies'
        ],
        'Large Downloads': [
            'OpenAlex bulk - 300GB via AWS S3',
            'Google Patents - via BigQuery'
        ]
    }
    
    for category, items in sources.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  - {item}")

def main():
    """Run all demos"""
    print("=" * 60)
    print("OSINT FORESIGHT - Data Collection Demo")
    print("=" * 60)
    
    # Run demos
    demo_worldbank_data()
    demo_openalex_search()
    demo_crossref_events()
    demo_ted_search()
    demo_national_procurement()
    demo_epo_patents()
    demo_data_summary()
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("Next steps:")
    print("1. Set up API keys where needed")
    print("2. Use existing pull scripts in src/pulls/")
    print("3. Schedule regular data updates")
    print("4. Store data in BigQuery for analysis")

if __name__ == '__main__':
    main()