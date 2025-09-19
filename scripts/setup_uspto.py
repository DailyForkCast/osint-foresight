#!/usr/bin/env python
"""Setup script for USPTO API configuration"""

import os
import yaml
import getpass
from pathlib import Path

def setup_uspto_api():
    """Interactive setup for USPTO API configuration"""

    print("="*60)
    print("USPTO API Setup for OSINT Foresight Analysis")
    print("="*60)

    config_path = "C:/Projects/OSINT - Foresight/config/uspto_config.yaml"

    # Load existing config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    print("\nUSPTO provides several APIs:")
    print("1. PatentsView API - FREE, no key required")
    print("2. USPTO Developer Portal - Requires registration")
    print("3. Bulk Data - Requires special access")

    print("\n" + "-"*60)
    choice = input("\nDo you have a USPTO API key? (y/n): ").strip().lower()

    if choice == 'y':
        print("\nPlease enter your USPTO API credentials:")
        api_key = getpass.getpass("API Key: ").strip()

        # Update config
        config['credentials']['api_key'] = api_key

        # Optional credentials
        client_id = input("Client ID (press Enter to skip): ").strip()
        if client_id:
            config['credentials']['client_id'] = client_id

        client_secret = getpass.getpass("Client Secret (press Enter to skip): ").strip()
        if client_secret:
            config['credentials']['client_secret'] = client_secret

        # Save updated config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print("\n✓ Configuration saved!")
    else:
        print("\nNo problem! The PatentsView API is FREE and doesn't require a key.")
        print("We'll use that for patent searches.")
        print("\nIf you want to register for additional APIs later:")
        print("→ https://developer.uspto.gov/")

    print("\n" + "-"*60)
    print("\nWould you like to test the connection now? (y/n): ", end="")
    test_choice = input().strip().lower()

    if test_choice == 'y':
        print("\nTesting USPTO API connection...\n")
        import sys
        sys.path.append('C:/Projects/OSINT - Foresight/src/pulls')
        from uspto_client import test_connection
        test_connection()

    print("\n" + "="*60)
    print("Setup complete! You can now use the USPTO client.")
    print("\nExample usage:")
    print("  from src.pulls.uspto_client import USPTOClient")
    print("  client = USPTOClient()")
    print("  patents = client.get_italy_patents()")
    print("="*60)

if __name__ == "__main__":
    setup_uspto_api()
