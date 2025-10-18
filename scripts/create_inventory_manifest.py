#!/usr/bin/env python3
"""
Phase 0: Create Canonical Inventory Manifest
Generates a comprehensive inventory of all datasets with sizes, counts, and provenance
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime
import sqlite3
import gzip
import zipfile

def get_file_hash(filepath, first_kb=2048):
    """Get hash of first 2KB for large files"""
    try:
        with open(filepath, 'rb') as f:
            data = f.read(first_kb)
            return hashlib.sha256(data).hexdigest()
    except:
        return None

def analyze_database(db_path):
    """Analyze SQLite database structure and row counts"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        db_info = {
            'type': 'sqlite',
            'tables': {}
        }

        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]

            # Get schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            db_info['tables'][table_name] = {
                'row_count': count,
                'columns': [col[1] for col in columns]
            }

        conn.close()
        return db_info
    except Exception as e:
        return {'error': str(e)}

def analyze_file(filepath):
    """Analyze a single file and return metadata"""
    path = Path(filepath)
    stat = path.stat()

    info = {
        'path': str(path),
        'size_bytes': stat.st_size,
        'size_human': format_size(stat.st_size),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'extension': path.suffix.lower(),
        'hash_2kb': get_file_hash(filepath)
    }

    # Special handling for databases
    if path.suffix.lower() == '.db':
        info['database_info'] = analyze_database(filepath)

    # Special handling for compressed files
    if path.suffix.lower() in ['.gz', '.zip']:
        info['compressed'] = True
        if path.suffix.lower() == '.gz':
            try:
                with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline()
                    info['first_line_sample'] = first_line[:200]
            except:
                pass

    return info

def format_size(bytes):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"

def scan_directory(base_path, patterns=['*.json', '*.csv', '*.tsv', '*.db', '*.xml', '*.gz', '*.zip']):
    """Scan directory for data files"""
    base = Path(base_path)
    files_info = []
    total_size = 0

    for pattern in patterns:
        for filepath in base.rglob(pattern):
            if filepath.is_file():
                try:
                    file_info = analyze_file(filepath)
                    files_info.append(file_info)
                    total_size += file_info['size_bytes']
                except Exception as e:
                    print(f"Error analyzing {filepath}: {e}")

    return files_info, total_size

def main():
    """Create comprehensive inventory manifest"""

    manifest = {
        'generated': datetime.now().isoformat(),
        'version': '1.0',
        'datasets': {},
        'summary': {
            'total_size_bytes': 0,
            'total_size_human': '',
            'total_files': 0,
            'by_type': {}
        },
        'provenance': {
            'local_files': [],
            'online_sources': []
        }
    }

    # Scan main project data directory
    print("Scanning C:/Projects/OSINT - Foresight/data/...")
    project_files, project_size = scan_directory("C:/Projects/OSINT - Foresight/data/")
    manifest['datasets']['project_data'] = {
        'path': 'C:/Projects/OSINT - Foresight/data/',
        'files': project_files,
        'total_size': project_size,
        'total_size_human': format_size(project_size),
        'file_count': len(project_files)
    }

    # Scan F:/OSINT_DATA
    print("Scanning F:/OSINT_DATA/...")
    osint_files, osint_size = scan_directory("F:/OSINT_DATA/")
    manifest['datasets']['osint_data'] = {
        'path': 'F:/OSINT_DATA/',
        'files': osint_files,
        'total_size': osint_size,
        'total_size_human': format_size(osint_size),
        'file_count': len(osint_files)
    }

    # Scan F:/TED_Data
    print("Scanning F:/TED_Data/...")
    ted_files, ted_size = scan_directory("F:/TED_Data/")
    manifest['datasets']['ted_data'] = {
        'path': 'F:/TED_Data/',
        'files': ted_files,
        'total_size': ted_size,
        'total_size_human': format_size(ted_size),
        'file_count': len(ted_files)
    }

    # Scan F:/OSINT_Backups (sample only due to size)
    print("Sampling F:/OSINT_Backups/...")
    backup_path = Path("F:/OSINT_Backups/")
    if backup_path.exists():
        # Just get top-level stats
        total_backup_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
        manifest['datasets']['osint_backups'] = {
            'path': 'F:/OSINT_Backups/',
            'total_size': total_backup_size,
            'total_size_human': format_size(total_backup_size),
            'note': 'Size calculated, detailed file listing omitted due to volume'
        }

    # Calculate totals
    all_files = project_files + osint_files + ted_files
    manifest['summary']['total_files'] = len(all_files)
    manifest['summary']['total_size_bytes'] = project_size + osint_size + ted_size
    manifest['summary']['total_size_human'] = format_size(manifest['summary']['total_size_bytes'])

    # Count by type
    for file_info in all_files:
        ext = file_info['extension']
        if ext not in manifest['summary']['by_type']:
            manifest['summary']['by_type'][ext] = {'count': 0, 'total_size': 0}
        manifest['summary']['by_type'][ext]['count'] += 1
        manifest['summary']['by_type'][ext]['total_size'] += file_info['size_bytes']

    # Add online source provenance (these don't have SHA256 but have URLs)
    manifest['provenance']['online_sources'] = [
        {
            'name': 'OpenAIRE API',
            'base_url': 'https://api.openaire.eu/search/',
            'last_accessed': '2025-09-22',
            'data_types': ['publications', 'datasets', 'software', 'projects']
        },
        {
            'name': 'CORDIS EU',
            'base_url': 'https://cordis.europa.eu/datalab/datalab.php',
            'last_accessed': '2025-09-21',
            'data_types': ['projects', 'results', 'reports']
        },
        {
            'name': 'OpenAlex API',
            'base_url': 'https://api.openalex.org/',
            'last_accessed': '2025-09-23',
            'data_types': ['works', 'authors', 'institutions', 'concepts']
        },
        {
            'name': 'TED Europa',
            'base_url': 'https://ted.europa.eu/',
            'last_accessed': '2025-09-23',
            'data_types': ['tenders', 'contracts', 'notices']
        }
    ]

    # Save manifest
    output_path = "C:/Projects/OSINT - Foresight/inventory_manifest.json"
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\nInventory manifest created: {output_path}")
    print(f"Total files: {manifest['summary']['total_files']}")
    print(f"Total size: {manifest['summary']['total_size_human']}")

    # Create verification samples
    print("\nCreating verification samples...")
    samples = []
    for dataset_name, dataset_info in manifest['datasets'].items():
        if 'files' in dataset_info and dataset_info['files']:
            # Take 3 random samples from each dataset
            import random
            sample_files = random.sample(dataset_info['files'], min(3, len(dataset_info['files'])))
            for f in sample_files:
                samples.append({
                    'dataset': dataset_name,
                    'path': f['path'],
                    'size': f['size_human'],
                    'hash_2kb': f.get('hash_2kb', 'N/A')
                })

    with open("C:/Projects/OSINT - Foresight/inventory_samples.json", 'w') as f:
        json.dump(samples, f, indent=2)

    print(f"Verification samples created: inventory_samples.json")

    return manifest

if __name__ == "__main__":
    manifest = main()
