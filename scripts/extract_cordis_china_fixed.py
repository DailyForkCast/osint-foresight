#!/usr/bin/env python3
"""
Extract CORDIS China Collaboration Data
Uses correct schema from existing CORDIS data
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

class CORDISChinaExtractor:
    def __init__(self):
        self.master_db = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/cordis_china")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_collaborations(self):
        """Extract Chinese collaborations using correct schema"""
        print("Extracting CORDIS China collaborations...")

        conn = sqlite3.connect(self.master_db)
        cur = conn.cursor()

        results = {
            'extraction_date': datetime.now().isoformat(),
            'chinese_organizations': [],
            'projects': [],
            'technology_areas': {},
            'funding_analysis': {},
            'collaboration_patterns': {},
            'risk_scores': []
        }

        # Use cordis_chinese_orgs table for Chinese organizations
        print("Extracting Chinese organizations...")
        cur.execute("SELECT org_name, org_type, project_count, total_funding, countries FROM cordis_chinese_orgs ORDER BY project_count DESC")
        chinese_orgs = cur.fetchall()

        for org_name, org_type, project_count, total_funding, countries in chinese_orgs:
            results['chinese_organizations'].append({
                'name': org_name,
                'type': org_type,
                'project_count': project_count,
                'total_funding': total_funding,
                'countries': countries
            })

        print(f"Found {len(chinese_orgs)} Chinese organizations")

        # Get projects with China involvement from cordis_projects_final
        print("Extracting projects with Chinese involvement...")
        cur.execute("""
            SELECT project_id, acronym, title, programme, start_date, end_date,
                   total_cost, eu_contribution, risk_score
            FROM cordis_projects_final
            WHERE china_involvement = 1
        """)
        china_projects = cur.fetchall()

        for proj in china_projects:
            project_data = {
                'project_id': proj[0],
                'acronym': proj[1],
                'title': proj[2],
                'programme': proj[3],
                'start_date': proj[4],
                'end_date': proj[5],
                'total_cost': proj[6],
                'eu_contribution': proj[7],
                'risk_score': proj[8]
            }
            results['projects'].append(project_data)

        print(f"Found {len(china_projects)} projects with Chinese involvement")

        # Get country collaboration data from cordis_project_countries
        print("Analyzing country collaboration patterns...")
        cur.execute("""
            SELECT country_code, SUM(participant_count) as total_participants
            FROM cordis_project_countries
            WHERE country_code != 'CN'
              AND project_id IN (
                  SELECT project_id FROM cordis_project_countries WHERE country_code = 'CN'
              )
            GROUP BY country_code
            ORDER BY total_participants DESC
            LIMIT 20
        """)

        country_collabs = cur.fetchall()
        results['collaboration_patterns']['by_country'] = {}
        for country, count in country_collabs:
            results['collaboration_patterns']['by_country'][country] = count

        # Calculate funding to China
        print("Calculating funding flows...")
        cur.execute("""
            SELECT SUM(eu_contribution) as total_eu_funding,
                   COUNT(*) as project_count,
                   AVG(risk_score) as avg_risk
            FROM cordis_projects_final
            WHERE china_involvement = 1
        """)
        funding = cur.fetchone()

        results['funding_analysis'] = {
            'total_eu_funding': funding[0] if funding[0] else 0,
            'china_project_count': funding[1] if funding[1] else 0,
            'average_risk_score': funding[2] if funding[2] else 0
        }

        # Get high-risk projects
        print("Identifying high-risk projects...")
        cur.execute("""
            SELECT project_id, acronym, title, risk_score
            FROM cordis_projects_final
            WHERE china_involvement = 1 AND risk_score > 60
            ORDER BY risk_score DESC
        """)
        high_risk = cur.fetchall()

        for proj_id, acronym, title, risk in high_risk:
            results['risk_scores'].append({
                'project_id': proj_id,
                'acronym': acronym,
                'title': title,
                'risk_score': risk
            })

        # Get collaboration data from cordis_china_collaborations
        print("Extracting collaboration details...")
        cur.execute("""
            SELECT project_id, chinese_org_name, collaboration_type,
                   technology_area, risk_level
            FROM cordis_china_collaborations
        """)
        collaborations = cur.fetchall()

        results['collaboration_details'] = []
        for proj_id, org_name, collab_type, tech_area, risk_level in collaborations:
            results['collaboration_details'].append({
                'project_id': proj_id,
                'chinese_organization': org_name,
                'collaboration_type': collab_type,
                'technology_area': tech_area,
                'risk_level': risk_level
            })

        conn.close()

        # Save results
        output_file = self.output_dir / f"cordis_china_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Results saved to {output_file}")

        # Generate summary report
        self.generate_summary_report(results)

        return results

    def generate_summary_report(self, results):
        """Generate markdown summary report"""

        total_funding = results['funding_analysis']['total_eu_funding']
        project_count = results['funding_analysis']['china_project_count']
        avg_risk = results['funding_analysis']['average_risk_score']

        report = f"""# CORDIS China Collaboration Intelligence Report
Generated: {results['extraction_date']}

## Executive Summary
- **Chinese Organizations Tracked**: {len(results['chinese_organizations'])}
- **Projects with Chinese Involvement**: {project_count}
- **Total EU Funding (China Projects)**: €{total_funding:,.2f}
- **Average Risk Score**: {avg_risk:.1f}/100
- **High-Risk Projects (>60)**: {len(results['risk_scores'])}

## Top Chinese Organizations by Project Count
"""
        # Top 15 Chinese organizations
        for i, org in enumerate(results['chinese_organizations'][:15], 1):
            funding_str = f"€{org['total_funding']:,.0f}" if org['total_funding'] else "N/A"
            report += f"{i}. **{org['name']}** ({org['type']}): {org['project_count']} projects\n"

        report += "\n## High-Risk Projects (Risk Score > 60)\n"
        for proj in results['risk_scores'][:10]:
            report += f"- **{proj['acronym']}** (Risk: {proj['risk_score']}): {proj['title'][:80]}...\n"

        report += "\n## Top EU Countries Collaborating with China\n"
        country_collabs = sorted(results['collaboration_patterns']['by_country'].items(),
                               key=lambda x: x[1], reverse=True)
        for i, (country, count) in enumerate(country_collabs[:15], 1):
            report += f"{i}. **{country}**: {count} collaborative participants\n"

        # Collaboration details
        if results.get('collaboration_details'):
            report += "\n## Technology Areas of Collaboration\n"
            tech_areas = {}
            for collab in results['collaboration_details']:
                tech = collab.get('technology_area')
                if tech:
                    tech_areas[tech] = tech_areas.get(tech, 0) + 1

            for tech, count in sorted(tech_areas.items(), key=lambda x: x[1], reverse=True)[:10]:
                report += f"- **{tech}**: {count} collaborations\n"

        # Intelligence insights
        report += f"""
## Key Intelligence Insights

1. **Scale of Collaboration**: {project_count} EU research projects involve Chinese entities
2. **Financial Exposure**: €{total_funding:,.0f} in EU funding flowing to China-involved projects
3. **Risk Profile**: Average risk score of {avg_risk:.1f} indicates moderate concern level
4. **High-Risk Focus**: {len(results['risk_scores'])} projects flagged as high-risk (>60/100)

## Risk Assessment

### Chinese Organizations of Concern:
"""
        # Top risk organizations
        high_activity_orgs = [org for org in results['chinese_organizations']
                             if org['project_count'] > 50][:5]
        for org in high_activity_orgs:
            report += f"- **{org['name']}**: {org['project_count']} projects (High Activity)\n"

        report += """
### Recommendations:
1. **Due Diligence**: Enhanced screening for projects involving high-activity Chinese organizations
2. **Technology Controls**: Review dual-use technologies in high-risk projects
3. **Monitoring**: Continuous tracking of funding flows and collaboration patterns
4. **Assessment**: Regular risk score updates based on geopolitical developments

---
*CORDIS China Intelligence Analysis*
*Personal OSINT Learning Project*
"""

        report_file = self.output_dir / f"CORDIS_CHINA_INTELLIGENCE_{datetime.now().strftime('%Y%m%d')}.md"
        report_file.write_text(report, encoding='utf-8')

        print(f"Intelligence report saved to {report_file}")

def main():
    extractor = CORDISChinaExtractor()
    results = extractor.extract_collaborations()

    print(f"\nCORDIS China Extraction Complete:")
    print(f"- Chinese Organizations: {len(results['chinese_organizations'])}")
    print(f"- Projects: {len(results['projects'])}")
    print(f"- High-Risk Projects: {len(results['risk_scores'])}")
    print(f"- Total EU Funding: €{results['funding_analysis']['total_eu_funding']:,.2f}")

if __name__ == "__main__":
    main()
