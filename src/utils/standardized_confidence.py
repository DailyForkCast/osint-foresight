"""
Standardized Confidence Module
All confidence scores use 0-1 scale with uncertainty bands
"""

from typing import Tuple, Dict, Any

class StandardizedConfidence:
    """Unified confidence scoring system"""

    @staticmethod
    def score(value: float, uncertainty: float = 0.1) -> Dict[str, Any]:
        """
        Create standardized confidence score

        Args:
            value: Confidence value (0.0 to 1.0)
            uncertainty: Uncertainty band (default 0.1)

        Returns:
            Standardized confidence dictionary
        """
        return {
            "confidence": round(value, 3),
            "uncertainty": round(uncertainty, 3),
            "range": [
                round(max(0, value - uncertainty), 3),
                round(min(1, value + uncertainty), 3)
            ],
            "category": StandardizedConfidence.categorize(value)
        }

    @staticmethod
    def categorize(value: float) -> str:
        """Map confidence value to category"""
        if value < 0.35:
            return "Low"
        elif value < 0.70:
            return "Medium"
        else:
            return "High"

    @staticmethod
    def to_probability_band(value: float) -> str:
        """Convert to narrative probability band"""
        if value < 0.30:
            return "[10,30)"
        elif value < 0.60:
            return "[30,60)"
        else:
            return "[60,90]"
