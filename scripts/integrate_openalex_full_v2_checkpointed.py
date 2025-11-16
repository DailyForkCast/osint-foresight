"""
Comprehensive OpenAlex Integration with CHECKPOINT/RESUME - VERSION 4.1
EXPANDED KEYWORDS + TOPICS + FILE-LEVEL CHECKPOINTING

Key Features:
- Tracks which files have been fully processed
- Can resume from checkpoint without re-scanning
- Allows iterative collection (first 25K, then another 25K, etc.)
- Saves checkpoint after every 10 files processed

Usage:
  # First pass: Collect 25,000 per tech
  python integrate_openalex_full_v2_checkpointed.py --max-per-tech 25000

  # Second pass: Collect another 25,000 per tech (50K total)
  python integrate_openalex_full_v2_checkpointed.py --max-per-tech 50000 --resume

  # Start fresh (ignore checkpoint)
  python integrate_openalex_full_v2_checkpointed.py --max-per-tech 25000 --fresh-start
"""

import sqlite3
import gzip
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re
import sys

# Paths
MASTER_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OPENALEX_DATA = Path("F:/OSINT_Backups/openalex/data")
CHECKPOINT_FILE = Path("C:/Projects/OSINT - Foresight/data/openalex_v4_checkpoint.json")

# Import keyword and topic loading functions from original script
def load_expanded_keywords():
    """Load expanded Stage 1 keywords from JSON configuration (V4)"""
    config_path = Path(__file__).parent.parent / "config" / "openalex_technology_keywords_expanded.json"

    if not config_path.exists():
        print(f"[WARN] V4 expanded keywords config not found at {config_path}")
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        expanded_keywords = {}
        for tech, keyword_groups in config.items():
            if tech.startswith('_'):
                continue

            all_keywords = []
            for group_name, keywords in keyword_groups.items():
                if isinstance(keywords, list):
                    all_keywords.extend(keywords)

            expanded_keywords[tech] = all_keywords

        print(f"[V4] Loaded expanded keyword patterns from {config_path.name}")
        for tech, keywords in expanded_keywords.items():
            print(f"  {tech}: {len(keywords)} keywords")

        return expanded_keywords

    except Exception as e:
        print(f"[ERROR] Failed to load expanded keywords: {e}")
        return None

def load_expanded_topics():
    """Load expanded topic patterns from JSON configuration (V3)"""
    config_path = Path(__file__).parent.parent / "config" / "openalex_relevant_topics_expanded.json"

    if not config_path.exists():
        print(f"[WARN] V3 expanded topics config not found at {config_path}")
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        expanded_topics = {}
        for tech, pattern_groups in config.items():
            if tech.startswith('_'):
                continue

            all_patterns = []
            for group_name, patterns in pattern_groups.items():
                if isinstance(patterns, list):
                    all_patterns.extend(patterns)

            expanded_topics[tech] = all_patterns

        print(f"[V3] Loaded expanded topic patterns from {config_path.name}")
        for tech, patterns in expanded_topics.items():
            print(f"  {tech}: {len(patterns)} patterns")

        return expanded_topics

    except Exception as e:
        print(f"[ERROR] Failed to load expanded topics: {e}")
        return None

# Load patterns
EXPANDED_KEYWORDS = load_expanded_keywords()
EXPANDED_TOPICS = load_expanded_topics()

if EXPANDED_KEYWORDS:
    TECHNOLOGY_KEYWORDS = EXPANDED_KEYWORDS
    print("[V4] Using EXPANDED keyword patterns (355 total)")
else:
    print("[ERROR] Failed to load expanded keywords")
    sys.exit(1)

if EXPANDED_TOPICS:
    RELEVANT_TOPICS = EXPANDED_TOPICS
    print("[V3] Using EXPANDED topic patterns (327 total)")
else:
    print("[ERROR] Failed to load expanded topics")
    sys.exit(1)

# Validation functions (same as V4)
EXCLUDED_SOURCE_PATTERNS = [
    r'.*\bbiolog', r'.*\bmedicine\b', r'.*\bmedical\b', r'.*\bclinical\b',
    r'.*\bagricult', r'.*\bgenomics?\b', r'.*\bchemistry\b', r'.*\becology\b',
    r'.*\bbotany\b', r'.*\bzoology\b', r'.*\bphysiology\b'
]

def matches_technology_improved(text, technology_keywords):
    """Improved keyword matching with word boundaries"""
    if not text:
        return False, None

    text_lower = text.lower()

    for keyword in technology_keywords:
        if ' ' in keyword:
            if keyword.lower() in text_lower:
                return True, keyword
        else:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                return True, keyword

    return False, None

def has_relevant_topic(topics, tech_name, strictness='moderate'):
    """Check if any of the work's topics are relevant to the technology"""
    if not topics:
        return False, None

    relevant_patterns = RELEVANT_TOPICS.get(tech_name, [])

    for topic in topics:
        topic_name = topic.get('display_name', '').lower()
        topic_score = topic.get('score', 0)

        for pattern in relevant_patterns:
            pattern_lower = pattern.lower()

            if strictness == 'lenient':
                if pattern_lower in topic_name or topic_name in pattern_lower:
                    return True, topic_name

            elif strictness == 'moderate':
                if pattern_lower in topic_name:
                    if len(pattern_lower) > 5 or topic_score > 0.3:
                        return True, topic_name

            elif strictness == 'strict':
                if pattern_lower == topic_name or (pattern_lower in topic_name and topic_score > 0.6):
                    return True, topic_name

    return False, None

def is_excluded_source(source_name):
    """Check if source should be excluded (biology, medicine journals)"""
    if not source_name:
        return False, None

    source_lower = source_name.lower()

    for pattern in EXCLUDED_SOURCE_PATTERNS:
        if re.search(pattern, source_lower):
            return True, pattern

    return False, None

def validate_work_multistage(work, tech_name, tech_keywords, strictness='moderate'):
    """Multi-stage validation for work classification"""

    validation_details = {
        'stage1_keyword': False,
        'stage2_topic': False,
        'stage3_source': True,
        'stage4_quality': True,
        'matched_keyword': None,
        'matched_topic': None,
        'exclusion_reason': None
    }

    # Extract text
    title = work.get('title', '')
    abstract_inverted = work.get('abstract_inverted_index') or {}
    abstract = ' '.join(abstract_inverted.keys()) if abstract_inverted else ''
    combined_text = f"{title} {abstract}"

    # Stage 1: Keyword matching
    has_keyword, matched_keyword = matches_technology_improved(combined_text, tech_keywords)
    validation_details['stage1_keyword'] = has_keyword
    validation_details['matched_keyword'] = matched_keyword

    if not has_keyword:
        return False, validation_details

    # Stage 2: Topic validation
    topics = work.get('topics') or []
    has_topic, matched_topic = has_relevant_topic(topics, tech_name, strictness=strictness)
    validation_details['stage2_topic'] = has_topic
    validation_details['matched_topic'] = matched_topic

    if not has_topic:
        return False, validation_details

    # Stage 3: Source exclusion
    primary_location = work.get('primary_location') or {}
    source = primary_location.get('source') or {}
    source_name = source.get('display_name', '')

    if tech_name != 'Biotechnology':
        is_excluded, exclusion_pattern = is_excluded_source(source_name)
        validation_details['stage3_source'] = not is_excluded
        validation_details['exclusion_reason'] = exclusion_pattern if is_excluded else None

        if is_excluded:
            return False, validation_details

    # Stage 4: Quality checks
    is_retracted = work.get('is_retracted', False)
    is_paratext = work.get('is_paratext', False)
    has_abstract = bool(abstract_inverted)

    validation_details['stage4_quality'] = not is_retracted and not is_paratext and has_abstract

    if is_retracted or is_paratext or not has_abstract:
        return False, validation_details

    return True, validation_details

# CHECKPOINT FUNCTIONS
def load_checkpoint():
    """Load checkpoint from file"""
    if not CHECKPOINT_FILE.exists():
        return None

    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            checkpoint = json.load(f)

        print(f"\n[CHECKPOINT] Loaded from {CHECKPOINT_FILE}")
        print(f"  Last updated: {checkpoint['last_updated']}")
        print(f"  Files processed: {len(checkpoint['processed_files']):,}")
        print(f"  Works collected:")
        for tech, count in checkpoint['tech_counts'].items():
            print(f"    {tech}: {count:,}")

        return checkpoint

    except Exception as e:
        print(f"[WARN] Failed to load checkpoint: {e}")
        return None

def save_checkpoint(checkpoint):
    """Save checkpoint to file"""
    try:
        CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        return True

    except Exception as e:
        print(f"[ERROR] Failed to save checkpoint: {e}")
        return False

def get_current_counts_from_db(conn):
    """Get current work counts per technology from database"""
    counts = {}

    for tech in TECHNOLOGY_KEYWORDS.keys():
        result = conn.execute("""
            SELECT COUNT(*) FROM openalex_works
            WHERE technology_domain = ?
        """, (tech,)).fetchone()

        counts[tech] = result[0] if result else 0

    return counts

def create_openalex_comprehensive_tables(conn):
    """Create comprehensive OpenAlex tables"""

    # Works
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_works (
        work_id TEXT PRIMARY KEY,
        doi TEXT,
        title TEXT,
        publication_year INTEGER,
        publication_date TEXT,
        type TEXT,
        cited_by_count INTEGER,
        is_retracted BOOLEAN,
        is_paratext BOOLEAN,
        abstract TEXT,
        primary_topic TEXT,
        technology_domain TEXT,
        keywords TEXT,
        open_access_status TEXT,
        source_name TEXT,
        validation_keyword TEXT,
        validation_topic TEXT,
        validation_score REAL,
        created_date TEXT,
        updated_date TEXT
    )
    """)

    # Authors
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_work_authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_id TEXT,
        author_id TEXT,
        author_position TEXT,
        institution_id TEXT,
        institution_name TEXT,
        country_code TEXT,
        FOREIGN KEY (work_id) REFERENCES openalex_works(work_id)
    )
    """)

    # Funders
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_work_funders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_id TEXT,
        funder_id TEXT,
        award_id TEXT,
        FOREIGN KEY (work_id) REFERENCES openalex_works(work_id)
    )
    """)

    # Topics
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_work_topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_id TEXT,
        topic_id TEXT,
        topic_name TEXT,
        score REAL,
        FOREIGN KEY (work_id) REFERENCES openalex_works(work_id)
    )
    """)

    # Integration log
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_integration_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        integration_date TEXT,
        technology_domain TEXT,
        works_processed INTEGER,
        authors_processed INTEGER,
        institutions_processed INTEGER,
        funders_processed INTEGER,
        data_source TEXT,
        notes TEXT
    )
    """)

    conn.commit()
    print("[OK] OpenAlex comprehensive tables created/verified")

def process_with_checkpoint(conn, max_works_per_tech=25000, strictness='moderate', resume=False, fresh_start=False):
    """
    Process OpenAlex files with checkpoint/resume capability

    Args:
        conn: Database connection
        max_works_per_tech: Maximum works to collect per technology
        strictness: Validation strictness
        resume: If True, resume from checkpoint
        fresh_start: If True, ignore existing checkpoint and start fresh
    """

    print(f"\n{'=' * 80}")
    print("OPENALEX V4.1 - CHECKPOINTED PROCESSING")
    print(f"{'=' * 80}")
    print(f"Max works per tech: {max_works_per_tech:,}")
    print(f"Strictness: {strictness}")
    print(f"Resume mode: {resume}")
    print(f"Fresh start: {fresh_start}")
    print()

    # Load or initialize checkpoint
    if resume and not fresh_start:
        checkpoint = load_checkpoint()
    else:
        checkpoint = None
        if fresh_start and CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()
            print("[OK] Removed old checkpoint - starting fresh")

    if checkpoint is None:
        # Get current counts from database
        current_counts = get_current_counts_from_db(conn)

        checkpoint = {
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'processed_files': [],
            'tech_counts': current_counts,
            'max_per_tech': max_works_per_tech,
            'strictness': strictness
        }
        print(f"\n[CHECKPOINT] Starting new collection")
        print(f"  Current counts in database:")
        for tech, count in current_counts.items():
            print(f"    {tech}: {count:,}")

    # Get all work files
    works_dir = OPENALEX_DATA / "works"
    if not works_dir.exists():
        print(f"[ERROR] Works directory not found: {works_dir}")
        return

    all_files = list(works_dir.rglob("*.gz"))
    print(f"\n[OK] Found {len(all_files):,} total work files")

    # Filter out already processed files
    processed_set = set(checkpoint['processed_files'])
    remaining_files = [f for f in all_files if str(f) not in processed_set]

    print(f"[OK] Already processed: {len(processed_set):,} files")
    print(f"[OK] Remaining to process: {len(remaining_files):,} files")

    if not remaining_files:
        print("\n[OK] All files already processed!")
        return

    # Check if any technology needs more works
    needs_more = False
    for tech, current_count in checkpoint['tech_counts'].items():
        if current_count < max_works_per_tech:
            needs_more = True
            remaining = max_works_per_tech - current_count
            print(f"  {tech}: {current_count:,} / {max_works_per_tech:,} ({remaining:,} needed)")

    if not needs_more:
        print("\n[OK] All technologies at max capacity!")
        return

    # Process remaining files
    print(f"\n[STARTING] Beginning to process {len(remaining_files)} files...")
    files_processed = 0
    works_collected = defaultdict(int)

    print(f"[DEBUG] About to start file loop...")
    print(f"[DEBUG] First remaining file: {remaining_files[0] if remaining_files else 'NONE'}")
    print(f"[DEBUG] Remaining files count: {len(remaining_files)}")
    for file_path in remaining_files:
        files_processed += 1
        if files_processed == 1:
            print(f"[DEBUG] Processing first file: {file_path}")

        # Check if we've hit max for all technologies
        all_maxed = all(checkpoint['tech_counts'][tech] >= max_works_per_tech
                       for tech in TECHNOLOGY_KEYWORDS.keys())
        if all_maxed:
            print(f"\n[OK] Reached max works for all technologies. Stopping.")
            break

        if files_processed % 10 == 0:
            print(f"\nProcessing {files_processed}/{len(remaining_files)}: {file_path.name}")
            status_parts = []
            for tech in ['AI', 'Quantum', 'Semiconductors']:
                count = checkpoint['tech_counts'].get(tech, 0)
                status_parts.append(f"{tech}: {count}/{max_works_per_tech}")
            print(f"  Status: {' | '.join(status_parts)}")

        # Process file
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    try:
                        work = json.loads(line)

                        # Check each technology
                        for tech_name, keywords in TECHNOLOGY_KEYWORDS.items():
                            if checkpoint['tech_counts'][tech_name] >= max_works_per_tech:
                                continue

                            # Validate work
                            is_valid, validation_details = validate_work_multistage(
                                work, tech_name, keywords, strictness=strictness
                            )

                            if is_valid:
                                # Insert into database
                                work_id = work.get('id', '').split('/')[-1]

                                # Extract data
                                abstract_inv = work.get('abstract_inverted_index') or {}
                                abstract = ' '.join(abstract_inv.keys())[:1000] if abstract_inv else None

                                topics = work.get('topics') or []
                                primary_topic = topics[0].get('display_name') if (topics and topics[0]) else None

                                oa = work.get('open_access') or {}
                                oa_status = oa.get('oa_status')

                                primary_location = work.get('primary_location') or {}
                                source = primary_location.get('source') or {}
                                source_name = source.get('display_name')

                                # Insert work
                                conn.execute("""
                                    INSERT OR IGNORE INTO openalex_works (
                                        work_id, doi, title, publication_year, publication_date,
                                        type, cited_by_count, is_retracted, is_paratext,
                                        abstract, primary_topic, technology_domain,
                                        open_access_status, source_name,
                                        validation_keyword, validation_topic, validation_score,
                                        created_date, updated_date
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    work_id, work.get('doi'), work.get('title'),
                                    work.get('publication_year'), work.get('publication_date'),
                                    work.get('type'), work.get('cited_by_count', 0),
                                    work.get('is_retracted', False), work.get('is_paratext', False),
                                    abstract, primary_topic, tech_name,
                                    oa_status, source_name,
                                    validation_details.get('matched_keyword'),
                                    validation_details.get('matched_topic'),
                                    1.0, work.get('created_date'), work.get('updated_date')
                                ))

                                # Insert authors
                                authorships = work.get('authorships') or []
                                for authorship in authorships:
                                    if not authorship:  # Skip None authorships
                                        continue
                                    author = authorship.get('author') or {}
                                    author_id = author.get('id', '').split('/')[-1]

                                    institutions_auth = authorship.get('institutions') or []
                                    for inst in institutions_auth:
                                        if not inst:  # Skip None institutions
                                            continue
                                        inst_id = inst.get('id', '').split('/')[-1]

                                        conn.execute("""
                                            INSERT INTO openalex_work_authors (
                                                work_id, author_id, author_position,
                                                institution_id, institution_name, country_code
                                            ) VALUES (?, ?, ?, ?, ?, ?)
                                        """, (
                                            work_id, author_id, authorship.get('author_position'),
                                            inst_id, inst.get('display_name'), inst.get('country_code')
                                        ))

                                # Insert funders
                                grants = work.get('grants') or []
                                for grant in grants:
                                    if not grant:  # Skip None grants
                                        continue
                                    funder = grant.get('funder')
                                    if funder:
                                        funder_id = funder.split('/')[-1] if isinstance(funder, str) else funder.get('id', '').split('/')[-1]
                                        conn.execute("""
                                            INSERT INTO openalex_work_funders (
                                                work_id, funder_id, award_id
                                            ) VALUES (?, ?, ?)
                                        """, (work_id, funder_id, grant.get('award_id')))

                                # Insert topics
                                for topic in topics:
                                    if topic:  # Skip None topics
                                        topic_id = topic.get('id', '').split('/')[-1]
                                        conn.execute("""
                                            INSERT INTO openalex_work_topics (
                                                work_id, topic_id, topic_name, score
                                            ) VALUES (?, ?, ?, ?)
                                        """, (work_id, topic_id, topic.get('display_name'), topic.get('score')))

                                # Update counts
                                checkpoint['tech_counts'][tech_name] += 1
                                works_collected[tech_name] += 1

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"  [WARN] Error processing {file_path.name}: {e}")

        # Mark file as processed
        checkpoint['processed_files'].append(str(file_path))

        # Save checkpoint every 10 files
        if files_processed % 10 == 0:
            checkpoint['last_updated'] = datetime.now().isoformat()
            conn.commit()
            save_checkpoint(checkpoint)
            print(f"  [CHECKPOINT] Saved at {files_processed} files")

    # Final save
    checkpoint['last_updated'] = datetime.now().isoformat()
    conn.commit()
    save_checkpoint(checkpoint)

    print(f"\n{'=' * 80}")
    print("PROCESSING COMPLETE")
    print(f"{'=' * 80}")
    print(f"Files processed this session: {files_processed:,}")
    print(f"Works collected this session:")
    for tech, count in sorted(works_collected.items()):
        print(f"  {tech}: {count:,}")
    print(f"\nTotal works in database:")
    for tech, count in sorted(checkpoint['tech_counts'].items()):
        print(f"  {tech}: {count:,}")
    print(f"\nCheckpoint saved to: {CHECKPOINT_FILE}")

def main():
    """Main integration function with checkpoint support"""
    import argparse

    parser = argparse.ArgumentParser(description='OpenAlex integration with checkpoint/resume')
    parser.add_argument('--max-per-tech', type=int, default=25000, help='Max works per technology')
    parser.add_argument('--strictness', choices=['lenient', 'moderate', 'strict'], default='moderate')
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    parser.add_argument('--fresh-start', action='store_true', help='Ignore checkpoint and start fresh')

    args = parser.parse_args()

    if not MASTER_DB.exists():
        print(f"[ERROR] Master database not found: {MASTER_DB}")
        return

    if not OPENALEX_DATA.exists():
        print(f"[ERROR] OpenAlex data directory not found: {OPENALEX_DATA}")
        return

    # Connect to database
    conn = sqlite3.connect(str(MASTER_DB))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-102400")

    # Create tables
    create_openalex_comprehensive_tables(conn)

    # Process with checkpoint
    process_with_checkpoint(
        conn,
        max_works_per_tech=args.max_per_tech,
        strictness=args.strictness,
        resume=args.resume,
        fresh_start=args.fresh_start
    )

    conn.close()

    print(f"\n{'=' * 80}")
    print("[OK] INTEGRATION COMPLETE")
    print(f"{'=' * 80}")

if __name__ == '__main__':
    main()
