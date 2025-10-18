#!/usr/bin/env python3
"""
Atlantic Council MCF Collector
Collects Military-Civil Fusion content from Atlantic Council
Priority: HIGH (Tier 3) - Supply chain mapping, defense industrial base analysis
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

class AtlanticCouncilMCFCollector(MCFBaseCollector):
    """Atlantic Council MCF intelligence collector for supply chain analysis"""

    def __init__(self):
        super().__init__()
        self.source_id = "atlantic_council"
        self.base_url = "https://www.atlanticcouncil.org"

        # Key Atlantic Council URLs
        self.council_urls = [
            "/programs/scowcroft-center-for-strategy-and-security/",
            "/programs/global-china-hub/",
            "/programs/geoeconomics-center/",
            "/category/defense-industrial-base/",
            "/category/supply-chains/",
            "/category/china/"
        ]

        # Atlantic Council publication types
        self.publication_types = [
            r"Issue Brief",
            r"Atlantic Council.*Report",
            r"Strategy Paper",
            r"Policy Brief",
            r"Working Paper",
            r"In-Depth Research"
        ]

        # MCF-specific search terms for Atlantic Council
        self.mcf_search_terms = [
            "China supply chain",
            "defense industrial base",
            "critical minerals China",
            "technology competition",
            "economic coercion China",
            "supply chain resilience",
            "friend-shoring",
            "semiconductor supply chain"
        ]

        # Supply chain focus areas
        self.supply_chain_areas = [
            'rare earth elements', 'critical minerals', 'lithium', 'cobalt',
            'semiconductor manufacturing', 'chip fabrication', 'wafer production',
            'defense supply chain', 'military logistics', 'defense contractors',
            'pharmaceutical supply chain', 'active pharmaceutical ingredients', 'API',
            'battery supply chain', 'energy storage', 'EV batteries',
            'telecommunications equipment', '5G infrastructure', 'network equipment',
            'solar panels', 'wind turbines', 'renewable energy components'
        ]

        # Defense industrial base entities
        self.defense_industrial_entities = [
            'Lockheed Martin', 'Boeing', 'Raytheon', 'Northrop Grumman',
            'General Dynamics', 'BAE Systems', 'L3Harris', 'Huntington Ingalls',
            'DCMA', 'Defense Contract Management Agency',
            'DIU', 'Defense Innovation Unit',
            'DARPA', 'Defense Advanced Research Projects Agency',
            'defense prime contractors', 'defense subcontractors',
            'ITAR', 'export controls', 'CFIUS'
        ]

        # Geopolitical supply chain terms
        self.geopolitical_terms = [
            'friend-shoring', 'near-shoring', 'on-shoring', 'reshoring',
            'supply chain resilience', 'supply chain security',
            'economic security', 'economic statecraft',
            'technology decoupling', 'selective decoupling',
            'CHIPS Act', 'Inflation Reduction Act', 'IRA',
            'EU Critical Raw Materials Act', 'economic coercion'
        ]

    def extract_atlantic_council_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from Atlantic Council publication"""
        metadata = {
            'title': 'Unknown Title',
            'publication_date': None,
            'authors': [],
            'document_type': 'analysis',
            'publication_type': None,
            'program': None,
            'topic_areas': [],
            'classification': 'unclassified'
        }

        # Extract title
        title_selectors = [
            'h1.entry-title',
            'h1.post-title',
            'h1.page-title',
            'h1',
            '.article-title',
            'title'
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                title_text = re.sub(r'\s+', ' ', title_text)
                metadata['title'] = title_text
                break

        # Extract publication date
        page_text = soup.get_text()

        date_patterns = [
            r'Published[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
            r'(\w+\s+\d{1,2},?\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                date_str = match.group(1)
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
                authors = []
                for author in re.split(r'[,;&]|\sand\s', authors_text):
                    author = author.strip()
                    if author and len(author) > 2:
                        author = re.sub(r'^(Dr|Professor|PhD)\.?\s*', '', author)
                        authors.append(author)
                metadata['authors'] = authors[:3]
                break

        # Determine publication type and program
        url_lower = url.lower()
        page_text_lower = page_text.lower()

        # Check for program affiliation
        if 'scowcroft' in url_lower or 'scowcroft center' in page_text_lower:
            metadata['program'] = 'Scowcroft Center for Strategy and Security'
        elif 'china-hub' in url_lower or 'global china hub' in page_text_lower:
            metadata['program'] = 'Global China Hub'
        elif 'geoeconomics' in url_lower:
            metadata['program'] = 'GeoEconomics Center'

        # Check publication type
        if 'issue-brief' in url_lower or 'issue brief' in page_text_lower:
            metadata['publication_type'] = 'Issue Brief'
            metadata['document_type'] = 'issue_brief'
        elif 'report' in url_lower:
            metadata['publication_type'] = 'Report'
            metadata['document_type'] = 'report'
        elif 'strategy-paper' in url_lower:
            metadata['publication_type'] = 'Strategy Paper'
            metadata['document_type'] = 'strategy_paper'

        # Extract topic areas
        topic_indicators = []
        for area in self.supply_chain_areas:
            if area.lower() in page_text_lower:
                topic_indicators.append(area)

        for term in self.geopolitical_terms:
            if term.lower() in page_text_lower:
                topic_indicators.append(term)

        metadata['topic_areas'] = list(set(topic_indicators))[:5]

        return metadata

    def collect_china_hub_content(self) -> list:
        """Collect Global China Hub content"""
        logger.info("Collecting Atlantic Council Global China Hub content")
        documents = []

        china_hub_url = urljoin(self.base_url, "/programs/global-china-hub/")

        response = self.fetch_url_with_retry(china_hub_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find publication links
        pub_links = soup.find_all('a', href=True)
        china_pub_urls = []

        for link in pub_links:
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for China-related content
            china_indicators = ['china', 'chinese', 'supply chain', 'technology', 'defense']
            if any(indicator in link_text.lower() for indicator in china_indicators):
                if href not in china_pub_urls and self.base_url in href:
                    china_pub_urls.append(href)

        logger.info(f"Found {len(china_pub_urls)} potential China Hub publications")

        # Process publications
        for pub_url in china_pub_urls[:20]:  # Limit collection
            try:
                pub_response = self.fetch_url_with_retry(pub_url)
                if not pub_response:
                    continue

                pub_soup = BeautifulSoup(pub_response.text, 'html.parser')
                content_text = pub_soup.get_text()

                # Calculate MCF relevance with supply chain bonus
                mcf_score = self.calculate_mcf_relevance(content_text)

                # Supply chain bonus
                supply_bonus = 0
                for area in self.supply_chain_areas:
                    if area.lower() in content_text.lower():
                        supply_bonus += 0.05

                # Defense industrial base bonus
                defense_bonus = 0
                for entity in self.defense_industrial_entities:
                    if entity.lower() in content_text.lower():
                        defense_bonus += 0.05

                mcf_score = min(mcf_score + supply_bonus + defense_bonus, 1.0)

                if mcf_score >= 0.3:
                    metadata = self.extract_atlantic_council_metadata(pub_soup, pub_url)

                    document_data = self.process_document(
                        pub_url,
                        self.source_id,
                        **metadata
                    )

                    if document_data:
                        documents.append(document_data)
                        logger.info(f"Collected China Hub document: {metadata['title'][:50]}... (Score: {mcf_score:.3f})")

            except Exception as e:
                logger.error(f"Error processing China Hub publication {pub_url}: {e}")

        return documents

    def collect_supply_chain_content(self) -> list:
        """Collect supply chain focused content"""
        logger.info("Collecting Atlantic Council supply chain content")
        documents = []

        supply_chain_urls = [
            "/category/supply-chains/",
            "/category/defense-industrial-base/",
            "/programs/geoeconomics-center/"
        ]

        for supply_url_path in supply_chain_urls:
            try:
                supply_url = urljoin(self.base_url, supply_url_path)
                response = self.fetch_url_with_retry(supply_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)

                for link in links[:10]:  # Limit per category
                    href = link['href']
                    link_text = link.get_text(strip=True)

                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)

                    # Filter for supply chain content
                    if any(term in link_text.lower() for term in ['supply', 'chain', 'industrial', 'manufacturing']):
                        try:
                            document_data = self.process_document(href, self.source_id)

                            if document_data and document_data['mcf_relevance_score'] >= 0.4:
                                documents.append(document_data)
                                logger.info(f"Collected supply chain document: {document_data.get('title', 'Unknown')[:40]}...")

                        except Exception as e:
                            logger.error(f"Error processing supply chain document {href}: {e}")

            except Exception as e:
                logger.error(f"Error collecting from {supply_url_path}: {e}")

        return documents

    def search_atlantic_council_mcf(self) -> list:
        """Search Atlantic Council for MCF content"""
        logger.info("Searching Atlantic Council for MCF content")
        documents = []

        for search_term in self.mcf_search_terms:
            try:
                # Atlantic Council search
                search_url = f"{self.base_url}/search/?q={search_term.replace(' ', '+')}"

                response = self.fetch_url_with_retry(search_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
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
                            logger.info(f"Found Atlantic Council MCF search result: {document_data.get('title', 'Unknown')[:40]}...")

                    except Exception as e:
                        logger.error(f"Error processing search result {href}: {e}")

            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")

        return documents

    def collect_all_mcf_content(self) -> dict:
        """Collect all Atlantic Council MCF content"""
        logger.info("Starting Atlantic Council MCF collection")

        all_documents = []
        collection_stats = {
            'source': 'Atlantic Council',
            'start_time': datetime.now().isoformat(),
            'china_hub_docs': 0,
            'supply_chain_docs': 0,
            'search_docs': 0,
            'total_documents': 0,
            'high_relevance_docs': 0,
            'supply_chain_focus_docs': 0,
            'defense_industrial_docs': 0,
            'errors': 0
        }

        # Collect China Hub content
        try:
            china_docs = self.collect_china_hub_content()
            all_documents.extend(china_docs)
            collection_stats['china_hub_docs'] = len(china_docs)
        except Exception as e:
            logger.error(f"Error collecting China Hub content: {e}")
            collection_stats['errors'] += 1

        # Collect supply chain content
        try:
            supply_docs = self.collect_supply_chain_content()
            all_documents.extend(supply_docs)
            collection_stats['supply_chain_docs'] = len(supply_docs)
        except Exception as e:
            logger.error(f"Error collecting supply chain content: {e}")
            collection_stats['errors'] += 1

        # Search for additional content
        try:
            search_docs = self.search_atlantic_council_mcf()
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

        # Count supply chain focused documents
        collection_stats['supply_chain_focus_docs'] = sum(
            1 for doc in all_documents
            if any(area.lower() in doc.get('content_text', '').lower()
                   for area in self.supply_chain_areas)
        )

        # Count defense industrial documents
        collection_stats['defense_industrial_docs'] = sum(
            1 for doc in all_documents
            if any(entity.lower() in doc.get('content_text', '').lower()
                   for entity in self.defense_industrial_entities)
        )

        collection_stats['end_time'] = datetime.now().isoformat()

        # Get updated database statistics
        db_stats = self.get_mcf_statistics()

        logger.info(f"""
Atlantic Council MCF Collection Complete:
- China Hub documents: {collection_stats['china_hub_docs']}
- Supply chain documents: {collection_stats['supply_chain_docs']}
- Search documents: {collection_stats['search_docs']}
- Total collected: {collection_stats['total_documents']}
- High relevance (>0.7): {collection_stats['high_relevance_docs']}
- Supply chain focus: {collection_stats['supply_chain_focus_docs']}
- Defense industrial focus: {collection_stats['defense_industrial_docs']}
- Total MCF documents in database: {db_stats.get('total_documents', 0)}
        """)

        return {
            'collection_stats': collection_stats,
            'database_stats': db_stats,
            'documents': all_documents
        }

def main():
    """Run Atlantic Council MCF collection"""
    collector = AtlanticCouncilMCFCollector()
    results = collector.collect_all_mcf_content()

    # Save collection report
    output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_atlantic_council")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"atlantic_council_mcf_collection_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Atlantic Council MCF collection report saved to: {report_file}")

if __name__ == "__main__":
    main()
