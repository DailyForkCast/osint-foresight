"""
Regional adapter for data source selection and terminology standardization.
Ensures region-agnostic data collection and reporting.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Region(Enum):
    """Supported regions for data collection."""
    EU = "EU"
    US = "US"
    UK = "UK"
    CANADA = "Canada"
    AUSTRALIA = "Australia"
    ASIA_PACIFIC = "Asia_Pacific"
    DEFAULT = "default"

    @classmethod
    def from_country(cls, country_code: str) -> 'Region':
        """Determine region from country code."""
        eu_countries = {
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
            'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
            'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
        }

        asia_pacific = {
            'JP', 'KR', 'CN', 'SG', 'MY', 'TH', 'ID', 'PH', 'VN', 'IN',
            'AU', 'NZ'
        }

        country_code = country_code.upper()

        if country_code in eu_countries:
            return cls.EU
        elif country_code == 'US':
            return cls.US
        elif country_code == 'GB':
            return cls.UK
        elif country_code == 'CA':
            return cls.CANADA
        elif country_code == 'AU':
            return cls.AUSTRALIA
        elif country_code in asia_pacific:
            return cls.ASIA_PACIFIC
        else:
            return cls.DEFAULT


@dataclass
class DataSource:
    """Represents a data source with regional context."""
    name: str
    type: str  # procurement, funding, patent, etc.
    region: Region
    priority: int
    endpoint: Optional[str] = None
    requires_auth: bool = False
    rate_limit: Optional[str] = None


class RegionalAdapter:
    """Adapts data collection to regional contexts."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize with regional configuration."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'data_sources_regional.yaml'

        self.config = self._load_config(config_path)
        self.terminology_map = self.config.get('terminology_map', {})

    def _load_config(self, config_path: Path) -> Dict:
        """Load regional configuration."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load regional config: {e}")
            return {}

    def get_data_sources(self, country_code: str, source_type: str) -> List[DataSource]:
        """
        Get prioritized data sources for a country and type.

        Args:
            country_code: ISO 2-letter country code
            source_type: Type of source (procurement, funding, patent, etc.)

        Returns:
            List of DataSource objects in priority order
        """
        region = Region.from_country(country_code)
        sources = []

        # Get source configuration
        source_config = self.config.get(f"{source_type}_sources", {})

        # Try region-specific first, then default
        regional_config = source_config.get(region.value, source_config.get('default', {}))

        if 'priority_order' in regional_config:
            for i, source_name in enumerate(regional_config['priority_order']):
                source = DataSource(
                    name=source_name,
                    type=source_type,
                    region=region,
                    priority=i
                )

                # Add endpoint if available
                if 'endpoints' in regional_config:
                    source.endpoint = regional_config['endpoints'].get(source_name)

                sources.append(source)

        # Add global sources if available
        if 'global' in source_config:
            global_config = source_config['global']
            if 'priority_order' in global_config:
                for i, source_name in enumerate(global_config['priority_order']):
                    source = DataSource(
                        name=source_name,
                        type=source_type,
                        region=Region.DEFAULT,
                        priority=len(sources) + i
                    )

                    if 'endpoints' in global_config:
                        source.endpoint = global_config['endpoints'].get(source_name)

                    sources.append(source)

        return sources

    def standardize_terminology(self, text: str) -> str:
        """
        Replace region-specific terms with neutral equivalents.

        Args:
            text: Text containing potentially region-specific terms

        Returns:
            Text with standardized terminology
        """
        result = text

        for specific_term, neutral_term in self.terminology_map.items():
            result = result.replace(specific_term, neutral_term)
            # Case-insensitive replacement
            result = result.replace(specific_term.lower(), neutral_term.lower())
            result = result.replace(specific_term.upper(), neutral_term.upper())

        return result

    def get_source_priority(self, country_code: str, source_type: str) -> Dict[str, int]:
        """
        Get source priority mapping for a country.

        Returns:
            Dict mapping source names to priority (lower is better)
        """
        sources = self.get_data_sources(country_code, source_type)
        return {s.name: s.priority for s in sources}

    def format_source_list(self, country_code: str, source_type: str,
                          max_sources: int = 5) -> str:
        """
        Format a human-readable list of recommended sources.

        Args:
            country_code: ISO 2-letter country code
            source_type: Type of source
            max_sources: Maximum number of sources to list

        Returns:
            Formatted string listing sources
        """
        sources = self.get_data_sources(country_code, source_type)[:max_sources]

        if not sources:
            return f"No {source_type} sources configured for {country_code}"

        lines = [f"Recommended {source_type} sources for {country_code}:"]
        for i, source in enumerate(sources, 1):
            line = f"{i}. {source.name}"
            if source.endpoint:
                line += f" ({source.endpoint})"
            lines.append(line)

        return "\n".join(lines)

    def get_national_first_sources(self, country_code: str) -> Dict[str, List[str]]:
        """
        Get all source types with national sources listed first.

        Returns:
            Dict mapping source type to prioritized source list
        """
        result = {}

        source_types = [
            'procurement', 'funding', 'patent', 'standards',
            'academic', 'organization', 'trade'
        ]

        for source_type in source_types:
            sources = self.get_data_sources(country_code, source_type)

            # Separate national from others
            national = []
            regional = []
            global_sources = []

            for source in sources:
                if 'national' in source.name.lower():
                    national.append(source.name)
                elif source.region != Region.DEFAULT:
                    regional.append(source.name)
                else:
                    global_sources.append(source.name)

            # Combine with national first
            result[source_type] = national + regional + global_sources

        return result

    def validate_source_availability(self, country_code: str,
                                    source_name: str) -> Dict[str, Any]:
        """
        Check if a specific source is available for a country.

        Returns:
            Dict with availability status and alternatives
        """
        region = Region.from_country(country_code)

        # Search all source types
        found = False
        source_type = None
        alternatives = []

        for st in ['procurement', 'funding', 'patent', 'standards',
                   'academic', 'organization', 'trade']:
            sources = self.get_data_sources(country_code, st)
            source_names = [s.name for s in sources]

            if source_name in source_names:
                found = True
                source_type = st
                break

            # Check for similar names
            for s in sources:
                if source_name.lower() in s.name.lower():
                    alternatives.append(s.name)

        return {
            'available': found,
            'source_type': source_type,
            'region': region.value,
            'alternatives': alternatives[:5]  # Top 5 alternatives
        }


class SourceSelector:
    """Selects appropriate data sources based on context."""

    def __init__(self, adapter: RegionalAdapter):
        self.adapter = adapter

    def select_sources(self, country_code: str, source_type: str,
                      required_sources: int = 2,
                      prefer_free: bool = True) -> List[DataSource]:
        """
        Select optimal sources based on requirements.

        Args:
            country_code: Target country
            source_type: Type of data source
            required_sources: Minimum number of sources needed
            prefer_free: Prefer free sources when available

        Returns:
            List of selected sources
        """
        all_sources = self.adapter.get_data_sources(country_code, source_type)

        if not all_sources:
            logger.warning(f"No sources available for {country_code}/{source_type}")
            return []

        # Filter by availability
        selected = []

        if prefer_free:
            # Prioritize free sources
            free_sources = [s for s in all_sources if not s.requires_auth]
            selected.extend(free_sources[:required_sources])

        # Add more if needed
        if len(selected) < required_sources:
            remaining = [s for s in all_sources if s not in selected]
            selected.extend(remaining[:required_sources - len(selected)])

        return selected[:required_sources]

    def get_fallback_chain(self, country_code: str,
                          source_type: str) -> List[List[DataSource]]:
        """
        Get tiered fallback chains for resilient data collection.

        Returns:
            List of source tiers (try tier 1 first, then tier 2, etc.)
        """
        all_sources = self.adapter.get_data_sources(country_code, source_type)

        # Group by characteristics
        tier1 = [s for s in all_sources if 'national' in s.name.lower()]
        tier2 = [s for s in all_sources if s.region != Region.DEFAULT and s not in tier1]
        tier3 = [s for s in all_sources if s not in tier1 and s not in tier2]

        return [tier1, tier2, tier3]


# Convenience functions
def get_regional_sources(country_code: str, source_type: str) -> List[str]:
    """Get source names for a country and type."""
    adapter = RegionalAdapter()
    sources = adapter.get_data_sources(country_code, source_type)
    return [s.name for s in sources]


def neutralize_text(text: str) -> str:
    """Remove region-specific terminology from text."""
    adapter = RegionalAdapter()
    return adapter.standardize_terminology(text)


def select_best_sources(country_code: str, source_type: str,
                       count: int = 3) -> List[str]:
    """Select the best sources for a country and type."""
    adapter = RegionalAdapter()
    selector = SourceSelector(adapter)
    sources = selector.select_sources(country_code, source_type, count)
    return [s.name for s in sources]


# Example usage
if __name__ == "__main__":
    # Test with different countries
    test_countries = ['SK', 'US', 'GB', 'JP', 'BR']

    adapter = RegionalAdapter()

    for country in test_countries:
        print(f"\n{country} Configuration:")
        print("-" * 40)

        # Get procurement sources
        print(adapter.format_source_list(country, 'procurement'))

        # Get funding sources
        print("\n" + adapter.format_source_list(country, 'funding'))

        # Test terminology standardization
        eu_text = "The Horizon Europe project received TED tender through CORDIS"
        neutral = adapter.standardize_terminology(eu_text)
        print(f"\nOriginal: {eu_text}")
        print(f"Neutral: {neutral}")

        # Get national-first ordering
        national_first = adapter.get_national_first_sources(country)
        print(f"\nNational-first sources for {country}:")
        for source_type, sources in national_first.items():
            if sources:
                print(f"  {source_type}: {sources[:3]}...")  # First 3
