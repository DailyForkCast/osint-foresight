#!/usr/bin/env python3
"""
Master Pull Orchestrator for OSINT Foresight
Manages data collection for all 44 countries across all data sources
Stores data on F: drive with appropriate scheduling
"""

import argparse
import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import schedule
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('F:/OSINT_Data/logs/master_pull.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterPullOrchestrator:
    """Orchestrates all data pulls for all countries"""
    
    # All 44 target countries
    COUNTRIES = [
        # EU Member States (27)
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 
        'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 
        'SI', 'ES', 'SE',
        # EEA/EFTA (3)
        'IS', 'NO', 'CH',
        # EU Candidates (9)
        'AL', 'BA', 'XK', 'ME', 'MK', 'RS', 'TR', 'MD', 'UA',
        # Others (5)
        'GB', 'AM', 'AZ', 'GE'
    ]
    
    # Data sources and their recommended pull frequencies
    DATA_SOURCES = {
        # Real-time / Daily sources
        'vessel_tracking': {
            'script': 'ais_pull.py',
            'frequency': 'daily',
            'priority': 'high',
            'countries': 'coastal',  # Only countries with ports
        },
        
        # Weekly sources
        'crossref': {
            'script': 'crossref_pull.py',
            'frequency': 'weekly',
            'priority': 'high',
            'countries': 'all',
        },
        'crossref_events': {
            'script': 'crossref_event_pull.py',
            'frequency': 'weekly',
            'priority': 'medium',
            'countries': 'all',
        },
        'patents': {
            'script': 'patents_pull.py',
            'frequency': 'weekly',
            'priority': 'high',
            'countries': 'all',
        },
        
        # Monthly sources
        'cordis': {
            'script': 'cordis_pull.py',
            'frequency': 'monthly',
            'priority': 'high',
            'countries': 'eu',  # EU members only
        },
        'ted_procurement': {
            'script': 'ted_pull.py',
            'frequency': 'monthly',
            'priority': 'high',
            'countries': 'eu',
        },
        'worldbank': {
            'script': 'worldbank_pull.py',
            'frequency': 'monthly',
            'priority': 'medium',
            'countries': 'all',
        },
        'oecd': {
            'script': 'oecd_pull.py',
            'frequency': 'monthly',
            'priority': 'medium',
            'countries': 'oecd',  # OECD members
        },
        'eurostat': {
            'script': 'eurostat_pull.py',
            'frequency': 'monthly',
            'priority': 'high',
            'countries': 'eu',
        },
        'gleif': {
            'script': 'gleif_pull.py',
            'frequency': 'monthly',
            'priority': 'medium',
            'countries': 'all',
        },
        'ietf': {
            'script': 'ietf_pull.py',
            'frequency': 'monthly',
            'priority': 'low',
            'countries': 'all',
        },
        'openaire': {
            'script': 'openaire_pull.py',
            'frequency': 'monthly',
            'priority': 'medium',
            'countries': 'all',
        },
        
        # Quarterly sources
        'commoncrawl': {
            'script': 'commoncrawl_pull.py',
            'frequency': 'quarterly',
            'priority': 'high',
            'countries': 'all',
        },
        
        # Annual sources
        'openalex_snapshot': {
            'script': 'openalex_snapshot.py',
            'frequency': 'yearly',
            'priority': 'low',
            'countries': 'all',
        },
    }
    
    # Country groupings
    EU_COUNTRIES = [
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
        'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
        'SI', 'ES', 'SE'
    ]
    
    COASTAL_COUNTRIES = [
        'BE', 'BG', 'HR', 'CY', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'IE', 'IT',
        'LV', 'LT', 'MT', 'NL', 'PL', 'PT', 'RO', 'SI', 'ES', 'SE', 'IS', 'NO',
        'AL', 'BA', 'ME', 'TR', 'UA', 'GB', 'GE'
    ]
    
    OECD_COUNTRIES = [
        'AT', 'BE', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT',
        'LV', 'LT', 'LU', 'NL', 'PL', 'PT', 'SK', 'SI', 'ES', 'SE', 'IS', 'NO',
        'CH', 'TR', 'GB'
    ]
    
    def __init__(self, base_dir: Path = Path('F:/OSINT_Data')):
        """Initialize orchestrator with F: drive storage"""
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create directory structure on F: drive
        self.create_directory_structure()
        
        # Load state
        self.state_file = self.base_dir / 'orchestrator_state.json'
        self.state = self.load_state()
        
    def create_directory_structure(self):
        """Create organized directory structure on F: drive"""
        
        directories = [
            'raw',  # Raw data from sources
            'processed',  # Processed/cleaned data
            'logs',  # Pull logs
            'reports',  # Analysis reports
            'backups',  # Data backups
            'common_crawl',  # Large Common Crawl data
            'openalex',  # OpenAlex snapshot
        ]
        
        for dir_name in directories:
            (self.base_dir / dir_name).mkdir(exist_ok=True)
        
        # Create country-specific directories
        for country in self.COUNTRIES:
            (self.base_dir / 'raw' / f'country={country}').mkdir(exist_ok=True)
            (self.base_dir / 'processed' / f'country={country}').mkdir(exist_ok=True)
    
    def load_state(self) -> Dict:
        """Load orchestrator state from disk"""
        
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        
        return {
            'last_pulls': {},
            'pull_history': [],
            'errors': []
        }
    
    def save_state(self):
        """Save orchestrator state to disk"""
        
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)
    
    def get_countries_for_source(self, source_config: Dict) -> List[str]:
        """Get list of countries for a data source"""
        
        country_scope = source_config.get('countries', 'all')
        
        if country_scope == 'all':
            return self.COUNTRIES
        elif country_scope == 'eu':
            return self.EU_COUNTRIES
        elif country_scope == 'coastal':
            return self.COASTAL_COUNTRIES
        elif country_scope == 'oecd':
            return self.OECD_COUNTRIES
        else:
            return self.COUNTRIES
    
    def should_pull(self, source: str, country: str) -> bool:
        """Check if a pull should be executed based on frequency"""
        
        config = self.DATA_SOURCES[source]
        frequency = config['frequency']
        
        # Get last pull time
        key = f"{source}_{country}"
        last_pull = self.state['last_pulls'].get(key)
        
        if not last_pull:
            return True
        
        last_pull_time = datetime.fromisoformat(last_pull)
        now = datetime.now()
        
        # Check based on frequency
        if frequency == 'daily':
            return (now - last_pull_time) >= timedelta(days=1)
        elif frequency == 'weekly':
            return (now - last_pull_time) >= timedelta(days=7)
        elif frequency == 'monthly':
            return (now - last_pull_time) >= timedelta(days=30)
        elif frequency == 'quarterly':
            return (now - last_pull_time) >= timedelta(days=90)
        elif frequency == 'yearly':
            return (now - last_pull_time) >= timedelta(days=365)
        
        return False
    
    def execute_pull(self, source: str, country: str) -> bool:
        """Execute a single data pull"""
        
        config = self.DATA_SOURCES[source]
        script = config['script']
        
        # Build command
        cmd = [
            'python', '-m', f'src.pulls.{script.replace(".py", "")}',
            '--country', country,
            '--out', str(self.base_dir / 'raw' / f'country={country}' / f'source={source}')
        ]
        
        logger.info(f"Executing: {source} for {country}")
        
        try:
            # Run with timeout based on source
            timeout = 3600 if source == 'commoncrawl' else 600  # 1 hour for CC, 10 min others
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                # Update state
                key = f"{source}_{country}"
                self.state['last_pulls'][key] = datetime.now().isoformat()
                
                # Log success
                self.state['pull_history'].append({
                    'source': source,
                    'country': country,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                })
                
                self.save_state()
                logger.info(f"Success: {source} for {country}")
                return True
            else:
                raise Exception(f"Non-zero return code: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout: {source} for {country}")
            self.state['errors'].append({
                'source': source,
                'country': country,
                'timestamp': datetime.now().isoformat(),
                'error': 'timeout'
            })
        except Exception as e:
            logger.error(f"Error: {source} for {country} - {e}")
            self.state['errors'].append({
                'source': source,
                'country': country,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
        
        self.save_state()
        return False
    
    def pull_all_countries(self, source: str):
        """Pull data for all applicable countries for a source"""
        
        config = self.DATA_SOURCES[source]
        countries = self.get_countries_for_source(config)
        
        logger.info(f"Starting {source} pull for {len(countries)} countries")
        
        success_count = 0
        for country in countries:
            if self.should_pull(source, country):
                if self.execute_pull(source, country):
                    success_count += 1
                
                # Rate limiting
                time.sleep(5)  # 5 seconds between pulls
        
        logger.info(f"Completed {source}: {success_count}/{len(countries)} successful")
    
    def run_daily_pulls(self):
        """Run all daily data pulls"""
        logger.info("Starting daily pulls")
        
        for source, config in self.DATA_SOURCES.items():
            if config['frequency'] == 'daily':
                self.pull_all_countries(source)
    
    def run_weekly_pulls(self):
        """Run all weekly data pulls"""
        logger.info("Starting weekly pulls")
        
        for source, config in self.DATA_SOURCES.items():
            if config['frequency'] == 'weekly':
                self.pull_all_countries(source)
    
    def run_monthly_pulls(self):
        """Run all monthly data pulls"""
        logger.info("Starting monthly pulls")
        
        for source, config in self.DATA_SOURCES.items():
            if config['frequency'] == 'monthly':
                self.pull_all_countries(source)
    
    def run_quarterly_pulls(self):
        """Run all quarterly data pulls"""
        logger.info("Starting quarterly pulls - Common Crawl")
        
        # Common Crawl is resource-intensive, run with special handling
        for country in self.COUNTRIES:
            if self.should_pull('commoncrawl', country):
                logger.info(f"Running Common Crawl for {country}")
                self.execute_pull('commoncrawl', country)
                time.sleep(300)  # 5 minute break between countries
    
    def setup_schedule(self):
        """Set up automated scheduling"""
        
        # Daily pulls at 2 AM
        schedule.every().day.at("02:00").do(self.run_daily_pulls)
        
        # Weekly pulls on Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(self.run_weekly_pulls)
        
        # Monthly pulls on 1st of month at 4 AM
        schedule.every().month.do(self.run_monthly_pulls)
        
        # Quarterly pulls (manual trigger for now due to resource requirements)
        # Can be scheduled with cron or Windows Task Scheduler
        
        logger.info("Schedule configured")
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        
        logger.info("Starting scheduler")
        self.setup_schedule()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def generate_status_report(self) -> str:
        """Generate status report of all pulls"""
        
        report = []
        report.append("OSINT Foresight Data Pull Status Report")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Data location: {self.base_dir}")
        report.append("")
        
        # Summary stats
        total_pulls = len(self.state['pull_history'])
        recent_errors = len([e for e in self.state['errors'] 
                           if datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(days=7)])
        
        report.append(f"Total pulls executed: {total_pulls}")
        report.append(f"Recent errors (7 days): {recent_errors}")
        report.append("")
        
        # Status by source
        report.append("Status by Data Source:")
        report.append("-" * 30)
        
        for source, config in self.DATA_SOURCES.items():
            countries = self.get_countries_for_source(config)
            up_to_date = 0
            needs_update = 0
            
            for country in countries:
                if self.should_pull(source, country):
                    needs_update += 1
                else:
                    up_to_date += 1
            
            report.append(f"{source:20} | Frequency: {config['frequency']:10} | "
                         f"Up-to-date: {up_to_date:3} | Needs update: {needs_update:3}")
        
        # Recent errors
        if self.state['errors']:
            report.append("")
            report.append("Recent Errors:")
            report.append("-" * 30)
            for error in self.state['errors'][-10:]:  # Last 10 errors
                report.append(f"{error['timestamp']}: {error['source']} - {error['country']}: {error['error']}")
        
        return "\n".join(report)
    
    def run_priority_pulls(self, priority: str = 'high'):
        """Run pulls for specific priority level"""
        
        logger.info(f"Running {priority} priority pulls")
        
        for source, config in self.DATA_SOURCES.items():
            if config['priority'] == priority:
                self.pull_all_countries(source)


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='Master Pull Orchestrator')
    parser.add_argument('--mode', choices=['scheduler', 'once', 'status', 'priority'],
                       default='once', help='Execution mode')
    parser.add_argument('--source', help='Specific source to pull')
    parser.add_argument('--country', help='Specific country to pull')
    parser.add_argument('--priority', choices=['high', 'medium', 'low'],
                       help='Priority level for priority mode')
    parser.add_argument('--base-dir', default='F:/OSINT_Data',
                       help='Base directory for data storage')
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = MasterPullOrchestrator(Path(args.base_dir))
    
    if args.mode == 'scheduler':
        # Run continuous scheduler
        orchestrator.run_scheduler()
    
    elif args.mode == 'once':
        # Run specific pull or all due pulls
        if args.source and args.country:
            orchestrator.execute_pull(args.source, args.country)
        elif args.source:
            orchestrator.pull_all_countries(args.source)
        else:
            # Run all due pulls
            orchestrator.run_daily_pulls()
            orchestrator.run_weekly_pulls()
            orchestrator.run_monthly_pulls()
    
    elif args.mode == 'status':
        # Generate and print status report
        report = orchestrator.generate_status_report()
        print(report)
        
        # Save report
        report_file = orchestrator.base_dir / 'reports' / f'status_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")
    
    elif args.mode == 'priority':
        # Run pulls by priority
        priority = args.priority or 'high'
        orchestrator.run_priority_pulls(priority)


if __name__ == '__main__':
    main()