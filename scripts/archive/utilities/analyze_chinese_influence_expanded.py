#!/usr/bin/env python3
"""
Expanded TED Chinese Influence Analysis
Per user requirements:
  - Track trade events with China
  - Track promotional events with China
  - Track ALL European Commission INTPA contracts (radar tracking)
  - Track cooperation programs (confirmed)
  - Track BRI projects
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


class ExpandedInfluenceAnalyzer:
    """Expanded influence pattern tracking per user requirements"""

    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

        # Load revalidation results
        self.results_file = self.find_latest_revalidation_results()
        with open(self.results_file, 'r', encoding='utf-8') as f:
            self.all_results = json.load(f)

        # EXPANDED Intelligence pattern definitions
        self.influence_patterns = {
            'trade_mission': [
                r'\b(trade\s+mission|business\s+mission|commercial\s+mission)\s+(to|with|in)?\s*china\b',
                r'\bchina[-\s]eu\s+(trade|business|commercial)\b',
                r'\beu[-\s]china\s+(trade|business|commercial)\b'
            ],
            'cooperation_program': [
                r'\b(china|chinese)[-\s](cooperation|partnership|collaboration)\s+(program|programme|project|initiative)\b',
                r'\beu[-\s]china\s+(cooperation|partnership|collaboration)\b',
                r'\bchina[-\s]eu\s+(cooperation|partnership|collaboration)\b',
                r'\bjoint\s+(program|programme|project)\s+with\s+china\b',
                r'\bbilateral\s+(program|programme|project)\s+(with\s+)?china\b'
            ],
            'trade_event': [
                # NEW: Trade exhibitions, conferences, trade shows
                r'\b(trade\s+)?(exhibition|expo|fair|show)\b.*\bchina\b',
                r'\bchina\b.{0,50}\b(exhibition|expo|fair|show)\b',
                r'\b(conference|summit|forum)\b.*\b(china|chinese)\b',
                r'\b(china|chinese)\b.{0,50}\b(conference|summit|forum)\b',
                r'\btrade\s+(event|gathering|meeting)\b.*\bchina\b',
                r'\bbusiness\s+(event|conference|forum)\b.*\bchina\b'
            ],
            'promotional_event': [
                # NEW: Investment/business promotion
                r'\b(investment|business)\s+promotion\b.*\bchina\b',
                r'\bchina\b.{0,50}\b(investment|business)\s+promotion\b',
                r'\bpromot(e|ing)\b.*\b(china|chinese)\b.*\b(investment|business|trade)\b',
                r'\b(economic|commercial)\s+promotion\b.*\bchina\b'
            ],
            'belt_road_initiative': [
                r'\bbelt\s+and\s+road\b',
                r'\bbri\b',
                r'\bone\s+belt\s+one\s+road\b',
                r'\bsilk\s+road\s+(initiative|project|program|programme)?\b',
                r'\b(new\s+)?silk\s+road\b'
            ],
            'chinese_funding': [
                r'\bchinese\s+(funded|financed|financing|investment)\b',
                r'\bfunding\s+from\s+china\b',
                r'\bchina\s+(investment|financing)\b',
                r'\bchinese\s+development\s+bank\b'
            ],
            'seventeen_plus_one': [
                r'\b17\+1\b',
                r'\bseventeen\s+plus\s+one\b',
                r'\bchina[-\s]ceec\b',
                r'\bcentral\s+and\s+eastern\s+european\s+countries.*china\b'
            ]
        }

        self.reference_patterns = {
            'hong_kong_office': [
                r'\bhong\s+kong\s+(office|liaison|representative|branch)\b',
                r'\bhk\s+(office|liaison|representative)\b'
            ],
            'geographic_reference': [
                r'\b(beijing|shanghai|shenzhen|guangzhou)\s+(office|representative|liaison)\b',
                r'\bchina\s+(desk|unit|department)\b'
            ],
            'academic_cultural': [
                r'\bchinese\s+(language|studies|culture|history|art)\b',
                r'\bconfucius\s+institute\b',
                r'\bchina\s+(studies|research)\s+(program|centre|center)\b',
                r'\bcultural\s+exchange.*china\b'
            ]
        }

    def find_latest_revalidation_results(self):
        """Find most recent revalidation results"""
        analysis_dir = Path("analysis")
        files = list(analysis_dir.glob("ted_revalidation_detailed_*.json"))
        if not files:
            raise FileNotFoundError("No revalidation results found!")
        latest = max(files, key=lambda p: p.stat().st_mtime)
        return latest

    def is_intpa_contract(self, contract_data):
        """Check if contract is from European Commission INTPA"""
        ca_name = str(contract_data['ca_name'] or '').lower()

        # Check for INTPA indicators
        intpa_patterns = [
            'intpa',
            'international partnerships',
            'directorate-general for international partnerships',
            'dg intpa'
        ]

        for pattern in intpa_patterns:
            if pattern in ca_name:
                return True

        return False

    def analyze_for_influence(self, contract):
        """Analyze contract for Chinese influence patterns"""

        # Get full contract data
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        full_contract = cursor.execute("""
            SELECT contract_title, contract_description, ca_name,
                   contractor_name, contractor_address, contractor_city,
                   cpv_code, value_total, currency, publication_date
            FROM ted_contracts_production
            WHERE id = ?
        """, (contract['id'],)).fetchone()
        conn.close()

        if not full_contract:
            return None

        # Combine text for pattern matching
        combined_text = ' '.join([
            str(full_contract['contract_title'] or ''),
            str(full_contract['contract_description'] or ''),
            str(full_contract['ca_name'] or ''),
            str(contract.get('contractor_name') or '')
        ]).lower()

        # Check for influence patterns
        influence_matches = {}
        for category, patterns in self.influence_patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    matches.append(pattern)
            if matches:
                influence_matches[category] = matches

        # Check for reference patterns
        reference_matches = {}
        for category, patterns in self.reference_patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    matches.append(pattern)
            if matches:
                reference_matches[category] = matches

        # Check if INTPA contract
        is_intpa = self.is_intpa_contract(full_contract)

        return {
            'contract_id': contract['id'],
            'notice_number': contract.get('notice_number'),
            'publication_date': full_contract['publication_date'],
            'ca_country': contract.get('ca_country'),
            'ca_name': full_contract['ca_name'],
            'contractor_name': full_contract['contractor_name'],
            'contract_title': full_contract['contract_title'],
            'contract_value': full_contract['value_total'],
            'currency': full_contract['currency'],
            'influence_patterns': influence_matches,
            'reference_patterns': reference_matches,
            'is_intpa': is_intpa,
            'original_category': contract.get('category'),
            'has_influence': len(influence_matches) > 0,
            'has_reference': len(reference_matches) > 0
        }

    def categorize_intelligence(self, analysis):
        """Categorize contract for intelligence purposes"""

        if not analysis:
            return 'UNKNOWN'

        influence = analysis['influence_patterns']
        reference = analysis['reference_patterns']
        is_intpa = analysis['is_intpa']

        # Priority categorization
        if 'belt_road_initiative' in influence:
            return 'BRI_RELATED'
        elif 'cooperation_program' in influence:
            return 'CHINA_COOPERATION'
        elif 'trade_mission' in influence:
            return 'TRADE_MISSION'
        elif 'trade_event' in influence:
            return 'TRADE_EVENT'  # NEW
        elif 'promotional_event' in influence:
            return 'PROMOTIONAL_EVENT'  # NEW
        elif 'chinese_funding' in influence:
            return 'CHINESE_FUNDED'
        elif 'seventeen_plus_one' in influence:
            return '17PLUS1_INITIATIVE'
        elif is_intpa:
            return 'INTPA_RADAR'  # NEW: Track all INTPA for radar
        elif 'hong_kong_office' in reference:
            return 'HK_REFERENCE'
        elif reference:
            return 'GEOGRAPHIC_REFERENCE'
        else:
            return 'NO_INFLUENCE_DETECTED'

    def analyze_all_uncertain(self):
        """Analyze all uncertain contracts for influence patterns"""

        print("\n" + "="*80)
        print("EXPANDED CHINESE INFLUENCE ANALYSIS")
        print("="*80)
        print()
        print("New Categories Added:")
        print("  - Trade Events (exhibitions, conferences, trade shows)")
        print("  - Promotional Events (investment/business promotion)")
        print("  - INTPA Radar (all European Commission INTPA contracts)")
        print()

        # Get uncertain contracts
        uncertain = [r for r in self.all_results if r['category'] == 'UNCERTAIN']

        print(f"Analyzing {len(uncertain)} uncertain contracts...")
        print()

        # Analyze each contract
        analyses = []
        categories = defaultdict(list)

        for i, contract in enumerate(uncertain, 1):
            if i % 25 == 0:
                print(f"  Processed {i}/{len(uncertain)}...")

            analysis = self.analyze_for_influence(contract)
            if analysis:
                category = self.categorize_intelligence(analysis)
                analysis['intelligence_category'] = category
                analyses.append(analysis)
                categories[category].append(analysis)

        print(f"  Completed {len(analyses)} contracts")
        print()

        # Print summary
        print("-"*80)
        print("INTELLIGENCE CATEGORIZATION RESULTS")
        print("-"*80)

        priority_order = [
            ('BRI_RELATED', 'HIGH'),
            ('CHINA_COOPERATION', 'HIGH'),
            ('TRADE_MISSION', 'HIGH'),
            ('TRADE_EVENT', 'MEDIUM-HIGH'),  # NEW
            ('PROMOTIONAL_EVENT', 'MEDIUM-HIGH'),  # NEW
            ('CHINESE_FUNDED', 'MEDIUM-HIGH'),
            ('17PLUS1_INITIATIVE', 'MEDIUM-HIGH'),
            ('INTPA_RADAR', 'MEDIUM'),  # NEW
            ('HK_REFERENCE', 'LOW-MEDIUM'),
            ('GEOGRAPHIC_REFERENCE', 'LOW'),
            ('NO_INFLUENCE_DETECTED', 'NONE')
        ]

        for category, priority in priority_order:
            count = len(categories[category])
            if count > 0:
                pct = count / len(analyses) * 100 if analyses else 0
                print(f"{category:30} {count:4d} ({pct:5.1f}%)  [{priority}]")

        print("-"*80)

        # Show samples of new categories
        if categories['TRADE_EVENT']:
            print("\n=== NEW: TRADE EVENTS ===")
            for contract in categories['TRADE_EVENT'][:5]:
                print(f"  - {contract['contract_title'][:80]}")
                print(f"    Patterns: {list(contract['influence_patterns'].keys())}")
                print()

        if categories['PROMOTIONAL_EVENT']:
            print("=== NEW: PROMOTIONAL EVENTS ===")
            for contract in categories['PROMOTIONAL_EVENT'][:5]:
                print(f"  - {contract['contract_title'][:80]}")
                print(f"    Patterns: {list(contract['influence_patterns'].keys())}")
                print()

        if categories['INTPA_RADAR']:
            print("=== NEW: INTPA RADAR TRACKING ===")
            for contract in categories['INTPA_RADAR'][:5]:
                print(f"  - {contract['contract_title'][:80]}")
                print(f"    CA: {contract['ca_name'][:60]}")
                print()

        # Save detailed results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path(f"analysis/ted_influence_expanded_{timestamp}.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total_analyzed': len(analyses),
                'categorization': {cat: len(contracts) for cat, contracts in categories.items()},
                'contracts': analyses
            }, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] Expanded analysis saved to: {output_file}")
        print()

        return categories, analyses

    def run_analysis(self):
        """Run complete expanded influence analysis"""

        print("\n" + "="*80)
        print("EXPANDED CHINESE INFLUENCE & PARTICIPATION ANALYSIS")
        print("="*80)

        # Analyze contracts
        categories, analyses = self.analyze_all_uncertain()

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print()
        print("High Priority Findings:")
        print(f"  - BRI-Related: {len(categories['BRI_RELATED'])}")
        print(f"  - China Cooperation: {len(categories['CHINA_COOPERATION'])}")
        print(f"  - Trade Missions: {len(categories['TRADE_MISSION'])}")
        print()
        print("New Category Findings:")
        print(f"  - Trade Events: {len(categories['TRADE_EVENT'])}")
        print(f"  - Promotional Events: {len(categories['PROMOTIONAL_EVENT'])}")
        print(f"  - INTPA Radar: {len(categories['INTPA_RADAR'])}")
        print()

        return categories, analyses


if __name__ == '__main__':
    analyzer = ExpandedInfluenceAnalyzer()
    categories, analyses = analyzer.run_analysis()
