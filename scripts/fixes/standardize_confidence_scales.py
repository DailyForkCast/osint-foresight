#!/usr/bin/env python3
"""
Confidence Scale Standardization Script
Converts all 0-20 confidence scores to 0-1 scale with uncertainty bands
Priority 1 Implementation - Week 1
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfidenceStandardizer:
    """Standardize all confidence scales across the project"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.conversion_log = []

        # Mapping for old to new scale
        self.scale_mapping = {
            # 0-20 scale to 0-1 scale with uncertainty
            "0-20": {
                "converter": lambda x: (x / 20.0, 0.05 if x < 10 else 0.10),  # Returns (confidence, uncertainty)
                "categories": {
                    (0, 7): "Low",
                    (8, 14): "Medium",
                    (15, 20): "High"
                }
            },
            # Already 0-1 scale - just add uncertainty
            "0-1": {
                "converter": lambda x: (x, 0.05 if x < 0.5 else 0.10),
                "categories": {
                    (0.0, 0.35): "Low",
                    (0.35, 0.70): "Medium",
                    (0.70, 1.0): "High"
                }
            }
        }

    def convert_confidence_value(self, value: Any, scale_type: str = "0-20") -> Dict[str, Any]:
        """
        Convert a confidence value to standardized format

        Returns:
            {
                "confidence": 0.75,
                "uncertainty": 0.10,
                "category": "High",
                "original_value": 15,
                "original_scale": "0-20"
            }
        """
        try:
            if isinstance(value, str):
                # Try to extract numeric value
                value = float(''.join(c for c in value if c.isdigit() or c == '.'))

            converter = self.scale_mapping[scale_type]["converter"]
            confidence, uncertainty = converter(float(value))

            # Determine category
            category = "Unknown"
            for range_tuple, cat in self.scale_mapping[scale_type]["categories"].items():
                if scale_type == "0-20":
                    if range_tuple[0] <= value <= range_tuple[1]:
                        category = cat
                        break
                else:
                    if range_tuple[0] <= confidence <= range_tuple[1]:
                        category = cat
                        break

            return {
                "confidence": round(confidence, 3),
                "uncertainty": round(uncertainty, 3),
                "confidence_range": [
                    round(max(0, confidence - uncertainty), 3),
                    round(min(1, confidence + uncertainty), 3)
                ],
                "category": category,
                "original_value": value,
                "original_scale": scale_type
            }
        except Exception as e:
            logger.warning(f"Could not convert value {value}: {e}")
            return {
                "confidence": 0.5,
                "uncertainty": 0.25,
                "category": "Unknown",
                "original_value": value,
                "error": str(e)
            }

    def process_json_file(self, file_path: Path) -> bool:
        """Process a single JSON file to standardize confidence scores"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            modified = False
            data = self.process_nested_dict(data, file_path)

            # Check if modifications were made
            if self.conversion_log and self.conversion_log[-1]['file'] == str(file_path):
                modified = True

            if modified:
                # Backup original
                backup_path = file_path.with_suffix('.json.bak')
                file_path.rename(backup_path)

                # Write updated data
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.info(f"Updated {file_path}")
                return True

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

        return False

    def process_nested_dict(self, obj: Any, file_path: Path, path: str = "") -> Any:
        """Recursively process nested dictionaries to find and convert confidence values"""

        if isinstance(obj, dict):
            # Check for confidence-related keys
            confidence_keys = [
                'confidence', 'confidence_score', 'confidence_level',
                'numeric_confidence', 'assessment_confidence'
            ]

            for key in confidence_keys:
                if key in obj and isinstance(obj[key], (int, float, str)):
                    # Detect scale type
                    value = obj[key]
                    if isinstance(value, str):
                        try:
                            value = float(''.join(c for c in value if c.isdigit() or c == '.'))
                        except:
                            continue

                    scale_type = "0-20" if value > 1 else "0-1"

                    # Convert value
                    converted = self.convert_confidence_value(value, scale_type)

                    # Update object with new structure
                    obj[key] = converted["confidence"]
                    obj[f"{key}_uncertainty"] = converted["uncertainty"]
                    obj[f"{key}_range"] = converted["confidence_range"]
                    obj[f"{key}_category"] = converted["category"]

                    # Log conversion
                    self.conversion_log.append({
                        "file": str(file_path),
                        "path": f"{path}/{key}",
                        "original": value,
                        "converted": converted
                    })

            # Recurse into nested objects
            for key, value in obj.items():
                obj[key] = self.process_nested_dict(value, file_path, f"{path}/{key}")

        elif isinstance(obj, list):
            # Process each item in list
            return [self.process_nested_dict(item, file_path, f"{path}[{i}]")
                    for i, item in enumerate(obj)]

        return obj

    def standardize_project(self) -> Dict[str, Any]:
        """Standardize all confidence scales across the project"""

        results = {
            "files_processed": 0,
            "files_modified": 0,
            "conversions": 0,
            "errors": []
        }

        # Target directories
        target_dirs = [
            "artifacts",
            "data/processed",
            "src/analysis",
            "scripts/analysis"
        ]

        for dir_name in target_dirs:
            dir_path = self.base_path / dir_name
            if not dir_path.exists():
                continue

            # Process all JSON files
            for json_file in dir_path.rglob("*.json"):
                results["files_processed"] += 1
                if self.process_json_file(json_file):
                    results["files_modified"] += 1

        results["conversions"] = len(self.conversion_log)

        # Save conversion log
        log_path = self.base_path / "confidence_standardization_log.json"
        from datetime import datetime
        with open(log_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "conversions": self.conversion_log
            }, f, indent=2)

        return results

    def update_python_files(self) -> int:
        """Update Python files to use new confidence scale"""

        replacements = [
            # Old pattern -> New pattern
            ("confidence_threshold: 0.75  # Standardized 0-1 scale", "confidence_threshold: 0.75  # Standardized 0-1 scale  # Standardized 0-1 scale"),
            ("confidence_score = ", "confidence_score = "),  # Remove division by 20
            ("range(0, 21)", "np.linspace(0, 1, 21)"),  # Update ranges
            ("confidence < 0.5", "confidence < 0.5"),
            ("confidence > 0.75", "confidence > 0.75"),
            ('confidence_0_1_with_uncertainty', 'confidence_0_1_with_uncertainty'),
        ]

        files_updated = 0

        for py_file in self.base_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_content = content

                for old, new in replacements:
                    import re
                    content = re.sub(old, new, content)

                if content != original_content:
                    # Backup and update
                    backup_path = py_file.with_suffix('.py.bak')
                    py_file.rename(backup_path)

                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)

                    files_updated += 1
                    logger.info(f"Updated Python file: {py_file}")

            except Exception as e:
                logger.error(f"Error updating {py_file}: {e}")

        return files_updated

def main():
    """Main execution function"""
    print("="*70)
    print("CONFIDENCE SCALE STANDARDIZATION")
    print("Converting all confidence scores to 0-1 scale with uncertainty")
    print("="*70)

    standardizer = ConfidenceStandardizer()

    # Phase 1: Convert JSON artifacts
    print("\nPhase 1: Converting JSON artifacts...")
    results = standardizer.standardize_project()

    print(f"Files processed: {results['files_processed']}")
    print(f"Files modified: {results['files_modified']}")
    print(f"Total conversions: {results['conversions']}")

    # Phase 2: Update Python files
    print("\nPhase 2: Updating Python files...")
    py_updated = standardizer.update_python_files()
    print(f"Python files updated: {py_updated}")

    # Phase 3: Create new validation module
    print("\nPhase 3: Creating standardized confidence module...")

    module_content = '''"""
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
'''

    module_path = Path("src/utils/standardized_confidence.py")
    module_path.parent.mkdir(parents=True, exist_ok=True)

    with open(module_path, 'w') as f:
        f.write(module_content)

    print(f"Created standardized confidence module: {module_path}")

    print("\n" + "="*70)
    print("STANDARDIZATION COMPLETE")
    print(f"Log saved to: confidence_standardization_log.json")
    print("="*70)

if __name__ == "__main__":
    main()
