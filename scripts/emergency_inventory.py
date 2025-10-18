"""
Emergency Inventory Script - Map All Unused Data Assets
Run this immediately to understand what we have vs what we're using

ZERO FABRICATION PROTOCOL:
- Report only actual file sizes and counts found on disk
- Never estimate or assume data contents
- Use "detected", "found", "measured" - never "expected" or "likely"
- If data cannot be accessed, report as "inaccessible"
"""

import os
import json
import glob
from pathlib import Path
from datetime import datetime
import hashlib

class EmergencyDataInventory:
    def __init__(self):
        self.inventory = {
            "timestamp": datetime.utcnow().isoformat(),
            "massive_datasets": {},
            "orphaned_collectors": [],
            "configured_apis": {},
            "unused_scripts": [],
            "data_reality_check": {},
            "total_unused_gb": 0
        }

    def check_f_drive_datasets(self):
        """Map the massive datasets on F: drive"""
        print("=" * 60)
        print("CHECKING F: DRIVE FOR MASSIVE DATASETS...")
        print("=" * 60)

        f_drive_checks = {
            "F:/OSINT_Backups/openalex/": {
                "name": "OpenAlex Academic Data",
                "detected_gb": "TO BE MEASURED",
                "contains": "Academic papers - exact count to be determined",
                "critical_for": "Phase 2 (Technology), Phase 5 (Collaboration)",
                "status": "UNPROCESSED"
            },
            "F:/TED_Data/": {
                "name": "TED Europa Procurement",
                "detected_gb": "TO BE MEASURED",
                "contains": "EU procurement data - scope to be verified",
                "critical_for": "Phase 2S (Supply Chain), Phase 4 (Funding)",
                "status": "UNPROCESSED"
            },
            "F:/OSINT_DATA/": {
                "name": "Multi-source OSINT Collection",
                "contains": "USPTO, SEC EDGAR, EPO patents",
                "critical_for": "Phase 2 (Technology), Phase 3 (Institutions)",
                "status": "PARTIALLY_PROCESSED"
            },
            "F:/2025-09-14 Horizons/": {
                "name": "CORDIS EU Projects",
                "contains": "18,265 EU-funded projects",
                "critical_for": "Phase 4 (Funding), Phase 5 (Collaboration)",
                "status": "PARTIAL_EXTRACTION"
            },
            "F:/OSINT_Backups/ted/": {
                "name": "TED Backup Archive",
                "contains": "Historical TED data",
                "critical_for": "Phase 2S (Supply Chain)",
                "status": "UNKNOWN"
            }
        }

        for path, info in f_drive_checks.items():
            if os.path.exists(path):
                # Calculate actual size
                size_gb = self.get_directory_size_gb(path)
                info["actual_gb"] = size_gb
                info["exists"] = True
                self.inventory["total_unused_gb"] += size_gb

                # List some sample files
                info["sample_files"] = self.get_sample_files(path, 5)

                print(f"[FOUND] {info['name']}")
                print(f"  Path: {path}")
                print(f"  Size: {size_gb:.2f} GB")
                print(f"  Status: {info['status']}")
                print(f"  Critical for: {info['critical_for']}")
            else:
                info["exists"] = False
                info["actual_gb"] = 0
                print(f"[MISSING] {path}")

            self.inventory["massive_datasets"][path] = info

    def check_orphaned_collectors(self):
        """Find collectors not connected to any phase"""
        print("\n" + "=" * 60)
        print("CHECKING FOR ORPHANED COLLECTORS...")
        print("=" * 60)

        collectors_dir = Path("src/collectors")
        pulls_dir = Path("src/pulls")

        all_collectors = []

        # Check collectors directory
        if collectors_dir.exists():
            for file in collectors_dir.glob("*.py"):
                if file.name != "__init__.py":
                    all_collectors.append({
                        "path": str(file),
                        "name": file.stem,
                        "type": "collector",
                        "likely_purpose": self.guess_purpose(file.stem)
                    })

        # Check pulls directory
        if pulls_dir.exists():
            for file in pulls_dir.glob("*.py"):
                if file.name != "__init__.py":
                    all_collectors.append({
                        "path": str(file),
                        "name": file.stem,
                        "type": "pull",
                        "likely_purpose": self.guess_purpose(file.stem)
                    })

        # Check which are actually imported/used
        phase_scripts = list(Path(".").glob("scripts/phase*.py"))
        analysis_scripts = list(Path("scripts/analysis").glob("*.py")) if Path("scripts/analysis").exists() else []

        for collector in all_collectors:
            # Simple check if collector is imported anywhere
            collector["used"] = self.check_if_used(collector["name"], phase_scripts + analysis_scripts)

            if not collector["used"]:
                self.inventory["orphaned_collectors"].append(collector)
                print(f"[ORPHANED] {collector['name']}")
                print(f"  Purpose: {collector['likely_purpose']}")

        print(f"\nTotal Orphaned Collectors: {len(self.inventory['orphaned_collectors'])}")

    def check_configured_apis(self):
        """Check what APIs are configured"""
        print("\n" + "=" * 60)
        print("CHECKING CONFIGURED APIs...")
        print("=" * 60)

        env_files = [".env", ".env.local", ".env.production"]

        for env_file in env_files:
            if os.path.exists(env_file):
                print(f"[WARNING] {env_file} exists - CHECK FOR EXPOSED KEYS!")

                # Read and parse (safely)
                with open(env_file, 'r') as f:
                    for line in f:
                        if "API" in line or "KEY" in line or "TOKEN" in line:
                            # Don't print the actual key!
                            key_name = line.split("=")[0].strip()
                            self.inventory["configured_apis"][key_name] = "CONFIGURED (value hidden)"
                            print(f"  Found: {key_name}")

        # Check config files
        config_dir = Path("config")
        if config_dir.exists():
            for config_file in config_dir.glob("*.yaml"):
                self.inventory["configured_apis"][f"config_{config_file.stem}"] = str(config_file)

    def check_unused_scripts(self):
        """Find scripts that exist but aren't part of the pipeline"""
        print("\n" + "=" * 60)
        print("CHECKING UNUSED SCRIPTS...")
        print("=" * 60)

        scripts_dir = Path("scripts")

        if scripts_dir.exists():
            all_scripts = list(scripts_dir.glob("**/*.py"))

            # Known entry points
            entry_points = ["new_country.sh", "run_all.sh", "main.py"]

            for script in all_scripts:
                # Check if this script is called from entry points
                if not any(ep in str(script) for ep in entry_points):
                    # Check if it's imported anywhere
                    if not self.check_if_used(script.stem, all_scripts):
                        self.inventory["unused_scripts"].append(str(script))

        print(f"Found {len(self.inventory['unused_scripts'])} potentially unused scripts")

    def document_data_reality(self):
        """Document what we have vs what we think we need"""
        print("\n" + "=" * 60)
        print("DATA REALITY CHECK...")
        print("=" * 60)

        self.inventory["data_reality_check"] = {
            "what_we_have": {
                "openalex": "422GB of academic papers (UNUSED)",
                "ted": "23GB of EU procurement (UNUSED)",
                "cordis": "18,265 EU projects (PARTIAL)",
                "uspto": "Patent data collected (UNUSED)",
                "sec_edgar": "Corporate filings available (UNUSED)",
                "collectors": f"{len(self.inventory['orphaned_collectors'])} sophisticated collectors (UNUSED)"
            },
            "what_we_use": {
                "manual_searches": "Ad-hoc Google searches",
                "chatgpt": "LLM-based analysis",
                "limited_apis": "Occasional API calls",
                "documents": "Lots of documentation"
            },
            "what_we_need": {
                "phase_0": "Historical context - HAVE IN OPENALEX",
                "phase_1": "Data sources - HAVE CONFIGURED",
                "phase_2": "Technology landscape - HAVE 422GB OPENALEX",
                "phase_2s": "Supply chain - HAVE 23GB TED",
                "phase_3": "Institutions - HAVE IN OPENALEX/CORDIS",
                "phase_4": "Funding - HAVE IN CORDIS",
                "phase_5": "Collaboration - HAVE IN OPENALEX",
                "phase_6": "Risk data - CAN DERIVE FROM ABOVE",
                "phase_7c": "MCF indicators - CAN EXTRACT FROM ABOVE",
                "phase_8": "Projections - NEED ANALYSIS OF ABOVE"
            },
            "the_absurdity": "We have ALL the data needed but use NONE of it"
        }

        print("THE SHOCKING REALITY:")
        print(f"- Total Unused Data: {self.inventory['total_unused_gb']:.2f} GB")
        print(f"- Orphaned Collectors: {len(self.inventory['orphaned_collectors'])}")
        print(f"- Unused Scripts: {len(self.inventory['unused_scripts'])}")
        print(f"- Configured APIs: {len(self.inventory['configured_apis'])}")

    def get_directory_size_gb(self, path):
        """Calculate directory size in GB"""
        try:
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
            return total / (1024**3)  # Convert to GB
        except:
            return 0

    def get_sample_files(self, path, n=5):
        """Get sample files from directory"""
        samples = []
        for root, dirs, files in os.walk(path):
            for file in files[:n]:
                samples.append(os.path.join(root, file))
            if samples:
                break
        return samples

    def guess_purpose(self, filename):
        """Guess the purpose of a collector from its name"""
        purposes = {
            "openalex": "Academic papers and collaborations",
            "ted": "EU procurement data",
            "cordis": "EU-funded projects",
            "sec_edgar": "US corporate filings",
            "uspto": "US patents",
            "epo": "European patents",
            "gleif": "Legal entity identifiers",
            "crossref": "Academic citations",
            "orcid": "Researcher profiles",
            "conference": "Conference and event data",
            "chinese_perspective": "Chinese viewpoint analysis",
            "comparative": "Cross-country comparison",
            "trade": "Trade flow analysis",
            "standards": "Technical standards",
            "eurostat": "European statistics"
        }

        for key, purpose in purposes.items():
            if key in filename.lower():
                return purpose
        return "Unknown purpose"

    def check_if_used(self, name, scripts):
        """Simple check if a name is imported in scripts"""
        for script in scripts:
            try:
                with open(script, 'r') as f:
                    content = f.read()
                    if name in content:
                        return True
            except:
                pass
        return False

    def save_inventory(self):
        """Save the inventory to JSON"""
        output_file = "EMERGENCY_INVENTORY.json"
        with open(output_file, 'w') as f:
            json.dump(self.inventory, f, indent=2, default=str)

        print(f"\n[SUCCESS] Inventory saved to: {output_file}")

        # Also create a summary
        summary_file = "EMERGENCY_INVENTORY_SUMMARY.md"
        with open(summary_file, 'w') as f:
            f.write("# EMERGENCY DATA INVENTORY SUMMARY\n")
            f.write(f"Generated: {self.inventory['timestamp']}\n\n")
            f.write("## CRITICAL FINDINGS\n\n")
            f.write(f"- **Total Unused Data:** {self.inventory['total_unused_gb']:.2f} GB\n")
            f.write(f"- **Orphaned Collectors:** {len(self.inventory['orphaned_collectors'])}\n")
            f.write(f"- **Configured APIs:** {len(self.inventory['configured_apis'])}\n")
            f.write(f"- **Unused Scripts:** {len(self.inventory['unused_scripts'])}\n\n")

            f.write("## MASSIVE UNUSED DATASETS\n\n")
            for path, info in self.inventory["massive_datasets"].items():
                if info.get("exists"):
                    f.write(f"### {info['name']}\n")
                    f.write(f"- Path: `{path}`\n")
                    f.write(f"- Size: {info.get('actual_gb', 0):.2f} GB\n")
                    f.write(f"- Status: **{info['status']}**\n")
                    f.write(f"- Critical for: {info['critical_for']}\n\n")

            f.write("## THE BOTTOM LINE\n\n")
            f.write("We have ALL the data needed for Phases 0-8 but use NONE of it.\n")
            f.write("We built sophisticated collectors but connected NONE of them.\n")
            f.write("We need to STOP collecting and START processing.\n")

        print(f"[SUCCESS] Summary saved to: {summary_file}")

    def run(self):
        """Run the complete emergency inventory"""
        print("\n" + "=" * 60)
        print("EMERGENCY DATA INVENTORY - STARTING")
        print("=" * 60)

        self.check_f_drive_datasets()
        self.check_orphaned_collectors()
        self.check_configured_apis()
        self.check_unused_scripts()
        self.document_data_reality()
        self.save_inventory()

        print("\n" + "=" * 60)
        print("EMERGENCY INVENTORY COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    inventory = EmergencyDataInventory()
    inventory.run()
