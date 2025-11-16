"""
COMPREHENSIVE KAGGLE ARXIV DATASET PROCESSOR
Deep dive extraction for multiple technology domains
Extracts: authors, affiliations (inferred), categories, topics, time trends, collaboration patterns
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import time

# Paths
KAGGLE_DATA = Path("F:/Kaggle_arXiv_extracted/arxiv-metadata-oai-snapshot.json")
MASTER_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")
PROCESSING_DB = Path("C:/Projects/OSINT - Foresight/data/kaggle_arxiv_processing.db")

# Expanded technology keywords (including new domains)
TECHNOLOGY_KEYWORDS = {
    'AI': {
        'categories': ['cs.AI', 'cs.LG', 'cs.CV', 'cs.CL', 'cs.RO', 'cs.NE', 'cs.MA', 'stat.ML'],
        'keywords': [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'natural language processing', 'computer vision',
            'reinforcement learning', 'generative ai', 'large language model',
            'transformer', 'llm', 'gpt', 'bert', 'chatbot', 'robotics',
            'convolutional', 'recurrent', 'attention mechanism', 'gan'
        ]
    },
    'Quantum': {
        'categories': ['quant-ph', 'cond-mat.mes-hall', 'cond-mat.supr-con',
                      'physics.atom-ph', 'physics.optics', 'cs.ET'],
        'keywords': [
            'quantum computing', 'quantum information', 'quantum mechanics',
            'qubit', 'quantum entanglement', 'quantum cryptography',
            'quantum simulation', 'quantum sensing', 'quantum communication',
            'quantum algorithm', 'quantum error correction', 'quantum supremacy',
            'superconducting qubit', 'topological qubit'
        ]
    },
    'Space': {
        'categories': [
            'astro-ph.IM', 'astro-ph.EP', 'astro-ph.CO', 'astro-ph.GA',
            'astro-ph.HE', 'astro-ph.SR', 'physics.space-ph',
            'physics.ao-ph', 'gr-qc', 'physics.plasm-ph'
        ],
        'keywords': [
            # Space technology & exploration
            'space technology', 'satellite', 'launch vehicle', 'spacecraft',
            'orbital mechanics', 'space exploration', 'astronaut', 'rocket',
            'space station', 'planetary science', 'space telescope', 'mars', 'lunar',
            # Astrophysics & astronomy
            'astrophysics', 'cosmology', 'exoplanet', 'gravitational wave',
            'black hole', 'neutron star', 'supernova', 'galaxy', 'dark matter',
            'dark energy', 'stellar evolution', 'cosmic microwave background',
            'pulsar', 'quasar'
        ]
    },
    'Semiconductors': {
        'categories': ['cond-mat.mtrl-sci', 'cond-mat.mes-hall', 'physics.app-ph', 'cs.AR'],
        'keywords': [
            'semiconductor', 'silicon', 'chip', 'transistor', 'mosfet',
            'integrated circuit', 'wafer', 'lithography', 'etching',
            'doping', 'cmos', 'gaas', 'gan', 'sic', 'wide bandgap',
            'euv', 'finfet', 'gate-all-around', 'chiplet', '3nm', '5nm',
            'photolithography', 'asml', 'tsmc process'
        ]
    },
    'Smart_City': {
        'categories': ['cs.CY', 'cs.NI', 'eess.SP', 'cs.SI'],
        'keywords': [
            'smart city', 'urban computing', 'intelligent transportation',
            'smart grid', 'iot', 'internet of things', 'sensor network',
            'traffic management', 'smart building', 'urban planning',
            'connected city', 'smart mobility', 'urban analytics',
            'civic technology', 'urban sensor', 'city data', '5g network'
        ]
    },
    'Neuroscience': {
        'categories': ['q-bio.NC', 'physics.bio-ph', 'cs.NE', 'stat.AP'],
        'keywords': [
            'neuroscience', 'brain', 'neural', 'neuron', 'synapse',
            'brain-computer interface', 'bci', 'cognitive', 'fmri',
            'electroencephalography', 'eeg', 'neuroimaging', 'cortex',
            'hippocampus', 'neuroplasticity', 'connectome', 'optogenetics',
            'neural circuit', 'brain network', 'neuroprosthetic'
        ]
    },
    'Biotechnology': {
        'categories': [
            'q-bio.GN', 'q-bio.BM', 'q-bio.CB', 'q-bio.QM', 'q-bio.PE',
            'q-bio.MN', 'q-bio.TO', 'q-bio.SC', 'physics.bio-ph'
        ],
        'keywords': [
            # Genetic engineering (original focus)
            'crispr', 'gene editing', 'synthetic biology', 'genome sequencing',
            'bioinformatics', 'protein engineering', 'cell therapy',
            'mrna vaccine', 'immunotherapy', 'bioengineering', 'genetic engineering',
            'cas9', 'gene therapy', 'recombinant dna',
            # Drug discovery & pharmacology
            'drug design', 'drug discovery', 'pharmacology', 'clinical trial',
            'pharmaceutical', 'medicinal chemistry', 'drug screening',
            # Tissue engineering & regenerative medicine
            'regenerative medicine', 'tissue engineering', 'tissue scaffold',
            'organ culture', 'stem cell', 'organoid', 'bioprinting',
            # Bioprocessing & biomanufacturing
            'fermentation', 'bioreactor', 'enzyme engineering', 'bioprocess',
            'metabolic engineering', 'biomanufacturing', 'biorefinery',
            # Systems biology & computational methods
            'metabolic network', 'pathway analysis', 'flux balance',
            'systems biology', 'computational biology', 'biological modeling',
            # Epidemiology & population biology
            'epidemiology', 'disease modeling', 'pandemic', 'epidemic',
            'population dynamics', 'evolutionary biology'
        ]
    },
    'Advanced_Materials': {
        'categories': ['cond-mat.mtrl-sci', 'cond-mat.mes-hall', 'physics.app-ph'],
        'keywords': [
            'graphene', 'metamaterial', 'nanomaterial', 'carbon nanotube',
            'superconductor', '2d material', 'quantum dot', 'photonic crystal',
            'smart material', 'biomaterial', 'composite material', 'perovskite',
            'topological insulator', 'van der waals'
        ]
    },
    'Energy': {
        'categories': [
            'physics.app-ph', 'cond-mat.mtrl-sci', 'physics.chem-ph',
            'nucl-th', 'nucl-ex', 'physics.plasm-ph'
        ],
        'keywords': [
            # Fusion & nuclear energy
            'fusion energy', 'nuclear fusion', 'tokamak', 'iter', 'stellarator',
            'nuclear reactor', 'nuclear energy', 'fission', 'thorium reactor',
            # Solar & photovoltaic
            'solar cell', 'photovoltaic', 'perovskite solar', 'thin film solar',
            'solar panel', 'solar energy',
            # Battery & energy storage
            'battery technology', 'energy storage', 'lithium ion', 'solid state battery',
            'redox flow battery', 'grid storage', 'supercapacitor', 'electrochemical',
            # Fuel cells & hydrogen
            'hydrogen fuel', 'fuel cell', 'electrolysis', 'hydrogen storage',
            'proton exchange membrane',
            # Renewable & carbon capture
            'renewable energy', 'carbon capture', 'carbon sequestration', 'wind energy',
            'hydroelectric', 'geothermal', 'biofuel', 'energy efficiency'
        ]
    }
}

def create_comprehensive_tables(conn):
    """Create tables for deep arXiv analysis"""

    # Main papers table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS kaggle_arxiv_papers (
        arxiv_id TEXT PRIMARY KEY,
        title TEXT,
        authors TEXT,
        author_count INTEGER,
        categories TEXT,
        primary_category TEXT,
        abstract TEXT,
        doi TEXT,
        report_number TEXT,
        journal_ref TEXT,
        comments TEXT,
        versions_count INTEGER,
        update_date TEXT,
        first_submission_date TEXT,
        submission_year INTEGER,
        submission_month INTEGER,
        technology_domains TEXT,
        technology_scores TEXT,
        processing_date TEXT
    )
    """)

    # Parsed authors table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS kaggle_arxiv_authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arxiv_id TEXT,
        author_name TEXT,
        author_order INTEGER,
        inferred_affiliation TEXT,
        inferred_country TEXT,
        FOREIGN KEY (arxiv_id) REFERENCES kaggle_arxiv_papers(arxiv_id)
    )
    """)

    # Categories mapping
    conn.execute("""
    CREATE TABLE IF NOT EXISTS kaggle_arxiv_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arxiv_id TEXT,
        category TEXT,
        is_primary BOOLEAN,
        FOREIGN KEY (arxiv_id) REFERENCES kaggle_arxiv_papers(arxiv_id)
    )
    """)

    # Technology classification
    conn.execute("""
    CREATE TABLE IF NOT EXISTS kaggle_arxiv_technology (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arxiv_id TEXT,
        technology_domain TEXT,
        match_score REAL,
        match_type TEXT,
        FOREIGN KEY (arxiv_id) REFERENCES kaggle_arxiv_papers(arxiv_id)
    )
    """)

    # Statistics per technology per year
    conn.execute("""
    CREATE TABLE IF NOT EXISTS kaggle_arxiv_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        technology_domain TEXT,
        year INTEGER,
        month INTEGER,
        paper_count INTEGER,
        total_authors INTEGER,
        avg_authors_per_paper REAL,
        top_categories TEXT,
        collection_date TEXT,
        UNIQUE(technology_domain, year, month)
    )
    """)

    # Author collaboration network
    conn.execute("""
    CREATE TABLE IF NOT EXISTS kaggle_arxiv_collaborations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author1 TEXT,
        author2 TEXT,
        collaboration_count INTEGER,
        technology_domains TEXT,
        papers TEXT,
        UNIQUE(author1, author2)
    )
    """)

    # Keyword extraction
    conn.execute("""
    CREATE TABLE IF NOT EXISTS kaggle_arxiv_keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arxiv_id TEXT,
        keyword TEXT,
        source TEXT,
        FOREIGN KEY (arxiv_id) REFERENCES kaggle_arxiv_papers(arxiv_id)
    )
    """)

    # Processing metadata
    conn.execute("""
    CREATE TABLE IF NOT EXISTS kaggle_arxiv_processing_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        processing_date TEXT,
        total_papers_processed INTEGER,
        papers_per_technology TEXT,
        processing_time_seconds REAL,
        data_source TEXT,
        notes TEXT
    )
    """)

    conn.commit()
    print("[OK] Comprehensive tables created")

def infer_affiliation_country(author_name, abstract='', comments=''):
    """
    Infer country/affiliation from author name and context
    Limited without full metadata, but can extract from comments/abstract
    """
    # Common university/institution patterns
    institution_patterns = {
        'MIT': 'USA',
        'Stanford': 'USA',
        'Harvard': 'USA',
        'Berkeley': 'USA',
        'Caltech': 'USA',
        'CMU': 'USA',
        'ETH': 'Switzerland',
        'Cambridge': 'UK',
        'Oxford': 'UK',
        'Tsinghua': 'China',
        'Peking University': 'China',
        'USTC': 'China',
        'CAS': 'China',
        'CNRS': 'France',
        'MPG': 'Germany',
        'Max Planck': 'Germany',
        'RIKEN': 'Japan',
        'University of Tokyo': 'Japan'
    }

    combined_text = f"{author_name} {abstract} {comments}".lower()

    for inst, country in institution_patterns.items():
        if inst.lower() in combined_text:
            return inst, country

    return None, None

def classify_technology(paper, tech_keywords):
    """
    Classify paper into technology domains based on categories and keywords
    Returns dict of {tech_domain: score}
    """
    scores = defaultdict(float)

    title = paper.get('title', '').lower()
    abstract = paper.get('abstract', '').lower()
    categories = paper.get('categories', '').split()

    combined_text = f"{title} {abstract}"

    for tech_name, tech_config in tech_keywords.items():
        score = 0.0

        # Category match (high weight)
        for category in categories:
            if category in tech_config['categories']:
                score += 5.0

        # Keyword match (medium weight)
        for keyword in tech_config['keywords']:
            if keyword in combined_text:
                score += 1.0

        if score > 0:
            scores[tech_name] = score

    return scores

def parse_authors(authors_str):
    """Parse author string into list"""
    # arXiv author format varies, try to split intelligently
    authors = []

    if not authors_str:
        return authors

    # Common separators: ', and', ' and ', ','
    author_list = re.split(r',\s*and\s+|,\s+|\s+and\s+', authors_str)

    for author in author_list:
        author = author.strip()
        if author and len(author) > 2:  # Filter out initials only
            authors.append(author)

    return authors

def process_kaggle_arxiv_comprehensive():
    """
    Main processing function - deep dive on Kaggle arXiv dataset
    Extracts ALL available metadata for technology analysis
    """

    print("=" * 80)
    print("KAGGLE ARXIV COMPREHENSIVE DEEP DIVE PROCESSOR")
    print("=" * 80)
    print()

    if not KAGGLE_DATA.exists():
        print(f"[ERROR] Kaggle data not found: {KAGGLE_DATA}")
        return

    print(f"Data file: {KAGGLE_DATA}")
    print(f"Size: {KAGGLE_DATA.stat().st_size / (1024**3):.2f} GB")
    print()

    # Create processing database
    PROCESSING_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(PROCESSING_DB))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    create_comprehensive_tables(conn)

    # Processing statistics
    start_time = time.time()
    total_papers = 0
    papers_by_tech = defaultdict(int)
    authors_by_tech = defaultdict(set)
    categories_by_tech = defaultdict(Counter)
    yearly_counts = defaultdict(lambda: defaultdict(int))

    print(f"Technologies to process: {len(TECHNOLOGY_KEYWORDS)}")
    for tech in TECHNOLOGY_KEYWORDS:
        print(f"  - {tech}")
    print()

    print("Processing papers from Kaggle dataset...")
    print("(This will take 20-40 minutes for 2.3M papers)")
    print()

    batch_size = 10000
    batch_papers = []
    batch_authors = []
    batch_categories = []
    batch_tech = []

    with open(KAGGLE_DATA, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line_num % 10000 == 0:
                print(f"Processing line {line_num:,}...", end='\r')

            try:
                paper = json.loads(line)
                total_papers += 1

                # Extract fields
                arxiv_id = paper.get('id', '')
                title = paper.get('title', '').replace('\n', ' ').strip()
                authors_str = paper.get('authors', '')
                categories = paper.get('categories', '')
                abstract = paper.get('abstract', '').replace('\n', ' ').strip()
                doi = paper.get('doi', '')
                report_num = paper.get('report-no', '')
                journal_ref = paper.get('journal-ref', '')
                comments = paper.get('comments', '')
                update_date = paper.get('update_date', '')
                versions = paper.get('versions', [])

                # Parse submission date from versions
                submission_date = None
                submission_year = None
                submission_month = None

                if versions:
                    first_version = versions[0]
                    created = first_version.get('created', '')
                    if created:
                        try:
                            # Format: 'Mon, 2 Apr 2007 19:18:42 GMT'
                            date_obj = datetime.strptime(created, '%a, %d %b %Y %H:%M:%S %Z')
                            submission_date = date_obj.isoformat()
                            submission_year = date_obj.year
                            submission_month = date_obj.month
                        except:
                            pass

                # Parse authors
                authors = parse_authors(authors_str)
                author_count = len(authors)

                # Classify technology
                tech_scores = classify_technology(paper, TECHNOLOGY_KEYWORDS)

                if not tech_scores:
                    continue  # Skip papers not matching any technology

                # Primary technology (highest score)
                primary_tech = max(tech_scores.items(), key=lambda x: x[1])[0]

                # Categories
                category_list = categories.split()
                primary_category = category_list[0] if category_list else None

                # Update statistics
                for tech in tech_scores.keys():
                    papers_by_tech[tech] += 1
                    authors_by_tech[tech].update(authors)
                    for cat in category_list:
                        categories_by_tech[tech][cat] += 1
                    if submission_year:
                        yearly_counts[tech][submission_year] += 1

                # Prepare batch inserts
                batch_papers.append((
                    arxiv_id, title, authors_str, author_count,
                    categories, primary_category, abstract[:2000],  # Limit abstract
                    doi, report_num, journal_ref, comments[:500],
                    len(versions), update_date, submission_date,
                    submission_year, submission_month,
                    ','.join(tech_scores.keys()),
                    json.dumps(tech_scores),
                    datetime.now().isoformat()
                ))

                # Authors
                for idx, author in enumerate(authors):
                    affiliation, country = infer_affiliation_country(author, abstract, comments)
                    batch_authors.append((arxiv_id, author, idx, affiliation, country))

                # Categories
                for idx, cat in enumerate(category_list):
                    batch_categories.append((arxiv_id, cat, idx == 0))

                # Technology classification
                for tech, score in tech_scores.items():
                    match_type = 'category' if any(cat in TECHNOLOGY_KEYWORDS[tech]['categories'] for cat in category_list) else 'keyword'
                    batch_tech.append((arxiv_id, tech, score, match_type))

                # Batch insert
                if len(batch_papers) >= batch_size:
                    conn.executemany("""
                        INSERT OR IGNORE INTO kaggle_arxiv_papers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, batch_papers)

                    conn.executemany("""
                        INSERT INTO kaggle_arxiv_authors (arxiv_id, author_name, author_order, inferred_affiliation, inferred_country)
                        VALUES (?,?,?,?,?)
                    """, batch_authors)

                    conn.executemany("""
                        INSERT INTO kaggle_arxiv_categories (arxiv_id, category, is_primary)
                        VALUES (?,?,?)
                    """, batch_categories)

                    conn.executemany("""
                        INSERT INTO kaggle_arxiv_technology (arxiv_id, technology_domain, match_score, match_type)
                        VALUES (?,?,?,?)
                    """, batch_tech)

                    conn.commit()

                    batch_papers = []
                    batch_authors = []
                    batch_categories = []
                    batch_tech = []

            except json.JSONDecodeError:
                continue
            except Exception as e:
                if line_num % 10000 == 0:
                    print(f"  [WARN] Error at line {line_num}: {e}")
                continue

    # Insert remaining batch
    if batch_papers:
        conn.executemany("INSERT OR IGNORE INTO kaggle_arxiv_papers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", batch_papers)
        conn.executemany("INSERT INTO kaggle_arxiv_authors (arxiv_id, author_name, author_order, inferred_affiliation, inferred_country) VALUES (?,?,?,?,?)", batch_authors)
        conn.executemany("INSERT INTO kaggle_arxiv_categories (arxiv_id, category, is_primary) VALUES (?,?,?)", batch_categories)
        conn.executemany("INSERT INTO kaggle_arxiv_technology (arxiv_id, technology_domain, match_score, match_type) VALUES (?,?,?,?)", batch_tech)
        conn.commit()

    processing_time = time.time() - start_time

    print(f"\n\n{'=' * 80}")
    print("PROCESSING COMPLETE")
    print(f"{'=' * 80}")
    print(f"Total papers processed: {total_papers:,}")
    print(f"Processing time: {processing_time:.1f} seconds ({processing_time/60:.1f} minutes)")
    print()

    # Generate statistics
    print("Papers per technology:")
    for tech in sorted(papers_by_tech.keys()):
        print(f"  {tech}: {papers_by_tech[tech]:,}")

    print(f"\nUnique authors per technology:")
    for tech in sorted(authors_by_tech.keys()):
        print(f"  {tech}: {len(authors_by_tech[tech]):,}")

    # Insert statistics
    for tech, year_counts in yearly_counts.items():
        for year, count in year_counts.items():
            conn.execute("""
                INSERT OR REPLACE INTO kaggle_arxiv_stats (
                    technology_domain, year, month, paper_count,
                    collection_date
                ) VALUES (?, ?, ?, ?, ?)
            """, (tech, year, None, count, datetime.now().isoformat()))

    # Log processing
    conn.execute("""
        INSERT INTO kaggle_arxiv_processing_log (
            processing_date, total_papers_processed,
            papers_per_technology, processing_time_seconds,
            data_source, notes
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        total_papers,
        json.dumps(papers_by_tech),
        processing_time,
        'Kaggle arXiv Snapshot (2.3M papers)',
        'Comprehensive deep dive - all metadata extracted'
    ))

    conn.commit()

    # Database statistics
    print(f"\n{'=' * 80}")
    print("DATABASE STATISTICS")
    print(f"{'=' * 80}")

    papers_count = conn.execute("SELECT COUNT(*) FROM kaggle_arxiv_papers").fetchone()[0]
    authors_count = conn.execute("SELECT COUNT(*) FROM kaggle_arxiv_authors").fetchone()[0]
    categories_count = conn.execute("SELECT COUNT(DISTINCT category) FROM kaggle_arxiv_categories").fetchone()[0]

    print(f"\nRecords in database:")
    print(f"  Papers: {papers_count:,}")
    print(f"  Author records: {authors_count:,}")
    print(f"  Unique categories: {categories_count}")

    print(f"\nDatabase saved to: {PROCESSING_DB}")
    print(f"Database size: {PROCESSING_DB.stat().st_size / (1024**2):.1f} MB")

    conn.close()

    print(f"\n{'=' * 80}")
    print("[OK] DEEP DIVE COMPLETE")
    print(f"{'=' * 80}")
    print()

if __name__ == '__main__':
    process_kaggle_arxiv_comprehensive()
