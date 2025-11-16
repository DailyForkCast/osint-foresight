#!/usr/bin/env python3
"""
Analyze sitemap date availability for all US_CAN sources.

This script checks each US_CAN source to see if their sitemaps/RSS feeds
provide publication dates in metadata (lastmod, published, etc.).
"""

import yaml
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import logging
from collections import defaultdict
import json

logging.basicConfig(level=logging.INFO, format='%(message)s')

def find_sitemap(domain):
    """Try to find sitemap for domain."""
    # Try common sitemap locations
    sitemap_urls = [
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/sitemap_index.xml",
        f"https://{domain}/post-sitemap.xml",
        f"https://www.{domain}/sitemap.xml",
    ]

    for sitemap_url in sitemap_urls:
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                return sitemap_url, response.text
        except:
            continue

    return None, None

def analyze_sitemap_dates(sitemap_xml):
    """Analyze whether sitemap contains lastmod dates."""
    try:
        root = ET.fromstring(sitemap_xml)

        # Handle namespaces
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Check if this is a sitemap index
        sitemapindex = root.findall('.//ns:sitemap', ns)
        if sitemapindex:
            return {
                "type": "sitemap_index",
                "count": len(sitemapindex),
                "sample_has_date": None
            }

        # Check for URLs
        urls = root.findall('.//ns:url', ns)
        if not urls:
            return {"type": "unknown", "count": 0, "sample_has_date": None}

        # Sample first 50 URLs
        sample_size = min(50, len(urls))
        dates_found = 0

        for url in urls[:sample_size]:
            lastmod = url.find('ns:lastmod', ns)
            if lastmod is not None and lastmod.text and lastmod.text.strip() != "":
                dates_found += 1

        return {
            "type": "url_set",
            "count": len(urls),
            "sample_size": sample_size,
            "dates_found": dates_found,
            "date_availability": f"{dates_found}/{sample_size}",
            "has_dates": dates_found > 0
        }
    except Exception as e:
        return {"type": "error", "error": str(e)}

def check_rss_dates(domain, rules):
    """Check if RSS feed provides dates."""
    rss_url = rules.get("rss_url")
    if not rss_url:
        return None

    if not rss_url.startswith("http"):
        rss_url = f"https://{domain}{rss_url}"

    try:
        response = requests.get(rss_url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.text)

            # Check for RSS items
            items = root.findall('.//item')
            if items:
                sample_size = min(10, len(items))
                dates_found = 0

                for item in items[:sample_size]:
                    pubDate = item.find('pubDate')
                    published = item.find('published')
                    if (pubDate is not None and pubDate.text) or (published is not None and published.text):
                        dates_found += 1

                return {
                    "type": "rss",
                    "count": len(items),
                    "sample_size": sample_size,
                    "dates_found": dates_found,
                    "date_availability": f"{dates_found}/{sample_size}",
                    "has_dates": dates_found > 0
                }
    except:
        pass

    return None

def main():
    # Load source rules
    with open("C:/Projects/OSINT - Foresight/config/thinktank_source_rules.yaml", 'r') as f:
        source_rules = yaml.safe_load(f)

    # Get US_CAN sources
    us_can_sources = []
    for domain, rules in source_rules.items():
        if domain == "default":
            continue
        if rules.get("region") == "US_CAN":
            us_can_sources.append((domain, rules))

    logging.info(f"Found {len(us_can_sources)} US_CAN sources")
    logging.info("=" * 80)

    results = {}

    for domain, rules in us_can_sources:
        logging.info(f"\n{'='*80}")
        logging.info(f"Analyzing: {domain}")
        logging.info(f"Name: {rules.get('name', 'N/A')}")
        logging.info(f"{'='*80}")

        result = {
            "domain": domain,
            "name": rules.get("name", "N/A"),
            "sitemap": None,
            "rss": None,
            "date_availability": "unknown"
        }

        # Check sitemap
        sitemap_url, sitemap_xml = find_sitemap(domain)
        if sitemap_url:
            logging.info(f"✓ Found sitemap: {sitemap_url}")
            sitemap_analysis = analyze_sitemap_dates(sitemap_xml)
            result["sitemap"] = sitemap_analysis

            if sitemap_analysis.get("type") == "url_set":
                logging.info(f"  Type: URL set")
                logging.info(f"  Total URLs: {sitemap_analysis['count']}")
                logging.info(f"  Dates in sample: {sitemap_analysis['date_availability']}")

                if sitemap_analysis.get("has_dates"):
                    logging.info(f"  ✓ DATES AVAILABLE IN SITEMAP")
                    result["date_availability"] = "sitemap"
                else:
                    logging.info(f"  ✗ NO DATES IN SITEMAP")
            elif sitemap_analysis.get("type") == "sitemap_index":
                logging.info(f"  Type: Sitemap index ({sitemap_analysis['count']} sitemaps)")
                result["date_availability"] = "needs_deeper_check"
        else:
            logging.info(f"✗ No sitemap found")

        # Check RSS
        rss_analysis = check_rss_dates(domain, rules)
        if rss_analysis:
            result["rss"] = rss_analysis
            logging.info(f"✓ Found RSS feed")
            logging.info(f"  Total items: {rss_analysis['count']}")
            logging.info(f"  Dates in sample: {rss_analysis['date_availability']}")

            if rss_analysis.get("has_dates"):
                logging.info(f"  ✓ DATES AVAILABLE IN RSS")
                if result["date_availability"] == "unknown":
                    result["date_availability"] = "rss"
            else:
                logging.info(f"  ✗ NO DATES IN RSS")

        # Final assessment
        if result["date_availability"] == "unknown":
            if not sitemap_url and not rss_analysis:
                result["date_availability"] = "no_feeds"
                logging.info(f"\n⚠ NO SITEMAP OR RSS FOUND - MUST CRAWL PAGES")
            else:
                result["date_availability"] = "none"
                logging.info(f"\n⚠ NO DATES IN METADATA - MUST FETCH PAGES TO FILTER")

        results[domain] = result

    # Save results
    output_path = "F:/ThinkTank_Sweeps/US_CAN_SITEMAP_ANALYSIS.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logging.info(f"\n\n{'='*80}")
    logging.info("SUMMARY")
    logging.info(f"{'='*80}")

    # Categorize sources
    has_sitemap_dates = [d for d, r in results.items() if r["date_availability"] == "sitemap"]
    has_rss_dates = [d for d, r in results.items() if r["date_availability"] == "rss"]
    no_dates = [d for d, r in results.items() if r["date_availability"] == "none"]
    no_feeds = [d for d, r in results.items() if r["date_availability"] == "no_feeds"]
    needs_check = [d for d, r in results.items() if r["date_availability"] == "needs_deeper_check"]

    logging.info(f"\nSources with dates in sitemap: {len(has_sitemap_dates)}")
    for domain in has_sitemap_dates:
        logging.info(f"  ✓ {domain}")

    logging.info(f"\nSources with dates in RSS: {len(has_rss_dates)}")
    for domain in has_rss_dates:
        logging.info(f"  ✓ {domain}")

    logging.info(f"\nSources WITHOUT dates in metadata: {len(no_dates)}")
    for domain in no_dates:
        logging.info(f"  ✗ {domain} - MUST FETCH PAGES")

    logging.info(f"\nSources with no feeds: {len(no_feeds)}")
    for domain in no_feeds:
        logging.info(f"  ⚠ {domain} - MUST CRAWL")

    if needs_check:
        logging.info(f"\nSources needing deeper check: {len(needs_check)}")
        for domain in needs_check:
            logging.info(f"  ? {domain}")

    logging.info(f"\n{'='*80}")
    logging.info(f"Results saved to: {output_path}")
    logging.info(f"{'='*80}")

    # Critical insight
    logging.info(f"\n🔍 KEY INSIGHT:")
    logging.info(f"   {len(has_sitemap_dates) + len(has_rss_dates)} sources can be pre-filtered (dates in metadata)")
    logging.info(f"   {len(no_dates) + len(no_feeds)} sources MUST fetch pages to determine date")
    logging.info(f"\n   Current filter logic filters out {len(no_dates) + len(no_feeds)} sources entirely!")
    logging.info(f"   This is why CSIS returned 0 results.")

if __name__ == "__main__":
    main()
