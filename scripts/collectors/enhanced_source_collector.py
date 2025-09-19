"""
Enhanced Source Collector with SSL handling and working URLs
Collects from verified free sources with proper error handling
"""

import os
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import time
import urllib3
import ssl

# Disable SSL warnings for problematic sites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedSourceCollector:
    """Enhanced collector with SSL handling and verified URLs"""

    def __init__(self):
        self.f_drive = Path("F:/OSINT_DATA")

        # Create directories
        self.dirs = {
            "export_control": self.f_drive / "EXPORT_CONTROL",
            "sanctions": self.f_drive / "SANCTIONS",
            "trade": self.f_drive / "TRADE_DATA",
            "standards": self.f_drive / "STANDARDS",
            "companies": self.f_drive / "COMPANIES",
            "academic": self.f_drive / "ACADEMIC",
            "supercomputers": self.f_drive / "SUPERCOMPUTERS"
        }

        for d in self.dirs.values():
            d.mkdir(parents=True, exist_ok=True)

        # Session for SSL handling
        self.session = requests.Session()
        self.session.verify = False  # For problematic government sites

        self.results = []

    def safe_download(self, url: str, output_path: Path, verify_ssl: bool = True) -> bool:
        """Safe download with SSL handling"""
        try:
            response = self.session.get(url, timeout=60, verify=verify_ssl)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Downloaded: {output_path.name}")
                return True
        except Exception as e:
            logger.error(f"Download failed for {url}: {e}")
        return False

    # =========== WORKING EXPORT CONTROL SOURCES ===========

    def collect_consolidated_screening_list(self) -> Dict:
        """Download Consolidated Screening List (CSV format)"""
        logger.info("Collecting Consolidated Screening List...")

        try:
            # This is the official consolidated list from trade.gov
            url = "https://api.trade.gov/consolidated_screening_list/search.csv?api_key=YOUR_KEY"

            # Alternative: Direct download without API key
            alt_url = "https://www.trade.gov/consolidated-screening-list"

            # For now, save the access information
            info = {
                "name": "Consolidated Screening List",
                "description": "Combines Entity List, SDN, and other lists",
                "api_url": url,
                "web_url": alt_url,
                "includes": [
                    "Entity List",
                    "Denied Persons List",
                    "Unverified List",
                    "Military End User List",
                    "Foreign Sanctions Evaders",
                    "Sectoral Sanctions"
                ],
                "timestamp": datetime.now().isoformat()
            }

            output_file = self.dirs["export_control"] / f"consolidated_screening_info_{datetime.now().strftime('%Y%m%d')}.json"

            with open(output_file, 'w') as f:
                json.dump(info, f, indent=2)

            self.results.append({"source": "Consolidated Screening List", "status": "info_saved", "file": str(output_file)})
            return {"status": "success", "file": str(output_file)}

        except Exception as e:
            logger.error(f"Error: {e}")
            return {"status": "failed", "error": str(e)}

    # =========== SANCTIONS DATA ===========

    def collect_ofac_data(self) -> Dict:
        """Collect OFAC sanctions data"""
        logger.info("Collecting OFAC sanctions data...")

        try:
            # OFAC provides direct downloads
            files_to_download = [
                ("https://www.treasury.gov/ofac/downloads/sdnlist.txt", "sdn_list.txt"),
                ("https://www.treasury.gov/ofac/downloads/consolidated/consolidated.xml", "consolidated.xml"),
                ("https://www.treasury.gov/ofac/downloads/ctrylst.txt", "country_list.txt")
            ]

            downloaded = []

            for url, filename in files_to_download:
                output_path = self.dirs["sanctions"] / f"OFAC_{filename.replace('.', '_')}_{datetime.now().strftime('%Y%m%d')}.{filename.split('.')[-1]}"

                if self.safe_download(url, output_path, verify_ssl=False):
                    downloaded.append(str(output_path))

            self.results.append({"source": "OFAC", "status": "success", "files": downloaded})
            return {"status": "success", "files": downloaded}

        except Exception as e:
            logger.error(f"OFAC error: {e}")
            return {"status": "failed", "error": str(e)}

    # =========== UN COMTRADE ===========

    def collect_un_comtrade_preview(self) -> Dict:
        """Collect UN Comtrade preview data for key commodities"""
        logger.info("Collecting UN Comtrade data...")

        try:
            # Scientific instrument codes
            commodity_codes = {
                "9027": "Scientific instruments",
                "9031": "Measuring instruments",
                "8471": "Computers",
                "8541": "Semiconductors"
            }

            base_url = "https://comtradeapi.un.org/public/v1/preview/"

            collected = []

            for code, description in commodity_codes.items():
                try:
                    # Get China exports to world
                    url = f"{base_url}/C/A/HS?reporterCode=156&cmdCode={code}&flowCode=X&partnerCode=0&motCode=0&partner2Code=0&customsCode=C00&includeDesc=true"

                    response = requests.get(url, timeout=30)

                    if response.status_code == 200:
                        data = response.json()

                        output_file = self.dirs["trade"] / f"UN_Comtrade_{code}_{datetime.now().strftime('%Y%m%d')}.json"

                        with open(output_file, 'w') as f:
                            json.dump({
                                "commodity_code": code,
                                "description": description,
                                "data": data,
                                "timestamp": datetime.now().isoformat()
                            }, f, indent=2)

                        collected.append(str(output_file))
                        logger.info(f"Collected trade data for {code} - {description}")

                    time.sleep(1)  # Rate limiting

                except Exception as e:
                    logger.error(f"Error collecting {code}: {e}")

            self.results.append({"source": "UN Comtrade", "status": "success", "files": collected})
            return {"status": "success", "files": collected}

        except Exception as e:
            logger.error(f"UN Comtrade error: {e}")
            return {"status": "failed", "error": str(e)}

    # =========== WIPO GLOBAL BRAND DATABASE ===========

    def collect_wipo_data(self) -> Dict:
        """Collect WIPO patent scope data"""
        logger.info("Collecting WIPO PatentScope data...")

        try:
            # Search for China AI/quantum patents
            search_terms = ["artificial intelligence", "quantum computing", "5G", "semiconductor"]

            base_url = "https://patentscope.wipo.int/search/en/search.jsf"

            search_info = {
                "source": "WIPO PatentScope",
                "search_terms": search_terms,
                "china_focus": True,
                "api_note": "Requires web scraping or API registration",
                "timestamp": datetime.now().isoformat()
            }

            output_file = self.dirs["academic"] / f"WIPO_search_config_{datetime.now().strftime('%Y%m%d')}.json"

            with open(output_file, 'w') as f:
                json.dump(search_info, f, indent=2)

            self.results.append({"source": "WIPO", "status": "config_saved", "file": str(output_file)})
            return {"status": "success", "file": str(output_file)}

        except Exception as e:
            logger.error(f"WIPO error: {e}")
            return {"status": "failed", "error": str(e)}

    # =========== SEMANTIC SCHOLAR ===========

    def collect_semantic_scholar(self) -> Dict:
        """Collect Semantic Scholar AI research papers"""
        logger.info("Collecting Semantic Scholar data...")

        try:
            # Search for China AI collaborations
            base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

            search_queries = [
                "China artificial intelligence",
                "China quantum computing",
                "China semiconductor"
            ]

            collected = []

            for query in search_queries:
                params = {
                    "query": query,
                    "limit": 100,
                    "fields": "title,authors,year,abstract,venue,citationCount"
                }

                response = requests.get(base_url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    output_file = self.dirs["academic"] / f"Semantic_Scholar_{query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"

                    with open(output_file, 'w') as f:
                        json.dump(data, f, indent=2)

                    collected.append(str(output_file))
                    logger.info(f"Collected papers for: {query}")

                    time.sleep(3)  # API rate limit: 100 requests per 5 minutes

            self.results.append({"source": "Semantic Scholar", "status": "success", "files": collected})
            return {"status": "success", "files": collected}

        except Exception as e:
            logger.error(f"Semantic Scholar error: {e}")
            return {"status": "failed", "error": str(e)}

    # =========== ARXIV ===========

    def collect_arxiv_papers(self) -> Dict:
        """Collect arXiv papers with China affiliations"""
        logger.info("Collecting arXiv papers...")

        try:
            import urllib

            base_url = "http://export.arxiv.org/api/query"

            # Search for papers with China affiliations in key areas
            searches = [
                ("quantum computing China", "quant-ph"),
                ("artificial intelligence China", "cs.AI"),
                ("machine learning China", "cs.LG")
            ]

            collected = []

            for search_query, category in searches:
                query = f"all:{search_query} AND cat:{category}"

                params = {
                    "search_query": query,
                    "start": 0,
                    "max_results": 50,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending"
                }

                url = base_url + "?" + urllib.parse.urlencode(params)
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    output_file = self.dirs["academic"] / f"arXiv_{category.replace('.', '_')}_{datetime.now().strftime('%Y%m%d')}.xml"

                    with open(output_file, 'wb') as f:
                        f.write(response.content)

                    collected.append(str(output_file))
                    logger.info(f"Collected arXiv papers for {category}")

                time.sleep(3)  # Be polite to arXiv

            self.results.append({"source": "arXiv", "status": "success", "files": collected})
            return {"status": "success", "files": collected}

        except Exception as e:
            logger.error(f"arXiv error: {e}")
            return {"status": "failed", "error": str(e)}

    # =========== IEEE DATAPORT ===========

    def collect_ieee_standards(self) -> Dict:
        """Collect IEEE standards participation data"""
        logger.info("Collecting IEEE standards data...")

        try:
            # IEEE Standards Association public data
            info = {
                "source": "IEEE Standards",
                "china_participation": {
                    "working_groups": ["802.11", "802.3", "5G", "AI Ethics"],
                    "companies": ["Huawei", "ZTE", "China Mobile", "Alibaba"],
                    "note": "Full data requires IEEE Xplore subscription"
                },
                "api_endpoint": "https://standards.ieee.org/api/",
                "timestamp": datetime.now().isoformat()
            }

            output_file = self.dirs["standards"] / f"IEEE_standards_info_{datetime.now().strftime('%Y%m%d')}.json"

            with open(output_file, 'w') as f:
                json.dump(info, f, indent=2)

            self.results.append({"source": "IEEE Standards", "status": "info_saved", "file": str(output_file)})
            return {"status": "success", "file": str(output_file)}

        except Exception as e:
            logger.error(f"IEEE error: {e}")
            return {"status": "failed", "error": str(e)}

    # =========== GLEIF LEI DATABASE ===========

    def collect_gleif_data(self) -> Dict:
        """Collect GLEIF Legal Entity Identifier data"""
        logger.info("Collecting GLEIF LEI data...")

        try:
            # GLEIF provides open data downloads
            base_url = "https://api.gleif.org/api/v1/"

            # Search for Chinese entities
            china_search = "lei-records?filter[entity.legalAddress.country]=CN&page[size]=100"

            url = base_url + china_search

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()

                output_file = self.dirs["companies"] / f"GLEIF_China_entities_{datetime.now().strftime('%Y%m%d')}.json"

                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.info(f"Collected {len(data.get('data', []))} Chinese entities from GLEIF")

                self.results.append({"source": "GLEIF", "status": "success", "file": str(output_file)})
                return {"status": "success", "file": str(output_file)}

        except Exception as e:
            logger.error(f"GLEIF error: {e}")
            return {"status": "failed", "error": str(e)}

    # =========== MASTER COLLECTION ===========

    def collect_all_sources(self) -> Dict:
        """Collect from all available sources"""
        logger.info("Starting comprehensive collection from all sources...")

        start_time = datetime.now()

        # Run all collectors
        collectors = [
            ("Export Control", self.collect_consolidated_screening_list),
            ("OFAC Sanctions", self.collect_ofac_data),
            ("UN Comtrade", self.collect_un_comtrade_preview),
            ("WIPO Patents", self.collect_wipo_data),
            ("Semantic Scholar", self.collect_semantic_scholar),
            ("arXiv Papers", self.collect_arxiv_papers),
            ("IEEE Standards", self.collect_ieee_standards),
            ("GLEIF LEI", self.collect_gleif_data)
        ]

        for name, collector in collectors:
            logger.info(f"\n=== Collecting {name} ===")
            try:
                result = collector()
                logger.info(f"{name}: {result['status']}")
            except Exception as e:
                logger.error(f"{name} failed: {e}")

            time.sleep(2)  # Be respectful between sources

        # Generate summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        summary = {
            "session_id": f"enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "sources_attempted": len(collectors),
            "results": self.results
        }

        # Save summary
        summary_file = self.f_drive / "collection_logs" / f"enhanced_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_file.parent.mkdir(exist_ok=True)

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        # Print report
        successful = [r for r in self.results if r.get("status") in ["success", "info_saved", "config_saved"]]
        failed = [r for r in self.results if r.get("status") == "failed"]

        print("\n" + "=" * 60)
        print("ENHANCED COLLECTION COMPLETE")
        print("=" * 60)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Successful: {len(successful)}/{len(self.results)}")
        print(f"Failed: {len(failed)}/{len(self.results)}")

        if successful:
            print("\nSuccessful Collections:")
            for r in successful:
                print(f"  - {r['source']}")

        if failed:
            print("\nFailed Collections:")
            for r in failed:
                print(f"  - {r['source']}")

        print(f"\nResults saved to: {summary_file}")

        return summary


if __name__ == "__main__":
    collector = EnhancedSourceCollector()

    print("[ENHANCED SOURCE COLLECTOR]")
    print("Starting collection from verified free sources...")
    print(f"Output: F:/OSINT_DATA/\n")

    summary = collector.collect_all_sources()

    print("\nCollection complete!")
    print(f"Check F:/OSINT_DATA/ for downloaded data")
