#!/usr/bin/env python3
"""
Regional University Collaboration Verifier
Checks collaboration rates for non-elite Italian universities
"""

import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RegionalUniversityVerifier:
    """Verify collaboration rates at regional Italian universities"""

    def __init__(self):
        self.output_dir = Path("reports/country=IT/regional_verification")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Sample of regional/non-elite Italian universities
        self.regional_universities = {
            # Southern Italy
            "University of Calabria": "https://ror.org/02rc97e94",
            "University of Basilicata": "https://ror.org/02qwy9e97",
            "University of Molise": "https://ror.org/04jkyg219",

            # Central Italy (smaller)
            "University of Camerino": "https://ror.org/05pf8gr89",
            "University of Macerata": "https://ror.org/05tj3dm42",

            # Northern Italy (regional)
            "University of Udine": "https://ror.org/05nsj7q40",
            "University of Brescia": "https://ror.org/02e3zdq86",

            # Islands
            "University of Sassari": "https://ror.org/05m9kpg86",
            "University of Messina": "https://ror.org/00rjy6r79"
        }

        # Elite universities for comparison
        self.elite_universities = {
            "Politecnico di Milano": "https://ror.org/01nffqt88",
            "University of Bologna": "https://ror.org/01111rn36",
            "Sapienza University": "https://ror.org/02p77k116",
            "Politecnico di Torino": "https://ror.org/00s6t1f81"
        }

        self.results = {
            'analysis_date': datetime.now().isoformat(),
            'regional_universities': {},
            'elite_universities': {},
            'comparison': {},
            'national_estimate': {}
        }

    def check_university_collaboration(self, name: str, ror_id: str, is_elite: bool = False) -> Dict:
        """Check China collaboration rate for a specific university"""

        logger.info(f"Checking {name}")

        # Using OpenAlex API with ROR ID
        base_url = "https://api.openalex.org/works"

        # Get total publications for this institution (2020-2024)
        total_params = {
            'filter': f'institutions.ror:{ror_id},from_publication_date:2020-01-01',
            'per_page': 1
        }

        # Get China collaborations
        china_params = {
            'filter': f'institutions.ror:{ror_id},institutions.country_code:CN,from_publication_date:2020-01-01',
            'per_page': 1
        }

        try:
            # Get total papers
            time.sleep(0.5)  # Rate limiting
            total_response = requests.get(base_url, params=total_params)
            if total_response.status_code == 200:
                total_papers = total_response.json().get('meta', {}).get('count', 0)
            else:
                total_papers = 0

            # Get China collaborations
            time.sleep(0.5)
            china_response = requests.get(base_url, params=china_params)
            if china_response.status_code == 200:
                china_papers = china_response.json().get('meta', {}).get('count', 0)
            else:
                china_papers = 0

            # Calculate rate
            if total_papers > 0:
                collaboration_rate = (china_papers / total_papers) * 100
            else:
                collaboration_rate = 0

            return {
                'name': name,
                'ror_id': ror_id,
                'total_papers': total_papers,
                'china_collaborations': china_papers,
                'collaboration_rate': round(collaboration_rate, 2),
                'type': 'elite' if is_elite else 'regional'
            }

        except Exception as e:
            logger.error(f"Error checking {name}: {e}")
            return {
                'name': name,
                'error': str(e)
            }

    def analyze_all_universities(self):
        """Check collaboration rates for all universities"""

        logger.info("Analyzing regional universities")
        for name, ror_id in self.regional_universities.items():
            result = self.check_university_collaboration(name, ror_id, is_elite=False)
            self.results['regional_universities'][name] = result

        logger.info("Analyzing elite universities for comparison")
        for name, ror_id in self.elite_universities.items():
            result = self.check_university_collaboration(name, ror_id, is_elite=True)
            self.results['elite_universities'][name] = result

    def calculate_weighted_average(self):
        """Calculate weighted national average based on research output"""

        regional_total_papers = 0
        regional_china_papers = 0
        elite_total_papers = 0
        elite_china_papers = 0

        # Sum regional universities
        for uni_data in self.results['regional_universities'].values():
            if 'total_papers' in uni_data:
                regional_total_papers += uni_data['total_papers']
                regional_china_papers += uni_data['china_collaborations']

        # Sum elite universities
        for uni_data in self.results['elite_universities'].values():
            if 'total_papers' in uni_data:
                elite_total_papers += uni_data['total_papers']
                elite_china_papers += uni_data['china_collaborations']

        # Calculate rates
        regional_rate = (regional_china_papers / regional_total_papers * 100) if regional_total_papers > 0 else 0
        elite_rate = (elite_china_papers / elite_total_papers * 100) if elite_total_papers > 0 else 0

        # Estimate national average (assuming our samples represent their categories)
        # Italy has ~90 universities: ~10 elite, ~20 mid-tier, ~60 regional
        # Assume mid-tier is between elite and regional
        mid_tier_rate = (elite_rate + regional_rate) / 2

        # Weight by estimated research output distribution
        # Elite: 40% of research, Mid-tier: 35%, Regional: 25%
        weighted_average = (
            (elite_rate * 0.40) +
            (mid_tier_rate * 0.35) +
            (regional_rate * 0.25)
        )

        self.results['comparison'] = {
            'regional_average_rate': round(regional_rate, 2),
            'elite_average_rate': round(elite_rate, 2),
            'estimated_mid_tier_rate': round(mid_tier_rate, 2),
            'weighted_national_average': round(weighted_average, 2),
            'ratio_elite_to_regional': round(elite_rate / regional_rate, 1) if regional_rate > 0 else None
        }

        self.results['national_estimate'] = {
            'method': 'Weighted average by institution type',
            'estimated_rate': round(weighted_average, 2),
            'openalex_actual': 3.38,
            'difference': round(weighted_average - 3.38, 2),
            'assessment': 'Close match validates prestige bias hypothesis' if abs(weighted_average - 3.38) < 2 else 'Significant difference'
        }

    def generate_report(self):
        """Generate comprehensive report"""

        self.analyze_all_universities()
        self.calculate_weighted_average()

        # Save JSON
        output_file = self.output_dir / 'regional_verification.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Create summary
        summary_file = self.output_dir / 'regional_verification_summary.md'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Regional vs Elite University Collaboration Verification\n\n")
            f.write(f"**Date:** {self.results['analysis_date']}\n\n")

            f.write("## Regional Universities (Non-Elite)\n\n")
            f.write("| University | Total Papers | China Collab | Rate |\n")
            f.write("|------------|--------------|--------------|------|\n")
            for name, data in self.results['regional_universities'].items():
                if 'total_papers' in data:
                    f.write(f"| {name} | {data['total_papers']} | {data['china_collaborations']} | {data['collaboration_rate']}% |\n")

            f.write("\n## Elite Universities (For Comparison)\n\n")
            f.write("| University | Total Papers | China Collab | Rate |\n")
            f.write("|------------|--------------|--------------|------|\n")
            for name, data in self.results['elite_universities'].items():
                if 'total_papers' in data:
                    f.write(f"| {name} | {data['total_papers']} | {data['china_collaborations']} | {data['collaboration_rate']}% |\n")

            f.write("\n## Key Findings\n\n")
            comp = self.results['comparison']
            f.write(f"- **Regional Average:** {comp['regional_average_rate']}%\n")
            f.write(f"- **Elite Average:** {comp['elite_average_rate']}%\n")
            f.write(f"- **Ratio:** Elite universities have {comp['ratio_elite_to_regional']}x higher China collaboration\n")
            f.write(f"- **Weighted National Estimate:** {comp['weighted_national_average']}%\n")
            f.write(f"- **OpenAlex National Actual:** 3.38%\n")

        logger.info(f"Reports saved to {self.output_dir}")

        return self.results

def main():
    verifier = RegionalUniversityVerifier()
    results = verifier.generate_report()

    print("\n=== REGIONAL UNIVERSITY VERIFICATION ===")
    print(f"Date: {results['analysis_date']}\n")

    print("Regional Universities Average:", results['comparison']['regional_average_rate'], "%")
    print("Elite Universities Average:", results['comparison']['elite_average_rate'], "%")
    print("Ratio (Elite/Regional):", results['comparison']['ratio_elite_to_regional'], "x")
    print("\nWeighted National Estimate:", results['comparison']['weighted_national_average'], "%")
    print("OpenAlex Actual:", "3.38%")

if __name__ == "__main__":
    main()
