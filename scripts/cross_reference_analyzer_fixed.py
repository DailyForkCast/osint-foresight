#!/usr/bin/env python3
"""
Cross-Reference Analysis System - FIXED VERSION
Analyzes connections between different intelligence sources
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

class CrossReferenceAnalyzer:
    def __init__(self):
        self.warehouse_path = Path("F:/OSINT_WAREHOUSE")
        self.output_path = Path("C:/Projects/OSINT - Foresight/analysis")

        self.source_mappings = {
            'patents': self.warehouse_path / 'osint_master.db',
            'leonardo': self.warehouse_path / 'osint_master.db',
            'mcf': self.warehouse_path / 'osint_master.db',
            'arctic': self.warehouse_path / 'osint_master.db',
            'taxonomy': self.warehouse_path / 'osint_master.db'
        }

        self.cross_references = {
            'entity_technology': {},
            'technology_sources': {},
            'source_overlaps': {},
            'critical_intersections': []
        }

    def perform_cross_reference_analysis(self):
        """Perform cross-reference analysis"""
        print("Performing cross-reference analysis...")

        self.build_entity_technology_matrix()
        self.identify_technology_overlaps()
        self.find_critical_intersections()

        return self.cross_references

    def build_entity_technology_matrix(self):
        """Build matrix of entities and technologies"""
        entity_tech_map = {}

        # From Leonardo assessments
        if self.source_mappings['leonardo'].exists():
            conn = sqlite3.connect(self.source_mappings['leonardo'])
            cur = conn.cursor()
            cur.execute('SELECT entity_name, technology_name FROM technology_assessments')
            for entity, tech in cur.fetchall():
                if entity not in entity_tech_map:
                    entity_tech_map[entity] = set()
                entity_tech_map[entity].add(tech)
            conn.close()

        # From MCF entities
        if self.source_mappings['mcf'].exists():
            conn = sqlite3.connect(self.source_mappings['mcf'])
            cur = conn.cursor()
            cur.execute('SELECT entity_name FROM mcf_entities')
            for row in cur.fetchall():
                entity = row[0]
                if entity and entity not in entity_tech_map:
                    entity_tech_map[entity] = set()
            conn.close()

        self.cross_references['entity_technology'] = {
            entity: list(techs) for entity, techs in entity_tech_map.items()
        }

    def identify_technology_overlaps(self):
        """Identify technologies in multiple sources"""
        tech_sources = {}
        source_techs = {}

        # MCF technologies
        if self.source_mappings['mcf'].exists():
            conn = sqlite3.connect(self.source_mappings['mcf'])
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT technology_name FROM dual_use_technologies")
            source_techs['mcf'] = set(row[0] for row in cur.fetchall() if row[0])
            conn.close()

        # Arctic technologies
        if self.source_mappings['arctic'].exists():
            conn = sqlite3.connect(self.source_mappings['arctic'])
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT technology_name FROM arctic_technologies")
            source_techs['arctic'] = set(row[0] for row in cur.fetchall() if row[0])
            conn.close()

        # Build technology -> sources mapping
        all_techs = set()
        for source_techs_set in source_techs.values():
            all_techs.update(source_techs_set)

        for tech in all_techs:
            tech_sources[tech] = []
            for source, techs in source_techs.items():
                if tech in techs:
                    tech_sources[tech].append(source)

        self.cross_references['technology_sources'] = tech_sources
        self.cross_references['multi_source_techs'] = {
            tech: sources for tech, sources in tech_sources.items()
            if len(sources) > 1
        }

    def find_critical_intersections(self):
        """Find critical cross-references - FIXED"""
        critical = []

        # High-risk entities with multiple technologies
        for entity, techs in self.cross_references['entity_technology'].items():
            if len(techs) > 2:
                if self.source_mappings['leonardo'].exists():
                    conn = sqlite3.connect(self.source_mappings['leonardo'])
                    cur = conn.cursor()
                    cur.execute('''
                        SELECT MAX(leonardo_composite_score)
                        FROM technology_assessments
                        WHERE entity_name = ?
                    ''', (entity,))
                    result = cur.fetchone()
                    max_score = result[0] if result else None
                    conn.close()

                    if max_score and max_score > 85:
                        critical.append({
                            'type': 'HIGH_RISK_MULTI_TECH',
                            'entity': entity,
                            'technologies': techs,
                            'risk_score': max_score,
                            'priority': 'CRITICAL'
                        })

        # Technologies in both MCF and Arctic
        for tech, sources in self.cross_references.get('multi_source_techs', {}).items():
            if 'mcf' in sources and 'arctic' in sources:
                critical.append({
                    'type': 'MCF_ARCTIC_CONVERGENCE',
                    'technology': tech,
                    'sources': sources,
                    'priority': 'HIGH'
                })

        # Patent activity check - FIXED
        patent_entities = set()
        if self.source_mappings['patents'].exists():
            conn = sqlite3.connect(self.source_mappings['patents'])
            cur = conn.cursor()

            # Get actual column from patent_searches
            cur.execute("PRAGMA table_info(patent_searches)")
            columns = [col[1] for col in cur.fetchall()]

            # Use search_query column which contains entity names
            if 'search_query' in columns:
                cur.execute("SELECT DISTINCT search_query FROM patent_searches")
                patent_entities = set(row[0] for row in cur.fetchall() if row[0])

            conn.close()

        for entity in patent_entities:
            if entity in self.cross_references['entity_technology']:
                critical.append({
                    'type': 'PATENT_NETWORK_NODE',
                    'entity': entity,
                    'patent_activity': True,
                    'technology_count': len(self.cross_references['entity_technology'][entity]),
                    'priority': 'ELEVATED'
                })

        self.cross_references['critical_intersections'] = critical

    def generate_cross_reference_report(self):
        """Generate cross-reference analysis report"""
        self.perform_cross_reference_analysis()

        report = f"""# CROSS-REFERENCE INTELLIGENCE ANALYSIS
Generated: {datetime.now().isoformat()}
Analysis Type: Multi-Source Cross-Reference

## EXECUTIVE SUMMARY

### Cross-Reference Statistics
- **Entities with Technologies**: {len(self.cross_references['entity_technology'])}
- **Multi-Source Technologies**: {len(self.cross_references.get('multi_source_techs', {}))}
- **Critical Intersections**: {len(self.cross_references['critical_intersections'])}

## ENTITY-TECHNOLOGY MATRIX

### Top Multi-Technology Entities
"""
        sorted_entities = sorted(
            self.cross_references['entity_technology'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        for entity, techs in sorted_entities[:5]:
            report += f"""
**{entity}**
- Technologies: {len(techs)}
- Key Areas: {', '.join(techs[:3]) if techs else 'N/A'}
"""

        if self.cross_references.get('multi_source_techs'):
            report += """
## MULTI-SOURCE TECHNOLOGY VALIDATION

### Technologies Confirmed Across Multiple Sources
"""
            for tech, sources in list(self.cross_references['multi_source_techs'].items())[:5]:
                report += f"- **{tech}**: Confirmed in {', '.join(sources)}\n"

        report += """
## CRITICAL INTERSECTIONS
"""
        for intersection in self.cross_references['critical_intersections'][:5]:
            report += f"""
**{intersection['type']}**
- Entity/Tech: {intersection.get('entity', intersection.get('technology', 'N/A'))}
- Priority: {intersection['priority']}
"""

        report += """
---
*Cross-Reference Intelligence Analysis*
*Personal OSINT Learning Project*
"""

        report_path = self.output_path / "CROSS_REFERENCE_ANALYSIS.md"
        report_path.write_text(report)
        print(f"Cross-reference analysis saved to {report_path}")

        return report

def main():
    analyzer = CrossReferenceAnalyzer()
    analyzer.generate_cross_reference_report()
    print("Cross-reference analysis complete!")

if __name__ == "__main__":
    main()
