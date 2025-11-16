#!/usr/bin/env python3
"""
EU MCF Report Downloader + Hasher
==================================

Downloads and processes reports identified by eu_mcf_report_finder.py

For each report:
1) Download to structured directory
2) Save as {year}_{publisher_org_snake}_{slug_title}_{lang}.{ext}
3) Compute SHA-256 hash and file size
4) Extract page count (for PDFs)
5) Emit JSON with processing results

Output: Enhanced JSON ready for database import
"""

import json
import hashlib
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import time
from PyPDF2 import PdfReader
import io

class EUMCFReportDownloader:
    """Download and hash EU MCF reports."""

    def __init__(self, input_file: str, output_dir: str = "data/external/eu_mcf_reports/downloads"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        self.results = []

    def slugify(self, text: str, max_length: int = 60) -> str:
        """Convert text to filename-safe slug."""
        # Remove special characters
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        # Replace spaces with underscores
        slug = re.sub(r'[-\s]+', '_', slug)
        # Truncate
        return slug[:max_length]

    def compute_sha256(self, content: bytes) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content).hexdigest()

    def extract_pdf_pages(self, content: bytes) -> Optional[int]:
        """Extract page count from PDF content."""
        try:
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            return len(reader.pages)
        except Exception as e:
            print(f"    [WARN] Could not extract page count: {e}")
            return None

    def download_and_process(self, report: Dict) -> Dict:
        """Download report and extract metadata."""
        result = {
            'title': report['title'],
            'publisher_org': report['publisher_org'],
            'download_url': report['download_url'],
            'canonical_url': report['canonical_url'],
            'publication_date_iso': report.get('publication_date_iso'),
            'year': report.get('year'),
            'language': report.get('language', 'en'),
            'file_ext': report['file_ext'],
            'topics': report.get('topics', []),
            'region_group': report.get('region_group', []),
            'country_list': report.get('country_list', []),
            'mcf_flag': report.get('mcf_flag', 0),
            'europe_focus_flag': report.get('europe_focus_flag', 0),
            'arctic_flag': report.get('arctic_flag', 0),
            'abstract': report.get('abstract'),
            'download_status': 'pending',
            'extraction_ok': False,
            'extraction_notes': []
        }

        try:
            # Download file
            print(f"  Downloading: {report['title'][:60]}...")
            response = self.session.get(report['download_url'], timeout=30)
            response.raise_for_status()
            content = response.content

            # Generate filename
            year_str = str(report.get('year', 'unknown'))
            pub_slug = self.slugify(report['publisher_org'])
            title_slug = self.slugify(report['title'])
            lang = report.get('language', 'en')
            ext = report['file_ext']

            filename = f"{year_str}_{pub_slug}_{title_slug}_{lang}.{ext}"
            filepath = self.output_dir / filename

            # Check for duplicate (by hash)
            file_hash = self.compute_sha256(content)
            result['hash_sha256'] = file_hash
            result['file_size_bytes'] = len(content)

            # Check if we already have this file
            existing = None
            for existing_file in self.output_dir.glob(f"*{ext}"):
                if existing_file.stat().st_size == len(content):
                    with open(existing_file, 'rb') as f:
                        if self.compute_sha256(f.read()) == file_hash:
                            existing = existing_file
                            break

            if existing:
                print(f"    [SKIP] Duplicate file already exists: {existing.name}")
                result['saved_path'] = str(existing)
                result['download_status'] = 'duplicate'
                result['extraction_notes'].append(f"Duplicate of existing file: {existing.name}")
            else:
                # Save file
                with open(filepath, 'wb') as f:
                    f.write(content)
                result['saved_path'] = str(filepath)
                result['download_status'] = 'success'
                print(f"    [OK] Saved: {filename}")

            # Extract page count for PDFs
            if ext == 'pdf':
                pages = self.extract_pdf_pages(content)
                if pages:
                    result['pages'] = pages
                    result['extraction_ok'] = True
                    result['extraction_notes'].append(f"Extracted {pages} pages")
                else:
                    result['pages'] = None
                    result['extraction_notes'].append("Could not extract page count")

            # Extract metadata from title/abstract
            result['collection_date_utc'] = datetime.utcnow().isoformat()

            return result

        except requests.exceptions.RequestException as e:
            print(f"    [ERROR] Download failed: {e}")
            result['download_status'] = 'failed'
            result['extraction_notes'].append(f"Download error: {str(e)}")
            return result

        except Exception as e:
            print(f"    [ERROR] Processing failed: {e}")
            result['download_status'] = 'error'
            result['extraction_notes'].append(f"Processing error: {str(e)}")
            return result

    def process_all(self) -> Dict:
        """Process all reports from finder output."""
        print("="*80)
        print("EU MCF REPORT DOWNLOADER + HASHER")
        print("="*80)

        # Load finder results
        with open(self.input_file, 'r', encoding='utf-8') as f:
            finder_data = json.load(f)

        reports = finder_data.get('reports', [])
        print(f"Found {len(reports)} reports to download")
        print(f"Output directory: {self.output_dir}")
        print("="*80)

        results = []
        for i, report in enumerate(reports, 1):
            print(f"\n[{i}/{len(reports)}] {report['publisher_org']}")
            result = self.download_and_process(report)
            results.append(result)
            time.sleep(1)  # Rate limiting

        # Generate summary
        successful = sum(1 for r in results if r['download_status'] in ['success', 'duplicate'])
        failed = sum(1 for r in results if r['download_status'] == 'failed')
        duplicates = sum(1 for r in results if r['download_status'] == 'duplicate')

        # Save enhanced results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir.parent / f"eu_mcf_reports_processed_{timestamp}.json"

        output_data = {
            'generated_at': datetime.now().isoformat(),
            'source_file': str(self.input_file),
            'total_reports': len(results),
            'successful_downloads': successful - duplicates,
            'duplicates': duplicates,
            'failed_downloads': failed,
            'total_size_bytes': sum(r.get('file_size_bytes', 0) for r in results),
            'by_publisher': {},
            'by_status': {
                'success': successful - duplicates,
                'duplicate': duplicates,
                'failed': failed
            },
            'reports': results
        }

        # Statistics by publisher
        for result in results:
            pub = result['publisher_org']
            if pub not in output_data['by_publisher']:
                output_data['by_publisher'][pub] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0
                }
            output_data['by_publisher'][pub]['total'] += 1
            if result['download_status'] in ['success', 'duplicate']:
                output_data['by_publisher'][pub]['successful'] += 1
            else:
                output_data['by_publisher'][pub]['failed'] += 1

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print("\n" + "="*80)
        print("DOWNLOAD COMPLETE")
        print("="*80)
        print(f"Total reports: {len(results)}")
        print(f"Successful downloads: {successful - duplicates}")
        print(f"Duplicates skipped: {duplicates}")
        print(f"Failed: {failed}")
        print(f"Total size: {output_data['total_size_bytes'] / (1024*1024):.2f} MB")
        print(f"\nBy publisher:")
        for pub, stats in sorted(output_data['by_publisher'].items()):
            print(f"  {pub}: {stats['successful']}/{stats['total']} successful")
        print(f"\nSaved to: {output_file}")
        print(f"Files in: {self.output_dir}")
        print("="*80)
        print("\n[OK] Ready for database import using import_thinktank_reports.py")

        return output_data


def main():
    """Main execution."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python eu_mcf_report_downloader.py <finder_output.json>")
        print("\nExample:")
        print("  python eu_mcf_report_downloader.py data/external/eu_mcf_reports/eu_mcf_reports_20251010_120000.json")
        sys.exit(1)

    input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"[ERROR] Input file not found: {input_file}")
        sys.exit(1)

    downloader = EUMCFReportDownloader(input_file)
    results = downloader.process_all()


if __name__ == "__main__":
    main()
