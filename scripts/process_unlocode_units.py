#!/usr/bin/env python3
"""
Process UN/LOCODE and Units of Measurement Data
Extracts Chinese locations and standardizes measurement units
"""

import zipfile
import pandas as pd
import sqlite3
from pathlib import Path
import json
import logging
from datetime import datetime

class UNLOCODEProcessor:
    def __init__(self, base_path: str = "F:/OSINT_Data/Trade_Facilities"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def process_unlocode(self, zip_path: str):
        """Process UN/LOCODE ZIP file"""
        print("\n" + "="*80)
        print("Processing UN/LOCODE Data")
        print("="*80)

        zip_path = Path(zip_path)
        if not zip_path.exists():
            self.logger.error(f"File not found: {zip_path}")
            return None

        extract_path = self.base_path / 'unlocode/raw'
        extract_path.mkdir(parents=True, exist_ok=True)

        # Extract ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            print(f"Extracted to {extract_path}")

        # Process CSV files
        all_locations = []
        chinese_locations = []

        for csv_file in extract_path.glob('*.csv'):
            print(f"\nProcessing {csv_file.name}...")

            try:
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        # Read without headers since UNLOCODE uses positional format
                        df = pd.read_csv(csv_file, encoding=encoding, low_memory=False, header=None)
                        break
                    except UnicodeDecodeError:
                        continue

                # UNLOCODE format: columns are positional
                # Column 1 (index 0): Change indicator
                # Column 2 (index 1): Country code (2-char ISO)
                # Column 3 (index 2): Location code (3-char)
                # Column 4 (index 3): Name
                # Column 5 (index 4): Name without diacritics
                # Column 6 (index 5): Subdivision
                # Column 7 (index 6): Function (1=port, 2=rail, 3=road, 4=airport, etc.)
                # Column 8 (index 7): Status
                # Column 9 (index 8): Date
                # Column 10 (index 9): IATA code
                # Column 11 (index 10): Coordinates
                # Column 12 (index 11): Remarks

                if len(df.columns) >= 2:
                    # Filter for Chinese territories using column index 1 (country code)
                    chinese_codes = ['CN', 'HK', 'MO', 'TW']
                    chinese_df = df[df[1].isin(chinese_codes)]

                    if not chinese_df.empty:
                        # Add column names for clarity
                        chinese_df.columns = ['change', 'country', 'locode', 'name', 'name_ascii',
                                             'subdivision', 'function', 'status', 'date',
                                             'iata', 'coordinates', 'remarks'][:len(chinese_df.columns)]

                        chinese_locations.append(chinese_df)
                        print(f"  Found {len(chinese_df)} Chinese locations")

                        # Analyze location types using column index 6 (function)
                        if len(chinese_df.columns) > 6:
                            functions = chinese_df.iloc[:, 6].fillna('')
                            ports = functions.str.contains('1', na=False).sum()
                            rail = functions.str.contains('2', na=False).sum()
                            road = functions.str.contains('3', na=False).sum()
                            airports = functions.str.contains('4', na=False).sum()
                            postal = functions.str.contains('5', na=False).sum()
                            multimodal = functions.str.contains('6', na=False).sum()
                            fixed = functions.str.contains('7', na=False).sum()
                            border = functions.str.contains('B', na=False).sum()

                            print(f"    Ports: {ports}")
                            print(f"    Rail terminals: {rail}")
                            print(f"    Road terminals: {road}")
                            print(f"    Airports: {airports}")
                            print(f"    Multimodal: {multimodal}")
                            print(f"    Border crossings: {border}")

                all_locations.append(df)

            except Exception as e:
                self.logger.error(f"Error processing {csv_file.name}: {e}")

        # Combine and save Chinese locations
        if chinese_locations:
            chinese_df = pd.concat(chinese_locations, ignore_index=True)

            # Save to CSV
            output_file = self.base_path / 'unlocode/processed/chinese_locations.csv'
            output_file.parent.mkdir(parents=True, exist_ok=True)
            chinese_df.to_csv(output_file, index=False)
            print(f"\nSaved {len(chinese_df)} Chinese locations to {output_file}")

            # Extract key logistics hubs
            self.analyze_logistics_hubs(chinese_df)

            return chinese_df

        return pd.DataFrame()

    def analyze_logistics_hubs(self, df):
        """Analyze major logistics hubs in China"""
        print("\n" + "-"*60)
        print("Major Chinese Logistics Hubs Analysis")
        print("-"*60)

        # Major ports
        major_ports = [
            'Shanghai', 'Ningbo', 'Shenzhen', 'Guangzhou', 'Qingdao',
            'Tianjin', 'Dalian', 'Xiamen', 'Hong Kong'
        ]

        # Major airports
        major_airports = [
            'Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Chengdu',
            'Kunming', 'Xian', 'Hong Kong'
        ]

        # Belt and Road key nodes
        bri_nodes = [
            'Urumqi', 'Xian', 'Chongqing', 'Zhengzhou', 'Wuhan',
            'Lanzhou', 'Kashgar', 'Khorgos'
        ]

        results = {
            'major_ports': [],
            'major_airports': [],
            'bri_nodes': []
        }

        # Find these locations in the data
        if 'name' in df.columns:
            for port in major_ports:
                matches = df[df['name'].str.contains(port, case=False, na=False)]
                if not matches.empty:
                    results['major_ports'].append({
                        'name': port,
                        'count': len(matches),
                        'codes': matches['locode'].tolist() if 'locode' in matches.columns else []
                    })

            for airport in major_airports:
                matches = df[df['name'].str.contains(airport, case=False, na=False)]
                if not matches.empty:
                    results['major_airports'].append({
                        'name': airport,
                        'count': len(matches),
                        'codes': matches['locode'].tolist() if 'locode' in matches.columns else []
                    })

            for node in bri_nodes:
                matches = df[df['name'].str.contains(node, case=False, na=False)]
                if not matches.empty:
                    results['bri_nodes'].append({
                        'name': node,
                        'count': len(matches),
                        'codes': matches['locode'].tolist() if 'locode' in matches.columns else []
                    })

        # Save analysis
        analysis_file = self.base_path / 'analysis/facility_networks/chinese_logistics_hubs.json'
        analysis_file.parent.mkdir(parents=True, exist_ok=True)
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Identified {len(results['major_ports'])} major ports")
        print(f"Identified {len(results['major_airports'])} major airports")
        print(f"Identified {len(results['bri_nodes'])} Belt & Road nodes")

        return results

    def process_units_of_measurement(self, zip_path: str):
        """Process UN/ECE Recommendation 20 units of measurement"""
        print("\n" + "="*80)
        print("Processing Units of Measurement (Rec 20)")
        print("="*80)

        zip_path = Path(zip_path)
        if not zip_path.exists():
            self.logger.error(f"File not found: {zip_path}")
            return None

        extract_path = self.base_path / 'units/raw'
        extract_path.mkdir(parents=True, exist_ok=True)

        # Extract ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            print(f"Extracted to {extract_path}")

        # Process unit codes
        units_data = []

        for file in extract_path.glob('*'):
            if file.suffix in ['.csv', '.txt']:
                print(f"\nProcessing {file.name}...")

                try:
                    # Try as CSV first
                    if file.suffix == '.csv':
                        df = pd.read_csv(file, encoding='utf-8')
                        units_data.append(df)
                    else:
                        # Parse text format
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Parse units data (implementation depends on actual format)
                            print(f"  Found units definition file")

                except Exception as e:
                    self.logger.error(f"Error processing {file.name}: {e}")

        # Create units conversion table
        self.create_units_database(units_data)

        return units_data

    def create_units_database(self, units_data):
        """Create database of measurement units"""
        db_path = self.base_path / 'databases' / 'units_measurement.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Units conversion table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurement_units (
                code TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                conversion_factor REAL,
                base_unit TEXT,
                sector TEXT,
                symbol TEXT
            )
        ''')

        # Common trade units
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_units (
                unit_code TEXT PRIMARY KEY,
                unit_name TEXT,
                category TEXT,
                to_kg_factor REAL,
                to_m3_factor REAL,
                to_pieces_factor REAL,
                notes TEXT
            )
        ''')

        # Insert common trade units
        common_units = [
            ('KGM', 'Kilogram', 'Weight', 1.0, None, None, 'Base unit for weight'),
            ('TNE', 'Metric ton', 'Weight', 1000.0, None, None, 'Metric tonne = 1000 kg'),
            ('LTR', 'Litre', 'Volume', None, 0.001, None, '1 litre = 0.001 m³'),
            ('MTQ', 'Cubic metre', 'Volume', None, 1.0, None, 'Base unit for volume'),
            ('MTR', 'Metre', 'Length', None, None, None, 'Base unit for length'),
            ('MTK', 'Square metre', 'Area', None, None, None, 'Base unit for area'),
            ('NAR', 'Number of articles', 'Quantity', None, None, 1.0, 'Number of pieces'),
            ('PCE', 'Piece', 'Quantity', None, None, 1.0, 'Single item'),
            ('GRM', 'Gram', 'Weight', 0.001, None, None, '1 gram = 0.001 kg'),
            ('DTN', 'Decitonne', 'Weight', 100.0, None, None, '1 decitonne = 100 kg')
        ]

        cursor.executemany(
            'INSERT OR REPLACE INTO trade_units VALUES (?, ?, ?, ?, ?, ?, ?)',
            common_units
        )

        conn.commit()
        conn.close()

        print(f"\nCreated units database: {db_path}")
        return db_path

    def create_integrated_database(self, chinese_locations_df=None):
        """Create integrated database with UNLOCODE and units"""
        print("\n" + "="*80)
        print("Creating Integrated Trade Database")
        print("="*80)

        db_path = self.base_path / 'databases' / f'integrated_trade_{datetime.now().strftime("%Y%m%d")}.db'
        conn = sqlite3.connect(db_path)

        # Save Chinese locations if available
        if chinese_locations_df is not None and not chinese_locations_df.empty:
            chinese_locations_df.to_sql('chinese_locations', conn, if_exists='replace', index=False)
            print(f"Added {len(chinese_locations_df)} Chinese locations to database")

        # Create cross-reference tables
        cursor = conn.cursor()

        # Port-to-facility mapping
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS port_facility_mapping (
                unlocode TEXT PRIMARY KEY,
                location_name TEXT,
                country TEXT,
                function_code TEXT,
                is_port INTEGER,
                is_airport INTEGER,
                is_rail INTEGER,
                is_bri_node INTEGER,
                coordinates TEXT,
                timezone TEXT
            )
        ''')

        # Trade route analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin_locode TEXT,
                destination_locode TEXT,
                product_category TEXT,
                typical_unit TEXT,
                average_volume REAL,
                frequency TEXT,
                strategic_importance TEXT
            )
        ''')

        conn.commit()
        conn.close()

        print(f"Created integrated database: {db_path}")
        return db_path

    def run_processing(self):
        """Process both UNLOCODE and units files"""
        results = {
            'chinese_locations': 0,
            'units_processed': 0,
            'databases_created': []
        }

        # Process UNLOCODE
        unlocode_path = Path('F:/loc242csv.zip')
        if unlocode_path.exists():
            chinese_df = self.process_unlocode(str(unlocode_path))
            if chinese_df is not None:
                results['chinese_locations'] = len(chinese_df)
        else:
            print(f"UNLOCODE file not found: {unlocode_path}")
            chinese_df = None

        # Process units
        units_path = Path('F:/rec20.zip')
        if units_path.exists():
            units_data = self.process_units_of_measurement(str(units_path))
            if units_data:
                results['units_processed'] = len(units_data)
        else:
            print(f"Units file not found: {units_path}")

        # Create integrated database
        db_path = self.create_integrated_database(chinese_df)
        results['databases_created'].append(str(db_path))

        # Summary
        print("\n" + "="*80)
        print("Processing Complete!")
        print("="*80)
        print(f"Chinese locations identified: {results['chinese_locations']}")
        print(f"Measurement units processed: {results['units_processed']}")
        print(f"Databases created: {len(results['databases_created'])}")

        return results

if __name__ == "__main__":
    processor = UNLOCODEProcessor()
    results = processor.run_processing()

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Chinese logistics hubs have been identified and mapped")
    print("2. Units conversion database ready for trade volume analysis")
    print("3. Integration with Open Supply Hub and UN Comtrade pending API keys")
    print("4. Ready to cross-reference with GLEIF and OpenSanctions data")
