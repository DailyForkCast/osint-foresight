"""
Standardization utilities for dates, confidence scores, and other common fields.
Ensures consistency across all artifacts and phases.
"""

from datetime import datetime, date
from typing import Union, Dict, Any, Optional, Tuple
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class DateFormat(Enum):
    """Standard date formats used across the project."""
    FULL_DATE = "%Y-%m-%d"      # ISO 8601 date
    YEAR_MONTH = "%Y-%m"         # Year-month only
    YEAR_ONLY = "%Y"             # Year only
    ISO_DATETIME = "%Y-%m-%dT%H:%M:%S"  # Full ISO datetime
    ISO_DATETIME_TZ = "%Y-%m-%dT%H:%M:%S%z"  # With timezone


class ConfidenceLevel(Enum):
    """Standard confidence levels with numeric mappings."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

    @classmethod
    def from_score(cls, score: float) -> 'ConfidenceLevel':
        """Convert numeric score to confidence level."""
        if score < 0.4:
            return cls.LOW
        elif score < 0.7:
            return cls.MEDIUM
        else:
            return cls.HIGH

    def to_score_range(self) -> Tuple[float, float]:
        """Get numeric range for this confidence level."""
        ranges = {
            ConfidenceLevel.LOW: (0.0, 0.4),
            ConfidenceLevel.MEDIUM: (0.4, 0.7),
            ConfidenceLevel.HIGH: (0.7, 1.0)
        }
        return ranges[self]


class DateStandardizer:
    """Standardize various date formats to ISO 8601."""

    # Common date patterns to recognize
    PATTERNS = [
        (r'^\d{4}-\d{2}-\d{2}$', DateFormat.FULL_DATE),
        (r'^\d{4}-\d{2}$', DateFormat.YEAR_MONTH),
        (r'^\d{4}$', DateFormat.YEAR_ONLY),
        (r'^\d{4}/\d{2}/\d{2}$', "%Y/%m/%d"),
        (r'^\d{2}/\d{2}/\d{4}$', "%d/%m/%Y"),
        (r'^\d{2}-\d{2}-\d{4}$', "%d-%m-%Y"),
        (r'^\d{4}\.\d{2}\.\d{2}$', "%Y.%m.%d"),
        (r'^\d{1,2} \w+ \d{4}$', "%d %B %Y"),
        (r'^\w+ \d{1,2}, \d{4}$', "%B %d, %Y"),
    ]

    @classmethod
    def standardize(cls, date_input: Union[str, datetime, date, int, float],
                   target_format: DateFormat = DateFormat.FULL_DATE) -> str:
        """
        Standardize any date input to ISO format.

        Args:
            date_input: Date in various formats (string, datetime, epoch, etc.)
            target_format: Target format to standardize to

        Returns:
            Standardized date string
        """
        if date_input is None:
            return None

        # Handle datetime/date objects
        if isinstance(date_input, datetime):
            return date_input.strftime(target_format.value)
        elif isinstance(date_input, date):
            return date_input.strftime(target_format.value)

        # Handle epoch timestamps
        elif isinstance(date_input, (int, float)):
            # Assume epoch timestamp
            dt = datetime.fromtimestamp(date_input)
            return dt.strftime(target_format.value)

        # Handle string inputs
        elif isinstance(date_input, str):
            date_input = date_input.strip()

            # Try each pattern
            for pattern_regex, pattern_format in cls.PATTERNS:
                if re.match(pattern_regex, date_input):
                    try:
                        if isinstance(pattern_format, DateFormat):
                            # Already in a standard format
                            if pattern_format == target_format:
                                return date_input
                            # Parse and reformat
                            dt = datetime.strptime(date_input, pattern_format.value)
                        else:
                            # Custom pattern
                            dt = datetime.strptime(date_input, pattern_format)

                        # Format to target
                        if target_format == DateFormat.YEAR_MONTH and pattern_format == DateFormat.YEAR_ONLY:
                            return f"{date_input}-01"  # Default to January
                        elif target_format == DateFormat.FULL_DATE and pattern_format == DateFormat.YEAR_ONLY:
                            return f"{date_input}-01-01"  # Default to January 1st
                        elif target_format == DateFormat.FULL_DATE and pattern_format == DateFormat.YEAR_MONTH:
                            return f"{date_input}-01"  # Default to 1st of month
                        else:
                            return dt.strftime(target_format.value)

                    except ValueError as e:
                        logger.debug(f"Failed to parse {date_input} with pattern {pattern_format}: {e}")
                        continue

            # If no pattern matched, try pandas-style parsing as fallback
            try:
                import pandas as pd
                dt = pd.to_datetime(date_input)
                return dt.strftime(target_format.value)
            except:
                logger.warning(f"Could not parse date: {date_input}")
                return date_input  # Return as-is if unparseable

        else:
            logger.warning(f"Unexpected date type: {type(date_input)}")
            return str(date_input)

    @classmethod
    def validate_iso_date(cls, date_str: str) -> bool:
        """Check if a string is a valid ISO 8601 date."""
        if not date_str:
            return False

        try:
            datetime.strptime(date_str, DateFormat.FULL_DATE.value)
            return True
        except ValueError:
            return False


class ConfidenceStandardizer:
    """Standardize confidence scores and labels."""

    @classmethod
    def standardize(cls, confidence_input: Union[str, float, Dict],
                   include_label: bool = True) -> Dict[str, Any]:
        """
        Standardize confidence to consistent format.

        Args:
            confidence_input: Confidence as string label, numeric score, or dict
            include_label: Whether to include text label

        Returns:
            Dict with 'score' and optionally 'label'
        """
        result = {}

        # Handle dict input
        if isinstance(confidence_input, dict):
            # Already standardized?
            if 'score' in confidence_input:
                result['score'] = float(confidence_input['score'])
            elif 'value' in confidence_input:
                result['score'] = float(confidence_input['value'])
            elif 'confidence' in confidence_input:
                result['score'] = float(confidence_input['confidence'])
            else:
                # Try to extract any numeric value
                for key, value in confidence_input.items():
                    if isinstance(value, (int, float)):
                        result['score'] = float(value)
                        break

            # Get label if requested
            if include_label and 'score' in result:
                if 'label' in confidence_input:
                    result['label'] = confidence_input['label']
                else:
                    result['label'] = ConfidenceLevel.from_score(result['score']).value

        # Handle numeric input
        elif isinstance(confidence_input, (int, float)):
            score = float(confidence_input)

            # Normalize to 0-1 range if needed
            if score > 1:
                if score <= 100:
                    score = score / 100
                else:
                    logger.warning(f"Confidence score {score} out of expected range")
                    score = min(1.0, score / 100)

            result['score'] = score
            if include_label:
                result['label'] = ConfidenceLevel.from_score(score).value

        # Handle string input
        elif isinstance(confidence_input, str):
            confidence_input = confidence_input.strip().lower()

            # Check for text labels
            label_map = {
                'low': (0.2, ConfidenceLevel.LOW),
                'medium': (0.55, ConfidenceLevel.MEDIUM),
                'med': (0.55, ConfidenceLevel.MEDIUM),
                'moderate': (0.55, ConfidenceLevel.MEDIUM),
                'high': (0.85, ConfidenceLevel.HIGH),
                'very high': (0.95, ConfidenceLevel.HIGH),
                'certain': (1.0, ConfidenceLevel.HIGH),
            }

            if confidence_input in label_map:
                score, level = label_map[confidence_input]
                result['score'] = score
                if include_label:
                    result['label'] = level.value
            else:
                # Try to parse as number
                try:
                    score = float(confidence_input.rstrip('%'))
                    if '%' in confidence_input:
                        score = score / 100
                    result['score'] = min(1.0, max(0.0, score))
                    if include_label:
                        result['label'] = ConfidenceLevel.from_score(result['score']).value
                except ValueError:
                    logger.warning(f"Could not parse confidence: {confidence_input}")
                    result['score'] = 0.5  # Default to medium
                    if include_label:
                        result['label'] = ConfidenceLevel.MEDIUM.value

        else:
            logger.warning(f"Unexpected confidence type: {type(confidence_input)}")
            result['score'] = 0.5
            if include_label:
                result['label'] = ConfidenceLevel.MEDIUM.value

        # Ensure score is in valid range
        if 'score' in result:
            result['score'] = round(min(1.0, max(0.0, result['score'])), 3)

        return result


class IDStandardizer:
    """Standardize organization and person identifiers."""

    # Patterns for different ID types
    ID_PATTERNS = {
        'ROR': r'^(?:ROR:)?(?:https://ror\.org/)?([0-9a-z]{9})$',
        'LEI': r'^(?:LEI:)?([0-9A-Z]{20})$',
        'GRID': r'^(?:GRID:)?grid\.([0-9]+\.[0-9a-f]+)$',
        'ORCID': r'^(?:ORCID:)?(?:https://orcid\.org/)?(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])$',
    }

    @classmethod
    def standardize_org_id(cls, id_input: str, id_type: Optional[str] = None) -> str:
        """
        Standardize organization ID to PREFIX:identifier format.

        Args:
            id_input: Raw ID string
            id_type: Optional ID type hint (ROR, LEI, GRID)

        Returns:
            Standardized ID in PREFIX:identifier format
        """
        if not id_input:
            return None

        id_input = str(id_input).strip()

        # Try to detect type if not provided
        if not id_type:
            for prefix, pattern in cls.ID_PATTERNS.items():
                if re.match(pattern, id_input, re.IGNORECASE):
                    id_type = prefix
                    break

        if id_type:
            pattern = cls.ID_PATTERNS.get(id_type)
            if pattern:
                match = re.match(pattern, id_input, re.IGNORECASE)
                if match:
                    return f"{id_type}:{match.group(1)}"

        # Return with detected or provided prefix
        if id_type and not id_input.startswith(f"{id_type}:"):
            return f"{id_type}:{id_input}"

        return id_input

    @classmethod
    def standardize_person_id(cls, id_input: str) -> str:
        """Standardize person ID (primarily ORCID)."""
        if not id_input:
            return None

        id_input = str(id_input).strip()

        # Check ORCID pattern
        match = re.match(cls.ID_PATTERNS['ORCID'], id_input, re.IGNORECASE)
        if match:
            return f"ORCID:{match.group(1)}"

        # If it looks like an ORCID, format it
        if re.match(r'^\d{4}-?\d{4}-?\d{4}-?\d{3}[0-9X]$', id_input):
            # Add hyphens if missing
            clean = id_input.replace('-', '')
            formatted = f"{clean[0:4]}-{clean[4:8]}-{clean[8:12]}-{clean[12:16]}"
            return f"ORCID:{formatted}"

        return id_input


class FieldStandardizer:
    """General field standardization utilities."""

    @classmethod
    def standardize_country_code(cls, country: str, alpha: int = 2) -> str:
        """
        Standardize country codes to ISO 3166-1.

        Args:
            country: Country name or code
            alpha: 2 for alpha-2 (default), 3 for alpha-3

        Returns:
            Standardized country code
        """
        # This would integrate with pycountry or similar
        # For now, basic mapping
        country_map = {
            'USA': 'US', 'United States': 'US', 'America': 'US',
            'UK': 'GB', 'United Kingdom': 'GB', 'Britain': 'GB',
            'Deutschland': 'DE', 'Germany': 'DE',
            'Slovak Republic': 'SK', 'Slovakia': 'SK',
            # Add more as needed
        }

        country = str(country).strip().upper()

        # Check if already in correct format
        if alpha == 2 and len(country) == 2:
            return country
        elif alpha == 3 and len(country) == 3:
            return country

        # Try mapping
        for key, value in country_map.items():
            if key.upper() == country:
                return value

        return country[:2] if alpha == 2 else country[:3]

    @classmethod
    def standardize_language_code(cls, language: str) -> str:
        """Standardize language codes to ISO 639-1."""
        language = str(language).strip().lower()

        # Map common variations
        lang_map = {
            'english': 'en', 'eng': 'en',
            'chinese': 'zh', 'chi': 'zh', 'zho': 'zh',
            'german': 'de', 'deu': 'de', 'ger': 'de',
            'french': 'fr', 'fra': 'fr', 'fre': 'fr',
            'spanish': 'es', 'esp': 'es', 'spa': 'es',
            # Add more as needed
        }

        if language in lang_map:
            return lang_map[language]

        # Return first 2 chars if looks like ISO code
        if len(language) >= 2:
            return language[:2]

        return language


# Convenience functions for common standardizations
def standardize_date(date_input: Any, format: str = "full") -> str:
    """Convenience function for date standardization."""
    format_map = {
        'full': DateFormat.FULL_DATE,
        'month': DateFormat.YEAR_MONTH,
        'year': DateFormat.YEAR_ONLY,
        'datetime': DateFormat.ISO_DATETIME
    }
    target = format_map.get(format, DateFormat.FULL_DATE)
    return DateStandardizer.standardize(date_input, target)


def standardize_confidence(conf_input: Any) -> Dict[str, Any]:
    """Convenience function for confidence standardization."""
    return ConfidenceStandardizer.standardize(conf_input)


def standardize_org_id(id_input: str, id_type: str = None) -> str:
    """Convenience function for org ID standardization."""
    return IDStandardizer.standardize_org_id(id_input, id_type)


def standardize_person_id(id_input: str) -> str:
    """Convenience function for person ID standardization."""
    return IDStandardizer.standardize_person_id(id_input)


# Example usage and tests
if __name__ == "__main__":
    # Test date standardization
    test_dates = [
        "2024-03-15",
        "2024/03/15",
        "15-03-2024",
        "March 15, 2024",
        "2024-03",
        "2024",
        1710460800,  # Epoch timestamp
    ]

    print("Date Standardization Tests:")
    for test_date in test_dates:
        result = standardize_date(test_date)
        print(f"  {test_date} -> {result}")

    print("\nConfidence Standardization Tests:")
    test_confidences = [
        "High",
        "low",
        0.75,
        "85%",
        {"score": 0.6, "label": "Medium"},
        0.3,
    ]

    for test_conf in test_confidences:
        result = standardize_confidence(test_conf)
        print(f"  {test_conf} -> {result}")

    print("\nID Standardization Tests:")
    test_ids = [
        ("https://ror.org/02j61yw88", "ROR"),
        ("grid.12345.6a", "GRID"),
        ("ABCDEFGHIJKLMNOPQRST", "LEI"),
        ("0000-0002-1825-0097", "ORCID"),
    ]

    for test_id, id_type in test_ids:
        result = standardize_org_id(test_id, id_type)
        print(f"  {test_id} -> {result}")
