#!/usr/bin/env python3
"""
Analyze current project structure and identify organizational issues
"""

import os
from pathlib import Path
from collections import defaultdict
import json

def analyze_project():
    """Analyze the current project structure"""
    
    root = Path.cwd()
    
    # Categories for files
    categories = {
        'analysis_scripts': [],
        'setup_scripts': [],
        'data_tools': [],
        'documentation': [],
        'config_files': [],
        'temp_files': [],
        'reports': [],
        'misplaced_outputs': []
    }
    
    # File patterns
    patterns = {
        'analysis_scripts': ['analyze_*.py', '*_analysis.py'],
        'setup_scripts': ['setup_*.py', 'create_*.py', 'configure_*.py'],
        'data_tools': ['load_*.py', '*_loader.py', 'quick_*.py'],
        'documentation': ['*.md', '!README.md'],
        'config_files': ['*.yaml', '*.yml', '*.json', '!package*.json'],
        'temp_files': ['~$*', '*.tmp', '*.bak'],
        'reports': ['*.docx', '*.xlsx', '*.pptx'],
        'backup_tools': ['*backup*.py', '*backup*.bat']
    }
    
    # Scan root directory
    root_files = []
    for item in root.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            root_files.append(item)
            
            # Categorize file
            categorized = False
            for category, pats in patterns.items():
                for pattern in pats:
                    if pattern.startswith('!'):
                        # Exclusion pattern
                        continue
                    if pattern.startswith('*'):
                        if item.name.endswith(pattern[1:]):
                            categories[category].append(item.name)
                            categorized = True
                            break
                    elif pattern.endswith('*'):
                        if item.name.startswith(pattern[:-1]):
                            categories[category].append(item.name)
                            categorized = True
                            break
                    elif '*' in pattern:
                        # Handle wildcards in middle
                        parts = pattern.split('*')
                        if item.name.startswith(parts[0]) and item.name.endswith(parts[1]):
                            categories[category].append(item.name)
                            categorized = True
                            break
                            
            if not categorized and item.suffix == '.py':
                categories['analysis_scripts'].append(item.name)
                
    # Analyze directory structure
    dirs = {}
    for item in root.rglob('*'):
        if item.is_dir() and not any(part.startswith('.') for part in item.parts):
            level = len(item.relative_to(root).parts)
            if level <= 2:
                dirs[str(item.relative_to(root))] = {
                    'level': level,
                    'file_count': len(list(item.glob('*.*'))),
                    'has_init': (item / '__init__.py').exists() if item.suffix != '' else False
                }
                
    # Generate report
    report = {
        'summary': {
            'total_root_files': len(root_files),
            'python_files': len([f for f in root_files if f.suffix == '.py']),
            'doc_files': len([f for f in root_files if f.suffix == '.md']),
            'config_files': len([f for f in root_files if f.suffix in ['.yaml', '.yml', '.json']]),
            'output_files': len([f for f in root_files if f.suffix in ['.docx', '.xlsx', '.pptx']])
        },
        'categorized_files': categories,
        'directory_structure': dirs,
        'issues': [],
        'recommendations': []
    }
    
    # Identify issues
    if report['summary']['total_root_files'] > 10:
        report['issues'].append(f"Root directory has {report['summary']['total_root_files']} files (should be <10)")
        
    if report['summary']['python_files'] > 3:
        report['issues'].append(f"Root has {report['summary']['python_files']} Python scripts (should be organized in subdirs)")
        
    if categories['temp_files']:
        report['issues'].append(f"Temporary files found: {categories['temp_files']}")
        
    if categories['misplaced_outputs']:
        report['issues'].append(f"Output files in root: {categories['misplaced_outputs']}")
        
    # Add recommendations
    if categories['analysis_scripts']:
        report['recommendations'].append(f"Move {len(categories['analysis_scripts'])} analysis scripts to scripts/analysis/")
        
    if categories['setup_scripts']:
        report['recommendations'].append(f"Move {len(categories['setup_scripts'])} setup scripts to scripts/setup/")
        
    if categories['data_tools']:
        report['recommendations'].append(f"Move {len(categories['data_tools'])} data tools to tools/data_loaders/")
        
    if not Path('scripts').exists():
        report['recommendations'].append("Create scripts/ directory for standalone scripts")
        
    if not Path('tools').exists():
        report['recommendations'].append("Create tools/ directory for development tools")
        
    if not Path('.gitignore').exists():
        report['recommendations'].append("Create .gitignore file to exclude temporary files")
        
    return report


def print_report(report):
    """Print the analysis report"""
    
    print("=" * 60)
    print("PROJECT STRUCTURE ANALYSIS REPORT")
    print("=" * 60)
    
    print("\n[SUMMARY]")
    print("-" * 40)
    for key, value in report['summary'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
        
    print("\n[ISSUES FOUND]")
    print("-" * 40)
    if report['issues']:
        for i, issue in enumerate(report['issues'], 1):
            print(f"  {i}. {issue}")
    else:
        print("  No major issues found")
        
    print("\n[RECOMMENDATIONS]")
    print("-" * 40)
    if report['recommendations']:
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    else:
        print("  Structure looks good")
        
    print("\n[FILES BY CATEGORY]")
    print("-" * 40)
    for category, files in report['categorized_files'].items():
        if files:
            print(f"\n  {category.replace('_', ' ').title()} ({len(files)} files):")
            for file in files[:5]:  # Show first 5
                print(f"    - {file}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")
                
    print("\n[KEY DIRECTORIES]")
    print("-" * 40)
    for dir_path, info in sorted(report['directory_structure'].items())[:10]:
        indent = "  " * info['level']
        print(f"{indent}{dir_path}/ ({info['file_count']} files)")
        
    print("\n" + "=" * 60)
    
    # Save report to JSON
    with open('project_structure_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    print("\nFull report saved to: project_structure_analysis.json")
    

def main():
    report = analyze_project()
    print_report(report)
    
    # Return exit code based on issues
    return 0 if not report['issues'] else 1


if __name__ == "__main__":
    exit(main())