#!/usr/bin/env python3
"""
Update all Python scripts to use consolidated osint_master.db
Replace references to archived databases
"""

import os
import re
from pathlib import Path
from datetime import datetime

class DatabaseReferenceUpdater:
    def __init__(self):
        self.scripts_dir = Path("C:/Projects/OSINT - Foresight/scripts")
        self.updates_made = []

        # Mapping of old database references to new
        self.db_replacements = {
            # Direct database replacements
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db",
            "osint_master.db": "osint_master.db"
        }

        # Table name updates (old table -> new table in master)
        self.table_replacements = {
            # TED tables
            "ted_china_contracts": "ted_china_contracts",
            "ted_procurement_chinese_entities_found": "ted_procurement_chinese_entities_found",
            "ted_procurement_pattern_matches": "ted_procurement_pattern_matches",

            # OpenAlex tables
            "import_openalex_institutions": "import_openalex_institutions",
            "import_openalex_china_entities": "import_openalex_china_entities",

            # Patent tables
            "patents": "patents",

            # Entity tables
            "entities": "entities",
            "entity_relationships": "entity_relationships"
        }

    def update_file(self, file_path):
        """Update database references in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content
            changes = []

            # Replace database names
            for old_db, new_db in self.db_replacements.items():
                pattern1 = rf'(["\'])([^"\']*){re.escape(old_db)}(["\'])'
                pattern2 = rf'(["\'])({re.escape(old_db)})(["\'])'

                if old_db in content:
                    content = re.sub(pattern1, rf'\1\2{new_db}\3', content)
                    content = re.sub(pattern2, rf'\1{new_db}\3', content)
                    changes.append(f"{old_db} -> {new_db}")

            # Update table names in SQL queries
            for old_table, new_table in self.table_replacements.items():
                # Match table names in SQL (FROM, JOIN, etc.)
                patterns = [
                    rf'\bFROM\s+{re.escape(old_table)}\b',
                    rf'\bJOIN\s+{re.escape(old_table)}\b',
                    rf'\bINTO\s+{re.escape(old_table)}\b',
                    rf'\bTABLE\s+{re.escape(old_table)}\b',
                    rf'"{re.escape(old_table)}"',
                    rf"'{re.escape(old_table)}'"
                ]

                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        content = re.sub(
                            pattern,
                            lambda m: m.group(0).replace(old_table, new_table),
                            content,
                            flags=re.IGNORECASE
                        )
                        if f"{old_table} -> {new_table}" not in changes:
                            changes.append(f"{old_table} -> {new_table}")

            # Only write if changes were made
            if content != original_content:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)

                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.updates_made.append({
                    'file': file_path.name,
                    'changes': changes,
                    'backup': backup_path.name
                })
                return True

        except Exception as e:
            print(f"Error updating {file_path.name}: {e}")
            return False

        return False

    def find_python_files(self):
        """Find all Python files in scripts directory"""
        python_files = []

        for root, dirs, files in os.walk(self.scripts_dir):
            # Skip certain directories
            if '__pycache__' in root or '.git' in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        return python_files

    def run(self):
        """Update all Python scripts"""
        print("="*60)
        print("UPDATING DATABASE REFERENCES IN SCRIPTS")
        print("="*60)

        python_files = self.find_python_files()
        print(f"\nFound {len(python_files)} Python files to check")

        updated_count = 0
        for file_path in python_files:
            if self.update_file(file_path):
                updated_count += 1
                print(f"  [UPDATED] {file_path.name}")
                for change in self.updates_made[-1]['changes']:
                    print(f"    - {change}")

        # Generate report
        if self.updates_made:
            self.generate_report()

        print("\n" + "="*60)
        print(f"COMPLETE: Updated {updated_count} files")
        print("="*60)

        return updated_count

    def generate_report(self):
        """Generate update report"""
        report = f"""# Database Reference Update Report
**Date**: {datetime.now().isoformat()}
**Files Updated**: {len(self.updates_made)}

## Changes Made

"""
        for update in self.updates_made:
            report += f"### {update['file']}\n"
            report += f"- Backup: {update['backup']}\n"
            report += f"- Changes:\n"
            for change in update['changes']:
                report += f"  - {change}\n"
            report += "\n"

        report += """
## Database Consolidation Map

All references updated to use `osint_master.db`:
- Patent data: google_patents_china.db → osint_master.db
- Entity graphs: entity_graph.db → osint_master.db
- TED data: ted_*.db → osint_master.db
- OpenAlex data: openalex_*.db → osint_master.db
- Intelligence feeds: *_intelligence.db → osint_master.db

## Table Name Updates

- chinese_patents → patents
- entity_nodes → entities
- ted_contracts → ted_china_contracts
- openalex_collaborations → import_openalex_institutions

## Verification

To verify scripts still work:
1. Test key collection scripts
2. Verify analysis scripts can query data
3. Check that views are accessible
"""

        report_path = Path("C:/Projects/OSINT - Foresight/KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE/SCRIPT_UPDATE_REPORT.md")
        with open(report_path, 'w') as f:
            f.write(report)

        print(f"\nReport saved to: {report_path.name}")

if __name__ == "__main__":
    updater = DatabaseReferenceUpdater()
    updater.run()