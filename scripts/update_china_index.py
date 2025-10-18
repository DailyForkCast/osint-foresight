#!/usr/bin/env python3
"""
Update China Analysis Index - Automated maintenance of China footprint documentation
Runs every 12 hours to track all China-related analysis files across the project.
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Set, Tuple

class ChinaIndexUpdater:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.china_files = {}
        self.country_analyses = {}
        self.stats = {
            'total_files': 0,
            'countries_with_analysis': set(),
            'data_sources': set(),
            'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        }

    def find_china_files(self) -> None:
        """Find all China-related files in the project."""
        # Pattern 1: Files with 'china' in the name (case-insensitive)
        china_patterns = [
            '**/*[Cc]hina*.json',
            '**/*[Cc]hina*.csv',
            '**/*[Cc]hina*.md',
            '**/*[Cc]hina*.sql',
            '**/*[Cc]hina*.log',
            '**/*[Cc]hina*.txt'
        ]

        for pattern in china_patterns:
            for file_path in self.project_root.glob(pattern):
                rel_path = file_path.relative_to(self.project_root)
                self.categorize_file(file_path, rel_path)

        # Pattern 2: Files in china_analysis directories
        for china_dir in self.project_root.glob('**/china_analysis/'):
            for file_path in china_dir.glob('*'):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.project_root)
                    self.categorize_file(file_path, rel_path)

    def categorize_file(self, file_path: Path, rel_path: Path) -> None:
        """Categorize a China file based on its location and content."""
        path_parts = rel_path.parts

        # Check if it's a country-specific analysis
        if 'countries' in path_parts or 'artifacts' in path_parts:
            # Extract country name
            for i, part in enumerate(path_parts):
                if part in ['countries', 'artifacts'] and i + 1 < len(path_parts):
                    country = path_parts[i + 1]
                    if country not in self.country_analyses:
                        self.country_analyses[country] = []
                    self.country_analyses[country].append({
                        'file': str(rel_path),
                        'description': self.extract_file_description(file_path),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
                    })
                    self.stats['countries_with_analysis'].add(country)
                    break
        else:
            # It's a core China file
            category = self.determine_category(rel_path)
            if category not in self.china_files:
                self.china_files[category] = []
            self.china_files[category].append({
                'file': str(rel_path),
                'description': self.extract_file_description(file_path),
                'size': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
            })

        self.stats['total_files'] += 1

        # Track data sources
        file_str = str(rel_path).lower()
        if 'usaspending' in file_str:
            self.stats['data_sources'].add('USAspending')
        if 'ted' in file_str:
            self.stats['data_sources'].add('TED')
        if 'openalex' in file_str:
            self.stats['data_sources'].add('OpenAlex')
        if 'cordis' in file_str:
            self.stats['data_sources'].add('CORDIS')
        if 'openaire' in file_str:
            self.stats['data_sources'].add('OpenAIRE')

    def determine_category(self, rel_path: Path) -> str:
        """Determine the category of a core China file."""
        file_str = str(rel_path).lower()
        name = rel_path.name.lower()

        if 'dictionary' in name or 'detection' in name or 'signal' in name:
            return 'Detection & Dictionaries'
        elif name.endswith('.sql'):
            return 'SQL & Queries'
        elif name.endswith('.md'):
            return 'Reports'
        elif 'timeline' in name or 'export' in name:
            return 'Exports & Timelines'
        elif 'ted' in name or 'usaspending' in name or 'openalex' in name:
            return 'Data Source Specific'
        else:
            return 'Analysis Results'

    def extract_file_description(self, file_path: Path) -> str:
        """Extract a description based on file name and content preview."""
        name = file_path.name

        # Common descriptions based on filename patterns
        descriptions = {
            'china_dictionary.json': 'Chinese entity name mappings and transliterations',
            'china_detection_dictionary.json': 'Methods and patterns for detecting China involvement',
            'china_signal_test_results.json': 'Test results for China detection algorithms',
            'china_analysis_results.json': 'Comprehensive China analysis across all sources',
            'china_usaspending_analysis.json': 'China patterns in US federal spending',
            'china_high_risk_contracts.csv': 'High-risk contracts involving Chinese entities',
            'china_collaboration_timeline.csv': 'Timeline of China collaborations across sources',
            'ted_china_findings.json': 'China involvement in TED procurement data',
            'CHINA_ANALYSIS_SUMMARY.md': 'Executive summary of China findings',
            'china_analysis_queries.sql': 'SQL queries for China analysis',
            'china_analysis_views.sql': 'Database views for China monitoring'
        }

        if name in descriptions:
            return descriptions[name]

        # Try to extract from file content for JSON files
        if name.endswith('.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if 'description' in data:
                            return data['description'][:100]
                        elif 'summary' in data:
                            return data['summary'][:100]
                        elif 'title' in data:
                            return data['title'][:100]
            except:
                pass

        # Generate based on filename
        base_name = name.replace('_', ' ').replace('-', ' ')
        return f"China analysis file: {base_name}"

    def generate_index(self) -> str:
        """Generate the markdown index document."""
        lines = []

        # Header
        lines.append("# China Analysis Index - Complete Repository Mapping")
        lines.append(f"**Last Updated:** {self.stats['last_updated']}")
        lines.append("**Auto-Update:** Every 12 hours via `scripts/update_china_index.py`")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Overview Statistics
        lines.append("## 📊 Overview Statistics")
        lines.append(f"- **Total China Analysis Files:** {self.stats['total_files']} files")
        lines.append(f"- **Countries with China Analysis:** {len(self.stats['countries_with_analysis'])} ({', '.join(sorted(self.stats['countries_with_analysis']))})")
        lines.append(f"- **Data Sources Covered:** {', '.join(sorted(self.stats['data_sources']))}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Core China Analysis Files
        lines.append("## 🌐 Core China Analysis Files")
        lines.append("Location: `analysis/china_footprint/`")
        lines.append("")

        for category in sorted(self.china_files.keys()):
            lines.append(f"### {category}")
            for file_info in sorted(self.china_files[category], key=lambda x: x['file']):
                lines.append(f"- `{Path(file_info['file']).name}` - {file_info['description']}")
                if file_info['size'] > 1024 * 1024:  # If larger than 1MB
                    size_mb = file_info['size'] / (1024 * 1024)
                    lines.append(f"  - Size: {size_mb:.1f}MB | Modified: {file_info['modified']}")
            lines.append("")

        lines.append("---")
        lines.append("")

        # Country-Specific Analysis
        lines.append("## 🌍 Country-Specific China Analysis")
        lines.append("")

        country_flags = {
            'Germany': '🇩🇪',
            'Italy': '🇮🇹',
            'Greece': '🇬🇷',
            'France': '🇫🇷',
            'Spain': '🇪🇸',
            'Poland': '🇵🇱',
            'Hungary': '🇭🇺',
            'Portugal': '🇵🇹',
            'Czech': '🇨🇿'
        }

        for country in sorted(self.country_analyses.keys()):
            flag = country_flags.get(country, '🌍')
            lines.append(f"### {flag} {country}")
            lines.append(f"Location: `countries/{country}/china_analysis/`")

            for file_info in self.country_analyses[country]:
                lines.append(f"- `{Path(file_info['file']).name}` - {file_info['description']}")
                lines.append(f"  - Path: `{file_info['file']}`")
                lines.append(f"  - Modified: {file_info['modified']}")
            lines.append("")

        # Quick Access Commands
        lines.append("---")
        lines.append("")
        lines.append("## 🚀 Quick Access Commands")
        lines.append("")
        lines.append("### Find all China files:")
        lines.append("```bash")
        lines.append("# Find all China-related files")
        lines.append('find . -iname "*china*" -type f')
        lines.append("")
        lines.append("# Count China analysis files by type")
        lines.append('find . -iname "*china*" -type f | sed \'s/.*\\.//\' | sort | uniq -c')
        lines.append("```")
        lines.append("")

        lines.append("### Generate China analysis report:")
        lines.append("```bash")
        lines.append("python scripts/generate_china_footprint_report.py --all-sources")
        lines.append("```")
        lines.append("")

        lines.append("### Update this index manually:")
        lines.append("```bash")
        lines.append("python scripts/update_china_index.py --force")
        lines.append("```")
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("## 🔗 Related Documents")
        lines.append("- [China Footprint Analysis Framework](../../docs/prompts/china_footprint_analysis.md)")
        lines.append("- [Master README](../../README.md)")
        lines.append("- [Project Organization Plan](../../PROJECT_ORGANIZATION_PLAN.md)")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*This index is automatically maintained. Manual edits will be overwritten during the next update cycle.*")

        return '\n'.join(lines)

    def save_index(self, output_path: str = "analysis/china_footprint/CHINA_ANALYSIS_INDEX.md") -> None:
        """Save the generated index to file."""
        output_file = self.project_root / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

        index_content = self.generate_index()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

        print(f"[SUCCESS] China Analysis Index updated: {output_file}")
        print(f"Statistics:")
        print(f"   - Total files: {self.stats['total_files']}")
        print(f"   - Countries: {len(self.stats['countries_with_analysis'])}")
        print(f"   - Data sources: {len(self.stats['data_sources'])}")


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description='Update China Analysis Index')
    parser.add_argument('--root', default='.', help='Project root directory')
    parser.add_argument('--output', default='analysis/china_footprint/CHINA_ANALYSIS_INDEX.md',
                       help='Output file path')
    parser.add_argument('--force', action='store_true', help='Force update even if recently updated')

    args = parser.parse_args()

    updater = ChinaIndexUpdater(args.root)
    updater.find_china_files()
    updater.save_index(args.output)

    print("[SUCCESS] China Analysis Index successfully updated!")


if __name__ == "__main__":
    main()
