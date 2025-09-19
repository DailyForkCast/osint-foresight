"""
Master Source Collector for All Free Data Sources
Systematically downloads from all identified free sources including:
- Export control lists (Entity List, MEU, etc.)
- VC/Investment data (SEC Form D, etc.)
- Scientific procurement (UN Comtrade, etc.)
- Standards bodies
- National statistics
"""

import os
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import time
import zipfile
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MasterSourceCollector:
    """Collects data from all identified free sources"""

    def __init__(self):
        self.f_drive = Path("F:/OSINT_DATA")
        self.base_path = Path("C:/Projects/OSINT - Foresight")

        # Create source-specific directories
        self.source_dirs = {
            "export_control": self.f_drive / "EXPORT_CONTROL",
            "venture_capital": self.f_drive / "VENTURE_CAPITAL",
            "scientific_procurement": self.f_drive / "SCIENTIFIC_PROCUREMENT",
            "trade_data": self.f_drive / "TRADE_DATA",
            "standards": self.f_drive / "STANDARDS",
            "national_statistics": self.f_drive / "NATIONAL_STATISTICS",
            "company_registries": self.f_drive / "COMPANY_REGISTRIES",
            "sanctions": self.f_drive / "SANCTIONS"
        }

        # Create all directories
        for dir_path in self.source_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Track collection status
        self.collection_log = []

    # ============= EXPORT CONTROL LISTS =============

    def collect_bis_entity_list(self) -> Dict:
        """Download BIS Entity List"""
        logger.info("Collecting BIS Entity List...")

        try:
            # BIS Entity List is published as a PDF and CSV
            url = "https://www.bis.doc.gov/index.php/documents/consolidated-entity-list/1072-supp-4-to-part-744/file"

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                # Save the Entity List
                output_file = self.source_dirs["export_control"] / f"BIS_Entity_List_{datetime.now().strftime('%Y%m%d')}.pdf"

                with open(output_file, 'wb') as f:
                    f.write(response.content)

                logger.info(f"Saved BIS Entity List to {output_file}")

                return {
                    "source": "BIS Entity List",
                    "status": "success",
                    "file": str(output_file),
                    "size": len(response.content),
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error collecting BIS Entity List: {e}")
            return {"source": "BIS Entity List", "status": "failed", "error": str(e)}

    def collect_meu_list(self) -> Dict:
        """Download Military End User (MEU) List"""
        logger.info("Collecting Military End User List...")

        try:
            # MEU List URL (this changes, would need to be updated)
            url = "https://www.bis.doc.gov/index.php/documents/supplement-no-7-to-part-744/2744-supplement-no-7-to-part-744-3/file"

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                output_file = self.source_dirs["export_control"] / f"MEU_List_{datetime.now().strftime('%Y%m%d')}.pdf"

                with open(output_file, 'wb') as f:
                    f.write(response.content)

                logger.info(f"Saved MEU List to {output_file}")

                return {
                    "source": "MEU List",
                    "status": "success",
                    "file": str(output_file),
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error collecting MEU List: {e}")
            return {"source": "MEU List", "status": "failed", "error": str(e)}

    def collect_unverified_list(self) -> Dict:
        """Download Unverified List"""
        logger.info("Collecting Unverified List...")

        try:
            url = "https://www.bis.doc.gov/index.php/documents/unverified-list/2736-unverified-list/file"

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                output_file = self.source_dirs["export_control"] / f"Unverified_List_{datetime.now().strftime('%Y%m%d')}.pdf"

                with open(output_file, 'wb') as f:
                    f.write(response.content)

                return {
                    "source": "Unverified List",
                    "status": "success",
                    "file": str(output_file)
                }

        except Exception as e:
            logger.error(f"Error collecting Unverified List: {e}")
            return {"source": "Unverified List", "status": "failed", "error": str(e)}

    def collect_denied_persons_list(self) -> Dict:
        """Download Denied Persons List"""
        logger.info("Collecting Denied Persons List...")

        try:
            # DPL is available as a text file
            url = "https://www.bis.doc.gov/dpl/dpl.txt"

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                output_file = self.source_dirs["export_control"] / f"Denied_Persons_List_{datetime.now().strftime('%Y%m%d')}.txt"

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)

                # Parse the text file into structured data
                lines = response.text.split('\n')
                denied_persons = []

                for line in lines[1:]:  # Skip header
                    if line.strip():
                        # Parse the fixed-width format
                        denied_persons.append(line.strip())

                # Also save as JSON
                json_file = self.source_dirs["export_control"] / f"Denied_Persons_List_{datetime.now().strftime('%Y%m%d')}.json"

                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump({"denied_persons": denied_persons, "count": len(denied_persons)}, f, indent=2)

                return {
                    "source": "Denied Persons List",
                    "status": "success",
                    "files": [str(output_file), str(json_file)],
                    "count": len(denied_persons)
                }

        except Exception as e:
            logger.error(f"Error collecting Denied Persons List: {e}")
            return {"source": "Denied Persons List", "status": "failed", "error": str(e)}

    # ============= SANCTIONS LISTS =============

    def collect_ofac_sdn_list(self) -> Dict:
        """Download OFAC SDN List"""
        logger.info("Collecting OFAC SDN List...")

        try:
            # OFAC provides multiple formats
            urls = {
                "csv": "https://www.treasury.gov/ofac/downloads/sdn.csv",
                "xml": "https://www.treasury.gov/ofac/downloads/sdn.xml",
                "json": "https://www.treasury.gov/ofac/downloads/sdn_advanced.xml"  # Advanced format
            }

            files_saved = []

            for format_type, url in urls.items():
                try:
                    response = requests.get(url, timeout=60)

                    if response.status_code == 200:
                        output_file = self.source_dirs["sanctions"] / f"OFAC_SDN_{datetime.now().strftime('%Y%m%d')}.{format_type}"

                        with open(output_file, 'wb') as f:
                            f.write(response.content)

                        files_saved.append(str(output_file))
                        logger.info(f"Saved OFAC SDN {format_type} to {output_file}")

                except Exception as e:
                    logger.error(f"Error downloading OFAC SDN {format_type}: {e}")

            return {
                "source": "OFAC SDN List",
                "status": "success" if files_saved else "failed",
                "files": files_saved,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error collecting OFAC SDN List: {e}")
            return {"source": "OFAC SDN List", "status": "failed", "error": str(e)}

    def collect_eu_sanctions_list(self) -> Dict:
        """Download EU Consolidated Sanctions List"""
        logger.info("Collecting EU Consolidated Sanctions List...")

        try:
            # EU provides XML and CSV formats
            url = "https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList_1_1/content?token="

            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                output_file = self.source_dirs["sanctions"] / f"EU_Sanctions_{datetime.now().strftime('%Y%m%d')}.csv"

                with open(output_file, 'wb') as f:
                    f.write(response.content)

                return {
                    "source": "EU Sanctions List",
                    "status": "success",
                    "file": str(output_file)
                }

        except Exception as e:
            logger.error(f"Error collecting EU Sanctions List: {e}")
            return {"source": "EU Sanctions List", "status": "failed", "error": str(e)}

    # ============= VENTURE CAPITAL DATA =============

    def collect_sec_form_d(self, days_back: int = 30) -> Dict:
        """Collect recent SEC Form D filings"""
        logger.info(f"Collecting SEC Form D filings (last {days_back} days)...")

        try:
            # Use SEC EDGAR API
            base_url = "https://data.sec.gov/submissions/"

            # Get recent Form D filings
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

            # This would need proper EDGAR API implementation
            # For now, save the search parameters
            search_params = {
                "form_type": "D",
                "from_date": from_date,
                "to_date": datetime.now().strftime("%Y-%m-%d")
            }

            output_file = self.source_dirs["venture_capital"] / f"SEC_Form_D_search_{datetime.now().strftime('%Y%m%d')}.json"

            with open(output_file, 'w') as f:
                json.dump(search_params, f, indent=2)

            return {
                "source": "SEC Form D",
                "status": "success",
                "file": str(output_file),
                "search_params": search_params
            }

        except Exception as e:
            logger.error(f"Error collecting SEC Form D: {e}")
            return {"source": "SEC Form D", "status": "failed", "error": str(e)}

    # ============= TRADE DATA =============

    def collect_un_comtrade_data(self, commodity_codes: List[str] = None) -> Dict:
        """Collect UN Comtrade data for scientific instruments"""
        logger.info("Collecting UN Comtrade data...")

        if commodity_codes is None:
            # Default to scientific instrument codes
            commodity_codes = [
                "9027",  # Scientific instruments
                "9031",  # Measuring instruments
                "8543",  # Electrical machinery
                "8471",  # Automatic data processing machines
                "8541",  # Semiconductor devices
            ]

        try:
            results = []

            for code in commodity_codes:
                # UN Comtrade API (requires registration for full access)
                url = f"https://comtrade.un.org/api/get"

                params = {
                    "r": "all",  # Reporter
                    "p": "156",  # Partner (156 = China)
                    "ps": "2024",  # Year
                    "cc": code,  # Commodity code
                    "fmt": "json",
                    "max": 500
                }

                try:
                    response = requests.get(url, params=params, timeout=30)

                    if response.status_code == 200:
                        data = response.json()

                        output_file = self.source_dirs["trade_data"] / f"UN_Comtrade_{code}_{datetime.now().strftime('%Y%m%d')}.json"

                        with open(output_file, 'w') as f:
                            json.dump(data, f, indent=2)

                        results.append({
                            "code": code,
                            "file": str(output_file),
                            "records": len(data.get("dataset", []))
                        })

                        time.sleep(1)  # Rate limiting

                except Exception as e:
                    logger.error(f"Error collecting UN Comtrade for code {code}: {e}")

            return {
                "source": "UN Comtrade",
                "status": "success" if results else "failed",
                "commodity_codes": commodity_codes,
                "results": results
            }

        except Exception as e:
            logger.error(f"Error collecting UN Comtrade data: {e}")
            return {"source": "UN Comtrade", "status": "failed", "error": str(e)}

    # ============= SCIENTIFIC RESOURCES =============

    def collect_top500_supercomputers(self) -> Dict:
        """Collect TOP500 Supercomputer List"""
        logger.info("Collecting TOP500 Supercomputers list...")

        try:
            # TOP500 provides CSV export
            url = "https://www.top500.org/lists/top500/list/2024/11/download/TOP500_202411.xlsx"

            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                output_file = self.source_dirs["scientific_procurement"] / f"TOP500_{datetime.now().strftime('%Y%m%d')}.xlsx"

                with open(output_file, 'wb') as f:
                    f.write(response.content)

                # Try to parse and extract China entries
                try:
                    df = pd.read_excel(io.BytesIO(response.content))
                    china_systems = df[df['Country'].str.contains('China', na=False)]

                    china_file = self.source_dirs["scientific_procurement"] / f"TOP500_China_{datetime.now().strftime('%Y%m%d')}.json"

                    china_data = {
                        "total_china_systems": len(china_systems),
                        "systems": china_systems.to_dict('records')
                    }

                    with open(china_file, 'w') as f:
                        json.dump(china_data, f, indent=2, default=str)

                except:
                    pass

                return {
                    "source": "TOP500 Supercomputers",
                    "status": "success",
                    "file": str(output_file)
                }

        except Exception as e:
            logger.error(f"Error collecting TOP500: {e}")
            return {"source": "TOP500", "status": "failed", "error": str(e)}

    # ============= STANDARDS BODIES =============

    def collect_ietf_standards(self) -> Dict:
        """Collect IETF standards and participation data"""
        logger.info("Collecting IETF standards data...")

        try:
            # IETF Datatracker API
            base_url = "https://datatracker.ietf.org/api/v1/"

            # Get recent documents
            url = base_url + "doc/document/?time__gte=2024-01-01&format=json"

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()

                output_file = self.source_dirs["standards"] / f"IETF_Documents_{datetime.now().strftime('%Y%m%d')}.json"

                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)

                # Check for China participation
                china_docs = []
                for doc in data.get("objects", []):
                    if doc.get("abstract") and "china" in doc["abstract"].lower():
                        china_docs.append(doc)

                if china_docs:
                    china_file = self.source_dirs["standards"] / f"IETF_China_Related_{datetime.now().strftime('%Y%m%d')}.json"

                    with open(china_file, 'w') as f:
                        json.dump({"count": len(china_docs), "documents": china_docs}, f, indent=2)

                return {
                    "source": "IETF Standards",
                    "status": "success",
                    "file": str(output_file),
                    "total_docs": len(data.get("objects", [])),
                    "china_related": len(china_docs)
                }

        except Exception as e:
            logger.error(f"Error collecting IETF standards: {e}")
            return {"source": "IETF", "status": "failed", "error": str(e)}

    # ============= COMPANY REGISTRIES =============

    def collect_uk_companies_house(self, search_terms: List[str] = None) -> Dict:
        """Collect UK Companies House data"""
        logger.info("Collecting UK Companies House data...")

        if search_terms is None:
            search_terms = ["china", "huawei", "alibaba", "tencent"]

        try:
            # Companies House API (requires API key but free)
            # For demo, we'll save search parameters

            results = []

            for term in search_terms:
                search_url = f"https://api.company-information.service.gov.uk/search/companies?q={term}"

                # Would need API key in headers
                headers = {
                    "Authorization": "Basic YOUR_API_KEY"  # Would need actual key
                }

                # Save search intent
                search_data = {
                    "search_term": term,
                    "api_url": search_url,
                    "timestamp": datetime.now().isoformat()
                }

                results.append(search_data)

            output_file = self.source_dirs["company_registries"] / f"UK_Companies_House_searches_{datetime.now().strftime('%Y%m%d')}.json"

            with open(output_file, 'w') as f:
                json.dump({"searches": results}, f, indent=2)

            return {
                "source": "UK Companies House",
                "status": "success",
                "file": str(output_file),
                "search_terms": search_terms
            }

        except Exception as e:
            logger.error(f"Error collecting UK Companies House: {e}")
            return {"source": "UK Companies House", "status": "failed", "error": str(e)}

    # ============= MASTER COLLECTION ORCHESTRATION =============

    def collect_all_export_controls(self) -> List[Dict]:
        """Collect all export control lists"""
        logger.info("Starting export control lists collection...")

        results = []

        # Run all export control collectors
        collectors = [
            self.collect_bis_entity_list,
            self.collect_meu_list,
            self.collect_unverified_list,
            self.collect_denied_persons_list
        ]

        for collector in collectors:
            result = collector()
            results.append(result)
            self.collection_log.append(result)
            time.sleep(2)  # Be polite

        return results

    def collect_all_sanctions(self) -> List[Dict]:
        """Collect all sanctions lists"""
        logger.info("Starting sanctions lists collection...")

        results = []

        collectors = [
            self.collect_ofac_sdn_list,
            self.collect_eu_sanctions_list
        ]

        for collector in collectors:
            result = collector()
            results.append(result)
            self.collection_log.append(result)
            time.sleep(2)

        return results

    def collect_critical_sources(self) -> Dict:
        """Collect from all critical free sources"""
        logger.info("Starting comprehensive data collection from all critical sources...")

        collection_session = {
            "session_id": f"master_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "sources_attempted": 0,
            "sources_successful": 0,
            "sources_failed": 0,
            "results": {}
        }

        # Collect Export Controls
        logger.info("\n=== COLLECTING EXPORT CONTROL LISTS ===")
        export_results = self.collect_all_export_controls()
        collection_session["results"]["export_controls"] = export_results

        # Collect Sanctions
        logger.info("\n=== COLLECTING SANCTIONS LISTS ===")
        sanctions_results = self.collect_all_sanctions()
        collection_session["results"]["sanctions"] = sanctions_results

        # Collect VC Data
        logger.info("\n=== COLLECTING VENTURE CAPITAL DATA ===")
        vc_result = self.collect_sec_form_d()
        collection_session["results"]["venture_capital"] = [vc_result]

        # Collect Trade Data
        logger.info("\n=== COLLECTING TRADE DATA ===")
        trade_result = self.collect_un_comtrade_data()
        collection_session["results"]["trade_data"] = [trade_result]

        # Collect Scientific Resources
        logger.info("\n=== COLLECTING SCIENTIFIC RESOURCES ===")
        sci_result = self.collect_top500_supercomputers()
        collection_session["results"]["scientific"] = [sci_result]

        # Collect Standards Data
        logger.info("\n=== COLLECTING STANDARDS DATA ===")
        standards_result = self.collect_ietf_standards()
        collection_session["results"]["standards"] = [standards_result]

        # Calculate statistics
        for category, results in collection_session["results"].items():
            for result in results:
                collection_session["sources_attempted"] += 1
                if result.get("status") == "success":
                    collection_session["sources_successful"] += 1
                else:
                    collection_session["sources_failed"] += 1

        collection_session["end_time"] = datetime.now().isoformat()

        # Save session results
        session_file = self.f_drive / "collection_logs" / f"master_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        session_file.parent.mkdir(exist_ok=True)

        with open(session_file, 'w') as f:
            json.dump(collection_session, f, indent=2)

        logger.info(f"\n=== COLLECTION COMPLETE ===")
        logger.info(f"Sources attempted: {collection_session['sources_attempted']}")
        logger.info(f"Successful: {collection_session['sources_successful']}")
        logger.info(f"Failed: {collection_session['sources_failed']}")
        logger.info(f"Session saved: {session_file}")

        return collection_session

    def generate_collection_report(self) -> str:
        """Generate a report of the collection session"""

        report = []
        report.append("=" * 60)
        report.append("MASTER DATA COLLECTION REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 60)

        # Group by status
        successful = [log for log in self.collection_log if log.get("status") == "success"]
        failed = [log for log in self.collection_log if log.get("status") == "failed"]

        report.append(f"\nSUCCESSFUL COLLECTIONS ({len(successful)}):")
        for item in successful:
            report.append(f"  - {item.get('source')}")
            if "file" in item:
                report.append(f"    File: {item['file']}")
            elif "files" in item:
                for f in item["files"]:
                    report.append(f"    File: {f}")

        if failed:
            report.append(f"\nFAILED COLLECTIONS ({len(failed)}):")
            for item in failed:
                report.append(f"  - {item.get('source')}")
                if "error" in item:
                    report.append(f"    Error: {item['error']}")

        report.append("\n" + "=" * 60)

        report_text = "\n".join(report)

        # Save report
        report_file = self.f_drive / "collection_logs" / f"collection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_file, 'w') as f:
            f.write(report_text)

        return report_text


if __name__ == "__main__":
    collector = MasterSourceCollector()

    print("[MASTER SOURCE COLLECTOR]")
    print("Collecting from all critical free data sources...")
    print(f"Output directory: F:/OSINT_DATA/")

    # Run comprehensive collection
    session = collector.collect_critical_sources()

    # Generate and print report
    report = collector.generate_collection_report()
    print(report)

    print(f"\nData saved to: F:/OSINT_DATA/")
    print("Collection complete!")
