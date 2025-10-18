#!/usr/bin/env python3
"""
NDU CSCMA MCF Collector
Collects Military-Civil Fusion content from National Defense University
China Strategic & Management Analytics (CSCMA)
Priority: HIGHEST (Tier 1) - PLA acquisition, doctrine, strategy
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

class NDUCSCMACollector(MCFBaseCollector):
    """NDU CSCMA MCF intelligence collector for PLA analysis"""

    def __init__(self):
        super().__init__()
        self.source_id = "ndu_cscma"
        self.base_url = "https://ndupress.ndu.edu"

        # Key NDU CSCMA URLs
        self.cscma_urls = [
            "/Publications/China/",
            "/China-Strategic-Perspectives/",
            "/Portals/68/Documents/stratperspective/",
            "/Publications/Publication-View/",
            "/Media/News/"
        ]

        # China Strategic Perspectives series patterns
        self.csp_patterns = [
            r"China Strategic Perspectives",
            r"CSP[-\s]?\d+",
            r"Strategic Perspectives.*China",
            r"PLA.*Study",
            r"Chinese.*Military"
        ]

        # MCF-specific search terms for NDU
        self.mcf_search_terms = [
            "military civil fusion",
            "dual-use technology China",
            "PLA modernization",
            "Chinese defense industry",
            "civil-military integration",
            "Chinese military doctrine",
            "PLA acquisition",
            "defense industrial base China"
        ]

        # PLA and Chinese military entities
        self.pla_entities = [
            'PLA', 'People\'s Liberation Army', 'Central Military Commission', 'CMC',
            'PLA Army', 'PLAA', 'PLA Navy', 'PLAN', 'PLA Air Force', 'PLAAF',
            'PLA Rocket Force', 'PLARF', 'Strategic Support Force', 'SSF',
            'National University of Defense Technology', 'NUDT',
            'Academy of Military Science', 'AMS', 'National Defense University',
            'Military Science Academy', 'Equipment Development Department'
        ]

    def extract_ndu_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from NDU CSCMA publication"""
        metadata = {
            'title': 'Unknown Title',
            'publication_date': None,
            'authors': [],
            'document_type': 'report',
            'series': None,
            'report_number': None,
            'classification': 'unclassified'
        }

        # Extract title
        title_selectors = [
            'h1.page-title',
            'h1',
            '.publication-title',
            '.entry-title',
            'title'
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                # Clean up title
                title_text = re.sub(r'\s+', ' ', title_text)
                metadata['title'] = title_text
                break

        # Extract series information
        page_text = soup.get_text()

        # Check for China Strategic Perspectives
        for pattern in self.csp_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                metadata['series'] = 'China Strategic Perspectives'

                # Extract report number
                number_match = re.search(r'CSP[-\s]?(\d+)', page_text, re.IGNORECASE)
                if number_match:
                    metadata['report_number'] = f"CSP-{number_match.group(1)}"
                break

        # Extract publication date
        date_patterns = [
            r'(\w+ \d{1,2}, \d{4})',  # January 15, 2024
            r'(\d{1,2}/\d{1,2}/\d{4})',  # 1/15/2024
            r'(\d{4}-\d{2}-\d{2})',  # 2024-01-15
            r'Published[:\s]+(\w+ \d{4})',  # Published: January 2024
            r'(\w+ \d{4})'  # January 2024
        ]

        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                date_str = match.group(1)
                try:
                    # Try different date formats
                    for fmt in ['%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d', '%B %Y']:
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

        # Extract authors
        author_selectors = [
            '.author',
            '.byline',
            '.publication-author',
            '.contributors'
        ]

        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                authors_text = author_elem.get_text(strip=True)
                # Split by common separators and clean
                authors = []
                for author in re.split(r'[,;&]|\band\b', authors_text):
                    author = author.strip()
                    if author and len(author) > 2:
                        # Remove titles and clean
                        author = re.sub(r'^(Dr|Professor|Col|Lt|Maj|General)\.?\s*', '', author)
                        authors.append(author)

                metadata['authors'] = authors[:3]  # Limit to 3 authors
                break

        # Determine document type
        if '/strategic-perspectives/' in url.lower() or 'csp' in url.lower():
            metadata['document_type'] = 'strategic_perspective'
        elif '/publications/' in url.lower():
            metadata['document_type'] = 'publication'
        elif '/press/' in url.lower():
            metadata['document_type'] = 'press_release'
        elif '.pdf' in url.lower():
            metadata['document_type'] = 'pdf_report'

        return metadata

    def collect_china_strategic_perspectives(self) -> list:
        """Collect China Strategic Perspectives series documents"""
        logger.info("Collecting China Strategic Perspectives from NDU")
        documents = []

        # Main China Strategic Perspectives page
        csp_url = urljoin(self.base_url, "/Publications/China-Strategic-Perspectives/")

        response = self.fetch_url_with_retry(csp_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all publication links
        pub_links = soup.find_all('a', href=True)
        csp_links = []

        for link in pub_links:
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for China Strategic Perspectives
            if any(pattern.lower() in link_text.lower() for pattern in ['china', 'strategic', 'perspective', 'csp', 'pla']):
                if href not in csp_links:
                    csp_links.append(href)

            # Also check href for CSP patterns
            if any(term in href.lower() for term in ['china', 'strategic', 'csp', 'pla']):
                if href not in csp_links:
                    csp_links.append(href)

        logger.info(f"Found {len(csp_links)} potential CSP documents")

        # Process each CSP document
        for csp_link in csp_links[:20]:  # Limit to prevent overwhelming
            try:
                csp_response = self.fetch_url_with_retry(csp_link)
                if not csp_response:
                    continue

                csp_soup = BeautifulSoup(csp_response.text, 'html.parser')
                content_text = csp_soup.get_text()

                # Calculate MCF relevance
                mcf_score = self.calculate_mcf_relevance(content_text)

                # Enhanced scoring for PLA/military content
                pla_bonus = 0
                for entity in self.pla_entities:
                    if entity.lower() in content_text.lower():
                        pla_bonus += 0.1

                mcf_score = min(mcf_score + pla_bonus, 1.0)

                if mcf_score >= 0.4:  # High threshold for NDU content
                    metadata = self.extract_ndu_metadata(csp_soup, csp_link)

                    document_data = self.process_document(
                        csp_link,
                        self.source_id,
                        **metadata
                    )

                    if document_data:
                        documents.append(document_data)
                        logger.info(f"Collected CSP document: {metadata['title'][:60]}... (Score: {mcf_score:.3f})")

            except Exception as e:
                logger.error(f"Error processing CSP document {csp_link}: {e}")

        return documents

    def collect_china_publications(self) -> list:
        """Collect general China-related publications from NDU"""
        logger.info("Collecting China publications from NDU")
        documents = []

        china_url = urljoin(self.base_url, "/Publications/China/")

        response = self.fetch_url_with_retry(china_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find publication listings
        pub_links = soup.find_all('a', href=True)
        china_pub_links = []

        for link in pub_links:
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for China-related content
            china_indicators = ['china', 'chinese', 'pla', 'military', 'defense', 'beijing']
            if any(indicator in link_text.lower() for indicator in china_indicators):
                if href not in china_pub_links:
                    china_pub_links.append(href)

        # Process China publications
        for pub_link in china_pub_links[:15]:  # Limit collection
            try:
                document_data = self.process_document(pub_link, self.source_id)

                if document_data and document_data['mcf_relevance_score'] >= 0.3:
                    documents.append(document_data)
                    logger.info(f"Collected China publication: {document_data.get('title', 'Unknown')[:50]}...")

            except Exception as e:
                logger.error(f"Error processing China publication {pub_link}: {e}")

        return documents

    def search_ndu_mcf_content(self) -> list:
        """Search NDU site for MCF-related content"""
        logger.info("Searching NDU for MCF content")
        documents = []

        # NDU search functionality
        base_search_url = f"{self.base_url}/Search/"

        for search_term in self.mcf_search_terms:
            try:
                # Construct search URL (may need adjustment based on NDU search implementation)
                search_url = f"{base_search_url}?query={search_term.replace(' ', '+')}"

                response = self.fetch_url_with_retry(search_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find search result links
                result_links = soup.find_all('a', href=True)

                for link in result_links[:3]:  # Limit results per search
                    href = link['href']

                    if not href.startswith('http') and href.startswith('/'):
                        href = urljoin(self.base_url, href)

                    if self.base_url not in href:
                        continue

                    try:
                        document_data = self.process_document(href, self.source_id)

                        if document_data and document_data['mcf_relevance_score'] >= 0.5:
                            documents.append(document_data)
                            logger.info(f"Found NDU MCF search result: {document_data.get('title', 'Unknown')[:40]}...")

                    except Exception as e:
                        logger.error(f"Error processing search result {href}: {e}")

            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")

        return documents

    def collect_all_mcf_content(self) -> dict:
        """Collect all NDU CSCMA MCF content"""
        logger.info("Starting NDU CSCMA MCF collection")

        all_documents = []
        collection_stats = {
            'source': 'NDU CSCMA',
            'start_time': datetime.now().isoformat(),
            'csp_docs': 0,
            'china_pub_docs': 0,
            'search_docs': 0,
            'total_documents': 0,
            'high_relevance_docs': 0,
            'pla_specific_docs': 0,
            'errors': 0
        }

        # Collect China Strategic Perspectives
        try:
            csp_docs = self.collect_china_strategic_perspectives()
            all_documents.extend(csp_docs)
            collection_stats['csp_docs'] = len(csp_docs)
        except Exception as e:
            logger.error(f"Error collecting CSP documents: {e}")
            collection_stats['errors'] += 1

        # Collect general China publications
        try:
            china_docs = self.collect_china_publications()
            all_documents.extend(china_docs)
            collection_stats['china_pub_docs'] = len(china_docs)
        except Exception as e:
            logger.error(f"Error collecting China publications: {e}")
            collection_stats['errors'] += 1

        # Search for additional MCF content
        try:
            search_docs = self.search_ndu_mcf_content()
            all_documents.extend(search_docs)
            collection_stats['search_docs'] = len(search_docs)
        except Exception as e:
            logger.error(f"Error searching MCF content: {e}")
            collection_stats['errors'] += 1

        # Calculate final statistics
        collection_stats['total_documents'] = len(all_documents)
        collection_stats['high_relevance_docs'] = sum(
            1 for doc in all_documents if doc.get('mcf_relevance_score', 0) >= 0.7
        )

        # Count PLA-specific documents
        collection_stats['pla_specific_docs'] = sum(
            1 for doc in all_documents
            if any(pla_entity.lower() in doc.get('content_text', '').lower()
                   for pla_entity in self.pla_entities)
        )

        collection_stats['end_time'] = datetime.now().isoformat()

        # Get updated database statistics
        db_stats = self.get_mcf_statistics()

        logger.info(f"""
NDU CSCMA MCF Collection Complete:
- CSP documents: {collection_stats['csp_docs']}
- China publications: {collection_stats['china_pub_docs']}
- Search documents: {collection_stats['search_docs']}
- Total collected: {collection_stats['total_documents']}
- High relevance (>0.7): {collection_stats['high_relevance_docs']}
- PLA-specific: {collection_stats['pla_specific_docs']}
- Total MCF documents in database: {db_stats.get('total_documents', 0)}
        """)

        return {
            'collection_stats': collection_stats,
            'database_stats': db_stats,
            'documents': all_documents
        }

def main():
    """Run NDU CSCMA MCF collection"""
    collector = NDUCSCMACollector()
    results = collector.collect_all_mcf_content()

    # Save collection report
    output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_ndu_cscma")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"ndu_cscma_mcf_collection_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"NDU CSCMA MCF collection report saved to: {report_file}")

if __name__ == "__main__":
    main()
