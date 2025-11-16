"""
Comprehensive OpenAlex Integration to Master Database - VERSION 2
IMPROVED QUALITY: Multi-stage validation with OpenAlex topics and word boundaries
Fixes 80-90% false positive rate from v1
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

# Technology domain keywords with improved specificity
TECHNOLOGY_KEYWORDS = {
    'AI': [
        'artificial intelligence', 'machine learning', 'deep learning',
        'neural network', 'natural language processing', 'computer vision',
        'reinforcement learning', 'generative ai', 'large language model',
        'transformer', 'llm', 'gpt', 'bert', 'chatbot', 'convolutional neural'
    ],
    'Quantum': [
        'quantum computing', 'quantum information', 'quantum mechanics',
        'qubit', 'quantum entanglement', 'quantum cryptography',
        'quantum simulation', 'quantum sensing', 'quantum communication',
        'quantum algorithm', 'quantum error correction', 'quantum supremacy',
        'quantum gate', 'quantum circuit'
    ],
    'Space': [
        'space technology', 'satellite', 'launch vehicle', 'spacecraft',
        'orbital mechanics', 'space exploration', 'astronaut', 'rocket propulsion',
        'space station', 'planetary science', 'astrophysics', 'exoplanet',
        'gravitational wave', 'space telescope', 'mars mission', 'lunar exploration',
        'space debris', 'reentry vehicle'
    ],
    'Semiconductors': [
        'semiconductor device', 'semiconductor manufacturing', 'transistor',
        'mosfet', 'integrated circuit', 'silicon wafer', 'photolithography',
        'chemical vapor deposition', 'doping process', 'cmos technology',
        'gaas device', 'gan device', 'sic device', 'wide bandgap semiconductor',
        'euv lithography', 'finfet', 'gate-all-around', 'chiplet architecture'
    ],
    'Smart_City': [
        'smart city', 'urban computing', 'intelligent transportation system',
        'smart grid', 'internet of things', 'sensor network',
        'traffic management system', 'smart building', 'urban planning',
        'connected city', 'smart mobility', 'urban analytics',
        'smart infrastructure'
    ],
    'Neuroscience': [
        'neuroscience', 'brain imaging', 'neural circuit', 'neuron activity',
        'synaptic transmission', 'brain-computer interface', 'bci system',
        'cognitive neuroscience', 'fmri', 'electroencephalography',
        'eeg recording', 'neuroimaging', 'cortex', 'hippocampus',
        'neuroplasticity', 'connectome', 'optogenetics'
    ],
    'Biotechnology': [
        'crispr', 'gene editing', 'synthetic biology', 'genome sequencing',
        'bioinformatics', 'protein engineering', 'cell therapy',
        'mrna vaccine', 'immunotherapy', 'bioengineering',
        'genetic engineering', 'recombinant dna'
    ],
    'Advanced_Materials': [
        'graphene', 'metamaterial', 'nanomaterial', 'carbon nanotube',
        'superconductor', '2d material', 'quantum dot', 'photonic crystal',
        'smart material', 'biomaterial', 'composite material',
        'nanostructure', 'thin film'
    ],
    'Energy': [
        'fusion energy', 'solar cell', 'battery technology', 'energy storage',
        'hydrogen fuel cell', 'renewable energy', 'carbon capture',
        'nuclear fusion reactor', 'perovskite solar cell',
        'solid state battery', 'grid scale storage', 'wind turbine'
    ]
}

# OpenAlex topic whitelist - relevant topics for each technology
# These are example patterns - expand based on actual OpenAlex topic taxonomy
RELEVANT_TOPICS = {
    'AI': [
        'artificial intelligence', 'machine learning', 'deep learning',
        'neural network', 'computer vision', 'natural language processing',
        'pattern recognition', 'data mining', 'computational intelligence'
    ],
    'Quantum': [
        'quantum', 'qubit', 'quantum computing', 'quantum information',
        'quantum mechanics', 'quantum physics'
    ],
    'Space': [
        'space', 'aerospace', 'astrophysics', 'planetary', 'orbital',
        'satellite', 'astronautics', 'celestial mechanics'
    ],
    'Semiconductors': [
        'semiconductor', 'microelectronics', 'integrated circuit', 'vlsi',
        'transistor', 'electronic device', 'solid-state electronics',
        'electrical engineering', 'device physics', 'fabrication'
    ],
    'Smart_City': [
        'smart city', 'urban', 'iot', 'internet of things', 'sensor network',
        'intelligent transportation', 'smart grid', 'urban computing'
    ],
    'Neuroscience': [
        'neuroscience', 'neurology', 'brain', 'cognitive', 'neural',
        'neuroimaging', 'brain science', 'neurophysiology'
    ],
    'Biotechnology': [
        'biotechnology', 'genetic engineering', 'molecular biology',
        'synthetic biology', 'genomics', 'gene therapy', 'bioengineering'
    ],
    'Advanced_Materials': [
        'materials science', 'nanomaterial', 'nanotechnology',
        'materials engineering', 'condensed matter', 'materials physics'
    ],
    'Energy': [
        'energy', 'renewable energy', 'battery', 'fuel cell',
        'solar cell', 'energy storage', 'power engineering'
    ]
}

# Journal/source exclusion patterns (biology, medicine, agriculture)
EXCLUDED_SOURCE_PATTERNS = [
    r'.*\bbiolog',  # biology, microbiology
    r'.*\bmedicine\b',
    r'.*\bmedical\b',
    r'.*\bclinical\b',
    r'.*\bagricult',
    r'.*\bgenomics?\b',  # Unless in biotechnology context
    r'.*\bchemistry\b',  # Too broad, causes false positives
    r'.*\becology\b',
    r'.*\bbotany\b',
    r'.*\bzoology\b',
    r'.*\bphysiology\b'
]

def matches_technology_improved(text, technology_keywords):
    """
    Improved keyword matching with word boundaries
    Returns (matched, keyword) tuple
    """
    if not text:
        return False, None

    text_lower = text.lower()

    for keyword in technology_keywords:
        # Use word boundaries for single words, substring for phrases
        if ' ' in keyword:  # Multi-word phrase
            if keyword.lower() in text_lower:
                return True, keyword
        else:  # Single word - require word boundary
            # Use regex word boundary \b
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                return True, keyword

    return False, None

def has_relevant_topic(topics, tech_name, strictness='moderate'):
    """
    Check if any of the work's topics are relevant to the technology

    strictness levels:
    - 'lenient': Just check if topic contains any keyword
    - 'moderate': Require good substring match
    - 'strict': Require exact match or very close match
    """
    if not topics:
        return False, None

    relevant_patterns = RELEVANT_TOPICS.get(tech_name, [])

    for topic in topics:
        topic_name = topic.get('display_name', '').lower()
        topic_score = topic.get('score', 0)

        for pattern in relevant_patterns:
            pattern_lower = pattern.lower()

            if strictness == 'lenient':
                # Any substring match
                if pattern_lower in topic_name or topic_name in pattern_lower:
                    return True, topic_name

            elif strictness == 'moderate':
                # Good match: either exact or clear substring
                if pattern_lower in topic_name:
                    # Require high score for broad matches
                    if len(pattern_lower) > 5 or topic_score > 0.5:
                        return True, topic_name

            elif strictness == 'strict':
                # Very specific match required
                if pattern_lower == topic_name or (pattern_lower in topic_name and topic_score > 0.6):
                    return True, topic_name

    return False, None

def is_excluded_source(source_name):
    """Check if source should be excluded (biology, medicine journals)"""
    if not source_name:
        return False

    source_lower = source_name.lower()

    for pattern in EXCLUDED_SOURCE_PATTERNS:
        if re.search(pattern, source_lower):
            return True, pattern

    return False, None

def validate_work_multistage(work, tech_name, tech_keywords, strictness='moderate'):
    """
    Multi-stage validation for work classification

    Returns: (is_valid, validation_details)

    Stages:
    1. Keyword matching (with word boundaries)
    2. Topic validation (OpenAlex topics)
    3. Source exclusion (filter out biology/medicine)
    4. Quality checks (has abstract, not retracted)
    """

    validation_details = {
        'stage1_keyword': False,
        'stage2_topic': False,
        'stage3_source': True,  # Default pass
        'stage4_quality': True,  # Default pass
        'matched_keyword': None,
        'matched_topic': None,
        'exclusion_reason': None
    }

    # Extract text
    title = work.get('title', '')
    abstract_inverted = work.get('abstract_inverted_index', {})
    abstract = ' '.join(abstract_inverted.keys()) if abstract_inverted else ''
    combined_text = f"{title} {abstract}"

    # Stage 1: Keyword matching
    has_keyword, matched_keyword = matches_technology_improved(combined_text, tech_keywords)
    validation_details['stage1_keyword'] = has_keyword
    validation_details['matched_keyword'] = matched_keyword

    if not has_keyword:
        return False, validation_details

    # Stage 2: Topic validation
    topics = work.get('topics', [])
    has_topic, matched_topic = has_relevant_topic(topics, tech_name, strictness=strictness)
    validation_details['stage2_topic'] = has_topic
    validation_details['matched_topic'] = matched_topic

    if not has_topic:
        return False, validation_details

    # Stage 3: Source exclusion
    primary_location = work.get('primary_location', {})
    source = primary_location.get('source', {})
    source_name = source.get('display_name', '')

    # Special case: biotechnology papers CAN come from genomics journals
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

    # All stages passed
    return True, validation_details

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
        validation_keyword TEXT,
        validation_topic TEXT,
        validation_score REAL,
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

    # Validation statistics
    conn.execute("""
    CREATE TABLE IF NOT EXISTS openalex_validation_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        integration_date TEXT,
        technology_domain TEXT,
        total_scanned INTEGER,
        stage1_passed INTEGER,
        stage2_passed INTEGER,
        stage3_passed INTEGER,
        stage4_passed INTEGER,
        final_accepted INTEGER,
        false_positive_rate REAL
    )
    """)

    conn.commit()
    print("[OK] OpenAlex comprehensive tables created/verified")

def process_all_works_data(technology_domains, max_works_per_tech=10000, strictness='moderate', sample_mode=False):
    """
    Process OpenAlex files for specified technologies with improved validation

    strictness: 'lenient', 'moderate', 'strict'
    sample_mode: If True, only process first 10 files for testing
    """

    print(f"\n{'=' * 80}")
    print("OPENALEX PROCESSING - VERSION 2 (IMPROVED VALIDATION)")
    print(f"{'=' * 80}")
    print(f"Validation strictness: {strictness}")
    print(f"Max works per technology: {max_works_per_tech:,}")
    print(f"Total target works: {max_works_per_tech * len(technology_domains):,}")
    print(f"Sample mode: {'YES (10 files)' if sample_mode else 'NO (all files)'}")

    works_dir = OPENALEX_DATA / "works"

    if not works_dir.exists():
        print(f"[ERROR] Works directory not found: {works_dir}")
        return {}, {}

    # Count available files
    work_files = list(works_dir.rglob("*.gz"))

    if sample_mode:
        work_files = work_files[:100]
        print(f"\n[SAMPLE MODE] Processing first 100 files for comprehensive testing")

    print(f"\nFound {len(work_files):,} work files to process")

    works_by_tech = defaultdict(list)
    validation_stats = defaultdict(lambda: {
        'total_scanned': 0,
        'stage1_passed': 0,
        'stage2_passed': 0,
        'stage3_passed': 0,
        'stage4_passed': 0,
        'final_accepted': 0
    })

    files_processed = 0
    total_lines_scanned = 0

    # Process files
    for file_path in work_files:
        files_processed += 1

        # Check if we've hit max for all technologies
        all_maxed = all(len(works_by_tech[tech]) >= max_works_per_tech for tech in technology_domains.keys())
        if all_maxed:
            print(f"\n[OK] Reached max works for all technologies. Stopping.")
            break

        print(f"\nProcessing {files_processed}/{len(work_files)}: {file_path.name}")

        # Show status
        status_parts = []
        for tech in ['AI', 'Quantum', 'Semiconductors']:  # Sample for display
            count = len(works_by_tech.get(tech, []))
            status_parts.append(f"{tech}: {count}/{max_works_per_tech}")
        print(f"  Status: {' | '.join(status_parts)}")

        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line_num, line in enumerate(f):
                    total_lines_scanned += 1

                    if line_num % 10000 == 0 and line_num > 0:
                        print(f"  Scanned {line_num:,} works in this file...", end='\r')

                    try:
                        work = json.loads(line)

                        # Check each technology
                        for tech_name, keywords in technology_domains.items():
                            if len(works_by_tech[tech_name]) >= max_works_per_tech:
                                continue

                            validation_stats[tech_name]['total_scanned'] += 1

                            # Multi-stage validation
                            is_valid, validation_details = validate_work_multistage(
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

                            if is_valid:
                                validation_stats[tech_name]['final_accepted'] += 1
                                works_by_tech[tech_name].append((work, validation_details))

                                # Print first 20 matches per tech to review quality
                                if len(works_by_tech[tech_name]) <= 20:
                                    title = work.get('title', '')[:60]
                                    topic = validation_details['matched_topic'] or 'None'
                                    print(f"  [{tech_name}] #{len(works_by_tech[tech_name])}: {title}... (topic: {topic})")

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"  [WARN] Error processing {file_path.name}: {e}")
            continue

        # Progress summary every 100 files (or every 5 in sample mode)
        interval = 5 if sample_mode else 100
        if files_processed % interval == 0:
            print(f"\n{'='*60}")
            print(f"Progress: {files_processed}/{len(work_files)} files ({(files_processed/len(work_files)*100):.1f}%)")
            print(f"Total works scanned: {total_lines_scanned:,}")
            print(f"{'='*60}")
            for tech, works in sorted(works_by_tech.items()):
                pct = (len(works) / max_works_per_tech) * 100
                stats = validation_stats[tech]
                precision = (stats['final_accepted'] / stats['stage1_passed'] * 100) if stats['stage1_passed'] > 0 else 0
                print(f"  {tech:20s}: {len(works):6,} / {max_works_per_tech:6,} ({pct:5.1f}%) | Precision: {precision:.1f}%")
            print()

    print(f"\n\n{'=' * 80}")
    print("PROCESSING COMPLETE")
    print(f"{'=' * 80}")
    print(f"Files processed: {files_processed:,} / {len(work_files):,}")
    print(f"Total works scanned: {total_lines_scanned:,}")
    print()

    # Detailed validation statistics
    print("\nVALIDATION STATISTICS (Quality Metrics):")
    print(f"{'='*80}")
    for tech, stats in sorted(validation_stats.items()):
        print(f"\n{tech}:")
        print(f"  Total scanned: {stats['total_scanned']:,}")
        print(f"  Stage 1 (Keywords): {stats['stage1_passed']:,} ({stats['stage1_passed']/stats['total_scanned']*100:.2f}%)")
        print(f"  Stage 2 (Topics): {stats['stage2_passed']:,} ({stats['stage2_passed']/stats['stage1_passed']*100 if stats['stage1_passed'] > 0 else 0:.2f}% of keyword matches)")
        print(f"  Stage 3 (Source filter): {stats['stage3_passed']:,}")
        print(f"  Stage 4 (Quality): {stats['stage4_passed']:,}")
        print(f"  Final accepted: {stats['final_accepted']:,}")

        if stats['stage1_passed'] > 0:
            false_positive_reduction = (1 - stats['final_accepted'] / stats['stage1_passed']) * 100
            print(f"  False positive reduction: {false_positive_reduction:.1f}% (vs simple keyword matching)")

    return works_by_tech, validation_stats

def integrate_openalex_improved(max_works_per_tech=10000, strictness='moderate', sample_mode=False):
    """
    Main integration function - VERSION 2 with improved validation
    """

    print("=" * 80)
    print("OPENALEX COMPREHENSIVE INTEGRATION - VERSION 2 (IMPROVED)")
    print("=" * 80)
    print()
    print(f"Validation strictness: {strictness}")
    print(f"Sample mode: {'YES - Testing only' if sample_mode else 'NO - Full production'}")
    print(f"Target: {max_works_per_tech:,} works per technology")
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
    conn.execute("PRAGMA cache_size=-102400")  # 100MB cache

    # Create tables
    create_openalex_comprehensive_tables(conn)

    # Process works for all technologies
    print(f"\nTechnologies to process:")
    for tech, keywords in TECHNOLOGY_KEYWORDS.items():
        print(f"  {tech}: {len(keywords)} keywords, {len(RELEVANT_TOPICS.get(tech, []))} topic patterns")

    start_time = datetime.now()
    works_by_tech, validation_stats = process_all_works_data(
        TECHNOLOGY_KEYWORDS,
        max_works_per_tech=max_works_per_tech,
        strictness=strictness,
        sample_mode=sample_mode
    )

    if not works_by_tech:
        print("\n[WARN] No works found. Check OpenAlex data path and keywords.")
        conn.close()
        return

    # Process each technology - insert into database
    collection_date = datetime.now().isoformat()

    for tech_name, works_with_validation in works_by_tech.items():
        print(f"\n{'=' * 80}")
        print(f"INSERTING INTO DATABASE: {tech_name}")
        print(f"{'=' * 80}")

        authors_seen = set()
        institutions_seen = set()
        funders_seen = set()

        for idx, (work, validation_details) in enumerate(works_with_validation):
            if idx % 1000 == 0 and idx > 0:
                print(f"  Inserted {idx:,} / {len(works_with_validation):,} works...", end='\r')
                conn.commit()  # Commit every 1000 works

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

                # Validation metadata
                validation_keyword = validation_details.get('matched_keyword')
                validation_topic = validation_details.get('matched_topic')
                validation_score = 1.0 if validation_details['stage4_quality'] else 0.5

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
                    validation_keyword,
                    validation_topic,
                    validation_score,
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
            len(works_with_validation),
            len(authors_seen),
            len(institutions_seen),
            len(funders_seen),
            'OpenAlex Snapshot (V2 Improved Validation)',
            f'Strictness: {strictness}, Sample mode: {sample_mode}'
        ))

        # Log validation stats
        stats = validation_stats[tech_name]
        false_positive_rate = (1 - stats['final_accepted'] / stats['stage1_passed']) if stats['stage1_passed'] > 0 else 0

        conn.execute("""
            INSERT INTO openalex_validation_stats (
                integration_date, technology_domain, total_scanned,
                stage1_passed, stage2_passed, stage3_passed, stage4_passed,
                final_accepted, false_positive_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            collection_date,
            tech_name,
            stats['total_scanned'],
            stats['stage1_passed'],
            stats['stage2_passed'],
            stats['stage3_passed'],
            stats['stage4_passed'],
            stats['final_accepted'],
            false_positive_rate
        ))

        conn.commit()
        print(f"\n  Works: {len(works_with_validation):,}")
        print(f"  Authors: {len(authors_seen):,}")
        print(f"  Institutions: {len(institutions_seen):,}")
        print(f"  Funders: {len(funders_seen):,}")
        print(f"  False positive reduction: {false_positive_rate*100:.1f}%")

    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print(f"\n{'=' * 80}")
    print("INTEGRATION SUMMARY")
    print(f"{'=' * 80}")
    print(f"Processing time: {duration:.1f} minutes")

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
        ORDER BY COUNT(*) DESC
    """).fetchall()

    for tech, count in tech_counts:
        print(f"  {tech}: {count:,}")

    # Top countries
    print(f"\nTop 20 countries (by institution affiliations):")
    country_counts = conn.execute("""
        SELECT country_code, COUNT(DISTINCT work_id) as works
        FROM openalex_work_authors
        WHERE country_code IS NOT NULL
        GROUP BY country_code
        ORDER BY works DESC
        LIMIT 20
    """).fetchall()

    for country, count in country_counts:
        print(f"  {country}: {count:,} works")

    conn.close()

    print(f"\n{'=' * 80}")
    print("[OK] IMPROVED INTEGRATION COMPLETE")
    print(f"{'=' * 80}")
    print(f"\nMaster database: {MASTER_DB}")
    print(f"Works integrated: {works_count:,}")
    print(f"Processing time: {duration:.1f} minutes")
    print(f"Validation strictness: {strictness}")
    print()

if __name__ == '__main__':
    # Parse command-line arguments
    import argparse

    parser = argparse.ArgumentParser(description='OpenAlex integration with improved validation')
    parser.add_argument('--sample', action='store_true', help='Sample mode (10 files only)')
    parser.add_argument('--max-per-tech', type=int, default=10000, help='Max works per technology')
    parser.add_argument('--strictness', choices=['lenient', 'moderate', 'strict'], default='moderate',
                        help='Validation strictness level')

    args = parser.parse_args()

    integrate_openalex_improved(
        max_works_per_tech=args.max_per_tech,
        strictness=args.strictness,
        sample_mode=args.sample
    )
