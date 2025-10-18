#!/usr/bin/env python3
"""
TED EU Procurement Data Processor
Processes 25GB of TED procurement data to identify Italy-China relationships
and dual-use technology transfers.
"""

import os
import json
import tarfile
import xml.etree.ElementTree as ET
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing
from dataclasses import dataclass, asdict
import tempfile
import shutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ted_processing.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class Contract:
    """TED Contract data structure"""
    contract_id: str
    title: str
    contracting_authority: str
    authority_country: str
    winners: List[Dict]
    value: float
    currency: str
    cpv_codes: List[str]
    date: str
    description: str
    technology_flags: List[str]
    source_file: str
    xml_path: str

class TEDProcessor:
    """
    Streaming processor for TED procurement data
    Focuses on Italy-China relationships and dual-use technology
    """

    def __init__(self, data_dir: str = "F:/TED_Data", output_dir: str = "data/processed/ted"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.checkpoint_file = self.output_dir / "checkpoint.json"
        self.temp_dir = Path("data/temp/ted_extraction")

        # Create output directories
        for subdir in ["contracts", "summaries", "italy_china", "technology", "temp"]:
            (self.output_dir / subdir).mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Search patterns
        self.italy_patterns = [
            "Italy", "Italia", "Italian", "Italiana", "Italiano",
            "Rome", "Roma", "Milan", "Milano", "Turin", "Torino"
        ]

        self.china_patterns = [
            "China", "Chinese", "Cina", "Cinese",
            "Huawei", "ZTE", "Xiaomi", "Lenovo", "BYD",
            "CRRC", "State Grid", "CATL", "Alibaba", "Tencent",
            "Beijing", "Shanghai", "Shenzhen", "Guangzhou"
        ]

        # Critical entities to track
        self.critical_chinese = {
            "huawei": ["Huawei", "华为"],
            "zte": ["ZTE", "中兴"],
            "crrc": ["CRRC", "中国中车"],
            "state_grid": ["State Grid", "国家电网"],
            "cnnc": ["China National Nuclear", "中国核工业"],
            "casic": ["China Aerospace", "航天科工"]
        }

        self.critical_italian = {
            "leonardo": ["Leonardo", "Finmeccanica"],
            "eni": ["ENI", "Ente Nazionale Idrocarburi"],
            "enel": ["Enel", "Ente nazionale per l'energia elettrica"],
            "tim": ["TIM", "Telecom Italia"],
            "fs": ["Ferrovie dello Stato", "Trenitalia"],
            "terna": ["Terna"]
        }

        # Technology keywords for dual-use identification
        self.tech_keywords = {
            "telecom": ["5G", "telecommunication", "network", "fiber optic", "wireless"],
            "semiconductor": ["chip", "semiconductor", "microelectronics", "integrated circuit"],
            "nuclear": ["nuclear", "reactor", "uranium", "enrichment"],
            "aerospace": ["satellite", "spacecraft", "aerospace", "launch vehicle"],
            "ai": ["artificial intelligence", "AI", "machine learning", "neural network"],
            "renewable": ["solar", "wind", "renewable", "photovoltaic", "battery storage"],
            "rail": ["railway", "high-speed rail", "signaling", "rolling stock"],
            "port": ["port", "terminal", "container", "maritime"],
            "critical_infra": ["power grid", "water supply", "telecommunications network"]
        }

        # Dual-use CPV codes (Common Procurement Vocabulary)
        self.dual_use_cpv = {
            "32400000": "Networks",
            "31700000": "Electronic equipment",
            "35100000": "Emergency and security equipment",
            "38000000": "Laboratory equipment",
            "30200000": "Computer equipment",
            "31600000": "Electrical equipment",
            "42000000": "Industrial machinery",
            "34600000": "Railway equipment"
        }

        # Load checkpoint if exists
        self.checkpoint = self.load_checkpoint()
        self.stats = {
            "total_contracts": 0,
            "italy_contracts": 0,
            "china_contracts": 0,
            "italy_china_contracts": 0,
            "technology_relevant": 0,
            "total_value_eur": 0.0
        }

    def load_checkpoint(self) -> Dict:
        """Load processing checkpoint for resumability"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                logging.info(f"Loaded checkpoint: {checkpoint['files_processed']} files processed")
                return checkpoint
        return {
            "last_file": None,
            "files_processed": [],
            "contracts_found": 0,
            "italy_china_found": 0,
            "processing_time": 0,
            "started": datetime.now().isoformat()
        }

    def save_checkpoint(self):
        """Save processing checkpoint"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def get_all_archives(self) -> List[Path]:
        """Get all TED archive files sorted by date"""
        monthly_dir = self.data_dir / "monthly"
        archives = []

        for year_dir in sorted(monthly_dir.iterdir()):
            if year_dir.is_dir():
                for archive in sorted(year_dir.glob("*.tar.gz")):
                    archives.append(archive)

        logging.info(f"Found {len(archives)} archive files to process")
        return archives

    def extract_contract_from_xml(self, xml_content: str, source_file: str) -> Optional[Contract]:
        """Extract contract details from TED XML"""
        try:
            root = ET.fromstring(xml_content)

            # Extract basic info (simplified - actual TED XML is complex)
            contract_id = root.findtext(".//NOTICE_ID", "")
            title = root.findtext(".//TITLE", "")

            # Contracting authority
            authority = root.findtext(".//NAME_ADDRESS_CONTACT/ORGANISATION", "")
            country = root.findtext(".//NAME_ADDRESS_CONTACT/COUNTRY", "")

            # Winners (may be multiple)
            winners = []
            for winner in root.findall(".//AWARD_OF_CONTRACT/ECONOMIC_OPERATOR"):
                winner_data = {
                    "name": winner.findtext("ORGANISATION", ""),
                    "country": winner.findtext("COUNTRY", ""),
                    "address": winner.findtext("ADDRESS", "")
                }
                winners.append(winner_data)

            # Value
            value_elem = root.find(".//COSTS_RANGE_AND_CURRENCY_WITH_VAT")
            value = 0.0
            currency = "EUR"
            if value_elem is not None:
                value_text = value_elem.findtext("VALUE_COST", "0")
                try:
                    value = float(value_text.replace(",", ""))
                except:
                    value = 0.0
                currency = value_elem.findtext("CURRENCY", "EUR")

            # CPV codes
            cpv_codes = []
            for cpv in root.findall(".//CPV_MAIN/CPV_CODE"):
                code = cpv.get("CODE", "")
                if code:
                    cpv_codes.append(code)

            # Date
            date = root.findtext(".//DATE_DISPATCH_NOTICE", "")

            # Description
            description = root.findtext(".//SHORT_DESCRIPTION", "")

            # Identify technology flags
            tech_flags = self.identify_technology_categories(
                title + " " + description if description else title
            )

            return Contract(
                contract_id=contract_id,
                title=title,
                contracting_authority=authority,
                authority_country=country,
                winners=winners,
                value=value,
                currency=currency,
                cpv_codes=cpv_codes,
                date=date,
                description=description,
                technology_flags=tech_flags,
                source_file=source_file,
                xml_path=""
            )

        except Exception as e:
            logging.debug(f"Error parsing XML: {e}")
            return None

    def identify_technology_categories(self, text: str) -> List[str]:
        """Identify technology categories from text"""
        text_lower = text.lower()
        categories = []

        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    categories.append(category)
                    break

        return categories

    def is_italy_china_contract(self, contract: Contract) -> Tuple[bool, str, List[str]]:
        """
        Check if contract involves Italy and China
        Returns: (is_match, direction, evidence)
        """
        evidence = []

        # Check if Italian contracting authority
        is_italian_authority = False
        if contract.authority_country in ["IT", "ITA", "Italy"]:
            is_italian_authority = True
            evidence.append(f"Italian authority: {contract.contracting_authority}")
        else:
            # Check patterns in authority name
            for pattern in self.italy_patterns:
                if pattern.lower() in contract.contracting_authority.lower():
                    is_italian_authority = True
                    evidence.append(f"Italian pattern in authority: {pattern}")
                    break

        # Check for Chinese winners
        chinese_winners = []
        for winner in contract.winners:
            # Check country code
            if winner.get("country") in ["CN", "CHN", "China"]:
                chinese_winners.append(winner["name"])
                evidence.append(f"Chinese winner: {winner['name']}")
            else:
                # Check patterns in winner name
                for pattern in self.china_patterns:
                    if pattern.lower() in winner.get("name", "").lower():
                        chinese_winners.append(winner["name"])
                        evidence.append(f"Chinese pattern in winner: {pattern}")
                        break

        # Determine direction
        if is_italian_authority and chinese_winners:
            return True, "IT->CN", evidence

        # Check reverse (Chinese authority, Italian winner) - rare but possible
        is_chinese_authority = contract.authority_country in ["CN", "CHN", "China"]
        italian_winners = []
        for winner in contract.winners:
            if winner.get("country") in ["IT", "ITA", "Italy"]:
                italian_winners.append(winner["name"])
                evidence.append(f"Italian winner: {winner['name']}")

        if is_chinese_authority and italian_winners:
            return True, "CN->IT", evidence

        return False, "", []

    def process_xml_file(self, xml_content: str, filename: str, archive_path: str) -> Optional[Dict]:
        """Process individual XML file"""
        contract = self.extract_contract_from_xml(xml_content, str(archive_path))

        if not contract:
            return None

        self.stats["total_contracts"] += 1

        # Check Italy involvement
        if contract.authority_country in ["IT", "ITA", "Italy"]:
            self.stats["italy_contracts"] += 1

        # Check China involvement
        for winner in contract.winners:
            if winner.get("country") in ["CN", "CHN", "China"]:
                self.stats["china_contracts"] += 1
                break

        # Check Italy-China connection
        is_match, direction, evidence = self.is_italy_china_contract(contract)

        if is_match:
            self.stats["italy_china_contracts"] += 1

            # Create detailed finding
            finding = {
                "contract": asdict(contract),
                "direction": direction,
                "evidence": evidence,
                "confidence": 0.95 if contract.authority_country in ["IT", "ITA"] else 0.85,
                "verification": {
                    "source_file": str(archive_path),
                    "xml_file": filename,
                    "extract_command": f"tar -xzf '{archive_path}' -O '{filename}' | grep -i 'china'",
                    "timestamp": datetime.now().isoformat()
                }
            }

            # Check for critical entities
            for entity_key, patterns in self.critical_chinese.items():
                for pattern in patterns:
                    if pattern.lower() in str(contract.winners).lower():
                        finding["critical_entity"] = entity_key
                        finding["risk_level"] = "HIGH"
                        break

            # Check technology relevance
            if contract.technology_flags:
                self.stats["technology_relevant"] += 1
                finding["technology_categories"] = contract.technology_flags

            # Check if dual-use CPV code
            for cpv in contract.cpv_codes:
                if cpv[:8] in self.dual_use_cpv:
                    finding["dual_use"] = True
                    finding["dual_use_category"] = self.dual_use_cpv[cpv[:8]]

            # Add value
            if contract.value > 0:
                self.stats["total_value_eur"] += contract.value

            return finding

        return None

    def process_archive(self, archive_path: Path) -> Dict:
        """Process single monthly archive"""
        logging.info(f"Processing: {archive_path}")
        start_time = datetime.now()

        # Skip if already processed
        if str(archive_path) in self.checkpoint["files_processed"]:
            logging.info(f"Skipping already processed: {archive_path}")
            return {"skipped": True}

        findings = []
        temp_extract = self.temp_dir / archive_path.stem

        try:
            # Extract archive to temp directory
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(temp_extract)

            # Process all XML files
            xml_files = list(temp_extract.rglob("*.xml"))
            logging.info(f"Found {len(xml_files)} XML files in {archive_path.name}")

            for xml_file in xml_files:
                try:
                    with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
                        xml_content = f.read()

                    finding = self.process_xml_file(
                        xml_content,
                        xml_file.name,
                        archive_path
                    )

                    if finding:
                        findings.append(finding)

                except Exception as e:
                    logging.debug(f"Error processing {xml_file}: {e}")
                    continue

            # Save findings
            if findings:
                output_file = self.output_dir / "italy_china" / f"{archive_path.stem}_findings.json"
                with open(output_file, 'w') as f:
                    json.dump(findings, f, indent=2)
                logging.info(f"Found {len(findings)} Italy-China contracts in {archive_path.name}")

            # Update checkpoint
            self.checkpoint["files_processed"].append(str(archive_path))
            self.checkpoint["contracts_found"] += len(xml_files)
            self.checkpoint["italy_china_found"] += len(findings)
            self.checkpoint["last_file"] = str(archive_path)
            self.save_checkpoint()

        except Exception as e:
            logging.error(f"Error processing archive {archive_path}: {e}")
            return {"error": str(e)}

        finally:
            # Cleanup temp files
            if temp_extract.exists():
                shutil.rmtree(temp_extract)

        processing_time = (datetime.now() - start_time).total_seconds()

        return {
            "archive": str(archive_path),
            "xml_files": len(xml_files) if 'xml_files' in locals() else 0,
            "findings": len(findings),
            "processing_time": processing_time
        }

    def process_year(self, year: int) -> Dict:
        """Process all archives for a specific year"""
        logging.info(f"Processing year: {year}")
        year_dir = self.data_dir / "monthly" / str(year)

        if not year_dir.exists():
            logging.warning(f"Year directory not found: {year_dir}")
            return {"year": year, "error": "Directory not found"}

        year_findings = []
        archives = sorted(year_dir.glob("*.tar.gz"))

        for archive in archives:
            result = self.process_archive(archive)
            if not result.get("skipped"):
                year_findings.append(result)

        # Save year summary
        summary = {
            "year": year,
            "archives_processed": len(year_findings),
            "total_findings": sum(r.get("findings", 0) for r in year_findings),
            "processing_time": sum(r.get("processing_time", 0) for r in year_findings),
            "stats": dict(self.stats)
        }

        summary_file = self.output_dir / "summaries" / f"year_{year}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def generate_report(self):
        """Generate final analysis report"""
        logging.info("Generating final report...")

        # Collect all findings
        all_findings = []
        for finding_file in (self.output_dir / "italy_china").glob("*.json"):
            with open(finding_file, 'r') as f:
                findings = json.load(f)
                all_findings.extend(findings)

        # Analysis
        report = {
            "processing_summary": {
                "total_contracts_analyzed": self.stats["total_contracts"],
                "italy_contracts": self.stats["italy_contracts"],
                "china_contracts": self.stats["china_contracts"],
                "italy_china_contracts": self.stats["italy_china_contracts"],
                "technology_relevant": self.stats["technology_relevant"],
                "total_value_eur": self.stats["total_value_eur"]
            },
            "findings_summary": {
                "total_italy_china": len(all_findings),
                "it_to_cn": len([f for f in all_findings if f.get("direction") == "IT->CN"]),
                "cn_to_it": len([f for f in all_findings if f.get("direction") == "CN->IT"]),
                "dual_use": len([f for f in all_findings if f.get("dual_use")]),
                "critical_entities": len([f for f in all_findings if f.get("critical_entity")])
            },
            "technology_breakdown": {},
            "temporal_analysis": {},
            "top_chinese_winners": {},
            "top_italian_authorities": {},
            "critical_findings": []
        }

        # Technology breakdown
        tech_counts = {}
        for finding in all_findings:
            for tech in finding.get("technology_categories", []):
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
        report["technology_breakdown"] = tech_counts

        # Temporal analysis
        yearly_counts = {}
        for finding in all_findings:
            year = finding["contract"]["date"][:4] if finding["contract"]["date"] else "Unknown"
            yearly_counts[year] = yearly_counts.get(year, 0) + 1
        report["temporal_analysis"] = yearly_counts

        # Top entities
        chinese_winners = {}
        italian_authorities = {}

        for finding in all_findings:
            # Chinese winners
            for winner in finding["contract"]["winners"]:
                if winner.get("country") in ["CN", "CHN", "China"]:
                    name = winner["name"]
                    chinese_winners[name] = chinese_winners.get(name, 0) + 1

            # Italian authorities
            if finding["contract"]["authority_country"] in ["IT", "ITA", "Italy"]:
                auth = finding["contract"]["contracting_authority"]
                italian_authorities[auth] = italian_authorities.get(auth, 0) + 1

        # Sort and limit to top 10
        report["top_chinese_winners"] = dict(sorted(chinese_winners.items(),
                                                    key=lambda x: x[1],
                                                    reverse=True)[:10])
        report["top_italian_authorities"] = dict(sorted(italian_authorities.items(),
                                                        key=lambda x: x[1],
                                                        reverse=True)[:10])

        # Critical findings (high-value or critical entity)
        critical = []
        for finding in all_findings:
            if (finding.get("critical_entity") or
                finding.get("dual_use") or
                finding["contract"]["value"] > 10000000):
                critical.append({
                    "contract_id": finding["contract"]["contract_id"],
                    "title": finding["contract"]["title"],
                    "value": finding["contract"]["value"],
                    "critical_entity": finding.get("critical_entity"),
                    "dual_use": finding.get("dual_use"),
                    "technology": finding.get("technology_categories"),
                    "date": finding["contract"]["date"]
                })

        report["critical_findings"] = sorted(critical,
                                            key=lambda x: x["value"],
                                            reverse=True)[:20]

        # Save report
        report_file = self.output_dir / "TED_ITALY_CHINA_ANALYSIS_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Generate markdown summary
        self.generate_markdown_report(report)

        return report

    def generate_markdown_report(self, report: Dict):
        """Generate markdown format report"""
        md_content = f"""# TED Italy-China Procurement Analysis Report
Generated: {datetime.now().isoformat()}

## Executive Summary

- **Total Contracts Analyzed:** {report['processing_summary']['total_contracts']:,}
- **Italy Contracts:** {report['processing_summary']['italy_contracts']:,}
- **Italy-China Contracts Found:** {report['processing_summary']['italy_china_contracts']}
- **Total Value:** €{report['processing_summary']['total_value_eur']:,.2f}
- **Technology-Relevant:** {report['processing_summary']['technology_relevant']}

## Key Findings

### Direction of Procurement
- Italy → China: {report['findings_summary']['it_to_cn']} contracts
- China → Italy: {report['findings_summary']['cn_to_it']} contracts
- Dual-Use Technology: {report['findings_summary']['dual_use']} contracts
- Critical Entities Involved: {report['findings_summary']['critical_entities']} contracts

### Technology Categories
"""
        for tech, count in sorted(report['technology_breakdown'].items(),
                                  key=lambda x: x[1], reverse=True):
            md_content += f"- {tech}: {count} contracts\n"

        md_content += """
### Temporal Trends
"""
        for year in sorted(report['temporal_analysis'].keys()):
            md_content += f"- {year}: {report['temporal_analysis'][year]} contracts\n"

        md_content += """
### Top Chinese Winners
"""
        for company, count in list(report['top_chinese_winners'].items())[:5]:
            md_content += f"1. {company}: {count} contracts\n"

        md_content += """
### Top Italian Contracting Authorities
"""
        for authority, count in list(report['top_italian_authorities'].items())[:5]:
            md_content += f"1. {authority}: {count} contracts\n"

        md_content += """
### Critical Findings (High-Value or Strategic)
"""
        for finding in report['critical_findings'][:10]:
            md_content += f"""
**Contract:** {finding['contract_id']}
- Title: {finding['title']}
- Value: €{finding['value']:,.2f}
- Critical Entity: {finding.get('critical_entity', 'N/A')}
- Dual-Use: {finding.get('dual_use', False)}
- Technology: {', '.join(finding.get('technology', [])) if finding.get('technology') else 'N/A'}
- Date: {finding['date']}
---
"""

        md_content += """
## Verification

All findings can be verified using the provided extraction commands in the JSON output files.
Each contract is traceable to its source archive and XML file.
"""

        # Save markdown report
        md_file = self.output_dir / "TED_ITALY_CHINA_ANALYSIS_REPORT.md"
        with open(md_file, 'w') as f:
            f.write(md_content)

        logging.info(f"Report saved to {md_file}")

    def run(self, test_mode=False, years=None, parallel=False):
        """
        Main processing function

        Args:
            test_mode: Process only first archive for testing
            years: List of years to process (None = all)
            parallel: Use parallel processing
        """
        logging.info("=" * 50)
        logging.info("Starting TED Procurement Data Processing")
        logging.info(f"Data directory: {self.data_dir}")
        logging.info(f"Output directory: {self.output_dir}")
        logging.info("=" * 50)

        if test_mode:
            # Test mode - process only first archive
            archives = self.get_all_archives()
            if archives:
                result = self.process_archive(archives[0])
                logging.info(f"Test result: {result}")
            return

        if years:
            # Process specific years
            for year in years:
                self.process_year(year)
        else:
            # Process all archives
            archives = self.get_all_archives()

            # Skip already processed files
            remaining = [a for a in archives if str(a) not in self.checkpoint["files_processed"]]
            logging.info(f"Processing {len(remaining)} remaining archives...")

            if parallel and len(remaining) > 1:
                # Parallel processing
                num_workers = min(multiprocessing.cpu_count() - 1, 4)
                with ProcessPoolExecutor(max_workers=num_workers) as executor:
                    futures = [executor.submit(self.process_archive, archive)
                              for archive in remaining]
                    for future in futures:
                        result = future.result()
                        logging.info(f"Processed: {result}")
            else:
                # Sequential processing
                for archive in remaining:
                    self.process_archive(archive)

        # Generate final report
        self.generate_report()

        logging.info("=" * 50)
        logging.info("Processing Complete!")
        logging.info(f"Total Italy-China contracts found: {self.stats['italy_china_contracts']}")
        logging.info(f"Reports saved to: {self.output_dir}")
        logging.info("=" * 50)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Process TED procurement data")
    parser.add_argument("--test", action="store_true", help="Test mode - process first file only")
    parser.add_argument("--years", nargs="+", type=int, help="Specific years to process")
    parser.add_argument("--parallel", action="store_true", help="Use parallel processing")
    parser.add_argument("--data-dir", default="F:/TED_Data", help="TED data directory")
    parser.add_argument("--output-dir", default="data/processed/ted", help="Output directory")

    args = parser.parse_args()

    processor = TEDProcessor(data_dir=args.data_dir, output_dir=args.output_dir)
    processor.run(test_mode=args.test, years=args.years, parallel=args.parallel)


if __name__ == "__main__":
    main()
