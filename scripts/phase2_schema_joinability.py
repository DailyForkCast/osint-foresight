#!/usr/bin/env python3
"""
Phase 2: Schema Standardization & Joinability Matrix
Aligns sources for cross-analysis and identifies join opportunities
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
from collections import defaultdict

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier

class SchemaAnalyzer:
    def __init__(self):
        self.canonical_fields = {
            'entity_id': ['id', 'entity_id', 'org_id', 'company_id', 'institution_id'],
            'org_name': ['name', 'organization', 'org_name', 'company_name', 'institution', 'beneficiary_name'],
            'country_iso': ['country', 'country_code', 'country_iso', 'iso_code', 'nation'],
            'year_month': ['date', 'year', 'publication_date', 'start_date', 'award_date'],
            'tech_keyword': ['keywords', 'technology', 'field', 'topic', 'domain'],
            'source': ['source', 'data_source', 'origin'],
            'doc_id': ['document_id', 'project_id', 'grant_id', 'contract_id', 'paper_id'],
            'china_related': ['china', 'chinese', 'cn', 'prc', 'beijing', 'shanghai'],
            'funding_amount': ['amount', 'funding', 'grant_amount', 'contract_value', 'budget'],
            'collaboration_type': ['type', 'collaboration', 'partnership', 'relationship']
        }

        self.joinability_matrix = {}
        self.schema_mappings = {}
        self.quality_scores = {}

    def analyze_database_schema(self, db_path):
        """Analyze database schema and map to canonical fields"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        schema_info = {}
        for table in tables:
            table_name = table[0]
            # SECURITY: Validate table name before use in SQL
            safe_table = validate_sql_identifier(table_name)
            cursor.execute(f"PRAGMA table_info({safe_table})")
            columns = cursor.fetchall()

            # Map columns to canonical fields
            column_mapping = {}
            for col in columns:
                col_name = col[1].lower()
                for canonical, variants in self.canonical_fields.items():
                    if any(v in col_name for v in variants):
                        column_mapping[col[1]] = canonical
                        break

            # Check data quality
            # SECURITY: safe_table already validated above
            cursor.execute(f"SELECT COUNT(*) FROM {safe_table}")
            total_rows = cursor.fetchone()[0]

            quality_metrics = {}
            if total_rows > 0:
                for col_name, canonical in column_mapping.items():
                    # SECURITY: Validate column name before use in SQL
                    safe_col = validate_sql_identifier(col_name)
                    cursor.execute(f"SELECT COUNT(*) FROM {safe_table} WHERE {safe_col} IS NOT NULL AND {safe_col} != ''")
                    non_null = cursor.fetchone()[0]
                    quality_metrics[canonical] = (non_null / total_rows) * 100

            schema_info[table_name] = {
                'columns': [col[1] for col in columns],
                'canonical_mapping': column_mapping,
                'row_count': total_rows,
                'quality_metrics': quality_metrics
            }

        conn.close()
        return schema_info

    def analyze_json_schema(self, json_path):
        """Analyze JSON file schema"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list) and len(data) > 0:
            sample = data[0]
        elif isinstance(data, dict):
            sample = data
        else:
            return {}

        # Map fields to canonical
        column_mapping = {}
        for field in sample.keys():
            field_lower = field.lower()
            for canonical, variants in self.canonical_fields.items():
                if any(v in field_lower for v in variants):
                    column_mapping[field] = canonical
                    break

        # Calculate quality
        quality_metrics = {}
        if isinstance(data, list):
            total = len(data)
            for field, canonical in column_mapping.items():
                non_null = sum(1 for item in data if item.get(field) and str(item.get(field)).strip())
                quality_metrics[canonical] = (non_null / total * 100) if total > 0 else 0

        return {
            'columns': list(sample.keys()),
            'canonical_mapping': column_mapping,
            'record_count': len(data) if isinstance(data, list) else 1,
            'quality_metrics': quality_metrics
        }

    def calculate_joinability(self, schema1, schema2):
        """Calculate joinability score between two schemas"""
        canonical1 = set(schema1.get('canonical_mapping', {}).values())
        canonical2 = set(schema2.get('canonical_mapping', {}).values())

        common_fields = canonical1.intersection(canonical2)

        if not common_fields:
            return 0

        # Calculate join score based on common fields and their quality
        join_score = 0
        join_fields = []

        # Priority join keys
        priority_keys = ['entity_id', 'org_name', 'doc_id']

        for field in common_fields:
            weight = 2.0 if field in priority_keys else 1.0
            quality1 = schema1.get('quality_metrics', {}).get(field, 0)
            quality2 = schema2.get('quality_metrics', {}).get(field, 0)
            field_score = (quality1 + quality2) / 200 * weight
            join_score += field_score

            if quality1 > 50 and quality2 > 50:  # Only viable if >50% populated
                join_fields.append(field)

        # Normalize to 0-100
        max_possible = len(common_fields) * 2.0
        normalized_score = (join_score / max_possible * 100) if max_possible > 0 else 0

        return {
            'score': min(normalized_score, 100),
            'common_fields': list(common_fields),
            'viable_join_fields': join_fields
        }

    def process_all_sources(self):
        """Process all data sources and create joinability matrix"""

        print("Analyzing data source schemas...")

        # Analyze databases
        databases = [
            ("OpenAIRE", "F:/OSINT_DATA/openaire_production_comprehensive/openaire_production.db"),
            ("CORDIS", "data/processed/cordis_unified/cordis_china_projects.db"),
        ]

        for name, path in databases:
            if Path(path).exists():
                print(f"Analyzing {name} database...")
                self.schema_mappings[name] = self.analyze_database_schema(path)

        # Analyze JSON files
        json_files = [
            ("CORDIS_China_Projects", "data/processed/cordis_multicountry/china_project_list_20250921_105946.json"),
            ("Poland_China_Collab", "data/processed/openaire_verified/PL_china_collaborations_20250922_202453.json"),
        ]

        for name, path in json_files:
            if Path(path).exists():
                print(f"Analyzing {name} JSON...")
                self.schema_mappings[name] = {path: self.analyze_json_schema(path)}

        # Calculate joinability matrix
        print("\nCalculating joinability matrix...")
        sources = list(self.schema_mappings.keys())

        for i, source1 in enumerate(sources):
            self.joinability_matrix[source1] = {}

            for source2 in sources[i+1:]:
                # Get first schema from each source
                schema1 = list(self.schema_mappings[source1].values())[0]
                schema2 = list(self.schema_mappings[source2].values())[0]

                joinability = self.calculate_joinability(schema1, schema2)
                self.joinability_matrix[source1][source2] = joinability

                # Symmetric
                if source2 not in self.joinability_matrix:
                    self.joinability_matrix[source2] = {}
                self.joinability_matrix[source2][source1] = joinability

        # Calculate data quality scores
        for source, schemas in self.schema_mappings.items():
            quality_scores = []
            total_records = 0

            for table_name, schema in schemas.items():
                if 'quality_metrics' in schema:
                    avg_quality = sum(schema['quality_metrics'].values()) / len(schema['quality_metrics']) if schema['quality_metrics'] else 0
                    quality_scores.append(avg_quality)
                    total_records += schema.get('row_count', 0) or schema.get('record_count', 0)

            self.quality_scores[source] = {
                'completeness': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                'total_records': total_records,
                'tables_analyzed': len(schemas)
            }

    def generate_report(self):
        """Generate Phase 2 report"""

        timestamp = datetime.now().isoformat()

        # Save detailed results
        results = {
            'generated': timestamp,
            'canonical_fields': self.canonical_fields,
            'schema_mappings': self.schema_mappings,
            'joinability_matrix': self.joinability_matrix,
            'quality_scores': self.quality_scores
        }

        with open("C:/Projects/OSINT - Foresight/phase2_schema_analysis.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)

        # Create joinability matrix CSV
        if self.joinability_matrix:
            sources = list(self.joinability_matrix.keys())
            matrix_data = []

            for source1 in sources:
                row = {'Source': source1}
                for source2 in sources:
                    if source1 == source2:
                        row[source2] = 100
                    else:
                        join_info = self.joinability_matrix.get(source1, {}).get(source2, {})
                        row[source2] = round(join_info.get('score', 0), 1) if join_info else 0
                matrix_data.append(row)

            df = pd.DataFrame(matrix_data)
            df.to_csv("C:/Projects/OSINT - Foresight/joinability_matrix.csv", index=False)

        # Generate markdown report
        report = f"""# Phase 2: Schema Standardization & Joinability Analysis

Generated: {timestamp}

## Canonical Field Definitions

| Canonical Field | Description | Source Variations |
|----------------|-------------|-------------------|
| entity_id | Unique identifier | {', '.join(self.canonical_fields['entity_id'])} |
| org_name | Organization name | {', '.join(self.canonical_fields['org_name'])} |
| country_iso | Country code | {', '.join(self.canonical_fields['country_iso'])} |
| year_month | Temporal field | {', '.join(self.canonical_fields['year_month'])} |
| tech_keyword | Technology terms | {', '.join(self.canonical_fields['tech_keyword'])} |
| doc_id | Document ID | {', '.join(self.canonical_fields['doc_id'])} |
| china_related | China indicators | {', '.join(self.canonical_fields['china_related'])} |

## Data Quality Scores (0-100)

| Source | Completeness | Total Records | Tables/Files |
|--------|--------------|---------------|--------------|
"""

        for source, scores in self.quality_scores.items():
            report += f"| {source} | {scores['completeness']:.1f}% | {scores['total_records']:,} | {scores['tables_analyzed']} |\n"

        report += "\n## Joinability Matrix (0-100 scores)\n\n"

        if self.joinability_matrix:
            # Create matrix table
            sources = list(self.joinability_matrix.keys())
            report += "| Source |"
            for s in sources:
                report += f" {s} |"
            report += "\n|" + "-|" * (len(sources) + 1) + "\n"

            for source1 in sources:
                report += f"| {source1} |"
                for source2 in sources:
                    if source1 == source2:
                        report += " 100 |"
                    else:
                        join_info = self.joinability_matrix.get(source1, {}).get(source2, {})
                        score = round(join_info.get('score', 0), 1) if join_info else 0
                        report += f" {score} |"
                report += "\n"

        report += "\n## High-Value Join Opportunities (>60 score)\n\n"

        processed = set()
        for source1, joins in self.joinability_matrix.items():
            for source2, join_info in joins.items():
                pair = tuple(sorted([source1, source2]))
                # Check if join_info is a dict before trying to get score
                if isinstance(join_info, dict):
                    score = join_info.get('score', 0)
                    if pair not in processed and score > 60:
                        processed.add(pair)
                        report += f"### {source1} ↔ {source2}\n"
                        report += f"- **Score**: {score:.1f}\n"
                        report += f"- **Viable Join Fields**: {', '.join(join_info.get('viable_join_fields', []))}\n"
                        report += f"- **Common Fields**: {', '.join(join_info.get('common_fields', []))}\n\n"

        report += """
## Remediation Actions

"""

        # Check for sources with low quality
        for source, scores in self.quality_scores.items():
            if scores['completeness'] < 30:
                report += f"⚠️ **{source}**: Low completeness ({scores['completeness']:.1f}%). Consider data enrichment or alternative sources.\n"

        # Check for isolated sources
        for source in self.joinability_matrix.keys():
            scores = []
            for j in self.joinability_matrix[source].values():
                if isinstance(j, dict):
                    scores.append(j.get('score', 0))
                elif isinstance(j, (int, float)):
                    scores.append(j)
            max_score = max(scores) if scores else 0
            if max_score < 30:
                report += f"⚠️ **{source}**: Low joinability (max {max_score:.1f}%). May need entity resolution or aliasing.\n"

        report += """

## Artifacts Created

1. `phase2_schema_analysis.json` - Detailed schema mappings
2. `joinability_matrix.csv` - Joinability scores matrix
3. This report - Schema standardization documentation

## Phase 2 Complete ✓

- Canonical fields defined: 10
- Sources analyzed: {}
- Joinability pairs evaluated: {}
- Data quality assessed
""".format(
            len(self.schema_mappings),
            len(processed)
        )

        with open("C:/Projects/OSINT - Foresight/phase2_schema_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\nPhase 2 Complete!")
        print(f"- Sources analyzed: {len(self.schema_mappings)}")
        print(f"- Joinability matrix created: joinability_matrix.csv")
        print(f"- Report saved: phase2_schema_report.md")

def main():
    analyzer = SchemaAnalyzer()
    analyzer.process_all_sources()
    analyzer.generate_report()

if __name__ == "__main__":
    main()
