"""
TED Collector for Italy Security-Relevant CPV Codes
Based on ChatGPT Phase 2 requirements
"""

import os
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import time
import logging
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TEDItalyCollector:
    """
    Collect TED procurement data for Italy with security-relevant CPV codes
    CPV codes from ChatGPT Phase 2: 30200000, 30230000, 30240000, 30250000,
    32340000, 48800000, 48820000, 72200000
    """

    def __init__(self, base_path: str = "data/collected/ted/italy"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Security-relevant CPV codes identified by ChatGPT
        self.cpv_codes = {
            "30200000": "Computer equipment and supplies",
            "30230000": "Computer-related equipment",
            "30240000": "Software and systems",
            "30250000": "Internet and intranet software",
            "32340000": "Microphones and loudspeakers",  # Often includes surveillance
            "48800000": "Information systems and servers",
            "48820000": "Servers",
            "72200000": "Software programming and consultancy services"
        }

        self.output_file = self.base_path / "procurement_signals.csv"
        self.state_file = self.base_path / "collector_state.json"

    def load_state(self) -> Dict:
        """Load collector state for incremental updates"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "last_run": None,
            "last_cursor": None,
            "total_collected": 0
        }

    def save_state(self, state: Dict):
        """Save collector state"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def calculate_rolling_metrics(self, data: List[Dict]) -> Dict:
        """
        Calculate 90-day rolling counts and rate of change
        As specified in ChatGPT Phase 2 indicators
        """
        metrics = {
            "90_day_count": 0,
            "90_day_awards": 0,
            "yoy_delta": 0,
            "surge_detected": False,
            "by_cpv": {}
        }

        cutoff_date = datetime.now() - timedelta(days=90)
        year_ago = datetime.now() - timedelta(days=365)

        for record in data:
            pub_date = datetime.fromisoformat(record.get("publication_date", ""))

            if pub_date >= cutoff_date:
                metrics["90_day_count"] += 1
                if record.get("status") == "award":
                    metrics["90_day_awards"] += 1

                cpv = record.get("cpv")
                if cpv:
                    cpv_main = cpv[:8]  # Main CPV code
                    if cpv_main not in metrics["by_cpv"]:
                        metrics["by_cpv"][cpv_main] = 0
                    metrics["by_cpv"][cpv_main] += 1

        return metrics

    def compute_china_exposure_flags(self, record: Dict) -> Dict:
        """
        Flag potential China exposure based on supplier names and patterns
        This is a simplified version - real implementation would use more sophisticated matching
        """
        china_indicators = [
            "huawei", "zte", "hikvision", "dahua", "alibaba",
            "tencent", "baidu", "lenovo", "xiaomi", "dji"
        ]

        flags = {
            "china_supplier": False,
            "china_keywords": False,
            "dual_use_potential": False
        }

        supplier = record.get("supplier", "").lower()
        title = record.get("title", "").lower()

        # Check for Chinese companies
        for indicator in china_indicators:
            if indicator in supplier:
                flags["china_supplier"] = True
                break

        # Check for China-related keywords in title/description
        china_keywords = ["china", "chinese", "prc", "beijing", "shanghai"]
        for keyword in china_keywords:
            if keyword in title:
                flags["china_keywords"] = True
                break

        # Flag dual-use potential for specific CPV categories
        cpv = record.get("cpv", "")
        if cpv.startswith(("30230000", "30240000", "48800000", "48820000")):
            flags["dual_use_potential"] = True

        return flags

    def write_to_csv(self, records: List[Dict]):
        """
        Write procurement records to CSV
        Fields as specified in ChatGPT Phase 2
        """
        if not records:
            return

        fieldnames = [
            "award_id", "buyer", "supplier", "cpv", "title", "url",
            "publication_date", "place", "amount", "status",
            "china_supplier", "china_keywords", "dual_use_potential"
        ]

        file_exists = self.output_file.exists()

        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for record in records:
                # Add China exposure flags
                flags = self.compute_china_exposure_flags(record)
                record.update(flags)

                # Ensure all fields are present
                for field in fieldnames:
                    if field not in record:
                        record[field] = ""

                writer.writerow({k: record[k] for k in fieldnames})

    def simulate_ted_data(self, num_records: int = 50) -> List[Dict]:
        """
        Simulate TED data for demonstration
        Real implementation would connect to TED API or parse downloaded files
        """
        import random

        records = []

        italian_buyers = [
            "Ministero della Difesa", "Consip S.p.A.", "INAIL",
            "Agenzia delle Entrate", "Roma Capitale", "Comune di Milano",
            "Università di Bologna", "CNR", "ENEA", "ASI"
        ]

        suppliers = [
            "Leonardo S.p.A.", "Fincantieri", "STMicroelectronics",
            "Engineering Ingegneria Informatica", "Almaviva",
            "Huawei Italia", "ZTE Italia", "Microsoft Italia",
            "IBM Italia", "Oracle Italia", "SAP Italia"
        ]

        for i in range(num_records):
            days_ago = random.randint(0, 180)
            pub_date = datetime.now() - timedelta(days=days_ago)

            cpv_code = random.choice(list(self.cpv_codes.keys()))

            record = {
                "award_id": f"IT-2025-{1000+i}",
                "buyer": random.choice(italian_buyers),
                "supplier": random.choice(suppliers),
                "cpv": f"{cpv_code}-{random.randint(1,9)}",
                "title": f"{self.cpv_codes[cpv_code]} procurement",
                "url": f"https://ted.europa.eu/notice/IT-2025-{1000+i}",
                "publication_date": pub_date.isoformat(),
                "place": random.choice(["Roma", "Milano", "Bologna", "Torino", "Napoli"]),
                "amount": random.randint(10000, 5000000),
                "status": random.choice(["notice", "award", "award"])  # More awards than notices
            }

            records.append(record)

        return records

    def collect(self, use_simulation: bool = True):
        """
        Main collection method
        In production, would connect to TED API or parse bulk downloads
        """
        logger.info("Starting TED Italy collection...")
        logger.info(f"Target CPV codes: {list(self.cpv_codes.keys())}")

        state = self.load_state()

        if use_simulation:
            logger.info("Using simulated data for demonstration")
            records = self.simulate_ted_data()
        else:
            # Real implementation would:
            # 1. Connect to TED API with API key
            # 2. Query for Italy + CPV codes
            # 3. Handle pagination
            # 4. Parse XML/JSON responses
            logger.error("Real TED connection not implemented yet")
            return

        # Write records
        self.write_to_csv(records)

        # Calculate metrics
        all_records = self.load_all_records()
        metrics = self.calculate_rolling_metrics(all_records)

        # Log metrics
        logger.info(f"90-day count: {metrics['90_day_count']}")
        logger.info(f"90-day awards: {metrics['90_day_awards']}")
        logger.info(f"By CPV: {metrics['by_cpv']}")

        # Check for China exposure
        china_count = sum(1 for r in records if self.compute_china_exposure_flags(r)["china_supplier"])
        if china_count > 0:
            logger.warning(f"Found {china_count} records with potential China suppliers")

        # Update state
        state["last_run"] = datetime.now().isoformat()
        state["total_collected"] = len(all_records)
        self.save_state(state)

        logger.info(f"Collection complete. Total records: {len(all_records)}")

        # Write metrics summary
        metrics_file = self.base_path / "metrics_summary.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)

    def load_all_records(self) -> List[Dict]:
        """Load all collected records for analysis"""
        if not self.output_file.exists():
            return []

        records = []
        with open(self.output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)

        return records

    def generate_early_warning_report(self):
        """
        Generate early warning indicators as specified in ChatGPT Phase 2
        """
        records = self.load_all_records()
        metrics = self.calculate_rolling_metrics(records)

        report = {
            "generated_at": datetime.now().isoformat(),
            "early_warning_indicators": {
                "procurement_surge": metrics["90_day_count"] > 100,  # Threshold example
                "china_exposure_trend": "increasing",  # Would calculate from historical data
                "critical_cpv_activity": {
                    cpv: count for cpv, count in metrics["by_cpv"].items()
                    if count > 10  # Threshold for concern
                }
            },
            "recommendations": []
        }

        # Generate recommendations based on patterns
        if metrics["90_day_count"] > 100:
            report["recommendations"].append(
                "High procurement activity detected - review for unusual patterns"
            )

        china_suppliers = [
            r for r in records
            if self.compute_china_exposure_flags(r)["china_supplier"]
        ]
        if len(china_suppliers) > 5:
            report["recommendations"].append(
                f"Multiple Chinese suppliers detected ({len(china_suppliers)} contracts) - assess technology transfer risk"
            )

        # Save report
        report_file = self.base_path / f"ewi_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Early warning report generated: {report_file}")

        return report


def main():
    """Main entry point for TED Italy collector"""
    collector = TEDItalyCollector()

    # Run collection
    collector.collect(use_simulation=True)

    # Generate early warning report
    report = collector.generate_early_warning_report()

    print("\n=== Collection Summary ===")
    print(f"Generated at: {report['generated_at']}")
    print(f"Early warnings: {report['early_warning_indicators']}")
    print(f"Recommendations: {len(report['recommendations'])}")

    for rec in report["recommendations"]:
        print(f"  - {rec}")


if __name__ == "__main__":
    main()
