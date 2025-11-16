#!/usr/bin/env python3
"""
USAspending 101-Column Format Processor

Specialized processor for 101-column USAspending assistance data format.
This format represents 26.7 GB of grant/loan data (files 5847, 5836).

Schema: Assistance/Grant data (not contracts)
Key fields:
  [9]  recipient_name
  [55] recipient_country_code
  [56] recipient_country_name
  [73] pop_country_code (place of performance)
  [74] pop_country_name

Input: F:/OSINT_DATA/USAspending/extracted_data/5847.dat.gz, 5836.dat.gz
Output: F:/OSINT_WAREHOUSE/osint_master.db (table: usaspending_china_101)
"""

import gzip
import sqlite3
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

@dataclass
class DetectionResult:
    """Result of China entity detection."""
    is_detected: bool
    detection_type: str
    field_index: int
    field_name: str
    matched_value: str
    confidence: str
    rationale: str

@dataclass
class Transaction101:
    """USAspending transaction record (101-column assistance format)."""
    transaction_id: str
    award_id: str
    recipient_name: str
    recipient_country_code: str
    recipient_country_name: str
    pop_country_code: str
    pop_country_name: str
    award_amount: float
    award_description: str
    awarding_agency: str
    sub_agency: str
    program_number: str
    program_title: str
    recipient_type: str
    action_date: str

class USAspending101Processor:
    """
    Processor for 101-column USAspending assistance format.

    Focuses on grants/loans rather than contracts.
    """

    # 101-column schema mapping (confirmed through analysis)
    SCHEMA = {
        0: 'transaction_id',
        1: 'award_id',
        7: 'award_description',
        9: 'recipient_name',
        12: 'awarding_agency_name',
        16: 'sub_agency_name',
        21: 'recipient_type',
        22: 'program_number',
        23: 'program_title',
        27: 'federal_action_obligation',  # Often $0 or null
        29: 'award_amount',  # Actual award amount (CORRECTED)
        55: 'recipient_country_code',
        56: 'recipient_country_name',
        73: 'pop_country_code',
        74: 'pop_country_name',
        94: 'action_date',
    }

    # China detection patterns (PRC only - NOT Taiwan)
    CHINA_COUNTRIES = [
        'china', 'hong kong', 'prc', "people's republic of china",
        'peoples republic of china', 'mainland china', 'chn'
    ]

    CHINA_ENTITIES = [
        # Telecommunications
        'huawei', 'zte', 'china telecom', 'china mobile', 'china unicom',
        # Surveillance
        'hikvision', 'dahua', 'zhejiang dahua',
        # Technology
        'lenovo', 'xiaomi', 'oppo electronics', 'vivo mobile', 'oneplus technology', 'realme',
        'alibaba', 'tencent', 'baidu', 'bytedance', 'tiktok',
        # Drones
        'dji', 'autel robotics',
        # Aviation
        'comac', 'avic',
        # Electronics
        'boe technology', 'tcl corporation', 'hisense', 'haier',
        # Semiconductors
        'smic', 'semiconductor manufacturing international',
        # Shipping
        'cosco', 'china ocean shipping',
        # Energy
        'cnooc', 'sinopec', 'petrochina',
        # Nuclear
        'cgnpc', 'china general nuclear',
        # Rail
        'china railway rolling stock', 'crrc corporation',
        # Automotive
        'nio inc', 'byd company', 'geely',
    ]

    # Known false positives to exclude
    FALSE_POSITIVES = [
        'boeing', 'comboed', 'senior', 'union', 'junior',
        'opportunities', 'opportunity', 'opposite', 'opposition',
        'corrections', 'crrctns',
        # Geographic false positives
        'san antonio',
        'indochina',  # Historical region, not PRC
        'indo-china',
        'french indochina',
        # Porcelain/ceramics companies
        'homer laughlin china company',
        'homer laughlin',
        'china porcelain',
        'fine china',
        'bone china',
        # Italian surnames
        'facchinaggi',
        'facchin',
        'vecchini',
        'zecchin',
        # US companies with Chinese-sounding names
        'cosco fire protection',  # US fire protection company (owned by German Minimax), not COSCO Shipping
        'cosco fire',
        'american cosco',  # American COSCO (not China COSCO Shipping)
        # European companies/joint ventures with Chinese-related names
        'sino european',  # European joint ventures
        'sino-german',
        'euro-china',
        'sino-french',
        'sino-italian',
        # Language service companies (translation/interpreting, not China-based)
        'chinese language services',  # e.g., ACTA CHINESE LANGUAGE SERVICES LLC
        'chinese language service',
        'chinese translation services',
        'chinese translation service',
        'chinese interpreting services',
        'chinese interpreting service',
        'chinese interpreter services',
        'chinese interpretation services',
        # Round 4: Entity name substring false positives
        'comac pump',  # Comac Pump & Well LLC (not COMAC aircraft)
        'comac well',
        'aztec environmental',  # Aztec Environmental (not ZTE)
        'aztec',  # Broader Aztec match
        'ezteq',  # EZ Tech company
        't k c enterprises',  # T K C Enterprises (41 false positives)
        'tkc enterprises',
        'mavich',  # Mavich LLC (contains 'avic')
        'vista gorgonio',  # Vista Gorgonio Inc
        'pri/djv',  # PRI/DJI Construction JV (not DJI drones)
        "avic's travel",  # Avic's Travel LLC (not AVIC)
    ]


    # ========== IMPORTANCE TIER PATTERNS ==========

    # TIER 1: Strategic Entities
    TIER_1_STRATEGIC_ENTITIES = [
        'CHINESE ACADEMY', 'HUAWEI', 'ZTE', 'LENOVO',
        'TENCENT', 'ALIBABA', 'BAIDU', 'DJI', 'HIKVISION',
        'DAHUA', 'HYTERA', 'AVIC', 'COMAC', 'CSSC', 'NORINCO',
        'CHINESE UNIVERSITY', 'TSINGHUA', 'PEKING UNIVERSITY',
        'CAS ', 'RESEARCH CENTER', 'RESEARCH INSTITUTE',
        'BEIJING BOOK',
    ]

    # TIER 1: Strategic Technologies
    TIER_1_STRATEGIC_TECH = [
        'QUANTUM', 'ARTIFICIAL INTELLIGENCE', 'MACHINE LEARNING',
        'SEMICONDUCTOR', 'CHIP MANUFACTURING', 'PROCESSOR DESIGN',
        'BIOTECHNOLOGY', 'PHARMACEUTICAL RESEARCH', 'GENE',
        'SATELLITE', 'SPACE STATION', 'ROCKET', 'MISSILE',
        'HYPERSONIC', 'NUCLEAR', 'FUSION',
        'ADVANCED MATERIALS', 'NANOMATERIAL', 'GRAPHENE',
        '5G NETWORK'
    ]

    # TIER 3: Office Supplies
    TIER_3_OFFICE_SUPPLIES = [
        'CARTRIDGE', 'TONER', 'INK', 'PAPER', 'STAPLE', 'FOLDER',
        'PEN', 'PENCIL', 'MARKER', 'ENVELOPE', 'CLIP', 'BINDER',
        'LABEL MAKER', 'P-TOUCH', 'BROTHER P-TOUCH',
        'PT-D600VP', 'MFR: BROTHER',
        'NOTEPAD', 'POST-IT'
    ]

    # TIER 3: Commodity Electronics
    TIER_3_COMMODITY_ELECTRONICS = [
        'SURGE PROTECTOR', 'SURGE SUPPRESSOR', 'SURGE,PROTECTOR',
        'POWER STRIP', 'EXTENSION CORD', 'CABLE', 'ADAPTER', 'USB',
        'CHARGER', 'BATTERY', 'FLASHLIGHT', 'LIGHT BULB', 'LED', 'LAMP',
        'ABSORBER', 'OVERVOLTAGE',
    ]

    # TIER 3: Hardware
    TIER_3_HARDWARE = [
        'SCREW', 'BOLT', 'NUT', 'WASHER', 'WEDGE', 'HOOK', 'HINGE',
        'LOCK', 'KEY', 'NAIL', 'HAMMER', 'WRENCH', 'PLIERS',
        'SCREWDRIVER', 'DRILL BIT',
        'RELAY', 'ELBOW', 'PIPE', 'TUBE', 'FITTING', 'GASKET',
        'RESISTOR', 'CAPACITOR',
    ]

    # TIER 3: Apparel
    TIER_3_APPAREL = [
        'APRON', 'GLOVE', 'SHOE', 'BOOT', 'HAT', 'UNIFORM',
        'VEST', 'JACKET', 'PANTS', 'SHIRT', 'SOCKS',
        'COLLAR,EXTRICATION',
    ]

    # TIER 3: Kitchen/Janitorial
    TIER_3_KITCHEN = [
        'FUNNEL', 'WHISK', 'SPATULA', 'LADLE', 'SPOON', 'FORK',
        'KNIFE', 'PLATE', 'CUP', 'MOP', 'BROOM', 'BUCKET',
        'CLEANER', 'DETERGENT', 'SOAP',
        'WHIP', 'SCOOP', 'MEASURING', 'SHAKER', 'SALT',
        'PEELER', 'POTATO PEELER', 'IRON',
    ]

    # TIER 3: Medical Supplies (basic)
    TIER_3_MEDICAL_BASIC = [
        'APPLICATOR', 'BANDAGE', 'GAUZE', 'SWAB', 'SYRINGE',
        'GLOVES MEDICAL', 'MASK', 'FACE SHIELD', 'DISPOSAB',
        'KIT,INTRAVE',
    ]

    # TIER 3: Auto Parts (commodity)
    TIER_3_AUTO_PARTS = [
        'BEARING', 'FILTER', 'BELT', 'HOSE', 'CLAMP', 'BRACKET',
        'STARTER KIT', 'WHEEL', 'TIRE',
        'INDICATOR,SPECIAL',
    ]

    # TIER 3: Miscellaneous Commodity
    TIER_3_MISC_COMMODITY = [
        'CART', 'TRAVEL CART',
        'ABRASIVE WHEEL',
        'STRAP', 'TIE DOWN'
    ]

    # TIER 2: Computers
    TIER_2_COMPUTERS = [
        'COMPUTER', 'DESKTOP', 'LAPTOP', 'SERVER', 'WORKSTATION',
        'IMAC', 'DELL', 'OPTIPLEX', 'HP ELITEBOOK', 'THINKPAD',
        'DISK DRIVE', 'HARD DRIVE', 'SSD', 'STORAGE',
        'MONITOR', 'DISPLAY', 'SCREEN'
    ]

    # TIER 2: Equipment
    TIER_2_EQUIPMENT = [
        'EQUIPMENT', 'MACHINERY', 'ENGINE', 'MOTOR', 'PUMP',
        'VALVE', 'COMPRESSOR', 'GENERATOR', 'TURBINE',
        'CIRCUIT BREAKER', 'CONTROL SYSTEM', 'SENSOR',
        'HEATER', 'TAPE', 'REFLECTIVE',
        'MICROTOME', 'HISTOLOGY',
    ]

    # TIER 2: Vehicles
    TIER_2_VEHICLES = [
        'VEHICLE', 'TRUCK', 'CAR', 'VAN', 'BUS',
        'AIRCRAFT', 'HELICOPTER', 'SHIP', 'VESSEL', 'BOAT'
    ]

    # TIER 2: Services
    TIER_2_SERVICES = [
        'CONSULTING', 'ENGINEERING', 'TECHNICAL SUPPORT',
        'SOFTWARE DEVELOPMENT', 'SYSTEM INTEGRATION',
        'CLEANING CONTRACT', 'OFFICE CLEANING', 'FACILITY',
        'CUSTOMS CLEARANCE', 'FREIGHT', 'TRANSPORTATION',
        'INTERPRETATION', 'TRANSLATION', 'TALENT SERVICES',
        'HOTEL', 'LODGING'
    ]

    # ========== END TIER PATTERNS ==========

    def __init__(self):
        self.output_dir = Path("data/processed/usaspending_101_production")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

        # Statistics
        self.stats = {
            'files_processed': 0,
            'total_records': 0,
            'china_detected': 0,
            'by_detection_type': defaultdict(int),
            'by_confidence': defaultdict(int),
            'total_value': 0.0,
        }

    def process_file(self, file_path: Path, batch_size: int = 5000,
                     max_records: Optional[int] = None) -> int:
        """
        Process a single 101-column .dat.gz file with streaming database saves.

        Args:
            file_path: Path to .dat.gz file
            batch_size: Number of detections to accumulate before saving
            max_records: Maximum records to process (for testing)

        Returns:
            Total number of detections found
        """

        print(f"\n{'='*80}")
        print(f"Processing 101-column format: {file_path.name}")
        print(f"Size: {file_path.stat().st_size / (1024**3):.1f} GB")
        print(f"{'='*80}\n")

        detections_batch = []
        total_detections = 0
        record_count = 0

        with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                # Progress indicator
                if line_num % 100000 == 0:
                    print(f"  Processed {line_num:,} lines, "
                          f"detected {total_detections:,} China-related (batch: {len(detections_batch)})")

                # Parse record
                fields = line.strip().split('\t')

                # Validate 101-column format
                if len(fields) < 90:  # Allow some flexibility
                    continue

                # Extract transaction
                try:
                    transaction = self._extract_transaction(fields)
                except Exception as e:
                    continue  # Skip malformed records

                # Detect China entities
                detection_results = self._detect_china_entity(transaction, fields)

                if detection_results:
                    # Build detection record
                    detection_record = self._build_detection_record(
                        transaction, detection_results, fields
                    )
                    detections_batch.append(detection_record)

                    # Update statistics
                    self.stats['china_detected'] += 1
                    self.stats['total_value'] += transaction.award_amount

                    for result in detection_results:
                        self.stats['by_detection_type'][result.detection_type] += 1
                        self.stats['by_confidence'][result.confidence] += 1

                    # Save batch to database when it reaches batch_size
                    if len(detections_batch) >= batch_size:
                        self._save_to_database(detections_batch)
                        total_detections += len(detections_batch)
                        detections_batch = []  # Clear batch

                record_count += 1
                self.stats['total_records'] += 1

                # Stop if reached max
                if max_records and record_count >= max_records:
                    print(f"\n  Reached max records limit: {max_records:,}")
                    break

        # Save any remaining detections
        if detections_batch:
            self._save_to_database(detections_batch)
            total_detections += len(detections_batch)

        print(f"\n  Completed: {record_count:,} records processed")
        print(f"  Detected: {total_detections:,} China-related transactions")

        return total_detections

    def _extract_transaction(self, fields: List[str]) -> Transaction101:
        """Extract transaction from 101-column fields."""

        def get_field(idx: int) -> str:
            """Get field value, handling NULL."""
            if idx < len(fields):
                val = fields[idx]
                return '' if val in ['\\N', '', 'NULL'] else val
            return ''

        def get_float(idx: int) -> float:
            """Get float field, handling NULL."""
            val = get_field(idx)
            try:
                return float(val) if val else 0.0
            except:
                return 0.0

        return Transaction101(
            transaction_id=get_field(0),
            award_id=get_field(1),
            recipient_name=get_field(9),
            recipient_country_code=get_field(55),
            recipient_country_name=get_field(56),
            pop_country_code=get_field(73),
            pop_country_name=get_field(74),
            award_amount=get_float(29),  # CORRECTED: Field 29, not 27
            award_description=get_field(7),
            awarding_agency=get_field(12),
            sub_agency=get_field(16),
            program_number=get_field(22),
            program_title=get_field(23),
            recipient_type=get_field(21),
            action_date=get_field(94),
        )

    def _detect_china_entity(self, transaction: Transaction101,
                             fields: List[str]) -> List[DetectionResult]:
        """
        Multi-field China entity detection for 101-column format.
        """

        results = []

        # 1. COUNTRY CHECK (highest confidence)
        # OPTION B: Check for product sourcing to distinguish from entity relationships

        # Check recipient country name
        if self._is_china_country(transaction.recipient_country_name):
            if self._is_product_sourcing_mention(transaction.award_description):
                # Product sourcing - separate category
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='china_sourced_product',
                    field_index=56,
                    field_name='recipient_country_name',
                    matched_value=transaction.recipient_country_name,
                    confidence='LOW',
                    rationale='Product origin language detected (possible data quality error)'
                ))
            else:
                # Legitimate Chinese entity
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='country',
                    field_index=56,
                    field_name='recipient_country_name',
                    matched_value=transaction.recipient_country_name,
                    confidence='HIGH',
                    rationale=f'Recipient in {transaction.recipient_country_name}'
                ))

        # Check recipient country code
        if self._is_china_country(transaction.recipient_country_code):
            if self._is_product_sourcing_mention(transaction.award_description):
                # Product sourcing - separate category
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='china_sourced_product',
                    field_index=55,
                    field_name='recipient_country_code',
                    matched_value=transaction.recipient_country_code,
                    confidence='LOW',
                    rationale='Product origin language detected (possible data quality error)'
                ))
            else:
                # Legitimate Chinese entity
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='country',
                    field_index=55,
                    field_name='recipient_country_code',
                    matched_value=transaction.recipient_country_code,
                    confidence='HIGH',
                    rationale=f'Recipient country code: {transaction.recipient_country_code}'
                ))

        # Check place of performance country name
        if self._is_china_country(transaction.pop_country_name):
            if self._is_product_sourcing_mention(transaction.award_description):
                # Product sourcing - likely data entry error
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='china_sourced_product',
                    field_index=74,
                    field_name='pop_country_name',
                    matched_value=transaction.pop_country_name,
                    confidence='LOW',
                    rationale='Product origin language detected (possible data quality error)'
                ))
            else:
                # Legitimate China place of performance
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='country',
                    field_index=74,
                    field_name='pop_country_name',
                    matched_value=transaction.pop_country_name,
                    confidence='HIGH',
                    rationale=f'Work performed in {transaction.pop_country_name}'
                ))

        # Check place of performance country code
        if self._is_china_country(transaction.pop_country_code):
            if self._is_product_sourcing_mention(transaction.award_description):
                # Product sourcing - likely data entry error (like T K C ENTERPRISES)
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='china_sourced_product',
                    field_index=73,
                    field_name='pop_country_code',
                    matched_value=transaction.pop_country_code,
                    confidence='LOW',
                    rationale='Product origin language detected (possible data quality error)'
                ))
            else:
                # Legitimate China place of performance
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='country',
                    field_index=73,
                    field_name='pop_country_code',
                    matched_value=transaction.pop_country_code,
                    confidence='HIGH',
                    rationale=f'POP country code: {transaction.pop_country_code}'
                ))

        # 2. ENTITY NAME CHECK
        entity_match = self._find_china_entity(transaction.recipient_name)
        if entity_match:
            results.append(DetectionResult(
                is_detected=True,
                detection_type='entity_name',
                field_index=9,
                field_name='recipient_name',
                matched_value=entity_match,
                confidence='HIGH',
                rationale=f'Known Chinese entity: {entity_match} in recipient name'
            ))

        return results

    def _is_china_country(self, country: str) -> bool:
        """Check if country field indicates China (PRC only, NOT Taiwan/ROC)."""
        if not country:
            return False
        country_lower = country.lower()

        # CRITICAL: Taiwan (ROC) is NOT China (PRC)
        if 'taiwan' in country_lower or country_lower == 'twn':
            return False

        return any(china_country in country_lower
                   for china_country in self.CHINA_COUNTRIES)

    def _find_china_entity(self, text: str) -> Optional[str]:
        """Find known Chinese entity in text with proper word boundaries."""
        if not text:
            return None
        text_lower = text.lower()

        # Check for false positives first
        for false_positive in self.FALSE_POSITIVES:
            if false_positive in text_lower:
                return None

        # Check for Chinese entities - APPLY WORD BOUNDARIES TO ALL
        for entity in self.CHINA_ENTITIES:
            if entity in text_lower:
                # Apply word boundary check to ALL entities (not just short ones)
                pattern = r'\b' + re.escape(entity) + r'\b'
                if re.search(pattern, text_lower):
                    return entity
        return None

    def _is_product_sourcing_mention(self, description: str) -> bool:
        """
        Check if description mentions China as product origin (not entity relationship).

        Returns True if description indicates China-manufactured product.
        This implements Option B: Separate category for supply chain visibility.
        """
        if not description:
            return False

        desc_lower = description.lower()

        # Product origin phrases (indicates manufacturing location, not entity)
        product_origin_phrases = [
            'made in china',
            'manufactured in china',
            'produced in china',
            'fabricated in china',
            'assembled in china',
            'origin china',
            'origin: china',
            'country of origin china',
            'country of origin: china',
            'made in prc',
            'manufactured in prc',
            'china acceptable',  # "made in China acceptable" (T K C ENTERPRISES pattern)
            'produced in prc',
        ]

        return any(phrase in desc_lower for phrase in product_origin_phrases)


    def _categorize_importance(self, recipient_name: str, vendor_name: str, description: str):
        """
        Categorize record by strategic intelligence value.

        Returns:
            tuple: (tier, importance_score, commodity_type)
        """
        desc = (description or '').upper()
        recipient = (recipient_name or '').upper()
        vendor = (vendor_name or '').upper()

        # Normalize description (handle comma variants)
        desc_normalized = desc.replace(',', ' ')

        # Special handling: Part number patterns (Brother label makers)
        if ('P/N:' in desc or 'MFR:' in desc) and 'BROTHER' in desc:
            return ('TIER_3', 0.1, 'office_supplies')

        # TIER 1: Strategic Entities (name match with word boundaries)
        for entity in self.TIER_1_STRATEGIC_ENTITIES:
            # Use word boundaries to avoid substring matches (ZTE != ZTERS, AZTEC, EZTEQ)
            pattern = r'\b' + re.escape(entity) + r'\b'
            if re.search(pattern, recipient, re.IGNORECASE) or re.search(pattern, vendor, re.IGNORECASE):
                return ('TIER_1', 1.0, 'strategic_entity')

        # TIER 1: Strategic Technologies (description match)
        for tech in self.TIER_1_STRATEGIC_TECH:
            if tech in desc_normalized:
                return ('TIER_1', 1.0, 'strategic_technology')

        # TIER 3: Commodity categories (description match)
        commodity_patterns = [
            (self.TIER_3_OFFICE_SUPPLIES, 'office_supplies'),
            (self.TIER_3_COMMODITY_ELECTRONICS, 'commodity_electronics'),
            (self.TIER_3_HARDWARE, 'hardware'),
            (self.TIER_3_APPAREL, 'apparel'),
            (self.TIER_3_KITCHEN, 'kitchen_janitorial'),
            (self.TIER_3_MEDICAL_BASIC, 'medical_supplies_basic'),
            (self.TIER_3_AUTO_PARTS, 'auto_parts_commodity'),
            (self.TIER_3_MISC_COMMODITY, 'misc_commodity'),
        ]

        for keywords, commodity_type in commodity_patterns:
            for keyword in keywords:
                if keyword in desc_normalized:
                    return ('TIER_3', 0.1, commodity_type)

        # TIER 2: Technology/Service categories
        tier2_patterns = [
            (self.TIER_2_COMPUTERS, 'computers_electronics'),
            (self.TIER_2_EQUIPMENT, 'specialized_equipment'),
            (self.TIER_2_VEHICLES, 'vehicles_transport'),
            (self.TIER_2_SERVICES, 'professional_services'),
        ]

        for keywords, category in tier2_patterns:
            for keyword in keywords:
                if keyword in desc_normalized:
                    return ('TIER_2', 0.5, category)

        # Special handling: Empty descriptions
        if len(desc.strip()) < 10 or 'DESCR N.A.' in desc:
            return ('TIER_2', 0.5, 'insufficient_description')

        # Default: TIER_2 (general technology/equipment)
        return ('TIER_2', 0.5, 'general_technology')


    def _build_detection_record(self, transaction: Transaction101,
                                 results: List[DetectionResult],
                                 fields: List[str]) -> Dict:
        """Build comprehensive detection record."""

        # Categorize importance tier
        importance_tier, importance_score, commodity_type = self._categorize_importance(
            recipient_name=recipient_name,
            vendor_name=vendor_name,
            description=award_description
        )

        return {
            # Transaction identifiers
            'transaction_id': transaction.transaction_id,
            'award_id': transaction.award_id,

            # Entity information
            'recipient_name': transaction.recipient_name,
            'recipient_country_code': transaction.recipient_country_code,
            'recipient_country_name': transaction.recipient_country_name,
            'pop_country_code': transaction.pop_country_code,
            'pop_country_name': transaction.pop_country_name,

            # Financial
            'award_amount': transaction.award_amount,

            # Program information
            'award_description': transaction.award_description[:500],
            'awarding_agency': transaction.awarding_agency,
            'sub_agency': transaction.sub_agency,
            'program_number': transaction.program_number,
            'program_title': transaction.program_title,
            'recipient_type': transaction.recipient_type,

            # Dates
            'action_date': transaction.action_date,

            # Detection metadata
            'detection_count': len(results),
            'detection_types': [r.detection_type for r in results],
            'highest_confidence': self._get_highest_confidence(results),
            'detection_details': [
                {
                    'type': r.detection_type,
                    'field_index': r.field_index,
                    'field_name': r.field_name,
                    'matched_value': r.matched_value,
                    'confidence': r.confidence,
                    'rationale': r.rationale,
                }
                for r in results
            ],

            # Processing metadata
            'processed_date': datetime.now().isoformat(),
            'format': '101-column',
        }

    def _get_highest_confidence(self, results: List[DetectionResult]) -> str:
        """Get highest confidence level from results."""
        if not results:
            return 'NONE'

        confidences = [r.confidence for r in results]
        if 'HIGH' in confidences:
            return 'HIGH'
        elif 'MEDIUM' in confidences:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _save_to_database(self, detections: List[Dict]):
        """Save detections to master database."""

        if not self.db_path.exists():
            print(f"Warning: Database not found: {self.db_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Create table if not exists
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usaspending_china_101 (
                transaction_id TEXT PRIMARY KEY,
                award_id TEXT,
                recipient_name TEXT,
                recipient_country_code TEXT,
                recipient_country_name TEXT,
                pop_country_code TEXT,
                pop_country_name TEXT,
                award_amount REAL,
                award_description TEXT,
                awarding_agency TEXT,
                sub_agency TEXT,
                program_number TEXT,
                program_title TEXT,
                recipient_type TEXT,
                action_date TEXT,
                detection_count INTEGER,
                detection_types TEXT,
                highest_confidence TEXT,
                detection_details TEXT,
                processed_date TEXT,
                format TEXT
            )
        ''')

        # Create indexes
        cur.execute('CREATE INDEX IF NOT EXISTS idx_101_recipient ON usaspending_china_101(recipient_name)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_101_country ON usaspending_china_101(recipient_country_name)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_101_confidence ON usaspending_china_101(highest_confidence)')

        # Insert records
        for detection in detections:
            cur.execute('''
                INSERT OR REPLACE INTO usaspending_china_101 VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                detection['transaction_id'],
                detection['award_id'],
                detection['recipient_name'],
                detection['recipient_country_code'],
                detection['recipient_country_name'],
                detection['pop_country_code'],
                detection['pop_country_name'],
                detection['award_amount'],
                detection['award_description'],
                detection['awarding_agency'],
                detection['sub_agency'],
                detection['program_number'],
                detection['program_title'],
                detection['recipient_type'],
                detection['action_date'],
                detection['detection_count'],
                json.dumps(detection['detection_types']),
                detection['highest_confidence'],
                json.dumps(detection['detection_details']),
                detection['processed_date'],
                detection['format'],
            ))

        conn.commit()
        conn.close()

        print(f"Saved {len(detections):,} records to database table: usaspending_china_101")

    def print_summary(self):
        """Print processing summary."""

        print(f"\n{'='*80}")
        print("101-COLUMN PROCESSING SUMMARY")
        print(f"{'='*80}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Total records: {self.stats['total_records']:,}")
        print(f"China detections: {self.stats['china_detected']:,} "
              f"({self.stats['china_detected']/max(self.stats['total_records'], 1)*100:.2f}%)")
        print(f"Total value: ${self.stats['total_value']:,.2f}")

        print(f"\nDetection Types:")
        for det_type, count in sorted(self.stats['by_detection_type'].items()):
            print(f"  {det_type}: {count:,}")

        print(f"\nConfidence Levels:")
        for confidence, count in sorted(self.stats['by_confidence'].items()):
            print(f"  {confidence}: {count:,}")

        print(f"{'='*80}\n")


def main():
    """Test on sample from 101-column file."""

    print("USAspending 101-Column Format Processor")
    print("="*80)

    processor = USAspending101Processor()

    # Test on 101-column file with limited records
    test_file = Path("F:/OSINT_DATA/USAspending/extracted_data/5847.dat.gz")

    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return

    print(f"\nTEST MODE: Processing first 100,000 records")
    print(f"File: {test_file.name}")
    print(f"Expected format: 101 columns\n")

    # Process (streaming mode - saves to database automatically)
    total_detections = processor.process_file(test_file, max_records=100000)

    # Summary
    processor.stats['files_processed'] = 1
    processor.print_summary()

    # Note about detections
    if total_detections > 0:
        print(f"\nTest complete: {total_detections} detections saved to database")
        print("Verify results before proceeding to full production run")
    else:
        print("\nNo detections found in test sample.")


if __name__ == '__main__':
    main()
