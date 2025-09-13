#!/usr/bin/env python3
"""
World Bank Data API Pull Script
Retrieves economic indicators and development data
Documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
import pandas as pd

class WorldBankPuller:
    """Pull economic and trade data from World Bank API"""
    
    BASE_URL = "https://api.worldbank.org/v2"
    
    # Country codes mapping
    COUNTRY_CODES = {
        'AT': 'AUT',  # Austria
        'PT': 'PRT',  # Portugal  
        'IE': 'IRL',  # Ireland
        'SK': 'SVK',  # Slovakia
        'BE': 'BEL',  # Belgium
        'BG': 'BGR',  # Bulgaria
        'HR': 'HRV',  # Croatia
        'CY': 'CYP',  # Cyprus
        'CZ': 'CZE',  # Czechia
        'DK': 'DNK',  # Denmark
        'EE': 'EST',  # Estonia
        'FI': 'FIN',  # Finland
        'FR': 'FRA',  # France
        'DE': 'DEU',  # Germany
        'GR': 'GRC',  # Greece
        'HU': 'HUN',  # Hungary
        'IT': 'ITA',  # Italy
        'LV': 'LVA',  # Latvia
        'LT': 'LTU',  # Lithuania
        'LU': 'LUX',  # Luxembourg
        'MT': 'MLT',  # Malta
        'NL': 'NLD',  # Netherlands
        'PL': 'POL',  # Poland
        'RO': 'ROU',  # Romania
        'SI': 'SVN',  # Slovenia
        'ES': 'ESP',  # Spain
        'SE': 'SWE',  # Sweden
        'GB': 'GBR',  # United Kingdom
        'NO': 'NOR',  # Norway
        'CH': 'CHE',  # Switzerland
        'TR': 'TUR',  # Turkey
        'UA': 'UKR',  # Ukraine
    }
    
    # Key economic indicators for technology assessment
    KEY_INDICATORS = {
        # Economic fundamentals
        'NY.GDP.MKTP.CD': 'GDP (current US$)',
        'NY.GDP.PCAP.CD': 'GDP per capita (current US$)',
        'NY.GDP.MKTP.KD.ZG': 'GDP growth (annual %)',
        
        # Trade indicators
        'NE.EXP.GNFS.CD': 'Exports of goods and services (current US$)',
        'NE.IMP.GNFS.CD': 'Imports of goods and services (current US$)',
        'NE.TRD.GNFS.ZS': 'Trade (% of GDP)',
        'TG.VAL.TOTL.GD.ZS': 'Merchandise trade (% of GDP)',
        
        # Technology and innovation
        'GB.XPD.RSDV.GD.ZS': 'R&D expenditure (% of GDP)',
        'IP.PAT.RESD': 'Patent applications, residents',
        'IP.PAT.NRES': 'Patent applications, nonresidents',
        'IP.TMK.TOTL': 'Trademark applications, total',
        
        # High-tech exports
        'TX.VAL.TECH.CD': 'High-technology exports (current US$)',
        'TX.VAL.TECH.MF.ZS': 'High-technology exports (% of manufactured exports)',
        
        # ICT and digital
        'IT.NET.USER.ZS': 'Individuals using the Internet (% of population)',
        'IT.NET.SECR': 'Secure Internet servers',
        'IT.NET.SECR.P6': 'Secure Internet servers (per 1 million people)',
        
        # Education and human capital
        'SE.XPD.TOTL.GD.ZS': 'Government expenditure on education (% of GDP)',
        'SE.TER.ENRR': 'School enrollment, tertiary (% gross)',
        'SL.TLF.ADVN.ZS': 'Labor force with advanced education (% of total)',
        
        # Business environment
        'IC.BUS.EASE.XQ': 'Ease of doing business score',
        'IC.REG.COST.PC.ZS': 'Cost of business start-up procedures (% of GNI per capita)',
        'IC.REG.DURS': 'Time required to start a business (days)',
        
        # Foreign investment
        'BX.KLT.DINV.CD.WD': 'Foreign direct investment, net inflows (BoP, current US$)',
        'BX.KLT.DINV.WD.GD.ZS': 'Foreign direct investment, net inflows (% of GDP)',
        
        # Infrastructure
        'IS.AIR.GOOD.MT.K1': 'Air transport, freight (million ton-km)',
        'IS.SHP.GOOD.TU': 'Container port traffic (TEU: 20 foot equivalent units)',
        'EG.ELC.ACCS.ZS': 'Access to electricity (% of population)',
    }
    
    def __init__(self, country: str, start_year: int, end_year: int, output_dir: Path):
        """Initialize World Bank puller"""
        self.country = country.upper()
        self.country_code = self.COUNTRY_CODES.get(self.country, self.country)
        self.start_year = start_year
        self.end_year = end_year
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_indicator(self, indicator_code: str, per_page: int = 1000) -> List[Dict]:
        """Get data for a specific indicator"""
        
        url = f"{self.BASE_URL}/country/{self.country_code}/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'per_page': per_page,
            'date': f'{self.start_year}:{self.end_year}'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            # World Bank API returns [page_info, data]
            if len(data) > 1 and data[1]:
                return data[1]
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {indicator_code}: {e}")
            return []
    
    def get_all_indicators(self) -> pd.DataFrame:
        """Get all key indicators for the country"""
        
        print(f"\nFetching World Bank indicators for {self.country}")
        all_data = []
        
        for code, name in self.KEY_INDICATORS.items():
            print(f"  Getting {name}...")
            data = self.get_indicator(code)
            
            for record in data:
                if record.get('value') is not None:
                    all_data.append({
                        'country': self.country,
                        'country_name': record.get('country', {}).get('value', ''),
                        'indicator_code': code,
                        'indicator_name': name,
                        'year': record.get('date'),
                        'value': record.get('value'),
                        'decimal': record.get('decimal', 2)
                    })
            
            # Be polite to the API
            time.sleep(0.5)
        
        return pd.DataFrame(all_data)
    
    def get_trade_partners(self) -> pd.DataFrame:
        """Get bilateral trade data using WITS integration"""
        
        print(f"\nFetching trade partner data via WITS integration")
        
        # World Bank WITS uses different endpoint
        wits_url = f"https://wits.worldbank.org/API/V1/SDMX/V21/rest/data"
        
        # Note: Full WITS integration requires more complex setup
        # This is a simplified version
        print("  Note: Full WITS integration requires additional setup")
        print("  See https://wits.worldbank.org/data/public/WITSAPI.pdf")
        
        return pd.DataFrame()
    
    def analyze_tech_competitiveness(self, df: pd.DataFrame) -> Dict:
        """Analyze technology competitiveness indicators"""
        
        if df.empty:
            return {}
        
        print("\n=== Technology Competitiveness Analysis ===")
        
        analysis = {}
        
        # Get latest values for key tech indicators
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]
        
        tech_indicators = [
            'GB.XPD.RSDV.GD.ZS',  # R&D expenditure
            'TX.VAL.TECH.MF.ZS',  # High-tech exports
            'IP.PAT.RESD',        # Patent applications
            'IT.NET.SECR.P6',     # Secure servers per million
        ]
        
        for indicator in tech_indicators:
            indicator_data = latest_data[latest_data['indicator_code'] == indicator]
            if not indicator_data.empty:
                value = indicator_data.iloc[0]['value']
                name = indicator_data.iloc[0]['indicator_name']
                analysis[indicator] = {
                    'name': name,
                    'value': value,
                    'year': latest_year
                }
                print(f"  {name}: {value:.2f} ({latest_year})")
        
        # Calculate trend for R&D spending
        rd_data = df[df['indicator_code'] == 'GB.XPD.RSDV.GD.ZS'].sort_values('year')
        if len(rd_data) > 1:
            first_value = rd_data.iloc[0]['value']
            last_value = rd_data.iloc[-1]['value']
            change = ((last_value - first_value) / first_value) * 100
            analysis['rd_trend'] = change
            print(f"\n  R&D spending trend: {change:+.1f}% over period")
        
        return analysis
    
    def save_results(self, df: pd.DataFrame, analysis: Dict):
        """Save results to files"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save raw data
        csv_file = self.output_dir / f"worldbank_{self.country}_{timestamp}.csv"
        df.to_csv(csv_file, index=False)
        print(f"\nSaved data to {csv_file}")
        
        # Save analysis
        analysis_file = self.output_dir / f"worldbank_analysis_{self.country}_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"Saved analysis to {analysis_file}")
        
        # Create summary report
        summary_file = self.output_dir / f"worldbank_summary_{self.country}_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(f"World Bank Data Summary for {self.country}\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(f"Period: {self.start_year} to {self.end_year}\n")
            f.write(f"Indicators collected: {df['indicator_code'].nunique()}\n")
            f.write(f"Total data points: {len(df)}\n\n")
            
            # Key metrics
            latest_year = df['year'].max()
            latest_data = df[df['year'] == latest_year]
            
            f.write(f"Latest Year Data ({latest_year}):\n")
            for _, row in latest_data.head(10).iterrows():
                f.write(f"  {row['indicator_name']}: {row['value']:.2f}\n")
        
        print(f"Saved summary to {summary_file}")
    
    def run(self):
        """Main execution method"""
        
        print(f"Starting World Bank data pull for {self.country}")
        print(f"Years: {self.start_year} to {self.end_year}")
        print(f"Output directory: {self.output_dir}")
        
        # Get all indicators
        df = self.get_all_indicators()
        
        if df.empty:
            print("No data retrieved")
            return
        
        # Analyze technology competitiveness
        analysis = self.analyze_tech_competitiveness(df)
        
        # Get trade partner data (if available)
        trade_df = self.get_trade_partners()
        
        # Save results
        self.save_results(df, analysis)
        
        print("\nWorld Bank data pull complete!")


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='Pull data from World Bank API')
    parser.add_argument('--country', required=True,
                       help='Country code (e.g., AT, DE, FR)')
    parser.add_argument('--start-year', type=int, default=2015,
                       help='Start year')
    parser.add_argument('--end-year', type=int,
                       default=datetime.now().year,
                       help='End year')
    parser.add_argument('--indicators', nargs='+',
                       help='Specific indicator codes to fetch')
    parser.add_argument('--out', default=None,
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Set output directory
    if args.out:
        output_dir = Path(args.out)
    else:
        output_dir = Path('data/raw/source=worldbank') / f'country={args.country}' / f'date={datetime.now().strftime("%Y-%m-%d")}'
    
    # Create puller and run
    puller = WorldBankPuller(
        country=args.country,
        start_year=args.start_year,
        end_year=args.end_year,
        output_dir=output_dir
    )
    
    # Override indicators if specified
    if args.indicators:
        puller.KEY_INDICATORS = {code: code for code in args.indicators}
    
    puller.run()


if __name__ == '__main__':
    main()