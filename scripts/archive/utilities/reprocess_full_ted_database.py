#!/usr/bin/env python3
"""
Full TED Database Reprocessing
Applies improved detection to all 1,131,420 contracts:
  1. Chinese contractor detection (word boundaries, Nuctech, +10 companies)
  2. Influence pattern detection (cooperation, trade events, INTPA)
  3. Updates database with comprehensive flags
"""

import sqlite3
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class FullTEDReprocessor:
    """Reprocess entire TED database with improved detection"""

    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

        # Enhanced Chinese company patterns (with word boundaries)
        self.china_patterns = [
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bguangzhou\b', r'\bshenzhen\b', r'\bhong kong\b', r'\bmacau\b',
            r'\bhuawei\b', r'\bzte\b', r'\balibaba\b', r'\btencent\b',
            r'\bsinopec\b', r'\bpetrochina\b', r'\blenovo\b', r'\bxiaomi\b',
            r'\bbyd\b', r'\bcosco\b', r'\bcnooc\b', r'\bcnpc\b', r'\bnuctech\b',
            r'\bhikvision\b', r'\bdahua\b', r'\bdji\b', r'\bbgi\b', r'\bcimc\b',
            r'\bcrrc\b', r'\bcomac\b', r'\bavic\b', r'\bnorinco\b', r'\bcasic\b'
        ]

        # Known Chinese companies (exact match)
        self.known_companies = [
            'Huawei', 'ZTE', 'SMIC', 'CNOOC', 'Sinopec', 'CNPC', 'PetroChina',
            'Xiaomi', 'BYD', 'CATL', 'Hikvision', 'Dahua', 'Alibaba', 'Tencent',
            'Baidu', 'China Mobile', 'China Telecom', 'China Unicom',
            'CRRC', 'COMAC', 'AVIC', 'Norinco', 'CETC', 'CASC', 'CASIC',
            'COSCO', 'China State Construction', 'PowerChina', 'CITIC', 'Nuctech',
            'Lenovo', 'DJI', 'BGI', 'CIMC', 'CNR Corporation'
        ]

        # Influence pattern definitions
        self.influence_patterns = {
            'cooperation_program': [
                r'\b(china|chinese)[-\s](cooperation|partnership|collaboration)\s+(program|programme|project|initiative)\b',
                r'\beu[-\s]china\s+(cooperation|partnership|collaboration)\b',
                r'\bchina[-\s]eu\s+(cooperation|partnership|collaboration)\b',
                r'\bjoint\s+(program|programme|project)\s+with\s+china\b',
                r'\bbilateral\s+(program|programme|project)\s+(with\s+)?china\b'
            ],
            'trade_mission': [
                r'\b(trade\s+mission|business\s+mission|commercial\s+mission)\s+(to|with|in)?\s*china\b',
                r'\bchina[-\s]eu\s+(trade|business|commercial)\b',
                r'\beu[-\s]china\s+(trade|business|commercial)\b'
            ],
            'trade_event': [
                r'\b(trade\s+)?(exhibition|expo|fair|show)\b.*\bchina\b',
                r'\bchina\b.{0,50}\b(exhibition|expo|fair|show)\b',
                r'\b(conference|summit|forum)\b.*\b(china|chinese)\b',
                r'\b(china|chinese)\b.{0,50}\b(conference|summit|forum)\b',
                r'\btrade\s+(event|gathering|meeting)\b.*\bchina\b',
                r'\bbusiness\s+(event|conference|forum)\b.*\bchina\b'
            ],
            'promotional_event': [
                r'\b(investment|business)\s+promotion\b.*\bchina\b',
                r'\bchina\b.{0,50}\b(investment|business)\s+promotion\b',
                r'\bpromot(e|ing)\b.*\b(china|chinese)\b.*\b(investment|business|trade)\b',
                r'\b(economic|commercial)\s+promotion\b.*\bchina\b'
            ],
            'belt_road_initiative': [
                r'\bbelt\s+and\s+road\s+(initiative|project|program|programme)?\b',
                r'\bone\s+belt\s+one\s+road\b',
                r'\bsilk\s+road\s+(initiative|project|program|programme)\b',
                r'\b(china|chinese).{0,50}\bbri\b',  # BRI with China context
                r'\bbri\b.{0,50}\b(china|chinese)\b'  # BRI with China context
            ],
            'chinese_funding': [
                r'\bchinese\s+(funded|financed|financing|investment)\b',
                r'\bfunding\s+from\s+china\b',
                r'\bchina\s+(investment|financing)\b',
                r'\bchinese\s+development\s+bank\b'
            ],
            'seventeen_plus_one': [
                r'\bseventeen\s+plus\s+one\b',  # Full phrase only
                r'\bchina[-\s]ceec\b',  # China-CEEC reference
                r'\b(china|chinese).{0,50}\b17\+1\b',  # 17+1 with China context
                r'\b17\+1\b.{0,50}\b(china|chinese|ceec)\b'  # 17+1 with China/CEEC context
                # REMOVED: standalone r'\b17\+1\b' - matches bus seating capacity
            ]
        }

        # Stats tracking
        self.stats = {
            'total_processed': 0,
            'chinese_contractors': 0,
            'influence_contracts': 0,
            'intpa_contracts': 0,
            'by_detection_method': defaultdict(int),
            'by_influence_category': defaultdict(int)
        }

    def detect_chinese_contractor(self, contract):
        """Detect if contract has Chinese contractor"""

        # Country code check (high confidence)
        contractor_country = (contract.get('contractor_country') or '').upper()
        if contractor_country in ['CN', 'CHN', 'HK', 'HKG', 'MAC']:
            return True, 'CN/HK country code', 0.95

        # Known company check (high confidence)
        contractor_name = str(contract.get('contractor_name') or '')
        for company in self.known_companies:
            if company.lower() in contractor_name.lower():
                return True, f'Known company: {company}', 0.90

        # Pattern matching in combined text (medium confidence)
        combined_text = ' '.join([
            str(contract.get('contract_title') or ''),
            str(contract.get('contract_description') or ''),
            str(contract.get('contractor_name') or ''),
            str(contract.get('contractor_address') or '')
        ]).lower()

        matches = []
        for pattern in self.china_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                matches.append(pattern)

        if len(matches) >= 3:
            return True, f'{len(matches)} strong pattern matches', 0.75
        elif len(matches) >= 2:
            return True, f'{len(matches)} pattern matches', 0.60
        elif len(matches) == 1:
            # Single pattern match - uncertain
            return 'uncertain', f'1 pattern match: {matches[0]}', 0.40

        return False, 'No patterns detected', 0.0

    def detect_influence_patterns(self, contract):
        """Detect Chinese influence patterns"""

        combined_text = ' '.join([
            str(contract.get('contract_title') or ''),
            str(contract.get('contract_description') or ''),
            str(contract.get('ca_name') or '')
        ]).lower()

        detected_patterns = {}

        for category, patterns in self.influence_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    if category not in detected_patterns:
                        detected_patterns[category] = []
                    detected_patterns[category].append(pattern)

        return detected_patterns

    def is_intpa_contract(self, contract):
        """Check if contract is from European Commission INTPA"""
        ca_name = str(contract.get('ca_name') or '').lower()

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

    def categorize_influence(self, influence_patterns):
        """Categorize influence for priority"""

        if 'belt_road_initiative' in influence_patterns:
            return 'BRI_RELATED', 'HIGH'
        elif 'cooperation_program' in influence_patterns:
            return 'CHINA_COOPERATION', 'HIGH'
        elif 'trade_mission' in influence_patterns:
            return 'TRADE_MISSION', 'HIGH'
        elif 'trade_event' in influence_patterns:
            return 'TRADE_EVENT', 'MEDIUM-HIGH'
        elif 'promotional_event' in influence_patterns:
            return 'PROMOTIONAL_EVENT', 'MEDIUM-HIGH'
        elif 'chinese_funding' in influence_patterns:
            return 'CHINESE_FUNDED', 'MEDIUM-HIGH'
        elif 'seventeen_plus_one' in influence_patterns:
            return '17PLUS1_INITIATIVE', 'MEDIUM-HIGH'

        return None, None

    def process_batch(self, contracts):
        """Process a batch of contracts"""

        updates = []

        for contract in contracts:
            self.stats['total_processed'] += 1

            # Detect Chinese contractor
            is_chinese, reason, confidence = self.detect_chinese_contractor(contract)

            # Detect influence patterns
            influence_patterns = self.detect_influence_patterns(contract)

            # Check INTPA
            is_intpa = self.is_intpa_contract(contract)

            # Categorize
            influence_category = None
            influence_priority = None

            if influence_patterns:
                influence_category, influence_priority = self.categorize_influence(influence_patterns)

            if is_intpa and not influence_category:
                influence_category = 'INTPA_RADAR'
                influence_priority = 'MEDIUM'

            # Track stats
            if is_chinese == True:
                self.stats['chinese_contractors'] += 1
                self.stats['by_detection_method'][reason.split(':')[0]] += 1

            if influence_category:
                self.stats['influence_contracts'] += 1
                self.stats['by_influence_category'][influence_category] += 1

            if is_intpa:
                self.stats['intpa_contracts'] += 1

            # Prepare update
            updates.append({
                'id': contract['id'],
                'is_chinese_related': 1 if is_chinese == True else 0,
                'chinese_confidence': confidence,
                'detection_rationale': reason,
                'influence_category': influence_category,
                'influence_priority': influence_priority,
                'influence_patterns': json.dumps(list(influence_patterns.keys())) if influence_patterns else None,
                'is_intpa_contract': 1 if is_intpa else 0
            })

        return updates

    def add_schema_columns(self):
        """Add new columns to database schema"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Add new columns if they don't exist
        try:
            cursor.execute("ALTER TABLE ted_contracts_production ADD COLUMN influence_category TEXT")
            print("  Added column: influence_category")
        except Exception as e:
            if "duplicate column name" not in str(e).lower():
                print(f"  Column influence_category already exists")

        try:
            cursor.execute("ALTER TABLE ted_contracts_production ADD COLUMN influence_priority TEXT")
            print("  Added column: influence_priority")
        except Exception as e:
            if "duplicate column name" not in str(e).lower():
                print(f"  Column influence_priority already exists")

        try:
            cursor.execute("ALTER TABLE ted_contracts_production ADD COLUMN influence_patterns TEXT")
            print("  Added column: influence_patterns")
        except Exception as e:
            if "duplicate column name" not in str(e).lower():
                print(f"  Column influence_patterns already exists")

        try:
            cursor.execute("ALTER TABLE ted_contracts_production ADD COLUMN is_intpa_contract INTEGER DEFAULT 0")
            print("  Added column: is_intpa_contract")
        except Exception as e:
            if "duplicate column name" not in str(e).lower():
                print(f"  Column is_intpa_contract already exists")

        conn.commit()
        conn.close()

    def update_database(self, updates):
        """Apply updates to database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update records
        for update in updates:
            cursor.execute("""
                UPDATE ted_contracts_production
                SET is_chinese_related = ?,
                    chinese_confidence = ?,
                    detection_rationale = ?,
                    influence_category = ?,
                    influence_priority = ?,
                    influence_patterns = ?,
                    is_intpa_contract = ?
                WHERE id = ?
            """, (
                update['is_chinese_related'],
                update['chinese_confidence'],
                update['detection_rationale'],
                update['influence_category'],
                update['influence_priority'],
                update['influence_patterns'],
                update['is_intpa_contract'],
                update['id']
            ))

        conn.commit()
        conn.close()

    def reprocess_full_database(self):
        """Reprocess entire TED database"""

        print("\n" + "="*80)
        print("FULL TED DATABASE REPROCESSING")
        print("="*80)
        print()
        print("Database:", self.db_path)
        print()

        # Get total count
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        total = cursor.execute("SELECT COUNT(*) FROM ted_contracts_production").fetchone()[0]
        print(f"Total contracts: {total:,}")
        print()

        # Add schema columns first
        print("Adding/verifying database schema columns...")
        self.add_schema_columns()
        print()

        # Process in batches
        batch_size = 10000
        offset = 0

        start_time = datetime.now()

        while offset < total:
            # Fetch batch
            cursor.execute("""
                SELECT id, contract_title, contract_description, ca_name,
                       contractor_name, contractor_address, contractor_country
                FROM ted_contracts_production
                LIMIT ? OFFSET ?
            """, (batch_size, offset))

            rows = cursor.fetchall()
            if not rows:
                break

            # Convert to dicts
            contracts = []
            for row in rows:
                contracts.append({
                    'id': row[0],
                    'contract_title': row[1],
                    'contract_description': row[2],
                    'ca_name': row[3],
                    'contractor_name': row[4],
                    'contractor_address': row[5],
                    'contractor_country': row[6]
                })

            # Process batch
            updates = self.process_batch(contracts)

            # Update database
            self.update_database(updates)

            # Progress
            offset += batch_size
            pct = (offset / total) * 100
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = offset / elapsed if elapsed > 0 else 0
            eta = (total - offset) / rate if rate > 0 else 0

            print(f"Progress: {offset:,}/{total:,} ({pct:.1f}%) | "
                  f"Rate: {rate:.0f} contracts/sec | "
                  f"ETA: {eta/60:.1f} min | "
                  f"Chinese: {self.stats['chinese_contractors']:,} | "
                  f"Influence: {self.stats['influence_contracts']:,}")

        conn.close()

        # Final stats
        elapsed_total = (datetime.now() - start_time).total_seconds()

        print()
        print("="*80)
        print("REPROCESSING COMPLETE")
        print("="*80)
        print()
        print(f"Total Processed: {self.stats['total_processed']:,}")
        print(f"Time Elapsed: {elapsed_total/60:.1f} minutes")
        print(f"Processing Rate: {self.stats['total_processed']/elapsed_total:.0f} contracts/sec")
        print()
        print(f"Chinese Contractors: {self.stats['chinese_contractors']:,} "
              f"({self.stats['chinese_contractors']/self.stats['total_processed']*100:.2f}%)")
        print(f"Influence Contracts: {self.stats['influence_contracts']:,} "
              f"({self.stats['influence_contracts']/self.stats['total_processed']*100:.2f}%)")
        print(f"INTPA Contracts: {self.stats['intpa_contracts']:,}")
        print()

        print("Detection Methods:")
        for method, count in sorted(self.stats['by_detection_method'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {method:40} {count:6,}")

        print()
        print("Influence Categories:")
        for category, count in sorted(self.stats['by_influence_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {category:40} {count:6,}")

        # Save stats
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stats_file = Path(f"analysis/ted_full_reprocessing_stats_{timestamp}.json")

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total_processed': self.stats['total_processed'],
                'chinese_contractors': self.stats['chinese_contractors'],
                'influence_contracts': self.stats['influence_contracts'],
                'intpa_contracts': self.stats['intpa_contracts'],
                'detection_methods': dict(self.stats['by_detection_method']),
                'influence_categories': dict(self.stats['by_influence_category']),
                'elapsed_seconds': elapsed_total
            }, f, indent=2)

        print()
        print(f"Stats saved to: {stats_file}")
        print()


if __name__ == '__main__':
    reprocessor = FullTEDReprocessor()
    reprocessor.reprocess_full_database()
