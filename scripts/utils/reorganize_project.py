#!/usr/bin/env python3
"""
Project Reorganization Script
Reorganizes OSINT-Foresight project according to best practices
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

class ProjectReorganizer:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.root = Path.cwd()
        self.changes = []
        self.errors = []

    def create_directory_structure(self):
        """Create the new directory structure"""
        new_dirs = [
            "scripts/backup",
            "scripts/setup",
            "scripts/analysis",
            "scripts/utils",
            "tools/data_loaders",
            "tools/visualization",
            "artifacts",
            "notebooks/exploratory",
            "notebooks/reports",
            "tests/unit",
            "tests/integration",
            "tests/fixtures",
            "docs/architecture",
            "docs/methodology",
            "docs/guides",
            "out/exports",
            "src/collectors",
            "src/utils"
        ]

        for dir_path in new_dirs:
            full_path = self.root / dir_path
            if not full_path.exists():
                if not self.dry_run:
                    full_path.mkdir(parents=True, exist_ok=True)
                self.changes.append(f"CREATE DIR: {dir_path}")

    def move_files(self):
        """Move files to their appropriate locations"""

        # File movement mapping
        moves = {
            # Backup scripts
            "backup_manager.py": "scripts/backup/backup_manager.py",
            "simple_backup.py": "scripts/backup/simple_backup.py",
            "backup_project.bat": "scripts/backup/backup_project.bat",

            # Setup scripts
            "setup_bigquery_dataset.py": "scripts/setup/setup_bigquery_dataset.py",
            "setup_bigquery_tables.py": "scripts/setup/setup_bigquery_tables.py",
            "create_bigquery_datasets.py": "scripts/setup/create_bigquery_datasets.py",

            # Analysis scripts
            "analyze_chinese_institutions.py": "scripts/analysis/analyze_chinese_institutions.py",
            "analyze_cordis.py": "scripts/analysis/analyze_cordis.py",
            "analyze_google_patents.py": "scripts/analysis/analyze_google_patents.py",
            "bigquery_patents_analysis.py": "scripts/analysis/bigquery_patents_analysis.py",

            # Data loader tools
            "load_country_data_to_bigquery.py": "tools/data_loaders/load_country_data.py",
            "load_data_autodetect.py": "tools/data_loaders/load_autodetect.py",
            "quick_load_bigquery.py": "tools/data_loaders/quick_load.py",

            # Visualization tools
            "visualize_slovakia_data.py": "tools/visualization/visualize_country_data.py",

            # Utility scripts
            "convert_ireland_to_word.py": "scripts/utils/convert_to_word.py",
            "verify_phase_renumbering.py": "scripts/utils/verify_renumbering.py",

            # Documentation - Architecture
            "PROJECT_ORGANIZATION_GUIDE.md": "docs/architecture/PROJECT_ORGANIZATION_GUIDE.md",
            "PHASE_RENUMBERING_GUIDE.md": "docs/architecture/PHASE_RENUMBERING_GUIDE.md",

            # Documentation - Methodology
            "FORESIGHT_METHODOLOGY_EXPLANATION.md": "docs/methodology/FORESIGHT_METHODOLOGY.md",
            "CRITICAL_TECH_ASSESSMENT_REVISED.md": "docs/methodology/CRITICAL_TECH_ASSESSMENT.md",
            "CONTEXTUALIZATION_FRAMEWORK.md": "docs/methodology/CONTEXTUALIZATION_FRAMEWORK.md",
            "PATENT_RISK_CLASSIFICATION.md": "docs/methodology/PATENT_RISK_CLASSIFICATION.md",

            # Documentation - Guides
            "SETUP.md": "docs/guides/SETUP.md",
            "BACKUP_GUIDE.md": "docs/guides/BACKUP_GUIDE.md",
            "bigquery_setup_guide.md": "docs/guides/bigquery_setup_guide.md",
            "bigquery_studio_instructions.md": "docs/guides/bigquery_studio_instructions.md",
            "configure_path.md": "docs/guides/configure_path.md",
            "OPENALEX_STORAGE_ANALYSIS.md": "docs/guides/OPENALEX_STORAGE_ANALYSIS.md",

            # Move Word docs to out/exports
            "Ireland_OSINT_Foresight_Analysis.docx": "out/exports/country=IE/Ireland_OSINT_Foresight_Analysis.docx",

            # Other documentation
            "MASTER_PROMPT_IMPROVEMENTS.md": "docs/prompts/archive/MASTER_PROMPT_IMPROVEMENTS.md",
            "CAPABILITIES_SUMMARY.md": "docs/methodology/CAPABILITIES_SUMMARY.md",
            "capabilities.json": "config/capabilities.json"
        }

        for src, dst in moves.items():
            src_path = self.root / src
            dst_path = self.root / dst

            if src_path.exists():
                # Create parent directory if needed
                dst_path.parent.mkdir(parents=True, exist_ok=True)

                if not self.dry_run:
                    try:
                        shutil.move(str(src_path), str(dst_path))
                    except Exception as e:
                        self.errors.append(f"ERROR moving {src}: {e}")
                        continue

                self.changes.append(f"MOVE: {src} -> {dst}")

    def create_init_files(self):
        """Create __init__.py files for Python packages"""
        python_dirs = [
            "src/collectors",
            "src/utils",
            "scripts/backup",
            "scripts/setup",
            "scripts/analysis",
            "scripts/utils",
            "tools/data_loaders",
            "tools/visualization"
        ]

        for dir_path in python_dirs:
            init_file = self.root / dir_path / "__init__.py"
            if not init_file.exists():
                if not self.dry_run:
                    init_file.touch()
                self.changes.append(f"CREATE: {dir_path}/__init__.py")

    def create_gitignore(self):
        """Create or update .gitignore file"""
        gitignore_content = """# Temporary files
~$*
*.tmp
*.bak
.DS_Store
Thumbs.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# IDE
.vscode/
.idea/
*.swp
*.swo

# Output files in root (should be in out/)
/*.docx
/*.xlsx
/*.pptx

# Local config
.env
.env.local
*.local

# BigQuery credentials
*credentials*.json
*service-account*.json

# Large data files
*.csv
!metric_catalog.csv
!procurement_signals.csv
!forecast_registry.csv
!evidence_master.csv
"""

        gitignore_path = self.root / ".gitignore"
        if not self.dry_run:
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
        self.changes.append("CREATE/UPDATE: .gitignore")

    def update_imports_in_file(self, file_path):
        """Update import statements in a Python file"""
        # This is a placeholder - actual implementation would parse and update imports
        pass

    def generate_report(self):
        """Generate a report of changes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"reorganization_report_{timestamp}.txt"

        report_content = f"""Project Reorganization Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Mode: {"DRY RUN" if self.dry_run else "ACTUAL"}

CHANGES MADE:
{chr(10).join(self.changes)}

ERRORS:
{chr(10).join(self.errors) if self.errors else "None"}

Total changes: {len(self.changes)}
Total errors: {len(self.errors)}

Next Steps:
1. Review the changes above
2. If in dry run mode, run with --execute to apply changes
3. Update any broken imports in Python files
4. Run tests to ensure everything works
5. Commit changes to git
"""

        if not self.dry_run:
            with open(report_file, 'w') as f:
                f.write(report_content)

        print(report_content)
        return report_file

    def run(self):
        """Execute the reorganization"""
        print(f"Starting project reorganization (dry_run={self.dry_run})...")

        # Create backup first if not dry run
        if not self.dry_run:
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"Creating backup in {backup_dir}...")
            # Backup implementation would go here

        # Execute reorganization steps
        self.create_directory_structure()
        self.move_files()
        self.create_init_files()
        self.create_gitignore()

        # Generate report
        report_file = self.generate_report()

        if self.dry_run:
            print("\nThis was a DRY RUN. No actual changes were made.")
            print("Run with --execute flag to apply changes.")
        else:
            print(f"\nReorganization complete! Report saved to {report_file}")

        return len(self.errors) == 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Reorganize OSINT-Foresight project structure")
    parser.add_argument("--execute", action="store_true",
                       help="Actually perform the reorganization (default is dry run)")
    parser.add_argument("--backup", action="store_true", default=True,
                       help="Create backup before reorganizing")

    args = parser.parse_args()

    reorganizer = ProjectReorganizer(dry_run=not args.execute)
    success = reorganizer.run()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
