#!/usr/bin/env python
"""Test various trademark search options for Italian companies"""

import requests
import json
from datetime import datetime

def test_trademark_searches():
    """Test different trademark search approaches"""

    print("="*60)
    print("Trademark Search Options for Italian Companies")
    print("="*60)

    # Test company
    test_company = "Leonardo"

    results = {}

    # 1. WIPO Global Brand Database (Free, no API key required)
    print("\n1. Testing WIPO Global Brand Database...")
    try:
        wipo_url = "https://www3.wipo.int/branddb/en/"
        print(f"   Access URL: {wipo_url}")
        print("   Status: Available for web search")
        print("   Coverage: International trademarks including EU")
        results['WIPO'] = "Available - Web interface"
    except Exception as e:
        print(f"   Error: {e}")
        results['WIPO'] = "Error"

    # 2. EUIPO eSearch (Free web access)
    print("\n2. Testing EUIPO eSearch...")
    try:
        euipo_url = "https://euipo.europa.eu/eSearch/"
        print(f"   Access URL: {euipo_url}")
        print("   Status: Available for web search")
        print("   Coverage: EU trademarks and designs")
        results['EUIPO'] = "Available - Web interface"
    except Exception as e:
        print(f"   Error: {e}")
        results['EUIPO'] = "Error"

    # 3. TMview (EU trademark network)
    print("\n3. Testing TMview...")
    try:
        tmview_url = "https://www.tmdn.org/tmview/"
        print(f"   Access URL: {tmview_url}")
        print("   Status: Web search available")
        print("   Coverage: 70+ IP offices worldwide")
        results['TMview'] = "Available - Web interface"
    except Exception as e:
        print(f"   Error: {e}")
        results['TMview'] = "Error"

    # 4. Italian Patent and Trademark Office (UIBM)
    print("\n4. Testing Italian Patent and Trademark Office (UIBM)...")
    try:
        uibm_url = "https://www.uibm.gov.it/"
        print(f"   Access URL: {uibm_url}")
        print("   Database: https://www.uibm.gov.it/bancadati/")
        print("   Status: Italian national trademarks")
        print("   Coverage: Italy-specific registrations")
        results['UIBM'] = "Available - Italian database"
    except Exception as e:
        print(f"   Error: {e}")
        results['UIBM'] = "Error"

    # Summary
    print("\n" + "="*60)
    print("SUMMARY - Available Trademark Data Sources:")
    print("-"*60)

    print("\nFor Italian Technology Companies:")
    print("1. EUIPO eSearch - Best for EU trademarks")
    print("2. WIPO Global Brand - International coverage")
    print("3. UIBM - Italian national trademarks")
    print("4. TMview - Multi-jurisdiction search")

    print("\nRecommended Approach:")
    print("- Use EUIPO for EU trademark data (most relevant)")
    print("- Supplement with WIPO for international filings")
    print("- Check UIBM for Italy-only registrations")

    # Sample Italian tech companies to search
    print("\n" + "="*60)
    print("Key Italian Technology Companies to Search:")
    print("-"*60)

    companies = [
        "Leonardo S.p.A. (Defense/Aerospace)",
        "Fincantieri (Naval/Maritime)",
        "STMicroelectronics (Semiconductors)",
        "Telespazio (Space/Satellite)",
        "Engineering Ingegneria Informatica (IT Services)",
        "Datalogic (Industrial Automation)",
        "Ansaldo Energia (Energy Systems)",
        "IMA Group (Packaging Machinery)",
        "Prysmian (Cables/Energy)",
        "Reply (IT Consulting)"
    ]

    for company in companies:
        print(f"  - {company}")

    print("\n" + "="*60)

    # Create a simple CSV with search URLs
    print("\nGenerating search URLs for manual searches...")

    search_urls = []
    for company_full in companies:
        company = company_full.split("(")[0].strip()
        search_urls.append({
            'Company': company,
            'EUIPO_Search': f"https://euipo.europa.eu/eSearch/#advanced/trademarks/applicants/{company.replace(' ', '%20')}",
            'WIPO_Search': f"https://www3.wipo.int/branddb/en/# (search for: {company})"
        })

    # Save to file
    import csv
    output_file = "C:/Projects/OSINT - Foresight/data/collected/trademark_search_urls.csv"

    try:
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Company', 'EUIPO_Search', 'WIPO_Search'])
            writer.writeheader()
            writer.writerows(search_urls)

        print(f"Search URLs saved to: {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")

    print("\n" + "="*60)
    print("Next Steps:")
    print("1. Use the generated URLs for manual searches")
    print("2. Consider web scraping for automation")
    print("3. Export results from web interfaces")
    print("="*60)

if __name__ == "__main__":
    test_trademark_searches()
