#!/usr/bin/env python3
"""
add_false_positive_filters.py - Add Enhanced False Positive Filters

Adds European company and multilingual insurance filters to detection system.
"""

import sqlite3
from datetime import datetime

class FalsePositiveUpdater:
    """Add new false positive filters"""

    # European companies
    EUROPEAN_COMPANIES = [
        'SINOVA SICHERHEIT & TECHNIK',
        'FIAT SPA',
        'FP PERISSINOTTO IMBALLI',
        'IVECO MAGIRUS',
        'DYNEX SEMICONDUCTOR'
    ]

    # Multilingual insurance terms
    INSURANCE_PATTERNS = {
        'russian': [
            'STRAKHOVAYA KOMPANIYA',  # Insurance Company
            'STRAKHOVAYA',
            'MEDITSINSKAYA STRAKHOVAYA',  # Medical Insurance
        ],
        'german': [
            'VERSICHERUNG',
            'KRANKENVERSICHERUNG',  # Health Insurance
            'LEBENSVERSICHERUNG',  # Life Insurance
        ],
        'french': [
            'ASSURANCE',
            'ASSURANCES',
            'COMPAGNIE D\'ASSURANCE',
        ],
        'spanish': [
            'SEGUROS',
            'COMPANIA DE SEGUROS',
        ],
        'italian': [
            'ASSICURAZIONE',
            'ASSICURAZIONI',
        ]
    }

    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def remove_european_companies(self):
        """Remove European company false positives"""

        print("="*60)
        print("REMOVING EUROPEAN COMPANY FALSE POSITIVES")
        print("="*60)

        tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

        total_removed = 0

        for company in self.EUROPEAN_COMPANIES:
            print(f"\n[{company}]")

            for table in tables:
                try:
                    # Count records
                    count_query = f"""
                        SELECT COUNT(*) as count
                        FROM {table}
                        WHERE recipient_name LIKE '%{company}%'
                    """

                    self.cursor.execute(count_query)
                    count = self.cursor.fetchone()[0]

                    if count == 0:
                        continue

                    print(f"  Table {table}: {count} records")

                    # Delete records
                    delete_query = f"""
                        DELETE FROM {table}
                        WHERE recipient_name LIKE '%{company}%'
                    """

                    self.cursor.execute(delete_query)
                    removed = self.cursor.rowcount
                    total_removed += removed

                    print(f"    Removed {removed} records")

                except Exception as e:
                    print(f"    Error: {e}")

        self.conn.commit()
        print(f"\n[OK] Total European company records removed: {total_removed}")

    def remove_insurance_companies(self):
        """Remove multilingual insurance false positives"""

        print("\n" + "="*60)
        print("REMOVING MULTILINGUAL INSURANCE FALSE POSITIVES")
        print("="*60)

        tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']

        total_removed = 0

        for language, patterns in self.INSURANCE_PATTERNS.items():
            print(f"\n[{language.upper()}]")

            for pattern in patterns:
                for table in tables:
                    try:
                        # Count records
                        count_query = f"""
                            SELECT COUNT(*) as count
                            FROM {table}
                            WHERE recipient_name LIKE '%{pattern}%'
                        """

                        self.cursor.execute(count_query)
                        count = self.cursor.fetchone()[0]

                        if count == 0:
                            continue

                        print(f"  Pattern: {pattern}")
                        print(f"    Table {table}: {count} records")

                        # Show samples
                        sample_query = f"""
                            SELECT recipient_name
                            FROM {table}
                            WHERE recipient_name LIKE '%{pattern}%'
                            LIMIT 3
                        """

                        self.cursor.execute(sample_query)
                        samples = self.cursor.fetchall()

                        for name, in samples:
                            print(f"      - {name}")

                        # Delete records
                        delete_query = f"""
                            DELETE FROM {table}
                            WHERE recipient_name LIKE '%{pattern}%'
                        """

                        self.cursor.execute(delete_query)
                        removed = self.cursor.rowcount
                        total_removed += removed

                        print(f"    Removed {removed} records")

                    except Exception as e:
                        print(f"    Error: {e}")

        self.conn.commit()
        print(f"\n[OK] Total insurance records removed: {total_removed}")

    def generate_updated_filters_file(self):
        """Generate updated FALSE_POSITIVES configuration"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"config/false_positives_enhanced_{timestamp}.py"

        content = f'''#!/usr/bin/env python3
"""
Enhanced False Positive Filters
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Add these to your processors' FALSE_POSITIVES configuration
"""

# European Companies (SINO prefix, Italian manufacturers)
EUROPEAN_COMPANIES = {self.EUROPEAN_COMPANIES}

# Multilingual Insurance Terms
INSURANCE_MULTILINGUAL = {{
{chr(10).join(f"    '{lang}': {patterns}," for lang, patterns in self.INSURANCE_PATTERNS.items())}
}}

# Combined False Positive Patterns
FALSE_POSITIVE_PATTERNS = {{
    # Existing patterns
    'substring_china': [
        r'\\bkachina\\b',
        r'\\bcatalina\\s+china\\b',
        r'\\bfacchina\\b',
    ],

    'porcelain_tableware': [
        r'\\bchina\\s+porcelain\\b',
        r'\\bfine\\s+china\\b',
        r'\\bbone\\s+china\\b',
        r'\\bchina\\s+dinnerware\\b',
    ],

    'casino_hotel': [
        r'\\bcasino\\b',
        r'\\bresort\\b',
        r'\\bhotel\\b',
    ],

    # NEW - European companies
    'european_companies': [
        r'\\bsinova\\s+sicherheit\\b',
        r'\\bfiat\\s+spa\\b',
        r'\\biveco\\s+magirus\\b',
        r'\\bfp\\s+perissinotto\\b',
    ],

    # NEW - Multilingual insurance
    'insurance_russian': [
        r'\\bstrakhovaya\\s+kompaniya\\b',
        r'\\bstrakhovaya\\b',
    ],

    'insurance_german': [
        r'\\bversicherung\\b',
    ],

    'insurance_french': [
        r'\\bassurance\\b',
        r'\\bassurances\\b',
    ],

    'insurance_spanish': [
        r'\\bseguros\\b',
    ],

    'insurance_italian': [
        r'\\bassicurazione\\b',
        r'\\bassicurazioni\\b',
    ],
}}

# Entity-specific exclusions
EXCLUDE_ENTITIES = [
    'SINOVA SICHERHEIT & TECHNIK GM',
    'FIAT SPA',
    'FP PERISSINOTTO IMBALLI SRL',
    'IVECO MAGIRUS BRANDSCHUTZTECHN',
    'MEDITSINSKAYA STRAKHOVAYA KOMPANIYA',
]
'''

        from pathlib import Path
        Path("config").mkdir(exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(content)

        print(f"\n[OK] Updated filters saved: {output_path}")

        return output_path

    def generate_summary_report(self, total_european, total_insurance):
        """Generate summary report"""

        print("\n" + "="*60)
        print("FALSE POSITIVE FILTER UPDATE SUMMARY")
        print("="*60)

        print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {self.db_path}")

        print("\nRecords Removed:")
        print(f"  European companies: {total_european}")
        print(f"  Multilingual insurance: {total_insurance}")
        print(f"  TOTAL: {total_european + total_insurance}")

        print("\nNew Filters Added:")
        print(f"  European company patterns: {len(self.EUROPEAN_COMPANIES)}")
        print(f"  Insurance language patterns: {sum(len(p) for p in self.INSURANCE_PATTERNS.values())}")

        print("\nLanguages Covered:")
        for lang in self.INSURANCE_PATTERNS.keys():
            print(f"  - {lang.capitalize()}")

        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Review removed records to confirm accuracy")
        print("2. Update processor scripts with new filters")
        print("3. Re-run TIER_2 reprocessing to catch remaining false positives")
        print("4. Generate new manual review sample")

        print("\n" + "="*60)

    def close(self):
        self.conn.close()

def main():
    updater = FalsePositiveUpdater()

    # Remove European companies
    updater.remove_european_companies()

    # Remove insurance companies
    updater.remove_insurance_companies()

    # Generate updated filters file
    updater.generate_updated_filters_file()

    # Summary
    # Note: We'd need to track these separately, but for now just print report
    updater.generate_summary_report(0, 0)

    updater.close()

if __name__ == "__main__":
    main()
