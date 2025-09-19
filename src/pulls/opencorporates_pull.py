#!/usr/bin/env python3
"""
OpenCorporates API Pull Script
Free corporate registry data from the world's largest open company database
200M+ companies from 140+ jurisdictions
"""

import argparse
import time
import json
import requests
from datetime import date
from pathlib import Path
import os

CONTACT = os.getenv("CONTACT_EMAIL", "research@example.org")
UA = {"User-Agent": f"osint-foresight/0.1 (mailto:{CONTACT})"}
BASE = "https://api.opencorporates.com/v0.4"

# Rate limiting: 200 requests per month for free tier
RATE_LIMIT_DELAY = 1.0

def get(path, params=None):
    """Make API request with error handling and rate limiting"""
    url = f"{BASE}/{path.lstrip('/')}"
    time.sleep(RATE_LIMIT_DELAY)

    for attempt in range(3):
        try:
            r = requests.get(url, params=params or {}, headers=UA, timeout=30)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                print(f"Rate limited, waiting 60 seconds...")
                time.sleep(60)
                continue
            elif r.status_code == 403:
                print(f"Access denied - check API key or rate limits")
                return None
            else:
                print(f"API error {r.status_code}: {r.text}")
                return None
        except Exception as e:
            print(f"Request error: {e}")
            if attempt < 2:
                time.sleep(5)
                continue
            return None
    return None

def search_companies(jurisdiction, query, per_page=30, max_pages=5):
    """Search for companies in a jurisdiction"""
    companies = []

    for page in range(1, max_pages + 1):
        params = {
            'jurisdiction_code': jurisdiction,
            'q': query,
            'per_page': per_page,
            'page': page
        }

        print(f"Searching page {page} for '{query}' in {jurisdiction}...")
        data = get("companies/search", params)

        if not data or 'companies' not in data.get('results', {}):
            break

        page_companies = data['results']['companies']
        if not page_companies:
            break

        companies.extend(page_companies)

        # Check if we have more pages
        total_pages = data['results'].get('total_pages', 1)
        if page >= total_pages:
            break

    return companies

def get_company_details(company_number, jurisdiction):
    """Get detailed company information"""
    path = f"companies/{jurisdiction}/{company_number}"
    data = get(path)

    if data and 'company' in data.get('results', {}):
        return data['results']['company']
    return None

def main():
    ap = argparse.ArgumentParser(description="OpenCorporates data collection")
    ap.add_argument("--jurisdiction", required=True, help="Jurisdiction code (e.g., 'cn', 'de', 'us_ca')")
    ap.add_argument("--query", required=True, help="Search query")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--per_page", type=int, default=30, help="Results per page")
    ap.add_argument("--max_pages", type=int, default=5, help="Maximum pages to fetch")
    ap.add_argument("--details", action='store_true', help="Fetch detailed company info")
    args = ap.parse_args()

    outdir = Path(args.out) / f"jurisdiction={args.jurisdiction}" / f"date={date.today()}"
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Searching OpenCorporates for '{args.query}' in {args.jurisdiction}")

    # Search for companies
    companies = search_companies(args.jurisdiction, args.query, args.per_page, args.max_pages)

    if not companies:
        print("No companies found")
        return

    # Save search results
    search_file = outdir / f"search_results_{args.query.replace(' ', '_')}.jsonl"
    with search_file.open("w", encoding="utf-8") as f:
        for company in companies:
            f.write(json.dumps(company, ensure_ascii=False) + "\n")

    print(f"Saved {len(companies)} companies to {search_file}")

    # Optionally fetch detailed information
    if args.details and len(companies) <= 50:  # Limit detailed fetching
        details_file = outdir / f"company_details_{args.query.replace(' ', '_')}.jsonl"
        detailed_count = 0

        with details_file.open("w", encoding="utf-8") as f:
            for company in companies:
                company_number = company.get('company_number')
                if company_number:
                    print(f"Fetching details for {company_number}...")
                    details = get_company_details(company_number, args.jurisdiction)
                    if details:
                        f.write(json.dumps(details, ensure_ascii=False) + "\n")
                        detailed_count += 1

        print(f"Saved {detailed_count} detailed company records")

    # Summary
    print("\nCollection Summary:")
    print(f"Jurisdiction: {args.jurisdiction}")
    print(f"Query: {args.query}")
    print(f"Companies found: {len(companies)}")
    print(f"Output directory: {outdir}")

if __name__ == "__main__":
    main()
