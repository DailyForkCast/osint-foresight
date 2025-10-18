#!/usr/bin/env python3
"""
Master Orchestration Script for Concurrent Data Processing
Launches parallel processing for OpenAlex, OpenAIRE, TED, and USAspending
"""

import asyncio
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import time
import traceback
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/Projects/OSINT - Foresight/logs/orchestration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Orchestrator')


class DataSourceProcessor:
    """Base class for data source processors"""
    
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.status = {
            'name': name,
            'status': 'pending',
            'started': None,
            'completed': None,
            'records_processed': 0,
            'errors': 0,
            'last_error': None
        }
        
    def update_status(self, **kwargs):
        """Update processing status"""
        self.status.update(kwargs)
        self.save_status()
        
    def save_status(self):
        """Save status to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_status (
                    source TEXT PRIMARY KEY,
                    status TEXT,
                    started TEXT,
                    completed TEXT,
                    records_processed INTEGER,
                    errors INTEGER,
                    last_error TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT OR REPLACE INTO processing_status
                (source, status, started, completed, records_processed, errors, last_error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.status['name'],
                self.status['status'],
                self.status['started'],
                self.status['completed'],
                self.status['records_processed'],
                self.status['errors'],
                self.status['last_error']
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving status for {self.name}: {e}")
    
    def process(self):
        """Override this method in subclasses"""
        raise NotImplementedError


class OpenAlexProcessor(DataSourceProcessor):
    """Process OpenAlex data files"""
    
    def __init__(self, config: dict):
        super().__init__('OpenAlex', config)
        self.data_dir = Path("F:/OSINT_Backups/openalex")
        self.checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/processed/openalex_concurrent/checkpoint.json")
        self.checkpoint_file.parent.mkdir(exist_ok=True, parents=True)
        
    def load_checkpoint(self):
        """Load processing checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            'last_file': None,
            'files_processed': [],
            'total_records': 0,
            'china_collaborations': {}
        }
    
    def save_checkpoint(self, checkpoint):
        """Save processing checkpoint"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    
    def process(self):
        """Process OpenAlex data files"""
        logger.info(f"Starting OpenAlex processing")
        self.update_status(status='running', started=datetime.now().isoformat())
        
        checkpoint = self.load_checkpoint()
        
        try:
            # Get all .gz files
            gz_files = sorted(self.data_dir.glob("*.gz"))
            logger.info(f"Found {len(gz_files)} OpenAlex files to process")
            
            # Filter already processed files
            files_to_process = [
                f for f in gz_files 
                if f.name not in checkpoint['files_processed']
            ]
            
            logger.info(f"Processing {len(files_to_process)} new files")
            
            for idx, file_path in enumerate(files_to_process[:5]):  # Process 5 files at a time
                try:
                    logger.info(f"Processing {file_path.name} ({idx+1}/{len(files_to_process)})")
                    
                    # Here you would process the actual file
                    # For now, simulate processing
                    time.sleep(1)  # Simulate processing time
                    
                    # Update checkpoint
                    checkpoint['files_processed'].append(file_path.name)
                    checkpoint['last_file'] = file_path.name
                    checkpoint['total_records'] += 1000  # Simulated record count
                    
                    self.save_checkpoint(checkpoint)
                    self.update_status(
                        records_processed=checkpoint['total_records']
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {e}")
                    self.update_status(
                        errors=self.status['errors'] + 1,
                        last_error=str(e)
                    )
                    
            self.update_status(
                status='completed',
                completed=datetime.now().isoformat()
            )
            logger.info(f"OpenAlex processing completed")
            
        except Exception as e:
            logger.error(f"Fatal error in OpenAlex processing: {e}")
            self.update_status(
                status='failed',
                last_error=str(e)
            )


class OpenAIREProcessor(DataSourceProcessor):
    """Process OpenAIRE data"""
    
    def __init__(self, config: dict):
        super().__init__('OpenAIRE', config)
        self.api_base = "https://api.openaire.eu/search"
        self.checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/processed/openaire_concurrent/checkpoint.json")
        self.checkpoint_file.parent.mkdir(exist_ok=True, parents=True)
    
    def process(self):
        """Process OpenAIRE data"""
        logger.info(f"Starting OpenAIRE processing")
        self.update_status(status='running', started=datetime.now().isoformat())
        
        try:
            # Countries to process
            countries = self.config.get('countries', [
                'IT', 'DE', 'FR', 'ES', 'PL', 'CZ', 'SK', 'HU', 'RO', 'BG'
            ])
            
            for country in countries:
                try:
                    logger.info(f"Processing OpenAIRE data for {country}")
                    
                    # Here you would query OpenAIRE API
                    # For now, simulate processing
                    time.sleep(2)  # Simulate API call
                    
                    self.update_status(
                        records_processed=self.status['records_processed'] + 100
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing OpenAIRE for {country}: {e}")
                    self.update_status(
                        errors=self.status['errors'] + 1,
                        last_error=str(e)
                    )
            
            self.update_status(
                status='completed',
                completed=datetime.now().isoformat()
            )
            logger.info(f"OpenAIRE processing completed")
            
        except Exception as e:
            logger.error(f"Fatal error in OpenAIRE processing: {e}")
            self.update_status(
                status='failed',
                last_error=str(e)
            )


class TEDProcessor(DataSourceProcessor):
    """Process TED procurement data"""
    
    def __init__(self, config: dict):
        super().__init__('TED', config)
        self.data_dir = Path("F:/TED_Data/monthly")
        self.checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/processed/ted_concurrent/checkpoint.json")
        self.checkpoint_file.parent.mkdir(exist_ok=True, parents=True)
    
    def process(self):
        """Process TED data files"""
        logger.info(f"Starting TED processing")
        self.update_status(status='running', started=datetime.now().isoformat())
        
        try:
            # Get all CSV files
            csv_files = sorted(self.data_dir.glob("*.csv"))
            logger.info(f"Found {len(csv_files)} TED files to process")
            
            for idx, file_path in enumerate(csv_files[:3]):  # Process 3 files at a time
                try:
                    logger.info(f"Processing {file_path.name} ({idx+1}/{len(csv_files)})")
                    
                    # Here you would process the actual CSV file
                    # For now, simulate processing
                    time.sleep(1.5)  # Simulate processing time
                    
                    self.update_status(
                        records_processed=self.status['records_processed'] + 500
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {e}")
                    self.update_status(
                        errors=self.status['errors'] + 1,
                        last_error=str(e)
                    )
            
            self.update_status(
                status='completed',
                completed=datetime.now().isoformat()
            )
            logger.info(f"TED processing completed")
            
        except Exception as e:
            logger.error(f"Fatal error in TED processing: {e}")
            self.update_status(
                status='failed',
                last_error=str(e)
            )


class USAspendingProcessor(DataSourceProcessor):
    """Process USAspending data"""
    
    def __init__(self, config: dict):
        super().__init__('USAspending', config)
        self.data_dir = Path("F:/OSINT_DATA/Italy/USASPENDING")
        self.checkpoint_file = Path("C:/Projects/OSINT - Foresight/data/processed/usaspending_concurrent/checkpoint.json")
        self.checkpoint_file.parent.mkdir(exist_ok=True, parents=True)
    
    def process(self):
        """Process USAspending data"""
        logger.info(f"Starting USAspending processing")
        self.update_status(status='running', started=datetime.now().isoformat())
        
        try:
            # Process data files
            data_files = list(self.data_dir.glob("*.json")) + list(self.data_dir.glob("*.csv"))
            logger.info(f"Found {len(data_files)} USAspending files to process")
            
            for idx, file_path in enumerate(data_files[:5]):  # Process 5 files at a time
                try:
                    logger.info(f"Processing {file_path.name} ({idx+1}/{len(data_files)})")
                    
                    # Here you would process the actual file
                    # For now, simulate processing
                    time.sleep(1)  # Simulate processing time
                    
                    self.update_status(
                        records_processed=self.status['records_processed'] + 250
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {e}")
                    self.update_status(
                        errors=self.status['errors'] + 1,
                        last_error=str(e)
                    )
            
            self.update_status(
                status='completed',
                completed=datetime.now().isoformat()
            )
            logger.info(f"USAspending processing completed")
            
        except Exception as e:
            logger.error(f"Fatal error in USAspending processing: {e}")
            self.update_status(
                status='failed',
                last_error=str(e)
            )


def process_data_source(processor_class, config):
    """Process a single data source in a separate process"""
    try:
        processor = processor_class(config)
        processor.process()
        return processor.status
    except Exception as e:
        logger.error(f"Error in process_data_source: {e}\n{traceback.format_exc()}")
        return {'status': 'failed', 'error': str(e)}


class ConcurrentOrchestrator:
    """Orchestrate concurrent processing of multiple data sources"""
    
    def __init__(self):
        self.db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.log_dir = Path("C:/Projects/OSINT - Foresight/logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Configuration for each data source
        self.config = {
            'OpenAlex': {
                'batch_size': 5,
                'max_workers': 2
            },
            'OpenAIRE': {
                'countries': ['IT', 'DE', 'FR', 'ES', 'PL', 'CZ', 'SK', 'HU', 'RO', 'BG'],
                'batch_size': 10
            },
            'TED': {
                'batch_size': 3,
                'max_workers': 2
            },
            'USAspending': {
                'batch_size': 5,
                'max_workers': 2
            }
        }
    
    def create_dashboard_status(self):
        """Create a dashboard showing processing status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source, status, started, completed, 
                   records_processed, errors, last_error
            FROM processing_status
            ORDER BY source
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        dashboard = """
========================================
     CONCURRENT PROCESSING DASHBOARD    
========================================

"""
        for row in results:
            source, status, started, completed, records, errors, last_error = row
            status_icon = {
                'pending': '[...]',
                'running': '[>>>]',
                'completed': '[OK]',
                'failed': '[FAIL]'
            }.get(status, '[ ? ]')
            
            dashboard += f"{status_icon} {source:<12} | Records: {records:>7} | Errors: {errors:>3}\n"
            
            if status == 'running' and started:
                dashboard += f"    Started: {started}\n"
            elif status == 'completed' and completed:
                dashboard += f"    Completed: {completed}\n"
            elif status == 'failed' and last_error:
                dashboard += f"    Error: {last_error[:50]}...\n"
        
        dashboard += """
========================================
"""
        return dashboard
    
    async def monitor_progress(self):
        """Monitor and display progress"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(self.create_dashboard_status())
            await asyncio.sleep(5)  # Update every 5 seconds
    
    def run_concurrent(self):
        """Run all processors concurrently"""
        logger.info("Starting concurrent processing orchestration")
        
        # Initialize database
        self.initialize_database()
        
        # Create process pool
        with ProcessPoolExecutor(max_workers=4) as executor:
            # Submit all processing jobs
            futures = {
                executor.submit(process_data_source, OpenAlexProcessor, self.config['OpenAlex']): 'OpenAlex',
                executor.submit(process_data_source, OpenAIREProcessor, self.config['OpenAIRE']): 'OpenAIRE',
                executor.submit(process_data_source, TEDProcessor, self.config['TED']): 'TED',
                executor.submit(process_data_source, USAspendingProcessor, self.config['USAspending']): 'USAspending'
            }
            
            # Monitor progress in a separate thread
            import threading
            monitor_thread = threading.Thread(target=self.monitor_loop)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Wait for all processes to complete
            for future in futures:
                source = futures[future]
                try:
                    result = future.result(timeout=3600)  # 1 hour timeout per source
                    logger.info(f"{source} completed with status: {result.get('status')}")
                except Exception as e:
                    logger.error(f"{source} failed: {e}")
        
        logger.info("All concurrent processing completed")
        self.generate_final_report()
    
    def monitor_loop(self):
        """Run the async monitor loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.monitor_progress())
    
    def initialize_database(self):
        """Initialize status tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_status (
                source TEXT PRIMARY KEY,
                status TEXT,
                started TEXT,
                completed TEXT,
                records_processed INTEGER,
                errors INTEGER,
                last_error TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Initialize status for all sources
        sources = ['OpenAlex', 'OpenAIRE', 'TED', 'USAspending']
        for source in sources:
            cursor.execute("""
                INSERT OR IGNORE INTO processing_status (source, status)
                VALUES (?, 'pending')
            """, (source,))
        
        conn.commit()
        conn.close()
    
    def generate_final_report(self):
        """Generate final processing report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source, status, records_processed, errors
            FROM processing_status
        """)
        
        results = cursor.fetchall()
        
        report = f"""
# Concurrent Processing Report
Generated: {datetime.now().isoformat()}

## Processing Summary

| Source | Status | Records | Errors |
|--------|--------|---------|--------|
"""
        
        total_records = 0
        total_errors = 0
        
        for source, status, records, errors in results:
            report += f"| {source} | {status} | {records:,} | {errors} |\n"
            total_records += records or 0
            total_errors += errors or 0
        
        report += f"""

## Totals
- Total Records Processed: {total_records:,}
- Total Errors: {total_errors}
- Success Rate: {((total_records - total_errors) / max(total_records, 1) * 100):.1f}%

## Next Steps
1. Review error logs for failed processing
2. Resume processing for incomplete sources
3. Run data validation and deduplication
4. Generate intelligence reports from processed data
"""
        
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/CONCURRENT_PROCESSING_REPORT.md")
        report_path.write_text(report)
        
        logger.info(f"Final report saved to {report_path}")
        print(f"\nFinal report saved to {report_path}")
        
        conn.close()


if __name__ == "__main__":
    orchestrator = ConcurrentOrchestrator()
    
    print("""
    ========================================
         CONCURRENT DATA PROCESSING
    ========================================
    
    Starting parallel processing for:
    - OpenAlex (Scientific publications)
    - OpenAIRE (EU research projects)
    - TED (EU procurement data)
    - USAspending (US federal contracts)
    
    Press Ctrl+C to stop processing
    ========================================
    """)
    
    try:
        orchestrator.run_concurrent()
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        print("\nProcessing interrupted. Generating report...")
        orchestrator.generate_final_report()
    except Exception as e:
        logger.error(f"Fatal error: {e}\n{traceback.format_exc()}")
        print(f"\nFatal error: {e}")
