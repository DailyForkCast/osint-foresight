#!/usr/bin/env python3
"""
CORDIS to Detection Format Converter
Extracts Chinese organization participations from CORDIS H2020 and Horizon Europe data
Converts to standardized detection NDJSON format for Phase 2
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CORDISDetector:
    """
    Detector for Chinese organizations in EU CORDIS projects

    Detection Method:
    - Primary: country == "CN" (ISO 3166-1 alpha-2 for China)
    - Secondary: Known Chinese institution names
    """

    def __init__(self):
        self.output_dir = Path("data/processed/cordis_v1")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Chinese institution keywords (from previous analysis)
        self.chinese_institution_keywords = {
            'TSINGHUA', 'PEKING', 'FUDAN', 'ZHEJIANG', 'SHANGHAI JIAO TONG',
            'CHINA AGRICULTURAL', 'CHINESE ACADEMY', 'BEIJING INSTITUTE',
            'NANJING UNIVERSITY', 'WUHAN UNIVERSITY', 'HARBIN INSTITUTE',
            'XIAN JIAOTONG', 'TONGJI UNIVERSITY', 'SICHUAN UNIVERSITY',
            'TIANJIN UNIVERSITY', 'DALIAN UNIVERSITY', 'SOUTHEAST UNIVERSITY'
        }

        # Stats
        self.stats = {
            'total_organizations': 0,
            'china_country_code': 0,
            'china_name_match': 0,
            'projects_with_china': set(),
            'chinese_organizations': {},
            'by_activity_type': {},
            'total_funding': 0.0
        }

    def _parse_float(self, value) -> float:
        """Parse float from various formats"""
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).replace(',', ''))
        except:
            return 0.0

    def is_chinese_organization(self, org: Dict) -> tuple[bool, str, int]:
        """
        Determine if organization is Chinese

        Returns:
            (is_chinese, detection_reason, confidence_score)
        """
        country = str(org.get('country', '')).strip().upper()
        name = str(org.get('name', '')).upper()

        # Primary criterion: country code
        if country == 'CN':
            return (True, 'country_code_CN', 95)

        # Secondary criterion: Known Chinese institution names
        for keyword in self.chinese_institution_keywords:
            if keyword in name:
                return (True, f'institution_name_match_{keyword}', 85)

        # Additional checks for "CHINA" or "CHINESE" in name
        if 'CHINA ' in name or ' CHINA' in name or name.startswith('CHINA'):
            if country in ['', 'XX', 'ZZ']:  # Unknown/international country codes
                return (True, 'china_in_name_no_country', 70)

        if 'CHINESE ' in name or ' CHINESE' in name:
            if country in ['', 'XX', 'ZZ']:
                return (True, 'chinese_in_name_no_country', 70)

        return (False, 'not_chinese', 0)

    def create_detection(self, org: Dict, project_id: int, detection_reason: str, confidence: int) -> Dict:
        """Create detection record in standardized format"""

        # Create unique detection ID
        detection_id = hashlib.sha256(
            f"cordis_{org.get('organisationID')}_{project_id}".encode()
        ).hexdigest()[:16]

        # Extract funding
        ec_contribution = org.get('ecContribution', '0')
        try:
            if isinstance(ec_contribution, (int, float)):
                funding_amount = float(ec_contribution)
            else:
                funding_amount = float(str(ec_contribution).replace(',', ''))
        except:
            funding_amount = 0.0

        detection = {
            'detection_id': f"cordis_{detection_id}",
            'detector_id': 'cordis_v1.0',
            'detector_version': 'v1.0',
            'detection_timestamp': datetime.now().isoformat(),

            # Entity information
            'entity_name': org.get('name', ''),
            'entity_type': 'research_organization',
            'entity_subtype': org.get('activityType', 'unknown'),

            # Geographic information
            'country_code': org.get('country', ''),
            'city': org.get('city', ''),
            'geolocation': org.get('geolocation', ''),

            # Project information
            'project_id': project_id,
            'project_acronym': org.get('projectAcronym', ''),
            'role': org.get('role', ''),
            'order': org.get('order', 0),

            # Funding information
            'funding_amount_eur': funding_amount,
            'total_cost_eur': self._parse_float(org.get('totalCost', 0)),

            # Detection metadata
            'confidence_score': confidence,
            'detection_reason': detection_reason,
            'is_sme': org.get('SME', False),

            # Provenance
            'evidence': {
                'source': 'CORDIS H2020/Horizon Europe',
                'file': 'organization.json',
                'organization_id': org.get('organisationID'),
                'rcn': org.get('rcn'),
                'content_update_date': org.get('contentUpdateDate', '')
            },

            # Temporal
            'valid_from': None,  # Would need project start date from project.json
            'valid_to': None,    # Would need project end date
            'end_of_participation': org.get('endOfParticipation', 'false')
        }

        return detection

    def process_organization_file(self, filepath: Path, program: str) -> List[Dict]:
        """Process organization.json file"""
        logger.info(f"Processing {program} organizations from {filepath}")

        detections = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                organizations = json.load(f)

            logger.info(f"Loaded {len(organizations)} organizations")

            for org in organizations:
                self.stats['total_organizations'] += 1

                # Check if Chinese
                is_chinese, reason, confidence = self.is_chinese_organization(org)

                if is_chinese:
                    # Update stats
                    if 'country_code' in reason:
                        self.stats['china_country_code'] += 1
                    elif 'name_match' in reason:
                        self.stats['china_name_match'] += 1

                    # Track projects
                    project_id = org.get('projectID')
                    self.stats['projects_with_china'].add(project_id)

                    # Track organizations
                    org_name = org.get('name', '')
                    if org_name not in self.stats['chinese_organizations']:
                        self.stats['chinese_organizations'][org_name] = {
                            'count': 0,
                            'total_funding': 0.0,
                            'projects': set(),
                            'activity_types': set()
                        }

                    self.stats['chinese_organizations'][org_name]['count'] += 1
                    self.stats['chinese_organizations'][org_name]['projects'].add(project_id)

                    # Funding
                    funding = self._parse_float(org.get('ecContribution', 0))
                    self.stats['chinese_organizations'][org_name]['total_funding'] += funding
                    self.stats['total_funding'] += funding

                    # Activity type
                    activity_type = org.get('activityType', 'unknown')
                    self.stats['chinese_organizations'][org_name]['activity_types'].add(activity_type)
                    self.stats['by_activity_type'][activity_type] = self.stats['by_activity_type'].get(activity_type, 0) + 1

                    # Create detection
                    detection = self.create_detection(org, project_id, reason, confidence)
                    detection['program'] = program  # Add program identifier
                    detections.append(detection)

                if self.stats['total_organizations'] % 10000 == 0:
                    logger.info(f"Processed {self.stats['total_organizations']:,} organizations, "
                               f"found {len(detections):,} Chinese participations")

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")
            raise

        return detections

    def save_detections(self, detections: List[Dict]):
        """Save detections to NDJSON format"""
        output_file = self.output_dir / "detections.ndjson"

        logger.info(f"Writing {len(detections)} detections to {output_file}")

        with open(output_file, 'w', encoding='utf-8') as f:
            for detection in detections:
                f.write(json.dumps(detection) + '\n')

        logger.info(f"Detections written successfully")

    def save_statistics(self):
        """Save processing statistics"""
        # Convert sets to lists for JSON serialization
        stats_serializable = {
            'total_organizations_processed': self.stats['total_organizations'],
            'detections_by_method': {
                'country_code_CN': self.stats['china_country_code'],
                'institution_name_match': self.stats['china_name_match']
            },
            'total_detections': self.stats['china_country_code'] + self.stats['china_name_match'],
            'unique_projects_with_china': len(self.stats['projects_with_china']),
            'unique_chinese_organizations': len(self.stats['chinese_organizations']),
            'total_funding_eur': self.stats['total_funding'],
            'by_activity_type': self.stats['by_activity_type'],
            'top_organizations': []
        }

        # Top organizations by participation count
        sorted_orgs = sorted(
            self.stats['chinese_organizations'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:20]

        for org_name, data in sorted_orgs:
            stats_serializable['top_organizations'].append({
                'name': org_name,
                'participations': data['count'],
                'total_funding_eur': data['total_funding'],
                'unique_projects': len(data['projects']),
                'activity_types': list(data['activity_types'])
            })

        stats_file = self.output_dir / "statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_serializable, f, indent=2)

        logger.info(f"Statistics saved to {stats_file}")

    def run(self):
        """Main processing pipeline"""
        logger.info("="*80)
        logger.info("CORDIS China Detector v1.0")
        logger.info("="*80)

        all_detections = []

        # Process H2020
        h2020_file = Path("countries/_global/data/cordis_raw/h2020/projects/organization.json")
        if h2020_file.exists():
            h2020_detections = self.process_organization_file(h2020_file, "H2020")
            all_detections.extend(h2020_detections)
            logger.info(f"H2020: {len(h2020_detections):,} Chinese participations found")
        else:
            logger.warning(f"H2020 file not found: {h2020_file}")

        # Process Horizon Europe
        horizon_file = Path("countries/_global/data/cordis_raw/horizon/projects/organization.json")
        if horizon_file.exists():
            horizon_detections = self.process_organization_file(horizon_file, "Horizon Europe")
            all_detections.extend(horizon_detections)
            logger.info(f"Horizon Europe: {len(horizon_detections):,} Chinese participations found")
        else:
            logger.warning(f"Horizon Europe file not found: {horizon_file}")

        # Save results
        if all_detections:
            self.save_detections(all_detections)
            self.save_statistics()

            logger.info("="*80)
            logger.info("SUMMARY")
            logger.info("="*80)
            logger.info(f"Total organizations processed: {self.stats['total_organizations']:,}")
            logger.info(f"Total Chinese participations: {len(all_detections):,}")
            logger.info(f"Unique Chinese organizations: {len(self.stats['chinese_organizations']):,}")
            logger.info(f"Unique projects with China: {len(self.stats['projects_with_china']):,}")
            logger.info(f"Total EU funding to Chinese orgs: €{self.stats['total_funding']:,.2f}")
            logger.info("="*80)
            logger.info(f"Output: {self.output_dir / 'detections.ndjson'}")
            logger.info(f"Statistics: {self.output_dir / 'statistics.json'}")
            logger.info("="*80)
        else:
            logger.warning("No Chinese participations found!")

if __name__ == "__main__":
    detector = CORDISDetector()
    detector.run()
