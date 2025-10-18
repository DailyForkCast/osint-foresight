#!/usr/bin/env python3
"""
Configuration loader for API keys and environment variables
Loads from .env.local file securely
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

class ConfigLoader:
    def __init__(self):
        """Initialize configuration loader"""
        # Find project root
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = self.project_root / '.env.local'

        # Load environment variables
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logging.info(f"Loaded environment from {self.env_file}")
        else:
            logging.warning(f"No .env.local file found at {self.env_file}")

    def get_uncomtrade_config(self):
        """Get UN Comtrade API configuration"""
        config = {
            'primary_key': os.getenv('UNCOMTRADE_PRIMARY_KEY'),
            'secondary_key': os.getenv('UNCOMTRADE_SECONDARY_KEY'),
            'base_url': os.getenv('UNCOMTRADE_BASE_URL', 'https://comtrade.un.org/api'),
            'rate_limit': int(os.getenv('UNCOMTRADE_RATE_LIMIT', '1'))
        }

        # Check if keys are configured
        if not config['primary_key'] or config['primary_key'] == 'YOUR_PRIMARY_KEY_HERE':
            logging.warning("UN Comtrade primary key not configured in .env.local")
            config['primary_key'] = None

        if not config['secondary_key'] or config['secondary_key'] == 'YOUR_SECONDARY_KEY_HERE':
            logging.warning("UN Comtrade secondary key not configured in .env.local")
            config['secondary_key'] = None

        return config

    def get_opensupplyhub_config(self):
        """Get Open Supply Hub API configuration"""
        config = {
            'api_key': os.getenv('OPENSUPPLYHUB_API_KEY'),
            'base_url': os.getenv('OPENSUPPLYHUB_BASE_URL', 'https://opensupplyhub.org/api')
        }

        if not config['api_key'] or config['api_key'] == 'YOUR_API_KEY_HERE':
            logging.warning("Open Supply Hub API key not configured in .env.local")
            config['api_key'] = None

        return config

    def get_ted_config(self):
        """Get TED Europe API configuration"""
        return {
            'api_key': os.getenv('TED_API_KEY'),
            'base_url': os.getenv('TED_API_BASE_URL', 'https://ted.europa.eu/api'),
            'version': os.getenv('TED_API_VERSION', 'v3'),
            'environment': os.getenv('TED_ENVIRONMENT', 'preview'),
            'rate_limit': int(os.getenv('TED_RATE_LIMIT', '1'))
        }

    def get_uspto_config(self):
        """Get USPTO API configuration"""
        return {
            'api_key': os.getenv('USPTO_API_KEY'),
            'open_data_key': os.getenv('USPTO_OPEN_DATA_API_KEY'),
            'base_url': os.getenv('USPTO_OPEN_DATA_BASE_URL', 'https://data.uspto.gov'),
            'rate_limit': int(os.getenv('USPTO_RATE_LIMIT', '45'))
        }

    def get_epo_config(self):
        """Get EPO API configuration"""
        return {
            'consumer_key': os.getenv('EPO_CONSUMER_KEY'),
            'consumer_secret': os.getenv('EPO_CONSUMER_SECRET')
        }

    def get_database_paths(self):
        """Get database file paths"""
        return {
            'trade_db': os.getenv('TRADE_DB_PATH', 'F:/OSINT_Data/Trade_Facilities/databases/'),
            'iso_db': os.getenv('ISO_DB_PATH', 'F:/OSINT_Data/Trade_Facilities/databases/iso_codes.db'),
            'unlocode_db': os.getenv('UNLOCODE_DB_PATH', 'F:/OSINT_Data/Trade_Facilities/databases/integrated_trade_20250921.db')
        }

# Singleton instance
config = ConfigLoader()

# Convenience functions
def get_uncomtrade_keys():
    """Get UN Comtrade API keys"""
    cfg = config.get_uncomtrade_config()
    return cfg['primary_key'], cfg['secondary_key']

def get_opensupplyhub_key():
    """Get Open Supply Hub API key"""
    cfg = config.get_opensupplyhub_config()
    return cfg['api_key']

def check_api_keys():
    """Check which API keys are configured"""
    print("\n" + "="*60)
    print("API Key Configuration Status")
    print("="*60)

    # Check UN Comtrade
    uncomtrade = config.get_uncomtrade_config()
    if uncomtrade['primary_key'] and uncomtrade['secondary_key']:
        print("[OK] UN Comtrade: Configured")
    else:
        print("[X] UN Comtrade: Not configured (edit .env.local)")

    # Check Open Supply Hub
    osh = config.get_opensupplyhub_config()
    if osh['api_key']:
        print("[OK] Open Supply Hub: Configured")
    else:
        print("[X] Open Supply Hub: Not configured (edit .env.local)")

    # Check TED
    ted = config.get_ted_config()
    if ted['api_key']:
        print("[OK] TED Europe: Configured")
    else:
        print("[X] TED Europe: Not configured")

    # Check USPTO
    uspto = config.get_uspto_config()
    if uspto['api_key']:
        print("[OK] USPTO: Configured")
    else:
        print("[X] USPTO: Not configured")

    # Check EPO
    epo = config.get_epo_config()
    if epo['consumer_key'] and epo['consumer_secret']:
        print("[OK] EPO: Configured")
    else:
        print("[X] EPO: Not configured")

    print("="*60)
    print("\nTo add UN Comtrade keys, edit .env.local and replace:")
    print("  UNCOMTRADE_PRIMARY_KEY=YOUR_PRIMARY_KEY_HERE")
    print("  UNCOMTRADE_SECONDARY_KEY=YOUR_SECONDARY_KEY_HERE")
    print("\nwith your actual API keys.")
    print("="*60)

if __name__ == "__main__":
    check_api_keys()
