#!/usr/bin/env python3
"""
Explore Eurostat File Dissemination API Directories
Identify bulk download files for COMEXT trade data
Date: October 30, 2025
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json

# URLs to explore
EUROSTAT_URLS = [
    "https://ec.europa.eu/eurostat/api/dissemination/files/?sort=1&dir=comext%2FCOMEXT_DATA",
    "https://ec.europa.eu/eurostat/api/dissemination/files/?sort=1&dir=comext%2FCOMEXT_DATA%2FPRODUCTS",
    "https://ec.europa.eu/eurostat/api/dissemination/files/?sort=1&dir=comext%2FCOMEXT_DATA%2FTRANSPORT_HS",
    "https://ec.europa.eu/eurostat/api/dissemination/files/?sort=1&dir=comext%2FCOMEXT_DATA%2FTRANSPORT_NST07"
]

def parse_size(size_str):
    """Convert size string to bytes"""
    if not size_str or size_str == '-':
        return 0

    size_str = size_str.strip()
    multipliers = {
        'K': 1024,
        'M': 1024 * 1024,
        'G': 1024 * 1024 * 1024
    }

    match = re.match(r'([\d.]+)\s*([KMG])?', size_str, re.IGNORECASE)
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        if unit:
            return int(value * multipliers.get(unit.upper(), 1))
        return int(value)
    return 0

def explore_directory(url):
    """Parse Eurostat directory listing"""
    print(f"\n{'='*80}")
    print(f"Exploring: {url}")
    print(f"{'='*80}")

    try:
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            print(f"[ERROR] HTTP {response.status_code}")
            return []

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find table rows (directory listings are usually in tables)
        files = []

        # Look for links in the page
        for link in soup.find_all('a'):
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # Skip parent directory links
            if text in ['Parent Directory', '..', 'Up']:
                continue

            # Look for actual files
            if any(ext in text.lower() for ext in ['.dat', '.7z', '.zip', '.txt', '.csv', '.gz']):
                files.append({
                    'name': text,
                    'href': href,
                    'type': 'file'
                })
            elif href and not href.startswith('http'):
                # Subdirectory
                files.append({
                    'name': text,
                    'href': href,
                    'type': 'directory'
                })

        # Try to find table with file details
        tables = soup.find_all('table')
        if tables:
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        # Typical format: Name, Size, Date
                        name_col = cols[0].get_text(strip=True)
                        size_col = cols[1].get_text(strip=True) if len(cols) > 1 else '-'
                        date_col = cols[2].get_text(strip=True) if len(cols) > 2 else '-'

                        # Skip parent directory
                        if name_col in ['Parent Directory', '..']:
                            continue

                        # Get link
                        link = cols[0].find('a')
                        href = link.get('href', '') if link else ''

                        # Parse size
                        size_bytes = parse_size(size_col)

                        # Determine type
                        is_file = any(ext in name_col.lower() for ext in ['.dat', '.7z', '.zip', '.txt', '.csv', '.gz'])

                        files.append({
                            'name': name_col,
                            'href': href,
                            'size_str': size_col,
                            'size_bytes': size_bytes,
                            'date': date_col,
                            'type': 'file' if is_file else 'directory'
                        })

        # Display results
        if not files:
            print("[WARN] No files found in directory")
            print("\nRAW HTML (first 2000 chars):")
            print(response.text[:2000])
        else:
            print(f"\nFound {len(files)} items:")

            # Sort by type and size
            files.sort(key=lambda x: (x['type'], -x.get('size_bytes', 0)))

            # Display directories
            dirs = [f for f in files if f['type'] == 'directory']
            if dirs:
                print(f"\nDirectories ({len(dirs)}):")
                for d in dirs:
                    print(f"  📁 {d['name']}")

            # Display files
            file_list = [f for f in files if f['type'] == 'file']
            if file_list:
                print(f"\nFiles ({len(file_list)}):")
                for f in file_list:
                    size_str = f.get('size_str', '-')
                    date_str = f.get('date', '-')
                    size_bytes = f.get('size_bytes', 0)

                    # Highlight large files (>500MB)
                    if size_bytes > 500 * 1024 * 1024:
                        marker = "⭐ [BULK]"
                    elif size_bytes > 100 * 1024 * 1024:
                        marker = "📦 [LARGE]"
                    else:
                        marker = "📄"

                    print(f"  {marker} {f['name']}")
                    print(f"      Size: {size_str} | Date: {date_str}")
                    if f.get('href'):
                        print(f"      URL: {f['href']}")

        return files

    except Exception as e:
        print(f"[ERROR] Failed to explore directory: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("="*80)
    print("EUROSTAT FILE DISSEMINATION API EXPLORER")
    print("="*80)
    print("Searching for bulk COMEXT data files...")

    all_findings = {}

    # Explore each URL
    for url in EUROSTAT_URLS:
        files = explore_directory(url)
        all_findings[url] = files

    # Summary
    print("\n" + "="*80)
    print("SUMMARY - BULK FILES IDENTIFIED")
    print("="*80)

    bulk_files = []
    for url, files in all_findings.items():
        for f in files:
            if f['type'] == 'file' and f.get('size_bytes', 0) > 500 * 1024 * 1024:
                bulk_files.append({
                    'directory': url,
                    'file': f
                })

    if bulk_files:
        print(f"\nFound {len(bulk_files)} bulk files (>500MB):")
        for item in bulk_files:
            f = item['file']
            print(f"\n⭐ {f['name']}")
            print(f"   Size: {f.get('size_str', 'Unknown')}")
            print(f"   Date: {f.get('date', 'Unknown')}")
            print(f"   Location: {item['directory']}")
            if f.get('href'):
                print(f"   Download: {f['href']}")
    else:
        print("\n[WARN] No bulk files (>500MB) found")
        print("\nNext steps:")
        print("1. Check subdirectories in PRODUCTS folder")
        print("2. Look for annual/monthly data files")
        print("3. Contact Eurostat support if needed")

    # Save results
    output_file = Path("analysis/eurostat_file_exploration_20251030.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_findings, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Full results saved to: {output_file}")

if __name__ == '__main__':
    main()
