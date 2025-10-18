#!/usr/bin/env python3
"""
EPO Authentication from Config File
"""

import requests
import base64
import json
import os
from pathlib import Path

def test_epo_auth_from_config():
    """Test EPO authentication from config file"""

    print("=" * 50)
    print("EPO OPS Authentication Test")
    print("=" * 50)

    # Load credentials from config file
    config_path = Path("C:/Projects/OSINT - Foresight/config/epo_credentials.json")

    if not config_path.exists():
        print(f"[ERROR] Config file not found: {config_path}")
        return False

    try:
        with open(config_path, 'r') as f:
            creds = json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not read config file: {e}")
        return False

    consumer_key = creds.get('EPO_CONSUMER_KEY', '').strip()
    consumer_secret = creds.get('EPO_CONSUMER_SECRET', '').strip()

    if not consumer_key or not consumer_secret:
        print("[ERROR] EPO credentials not found in config file")
        print("Please edit: C:/Projects/OSINT - Foresight/config/epo_credentials.json")
        print("Replace YOUR_CONSUMER_KEY_HERE and YOUR_CONSUMER_SECRET_HERE with your actual values")
        return False

    if consumer_key == "YOUR_CONSUMER_KEY_HERE":
        print("[ERROR] Please replace YOUR_CONSUMER_KEY_HERE with your actual EPO consumer key")
        print("Edit: C:/Projects/OSINT - Foresight/config/epo_credentials.json")
        return False

    print(f"Using consumer key: {consumer_key[:8]}...")

    try:
        # Encode credentials
        credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

        # Setup headers
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Request data
        data = {'grant_type': 'client_credentials'}

        print("Requesting access token from EPO...")

        # Make authentication request
        response = requests.post(
            'https://ops.epo.org/3.2/auth/accesstoken',
            headers=headers,
            data=data,
            timeout=10
        )

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            token_data = response.json()

            print("[SUCCESS] EPO authentication successful!")
            print(f"Token type: {token_data.get('token_type')}")
            print(f"Expires in: {token_data.get('expires_in')} seconds")

            # Save authentication configuration
            auth_config = {
                'epo_ops': {
                    'status': 'authenticated',
                    'consumer_key': consumer_key[:8] + "...",
                    'token_type': token_data.get('token_type'),
                    'expires_in': token_data.get('expires_in'),
                    'test_successful': True,
                    'access_token': token_data.get('access_token')
                }
            }

            auth_config_file = "C:/Projects/OSINT - Foresight/config/patent_auth.json"
            os.makedirs(os.path.dirname(auth_config_file), exist_ok=True)

            with open(auth_config_file, 'w') as f:
                json.dump(auth_config, f, indent=2)

            print(f"Authentication config saved to: {auth_config_file}")
            print("\n[SUCCESS] EPO is ready for patent analysis!")
            print("\nNext steps:")
            print("1. Run: python scripts/patent_comprehensive_analyzer.py")
            print("2. Or test EPO client: python scripts/collectors/epo_ops_client.py")

            return True

        else:
            print(f"[ERROR] Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Authentication error: {e}")
        return False

if __name__ == "__main__":
    test_epo_auth_from_config()
