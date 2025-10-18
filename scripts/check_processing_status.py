"""
Check Processing Status Before Starting New Analysis
Prevents duplicate work by showing what's already been processed
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import hashlib

class ProcessingStatusChecker:
    """Check what data has been processed to avoid duplication"""

    def __init__(self):
        self.project_root = Path("C:/Projects/OSINT - Foresight")
        self.data_root = self.project_root / "data"
        self.status = {
            "openalex": self._check_openalex(),
            "ted": self._check_ted(),
            "cordis": self._check_cordis(),
            "sec_edgar": self._check_sec(),
            "epo_patents": self._check_epo()
        }

    def _check_openalex(self) -> Dict:
        """Check OpenAlex processing status"""
        status = {
            "processed": False,
            "sessions": [],
            "total_records": 0,
            "findings": 0,
            "output_files": []
        }

        # Check various output directories
        dirs_to_check = [
            "processed/openalex_germany_china",
            "processed/openalex_real_data",
            "processed/openalex_systematic",
            "real_verified"
        ]

        for dir_name in dirs_to_check:
            dir_path = self.data_root / dir_name
            if dir_path.exists():
                # Check for checkpoint files
                checkpoint = dir_path / "checkpoint.json"
                if checkpoint.exists():
                    with open(checkpoint, 'r') as f:
                        data = json.load(f)
                        status["sessions"].append({
                            "timestamp": data.get("timestamp", "Unknown"),
                            "location": str(dir_path),
                            "records": data.get("stats", {}).get("total_papers", 0),
                            "findings": data.get("stats", {}).get("germany_china_collaborations", 0)
                        })
                        status["total_records"] += data.get("stats", {}).get("total_papers", 0)
                        status["findings"] += data.get("stats", {}).get("germany_china_collaborations", 0)

                # Check for output files
                for file in dir_path.glob("*.json"):
                    if "checkpoint" not in file.name:
                        status["output_files"].append(str(file))

                for file in dir_path.glob("*.md"):
                    status["output_files"].append(str(file))

        status["processed"] = len(status["sessions"]) > 0
        return status

    def _check_ted(self) -> Dict:
        """Check TED processing status"""
        status = {
            "processed": False,
            "sessions": [],
            "output_files": []
        }

        ted_dirs = [
            "processed/ted_analysis",
            "processed/ted_complete_analysis",
            "processed/ted_italy_analysis",
            "processed/ted_china_contracts",
            "processed/ted_risk_analysis"
        ]

        for dir_name in ted_dirs:
            dir_path = self.data_root / dir_name
            if dir_path.exists():
                status["processed"] = True
                files = list(dir_path.glob("*.json")) + list(dir_path.glob("*.csv"))
                status["output_files"].extend([str(f) for f in files])

                # Check for analysis results
                for json_file in dir_path.glob("*.json"):
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                status["sessions"].append({
                                    "file": str(json_file),
                                    "timestamp": json_file.stat().st_mtime
                                })
                    except:
                        pass

        return status

    def _check_cordis(self) -> Dict:
        """Check CORDIS processing status"""
        status = {
            "processed": False,
            "sessions": [],
            "output_files": []
        }

        cordis_dirs = [
            "processed/cordis_comprehensive",
            "processed/italy_cordis"
        ]

        for dir_name in cordis_dirs:
            dir_path = self.data_root / dir_name
            if dir_path.exists():
                status["processed"] = True
                files = list(dir_path.glob("*.*"))
                status["output_files"].extend([str(f) for f in files])

        return status

    def _check_sec(self) -> Dict:
        """Check SEC EDGAR processing status"""
        status = {
            "processed": False,
            "output_files": []
        }

        sec_dirs = ["processed/sec_italian_networks"]
        for dir_name in sec_dirs:
            dir_path = self.data_root / dir_name
            if dir_path.exists():
                status["processed"] = True
                status["output_files"].extend([str(f) for f in dir_path.glob("*.*")])

        return status

    def _check_epo(self) -> Dict:
        """Check EPO patent processing status"""
        status = {
            "processed": False,
            "output_files": []
        }

        # Check for patent analysis outputs
        patent_dirs = ["processed/patent_tech_transfer"]
        for dir_name in patent_dirs:
            dir_path = self.data_root / dir_name
            if dir_path.exists():
                status["processed"] = True
                status["output_files"].extend([str(f) for f in dir_path.glob("*.*")])

        return status

    def generate_report(self) -> str:
        """Generate status report"""
        report = f"""
# DATA PROCESSING STATUS CHECK
Generated: {datetime.now().isoformat()}

## QUICK SUMMARY
"""

        for source, info in self.status.items():
            if info["processed"]:
                emoji = "[DONE]"
                status_text = "PROCESSED"
            else:
                emoji = "[TODO]"
                status_text = "NOT PROCESSED"

            report += f"- {emoji} **{source.upper()}**: {status_text}"

            if source == "openalex" and info["processed"]:
                report += f" ({info['total_records']:,} records, {info['findings']} findings)"
            elif info.get("output_files"):
                report += f" ({len(info['output_files'])} output files)"

            report += "\n"

        # Detailed sections
        report += "\n## DETAILED STATUS\n"

        # OpenAlex details
        if self.status["openalex"]["processed"]:
            report += "\n### OpenAlex Processing Sessions\n"
            for session in self.status["openalex"]["sessions"]:
                report += f"- **{session['timestamp']}**\n"
                report += f"  - Location: `{session['location']}`\n"
                report += f"  - Records: {session['records']:,}\n"
                report += f"  - Findings: {session['findings']}\n"

            report += f"\n**Total OpenAlex Records Processed:** {self.status['openalex']['total_records']:,}\n"
            report += f"**Total Germany-China Collaborations Found:** {self.status['openalex']['findings']}\n"

            report += "\n**Output Files:**\n"
            for file in self.status["openalex"]["output_files"][:5]:  # Show first 5
                report += f"- `{file}`\n"
            if len(self.status["openalex"]["output_files"]) > 5:
                report += f"- ... and {len(self.status['openalex']['output_files']) - 5} more\n"

        # TED details
        if self.status["ted"]["processed"]:
            report += "\n### TED Processing\n"
            report += f"Found {len(self.status['ted']['output_files'])} output files:\n"
            for file in self.status["ted"]["output_files"][:5]:
                report += f"- `{file}`\n"

        # Recommendations
        report += "\n## RECOMMENDATIONS\n"

        unprocessed = [k for k, v in self.status.items() if not v["processed"]]
        if unprocessed:
            report += "\n### Not Yet Processed:\n"
            for source in unprocessed:
                report += f"- **{source.upper()}**: Ready to process\n"

        if self.status["openalex"]["processed"] and self.status["openalex"]["total_records"] < 10000000:
            report += "\n### OpenAlex:\n"
            report += "- [WARNING] Only processed ~1.2M of ~250M records (0.5%)\n"
            report += "- Recommend resuming with checkpoint\n"

        report += "\n## NEXT STEPS\n"
        report += "1. Check `docs/MASTER_DATA_PROCESSING_LOG.md` for full details\n"
        report += "2. Use checkpoint files to resume processing\n"
        report += "3. Update log after any new processing\n"

        return report

    def check_duplicates(self, proposed_analysis: str) -> bool:
        """Check if proposed analysis would duplicate existing work"""
        proposed_lower = proposed_analysis.lower()

        # Check OpenAlex
        if "openalex" in proposed_lower and "germany" in proposed_lower and "china" in proposed_lower:
            if self.status["openalex"]["findings"] > 0:
                print("[WARNING] Germany-China OpenAlex analysis already exists!")
                print(f"  - Already found {self.status['openalex']['findings']} collaborations")
                print(f"  - Check existing results before proceeding")
                return True

        # Check TED
        if "ted" in proposed_lower and self.status["ted"]["processed"]:
            print("[WARNING] TED data may have been processed!")
            print(f"  - Found {len(self.status['ted']['output_files'])} existing files")
            print("  - Verify if your analysis is different")
            return True

        return False

    def save_status(self):
        """Save current status to file"""
        status_file = self.data_root / "processing_status.json"
        with open(status_file, 'w') as f:
            json.dump({
                "generated": datetime.now().isoformat(),
                "status": self.status
            }, f, indent=2, default=str)
        print(f"Status saved to {status_file}")


def main():
    """Run status check"""
    print("=" * 50)
    print("CHECKING DATA PROCESSING STATUS")
    print("=" * 50)

    checker = ProcessingStatusChecker()

    # Generate and print report
    report = checker.generate_report()
    print(report)

    # Save report
    report_file = Path("data/processing_status_report.md")
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")

    # Save JSON status
    checker.save_status()

    # Interactive check
    print("\n" + "=" * 50)
    response = input("Enter proposed analysis to check for duplicates (or 'skip'): ")
    if response.lower() != 'skip':
        is_duplicate = checker.check_duplicates(response)
        if not is_duplicate:
            print("[OK] No obvious duplicates found - proceed with analysis")

    print("\n" + "=" * 50)
    print("Remember to update MASTER_DATA_PROCESSING_LOG.md after processing!")

if __name__ == "__main__":
    main()
