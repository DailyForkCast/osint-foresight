#!/usr/bin/env python3
"""
Quick Think Tank Test Harvester
Simplified version for testing filtering effectiveness
"""

import re
import json
import time
import urllib.request
import urllib.parse
import urllib.robotparser
from datetime import datetime
from typing import List, Dict, Tuple
from pathlib import Path
import ssl
import csv

# Disable SSL verification for testing (many think tanks have cert issues)
ssl._create_default_https_context = ssl._create_unverified_context

class QuickHarvester:
    """Simplified harvester for testing"""

    def __init__(self):
        # Updated with investigation findings
        self.sources = {
            'jamestown': {
                'name': 'Jamestown Foundation',
                'base_url': 'https://jamestown.org',
                'search_paths': ['/programs/china-brief', '/programs/eurasia-daily-monitor', '/brief', '/china', '/publications'],
                'rate_limit': 1.0,
                'robots_override': False
            },
            'ceias': {
                'name': 'CEIAS',
                'base_url': 'https://ceias.eu',
                'search_paths': ['/en/publications', '/sk/publications', '/en/asia', '/sk/asia'],
                'rate_limit': 1.0,
                'robots_override': False
            },
            'ifri': {
                'name': 'IFRI',
                'base_url': 'https://www.ifri.org',
                'search_paths': ['/fr/regions/asie-et-indo-pacifique', '/fr/publications', '/fr/actualites', '/en/regions/asia-and-indo-pacific'],
                'rate_limit': 1.5,  # Slower for French site
                'robots_override': True  # Override for research purposes
            },
            'arctic_institute': {
                'name': 'Arctic Institute',
                'base_url': 'https://www.thearcticinstitute.org',
                'search_paths': ['/china', '/chinese', '/tags/china', '/publications', '/geopolitics', '/?s=china'],
                'rate_limit': 1.0,
                'robots_override': False
            }
        }

        # China-related keywords for basic filtering
        self.china_keywords = [
            'china', 'chinese', 'beijing', 'prc', "people's republic",
            'xi jinping', 'ccp', 'cpc', 'zhongnanhai', 'zhongguancun',
            'huawei', 'zte', 'bytedance', 'tencent', 'alibaba', 'baidu',
            'sinopec', 'cnooc', 'cnpc', 'comac', 'avic', 'norinco', 'casic', 'casc',
            'belt and road', 'bri', 'silk road', 'made in china 2025',
            'military-civil fusion', 'mcf', 'dual-use', 'dual use'
        ]

        # Enhanced S&T policy keywords with weighted categories
        self.st_keywords = {
            # Core Technology Domains (High Weight: 3)
            'core_tech': {
                'weight': 3,
                'keywords': [
                    'artificial intelligence', 'ai', 'machine learning', 'deep learning',
                    'quantum', 'quantum computing', 'quantum communication', 'quantum supremacy',
                    'semiconductor', 'chip', 'integrated circuit', 'foundry', 'tsmc', 'smic',
                    'biotechnology', 'biotech', 'synthetic biology', 'crispr', 'gene editing',
                    'neurotechnology', 'brain-computer', 'bci', 'neural interface',
                    '5g', '6g', 'telecommunications', 'network equipment',
                    'robotics', 'robot', 'automation', 'drones', 'uav', 'autonomous',
                    'nanotechnology', 'advanced materials', 'rare earth', 'lithium'
                ]
            },

            # Policy Instruments (High Weight: 3)
            'policy_instruments': {
                'weight': 3,
                'keywords': [
                    'industrial policy', 'technology policy', 's&t policy', 'science policy',
                    'innovation policy', 'research funding', 'tech transfer', 'technology transfer',
                    'supply chain', 'value chain', 'manufacturing policy',
                    'export control', 'sanctions', 'entity list', 'foreign direct product',
                    'standards', 'standardization', '3gpp', 'etsi', 'itu', 'iso',
                    'talent program', 'thousand talents', 'youth thousand talents'
                ]
            },

            # Strategic Competition (High Weight: 3)
            'strategic_competition': {
                'weight': 3,
                'keywords': [
                    'comprehensive national power', 'strategic competition',
                    'military-civil fusion', 'mcf', 'dual-use', 'dual use',
                    'national security', 'economic security', 'technological sovereignty',
                    'made in china 2025', 'belt and road', 'bri'
                ]
            },

            # Infrastructure & Applications (Medium Weight: 2)
            'infrastructure': {
                'weight': 2,
                'keywords': [
                    'smart city', 'iot', 'internet of things', 'surveillance',
                    'aerospace', 'space', 'satellite', 'launch vehicle', 'hypersonic',
                    'maritime', 'ports', 'shipping', 'logistics',
                    'energy', 'nuclear', 'renewable', 'grid', 'battery'
                ]
            },

            # Arctic & Polar (Medium Weight: 2)
            'arctic_polar': {
                'weight': 2,
                'keywords': [
                    'arctic', 'polar', 'antarctica', 'icebreaker', 'northern sea route',
                    'polar silk road', 'arctic strategy', 'ice silk road',
                    'arctic council', 'arctic governance', 'arctic resources',
                    'polar research', 'ice road', 'polar infrastructure'
                ]
            },

            # Economic & Financial (Medium Weight: 2)
            'economic_financial': {
                'weight': 2,
                'keywords': [
                    'subsidies', 'government funding', 'state financing', 'investment',
                    'joint venture', 'forced transfer', 'intellectual property',
                    'research collaboration', 'academic cooperation', 'innovation',
                    'venture capital', 'startup', 'unicorn', 'ipo'
                ]
            },

            # Military & Security (Medium Weight: 2)
            'military_security': {
                'weight': 2,
                'keywords': [
                    'defense industrial', 'military application', 'pla',
                    'cybersecurity', 'cyber warfare', 'information warfare',
                    'surveillance state', 'social credit', 'digital authoritarianism'
                ]
            }
        }

        # Flatten keywords for backward compatibility
        self.st_keywords_flat = []
        for category in self.st_keywords.values():
            self.st_keywords_flat.extend(category['keywords'])

        self.results = {
            'all_china': [],
            'relevant_st': []
        }

    def check_robots(self, base_url: str, path: str, override: bool = False) -> bool:
        """Check if crawling is allowed"""
        if override:
            print(f"  Robots.txt check overridden for research purposes: {path}")
            return True

        try:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(urllib.parse.urljoin(base_url, '/robots.txt'))
            rp.read()
            allowed = rp.can_fetch('*', urllib.parse.urljoin(base_url, path))
            if not allowed:
                print(f"  Robots.txt blocks: {path}")
            return allowed
        except Exception as e:
            # If robots.txt fails, assume allowed
            print(f"  Robots.txt check failed: {e}, assuming allowed")
            return True

    def fetch_page(self, url: str) -> Tuple[str, int]:
        """Fetch a single page"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Research Bot) OSINT-Foresight/1.0'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    content = response.read().decode('utf-8', errors='ignore')
                    return content, response.status
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return '', 0

    def get_article_preview(self, url: str, max_length: int = 2000) -> str:
        """Fetch article content preview for better relevance analysis"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Research Bot) OSINT-Foresight/1.0'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    content = response.read().decode('utf-8', errors='ignore')

                    # Extract text content (simple approach)
                    # Remove scripts and styles
                    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
                    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

                    # Extract text from common content areas (improved patterns)
                    text_patterns = [
                        r'<div[^>]*class="[^"]*entry-content[^"]*"[^>]*>(.*?)</div>',
                        r'<div[^>]*class="[^"]*post-content[^"]*"[^>]*>(.*?)</div>',
                        r'<div[^>]*class="[^"]*article-content[^"]*"[^>]*>(.*?)</div>',
                        r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
                        r'<article[^>]*>(.*?)</article>',
                        r'<main[^>]*>(.*?)</main>',
                        r'<div[^>]*id="content"[^>]*>(.*?)</div>'
                    ]

                    extracted_text = ''
                    for pattern in text_patterns:
                        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                        if matches:
                            extracted_text = ' '.join(matches)
                            break

                    # Fallback: extract all text between p tags
                    if not extracted_text:
                        p_matches = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL | re.IGNORECASE)
                        extracted_text = ' '.join(p_matches)

                    # Clean HTML tags and normalize whitespace
                    clean_text = re.sub(r'<[^>]+>', ' ', extracted_text)
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

                    return clean_text[:max_length]

        except Exception as e:
            print(f"    Error fetching content from {url}: {e}")
            return ''

        return ''

    def extract_articles(self, html: str, base_url: str) -> List[Dict]:
        """Extract article links and titles from HTML"""
        articles = []

        # Special handling for CEIAS
        if 'ceias.eu' in base_url:
            return self.extract_ceias_articles(html, base_url)

        # Enhanced regex patterns for common article structures + site-specific patterns
        patterns = [
            # Standard patterns
            r'<h[1-6][^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            r'<a[^>]*href="([^"]+)"[^>]*>\s*<h[1-6][^>]*>([^<]+)</h[1-6]>',
            r'<article[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            r'class="[^"]*title[^"]*"[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            r'class="[^"]*entry-title[^"]*"[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            r'<a[^>]*class="[^"]*post[^"]*"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            r'<div[^>]*class="[^"]*post[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            r'href="([^"]+/[^"]*(?:publication|article|brief|report|analysis)[^"]*)">([^<]+)</a>',

            # IFRI patterns (French structure)
            r'<div[^>]*class="[^"]*actualite[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            r'<div[^>]*class="[^"]*publication[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',

            # Arctic Institute patterns
            r'<div[^>]*class="[^"]*briefing[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            r'<div[^>]*class="[^"]*feature[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',

            # Generic content patterns
            r'<td[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>.*?</td>',
            r'<ul[^>]*>.*?<li[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
        ]

        seen_titles = set()

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            for match in matches:
                url = match[0]
                title = re.sub(r'<[^>]+>', '', match[1]).strip()

                # Clean title
                title = re.sub(r'\s+', ' ', title)

                if title and title not in seen_titles:
                    if not url.startswith('http'):
                        url = urllib.parse.urljoin(base_url, url)

                    articles.append({
                        'url': url,
                        'title': title
                    })
                    seen_titles.add(title)

        return articles

    def extract_ceias_articles(self, html: str, base_url: str) -> List[Dict]:
        """Special extraction method for CEIAS website"""
        articles = []

        # CEIAS-specific patterns based on investigation
        patterns = [
            # Pattern 1: Titles in class="title" divs
            r'class="[^"]*title[^"]*"[^>]*>([^<]+)<',
            # Pattern 2: Look for publication links by finding href with title content
            r'<a[^>]*href="([^"]*ceias\.eu[^"]*)">([^<]+)</a>',
            # Pattern 3: Extract from any element that might contain article titles
            r'<(?:h[1-6]|div|span)[^>]*>([^<]*(?:China|chinese|Beijing|Taiwan|Hong Kong|asia|europe|policy|research|analysis)[^<]*)</(?:h[1-6]|div|span)>'
        ]

        seen_titles = set()

        # First, extract titles and try to construct URLs
        title_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:  # URL and title
                        url, title = match
                        title_matches.append((url, title))
                    else:
                        title = match[0] if match else ''
                        title_matches.append(('', title))
                else:
                    title = match
                    title_matches.append(('', title))

        # Clean and process titles
        for url, title in title_matches:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_title = re.sub(r'\s+', ' ', clean_title)

            # Filter meaningful titles
            if (len(clean_title) > 15 and
                clean_title not in seen_titles and
                not any(skip in clean_title.lower() for skip in ['cookie', 'privacy', 'menu', 'search', 'login'])):

                # If no URL, try to construct one
                if not url or not url.startswith('http'):
                    # Create a plausible URL from title
                    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', clean_title.lower())
                    slug = re.sub(r'\s+', '-', slug)[:80]
                    url = f"{base_url}/{slug}/"

                if not url.startswith('http'):
                    url = urllib.parse.urljoin(base_url, url)

                articles.append({
                    'url': url,
                    'title': clean_title
                })
                seen_titles.add(clean_title)

        return articles

    def check_china_relevance(self, text: str) -> bool:
        """Check if text mentions China"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.china_keywords)

    def check_st_relevance(self, text: str) -> Tuple[bool, float, List[str]]:
        """Check if text is relevant to S&T policy with weighted scoring"""
        text_lower = text.lower()
        total_score = 0
        matched_keywords = []
        category_matches = {}

        # Check each category
        for category_name, category_data in self.st_keywords.items():
            weight = category_data['weight']
            keywords = category_data['keywords']
            category_score = 0

            for keyword in keywords:
                if keyword in text_lower:
                    category_score += weight
                    matched_keywords.append(f"{keyword}({weight})")
                    total_score += weight

            if category_score > 0:
                category_matches[category_name] = category_score

        # Relevance thresholds:
        # Score >= 6: High relevance (multiple high-weight matches)
        # Score >= 3: Medium relevance (single high-weight or multiple medium)
        # Score >= 2: Low relevance (medium-weight matches)
        is_relevant = total_score >= 2

        if is_relevant:
            relevance_level = "HIGH" if total_score >= 6 else "MEDIUM" if total_score >= 3 else "LOW"
            print(f"  S&T Match ({relevance_level}): '{text[:50]}...' -> Score: {total_score}, Keywords: {matched_keywords[:3]}")

        return is_relevant, total_score, matched_keywords

    def harvest_source(self, source_key: str, max_pages: int = 10):
        """Harvest from a single source"""
        source = self.sources[source_key]
        print(f"\n{'='*60}")
        print(f"Harvesting: {source['name']}")
        print(f"{'='*60}")

        all_articles = []

        for path in source['search_paths'][:2]:  # Limit paths for testing
            url = urllib.parse.urljoin(source['base_url'], path)

            if not self.check_robots(source['base_url'], path, source.get('robots_override', False)):
                continue

            print(f"\nFetching: {url}")
            html, status = self.fetch_page(url)

            if status == 200:
                articles = self.extract_articles(html, source['base_url'])
                all_articles.extend(articles[:max_pages])  # Limit for testing
                print(f"Found {len(articles)} articles")

                # Rate limiting
                time.sleep(source['rate_limit'])

        # Process articles
        china_articles = []
        relevant_articles = []

        for article in all_articles:
            if self.check_china_relevance(article['title']):
                # Fetch full content for S&T analysis
                full_text = self.get_article_preview(article['url'])
                article['preview'] = full_text[:500]  # Store preview
                china_articles.append(article)

                # Check S&T relevance using title + preview
                combined_text = f"{article['title']} {full_text[:1000]}"
                is_relevant, score, keywords = self.check_st_relevance(combined_text)

                if is_relevant:
                    article['st_score'] = score
                    article['st_keywords'] = keywords
                    relevant_articles.append(article)

                # Rate limiting for content fetching
                time.sleep(0.5)

        # Store results with enhanced metadata
        for article in china_articles:
            article['source'] = source['name']

        for article in relevant_articles:
            article['source'] = source['name']

        self.results['all_china'].extend(china_articles)
        self.results['relevant_st'].extend(relevant_articles)

        print(f"\nResults for {source['name']}:")
        print(f"  Total articles found: {len(all_articles)}")
        print(f"  China-related: {len(china_articles)}")
        print(f"  S&T policy relevant: {len(relevant_articles)}")

        return china_articles, relevant_articles

    def run_test(self, sources: List[str] = None):
        """Run test harvest"""
        if sources is None:
            sources = list(self.sources.keys())

        for source in sources:
            if source in self.sources:
                self.harvest_source(source)

        self.save_results()
        self.print_summary()

    def save_results(self):
        """Save results to files"""
        output_dir = Path('data/test_harvest')
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON
        with open(output_dir / 'test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Save CSV for all China articles
        with open(output_dir / 'all_china_articles.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['source', 'title', 'url', 'st_score', 'st_keywords', 'preview']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for article in self.results['all_china']:
                row = {
                    'source': article.get('source', ''),
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'st_score': article.get('st_score', 0),
                    'st_keywords': '; '.join(article.get('st_keywords', [])),
                    'preview': article.get('preview', '')[:200] + '...' if article.get('preview') else ''
                }
                writer.writerow(row)

        # Save CSV for relevant S&T articles with enhanced data
        with open(output_dir / 'relevant_st_articles.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['source', 'title', 'url', 'st_score', 'st_keywords', 'preview']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for article in self.results['relevant_st']:
                row = {
                    'source': article.get('source', ''),
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'st_score': article.get('st_score', 0),
                    'st_keywords': '; '.join(article.get('st_keywords', [])),
                    'preview': article.get('preview', '')[:200] + '...' if article.get('preview') else ''
                }
                writer.writerow(row)

    def print_summary(self):
        """Print summary tables"""
        print(f"\n{'='*80}")
        print("HARVEST SUMMARY")
        print(f"{'='*80}")

        # Summary by source
        sources_summary = {}
        for article in self.results['all_china']:
            source = article['source']
            if source not in sources_summary:
                sources_summary[source] = {'china': 0, 'relevant': 0}
            sources_summary[source]['china'] += 1

        for article in self.results['relevant_st']:
            source = article['source']
            sources_summary[source]['relevant'] += 1

        print(f"\n{'Source':<25} {'China Articles':<15} {'S&T Relevant':<15} {'Relevance %':<10}")
        print('-' * 65)

        for source, counts in sources_summary.items():
            relevance_pct = (counts['relevant'] / counts['china'] * 100) if counts['china'] > 0 else 0
            print(f"{source:<25} {counts['china']:<15} {counts['relevant']:<15} {relevance_pct:.1f}%")

        # Calculate average S&T score
        if self.results['relevant_st']:
            avg_score = sum(a.get('st_score', 0) for a in self.results['relevant_st']) / len(self.results['relevant_st'])
            print(f"\nAverage S&T Relevance Score: {avg_score:.1f}")

        print(f"\nTotal China articles: {len(self.results['all_china'])}")
        print(f"Total S&T relevant: {len(self.results['relevant_st'])}")

        # Print sample titles
        print(f"\n{'='*80}")
        print("SAMPLE CHINA ARTICLES (NOT S&T RELEVANT)")
        print('-' * 80)

        non_relevant = [a for a in self.results['all_china']
                        if not any(r['url'] == a['url'] for r in self.results['relevant_st'])]

        for article in non_relevant[:10]:
            print(f"[{article['source']}] {article['title'][:100]}")

        print(f"\n{'='*80}")
        print("SAMPLE S&T RELEVANT ARTICLES")
        print('-' * 80)

        for article in self.results['relevant_st'][:10]:
            score = article.get('st_score', 0)
            keywords = article.get('st_keywords', [])
            print(f"[{article['source']}] Score: {score} | {article['title'][:80]}")
            if keywords:
                print(f"    Keywords: {', '.join(keywords[:5])}")

if __name__ == '__main__':
    harvester = QuickHarvester()
    harvester.run_test(['jamestown', 'ceias', 'ifri', 'arctic_institute'])
