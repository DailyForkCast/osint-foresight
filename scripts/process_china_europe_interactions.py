#!/usr/bin/env python3
"""
Process China-Europe/Eurasia Interactions Across All Data Sources
Captures relationships between China and ALL European/Eurasian countries
"""

import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import gzip
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ChinaEuropeInteractionProcessor:
    """Process all China-Europe/Eurasia interactions across data sources"""
    
    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        
        # COMPREHENSIVE target country lists
        
        # EU Member States (27)
        self.eu_countries = {
            'AT': 'Austria',
            'BE': 'Belgium', 
            'BG': 'Bulgaria',
            'HR': 'Croatia',
            'CY': 'Cyprus',
            'CZ': 'Czech Republic',
            'DK': 'Denmark',
            'EE': 'Estonia',
            'FI': 'Finland',
            'FR': 'France',
            'DE': 'Germany',
            'GR': 'Greece',
            'HU': 'Hungary',
            'IE': 'Ireland',
            'IT': 'Italy',
            'LV': 'Latvia',
            'LT': 'Lithuania',
            'LU': 'Luxembourg',
            'MT': 'Malta',
            'NL': 'Netherlands',
            'PL': 'Poland',
            'PT': 'Portugal',
            'RO': 'Romania',
            'SK': 'Slovakia',
            'SI': 'Slovenia',
            'ES': 'Spain',
            'SE': 'Sweden'
        }
        
        # European Non-EU Countries
        self.europe_non_eu = {
            'AL': 'Albania',
            'AD': 'Andorra',
            'AM': 'Armenia',
            'AZ': 'Azerbaijan',
            'BY': 'Belarus',
            'BA': 'Bosnia and Herzegovina',
            'GE': 'Georgia',
            'IS': 'Iceland',
            'XK': 'Kosovo',
            'LI': 'Liechtenstein',
            'MD': 'Moldova',
            'MC': 'Monaco',
            'ME': 'Montenegro',
            'MK': 'North Macedonia',
            'NO': 'Norway',
            'RU': 'Russia',
            'SM': 'San Marino',
            'RS': 'Serbia',
            'CH': 'Switzerland',
            'TR': 'Turkey',
            'UA': 'Ukraine',
            'GB': 'United Kingdom',
            'VA': 'Vatican City'
        }
        
        # Central Asian Countries (Eurasia)
        self.central_asia = {
            'KZ': 'Kazakhstan',
            'KG': 'Kyrgyzstan',
            'TJ': 'Tajikistan',
            'TM': 'Turkmenistan',
            'UZ': 'Uzbekistan'
        }
        
        # Belt and Road Initiative (BRI) Countries in Europe/Eurasia
        self.bri_europe = [
            'AL', 'AM', 'AT', 'AZ', 'BY', 'BA', 'BG', 'HR', 'CZ', 'EE',
            'GE', 'GR', 'HU', 'IT', 'KZ', 'KG', 'LV', 'LT', 'LU', 'MD',
            'ME', 'MK', 'PL', 'PT', 'RO', 'RU', 'RS', 'SK', 'SI', 'TJ',
            'TR', 'TM', 'UA', 'UZ'
        ]
        
        # 17+1 Format Countries (China-CEEC)
        self.seventeen_plus_one = [
            'AL', 'BA', 'BG', 'HR', 'CZ', 'EE', 'GR', 'HU', 'LV', 'LT',
            'ME', 'MK', 'PL', 'RO', 'RS', 'SK', 'SI'
        ]
        
        # All target countries combined
        self.all_target_countries = {}
        self.all_target_countries.update(self.eu_countries)
        self.all_target_countries.update(self.europe_non_eu)
        self.all_target_countries.update(self.central_asia)
        
        # China identifiers
        self.china_codes = ['CN', 'CHN', 'HK', 'HKG', 'MO', 'MAC']
        
        # Initialize results structure
        self.interactions = {
            'timestamp': datetime.now().isoformat(),
            'by_country': {},
            'by_category': {
                'eu_members': {},
                'bri_countries': {},
                '17_plus_1': {},
                'central_asia': {},
                'other_europe': {}
            },
            'by_source': {
                'openalex': {},
                'ted': {},
                'cordis': {},
                'usaspending': {},
                'patents': {},
                'sec_edgar': {}
            },
            'by_type': {
                'academic_collaboration': [],
                'procurement_contracts': [],
                'research_projects': [],
                'corporate_relationships': [],
                'patents': [],
                'investments': []
            },
            'by_year': {},  # Added this key
            'statistics': {
                'total_interactions': 0,
                'countries_with_interactions': 0,
                'top_collaborators': [],
                'by_year': {}
            }
        }
    
    def process_openalex_interactions(self):
        """Process OpenAlex academic collaborations"""
        
        logging.info("Processing OpenAlex China-Europe/Eurasia interactions...")
        
        # Check OpenAlex checkpoint for existing data
        checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/processed/openalex_multicountry_temporal/processing_checkpoint.json")
        
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
                
                stats = data.get('stats', {})
                country_collabs = stats.get('country_collaborations', {})
                
                # Process each target country
                for country_code, country_name in self.all_target_countries.items():
                    if country_code in country_collabs:
                        count = country_collabs[country_code]
                        
                        if country_code not in self.interactions['by_country']:
                            self.interactions['by_country'][country_code] = {
                                'name': country_name,
                                'interactions': {}
                            }
                        
                        self.interactions['by_country'][country_code]['interactions']['openalex'] = {
                            'count': count,
                            'type': 'academic_papers'
                        }
                        
                        # Categorize
                        if country_code in self.eu_countries:
                            self.interactions['by_category']['eu_members'][country_code] = count
                        if country_code in self.bri_europe:
                            self.interactions['by_category']['bri_countries'][country_code] = count
                        if country_code in self.seventeen_plus_one:
                            self.interactions['by_category']['17_plus_1'][country_code] = count
                        if country_code in self.central_asia:
                            self.interactions['by_category']['central_asia'][country_code] = count
                        
                        self.interactions['statistics']['total_interactions'] += count
                
                # Process temporal data
                period_collabs = stats.get('period_collaborations', {})
                for period, countries in period_collabs.items():
                    year_match = re.search(r'(\d{4})', period)
                    if year_match:
                        year = year_match.group(1)
                        if year not in self.interactions['by_year']:
                            self.interactions['by_year'][year] = {}
                        
                        for country_code in countries:
                            if country_code in self.all_target_countries:
                                if country_code not in self.interactions['by_year'][year]:
                                    self.interactions['by_year'][year][country_code] = 0
                                self.interactions['by_year'][year][country_code] += countries[country_code]
        
        logging.info(f"  Found OpenAlex collaborations with {len([c for c in self.interactions['by_country'] if 'openalex' in self.interactions['by_country'][c].get('interactions', {})])} countries")
    
    def process_ted_interactions(self):
        """Process TED procurement data"""
        
        logging.info("Processing TED China-Europe procurement...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if TED data exists
            country_codes = list(self.all_target_countries.keys())
            cursor.execute("""
                SELECT buyer_country, COUNT(*) as count, SUM(contract_value) as total_value
                FROM ted_china_contracts
                WHERE buyer_country IN ({})
                GROUP BY buyer_country
            """.format(','.join(['?'] * len(country_codes))), country_codes)

            results = cursor.fetchall()
            
            for country, count, value in results:
                if country in self.all_target_countries:
                    if country not in self.interactions['by_country']:
                        self.interactions['by_country'][country] = {
                            'name': self.all_target_countries[country],
                            'interactions': {}
                        }
                    
                    self.interactions['by_country'][country]['interactions']['ted'] = {
                        'count': count,
                        'total_value': value,
                        'type': 'procurement_contracts'
                    }
                    
                    self.interactions['by_type']['procurement_contracts'].append({
                        'country': country,
                        'count': count,
                        'value': value
                    })
        
        except sqlite3.OperationalError as e:
            logging.warning(f"  TED data not yet processed: {e}")
        
        conn.close()
    
    def process_usaspending_interactions(self):
        """Process USAspending for EU/China triangular relationships"""
        
        logging.info("Processing USAspending triangular relationships...")
        
        # Look for:
        # 1. Chinese companies contracting in EU countries
        # 2. EU companies with China connections in US contracts
        # 3. Programs mentioning both China and EU countries
        
        conn = sqlite3.connect("F:/OSINT_DATA/usaspending_complete.db")
        cursor = conn.cursor()
        
        try:
            # Find contracts involving both China and EU entities
            for country_code, country_name in self.all_target_countries.items():
                cursor.execute("""
                    SELECT COUNT(*), SUM(contract_value)
                    FROM contracts
                    WHERE (vendor_country = ? OR recipient_country = ?)
                    AND (vendor_name LIKE '%china%' OR vendor_name LIKE '%chinese%'
                         OR description LIKE '%china%' OR description LIKE '%chinese%')
                """, (country_code, country_code))
                
                result = cursor.fetchone()
                if result and result[0] > 0:
                    if country_code not in self.interactions['by_country']:
                        self.interactions['by_country'][country_code] = {
                            'name': country_name,
                            'interactions': {}
                        }
                    
                    self.interactions['by_country'][country_code]['interactions']['usaspending_triangular'] = {
                        'count': result[0],
                        'value': result[1],
                        'type': 'triangular_contracts'
                    }
        
        except Exception as e:
            logging.warning(f"  USAspending processing error: {e}")
        
        conn.close()
    
    def process_cordis_interactions(self):
        """Process CORDIS EU research projects with China"""
        
        logging.info("Processing CORDIS China-EU research collaborations...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT country, COUNT(*) as project_count
                FROM cordis_china_collaborations
                GROUP BY country
            """)
            
            results = cursor.fetchall()
            
            for country, count in results:
                if country in self.all_target_countries:
                    if country not in self.interactions['by_country']:
                        self.interactions['by_country'][country] = {
                            'name': self.all_target_countries[country],
                            'interactions': {}
                        }
                    
                    self.interactions['by_country'][country]['interactions']['cordis'] = {
                        'count': count,
                        'type': 'eu_research_projects'
                    }
                    
                    self.interactions['by_type']['research_projects'].append({
                        'country': country,
                        'count': count,
                        'source': 'cordis'
                    })
        
        except sqlite3.OperationalError:
            logging.warning("  CORDIS data not yet processed")
        
        conn.close()
    
    def analyze_patterns(self):
        """Analyze patterns in China-Europe interactions"""
        
        logging.info("\nAnalyzing interaction patterns...")
        
        # Calculate statistics
        self.interactions['statistics']['countries_with_interactions'] = len(self.interactions['by_country'])
        
        # Top collaborators
        country_totals = {}
        for country_code, data in self.interactions['by_country'].items():
            total = sum(
                interaction.get('count', 0) 
                for interaction in data['interactions'].values()
            )
            country_totals[country_code] = total
        
        self.interactions['statistics']['top_collaborators'] = sorted(
            country_totals.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Identify key patterns
        patterns = {
            'bri_concentration': len([
                c for c in self.bri_europe 
                if c in self.interactions['by_country']
            ]),
            'seventeen_plus_one_active': len([
                c for c in self.seventeen_plus_one 
                if c in self.interactions['by_country']
            ]),
            'central_asia_engagement': len([
                c for c in self.central_asia.keys() 
                if c in self.interactions['by_country']
            ])
        }
        
        self.interactions['patterns'] = patterns
    
    def generate_report(self) -> str:
        """Generate comprehensive interaction report"""
        
        report = f"""
# China-Europe/Eurasia Interaction Analysis
Generated: {self.interactions['timestamp']}

## Executive Summary

**Coverage**: {self.interactions['statistics']['countries_with_interactions']} of {len(self.all_target_countries)} target countries have documented interactions with China

**Total Interactions**: {self.interactions['statistics']['total_interactions']:,}

## Top 10 Collaborating Countries

| Rank | Country | Code | Total Interactions | Categories |
|------|---------|------|--------------------|------------|
"""
        
        for i, (country_code, count) in enumerate(self.interactions['statistics']['top_collaborators'], 1):
            country_name = self.all_target_countries.get(country_code, country_code)
            
            categories = []
            if country_code in self.eu_countries:
                categories.append('EU')
            if country_code in self.bri_europe:
                categories.append('BRI')
            if country_code in self.seventeen_plus_one:
                categories.append('17+1')
            if country_code in self.central_asia:
                categories.append('Central Asia')
            
            report += f"| {i} | {country_name} | {country_code} | {count:,} | {', '.join(categories)} |\n"
        
        # Analysis by category
        report += """

## Analysis by Category

### EU Member States
"""
        eu_active = len([c for c in self.eu_countries if c in self.interactions['by_country']])
        report += f"- Active: {eu_active} of 27 member states\n"
        report += f"- Total interactions: {sum(self.interactions['by_category']['eu_members'].values()):,}\n"
        
        report += """

### Belt and Road Initiative (BRI) Countries
"""
        bri_active = self.interactions['patterns']['bri_concentration']
        report += f"- Active: {bri_active} of {len(self.bri_europe)} BRI countries in Europe/Eurasia\n"
        report += f"- Total interactions: {sum(self.interactions['by_category']['bri_countries'].values()):,}\n"
        
        report += """

### 17+1 Format (China-CEEC)
"""
        seventeen_active = self.interactions['patterns']['seventeen_plus_one_active']
        report += f"- Active: {seventeen_active} of 17 countries\n"
        report += f"- Total interactions: {sum(self.interactions['by_category']['17_plus_1'].values()):,}\n"
        
        report += """

### Central Asian Countries
"""
        ca_active = self.interactions['patterns']['central_asia_engagement']
        report += f"- Active: {ca_active} of 5 countries\n"
        report += f"- Total interactions: {sum(self.interactions['by_category']['central_asia'].values()):,}\n"
        
        # By data source
        report += """

## Interactions by Data Source

| Source | Countries | Type |
|--------|-----------|------|
"""
        
        source_counts = {
            'OpenAlex': len([c for c in self.interactions['by_country'] if 'openalex' in self.interactions['by_country'][c].get('interactions', {})]),
            'TED': len([c for c in self.interactions['by_country'] if 'ted' in self.interactions['by_country'][c].get('interactions', {})]),
            'CORDIS': len([c for c in self.interactions['by_country'] if 'cordis' in self.interactions['by_country'][c].get('interactions', {})]),
            'USAspending': len([c for c in self.interactions['by_country'] if 'usaspending_triangular' in self.interactions['by_country'][c].get('interactions', {})])
        }
        
        for source, count in source_counts.items():
            if count > 0:
                type_desc = {
                    'OpenAlex': 'Academic collaborations',
                    'TED': 'Procurement contracts',
                    'CORDIS': 'EU research projects',
                    'USAspending': 'Triangular relationships'
                }.get(source, 'Various')
                
                report += f"| {source} | {count} | {type_desc} |\n"
        
        # Key findings
        report += """

## Key Findings

1. **Geographic Distribution**: China's engagement spans across all regions of Europe and Eurasia

2. **BRI Concentration**: Strong focus on Belt and Road Initiative countries

3. **17+1 Format**: Active engagement with Central and Eastern European countries

4. **Academic vs Commercial**: Mix of academic collaboration and commercial contracts

## Countries Requiring Further Investigation

"""
        
        # Countries with no interactions found
        no_interactions = [code for code in self.all_target_countries if code not in self.interactions['by_country']]
        if no_interactions:
            report += "### No Interactions Detected (May need different data sources):\n\n"
            for code in no_interactions[:10]:  # Show first 10
                report += f"- {self.all_target_countries[code]} ({code})\n"
            
            if len(no_interactions) > 10:
                report += f"- ... and {len(no_interactions) - 10} more\n"
        
        report += """

## Data Quality Notes

- OpenAlex: Currently using sample data only (full dataset needed)
- TED: Extraction required for complete analysis
- CORDIS: Limited data available
- USAspending: Triangular relationships partially captured

## Recommendations

1. **Priority Countries for Deep Dive**:
   - Focus on top 10 collaborators
   - Investigate BRI countries with high interaction counts
   - Analyze 17+1 format countries for policy implications

2. **Data Collection Priorities**:
   - Download full OpenAlex dataset
   - Extract all TED procurement data
   - Process patent databases for technology transfer
   - Analyze investment flows through SEC EDGAR

3. **Analysis Focus Areas**:
   - Technology domains of collaboration
   - Financial values of interactions
   - Temporal trends (pre/post BRI, pre/post COVID)
   - Sector-specific penetration
"""
        
        return report
    
    def save_results(self):
        """Save interaction results"""
        
        # Save JSON
        json_path = Path("C:/Projects/OSINT - Foresight/analysis/china_europe_interactions.json")
        with open(json_path, 'w') as f:
            json.dump(self.interactions, f, indent=2)
        
        # Save report
        report = self.generate_report()
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/CHINA_EUROPE_INTERACTIONS.md")
        report_path.write_text(report)
        
        logging.info(f"\nResults saved:")
        logging.info(f"  JSON: {json_path}")
        logging.info(f"  Report: {report_path}")
    
    def run(self):
        """Run complete interaction analysis"""
        
        print("="*60)
        print("CHINA-EUROPE/EURASIA INTERACTION ANALYSIS")
        print("="*60)
        print(f"\nAnalyzing interactions with {len(self.all_target_countries)} countries...\n")
        
        # Process each data source
        self.process_openalex_interactions()
        self.process_ted_interactions()
        self.process_cordis_interactions()
        self.process_usaspending_interactions()
        
        # Analyze patterns
        self.analyze_patterns()
        
        # Save results
        self.save_results()
        
        # Print summary
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        
        print(f"\nCountries with interactions: {self.interactions['statistics']['countries_with_interactions']}")
        print(f"Total interactions found: {self.interactions['statistics']['total_interactions']:,}")
        
        print("\nTop 5 collaborators:")
        for code, count in self.interactions['statistics']['top_collaborators'][:5]:
            name = self.all_target_countries.get(code, code)
            print(f"  {name} ({code}): {count:,} interactions")
        
        return self.interactions


if __name__ == "__main__":
    processor = ChinaEuropeInteractionProcessor()
    results = processor.run()
