"""
Comprehensive OpenAlex Integration to Master Database
Extracts: works, authors, institutions, funders, countries for any technology domain
Designed for multi-technology analysis with rich metadata
"""

import sqlite3
import gzip
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

# Paths
MASTER_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OPENALEX_DATA = Path("F:/OSINT_Backups/openalex/data")

# Technology domain keywords (expandable)
TECHNOLOGY_KEYWORDS = {
    'AI': [
        'artificial intelligence', 'machine learning', 'deep learning',
        'neural network', 'natural language processing', 'computer vision',
        'reinforcement learning', 'generative ai', 'large language model',
        'transformer', 'llm', 'gpt', 'bert', 'chatbot', 'robotics'
    ],
    'Quantum': [
        'quantum computing', 'quantum information', 'quantum mechanics',
        'qubit', 'quantum entanglement', 'quantum cryptography',
        'quantum simulation', 'quantum sensing', 'quantum communication',
        'quantum algorithm', 'quantum error correction', 'quantum supremacy'
    ],
    'Space': [
        'space technology', 'satellite', 'launch vehicle', 'spacecraft',
        'orbital mechanics', 'space exploration', 'astronaut', 'rocket',
        'space station', 'planetary science', 'astrophysics', 'exoplanet',
        'gravitational wave', 'space telescope', 'mars', 'lunar'
    ],
    'Semiconductors': [
        'semiconductor', 'silicon', 'chip', 'transistor', 'mosfet',
        'integrated circuit', 'wafer', 'lithography', 'etching',
        'doping', 'cmos', 'gaas', 'gan', 'sic', 'wide bandgap',
        'euv', 'finfet', 'gate-all-around', 'chiplet', '3nm', '5nm'
    ],
    'Smart_City': [
        'smart city', 'urban computing', 'intelligent transportation',
        'smart grid', 'iot', 'internet of things', 'sensor network',
        'traffic management', 'smart building', 'urban planning',
        'connected city', 'smart mobility', 'urban analytics'
    ],
    'Neuroscience': [
        'neuroscience', 'brain', 'neural', 'neuron', 'synapse',
        'brain-computer interface', 'bci', 'cognitive', 'fmri',
        'electroencephalography', 'eeg', 'neuroimaging', 'cortex',
        'hippocampus', 'neuroplasticity', 'connectome', 'optogenetics'
    ],
    'Biotechnology': [
        'crispr', 'gene editing', 'synthetic biology', 'genome sequencing',
        'bioinformatics', 'protein engineering', 'cell therapy',
        'mrna vaccine', 'immunotherapy', 'bioengineering', 'genetic engineering'
    ],
    'Advanced_Materials': [
        'graphene', 'metamaterial', 'nanomaterial', 'carbon nanotube',
        'superconductor', '2d material', 'quantum dot', 'photonic crystal',
        'smart material', 'biomaterial', 'composite material'
    ],
    'Energy': [
        'fusion energy', 'solar cell', 'battery technology', 'energy storage',
        'hydrogen fuel', 'renewable energy', 'carbon capture', 'nuclear fusion',
        'perovskite solar', 'solid state battery', 'grid storage'
    ]
}

def create_openalex_comprehensive_tables(conn):
    """Create comprehensive OpenAlex tables for multi-technology analysis"""

    # Works (publications)
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
        created_date TEXT,
        updated_date TEXT
    )
    """)

    # Authors with full metadata
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_authors_full (
        author_id TEXT PRIMARY KEY,
        orcid TEXT,
        display_name TEXT,
        works_count INTEGER,
        cited_by_count INTEGER,
        h_index INTEGER,
        i10_index INTEGER,
        last_known_institution_id TEXT,
        last_known_institution_name TEXT,
        institution_country_code TEXT,
        institution_country_name TEXT,
        created_date TEXT,
        updated_date TEXT
    )
    """)

    # Work-Author relationship
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_work_authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_id TEXT,
        author_id TEXT,
        author_position TEXT,
        institution_id TEXT,
        institution_name TEXT,
        country_code TEXT,
        FOREIGN KEY (work_id) REFERENCES openalex_works(work_id),
        FOREIGN KEY (author_id) REFERENCES openalex_authors_full(author_id)
    )
    """)

    # Institutions
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_institutions (
        institution_id TEXT PRIMARY KEY,
        display_name TEXT,
        ror TEXT,
        country_code TEXT,
        country_name TEXT,
        type TEXT,
        works_count INTEGER,
        cited_by_count INTEGER,
        city TEXT,
        region TEXT,
        created_date TEXT,
        updated_date TEXT
    )
    """)

    # Funders
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_funders_full (
        funder_id TEXT PRIMARY KEY,
        display_name TEXT,
        alternate_titles TEXT,
        country_code TEXT,
        country_name TEXT,
        description TEXT,
        works_count INTEGER,
        grants_count INTEGER,
        created_date TEXT,
        updated_date TEXT
    )
    """)

    # Work-Funder relationship (grants)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_work_funders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_id TEXT,
        funder_id TEXT,
        award_id TEXT,
        FOREIGN KEY (work_id) REFERENCES openalex_works(work_id),
        FOREIGN KEY (funder_id) REFERENCES openalex_funders_full(funder_id)
    )
    """)

    # Topics/Concepts
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

    # Country statistics per technology
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_country_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        technology_domain TEXT,
        country_code TEXT,
        country_name TEXT,
        works_count INTEGER,
        total_citations INTEGER,
        avg_citations_per_work REAL,
        h_index INTEGER,
        top_institutions TEXT,
        collection_date TEXT,
        UNIQUE(technology_domain, country_code)
    )
    """)

    # Integration metadata
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

def matches_technology(text, technology_keywords):
    """Check if text matches any technology keywords"""
    if not text:
        return False

    text_lower = text.lower()
    for keyword in technology_keywords:
        if keyword.lower() in text_lower:
            return True
    return False

def sample_works_data(technology_domains, max_works_per_tech=1000):
    """
    Sample works from OpenAlex dataset for specified technologies
    This is a SAMPLE function - for full processing, modify to process all files
    """

    print(f"\n{'=' * 80}")
    print("SAMPLING OPENALEX WORKS DATA")
    print(f"{'=' * 80}")

    works_dir = OPENALEX_DATA / "works"

    if not works_dir.exists():
        print(f"[ERROR] Works directory not found: {works_dir}")
        return {}

    # Count available files
    work_files = list(works_dir.rglob("*.gz"))
    print(f"Found {len(work_files):,} work files in OpenAlex dataset")
    print(f"Sampling first 10 files for demo (modify for full processing)\n")

    works_by_tech = defaultdict(list)
    files_processed = 0

    # Sample first 10 files (modify for full processing)
    for file_path in work_files[:10]:
        files_processed += 1
        print(f"Processing {files_processed}/10: {file_path.name}")

        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line_num, line in enumerate(f):
                    if line_num % 1000 == 0 and line_num > 0:
                        print(f"  Line {line_num:,}...", end='\r')

                    try:
                        work = json.loads(line)

                        # Check title and abstract against technology keywords
                        title = work.get('title', '')
                        abstract_inverted = work.get('abstract_inverted_index', {})
                        abstract = ' '.join(abstract_inverted.keys()) if abstract_inverted else ''

                        combined_text = f"{title} {abstract}"

                        # Check each technology
                        for tech_name, keywords in technology_domains.items():
                            if len(works_by_tech[tech_name]) >= max_works_per_tech:
                                continue

                            if matches_technology(combined_text, keywords):
                                works_by_tech[tech_name].append(work)
                                print(f"  [{tech_name}] Found matching work: {title[:60]}...")

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"  [WARN] Error processing {file_path.name}: {e}")
            continue

    print(f"\n\n{'=' * 80}")
    print("SAMPLING COMPLETE")
    print(f"{'=' * 80}")
    for tech, works in works_by_tech.items():
        print(f"  {tech}: {len(works):,} works sampled")

    return works_by_tech

def integrate_openalex_sample():
    """
    Main integration function - SAMPLE MODE
    For full integration, call sample_works_data() with all files
    """

    print("=" * 80)
    print("OPENALEX COMPREHENSIVE INTEGRATION (SAMPLE MODE)")
    print("=" * 80)
    print()
    print("NOTE: This is a SAMPLE integration using 10 files.")
    print("For FULL integration, modify sample_works_data() to process all files.")
    print()

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

    # Create tables
    create_openalex_comprehensive_tables(conn)

    # Sample works for all technologies
    print(f"\nTechnologies to process:")
    for tech, keywords in TECHNOLOGY_KEYWORDS.items():
        print(f"  {tech}: {len(keywords)} keywords")

    works_by_tech = sample_works_data(TECHNOLOGY_KEYWORDS, max_works_per_tech=100)

    if not works_by_tech:
        print("\n[WARN] No works found. Check OpenAlex data path and keywords.")
        conn.close()
        return

    # Process each technology
    collection_date = datetime.now().isoformat()

    for tech_name, works in works_by_tech.items():
        print(f"\n{'=' * 80}")
        print(f"PROCESSING: {tech_name}")
        print(f"{'=' * 80}")

        authors_seen = set()
        institutions_seen = set()
        funders_seen = set()

        for work in works:
            # Insert work
            try:
                work_id = work.get('id', '').split('/')[-1]

                # Extract abstract
                abstract_inv = work.get('abstract_inverted_index', {})
                abstract = ' '.join(abstract_inv.keys())[:1000] if abstract_inv else None

                # Extract primary topic
                topics = work.get('topics', [])
                primary_topic = topics[0].get('display_name') if topics else None

                # Extract open access
                oa = work.get('open_access', {})
                oa_status = oa.get('oa_status')

                # Extract source
                primary_location = work.get('primary_location', {})
                source = primary_location.get('source', {})
                source_name = source.get('display_name')

                conn.execute("""
                    INSERT OR IGNORE INTO openalex_works (
                        work_id, doi, title, publication_year, publication_date,
                        type, cited_by_count, is_retracted, is_paratext,
                        abstract, primary_topic, technology_domain,
                        open_access_status, source_name, created_date, updated_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    work_id,
                    work.get('doi'),
                    work.get('title'),
                    work.get('publication_year'),
                    work.get('publication_date'),
                    work.get('type'),
                    work.get('cited_by_count', 0),
                    work.get('is_retracted', False),
                    work.get('is_paratext', False),
                    abstract,
                    primary_topic,
                    tech_name,
                    oa_status,
                    source_name,
                    work.get('created_date'),
                    work.get('updated_date')
                ))

                # Insert authors and authorships
                authorships = work.get('authorships', [])
                for authorship in authorships:
                    author = authorship.get('author', {})
                    author_id = author.get('id', '').split('/')[-1]

                    if author_id and author_id not in authors_seen:
                        authors_seen.add(author_id)

                        # Note: Full author metadata requires processing authors/ directory
                        # This is placeholder - implement full author processing separately

                    # Insert work-author relationship
                    institutions_auth = authorship.get('institutions', [])
                    for inst in institutions_auth:
                        inst_id = inst.get('id', '').split('/')[-1]
                        inst_name = inst.get('display_name')
                        country = inst.get('country_code')

                        conn.execute("""
                            INSERT INTO openalex_work_authors (
                                work_id, author_id, author_position,
                                institution_id, institution_name, country_code
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            work_id,
                            author_id,
                            authorship.get('author_position'),
                            inst_id,
                            inst_name,
                            country
                        ))

                        if inst_id:
                            institutions_seen.add(inst_id)

                # Insert funders/grants
                grants = work.get('grants', [])
                for grant in grants:
                    funder = grant.get('funder')
                    if funder:
                        funder_id = funder.split('/')[-1]
                        funders_seen.add(funder_id)

                        conn.execute("""
                            INSERT INTO openalex_work_funders (
                                work_id, funder_id, award_id
                            ) VALUES (?, ?, ?)
                        """, (
                            work_id,
                            funder_id,
                            grant.get('award_id')
                        ))

                # Insert topics
                for topic in topics:
                    topic_id = topic.get('id', '').split('/')[-1]
                    conn.execute("""
                        INSERT INTO openalex_work_topics (
                            work_id, topic_id, topic_name, score
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        work_id,
                        topic_id,
                        topic.get('display_name'),
                        topic.get('score')
                    ))

            except Exception as e:
                print(f"  [WARN] Error inserting work: {e}")
                continue

        # Log integration
        conn.execute("""
            INSERT INTO openalex_integration_log (
                integration_date, technology_domain, works_processed,
                authors_processed, institutions_processed, funders_processed,
                data_source, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            collection_date,
            tech_name,
            len(works),
            len(authors_seen),
            len(institutions_seen),
            len(funders_seen),
            'OpenAlex Snapshot (Sample 10 files)',
            'Sample integration - process all files for complete data'
        ))

        print(f"  Works: {len(works):,}")
        print(f"  Authors: {len(authors_seen):,}")
        print(f"  Institutions: {len(institutions_seen):,}")
        print(f"  Funders: {len(funders_seen):,}")

    conn.commit()

    # Summary
    print(f"\n{'=' * 80}")
    print("INTEGRATION SUMMARY")
    print(f"{'=' * 80}")

    works_count = conn.execute("SELECT COUNT(*) FROM openalex_works").fetchone()[0]
    authors_count = conn.execute("SELECT COUNT(DISTINCT author_id) FROM openalex_work_authors").fetchone()[0]
    institutions_count = conn.execute("SELECT COUNT(DISTINCT institution_id) FROM openalex_work_authors WHERE institution_id IS NOT NULL").fetchone()[0]
    funders_count = conn.execute("SELECT COUNT(DISTINCT funder_id) FROM openalex_work_funders").fetchone()[0]

    print(f"\nTotal records in master database:")
    print(f"  Works: {works_count:,}")
    print(f"  Unique authors: {authors_count:,}")
    print(f"  Unique institutions: {institutions_count:,}")
    print(f"  Unique funders: {funders_count:,}")

    # Per-technology breakdown
    print(f"\nWorks per technology:")
    tech_counts = conn.execute("""
        SELECT technology_domain, COUNT(*)
        FROM openalex_works
        GROUP BY technology_domain
    """).fetchall()

    for tech, count in tech_counts:
        print(f"  {tech}: {count:,}")

    # Top countries
    print(f"\nTop countries (by institution affiliations):")
    country_counts = conn.execute("""
        SELECT country_code, COUNT(DISTINCT work_id) as works
        FROM openalex_work_authors
        WHERE country_code IS NOT NULL
        GROUP BY country_code
        ORDER BY works DESC
        LIMIT 10
    """).fetchall()

    for country, count in country_counts:
        print(f"  {country}: {count:,} works")

    conn.close()

    print(f"\n{'=' * 80}")
    print("[OK] SAMPLE INTEGRATION COMPLETE")
    print(f"{'=' * 80}")
    print(f"\nMaster database: {MASTER_DB}")
    print(f"To process FULL dataset, modify sample_works_data() to process all files")
    print()

if __name__ == '__main__':
    integrate_openalex_sample()
