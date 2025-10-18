#!/usr/bin/env python3
"""
Phase 2: Schema Harmonization on Full Dataset
Creates joinability matrix and canonical field mappings
"""

import json
import csv
from pathlib import Path
from datetime import datetime
import sys
from collections import defaultdict
import pandas as pd

class SchemaHarmonizer:
    def __init__(self):
        # Load Phase 1 results
        self.load_phase1_results()

        self.canonical_fields = {
            # Universal identifiers
            'id': ['id', 'ID', '_id', 'identifier', 'uuid', 'guid'],
            'name': ['name', 'title', 'label', 'description', 'project_name'],
            'date': ['date', 'created', 'modified', 'timestamp', 'datetime'],

            # Organization fields
            'organization': ['organization', 'org', 'company', 'institution', 'entity'],
            'organization_id': ['org_id', 'organization_id', 'company_id', 'entity_id'],
            'country': ['country', 'country_code', 'nation', 'location'],

            # Financial fields
            'amount': ['amount', 'value', 'cost', 'price', 'budget'],
            'currency': ['currency', 'currency_code', 'curr'],

            # Technical fields
            'technology': ['technology', 'tech', 'field', 'domain', 'area'],
            'keywords': ['keywords', 'tags', 'topics', 'subjects'],

            # Relationship fields
            'parent_id': ['parent_id', 'parent', 'related_id'],
            'source': ['source', 'origin', 'from', 'provider'],
            'target': ['target', 'destination', 'to', 'recipient']
        }

        self.joinability_matrix = {}
        self.field_mappings = {}
        self.quality_scores = {}
        self.join_examples = []

    def load_phase1_results(self):
        """Load content profiles and schema registry from Phase 1"""
        profiles_path = Path("C:/Projects/OSINT - Foresight/content_profiles_complete.json")
        schema_path = Path("C:/Projects/OSINT - Foresight/schema_registry.json")

        if profiles_path.exists():
            with open(profiles_path, 'r') as f:
                self.content_profiles = json.load(f)
            print(f"Loaded {len(self.content_profiles)} content profiles")
        else:
            print("WARNING: No content profiles found, using empty set")
            self.content_profiles = {}

        if schema_path.exists():
            with open(schema_path, 'r') as f:
                self.schema_registry = json.load(f)
            print(f"Loaded {len(self.schema_registry)} schemas")
        else:
            print("WARNING: No schema registry found, using empty set")
            self.schema_registry = {}

    def map_to_canonical(self, field_name):
        """Map a field name to its canonical form"""
        field_lower = field_name.lower()

        for canonical, variants in self.canonical_fields.items():
            if field_lower in [v.lower() for v in variants]:
                return canonical

        # Check for partial matches
        for canonical, variants in self.canonical_fields.items():
            for variant in variants:
                if variant.lower() in field_lower or field_lower in variant.lower():
                    return canonical

        return None  # No canonical mapping found

    def analyze_schemas(self):
        """Analyze all schemas and create field mappings"""
        print("\nAnalyzing schemas and creating canonical mappings...")

        for source_key, schemas in self.schema_registry.items():
            if not schemas:
                continue

            # Take first schema as representative
            schema = schemas[0] if isinstance(schemas[0], dict) else {}

            mapping = {}
            canonical_coverage = 0

            for field_name in schema.keys():
                canonical = self.map_to_canonical(field_name)
                if canonical:
                    mapping[field_name] = canonical
                    canonical_coverage += 1

            self.field_mappings[source_key] = {
                'original_fields': list(schema.keys()),
                'canonical_mappings': mapping,
                'coverage': canonical_coverage / len(schema) * 100 if schema else 0
            }

        print(f"Created mappings for {len(self.field_mappings)} sources")

    def calculate_joinability(self):
        """Calculate joinability scores between all source pairs"""
        print("\nCalculating joinability matrix...")

        sources = list(self.field_mappings.keys())

        for i, source1 in enumerate(sources):
            for j, source2 in enumerate(sources):
                if i >= j:  # Skip diagonal and lower triangle
                    continue

                # Get canonical fields for each source
                canonical1 = set(self.field_mappings[source1]['canonical_mappings'].values())
                canonical2 = set(self.field_mappings[source2]['canonical_mappings'].values())

                # Calculate overlap
                common_fields = canonical1 & canonical2

                # Joinability score
                if canonical1 and canonical2:
                    score = len(common_fields) / min(len(canonical1), len(canonical2))
                else:
                    score = 0.0

                pair_key = f"{source1}_{source2}"
                self.joinability_matrix[pair_key] = {
                    'source1': source1,
                    'source2': source2,
                    'common_fields': list(common_fields),
                    'score': score,
                    'viability': 'HIGH' if score > 0.5 else 'MEDIUM' if score > 0.2 else 'LOW'
                }

        print(f"Calculated joinability for {len(self.joinability_matrix)} pairs")

        # Count high-viability pairs
        high_viability = sum(1 for j in self.joinability_matrix.values() if j['viability'] == 'HIGH')
        print(f"High-viability pairs: {high_viability}")

    def generate_join_examples(self):
        """Generate example joins for high-viability pairs"""
        print("\nGenerating join examples...")

        examples_needed = 10  # Per high-viability pair

        for pair_key, joinability in self.joinability_matrix.items():
            if joinability['viability'] != 'HIGH':
                continue

            source1 = joinability['source1']
            source2 = joinability['source2']
            common_fields = joinability['common_fields']

            if not common_fields:
                continue

            # Find actual files for these sources
            files1 = [p for p, prof in self.content_profiles.items()
                     if source1.split('_')[0] in prof.get('location', '')]
            files2 = [p for p, prof in self.content_profiles.items()
                     if source2.split('_')[0] in prof.get('location', '')]

            if files1 and files2:
                for i in range(min(examples_needed, len(files1), len(files2))):
                    self.join_examples.append({
                        'pair': pair_key,
                        'file1': files1[i] if i < len(files1) else files1[0],
                        'file2': files2[i] if i < len(files2) else files2[0],
                        'join_fields': common_fields[:3],  # Top 3 common fields
                        'viability': 'HIGH'
                    })

        print(f"Generated {len(self.join_examples)} join examples")

    def calculate_quality_scores(self):
        """Calculate data quality scores (0-100) for each source"""
        print("\nCalculating quality scores...")

        for source_key in self.field_mappings.keys():
            # Find files for this source
            source_files = [p for p, prof in self.content_profiles.items()
                          if source_key.split('_')[0] in prof.get('location', '')]

            if not source_files:
                self.quality_scores[source_key] = {
                    'completeness': 0,
                    'consistency': 0,
                    'validity': 0,
                    'overall': 0
                }
                continue

            # Calculate metrics
            parse_success = sum(1 for f in source_files
                              if self.content_profiles[f].get('parse_status') == 'success')

            completeness = (parse_success / len(source_files) * 100) if source_files else 0

            # Consistency based on schema coverage
            consistency = self.field_mappings[source_key]['coverage']

            # Validity based on successful parsing
            validity = completeness  # Simplified: valid if parseable

            # Overall score
            overall = (completeness + consistency + validity) / 3

            self.quality_scores[source_key] = {
                'completeness': round(completeness, 1),
                'consistency': round(consistency, 1),
                'validity': round(validity, 1),
                'overall': round(overall, 1)
            }

        print(f"Calculated quality scores for {len(self.quality_scores)} sources")

    def save_results(self):
        """Save all Phase 2 results"""
        print("\nSaving results...")

        # Save canonical field definitions
        with open("C:/Projects/OSINT - Foresight/canonical_fields.json", 'w') as f:
            json.dump(self.canonical_fields, f, indent=2)

        # Save field mappings
        with open("C:/Projects/OSINT - Foresight/field_mappings.json", 'w') as f:
            json.dump(self.field_mappings, f, indent=2)

        # Save joinability matrix as CSV
        with open("C:/Projects/OSINT - Foresight/joinability_matrix.csv", 'w', newline='') as f:
            fieldnames = ['source1', 'source2', 'score', 'viability', 'common_fields']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for joinability in self.joinability_matrix.values():
                writer.writerow({
                    'source1': joinability['source1'],
                    'source2': joinability['source2'],
                    'score': joinability['score'],
                    'viability': joinability['viability'],
                    'common_fields': ','.join(joinability['common_fields'])
                })

        # Save quality scorecards
        with open("C:/Projects/OSINT - Foresight/data_quality_scorecards.json", 'w') as f:
            json.dump(self.quality_scores, f, indent=2)

        # Save join examples
        with open("C:/Projects/OSINT - Foresight/join_examples.json", 'w') as f:
            json.dump(self.join_examples, f, indent=2)

        print("All results saved")

    def generate_report(self):
        """Generate Phase 2 report"""
        report = "# Phase 2: Schema Harmonization Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"

        report += "## Summary\n\n"
        report += f"- Sources analyzed: {len(self.field_mappings)}\n"
        report += f"- Joinability pairs: {len(self.joinability_matrix)}\n"

        high_viability = sum(1 for j in self.joinability_matrix.values() if j['viability'] == 'HIGH')
        report += f"- High-viability pairs: {high_viability}\n"
        report += f"- Join examples: {len(self.join_examples)}\n\n"

        report += "## Canonical Field Coverage\n\n"
        for source, mapping in sorted(self.field_mappings.items()):
            report += f"- **{source}**: {mapping['coverage']:.1f}% coverage\n"

        report += "\n## Quality Scores\n\n"
        report += "| Source | Completeness | Consistency | Validity | Overall |\n"
        report += "|--------|--------------|-------------|----------|---------|\n"

        for source, scores in sorted(self.quality_scores.items()):
            report += f"| {source} | {scores['completeness']} | {scores['consistency']} | "
            report += f"{scores['validity']} | {scores['overall']} |\n"

        report += "\n## Compliance Status\n\n"
        report += "- ✅ Canonical field definitions created\n"
        report += "- ✅ Joinability matrix computed\n"
        report += "- ✅ Quality scorecards (0-100) generated\n"
        report += f"- {'✅' if len(self.join_examples) >= 10 else '⚠️'} Join examples: {len(self.join_examples)}\n"

        with open("C:/Projects/OSINT - Foresight/phase2_harmonization_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print("\nReport saved: phase2_harmonization_report.md")

    def run(self):
        """Execute Phase 2 schema harmonization"""
        print("\n" + "="*70)
        print("PHASE 2: SCHEMA HARMONIZATION")
        print("="*70)

        # Analyze schemas and create mappings
        self.analyze_schemas()

        # Calculate joinability
        self.calculate_joinability()

        # Generate join examples
        self.generate_join_examples()

        # Calculate quality scores
        self.calculate_quality_scores()

        # Save results
        self.save_results()

        # Generate report
        self.generate_report()

        print("\n" + "="*70)
        print("PHASE 2 COMPLETE")
        print("="*70)

        return 0


if __name__ == "__main__":
    harmonizer = SchemaHarmonizer()
    sys.exit(harmonizer.run())
