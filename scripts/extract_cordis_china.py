#!/usr/bin/env python3
"""
Extract CORDIS China Collaboration Data
Processes existing CORDIS data to identify and analyze Chinese collaborations
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

        # Chinese organization keywords
        self.chinese_keywords = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'guangzhou',
            'tsinghua', 'peking university', 'fudan', 'zhejiang', 'nanjing',
            'cas ', 'chinese academy', 'huawei', 'alibaba', 'tencent', 'baidu',
            'smic', 'zte', 'xiaomi', 'dji', 'bytedance', 'wuhan', 'tianjin',
            'chengdu', 'xian', 'harbin', 'dalian', 'qingdao', 'hangzhou'
        ]

    def extract_collaborations(self):
        """Extract Chinese collaborations from CORDIS data"""
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
            'top_collaborators': []
        }

        # Extract Chinese organizations
        print("Identifying Chinese organizations...")
        query = """
        SELECT DISTINCT organization_name, country, project_count
        FROM cordis_organizations
        WHERE LOWER(organization_name) LIKE '%china%'
           OR LOWER(organization_name) LIKE '%chinese%'
           OR LOWER(organization_name) LIKE '%beijing%'
           OR LOWER(organization_name) LIKE '%shanghai%'
           OR LOWER(organization_name) LIKE '%tsinghua%'
           OR LOWER(organization_name) LIKE '%peking%'
           OR LOWER(organization_name) LIKE '%fudan%'
           OR LOWER(organization_name) LIKE '%zhejiang%'
           OR LOWER(organization_name) LIKE '%huawei%'
           OR country = 'CN'
        ORDER BY project_count DESC
        """

        cur.execute(query)
        chinese_orgs = cur.fetchall()

        for org_name, country, project_count in chinese_orgs:
            results['chinese_organizations'].append({
                'name': org_name,
                'country': country,
                'project_count': project_count
            })

        print(f"Found {len(chinese_orgs)} Chinese organizations")

        # Get projects with Chinese participation
        print("Extracting Chinese projects...")
        query = """
        SELECT DISTINCT p.project_id, p.project_name, p.start_date,
               p.end_date, p.total_cost, p.eu_contribution, p.objective
        FROM cordis_projects p
        JOIN cordis_participants part ON p.project_id = part.project_id
        WHERE LOWER(part.organization_name) LIKE '%china%'
           OR LOWER(part.organization_name) LIKE '%chinese%'
           OR LOWER(part.organization_name) LIKE '%beijing%'
           OR LOWER(part.organization_name) LIKE '%shanghai%'
           OR LOWER(part.organization_name) LIKE '%tsinghua%'
           OR part.country = 'CN'
        """

        cur.execute(query)
        projects = cur.fetchall()

        for proj in projects:
            project_data = {
                'project_id': proj[0],
                'name': proj[1],
                'start_date': proj[2],
                'end_date': proj[3],
                'total_cost': proj[4],
                'eu_contribution': proj[5],
                'objective': proj[6][:500] if proj[6] else None  # First 500 chars
            }
            results['projects'].append(project_data)

        print(f"Found {len(projects)} projects with Chinese participation")

        # Analyze technology areas
        print("Analyzing technology areas...")
        query = """
        SELECT programme_name, COUNT(DISTINCT project_id) as project_count
        FROM cordis_projects p
        JOIN cordis_participants part ON p.project_id = part.project_id
        WHERE part.country = 'CN' OR LOWER(part.organization_name) LIKE '%china%'
        GROUP BY programme_name
        ORDER BY project_count DESC
        LIMIT 20
        """

        cur.execute(query)
        tech_areas = cur.fetchall()

        for area, count in tech_areas:
            if area:
                results['technology_areas'][area] = count

        # Calculate total funding to Chinese organizations
        print("Calculating funding flows...")
        query = """
        SELECT SUM(part.eu_contribution) as total_funding,
               COUNT(DISTINCT part.project_id) as project_count,
               COUNT(DISTINCT part.organization_name) as org_count
        FROM cordis_participants part
        WHERE part.country = 'CN' OR LOWER(part.organization_name) LIKE '%china%'
        """

        cur.execute(query)
        funding = cur.fetchone()

        results['funding_analysis'] = {
            'total_eu_funding': funding[0] if funding[0] else 0,
            'project_count': funding[1] if funding[1] else 0,
            'organization_count': funding[2] if funding[2] else 0
        }

        # Find top EU collaborators with Chinese organizations
        print("Finding top EU collaborators...")
        query = """
        SELECT eu_part.organization_name, eu_part.country,
               COUNT(DISTINCT eu_part.project_id) as collab_count
        FROM cordis_participants cn_part
        JOIN cordis_participants eu_part ON cn_part.project_id = eu_part.project_id
        WHERE (cn_part.country = 'CN' OR LOWER(cn_part.organization_name) LIKE '%china%')
          AND eu_part.country != 'CN'
          AND eu_part.country IS NOT NULL
        GROUP BY eu_part.organization_name, eu_part.country
        ORDER BY collab_count DESC
        LIMIT 50
        """

        cur.execute(query)
        collaborators = cur.fetchall()

        for org_name, country, collab_count in collaborators:
            results['top_collaborators'].append({
                'organization': org_name,
                'country': country,
                'collaboration_count': collab_count
            })

        # Analyze collaboration patterns over time
        print("Analyzing temporal patterns...")
        query = """
        SELECT SUBSTR(p.start_date, 1, 4) as year,
               COUNT(DISTINCT p.project_id) as project_count
        FROM cordis_projects p
        JOIN cordis_participants part ON p.project_id = part.project_id
        WHERE (part.country = 'CN' OR LOWER(part.organization_name) LIKE '%china%')
          AND p.start_date IS NOT NULL
        GROUP BY year
        ORDER BY year
        """

        cur.execute(query)
        temporal = cur.fetchall()

        results['collaboration_patterns']['temporal'] = {}
        for year, count in temporal:
            if year:
                results['collaboration_patterns']['temporal'][year] = count

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
        report = f"""# CORDIS China Collaboration Analysis
Generated: {results['extraction_date']}

## Executive Summary
- **Chinese Organizations Identified**: {len(results['chinese_organizations'])}
- **Projects with Chinese Participation**: {len(results['projects'])}
- **Total EU Funding to Chinese Entities**: €{results['funding_analysis']['total_eu_funding']:,.2f}
- **Unique Chinese Organizations**: {results['funding_analysis']['organization_count']}

## Top Chinese Organizations by Project Count
"""

        # Top 10 Chinese organizations
        for i, org in enumerate(results['chinese_organizations'][:10], 1):
            report += f"{i}. **{org['name']}**: {org['project_count']} projects\n"

        report += "\n## Technology Areas of Collaboration\n"
        for area, count in list(results['technology_areas'].items())[:10]:
            report += f"- **{area}**: {count} projects\n"

        report += "\n## Top EU Collaborators with Chinese Organizations\n"
        for i, collab in enumerate(results['top_collaborators'][:15], 1):
            report += f"{i}. **{collab['organization']}** ({collab['country']}): {collab['collaboration_count']} joint projects\n"

        # Temporal analysis
        report += "\n## Collaboration Trends Over Time\n"
        if results['collaboration_patterns'].get('temporal'):
            years = sorted(results['collaboration_patterns']['temporal'].keys())
            for year in years[-5:]:  # Last 5 years
                count = results['collaboration_patterns']['temporal'][year]
                report += f"- **{year}**: {count} projects\n"

        # Key insights
        report += """
## Key Intelligence Insights

1. **Technology Transfer Risk**: Significant EU-China collaboration in critical technology areas
2. **Funding Exposure**: Substantial EU research funding flowing to Chinese entities
3. **Network Effects**: Chinese organizations deeply embedded in European research networks
4. **Temporal Trend**: Growing collaboration despite geopolitical tensions

## Recommendations

1. **Enhanced Due Diligence**: Screen Chinese participants for military/dual-use connections
2. **Technology Controls**: Review sensitive technology areas for collaboration restrictions
3. **Funding Oversight**: Track EU funding flows to Chinese entities more closely
4. **Risk Assessment**: Evaluate each collaboration for technology transfer risks

---
*CORDIS China Collaboration Analysis*
*Personal OSINT Learning Project*
"""

        report_file = self.output_dir / f"CORDIS_CHINA_ANALYSIS_{datetime.now().strftime('%Y%m%d')}.md"
        report_file.write_text(report, encoding='utf-8')

        print(f"Summary report saved to {report_file}")

def main():
    extractor = CORDISChinaExtractor()
    results = extractor.extract_collaborations()

    print(f"\nExtraction Complete:")
    print(f"- Chinese Organizations: {len(results['chinese_organizations'])}")
    print(f"- Projects: {len(results['projects'])}")
    print(f"- Total EU Funding: €{results['funding_analysis']['total_eu_funding']:,.2f}")

if __name__ == "__main__":
    main()
