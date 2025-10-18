#!/usr/bin/env python3
"""
Test Phase 2 MCF Collectors
Run all Phase 2 (Technology Pathways) collectors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcf_collection_orchestrator import MCFCollectionOrchestrator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run Phase 2 MCF collection"""
    logger.info("Starting Phase 2 MCF Collection - Technology Pathways")

    orchestrator = MCFCollectionOrchestrator()

    # Run Phase 2 collectors
    results = orchestrator.run_comprehensive_collection(phases=['phase2'])

    # Print summary
    summary = results['session_summary']
    print(f"""
Phase 2 MCF Collection Complete:
=====================================
Documents Collected: {summary['total_documents_collected']}
High Relevance Documents: {summary['total_high_relevance_docs']}
Database Growth: +{summary['database_growth']['documents_added']} docs, +{summary['database_growth']['entities_added']} entities
Collectors: {', '.join(summary['collectors_run'])}
    """)

if __name__ == "__main__":
    main()
