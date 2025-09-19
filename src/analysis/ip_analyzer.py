"""Intellectual Property Data Analysis Tools

Analyzes aggregated trademark and patent data for Italian technology companies
to identify trends, technology areas, and potential security concerns.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

class IPAnalyzer:
    """Analyzer for intellectual property data"""

    def __init__(self, aggregated_path: str = "C:/Projects/OSINT - Foresight/data/collected/aggregated"):
        """Initialize analyzer"""
        self.aggregated_path = Path(aggregated_path)
        self.output_path = self.aggregated_path / "analysis_outputs"
        self.output_path.mkdir(exist_ok=True)

        # Technology classification mappings
        self.tech_nice_classes = {
            'Computing/Software': [9, 42],
            'Telecommunications': [38],
            'Business/Data': [35],
            'Defense/Aerospace': [12, 13],
            'Electronics': [9],
            'Security': [45],
            'Industrial': [7, 12],
            'Energy': [4, 9, 11]
        }

        self.tech_ipc_codes = {
            'Computing': ['G06F', 'G06N', 'G06K'],
            'Semiconductors': ['H01L', 'H03K'],
            'Telecommunications': ['H04L', 'H04W', 'H04B'],
            'Aerospace': ['B64C', 'B64D', 'B64G'],
            'Defense': ['F41', 'F42'],
            'Energy': ['H02J', 'H02K', 'H01M'],
            'Robotics': ['B25J'],
            'Optics/Sensors': ['G01', 'G02B']
        }

        # Companies of interest
        self.key_companies = [
            'LEONARDO', 'FINCANTIERI', 'STMICROELECTRONICS',
            'TELESPAZIO', 'THALES ALENIA', 'ANSALDO',
            'DATALOGIC', 'ENGINEERING', 'REPLY', 'PRYSMIAN'
        ]

    def load_data(self, data_type: str = 'trademarks') -> Optional[pd.DataFrame]:
        """Load the most recent aggregated data file"""
        pattern = f"{data_type}_aggregated_*.csv"
        files = list(self.aggregated_path.glob(pattern))

        if not files:
            print(f"No {data_type} aggregated files found")
            return None

        # Get most recent file
        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        print(f"Loading: {latest_file.name}")

        df = pd.read_csv(latest_file, low_memory=False)

        # Parse dates if present
        date_columns = ['filing_date_parsed', 'filing_date', 'priority_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df

    def analyze_filing_trends(self, df: pd.DataFrame,
                             data_type: str = 'trademarks') -> Dict:
        """Analyze filing trends over time"""
        results = {}

        if 'filing_year' not in df.columns:
            if 'filing_date_parsed' in df.columns:
                df['filing_year'] = df['filing_date_parsed'].dt.year
            else:
                return results

        # Overall trend
        yearly_counts = df['filing_year'].value_counts().sort_index()
        results['yearly_filings'] = yearly_counts.to_dict()

        # Recent 5-year trend
        current_year = datetime.now().year
        recent_years = range(current_year - 5, current_year + 1)
        recent_trend = yearly_counts[yearly_counts.index.isin(recent_years)]
        results['recent_trend'] = recent_trend.to_dict()

        # Growth rate
        if len(recent_trend) > 1:
            growth_rate = (recent_trend.iloc[-1] - recent_trend.iloc[0]) / recent_trend.iloc[0] * 100
            results['5_year_growth'] = round(growth_rate, 2)

        # By company (if applicable)
        owner_col = 'owner_standardized' if data_type == 'trademarks' else 'applicant_standardized'
        if owner_col in df.columns:
            company_trends = {}
            for company in self.key_companies:
                company_df = df[df[owner_col] == company]
                if not company_df.empty:
                    company_yearly = company_df['filing_year'].value_counts().sort_index()
                    company_trends[company] = company_yearly.to_dict()
            results['company_trends'] = company_trends

        return results

    def analyze_technology_areas(self, df: pd.DataFrame,
                                data_type: str = 'trademarks') -> Dict:
        """Analyze technology classification distribution"""
        results = {}

        if data_type == 'trademarks' and 'nice_classes' in df.columns:
            # Parse Nice classes
            all_classes = []
            for classes in df['nice_classes'].dropna():
                if isinstance(classes, str):
                    # Handle various formats: "9, 35, 42" or "009 035 042"
                    import re
                    numbers = re.findall(r'\d+', str(classes))
                    all_classes.extend([int(n) for n in numbers])

            if all_classes:
                class_counts = pd.Series(all_classes).value_counts()
                results['nice_class_distribution'] = class_counts.head(10).to_dict()

                # Map to technology areas
                tech_areas = {}
                for tech, classes in self.tech_nice_classes.items():
                    count = sum(class_counts.get(c, 0) for c in classes)
                    if count > 0:
                        tech_areas[tech] = count
                results['technology_areas'] = dict(sorted(tech_areas.items(),
                                                         key=lambda x: x[1],
                                                         reverse=True))

        elif data_type == 'patents' and 'ipc_codes' in df.columns:
            # Parse IPC codes
            all_codes = []
            for codes in df['ipc_codes'].dropna():
                if isinstance(codes, str):
                    # Extract main IPC categories (first 4 chars)
                    code_list = str(codes).split(';') if ';' in str(codes) else str(codes).split(',')
                    for code in code_list:
                        if len(code.strip()) >= 4:
                            all_codes.append(code.strip()[:4])

            if all_codes:
                code_counts = pd.Series(all_codes).value_counts()
                results['ipc_distribution'] = code_counts.head(10).to_dict()

                # Map to technology areas
                tech_areas = {}
                for tech, codes in self.tech_ipc_codes.items():
                    count = sum(code_counts.get(c, 0) for c in codes)
                    if count > 0:
                        tech_areas[tech] = count
                results['technology_areas'] = dict(sorted(tech_areas.items(),
                                                         key=lambda x: x[1],
                                                         reverse=True))

        return results

    def identify_collaboration_patterns(self, df: pd.DataFrame,
                                      data_type: str = 'trademarks') -> Dict:
        """Identify potential collaborations and joint ventures"""
        results = {}
        owner_col = 'owner' if data_type == 'trademarks' else 'applicant'

        if owner_col not in df.columns:
            return results

        # Look for multiple owners (joint ownership)
        joint_ownership = []
        for idx, owner in df[owner_col].items():
            if pd.notna(owner) and any(separator in str(owner) for separator in [';', '&', ' and ', ',']):
                joint_ownership.append({
                    'index': idx,
                    'owners': owner,
                    'filing_year': df.loc[idx, 'filing_year'] if 'filing_year' in df.columns else None
                })

        results['joint_ownership_count'] = len(joint_ownership)
        results['joint_ownership_percentage'] = round(len(joint_ownership) / len(df) * 100, 2)

        # Identify international collaborations
        international_collabs = []
        for item in joint_ownership:
            owners_lower = str(item['owners']).lower()
            # Check for common international partnership indicators
            if any(country in owners_lower for country in ['usa', 'us', 'america', 'china', 'cn',
                                                           'germany', 'de', 'france', 'fr',
                                                           'japan', 'jp', 'korea', 'kr']):
                international_collabs.append(item)

        results['international_collaborations'] = len(international_collabs)

        return results

    def generate_security_insights(self, df: pd.DataFrame,
                                  data_type: str = 'trademarks') -> Dict:
        """Generate security-relevant insights"""
        insights = {
            'critical_technology_focus': [],
            'rapid_growth_areas': [],
            'international_exposure': [],
            'recommendations': []
        }

        # Analyze technology areas
        tech_analysis = self.analyze_technology_areas(df, data_type)

        if 'technology_areas' in tech_analysis:
            # Identify critical technology focus
            critical_techs = ['Defense/Aerospace', 'Computing/Software', 'Semiconductors',
                            'Telecommunications', 'Security']

            for tech in critical_techs:
                if tech in tech_analysis['technology_areas']:
                    count = tech_analysis['technology_areas'][tech]
                    percentage = round(count / len(df) * 100, 2)
                    insights['critical_technology_focus'].append({
                        'technology': tech,
                        'count': count,
                        'percentage': percentage
                    })

        # Analyze filing trends
        trend_analysis = self.analyze_filing_trends(df, data_type)

        if 'recent_trend' in trend_analysis and len(trend_analysis['recent_trend']) > 2:
            recent = trend_analysis['recent_trend']
            years = sorted(recent.keys())

            # Calculate year-over-year growth
            for i in range(1, len(years)):
                if recent[years[i-1]] > 0:
                    growth = (recent[years[i]] - recent[years[i-1]]) / recent[years[i-1]] * 100
                    if growth > 50:  # Rapid growth threshold
                        insights['rapid_growth_areas'].append({
                            'period': f"{years[i-1]}-{years[i]}",
                            'growth_rate': round(growth, 2)
                        })

        # Collaboration patterns
        collab_analysis = self.identify_collaboration_patterns(df, data_type)

        if collab_analysis.get('international_collaborations', 0) > 0:
            insights['international_exposure'].append({
                'type': 'International Collaborations',
                'count': collab_analysis['international_collaborations'],
                'risk_level': 'Medium' if collab_analysis['international_collaborations'] > 10 else 'Low'
            })

        # Generate recommendations
        if insights['critical_technology_focus']:
            insights['recommendations'].append(
                "Monitor IP filings in critical technology areas for potential technology transfer risks"
            )

        if insights['rapid_growth_areas']:
            insights['recommendations'].append(
                "Investigate rapid growth areas for emerging capabilities and potential dual-use applications"
            )

        if insights['international_exposure']:
            insights['recommendations'].append(
                "Review international collaborations for technology security implications"
            )

        return insights

    def create_summary_report(self, save_path: str = None) -> Dict:
        """Create comprehensive analysis report"""
        print("="*60)
        print("IP Data Analysis Report")
        print("="*60)

        report = {
            'generated_at': datetime.now().isoformat(),
            'trademarks': {},
            'patents': {},
            'security_insights': {}
        }

        # Analyze trademarks
        print("\nAnalyzing trademark data...")
        tm_df = self.load_data('trademarks')
        if tm_df is not None:
            print(f"  Loaded {len(tm_df)} trademark records")

            report['trademarks'] = {
                'total_records': len(tm_df),
                'filing_trends': self.analyze_filing_trends(tm_df, 'trademarks'),
                'technology_areas': self.analyze_technology_areas(tm_df, 'trademarks'),
                'collaborations': self.identify_collaboration_patterns(tm_df, 'trademarks'),
                'security_insights': self.generate_security_insights(tm_df, 'trademarks')
            }

        # Analyze patents
        print("\nAnalyzing patent data...")
        patent_df = self.load_data('patents')
        if patent_df is not None:
            print(f"  Loaded {len(patent_df)} patent records")

            report['patents'] = {
                'total_records': len(patent_df),
                'filing_trends': self.analyze_filing_trends(patent_df, 'patents'),
                'technology_areas': self.analyze_technology_areas(patent_df, 'patents'),
                'collaborations': self.identify_collaboration_patterns(patent_df, 'patents'),
                'security_insights': self.generate_security_insights(patent_df, 'patents')
            }

        # Combined security insights
        print("\nGenerating security insights...")
        combined_insights = []

        if report['trademarks'].get('security_insights'):
            tm_insights = report['trademarks']['security_insights']
            if tm_insights.get('critical_technology_focus'):
                combined_insights.append("Trademark filings show focus on critical technologies")

        if report['patents'].get('security_insights'):
            patent_insights = report['patents']['security_insights']
            if patent_insights.get('critical_technology_focus'):
                combined_insights.append("Patent portfolio indicates advanced technology development")

        report['security_insights'] = {
            'summary': combined_insights,
            'risk_assessment': self.assess_overall_risk(report),
            'recommendations': self.generate_recommendations(report)
        }

        # Save report
        if save_path:
            output_file = Path(save_path)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_path / f"ip_analysis_report_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nReport saved to: {output_file}")

        # Print summary
        self.print_report_summary(report)

        return report

    def assess_overall_risk(self, report: Dict) -> str:
        """Assess overall technology security risk"""
        risk_score = 0

        # Check for critical technology focus
        if report.get('trademarks', {}).get('security_insights', {}).get('critical_technology_focus'):
            risk_score += len(report['trademarks']['security_insights']['critical_technology_focus'])

        if report.get('patents', {}).get('security_insights', {}).get('critical_technology_focus'):
            risk_score += len(report['patents']['security_insights']['critical_technology_focus'])

        # Check for international collaborations
        tm_collabs = report.get('trademarks', {}).get('collaborations', {}).get('international_collaborations', 0)
        patent_collabs = report.get('patents', {}).get('collaborations', {}).get('international_collaborations', 0)

        if tm_collabs + patent_collabs > 20:
            risk_score += 3
        elif tm_collabs + patent_collabs > 10:
            risk_score += 2
        elif tm_collabs + patent_collabs > 0:
            risk_score += 1

        # Determine risk level
        if risk_score >= 5:
            return "HIGH - Significant technology security considerations"
        elif risk_score >= 3:
            return "MEDIUM - Moderate technology security considerations"
        else:
            return "LOW - Limited technology security concerns"

    def generate_recommendations(self, report: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Based on trademark analysis
        if report.get('trademarks', {}).get('filing_trends', {}).get('5_year_growth', 0) > 20:
            recommendations.append(
                "Rapid trademark growth detected - monitor for technology commercialization patterns"
            )

        # Based on patent analysis
        if report.get('patents', {}).get('total_records', 0) > 100:
            recommendations.append(
                "Significant patent portfolio - conduct detailed technology assessment"
            )

        # Based on collaborations
        total_collabs = (
            report.get('trademarks', {}).get('collaborations', {}).get('joint_ownership_count', 0) +
            report.get('patents', {}).get('collaborations', {}).get('joint_ownership_count', 0)
        )

        if total_collabs > 10:
            recommendations.append(
                "Multiple joint ownerships detected - review for technology transfer implications"
            )

        # General recommendations
        recommendations.extend([
            "Continue monitoring IP filings quarterly",
            "Cross-reference with procurement and export data",
            "Investigate companies with rapid filing growth"
        ])

        return recommendations

    def print_report_summary(self, report: Dict):
        """Print report summary to console"""
        print("\n" + "="*60)
        print("Analysis Summary")
        print("="*60)

        # Trademark summary
        if report.get('trademarks'):
            tm = report['trademarks']
            print(f"\nTrademarks:")
            print(f"  Total records: {tm.get('total_records', 0)}")

            if tm.get('technology_areas', {}).get('technology_areas'):
                print(f"  Top technology areas:")
                for tech, count in list(tm['technology_areas']['technology_areas'].items())[:3]:
                    print(f"    - {tech}: {count}")

            if tm.get('filing_trends', {}).get('5_year_growth'):
                print(f"  5-year growth: {tm['filing_trends']['5_year_growth']}%")

        # Patent summary
        if report.get('patents'):
            patents = report['patents']
            print(f"\nPatents:")
            print(f"  Total records: {patents.get('total_records', 0)}")

            if patents.get('technology_areas', {}).get('technology_areas'):
                print(f"  Top technology areas:")
                for tech, count in list(patents['technology_areas']['technology_areas'].items())[:3]:
                    print(f"    - {tech}: {count}")

        # Security assessment
        if report.get('security_insights'):
            print(f"\nSecurity Assessment:")
            print(f"  Risk Level: {report['security_insights'].get('risk_assessment', 'Unknown')}")

            if report['security_insights'].get('recommendations'):
                print(f"\n  Key Recommendations:")
                for rec in report['security_insights']['recommendations'][:3]:
                    print(f"    - {rec}")

        print("\n" + "="*60)

def main():
    """Main execution"""
    analyzer = IPAnalyzer()
    report = analyzer.create_summary_report()
    return report

if __name__ == "__main__":
    main()
