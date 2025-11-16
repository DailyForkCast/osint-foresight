#!/usr/bin/env python3
"""
Expand Country Coverage to 68 Countries
Adds all missing countries with basic template data
"""

import json
from pathlib import Path
from datetime import datetime

# Country name mappings (ISO 2-letter to full name)
COUNTRY_NAMES = {
    'AE': 'United Arab Emirates', 'AL': 'Albania', 'AM': 'Armenia', 'AR': 'Argentina',
    'AT': 'Austria', 'AU': 'Australia', 'AZ': 'Azerbaijan', 'BA': 'Bosnia and Herzegovina',
    'BE': 'Belgium', 'BG': 'Bulgaria', 'BR': 'Brazil', 'BY': 'Belarus',
    'CA': 'Canada', 'CH': 'Switzerland', 'CL': 'Chile', 'CY': 'Cyprus',
    'CZ': 'Czech Republic', 'DE': 'Germany', 'DK': 'Denmark', 'EE': 'Estonia',
    'EG': 'Egypt', 'ES': 'Spain', 'FI': 'Finland', 'FR': 'France',
    'GB': 'United Kingdom', 'GE': 'Georgia', 'GR': 'Greece', 'HR': 'Croatia',
    'HU': 'Hungary', 'IE': 'Ireland', 'IL': 'Israel', 'IN': 'India',
    'IS': 'Iceland', 'IT': 'Italy', 'JP': 'Japan', 'KE': 'Kenya',
    'KR': 'South Korea', 'KZ': 'Kazakhstan', 'LT': 'Lithuania', 'LU': 'Luxembourg',
    'LV': 'Latvia', 'ME': 'Montenegro', 'MK': 'North Macedonia', 'MT': 'Malta',
    'MX': 'Mexico', 'MY': 'Malaysia', 'NG': 'Nigeria', 'NL': 'Netherlands',
    'NO': 'Norway', 'NZ': 'New Zealand', 'PL': 'Poland', 'PT': 'Portugal',
    'RO': 'Romania', 'RS': 'Serbia', 'RU': 'Russia', 'SA': 'Saudi Arabia',
    'SE': 'Sweden', 'SG': 'Singapore', 'SI': 'Slovenia', 'SK': 'Slovakia',
    'TH': 'Thailand', 'TR': 'Turkey', 'TW': 'Taiwan', 'UA': 'Ukraine',
    'US': 'United States', 'VN': 'Vietnam', 'XK': 'Kosovo', 'ZA': 'South Africa'
}

# Priority tier mappings
PRIORITY_TIERS = {
    'tier_1': ['GR', 'HU', 'RS', 'TR'],  # Gateway countries with Chinese penetration
    'tier_2': ['AM', 'AZ', 'BA', 'IS', 'ME', 'MK', 'NO', 'XK'],  # Expanded coverage
    'tier_3': ['BE', 'ES', 'NL', 'SE'],  # Major EU economies
    'tier_4_eu': ['AT', 'BG', 'CY', 'DK', 'FI', 'GE', 'HR', 'LT', 'LU', 'LV', 'MT', 'PT', 'RO', 'SI', 'SK', 'UA'],  # Rest of Europe
    'tier_5_five_eyes': ['US', 'CA', 'AU', 'NZ'],  # Five Eyes allies
    'tier_6_asia_pacific': ['JP', 'KR', 'SG', 'TW', 'IN', 'TH', 'MY', 'VN'],  # Asia-Pacific
    'tier_7_middle_east': ['IL', 'AE', 'SA'],  # Middle East
    'tier_8_latin_america': ['BR', 'MX', 'AR', 'CL'],  # Latin America
    'tier_9_africa': ['ZA', 'EG', 'KE', 'NG'],  # Africa
    'tier_10_russia_sphere': ['RU', 'BY', 'KZ']  # Russia sphere
}

# China bilateral agreements (basic templates)
CHINA_TREATIES = {
    # Europe
    'GR': ['Greece-China Comprehensive Strategic Partnership (2006)', 'BRI MOU (2019)'],
    'HU': ['Hungary-China Comprehensive Strategic Partnership (2017)', 'BRI MOU (2015)'],
    'RS': ['Serbia-China Comprehensive Strategic Partnership (2016)', 'BRI MOU (2016)'],
    'TR': ['Turkey-China Strategic Cooperation (2010)'],
    'RO': ['Romania-China Strategic Partnership (2013)'],
    'BG': ['Bulgaria-China Strategic Partnership (2014)'],
    'HR': ['Croatia-China Strategic Partnership (2005)'],

    # Five Eyes
    'US': ['US-China Phase One Trade Deal (2020)', 'US-China Science & Technology Cooperation Agreement'],
    'CA': ['Canada-China Foreign Investment Promotion and Protection Agreement (2012)'],
    'AU': ['Australia-China Free Trade Agreement (2015)'],
    'NZ': ['New Zealand-China Free Trade Agreement (2008)'],

    # Asia-Pacific
    'JP': ['Japan-China Strategic Mutually Beneficial Relationship (2008)'],
    'KR': ['South Korea-China Strategic Cooperative Partnership (2008)', 'ROK-China FTA (2015)'],
    'SG': ['Singapore-China Free Trade Agreement (2008)'],
    'TW': ['Economic Cooperation Framework Agreement (ECFA) (2010)'],  # Taiwan-specific
    'TH': ['Thailand-China Strategic Partnership (2012)'],
    'MY': ['Malaysia-China Comprehensive Strategic Partnership (2013)'],
    'VN': ['Vietnam-China Comprehensive Strategic Cooperative Partnership (2008)'],
    'IN': ['India-China Strategic Cooperative Partnership (2005)'],

    # Middle East
    'IL': ['Israel-China Innovation Partnership (2013)'],
    'AE': ['UAE-China Strategic Partnership (2012)'],
    'SA': ['Saudi Arabia-China Comprehensive Strategic Partnership (2016)'],

    # Latin America
    'BR': ['Brazil-China Strategic Partnership (1993)'],
    'MX': ['Mexico-China Strategic Partnership (2013)'],
    'AR': ['Argentina-China Comprehensive Strategic Partnership (2014)'],
    'CL': ['Chile-China Free Trade Agreement (2005)'],

    # Africa
    'ZA': ['South Africa-China Comprehensive Strategic Partnership (2010)'],
    'EG': ['Egypt-China Comprehensive Strategic Partnership (2014)'],
    'KE': ['Kenya-China Strategic Partnership (2005)'],
    'NG': ['Nigeria-China Strategic Partnership (2005)'],

    # Russia sphere
    'RU': ['Russia-China Comprehensive Strategic Partnership of Coordination (2001)'],
    'BY': ['Belarus-China Strategic Partnership (2013)'],
    'KZ': ['Kazakhstan-China Comprehensive Strategic Partnership (2013)', 'BRI Key Partner'],

    # Caucasus/Eastern Partnership
    'AM': ['Armenia-China Strategic Partnership (2015)'],
    'AZ': ['Azerbaijan-China Strategic Partnership (2015)'],
    'GE': ['Georgia-China Strategic Partnership (2015)'],
    'UA': ['Ukraine-China Strategic Partnership (2011)'],

    # Balkans
    'BA': ['Bosnia-China Strategic Partnership (2017)'],
    'ME': ['Montenegro-China Strategic Cooperation (2013)'],
    'MK': ['North Macedonia-China Strategic Partnership (2013)'],
    'XK': ['Kosovo-China limited relations (no formal recognition)'],

    # Nordic/Baltic
    'NO': ['Norway-China FTA Negotiations'],
    'IS': ['Iceland-China Free Trade Agreement (2013)'],
    'SE': ['Sweden-China Innovation Partnership'],
    'DK': ['Denmark-China Comprehensive Strategic Partnership (2008)'],
    'FI': ['Finland-China Future-Oriented Partnership (2017)'],
    'LT': ['Lithuania-China Strategic Partnership (2012)'],
    'LV': ['Latvia-China Strategic Partnership (2016)'],

    # Other EU
    'AT': ['Austria-China Strategic Partnership (2018)'],
    'BE': ['Belgium-China Comprehensive Partnership (2014)'],
    'NL': ['Netherlands-China Comprehensive Partnership (2014)'],
    'ES': ['Spain-China Comprehensive Strategic Partnership (2005)'],
    'PT': ['Portugal-China Strategic Partnership (2005)'],
    'CY': ['Cyprus-China Strategic Partnership (2015)'],
    'MT': ['Malta-China Strategic Partnership (2014)'],
    'LU': ['Luxembourg-China Financial Cooperation'],
    'SI': ['Slovenia-China Strategic Partnership (2017)'],
    'SK': ['Slovakia-China Strategic Partnership (2015)'],
}


def create_country_template(country_code: str) -> dict:
    """Create basic template for a country"""

    country_name = COUNTRY_NAMES.get(country_code, country_code)

    template = {
        "country_name": country_name,
        "iso_code": country_code,
        "procurement": {
            "national_platforms": [
                {
                    "name": f"{country_name} National Procurement Platform",
                    "url": "",
                    "description": "To be researched",
                    "data_types": ["tenders", "contracts", "awards"],
                    "api_available": False,
                    "collection_method": "To be determined"
                }
            ]
        },
        "company_registries": {
            "primary": {
                "name": f"{country_name} Business Register",
                "url": "",
                "data_types": ["company_data", "officers", "filings"],
                "access": "To be researched"
            },
            "beneficial_ownership": {
                "name": f"{country_name} Beneficial Ownership Register",
                "url": "",
                "availability": "To be researched",
                "public_access": False
            }
        },
        "investment_screening": {
            "authority": {
                "name": f"{country_name} Investment Screening Authority",
                "url": "",
                "established": "To be researched",
                "china_relevance": "FDI screening mechanism"
            }
        },
        "research_funding": {
            "agencies": [
                {
                    "name": f"{country_name} National Research Agency",
                    "url": "",
                    "data_types": ["grants", "projects", "collaborations"],
                    "china_relevance": "May fund joint research projects with Chinese partners"
                }
            ]
        },
        "patents": {
            "offices": [
                {
                    "name": f"{country_name} Patent Office",
                    "url": "",
                    "data_types": ["patents", "applications", "classifications"],
                    "api_available": False,
                    "collection_method": "To be determined"
                }
            ]
        },
        "trade_data": {
            "sources": [
                {
                    "name": f"{country_name} Trade Statistics",
                    "url": "",
                    "data_types": ["imports", "exports", "trade_balance"],
                    "china_relevance": "Track bilateral trade dependencies"
                }
            ]
        },
        "treaties": {
            "bilateral_agreements": CHINA_TREATIES.get(country_code, [f"{country_name}-China bilateral relations to be researched"])
        },
        "intelligence_reports": {
            "agencies": [
                {
                    "name": f"{country_name} Intelligence Service",
                    "url": "",
                    "reports_available": False,
                    "china_focus": "To be researched"
                }
            ],
            "think_tanks": []
        },
        "critical_infrastructure": {
            "databases": []
        },
        "supply_chain": {
            "resilience_programs": []
        },
        "strategic_reserves": {
            "authority": f"{country_name} Strategic Reserve (if exists)",
            "url": "",
            "critical_materials": []
        },
        "defense_industrial_base": {
            "authority": f"{country_name} Defense Industrial Base (if exists)",
            "url": "",
            "data_types": []
        },
        "export_controls": {
            "authority": f"{country_name} Export Control Authority",
            "url": "",
            "dual_use_list": "To be researched"
        },
        "national_strategies": {
            "technology_strategies": []
        },
        "research_institutes": {
            "strategic_technology": []
        },
        "notes": f"Basic template for {country_name}. Requires detailed research to populate all fields.",
        "data_quality": "TEMPLATE",
        "last_updated": datetime.now().isoformat(),
        "priority_tier": get_priority_tier(country_code)
    }

    return template


def get_priority_tier(country_code: str) -> str:
    """Get priority tier for a country"""
    for tier_name, countries in PRIORITY_TIERS.items():
        if country_code in countries:
            return tier_name
    return "unclassified"


def main():
    """Main execution"""

    print("="*80)
    print("EXPANDING COUNTRY COVERAGE TO 68 COUNTRIES")
    print("="*80)

    # Load current data
    config_file = Path("C:/Projects/OSINT - Foresight/config/country_specific_data_sources.json")

    with open(config_file, 'r', encoding='utf-8') as f:
        current_data = json.load(f)

    current_countries = set(k for k in current_data.keys() if k != '_TEMPLATE')
    print(f"\nCurrent countries: {len(current_countries)}")

    # Load expanded countries list
    expanded_file = Path("C:/Projects/OSINT - Foresight/config/expanded_countries.json")

    with open(expanded_file, 'r', encoding='utf-8') as f:
        expanded_data = json.load(f)

    # Get all unique countries
    all_countries = set()
    for category in expanded_data['categories'].values():
        all_countries.update(category['countries'])

    # Identify countries to add
    to_add = sorted(list(all_countries - current_countries))

    print(f"Total countries in scope: {len(all_countries)}")
    print(f"Countries to add: {len(to_add)}")
    print(f"\nAdding countries: {to_add}")

    # Add each country
    added_count = 0
    for country_code in to_add:
        if country_code not in current_data:
            print(f"  Adding {country_code} ({COUNTRY_NAMES.get(country_code, country_code)})...")
            current_data[country_code] = create_country_template(country_code)
            added_count += 1

    # Save updated data
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"SUCCESS: Added {added_count} countries")
    print(f"Total countries now: {len([k for k in current_data.keys() if k != '_TEMPLATE'])}")
    print(f"{'='*80}")

    # Summary by tier
    print(f"\nCountries by priority tier:")
    for tier_name, countries in PRIORITY_TIERS.items():
        tier_added = [c for c in countries if c in to_add]
        if tier_added:
            print(f"  {tier_name}: {len(tier_added)} - {tier_added}")


if __name__ == "__main__":
    main()
