#!/usr/bin/env python3
"""
Process TED historical data for 2006-2009 period
This captures the pre-financial crisis baseline and early China engagement
"""

import sys
import logging
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from process_ted_procurement_multicountry import MultiCountryTEDProcessor

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ted_historical_2006_2009_processing.log'),
            logging.StreamHandler()
        ]
    )

    # Create processor for 2006-2009 data
    processor = MultiCountryTEDProcessor(
        data_dir="F:/TED_Data",
        output_dir="data/processed/ted_historical_2006_2009"
    )

    # Process early historical periods
    periods = {
        "pre_crisis_2006_2007": {
            "years": ["2006", "2007"],
            "description": "Pre-financial crisis baseline",
            "context": "Normal trade relations, minimal China presence expected"
        },
        "financial_crisis_2008_2009": {
            "years": ["2008", "2009"],
            "description": "Global financial crisis period",
            "context": "Economic disruption, potential China opportunity seeking"
        }
    }

    logging.info("Starting TED Historical 2006-2009 Processing...")
    logging.info("Capturing pre-crisis baseline and financial crisis periods")

    monthly_dir = Path("F:/TED_Data/monthly")

    for period_name, period_info in periods.items():
        logging.info(f"\n{'='*50}")
        logging.info(f"PROCESSING PERIOD: {period_name}")
        logging.info(f"Description: {period_info['description']}")
        logging.info(f"Context: {period_info['context']}")
        logging.info(f"Years: {', '.join(period_info['years'])}")
        logging.info(f"{'='*50}")

        period_archives = []
        for year in period_info["years"]:
            year_dir = monthly_dir / year
            if year_dir.exists():
                for archive in sorted(year_dir.glob("TED_monthly_*.tar.gz")):
                    period_archives.append(archive)
                logging.info(f"Found archives for {year}")
            else:
                logging.warning(f"No data directory found for {year} at {year_dir}")

        logging.info(f"Found {len(period_archives)} archives for {period_name}")

        if not period_archives:
            logging.warning(f"No archives found for {period_name}, skipping...")
            continue

        # Process period archives
        period_findings = 0
        for i, archive_path in enumerate(period_archives):
            logging.info(f"[{period_name}] Processing {i+1}/{len(period_archives)}: {archive_path.name}")

            try:
                results = processor.process_archive(archive_path)

                # Save checkpoint
                processor.checkpoint["processed_files"].append(str(archive_path))
                processor.checkpoint["last_file"] = str(archive_path)

                # Collect findings
                archive_findings = 0
                for country, findings in results["findings_by_country"].items():
                    if findings:  # Check if findings is not empty
                        processor.checkpoint["country_findings"][country].extend(
                            [f.__dict__ if hasattr(f, '__dict__') else f for f in findings]
                        )
                        archive_findings += len(findings)

                period_findings += archive_findings
                processor.save_checkpoint()

                logging.info(f"  --> Completed: {archive_findings} China-related contracts found")

            except Exception as e:
                logging.error(f"Error processing {archive_path}: {e}")
                continue

        logging.info(f"Period {period_name} complete: {period_findings} total findings")

    # Generate outputs
    logging.info("\nGenerating 2006-2009 analysis outputs...")
    processor.save_findings_by_country()
    processor.save_findings_by_company()
    processor.save_findings_by_sector()

    # Generate early period analysis
    generate_early_period_analysis(processor)

    logging.info("TED Historical 2006-2009 Processing Complete!")
    logging.info(f"Results saved to: data/processed/ted_historical_2006_2009")

def generate_early_period_analysis(processor):
    """Generate analysis specific to 2006-2009 period"""
    import json
    from collections import defaultdict

    analysis = {
        "period": "2006-2009",
        "description": "Pre-financial crisis and crisis period analysis",
        "findings": {
            "pre_crisis_2006_2007": {
                "description": "Baseline before global financial crisis",
                "expected": "Minimal Chinese presence in EU procurement",
                "contracts": 0,
                "entities": [],
                "countries_affected": []
            },
            "financial_crisis_2008_2009": {
                "description": "Global financial crisis period",
                "expected": "Potential increase as China seeks opportunities",
                "contracts": 0,
                "entities": [],
                "countries_affected": []
            }
        },
        "insights": [],
        "strategic_implications": []
    }

    # Analyze findings by period
    for country, findings_dicts in processor.checkpoint["country_findings"].items():
        for finding in findings_dicts:
            year = finding.get("date", "")[:4] if finding.get("date") else ""
            entity = finding.get("chinese_entity", "")

            if year in ["2006", "2007"]:
                analysis["findings"]["pre_crisis_2006_2007"]["contracts"] += 1
                if entity and entity not in analysis["findings"]["pre_crisis_2006_2007"]["entities"]:
                    analysis["findings"]["pre_crisis_2006_2007"]["entities"].append(entity)
                if country not in analysis["findings"]["pre_crisis_2006_2007"]["countries_affected"]:
                    analysis["findings"]["pre_crisis_2006_2007"]["countries_affected"].append(country)

            elif year in ["2008", "2009"]:
                analysis["findings"]["financial_crisis_2008_2009"]["contracts"] += 1
                if entity and entity not in analysis["findings"]["financial_crisis_2008_2009"]["entities"]:
                    analysis["findings"]["financial_crisis_2008_2009"]["entities"].append(entity)
                if country not in analysis["findings"]["financial_crisis_2008_2009"]["countries_affected"]:
                    analysis["findings"]["financial_crisis_2008_2009"]["countries_affected"].append(country)

    # Generate insights
    if analysis["findings"]["pre_crisis_2006_2007"]["contracts"] == 0:
        analysis["insights"].append("No Chinese presence detected in EU procurement 2006-2007 (expected baseline)")
    else:
        analysis["insights"].append(f"Early Chinese presence detected: {analysis['findings']['pre_crisis_2006_2007']['contracts']} contracts in 2006-2007")

    if analysis["findings"]["financial_crisis_2008_2009"]["contracts"] > analysis["findings"]["pre_crisis_2006_2007"]["contracts"]:
        analysis["insights"].append("Chinese procurement increased during financial crisis (opportunistic behavior)")

    # Strategic implications
    analysis["strategic_implications"] = [
        "Baseline establishes when China first entered EU procurement market",
        "Financial crisis period shows whether China exploited economic vulnerability",
        "Pre-BRI data crucial for understanding strategic evolution"
    ]

    # Save analysis
    analysis_dir = Path("data/processed/ted_historical_2006_2009/analysis")
    analysis_dir.mkdir(exist_ok=True, parents=True)

    with open(analysis_dir / "early_period_analysis_2006_2009.json", 'w') as f:
        json.dump(analysis, f, indent=2)

    # Generate markdown report
    report = f"""# TED Early Historical Analysis: 2006-2009

## Period Overview
- **Pre-Crisis (2006-2007):** {analysis['findings']['pre_crisis_2006_2007']['contracts']} contracts found
- **Financial Crisis (2008-2009):** {analysis['findings']['financial_crisis_2008_2009']['contracts']} contracts found

## Key Findings

### Pre-Crisis Baseline (2006-2007)
- **Contracts:** {analysis['findings']['pre_crisis_2006_2007']['contracts']}
- **Chinese Entities:** {', '.join(analysis['findings']['pre_crisis_2006_2007']['entities']) or 'None detected'}
- **Countries Affected:** {', '.join(analysis['findings']['pre_crisis_2006_2007']['countries_affected']) or 'None'}

### Financial Crisis Period (2008-2009)
- **Contracts:** {analysis['findings']['financial_crisis_2008_2009']['contracts']}
- **Chinese Entities:** {', '.join(analysis['findings']['financial_crisis_2008_2009']['entities']) or 'None detected'}
- **Countries Affected:** {', '.join(analysis['findings']['financial_crisis_2008_2009']['countries_affected']) or 'None'}

## Strategic Insights
{chr(10).join(f"- {insight}" for insight in analysis['insights'])}

## Implications
{chr(10).join(f"- {impl}" for impl in analysis['strategic_implications'])}

---
*Analysis complete. This baseline data is crucial for understanding China's strategic evolution in EU procurement.*
"""

    with open(analysis_dir / "EARLY_PERIOD_REPORT_2006_2009.md", 'w') as f:
        f.write(report)

    logging.info("Early period analysis saved to analysis/early_period_analysis_2006_2009.json")
    logging.info("Report saved to analysis/EARLY_PERIOD_REPORT_2006_2009.md")

if __name__ == "__main__":
    main()
