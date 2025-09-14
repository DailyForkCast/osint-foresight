#!/usr/bin/env python3
"""
OECD Data API Pull Script
Retrieves economic, trade, and innovation data from OECD
Documentation: https://data.oecd.org/api/
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
import pandas as pd
import xml.etree.ElementTree as ET

class OECDPuller:
    """Pull data from OECD API"""

    # OECD API endpoint
    BASE_URL = "https://stats.oecd.org/SDMX-JSON/data"

    # Country codes (OECD uses 3-letter ISO codes)
    COUNTRY_CODES = {
        'AT': 'AUT',  # Austria
        'BE': 'BEL',  # Belgium
        'CZ': 'CZE',  # Czechia
        'DK': 'DNK',  # Denmark
        'EE': 'EST',  # Estonia
        'FI': 'FIN',  # Finland
        'FR': 'FRA',  # France
        'DE': 'DEU',  # Germany
        'GR': 'GRC',  # Greece
        'HU': 'HUN',  # Hungary
        'IE': 'IRL',  # Ireland
        'IT': 'ITA',  # Italy
        'LV': 'LVA',  # Latvia
        'LT': 'LTU',  # Lithuania
        'LU': 'LUX',  # Luxembourg
        'NL': 'NLD',  # Netherlands
        'PL': 'POL',  # Poland
        'PT': 'PRT',  # Portugal
        'SK': 'SVK',  # Slovakia
        'SI': 'SVN',  # Slovenia
        'ES': 'ESP',  # Spain
        'SE': 'SWE',  # Sweden
        'GB': 'GBR',  # United Kingdom
        'NO': 'NOR',  # Norway
        'CH': 'CHE',  # Switzerland
        'TR': 'TUR',  # Turkey
        'US': 'USA',  # United States (for comparison)
        'JP': 'JPN',  # Japan (for comparison)
        'KR': 'KOR',  # Korea (for comparison)
        'CN': 'CHN',  # China (for comparison)
    }

    # Key datasets for technology and economic analysis
    KEY_DATASETS = {
        # Science, Technology and Innovation
        'MSTI_PUB': {
            'name': 'Main Science and Technology Indicators',
            'measures': ['GERD', 'BERD', 'GOVERD', 'HERD'],  # R&D expenditure by sector
            'description': 'R&D expenditure and personnel'
        },

        'PATS_IPC': {
            'name': 'Patents by technology',
            'measures': ['TOTAL', 'ICT', 'BIOTECH', 'NANOTECH'],
            'description': 'Patent applications by technology field'
        },

        # Trade and Supply Chains
        'TiVA_2021': {
            'name': 'Trade in Value Added',
            'measures': ['EXGR', 'IMGR', 'DEXFVASH', 'FFD_DVA'],
            'description': 'Global value chains and trade in value added'
        },

        'BTDIXE': {
            'name': 'Bilateral Trade by Industry and End-use',
            'measures': ['TOTAL', 'INTERM', 'CONSUM', 'CAPITAL'],
            'description': 'Detailed bilateral trade flows'
        },

        # Digital Economy
        'ICT_BUS': {
            'name': 'ICT usage by businesses',
            'measures': ['E_COMMERCE', 'CLOUD', 'BIG_DATA', 'AI'],
            'description': 'Digital technology adoption by enterprises'
        },

        'BROADBAND_DB': {
            'name': 'Broadband statistics',
            'measures': ['TOTAL', 'FIBRE', 'SPEED'],
            'description': 'Broadband penetration and quality'
        },

        # Economic Indicators
        'QNA': {
            'name': 'Quarterly National Accounts',
            'measures': ['GDP', 'GDPV', 'CPI', 'PPI'],
            'description': 'GDP and price indices'
        },

        'FDI_FLOW': {
            'name': 'Foreign Direct Investment',
            'measures': ['IN', 'OUT', 'IN_STOCK', 'OUT_STOCK'],
            'description': 'FDI flows and stocks'
        },

        # Education and Skills
        'EAG_NEAC': {
            'name': 'Education at a Glance',
            'measures': ['TERTIARY', 'STEM', 'PHD'],
            'description': 'Educational attainment and STEM graduates'
        },

        # Environment and Sustainability
        'GREEN_GROWTH': {
            'name': 'Green Growth Indicators',
            'measures': ['CO2_PROD', 'RENEWABLE', 'GREEN_TECH'],
            'description': 'Environmental technology and green innovation'
        }
    }

    def __init__(self, country: str, start_year: int, end_year: int, output_dir: Path):
        """Initialize OECD puller"""
        self.country = country.upper()
        self.country_code = self.COUNTRY_CODES.get(self.country, self.country)
        self.start_year = start_year
        self.end_year = end_year
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_dataset(self, dataset_code: str, filter_expr: str = None) -> pd.DataFrame:
        """Get data from a specific OECD dataset"""

        # Build filter expression if not provided
        if not filter_expr:
            filter_expr = f"{self.country_code}/all"

        # Build URL
        url = f"{self.BASE_URL}/{dataset_code}/{filter_expr}/all"

        params = {
            'startTime': self.start_year,
            'endTime': self.end_year,
            'dimensionAtObservation': 'allDimensions'
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Parse OECD JSON-stat format
            df = self.parse_oecd_json(data, dataset_code)
            return df

        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {dataset_code}: {e}")
            return pd.DataFrame()

    def parse_oecd_json(self, data: Dict, dataset_code: str) -> pd.DataFrame:
        """Parse OECD JSON-stat response into DataFrame"""

        if 'dataSets' not in data or not data['dataSets']:
            return pd.DataFrame()

        dataset = data['dataSets'][0]

        if 'observations' not in dataset:
            return pd.DataFrame()

        # Get dimension information
        structure = data.get('structure', {})
        dimensions = structure.get('dimensions', {}).get('observation', [])

        # Build records from observations
        records = []
        for obs_key, obs_value in dataset['observations'].items():
            if obs_value and obs_value[0] is not None:  # obs_value is [value, status]
                record = {
                    'value': obs_value[0],
                    'dataset': dataset_code
                }

                # Parse observation key to get dimension values
                key_parts = obs_key.split(':')
                for i, dim in enumerate(dimensions):
                    if i < len(key_parts):
                        dim_idx = int(key_parts[i])
                        if 'values' in dim and dim_idx < len(dim['values']):
                            dim_value = dim['values'][dim_idx]
                            record[dim['id']] = dim_value.get('id', dim_value.get('name', ''))

                            # Add labels if available
                            if 'name' in dim_value:
                                record[f"{dim['id']}_label"] = dim_value['name']

                records.append(record)

        return pd.DataFrame(records)

    def get_rd_indicators(self) -> pd.DataFrame:
        """Get R&D and innovation indicators"""

        print(f"\nFetching R&D indicators for {self.country}")

        # Main Science and Technology Indicators
        df = self.get_dataset('MSTI_PUB', f"{self.country_code}")

        if not df.empty:
            # Extract key metrics
            gerd = df[df.get('VARIABLE', '') == 'GERD']  # Gross R&D expenditure
            if not gerd.empty:
                latest_gerd = gerd.iloc[-1]['value']
                print(f"  R&D expenditure (% GDP): {latest_gerd:.2f}")

            berd = df[df.get('VARIABLE', '') == 'BERD']  # Business R&D
            if not berd.empty:
                latest_berd = berd.iloc[-1]['value']
                print(f"  Business R&D (% GDP): {latest_berd:.2f}")

        return df

    def get_trade_value_added(self) -> pd.DataFrame:
        """Get Trade in Value Added (TiVA) data"""

        print(f"\nFetching Trade in Value Added data for {self.country}")

        # TiVA database for global value chains
        df = self.get_dataset('TiVA_2021', f"{self.country_code}")

        if not df.empty:
            # Analyze participation in global value chains
            gvc_participation = df[df.get('INDICATOR', '') == 'EXGR_FVA']
            if not gvc_participation.empty:
                latest_gvc = gvc_participation.iloc[-1]['value']
                print(f"  GVC participation index: {latest_gvc:.2f}")

        return df

    def get_digital_indicators(self) -> pd.DataFrame:
        """Get digital economy indicators"""

        print(f"\nFetching digital economy indicators for {self.country}")

        all_data = []

        # ICT usage by businesses
        ict_df = self.get_dataset('ICT_BUS', f"{self.country_code}")
        if not ict_df.empty:
            ict_df['category'] = 'ICT Business Usage'
            all_data.append(ict_df)

        # Broadband statistics
        bb_df = self.get_dataset('BROADBAND_DB', f"{self.country_code}")
        if not bb_df.empty:
            bb_df['category'] = 'Broadband'
            all_data.append(bb_df)

        if all_data:
            return pd.concat(all_data, ignore_index=True)

        return pd.DataFrame()

    def get_fdi_flows(self) -> pd.DataFrame:
        """Get Foreign Direct Investment data"""

        print(f"\nFetching FDI data for {self.country}")

        df = self.get_dataset('FDI_FLOW', f"{self.country_code}")

        if not df.empty:
            # Calculate FDI balance
            inflows = df[df.get('MEASURE', '') == 'INFLOWS']
            outflows = df[df.get('MEASURE', '') == 'OUTFLOWS']

            if not inflows.empty and not outflows.empty:
                latest_in = inflows.iloc[-1]['value']
                latest_out = outflows.iloc[-1]['value']
                print(f"  FDI inflows: ${latest_in:.2f}B")
                print(f"  FDI outflows: ${latest_out:.2f}B")
                print(f"  Net FDI: ${latest_in - latest_out:+.2f}B")

        return df

    def get_green_tech(self) -> pd.DataFrame:
        """Get green technology and sustainability indicators"""

        print(f"\nFetching green technology indicators for {self.country}")

        df = self.get_dataset('GREEN_GROWTH', f"{self.country_code}")

        if not df.empty:
            # Green patents
            green_patents = df[df.get('INDICATOR', '').str.contains('PATENT', na=False)]
            if not green_patents.empty:
                latest_patents = green_patents.iloc[-1]['value']
                print(f"  Green technology patents: {latest_patents:.0f}")

        return df

    def analyze_competitiveness(self, all_data: Dict[str, pd.DataFrame]) -> Dict:
        """Analyze overall competitiveness from multiple indicators"""

        print("\n=== Competitiveness Analysis ===")

        analysis = {
            'country': self.country,
            'period': f"{self.start_year}-{self.end_year}",
            'indicators': {}
        }

        # R&D intensity
        if 'rd' in all_data and not all_data['rd'].empty:
            rd_df = all_data['rd']
            gerd = rd_df[rd_df.get('VARIABLE', '') == 'GERD']
            if not gerd.empty:
                analysis['indicators']['rd_intensity'] = gerd.iloc[-1]['value']

        # Digital adoption
        if 'digital' in all_data and not all_data['digital'].empty:
            digital_df = all_data['digital']
            cloud = digital_df[digital_df.get('VARIABLE', '').str.contains('CLOUD', na=False)]
            if not cloud.empty:
                analysis['indicators']['cloud_adoption'] = cloud.iloc[-1]['value']

        # Trade integration
        if 'tiva' in all_data and not all_data['tiva'].empty:
            tiva_df = all_data['tiva']
            gvc = tiva_df[tiva_df.get('INDICATOR', '') == 'EXGR_FVA']
            if not gvc.empty:
                analysis['indicators']['gvc_participation'] = gvc.iloc[-1]['value']

        # Green innovation
        if 'green' in all_data and not all_data['green'].empty:
            green_df = all_data['green']
            patents = green_df[green_df.get('INDICATOR', '').str.contains('PATENT', na=False)]
            if not patents.empty:
                analysis['indicators']['green_patents'] = patents.iloc[-1]['value']

        # Print summary
        for indicator, value in analysis['indicators'].items():
            print(f"  {indicator}: {value:.2f}")

        return analysis

    def save_results(self, all_data: Dict[str, pd.DataFrame], analysis: Dict):
        """Save all results to files"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save each dataset
        for name, df in all_data.items():
            if not df.empty:
                file_path = self.output_dir / f"oecd_{name}_{self.country}_{timestamp}.csv"
                df.to_csv(file_path, index=False)
                print(f"\nSaved {name} data to {file_path}")

        # Save analysis
        analysis_file = self.output_dir / f"oecd_analysis_{self.country}_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"Saved analysis to {analysis_file}")

        # Create summary report
        summary_file = self.output_dir / f"oecd_summary_{self.country}_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(f"OECD Data Summary for {self.country}\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(f"Period: {self.start_year} to {self.end_year}\n\n")

            f.write("Datasets collected:\n")
            for name, df in all_data.items():
                if not df.empty:
                    f.write(f"  {name}: {len(df)} records\n")

            f.write("\nKey Competitiveness Indicators:\n")
            for indicator, value in analysis['indicators'].items():
                f.write(f"  {indicator}: {value:.2f}\n")

        print(f"Saved summary to {summary_file}")

    def run(self):
        """Main execution method"""

        print(f"Starting OECD data pull for {self.country}")
        print(f"Years: {self.start_year} to {self.end_year}")
        print(f"Output directory: {self.output_dir}")

        # Collect all data
        all_data = {
            'rd': self.get_rd_indicators(),
            'tiva': self.get_trade_value_added(),
            'digital': self.get_digital_indicators(),
            'fdi': self.get_fdi_flows(),
            'green': self.get_green_tech()
        }

        # Analyze competitiveness
        analysis = self.analyze_competitiveness(all_data)

        # Save results
        self.save_results(all_data, analysis)

        print("\nOECD data pull complete!")


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(description='Pull data from OECD API')
    parser.add_argument('--country', required=True,
                       help='Country code (e.g., AT, DE, FR)')
    parser.add_argument('--start-year', type=int, default=2015,
                       help='Start year')
    parser.add_argument('--end-year', type=int,
                       default=datetime.now().year,
                       help='End year')
    parser.add_argument('--datasets', nargs='+',
                       help='Specific dataset codes to fetch')
    parser.add_argument('--out', default=None,
                       help='Output directory')

    args = parser.parse_args()

    # Set output directory
    if args.out:
        output_dir = Path(args.out)
    else:
        output_dir = Path('data/raw/source=oecd') / f'country={args.country}' / f'date={datetime.now().strftime("%Y-%m-%d")}'

    # Create puller and run
    puller = OECDPuller(
        country=args.country,
        start_year=args.start_year,
        end_year=args.end_year,
        output_dir=output_dir
    )

    puller.run()


if __name__ == '__main__':
    main()
