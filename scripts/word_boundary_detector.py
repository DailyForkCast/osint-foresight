
import re

class WordBoundaryChineseDetector:
    """
    Enhanced Chinese entity detection with word boundary checking

    Prevents substring false positives:
    - "MACHINARY" no longer matches "CHINA"
    - "HEIZTECHNIK" no longer matches "ZTE"
    - "KASINO" no longer matches "SINO"
    """

    @staticmethod
    def detect_pattern_with_boundary(text, patterns, min_length=3):
        """
        Detect patterns using word boundaries

        Args:
            text: Text to search
            patterns: List/set of patterns to match
            min_length: Minimum pattern length for boundary checking (default: 3)

        Returns:
            (matched_pattern, confidence) or (None, 0)
        """
        if not text:
            return None, 0

        text_upper = text.upper()

        for pattern in patterns:
            pattern_upper = pattern.upper()

            # For very short patterns (< min_length), require exact word match
            if len(pattern_upper) < min_length:
                # Must be a complete word
                if re.search(r'\b' + re.escape(pattern_upper) + r'\b', text_upper):
                    return pattern, 0.9
            else:
                # For longer patterns, check word boundary
                if re.search(r'\b' + re.escape(pattern_upper) + r'\b', text_upper):
                    return pattern, 0.9
                # Also allow as part of compound (with hyphen or underscore)
                elif re.search(r'(^|[\s_-])' + re.escape(pattern_upper) + r'($|[\s_-])', text_upper):
                    return pattern, 0.85

        return None, 0

    @staticmethod
    def detect_chinese_name(company_name, chinese_patterns):
        """
        Detect Chinese company name with word boundaries

        Example usage:
            patterns = ['HUAWEI', 'ZTE', 'BEIJING', 'SHANGHAI', 'CHINA']
            matched, confidence = WordBoundaryChineseDetector.detect_chinese_name(name, patterns)
        """
        return WordBoundaryChineseDetector.detect_pattern_with_boundary(
            company_name, chinese_patterns, min_length=3
        )

    @staticmethod
    def detect_chinese_country(country_text, country_patterns):
        """
        Detect Chinese country indicators with word boundaries

        Example usage:
            patterns = ['CHINA', 'CHN', 'PRC', 'BEIJING', 'SHANGHAI']
            matched, confidence = WordBoundaryChineseDetector.detect_chinese_country(country, patterns)
        """
        return WordBoundaryChineseDetector.detect_pattern_with_boundary(
            country_text, country_patterns, min_length=2
        )
