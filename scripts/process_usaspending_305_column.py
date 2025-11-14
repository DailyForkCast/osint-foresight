#!/usr/bin/env python3
"""
USAspending 305-Column Format Processor

Processes 305-column USAspending data for Chinese entity detection.
Target: 5848.dat.gz (15.4 GB)

CRITICAL: Taiwan (ROC) is NOT China (PRC) - explicitly excluded
"""

import gzip
import json
import sqlite3
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Import language detection helper for European language false positive filtering
sys.path.insert(0, str(Path(__file__).parent))
from language_detection_helper import EuropeanLanguageDetector


class USAspending305Processor:
    """Process 305-column USAspending format for China detection."""

    # China country identifiers (PRC only, NOT Taiwan/ROC)
    CHINA_COUNTRIES = {
        'china', 'chinese', 'prc', 'p.r.c.', 'p r c', 'p. r. c.',  # PRC variants
        'people\'s republic',
        'beijing', 'shanghai', 'guangzhou', 'shenzhen',
        'chongqing', 'tianjin', 'wuhan', 'xi\'an',
        'hangzhou', 'nanjing', 'chengdu', 'dalian',
        'chn'  # China country code
    }

    # CRITICAL: Taiwan exclusion patterns
    TAIWAN_EXCLUSIONS = {
        'taiwan', 'twn', 'republic of china', 'roc', 'taipei',
        'formosa', 'chinese taipei'
    }

    # Hong Kong detection
    HONG_KONG = {'hong kong', 'hongkong', 'hkg', 'h.k.', 'hk'}

    # Chinese name indicators
    CHINESE_NAME_PATTERNS = {
        # Major cities
        'beijing', 'shanghai', 'guangzhou', 'shenzhen',
        'hong kong',  # Also catches "Hong-Kong" after normalization
        'china', 'chinese', 'sino',

        # Tech companies (BIS Entity List)
        'huawei', 'hwawei', 'huawai', 'huwei',  # Huawei + common misspellings
        'zte',
        'hikvision', 'dahua',
        'hytera',

        # Other major companies
        'alibaba', 'tencent', 'baidu', 'lenovo',
        'haier', 'xiaomi', 'byd', 'geely',

        # Defense/aerospace (BIS Entity List)
        'comac', 'avic', 'norinco', 'cssc',

        # Semiconductor (BIS Entity List)
        'semiconductor manufacturing international',
        'smic',

        # Research institutions (BIS Entity List)
        'academy of military medical sciences',
        'china academy of aerospace',
        'china electronics technology group',
        'cetc',

        # Universities (BIS Entity List) - Major Chinese universities
        'beihang university',
        'harbin institute of technology',
        'harbin engineering university',
        'northwestern polytechnical university',
        'nanjing university of aeronautics',
        'nanjing university of science and technology',
        'national university of defense technology',
        'sichuan university',
        'tianjin university',
        'tsinghua', 'peking university',
        'chinese academy of sciences',
        'chinese academy',
    }

    # Known false positives to exclude
    FALSE_POSITIVES = {
        'boeing', 'comboed', 'senior', 'union', 'junior',
        'opportunities', 'opportunity', 'opposite', 'opposition',
        'corrections', 'crrctns',
        # Geographic false positives
        'san antonio',
        'china beach',  # California location
        'china cove',
        'indochina',  # Historical region, not PRC
        'indo-china',
        'french indochina',
        # Restaurant chains
        'china king',
        'china king restaurant',
        'great wall chinese restaurant',
        'great wall restaurant',
        'chinese restaurant',
        'chinese food',
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
        # Round 5: Audit-discovered false positives (2025-11-03)
        'china wok',  # US restaurant
        'chinese historical society',  # US cultural organizations
        'chinese american museum',  # US museum
        'museum of chinese',  # US museums
        'chinati foundation',  # US art museum (Marfa, Texas)
        'china, michigan',  # US town
    }

    # 305-column schema based on deep analysis
    SCHEMA = {
        0: 'transaction_id',
        1: 'award_identifier',
        4: 'action_date',
        8: 'funding_agency_code',
        10: 'award_description',
        13: 'vendor_name',
        21: 'federal_action_obligation',
        22: 'base_and_exercised_options_value',
        49: 'pop_country_name',  # Place of Performance
        50: 'pop_country_code',
        69: 'base_and_all_options_value',
        107: 'recipient_country_code',  # CHN, USA, etc.
        108: 'recipient_country_name',  # CHINA, UNITED STATES, etc.
        160: 'award_amount',  # Primary award amount
        192: 'current_total_value',
        200: 'recipient_name',  # Primary recipient name
    }


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
        """Initialize processor."""
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/usaspending_305")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize European language false positive detector
        self.language_detector = EuropeanLanguageDetector(confidence_threshold=0.8)

        self.stats = {
            'total_records': 0,
            'china_detected': 0,
            'files_processed': 0,
            'total_value': 0.0,
        }

        self.detection_buffer = []
        self.batch_size = 5000

        self._init_database()

    def _init_database(self):
        """Initialize database and create table."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS usaspending_china_305 (
                transaction_id TEXT PRIMARY KEY,
                award_id TEXT,
                recipient_name TEXT,
                recipient_country_code TEXT,
                recipient_country_name TEXT,
                pop_country_code TEXT,
                pop_country_name TEXT,
                award_amount REAL,
                award_description TEXT,
                funding_agency_code TEXT,
                vendor_name TEXT,
                action_date TEXT,
                detection_count INTEGER,
                detection_types TEXT,
                highest_confidence TEXT,
                detection_details TEXT,
                processed_date TEXT,
                format TEXT DEFAULT '305-column'
            )
        ''')

        # Create indexes
        cur.execute('CREATE INDEX IF NOT EXISTS idx_305_recipient_country ON usaspending_china_305(recipient_country_code)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_305_pop_country ON usaspending_china_305(pop_country_code)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_305_amount ON usaspending_china_305(award_amount)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_305_date ON usaspending_china_305(action_date)')

        conn.commit()
        conn.close()

        print(f"Database initialized: {self.db_path}")
        print(f"Table: usaspending_china_305")

    def _is_china_country(self, country: str) -> bool:
        """Check if country field indicates China (PRC only, NOT Taiwan/ROC)."""
        if not country:
            return False

        country_lower = country.lower().strip()

        # CRITICAL: Taiwan (ROC) is NOT China (PRC) - check all Taiwan patterns
        for taiwan_pattern in self.TAIWAN_EXCLUSIONS:
            if taiwan_pattern in country_lower:
                return False

        # Check for false positives (restaurants, locations, etc.)
        for false_positive in self.FALSE_POSITIVES:
            if false_positive in country_lower:
                return False

        return any(china_country in country_lower
                   for china_country in self.CHINA_COUNTRIES)

    def _is_hong_kong(self, country: str) -> bool:
        """Check if country indicates Hong Kong."""
        if not country:
            return False
        return any(hk in country.lower() for hk in self.HONG_KONG)

    def _has_chinese_name(self, name: str) -> bool:
        """Check if name suggests Chinese entity with proper word boundaries.

        Includes normalization to catch obfuscation:
        - Spaced: "H u a w e i"
        - Hyphenated: "Hua-wei"
        - Punctuated: "Hua.wei", "Hua,wei"
        - Unicode: Zero-width spaces, Cyrillic lookalikes
        """
        if not name:
            return False

        # PRIORITY 2.1: Unicode normalization (remove zero-width, normalize lookalikes)
        import unicodedata

        # Remove zero-width characters
        name_clean = name
        zero_width_chars = [
            '\u200B',  # Zero-width space
            '\u200C',  # Zero-width non-joiner
            '\u200D',  # Zero-width joiner
            '\uFEFF',  # Zero-width no-break space
        ]
        for zwc in zero_width_chars:
            name_clean = name_clean.replace(zwc, '')

        # Normalize Unicode to NFD (decomposed) then remove combining marks
        name_clean = unicodedata.normalize('NFD', name_clean)

        # Map Cyrillic/Greek lookalikes to Latin equivalents
        cyrillic_to_latin = {
            'а': 'a', 'А': 'A',  # Cyrillic a
            'е': 'e', 'Е': 'E',  # Cyrillic e/ye
            'о': 'o', 'О': 'O',  # Cyrillic o
            'р': 'p', 'Р': 'P',  # Cyrillic r
            'с': 'c', 'С': 'C',  # Cyrillic s
            'у': 'y', 'У': 'Y',  # Cyrillic u
            'х': 'x', 'Х': 'X',  # Cyrillic kh
            'Н': 'H',            # Cyrillic N (looks like Latin H)
            'Т': 'T',            # Cyrillic T (looks like Latin T)
            'Η': 'H',            # Greek capital Eta
        }
        for cyr, lat in cyrillic_to_latin.items():
            name_clean = name_clean.replace(cyr, lat)

        name_lower = name_clean.lower()

        # CRITICAL: Taiwan exclusion - check all patterns
        for taiwan_pattern in self.TAIWAN_EXCLUSIONS:
            if taiwan_pattern in name_lower:
                return False

        # Check for false positives first
        for false_positive in self.FALSE_POSITIVES:
            if false_positive in name_lower:
                return False

        # PRIORITY 1.2: Enhanced normalization (remove spaces, hyphens, punctuation)
        # This catches: "H u a w e i", "Hua-wei", "Hua.wei", "Hua_wei", etc.
        name_normalized = re.sub(r'[\s\-._/,]+', '', name_lower)

        # Check Chinese name patterns
        pattern_matched = False
        for pattern in self.CHINESE_NAME_PATTERNS:
            # Try exact match with word boundaries first
            word_pattern = r'\b' + re.escape(pattern) + r'\b'
            if re.search(word_pattern, name_lower):
                pattern_matched = True
                break

            # Try normalized match (catches "H u a w e i", "Hua-wei Technologies", etc.)
            # Use SAME normalization as the name (remove spaces, hyphens, punctuation)
            pattern_normalized = re.sub(r'[\s\-._/,]+', '', pattern)

            # Reduce threshold to catch "zte" (3 letters)
            if len(pattern_normalized) >= 3:  # Allow 3+ letter patterns
                # Use only LEADING word boundary (allows "huawei" to match in "huaweitechnologies")
                # This catches "Hua-wei Technologies" where normalized is "huaweitechnologies"
                norm_pattern_regex = r'\b' + re.escape(pattern_normalized)
                if re.search(norm_pattern_regex, name_normalized):
                    pattern_matched = True
                    break

        # If pattern matched, check for European language false positives
        if pattern_matched:
            # CRITICAL FIX: Only use language detector for longer strings WITHOUT company suffixes
            # Short strings like "ZTE" get falsely detected as European languages
            # Company names like "ZTE Corporation" get falsely detected as Italian
            # Skip language detection for:
            # 1. Names < 10 characters
            # 2. Names with company suffixes (Corporation, LLC, Inc, etc.)
            company_suffixes = [
                'corporation', 'corp', 'inc', 'llc', 'ltd', 'limited',
                'company', 'co', 'gmbh', 'ag', 'sa', 'technologies'
            ]
            has_company_suffix = any(suffix in name_lower for suffix in company_suffixes)

            if len(name) >= 10 and not has_company_suffix:
                # Use language detector to filter European language false positives
                lang_result = self.language_detector.analyze_text(name)
                if lang_result.is_likely_false_positive:
                    return False  # European language false positive detected
            return True

        return False

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


    def _detect_china_connection(self, fields: List[str]) -> Optional[Dict[str, Any]]:
        """Detect China connection in record."""

        def get_field(idx: int) -> str:
            if idx < len(fields):
                val = fields[idx].strip()
                return val if val != '\\N' else ''
            return ''

        def get_float(idx: int) -> float:
            val = get_field(idx)
            if not val or val == '\\N':
                return 0.0
            try:
                return float(val.replace(',', ''))
            except:
                return 0.0

        # Get key fields
        recipient_name = get_field(200)
        vendor_name = get_field(13)
        recipient_country_code = get_field(107)
        recipient_country_name = get_field(108)
        pop_country_code = get_field(50)
        pop_country_name = get_field(49)
        award_description = get_field(10)

        detections = []
        confidence_scores = []

        # Detection 1: Recipient country is China
        # OPTION B: Check if this is product sourcing (data quality error)
        if self._is_china_country(recipient_country_code) or self._is_china_country(recipient_country_name):
            if self._is_product_sourcing_mention(award_description):
                # Product sourcing - separate category
                detections.append('china_sourced_product')
                confidence_scores.append(0.30)  # LOW confidence for supply chain tracking
            else:
                # Legitimate Chinese entity
                detections.append('recipient_country_china')
                confidence_scores.append(0.95)

        # Detection 2: Place of Performance is China
        # OPTION B: Check if this is product sourcing (data quality error like T K C ENTERPRISES)
        if self._is_china_country(pop_country_code) or self._is_china_country(pop_country_name):
            if self._is_product_sourcing_mention(award_description):
                # Product sourcing - likely data entry error (pop_country_code=CHN for US company)
                detections.append('china_sourced_product')
                confidence_scores.append(0.30)  # LOW confidence for supply chain tracking
            else:
                # Legitimate China place of performance
                detections.append('pop_country_china')
                confidence_scores.append(0.90)

        # Detection 3: Hong Kong recipient
        if self._is_hong_kong(recipient_country_code) or self._is_hong_kong(recipient_country_name):
            detections.append('recipient_country_hong_kong')
            confidence_scores.append(0.85)

        # Detection 4: Hong Kong place of performance
        if self._is_hong_kong(pop_country_code) or self._is_hong_kong(pop_country_name):
            detections.append('pop_country_hong_kong')
            confidence_scores.append(0.80)

        # Detection 5: Chinese name pattern in recipient
        if self._has_chinese_name(recipient_name):
            detections.append('chinese_name_recipient')
            confidence_scores.append(0.70)

        # Detection 6: Chinese name pattern in vendor
        if self._has_chinese_name(vendor_name):
            detections.append('chinese_name_vendor')
            confidence_scores.append(0.65)

        # If no detections, return None
        if not detections:
            return None

        # Categorize importance tier
        importance_tier, importance_score, commodity_type = self._categorize_importance(
            recipient_name=recipient_name,
            vendor_name=vendor_name,
            description=award_description
        )

        # Build detection result
        return {
            'transaction_id': get_field(0),
            'award_id': get_field(1),
            'recipient_name': recipient_name,
            'recipient_country_code': recipient_country_code,
            'recipient_country_name': recipient_country_name,
            'pop_country_code': pop_country_code,
            'pop_country_name': pop_country_name,
            'award_amount': get_float(160),
            'award_description': get_field(10),
            'funding_agency_code': get_field(8),
            'vendor_name': vendor_name,
            'action_date': get_field(4),
            'detection_count': len(detections),
            'detection_types': json.dumps(detections),
            'highest_confidence': max(confidence_scores),
            'detection_details': json.dumps({
                'detections': detections,
                'confidences': confidence_scores,
                'recipient_country': recipient_country_name or recipient_country_code,
                'pop_country': pop_country_name or pop_country_code,
            }),
            'processed_date': datetime.now().isoformat(),
            'importance_tier': importance_tier,
            'importance_score': importance_score,
            'commodity_type': commodity_type,
        }

    def _save_batch(self):
        """Save current batch to database."""
        if not self.detection_buffer:
            return

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.executemany('''
            INSERT OR REPLACE INTO usaspending_china_305 (
                transaction_id, award_id, recipient_name,
                recipient_country_code, recipient_country_name,
                pop_country_code, pop_country_name,
                award_amount, award_description, funding_agency_code,
                vendor_name, action_date,
                detection_count, detection_types, highest_confidence,
                detection_details, processed_date,
                importance_tier, importance_score, commodity_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            (
                d['transaction_id'], d['award_id'], d['recipient_name'],
                d['recipient_country_code'], d['recipient_country_name'],
                d['pop_country_code'], d['pop_country_name'],
                d['award_amount'], d['award_description'], d['funding_agency_code'],
                d['vendor_name'], d['action_date'],
                d['detection_count'], d['detection_types'], d['highest_confidence'],
                d['detection_details'], d['processed_date'],
                d['importance_tier'], d['importance_score'], d['commodity_type']
            )
            for d in self.detection_buffer
        ])

        conn.commit()
        conn.close()

        self.detection_buffer.clear()

    def process_file(self, file_path: Path, max_records: Optional[int] = None) -> int:
        """Process a single USAspending data file."""

        print(f"\n{'='*80}")
        print(f"Processing 305-column format: {file_path.name}")
        print(f"Size: {file_path.stat().st_size / (1024**3):.1f} GB")
        print(f"{'='*80}\n")

        detections_this_file = 0
        batch_detections = 0

        with gzip.open(file_path, 'rt', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if max_records and i >= max_records:
                    break

                self.stats['total_records'] += 1

                fields = line.strip().split('\t')
                if len(fields) < 200:
                    continue

                detection = self._detect_china_connection(fields)
                if detection:
                    self.detection_buffer.append(detection)
                    detections_this_file += 1
                    batch_detections += 1
                    self.stats['china_detected'] += 1
                    self.stats['total_value'] += detection['award_amount']

                    # Save batch
                    if len(self.detection_buffer) >= self.batch_size:
                        self._save_batch()
                        batch_detections = 0

                # Progress update
                if (i + 1) % 100000 == 0:
                    print(f"  Processed {i + 1:,} lines, detected {self.stats['china_detected']:,} China-related (batch: {batch_detections})")

        # Save remaining
        if self.detection_buffer:
            self._save_batch()

        print(f"\nFile complete: {detections_this_file:,} detections")
        return detections_this_file

    def print_summary(self):
        """Print processing summary."""
        print(f"\nTotal records processed: {self.stats['total_records']:,}")
        print(f"China-related detections: {self.stats['china_detected']:,}")
        print(f"Detection rate: {self.stats['china_detected'] / max(self.stats['total_records'], 1):.4%}")
        print(f"Total award value: ${self.stats['total_value']:,.2f}")
        print(f"Average award value: ${self.stats['total_value'] / max(self.stats['china_detected'], 1):,.2f}")


if __name__ == '__main__':
    # Test mode
    print("305-Column Processor - Test Mode")
    print("Use run_305_production.py for full production run")
