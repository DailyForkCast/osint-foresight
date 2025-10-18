#!/usr/bin/env python3
"""
USCC MCF Collector
Collects Military-Civil Fusion content from US-China Economic and Security Review Commission
Priority: HIGHEST (Tier 1) - Economic-security nexus, tech chapters, entity analysis
"""

import re
import json
import logging
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collectors.mcf_base_collector import MCFBaseCollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class USCCMCFCollector(MCFBaseCollector):
    """USCC MCF intelligence collector for economic-security analysis"""

    def __init__(self):
        super().__init__()
        self.source_id = "uscc"
        self.base_url = "https://www.uscc.gov"

        # Key USCC URLs
        self.uscc_urls = [
            "/annual-reports/",
            "/hearings/",
            "/research/",
            "/publications/",
            "/commissioners-corner/",
            "/sites/default/files/"
        ]

        # USCC report patterns
        self.report_patterns = [
            r"Annual Report to Congress",
            r"USCC.*Report",
            r"Hearing.*China",
            r"China.*Security",
            r"Economic.*Security.*Review"
        ]

        # MCF-specific search terms for USCC
        self.mcf_search_terms = [
            "military civil fusion",
            "dual-use technology transfer",
            "Chinese economic espionage",
            "technology acquisition China",
            "Chinese state-owned enterprises",
            "Belt and Road Initiative",
            "Made in China 2025",
            "Chinese industrial policy"
        ]

        # Economic-security entities
        self.economic_entities = [
            'State-owned enterprises', 'SOE', 'SASAC',
            'Ministry of Industry and Information Technology', 'MIIT',
            'National Development and Reform Commission', 'NDRC',
            'Ministry of Science and Technology', 'MOST',
            'China Investment Corporation', 'CIC',
            'Silk Road Fund', 'Asian Infrastructure Investment Bank', 'AIIB',
            'China Development Bank', 'China Export-Import Bank',
            'Confucius Institute', 'Thousand Talents Program',
            'Belt and Road Initiative', 'BRI', 'One Belt One Road'
        ]

        # Technology focus areas
        self.tech_focus_areas = [
            'artificial intelligence', 'AI', 'machine learning',
            'semiconductors', 'microchips', 'integrated circuits',
            '5G', '6G', 'telecommunications', 'Huawei', 'ZTE',
            'quantum computing', 'quantum communications',
            'biotechnology', 'genetic engineering', 'CRISPR',
            'renewable energy', 'solar panels', 'wind turbines',
            'electric vehicles', 'batteries', 'lithium',
            'robotics', 'automation', 'manufacturing'
        ]

    def extract_uscc_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from USCC document"""
        metadata = {
            'title': 'Unknown Title',
            'publication_date': None,
            'authors': [],
            'document_type': 'report',
            'report_type': None,
            'hearing_date': None,
            'witnesses': [],
            'classification': 'unclassified'
        }

        # Extract title
        title_selectors = [
            'h1.page-title',
            'h1',
            '.report-title',
            '.hearing-title',
            '.publication-title',
            'title'
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                title_text = re.sub(r'\s+', ' ', title_text)
                metadata['title'] = title_text
                break

        # Extract publication/hearing date
        page_text = soup.get_text()

        date_patterns = [
            r'(?:Published|Date|Hearing).*?(\w+\s+\d{1,2},?\s+\d{4})',
            r'(\w+\s+\d{1,2},?\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                for date_str in matches:
                    try:
                        for fmt in ['%B %d, %Y', '%B %d %Y', '%m/%d/%Y', '%Y-%m-%d']:
                            try:
                                parsed_date = datetime.strptime(date_str, fmt)
                                metadata['publication_date'] = parsed_date.date().isoformat()
                                break
                            except ValueError:
                                continue
                        if metadata['publication_date']:
                            break
                    except ValueError:
                        continue

        # Determine document type and extract specific metadata
        url_lower = url.lower()
        page_text_lower = page_text.lower()

        if 'annual-report' in url_lower or 'annual report' in page_text_lower:
            metadata['document_type'] = 'annual_report'
            metadata['report_type'] = 'Annual Report to Congress'

            # Extract year from annual report
            year_match = re.search(r'(\d{4})\s*annual\s*report', page_text_lower)
            if year_match:
                metadata['report_year'] = year_match.group(1)

        elif 'hearing' in url_lower or 'hearing' in page_text_lower:
            metadata['document_type'] = 'hearing'

            # Extract hearing date
            hearing_date_match = re.search(r'hearing.*?(\w+\s+\d{1,2},?\s+\d{4})', page_text_lower)
            if hearing_date_match:
                metadata['hearing_date'] = hearing_date_match.group(1)

            # Extract witnesses
            witness_patterns = [
                r'witness(?:es)?[:\s]+(.*?)(?:\n|$)',
                r'testimony.*?by[:\s]+(.*?)(?:\n|$)',
                r'presented\s+by[:\s]+(.*?)(?:\n|$)'
            ]

            for pattern in witness_patterns:
                witness_matches = re.findall(pattern, page_text, re.IGNORECASE)
                if witness_matches:
                    witnesses = []
                    for witness_text in witness_matches[:3]:  # Limit witnesses
                        # Clean witness names
                        witness = re.sub(r'[^\w\s,.-]', '', witness_text.strip())
                        if witness and len(witness) > 5:
                            witnesses.append(witness)
                    if witnesses:
                        metadata['witnesses'] = witnesses
                        break

        elif 'research' in url_lower:
            metadata['document_type'] = 'research_report'
        elif '.pdf' in url_lower:
            metadata['document_type'] = 'pdf_document'

        # Extract commissioners/authors
        author_patterns = [
            r'commissioner[s]?[:\s]+(.*?)(?:\n|$)',
            r'author[s]?[:\s]+(.*?)(?:\n|$)',
            r'prepared\s+by[:\s]+(.*?)(?:\n|$)'
        ]

        for pattern in author_patterns:
            author_matches = re.findall(pattern, page_text, re.IGNORECASE)
            if author_matches:
                authors = []
                for author_text in author_matches[:3]:
                    author = author_text.strip()
                    if author and len(author) > 3:
                        authors.append(author)
                if authors:
                    metadata['authors'] = authors
                    break

        return metadata

    def collect_annual_reports(self) -> list:
        """Collect USCC Annual Reports"""
        logger.info("Collecting USCC Annual Reports")
        documents = []

        annual_reports_url = urljoin(self.base_url, "/annual-reports/")

        response = self.fetch_url_with_retry(annual_reports_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find annual report links
        report_links = soup.find_all('a', href=True)
        annual_report_urls = []

        for link in report_links:
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for annual reports
            if any(term in link_text.lower() for term in ['annual report', 'report to congress', '20']):
                if href not in annual_report_urls:
                    annual_report_urls.append(href)

        logger.info(f"Found {len(annual_report_urls)} potential annual reports")

        # Process annual reports
        for report_url in annual_report_urls[:10]:  # Limit to recent reports
            try:
                report_response = self.fetch_url_with_retry(report_url)
                if not report_response:
                    continue

                report_soup = BeautifulSoup(report_response.text, 'html.parser')
                content_text = report_soup.get_text()

                # Calculate MCF relevance with economic bonus
                mcf_score = self.calculate_mcf_relevance(content_text)

                # Economic-security bonus
                economic_bonus = 0
                for entity in self.economic_entities:
                    if entity.lower() in content_text.lower():
                        economic_bonus += 0.05

                # Technology focus bonus
                tech_bonus = 0
                for tech in self.tech_focus_areas:
                    if tech.lower() in content_text.lower():
                        tech_bonus += 0.05

                mcf_score = min(mcf_score + economic_bonus + tech_bonus, 1.0)

                if mcf_score >= 0.3:  # Lower threshold for comprehensive reports
                    metadata = self.extract_uscc_metadata(report_soup, report_url)

                    document_data = self.process_document(
                        report_url,
                        self.source_id,
                        **metadata
                    )

                    if document_data:
                        documents.append(document_data)
                        logger.info(f"Collected USCC Annual Report: {metadata['title'][:50]}... (Score: {mcf_score:.3f})")

            except Exception as e:
                logger.error(f"Error processing annual report {report_url}: {e}")

        return documents

    def collect_hearings(self) -> list:
        """Collect USCC hearing transcripts"""
        logger.info("Collecting USCC hearings")
        documents = []

        hearings_url = urljoin(self.base_url, "/hearings/")

        response = self.fetch_url_with_retry(hearings_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find hearing links
        hearing_links = soup.find_all('a', href=True)
        hearing_urls = []

        for link in hearing_links:
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for hearings related to technology/economy/security
            mcf_indicators = [
                'technology', 'economic', 'security', 'military', 'defense',
                'trade', 'investment', 'innovation', 'china', 'chinese'
            ]

            if any(indicator in link_text.lower() for indicator in mcf_indicators):
                if href not in hearing_urls:
                    hearing_urls.append(href)

        logger.info(f"Found {len(hearing_urls)} potential hearings")

        # Process hearings
        for hearing_url in hearing_urls[:15]:  # Limit hearings
            try:
                hearing_response = self.fetch_url_with_retry(hearing_url)
                if not hearing_response:
                    continue

                hearing_soup = BeautifulSoup(hearing_response.text, 'html.parser')
                content_text = hearing_soup.get_text()

                # Calculate MCF relevance
                mcf_score = self.calculate_mcf_relevance(content_text)

                # Hearing-specific bonus for witness expertise
                if any(term in content_text.lower() for term in ['testimony', 'witness', 'expert']):
                    mcf_score = min(mcf_score + 0.1, 1.0)

                if mcf_score >= 0.4:
                    metadata = self.extract_uscc_metadata(hearing_soup, hearing_url)

                    document_data = self.process_document(
                        hearing_url,
                        self.source_id,
                        **metadata
                    )

                    if document_data:
                        documents.append(document_data)
                        logger.info(f"Collected USCC hearing: {metadata['title'][:50]}... (Score: {mcf_score:.3f})")

            except Exception as e:
                logger.error(f"Error processing hearing {hearing_url}: {e}")

        return documents

    def collect_research_publications(self) -> list:
        """Collect USCC research publications"""
        logger.info("Collecting USCC research publications")
        documents = []

        research_url = urljoin(self.base_url, "/research/")

        response = self.fetch_url_with_retry(research_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find research publication links
        research_links = soup.find_all('a', href=True)

        for link in research_links[:20]:  # Limit research documents
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for research content
            if any(term in link_text.lower() for term in ['research', 'study', 'analysis', 'report']):
                try:
                    document_data = self.process_document(href, self.source_id)

                    if document_data and document_data['mcf_relevance_score'] >= 0.4:
                        documents.append(document_data)
                        logger.info(f"Collected USCC research: {document_data.get('title', 'Unknown')[:40]}...")

                except Exception as e:
                    logger.error(f"Error processing research document {href}: {e}")

        return documents

    def search_uscc_mcf_content(self) -> list:
        """Search USCC for additional MCF content"""
        logger.info("Searching USCC for MCF content")
        documents = []

        for search_term in self.mcf_search_terms:
            try:
                # USCC search functionality
                search_url = f"{self.base_url}/search?query={search_term.replace(' ', '+')}"

                response = self.fetch_url_with_retry(search_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find search result links
                result_links = soup.find_all('a', href=True)

                for link in result_links[:2]:  # Limit results per search
                    href = link['href']

                    if not href.startswith('http') and href.startswith('/'):
                        href = urljoin(self.base_url, href)

                    if self.base_url not in href:
                        continue

                    try:
                        document_data = self.process_document(href, self.source_id)

                        if document_data and document_data['mcf_relevance_score'] >= 0.5:
                            documents.append(document_data)
                            logger.info(f"Found USCC MCF search result: {document_data.get('title', 'Unknown')[:40]}...")

                    except Exception as e:
                        logger.error(f"Error processing search result {href}: {e}")

            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")

        return documents

    def collect_all_mcf_content(self) -> dict:
        """Collect all USCC MCF content"""
        logger.info("Starting USCC MCF collection")

        all_documents = []
        collection_stats = {
            'source': 'USCC',
            'start_time': datetime.now().isoformat(),
            'annual_report_docs': 0,
            'hearing_docs': 0,
            'research_docs': 0,
            'search_docs': 0,
            'total_documents': 0,
            'high_relevance_docs': 0,
            'economic_security_docs': 0,
            'technology_focus_docs': 0,
            'errors': 0
        }

        # Collect annual reports
        try:
            annual_docs = self.collect_annual_reports()
            all_documents.extend(annual_docs)
            collection_stats['annual_report_docs'] = len(annual_docs)
        except Exception as e:
            logger.error(f"Error collecting annual reports: {e}")
            collection_stats['errors'] += 1

        # Collect hearings
        try:
            hearing_docs = self.collect_hearings()
            all_documents.extend(hearing_docs)
            collection_stats['hearing_docs'] = len(hearing_docs)
        except Exception as e:
            logger.error(f"Error collecting hearings: {e}")
            collection_stats['errors'] += 1

        # Collect research publications
        try:
            research_docs = self.collect_research_publications()
            all_documents.extend(research_docs)
            collection_stats['research_docs'] = len(research_docs)
        except Exception as e:
            logger.error(f"Error collecting research: {e}")
            collection_stats['errors'] += 1

        # Search for additional content
        try:
            search_docs = self.search_uscc_mcf_content()
            all_documents.extend(search_docs)
            collection_stats['search_docs'] = len(search_docs)
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            collection_stats['errors'] += 1

        # Calculate final statistics
        collection_stats['total_documents'] = len(all_documents)
        collection_stats['high_relevance_docs'] = sum(
            1 for doc in all_documents if doc.get('mcf_relevance_score', 0) >= 0.7
        )

        # Count economic-security specific documents
        collection_stats['economic_security_docs'] = sum(
            1 for doc in all_documents
            if any(entity.lower() in doc.get('content_text', '').lower()
                   for entity in self.economic_entities)
        )

        # Count technology-focused documents
        collection_stats['technology_focus_docs'] = sum(
            1 for doc in all_documents
            if any(tech.lower() in doc.get('content_text', '').lower()
                   for tech in self.tech_focus_areas)
        )

        collection_stats['end_time'] = datetime.now().isoformat()

        # Get updated database statistics
        db_stats = self.get_mcf_statistics()

        logger.info(f"""
USCC MCF Collection Complete:
- Annual report documents: {collection_stats['annual_report_docs']}
- Hearing documents: {collection_stats['hearing_docs']}
- Research documents: {collection_stats['research_docs']}
- Search documents: {collection_stats['search_docs']}
- Total collected: {collection_stats['total_documents']}
- High relevance (>0.7): {collection_stats['high_relevance_docs']}
- Economic-security focus: {collection_stats['economic_security_docs']}
- Technology focus: {collection_stats['technology_focus_docs']}
- Total MCF documents in database: {db_stats.get('total_documents', 0)}
        """)

        return {
            'collection_stats': collection_stats,
            'database_stats': db_stats,
            'documents': all_documents
        }

def main():
    """Run USCC MCF collection"""
    collector = USCCMCFCollector()
    results = collector.collect_all_mcf_content()

    # Save collection report
    output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_uscc")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"uscc_mcf_collection_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"USCC MCF collection report saved to: {report_file}")

if __name__ == "__main__":
    main()
