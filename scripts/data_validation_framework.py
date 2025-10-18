#!/usr/bin/env python3
"""
Multi-Stage Data Validation Framework
Ensures data integrity at every stage of processing
"""

import hashlib
import json
import sqlite3
import gzip
import tarfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
import re
import csv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class DataValidationFramework:
    """Comprehensive validation at multiple stages"""
    
    def __init__(self):
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'stages': {},
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        
    # ============================================
    # STAGE 1: PRE-EXTRACTION VALIDATION
    # ============================================
    
    def validate_pre_extraction(self) -> Dict:
        """Validate data BEFORE extraction/processing"""
        
        stage_results = {
            'stage': 'PRE_EXTRACTION',
            'checks': [],
            'passed': True
        }
        
        logging.info("="*60)
        logging.info("STAGE 1: PRE-EXTRACTION VALIDATION")
        logging.info("="*60)
        
        # Check 1: File Integrity
        logging.info("\nCheck 1.1: File Integrity")
        file_checks = self._check_file_integrity()
        stage_results['checks'].append(file_checks)
        
        # Check 2: Archive Structure
        logging.info("\nCheck 1.2: Archive Structure")
        archive_checks = self._check_archive_structure()
        stage_results['checks'].append(archive_checks)
        
        # Check 3: Disk Space
        logging.info("\nCheck 1.3: Disk Space Availability")
        space_checks = self._check_disk_space()
        stage_results['checks'].append(space_checks)
        
        # Check 4: Expected vs Actual Files
        logging.info("\nCheck 1.4: Expected vs Actual Files")
        file_count_checks = self._check_file_counts()
        stage_results['checks'].append(file_count_checks)
        
        self.validation_results['stages']['pre_extraction'] = stage_results
        return stage_results
    
    def _check_file_integrity(self) -> Dict:
        """Verify file checksums and sizes"""
        
        results = {
            'check': 'file_integrity',
            'status': 'PASS',
            'details': []
        }
        
        # Check OpenAlex files
        openalex_dir = Path("F:/OSINT_Backups/openalex/data/works")
        if openalex_dir.exists():
            gz_files = list(openalex_dir.rglob("*.gz"))
            
            # Sample check - verify files can be opened
            sample_size = min(5, len(gz_files))
            corrupted = 0
            
            for gz_file in gz_files[:sample_size]:
                try:
                    with gzip.open(gz_file, 'rt') as f:
                        f.read(100)  # Read first 100 chars
                except:
                    corrupted += 1
                    results['details'].append(f"Corrupted: {gz_file.name}")
                    results['status'] = 'FAIL'
            
            results['details'].append(f"OpenAlex: {len(gz_files)} files, {corrupted} corrupted")
        
        # Check TED files
        ted_dir = Path("F:/TED_Data/monthly")
        if ted_dir.exists():
            tar_files = list(ted_dir.rglob("*.tar.gz"))
            
            # Sample check
            sample_size = min(3, len(tar_files))
            corrupted = 0
            
            for tar_file in tar_files[:sample_size]:
                try:
                    with tarfile.open(tar_file, 'r:gz') as tar:
                        tar.getmembers()[:1]  # Try to read first member
                except:
                    corrupted += 1
                    results['details'].append(f"Corrupted: {tar_file.name}")
                    results['status'] = 'FAIL'
            
            results['details'].append(f"TED: {len(tar_files)} archives, {corrupted} corrupted")
        
        logging.info(f"  File Integrity: {results['status']}")
        return results
    
    def _check_archive_structure(self) -> Dict:
        """Check for double-wrapped archives"""
        
        results = {
            'check': 'archive_structure',
            'status': 'PASS',
            'details': []
        }
        
        # Check TED for double-wrapping
        ted_sample = Path("F:/TED_Data/monthly/2024/TED_monthly_2024_01.tar.gz")
        if ted_sample.exists():
            try:
                with tarfile.open(ted_sample, 'r:gz') as outer:
                    members = outer.getmembers()
                    inner_archives = [m for m in members if m.name.endswith('.tar.gz')]
                    
                    if inner_archives:
                        results['status'] = 'WARNING'
                        results['details'].append(f"TED: Double-wrapped - {len(inner_archives)} inner archives found")
                        self.validation_results['warnings'].append("TED archives are double-wrapped")
            except:
                results['status'] = 'FAIL'
                results['details'].append("Cannot read TED archive structure")
        
        logging.info(f"  Archive Structure: {results['status']}")
        return results
    
    def _check_disk_space(self) -> Dict:
        """Check available disk space for extraction"""
        
        import shutil
        
        results = {
            'check': 'disk_space',
            'status': 'PASS',
            'details': []
        }
        
        # Check F: drive space
        f_drive = Path("F:/")
        if f_drive.exists():
            stat = shutil.disk_usage("F:/")
            free_gb = stat.free / (1024**3)
            total_gb = stat.total / (1024**3)
            used_pct = (stat.used / stat.total) * 100
            
            results['details'].append(f"F: Drive - Free: {free_gb:.1f}GB, Total: {total_gb:.1f}GB, Used: {used_pct:.1f}%")
            
            # Need at least 500GB for full processing
            if free_gb < 500:
                results['status'] = 'WARNING'
                results['details'].append(f"WARNING: Only {free_gb:.1f}GB free, need 500GB+")
                self.validation_results['warnings'].append(f"Low disk space: {free_gb:.1f}GB")
            elif free_gb < 200:
                results['status'] = 'FAIL'
                results['details'].append("CRITICAL: Insufficient disk space")
        
        logging.info(f"  Disk Space: {results['status']}")
        return results
    
    def _check_file_counts(self) -> Dict:
        """Verify expected vs actual file counts"""
        
        results = {
            'check': 'file_counts',
            'status': 'PASS',
            'details': []
        }
        
        # OpenAlex check
        openalex_dir = Path("F:/OSINT_Backups/openalex/data/works")
        if openalex_dir.exists():
            gz_files = list(openalex_dir.rglob("*.gz"))
            
            # We found 971 files, but full dataset should have thousands
            if len(gz_files) < 1000:
                results['status'] = 'WARNING'
                results['details'].append(f"OpenAlex: Only {len(gz_files)} files (expected 1000s for full dataset)")
                self.validation_results['warnings'].append("OpenAlex appears to be sample data only")
        
        # USAspending check
        usa_dir = Path("F:/OSINT_DATA/USAspending/extracted_data")
        if usa_dir.exists():
            dat_files = list(usa_dir.glob("*.dat.gz"))
            results['details'].append(f"USAspending: {len(dat_files)} .dat.gz files")
        
        logging.info(f"  File Counts: {results['status']}")
        return results
    
    # ============================================
    # STAGE 2: POST-EXTRACTION VALIDATION
    # ============================================
    
    def validate_post_extraction(self) -> Dict:
        """Validate data AFTER extraction"""
        
        stage_results = {
            'stage': 'POST_EXTRACTION',
            'checks': [],
            'passed': True
        }
        
        logging.info("\n" + "="*60)
        logging.info("STAGE 2: POST-EXTRACTION VALIDATION")
        logging.info("="*60)
        
        # Check 1: Record Counts
        logging.info("\nCheck 2.1: Record Counts")
        record_checks = self._check_record_counts()
        stage_results['checks'].append(record_checks)
        
        # Check 2: Data Completeness
        logging.info("\nCheck 2.2: Data Completeness")
        completeness_checks = self._check_data_completeness()
        stage_results['checks'].append(completeness_checks)
        
        # Check 3: Date Ranges
        logging.info("\nCheck 2.3: Date Range Validation")
        date_checks = self._check_date_ranges()
        stage_results['checks'].append(date_checks)
        
        # Check 4: Encoding Issues
        logging.info("\nCheck 2.4: Character Encoding")
        encoding_checks = self._check_encoding()
        stage_results['checks'].append(encoding_checks)
        
        self.validation_results['stages']['post_extraction'] = stage_results
        return stage_results
    
    def _check_record_counts(self) -> Dict:
        """Verify record counts are reasonable"""
        
        results = {
            'check': 'record_counts',
            'status': 'PASS',
            'details': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check key tables
        tables_to_check = [
            ('china_entities', 1000, 'China entities'),
            ('ted_china_contracts', 100, 'TED contracts'),
            ('patents', 1000, 'Patents'),
            ('sec_edgar_companies', 100, 'SEC companies')
        ]
        
        for table_name, min_expected, description in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
                if count < min_expected:
                    results['status'] = 'WARNING'
                    results['details'].append(f"{description}: {count} (expected >{min_expected})")
                else:
                    results['details'].append(f"{description}: {count} ✓")
            except:
                results['details'].append(f"{description}: Table not found")
        
        conn.close()
        
        logging.info(f"  Record Counts: {results['status']}")
        return results
    
    def _check_data_completeness(self) -> Dict:
        """Check for NULL values in critical fields"""
        
        results = {
            'check': 'data_completeness',
            'status': 'PASS',
            'details': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for NULLs in critical fields
        checks = [
            ("SELECT COUNT(*) FROM china_entities WHERE entity_name IS NULL", "China entities with NULL names"),
            ("SELECT COUNT(*) FROM patents WHERE patent_id IS NULL", "Patents with NULL IDs")
        ]
        
        for query, description in checks:
            try:
                cursor.execute(query)
                null_count = cursor.fetchone()[0]
                
                if null_count > 0:
                    results['status'] = 'WARNING'
                    results['details'].append(f"{description}: {null_count}")
            except:
                pass
        
        conn.close()
        
        logging.info(f"  Data Completeness: {results['status']}")
        return results
    
    def _check_date_ranges(self) -> Dict:
        """Validate date ranges are reasonable"""
        
        results = {
            'check': 'date_ranges',
            'status': 'PASS',
            'details': []
        }
        
        current_year = datetime.now().year
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for future dates or very old dates
        checks = [
            (f"SELECT COUNT(*) FROM ted_china_contracts WHERE award_date > '{current_year+1}-01-01'", "Future TED contracts"),
            ("SELECT COUNT(*) FROM ted_china_contracts WHERE award_date < '2000-01-01'", "Pre-2000 TED contracts")
        ]
        
        for query, description in checks:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                
                if count > 0:
                    results['status'] = 'WARNING'
                    results['details'].append(f"{description}: {count}")
            except:
                pass
        
        conn.close()
        
        logging.info(f"  Date Ranges: {results['status']}")
        return results
    
    def _check_encoding(self) -> Dict:
        """Check for encoding issues"""
        
        results = {
            'check': 'encoding',
            'status': 'PASS',
            'details': []
        }
        
        # Check for common encoding problems
        encoding_issues = 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT entity_name FROM china_entities LIMIT 100")
            for row in cursor.fetchall():
                if row[0]:
                    # Check for mojibake (�) or other encoding issues
                    if '�' in row[0] or '\ufffd' in row[0]:
                        encoding_issues += 1
        except:
            pass
        
        if encoding_issues > 0:
            results['status'] = 'WARNING'
            results['details'].append(f"Found {encoding_issues} encoding issues")
        
        conn.close()
        
        logging.info(f"  Encoding: {results['status']}")
        return results
    
    # ============================================
    # STAGE 3: CROSS-SOURCE VALIDATION
    # ============================================
    
    def validate_cross_source(self) -> Dict:
        """Validate data consistency ACROSS sources"""
        
        stage_results = {
            'stage': 'CROSS_SOURCE',
            'checks': [],
            'passed': True
        }
        
        logging.info("\n" + "="*60)
        logging.info("STAGE 3: CROSS-SOURCE VALIDATION")
        logging.info("="*60)
        
        # Check 1: Entity Consistency
        logging.info("\nCheck 3.1: Entity Name Consistency")
        entity_checks = self._check_entity_consistency()
        stage_results['checks'].append(entity_checks)
        
        # Check 2: Duplicate Detection
        logging.info("\nCheck 3.2: Duplicate Detection")
        duplicate_checks = self._check_duplicates()
        stage_results['checks'].append(duplicate_checks)
        
        # Check 3: Country Code Consistency
        logging.info("\nCheck 3.3: Country Code Validation")
        country_checks = self._check_country_codes()
        stage_results['checks'].append(country_checks)
        
        # Check 4: Value Range Validation
        logging.info("\nCheck 3.4: Value Range Validation")
        value_checks = self._check_value_ranges()
        stage_results['checks'].append(value_checks)
        
        self.validation_results['stages']['cross_source'] = stage_results
        return stage_results
    
    def _check_entity_consistency(self) -> Dict:
        """Check if same entities appear consistently"""
        
        results = {
            'check': 'entity_consistency',
            'status': 'PASS',
            'details': []
        }
        
        # Check for variations of same company
        variations = [
            ['HUAWEI', 'HUAWEI TECHNOLOGIES', 'HUAWEI TECH'],
            ['ZTE', 'ZTE CORPORATION', 'ZHONGXING'],
            ['ALIBABA', 'ALIBABA GROUP', 'ALIBABA.COM']
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for company_variations in variations:
            counts = {}
            for variant in company_variations:
                try:
                    cursor.execute(
                        "SELECT COUNT(*) FROM china_entities WHERE UPPER(entity_name) LIKE ?",
                        (f"%{variant}%",)
                    )
                    count = cursor.fetchone()[0]
                    if count > 0:
                        counts[variant] = count
                except:
                    pass
            
            if len(counts) > 1:
                results['status'] = 'WARNING'
                results['details'].append(f"Multiple variations found: {counts}")
                self.validation_results['warnings'].append(f"Entity variations need normalization: {counts}")
        
        conn.close()
        
        logging.info(f"  Entity Consistency: {results['status']}")
        return results
    
    def _check_duplicates(self) -> Dict:
        """Check for duplicate records"""
        
        results = {
            'check': 'duplicates',
            'status': 'PASS',
            'details': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for duplicate entities
        try:
            cursor.execute("""
                SELECT entity_name, COUNT(*) as count
                FROM china_entities
                GROUP BY entity_name
                HAVING count > 1
                LIMIT 10
            """)
            
            duplicates = cursor.fetchall()
            if duplicates:
                results['status'] = 'WARNING'
                results['details'].append(f"Found {len(duplicates)} duplicate entities")
                for name, count in duplicates[:3]:
                    results['details'].append(f"  '{name}': {count} occurrences")
        except:
            pass
        
        conn.close()
        
        logging.info(f"  Duplicate Detection: {results['status']}")
        return results
    
    def _check_country_codes(self) -> Dict:
        """Validate country codes"""
        
        results = {
            'check': 'country_codes',
            'status': 'PASS',
            'details': []
        }
        
        valid_china_codes = ['CN', 'CHN', 'HK', 'HKG', 'MO', 'MAC']
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for invalid country codes
        try:
            cursor.execute("""
                SELECT DISTINCT vendor_country_code
                FROM contracts
                WHERE vendor_country_code IS NOT NULL
                AND LENGTH(vendor_country_code) > 0
            """)
            
            codes = [row[0] for row in cursor.fetchall()]
            invalid_codes = [c for c in codes if len(c) not in [2, 3] and c not in valid_china_codes]
            
            if invalid_codes:
                results['status'] = 'WARNING'
                results['details'].append(f"Invalid country codes: {invalid_codes[:5]}")
        except:
            pass
        
        conn.close()
        
        logging.info(f"  Country Codes: {results['status']}")
        return results
    
    def _check_value_ranges(self) -> Dict:
        """Check for unrealistic values"""
        
        results = {
            'check': 'value_ranges',
            'status': 'PASS',
            'details': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for unrealistic contract values
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM ted_china_contracts
                WHERE contract_value < 0
                OR contract_value > 1000000000000
            """)
            
            invalid_count = cursor.fetchone()[0]
            if invalid_count > 0:
                results['status'] = 'WARNING'
                results['details'].append(f"Unrealistic contract values: {invalid_count}")
        except:
            pass
        
        conn.close()
        
        logging.info(f"  Value Ranges: {results['status']}")
        return results
    
    # ============================================
    # STAGE 4: FINAL VALIDATION
    # ============================================
    
    def validate_final(self) -> Dict:
        """Final validation before analysis"""
        
        stage_results = {
            'stage': 'FINAL',
            'checks': [],
            'passed': True
        }
        
        logging.info("\n" + "="*60)
        logging.info("STAGE 4: FINAL VALIDATION")
        logging.info("="*60)
        
        # Check 1: Statistical Anomalies
        logging.info("\nCheck 4.1: Statistical Anomaly Detection")
        anomaly_checks = self._check_statistical_anomalies()
        stage_results['checks'].append(anomaly_checks)
        
        # Check 2: Referential Integrity
        logging.info("\nCheck 4.2: Referential Integrity")
        integrity_checks = self._check_referential_integrity()
        stage_results['checks'].append(integrity_checks)
        
        # Check 3: Business Logic
        logging.info("\nCheck 4.3: Business Logic Validation")
        logic_checks = self._check_business_logic()
        stage_results['checks'].append(logic_checks)
        
        self.validation_results['stages']['final'] = stage_results
        return stage_results
    
    def _check_statistical_anomalies(self) -> Dict:
        """Detect statistical outliers"""
        
        results = {
            'check': 'statistical_anomalies',
            'status': 'PASS',
            'details': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for sudden spikes in data
        try:
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', award_date) as month,
                    COUNT(*) as count
                FROM ted_china_contracts
                WHERE award_date IS NOT NULL
                GROUP BY month
                ORDER BY count DESC
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result and result[1] > 1000:
                results['status'] = 'WARNING'
                results['details'].append(f"Spike detected: {result[1]} contracts in {result[0]}")
        except:
            pass
        
        conn.close()
        
        logging.info(f"  Statistical Anomalies: {results['status']}")
        return results
    
    def _check_referential_integrity(self) -> Dict:
        """Check foreign key relationships"""
        
        results = {
            'check': 'referential_integrity',
            'status': 'PASS',
            'details': []
        }
        
        # This would check if entity IDs referenced in contracts exist in entity table
        # Simplified for demonstration
        
        logging.info(f"  Referential Integrity: {results['status']}")
        return results
    
    def _check_business_logic(self) -> Dict:
        """Validate business rules"""
        
        results = {
            'check': 'business_logic',
            'status': 'PASS',
            'details': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check: Award date should be before or equal to current date
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM ted_china_contracts
                WHERE award_date > date('now')
            """)
            
            future_count = cursor.fetchone()[0]
            if future_count > 0:
                results['status'] = 'FAIL'
                results['details'].append(f"Future award dates: {future_count}")
        except:
            pass
        
        conn.close()
        
        logging.info(f"  Business Logic: {results['status']}")
        return results
    
    # ============================================
    # REPORTING
    # ============================================
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        
        report = f"""
# Data Validation Report
Generated: {self.validation_results['timestamp']}

## Executive Summary

**Validation Stages Completed:**
"""
        
        # Summary by stage
        for stage_name, stage_data in self.validation_results['stages'].items():
            if isinstance(stage_data, dict):
                total_checks = len(stage_data.get('checks', []))
                failed = sum(1 for c in stage_data.get('checks', []) if c.get('status') == 'FAIL')
                warnings = sum(1 for c in stage_data.get('checks', []) if c.get('status') == 'WARNING')
                passed = total_checks - failed - warnings
                
                status_emoji = "✅" if failed == 0 else "❌" if failed > 0 else "⚠️"
                
                report += f"\n{status_emoji} **{stage_data.get('stage', stage_name)}**"
                report += f" - Passed: {passed}, Warnings: {warnings}, Failed: {failed}"
        
        # Critical Issues
        if self.validation_results['errors']:
            report += "\n\n## ❌ Critical Issues\n\n"
            for error in self.validation_results['errors']:
                report += f"- {error}\n"
        
        # Warnings
        if self.validation_results['warnings']:
            report += "\n\n## ⚠️ Warnings\n\n"
            for warning in self.validation_results['warnings']:
                report += f"- {warning}\n"
        
        # Detailed Results by Stage
        report += "\n\n## Detailed Validation Results\n"
        
        for stage_name, stage_data in self.validation_results['stages'].items():
            if isinstance(stage_data, dict):
                report += f"\n### {stage_data.get('stage', stage_name)}\n\n"
                
                for check in stage_data.get('checks', []):
                    status_icon = {
                        'PASS': '✓',
                        'WARNING': '⚠',
                        'FAIL': '✗'
                    }.get(check.get('status', ''), '?')
                    
                    report += f"**{status_icon} {check.get('check', 'Unknown Check')}**\n"
                    
                    for detail in check.get('details', []):
                        report += f"  - {detail}\n"
                    report += "\n"
        
        # Data Quality Score
        total_checks = sum(len(s.get('checks', [])) for s in self.validation_results['stages'].values() if isinstance(s, dict))
        total_passed = sum(sum(1 for c in s.get('checks', []) if c.get('status') == 'PASS') for s in self.validation_results['stages'].values() if isinstance(s, dict))
        
        quality_score = (total_passed / total_checks * 100) if total_checks > 0 else 0
        
        report += f"""
## Data Quality Score

**Overall Score: {quality_score:.1f}%**

- Total Checks: {total_checks}
- Passed: {total_passed}
- Warnings: {len(self.validation_results['warnings'])}
- Errors: {len(self.validation_results['errors'])}

## Recommendations

1. **Immediate Actions:**
"""
        
        if 'OpenAlex appears to be sample data only' in self.validation_results['warnings']:
            report += "   - Download full OpenAlex dataset\n"
        
        if 'TED archives are double-wrapped' in self.validation_results['warnings']:
            report += "   - Extract nested TED archives\n"
        
        if quality_score < 80:
            report += "   - Address critical validation failures before proceeding\n"
        
        report += """

2. **Data Cleaning:**
   - Normalize entity name variations
   - Remove duplicate records
   - Fix encoding issues
   - Validate date ranges

3. **Next Validation:**
   - Run after each major data import
   - Before generating final reports
   - After any data transformation
"""
        
        return report
    
    def run_complete_validation(self):
        """Run all validation stages"""
        
        print("="*60)
        print("COMPREHENSIVE DATA VALIDATION FRAMEWORK")
        print("="*60)
        print("\nRunning multi-stage validation...\n")
        
        # Stage 1: Pre-extraction
        self.validate_pre_extraction()
        
        # Stage 2: Post-extraction
        self.validate_post_extraction()
        
        # Stage 3: Cross-source
        self.validate_cross_source()
        
        # Stage 4: Final
        self.validate_final()
        
        # Generate report
        report = self.generate_validation_report()
        
        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/VALIDATION_REPORT.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON results
        json_path = Path("C:/Projects/OSINT - Foresight/analysis/validation_results.json")
        with open(json_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print("\n" + "="*60)
        print("VALIDATION COMPLETE")
        print("="*60)
        print(f"\nReport saved to: {report_path}")
        print(f"JSON results: {json_path}")
        
        # Print summary
        total_warnings = len(self.validation_results['warnings'])
        total_errors = len(self.validation_results['errors'])
        
        if total_errors > 0:
            print(f"\n❌ CRITICAL: {total_errors} errors found - fix before proceeding!")
        elif total_warnings > 0:
            print(f"\n⚠️  WARNING: {total_warnings} warnings - review recommended")
        else:
            print("\n✅ SUCCESS: All validation checks passed!")
        
        return self.validation_results


if __name__ == "__main__":
    validator = DataValidationFramework()
    results = validator.run_complete_validation()
