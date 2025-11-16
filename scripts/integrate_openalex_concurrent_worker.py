"""
OpenAlex V4 Concurrent Worker - WITH NULL DATA PROTOCOL
Processes a partition of date directories with NULL data capture

NULL Data Protocol (USPTO Methodology Applied):
- Captures works that FAILED keyword matching but have other relevant signals
- Similar to capturing USPTO patents with NULL assignee, NULL location
- Identifies gaps in our keyword coverage
"""

import sqlite3
import gzip
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re
import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import from main script
from integrate_openalex_full_v2 import (
    TECHNOLOGY_KEYWORDS,
    RELEVANT_TOPICS,
    EXCLUDED_SOURCE_PATTERNS,
    matches_technology_improved,
    has_relevant_topic,
    is_excluded_source,
    load_expanded_keywords,
    load_expanded_topics
)

# Paths
MASTER_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OPENALEX_DATA = Path("F:/OSINT_Backups/openalex/data/works")

def create_null_data_tables(conn):
    """Create tables for NULL data capture (USPTO methodology)"""

    # Works that FAILED keyword matching but have other relevant signals
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_null_keyword_fails (
        work_id TEXT PRIMARY KEY,
        doi TEXT,
        title TEXT,
        publication_year INTEGER,
        cited_by_count INTEGER,
        abstract TEXT,
        technology_domain TEXT,
        null_reason TEXT,
        matched_topic TEXT,
        topic_score REAL,
        has_chinese_institution BOOLEAN,
        has_strategic_funder BOOLEAN,
        high_citations BOOLEAN,
        created_date TEXT
    )
    """)

    # Works that passed keywords BUT failed topic validation
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_null_topic_fails (
        work_id TEXT PRIMARY KEY,
        doi TEXT,
        title TEXT,
        publication_year INTEGER,
        cited_by_count INTEGER,
        abstract TEXT,
        technology_domain TEXT,
        matched_keyword TEXT,
        actual_topics TEXT,
        created_date TEXT
    )
    """)

    # Works from strategic institutions but failed both validations
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_null_strategic_institution (
        work_id TEXT PRIMARY KEY,
        doi TEXT,
        title TEXT,
        publication_year INTEGER,
        institution_id TEXT,
        institution_name TEXT,
        institution_country TEXT,
        abstract TEXT,
        all_topics TEXT,
        created_date TEXT
    )
    """)

    conn.commit()
    print("[OK] NULL data capture tables created/verified")

def validate_work_with_null_capture(work, tech_name, tech_keywords, strictness='moderate'):
    """
    Enhanced validation with NULL data capture

    Returns: (is_valid, validation_details, null_data_captures)

    null_data_captures contains works that:
    1. Failed keyword matching BUT have relevant topics
    2. Failed topic validation BUT matched keywords
    3. Have Chinese/strategic institutions BUT failed both
    """

    validation_details = {
        'stage1_keyword': False,
        'stage2_topic': False,
        'stage3_source': True,
        'stage4_quality': True,
        'matched_keyword': None,
        'matched_topic': None,
        'exclusion_reason': None
    }

    null_captures = {
        'keyword_fail_topic_pass': None,
        'keyword_pass_topic_fail': None,
        'strategic_institution_both_fail': None
    }

    # Extract work data
    title = work.get('title', '')
    abstract_inverted = work.get('abstract_inverted_index', {})
    abstract = ' '.join(abstract_inverted.keys()) if abstract_inverted else ''
    combined_text = f"{title} {abstract}"
    topics = work.get('topics', [])

    # Stage 1: Keyword matching
    has_keyword, matched_keyword = matches_technology_improved(combined_text, tech_keywords)
    validation_details['stage1_keyword'] = has_keyword
    validation_details['matched_keyword'] = matched_keyword

    # Stage 2: Topic validation
    has_topic, matched_topic = has_relevant_topic(topics, tech_name, strictness=strictness)
    validation_details['stage2_topic'] = has_topic
    validation_details['matched_topic'] = matched_topic

    # NULL DATA PROTOCOL: Capture works that failed keyword BUT have relevant topics
    if not has_keyword and has_topic:
        # This is a gap in our keyword coverage!
        work_id = work.get('id', '').split('/')[-1]

        # Check additional signals
        has_chinese_inst = check_chinese_institution(work)
        has_strategic_funder = check_strategic_funder(work)
        high_citations = work.get('cited_by_count', 0) > 50

        null_captures['keyword_fail_topic_pass'] = {
            'work_id': work_id,
            'doi': work.get('doi'),
            'title': title[:500],
            'publication_year': work.get('publication_year'),
            'cited_by_count': work.get('cited_by_count', 0),
            'abstract': abstract[:1000] if abstract else None,
            'technology_domain': tech_name,
            'null_reason': 'KEYWORD_FAIL_TOPIC_PASS',
            'matched_topic': matched_topic,
            'topic_score': topics[0].get('score') if topics else 0,
            'has_chinese_institution': has_chinese_inst,
            'has_strategic_funder': has_strategic_funder,
            'high_citations': high_citations
        }

    # NULL DATA PROTOCOL: Capture works that passed keyword BUT failed topic
    if has_keyword and not has_topic:
        work_id = work.get('id', '').split('/')[-1]

        # Extract actual topics for analysis
        actual_topics = ', '.join([t.get('display_name', '') for t in topics[:5]])

        null_captures['keyword_pass_topic_fail'] = {
            'work_id': work_id,
            'doi': work.get('doi'),
            'title': title[:500],
            'publication_year': work.get('publication_year'),
            'cited_by_count': work.get('cited_by_count', 0),
            'abstract': abstract[:1000] if abstract else None,
            'technology_domain': tech_name,
            'matched_keyword': matched_keyword,
            'actual_topics': actual_topics
        }

    # NULL DATA PROTOCOL: Capture works from strategic institutions that failed both
    if not has_keyword and not has_topic:
        has_strategic_inst = check_strategic_institution(work)

        if has_strategic_inst:
            work_id = work.get('id', '').split('/')[-1]
            inst_info = get_institution_info(work)

            all_topics = ', '.join([t.get('display_name', '') for t in topics[:10]])

            null_captures['strategic_institution_both_fail'] = {
                'work_id': work_id,
                'doi': work.get('doi'),
                'title': title[:500],
                'publication_year': work.get('publication_year'),
                'institution_id': inst_info.get('id'),
                'institution_name': inst_info.get('name'),
                'institution_country': inst_info.get('country'),
                'abstract': abstract[:1000] if abstract else None,
                'all_topics': all_topics
            }

    # Continue with standard validation
    if not has_keyword:
        return False, validation_details, null_captures

    if not has_topic:
        return False, validation_details, null_captures

    # Stage 3: Source exclusion
    primary_location = work.get('primary_location', {})
    source = primary_location.get('source', {})
    source_name = source.get('display_name', '')

    if tech_name != 'Biotechnology':
        is_excluded, exclusion_pattern = is_excluded_source(source_name)
        validation_details['stage3_source'] = not is_excluded
        validation_details['exclusion_reason'] = exclusion_pattern if is_excluded else None

        if is_excluded:
            return False, validation_details, null_captures

    # Stage 4: Quality checks
    is_retracted = work.get('is_retracted', False)
    is_paratext = work.get('is_paratext', False)
    has_abstract = bool(abstract_inverted)

    validation_details['stage4_quality'] = not is_retracted and not is_paratext and has_abstract

    if is_retracted or is_paratext or not has_abstract:
        return False, validation_details, null_captures

    # All stages passed
    return True, validation_details, null_captures

def check_chinese_institution(work):
    """Check if work has Chinese institution affiliation"""
    authorships = work.get('authorships', [])
    for authorship in authorships:
        institutions = authorship.get('institutions', [])
        for inst in institutions:
            country = inst.get('country_code', '')
            if country == 'CN':
                return True
    return False

def check_strategic_funder(work):
    """Check if work has strategic funder (US DOD, DOE, NSF, China NSFC, etc.)"""
    strategic_funder_patterns = [
        'department of defense', 'dod', 'darpa', 'onr', 'air force',
        'department of energy', 'doe',
        'national science foundation', 'nsf',
        'national natural science foundation', 'nsfc',
        'european research council', 'erc',
        'horizon 2020', 'horizon europe'
    ]

    grants = work.get('grants', [])
    for grant in grants:
        funder_name = grant.get('funder_display_name', '').lower()
        for pattern in strategic_funder_patterns:
            if pattern in funder_name:
                return True
    return False

def check_strategic_institution(work):
    """Check if work is from a strategic research institution"""
    strategic_patterns = [
        'tsinghua', 'peking university', 'beijing university',
        'chinese academy', 'cas ',
        'mit ', 'stanford', 'berkeley', 'caltech',
        'max planck', 'fraunhofer',
        'oxford', 'cambridge',
        'eth zurich', 'epfl'
    ]

    authorships = work.get('authorships', [])
    for authorship in authorships:
        institutions = authorship.get('institutions', [])
        for inst in institutions:
            inst_name = inst.get('display_name', '').lower()
            for pattern in strategic_patterns:
                if pattern in inst_name:
                    return True
    return False

def get_institution_info(work):
    """Get primary institution info from work"""
    authorships = work.get('authorships', [])
    if authorships:
        institutions = authorships[0].get('institutions', [])
        if institutions:
            inst = institutions[0]
            return {
                'id': inst.get('id', '').split('/')[-1],
                'name': inst.get('display_name'),
                'country': inst.get('country_code')
            }
    return {}

def process_partition_data(partition_id, start_date, end_date, max_works_per_tech, strictness):
    """Process a partition of OpenAlex data with NULL capture"""

    print(f"\n{'=' * 80}")
    print(f"PARTITION {partition_id} - NULL DATA PROTOCOL ACTIVE")
    print(f"{'=' * 80}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Max works per technology: {max_works_per_tech:,}")
    print(f"Strictness: {strictness}")
    print()

    # Get date directories in range
    all_dirs = sorted(OPENALEX_DATA.glob('updated_date=*'))
    partition_dirs = [d for d in all_dirs if start_date <= d.name <= end_date]

    print(f"Processing {len(partition_dirs)} directories in this partition")

    # Get all files from partition directories
    work_files = []
    for date_dir in partition_dirs:
        work_files.extend(date_dir.glob('*.gz'))

    print(f"Found {len(work_files):,} files to process\n")

    # Processing counters
    works_by_tech = defaultdict(list)
    validation_stats = defaultdict(lambda: {
        'total_scanned': 0,
        'stage1_passed': 0,
        'stage2_passed': 0,
        'stage3_passed': 0,
        'stage4_passed': 0,
        'final_accepted': 0
    })

    # NULL data captures
    null_keyword_fails = []
    null_topic_fails = []
    null_strategic_inst = []

    files_processed = 0
    total_works_scanned = 0

    # Process files
    for file_path in work_files:
        files_processed += 1

        # Check if all technologies maxed
        all_maxed = all(len(works_by_tech[tech]) >= max_works_per_tech for tech in TECHNOLOGY_KEYWORDS.keys())
        if all_maxed:
            print(f"\n[OK] Partition {partition_id}: Reached max for all technologies")
            break

        if files_processed % 10 == 0:
            print(f"[Partition {partition_id}] Processing file {files_processed}/{len(work_files)}")

        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line_num, line in enumerate(f):
                    total_works_scanned += 1

                    if total_works_scanned % 50000 == 0:
                        print(f"[Partition {partition_id}] Scanned {total_works_scanned:,} works total")

                    try:
                        work = json.loads(line)

                        # Check each technology
                        for tech_name, keywords in TECHNOLOGY_KEYWORDS.items():
                            if len(works_by_tech[tech_name]) >= max_works_per_tech:
                                continue

                            validation_stats[tech_name]['total_scanned'] += 1

                            # Enhanced validation with NULL capture
                            is_valid, validation_details, null_captures = validate_work_with_null_capture(
                                work, tech_name, keywords, strictness=strictness
                            )

                            # Update stats
                            if validation_details['stage1_keyword']:
                                validation_stats[tech_name]['stage1_passed'] += 1
                            if validation_details['stage2_topic']:
                                validation_stats[tech_name]['stage2_passed'] += 1
                            if validation_details['stage3_source']:
                                validation_stats[tech_name]['stage3_passed'] += 1
                            if validation_details['stage4_quality']:
                                validation_stats[tech_name]['stage4_passed'] += 1

                            # Capture NULL data
                            if null_captures['keyword_fail_topic_pass']:
                                null_keyword_fails.append(null_captures['keyword_fail_topic_pass'])
                            if null_captures['keyword_pass_topic_fail']:
                                null_topic_fails.append(null_captures['keyword_pass_topic_fail'])
                            if null_captures['strategic_institution_both_fail']:
                                null_strategic_inst.append(null_captures['strategic_institution_both_fail'])

                            if is_valid:
                                validation_stats[tech_name]['final_accepted'] += 1
                                works_by_tech[tech_name].append((work, validation_details))

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"  [WARN] Error processing {file_path.name}: {e}")
            continue

    # Summary
    print(f"\n{'=' * 80}")
    print(f"PARTITION {partition_id} PROCESSING COMPLETE")
    print(f"{'=' * 80}")
    print(f"Files processed: {files_processed:,}")
    print(f"Works scanned: {total_works_scanned:,}")
    print()

    print("Works collected per technology:")
    for tech, works in sorted(works_by_tech.items()):
        print(f"  {tech:20s}: {len(works):6,}")

    print(f"\nNULL Data Captures:")
    print(f"  Keyword FAIL + Topic PASS: {len(null_keyword_fails):,} (gaps in keyword coverage)")
    print(f"  Keyword PASS + Topic FAIL: {len(null_topic_fails):,} (potential false positives)")
    print(f"  Strategic Institution Both FAIL: {len(null_strategic_inst):,} (missed strategic works)")

    return works_by_tech, validation_stats, null_keyword_fails, null_topic_fails, null_strategic_inst

def insert_null_data(conn, null_keyword_fails, null_topic_fails, null_strategic_inst):
    """Insert NULL data captures into database"""

    print(f"\n{'=' * 80}")
    print("INSERTING NULL DATA CAPTURES")
    print(f"{'=' * 80}")

    # Insert keyword fails (topic passes)
    print(f"\n[1/3] Inserting {len(null_keyword_fails):,} keyword fails...")
    for capture in null_keyword_fails:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO openalex_null_keyword_fails (
                    work_id, doi, title, publication_year, cited_by_count,
                    abstract, technology_domain, null_reason, matched_topic,
                    topic_score, has_chinese_institution, has_strategic_funder,
                    high_citations, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                capture['work_id'],
                capture['doi'],
                capture['title'],
                capture['publication_year'],
                capture['cited_by_count'],
                capture['abstract'],
                capture['technology_domain'],
                capture['null_reason'],
                capture['matched_topic'],
                capture['topic_score'],
                capture['has_chinese_institution'],
                capture['has_strategic_funder'],
                capture['high_citations'],
                datetime.now().isoformat()
            ))
        except Exception as e:
            print(f"  [WARN] Error inserting keyword fail: {e}")

    # Insert topic fails (keyword passes)
    print(f"\n[2/3] Inserting {len(null_topic_fails):,} topic fails...")
    for capture in null_topic_fails:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO openalex_null_topic_fails (
                    work_id, doi, title, publication_year, cited_by_count,
                    abstract, technology_domain, matched_keyword, actual_topics,
                    created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                capture['work_id'],
                capture['doi'],
                capture['title'],
                capture['publication_year'],
                capture['cited_by_count'],
                capture['abstract'],
                capture['technology_domain'],
                capture['matched_keyword'],
                capture['actual_topics'],
                datetime.now().isoformat()
            ))
        except Exception as e:
            print(f"  [WARN] Error inserting topic fail: {e}")

    # Insert strategic institution both fails
    print(f"\n[3/3] Inserting {len(null_strategic_inst):,} strategic institution fails...")
    for capture in null_strategic_inst:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO openalex_null_strategic_institution (
                    work_id, doi, title, publication_year, institution_id,
                    institution_name, institution_country, abstract, all_topics,
                    created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                capture['work_id'],
                capture['doi'],
                capture['title'],
                capture['publication_year'],
                capture['institution_id'],
                capture['institution_name'],
                capture['institution_country'],
                capture['abstract'],
                capture['all_topics'],
                datetime.now().isoformat()
            ))
        except Exception as e:
            print(f"  [WARN] Error inserting strategic inst fail: {e}")

    conn.commit()
    print("\n[OK] NULL data captures inserted")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenAlex concurrent worker with NULL data capture')
    parser.add_argument('--partition-id', type=int, required=True, help='Partition ID')
    parser.add_argument('--start-date', required=True, help='Start date (updated_date=YYYY-MM-DD format)')
    parser.add_argument('--end-date', required=True, help='End date (updated_date=YYYY-MM-DD format)')
    parser.add_argument('--max-per-tech', type=int, default=25000, help='Max works per technology')
    parser.add_argument('--strictness', choices=['lenient', 'moderate', 'strict'], default='moderate')

    args = parser.parse_args()

    print(f"{'=' * 80}")
    print(f"OPENALEX CONCURRENT WORKER - PARTITION {args.partition_id}")
    print(f"WITH NULL DATA PROTOCOL")
    print(f"{'=' * 80}\n")

    # Connect to database
    conn = sqlite3.connect(str(MASTER_DB))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # Create NULL data tables
    create_null_data_tables(conn)

    # Process partition
    works_by_tech, validation_stats, null_keyword_fails, null_topic_fails, null_strategic_inst = process_partition_data(
        args.partition_id,
        args.start_date,
        args.end_date,
        args.max_per_tech,
        args.strictness
    )

    # Insert NULL data captures
    insert_null_data(conn, null_keyword_fails, null_topic_fails, null_strategic_inst)

    # Insert regular works (using existing logic from main script)
    # TODO: Import and call insert logic from main script

    conn.close()

    print(f"\n[OK] Partition {args.partition_id} complete")
