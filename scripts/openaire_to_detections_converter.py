#!/usr/bin/env python3
"""
OpenAIRE to Detection Format Converter
Extracts Chinese research collaborations from OpenAIRE data
Converts to standardized detection NDJSON format for Phase 2
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpenAIREDetector:
    """
    Detector for Chinese research collaborations in OpenAIRE publications

    Detection Method:
    - Extracts publications with country_code CN or HK in organizations
    - Tracks collaboration countries
    - Records organization names and DOIs
    """

    def __init__(self):
        self.output_dir = Path("data/processed/openaire_v1")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Stats
        self.stats = {
            'total_collaborations': 0,
            'by_country': {},
            'by_year': {},
            'organizations': {},
            'total_countries': set()
        }

    def create_detection(self, collab: Dict, org_index: int, org_data: Dict) -> Dict:
        """Create detection record in standardized format"""

        # Create unique detection ID
        detection_id = hashlib.sha256(
            f"openaire_{collab['id']}_{org_index}".encode()
        ).hexdigest()[:16]

        # Parse date
        pub_year = collab.get('date', '')[:4] if collab.get('date') else 'unknown'

        detection = {
            'detection_id': f"openaire_{detection_id}",
            'detector_id': 'openaire_v1.0',
            'detector_version': 'v1.0',
            'detection_timestamp': datetime.now().isoformat(),

            # Entity information
            'entity_name': org_data.get('organization', 'Unknown'),
            'entity_type': 'research_organization',
            'entity_subtype': 'openaire_publication_author',

            # Geographic information
            'country_code': org_data.get('country', ''),

            # Publication information
            'publication_id': collab.get('id'),
            'publication_title': collab.get('title', ''),
            'publication_doi': collab.get('doi', ''),
            'publication_type': collab.get('type', 'publication'),
            'publication_year': pub_year,

            # Collaboration information
            'collaboration_countries': collab.get('countries_list', '').split(','),
            'num_countries': collab.get('num_countries', 0),
            'partner_countries': collab.get('partner_countries', ''),

            # Detection metadata
            'confidence_score': 90,  # High - OpenAIRE is curated database
            'detection_reason': 'country_code_in_organizations',

            # Provenance
            'evidence': {
                'source': 'OpenAIRE Research Graph',
                'file': 'openaire_china_extraction_20250927_131055.json',
                'record_id': collab.get('id'),
                'doi': collab.get('doi', ''),
                'extraction_time': '2025-09-27T13:10:55.753644'
            },

            # Temporal
            'valid_from': pub_year if pub_year != 'unknown' else None,
            'valid_to': None,
        }

        return detection

    def process_openaire_file(self, filepath: Path) -> List[Dict]:
        """Process OpenAIRE extraction JSON file"""
        logger.info(f"Processing OpenAIRE data from {filepath}")

        detections = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            collaborations = data.get('china_collaborations', [])
            logger.info(f"Loaded {len(collaborations)} China collaborations")

            for collab in collaborations:
                self.stats['total_collaborations'] += 1

                # Parse organizations
                try:
                    orgs_str = collab.get('organizations', '[]')
                    orgs = json.loads(orgs_str) if isinstance(orgs_str, str) else orgs_str
                except:
                    orgs = []

                # Extract year for stats
                pub_year = collab.get('date', '')[:4] if collab.get('date') else 'unknown'
                self.stats['by_year'][pub_year] = self.stats['by_year'].get(pub_year, 0) + 1

                # Track countries
                countries = collab.get('countries_list', '').split(',')
                for country in countries:
                    if country:
                        self.stats['total_countries'].add(country)
                        self.stats['by_country'][country] = self.stats['by_country'].get(country, 0) + 1

                # Create detection for each organization
                for org_idx, org in enumerate(orgs):
                    org_name = org.get('organization', 'Unknown')
                    org_country = org.get('country', '')

                    # Track organization
                    if org_name not in self.stats['organizations']:
                        self.stats['organizations'][org_name] = {
                            'count': 0,
                            'countries': set(),
                            'publications': set()
                        }

                    self.stats['organizations'][org_name]['count'] += 1
                    self.stats['organizations'][org_name]['countries'].add(org_country)
                    self.stats['organizations'][org_name]['publications'].add(collab.get('id', 0))

                    # Create detection
                    detection = self.create_detection(collab, org_idx, org)
                    detections.append(detection)

                if self.stats['total_collaborations'] % 100 == 0:
                    logger.info(f"Processed {self.stats['total_collaborations']:,} collaborations, "
                               f"{len(detections):,} organization participations")

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
            'total_collaborations': self.stats['total_collaborations'],
            'total_organizations': len(self.stats['organizations']),
            'total_countries': len(self.stats['total_countries']),
            'by_country': self.stats['by_country'],
            'by_year': self.stats['by_year'],
            'top_organizations': []
        }

        # Top organizations by participation count
        sorted_orgs = sorted(
            self.stats['organizations'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:20]

        for org_name, data in sorted_orgs:
            stats_serializable['top_organizations'].append({
                'name': org_name,
                'participations': data['count'],
                'unique_publications': len(data['publications']),
                'countries': list(data['countries'])
            })

        stats_file = self.output_dir / "statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_serializable, f, indent=2)

        logger.info(f"Statistics saved to {stats_file}")

    def run(self):
        """Main processing pipeline"""
        logger.info("="*80)
        logger.info("OpenAIRE China Detector v1.0")
        logger.info("="*80)

        # Process OpenAIRE file
        openaire_file = Path("data/processed/openaire_china_extraction_20250927_131055.json")
        if not openaire_file.exists():
            logger.error(f"OpenAIRE file not found: {openaire_file}")
            return

        detections = self.process_openaire_file(openaire_file)

        # Save results
        if detections:
            self.save_detections(detections)
            self.save_statistics()

            logger.info("="*80)
            logger.info("SUMMARY")
            logger.info("="*80)
            logger.info(f"Total collaborations processed: {self.stats['total_collaborations']:,}")
            logger.info(f"Total organization participations: {len(detections):,}")
            logger.info(f"Unique organizations: {len(self.stats['organizations']):,}")
            logger.info(f"Countries involved: {len(self.stats['total_countries']):,}")
            logger.info("="*80)
            logger.info(f"Output: {self.output_dir / 'detections.ndjson'}")
            logger.info(f"Statistics: {self.output_dir / 'statistics.json'}")
            logger.info("="*80)
        else:
            logger.warning("No detections found!")

if __name__ == "__main__":
    detector = OpenAIREDetector()
    detector.run()
