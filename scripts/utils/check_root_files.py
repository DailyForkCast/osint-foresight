#!/usr/bin/env python3
"""
Check for files that shouldn't be in the root directory
Used by pre-commit hooks to enforce project structure
"""

import sys
import os
from pathlib import Path
import argparse

# Files allowed in root directory
ALLOWED_ROOT_FILES = {
    # Core project files
    'README.md',
    'LICENSE',
    'Makefile',

    # Python project files
    'requirements.txt',
    'setup.py',
    'setup.cfg',
    'pyproject.toml',
    'manage.py',  # Django projects

    # Environment files
    'environment.yml',
    '.env.example',

    # Git files
    '.gitignore',
    '.gitattributes',

    # CI/CD
    '.pre-commit-config.yaml',
    'Dockerfile',
    'docker-compose.yml',
    '.travis.yml',
    '.gitlab-ci.yml',
    '.github',

    # IDE configs (though better in .gitignore)
    '.vscode',
    '.idea',
}

def check_python_files():
    """Check for Python files that shouldn't be in root"""

    root = Path.cwd()
    python_files = [f for f in root.glob('*.py') if f.is_file()]

    disallowed = []
    for file in python_files:
        if file.name not in ALLOWED_ROOT_FILES and file.name not in ['setup.py', 'manage.py']:
            disallowed.append(file.name)

    if disallowed:
        print(f"ERROR: Found Python files in root that should be organized:")
        for file in disallowed:
            # Suggest where to move it
            if file.startswith('test_'):
                suggestion = 'tests/integration/'
            elif file.startswith('demo_'):
                suggestion = 'scripts/demos/'
            elif file.startswith('analyze_'):
                suggestion = 'scripts/analysis/'
            elif file.startswith('load_'):
                suggestion = 'tools/data_loaders/'
            else:
                suggestion = 'scripts/utils/'

            print(f"  - {file} -> {suggestion}")

        return 1

    return 0

def check_document_files():
    """Check for Word/Excel/PowerPoint files in root"""

    root = Path.cwd()
    doc_extensions = ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']

    doc_files = []
    for ext in doc_extensions:
        doc_files.extend([f.name for f in root.glob(f'*{ext}') if f.is_file()])

    if doc_files:
        print(f"ERROR: Found document files in root that should be in out/exports/:")
        for file in doc_files:
            # Try to determine country from filename
            country_hint = ''
            for country in ['Ireland', 'Austria', 'Slovakia', 'Portugal']:
                if country.lower() in file.lower():
                    country_code = {
                        'ireland': 'IE',
                        'austria': 'AT',
                        'slovakia': 'SK',
                        'portugal': 'PT'
                    }[country.lower()]
                    country_hint = f'country={country_code}/'
                    break

            print(f"  - {file} -> out/exports/{country_hint}")

        return 1

    return 0

def check_markdown_files():
    """Check for Markdown files that should be organized"""

    root = Path.cwd()
    md_files = [f for f in root.glob('*.md') if f.is_file()]

    # Files that must stay in root
    must_keep = {'README.md', 'LICENSE.md', 'CONTRIBUTING.md', 'CHANGELOG.md', 'CODE_OF_CONDUCT.md'}

    suggestions = []
    for file in md_files:
        if file.name not in must_keep:
            # Suggest destination based on name
            name_lower = file.name.lower()

            if 'guide' in name_lower or 'setup' in name_lower or 'install' in name_lower:
                dest = 'docs/guides/'
            elif 'methodology' in name_lower or 'framework' in name_lower or 'assessment' in name_lower:
                dest = 'docs/methodology/'
            elif 'roadmap' in name_lower or 'plan' in name_lower:
                dest = 'docs/planning/'
            elif 'analysis' in name_lower or 'report' in name_lower or 'summary' in name_lower or 'status' in name_lower:
                dest = 'docs/reports/'
            elif 'source' in name_lower or 'inventory' in name_lower or 'reference' in name_lower:
                dest = 'docs/references/'
            else:
                dest = 'docs/'

            suggestions.append((file.name, dest))

    if suggestions:
        print(f"WARNING: Found {len(suggestions)} Markdown files that could be better organized:")
        for file, dest in suggestions:
            print(f"  - {file} → {dest}")
        print("\nConsider moving these files for better organization.")
        # Return 0 (warning only) so it doesn't block commits
        return 0

    return 0

def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(description='Check root directory compliance')
    parser.add_argument('--docs', action='store_true',
                       help='Check for document files (.docx, .xlsx, .pptx)')
    parser.add_argument('--python', action='store_true',
                       help='Check for Python files')
    parser.add_argument('--markdown', action='store_true',
                       help='Check for Markdown files to organize')
    parser.add_argument('--all', action='store_true',
                       help='Run all checks')

    args = parser.parse_args()

    # Default to checking Python files if no specific check requested
    if not any([args.docs, args.python, args.markdown, args.all]):
        args.python = True

    exit_code = 0

    if args.all or args.python:
        exit_code |= check_python_files()

    if args.all or args.docs:
        exit_code |= check_document_files()

    if args.all or args.markdown:
        exit_code |= check_markdown_files()

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
