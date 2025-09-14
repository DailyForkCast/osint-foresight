#!/usr/bin/env python3
"""
Initialize F: drive structure for OSINT data collection
Creates all necessary directories and initial configuration
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

def initialize_f_drive():
    """Set up F: drive for OSINT data collection"""

    print("=" * 60)
    print("OSINT FORESIGHT - F: DRIVE INITIALIZATION")
    print("=" * 60)

    base_dir = Path('F:/OSINT_Data')

    # All 44 countries
    countries = [
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
        'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
        'SI', 'ES', 'SE', 'IS', 'NO', 'CH', 'AL', 'BA', 'XK', 'ME', 'MK', 'RS',
        'TR', 'MD', 'UA', 'GB', 'AM', 'AZ', 'GE'
    ]

    # Data sources
    sources = [
        'crossref', 'crossref_events', 'worldbank', 'oecd', 'eurostat',
        'cordis', 'ted', 'gleif', 'ietf', 'patents', 'openaire',
        'commoncrawl', 'vessel_tracking', 'procurement', 'national_stats'
    ]

    print(f"\nTarget directory: {base_dir}")
    print(f"Countries: {len(countries)}")
    print(f"Data sources: {len(sources)}")

    # Create main structure
    print("\nCreating directory structure...")

    directories = {
        'raw': 'Raw data from sources',
        'processed': 'Cleaned and normalized data',
        'analysis': 'Analysis results',
        'reports': 'Generated reports',
        'logs': 'Pull and processing logs',
        'backups': 'Data backups',
        'common_crawl': 'Common Crawl data (large)',
        'openalex': 'OpenAlex snapshot (300GB)',
        'cache': 'Temporary cache',
        'config': 'Configuration files'
    }

    for dir_name, description in directories.items():
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_name:15} - {description}")

    # Create country-specific directories
    print("\nCreating country directories...")

    for country in countries:
        # Raw data directories
        for source in sources:
            path = base_dir / 'raw' / f'country={country}' / f'source={source}'
            path.mkdir(parents=True, exist_ok=True)

        # Processed data directories
        proc_path = base_dir / 'processed' / f'country={country}'
        proc_path.mkdir(parents=True, exist_ok=True)

        # Reports directory
        report_path = base_dir / 'reports' / f'country={country}'
        report_path.mkdir(parents=True, exist_ok=True)

        print(f"  ✓ {country} directories created")

    # Create configuration file
    print("\nCreating configuration...")

    config = {
        'initialized': datetime.now().isoformat(),
        'version': '1.0',
        'countries': countries,
        'sources': sources,
        'storage': {
            'base_path': str(base_dir),
            'backup_path': 'F:/OSINT_Backups',
            'max_size_gb': 2000
        },
        'schedule': {
            'daily': ['vessel_tracking'],
            'weekly': ['crossref', 'crossref_events', 'patents'],
            'monthly': ['worldbank', 'oecd', 'eurostat', 'cordis', 'ted', 'gleif'],
            'quarterly': ['commoncrawl'],
            'yearly': ['openalex']
        }
    }

    config_file = base_dir / 'config' / 'master_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"  ✓ Configuration saved to {config_file}")

    # Create initial state file
    state = {
        'last_pulls': {},
        'pull_history': [],
        'errors': [],
        'statistics': {
            'total_pulls': 0,
            'successful_pulls': 0,
            'failed_pulls': 0,
            'total_data_gb': 0
        }
    }

    state_file = base_dir / 'orchestrator_state.json'
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    print(f"  ✓ State file created at {state_file}")

    # Create README
    readme_content = f"""# OSINT Foresight Data Repository

## Overview
This directory contains all data collected for the OSINT Foresight project.

## Structure
- **raw/**: Raw data as collected from sources
- **processed/**: Cleaned and normalized data
- **analysis/**: Analysis results and intermediate files
- **reports/**: Generated reports by country
- **logs/**: Pull and processing logs
- **common_crawl/**: Common Crawl intelligence data
- **openalex/**: OpenAlex research data snapshot

## Countries
Total: {len(countries)} countries
{', '.join(countries)}

## Data Sources
Total: {len(sources)} sources
{', '.join(sources)}

## Storage Information
- Location: F:/OSINT_Data
- Backup: F:/OSINT_Backups
- Max Size: 2TB
- Initialized: {datetime.now().isoformat()}

## Automated Schedule
- **Daily**: Vessel tracking, news monitoring
- **Weekly**: Publications, patents, events
- **Monthly**: Economic indicators, procurement, statistics
- **Quarterly**: Common Crawl intelligence extraction
- **Yearly**: OpenAlex snapshot update

## Usage
Run status check:
```
python src/pulls/master_pull_orchestrator.py --mode status
```

Run manual pull:
```
python src/pulls/master_pull_orchestrator.py --source worldbank --country AT
```

## Contact
Project: OSINT Foresight
Updated: {datetime.now().strftime('%Y-%m-%d')}
"""

    readme_file = base_dir / 'README.md'
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print(f"  ✓ README created at {readme_file}")

    # Calculate storage requirements
    print("\n" + "=" * 60)
    print("STORAGE REQUIREMENTS ESTIMATE")
    print("=" * 60)

    estimates = {
        'Per country per month': '2-5 GB',
        'All countries per month': '100-200 GB',
        'Common Crawl quarterly': '50-100 GB',
        'OpenAlex snapshot': '300 GB',
        'First year estimate': '1.5-2 TB',
        'Recommended space': '2-3 TB'
    }

    for item, size in estimates.items():
        print(f"  {item:25} : {size}")

    # Check available space
    try:
        usage = shutil.disk_usage('F:/')
        total_gb = usage.total / (1024**3)
        free_gb = usage.free / (1024**3)
        used_pct = (usage.used / usage.total) * 100

        print(f"\nF: Drive Status:")
        print(f"  Total: {total_gb:.1f} GB")
        print(f"  Free:  {free_gb:.1f} GB")
        print(f"  Used:  {used_pct:.1f}%")

        if free_gb < 2000:
            print(f"\n⚠ Warning: Only {free_gb:.1f} GB free. Recommended: 2000+ GB")
    except:
        print("\n⚠ Could not check F: drive space")

    print("\n" + "=" * 60)
    print("INITIALIZATION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run test pull: python src/pulls/worldbank_pull.py --country AT")
    print("2. Set up scheduler: Run scheduled_tasks/setup_automated_pulls.bat as Admin")
    print("3. Start collection: python src/pulls/master_pull_orchestrator.py --mode once")
    print("4. Monitor: python src/pulls/master_pull_orchestrator.py --mode status")

if __name__ == '__main__':
    initialize_f_drive()
