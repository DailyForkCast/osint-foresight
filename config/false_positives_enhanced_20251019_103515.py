#!/usr/bin/env python3
"""
Enhanced False Positive Filters
Generated: 2025-10-19 10:35:15

Add these to your processors' FALSE_POSITIVES configuration
"""

# European Companies (SINO prefix, Italian manufacturers)
EUROPEAN_COMPANIES = ['SINOVA SICHERHEIT & TECHNIK', 'FIAT SPA', 'FP PERISSINOTTO IMBALLI', 'IVECO MAGIRUS', 'DYNEX SEMICONDUCTOR']

# Multilingual Insurance Terms
INSURANCE_MULTILINGUAL = {
    'russian': ['STRAKHOVAYA KOMPANIYA', 'STRAKHOVAYA', 'MEDITSINSKAYA STRAKHOVAYA'],
    'german': ['VERSICHERUNG', 'KRANKENVERSICHERUNG', 'LEBENSVERSICHERUNG'],
    'french': ['ASSURANCE', 'ASSURANCES', "COMPAGNIE D'ASSURANCE"],
    'spanish': ['SEGUROS', 'COMPANIA DE SEGUROS'],
    'italian': ['ASSICURAZIONE', 'ASSICURAZIONI'],
}

# Combined False Positive Patterns
FALSE_POSITIVE_PATTERNS = {
    # Existing patterns
    'substring_china': [
        r'\bkachina\b',
        r'\bcatalina\s+china\b',
        r'\bfacchina\b',
    ],

    'porcelain_tableware': [
        r'\bchina\s+porcelain\b',
        r'\bfine\s+china\b',
        r'\bbone\s+china\b',
        r'\bchina\s+dinnerware\b',
    ],

    'casino_hotel': [
        r'\bcasino\b',
        r'\bresort\b',
        r'\bhotel\b',
    ],

    # NEW - European companies
    'european_companies': [
        r'\bsinova\s+sicherheit\b',
        r'\bfiat\s+spa\b',
        r'\biveco\s+magirus\b',
        r'\bfp\s+perissinotto\b',
    ],

    # NEW - Multilingual insurance
    'insurance_russian': [
        r'\bstrakhovaya\s+kompaniya\b',
        r'\bstrakhovaya\b',
    ],

    'insurance_german': [
        r'\bversicherung\b',
    ],

    'insurance_french': [
        r'\bassurance\b',
        r'\bassurances\b',
    ],

    'insurance_spanish': [
        r'\bseguros\b',
    ],

    'insurance_italian': [
        r'\bassicurazione\b',
        r'\bassicurazioni\b',
    ],
}

# Entity-specific exclusions
EXCLUDE_ENTITIES = [
    'SINOVA SICHERHEIT & TECHNIK GM',
    'FIAT SPA',
    'FP PERISSINOTTO IMBALLI SRL',
    'IVECO MAGIRUS BRANDSCHUTZTECHN',
    'MEDITSINSKAYA STRAKHOVAYA KOMPANIYA',
]
