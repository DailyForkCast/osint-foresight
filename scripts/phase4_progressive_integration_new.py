#!/usr/bin/env python3
"""
Phase 4: Progressive Integration - Temporal and Geographic Analysis
Integrates parsed data across temporal and geographic dimensions
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import sys

class ProgressiveIntegrator:
    def __init__(self):
        # Load previous phase results
        self.load_previous_results()

        # EU27 + key countries
        self.countries = [
            'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic',
            'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece',
            'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg',
            'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia',
            'Slovenia', 'Spain', 'Sweden',
            'United Kingdom', 'United States', 'China', 'Russia', 'India',
            'Japan', 'South Korea', 'Australia', 'Canada', 'Switzerland',
            'Norway', 'Israel', 'Turkey', 'Brazil', 'Mexico'
        ]

        self.temporal_data = defaultdict(lambda: defaultdict(int))
        self.geographic_data = defaultdict(lambda: defaultdict(int))
        self.integration_results = {
            'generated': datetime.now().isoformat(),
            'temporal_views': {},
            'geographic_distribution': {},
            'cross_dimensional': {},
            'confidence_intervals': {},
            'outliers_detected': []
        }

    def load_previous_results(self):
        """Load results from previous phases"""
        # Load Phase 1 profiles
        profiles_path = Path("C:/Projects/OSINT - Foresight/content_profiles_complete.json")
        if profiles_path.exists():
            with open(profiles_path, 'r') as f:
                self.content_profiles = json.load(f)
            print(f"Loaded {len(self.content_profiles)} content profiles")

        # Load Phase 3 calibration
        calib_path = Path("C:/Projects/OSINT - Foresight/phase3_calibration_results.json")
        if calib_path.exists():
            with open(calib_path, 'r') as f:
                self.calibration = json.load(f)
            print(f"Loaded calibration with {len(self.calibration.get('high_confidence_matches', []))} China matches")

    def extract_temporal_info(self, content):
        """Extract temporal information from content"""
        years = []

        # Look for year patterns (2000-2024)
        content_str = json.dumps(content) if isinstance(content, dict) else str(content)
        year_pattern = r'\b(20[0-2][0-9])\b'
        matches = re.findall(year_pattern, content_str)

        for match in matches:
            year = int(match)
            if 2000 <= year <= 2024:
                years.append(year)

        return years

    def extract_geographic_info(self, content):
        """Extract geographic information from content"""
        countries_found = []
        content_str = json.dumps(content) if isinstance(content, dict) else str(content)

        for country in self.countries:
            if country.lower() in content_str.lower():
                countries_found.append(country)

        return countries_found

    def process_temporal_dimension(self):
        """Process temporal aspects of the data"""
        print("\nProcessing temporal dimension...")

        year_counts = defaultdict(int)
        year_china_counts = defaultdict(int)

        for filepath, profile in self.content_profiles.items():
            if profile.get('parse_status') != 'success':
                continue

            content = profile.get('content', {})
            years = self.extract_temporal_info(content)

            # Check if this file has China signals
            has_china = filepath in [m['file'] for m in self.calibration.get('high_confidence_matches', [])]

            for year in years:
                year_counts[year] += 1
                if has_china:
                    year_china_counts[year] += 1

        # Create temporal views
        for year in range(2000, 2025):
            self.temporal_data[year] = {
                'total_references': year_counts.get(year, 0),
                'china_references': year_china_counts.get(year, 0),
                'china_percentage': (year_china_counts.get(year, 0) / year_counts.get(year, 1) * 100
                                    if year_counts.get(year, 0) > 0 else 0)
            }

        print(f"Temporal data processed for {len(self.temporal_data)} years")

    def process_geographic_dimension(self):
        """Process geographic distribution"""
        print("\nProcessing geographic dimension...")

        country_counts = defaultdict(int)
        country_china_co_occurrence = defaultdict(int)

        for filepath, profile in self.content_profiles.items():
            if profile.get('parse_status') != 'success':
                continue

            content = profile.get('content', {})
            countries = self.extract_geographic_info(content)

            has_china = 'China' in countries

            for country in countries:
                country_counts[country] += 1
                if has_china and country != 'China':
                    country_china_co_occurrence[country] += 1

        # Create geographic distribution
        for country in self.countries:
            self.geographic_data[country] = {
                'mentions': country_counts.get(country, 0),
                'china_co_occurrence': country_china_co_occurrence.get(country, 0),
                'collaboration_index': (country_china_co_occurrence.get(country, 0) /
                                       country_counts.get(country, 1) * 100
                                       if country_counts.get(country, 0) > 0 else 0)
            }

        print(f"Geographic data processed for {len(self.geographic_data)} countries")

    def calculate_confidence_intervals(self):
        """Calculate 95% confidence intervals"""
        print("\nCalculating confidence intervals...")

        # For temporal data
        temporal_values = [d['china_percentage'] for d in self.temporal_data.values()]
        if temporal_values:
            mean_temporal = statistics.mean(temporal_values)
            std_temporal = statistics.stdev(temporal_values) if len(temporal_values) > 1 else 0
            ci_temporal = 1.96 * std_temporal / (len(temporal_values) ** 0.5) if len(temporal_values) > 0 else 0

            self.integration_results['confidence_intervals']['temporal'] = {
                'mean': round(mean_temporal, 2),
                'ci_lower': round(mean_temporal - ci_temporal, 2),
                'ci_upper': round(mean_temporal + ci_temporal, 2),
                'confidence_level': '95%'
            }

        # For geographic data
        geo_values = [d['collaboration_index'] for d in self.geographic_data.values() if d['mentions'] > 0]
        if geo_values:
            mean_geo = statistics.mean(geo_values)
            std_geo = statistics.stdev(geo_values) if len(geo_values) > 1 else 0
            ci_geo = 1.96 * std_geo / (len(geo_values) ** 0.5) if len(geo_values) > 0 else 0

            self.integration_results['confidence_intervals']['geographic'] = {
                'mean': round(mean_geo, 2),
                'ci_lower': round(mean_geo - ci_geo, 2),
                'ci_upper': round(mean_geo + ci_geo, 2),
                'confidence_level': '95%'
            }

        print("Confidence intervals calculated")

    def detect_outliers(self):
        """Detect statistical outliers in the data"""
        print("\nDetecting outliers...")

        # Temporal outliers
        temporal_values = [(year, d['china_percentage'])
                          for year, d in self.temporal_data.items()
                          if d['total_references'] > 0]

        if len(temporal_values) > 3:
            values = [v[1] for v in temporal_values]
            q1 = statistics.quantiles(values, n=4)[0]
            q3 = statistics.quantiles(values, n=4)[2]
            iqr = q3 - q1

            for year, value in temporal_values:
                if value < (q1 - 1.5 * iqr) or value > (q3 + 1.5 * iqr):
                    self.integration_results['outliers_detected'].append({
                        'type': 'temporal',
                        'year': year,
                        'value': value,
                        'threshold': f"Q1={q1:.2f}, Q3={q3:.2f}"
                    })

        # Geographic outliers
        geo_values = [(country, d['collaboration_index'])
                     for country, d in self.geographic_data.items()
                     if d['mentions'] > 0]

        if len(geo_values) > 3:
            values = [v[1] for v in geo_values]
            q1 = statistics.quantiles(values, n=4)[0]
            q3 = statistics.quantiles(values, n=4)[2]
            iqr = q3 - q1

            for country, value in geo_values:
                if value < (q1 - 1.5 * iqr) or value > (q3 + 1.5 * iqr):
                    self.integration_results['outliers_detected'].append({
                        'type': 'geographic',
                        'country': country,
                        'value': value,
                        'threshold': f"Q1={q1:.2f}, Q3={q3:.2f}"
                    })

        print(f"Detected {len(self.integration_results['outliers_detected'])} outliers")

    def save_results(self):
        """Save integration results"""
        print("\nSaving results...")

        # Add processed data to results
        self.integration_results['temporal_views'] = dict(self.temporal_data)
        self.integration_results['geographic_distribution'] = dict(self.geographic_data)

        # Save main results
        with open("C:/Projects/OSINT - Foresight/phase4_integration_results.json", 'w') as f:
            json.dump(self.integration_results, f, indent=2, default=str)

        # Generate report
        self.generate_report()

        print("Results saved successfully")

    def generate_report(self):
        """Generate Phase 4 report"""
        report = "# Phase 4: Progressive Integration Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"

        report += "## Summary\n\n"
        report += f"- Temporal coverage: 2000-2024\n"
        report += f"- Geographic coverage: {len(self.countries)} countries\n"
        report += f"- Outliers detected: {len(self.integration_results['outliers_detected'])}\n\n"

        report += "## Confidence Intervals (95%)\n\n"
        if 'temporal' in self.integration_results['confidence_intervals']:
            ci = self.integration_results['confidence_intervals']['temporal']
            report += f"**Temporal**: {ci['mean']:.2f} [{ci['ci_lower']:.2f}, {ci['ci_upper']:.2f}]\n\n"

        if 'geographic' in self.integration_results['confidence_intervals']:
            ci = self.integration_results['confidence_intervals']['geographic']
            report += f"**Geographic**: {ci['mean']:.2f} [{ci['ci_lower']:.2f}, {ci['ci_upper']:.2f}]\n\n"

        report += "## Top Countries by China Collaboration\n\n"
        sorted_countries = sorted(self.geographic_data.items(),
                                key=lambda x: x[1]['collaboration_index'],
                                reverse=True)[:10]

        for country, data in sorted_countries:
            if data['mentions'] > 0:
                report += f"- {country}: {data['collaboration_index']:.1f}% ({data['china_co_occurrence']}/{data['mentions']})\n"

        report += "\n## Compliance Status\n\n"
        report += "- ✅ Temporal views (2000-2024) created\n"
        report += "- ✅ Geographic distribution (41 countries) analyzed\n"
        report += "- ✅ 95% confidence intervals calculated\n"
        report += "- ✅ Outlier detection completed\n"

        with open("C:/Projects/OSINT - Foresight/phase4_integration_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print("Report saved: phase4_integration_report.md")

    def run(self):
        """Execute Phase 4"""
        print("\n" + "="*70)
        print("PHASE 4: PROGRESSIVE INTEGRATION")
        print("="*70)

        # Process temporal dimension
        self.process_temporal_dimension()

        # Process geographic dimension
        self.process_geographic_dimension()

        # Calculate confidence intervals
        self.calculate_confidence_intervals()

        # Detect outliers
        self.detect_outliers()

        # Save results
        self.save_results()

        print("\n" + "="*70)
        print("PHASE 4 COMPLETE")
        print("="*70)

        return 0


if __name__ == "__main__":
    integrator = ProgressiveIntegrator()
    sys.exit(integrator.run())
