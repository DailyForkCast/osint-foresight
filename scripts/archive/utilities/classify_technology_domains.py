#!/usr/bin/env python3
"""
Technology Domain Classification for OpenAlex Entities
Maps institutions to strategic technology domains based on their research output
"""

import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=120.0)
cur = conn.cursor()

print("="*80)
print("TECHNOLOGY DOMAIN CLASSIFICATION")
print("="*80)

# Define strategic technology domain mapping
# Based on ASPI Critical Technology Tracker categories
DOMAIN_MAPPINGS = {
    'Quantum Computing': [
        'Quantum', 'quantum', 'Qubit', 'qubit', 'Superconducting', 'superconducting',
        'Quantum Information', 'Quantum Cryptography', 'Quantum Dots', 'quantum dots',
        'Quantum Mechanics', 'Topological Quantum'
    ],

    'Artificial Intelligence': [
        'Neural Networks', 'neural networks', 'Machine Learning', 'machine learning',
        'Deep Learning', 'deep learning', 'Computer Vision', 'computer vision',
        'Natural Language Processing', 'NLP', 'Reinforcement Learning',
        'Pattern Recognition', 'Image Recognition'
    ],

    'Semiconductors': [
        'Semiconductor', 'semiconductor', 'Transistor', 'transistor', 'CMOS',
        'Integrated Circuits', 'integrated circuits', 'Chip', 'Microprocessor',
        'VLSI', 'Nanofabrication', 'Wafer', 'Silicon'
    ],

    'Telecommunications': [
        '5G', '6G', 'Wireless', 'wireless', 'Network', 'Communications',
        'Antenna', 'antenna', 'RF', 'Radio Frequency', 'Mobile', 'Cellular',
        'Satellite Communication', 'Optical Communication'
    ],

    'Aerospace': [
        'Aerospace', 'aerospace', 'Aircraft', 'aircraft', 'UAV', 'Drone', 'drone',
        'Satellite', 'satellite', 'Space', 'Orbital', 'Rocket', 'Hypersonic',
        'Aerodynamics', 'Flight Control'
    ],

    'Biotechnology': [
        'CRISPR', 'Gene Editing', 'gene editing', 'Synthetic Biology', 'Genomics',
        'Bioinformatics', 'Protein Engineering', 'Genetic Engineering',
        'Bioengineering', 'Molecular Biology', 'DNA Sequencing'
    ],

    'Advanced Materials': [
        'Graphene', 'graphene', 'Carbon Nanotube', 'carbon nanotube', 'Metamaterial',
        'metamaterial', 'Nanocomposite', 'Nanomaterial', 'nanomaterial',
        'Superconductor', 'Smart Materials', 'Advanced Composite'
    ],

    'Cybersecurity': [
        'Cybersecurity', 'cybersecurity', 'Cryptography', 'cryptography',
        'Encryption', 'encryption', 'Network Security', 'Information Security',
        'Malware', 'Intrusion Detection', 'Blockchain'
    ],

    'Energy Storage': [
        'Battery', 'battery', 'Lithium-ion', 'lithium-ion', 'Energy Storage',
        'energy storage', 'Supercapacitor', 'Fuel Cell', 'fuel cell',
        'Solar Cell', 'solar cell', 'Photovoltaic'
    ],

    'Robotics & Autonomous Systems': [
        'Robot', 'robot', 'Robotics', 'robotics', 'Autonomous', 'autonomous',
        'Self-driving', 'Unmanned', 'Control Systems', 'Sensor Fusion',
        'Path Planning'
    ],

    'Nuclear Technology': [
        'Nuclear', 'nuclear', 'Reactor', 'reactor', 'Fusion', 'fusion',
        'Fission', 'Radioactive', 'Radiation', 'Plutonium', 'Uranium'
    ],

    'Hypersonics': [
        'Hypersonic', 'hypersonic', 'Supersonic', 'Mach', 'Scramjet',
        'High-speed flight'
    ]
}

print("\n1. Mapping topics to strategic domains...")
print("-"*80)

# Get all unique topics
cur.execute('SELECT DISTINCT topic_name FROM openalex_work_topics')
all_topics = [row[0] for row in cur.fetchall()]
print(f"Total unique topics: {len(all_topics)}")

# Map topics to domains
topic_to_domain = {}
domain_topic_count = defaultdict(int)

for topic in all_topics:
    topic_lower = topic.lower()
    for domain, keywords in DOMAIN_MAPPINGS.items():
        for keyword in keywords:
            if keyword.lower() in topic_lower:
                topic_to_domain[topic] = domain
                domain_topic_count[domain] += 1
                break
        if topic in topic_to_domain:
            break

print(f"Topics mapped to strategic domains: {len(topic_to_domain)}")
print("\nTopics per domain:")
for domain, count in sorted(domain_topic_count.items(), key=lambda x: x[1], reverse=True):
    print(f"  {domain:40} {count:4} topics")

# 2. Add technology_domain column if it doesn't exist
print("\n2. Adding technology_domain column to openalex_entities...")
print("-"*80)

try:
    cur.execute('ALTER TABLE openalex_entities ADD COLUMN technology_domain TEXT')
    conn.commit()
    print("  Column added successfully")
except sqlite3.OperationalError as e:
    if 'duplicate column' in str(e).lower():
        print("  Column already exists, continuing...")
    else:
        raise

# 3. Classify institutions based on their research output
print("\n3. Classifying institutions by dominant research domain...")
print("-"*80)

# Get institution research profiles
print("  Analyzing research portfolios...")

institution_domains = defaultdict(lambda: defaultdict(int))

# For each work with topics and institution affiliation
cur.execute('''
    SELECT DISTINCT
        wa.institution_id,
        wa.institution_name,
        wt.topic_name,
        wt.score
    FROM openalex_work_authors wa
    JOIN openalex_work_topics wt ON wa.work_id = wt.work_id
    WHERE wa.institution_id IS NOT NULL
      AND wa.institution_name IS NOT NULL
      AND wt.topic_name IS NOT NULL
''')

processed = 0
for inst_id, inst_name, topic, score in cur:
    if topic in topic_to_domain:
        domain = topic_to_domain[topic]
        # Weight by topic score
        institution_domains[inst_id][domain] += score

    processed += 1
    if processed % 10000 == 0:
        print(f"  Processed {processed:,} work-topic-institution relationships...")

print(f"  Total relationships processed: {processed:,}")
print(f"  Institutions with domain classifications: {len(institution_domains):,}")

# 4. Assign primary domain to each institution
print("\n4. Assigning primary technology domains to institutions...")
print("-"*80)

updates = 0
multi_domain = 0

for inst_id, domains in institution_domains.items():
    if not domains:
        continue

    # Get primary domain (highest aggregate score)
    primary_domain = max(domains.items(), key=lambda x: x[1])[0]

    # Check if multi-domain (2+ domains with >30% of primary)
    primary_score = domains[primary_domain]
    significant_domains = [d for d, s in domains.items() if s > primary_score * 0.3]

    if len(significant_domains) > 1:
        domain_str = f"{primary_domain} (+" + ", ".join([d for d in significant_domains if d != primary_domain]) + ")"
        multi_domain += 1
    else:
        domain_str = primary_domain

    # Update entity
    cur.execute('''
        UPDATE openalex_entities
        SET technology_domain = ?
        WHERE entity_id = ?
    ''', (domain_str, inst_id))

    updates += 1
    if updates % 100 == 0:
        print(f"  Updated {updates:,} institutions...")

conn.commit()

print(f"  Total institutions updated: {updates:,}")
print(f"  Multi-domain institutions: {multi_domain:,}")

# 5. Verification and Statistics
print("\n" + "="*80)
print("CLASSIFICATION RESULTS")
print("="*80)

cur.execute('SELECT COUNT(*) FROM openalex_entities')
total_entities = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM openalex_entities WHERE technology_domain IS NOT NULL')
classified = cur.fetchone()[0]

print(f"\nTotal entities: {total_entities:,}")
print(f"Classified: {classified:,} ({100*classified/total_entities:.1f}%)")
print(f"Unclassified: {total_entities - classified:,} ({100*(total_entities-classified)/total_entities:.1f}%)")

# Domain distribution
cur.execute('''
    SELECT
        CASE
            WHEN technology_domain LIKE '%+%' THEN SUBSTR(technology_domain, 1, INSTR(technology_domain, ' (') - 1)
            ELSE technology_domain
        END as primary_domain,
        COUNT(*) as count
    FROM openalex_entities
    WHERE technology_domain IS NOT NULL
    GROUP BY primary_domain
    ORDER BY count DESC
''')

print("\nPrimary domain distribution:")
for domain, count in cur.fetchall():
    print(f"  {count:4,} institutions: {domain}")

# Sample classified institutions
print("\n" + "="*80)
print("SAMPLE CLASSIFIED INSTITUTIONS")
print("="*80)

cur.execute('''
    SELECT name, country_code, technology_domain, works_count
    FROM openalex_entities
    WHERE technology_domain IS NOT NULL
    ORDER BY works_count DESC
    LIMIT 20
''')

print("\nTop 20 institutions by research output:")
for name, country, domain, works in cur.fetchall():
    country_str = country if country else "??"
    print(f"  [{country_str}] {name[:50]:50} | {domain[:40]:40} | {works:4} works")

# Strategic technology institutions
print("\n" + "="*80)
print("STRATEGIC TECHNOLOGY INSTITUTIONS")
print("="*80)

for tech in ['Quantum Computing', 'Artificial Intelligence', 'Semiconductors', 'Hypersonics']:
    cur.execute('''
        SELECT name, country_code, works_count
        FROM openalex_entities
        WHERE technology_domain LIKE ?
        ORDER BY works_count DESC
        LIMIT 5
    ''', (f'%{tech}%',))

    print(f"\nTop {tech} institutions:")
    for name, country, works in cur.fetchall():
        country_str = country if country else "??"
        print(f"  [{country_str}] {name[:60]:60} ({works} works)")

conn.close()

print("\n" + "="*80)
print("[SUCCESS] Technology domain classification complete!")
print("="*80)
