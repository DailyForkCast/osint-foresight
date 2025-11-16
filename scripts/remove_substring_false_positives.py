#!/usr/bin/env python3
"""
remove_substring_false_positives.py - Remove Substring False Positives

Removes entities where chinese_name detector matched SUBSTRINGS within
larger words (word boundary issue).

Categories:
1. Taiwan entities (policy-based exclusion)
2. German technical words (TECHNIK → CHIN/ZTE)
3. German casino (KASINO → SINO)
4. Machinery misspellings (MACHINARY → CHIN)
5. Technology companies (BIZTECH, MOZTECH → ZTE)
6. Indochina region (geographic name, not China)
7. Russian/European false positives
8. Common English words (THE, LIMITED)
9. Personal names
"""

import sqlite3
from datetime import datetime
import json

class SubstringFalsePositiveRemover:
    """Remove substring-based false positives from TIER_2"""

    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.stats = {
            'taiwan_entities': 0,
            'german_technical': 0,
            'german_casino': 0,
            'machinery_misspelling': 0,
            'tech_companies': 0,
            'indochina_region': 0,
            'russian_european': 0,
            'common_words': 0,
            'personal_names': 0,
            'other_european': 0,
            'total_removed': 0
        }

    def remove_entities(self, patterns, category_name):
        """Remove entities matching any pattern in the list"""

        print(f"\n{'='*80}")
        print(f"REMOVING: {category_name}")
        print("="*80)

        tables = ['usaspending_china_305', 'usaspending_china_101', 'usaspending_china_comprehensive']
        total_removed = 0

        for pattern in patterns:
            pattern_removed = 0

            for table in tables:
                # Count records
                count_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table}
                    WHERE recipient_name LIKE ? OR vendor_name LIKE ?
                """

                try:
                    self.cursor.execute(count_query, (pattern, pattern))
                    count = self.cursor.fetchone()[0]

                    if count == 0:
                        continue

                    print(f"\n  Pattern: {pattern}")
                    print(f"  Table: {table}")
                    print(f"  Records to remove: {count}")

                    # Delete records
                    delete_query = f"""
                        DELETE FROM {table}
                        WHERE recipient_name LIKE ? OR vendor_name LIKE ?
                    """

                    self.cursor.execute(delete_query, (pattern, pattern))
                    removed = self.cursor.rowcount
                    pattern_removed += removed
                    total_removed += removed

                    print(f"  [OK] Removed {removed} records")

                except Exception as e:
                    print(f"  [ERROR] {table}: {e}")

            if pattern_removed > 0:
                print(f"  Total for pattern: {pattern_removed}")

        print(f"\n  CATEGORY TOTAL: {total_removed} records removed")
        return total_removed

    def process_all(self):
        """Process all substring false positive removals"""

        print("="*80)
        print("SUBSTRING FALSE POSITIVE REMOVAL")
        print("="*80)
        print(f"\nDatabase: {self.db_path}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. Taiwan Entities (5 records)
        taiwan_patterns = [
            "%OFFICE OF THE PRESIDENT REPUBLIC OF CHINA (TAIWAN)%",
            "%CHINA MEDICAL UNIVERSITY HOSPITAL%",
        ]
        self.stats['taiwan_entities'] = self.remove_entities(
            taiwan_patterns,
            "Taiwan Entities (Policy Exclusion)"
        )

        # 2. German Technical Words (37+ records)
        german_tech_patterns = [
            "%HEIZTECHNISCHE%",
            "%HEIZTECHNIK%",
            "%KONFERENZTECHNIK%",
            "%KONFERENZTECHNI%",
            "%MEDIZINTECHNIK%",
            "%ROHR- UND HEIZTECHNIK%",
            "%SOLAR- & HEIZTECHNIK%",
            "%BRAEHLER ICS KONFERENZTECHNI%",
            "%TTV-BILD-+ KONFERENZTECHNIK%",
            "%EICKEMEYER MEDIZINTECHNIK%",
        ]
        self.stats['german_technical'] = self.remove_entities(
            german_tech_patterns,
            "German Technical Words (TECHNIK)"
        )

        # 3. German Casino (6 records)
        casino_patterns = [
            "%UHG KASINO%",
        ]
        self.stats['german_casino'] = self.remove_entities(
            casino_patterns,
            "German Casino (KASINO)"
        )

        # 4. Machinery Misspelling (129 records - LARGEST!)
        machinery_patterns = [
            "%MACHINARY%",
        ]
        self.stats['machinery_misspelling'] = self.remove_entities(
            machinery_patterns,
            "Machinery Misspelling (MACHINARY)"
        )

        # 5. Technology Companies with ZTE substring
        tech_company_patterns = [
            "%BIZTECH FUSION%",
            "%MOZTECH CONSTRUCOES%",
        ]
        self.stats['tech_companies'] = self.remove_entities(
            tech_company_patterns,
            "Technology Companies (ZTE substring)"
        )

        # 6. Indochina Region (44 records)
        indochina_patterns = [
            "%INDOCHINA HOLIDAYS%",
            "%INDOCHINA RESEARCH%",
            "%TRAFFIC INTERNATIONAL IN INDOCHINA%",
        ]
        self.stats['indochina_region'] = self.remove_entities(
            indochina_patterns,
            "Indochina Region (Geographic Name)"
        )

        # 7. Russian/European (15+ records)
        russian_european_patterns = [
            '%ZAO "GOLITSINO"%',
            "%RUSSINOV COM%",
        ]
        self.stats['russian_european'] = self.remove_entities(
            russian_european_patterns,
            "Russian/Eastern European (SINO substring)"
        )

        # 8. Other European (15+ records)
        other_european_patterns = [
            "%INSINOORITOIMISTO%",  # Finnish
            "%ASTIKO PRASINO%",     # Greek
            "%SINOS GROUP INTERNATIONAL%",  # Italian
            "%ENSINO%",             # Portuguese (teaching)
            "%PAND K. LAKASZTEXTIL%",  # Hungarian
        ]
        self.stats['other_european'] = self.remove_entities(
            other_european_patterns,
            "Other European (Various SINO substrings)"
        )

        # 9. Personal Names (12 records)
        personal_name_patterns = [
            "%TAMERA A KIRJUKCHINA%",
        ]
        self.stats['personal_names'] = self.remove_entities(
            personal_name_patterns,
            "Personal Names (CHINA in surname)"
        )

        # 10. Common Words (if detected - usually these are in vendor names)
        # Note: Being conservative here - only removing if clearly false positive
        common_word_patterns = [
            "%pittsburgh mercy hospital%",  # lowercase issue + HE substring
        ]
        self.stats['common_words'] = self.remove_entities(
            common_word_patterns,
            "Common Words (THE, HE substrings)"
        )

        # Calculate total
        self.stats['total_removed'] = sum([
            self.stats['taiwan_entities'],
            self.stats['german_technical'],
            self.stats['german_casino'],
            self.stats['machinery_misspelling'],
            self.stats['tech_companies'],
            self.stats['indochina_region'],
            self.stats['russian_european'],
            self.stats['other_european'],
            self.stats['personal_names'],
            self.stats['common_words'],
        ])

        # Commit all changes
        self.conn.commit()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print detailed summary"""

        print("\n" + "="*80)
        print("SUBSTRING FALSE POSITIVE REMOVAL COMPLETE")
        print("="*80)

        print(f"\nREMOVAL STATISTICS:")
        print(f"{'Category':<40} {'Records Removed':<15}")
        print("-"*80)

        print(f"{'Taiwan Entities':<40} {self.stats['taiwan_entities']:<15}")
        print(f"{'German Technical Words':<40} {self.stats['german_technical']:<15}")
        print(f"{'German Casino':<40} {self.stats['german_casino']:<15}")
        print(f"{'Machinery Misspelling':<40} {self.stats['machinery_misspelling']:<15}")
        print(f"{'Technology Companies':<40} {self.stats['tech_companies']:<15}")
        print(f"{'Indochina Region':<40} {self.stats['indochina_region']:<15}")
        print(f"{'Russian/European':<40} {self.stats['russian_european']:<15}")
        print(f"{'Other European':<40} {self.stats['other_european']:<15}")
        print(f"{'Personal Names':<40} {self.stats['personal_names']:<15}")
        print(f"{'Common Words':<40} {self.stats['common_words']:<15}")
        print("-"*80)
        print(f"{'TOTAL REMOVED':<40} {self.stats['total_removed']:<15}")

        print("\n" + "="*80)
        print("CATEGORIES EXPLAINED")
        print("="*80)

        print("\n1. TAIWAN ENTITIES (Policy Exclusion)")
        print("   - Office of the President Republic of China (Taiwan)")
        print("   - China Medical University Hospital (Taiwan)")
        print("   - Reason: Taiwan policy - not mainland China threat")

        print("\n2. GERMAN TECHNICAL WORDS")
        print("   - HEIZTECHNIK (heating technology) contains 'ZTE' and 'CHIN'")
        print("   - KONFERENZTECHNIK (conference technology) contains 'ZTE'")
        print("   - MEDIZINTECHNIK (medical technology) contains 'ZTE' and 'CHIN'")
        print("   - Reason: German word substrings triggering Chinese patterns")

        print("\n3. GERMAN CASINO")
        print("   - KASINO (casino) contains 'SINO'")
        print("   - Reason: German word triggering Chinese pattern")

        print("\n4. MACHINERY MISSPELLING (LARGEST CATEGORY)")
        print("   - MACHINARY (common misspelling) contains 'CHIN' and 'CHINA'")
        print("   - Companies: Cambodia, South Korea machinery suppliers")
        print("   - Reason: Misspelling creating false Chinese pattern match")

        print("\n5. TECHNOLOGY COMPANIES")
        print("   - BIZTECH, MOZTECH contain 'ZTE'")
        print("   - Reason: Company names triggering ZTE (Chinese telecom) pattern")

        print("\n6. INDOCHINA REGION")
        print("   - INDOCHINA = Vietnam/Cambodia/Laos geographic region")
        print("   - Contains 'CHIN' and 'CHINA'")
        print("   - Reason: Historical geographic name, not related to PRC")

        print("\n7. RUSSIAN/EASTERN EUROPEAN")
        print("   - Russian company names containing 'SINO'")
        print("   - ZAO GOLITSINO, RUSSINOV")
        print("   - Reason: Russian words triggering SINO pattern")

        print("\n8. OTHER EUROPEAN")
        print("   - Finnish: INSINOORITOIMISTO (engineering firm)")
        print("   - Portuguese: ENSINO (teaching)")
        print("   - Greek, Italian companies")
        print("   - Reason: European words containing Chinese patterns")

        print("\n9. PERSONAL NAMES")
        print("   - Dr. Tamera A Kirjukchina")
        print("   - Reason: Surname contains 'CHINA'")

        print("\n10. COMMON WORDS")
        print("   - Words like 'THE', 'LIMITED' contain 'HE', 'LI'")
        print("   - Reason: English words triggering Chinese name patterns")

        print("\n" + "="*80)
        print("NOT REMOVED (Requires Investigation)")
        print("="*80)

        print("\nThe following entities were NOT removed (may be legitimate PRC entities):")
        print("  - CHINA RAILWAY JIANCHANG ENGINE")
        print("  - CHINA SHIPPING DEVELOPMENT CO., LTD.")
        print("  - CHINA SOUTH LOCOMOTIVE & ROLLING STOCK INDUSTRY (GROUP) CORP")
        print("  - THE CHINA NAVIGATION COMPANY PTE. LTD.")
        print("  - LENOVO GROUP LIMITED (already in supply chain tracking)")
        print("  - OVERSEA-CHINESE BANKING CORPORATION LIMITED (requires investigation)")

        print("\nThese entities contain 'CHINA' in their official names and may have")
        print("actual PRC connections that need investigation.")

        print("\n" + "="*80)
        print("DETECTION SYSTEM RECOMMENDATIONS")
        print("="*80)

        print("\nRoot Cause: Chinese name detector lacks WORD BOUNDARY checking")
        print("\nFixes Needed:")
        print("  1. Add \\b word boundaries to pattern matching")
        print("  2. Exclude common European words (TECHNIK, KASINO, etc.)")
        print("  3. Add language detection (German, Russian, etc.)")
        print("  4. Filter out common English words (THE, LIMITED, etc.)")
        print("  5. Special handling for geographic names (INDOCHINA)")

        print("\nExample Fix:")
        print("  Before: if 'CHIN' in name")
        print("  After:  if re.search(r'\\bCHIN\\b', name)")

        print("\n" + "="*80)

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"analysis/substring_removal_report_{timestamp}.json"

        with open(report_path, 'w') as f:
            json.dump({
                'removal_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'statistics': self.stats,
                'total_removed': self.stats['total_removed']
            }, f, indent=2)

        print(f"\nReport saved: {report_path}")
        print("="*80)

    def close(self):
        self.conn.close()

def main():
    print("\n" + "="*80)
    print("IMPORTANT: This will remove ~275-300 records from the database")
    print("="*80)
    print("\nCategories to be removed:")
    print("  1. Taiwan entities (5 records)")
    print("  2. German technical words (37+ records)")
    print("  3. German casino (6 records)")
    print("  4. Machinery misspellings (129 records)")
    print("  5. Technology companies (2+ records)")
    print("  6. Indochina region (44 records)")
    print("  7. Russian/European (15+ records)")
    print("  8. Other European (15+ records)")
    print("  9. Personal names (12 records)")
    print(" 10. Common words (1+ records)")

    print("\nEntities NOT removed (require investigation):")
    print("  - China Railway, China Shipping, China South Locomotive")
    print("  - Lenovo (in supply chain tracking)")
    print("  - Oversea-Chinese Banking")

    response = input("\nProceed with removal? (yes/no): ")

    if response.lower() != 'yes':
        print("\n[CANCELLED] No changes made to database")
        return

    remover = SubstringFalsePositiveRemover()
    remover.process_all()
    remover.close()

if __name__ == "__main__":
    main()
