#!/usr/bin/env python3
"""
Check what Five Year Plan documents we have and identify gaps
"""

import json
import os

# Five Year Plans we should look for
fyp_list = {
    "9th": "1996-2000",
    "10th": "2001-2005",
    "11th": "2006-2010",
    "12th": "2011-2015",
    "13th": "2016-2020",
    "14th": "2021-2025",
    "15th": "2026-2030"
}

found_fyps = {
    "documents": [],
    "mentions": []
}

# Search China_Sweeps
for root, dirs, files in os.walk('F:/China_Sweeps/data/'):
    for file in files:
        if file.endswith('.json'):
            try:
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Check if it's a collection file
                if 'extracted_documents' in data:
                    for doc in data.get('extracted_documents', []):
                        title = doc.get('title', '').lower()
                        content = doc.get('content_text', '').lower()

                        # Check for FYP mentions
                        for fyp_num, period in fyp_list.items():
                            patterns = [
                                f"{fyp_num} five",
                                f"{fyp_num} five-year",
                                period,
                                fyp_num.replace("th", "")
                            ]

                            for pattern in patterns:
                                if pattern in title or pattern in content:
                                    found_fyps["mentions"].append({
                                        "fyp": f"{fyp_num} FYP ({period})",
                                        "title": doc.get('title', 'Unknown'),
                                        "source": doc.get('source_name', 'Unknown'),
                                        "url": doc.get('canonical_url', 'Unknown'),
                                        "file": file
                                    })
                                    break
            except Exception as e:
                pass

# Search Europe_China_Sweeps
for root, dirs, files in os.walk('F:/Europe_China_Sweeps/RAW/'):
    for file in files:
        if file.endswith('.json'):
            try:
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                title = data.get('title', '').lower()
                content = str(data.get('text_preview', '')).lower()

                for fyp_num, period in fyp_list.items():
                    patterns = [f"{fyp_num} five", f"{fyp_num} five-year", period]
                    for pattern in patterns:
                        if pattern in title or pattern in content:
                            found_fyps["mentions"].append({
                                "fyp": f"{fyp_num} FYP ({period})",
                                "title": data.get('title', 'Unknown'),
                                "source": data.get('source_name', 'Unknown'),
                                "url": data.get('canonical_url', 'Unknown'),
                                "file": file
                            })
                            break
            except Exception as e:
                pass

# Remove duplicates
unique_mentions = []
seen = set()
for item in found_fyps["mentions"]:
    key = (item["fyp"], item["title"])
    if key not in seen:
        seen.add(key)
        unique_mentions.append(item)

print("=" * 80)
print("FIVE YEAR PLAN DOCUMENT INVENTORY")
print("=" * 80)
print()

print(f"FOUND: {len(unique_mentions)} documents mentioning Five Year Plans")
print()

if unique_mentions:
    print("DOCUMENTS WITH FYP MENTIONS:")
    print("-" * 80)
    for item in unique_mentions:
        print(f"\n{item['fyp']}")
        print(f"  Title: {item['title']}")
        print(f"  Source: {item['source']}")
        if item['url'] != 'Unknown':
            print(f"  URL: {item['url']}")
        print(f"  File: {item['file']}")
else:
    print("No Five Year Plan documents found in current collection.")

print()
print("=" * 80)
print("GAPS IDENTIFIED:")
print("=" * 80)

fyps_found = set([item['fyp'].split()[0] for item in unique_mentions])
for fyp_num, period in fyp_list.items():
    if fyp_num not in fyps_found:
        print(f"  ❌ {fyp_num} Five Year Plan ({period}) - NOT FOUND")
    else:
        print(f"  ✓ {fyp_num} Five Year Plan ({period}) - Mentioned")

print()
print("=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print()
print("We should specifically collect the full official Five Year Plan documents.")
print("Best sources:")
print("  1. China Copyright & Media (Rogier Creemers) - has English translations")
print("  2. National Development and Reform Commission (NDRC) - official source")
print("  3. Xinhua News Agency - official announcements")
print()
print("Priority order: 14th (current), 13th, 12th, 11th for past 20 years")
