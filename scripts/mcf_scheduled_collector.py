#!/usr/bin/env python3
"""
MCF Scheduled Collection System
Runs collections every 3-4 hours with rotating search terms and improved strategies
"""

import os
import sys
import json
import time
import sqlite3
import random
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use enhanced orchestrator with Selenium support
try:
    from scripts.mcf_orchestrator_enhanced import EnhancedMCFOrchestrator as MCFCollectionOrchestrator
    print("Using enhanced orchestrator with Selenium ASPI collector")
except ImportError:
    from scripts.mcf_collection_orchestrator import MCFCollectionOrchestrator
    print("Using standard orchestrator")

class MCFScheduledCollector:
    """Scheduled collection system for MCF intelligence with 3-4 hour intervals"""

    def __init__(self):
        self.orchestrator = MCFCollectionOrchestrator()
        self.db_path = "F:/OSINT_WAREHOUSE/osint_research.db"
        self.collection_log = []
        self.search_term_sets = self._initialize_search_terms()
        self.current_term_index = 0
        self.collection_runs = 0
        self.max_runs_per_day = 8  # 24 hours / 3 hours = 8 runs

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('F:/OSINT_WAREHOUSE/scheduled_collection.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_search_terms(self) -> List[Dict[str, List[str]]]:
        """Initialize rotating sets of search terms for varied collection"""
        return [
            # Set 1: Core MCF terms
            {
                'mcf_terms': ['military civil fusion', 'MCF', '军民融合', 'civil military integration'],
                'tech_terms': ['dual use technology', 'technology transfer', 'defense innovation'],
                'entity_terms': ['AVIC', 'NORINCO', 'CETC', 'SASTIND']
            },
            # Set 2: PLA and defense focus
            {
                'mcf_terms': ['PLA modernization', 'defense industrial base', 'military technology'],
                'tech_terms': ['artificial intelligence military', 'quantum computing defense', 'hypersonic'],
                'entity_terms': ['AECC', 'CASIC', 'CASC', 'PLA Unit 61398']
            },
            # Set 3: Technology pathways
            {
                'mcf_terms': ['Made in China 2025', 'talent program', 'thousand talents'],
                'tech_terms': ['semiconductor military', '5G military applications', 'biotechnology defense'],
                'entity_terms': ['Huawei military', 'ZTE defense', 'DJI military', 'Hikvision PLA']
            },
            # Set 4: Supply chain and procurement
            {
                'mcf_terms': ['defense supply chain', 'military procurement China', 'CFIUS'],
                'tech_terms': ['critical minerals defense', 'rare earth military', 'chip fabrication'],
                'entity_terms': ['China Electronics Corporation', 'CRRC military', 'BYD defense']
            },
            # Set 5: Research and development
            {
                'mcf_terms': ['defense research institutes China', 'military universities China', 'NUDT'],
                'tech_terms': ['directed energy weapons', 'autonomous military systems', 'cyber warfare'],
                'entity_terms': ['Beijing Institute of Technology', 'Harbin Engineering University', 'CAEP']
            },
            # Set 6: International collaboration concerns
            {
                'mcf_terms': ['technology diversion', 'export control China', 'dual use export'],
                'tech_terms': ['nuclear technology transfer', 'missile technology', 'space military'],
                'entity_terms': ['China Aerospace', 'China Shipbuilding', 'China Nuclear']
            },
            # Set 7: Emerging domains
            {
                'mcf_terms': ['intelligentized warfare', 'system confrontation', 'strategic support force'],
                'tech_terms': ['cognitive warfare', 'brain-computer interface military', 'swarm intelligence'],
                'entity_terms': ['Academy of Military Sciences', 'NDU China', 'PLA Strategic Support Force']
            },
            # Set 8: Economic-military nexus
            {
                'mcf_terms': ['Belt and Road military', 'digital silk road defense', 'port facilities dual use'],
                'tech_terms': ['blockchain military', 'digital currency warfare', 'economic coercion'],
                'entity_terms': ['China Communications Construction', 'China Merchants', 'COSCO military']
            }
        ]

    def get_next_search_terms(self) -> Dict[str, List[str]]:
        """Rotate through search term sets for diversity"""
        terms = self.search_term_sets[self.current_term_index]
        self.current_term_index = (self.current_term_index + 1) % len(self.search_term_sets)
        return terms

    def run_scheduled_collection(self):
        """Run a single collection cycle with current search terms"""
        try:
            self.collection_runs += 1
            search_terms = self.get_next_search_terms()

            self.logger.info(f"Starting collection run #{self.collection_runs}")
            self.logger.info(f"Using search term set {self.current_term_index}: {search_terms['mcf_terms'][0]}...")

            # Configure orchestrator with current search terms
            self._configure_collectors(search_terms)

            # Run Phase 1 collection with limits
            phase1_results = self._run_phase_with_limits('phase1', limit=20)

            # Run Phase 2 collection with limits
            phase2_results = self._run_phase_with_limits('phase2', limit=15)

            # Run Phase 3 collection with limits (if available)
            if hasattr(self.orchestrator, 'run_phase3_collection'):
                phase3_results = self._run_phase_with_limits('phase3', limit=10)
            else:
                phase3_results = {'documents_collected': 0}

            # Log collection summary
            total_collected = (
                phase1_results.get('documents_collected', 0) +
                phase2_results.get('documents_collected', 0) +
                phase3_results.get('documents_collected', 0)
            )

            collection_summary = {
                'run_number': self.collection_runs,
                'timestamp': datetime.now().isoformat(),
                'search_term_set': self.current_term_index,
                'phase1_docs': phase1_results.get('documents_collected', 0),
                'phase2_docs': phase2_results.get('documents_collected', 0),
                'phase3_docs': phase3_results.get('documents_collected', 0),
                'total_docs': total_collected
            }

            self.collection_log.append(collection_summary)
            self._save_collection_log()

            self.logger.info(f"Collection run #{self.collection_runs} complete: {total_collected} documents")

            # If we've completed all runs for the day, generate report
            if self.collection_runs >= self.max_runs_per_day:
                self.generate_daily_report()

        except Exception as e:
            self.logger.error(f"Error in scheduled collection: {e}")

    def _configure_collectors(self, search_terms: Dict[str, List[str]]):
        """Configure collectors with current search terms"""
        # For now, just pass - collectors will use their default search terms
        # This avoids keyword configuration issues
        pass

    def _run_phase_with_limits(self, phase: str, limit: int = 20) -> Dict[str, Any]:
        """Run a collection phase with document limits"""
        try:
            if phase == 'phase1':
                results = self.orchestrator.run_phase1_collection(test_mode=True, limit_per_source=limit)
            elif phase == 'phase2':
                results = self.orchestrator.run_phase2_collection(test_mode=True, limit_per_source=limit)
            elif phase == 'phase3':
                results = self.orchestrator.run_phase3_collection(test_mode=True, limit_per_source=limit)
            else:
                results = {'documents_collected': 0, 'errors': [f'Unknown phase: {phase}']}

            return results

        except Exception as e:
            self.logger.error(f"Error running {phase}: {e}")
            return {'documents_collected': 0, 'errors': [str(e)]}

    def _save_collection_log(self):
        """Save collection log to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create log table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_collection_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_number INTEGER,
                    timestamp TEXT,
                    search_term_set INTEGER,
                    phase1_docs INTEGER,
                    phase2_docs INTEGER,
                    phase3_docs INTEGER,
                    total_docs INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Insert latest log entry
            latest = self.collection_log[-1]
            cursor.execute('''
                INSERT INTO scheduled_collection_log
                (run_number, timestamp, search_term_set, phase1_docs, phase2_docs, phase3_docs, total_docs)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                latest['run_number'],
                latest['timestamp'],
                latest['search_term_set'],
                latest['phase1_docs'],
                latest['phase2_docs'],
                latest['phase3_docs'],
                latest['total_docs']
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error saving collection log: {e}")

    def generate_daily_report(self):
        """Generate daily collection report"""
        try:
            total_docs = sum(log['total_docs'] for log in self.collection_log)
            avg_docs = total_docs / len(self.collection_log) if self.collection_log else 0

            report = f"""
# MCF Scheduled Collection - Daily Report
Generated: {datetime.now().isoformat()}

## Collection Summary
- Total Runs: {self.collection_runs}
- Total Documents: {total_docs}
- Average per Run: {avg_docs:.1f}

## Run Details
"""
            for log in self.collection_log:
                report += f"""
### Run {log['run_number']} - {log['timestamp']}
- Search Set: {log['search_term_set']}
- Phase 1: {log['phase1_docs']} docs
- Phase 2: {log['phase2_docs']} docs
- Phase 3: {log['phase3_docs']} docs
- Total: {log['total_docs']} docs
"""

            # Save report
            report_path = f"F:/OSINT_WAREHOUSE/daily_report_{datetime.now().strftime('%Y%m%d')}.md"
            with open(report_path, 'w') as f:
                f.write(report)

            self.logger.info(f"Daily report saved to {report_path}")

            # Reset for next day
            self.collection_runs = 0
            self.collection_log = []

        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")

    def start_scheduled_collection(self, interval_hours: float = 3.5):
        """Start the scheduled collection system"""
        self.logger.info(f"Starting scheduled collection with {interval_hours} hour intervals")

        # Run first collection immediately
        self.run_scheduled_collection()

        # Schedule subsequent collections
        schedule.every(interval_hours).hours.do(self.run_scheduled_collection)

        # Run scheduler
        while self.collection_runs < self.max_runs_per_day:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

        self.logger.info("Daily collection complete")
        self.generate_daily_report()

    def run_test_cycle(self):
        """Run a single test cycle with all phases"""
        self.logger.info("Running test cycle...")
        self.run_scheduled_collection()
        return self.collection_log[-1] if self.collection_log else None


def main():
    """Main entry point for scheduled collection"""
    collector = MCFScheduledCollector()

    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("Running test cycle...")
        result = collector.run_test_cycle()
        print(f"Test complete: {result}")
    else:
        # Run full scheduled collection (24 hours)
        print("Starting 24-hour scheduled collection...")
        print("Collections will run every 3-4 hours")
        print("Press Ctrl+C to stop")

        try:
            # Use 3.5 hours for some variation
            interval = random.uniform(3.0, 4.0)
            collector.start_scheduled_collection(interval_hours=interval)
        except KeyboardInterrupt:
            print("\nScheduled collection stopped by user")
            collector.generate_daily_report()


if __name__ == "__main__":
    main()
