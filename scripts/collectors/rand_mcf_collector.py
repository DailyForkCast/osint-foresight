#!/usr/bin/env python3
"""
RAND Corporation MCF Collector
Collects Military-Civil Fusion content from RAND Corporation
Priority: HIGH (Tier 2) - Strategic analysis, defense policy, technology assessment
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

class RANDMCFCollector(MCFBaseCollector):
    """RAND Corporation MCF intelligence collector for strategic analysis"""

    def __init__(self):
        super().__init__()
        self.source_id = "rand"
        self.base_url = "https://www.rand.org"

        # Key RAND URLs
        self.rand_urls = [
            "/topics/china.html",
            "/topics/national-security.html",
            "/topics/military-technology.html",
            "/topics/defense-strategy.html",
            "/pubs/research_reports/",
            "/pubs/perspectives/",
            "/pubs/testimonies/"
        ]

        # RAND publication types
        self.publication_types = [
            r"Research Report",
            r"RR-\\d+",
            r"Perspective",
            r"PE-\\d+",
            r"Testimony",
            r"CT-\\d+",
            r"Working Paper",
            r"WR-\\d+"
        ]

        # MCF-specific search terms for RAND
        self.mcf_search_terms = [
            "China military modernization",
            "Chinese defense industry",
            "technology competition China",
            "Chinese military capabilities",
            "PLA modernization",
            "dual-use technology China",
            "Chinese innovation system",
            "China strategic competition"
        ]

        # Defense and security focus areas
        self.defense_areas = [
            'strategic competition', 'great power competition',
            'military modernization', 'defense transformation',
            'emerging technologies', 'disruptive technologies',
            'artificial intelligence', 'AI warfare',
            'cyber warfare', 'information operations',
            'space warfare', 'counter-space capabilities',
            'hypersonic weapons', 'precision strike',
            'electronic warfare', 'signal intelligence'
        ]

        # Chinese military and strategic entities
        self.chinese_strategic_entities = [
            'People\'s Liberation Army', 'PLA',
            'Central Military Commission', 'CMC',
            'PLA Army', 'PLAA', 'PLA Navy', 'PLAN',
            'PLA Air Force', 'PLAAF', 'PLA Rocket Force', 'PLARF',
            'Strategic Support Force', 'SSF',
            'Ministry of National Defense', 'MND',
            'Equipment Development Department', 'EDD',
            'Academy of Military Science', 'AMS',
            'National University of Defense Technology', 'NUDT'
        ]

        # Technology development areas
        self.tech_development_areas = [
            'directed energy weapons', 'laser weapons',
            'autonomous weapons systems', 'swarming drones',
            'quantum radar', 'quantum communications',
            'biotechnology weapons', 'genetic weapons',
            'nanotechnology applications', 'advanced materials',
            'solid rocket motors', 'scramjet engines',
            'stealth technology', 'counter-stealth'
        ]

    def extract_rand_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from RAND publication"""
        metadata = {
            'title': 'Unknown Title',
            'publication_date': None,
            'authors': [],
            'document_type': 'report',
            'publication_type': None,
            'report_number': None,
            'topic_areas': [],
            'classification': 'unclassified'
        }

        # Extract title
        title_selectors = [
            'h1.product-header__title',
            'h1.page-title',
            'h1',
            '.publication-title',
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

        date_patterns = [
            r'Published[:\\s]+(\\w+\\s+\\d{1,2},?\\s+\\d{4})',
            r'Date[:\\s]+(\\w+\\s+\\d{1,2},?\\s+\\d{4})',
            r'(\\w+\\s+\\d{1,2},?\\s+\\d{4})',
            r'(\\d{1,2}/\\d{1,2}/\\d{4})',
            r'(\\d{4})'  # Year only as fallback
        ]

        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                date_str = match.group(1)
                try:
                    for fmt in ['%B %d, %Y', '%B %d %Y', '%m/%d/%Y', '%Y']:
                        try:
                            if fmt == '%Y':
                                parsed_date = datetime.strptime(date_str + '-01-01', '%Y-%m-%d')
                            else:
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
            '.product-header__authors',
            '.author',
            '.byline',
            '.publication-authors'
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

                metadata['authors'] = authors[:4]  # Limit to 4 authors
                break

        # Extract report number and publication type
        url_lower = url.lower()
        page_text_lower = page_text.lower()

        # RAND report number patterns
        report_patterns = [
            r'(RR-\\d+)',  # Research Report
            r'(PE-\\d+)',  # Perspective
            r'(CT-\\d+)',  # Testimony
            r'(WR-\\d+)',  # Working Paper
            r'(CF-\\d+)',  # Conference Proceedings
            r'(TL-\\d+)'   # Tool
        ]

        for pattern in report_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                metadata['report_number'] = match.group(1).upper()

                # Determine publication type from report number
                if metadata['report_number'].startswith('RR'):
                    metadata['publication_type'] = 'Research Report'
                    metadata['document_type'] = 'research_report'
                elif metadata['report_number'].startswith('PE'):
                    metadata['publication_type'] = 'Perspective'
                    metadata['document_type'] = 'perspective'
                elif metadata['report_number'].startswith('CT'):
                    metadata['publication_type'] = 'Testimony'
                    metadata['document_type'] = 'testimony'
                elif metadata['report_number'].startswith('WR'):
                    metadata['publication_type'] = 'Working Paper'
                    metadata['document_type'] = 'working_paper'
                break

        # If no report number found, determine type from URL/content
        if not metadata['publication_type']:
            if 'testimony' in url_lower:
                metadata['publication_type'] = 'Testimony'
                metadata['document_type'] = 'testimony'
            elif 'perspective' in url_lower:
                metadata['publication_type'] = 'Perspective'
                metadata['document_type'] = 'perspective'
            elif 'research' in url_lower:
                metadata['publication_type'] = 'Research Report'
                metadata['document_type'] = 'research_report'

        # Extract topic areas
        topic_indicators = []
        for area in self.defense_areas:
            if area.lower() in page_text_lower:
                topic_indicators.append(area)

        for tech in self.tech_development_areas:
            if tech.lower() in page_text_lower:
                topic_indicators.append(tech)

        metadata['topic_areas'] = list(set(topic_indicators))[:5]  # Limit topics

        return metadata

    def collect_rand_china_content(self) -> list:
        """Collect RAND content on China"""
        logger.info("Collecting RAND China content")
        documents = []

        china_url = urljoin(self.base_url, "/topics/china.html")

        response = self.fetch_url_with_retry(china_url)
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

            # Filter for publications
            if any(term in href.lower() for term in ['/pubs/', '/research', '/perspective', '/testimony']):
                if href not in china_pub_urls and self.base_url in href:
                    china_pub_urls.append(href)

        logger.info(f"Found {len(china_pub_urls)} potential RAND China publications")

        # Process China publications
        for pub_url in china_pub_urls[:20]:  # Limit collection
            try:
                pub_response = self.fetch_url_with_retry(pub_url)
                if not pub_response:
                    continue

                pub_soup = BeautifulSoup(pub_response.text, 'html.parser')
                content_text = pub_soup.get_text()

                # Calculate MCF relevance with strategic analysis bonus
                mcf_score = self.calculate_mcf_relevance(content_text)

                # Strategic entity bonus
                strategic_bonus = 0
                for entity in self.chinese_strategic_entities:
                    if entity.lower() in content_text.lower():
                        strategic_bonus += 0.05

                # Defense technology bonus
                tech_bonus = 0
                for tech in self.tech_development_areas:
                    if tech.lower() in content_text.lower():
                        tech_bonus += 0.05

                mcf_score = min(mcf_score + strategic_bonus + tech_bonus, 1.0)

                if mcf_score >= 0.3:  # Threshold for RAND content
                    metadata = self.extract_rand_metadata(pub_soup, pub_url)

                    document_data = self.process_document(
                        pub_url,
                        self.source_id,
                        **metadata
                    )

                    if document_data:
                        documents.append(document_data)
                        logger.info(f"Collected RAND China publication: {metadata['title'][:50]}... (Score: {mcf_score:.3f})")

            except Exception as e:
                logger.error(f"Error processing RAND China publication {pub_url}: {e}")

        return documents

    def collect_rand_defense_content(self) -> list:
        """Collect RAND defense and security content"""
        logger.info("Collecting RAND defense content")
        documents = []

        defense_urls = [
            "/topics/national-security.html",
            "/topics/military-technology.html",
            "/topics/defense-strategy.html"
        ]

        for defense_topic_url in defense_urls:
            try:
                topic_url = urljoin(self.base_url, defense_topic_url)
                response = self.fetch_url_with_retry(topic_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find defense publication links
                pub_links = soup.find_all('a', href=True)

                for link in pub_links[:10]:  # Limit per topic
                    href = link['href']
                    link_text = link.get_text(strip=True)

                    # Make absolute URL
                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)

                    # Filter for publications with China/technology focus
                    if any(term in href.lower() for term in ['/pubs/', '/research']) and \
                       any(indicator in link_text.lower() for indicator in ['china', 'technology', 'military', 'strategic']):
                        try:
                            document_data = self.process_document(href, self.source_id)

                            if document_data and document_data['mcf_relevance_score'] >= 0.4:
                                documents.append(document_data)
                                logger.info(f"Collected RAND defense: {document_data.get('title', 'Unknown')[:40]}...")

                        except Exception as e:
                            logger.error(f"Error processing defense document {href}: {e}")

            except Exception as e:
                logger.error(f"Error collecting from {defense_topic_url}: {e}")

        return documents

    def search_rand_mcf_content(self) -> list:
        """Search RAND for MCF content"""
        logger.info("Searching RAND for MCF content")
        documents = []

        for search_term in self.mcf_search_terms:
            try:
                # RAND search functionality
                search_url = f"{self.base_url}/search?query={search_term.replace(' ', '+')}"

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

                    if self.base_url not in href or '/pubs/' not in href:
                        continue

                    try:
                        document_data = self.process_document(href, self.source_id)

                        if document_data and document_data['mcf_relevance_score'] >= 0.5:
                            documents.append(document_data)
                            logger.info(f"Found RAND MCF search result: {document_data.get('title', 'Unknown')[:40]}...")

                    except Exception as e:
                        logger.error(f"Error processing search result {href}: {e}")

            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")

        return documents

    def collect_all_mcf_content(self) -> dict:
        """Collect all RAND MCF content"""
        logger.info("Starting RAND MCF collection")

        all_documents = []
        collection_stats = {
            'source': 'RAND Corporation',
            'start_time': datetime.now().isoformat(),
            'china_docs': 0,
            'defense_docs': 0,
            'search_docs': 0,
            'total_documents': 0,
            'high_relevance_docs': 0,
            'strategic_entity_docs': 0,
            'defense_tech_docs': 0,
            'errors': 0
        }

        # Collect China content
        try:
            china_docs = self.collect_rand_china_content()
            all_documents.extend(china_docs)
            collection_stats['china_docs'] = len(china_docs)
        except Exception as e:
            logger.error(f"Error collecting China content: {e}")
            collection_stats['errors'] += 1

        # Collect defense content
        try:
            defense_docs = self.collect_rand_defense_content()
            all_documents.extend(defense_docs)
            collection_stats['defense_docs'] = len(defense_docs)
        except Exception as e:
            logger.error(f"Error collecting defense content: {e}")
            collection_stats['errors'] += 1

        # Search for additional content
        try:
            search_docs = self.search_rand_mcf_content()
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

        # Count strategic entity documents
        collection_stats['strategic_entity_docs'] = sum(
            1 for doc in all_documents
            if any(entity.lower() in doc.get('content_text', '').lower()
                   for entity in self.chinese_strategic_entities)
        )

        # Count defense technology documents
        collection_stats['defense_tech_docs'] = sum(
            1 for doc in all_documents
            if any(tech.lower() in doc.get('content_text', '').lower()
                   for tech in self.tech_development_areas)
        )

        collection_stats['end_time'] = datetime.now().isoformat()

        # Get updated database statistics
        db_stats = self.get_mcf_statistics()

        logger.info(f"""
RAND MCF Collection Complete:
- China documents: {collection_stats['china_docs']}
- Defense documents: {collection_stats['defense_docs']}
- Search documents: {collection_stats['search_docs']}
- Total collected: {collection_stats['total_documents']}
- High relevance (>0.7): {collection_stats['high_relevance_docs']}
- Strategic entity focus: {collection_stats['strategic_entity_docs']}
- Defense technology focus: {collection_stats['defense_tech_docs']}
- Total MCF documents in database: {db_stats.get('total_documents', 0)}
        """)

        return {
            'collection_stats': collection_stats,
            'database_stats': db_stats,
            'documents': all_documents
        }

def main():
    """Run RAND MCF collection"""
    collector = RANDMCFCollector()
    results = collector.collect_all_mcf_content()

    # Save collection report
    output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_rand")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"rand_mcf_collection_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"RAND MCF collection report saved to: {report_file}")

if __name__ == "__main__":
    main()
