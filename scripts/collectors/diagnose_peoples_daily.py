#!/usr/bin/env python3
"""
Diagnostic: Why is People's Daily finding 0 article links?
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

# Fetch People's Daily homepage from Wayback
archive_url = "https://web.archive.org/web/20250103165346/http://paper.people.com.cn/"
response = requests.get(archive_url, timeout=60)
soup = BeautifulSoup(response.content, 'lxml')

# Remove scripts, styles
for tag in soup(['script', 'style', 'iframe']):
    tag.decompose()

# Find all links
links = soup.find_all('a', href=True)
print(f"Total links found: {len(links)}\n")

# Sample first 50 links AND check for article patterns
wayback_pattern = r'https?://web\.archive\.org/web/\d{14}/(.*)'
article_patterns = [
    '/article/', '/articles/', '/research/', '/report/',
    '/analysis/', '/commentary/', '/publication/',
    '/view/', '/detail/', '/content/', '/show/',
    '/info/', '/news/', '/insights/',
    '/xwdt/', '/yjcg/', '/gjwtyj/', '/sspl/', '/zzybg/', '/xslw/'
]

print("First 50 href values (WITH pattern matching):")
print("=" * 120)

for i, link in enumerate(links[:50]):
    href = link.get('href')
    link_text = link.get_text(strip=True)[:50]

    # Extract original URL if Wayback-rewritten
    wayback_match = re.match(wayback_pattern, href)
    if wayback_match:
        original_href = wayback_match.group(1)
    else:
        original_href = href

    # Check patterns
    has_date_pattern = bool(re.search(r'/20\d{2}', original_href))
    has_html = '.html' in original_href.lower()
    has_article_pattern = any(pattern in original_href.lower() for pattern in article_patterns)

    match_status = []
    if has_date_pattern:
        match_status.append("DATE")
    if has_html:
        match_status.append("HTML")
    if has_article_pattern:
        match_status.append("ARTICLE_PATTERN")

    match_str = f"[{', '.join(match_status)}]" if match_status else "[NO MATCH]"

    print(f"{i+1}. {match_str}")
    print(f"   Original: {original_href[:100]}")
    print(f"   Text: {link_text}")
    print()
