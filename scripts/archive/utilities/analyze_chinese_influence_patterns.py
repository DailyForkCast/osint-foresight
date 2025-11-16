#!/usr/bin/env python3
"""
Enhanced TED Analysis: Chinese Influence & Participation Tracking
Distinguishes between:
  1. Direct Chinese Contractors (business transactions)
  2. Chinese Influence/Participation (trade missions, cooperation, BRI)
  3. Geographic References (informational only)
  4. False Positives (innocent references)
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


class ChineseInfluenceAnalyzer:
    """Analyze TED contracts for Chinese influence patterns"""

    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

        # Load revalidation results
        self.results_file = self.find_latest_revalidation_results()
        with open(self.results_file, 'r', encoding='utf-8') as f:
            self.all_results = json.load(f)

        # Intelligence pattern definitions
        self.influence_patterns = {
            'trade_mission': [
                r'\b(trade\s+mission|business\s+mission|commercial\s+mission)\s+(to|with|in)\s+china\b',
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
            'belt_road_initiative': [
                r'\bbelt\s+and\s+road\b',
                r'\bbri\b',
                r'\bone\s+belt\s+one\s+road\b',
                r'\bsilk\s+road\s+(initiative|project|program|programme)\b',
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

        # Priority categorization
        if 'belt_road_initiative' in influence:
            return 'BRI_RELATED'
        elif 'trade_mission' in influence or 'cooperation_program' in influence:
            return 'CHINA_COOPERATION'
        elif 'chinese_funding' in influence:
            return 'CHINESE_FUNDED'
        elif 'seventeen_plus_one' in influence:
            return '17PLUS1_INITIATIVE'
        elif 'hong_kong_office' in reference:
            return 'HK_REFERENCE'
        elif reference:
            return 'GEOGRAPHIC_REFERENCE'
        else:
            return 'NO_INFLUENCE_DETECTED'

    def analyze_all_uncertain(self):
        """Analyze all uncertain contracts for influence patterns"""

        print("\n" + "="*80)
        print("CHINESE INFLUENCE & PARTICIPATION ANALYSIS")
        print("="*80)
        print()

        # Get uncertain and false positive contracts
        uncertain = [r for r in self.all_results if r['category'] == 'UNCERTAIN']

        print(f"Analyzing {len(uncertain)} uncertain contracts for influence patterns...")
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
            'BRI_RELATED',
            'CHINA_COOPERATION',
            'CHINESE_FUNDED',
            '17PLUS1_INITIATIVE',
            'HK_REFERENCE',
            'GEOGRAPHIC_REFERENCE',
            'NO_INFLUENCE_DETECTED'
        ]

        for category in priority_order:
            count = len(categories[category])
            if count > 0:
                pct = count / len(analyses) * 100 if analyses else 0
                print(f"{category:30} {count:4d} ({pct:5.1f}%)")

        print("-"*80)

        # Show samples
        print()
        print("=== HIGH PRIORITY: BRI-RELATED CONTRACTS ===")
        for contract in categories['BRI_RELATED'][:5]:
            print(f"  - {contract['contract_title'][:80]}")
            print(f"    CA: {contract['ca_name'][:60]}")
            print(f"    Patterns: {list(contract['influence_patterns'].keys())}")
            print()

        print()
        print("=== HIGH PRIORITY: CHINA COOPERATION PROGRAMS ===")
        for contract in categories['CHINA_COOPERATION'][:5]:
            print(f"  - {contract['contract_title'][:80]}")
            print(f"    CA: {contract['ca_name'][:60]}")
            print(f"    Patterns: {list(contract['influence_patterns'].keys())}")
            print()

        # Save detailed results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path(f"analysis/ted_chinese_influence_analysis_{timestamp}.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total_analyzed': len(analyses),
                'categorization': {cat: len(contracts) for cat, contracts in categories.items()},
                'contracts': analyses
            }, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] Detailed analysis saved to: {output_file}")

        return categories, analyses

    def generate_influence_report(self, categories, analyses):
        """Generate intelligence report on Chinese influence"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        report = f"""# TED Contracts: Chinese Influence & Participation Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Contracts Analyzed:** {len(analyses)}
**Intelligence Focus:** Beyond direct contractors - tracking Chinese influence

---

## Executive Summary

This analysis identifies EU procurement contracts that indicate **Chinese influence or participation** even when the contractor is not directly Chinese. This includes:

- Belt and Road Initiative projects
- EU-China trade missions and cooperation programs
- Chinese-funded initiatives
- 17+1 (China-CEEC) cooperation
- Geographic references (Hong Kong offices, etc.)

### Key Findings

| Category | Count | Percentage | Intelligence Priority |
|----------|-------|------------|----------------------|
| **BRI-Related** | {len(categories['BRI_RELATED'])} | {len(categories['BRI_RELATED'])/len(analyses)*100:.1f}% | 🔴 **HIGH** |
| **China Cooperation Programs** | {len(categories['CHINA_COOPERATION'])} | {len(categories['CHINA_COOPERATION'])/len(analyses)*100:.1f}% | 🔴 **HIGH** |
| **Chinese Funded** | {len(categories['CHINESE_FUNDED'])} | {len(categories['CHINESE_FUNDED'])/len(analyses)*100:.1f}% | 🟠 **MEDIUM-HIGH** |
| **17+1 Initiative** | {len(categories['17PLUS1_INITIATIVE'])} | {len(categories['17PLUS1_INITIATIVE'])/len(analyses)*100:.1f}% | 🟠 **MEDIUM-HIGH** |
| **Hong Kong Reference** | {len(categories['HK_REFERENCE'])} | {len(categories['HK_REFERENCE'])/len(analyses)*100:.1f}% | 🟡 **LOW-MEDIUM** |
| **Geographic Reference** | {len(categories['GEOGRAPHIC_REFERENCE'])} | {len(categories['GEOGRAPHIC_REFERENCE'])/len(analyses)*100:.1f}% | 🟢 **LOW** |
| **No Influence Detected** | {len(categories['NO_INFLUENCE_DETECTED'])} | {len(categories['NO_INFLUENCE_DETECTED'])/len(analyses)*100:.1f}% | ⚪ **NONE** |

---

## High Priority: Belt and Road Initiative (BRI)

**Count:** {len(categories['BRI_RELATED'])}
**Why Important:** BRI projects often involve Chinese financing, contractors, and strategic influence

### Sample BRI-Related Contracts

"""

        for i, contract in enumerate(categories['BRI_RELATED'][:10], 1):
            report += f"""
#### {i}. {contract['contract_title'][:100]}

- **Contracting Authority:** {contract['ca_name'][:80]}
- **Country:** {contract['ca_country']}
- **Date:** {contract['publication_date']}
- **Value:** {contract['contract_value']} {contract['currency']}
- **Patterns Detected:** {', '.join(contract['influence_patterns'].keys())}

"""

        report += f"""
---

## High Priority: China Cooperation Programs

**Count:** {len(categories['CHINA_COOPERATION'])}
**Why Important:** Indicates Chinese participation/involvement in EU programs

### Sample Cooperation Contracts

"""

        for i, contract in enumerate(categories['CHINA_COOPERATION'][:10], 1):
            report += f"""
#### {i}. {contract['contract_title'][:100]}

- **Contracting Authority:** {contract['ca_name'][:80]}
- **Country:** {contract['ca_country']}
- **Date:** {contract['publication_date']}
- **Value:** {contract['contract_value']} {contract['currency']}
- **Patterns Detected:** {', '.join(contract['influence_patterns'].keys())}

"""

        report += f"""
---

## Medium Priority: Chinese Funded & 17+1 Initiative

### Chinese Funded Projects ({len(categories['CHINESE_FUNDED'])})

"""

        for contract in categories['CHINESE_FUNDED'][:5]:
            report += f"- {contract['contract_title'][:80]} ({contract['ca_country']})\n"

        report += f"""

### 17+1 (China-CEEC) Initiative ({len(categories['17PLUS1_INITIATIVE'])})

"""

        for contract in categories['17PLUS1_INITIATIVE'][:5]:
            report += f"- {contract['contract_title'][:80]} ({contract['ca_country']})\n"

        report += f"""

---

## Low Priority: Geographic References

### Hong Kong Offices ({len(categories['HK_REFERENCE'])})

"""
        for contract in categories['HK_REFERENCE'][:5]:
            report += f"- {contract['contract_title'][:80]} ({contract['ca_country']})\n"

        report += f"""

**Note:** Hong Kong office references noted for awareness but not critical indicators alone.

### Other Geographic References ({len(categories['GEOGRAPHIC_REFERENCE'])})

"""
        for contract in categories['GEOGRAPHIC_REFERENCE'][:5]:
            report += f"- {contract['contract_title'][:80]} ({contract['ca_country']})\n"

        report += """

---

## Recommendations

### Track as Chinese Influence (Not Just Contractors)

1. **BRI Projects** - Monitor for Chinese financing, influence, strategic positioning
2. **Cooperation Programs** - Track Chinese participation in EU programs
3. **Trade Missions** - Note Chinese involvement in EU business activities

### Maintain Separate Categories

**Direct Chinese Contractors:**
- 151 confirmed (from revalidation)
- Clear business transactions with Chinese companies

**Chinese Influence/Participation:**
- BRI, cooperation programs, trade missions
- Indirect Chinese involvement/influence
- Strategic intelligence value

### Database Schema Recommendation

Add new fields to track influence:
```sql
ALTER TABLE ted_contracts_production ADD COLUMN chinese_influence_type TEXT;
ALTER TABLE ted_contracts_production ADD COLUMN influence_patterns TEXT;
ALTER TABLE ted_contracts_production ADD COLUMN intelligence_priority TEXT;
```

---

## Files Generated

1. **This Report:** `analysis/TED_CHINESE_INFLUENCE_REPORT_{timestamp}.md`
2. **Detailed Data:** `analysis/ted_chinese_influence_analysis_{timestamp}.json`

---

**Analysis Status:** Complete
**Intelligence Value:** High - reveals indirect Chinese involvement
**Next Step:** Review high-priority BRI and cooperation contracts
"""

        # Save report
        report_file = Path(f"analysis/TED_CHINESE_INFLUENCE_REPORT_{timestamp}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"[SUCCESS] Intelligence report saved to: {report_file}")

        return report_file

    def run_analysis(self):
        """Run complete influence analysis"""

        print("\n" + "="*80)
        print("CHINESE INFLUENCE & PARTICIPATION ANALYSIS")
        print("Tracking: BRI, Trade Missions, Cooperation Programs, Funding")
        print("="*80)

        # Analyze contracts
        categories, analyses = self.analyze_all_uncertain()

        # Generate report
        report_file = self.generate_influence_report(categories, analyses)

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"\nHigh Priority Findings:")
        print(f"  - BRI-Related: {len(categories['BRI_RELATED'])}")
        print(f"  - China Cooperation: {len(categories['CHINA_COOPERATION'])}")
        print(f"  - Chinese Funded: {len(categories['CHINESE_FUNDED'])}")
        print(f"  - 17+1 Initiative: {len(categories['17PLUS1_INITIATIVE'])}")
        print()
        print(f"Report saved to: {report_file}")
        print()

        return categories, report_file


if __name__ == '__main__':
    analyzer = ChineseInfluenceAnalyzer()
    categories, report_file = analyzer.run_analysis()
