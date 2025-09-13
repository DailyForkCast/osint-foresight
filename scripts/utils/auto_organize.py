#!/usr/bin/env python3
"""
Automated File Organization System for OSINT Foresight
Ensures all files follow the project structure guidelines
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectOrganizer:
    """Automatically organizes project files according to best practices"""
    
    def __init__(self, project_root: Path = Path.cwd()):
        self.root = project_root
        self.dry_run = True  # Safety: always dry run by default
        self.moves = []  # Track proposed moves
        
        # Define file mappings
        self.file_rules = {
            # Python files in root (except setup files)
            'root_python': {
                'pattern': '*.py',
                'location': 'root',
                'rules': [
                    ('test_*.py', 'tests/integration/'),
                    ('*_test.py', 'tests/unit/'),
                    ('demo_*.py', 'scripts/demos/'),
                    ('initialize_*.py', 'scripts/setup/'),
                    ('setup_*.py', 'scripts/setup/'),
                    ('analyze_*.py', 'scripts/analysis/'),
                    ('visualize_*.py', 'tools/visualization/'),
                    ('load_*.py', 'tools/data_loaders/'),
                    ('backup_*.py', 'scripts/backup/'),
                    ('convert_*.py', 'scripts/utils/'),
                ]
            },
            
            # Documentation in root (except README)
            'root_docs': {
                'pattern': '*.md',
                'location': 'root',
                'rules': [
                    ('README.md', None),  # Keep in root
                    ('LICENSE*', None),  # Keep in root
                    ('*GUIDE*.md', 'docs/guides/'),
                    ('*METHODOLOGY*.md', 'docs/methodology/'),
                    ('*FRAMEWORK*.md', 'docs/methodology/'),
                    ('*ASSESSMENT*.md', 'docs/methodology/'),
                    ('*SUMMARY*.md', 'docs/reports/'),
                    ('*ANALYSIS*.md', 'docs/analysis/'),
                    ('*ROADMAP*.md', 'docs/planning/'),
                    ('*SETUP*.md', 'docs/guides/'),
                    ('*INVENTORY*.md', 'docs/references/'),
                    ('*SOURCES*.md', 'docs/references/'),
                    ('*STATUS*.md', 'docs/reports/'),
                ]
            },
            
            # Word documents should never be in root
            'word_docs': {
                'pattern': '*.docx',
                'location': 'root',
                'rules': [
                    ('*Ireland*.docx', 'out/exports/country=IE/'),
                    ('*Austria*.docx', 'out/exports/country=AT/'),
                    ('*Slovakia*.docx', 'out/exports/country=SK/'),
                    ('*Portugal*.docx', 'out/exports/country=PT/'),
                    ('*.docx', 'out/exports/'),
                ]
            },
            
            # Config files
            'config_files': {
                'pattern': '*.json',
                'location': 'root',
                'rules': [
                    ('package*.json', None),  # Keep in root if exists
                    ('tsconfig.json', None),  # Keep in root if exists
                    ('capabilities.json', 'config/'),
                    ('*config*.json', 'config/'),
                    ('*.json', 'data/processed/'),
                ]
            },
            
            # Data files
            'data_files': {
                'pattern': '*.csv',
                'location': 'root',
                'rules': [
                    ('*country=*/*.csv', None),  # Already organized
                    ('*.csv', 'data/raw/'),
                ]
            },
        }
        
        # Define directory structure requirements
        self.required_dirs = [
            'src/analysis',
            'src/pulls',
            'src/utils',
            'scripts/analysis',
            'scripts/backup',
            'scripts/demos',
            'scripts/setup',
            'scripts/utils',
            'tools/data_loaders',
            'tools/visualization',
            'config',
            'data/raw',
            'data/processed',
            'data/interim',
            'docs/architecture',
            'docs/guides',
            'docs/methodology',
            'docs/planning',
            'docs/prompts',
            'docs/references',
            'docs/reports',
            'docs/analysis',
            'reports',
            'artifacts',
            'evidence',
            'notebooks/exploratory',
            'notebooks/reports',
            'tests/unit',
            'tests/integration',
            'tests/fixtures',
            'out/exports',
            'queries/keywords',
            'archive',
            'scheduled_tasks',
        ]
    
    def ensure_directories(self):
        """Create all required directories if they don't exist"""
        
        for dir_path in self.required_dirs:
            full_path = self.root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")
    
    def find_misplaced_files(self) -> List[Tuple[Path, Path]]:
        """Find files that should be moved according to rules"""
        
        moves = []
        
        for category, config in self.file_rules.items():
            pattern = config['pattern']
            location = config['location']
            rules = config['rules']
            
            # Find files matching pattern
            if location == 'root':
                search_path = self.root
                files = list(search_path.glob(pattern))
                # Filter out files already in subdirectories
                files = [f for f in files if f.parent == self.root]
            else:
                search_path = self.root / location
                if search_path.exists():
                    files = list(search_path.glob(pattern))
                else:
                    files = []
            
            # Apply rules to each file
            for file_path in files:
                for pattern_rule, destination in rules:
                    if self._matches_pattern(file_path.name, pattern_rule):
                        if destination is None:
                            # File should stay where it is
                            break
                        else:
                            dest_path = self.root / destination / file_path.name
                            if file_path != dest_path:
                                moves.append((file_path, dest_path))
                        break
        
        return moves
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches pattern (simple wildcard matching)"""
        
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def analyze_structure(self) -> Dict:
        """Analyze current project structure and identify issues"""
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'root_files': [],
            'misplaced_files': [],
            'missing_dirs': [],
            'suggestions': []
        }
        
        # Check for files in root that shouldn't be there
        allowed_root_files = {
            'README.md', 'LICENSE', 'Makefile', 'requirements.txt',
            'environment.yml', '.gitignore', '.pre-commit-config.yaml',
            'pyproject.toml', 'setup.py', 'setup.cfg'
        }
        
        for item in self.root.iterdir():
            if item.is_file():
                if item.name not in allowed_root_files:
                    analysis['root_files'].append(item.name)
        
        # Find misplaced files
        moves = self.find_misplaced_files()
        analysis['misplaced_files'] = [
            {'from': str(src.relative_to(self.root)), 
             'to': str(dest.relative_to(self.root))}
            for src, dest in moves
        ]
        
        # Check for missing directories
        for dir_path in self.required_dirs:
            full_path = self.root / dir_path
            if not full_path.exists():
                analysis['missing_dirs'].append(dir_path)
        
        # Generate suggestions
        if analysis['root_files']:
            analysis['suggestions'].append(
                f"Found {len(analysis['root_files'])} files in root that should be organized"
            )
        
        if analysis['missing_dirs']:
            analysis['suggestions'].append(
                f"Missing {len(analysis['missing_dirs'])} required directories"
            )
        
        if analysis['misplaced_files']:
            analysis['suggestions'].append(
                f"Found {len(analysis['misplaced_files'])} files that should be moved"
            )
        
        return analysis
    
    def organize(self, dry_run: bool = True):
        """Organize files according to rules"""
        
        self.dry_run = dry_run
        
        # Ensure all directories exist
        if not dry_run:
            self.ensure_directories()
        
        # Find files to move
        moves = self.find_misplaced_files()
        
        if not moves:
            logger.info("[OK] All files are properly organized!")
            return
        
        logger.info(f"Found {len(moves)} files to organize")
        
        for src, dest in moves:
            if dry_run:
                logger.info(f"[DRY RUN] Would move: {src.name} -> {dest.relative_to(self.root)}")
            else:
                # Create destination directory if needed
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(src), str(dest))
                logger.info(f"Moved: {src.name} -> {dest.relative_to(self.root)}")
        
        if dry_run:
            logger.info("\n[OK] Dry run complete. Use --execute to apply changes.")
        else:
            logger.info("\n[OK] Organization complete!")
    
    def create_report(self) -> str:
        """Create a detailed report of the project structure"""
        
        analysis = self.analyze_structure()
        
        report = []
        report.append("=" * 60)
        report.append("PROJECT STRUCTURE ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {analysis['timestamp']}")
        report.append("")
        
        # Root files analysis
        report.append("ROOT DIRECTORY STATUS")
        report.append("-" * 30)
        if analysis['root_files']:
            report.append(f"[WARNING] Files that should be organized ({len(analysis['root_files'])}):")
            for file in analysis['root_files']:
                report.append(f"  - {file}")
        else:
            report.append("[OK] Root directory is clean")
        report.append("")
        
        # Missing directories
        if analysis['missing_dirs']:
            report.append("MISSING DIRECTORIES")
            report.append("-" * 30)
            for dir_path in analysis['missing_dirs']:
                report.append(f"  - {dir_path}")
            report.append("")
        
        # Misplaced files
        if analysis['misplaced_files']:
            report.append("FILES TO REORGANIZE")
            report.append("-" * 30)
            for move in analysis['misplaced_files']:
                report.append(f"  {move['from']}")
                report.append(f"    -> {move['to']}")
            report.append("")
        
        # Suggestions
        if analysis['suggestions']:
            report.append("RECOMMENDATIONS")
            report.append("-" * 30)
            for suggestion in analysis['suggestions']:
                report.append(f"  * {suggestion}")
            report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 30)
        total_issues = (
            len(analysis['root_files']) + 
            len(analysis['missing_dirs']) + 
            len(analysis['misplaced_files'])
        )
        
        if total_issues == 0:
            report.append("[OK] Project structure is fully compliant!")
        else:
            report.append(f"[WARNING] Found {total_issues} issues to address")
            report.append("  Run with --execute to automatically fix")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, output_path: Path = None):
        """Save analysis report to file"""
        
        if output_path is None:
            output_path = self.root / 'docs' / 'reports' / f'structure_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.create_report()
        with open(output_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved to: {output_path}")
        return output_path


def main():
    """Main entry point for auto-organization"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Automatically organize project files')
    parser.add_argument('--execute', action='store_true',
                       help='Actually move files (default is dry run)')
    parser.add_argument('--report', action='store_true',
                       help='Generate and save analysis report')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress output')
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Create organizer
    organizer = ProjectOrganizer()
    
    if args.report:
        # Generate report
        report = organizer.create_report()
        print(report)
        organizer.save_report()
    else:
        # Run organization
        organizer.organize(dry_run=not args.execute)


if __name__ == '__main__':
    main()