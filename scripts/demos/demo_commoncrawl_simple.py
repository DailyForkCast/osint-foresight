#!/usr/bin/env python3
"""
Simple demonstration of Common Crawl intelligence extraction
Shows how to find supplier relationships and technology signals
"""

import requests
import json
import re
from typing import List, Dict

def demo_common_crawl():
    """Demonstrate Common Crawl intelligence extraction"""

    print("=" * 60)
    print("COMMON CRAWL INTELLIGENCE EXTRACTION DEMO")
    print("=" * 60)

    # Step 1: Query Common Crawl Index
    print("\n1. QUERYING COMMON CRAWL INDEX")
    print("-" * 40)

    # Example: Find Austrian tech company pages
    index_url = "https://index.commoncrawl.org/CC-MAIN-2024-10-index"
    params = {
        'url': '*.at/about*',  # Austrian domains, about pages
        'output': 'json',
        'limit': 5
    }

    print(f"Query: Find Austrian company 'about' pages")
    print(f"URL pattern: {params['url']}")

    try:
        response = requests.get(index_url, params=params)
        results = []
        for line in response.text.strip().split('\n')[:3]:  # First 3 results
            if line:
                result = json.loads(line)
                results.append(result)
                print(f"  Found: {result['url']}")
    except Exception as e:
        print(f"  (Demo mode - simulating results)")
        results = [
            {'url': 'https://example-tech.at/about', 'offset': '1000', 'length': '50000'},
            {'url': 'https://ai-startup.at/about-us', 'offset': '2000', 'length': '45000'},
        ]
        for r in results:
            print(f"  Found: {r['url']}")

    # Step 2: Demonstrate extraction patterns
    print("\n2. EXTRACTION PATTERNS")
    print("-" * 40)

    # Simulate HTML content from a company page
    sample_html = """
    <html>
    <body>
        <div class="about-section">
            <h2>About Our Company</h2>
            <p>We are a leading AI company based in Vienna, Austria.
            Our key suppliers include NVIDIA GmbH for GPUs and Amazon Web Services for cloud infrastructure.
            We partner with Microsoft Research on quantum computing initiatives.</p>

            <h3>Our Technology Stack</h3>
            <p>We leverage TensorFlow and PyTorch for our machine learning models.
            Our infrastructure runs on AWS using Kubernetes for container orchestration.
            We are ISO 27001 certified for information security.</p>

            <h3>Key Customers</h3>
            <p>We proudly serve major enterprises including Siemens AG, Red Bull GmbH,
            and Erste Bank. Our solutions power AI initiatives across Europe.</p>
        </div>
    </body>
    </html>
    """

    print("Sample page content:")
    print("  URL: https://ai-startup.at/about-us")

    # Step 3: Extract supply chain relationships
    print("\n3. EXTRACTING SUPPLY CHAIN RELATIONSHIPS")
    print("-" * 40)

    # Supplier patterns
    supplier_pattern = r"(?:supplier|vendor)s?\s+include\s+([A-Z][A-Za-z\s&,]+(?:GmbH|AG|Inc|Ltd))"
    suppliers = re.findall(supplier_pattern, sample_html, re.IGNORECASE)

    print("Suppliers found:")
    for supplier in suppliers:
        companies = [c.strip() for c in supplier.split(' and ')]
        for company in companies:
            print(f"  -> {company}")

    # Partner patterns
    partner_pattern = r"partner\s+with\s+([A-Z][A-Za-z\s]+(?:Research|Labs|Institute)?)"
    partners = re.findall(partner_pattern, sample_html, re.IGNORECASE)

    print("\nPartners found:")
    for partner in partners:
        print(f"  -> {partner}")

    # Customer patterns
    customer_pattern = r"(?:serve|serving)\s+(?:major\s+)?(?:enterprises\s+)?including\s+([^.]+)"
    customers = re.findall(customer_pattern, sample_html, re.IGNORECASE)

    print("\nCustomers found:")
    if customers:
        customer_list = customers[0].split(',')
        for customer in customer_list:
            customer = customer.replace(' and ', ',').strip()
            if customer:
                print(f"  -> {customer}")

    # Step 4: Extract technology adoption
    print("\n4. EXTRACTING TECHNOLOGY SIGNALS")
    print("-" * 40)

    tech_patterns = {
        'AI/ML': ['TensorFlow', 'PyTorch', 'machine learning', 'AI'],
        'Cloud': ['AWS', 'Amazon Web Services', 'Azure', 'Google Cloud'],
        'DevOps': ['Kubernetes', 'Docker', 'container orchestration'],
        'Quantum': ['quantum computing', 'quantum', 'QKD'],
    }

    print("Technologies detected:")
    for category, keywords in tech_patterns.items():
        found = []
        for keyword in keywords:
            if keyword.lower() in sample_html.lower():
                found.append(keyword)
        if found:
            print(f"  {category}: {', '.join(found)}")

    # Step 5: Extract certifications
    print("\n5. EXTRACTING CERTIFICATIONS")
    print("-" * 40)

    cert_pattern = r"(ISO\s+\d+(?::\d+)?)\s+certified"
    certifications = re.findall(cert_pattern, sample_html, re.IGNORECASE)

    print("Certifications found:")
    for cert in certifications:
        print(f"  -> {cert}")

    # Step 6: Build intelligence graph
    print("\n6. INTELLIGENCE GRAPH")
    print("-" * 40)

    print("Supply Chain Network:")
    print("  ai-startup.at")
    print("    +-- Suppliers:")
    print("    |   +-- NVIDIA GmbH (GPUs)")
    print("    |   +-- Amazon Web Services (Cloud)")
    print("    +-- Partners:")
    print("    |   +-- Microsoft Research (Quantum)")
    print("    +-- Customers:")
    print("        +-- Siemens AG")
    print("        +-- Red Bull GmbH")
    print("        +-- Erste Bank")

    # Step 7: Scale to full analysis
    print("\n7. SCALING TO FULL ANALYSIS")
    print("-" * 40)

    print("To analyze an entire country:")
    print("  1. Query index for all .at domains (~100,000 pages)")
    print("  2. Filter for relevant pages (about, partners, technology)")
    print("  3. Download WARC records (only needed pages, not all)")
    print("  4. Extract signals from each page")
    print("  5. Build comprehensive supply chain graph")
    print("  6. Identify technology clusters")
    print("  7. Track changes over time (monthly crawls)")

    print("\nEstimated data for Austria:")
    print("  * Tech companies: ~500-1000")
    print("  * Relevant pages: ~10,000-20,000")
    print("  * Download size: ~1-5 GB (filtered)")
    print("  * Processing time: 2-4 hours")
    print("  * Unique relationships: ~5,000-10,000")

    # Example output
    print("\n8. EXAMPLE INTELLIGENCE OUTPUT")
    print("-" * 40)

    intelligence = {
        "Hidden Suppliers": [
            "NVIDIA GmbH → ai-startup.at (GPUs)",
            "TSMC → austriamicrosystems.com (chip fabrication)",
            "Infineon → kapsch.at (semiconductors)"
        ],
        "Technology Adoption": {
            "AI/ML": "45% of tech companies",
            "Cloud": "78% using AWS or Azure",
            "Quantum": "3 companies with quantum initiatives"
        },
        "Supply Chain Risks": [
            "High dependency on Asian semiconductors",
            "Cloud concentration in US providers",
            "Single-source suppliers for critical components"
        ],
        "Emerging Partnerships": [
            "AT-DE quantum computing collaboration",
            "AT-CH blockchain initiative",
            "AT-CZ AI research network"
        ]
    }

    print(json.dumps(intelligence, indent=2))

    print("\n" + "=" * 60)
    print("END OF DEMO")
    print("=" * 60)

if __name__ == '__main__':
    demo_common_crawl()
