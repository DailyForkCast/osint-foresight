#!/usr/bin/env python3
"""
Simple EPO Authentication Test - Environment Variables
"""

import requests
import base64
import json
import os

def test_epo_auth():
    """Test EPO authentication from environment variables"""

    print("=" * 50)
    print("EPO OPS Authentication Test")
    print("=" * 50)

    # Get from environment
    consumer_key = os.getenv('EPO_CONSUMER_KEY')
    consumer_secret = os.getenv('EPO_CONSUMER_SECRET')

    if not consumer_key or not consumer_secret:
        print("[ERROR] EPO credentials not found in environment")
        print("Please set:")
        print("  set EPO_CONSUMER_KEY=your_key")
        print("  set EPO_CONSUMER_SECRET=your_secret")
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

            # Save configuration
            config = {
                'epo_ops': {
                    'status': 'authenticated',
                    'consumer_key': consumer_key[:8] + "...",
                    'token_type': token_data.get('token_type'),
                    'expires_in': token_data.get('expires_in'),
                    'test_successful': True
                }
            }

            config_file = "C:/Projects/OSINT - Foresight/config/patent_auth.json"
            os.makedirs(os.path.dirname(config_file), exist_ok=True)

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"Configuration saved to: {config_file}")
            print("\n[SUCCESS] EPO is ready for patent analysis!")

            return True

        else:
            print(f"[ERROR] Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Authentication error: {e}")
        return False

if __name__ == "__main__":
    test_epo_auth()
