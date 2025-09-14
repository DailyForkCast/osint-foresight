"""
Citation validator and standardizer for OSINT Foresight.
Ensures all citations include exact URLs and accessed dates.
"""

import re
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
import logging
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """Represents a standardized citation with all required fields."""

    # Required fields
    exact_url: str
    title: str
    accessed_date: str

    # Optional but recommended fields
    author: Optional[str] = None
    publication: Optional[str] = None
    publication_date: Optional[str] = None
    archive_url: Optional[str] = None
    doi: Optional[str] = None
    document_type: Optional[str] = None

    # Tracking fields
    extraction_date: Optional[str] = None
    verification_date: Optional[str] = None
    confidence_score: Optional[float] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate citation upon creation."""
        self.validate()

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the citation meets all requirements."""
        errors = []

        # Validate URL
        url_errors = self._validate_url()
        errors.extend(url_errors)

        # Validate accessed_date
        date_errors = self._validate_accessed_date()
        errors.extend(date_errors)

        # Validate title
        if not self.title or len(self.title.strip()) == 0:
            errors.append("Title cannot be empty")

        return len(errors) == 0, errors

    def _validate_url(self) -> List[str]:
        """Validate that URL is exact and not a homepage."""
        errors = []

        if not self.exact_url:
            errors.append("URL is required")
            return errors

        # Check URL format
        if not self.exact_url.startswith(('http://', 'https://')):
            errors.append(f"URL must start with http:// or https://: {self.exact_url}")

        # Parse URL
        try:
            parsed = urlparse(self.exact_url)

            # Check if it's just a homepage (no path or only /)
            if not parsed.path or parsed.path == '/':
                errors.append(
                    f"URL appears to be a homepage, not a specific document: {self.exact_url}\n"
                    f"Please provide the full URL to the specific article or document."
                )

            # Warn about common homepage patterns
            homepage_patterns = [
                r'^https?://[^/]+/?$',
                r'^https?://www\.[^/]+/?$',
                r'^https?://[^/]+/index\.(html?|php|asp)$'
            ]

            for pattern in homepage_patterns:
                if re.match(pattern, self.exact_url):
                    errors.append(
                        f"URL appears to be a homepage: {self.exact_url}\n"
                        f"Citation must link to specific document."
                    )
                    break

        except Exception as e:
            errors.append(f"Invalid URL format: {e}")

        return errors

    def _validate_accessed_date(self) -> List[str]:
        """Validate accessed_date format and logic."""
        errors = []

        if not self.accessed_date:
            errors.append("accessed_date is REQUIRED for all citations")
            return errors

        # Check date format (YYYY-MM-DD)
        try:
            parsed_date = datetime.strptime(self.accessed_date, "%Y-%m-%d")

            # Check if date is in future
            if parsed_date.date() > date.today():
                errors.append(f"accessed_date cannot be in the future: {self.accessed_date}")

        except ValueError:
            errors.append(
                f"accessed_date must be in YYYY-MM-DD format, got: {self.accessed_date}"
            )

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert citation to dictionary format."""
        return {
            'exact_url': self.exact_url,
            'title': self.title,
            'accessed_date': self.accessed_date,
            'author': self.author,
            'publication': self.publication,
            'publication_date': self.publication_date,
            'archive_url': self.archive_url,
            'doi': self.doi,
            'document_type': self.document_type,
            'extraction_date': self.extraction_date,
            'verification_date': self.verification_date,
            'confidence_score': self.confidence_score,
            'metadata': self.metadata
        }

    def to_formatted_string(self) -> str:
        """Generate formatted citation string."""
        parts = []

        # Author
        if self.author:
            parts.append(f"{self.author}.")

        # Publication date
        if self.publication_date:
            parts.append(f"({self.publication_date}).")

        # Title
        parts.append(f"{self.title}.")

        # Publication
        if self.publication:
            parts.append(f"{self.publication}.")

        # Retrieved statement
        parts.append(f"Retrieved {self.accessed_date}, from {self.exact_url}")

        # Archive
        if self.archive_url:
            parts.append(f"[Archived at: {self.archive_url}]")

        return " ".join(parts)


class CitationValidator:
    """Validates and standardizes citations across the project."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_checked': 0,
            'valid': 0,
            'invalid': 0,
            'missing_accessed_date': 0,
            'homepage_urls': 0,
            'missing_archive': 0
        }

    def validate_citation_dict(self, citation_data: Dict) -> Tuple[bool, List[str]]:
        """Validate a citation in dictionary format."""
        errors = []

        # Check for required fields
        required = ['exact_url', 'title', 'accessed_date']
        for field in required:
            if field not in citation_data or not citation_data[field]:
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, errors

        # Create Citation object for validation
        try:
            citation = Citation(
                exact_url=citation_data.get('exact_url', ''),
                title=citation_data.get('title', ''),
                accessed_date=citation_data.get('accessed_date', ''),
                author=citation_data.get('author'),
                publication=citation_data.get('publication'),
                publication_date=citation_data.get('publication_date'),
                archive_url=citation_data.get('archive_url'),
                doi=citation_data.get('doi'),
                document_type=citation_data.get('document_type')
            )

            is_valid, validation_errors = citation.validate()
            return is_valid, validation_errors

        except Exception as e:
            return False, [str(e)]

    def validate_batch(self, citations: List[Dict]) -> Dict[str, Any]:
        """Validate a batch of citations and return report."""
        results = {
            'valid': [],
            'invalid': [],
            'stats': self.stats.copy()
        }

        for citation_data in citations:
            self.stats['total_checked'] += 1

            is_valid, errors = self.validate_citation_dict(citation_data)

            if is_valid:
                self.stats['valid'] += 1
                results['valid'].append(citation_data)
            else:
                self.stats['invalid'] += 1
                results['invalid'].append({
                    'citation': citation_data,
                    'errors': errors
                })

                # Track specific error types
                for error in errors:
                    if 'accessed_date' in error.lower():
                        self.stats['missing_accessed_date'] += 1
                    if 'homepage' in error.lower():
                        self.stats['homepage_urls'] += 1

        results['stats'] = self.stats
        return results

    def fix_common_issues(self, citation_data: Dict) -> Dict:
        """Attempt to fix common citation issues."""
        fixed = citation_data.copy()

        # Add today's date if accessed_date is missing
        if 'accessed_date' not in fixed or not fixed['accessed_date']:
            fixed['accessed_date'] = date.today().strftime("%Y-%m-%d")
            logger.warning(f"Added today's date as accessed_date for: {fixed.get('title', 'Unknown')}")

        # Fix date format if needed
        if 'accessed_date' in fixed:
            fixed['accessed_date'] = self._standardize_date(fixed['accessed_date'])

        if 'publication_date' in fixed:
            fixed['publication_date'] = self._standardize_date(fixed['publication_date'])

        # Clean URL
        if 'exact_url' in fixed:
            fixed['exact_url'] = self._clean_url(fixed['exact_url'])

        # Ensure title exists
        if 'title' not in fixed or not fixed['title']:
            # Try to extract from URL or set placeholder
            fixed['title'] = self._extract_title_from_url(fixed.get('exact_url', ''))

        return fixed

    def _standardize_date(self, date_str: str) -> str:
        """Convert various date formats to YYYY-MM-DD."""
        if not date_str:
            return ""

        # Already in correct format?
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str

        # Try common formats
        formats = [
            "%Y/%m/%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%B %d, %Y",
            "%d %B %Y",
            "%Y%m%d"
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_str}")
        return date_str

    def _clean_url(self, url: str) -> str:
        """Clean and validate URL."""
        if not url:
            return ""

        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Remove trailing slashes from document URLs (but keep for actual paths)
        if url.count('/') > 3:  # More than just protocol://domain/
            url = url.rstrip('/')

        return url

    def _extract_title_from_url(self, url: str) -> str:
        """Try to extract a title from URL path."""
        if not url:
            return "Untitled Document"

        try:
            parsed = urlparse(url)
            path = parsed.path

            # Get last part of path
            if path and path != '/':
                # Remove extension
                title = path.split('/')[-1]
                title = re.sub(r'\.[^.]+$', '', title)
                # Replace separators with spaces
                title = re.sub(r'[-_]', ' ', title)
                # Capitalize words
                title = title.title()
                return title
        except:
            pass

        return "Untitled Document"

    def generate_report(self) -> str:
        """Generate a validation report."""
        report = []
        report.append("=" * 60)
        report.append("Citation Validation Report")
        report.append("=" * 60)
        report.append(f"Total Citations Checked: {self.stats['total_checked']}")
        report.append(f"Valid: {self.stats['valid']}")
        report.append(f"Invalid: {self.stats['invalid']}")
        report.append("")

        if self.stats['invalid'] > 0:
            report.append("Common Issues Found:")
            if self.stats['missing_accessed_date'] > 0:
                report.append(f"  - Missing accessed_date: {self.stats['missing_accessed_date']}")
            if self.stats['homepage_urls'] > 0:
                report.append(f"  - Homepage URLs instead of specific documents: {self.stats['homepage_urls']}")
            if self.stats['missing_archive'] > 0:
                report.append(f"  - Missing archive URLs (recommended): {self.stats['missing_archive']}")

        report.append("")
        report.append("Validation Rate: {:.1f}%".format(
            (self.stats['valid'] / self.stats['total_checked'] * 100) if self.stats['total_checked'] > 0 else 0
        ))

        return "\n".join(report)


def validate_file(filepath: str) -> None:
    """Validate all citations in a JSON file."""
    validator = CitationValidator()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract citations based on common structures
        citations = []

        # Check different possible locations
        if 'citations' in data:
            citations = data['citations']
        elif 'references' in data:
            citations = data['references']
        elif 'sources' in data:
            citations = data['sources']
        elif isinstance(data, list):
            citations = data

        if citations:
            results = validator.validate_batch(citations)

            print(validator.generate_report())

            if results['invalid']:
                print("\nInvalid Citations Found:")
                for item in results['invalid']:
                    print(f"\nTitle: {item['citation'].get('title', 'Unknown')}")
                    print(f"URL: {item['citation'].get('exact_url', 'Missing')}")
                    print("Errors:")
                    for error in item['errors']:
                        print(f"  - {error}")
        else:
            print(f"No citations found in {filepath}")

    except Exception as e:
        print(f"Error validating file: {e}")


# Example usage
if __name__ == "__main__":
    # Test citations
    test_citations = [
        {
            "title": "Mass Firing of Probationary Federal Employees Was Illegal, Judge Rules",
            "exact_url": "https://www.nytimes.com/2025/09/13/us/politics/probationary-employees-firing-illegal.html",
            "accessed_date": "2025-09-13",
            "author": "Charlie Savage",
            "publication": "The New York Times"
        },
        {
            "title": "Bad Citation - Homepage Only",
            "exact_url": "https://www.nytimes.com",  # This should fail
            "accessed_date": "2025-09-13"
        },
        {
            "title": "Missing Accessed Date",
            "exact_url": "https://example.com/article/specific-page.html"
            # Missing accessed_date - should fail
        }
    ]

    validator = CitationValidator()
    results = validator.validate_batch(test_citations)

    print(validator.generate_report())

    # Show how to fix issues
    print("\n" + "=" * 60)
    print("Attempting to fix common issues...")
    print("=" * 60)

    for invalid in results['invalid']:
        fixed = validator.fix_common_issues(invalid['citation'])
        is_valid, errors = validator.validate_citation_dict(fixed)

        if is_valid:
            print(f"✓ Fixed: {fixed['title']}")
        else:
            print(f"✗ Still invalid: {fixed['title']}")
            for error in errors:
                print(f"  - {error}")