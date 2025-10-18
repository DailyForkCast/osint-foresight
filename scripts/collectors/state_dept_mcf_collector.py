#!/usr/bin/env python3
"""
State Department MCF Collector
Collects Military-Civil Fusion related content from State Department
Priority: HIGHEST (Tier 1)
"""

import re
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

class StateDeptMCFCollector(MCFBaseCollector):
    """State Department MCF intelligence collector"""

    def __init__(self):
        super().__init__()
        self.source_id = "state_dept"
        self.base_url = "https://www.state.gov"

        # Key State Department MCF URLs
        self.mcf_urls = [
            "/military-civil-fusion/",
            "/key-topics/economic-prosperity/business-engagement/",
            "/bureaus-offices/economic-and-business-affairs/",
            "/policy-issues/economic-prosperity/",
            "/policy-issues/regional-security/"
        ]

        # MCF-specific search terms for State Dept
        self.mcf_search_terms = [
            "military civil fusion",
            "dual-use technology",
            "technology transfer China",
            "Chinese defense companies",
            "export controls China"
        ]

    def extract_document_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from State Department page"""
        metadata = {
            'title': 'Unknown Title',
            'publication_date': None,
            'authors': [],
            'document_type': 'webpage',
            'bureau': None
        }

        # Extract title
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)

        # Extract publication date
        date_selectors = [
            '.entry-date',
            '.date',
            '.publication-date',
            'time[datetime]',
            '.post-date'
        ]

        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                try:
                    # Try to parse various date formats
                    if 'T' in date_text:
                        parsed_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                    else:
                        parsed_date = datetime.strptime(date_text, '%B %d, %Y')
                    metadata['publication_date'] = parsed_date.date().isoformat()
                    break
                except ValueError:
                    continue

        # Extract bureau/office information
        bureau_indicators = [
            'Bureau of Economic and Business Affairs',
            'Bureau of International Security',
            'Bureau of Political-Military Affairs',
            'Office of Economic Sanctions Policy'
        ]

        page_text = soup.get_text()
        for bureau in bureau_indicators:
            if bureau in page_text:
                metadata['bureau'] = bureau
                break

        # Determine document type
        if '/press-releases/' in url:
            metadata['document_type'] = 'press_release'
        elif '/reports/' in url:
            metadata['document_type'] = 'report'
        elif '/fact-sheets/' in url:
            metadata['document_type'] = 'fact_sheet'
        elif '/speeches/' in url:
            metadata['document_type'] = 'speech'
        elif '/testimony/' in url:
            metadata['document_type'] = 'testimony'

        return metadata

    def collect_mcf_page(self, mcf_path: str) -> list:
        """Collect MCF documents from a specific State Dept path"""
        url = urljoin(self.base_url, mcf_path)
        logger.info(f"Collecting MCF content from: {url}")

        response = self.fetch_url_with_retry(url)
        if not response:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        documents = []

        # Find all links that might contain MCF content
        links = soup.find_all('a', href=True)
        mcf_links = []

        for link in links:
            href = link['href']
            link_text = link.get_text(strip=True).lower()

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)
            elif not href.startswith('http'):
                continue

            # Filter for MCF-relevant links
            mcf_relevant = False

            # Check link text for MCF keywords
            for term in self.mcf_search_terms:
                if term.lower() in link_text:
                    mcf_relevant = True
                    break

            # Check URL path for MCF indicators
            mcf_path_indicators = [
                'china', 'military', 'defense', 'dual-use', 'export-control',
                'technology', 'sanctions', 'entity-list'
            ]

            for indicator in mcf_path_indicators:
                if indicator in href.lower():
                    mcf_relevant = True
                    break

            if mcf_relevant and href not in mcf_links:
                mcf_links.append(href)

        # Process each MCF-relevant link
        for link_url in mcf_links[:20]:  # Limit to prevent overwhelming
            try:
                link_response = self.fetch_url_with_retry(link_url)
                if not link_response:
                    continue

                link_soup = BeautifulSoup(link_response.text, 'html.parser')
                content_text = link_soup.get_text()

                # Calculate MCF relevance
                mcf_score = self.calculate_mcf_relevance(content_text)

                if mcf_score >= 0.3:  # Higher threshold for State Dept
                    metadata = self.extract_document_metadata(link_soup, link_url)

                    document_data = self.process_document(
                        link_url,
                        self.source_id,
                        **metadata
                    )

                    if document_data:
                        documents.append(document_data)
                        logger.info(f"Collected MCF document: {metadata['title'][:60]}... (Score: {mcf_score:.3f})")

            except Exception as e:
                logger.error(f"Error processing link {link_url}: {e}")
                continue

        return documents

    def search_state_dept_mcf(self, search_term: str, max_results: int = 10) -> list:
        """Search State Department site for MCF content"""
        # State Dept search URL pattern
        search_url = f"https://www.state.gov/search/?query={search_term.replace(' ', '+')}"

        logger.info(f"Searching State Dept for: {search_term}")

        response = self.fetch_url_with_retry(search_url)
        if not response:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        documents = []

        # Find search result links
        result_links = soup.find_all('a', href=True)
        processed_urls = set()

        for link in result_links[:max_results]:
            href = link['href']

            # Skip non-content URLs
            if any(skip in href for skip in ['javascript:', 'mailto:', '#', 'pdf']):
                continue

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            if href in processed_urls:
                continue
            processed_urls.add(href)

            try:
                # Process the search result page
                document_data = self.process_document(href, self.source_id)

                if document_data and document_data['mcf_relevance_score'] >= 0.4:
                    documents.append(document_data)
                    logger.info(f"Found MCF search result: {document_data.get('title', 'Unknown')[:50]}...")

            except Exception as e:
                logger.error(f"Error processing search result {href}: {e}")
                continue

        return documents

    def collect_all_mcf_content(self) -> dict:
        """Collect all State Department MCF content"""
        logger.info("Starting State Department MCF collection")

        all_documents = []
        collection_stats = {
            'source': 'State Department',
            'start_time': datetime.now().isoformat(),
            'urls_processed': 0,
            'documents_collected': 0,
            'high_relevance_docs': 0,
            'errors': 0
        }

        # Collect from known MCF URLs
        for mcf_path in self.mcf_urls:
            try:
                documents = self.collect_mcf_page(mcf_path)
                all_documents.extend(documents)
                collection_stats['urls_processed'] += 1

            except Exception as e:
                logger.error(f"Error collecting from {mcf_path}: {e}")
                collection_stats['errors'] += 1

        # Search for additional MCF content
        for search_term in self.mcf_search_terms:
            try:
                search_documents = self.search_state_dept_mcf(search_term, max_results=5)
                all_documents.extend(search_documents)

            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")
                collection_stats['errors'] += 1

        # Calculate final statistics
        collection_stats['documents_collected'] = len(all_documents)
        collection_stats['high_relevance_docs'] = sum(
            1 for doc in all_documents if doc.get('mcf_relevance_score', 0) >= 0.7
        )
        collection_stats['end_time'] = datetime.now().isoformat()

        # Get updated database statistics
        db_stats = self.get_mcf_statistics()

        logger.info(f"""
State Department MCF Collection Complete:
- Documents collected: {collection_stats['documents_collected']}
- High relevance (>0.7): {collection_stats['high_relevance_docs']}
- Errors encountered: {collection_stats['errors']}
- Total MCF documents in database: {db_stats.get('total_documents', 0)}
        """)

        return {
            'collection_stats': collection_stats,
            'database_stats': db_stats,
            'documents': all_documents
        }

def main():
    """Run State Department MCF collection"""
    collector = StateDeptMCFCollector()
    results = collector.collect_all_mcf_content()

    # Save collection report
    output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_state_dept")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"state_dept_mcf_collection_{timestamp}.json"

    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Collection report saved to: {report_file}")

if __name__ == "__main__":
    main()
