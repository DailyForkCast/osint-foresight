"""
TED Germany Contract Extractor
Processes 23GB of TED procurement data to extract German contracts
Focuses on defense, technology, and China-linked suppliers
"""

import os
import json
import csv
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TEDGermanyExtractor:
    """Extract and analyze German contracts from TED data"""

    def __init__(self):
        self.ted_path = Path("F:/TED_Data/monthly")
        self.output_dir = Path("F:/OSINT_DATA/Germany_Analysis/TED_Contracts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Critical CPV codes for technology and defense
        self.critical_cpv_codes = {
            "30000000": "Office and computing machinery",
            "30200000": "Computer equipment and supplies",
            "32000000": "Radio, TV, communication",
            "34000000": "Transport equipment",
            "34700000": "Aircraft and spacecraft",
            "35000000": "Security, safety, police and defence",
            "38000000": "Laboratory equipment",
            "45000000": "Construction work",
            "48000000": "Software package",
            "50000000": "Repair and maintenance",
            "64200000": "Telecommunications",
            "71000000": "Architectural and engineering",
            "72000000": "IT services",
            "73000000": "Research and development"
        }

        # China-related keywords
        self.china_indicators = [
            "huawei", "zte", "hikvision", "dahua", "china", "chinese",
            "beijing", "shanghai", "shenzhen", "alibaba", "tencent",
            "lenovo", "xiaomi", "dji", "bytedance"
        ]

        # German organizations to track
        self.german_entities = [
            "bundeswehr", "fraunhofer", "siemens", "sap", "deutsche bahn",
            "lufthansa", "bmw", "volkswagen", "mercedes", "bosch",
            "infineon", "deutsche telekom", "bayer", "basf", "thyssenkrupp"
        ]

        self.results = {
            "total_contracts": 0,
            "german_contracts": 0,
            "critical_contracts": 0,
            "china_linked": 0,
            "contracts": []
        }

    def process_ted_data(self, start_year: int = 2020, end_year: int = 2024):
        """Process TED data for specified years"""
        logger.info(f"Processing TED data from {start_year} to {end_year}")

        for year in range(start_year, end_year + 1):
            year_path = self.ted_path / str(year)
            if not year_path.exists():
                logger.warning(f"Year {year} directory not found")
                continue

            logger.info(f"Processing year {year}")
            self.process_year(year_path, year)

        # Save results
        self.save_results()
        self.print_summary()

    def process_year(self, year_path: Path, year: int):
        """Process all months in a year"""
        for month in range(1, 13):
            month_str = f"{month:02d}"
            month_path = year_path / month_str

            if not month_path.exists():
                continue

            logger.info(f"Processing {year}/{month_str}")

            # Process all files in month directory
            for file_path in month_path.iterdir():
                if file_path.suffix in ['.xml', '.json', '.csv', '.zip']:
                    self.process_file(file_path)

    def process_file(self, file_path: Path):
        """Process individual TED file"""
        try:
            if file_path.suffix == '.zip':
                self.process_zip(file_path)
            elif file_path.suffix == '.xml':
                self.process_xml(file_path)
            elif file_path.suffix == '.json':
                self.process_json(file_path)
            elif file_path.suffix == '.csv':
                self.process_csv(file_path)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    def process_xml(self, file_path: Path):
        """Process XML TED file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract contract information
            contract = self.extract_contract_info_xml(root)
            if contract:
                self.analyze_contract(contract)

        except Exception as e:
            logger.debug(f"XML processing error for {file_path}: {e}")

    def extract_contract_info_xml(self, root: ET.Element) -> Dict:
        """Extract contract information from XML"""
        contract = {}

        # Common TED XML structure
        try:
            # Try to find country
            country = root.find(".//COUNTRY")
            if country is not None and country.text == "DE":
                contract["country"] = "Germany"

            # CPV codes
            cpv = root.find(".//CPV_MAIN//CPV_CODE")
            if cpv is not None:
                contract["cpv_code"] = cpv.get("CODE", "")

            # Contract title
            title = root.find(".//TITLE")
            if title is not None:
                contract["title"] = title.text

            # Contracting authority
            authority = root.find(".//CONTRACTING_BODY//OFFICIALNAME")
            if authority is not None:
                contract["authority"] = authority.text

            # Winner/supplier
            winner = root.find(".//AWARDED_CONTRACT//CONTRACTOR//OFFICIALNAME")
            if winner is not None:
                contract["supplier"] = winner.text

            # Value
            value = root.find(".//VAL_TOTAL")
            if value is not None:
                contract["value"] = value.text

            # Date
            date = root.find(".//DATE_PUB")
            if date is not None:
                contract["date"] = date.text

            return contract if contract.get("country") == "Germany" else None

        except:
            return None

    def process_json(self, file_path: Path):
        """Process JSON TED file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                for item in data:
                    contract = self.extract_contract_info_json(item)
                    if contract:
                        self.analyze_contract(contract)
            else:
                contract = self.extract_contract_info_json(data)
                if contract:
                    self.analyze_contract(contract)

        except Exception as e:
            logger.debug(f"JSON processing error for {file_path}: {e}")

    def extract_contract_info_json(self, data: Dict) -> Dict:
        """Extract contract information from JSON"""
        contract = {}

        # Check if German contract
        country = data.get("country", data.get("buyer_country", ""))
        if "DE" in country or "Germany" in country:
            contract["country"] = "Germany"
            contract["cpv_code"] = data.get("cpv_code", data.get("cpv", ""))
            contract["title"] = data.get("title", data.get("contract_title", ""))
            contract["authority"] = data.get("buyer_name", data.get("contracting_authority", ""))
            contract["supplier"] = data.get("winner_name", data.get("supplier", ""))
            contract["value"] = data.get("value", data.get("contract_value", 0))
            contract["date"] = data.get("publication_date", data.get("date", ""))

            return contract

        return None

    def process_csv(self, file_path: Path):
        """Process CSV TED file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    contract = self.extract_contract_info_csv(row)
                    if contract:
                        self.analyze_contract(contract)

        except Exception as e:
            logger.debug(f"CSV processing error for {file_path}: {e}")

    def extract_contract_info_csv(self, row: Dict) -> Dict:
        """Extract contract information from CSV row"""
        contract = {}

        # Check various possible column names
        country = row.get("country", row.get("ISO_COUNTRY_CODE", row.get("buyer_country", "")))

        if "DE" in country or "Germany" in str(country):
            contract["country"] = "Germany"
            contract["cpv_code"] = row.get("cpv", row.get("CPV_CODE", ""))
            contract["title"] = row.get("title", row.get("TITLE", ""))
            contract["authority"] = row.get("buyer", row.get("AUTHORITY_NAME", ""))
            contract["supplier"] = row.get("supplier", row.get("WINNER", ""))
            contract["value"] = row.get("value", row.get("VALUE_EUR", 0))
            contract["date"] = row.get("date", row.get("PUBLICATION_DATE", ""))

            return contract

        return None

    def process_zip(self, file_path: Path):
        """Process ZIP file containing TED data"""
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                for file_info in z.namelist():
                    # Extract to temp and process
                    if file_info.endswith(('.xml', '.json', '.csv')):
                        with z.open(file_info) as f:
                            content = f.read()
                            # Process based on file type
                            temp_file = self.output_dir / f"temp_{file_info}"
                            temp_file.write_bytes(content)

                            if file_info.endswith('.xml'):
                                self.process_xml(temp_file)
                            elif file_info.endswith('.json'):
                                self.process_json(temp_file)
                            elif file_info.endswith('.csv'):
                                self.process_csv(temp_file)

                            temp_file.unlink()  # Clean up temp file

        except Exception as e:
            logger.debug(f"ZIP processing error for {file_path}: {e}")

    def analyze_contract(self, contract: Dict):
        """Analyze contract for critical indicators"""
        if not contract:
            return

        self.results["total_contracts"] += 1

        # German contract
        if contract.get("country") == "Germany":
            self.results["german_contracts"] += 1

            # Check if critical CPV code
            cpv_code = str(contract.get("cpv_code", ""))[:8]
            if cpv_code in self.critical_cpv_codes:
                contract["critical"] = True
                contract["cpv_description"] = self.critical_cpv_codes[cpv_code]
                self.results["critical_contracts"] += 1

            # Check for China links
            contract_str = json.dumps(contract).lower()
            china_linked = False
            for indicator in self.china_indicators:
                if indicator in contract_str:
                    china_linked = True
                    contract["china_indicator"] = indicator
                    break

            if china_linked:
                self.results["china_linked"] += 1
                contract["china_risk"] = "HIGH"

            # Store significant contracts
            if contract.get("critical") or china_linked:
                self.results["contracts"].append(contract)

    def save_results(self):
        """Save analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed contracts
        contracts_file = self.output_dir / f"germany_contracts_{timestamp}.json"
        with open(contracts_file, 'w', encoding='utf-8') as f:
            json.dump(self.results["contracts"], f, indent=2, ensure_ascii=False)

        # Save summary
        summary = {
            "analysis_date": datetime.now().isoformat(),
            "data_source": "TED Europa (23GB)",
            "years_analyzed": "2020-2024",
            "statistics": {
                "total_contracts_processed": self.results["total_contracts"],
                "german_contracts": self.results["german_contracts"],
                "critical_technology_contracts": self.results["critical_contracts"],
                "china_linked_contracts": self.results["china_linked"],
                "critical_cpv_codes": list(self.critical_cpv_codes.keys())
            },
            "key_findings": self.generate_key_findings(),
            "recommendations": [
                "Deep dive into China-linked suppliers",
                "Review all critical technology procurements",
                "Map supplier networks for dual-use items",
                "Establish monitoring for sensitive procurements"
            ]
        }

        summary_file = self.output_dir / f"germany_ted_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to {self.output_dir}")

    def generate_key_findings(self) -> List[str]:
        """Generate key findings from analysis"""
        findings = []

        if self.results["german_contracts"] > 0:
            findings.append(f"Analyzed {self.results['german_contracts']} German contracts")

        if self.results["critical_contracts"] > 0:
            findings.append(f"{self.results['critical_contracts']} contracts in critical technology sectors")

        if self.results["china_linked"] > 0:
            findings.append(f"{self.results['china_linked']} contracts with potential China links")
            china_rate = (self.results["china_linked"] / self.results["german_contracts"] * 100)
            findings.append(f"China involvement rate: {china_rate:.2f}%")

        # Top CPV categories
        cpv_counts = {}
        for contract in self.results["contracts"]:
            cpv = contract.get("cpv_code", "")[:8]
            cpv_counts[cpv] = cpv_counts.get(cpv, 0) + 1

        if cpv_counts:
            top_cpv = sorted(cpv_counts.items(), key=lambda x: x[1], reverse=True)[0]
            findings.append(f"Most common critical category: {self.critical_cpv_codes.get(top_cpv[0], top_cpv[0])}")

        return findings

    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "="*60)
        print("TED GERMANY CONTRACT ANALYSIS")
        print("="*60)
        print(f"\nData Source: 23GB TED Europa procurement data")
        print(f"Total Contracts Processed: {self.results['total_contracts']}")
        print(f"German Contracts: {self.results['german_contracts']}")
        print(f"Critical Technology Contracts: {self.results['critical_contracts']}")
        print(f"China-Linked Contracts: {self.results['china_linked']}")

        if self.results["german_contracts"] > 0:
            china_rate = (self.results["china_linked"] / self.results["german_contracts"] * 100)
            print(f"China Involvement Rate: {china_rate:.2f}%")

        print("\nKey Risk Areas:")
        for cpv_code, description in self.critical_cpv_codes.items():
            count = sum(1 for c in self.results["contracts"]
                       if str(c.get("cpv_code", ""))[:8] == cpv_code)
            if count > 0:
                print(f"  - {description}: {count} contracts")

        print("\n" + "="*60)


if __name__ == "__main__":
    print("[TED GERMANY CONTRACT EXTRACTOR]")
    print("Processing 23GB of TED procurement data...")
    print("This will take several hours to complete\n")

    extractor = TEDGermanyExtractor()

    # Process recent years first (most relevant)
    extractor.process_ted_data(start_year=2022, end_year=2024)

    print("\n[EXTRACTION COMPLETE]")
    print(f"Results saved to: F:/OSINT_DATA/Germany_Analysis/TED_Contracts/")
    print("Next step: Analyze China-linked suppliers and technology transfers")
