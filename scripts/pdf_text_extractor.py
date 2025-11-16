#!/usr/bin/env python3
"""
PDF Text Extraction Module
Extracts text content from PDF files for warehouse integration
Supports fallback between multiple extraction libraries
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PDFTextExtractor:
    """Extract text from PDF files using multiple methods with fallback"""

    def __init__(self):
        self.pdfplumber_available = False
        self.pypdf2_available = False

        # Try importing pdfplumber
        try:
            import pdfplumber
            self.pdfplumber = pdfplumber
            self.pdfplumber_available = True
            logger.info("pdfplumber loaded successfully")
        except ImportError:
            logger.warning("pdfplumber not available")

        # Try importing PyPDF2
        try:
            import PyPDF2
            self.PyPDF2 = PyPDF2
            self.pypdf2_available = True
            logger.info("PyPDF2 loaded successfully")
        except ImportError:
            logger.warning("PyPDF2 not available")

        if not self.pdfplumber_available and not self.pypdf2_available:
            logger.error("No PDF extraction libraries available! Install pdfplumber or PyPDF2")

    def extract_text(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract text from PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with:
                - text: Extracted text content
                - pages: Number of pages
                - method: Extraction method used
                - success: Boolean success flag
        """
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return {
                "text": "",
                "pages": 0,
                "method": "none",
                "success": False,
                "error": "File not found"
            }

        # Try pdfplumber first (generally better quality)
        if self.pdfplumber_available:
            result = self._extract_with_pdfplumber(pdf_file)
            if result["success"]:
                return result
            logger.warning(f"pdfplumber failed for {pdf_file.name}, trying PyPDF2")

        # Fallback to PyPDF2
        if self.pypdf2_available:
            result = self._extract_with_pypdf2(pdf_file)
            if result["success"]:
                return result
            logger.error(f"PyPDF2 also failed for {pdf_file.name}")

        # All methods failed
        return {
            "text": "",
            "pages": 0,
            "method": "none",
            "success": False,
            "error": "All extraction methods failed"
        }

    def _extract_with_pdfplumber(self, pdf_file: Path) -> Dict[str, Any]:
        """Extract text using pdfplumber"""
        try:
            with self.pdfplumber.open(str(pdf_file)) as pdf:
                text_parts = []
                pages = len(pdf.pages)

                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                extracted_text = "\n\n".join(text_parts)

                return {
                    "text": extracted_text,
                    "pages": pages,
                    "method": "pdfplumber",
                    "success": True,
                    "char_count": len(extracted_text)
                }
        except Exception as e:
            logger.error(f"pdfplumber extraction error for {pdf_file.name}: {e}")
            return {
                "text": "",
                "pages": 0,
                "method": "pdfplumber",
                "success": False,
                "error": str(e)
            }

    def _extract_with_pypdf2(self, pdf_file: Path) -> Dict[str, Any]:
        """Extract text using PyPDF2"""
        try:
            with open(pdf_file, 'rb') as f:
                pdf_reader = self.PyPDF2.PdfReader(f)
                text_parts = []
                pages = len(pdf_reader.pages)

                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                extracted_text = "\n\n".join(text_parts)

                return {
                    "text": extracted_text,
                    "pages": pages,
                    "method": "PyPDF2",
                    "success": True,
                    "char_count": len(extracted_text)
                }
        except Exception as e:
            logger.error(f"PyPDF2 extraction error for {pdf_file.name}: {e}")
            return {
                "text": "",
                "pages": 0,
                "method": "PyPDF2",
                "success": False,
                "error": str(e)
            }

    def extract_text_simple(self, pdf_path: str) -> str:
        """
        Simplified interface that just returns the text string

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or empty string on failure
        """
        result = self.extract_text(pdf_path)
        return result.get("text", "") if result else ""


# Convenience function for quick usage
def extract_pdf_text(pdf_path: str) -> str:
    """
    Quick function to extract text from a PDF

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text content
    """
    extractor = PDFTextExtractor()
    return extractor.extract_text_simple(pdf_path)


if __name__ == "__main__":
    # Test the extractor
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) < 2:
        print("Usage: python pdf_text_extractor.py <pdf_file>")
        sys.exit(1)

    test_pdf = sys.argv[1]
    print(f"\n{'='*80}")
    print(f"Testing PDF Text Extraction")
    print(f"{'='*80}\n")
    print(f"File: {test_pdf}\n")

    extractor = PDFTextExtractor()
    result = extractor.extract_text(test_pdf)

    print(f"Success: {result['success']}")
    print(f"Method: {result['method']}")
    print(f"Pages: {result['pages']}")
    print(f"Characters: {result.get('char_count', 0):,}")

    if result['success']:
        preview = result['text'][:500]
        print(f"\nText Preview (first 500 chars):")
        print(f"{'-'*80}")
        print(preview)
        print(f"{'-'*80}")
    else:
        print(f"\nError: {result.get('error', 'Unknown error')}")
