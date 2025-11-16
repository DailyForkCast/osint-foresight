#!/usr/bin/env python3
"""
ASPI Italy Infrastructure Analyzer
Extracts and analyzes Chinese infrastructure presence in Italy
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def analyze_italy_infrastructure():
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get all Italy infrastructure
    italy_infra = conn.execute("""
        SELECT
            company_name,
            infrastructure_type,
            secondary_infrastructure_type,
            city,
            label,
            year_commenced,
            year_ended,
            primary_topic,
            secondary_topic,
            third_topic,
            description,
            is_soe
        FROM aspi_infrastructure
        WHERE country_name = 'Italy'
        ORDER BY year_commenced DESC
    """).fetchall()

    # Statistics
    total = len(italy_infra)

    # By company
    by_company = defaultdict(int)
    for row in italy_infra:
        by_company[row['company_name']] += 1

    # By infrastructure type
    by_type = defaultdict(int)
    for row in italy_infra:
        by_type[row['infrastructure_type']] += 1

    # By technology topic
    by_topic = defaultdict(int)
    for row in italy_infra:
        if row['primary_topic']:
            by_topic[row['primary_topic']] += 1
        if row['secondary_topic']:
            by_topic[row['secondary_topic']] += 1
        if row['third_topic']:
            by_topic[row['third_topic']] += 1

    # By year
    by_year = defaultdict(int)
    for row in italy_infra:
        if row['year_commenced']:
            by_year[row['year_commenced']] += 1

    # By city
    by_city = defaultdict(int)
    for row in italy_infra:
        if row['city']:
            by_city[row['city']] += 1

    conn.close()

    # Generate report
    report = f"""# ASPI China Tech Map - Italy Infrastructure Analysis
**Generated:** {datetime.now().isoformat()}

## Overview

**Total Chinese Infrastructure Projects in Italy: {total}**

Italy ranks **#18 globally** out of 146 countries for Chinese infrastructure presence.

---

## Company Presence

| Company | Projects | % of Italy Total |
|---------|----------|------------------|
"""

    for company, count in sorted(by_company.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        report += f"| {company} | {count} | {pct:.1f}% |\n"

    report += f"""\n---

## Infrastructure Types

| Type | Count | % of Italy Total |
|------|-------|------------------|
"""

    for itype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        report += f"| {itype} | {count} | {pct:.1f}% |\n"

    report += f"""\n---

## Technology Focus

| Technology Topic | Mentions | % of Italy Total |
|-----------------|----------|------------------|
"""

    for topic, count in sorted(by_topic.items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = (count / total * 100) if total > 0 else 0
        report += f"| {topic} | {count} | {pct:.1f}% |\n"

    report += f"""\n---

## Timeline Analysis

| Year | Projects Started | Cumulative |
|------|-----------------|------------|
"""

    cumulative = 0
    for year in sorted([y for y in by_year.keys() if y], reverse=True):
        count = by_year[year]
        cumulative += count
        report += f"| {year} | {count} | {cumulative} |\n"

    report += f"""\n---

## Geographic Distribution

| City | Projects |
|------|----------|
"""

    for city, count in sorted(by_city.items(), key=lambda x: x[1], reverse=True)[:10]:
        report += f"| {city} | {count} |\n"

    report += f"""\n---

## Detailed Project List

"""

    for i, row in enumerate(italy_infra, 1):
        year = row['year_commenced'] if row['year_commenced'] else 'Unknown'
        city = row['city'] if row['city'] else 'Unknown'
        topic = row['primary_topic'] if row['primary_topic'] else 'Unspecified'

        report += f"""### {i}. {row['label'] if row['label'] else 'Unnamed Project'}
- **Company:** {row['company_name']}
- **Type:** {row['infrastructure_type']}
- **Location:** {city}
- **Year:** {year}
- **Topic:** {topic}
- **Description:** {row['description'][:200] if row['description'] else 'No description available'}...

"""

    report += f"""\n---

## Key Findings

### High-Risk Companies in Italy:
"""

    # Check which Italy companies are on BIS list
    conn = sqlite3.connect(Path("F:/OSINT_WAREHOUSE/osint_master.db"))
    bis_in_italy = conn.execute("""
        SELECT DISTINCT a.company_name, COUNT(*) as project_count
        FROM aspi_infrastructure a
        JOIN bis_entity_list_fixed b ON UPPER(b.entity_name) LIKE '%' || UPPER(a.company_name) || '%'
        WHERE a.country_name = 'Italy'
        GROUP BY a.company_name
    """).fetchall()
    conn.close()

    if bis_in_italy:
        for company, count in bis_in_italy:
            report += f"- **{company}**: {count} projects (ON BIS ENTITY LIST)\n"
    else:
        report += "- No companies on BIS Entity List detected in Italy data\n"

    report += f"""
### Infrastructure Concentration:
- Top company: {max(by_company.items(), key=lambda x: x[1])[0]} ({max(by_company.values())} projects, {max(by_company.values())/total*100:.1f}%)
- Top infrastructure type: {max(by_type.items(), key=lambda x: x[1])[0]} ({max(by_type.values())} projects)
- Top technology: {max(by_topic.items(), key=lambda x: x[1])[0] if by_topic else 'None'} ({max(by_topic.values()) if by_topic else 0} mentions)

### Timeline:
- Most active year: {max(by_year.items(), key=lambda x: x[1])[0] if by_year else 'Unknown'} ({max(by_year.values()) if by_year else 0} projects)
- Geographic spread: {len(by_city)} cities

---

## Strategic Assessment

**Italy Infrastructure Significance:**
- Ranks #18 globally ({total} projects)
- Represents {total/3947*100:.2f}% of total global Chinese tech infrastructure
- Primary focus: {max(by_type.items(), key=lambda x: x[1])[0] if by_type else 'Unknown'}
- Technology emphasis: {max(by_topic.items(), key=lambda x: x[1])[0] if by_topic else 'Unknown'}

**Implications for Italy Assessment:**
- Infrastructure presence confirms operational relationships
- Geographic data enables network mapping
- Timeline shows expansion patterns
- Technology focus reveals strategic priorities

---

*Analysis based on ASPI China Tech Map dataset*
*Italy infrastructure: {total} projects across {len(by_company)} companies*
"""

    # Save report
    report_path = Path("C:/Projects/OSINT - Foresight/analysis/ASPI_ITALY_INFRASTRUCTURE_REPORT.md")
    report_path.write_text(report, encoding='utf-8')

    # Save JSON
    json_data = {
        'total_projects': total,
        'global_rank': 18,
        'percentage_of_global': round(total/3947*100, 2),
        'companies': dict(sorted(by_company.items(), key=lambda x: x[1], reverse=True)),
        'infrastructure_types': dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True)),
        'technology_topics': dict(sorted(by_topic.items(), key=lambda x: x[1], reverse=True)),
        'cities': dict(sorted(by_city.items(), key=lambda x: x[1], reverse=True)),
        'timeline': dict(sorted(by_year.items())),
        'bis_companies': [{'company': c, 'projects': p} for c, p in bis_in_italy] if bis_in_italy else []
    }

    json_path = Path("C:/Projects/OSINT - Foresight/analysis/ASPI_ITALY_INFRASTRUCTURE.json")
    json_path.write_text(json.dumps(json_data, indent=2), encoding='utf-8')

    print(f"\n{'='*80}")
    print(f"Italy Infrastructure Analysis Complete")
    print(f"{'='*80}")
    print(f"Total projects: {total}")
    print(f"Companies: {len(by_company)}")
    print(f"Infrastructure types: {len(by_type)}")
    print(f"Cities: {len(by_city)}")
    print(f"BIS companies in Italy: {len(bis_in_italy)}")
    print(f"{'='*80}")
    print(f"\nReports saved:")
    print(f"  - {report_path}")
    print(f"  - {json_path}")
    print(f"{'='*80}")

if __name__ == "__main__":
    analyze_italy_infrastructure()
