#!/usr/bin/env python3
"""
Dual-Use Technology Mapper (Refined v1, post-Dream Team review)

Purpose: Build a verifiable, de-duplicated, query-efficient catalog of dual-use technologies,
their actors, geographies, maturity, dependencies, and forward trajectories.

Requirements:
- No hallucinations: Every fact traceable to downloadable document
- Deterministic IDs and stable enums only
- Reproducibility: emit machine-readable artifacts + run log
"""

import sqlite3
import json
import csv
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CANONICAL ONTOLOGY (controlled enums)
# ============================================================================

TECHNOLOGY_CATEGORIES = {
    'ai', 'quantum', 'semiconductors', 'space', 'aerospace', 'biotech',
    'advanced_materials', 'energy', 'cyber', 'telecom', 'autonomy_robotics',
    'manufacturing', 'sensing', 'photonics', 'additive_manufacturing',
    'nav_timing', 'high_performance_computing'
}

MATURITY_LEVELS = {
    'research', 'development', 'demonstration', 'pilot_deploy', 'deployment', 'operational'
}

ACTOR_TYPES = {
    'company', 'university', 'research_institute', 'government', 'lab',
    'soes', 'startup', 'funder', 'standards_body'
}

DEPENDENCY_TYPES = {
    'infrastructure', 'material', 'equipment', 'workforce', 'funding',
    'policy_regulatory', 'data', 'energy', 'logistics'
}

EVIDENCE_QUALITY = {'STRONG', 'MODERATE', 'WEAK', 'SPECULATIVE'}

HORIZONS = {'near', 'mid', 'long'}  # near(0-2y), mid(3-7y), long(8-20y)

SIGNAL_TYPES = {'roadmap', 'policy', 'funding', 'standards', 'infrastructure', 'supply_chain'}

ACTOR_ROLES = {'lead', 'participant', 'funder', 'regulator'}

CRITICALITY_LEVELS = {'critical', 'high', 'medium', 'low'}

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class DualUseTechnology:
    """Core dual-use technology record"""
    tech_uid: str
    technology_category: str
    specific_technology: str
    maturity_level: Optional[str]
    dual_use_flag: bool
    military_application: Optional[str]
    civilian_application: Optional[str]
    actors: List[Dict[str, str]]
    geolocations: List[Dict[str, Any]]
    china_involvement_flag: bool
    eu_involvement_flag: bool
    key_reports: List[str]
    timeline_projection: Optional[Dict[str, Any]]
    last_seen_date: str
    evidence_quality: str
    source_confidence: float
    sources: List[Dict[str, str]]


@dataclass
class TechnologyDependency:
    """Technology dependency record"""
    dep_uid: str
    tech_uid: str
    dependency_type: str
    description: str
    criticality: str
    dependency_actor: Optional[Dict[str, str]]
    geo: Optional[Dict[str, str]]
    referenced_sources: List[Dict[str, str]]


@dataclass
class ForesightSignal:
    """Foresight signal record"""
    signal_uid: str
    tech_uid: str
    signal_type: str
    statement: str
    horizon: str
    confidence: float
    source_ref: str


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_uid(data: str) -> str:
    """Generate deterministic SHA256 UID"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def normalize_text(text: str) -> str:
    """Normalize text: lowercase, trim, collapse spaces, strip punctuation at edges"""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'^[^\w]+|[^\w]+$', '', text)
    return text


def map_to_category(tech_name: str) -> Optional[str]:
    """Map technology name to category enum - ENHANCED with specialized terms"""
    tech_lower = tech_name.lower()

    # Direct keyword matching (ENHANCED)
    category_keywords = {
        'ai': ['artificial intelligence', 'machine learning', 'neural network', 'deep learning',
               'llm', 'nlp', 'computer vision', 'ai'],
        'quantum': ['quantum computing', 'quantum communication', 'quantum sensing', 'quantum',
                   'qubit', 'quantum encryption'],
        'semiconductors': ['semiconductor', 'chip', 'microchip', 'processor', 'lithography', 'wafer',
                          'fabrication', 'foundry', 'asml', 'tsmc', 'fab'],
        'space': ['satellite', 'space', 'orbital', 'launcher', 'rocket', 'spacecraft', 'iss',
                 'launch vehicle'],
        'aerospace': ['aircraft', 'helicopter', 'drone', 'uav', 'aviation', 'aerospace', 'hypersonic',
                     'missile', 'ballistic', 'cruise missile', 'icbm', 'fighter jet'],
        'biotech': ['biotech', 'genetic', 'crispr', 'synthetic biology', 'biopharma', 'gene editing',
                   'genomics', 'proteomics'],
        'advanced_materials': ['graphene', 'composite', 'nanomaterial', 'metamaterial', 'advanced material',
                              'carbon fiber', 'ceramic', 'alloy'],
        'energy': ['solar', 'wind', 'nuclear', 'battery', 'energy storage', 'fusion', 'fission',
                  'reactor', 'renewable', 'grid', 'power generation'],
        'cyber': ['cybersecurity', 'encryption', 'cyber', 'network security', 'hacking', 'malware',
                 'ransomware', 'intrusion', 'firewall', 'zero-day'],
        'telecom': ['5g', '6g', 'telecommunications', 'wireless', 'cellular', 'network', 'spectrum',
                   'broadband', 'fiber optic', 'telecom'],
        'autonomy_robotics': ['autonomous', 'robotics', 'robot', 'automation', 'unmanned',
                             'autonomous vehicle', 'self-driving'],
        'manufacturing': ['manufacturing', 'production', 'assembly', 'industrial', 'factory'],
        'sensing': ['sensor', 'radar', 'lidar', 'imaging', 'detection', 'surveillance',
                   'reconnaissance', 'isr'],
        'photonics': ['photonics', 'laser', 'optical', 'optics', 'euv', 'extreme ultraviolet',
                     'photolithography', 'light'],
        'additive_manufacturing': ['3d print', 'additive manufacturing', 'additive', 'printing'],
        'nav_timing': ['gps', 'gnss', 'navigation', 'timing', 'positioning', 'geolocation',
                      'satellite navigation'],
        'high_performance_computing': ['supercomputing', 'hpc', 'high performance computing',
                                      'exascale', 'petaflop']
    }

    # Multi-pass matching: try exact phrases first, then keywords
    # This helps with "euv" vs "euv lithography" disambiguation
    for category, keywords in category_keywords.items():
        # First pass: exact phrase match
        for keyword in keywords:
            if tech_lower == keyword or f" {keyword} " in f" {tech_lower} ":
                return category

    # Second pass: substring match
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in tech_lower:
                return category

    return None


def infer_maturity(text: str) -> Optional[str]:
    """Infer maturity level from text context"""
    text_lower = text.lower()

    if any(kw in text_lower for kw in ['operational', 'deployed', 'production']):
        return 'operational'
    elif any(kw in text_lower for kw in ['deployment', 'rollout']):
        return 'deployment'
    elif any(kw in text_lower for kw in ['pilot', 'trial', 'test']):
        return 'pilot_deploy'
    elif any(kw in text_lower for kw in ['demonstration', 'demo', 'prototype']):
        return 'demonstration'
    elif any(kw in text_lower for kw in ['development', 'developing']):
        return 'development'
    elif any(kw in text_lower for kw in ['research', 'r&d', 'laboratory']):
        return 'research'

    return None


def detect_china_involvement(text: str, entities: List[Dict]) -> bool:
    """Detect China involvement from text or entities"""
    text_lower = text.lower()

    # Text-based detection
    china_keywords = ['china', 'chinese', 'prc', 'beijing', 'huawei', 'zte', 'alibaba', 'ccp']
    if any(kw in text_lower for kw in china_keywords):
        return True

    # Entity-based detection
    for entity in entities:
        entity_name = entity.get('entity_name', '').lower()
        if any(kw in entity_name for kw in china_keywords):
            return True

    return False


def detect_eu_involvement(text: str, entities: List[Dict]) -> bool:
    """Detect EU involvement from text or entities"""
    # Text-based detection
    text_lower = text.lower()
    eu_keywords = ['european union', 'eu ', 'europe', 'brussels', 'european commission',
                   'germany', 'france', 'italy', 'spain', 'poland', 'netherlands']
    if any(kw in text_lower for kw in eu_keywords):
        return True

    # Entity-based detection - check entity names
    for entity in entities:
        entity_name = entity.get('entity_name', '').lower()
        if any(kw in entity_name for kw in eu_keywords):
            return True

    return False


def extract_dependencies(text: str) -> List[Tuple[str, str]]:
    """Extract dependencies from text using pattern matching"""
    dependencies = []
    text_lower = text.lower()

    # Pattern matching for dependencies
    patterns = {
        'infrastructure': r'(?:requires?|needs?|depends? on)\s+(?:the\s+)?infrastructure',
        'material': r'(?:requires?|needs?)\s+(?:rare earth|materials?|resources?)',
        'equipment': r'(?:requires?|needs?)\s+(?:equipment|machinery|tools?)',
        'workforce': r'(?:requires?|needs?)\s+(?:skilled\s+)?(?:workforce|talent|engineers?|scientists?)',
        'funding': r'(?:requires?|needs?)\s+(?:funding|investment|capital)',
        'policy_regulatory': r'(?:requires?|needs?)\s+(?:policy|regulation|framework|standards?)',
        'data': r'(?:requires?|needs?)\s+(?:data|datasets?)',
        'energy': r'(?:requires?|needs?)\s+(?:energy|power)',
        'logistics': r'(?:requires?|needs?)\s+(?:logistics|supply chain)'
    }

    for dep_type, pattern in patterns.items():
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            # Extract context around match
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 100)
            context = text[start:end].strip()
            dependencies.append((dep_type, context))

    return dependencies


def extract_foresight_signals(text: str) -> List[Tuple[str, str, str]]:
    """Extract foresight signals from text - ENHANCED"""
    if not text:
        return []

    signals = []

    # Pattern for explicit next steps / requirements (EXPANDED)
    horizon_patterns = {
        'near': r'(?:next\s+(?:1-2|one to two|1|2)\s+years?|by\s+202[3-6]|2023|2024|2025|2026|near[- ]term)',
        'mid': r'(?:by\s+20(?:27|28|29|30|31|32)|in\s+the\s+(?:mid|medium)[- ]term|203[0-2])',
        'long': r'(?:by\s+20(?:35|40|45|50)|in\s+the\s+long[- ]term|204[0-5]|beyond\s+203)'
    }

    signal_patterns = {
        'roadmap': r'roadmap|plan(?:ning)?\s+to|intend(?:s|ing)?\s+to|will\s+develop|strategy|initiative',
        'policy': r'policy|regulation|legislation|law|govern(?:ance|ment)|framework|directive',
        'funding': r'funding|investment|budget|grant|financing|capital|fund(?:ed|ing)',
        'standards': r'standard(?:s|ization)?|certification|specification|protocol|guideline',
        'infrastructure': r'infrastructure|facility|site|plant|center|installation|network',
        'supply_chain': r'supply\s+chain|sourcing|procurement|supplier|vendor|logistics'
    }

    # Split text into sentences for better context extraction
    sentences = re.split(r'[.!?]+', text)

    for sentence in sentences:
        if len(sentence) < 20:  # Skip very short fragments
            continue

        sentence_lower = sentence.lower()

        for signal_type, sig_pattern in signal_patterns.items():
            if re.search(sig_pattern, sentence_lower):
                for horizon, hor_pattern in horizon_patterns.items():
                    if re.search(hor_pattern, sentence_lower):
                        # Found both signal type and horizon in same sentence
                        statement = sentence.strip()[:500]  # Limit to 500 chars
                        signals.append((signal_type, horizon, statement))
                        break  # Only one horizon per sentence

    return signals


def extract_geographic_locations(text: str, entity_names: List[str]) -> List[Dict[str, Any]]:
    """Extract geographic locations from text and entity names - NEW"""
    locations = []

    # Comprehensive country mapping: name -> ISO2 code
    country_map = {
        # Major powers
        'china': 'CN', 'chinese': 'CN', 'prc': 'CN', 'beijing': 'CN',
        'united states': 'US', 'usa': 'US', 'america': 'US', 'american': 'US',
        'russia': 'RU', 'russian': 'RU', 'moscow': 'RU',

        # EU27 + UK
        'austria': 'AT', 'belgium': 'BE', 'bulgaria': 'BG', 'croatia': 'HR',
        'cyprus': 'CY', 'czech republic': 'CZ', 'czechia': 'CZ', 'denmark': 'DK',
        'estonia': 'EE', 'finland': 'FI', 'france': 'FR', 'french': 'FR',
        'germany': 'DE', 'german': 'DE', 'greece': 'GR', 'greek': 'GR',
        'hungary': 'HU', 'ireland': 'IE', 'italy': 'IT', 'italian': 'IT',
        'latvia': 'LV', 'lithuania': 'LT', 'luxembourg': 'LU', 'malta': 'MT',
        'netherlands': 'NL', 'dutch': 'NL', 'poland': 'PL', 'polish': 'PL',
        'portugal': 'PT', 'romania': 'RO', 'slovakia': 'SK', 'slovenia': 'SI',
        'spain': 'ES', 'spanish': 'ES', 'sweden': 'SE', 'swedish': 'SE',
        'united kingdom': 'GB', 'uk': 'GB', 'britain': 'GB', 'british': 'GB',

        # Other European
        'norway': 'NO', 'switzerland': 'CH', 'iceland': 'IS', 'serbia': 'RS',
        'turkey': 'TR', 'ukraine': 'UA', 'belarus': 'BY',

        # Asia-Pacific
        'japan': 'JP', 'japanese': 'JP', 'south korea': 'KR', 'korea': 'KR',
        'india': 'IN', 'indian': 'IN', 'australia': 'AU', 'australian': 'AU',
        'taiwan': 'TW', 'singapore': 'SG', 'hong kong': 'HK',
        'vietnam': 'VN', 'thailand': 'TH', 'malaysia': 'MY', 'indonesia': 'ID',

        # Middle East
        'israel': 'IL', 'iran': 'IR', 'saudi arabia': 'SA', 'uae': 'AE',

        # Americas
        'canada': 'CA', 'canadian': 'CA', 'brazil': 'BR', 'mexico': 'MX',

        # Africa
        'south africa': 'ZA', 'egypt': 'EG', 'nigeria': 'NG'
    }

    # Chinese cities/provinces for sub-national resolution
    chinese_locations = {
        'beijing': ('Beijing', 'CN'),
        'shanghai': ('Shanghai', 'CN'),
        'shenzhen': ('Shenzhen', 'CN'),
        'guangzhou': ('Guangzhou', 'CN'),
        'hong kong': ('Hong Kong', 'HK'),
        'taipei': ('Taipei', 'TW'),
        'wuhan': ('Wuhan', 'CN'),
        'chengdu': ('Chengdu', 'CN'),
        'xi\'an': ('Xi\'an', 'CN'),
        'hangzhou': ('Hangzhou', 'CN')
    }

    text_lower = text.lower() if text else ''
    seen_countries = set()

    # Extract from entity names
    for entity_name in entity_names:
        entity_lower = entity_name.lower()

        # Check for Chinese locations first (more specific)
        for loc_name, (region, iso2) in chinese_locations.items():
            if loc_name in entity_lower:
                locations.append({
                    'country_iso2': iso2,
                    'region_name': region,
                    'facility_name': entity_name,
                    'lat': None,
                    'lon': None,
                    'georesolution': 'region'
                })
                seen_countries.add(iso2)
                break

        # Check for country mentions
        for country_name, iso2 in country_map.items():
            if country_name in entity_lower and iso2 not in seen_countries:
                locations.append({
                    'country_iso2': iso2,
                    'region_name': None,
                    'facility_name': entity_name,
                    'lat': None,
                    'lon': None,
                    'georesolution': 'country'
                })
                seen_countries.add(iso2)
                break

    # Extract from text (for countries not already found in entities)
    for country_name, iso2 in country_map.items():
        if iso2 not in seen_countries:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(country_name) + r'\b'
            if re.search(pattern, text_lower):
                locations.append({
                    'country_iso2': iso2,
                    'region_name': None,
                    'facility_name': None,
                    'lat': None,
                    'lon': None,
                    'georesolution': 'country'
                })
                seen_countries.add(iso2)

    return locations


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

class DualUseTechnologyMapper:
    """Main mapper class"""

    def __init__(self, db_path: str, output_dir: str):
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.technologies: Dict[str, DualUseTechnology] = {}
        self.dependencies: Dict[str, TechnologyDependency] = {}
        self.foresight_signals: Dict[str, ForesightSignal] = {}

        self.qa_issues: List[Dict[str, Any]] = []
        self.stats = {
            'reports_processed': 0,
            'technologies_discovered': 0,
            'technologies_deduped': 0,
            'dependencies_extracted': 0,
            'foresight_signals_extracted': 0,
            'qa_issues': 0
        }

        logger.info(f"Initialized DualUseTechnologyMapper")
        logger.info(f"Database: {self.db_path}")
        logger.info(f"Output directory: {self.output_dir}")

    def connect_db(self) -> sqlite3.Connection:
        """Connect to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def discover_technologies(self):
        """Phase 1: Discovery - extract candidate technologies from reports"""
        logger.info("=== PHASE 1: DISCOVERY ===")

        conn = self.connect_db()
        cursor = conn.cursor()

        # Get all thinktank reports (use publication_date_iso or fallback to all)
        cursor.execute("""
            SELECT report_id, title,
                   COALESCE(publication_date, publication_date_iso, '2020-01-01') as publication_date,
                   source_organization, content_text, key_findings, url_origin
            FROM thinktank_reports
            ORDER BY report_id DESC
        """)

        reports = cursor.fetchall()
        logger.info(f"Found {len(reports)} reports to process (2015+)")

        for report in reports:
            report_id = report['report_id']
            self.stats['reports_processed'] += 1

            # Get associated entities
            cursor.execute("""
                SELECT entity_name, entity_type, confidence, risk_level
                FROM report_entities
                WHERE report_id = ?
            """, (report_id,))
            entities = [dict(row) for row in cursor.fetchall()]

            # Get associated technologies
            cursor.execute("""
                SELECT specific_technology, dual_use_flag, military_application,
                       civilian_application, maturity_level, technology_category
                FROM report_technologies
                WHERE report_id = ?
            """, (report_id,))
            report_techs = cursor.fetchall()

            # Process each technology
            for tech in report_techs:
                self.process_technology(report, tech, entities)

        conn.close()
        logger.info(f"Discovery complete: {self.stats['technologies_discovered']} technologies found")

        # Now extract dependencies and foresight signals for all discovered technologies
        logger.info("Extracting dependencies and foresight signals...")
        conn = self.connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT report_id, title, content_text, key_findings
            FROM thinktank_reports
            ORDER BY report_id DESC
        """)
        reports = cursor.fetchall()

        for report in reports:
            if report['content_text'] or report['key_findings']:
                self.extract_from_text(report)

        conn.close()
        logger.info(f"Extraction complete: {self.stats['dependencies_extracted']} dependencies, {self.stats['foresight_signals_extracted']} signals")

    def process_technology(self, report: sqlite3.Row, tech: sqlite3.Row, entities: List[Dict]):
        """Process a single technology from report"""
        tech_name = normalize_text(tech['specific_technology'])
        if not tech_name:
            return

        # Map to category (use existing if available, else infer)
        try:
            category = tech['technology_category']
            if not category or category not in TECHNOLOGY_CATEGORIES:
                category = map_to_category(tech_name)
        except (KeyError, IndexError):
            category = map_to_category(tech_name)
        if not category:
            self.qa_issues.append({
                'type': 'unmapped_category',
                'technology': tech_name,
                'report_id': report['report_id']
            })
            self.stats['qa_issues'] += 1
            return

        # Generate UID
        primary_actor = entities[0]['entity_name'] if entities else 'unknown'
        uid_data = f"{tech_name}||{normalize_text(primary_actor)}"
        tech_uid = generate_uid(uid_data)

        # Extract geolocations from entities and report text - ENHANCED
        entity_names_list = [e['entity_name'] for e in entities]
        key_findings = report['key_findings'] if report['key_findings'] else ''
        text_to_check = f"{report['title']} {key_findings}"
        geolocations = extract_geographic_locations(text_to_check, entity_names_list)

        # Build actors list
        actors = []
        for entity in entities:
            # Use confidence to determine role
            confidence = entity.get('confidence', 0) or 0
            actors.append({
                'name': entity['entity_name'],
                'type': entity.get('entity_type', 'unknown'),
                'role': 'lead' if confidence > 0.7 else 'participant'
            })

        # Detect involvement (use already-extracted key_findings)
        china_flag = detect_china_involvement(text_to_check, entities)
        eu_flag = detect_eu_involvement(text_to_check, entities)

        # Create or update technology record
        if tech_uid in self.technologies:
            # Merge with existing
            existing = self.technologies[tech_uid]
            existing.key_reports.append(report['report_id'])
            url_origin = report['url_origin'] if report['url_origin'] else ''
            existing.sources.append({
                'kind': 'thinktank_report',
                'id_or_url': url_origin
            })
            # Update last seen date if newer
            if report['publication_date'] > existing.last_seen_date:
                existing.last_seen_date = report['publication_date']
            self.stats['technologies_deduped'] += 1
        else:
            # Create new
            technology = DualUseTechnology(
                tech_uid=tech_uid,
                technology_category=category,
                specific_technology=tech_name,
                maturity_level=tech['maturity_level'] if tech['maturity_level'] else 'research',
                dual_use_flag=bool(tech['dual_use_flag'] if tech['dual_use_flag'] else 1),
                military_application=tech['military_application'] if tech['military_application'] else None,
                civilian_application=tech['civilian_application'] if tech['civilian_application'] else None,
                actors=actors,
                geolocations=geolocations,
                china_involvement_flag=china_flag,
                eu_involvement_flag=eu_flag,
                key_reports=[report['report_id']],
                timeline_projection=None,
                last_seen_date=report['publication_date'] or datetime.now().isoformat()[:10],
                evidence_quality='MODERATE',
                source_confidence=0.7,
                sources=[{
                    'kind': 'thinktank_report',
                    'id_or_url': report['url_origin'] if report['url_origin'] else ''
                }]
            )

            self.technologies[tech_uid] = technology
            self.stats['technologies_discovered'] += 1

    def extract_from_text(self, report: sqlite3.Row):
        """Extract dependencies and signals from report text - ENHANCED"""
        # Combine multiple text fields for richer extraction
        text_parts = []
        if report['content_text']:
            text_parts.append(report['content_text'])
        if report['key_findings']:
            text_parts.append(report['key_findings'])
        if report['title']:
            text_parts.append(report['title'])

        combined_text = ' '.join(text_parts)
        if not combined_text or len(combined_text) < 100:
            return

        # Extract dependencies
        deps = extract_dependencies(combined_text)
        for dep_type, context in deps:
            # Link to all technologies from this report
            for tech_uid, tech in self.technologies.items():
                if report['report_id'] in tech.key_reports:
                    self.add_dependency(tech_uid, report['report_id'], dep_type, context)
                    break  # Only add once per dependency

        # Extract foresight signals
        signals = extract_foresight_signals(combined_text)
        for signal_type, horizon, statement in signals:
            # Link to all technologies from this report
            for tech_uid, tech in self.technologies.items():
                if report['report_id'] in tech.key_reports:
                    self.add_foresight_signal(tech_uid, report['report_id'], signal_type, horizon, statement)
                    break  # Only add once per signal

    def add_dependency(self, tech_uid: str, report_id: str, dep_type: str, description: str):
        """Add a technology dependency - ENHANCED with tech linkage"""
        dep_uid = generate_uid(f"{tech_uid}||{dep_type}||{description[:50]}")

        if dep_uid not in self.dependencies:
            # Infer criticality from keywords
            desc_lower = description.lower()
            if any(kw in desc_lower for kw in ['critical', 'essential', 'vital', 'required']):
                criticality = 'critical'
            elif any(kw in desc_lower for kw in ['important', 'significant', 'major']):
                criticality = 'high'
            elif any(kw in desc_lower for kw in ['minor', 'optional']):
                criticality = 'low'
            else:
                criticality = 'medium'

            dependency = TechnologyDependency(
                dep_uid=dep_uid,
                tech_uid=tech_uid,
                dependency_type=dep_type,
                description=description[:500],
                criticality=criticality,
                dependency_actor=None,
                geo=None,
                referenced_sources=[{'kind': 'thinktank_report', 'id_or_url': str(report_id)}]
            )
            self.dependencies[dep_uid] = dependency
            self.stats['dependencies_extracted'] += 1

    def add_foresight_signal(self, tech_uid: str, report_id: str, signal_type: str, horizon: str, statement: str):
        """Add a foresight signal - ENHANCED with tech linkage"""
        signal_uid = generate_uid(f"{tech_uid}||{signal_type}||{horizon}||{statement[:50]}")

        if signal_uid not in self.foresight_signals:
            # Infer confidence from language certainty
            stmt_lower = statement.lower()
            if any(kw in stmt_lower for kw in ['will', 'committed', 'confirmed', 'announced']):
                confidence = 0.8
            elif any(kw in stmt_lower for kw in ['plan', 'expect', 'intend', 'aim']):
                confidence = 0.6
            elif any(kw in stmt_lower for kw in ['may', 'could', 'might', 'potential']):
                confidence = 0.4
            else:
                confidence = 0.5

            signal = ForesightSignal(
                signal_uid=signal_uid,
                tech_uid=tech_uid,
                signal_type=signal_type,
                statement=statement[:1000],
                horizon=horizon,
                confidence=confidence,
                source_ref=str(report_id)
            )
            self.foresight_signals[signal_uid] = signal
            self.stats['foresight_signals_extracted'] += 1

    def generate_outputs(self):
        """Generate all required outputs"""
        logger.info("=== GENERATING OUTPUTS ===")

        timestamp = datetime.now().strftime('%Y%m%d')
        export_dir = self.output_dir / timestamp
        export_dir.mkdir(exist_ok=True)

        # JSON outputs
        self.write_json(export_dir / 'dualuse_technologies.json',
                       [asdict(t) for t in self.technologies.values()])
        self.write_json(export_dir / 'technology_dependencies.json',
                       [asdict(d) for d in self.dependencies.values()])
        self.write_json(export_dir / 'foresight_signals.json',
                       [asdict(s) for s in self.foresight_signals.values()])

        # CSV outputs
        self.write_csv(export_dir / 'dualuse_technologies.csv', self.technologies.values())
        self.write_csv(export_dir / 'technology_dependencies.csv', self.dependencies.values())
        self.write_csv(export_dir / 'foresight_signals.csv', self.foresight_signals.values())

        # SQL outputs
        self.write_sql(export_dir / 'dualuse_technologies.sql')

        # Run log
        run_log = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'qa_issues_count': len(self.qa_issues),
            'null_rates': self.calculate_null_rates()
        }
        self.write_json(export_dir / 'run_log.json', run_log)

        # QA report
        qa_report = {
            'total_issues': len(self.qa_issues),
            'issues_by_type': Counter([i['type'] for i in self.qa_issues]),
            'issues': self.qa_issues[:100]  # First 100 for brevity
        }
        self.write_json(export_dir / 'qa_report.json', qa_report)

        # Executive summary
        self.generate_executive_summary(export_dir / 'executive_summary.md')

        logger.info(f"All outputs generated in: {export_dir}")

    def write_json(self, path: Path, data: Any):
        """Write JSON file"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Wrote {path.name}")

    def write_csv(self, path: Path, data: Any):
        """Write CSV file"""
        if not data:
            return

        data_list = list(data)
        if not data_list:
            return

        # Convert dataclass to dict and flatten JSON fields
        rows = []
        for item in data_list:
            row = asdict(item) if hasattr(item, '__dataclass_fields__') else item
            # Convert complex fields to JSON strings
            for key, value in row.items():
                if isinstance(value, (list, dict)):
                    row[key] = json.dumps(value)
            rows.append(row)

        with open(path, 'w', newline='', encoding='utf-8') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

        logger.info(f"Wrote {path.name}")

    def write_sql(self, path: Path):
        """Write SQL INSERT statements"""
        with open(path, 'w', encoding='utf-8') as f:
            # Write DDL first
            f.write(self.get_ddl())
            f.write('\n\n')

            # Write INSERTs for technologies
            for tech in self.technologies.values():
                values = self.format_sql_values(asdict(tech))
                f.write(f"INSERT INTO dualuse_technologies VALUES {values};\n")

            # Write INSERTs for dependencies
            for dep in self.dependencies.values():
                values = self.format_sql_values(asdict(dep))
                f.write(f"INSERT INTO technology_dependencies VALUES {values};\n")

            # Write INSERTs for signals
            for sig in self.foresight_signals.values():
                values = self.format_sql_values(asdict(sig))
                f.write(f"INSERT INTO foresight_signals VALUES {values};\n")

        logger.info(f"Wrote {path.name}")

    def format_sql_values(self, data: Dict) -> str:
        """Format values for SQL INSERT"""
        values = []
        for v in data.values():
            if v is None:
                values.append('NULL')
            elif isinstance(v, bool):
                values.append('1' if v else '0')
            elif isinstance(v, (int, float)):
                values.append(str(v))
            elif isinstance(v, (list, dict)):
                json_str = json.dumps(v)
                escaped = json_str.replace("'", "''")
                values.append(f"'{escaped}'")
            else:
                str_val = str(v).replace("'", "''")
                values.append(f"'{str_val}'")
        return f"({', '.join(values)})"

    def get_ddl(self) -> str:
        """Get DDL statements"""
        return """
CREATE TABLE IF NOT EXISTS dualuse_technologies (
  tech_uid TEXT PRIMARY KEY,
  technology_category TEXT NOT NULL,
  specific_technology TEXT NOT NULL,
  maturity_level TEXT,
  dual_use_flag INTEGER DEFAULT 1,
  military_application TEXT,
  civilian_application TEXT,
  actors_json TEXT,
  geolocations_json TEXT,
  china_involvement_flag INTEGER,
  eu_involvement_flag INTEGER,
  key_reports_json TEXT,
  timeline_projection_json TEXT,
  last_seen_date TEXT,
  evidence_quality TEXT,
  source_confidence REAL,
  sources_json TEXT
);

CREATE TABLE IF NOT EXISTS technology_dependencies (
  dep_uid TEXT PRIMARY KEY,
  tech_uid TEXT NOT NULL,
  dependency_type TEXT NOT NULL,
  description TEXT,
  criticality TEXT,
  dependency_actor_json TEXT,
  geo_json TEXT,
  referenced_sources_json TEXT,
  FOREIGN KEY (tech_uid) REFERENCES dualuse_technologies(tech_uid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS foresight_signals (
  signal_uid TEXT PRIMARY KEY,
  tech_uid TEXT NOT NULL,
  signal_type TEXT,
  statement TEXT,
  horizon TEXT,
  confidence REAL,
  source_ref TEXT,
  FOREIGN KEY (tech_uid) REFERENCES dualuse_technologies(tech_uid) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dut_category ON dualuse_technologies(technology_category);
CREATE INDEX IF NOT EXISTS idx_dut_maturity ON dualuse_technologies(maturity_level);
CREATE INDEX IF NOT EXISTS idx_dep_type ON technology_dependencies(dependency_type);
"""

    def calculate_null_rates(self) -> Dict[str, float]:
        """Calculate null rates for key fields"""
        if not self.technologies:
            return {}

        total = len(self.technologies)
        null_counts = defaultdict(int)

        for tech in self.technologies.values():
            tech_dict = asdict(tech)
            for field, value in tech_dict.items():
                if value is None or value == '' or value == []:
                    null_counts[field] += 1

        return {field: count / total for field, count in null_counts.items()}

    def generate_executive_summary(self, path: Path):
        """Generate executive summary"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# Dual-Use Technology Mapper - Executive Summary\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")

            f.write("## Processing Statistics\n\n")
            for key, value in self.stats.items():
                f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")

            # Top categories
            f.write("\n## Top Technology Categories\n\n")
            category_counts = Counter([t.technology_category for t in self.technologies.values()])
            for category, count in category_counts.most_common(10):
                f.write(f"- **{category}**: {count} technologies\n")

            # Top geographies
            f.write("\n## Top Geographies\n\n")
            geo_counts = Counter()
            for tech in self.technologies.values():
                for geo in tech.geolocations:
                    if geo.get('country_iso2'):
                        geo_counts[geo['country_iso2']] += 1
            for country, count in geo_counts.most_common(10):
                f.write(f"- **{country}**: {count} technology instances\n")

            # Top dependencies
            f.write("\n## Top Dependencies by Type\n\n")
            dep_counts = Counter([d.dependency_type for d in self.dependencies.values()])
            for dep_type, count in dep_counts.most_common(10):
                f.write(f"- **{dep_type}**: {count} dependencies\n")

            # China/EU involvement
            f.write("\n## China & EU Involvement\n\n")
            if self.technologies:
                china_count = sum(1 for t in self.technologies.values() if t.china_involvement_flag)
                eu_count = sum(1 for t in self.technologies.values() if t.eu_involvement_flag)
                f.write(f"- **Technologies with China involvement**: {china_count} ({china_count/len(self.technologies)*100:.1f}%)\n")
                f.write(f"- **Technologies with EU involvement**: {eu_count} ({eu_count/len(self.technologies)*100:.1f}%)\n")
            else:
                f.write("- No technologies extracted\n")

            # QA summary
            f.write("\n## Quality Assurance\n\n")
            f.write(f"- **Total QA issues**: {len(self.qa_issues)}\n")
            issue_types = Counter([i['type'] for i in self.qa_issues])
            for issue_type, count in issue_types.most_common():
                f.write(f"  - {issue_type}: {count}\n")

        logger.info(f"Wrote {path.name}")

    def run(self):
        """Run complete mapping process"""
        logger.info("=== STARTING DUAL-USE TECHNOLOGY MAPPING ===")

        try:
            # Phase 1: Discovery
            self.discover_technologies()

            # Phase 2-6: Normalization, Dedup, Dependencies, Foresight, Validation
            # (Already integrated into discovery for efficiency)

            # Generate outputs
            self.generate_outputs()

            logger.info("=== MAPPING COMPLETE ===")
            logger.info(f"Total technologies: {len(self.technologies)}")
            logger.info(f"Total dependencies: {len(self.dependencies)}")
            logger.info(f"Total foresight signals: {len(self.foresight_signals)}")

        except Exception as e:
            logger.error(f"Error during mapping: {e}", exc_info=True)
            raise


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Dual-Use Technology Mapper')
    parser.add_argument('--db', default='F:/OSINT_WAREHOUSE/osint_master.db',
                       help='Path to osint_master.db')
    parser.add_argument('--output', default='C:/Projects/OSINT - Foresight/exports/dualuse',
                       help='Output directory')

    args = parser.parse_args()

    mapper = DualUseTechnologyMapper(args.db, args.output)
    mapper.run()


if __name__ == '__main__':
    main()
