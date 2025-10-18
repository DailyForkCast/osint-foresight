#!/usr/bin/env python3
"""
CSET MCF Collector
Collects Military-Civil Fusion content from Center for Security and Emerging Technology
Priority: HIGH (Tier 2) - Technology pathways, AI, semiconductor policy analysis
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

class CSETMCFCollector(MCFBaseCollector):
    """CSET MCF intelligence collector for technology pathway analysis"""

    def __init__(self):
        super().__init__()
        self.source_id = "cset"
        self.base_url = "https://cset.georgetown.edu"

        # Key CSET URLs
        self.cset_urls = [
            "/publications/",
            "/research/",
            "/blog/",
            "/data/",
            "/events/",
            "/briefings/"
        ]

        # CSET publication patterns
        self.pub_patterns = [
            r"CSET.*Brief",
            r"Policy.*Brief",
            r"Data.*Brief",
            r"Issue.*Brief",
            r"Research.*Report",
            r"Translation"
        ]

        # MCF-specific search terms for CSET
        self.mcf_search_terms = [
            "China technology transfer",
            "Chinese AI development",
            "semiconductor competition China",
            "Chinese military modernization",
            "dual-use technology China",
            "Chinese tech companies military",
            "China industrial policy",
            "Chinese innovation system"
        ]

        # Technology focus areas for CSET
        self.tech_pathways = [
            'artificial intelligence', 'AI', 'machine learning', 'deep learning',
            'semiconductors', 'chips', 'microprocessors', 'TSMC', 'SMIC',
            'quantum computing', 'quantum technology', 'quantum communications',
            'biotechnology', 'synthetic biology', 'gene editing',
            '5G', '6G', 'telecommunications infrastructure',
            'autonomous systems', 'robotics', 'unmanned systems',
            'hypersonics', 'space technology', 'satellites',
            'cybersecurity', 'cyber operations', 'information warfare'
        ]

        # Chinese tech entities tracked by CSET
        self.chinese_tech_entities = [
            'Baidu', 'Alibaba', 'Tencent', 'ByteDance', 'TikTok',
            'Huawei', 'ZTE', 'Xiaomi', 'DJI', 'SenseTime',
            'Megvii', 'iFlytek', 'Cambricon', 'Horizon Robotics',
            'SMIC', 'YMTC', 'Unisoc', 'Allwinner',
            'CETC', 'CAS', 'Tsinghua University', 'Peking University'
        ]

    def extract_cset_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from CSET publication"""
        metadata = {
            'title': 'Unknown Title',
            'publication_date': None,
            'authors': [],
            'document_type': 'report',
            'publication_type': None,
            'topic_areas': [],
            'classification': 'unclassified'
        }

        # Extract title
        title_selectors = [
            'h1.entry-title',
            'h1.post-title',
            'h1.page-title',
            'h1',
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

        # Extract publication date
        page_text = soup.get_text()

        date_patterns = [
            r'Published[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
            r'Date[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
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
            '.publication-authors',
            '.contributors'
        ]

        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                authors_text = author_elem.get_text(strip=True)
                # Split by common separators
                authors = []
                for author in re.split(r'[,;&]|\\band\\b', authors_text):
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

        if 'policy-brief' in url_lower or 'policy brief' in page_text_lower:
            metadata['publication_type'] = 'Policy Brief'
            metadata['document_type'] = 'policy_brief'
        elif 'data-brief' in url_lower or 'data brief' in page_text_lower:
            metadata['publication_type'] = 'Data Brief'
            metadata['document_type'] = 'data_brief'
        elif 'issue-brief' in url_lower or 'issue brief' in page_text_lower:
            metadata['publication_type'] = 'Issue Brief'
            metadata['document_type'] = 'issue_brief'
        elif 'research' in url_lower:
            metadata['publication_type'] = 'Research Report'
            metadata['document_type'] = 'research_report'
        elif 'translation' in url_lower:
            metadata['publication_type'] = 'Translation'
            metadata['document_type'] = 'translation'
        elif 'blog' in url_lower:
            metadata['publication_type'] = 'Blog Post'
            metadata['document_type'] = 'blog_post'

        # Extract topic areas
        topic_indicators = []
        for tech in self.tech_pathways:
            if tech.lower() in page_text_lower:
                topic_indicators.append(tech)

        metadata['topic_areas'] = list(set(topic_indicators))[:5]  # Limit topics

        return metadata

    def collect_cset_publications(self) -> list:
        """Collect CSET publications"""
        logger.info("Collecting CSET publications")
        documents = []

        publications_url = urljoin(self.base_url, "/publications/")

        response = self.fetch_url_with_retry(publications_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find publication links
        pub_links = soup.find_all('a', href=True)
        publication_urls = []

        for link in pub_links:
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for publications
            if any(term in link_text.lower() for term in ['brief', 'report', 'policy', 'research', 'china']):
                if href not in publication_urls and self.base_url in href:
                    publication_urls.append(href)

        logger.info(f"Found {len(publication_urls)} potential CSET publications")

        # Process publications
        for pub_url in publication_urls[:25]:  # Limit collection
            try:
                pub_response = self.fetch_url_with_retry(pub_url)
                if not pub_response:
                    continue

                pub_soup = BeautifulSoup(pub_response.text, 'html.parser')
                content_text = pub_soup.get_text()

                # Calculate MCF relevance with tech pathway bonus
                mcf_score = self.calculate_mcf_relevance(content_text)

                # Technology pathway bonus
                tech_bonus = 0
                for tech in self.tech_pathways:
                    if tech.lower() in content_text.lower():
                        tech_bonus += 0.05

                # Chinese entity bonus
                entity_bonus = 0
                for entity in self.chinese_tech_entities:
                    if entity.lower() in content_text.lower():
                        entity_bonus += 0.05

                mcf_score = min(mcf_score + tech_bonus + entity_bonus, 1.0)

                if mcf_score >= 0.3:  # Threshold for CSET content
                    metadata = self.extract_cset_metadata(pub_soup, pub_url)

                    document_data = self.process_document(
                        pub_url,
                        self.source_id,
                        **metadata
                    )

                    if document_data:
                        documents.append(document_data)
                        logger.info(f"Collected CSET publication: {metadata['title'][:50]}... (Score: {mcf_score:.3f})")

            except Exception as e:
                logger.error(f"Error processing CSET publication {pub_url}: {e}")

        return documents

    def collect_cset_research(self) -> list:
        """Collect CSET research reports"""
        logger.info("Collecting CSET research")
        documents = []

        research_url = urljoin(self.base_url, "/research/")

        response = self.fetch_url_with_retry(research_url)
        if not response:
            return documents

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find research links
        research_links = soup.find_all('a', href=True)

        for link in research_links[:15]:  # Limit research documents
            href = link['href']
            link_text = link.get_text(strip=True)

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.base_url, href)

            # Filter for research content with China focus
            china_indicators = ['china', 'chinese', 'technology', 'AI', 'semiconductor']
            if any(indicator in link_text.lower() for indicator in china_indicators):
                try:
                    document_data = self.process_document(href, self.source_id)

                    if document_data and document_data['mcf_relevance_score'] >= 0.4:
                        documents.append(document_data)
                        logger.info(f"Collected CSET research: {document_data.get('title', 'Unknown')[:40]}...")

                except Exception as e:
                    logger.error(f"Error processing research document {href}: {e}")

        return documents

    def search_cset_mcf_content(self) -> list:
        """Search CSET for MCF content"""
        logger.info("Searching CSET for MCF content")
        documents = []

        for search_term in self.mcf_search_terms:
            try:
                # CSET search functionality (adjust based on site implementation)
                search_url = f"{self.base_url}/search/?q={search_term.replace(' ', '+')}"

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
                            logger.info(f"Found CSET MCF search result: {document_data.get('title', 'Unknown')[:40]}...")

                    except Exception as e:
                        logger.error(f"Error processing search result {href}: {e}")

            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")

        return documents

    def collect_all_mcf_content(self) -> dict:
        """Collect all CSET MCF content"""
        logger.info("Starting CSET MCF collection")

        all_documents = []
        collection_stats = {
            'source': 'CSET',
            'start_time': datetime.now().isoformat(),
            'publication_docs': 0,
            'research_docs': 0,
            'search_docs': 0,
            'total_documents': 0,
            'high_relevance_docs': 0,
            'tech_pathway_docs': 0,
            'chinese_entity_docs': 0,
            'errors': 0
        }

        # Collect publications
        try:
            pub_docs = self.collect_cset_publications()
            all_documents.extend(pub_docs)
            collection_stats['publication_docs'] = len(pub_docs)
        except Exception as e:
            logger.error(f"Error collecting publications: {e}")
            collection_stats['errors'] += 1

        # Collect research
        try:
            research_docs = self.collect_cset_research()
            all_documents.extend(research_docs)
            collection_stats['research_docs'] = len(research_docs)
        except Exception as e:
            logger.error(f"Error collecting research: {e}")
            collection_stats['errors'] += 1

        # Search for additional content
        try:
            search_docs = self.search_cset_mcf_content()
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

        # Count tech pathway documents
        collection_stats['tech_pathway_docs'] = sum(
            1 for doc in all_documents
            if any(tech.lower() in doc.get('content_text', '').lower()
                   for tech in self.tech_pathways)
        )

        # Count Chinese entity documents
        collection_stats['chinese_entity_docs'] = sum(
            1 for doc in all_documents
            if any(entity.lower() in doc.get('content_text', '').lower()
                   for entity in self.chinese_tech_entities)
        )

        collection_stats['end_time'] = datetime.now().isoformat()

        # Get updated database statistics
        db_stats = self.get_mcf_statistics()

        logger.info(f"""
CSET MCF Collection Complete:
- Publication documents: {collection_stats['publication_docs']}
- Research documents: {collection_stats['research_docs']}
- Search documents: {collection_stats['search_docs']}
- Total collected: {collection_stats['total_documents']}
- High relevance (>0.7): {collection_stats['high_relevance_docs']}
- Tech pathway focus: {collection_stats['tech_pathway_docs']}
- Chinese entity focus: {collection_stats['chinese_entity_docs']}
- Total MCF documents in database: {db_stats.get('total_documents', 0)}
        """)

        return {
            'collection_stats': collection_stats,
            'database_stats': db_stats,
            'documents': all_documents
        }

def main():
    """Run CSET MCF collection"""
    collector = CSETMCFCollector()
    results = collector.collect_all_mcf_content()

    # Save collection report
    output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_cset")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"cset_mcf_collection_{timestamp}.json"

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"CSET MCF collection report saved to: {report_file}")

if __name__ == "__main__":
    main()
