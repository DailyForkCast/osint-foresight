#!/usr/bin/env python3
"""
Eurostat API Pull Script
Retrieves EU statistics including trade, innovation, and economic data
Documentation: https://ec.europa.eu/eurostat/web/main/data/web-services
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
import pandas as pd

class EurostatPuller:
    """Pull data from Eurostat API"""
    
    # Eurostat API endpoints
    BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination"
    STATISTICS_URL = f"{BASE_URL}/statistics/1.0"
    CATALOGUE_URL = f"{BASE_URL}/catalogue/1.0"
    
    # Country codes (Eurostat uses 2-letter ISO codes)
    COUNTRY_CODES = {
        'AT': 'AT',  # Austria
        'BE': 'BE',  # Belgium
        'BG': 'BG',  # Bulgaria
        'HR': 'HR',  # Croatia
        'CY': 'CY',  # Cyprus
        'CZ': 'CZ',  # Czechia
        'DK': 'DK',  # Denmark
        'EE': 'EE',  # Estonia
        'FI': 'FI',  # Finland
        'FR': 'FR',  # France
        'DE': 'DE',  # Germany
        'GR': 'EL',  # Greece (uses EL in Eurostat)
        'HU': 'HU',  # Hungary
        'IE': 'IE',  # Ireland
        'IT': 'IT',  # Italy
        'LV': 'LV',  # Latvia
        'LT': 'LT',  # Lithuania
        'LU': 'LU',  # Luxembourg
        'MT': 'MT',  # Malta
        'NL': 'NL',  # Netherlands
        'PL': 'PL',  # Poland
        'PT': 'PT',  # Portugal
        'RO': 'RO',  # Romania
        'SK': 'SK',  # Slovakia
        'SI': 'SI',  # Slovenia
        'ES': 'ES',  # Spain
        'SE': 'SE',  # Sweden
        'GB': 'UK',  # United Kingdom (UK in Eurostat)
        'NO': 'NO',  # Norway
        'CH': 'CH',  # Switzerland
        'TR': 'TR',  # Turkey
    }
    
    # Key datasets for technology and trade analysis
    KEY_DATASETS = {
        # International trade
        'ext_go_detail': 'International trade in goods - detailed data',
        'ext_st_27_2020sitc': 'International trade by SITC',
        'DS-018995': 'EU trade since 1988 by HS2,4,6 and CN8',
        
        # High-tech trade
        'htec_trd_tot4': 'High-tech trade by high-tech group',
        'htec_trd_group4': 'High-tech exports by partner',
        
        # R&D and innovation
        'rd_e_gerdtot': 'R&D expenditure',
        'rd_p_persocc': 'R&D personnel',
        'pat_ep_rtot': 'Patent applications to EPO',
        'htec_eco_ent': 'High-tech enterprises',
        
        # Digital economy
        'isoc_ci_it_en2': 'Enterprises using cloud computing',
        'isoc_eb_ai': 'Use of artificial intelligence',
        'isoc_eb_bd': 'Big data analysis',
        'isoc_eb_iot': 'Internet of Things usage',
        
        # Supply chain indicators
        'sts_inpr_m': 'Producer prices in industry',
        'sts_inpp_m': 'Import prices',
        'road_go_ta_tott': 'Road freight transport',
        'mar_go_qm_cy': 'Maritime transport - goods',
        
        # Economic indicators
        'nama_10_gdp': 'GDP and main components',
        'nama_10_fcs': 'Final consumption aggregates',
        'ert_bil_eur_m': 'Exchange rates',
    }
    
    def __init__(self, country: str, start_year: int, end_year: int, output_dir: Path):
        """Initialize Eurostat puller"""
        self.country = country.upper()
        self.country_code = self.COUNTRY_CODES.get(self.country, self.country)
        self.start_year = start_year
        self.end_year = end_year
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_dataset_metadata(self, dataset_code: str) -> Dict:
        """Get metadata for a dataset"""
        
        url = f"{self.CATALOGUE_URL}/datasets/{dataset_code}"
        params = {'lang': 'en'}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  Error getting metadata for {dataset_code}: {e}")
            return {}
    
    def get_dataset(self, dataset_code: str, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Get data from a specific dataset"""
        
        # Build filter string
        filter_params = []
        
        # Add country filter
        filter_params.append(f"geo={self.country_code}")
        
        # Add time filter
        time_filter = []
        for year in range(self.start_year, self.end_year + 1):
            time_filter.append(str(year))
        filter_params.append(f"time={'+'.join(time_filter)}")
        
        # Add custom filters
        if filters:
            for key, value in filters.items():
                filter_params.append(f"{key}={value}")
        
        # Build URL
        url = f"{self.STATISTICS_URL}/data/{dataset_code}"
        params = {
            'format': 'JSON',
            'lang': 'en',
            'filters': '&'.join(filter_params)
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse Eurostat JSON format
            df = self.parse_eurostat_json(data)
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {dataset_code}: {e}")
            return pd.DataFrame()
    
    def parse_eurostat_json(self, data: Dict) -> pd.DataFrame:
        """Parse Eurostat JSON response into DataFrame"""
        
        if 'value' not in data or 'dimension' not in data:
            return pd.DataFrame()
        
        # Extract dimensions
        dimensions = data['dimension']
        values = data['value']
        
        # Build records
        records = []
        for idx, value in values.items():
            if value is not None:
                record = {'value': value, 'index': int(idx)}
                
                # Add dimension values
                for dim_name, dim_data in dimensions.items():
                    if 'category' in dim_data and 'index' in dim_data['category']:
                        # Find which category this index belongs to
                        for cat_id, cat_idx in dim_data['category']['index'].items():
                            if cat_idx == int(idx):
                                record[dim_name] = cat_id
                                if 'label' in dim_data['category']:
                                    record[f"{dim_name}_label"] = dim_data['category']['label'].get(cat_id, cat_id)
                
                records.append(record)
        
        return pd.DataFrame(records)
    
    def get_trade_flows(self) -> pd.DataFrame:
        """Get international trade flow data"""
        
        print(f"\nFetching trade flow data for {self.country}")
        
        # Get detailed trade data
        df = self.get_dataset('ext_go_detail', {
            'partner': 'WORLD',  # All partners
            'indicators': 'QUANTITY+VALUE',  # Both quantity and value
            'flow': 'IMPORT+EXPORT'  # Both flows
        })
        
        if df.empty:
            # Try alternative dataset
            df = self.get_dataset('DS-018995')
        
        return df
    
    def get_hightech_trade(self) -> pd.DataFrame:
        """Get high-tech trade statistics"""
        
        print(f"\nFetching high-tech trade data for {self.country}")
        
        df = self.get_dataset('htec_trd_tot4')
        
        if not df.empty:
            # Calculate high-tech trade balance
            exports = df[df.get('flow', '') == 'EXPORT']['value'].sum()
            imports = df[df.get('flow', '') == 'IMPORT']['value'].sum()
            
            print(f"  High-tech exports: €{exports:,.0f}M")
            print(f"  High-tech imports: €{imports:,.0f}M")
            print(f"  Balance: €{exports-imports:+,.0f}M")
        
        return df
    
    def get_innovation_indicators(self) -> pd.DataFrame:
        """Get R&D and innovation indicators"""
        
        print(f"\nFetching innovation indicators for {self.country}")
        
        all_data = []
        
        # R&D expenditure
        rd_df = self.get_dataset('rd_e_gerdtot', {'sectperf': 'TOTAL'})
        if not rd_df.empty:
            rd_df['indicator'] = 'R&D Expenditure'
            all_data.append(rd_df)
        
        # Patent applications
        pat_df = self.get_dataset('pat_ep_rtot')
        if not pat_df.empty:
            pat_df['indicator'] = 'EPO Patents'
            all_data.append(pat_df)
        
        # High-tech enterprises
        ht_df = self.get_dataset('htec_eco_ent')
        if not ht_df.empty:
            ht_df['indicator'] = 'High-tech Enterprises'
            all_data.append(ht_df)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        
        return pd.DataFrame()
    
    def get_digital_economy(self) -> pd.DataFrame:
        """Get digital economy indicators"""
        
        print(f"\nFetching digital economy indicators for {self.country}")
        
        all_data = []
        
        # Cloud computing
        cloud_df = self.get_dataset('isoc_ci_it_en2')
        if not cloud_df.empty:
            cloud_df['technology'] = 'Cloud Computing'
            all_data.append(cloud_df)
        
        # AI usage
        ai_df = self.get_dataset('isoc_eb_ai')
        if not ai_df.empty:
            ai_df['technology'] = 'Artificial Intelligence'
            all_data.append(ai_df)
        
        # Big data
        bd_df = self.get_dataset('isoc_eb_bd')
        if not bd_df.empty:
            bd_df['technology'] = 'Big Data'
            all_data.append(bd_df)
        
        # IoT
        iot_df = self.get_dataset('isoc_eb_iot')
        if not iot_df.empty:
            iot_df['technology'] = 'Internet of Things'
            all_data.append(iot_df)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        
        return pd.DataFrame()
    
    def save_results(self, 
                    trade_df: pd.DataFrame,
                    hightech_df: pd.DataFrame,
                    innovation_df: pd.DataFrame,
                    digital_df: pd.DataFrame):
        """Save all results to files"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save each dataset
        datasets = {
            'trade': trade_df,
            'hightech': hightech_df,
            'innovation': innovation_df,
            'digital': digital_df
        }
        
        for name, df in datasets.items():
            if not df.empty:
                file_path = self.output_dir / f"eurostat_{name}_{self.country}_{timestamp}.csv"
                df.to_csv(file_path, index=False)
                print(f"Saved {name} data to {file_path}")
        
        # Create summary report
        summary_file = self.output_dir / f"eurostat_summary_{self.country}_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Eurostat Data Summary for {self.country}\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(f"Period: {self.start_year} to {self.end_year}\n\n")
            
            f.write("Data collected:\n")
            for name, df in datasets.items():
                if not df.empty:
                    f.write(f"  {name}: {len(df)} records\n")
            
            # Key findings
            f.write("\nKey Findings:\n")
            
            if not innovation_df.empty:
                latest_rd = innovation_df[innovation_df['indicator'] == 'R&D Expenditure']
                if not latest_rd.empty:
                    f.write(f"  R&D Expenditure: {latest_rd.iloc[-1]['value']:.2f}\n")
            
            if not digital_df.empty:
                for tech in digital_df['technology'].unique():
                    tech_data = digital_df[digital_df['technology'] == tech]
                    if not tech_data.empty:
                        f.write(f"  {tech} adoption: {tech_data.iloc[-1]['value']:.1f}%\n")
        
        print(f"Saved summary to {summary_file}")
    
    def run(self):
        """Main execution method"""
        
        print(f"Starting Eurostat data pull for {self.country}")
        print(f"Years: {self.start_year} to {self.end_year}")
        print(f"Output directory: {self.output_dir}")
        
        # Get different data categories
        trade_df = self.get_trade_flows()
        hightech_df = self.get_hightech_trade()
        innovation_df = self.get_innovation_indicators()
        digital_df = self.get_digital_economy()
        
        # Save results
        self.save_results(trade_df, hightech_df, innovation_df, digital_df)
        
        print("\nEurostat data pull complete!")


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='Pull data from Eurostat API')
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
        output_dir = Path('data/raw/source=eurostat') / f'country={args.country}' / f'date={datetime.now().strftime("%Y-%m-%d")}'
    
    # Create puller and run
    puller = EurostatPuller(
        country=args.country,
        start_year=args.start_year,
        end_year=args.end_year,
        output_dir=output_dir
    )
    
    # Override datasets if specified
    if args.datasets:
        puller.KEY_DATASETS = {code: code for code in args.datasets}
    
    puller.run()


if __name__ == '__main__':
    main()