#!/usr/bin/env python3
"""
UN Comtrade API Pull Script
Retrieves international trade flow data from UN Comtrade
Documentation: https://comtradeapi.un.org/
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
import pandas as pd

class ComtradePuller:
    """Pull trade data from UN Comtrade API"""
    
    BASE_URL = "https://comtrade.un.org/api"
    
    # Country codes for our target countries
    COUNTRY_CODES = {
        'AT': '040',  # Austria
        'PT': '620',  # Portugal
        'IE': '372',  # Ireland
        'SK': '703',  # Slovakia
    }
    
    # Critical technology-related HS codes (2-digit chapters)
    TECH_HS_CODES = {
        '84': 'Nuclear reactors, machinery, computers',
        '85': 'Electrical machinery, electronics',
        '90': 'Optical, medical, scientific instruments',
        '28': 'Inorganic chemicals, rare earth elements',
        '29': 'Organic chemicals',
        '38': 'Chemical products',
        '39': 'Plastics and articles',
        '72': 'Iron and steel',
        '73': 'Articles of iron or steel',
        '74': 'Copper and articles',
        '76': 'Aluminum and articles',
        '81': 'Other base metals (tungsten, molybdenum, tantalum)',
        '87': 'Vehicles and parts',
        '88': 'Aircraft and spacecraft',
        '89': 'Ships and boats',
    }
    
    # Supply chain critical products (6-digit HS codes)
    CRITICAL_PRODUCTS = {
        '854140': 'Photosensitive semiconductor devices, solar cells',
        '854231': 'Electronic integrated circuits - processors',
        '854232': 'Electronic integrated circuits - memories',
        '854233': 'Electronic integrated circuits - amplifiers',
        '850300': 'Electric motor parts',
        '850440': 'Static converters',
        '850680': 'Lithium batteries',
        '284410': 'Uranium natural',
        '280461': 'Silicon >99.99% pure',
        '281820': 'Aluminum oxide',
        '8112': 'Beryllium, chromium, germanium, vanadium, gallium, hafnium',
    }
    
    def __init__(self, country: str, start_year: int, end_year: int, output_dir: Path):
        """Initialize Comtrade puller"""
        self.country = country.upper()
        self.country_code = self.COUNTRY_CODES.get(self.country)
        if not self.country_code:
            raise ValueError(f"Country {self.country} not supported")
        
        self.start_year = start_year
        self.end_year = end_year
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting (100 requests per hour for free tier)
        self.request_delay = 36  # seconds between requests (100/hour)
        self.last_request = 0
        
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request
        if elapsed < self.request_delay:
            wait_time = self.request_delay - elapsed
            print(f"  Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        self.last_request = time.time()
        
    def get_trade_flow(self, 
                      flow_type: str = 'M',  # M=imports, X=exports
                      partner: str = '0',     # 0=World, or specific country
                      commodity: str = 'TOTAL', # HS code or TOTAL
                      year: Optional[int] = None) -> Optional[Dict]:
        """Get trade flow data"""
        
        self._rate_limit()
        
        # Build parameters for legacy API
        flow_map = {'M': '1', 'X': '2'}  # 1=imports, 2=exports
        
        params = {
            'type': 'C',  # Commodities
            'freq': 'A',  # Annual
            'px': 'HS',   # Harmonized System
            'ps': year or self.end_year,
            'r': self.country_code,
            'cc': commodity if commodity != 'TOTAL' else 'AG0',
            'rg': flow_map.get(flow_type, '1'),
            'p': partner,
            'fmt': 'json',
            'max': 10000  # Max records
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/get",
                params=params,
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'dataset' in data:
                return data['dataset']
            else:
                print(f"  No data returned for {params}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching data: {e}")
            return None
    
    def analyze_supply_chain_dependencies(self) -> pd.DataFrame:
        """Analyze supply chain dependencies for critical products"""
        
        print(f"\nAnalyzing supply chain dependencies for {self.country}")
        results = []
        
        # Check imports of critical products
        for hs_code, description in self.CRITICAL_PRODUCTS.items():
            print(f"  Checking {hs_code}: {description}")
            
            # Get import data
            import_data = self.get_trade_flow(
                flow_type='M',
                commodity=hs_code,
                year=self.end_year
            )
            
            if import_data:
                for record in import_data:
                    results.append({
                        'country': self.country,
                        'year': self.end_year,
                        'flow': 'Import',
                        'hs_code': hs_code,
                        'product': description,
                        'partner': record.get('ptTitle', ''),
                        'partner_code': record.get('ptCode', ''),
                        'trade_value': record.get('TradeValue', 0),
                        'quantity': record.get('NetWeight', 0),
                        'unit': record.get('qtDesc', '')
                    })
        
        if results:
            df = pd.DataFrame(results)
            
            # Calculate concentration metrics
            print("\n=== Supply Concentration Analysis ===")
            for hs_code in df['hs_code'].unique():
                product_df = df[df['hs_code'] == hs_code]
                total_value = product_df['trade_value'].sum()
                
                if total_value > 0:
                    # Top suppliers
                    top_suppliers = product_df.groupby('partner')['trade_value'].sum()
                    top_suppliers = top_suppliers.sort_values(ascending=False).head(3)
                    
                    print(f"\n{self.CRITICAL_PRODUCTS[hs_code]}:")
                    print(f"  Total import value: ${total_value:,.0f}")
                    print("  Top suppliers:")
                    for partner, value in top_suppliers.items():
                        share = (value / total_value) * 100
                        print(f"    {partner}: ${value:,.0f} ({share:.1f}%)")
            
            return df
        
        return pd.DataFrame()
    
    def get_trade_balance(self) -> pd.DataFrame:
        """Get overall trade balance by year"""
        
        print(f"\nGetting trade balance for {self.country}")
        results = []
        
        for year in range(self.start_year, self.end_year + 1):
            print(f"  Year {year}...")
            
            # Get total imports
            import_data = self.get_trade_flow(
                flow_type='M',
                commodity='TOTAL',
                year=year
            )
            
            # Get total exports
            export_data = self.get_trade_flow(
                flow_type='X',
                commodity='TOTAL',
                year=year
            )
            
            if import_data and export_data:
                total_imports = sum(r.get('TradeValue', 0) for r in import_data)
                total_exports = sum(r.get('TradeValue', 0) for r in export_data)
                
                results.append({
                    'country': self.country,
                    'year': year,
                    'total_imports': total_imports,
                    'total_exports': total_exports,
                    'trade_balance': total_exports - total_imports
                })
        
        return pd.DataFrame(results)
    
    def get_tech_trade_flows(self) -> pd.DataFrame:
        """Get trade flows for technology products"""
        
        print(f"\nGetting technology trade flows for {self.country}")
        results = []
        
        # Focus on most recent year for detailed analysis
        year = self.end_year
        
        for hs_code, description in list(self.TECH_HS_CODES.items())[:5]:  # Limit due to rate limiting
            print(f"  Checking HS {hs_code}: {description}")
            
            # Get imports
            import_data = self.get_trade_flow(
                flow_type='M',
                commodity=hs_code,
                year=year
            )
            
            # Get exports
            export_data = self.get_trade_flow(
                flow_type='X',
                commodity=hs_code,
                year=year
            )
            
            if import_data:
                for record in import_data:
                    results.append({
                        'country': self.country,
                        'year': year,
                        'flow': 'Import',
                        'hs_chapter': hs_code,
                        'category': description,
                        'partner': record.get('ptTitle', ''),
                        'trade_value': record.get('TradeValue', 0)
                    })
            
            if export_data:
                for record in export_data:
                    results.append({
                        'country': self.country,
                        'year': year,
                        'flow': 'Export',
                        'hs_chapter': hs_code,
                        'category': description,
                        'partner': record.get('ptTitle', ''),
                        'trade_value': record.get('TradeValue', 0)
                    })
        
        return pd.DataFrame(results)
    
    def analyze_china_dependency(self) -> pd.DataFrame:
        """Analyze trade dependency on China"""
        
        print(f"\nAnalyzing China trade dependency for {self.country}")
        
        # China's country code
        china_code = '156'
        
        results = []
        
        # Check key technology imports from China
        for hs_code, description in list(self.TECH_HS_CODES.items())[:5]:
            print(f"  Checking imports from China - HS {hs_code}")
            
            data = self.get_trade_flow(
                flow_type='M',
                partner=china_code,
                commodity=hs_code,
                year=self.end_year
            )
            
            if data:
                for record in data:
                    results.append({
                        'country': self.country,
                        'year': self.end_year,
                        'hs_chapter': hs_code,
                        'category': description,
                        'import_value_from_china': record.get('TradeValue', 0),
                        'quantity': record.get('NetWeight', 0)
                    })
        
        if results:
            df = pd.DataFrame(results)
            total_china_imports = df['import_value_from_china'].sum()
            
            print(f"\n=== China Dependency Summary ===")
            print(f"Total tech imports from China: ${total_china_imports:,.0f}")
            print("\nTop categories:")
            top_cats = df.groupby('category')['import_value_from_china'].sum()
            top_cats = top_cats.sort_values(ascending=False)
            for cat, value in top_cats.items():
                print(f"  {cat}: ${value:,.0f}")
            
            return df
        
        return pd.DataFrame()
    
    def save_results(self, 
                    supply_chain_df: pd.DataFrame,
                    trade_balance_df: pd.DataFrame,
                    tech_flows_df: pd.DataFrame,
                    china_df: pd.DataFrame):
        """Save all results to files"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save supply chain dependencies
        if not supply_chain_df.empty:
            file_path = self.output_dir / f"comtrade_supply_chain_{self.country}_{timestamp}.csv"
            supply_chain_df.to_csv(file_path, index=False)
            print(f"\nSaved supply chain data to {file_path}")
        
        # Save trade balance
        if not trade_balance_df.empty:
            file_path = self.output_dir / f"comtrade_trade_balance_{self.country}_{timestamp}.csv"
            trade_balance_df.to_csv(file_path, index=False)
            print(f"Saved trade balance to {file_path}")
        
        # Save tech flows
        if not tech_flows_df.empty:
            file_path = self.output_dir / f"comtrade_tech_flows_{self.country}_{timestamp}.csv"
            tech_flows_df.to_csv(file_path, index=False)
            print(f"Saved tech flows to {file_path}")
        
        # Save China dependency
        if not china_df.empty:
            file_path = self.output_dir / f"comtrade_china_dependency_{self.country}_{timestamp}.csv"
            china_df.to_csv(file_path, index=False)
            print(f"Saved China dependency analysis to {file_path}")
        
        # Create summary report
        summary_file = self.output_dir / f"comtrade_summary_{self.country}_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write(f"UN Comtrade Analysis Summary for {self.country}\n")
            f.write(f"{'=' * 50}\n\n")
            
            if not trade_balance_df.empty:
                latest = trade_balance_df.iloc[-1]
                f.write(f"Trade Balance ({latest['year']}):\n")
                f.write(f"  Imports: ${latest['total_imports']:,.0f}\n")
                f.write(f"  Exports: ${latest['total_exports']:,.0f}\n")
                f.write(f"  Balance: ${latest['trade_balance']:,.0f}\n\n")
            
            if not china_df.empty:
                total_china = china_df['import_value_from_china'].sum()
                f.write(f"China Dependency:\n")
                f.write(f"  Total tech imports from China: ${total_china:,.0f}\n\n")
            
            if not supply_chain_df.empty:
                f.write(f"Critical Products Monitored: {supply_chain_df['hs_code'].nunique()}\n")
                f.write(f"Supply Partners: {supply_chain_df['partner'].nunique()}\n")
        
        print(f"Saved summary to {summary_file}")
    
    def run(self):
        """Main execution method"""
        
        print(f"Starting UN Comtrade data pull for {self.country}")
        print(f"Years: {self.start_year} to {self.end_year}")
        print(f"Output directory: {self.output_dir}")
        print(f"Note: Rate limited to 100 requests/hour on free tier")
        
        # Get trade balance over time
        trade_balance_df = self.get_trade_balance()
        
        # Analyze supply chain dependencies
        supply_chain_df = self.analyze_supply_chain_dependencies()
        
        # Get technology trade flows
        tech_flows_df = self.get_tech_trade_flows()
        
        # Analyze China dependency
        china_df = self.analyze_china_dependency()
        
        # Save all results
        self.save_results(
            supply_chain_df,
            trade_balance_df,
            tech_flows_df,
            china_df
        )
        
        print("\nUN Comtrade data pull complete!")


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='Pull trade data from UN Comtrade')
    parser.add_argument('--country', required=True, 
                       choices=['AT', 'PT', 'IE', 'SK'],
                       help='Country code (AT, PT, IE, SK)')
    parser.add_argument('--start-year', type=int, default=2020,
                       help='Start year')
    parser.add_argument('--end-year', type=int, 
                       default=datetime.now().year,
                       help='End year')
    parser.add_argument('--out', default=None,
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Set output directory
    if args.out:
        output_dir = Path(args.out)
    else:
        output_dir = Path('data/raw/source=comtrade') / f'country={args.country}' / f'date={datetime.now().strftime("%Y-%m-%d")}'
    
    # Create puller and run
    puller = ComtradePuller(
        country=args.country,
        start_year=args.start_year,
        end_year=args.end_year,
        output_dir=output_dir
    )
    
    puller.run()


if __name__ == '__main__':
    main()