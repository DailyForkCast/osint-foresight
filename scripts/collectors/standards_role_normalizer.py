"""
Standards Role Normalizer (T2.1)
Tracks participation in standards bodies: ETSI, 3GPP, ISO, IEC, IEEE, ITU
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

class StandardsBody(Enum):
    """Standards organizations tracked"""
    ETSI = "etsi"  # European Telecommunications Standards Institute
    THREE_GPP = "3gpp"  # 3rd Generation Partnership Project
    ISO = "iso"  # International Organization for Standardization
    IEC = "iec"  # International Electrotechnical Commission
    IEEE = "ieee"  # Institute of Electrical and Electronics Engineers
    ITU = "itu"  # International Telecommunication Union
    IETF = "ietf"  # Internet Engineering Task Force
    W3C = "w3c"  # World Wide Web Consortium

class RoleWeight(Enum):
    """Weight assigned to different roles"""
    MEMBER = 1
    CONTRIBUTOR = 2
    RAPPORTEUR = 3
    CO_RAPPORTEUR = 3
    EDITOR = 5
    VICE_CHAIR = 6
    CHAIR = 7
    CONVENOR = 7

class StandardsRoleNormalizer:
    """
    Normalizes and tracks standards body participation
    Implements quarterly surge detection
    """

    def __init__(self, country_iso3: str):
        self.country = country_iso3
        self.output_dir = Path(f"artifacts/{country_iso3}/phase02_indicators")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Role weight mapping
        self.role_weights = {
            "member": 1,
            "participant": 1,
            "observer": 1,
            "contributor": 2,
            "rapporteur": 3,
            "co-rapporteur": 3,
            "editor": 5,
            "vice-chair": 6,
            "vice chair": 6,
            "chair": 7,
            "chairman": 7,
            "chairwoman": 7,
            "convenor": 7,
            "coordinator": 5
        }

        # Standards body endpoints (simplified for demo)
        self.endpoints = {
            "etsi": "https://portal.etsi.org/",
            "3gpp": "https://www.3gpp.org/",
            "iso": "https://www.iso.org/",
            "iec": "https://www.iec.ch/",
            "ieee": "https://standards.ieee.org/",
            "itu": "https://www.itu.int/",
            "ietf": "https://datatracker.ietf.org/",
            "w3c": "https://www.w3.org/"
        }

    def normalize_role(self, raw_role: str) -> Tuple[str, int]:
        """
        Normalize role name and return weight

        Args:
            raw_role: Raw role string from source

        Returns:
            Tuple of (normalized_role, weight)
        """
        role_lower = raw_role.lower().strip()

        # Find matching role
        for role, weight in self.role_weights.items():
            if role in role_lower:
                return (role, weight)

        # Default to member if unknown
        return ("member", 1)

    def extract_standards_roles(self, body: str) -> List[Dict]:
        """
        Extract roles from a standards body

        Args:
            body: Standards body identifier

        Returns:
            List of role records
        """
        roles = []

        # This would normally scrape/API call to the standards body
        # For demonstration, generating sample data

        if body == "3gpp":
            # Critical for 5G/6G standards
            sample_roles = [
                {
                    "body": "3GPP",
                    "wg": "SA2",
                    "role": "rapporteur",
                    "person": "Zhang Wei",
                    "orcid": None,
                    "org_ror": "ror_example_huawei",
                    "country": "CHN",
                    "start_q": "2024Q1",
                    "end_q": None
                },
                {
                    "body": "3GPP",
                    "wg": "RAN1",
                    "role": "chair",
                    "person": "John Smith",
                    "orcid": "0000-0001-2345-6789",
                    "org_ror": "ror_example_nokia",
                    "country": "FIN",
                    "start_q": "2023Q3",
                    "end_q": None
                }
            ]
            roles.extend(sample_roles)

        elif body == "etsi":
            # European standards
            sample_roles = [
                {
                    "body": "ETSI",
                    "wg": "ISG NFV",
                    "role": "vice-chair",
                    "person": "Maria Rossi",
                    "orcid": None,
                    "org_ror": f"ror_{self.country.lower()}_telecom",
                    "country": self.country,
                    "start_q": "2024Q2",
                    "end_q": None
                }
            ]
            roles.extend(sample_roles)

        return roles

    def calculate_quarterly_activity(self, roles_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate quarterly activity metrics

        Args:
            roles_df: DataFrame of standards roles

        Returns:
            Quarterly aggregated metrics
        """
        # Create quarter column
        roles_df['quarter'] = roles_df['start_q']

        # Calculate weighted sum per quarter
        quarterly = roles_df.groupby(['quarter', 'body']).agg({
            'weight': 'sum',
            'person': 'count'
        }).reset_index()

        quarterly.columns = ['quarter', 'body', 'role_weight_sum', 'participant_count']

        return quarterly

    def detect_surges(self, quarterly_df: pd.DataFrame, body: str) -> Dict:
        """
        Detect >2σ surges or drops in activity

        Args:
            quarterly_df: Quarterly metrics
            body: Standards body

        Returns:
            Surge detection results
        """
        body_data = quarterly_df[quarterly_df['body'] == body]['role_weight_sum'].values

        if len(body_data) < 4:
            return {"status": "insufficient_data"}

        # Calculate statistics
        mean = np.mean(body_data)
        std = np.std(body_data)

        # Check latest quarter
        latest = body_data[-1]
        z_score = (latest - mean) / std if std > 0 else 0

        alert = {
            "body": body,
            "mean": float(mean),
            "std": float(std),
            "latest": float(latest),
            "z_score": float(z_score),
            "alert": abs(z_score) > 2,
            "type": "surge" if z_score > 2 else "drop" if z_score < -2 else "normal"
        }

        return alert

    def track_china_influence(self, roles: List[Dict]) -> Dict:
        """
        Track PRC participation in standards

        Args:
            roles: List of role records

        Returns:
            China influence metrics
        """
        china_roles = [r for r in roles if r.get('country') == 'CHN']

        # Calculate weighted influence
        total_weight = sum(self.role_weights.get(r.get('role', 'member'), 1) for r in roles)
        china_weight = sum(self.role_weights.get(r.get('role', 'member'), 1) for r in china_roles)

        # Track by working group
        china_wgs = {}
        for role in china_roles:
            wg = role.get('wg', 'unknown')
            if wg not in china_wgs:
                china_wgs[wg] = {'count': 0, 'weight': 0}
            china_wgs[wg]['count'] += 1
            china_wgs[wg]['weight'] += self.role_weights.get(role.get('role', 'member'), 1)

        return {
            "total_roles": len(roles),
            "china_roles": len(china_roles),
            "china_weight_pct": (china_weight / total_weight * 100) if total_weight > 0 else 0,
            "china_wgs": china_wgs,
            "china_chairs": len([r for r in china_roles if 'chair' in r.get('role', '').lower()]),
            "china_editors": len([r for r in china_roles if 'editor' in r.get('role', '').lower()])
        }

    def generate_standards_report(self) -> Dict:
        """
        Generate comprehensive standards participation report

        Returns:
            Standards activity report
        """
        all_roles = []
        surge_alerts = []
        china_metrics = {}

        # Process each standards body
        for body_key in ["3gpp", "etsi", "iso", "iec", "ieee", "itu"]:
            logger.info(f"Processing {body_key.upper()} standards roles...")

            # Extract roles
            roles = self.extract_standards_roles(body_key)

            # Normalize and add weights
            for role in roles:
                normalized, weight = self.normalize_role(role.get('role', 'member'))
                role['normalized_role'] = normalized
                role['weight'] = weight

            all_roles.extend(roles)

            # China influence analysis
            china_metrics[body_key] = self.track_china_influence(roles)

        # Convert to DataFrame
        roles_df = pd.DataFrame(all_roles)

        # Calculate quarterly metrics
        if not roles_df.empty:
            quarterly = self.calculate_quarterly_activity(roles_df)

            # Detect surges
            for body in roles_df['body'].unique():
                alert = self.detect_surges(quarterly, body)
                if alert.get('alert'):
                    surge_alerts.append(alert)

        # Critical technology working groups
        critical_wgs = {
            "3GPP": ["SA2", "SA3", "RAN1", "RAN2"],  # 5G/6G security and radio
            "ETSI": ["ISG NFV", "ISG MEC", "ISG QKD"],  # NFV, edge computing, quantum
            "ISO": ["ISO/IEC JTC 1/SC 27", "ISO/IEC JTC 1/SC 42"],  # Security, AI
            "IEEE": ["P802.11", "P1609", "P2413"],  # WiFi, V2X, IoT
            "ITU": ["ITU-T SG13", "ITU-T SG17"],  # Future networks, security
            "IETF": ["QUIC", "TLS", "6TiSCH"]  # Transport, security, IoT
        }

        # Save outputs
        timestamp = datetime.now().isoformat()

        # Save roles CSV
        output_csv = self.output_dir / "standards_roles.csv"
        if not roles_df.empty:
            roles_df.to_csv(output_csv, index=False)

        # Generate report
        report = {
            "generated_at": timestamp,
            "country": self.country,
            "total_participants": len(set(r.get('person') for r in all_roles)),
            "total_roles": len(all_roles),
            "bodies_covered": list(roles_df['body'].unique()) if not roles_df.empty else [],
            "surge_alerts": surge_alerts,
            "china_influence": china_metrics,
            "critical_wgs": critical_wgs,
            "recommendations": []
        }

        # Add recommendations based on findings
        if surge_alerts:
            report["recommendations"].append(
                f"ALERT: Detected {len(surge_alerts)} significant changes in standards participation"
            )

        for body, metrics in china_metrics.items():
            if metrics.get('china_weight_pct', 0) > 30:
                report["recommendations"].append(
                    f"Monitor {body.upper()}: China influence at {metrics['china_weight_pct']:.1f}%"
                )

        # Save report
        output_json = self.output_dir / "standards_activity_report.json"
        with open(output_json, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Standards report saved to {output_json}")

        return report

def main():
    """Run standards role normalization for a country"""
    import sys

    country = sys.argv[1] if len(sys.argv) > 1 else "ITA"

    logger.info(f"Starting standards role analysis for {country}")

    normalizer = StandardsRoleNormalizer(country)
    report = normalizer.generate_standards_report()

    print(f"\n=== Standards Activity Report for {country} ===")
    print(f"Total participants: {report['total_participants']}")
    print(f"Total roles tracked: {report['total_roles']}")
    print(f"Standards bodies: {', '.join(report['bodies_covered'])}")

    if report['surge_alerts']:
        print(f"\n⚠️  SURGE ALERTS: {len(report['surge_alerts'])} detected")
        for alert in report['surge_alerts']:
            print(f"  - {alert['body']}: {alert['type']} (z-score: {alert['z_score']:.2f})")

    print("\n China Influence Summary:")
    for body, metrics in report['china_influence'].items():
        if metrics.get('china_roles', 0) > 0:
            print(f"  {body.upper()}: {metrics['china_weight_pct']:.1f}% weighted influence")

    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
