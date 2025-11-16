#!/usr/bin/env python3
"""
Update Performance Documentation with Corrected Claims
Fixes overstated performance claims based on actual benchmark results
"""

from pathlib import Path
import re

# Files to update
FILES_TO_UPDATE = [
    "analysis/PERFORMANCE_OPTIMIZATION_COMPLETE.md",
    "analysis/PERFORMANCE_OPTIMIZATION_PROGRESS.md",
    "analysis/INDEX_CREATION_FINAL_REPORT.md"
]

# Replacement patterns
REPLACEMENTS = [
    # Overall speedup claims
    (r'\*\*100-500x faster\*\*', '**5-30x faster** (verified)'),
    (r'\*\*100-1000x\*\*', '**5-30x**'),
    (r'100-1000x faster', '5-30x faster'),
    (r'100-500x faster', '5-30x faster'),

    # Specific timing claims - GLEIF
    (r'120\.69ms', '8,741ms (cold cache)'),
    (r'120ms', '8,741ms (cold cache)'),

    # USPTO
    (r'1\.99ms', '12,443ms (cold cache)'),
    (r'2ms', '12,443ms (cold cache)'),

    # arXiv
    (r'95\.56ms', '547ms (cold cache)'),
    (r'95ms', '547ms (cold cache)'),

    # Specific improvement claims
    (r'20-1000x', '5-10x'),
    (r'400-500x faster', '5-10x faster (name searches need FTS)'),
    (r'50-100x faster', '20-30x faster'),
    (r'\*\*20x faster\*\*', '**5-7x faster**'),
    (r'\*\*1000x faster\*\*', '**5-10x faster**'),
    (r'\*\*20-40x faster\*\*', '**3-5x faster**'),

    # Performance ratings
    (r'EXCELLENT \(SSD\)', 'GOOD (cold cache)'),
]

def update_file(filepath):
    """Update a single file with corrected performance claims"""
    path = Path(filepath)

    if not path.exists():
        print(f"SKIP: {filepath} (not found)")
        return

    print(f"\nUpdating: {filepath}")

    # Read content
    content = path.read_text(encoding='utf-8')
    original_content = content

    # Apply replacements
    changes = 0
    for pattern, replacement in REPLACEMENTS:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            matches = len(re.findall(pattern, content))
            print(f"  - Replaced '{pattern}' ({matches} occurrences)")
            changes += matches
            content = new_content

    # Write back if changed
    if content != original_content:
        path.write_text(content, encoding='utf-8')
        print(f"  [SAVE] {changes} total changes made")
    else:
        print(f"  [SKIP] No changes needed")

def add_disclaimer_section(filepath):
    """Add performance disclaimer to file"""
    path = Path(filepath)

    if not path.exists():
        return

    content = path.read_text(encoding='utf-8')

    # Check if disclaimer already exists
    if 'Performance Note' in content or 'Cold Cache' in content:
        return

    # Add disclaimer after first heading
    disclaimer = """
## ⚠️ Performance Note

**Important:** All performance measurements are first-run (cold cache) results on a 94GB database.
Warm cache performance (subsequent queries) is significantly better:
- **Cold cache** (first run): 500ms - 12s
- **Warm cache** (subsequent runs): 50ms - 2s (estimated)
- **Hot cache** (fully cached): 10ms - 500ms (estimated)

**LIKE queries** with text prefix patterns (e.g., `legal_name LIKE 'CHINA%'`) do not benefit from B-tree indices.
Full-Text Search (FTS) implementation recommended for 100x+ improvement on name searches.

---
"""

    # Insert after first heading (after "# ")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# ') and i > 0:
            lines.insert(i+1, disclaimer)
            break

    new_content = '\n'.join(lines)

    if new_content != content:
        path.write_text(new_content, encoding='utf-8')
        print(f"\n[ADDED] Performance disclaimer to {filepath}")

def main():
    print("=" * 80)
    print("UPDATING PERFORMANCE DOCUMENTATION")
    print("=" * 80)
    print("\nCorrecting overstated performance claims with actual benchmark results...")
    print("")

    # Update all files
    for filepath in FILES_TO_UPDATE:
        update_file(filepath)
        add_disclaimer_section(filepath)

    print("\n" + "=" * 80)
    print("DOCUMENTATION UPDATE COMPLETE")
    print("=" * 80)
    print("\nSummary:")
    print("  - Performance claims updated from '100-1000x' to '5-30x'")
    print("  - Timing data updated with actual benchmark results")
    print("  - Performance disclaimers added")
    print("  - Cold cache vs warm cache distinction added")
    print("\nFiles updated:")
    for filepath in FILES_TO_UPDATE:
        if Path(filepath).exists():
            print(f"  - {filepath}")

    print("\nNext steps:")
    print("  1. Run warm cache benchmark tests")
    print("  2. Implement FTS for name searches")
    print("  3. Add composite indices for multi-filter queries")

if __name__ == '__main__':
    main()
