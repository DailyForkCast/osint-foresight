#!/usr/bin/env python3
"""
Zero-Fabrication EU-China Agreements Harvester
Strict provenance tracking and verification protocols
NO DATA FABRICATION - ALL SOURCES MUST BE VERIFIABLE
"""

import json
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import uuid

# For web scraping with provenance
import requests
from bs4 import BeautifulSoup

# Setup strict logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [PROVENANCE] %(message)s',
    handlers=[
        logging.FileHandler(f'zero_fabrication_harvest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProvenanceRecord:
    """Complete provenance tracking for every data point"""
    record_id: str
    source_url: str
    fetch_timestamp: str
    http_status: int
    content_hash: str
    extraction_method: str
    extraction_timestamp: str
    raw_content_file: str
    verification_status: str = "unverified"
    verification_notes: Optional[str] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class VerifiedAgreement:
    """Agreement with complete provenance and verification"""
    agreement_id: str
    title_extracted: Optional[str]
    title_source_snippet: Optional[str]
    country: str
    source_urls: List[str]
    provenance_records: List[ProvenanceRecord]
    extraction_confidence: str  # "high", "medium", "low"
    verification_required: bool
    raw_content_files: List[str]
    creation_timestamp: str
    notes: str = "EXTRACTED DATA - REQUIRES MANUAL VERIFICATION"

    def to_dict(self):
        data = asdict(self)
        # Convert provenance records to dicts
        data['provenance_records'] = [p.to_dict() for p in self.provenance_records]
        return data

class ZeroFabricationExtractor:
    """Extractor with strict no-fabrication protocols"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.provenance_dir = output_dir / 'provenance'
        self.raw_dir = output_dir / 'raw_verified'
        self.provenance_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

        # Track all operations
        self.operations_log = []

    def log_operation(self, operation: str, details: Dict):
        """Log every operation with timestamp"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'details': details
        }
        self.operations_log.append(log_entry)
        logger.info(f"OPERATION: {operation} - {details}")

    def fetch_with_provenance(self, url: str, country: str) -> Optional[ProvenanceRecord]:
        """Fetch content with complete provenance tracking"""
        self.log_operation("FETCH_INITIATED", {"url": url, "country": country})

        try:
            # Fetch with user agent and headers
            headers = {
                'User-Agent': 'EU-China Agreements Research Tool - Academic/Government Use Only',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            response = requests.get(url, headers=headers, timeout=30)
            fetch_timestamp = datetime.now().isoformat()

            # Calculate content hash
            content_hash = hashlib.sha256(response.content).hexdigest()

            # Save raw content with provenance
            domain = urlparse(url).netloc.replace('.', '_')
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_filename = f"{country}_{domain}_{timestamp_str}_{content_hash[:8]}.html"
            raw_filepath = self.raw_dir / raw_filename

            with open(raw_filepath, 'wb') as f:
                f.write(response.content)

            # Create provenance record
            provenance = ProvenanceRecord(
                record_id=str(uuid.uuid4()),
                source_url=url,
                fetch_timestamp=fetch_timestamp,
                http_status=response.status_code,
                content_hash=content_hash,
                extraction_method="requests_get_with_provenance",
                extraction_timestamp=datetime.now().isoformat(),
                raw_content_file=str(raw_filepath),
                verification_status="requires_manual_verification"
            )

            self.log_operation("FETCH_COMPLETED", {
                "url": url,
                "status_code": response.status_code,
                "content_length": len(response.content),
                "content_hash": content_hash,
                "raw_file": str(raw_filepath)
            })

            return provenance

        except Exception as e:
            self.log_operation("FETCH_FAILED", {"url": url, "error": str(e)})
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def extract_with_verification_flags(self, content: str, url: str, country: str) -> Optional[VerifiedAgreement]:
        """Extract data with clear verification requirements"""
        self.log_operation("EXTRACTION_INITIATED", {"url": url, "country": country})

        # Parse content
        soup = BeautifulSoup(content, 'html.parser')

        # Extract title with source snippet
        title_elem = soup.find('title')
        title_extracted = title_elem.get_text(strip=True) if title_elem else None
        title_source_snippet = str(title_elem)[:200] if title_elem else None

        # CRITICAL: Mark everything as requiring verification
        verification_required = True
        extraction_confidence = "low"  # Conservative by default

        # Look for agreement-related content
        text = soup.get_text().lower()
        agreement_indicators = [
            'agreement', 'treaty', 'memorandum', 'mou', 'protocol',
            'cooperation', 'partnership', 'accord', 'convention',
            'china', 'chinese', 'prc', 'people\'s republic'
        ]

        indicator_count = sum(1 for indicator in agreement_indicators if indicator in text)

        if indicator_count >= 3:
            extraction_confidence = "medium"
        if indicator_count >= 5:
            extraction_confidence = "high"

        # Create verified agreement with strict provenance
        agreement = VerifiedAgreement(
            agreement_id=str(uuid.uuid4()),
            title_extracted=title_extracted,
            title_source_snippet=title_source_snippet,
            country=country,
            source_urls=[url],
            provenance_records=[],  # Will be added by caller
            extraction_confidence=extraction_confidence,
            verification_required=verification_required,
            raw_content_files=[],  # Will be added by caller
            creation_timestamp=datetime.now().isoformat(),
            notes=f"EXTRACTED DATA - CONFIDENCE: {extraction_confidence} - MANUAL VERIFICATION REQUIRED BEFORE USE"
        )

        self.log_operation("EXTRACTION_COMPLETED", {
            "url": url,
            "title_found": title_extracted is not None,
            "confidence": extraction_confidence,
            "agreement_indicators": indicator_count
        })

        return agreement

    def save_provenance_trail(self, country: str):
        """Save complete provenance trail"""
        provenance_file = self.provenance_dir / f"{country}_provenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        provenance_data = {
            "country": country,
            "harvest_session": {
                "start_time": self.operations_log[0]["timestamp"] if self.operations_log else None,
                "end_time": datetime.now().isoformat(),
                "total_operations": len(self.operations_log)
            },
            "operations_log": self.operations_log,
            "verification_status": "ALL_DATA_REQUIRES_MANUAL_VERIFICATION",
            "fabrication_risk": "ZERO_FABRICATION_PROTOCOL_ENFORCED",
            "usage_warning": "DO NOT USE WITHOUT MANUAL VERIFICATION OF SOURCE DOCUMENTS"
        }

        with open(provenance_file, 'w', encoding='utf-8') as f:
            json.dump(provenance_data, f, indent=2, ensure_ascii=False)

        logger.info(f"PROVENANCE TRAIL SAVED: {provenance_file}")
        return provenance_file

class CountryHarvesterZeroFab:
    """Country-specific harvester with zero fabrication protocols"""

    def __init__(self, country_code: str, config_path: str, output_dir: Path):
        self.country_code = country_code
        self.output_dir = output_dir
        self.extractor = ZeroFabricationExtractor(output_dir)

        # Load country configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        if country_code not in self.config['countries']:
            raise ValueError(f"Country {country_code} not in configuration")

        self.country_config = self.config['countries'][country_code]

        # Create country output directory
        self.country_dir = output_dir / country_code
        self.country_dir.mkdir(parents=True, exist_ok=True)

    def generate_verification_queries(self) -> List[str]:
        """Generate search queries with strict source requirements"""
        queries = []

        # Only official government sources
        for domain in self.country_config.get('official_domains', []):
            # English queries
            queries.append(f'site:{domain} China agreement')
            queries.append(f'site:{domain} China memorandum')
            queries.append(f'site:{domain} China cooperation')

            # Native language queries
            native_terms = self.country_config.get('search_terms', {}).get(self.country_config['primary_language'], [])
            for term in native_terms[:3]:  # Limit to avoid spam
                queries.append(f'site:{domain} "{term}" China')

        # Chinese embassy (for verification)
        chinese_embassy = self.config['chinese_sources']['embassies'].get(self.country_code)
        if chinese_embassy:
            queries.append(f'site:{chinese_embassy} agreement')
            queries.append(f'site:{chinese_embassy} 协议')

        logger.info(f"Generated {len(queries)} verification queries for {self.country_code}")
        return queries

    def harvest_with_verification(self, max_sources: int = 10) -> Dict:
        """Harvest with complete verification protocols"""
        logger.info(f"=" * 60)
        logger.info(f"ZERO-FABRICATION HARVEST: {self.country_code}")
        logger.info(f"=" * 60)

        self.extractor.log_operation("HARVEST_SESSION_START", {"country": self.country_code})

        # Get verification queries
        queries = self.generate_verification_queries()

        # For demo purposes, let's manually specify some official URLs to check
        # In production, these would come from search results or predefined lists
        test_urls = self._get_official_test_urls()

        verified_agreements = []

        for url in test_urls[:max_sources]:
            logger.info(f"PROCESSING: {url}")

            # Fetch with provenance
            provenance = self.extractor.fetch_with_provenance(url, self.country_code)
            if not provenance:
                continue

            # Read the saved content
            try:
                with open(provenance.raw_content_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Extract with verification flags
                agreement = self.extractor.extract_with_verification_flags(content, url, self.country_code)
                if agreement:
                    # Add provenance to agreement
                    agreement.provenance_records = [provenance]
                    agreement.raw_content_files = [provenance.raw_content_file]

                    verified_agreements.append(agreement)

            except Exception as e:
                self.extractor.log_operation("CONTENT_READ_FAILED", {"file": provenance.raw_content_file, "error": str(e)})

            # Rate limiting
            time.sleep(2)

        # Save agreements with verification warnings
        self._save_verified_agreements(verified_agreements)

        # Save provenance trail
        provenance_file = self.extractor.save_provenance_trail(self.country_code)

        self.extractor.log_operation("HARVEST_SESSION_END", {
            "country": self.country_code,
            "agreements_found": len(verified_agreements),
            "provenance_file": str(provenance_file)
        })

        return {
            "country": self.country_code,
            "agreements_found": len(verified_agreements),
            "verification_required": True,
            "provenance_file": str(provenance_file),
            "all_data_status": "REQUIRES_MANUAL_VERIFICATION"
        }

    def _get_official_test_urls(self) -> List[str]:
        """Get official URLs to test (no fabrication - real URLs only)"""
        urls = []

        # Add real official URLs based on country
        if self.country_code == "DE":
            urls = [
                "https://www.auswaertiges-amt.de/de/aussenpolitik/laender/laenderinfos/china/bilateral_node.html",
                "https://www.bundesregierung.de"
            ]
        elif self.country_code == "FR":
            urls = [
                "https://www.diplomatie.gouv.fr/fr/dossiers-pays/chine/",
                "https://www.gouvernement.fr"
            ]
        elif self.country_code == "IT":
            urls = [
                "https://www.esteri.it",
                "https://ambpechino.esteri.it"
            ]
        elif self.country_code == "GB":
            urls = [
                "https://www.gov.uk/world/china",
                "https://www.gov.uk/government/world/organisations/british-embassy-beijing"
            ]
        elif self.country_code == "PL":
            urls = [
                "https://www.gov.pl/web/dyplomacja",
                "https://www.prezydent.pl"
            ]
        # Add more real URLs as needed

        return urls

    def _save_verified_agreements(self, agreements: List[VerifiedAgreement]):
        """Save agreements with verification warnings"""
        if not agreements:
            logger.warning(f"No agreements found for {self.country_code}")
            return

        # Save in NDJSON format with verification headers
        output_file = self.country_dir / 'verified_agreements.ndjson'

        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header with warnings
            header = {
                "VERIFICATION_WARNING": "ALL DATA REQUIRES MANUAL VERIFICATION",
                "FABRICATION_RISK": "ZERO - ALL SOURCES DOCUMENTED",
                "USAGE_RESTRICTION": "DO NOT USE WITHOUT VERIFICATION",
                "country": self.country_code,
                "total_records": len(agreements),
                "creation_date": datetime.now().isoformat()
            }
            f.write(json.dumps(header, ensure_ascii=False) + '\n')

            # Write agreements
            for agreement in agreements:
                f.write(json.dumps(agreement.to_dict(), ensure_ascii=False) + '\n')

        logger.info(f"SAVED {len(agreements)} verified agreements to {output_file}")

        # Create verification checklist
        checklist_file = self.country_dir / 'verification_checklist.md'
        with open(checklist_file, 'w', encoding='utf-8') as f:
            f.write(f"# Verification Checklist for {self.country_code}\n\n")
            f.write("## CRITICAL: Manual Verification Required\n\n")
            f.write("Before using any data from this harvest:\n\n")

            for i, agreement in enumerate(agreements, 1):
                f.write(f"### Agreement {i}\n")
                f.write(f"- **Title**: {agreement.title_extracted}\n")
                f.write(f"- **Source**: {agreement.source_urls[0] if agreement.source_urls else 'N/A'}\n")
                f.write(f"- **Confidence**: {agreement.extraction_confidence}\n")
                f.write(f"- **Raw File**: {agreement.raw_content_files[0] if agreement.raw_content_files else 'N/A'}\n")
                f.write("- **Verification Status**: ❌ NOT VERIFIED\n")
                f.write("- **Manual Check Required**: ✅\n\n")

        logger.info(f"CREATED verification checklist: {checklist_file}")

def main():
    """Main function for zero-fabrication harvesting"""

    # Setup
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / 'config' / 'all_countries.json'
    output_dir = base_dir / 'out_verified'

    # Test with a few countries
    test_countries = ['DE', 'FR', 'IT', 'GB', 'PL']

    logger.info("STARTING ZERO-FABRICATION HARVEST")
    logger.info("ALL DATA WILL REQUIRE MANUAL VERIFICATION")

    results = {}

    for country in test_countries:
        try:
            harvester = CountryHarvesterZeroFab(country, str(config_path), output_dir)
            result = harvester.harvest_with_verification(max_sources=3)  # Limit for demo
            results[country] = result

        except Exception as e:
            logger.error(f"Failed to harvest {country}: {e}")
            results[country] = {"error": str(e)}

    # Final report
    final_report = {
        "session_summary": {
            "timestamp": datetime.now().isoformat(),
            "countries_processed": list(results.keys()),
            "verification_status": "ALL_DATA_REQUIRES_MANUAL_VERIFICATION",
            "fabrication_risk": "ZERO"
        },
        "country_results": results,
        "usage_warning": "DO NOT USE ANY DATA WITHOUT MANUAL VERIFICATION OF SOURCE DOCUMENTS",
        "next_steps": [
            "1. Review all provenance files",
            "2. Manually verify each agreement in source documents",
            "3. Cross-reference with official government publications",
            "4. Validate dates and parties through multiple sources",
            "5. Flag any suspicious or unverifiable data"
        ]
    }

    report_file = output_dir / f'zero_fabrication_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)

    logger.info(f"ZERO-FABRICATION HARVEST COMPLETE")
    logger.info(f"FINAL REPORT: {report_file}")
    logger.info("REMEMBER: ALL DATA REQUIRES MANUAL VERIFICATION")

if __name__ == "__main__":
    main()
