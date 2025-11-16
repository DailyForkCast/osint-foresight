#!/usr/bin/env python3
"""
Deep per-source sitemap analysis for US_CAN think tanks.

For each source, this script:
1. Finds their sitemap
2. If it's a sitemap index, checks EACH sub-sitemap
3. Samples URLs from each sitemap to check date availability
4. Provides actionable recommendations
"""

import yaml
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import logging
import json
import time

logging.basicConfig(level=logging.INFO, format='%(message)s')

def fetch_with_retry(url, timeout=10, retries=3):
    """Fetch URL with retries."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/1.0)'
            })
            if response.status_code == 200:
                return response.text
            time.sleep(1)
        except Exception as e:
            if attempt == retries - 1:
                logging.warning(f"Failed to fetch {url}: {e}")
                return None
            time.sleep(1)
    return None

def analyze_url_sitemap(sitemap_xml, sitemap_url):
    """Analyze a sitemap containing URLs."""
    try:
        root = ET.fromstring(sitemap_xml)
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = root.findall('.//ns:url', ns)
        if not urls:
            return {"type": "empty", "count": 0}

        # Sample first 100 URLs
        sample_size = min(100, len(urls))
        dates_found = 0
        date_examples = []

        for url in urls[:sample_size]:
            lastmod = url.find('ns:lastmod', ns)
            if lastmod is not None and lastmod.text and lastmod.text.strip():
                dates_found += 1
                if len(date_examples) < 3:
                    loc = url.find('ns:loc', ns)
                    date_examples.append({
                        "url": loc.text if loc is not None else "unknown",
                        "date": lastmod.text
                    })

        return {
            "type": "url_sitemap",
            "total_urls": len(urls),
            "sample_size": sample_size,
            "dates_found": dates_found,
            "date_percentage": round(dates_found / sample_size * 100, 1),
            "has_dates": dates_found > 0,
            "date_examples": date_examples
        }
    except Exception as e:
        return {"type": "error", "error": str(e)}

def analyze_sitemap_index(sitemap_xml, index_url):
    """Analyze a sitemap index by checking each sub-sitemap."""
    try:
        root = ET.fromstring(sitemap_xml)
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        sitemaps = root.findall('.//ns:sitemap', ns)
        if not sitemaps:
            return {"type": "empty_index", "count": 0}

        logging.info(f"  Found {len(sitemaps)} sub-sitemaps, checking each...")

        sub_results = []
        for idx, sitemap_elem in enumerate(sitemaps[:10]):  # Check first 10 sub-sitemaps
            loc = sitemap_elem.find('ns:loc', ns)
            if loc is None or not loc.text:
                continue

            sub_url = loc.text
            logging.info(f"    [{idx+1}/{min(10, len(sitemaps))}] Checking {sub_url}...")

            sub_xml = fetch_with_retry(sub_url)
            if sub_xml:
                analysis = analyze_url_sitemap(sub_xml, sub_url)
                sub_results.append({
                    "url": sub_url,
                    "analysis": analysis
                })
                time.sleep(0.5)  # Be nice to servers

        # Aggregate results
        total_urls = sum(r["analysis"].get("total_urls", 0) for r in sub_results)
        total_with_dates = sum(r["analysis"].get("dates_found", 0) for r in sub_results)
        total_sampled = sum(r["analysis"].get("sample_size", 0) for r in sub_results)

        has_any_dates = any(r["analysis"].get("has_dates", False) for r in sub_results)

        return {
            "type": "sitemap_index",
            "total_sitemaps": len(sitemaps),
            "checked_sitemaps": len(sub_results),
            "total_urls": total_urls,
            "total_sampled": total_sampled,
            "dates_found": total_with_dates,
            "date_percentage": round(total_with_dates / total_sampled * 100, 1) if total_sampled > 0 else 0,
            "has_dates": has_any_dates,
            "sub_sitemaps": sub_results
        }
    except Exception as e:
        return {"type": "error", "error": str(e)}

def find_sitemap(domain):
    """Find sitemap for domain."""
    sitemap_urls = [
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/sitemap_index.xml",
        f"https://{domain}/post-sitemap.xml",
        f"https://www.{domain}/sitemap.xml",
    ]

    for url in sitemap_urls:
        xml = fetch_with_retry(url)
        if xml:
            return url, xml

    return None, None

def analyze_source(domain, rules):
    """Deep analysis of a single source."""
    logging.info(f"\n{'='*80}")
    logging.info(f"SOURCE: {domain}")
    logging.info(f"NAME: {rules.get('name', 'N/A')}")
    logging.info(f"{'='*80}")

    result = {
        "domain": domain,
        "name": rules.get("name", "N/A"),
        "sitemap_url": None,
        "analysis": None,
        "recommendation": None
    }

    # Find sitemap
    sitemap_url, sitemap_xml = find_sitemap(domain)

    if not sitemap_url:
        logging.info("❌ NO SITEMAP FOUND")
        result["recommendation"] = "MUST_CRAWL_HTML"
        result["analysis"] = {"type": "no_sitemap"}
        return result

    logging.info(f"✓ Found sitemap: {sitemap_url}")
    result["sitemap_url"] = sitemap_url

    # Determine if it's an index or URL sitemap
    try:
        root = ET.fromstring(sitemap_xml)
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Check for sitemap index
        if root.findall('.//ns:sitemap', ns):
            logging.info("  Type: SITEMAP INDEX")
            analysis = analyze_sitemap_index(sitemap_xml, sitemap_url)
        else:
            logging.info("  Type: URL SITEMAP")
            analysis = analyze_url_sitemap(sitemap_xml, sitemap_url)

        result["analysis"] = analysis

        # Determine recommendation
        if analysis.get("has_dates"):
            percentage = analysis.get("date_percentage", 0)
            if percentage > 80:
                result["recommendation"] = "CAN_PREFILTER_MOST"
                logging.info(f"✓ RECOMMENDATION: Can pre-filter {percentage}% of items (dates in sitemap)")
            elif percentage > 20:
                result["recommendation"] = "CAN_PREFILTER_SOME"
                logging.info(f"⚠ RECOMMENDATION: Can pre-filter {percentage}% of items (partial dates)")
            else:
                result["recommendation"] = "MUST_FETCH_PAGES_MOSTLY"
                logging.info(f"⚠ RECOMMENDATION: Only {percentage}% have dates, must fetch most pages")
        else:
            result["recommendation"] = "MUST_FETCH_ALL_PAGES"
            logging.info(f"❌ RECOMMENDATION: NO dates in sitemap, must fetch ALL pages to filter")

        # Show examples if dates found
        if analysis.get("date_examples"):
            logging.info("\n  Example URLs with dates:")
            for ex in analysis["date_examples"]:
                logging.info(f"    • {ex['date']} - {ex['url'][:80]}...")

        # Show stats
        if analysis.get("type") == "sitemap_index":
            logging.info(f"\n  Statistics:")
            logging.info(f"    Total sub-sitemaps: {analysis['total_sitemaps']}")
            logging.info(f"    Checked: {analysis['checked_sitemaps']}")
            logging.info(f"    Total URLs found: {analysis['total_urls']}")
            logging.info(f"    URLs with dates: {analysis['dates_found']}/{analysis['total_sampled']} ({analysis['date_percentage']}%)")
        elif analysis.get("type") == "url_sitemap":
            logging.info(f"\n  Statistics:")
            logging.info(f"    Total URLs: {analysis['total_urls']}")
            logging.info(f"    URLs with dates: {analysis['dates_found']}/{analysis['sample_size']} ({analysis['date_percentage']}%)")

    except Exception as e:
        logging.error(f"Error analyzing sitemap: {e}")
        result["analysis"] = {"type": "error", "error": str(e)}
        result["recommendation"] = "ERROR"

    return result

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

    logging.info(f"{'='*80}")
    logging.info(f"DEEP SITEMAP ANALYSIS - US_CAN SOURCES")
    logging.info(f"Total sources: {len(us_can_sources)}")
    logging.info(f"{'='*80}")

    results = {}

    for domain, rules in us_can_sources:
        result = analyze_source(domain, rules)
        results[domain] = result
        time.sleep(1)  # Be nice to servers

    # Save detailed results
    output_path = "F:/ThinkTank_Sweeps/US_CAN_SITEMAP_DEEP_ANALYSIS.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logging.info(f"\n\n{'='*80}")
    logging.info("SUMMARY BY RECOMMENDATION")
    logging.info(f"{'='*80}")

    # Group by recommendation
    by_recommendation = {}
    for domain, result in results.items():
        rec = result.get("recommendation", "UNKNOWN")
        if rec not in by_recommendation:
            by_recommendation[rec] = []
        by_recommendation[rec].append(domain)

    for rec, domains in sorted(by_recommendation.items()):
        logging.info(f"\n{rec}: {len(domains)} sources")
        for domain in domains:
            analysis = results[domain].get("analysis", {})
            percentage = analysis.get("date_percentage", 0)
            logging.info(f"  • {domain} ({percentage}% with dates)")

    logging.info(f"\n{'='*80}")
    logging.info(f"Detailed results saved to: {output_path}")
    logging.info(f"{'='*80}")

    # Critical insight
    can_prefilter = len(by_recommendation.get("CAN_PREFILTER_MOST", []))
    must_fetch_all = len(by_recommendation.get("MUST_FETCH_ALL_PAGES", []))
    must_crawl = len(by_recommendation.get("MUST_CRAWL_HTML", []))

    logging.info(f"\n🔍 ACTIONABLE INSIGHTS:")
    logging.info(f"   ✓ {can_prefilter} sources: Can pre-filter effectively (>80% have dates)")
    logging.info(f"   ⚠ {must_fetch_all} sources: Must fetch pages to filter (0% have dates)")
    logging.info(f"   ⚠ {must_crawl} sources: No sitemap, must crawl HTML")
    logging.info(f"\n   CRITICAL: Current filter logic would skip {must_fetch_all + must_crawl} sources entirely!")
    logging.info(f"   FIX NEEDED: Use three-way filtering logic")

if __name__ == "__main__":
    main()
