#!/usr/bin/env python3
"""
USAspending Comprehensive Processor

Multi-field China entity detection for federal spending data.
Based on complete 206-column schema analysis.

Strategy:
1. Check ALL country fields (recipient, POP, sub-awardee)
2. Check ALL entity name fields (prime + sub, including parents)
3. Analyze descriptions with technology keywords
4. Cross-reference with known entities database
5. Handle NULL values properly (not fabricate data)

Input: F:/OSINT_DATA/USAspending/extracted_data/*.dat.gz
Output: data/processed/usaspending_production/
"""

import gzip
import sqlite3
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

@dataclass
class DetectionResult:
    """Result of China entity detection."""
    is_detected: bool
    detection_type: str  # 'country', 'entity_name', 'parent', 'sub_awardee', 'description'
    field_index: int
    field_name: str
    matched_value: str
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW'
    rationale: str

@dataclass
class Transaction:
    """USAspending transaction record."""
    transaction_id: str
    piid: str
    fain: str
    recipient_name: str
    recipient_parent_name: str
    recipient_country: str
    pop_country: str
    sub_awardee_name: str
    sub_awardee_parent_name: str
    sub_awardee_country: str
    award_description: str
    subaward_description: str
    federal_action_obligation: float
    total_dollars_obligated: float
    awarding_agency: str
    funding_agency: str
    naics_code: str
    naics_description: str
    psc_code: str
    psc_description: str
    action_date: str
    fiscal_year: str
    recipient_uei: str
    recipient_duns: str

class USAspendingComprehensiveProcessor:
    """
    Comprehensive processor for USAspending data.

    Uses multi-field detection strategy based on complete schema analysis.
    """

    # Column mapping (from schema analysis)
    SCHEMA = {
        2: 'transaction_id',
        4: 'piid',
        120: 'fain',
        23: 'recipient_name',
        27: 'recipient_parent_name',
        29: 'recipient_location_country_name',
        39: 'pop_country_name',
        59: 'sub_awardee_name',
        63: 'sub_awardee_parent_name',
        65: 'sub_awardee_country_name',
        46: 'award_description',
        82: 'subaward_description',
        6: 'federal_action_obligation',
        140: 'total_dollars_obligated',
        16: 'awarding_toptier_agency_name',
        10: 'funding_toptier_agency_name',
        47: 'naics_code',
        48: 'naics_description',
        163: 'product_or_service_code',
        164: 'product_or_service_code_description',
        7: 'action_date',
        8: 'fiscal_year',
        22: 'recipient_uei',
        21: 'recipient_duns',
    }

    # China detection patterns
    CHINA_COUNTRIES = [
        'china', 'hong kong', 'prc', "people's republic of china",
        'peoples republic of china', 'mainland china'
    ]

    CHINA_ENTITIES = [
        # Telecommunications
        'huawei', 'zte', 'china telecom', 'china mobile', 'china unicom',
        # Surveillance
        'hikvision', 'dahua', 'zhejiang dahua',
        # Technology (use full company names for short brands to avoid false positives)
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
        # Rail (use full name to avoid matching "corrections")
        'china railway rolling stock', 'crrc corporation',
        # Automotive
        'nio inc', 'byd company', 'geely',
    ]

    # Known false positives to exclude
    FALSE_POSITIVES = [
        'boeing',  # Don't match 'boe' in 'boeing'
        'comboed',  # Don't match 'boe' in 'comboed'
        'senior',  # Don't match 'nio' in 'senior'
        'union',  # Don't match 'nio' in 'union'
        'junior',  # Don't match 'nio' in 'junior'
        'opportunities',  # Don't match 'oppo' in 'opportunities'
        'opportunity',  # Don't match 'oppo' in 'opportunity'
        'opposite',  # Don't match 'oppo' in 'opposite'
        'opposition',  # Don't match 'oppo' in 'opposition'
        'corrections',  # Don't match 'crrc' in 'corrections'
        'crrctns',  # Don't match 'crrc' in abbreviated 'crrctns'
        # Geographic false positives
        'san antonio',
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
        'cosco fire protection',  # Not COSCO shipping
        'cosco fire',
        'american cosco',  # American COSCO (not China COSCO Shipping)
        # European companies/joint ventures with Chinese-related names
        'sino european',  # European joint ventures
        'sino-german',
        'euro-china',
        'sino-french',
        'sino-italian',
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

    SENSITIVE_NAICS = {
        '334': 'Computer and Electronic Product Manufacturing',
        '336': 'Transportation Equipment Manufacturing',
        '541': 'Professional, Scientific, and Technical Services',
        '517': 'Telecommunications',
        '518': 'Data Processing, Hosting',
    }

    SENSITIVE_AGENCIES = [
        'Department of Defense', 'DOD', 'DEPT OF DEFENSE',
        'Department of Energy', 'DOE',
        'NASA', 'National Aeronautics and Space Administration',
        'NSF', 'National Science Foundation',
        'DARPA', 'Defense Advanced Research Projects',
        'NIST', 'National Institute of Standards',
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
        self.output_dir = Path("data/processed/usaspending_production")
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

    def process_file(self, file_path: Path, batch_size: int = 100000,
                     max_records: Optional[int] = None) -> List[Dict]:
        """
        Process a single .dat.gz file.

        Args:
            file_path: Path to .dat.gz file
            batch_size: Records per batch
            max_records: Maximum records to process (for testing)

        Returns:
            List of detected China-related transactions
        """

        print(f"\n{'='*80}")
        print(f"Processing: {file_path.name}")
        print(f"Size: {file_path.stat().st_size / (1024**3):.1f} GB")
        print(f"{'='*80}\n")

        detections = []
        batch = []
        record_count = 0

        with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                # Progress indicator
                if line_num % 100000 == 0:
                    print(f"  Processed {line_num:,} lines, "
                          f"detected {len(detections):,} China-related")

                # Parse record
                fields = line.strip().split('\t')
                if len(fields) < 206:
                    continue  # Skip incomplete records

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
                    detections.append(detection_record)

                    # Update statistics
                    self.stats['china_detected'] += 1
                    self.stats['total_value'] += transaction.federal_action_obligation

                    for result in detection_results:
                        self.stats['by_detection_type'][result.detection_type] += 1
                        self.stats['by_confidence'][result.confidence] += 1

                record_count += 1
                self.stats['total_records'] += 1

                # Stop if reached max
                if max_records and record_count >= max_records:
                    print(f"\n  Reached max records limit: {max_records:,}")
                    break

        print(f"\n  Completed: {record_count:,} records processed")
        print(f"  Detected: {len(detections):,} China-related transactions")

        return detections

    def _extract_transaction(self, fields: List[str]) -> Transaction:
        """Extract transaction from fields using schema mapping."""

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

        return Transaction(
            transaction_id=get_field(2),
            piid=get_field(4),
            fain=get_field(120),
            recipient_name=get_field(23),
            recipient_parent_name=get_field(27),
            recipient_country=get_field(29),
            pop_country=get_field(39),
            sub_awardee_name=get_field(59),
            sub_awardee_parent_name=get_field(63),
            sub_awardee_country=get_field(65),
            award_description=get_field(46),
            subaward_description=get_field(82),
            federal_action_obligation=get_float(6),
            total_dollars_obligated=get_float(140),
            awarding_agency=get_field(16),
            funding_agency=get_field(10),
            naics_code=get_field(47),
            naics_description=get_field(48),
            psc_code=get_field(163),
            psc_description=get_field(164),
            action_date=get_field(7),
            fiscal_year=get_field(8),
            recipient_uei=get_field(22),
            recipient_duns=get_field(21),
        )

    def _detect_china_entity(self, transaction: Transaction,
                             fields: List[str]) -> List[DetectionResult]:
        """
        Multi-field China entity detection.

        Returns list of detection results (can have multiple signals).
        """

        results = []

        # 1. COUNTRY CHECK (highest confidence)
        # Check recipient country
        # OPTION B: Check if this is product sourcing (data quality error)
        if self._is_china_country(transaction.recipient_country):
            if self._is_product_sourcing_mention(transaction.award_description):
                # Product sourcing - separate category
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='china_sourced_product',
                    field_index=29,
                    field_name='recipient_location_country_name',
                    matched_value=transaction.recipient_country,
                    confidence='LOW',
                    rationale='Product origin language detected (possible data quality error)'
                ))
            else:
                # Legitimate Chinese entity
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='country',
                    field_index=29,
                    field_name='recipient_location_country_name',
                    matched_value=transaction.recipient_country,
                    confidence='HIGH',
                    rationale=f'Recipient located in {transaction.recipient_country}'
                ))

        # Check place of performance country
        # OPTION B: Check if this is product sourcing (data quality error like T K C ENTERPRISES)
        if self._is_china_country(transaction.pop_country):
            if self._is_product_sourcing_mention(transaction.award_description):
                # Product sourcing - likely data entry error (pop_country=CHN for US company)
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='china_sourced_product',
                    field_index=39,
                    field_name='pop_country_name',
                    matched_value=transaction.pop_country,
                    confidence='LOW',
                    rationale='Product origin language detected (possible data quality error)'
                ))
            else:
                # Legitimate China place of performance
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='country',
                    field_index=39,
                    field_name='pop_country_name',
                    matched_value=transaction.pop_country,
                    confidence='HIGH',
                    rationale=f'Work performed in {transaction.pop_country}'
                ))

        # Check sub-awardee country
        # OPTION B: Check if this is product sourcing (data quality error)
        if self._is_china_country(transaction.sub_awardee_country):
            # Check both main description and subaward description
            is_product_sourcing = (
                self._is_product_sourcing_mention(transaction.award_description) or
                self._is_product_sourcing_mention(transaction.subaward_description)
            )

            if is_product_sourcing:
                # Product sourcing - separate category
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='china_sourced_product',
                    field_index=65,
                    field_name='sub_awardee_country_name',
                    matched_value=transaction.sub_awardee_country,
                    confidence='LOW',
                    rationale='Product origin language detected (possible data quality error)'
                ))
            else:
                # Legitimate Chinese sub-contractor
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='country',
                    field_index=65,
                    field_name='sub_awardee_country_name',
                    matched_value=transaction.sub_awardee_country,
                    confidence='HIGH',
                    rationale=f'Sub-contractor in {transaction.sub_awardee_country}'
                ))

        # 2. ENTITY NAME CHECK (medium-high confidence)
        # Check recipient name
        entity_match = self._find_china_entity(transaction.recipient_name)
        if entity_match:
            results.append(DetectionResult(
                is_detected=True,
                detection_type='entity_name',
                field_index=23,
                field_name='recipient_name',
                matched_value=entity_match,
                confidence='HIGH',
                rationale=f'Known Chinese entity: {entity_match} in recipient name'
            ))

        # Check recipient parent name
        entity_match = self._find_china_entity(transaction.recipient_parent_name)
        if entity_match:
            results.append(DetectionResult(
                is_detected=True,
                detection_type='parent',
                field_index=27,
                field_name='recipient_parent_name',
                matched_value=entity_match,
                confidence='HIGH',
                rationale=f'Chinese parent company: {entity_match}'
            ))

        # Check sub-awardee name (with smart country/parent verification)
        entity_match = self._find_china_entity(transaction.sub_awardee_name)
        if entity_match:
            # OPTION A: Flag US subsidiaries of Chinese companies
            # Check if:
            # 1. Country is China/Hong Kong, OR
            # 2. Parent company is Chinese (even if sub-awardee is US-based)
            is_china_based = self._is_china_country(transaction.sub_awardee_country)
            has_chinese_parent = self._find_china_entity(transaction.sub_awardee_parent_name) is not None

            if is_china_based or has_chinese_parent:
                location_note = transaction.sub_awardee_country if is_china_based else f"US subsidiary"
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='sub_awardee',
                    field_index=59,
                    field_name='sub_awardee_name',
                    matched_value=entity_match,
                    confidence='HIGH',
                    rationale=f'Chinese sub-contractor: {entity_match} ({location_note})'
                ))
            # Else: US company with no Chinese parent (like COSCO Fire Protection) - false positive

        # Check sub-awardee parent (with country verification)
        entity_match = self._find_china_entity(transaction.sub_awardee_parent_name)
        if entity_match:
            # Flag if parent company is Chinese (regardless of sub-awardee country)
            # This catches Lenovo Group Limited owning Lenovo (US) Inc
            results.append(DetectionResult(
                is_detected=True,
                detection_type='sub_awardee_parent',
                field_index=63,
                field_name='sub_awardee_parent_name',
                matched_value=entity_match,
                confidence='HIGH',
                rationale=f'Chinese parent company: {entity_match}'
            ))

        # 3. DESCRIPTION CHECK (medium confidence, requires context)
        # Check if description mentions China + sensitive technology
        if self._is_sensitive_context(transaction):
            desc_match = self._find_china_in_description(transaction)
            if desc_match:
                results.append(DetectionResult(
                    is_detected=True,
                    detection_type='description',
                    field_index=46,
                    field_name='award_description',
                    matched_value=desc_match,
                    confidence='MEDIUM',
                    rationale=f'China mentioned in sensitive tech context: {desc_match}'
                ))

        return results

    def _is_china_country(self, country: str) -> bool:
        """Check if country field indicates China (PRC only, NOT Taiwan/ROC)."""
        if not country:
            return False

        country_lower = country.lower().strip()

        # CRITICAL: Taiwan (ROC) is NOT China (PRC)
        # Exclude any mentions of Taiwan
        if 'taiwan' in country_lower or country_lower == 'twn':
            return False

        return any(china_country in country_lower
                   for china_country in self.CHINA_COUNTRIES)

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


    def _find_china_entity(self, text: str) -> Optional[str]:
        """
        Find known Chinese entity in text with proper word boundaries.

        Uses word boundary matching for ALL entities to avoid false positives.
        """
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

    def _is_sensitive_context(self, transaction: Transaction) -> bool:
        """Check if transaction is in sensitive technology context."""

        # Check NAICS code
        if transaction.naics_code:
            for prefix, desc in self.SENSITIVE_NAICS.items():
                if transaction.naics_code.startswith(prefix):
                    return True

        # Check agency
        for agency in self.SENSITIVE_AGENCIES:
            if agency.lower() in transaction.awarding_agency.lower():
                return True
            if agency.lower() in transaction.funding_agency.lower():
                return True

        return False

    def _find_china_in_description(self, transaction: Transaction) -> Optional[str]:
        """
        Find China mentions in descriptions.

        NOTE: Very conservative to avoid false positives.
        - Removed 'prc' (causes false matches with military equipment codes like PRC-90-2)
        - Only flags if China is mentioned with procurement/contracting context
        """

        descriptions = [
            transaction.award_description,
            transaction.subaward_description
        ]

        for desc in descriptions:
            if not desc:
                continue
            desc_lower = desc.lower()

            # Look for China keywords (removed 'prc' due to military acronyms)
            for keyword in ['chinese company', 'chinese supplier', 'chinese manufacturer',
                           'china-based', 'beijing-based', 'shanghai-based']:
                if keyword in desc_lower:
                    # Extract context (50 chars around keyword)
                    idx = desc_lower.find(keyword)
                    start = max(0, idx - 25)
                    end = min(len(desc), idx + 25)
                    context = desc[start:end]
                    return f"...{context}..."

        return None

    def _build_detection_record(self, transaction: Transaction,
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
            'piid': transaction.piid,
            'fain': transaction.fain,
            'recipient_uei': transaction.recipient_uei,
            'recipient_duns': transaction.recipient_duns,

            # Entity information
            'recipient_name': transaction.recipient_name,
            'recipient_parent_name': transaction.recipient_parent_name,
            'recipient_country': transaction.recipient_country,
            'pop_country': transaction.pop_country,
            'sub_awardee_name': transaction.sub_awardee_name,
            'sub_awardee_parent_name': transaction.sub_awardee_parent_name,
            'sub_awardee_country': transaction.sub_awardee_country,

            # Financial
            'federal_action_obligation': transaction.federal_action_obligation,
            'total_dollars_obligated': transaction.total_dollars_obligated,

            # Agency and classification
            'awarding_agency': transaction.awarding_agency,
            'funding_agency': transaction.funding_agency,
            'naics_code': transaction.naics_code,
            'naics_description': transaction.naics_description,
            'psc_code': transaction.psc_code,
            'psc_description': transaction.psc_description,

            # Dates
            'action_date': transaction.action_date,
            'fiscal_year': transaction.fiscal_year,

            # Descriptions
            'award_description': transaction.award_description[:500],  # Truncate
            'subaward_description': transaction.subaward_description[:500],

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
            'importance_tier': importance_tier,
            'importance_score': importance_score,
            'commodity_type': commodity_type,
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

    def save_results(self, detections: List[Dict], file_name: str):
        """Save detection results."""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON
        output_file = self.output_dir / f"{file_name}_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_date': timestamp,
                'file_processed': file_name,
                'total_detections': len(detections),
                'statistics': dict(self.stats),
                'detections': detections
            }, f, indent=2)

        print(f"\nSaved {len(detections):,} detections to: {output_file}")

        # Save to database
        self._save_to_database(detections)

    def _save_to_database(self, detections: List[Dict]):
        """Save detections to master database."""

        if not self.db_path.exists():
            print(f"Warning: Database not found: {self.db_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Create table if not exists
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usaspending_china_comprehensive (
                transaction_id TEXT PRIMARY KEY,
                piid TEXT,
                fain TEXT,
                recipient_uei TEXT,
                recipient_name TEXT,
                recipient_parent_name TEXT,
                recipient_country TEXT,
                pop_country TEXT,
                sub_awardee_name TEXT,
                sub_awardee_parent_name TEXT,
                sub_awardee_country TEXT,
                federal_action_obligation REAL,
                total_dollars_obligated REAL,
                awarding_agency TEXT,
                funding_agency TEXT,
                naics_code TEXT,
                naics_description TEXT,
                psc_code TEXT,
                action_date TEXT,
                fiscal_year TEXT,
                award_description TEXT,
                detection_count INTEGER,
                detection_types TEXT,
                highest_confidence TEXT,
                detection_details TEXT,
                processed_date TEXT
            )
        ''')

        # Create indexes
        cur.execute('CREATE INDEX IF NOT EXISTS idx_usaspending_recipient ON usaspending_china_comprehensive(recipient_name)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_usaspending_country ON usaspending_china_comprehensive(recipient_country)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_usaspending_confidence ON usaspending_china_comprehensive(highest_confidence)')

        # Insert records
        for detection in detections:
            cur.execute('''
                INSERT OR REPLACE INTO usaspending_china_comprehensive VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                detection['transaction_id'],
                detection['piid'],
                detection['fain'],
                detection['recipient_uei'],
                detection['recipient_name'],
                detection['recipient_parent_name'],
                detection['recipient_country'],
                detection['pop_country'],
                detection['sub_awardee_name'],
                detection['sub_awardee_parent_name'],
                detection['sub_awardee_country'],
                detection['federal_action_obligation'],
                detection['total_dollars_obligated'],
                detection['awarding_agency'],
                detection['funding_agency'],
                detection['naics_code'],
                detection['naics_description'],
                detection['psc_code'],
                detection['action_date'],
                detection['fiscal_year'],
                detection['award_description'],
                detection['detection_count'],
                json.dumps(detection['detection_types']),
                detection['highest_confidence'],
                json.dumps(detection['detection_details']),
                detection['processed_date'],
            ))

        conn.commit()
        conn.close()

        print(f"Saved {len(detections):,} records to database")

    def print_summary(self):
        """Print processing summary."""

        print(f"\n{'='*80}")
        print("PROCESSING SUMMARY")
        print(f"{'='*80}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Total records: {self.stats['total_records']:,}")
        print(f"China detections: {self.stats['china_detected']:,} "
              f"({self.stats['china_detected']/self.stats['total_records']*100:.2f}%)")
        print(f"Total value: ${self.stats['total_value']:,.2f}")

        print(f"\nDetection Types:")
        for det_type, count in sorted(self.stats['by_detection_type'].items()):
            print(f"  {det_type}: {count:,}")

        print(f"\nConfidence Levels:")
        for confidence, count in sorted(self.stats['by_confidence'].items()):
            print(f"  {confidence}: {count:,}")

        print(f"{'='*80}\n")


def main():
    """Test on sample file."""

    print("USAspending Comprehensive Processor")
    print("="*80)

    processor = USAspendingComprehensiveProcessor()

    # Test on one file with limited records
    test_file = Path("F:/OSINT_DATA/USAspending/extracted_data/5876.dat.gz")

    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return

    print(f"\nTEST MODE: Processing first 100,000 records")
    print(f"File: {test_file.name}\n")

    # Process
    detections = processor.process_file(test_file, max_records=100000)

    # Save
    processor.save_results(detections, test_file.stem)

    # Summary
    processor.stats['files_processed'] = 1
    processor.print_summary()

    # Show sample detections
    if detections:
        print("\nSample Detections (first 3):")
        print("-" * 80)
        for i, detection in enumerate(detections[:3], 1):
            print(f"\n{i}. {detection['recipient_name']}")
            print(f"   Amount: ${detection['federal_action_obligation']:,.2f}")
            print(f"   Confidence: {detection['highest_confidence']}")
            print(f"   Detections: {detection['detection_count']}")
            for detail in detection['detection_details']:
                print(f"     - {detail['type']}: {detail['rationale']}")


if __name__ == '__main__':
    main()
