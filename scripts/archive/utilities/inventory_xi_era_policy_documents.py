#!/usr/bin/env python3
"""
Comprehensive inventory of Xi Jinping-era policy documents (2012-2025)
Checks what we have and identifies gaps for collection
"""

import json
import os
from datetime import datetime
from collections import defaultdict

# Master list of critical Xi Jinping-era policy documents
CRITICAL_DOCUMENTS = {
    "five_year_plans": [
        {"name": "11th Five Year Plan", "period": "2006-2010", "year": 2006, "priority": "MEDIUM"},
        {"name": "12th Five Year Plan", "period": "2011-2015", "year": 2011, "priority": "HIGH"},
        {"name": "13th Five Year Plan", "period": "2016-2020", "year": 2016, "priority": "HIGH"},
        {"name": "14th Five Year Plan", "period": "2021-2025", "year": 2021, "priority": "CRITICAL"},
        {"name": "15th Five Year Plan Outline", "period": "2026-2030", "year": 2025, "priority": "HIGH"}
    ],
    "national_security": [
        {"name": "National Security Law", "year": 2015, "priority": "CRITICAL"},
        {"name": "Counter-Espionage Law", "year": 2014, "priority": "HIGH"},
        {"name": "Counter-Espionage Law (Revised)", "year": 2023, "priority": "CRITICAL"},
        {"name": "State Secrets Law", "year": 2010, "priority": "HIGH"},
        {"name": "State Secrets Law (Revised)", "year": 2024, "priority": "CRITICAL"},
        {"name": "Counter-Terrorism Law", "year": 2015, "priority": "HIGH"},
        {"name": "National Intelligence Law", "year": 2017, "priority": "CRITICAL"},
        {"name": "National Defense Law (Revised)", "year": 2020, "priority": "HIGH"},
        {"name": "National Security Strategy Outline", "year": 2015, "priority": "HIGH"}
    ],
    "cybersecurity": [
        {"name": "Cybersecurity Law", "year": 2017, "priority": "CRITICAL"},
        {"name": "Data Security Law", "year": 2021, "priority": "CRITICAL"},
        {"name": "Personal Information Protection Law", "year": 2021, "priority": "HIGH"},
        {"name": "Critical Information Infrastructure Protection Regulations", "year": 2021, "priority": "HIGH"},
        {"name": "Multi-Level Protection Scheme (MLPS) 2.0", "year": 2019, "priority": "HIGH"},
        {"name": "Cybersecurity Review Measures", "year": 2022, "priority": "HIGH"}
    ],
    "technology_strategy": [
        {"name": "Made in China 2025", "year": 2015, "priority": "CRITICAL"},
        {"name": "Internet Plus Action Plan", "year": 2015, "priority": "HIGH"},
        {"name": "New Generation Artificial Intelligence Development Plan", "year": 2017, "priority": "CRITICAL"},
        {"name": "National Innovation-Driven Development Strategy", "year": 2016, "priority": "HIGH"},
        {"name": "National Medium- and Long-Term Program for Science and Technology Development (2006-2020)", "year": 2006, "priority": "MEDIUM"},
        {"name": "National Informatization Development Strategy (2006-2020)", "year": 2006, "priority": "MEDIUM"},
        {"name": "New Infrastructure Development Plan", "year": 2020, "priority": "HIGH"},
        {"name": "Digital China Development Plan", "year": 2023, "priority": "HIGH"},
        {"name": "National Standardization Development Outline", "year": 2021, "priority": "MEDIUM"}
    ],
    "mcf_documents": [
        {"name": "Opinions on Military-Civil Fusion Development Strategy", "year": 2015, "priority": "CRITICAL"},
        {"name": "Military-Civil Fusion Development Strategy Outline", "year": 2016, "priority": "CRITICAL"},
        {"name": "Regulations on Weaponry and Equipment Acquisition", "year": 2015, "priority": "MEDIUM"},
        {"name": "Defense Science and Technology Industry Reform Opinions", "year": 2017, "priority": "HIGH"}
    ],
    "industrial_policy": [
        {"name": "Strategic Emerging Industries Development Plan (12th FYP)", "year": 2012, "priority": "HIGH"},
        {"name": "Strategic Emerging Industries Development Plan (13th FYP)", "year": 2016, "priority": "HIGH"},
        {"name": "Robotics Industry Development Plan (2016-2020)", "year": 2016, "priority": "MEDIUM"},
        {"name": "New Energy Vehicle Industry Development Plan (2021-2035)", "year": 2020, "priority": "HIGH"},
        {"name": "Integrated Circuit Industry Development Guidelines", "year": 2014, "priority": "HIGH"},
        {"name": "National Satellite Navigation Industry Development Plan", "year": 2013, "priority": "MEDIUM"}
    ],
    "international_strategy": [
        {"name": "Belt and Road Initiative Vision and Actions", "year": 2015, "priority": "CRITICAL"},
        {"name": "Global Security Initiative", "year": 2022, "priority": "HIGH"},
        {"name": "Global Development Initiative", "year": 2021, "priority": "HIGH"},
        {"name": "Global Civilization Initiative", "year": 2023, "priority": "MEDIUM"},
        {"name": "China's Arctic Policy White Paper", "year": 2018, "priority": "MEDIUM"},
        {"name": "China's Space Activities White Paper", "year": 2016, "priority": "MEDIUM"}
    ],
    "standards_technical": [
        {"name": "China Standards 2035", "year": 2020, "priority": "HIGH"},
        {"name": "National Big Data Strategy", "year": 2015, "priority": "HIGH"},
        {"name": "Blockchain Technology and Application White Paper", "year": 2016, "priority": "MEDIUM"},
        {"name": "6G Development White Paper", "year": 2020, "priority": "MEDIUM"}
    ]
}

# Search patterns for each document category
SEARCH_PATTERNS = {
    "five_year_plans": [
        "five year plan", "five-year plan", "fyp",
        "11th five", "12th five", "13th five", "14th five", "15th five"
    ],
    "national_security": [
        "national security law", "counter-espionage",
        "state secrets", "counter-terrorism", "intelligence law"
    ],
    "cybersecurity": [
        "cybersecurity law", "data security law",
        "personal information protection", "critical information infrastructure",
        "mlps", "multi-level protection"
    ],
    "technology_strategy": [
        "made in china 2025", "internet plus",
        "artificial intelligence development", "innovation-driven",
        "new infrastructure", "digital china"
    ],
    "mcf_documents": [
        "military-civil fusion", "mcf",
        "weaponry equipment", "defense science"
    ],
    "industrial_policy": [
        "strategic emerging industries", "robotics industry",
        "new energy vehicle", "integrated circuit", "semiconductor",
        "satellite navigation"
    ],
    "international_strategy": [
        "belt and road", "bri",
        "global security initiative", "global development initiative",
        "arctic policy", "space activities"
    ],
    "standards_technical": [
        "china standards 2035", "big data strategy",
        "blockchain", "6g development"
    ]
}

found_documents = defaultdict(list)
total_files_scanned = 0

def search_directory(directory_path, label):
    """Search a directory for Xi-era policy documents"""
    global total_files_scanned

    if not os.path.exists(directory_path):
        print(f"WARNING: Directory not found: {directory_path}")
        return

    print(f"Scanning {label}...")
    files_in_dir = 0

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.json'):
                files_in_dir += 1
                total_files_scanned += 1

                try:
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Extract text content
                    text_content = ""
                    title = ""

                    # Handle different JSON structures
                    if 'extracted_documents' in data:
                        for doc in data.get('extracted_documents', []):
                            title = doc.get('title', '').lower()
                            content = doc.get('content_text', '').lower()
                            text_content = f"{title} {content}"

                            # Check against all patterns
                            for category, patterns in SEARCH_PATTERNS.items():
                                for pattern in patterns:
                                    if pattern.lower() in text_content:
                                        found_documents[category].append({
                                            "title": doc.get('title', 'Unknown'),
                                            "source": doc.get('source_name', label),
                                            "url": doc.get('canonical_url', 'Unknown'),
                                            "date": doc.get('publish_date', 'Unknown'),
                                            "file": file,
                                            "matched_pattern": pattern,
                                            "category": category
                                        })
                                        break
                    else:
                        title = data.get('title', '').lower()
                        text_preview = str(data.get('text_preview', '')).lower()
                        content = str(data.get('content', '')).lower()
                        text_content = f"{title} {text_preview} {content}"

                        for category, patterns in SEARCH_PATTERNS.items():
                            for pattern in patterns:
                                if pattern.lower() in text_content:
                                    found_documents[category].append({
                                        "title": data.get('title', 'Unknown'),
                                        "source": data.get('source_name', label),
                                        "url": data.get('canonical_url', 'Unknown'),
                                        "date": data.get('publish_date', 'Unknown'),
                                        "file": file,
                                        "matched_pattern": pattern,
                                        "category": category
                                    })
                                    break

                except Exception as e:
                    continue

    print(f"  Scanned {files_in_dir} files in {label}")

# Execute search across all sweep directories
print("=" * 80)
print("XI JINPING-ERA POLICY DOCUMENTS INVENTORY")
print("=" * 80)
print()

search_directory('F:/China_Sweeps/data/', 'China Policy Sweeps')
search_directory('F:/Europe_China_Sweeps/RAW/', 'Europe-China Sweeps')
search_directory('F:/ThinkTank_Sweeps/', 'Think Tank Sweeps')

print()
print(f"Total files scanned: {total_files_scanned:,}")
print()

# Generate report
print("=" * 80)
print("INVENTORY RESULTS BY CATEGORY")
print("=" * 80)
print()

# Create detailed inventory report
inventory_report = {
    "scan_date": datetime.now().isoformat(),
    "files_scanned": total_files_scanned,
    "documents_found": {},
    "critical_gaps": [],
    "collection_priorities": {}
}

for category, doc_list in CRITICAL_DOCUMENTS.items():
    print(f"\n{'=' * 80}")
    print(f"{category.upper().replace('_', ' ')}")
    print('=' * 80)

    found_in_category = found_documents.get(category, [])

    for doc in doc_list:
        doc_name = doc['name']
        priority = doc['priority']
        year = doc.get('year', 'N/A')

        # Check if we found this document
        found_matches = [f for f in found_in_category if any(
            keyword in f['title'].lower()
            for keyword in doc_name.lower().split()
        )]

        if found_matches:
            print(f"\n[FOUND] {doc_name} ({year}) - {len(found_matches)} references")
            print(f"   Priority: {priority}")
            for match in found_matches[:3]:  # Show top 3 matches
                print(f"   - {match['title'][:80]}")
                print(f"     Source: {match['source']}, File: {match['file']}")

            inventory_report['documents_found'][doc_name] = {
                "status": "FOUND",
                "references": len(found_matches),
                "priority": priority,
                "year": year,
                "samples": found_matches[:3]
            }
        else:
            print(f"\n[MISSING] {doc_name} ({year})")
            print(f"   Priority: {priority}")

            inventory_report['documents_found'][doc_name] = {
                "status": "MISSING",
                "priority": priority,
                "year": year
            }

            if priority in ["CRITICAL", "HIGH"]:
                inventory_report['critical_gaps'].append({
                    "name": doc_name,
                    "year": year,
                    "priority": priority,
                    "category": category
                })

# Save detailed report
output_file = 'C:/Projects/OSINT - Foresight/MCF Presentations/xi_era_policy_inventory.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(inventory_report, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print("CRITICAL GAPS SUMMARY")
print("=" * 80)
print()

critical_gaps = [doc for doc in inventory_report['critical_gaps'] if doc['priority'] == 'CRITICAL']
high_priority_gaps = [doc for doc in inventory_report['critical_gaps'] if doc['priority'] == 'HIGH']

print(f"CRITICAL Priority Missing: {len(critical_gaps)}")
for gap in critical_gaps:
    print(f"   - {gap['name']} ({gap['year']})")

print()
print(f"HIGH Priority Missing: {len(high_priority_gaps)}")
for gap in high_priority_gaps:
    print(f"   - {gap['name']} ({gap['year']})")

print()
print(f"Detailed inventory saved to: {output_file}")
print()
print("=" * 80)
