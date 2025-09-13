# src/analysis/health_check.py
"""
Health check for country data completeness and freshness.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import os

def check_file(path: Path, max_age_days: int = 30) -> dict:
    """Check if file exists and its age."""
    result = {
        "path": str(path),
        "exists": path.exists(),
        "size": 0,
        "age_days": None,
        "status": "missing"
    }
    
    if path.exists():
        stat = path.stat()
        result["size"] = stat.st_size
        age = datetime.now() - datetime.fromtimestamp(stat.st_mtime)
        result["age_days"] = age.days
        
        if result["size"] == 0:
            result["status"] = "empty"
        elif age.days > max_age_days:
            result["status"] = "stale"
        else:
            result["status"] = "ok"
    
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, help="Country ISO code")
    ap.add_argument("--max-age", type=int, default=30, help="Max age in days before considering stale")
    args = ap.parse_args()
    
    country = args.country.upper()
    base = Path("data/processed") / f"country={country}"
    reports = Path("reports") / f"country={country}"
    outputs = Path("outputs") / f"country={country}"
    
    # Files to check
    files_to_check = [
        # Processed data
        base / "relationships.csv",
        base / "signals.csv", 
        base / "standards_roles.tsv",
        base / "institutions.csv",
        base / "mechanism_incidents.tsv",
        base / "programs.csv",
        base / "sanctions_hits.csv",
        base / "cer_master.csv",
        # Reports
        reports / "phase-0_taxonomy.md",
        reports / "phase-1_setup.md",
        reports / "phase-2_indicators.md",
        reports / "phase-3_landscape.md",
        reports / "phase-4_supply_chain.md",
        reports / "phase-5_institutions.md",
        reports / "phase-6_funders.md",
        reports / "phase-7_links.md",
        reports / "phase-8_risk.md",
        reports / "phase-9_posture.md",
        reports / "phase-10_redteam.md",
        reports / "phase-11_foresight.md",
        # Outputs
        outputs / "phase-3" / "sector_maturity.tsv",
        outputs / "phase-3" / "top_institutions.tsv",
    ]
    
    print(f"\nHEALTH CHECK: {country}")
    print("=" * 60)
    
    ok_count = 0
    missing_count = 0
    stale_count = 0
    empty_count = 0
    
    for file in files_to_check:
        result = check_file(file, args.max_age)
        
        status_symbol = {
            "ok": "[OK]",
            "missing": "[MISSING]",
            "stale": "[STALE]",
            "empty": "[EMPTY]"
        }.get(result["status"], "[?]")
        
        rel_path = str(file).replace(str(Path.cwd()) + os.sep, "")
        
        if result["exists"]:
            age_str = f"{result['age_days']}d old" if result["age_days"] is not None else ""
            size_str = f"{result['size']} bytes"
            print(f"{status_symbol} {rel_path:60} {size_str:>12} {age_str:>10}")
        else:
            print(f"{status_symbol} {rel_path:60} {'missing':>12}")
        
        if result["status"] == "ok":
            ok_count += 1
        elif result["status"] == "missing":
            missing_count += 1
        elif result["status"] == "stale":
            stale_count += 1
        elif result["status"] == "empty":
            empty_count += 1
    
    print("\n" + "=" * 60)
    print(f"Summary: {ok_count} OK, {missing_count} missing, {empty_count} empty, {stale_count} stale")
    
    if missing_count > 0:
        print(f"\n[WARNING] {missing_count} files are missing. Run data collection or create placeholders.")
    if stale_count > 0:
        print(f"\n[WARNING] {stale_count} files are older than {args.max_age} days. Consider refreshing.")
    
    return 0 if (missing_count == 0 and empty_count == 0) else 1

if __name__ == "__main__":
    raise SystemExit(main())