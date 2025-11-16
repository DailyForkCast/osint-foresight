#!/usr/bin/env python3
"""
TIER_2 False Positive Filters
Auto-generated from manual audit on 2025-10-18 22:44:35

Add these to your processors' FALSE_POSITIVES list
"""

TIER2_FALSE_POSITIVES = [
    # Substring matches (Kachina, Catalina, Facchina)
    "AIA LIFE INSURANCE COMPANY LIMITED BEIJING BRANCH",
    "BEIJING ADEN HOTEL SERVICES CO.  LTD.",
    "BEIJING ZHICHENG HUAYUAN HOTEL MANAGEMENT CONSULTING CENTER ?ORDINARY PARTNERSH IP)",
    "BOYD GAMING CORPORATION",
    "CASINO AUTO BODY INC",
    "CATALINA CHINA  INC.",
    "CHINA LIFE INSURANCE COMPANY",
    "FACCHINA GLOBAL SERVICES  LLC",
    "HARRAHS SHREVEPORT CASINO AND",
    "KACHINA INVESTMENTS LLC",
    "KACHINA VENTURES LLC",
    "MSD BIZTECH CONSULTING  INC.",
    "PEPPERS CASINO & RESTAURANT",
    "RIVERSIDE CASINO & GOLF RESORT  LLC",
    "SAFARI PARK HOTEL & CASINO",
    "SINOASIA B&R INSURANCE COMPANY JOINT STOCK COMPANY",
    "SKYDIVE ELSINORE INC",
    "SOC COOP LIVORNESE FACCHINAGGI E TRASPORTI",
    "THE PORTMAN RITZ-CATLTON HOTEL",
]

# Pattern-based filters (add to processor logic)
FALSE_POSITIVE_PATTERNS = {
    'substring_china': [
        r'\bkachina\b',
        r'\bcatalina china\b',
        r'\bfacchina\b',
    ],
    'casino_hotel': [
        r'\bcasino\b',
        r'\bresort\b',
        r'\bhotel\b',
    ],
    'italian_companies': [
        r'\bsoc coop livornese\b',
        r'\bfacchinaggi\b',
    ]
}
