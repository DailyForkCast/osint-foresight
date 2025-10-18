#!/usr/bin/env python3
"""
Quarantine all existing data and create clean verification system
Move all contaminated data to quarantine folder
Build fresh database with manual verification only
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import os

class DataQuarantineManager:
    """Quarantine contaminated data and create clean system"""

    def __init__(self):
        """Initialize quarantine manager"""
        self.results_dir = Path('athena_results')
        self.quarantine_dir = Path('QUARANTINE_DATA')
        self.verified_dir = Path('VERIFIED_CLEAN')
        self.manual_review_dir = Path('MANUAL_REVIEW_QUEUE')

    def create_quarantine_structure(self):
        """Create quarantine and clean directories"""
        print("Creating quarantine structure...")

        # Create directories
        self.quarantine_dir.mkdir(exist_ok=True)
        self.verified_dir.mkdir(exist_ok=True)
        self.manual_review_dir.mkdir(exist_ok=True)

        # Create subdirectories
        (self.quarantine_dir / 'original_harvest').mkdir(exist_ok=True)
        (self.quarantine_dir / 'false_analyses').mkdir(exist_ok=True)
        (self.quarantine_dir / 'misclassified').mkdir(exist_ok=True)

        (self.verified_dir / 'agreements').mkdir(exist_ok=True)
        (self.verified_dir / 'evidence').mkdir(exist_ok=True)
        (self.verified_dir / 'sources').mkdir(exist_ok=True)

        print("Directory structure created")

    def quarantine_all_data(self):
        """Move all existing data to quarantine"""
        print("\n" + "="*80)
        print("QUARANTINING ALL EXISTING DATA")
        print("="*80)

        # Create quarantine log
        quarantine_log = {
            'quarantine_date': datetime.now().isoformat(),
            'reason': 'Complete data contamination - false positives, misclassification',
            'files_quarantined': [],
            'issues_found': [
                'Iceland: 100% false positives (77/77)',
                'Sister cities: 812 reported, only 9 verified',
                'Total agreements: 4,579 reported, only 640 passed basic filters',
                'Of 640 "verified", Iceland shows 100% false positives',
                'Pattern matching produced industrial spam, stock photos, language learning sites',
                'No actual content verification performed'
            ]
        }

        # Move all JSON files to quarantine
        json_files = list(self.results_dir.glob('*.json'))
        print(f"\nQuarantining {len(json_files)} contaminated files...")

        for json_file in json_files:
            try:
                # Determine quarantine location
                if 'harvest' in json_file.name.lower():
                    dest_dir = self.quarantine_dir / 'original_harvest'
                elif any(word in json_file.name.lower() for word in ['analysis', 'report', 'audit']):
                    dest_dir = self.quarantine_dir / 'false_analyses'
                else:
                    dest_dir = self.quarantine_dir / 'misclassified'

                # Move file
                dest_path = dest_dir / json_file.name
                shutil.move(str(json_file), str(dest_path))

                quarantine_log['files_quarantined'].append({
                    'original': str(json_file),
                    'quarantined_to': str(dest_path),
                    'reason': 'Data contamination'
                })

                print(f"  Quarantined: {json_file.name}")

            except Exception as e:
                print(f"  Error quarantining {json_file.name}: {e}")

        # Save quarantine log
        log_file = self.quarantine_dir / f'QUARANTINE_LOG_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(quarantine_log, f, indent=2, ensure_ascii=False)

        print(f"\nOK Quarantine complete. Log saved: {log_file}")

        return quarantine_log

    def extract_for_manual_review(self):
        """Extract URLs for manual review"""
        print("\n" + "="*80)
        print("EXTRACTING DATA FOR MANUAL REVIEW")
        print("="*80)

        # Load the quarantined data to extract URLs
        all_urls = set()

        # Try to load from quarantine
        for quarantine_file in self.quarantine_dir.glob('**/*.json'):
            if 'LOG' not in quarantine_file.name:
                try:
                    with open(quarantine_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._extract_urls(data, all_urls)
                except:
                    pass

        print(f"Extracted {len(all_urls)} unique URLs for review")

        # Create review batches
        urls_list = list(all_urls)
        batch_size = 100

        for i in range(0, len(urls_list), batch_size):
            batch = urls_list[i:i+batch_size]
            batch_num = (i // batch_size) + 1

            review_file = self.manual_review_dir / f'review_batch_{batch_num:03d}.json'

            review_data = {
                'batch_number': batch_num,
                'total_urls': len(batch),
                'review_status': 'pending',
                'urls_to_review': []
            }

            for url in batch:
                review_data['urls_to_review'].append({
                    'url': url,
                    'verification': {
                        'is_agreement': None,
                        'is_europe': None,
                        'is_china': None,
                        'european_entity': None,
                        'chinese_entity': None,
                        'agreement_type': None,
                        'date': None,
                        'status': None,
                        'notes': None
                    }
                })

            with open(review_file, 'w', encoding='utf-8') as f:
                json.dump(review_data, f, indent=2, ensure_ascii=False)

        total_batches = (len(urls_list) + batch_size - 1) // batch_size
        print(f"OK Created {total_batches} review batches of up to {batch_size} URLs each")

        return total_batches

    def _extract_urls(self, obj, url_set):
        """Recursively extract URLs"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['url', 'source_url'] and isinstance(value, str) and value.startswith('http'):
                    url_set.add(value)
                else:
                    self._extract_urls(value, url_set)
        elif isinstance(obj, list):
            for item in obj:
                self._extract_urls(item, url_set)

    def create_verification_template(self):
        """Create template for manual verification"""
        template = {
            'verification_template': {
                'url': 'URL to verify',
                'verified': False,
                'verification_date': None,
                'verified_by': None,
                'is_actual_agreement': False,
                'agreement_details': {
                    'type': None,  # MOU, Treaty, Partnership, Trade, Investment, etc.
                    'parties': {
                        'european': [],  # List of European parties
                        'chinese': []    # List of Chinese parties
                    },
                    'date_signed': None,
                    'date_effective': None,
                    'status': None,  # Active, Terminated, Suspended, Unknown
                    'scope': [],  # Trade, Technology, Education, Infrastructure, etc.
                    'key_provisions': [],
                    'value': None,  # Financial value if applicable
                    'duration': None,
                    'source_type': None,  # Government, News, Academic, Think Tank, etc.
                    'source_credibility': None  # High, Medium, Low
                },
                'evidence': {
                    'page_title': None,
                    'relevant_text': None,
                    'official_source': False,
                    'requires_translation': False
                },
                'red_flags': {
                    'is_spam': False,
                    'is_unrelated': False,
                    'is_duplicate': False,
                    'is_news_about_agreement': False,  # Not the agreement itself
                    'geographic_mismatch': False
                }
            }
        }

        template_file = self.verified_dir / 'VERIFICATION_TEMPLATE.json'
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        print(f"OK Verification template saved: {template_file}")

        return template

    def create_clean_database(self):
        """Initialize clean database structure"""
        clean_db = {
            'database_version': '2.0_CLEAN',
            'created': datetime.now().isoformat(),
            'verification_standard': 'MANUAL_ONLY',
            'total_verified': 0,
            'agreements': {
                'bilateral_treaties': [],
                'mous': [],
                'trade_agreements': [],
                'investment_agreements': [],
                'sister_cities': [],
                'university_partnerships': [],
                'research_cooperation': [],
                'infrastructure_projects': [],
                'other': []
            },
            'by_country': {},
            'by_year': {},
            'verification_log': []
        }

        db_file = self.verified_dir / 'CLEAN_DATABASE.json'
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(clean_db, f, indent=2, ensure_ascii=False)

        print(f"OK Clean database initialized: {db_file}")

        return clean_db

    def generate_status_report(self):
        """Generate status report"""
        report = {
            'title': 'DATA QUARANTINE AND CLEANUP STATUS',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'original_claimed_agreements': 4579,
                'after_basic_filter': 640,
                'iceland_false_positive_rate': '100%',
                'estimated_total_false_positives': 'Unknown - requires manual verification',
                'verified_clean_agreements': 0
            },
            'actions_taken': [
                'All existing data quarantined',
                'Clean directory structure created',
                'Manual review batches prepared',
                'Verification template created',
                'Clean database initialized'
            ],
            'next_steps': [
                '1. Manually review each URL batch',
                '2. Visit actual URLs to verify content',
                '3. Check for official government sources',
                '4. Document verified agreements only',
                '5. Build clean database from scratch'
            ],
            'known_contamination': [
                'Industrial machinery spam',
                'Stock photo sites',
                'Language learning sites',
                'Dating sites',
                'Unrelated news articles',
                'Geographic mismatches',
                'False pattern matches'
            ]
        }

        report_file = self.verified_dir / f'CLEANUP_STATUS_{datetime.now().strftime("%Y%m%d")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("\n" + "="*80)
        print("STATUS REPORT")
        print("="*80)
        print(f"Original claimed agreements: {report['summary']['original_claimed_agreements']}")
        print(f"After basic filter: {report['summary']['after_basic_filter']}")
        print(f"Iceland false positive rate: {report['summary']['iceland_false_positive_rate']}")
        print(f"Verified clean agreements: {report['summary']['verified_clean_agreements']}")
        print(f"\nReport saved: {report_file}")

        return report

def main():
    """Execute quarantine and cleanup"""
    manager = DataQuarantineManager()

    # Create structure
    manager.create_quarantine_structure()

    # Quarantine all existing data
    quarantine_log = manager.quarantine_all_data()

    # Extract for manual review
    total_batches = manager.extract_for_manual_review()

    # Create verification template
    manager.create_verification_template()

    # Initialize clean database
    manager.create_clean_database()

    # Generate status report
    manager.generate_status_report()

    print("\n" + "="*80)
    print("QUARANTINE COMPLETE")
    print("="*80)
    print(f"OK All contaminated data moved to: QUARANTINE_DATA/")
    print(f"OK Clean workspace created at: VERIFIED_CLEAN/")
    print(f"OK {total_batches} batches ready for manual review in: MANUAL_REVIEW_QUEUE/")
    print("\nNEXT STEP: Manually review each URL to verify actual agreements")
    print("="*80)

if __name__ == "__main__":
    main()
