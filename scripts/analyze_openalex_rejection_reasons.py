"""
Analyze OpenAlex V2 Rejection Patterns
Similar to USPTO NULL data handling methodology
"""
import sqlite3
import gzip
import json
from pathlib import Path
from collections import defaultdict
import re

MASTER_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OPENALEX_DATA = Path("F:/OSINT_Backups/openalex/data/works")

TECHNOLOGY_KEYWORDS = {
    'AI': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network'],
    'Quantum': ['quantum computing', 'quantum information', 'qubit'],
    'Semiconductors': ['semiconductor device', 'transistor', 'integrated circuit'],
}

RELEVANT_TOPICS = {
    'AI': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network'],
    'Quantum': ['quantum', 'qubit', 'quantum computing'],
    'Semiconductors': ['semiconductor', 'microelectronics', 'integrated circuit'],
}

EXCLUDED_SOURCE_PATTERNS = [
    r'.*\bbiolog', r'.*\bmedicine\b', r'.*\bmedical\b', r'.*\bclinical\b',
    r'.*\bagricult', r'.*\bgenomics?\b', r'.*\bchemistry\b', r'.*\becology\b'
]

def matches_keyword(text, keywords):
    """Check if text matches any keyword"""
    if not text:
        return False, None
    text_lower = text.lower()
    for keyword in keywords:
        if ' ' in keyword:
            if keyword.lower() in text_lower:
                return True, keyword
        else:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                return True, keyword
    return False, None

def analyze_rejection_category(work, tech_name, tech_keywords):
    """
    Categorize WHY a work was rejected
    Returns: (category, details)
    """
    title = work.get('title', '')
    abstract_inv = work.get('abstract_inverted_index', {})
    abstract = ' '.join(abstract_inv.keys()) if abstract_inv else ''
    combined_text = f"{title} {abstract}"

    # Check keyword match
    has_keyword, matched_keyword = matches_keyword(combined_text, tech_keywords)

    if not has_keyword:
        return 'NO_KEYWORD_MATCH', {'reason': 'Text does not contain target keywords'}

    # Keyword matched - now check topic rejection reasons
    topics = work.get('topics', [])

    # Category 1: No topic metadata
    if not topics:
        return 'NO_TOPIC_DATA', {
            'reason': 'Keyword matched but work has no topic metadata',
            'keyword': matched_keyword,
            'has_abstract': bool(abstract_inv)
        }

    # Category 2: Has topics but none are relevant
    topic_names = [t.get('display_name', '').lower() for t in topics]
    relevant_patterns = RELEVANT_TOPICS.get(tech_name, [])

    has_any_match = False
    for topic_name in topic_names:
        for pattern in relevant_patterns:
            if pattern.lower() in topic_name or topic_name in pattern.lower():
                has_any_match = True
                break
        if has_any_match:
            break

    if not has_any_match:
        # Check if topics are clearly NON-relevant (biology, medicine, etc.)
        has_negative_topic = False
        negative_topics = []
        for topic_name in topic_names:
            if any(re.search(pattern, topic_name) for pattern in EXCLUDED_SOURCE_PATTERNS):
                has_negative_topic = True
                negative_topics.append(topic_name)

        if has_negative_topic:
            return 'CONFIRMED_NON_RELEVANT', {
                'reason': 'Keyword matched but topics are clearly non-relevant (biology/medicine)',
                'keyword': matched_keyword,
                'topics': topic_names[:3],
                'negative_topics': negative_topics
            }
        else:
            return 'UNCERTAIN_TOPIC_MISMATCH', {
                'reason': 'Keyword matched, has topics, but no pattern match',
                'keyword': matched_keyword,
                'topics': topic_names[:3],
                'topic_count': len(topics)
            }

    # Has relevant topic - check other rejection reasons
    primary_location = work.get('primary_location', {})
    source = primary_location.get('source', {})
    source_name = source.get('display_name', '')

    # Check if source is excluded
    if source_name:
        for pattern in EXCLUDED_SOURCE_PATTERNS:
            if re.search(pattern, source_name.lower()):
                return 'EXCLUDED_SOURCE', {
                    'reason': 'Relevant topic but published in excluded journal',
                    'keyword': matched_keyword,
                    'source': source_name,
                    'topics': topic_names[:2]
                }

    # Check quality issues
    is_retracted = work.get('is_retracted', False)
    is_paratext = work.get('is_paratext', False)
    has_abstract = bool(abstract_inv)

    if not has_abstract:
        return 'NO_ABSTRACT', {
            'reason': 'Passed validation but lacks abstract',
            'keyword': matched_keyword,
            'topics': topic_names[:2]
        }

    if is_retracted:
        return 'RETRACTED', {
            'reason': 'Retracted publication',
            'keyword': matched_keyword
        }

    if is_paratext:
        return 'PARATEXT', {
            'reason': 'Paratext (not substantive research)',
            'keyword': matched_keyword
        }

    # Should have been accepted - this is unexpected
    return 'SHOULD_BE_ACCEPTED', {
        'reason': 'Appears to meet all criteria',
        'keyword': matched_keyword,
        'topics': topic_names[:2]
    }

def main():
    print("=" * 80)
    print("OPENALEX REJECTION PATTERN ANALYSIS")
    print("=" * 80)
    print()

    # Sample 100 files for analysis
    works_dir = OPENALEX_DATA
    date_dirs = sorted(works_dir.glob('updated_date=*'))

    # Sample from diverse directories
    step = max(1, len(date_dirs) // 20)
    work_files = []
    for i in range(0, len(date_dirs), step)[:20]:
        files_in_dir = sorted(date_dirs[i].glob('*.gz'))
        if files_in_dir:
            work_files.extend(files_in_dir[:5])

    work_files = work_files[:100]
    print(f"Analyzing {len(work_files)} files from {len(date_dirs)} date directories")
    print()

    rejection_stats = defaultdict(lambda: defaultdict(int))
    examples = defaultdict(list)

    files_analyzed = 0
    works_analyzed = 0

    for file_path in work_files[:20]:  # Analyze first 20 files for speed
        files_analyzed += 1

        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line_num, line in enumerate(f):
                    works_analyzed += 1

                    if works_analyzed % 5000 == 0:
                        print(f"Analyzed {works_analyzed:,} works...", end='\r')

                    try:
                        work = json.loads(line)

                        # Check each technology
                        for tech_name, keywords in TECHNOLOGY_KEYWORDS.items():
                            category, details = analyze_rejection_category(work, tech_name, keywords)
                            rejection_stats[tech_name][category] += 1

                            # Store examples
                            if len(examples[f"{tech_name}_{category}"]) < 3:
                                examples[f"{tech_name}_{category}"].append({
                                    'title': work.get('title', '')[:80],
                                    'details': details
                                })

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue

    print()
    print()
    print("=" * 80)
    print("REJECTION ANALYSIS RESULTS")
    print("=" * 80)
    print(f"Files analyzed: {files_analyzed}")
    print(f"Works analyzed: {works_analyzed:,}")
    print()

    for tech_name in TECHNOLOGY_KEYWORDS.keys():
        print(f"\n{tech_name}")
        print("-" * 80)

        stats = rejection_stats[tech_name]
        total = sum(stats.values())

        # Sort by count
        sorted_categories = sorted(stats.items(), key=lambda x: x[1], reverse=True)

        for category, count in sorted_categories:
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {category:30s}: {count:6,} ({pct:5.1f}%)")

        print(f"  {'TOTAL':30s}: {total:6,}")

    # Print examples
    print()
    print()
    print("=" * 80)
    print("EXAMPLE REJECTIONS BY CATEGORY")
    print("=" * 80)

    for tech_name in TECHNOLOGY_KEYWORDS.keys():
        print(f"\n{tech_name}")
        print("-" * 80)

        for category in ['NO_TOPIC_DATA', 'UNCERTAIN_TOPIC_MISMATCH', 'CONFIRMED_NON_RELEVANT']:
            key = f"{tech_name}_{category}"
            if key in examples and examples[key]:
                print(f"\n  {category}:")
                for i, ex in enumerate(examples[key][:2], 1):
                    print(f"    Example {i}: {ex['title']}")
                    print(f"      Reason: {ex['details'].get('reason', 'N/A')}")
                    if 'topics' in ex['details']:
                        print(f"      Topics: {', '.join(ex['details']['topics'])}")
                    print()

    # Summary recommendations
    print()
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    print("1. HIGH PRIORITY - Review 'UNCERTAIN_TOPIC_MISMATCH' category:")
    print("   These have keywords AND topics, but topics don't match our patterns")
    print("   → May need to expand RELEVANT_TOPICS lists")
    print()

    print("2. MEDIUM PRIORITY - Review 'NO_TOPIC_DATA' category:")
    print("   These have keywords but no topic metadata")
    print("   → Data limitation, not validation issue")
    print()

    print("3. LOW PRIORITY - 'CONFIRMED_NON_RELEVANT' are correctly excluded")
    print("   These have biology/medicine topics")
    print()

if __name__ == '__main__':
    main()
