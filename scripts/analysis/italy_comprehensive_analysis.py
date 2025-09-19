#!/usr/bin/env python3
"""
Comprehensive Italy Analysis using all free data sources
Combines GLEIF, Semantic Scholar, Eurostat, and existing data
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.collectors.gleif_ownership_tracker import GLEIFOwnershipTracker
from src.collectors.semantic_scholar_tracker import SemanticScholarTracker
from src.collectors.eurostat_trade_analyzer import EurostatTradeAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ItalyComprehensiveAnalyzer:
    """Run comprehensive analysis on Italy using all available free sources"""

    def __init__(self):
        self.country = "ITA"
        self.output_dir = Path(f"artifacts/{self.country}/comprehensive_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize collectors
        self.gleif_tracker = GLEIFOwnershipTracker(self.country)
        self.scholar_tracker = SemanticScholarTracker(self.country)
        self.trade_analyzer = EurostatTradeAnalyzer("IT")  # Eurostat uses 2-letter codes

    def analyze_key_companies(self):
        """Analyze ownership of key Italian aerospace/defense companies"""

        # Key Italian companies with LEIs (found from various sources)
        italian_companies = {
            "549300MLUDYVRQOOXS22": "Leonardo S.p.A.",  # Major defense contractor
            "BUCRF72VH5RBN7X3HF75": "ENI S.p.A.",  # Energy
            "549300XFRF6G2JT5PG12": "Fincantieri S.p.A.",  # Shipbuilding
            "5493008W3WMHRZMBCJ48": "STMicroelectronics",  # Semiconductors
            "815600E2E1D2643CE860": "Pirelli & C. S.p.A.",  # Now Chinese-owned
            "549300TRUWO2CD2G5692": "Intesa Sanpaolo S.p.A.",  # Banking
            "549300R8O5L1HXWMWD73": "Enel S.p.A.",  # Energy
            "815600BFE89DF8075748": "Telecom Italia S.p.A.",  # Telecom
        }

        results = {
            "analyzed_at": datetime.now().isoformat(),
            "companies": {},
            "critical_findings": [],
            "china_owned": [],
            "complex_structures": []
        }

        logger.info(f"Analyzing {len(italian_companies)} Italian companies")

        for lei, name in italian_companies.items():
            logger.info(f"Analyzing {name} (LEI: {lei})")

            try:
                # Trace ownership chain
                ownership = self.gleif_tracker.trace_ownership_chain(lei)

                if ownership['entity']:
                    company_data = {
                        "name": name,
                        "lei": lei,
                        "country": ownership['entity'].get('country'),
                        "status": ownership['entity'].get('status'),
                        "has_parent": ownership['direct_parent'] is not None,
                        "ultimate_parent": None,
                        "china_owned": ownership['china_owned'],
                        "russia_owned": ownership['russia_owned'],
                        "risk_level": ownership['risk_level'],
                        "risk_factors": ownership['risk_factors']
                    }

                    if ownership['ultimate_parent']:
                        company_data['ultimate_parent'] = {
                            "name": ownership['ultimate_parent']['name'],
                            "country": ownership['ultimate_parent']['country'],
                            "lei": ownership['ultimate_parent']['lei']
                        }

                    results['companies'][lei] = company_data

                    # Flag critical findings
                    if ownership['china_owned']:
                        results['china_owned'].append(name)
                        results['critical_findings'].append(
                            f"⚠️ {name} has Chinese ultimate ownership"
                        )

                    if ownership['russia_owned']:
                        results['critical_findings'].append(
                            f"⚠️ {name} has Russian ultimate ownership"
                        )

                    if len(ownership['ownership_chain']) > 3:
                        results['complex_structures'].append({
                            "company": name,
                            "levels": len(ownership['ownership_chain'])
                        })

            except Exception as e:
                logger.error(f"Error analyzing {name}: {e}")
                results['companies'][lei] = {"error": str(e)}

        # Save results
        output_file = self.output_dir / "company_ownership_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Company ownership analysis saved to {output_file}")
        return results

    def analyze_research_networks(self):
        """Analyze Italian research institution China connections"""

        # Key Italian research institutions
        institutions = [
            "Politecnico di Milano",  # Top engineering school
            "Politecnico di Torino",  # Engineering/aerospace
            "Sapienza University of Rome",  # Largest university
            "University of Bologna",  # Oldest university
            "Scuola Superiore Sant'Anna",  # Elite institution
            "CNR",  # National Research Council
            "INFN",  # Nuclear physics
            "IIT",  # Italian Institute of Technology
        ]

        results = {
            "analyzed_at": datetime.now().isoformat(),
            "institutions": {},
            "high_risk_researchers": [],
            "china_collaborations": {
                "total": 0,
                "by_field": {}
            }
        }

        for institution in institutions[:4]:  # Limit to avoid rate limits
            logger.info(f"Analyzing research network for {institution}")

            try:
                # Find China-linked researchers
                china_linked = self.scholar_tracker.find_china_linked_researchers(
                    institution,
                    field="artificial intelligence"
                )

                # Analyze talent flows
                talent_flow = self.scholar_tracker.analyze_institution_talent_flow(
                    institution,
                    years=3
                )

                inst_data = {
                    "china_linked_researchers": len(china_linked),
                    "high_collaboration_researchers": [],
                    "sensitive_research_overlaps": 0
                }

                # Find high-risk individuals
                for researcher in china_linked:
                    if researcher.get('china_collaboration_rate', 0) > 30:
                        inst_data['high_collaboration_researchers'].append({
                            "name": researcher['name'],
                            "rate": researcher['china_collaboration_rate'],
                            "papers": len(researcher.get('china_papers', []))
                        })

                        if researcher.get('china_collaboration_rate', 0) > 50:
                            results['high_risk_researchers'].append({
                                "name": researcher['name'],
                                "institution": institution,
                                "collaboration_rate": researcher['china_collaboration_rate']
                            })

                # Count sensitive overlaps
                for collab in talent_flow.get('collaboration_metrics', {}).get('china_collaborators', []):
                    if collab.get('sensitive_overlaps', 0) > 0:
                        inst_data['sensitive_research_overlaps'] += collab['sensitive_overlaps']

                results['institutions'][institution] = inst_data
                results['china_collaborations']['total'] += len(china_linked)

            except Exception as e:
                logger.error(f"Error analyzing {institution}: {e}")
                results['institutions'][institution] = {"error": str(e)}

        # Save results
        output_file = self.output_dir / "research_network_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Research network analysis saved to {output_file}")
        return results

    def analyze_supply_chains(self):
        """Analyze critical component supply chains"""

        logger.info("Analyzing Italy supply chain dependencies")

        try:
            # Generate comprehensive supply chain report
            report = self.trade_analyzer.generate_supply_chain_report()

            # Extract key findings for Italy
            italy_findings = {
                "analyzed_at": datetime.now().isoformat(),
                "critical_dependencies": report['component_analysis']['critical_dependencies'],
                "risk_summary": report['risk_summary'],
                "recommendations": report['component_analysis']['recommendations'],
                "semiconductor_dependence": None,
                "aerospace_components": None
            }

            # Extract specific category data
            categories = report['component_analysis'].get('categories', {})

            if 'semiconductors' in categories:
                italy_findings['semiconductor_dependence'] = {
                    "average_china_dependence": categories['semiconductors']['average_china_dependence'],
                    "high_risk_components": categories['semiconductors']['high_risk_count']
                }

            if 'aerospace' in categories:
                italy_findings['aerospace_components'] = {
                    "average_china_dependence": categories['aerospace']['average_china_dependence'],
                    "high_risk_components": categories['aerospace']['high_risk_count']
                }

            # Save results
            output_file = self.output_dir / "supply_chain_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(italy_findings, f, indent=2)

            logger.info(f"Supply chain analysis saved to {output_file}")
            return italy_findings

        except Exception as e:
            logger.error(f"Error analyzing supply chains: {e}")
            return {"error": str(e)}

    def generate_master_report(self):
        """Combine all analyses into master report"""

        logger.info("Generating comprehensive Italy analysis report")

        # Run all analyses
        ownership = self.analyze_key_companies()
        research = self.analyze_research_networks()
        supply_chain = self.analyze_supply_chains()

        # Compile master report
        master_report = {
            "generated_at": datetime.now().isoformat(),
            "country": "Italy",
            "executive_summary": {
                "china_owned_companies": ownership.get('china_owned', []),
                "high_risk_researchers": len(research.get('high_risk_researchers', [])),
                "critical_supply_dependencies": len(supply_chain.get('critical_dependencies', [])),
                "overall_risk_level": "TO_BE_DETERMINED"
            },
            "ownership_analysis": {
                "companies_analyzed": len(ownership.get('companies', {})),
                "china_owned": ownership.get('china_owned', []),
                "complex_structures": ownership.get('complex_structures', []),
                "critical_findings": ownership.get('critical_findings', [])
            },
            "research_network_analysis": {
                "institutions_analyzed": len(research.get('institutions', {})),
                "total_china_collaborations": research.get('china_collaborations', {}).get('total', 0),
                "high_risk_researchers": research.get('high_risk_researchers', [])
            },
            "supply_chain_analysis": {
                "critical_dependencies": supply_chain.get('critical_dependencies', []),
                "semiconductor_risk": supply_chain.get('semiconductor_dependence'),
                "aerospace_risk": supply_chain.get('aerospace_components'),
                "recommendations": supply_chain.get('recommendations', [])
            },
            "critical_intelligence_gaps": [
                "No central MoU registry - unable to track research agreements",
                "Conference side meetings not monitored",
                "Joint lab agreements lack transparency",
                "Talent program participation unknown",
                "Dual-use technology transfers untracked"
            ],
            "immediate_actions_required": []
        }

        # Determine overall risk level
        risk_factors = 0
        if ownership.get('china_owned'):
            risk_factors += 2
        if len(research.get('high_risk_researchers', [])) > 5:
            risk_factors += 2
        if len(supply_chain.get('critical_dependencies', [])) > 3:
            risk_factors += 2

        if risk_factors >= 4:
            master_report['executive_summary']['overall_risk_level'] = "HIGH"
        elif risk_factors >= 2:
            master_report['executive_summary']['overall_risk_level'] = "MEDIUM-HIGH"
        else:
            master_report['executive_summary']['overall_risk_level'] = "MEDIUM"

        # Add immediate actions
        if ownership.get('china_owned'):
            master_report['immediate_actions_required'].append(
                f"Security review required for {len(ownership['china_owned'])} Chinese-owned companies"
            )

        if research.get('high_risk_researchers'):
            master_report['immediate_actions_required'].append(
                f"Monitor {len(research['high_risk_researchers'])} researchers with >50% China collaboration"
            )

        if supply_chain.get('critical_dependencies'):
            master_report['immediate_actions_required'].append(
                "Implement supply chain diversification for critical components"
            )

        # Add MoU registry requirement
        master_report['immediate_actions_required'].append(
            "Establish central MoU registry within 30 days"
        )

        # Save master report
        output_file = self.output_dir / "ITALY_MASTER_ANALYSIS_REPORT.json"
        with open(output_file, 'w') as f:
            json.dump(master_report, f, indent=2)

        # Also save as markdown
        md_report = self._format_markdown_report(master_report)
        md_file = self.output_dir / "ITALY_MASTER_ANALYSIS_REPORT.md"
        with open(md_file, 'w') as f:
            f.write(md_report)

        logger.info(f"Master report saved to {output_file}")
        logger.info(f"Markdown report saved to {md_file}")

        return master_report

    def _format_markdown_report(self, report):
        """Format report as markdown"""

        md = f"""# Italy Comprehensive Security Analysis
## Enhanced with GLEIF, Semantic Scholar, and Eurostat Data

**Generated:** {report['generated_at']}
**Risk Level:** {report['executive_summary']['overall_risk_level']}

## Executive Summary

### Critical Findings
- **Chinese-owned companies:** {', '.join(report['executive_summary']['china_owned_companies']) if report['executive_summary']['china_owned_companies'] else 'None identified'}
- **High-risk researchers:** {report['executive_summary']['high_risk_researchers']}
- **Critical supply dependencies:** {report['executive_summary']['critical_supply_dependencies']}

## Ownership Analysis (GLEIF)

**Companies analyzed:** {report['ownership_analysis']['companies_analyzed']}

### Chinese-Owned Entities
"""

        if report['ownership_analysis']['china_owned']:
            for company in report['ownership_analysis']['china_owned']:
                md += f"- ⚠️ **{company}** - Chinese ultimate ownership\n"
        else:
            md += "- None identified\n"

        md += """
### Complex Ownership Structures
"""

        for structure in report['ownership_analysis']['complex_structures']:
            md += f"- {structure['company']}: {structure['levels']} levels\n"

        md += """
## Research Network Analysis (Semantic Scholar)

**Institutions analyzed:** {report['research_network_analysis']['institutions_analyzed']}
**Total China collaborations:** {report['research_network_analysis']['total_china_collaborations']}

### High-Risk Researchers (>50% China collaboration)
"""

        for researcher in report['research_network_analysis']['high_risk_researchers'][:5]:
            md += f"- {researcher['name']} ({researcher['institution']}): {researcher['collaboration_rate']:.1f}%\n"

        md += """
## Supply Chain Analysis (Eurostat)

### Semiconductor Dependence
"""

        if report['supply_chain_analysis']['semiconductor_risk']:
            risk = report['supply_chain_analysis']['semiconductor_risk']
            md += f"- Average China dependence: {risk['average_china_dependence']:.1f}%\n"
            md += f"- High-risk components: {risk['high_risk_components']}\n"

        md += """
### Critical Dependencies
"""

        for dep in report['supply_chain_analysis']['critical_dependencies'][:5]:
            md += f"- {dep['description']} (HS {dep['hs_code']}): {dep['china_dependence']:.1f}% China dependent\n"

        md += """
## Critical Intelligence Gaps
"""

        for gap in report['critical_intelligence_gaps']:
            md += f"- {gap}\n"

        md += """
## Immediate Actions Required
"""

        for action in report['immediate_actions_required']:
            md += f"1. {action}\n"

        return md

def main():
    """Run comprehensive Italy analysis"""

    analyzer = ItalyComprehensiveAnalyzer()

    print("\n" + "="*60)
    print("ITALY COMPREHENSIVE SECURITY ANALYSIS")
    print("Using GLEIF, Semantic Scholar, and Eurostat")
    print("="*60 + "\n")

    # Generate master report
    report = analyzer.generate_master_report()

    print(f"\n✅ Analysis complete!")
    print(f"\nKey Findings:")
    print(f"- Risk Level: {report['executive_summary']['overall_risk_level']}")
    print(f"- Chinese-owned companies: {len(report['executive_summary']['china_owned_companies'])}")
    print(f"- High-risk researchers: {report['executive_summary']['high_risk_researchers']}")
    print(f"- Critical dependencies: {report['executive_summary']['critical_supply_dependencies']}")

    if report['immediate_actions_required']:
        print(f"\n🚨 Immediate Actions Required:")
        for i, action in enumerate(report['immediate_actions_required'], 1):
            print(f"  {i}. {action}")

    print(f"\nReports saved to: artifacts/ITA/comprehensive_analysis/")

if __name__ == "__main__":
    main()
