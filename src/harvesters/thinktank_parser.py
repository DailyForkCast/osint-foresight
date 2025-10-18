#!/usr/bin/env python3
"""
Think Tank Parser - HTML and PDF Content Extraction

This module handles extraction of structured content from HTML pages and PDF documents
with metadata extraction, language detection, and content cleaning.

Key Features:
- HTML content extraction with CSS selector support
- PDF text extraction with metadata
- Author and publication date extraction
- Language detection and classification
- Content cleaning and normalization
- Abstract and summary identification
"""

import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import dateutil.parser as date_parser

# HTML parsing
from bs4 import BeautifulSoup, Comment
import html2text

# PDF parsing
import PyPDF2
import fitz  # PyMuPDF as fallback
import pdfplumber

# Language detection
from langdetect import detect, LangDetectError

# Text processing
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords


@dataclass
class ParsedContent:
    """Structured content extracted from a document"""
    title: str
    text: str
    html: Optional[str] = None
    abstract: Optional[str] = None
    authors: List[str] = None
    publish_date: Optional[datetime] = None
    language: str = 'en'
    document_type: str = 'article'
    metadata: Dict[str, Any] = None
    word_count: int = 0
    reading_time_minutes: int = 0

    def __post_init__(self):
        if self.authors is None:
            self.authors = []
        if self.metadata is None:
            self.metadata = {}
        if self.word_count == 0 and self.text:
            self.word_count = len(self.text.split())
        if self.reading_time_minutes == 0 and self.word_count > 0:
            # Assume 200 words per minute reading speed
            self.reading_time_minutes = max(1, self.word_count // 200)


class ThinkTankParser:
    """Parser for extracting content from HTML and PDF documents"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize NLTK components
        self._ensure_nltk_data()

        # HTML to text converter
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0  # No line wrapping

        # Common selectors for different think tanks
        self.default_selectors = {
            'title': ['h1', '.title', '.headline', '.entry-title', 'title'],
            'content': ['.content', '.entry-content', '.post-content', '.article-content', 'article', 'main'],
            'abstract': ['.abstract', '.summary', '.excerpt', '.lead', '.intro'],
            'authors': ['.author', '.byline', '.by-author', '.writers', '.credits'],
            'date': ['.date', '.published', '.publish-date', '.post-date', 'time[datetime]'],
            'exclude': ['.sidebar', '.navigation', '.footer', '.header', '.comments', '.related', '.share']
        }

        # Date patterns for extraction
        self.date_patterns = [
            r'\b(\d{1,2}[\s/\-\.]\d{1,2}[\s/\-\.]\d{4})\b',  # MM/DD/YYYY
            r'\b(\d{4}[\s/\-\.]\d{1,2}[\s/\-\.]\d{1,2})\b',  # YYYY/MM/DD
            r'\b(\w+\s+\d{1,2},?\s+\d{4})\b',  # Month DD, YYYY
            r'\b(\d{1,2}\s+\w+\s+\d{4})\b',  # DD Month YYYY
        ]

    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        try:
            import nltk
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            self.logger.info("Downloading required NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)

    async def parse_html(self, content: bytes, url: str, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse HTML content and extract structured data"""
        try:
            # Decode content
            text_content = content.decode('utf-8', errors='ignore')

            # Parse with BeautifulSoup
            soup = BeautifulSoup(text_content, 'html.parser')

            # Get selectors for this source
            selectors = source_config.get('selectors', {})
            merged_selectors = {**self.default_selectors, **selectors}

            # Remove unwanted elements
            self._remove_unwanted_elements(soup, merged_selectors.get('exclude', []))

            # Extract content based on source configuration
            extraction_strategy = source_config.get('extraction_strategy', 'single_article')

            if extraction_strategy == 'article_list':
                return await self._extract_article_list(soup, url, merged_selectors)
            else:
                return await self._extract_single_article(soup, url, merged_selectors)

        except Exception as e:
            self.logger.error(f"Error parsing HTML from {url}: {e}")
            return []

    async def _extract_single_article(self, soup: BeautifulSoup, url: str,
                                    selectors: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Extract a single article from HTML"""
        extracted = {}

        # Extract title
        title = self._extract_with_selectors(soup, selectors['title'])
        extracted['title'] = self._clean_text(title) if title else 'Untitled'

        # Extract main content
        content_element = self._find_element_with_selectors(soup, selectors['content'])
        if content_element:
            # Get both HTML and text versions
            extracted['html'] = str(content_element)
            extracted['text'] = self._extract_text_from_element(content_element)
        else:
            # Fallback to body content
            body = soup.find('body')
            if body:
                extracted['text'] = self._extract_text_from_element(body)
                extracted['html'] = str(body)
            else:
                extracted['text'] = soup.get_text()
                extracted['html'] = str(soup)

        # Extract abstract/summary
        abstract = self._extract_with_selectors(soup, selectors['abstract'])
        if abstract:
            extracted['abstract'] = self._clean_text(abstract)

        # Extract authors
        authors = self._extract_authors(soup, selectors['authors'])
        extracted['authors'] = authors

        # Extract publication date
        pub_date = self._extract_publication_date(soup, selectors['date'])
        extracted['publish_date'] = pub_date

        # Detect language
        extracted['language'] = self._detect_language(extracted['text'])

        # Determine document type
        extracted['document_type'] = self._determine_document_type(soup, extracted)

        # Add URL
        extracted['url'] = url

        # Create ParsedContent object
        parsed = ParsedContent(**extracted)

        return [asdict(parsed)]

    async def _extract_article_list(self, soup: BeautifulSoup, url: str,
                                  selectors: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Extract multiple articles from a list page"""
        articles = []

        # Find article containers
        article_selectors = selectors.get('article_container', ['.article', '.post', '.item'])
        article_elements = []

        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                article_elements = elements
                break

        # Extract each article
        for article_elem in article_elements:
            try:
                extracted = {}

                # Extract title
                title = self._extract_with_selectors(article_elem, selectors['title'])
                extracted['title'] = self._clean_text(title) if title else 'Untitled'

                # Extract text content
                text = self._extract_text_from_element(article_elem)
                extracted['text'] = text

                # Extract article URL
                link_elem = article_elem.find('a', href=True)
                if link_elem:
                    article_url = urljoin(url, link_elem['href'])
                    extracted['url'] = article_url
                else:
                    extracted['url'] = url

                # Extract other metadata
                extracted['authors'] = self._extract_authors(article_elem, selectors['authors'])
                extracted['publish_date'] = self._extract_publication_date(article_elem, selectors['date'])
                extracted['language'] = self._detect_language(text)
                extracted['document_type'] = 'article'

                # Only include if we have substantial content
                if len(text.split()) > 50:  # At least 50 words
                    parsed = ParsedContent(**extracted)
                    articles.append(asdict(parsed))

            except Exception as e:
                self.logger.warning(f"Error extracting article: {e}")
                continue

        return articles

    def _remove_unwanted_elements(self, soup: BeautifulSoup, exclude_selectors: List[str]):
        """Remove unwanted elements from the soup"""
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove script and style tags
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()

        # Remove elements matching exclude selectors
        for selector in exclude_selectors:
            for element in soup.select(selector):
                element.decompose()

    def _extract_with_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Extract text using a list of CSS selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None

    def _find_element_with_selectors(self, soup: BeautifulSoup, selectors: List[str]):
        """Find element using a list of CSS selectors"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element
        return None

    def _extract_text_from_element(self, element) -> str:
        """Extract clean text from a BeautifulSoup element"""
        if not element:
            return ""

        # Convert to text using html2text for better formatting
        html_content = str(element)
        text = self.html_converter.handle(html_content)

        # Clean up the text
        text = self._clean_text(text)

        return text

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove markdown artifacts from html2text
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links

        # Remove extra newlines
        text = re.sub(r'\n+', '\n', text)

        # Strip and return
        return text.strip()

    def _extract_authors(self, soup: BeautifulSoup, author_selectors: List[str]) -> List[str]:
        """Extract author names from HTML"""
        authors = []

        for selector in author_selectors:
            elements = soup.select(selector)
            for element in elements:
                author_text = element.get_text(strip=True)
                # Clean up author text
                author_text = re.sub(r'^(By:?\s*|Author:?\s*)', '', author_text, flags=re.IGNORECASE)

                # Split multiple authors
                if ',' in author_text:
                    author_list = [a.strip() for a in author_text.split(',')]
                elif ' and ' in author_text:
                    author_list = [a.strip() for a in author_text.split(' and ')]
                else:
                    author_list = [author_text.strip()]

                # Filter out empty authors and add to list
                for author in author_list:
                    if author and len(author) > 2:
                        authors.append(author)

        return list(set(authors))  # Remove duplicates

    def _extract_publication_date(self, soup: BeautifulSoup, date_selectors: List[str]) -> Optional[datetime]:
        """Extract publication date from HTML"""
        # Try selectors first
        for selector in date_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Check for datetime attribute
                datetime_attr = element.get('datetime') or element.get('content')
                if datetime_attr:
                    try:
                        return date_parser.parse(datetime_attr)
                    except:
                        pass

                # Check element text
                date_text = element.get_text(strip=True)
                if date_text:
                    parsed_date = self._parse_date_string(date_text)
                    if parsed_date:
                        return parsed_date

        # Fallback: search for date patterns in text
        all_text = soup.get_text()
        return self._extract_date_from_text(all_text)

    def _parse_date_string(self, date_string: str) -> Optional[datetime]:
        """Parse various date string formats"""
        try:
            # Try dateutil parser first
            return date_parser.parse(date_string, fuzzy=True)
        except:
            # Try regex patterns
            for pattern in self.date_patterns:
                match = re.search(pattern, date_string, re.IGNORECASE)
                if match:
                    try:
                        return date_parser.parse(match.group(1))
                    except:
                        continue
        return None

    def _extract_date_from_text(self, text: str) -> Optional[datetime]:
        """Extract date from free text using patterns"""
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    return date_parser.parse(match)
                except:
                    continue
        return None

    def _detect_language(self, text: str) -> str:
        """Detect language of text content"""
        if not text or len(text.strip()) < 50:
            return 'en'  # Default to English

        try:
            # Use first 1000 characters for detection
            sample = text[:1000]
            return detect(sample)
        except (LangDetectError, Exception):
            return 'en'  # Default to English

    def _determine_document_type(self, soup: BeautifulSoup, extracted: Dict[str, Any]) -> str:
        """Determine document type based on content and structure"""
        title = extracted.get('title', '').lower()

        # Check for specific document type indicators
        if any(keyword in title for keyword in ['report', 'study', 'analysis', 'assessment']):
            return 'report'
        elif any(keyword in title for keyword in ['brief', 'briefing', 'memo', 'note']):
            return 'briefing'
        elif any(keyword in title for keyword in ['comment', 'commentary', 'opinion']):
            return 'commentary'
        elif any(keyword in title for keyword in ['policy', 'recommendation']):
            return 'policy'
        else:
            return 'article'

    async def parse_pdf(self, content: bytes, url: str, source_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse PDF content and extract structured data"""
        try:
            extracted = await self._extract_pdf_content(content)
            if not extracted:
                return None

            # Add URL
            extracted['url'] = url

            # Detect language
            extracted['language'] = self._detect_language(extracted['text'])

            # Set document type to report for PDFs
            extracted['document_type'] = 'report'

            # Create ParsedContent object
            parsed = ParsedContent(**extracted)
            return asdict(parsed)

        except Exception as e:
            self.logger.error(f"Error parsing PDF from {url}: {e}")
            return None

    async def _extract_pdf_content(self, content: bytes) -> Optional[Dict[str, Any]]:
        """Extract text and metadata from PDF content"""
        extracted = {}

        # Try multiple PDF extraction methods
        success = False

        # Method 1: pdfplumber (usually best for text extraction)
        try:
            import io
            pdf_file = io.BytesIO(content)
            with pdfplumber.open(pdf_file) as pdf:
                text_parts = []
                for page in pdf.pages[:20]:  # Limit to first 20 pages
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                if text_parts:
                    extracted['text'] = '\n\n'.join(text_parts)
                    success = True

                    # Extract metadata
                    if pdf.metadata:
                        extracted['title'] = pdf.metadata.get('Title', 'Untitled')
                        extracted['authors'] = self._parse_pdf_authors(pdf.metadata.get('Author', ''))

                        # Try to parse creation date
                        if 'CreationDate' in pdf.metadata:
                            try:
                                extracted['publish_date'] = pdf.metadata['CreationDate']
                            except:
                                pass

        except Exception as e:
            self.logger.debug(f"pdfplumber extraction failed: {e}")

        # Method 2: PyMuPDF (fitz) as fallback
        if not success:
            try:
                import io
                pdf_doc = fitz.open(stream=content, filetype="pdf")
                text_parts = []

                for page_num in range(min(20, len(pdf_doc))):  # Limit to first 20 pages
                    page = pdf_doc[page_num]
                    page_text = page.get_text()
                    if page_text:
                        text_parts.append(page_text)

                if text_parts:
                    extracted['text'] = '\n\n'.join(text_parts)
                    success = True

                    # Extract metadata
                    metadata = pdf_doc.metadata
                    if metadata:
                        extracted['title'] = metadata.get('title', 'Untitled')
                        extracted['authors'] = self._parse_pdf_authors(metadata.get('author', ''))

                pdf_doc.close()

            except Exception as e:
                self.logger.debug(f"PyMuPDF extraction failed: {e}")

        # Method 3: PyPDF2 as final fallback
        if not success:
            try:
                import io
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                text_parts = []
                for page_num in range(min(20, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                if text_parts:
                    extracted['text'] = '\n\n'.join(text_parts)
                    success = True

                    # Extract metadata
                    if pdf_reader.metadata:
                        extracted['title'] = pdf_reader.metadata.get('/Title', 'Untitled')
                        extracted['authors'] = self._parse_pdf_authors(pdf_reader.metadata.get('/Author', ''))

            except Exception as e:
                self.logger.debug(f"PyPDF2 extraction failed: {e}")

        if not success:
            self.logger.warning("All PDF extraction methods failed")
            return None

        # Clean up extracted text
        if 'text' in extracted:
            extracted['text'] = self._clean_pdf_text(extracted['text'])

        # Set defaults
        if 'title' not in extracted or not extracted['title']:
            extracted['title'] = 'Untitled PDF Document'

        if 'authors' not in extracted:
            extracted['authors'] = []

        return extracted

    def _parse_pdf_authors(self, author_string: str) -> List[str]:
        """Parse author string from PDF metadata"""
        if not author_string:
            return []

        # Clean up author string
        author_string = author_string.strip()

        # Split by common separators
        separators = [';', ',', ' and ', ' & ', '\n']
        authors = [author_string]

        for sep in separators:
            new_authors = []
            for author in authors:
                new_authors.extend([a.strip() for a in author.split(sep)])
            authors = new_authors

        # Filter out empty authors
        return [author for author in authors if author and len(author) > 2]

    def _clean_pdf_text(self, text: str) -> str:
        """Clean text extracted from PDF"""
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove page breaks and headers/footers patterns
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)  # Page numbers
        text = re.sub(r'\n\s*\|\s*\n', '\n', text)   # Page separators

        # Fix broken words (common in PDF extraction)
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)

        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)

        return text.strip()


# Utility functions
def asdict(parsed_content: ParsedContent) -> Dict[str, Any]:
    """Convert ParsedContent to dictionary"""
    result = {}
    for field in parsed_content.__dataclass_fields__:
        value = getattr(parsed_content, field)
        if isinstance(value, datetime):
            result[field] = value.isoformat()
        else:
            result[field] = value
    return result


if __name__ == "__main__":
    import asyncio

    async def test_parser():
        """Test the parser functionality"""
        parser = ThinkTankParser()

        # Test HTML parsing
        html_content = b"""
        <html>
        <head><title>Test Article</title></head>
        <body>
            <h1>China's AI Strategy</h1>
            <div class="author">John Doe</div>
            <div class="date">March 15, 2024</div>
            <div class="content">
                <p>This is a test article about China's artificial intelligence strategy.</p>
                <p>It covers multiple aspects of the policy landscape.</p>
            </div>
        </body>
        </html>
        """

        results = await parser.parse_html(html_content, "https://example.com/test", {})
        print("HTML Parsing Results:")
        for result in results:
            print(f"Title: {result['title']}")
            print(f"Authors: {result['authors']}")
            print(f"Date: {result.get('publish_date')}")
            print(f"Language: {result['language']}")
            print(f"Text length: {len(result['text'])} chars")
            print("---")

    # Run test
    # asyncio.run(test_parser())
