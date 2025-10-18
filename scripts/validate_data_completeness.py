#!/usr/bin/env python3
"""
Comprehensive Data Validation Script
Verifies that all data has been properly extracted and processed
"""

import os
import gzip
import tarfile
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib

class DataCompletenessValidator:
    """Validate that all data sources have been properly processed"""
    
    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'openalex': {},
            'ted': {},
            'openaire': {},
            'usaspending': {},
            'issues_found': [],
            'recommendations': []
        }
    
    def validate_openalex(self):
        """Validate OpenAlex data extraction"""
        print("\n" + "="*60)
        print("VALIDATING OPENALEX DATA")
        print("="*60)
        
        openalex_dir = Path("F:/OSINT_Backups/openalex/data/works")
        
        # Count total .gz files
        gz_files = list(openalex_dir.rglob("*.gz"))
        print(f"Found {len(gz_files)} .gz files in OpenAlex")
        
        # Sample some files to check structure
        sample_count = min(5, len(gz_files))
        total_records = 0
        file_sizes = []
        
        print("\nSampling files to check structure:")
        for i, gz_file in enumerate(gz_files[:sample_count]):
            file_size = gz_file.stat().st_size
            file_sizes.append(file_size)
            
            try:
                with gzip.open(gz_file, 'rt') as f:
                    # Each line is a JSON record
                    record_count = 0
                    for line in f:
                        if line.strip():
                            record_count += 1
                            if record_count == 1:
                                # Check first record structure
                                data = json.loads(line)
                                if 'id' not in data or 'display_name' not in data:
                                    self.validation_results['issues_found'].append(
                                        f"OpenAlex file {gz_file.name} has unexpected structure"
                                    )
                    
                    total_records += record_count
                    print(f"  {gz_file.parent.name}/{gz_file.name}: {file_size:,} bytes, {record_count:,} records")
                    
            except Exception as e:
                print(f"  ERROR reading {gz_file.name}: {e}")
                self.validation_results['issues_found'].append(
                    f"Cannot read OpenAlex file {gz_file.name}: {e}"
                )
        
        avg_size = sum(file_sizes) / len(file_sizes) if file_sizes else 0
        estimated_total = (avg_size * len(gz_files)) / (1024**3)  # GB
        
        self.validation_results['openalex'] = {
            'total_files': len(gz_files),
            'sampled_files': sample_count,
            'sample_records': total_records,
            'average_file_size': avg_size,
            'estimated_total_size_gb': estimated_total
        }
        
        print(f"\nEstimated total OpenAlex size: {estimated_total:.2f} GB")
        
        # Check database for processed records
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE name LIKE 'openalex%'")
            table_count = cursor.fetchone()[0]
            print(f"OpenAlex tables in database: {table_count}")
            
            if table_count == 0:
                self.validation_results['issues_found'].append(
                    "No OpenAlex data found in database - needs processing"
                )
                self.validation_results['recommendations'].append(
                    "Process OpenAlex data using proper extraction script"
                )
        except Exception as e:
            print(f"Database check error: {e}")
        
        conn.close()
        
        # Key finding
        if avg_size < 100000:  # Less than 100KB average
            print("\n[WARNING] OpenAlex files are very small!")
            print("This appears to be a SAMPLE dataset, not the full OpenAlex dump.")
            self.validation_results['issues_found'].append(
                "OpenAlex files are too small - likely sample data only"
            )
            self.validation_results['recommendations'].append(
                "Download full OpenAlex dataset from https://openalex.org/data/download"
            )
    
    def validate_ted(self):
        """Validate TED data extraction"""
        print("\n" + "="*60)
        print("VALIDATING TED DATA")
        print("="*60)
        
        ted_dir = Path("F:/TED_Data/monthly")
        
        # Find all tar.gz files
        tar_files = list(ted_dir.rglob("*.tar.gz"))
        print(f"Found {len(tar_files)} tar.gz files in TED")
        
        # Check for double-wrapping
        double_wrapped = []
        extracted_count = 0
        
        print("\nChecking for double-wrapped archives:")
        for tar_file in tar_files[:5]:  # Sample first 5
            try:
                with tarfile.open(tar_file, 'r:gz') as tar:
                    members = tar.getmembers()
                    for member in members[:5]:  # Check first 5 members
                        if member.name.endswith('.tar.gz'):
                            double_wrapped.append(tar_file)
                            print(f"  [DOUBLE-WRAPPED] {tar_file.name} contains {member.name}")
                            break
                        elif member.name.endswith('.csv'):
                            extracted_count += 1
                            print(f"  [EXTRACTED] {tar_file.name} contains CSV files")
                            break
            except Exception as e:
                print(f"  ERROR reading {tar_file.name}: {e}")
        
        self.validation_results['ted'] = {
            'total_archives': len(tar_files),
            'double_wrapped_count': len(double_wrapped),
            'needs_extraction': len(double_wrapped) > 0
        }
        
        if double_wrapped:
            print(f"\n[CRITICAL] Found {len(double_wrapped)} double-wrapped TED archives!")
            self.validation_results['issues_found'].append(
                f"TED data has {len(double_wrapped)} double-wrapped tar.gz files"
            )
            self.validation_results['recommendations'].append(
                "Extract nested tar.gz files from TED archives before processing"
            )
        
        # Check CSV extraction
        csv_dir = Path("F:/TED_Data/csv_historical")
        if csv_dir.exists():
            csv_files = list(csv_dir.rglob("*.csv"))
            print(f"\nFound {len(csv_files)} extracted CSV files")
            
            if csv_files:
                total_size = sum(f.stat().st_size for f in csv_files) / (1024**3)
                print(f"Total CSV size: {total_size:.2f} GB")
        else:
            print("\n[WARNING] No csv_historical directory found")
            self.validation_results['issues_found'].append(
                "TED CSV files not extracted to csv_historical directory"
            )
    
    def check_database_completeness(self):
        """Check what's actually in the database"""
        print("\n" + "="*60)
        print("DATABASE COMPLETENESS CHECK")
        print("="*60)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all tables and their record counts
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        
        print("\nKey table record counts:")
        key_tables = [
            ('china_entities', 'China entities'),
            ('ted_china_contracts', 'TED China contracts'),
            ('cordis_china_collaborations', 'CORDIS collaborations'),
            ('openalex_institutions', 'OpenAlex institutions'),
            ('sec_edgar_companies', 'SEC EDGAR companies'),
            ('patents', 'Patents')
        ]
        
        for table_name, description in key_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  {description:<30}: {count:>10,}")
                
                if count == 0:
                    self.validation_results['issues_found'].append(
                        f"Table {table_name} is empty"
                    )
            except sqlite3.OperationalError:
                print(f"  {description:<30}: [TABLE NOT FOUND]")
                self.validation_results['issues_found'].append(
                    f"Table {table_name} does not exist"
                )
        
        conn.close()
    
    def generate_report(self):
        """Generate validation report"""
        report = f"""
# Data Completeness Validation Report
Generated: {self.validation_results['timestamp']}

## Executive Summary

### Issues Found: {len(self.validation_results['issues_found'])}
"""
        
        if self.validation_results['issues_found']:
            report += "\n**Critical Issues:**\n"
            for issue in self.validation_results['issues_found']:
                report += f"- {issue}\n"
        else:
            report += "No critical issues found.\n"
        
        report += """
## OpenAlex Validation
"""
        openalex = self.validation_results['openalex']
        if openalex:
            report += f"""
- Total files: {openalex.get('total_files', 0)}
- Estimated size: {openalex.get('estimated_total_size_gb', 0):.2f} GB
- Sample records: {openalex.get('sample_records', 0):,}

**Assessment**: 
"""
            if openalex.get('estimated_total_size_gb', 0) < 10:
                report += "This appears to be a SAMPLE dataset, not the full OpenAlex dump (which is ~300GB).\n"
            else:
                report += "Full dataset appears to be present.\n"
        
        report += """
## TED Validation
"""
        ted = self.validation_results['ted']
        if ted:
            report += f"""
- Total archives: {ted.get('total_archives', 0)}
- Double-wrapped files: {ted.get('double_wrapped_count', 0)}
- Needs extraction: {ted.get('needs_extraction', False)}

**Assessment**: 
"""
            if ted.get('needs_extraction'):
                report += "TED files are double-wrapped (tar.gz containing tar.gz). Extraction required!\n"
            else:
                report += "TED files appear properly extracted.\n"
        
        report += """
## Recommendations

### Immediate Actions Required:
"""
        
        if self.validation_results['recommendations']:
            for i, rec in enumerate(self.validation_results['recommendations'], 1):
                report += f"{i}. {rec}\n"
        else:
            report += "No immediate actions required.\n"
        
        report += """
### Next Steps:

1. **OpenAlex**: 
   - If using sample data, download full dataset from https://openalex.org/data/download
   - Full dataset is ~300GB compressed, ~1TB uncompressed
   - Process incrementally using checkpoint system

2. **TED**:
   - Extract double-wrapped tar.gz files
   - Process CSV files for China entity detection
   - Focus on recent years (2020-2024) first

3. **Verification**:
   - Run spot checks on extracted data
   - Verify China entity detection is working
   - Check for data currency (how recent is the data?)
"""
        
        return report
    
    def run(self):
        """Run complete validation"""
        print("="*60)
        print("DATA COMPLETENESS VALIDATION")
        print("="*60)
        
        self.validate_openalex()
        self.validate_ted()
        self.check_database_completeness()
        
        report = self.generate_report()
        
        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/DATA_VALIDATION_REPORT.md")
        report_path.write_text(report)
        
        print("\n" + "="*60)
        print("VALIDATION COMPLETE")
        print("="*60)
        
        print(f"\nIssues found: {len(self.validation_results['issues_found'])}")
        print(f"Report saved to: {report_path}")
        
        # Save JSON results
        json_path = Path("C:/Projects/OSINT - Foresight/analysis/data_validation_results.json")
        with open(json_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        return self.validation_results

if __name__ == "__main__":
    validator = DataCompletenessValidator()
    results = validator.run()
    
    if results['issues_found']:
        print("\n[ACTION REQUIRED] Critical issues need attention!")
        for issue in results['issues_found'][:3]:
            print(f"  - {issue}")
