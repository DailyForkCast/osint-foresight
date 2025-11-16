#!/usr/bin/env python3
"""
Netherlands + Semiconductors Focused Finder
============================================

Target: Dutch and EU semiconductor resilience, export controls, and ASML-related research

Focus Areas:
  - Netherlands semiconductor policy
  - ASML export controls to China
  - EU Chips Act implementation
  - Dutch-China technology relations
  - Semiconductor supply chain security

Sources:
  - Dutch Government (Rijksoverheid)
  - Dutch Parliament (Tweede Kamer)
  - Clingendael Institute
  - Rathenau Institute
  - EC DG GROW, DG TRADE
  - European Chips Act documentation
  - Dutch think tanks and research institutes

Output: JSON with semiconductor-focused reports (2015-present)
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import time
from pathlib import Path

class NetherlandsSemiconductorFinder:
    """Find Netherlands and semiconductor-related policy reports."""

    def __init__(self, output_dir: str = "data/external/netherlands_semiconductors"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Netherlands + Semiconductors keywords
        self.netherlands_keywords = [
            'netherlands', 'dutch', 'holland', 'asml', 'eindhoven',
            'benelux', 'amsterdam', 'the hague'
        ]

        self.semiconductor_keywords = [
            'semiconductor', 'chip', 'asml', 'lithography', 'euv',
            'microchip', 'integrated circuit', 'fabrication', 'foundry',
            'tsmc', 'wafer', 'nanometer', 'photonics'
        ]

        self.policy_keywords = [
            'export control', 'export restriction', 'technology transfer',
            'chips act', 'semiconductor resilience', 'supply chain',
            'strategic autonomy', 'dual-use', 'trade policy',
            'innovation policy', 'industrial strategy'
        ]

        self.china_keywords = [
            'china', 'chinese', 'prc', 'beijing', 'sino-'
        ]

        self.results = []

    def is_semiconductor_policy(self, text: str) -> tuple[bool, list]:
        """Check if content is about semiconductor policy."""
        text_lower = text.lower()

        has_semiconductor = any(kw in text_lower for kw in self.semiconductor_keywords)
        has_policy = any(kw in text_lower for kw in self.policy_keywords)
        has_netherlands = any(kw in text_lower for kw in self.netherlands_keywords)
        has_china = any(kw in text_lower for kw in self.china_keywords)

        topics = []
        if has_semiconductor:
            topics.append('semiconductors')
        if 'export control' in text_lower or 'export restriction' in text_lower:
            topics.append('export_controls')
        if 'supply chain' in text_lower:
            topics.append('supply_chain')
        if 'chips act' in text_lower:
            topics.append('chips_act')
        if 'asml' in text_lower:
            topics.append('asml')

        # Must have semiconductor AND (Netherlands OR policy)
        is_relevant = has_semiconductor and (has_netherlands or has_policy)

        return (is_relevant, topics)

    def verify_download_link(self, url: str) -> Optional[Dict]:
        """Verify that URL is a direct download link for PDF/DOCX."""
        try:
            response = self.session.head(url, allow_redirects=True, timeout=10)
            content_type = response.headers.get('Content-Type', '').lower()

            if 'pdf' in content_type:
                return {'url': url, 'type': 'pdf', 'content_type': content_type}
            elif 'word' in content_type or 'docx' in content_type:
                return {'url': url, 'type': 'docx', 'content_type': content_type}
            elif url.endswith('.pdf'):
                return {'url': url, 'type': 'pdf', 'content_type': 'application/pdf'}
            elif url.endswith('.docx'):
                return {'url': url, 'type': 'docx', 'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}

            return None

        except Exception as e:
            print(f"  [WARN] Could not verify {url}: {e}")
            return None

    def extract_date_from_text(self, text: str) -> Optional[Dict]:
        """Extract publication date from text."""
        patterns = [
            r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{2})/(\d{2})/(\d{4})',
            r'(\d{4})',  # Year only
        ]

        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()

                if len(groups) == 3 and groups[1].lower() in months:
                    day, month_name, year = groups
                    return {
                        'year': int(year),
                        'month': months[month_name.lower()],
                        'day': int(day),
                        'iso': f"{year}-{months[month_name.lower()]:02d}-{int(day):02d}"
                    }
                elif len(groups) == 2 and groups[0].lower() in months:
                    month_name, year = groups
                    return {
                        'year': int(year),
                        'month': months[month_name.lower()],
                        'day': None,
                        'iso': f"{year}-{months[month_name.lower()]:02d}-01"
                    }
                elif len(groups) == 3 and groups[0].isdigit() and len(groups[0]) == 4:
                    year, month, day = groups
                    return {
                        'year': int(year),
                        'month': int(month),
                        'day': int(day),
                        'iso': f"{year}-{month}-{day}"
                    }
                elif len(groups) == 1 and len(groups[0]) == 4:
                    year = groups[0]
                    return {
                        'year': int(year),
                        'month': None,
                        'day': None,
                        'iso': f"{year}-01-01"
                    }

        return None

    def scrape_clingendael(self) -> List[Dict]:
        """Scrape Clingendael Institute (Dutch international relations think tank)."""
        print("\n[Clingendael] Scraping https://www.clingendael.org/publications...")
        results = []

        try:
            # Search for semiconductor and China-related publications
            search_terms = ['semiconductor', 'chips', 'asml', 'technology china']

            for term in search_terms:
                url = f"https://www.clingendael.org/search?search={term.replace(' ', '%20')}"
                response = self.session.get(url, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')

                for item in soup.find_all(['article', 'div'], class_=re.compile(r'publication|result|item')):
                    try:
                        title_elem = item.find(['h2', 'h3', 'a'])
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)

                        link_elem = item.find('a', href=True)
                        if not link_elem:
                            continue
                        link = urljoin(url, link_elem['href'])

                        desc_elem = item.find(['p', 'div'], class_=re.compile(r'description|summary|excerpt'))
                        description = desc_elem.get_text(strip=True) if desc_elem else ""

                        combined_text = f"{title} {description}"
                        is_relevant, topics = self.is_semiconductor_policy(combined_text)

                        if is_relevant:
                            # Visit detail page
                            detail_response = self.session.get(link, timeout=10)
                            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

                            pdf_link = detail_soup.find('a', href=re.compile(r'\.pdf$|/download'))
                            if pdf_link:
                                download_url = urljoin(link, pdf_link['href'])
                                verified = self.verify_download_link(download_url)

                                if verified:
                                    date_elem = detail_soup.find(['time', 'span'], class_=re.compile(r'date'))
                                    date_info = None
                                    if date_elem:
                                        date_info = self.extract_date_from_text(date_elem.get_text())

                                    if date_info and date_info['year'] < 2015:
                                        continue

                                    has_china = any(kw in combined_text.lower() for kw in self.china_keywords)

                                    results.append({
                                        'title': title,
                                        'publisher_org': 'Clingendael Institute',
                                        'publication_date_iso': date_info['iso'] if date_info else None,
                                        'year': date_info['year'] if date_info else None,
                                        'month': date_info['month'] if date_info else None,
                                        'day': date_info['day'] if date_info else None,
                                        'canonical_url': link,
                                        'download_url': download_url,
                                        'language': 'en',
                                        'authors': None,
                                        'region_group': ['europe', 'east_asia'] if has_china else ['europe'],
                                        'country_list': ['NL', 'CN'] if has_china else ['NL'],
                                        'topics': topics,
                                        'subtopics': [],
                                        'mcf_flag': 0,
                                        'europe_focus_flag': 1,
                                        'arctic_flag': 0,
                                        'doc_type': 'report',
                                        'file_ext': verified['type'],
                                        'abstract': description[:500] if description else None
                                    })
                                    print(f"  [OK] Found: {title[:60]}...")

                            time.sleep(0.5)

                    except Exception as e:
                        print(f"  [WARN] Error processing item: {e}")
                        continue

                time.sleep(1)

        except Exception as e:
            print(f"  [ERROR] Failed to scrape Clingendael: {e}")

        return results

    def scrape_rathenau(self) -> List[Dict]:
        """Scrape Rathenau Institute (Dutch technology assessment)."""
        print("\n[Rathenau] Scraping https://www.rathenau.nl/en/publications...")
        results = []

        try:
            url = "https://www.rathenau.nl/en/publications"
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            for item in soup.find_all(['article', 'div'], class_=re.compile(r'publication|teaser')):
                try:
                    title_elem = item.find(['h2', 'h3', 'a'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)

                    # Check if semiconductor-related
                    if not any(kw in title.lower() for kw in self.semiconductor_keywords + ['technology', 'innovation', 'china']):
                        continue

                    link_elem = item.find('a', href=True)
                    if not link_elem:
                        continue
                    link = urljoin(url, link_elem['href'])

                    desc_elem = item.find(['p', 'div'], class_=re.compile(r'description|summary'))
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    combined_text = f"{title} {description}"
                    is_relevant, topics = self.is_semiconductor_policy(combined_text)

                    if is_relevant:
                        # Visit detail page
                        detail_response = self.session.get(link, timeout=10)
                        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

                        pdf_link = detail_soup.find('a', href=re.compile(r'\.pdf$'))
                        if pdf_link:
                            download_url = urljoin(link, pdf_link['href'])
                            verified = self.verify_download_link(download_url)

                            if verified:
                                date_elem = detail_soup.find(['time', 'span'], class_=re.compile(r'date'))
                                date_info = None
                                if date_elem:
                                    date_info = self.extract_date_from_text(date_elem.get_text())

                                if date_info and date_info['year'] < 2015:
                                    continue

                                has_china = any(kw in combined_text.lower() for kw in self.china_keywords)

                                results.append({
                                    'title': title,
                                    'publisher_org': 'Rathenau Institute',
                                    'publication_date_iso': date_info['iso'] if date_info else None,
                                    'year': date_info['year'] if date_info else None,
                                    'month': date_info['month'] if date_info else None,
                                    'day': date_info['day'] if date_info else None,
                                    'canonical_url': link,
                                    'download_url': download_url,
                                    'language': 'en',
                                    'authors': None,
                                    'region_group': ['europe', 'east_asia'] if has_china else ['europe'],
                                    'country_list': ['NL', 'CN'] if has_china else ['NL'],
                                    'topics': topics,
                                    'subtopics': [],
                                    'mcf_flag': 0,
                                    'europe_focus_flag': 1,
                                    'arctic_flag': 0,
                                    'doc_type': 'report',
                                    'file_ext': verified['type'],
                                    'abstract': description[:500] if description else None
                                })
                                print(f"  [OK] Found: {title[:60]}...")

                        time.sleep(0.5)

                except Exception as e:
                    print(f"  [WARN] Error processing item: {e}")
                    continue

        except Exception as e:
            print(f"  [ERROR] Failed to scrape Rathenau: {e}")

        return results

    def scrape_ec_chips_act(self) -> List[Dict]:
        """Scrape EC documentation on European Chips Act."""
        print("\n[EC Chips Act] Searching EC documentation...")
        results = []

        try:
            # Known EC Chips Act documentation URLs
            chips_act_urls = [
                "https://ec.europa.eu/commission/presscorner/detail/en/ip_23_510",  # Chips Act announcement
                "https://digital-strategy.ec.europa.eu/en/policies/european-chips-act",
            ]

            for url in chips_act_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Look for PDF links
                    pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$'))

                    for pdf_link in pdf_links:
                        try:
                            download_url = urljoin(url, pdf_link['href'])
                            verified = self.verify_download_link(download_url)

                            if verified:
                                # Get title from link text or nearby heading
                                title = pdf_link.get_text(strip=True) or "European Chips Act Documentation"

                                # Extract date from page
                                date_elem = soup.find(['time', 'span'], class_=re.compile(r'date'))
                                date_info = None
                                if date_elem:
                                    date_info = self.extract_date_from_text(date_elem.get_text())

                                if not date_info:
                                    # Try to extract from URL or filename
                                    date_match = re.search(r'(\d{4})', download_url)
                                    if date_match:
                                        year = int(date_match.group(1))
                                        if year >= 2015:
                                            date_info = {
                                                'year': year,
                                                'month': None,
                                                'day': None,
                                                'iso': f"{year}-01-01"
                                            }

                                if date_info and date_info['year'] >= 2015:
                                    results.append({
                                        'title': title,
                                        'publisher_org': 'European Commission',
                                        'publication_date_iso': date_info['iso'],
                                        'year': date_info['year'],
                                        'month': date_info['month'],
                                        'day': date_info['day'],
                                        'canonical_url': url,
                                        'download_url': download_url,
                                        'language': 'en',
                                        'authors': None,
                                        'region_group': ['europe'],
                                        'country_list': ['EU'],
                                        'topics': ['semiconductors', 'chips_act'],
                                        'subtopics': [],
                                        'mcf_flag': 0,
                                        'europe_focus_flag': 1,
                                        'arctic_flag': 0,
                                        'doc_type': 'policy_document',
                                        'file_ext': verified['type'],
                                        'abstract': 'European Chips Act documentation on semiconductor resilience and strategic autonomy'
                                    })
                                    print(f"  [OK] Found: {title[:60]}...")

                        except Exception as e:
                            print(f"  [WARN] Error processing PDF link: {e}")
                            continue

                    time.sleep(1)

                except Exception as e:
                    print(f"  [WARN] Error processing URL {url}: {e}")
                    continue

        except Exception as e:
            print(f"  [ERROR] Failed to scrape EC Chips Act: {e}")

        return results

    def run_all(self) -> Dict:
        """Run all scrapers and aggregate results."""
        print("="*80)
        print("NETHERLANDS + SEMICONDUCTORS FOCUSED FINDER")
        print("="*80)
        print(f"Target: Dutch and EU semiconductor policy (2015-present)")
        print(f"Focus: ASML, export controls, Chips Act, China relations")
        print(f"Output: Direct-downloadable PDFs/DOCX only")
        print("="*80)

        all_results = []

        # Scrape each source
        all_results.extend(self.scrape_clingendael())
        all_results.extend(self.scrape_rathenau())
        all_results.extend(self.scrape_ec_chips_act())

        # Deduplicate by download URL
        seen_urls = set()
        deduplicated = []
        for result in all_results:
            if result['download_url'] not in seen_urls:
                seen_urls.add(result['download_url'])
                deduplicated.append(result)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"netherlands_semiconductors_{timestamp}.json"

        output_data = {
            'generated_at': datetime.now().isoformat(),
            'filter': 'publication_date >= 2015-01-01, Netherlands + Semiconductors focus',
            'total_found': len(deduplicated),
            'by_publisher': {},
            'by_topic': {},
            'asml_count': sum(1 for r in deduplicated if 'asml' in r.get('topics', [])),
            'china_related': sum(1 for r in deduplicated if 'CN' in r.get('country_list', [])),
            'reports': deduplicated
        }

        # Statistics
        for result in deduplicated:
            pub = result['publisher_org']
            output_data['by_publisher'][pub] = output_data['by_publisher'].get(pub, 0) + 1

            for topic in result['topics']:
                output_data['by_topic'][topic] = output_data['by_topic'].get(topic, 0) + 1

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print("\n" + "="*80)
        print("FINDER COMPLETE")
        print("="*80)
        print(f"Total reports found: {len(deduplicated)}")
        print(f"ASML-related reports: {output_data['asml_count']}")
        print(f"China-related reports: {output_data['china_related']}")
        print(f"\nBy publisher:")
        for pub, count in sorted(output_data['by_publisher'].items()):
            print(f"  {pub}: {count}")
        print(f"\nBy topic:")
        for topic, count in sorted(output_data['by_topic'].items()):
            print(f"  {topic}: {count}")
        print(f"\nSaved to: {output_file}")
        print("="*80)

        return output_data


def main():
    """Main execution."""
    finder = NetherlandsSemiconductorFinder()
    results = finder.run_all()

    print(f"\n[OK] Found {results['total_found']} reports ready for download")
    print(f"[OK] Use eu_mcf_report_downloader.py to download and hash")


if __name__ == "__main__":
    main()
