#!/usr/bin/env python3
"""
Simple EPO Authentication Test
Test EPO OPS authentication with your consumer key and secret
"""

import requests
import base64
import json
import sys

def test_epo_authentication(consumer_key, consumer_secret):
    """Test EPO OPS authentication"""

    print("=" * 50)
    print("EPO OPS Authentication Test")
    print("=" * 50)

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
            print(f"Access token: {token_data.get('access_token', '')[:20]}...")

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
            import os
            os.makedirs(os.path.dirname(config_file), exist_ok=True)

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"Configuration saved to: {config_file}")

            return True

        else:
            print(f"[ERROR] Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Authentication error: {e}")
        return False

if __name__ == "__main__":
    print("EPO OPS Authentication Test")
    print("Please provide your EPO consumer key and secret:")
    print()

    # Get credentials from user input
    consumer_key = input("Enter EPO Consumer Key: ").strip()
    consumer_secret = input("Enter EPO Consumer Secret: ").strip()

    if consumer_key and consumer_secret:
        success = test_epo_authentication(consumer_key, consumer_secret)

        if success:
            print("\n[NEXT STEPS]")
            print("1. EPO authentication successful")
            print("2. Set environment variables for future use:")
            print(f"   set EPO_CONSUMER_KEY={consumer_key}")
            print(f"   set EPO_CONSUMER_SECRET={consumer_secret}")
            print("3. Run patent comprehensive analyzer:")
            print("   python scripts/patent_comprehensive_analyzer.py")
        else:
            print("\n[TROUBLESHOOTING]")
            print("1. Verify credentials from EPO developer portal")
            print("2. Check network connectivity")
            print("3. Ensure application is approved in EPO portal")
    else:
        print("Both consumer key and secret are required")
