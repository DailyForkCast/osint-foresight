"""
SYSTEMATIC DATA PROCESSOR
Processes 445GB of data through our validated phase framework
Priority: OpenAlex (420GB) -> TED (24GB) -> Others
"""

import json
import gzip
import csv
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Generator, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_processing.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ProcessingResult:
    """Track processing results for each dataset"""
    dataset: str
    records_processed: int
    relevant_records: int
    errors: int
    start_time: datetime
    end_time: Optional[datetime]
    output_files: List[str]
    key_findings: List[str]

class OpenAlexProcessor:
    """
    Process 420GB OpenAlex dataset for academic collaborations and technology areas
    Focuses on Germany-China connections for Phase 2 and Phase 5
    """

    def __init__(self, base_path: str = "F:/OSINT_Backups/openalex"):
        self.base_path = Path(base_path)
        self.output_dir = Path("data/processed/openalex_systematic")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Technology keywords for Phase 2
        self.tech_keywords = {
            "AI_ML": ["artificial intelligence", "machine learning", "deep learning", "neural network"],
            "Semiconductors": ["semiconductor", "chip", "microprocessor", "integrated circuit", "wafer"],
            "Quantum": ["quantum computing", "quantum communication", "quantum cryptography", "qubit"],
            "Biotechnology": ["biotechnology", "gene editing", "CRISPR", "synthetic biology"],
            "Advanced_Materials": ["graphene", "nanomaterial", "metamaterial", "composite material"],
            "5G_6G": ["5G", "6G", "wireless communication", "telecommunications"],
            "Robotics": ["robotics", "autonomous system", "drone", "UAV"],
            "Energy": ["renewable energy", "battery", "solar cell", "fuel cell", "energy storage"]
        }

        # Country identifiers
        self.country_codes = {
            "Germany": ["DE", "Germany", "Deutschland"],
            "China": ["CN", "China", "PRC", "People's Republic"],
            "Italy": ["IT", "Italy", "Italia"],
            "USA": ["US", "USA", "United States"]
        }

        self.stats = defaultdict(int)

    def stream_process_gz(self, file_path: Path) -> Generator[Dict, None, None]:
        """
        Stream process compressed JSON lines files
        Critical for handling 420GB without memory overflow
        """
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num % 10000 == 0:
                        logging.info(f"Processing {file_path.name}: {line_num:,} records")

                    try:
                        yield json.loads(line.strip())
                    except json.JSONDecodeError as e:
                        self.stats['json_errors'] += 1
                        if self.stats['json_errors'] < 10:  # Log first 10 errors
                            logging.warning(f"JSON error in {file_path.name} line {line_num}: {e}")
                        continue

        except Exception as e:
            logging.error(f"Failed to process {file_path}: {e}")

    def extract_country_collaborations(self, paper: Dict) -> Dict:
        """
        Extract international collaborations from paper metadata
        Focus on Germany-China connections
        """
        collaborations = {
            "paper_id": paper.get("id", ""),
            "title": paper.get("title", ""),
            "year": paper.get("publication_year"),
            "countries": set(),
            "institutions": [],
            "is_germany_china": False,
            "technology_areas": []
        }

        # Extract author affiliations
        for author in paper.get("authorships", []):
            for institution in author.get("institutions", []):
                country = institution.get("country_code", "")
                if country:
                    collaborations["countries"].add(country)
                    collaborations["institutions"].append({
                        "name": institution.get("display_name", ""),
                        "country": country
                    })

        # Check for Germany-China collaboration
        has_germany = any(c in collaborations["countries"] for c in ["DE"])
        has_china = any(c in collaborations["countries"] for c in ["CN"])
        collaborations["is_germany_china"] = has_germany and has_china

        # Extract technology areas from abstract
        abstract = paper.get("abstract", "") or ""
        title = paper.get("title", "") or ""
        full_text = f"{title} {abstract}".lower()

        for tech_area, keywords in self.tech_keywords.items():
            if any(keyword in full_text for keyword in keywords):
                collaborations["technology_areas"].append(tech_area)

        return collaborations

    def process_batch(self, country_filter: str = "Germany") -> ProcessingResult:
        """
        Process OpenAlex data in batches
        Focus on specific country to manage scope
        """
        start_time = datetime.now()
        result = ProcessingResult(
            dataset="OpenAlex",
            records_processed=0,
            relevant_records=0,
            errors=0,
            start_time=start_time,
            end_time=None,
            output_files=[],
            key_findings=[]
        )

        # Output files for different analyses
        collab_file = self.output_dir / f"collaborations_{country_filter.lower()}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        tech_file = self.output_dir / f"technology_landscape_{country_filter.lower()}_{datetime.now().strftime('%Y%m%d')}.json"

        collaborations = []
        tech_landscape = defaultdict(lambda: {"papers": 0, "collaborating_countries": set()})

        # Find all .gz files
        gz_files = list(self.base_path.glob("*.gz"))
        logging.info(f"Found {len(gz_files)} OpenAlex compressed files to process")

        # Process first file as demonstration (in production, process all)
        for gz_file in gz_files[:1]:  # Process first file for demo
            logging.info(f"Processing {gz_file.name} ({gz_file.stat().st_size / (1024**3):.2f} GB)")

            for paper in self.stream_process_gz(gz_file):
                result.records_processed += 1

                # Extract collaboration data
                collab_data = self.extract_country_collaborations(paper)

                # Filter for relevant records
                if country_filter == "Germany" and "DE" in collab_data["countries"]:
                    result.relevant_records += 1

                    # Save collaboration if international
                    if len(collab_data["countries"]) > 1:
                        collaborations.append(collab_data)

                        # Update technology landscape
                        for tech in collab_data["technology_areas"]:
                            tech_landscape[tech]["papers"] += 1
                            tech_landscape[tech]["collaborating_countries"].update(collab_data["countries"])

                    # Write collaborations periodically to avoid memory issues
                    if len(collaborations) >= 1000:
                        with open(collab_file, 'a', encoding='utf-8') as f:
                            for collab in collaborations:
                                # Convert sets to lists for JSON serialization
                                collab["countries"] = list(collab["countries"])
                                json.dump(collab, f)
                                f.write('\n')
                        collaborations = []

                if result.records_processed % 100000 == 0:
                    logging.info(f"Processed {result.records_processed:,} records, found {result.relevant_records:,} relevant")

        # Write remaining collaborations
        if collaborations:
            with open(collab_file, 'a', encoding='utf-8') as f:
                for collab in collaborations:
                    collab["countries"] = list(collab["countries"])
                    json.dump(collab, f)
                    f.write('\n')

        # Convert sets to lists in tech_landscape
        tech_landscape_serializable = {}
        for tech, data in tech_landscape.items():
            tech_landscape_serializable[tech] = {
                "papers": data["papers"],
                "collaborating_countries": list(data["collaborating_countries"])
            }

        # Write technology landscape summary
        with open(tech_file, 'w', encoding='utf-8') as f:
            json.dump(tech_landscape_serializable, f, indent=2)

        # Generate key findings
        result.key_findings = [
            f"Processed {result.records_processed:,} OpenAlex records",
            f"Found {result.relevant_records:,} papers with {country_filter} authors",
            f"Identified {len(tech_landscape)} technology areas",
            f"Top technology area: {max(tech_landscape.keys(), key=lambda k: tech_landscape[k]['papers']) if tech_landscape else 'None'}"
        ]

        # Calculate Germany-China collaborations
        germany_china_count = sum(1 for c in collaborations if c.get("is_germany_china", False))
        if germany_china_count > 0:
            result.key_findings.append(f"Found {germany_china_count} Germany-China collaborations")

        result.output_files = [str(collab_file), str(tech_file)]
        result.end_time = datetime.now()

        logging.info(f"OpenAlex processing complete: {result.relevant_records:,} relevant records in {(result.end_time - result.start_time).total_seconds():.1f} seconds")

        return result

class TEDProcessor:
    """
    Process 24GB TED procurement data for supply chain analysis
    Focus on technology procurement and Chinese supplier involvement
    """

    def __init__(self, base_path: str = "F:/TED_Data"):
        self.base_path = Path(base_path)
        self.output_dir = Path("data/processed/ted_systematic")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Technology-related CPV codes (Common Procurement Vocabulary)
        self.tech_cpv_codes = {
            "30200000": "Computer equipment and supplies",
            "32000000": "Radio, television, communication, telecommunication equipment",
            "38000000": "Laboratory, optical and precision equipments",
            "48000000": "Software and information systems",
            "72000000": "IT services",
            "73000000": "Research and development services"
        }

        self.stats = defaultdict(int)

    def extract_supplier_info(self, contract: Dict) -> Dict:
        """
        Extract supplier information and identify potential China connections
        """
        supplier_info = {
            "contract_id": contract.get("id", ""),
            "title": contract.get("title", ""),
            "buyer_country": contract.get("buyer", {}).get("country", ""),
            "value_eur": contract.get("value", {}).get("amount", 0),
            "cpv_codes": contract.get("cpv_codes", []),
            "suppliers": [],
            "has_chinese_supplier": False,
            "technology_related": False
        }

        # Check if technology-related
        for cpv in supplier_info["cpv_codes"]:
            if any(cpv.startswith(tech_code) for tech_code in self.tech_cpv_codes.keys()):
                supplier_info["technology_related"] = True
                break

        # Extract supplier details
        for supplier in contract.get("suppliers", []):
            supplier_country = supplier.get("country", "")
            supplier_name = supplier.get("name", "")

            supplier_info["suppliers"].append({
                "name": supplier_name,
                "country": supplier_country
            })

            # Check for Chinese suppliers
            if supplier_country in ["CN", "CHN"]:
                supplier_info["has_chinese_supplier"] = True

            # Check for Chinese company names (basic heuristic)
            chinese_indicators = ["huawei", "zte", "xiaomi", "lenovo", "alibaba", "tencent"]
            if any(indicator in supplier_name.lower() for indicator in chinese_indicators):
                supplier_info["has_chinese_supplier"] = True

        return supplier_info

    def process_monthly_data(self, country_code: str = "DE") -> ProcessingResult:
        """
        Process TED monthly archives for specific country
        """
        start_time = datetime.now()
        result = ProcessingResult(
            dataset="TED",
            records_processed=0,
            relevant_records=0,
            errors=0,
            start_time=start_time,
            end_time=None,
            output_files=[],
            key_findings=[]
        )

        # Find monthly directories
        monthly_dirs = [d for d in self.base_path.iterdir() if d.is_dir() and "monthly" in d.name.lower()]
        logging.info(f"Found {len(monthly_dirs)} TED monthly archives")

        supply_chain_file = self.output_dir / f"supply_chain_{country_code}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        tech_procurement_file = self.output_dir / f"tech_procurement_{country_code}_{datetime.now().strftime('%Y%m%d')}.json"

        all_contracts = []
        tech_procurement_stats = defaultdict(lambda: {"count": 0, "total_value": 0, "chinese_suppliers": 0})

        # Process first monthly directory as demo
        for monthly_dir in monthly_dirs[:1]:
            logging.info(f"Processing {monthly_dir.name}")

            # Look for JSON or CSV files
            data_files = list(monthly_dir.glob("*.json")) + list(monthly_dir.glob("*.csv"))

            for data_file in data_files[:5]:  # Process first 5 files for demo
                logging.info(f"Processing {data_file.name}")

                try:
                    if data_file.suffix == ".json":
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            contracts = data if isinstance(data, list) else [data]
                    elif data_file.suffix == ".csv":
                        contracts = []
                        with open(data_file, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            contracts = list(reader)

                    for contract in contracts:
                        result.records_processed += 1

                        # Extract supplier information
                        supplier_info = self.extract_supplier_info(contract)

                        # Filter for relevant country
                        if supplier_info["buyer_country"] == country_code:
                            result.relevant_records += 1

                            if supplier_info["technology_related"]:
                                all_contracts.append(supplier_info)

                                # Update statistics
                                for cpv in supplier_info["cpv_codes"]:
                                    for tech_code, tech_name in self.tech_cpv_codes.items():
                                        if cpv.startswith(tech_code):
                                            tech_procurement_stats[tech_name]["count"] += 1
                                            tech_procurement_stats[tech_name]["total_value"] += supplier_info["value_eur"]
                                            if supplier_info["has_chinese_supplier"]:
                                                tech_procurement_stats[tech_name]["chinese_suppliers"] += 1

                except Exception as e:
                    logging.error(f"Error processing {data_file}: {e}")
                    result.errors += 1

        # Write supply chain data
        with open(supply_chain_file, 'w', encoding='utf-8') as f:
            for contract in all_contracts:
                json.dump(contract, f)
                f.write('\n')

        # Write technology procurement statistics
        with open(tech_procurement_file, 'w', encoding='utf-8') as f:
            json.dump(dict(tech_procurement_stats), f, indent=2)

        # Generate key findings
        total_tech_contracts = sum(stats["count"] for stats in tech_procurement_stats.values())
        total_chinese_suppliers = sum(stats["chinese_suppliers"] for stats in tech_procurement_stats.values())

        result.key_findings = [
            f"Processed {result.records_processed:,} TED contracts",
            f"Found {result.relevant_records:,} contracts for {country_code}",
            f"Identified {total_tech_contracts} technology procurement contracts",
            f"Found {total_chinese_suppliers} contracts with Chinese suppliers"
        ]

        if tech_procurement_stats:
            top_category = max(tech_procurement_stats.keys(),
                             key=lambda k: tech_procurement_stats[k]["count"])
            result.key_findings.append(f"Top procurement category: {top_category}")

        result.output_files = [str(supply_chain_file), str(tech_procurement_file)]
        result.end_time = datetime.now()

        logging.info(f"TED processing complete: {result.relevant_records:,} relevant records in {(result.end_time - result.start_time).total_seconds():.1f} seconds")

        return result

class DataProcessingOrchestrator:
    """
    Orchestrate processing of all datasets systematically
    """

    def __init__(self):
        self.results_dir = Path("data/processed/orchestrated_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.processing_results = []

    def process_all_datasets(self, target_country: str = "Germany", country_code: str = "DE"):
        """
        Process all available datasets for target country
        """
        logging.info(f"\n{'='*60}")
        logging.info(f"SYSTEMATIC DATA PROCESSING FOR {target_country}")
        logging.info(f"{'='*60}\n")

        start_time = datetime.now()

        # 1. Process OpenAlex (420GB)
        logging.info("\n[1/2] Processing OpenAlex Academic Data (420GB)...")
        logging.info("-" * 40)
        try:
            openalex_processor = OpenAlexProcessor()
            openalex_result = openalex_processor.process_batch(target_country)
            self.processing_results.append(openalex_result)

            for finding in openalex_result.key_findings:
                logging.info(f"  - {finding}")
        except Exception as e:
            logging.error(f"OpenAlex processing failed: {e}")

        # 2. Process TED (24GB)
        logging.info("\n[2/2] Processing TED Procurement Data (24GB)...")
        logging.info("-" * 40)
        try:
            ted_processor = TEDProcessor()
            ted_result = ted_processor.process_monthly_data(country_code)
            self.processing_results.append(ted_result)

            for finding in ted_result.key_findings:
                logging.info(f"  - {finding}")
        except Exception as e:
            logging.error(f"TED processing failed: {e}")

        # Generate consolidated report
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        report = {
            "processing_date": datetime.now().isoformat(),
            "target_country": target_country,
            "country_code": country_code,
            "total_duration_seconds": duration,
            "datasets_processed": len(self.processing_results),
            "total_records": sum(r.records_processed for r in self.processing_results),
            "relevant_records": sum(r.relevant_records for r in self.processing_results),
            "processing_results": [
                {
                    "dataset": r.dataset,
                    "records_processed": r.records_processed,
                    "relevant_records": r.relevant_records,
                    "errors": r.errors,
                    "duration": (r.end_time - r.start_time).total_seconds() if r.end_time else 0,
                    "output_files": r.output_files,
                    "key_findings": r.key_findings
                }
                for r in self.processing_results
            ]
        }

        # Save consolidated report
        report_file = self.results_dir / f"processing_report_{country_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        logging.info(f"\n{'='*60}")
        logging.info("PROCESSING COMPLETE")
        logging.info(f"{'='*60}")
        logging.info(f"Total records processed: {report['total_records']:,}")
        logging.info(f"Relevant records found: {report['relevant_records']:,}")
        logging.info(f"Processing time: {duration:.1f} seconds")
        logging.info(f"Report saved to: {report_file}")

        return report

def main():
    """
    Main entry point for systematic data processing
    """
    print("\n" + "="*80)
    print("SYSTEMATIC DATA PROCESSOR")
    print("Processing 445GB of orphaned data through validated framework")
    print("="*80 + "\n")

    # Initialize orchestrator
    orchestrator = DataProcessingOrchestrator()

    # Process all datasets for Germany
    report = orchestrator.process_all_datasets("Germany", "DE")

    print("\n" + "="*80)
    print("DATA PROCESSING SUMMARY")
    print("="*80)
    print(f"\nDatasets processed: {report['datasets_processed']}")
    print(f"Total records: {report['total_records']:,}")
    print(f"Relevant records: {report['relevant_records']:,}")
    print(f"Processing time: {report['total_duration_seconds']:.1f} seconds")

    print("\nKEY FINDINGS:")
    print("-" * 40)
    for result in report['processing_results']:
        print(f"\n{result['dataset']}:")
        for finding in result['key_findings']:
            print(f"  - {finding}")

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Process remaining OpenAlex files (419GB)")
    print("2. Process remaining TED monthly archives (23GB)")
    print("3. Connect processed data to phase framework")
    print("4. Generate phase-specific outputs")
    print("5. Run full country analysis with processed data")

if __name__ == "__main__":
    main()
