#!/usr/bin/env python3
"""
MERICS MCF Collector
Collects Military-Civil Fusion content from Mercator Institute for China Studies
Priority: HIGH (Tier 2) - Economic analysis, industrial policy, technology competition
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

class MERICSMCFCollector(MCFBaseCollector):
    """MERICS MCF intelligence collector for economic and industrial analysis"""

    def __init__(self):
        super().__init__()
        self.source_id = "merics"
        self.base_url = "https://merics.org"

        # Key MERICS URLs
        self.merics_urls = [
            "/en/analysis/",
            "/en/tracker/",
            "/en/short-analysis/",
            "/en/china-monitor/",
            "/en/report/",
            "/en/briefing/"
        ]

        # MERICS publication types
        self.publication_types = [
            r"China Monitor",
            r"MERICS.*Brief",
            r"Short.*Analysis",
            r"China.*Tracker",
            r"Report",
            r"Analysis"
        ]

        # MCF-specific search terms for MERICS
        self.mcf_search_terms = [
            "Chinese industrial policy",
            "Made in China 2025",
            "dual circulation strategy",
            "Chinese state capitalism",
            "technology transfer China",
            "Chinese innovation system",
            "China semiconductor strategy",
            "Chinese digital economy"
        ]

        # Economic and industrial entities
        self.economic_entities = [
            'State Council', 'NDRC', 'MIIT', 'SASAC',
            'Ministry of Commerce', 'MOFCOM',
            'People\'s Bank of China', 'PBOC',
            'China Securities Regulatory Commission', 'CSRC',
            'National Development and Reform Commission',
            'State-owned Assets Supervision', 'Administration Commission',
            'China Investment Corporation', 'CIC',
            'China Development Bank', 'CDB',
            'Export-Import Bank of China'
        ]

        # Industrial policy areas
        self.industrial_policies = [
            'Made in China 2025', 'MiC 2025',
            'dual circulation', 'dual circulation strategy',
            'indigenous innovation', 'technological self-reliance',
            'national champions', 'state-owned enterprises',
            'industrial upgrading', 'value chain upgrading',
            'digital economy', 'digital transformation',
            'green development', 'carbon neutrality',
            'Belt and Road Initiative', 'BRI'
        ]

        # Technology sectors tracked by MERICS
        self.tech_sectors = [
            'artificial intelligence', 'AI',
            'electric vehicles', 'EVs', 'new energy vehicles',
            'renewable energy', 'solar', 'wind power',
            'telecommunications', '5G', '6G',
            'semiconductors', 'integrated circuits',
            'biotechnology', 'pharmaceuticals',
            'advanced manufacturing', 'Industry 4.0',
            'fintech', 'digital payments'
        ]

    def extract_merics_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from MERICS publication"""
        metadata = {
            'title': 'Unknown Title',
            'publication_date': None,
            'authors': [],
            'document_type': 'analysis',
            'publication_type': None,
            'topic_areas': [],
            'geographic_focus': [],
            'classification': 'unclassified'
        }

        # Extract title
        title_selectors = [
            'h1.entry-title',
            'h1.article-title',
            'h1.page-title',
            'h1',
            '.post-title',
            'title'
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                title_text = re.sub(r'\\s+', ' ', title_text)
                metadata['title'] = title_text
                break

        # Extract publication date
        page_text = soup.get_text()

        # MERICS often uses German date formats
        date_patterns = [
            r'(\\d{1,2}\\.\\d{1,2}\\.\\d{4})',  # German format: 15.01.2024
            r'(\\w+\\s+\\d{1,2},?\\s+\\d{4})',  # English format: January 15, 2024
            r'(\\d{1,2}/\\d{1,2}/\\d{4})',  # US format: 1/15/2024
            r'(\\d{4}-\\d{2}-\\d{2})'  # ISO format: 2024-01-15
        ]

        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                date_str = match.group(1)
                try:
                    for fmt in ['%d.%m.%Y', '%B %d, %Y', '%B %d %Y', '%m/%d/%Y', '%Y-%m-%d']:
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
            '.post-author',
            '.article-author',
            '.contributors'
        ]

        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                authors_text = author_elem.get_text(strip=True)
                # Split by common separators
                authors = []
                for author in re.split(r'[,;&]|\\sand\\s', authors_text):
                    author = author.strip()
                    if author and len(author) > 2:
                        # Remove titles
                        author = re.sub(r'^(Dr|Professor|PhD)\\.?\\s*', '', author)
                        authors.append(author)

                metadata['authors'] = authors[:3]  # Limit to 3 authors
                break

        # Determine publication type
        url_lower = url.lower()
        page_text_lower = page_text.lower()

        if 'china-monitor' in url_lower or 'china monitor' in page_text_lower:
            metadata['publication_type'] = 'China Monitor'
            metadata['document_type'] = 'monitor'
        elif 'short-analysis' in url_lower or 'short analysis' in page_text_lower:
            metadata['publication_type'] = 'Short Analysis'
            metadata['document_type'] = 'short_analysis'
        elif 'briefing' in url_lower:
            metadata['publication_type'] = 'Briefing'
            metadata['document_type'] = 'briefing'
        elif 'tracker' in url_lower:
            metadata['publication_type'] = 'Tracker'
            metadata['document_type'] = 'tracker'
        elif 'report' in url_lower:
            metadata['publication_type'] = 'Report'
            metadata['document_type'] = 'report'

        # Extract topic areas
        topic_indicators = []
        for policy in self.industrial_policies:
            if policy.lower() in page_text_lower:
                topic_indicators.append(policy)

        for sector in self.tech_sectors:
            if sector.lower() in page_text_lower:
                topic_indicators.append(sector)

        metadata['topic_areas'] = list(set(topic_indicators))[:5]  # Limit topics

        # Extract geographic focus
        geographic_terms = ['China', 'Chinese', 'Beijing', 'Shanghai', 'Shenzhen',
                           'Guangzhou', 'Europe', 'Germany', 'EU', 'United States']
        geographic_focus = []
        for term in geographic_terms:
            if term.lower() in page_text_lower:
                geographic_focus.append(term)

        metadata['geographic_focus'] = list(set(geographic_focus))[:3]

        return metadata

    def collect_merics_analysis(self) -> list:
        """Collect MERICS analysis publications"""
        logger.info("Collecting MERICS analysis")
        documents = []

        analysis_url = urljoin(self.base_url, "/en/analysis/")

        response = self.fetch_url_with_retry(analysis_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find analysis links
        analysis_links = soup.find_all('a', href=True)
        analysis_urls = []

        for link in analysis_links:
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for analysis content
            if any(term in link_text.lower() for term in ['china', 'chinese', 'technology', 'economy', 'policy']):
                if href not in analysis_urls and self.base_url in href:
                    analysis_urls.append(href)

        logger.info(f"Found {len(analysis_urls)} potential MERICS analysis documents")

        # Process analysis documents
        for analysis_url in analysis_urls[:20]:  # Limit collection
            try:
                analysis_response = self.fetch_url_with_retry(analysis_url)
                if not analysis_response:
                    continue

                analysis_soup = BeautifulSoup(analysis_response.text, 'html.parser')
                content_text = analysis_soup.get_text()

                # Calculate MCF relevance with economic policy bonus
                mcf_score = self.calculate_mcf_relevance(content_text)

                # Economic policy bonus
                policy_bonus = 0
                for policy in self.industrial_policies:
                    if policy.lower() in content_text.lower():
                        policy_bonus += 0.05

                # Economic entity bonus
                entity_bonus = 0
                for entity in self.economic_entities:
                    if entity.lower() in content_text.lower():
                        entity_bonus += 0.05

                mcf_score = min(mcf_score + policy_bonus + entity_bonus, 1.0)

                if mcf_score >= 0.3:  # Threshold for MERICS content
                    metadata = self.extract_merics_metadata(analysis_soup, analysis_url)

                    document_data = self.process_document(
                        analysis_url,
                        self.source_id,
                        **metadata
                    )

                    if document_data:
                        documents.append(document_data)
                        logger.info(f"Collected MERICS analysis: {metadata['title'][:50]}... (Score: {mcf_score:.3f})")

            except Exception as e:
                logger.error(f"Error processing MERICS analysis {analysis_url}: {e}")

        return documents

    def collect_china_monitor(self) -> list:
        """Collect China Monitor series"""
        logger.info("Collecting MERICS China Monitor")
        documents = []

        monitor_url = urljoin(self.base_url, "/en/china-monitor/")

        response = self.fetch_url_with_retry(monitor_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find China Monitor links
        monitor_links = soup.find_all('a', href=True)

        for link in monitor_links[:15]:  # Limit monitor documents
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for China Monitor content
            if 'monitor' in link_text.lower() or 'china' in link_text.lower():
                try:
                    document_data = self.process_document(href, self.source_id)

                    if document_data and document_data['mcf_relevance_score'] >= 0.4:
                        documents.append(document_data)
                        logger.info(f"Collected China Monitor: {document_data.get('title', 'Unknown')[:40]}...")

                except Exception as e:
                    logger.error(f"Error processing China Monitor {href}: {e}")

        return documents

    def collect_merics_trackers(self) -> list:
        """Collect MERICS tracker data"""
        logger.info("Collecting MERICS trackers")
        documents = []

        tracker_url = urljoin(self.base_url, "/en/tracker/")

        response = self.fetch_url_with_retry(tracker_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find tracker links
        tracker_links = soup.find_all('a', href=True)

        for link in tracker_links[:10]:  # Limit tracker documents
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for tracker content
            if any(term in link_text.lower() for term in ['tracker', 'data', 'investment', 'technology']):
                try:
                    document_data = self.process_document(href, self.source_id)

                    if document_data and document_data['mcf_relevance_score'] >= 0.3:
                        documents.append(document_data)
                        logger.info(f"Collected MERICS tracker: {document_data.get('title', 'Unknown')[:40]}...")

                except Exception as e:
                    logger.error(f"Error processing tracker {href}: {e}")

        return documents

    def search_merics_mcf_content(self) -> list:
        """Search MERICS for MCF content"""
        logger.info("Searching MERICS for MCF content")
        documents = []

        for search_term in self.mcf_search_terms:
            try:
                # MERICS search functionality
                search_url = f"{self.base_url}/en/search?q={search_term.replace(' ', '+')}"

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
                            logger.info(f"Found MERICS MCF search result: {document_data.get('title', 'Unknown')[:40]}...")

                    except Exception as e:
                        logger.error(f"Error processing search result {href}: {e}")

            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")

        return documents

    def collect_all_mcf_content(self) -> dict:
        """Collect all MERICS MCF content"""
        logger.info("Starting MERICS MCF collection")

        all_documents = []
        collection_stats = {
            'source': 'MERICS',
            'start_time': datetime.now().isoformat(),
            'analysis_docs': 0,
            'monitor_docs': 0,
            'tracker_docs': 0,
            'search_docs': 0,
            'total_documents': 0,
            'high_relevance_docs': 0,
            'industrial_policy_docs': 0,
            'economic_entity_docs': 0,
            'errors': 0
        }

        # Collect analysis documents
        try:
            analysis_docs = self.collect_merics_analysis()
            all_documents.extend(analysis_docs)
            collection_stats['analysis_docs'] = len(analysis_docs)
        except Exception as e:
            logger.error(f"Error collecting analysis: {e}")
            collection_stats['errors'] += 1

        # Collect China Monitor
        try:
            monitor_docs = self.collect_china_monitor()
            all_documents.extend(monitor_docs)
            collection_stats['monitor_docs'] = len(monitor_docs)
        except Exception as e:
            logger.error(f"Error collecting China Monitor: {e}")
            collection_stats['errors'] += 1

        # Collect trackers
        try:
            tracker_docs = self.collect_merics_trackers()
            all_documents.extend(tracker_docs)
            collection_stats['tracker_docs'] = len(tracker_docs)
        except Exception as e:
            logger.error(f"Error collecting trackers: {e}")
            collection_stats['errors'] += 1

        # Search for additional content
        try:
            search_docs = self.search_merics_mcf_content()
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

        # Count industrial policy documents
        collection_stats['industrial_policy_docs'] = sum(
            1 for doc in all_documents
            if any(policy.lower() in doc.get('content_text', '').lower()
                   for policy in self.industrial_policies)
        )

        # Count economic entity documents
        collection_stats['economic_entity_docs'] = sum(
            1 for doc in all_documents
            if any(entity.lower() in doc.get('content_text', '').lower()
                   for entity in self.economic_entities)
        )

        collection_stats['end_time'] = datetime.now().isoformat()

        # Get updated database statistics
        db_stats = self.get_mcf_statistics()

        logger.info(f"""
MERICS MCF Collection Complete:
- Analysis documents: {collection_stats['analysis_docs']}
- China Monitor documents: {collection_stats['monitor_docs']}
- Tracker documents: {collection_stats['tracker_docs']}
- Search documents: {collection_stats['search_docs']}
- Total collected: {collection_stats['total_documents']}
- High relevance (>0.7): {collection_stats['high_relevance_docs']}
- Industrial policy focus: {collection_stats['industrial_policy_docs']}
- Economic entity focus: {collection_stats['economic_entity_docs']}
- Total MCF documents in database: {db_stats.get('total_documents', 0)}
        """)

        return {
            'collection_stats': collection_stats,
            'database_stats': db_stats,
            'documents': all_documents
        }

def main():
    """Run MERICS MCF collection"""
    collector = MERICSMCFCollector()
    results = collector.collect_all_mcf_content()

    # Save collection report
    output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_merics")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"merics_mcf_collection_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"MERICS MCF collection report saved to: {report_file}")

if __name__ == "__main__":
    main()
