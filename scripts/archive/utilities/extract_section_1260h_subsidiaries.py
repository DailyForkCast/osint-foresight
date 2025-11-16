#!/usr/bin/env python3
"""
Extract Subsidiaries from Section 1260H Document

Creates comprehensive subsidiary database from official US DOD Section 1260H list.
"""

import json
from datetime import datetime
from pathlib import Path

# Output path
OUTPUT_PATH = Path("data/section_1260h_subsidiaries.json")

print("="*80)
print("EXTRACTING SECTION 1260H SUBSIDIARIES")
print("="*80)
print()

# Manually extracted from Section 1260H PDF
subsidiaries_data = {
    "metadata": {
        "source": "Section 1260H of the William M. (Mac) Thornberry National Defense Authorization Act for Fiscal Year 2021",
        "source_document": "ENTITIES-IDENTIFIED-AS-CHINESE-MILITARY-COMPANIES-OPERATING-IN-THE-UNITED-STATES.pdf",
        "extraction_date": datetime.now().isoformat(),
        "total_parent_entities": 0,
        "total_subsidiaries": 0
    },
    "entities": {}
}

# AVIC - Aviation Industry Corporation of China (14 subsidiaries)
subsidiaries_data["entities"]["AVIC"] = {
    "entity_id": "SOE-MCF-001",
    "official_name": "Aviation Industry Corporation of China Ltd.",
    "subsidiaries": [
        {"name": "AVIC Aerospace Systems Co., Ltd.", "type": "subsidiary"},
        {"name": "AVIC Airborne Systems Co., Ltd.", "type": "subsidiary", "former_name": "China Avionics Systems Co., Ltd."},
        {"name": "AVIC Asset Management Corporation Ltd.", "type": "subsidiary"},
        {"name": "AVIC Aviation High-Technology Company Limited", "type": "subsidiary", "short_name": "AVIC Aviation Hi-Tech"},
        {"name": "AVIC Electromechanical Systems Co. Ltd.", "type": "subsidiary"},
        {"name": "AVIC Heavy Machinery Company Limited", "type": "subsidiary", "short_name": "AVIC Heavy Machinery"},
        {"name": "AVIC JONHON Optronic Technology Co., Ltd.", "type": "subsidiary", "short_name": "AVIC Jonhon"},
        {"name": "AVIC Shenyang Aircraft Company Limited", "type": "subsidiary", "short_name": "AVIC Shenyang"},
        {"name": "AVIC Xi'an Aircraft Industry Group Company Ltd.", "type": "subsidiary", "short_name": "AVIC Xi'an"},
        {"name": "Changhe Aircraft Industries (Group) Co., Ltd.", "type": "subsidiary"},
        {"name": "Jiangxi Hongdu Aviation Industry Co., Ltd.", "type": "subsidiary", "short_name": "Hongdu Aviation"},
        {"name": "Shenyang Aircraft Design Institute", "type": "subsidiary"},
        {"name": "Xi'an Aircraft Industry Group Co., Ltd.", "type": "subsidiary"},
        {"name": "Zhonghang Electronic Measuring Instruments Company Limited", "type": "subsidiary", "short_name": "ZEMIC"}
    ]
}

# BGI Group (3 subsidiaries)
subsidiaries_data["entities"]["BGI"] = {
    "entity_id": "MCF-PRIVATE-010",
    "official_name": "BGI Group",
    "subsidiaries": [
        {"name": "BGI Genomics Co., Ltd.", "type": "subsidiary", "short_name": "BGI"},
        {"name": "Forensic Genomics International", "type": "subsidiary", "short_name": "FGI"},
        {"name": "MGI Tech Co., Ltd.", "type": "subsidiary", "short_name": "MGI"}
    ]
}

# CASIC - China Aerospace Science and Industry Corporation (5 subsidiaries)
subsidiaries_data["entities"]["CASIC"] = {
    "entity_id": "SOE-MCF-002",
    "official_name": "China Aerospace Science and Industry Corporation Limited",
    "subsidiaries": [
        {"name": "Addsino Co., Ltd.", "type": "subsidiary"},
        {"name": "Aerospace Precision Products Co., Ltd.", "type": "subsidiary"},
        {"name": "Aerosun Corporation", "type": "subsidiary", "short_name": "Aerosun"},
        {"name": "Aisino Corporation", "type": "subsidiary"},
        {"name": "China Aerospace Automotive Co., Ltd.", "type": "subsidiary"}
    ]
}

# CCCG - China Communications Construction Group (6 subsidiaries)
subsidiaries_data["entities"]["CCCG"] = {
    "entity_id": "SOE-MCF-031",
    "official_name": "China Communications Construction Group (Limited)",
    "subsidiaries": [
        {"name": "China Airport Construction Group Corporation", "type": "subsidiary"},
        {"name": "China Communications Construction Company Limited", "type": "subsidiary", "short_name": "CCCC"},
        {"name": "China Communications Constructions USA, Inc.", "type": "us_subsidiary"},
        {"name": "China Traffic Construction USA, Inc.", "type": "us_subsidiary"},
        {"name": "John Holland Group Pty Ltd.", "type": "subsidiary"},
        {"name": "John Holland Services Pty Ltd.", "type": "subsidiary"}
    ]
}

# CEC - China Electronics Corporation (1 subsidiary)
subsidiaries_data["entities"]["CEC"] = {
    "entity_id": "SOE-MCF-011",
    "official_name": "China Electronics Corporation",
    "subsidiaries": [
        {"name": "China International Information Services Ltd.", "type": "subsidiary"}
    ]
}

# CETC - China Electronics Technology Group (8 subsidiaries including Hikvision)
subsidiaries_data["entities"]["CETC"] = {
    "entity_id": "SOE-MCF-010",
    "official_name": "China Electronics Technology Group Corporation",
    "subsidiaries": [
        {"name": "Anhui Sun Create Electronics Co., Ltd.", "type": "subsidiary"},
        {"name": "Cheng Du Westone Information Industry Co., Ltd.", "type": "subsidiary"},
        {"name": "GLARUN Technology Co., Ltd.", "type": "subsidiary"},
        {"name": "Guangzhou GCI Science & Technology Co., Ltd.", "type": "subsidiary"},
        {"name": "Hangzhou Hikvision Digital Technology Co., Ltd.", "type": "subsidiary", "short_name": "Hikvision", "note": "42% stake, separate Section 1260H listing"},
        {"name": "Phoenix Optics Company Limited", "type": "subsidiary"},
        {"name": "Shanghai East China Computer Co., Ltd.", "type": "subsidiary"},
        {"name": "Taiji Computer Co., Ltd.", "type": "subsidiary"}
    ]
}

# China Mobile (2 entities - parent and operating company)
subsidiaries_data["entities"]["China Mobile"] = {
    "entity_id": "SOE-MCF-012",
    "official_name": "China Mobile Communications Group Co., Ltd.",
    "subsidiaries": [
        {"name": "China Mobile Limited", "type": "operating_company", "short_name": "China Mobile"}
    ]
}

# China SpaceSat (2 subsidiaries)
subsidiaries_data["entities"]["China SpaceSat"] = {
    "entity_id": "MCF-SPACE-002",
    "official_name": "China SpaceSat Co., Ltd.",
    "subsidiaries": [
        {"name": "Oriental Blue Sky Titanium Technology Co., Ltd.", "type": "subsidiary"},
        {"name": "Xi'an Aerospace Tianhua Data Technology Co., Ltd.", "type": "subsidiary"}
    ]
}

# China Telecom (1 subsidiary)
subsidiaries_data["entities"]["China Telecom"] = {
    "entity_id": "SOE-MCF-013",
    "official_name": "China Telecom Group Co., Ltd.",
    "subsidiaries": [
        {"name": "China Telecom Corporation Limited", "type": "operating_company"}
    ]
}

# China Unicom (4 subsidiaries)
subsidiaries_data["entities"]["China Unicom"] = {
    "entity_id": "SOE-MCF-014",
    "official_name": "China United Network Communications Group Co., Ltd.",
    "subsidiaries": [
        {"name": "China Unicom (BVI) Co., Ltd.", "type": "subsidiary"},
        {"name": "China Unicom (Hong Kong) Limited", "type": "subsidiary", "short_name": "China Unicom HK"},
        {"name": "China Unicom Group (BVI) Co., Ltd.", "type": "subsidiary"},
        {"name": "China United Network Communications Co., Ltd.", "type": "operating_company"}
    ]
}

# CNCEC - China National Chemical Engineering Group (1 subsidiary)
subsidiaries_data["entities"]["CNCEC"] = {
    "entity_id": "SOE-MCF-051",
    "official_name": "China National Chemical Engineering Group Corporation",
    "subsidiaries": [
        {"name": "China National Chemical Engineering Co., Ltd.", "type": "subsidiary"}
    ]
}

# CNOOC - China National Offshore Oil Corporation (2 subsidiaries)
subsidiaries_data["entities"]["CNOOC"] = {
    "entity_id": "SOE-MCF-050",
    "official_name": "China National Offshore Oil Corporation",
    "subsidiaries": [
        {"name": "CNOOC China Limited", "type": "subsidiary", "short_name": "CNOOC China Ltd."},
        {"name": "CNOOC International Trading Co., Ltd.", "type": "subsidiary", "short_name": "CNOOC International Trading"}
    ]
}

# COMAC - Commercial Aircraft Corporation (3 subsidiaries)
subsidiaries_data["entities"]["COMAC"] = {
    "entity_id": "SOE-MCF-003",
    "official_name": "Commercial Aircraft Corporation of China Limited",
    "subsidiaries": [
        {"name": "Beijing Aeronautical Science & Technology Research Institute", "type": "subsidiary", "short_name": "Beijing Research Center"},
        {"name": "COMAC America Corporation", "type": "us_subsidiary", "short_name": "CAC"},
        {"name": "Shanghai Aircraft Manufacturing Co., Ltd.", "type": "subsidiary", "short_name": "Assembly Manufacturing Center"}
    ]
}

# COSCO SHIPPING (2 subsidiaries)
subsidiaries_data["entities"]["COSCO Shipping"] = {
    "entity_id": "SOE-2016-001",
    "official_name": "China COSCO SHIPPING Corporation Limited",
    "subsidiaries": [
        {"name": "COSCO SHIPPING (North America) Inc.", "type": "us_subsidiary"},
        {"name": "COSCO SHIPPING Finance Co., Ltd.", "type": "subsidiary"}
    ],
    "note": "COSCO has 30+ additional subsidiaries not listed in Section 1260H (OOCL, COSCO Shipping Lines, etc.)"
}

# CSCEC - China State Construction Engineering (1 subsidiary)
subsidiaries_data["entities"]["CSCEC"] = {
    "entity_id": "SOE-MCF-030",
    "official_name": "China State Construction Engineering Corporation Limited",
    "subsidiaries": [
        {"name": "China Construction America, Inc.", "type": "us_subsidiary"}
    ]
}

# CSSC - China State Shipbuilding (3 subsidiaries)
subsidiaries_data["entities"]["CSSC"] = {
    "entity_id": "SOE-MCF-004",
    "official_name": "China State Shipbuilding Corporation Limited",
    "subsidiaries": [
        {"name": "CSSC Offshore & Marine Engineering (Group) Company Limited", "type": "subsidiary", "short_name": "COMEC"},
        {"name": "Guangzhou Wenchong Shipyard Co., Ltd.", "type": "subsidiary"},
        {"name": "Huacheng (Tianjin) Ship Leasing Co., Ltd.", "type": "subsidiary"}
    ]
}

# CSGC - China South Industries Group (2 subsidiaries)
subsidiaries_data["entities"]["CSGC"] = {
    "entity_id": "SOE-MCF-006",
    "official_name": "China South Industries Group Corporation",
    "subsidiaries": [
        {"name": "Costar Group Co., Ltd.", "type": "subsidiary", "short_name": "Costar"},
        {"name": "Heilongjiang Northern Tools Co., Ltd.", "type": "subsidiary"}
    ]
}

# Dahua (1 subsidiary)
subsidiaries_data["entities"]["Dahua"] = {
    "entity_id": "MCF-PRIVATE-005",
    "official_name": "Zhejiang Dahua Technology Co., Ltd.",
    "subsidiaries": [
        {"name": "Chengdu Dahua Wisdom Information Technology Co., Ltd.", "type": "subsidiary"}
    ]
}

# DJI (1 subsidiary)
subsidiaries_data["entities"]["DJI"] = {
    "entity_id": "MCF-PRIVATE-004",
    "official_name": "Shenzhen DJI Innovation Technology Co., Ltd.",
    "subsidiaries": [
        {"name": "Shenzhen Dajiang Baiwang Technology Co., Ltd.", "type": "subsidiary"}
    ]
}

# GTCOM (1 subsidiary)
subsidiaries_data["entities"]["GTCOM"] = {
    "entity_id": "MCF-CYBER-003",
    "official_name": "Global Tone Communication Technology Co., Ltd.",
    "subsidiaries": [
        {"name": "GTCOM Technology Corporation", "type": "us_subsidiary", "short_name": "GTCOM-US"}
    ]
}

# Huawei (1 subsidiary - listed as parent-child relationship)
subsidiaries_data["entities"]["Huawei"] = {
    "entity_id": "MCF-PRIVATE-001",
    "official_name": "Huawei Investment & Holding Co., Ltd.",
    "subsidiaries": [
        {"name": "Huawei Technologies Co., Ltd.", "type": "operating_company", "short_name": "Huawei"}
    ],
    "note": "Huawei has numerous international subsidiaries not listed in Section 1260H"
}

# Norinco (2 subsidiaries)
subsidiaries_data["entities"]["Norinco"] = {
    "entity_id": "SOE-MCF-005",
    "official_name": "China North Industries Group Corporation Limited",
    "subsidiaries": [
        {"name": "Harbin First Machinery Group Ltd.", "type": "subsidiary"},
        {"name": "Inner Mongolia First Machinery Group Co., Ltd.", "type": "subsidiary", "short_name": "Inner Mongolia"}
    ]
}

# SDIC Intelligence (1 subsidiary)
subsidiaries_data["entities"]["SDIC Intelligence"] = {
    "entity_id": "MCF-TECH-022",
    "official_name": "SDIC Intelligence (Xiamen) Information Co., Ltd.",
    "subsidiaries": [
        {"name": "Xiamen Meiya Zhongmin Electronic Technology Co., Ltd.", "type": "subsidiary"}
    ]
}

# SMIC - Semiconductor Manufacturing International (14 subsidiaries!)
subsidiaries_data["entities"]["SMIC"] = {
    "entity_id": "MCF-PRIVATE-002",
    "official_name": "Semiconductor Manufacturing International Corporation",
    "subsidiaries": [
        {"name": "Better Way Enterprises Limited", "type": "subsidiary"},
        {"name": "China IC Capital Co., Ltd.", "type": "subsidiary"},
        {"name": "Magnificent Tower Limited", "type": "subsidiary"},
        {"name": "Semiconductor Manufacturing International (Beijing) Corporation", "type": "subsidiary", "short_name": "SMIC Beijing"},
        {"name": "Semiconductor Manufacturing International (Shenzhen) Corporation", "type": "subsidiary", "short_name": "SMIC Shenzhen"},
        {"name": "Semiconductor Manufacturing International (Tianjin) Corporation", "type": "subsidiary", "short_name": "SMIC Tianjin"},
        {"name": "Semiconductor Manufacturing North China (Beijing) Corporation", "type": "subsidiary"},
        {"name": "Semiconductor Manufacturing South China Corporation", "type": "subsidiary", "short_name": "SMIC South China"},
        {"name": "SilTech Semiconductor Corporation", "type": "subsidiary"},
        {"name": "SMIC Holdings Limited", "type": "subsidiary", "short_name": "SMIC Holdings"},
        {"name": "SMIC Semiconductor Manufacturing (Shanghai) Co., Ltd", "type": "subsidiary", "short_name": "SMIC Shanghai"},
        {"name": "SMIC, Americas", "type": "us_subsidiary"}
    ]
}

# Calculate totals
total_parents = len(subsidiaries_data["entities"])
total_subs = sum(len(entity["subsidiaries"]) for entity in subsidiaries_data["entities"].values())

subsidiaries_data["metadata"]["total_parent_entities"] = total_parents
subsidiaries_data["metadata"]["total_subsidiaries"] = total_subs

print(f"Extracted subsidiaries for {total_parents} parent entities")
print(f"Total subsidiaries: {total_subs}")
print()

# Show breakdown
print("Subsidiary Counts by Parent:")
print("-" * 80)
for parent, data in sorted(subsidiaries_data["entities"].items(), key=lambda x: len(x[1]["subsidiaries"]), reverse=True):
    count = len(data["subsidiaries"])
    print(f"{parent:30} {count:3} subsidiaries")

# Save to file
OUTPUT_PATH.parent.mkdir(exist_ok=True)
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(subsidiaries_data, f, indent=2, ensure_ascii=False)

print()
print("="*80)
print(f"Subsidiary database saved to: {OUTPUT_PATH}")
print("="*80)
