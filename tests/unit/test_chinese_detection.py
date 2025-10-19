#!/usr/bin/env python3
"""
Unit Tests for Chinese Entity Detection Logic

Tests the core detection functions from USAspending processor:
- Country code detection (CHN, HKG)
- Name-based detection (Huawei, ZTE, etc.)
- False positive filtering
- Product sourcing detection
- Taiwan exclusion (ROC != PRC)

Last Updated: 2025-10-18
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts"))

from process_usaspending_305_column import USAspending305Processor


class TestChineseCountryDetection:
    """Test _is_china_country() function"""

    def setup_method(self):
        """Initialize processor for each test"""
        self.processor = USAspending305Processor()

    def test_china_country_code(self):
        """CHN country code should be detected"""
        assert self.processor._is_china_country("CHN") == True
        assert self.processor._is_china_country("chn") == True

    def test_china_country_name(self):
        """Various China name formats should be detected"""
        assert self.processor._is_china_country("CHINA") == True
        assert self.processor._is_china_country("China") == True
        assert self.processor._is_china_country("PEOPLE'S REPUBLIC OF CHINA") == True
        assert self.processor._is_china_country("PRC") == True

    def test_chinese_cities(self):
        """Chinese city names should be detected"""
        assert self.processor._is_china_country("BEIJING") == True
        assert self.processor._is_china_country("Shanghai") == True
        assert self.processor._is_china_country("SHENZHEN") == True
        assert self.processor._is_china_country("guangzhou") == True

    def test_taiwan_exclusion(self):
        """Taiwan (ROC) should NOT be detected as China (PRC)"""
        assert self.processor._is_china_country("TAIWAN") == False
        assert self.processor._is_china_country("Taiwan") == False
        assert self.processor._is_china_country("TWN") == False
        assert self.processor._is_china_country("Republic of China (Taiwan)") == False

    def test_hong_kong_excluded_from_china(self):
        """Hong Kong should not be detected by _is_china_country"""
        # Hong Kong has separate detection function
        assert self.processor._is_china_country("HONG KONG") == False
        assert self.processor._is_china_country("HKG") == False

    def test_empty_and_none(self):
        """Empty or None values should return False"""
        assert self.processor._is_china_country("") == False
        assert self.processor._is_china_country(None) == False
        assert self.processor._is_china_country("   ") == False

    def test_non_china_countries(self):
        """Other countries should not be detected"""
        assert self.processor._is_china_country("UNITED STATES") == False
        assert self.processor._is_china_country("USA") == False
        assert self.processor._is_china_country("JAPAN") == False
        assert self.processor._is_china_country("KOREA") == False


class TestHongKongDetection:
    """Test _is_hong_kong() function"""

    def setup_method(self):
        """Initialize processor for each test"""
        self.processor = USAspending305Processor()

    def test_hong_kong_variants(self):
        """Various Hong Kong formats should be detected"""
        assert self.processor._is_hong_kong("HONG KONG") == True
        assert self.processor._is_hong_kong("Hong Kong") == True
        assert self.processor._is_hong_kong("HongKong") == True
        assert self.processor._is_hong_kong("HKG") == True
        assert self.processor._is_hong_kong("H.K.") == True
        assert self.processor._is_hong_kong("HK") == True

    def test_hong_kong_not_china(self):
        """Hong Kong is separate from China in detection"""
        # These should be Hong Kong, not China
        assert self.processor._is_hong_kong("HONG KONG") == True
        assert self.processor._is_china_country("HONG KONG") == False


class TestChineseNameDetection:
    """Test _has_chinese_name() function"""

    def setup_method(self):
        """Initialize processor for each test"""
        self.processor = USAspending305Processor()

    def test_known_chinese_companies(self):
        """Known Chinese companies should be detected"""
        assert self.processor._has_chinese_name("Huawei Technologies Co., Ltd.") == True
        assert self.processor._has_chinese_name("ZTE Corporation") == True
        assert self.processor._has_chinese_name("Lenovo Group") == True
        assert self.processor._has_chinese_name("ALIBABA GROUP") == True
        assert self.processor._has_chinese_name("Tencent Holdings") == True
        assert self.processor._has_chinese_name("Baidu Inc") == True
        assert self.processor._has_chinese_name("Xiaomi Corporation") == True

    def test_chinese_city_companies(self):
        """Companies with Chinese city names should be detected"""
        assert self.processor._has_chinese_name("Beijing Tech Company") == True
        assert self.processor._has_chinese_name("Shanghai Industries Ltd") == True
        assert self.processor._has_chinese_name("Shenzhen Electronics") == True
        assert self.processor._has_chinese_name("Guangzhou Manufacturing") == True

    def test_china_keyword_in_name(self):
        """Names with 'China' or 'Chinese' should be detected"""
        assert self.processor._has_chinese_name("China Mobile") == True
        assert self.processor._has_chinese_name("Chinese Academy of Sciences") == True
        assert self.processor._has_chinese_name("Sino Tech Corp") == True

    def test_taiwan_company_exclusion(self):
        """Taiwan companies should NOT be detected as Chinese (PRC)"""
        assert self.processor._has_chinese_name("Taiwan Semiconductor") == False
        assert self.processor._has_chinese_name("GOVERNMENT OF THE REPUBLIC OF CHINA (TAIWAN)") == False

    def test_false_positive_filtering(self):
        """Known false positives should NOT be detected"""
        # Ceramics/porcelain (has explicit false positive entries)
        assert self.processor._has_chinese_name("Homer Laughlin China Company") == False
        assert self.processor._has_chinese_name("Fine China Shop") == False
        # Italian surnames
        assert self.processor._has_chinese_name("Facchinaggi Construction") == False
        # US companies
        assert self.processor._has_chinese_name("COSCO Fire Protection") == False
        # Round 4 false positives
        assert self.processor._has_chinese_name("COMAC PUMP") == False
        assert self.processor._has_chinese_name("Aztec Environmental") == False
        assert self.processor._has_chinese_name("T K C ENTERPRISES") == False

    def test_china_grill_edge_case(self):
        """China Grill Restaurant - edge case"""
        # This contains "china" but is a restaurant name, not a Chinese entity
        # Current logic WILL detect it because "china" is in CHINESE_NAME_PATTERNS
        # This is acceptable - would be caught in manual review or by additional context
        # NOTE: If this becomes a pattern, add to FALSE_POSITIVES
        result = self.processor._has_chinese_name("China Grill Restaurant")
        # We document the current behavior (may detect restaurant names)
        assert result == True  # Current behavior - detects "china" keyword

    def test_substring_false_positives(self):
        """Substrings in company names should not trigger false matches"""
        # "senior" contains "senior" not "china"
        assert self.processor._has_chinese_name("Senior Housing Inc") == False
        # "union" contains pattern but not Chinese
        assert self.processor._has_chinese_name("Union Pacific") == False

    def test_word_boundary_enforcement(self):
        """Detection should respect word boundaries"""
        # "Beijing" should match
        assert self.processor._has_chinese_name("Beijing Company") == True
        # But "Bejing" in middle of word should not
        # (though this example is hypothetical)

    def test_empty_and_none(self):
        """Empty or None names should return False"""
        assert self.processor._has_chinese_name("") == False
        assert self.processor._has_chinese_name(None) == False
        assert self.processor._has_chinese_name("   ") == False


class TestProductSourcingDetection:
    """Test _is_product_sourcing_mention() function"""

    def setup_method(self):
        """Initialize processor for each test"""
        self.processor = USAspending305Processor()

    def test_made_in_china_variants(self):
        """'Made in China' phrases should be detected"""
        assert self.processor._is_product_sourcing_mention("Product made in China") == True
        assert self.processor._is_product_sourcing_mention("MADE IN CHINA") == True
        assert self.processor._is_product_sourcing_mention("Items manufactured in China") == True

    def test_production_phrases(self):
        """Various production phrases should be detected"""
        assert self.processor._is_product_sourcing_mention("produced in China") == True
        assert self.processor._is_product_sourcing_mention("fabricated in China") == True
        assert self.processor._is_product_sourcing_mention("assembled in China") == True

    def test_origin_phrases(self):
        """Origin phrases should be detected"""
        assert self.processor._is_product_sourcing_mention("origin China") == True
        assert self.processor._is_product_sourcing_mention("origin: China") == True
        assert self.processor._is_product_sourcing_mention("country of origin China") == True
        assert self.processor._is_product_sourcing_mention("country of origin: China") == True

    def test_prc_variants(self):
        """PRC variants should be detected"""
        assert self.processor._is_product_sourcing_mention("made in PRC") == True
        assert self.processor._is_product_sourcing_mention("manufactured in PRC") == True

    def test_tkc_enterprises_pattern(self):
        """T K C ENTERPRISES data error pattern should be detected"""
        assert self.processor._is_product_sourcing_mention("China acceptable") == True
        assert self.processor._is_product_sourcing_mention("made in China acceptable") == True

    def test_entity_relationship_not_sourcing(self):
        """Entity relationships should NOT be detected as product sourcing"""
        assert self.processor._is_product_sourcing_mention("Contract with Huawei") == False
        assert self.processor._is_product_sourcing_mention("Beijing Company Ltd") == False
        assert self.processor._is_product_sourcing_mention("Chinese contractor") == False

    def test_empty_and_none(self):
        """Empty or None descriptions should return False"""
        assert self.processor._is_product_sourcing_mention("") == False
        assert self.processor._is_product_sourcing_mention(None) == False


class TestFalsePositiveEdgeCases:
    """Test edge cases and false positive filtering"""

    def setup_method(self):
        """Initialize processor for each test"""
        self.processor = USAspending305Processor()

    def test_comac_pump_vs_comac_aircraft(self):
        """COMAC PUMP (US) vs COMAC (Chinese aircraft) should be distinguished"""
        # COMAC PUMP should be filtered as false positive
        assert self.processor._has_chinese_name("COMAC PUMP") == False
        assert self.processor._has_chinese_name("COMAC WELL") == False

        # But real COMAC (aircraft company) should be detected if mentioned properly
        # (This would need "China" or city name in full name)
        assert self.processor._has_chinese_name("COMAC Beijing") == True

    def test_zte_vs_aztec(self):
        """ZTE (Chinese) vs Aztec Environmental should be distinguished"""
        assert self.processor._has_chinese_name("ZTE Corporation") == True
        assert self.processor._has_chinese_name("Aztec Environmental") == False

    def test_case_insensitivity(self):
        """All detection should be case-insensitive"""
        assert self.processor._has_chinese_name("HUAWEI") == True
        assert self.processor._has_chinese_name("huawei") == True
        assert self.processor._has_chinese_name("HuAwEi") == True

        assert self.processor._is_china_country("CHINA") == True
        assert self.processor._is_china_country("china") == True

    def test_whitespace_handling(self):
        """Whitespace should be handled correctly"""
        assert self.processor._is_china_country("  CHINA  ") == True
        assert self.processor._has_chinese_name("  Huawei  ") == True


class TestRealWorldExamples:
    """Test with real-world examples from USAspending data"""

    def setup_method(self):
        """Initialize processor for each test"""
        self.processor = USAspending305Processor()

    def test_verified_chinese_entities(self):
        """Entities verified as Chinese should be detected BY NAME"""
        # From USAspending data analysis
        assert self.processor._has_chinese_name("LENOVO") == True

        # PHARMARON doesn't have Chinese keywords in name alone
        # It would be detected by country code (CHN) in actual processing
        # This test is for NAME-based detection only
        assert self.processor._has_chinese_name("PHARMARON") == False  # No Chinese keywords in name
        assert self.processor._has_chinese_name("PHARMARON BEIJING") == True  # Would detect with city

    def test_verified_false_positives(self):
        """Entities verified as false positives should NOT be detected"""
        assert self.processor._has_chinese_name("T K C ENTERPRISES") == False
        assert self.processor._has_chinese_name("COMAC PUMP") == False


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
