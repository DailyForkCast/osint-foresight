#!/usr/bin/env python3
"""
Common Crawl Intelligence Extraction
Finds hidden supplier relationships, technology adoption, and partnerships
Documentation: https://commoncrawl.org/the-data/get-started/
"""

import argparse
import json
import gzip
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
import requests
from io import BytesIO
import pandas as pd
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import warc

class CommonCrawlIntelligence:
    """Extract supply chain and technology signals from Common Crawl"""

    # Common Crawl index URL
    INDEX_URL = "https://index.commoncrawl.org/CC-MAIN-{crawl}/index"
    S3_BASE = "https://data.commoncrawl.org/"

    # Latest crawls (update monthly)
    CRAWLS = [
        "2024-10",  # March 2024
        "2024-05",  # January 2024
        "2023-50",  # December 2023
    ]

    # Country domain mappings
    COUNTRY_DOMAINS = {
        'AT': '.at',
        'DE': '.de',
        'FR': '.fr',
        'IT': '.it',
        'ES': '.es',
        'PT': '.pt',
        'IE': '.ie',
        'SK': '.sk',
        'CZ': '.cz',
        'PL': '.pl',
        'HU': '.hu',
        'RO': '.ro',
        'BG': '.bg',
        'GR': '.gr',
        'BE': '.be',
        'NL': '.nl',
        'LU': '.lu',
        'DK': '.dk',
        'SE': '.se',
        'FI': '.fi',
        'NO': '.no',
        'CH': '.ch',
        'GB': ['.uk', '.co.uk'],
    }

    # Supply chain relationship patterns
    SUPPLIER_PATTERNS = [
        # Direct supplier mentions
        r"(?:our|key|main|primary|strategic|trusted|certified|qualified)\s+(?:supplier|vendor|partner)s?\s+(?:include|are|is)\s+([A-Z][A-Za-z\s&,]+(?:Ltd|Inc|GmbH|AG|SA|SRL|BV|AB|AS|OY))",
        r"(?:supplied|provided|sourced)\s+(?:by|from)\s+([A-Z][A-Za-z\s&,]+(?:Ltd|Inc|GmbH|AG|SA|SRL|BV|AB|AS|OY))",
        r"(?:we|We)\s+(?:partner|work|collaborate)\s+with\s+([A-Z][A-Za-z\s&,]+(?:Ltd|Inc|GmbH|AG|SA|SRL|BV|AB|AS|OY))",

        # Customer relationships (reverse supply chain)
        r"(?:our|key|major)\s+(?:customer|client)s?\s+(?:include|are)\s+([A-Z][A-Za-z\s&,]+(?:Ltd|Inc|GmbH|AG|SA|SRL|BV|AB|AS|OY))",
        r"(?:we|We)\s+(?:supply|provide|deliver)\s+(?:to|for)\s+([A-Z][A-Za-z\s&,]+(?:Ltd|Inc|GmbH|AG|SA|SRL|BV|AB|AS|OY))",

        # Partnership patterns
        r"(?:joint venture|partnership|collaboration|alliance)\s+with\s+([A-Z][A-Za-z\s&,]+(?:Ltd|Inc|GmbH|AG|SA|SRL|BV|AB|AS|OY))",
        r"(?:strategic|technology|research|development)\s+(?:partner|partnership)\s+with\s+([A-Z][A-Za-z\s&,]+(?:Ltd|Inc|GmbH|AG|SA|SRL|BV|AB|AS|OY))",

        # Supply chain mentions in lists
        r"(?:Suppliers|Vendors|Partners):\s*(?:</?\w+>)*\s*([A-Z][A-Za-z\s&,\-•;]+)",
        r"(?:Key|Main|Strategic)\s+(?:Suppliers|Partners)(?:</?\w+>)*\s*[:•]\s*([A-Z][A-Za-z\s&,\-•;]+)",
    ]

    # Technology adoption patterns
    TECH_PATTERNS = {
        'ai_ml': [
            r"(?:we|We)\s+(?:use|utilize|employ|leverage|implement|deploy)\s+(?:artificial intelligence|AI|machine learning|ML|deep learning|neural network)",
            r"(?:our|Our)\s+(?:AI|ML|artificial intelligence|machine learning)\s+(?:solution|system|platform|technology|model)",
            r"(?:powered by|based on|built with)\s+(?:AI|ML|artificial intelligence|machine learning)",
            r"(?:TensorFlow|PyTorch|scikit-learn|Keras|OpenAI|GPT|BERT|transformer model)",
        ],
        'cloud': [
            r"(?:we|We)\s+(?:use|utilize|deploy|host|run)\s+(?:on|in)\s+(?:AWS|Amazon Web Services|Azure|Google Cloud|GCP|cloud)",
            r"(?:our|Our)\s+(?:infrastructure|platform|services|applications)\s+(?:on|in)\s+(?:the cloud|AWS|Azure|GCP)",
            r"(?:cloud-native|cloud-first|cloud-based|SaaS|PaaS|IaaS)",
            r"(?:Kubernetes|Docker|containerized|microservices|serverless)",
        ],
        'blockchain': [
            r"(?:blockchain|distributed ledger|smart contract|DLT|Web3)",
            r"(?:Ethereum|Hyperledger|Corda|Polygon|Solana)",
            r"(?:NFT|cryptocurrency|crypto|DeFi|tokenization)",
        ],
        'quantum': [
            r"(?:quantum computing|quantum computer|quantum algorithm|quantum simulation)",
            r"(?:quantum-ready|quantum-safe|post-quantum|QKD)",
            r"(?:IBM Quantum|IonQ|Rigetti|D-Wave|quantum annealing)",
        ],
        'iot': [
            r"(?:IoT|Internet of Things|connected device|smart sensor|edge computing)",
            r"(?:industrial IoT|IIoT|Industry 4\.0|smart factory|digital twin)",
            r"(?:MQTT|LoRaWAN|NB-IoT|Zigbee|edge analytics)",
        ],
        'cybersecurity': [
            r"(?:zero trust|SIEM|SOC|threat intelligence|endpoint protection)",
            r"(?:ISO 27001|SOC 2|GDPR compliant|NIST framework)",
            r"(?:penetration testing|vulnerability assessment|security audit)",
        ],
    }

    # Certification and standards patterns
    CERTIFICATION_PATTERNS = [
        r"(?:certified|compliant|conformant)\s+(?:to|with)\s+(ISO\s+\d+|CE|FCC|UL|TÜV|EN\s+\d+)",
        r"(ISO\s+\d+(?::\d+)?)\s+(?:certified|certification|compliant)",
        r"(?:holds?|received?|obtained?)\s+(?:the\s+)?(ISO\s+\d+|CE|FCC|UL)\s+(?:certification|certificate)",
    ]

    def __init__(self, country: str, output_dir: Path):
        """Initialize Common Crawl intelligence extractor"""
        self.country = country.upper()
        self.country_domain = self.COUNTRY_DOMAINS.get(self.country, f'.{country.lower()}')
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def query_index(self, domain: str, crawl: str = "2024-10") -> List[Dict]:
        """Query Common Crawl index for a specific domain"""

        index_url = self.INDEX_URL.format(crawl=crawl)
        params = {
            'url': f'*.{domain}/*',
            'output': 'json',
            'limit': 1000  # Limit results per query
        }

        print(f"  Querying index for {domain} in crawl {crawl}...")

        try:
            response = requests.get(index_url, params=params)
            response.raise_for_status()

            # Parse JSON lines response
            results = []
            for line in response.text.strip().split('\n'):
                if line:
                    results.append(json.loads(line))

            print(f"    Found {len(results)} pages")
            return results

        except requests.exceptions.RequestException as e:
            print(f"    Error querying index: {e}")
            return []

    def download_warc_record(self, record: Dict) -> str:
        """Download a specific WARC record from Common Crawl"""

        # Extract WARC location info
        filename = record['filename']
        offset = int(record['offset'])
        length = int(record['length'])

        # Build S3 URL
        url = self.S3_BASE + filename

        # Use HTTP range request to get specific record
        headers = {'Range': f'bytes={offset}-{offset+length-1}'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Decompress GZIP content
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
                warc_content = gz.read()

            return warc_content.decode('utf-8', errors='ignore')

        except Exception as e:
            print(f"    Error downloading WARC record: {e}")
            return ""

    def extract_page_content(self, warc_content: str) -> Tuple[str, str]:
        """Extract URL and HTML content from WARC record"""

        # Parse WARC headers
        lines = warc_content.split('\n')
        url = ""
        html_start = 0

        for i, line in enumerate(lines):
            if line.startswith('WARC-Target-URI:'):
                url = line.split(':', 1)[1].strip()
            elif line == '' and i > 0:  # Empty line marks end of headers
                html_start = i + 1
                break

        # Extract HTML content
        html_content = '\n'.join(lines[html_start:])

        # Find actual HTML start (after HTTP headers)
        html_marker = html_content.find('<html')
        if html_marker == -1:
            html_marker = html_content.find('<!DOCTYPE')
        if html_marker != -1:
            html_content = html_content[html_marker:]

        return url, html_content

    def extract_supply_chain_signals(self, html: str, url: str) -> Dict:
        """Extract supply chain relationships from HTML"""

        signals = {
            'url': url,
            'suppliers': [],
            'customers': [],
            'partners': [],
            'certifications': [],
            'technologies': {},
        }

        # Parse HTML
        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
        except:
            text = html

        # Extract text from specific sections
        important_sections = []

        # Look for about/partner/supplier pages
        if any(keyword in url.lower() for keyword in ['about', 'partner', 'supplier', 'vendor', 'customer', 'client']):
            important_sections.append(text)

        # Look for specific divs/sections
        for tag in soup.find_all(['div', 'section', 'article']):
            class_str = ' '.join(tag.get('class', []))
            id_str = tag.get('id', '')

            if any(keyword in class_str.lower() + id_str.lower()
                   for keyword in ['partner', 'supplier', 'vendor', 'customer', 'client', 'about']):
                important_sections.append(tag.get_text(separator=' ', strip=True))

        # Combine all text
        full_text = ' '.join(important_sections) if important_sections else text

        # Extract supplier relationships
        for pattern in self.SUPPLIER_PATTERNS:
            matches = re.findall(pattern, full_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Clean up company names
                companies = [c.strip() for c in re.split(r'[,;]', match) if c.strip()]
                for company in companies:
                    if len(company) > 3 and len(company) < 100:  # Basic validation
                        if 'customer' in pattern.lower():
                            signals['customers'].append(company)
                        elif 'partner' in pattern.lower():
                            signals['partners'].append(company)
                        else:
                            signals['suppliers'].append(company)

        # Extract technology adoption
        for tech_category, patterns in self.TECH_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    if tech_category not in signals['technologies']:
                        signals['technologies'][tech_category] = []

                    # Extract context around the match
                    matches = re.finditer(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        start = max(0, match.start() - 50)
                        end = min(len(full_text), match.end() + 50)
                        context = full_text[start:end].strip()
                        signals['technologies'][tech_category].append(context)

        # Extract certifications
        for pattern in self.CERTIFICATION_PATTERNS:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            signals['certifications'].extend(matches)

        # Deduplicate
        signals['suppliers'] = list(set(signals['suppliers']))
        signals['customers'] = list(set(signals['customers']))
        signals['partners'] = list(set(signals['partners']))
        signals['certifications'] = list(set(signals['certifications']))

        return signals

    def analyze_domain(self, domain: str, sample_size: int = 100) -> pd.DataFrame:
        """Analyze a specific domain for supply chain signals"""

        print(f"\nAnalyzing {domain}...")

        all_signals = []

        # Query index for this domain
        index_results = self.query_index(domain)

        # Sample pages to analyze
        for i, record in enumerate(index_results[:sample_size]):
            if i % 10 == 0:
                print(f"  Processing {i}/{min(sample_size, len(index_results))} pages...")

            # Download WARC record
            warc_content = self.download_warc_record(record)

            if warc_content:
                # Extract page content
                url, html = self.extract_page_content(warc_content)

                # Extract signals
                signals = self.extract_supply_chain_signals(html, url)

                # Only keep if we found something
                if (signals['suppliers'] or signals['customers'] or
                    signals['partners'] or signals['technologies'] or signals['certifications']):
                    all_signals.append(signals)

        return all_signals

    def find_tech_companies(self, min_pages: int = 10) -> List[str]:
        """Find technology companies in the country"""

        print(f"\nFinding technology companies in {self.country}...")

        # Query for common tech company patterns
        tech_domains = []

        if isinstance(self.country_domain, list):
            domains = self.country_domain
        else:
            domains = [self.country_domain]

        for domain in domains:
            # Look for tech-related domains
            for prefix in ['tech', 'software', 'digital', 'cyber', 'data', 'ai', 'cloud']:
                test_domain = f'{prefix}*{domain}'
                results = self.query_index(test_domain)

                # Extract unique domains
                for result in results:
                    url = result.get('url', '')
                    parsed = urlparse(url)
                    if parsed.netloc and parsed.netloc not in tech_domains:
                        tech_domains.append(parsed.netloc)

        print(f"  Found {len(tech_domains)} potential tech companies")
        return tech_domains[:100]  # Limit to top 100

    def create_supply_chain_graph(self, all_signals: List[Dict]) -> pd.DataFrame:
        """Create supply chain relationship graph from signals"""

        edges = []

        for signal in all_signals:
            source = urlparse(signal['url']).netloc

            # Supplier relationships
            for supplier in signal['suppliers']:
                edges.append({
                    'source': source,
                    'target': supplier,
                    'relationship': 'supplier',
                    'url': signal['url']
                })

            # Customer relationships
            for customer in signal['customers']:
                edges.append({
                    'source': source,
                    'target': customer,
                    'relationship': 'customer',
                    'url': signal['url']
                })

            # Partner relationships
            for partner in signal['partners']:
                edges.append({
                    'source': source,
                    'target': partner,
                    'relationship': 'partner',
                    'url': signal['url']
                })

        return pd.DataFrame(edges)

    def create_tech_adoption_report(self, all_signals: List[Dict]) -> pd.DataFrame:
        """Create technology adoption report from signals"""

        tech_adoption = []

        for signal in all_signals:
            source = urlparse(signal['url']).netloc

            for tech_category, contexts in signal['technologies'].items():
                tech_adoption.append({
                    'company': source,
                    'technology': tech_category,
                    'evidence_count': len(contexts),
                    'url': signal['url'],
                    'sample_context': contexts[0] if contexts else ''
                })

        return pd.DataFrame(tech_adoption)

    def save_results(self, all_signals: List[Dict], tech_companies: List[str]):
        """Save extracted intelligence to files"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save raw signals
        signals_file = self.output_dir / f"cc_signals_{self.country}_{timestamp}.json"
        with open(signals_file, 'w') as f:
            json.dump(all_signals, f, indent=2)
        print(f"\nSaved signals to {signals_file}")

        # Create and save supply chain graph
        if all_signals:
            graph_df = self.create_supply_chain_graph(all_signals)
            graph_file = self.output_dir / f"cc_supply_chain_{self.country}_{timestamp}.csv"
            graph_df.to_csv(graph_file, index=False)
            print(f"Saved supply chain graph to {graph_file}")

            # Create and save tech adoption report
            tech_df = self.create_tech_adoption_report(all_signals)
            tech_file = self.output_dir / f"cc_tech_adoption_{self.country}_{timestamp}.csv"
            tech_df.to_csv(tech_file, index=False)
            print(f"Saved tech adoption to {tech_file}")

        # Save tech companies list
        companies_file = self.output_dir / f"cc_tech_companies_{self.country}_{timestamp}.txt"
        with open(companies_file, 'w') as f:
            for company in tech_companies:
                f.write(f"{company}\n")
        print(f"Saved tech companies to {companies_file}")

        # Create summary report
        summary_file = self.output_dir / f"cc_summary_{self.country}_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Common Crawl Intelligence Summary for {self.country}\n")
            f.write(f"{'=' * 50}\n\n")

            f.write(f"Tech companies found: {len(tech_companies)}\n")
            f.write(f"Pages analyzed: {len(all_signals)}\n\n")

            # Count relationships
            total_suppliers = sum(len(s['suppliers']) for s in all_signals)
            total_customers = sum(len(s['customers']) for s in all_signals)
            total_partners = sum(len(s['partners']) for s in all_signals)

            f.write(f"Supply Chain Relationships Found:\n")
            f.write(f"  Suppliers: {total_suppliers}\n")
            f.write(f"  Customers: {total_customers}\n")
            f.write(f"  Partners: {total_partners}\n\n")

            # Count technologies
            f.write(f"Technology Adoption:\n")
            tech_counts = {}
            for signal in all_signals:
                for tech in signal['technologies']:
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1

            for tech, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {tech}: {count} companies\n")

        print(f"Saved summary to {summary_file}")

    def run(self, sample_companies: int = 10, pages_per_company: int = 50):
        """Main execution method"""

        print(f"Starting Common Crawl intelligence extraction for {self.country}")
        print(f"Output directory: {self.output_dir}")

        # Find tech companies
        tech_companies = self.find_tech_companies()

        # Analyze sample of companies
        all_signals = []
        for i, company in enumerate(tech_companies[:sample_companies]):
            print(f"\n[{i+1}/{sample_companies}] Analyzing {company}")
            signals = self.analyze_domain(company, sample_size=pages_per_company)
            all_signals.extend(signals)

        # Save results
        self.save_results(all_signals, tech_companies)

        print("\nCommon Crawl intelligence extraction complete!")


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(description='Extract intelligence from Common Crawl')
    parser.add_argument('--country', required=True,
                       help='Country code (e.g., AT, DE, FR)')
    parser.add_argument('--companies', type=int, default=10,
                       help='Number of companies to analyze')
    parser.add_argument('--pages', type=int, default=50,
                       help='Pages per company to analyze')
    parser.add_argument('--out', default=None,
                       help='Output directory')

    args = parser.parse_args()

    # Set output directory
    if args.out:
        output_dir = Path(args.out)
    else:
        output_dir = Path('data/raw/source=commoncrawl') / f'country={args.country}' / f'date={datetime.now().strftime("%Y-%m-%d")}'

    # Create extractor and run
    extractor = CommonCrawlIntelligence(
        country=args.country,
        output_dir=output_dir
    )

    extractor.run(
        sample_companies=args.companies,
        pages_per_company=args.pages
    )


if __name__ == '__main__':
    main()
