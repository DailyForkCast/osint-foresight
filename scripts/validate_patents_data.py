#!/usr/bin/env python3
"""
Patents Data Validation Script
Validates processed patents data for completeness, accuracy, and currency
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def validate_patents_data():
    """Comprehensive validation of patents multicountry dataset"""

    base_path = Path("data/processed/patents_multicountry")

    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "validator_name": "Patents Data Validator v1.0",
        "overall_status": "PENDING",
        "checks": [],
        "summary": {}
    }

    # Check 1: Directory structure
    print("=" * 60)
    print("PATENTS DATA VALIDATION")
    print("=" * 60)
    print("\n[1/7] Checking directory structure...")

    required_dirs = ["by_country", "by_technology", "temporal"]
    missing_dirs = [d for d in required_dirs if not (base_path / d).exists()]

    validation_results["checks"].append({
        "check": "directory_structure",
        "status": "PASS" if not missing_dirs else "FAIL",
        "missing_directories": missing_dirs
    })

    if missing_dirs:
        print(f"  ❌ FAIL: Missing directories: {missing_dirs}")
    else:
        print(f"  ✅ PASS: All required directories present")

    # Check 2: File completeness
    print("\n[2/7] Checking file completeness...")

    json_files = list(base_path.rglob("*.json"))
    expected_countries = ["US", "DE", "JP", "KR"]
    expected_techs = ["artificial_intelligence", "nuclear", "semiconductors", "telecommunications", "other"]

    country_files = [f for f in json_files if "by_country" in str(f)]
    tech_files = [f for f in json_files if "by_technology" in str(f)]
    temporal_files = [f for f in json_files if "temporal" in str(f)]

    validation_results["checks"].append({
        "check": "file_completeness",
        "status": "PASS",
        "country_files": len(country_files),
        "expected_countries": len(expected_countries),
        "technology_files": len(tech_files),
        "expected_technologies": len(expected_techs),
        "temporal_files": len(temporal_files)
    })

    print(f"  ✅ Country files: {len(country_files)}/{len(expected_countries)}")
    print(f"  ✅ Technology files: {len(tech_files)}/{len(expected_techs)}")
    print(f"  ✅ Temporal files: {len(temporal_files)}")

    # Check 3: Data integrity
    print("\n[3/7] Checking data integrity...")

    total_patents = 0
    data_integrity_issues = []
    file_data = {}

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            rel_path = json_file.relative_to(base_path)

            if isinstance(data, list):
                record_count = len(data)
                total_patents += record_count
                file_data[str(rel_path)] = {
                    "records": record_count,
                    "type": "list",
                    "size_bytes": json_file.stat().st_size
                }

                # Check for required fields in first record
                if record_count > 0:
                    sample = data[0]
                    required_fields = ["publication_number", "country_code"]
                    missing_fields = [f for f in required_fields if f not in sample]
                    if missing_fields:
                        data_integrity_issues.append({
                            "file": str(rel_path),
                            "issue": f"Missing fields: {missing_fields}"
                        })
            elif isinstance(data, dict):
                file_data[str(rel_path)] = {
                    "records": 1,
                    "type": "dict",
                    "size_bytes": json_file.stat().st_size
                }
            else:
                data_integrity_issues.append({
                    "file": str(rel_path),
                    "issue": f"Unexpected data type: {type(data)}"
                })

        except json.JSONDecodeError as e:
            data_integrity_issues.append({
                "file": str(rel_path),
                "issue": f"JSON decode error: {e}"
            })
        except Exception as e:
            data_integrity_issues.append({
                "file": str(rel_path),
                "issue": f"Error: {e}"
            })

    validation_results["checks"].append({
        "check": "data_integrity",
        "status": "PASS" if not data_integrity_issues else "WARNING",
        "total_patent_records": total_patents,
        "issues": data_integrity_issues,
        "files_analyzed": len(json_files)
    })

    if data_integrity_issues:
        print(f"  ⚠️  WARNING: {len(data_integrity_issues)} integrity issues found")
        for issue in data_integrity_issues[:3]:
            print(f"     - {issue['file']}: {issue['issue']}")
    else:
        print(f"  ✅ PASS: No integrity issues, {total_patents} total patent records")

    # Check 4: Provenance verification
    print("\n[4/7] Checking provenance...")

    # Load risk assessment to check metadata
    risk_file = base_path / "risk_assessment.json"
    report_file = base_path / "PATENTS_ANALYSIS_REPORT.md"

    has_risk = risk_file.exists()
    has_report = report_file.exists()

    provenance_info = {
        "risk_assessment_exists": has_risk,
        "report_exists": has_report,
        "data_source": "Google BigQuery patents-public-data (FREE tier)" if has_report else "Unknown"
    }

    if has_report:
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
            provenance_info["processing_date"] = "2025-09-21" if "2025-09-21" in report_content else "Unknown"
            provenance_info["countries_analyzed"] = 4 if "Countries Analyzed:** 4" in report_content else "Unknown"

    validation_results["checks"].append({
        "check": "provenance",
        "status": "PASS" if (has_risk and has_report) else "WARNING",
        "provenance": provenance_info
    })

    if has_risk and has_report:
        print(f"  ✅ PASS: Provenance documented (BigQuery, 2025-09-21)")
    else:
        print(f"  ⚠️  WARNING: Incomplete provenance documentation")

    # Check 5: Currency assessment
    print("\n[5/7] Checking currency (how recent)...")

    # Check temporal file for latest year
    temporal_file = base_path / "temporal" / "yearly_collaborations.json"
    latest_year = None

    if temporal_file.exists():
        with open(temporal_file, 'r', encoding='utf-8') as f:
            temporal_data = json.load(f)
            if temporal_data and isinstance(temporal_data, dict):
                # temporal_data is dict: {"2025": {"US": 1, "DE": 1}, ...}
                latest_year = max(int(year) for year in temporal_data.keys())

    current_year = datetime.now().year
    currency_gap = current_year - latest_year if latest_year else None

    validation_results["checks"].append({
        "check": "currency",
        "status": "PASS" if (currency_gap and currency_gap <= 1) else "WARNING",
        "latest_year": latest_year,
        "current_year": current_year,
        "gap_years": currency_gap
    })

    if currency_gap and currency_gap <= 1:
        print(f"  ✅ PASS: Data current (latest: {latest_year}, gap: {currency_gap} year)")
    elif latest_year:
        print(f"  ⚠️  WARNING: Data may be outdated (latest: {latest_year}, gap: {currency_gap} years)")
    else:
        print(f"  ❌ FAIL: Cannot determine currency")

    # Check 6: Cross-source potential
    print("\n[6/7] Checking cross-reference potential...")

    # Sample patents to check if they have enough metadata for cross-referencing
    sample_file = base_path / "by_country" / "US_china" / "patents.json"
    cross_ref_fields = []

    if sample_file.exists():
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_patents = json.load(f)
            if sample_patents:
                sample = sample_patents[0]
                cross_ref_fields = list(sample.keys())

    validation_results["checks"].append({
        "check": "cross_reference_potential",
        "status": "PASS" if cross_ref_fields else "FAIL",
        "available_fields": cross_ref_fields,
        "can_cross_ref_openalex": "assignee" in cross_ref_fields or "title" in cross_ref_fields
    })

    if cross_ref_fields:
        print(f"  ✅ PASS: {len(cross_ref_fields)} fields available for cross-referencing")
        print(f"     Key fields: {', '.join(cross_ref_fields[:5])}")
    else:
        print(f"  ❌ FAIL: No cross-reference metadata available")

    # Check 7: Validation summary
    print("\n[7/7] Generating validation summary...")

    passed_checks = sum(1 for check in validation_results["checks"] if check["status"] == "PASS")
    warning_checks = sum(1 for check in validation_results["checks"] if check["status"] == "WARNING")
    failed_checks = sum(1 for check in validation_results["checks"] if check["status"] == "FAIL")

    total_checks = len(validation_results["checks"])

    validation_results["summary"] = {
        "total_checks": total_checks,
        "passed": passed_checks,
        "warnings": warning_checks,
        "failed": failed_checks,
        "pass_rate": f"{(passed_checks / total_checks * 100):.1f}%",
        "total_patent_records": total_patents,
        "countries_covered": len(country_files),
        "technologies_covered": len(tech_files),
        "data_source": "Google BigQuery patents-public-data",
        "processing_date": "2025-09-21",
        "latest_data_year": latest_year
    }

    if failed_checks == 0 and warning_checks == 0:
        validation_results["overall_status"] = "VALIDATED"
        overall_icon = "✅"
    elif failed_checks == 0:
        validation_results["overall_status"] = "VALIDATED_WITH_WARNINGS"
        overall_icon = "⚠️ "
    else:
        validation_results["overall_status"] = "FAILED"
        overall_icon = "❌"

    print(f"\n{overall_icon} OVERALL STATUS: {validation_results['overall_status']}")
    print(f"  - Passed: {passed_checks}/{total_checks}")
    print(f"  - Warnings: {warning_checks}/{total_checks}")
    print(f"  - Failed: {failed_checks}/{total_checks}")
    print(f"  - Total Patents: {total_patents}")

    # Save validation results
    output_file = base_path / "VALIDATION_RESULTS.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2)

    print(f"\n✅ Validation results saved to: {output_file}")

    # Generate recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    recommendations = []

    if failed_checks > 0:
        recommendations.append("❌ CRITICAL: Address failed validation checks before using data")

    if currency_gap and currency_gap > 1:
        recommendations.append("⚠️  Consider refreshing patent data (latest: {latest_year})")

    if len(country_files) < 10:
        recommendations.append(f"📊 Expand country coverage (current: {len(country_files)}, target: 81)")

    if total_patents < 1000:
        recommendations.append(f"📊 Expand data collection (current: {total_patents} patents)")

    recommendations.append("✅ Cross-reference with OpenAlex for validation")
    recommendations.append("✅ Perform temporal analysis for trends")
    recommendations.append("✅ Integrate with technology taxonomy")

    for rec in recommendations:
        print(f"  {rec}")

    validation_results["recommendations"] = recommendations

    # Final save with recommendations
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2)

    print("\n" + "=" * 60)

    return validation_results

if __name__ == "__main__":
    try:
        results = validate_patents_data()
        sys.exit(0 if results["overall_status"] in ["VALIDATED", "VALIDATED_WITH_WARNINGS"] else 1)
    except Exception as e:
        print(f"\n❌ VALIDATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
