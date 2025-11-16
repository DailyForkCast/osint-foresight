#!/usr/bin/env python3
"""
Quick diagnostic: What links are actually on Qiushi homepage?
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Fetch Qiushi homepage from Wayback
archive_url = "https://web.archive.org/web/20250102125229/http://qstheory.cn/"
response = requests.get(archive_url, timeout=60)
soup = BeautifulSoup(response.content, 'lxml')

# Remove scripts, styles
for tag in soup(['script', 'style', 'iframe']):
    tag.decompose()

# Find all links
links = soup.find_all('a', href=True)
print(f"Total links found: {len(links)}\n")

# Sample first 50 links
print("First 50 href values:")
print("=" * 80)
for i, link in enumerate(links[:50]):
    href = link.get('href')
    link_text = link.get_text(strip=True)[:50]
    print(f"{i+1}. href='{href}'")
    print(f"   text: {link_text}")
    print()
