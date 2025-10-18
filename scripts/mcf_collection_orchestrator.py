#!/usr/bin/env python3
"""
MCF Collection Orchestrator
Coordinates Military-Civil Fusion intelligence collection across all sources
Based on MCF_COLLECTION_IMPLEMENTATION_PLAN.md
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collectors.mcf_base_collector import MCFBaseCollector
from collectors.state_dept_mcf_collector import StateDeptMCFCollector
from collectors.aspi_mcf_collector import ASPIMCFCollector
from collectors.ndu_cscma_collector import NDUCSCMACollector
from collectors.casi_mcf_collector import CASIMCFCollector
from collectors.uscc_mcf_collector import USCCMCFCollector
from collectors.cset_mcf_collector import CSETMCFCollector
from collectors.merics_mcf_collector import MERICSMCFCollector
from collectors.rand_mcf_collector import RANDMCFCollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCFCollectionOrchestrator:
    """Orchestrates MCF intelligence collection across all sources"""

    def __init__(self, warehouse_path: str = "F:/OSINT_WAREHOUSE/osint_research.db"):
        self.warehouse_path = warehouse_path
        self.base_collector = MCFBaseCollector(warehouse_path)

        # Initialize collectors for each tier
        self.tier1_collectors = {
            'state_dept': StateDeptMCFCollector(),
            'aspi': ASPIMCFCollector(),
            'ndu_cscma': NDUCSCMACollector(),
            'casi': CASIMCFCollector(),
            'uscc': USCCMCFCollector()
        }

        # Initialize Tier 2 collectors (Phase 2)
        self.tier2_collectors = {
            'cset': CSETMCFCollector(),
            'merics': MERICSMCFCollector(),
            'rand': RANDMCFCollector()
        }

        # Collection phases from implementation plan
        self.collection_phases = {
            'phase1': {
                'name': 'MCF Core Sources',
                'priority': 'HIGHEST',
                'collectors': ['state_dept', 'aspi', 'ndu_cscma', 'casi', 'uscc'],
                'target_docs': 500,
                'expected_high_relevance': 300
            },
            'phase2': {
                'name': 'Technology Pathways',
                'priority': 'HIGH',
                'collectors': ['cset', 'merics', 'rand'],  # CSIS, Jamestown pending
                'target_docs': 400,
                'expected_high_relevance': 250
            },
            'phase3': {
                'name': 'Supply Chain Mapping',
                'priority': 'HIGH',
                'collectors': [],  # Atlantic Council, FDD, RUSI, Wilson, Carnegie
                'target_docs': 250,
                'expected_high_relevance': 150
            },
            'phase4': {
                'name': 'Regional Integration',
                'priority': 'MEDIUM',
                'collectors': [],  # FOI, Arctic Institute, CEIAS, NBR
                'target_docs': 200,
                'expected_high_relevance': 100
            }
        }

        # Output directory for reports
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_orchestrated")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_phase_collection(self, phase_name: str) -> Dict:
        """Run collection for a specific phase"""
        if phase_name not in self.collection_phases:
            raise ValueError(f"Unknown phase: {phase_name}")

        phase_config = self.collection_phases[phase_name]
        logger.info(f"Starting {phase_config['name']} collection (Priority: {phase_config['priority']})")

        phase_results = {
            'phase': phase_name,
            'phase_name': phase_config['name'],
            'start_time': datetime.now().isoformat(),
            'collector_results': {},
            'phase_stats': {
                'total_documents': 0,
                'high_relevance_docs': 0,
                'unique_entities': 0,
                'errors': 0
            }
        }

        # Get initial database stats
        initial_stats = self.base_collector.get_mcf_statistics()

        # Run each collector in the phase
        for collector_name in phase_config['collectors']:
            # Check both tier1 and tier2 collectors
            if collector_name in self.tier1_collectors:
                collector = self.tier1_collectors[collector_name]
            elif collector_name in self.tier2_collectors:
                collector = self.tier2_collectors[collector_name]
            else:
                logger.warning(f"Collector {collector_name} not available yet")
                continue

            try:
                logger.info(f"Running {collector_name} collector...")
                # collector variable is already set above

                collector_results = collector.collect_all_mcf_content()
                phase_results['collector_results'][collector_name] = collector_results

                # Update phase statistics
                phase_stats = collector_results.get('collection_stats', {})
                phase_results['phase_stats']['total_documents'] += phase_stats.get('total_documents', 0)
                phase_results['phase_stats']['high_relevance_docs'] += phase_stats.get('high_relevance_docs', 0)
                phase_results['phase_stats']['errors'] += phase_stats.get('errors', 0)

                logger.info(f"Completed {collector_name}: {phase_stats.get('total_documents', 0)} documents collected")

            except Exception as e:
                logger.error(f"Error running {collector_name} collector: {e}")
                phase_results['phase_stats']['errors'] += 1

        # Get final database stats
        final_stats = self.base_collector.get_mcf_statistics()
        phase_results['database_growth'] = {
            'documents_added': final_stats.get('total_documents', 0) - initial_stats.get('total_documents', 0),
            'entities_added': final_stats.get('total_entities', 0) - initial_stats.get('total_entities', 0)
        }

        phase_results['end_time'] = datetime.now().isoformat()

        # Analyze entity extraction across phase
        unique_entities = self.analyze_phase_entities(phase_results)
        phase_results['phase_stats']['unique_entities'] = len(unique_entities)

        logger.info(f"""
{phase_config['name']} Collection Complete:
- Documents collected: {phase_results['phase_stats']['total_documents']}
- High relevance (>0.7): {phase_results['phase_stats']['high_relevance_docs']}
- Unique entities: {phase_results['phase_stats']['unique_entities']}
- Database documents added: {phase_results['database_growth']['documents_added']}
- Database entities added: {phase_results['database_growth']['entities_added']}
        """)

        return phase_results

    def analyze_phase_entities(self, phase_results: Dict) -> List[str]:
        """Analyze entities extracted across all collectors in a phase"""
        all_entities = set()

        for collector_name, collector_results in phase_results['collector_results'].items():
            documents = collector_results.get('documents', [])
            for doc in documents:
                entities = doc.get('entities', {})
                for entity_type, entity_list in entities.items():
                    all_entities.update(entity_list)

        return list(all_entities)

    def run_comprehensive_collection(self, phases: List[str] = None) -> Dict:
        """Run comprehensive MCF collection across specified phases"""
        if phases is None:
            phases = ['phase1']  # Start with Phase 1 only (Tier 1 sources)

        logger.info(f"Starting comprehensive MCF collection for phases: {phases}")

        comprehensive_results = {
            'collection_session': {
                'start_time': datetime.now().isoformat(),
                'phases_planned': phases,
                'total_target_docs': sum(self.collection_phases[p]['target_docs'] for p in phases),
                'orchestrator_version': '1.0'
            },
            'phase_results': {},
            'session_summary': {}
        }

        # Get initial overall statistics
        initial_db_stats = self.base_collector.get_mcf_statistics()

        # Run each phase sequentially
        for phase_name in phases:
            try:
                phase_results = self.run_phase_collection(phase_name)
                comprehensive_results['phase_results'][phase_name] = phase_results

            except Exception as e:
                logger.error(f"Failed to complete {phase_name}: {e}")
                comprehensive_results['phase_results'][phase_name] = {
                    'error': str(e),
                    'status': 'failed'
                }

        # Generate session summary
        comprehensive_results['session_summary'] = self.generate_session_summary(
            comprehensive_results, initial_db_stats
        )

        comprehensive_results['collection_session']['end_time'] = datetime.now().isoformat()

        # Save comprehensive results
        self.save_collection_results(comprehensive_results)

        return comprehensive_results

    def generate_session_summary(self, comprehensive_results: Dict, initial_db_stats: Dict) -> Dict:
        """Generate comprehensive session summary"""
        final_db_stats = self.base_collector.get_mcf_statistics()

        session_summary = {
            'total_phases_completed': len([p for p in comprehensive_results['phase_results'].values() if 'error' not in p]),
            'total_documents_collected': 0,
            'total_high_relevance_docs': 0,
            'total_errors': 0,
            'database_growth': {
                'documents_added': final_db_stats.get('total_documents', 0) - initial_db_stats.get('total_documents', 0),
                'entities_added': final_db_stats.get('total_entities', 0) - initial_db_stats.get('total_entities', 0)
            },
            'collectors_run': [],
            'top_entities_by_type': {},
            'mcf_relevance_distribution': {}
        }

        # Aggregate statistics across all phases
        for phase_name, phase_results in comprehensive_results['phase_results'].items():
            if 'error' in phase_results:
                continue

            phase_stats = phase_results.get('phase_stats', {})
            session_summary['total_documents_collected'] += phase_stats.get('total_documents', 0)
            session_summary['total_high_relevance_docs'] += phase_stats.get('high_relevance_docs', 0)
            session_summary['total_errors'] += phase_stats.get('errors', 0)

            # Track collectors used
            for collector_name in phase_results.get('collector_results', {}):
                if collector_name not in session_summary['collectors_run']:
                    session_summary['collectors_run'].append(collector_name)

        # Query database for entity distribution
        session_summary['top_entities_by_type'] = self.get_entity_distribution()

        # Calculate success metrics
        session_summary['success_metrics'] = {
            'target_achievement': {
                'documents': session_summary['total_documents_collected'] / comprehensive_results['collection_session']['total_target_docs'] if comprehensive_results['collection_session']['total_target_docs'] > 0 else 0,
                'high_relevance_rate': session_summary['total_high_relevance_docs'] / session_summary['total_documents_collected'] if session_summary['total_documents_collected'] > 0 else 0
            },
            'error_rate': session_summary['total_errors'] / max(session_summary['total_documents_collected'], 1),
            'entities_per_document': session_summary['database_growth']['entities_added'] / max(session_summary['database_growth']['documents_added'], 1)
        }

        return session_summary

    def get_entity_distribution(self) -> Dict:
        """Get distribution of entities by type from database"""
        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            # Get top entities by type
            cursor.execute("""
                SELECT type, name, COUNT(*) as frequency
                FROM mcf_entities
                GROUP BY type, name
                ORDER BY type, frequency DESC
            """)

            entity_distribution = {}
            for row in cursor.fetchall():
                entity_type, name, frequency = row
                if entity_type not in entity_distribution:
                    entity_distribution[entity_type] = []

                if len(entity_distribution[entity_type]) < 10:  # Top 10 per type
                    entity_distribution[entity_type].append({
                        'name': name,
                        'frequency': frequency
                    })

            conn.close()
            return entity_distribution

        except Exception as e:
            logger.error(f"Error getting entity distribution: {e}")
            return {}

    def save_collection_results(self, results: Dict):
        """Save collection results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_dir / f"mcf_comprehensive_collection_{timestamp}.json"

        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Comprehensive collection results saved to: {results_file}")

            # Also save a summary report
            summary_file = self.output_dir / f"mcf_collection_summary_{timestamp}.md"
            self.generate_markdown_summary(results, summary_file)

        except Exception as e:
            logger.error(f"Error saving collection results: {e}")

    def generate_markdown_summary(self, results: Dict, output_file: Path):
        """Generate human-readable markdown summary"""
        session = results['collection_session']
        summary = results['session_summary']

        markdown_content = f"""# MCF Collection Session Summary

**Date**: {session['start_time'][:10]}
**Duration**: {session['start_time']} to {session['end_time']}
**Phases**: {', '.join(session['phases_planned'])}

## 📊 Collection Results

### Overall Statistics
- **Documents Collected**: {summary['total_documents_collected']}
- **High Relevance Documents**: {summary['total_high_relevance_docs']} ({summary['success_metrics']['target_achievement']['high_relevance_rate']:.1%})
- **Database Growth**: +{summary['database_growth']['documents_added']} documents, +{summary['database_growth']['entities_added']} entities
- **Collectors Used**: {', '.join(summary['collectors_run'])}

### Success Metrics
- **Target Achievement**: {summary['success_metrics']['target_achievement']['documents']:.1%}
- **High Relevance Rate**: {summary['success_metrics']['target_achievement']['high_relevance_rate']:.1%}
- **Error Rate**: {summary['success_metrics']['error_rate']:.1%}
- **Entities per Document**: {summary['success_metrics']['entities_per_document']:.1f}

## 🎯 Phase Results

"""

        for phase_name, phase_results in results['phase_results'].items():
            if 'error' in phase_results:
                markdown_content += f"### {phase_name.upper()}: FAILED\n**Error**: {phase_results['error']}\n\n"
                continue

            phase_stats = phase_results['phase_stats']
            markdown_content += f"""### {phase_name.upper()}: {phase_results['phase_name']}
- **Documents**: {phase_stats['total_documents']}
- **High Relevance**: {phase_stats['high_relevance_docs']}
- **Unique Entities**: {phase_stats['unique_entities']}
- **Errors**: {phase_stats['errors']}

"""

        # Add entity distribution
        markdown_content += "## 🏢 Top Entities by Type\n\n"
        for entity_type, entities in summary['top_entities_by_type'].items():
            markdown_content += f"### {entity_type.title()}\n"
            for entity in entities[:5]:  # Top 5 per type
                markdown_content += f"- **{entity['name']}** ({entity['frequency']} occurrences)\n"
            markdown_content += "\n"

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Markdown summary saved to: {output_file}")

def main():
    """Run MCF collection orchestrator"""
    orchestrator = MCFCollectionOrchestrator()

    # Start with Phase 1 (Tier 1 sources only)
    logger.info("Starting MCF Collection Orchestrator - Phase 1 (Tier 1 Sources)")

    try:
        results = orchestrator.run_comprehensive_collection(phases=['phase1'])

        # Print summary
        summary = results['session_summary']
        print(f"""
MCF Collection Phase 1 Complete:
=====================================
Documents Collected: {summary['total_documents_collected']}
High Relevance Documents: {summary['total_high_relevance_docs']}
Database Growth: +{summary['database_growth']['documents_added']} docs, +{summary['database_growth']['entities_added']} entities
Success Rate: {summary['success_metrics']['target_achievement']['documents']:.1%}
Collectors: {', '.join(summary['collectors_run'])}

Next Steps:
- Implement remaining Tier 1 collectors (NDU CSCMA, CASI, USCC)
- Deploy Phase 2 (Technology Pathways) collectors
- Expand to Phase 3 (Supply Chain Mapping)
        """)

    except Exception as e:
        logger.error(f"MCF collection orchestrator failed: {e}")
        raise

if __name__ == "__main__":
    main()
