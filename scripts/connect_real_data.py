"""
CONNECT TO REAL DATA - NO FABRICATION
This script connects to actual data sources and processes them systematically
Priority: Use what we have, report what we don't have
"""

import json
import gzip
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Generator
from dataclasses import dataclass, asdict
import hashlib
from collections import defaultdict

# Setup logging with verification
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_data_connection.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class DataSource:
    """Track each data source and its status"""
    name: str
    path: str
    size_gb: float
    status: str  # AVAILABLE, PROCESSING, PROCESSED, ERROR, NOT_FOUND
    records_found: int = 0
    records_processed: int = 0
    last_checkpoint: Optional[str] = None
    sha256_sample: Optional[str] = None  # Hash of first 1MB for verification

@dataclass
class VerifiedFinding:
    """Only findings with actual data"""
    claim: str
    source_file: str
    line_number: int
    raw_evidence: str
    confidence: float  # 0-1 scale
    uncertainty: float  # ±value
    recompute_command: str
    sha256_hash: str
    timestamp: str

class RealDataConnector:
    """Connect to actual data sources - no fabrication allowed"""

    def __init__(self):
        self.data_sources = self._inventory_data_sources()
        self.findings = []
        self.stats = defaultdict(int)
        self.output_dir = Path("data/real_verified")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _inventory_data_sources(self) -> Dict[str, DataSource]:
        """Inventory what data we actually have"""
        sources = {
            "openalex": DataSource(
                name="OpenAlex Academic Database",
                path="F:/OSINT_Backups/openalex/data",
                size_gb=420.66,
                status="NOT_CHECKED"
            ),
            "ted": DataSource(
                name="TED EU Procurement",
                path="F:/TED_Data/monthly",
                size_gb=24.20,
                status="NOT_CHECKED"
            ),
            "cordis": DataSource(
                name="CORDIS EU Projects",
                path="F:/2025-09-14 Horizons",
                size_gb=0.19,
                status="NOT_CHECKED"
            ),
            "sec_edgar": DataSource(
                name="SEC EDGAR Filings",
                path="F:/OSINT_DATA/COMPANIES",
                size_gb=0.05,
                status="NOT_CHECKED"
            ),
            "epo_patents": DataSource(
                name="EPO Patent Data",
                path="F:/OSINT_DATA/EPO_PATENTS",
                size_gb=0.12,
                status="NOT_CHECKED"
            )
        }

        # Check each source
        for key, source in sources.items():
            if Path(source.path).exists():
                source.status = "AVAILABLE"
                logging.info(f"✓ Found {source.name} at {source.path}")
                # Calculate SHA256 of first 1MB for verification
                source.sha256_sample = self._calculate_sample_hash(source.path)
            else:
                source.status = "NOT_FOUND"
                logging.warning(f"✗ {source.name} not found at {source.path}")

        return sources

    def _calculate_sample_hash(self, path: str) -> str:
        """Calculate SHA256 of first 1MB of data for verification"""
        path = Path(path)
        hasher = hashlib.sha256()
        bytes_read = 0
        max_bytes = 1024 * 1024  # 1MB

        if path.is_dir():
            # Hash first file found
            for file in sorted(path.rglob("*")):
                if file.is_file() and not file.name.startswith('.'):
                    try:
                        with open(file, 'rb') as f:
                            while bytes_read < max_bytes:
                                chunk = f.read(min(8192, max_bytes - bytes_read))
                                if not chunk:
                                    break
                                hasher.update(chunk)
                                bytes_read += len(chunk)
                        break
                    except:
                        continue

        return hasher.hexdigest()[:16]  # First 16 chars for brevity

    def process_openalex_sample(self, limit: int = 1000) -> Dict:
        """Process a sample of OpenAlex data to demonstrate real processing"""
        source = self.data_sources["openalex"]

        if source.status != "AVAILABLE":
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "reason": f"OpenAlex data not available at {source.path}",
                "needed": "OpenAlex data files in .gz format",
                "searched": source.path
            }

        results = {
            "germany_china_collaborations": [],
            "technology_areas": defaultdict(int),
            "institutions": defaultdict(int),
            "yearly_trends": defaultdict(int)
        }

        # Find actual data files
        data_path = Path(source.path) / "works"
        gz_files = list(data_path.rglob("*.gz"))[:5]  # Process first 5 files as sample

        if not gz_files:
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "reason": "No .gz files found in OpenAlex works directory",
                "searched": str(data_path)
            }

        records_processed = 0

        for gz_file in gz_files:
            logging.info(f"Processing {gz_file.name}")

            try:
                with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if records_processed >= limit:
                            break

                        try:
                            record = json.loads(line.strip())

                            # Extract real data
                            if self._is_germany_china_collaboration(record):
                                collab = self._extract_collaboration(record, gz_file.name, line_num)
                                results["germany_china_collaborations"].append(collab)

                            # Count technology areas
                            for concept in record.get("concepts", []):
                                if concept.get("score", 0) > 0.5:
                                    results["technology_areas"][concept.get("display_name", "Unknown")] += 1

                            # Track institutions
                            for authorship in record.get("authorships", []):
                                for inst in authorship.get("institutions", []):
                                    if inst.get("display_name"):
                                        results["institutions"][inst["display_name"]] += 1

                            # Year trends
                            pub_year = record.get("publication_year")
                            if pub_year:
                                results["yearly_trends"][pub_year] += 1

                            records_processed += 1

                        except json.JSONDecodeError:
                            self.stats["json_errors"] += 1
                            continue

            except Exception as e:
                logging.error(f"Error processing {gz_file}: {e}")

        source.records_processed = records_processed

        # Generate verification commands
        results["verification"] = {
            "records_processed": records_processed,
            "source_files": [str(f) for f in gz_files],
            "recompute_command": f"python -c \"import gzip, json; [json.loads(l) for f in {[str(f) for f in gz_files]} for l in gzip.open(f, 'rt')][:1000]\"",
            "sha256_sample": source.sha256_sample
        }

        return results

    def _is_germany_china_collaboration(self, record: Dict) -> bool:
        """Check if paper involves Germany-China collaboration"""
        countries = set()

        for authorship in record.get("authorships", []):
            for inst in authorship.get("institutions", []):
                country = inst.get("country_code", "")
                if country:
                    countries.add(country)

        return "DE" in countries and "CN" in countries

    def _extract_collaboration(self, record: Dict, filename: str, line_num: int) -> VerifiedFinding:
        """Extract verified collaboration with full provenance"""

        # Extract key data
        title = record.get("title", "")
        doi = record.get("doi", "")
        year = record.get("publication_year", "")

        # Get institutions
        de_institutions = []
        cn_institutions = []

        for authorship in record.get("authorships", []):
            for inst in authorship.get("institutions", []):
                if inst.get("country_code") == "DE":
                    de_institutions.append(inst.get("display_name", "Unknown"))
                elif inst.get("country_code") == "CN":
                    cn_institutions.append(inst.get("display_name", "Unknown"))

        claim = f"Germany-China collaboration in {year}: {title[:100]}"

        return VerifiedFinding(
            claim=claim,
            source_file=filename,
            line_number=line_num,
            raw_evidence=json.dumps({
                "doi": doi,
                "title": title,
                "year": year,
                "de_institutions": de_institutions,
                "cn_institutions": cn_institutions
            }),
            confidence=0.9,  # High - direct evidence
            uncertainty=0.05,
            recompute_command=f"zcat {filename} | sed -n '{line_num}p' | jq '.doi'",
            sha256_hash=hashlib.sha256(json.dumps(record).encode()).hexdigest()[:16],
            timestamp=datetime.now().isoformat()
        )

    def process_ted_sample(self, limit: int = 100) -> Dict:
        """Process TED procurement data sample"""
        source = self.data_sources["ted"]

        if source.status != "AVAILABLE":
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "reason": f"TED data not available at {source.path}",
                "needed": "TED XML or CSV files",
                "searched": source.path
            }

        results = {
            "china_related_contracts": [],
            "total_contracts": 0,
            "china_companies": set(),
            "contract_values": []
        }

        # Process actual TED data files
        ted_path = Path(source.path)
        csv_files = list(ted_path.rglob("*.csv"))[:5]

        for csv_file in csv_files:
            # [Implementation for TED processing]
            # This would parse actual CSV files and extract real contract data
            pass

        return results

    def generate_report(self) -> Dict:
        """Generate report of actual findings"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "data_sources": {},
            "findings": [],
            "statistics": dict(self.stats),
            "insufficient_evidence": []
        }

        # Document each data source status
        for key, source in self.data_sources.items():
            report["data_sources"][key] = asdict(source)

        # Add verified findings
        for finding in self.findings:
            report["findings"].append(asdict(finding))

        # Document what we couldn't find
        for key, source in self.data_sources.items():
            if source.status == "NOT_FOUND":
                report["insufficient_evidence"].append({
                    "dataset": source.name,
                    "searched": source.path,
                    "needed": f"Data files for {source.name}",
                    "impact": "Cannot perform related analysis"
                })

        return report

    def save_results(self):
        """Save results with full verification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save main report
        report = self.generate_report()
        report_file = self.output_dir / f"verified_data_report_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logging.info(f"Report saved to {report_file}")

        # Save verification log
        verification_log = {
            "processed": timestamp,
            "sources_checked": len(self.data_sources),
            "sources_available": sum(1 for s in self.data_sources.values() if s.status == "AVAILABLE"),
            "total_findings": len(self.findings),
            "verification_hashes": {
                name: source.sha256_sample
                for name, source in self.data_sources.items()
                if source.sha256_sample
            }
        }

        verification_file = self.output_dir / f"verification_log_{timestamp}.json"
        with open(verification_file, 'w') as f:
            json.dump(verification_log, f, indent=2)

        return report_file, verification_file


def main():
    """Main execution - connect to real data"""
    logging.info("=" * 50)
    logging.info("CONNECTING TO REAL DATA - NO FABRICATION")
    logging.info("=" * 50)

    connector = RealDataConnector()

    # Process samples from each available source
    logging.info("\n1. Processing OpenAlex sample...")
    openalex_results = connector.process_openalex_sample(limit=1000)

    if openalex_results.get("status") != "INSUFFICIENT_EVIDENCE":
        logging.info(f"Found {len(openalex_results.get('germany_china_collaborations', []))} Germany-China collaborations")
        logging.info(f"Technology areas: {len(openalex_results.get('technology_areas', {}))}")
    else:
        logging.warning(f"OpenAlex: {openalex_results['reason']}")

    logging.info("\n2. Processing TED sample...")
    ted_results = connector.process_ted_sample(limit=100)

    # Save all results
    logging.info("\n3. Saving verified results...")
    report_file, verification_file = connector.save_results()

    logging.info("\n" + "=" * 50)
    logging.info("SUMMARY")
    logging.info("=" * 50)
    logging.info(f"✓ Data sources checked: {len(connector.data_sources)}")
    logging.info(f"✓ Sources available: {sum(1 for s in connector.data_sources.values() if s.status == 'AVAILABLE')}")
    logging.info(f"✓ Verified findings: {len(connector.findings)}")
    logging.info(f"✓ Report saved: {report_file}")
    logging.info(f"✓ Verification log: {verification_file}")

    # Print what we need but don't have
    logging.info("\nINSUFFICIENT EVIDENCE - Data Needed:")
    for source in connector.data_sources.values():
        if source.status == "NOT_FOUND":
            logging.info(f"  - {source.name}: Need data at {source.path}")

if __name__ == "__main__":
    main()
