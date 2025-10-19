# Fix Implementation Plan

**Date**: 2025-10-18
**Issues**: 9 total (3 MEDIUM, 6 LOW)
**Estimated Time**: 3-4 hours
**Strategy**: Fix in order of impact and complexity

---

## Pre-Flight Checklist

Before starting fixes:
- [x] All issues documented in ISSUE_TRACKER.md
- [x] Red team validation baseline established
- [x] Current test results: 31/31 passing
- [x] Git status clean (recommend commit before fixes)

---

## Phase 1: Quick Wins (40 minutes)

### Fix 1: Add "P.R.C." Variants (10 min)
**Issue**: ISS-006
**File**: `scripts/process_usaspending_305_column.py`
**Change**:
```python
# Line ~24-30
CHINA_COUNTRIES = {
    'china', 'chinese', 'prc',
    'p.r.c.', 'p r c', 'p. r. c.',  # ADD THIS LINE
    'people\'s republic',
    # ... rest
}
```

**Test**:
```bash
python -c "from scripts.process_usaspending_305_column import USAspending305Processor; p = USAspending305Processor(); print('P.R.C.:', p._is_china_country('P.R.C.')); print('P R C:', p._is_china_country('P R C'))"
```

**Expected**: Both print True

---

### Fix 2: Add Misspelling Patterns (15 min)
**Issues**: ISS-004, ISS-005
**File**: `scripts/process_usaspending_305_column.py`
**Change**:
```python
# Line ~36-42
CHINESE_NAME_PATTERNS = {
    'beijing', 'shanghai', 'guangzhou', 'shenzhen',
    'china', 'chinese', 'sino',
    'huawei', 'hwawei', 'huawai', 'huwei',  # ADD MISSPELLINGS
    'zte', 'z t e',  # ADD SPACED VARIANT
    'alibaba', 'tencent', 'baidu', 'lenovo',
    'haier', 'xiaomi', 'byd', 'geely'
}
```

**Test**:
```bash
python -c "from scripts.process_usaspending_305_column import USAspending305Processor; p = USAspending305Processor(); print('Hwawei:', p._has_chinese_name('Hwawei')); print('Huawai:', p._has_chinese_name('Huawai'))"
```

**Expected**: Both print True

---

### Fix 3: Add Restaurant/Location False Positives (15 min)
**Issues**: ISS-007, ISS-008, ISS-009
**File**: `scripts/process_usaspending_305_column.py`
**Change**:
```python
# Line ~44-75 (in FALSE_POSITIVES set)
FALSE_POSITIVES = {
    # ... existing ...

    # ADD THESE:
    # Geographic locations
    'china beach',
    'china cove',

    # Restaurant chains
    'china king',
    'china king restaurant',
    'great wall chinese restaurant',
    'great wall restaurant',
    'chinese restaurant',
    'chinese food',
}
```

**Test**:
```bash
python -c "from scripts.process_usaspending_305_column import USAspending305Processor; p = USAspending305Processor(); print('China Beach:', p._has_chinese_name('China Beach')); print('China King:', p._has_chinese_name('China King Restaurant')); print('Great Wall:', p._has_chinese_name('Great Wall Chinese Restaurant'))"
```

**Expected**: All print False

---

### Phase 1 Validation
```bash
# Run unit tests
pytest tests/unit/test_chinese_detection.py -v

# Run red team (should show improvement)
python tests/RED_TEAM_VALIDATION.py

# Expected results:
# - Bypasses: 3 → 1 (only "H u a w e i" remains)
# - False positives: 3 → 0
```

---

## Phase 2: Medium Complexity (1.5 hours)

### Fix 4: Spaced Name Bypass (1 hour)
**Issue**: ISS-002
**File**: `scripts/process_usaspending_305_column.py`
**Change**: Replace entire `_has_chinese_name` function

**Old function** (line ~297-326):
```python
def _has_chinese_name(self, name: str) -> bool:
    """Check if name suggests Chinese entity with proper word boundaries."""
    if not name:
        return False
    name_lower = name.lower()

    # ... existing logic ...
```

**New function**:
```python
def _has_chinese_name(self, name: str) -> bool:
    """Check if name suggests Chinese entity with proper word boundaries.

    Includes normalization to catch spaced obfuscation (e.g., "H u a w e i").
    """
    if not name:
        return False

    name_lower = name.lower()

    # CRITICAL FIX: Exclude Taiwan's official name
    if 'republic of china' in name_lower and 'taiwan' in name_lower:
        return False

    if 'taiwan' in name_lower:
        return False

    # Check for false positives first
    for false_positive in self.FALSE_POSITIVES:
        if false_positive in name_lower:
            return False

    # NEW: Create normalized version (remove spaces for pattern matching)
    name_normalized = re.sub(r'\s+', '', name_lower)

    # Check Chinese name patterns
    for pattern in self.CHINESE_NAME_PATTERNS:
        # Try exact match with word boundaries first
        word_pattern = r'\b' + re.escape(pattern) + r'\b'
        if re.search(word_pattern, name_lower):
            return True

        # NEW: Try normalized match (catches "H u a w e i" as "huawei")
        pattern_normalized = re.sub(r'\s+', '', pattern)
        if len(pattern_normalized) >= 5:  # Only for substantial patterns
            if pattern_normalized in name_normalized:
                return True

    return False
```

**Test**:
```bash
python -c "from scripts.process_usaspending_305_column import USAspending305Processor; p = USAspending305Processor(); print('H u a w e i:', p._has_chinese_name('H u a w e i')); print('Z T E:', p._has_chinese_name('Z T E')); print('Huawei:', p._has_chinese_name('Huawei'))"
```

**Expected**: All print True

---

### Fix 5: Inventory Tool (30 min)
**Issue**: ISS-001
**File**: `scripts/utils/create_script_inventory.py`
**Change**: Replace `scan_scripts` function

**Old function** (line ~29-53):
```python
def scan_scripts(self):
    """Scan all Python files in the project"""
    print("Scanning for Python scripts...")

    # Scan root directory
    for script in self.project_root.glob("*.py"):
        self.analyze_script(script, location="root")

    # Scan scripts/ directory
    scripts_dir = self.project_root / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.rglob("*.py"):
            # ...
```

**New function**:
```python
def scan_scripts(self):
    """Scan ALL Python files in the project (entire tree)"""
    print("Scanning entire project for Python scripts...")

    # Scan entire project recursively
    for script in self.project_root.rglob("*.py"):
        # Skip __pycache__, virtual environments, and .git
        script_str = str(script)
        if any(skip in script_str for skip in ['__pycache__', '.venv', 'venv', '.git']):
            continue

        # Determine location relative to project root
        try:
            rel_path = script.relative_to(self.project_root)
            if rel_path.parent == Path('.'):
                location = "root"
            else:
                # Use first directory as location category
                parts = rel_path.parts
                location = str(parts[0]) if len(parts) > 1 else "root"
        except ValueError:
            location = "external"

        self.analyze_script(script, location=location)

    print(f"Found {len(self.scripts)} scripts")
```

**Test**:
```bash
python scripts/utils/create_script_inventory.py

# Check count in output
# Expected: ~1,300 scripts (not 902)
```

---

### Phase 2 Validation
```bash
# Run full test suite
pytest tests/ -v

# Run red team
python tests/RED_TEAM_VALIDATION.py

# Expected results:
# - Bypasses: 0
# - False positives: 0
# - Unit tests: All passing
# - Inventory: 1,300+ scripts
```

---

## Phase 3: Integration Tests (1-2 hours)

### Fix 6: Add Integration Tests
**Issue**: ISS-003
**New File**: `tests/integration/test_detection_pipeline.py`

**Create file with**:
```python
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
        """CHN country code should give 0.9 confidence"""
        fields = self._create_fields(recipient_country_code='CHN')
        result = self.processor._detect_china_connection(fields)

        assert result is not None
        assert result['confidence'] == 0.9
        assert 'pop_country_china' in result['detection_types'] or \
               'recipient_country_china' in result['detection_types']

    def test_name_only_gives_medium_confidence(self):
        """Name match only should give 0.6 confidence"""
        fields = self._create_fields(recipient_name='Huawei Technologies Co Ltd')
        result = self.processor._detect_china_connection(fields)

        assert result is not None
        assert result['confidence'] == 0.6
        assert 'chinese_name_recipient' in result['detection_types']

    def test_product_sourcing_gives_low_confidence(self):
        """Product sourcing should give 0.3 confidence"""
        fields = self._create_fields(award_description='Equipment made in China')
        result = self.processor._detect_china_connection(fields)

        assert result is not None
        assert result['confidence'] == 0.3
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
        # Hong Kong detection logic (check actual implementation)

    def test_taiwan_excluded(self):
        """Taiwan should NOT be detected as China"""
        fields = self._create_fields(
            recipient_name='Taiwan Semiconductor Manufacturing',
            recipient_country_code='TWN'
        )
        result = self.processor._detect_china_connection(fields)

        assert result is None  # Should NOT detect Taiwan as China


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Create directory**:
```bash
mkdir -p tests/integration
touch tests/integration/__init__.py
```

**Test**:
```bash
pytest tests/integration/test_detection_pipeline.py -v
```

**Expected**: All tests pass

---

## Post-Fix Validation

### Complete Test Suite
```bash
# Run everything
pytest tests/ -v --tb=short

# Should see:
# - tests/unit/test_chinese_detection.py: 31+ tests passing
# - tests/integration/test_detection_pipeline.py: 6 tests passing
# Total: 37+ tests
```

### Red Team Re-validation
```bash
python tests/RED_TEAM_VALIDATION.py

# Expected final results:
# ================================================================================
# Bypass attempts found: 0
# False positives found: 0
# ================================================================================
# PASS: No critical issues found in red team testing
# ================================================================================
```

### Inventory Verification
```bash
python scripts/utils/create_script_inventory.py

# Check output:
# Total Scripts: ~1,300 (not 902)
```

---

## Success Criteria

All of the following must be true:
- [ ] All 9 issues marked as Fixed
- [ ] Unit tests: 31+ passing
- [ ] Integration tests: 6+ passing
- [ ] Red team bypasses: 0
- [ ] Red team false positives: 0
- [ ] Inventory count: 1,300+ scripts
- [ ] No new test failures introduced

---

## Rollback Plan

If fixes cause problems:
```bash
# Git rollback
git checkout -- scripts/process_usaspending_305_column.py
git checkout -- scripts/utils/create_script_inventory.py

# Re-run tests to confirm rollback
pytest tests/unit/ -v
```

---

## Time Tracking

| Phase | Estimated | Actual | Status |
|-------|-----------|--------|--------|
| Phase 1 | 40 min | - | Pending |
| Phase 2 | 1.5 hours | - | Pending |
| Phase 3 | 1-2 hours | - | Pending |
| **Total** | **3-4 hours** | **-** | **Pending** |

---

**Ready to Begin**: Yes
**Next Step**: Start Phase 1, Fix 1 (P.R.C. variants)
