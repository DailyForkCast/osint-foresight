#!/usr/bin/env python3
"""
Create comprehensive database of all CORDIS China collaboration projects
Outputs to both SQLite and Excel formats
"""

import json
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

class CORDISProjectDatabase:
    def __init__(self, base_path: str = "data/raw/source=cordis"):
        self.base_path = Path(base_path)
        self.projects = {}
        self.china_projects = set()

    def load_cordis_data(self):
        """Load all CORDIS project and organization data"""
        print("Loading CORDIS data...")

        all_projects = {}
        all_orgs = defaultdict(list)

        for program in ["h2020", "horizon"]:
            program_path = self.base_path / program / "projects"

            # Load projects
            project_file = program_path / "project.json"
            if project_file.exists():
                with open(project_file, 'r', encoding='utf-8') as f:
                    projects = json.load(f)
                    for project in projects:
                        if isinstance(project, dict) and 'id' in project:
                            project['programme'] = program.upper()
                            all_projects[project['id']] = project

            # Load organizations
            org_file = program_path / "organization.json"
            if org_file.exists():
                with open(org_file, 'r', encoding='utf-8') as f:
                    organizations = json.load(f)
                    for org in organizations:
                        if isinstance(org, dict) and 'projectID' in org:
                            all_orgs[org['projectID']].append(org)

        print(f"Loaded {len(all_projects)} projects and organizations for {len(all_orgs)} projects")
        return all_projects, all_orgs

    def identify_china_projects(self, all_projects, all_orgs):
        """Identify all projects with China participation"""
        print("\nIdentifying China collaboration projects...")

        china_project_details = {}

        for project_id, orgs in all_orgs.items():
            if project_id not in all_projects:
                continue

            project = all_projects[project_id]

            # Check if China is involved
            countries = set()
            organizations = []
            chinese_orgs = []
            total_orgs = len(orgs)

            for org in orgs:
                country = org.get('country', '').upper()
                if country:
                    countries.add(country)

                org_info = {
                    'name': org.get('name', 'Unknown'),
                    'country': country,
                    'city': org.get('city', ''),
                    'type': org.get('activityType', ''),
                    'ec_contribution': org.get('ecContribution', 0),
                    'net_contribution': org.get('netEcContribution', 0),
                    'total_cost': org.get('totalCost', 0)
                }
                organizations.append(org_info)

                if country == 'CN':
                    chinese_orgs.append(org_info)

            # If China is involved, add to our collection
            if 'CN' in countries and len(countries) > 1:  # China plus at least one other country

                # Parse dates
                start_date = project.get('startDate', '')
                end_date = project.get('endDate', '')
                start_year = int(start_date[:4]) if start_date and len(start_date) >= 4 else None
                end_year = int(end_date[:4]) if end_date and len(end_date) >= 4 else None

                # Determine status
                status = project.get('status', 'UNKNOWN')
                if status == 'SIGNED':
                    if end_date and datetime.strptime(end_date[:10], '%Y-%m-%d') < datetime.now():
                        status = 'COMPLETED'
                    else:
                        status = 'ONGOING'

                # Extract topics
                topics = project.get('topics', [])
                if isinstance(topics, str):
                    topics = [topics]

                # Calculate EU vs non-EU countries
                eu_countries = {'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                               'DE', 'GR', 'EL', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT',
                               'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'}
                eu_partners = len([c for c in countries if c in eu_countries])
                non_eu_partners = len(countries) - eu_partners

                project_details = {
                    'project_id': project_id,
                    'acronym': project.get('acronym', ''),
                    'title': project.get('title', ''),
                    'objective': project.get('objective', '')[:500] if project.get('objective') else '',
                    'programme': project.get('programme', ''),
                    'funding_scheme': project.get('fundingScheme', ''),
                    'status': status,
                    'start_date': start_date,
                    'end_date': end_date,
                    'start_year': start_year,
                    'end_year': end_year,
                    'duration_months': None,
                    'total_cost': project.get('totalCost', 0),
                    'ec_contribution': project.get('ecMaxContribution', 0),
                    'coordinator_country': project.get('coordinatorCountry', ''),
                    'num_countries': len(countries),
                    'num_organizations': total_orgs,
                    'num_chinese_orgs': len(chinese_orgs),
                    'countries_list': ', '.join(sorted(countries)),
                    'eu_partners': eu_partners,
                    'non_eu_partners': non_eu_partners,
                    'chinese_organizations': ', '.join([org['name'] for org in chinese_orgs]),
                    'topics': ', '.join(topics) if topics else '',
                    'keywords': project.get('keywords', ''),
                    'call': project.get('masterCall', ''),
                    'organizations': organizations,
                    'all_org_names': ', '.join([org['name'] for org in organizations[:10]])  # First 10 orgs
                }

                # Calculate duration
                if start_date and end_date:
                    try:
                        start_dt = datetime.strptime(start_date[:10], '%Y-%m-%d')
                        end_dt = datetime.strptime(end_date[:10], '%Y-%m-%d')
                        project_details['duration_months'] = round((end_dt - start_dt).days / 30.44)
                    except:
                        pass

                china_project_details[project_id] = project_details
                self.china_projects.add(project_id)

        print(f"Found {len(china_project_details)} projects with China collaboration")
        return china_project_details

    def create_sqlite_database(self, project_details):
        """Create SQLite database with project information"""
        print("\nCreating SQLite database...")

        db_path = Path("data/processed/cordis_unified/cordis_china_projects.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing database
        if db_path.exists():
            db_path.unlink()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create main projects table
        cursor.execute("""
        CREATE TABLE projects (
            project_id TEXT PRIMARY KEY,
            acronym TEXT,
            title TEXT,
            objective TEXT,
            programme TEXT,
            funding_scheme TEXT,
            status TEXT,
            start_date TEXT,
            end_date TEXT,
            start_year INTEGER,
            end_year INTEGER,
            duration_months INTEGER,
            total_cost REAL,
            ec_contribution REAL,
            coordinator_country TEXT,
            num_countries INTEGER,
            num_organizations INTEGER,
            num_chinese_orgs INTEGER,
            countries_list TEXT,
            eu_partners INTEGER,
            non_eu_partners INTEGER,
            chinese_organizations TEXT,
            topics TEXT,
            keywords TEXT,
            call TEXT,
            all_org_names TEXT
        )
        """)

        # Create organizations table
        cursor.execute("""
        CREATE TABLE organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            org_name TEXT,
            country TEXT,
            city TEXT,
            org_type TEXT,
            ec_contribution REAL,
            net_contribution REAL,
            total_cost REAL,
            is_chinese BOOLEAN,
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        )
        """)

        # Create countries table
        cursor.execute("""
        CREATE TABLE project_countries (
            project_id TEXT,
            country_code TEXT,
            PRIMARY KEY (project_id, country_code),
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        )
        """)

        # Insert project data
        for project_id, details in project_details.items():
            # Insert main project
            cursor.execute("""
            INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                details['project_id'],
                details['acronym'],
                details['title'],
                details['objective'],
                details['programme'],
                details['funding_scheme'],
                details['status'],
                details['start_date'],
                details['end_date'],
                details['start_year'],
                details['end_year'],
                details['duration_months'],
                details['total_cost'],
                details['ec_contribution'],
                details['coordinator_country'],
                details['num_countries'],
                details['num_organizations'],
                details['num_chinese_orgs'],
                details['countries_list'],
                details['eu_partners'],
                details['non_eu_partners'],
                details['chinese_organizations'],
                details['topics'],
                details['keywords'],
                details['call'],
                details['all_org_names']
            ))

            # Insert organizations
            for org in details['organizations']:
                cursor.execute("""
                INSERT INTO organizations (project_id, org_name, country, city, org_type,
                                         ec_contribution, net_contribution, total_cost, is_chinese)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_id,
                    org['name'],
                    org['country'],
                    org['city'],
                    org['type'],
                    org['ec_contribution'],
                    org['net_contribution'],
                    org['total_cost'],
                    1 if org['country'] == 'CN' else 0
                ))

            # Insert countries
            countries = details['countries_list'].split(', ')
            for country in countries:
                if country:
                    cursor.execute("""
                    INSERT OR IGNORE INTO project_countries (project_id, country_code)
                    VALUES (?, ?)
                    """, (project_id, country))

        # Create indexes for better query performance
        cursor.execute("CREATE INDEX idx_status ON projects(status)")
        cursor.execute("CREATE INDEX idx_programme ON projects(programme)")
        cursor.execute("CREATE INDEX idx_start_year ON projects(start_year)")
        cursor.execute("CREATE INDEX idx_coordinator ON projects(coordinator_country)")
        cursor.execute("CREATE INDEX idx_org_country ON organizations(country)")
        cursor.execute("CREATE INDEX idx_org_chinese ON organizations(is_chinese)")

        conn.commit()
        conn.close()

        print(f"SQLite database created: {db_path}")
        return db_path

    def create_excel_export(self, project_details):
        """Export project details to Excel with multiple sheets"""
        print("\nCreating Excel export...")

        excel_path = Path("data/processed/cordis_unified/cordis_china_projects.xlsx")
        excel_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Try xlsxwriter first (better formatting)
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:

            # Main projects sheet
            projects_data = []
            for project_id, details in project_details.items():
                projects_data.append({
                    'Project ID': details['project_id'],
                    'Acronym': details['acronym'],
                    'Title': details['title'],
                    'Programme': details['programme'],
                    'Status': details['status'],
                    'Start Year': details['start_year'],
                    'End Year': details['end_year'],
                    'Duration (months)': details['duration_months'],
                    'Total Cost (€)': details['total_cost'],
                    'EC Contribution (€)': details['ec_contribution'],
                    'Coordinator Country': details['coordinator_country'],
                    '# Countries': details['num_countries'],
                    '# Organizations': details['num_organizations'],
                    '# Chinese Orgs': details['num_chinese_orgs'],
                    'EU Partners': details['eu_partners'],
                    'Non-EU Partners': details['non_eu_partners'],
                    'Countries': details['countries_list'],
                    'Chinese Organizations': details['chinese_organizations'],
                    'Topics': details['topics'],
                    'Funding Scheme': details['funding_scheme']
                })

            df_projects = pd.DataFrame(projects_data)
            df_projects = df_projects.sort_values(['Programme', 'Start Year', 'Acronym'])
            df_projects.to_excel(writer, sheet_name='Projects', index=False)

            # Summary statistics sheet
            summary_data = {
                'Metric': [
                    'Total Projects with China',
                    'H2020 Projects',
                    'Horizon Europe Projects',
                    'Ongoing Projects',
                    'Completed Projects',
                    'Total EC Funding (€B)',
                    'Average Project Value (€M)',
                    'Average # Countries per Project',
                    'Average # Chinese Orgs per Project',
                    'Projects with China as Coordinator'
                ],
                'Value': [
                    len(project_details),
                    sum(1 for d in project_details.values() if d['programme'] == 'H2020'),
                    sum(1 for d in project_details.values() if d['programme'] == 'HORIZON'),
                    sum(1 for d in project_details.values() if d['status'] == 'ONGOING'),
                    sum(1 for d in project_details.values() if d['status'] == 'COMPLETED'),
                    sum(d['ec_contribution'] for d in project_details.values()) / 1e9,
                    sum(d['total_cost'] for d in project_details.values()) / len(project_details) / 1e6,
                    sum(d['num_countries'] for d in project_details.values()) / len(project_details),
                    sum(d['num_chinese_orgs'] for d in project_details.values()) / len(project_details),
                    sum(1 for d in project_details.values() if d['coordinator_country'] == 'CN')
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)

            # Chinese organizations analysis
            chinese_org_counts = defaultdict(int)
            for details in project_details.values():
                for org in details['organizations']:
                    if org['country'] == 'CN':
                        chinese_org_counts[org['name']] += 1

            df_chinese_orgs = pd.DataFrame([
                {'Organization': org, 'Project Count': count}
                for org, count in sorted(chinese_org_counts.items(), key=lambda x: x[1], reverse=True)
            ])
            df_chinese_orgs.to_excel(writer, sheet_name='Chinese Organizations', index=False)

            # Yearly trends
            yearly_data = defaultdict(lambda: {'count': 0, 'funding': 0})
            for details in project_details.values():
                if details['start_year']:
                    yearly_data[details['start_year']]['count'] += 1
                    yearly_data[details['start_year']]['funding'] += details['ec_contribution']

            df_yearly = pd.DataFrame([
                {
                    'Year': year,
                    'Projects Started': data['count'],
                    'EC Funding (€M)': data['funding'] / 1e6
                }
                for year, data in sorted(yearly_data.items())
            ])
            df_yearly.to_excel(writer, sheet_name='Yearly Trends', index=False)

            # Country collaboration matrix
            country_pairs = defaultdict(int)
            for details in project_details.values():
                countries = details['countries_list'].split(', ')
                for i, c1 in enumerate(countries):
                    for c2 in countries[i+1:]:
                        if c1 != 'CN' and c2 != 'CN':
                            pair = tuple(sorted([c1, c2]))
                            country_pairs[pair] += 1

            df_pairs = pd.DataFrame([
                {'Country 1': pair[0], 'Country 2': pair[1], 'Joint Projects with China': count}
                for pair, count in sorted(country_pairs.items(), key=lambda x: x[1], reverse=True)[:50]
            ])
            df_pairs.to_excel(writer, sheet_name='Country Pairs', index=False)

                # Format the Excel file if xlsxwriter
                workbook = writer.book
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#D7E4BD',
                    'border': 1
                })

                money_format = workbook.add_format({'num_format': '€#,##0'})

                # Apply formatting to Projects sheet
                worksheet = writer.sheets['Projects']
                worksheet.set_column('A:A', 12)  # Project ID
                worksheet.set_column('B:B', 15)  # Acronym
                worksheet.set_column('C:C', 50)  # Title
                worksheet.set_column('I:J', 15, money_format)  # Cost columns

        except ImportError:
            # Fallback to openpyxl (basic formatting)
            print("xlsxwriter not available, using openpyxl...")
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:

                # Main projects sheet
                projects_data = []
                for project_id, details in project_details.items():
                    projects_data.append({
                        'Project ID': details['project_id'],
                        'Acronym': details['acronym'],
                        'Title': details['title'],
                        'Programme': details['programme'],
                        'Status': details['status'],
                        'Start Year': details['start_year'],
                        'End Year': details['end_year'],
                        'Duration (months)': details['duration_months'],
                        'Total Cost (€)': details['total_cost'],
                        'EC Contribution (€)': details['ec_contribution'],
                        'Coordinator Country': details['coordinator_country'],
                        '# Countries': details['num_countries'],
                        '# Organizations': details['num_organizations'],
                        '# Chinese Orgs': details['num_chinese_orgs'],
                        'EU Partners': details['eu_partners'],
                        'Non-EU Partners': details['non_eu_partners'],
                        'Countries': details['countries_list'],
                        'Chinese Organizations': details['chinese_organizations'],
                        'Topics': details['topics'],
                        'Funding Scheme': details['funding_scheme']
                    })

                df_projects = pd.DataFrame(projects_data)
                df_projects = df_projects.sort_values(['Programme', 'Start Year', 'Acronym'])
                df_projects.to_excel(writer, sheet_name='Projects', index=False)

                # Summary statistics sheet
                summary_data = {
                    'Metric': [
                        'Total Projects with China',
                        'H2020 Projects',
                        'Horizon Europe Projects',
                        'Ongoing Projects',
                        'Completed Projects',
                        'Total EC Funding (€B)',
                        'Average Project Value (€M)',
                        'Average # Countries per Project',
                        'Average # Chinese Orgs per Project',
                        'Projects with China as Coordinator'
                    ],
                    'Value': [
                        len(project_details),
                        sum(1 for d in project_details.values() if d['programme'] == 'H2020'),
                        sum(1 for d in project_details.values() if d['programme'] == 'HORIZON'),
                        sum(1 for d in project_details.values() if d['status'] == 'ONGOING'),
                        sum(1 for d in project_details.values() if d['status'] == 'COMPLETED'),
                        sum(d['ec_contribution'] for d in project_details.values()) / 1e9,
                        sum(d['total_cost'] for d in project_details.values()) / len(project_details) / 1e6,
                        sum(d['num_countries'] for d in project_details.values()) / len(project_details),
                        sum(d['num_chinese_orgs'] for d in project_details.values()) / len(project_details),
                        sum(1 for d in project_details.values() if d['coordinator_country'] == 'CN')
                    ]
                }
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Summary', index=False)

                # Chinese organizations analysis
                chinese_org_counts = defaultdict(int)
                for details in project_details.values():
                    for org in details['organizations']:
                        if org['country'] == 'CN':
                            chinese_org_counts[org['name']] += 1

                df_chinese_orgs = pd.DataFrame([
                    {'Organization': org, 'Project Count': count}
                    for org, count in sorted(chinese_org_counts.items(), key=lambda x: x[1], reverse=True)
                ])
                df_chinese_orgs.to_excel(writer, sheet_name='Chinese Organizations', index=False)

                # Yearly trends
                yearly_data = defaultdict(lambda: {'count': 0, 'funding': 0})
                for details in project_details.values():
                    if details['start_year']:
                        yearly_data[details['start_year']]['count'] += 1
                        yearly_data[details['start_year']]['funding'] += details['ec_contribution']

                df_yearly = pd.DataFrame([
                    {
                        'Year': year,
                        'Projects Started': data['count'],
                        'EC Funding (€M)': data['funding'] / 1e6
                    }
                    for year, data in sorted(yearly_data.items())
                ])
                df_yearly.to_excel(writer, sheet_name='Yearly Trends', index=False)

                # Country collaboration matrix
                country_pairs = defaultdict(int)
                for details in project_details.values():
                    countries = details['countries_list'].split(', ')
                    for i, c1 in enumerate(countries):
                        for c2 in countries[i+1:]:
                            if c1 != 'CN' and c2 != 'CN':
                                pair = tuple(sorted([c1, c2]))
                                country_pairs[pair] += 1

                df_pairs = pd.DataFrame([
                    {'Country 1': pair[0], 'Country 2': pair[1], 'Joint Projects with China': count}
                    for pair, count in sorted(country_pairs.items(), key=lambda x: x[1], reverse=True)[:50]
                ])
                df_pairs.to_excel(writer, sheet_name='Country Pairs', index=False)

        print(f"Excel file created: {excel_path}")
        return excel_path

    def generate_analysis_report(self, project_details):
        """Generate detailed analysis report"""
        print("\nGenerating analysis report...")

        report_path = Path("data/processed/cordis_unified/CORDIS_CHINA_PROJECTS_DETAILED_ANALYSIS.md")

        # Calculate statistics
        total_projects = len(project_details)
        total_funding = sum(d['ec_contribution'] for d in project_details.values())
        h2020_count = sum(1 for d in project_details.values() if d['programme'] == 'H2020')
        horizon_count = sum(1 for d in project_details.values() if d['programme'] == 'HORIZON')

        # Get top Chinese organizations
        chinese_org_counts = defaultdict(int)
        for details in project_details.values():
            for org in details['organizations']:
                if org['country'] == 'CN':
                    chinese_org_counts[org['name']] += 1

        top_chinese_orgs = sorted(chinese_org_counts.items(), key=lambda x: x[1], reverse=True)[:20]

        # Technology area analysis
        topic_counts = defaultdict(int)
        for details in project_details.values():
            if details['topics']:
                for topic in details['topics'].split(', '):
                    if topic:
                        topic_counts[topic] += 1

        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:20]

        report = f"""# CORDIS China Collaboration Projects - Detailed Analysis
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

**Total Unique Projects with China Participation: {total_projects}**

### Programme Distribution
- H2020 (2014-2020): {h2020_count} projects
- Horizon Europe (2021-2027): {horizon_count} projects

### Financial Overview
- Total EC Contribution: €{total_funding:,.0f}
- Average EC Contribution per Project: €{total_funding/total_projects:,.0f}

### Project Status
- Ongoing: {sum(1 for d in project_details.values() if d['status'] == 'ONGOING')}
- Completed: {sum(1 for d in project_details.values() if d['status'] == 'COMPLETED')}
- Other: {sum(1 for d in project_details.values() if d['status'] not in ['ONGOING', 'COMPLETED'])}

## Top Chinese Organizations (by project participation)

| Rank | Organization | Projects |
|------|-------------|----------|
"""
        for i, (org, count) in enumerate(top_chinese_orgs, 1):
            report += f"| {i} | {org} | {count} |\n"

        report += f"""

## Technology Focus Areas (Top 20)

| Topic | Project Count |
|-------|--------------|
"""
        for topic, count in top_topics:
            report += f"| {topic} | {count} |\n"

        report += f"""

## Temporal Analysis

### Projects by Start Year
"""
        yearly_data = defaultdict(lambda: {'count': 0, 'funding': 0})
        for details in project_details.values():
            if details['start_year']:
                yearly_data[details['start_year']]['count'] += 1
                yearly_data[details['start_year']]['funding'] += details['ec_contribution']

        report += "| Year | Projects | EC Funding (€M) |\n|------|----------|----------------|\n"
        for year in sorted(yearly_data.keys()):
            data = yearly_data[year]
            report += f"| {year} | {data['count']} | {data['funding']/1e6:.1f} |\n"

        report += f"""

## Collaboration Patterns

### Average Metrics
- Countries per project: {sum(d['num_countries'] for d in project_details.values())/total_projects:.1f}
- Organizations per project: {sum(d['num_organizations'] for d in project_details.values())/total_projects:.1f}
- Chinese organizations per project: {sum(d['num_chinese_orgs'] for d in project_details.values())/total_projects:.1f}

### Geographic Distribution
- Projects with China as coordinator: {sum(1 for d in project_details.values() if d['coordinator_country'] == 'CN')}
- Average EU partners per project: {sum(d['eu_partners'] for d in project_details.values())/total_projects:.1f}
- Average non-EU partners per project: {sum(d['non_eu_partners'] for d in project_details.values())/total_projects:.1f}

## Data Outputs

### SQLite Database
- Location: `data/processed/cordis_unified/cordis_china_projects.db`
- Tables: projects, organizations, project_countries
- Total records: {total_projects} projects with full metadata

### Excel Export
- Location: `data/processed/cordis_unified/cordis_china_projects.xlsx`
- Sheets: Projects, Summary, Chinese Organizations, Yearly Trends, Country Pairs

### Query Examples

```sql
-- Find all projects with Tsinghua University
SELECT p.* FROM projects p
JOIN organizations o ON p.project_id = o.project_id
WHERE o.org_name LIKE '%TSINGHUA%';

-- Get ongoing projects in AI/ML field
SELECT * FROM projects
WHERE status = 'ONGOING'
AND (keywords LIKE '%artificial intelligence%'
     OR keywords LIKE '%machine learning%'
     OR topics LIKE '%AI%');

-- Find projects with multiple Chinese organizations
SELECT project_id, acronym, title, num_chinese_orgs, chinese_organizations
FROM projects
WHERE num_chinese_orgs > 2
ORDER BY num_chinese_orgs DESC;
```

## Notes

1. **Data Completeness**: Based on CORDIS public database exports
2. **China Definition**: Projects must have at least one Chinese organization and one non-Chinese partner
3. **Status Determination**: Based on end dates and current status fields
4. **Financial Data**: EC contribution amounts, not total project costs

---
*This analysis provides a comprehensive view of EU-China research collaboration through Framework Programmes*
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Report saved: {report_path}")
        return report_path

    def run(self):
        """Run the complete analysis"""
        print("=" * 60)
        print("CORDIS China Projects Database Creator")
        print("=" * 60)

        # Load all data
        all_projects, all_orgs = self.load_cordis_data()

        # Identify China projects
        china_project_details = self.identify_china_projects(all_projects, all_orgs)

        # Create outputs
        db_path = self.create_sqlite_database(china_project_details)
        excel_path = self.create_excel_export(china_project_details)
        report_path = self.generate_analysis_report(china_project_details)

        print("\n" + "=" * 60)
        print("DATABASE CREATION COMPLETE")
        print("=" * 60)
        print(f"\nOutputs created:")
        print(f"  SQLite Database: {db_path}")
        print(f"  Excel Export: {excel_path}")
        print(f"  Analysis Report: {report_path}")
        print(f"\nTotal China collaboration projects: {len(china_project_details)}")

if __name__ == "__main__":
    creator = CORDISProjectDatabase()
    creator.run()
