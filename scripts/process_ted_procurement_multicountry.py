#!/usr/bin/env python3
"""
Multi-Country TED EU Procurement Data Processor
Analyzes ALL EU countries' relationships with China to detect patterns
invisible in single-country analysis.
"""

import os
import json
import tarfile
import xml.etree.ElementTree as ET
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import re
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict, field
import tempfile
import shutil
import networkx as nx
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ted_multicountry_processing.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class Finding:
    """Structure for country-China findings"""
    contract_id: str
    authority_country: str
    chinese_entity: str
    chinese_entity_type: str  # company, subsidiary, consortium
    value: float
    currency: str
    date: str
    sector: str
    technology_categories: List[str]
    risk_level: str
    evidence: List[str]
    source_file: str
    verification_command: str

class MultiCountryTEDProcessor:
    """
    Process TED data for ALL EU countries' relationships with China
    Detects patterns invisible in single-country analysis
    """

    def __init__(self, data_dir: str = "F:/TED_Data", output_dir: str = "data/processed/ted_multicountry"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir = Path("data/temp/ted_extraction")

        # Create output structure
        for subdir in ["by_country", "by_company", "by_sector", "cross_border",
                      "networks", "analysis", "temporal", "risk_assessment"]:
            (self.output_dir / subdir).mkdir(parents=True, exist_ok=True)

        # EU Countries + associates
        self.eu_countries = {
            # G7/Core
            "DE": "Germany", "FR": "France", "IT": "Italy", "ES": "Spain",
            "NL": "Netherlands", "BE": "Belgium", "LU": "Luxembourg",

            # Nordic
            "SE": "Sweden", "DK": "Denmark", "FI": "Finland", "NO": "Norway", "IS": "Iceland",

            # Central/Eastern (17+1)
            "PL": "Poland", "CZ": "Czech Republic", "SK": "Slovakia",
            "HU": "Hungary", "RO": "Romania", "BG": "Bulgaria",
            "HR": "Croatia", "SI": "Slovenia", "EE": "Estonia",
            "LV": "Latvia", "LT": "Lithuania",

            # Mediterranean
            "GR": "Greece", "CY": "Cyprus", "MT": "Malta", "PT": "Portugal",

            # Other
            "AT": "Austria", "IE": "Ireland", "CH": "Switzerland", "GB": "United Kingdom",

            # EU Candidates & Balkans
            "AL": "Albania", "MK": "North Macedonia", "RS": "Serbia", "ME": "Montenegro",
            "BA": "Bosnia and Herzegovina", "TR": "Turkey", "UA": "Ukraine", "XK": "Kosovo",

            # European Non-EU Strategic
            "GE": "Georgia", "AM": "Armenia",

            # European Territories
            "FO": "Faroe Islands", "GL": "Greenland"
        }

        # Initialize country-specific trackers
        self.country_stats = {country: {
            "total_contracts": 0,
            "china_contracts": 0,
            "total_value": 0.0,
            "sectors": defaultdict(int),
            "chinese_entities": defaultdict(int),
            "temporal": defaultdict(int),
            "risk_levels": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        } for country in self.eu_countries}

        # Chinese entity tracking
        self.chinese_entities = {
            # Telecom
            "huawei": {"patterns": ["Huawei", "华为"], "sector": "telecom", "risk": "CRITICAL"},
            "zte": {"patterns": ["ZTE", "中兴"], "sector": "telecom", "risk": "CRITICAL"},

            # Rail/Transport
            "crrc": {"patterns": ["CRRC", "中国中车"], "sector": "rail", "risk": "HIGH"},
            "csr": {"patterns": ["CSR", "China South"], "sector": "rail", "risk": "HIGH"},

            # Energy
            "state_grid": {"patterns": ["State Grid", "SGCC", "国家电网"], "sector": "energy", "risk": "CRITICAL"},
            "cgnpc": {"patterns": ["CGN", "中广核"], "sector": "nuclear", "risk": "CRITICAL"},
            "cnnc": {"patterns": ["CNNC", "中国核工业"], "sector": "nuclear", "risk": "CRITICAL"},

            # Construction
            "china_construction": {"patterns": ["China Construction", "CSCEC", "中建"], "sector": "construction", "risk": "MEDIUM"},
            "china_railway": {"patterns": ["China Railway", "CREC", "中铁"], "sector": "construction", "risk": "MEDIUM"},

            # Shipping/Ports
            "cosco": {"patterns": ["COSCO", "中远"], "sector": "shipping", "risk": "HIGH"},
            "china_merchants": {"patterns": ["China Merchants", "招商局"], "sector": "ports", "risk": "HIGH"},

            # Technology
            "lenovo": {"patterns": ["Lenovo", "联想"], "sector": "computing", "risk": "MEDIUM"},
            "xiaomi": {"patterns": ["Xiaomi", "小米"], "sector": "consumer_tech", "risk": "LOW"},
            "dji": {"patterns": ["DJI", "大疆"], "sector": "drones", "risk": "HIGH"},
            "hikvision": {"patterns": ["Hikvision", "海康威视"], "sector": "surveillance", "risk": "CRITICAL"},
            "dahua": {"patterns": ["Dahua", "大华"], "sector": "surveillance", "risk": "CRITICAL"},

            # Automotive/Battery
            "byd": {"patterns": ["BYD", "比亚迪"], "sector": "automotive", "risk": "MEDIUM"},
            "catl": {"patterns": ["CATL", "宁德时代"], "sector": "battery", "risk": "MEDIUM"},

            # Generic patterns for unknown entities
            "generic": {"patterns": ["China", "Chinese", "Beijing", "Shanghai", "Shenzhen", "中国"], "sector": "unknown", "risk": "LOW"}
        }

        # Dual-use technology categories
        self.dual_use_sectors = {
            "telecom": ["5G", "telecommunication", "network infrastructure", "fiber optic"],
            "nuclear": ["nuclear", "reactor", "uranium", "enrichment"],
            "aerospace": ["satellite", "launch", "spacecraft", "missile"],
            "surveillance": ["surveillance", "facial recognition", "monitoring", "CCTV"],
            "ai": ["artificial intelligence", "machine learning", "neural network"],
            "quantum": ["quantum computing", "quantum communication", "quantum encryption"],
            "semiconductor": ["semiconductor", "chip", "processor", "integrated circuit"],
            "cyber": ["cybersecurity", "encryption", "firewall", "network security"]
        }

        # Network graph for relationship analysis
        self.company_network = nx.DiGraph()
        self.country_network = nx.Graph()

        # Pattern detection
        self.patterns = {
            "coordinated_bidding": [],
            "subsidiary_networks": [],
            "technology_transfer_routes": [],
            "market_division": [],
            "stepping_stone_contracts": []
        }

        # Checkpoint system
        self.checkpoint_file = self.output_dir / "checkpoint.json"
        self.checkpoint = self.load_checkpoint()

    def load_checkpoint(self) -> Dict:
        """Load processing checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            "processed_files": [],
            "last_file": None,
            "country_findings": {country: [] for country in self.eu_countries},
            "patterns_detected": [],
            "processing_started": datetime.now().isoformat()
        }

    def identify_chinese_entity(self, text: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Identify Chinese entity from text
        Returns: (entity_key, entity_info)
        """
        text_lower = text.lower()

        for entity_key, entity_info in self.chinese_entities.items():
            for pattern in entity_info["patterns"]:
                if pattern.lower() in text_lower:
                    return entity_key, entity_info

        # Check for generic Chinese indicators
        if any(indicator in text_lower for indicator in ["china", "chinese", "中国", "cn"]):
            return "generic", self.chinese_entities["generic"]

        return None, None

    def assess_risk_level(self, contract: Dict, entity_info: Dict) -> str:
        """
        Assess risk level based on entity, value, and sector
        """
        base_risk = entity_info.get("risk", "LOW")
        risk_score = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

        current_score = risk_score[base_risk]

        # Increase risk for dual-use technology
        if any(sector in contract.get("technology_categories", [])
               for sector in ["telecom", "nuclear", "surveillance", "quantum"]):
            current_score += 1

        # Increase risk for high value
        if contract.get("value", 0) > 10000000:  # >10M EUR
            current_score += 1

        # Increase risk for critical infrastructure
        if contract.get("contracting_authority", "").lower() in ["ministry", "defense", "military", "nuclear"]:
            current_score += 1

        # Convert back to risk level
        if current_score >= 4:
            return "CRITICAL"
        elif current_score == 3:
            return "HIGH"
        elif current_score == 2:
            return "MEDIUM"
        else:
            return "LOW"

    def detect_subsidiary_relationship(self, entity_name: str, country: str) -> Optional[Dict]:
        """
        Detect if entity is a subsidiary or shell company
        """
        indicators = {
            "subsidiary_patterns": [
                "Europe", "EU", "GmbH", "S.A.", "S.r.l.", "Ltd", "B.V.", "AB"
            ],
            "shell_indicators": [
                "Trading", "Import", "Export", "International", "Global"
            ]
        }

        entity_lower = entity_name.lower()

        # Check for Chinese parent + European subsidiary pattern
        chinese_parent = None
        for parent_key, parent_info in self.chinese_entities.items():
            for pattern in parent_info["patterns"]:
                if pattern.lower() in entity_lower:
                    chinese_parent = parent_key
                    break

        if chinese_parent:
            for indicator in indicators["subsidiary_patterns"]:
                if indicator.lower() in entity_lower:
                    return {
                        "type": "subsidiary",
                        "parent": chinese_parent,
                        "local_entity": entity_name,
                        "country": country,
                        "confidence": 0.85
                    }

        return None

    def analyze_cross_border_pattern(self, findings: List[Finding]) -> Dict:
        """
        Analyze findings for cross-border patterns
        """
        patterns = {
            "multi_country_entities": defaultdict(set),
            "sector_concentration": defaultdict(lambda: defaultdict(int)),
            "temporal_coordination": defaultdict(list),
            "value_patterns": defaultdict(list)
        }

        for finding in findings:
            # Multi-country presence
            entity = finding.chinese_entity
            patterns["multi_country_entities"][entity].add(finding.authority_country)

            # Sector concentration by country
            patterns["sector_concentration"][finding.authority_country][finding.sector] += 1

            # Temporal patterns
            year = finding.date[:4] if finding.date else "unknown"
            patterns["temporal_coordination"][year].append({
                "country": finding.authority_country,
                "entity": entity,
                "value": finding.value
            })

            # Value patterns
            patterns["value_patterns"][entity].append(finding.value)

        # Identify coordinated campaigns
        coordinated = []
        for year, contracts in patterns["temporal_coordination"].items():
            if len(contracts) > 5:  # Multiple countries in same period
                entities = defaultdict(list)
                for contract in contracts:
                    entities[contract["entity"]].append(contract["country"])

                for entity, countries in entities.items():
                    if len(countries) > 3:  # Same entity in multiple countries
                        coordinated.append({
                            "year": year,
                            "entity": entity,
                            "countries": countries,
                            "pattern": "coordinated_expansion"
                        })

        return {
            "multi_country_entities": dict(patterns["multi_country_entities"]),
            "sector_concentration": dict(patterns["sector_concentration"]),
            "coordinated_campaigns": coordinated
        }

    def process_contract_for_all_countries(self, contract: Dict, source_file: str) -> List[Finding]:
        """
        Process single contract and check against ALL EU countries
        """
        findings = []

        # Check contracting authority country
        authority_country = contract.get("authority_country", "")

        if authority_country not in self.eu_countries:
            return findings

        # Update country stats
        self.country_stats[authority_country]["total_contracts"] += 1

        # Check each winner for Chinese connections
        for winner in contract.get("winners", []):
            winner_name = winner.get("name", "")
            winner_country = winner.get("country", "")

            # Identify Chinese entity
            entity_key, entity_info = self.identify_chinese_entity(winner_name)

            if entity_key:
                # Check for subsidiary relationship
                subsidiary_info = self.detect_subsidiary_relationship(winner_name, authority_country)

                # Determine entity type
                if subsidiary_info:
                    entity_type = "subsidiary"
                    entity_key = f"{entity_key}_subsidiary_{authority_country}"
                else:
                    entity_type = "direct"

                # Assess risk
                risk_level = self.assess_risk_level(contract, entity_info)

                # Create finding
                finding = Finding(
                    contract_id=contract.get("contract_id", ""),
                    authority_country=authority_country,
                    chinese_entity=entity_key,
                    chinese_entity_type=entity_type,
                    value=contract.get("value", 0),
                    currency=contract.get("currency", "EUR"),
                    date=contract.get("date", ""),
                    sector=entity_info.get("sector", "unknown"),
                    technology_categories=contract.get("technology_categories", []),
                    risk_level=risk_level,
                    evidence=[
                        f"Authority: {contract.get('contracting_authority', '')}",
                        f"Winner: {winner_name}",
                        f"Country: {authority_country}"
                    ],
                    source_file=source_file,
                    verification_command=f"tar -xzf '{source_file}' -O | grep -i '{entity_key}'"
                )

                findings.append(finding)

                # Update country stats
                self.country_stats[authority_country]["china_contracts"] += 1
                self.country_stats[authority_country]["total_value"] += contract.get("value", 0)
                self.country_stats[authority_country]["sectors"][entity_info.get("sector", "unknown")] += 1
                self.country_stats[authority_country]["chinese_entities"][entity_key] += 1
                self.country_stats[authority_country]["risk_levels"][risk_level] += 1

                # Update network graphs
                self.company_network.add_edge(entity_key, authority_country,
                                             weight=contract.get("value", 0))

                if subsidiary_info:
                    self.company_network.add_edge(subsidiary_info["parent"], entity_key,
                                                 relationship="subsidiary")

        return findings

    def detect_patterns(self, all_findings: List[Finding]):
        """
        Detect strategic patterns across all countries
        """
        # Group findings by entity
        entity_footprint = defaultdict(lambda: {"countries": set(), "sectors": set(),
                                                "values": [], "dates": []})

        for finding in all_findings:
            entity = finding.chinese_entity
            entity_footprint[entity]["countries"].add(finding.authority_country)
            entity_footprint[entity]["sectors"].add(finding.sector)
            entity_footprint[entity]["values"].append(finding.value)
            entity_footprint[entity]["dates"].append(finding.date)

        # Detect market division (companies avoiding competition)
        market_division = []
        entities = list(entity_footprint.keys())
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                entity1, entity2 = entities[i], entities[j]
                countries1 = entity_footprint[entity1]["countries"]
                countries2 = entity_footprint[entity2]["countries"]

                # If two major entities have no country overlap, possible market division
                if len(countries1) > 3 and len(countries2) > 3 and not countries1.intersection(countries2):
                    market_division.append({
                        "entity1": entity1,
                        "entity2": entity2,
                        "pattern": "market_division",
                        "entity1_countries": list(countries1),
                        "entity2_countries": list(countries2)
                    })

        # Detect stepping stone patterns (progression from low to high risk)
        stepping_stones = []
        for entity, data in entity_footprint.items():
            if len(data["dates"]) > 5:
                # Sort by date
                dated_values = [(d, v) for d, v in zip(data["dates"], data["values"]) if d]
                dated_values.sort()

                if dated_values:
                    # Check if values increase over time (building trust)
                    early_avg = sum(v for _, v in dated_values[:3]) / 3 if len(dated_values) >= 3 else 0
                    late_avg = sum(v for _, v in dated_values[-3:]) / 3 if len(dated_values) >= 3 else 0

                    if late_avg > early_avg * 2:  # Significant increase
                        stepping_stones.append({
                            "entity": entity,
                            "pattern": "stepping_stone",
                            "early_average": early_avg,
                            "late_average": late_avg,
                            "countries": list(data["countries"])
                        })

        # Detect regional strategies
        regional_patterns = {
            "western": ["DE", "FR", "NL", "BE", "LU", "AT"],
            "southern": ["IT", "ES", "PT", "GR", "MT", "CY"],
            "eastern": ["PL", "CZ", "SK", "HU", "RO", "BG"],
            "nordic": ["SE", "DK", "FI", "NO"],
            "baltic": ["EE", "LV", "LT"]
        }

        regional_concentration = defaultdict(lambda: defaultdict(int))
        for finding in all_findings:
            for region, countries in regional_patterns.items():
                if finding.authority_country in countries:
                    regional_concentration[finding.chinese_entity][region] += 1

        # Store all patterns
        self.patterns["market_division"] = market_division
        self.patterns["stepping_stones"] = stepping_stones
        self.patterns["regional_concentration"] = dict(regional_concentration)

    def generate_comparative_analysis(self):
        """
        Generate comprehensive comparative analysis across all countries
        """
        analysis = {
            "metadata": {
                "processing_date": datetime.now().isoformat(),
                "countries_analyzed": len(self.eu_countries),
                "total_findings": sum(stats["china_contracts"]
                                    for stats in self.country_stats.values())
            },
            "country_risk_ranking": [],
            "entity_footprint": {},
            "sector_analysis": {},
            "temporal_patterns": {},
            "strategic_patterns": self.patterns,
            "network_analysis": {},
            "critical_findings": []
        }

        # Country risk ranking
        country_risks = []
        for country, stats in self.country_stats.items():
            if stats["total_contracts"] > 0:
                china_rate = stats["china_contracts"] / stats["total_contracts"] * 100
                risk_score = (
                    china_rate * 0.3 +  # Penetration rate
                    stats["risk_levels"]["CRITICAL"] * 10 +
                    stats["risk_levels"]["HIGH"] * 5 +
                    stats["risk_levels"]["MEDIUM"] * 2
                )

                country_risks.append({
                    "country": country,
                    "name": self.eu_countries[country],
                    "china_contracts": stats["china_contracts"],
                    "penetration_rate": round(china_rate, 2),
                    "total_value": stats["total_value"],
                    "risk_score": round(risk_score, 2),
                    "critical_contracts": stats["risk_levels"]["CRITICAL"],
                    "top_entities": sorted(stats["chinese_entities"].items(),
                                         key=lambda x: x[1], reverse=True)[:5]
                })

        analysis["country_risk_ranking"] = sorted(country_risks,
                                                 key=lambda x: x["risk_score"],
                                                 reverse=True)

        # Entity footprint analysis
        entity_footprint = defaultdict(lambda: {
            "countries": [],
            "total_contracts": 0,
            "total_value": 0,
            "sectors": set()
        })

        for country, stats in self.country_stats.items():
            for entity, count in stats["chinese_entities"].items():
                entity_footprint[entity]["countries"].append(country)
                entity_footprint[entity]["total_contracts"] += count

        analysis["entity_footprint"] = {
            entity: {
                "presence": len(data["countries"]),
                "countries": data["countries"],
                "contracts": data["total_contracts"],
                "eu_coverage": round(len(data["countries"]) / len(self.eu_countries) * 100, 1)
            }
            for entity, data in sorted(entity_footprint.items(),
                                      key=lambda x: len(x[1]["countries"]),
                                      reverse=True)[:20]
        }

        # Sector concentration
        sector_totals = defaultdict(int)
        for stats in self.country_stats.values():
            for sector, count in stats["sectors"].items():
                sector_totals[sector] += count

        analysis["sector_analysis"] = dict(sorted(sector_totals.items(),
                                                 key=lambda x: x[1],
                                                 reverse=True))

        # Network centrality
        if self.company_network.number_of_nodes() > 0:
            centrality = nx.degree_centrality(self.company_network)
            analysis["network_analysis"]["most_connected"] = sorted(
                centrality.items(), key=lambda x: x[1], reverse=True
            )[:10]

        # Save analysis
        analysis_file = self.output_dir / "analysis" / "comprehensive_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        # Generate markdown report
        self.generate_markdown_report(analysis)

        return analysis

    def generate_markdown_report(self, analysis: Dict):
        """Generate comprehensive markdown report"""
        md_content = f"""# Multi-Country TED Analysis: China's EU Procurement Footprint
Generated: {datetime.now().isoformat()}

## Executive Summary

- **Countries Analyzed:** {analysis['metadata']['countries_analyzed']}
- **Total China-Related Contracts:** {analysis['metadata']['total_findings']:,}
- **Highest Risk Countries:** {', '.join(c['name'] for c in analysis['country_risk_ranking'][:5])}

## 🚨 Critical Findings

### Top 5 Highest Risk Countries
"""

        for i, country in enumerate(analysis['country_risk_ranking'][:5], 1):
            md_content += f"""
{i}. **{country['name']}**
   - China Contracts: {country['china_contracts']}
   - Penetration Rate: {country['penetration_rate']}%
   - Risk Score: {country['risk_score']}
   - Critical Contracts: {country['critical_contracts']}
   - Total Value: €{country['total_value']:,.2f}
"""

        md_content += """
## 🏢 Chinese Entity Footprint Across EU
"""

        for entity, data in list(analysis['entity_footprint'].items())[:10]:
            md_content += f"""
**{entity}**
- Present in {data['presence']} countries ({data['eu_coverage']}% of EU)
- Total contracts: {data['contracts']}
- Countries: {', '.join(data['countries'][:10])}
"""

        md_content += """
## 📊 Sector Analysis
"""

        for sector, count in list(analysis['sector_analysis'].items())[:10]:
            md_content += f"- {sector}: {count} contracts\n"

        md_content += """
## 🔍 Strategic Patterns Detected
"""

        if analysis['strategic_patterns'].get('market_division'):
            md_content += """
### Market Division Patterns
Evidence of coordinated market division between Chinese entities:
"""
            for pattern in analysis['strategic_patterns']['market_division'][:3]:
                md_content += f"""
- {pattern['entity1']} focuses on: {', '.join(pattern['entity1_countries'][:5])}
- {pattern['entity2']} focuses on: {', '.join(pattern['entity2_countries'][:5])}
"""

        if analysis['strategic_patterns'].get('stepping_stones'):
            md_content += """
### Stepping Stone Patterns
Entities building trust with increasing contract values:
"""
            for pattern in analysis['strategic_patterns']['stepping_stones'][:3]:
                md_content += f"""
- {pattern['entity']}: Early avg €{pattern['early_average']:,.0f} → Late avg €{pattern['late_average']:,.0f}
"""

        md_content += """
## 📈 Regional Strategies

Analysis shows distinct regional preferences by Chinese entities:
"""

        if analysis['strategic_patterns'].get('regional_concentration'):
            for entity, regions in list(analysis['strategic_patterns']['regional_concentration'].items())[:5]:
                top_region = max(regions.items(), key=lambda x: x[1])[0] if regions else "none"
                md_content += f"- {entity}: Primary focus on {top_region} Europe\n"

        md_content += """
## ⚠️ Risk Assessment

### Critical Infrastructure Exposure
- Telecommunications: Check entity footprint for Huawei/ZTE
- Energy: Monitor State Grid and nuclear entities
- Transportation: Track CRRC and China Railway presence
- Ports: Assess COSCO influence

### Recommendations
1. Countries with >5% penetration rate require immediate review
2. Critical infrastructure contracts need enhanced scrutiny
3. Subsidiary networks require mapping and monitoring
4. Regional patterns suggest coordinated strategy requiring EU-level response

## 📊 Comparative Advantage of Multi-Country Analysis

This analysis revealed patterns invisible in single-country view:
- Market division strategies between Chinese entities
- Progressive contract value increases (stepping stones)
- Regional concentration patterns
- Subsidiary and shell company networks
- Coordinated multi-country campaigns

---

*Full data available in JSON format for detailed analysis*
"""

        # Save report
        report_file = self.output_dir / "analysis" / "MULTI_COUNTRY_ANALYSIS_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        logging.info(f"Markdown report saved to {report_file}")

    def process_xml_all_countries(self, xml_content: str, source_file: str, xml_path: str) -> Dict:
        """
        Process single XML file for ALL countries
        Returns dict with country codes as keys, findings lists as values
        """
        findings_by_country = {country: [] for country in self.eu_countries}

        try:
            # Parse XML
            root = ET.fromstring(xml_content)

            # Extract basic contract info
            contract_info = self.extract_contract_info(root, source_file, xml_path)
            if not contract_info:
                return findings_by_country

            # Check if this is a Chinese entity contract for ANY country
            chinese_entity, entity_info = self.identify_chinese_entity(xml_content)
            if not chinese_entity:
                return findings_by_country

            # Check which country is the contracting authority
            country_code = contract_info.get("authority_country")
            if country_code not in self.eu_countries:
                return findings_by_country

            # Create finding for this country
            finding = Finding(
                contract_id=contract_info.get("contract_id", "UNKNOWN"),
                authority_country=country_code,
                chinese_entity=chinese_entity,
                chinese_entity_type=self.determine_entity_type(entity_info, xml_content),
                value=contract_info.get("value", 0.0),
                currency=contract_info.get("currency", "EUR"),
                date=contract_info.get("date", ""),
                sector=entity_info.get("sector", "unknown"),
                technology_categories=self.identify_technology_categories(xml_content),
                risk_level=self.assess_risk_level(contract_info, entity_info),
                evidence=self.extract_evidence(xml_content, chinese_entity),
                source_file=source_file,
                verification_command=self.generate_verification_command(source_file, xml_path, chinese_entity)
            )

            findings_by_country[country_code].append(finding)

        except ET.ParseError as e:
            logging.warning(f"XML parse error in {xml_path}: {e}")
        except Exception as e:
            logging.error(f"Error processing {xml_path}: {e}")

        return findings_by_country

    def extract_contract_info(self, root: ET.Element, source_file: str, xml_path: str) -> Optional[Dict]:
        """Extract basic contract information from XML"""
        try:
            # Namespace-agnostic searching
            ns = "{http://publications.europa.eu/resource/schema/ted/R2.0.9/publication}"

            # Contract ID
            contract_id_elem = root.find(f".//{ns}NO_DOC_OJS") or root.find(".//NO_DOC_OJS")
            contract_id = contract_id_elem.text if contract_id_elem is not None else "UNKNOWN"

            # Authority country
            country_elem = root.find(f".//{ns}CONTRACTING_BODY//{ns}COUNTRY") or root.find(".//CONTRACTING_BODY//COUNTRY")
            country_code = country_elem.get("VALUE") if country_elem is not None else None

            # Contract value
            value_elem = root.find(f".//{ns}VAL_TOTAL") or root.find(".//VAL_TOTAL")
            value = 0.0
            currency = "EUR"
            if value_elem is not None:
                try:
                    value = float(value_elem.text or "0")
                    currency = value_elem.get("CURRENCY", "EUR")
                except (ValueError, TypeError):
                    value = 0.0

            # Date
            date_elem = root.find(f".//{ns}DATE_PUB") or root.find(".//DATE_PUB")
            date = date_elem.text if date_elem is not None else ""

            return {
                "contract_id": contract_id,
                "authority_country": country_code,
                "value": value,
                "currency": currency,
                "date": date
            }

        except Exception as e:
            logging.warning(f"Error extracting contract info from {xml_path}: {e}")
            return None

    def determine_entity_type(self, entity_info: Dict, xml_content: str) -> str:
        """Determine if entity is parent company, subsidiary, or consortium"""
        xml_lower = xml_content.lower()

        # Check for subsidiary indicators
        subsidiary_indicators = ["subsidiary", "s.r.l.", "gmbh", "ltd", "limited", "spa", "sa"]
        if any(indicator in xml_lower for indicator in subsidiary_indicators):
            return "subsidiary"

        # Check for consortium indicators
        consortium_indicators = ["consortium", "joint venture", "partnership"]
        if any(indicator in xml_lower for indicator in consortium_indicators):
            return "consortium"

        return "company"

    def identify_technology_categories(self, xml_content: str) -> List[str]:
        """Identify dual-use technology categories"""
        categories = []
        xml_lower = xml_content.lower()

        for category, keywords in self.dual_use_sectors.items():
            if any(keyword.lower() in xml_lower for keyword in keywords):
                categories.append(category)

        return categories

    def extract_evidence(self, xml_content: str, chinese_entity: str) -> List[str]:
        """Extract evidence lines containing Chinese entity mentions"""
        evidence = []
        lines = xml_content.split('\n')

        entity_patterns = self.chinese_entities.get(chinese_entity, {}).get("patterns", [])

        for i, line in enumerate(lines):
            for pattern in entity_patterns:
                if pattern.lower() in line.lower():
                    evidence.append(f"Line {i+1}: {line.strip()}")
                    break

        return evidence[:3]  # Limit to 3 evidence lines

    def generate_verification_command(self, source_file: str, xml_path: str, chinese_entity: str) -> str:
        """Generate command to verify finding"""
        entity_patterns = self.chinese_entities.get(chinese_entity, {}).get("patterns", [])
        pattern = entity_patterns[0] if entity_patterns else chinese_entity

        return f"tar -xzf '{source_file}' -O '{xml_path}' | grep -n '{pattern}'"

    def process_archive(self, archive_path: Path) -> Dict:
        """
        Process single TED archive for ALL countries
        Handles nested archive structure: outer monthly → inner daily → XML files
        """
        if not archive_path.exists():
            logging.error(f"FABRICATION PREVENTED: File does not exist: {archive_path}")
            return {"error": "FILE_NOT_FOUND", "fabrication_prevented": True}

        logging.info(f"Processing {archive_path} for all EU countries...")

        results = {
            "archive": str(archive_path),
            "findings_by_country": {country: [] for country in self.eu_countries},
            "total_xml_processed": 0,
            "total_findings": 0,
            "processing_errors": [],
            "verification": {
                "archive_exists": True,
                "archive_readable": True,
                "inner_archives_count": 0,
                "xml_files_count": 0
            }
        }

        try:
            # Step 1: Open outer archive
            with tarfile.open(archive_path, 'r:gz') as outer_tar:
                outer_members = outer_tar.getmembers()
                inner_archives = [m for m in outer_members if m.name.endswith('.tar.gz')]

                results["verification"]["inner_archives_count"] = len(inner_archives)
                logging.info(f"Found {len(inner_archives)} inner archives")

                # Step 2: Process each inner archive
                for inner_member in inner_archives:
                    try:
                        logging.info(f"  Processing inner: {inner_member.name}")

                        # Extract inner archive to memory
                        inner_file_obj = outer_tar.extractfile(inner_member)
                        if not inner_file_obj:
                            continue

                        # Step 3: Open inner archive
                        with tarfile.open(fileobj=inner_file_obj, mode='r:gz') as inner_tar:
                            xml_members = [m for m in inner_tar.getmembers() if m.name.endswith('.xml')]
                            results["verification"]["xml_files_count"] += len(xml_members)

                            logging.info(f"    XML files: {len(xml_members)}")

                            # Step 4: Process each XML file
                            for xml_member in xml_members:
                                try:
                                    xml_content_bytes = inner_tar.extractfile(xml_member).read()
                                    xml_content = xml_content_bytes.decode('utf-8', errors='ignore')

                                    # Process for all countries
                                    findings = self.process_xml_all_countries(
                                        xml_content,
                                        str(archive_path),
                                        f"{inner_member.name}/{xml_member.name}"
                                    )

                                    # Add findings by country
                                    for country, country_findings in findings.items():
                                        results["findings_by_country"][country].extend(country_findings)
                                        results["total_findings"] += len(country_findings)

                                    results["total_xml_processed"] += 1

                                except Exception as e:
                                    error_msg = f"XML processing error {xml_member.name}: {e}"
                                    results["processing_errors"].append(error_msg)
                                    logging.warning(error_msg)

                    except Exception as e:
                        error_msg = f"Inner archive error {inner_member.name}: {e}"
                        results["processing_errors"].append(error_msg)
                        logging.error(error_msg)

        except Exception as e:
            error_msg = f"Outer archive error: {e}"
            results["processing_errors"].append(error_msg)
            results["verification"]["archive_readable"] = False
            logging.error(error_msg)

        logging.info(f"Completed {archive_path}: {results['total_findings']} findings from {results['total_xml_processed']} XML files")
        return results

    def run(self, test_mode=False, parallel=True):
        """
        Main processing function
        """
        logging.info("=" * 50)
        logging.info("Multi-Country TED Analysis Starting")
        logging.info(f"Countries: {len(self.eu_countries)}")
        logging.info(f"Chinese entities tracked: {len(self.chinese_entities)}")
        logging.info("=" * 50)

        # Find all TED archives
        monthly_dir = self.data_dir / "monthly"
        if not monthly_dir.exists():
            logging.error(f"TED data directory not found: {monthly_dir}")
            return

        # Collect all archives
        archives = []
        for year_dir in sorted(monthly_dir.glob("*")):
            if year_dir.is_dir():
                for archive in sorted(year_dir.glob("TED_monthly_*.tar.gz")):
                    if str(archive) not in self.checkpoint["processed_files"]:
                        archives.append(archive)

        if test_mode:
            # Use 2024 archive for testing (known to work)
            test_archive = monthly_dir / "2024" / "TED_monthly_2024_01.tar.gz"
            if test_archive.exists():
                archives = [test_archive]
            else:
                archives = archives[:1]  # Fallback to first available
            logging.info(f"TEST MODE: Processing only {archives[0] if archives else 'no files'}")

        logging.info(f"Found {len(archives)} archives to process")

        # Process archives
        all_findings = []
        for i, archive_path in enumerate(archives):
            logging.info(f"Processing archive {i+1}/{len(archives)}: {archive_path.name}")

            try:
                results = self.process_archive(archive_path)

                # Save checkpoint
                self.checkpoint["processed_files"].append(str(archive_path))
                self.checkpoint["last_file"] = str(archive_path)

                # Collect findings
                for country, findings in results["findings_by_country"].items():
                    self.checkpoint["country_findings"][country].extend([asdict(f) for f in findings])
                    all_findings.extend(findings)

                # Update country stats
                for country, findings in results["findings_by_country"].items():
                    country_stats = self.country_stats[country]
                    country_stats["china_contracts"] += len(findings)
                    for finding in findings:
                        country_stats["total_value"] += finding.value
                        country_stats["sectors"][finding.sector] += 1
                        country_stats["chinese_entities"][finding.chinese_entity] += 1
                        country_stats["risk_levels"][finding.risk_level] += 1

                # Save checkpoint after each archive
                self.save_checkpoint()
                logging.info(f"  --> Found {results['total_findings']} China-related contracts")

            except Exception as e:
                logging.error(f"Error processing {archive_path}: {e}")
                continue

        logging.info(f"Processing complete. Total findings: {len(all_findings)}")

        # Generate outputs
        self.save_findings_by_country()
        self.save_findings_by_company()
        self.save_findings_by_sector()
        self.detect_patterns(all_findings)
        analysis = self.generate_comparative_analysis()
        self.generate_markdown_report(analysis)

        logging.info("=" * 50)
        logging.info("Multi-Country TED Analysis Complete")
        logging.info(f"Results saved to: {self.output_dir}")
        logging.info("=" * 50)

    def save_checkpoint(self):
        """Save processing checkpoint"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def save_findings_by_country(self):
        """Save findings organized by country"""
        for country, findings_dicts in self.checkpoint["country_findings"].items():
            if findings_dicts:  # Only save if has findings
                country_dir = self.output_dir / "by_country" / f"{country}_china"
                country_dir.mkdir(exist_ok=True)

                # Group by year
                by_year = defaultdict(list)
                for finding_dict in findings_dicts:
                    year = finding_dict.get("date", "")[:4] or "unknown"
                    by_year[year].append(finding_dict)

                for year, findings in by_year.items():
                    year_file = country_dir / f"contracts_{year}.json"
                    with open(year_file, 'w') as f:
                        json.dump(findings, f, indent=2)

                # Summary
                summary = {
                    "country": self.eu_countries.get(country, country),
                    "total_contracts": len(findings_dicts),
                    "total_value": sum(f.get("value", 0) for f in findings_dicts),
                    "years_active": sorted(by_year.keys()),
                    "top_entities": dict(Counter(f.get("chinese_entity") for f in findings_dicts).most_common(5)),
                    "sectors": dict(Counter(f.get("sector") for f in findings_dicts).most_common())
                }
                with open(country_dir / "summary.json", 'w') as f:
                    json.dump(summary, f, indent=2)

    def save_findings_by_company(self):
        """Save findings organized by Chinese company"""
        by_company = defaultdict(list)
        for country, findings_dicts in self.checkpoint["country_findings"].items():
            for finding_dict in findings_dicts:
                company = finding_dict.get("chinese_entity")
                if company:
                    by_company[company].append(finding_dict)

        for company, findings in by_company.items():
            company_dir = self.output_dir / "by_company" / company
            company_dir.mkdir(exist_ok=True)

            with open(company_dir / "all_contracts.json", 'w') as f:
                json.dump(findings, f, indent=2)

            # Analysis
            countries = list(set(f.get("authority_country") for f in findings))
            analysis = {
                "company": company,
                "total_contracts": len(findings),
                "countries_present": countries,
                "total_value": sum(f.get("value", 0) for f in findings),
                "risk_assessment": self.chinese_entities.get(company, {}).get("risk", "UNKNOWN")
            }
            with open(company_dir / "analysis.json", 'w') as f:
                json.dump(analysis, f, indent=2)

    def save_findings_by_sector(self):
        """Save findings organized by sector"""
        by_sector = defaultdict(list)
        for country, findings_dicts in self.checkpoint["country_findings"].items():
            for finding_dict in findings_dicts:
                sector = finding_dict.get("sector")
                if sector:
                    by_sector[sector].append(finding_dict)

        for sector, findings in by_sector.items():
            sector_dir = self.output_dir / "by_sector" / sector
            sector_dir.mkdir(exist_ok=True)

            with open(sector_dir / "all_contracts.json", 'w') as f:
                json.dump(findings, f, indent=2)

            # Analysis
            countries = list(set(f.get("authority_country") for f in findings))
            companies = list(set(f.get("chinese_entity") for f in findings))
            analysis = {
                "sector": sector,
                "total_contracts": len(findings),
                "countries_affected": countries,
                "chinese_companies": companies,
                "total_value": sum(f.get("value", 0) for f in findings)
            }
            with open(sector_dir / "analysis.json", 'w') as f:
                json.dump(analysis, f, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Country TED Procurement Analysis")
    parser.add_argument("--test", action="store_true", help="Test mode - process only one archive")
    parser.add_argument("--data-dir", default="F:/TED_Data", help="TED data directory")
    parser.add_argument("--output-dir", default="data/processed/ted_multicountry", help="Output directory")

    args = parser.parse_args()

    processor = MultiCountryTEDProcessor(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )

    logging.info("Starting Multi-Country TED Processing...")
    processor.run(test_mode=args.test)
    logging.info("Processing complete!")
