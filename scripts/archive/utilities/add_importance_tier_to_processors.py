#!/usr/bin/env python3
"""
Add Importance Tier Categorization to USAspending Processors

This script contains the importance tier categorization function that needs
to be added to all three processors (305, 101, comprehensive).

The function will be added to the processor class and called during detection.
"""

# This is the categorization function to add to each processor class

CATEGORIZATION_METHOD = '''
    # ========== IMPORTANCE TIER CATEGORIZATION ==========

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

        # TIER 1: Strategic Entities (name match)
        for entity in self.TIER_1_STRATEGIC_ENTITIES:
            if entity in recipient or entity in vendor:
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

    # ========== END IMPORTANCE TIER CATEGORIZATION ==========
'''

# Instructions for adding to _detect_china_connection method
DETECTION_UPDATE_INSTRUCTIONS = '''
# In _detect_china_connection method, before returning the detection dict, add:

        # Categorize importance tier
        importance_tier, importance_score, commodity_type = self._categorize_importance(
            recipient_name=recipient_name,
            vendor_name=vendor_name,
            description=award_description
        )

# Then add these fields to the return dict:

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
            # NEW FIELDS:
            'importance_tier': importance_tier,
            'importance_score': importance_score,
            'commodity_type': commodity_type,
        }
'''

# Instructions for updating _save_batch method
SAVE_BATCH_UPDATE_INSTRUCTIONS = '''
# In _save_batch method, update the INSERT statement:

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
'''

print("="*80)
print("IMPORTANCE TIER CATEGORIZATION CODE")
print("="*80)
print("\n1. Add this method to the processor class (after __init__):")
print(CATEGORIZATION_METHOD)
print("\n2. Update _detect_china_connection method:")
print(DETECTION_UPDATE_INSTRUCTIONS)
print("\n3. Update _save_batch method:")
print(SAVE_BATCH_UPDATE_INSTRUCTIONS)
print("\n" + "="*80)
print("Apply these changes to all three processors:")
print("  - scripts/process_usaspending_305_column.py")
print("  - scripts/process_usaspending_101_column.py")
print("  - scripts/process_usaspending_comprehensive.py")
print("="*80)
