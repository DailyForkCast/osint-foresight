#!/usr/bin/env python3
"""
Batch URL Checker for Policy Documents

Quickly checks all URLs for 404s and other HTTP errors
"""

import sqlite3
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json

def check_url(doc_id, url, country, title):
    """
    Check if URL is accessible
    Returns: (doc_id, country, title, url, status_code, error_message)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)

        return {
            'doc_id': doc_id,
            'country': country,
            'title': title[:60],
            'url': url,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'error': None
        }
    except requests.exceptions.Timeout:
        return {
            'doc_id': doc_id,
            'country': country,
            'title': title[:60],
            'url': url,
            'status_code': None,
            'success': False,
            'error': 'Timeout'
        }
    except requests.exceptions.RequestException as e:
        return {
            'doc_id': doc_id,
            'country': country,
            'title': title[:60],
            'url': url,
            'status_code': None,
            'success': False,
            'error': str(e)[:100]
        }
    except Exception as e:
        return {
            'doc_id': doc_id,
            'country': country,
            'title': title[:60],
            'url': url,
            'status_code': None,
            'success': False,
            'error': f'Unexpected: {str(e)[:100]}'
        }

def check_all_urls(db_path, output_file=None, max_workers=10):
    """
    Check all policy document URLs in parallel
    """
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT document_id, country_code, document_title, document_url
        FROM policy_documents
        ORDER BY country_code
    ''')

    documents = cursor.fetchall()
    conn.close()

    print("=" * 70)
    print("POLICY DOCUMENT URL BATCH CHECK")
    print("=" * 70)
    print(f"\nTotal documents: {len(documents)}")
    print(f"Checking URLs with {max_workers} parallel connections...")
    print()

    results = []
    successful = 0
    failed = 0

    # Check URLs in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(check_url, doc[0], doc[3], doc[1], doc[2]): doc
            for doc in documents
        }

        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)

            if result['success']:
                print(f"[{i}/{len(documents)}] [OK] {result['country']} - {result['title'][:50]}")
                successful += 1
            else:
                print(f"[{i}/{len(documents)}] [FAIL] {result['country']} - {result['title'][:50]}")
                print(f"          Status: {result['status_code']}, Error: {result['error']}")
                failed += 1

    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"\nSuccessful (200 OK): {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(documents)}")
    print()

    # Group failures by country
    failures_by_country = {}
    for result in results:
        if not result['success']:
            country = result['country']
            if country not in failures_by_country:
                failures_by_country[country] = []
            failures_by_country[country].append(result)

    if failures_by_country:
        print("FAILURES BY COUNTRY:")
        print()
        for country in sorted(failures_by_country.keys()):
            print(f"{country}: {len(failures_by_country[country])} failed")
            for failure in failures_by_country[country]:
                print(f"  - {failure['title']}")
                print(f"    URL: {failure['url']}")
                issue = failure['error'] if failure['error'] else f"HTTP {failure['status_code']}"
                print(f"    Issue: {issue}")
                print()

    # Save detailed results
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'checked_at': datetime.now().isoformat(),
                'total_documents': len(documents),
                'successful': successful,
                'failed': failed,
                'results': results
            }, f, indent=2)
        print(f"[OK] Detailed results saved to: {output_file}")
        print()

    return results

if __name__ == '__main__':
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    output_file = f"C:/Projects/OSINT-Foresight/analysis/policy_url_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    print("Checking all 98 policy document URLs...")
    print("This will take ~30-60 seconds")
    print()

    results = check_all_urls(db_path, output_file, max_workers=10)

    print("Next step: Review failures and search for correct URLs")
    print("Tip: Use the findings to update your verification CSV")
    print()
