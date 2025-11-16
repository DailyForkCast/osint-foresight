"""
Query CORDIS database for quantum research projects
NO FABRICATION - Only report actual database contents
"""

import sqlite3
import json
from pathlib import Path

def query_cordis_quantum():
    db_path = "F:/OSINT_WAREHOUSE/osint_research.db"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Count total quantum projects
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM cordis_projects
            WHERE title LIKE '%quantum%' OR objective LIKE '%quantum%'
        """)
        total = cursor.fetchone()['total']
        print(f"Total quantum projects in CORDIS: {total}")

        # Get detailed project information
        cursor.execute("""
            SELECT
                project_id,
                title,
                objective,
                total_cost,
                ec_contribution,
                start_date,
                end_date,
                status,
                programme
            FROM cordis_projects
            WHERE title LIKE '%quantum%' OR objective LIKE '%quantum%'
            ORDER BY total_cost DESC
        """)

        projects = []
        for row in cursor.fetchall():
            projects.append(dict(row))

        # Get organizations involved in quantum projects
        cursor.execute("""
            SELECT DISTINCT
                o.organization_name,
                o.country,
                COUNT(*) as project_count
            FROM cordis_organizations o
            JOIN cordis_project_participants pp ON o.organization_id = pp.organization_id
            JOIN cordis_projects p ON pp.project_id = p.project_id
            WHERE p.title LIKE '%quantum%' OR p.objective LIKE '%quantum%'
            GROUP BY o.organization_name, o.country
            ORDER BY project_count DESC
            LIMIT 50
        """)

        organizations = [dict(row) for row in cursor.fetchall()]

        # Get countries involved
        cursor.execute("""
            SELECT
                country,
                COUNT(DISTINCT p.project_id) as project_count,
                SUM(p.total_cost) as total_funding
            FROM cordis_project_countries pc
            JOIN cordis_projects p ON pc.project_id = p.project_id
            WHERE p.title LIKE '%quantum%' OR p.objective LIKE '%quantum%'
            GROUP BY country
            ORDER BY project_count DESC
        """)

        countries = [dict(row) for row in cursor.fetchall()]

        conn.close()

        # Generate report
        report = {
            'source': 'CORDIS EU Research Database',
            'query_date': '2025-10-06',
            'database_path': db_path,
            'total_quantum_projects': total,
            'projects': projects,
            'leading_organizations': organizations,
            'countries': countries,
            'funding_summary': {
                'total_cost': sum(p.get('total_cost', 0) or 0 for p in projects),
                'ec_contribution': sum(p.get('ec_contribution', 0) or 0 for p in projects)
            }
        }

        output_path = "C:/Projects/OSINT - Foresight/analysis/quantum_tech/cordis_quantum_analysis.json"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {output_path}")
        print(f"\nTop 10 Organizations:")
        for org in organizations[:10]:
            print(f"  - {org['organization_name']} ({org['country']}): {org['project_count']} projects")

        print(f"\nTop 10 Countries:")
        for country in countries[:10]:
            print(f"  - {country['country']}: {country['project_count']} projects")

        return report

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    query_cordis_quantum()
