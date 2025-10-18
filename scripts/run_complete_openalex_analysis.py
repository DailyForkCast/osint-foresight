"""
Complete OpenAlex Multi-Country Analysis Runner
Executes the full analysis pipeline from data processing to intelligence reporting
"""

import os
import sys
import subprocess
import logging
import argparse
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_command(command, description):
    """Run a command and handle errors"""
    logging.info(f"Starting: {description}")
    logging.info(f"Command: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        if result.returncode == 0:
            logging.info(f"✅ Success: {description}")
            if result.stdout:
                logging.info(f"Output: {result.stdout[:500]}...")
            return True
        else:
            logging.error(f"❌ Failed: {description}")
            logging.error(f"Error: {result.stderr}")
            return False

    except Exception as e:
        logging.error(f"❌ Exception in {description}: {e}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    logging.info("Checking prerequisites...")

    # Check OpenAlex data availability
    data_path = Path("F:/OSINT_Backups/openalex/data/works")
    if not data_path.exists():
        logging.error(f"❌ OpenAlex data not found at {data_path}")
        return False

    # Count available files
    gz_files = list(data_path.rglob("*.gz"))
    if len(gz_files) == 0:
        logging.error("❌ No .gz data files found")
        return False

    logging.info(f"✅ Found {len(gz_files)} OpenAlex data files")

    # Check output directory
    output_dir = Path("data/processed/openalex_multicountry_temporal")
    if not output_dir.exists():
        logging.info("Creating output directory structure...")
        success = run_command(
            "python scripts/create_openalex_multicountry_processor.py",
            "Setting up infrastructure"
        )
        if not success:
            return False

    logging.info("✅ All prerequisites met")
    return True

def run_data_processing(max_files=None, resume_checkpoint=True):
    """Run the main data processing"""
    logging.info("=" * 60)
    logging.info("PHASE 1: DATA PROCESSING")
    logging.info("=" * 60)

    # Build command
    cmd_parts = ["python", "scripts/process_openalex_multicountry_temporal.py"]

    if resume_checkpoint:
        cmd_parts.append("--resume-checkpoint")

    if max_files:
        cmd_parts.extend(["--max-files", str(max_files)])

    command = " ".join(cmd_parts)

    return run_command(
        command,
        f"Processing OpenAlex data (max files: {max_files or 'ALL'})"
    )

def run_intelligence_reporting():
    """Run the strategic intelligence reporting"""
    logging.info("=" * 60)
    logging.info("PHASE 2: INTELLIGENCE REPORTING")
    logging.info("=" * 60)

    return run_command(
        "python scripts/generate_openalex_strategic_intelligence_report.py",
        "Generating strategic intelligence reports"
    )

def display_results():
    """Display analysis results summary"""
    logging.info("=" * 60)
    logging.info("ANALYSIS RESULTS")
    logging.info("=" * 60)

    output_dir = Path("data/processed/openalex_multicountry_temporal")
    analysis_dir = output_dir / "analysis"

    if analysis_dir.exists():
        logging.info(f"📁 Output Directory: {output_dir}")
        logging.info("📋 Generated Files:")

        key_files = [
            "EXECUTIVE_BRIEFING.md",
            "EXECUTIVE_DASHBOARD.json",
            "COUNTRY_RISK_MATRIX.json",
            "TECHNOLOGY_THREAT_ASSESSMENT.json",
            "TEMPORAL_INTELLIGENCE_BRIEFING.json"
        ]

        for filename in key_files:
            filepath = analysis_dir / filename
            if filepath.exists():
                size = filepath.stat().st_size
                logging.info(f"  ✅ {filename} ({size:,} bytes)")
            else:
                logging.info(f"  ❌ {filename} (missing)")

        # Display executive summary if available
        briefing_file = analysis_dir / "EXECUTIVE_BRIEFING.md"
        if briefing_file.exists():
            logging.info("\n📊 Executive Summary Preview:")
            try:
                with open(briefing_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[:15]:  # First 15 lines
                        logging.info(f"  {line.rstrip()}")
                logging.info("  ...")
            except Exception as e:
                logging.error(f"Error reading briefing: {e}")

    else:
        logging.error("❌ Analysis directory not found")

def run_validation():
    """Run validation checks on the results"""
    logging.info("=" * 60)
    logging.info("PHASE 3: VALIDATION")
    logging.info("=" * 60)

    output_dir = Path("data/processed/openalex_multicountry_temporal")

    # Check if analysis was successful
    analysis_files = list((output_dir / "analysis").glob("comprehensive_analysis_*.json"))
    if not analysis_files:
        logging.error("❌ No analysis files found - processing may have failed")
        return False

    # Load latest analysis for validation
    latest_analysis = max(analysis_files, key=lambda x: x.stat().st_mtime)
    logging.info(f"📄 Validating: {latest_analysis.name}")

    try:
        import json
        with open(latest_analysis, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)

        # Basic validation
        processing_summary = analysis_data.get("processing_summary", {})
        total_papers = processing_summary.get("total_papers_analyzed", 0)
        china_papers = processing_summary.get("papers_with_china", 0)
        errors = processing_summary.get("processing_errors", 0)

        logging.info(f"✅ Validation Results:")
        logging.info(f"  📊 Total papers analyzed: {total_papers:,}")
        logging.info(f"  🇨🇳 Papers with China: {china_papers:,}")
        logging.info(f"  ⚠️ Processing errors: {errors:,}")

        if total_papers == 0:
            logging.warning("⚠️ No papers were analyzed - check data accessibility")
            return False

        if errors / max(total_papers, 1) > 0.1:
            logging.warning(f"⚠️ High error rate: {(errors/total_papers)*100:.1f}%")

        logging.info("✅ Validation passed")
        return True

    except Exception as e:
        logging.error(f"❌ Validation failed: {e}")
        return False

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Complete OpenAlex Multi-Country Analysis")
    parser.add_argument("--max-files", type=int, help="Maximum files to process (for testing)")
    parser.add_argument("--no-resume", action="store_true", help="Don't resume from checkpoint")
    parser.add_argument("--skip-processing", action="store_true", help="Skip data processing, only generate reports")
    parser.add_argument("--validate-only", action="store_true", help="Only run validation")

    args = parser.parse_args()

    start_time = datetime.now()
    logging.info("🚀 Starting Complete OpenAlex Multi-Country Analysis")
    logging.info(f"⏰ Start time: {start_time.isoformat()}")

    # Check prerequisites
    if not check_prerequisites():
        logging.error("❌ Prerequisites not met - exiting")
        sys.exit(1)

    success = True

    if args.validate_only:
        # Only run validation
        success = run_validation()
    else:
        # Run data processing (unless skipped)
        if not args.skip_processing:
            success = run_data_processing(
                max_files=args.max_files,
                resume_checkpoint=not args.no_resume
            )

        # Run intelligence reporting
        if success:
            success = run_intelligence_reporting()

        # Run validation
        if success:
            success = run_validation()

    # Display results
    display_results()

    # Final status
    end_time = datetime.now()
    duration = end_time - start_time

    logging.info("=" * 60)
    if success:
        logging.info("🎉 ANALYSIS COMPLETE - SUCCESS")
        logging.info(f"⏱️  Total time: {duration}")
        logging.info("📋 Ready for strategic intelligence review")
    else:
        logging.error("❌ ANALYSIS FAILED")
        logging.error("🔧 Check logs for error details")
        sys.exit(1)

    logging.info("=" * 60)

if __name__ == "__main__":
    main()
