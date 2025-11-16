#!/usr/bin/env python3
"""
CORDIS Complete Reprocessing Script

Problem: The existing cordis_full_projects table (10,000 Horizon Europe projects) has:
- Empty coordinator_country fields
- Empty participant_countries fields
- Empty participants fields
- Only 383 projects (3.8%) have country linkages in cordis_project_countries

Root Cause: Database ingestion only processed project.json but NEVER processed
organization.json which contains all participant/country information.

Solution: Parse organization.json to extract:
1. All organizations with countries for each project
2. Coordinator identification (role='coordinator')
3. Participant countries list
4. Chinese entity detection on organization names
5. Rebuild cordis_project_countries table with complete data

Data Source: /f/DECOMPRESSED_DATA/horizons_data/Horizons/cordis-HORIZONprojects-json (1)/
- project.json: Project metadata (already loaded)
- organization.json: Participant/country data (NEEDS PROCESSING)

Expected Output:
- cordis_full_projects: Updated with coordinator_country, participant_countries
- cordis_project_countries: Rebuilt with all 10,000 projects + countries
- cordis_organizations: Populated with all participating organizations
- cordis_project_participants: Populated with project-organization links
- Chinese entity detection run on all organization names

Runtime: 30-60 minutes for full reprocessing
"""

import json
import sqlite3
from datetime import datetime
from collections import defaultdict
import re
from pathlib import Path

# Configuration
DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
HORIZON_DATA_DIR = "F:/DECOMPRESSED_DATA/horizons_data/Horizons/cordis-HORIZONprojects-json (1)"
H2020_DATA_DIR = "F:/DECOMPRESSED_DATA/horizons_data/Horizons/cordis-h2020projects-json"

# Chinese entity patterns (simplified - expand as needed)
CHINESE_PATTERNS = [
    # Chinese universities
    r'TSINGHUA', r'PEKING UNIVERSITY', r'BEIJING', r'SHANGHAI', r'FUDAN',
    r'ZHEJIANG UNIVERSITY', r'NANJING', r'XI.?AN', r'WUHAN', r'HARBIN',
    r'JILIN UNIVERSITY', r'SUN YAT', r'TONGJI', r'NANKAI', r'TIANJIN',
    r'SICHUAN', r'CHONGQING', r'DALIAN', r'XIAMEN', r'HUAZHONG',

    # Chinese Academy of Sciences
    r'CHINESE ACADEMY OF SCIENCES', r'\bCAS\b', r'INSTITUTE.*CHINA',

    # Chinese companies
    r'HUAWEI', r'ZTE', r'LENOVO', r'TENCENT', r'ALIBABA', r'BAIDU',
    r'CHINA TELECOM', r'CHINA MOBILE', r'CHINA UNICOM',
    r'SINOPEC', r'PETROCHINA', r'CNOOC', r'STATE GRID',

    # Generic Chinese indicators
    r'CHINA\s+\w+\s+(UNIVERSITY|INSTITUTE|ACADEMY|CORPORATION|COMPANY)',
    r'(UNIVERSITY|INSTITUTE).*CHINA',
    r'CHINA NATIONAL', r'PEOPLE.?S REPUBLIC'
]

# Country code mappings
CHINESE_COUNTRY_CODES = ['CN', 'HK', 'MO']  # China, Hong Kong, Macau

def log(msg):
    """Thread-safe logging with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def is_chinese_entity(org_name, country_code):
    """
    Detect if organization is Chinese based on name patterns and country code.

    Args:
        org_name (str): Organization name
        country_code (str): ISO country code

    Returns:
        bool: True if Chinese entity
    """
    if not org_name:
        return False

    # Explicit country code check
    if country_code in CHINESE_COUNTRY_CODES:
        return True

    # Convert to string and pattern match on name
    org_upper = str(org_name).upper()
    for pattern in CHINESE_PATTERNS:
        if re.search(pattern, org_upper):
            return True

    return False

def load_json_file(file_path):
    """Load JSON file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log(f"ERROR loading {file_path}: {e}")
        return None

def process_horizon_data(conn, data_dir, framework='HORIZON'):
    """
    Process Horizon Europe or H2020 data from JSON files.

    Args:
        conn: SQLite connection
        data_dir: Path to CORDIS JSON directory
        framework: 'HORIZON' or 'H2020'
    """
    cursor = conn.cursor()

    log(f"="*80)
    log(f"PROCESSING {framework} DATA")
    log(f"Source: {data_dir}")
    log(f"="*80)

    # Load source files
    log(f"\n[1] Loading JSON source files...")
    project_file = f"{data_dir}/project.json"
    org_file = f"{data_dir}/organization.json"

    if not Path(project_file).exists():
        log(f"ERROR: {project_file} not found!")
        return

    if not Path(org_file).exists():
        log(f"ERROR: {org_file} not found!")
        return

    projects = load_json_file(project_file)
    organizations = load_json_file(org_file)

    if not projects or not organizations:
        log("ERROR: Failed to load source files")
        return

    log(f"  Loaded {len(projects):,} projects")
    log(f"  Loaded {len(organizations):,} organization records")

    # Build project lookup for validation
    project_ids = {p['id'] for p in projects}
    log(f"  Unique projects in project.json: {len(project_ids):,}")

    # Process organizations by project
    log(f"\n[2] Processing organizations and extracting country data...")

    org_by_project = defaultdict(list)
    for org in organizations:
        proj_id = org.get('projectID')
        if proj_id:
            org_by_project[proj_id].append(org)

    log(f"  Organizations grouped by project: {len(org_by_project):,} projects have participants")

    # Statistics
    stats = {
        'projects_processed': 0,
        'projects_with_participants': 0,
        'total_organizations': 0,
        'chinese_organizations': 0,
        'projects_with_chinese_involvement': 0,
        'countries_found': set()
    }

    # Process each project
    log(f"\n[3] Updating project country and participant data...")

    for project in projects:
        project_id = project['id']
        stats['projects_processed'] += 1

        # Get organizations for this project
        project_orgs = org_by_project.get(project_id, [])

        if not project_orgs:
            continue

        stats['projects_with_participants'] += 1
        stats['total_organizations'] += len(project_orgs)

        # Extract country and participant information
        coordinator_country = None
        participant_countries = []
        has_chinese_involvement = False

        for org in project_orgs:
            country = org.get('country', '').strip()
            if country:
                stats['countries_found'].add(country)
                participant_countries.append(country)

            # Check if coordinator
            if org.get('role') == 'coordinator':
                coordinator_country = country

            # Check for Chinese involvement
            org_name = org.get('name', '')
            if is_chinese_entity(org_name, country):
                has_chinese_involvement = True
                stats['chinese_organizations'] += 1

        if has_chinese_involvement:
            stats['projects_with_chinese_involvement'] += 1

        # Update cordis_full_projects table
        unique_countries = list(set(participant_countries))
        participant_countries_json = json.dumps(unique_countries)

        cursor.execute("""
            UPDATE cordis_full_projects
            SET coordinator_country = ?,
                participant_countries = ?,
                china_involvement = ?
            WHERE project_id = ?
        """, (
            coordinator_country or '',
            participant_countries_json,
            1 if has_chinese_involvement else 0,
            str(project_id)
        ))

        # Insert/update cordis_project_countries entries
        for country in unique_countries:
            cursor.execute("""
                INSERT OR REPLACE INTO cordis_project_countries
                (project_id, country_code, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (str(project_id), country))

        # Insert organizations into cordis_organizations
        for org in project_orgs:
            org_name = org.get('name', '')
            country = org.get('country', '').strip()
            is_chinese = is_chinese_entity(org_name, country)

            cursor.execute("""
                INSERT OR IGNORE INTO cordis_organizations
                (org_id, name, country, city, organization_type, is_chinese, created_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                org.get('organisationID'),
                org_name,
                country,
                org.get('city', ''),
                org.get('activityType', ''),
                1 if is_chinese else 0
            ))

            # Insert project-organization link
            cursor.execute("""
                INSERT OR IGNORE INTO cordis_project_participants
                (project_id, org_id, role, eu_contribution, is_coordinator, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                str(project_id),
                org.get('organisationID'),
                org.get('role', ''),
                org.get('ecContribution', 0),
                1 if org.get('role') == 'coordinator' else 0
            ))

        # Progress logging
        if stats['projects_processed'] % 1000 == 0:
            log(f"  Processed {stats['projects_processed']:,} projects...")
            conn.commit()

    conn.commit()

    # Final statistics
    log(f"\n[4] {framework} Processing Complete:")
    log(f"  Projects processed: {stats['projects_processed']:,}")
    log(f"  Projects with participants: {stats['projects_with_participants']:,}")
    log(f"  Total organizations: {stats['total_organizations']:,}")
    log(f"  Chinese organizations detected: {stats['chinese_organizations']:,}")
    log(f"  Projects with Chinese involvement: {stats['projects_with_chinese_involvement']:,}")
    log(f"  Unique countries: {len(stats['countries_found'])}")

    return stats

def validate_reprocessing(conn):
    """Validate the reprocessed data."""
    cursor = conn.cursor()

    log(f"\n" + "="*80)
    log("VALIDATION: Reprocessed Data Quality Check")
    log("="*80)

    # Check cordis_full_projects updates
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN coordinator_country != '' THEN 1 ELSE 0 END) as with_coordinator,
            SUM(CASE WHEN participant_countries != '[]' THEN 1 ELSE 0 END) as with_participants,
            SUM(CASE WHEN china_involvement = 1 THEN 1 ELSE 0 END) as with_china
        FROM cordis_full_projects
    """)
    total, with_coord, with_parts, with_china = cursor.fetchone()

    log(f"\ncordis_full_projects:")
    log(f"  Total projects: {total:,}")
    log(f"  With coordinator_country: {with_coord:,} ({with_coord/total*100:.1f}%)")
    log(f"  With participant_countries: {with_parts:,} ({with_parts/total*100:.1f}%)")
    log(f"  With China involvement: {with_china:,} ({with_china/total*100:.1f}%)")

    # Check cordis_project_countries
    cursor.execute("SELECT COUNT(*) FROM cordis_project_countries")
    country_links = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT project_id) FROM cordis_project_countries")
    projects_with_countries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT country_code) FROM cordis_project_countries")
    unique_countries = cursor.fetchone()[0]

    log(f"\ncordis_project_countries:")
    log(f"  Total country linkages: {country_links:,}")
    log(f"  Projects with countries: {projects_with_countries:,} ({projects_with_countries/total*100:.1f}%)")
    log(f"  Unique countries: {unique_countries}")

    # Check cordis_organizations
    cursor.execute("SELECT COUNT(*) FROM cordis_organizations")
    total_orgs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cordis_organizations WHERE is_chinese = 1")
    chinese_orgs = cursor.fetchone()[0]

    log(f"\ncordis_organizations:")
    log(f"  Total organizations: {total_orgs:,}")
    if total_orgs > 0:
        log(f"  Chinese organizations: {chinese_orgs:,} ({chinese_orgs/total_orgs*100:.1f}%)")
    else:
        log(f"  Chinese organizations: {chinese_orgs:,} (N/A - no organizations)")

    # Top countries
    cursor.execute("""
        SELECT country_code, COUNT(*) as count
        FROM cordis_project_countries
        GROUP BY country_code
        ORDER BY count DESC
        LIMIT 15
    """)
    log(f"\nTop 15 countries by project participation:")
    for country, count in cursor.fetchall():
        log(f"  {country}: {count:,} projects")

    # Netherlands-specific validation
    cursor.execute("""
        SELECT COUNT(DISTINCT pc.project_id)
        FROM cordis_project_countries pc
        WHERE pc.country_code = 'NL'
    """)
    nl_projects = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT pc.project_id)
        FROM cordis_project_countries pc
        JOIN cordis_full_projects fp ON pc.project_id = fp.project_id
        WHERE pc.country_code = 'NL' AND fp.china_involvement = 1
    """)
    nl_china_projects = cursor.fetchone()[0]

    log(f"\nNetherlands Validation:")
    log(f"  Total NL projects: {nl_projects:,}")
    log(f"  NL projects with China: {nl_china_projects} ({nl_china_projects/nl_projects*100:.1f}%)")

def main():
    """Main execution function."""
    start_time = datetime.now()

    log("="*80)
    log("CORDIS COMPLETE REPROCESSING - START")
    log("="*80)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing data in tables being rebuilt
    log("\n[SETUP] Clearing existing incomplete data...")
    cursor.execute("DELETE FROM cordis_project_countries")
    cursor.execute("DELETE FROM cordis_organizations")
    cursor.execute("DELETE FROM cordis_project_participants")
    conn.commit()
    log("  Cleared cordis_project_countries, cordis_organizations, cordis_project_participants")

    # Process Horizon Europe data
    if Path(HORIZON_DATA_DIR).exists():
        horizon_stats = process_horizon_data(conn, HORIZON_DATA_DIR, 'HORIZON')
    else:
        log(f"WARNING: Horizon data directory not found: {HORIZON_DATA_DIR}")
        horizon_stats = None

    # Process H2020 data (if needed)
    # if H2020_DATA_DIR.exists():
    #     h2020_stats = process_horizon_data(conn, H2020_DATA_DIR, 'H2020')

    # Validation
    validate_reprocessing(conn)

    # Cleanup
    conn.close()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    log("\n" + "="*80)
    log("CORDIS COMPLETE REPROCESSING - FINISHED")
    log(f"Duration: {duration/60:.1f} minutes")
    log("="*80)

if __name__ == "__main__":
    main()
