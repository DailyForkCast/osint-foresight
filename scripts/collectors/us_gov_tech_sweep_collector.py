#!/usr/bin/env python3
"""
U.S. Government Technology Sweep Collector
Fast-Path: Laws & Regulations (Last 5 Years)

Collects from:
1. Federal Register API (rules & notices)
2. Regulations.gov API (dockets & documents)
3. Congress.gov / govinfo (Public Laws)

Purpose: Build comprehensive knowledge database of U.S. government tech policy
"""

import requests
import json
import hashlib
import re
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from collections import Counter
import logging
import time

# Try to load .env.local file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Load from .env.local (project standard)
    load_dotenv('.env.local')
    # Also try .env as fallback
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use environment variables directly

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Time window: Last 10 years
DATE_START = (datetime.now() - timedelta(days=10*365)).strftime('%Y-%m-%d')
DATE_END = datetime.now().strftime('%Y-%m-%d')

# Topic keywords (OR logic, case-insensitive)
TECH_KEYWORDS = [
    "advanced technology", "emerging technology", "dual-use", "AI",
    "artificial intelligence", "foundation model", "machine learning",
    "quantum", "semiconductor", "microelectronics", "chip", "space", "LEO",
    "biotechnology", "biosecurity", "advanced materials", "robotics", "autonomy",
    "cybersecurity", "HPC", "photonic", "sensing", "additive manufacturing",
    "3D printing", "navigation", "timing", "GNSS", "PNT", "critical mineral",
    "rare earth", "export control", "ECCN", "EAR", "ITAR", "supply chain",
    "standards", "6G", "Open RAN"
]

# Agency filters - mapping abbreviations to Federal Register API slugs
AGENCY_SLUGS = {
    'NIST': 'national-institute-of-standards-and-technology',
    'BIS': 'industry-and-security-bureau',
    'NTIA': 'national-telecommunications-and-information-administration',
    'FCC': 'federal-communications-commission',
    'FTC': 'federal-trade-commission',
    'DOE': 'energy-department',
    'DHS': 'homeland-security-department',
    'CISA': 'cybersecurity-and-infrastructure-security-agency',
    'State': 'state-department',
    'Treasury': 'treasury-department',
    'USTR': 'trade-representative-office-of-the-united-states',
    'NASA': 'national-aeronautics-and-space-administration',
    'NSF': 'national-science-foundation',
    'DoD': 'defense-department',
    'Commerce': 'commerce-department'
}

# API endpoints
FEDERAL_REGISTER_API = "https://www.federalregister.gov/api/v1"
REGULATIONS_GOV_API = "https://api.regulations.gov/v4"
CONGRESS_GOV_API = "https://api.congress.gov/v3"

# API keys (read from environment variables or .env file)
REGULATIONS_GOV_API_KEY = os.getenv('REGULATIONS_GOV_API_KEY')
CONGRESS_GOV_API_KEY = os.getenv('CONGRESS_GOV_API_KEY')

# Output directory - save to F drive for large-scale storage
OUTPUT_DIR = Path("F:/OSINT_DATA/us_gov_tech_sweep")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class DocumentMetadata:
    """Standardized document metadata"""
    # Core fields
    title: str
    publisher_org: str
    publisher_type: str
    document_type: str
    publication_date_iso: str
    year: int
    month: int
    day: int
    canonical_url: str
    download_url: Optional[str]
    language: str = "en"
    pages: Optional[int] = None
    authors: Optional[str] = None

    # Classification
    topics: List[str] = field(default_factory=list)
    subtopics: List[str] = field(default_factory=list)
    us_focus_flag: bool = True

    # Identifiers
    doc_number: Optional[str] = None
    collection: str = ""
    agency_bureau: Optional[str] = None

    # Content
    summary: Optional[str] = None
    citation_suggested: Optional[str] = None

    # Regulatory-specific
    rin: Optional[str] = None
    docket_id: Optional[str] = None
    fr_doc_number: Optional[str] = None
    cfr_citation: Optional[str] = None
    public_law_number: Optional[str] = None
    bill_number: Optional[str] = None
    statutes_at_large_citation: Optional[str] = None

    # File metadata
    saved_path: Optional[str] = None
    file_ext: Optional[str] = None
    file_size_bytes: Optional[int] = None
    hash_sha256: Optional[str] = None
    extraction_ok: bool = True
    extraction_notes: Optional[str] = None


# ============================================================================
# FAST-PATH A: FEDERAL REGISTER API
# ============================================================================

class FederalRegisterCollector:
    """Collector for Federal Register rules & notices"""

    def __init__(self):
        self.base_url = FEDERAL_REGISTER_API
        self.documents = []
        self.stats = Counter()

    def build_search_query(self) -> str:
        """Build search query from keywords"""
        # Federal Register API uses term parameter for text search
        return " OR ".join(f'"{kw}"' for kw in TECH_KEYWORDS[:10])  # Limit to avoid URL length

    def search_documents(self, start_date: str, end_date: str) -> List[Dict]:
        """Search Federal Register API"""
        logger.info("=== FEDERAL REGISTER API SEARCH ===")

        url = f"{self.base_url}/documents.json"

        all_results = []

        # Search by agency (Federal Register API uses slug identifiers)
        # Start with high-priority tech agencies
        priority_agencies = ['NIST', 'BIS', 'NTIA', 'FCC', 'DOE', 'NASA', 'NSF', 'CISA']

        for agency_abbr in priority_agencies:
            agency_slug = AGENCY_SLUGS.get(agency_abbr)
            if not agency_slug:
                logger.warning(f"No slug mapping for {agency_abbr}, skipping")
                continue

            logger.info(f"Searching {agency_abbr} ({agency_slug})...")

            # Build parameters using proper slug format
            params = {
                'conditions[publication_date][gte]': start_date,
                'conditions[publication_date][lte]': end_date,
                'conditions[agencies][]': [agency_slug],
                'conditions[type][]': ['RULE', 'PRORULE', 'NOTICE'],
                'per_page': 100,
                'page': 1,
                'order': 'newest'
            }

            try:
                while True:
                    logger.info(f"  Fetching {agency_abbr} page {params['page']}...")
                    response = requests.get(url, params=params, timeout=30)

                    if response.status_code != 200:
                        logger.error(f"  API error for {agency_abbr}: {response.status_code}")
                        if response.status_code == 400:
                            logger.error(f"  Response: {response.text[:200]}")
                        break

                    data = response.json()
                    results = data.get('results', [])

                    if not results:
                        break

                    # Filter by keywords in title/abstract
                    filtered_results = []
                    for doc in results:
                        text = f"{doc.get('title', '')} {doc.get('abstract', '')}".lower()
                        if any(kw.lower() in text for kw in TECH_KEYWORDS):
                            filtered_results.append(doc)

                    all_results.extend(filtered_results)
                    self.stats['api_calls'] += 1
                    self.stats['documents_found'] += len(results)
                    self.stats['documents_filtered'] += len(filtered_results)

                    logger.info(f"    Found {len(results)} docs, {len(filtered_results)} match keywords")

                    # Check if more pages
                    if len(results) < params['per_page']:
                        break

                    params['page'] += 1
                    time.sleep(0.5)  # Rate limiting

                    # Limit pages per agency
                    if params['page'] > 10:  # Max 1000 docs per agency
                        logger.warning(f"  Hit page limit for {agency_abbr}, moving to next agency")
                        break

            except Exception as e:
                logger.error(f"  Search error for {agency_abbr}: {e}")

        logger.info(f"Found {len(all_results)} documents")
        return all_results

    def parse_document(self, doc: Dict) -> DocumentMetadata:
        """Parse Federal Register document to standard metadata"""

        pub_date = doc.get('publication_date', '')
        if pub_date:
            dt = datetime.strptime(pub_date, '%Y-%m-%d')
            year, month, day = dt.year, dt.month, dt.day
        else:
            year = month = day = None

        # Determine document type
        doc_type = doc.get('type', '').lower()
        if doc_type in ['rule', 'final rule']:
            document_type = 'regulation'
        elif doc_type in ['proposed rule', 'prorule']:
            document_type = 'rule'
        else:
            document_type = 'notice'

        # Extract agency info
        agencies = doc.get('agencies', [])
        agency_names = [a.get('name', '') for a in agencies if isinstance(a, dict)]
        primary_agency = agency_names[0] if agency_names else None

        # Map to bureau abbreviation
        agency_bureau = self._map_agency_abbreviation(primary_agency)

        # Build metadata
        metadata = DocumentMetadata(
            title=doc.get('title', ''),
            publisher_org=primary_agency or 'Federal Government',
            publisher_type='government',
            document_type=document_type,
            publication_date_iso=pub_date,
            year=year,
            month=month,
            day=day,
            canonical_url=doc.get('html_url', ''),
            download_url=doc.get('pdf_url'),
            pages=None,  # Extract from PDF later
            authors=', '.join(agency_names) if len(agency_names) > 1 else None,
            topics=self._extract_topics(doc),
            subtopics=[],
            us_focus_flag=True,
            doc_number=doc.get('document_number'),
            collection='Federal Register',
            agency_bureau=agency_bureau,
            summary=doc.get('abstract'),
            citation_suggested=doc.get('citation'),
            fr_doc_number=doc.get('document_number'),
            rin=doc.get('regulation_id_number'),
            docket_id=self._extract_docket_id(doc),
            cfr_citation=self._extract_cfr_citation(doc)
        )

        return metadata

    def _map_agency_abbreviation(self, agency_name: Optional[str]) -> Optional[str]:
        """Map full agency name to abbreviation"""
        if not agency_name:
            return None

        mapping = {
            'National Institute of Standards and Technology': 'DOC/NIST',
            'Bureau of Industry and Security': 'DOC/BIS',
            'National Telecommunications and Information Administration': 'DOC/NTIA',
            'Federal Communications Commission': 'FCC',
            'Federal Trade Commission': 'FTC',
            'Department of Energy': 'DOE',
            'Department of Homeland Security': 'DHS',
            'Cybersecurity and Infrastructure Security Agency': 'DHS/CISA',
            'Department of State': 'State',
            'Department of the Treasury': 'Treasury',
            'Office of the United States Trade Representative': 'USTR',
            'National Aeronautics and Space Administration': 'NASA',
            'National Science Foundation': 'NSF',
            'Department of Defense': 'DoD'
        }

        for full_name, abbrev in mapping.items():
            if full_name.lower() in agency_name.lower():
                return abbrev

        return agency_name[:20]  # Fallback to truncated name

    def _extract_topics(self, doc: Dict) -> List[str]:
        """Extract topics from document"""
        topics = []

        # Check title and abstract
        text = f"{doc.get('title', '')} {doc.get('abstract', '')}".lower()

        # Match against keyword list
        for keyword in TECH_KEYWORDS:
            if keyword.lower() in text:
                topics.append(keyword)

        # Also add agency topics
        if doc.get('topics'):
            topics.extend(doc['topics'])

        return list(set(topics))[:10]  # Dedupe and limit

    def _extract_docket_id(self, doc: Dict) -> Optional[str]:
        """Extract docket ID if present"""
        # Check various fields
        if doc.get('docket_id'):
            return doc['docket_id']

        # Check in docket_ids array
        docket_ids = doc.get('docket_ids', [])
        if docket_ids:
            return docket_ids[0]

        return None

    def _extract_cfr_citation(self, doc: Dict) -> Optional[str]:
        """Extract CFR citation if present"""
        cfr_refs = doc.get('cfr_references', [])
        if cfr_refs:
            # Build citation from first reference
            ref = cfr_refs[0]
            if isinstance(ref, dict):
                title = ref.get('title')
                chapter = ref.get('chapter')
                if title and chapter:
                    return f"{title} CFR {chapter}"

        return None

    def collect(self) -> List[DocumentMetadata]:
        """Run full collection"""
        logger.info(f"Collecting Federal Register documents ({DATE_START} to {DATE_END})")

        raw_docs = self.search_documents(DATE_START, DATE_END)

        for doc in raw_docs:
            try:
                metadata = self.parse_document(doc)
                self.documents.append(metadata)
                self.stats['parsed'] += 1
            except Exception as e:
                logger.error(f"Parse error: {e}")
                self.stats['errors'] += 1

        logger.info(f"Collected {len(self.documents)} Federal Register documents")
        return self.documents


# ============================================================================
# FAST-PATH B: REGULATIONS.GOV API
# ============================================================================

class RegulationsGovCollector:
    """Collector for Regulations.gov dockets & documents"""

    def __init__(self, api_key: Optional[str] = None):
        self.base_url = REGULATIONS_GOV_API
        self.api_key = api_key or REGULATIONS_GOV_API_KEY
        self.documents = []
        self.stats = Counter()

        # Agency abbreviations for Regulations.gov
        self.agencies = ['NIST', 'BIS', 'NTIA', 'FCC', 'DOE', 'NASA', 'NSF', 'CISA']

    def search_dockets(self, start_date: str, end_date: str) -> List[Dict]:
        """Search for dockets matching our criteria"""
        logger.info("Searching Regulations.gov dockets...")

        all_dockets = []

        for agency in self.agencies:
            logger.info(f"Searching {agency} dockets...")

            # Search for dockets by agency and keywords
            for keyword in TECH_KEYWORDS[:10]:  # Limit to top keywords
                try:
                    url = f"{self.base_url}/dockets"
                    params = {
                        'filter[agencyId]': agency,
                        'filter[searchTerm]': keyword,
                        'filter[postedDate][ge]': start_date,
                        'filter[postedDate][le]': end_date,
                        'page[size]': 100,
                        'page[number]': 1,
                        'api_key': self.api_key
                    }

                    response = requests.get(url, params=params, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        dockets = data.get('data', [])
                        all_dockets.extend(dockets)
                        self.stats['api_calls'] += 1
                        self.stats['dockets_found'] += len(dockets)
                        logger.info(f"  {agency}/{keyword}: {len(dockets)} dockets")
                        time.sleep(0.5)  # Rate limiting
                    elif response.status_code == 429:
                        logger.warning(f"  Rate limit hit for {agency}, waiting...")
                        time.sleep(5)
                    else:
                        logger.error(f"  API error {response.status_code}")

                except Exception as e:
                    logger.error(f"  Search error for {agency}/{keyword}: {e}")

        logger.info(f"Found {len(all_dockets)} total dockets")
        return all_dockets

    def get_docket_documents(self, docket_id: str) -> List[Dict]:
        """Get all documents for a specific docket"""
        try:
            url = f"{self.base_url}/documents"
            params = {
                'filter[docketId]': docket_id,
                'page[size]': 100,
                'api_key': self.api_key
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Error fetching documents for {docket_id}: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error getting docket documents: {e}")
            return []

    def parse_document(self, doc: Dict, docket_id: Optional[str] = None) -> DocumentMetadata:
        """Parse Regulations.gov document to standard metadata"""

        attrs = doc.get('attributes', {})

        # Parse date
        posted_date = attrs.get('postedDate', '')
        if posted_date:
            dt = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
            year, month, day = dt.year, dt.month, dt.day
        else:
            year = month = day = None

        # Determine document type
        doc_type = attrs.get('documentType', '').lower()
        if 'rule' in doc_type:
            document_type = 'regulation' if 'final' in doc_type else 'rule'
        else:
            document_type = 'notice'

        # Get agency
        agency_id = attrs.get('agencyId', '')

        # Get file URLs
        file_formats = attrs.get('fileFormats', [])
        pdf_url = None
        for fmt in file_formats:
            if fmt.lower() == 'pdf':
                # Construct download URL
                doc_id = doc.get('id', '')
                pdf_url = f"{self.base_url}/documents/{doc_id}/download"

        metadata = DocumentMetadata(
            title=attrs.get('title', ''),
            publisher_org=agency_id or 'Federal Government',
            publisher_type='government',
            document_type=document_type,
            publication_date_iso=posted_date[:10] if posted_date else '',
            year=year,
            month=month,
            day=day,
            canonical_url=f"https://www.regulations.gov/document/{doc.get('id', '')}",
            download_url=pdf_url,
            topics=self._extract_topics(attrs),
            subtopics=[],
            us_focus_flag=True,
            doc_number=doc.get('id'),
            collection='Regulations.gov',
            agency_bureau=agency_id,
            summary=attrs.get('summary'),
            docket_id=docket_id or attrs.get('docketId')
        )

        return metadata

    def _extract_topics(self, attrs: Dict) -> List[str]:
        """Extract topics from document attributes"""
        topics = []

        # Check title and summary
        text = f"{attrs.get('title', '')} {attrs.get('summary', '')}".lower()

        for keyword in TECH_KEYWORDS:
            if keyword.lower() in text:
                topics.append(keyword)

        return list(set(topics))[:10]

    def collect(self) -> List[DocumentMetadata]:
        """Run full collection"""
        logger.info("=== REGULATIONS.GOV API COLLECTION ===")

        if not self.api_key:
            logger.warning("No Regulations.gov API key provided - skipping")
            logger.info("Get API key at: https://open.gsa.gov/api/regulationsgov/")
            return []

        logger.info(f"Collecting Regulations.gov documents ({DATE_START} to {DATE_END})")

        # Search for dockets
        dockets = self.search_dockets(DATE_START, DATE_END)

        # For each docket, get documents
        for docket in dockets[:50]:  # Limit to first 50 dockets to avoid overwhelming
            docket_id = docket.get('id')
            logger.info(f"Fetching documents for docket {docket_id}...")

            docs = self.get_docket_documents(docket_id)

            for doc in docs:
                try:
                    metadata = self.parse_document(doc, docket_id)
                    self.documents.append(metadata)
                    self.stats['parsed'] += 1
                except Exception as e:
                    logger.error(f"Parse error: {e}")
                    self.stats['errors'] += 1

            time.sleep(1)  # Rate limiting between dockets

        logger.info(f"Collected {len(self.documents)} Regulations.gov documents")
        return self.documents


# ============================================================================
# FAST-PATH C: CONGRESS.GOV / GOVINFO (PUBLIC LAWS)
# ============================================================================

class CongressGovCollector:
    """Collector for Congress.gov enacted laws"""

    def __init__(self, api_key: Optional[str] = None):
        self.base_url = CONGRESS_GOV_API
        self.api_key = api_key or CONGRESS_GOV_API_KEY
        self.documents = []
        self.stats = Counter()

    def search_public_laws(self, start_date: str, end_date: str) -> List[Dict]:
        """Search for enacted Public Laws"""
        logger.info("Searching Congress.gov for Public Laws...")

        all_laws = []

        # Congress.gov organizes by Congress number (e.g., 114th, 115th, etc.)
        # 2015-2025 covers congresses 114-119
        start_year = int(start_date[:4])
        end_year = int(end_date[:4])

        # Calculate congress numbers (new congress every 2 years, 114th started Jan 2015)
        start_congress = 114 + (start_year - 2015) // 2
        end_congress = 114 + (end_year - 2015) // 2 + 1

        for congress in range(start_congress, end_congress + 1):
            logger.info(f"Searching {congress}th Congress...")

            try:
                url = f"{self.base_url}/bill/{congress}"
                params = {
                    'format': 'json',
                    'limit': 250,
                    'offset': 0,
                    'api_key': self.api_key
                }

                while True:
                    response = requests.get(url, params=params, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        bills = data.get('bills', [])

                        # Filter for enacted laws only
                        for bill in bills:
                            if bill.get('latestAction', {}).get('actionCode') == 'E40000':
                                # This is an enacted law
                                all_laws.append(bill)

                        self.stats['api_calls'] += 1
                        self.stats['bills_checked'] += len(bills)

                        # Check if more results
                        if len(bills) < params['limit']:
                            break

                        params['offset'] += params['limit']
                        time.sleep(0.5)  # Rate limiting

                    elif response.status_code == 429:
                        logger.warning("Rate limit hit, waiting...")
                        time.sleep(5)
                    else:
                        logger.error(f"API error {response.status_code}")
                        break

            except Exception as e:
                logger.error(f"Search error for Congress {congress}: {e}")

        logger.info(f"Found {len(all_laws)} enacted laws")
        return all_laws

    def get_law_details(self, bill_type: str, bill_number: int, congress: int) -> Optional[Dict]:
        """Get detailed information about a specific law"""
        try:
            url = f"{self.base_url}/bill/{congress}/{bill_type}/{bill_number}"
            params = {
                'format': 'json',
                'api_key': self.api_key
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json().get('bill', {})
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting law details: {e}")
            return None

    def parse_law(self, bill: Dict) -> Optional[DocumentMetadata]:
        """Parse Congress.gov bill to standard metadata"""

        # Only process if it matches our tech keywords
        title = bill.get('title', '')
        summary_text = bill.get('summary', {}).get('text', '') if isinstance(bill.get('summary'), dict) else ''
        text_to_check = f"{title} {summary_text}".lower()

        # Check if matches any tech keywords
        if not any(kw.lower() in text_to_check for kw in TECH_KEYWORDS):
            return None

        # Parse date
        law_date = bill.get('becameLaw', {}).get('date', '') if isinstance(bill.get('becameLaw'), dict) else ''
        if law_date:
            try:
                dt = datetime.fromisoformat(law_date.replace('Z', '+00:00'))
                year, month, day = dt.year, dt.month, dt.day
            except:
                year = month = day = None
        else:
            year = month = day = None

        # Extract Public Law number
        public_law = bill.get('becameLaw', {}).get('publicLaw', '') if isinstance(bill.get('becameLaw'), dict) else ''

        # Build govinfo PDF URL
        if public_law:
            # Format: https://www.govinfo.gov/content/pkg/PLAW-{congress}publ{number}/pdf/PLAW-{congress}publ{number}.pdf
            pdf_url = f"https://www.govinfo.gov/content/pkg/{public_law}/pdf/{public_law}.pdf"
        else:
            pdf_url = None

        metadata = DocumentMetadata(
            title=title,
            publisher_org='U.S. Congress',
            publisher_type='congress',
            document_type='law',
            publication_date_iso=law_date[:10] if law_date else '',
            year=year,
            month=month,
            day=day,
            canonical_url=f"https://www.congress.gov/bill/{bill.get('congress', '')}-congress/"
                          f"{bill.get('type', '').lower()}/{bill.get('number', '')}",
            download_url=pdf_url,
            topics=self._extract_topics(bill),
            subtopics=[],
            us_focus_flag=True,
            doc_number=public_law,
            collection='Congress.gov',
            agency_bureau='Congress',
            summary=summary_text[:500] if summary_text else None,
            public_law_number=public_law,
            bill_number=f"{bill.get('type', '')}{bill.get('number', '')}"
        )

        return metadata

    def _extract_topics(self, bill: Dict) -> List[str]:
        """Extract topics from bill"""
        topics = []

        # Check title and summary
        title = bill.get('title', '')
        summary_text = bill.get('summary', {}).get('text', '') if isinstance(bill.get('summary'), dict) else ''
        text = f"{title} {summary_text}".lower()

        for keyword in TECH_KEYWORDS:
            if keyword.lower() in text:
                topics.append(keyword)

        return list(set(topics))[:10]

    def collect(self) -> List[DocumentMetadata]:
        """Run full collection"""
        logger.info("=== CONGRESS.GOV API COLLECTION ===")

        if not self.api_key:
            logger.warning("No Congress.gov API key provided - skipping")
            logger.info("Get API key at: https://api.congress.gov/sign-up/")
            return []

        logger.info(f"Collecting Congress.gov Public Laws ({DATE_START} to {DATE_END})")

        # Search for enacted laws
        laws = self.search_public_laws(DATE_START, DATE_END)

        # Parse each law
        for law in laws:
            try:
                metadata = self.parse_law(law)
                if metadata:  # Only add if it matches tech keywords
                    self.documents.append(metadata)
                    self.stats['parsed'] += 1
            except Exception as e:
                logger.error(f"Parse error: {e}")
                self.stats['errors'] += 1

        logger.info(f"Collected {len(self.documents)} Congress.gov laws")
        return self.documents


# ============================================================================
# SHARED: DOWNLOADER + HASHER
# ============================================================================

class DocumentDownloader:
    """Download and hash documents"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stats = Counter()

    def download_document(self, metadata: DocumentMetadata) -> DocumentMetadata:
        """Download document and compute hash"""

        if not metadata.download_url:
            metadata.extraction_notes = "No download URL available"
            return metadata

        try:
            # Build filename
            year = metadata.year or datetime.now().year
            collection_snake = metadata.collection.lower().replace(' ', '_')
            doc_num = metadata.doc_number or metadata.fr_doc_number or 'unknown'
            doc_num_clean = re.sub(r'[^\w\-]', '_', str(doc_num))

            # Get title slug
            title_slug = re.sub(r'[^\w\s-]', '', metadata.title[:40])
            title_slug = re.sub(r'[-\s]+', '_', title_slug).strip('_').lower()

            # Determine extension
            ext = 'pdf'
            if metadata.download_url.endswith('.html'):
                ext = 'html'
            elif metadata.download_url.endswith('.xml'):
                ext = 'xml'

            filename = f"{year}_{collection_snake}_{doc_num_clean}_{title_slug}.{ext}"
            filepath = self.output_dir / filename

            # Download
            response = requests.get(metadata.download_url, timeout=60, stream=True)
            response.raise_for_status()

            # Save file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Compute hash
            sha256_hash = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

            # Update metadata
            metadata.saved_path = str(filepath)
            metadata.file_ext = ext
            metadata.file_size_bytes = filepath.stat().st_size
            metadata.hash_sha256 = sha256_hash.hexdigest()
            metadata.extraction_ok = True

            # Try to get page count for PDFs
            if ext == 'pdf':
                try:
                    import PyPDF2
                    with open(filepath, 'rb') as f:
                        pdf = PyPDF2.PdfReader(f)
                        metadata.pages = len(pdf.pages)
                except:
                    pass

            self.stats['downloaded'] += 1
            logger.info(f"Downloaded: {filename}")

        except Exception as e:
            logger.error(f"Download error: {e}")
            metadata.extraction_ok = False
            metadata.extraction_notes = str(e)
            self.stats['download_errors'] += 1

        return metadata


# ============================================================================
# QA VALIDATION
# ============================================================================

class QAValidator:
    """Validate collected documents"""

    def __init__(self):
        self.issues = []
        self.stats = Counter()

    def validate_document(self, metadata: DocumentMetadata) -> List[str]:
        """Validate a single document"""
        issues = []

        # Check canonical URL resolves
        if metadata.canonical_url:
            try:
                response = requests.head(metadata.canonical_url, timeout=10, allow_redirects=True)
                if response.status_code >= 400:
                    issues.append({
                        'type': 'dead_link',
                        'field': 'canonical_url',
                        'value': metadata.canonical_url,
                        'doc_number': metadata.doc_number
                    })
            except:
                issues.append({
                    'type': 'dead_link',
                    'field': 'canonical_url',
                    'value': metadata.canonical_url,
                    'doc_number': metadata.doc_number
                })

        # Check for authoritative identifier
        has_identifier = any([
            metadata.public_law_number,
            metadata.fr_doc_number,
            metadata.rin,
            metadata.docket_id
        ])

        if not has_identifier and metadata.document_type in ['law', 'regulation', 'rule']:
            issues.append({
                'type': 'missing_identifier',
                'doc_number': metadata.doc_number,
                'document_type': metadata.document_type
            })

        # Validate enums
        valid_pub_types = ['government', 'congress']
        if metadata.publisher_type not in valid_pub_types:
            issues.append({
                'type': 'enum_unmapped',
                'field': 'publisher_type',
                'value': metadata.publisher_type,
                'doc_number': metadata.doc_number
            })

        valid_doc_types = ['law', 'regulation', 'rule', 'notice']
        if metadata.document_type not in valid_doc_types:
            issues.append({
                'type': 'enum_unmapped',
                'field': 'document_type',
                'value': metadata.document_type,
                'doc_number': metadata.doc_number
            })

        return issues

    def validate_all(self, documents: List[DocumentMetadata]) -> Dict:
        """Validate all documents"""
        logger.info("=== QA VALIDATION ===")

        for doc in documents:
            issues = self.validate_document(doc)
            if issues:
                self.issues.extend(issues)
                for issue in issues:
                    self.stats[issue['type']] += 1

        qa_report = {
            'total_documents': len(documents),
            'total_issues': len(self.issues),
            'issues_by_type': dict(self.stats),
            'issues': self.issues[:100]  # First 100 for brevity
        }

        logger.info(f"QA complete: {len(self.issues)} issues found")
        return qa_report


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class USGovTechSweepOrchestrator:
    """Main orchestrator for U.S. Gov Tech Sweep"""

    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.all_documents = []
        self.stats = Counter()

        logger.info("=== U.S. GOV TECH SWEEP ORCHESTRATOR ===")
        logger.info(f"Date range: {DATE_START} to {DATE_END}")
        logger.info(f"Output dir: {self.output_dir}")

    def run_fast_path(self):
        """Execute fast-path collection"""
        logger.info("Starting Fast-Path Collection...")

        # Fast-Path A: Federal Register
        fr_collector = FederalRegisterCollector()
        fr_docs = fr_collector.collect()
        self.all_documents.extend(fr_docs)
        self.stats['federal_register'] = len(fr_docs)

        # Fast-Path B: Regulations.gov
        reg_collector = RegulationsGovCollector()
        reg_docs = reg_collector.collect()
        self.all_documents.extend(reg_docs)
        self.stats['regulations_gov'] = len(reg_docs)

        # Fast-Path C: Congress.gov
        congress_collector = CongressGovCollector()
        congress_docs = congress_collector.collect()
        self.all_documents.extend(congress_docs)
        self.stats['congress_gov'] = len(congress_docs)

        logger.info(f"Fast-Path complete: {len(self.all_documents)} documents collected")

    def download_documents(self):
        """Download all collected documents"""
        logger.info("=== DOWNLOADING DOCUMENTS ===")

        downloader = DocumentDownloader(self.output_dir / 'files')

        for i, doc in enumerate(self.all_documents):
            if doc.download_url:
                self.all_documents[i] = downloader.download_document(doc)

                # Rate limiting
                if (i + 1) % 10 == 0:
                    time.sleep(1)

        self.stats.update(downloader.stats)

    def validate_documents(self) -> Dict:
        """Run QA validation"""
        validator = QAValidator()
        qa_report = validator.validate_all(self.all_documents)

        # Save QA report
        qa_path = self.output_dir / 'qa_report.json'
        with open(qa_path, 'w', encoding='utf-8') as f:
            json.dump(qa_report, f, indent=2, ensure_ascii=False)

        logger.info(f"QA report saved: {qa_path}")
        return qa_report

    def generate_summary(self):
        """Generate post-run summary"""
        logger.info("=== GENERATING SUMMARY ===")

        summary = {
            'collection_date': datetime.now().isoformat(),
            'date_range': f"{DATE_START} to {DATE_END}",
            'total_documents': len(self.all_documents),
            'stats': dict(self.stats),
            'by_document_type': Counter([d.document_type for d in self.all_documents]),
            'by_agency': Counter([d.agency_bureau for d in self.all_documents if d.agency_bureau]),
            'by_collection': Counter([d.collection for d in self.all_documents]),
            'by_year': Counter([d.year for d in self.all_documents if d.year]),
            'top_topics': Counter([t for d in self.all_documents for t in d.topics]).most_common(15)
        }

        # Save summary
        summary_path = self.output_dir / 'collection_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Save documents catalog
        catalog_path = self.output_dir / 'documents_catalog.json'
        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump([asdict(d) for d in self.all_documents], f, indent=2, ensure_ascii=False)

        logger.info(f"Summary saved: {summary_path}")
        logger.info(f"Catalog saved: {catalog_path}")

        # Print summary
        print("\n" + "="*60)
        print("U.S. GOV TECH SWEEP - COLLECTION SUMMARY")
        print("="*60)
        print(f"Total Documents: {summary['total_documents']}")
        print(f"\nBy Document Type:")
        for doc_type, count in summary['by_document_type'].items():
            print(f"  {doc_type}: {count}")
        print(f"\nTop 10 Agencies:")
        for agency, count in Counter(summary['by_agency']).most_common(10):
            print(f"  {agency}: {count}")
        print(f"\nTop 10 Topics:")
        for topic, count in summary['top_topics'][:10]:
            print(f"  {topic}: {count}")
        print("="*60)

    def run(self):
        """Run complete orchestration"""
        try:
            # Step 1: Fast-path collection
            self.run_fast_path()

            # Step 2: Download documents
            if self.all_documents:
                self.download_documents()

            # Step 3: QA validation
            if self.all_documents:
                self.validate_documents()

            # Step 4: Generate summary
            self.generate_summary()

            logger.info("=== COLLECTION COMPLETE ===")

        except Exception as e:
            logger.error(f"Orchestration error: {e}", exc_info=True)
            raise


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='U.S. Gov Tech Sweep Collector')
    parser.add_argument('--output-dir', default=str(OUTPUT_DIR),
                       help='Output directory')
    parser.add_argument('--regulations-api-key', help='Regulations.gov API key')
    parser.add_argument('--congress-api-key', help='Congress.gov API key')

    args = parser.parse_args()

    # Set API keys if provided
    global REGULATIONS_GOV_API_KEY, CONGRESS_GOV_API_KEY
    if args.regulations_api_key:
        REGULATIONS_GOV_API_KEY = args.regulations_api_key
    if args.congress_api_key:
        CONGRESS_GOV_API_KEY = args.congress_api_key

    # Run orchestrator
    orchestrator = USGovTechSweepOrchestrator(Path(args.output_dir))
    orchestrator.run()


if __name__ == '__main__':
    main()
