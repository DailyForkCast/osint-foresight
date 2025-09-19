"""CSV Data Aggregator for Intellectual Property Exports

Aggregates and standardizes CSV exports from various trademark and patent databases
for Italian technology companies.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IPDataAggregator:
    """Aggregates intellectual property data from multiple CSV exports"""

    def __init__(self, base_path: str = "C:/Projects/OSINT - Foresight/data/collected"):
        """Initialize aggregator with base data path"""
        self.base_path = Path(base_path)
        self.trademark_path = self.base_path / "trademarks"
        self.patent_path = self.base_path / "patents"
        self.aggregated_path = self.base_path / "aggregated"

        # Create directories if they don't exist
        for path in [self.trademark_path, self.patent_path, self.aggregated_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Company name standardization mapping
        self.company_aliases = {
            'leonardo': ['leonardo spa', 'leonardo s.p.a.', 'leonardo s.p.a', 'finmeccanica', 'leonardo-finmeccanica'],
            'stmicroelectronics': ['stmicro', 'st microelectronics', 'stmicroelectronics n.v.', 'sgm-thomson'],
            'fincantieri': ['fincantieri spa', 'fincantieri s.p.a.', 'fincantieri s.p.a'],
            'telespazio': ['telespazio spa', 'telespazio s.p.a.'],
            'thales alenia': ['thales alenia space', 'thales alenia space italia', 'tas-i'],
            'ansaldo': ['ansaldo energia', 'ansaldo energia spa', 'ansaldo nucleare'],
            'datalogic': ['datalogic spa', 'datalogic s.p.a.', 'datalogic scanning'],
            'engineering': ['engineering ingegneria informatica', 'engineering spa'],
            'reply': ['reply spa', 'reply s.p.a.'],
            'prysmian': ['prysmian spa', 'prysmian group', 'prysmian s.p.a.']
        }

        # Standard column mappings for different sources
        self.column_mappings = {
            'euipo': {
                'Application number': 'application_number',
                'Trade mark name': 'mark_name',
                'Owner name': 'owner',
                'Filing date': 'filing_date',
                'Nice class': 'nice_classes',
                'Status': 'status'
            },
            'wipo': {
                'Registration Number': 'application_number',
                'Mark': 'mark_name',
                'Holder': 'owner',
                'Application Date': 'filing_date',
                'Nice Cl.': 'nice_classes',
                'Status': 'status'
            },
            'epo': {
                'Publication Number': 'publication_number',
                'Title': 'title',
                'Applicant': 'applicant',
                'Filing Date': 'filing_date',
                'IPC': 'ipc_codes',
                'Status': 'status'
            },
            'google': {
                'id': 'publication_number',
                'title': 'title',
                'assignee': 'applicant',
                'filing_date': 'filing_date',
                'classifications': 'ipc_codes',
                'legal_status': 'status'
            }
        }

    def standardize_company_name(self, name: str) -> str:
        """Standardize company name variations"""
        if pd.isna(name):
            return 'Unknown'

        name_lower = str(name).lower().strip()

        for standard, aliases in self.company_aliases.items():
            if name_lower in aliases or any(alias in name_lower for alias in aliases):
                return standard.upper()

        # If no match, return cleaned version
        return name.strip().upper()

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if pd.isna(date_str):
            return None

        date_formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y%m%d',
            '%d.%m.%Y',
            '%Y',
        ]

        for fmt in date_formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue

        # Try pandas parser as fallback
        try:
            return pd.to_datetime(date_str)
        except:
            logger.warning(f"Could not parse date: {date_str}")
            return None

    def detect_source(self, filepath: Path, df: pd.DataFrame) -> str:
        """Detect the source database based on file path and column names"""
        filepath_str = str(filepath).lower()
        columns = [col.lower() for col in df.columns]

        if 'euipo' in filepath_str or 'trade mark name' in columns:
            return 'euipo'
        elif 'wipo' in filepath_str or 'holder' in columns:
            return 'wipo'
        elif 'epo' in filepath_str or 'espacenet' in filepath_str or 'ipc' in columns:
            return 'epo'
        elif 'google' in filepath_str or 'assignee' in columns:
            return 'google'
        elif 'uibm' in filepath_str:
            return 'uibm'
        else:
            return 'unknown'

    def standardize_columns(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Standardize column names based on source"""
        if source in self.column_mappings:
            mapping = self.column_mappings[source]
            # Create reverse mapping for existing columns
            existing_cols = {col.lower(): col for col in df.columns}
            rename_dict = {}

            for orig, standard in mapping.items():
                orig_lower = orig.lower()
                if orig_lower in existing_cols:
                    rename_dict[existing_cols[orig_lower]] = standard

            if rename_dict:
                df = df.rename(columns=rename_dict)

        return df

    def aggregate_trademarks(self, output_file: str = None) -> pd.DataFrame:
        """Aggregate all trademark CSV files"""
        logger.info("Starting trademark aggregation...")

        all_trademarks = []

        # Search for CSV files in trademark subdirectories
        for subdir in self.trademark_path.iterdir():
            if subdir.is_dir():
                for csv_file in subdir.glob("*.csv"):
                    logger.info(f"Processing: {csv_file.name}")

                    try:
                        df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)

                        # Detect source and standardize
                        source = self.detect_source(csv_file, df)
                        df = self.standardize_columns(df, source)

                        # Add metadata
                        df['source_file'] = csv_file.name
                        df['source_database'] = source
                        df['import_date'] = datetime.now()

                        # Standardize company names if owner column exists
                        if 'owner' in df.columns:
                            df['owner_standardized'] = df['owner'].apply(self.standardize_company_name)

                        # Parse dates
                        if 'filing_date' in df.columns:
                            df['filing_date_parsed'] = df['filing_date'].apply(self.parse_date)
                            df['filing_year'] = df['filing_date_parsed'].dt.year

                        all_trademarks.append(df)
                        logger.info(f"  Added {len(df)} records from {source}")

                    except Exception as e:
                        logger.error(f"  Error processing {csv_file.name}: {e}")

        # Also check root trademark directory
        for csv_file in self.trademark_path.glob("*.csv"):
            if csv_file.is_file():
                try:
                    df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)
                    source = self.detect_source(csv_file, df)
                    df = self.standardize_columns(df, source)
                    df['source_file'] = csv_file.name
                    df['source_database'] = source
                    df['import_date'] = datetime.now()

                    if 'owner' in df.columns:
                        df['owner_standardized'] = df['owner'].apply(self.standardize_company_name)

                    all_trademarks.append(df)
                    logger.info(f"Added {len(df)} records from {csv_file.name}")
                except Exception as e:
                    logger.error(f"Error processing {csv_file.name}: {e}")

        if all_trademarks:
            # Combine all dataframes
            combined_df = pd.concat(all_trademarks, ignore_index=True, sort=False)

            # Remove duplicates based on key fields
            if 'application_number' in combined_df.columns:
                combined_df = combined_df.drop_duplicates(subset=['application_number'], keep='first')

            # Sort by filing date
            if 'filing_date_parsed' in combined_df.columns:
                combined_df = combined_df.sort_values('filing_date_parsed', ascending=False)

            # Save aggregated file
            if output_file:
                output_path = self.aggregated_path / output_file
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = self.aggregated_path / f"trademarks_aggregated_{timestamp}.csv"

            combined_df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Saved aggregated trademarks to: {output_path}")
            logger.info(f"Total records: {len(combined_df)}")

            return combined_df
        else:
            logger.warning("No trademark files found to aggregate")
            return pd.DataFrame()

    def aggregate_patents(self, output_file: str = None) -> pd.DataFrame:
        """Aggregate all patent CSV files"""
        logger.info("Starting patent aggregation...")

        all_patents = []

        # Search for CSV files in patent subdirectories
        for subdir in self.patent_path.iterdir():
            if subdir.is_dir():
                for csv_file in subdir.glob("*.csv"):
                    logger.info(f"Processing: {csv_file.name}")

                    try:
                        df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)

                        # Detect source and standardize
                        source = self.detect_source(csv_file, df)
                        df = self.standardize_columns(df, source)

                        # Add metadata
                        df['source_file'] = csv_file.name
                        df['source_database'] = source
                        df['import_date'] = datetime.now()

                        # Standardize company names
                        if 'applicant' in df.columns:
                            df['applicant_standardized'] = df['applicant'].apply(self.standardize_company_name)

                        # Parse dates
                        if 'filing_date' in df.columns:
                            df['filing_date_parsed'] = df['filing_date'].apply(self.parse_date)
                            df['filing_year'] = df['filing_date_parsed'].dt.year

                        all_patents.append(df)
                        logger.info(f"  Added {len(df)} records from {source}")

                    except Exception as e:
                        logger.error(f"  Error processing {csv_file.name}: {e}")

        # Check root patent directory
        for csv_file in self.patent_path.glob("*.csv"):
            if csv_file.is_file():
                try:
                    df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)
                    source = self.detect_source(csv_file, df)
                    df = self.standardize_columns(df, source)
                    df['source_file'] = csv_file.name
                    df['source_database'] = source
                    df['import_date'] = datetime.now()

                    if 'applicant' in df.columns:
                        df['applicant_standardized'] = df['applicant'].apply(self.standardize_company_name)

                    all_patents.append(df)
                    logger.info(f"Added {len(df)} records from {csv_file.name}")
                except Exception as e:
                    logger.error(f"Error processing {csv_file.name}: {e}")

        if all_patents:
            # Combine all dataframes
            combined_df = pd.concat(all_patents, ignore_index=True, sort=False)

            # Remove duplicates
            if 'publication_number' in combined_df.columns:
                combined_df = combined_df.drop_duplicates(subset=['publication_number'], keep='first')

            # Sort by filing date
            if 'filing_date_parsed' in combined_df.columns:
                combined_df = combined_df.sort_values('filing_date_parsed', ascending=False)

            # Save aggregated file
            if output_file:
                output_path = self.aggregated_path / output_file
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = self.aggregated_path / f"patents_aggregated_{timestamp}.csv"

            combined_df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Saved aggregated patents to: {output_path}")
            logger.info(f"Total records: {len(combined_df)}")

            return combined_df
        else:
            logger.warning("No patent files found to aggregate")
            return pd.DataFrame()

    def generate_summary_report(self, trademarks_df: pd.DataFrame = None,
                               patents_df: pd.DataFrame = None) -> Dict:
        """Generate summary statistics from aggregated data"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'trademarks': {},
            'patents': {}
        }

        if trademarks_df is not None and not trademarks_df.empty:
            report['trademarks'] = {
                'total_records': len(trademarks_df),
                'unique_owners': trademarks_df['owner_standardized'].nunique() if 'owner_standardized' in trademarks_df else 0,
                'date_range': {
                    'earliest': str(trademarks_df['filing_date_parsed'].min()) if 'filing_date_parsed' in trademarks_df else None,
                    'latest': str(trademarks_df['filing_date_parsed'].max()) if 'filing_date_parsed' in trademarks_df else None
                },
                'by_source': trademarks_df['source_database'].value_counts().to_dict() if 'source_database' in trademarks_df else {},
                'by_company': trademarks_df['owner_standardized'].value_counts().head(10).to_dict() if 'owner_standardized' in trademarks_df else {},
                'by_year': trademarks_df['filing_year'].value_counts().sort_index().to_dict() if 'filing_year' in trademarks_df else {}
            }

        if patents_df is not None and not patents_df.empty:
            report['patents'] = {
                'total_records': len(patents_df),
                'unique_applicants': patents_df['applicant_standardized'].nunique() if 'applicant_standardized' in patents_df else 0,
                'date_range': {
                    'earliest': str(patents_df['filing_date_parsed'].min()) if 'filing_date_parsed' in patents_df else None,
                    'latest': str(patents_df['filing_date_parsed'].max()) if 'filing_date_parsed' in patents_df else None
                },
                'by_source': patents_df['source_database'].value_counts().to_dict() if 'source_database' in patents_df else {},
                'by_company': patents_df['applicant_standardized'].value_counts().head(10).to_dict() if 'applicant_standardized' in patents_df else {},
                'by_year': patents_df['filing_year'].value_counts().sort_index().to_dict() if 'filing_year' in patents_df else {}
            }

        # Save report
        report_path = self.aggregated_path / f"aggregation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Report saved to: {report_path}")

        return report

    def run_full_aggregation(self):
        """Run complete aggregation process"""
        print("="*60)
        print("IP Data Aggregation Process")
        print("="*60)

        # Aggregate trademarks
        print("\n1. Aggregating trademark data...")
        tm_df = self.aggregate_trademarks()

        # Aggregate patents
        print("\n2. Aggregating patent data...")
        patent_df = self.aggregate_patents()

        # Generate report
        print("\n3. Generating summary report...")
        report = self.generate_summary_report(tm_df, patent_df)

        # Print summary
        print("\n" + "="*60)
        print("Aggregation Summary")
        print("="*60)

        if report['trademarks']:
            print(f"\nTrademarks:")
            print(f"  Total records: {report['trademarks'].get('total_records', 0)}")
            print(f"  Unique owners: {report['trademarks'].get('unique_owners', 0)}")
            if report['trademarks'].get('by_company'):
                print(f"\n  Top companies:")
                for company, count in list(report['trademarks']['by_company'].items())[:5]:
                    print(f"    {company}: {count}")

        if report['patents']:
            print(f"\nPatents:")
            print(f"  Total records: {report['patents'].get('total_records', 0)}")
            print(f"  Unique applicants: {report['patents'].get('unique_applicants', 0)}")
            if report['patents'].get('by_company'):
                print(f"\n  Top companies:")
                for company, count in list(report['patents']['by_company'].items())[:5]:
                    print(f"    {company}: {count}")

        print("\n" + "="*60)
        print("Aggregation complete!")
        print(f"Results saved to: {self.aggregated_path}")
        print("="*60)

        return tm_df, patent_df, report

def main():
    """Main execution function"""
    aggregator = IPDataAggregator()
    aggregator.run_full_aggregation()

if __name__ == "__main__":
    main()
