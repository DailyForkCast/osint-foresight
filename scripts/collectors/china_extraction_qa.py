#!/usr/bin/env python3
"""
China Policy Collector - Extraction & QA Framework
Handles HTML/PDF extraction, normalization, deduplication, and quality assurance
"""

import re
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from dataclasses import asdict

import requests
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException

# Optional PDF support
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyMuPDF not available - PDF extraction disabled")

logger = logging.getLogger(__name__)


class DocumentExtractor:
    """Extract content and metadata from HTML and PDF documents"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (OSINT-Foresight/1.0; Research; +https://github.com/osint-foresight)'
        })

    def extract_from_html(self, html: str, url: str) -> Dict:
        """Extract structured data from HTML"""
        soup = BeautifulSoup(html, 'html.parser')

        # Extract metadata
        metadata = {
            'title': self._extract_title(soup),
            'publication_date': self._extract_date(soup),
            'date_source': None,
            'date_confidence': None,
            'language': self._detect_language(soup),
            'description': self._extract_description(soup),
            'keywords': self._extract_keywords(soup),
            'content_text': self._extract_main_content(soup),
            'content_length': 0,
            'extraction_ok': True,
            'extraction_notes': []
        }

        # Detect language from content
        if metadata['content_text']:
            try:
                detected_lang = detect(metadata['content_text'])
                if metadata['language'] != detected_lang:
                    metadata['extraction_notes'].append(
                        f"Language mismatch: meta={metadata['language']}, detected={detected_lang}"
                    )
                    metadata['language'] = detected_lang
            except LangDetectException:
                metadata['extraction_notes'].append("Language detection failed")

        metadata['content_length'] = len(metadata['content_text']) if metadata['content_text'] else 0

        # Set date confidence based on source
        if metadata['publication_date']:
            if metadata['date_source'] in ['meta', 'schema']:
                metadata['date_confidence'] = 'high'
            elif metadata['date_source'] == 'inline':
                metadata['date_confidence'] = 'medium'
            elif metadata['date_source'] == 'url':
                metadata['date_confidence'] = 'low'
            else:
                metadata['date_confidence'] = 'low'

        return metadata

    def extract_from_pdf(self, pdf_path: Path) -> Dict:
        """Extract structured data from PDF"""
        if not PDF_AVAILABLE:
            return {
                'extraction_ok': False,
                'extraction_notes': ['PyMuPDF not available']
            }

        try:
            doc = fitz.open(pdf_path)

            metadata = {
                'title': doc.metadata.get('title', ''),
                'pages': doc.page_count,
                'content_text': '',
                'content_length': 0,
                'extraction_ok': True,
                'extraction_notes': []
            }

            # Extract text from all pages
            full_text = []
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text()
                full_text.append(text)

            metadata['content_text'] = '\n'.join(full_text)
            metadata['content_length'] = len(metadata['content_text'])

            # Detect language
            if metadata['content_text']:
                try:
                    metadata['language'] = detect(metadata['content_text'])
                except LangDetectException:
                    metadata['language'] = 'unknown'
                    metadata['extraction_notes'].append("Language detection failed")

            doc.close()
            return metadata

        except Exception as e:
            logger.error(f"PDF extraction failed for {pdf_path}: {e}")
            return {
                'extraction_ok': False,
                'extraction_notes': [f"PDF extraction error: {str(e)}"]
            }

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract title from HTML"""
        # Try meta tags first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()

        twitter_title = soup.find('meta', {'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title['content'].strip()

        # Try <title> tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.text.strip()

        # Try <h1> tag
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.text.strip()

        return None

    def _extract_date(self, soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
        """Extract publication date and source from HTML"""
        # Try meta tags (highest confidence)
        date_meta = soup.find('meta', {'name': 'date'})
        if date_meta and date_meta.get('content'):
            return date_meta['content'], 'meta'

        pub_meta = soup.find('meta', {'property': 'article:published_time'})
        if pub_meta and pub_meta.get('content'):
            return pub_meta['content'], 'meta'

        # Try schema.org (high confidence)
        ld_json = soup.find('script', {'type': 'application/ld+json'})
        if ld_json:
            try:
                data = json.loads(ld_json.string)
                if 'datePublished' in data:
                    return data['datePublished'], 'schema'
            except:
                pass

        # Try inline patterns (medium confidence)
        # Pattern: 发布时间: YYYY-MM-DD or Updated: YYYY-MM-DD
        text = soup.get_text()
        date_patterns = [
            r'发布时间[:：]\s*(\d{4}[-/]\d{2}[-/]\d{2})',
            r'发布日期[:：]\s*(\d{4}[-/]\d{2}[-/]\d{2})',
            r'Updated[:：]\s*(\d{4}[-/]\d{2}[-/]\d{2})',
            r'Published[:：]\s*(\d{4}[-/]\d{2}[-/]\d{2})',
            r'Date[:：]\s*(\d{4}[-/]\d{2}[-/]\d{2})'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).replace('/', '-'), 'inline'

        return None, None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract description from HTML"""
        # Try meta description
        desc_meta = soup.find('meta', {'name': 'description'})
        if desc_meta and desc_meta.get('content'):
            return desc_meta['content'].strip()

        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()

        return None

    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from HTML"""
        keywords_meta = soup.find('meta', {'name': 'keywords'})
        if keywords_meta and keywords_meta.get('content'):
            keywords = keywords_meta['content']
            return [k.strip() for k in keywords.split(',')]
        return []

    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main content text from HTML"""
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            script.decompose()

        # Try article tag first
        article = soup.find('article')
        if article:
            return article.get_text(separator=' ', strip=True)

        # Try main content divs
        content_divs = soup.find_all('div', class_=re.compile(r'content|article|main|body'))
        if content_divs:
            # Get largest content div
            largest = max(content_divs, key=lambda d: len(d.get_text()))
            return largest.get_text(separator=' ', strip=True)

        # Fallback to body
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)

        return None

    def _detect_language(self, soup: BeautifulSoup) -> str:
        """Detect language from HTML"""
        # Try html lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            lang = html_tag['lang'][:2].lower()
            return lang

        # Try meta tags
        lang_meta = soup.find('meta', {'http-equiv': 'content-language'})
        if lang_meta and lang_meta.get('content'):
            return lang_meta['content'][:2].lower()

        return 'en'  # Default


class TopicClassifier:
    """Classify documents into topics and subtopics"""

    TOPIC_KEYWORDS = {
        'science_technology': [
            'science', 'technology', 'innovation', 'research', 'development',
            '科技', '创新', '研发', '科学', '技术'
        ],
        'industrial_policy': [
            'industry', 'manufacturing', 'production', 'industrial',
            '工业', '制造', '生产', '产业'
        ],
        'standards': [
            'standard', 'specification', 'norm', 'certification',
            '标准', '规范', '认证'
        ],
        'five_year_plan': [
            'five year plan', '5-year plan', 'five-year plan',
            '五年规划', '十四五', '十三五'
        ],
        'international_cooperation': [
            'cooperation', 'collaboration', 'partnership', 'joint',
            '合作', '协作', '伙伴', '联合'
        ],
        'dual_use': [
            'dual use', 'dual-use', 'military', 'defense', 'strategic',
            '军民融合', '国防', '军事', '战略'
        ],
        'belt_road': [
            'belt and road', 'BRI', 'one belt one road',
            '一带一路', '带路'
        ],
        'energy': [
            'energy', 'renewable', 'solar', 'wind', 'nuclear',
            '能源', '可再生', '太阳能', '风能', '核能'
        ],
        'ai_technology': [
            'artificial intelligence', 'AI', 'machine learning', 'deep learning',
            '人工智能', '机器学习', '深度学习'
        ],
        'semiconductors': [
            'semiconductor', 'chip', 'integrated circuit', 'microchip',
            '半导体', '芯片', '集成电路'
        ],
        'quantum': [
            'quantum', 'quantum computing', 'quantum communication',
            '量子', '量子计算', '量子通信'
        ],
        'biotechnology': [
            'biotechnology', 'biotech', 'genetic', 'pharmaceutical',
            '生物技术', '基因', '制药'
        ]
    }

    SUBTOPIC_KEYWORDS = {
        'policy_document': ['policy', 'regulation', 'guideline', '政策', '规定'],
        'five_year_plan': ['five year', '五年', '十四五', '十三五'],
        'white_paper': ['white paper', 'whitepaper', '白皮书'],
        'notice': ['notice', 'announcement', '通知', '公告'],
        'cooperation_agreement': ['agreement', 'MOU', 'memorandum', '协议', '谅解备忘录'],
        'program': ['program', 'initiative', 'project', '项目', '计划']
    }

    def classify(self, title: str, content: str) -> Tuple[List[str], List[str]]:
        """Classify document into topics and subtopics"""
        combined_text = f"{title} {content}".lower()

        topics = []
        subtopics = []

        # Classify topics
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    topics.append(topic)
                    break

        # Classify subtopics
        for subtopic, keywords in self.SUBTOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    subtopics.append(subtopic)
                    break

        return topics, subtopics


class EntityExtractor:
    """Extract entity mentions from documents"""

    # Known Chinese entities (subset - expand as needed)
    KNOWN_ENTITIES = [
        'State Council', 'MOST', 'MIIT', 'NDRC', 'MOFCOM', 'SASAC',
        'Chinese Academy of Sciences', 'CAS',
        'Tsinghua University', 'Peking University',
        'Huawei', 'ZTE', 'SMIC', 'CATL',
        'AIIB', 'Belt and Road Initiative', 'BRI'
    ]

    def extract(self, title: str, content: str) -> List[str]:
        """Extract entity mentions"""
        combined_text = f"{title} {content}"
        entities = []

        for entity in self.KNOWN_ENTITIES:
            if entity in combined_text:
                entities.append(entity)

        return list(set(entities))  # Deduplicate


class QAFramework:
    """Quality assurance checks for collected documents"""

    def __init__(self):
        self.checks = []

    def validate_document(self, doc_dict: Dict, file_path: Optional[Path] = None) -> Tuple[bool, List[str]]:
        """Run all QA checks on document"""
        issues = []

        # Check required fields
        required_fields = ['title', 'publisher_org', 'publisher_type', 'document_type',
                          'publication_date_iso', 'canonical_url']
        for field in required_fields:
            if not doc_dict.get(field):
                issues.append(f"missing_required_field: {field}")

        # Check date format (ISO 8601)
        pub_date = doc_dict.get('publication_date_iso')
        if pub_date:
            if not self._is_valid_iso_date(pub_date):
                issues.append(f"invalid_date_format: {pub_date}")

            # Check date range (2010-present)
            try:
                date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                if date_obj.year < 2010 or date_obj.year > datetime.now().year:
                    issues.append(f"date_out_of_range: {pub_date}")
            except:
                issues.append(f"date_parse_error: {pub_date}")

        # Check enum values
        if doc_dict.get('publisher_type') not in ['central', 'ministry', 'agency', 'academia',
                                                   'standards', 'soe', 'provincial', 'secondary',
                                                   'foreign_coop']:
            issues.append(f"invalid_publisher_type: {doc_dict.get('publisher_type')}")

        if doc_dict.get('document_type') not in ['white_paper', 'plan', 'notice',
                                                  'regulation_summary', 'program_brief',
                                                  'press_release', 'research_note', 'mou',
                                                  'international_plan']:
            issues.append(f"invalid_document_type: {doc_dict.get('document_type')}")

        # Check file integrity if path provided
        if file_path and file_path.exists():
            stated_size = doc_dict.get('file_size_bytes')
            actual_size = file_path.stat().st_size
            if stated_size and abs(stated_size - actual_size) > 100:  # Allow 100 byte variance
                issues.append(f"file_size_mismatch: stated={stated_size}, actual={actual_size}")

            # Verify hash
            stated_hash = doc_dict.get('hash_sha256')
            if stated_hash:
                actual_hash = self._compute_file_hash(file_path)
                if actual_hash != stated_hash:
                    issues.append(f"hash_mismatch: stated={stated_hash[:16]}..., actual={actual_hash[:16]}...")

        # Check provenance
        if not doc_dict.get('provenance_chain') or len(doc_dict.get('provenance_chain', [])) == 0:
            issues.append("missing_provenance_chain")

        if not doc_dict.get('archive_url') and doc_dict.get('fetch_mode') != 'direct':
            issues.append("missing_archive_url")

        # Check safe source
        if not doc_dict.get('verified_safe_source'):
            issues.append("unverified_source")

        return len(issues) == 0, issues

    def _is_valid_iso_date(self, date_str: str) -> bool:
        """Check if string is valid ISO 8601 date"""
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except:
            return False

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()


class DeduplicationEngine:
    """Deduplicate documents across runs and sources"""

    def __init__(self):
        self.seen_hashes = set()
        self.seen_titles = {}  # title -> (hash, url)

    def is_duplicate(self, doc_dict: Dict) -> Tuple[bool, Optional[str]]:
        """Check if document is duplicate"""
        # Primary: SHA256 hash
        doc_hash = doc_dict.get('hash_sha256')
        if doc_hash and doc_hash in self.seen_hashes:
            return True, f"duplicate_hash: {doc_hash[:16]}..."

        # Secondary: Title similarity
        title = doc_dict.get('title', '').lower().strip()
        publisher = doc_dict.get('publisher_org', '').lower().strip()

        if title:
            for seen_title, (seen_hash, seen_url) in self.seen_titles.items():
                similarity = self._similarity(title, seen_title)
                if similarity >= 0.92:  # 92% similarity threshold
                    return True, f"duplicate_title: {similarity:.2f} similar to {seen_url}"

        return False, None

    def add_document(self, doc_dict: Dict):
        """Add document to seen set"""
        doc_hash = doc_dict.get('hash_sha256')
        if doc_hash:
            self.seen_hashes.add(doc_hash)

        title = doc_dict.get('title', '').lower().strip()
        url = doc_dict.get('canonical_url', '')
        if title:
            self.seen_titles[title] = (doc_hash, url)

    def _similarity(self, a: str, b: str) -> float:
        """Compute similarity between two strings"""
        return SequenceMatcher(None, a, b).ratio()

    def load_existing_hashes(self, items_file: Path):
        """Load hashes from existing items.json to avoid reprocessing"""
        if items_file.exists():
            try:
                with open(items_file, 'r') as f:
                    items = json.load(f)
                    for item in items:
                        self.add_document(item)
                logger.info(f"Loaded {len(self.seen_hashes)} existing hashes from {items_file}")
            except Exception as e:
                logger.error(f"Failed to load existing hashes: {e}")


class TranslationService:
    """Machine translation for non-English titles"""

    def __init__(self):
        self.cache = {}

    def translate_title(self, title: str, source_lang: str = 'zh-CN',
                       target_lang: str = 'en') -> Optional[str]:
        """Translate title (placeholder - would use real translation API)"""
        # Cache check
        cache_key = f"{source_lang}:{target_lang}:{title}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # TODO: Implement actual translation API call
        # For now, return None to indicate translation needed
        logger.warning(f"Translation needed for: {title[:50]}...")

        return None


def compute_hashes(content: bytes, text: str) -> Tuple[str, str]:
    """Compute both file and text hashes"""
    # File hash (SHA256 of raw bytes)
    file_hash = hashlib.sha256(content).hexdigest()

    # Text hash (SHA256 of normalized text)
    text_normalized = re.sub(r'\s+', ' ', text).strip()
    text_hash = hashlib.sha256(text_normalized.encode('utf-8')).hexdigest()

    return file_hash, text_hash


# Convenience function for integration
def process_document(html_content: str, url: str, file_path: Optional[Path] = None) -> Dict:
    """Complete extraction and QA pipeline for a document"""
    extractor = DocumentExtractor()
    classifier = TopicClassifier()
    entity_extractor = EntityExtractor()
    qa = QAFramework()

    # Extract metadata and content
    if file_path and file_path.suffix == '.pdf':
        metadata = extractor.extract_from_pdf(file_path)
    else:
        metadata = extractor.extract_from_html(html_content, url)

    # Classify topics
    title = metadata.get('title', '')
    content = metadata.get('content_text', '')
    topics, subtopics = classifier.classify(title, content)
    metadata['topics'] = topics
    metadata['subtopics'] = subtopics

    # Extract entities
    entities = entity_extractor.extract(title, content)
    metadata['entities'] = entities

    # Compute hashes
    if html_content:
        file_hash, text_hash = compute_hashes(html_content.encode('utf-8'), content)
        metadata['hash_sha256'] = file_hash
        metadata['text_hash_sha256'] = text_hash

    # Run QA
    is_valid, issues = qa.validate_document(metadata, file_path)
    metadata['qa_issues'] = issues

    return metadata
