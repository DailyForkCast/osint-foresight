#!/usr/bin/env python3
"""
Strict Verification - Filter for ACTUAL Europe-China agreements only
Exclude noise, irrelevant content, and misclassified URLs
"""

import json
from pathlib import Path
from collections import Counter
import re
from datetime import datetime

class StrictVerifier:
    """Apply strict verification criteria"""

    def __init__(self):
        """Initialize verifier"""
        self.results_dir = Path('athena_results')

        # Noise patterns to exclude
        self.exclude_patterns = [
            'casino', 'gambling', 'slot', 'poker', 'bet', 'gaming',
            'login', 'signin', 'password',
            'africa', 'south-africa', 'kenya', 'nigeria',
            'india', 'pakistan', 'bangladesh',
            'russia', 'putin',
            'america', 'usa', 'united-states', 'canada', 'mexico',
            'brazil', 'argentina', 'chile',
            'australia', 'new-zealand',
            'japan', 'korea', 'vietnam', 'thailand', 'indonesia',
            'iran', 'saudi', 'israel', 'uae',
            'porn', 'sex', 'adult', 'escort',
            'shop', 'store', 'buy', 'sale', 'discount',
            'download', 'torrent', 'crack', 'keygen'
        ]

        # European entities (strict list)
        self.european_entities = {
            # EU institutions
            'eu': ['european union', 'europa.eu', 'ec.europa.eu', 'european commission'],
            # EU member states
            'germany': ['germany', 'german', 'deutschland', 'berlin', 'munich', 'hamburg', '.de'],
            'france': ['france', 'french', 'paris', 'lyon', 'marseille', '.fr'],
            'italy': ['italy', 'italian', 'rome', 'milan', 'venice', '.it'],
            'spain': ['spain', 'spanish', 'madrid', 'barcelona', '.es'],
            'poland': ['poland', 'polish', 'warsaw', 'krakow', '.pl'],
            'netherlands': ['netherlands', 'dutch', 'amsterdam', 'rotterdam', '.nl'],
            'belgium': ['belgium', 'belgian', 'brussels', '.be'],
            'greece': ['greece', 'greek', 'athens', 'thessaloniki', '.gr'],
            'portugal': ['portugal', 'portuguese', 'lisbon', 'porto', '.pt'],
            'czech': ['czech', 'prague', 'czechia', '.cz'],
            'hungary': ['hungary', 'hungarian', 'budapest', '.hu'],
            'sweden': ['sweden', 'swedish', 'stockholm', '.se'],
            'austria': ['austria', 'austrian', 'vienna', '.at'],
            'denmark': ['denmark', 'danish', 'copenhagen', '.dk'],
            'finland': ['finland', 'finnish', 'helsinki', '.fi'],
            'slovakia': ['slovakia', 'slovak', 'bratislava', '.sk'],
            'ireland': ['ireland', 'irish', 'dublin', '.ie'],
            'croatia': ['croatia', 'croatian', 'zagreb', '.hr'],
            'lithuania': ['lithuania', 'lithuanian', 'vilnius', '.lt'],
            'slovenia': ['slovenia', 'slovenian', 'ljubljana', '.si'],
            'latvia': ['latvia', 'latvian', 'riga', '.lv'],
            'estonia': ['estonia', 'estonian', 'tallinn', '.ee'],
            'luxembourg': ['luxembourg', '.lu'],
            'cyprus': ['cyprus', 'cypriot', '.cy'],
            'malta': ['malta', 'maltese', '.mt'],
            'romania': ['romania', 'romanian', 'bucharest', '.ro'],
            'bulgaria': ['bulgaria', 'bulgarian', 'sofia', '.bg'],
            # Non-EU Europe
            'uk': ['uk', 'united kingdom', 'britain', 'british', 'london', 'manchester', '.uk'],
            'switzerland': ['switzerland', 'swiss', 'zurich', 'geneva', '.ch'],
            'norway': ['norway', 'norwegian', 'oslo', 'bergen', '.no'],
            'iceland': ['iceland', 'icelandic', 'reykjavik', '.is'],
            'serbia': ['serbia', 'serbian', 'belgrade', '.rs'],
            'albania': ['albania', 'albanian', 'tirana', '.al'],
            'macedonia': ['macedonia', 'macedonian', 'skopje', '.mk'],
            'montenegro': ['montenegro', 'podgorica', '.me'],
            'bosnia': ['bosnia', 'sarajevo', '.ba'],
            'kosovo': ['kosovo', 'pristina'],
            'turkey': ['turkey', 'turkish', 'turkiye', 'istanbul', 'ankara', '.tr'],
            'georgia': ['georgia', 'tbilisi', '.ge'],
            'armenia': ['armenia', 'yerevan', '.am'],
            'azerbaijan': ['azerbaijan', 'baku', '.az']
        }

        # Chinese entities (strict list)
        self.chinese_entities = [
            'china', 'chinese', 'prc', 'peoples republic',
            'beijing', 'shanghai', 'guangzhou', 'shenzhen', 'tianjin',
            'wuhan', 'chengdu', 'xian', 'hangzhou', 'nanjing',
            'sino-', 'cn-', '.cn',
            'belt and road', 'belt & road', 'bri', 'silk road',
            'huawei', 'alibaba', 'tencent', 'bytedance', 'xiaomi',
            'sinopec', 'cnpc', 'cosco', 'china railway', 'sinohydro'
        ]

        # Agreement indicators (must have)
        self.agreement_indicators = [
            'agreement', 'cooperation', 'partnership', 'mou', 'memorandum',
            'treaty', 'accord', 'pact', 'deal', 'contract',
            'joint', 'bilateral', 'framework', 'understanding',
            'sister city', 'twin city', 'investment', 'trade'
        ]

    def load_audit_results(self):
        """Load the audit results"""
        audit_file = self.results_dir / 'COMPLETE_AUDIT_20250928_163111.json'
        with open(audit_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def is_excluded(self, url):
        """Check if URL should be excluded"""
        url_lower = url.lower()
        for pattern in self.exclude_patterns:
            if pattern in url_lower:
                return True
        return False

    def has_european_entity(self, url):
        """Check for specific European entity"""
        url_lower = url.lower()
        for country, keywords in self.european_entities.items():
            for keyword in keywords:
                if keyword in url_lower:
                    return country
        return None

    def has_chinese_entity(self, url):
        """Check for Chinese entity"""
        url_lower = url.lower()
        for entity in self.chinese_entities:
            if entity in url_lower:
                return True
        return False

    def has_agreement_indicator(self, url):
        """Check for agreement indicators"""
        url_lower = url.lower()
        for indicator in self.agreement_indicators:
            if indicator in url_lower:
                return indicator
        return None

    def verify_strictly(self):
        """Apply strict verification"""
        print("\n" + "="*80)
        print("STRICT VERIFICATION - ACTUAL AGREEMENTS ONLY")
        print("="*80)

        # Load audit data
        audit = self.load_audit_results()
        sample_urls = [item['url'] for item in audit['sample_relevant']]

        # Load all unique URLs from the original harvest files
        all_urls = set()
        for json_file in self.results_dir.glob('*.json'):
            if 'AUDIT' not in json_file.name and 'STRICT' not in json_file.name:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.extract_urls(data, all_urls)
                except:
                    pass

        print(f"Total unique URLs to verify: {len(all_urls)}")

        # Strict verification
        verified_agreements = []
        excluded_noise = []
        missing_europe = []
        missing_china = []
        missing_agreement = []

        for url in all_urls:
            # Skip if excluded pattern
            if self.is_excluded(url):
                excluded_noise.append(url)
                continue

            # Check for European entity
            europe = self.has_european_entity(url)
            if not europe:
                missing_europe.append(url)
                continue

            # Check for Chinese entity
            if not self.has_chinese_entity(url):
                missing_china.append(url)
                continue

            # Check for agreement indicator
            agreement_type = self.has_agreement_indicator(url)
            if not agreement_type:
                missing_agreement.append(url)
                continue

            # Passes all checks
            verified_agreements.append({
                'url': url,
                'european_entity': europe,
                'agreement_type': agreement_type
            })

        # Statistics
        print(f"\n--- VERIFICATION RESULTS ---")
        print(f"Excluded (noise/spam): {len(excluded_noise)}")
        print(f"Missing European entity: {len(missing_europe)}")
        print(f"Missing Chinese entity: {len(missing_china)}")
        print(f"Missing agreement indicator: {len(missing_agreement)}")
        print(f"\nVERIFIED AGREEMENTS: {len(verified_agreements)}")

        # Country breakdown
        country_counts = Counter(a['european_entity'] for a in verified_agreements)
        print(f"\n--- BY EUROPEAN COUNTRY/ENTITY ---")
        for country, count in country_counts.most_common(20):
            print(f"{country:20} {count:4} agreements")

        # Agreement type breakdown
        type_counts = Counter(a['agreement_type'] for a in verified_agreements)
        print(f"\n--- BY AGREEMENT TYPE ---")
        for agreement_type, count in type_counts.most_common():
            print(f"{agreement_type:20} {count:4} agreements")

        # Sample verified agreements
        print(f"\n--- SAMPLE VERIFIED AGREEMENTS ---")
        for agreement in verified_agreements[:10]:
            print(f"\nURL: {agreement['url'][:100]}")
            print(f"  European: {agreement['european_entity']}")
            print(f"  Type: {agreement['agreement_type']}")

        # Save results
        strict_results = {
            'verification_timestamp': datetime.now().isoformat(),
            'total_urls_checked': len(all_urls),
            'excluded_noise': len(excluded_noise),
            'missing_europe': len(missing_europe),
            'missing_china': len(missing_china),
            'missing_agreement': len(missing_agreement),
            'verified_agreements': len(verified_agreements),
            'country_breakdown': dict(country_counts),
            'type_breakdown': dict(type_counts),
            'verified_list': verified_agreements
        }

        output_file = self.results_dir / f'STRICT_VERIFICATION_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(strict_results, f, indent=2, ensure_ascii=False)

        print(f"\n--- STRICT VERIFICATION SAVED ---")
        print(f"Location: {output_file}")

        print(f"\n" + "="*80)
        print(f"FINAL VERIFIED COUNT")
        print(f"="*80)
        print(f"ACTUAL Europe-China Agreements with strict criteria: {len(verified_agreements)}")
        print(f"\nThese URLs:")
        print(f"1. Do NOT contain noise/spam keywords")
        print(f"2. DO contain specific European country/entity")
        print(f"3. DO contain Chinese entity/keyword")
        print(f"4. DO contain agreement/cooperation indicator")

        return strict_results

    def extract_urls(self, obj, url_set):
        """Recursively extract URLs"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['url', 'source_url'] and isinstance(value, str) and value.startswith('http'):
                    url_set.add(value)
                else:
                    self.extract_urls(value, url_set)
        elif isinstance(obj, list):
            for item in obj:
                self.extract_urls(item, url_set)

def main():
    """Run strict verification"""
    verifier = StrictVerifier()
    verifier.verify_strictly()

if __name__ == "__main__":
    main()
