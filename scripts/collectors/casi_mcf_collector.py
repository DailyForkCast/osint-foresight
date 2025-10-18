#!/usr/bin/env python3
"""
CASI MCF Collector
Collects Military-Civil Fusion content from China Aerospace Studies Institute (CASI)
Priority: HIGHEST (Tier 1) - PLA aerospace, AVIC/AECC ecosystems, translations
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

class CASIMCFCollector(MCFBaseCollector):
    """CASI MCF intelligence collector for aerospace and PLA analysis"""

    def __init__(self):
        super().__init__()
        self.source_id = "casi"
        self.base_url = "https://www.airuniversity.af.edu/CASI"

        # Key CASI URLs
        self.casi_urls = [
            "/Publications/",
            "/Research/",
            "/Articles/",
            "/Display/Article/",
            "/Research/China-Aerospace-Studies-Institute/"
        ]

        # CASI publication categories
        self.publication_categories = [
            "Articles",
            "Special Reports",
            "Translations",
            "China Brief",
            "Research Papers",
            "Policy Analysis"
        ]

        # Aerospace and defense entities
        self.aerospace_entities = [
            'AVIC', 'Aviation Industry Corporation of China',
            'AECC', 'Aero Engine Corporation of China',
            'CASC', 'China Aerospace Science and Technology Corporation',
            'CASIC', 'China Aerospace Science and Industry Corporation',
            'COMAC', 'Commercial Aircraft Corporation of China',
            'PLA Air Force', 'PLAAF', 'PLA Navy', 'PLAN',
            'Strategic Support Force', 'SSF', 'Space Force',
            'China Manned Space Agency', 'CMSA',
            'Chengdu Aircraft', 'Shenyang Aircraft', 'Xian Aircraft',
            'Beijing Institute of Technology', 'Harbin Institute of Technology'
        ]

        # MCF-specific search terms for CASI
        self.mcf_search_terms = [
            "military civil fusion aerospace",
            "dual-use space technology",
            "AVIC military civilian",
            "Chinese aerospace industry",
            "PLA air force modernization",
            "space-based capabilities",
            "satellite dual-use",
            "aerospace manufacturing China"
        ]

        # Translation indicators
        self.translation_indicators = [
            'translated', 'translation', 'original Chinese',
            'Chinese source', 'translated from', '翻译',
            'bilingual', 'Chinese text', 'original document'
        ]

    def extract_casi_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from CASI publication"""
        metadata = {
            'title': 'Unknown Title',
            'publication_date': None,
            'authors': [],
            'document_type': 'article',
            'publication_category': None,
            'is_translation': False,
            'original_source': None,
            'classification': 'unclassified'
        }

        # Extract title
        title_selectors = [
            'h1.page-title',
            'h1.article-title',
            'h1',
            '.entry-title',
            '.publication-title',
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

        # Extract publication date
        page_text = soup.get_text()

        date_patterns = [
            r'Published[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',  # Published: January 15, 2024
            r'Date[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',      # Date: January 15, 2024
            r'(\w+\s+\d{1,2},?\s+\d{4})',                # January 15, 2024
            r'(\d{1,2}/\d{1,2}/\d{4})',                  # 1/15/2024
            r'(\d{4}-\d{2}-\d{2})'                       # 2024-01-15
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
            '.byline',
            '.author',
            '.article-author',
            '.publication-author',
            '.contributor'
        ]

        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                authors_text = author_elem.get_text(strip=True)
                # Clean and split authors
                authors = []
                for author in re.split(r'[,;&]|\band\b', authors_text):
                    author = author.strip()
                    if author and len(author) > 2:
                        # Remove common titles
                        author = re.sub(r'^(Dr|Professor|Col|Lt|Maj|General|Captain)\.?\s*', '', author)
                        authors.append(author)

                metadata['authors'] = authors[:3]  # Limit to 3 authors
                break

        # Determine if this is a translation
        translation_text = page_text.lower()
        for indicator in self.translation_indicators:
            if indicator.lower() in translation_text:
                metadata['is_translation'] = True
                break

        # Extract original source for translations
        if metadata['is_translation']:
            source_patterns = [
                r'original(?:\s+source)?[:\s]+([^.\n]+)',
                r'translated\s+from[:\s]+([^.\n]+)',
                r'chinese\s+source[:\s]+([^.\n]+)',
                r'source[:\s]+([^.\n]*chinese[^.\n]*)'
            ]

            for pattern in source_patterns:
                match = re.search(pattern, translation_text, re.IGNORECASE)
                if match:
                    metadata['original_source'] = match.group(1).strip()
                    break

        # Determine publication category
        url_lower = url.lower()
        page_text_lower = page_text.lower()

        if 'translation' in url_lower or 'translation' in page_text_lower:
            metadata['publication_category'] = 'Translation'
        elif 'special-report' in url_lower or 'special report' in page_text_lower:
            metadata['publication_category'] = 'Special Report'
        elif 'research' in url_lower:
            metadata['publication_category'] = 'Research Paper'
        elif 'brief' in url_lower or 'brief' in page_text_lower:
            metadata['publication_category'] = 'China Brief'
        else:
            metadata['publication_category'] = 'Article'

        # Determine document type from URL
        if '/article/' in url_lower:
            metadata['document_type'] = 'article'
        elif '/report/' in url_lower:
            metadata['document_type'] = 'report'
        elif '/translation/' in url_lower:
            metadata['document_type'] = 'translation'
        elif '.pdf' in url_lower:
            metadata['document_type'] = 'pdf_document'

        return metadata

    def collect_casi_publications(self) -> list:
        """Collect publications from CASI main sections"""
        logger.info("Collecting publications from CASI")
        documents = []

        for casi_path in self.casi_urls:
            try:
                url = urljoin(self.base_url, casi_path)
                response = self.fetch_url_with_retry(url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find publication links
                pub_links = soup.find_all('a', href=True)
                relevant_links = []

                for link in pub_links:
                    href = link['href']
                    link_text = link.get_text(strip=True)

                    # Make absolute URL
                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)

                    # Filter for aerospace/China-related content
                    aerospace_keywords = [
                        'china', 'chinese', 'aerospace', 'aviation', 'space',
                        'avic', 'pla', 'military', 'defense', 'air force',
                        'satellite', 'missile', 'aircraft', 'engine'
                    ]

                    if any(keyword in link_text.lower() for keyword in aerospace_keywords):
                        if href not in relevant_links:
                            relevant_links.append(href)

                    # Also check href for relevant terms
                    if any(keyword in href.lower() for keyword in aerospace_keywords):
                        if href not in relevant_links:
                            relevant_links.append(href)

                # Process relevant publications
                for pub_link in relevant_links[:15]:  # Limit to prevent overwhelming
                    try:
                        pub_response = self.fetch_url_with_retry(pub_link)
                        if not pub_response:
                            continue

                        pub_soup = BeautifulSoup(pub_response.text, 'html.parser')
                        content_text = pub_soup.get_text()

                        # Calculate MCF relevance with aerospace bonus
                        mcf_score = self.calculate_mcf_relevance(content_text)

                        # Aerospace/AVIC bonus scoring
                        aerospace_bonus = 0
                        for entity in self.aerospace_entities:
                            if entity.lower() in content_text.lower():
                                aerospace_bonus += 0.1

                        mcf_score = min(mcf_score + aerospace_bonus, 1.0)

                        if mcf_score >= 0.4:  # High threshold for CASI
                            metadata = self.extract_casi_metadata(pub_soup, pub_link)

                            document_data = self.process_document(
                                pub_link,
                                self.source_id,
                                **metadata
                            )

                            if document_data:
                                documents.append(document_data)
                                logger.info(f"Collected CASI publication: {metadata['title'][:50]}... (Score: {mcf_score:.3f})")

                    except Exception as e:
                        logger.error(f"Error processing publication {pub_link}: {e}")

            except Exception as e:
                logger.error(f"Error collecting from {casi_path}: {e}")

        return documents

    def collect_casi_translations(self) -> list:
        """Collect Chinese document translations from CASI"""
        logger.info("Collecting translations from CASI")
        documents = []

        # Look for translation-specific sections
        translation_urls = [
            urljoin(self.base_url, "/Publications/Translations/"),
            urljoin(self.base_url, "/Research/Translations/"),
            urljoin(self.base_url, "/Articles/Translations/")
        ]

        for trans_url in translation_urls:
            try:
                response = self.fetch_url_with_retry(trans_url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find translation links
                trans_links = soup.find_all('a', href=True)

                for link in trans_links[:10]:  # Limit translations
                    href = link['href']
                    link_text = link.get_text(strip=True)

                    # Make absolute URL
                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)

                    # Look for translation indicators
                    if any(indicator in link_text.lower() for indicator in self.translation_indicators):
                        try:
                            document_data = self.process_document(href, self.source_id)

                            if document_data and document_data['mcf_relevance_score'] >= 0.5:
                                # Mark as translation
                                document_data['is_translation'] = True
                                document_data['document_type'] = 'translation'

                                documents.append(document_data)
                                logger.info(f"Collected CASI translation: {document_data.get('title', 'Unknown')[:40]}...")

                        except Exception as e:
                            logger.error(f"Error processing translation {href}: {e}")

            except Exception as e:
                logger.error(f"Error collecting translations from {trans_url}: {e}")

        return documents

    def search_casi_mcf_content(self) -> list:
        """Search CASI for additional MCF content"""
        logger.info("Searching CASI for MCF content")
        documents = []

        for search_term in self.mcf_search_terms:
            try:
                # CASI search URL pattern (may need adjustment)
                search_url = f"{self.base_url}/Search?query={search_term.replace(' ', '+')}"

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
                            logger.info(f"Found CASI MCF search result: {document_data.get('title', 'Unknown')[:40]}...")

                    except Exception as e:
                        logger.error(f"Error processing search result {href}: {e}")

            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")

        return documents

    def collect_all_mcf_content(self) -> dict:
        """Collect all CASI MCF content"""
        logger.info("Starting CASI MCF collection")

        all_documents = []
        collection_stats = {
            'source': 'CASI',
            'start_time': datetime.now().isoformat(),
            'publication_docs': 0,
            'translation_docs': 0,
            'search_docs': 0,
            'total_documents': 0,
            'high_relevance_docs': 0,
            'aerospace_specific_docs': 0,
            'bilingual_docs': 0,
            'errors': 0
        }

        # Collect main publications
        try:
            pub_docs = self.collect_casi_publications()
            all_documents.extend(pub_docs)
            collection_stats['publication_docs'] = len(pub_docs)
        except Exception as e:
            logger.error(f"Error collecting publications: {e}")
            collection_stats['errors'] += 1

        # Collect translations
        try:
            trans_docs = self.collect_casi_translations()
            all_documents.extend(trans_docs)
            collection_stats['translation_docs'] = len(trans_docs)
        except Exception as e:
            logger.error(f"Error collecting translations: {e}")
            collection_stats['errors'] += 1

        # Search for additional content
        try:
            search_docs = self.search_casi_mcf_content()
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

        # Count aerospace-specific documents
        collection_stats['aerospace_specific_docs'] = sum(
            1 for doc in all_documents
            if any(aero_entity.lower() in doc.get('content_text', '').lower()
                   for aero_entity in self.aerospace_entities)
        )

        # Count bilingual/translation documents
        collection_stats['bilingual_docs'] = sum(
            1 for doc in all_documents
            if doc.get('is_translation', False) or
            any(indicator in doc.get('content_text', '').lower()
                for indicator in self.translation_indicators)
        )

        collection_stats['end_time'] = datetime.now().isoformat()

        # Get updated database statistics
        db_stats = self.get_mcf_statistics()

        logger.info(f"""
CASI MCF Collection Complete:
- Publication documents: {collection_stats['publication_docs']}
- Translation documents: {collection_stats['translation_docs']}
- Search documents: {collection_stats['search_docs']}
- Total collected: {collection_stats['total_documents']}
- High relevance (>0.7): {collection_stats['high_relevance_docs']}
- Aerospace-specific: {collection_stats['aerospace_specific_docs']}
- Bilingual/Translations: {collection_stats['bilingual_docs']}
- Total MCF documents in database: {db_stats.get('total_documents', 0)}
        """)

        return {
            'collection_stats': collection_stats,
            'database_stats': db_stats,
            'documents': all_documents
        }

def main():
    """Run CASI MCF collection"""
    collector = CASIMCFCollector()
    results = collector.collect_all_mcf_content()

    # Save collection report
    output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_casi")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"casi_mcf_collection_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"CASI MCF collection report saved to: {report_file}")

if __name__ == "__main__":
    main()
