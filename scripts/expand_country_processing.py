#!/usr/bin/env python3
"""
Automated Country Expansion Processor
Expands intelligence collection to full European region plus strategic partners
Includes: UK, Norway, Switzerland, Balkans, Turkey, Armenia, Azerbaijan, Georgia, Iceland
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CountryExpansionProcessor:
    """Process data for expanded country coverage"""

    def __init__(self):
        self.base_path = Path("C:/Projects/OSINT - Foresight")
        self.config_file = self.base_path / "config/expanded_countries.json"
        self.load_config()

        # Data source paths
        self.data_sources = {
            'openalex': Path("F:/OSINT_Backups/openalex/data/"),
            'ted': Path("F:/TED_Data/monthly/"),
            'usaspending': Path("F:/OSINT_DATA/USAspending/"),
            'cordis': self.base_path / "countries/_global/data/cordis_raw/",
        }

    def load_config(self):
        """Load expanded country configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logging.info(f"Loaded config: {self.config['total_countries']} countries")
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            sys.exit(1)

    def get_expanded_countries(self) -> Dict[str, str]:
        """Get full expanded country list"""
        expanded = {}

        # Combine all categories
        for category, data in self.config['categories'].items():
            for code in data['countries']:
                # Get full name (would need a country code -> name mapping)
                expanded[code] = category

        return expanded

    def get_new_countries(self) -> List[str]:
        """Get newly added countries for priority processing"""
        return self.config['priority_tiers']['tier_2_expanded_coverage']['countries']

    def verify_data_access(self) -> Dict[str, bool]:
        """Verify access to all data sources"""
        status = {}

        for source, path in self.data_sources.items():
            exists = path.exists()
            status[source] = exists

            if exists:
                logging.info(f"✓ {source}: {path}")
            else:
                logging.warning(f"✗ {source}: {path} NOT FOUND")

        return status

    def create_processing_queue(self) -> List[Dict]:
        """Create prioritized processing queue"""
        queue = []

        # Priority 1: New countries (Tier 2)
        new_countries = self.get_new_countries()
        for country in new_countries:
            queue.append({
                'country': country,
                'priority': 1,
                'reason': 'Newly added - expanded coverage',
                'sources': ['openalex', 'ted', 'usaspending', 'cordis']
            })

        # Priority 2: High-risk gateways (Tier 1)
        tier1_countries = self.config['priority_tiers']['tier_1_high_priority']['countries']
        for country in tier1_countries:
            if country not in new_countries:  # Avoid duplicates
                queue.append({
                    'country': country,
                    'priority': 2,
                    'reason': 'Gateway country - high Chinese penetration',
                    'sources': ['openalex', 'ted', 'usaspending', 'cordis']
                })

        # Priority 3: Major economies (Tier 3)
        tier3_countries = self.config['priority_tiers']['tier_3_major_economies']['countries']
        for country in tier3_countries:
            queue.append({
                'country': country,
                'priority': 3,
                'reason': 'Major economy - high R&D volume',
                'sources': ['openalex', 'ted', 'usaspending', 'cordis']
            })

        # Priority 4: Rest of Europe (Tier 4)
        tier4_countries = self.config['priority_tiers']['tier_4_rest_of_europe']['countries']
        for country in tier4_countries:
            queue.append({
                'country': country,
                'priority': 4,
                'reason': 'Comprehensive coverage',
                'sources': ['openalex', 'ted', 'usaspending', 'cordis']
            })

        # Sort by priority
        queue.sort(key=lambda x: x['priority'])

        logging.info(f"Created processing queue: {len(queue)} countries")
        return queue

    def generate_processing_commands(self, queue: List[Dict]) -> List[str]:
        """Generate shell commands for processing"""
        commands = []

        for item in queue:
            country = item['country']

            # OpenAlex processing
            commands.append(
                f"python scripts/process_openalex_country.py "
                f"--country {country} --target CN --streaming"
            )

            # TED processing (only for EU/EEA countries)
            if self._is_ted_eligible(country):
                commands.append(
                    f"python scripts/process_ted_country.py "
                    f"--country {country} --years 2010-2025"
                )

            # USAspending processing (all countries)
            commands.append(
                f"python scripts/process_usaspending_country.py "
                f"--country {country} --china-analysis"
            )

            # CORDIS processing (EU framework participants)
            if self._is_cordis_eligible(country):
                commands.append(
                    f"python scripts/process_cordis_country.py "
                    f"--country {country} --china-collaborations"
                )

        return commands

    def _is_ted_eligible(self, country_code: str) -> bool:
        """Check if country is eligible for TED procurement data"""
        # EU27 + EEA (NO, IS, LI) + CH
        ted_eligible = (
            country_code in self.config['categories']['european_union']['countries']
            or country_code in ['NO', 'IS', 'LI', 'CH']
        )
        return ted_eligible

    def _is_cordis_eligible(self, country_code: str) -> bool:
        """Check if country participates in EU research framework"""
        # EU27 + associated countries (UK, NO, IS, CH, TR, etc.)
        cordis_eligible = (
            country_code in self.config['categories']['european_union']['countries']
            or country_code in ['GB', 'NO', 'IS', 'CH', 'TR', 'IL', 'UA', 'GE', 'AM', 'MD']
        )
        return cordis_eligible

    def create_batch_scripts(self, queue: List[Dict]):
        """Create batch processing scripts"""

        # Priority 1 & 2 countries (immediate processing)
        high_priority = [item for item in queue if item['priority'] <= 2]
        self._create_batch_script(
            high_priority,
            "process_expanded_countries_high_priority.bat",
            "HIGH PRIORITY: New countries + Gateway countries"
        )

        # All countries (comprehensive processing)
        self._create_batch_script(
            queue,
            "process_expanded_countries_all.bat",
            "COMPREHENSIVE: All expanded country coverage"
        )

        # By data source
        for source in ['openalex', 'ted', 'usaspending', 'cordis']:
            source_queue = [item for item in queue if source in item['sources']]
            self._create_batch_script(
                source_queue,
                f"process_{source}_expanded.bat",
                f"{source.upper()}: Expanded country processing"
            )

    def _create_batch_script(self, queue: List[Dict], filename: str, description: str):
        """Create a batch processing script"""

        script_path = self.base_path / "scripts" / filename

        with open(script_path, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f"REM {description}\n")
            f.write(f"REM Generated: {datetime.now().isoformat()}\n")
            f.write(f"REM Countries: {len(queue)}\n\n")

            f.write(f"cd /d \"{self.base_path}\"\n\n")

            for item in queue:
                country = item['country']
                f.write(f"echo Processing {country} - {item['reason']}\n")

                for source in item['sources']:
                    if source == 'openalex':
                        f.write(f"python scripts/process_openalex_country.py --country {country} --target CN --streaming\n")
                    elif source == 'ted' and self._is_ted_eligible(country):
                        f.write(f"python scripts/process_ted_country.py --country {country} --years 2010-2025\n")
                    elif source == 'usaspending':
                        f.write(f"python scripts/process_usaspending_country.py --country {country} --china-analysis\n")
                    elif source == 'cordis' and self._is_cordis_eligible(country):
                        f.write(f"python scripts/process_cordis_country.py --country {country} --china-collaborations\n")

                f.write(f"\n")

            f.write(f"echo Completed: {len(queue)} countries processed\n")
            f.write(f"pause\n")

        logging.info(f"Created batch script: {script_path}")

    def generate_status_report(self, queue: List[Dict]) -> Dict:
        """Generate expansion status report"""

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_countries': self.config['total_countries'],
            'expanded_coverage': {
                'new_countries': len(self.get_new_countries()),
                'high_priority': len([q for q in queue if q['priority'] <= 2]),
                'total_queue': len(queue)
            },
            'data_sources': {
                'openalex': len([q for q in queue if 'openalex' in q['sources']]),
                'ted': len([q for q in queue if 'ted' in q['sources'] and self._is_ted_eligible(q['country'])]),
                'usaspending': len([q for q in queue if 'usaspending' in q['sources']]),
                'cordis': len([q for q in queue if 'cordis' in q['sources'] and self._is_cordis_eligible(q['country'])])
            },
            'priority_breakdown': {
                'priority_1': len([q for q in queue if q['priority'] == 1]),
                'priority_2': len([q for q in queue if q['priority'] == 2]),
                'priority_3': len([q for q in queue if q['priority'] == 3]),
                'priority_4': len([q for q in queue if q['priority'] == 4])
            },
            'new_countries_list': self.get_new_countries(),
            'queue': queue
        }

        # Save report
        report_path = self.base_path / "analysis/country_expansion_status.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        logging.info(f"Status report saved: {report_path}")
        return report

    def run(self):
        """Execute country expansion processing"""

        logging.info("="*70)
        logging.info("COUNTRY EXPANSION PROCESSOR")
        logging.info("="*70)

        # Step 1: Verify data access
        logging.info("\nStep 1: Verifying data access...")
        access_status = self.verify_data_access()
        accessible = sum(1 for v in access_status.values() if v)
        logging.info(f"Data sources accessible: {accessible}/{len(access_status)}")

        # Step 2: Create processing queue
        logging.info("\nStep 2: Creating processing queue...")
        queue = self.create_processing_queue()

        # Step 3: Generate batch scripts
        logging.info("\nStep 3: Generating batch processing scripts...")
        self.create_batch_scripts(queue)

        # Step 4: Generate status report
        logging.info("\nStep 4: Generating status report...")
        report = self.generate_status_report(queue)

        # Summary
        logging.info("\n" + "="*70)
        logging.info("EXPANSION SUMMARY")
        logging.info("="*70)
        logging.info(f"Total countries: {report['total_countries']}")
        logging.info(f"New countries: {report['expanded_coverage']['new_countries']}")
        logging.info(f"High priority: {report['expanded_coverage']['high_priority']}")
        logging.info(f"Processing queue: {report['expanded_coverage']['total_queue']}")
        logging.info("\nNew countries:")
        for country in report['new_countries_list']:
            logging.info(f"  - {country}")

        logging.info("\nBatch scripts created:")
        logging.info("  - process_expanded_countries_high_priority.bat")
        logging.info("  - process_expanded_countries_all.bat")
        logging.info("  - process_openalex_expanded.bat")
        logging.info("  - process_ted_expanded.bat")
        logging.info("  - process_usaspending_expanded.bat")
        logging.info("  - process_cordis_expanded.bat")

        logging.info("\n" + "="*70)
        logging.info("READY FOR PROCESSING")
        logging.info("="*70)

if __name__ == "__main__":
    processor = CountryExpansionProcessor()
    processor.run()