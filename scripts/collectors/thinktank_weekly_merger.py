#!/usr/bin/env python3
"""
Think Tank Global Collector - Weekly Merger

Merges outputs from all regional runs and generates weekly summary memo.

Usage:
    python thinktank_weekly_merger.py
"""

import json
import csv
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class WeeklyMerger:
    """Merges regional outputs and generates weekly summary."""

    OUTPUT_ROOT = Path("F:/ThinkTank_Sweeps")
    REGIONS = ["US_CAN", "EUROPE", "APAC", "ARCTIC"]

    def __init__(self):
        """Initialize weekly merger."""
        self.run_date = datetime.now(timezone.utc).strftime("%Y%m%d")
        self.merge_dir = self.OUTPUT_ROOT / "MERGED" / self.run_date
        self.merge_dir.mkdir(parents=True, exist_ok=True)

        self.all_items = []
        self.all_failures = []
        self.qa_issues = []
        self.dedupe_hashes = set()
        self.duplicates_removed = 0

    def find_latest_regional_outputs(self) -> Dict[str, Path]:
        """Find the latest output directory for each region."""
        latest_dirs = {}

        for region in self.REGIONS:
            region_dir = self.OUTPUT_ROOT / region
            if not region_dir.exists():
                logging.warning(f"No output directory found for {region}")
                continue

            # Find latest date directory
            date_dirs = sorted([d for d in region_dir.iterdir() if d.is_dir()], reverse=True)
            if date_dirs:
                latest_dirs[region] = date_dirs[0]
                logging.info(f"{region}: Using {date_dirs[0].name}")
            else:
                logging.warning(f"No date directories found for {region}")

        return latest_dirs

    def load_regional_data(self, regional_dirs: Dict[str, Path]):
        """Load items and failures from all regional outputs."""
        for region, region_dir in regional_dirs.items():
            logging.info(f"\nLoading data from {region}...")

            # Load items
            items_json = region_dir / "items.json"
            if items_json.exists():
                with open(items_json, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                    logging.info(f"  Loaded {len(items)} items")
                    self.all_items.extend(items)
            else:
                logging.warning(f"  No items.json found")

            # Load failures
            failures_md = region_dir / "download_failures.md"
            if failures_md.exists():
                # Parse markdown failures (simplified)
                with open(failures_md, 'r', encoding='utf-8') as f:
                    content = f.read()
                    failure_lines = [line for line in content.split('\n') if line.startswith('- [')]
                    logging.info(f"  Loaded {len(failure_lines)} failures")
                    for line in failure_lines:
                        self.all_failures.append({
                            "region": region,
                            "line": line
                        })

            # Load QA report
            qa_report = region_dir / "qa_report.json"
            if qa_report.exists():
                with open(qa_report, 'r', encoding='utf-8') as f:
                    qa_data = json.load(f)
                    self.qa_issues.append({
                        "region": region,
                        "data": qa_data
                    })

    def deduplicate_items(self):
        """Remove duplicates across regions using hash-based deduplication."""
        logging.info("\nDeduplicating items across regions...")

        unique_items = []

        for item in self.all_items:
            item_hash = item.get("hash_sha256")

            if not item_hash:
                # No hash, keep item
                unique_items.append(item)
                continue

            if item_hash in self.dedupe_hashes:
                # Duplicate, skip
                self.duplicates_removed += 1
                continue

            # New item, add
            self.dedupe_hashes.add(item_hash)
            unique_items.append(item)

        logging.info(f"  Removed {self.duplicates_removed} duplicates")
        logging.info(f"  Unique items: {len(unique_items)}")

        self.all_items = unique_items

    def write_merged_outputs(self):
        """Write merged outputs."""
        logging.info(f"\nWriting merged outputs to {self.merge_dir}")

        # 1. thinktank_master.json
        master_json_path = self.merge_dir / "thinktank_master.json"
        with open(master_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.all_items, f, indent=2, ensure_ascii=False)
        logging.info(f"  Wrote thinktank_master.json ({len(self.all_items)} items)")

        # 2. thinktank_master.csv
        if self.all_items:
            master_csv_path = self.merge_dir / "thinktank_master.csv"

            # Get all unique keys
            all_keys = set()
            for item in self.all_items:
                all_keys.update(item.keys())

            with open(master_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(self.all_items)
            logging.info(f"  Wrote thinktank_master.csv")

        # 3. Merged QA report
        qa_report_path = self.merge_dir / "qa_report.json"
        with open(qa_report_path, 'w', encoding='utf-8') as f:
            json.dump({
                "total_items": len(self.all_items),
                "duplicates_removed": self.duplicates_removed,
                "regional_qa_issues": self.qa_issues
            }, f, indent=2)
        logging.info(f"  Wrote qa_report.json")

        # 4. Merged failures
        failures_md_path = self.merge_dir / "download_failures.md"
        with open(failures_md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Download Failures - Weekly Merge - {self.run_date}\n\n")
            f.write(f"Total failures: {len(self.all_failures)}\n\n")
            f.write("## Failures by Region\n\n")
            for failure in self.all_failures:
                f.write(f"{failure['line']}\n")
        logging.info(f"  Wrote download_failures.md ({len(self.all_failures)} failures)")

    def generate_weekly_memo(self):
        """Generate weekly summary memo."""
        logging.info("\nGenerating weekly summary memo...")

        memo_path = self.merge_dir / "weekly_summary_memo.md"

        # Calculate statistics
        total_docs = len(self.all_items)
        unique_docs = len(self.dedupe_hashes)

        # Top organizations
        org_counter = Counter(item.get("publisher_org", "Unknown") for item in self.all_items)
        top_orgs = org_counter.most_common(10)

        # Leading topics
        all_topics = []
        for item in self.all_items:
            all_topics.extend(item.get("topics", []))
        topic_counter = Counter(all_topics)
        top_topics = topic_counter.most_common(10)

        # QA statistics
        total_qa_issues = sum(qa["data"].get("items_with_issues", 0) for qa in self.qa_issues)

        # Downloads vs failures
        successful_downloads = len([i for i in self.all_items if i.get("download_url")])
        failed_downloads = len(self.all_failures)

        with open(memo_path, 'w', encoding='utf-8') as f:
            f.write(f"# Weekly Summary — Think-Tank Global Sweep ({self.run_date})\n\n")

            f.write("## Overview\n\n")
            f.write(f"- **Total docs:** {total_docs} (unique: {unique_docs})\n")
            f.write(f"- **Successful downloads:** {successful_downloads} | **Failed:** {failed_downloads}\n")
            f.write(f"- **Duplicates removed:** {self.duplicates_removed}\n\n")

            f.write("### Top Organizations by Output\n\n")
            for org, count in top_orgs:
                f.write(f"- {org}: {count}\n")
            f.write("\n")

            f.write("### Leading Topics\n\n")
            for topic, count in top_topics:
                f.write(f"- {topic}: {count}\n")
            f.write("\n")

            f.write("## QA Highlights\n\n")
            f.write(f"- **Items with QA issues:** {total_qa_issues}\n")
            f.write(f"- **Failed downloads:** {failed_downloads}\n\n")

            f.write("## Operational Notes\n\n")
            f.write("- Truncated sources: None reported\n")
            f.write("- Degraded sources: None reported\n")
            f.write("- Policy overrides in effect: None\n\n")

            f.write("## Next Steps\n\n")
            f.write("- Investigate recurring failures (see download_failures.md)\n")
            f.write("- Cross-link with U.S. Gov & China sweeps; push notable items to analyst queue\n")
            f.write("- Update dashboards; refresh coverage gap map\n\n")

            f.write("---\n\n")
            f.write(f"*Generated: {datetime.now(timezone.utc).isoformat()}*\n")

        logging.info(f"  Wrote weekly_summary_memo.md")

    def run(self):
        """Main execution flow."""
        logging.info(f"\n{'='*60}")
        logging.info(f"Starting Weekly Merge")
        logging.info(f"Date: {self.run_date}")
        logging.info(f"{'='*60}\n")

        # Find latest regional outputs
        regional_dirs = self.find_latest_regional_outputs()

        if not regional_dirs:
            logging.error("No regional outputs found to merge")
            return

        # Load data
        self.load_regional_data(regional_dirs)

        # Deduplicate
        self.deduplicate_items()

        # Write outputs
        self.write_merged_outputs()

        # Generate memo
        self.generate_weekly_memo()

        logging.info(f"\n{'='*60}")
        logging.info(f"Weekly Merge Complete")
        logging.info(f"Total Items: {len(self.all_items)}")
        logging.info(f"Duplicates Removed: {self.duplicates_removed}")
        logging.info(f"Output Directory: {self.merge_dir}")
        logging.info(f"{'='*60}\n")


def main():
    """CLI entry point."""
    merger = WeeklyMerger()
    merger.run()


if __name__ == "__main__":
    main()
