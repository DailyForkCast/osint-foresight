#!/usr/bin/env python3
"""
Enhanced MCF Collection Orchestrator with Selenium Support
Coordinates Military-Civil Fusion intelligence collection with Selenium for blocked sites
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

# Enhanced State Dept collector with dynamic URLs
try:
    from collectors.state_dept_mcf_collector_enhanced import StateDeptMCFCollectorEnhanced as StateDeptMCFCollector
    print("Using enhanced State Dept collector with dynamic URL discovery")
except ImportError:
    from collectors.state_dept_mcf_collector import StateDeptMCFCollector
    print("Using standard State Dept collector")

# Selenium-based ASPI collector to bypass 403 blocking
try:
    from collectors.aspi_selenium_collector import ASPISeleniumCollector as ASPIMCFCollector
    print("Using Selenium-based ASPI collector to bypass blocking")
except ImportError:
    from collectors.aspi_mcf_collector import ASPIMCFCollector
    print("WARNING: Using standard ASPI collector - may encounter 403 errors")

# Standard collectors
from collectors.ndu_cscma_collector import NDUCSCMACollector
from collectors.casi_mcf_collector import CASIMCFCollector
from collectors.uscc_mcf_collector import USCCMCFCollector
from collectors.cset_mcf_collector import CSETMCFCollector
from collectors.merics_mcf_collector import MERICSMCFCollector
from collectors.rand_mcf_collector import RANDMCFCollector

# Phase 3 collector (Atlantic Council)
try:
    from collectors.atlantic_council_mcf_collector import AtlanticCouncilMCFCollector
    phase3_available = True
except ImportError:
    phase3_available = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedMCFOrchestrator:
    """Enhanced orchestrator with Selenium support for blocked sites"""

    def __init__(self, warehouse_path: str = "F:/OSINT_WAREHOUSE/osint_research.db"):
        self.warehouse_path = warehouse_path
        self.base_collector = MCFBaseCollector(warehouse_path)

        # Initialize Tier 1 collectors with enhanced versions
        self.tier1_collectors = {
            'state_dept': StateDeptMCFCollector(),
            'aspi': ASPIMCFCollector(),  # Now using Selenium version
            'ndu_cscma': NDUCSCMACollector(),
            'casi': CASIMCFCollector(),
            'uscc': USCCMCFCollector()
        }

        # Initialize Tier 2 collectors
        self.tier2_collectors = {
            'cset': CSETMCFCollector(),
            'merics': MERICSMCFCollector(),
            'rand': RANDMCFCollector()
        }

        # Initialize Tier 3 collectors if available
        self.tier3_collectors = {}
        if phase3_available:
            self.tier3_collectors['atlantic_council'] = AtlanticCouncilMCFCollector()

        # Collection phases configuration
        self.collection_phases = {
            'phase1': {
                'name': 'MCF Core Sources (Enhanced)',
                'priority': 'HIGHEST',
                'collectors': self.tier1_collectors,
                'target_docs': 500,
                'expected_high_relevance': 300
            },
            'phase2': {
                'name': 'Technology Pathways',
                'priority': 'HIGH',
                'collectors': self.tier2_collectors,
                'target_docs': 400,
                'expected_high_relevance': 250
            },
            'phase3': {
                'name': 'Supply Chain Mapping',
                'priority': 'HIGH',
                'collectors': self.tier3_collectors,
                'target_docs': 250,
                'expected_high_relevance': 150
            }
        }

        # Output directory
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/mcf_enhanced")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Enhanced MCF Orchestrator initialized")
        logger.info(f"Tier 1: {len(self.tier1_collectors)} collectors (with Selenium ASPI)")
        logger.info(f"Tier 2: {len(self.tier2_collectors)} collectors")
        logger.info(f"Tier 3: {len(self.tier3_collectors)} collectors")

    def run_phase1_collection(self, test_mode: bool = False, limit_per_source: int = 20) -> Dict:
        """Run Phase 1 collection with enhanced collectors"""
        logger.info("Starting Phase 1: MCF Core Sources (Enhanced with Selenium)")

        phase_results = {
            'phase': 'phase1',
            'name': 'MCF Core Sources (Enhanced)',
            'timestamp': datetime.now().isoformat(),
            'collectors': {},
            'documents_collected': 0,
            'high_relevance_count': 0,
            'errors': []
        }

        for collector_name, collector in self.tier1_collectors.items():
            try:
                logger.info(f"Running {collector_name} collector...")

                # Special handling for ASPI Selenium collector
                if collector_name == 'aspi' and hasattr(collector, 'setup_driver'):
                    logger.info("Using Selenium automation for ASPI...")

                # Run collection with limits
                if hasattr(collector, 'run_collection'):
                    result = collector.run_collection(limit=limit_per_source)
                else:
                    result = {'documents_collected': 0, 'error': 'No run_collection method'}

                phase_results['collectors'][collector_name] = result
                phase_results['documents_collected'] += result.get('documents_collected', 0)
                phase_results['high_relevance_count'] += result.get('high_relevance', 0)

                logger.info(f"{collector_name}: {result.get('documents_collected', 0)} documents")

            except Exception as e:
                error_msg = f"Error in {collector_name}: {str(e)}"
                logger.error(error_msg)
                phase_results['errors'].append(error_msg)
                phase_results['collectors'][collector_name] = {'error': str(e)}

        # Save phase results
        self._save_phase_results(phase_results, 'phase1')

        logger.info(f"Phase 1 complete: {phase_results['documents_collected']} documents collected")
        logger.info(f"High relevance: {phase_results['high_relevance_count']} documents")

        return phase_results

    def run_phase2_collection(self, test_mode: bool = False, limit_per_source: int = 15) -> Dict:
        """Run Phase 2 Technology Pathways collection"""
        logger.info("Starting Phase 2: Technology Pathways")

        phase_results = {
            'phase': 'phase2',
            'name': 'Technology Pathways',
            'timestamp': datetime.now().isoformat(),
            'collectors': {},
            'documents_collected': 0,
            'high_relevance_count': 0,
            'errors': []
        }

        for collector_name, collector in self.tier2_collectors.items():
            try:
                logger.info(f"Running {collector_name} collector...")

                if hasattr(collector, 'run_collection'):
                    result = collector.run_collection(limit=limit_per_source)
                else:
                    result = {'documents_collected': 0, 'error': 'No run_collection method'}

                phase_results['collectors'][collector_name] = result
                phase_results['documents_collected'] += result.get('documents_collected', 0)
                phase_results['high_relevance_count'] += result.get('high_relevance', 0)

                logger.info(f"{collector_name}: {result.get('documents_collected', 0)} documents")

            except Exception as e:
                error_msg = f"Error in {collector_name}: {str(e)}"
                logger.error(error_msg)
                phase_results['errors'].append(error_msg)
                phase_results['collectors'][collector_name] = {'error': str(e)}

        # Save phase results
        self._save_phase_results(phase_results, 'phase2')

        logger.info(f"Phase 2 complete: {phase_results['documents_collected']} documents collected")
        return phase_results

    def run_phase3_collection(self, test_mode: bool = False, limit_per_source: int = 10) -> Dict:
        """Run Phase 3 Supply Chain Mapping collection"""
        logger.info("Starting Phase 3: Supply Chain Mapping")

        phase_results = {
            'phase': 'phase3',
            'name': 'Supply Chain Mapping',
            'timestamp': datetime.now().isoformat(),
            'collectors': {},
            'documents_collected': 0,
            'high_relevance_count': 0,
            'errors': []
        }

        if not self.tier3_collectors:
            logger.warning("No Phase 3 collectors available yet")
            phase_results['errors'].append("Phase 3 collectors not fully implemented")
            return phase_results

        for collector_name, collector in self.tier3_collectors.items():
            try:
                logger.info(f"Running {collector_name} collector...")

                if hasattr(collector, 'run_collection'):
                    result = collector.run_collection(limit=limit_per_source)
                else:
                    result = {'documents_collected': 0, 'error': 'No run_collection method'}

                phase_results['collectors'][collector_name] = result
                phase_results['documents_collected'] += result.get('documents_collected', 0)
                phase_results['high_relevance_count'] += result.get('high_relevance', 0)

                logger.info(f"{collector_name}: {result.get('documents_collected', 0)} documents")

            except Exception as e:
                error_msg = f"Error in {collector_name}: {str(e)}"
                logger.error(error_msg)
                phase_results['errors'].append(error_msg)
                phase_results['collectors'][collector_name] = {'error': str(e)}

        # Save phase results
        self._save_phase_results(phase_results, 'phase3')

        logger.info(f"Phase 3 complete: {phase_results['documents_collected']} documents collected")
        return phase_results

    def run_all_phases(self, test_mode: bool = False) -> Dict:
        """Run all collection phases"""
        logger.info("Starting enhanced MCF collection across all phases")

        all_results = {
            'timestamp': datetime.now().isoformat(),
            'phases': {},
            'total_documents': 0,
            'total_high_relevance': 0,
            'selenium_enabled': True
        }

        # Run each phase
        phase1_results = self.run_phase1_collection(test_mode=test_mode)
        all_results['phases']['phase1'] = phase1_results
        all_results['total_documents'] += phase1_results['documents_collected']
        all_results['total_high_relevance'] += phase1_results['high_relevance_count']

        phase2_results = self.run_phase2_collection(test_mode=test_mode)
        all_results['phases']['phase2'] = phase2_results
        all_results['total_documents'] += phase2_results['documents_collected']
        all_results['total_high_relevance'] += phase2_results['high_relevance_count']

        if self.tier3_collectors:
            phase3_results = self.run_phase3_collection(test_mode=test_mode)
            all_results['phases']['phase3'] = phase3_results
            all_results['total_documents'] += phase3_results['documents_collected']
            all_results['total_high_relevance'] += phase3_results['high_relevance_count']

        # Save combined results
        output_file = self.output_dir / f"enhanced_mcf_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        logger.info(f"All phases complete: {all_results['total_documents']} total documents")
        logger.info(f"High relevance: {all_results['total_high_relevance']} documents")
        logger.info(f"Results saved to: {output_file}")

        return all_results

    def _save_phase_results(self, results: Dict, phase_name: str):
        """Save phase results to file"""
        output_file = self.output_dir / f"{phase_name}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Phase results saved to: {output_file}")

    def get_collection_statistics(self) -> Dict:
        """Get statistics from the database"""
        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            # Get document counts by source
            cursor.execute("""
                SELECT source, COUNT(*) as count, AVG(relevance_score) as avg_relevance
                FROM mcf_documents
                GROUP BY source
            """)
            source_stats = cursor.fetchall()

            # Get entity counts
            cursor.execute("""
                SELECT entity_name, COUNT(*) as mention_count
                FROM mcf_entities
                GROUP BY entity_name
                ORDER BY mention_count DESC
                LIMIT 20
            """)
            top_entities = cursor.fetchall()

            conn.close()

            return {
                'source_statistics': source_stats,
                'top_entities': top_entities,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}


def main():
    """Main entry point for enhanced orchestrator"""
    orchestrator = EnhancedMCFOrchestrator()

    # Check command line arguments
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == '--phase1':
            orchestrator.run_phase1_collection(test_mode=True)
        elif sys.argv[1] == '--phase2':
            orchestrator.run_phase2_collection(test_mode=True)
        elif sys.argv[1] == '--phase3':
            orchestrator.run_phase3_collection(test_mode=True)
        elif sys.argv[1] == '--stats':
            stats = orchestrator.get_collection_statistics()
            print(json.dumps(stats, indent=2))
        else:
            orchestrator.run_all_phases(test_mode=True)
    else:
        # Run all phases
        orchestrator.run_all_phases(test_mode=False)


if __name__ == "__main__":
    main()
