"""
MoU Registry System for Italy Research Institutions
Critical gap identified by ChatGPT Phase 5: No central MoU registry
"""

import json
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict, Optional
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MoUStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class MoURegistry:
    """
    Central registry for tracking MoUs between Italian and foreign institutions
    Addresses critical oversight gap identified in ChatGPT analysis
    """

    def __init__(self, base_path: str = "data/registry/mou"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.registry_file = self.base_path / "mou_registry.json"
        self.audit_log = self.base_path / "audit_log.json"
        self.risk_assessments = self.base_path / "risk_assessments.json"

        # Load existing registry
        self.registry = self.load_registry()

        # Italian institutions requiring monitoring (from ChatGPT Phase 5)
        self.monitored_institutions = {
            "CNR": {"type": "research", "risk_level": "high"},
            "IIT": {"type": "research", "risk_level": "high"},
            "Sant'Anna School": {"type": "university", "risk_level": "high"},
            "University of Padua": {"type": "university", "risk_level": "high"},
            "Politecnico di Milano": {"type": "university", "risk_level": "high"},
            "CINECA": {"type": "computing", "risk_level": "critical"},
            "ASI": {"type": "space", "risk_level": "critical"},
            "INFN": {"type": "physics", "risk_level": "high"},
            "ENEA": {"type": "energy", "risk_level": "medium"},
            "Leonardo S.p.A.": {"type": "defense", "risk_level": "critical"},
            "STMicroelectronics": {"type": "semiconductor", "risk_level": "critical"},
            "Fincantieri": {"type": "naval", "risk_level": "critical"}
        }

        # High-risk foreign partners (focus on China per analysis)
        self.high_risk_partners = {
            "CAS": "Chinese Academy of Sciences",
            "CNSA": "China National Space Administration",
            "Tsinghua University": "Leading Chinese university",
            "USTC": "University of Science and Technology of China",
            "Huazhong University": "Tech focus",
            "AVIC": "Aviation Industry Corporation of China",
            "CASC": "China Aerospace Science and Technology",
            "NORINCO": "Defense conglomerate"
        }

    def load_registry(self) -> Dict:
        """Load existing MoU registry"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {"mous": [], "metadata": {"created": datetime.now().isoformat()}}

    def save_registry(self):
        """Save registry to disk"""
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2, default=str)

    def register_mou(self, mou_data: Dict) -> str:
        """
        Register a new MoU in the system
        Returns MoU ID
        """
        # Generate unique ID
        mou_id = f"MOU-{datetime.now().strftime('%Y%m%d')}-{len(self.registry['mous']) + 1:04d}"

        # Assess risk level
        risk_level = self.assess_mou_risk(mou_data)

        # Create MoU record
        mou_record = {
            "mou_id": mou_id,
            "registered_at": datetime.now().isoformat(),
            "italian_institution": mou_data.get("italian_institution"),
            "foreign_partner": mou_data.get("foreign_partner"),
            "partner_country": mou_data.get("partner_country"),
            "signing_date": mou_data.get("signing_date"),
            "expiry_date": mou_data.get("expiry_date"),
            "status": mou_data.get("status", MoUStatus.ACTIVE.value),
            "scope": mou_data.get("scope", []),
            "technology_areas": mou_data.get("technology_areas", []),
            "funding_amount": mou_data.get("funding_amount"),
            "ip_sharing": mou_data.get("ip_sharing", "unknown"),
            "data_sharing": mou_data.get("data_sharing", "unknown"),
            "personnel_exchange": mou_data.get("personnel_exchange", False),
            "joint_labs": mou_data.get("joint_labs", False),
            "conference_initiated": mou_data.get("conference_initiated", False),
            "conference_event": mou_data.get("conference_event"),
            "risk_level": risk_level.value,
            "oversight_required": risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL],
            "notes": mou_data.get("notes", "")
        }

        # Add to registry
        self.registry["mous"].append(mou_record)
        self.save_registry()

        # Log the registration
        self.log_action("register", mou_id, mou_record)

        # Trigger alerts if high risk
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.trigger_alert(mou_record)

        logger.info(f"Registered MoU: {mou_id} with risk level: {risk_level.value}")

        return mou_id

    def assess_mou_risk(self, mou_data: Dict) -> RiskLevel:
        """
        Assess risk level of an MoU based on multiple factors
        """
        risk_score = 0

        # Check Italian institution risk level
        italian_inst = mou_data.get("italian_institution")
        if italian_inst in self.monitored_institutions:
            inst_risk = self.monitored_institutions[italian_inst]["risk_level"]
            if inst_risk == "critical":
                risk_score += 10
            elif inst_risk == "high":
                risk_score += 7
            elif inst_risk == "medium":
                risk_score += 4

        # Check foreign partner risk
        foreign_partner = mou_data.get("foreign_partner")
        if any(high_risk in foreign_partner for high_risk in self.high_risk_partners):
            risk_score += 10

        # Check country risk (China focus)
        partner_country = mou_data.get("partner_country", "").lower()
        if partner_country in ["china", "cn", "prc"]:
            risk_score += 8
        elif partner_country in ["russia", "iran", "north korea"]:
            risk_score += 10

        # Check technology sensitivity
        tech_areas = mou_data.get("technology_areas", [])
        sensitive_techs = ["quantum", "defense", "semiconductor", "space", "nuclear", "ai", "robotics"]
        for tech in tech_areas:
            if any(sensitive in tech.lower() for sensitive in sensitive_techs):
                risk_score += 5

        # Check data/IP sharing
        if mou_data.get("ip_sharing") == "yes":
            risk_score += 5
        if mou_data.get("data_sharing") == "yes":
            risk_score += 3

        # Personnel exchange increases risk
        if mou_data.get("personnel_exchange"):
            risk_score += 4

        # Joint labs are high risk
        if mou_data.get("joint_labs"):
            risk_score += 6

        # Determine risk level
        if risk_score >= 25:
            return RiskLevel.CRITICAL
        elif risk_score >= 18:
            return RiskLevel.HIGH
        elif risk_score >= 12:
            return RiskLevel.MEDIUM
        elif risk_score >= 6:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    def query_mous(self, filters: Dict) -> List[Dict]:
        """
        Query MoUs based on filters
        """
        results = []

        for mou in self.registry.get("mous", []):
            match = True

            # Apply filters
            if "italian_institution" in filters:
                if mou["italian_institution"] != filters["italian_institution"]:
                    match = False

            if "partner_country" in filters:
                if mou["partner_country"].lower() != filters["partner_country"].lower():
                    match = False

            if "risk_level" in filters:
                if mou["risk_level"] != filters["risk_level"]:
                    match = False

            if "status" in filters:
                if mou["status"] != filters["status"]:
                    match = False

            if "technology_area" in filters:
                if filters["technology_area"] not in mou.get("technology_areas", []):
                    match = False

            if match:
                results.append(mou)

        return results

    def generate_oversight_report(self) -> Dict:
        """
        Generate oversight report for high-risk MoUs
        """
        all_mous = self.registry.get("mous", [])

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_mous": len(all_mous),
            "by_status": {},
            "by_risk_level": {},
            "by_country": {},
            "critical_concerns": [],
            "recommendations": []
        }

        # Analyze by status
        for mou in all_mous:
            status = mou["status"]
            report["by_status"][status] = report["by_status"].get(status, 0) + 1

            risk = mou["risk_level"]
            report["by_risk_level"][risk] = report["by_risk_level"].get(risk, 0) + 1

            country = mou["partner_country"]
            report["by_country"][country] = report["by_country"].get(country, 0) + 1

        # Identify critical concerns
        critical_mous = [m for m in all_mous if m["risk_level"] == "critical"]
        high_risk_mous = [m for m in all_mous if m["risk_level"] == "high"]

        if critical_mous:
            report["critical_concerns"].append(
                f"{len(critical_mous)} critical-risk MoUs require immediate review"
            )

        china_mous = [m for m in all_mous if m["partner_country"].lower() in ["china", "cn", "prc"]]
        if len(china_mous) > 10:
            report["critical_concerns"].append(
                f"High concentration of Chinese partnerships ({len(china_mous)} MoUs)"
            )

        # Check for quantum/defense concerns
        quantum_mous = [m for m in all_mous if "quantum" in str(m.get("technology_areas", [])).lower()]
        defense_mous = [m for m in all_mous if "defense" in str(m.get("technology_areas", [])).lower()]

        if quantum_mous:
            report["critical_concerns"].append(
                f"{len(quantum_mous)} MoUs involve quantum technology"
            )

        if defense_mous:
            report["critical_concerns"].append(
                f"{len(defense_mous)} MoUs involve defense-related technology"
            )

        # Generate recommendations
        if critical_mous or high_risk_mous:
            report["recommendations"].append(
                "Immediate security review required for all critical/high-risk MoUs"
            )

        unvetted = [m for m in all_mous if not m.get("security_review_date")]
        if len(unvetted) > len(all_mous) * 0.5:
            report["recommendations"].append(
                f"{len(unvetted)} MoUs lack security review - implement vetting process"
            )

        if not any(m.get("ip_sharing") != "unknown" for m in all_mous):
            report["recommendations"].append(
                "IP sharing terms unknown for most MoUs - require disclosure"
            )

        return report

    def trigger_alert(self, mou_record: Dict):
        """
        Trigger alert for high-risk MoUs
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "alert_type": "HIGH_RISK_MOU",
            "mou_id": mou_record["mou_id"],
            "risk_level": mou_record["risk_level"],
            "italian_institution": mou_record["italian_institution"],
            "foreign_partner": mou_record["foreign_partner"],
            "technology_areas": mou_record.get("technology_areas", []),
            "message": f"High-risk MoU registered between {mou_record['italian_institution']} and {mou_record['foreign_partner']}"
        }

        # In production, would send to monitoring system
        logger.warning(f"ALERT: {alert['message']}")

        # Save alert
        alerts_file = self.base_path / "alerts.json"
        alerts = []
        if alerts_file.exists():
            with open(alerts_file, 'r') as f:
                alerts = json.load(f)
        alerts.append(alert)
        with open(alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)

    def log_action(self, action: str, mou_id: str, details: Dict):
        """
        Log actions for audit trail
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "mou_id": mou_id,
            "details": details
        }

        logs = []
        if self.audit_log.exists():
            with open(self.audit_log, 'r') as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(self.audit_log, 'w') as f:
            json.dump(logs, f, indent=2)

    def populate_sample_data(self):
        """
        Populate registry with sample data based on ChatGPT Phase 5 findings
        """
        sample_mous = [
            {
                "italian_institution": "CNR",
                "foreign_partner": "CAS Institute of Computing",
                "partner_country": "China",
                "signing_date": "2023-06-15",
                "expiry_date": "2026-06-14",
                "scope": ["joint research", "personnel exchange"],
                "technology_areas": ["quantum computing", "AI"],
                "ip_sharing": "yes",
                "personnel_exchange": True,
                "conference_initiated": True,
                "conference_event": "Q2B 2023"
            },
            {
                "italian_institution": "ASI",
                "foreign_partner": "CNSA-adjacent institute",
                "partner_country": "China",
                "signing_date": "2022-10-20",
                "expiry_date": "2025-10-19",
                "scope": ["space technology", "earth observation"],
                "technology_areas": ["satellite", "remote sensing"],
                "ip_sharing": "partial",
                "joint_labs": False,
                "conference_initiated": True,
                "conference_event": "IAC 2022"
            },
            {
                "italian_institution": "IIT",
                "foreign_partner": "Tsinghua Robotics Lab",
                "partner_country": "China",
                "signing_date": "2024-03-10",
                "expiry_date": "2027-03-09",
                "scope": ["robotics research", "AI"],
                "technology_areas": ["robotics", "machine learning"],
                "data_sharing": "yes",
                "personnel_exchange": True,
                "conference_initiated": True,
                "conference_event": "ICRA 2023"
            },
            {
                "italian_institution": "University of Padua",
                "foreign_partner": "MIT",
                "partner_country": "USA",
                "signing_date": "2024-01-15",
                "expiry_date": "2027-01-14",
                "scope": ["quantum research"],
                "technology_areas": ["quantum encryption"],
                "ip_sharing": "no",
                "personnel_exchange": True,
                "joint_labs": True
            }
        ]

        for mou_data in sample_mous:
            self.register_mou(mou_data)

        logger.info(f"Populated {len(sample_mous)} sample MoUs")


def main():
    """Main entry point"""
    registry = MoURegistry()

    print("\n=== MoU Registry System ===")
    print("Addressing critical gap: No central MoU registry")
    print("Institution coverage: 12 key Italian research centers")

    # Populate sample data
    registry.populate_sample_data()

    # Query China-related MoUs
    china_mous = registry.query_mous({"partner_country": "China"})
    print(f"\nChina-related MoUs: {len(china_mous)}")

    # Query critical risk MoUs
    critical_mous = registry.query_mous({"risk_level": "critical"})
    print(f"Critical risk MoUs: {len(critical_mous)}")

    # Generate oversight report
    report = registry.generate_oversight_report()
    print(f"\n=== Oversight Report ===")
    print(f"Total MoUs: {report['total_mous']}")
    print(f"Risk levels: {report['by_risk_level']}")
    print(f"Critical concerns: {len(report['critical_concerns'])}")

    for concern in report["critical_concerns"]:
        print(f"  ⚠ {concern}")

    print(f"\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  • {rec}")

    # Save report
    report_file = registry.base_path / "oversight_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nOutputs saved to: {registry.base_path}")


if __name__ == "__main__":
    main()
