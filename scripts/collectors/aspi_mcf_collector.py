#!/usr/bin/env python3
"""
ASPI MCF Collector
Collects Military-Civil Fusion data from ASPI (Australian Strategic Policy Institute)
Priority: HIGHEST (Tier 1) - Critical Tech Tracker and company mapping
"""

import re
import json
import csv
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

class ASPIMCFCollector(MCFBaseCollector):
    """ASPI MCF intelligence collector focusing on Critical Tech Tracker and company mapping"""

    def __init__(self):
        super().__init__()
        self.source_id = "aspi"
        self.base_url = "https://www.aspi.org.au"

        # Key ASPI MCF URLs and resources
        self.mcf_urls = [
            "/programs/critical-technology-tracker/",
            "/programs/china/",
            "/programs/defense-and-strategy/",
            "/research/technology-governance/",
            "/research/china-technology-capabilities/"
        ]

        # Critical Tech Tracker specific URLs
        self.tech_tracker_urls = [
            "https://unitracker.aspi.org.au/",
            "https://www.aspi.org.au/report/critical-technology-tracker",
            "https://www.aspi.org.au/research/critical-technology-tracker"
        ]

        # MCF-specific search terms for ASPI
        self.mcf_search_terms = [
            "military civil fusion",
            "dual-use technology",
            "Chinese defense companies",
            "technology transfer China",
            "AVIC", "CETC", "NORINCO"
        ]

        # Critical technology categories from ASPI tracker
        self.critical_tech_categories = [
            "Artificial Intelligence",
            "Quantum Computing",
            "Advanced Communications",
            "Hypersonics",
            "Semiconductors",
            "Advanced Materials",
            "Biotechnology",
            "Space Technology",
            "Cyber Security",
            "Autonomous Systems"
        ]

    def extract_aspi_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from ASPI page"""
        metadata = {
            'title': 'Unknown Title',
            'publication_date': None,
            'authors': [],
            'document_type': 'report',
            'program': None,
            'technology_category': None
        }

        # Extract title
        title_selectors = ['h1.entry-title', 'h1', '.post-title', 'title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                metadata['title'] = title_elem.get_text(strip=True)
                break

        # Extract publication date
        date_selectors = [
            '.entry-date',
            '.publication-date',
            '.post-date',
            'time[datetime]',
            '.date'
        ]

        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                try:
                    if 'T' in date_text:
                        parsed_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                    else:
                        # Try various date formats
                        for fmt in ['%B %d, %Y', '%Y-%m-%d', '%d %B %Y']:
                            try:
                                parsed_date = datetime.strptime(date_text, fmt)
                                break
                            except ValueError:
                                continue
                    metadata['publication_date'] = parsed_date.date().isoformat()
                    break
                except (ValueError, NameError):
                    continue

        # Extract authors
        author_selectors = ['.author', '.byline', '.post-author', '.entry-author']
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                authors_text = author_elem.get_text(strip=True)
                # Split by common separators
                authors = [author.strip() for author in re.split(r'[,&]|\band\b', authors_text) if author.strip()]
                metadata['authors'] = authors[:3]  # Limit to 3 authors
                break

        # Determine program/category
        programs = [
            'Critical Technology Tracker',
            'China Program',
            'Defense and Strategy',
            'Technology Governance',
            'International Cyber Policy Centre'
        ]

        page_text = soup.get_text().lower()
        for program in programs:
            if program.lower() in page_text:
                metadata['program'] = program
                break

        # Check for technology categories
        for tech_cat in self.critical_tech_categories:
            if tech_cat.lower() in page_text:
                metadata['technology_category'] = tech_cat
                break

        # Determine document type from URL
        if '/report/' in url:
            metadata['document_type'] = 'report'
        elif '/analysis/' in url:
            metadata['document_type'] = 'analysis'
        elif '/brief/' in url:
            metadata['document_type'] = 'brief'
        elif '/tracker/' in url:
            metadata['document_type'] = 'tracker_data'

        return metadata

    def collect_critical_tech_tracker_data(self) -> list:
        """Collect data from ASPI Critical Technology Tracker"""
        logger.info("Collecting Critical Technology Tracker data from ASPI")
        documents = []

        for tracker_url in self.tech_tracker_urls:
            try:
                response = self.fetch_url_with_retry(tracker_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for CSV/data download links
                download_links = soup.find_all('a', href=True)
                csv_links = []

                for link in download_links:
                    href = link['href']
                    link_text = link.get_text(strip=True).lower()

                    if any(term in href.lower() for term in ['.csv', 'download', 'data']):
                        csv_links.append(urljoin(tracker_url, href))

                    if any(term in link_text for term in ['download', 'csv', 'data', 'tracker']):
                        csv_links.append(urljoin(tracker_url, href))

                # Process CSV data if available
                for csv_url in csv_links[:3]:  # Limit to prevent overwhelming
                    try:
                        csv_response = self.fetch_url_with_retry(csv_url)
                        if csv_response and 'text/csv' in csv_response.headers.get('content-type', ''):
                            # Process CSV content for MCF entities
                            csv_content = csv_response.text
                            entities = self.extract_entities_from_csv(csv_content)

                            if entities:
                                document_data = {
                                    'source_id': self.source_id,
                                    'url': csv_url,
                                    'title': 'ASPI Critical Technology Tracker Data',
                                    'document_type': 'dataset',
                                    'mcf_relevance_score': 0.95,  # High relevance for tracker data
                                    'entities': entities,
                                    'content_text': csv_content[:10000],  # First 10k chars
                                    'publication_date': datetime.now().date().isoformat(),
                                    'provenance': {
                                        'source': 'ASPI Critical Tech Tracker',
                                        'data_type': 'CSV',
                                        'collected_date': datetime.now().isoformat()
                                    }
                                }

                                doc_id = self.store_mcf_document(document_data)
                                if doc_id:
                                    documents.append(document_data)
                                    logger.info(f"Collected Critical Tech Tracker CSV: {csv_url}")

                    except Exception as e:
                        logger.error(f"Error processing CSV {csv_url}: {e}")

                # Process main tracker page content
                content_text = soup.get_text()
                mcf_score = self.calculate_mcf_relevance(content_text)

                if mcf_score >= 0.4:
                    metadata = self.extract_aspi_metadata(soup, tracker_url)
                    document_data = self.process_document(tracker_url, self.source_id, **metadata)

                    if document_data:
                        documents.append(document_data)

            except Exception as e:
                logger.error(f"Error collecting from tracker URL {tracker_url}: {e}")

        return documents

    def extract_entities_from_csv(self, csv_content: str) -> dict:
        """Extract MCF entities from CSV data"""
        entities = {
            'companies': [],
            'institutes': [],
            'technologies': [],
            'countries': []
        }

        try:
            # Parse CSV content
            lines = csv_content.split('\n')
            if len(lines) < 2:
                return entities

            # Assume first line is header
            header = [col.strip().lower() for col in lines[0].split(',')]

            # Look for relevant columns
            name_cols = [i for i, col in enumerate(header) if any(term in col for term in ['name', 'organization', 'company', 'institution'])]
            country_cols = [i for i, col in enumerate(header) if 'country' in col]
            tech_cols = [i for i, col in enumerate(header) if any(term in col for term in ['technology', 'field', 'category'])]

            # Process data rows
            for line in lines[1:100]:  # Limit to first 100 rows
                if not line.strip():
                    continue

                cols = [col.strip().strip('"') for col in line.split(',')]

                # Extract organizations/companies
                for name_col in name_cols:
                    if name_col < len(cols) and cols[name_col]:
                        entity_name = cols[name_col]
                        if len(entity_name) > 3 and entity_name not in entities['companies']:
                            # Classify as company or institute
                            if any(term in entity_name.lower() for term in ['university', 'institute', 'academy', 'laboratory']):
                                if entity_name not in entities['institutes']:
                                    entities['institutes'].append(entity_name)
                            else:
                                entities['companies'].append(entity_name)

                # Extract countries
                for country_col in country_cols:
                    if country_col < len(cols) and cols[country_col]:
                        country = cols[country_col]
                        if country and country not in entities['countries']:
                            entities['countries'].append(country)

                # Extract technologies
                for tech_col in tech_cols:
                    if tech_col < len(cols) and cols[tech_col]:
                        technology = cols[tech_col]
                        if technology and technology not in entities['technologies']:
                            entities['technologies'].append(technology)

        except Exception as e:
            logger.error(f"Error parsing CSV data: {e}")

        return entities

    def collect_aspi_mcf_reports(self) -> list:
        """Collect MCF-relevant reports from ASPI"""
        logger.info("Collecting MCF reports from ASPI")
        documents = []

        for mcf_path in self.mcf_urls:
            try:
                url = urljoin(self.base_url, mcf_path)
                response = self.fetch_url_with_retry(url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find report links
                report_links = soup.find_all('a', href=True)
                mcf_report_urls = []

                for link in report_links:
                    href = link['href']
                    link_text = link.get_text(strip=True).lower()

                    # Make absolute URL
                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)

                    # Filter for MCF-relevant reports
                    mcf_keywords = ['china', 'military', 'defense', 'dual-use', 'technology', 'critical tech']
                    if any(keyword in link_text for keyword in mcf_keywords) or any(keyword in href.lower() for keyword in mcf_keywords):
                        if href not in mcf_report_urls:
                            mcf_report_urls.append(href)

                # Process each report
                for report_url in mcf_report_urls[:10]:  # Limit to prevent overwhelming
                    try:
                        metadata = {}
                        document_data = self.process_document(report_url, self.source_id, **metadata)

                        if document_data and document_data['mcf_relevance_score'] >= 0.4:
                            documents.append(document_data)
                            logger.info(f"Collected ASPI MCF report: {document_data.get('title', 'Unknown')[:50]}...")

                    except Exception as e:
                        logger.error(f"Error processing report {report_url}: {e}")

            except Exception as e:
                logger.error(f"Error collecting from {mcf_path}: {e}")

        return documents

    def search_aspi_mcf_content(self) -> list:
        """Search ASPI site for additional MCF content"""
        logger.info("Searching ASPI for additional MCF content")
        documents = []

        for search_term in self.mcf_search_terms:
            try:
                # ASPI search URL pattern
                search_url = f"{self.base_url}/?s={search_term.replace(' ', '+')}"

                response = self.fetch_url_with_retry(search_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find search result links
                result_links = soup.find_all('a', href=True)

                for link in result_links[:5]:  # Limit results per search term
                    href = link['href']

                    if not href.startswith('http') and href.startswith('/'):
                        href = urljoin(self.base_url, href)

                    if self.base_url not in href:
                        continue

                    try:
                        document_data = self.process_document(href, self.source_id)

                        if document_data and document_data['mcf_relevance_score'] >= 0.5:
                            documents.append(document_data)
                            logger.info(f"Found ASPI MCF search result: {document_data.get('title', 'Unknown')[:50]}...")

                    except Exception as e:
                        logger.error(f"Error processing search result {href}: {e}")

            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")

        return documents

    def collect_all_mcf_content(self) -> dict:
        """Collect all ASPI MCF content"""
        logger.info("Starting ASPI MCF collection")

        all_documents = []
        collection_stats = {
            'source': 'ASPI',
            'start_time': datetime.now().isoformat(),
            'tracker_docs': 0,
            'report_docs': 0,
            'search_docs': 0,
            'total_documents': 0,
            'high_relevance_docs': 0,
            'errors': 0
        }

        # Collect Critical Tech Tracker data
        try:
            tracker_docs = self.collect_critical_tech_tracker_data()
            all_documents.extend(tracker_docs)
            collection_stats['tracker_docs'] = len(tracker_docs)
        except Exception as e:
            logger.error(f"Error collecting tracker data: {e}")
            collection_stats['errors'] += 1

        # Collect MCF reports
        try:
            report_docs = self.collect_aspi_mcf_reports()
            all_documents.extend(report_docs)
            collection_stats['report_docs'] = len(report_docs)
        except Exception as e:
            logger.error(f"Error collecting reports: {e}")
            collection_stats['errors'] += 1

        # Search for additional content
        try:
            search_docs = self.search_aspi_mcf_content()
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
        collection_stats['end_time'] = datetime.now().isoformat()

        # Get updated database statistics
        db_stats = self.get_mcf_statistics()

        logger.info(f"""
ASPI MCF Collection Complete:
- Tracker documents: {collection_stats['tracker_docs']}
- Report documents: {collection_stats['report_docs']}
- Search documents: {collection_stats['search_docs']}
- Total collected: {collection_stats['total_documents']}
- High relevance (>0.7): {collection_stats['high_relevance_docs']}
- Total MCF documents in database: {db_stats.get('total_documents', 0)}
        """)

        return {
            'collection_stats': collection_stats,
            'database_stats': db_stats,
            'documents': all_documents
        }

def main():
    """Run ASPI MCF collection"""
    collector = ASPIMCFCollector()
    results = collector.collect_all_mcf_content()

    # Save collection report
    output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_aspi")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"aspi_mcf_collection_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"ASPI MCF collection report saved to: {report_file}")

if __name__ == "__main__":
    main()
