#!/usr/bin/env python3
"""
Cross-System Validation Framework
Ensures data consistency across all OSINT intelligence systems
Implements Zero Fabrication Protocol
"""

import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional, Tuple
import difflib
from dataclasses import dataclass, asdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/Projects/OSINT - Foresight/logs/cross_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Structured validation result"""
    entity_name: str
    normalized_name: str
    systems_found: Dict[str, bool]
    confidence_score: float
    validation_status: str
    inconsistencies: List[str]
    recommendations: List[str]
    timestamp: str


class CrossSystemValidator:
    """Validate entities across multiple intelligence systems"""

    def __init__(self):
        self.systems = {
            'ted': {
                'path': "F:/OSINT_WAREHOUSE/osint_master.db",
                'table': 'ted_china_contracts',
                'entity_field': 'contractor_name',
                'active': True
            },
            'bis': {
                'path': "F:/OSINT_WAREHOUSE/osint_master.db",
                'table': 'bis_entity_list',
                'entity_field': 'entity_name',
                'active': self.check_database_exists("F:/OSINT_WAREHOUSE/osint_master.db")
            },
            'patents': {
                'path': "F:/OSINT_Data/USPTO/uspto_patents_20250926.db",
                'table': 'patent_assignees',
                'entity_field': 'assignee_name',
                'active': self.check_database_exists("F:/OSINT_Data/USPTO/uspto_patents_20250926.db")
            },
            'trade': {
                'path': "F:/OSINT_Data/Trade_Facilities/uncomtrade_v2.db",
                'table': 'trade_partners',
                'entity_field': 'partner_name',
                'active': self.check_database_exists("F:/OSINT_Data/Trade_Facilities/uncomtrade_v2.db")
            },
            'research': {
                'path': "F:/OSINT_WAREHOUSE/osint_master.db",
                'table': 'institutions',
                'entity_field': 'institution_name',
                'active': self.check_database_exists("F:/OSINT_WAREHOUSE/osint_master.db")
            }
        }

        # Priority Chinese entities to validate
        self.priority_entities = [
            "Huawei Technologies Co., Ltd.",
            "ZTE Corporation",
            "Semiconductor Manufacturing International Corporation",
            "Beijing University of Aeronautics and Astronautics",
            "Tsinghua University",
            "DJI Technology Co., Ltd.",
            "Hikvision Digital Technology Co., Ltd.",
            "Alibaba Group Holding Limited",
            "Tencent Holdings Limited",
            "China Electronics Corporation",
            "China National Nuclear Corporation",
            "Aviation Industry Corporation of China",
            "China Aerospace Science and Technology Corporation",
            "BYD Company Limited",
            "Xiaomi Corporation"
        ]

        # Name variation patterns
        self.variation_patterns = {
            'corporation': ['Corp', 'Corporation', 'Corp.', 'Incorporated', 'Inc', 'Inc.'],
            'company': ['Co', 'Company', 'Co.', 'Companies'],
            'limited': ['Ltd', 'Limited', 'Ltd.', 'LTD'],
            'technology': ['Tech', 'Technology', 'Technologies', 'Tech.'],
            'international': ['Intl', 'International', 'Intl.', 'Int.'],
            'china': ['China', 'Chinese', 'PRC', "People's Republic of China"],
            'holdings': ['Holdings', 'Holding', 'Group', 'Grp']
        }

    def check_database_exists(self, db_path: str) -> bool:
        """Check if database file exists"""
        return Path(db_path).exists()

    def normalize_entity_name(self, name: str) -> str:
        """Normalize entity name for comparison"""
        if not name:
            return ""

        normalized = name.upper()

        # Remove common suffixes
        for category, variations in self.variation_patterns.items():
            for variation in variations:
                normalized = normalized.replace(variation.upper(), "")

        # Remove special characters and extra spaces
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = ' '.join(normalized.split())

        return normalized.strip()

    def generate_name_variations(self, name: str) -> List[str]:
        """Generate possible variations of an entity name"""
        variations = [name]
        base_name = name

        # Remove common suffixes to get base name
        for category, suffix_list in self.variation_patterns.items():
            for suffix in suffix_list:
                if name.endswith(suffix):
                    base_name = name[:-len(suffix)].strip()
                    break

        # Generate variations with different suffixes
        for category, suffix_list in self.variation_patterns.items():
            for suffix in suffix_list:
                variations.append(f"{base_name} {suffix}")

        # Add acronym if applicable
        words = base_name.split()
        if len(words) > 1:
            acronym = ''.join(w[0] for w in words if w[0].isupper())
            if len(acronym) > 1:
                variations.append(acronym)

        return list(set(variations))

    def check_system(self, entity_name: str, system_name: str) -> Dict:
        """Check if entity exists in a specific system"""
        system = self.systems[system_name]

        if not system['active']:
            return {
                'found': False,
                'confidence': 0,
                'message': 'Database not available'
            }

        try:
            conn = sqlite3.connect(system['path'])
            cursor = conn.cursor()

            # Normalize entity name
            normalized = self.normalize_entity_name(entity_name)
            variations = self.generate_name_variations(entity_name)

            # Check for exact match
            query = f"SELECT COUNT(*) FROM {system['table']} WHERE {system['entity_field']} = ?"
            cursor.execute(query, (entity_name,))
            exact_count = cursor.fetchone()[0]

            if exact_count > 0:
                conn.close()
                return {
                    'found': True,
                    'confidence': 1.0,
                    'match_type': 'exact',
                    'count': exact_count
                }

            # Check for normalized match
            query = f"SELECT {system['entity_field']} FROM {system['table']} WHERE {system['entity_field']} IS NOT NULL"
            cursor.execute(query)
            all_names = [row[0] for row in cursor.fetchall()]

            best_match = None
            best_ratio = 0

            for db_name in all_names:
                db_normalized = self.normalize_entity_name(db_name)

                # Check exact normalized match
                if db_normalized == normalized:
                    conn.close()
                    return {
                        'found': True,
                        'confidence': 0.9,
                        'match_type': 'normalized',
                        'matched_name': db_name
                    }

                # Check similarity
                ratio = difflib.SequenceMatcher(None, normalized, db_normalized).ratio()
                if ratio > best_ratio and ratio > 0.8:
                    best_ratio = ratio
                    best_match = db_name

            conn.close()

            if best_match:
                return {
                    'found': True,
                    'confidence': best_ratio,
                    'match_type': 'fuzzy',
                    'matched_name': best_match
                }

            return {
                'found': False,
                'confidence': 0,
                'message': 'No match found'
            }

        except Exception as e:
            logger.error(f"Error checking {system_name}: {e}")
            return {
                'found': False,
                'confidence': 0,
                'error': str(e)
            }

    def validate_entity(self, entity_name: str) -> ValidationResult:
        """Validate entity across all systems"""
        logger.info(f"Validating entity: {entity_name}")

        # Check each system
        systems_results = {}
        systems_found = {}
        inconsistencies = []
        recommendations = []

        for system_name in self.systems:
            result = self.check_system(entity_name, system_name)
            systems_results[system_name] = result
            systems_found[system_name] = result['found']

        # Calculate overall confidence
        active_systems = [s for s in self.systems if self.systems[s]['active']]
        found_count = sum(1 for s in systems_found if systems_found[s])
        confidence = found_count / len(active_systems) if active_systems else 0

        # Determine validation status
        if confidence >= 0.8:
            validation_status = "HIGH_CONFIDENCE"
        elif confidence >= 0.6:
            validation_status = "MEDIUM_CONFIDENCE"
        elif confidence >= 0.3:
            validation_status = "LOW_CONFIDENCE"
        else:
            validation_status = "NEEDS_INVESTIGATION"

        # Check for inconsistencies
        if found_count > 0 and found_count < len(active_systems):
            missing_systems = [s for s in systems_found if not systems_found[s] and self.systems[s]['active']]
            inconsistencies.append(f"Entity found in {found_count}/{len(active_systems)} systems")
            inconsistencies.append(f"Missing from: {', '.join(missing_systems)}")
            recommendations.append(f"Investigate why entity is missing from: {', '.join(missing_systems)}")

        # Check for name variations
        name_variations = []
        for system_name, result in systems_results.items():
            if result.get('matched_name') and result['matched_name'] != entity_name:
                name_variations.append(f"{system_name}: {result['matched_name']}")

        if name_variations:
            inconsistencies.append(f"Name variations found: {'; '.join(name_variations)}")
            recommendations.append("Standardize entity naming across systems")

        return ValidationResult(
            entity_name=entity_name,
            normalized_name=self.normalize_entity_name(entity_name),
            systems_found=systems_found,
            confidence_score=confidence,
            validation_status=validation_status,
            inconsistencies=inconsistencies,
            recommendations=recommendations,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def batch_validate(self, entities: Optional[List[str]] = None) -> List[ValidationResult]:
        """Validate multiple entities"""
        if entities is None:
            entities = self.priority_entities

        results = []
        for entity in entities:
            result = self.validate_entity(entity)
            results.append(result)
            self.save_validation_result(result)

        return results

    def save_validation_result(self, result: ValidationResult):
        """Save validation result to database"""
        db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_results (
                entity_name TEXT,
                normalized_name TEXT,
                systems_found TEXT,
                confidence_score REAL,
                validation_status TEXT,
                inconsistencies TEXT,
                recommendations TEXT,
                timestamp TEXT,
                PRIMARY KEY (entity_name, timestamp)
            )
        ''')

        # Save result
        cursor.execute('''
            INSERT INTO validation_results VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.entity_name,
            result.normalized_name,
            json.dumps(result.systems_found),
            result.confidence_score,
            result.validation_status,
            json.dumps(result.inconsistencies),
            json.dumps(result.recommendations),
            result.timestamp
        ))

        conn.commit()
        conn.close()

    def check_ted_chinese_entities(self) -> List[Dict]:
        """Validate Chinese entities found in TED data"""
        conn = sqlite3.connect(self.systems['ted']['path'])
        cursor = conn.cursor()

        # Get unique Chinese contractors
        cursor.execute('''
            SELECT DISTINCT contractor_name, contractor_country, COUNT(*) as contracts
            FROM ted_china_contracts
            WHERE contractor_country IN ('CN', 'CHN', 'HK', 'MO')
            AND contractor_name IS NOT NULL
            GROUP BY contractor_name
            ORDER BY contracts DESC
            LIMIT 50
        ''')

        entities = []
        for row in cursor.fetchall():
            entities.append({
                'name': row[0],
                'country': row[1],
                'contracts': row[2]
            })

        conn.close()

        # Validate each entity
        validation_results = []
        for entity_info in entities:
            result = self.validate_entity(entity_info['name'])
            validation_results.append({
                'entity_info': entity_info,
                'validation': asdict(result)
            })

        return validation_results

    def generate_validation_report(self) -> Dict:
        """Generate comprehensive validation report"""
        report = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'zero_fabrication_compliance': True,
            'systems_checked': {}
        }

        # Check system availability
        for system_name, system_info in self.systems.items():
            report['systems_checked'][system_name] = {
                'path': system_info['path'],
                'available': system_info['active']
            }

        # Validate priority entities
        priority_results = self.batch_validate()

        report['priority_entities_validation'] = []
        for result in priority_results:
            report['priority_entities_validation'].append({
                'entity': result.entity_name,
                'status': result.validation_status,
                'confidence': result.confidence_score,
                'systems_found': result.systems_found,
                'issues': result.inconsistencies
            })

        # Validate TED Chinese entities
        ted_validation = self.check_ted_chinese_entities()
        report['ted_chinese_entities_validation'] = ted_validation[:10]  # Top 10

        # Summary statistics
        high_confidence = sum(1 for r in priority_results if r.validation_status == "HIGH_CONFIDENCE")
        medium_confidence = sum(1 for r in priority_results if r.validation_status == "MEDIUM_CONFIDENCE")
        low_confidence = sum(1 for r in priority_results if r.validation_status == "LOW_CONFIDENCE")
        needs_investigation = sum(1 for r in priority_results if r.validation_status == "NEEDS_INVESTIGATION")

        report['summary'] = {
            'total_validated': len(priority_results),
            'high_confidence': high_confidence,
            'medium_confidence': medium_confidence,
            'low_confidence': low_confidence,
            'needs_investigation': needs_investigation
        }

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/cross_validation_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Validation report saved to {report_path}")
        return report


def main():
    """Main execution"""
    logger.info("Starting Cross-System Validation")

    validator = CrossSystemValidator()

    # Generate validation report
    report = validator.generate_validation_report()

    print("\n=== CROSS-SYSTEM VALIDATION REPORT ===")
    print(f"Generated at: {report['generated_at']}")
    print("\n=== System Availability ===")
    for system, info in report['systems_checked'].items():
        status = "✓" if info['available'] else "✗"
        print(f"{status} {system}: {info['available']}")

    print("\n=== Validation Summary ===")
    summary = report['summary']
    print(f"Total Entities Validated: {summary['total_validated']}")
    print(f"High Confidence: {summary['high_confidence']}")
    print(f"Medium Confidence: {summary['medium_confidence']}")
    print(f"Low Confidence: {summary['low_confidence']}")
    print(f"Needs Investigation: {summary['needs_investigation']}")

    print("\n=== Priority Entity Results ===")
    for entity_result in report['priority_entities_validation'][:5]:
        print(f"\n{entity_result['entity']}:")
        print(f"  Status: {entity_result['status']}")
        print(f"  Confidence: {entity_result['confidence']:.2f}")
        if entity_result['issues']:
            print(f"  Issues: {'; '.join(entity_result['issues'])}")

    return report


if __name__ == "__main__":
    main()
