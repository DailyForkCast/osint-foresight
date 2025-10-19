#!/usr/bin/env python3
"""
Integration Tests for Detection Pipeline

Tests full _detect_china_connection() method including confidence scoring.

Last Updated: 2025-10-18
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts"))

from process_usaspending_305_column import USAspending305Processor


class TestConfidenceScoring:
    """Test confidence scoring in full detection pipeline"""

    def setup_method(self):
        self.processor = USAspending305Processor()

    def _create_fields(self, **kwargs):
        """Helper to create 305-column field array"""
        fields = [''] * 305
        for key, value in kwargs.items():
            if key == 'recipient_country_code':
                fields[107] = value
            elif key == 'recipient_country_name':
                fields[108] = value
            elif key == 'recipient_name':
                fields[200] = value
            elif key == 'vendor_name':
                fields[13] = value
            elif key == 'award_description':
                fields[10] = value
            elif key == 'pop_country_code':
                fields[50] = value
            elif key == 'pop_country_name':
                fields[49] = value
        return fields

    def test_country_code_gives_high_confidence(self):
        """CHN country code should give 0.95 confidence"""
        fields = self._create_fields(recipient_country_code='CHN')
        result = self.processor._detect_china_connection(fields)

        assert result is not None
        assert result['highest_confidence'] == 0.95
        detection_types = result['detection_types']
        assert 'pop_country_china' in detection_types or \
               'recipient_country_china' in detection_types

    def test_name_only_gives_medium_confidence(self):
        """Name match only should give 0.70 confidence"""
        fields = self._create_fields(recipient_name='Huawei Technologies Co Ltd')
        result = self.processor._detect_china_connection(fields)

        assert result is not None
        assert result['highest_confidence'] == 0.70
        assert 'chinese_name_recipient' in result['detection_types']

    def test_product_sourcing_gives_low_confidence(self):
        """Product sourcing should give 0.30 confidence (needs country + description)"""
        fields = self._create_fields(
            recipient_country_code='CHN',
            award_description='Equipment made in China'
        )
        result = self.processor._detect_china_connection(fields)

        assert result is not None
        assert result['highest_confidence'] == 0.30
        assert 'china_sourced_product' in result['detection_types']

    def test_no_detection_returns_none(self):
        """No indicators should return None"""
        fields = self._create_fields(
            recipient_name='Boeing Corporation',
            recipient_country_code='USA'
        )
        result = self.processor._detect_china_connection(fields)

        assert result is None

    def test_hong_kong_detected_separately(self):
        """Hong Kong should be detected but marked as HKG"""
        fields = self._create_fields(recipient_country_code='HKG')
        result = self.processor._detect_china_connection(fields)

        assert result is not None
        # Hong Kong should have high confidence (0.85 for recipient)
        assert result['highest_confidence'] == 0.85
        assert 'hong_kong' in result['detection_types']

    def test_taiwan_excluded(self):
        """Taiwan should NOT be detected as China"""
        fields = self._create_fields(
            recipient_name='Taiwan Semiconductor Manufacturing',
            recipient_country_code='TWN'
        )
        result = self.processor._detect_china_connection(fields)

        assert result is None  # Should NOT detect Taiwan as China

    def test_spaced_name_detection(self):
        """Spaced names like 'H u a w e i' should be detected"""
        fields = self._create_fields(recipient_name='H u a w e i Technologies')
        result = self.processor._detect_china_connection(fields)

        assert result is not None
        assert result['highest_confidence'] == 0.70  # Name-based detection
        assert 'chinese_name_recipient' in result['detection_types']

    def test_false_positives_excluded(self):
        """Restaurant and location names should NOT be detected"""
        test_cases = [
            'China Beach',
            'China King Restaurant',
            'Great Wall Chinese Restaurant',
        ]

        for name in test_cases:
            fields = self._create_fields(recipient_name=name)
            result = self.processor._detect_china_connection(fields)
            assert result is None, f"'{name}' should not be detected as Chinese entity"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
