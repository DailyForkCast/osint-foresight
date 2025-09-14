#!/usr/bin/env python3
"""
Test suite for OSINT Foresight improvements.
Run this to verify all new components are working correctly.
"""

import sys
import json
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_schemas():
    """Test that all schemas are valid JSON."""
    print("Testing schemas...")
    try:
        with open('config/artifact_schemas.json') as f:
            schemas = json.load(f)
        print(f"  [OK] Loaded {len(schemas['schemas'])} schema definitions")
        return True
    except Exception as e:
        print(f"  [FAIL] Schema test failed: {e}")
        return False

def test_rate_limiter():
    """Test rate limiter functionality."""
    print("Testing rate limiter...")
    try:
        from src.utils.rate_limiter import RateLimiter, RateLimitConfig

        config = RateLimitConfig(calls_per_second=10)
        limiter = RateLimiter(config)

        async def test():
            for i in range(5):
                await limiter.acquire()
            return True

        result = asyncio.run(test())
        print("  [OK] Rate limiter working")
        return result
    except Exception as e:
        print(f"  [FAIL] Rate limiter test failed: {e}")
        return False

def test_standardization():
    """Test standardization utilities."""
    print("Testing standardization...")
    try:
        from src.utils.standardization import (
            standardize_date,
            standardize_confidence,
            standardize_org_id
        )

        # Test date
        date = standardize_date("2024-03-15")
        assert date == "2024-03-15"

        # Test confidence
        conf = standardize_confidence("High")
        assert 0.7 <= conf['score'] <= 1.0
        assert conf['label'] == "High"

        # Test ID
        org_id = standardize_org_id("02j61yw88", "ROR")
        assert org_id == "ROR:02j61yw88"

        print("  [OK] Standardization working")
        return True
    except Exception as e:
        print(f"  [FAIL] Standardization test failed: {e}")
        return False

def test_regional_adapter():
    """Test regional adapter functionality."""
    print("Testing regional adapter...")
    try:
        from src.utils.regional_adapter import RegionalAdapter

        adapter = RegionalAdapter()

        # Test source selection
        sources = adapter.get_data_sources("SK", "procurement")
        assert len(sources) > 0

        # Test terminology standardization
        text = "Horizon Europe project"
        neutral = adapter.standardize_terminology(text)
        assert "Horizon Europe" not in neutral or neutral != text

        print(f"  [OK] Regional adapter working ({len(sources)} sources found)")
        return True
    except Exception as e:
        print(f"  [FAIL] Regional adapter test failed: {e}")
        return False

def test_api_config():
    """Test API configuration loading."""
    print("Testing API configuration...")
    try:
        import yaml

        with open('config/api_specifications.yaml') as f:
            config = yaml.safe_load(f)

        apis = config.get('apis', {})
        print(f"  [OK] Loaded {len(apis)} API configurations")
        return True
    except Exception as e:
        print(f"  [FAIL] API config test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("OSINT Foresight Improvement Test Suite")
    print("="*50 + "\n")

    tests = [
        test_schemas,
        test_api_config,
        test_rate_limiter,
        test_standardization,
        test_regional_adapter
    ]

    results = []
    for test in tests:
        results.append(test())
        print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("="*50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] All tests passed!")
        return 0
    else:
        print("[ERROR] Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
