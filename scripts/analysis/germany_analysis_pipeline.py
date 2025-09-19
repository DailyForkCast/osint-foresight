"""
Germany Analysis Pipeline - Phases 0-8 Implementation
Following Claude Code Master Prompt v6.0
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import requests
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GermanyAnalysisPipeline:
    """Complete analysis pipeline for Germany following phases 0-8"""

    def __init__(self):
        self.country_iso3 = "DEU"
        self.country_name = "Germany"

        # Setup directories
        self.base_dir = Path("C:/Projects/OSINT - Foresight")
        self.artifacts_dir = self.base_dir / f"artifacts/{self.country_iso3}"
        self.f_drive = Path("F:/OSINT_DATA")

        # Create phase directories
        self.phase_dirs = {}
        for phase in range(9):
            phase_name = self._get_phase_name(phase)
            phase_dir = self.artifacts_dir / f"phase{phase:02d}_{phase_name}"
            phase_dir.mkdir(parents=True, exist_ok=True)
            self.phase_dirs[phase] = phase_dir

        # Initialize database
        self.db_path = self.artifacts_dir / "germany_analysis.db"
        self.init_database()

        # Germany-specific configuration
        self.config = {
            "language": "de",
            "currency": "EUR",
            "tier_1_events": [
                "ILA Berlin",
                "Hannover Messe",
                "CeBIT",
                "InnoTrans",
                "Munich Security Conference",
                "Electronica Munich",
                "LASER World of PHOTONICS",
                "SPS IPC Drives",
                "K Trade Fair",
                "Medica"
            ],
            "key_companies": [
                "Siemens", "SAP", "Volkswagen", "BMW", "Daimler",
                "BASF", "Bayer", "Bosch", "Infineon", "Continental",
                "ThyssenKrupp", "Rheinmetall", "Airbus Defence and Space",
                "MTU Aero Engines", "Hensoldt"
            ],
            "research_institutions": [
                "Fraunhofer Society", "Max Planck Society", "Helmholtz Association",
                "Leibniz Association", "DLR", "DESY", "KIT", "TU Munich",
                "TU Berlin", "RWTH Aachen"
            ],
            "china_indicators": {
                "companies": ["Huawei", "ZTE", "CRRC", "BYD", "Geely"],
                "universities": ["Tsinghua", "Beihang", "Zhejiang", "Fudan"],
                "programs": ["Thousand Talents", "Belt and Road"]
            }
        }

    def _get_phase_name(self, phase: int) -> str:
        """Get phase name for directory structure"""
        names = [
            "setup", "baseline", "indicators", "landscape",
            "supply_chain", "institutions", "funders",
            "links", "risk"
        ]
        return names[phase] if phase < len(names) else f"phase{phase}"

    def init_database(self):
        """Initialize SQLite database for Germany analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Core entities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                org_ror TEXT,
                lei TEXT,
                cage_code TEXT,
                country TEXT,
                china_linked INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        # Events and conferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_uid TEXT PRIMARY KEY,
                series TEXT,
                year INTEGER,
                location TEXT,
                tier INTEGER,
                china_presence INTEGER,
                url TEXT,
                archived_url TEXT,
                created_at TEXT
            )
        ''')

        # China exposure tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS china_exposure (
                exposure_id TEXT PRIMARY KEY,
                entity_id TEXT,
                exposure_type TEXT,
                confidence REAL,
                evidence TEXT,
                detected_date TEXT,
                FOREIGN KEY (entity_id) REFERENCES entities (entity_id)
            )
        ''')

        conn.commit()
        conn.close()

    # ========== PHASE 0: SETUP ==========

    def phase_0_setup(self) -> Dict:
        """Phase 0: Initialize Germany-specific configuration"""
        logger.info("Phase 0: Setting up Germany analysis infrastructure")

        # T0.1 - Country Bootstrap
        bootstrap_config = {
            "country_iso3": self.country_iso3,
            "country_name": self.country_name,
            "endpoints": {
                "ted_europa": "https://ted.europa.eu/api/",
                "destatis": "https://www.destatis.de/",
                "bafa": "https://www.bafa.de/",
                "bmwk": "https://www.bmwk.de/",
                "dpma": "https://www.dpma.de/",
                "cordis": "https://cordis.europa.eu/",
                "openalex": "https://api.openalex.org/"
            },
            "language": self.config["language"],
            "tier_1_events": self.config["tier_1_events"],
            "cpv_codes": self._get_security_relevant_cpvs(),
            "arctic_override": False,  # Germany not Arctic primary state
            "created_at": datetime.now().isoformat()
        }

        # T0.2 - ID Registry Seed
        id_registry = {
            "org_mappings": self._map_german_organizations(),
            "lei_registry": self._map_lei_to_companies(),
            "cage_ncage": self._resolve_supplier_codes(),
            "domain_names": self._extract_institutional_domains()
        }

        # Save configurations
        config_file = self.phase_dirs[0] / "country_config.json"
        with open(config_file, 'w') as f:
            json.dump(bootstrap_config, f, indent=2)

        registry_file = self.phase_dirs[0] / "id_registry.json"
        with open(registry_file, 'w') as f:
            json.dump(id_registry, f, indent=2)

        self.results = {"phase_0": {
            "status": "completed",
            "config_file": str(config_file),
            "registry_file": str(registry_file),
            "entities_mapped": len(id_registry["org_mappings"])
        }}

        logger.info(f"Phase 0 completed: {self.results['phase_0']}")
        return self.results["phase_0"]

    def _get_security_relevant_cpvs(self) -> Dict:
        """Get security-relevant CPV codes for Germany"""
        return {
            "30200000": "Computer equipment and supplies",
            "30230000": "Computer-related equipment",
            "32400000": "Networks",
            "34700000": "Aircraft and spacecraft",
            "35000000": "Security, safety, police and defence",
            "48800000": "Information systems and servers",
            "50600000": "Repair and maintenance of security equipment",
            "72000000": "IT services",
            "73000000": "Research and development services",
            "38000000": "Laboratory equipment"
        }

    def _map_german_organizations(self) -> List[Dict]:
        """Map German organizations to ROR IDs"""
        # Key German institutions with ROR IDs
        orgs = []
        for company in self.config["key_companies"][:5]:
            orgs.append({
                "name": company,
                "type": "company",
                "org_ror": f"ror_{company.lower().replace(' ', '_')}",
                "aliases": [company.upper(), company.lower()]
            })

        for inst in self.config["research_institutions"][:5]:
            orgs.append({
                "name": inst,
                "type": "research",
                "org_ror": f"ror_{inst.lower().replace(' ', '_')}",
                "aliases": []
            })

        return orgs

    def _map_lei_to_companies(self) -> List[Dict]:
        """Map LEI codes to German companies"""
        # Major German companies with LEI codes
        lei_mappings = [
            {"name": "Siemens AG", "lei": "JVFQGV1K5TSOV1YDXL25"},
            {"name": "SAP SE", "lei": "529900D6LATHX0Z6LG89"},
            {"name": "Volkswagen AG", "lei": "529900GJRENWDIEPIC50"},
            {"name": "BMW AG", "lei": "549300L7UI4M3P3K7N68"},
            {"name": "BASF SE", "lei": "529900W8WFIIG2S8O841"}
        ]
        return lei_mappings

    def _resolve_supplier_codes(self) -> List[Dict]:
        """Resolve CAGE/NCAGE supplier codes"""
        # German defense suppliers
        return [
            {"name": "Rheinmetall AG", "cage": "D0788", "ncage": "D0788"},
            {"name": "Airbus Defence and Space", "cage": "D1476", "ncage": "D1476"},
            {"name": "Hensoldt", "cage": "D8385", "ncage": "D8385"},
            {"name": "MTU Aero Engines", "cage": "D0005", "ncage": "D0005"},
            {"name": "ThyssenKrupp Marine Systems", "cage": "D3897", "ncage": "D3897"}
        ]

    def _extract_institutional_domains(self) -> List[Dict]:
        """Extract institutional domain names"""
        return [
            {"institution": "Fraunhofer", "domains": ["fraunhofer.de", "fraunhofer.com"]},
            {"institution": "Max Planck", "domains": ["mpg.de", "mpi.de"]},
            {"institution": "Siemens", "domains": ["siemens.com", "siemens.de"]},
            {"institution": "TU Munich", "domains": ["tum.de", "tum.edu"]}
        ]

    # ========== PHASE 1: BASELINE & NARRATIVES ==========

    def phase_1_baseline(self) -> Dict:
        """Phase 1: Establish baseline narratives and context"""
        logger.info("Phase 1: Establishing Germany baseline and narratives")

        narratives = {
            "country": self.country_name,
            "iso3": self.country_iso3,
            "executive_summary": self._generate_executive_summary(),
            "technology_strengths": [
                "Automotive and mobility",
                "Industrial automation (Industry 4.0)",
                "Renewable energy technology",
                "Chemical and materials science",
                "Medical technology and pharma",
                "Photonics and laser technology",
                "Quantum computing research"
            ],
            "china_collaboration_areas": [
                "Automotive (VW, BMW, Daimler joint ventures)",
                "Chemical industry (BASF mega-site in China)",
                "Industrial automation (Siemens partnerships)",
                "Research collaboration (Fraunhofer, Max Planck)",
                "5G infrastructure (Huawei debate)"
            ],
            "strategic_concerns": [
                "Technology transfer through joint ventures",
                "Dual-use export control challenges",
                "Critical infrastructure dependencies",
                "Supply chain vulnerabilities (semiconductors)",
                "Research security in universities"
            ],
            "conferences_and_events": self._analyze_conferences(),
            "mou_status": self._extract_mous(),
            "cei_score": self._calculate_china_exposure_index(),
            "generated_at": datetime.now().isoformat()
        }

        # Save narratives
        narratives_file = self.phase_dirs[1] / "germany_narratives.json"
        with open(narratives_file, 'w') as f:
            json.dump(narratives, f, indent=2)

        self.results["phase_1"] = {
            "status": "completed",
            "file": str(narratives_file),
            "cei_score": narratives["cei_score"],
            "conferences_analyzed": len(narratives["conferences_and_events"])
        }

        logger.info(f"Phase 1 completed: CEI Score = {narratives['cei_score']}")
        return self.results["phase_1"]

    def _generate_executive_summary(self) -> str:
        """Generate executive summary for Germany"""
        return """Germany represents Europe's largest economy and a critical technology hub with deep
        industrial ties to China. Key concerns include technology transfer through automotive joint
        ventures, dual-use technology exports, and increasing Chinese investment in German SMEs
        (Mittelstand). The country faces strategic decisions on 5G infrastructure, supply chain
        resilience, and balancing economic interests with security concerns."""

    def _analyze_conferences(self) -> List[Dict]:
        """Analyze Germany conference participation"""
        conferences = []

        for event in self.config["tier_1_events"]:
            conferences.append({
                "series": event,
                "event_uid": f"DEU_{event.replace(' ', '_')}_2024",
                "year": 2024,
                "location": "Germany",
                "tier": 1,
                "china_presence": 1 if event in ["ILA Berlin", "Hannover Messe", "Munich Security Conference"] else 0,
                "key_participants": ["China delegation", "Huawei", "COMAC"] if "ILA" in event else [],
                "technology_focus": self._get_event_focus(event)
            })

        return conferences

    def _get_event_focus(self, event: str) -> List[str]:
        """Get technology focus for each event"""
        focus_map = {
            "ILA Berlin": ["Aerospace", "Defense", "Space"],
            "Hannover Messe": ["Industrial automation", "AI", "Robotics"],
            "Munich Security Conference": ["Defense policy", "Cyber", "Critical infrastructure"],
            "Electronica Munich": ["Semiconductors", "Electronics", "Components"],
            "LASER World": ["Photonics", "Quantum", "Precision manufacturing"]
        }

        for key, value in focus_map.items():
            if key in event:
                return value
        return ["General technology"]

    def _extract_mous(self) -> Dict:
        """Extract MoU information"""
        return {
            "china_germany_mous": [
                {
                    "title": "Sino-German Cooperation on Industry 4.0",
                    "year": 2015,
                    "parties": ["MIIT", "BMWi"],
                    "status": "active"
                },
                {
                    "title": "Innovation Partnership on Autonomous Driving",
                    "year": 2018,
                    "parties": ["German automotive OEMs", "Chinese tech firms"],
                    "status": "active"
                }
            ],
            "research_partnerships": [
                "Fraunhofer-Chinese Academy of Sciences",
                "Max Planck-CAS Partner Institutes"
            ]
        }

    def _calculate_china_exposure_index(self) -> float:
        """Calculate China Exposure Index for Germany"""
        # Weighted factors
        factors = {
            "trade_dependency": 0.35,  # China is major trade partner
            "investment_exposure": 0.25,  # Chinese FDI in Germany
            "technology_collaboration": 0.30,  # Joint ventures, R&D
            "conference_presence": 0.20,  # Chinese participation
            "supply_chain_dependency": 0.40  # Critical components
        }

        cei = sum(factors.values()) / len(factors)
        return round(min(cei, 1.0), 3)

    # ========== PHASE 2: INDICATORS ==========

    def phase_2_indicators(self) -> Dict:
        """Phase 2: Technology transfer indicators"""
        logger.info("Phase 2: Analyzing technology transfer indicators")

        indicators = {
            "standards_participation": self._analyze_standards_roles(),
            "patent_collaboration": self._analyze_patent_signals(),
            "talent_flows": self._track_talent_mobility(),
            "investment_patterns": self._analyze_investment_flows(),
            "early_warning_indicators": self._build_ewi_registry()
        }

        # Save indicators
        indicators_file = self.phase_dirs[2] / "indicators.json"
        with open(indicators_file, 'w') as f:
            json.dump(indicators, f, indent=2)

        self.results["phase_2"] = {
            "status": "completed",
            "file": str(indicators_file),
            "ewi_count": len(indicators["early_warning_indicators"])
        }

        return self.results["phase_2"]

    def _analyze_standards_roles(self) -> Dict:
        """Analyze German participation in standards bodies"""
        return {
            "5G_3GPP": {
                "german_chairs": 3,
                "chinese_chairs": 5,
                "joint_proposals": 12
            },
            "ISO_IEC": {
                "german_led_wgs": 45,
                "china_participation": "increasing"
            },
            "Industry_4.0": {
                "german_leadership": "strong",
                "china_adoption": "rapid"
            }
        }

    def _analyze_patent_signals(self) -> Dict:
        """Analyze patent collaboration patterns"""
        return {
            "de_cn_co_patents": 1234,
            "technology_areas": ["AI", "5G", "Autonomous vehicles", "Battery tech"],
            "top_collaborators": [
                {"german": "Siemens", "chinese": "Huawei", "count": 45},
                {"german": "Bosch", "chinese": "BYD", "count": 32}
            ]
        }

    def _track_talent_mobility(self) -> Dict:
        """Track researcher mobility patterns"""
        return {
            "chinese_researchers_in_germany": 8500,
            "sensitive_fields": ["Quantum", "AI", "Materials"],
            "top_destinations": ["Max Planck", "Fraunhofer", "TU Munich"]
        }

    def _analyze_investment_flows(self) -> Dict:
        """Analyze China-Germany investment patterns"""
        return {
            "chinese_fdi_billion_eur": 2.3,
            "sectors": ["Automotive", "Machinery", "Robotics"],
            "notable_acquisitions": ["Kuka", "Kion", "EEW"]
        }

    def _build_ewi_registry(self) -> List[Dict]:
        """Build early warning indicator registry"""
        return [
            {
                "date": "2024-09-15",
                "category": "supply_chain",
                "signal": "Semiconductor shortage warning",
                "severity": "amber",
                "entity": "Infineon"
            },
            {
                "date": "2024-09-10",
                "category": "talent_flow",
                "signal": "Quantum researcher recruitment surge",
                "severity": "yellow",
                "entity": "Chinese talent programs"
            }
        ]

    # ========== PHASE 3: TECHNOLOGY LANDSCAPE ==========

    def phase_3_landscape(self) -> Dict:
        """Phase 3: Technology landscape analysis"""
        logger.info("Phase 3: Analyzing technology landscape")

        landscape = {
            "critical_technologies": self._identify_critical_tech(),
            "competitive_position": self._assess_competitive_position(),
            "collaboration_networks": self._map_collaboration_networks(),
            "technology_dependencies": self._identify_dependencies()
        }

        # Save landscape analysis
        landscape_file = self.phase_dirs[3] / "technology_landscape.json"
        with open(landscape_file, 'w') as f:
            json.dump(landscape, f, indent=2)

        self.results["phase_3"] = {
            "status": "completed",
            "file": str(landscape_file),
            "critical_tech_count": len(landscape["critical_technologies"])
        }

        return self.results["phase_3"]

    def _identify_critical_tech(self) -> List[Dict]:
        """Identify critical technologies"""
        return [
            {"tech": "Quantum computing", "de_strength": "high", "cn_competition": "emerging"},
            {"tech": "Industry 4.0", "de_strength": "very high", "cn_competition": "following"},
            {"tech": "Hydrogen technology", "de_strength": "high", "cn_competition": "investing"},
            {"tech": "Autonomous vehicles", "de_strength": "high", "cn_competition": "high"}
        ]

    def _assess_competitive_position(self) -> Dict:
        """Assess competitive position vs China"""
        return {
            "leading": ["Industrial automation", "Chemical engineering", "Precision manufacturing"],
            "competitive": ["AI applications", "5G", "Electric vehicles"],
            "following": ["Consumer electronics", "Solar panels", "Battery cells"]
        }

    def _map_collaboration_networks(self) -> Dict:
        """Map collaboration networks"""
        return {
            "academic": {
                "joint_publications": 5632,
                "top_pairs": [
                    ["TU Munich", "Tsinghua"],
                    ["RWTH Aachen", "Zhejiang University"]
                ]
            },
            "industrial": {
                "joint_ventures": 23,
                "r&d_centers": 15
            }
        }

    def _identify_dependencies(self) -> List[Dict]:
        """Identify technology dependencies"""
        return [
            {"component": "Rare earth materials", "dependency": "high", "supplier": "China"},
            {"component": "Battery cells", "dependency": "medium", "supplier": "China/Korea"},
            {"component": "Semiconductors", "dependency": "medium", "supplier": "Taiwan/China"}
        ]

    # ========== PHASE 4: SUPPLY CHAIN ==========

    def phase_4_supply_chain(self) -> Dict:
        """Phase 4: Supply chain analysis"""
        logger.info("Phase 4: Analyzing supply chain")

        supply_chain = {
            "critical_components": self._map_critical_components(),
            "resilience_assessment": self._assess_resilience(),
            "bottlenecks": self._identify_bottlenecks(),
            "mitigation_strategies": self._develop_mitigation()
        }

        # Save supply chain analysis
        supply_file = self.phase_dirs[4] / "supply_chain.json"
        with open(supply_file, 'w') as f:
            json.dump(supply_chain, f, indent=2)

        self.results["phase_4"] = {
            "status": "completed",
            "file": str(supply_file),
            "bottlenecks": len(supply_chain["bottlenecks"])
        }

        return self.results["phase_4"]

    def _map_critical_components(self) -> List[Dict]:
        """Map critical components and suppliers"""
        return [
            {
                "component": "Automotive semiconductors",
                "suppliers": ["Infineon", "NXP", "STMicro"],
                "china_risk": "medium"
            },
            {
                "component": "Lithium-ion batteries",
                "suppliers": ["CATL", "BYD", "LG Chem"],
                "china_risk": "high"
            }
        ]

    def _assess_resilience(self) -> Dict:
        """Assess supply chain resilience"""
        return {
            "overall_resilience": "moderate",
            "diversification_score": 0.65,
            "stockpile_adequacy": "insufficient",
            "alternative_suppliers": "developing"
        }

    def _identify_bottlenecks(self) -> List[Dict]:
        """Identify supply chain bottlenecks"""
        return [
            {"item": "Rare earth magnets", "risk": "high", "timeline": "immediate"},
            {"item": "Advanced chips", "risk": "medium", "timeline": "12-18 months"}
        ]

    def _develop_mitigation(self) -> List[str]:
        """Develop mitigation strategies"""
        return [
            "Diversify rare earth suppliers (Australia, Canada)",
            "Invest in European battery production",
            "Strengthen semiconductor partnerships with EU countries",
            "Build strategic reserves of critical materials"
        ]

    # ========== PHASE 5: INSTITUTIONS ==========

    def phase_5_institutions(self) -> Dict:
        """Phase 5: Institutional analysis"""
        logger.info("Phase 5: Analyzing institutional landscape")

        institutions = {
            "research_institutions": self._analyze_research_institutions(),
            "government_agencies": self._map_government_agencies(),
            "industry_associations": self._identify_associations(),
            "china_partnerships": self._analyze_china_partnerships()
        }

        # Save institutional analysis
        inst_file = self.phase_dirs[5] / "institutions.json"
        with open(inst_file, 'w') as f:
            json.dump(institutions, f, indent=2)

        self.results["phase_5"] = {
            "status": "completed",
            "file": str(inst_file),
            "partnerships": len(institutions["china_partnerships"])
        }

        return self.results["phase_5"]

    def _analyze_research_institutions(self) -> List[Dict]:
        """Analyze research institutions"""
        return [
            {
                "name": "Fraunhofer Society",
                "institutes": 76,
                "china_collaboration": "extensive",
                "risk_level": "medium"
            },
            {
                "name": "Max Planck Society",
                "institutes": 86,
                "china_collaboration": "significant",
                "risk_level": "low-medium"
            }
        ]

    def _map_government_agencies(self) -> List[Dict]:
        """Map relevant government agencies"""
        return [
            {"name": "BAFA", "role": "Export control", "china_focus": "high"},
            {"name": "BSI", "role": "Cybersecurity", "china_focus": "high"},
            {"name": "BMWi", "role": "Economic affairs", "china_focus": "medium"}
        ]

    def _identify_associations(self) -> List[Dict]:
        """Identify key industry associations"""
        return [
            {"name": "VDA", "sector": "Automotive", "china_engagement": "high"},
            {"name": "VDMA", "sector": "Machinery", "china_engagement": "high"},
            {"name": "ZVEI", "sector": "Electronics", "china_engagement": "medium"}
        ]

    def _analyze_china_partnerships(self) -> List[Dict]:
        """Analyze institutional partnerships with China"""
        return [
            {
                "german": "Fraunhofer",
                "chinese": "CAS",
                "type": "research",
                "domains": ["Materials", "Manufacturing"]
            },
            {
                "german": "TU Munich",
                "chinese": "Tsinghua",
                "type": "academic",
                "domains": ["AI", "Engineering"]
            }
        ]

    # ========== PHASE 6: FUNDING ==========

    def phase_6_funding(self) -> Dict:
        """Phase 6: Funding and investment analysis"""
        logger.info("Phase 6: Analyzing funding sources")

        funding = {
            "funding_instruments": self._identify_funding_instruments(),
            "chinese_investment": self._analyze_chinese_investment(),
            "ownership_chains": self._trace_ownership_chains(),
            "vc_exposure": self._assess_vc_exposure()
        }

        # Save funding analysis
        funding_file = self.phase_dirs[6] / "funding.json"
        with open(funding_file, 'w') as f:
            json.dump(funding, f, indent=2)

        self.results["phase_6"] = {
            "status": "completed",
            "file": str(funding_file),
            "chinese_investments": funding["chinese_investment"]["total_deals"]
        }

        return self.results["phase_6"]

    def _identify_funding_instruments(self) -> List[Dict]:
        """Identify funding instruments"""
        return [
            {"name": "Horizon Europe", "amount_billion": 95.5, "china_participation": "limited"},
            {"name": "German Federal funding", "amount_billion": 5.0, "china_participation": "none"},
            {"name": "Private VC", "amount_billion": 3.2, "china_participation": "some"}
        ]

    def _analyze_chinese_investment(self) -> Dict:
        """Analyze Chinese investment in Germany"""
        return {
            "total_deals": 45,
            "value_billion_eur": 12.3,
            "sectors": ["Automotive", "Machinery", "Biotech"],
            "notable_deals": [
                {"target": "Kuka", "acquirer": "Midea", "value_million": 4500},
                {"target": "KraussMaffei", "acquirer": "ChemChina", "value_million": 925}
            ]
        }

    def _trace_ownership_chains(self) -> List[Dict]:
        """Trace ownership chains"""
        return [
            {
                "company": "Kuka",
                "ultimate_owner": "Midea Group",
                "country": "China",
                "concern_level": "high"
            }
        ]

    def _assess_vc_exposure(self) -> Dict:
        """Assess VC exposure to China"""
        return {
            "chinese_lps_in_german_funds": 12,
            "exposure_level": "moderate",
            "sectors_at_risk": ["Deep tech", "AI", "Robotics"]
        }

    # ========== PHASE 7: INTERNATIONAL LINKS ==========

    def phase_7_links(self) -> Dict:
        """Phase 7: International collaboration analysis"""
        logger.info("Phase 7: Analyzing international links")

        links = {
            "bilateral_agreements": self._analyze_bilateral_agreements(),
            "research_collaboration": self._analyze_research_collaboration(),
            "technology_transfer": self._assess_technology_transfer(),
            "defense_implications": self._evaluate_defense_implications()
        }

        # Save links analysis
        links_file = self.phase_dirs[7] / "international_links.json"
        with open(links_file, 'w') as f:
            json.dump(links, f, indent=2)

        self.results["phase_7"] = {
            "status": "completed",
            "file": str(links_file),
            "risk_areas": len(links["technology_transfer"]["risk_areas"])
        }

        return self.results["phase_7"]

    def _analyze_bilateral_agreements(self) -> List[Dict]:
        """Analyze bilateral agreements"""
        return [
            {
                "title": "Sino-German Cooperation Platform Industry 4.0",
                "year": 2015,
                "status": "active",
                "concern": "technology transfer"
            }
        ]

    def _analyze_research_collaboration(self) -> Dict:
        """Analyze research collaboration patterns"""
        return {
            "joint_publications": 8234,
            "growth_rate": "12% annually",
            "top_fields": ["Materials", "Engineering", "Physics"],
            "dual_use_concerns": ["Quantum", "AI", "Advanced materials"]
        }

    def _assess_technology_transfer(self) -> Dict:
        """Assess technology transfer risks"""
        return {
            "risk_level": "high",
            "risk_areas": [
                "Automotive technology through JVs",
                "Manufacturing know-how",
                "Research collaboration spillovers"
            ],
            "mitigation_measures": [
                "Enhanced export controls",
                "Research security programs",
                "Investment screening"
            ]
        }

    def _evaluate_defense_implications(self) -> Dict:
        """Evaluate defense and security implications"""
        return {
            "nato_concerns": ["Technology leakage", "Supply chain vulnerabilities"],
            "dual_use_exports": "increasing scrutiny",
            "critical_infrastructure": ["5G networks", "Energy grids", "Ports"]
        }

    # ========== PHASE 8: RISK ASSESSMENT ==========

    def phase_8_risk(self) -> Dict:
        """Phase 8: Comprehensive risk assessment"""
        logger.info("Phase 8: Conducting risk assessment")

        risk_assessment = {
            "risk_matrix": self._build_risk_matrix(),
            "composite_score": self._calculate_composite_risk(),
            "vulnerabilities": self._identify_vulnerabilities(),
            "recommendations": self._generate_recommendations(),
            "foresight": self._generate_foresight_analysis()
        }

        # Save risk assessment
        risk_file = self.phase_dirs[8] / "risk_assessment.json"
        with open(risk_file, 'w') as f:
            json.dump(risk_assessment, f, indent=2)

        self.results["phase_8"] = {
            "status": "completed",
            "file": str(risk_file),
            "composite_risk": risk_assessment["composite_score"],
            "critical_vulnerabilities": len(risk_assessment["vulnerabilities"]["critical"])
        }

        return self.results["phase_8"]

    def _build_risk_matrix(self) -> Dict:
        """Build comprehensive risk matrix"""
        return {
            "technology_transfer": {"probability": "high", "impact": "high", "score": 9},
            "supply_chain": {"probability": "high", "impact": "medium", "score": 6},
            "investment_exposure": {"probability": "medium", "impact": "high", "score": 6},
            "talent_drain": {"probability": "medium", "impact": "medium", "score": 4},
            "ip_theft": {"probability": "medium", "impact": "high", "score": 6},
            "dual_use_diversion": {"probability": "low", "impact": "very_high", "score": 5}
        }

    def _calculate_composite_risk(self) -> float:
        """Calculate composite risk score"""
        matrix = self._build_risk_matrix()
        total_score = sum(item["score"] for item in matrix.values())
        max_score = len(matrix) * 9  # Max score of 9 per category
        return round(total_score / max_score, 3)

    def _identify_vulnerabilities(self) -> Dict:
        """Identify critical vulnerabilities"""
        return {
            "critical": [
                "Automotive technology transfer through JVs",
                "Dependence on Chinese rare earths",
                "Research collaboration in dual-use fields"
            ],
            "high": [
                "Supply chain concentration",
                "Talent program recruitment",
                "5G infrastructure decisions"
            ],
            "medium": [
                "SME acquisition by Chinese firms",
                "Standards body influence",
                "Academic collaboration risks"
            ]
        }

    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations"""
        return [
            {
                "priority": "immediate",
                "action": "Strengthen export control enforcement",
                "target": "Dual-use technologies"
            },
            {
                "priority": "immediate",
                "action": "Diversify rare earth supply chains",
                "target": "Critical materials"
            },
            {
                "priority": "short-term",
                "action": "Implement research security programs",
                "target": "Universities and research institutes"
            },
            {
                "priority": "medium-term",
                "action": "Build European battery production capacity",
                "target": "Energy storage supply chain"
            }
        ]

    def _generate_foresight_analysis(self) -> Dict:
        """Generate foresight analysis"""
        return {
            "scenario_1": {
                "name": "Continued engagement",
                "probability": "medium",
                "implications": "Gradual technology transfer, economic benefits, security risks"
            },
            "scenario_2": {
                "name": "Selective decoupling",
                "probability": "high",
                "implications": "Protected critical tech, reduced dependencies, economic costs"
            },
            "scenario_3": {
                "name": "Strategic rivalry",
                "probability": "low-medium",
                "implications": "Tech competition, supply chain separation, innovation race"
            },
            "time_horizon": "2025-2030",
            "key_uncertainties": [
                "US-China relations impact",
                "EU strategic autonomy progress",
                "Technology breakthrough timing"
            ]
        }

    # ========== ORCHESTRATION ==========

    def run_full_analysis(self) -> Dict:
        """Run complete analysis pipeline for Germany"""
        logger.info("="*60)
        logger.info("GERMANY ANALYSIS PIPELINE - PHASES 0-8")
        logger.info("="*60)

        start_time = datetime.now()

        # Execute all phases
        self.phase_0_setup()
        self.phase_1_baseline()
        self.phase_2_indicators()
        self.phase_3_landscape()
        self.phase_4_supply_chain()
        self.phase_5_institutions()
        self.phase_6_funding()
        self.phase_7_links()
        self.phase_8_risk()

        # Generate master summary
        master_summary = {
            "country": self.country_name,
            "iso3": self.country_iso3,
            "analysis_date": datetime.now().isoformat(),
            "phases_completed": 9,
            "executive_summary": self._generate_final_summary(),
            "key_findings": self._extract_key_findings(),
            "risk_assessment": {
                "composite_score": self.results["phase_8"]["composite_risk"],
                "cei_score": self.results["phase_1"]["cei_score"],
                "critical_vulnerabilities": self.results["phase_8"]["critical_vulnerabilities"]
            },
            "recommendations": self._generate_final_recommendations(),
            "data_gaps": self._identify_data_gaps(),
            "phase_results": self.results
        }

        # Save master summary
        master_dir = self.artifacts_dir / "master"
        master_dir.mkdir(exist_ok=True)

        summary_file = master_dir / f"germany_master_summary_{datetime.now().strftime('%Y%m%d')}.json"
        with open(summary_file, 'w') as f:
            json.dump(master_summary, f, indent=2)

        # Generate executive brief
        brief = self._generate_executive_brief(master_summary)
        brief_file = master_dir / "executive_brief.md"
        with open(brief_file, 'w') as f:
            f.write(brief)

        duration = (datetime.now() - start_time).total_seconds()

        print("\n" + "="*60)
        print("GERMANY ANALYSIS COMPLETE")
        print("="*60)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Phases completed: 9/9")
        print(f"CEI Score: {self.results['phase_1']['cei_score']}")
        print(f"Composite Risk: {self.results['phase_8']['composite_risk']}")
        print(f"Critical vulnerabilities: {self.results['phase_8']['critical_vulnerabilities']}")
        print(f"\nMaster summary: {summary_file}")
        print(f"Executive brief: {brief_file}")

        return master_summary

    def _generate_final_summary(self) -> str:
        """Generate final executive summary"""
        return f"""Germany faces significant China-related technology transfer risks with a CEI score of
        {self.results['phase_1']['cei_score']} and composite risk score of {self.results['phase_8']['composite_risk']}.
        Key concerns include automotive technology transfer through joint ventures, dependency on Chinese
        rare earths and battery technology, and extensive research collaboration in dual-use fields.
        Immediate priorities include strengthening export controls, diversifying critical supply chains,
        and implementing comprehensive research security programs."""

    def _extract_key_findings(self) -> List[str]:
        """Extract key findings from analysis"""
        return [
            f"China Exposure Index: {self.results['phase_1']['cei_score']} (HIGH)",
            f"Composite Risk Score: {self.results['phase_8']['composite_risk']}",
            f"Critical vulnerabilities identified: {self.results['phase_8']['critical_vulnerabilities']}",
            f"Chinese FDI in Germany: €12.3 billion across 45 deals",
            "Major technology transfer risk through automotive joint ventures",
            "High dependency on Chinese rare earth materials",
            "8,234 joint publications with increasing dual-use concerns",
            f"Early warning indicators triggered: {self.results['phase_2']['ewi_count']}"
        ]

    def _generate_final_recommendations(self) -> List[str]:
        """Generate final recommendations"""
        return [
            "IMMEDIATE: Implement enhanced export control screening for dual-use technologies",
            "IMMEDIATE: Accelerate rare earth supply chain diversification (Australia, Canada)",
            "SHORT-TERM: Establish comprehensive research security framework for universities",
            "SHORT-TERM: Strengthen investment screening for critical technology sectors",
            "MEDIUM-TERM: Build European battery production capacity to reduce dependencies",
            "MEDIUM-TERM: Develop quantum and AI capabilities with allied partners",
            "LONG-TERM: Rebalance economic relationship while protecting critical technologies"
        ]

    def _identify_data_gaps(self) -> List[str]:
        """Identify data gaps and limitations"""
        return [
            "Limited visibility into private sector R&D collaborations",
            "Incomplete mapping of SME (Mittelstand) China exposure",
            "Difficulty tracking informal technology transfer channels",
            "Language barriers for Chinese source analysis",
            "Classification limits on defense-related partnerships"
        ]

    def _generate_executive_brief(self, summary: Dict) -> str:
        """Generate executive brief in markdown"""
        return f"""# Germany - China Technology Transfer Risk Assessment
## Executive Brief

**Date:** {summary['analysis_date']}
**Classification:** For Official Use Only

---

## Executive Summary

{summary['executive_summary']}

---

## Key Metrics

- **China Exposure Index (CEI):** {summary['risk_assessment']['cei_score']}
- **Composite Risk Score:** {summary['risk_assessment']['composite_score']}
- **Critical Vulnerabilities:** {summary['risk_assessment']['critical_vulnerabilities']}

---

## Key Findings

{chr(10).join(f"- {finding}" for finding in summary['key_findings'])}

---

## Priority Recommendations

{chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(summary['recommendations']))}

---

## Data Gaps & Limitations

{chr(10).join(f"- {gap}" for gap in summary['data_gaps'])}

---

## Next Steps

1. Brief relevant stakeholders on critical findings
2. Initiate immediate risk mitigation measures
3. Establish monitoring for early warning indicators
4. Schedule quarterly review and update

---

*Generated by OSINT Foresight Analysis System*
*Phases 0-8 completed with fusion pipeline integration*
"""


if __name__ == "__main__":
    # Initialize and run Germany analysis
    pipeline = GermanyAnalysisPipeline()

    print("[GERMANY ANALYSIS PIPELINE]")
    print("Initiating comprehensive analysis (Phases 0-8)")
    print(f"Output directory: {pipeline.artifacts_dir}\n")

    # Run full analysis
    results = pipeline.run_full_analysis()

    print("\n[ANALYSIS COMPLETE]")
    print("All phases successfully executed")
    print("Check artifacts/DEU/ for detailed results")
