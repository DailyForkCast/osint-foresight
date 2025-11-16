#!/usr/bin/env python3
"""
archive_old_docs.py - Automated Documentation Archival System

Implements the ARCHIVAL_POLICY.md for OSINT Foresight project:
- Archives documentation files (*.md, *.json, *.txt) older than 90 days
- Protects Tier 1+2 critical documentation
- Organizes by archival date (YYYY-MM) and data source
- Updates ARCHIVE_INDEX.md for each month
- Generates comprehensive archival report

Usage:
    python archive_old_docs.py --dry-run    # Preview what would be archived
    python archive_old_docs.py              # Execute archival
    python archive_old_docs.py --age 60     # Archive files older than 60 days
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import argparse

# Configuration
PROJECT_ROOT = Path("C:/Projects/OSINT - Foresight")
ARCHIVE_AGE_DAYS = 90  # Default: archive files older than 90 days
CHECKPOINT_AGE_DAYS = 30  # Keep checkpoints active for 30 days minimum

# Directories to scan
SCAN_DIRS = [
    PROJECT_ROOT / "analysis",
    PROJECT_ROOT / "KNOWLEDGE_BASE"
]

# Archive locations
ARCHIVES = {
    "analysis": PROJECT_ROOT / "analysis" / "archive",
    "KNOWLEDGE_BASE": PROJECT_ROOT / "KNOWLEDGE_BASE" / "archive"
}

# File extensions to archive
ARCHIVAL_EXTENSIONS = [".md", ".json", ".txt"]

# Protected files (NEVER archive these)
PROTECTED_FILES = [
    # Tier 1: Critical Documentation
    "README.md",
    "CLAUDE_CODE_MASTER_V9.8_COMPLETE.md",
    "UNIFIED_DATA_INFRASTRUCTURE_INVENTORY_MULTICOUNTRY.md",
    "SCRIPTS_INVENTORY.md",

    # Tier 2: Architecture
    "DATABASE_CONSOLIDATION_REPORT.md",
    "CONSOLIDATION_COMPLETE_SUMMARY.md",
    "FINAL_CONSOLIDATION_REPORT.md",

    # Policy and index files
    "ARCHIVAL_POLICY.md",
    "DOCUMENTATION_REMEDIATION_COMPLETION_REPORT.md",
    "ARCHIVE_INDEX.md",

    # Archive READMEs
    "README.md"  # In archive directories
]

# Protected patterns (files matching these patterns are never archived)
PROTECTED_PATTERNS = [
    "CURRENT",
    "STATUS",
    "MASTER",
    "INVENTORY",
    "POLICY"
]

# Protected directories (never scan these)
PROTECTED_DIRS = [
    "archive",  # Don't re-archive archives
    "scripts",  # Code is never archived
    "src",
    "tests",
    "config",
    "data",
    "database",
    "docs/prompts/active/master",
    "KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE"
]

# Data source categories for analysis files
DATA_SOURCES = ["openalex", "ted", "uspto", "usaspending", "cross-source"]

# Active checkpoint files (protect recent checkpoints)
CHECKPOINT_PATTERNS = ["checkpoint", "status", "progress"]


class ArchivalStats:
    """Track statistics during archival process"""
    def __init__(self):
        self.scanned = 0
        self.eligible = 0
        self.protected = 0
        self.archived = 0
        self.errors = []
        self.by_source = defaultdict(int)
        self.by_month = defaultdict(int)
        self.total_size = 0

    def add_archived(self, file_path, source, month):
        self.archived += 1
        self.by_source[source] += 1
        self.by_month[month] += 1
        try:
            self.total_size += file_path.stat().st_size
        except:
            pass


def is_protected_file(file_path: Path) -> tuple[bool, str]:
    """
    Check if a file is protected from archival.
    Returns (is_protected, reason)
    """
    filename = file_path.name

    # Check exact filename matches
    if filename in PROTECTED_FILES:
        return True, f"Protected file: {filename}"

    # Check protected patterns
    for pattern in PROTECTED_PATTERNS:
        if pattern.upper() in filename.upper():
            return True, f"Contains protected pattern: {pattern}"

    # Check if in protected directory
    relative = file_path.relative_to(PROJECT_ROOT)
    for protected_dir in PROTECTED_DIRS:
        if protected_dir in str(relative):
            return True, f"In protected directory: {protected_dir}"

    # Check if it's a recent checkpoint
    if any(p in filename.lower() for p in CHECKPOINT_PATTERNS):
        age_days = get_file_age_days(file_path)
        if age_days < CHECKPOINT_AGE_DAYS:
            return True, f"Recent checkpoint file (< {CHECKPOINT_AGE_DAYS} days)"

    return False, ""


def get_file_age_days(file_path: Path) -> int:
    """Get the age of a file in days since last modification"""
    try:
        mtime = file_path.stat().st_mtime
        file_date = datetime.fromtimestamp(mtime)
        age = datetime.now() - file_date
        return age.days
    except Exception as e:
        print(f"Warning: Could not get age for {file_path}: {e}")
        return 0


def determine_data_source(file_path: Path) -> str:
    """Determine which data source category a file belongs to"""
    filename_lower = file_path.name.lower()

    # Check filename for data source indicators
    for source in DATA_SOURCES:
        if source in filename_lower:
            return source

    # Check parent directory names
    for parent in file_path.parents:
        parent_lower = parent.name.lower()
        for source in DATA_SOURCES:
            if source in parent_lower:
                return source

    # Default to cross-source if no specific source identified
    return "cross-source"


def get_archive_path(file_path: Path, archive_root: Path) -> Path:
    """Determine the archive destination path for a file"""
    # Get archival month (YYYY-MM)
    mtime = file_path.stat().st_mtime
    file_date = datetime.fromtimestamp(mtime)
    archive_month = file_date.strftime("%Y-%m")

    # Determine base archive location
    if "analysis" in str(file_path):
        # Analysis files: organize by data source
        data_source = determine_data_source(file_path)
        archive_dir = archive_root / archive_month / data_source
    else:
        # KNOWLEDGE_BASE files: just by month
        archive_dir = archive_root / archive_month

    return archive_dir / file_path.name


def create_archive_index(archive_month_dir: Path, archived_files: list):
    """Create or update ARCHIVE_INDEX.md for a month"""
    index_path = archive_month_dir / "ARCHIVE_INDEX.md"

    # Calculate statistics
    total_files = len(archived_files)
    total_size = sum(f.get('size', 0) for f in archived_files)
    size_mb = total_size / (1024 * 1024)

    # Group by data source if in analysis
    by_source = defaultdict(int)
    for f in archived_files:
        source = f.get('source', 'unknown')
        by_source[source] += 1

    # Create index content
    month_year = archive_month_dir.name
    now = datetime.now().strftime("%Y-%m-%d")

    content = f"""# Archive Index - {month_year}

**Archive Date**: {month_year}
**Files Archived**: {total_files}
**Total Size**: {size_mb:.2f} MB
**Index Updated**: {now}

## Archived Files

| File Name | Original Location | Archive Date | Reason | Superseded By |
|-----------|-------------------|--------------|--------|---------------|
"""

    # Add file entries
    for f in sorted(archived_files, key=lambda x: x['name']):
        name = f['name']
        original = f.get('original', 'unknown')
        date = f.get('date', now)
        reason = f.get('reason', 'Automated archival (>90 days old)')
        superseded = f.get('superseded', 'N/A')
        content += f"| {name} | {original} | {date} | {reason} | {superseded} |\n"

    # Add data source breakdown if in analysis
    if by_source:
        content += "\n## Data Source Breakdown\n\n"
        for source in sorted(by_source.keys()):
            count = by_source[source]
            content += f"- **{source}**: {count} files\n"

    content += "\n## Notes\n\n"
    content += f"This archive was automatically generated by archive_old_docs.py on {now}.\n"
    content += "Files are organized by data source (for analysis files) or date (for KNOWLEDGE_BASE files).\n"

    # Write index
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  ✓ Updated {index_path}")


def scan_directory(scan_dir: Path, age_threshold_days: int, dry_run: bool, stats: ArchivalStats):
    """Scan a directory for files eligible for archival"""
    archive_root = ARCHIVES.get(scan_dir.name, scan_dir / "archive")
    archived_by_month = defaultdict(list)

    print(f"\n{'='*60}")
    print(f"Scanning: {scan_dir}")
    print(f"Archive root: {archive_root}")
    print(f"{'='*60}")

    # Walk directory tree
    for root, dirs, files in os.walk(scan_dir):
        # Skip protected directories
        dirs[:] = [d for d in dirs if d not in PROTECTED_DIRS]

        for filename in files:
            file_path = Path(root) / filename
            stats.scanned += 1

            # Check file extension
            if file_path.suffix not in ARCHIVAL_EXTENSIONS:
                continue

            # Check if protected
            is_protected, reason = is_protected_file(file_path)
            if is_protected:
                stats.protected += 1
                if dry_run:
                    print(f"  ⚠️  PROTECTED: {file_path.name} - {reason}")
                continue

            # Check age
            age_days = get_file_age_days(file_path)
            if age_days < age_threshold_days:
                continue

            stats.eligible += 1

            # Determine archive location
            archive_path = get_archive_path(file_path, archive_root)
            archive_month = archive_path.parent.parent.name if "analysis" in str(scan_dir) else archive_path.parent.name
            data_source = determine_data_source(file_path)

            if dry_run:
                print(f"  📦 WOULD ARCHIVE: {file_path.name}")
                print(f"     Age: {age_days} days | Source: {data_source}")
                print(f"     → {archive_path}")
            else:
                try:
                    # Create archive directory
                    archive_path.parent.mkdir(parents=True, exist_ok=True)

                    # Move file
                    shutil.move(str(file_path), str(archive_path))

                    # Track for index
                    archived_by_month[archive_month].append({
                        'name': filename,
                        'original': str(file_path.relative_to(PROJECT_ROOT)),
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'reason': f'Automated archival ({age_days} days old)',
                        'source': data_source,
                        'size': file_path.stat().st_size
                    })

                    stats.add_archived(archive_path, data_source, archive_month)
                    print(f"  ✓ ARCHIVED: {filename} → {archive_path}")

                except Exception as e:
                    error_msg = f"Failed to archive {file_path}: {e}"
                    stats.errors.append(error_msg)
                    print(f"  ❌ ERROR: {error_msg}")

    # Create/update archive indexes
    if not dry_run:
        for month, files in archived_by_month.items():
            if "analysis" in str(scan_dir):
                month_dir = archive_root / month
            else:
                month_dir = archive_root / month
            create_archive_index(month_dir, files)


def generate_report(stats: ArchivalStats, age_threshold: int, dry_run: bool):
    """Generate archival summary report"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*60}")
    print(f"ARCHIVAL {'PREVIEW' if dry_run else 'SUMMARY'}")
    print(f"{'='*60}")
    print(f"Timestamp: {now}")
    print(f"Age Threshold: {age_threshold} days")
    print(f"Mode: {'DRY RUN (no changes made)' if dry_run else 'LIVE EXECUTION'}")
    print()
    print(f"Files Scanned:    {stats.scanned}")
    print(f"Files Eligible:   {stats.eligible}")
    print(f"Files Protected:  {stats.protected}")

    if not dry_run:
        print(f"Files Archived:   {stats.archived}")
        print(f"Total Size:       {stats.total_size / (1024*1024):.2f} MB")
        print(f"Errors:           {len(stats.errors)}")

    if stats.by_source:
        print(f"\nBy Data Source:")
        for source in sorted(stats.by_source.keys()):
            print(f"  - {source}: {stats.by_source[source]} files")

    if stats.by_month:
        print(f"\nBy Archive Month:")
        for month in sorted(stats.by_month.keys()):
            print(f"  - {month}: {stats.by_month[month]} files")

    if stats.errors:
        print(f"\nErrors Encountered:")
        for error in stats.errors:
            print(f"  ❌ {error}")

    print(f"\n{'='*60}")

    if dry_run:
        print("ℹ️  This was a DRY RUN. No files were moved.")
        print("   Run without --dry-run to execute archival.")
    else:
        print("✅ Archival complete. Check ARCHIVE_INDEX.md files for details.")

    print(f"{'='*60}\n")


def main():
    """Main archival process"""
    parser = argparse.ArgumentParser(
        description="Archive old documentation files per ARCHIVAL_POLICY.md"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be archived without making changes"
    )
    parser.add_argument(
        "--age",
        type=int,
        default=ARCHIVE_AGE_DAYS,
        help=f"Archive files older than this many days (default: {ARCHIVE_AGE_DAYS})"
    )

    args = parser.parse_args()

    print(f"\n{'#'*60}")
    print("# OSINT Foresight - Documentation Archival System")
    print(f"# {'DRY RUN MODE' if args.dry_run else 'LIVE EXECUTION MODE'}")
    print(f"{'#'*60}\n")

    if not args.dry_run:
        response = input("⚠️  This will move files to archive. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Archival cancelled.")
            return

    stats = ArchivalStats()

    # Scan each directory
    for scan_dir in SCAN_DIRS:
        if scan_dir.exists():
            scan_directory(scan_dir, args.age, args.dry_run, stats)
        else:
            print(f"⚠️  Directory not found: {scan_dir}")

    # Generate report
    generate_report(stats, args.age, args.dry_run)

    # Save report to file (if not dry run)
    if not dry_run:
        report_path = PROJECT_ROOT / "analysis" / f"ARCHIVAL_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'age_threshold_days': args.age,
            'stats': {
                'scanned': stats.scanned,
                'eligible': stats.eligible,
                'protected': stats.protected,
                'archived': stats.archived,
                'total_size_mb': stats.total_size / (1024*1024),
                'errors': len(stats.errors)
            },
            'by_source': dict(stats.by_source),
            'by_month': dict(stats.by_month),
            'errors': stats.errors
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Report saved: {report_path}")


if __name__ == "__main__":
    main()
