#!/usr/bin/env python3
"""
Fix classification labels in all reports
Removes official-sounding classification markings from personal OSINT learning project
"""

import os
from pathlib import Path

def fix_classification_labels():
    """Remove or replace official classification markings"""

    # Directories to check
    directories = [
        Path("C:/Projects/OSINT - Foresight/analysis"),
        Path("C:/Projects/OSINT - Foresight/docs"),
        Path("C:/Projects/OSINT - Foresight/reports")
    ]

    # Phrases to replace
    replacements = {
        "*Classification: For Official Use Only*": "*Personal OSINT Learning Project*",
        "*Classification: Unclassified - OSINT Analysis*": "*Personal OSINT Analysis*",
        "Classification: For Official Use Only": "Personal OSINT Learning Project",
        "Classification: Unclassified": "Personal Research",
        "*For Official Use Only*": "*Personal Research*",
        "For Official Use Only": "Personal Research"
    }

    fixed_files = []

    for directory in directories:
        if not directory.exists():
            continue

        # Find all .md files
        for md_file in directory.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                original_content = content

                # Apply replacements
                for old_text, new_text in replacements.items():
                    content = content.replace(old_text, new_text)

                # Only write if changed
                if content != original_content:
                    md_file.write_text(content, encoding='utf-8')
                    fixed_files.append(md_file.name)
                    print(f"Fixed: {md_file.name}")

            except Exception as e:
                print(f"Error processing {md_file.name}: {e}")

    print(f"\nFixed {len(fixed_files)} files")
    print("All classification markings have been updated to reflect personal learning project status")

    return fixed_files

if __name__ == "__main__":
    print("Fixing Classification Labels")
    print("=" * 50)
    print("Removing official-sounding classification markings...")
    print("This is a personal OSINT learning project\n")

    fixed = fix_classification_labels()

    if fixed:
        print("\nFiles updated:")
        for filename in fixed:
            print(f"  - {filename}")
    else:
        print("\nNo files needed updating")
