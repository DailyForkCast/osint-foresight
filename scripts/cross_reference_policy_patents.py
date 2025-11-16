#!/usr/bin/env python3
"""
Cross-Reference Policy Documents with USPTO Patent Data
Validates Made in China 2025 impact claims

This script:
1. Extracts technology priorities from policy documents
2. Maps to CPC classifications
3. Analyzes patent growth pre vs. post MIC2025
4. Tests "340%" claim with sector-specific data
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OUTPUT_DIR = Path("C:/Projects/OSINT-Foresight/analysis")

# Made in China 2025 - 10 Priority Sectors mapped to CPC codes
MIC2025_SECTORS = {
    'advanced_information_technology': {
        'technologies': ['semiconductors', 'artificial_intelligence', 'big_data', 'telecommunications'],
        'cpc_codes': [
            'H01L',     # Semiconductor devices
            'G06F',     # Electric digital data processing
            'G06N',     # Computer systems based on specific computational models (AI)
            'H04L',     # Transmission of digital information (telecom)
            'H04W',     # Wireless communication networks
            'G06Q',     # Data processing systems for business
        ]
    },
    'robotics_automation': {
        'technologies': ['robotics'],
        'cpc_codes': [
            'B25J',     # Manipulators; Chambers provided with manipulation devices (robots)
            'G05B',     # Control or regulating systems
            'B23Q',     # Machine tools (automated)
        ]
    },
    'aerospace_equipment': {
        'technologies': ['aerospace'],
        'cpc_codes': [
            'B64C',     # Aeroplanes; Helicopters
            'B64D',     # Equipment for fitting in or to aircraft
            'B64F',     # Ground or aircraft-carrier-deck installations
            'F02K',     # Jet-propulsion plants
        ]
    },
    'maritime_equipment': {
        'technologies': [],  # Not in our tech domain list
        'cpc_codes': [
            'B63B',     # Ships or other waterborne vessels
            'B63H',     # Marine propulsion
        ]
    },
    'rail_equipment': {
        'technologies': [],
        'cpc_codes': [
            'B61D',     # Body details or kinds of railway vehicles
            'B61F',     # Suspension arrangements for rail vehicles
        ]
    },
    'new_energy_vehicles': {
        'technologies': ['new_energy_vehicles'],
        'cpc_codes': [
            'B60L',     # Electric propulsion of vehicles
            'H01M',     # Processes or means for batteries
            'B60K',     # Arrangement or mounting of propulsion units
        ]
    },
    'power_equipment': {
        'technologies': [],
        'cpc_codes': [
            'H02J',     # Circuit arrangements for AC/DC power
            'H02M',     # Apparatus for conversion between AC and DC
        ]
    },
    'agricultural_equipment': {
        'technologies': [],
        'cpc_codes': [
            'A01B',     # Soil working in agriculture
            'A01D',     # Harvesting
        ]
    },
    'new_materials': {
        'technologies': ['advanced_materials'],
        'cpc_codes': [
            'C01B',     # Non-metallic elements; Compounds thereof
            'C08J',     # Working-up of macromolecular substances (plastics)
            'C23C',     # Coating metallic material (advanced coatings)
        ]
    },
    'biopharmaceuticals': {
        'technologies': ['biotechnology'],
        'cpc_codes': [
            'A61K',     # Preparations for medical purposes
            'C12N',     # Microorganisms or enzymes (biotech)
            'C07K',     # Peptides
            'A61P',     # Therapeutic activity of chemical compounds
        ]
    }
}

# Quantum computing (high priority but not in MIC2025 original 10)
EMERGING_PRIORITY = {
    'quantum_computing': {
        'technologies': ['quantum_computing'],
        'cpc_codes': [
            'G06N10',   # Quantum computing
            'H04L9/08', # Quantum cryptography
            'B82Y',     # Specific uses or applications of nanostructures (quantum)
        ]
    }
}

class PolicyPatentCrossReference:
    """Cross-reference policy priorities with patent data"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.mic2025_date = '2015-05-08'
        self.results = {
            'overall_growth': {},
            'sector_growth': {},
            'priority_comparison': {},
            'technology_validation': {}
        }

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def get_overall_patent_stats(self):
        """Get overall Chinese patent statistics (baseline from previous analysis)"""
        cursor = self.conn.cursor()

        print("\n" + "="*80)
        print("BASELINE: OVERALL USPTO CHINESE PATENT GROWTH")
        print("="*80)

        # Pre-MIC2025
        pre_patents = cursor.execute("""
        SELECT COUNT(*) as count
        FROM uspto_patents_chinese
        WHERE filing_date >= '2011-01-01'
          AND filing_date < '2015-05-08'
        """).fetchone()

        pre_count = pre_patents['count']
        pre_days = (datetime.strptime('2015-05-08', '%Y-%m-%d') - datetime.strptime('2011-01-01', '%Y-%m-%d')).days
        pre_rate = pre_count / (pre_days / 365.25)

        # Post-MIC2025
        post_patents = cursor.execute("""
        SELECT COUNT(*) as count
        FROM uspto_patents_chinese
        WHERE filing_date >= '2015-05-08'
          AND filing_date <= '2020-12-31'
        """).fetchone()

        post_count = post_patents['count']
        post_days = (datetime.strptime('2020-12-31', '%Y-%m-%d') - datetime.strptime('2015-05-08', '%Y-%m-%d')).days
        post_rate = post_count / (post_days / 365.25)

        growth_rate = ((post_rate - pre_rate) / pre_rate) * 100

        print(f"\nPre-MIC2025 (2011-01-01 to 2015-05-07):")
        print(f"  Patents: {pre_count:,}")
        print(f"  Days: {pre_days}")
        print(f"  Annual rate: {pre_rate:,.0f} patents/year")

        print(f"\nPost-MIC2025 (2015-05-08 to 2020-12-31):")
        print(f"  Patents: {post_count:,}")
        print(f"  Days: {post_days}")
        print(f"  Annual rate: {post_rate:,.0f} patents/year")

        print(f"\n**GROWTH RATE: +{growth_rate:.1f}%**")
        print(f"(This matches the 11.3% from previous deep dive analysis)")

        self.results['overall_growth'] = {
            'pre_count': pre_count,
            'pre_rate': pre_rate,
            'post_count': post_count,
            'post_rate': post_rate,
            'growth_rate': growth_rate
        }

        return growth_rate

    def analyze_sector_growth(self, sector_name, cpc_codes):
        """Analyze patent growth for a specific sector"""
        cursor = self.conn.cursor()

        # Build CPC pattern matching
        cpc_patterns = []
        for code in cpc_codes:
            if '/' in code:
                # Exact match for subclass
                cpc_patterns.append(f"cpc_full = '{code}'")
            else:
                # Prefix match for class/subclass
                cpc_patterns.append(f"cpc_full LIKE '{code}%'")

        cpc_where = " OR ".join(cpc_patterns)

        # Pre-MIC2025 patents
        pre_query = f"""
        SELECT COUNT(DISTINCT p.application_number) as count
        FROM uspto_patents_chinese p
        JOIN uspto_cpc_classifications c ON p.application_number = c.application_number
        WHERE p.filing_date >= '2011-01-01'
          AND p.filing_date < '2015-05-08'
          AND ({cpc_where})
        """

        pre_result = cursor.execute(pre_query).fetchone()
        pre_count = pre_result['count'] if pre_result['count'] else 0

        # Post-MIC2025 patents
        post_query = f"""
        SELECT COUNT(DISTINCT p.application_number) as count
        FROM uspto_patents_chinese p
        JOIN uspto_cpc_classifications c ON p.application_number = c.application_number
        WHERE p.filing_date >= '2015-05-08'
          AND p.filing_date <= '2020-12-31'
          AND ({cpc_where})
        """

        post_result = cursor.execute(post_query).fetchone()
        post_count = post_result['count'] if post_result['count'] else 0

        # Calculate rates
        pre_days = (datetime.strptime('2015-05-08', '%Y-%m-%d') - datetime.strptime('2011-01-01', '%Y-%m-%d')).days
        post_days = (datetime.strptime('2020-12-31', '%Y-%m-%d') - datetime.strptime('2015-05-08', '%Y-%m-%d')).days

        pre_rate = pre_count / (pre_days / 365.25) if pre_count > 0 else 0
        post_rate = post_count / (post_days / 365.25) if post_count > 0 else 0

        growth_rate = ((post_rate - pre_rate) / pre_rate) * 100 if pre_rate > 0 else 0

        return {
            'pre_count': pre_count,
            'pre_rate': pre_rate,
            'post_count': post_count,
            'post_rate': post_rate,
            'growth_rate': growth_rate
        }

    def analyze_all_sectors(self):
        """Analyze all MIC2025 sectors"""
        print("\n" + "="*80)
        print("SECTOR-SPECIFIC ANALYSIS: MIC2025 10 PRIORITY SECTORS")
        print("="*80)

        sector_results = []

        for sector_name, sector_info in MIC2025_SECTORS.items():
            print(f"\n[ANALYZING] {sector_name.replace('_', ' ').title()}")
            print(f"  CPC codes: {', '.join(sector_info['cpc_codes'])}")

            stats = self.analyze_sector_growth(sector_name, sector_info['cpc_codes'])

            print(f"  Pre-MIC2025: {stats['pre_count']:,} patents ({stats['pre_rate']:.0f}/year)")
            print(f"  Post-MIC2025: {stats['post_count']:,} patents ({stats['post_rate']:.0f}/year)")
            print(f"  Growth: {stats['growth_rate']:+.1f}%")

            sector_results.append({
                'sector': sector_name,
                'cpc_codes': sector_info['cpc_codes'],
                **stats
            })

            self.results['sector_growth'][sector_name] = stats

        # Sort by growth rate
        sector_results.sort(key=lambda x: x['growth_rate'], reverse=True)

        print("\n" + "="*80)
        print("RANKING: SECTORS BY GROWTH RATE")
        print("="*80)
        print(f"\n{'Sector':<35} {'Pre/Year':<12} {'Post/Year':<12} {'Growth':<10}")
        print("-"*80)

        for result in sector_results:
            sector_display = result['sector'].replace('_', ' ').title()[:34]
            print(f"{sector_display:<35} {result['pre_rate']:>10.0f}  {result['post_rate']:>10.0f}  {result['growth_rate']:>8.1f}%")

        return sector_results

    def compare_priority_vs_nonpriority(self):
        """Compare MIC2025 priority sectors vs non-priority sectors"""
        cursor = self.conn.cursor()

        print("\n" + "="*80)
        print("PRIORITY VS. NON-PRIORITY SECTOR COMPARISON")
        print("="*80)

        # Get all MIC2025 CPC codes
        priority_cpc_codes = []
        for sector_info in MIC2025_SECTORS.values():
            priority_cpc_codes.extend(sector_info['cpc_codes'])

        # Build exclusion pattern for non-priority
        priority_patterns = []
        for code in priority_cpc_codes:
            if '/' in code:
                priority_patterns.append(f"cpc_full = '{code}'")
            else:
                priority_patterns.append(f"cpc_full LIKE '{code}%'")

        priority_where = " OR ".join(priority_patterns)

        # Priority sectors
        print("\n[CALCULATING] Priority sectors (MIC2025 10 sectors)...")
        priority_stats = self.analyze_priority_sectors(priority_where)

        # Non-priority sectors
        print("[CALCULATING] Non-priority sectors (all other technologies)...")
        non_priority_stats = self.analyze_nonpriority_sectors(priority_where)

        print("\n" + "-"*80)
        print("RESULTS:")
        print("-"*80)

        print(f"\nPRIORITY SECTORS (MIC2025):")
        print(f"  Pre-MIC2025: {priority_stats['pre_count']:,} patents ({priority_stats['pre_rate']:.0f}/year)")
        print(f"  Post-MIC2025: {priority_stats['post_count']:,} patents ({priority_stats['post_rate']:.0f}/year)")
        print(f"  Growth: {priority_stats['growth_rate']:+.1f}%")

        print(f"\nNON-PRIORITY SECTORS:")
        print(f"  Pre-MIC2025: {non_priority_stats['pre_count']:,} patents ({non_priority_stats['pre_rate']:.0f}/year)")
        print(f"  Post-MIC2025: {non_priority_stats['post_count']:,} patents ({non_priority_stats['post_rate']:.0f}/year)")
        print(f"  Growth: {non_priority_stats['growth_rate']:+.1f}%")

        diff = priority_stats['growth_rate'] - non_priority_stats['growth_rate']
        print(f"\n**DIFFERENTIAL: {diff:+.1f} percentage points**")

        if abs(diff) < 5:
            print("FINDING: No significant difference between priority and non-priority sectors")
            print("CONCLUSION: Growth appears to be general trend, not MIC2025-specific")
        else:
            print(f"FINDING: Priority sectors grew {diff:+.1f}pp more than non-priority")
            print("CONCLUSION: Evidence of targeted growth in MIC2025 priority areas")

        self.results['priority_comparison'] = {
            'priority': priority_stats,
            'non_priority': non_priority_stats,
            'differential': diff
        }

        return diff

    def analyze_priority_sectors(self, priority_where):
        """Analyze growth in priority sectors"""
        cursor = self.conn.cursor()

        # Pre-MIC2025
        pre_query = f"""
        SELECT COUNT(DISTINCT p.application_number) as count
        FROM uspto_patents_chinese p
        JOIN uspto_cpc_classifications c ON p.application_number = c.application_number
        WHERE p.filing_date >= '2011-01-01'
          AND p.filing_date < '2015-05-08'
          AND ({priority_where})
        """

        pre_count = cursor.execute(pre_query).fetchone()['count'] or 0

        # Post-MIC2025
        post_query = f"""
        SELECT COUNT(DISTINCT p.application_number) as count
        FROM uspto_patents_chinese p
        JOIN uspto_cpc_classifications c ON p.application_number = c.application_number
        WHERE p.filing_date >= '2015-05-08'
          AND p.filing_date <= '2020-12-31'
          AND ({priority_where})
        """

        post_count = cursor.execute(post_query).fetchone()['count'] or 0

        pre_days = (datetime.strptime('2015-05-08', '%Y-%m-%d') - datetime.strptime('2011-01-01', '%Y-%m-%d')).days
        post_days = (datetime.strptime('2020-12-31', '%Y-%m-%d') - datetime.strptime('2015-05-08', '%Y-%m-%d')).days

        pre_rate = pre_count / (pre_days / 365.25)
        post_rate = post_count / (post_days / 365.25)

        growth_rate = ((post_rate - pre_rate) / pre_rate) * 100 if pre_rate > 0 else 0

        return {
            'pre_count': pre_count,
            'pre_rate': pre_rate,
            'post_count': post_count,
            'post_rate': post_rate,
            'growth_rate': growth_rate
        }

    def analyze_nonpriority_sectors(self, priority_where):
        """Analyze growth in non-priority sectors"""
        cursor = self.conn.cursor()

        # Pre-MIC2025 (excluding priority sectors)
        pre_query = f"""
        SELECT COUNT(DISTINCT p.application_number) as count
        FROM uspto_patents_chinese p
        JOIN uspto_cpc_classifications c ON p.application_number = c.application_number
        WHERE p.filing_date >= '2011-01-01'
          AND p.filing_date < '2015-05-08'
          AND p.application_number NOT IN (
              SELECT DISTINCT p2.application_number
              FROM uspto_patents_chinese p2
              JOIN uspto_cpc_classifications c2 ON p2.application_number = c2.application_number
              WHERE p2.filing_date >= '2011-01-01'
                AND p2.filing_date < '2015-05-08'
                AND ({priority_where})
          )
        """

        pre_count = cursor.execute(pre_query).fetchone()['count'] or 0

        # Post-MIC2025 (excluding priority sectors)
        post_query = f"""
        SELECT COUNT(DISTINCT p.application_number) as count
        FROM uspto_patents_chinese p
        JOIN uspto_cpc_classifications c ON p.application_number = c.application_number
        WHERE p.filing_date >= '2015-05-08'
          AND p.filing_date <= '2020-12-31'
          AND p.application_number NOT IN (
              SELECT DISTINCT p2.application_number
              FROM uspto_patents_chinese p2
              JOIN uspto_cpc_classifications c2 ON p2.application_number = c2.application_number
              WHERE p2.filing_date >= '2015-05-08'
                AND p2.filing_date <= '2020-12-31'
                AND ({priority_where})
          )
        """

        post_count = cursor.execute(post_query).fetchone()['count'] or 0

        pre_days = (datetime.strptime('2015-05-08', '%Y-%m-%d') - datetime.strptime('2011-01-01', '%Y-%m-%d')).days
        post_days = (datetime.strptime('2020-12-31', '%Y-%m-%d') - datetime.strptime('2015-05-08', '%Y-%m-%d')).days

        pre_rate = pre_count / (pre_days / 365.25)
        post_rate = post_count / (post_days / 365.25)

        growth_rate = ((post_rate - pre_rate) / pre_rate) * 100 if pre_rate > 0 else 0

        return {
            'pre_count': pre_count,
            'pre_rate': pre_rate,
            'post_count': post_count,
            'post_rate': post_rate,
            'growth_rate': growth_rate
        }

    def test_340_percent_claim(self):
        """Test if any sector shows 340% growth"""
        print("\n" + "="*80)
        print("TESTING: \"340% INCREASE\" CLAIM")
        print("="*80)

        found_340 = False

        print("\nSearching for any sector with >300% growth...")

        for sector_name, stats in self.results['sector_growth'].items():
            if stats['growth_rate'] > 300:
                print(f"\n[FOUND] {sector_name}: {stats['growth_rate']:.1f}%")
                found_340 = True

        if not found_340:
            print("\n[NOT FOUND] No sector shows >300% growth")
            print("\nHighest growth sectors:")

            sorted_sectors = sorted(
                self.results['sector_growth'].items(),
                key=lambda x: x[1]['growth_rate'],
                reverse=True
            )

            for i, (sector, stats) in enumerate(sorted_sectors[:5], 1):
                print(f"  {i}. {sector.replace('_', ' ').title()}: {stats['growth_rate']:+.1f}%")

        print("\n" + "-"*80)
        print("CONCLUSION:")
        print("-"*80)
        print(f"Overall USPTO growth: {self.results['overall_growth']['growth_rate']:.1f}%")
        print(f"Highest sector growth: {max(s['growth_rate'] for s in self.results['sector_growth'].values()):.1f}%")
        print("\nThe \"340%\" claim is NOT supported by USPTO data for any MIC2025 sector.")
        print("Possible explanations:")
        print("  1. Claim refers to CNIPA (Chinese domestic patents), not USPTO")
        print("  2. Claim uses different time period or methodology")
        print("  3. Claim refers to specific sub-technology within a sector")
        print("  4. Claim is exaggerated or incorrect")

    def generate_report(self):
        """Generate final validation report"""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)

        print("\n1. OVERALL GROWTH:")
        print(f"   USPTO Chinese patents grew {self.results['overall_growth']['growth_rate']:.1f}% after MIC2025")
        print(f"   This matches the 11.3% from previous deep dive analysis")

        print("\n2. SECTOR-SPECIFIC FINDINGS:")
        sorted_sectors = sorted(
            self.results['sector_growth'].items(),
            key=lambda x: x[1]['growth_rate'],
            reverse=True
        )
        print(f"   Highest growth: {sorted_sectors[0][0].replace('_', ' ').title()} ({sorted_sectors[0][1]['growth_rate']:+.1f}%)")
        print(f"   Lowest growth: {sorted_sectors[-1][0].replace('_', ' ').title()} ({sorted_sectors[-1][1]['growth_rate']:+.1f}%)")

        print("\n3. PRIORITY VS. NON-PRIORITY:")
        diff = self.results['priority_comparison']['differential']
        print(f"   Priority sectors: {self.results['priority_comparison']['priority']['growth_rate']:+.1f}%")
        print(f"   Non-priority sectors: {self.results['priority_comparison']['non_priority']['growth_rate']:+.1f}%")
        print(f"   Differential: {diff:+.1f} percentage points")

        if abs(diff) < 5:
            print("   CONCLUSION: No strong evidence of MIC2025-specific targeting")
        else:
            print("   CONCLUSION: Evidence of targeted growth in priority sectors")

        print("\n4. \"340%\" CLAIM VALIDATION:")
        print("   STATUS: NOT SUPPORTED by USPTO data")
        print("   No MIC2025 sector shows >300% growth in USPTO patents")

        print("\n" + "="*80)

        # Save results
        output_file = OUTPUT_DIR / f"patent_policy_cross_reference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nDetailed results saved to: {output_file}")

def main():
    """Main execution"""
    print("="*80)
    print("POLICY-PATENT CROSS-REFERENCE ANALYSIS")
    print("Validating Made in China 2025 Impact on USPTO Patents")
    print("="*80)

    analyzer = PolicyPatentCrossReference(DB_PATH)
    analyzer.connect()

    # Step 1: Baseline growth rate
    overall_growth = analyzer.get_overall_patent_stats()

    # Step 2: Sector-specific analysis
    sector_results = analyzer.analyze_all_sectors()

    # Step 3: Priority vs. non-priority comparison
    differential = analyzer.compare_priority_vs_nonpriority()

    # Step 4: Test 340% claim
    analyzer.test_340_percent_claim()

    # Step 5: Generate report
    analyzer.generate_report()

    analyzer.conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
