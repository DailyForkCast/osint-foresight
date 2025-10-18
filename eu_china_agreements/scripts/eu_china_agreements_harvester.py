#!/usr/bin/env python3
"""
EU-China Agreements Harvester v1.0
Comprehensive crawler for EU-China bilateral agreements, treaties, MoUs, and partnerships
"""

import json
import os
import sys
import time
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, urljoin
import re

# For web scraping
import requests
from bs4 import BeautifulSoup
import pdfplumber

# For text processing
from difflib import SequenceMatcher
from rapidfuzz import fuzz
import langdetect

# For data storage
import sqlite3
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eu_china_harvester.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Agreement:
    """Data model for agreements matching the schema"""
    agreement_id: str
    title_en: Optional[str]
    title_native: Optional[str]
    country: str
    subnational_party: Optional[str]
    cn_party: Optional[str]
    type: str
    sector: str
    date_signed: Optional[str]
    date_effective: Optional[str]
    status: str
    status_basis: Optional[str]
    jurisdiction_level: str
    sources: List[str]
    source_confidence: str
    summary: Optional[str]
    last_seen: str
    notes: Optional[str]
    raw_text: Optional[str]

    def to_dict(self):
        return asdict(self)

class SearchQueryGenerator:
    """Generate search queries for different countries and languages"""

    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def generate_queries(self, country_code: str) -> List[Dict[str, Any]]:
        """Generate all search queries for a country"""
        if country_code not in self.config['countries']:
            raise ValueError(f"Country {country_code} not in configuration")

        country = self.config['countries'][country_code]
        queries = []

        # Generate queries for each language
        for lang in country['languages']:
            terms = country['search_terms'][lang]

            # Official domain queries
            for domain in country['official_domains']:
                for term in terms[:5]:  # Limit terms to avoid too many queries
                    query = {
                        'query': f'site:{domain} "{term}" China OR PRC 2000..2025',
                        'language': lang,
                        'domain': domain,
                        'type': 'official',
                        'country': country_code
                    }
                    queries.append(query)

            # Municipal queries
            if country.get('municipal_pattern'):
                for term in ['sister city', 'twinning', 'partnership']:
                    native_term = self._translate_term(term, lang, country)
                    if native_term:
                        query = {
                            'query': f'site:{country["municipal_pattern"]} "{native_term}" China',
                            'language': lang,
                            'type': 'municipal',
                            'country': country_code
                        }
                        queries.append(query)

            # University queries
            if country.get('university_pattern'):
                for term in ['memorandum', 'cooperation', 'exchange']:
                    native_term = self._translate_term(term, lang, country)
                    if native_term:
                        query = {
                            'query': f'site:{country["university_pattern"]} "{native_term}" China',
                            'language': lang,
                            'type': 'university',
                            'country': country_code
                        }
                        queries.append(query)

        # Chinese side queries
        chinese_embassy = self.config['chinese_sources']['embassies'].get(country_code)
        if chinese_embassy:
            query = {
                'query': f'site:{chinese_embassy} agreement OR 协议',
                'language': 'zh',
                'type': 'chinese_embassy',
                'country': country_code
            }
            queries.append(query)

        return queries

    def _translate_term(self, term: str, lang: str, country: Dict) -> Optional[str]:
        """Simple term translation helper"""
        term_map = {
            'sister city': {
                'it': 'gemellaggio',
                'de': 'Städtepartnerschaft',
                'fr': 'jumelage',
                'pl': 'partnerstwo miast',
                'es': 'hermanamiento'
            },
            'memorandum': {
                'it': 'memorandum',
                'de': 'Absichtserklärung',
                'fr': 'mémorandum',
                'pl': 'memorandum',
                'es': 'memorando'
            },
            'cooperation': {
                'it': 'cooperazione',
                'de': 'Kooperation',
                'fr': 'coopération',
                'pl': 'współpraca',
                'es': 'cooperación'
            }
        }

        if term in term_map and lang in term_map[term]:
            return term_map[term][lang]
        return None

class AgreementExtractor:
    """Extract agreement information from web pages and PDFs"""

    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # Compile regex patterns
        self.date_pattern = re.compile(
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b|\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b'
        )
        self.status_patterns = {}
        for country_code in self.config['countries']:
            country = self.config['countries'][country_code]
            self.status_patterns[country_code] = {
                status: re.compile('|'.join(keywords), re.IGNORECASE)
                for status, keywords in country.get('status_keywords', {}).items()
            }

    def extract_from_html(self, html: str, url: str, country_code: str) -> Optional[Agreement]:
        """Extract agreement data from HTML"""
        soup = BeautifulSoup(html, 'html.parser')

        # Extract text
        text = soup.get_text(separator=' ', strip=True)

        # Detect language
        try:
            lang = langdetect.detect(text[:1000])
        except:
            lang = 'unknown'

        # Extract title
        title_native = self._extract_title(soup, lang)
        title_en = self._translate_title(title_native, lang) if lang != 'en' else title_native

        # Extract dates
        dates = self._extract_dates(text)
        date_signed = dates[0] if dates else None
        date_effective = dates[1] if len(dates) > 1 else date_signed

        # Extract parties
        parties = self._extract_parties(text, country_code)

        # Detect agreement type
        agreement_type = self._detect_type(text, country_code)

        # Detect sector
        sector = self._detect_sector(text)

        # Extract status
        status, status_basis = self._extract_status(text, country_code)

        # Determine jurisdiction level
        jurisdiction_level = self._determine_jurisdiction(url, parties.get('subnational'))

        # Create agreement object
        agreement = Agreement(
            agreement_id=str(uuid.uuid4()),
            title_en=title_en,
            title_native=title_native,
            country=country_code,
            subnational_party=parties.get('subnational'),
            cn_party=parties.get('chinese'),
            type=agreement_type,
            sector=sector,
            date_signed=date_signed,
            date_effective=date_effective,
            status=status,
            status_basis=status_basis,
            jurisdiction_level=jurisdiction_level,
            sources=[url],
            source_confidence=self._assess_confidence(url),
            summary=self._generate_summary(text, title_native),
            last_seen=datetime.now().isoformat(),
            notes=None,
            raw_text=text[:5000]  # Store first 5000 chars
        )

        return agreement

    def extract_from_pdf(self, pdf_path: str, url: str, country_code: str) -> Optional[Agreement]:
        """Extract agreement data from PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ''
                for page in pdf.pages[:10]:  # Read first 10 pages
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'

                if text:
                    # Create fake HTML for consistent processing
                    html = f'<html><body>{text}</body></html>'
                    return self.extract_from_html(html, url, country_code)
        except Exception as e:
            logger.error(f"Error extracting from PDF {pdf_path}: {e}")

        return None

    def _extract_title(self, soup: BeautifulSoup, lang: str) -> str:
        """Extract title from HTML"""
        # Try standard title tags
        title = soup.find('title')
        if title:
            return title.get_text(strip=True)

        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        # Try meta description
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            return meta.get('content', '')

        return "Untitled Agreement"

    def _translate_title(self, title: str, lang: str) -> str:
        """Placeholder for title translation"""
        # In production, use a translation API
        return title

    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        dates = []
        matches = self.date_pattern.findall(text)

        for match in matches[:5]:  # Limit to first 5 dates
            if match[0]:  # DD/MM/YYYY format
                date = f"{match[2]}-{match[1]:0>2}-{match[0]:0>2}"
            else:  # YYYY/MM/DD format
                date = f"{match[3]}-{match[4]:0>2}-{match[5]:0>2}"

            # Validate date
            try:
                datetime.strptime(date, '%Y-%m-%d')
                dates.append(date)
            except:
                continue

        return sorted(list(set(dates)))

    def _extract_parties(self, text: str, country_code: str) -> Dict[str, str]:
        """Extract parties from text"""
        parties = {}

        # Look for Chinese entities
        chinese_entities = [
            'People\'s Republic of China', 'PRC', 'China',
            '中华人民共和国', '中国',
            'Chinese Ministry', 'Chinese Government',
            'Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen'
        ]

        for entity in chinese_entities:
            if entity in text:
                parties['chinese'] = entity
                break

        # Look for subnational entities
        country = self.config['countries'][country_code]
        if country_code == 'IT':
            cities = ['Roma', 'Milano', 'Napoli', 'Torino', 'Venezia', 'Firenze']
            regions = ['Lombardia', 'Lazio', 'Campania', 'Veneto', 'Toscana']
        elif country_code == 'DE':
            cities = ['Berlin', 'München', 'Hamburg', 'Frankfurt', 'Köln']
            regions = ['Bayern', 'Nordrhein-Westfalen', 'Baden-Württemberg']
        elif country_code == 'FR':
            cities = ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice']
            regions = ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Nouvelle-Aquitaine']
        elif country_code == 'PL':
            cities = ['Warszawa', 'Kraków', 'Łódź', 'Wrocław', 'Poznań']
            regions = ['Mazowieckie', 'Małopolskie', 'Wielkopolskie']
        elif country_code == 'ES':
            cities = ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao']
            regions = ['Cataluña', 'Andalucía', 'Comunidad de Madrid']
        else:
            cities = []
            regions = []

        for city in cities:
            if city in text:
                parties['subnational'] = city
                break

        if 'subnational' not in parties:
            for region in regions:
                if region in text:
                    parties['subnational'] = region
                    break

        return parties

    def _detect_type(self, text: str, country_code: str) -> str:
        """Detect agreement type"""
        country = self.config['countries'][country_code]
        type_mapping = country.get('type_mapping', {})

        text_lower = text.lower()
        for native_term, agreement_type in type_mapping.items():
            if native_term.lower() in text_lower:
                return agreement_type

        # Default fallback
        if 'memorandum' in text_lower or 'mou' in text_lower:
            return 'MoU'
        elif 'treaty' in text_lower or 'agreement' in text_lower:
            return 'treaty'
        elif 'sister' in text_lower or 'twinning' in text_lower:
            return 'sister_city'

        return 'unknown'

    def _detect_sector(self, text: str) -> str:
        """Detect agreement sector"""
        text_lower = text.lower()
        sector_scores = {}

        for sector, keywords in self.config['sector_keywords'].items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if score > 0:
                sector_scores[sector] = score

        if sector_scores:
            return max(sector_scores, key=sector_scores.get)

        return 'other'

    def _extract_status(self, text: str, country_code: str) -> Tuple[str, Optional[str]]:
        """Extract agreement status"""
        if country_code not in self.status_patterns:
            return 'unknown', None

        patterns = self.status_patterns[country_code]

        for status, pattern in patterns.items():
            match = pattern.search(text)
            if match:
                # Extract surrounding context
                start = max(0, match.start() - 60)
                end = min(len(text), match.end() + 60)
                context = text[start:end].strip()
                return status, context

        return 'unknown', None

    def _determine_jurisdiction(self, url: str, subnational: Optional[str]) -> str:
        """Determine jurisdiction level"""
        url_lower = url.lower()

        if any(term in url_lower for term in ['ministry', 'government', 'gov', 'stato']):
            return 'national'
        elif any(term in url_lower for term in ['region', 'province', 'land', 'département']):
            return 'regional'
        elif any(term in url_lower for term in ['city', 'comune', 'stadt', 'ville']):
            return 'municipal'
        elif any(term in url_lower for term in ['university', 'uni', 'edu']):
            return 'institution'
        elif subnational:
            return 'municipal'

        return 'national'

    def _assess_confidence(self, url: str) -> str:
        """Assess source confidence based on URL"""
        domain = urlparse(url).netloc.lower()

        # High confidence for official domains
        official_domains = []
        for country in self.config['countries'].values():
            official_domains.extend(country['official_domains'])

        if any(official in domain for official in official_domains):
            return 'high'

        # Medium confidence for known news/academic sources
        if any(term in domain for term in ['reuters', 'bloomberg', 'ft.com', 'edu', 'ac.']):
            return 'medium'

        return 'low'

    def _generate_summary(self, text: str, title: str) -> str:
        """Generate a brief summary"""
        # Simple extractive summary - take first 2-3 sentences
        sentences = text.split('.')[:3]
        summary = '. '.join(sentences).strip()

        if len(summary) > 300:
            summary = summary[:297] + '...'

        return summary or f"Agreement: {title}"

class DeduplicationEngine:
    """Deduplicate and link similar agreements"""

    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold

    def find_duplicates(self, agreements: List[Agreement]) -> List[List[Agreement]]:
        """Find duplicate agreement clusters"""
        clusters = []
        processed = set()

        for i, agreement1 in enumerate(agreements):
            if i in processed:
                continue

            cluster = [agreement1]
            processed.add(i)

            for j, agreement2 in enumerate(agreements[i+1:], i+1):
                if j in processed:
                    continue

                if self._are_similar(agreement1, agreement2):
                    cluster.append(agreement2)
                    processed.add(j)

            if len(cluster) > 1:
                clusters.append(cluster)

        return clusters

    def merge_agreements(self, cluster: List[Agreement]) -> Agreement:
        """Merge a cluster of duplicate agreements"""
        # Sort by source confidence
        confidence_order = {'high': 3, 'medium': 2, 'low': 1}
        cluster.sort(key=lambda a: confidence_order.get(a.source_confidence, 0), reverse=True)

        # Use highest confidence as base
        merged = cluster[0]

        # Combine sources
        all_sources = []
        for agreement in cluster:
            all_sources.extend(agreement.sources)
        merged.sources = list(set(all_sources))

        # Merge missing fields
        for agreement in cluster[1:]:
            if not merged.title_en and agreement.title_en:
                merged.title_en = agreement.title_en
            if not merged.date_signed and agreement.date_signed:
                merged.date_signed = agreement.date_signed
            if not merged.cn_party and agreement.cn_party:
                merged.cn_party = agreement.cn_party
            if merged.status == 'unknown' and agreement.status != 'unknown':
                merged.status = agreement.status
                merged.status_basis = agreement.status_basis

        return merged

    def _are_similar(self, agreement1: Agreement, agreement2: Agreement) -> bool:
        """Check if two agreements are similar enough to be duplicates"""
        # Country must match
        if agreement1.country != agreement2.country:
            return False

        # Check title similarity
        title1 = agreement1.title_native or agreement1.title_en or ''
        title2 = agreement2.title_native or agreement2.title_en or ''

        if title1 and title2:
            title_similarity = fuzz.ratio(title1.lower(), title2.lower()) / 100
            if title_similarity < 0.7:
                return False

        # Check date proximity (within 30 days)
        if agreement1.date_signed and agreement2.date_signed:
            try:
                date1 = datetime.fromisoformat(agreement1.date_signed)
                date2 = datetime.fromisoformat(agreement2.date_signed)
                if abs((date1 - date2).days) > 30:
                    return False
            except:
                pass

        # Check party overlap
        if agreement1.cn_party and agreement2.cn_party:
            party_similarity = fuzz.ratio(
                agreement1.cn_party.lower(),
                agreement2.cn_party.lower()
            ) / 100
            if party_similarity > self.similarity_threshold:
                return True

        # Check URL overlap
        urls1 = set(agreement1.sources)
        urls2 = set(agreement2.sources)
        if urls1 & urls2:
            return True

        # Final title check with high threshold
        if title1 and title2:
            return title_similarity > self.similarity_threshold

        return False

class ValidationEngine:
    """Validate and QA agreements"""

    def __init__(self):
        self.issues = []

    def validate(self, agreement: Agreement) -> Tuple[bool, List[str]]:
        """Validate an agreement and return issues"""
        issues = []

        # Date validation
        if agreement.date_signed and agreement.date_effective:
            try:
                signed = datetime.fromisoformat(agreement.date_signed)
                effective = datetime.fromisoformat(agreement.date_effective)
                if effective < signed:
                    issues.append("Effective date before signed date")
            except:
                issues.append("Invalid date format")

        # Status validation
        if agreement.status == 'active' and agreement.date_effective:
            try:
                effective = datetime.fromisoformat(agreement.date_effective)
                if effective > datetime.now():
                    issues.append("Active status but future effective date")
            except:
                pass

        # Source validation
        if not agreement.sources:
            issues.append("No sources provided")

        # Required fields
        if not agreement.title_en and not agreement.title_native:
            issues.append("No title provided")

        if not agreement.country:
            issues.append("No country specified")

        # Conflicting status
        if agreement.status == 'terminated' and not agreement.status_basis:
            issues.append("Terminated status without basis")

        self.issues.extend(issues)
        return len(issues) == 0, issues

    def generate_qa_report(self, agreements: List[Agreement]) -> Dict:
        """Generate QA report for agreements"""
        report = {
            'total_agreements': len(agreements),
            'validation_issues': self.issues,
            'coverage': {},
            'status_distribution': {},
            'type_distribution': {},
            'confidence_distribution': {},
            'date_coverage': {}
        }

        # Calculate distributions
        for agreement in agreements:
            # Country coverage
            country = agreement.country
            if country not in report['coverage']:
                report['coverage'][country] = {
                    'total': 0,
                    'national': 0,
                    'regional': 0,
                    'municipal': 0,
                    'institution': 0
                }
            report['coverage'][country]['total'] += 1
            report['coverage'][country][agreement.jurisdiction_level] += 1

            # Status distribution
            status = agreement.status
            report['status_distribution'][status] = report['status_distribution'].get(status, 0) + 1

            # Type distribution
            agreement_type = agreement.type
            report['type_distribution'][agreement_type] = report['type_distribution'].get(agreement_type, 0) + 1

            # Confidence distribution
            confidence = agreement.source_confidence
            report['confidence_distribution'][confidence] = report['confidence_distribution'].get(confidence, 0) + 1

            # Date coverage
            if agreement.date_signed:
                try:
                    year = agreement.date_signed[:4]
                    report['date_coverage'][year] = report['date_coverage'].get(year, 0) + 1
                except:
                    pass

        # Calculate KPIs
        report['kpis'] = {
            'precision_at_official': self._calculate_precision(agreements),
            'status_clarity_rate': self._calculate_status_clarity(agreements),
            'date_completeness': self._calculate_date_completeness(agreements)
        }

        return report

    def _calculate_precision(self, agreements: List[Agreement]) -> float:
        """Calculate precision at official sources"""
        high_confidence = sum(1 for a in agreements if a.source_confidence == 'high')
        return high_confidence / len(agreements) if agreements else 0

    def _calculate_status_clarity(self, agreements: List[Agreement]) -> float:
        """Calculate status clarity rate"""
        known_status = sum(1 for a in agreements if a.status != 'unknown')
        return known_status / len(agreements) if agreements else 0

    def _calculate_date_completeness(self, agreements: List[Agreement]) -> float:
        """Calculate date completeness"""
        with_dates = sum(1 for a in agreements if a.date_signed or a.date_effective)
        return with_dates / len(agreements) if agreements else 0

class EUChinaAgreementsHarvester:
    """Main harvester orchestrator"""

    def __init__(self, config_path: str, output_dir: str):
        self.config_path = config_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.query_generator = SearchQueryGenerator(config_path)
        self.extractor = AgreementExtractor(config_path)
        self.deduplicator = DeduplicationEngine()
        self.validator = ValidationEngine()

        # Session for web requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def harvest_country(self, country_code: str, limit: int = 100):
        """Harvest agreements for a specific country"""
        logger.info(f"Starting harvest for {country_code}")

        # Create country output directory
        country_dir = self.output_dir / 'agreements' / country_code
        raw_dir = country_dir / 'raw'
        raw_dir.mkdir(parents=True, exist_ok=True)

        # Generate queries
        queries = self.query_generator.generate_queries(country_code)
        logger.info(f"Generated {len(queries)} queries for {country_code}")

        # Collect agreements
        agreements = []
        processed_urls = set()

        for query in queries[:limit]:  # Limit for pilot
            results = self._execute_search(query)

            for result in results:
                url = result['url']
                if url in processed_urls:
                    continue
                processed_urls.add(url)

                # Fetch and extract
                content = self._fetch_content(url)
                if content:
                    # Save raw content
                    raw_file = self._save_raw(content, url, raw_dir)

                    # Extract agreement
                    agreement = self.extractor.extract_from_html(
                        content, url, country_code
                    )

                    if agreement:
                        # Validate
                        is_valid, issues = self.validator.validate(agreement)
                        if not is_valid:
                            logger.warning(f"Validation issues for {url}: {issues}")

                        agreements.append(agreement)

                # Rate limiting
                time.sleep(1)

        logger.info(f"Extracted {len(agreements)} agreements for {country_code}")

        # Deduplicate
        if agreements:
            clusters = self.deduplicator.find_duplicates(agreements)
            logger.info(f"Found {len(clusters)} duplicate clusters")

            # Merge duplicates
            for cluster in clusters:
                merged = self.deduplicator.merge_agreements(cluster)
                # Replace cluster with merged
                for agreement in cluster:
                    if agreement in agreements:
                        agreements.remove(agreement)
                agreements.append(merged)

        # Save agreements
        output_file = country_dir / 'agreements.ndjson'
        with open(output_file, 'w', encoding='utf-8') as f:
            for agreement in agreements:
                json.dump(agreement.to_dict(), f, ensure_ascii=False)
                f.write('\n')

        logger.info(f"Saved {len(agreements)} agreements to {output_file}")

        # Generate QA report
        qa_report = self.validator.generate_qa_report(agreements)
        report_file = self.output_dir / 'logs' / f'{country_code}_coverage.json'
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(qa_report, f, indent=2, ensure_ascii=False)

        logger.info(f"Generated QA report: {report_file}")

        return agreements

    def _execute_search(self, query: Dict) -> List[Dict]:
        """Execute a search query (placeholder - needs search API integration)"""
        # In production, integrate with search API or Selenium for scraping
        # For now, return empty results
        logger.info(f"Would execute query: {query['query']}")
        return []

    def _fetch_content(self, url: str) -> Optional[str]:
        """Fetch content from URL"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _save_raw(self, content: str, url: str, raw_dir: Path) -> Path:
        """Save raw content to file"""
        # Generate filename from URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()
        filename = raw_dir / f"{url_hash}.html"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        return filename

    def run_pilot(self, countries: List[str] = None):
        """Run pilot harvest for specified countries"""
        if not countries:
            countries = ['IT', 'DE', 'FR', 'PL', 'ES']

        logger.info(f"Starting pilot harvest for {countries}")

        all_agreements = {}

        for country in countries:
            agreements = self.harvest_country(country, limit=10)  # Small limit for pilot
            all_agreements[country] = agreements

        # Generate combined report
        self._generate_combined_report(all_agreements)

        logger.info("Pilot harvest complete")

        return all_agreements

    def _generate_combined_report(self, all_agreements: Dict[str, List[Agreement]]):
        """Generate combined report for all countries"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'countries': {},
            'totals': {
                'agreements': 0,
                'high_confidence': 0,
                'with_dates': 0,
                'active': 0
            }
        }

        for country, agreements in all_agreements.items():
            report['countries'][country] = {
                'total': len(agreements),
                'by_type': {},
                'by_status': {},
                'by_jurisdiction': {}
            }

            for agreement in agreements:
                # Update country stats
                type_key = agreement.type
                report['countries'][country]['by_type'][type_key] = \
                    report['countries'][country]['by_type'].get(type_key, 0) + 1

                status_key = agreement.status
                report['countries'][country]['by_status'][status_key] = \
                    report['countries'][country]['by_status'].get(status_key, 0) + 1

                jurisdiction_key = agreement.jurisdiction_level
                report['countries'][country]['by_jurisdiction'][jurisdiction_key] = \
                    report['countries'][country]['by_jurisdiction'].get(jurisdiction_key, 0) + 1

                # Update totals
                report['totals']['agreements'] += 1
                if agreement.source_confidence == 'high':
                    report['totals']['high_confidence'] += 1
                if agreement.date_signed or agreement.date_effective:
                    report['totals']['with_dates'] += 1
                if agreement.status == 'active':
                    report['totals']['active'] += 1

        # Save report
        report_file = self.output_dir / 'logs' / 'pilot_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Generated combined report: {report_file}")

def main():
    """Main entry point"""
    # Setup paths
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / 'config' / 'countries.json'
    output_dir = base_dir / 'out'

    # Create harvester
    harvester = EUChinaAgreementsHarvester(str(config_path), str(output_dir))

    # Run pilot for Italy first
    logger.info("Starting pilot harvest for Italy")
    agreements = harvester.harvest_country('IT', limit=5)

    if agreements:
        logger.info(f"Successfully harvested {len(agreements)} agreements for Italy")
        logger.info("Sample agreement:")
        logger.info(json.dumps(agreements[0].to_dict(), indent=2, ensure_ascii=False))
    else:
        logger.info("No agreements found in pilot - this is expected without search API integration")

    # Generate report
    logger.info("Pilot complete. Check logs for details.")

if __name__ == "__main__":
    main()
