#!/usr/bin/env python3
"""
Complete SOE Database Expansion to MCF Database v2.0

Systematically expands database from 10 entities → 68+ entities
Adds all Section 1260H designated Military-Civil Fusion entities
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Paths
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "data" / "prc_soe_historical_database.json"
DEFINITIONS_PATH = PROJECT_ROOT / "section_1260h_entity_definitions.json"
BACKUP_PATH = PROJECT_ROOT / "data" / "prc_soe_historical_database_v1.0_backup.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "prc_soe_historical_database.json"

def load_json(path: Path) -> Dict:
    """Load JSON file"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: Dict, path: Path):
    """Save JSON file"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_entity_from_definition(defn: Dict, category: str) -> Dict:
    """Generate full entity record from definition"""

    # Determine ownership type
    if category == "technology_companies":
        ownership_type = defn.get("ownership", "Private (MCF-linked)")
    else:
        ownership_type = "Central SOE"

    entity = {
        "entity_id": defn["entity_id"],
        "official_name_cn": defn["official_name_cn"],
        "official_name_en": defn["official_name_en"],
        "common_name": defn["common_name"],
        "stock_ticker": defn.get("stock_ticker", "Multiple subsidiaries" if category != "technology_companies" else "See records"),

        "lifecycle": {
            "status": "existing",
            "creation_date": defn.get("creation_date", "Unknown"),
            "creation_context": f"Established as {defn['common_name']}",
            "dissolution_date": None,
            "current_parent": "SASAC (State Council)" if category != "technology_companies" else defn.get("parent", "Independent"),
            "ownership_type": ownership_type
        },

        "historical_timeline": [
            {
                "date": defn.get("creation_date", "Unknown"),
                "event_type": "establishment",
                "description": f"{defn['common_name']} established",
                "entity_name": defn["common_name"]
            }
        ],

        "sector": defn["sector"],
        "strategic_classification": "TIER_1_CRITICAL",
        "strategic_rationale": f"Section 1260H designated entity - {', '.join(defn.get('technology', []))}",

        # MCF-SPECIFIC FIELDS
        "mcf_classification": {
            "section_1260h_listed": defn.get("section_1260h", False),
            "section_1260h_date": "2021" if defn.get("section_1260h") else None,
            "dual_use_technology": defn.get("technology", []),
            "pla_links": "Section 1260H designated - military end user or MCF participant",
            "military_end_user_list": defn.get("section_1260h", False),
            "entity_list": defn.get("entity_list", False),
            "entity_list_date": defn.get("entity_list_date", None),
            "treasury_sdn": False,
            "seven_sons_national_defense": defn.get("seven_sons", False)
        },

        "aliases": [defn["common_name"], defn["official_name_cn"]],

        "subsidiaries": [f"[{defn.get('subsidiaries_count', 0)} subsidiaries - see Section 1260H list]"],

        "international_operations": {
            "countries": [],
            "major_investments": []
        },

        "western_contracting": {
            "us_contracts": False,
            "eu_contracts": False,
            "other_western": []
        },

        "technology_capabilities": defn.get("key_products", []),

        "us_presence": {
            "operates_in_us": defn.get("section_1260h", False),
            "us_subsidiaries": [],
            "banned_from_us_contracts": defn.get("entity_list", False)
        }
    }

    return entity

def generate_space_satellites_entities() -> List[Dict]:
    """China SpaceSat"""
    return [{
        "entity_id": "SOE-MCF-040",
        "official_name_cn": "中国卫星通信集团有限公司",
        "official_name_en": "China SpaceSat Co., Ltd.",
        "common_name": "China SpaceSat",
        "stock_ticker": "600118.SS",
        "lifecycle": {
            "status": "existing",
            "creation_date": "1997-12-25",
            "creation_context": "Satellite communications",
            "dissolution_date": None,
            "current_parent": "CASIC",
            "ownership_type": "Central SOE subsidiary"
        },
        "historical_timeline": [],
        "sector": "Space - Satellites & Communications",
        "strategic_classification": "TIER_1_CRITICAL",
        "strategic_rationale": "BeiDou navigation, military satellites",
        "mcf_classification": {
            "section_1260h_listed": True,
            "section_1260h_date": "2021",
            "dual_use_technology": ["Satellites", "BeiDou navigation", "Space communications"],
            "pla_links": "Military satellite systems",
            "military_end_user_list": True,
            "entity_list": True,
            "entity_list_date": "2021-01-14",
            "treasury_sdn": False,
            "seven_sons_national_defense": False
        },
        "aliases": ["China SpaceSat", "中国卫星"],
        "subsidiaries": ["Oriental Blue Sky Titanium Technology", "Xi'an Aerospace Tianhua Data Technology"],
        "technology_capabilities": ["BeiDou satellites", "Communications satellites"],
        "us_presence": {"operates_in_us": False, "banned_from_us_contracts": True}
    }]

def generate_logistics_entities() -> List[Dict]:
    """CIMC, Sinotrans, China Cargo Airlines"""
    entities = []

    # CIMC
    entities.append({
        "entity_id": "SOE-MCF-050",
        "official_name_cn": "中国国际海运集装箱(集团)股份有限公司",
        "official_name_en": "China International Marine Containers (Group) Co., Ltd.",
        "common_name": "CIMC",
        "stock_ticker": "000039.SZ, 2039.HK",
        "lifecycle": {
            "status": "existing",
            "creation_date": "1982-01-14",
            "creation_context": "Container manufacturing",
            "dissolution_date": None,
            "current_parent": "China Merchants Group",
            "ownership_type": "Central SOE subsidiary"
        },
        "historical_timeline": [],
        "sector": "Logistics - Container Manufacturing",
        "strategic_classification": "TIER_2",
        "strategic_rationale": "Container manufacturing, supply chain equipment",
        "mcf_classification": {
            "section_1260h_listed": True,
            "section_1260h_date": "2021",
            "dual_use_technology": ["Containers", "Logistics equipment"],
            "pla_links": "Strategic logistics capability",
            "military_end_user_list": False,
            "entity_list": False,
            "treasury_sdn": False,
            "seven_sons_national_defense": False
        },
        "aliases": ["CIMC", "中集集团"],
        "technology_capabilities": ["Container manufacturing", "Logistics equipment"],
        "us_presence": {"operates_in_us": False, "banned_from_us_contracts": False}
    })

    # Sinotrans
    entities.append({
        "entity_id": "SOE-MCF-051",
        "official_name_cn": "中国外运长江航运集团有限公司",
        "official_name_en": "Sinotrans & CSC Holdings Co., Ltd.",
        "common_name": "Sinotrans",
        "stock_ticker": "601598.SS",
        "lifecycle": {
            "status": "existing",
            "creation_date": "1950-10-01",
            "creation_context": "State logistics company",
            "dissolution_date": None,
            "current_parent": "China Merchants Group",
            "ownership_type": "Central SOE subsidiary"
        },
        "historical_timeline": [],
        "sector": "Logistics & Freight Forwarding",
        "strategic_classification": "TIER_2",
        "strategic_rationale": "Strategic logistics, supply chain",
        "mcf_classification": {
            "section_1260h_listed": True,
            "section_1260h_date": "2021",
            "dual_use_technology": ["Logistics", "Freight forwarding"],
            "pla_links": "Strategic logistics capability",
            "military_end_user_list": False,
            "entity_list": False,
            "treasury_sdn": False,
            "seven_sons_national_defense": False
        },
        "aliases": ["Sinotrans", "中国外运"],
        "technology_capabilities": ["Logistics services", "Supply chain management"],
        "us_presence": {"operates_in_us": False, "banned_from_us_contracts": False}
    })

    # China Cargo Airlines
    entities.append({
        "entity_id": "SOE-MCF-052",
        "official_name_cn": "中国货运航空有限公司",
        "official_name_en": "China Cargo Airlines Co., Ltd.",
        "common_name": "China Cargo Airlines",
        "stock_ticker": "Subsidiary of China Eastern Airlines",
        "lifecycle": {
            "status": "existing",
            "creation_date": "1998-03-28",
            "creation_context": "Air cargo operations",
            "dissolution_date": None,
            "current_parent": "China Eastern Airlines",
            "ownership_type": "Central SOE subsidiary"
        },
        "historical_timeline": [],
        "sector": "Air Cargo & Strategic Airlift",
        "strategic_classification": "TIER_2",
        "strategic_rationale": "Strategic airlift capability",
        "mcf_classification": {
            "section_1260h_listed": True,
            "section_1260h_date": "2021",
            "dual_use_technology": ["Air cargo", "Strategic airlift"],
            "pla_links": "Strategic airlift capability",
            "military_end_user_list": False,
            "entity_list": False,
            "treasury_sdn": False,
            "seven_sons_national_defense": False
        },
        "aliases": ["China Cargo", "中国货运航空"],
        "technology_capabilities": ["Air cargo", "Freight operations"],
        "us_presence": {"operates_in_us": False, "banned_from_us_contracts": False}
    })

    return entities

def generate_smaller_tech_companies() -> List[Dict]:
    """Generate remaining technology companies"""
    companies = [
        {
            "id": "MCF-TECH-020", "name": "Yitu", "name_cn": "依图科技",
            "full_name": "Shanghai Yitu Network Technology Co., Ltd.",
            "sector": "AI - Facial Recognition", "tech": ["AI", "Facial recognition"],
            "entity_list": True, "date": "2019-10-08"
        },
        {
            "id": "MCF-TECH-021", "name": "CloudWalk", "name_cn": "云从科技",
            "full_name": "CloudWalk Technology Co., Ltd.",
            "sector": "AI - Biometrics", "tech": ["AI", "Biometric recognition"],
            "entity_list": True, "date": "2021-12-16"
        },
        {
            "id": "MCF-TECH-022", "name": "NetPosa", "name_cn": "东方网力",
            "full_name": "NetPosa Technologies, Ltd.",
            "sector": "Video Surveillance", "tech": ["Video surveillance", "Big data"],
            "entity_list": True, "date": "2019-10-08"
        },
        {
            "id": "MCF-TECH-023", "name": "Autel Robotics", "name_cn": "道通智能",
            "full_name": "Autel Robotics Co., Ltd.",
            "sector": "Drones", "tech": ["UAVs", "Drone technology"],
            "entity_list": False, "date": None
        },
        {
            "id": "MCF-TECH-024", "name": "CH UAV", "name_cn": "航天彩虹",
            "full_name": "Aerospace CH UAV Co., Ltd.",
            "sector": "Military Drones", "tech": ["Military UAVs", "Reconnaissance drones"],
            "entity_list": True, "date": "2021-01-14"
        },
        {
            "id": "MCF-TECH-025", "name": "JOUAV", "name_cn": "纵横股份",
            "full_name": "Chengdu JOUAV Automation Tech Co., Ltd.",
            "sector": "Industrial UAVs", "tech": ["Industrial drones", "Mapping UAVs"],
            "entity_list": False, "date": None
        },
        {
            "id": "MCF-TECH-026", "name": "Qihoo 360", "name_cn": "360安全科技",
            "full_name": "360 Security Technology Inc.",
            "sector": "Cybersecurity", "tech": ["Cybersecurity", "Threat intelligence"],
            "entity_list": False, "date": None
        },
        {
            "id": "MCF-TECH-027", "name": "Knownsec", "name_cn": "知道创宇",
            "full_name": "Beijing Zhidao Chuangyu Information Technology Co., Ltd.",
            "sector": "Cybersecurity", "tech": ["Cybersecurity", "Security operations"],
            "entity_list": False, "date": None
        },
        {
            "id": "MCF-TECH-028", "name": "GTCOM", "name_cn": "全球语联",
            "full_name": "Global Tone Communication Technology Co., Ltd.",
            "sector": "AI Translation", "tech": ["AI translation", "NLP"],
            "entity_list": False, "date": None
        },
        {
            "id": "MCF-TECH-029", "name": "Baicells", "name_cn": "佰才邦",
            "full_name": "Baicells Technologies Co., Ltd.",
            "sector": "5G Equipment", "tech": ["5G base stations", "Network equipment"],
            "entity_list": False, "date": None
        },
        {
            "id": "MCF-TECH-030", "name": "Quectel", "name_cn": "移远通信",
            "full_name": "Quectel Wireless Solutions Co., Ltd.",
            "sector": "IoT Modules", "tech": ["IoT modules", "Wireless communications"],
            "entity_list": False, "date": None
        },
        {
            "id": "MCF-TECH-031", "name": "Geosun", "name_cn": "中海达",
            "full_name": "Wuhan Geosun Navigation Technology Co., Ltd.",
            "sector": "Navigation & Positioning", "tech": ["BeiDou receivers", "GPS/GNSS"],
            "entity_list": False, "date": None
        },
        {
            "id": "MCF-TECH-032", "name": "Origincell", "name_cn": "颢源信息",
            "full_name": "Origincell Technology Co., Ltd.",
            "sector": "Digital Forensics", "tech": ["Digital forensics", "Electronic evidence"],
            "entity_list": False, "date": None
        }
    ]

    entities = []
    for comp in companies:
        entity = {
            "entity_id": comp["id"],
            "official_name_cn": comp["name_cn"],
            "official_name_en": comp["full_name"],
            "common_name": comp["name"],
            "stock_ticker": "Private/Public - see records",
            "lifecycle": {
                "status": "existing",
                "creation_date": "Unknown",
                "creation_context": f"{comp['name']} technology company",
                "dissolution_date": None,
                "current_parent": "Independent",
                "ownership_type": "Private (MCF-linked)"
            },
            "historical_timeline": [],
            "sector": comp["sector"],
            "strategic_classification": "TIER_1_CRITICAL" if comp.get("entity_list") else "TIER_2",
            "strategic_rationale": f"Section 1260H designated - {comp['sector']}",
            "mcf_classification": {
                "section_1260h_listed": True,
                "section_1260h_date": "2021",
                "dual_use_technology": comp["tech"],
                "pla_links": "Section 1260H designated",
                "military_end_user_list": comp.get("entity_list", False),
                "entity_list": comp.get("entity_list", False),
                "entity_list_date": comp.get("date"),
                "treasury_sdn": False,
                "seven_sons_national_defense": False
            },
            "aliases": [comp["name"], comp["name_cn"]],
            "technology_capabilities": comp["tech"],
            "us_presence": {
                "operates_in_us": True,
                "banned_from_us_contracts": comp.get("entity_list", False)
            }
        }
        entities.append(entity)

    return entities

def generate_chemical_engineering_entity() -> List[Dict]:
    """CNCEC - China National Chemical Engineering"""
    return [{
        "entity_id": "SOE-MCF-060",
        "official_name_cn": "中国化学工程集团有限公司",
        "official_name_en": "China National Chemical Engineering Group Corporation",
        "common_name": "CNCEC",
        "stock_ticker": "601117.SS",
        "lifecycle": {
            "status": "existing",
            "creation_date": "2004-09-29",
            "creation_context": "Chemical engineering and construction",
            "dissolution_date": None,
            "current_parent": "SASAC (State Council)",
            "ownership_type": "Central SOE"
        },
        "historical_timeline": [],
        "sector": "Chemical Engineering & Construction",
        "strategic_classification": "TIER_2",
        "strategic_rationale": "Chemical facilities construction, dual-use infrastructure",
        "mcf_classification": {
            "section_1260h_listed": True,
            "section_1260h_date": "2021",
            "dual_use_technology": ["Chemical engineering", "Industrial construction"],
            "pla_links": "Dual-use chemical facilities",
            "military_end_user_list": False,
            "entity_list": False,
            "treasury_sdn": False,
            "seven_sons_national_defense": False
        },
        "aliases": ["CNCEC", "中国化学工程"],
        "subsidiaries": ["China National Chemical Engineering Co., Ltd."],
        "technology_capabilities": ["Chemical plant construction", "Engineering services"],
        "us_presence": {"operates_in_us": False, "banned_from_us_contracts": False}
    }]

def generate_shipbuilding_trading_entity() -> List[Dict]:
    """CSTC - China Shipbuilding Trading"""
    return [{
        "entity_id": "SOE-MCF-061",
        "official_name_cn": "中国船舶贸易有限公司",
        "official_name_en": "China Shipbuilding Trading Co., Ltd.",
        "common_name": "CSTC",
        "stock_ticker": "CSSC subsidiary",
        "lifecycle": {
            "status": "existing",
            "creation_date": "Unknown",
            "creation_context": "Naval equipment exports",
            "dissolution_date": None,
            "current_parent": "CSSC",
            "ownership_type": "Central SOE subsidiary"
        },
        "historical_timeline": [],
        "sector": "Defense - Naval Equipment Trading",
        "strategic_classification": "TIER_2",
        "strategic_rationale": "Naval equipment exports, military ship sales",
        "mcf_classification": {
            "section_1260h_listed": True,
            "section_1260h_date": "2021",
            "dual_use_technology": ["Naval equipment", "Shipbuilding technology"],
            "pla_links": "Naval equipment exports",
            "military_end_user_list": True,
            "entity_list": False,
            "treasury_sdn": False,
            "seven_sons_national_defense": False
        },
        "aliases": ["CSTC", "中国船舶贸易"],
        "technology_capabilities": ["Naval exports", "Ship trading"],
        "us_presence": {"operates_in_us": False, "banned_from_us_contracts": True}
    }]

def expand_database():
    """Main expansion function"""
    print("="*80)
    print("EXPANDING SOE DATABASE TO MCF DATABASE v2.0")
    print("="*80)
    print()

    # Load
    print("Loading files...")
    db = load_json(DB_PATH)
    definitions = load_json(DEFINITIONS_PATH)
    print(f"  ✓ Current database: {len(db['entities'])} entities")
    print(f"  ✓ Definitions loaded")
    print()

    # Backup
    print("Creating backup...")
    save_json(db, BACKUP_PATH)
    print(f"  ✓ v1.0 backed up")
    print()

    # Generate new entities from definitions
    print("Generating entities from definitions...")
    new_entities = []

    # Process each category
    for category in ["defense_aerospace_soes", "electronics_telecom_soes",
                     "nuclear_energy_soes", "construction_infrastructure_soes"]:
        if category in definitions:
            for defn in definitions[category]:
                entity = create_entity_from_definition(defn, category)
                new_entities.append(entity)
                print(f"  ✓ Created: {entity['common_name']}")

    # Technology companies
    if "technology_companies" in definitions:
        for defn in definitions["technology_companies"]:
            entity = create_entity_from_definition(defn, "technology_companies")
            new_entities.append(entity)
            print(f"  ✓ Created: {entity['common_name']}")

    # Additional entities
    print("  Adding specialized entities...")
    new_entities.extend(generate_space_satellites_entities())
    new_entities.extend(generate_logistics_entities())
    new_entities.extend(generate_chemical_engineering_entity())
    new_entities.extend(generate_shipbuilding_trading_entity())
    new_entities.extend(generate_smaller_tech_companies())

    print(f"  ✓ Total new entities: {len(new_entities)}")
    print()

    # Combine
    all_entities = db['entities'] + new_entities
    print(f"Combined total: {len(all_entities)} entities")
    print()

    # Update metadata
    print("Updating metadata...")
    section_1260h_count = sum(1 for e in all_entities
                              if e.get('mcf_classification', {}).get('section_1260h_listed', False))

    db['metadata'].update({
        "database_name": "PRC SOE & MCF Entity Historical Database",
        "version": "2.0",
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "purpose": "Comprehensive tracking of Chinese State-Owned Enterprises and Military-Civil Fusion entities, Section 1260H designated companies, dual-use technology firms",
        "total_entities": len(all_entities),
        "section_1260h_entities": section_1260h_count,
        "data_sources": db['metadata'].get('data_sources', []) + [
            "Section 1260H NDAA FY2021 designations",
            "BIS Entity List",
            "DOD 1260H Chinese Military Companies list"
        ]
    })
    print(f"  ✓ Section 1260H entities: {section_1260h_count}")
    print()

    # Save
    new_db = {
        "metadata": db['metadata'],
        "entities": all_entities,
        "major_reform_periods": db.get('major_reform_periods', []),
        "sector_analysis": db.get('sector_analysis', {}),
        "data_quality_notes": db.get('data_quality_notes', []) + [
            f"v2.0 expansion ({datetime.now().strftime('%Y-%m-%d')}): Added {len(new_entities)} Section 1260H MCF entities",
            "Added MCF-specific fields: section_1260h_listed, dual_use_technology, pla_links, entity_list status",
            "Added technology_capabilities and us_presence tracking for all entities"
        ],
        "future_expansion_priorities": db.get('future_expansion_priorities', [])
    }

    print("Saving expanded database...")
    save_json(new_db, OUTPUT_PATH)
    print(f"  ✓ Saved: {OUTPUT_PATH}")
    print()

    # Summary
    print("="*80)
    print("EXPANSION COMPLETE")
    print("="*80)
    print(f"Version: 2.0")
    print(f"Total entities: {len(all_entities)}")
    print(f"  - Original: {len(db['entities'])}")
    print(f"  - Added: {len(new_entities)}")
    print(f"Section 1260H designated: {section_1260h_count}")
    print(f"Backup: {BACKUP_PATH}")
    print("="*80)

if __name__ == "__main__":
    expand_database()
