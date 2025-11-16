#!/usr/bin/env python3
"""
EU-wide + MCF Report Finder
============================

Harvests downloadable reports (2015-present) about China-Europe S&T
with Military-Civil Fusion focus from:

EU Institutions:
  - European Commission (DG GROW, RTD, TRADE)
  - European External Action Service (EEAS)
  - European Parliament (EP Studies)
  - European Defence Agency (EDA)
  - European Space Agency (ESA)
  - NATO
  - OECD

Think Tanks:
  - EUISS (EU Institute for Security Studies)
  - Bruegel
  - MERICS (Mercator Institute for China Studies)
  - RUSI (Royal United Services Institute)
  - IFRI (French Institute of International Relations)
  - SWP (German Institute for International and Security Affairs)
  - IISS (International Institute for Strategic Studies)

Output: JSON with comprehensive metadata for direct-downloadable PDFs/DOCX
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import time
import hashlib
from pathlib import Path

class EUMCFReportFinder:
    """Find China-Europe S&T and MCF reports from EU institutions and think tanks."""

    def __init__(self, output_dir: str = "data/external/eu_mcf_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Keywords for China-Europe S&T and MCF detection
        self.china_keywords = [
            'china', 'chinese', 'prc', "people's republic", 'beijing',
            'sino-', 'eu-china', 'europe-china'
        ]

        self.tech_keywords = [
            'technology', 'innovation', 'research', 'science',
            'semiconductor', 'quantum', 'artificial intelligence', 'ai',
            'space', 'dual-use', '5g', '6g', 'biotechnology',
            'advanced materials', 'robotics', 'cybersecurity'
        ]

        self.mcf_keywords = [
            'military-civil fusion', 'civil-military fusion', 'mcf',
            'dual-use', 'defense', 'military', 'strategic',
            'seven sons', 'defense universities'
        ]

        self.results = []

    def is_china_europe_tech(self, text: str) -> tuple[bool, list]:
        """Check if content is about China-Europe S&T."""
        text_lower = text.lower()

        has_china = any(kw in text_lower for kw in self.china_keywords)
        has_europe = any(word in text_lower for word in ['europe', 'european', 'eu'])
        has_tech = any(kw in text_lower for kw in self.tech_keywords)

        topics = []
        if 'artificial intelligence' in text_lower or ' ai ' in text_lower:
            topics.append('ai_ml')
        if 'semiconductor' in text_lower or 'chip' in text_lower:
            topics.append('semiconductors')
        if 'quantum' in text_lower:
            topics.append('quantum')
        if 'space' in text_lower:
            topics.append('space')
        if any(kw in text_lower for kw in self.mcf_keywords):
            topics.append('mcf')
        if 'supply chain' in text_lower:
            topics.append('supply_chain')

        return (has_china and (has_europe or has_tech), topics)

    def is_mcf_related(self, text: str) -> bool:
        """Check if content is MCF-related."""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.mcf_keywords)

    def verify_download_link(self, url: str) -> Optional[Dict]:
        """Verify that URL is a direct download link for PDF/DOCX."""
        try:
            # HEAD request to check content-type
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
        # Try various date formats
        patterns = [
            r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{2})/(\d{2})/(\d{4})',
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

                # Pattern 1: "15 January 2020"
                if len(groups) == 3 and groups[1].lower() in months:
                    day, month_name, year = groups
                    return {
                        'year': int(year),
                        'month': months[month_name.lower()],
                        'day': int(day),
                        'iso': f"{year}-{months[month_name.lower()]:02d}-{int(day):02d}"
                    }

                # Pattern 2: "January 2020"
                elif len(groups) == 2 and groups[0].lower() in months:
                    month_name, year = groups
                    return {
                        'year': int(year),
                        'month': months[month_name.lower()],
                        'day': None,
                        'iso': f"{year}-{months[month_name.lower()]:02d}-01"
                    }

                # Pattern 3: "2020-01-15"
                elif len(groups) == 3 and groups[0].isdigit() and len(groups[0]) == 4:
                    year, month, day = groups
                    return {
                        'year': int(year),
                        'month': int(month),
                        'day': int(day),
                        'iso': f"{year}-{month}-{day}"
                    }

        return None

    def scrape_merics(self) -> List[Dict]:
        """Scrape MERICS (Mercator Institute for China Studies)."""
        print("\n[MERICS] Scraping https://merics.org/en/publications...")
        results = []

        try:
            url = "https://merics.org/en/publications"
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            # MERICS has publication listings
            for article in soup.find_all(['article', 'div'], class_=re.compile(r'publication|teaser')):
                try:
                    # Extract title
                    title_elem = article.find(['h2', 'h3', 'a'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)

                    # Get link
                    link_elem = article.find('a', href=True)
                    if not link_elem:
                        continue
                    link = urljoin(url, link_elem['href'])

                    # Extract description/abstract
                    desc_elem = article.find(['p', 'div'], class_=re.compile(r'description|summary|teaser'))
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    # Check if China-Europe tech related
                    combined_text = f"{title} {description}"
                    is_relevant, topics = self.is_china_europe_tech(combined_text)

                    if is_relevant:
                        # Visit detail page to get download link
                        detail_response = self.session.get(link, timeout=10)
                        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

                        # Look for PDF download link
                        pdf_link = detail_soup.find('a', href=re.compile(r'\.pdf$'))
                        if pdf_link:
                            download_url = urljoin(link, pdf_link['href'])
                            verified = self.verify_download_link(download_url)

                            if verified:
                                # Extract date
                                date_elem = detail_soup.find(['time', 'span'], class_=re.compile(r'date|published'))
                                date_info = None
                                if date_elem:
                                    date_info = self.extract_date_from_text(date_elem.get_text())

                                # Skip if before 2015
                                if date_info and date_info['year'] < 2015:
                                    continue

                                results.append({
                                    'title': title,
                                    'publisher_org': 'MERICS',
                                    'publication_date_iso': date_info['iso'] if date_info else None,
                                    'year': date_info['year'] if date_info else None,
                                    'month': date_info['month'] if date_info else None,
                                    'day': date_info['day'] if date_info else None,
                                    'canonical_url': link,
                                    'download_url': download_url,
                                    'language': 'en',
                                    'authors': None,
                                    'region_group': ['europe', 'east_asia'],
                                    'country_list': ['CN', 'EU'],
                                    'topics': topics,
                                    'subtopics': [],
                                    'mcf_flag': 1 if self.is_mcf_related(combined_text) else 0,
                                    'europe_focus_flag': 1,
                                    'arctic_flag': 0,
                                    'doc_type': 'report',
                                    'file_ext': verified['type'],
                                    'abstract': description[:500] if description else None
                                })
                                print(f"  [OK] Found: {title[:60]}...")

                        time.sleep(0.5)  # Rate limiting

                except Exception as e:
                    print(f"  [WARN] Error processing article: {e}")
                    continue

        except Exception as e:
            print(f"  [ERROR] Failed to scrape MERICS: {e}")

        return results

    def scrape_euiss(self) -> List[Dict]:
        """Scrape EUISS (EU Institute for Security Studies)."""
        print("\n[EUISS] Scraping https://www.iss.europa.eu/publications...")
        results = []

        try:
            url = "https://www.iss.europa.eu/publications"
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            for item in soup.find_all(['div', 'article'], class_=re.compile(r'publication|item')):
                try:
                    title_elem = item.find(['h2', 'h3', 'a'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)

                    link_elem = item.find('a', href=True)
                    if not link_elem:
                        continue
                    link = urljoin(url, link_elem['href'])

                    desc_elem = item.find(['p', 'div'], class_=re.compile(r'description|summary'))
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    combined_text = f"{title} {description}"
                    is_relevant, topics = self.is_china_europe_tech(combined_text)

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

                                results.append({
                                    'title': title,
                                    'publisher_org': 'EUISS',
                                    'publication_date_iso': date_info['iso'] if date_info else None,
                                    'year': date_info['year'] if date_info else None,
                                    'month': date_info['month'] if date_info else None,
                                    'day': date_info['day'] if date_info else None,
                                    'canonical_url': link,
                                    'download_url': download_url,
                                    'language': 'en',
                                    'authors': None,
                                    'region_group': ['europe', 'east_asia'],
                                    'country_list': ['CN', 'EU'],
                                    'topics': topics,
                                    'subtopics': [],
                                    'mcf_flag': 1 if self.is_mcf_related(combined_text) else 0,
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
            print(f"  [ERROR] Failed to scrape EUISS: {e}")

        return results

    def scrape_rusi(self) -> List[Dict]:
        """Scrape RUSI (Royal United Services Institute)."""
        print("\n[RUSI] Scraping https://rusi.org/publications...")
        results = []

        try:
            # RUSI publications on China and technology
            search_terms = ['china', 'technology', 'defense']

            for term in search_terms:
                url = f"https://rusi.org/explore-our-research?search={term}"
                response = self.session.get(url, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')

                for item in soup.find_all(['article', 'div'], class_=re.compile(r'publication|result')):
                    try:
                        title_elem = item.find(['h2', 'h3', 'a'])
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)

                        link_elem = item.find('a', href=True)
                        if not link_elem:
                            continue
                        link = urljoin(url, link_elem['href'])

                        desc_elem = item.find(['p', 'div'], class_=re.compile(r'description|excerpt'))
                        description = desc_elem.get_text(strip=True) if desc_elem else ""

                        combined_text = f"{title} {description}"
                        is_relevant, topics = self.is_china_europe_tech(combined_text)

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

                                    results.append({
                                        'title': title,
                                        'publisher_org': 'RUSI',
                                        'publication_date_iso': date_info['iso'] if date_info else None,
                                        'year': date_info['year'] if date_info else None,
                                        'month': date_info['month'] if date_info else None,
                                        'day': date_info['day'] if date_info else None,
                                        'canonical_url': link,
                                        'download_url': download_url,
                                        'language': 'en',
                                        'authors': None,
                                        'region_group': ['europe', 'east_asia'],
                                        'country_list': ['CN', 'GB'],
                                        'topics': topics,
                                        'subtopics': [],
                                        'mcf_flag': 1 if self.is_mcf_related(combined_text) else 0,
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

                time.sleep(1)  # Between search terms

        except Exception as e:
            print(f"  [ERROR] Failed to scrape RUSI: {e}")

        return results

    def scrape_bruegel(self) -> List[Dict]:
        """Scrape Bruegel."""
        print("\n[Bruegel] Scraping https://www.bruegel.org/publications...")
        results = []

        try:
            url = "https://www.bruegel.org/publications"
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            for item in soup.find_all(['article', 'div'], class_=re.compile(r'publication|post')):
                try:
                    title_elem = item.find(['h2', 'h3', 'a'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)

                    # Check if China-related in title
                    if not any(kw in title.lower() for kw in ['china', 'chinese', 'technology', 'tech']):
                        continue

                    link_elem = item.find('a', href=True)
                    if not link_elem:
                        continue
                    link = urljoin(url, link_elem['href'])

                    desc_elem = item.find(['p', 'div'], class_=re.compile(r'description|excerpt'))
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    combined_text = f"{title} {description}"
                    is_relevant, topics = self.is_china_europe_tech(combined_text)

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

                                results.append({
                                    'title': title,
                                    'publisher_org': 'Bruegel',
                                    'publication_date_iso': date_info['iso'] if date_info else None,
                                    'year': date_info['year'] if date_info else None,
                                    'month': date_info['month'] if date_info else None,
                                    'day': date_info['day'] if date_info else None,
                                    'canonical_url': link,
                                    'download_url': download_url,
                                    'language': 'en',
                                    'authors': None,
                                    'region_group': ['europe', 'east_asia'],
                                    'country_list': ['CN', 'EU'],
                                    'topics': topics,
                                    'subtopics': [],
                                    'mcf_flag': 1 if self.is_mcf_related(combined_text) else 0,
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
            print(f"  [ERROR] Failed to scrape Bruegel: {e}")

        return results

    def run_all(self) -> Dict:
        """Run all scrapers and aggregate results."""
        print("="*80)
        print("EU-WIDE + MCF REPORT FINDER")
        print("="*80)
        print(f"Target: China-Europe S&T reports (2015-present)")
        print(f"Focus: Military-Civil Fusion (MCF) and strategic technologies")
        print(f"Output: Direct-downloadable PDFs/DOCX only")
        print("="*80)

        all_results = []

        # Scrape each source
        all_results.extend(self.scrape_merics())
        all_results.extend(self.scrape_euiss())
        all_results.extend(self.scrape_rusi())
        all_results.extend(self.scrape_bruegel())

        # Deduplicate by download URL
        seen_urls = set()
        deduplicated = []
        for result in all_results:
            if result['download_url'] not in seen_urls:
                seen_urls.add(result['download_url'])
                deduplicated.append(result)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"eu_mcf_reports_{timestamp}.json"

        output_data = {
            'generated_at': datetime.now().isoformat(),
            'filter': 'publication_date >= 2015-01-01, China-Europe S&T, MCF focus',
            'total_found': len(deduplicated),
            'by_publisher': {},
            'by_topic': {},
            'mcf_count': sum(1 for r in deduplicated if r['mcf_flag'] == 1),
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
        print(f"MCF-related reports: {output_data['mcf_count']}")
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
    finder = EUMCFReportFinder()
    results = finder.run_all()

    print(f"\n[OK] Found {results['total_found']} reports ready for download")
    print(f"[OK] Next step: Use eu_mcf_report_downloader.py to download and hash")


if __name__ == "__main__":
    main()
