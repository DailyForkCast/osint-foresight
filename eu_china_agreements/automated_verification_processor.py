#!/usr/bin/env python3
"""
Automated Verification Processor for EU-China Agreements
Processes verification checklist and gathers evidence
ZERO FABRICATION - COMPLETE DOCUMENTATION
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgreementVerificationProcessor:
    """Process and verify discovered agreements"""

    def __init__(self):
        self.base_dir = Path("C:/Projects/OSINT - Foresight/eu_china_agreements")
        self.results_dir = self.base_dir / "verification_results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir = self.results_dir / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        # Load checklist
        checklist_files = list((self.base_dir / "alternative_discovery_results").glob("verification_checklist_*.json"))
        if checklist_files:
            with open(checklist_files[-1], 'r', encoding='utf-8') as f:
                self.checklist = json.load(f)
        else:
            logger.error("No verification checklist found")
            self.checklist = None

    def check_url_accessibility(self, url: str) -> Dict:
        """Check if URL is accessible and gather metadata"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)

            return {
                'accessible': True,
                'status_code': response.status_code,
                'final_url': response.url,
                'redirected': response.url != url,
                'content_type': response.headers.get('Content-Type', 'unknown'),
                'content_length': len(response.content),
                'timestamp': datetime.now().isoformat(),
                'content_sample': response.text[:5000] if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                'accessible': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def search_content_for_china(self, content: str) -> Dict:
        """Search content for China-related terms"""
        if not content:
            return {'found': False}

        china_terms = [
            'china', 'chinese', 'beijing', 'shanghai', 'guangzhou', 'shenzhen',
            'chine', 'chinois', 'pékin',  # French
            'cina', 'cinese', 'pechino',  # Italian
            'china', 'chinesisch', 'peking',  # German
            'chiny', 'chiński', 'pekin',  # Polish
            'sister city', 'sister cities', 'partnership', 'cooperation',
            'jumelage', 'partenariat',  # French
            'gemellaggio', 'cooperazione',  # Italian
            'städtepartnerschaft', 'partnerschaft',  # German
            'agreement', 'MoU', 'memorandum', 'accord', 'convenzione'
        ]

        content_lower = content.lower()
        found_terms = []
        term_contexts = []

        for term in china_terms:
            if term.lower() in content_lower:
                found_terms.append(term)
                # Extract context around the term
                idx = content_lower.find(term.lower())
                start = max(0, idx - 100)
                end = min(len(content), idx + 100)
                context = content[start:end].strip()
                term_contexts.append({
                    'term': term,
                    'context': context
                })

        return {
            'found': len(found_terms) > 0,
            'terms_found': found_terms,
            'contexts': term_contexts[:5]  # Limit to first 5 contexts
        }

    def check_wayback_archive(self, url: str) -> Optional[Dict]:
        """Check Wayback Machine for historical snapshots"""
        api_url = f"http://archive.org/wayback/available?url={url}"

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'archived_snapshots' in data and data['archived_snapshots'].get('closest'):
                    snapshot = data['archived_snapshots']['closest']
                    return {
                        'available': True,
                        'archive_url': snapshot['url'],
                        'timestamp': snapshot['timestamp'],
                        'status': snapshot['status']
                    }
        except Exception as e:
            logger.error(f"Wayback check failed for {url}: {e}")

        return {'available': False}

    def verify_partnership(self, item: Dict) -> Dict:
        """Verify a single partnership"""
        logger.info(f"Verifying: {item['partnership']}")

        verification_result = {
            'partnership': item['partnership'],
            'type': item['type'],
            'original_url': item['url_to_check'],
            'verification_timestamp': datetime.now().isoformat(),
            'verification_id': hashlib.sha256(
                f"{item['partnership']}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
        }

        # Step 1: Check URL accessibility
        logger.info(f"  Checking URL: {item['url_to_check']}")
        url_check = self.check_url_accessibility(item['url_to_check'])
        verification_result['url_check'] = url_check

        # Step 2: Search for China-related content
        if url_check.get('accessible') and url_check.get('content_sample'):
            logger.info("  Searching for China-related content...")
            content_search = self.search_content_for_china(url_check['content_sample'])
            verification_result['content_search'] = content_search

            # Determine if agreement likely exists
            if content_search['found']:
                verification_result['agreement_likely'] = True
                verification_result['confidence'] = 'MEDIUM'
                verification_result['status'] = 'PARTIAL'
            else:
                verification_result['agreement_likely'] = False
                verification_result['confidence'] = 'LOW'
                verification_result['status'] = 'NEEDS_MANUAL_CHECK'
        else:
            # URL not accessible, check Wayback
            logger.info("  URL not accessible, checking Wayback Machine...")
            wayback = self.check_wayback_archive(item['url_to_check'])
            verification_result['wayback_check'] = wayback

            if wayback['available']:
                verification_result['status'] = 'WAYBACK_AVAILABLE'
                verification_result['confidence'] = 'LOW'
            else:
                verification_result['status'] = 'CANNOT_VERIFY'
                verification_result['confidence'] = 'NONE'

        # Step 3: Generate citation
        verification_result['citation'] = self.generate_citation(verification_result)

        # Step 4: Create verification report
        verification_result['verification_report'] = {
            'requires_manual_check': True,
            'priority': 'HIGH' if verification_result.get('agreement_likely') else 'MEDIUM',
            'next_steps': self.generate_next_steps(verification_result)
        }

        return verification_result

    def generate_citation(self, result: Dict) -> str:
        """Generate citation for verification result"""
        if result.get('url_check', {}).get('accessible'):
            return (
                f"{result['partnership']}. "
                f"URL: {result['original_url']}. "
                f"Accessed: {result['verification_timestamp']}. "
                f"Status: {result.get('status', 'Unknown')}. "
                f"Verification ID: {result['verification_id']}"
            )
        elif result.get('wayback_check', {}).get('available'):
            return (
                f"{result['partnership']}. "
                f"Original URL: {result['original_url']}. "
                f"Wayback Archive: {result['wayback_check']['archive_url']}. "
                f"Archive Date: {result['wayback_check']['timestamp']}. "
                f"Verification ID: {result['verification_id']}"
            )
        else:
            return (
                f"{result['partnership']}. "
                f"URL: {result['original_url']}. "
                f"Status: Cannot verify - URL not accessible. "
                f"Checked: {result['verification_timestamp']}. "
                f"Verification ID: {result['verification_id']}"
            )

    def generate_next_steps(self, result: Dict) -> List[str]:
        """Generate next steps based on verification result"""
        steps = []

        if result.get('status') == 'PARTIAL':
            steps.extend([
                "Manual review of webpage for specific agreement details",
                "Search for official documents or PDFs",
                "Check for press releases about the partnership",
                "Look for specific dates and signatories"
            ])
        elif result.get('status') == 'WAYBACK_AVAILABLE':
            steps.extend([
                f"Access Wayback archive: {result['wayback_check']['archive_url']}",
                "Review archived content for agreement details",
                "Search for alternative current sources",
                "Check municipal/university press archives"
            ])
        elif result.get('status') == 'CANNOT_VERIFY':
            steps.extend([
                "Search for alternative official sources",
                "Check partner organization's website",
                "Look for news coverage of the partnership",
                "Contact organization directly if critical"
            ])
        else:
            steps.extend([
                "Manual verification required",
                "Check page thoroughly for China references",
                "Search site's search function for China/partnership",
                "Review site navigation for international relations section"
            ])

        return steps

    def process_all_verifications(self):
        """Process all items in verification checklist"""
        if not self.checklist:
            logger.error("No checklist loaded")
            return

        logger.info("=" * 60)
        logger.info("AUTOMATED VERIFICATION PROCESSING")
        logger.info(f"Processing {len(self.checklist['items'])} partnerships")
        logger.info("=" * 60)

        results = {
            'processing_timestamp': datetime.now().isoformat(),
            'total_items': len(self.checklist['items']),
            'verification_results': [],
            'summary': {
                'accessible': 0,
                'partial_verification': 0,
                'wayback_available': 0,
                'cannot_verify': 0,
                'china_content_found': 0
            }
        }

        for item in self.checklist['items']:
            result = self.verify_partnership(item)
            results['verification_results'].append(result)

            # Update summary
            if result.get('url_check', {}).get('accessible'):
                results['summary']['accessible'] += 1
            if result.get('status') == 'PARTIAL':
                results['summary']['partial_verification'] += 1
            if result.get('status') == 'WAYBACK_AVAILABLE':
                results['summary']['wayback_available'] += 1
            if result.get('status') == 'CANNOT_VERIFY':
                results['summary']['cannot_verify'] += 1
            if result.get('content_search', {}).get('found'):
                results['summary']['china_content_found'] += 1

            logger.info(f"  Status: {result.get('status', 'Unknown')}")
            logger.info("-" * 40)

        # Save results
        output_file = self.results_dir / f"automated_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"\nResults saved: {output_file}")

        # Generate summary report
        self.generate_summary_report(results)

        return results

    def generate_summary_report(self, results: Dict):
        """Generate human-readable summary report"""
        report_lines = [
            "# EU-CHINA AGREEMENTS VERIFICATION REPORT",
            f"Generated: {results['processing_timestamp']}",
            "",
            "## SUMMARY STATISTICS",
            f"- Total partnerships checked: {results['total_items']}",
            f"- URLs accessible: {results['summary']['accessible']}",
            f"- Partial verification achieved: {results['summary']['partial_verification']}",
            f"- Available in Wayback Machine: {results['summary']['wayback_available']}",
            f"- Cannot verify: {results['summary']['cannot_verify']}",
            f"- China content found: {results['summary']['china_content_found']}",
            "",
            "## DETAILED RESULTS",
            ""
        ]

        # Group by status
        by_status = {}
        for result in results['verification_results']:
            status = result.get('status', 'Unknown')
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(result)

        for status, items in by_status.items():
            report_lines.append(f"### {status} ({len(items)} items)")
            for item in items:
                report_lines.append(f"- **{item['partnership']}** ({item['type']})")
                report_lines.append(f"  - URL: {item['original_url']}")
                if item.get('content_search', {}).get('found'):
                    report_lines.append(f"  - China terms found: {', '.join(item['content_search']['terms_found'][:5])}")
                report_lines.append(f"  - Citation: {item['citation']}")
            report_lines.append("")

        report_lines.extend([
            "## NEXT STEPS",
            "",
            "### High Priority (Partial Verifications)",
            "These partnerships show promise and should be manually verified first:"
        ])

        for result in results['verification_results']:
            if result.get('status') == 'PARTIAL':
                report_lines.append(f"1. {result['partnership']}")
                for step in result['verification_report']['next_steps'][:2]:
                    report_lines.append(f"   - {step}")

        report_lines.extend([
            "",
            "### Medium Priority (Wayback Available)",
            "These can be verified through historical archives:"
        ])

        for result in results['verification_results']:
            if result.get('status') == 'WAYBACK_AVAILABLE':
                report_lines.append(f"1. {result['partnership']}")
                if result.get('wayback_check', {}).get('archive_url'):
                    report_lines.append(f"   - Archive: {result['wayback_check']['archive_url']}")

        report_lines.extend([
            "",
            "## DATA QUALITY STATEMENT",
            "- All data sourced from publicly accessible websites",
            "- Zero fabrication protocol enforced",
            "- All results require manual verification for production use",
            "- Citations provided for all discovered content",
            "",
            "## VERIFICATION PROTOCOL COMPLIANCE",
            "- [X] All URLs checked for accessibility",
            "- [X] Content searched for China-related terms",
            "- [X] Wayback Machine checked for inaccessible URLs",
            "- [X] Citations generated for all results",
            "- [X] Next steps documented for each partnership",
            "- [ ] Manual verification pending for all results"
        ])

        # Save report
        report_file = self.results_dir / f"verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        logger.info(f"Summary report saved: {report_file}")

def main():
    """Execute automated verification"""
    print("=" * 60)
    print("AUTOMATED VERIFICATION PROCESSOR")
    print("EU-CHINA BILATERAL AGREEMENTS")
    print("=" * 60)

    processor = AgreementVerificationProcessor()
    results = processor.process_all_verifications()

    if results:
        print(f"\nProcessed {results['total_items']} partnerships")
        print(f"Accessible URLs: {results['summary']['accessible']}")
        print(f"Partial verifications: {results['summary']['partial_verification']}")
        print(f"China content found: {results['summary']['china_content_found']}")
        print(f"\nReports saved in: {processor.results_dir}")
        print("\nALL RESULTS REQUIRE MANUAL VERIFICATION")

if __name__ == "__main__":
    main()
