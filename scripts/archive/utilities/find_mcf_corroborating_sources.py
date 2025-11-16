#!/usr/bin/env python3
"""
Find corroborating sources from sweeps for MCF presentation claims
"""

import json
import os
import sqlite3
from pathlib import Path
from collections import defaultdict
import re

# MCF-related keywords to search for
MCF_KEYWORDS = {
    "mcf_direct": ["military-civil fusion", "军民融合", "mcf", "civil-military integration"],
    "legal_framework": ["national security law", "intelligence law", "data security law", "state secrets"],
    "talent_programs": ["thousand talents", "changjiang scholars", "talent recruitment"],
    "technology_domains": ["semiconductors", "quantum", "artificial intelligence", "aerospace", "biotechnology"],
    "bri": ["belt and road", "一带一路", "bri", "new silk road"],
    "initiatives": ["global security initiative", "global development initiative", "global civilization initiative"],
    "institutions": ["sastind", "most", "mofcom", "miit", "sasac"],
    "universities": ["seven sons", "beihang", "harbin institute", "northwestern polytechnical"],
}

results = {
    "china_sweeps": [],
    "europe_china_sweeps": [],
    "thinktank_sweeps": [],
    "thinktank_database": []
}

def search_json_file(filepath, keywords_dict):
    """Search JSON file for MCF-related keywords"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert to string for searching
        content = json.dumps(data, ensure_ascii=False).lower()

        matches = {}
        for category, keywords in keywords_dict.items():
            for keyword in keywords:
                if keyword.lower() in content:
                    if category not in matches:
                        matches[category] = []
                    matches[category].append(keyword)

        if matches:
            return {
                "file": str(filepath),
                "matches": matches,
                "title": data.get("title", data.get("Title", "Unknown")),
                "date": data.get("date", data.get("Date", data.get("publication_date", "Unknown"))),
                "source": data.get("source", data.get("Source", "Unknown"))
            }
    except Exception as e:
        pass
    return None

# 1. Search China_Sweeps
print("Searching China_Sweeps...")
china_sweeps_path = Path("F:/China_Sweeps/data")
if china_sweeps_path.exists():
    for json_file in china_sweeps_path.glob("*.json"):
        result = search_json_file(json_file, MCF_KEYWORDS)
        if result:
            results["china_sweeps"].append(result)

print(f"  Found {len(results['china_sweeps'])} relevant documents")

# 2. Search Europe_China_Sweeps
print("Searching Europe_China_Sweeps...")
europe_china_path = Path("F:/Europe_China_Sweeps/RAW")
if europe_china_path.exists():
    for json_file in europe_china_path.rglob("*.json"):
        result = search_json_file(json_file, MCF_KEYWORDS)
        if result:
            results["europe_china_sweeps"].append(result)

print(f"  Found {len(results['europe_china_sweeps'])} relevant documents")

# 3. Search ThinkTank PDFs metadata (we can't read PDFs but can use filenames)
print("Searching ThinkTank_Sweeps filenames...")
thinktank_path = Path("F:/ThinkTank_Sweeps")
if thinktank_path.exists():
    for pdf_file in thinktank_path.rglob("*.pdf"):
        filename = pdf_file.name.lower()
        matches = {}
        for category, keywords in MCF_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in filename:
                    if category not in matches:
                        matches[category] = []
                    matches[category].append(keyword)

        if matches:
            results["thinktank_sweeps"].append({
                "file": str(pdf_file),
                "matches": matches,
                "filename": pdf_file.name
            })

print(f"  Found {len(results['thinktank_sweeps'])} relevant PDFs")

# 4. Query thinktank database
print("Searching thinktank database...")
try:
    conn = sqlite3.connect("F:/OSINT_WAREHOUSE/osint_master.db")
    cursor = conn.cursor()

    # Search for MCF-related reports
    search_terms = [
        "China", "military", "fusion", "technology transfer", "semiconductor",
        "quantum", "AI", "Belt and Road", "BRI", "talent", "espionage",
        "dual-use", "export control", "intellectual property"
    ]

    for term in search_terms:
        cursor.execute("""
            SELECT source_name, title, abstract, publication_date, url, file_path
            FROM thinktank_reports
            WHERE title LIKE ? OR abstract LIKE ?
            ORDER BY publication_date DESC
            LIMIT 10
        """, (f"%{term}%", f"%{term}%"))

        for row in cursor.fetchall():
            results["thinktank_database"].append({
                "source": row[0],
                "title": row[1],
                "abstract": row[2],
                "date": row[3],
                "url": row[4],
                "file_path": row[5],
                "search_term": term
            })

    conn.close()
    print(f"  Found {len(results['thinktank_database'])} relevant reports")
except Exception as e:
    print(f"  Database query error: {e}")

# 5. Organize results by MCF presentation slide
organized = {
    "slide_3_historical_context": [],
    "slide_4_what_is_mcf": [],
    "slide_5_strategic_objectives": [],
    "slide_6_policy_evolution": [],
    "slide_7_legal_architecture": [],
    "slide_8_institutional_architecture": [],
    "slide_9_strategic_approach": [],
    "slide_10_transfer_mechanisms": [],
    "slide_11_priority_domains": [],
    "slide_12_mcf_to_nqpf": [],
    "slide_13_global_initiatives": [],
    "slide_14_track_record": [],
    "slide_15_global_engagement": [],
}

# Map results to slides based on content
for source_type, items in results.items():
    for item in items:
        matches = item.get("matches", {})

        # Legal framework -> Slide 7
        if "legal_framework" in matches:
            organized["slide_7_legal_architecture"].append({
                "source_type": source_type,
                "item": item
            })

        # Institutions -> Slide 8
        if "institutions" in matches or "universities" in matches:
            organized["slide_8_institutional_architecture"].append({
                "source_type": source_type,
                "item": item
            })

        # Technology domains -> Slide 11
        if "technology_domains" in matches:
            organized["slide_11_priority_domains"].append({
                "source_type": source_type,
                "item": item
            })

        # BRI -> Slide 13, 15
        if "bri" in matches:
            organized["slide_13_global_initiatives"].append({
                "source_type": source_type,
                "item": item
            })
            organized["slide_15_global_engagement"].append({
                "source_type": source_type,
                "item": item
            })

        # Initiatives -> Slide 13
        if "initiatives" in matches:
            organized["slide_13_global_initiatives"].append({
                "source_type": source_type,
                "item": item
            })

        # Talent programs -> Slide 10, 15
        if "talent_programs" in matches:
            organized["slide_10_transfer_mechanisms"].append({
                "source_type": source_type,
                "item": item
            })

# Save results
output_file = "C:/Projects/OSINT - Foresight/mcf_corroborating_sources.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        "summary": {
            "china_sweeps_count": len(results["china_sweeps"]),
            "europe_china_sweeps_count": len(results["europe_china_sweeps"]),
            "thinktank_sweeps_count": len(results["thinktank_sweeps"]),
            "thinktank_database_count": len(results["thinktank_database"]),
            "total_sources": sum(len(v) for v in results.values())
        },
        "by_source_type": results,
        "by_presentation_slide": organized
    }, f, indent=2, ensure_ascii=False)

print(f"\n=== SUMMARY ===")
print(f"China Sweeps: {len(results['china_sweeps'])} sources")
print(f"Europe-China Sweeps: {len(results['europe_china_sweeps'])} sources")
print(f"ThinkTank PDFs: {len(results['thinktank_sweeps'])} sources")
print(f"ThinkTank Database: {len(results['thinktank_database'])} sources")
print(f"TOTAL: {sum(len(v) for v in results.values())} corroborating sources")
print(f"\nResults saved to: {output_file}")
