"""
Analyze OpenAlex Topic Taxonomy Structure

Purpose: Understand how OpenAlex classifies works by topic so we can use
         this metadata to filter out false positives.

Goal: Document topic patterns for:
      - True semiconductor papers
      - Quantum papers
      - Biology papers (false positives)
      - Other technology domains
"""

import gzip
import json
from pathlib import Path
from collections import Counter, defaultdict

# OpenAlex data location
OPENALEX_DATA = Path("F:/OSINT_Backups/openalex/data/works")

def analyze_topics():
    """Analyze OpenAlex topic structure from raw data"""

    print("="*80)
    print("OPENALEX TOPIC TAXONOMY ANALYSIS")
    print("="*80)
    print("\nAnalyzing first data file for topic structure...")

    # Pick a sample file
    sample_file = OPENALEX_DATA / "updated_date=2024-12-02/part_000.gz"

    if not sample_file.exists():
        print(f"ERROR: Sample file not found: {sample_file}")
        return

    # Collect samples by keyword category
    semiconductor_samples = []
    quantum_samples = []
    biology_samples = []
    ai_samples = []

    # Topic distribution counters
    all_topics = Counter()
    semiconductor_topics = Counter()
    quantum_topics = Counter()
    biology_topics = Counter()

    print(f"Reading: {sample_file.name}")
    print("Sampling first 50,000 works...\n")

    with gzip.open(sample_file, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 50000:  # Sample first 50K works
                break

            if i > 0 and i % 10000 == 0:
                print(f"  Processed {i:,} works...")

            try:
                work = json.loads(line)
                title = work.get('title', '').lower()
                topics = work.get('topics', [])

                # Collect topic names
                for topic in topics:
                    topic_name = topic.get('display_name', 'Unknown')
                    all_topics[topic_name] += 1

                # Find true semiconductor papers
                if any(kw in title for kw in ['semiconductor', 'transistor', 'mosfet', 'integrated circuit', 'cmos']):
                    if len(semiconductor_samples) < 10:
                        semiconductor_samples.append(work)
                    for topic in topics:
                        semiconductor_topics[topic.get('display_name', 'Unknown')] += 1

                # Quantum papers
                elif any(kw in title for kw in ['quantum', 'qubit', 'entanglement', 'quantum computing']):
                    if len(quantum_samples) < 10:
                        quantum_samples.append(work)
                    for topic in topics:
                        quantum_topics[topic.get('display_name', 'Unknown')] += 1

                # Biology papers (potential false positives)
                elif any(kw in title for kw in ['protein', 'gene', 'bacterial', 'cell', 'dna', 'enzyme']):
                    if len(biology_samples) < 10:
                        biology_samples.append(work)
                    for topic in topics:
                        biology_topics[topic.get('display_name', 'Unknown')] += 1

                # AI/ML papers
                elif any(kw in title for kw in ['machine learning', 'deep learning', 'neural network', 'artificial intelligence']):
                    if len(ai_samples) < 10:
                        ai_samples.append(work)

            except Exception as e:
                continue

    print(f"\n{'='*80}")
    print("SEMICONDUCTOR PAPER SAMPLES (true positives)")
    print('='*80)

    for i, work in enumerate(semiconductor_samples, 1):
        title = work.get('title', 'N/A')
        print(f"\n{i}. {title[:90]}")

        topics = work.get('topics', [])
        if topics:
            print("   TOPICS:")
            for topic in topics[:3]:  # Top 3 topics
                name = topic.get('display_name', 'N/A')
                score = topic.get('score', 0)
                print(f"     - {name} (score: {score:.3f})")
        else:
            print("   TOPICS: None")

        source = work.get('primary_location', {}).get('source', {})
        source_name = source.get('display_name', 'N/A')
        print(f"   SOURCE: {source_name}")
        print(f"   TYPE: {work.get('type', 'N/A')}")

    print(f"\n{'='*80}")
    print("QUANTUM PAPER SAMPLES")
    print('='*80)

    for i, work in enumerate(quantum_samples, 1):
        title = work.get('title', 'N/A')
        print(f"\n{i}. {title[:90]}")

        topics = work.get('topics', [])
        if topics:
            print("   TOPICS:")
            for topic in topics[:3]:
                name = topic.get('display_name', 'N/A')
                score = topic.get('score', 0)
                print(f"     - {name} (score: {score:.3f})")
        else:
            print("   TOPICS: None")

        source = work.get('primary_location', {}).get('source', {})
        source_name = source.get('display_name', 'N/A')
        print(f"   SOURCE: {source_name}")

    print(f"\n{'='*80}")
    print("BIOLOGY PAPER SAMPLES (potential false positives)")
    print('='*80)

    for i, work in enumerate(biology_samples, 1):
        title = work.get('title', 'N/A')
        print(f"\n{i}. {title[:90]}")

        topics = work.get('topics', [])
        if topics:
            print("   TOPICS:")
            for topic in topics[:3]:
                name = topic.get('display_name', 'N/A')
                score = topic.get('score', 0)
                print(f"     - {name} (score: {score:.3f})")
        else:
            print("   TOPICS: None")

        source = work.get('primary_location', {}).get('source', {})
        source_name = source.get('display_name', 'N/A')
        print(f"   SOURCE: {source_name}")

    # Analyze topic distributions
    print(f"\n{'='*80}")
    print("TOPIC DISTRIBUTION ANALYSIS")
    print('='*80)

    print(f"\nTop 20 topics in SEMICONDUCTOR papers:")
    for topic, count in semiconductor_topics.most_common(20):
        print(f"  {topic}: {count}")

    print(f"\nTop 20 topics in QUANTUM papers:")
    for topic, count in quantum_topics.most_common(20):
        print(f"  {topic}: {count}")

    print(f"\nTop 20 topics in BIOLOGY papers:")
    for topic, count in biology_topics.most_common(20):
        print(f"  {topic}: {count}")

    print(f"\nTop 30 most common topics overall (in 50K works):")
    for topic, count in all_topics.most_common(30):
        print(f"  {topic}: {count}")

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print('='*80)
    print(f"\nSamples collected:")
    print(f"  Semiconductor papers: {len(semiconductor_samples)}")
    print(f"  Quantum papers: {len(quantum_samples)}")
    print(f"  Biology papers: {len(biology_samples)}")
    print(f"  AI papers: {len(ai_samples)}")
    print(f"\nUnique topics found: {len(all_topics)}")

    # Save results
    results = {
        'semiconductor_topics': dict(semiconductor_topics.most_common(30)),
        'quantum_topics': dict(quantum_topics.most_common(30)),
        'biology_topics': dict(biology_topics.most_common(30)),
        'all_topics': dict(all_topics.most_common(50))
    }

    import json
    output_file = Path("analysis/openalex_topic_analysis.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    analyze_topics()
