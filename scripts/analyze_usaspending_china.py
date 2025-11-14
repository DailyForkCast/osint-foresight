#!/usr/bin/env python3
"""
Analyze USAspending Data for China References
Carefully handles false positives like "China Lake, CA"
"""

import os
import gzip
import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime
import csv
import logging

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class USAspendingChinaAnalyzer:
    """Analyze USAspending data for legitimate China references"""
    
    def __init__(self):
        self.data_dir = Path("F:/OSINT_DATA/USAspending")
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.extracted_dir = self.data_dir / "extracted_data"
        
        # False positive patterns to exclude
        self.false_positives = [
            r'china\s+lake',  # China Lake Naval Weapons Station, CA
            r'china\s+grove',  # China Grove, TX/NC
            r'china\s+spring',  # China Spring, TX
            r'china\s+beach',  # Various US locations
            r'china\s+town',  # Chinatown (various US cities)
            r'china\s+basin',  # Geographic location in Maine
            r'china\s+creek',  # Various US locations
            r'china\s+camp',  # China Camp State Park, CA
            r'china\s+garden',  # Restaurant names
            r'china\s+wok',  # Restaurant names
            r'china\s+buffet',  # Restaurant names
            r'china\s+express',  # Restaurant names
            r'china\s+king',  # Restaurant names
            r'china\s+star',  # Restaurant names
            r'china\s+house',  # Restaurant names
            r'china\s+palace',  # Restaurant names
        ]
        
        # Legitimate China patterns
        self.china_patterns = [
            r'people[\'\s]*s?\s+republic\s+of\s+china',
            r'\bprc\b',
            r'beijing',
            r'shanghai',
            r'guangzhou',
            r'shenzhen',
            r'hong\s+kong',
            r'huawei',
            r'alibaba',
            r'tencent',
            r'baidu',
            r'xiaomi',
            r'lenovo',
            r'zte\b',
            r'china\s+telecom',
            r'china\s+mobile',
            r'china\s+unicom',
            r'sinopec',
            r'petrochina',
            r'bank\s+of\s+china',
            r'china\s+construction\s+bank',
            r'icbc',  # Industrial and Commercial Bank of China
            r'china\s+development\s+bank',
            r'silk\s+road',
            r'belt\s+and\s+road',
            r'made\s+in\s+china',
            r'export.*china',
            r'import.*china',
            r'china.*trade',
            r'china.*tariff',
            r'china.*sanction',
            r'chinese\s+government',
            r'chinese\s+military',
            r'chinese\s+company',
            r'chinese\s+firm',
            r'chinese\s+vendor',
            r'chinese\s+supplier',
            r'chinese\s+contractor',
            r'chinese\s+manufacturer',
            r'chinese-owned',
            r'china-based',
            r'headquartered.*china',
        ]
        
        # Country code
        self.china_country_codes = ['CN', 'CHN', 'HK', 'HKG', 'MO', 'MAC']
    
    def is_false_positive(self, text: str) -> bool:
        """Check if text contains false positive China reference"""
        text_lower = text.lower()
        
        for pattern in self.false_positives:
            if re.search(pattern, text_lower):
                return True
        
        # Additional checks for US locations
        if 'china' in text_lower:
            # Check for US state abbreviations near "China"
            us_states = r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b'
            if re.search(f'china[^,]*,\s*{us_states}', text_lower):
                return True
            
            # Check for US zip codes
            if re.search(r'china.*\b\d{5}(-\d{4})?\b', text_lower):
                return True
        
        return False
    
    def is_china_reference(self, text: str) -> dict:
        """Check if text contains legitimate China reference"""
        if not text:
            return {'is_china': False}
        
        text_lower = text.lower()
        
        # First check for false positives
        if self.is_false_positive(text):
            return {'is_china': False, 'reason': 'false_positive'}
        
        # Check for legitimate patterns
        matches = []
        for pattern in self.china_patterns:
            if re.search(pattern, text_lower):
                matches.append(pattern)
        
        if matches:
            return {
                'is_china': True,
                'patterns_matched': matches,
                'confidence': 'high' if len(matches) > 1 else 'medium'
            }
        
        # Basic "china" check (lower confidence)
        if 'china' in text_lower or 'chinese' in text_lower:
            return {
                'is_china': True,
                'patterns_matched': ['basic_china'],
                'confidence': 'low'
            }
        
        return {'is_china': False}
    
    def check_existing_databases(self):
        """Check what's in existing USAspending databases"""
        print("\n" + "="*60)
        print("CHECKING EXISTING USASPENDING DATABASES")
        print("="*60)
        
        db_files = list(self.data_dir.parent.glob("usaspending*.db"))
        
        for db_file in db_files:
            if not db_file.exists():
                continue
                
            print(f"\nDatabase: {db_file.name} ({db_file.stat().st_size / (1024**2):.1f} MB)")
            
            try:
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()
                
                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"  Tables: {[t[0] for t in tables[:5]]}")
                
                # Check for China-related content
                for table in tables[:3]:  # Check first 3 tables
                    table_name = table[0]
                    # SECURITY: Validate table name before use in SQL
                    safe_table = validate_sql_identifier(table_name)

                    # Get column names
                    cursor.execute(f"PRAGMA table_info({safe_table})")
                    columns = [col[1] for col in cursor.fetchall()]

                    # Search text columns for China
                    text_columns = [col for col in columns if 'name' in col.lower() or
                                   'description' in col.lower() or 'vendor' in col.lower() or
                                   'recipient' in col.lower() or 'country' in col.lower()]

                    if text_columns:
                        print(f"\n  Checking table '{table_name}' columns: {text_columns[:3]}")

                        for col in text_columns[:2]:  # Check first 2 text columns
                            # SECURITY: Validate column name before use in SQL
                            safe_col = validate_sql_identifier(col)
                            query = f"""
                                SELECT COUNT(*), {safe_col}
                                FROM {safe_table}
                                WHERE LOWER({safe_col}) LIKE '%china%'
                                   OR LOWER({safe_col}) LIKE '%chinese%'
                                   OR LOWER({safe_col}) LIKE '%beijing%'
                                   OR LOWER({safe_col}) LIKE '%huawei%'
                                LIMIT 5
                            """

                            try:
                                cursor.execute(query)
                                results = cursor.fetchall()
                                if results and results[0][0] > 0:
                                    print(f"    Found {results[0][0]} potential China references in {col}")
                                    for row in results:
                                        if row[1]:
                                            print(f"      Sample: {row[1][:100]}")
                            except Exception as e:
                                pass
                
                conn.close()
                
            except Exception as e:
                print(f"  Error reading database: {e}")
    
    def analyze_dat_files(self, sample_size: int = 10):
        """Analyze .dat.gz files for China content"""
        print("\n" + "="*60)
        print("ANALYZING DAT.GZ FILES")
        print("="*60)
        
        dat_files = list(self.extracted_dir.glob("*.dat.gz"))
        print(f"Found {len(dat_files)} .dat.gz files")
        
        china_references = []
        files_checked = 0
        total_records = 0
        
        # Sample files
        for dat_file in dat_files[:sample_size]:
            print(f"\nChecking {dat_file.name}...")
            
            try:
                with gzip.open(dat_file, 'rt', encoding='utf-8', errors='ignore') as f:
                    # Read as TSV
                    reader = csv.reader(f, delimiter='\t')
                    
                    for row_num, row in enumerate(reader):
                        total_records += 1
                        
                        # Convert row to text
                        row_text = ' '.join(str(cell) for cell in row)
                        
                        # Check for China references
                        result = self.is_china_reference(row_text)
                        
                        if result['is_china']:
                            china_references.append({
                                'file': dat_file.name,
                                'row': row_num,
                                'confidence': result.get('confidence', 'unknown'),
                                'patterns': result.get('patterns_matched', []),
                                'sample': row_text[:200]
                            })
                            
                            print(f"  [FOUND] Row {row_num}: {result['patterns_matched']}")
                            print(f"    Sample: {row_text[:150]}...")
                        
                        # Progress update
                        if row_num % 1000 == 0 and row_num > 0:
                            print(f"  Processed {row_num:,} rows...")
                
                files_checked += 1
                
            except Exception as e:
                print(f"  Error reading {dat_file.name}: {e}")
        
        # Summary
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        print(f"Files checked: {files_checked}")
        print(f"Total records: {total_records:,}")
        print(f"China references found: {len(china_references)}")
        
        if china_references:
            print("\nSample China References:")
            
            # Group by confidence
            high_conf = [r for r in china_references if r['confidence'] == 'high']
            med_conf = [r for r in china_references if r['confidence'] == 'medium']
            low_conf = [r for r in china_references if r['confidence'] == 'low']
            
            if high_conf:
                print(f"\nHIGH CONFIDENCE ({len(high_conf)}):")
                for ref in high_conf[:3]:
                    print(f"  File: {ref['file']}, Row: {ref['row']}")
                    print(f"  Patterns: {ref['patterns']}")
                    print(f"  Sample: {ref['sample']}\n")
            
            if med_conf:
                print(f"\nMEDIUM CONFIDENCE ({len(med_conf)}):")
                for ref in med_conf[:2]:
                    print(f"  File: {ref['file']}, Row: {ref['row']}")
                    print(f"  Sample: {ref['sample'][:100]}...\n")
        
        return china_references
    
    def test_false_positive_detection(self):
        """Test false positive detection"""
        print("\n" + "="*60)
        print("TESTING FALSE POSITIVE DETECTION")
        print("="*60)
        
        test_cases = [
            # False positives
            ("Contract awarded to China Lake Naval Weapons Center, CA", False),
            ("Meeting at China Grove, TX 78263", False),
            ("China Town Restaurant, New York, NY", False),
            ("China Spring Independent School District, TX", False),
            ("Naval Air Weapons Station China Lake, California", False),
            
            # True positives
            ("Huawei Technologies Co. Ltd.", True),
            ("Vendor: Beijing Electronics Corporation", True),
            ("Imported from People's Republic of China", True),
            ("Contract with Chinese manufacturer", True),
            ("Sanctions on Chinese military companies", True),
            ("Trade agreement with China", True),
            ("Bank of China New York Branch", True),
        ]
        
        print("\nTest Results:")
        for text, expected in test_cases:
            result = self.is_china_reference(text)
            is_china = result['is_china']
            
            if is_china == expected:
                status = "[PASS]"
            else:
                status = "[FAIL]"
            
            print(f"{status} '{text[:60]}...'")
            print(f"       Expected: {expected}, Got: {is_china}")
            if result.get('reason'):
                print(f"       Reason: {result['reason']}")
            print()
    
    def run(self):
        """Run complete analysis"""
        print("="*60)
        print("USASPENDING CHINA ANALYSIS")
        print("="*60)
        
        # Test false positive detection
        self.test_false_positive_detection()
        
        # Check existing databases
        self.check_existing_databases()
        
        # Analyze dat files
        china_refs = self.analyze_dat_files(sample_size=5)
        
        # Save results
        output_file = Path("C:/Projects/OSINT - Foresight/analysis/usaspending_china_analysis.json")
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'references_found': len(china_refs),
                'sample_references': china_refs[:20]
            }, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    analyzer = USAspendingChinaAnalyzer()
    analyzer.run()
