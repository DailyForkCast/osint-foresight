#!/usr/bin/env python3
"""Generate comprehensive script inventory"""

import os
from pathlib import Path
from collections import defaultdict

print('SCRIPT INVENTORY - OSINT Foresight Project')
print('='*70)
print()

# Find all Python scripts
scripts_by_category = defaultdict(list)
total_scripts = 0

for root, dirs, files in os.walk('scripts/'):
    # Skip __pycache__ and .git
    if '__pycache__' in root or '.git' in root:
        continue

    for file in files:
        if file.endswith('.py') and file != '__init__.py':
            full_path = Path(root) / file
            category = str(Path(root).relative_to('scripts'))
            if category == '.':
                category = 'root'

            scripts_by_category[category].append(file)
            total_scripts += 1

# Print organized inventory
for category in sorted(scripts_by_category.keys()):
    count = len(scripts_by_category[category])
    print(f'\n{category}/ ({count} scripts)')
    print('-' * 70)
    for script in sorted(scripts_by_category[category]):
        print(f'  - {script}')

print()
print('='*70)
print(f'TOTAL: {total_scripts} operational Python scripts')
print(f'CATEGORIES: {len(scripts_by_category)}')
print('='*70)

# Save to file
output_file = 'SCRIPT_INVENTORY_20251018.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('# Script Inventory - OSINT Foresight Project\n')
    f.write('**Generated**: October 18, 2025\n\n')
    f.write(f'**Total Scripts**: {total_scripts}\n')
    f.write(f'**Categories**: {len(scripts_by_category)}\n\n')
    f.write('---\n\n')

    for category in sorted(scripts_by_category.keys()):
        count = len(scripts_by_category[category])
        f.write(f'## {category}/ ({count} scripts)\n\n')
        for script in sorted(scripts_by_category[category]):
            f.write(f'- `{script}`\n')
        f.write('\n')

    f.write('---\n\n')
    f.write(f'**Total**: {total_scripts} operational Python scripts across {len(scripts_by_category)} categories\n')

print(f'\nInventory saved to: {output_file}')
