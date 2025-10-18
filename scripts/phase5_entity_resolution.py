#!/usr/bin/env python3
"""
Phase 5: Entity Resolution & Timeline Construction
Build entity registry, resolve duplicates, and create event timelines
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher
import pandas as pd

class EntityResolver:
    def __init__(self):
        self.entity_registry = {}
        self.entity_aliases = defaultdict(set)
        self.entity_timelines = defaultdict(list)
        self.resolution_log = []

        self.resolution_results = {
            'generated': datetime.now().isoformat(),
            'entities_discovered': 0,
            'duplicates_resolved': 0,
            'timelines_created': 0,
            'cross_references': 0
        }

    def normalize_entity_name(self, name):
        """Normalize entity name for matching"""
        if not name:
            return ""

        # Convert to uppercase
        name = name.upper()

        # Remove common suffixes
        suffixes = [
            ' LTD', ' LIMITED', ' LLC', ' INC', ' CORP', ' CORPORATION',
            ' GMBH', ' AG', ' SA', ' SPA', ' SRL', ' BV', ' NV',
            ' CO', ' COMPANY', ' GROUP', ' HOLDINGS', ' INTERNATIONAL'
        ]

        for suffix in suffixes:
            name = name.replace(suffix, '')

        # Remove punctuation
        name = re.sub(r'[^\w\s]', ' ', name)

        # Normalize whitespace
        name = ' '.join(name.split())

        return name

    def calculate_similarity(self, name1, name2):
        """Calculate similarity score between two entity names"""
        norm1 = self.normalize_entity_name(name1)
        norm2 = self.normalize_entity_name(name2)

        if not norm1 or not norm2:
            return 0

        # Exact match after normalization
        if norm1 == norm2:
            return 1.0

        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, norm1, norm2).ratio()

    def extract_entities_from_cordis(self):
        """Extract entities from CORDIS database"""
        print("Extracting entities from CORDIS...")

        cordis_db = Path("data/processed/cordis_unified/cordis_china_projects.db")
        if not cordis_db.exists():
            return

        conn = sqlite3.connect(cordis_db)
        cursor = conn.cursor()

        # Get organizations
        try:
            cursor.execute("""
                SELECT DISTINCT coordinator_name, coordinator_country,
                       coordinator_type, project_id, start_date
                FROM projects
                WHERE coordinator_name IS NOT NULL
            """)

            for name, country, org_type, project_id, start_date in cursor.fetchall():
                entity_id = self.get_or_create_entity(name, 'organization', country)

                # Add to timeline
                if start_date:
                    self.entity_timelines[entity_id].append({
                        'date': start_date,
                        'event_type': 'project_start',
                        'source': 'CORDIS',
                        'project_id': project_id,
                        'details': f"Started project {project_id}"
                    })

                # Store metadata
                if entity_id not in self.entity_registry:
                    self.entity_registry[entity_id] = {
                        'canonical_name': name,
                        'type': 'organization',
                        'country': country,
                        'org_type': org_type,
                        'sources': set(['CORDIS']),
                        'first_seen': start_date,
                        'last_seen': start_date
                    }
                else:
                    self.entity_registry[entity_id]['sources'].add('CORDIS')
                    if start_date:
                        if not self.entity_registry[entity_id]['first_seen'] or start_date < self.entity_registry[entity_id]['first_seen']:
                            self.entity_registry[entity_id]['first_seen'] = start_date
                        if not self.entity_registry[entity_id]['last_seen'] or start_date > self.entity_registry[entity_id]['last_seen']:
                            self.entity_registry[entity_id]['last_seen'] = start_date

        except Exception as e:
            print(f"Error extracting CORDIS entities: {e}")

        conn.close()

    def extract_entities_from_json(self):
        """Extract entities from JSON files"""
        print("Extracting entities from JSON files...")

        json_pattern = Path("data/processed").rglob("*china*.json")

        for json_file in list(json_pattern)[:10]:  # Process first 10 files
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if isinstance(data, list):
                    for item in data[:100]:  # Sample first 100 items
                        self.extract_entity_from_dict(item, str(json_file))
                elif isinstance(data, dict):
                    if 'organizations' in data:
                        for org in data['organizations'][:100]:
                            self.extract_entity_from_dict(org, str(json_file))
                    elif 'entities' in data:
                        for entity in data['entities'][:100]:
                            self.extract_entity_from_dict(entity, str(json_file))

            except Exception as e:
                print(f"Error processing {json_file}: {e}")

    def extract_entity_from_dict(self, item, source):
        """Extract entity from dictionary item"""
        # Look for name fields
        name_fields = ['name', 'organization', 'company', 'institution', 'org_name', 'entity_name']
        name = None

        for field in name_fields:
            if field in item and item[field]:
                name = item[field]
                break

        if name:
            # Determine entity type
            entity_type = 'organization'
            if 'type' in item:
                entity_type = item['type']
            elif 'entity_type' in item:
                entity_type = item['entity_type']

            # Get country if available
            country = item.get('country') or item.get('country_code')

            entity_id = self.get_or_create_entity(name, entity_type, country)

            # Add timeline event if date available
            date_fields = ['date', 'publication_date', 'created_at', 'timestamp']
            for field in date_fields:
                if field in item and item[field]:
                    self.entity_timelines[entity_id].append({
                        'date': item[field],
                        'event_type': 'mention',
                        'source': Path(source).stem,
                        'details': f"Mentioned in {Path(source).name}"
                    })
                    break

    def get_or_create_entity(self, name, entity_type='organization', country=None):
        """Get existing entity ID or create new one"""
        normalized = self.normalize_entity_name(name)

        # Check for exact match
        for entity_id, entity in self.entity_registry.items():
            if self.normalize_entity_name(entity['canonical_name']) == normalized:
                # Add alias if different
                if name != entity['canonical_name']:
                    self.entity_aliases[entity_id].add(name)
                return entity_id

        # Check for fuzzy match
        best_match = None
        best_score = 0

        for entity_id, entity in self.entity_registry.items():
            score = self.calculate_similarity(name, entity['canonical_name'])
            if score > 0.85 and score > best_score:  # 85% similarity threshold
                best_match = entity_id
                best_score = score

        if best_match:
            # Found likely duplicate
            self.entity_aliases[best_match].add(name)
            self.resolution_log.append({
                'original': name,
                'resolved_to': self.entity_registry[best_match]['canonical_name'],
                'similarity': best_score,
                'method': 'fuzzy_match'
            })
            self.resolution_results['duplicates_resolved'] += 1
            return best_match

        # Create new entity
        entity_id = f"E{len(self.entity_registry):06d}"
        self.entity_registry[entity_id] = {
            'canonical_name': name,
            'type': entity_type,
            'country': country,
            'sources': set(),
            'first_seen': None,
            'last_seen': None
        }
        self.resolution_results['entities_discovered'] += 1

        return entity_id

    def resolve_cross_references(self):
        """Resolve cross-references between entities"""
        print("Resolving cross-references...")

        # Group entities by country and type for potential matches
        country_groups = defaultdict(list)
        for entity_id, entity in self.entity_registry.items():
            if entity['country']:
                country_groups[entity['country']].append(entity_id)

        # Check for related entities within same country
        for country, entities in country_groups.items():
            for i, entity1_id in enumerate(entities):
                for entity2_id in entities[i+1:]:
                    entity1 = self.entity_registry[entity1_id]
                    entity2 = self.entity_registry[entity2_id]

                    # Check if names are related (e.g., parent/subsidiary)
                    name1 = self.normalize_entity_name(entity1['canonical_name'])
                    name2 = self.normalize_entity_name(entity2['canonical_name'])

                    if name1 in name2 or name2 in name1:
                        # Potential parent/subsidiary relationship
                        self.resolution_log.append({
                            'type': 'potential_relationship',
                            'entity1': entity1['canonical_name'],
                            'entity2': entity2['canonical_name'],
                            'relationship': 'parent_subsidiary'
                        })
                        self.resolution_results['cross_references'] += 1

    def build_timelines(self):
        """Build consolidated timelines for entities"""
        print("Building entity timelines...")

        for entity_id, events in self.entity_timelines.items():
            if events:
                # Sort events by date
                sorted_events = sorted(events, key=lambda x: x['date'] if x['date'] else '1900-01-01')

                # Update entity first/last seen
                if sorted_events:
                    first_date = sorted_events[0]['date']
                    last_date = sorted_events[-1]['date']

                    if entity_id in self.entity_registry:
                        self.entity_registry[entity_id]['first_seen'] = first_date
                        self.entity_registry[entity_id]['last_seen'] = last_date
                        self.entity_registry[entity_id]['event_count'] = len(sorted_events)

                self.resolution_results['timelines_created'] += 1

    def generate_report(self):
        """Generate Phase 5 entity resolution report"""

        # Convert sets to lists for JSON serialization
        registry_serializable = {}
        for entity_id, entity in self.entity_registry.items():
            entity_copy = entity.copy()
            entity_copy['sources'] = list(entity_copy['sources']) if 'sources' in entity_copy else []
            entity_copy['aliases'] = list(self.entity_aliases[entity_id]) if entity_id in self.entity_aliases else []
            registry_serializable[entity_id] = entity_copy

        # Save entity registry
        with open("C:/Projects/OSINT - Foresight/entity_registry.json", 'w', encoding='utf-8') as f:
            json.dump(registry_serializable, f, indent=2, default=str)

        # Save resolution log
        with open("C:/Projects/OSINT - Foresight/entity_resolution_log.json", 'w', encoding='utf-8') as f:
            json.dump(self.resolution_log, f, indent=2)

        # Create entity summary CSV
        entity_data = []
        for entity_id, entity in self.entity_registry.items():
            entity_data.append({
                'ID': entity_id,
                'Name': entity['canonical_name'],
                'Type': entity['type'],
                'Country': entity['country'],
                'Sources': len(entity['sources']) if 'sources' in entity else 0,
                'Aliases': len(self.entity_aliases[entity_id]),
                'Events': entity.get('event_count', 0),
                'First_Seen': entity.get('first_seen'),
                'Last_Seen': entity.get('last_seen')
            })

        df = pd.DataFrame(entity_data)
        df.to_csv("C:/Projects/OSINT - Foresight/entity_summary.csv", index=False)

        # Generate markdown report
        report = f"""# Phase 5: Entity Resolution & Timeline Report

Generated: {self.resolution_results['generated']}

## Resolution Summary

| Metric | Value |
|--------|-------|
| Entities Discovered | {self.resolution_results['entities_discovered']:,} |
| Duplicates Resolved | {self.resolution_results['duplicates_resolved']:,} |
| Timelines Created | {self.resolution_results['timelines_created']:,} |
| Cross-References | {self.resolution_results['cross_references']:,} |

## Entity Statistics

### By Type
"""

        type_counts = defaultdict(int)
        for entity in self.entity_registry.values():
            type_counts[entity['type']] += 1

        for entity_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{entity_type}**: {count:,}\n"

        report += "\n### By Country (Top 10)\n"

        country_counts = defaultdict(int)
        for entity in self.entity_registry.values():
            if entity['country']:
                country_counts[entity['country']] += 1

        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"- **{country}**: {count:,}\n"

        report += "\n## Resolution Quality\n\n"

        if self.resolution_log:
            # Analyze resolution methods
            methods = defaultdict(int)
            for log_entry in self.resolution_log:
                if 'method' in log_entry:
                    methods[log_entry['method']] += 1

            report += "### Resolution Methods Used\n"
            for method, count in methods.items():
                report += f"- **{method}**: {count:,} cases\n"

            # Show sample resolutions
            report += "\n### Sample Resolutions\n"
            for entry in self.resolution_log[:5]:
                if 'original' in entry and 'resolved_to' in entry:
                    report += f"- \"{entry['original']}\" → \"{entry['resolved_to']}\" (similarity: {entry.get('similarity', 0):.2f})\n"

        report += "\n## Entity Timeline Coverage\n\n"

        entities_with_timeline = sum(1 for e in self.entity_registry.values() if e.get('event_count', 0) > 0)
        report += f"- Entities with timeline data: {entities_with_timeline:,}\n"
        report += f"- Total timeline events: {sum(e.get('event_count', 0) for e in self.entity_registry.values()):,}\n"

        # Find most active entities
        active_entities = sorted(
            [(id, e) for id, e in self.entity_registry.items()],
            key=lambda x: x[1].get('event_count', 0),
            reverse=True
        )[:10]

        if active_entities:
            report += "\n### Most Active Entities\n"
            for entity_id, entity in active_entities:
                if entity.get('event_count', 0) > 0:
                    report += f"- **{entity['canonical_name']}**: {entity.get('event_count', 0)} events\n"

        report += """
## Alias Resolution

"""

        # Count entities with aliases
        entities_with_aliases = sum(1 for aliases in self.entity_aliases.values() if len(aliases) > 0)
        total_aliases = sum(len(aliases) for aliases in self.entity_aliases.values())

        report += f"- Entities with aliases: {entities_with_aliases:,}\n"
        report += f"- Total aliases resolved: {total_aliases:,}\n"

        # Show entities with most aliases
        most_aliases = sorted(
            [(id, aliases) for id, aliases in self.entity_aliases.items()],
            key=lambda x: len(x[1]),
            reverse=True
        )[:5]

        if most_aliases:
            report += "\n### Entities with Most Aliases\n"
            for entity_id, aliases in most_aliases:
                if entity_id in self.entity_registry:
                    entity = self.entity_registry[entity_id]
                    report += f"- **{entity['canonical_name']}**: {len(aliases)} aliases\n"
                    for alias in list(aliases)[:3]:
                        report += f"  - {alias}\n"

        report += """
## Data Quality Indicators

✅ **Strengths**:
- Entity deduplication active
- Fuzzy matching with 85% threshold
- Timeline construction from multiple sources
- Cross-reference detection

⚠️ **Limitations**:
- Limited to sampled data
- May miss complex entity relationships
- Temporal data not available for all entities

## Artifacts Created

1. `entity_registry.json` - Complete entity registry with metadata
2. `entity_resolution_log.json` - Detailed resolution decisions
3. `entity_summary.csv` - Entity summary table
4. This report - Phase 5 documentation

## Phase 5 Complete ✓

Entity resolution accomplished with deduplication and timeline construction.
Ready for quality monitoring in Phase 6.
"""

        with open("C:/Projects/OSINT - Foresight/phase5_entity_resolution_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\nPhase 5 Complete!")
        print(f"- Entities discovered: {self.resolution_results['entities_discovered']:,}")
        print(f"- Duplicates resolved: {self.resolution_results['duplicates_resolved']:,}")
        print(f"- Reports saved: phase5_entity_resolution_report.md")

def main():
    resolver = EntityResolver()
    resolver.extract_entities_from_cordis()
    resolver.extract_entities_from_json()
    resolver.resolve_cross_references()
    resolver.build_timelines()
    resolver.generate_report()

if __name__ == "__main__":
    main()
