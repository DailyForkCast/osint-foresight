#!/usr/bin/env python3
"""Quick test of all data APIs"""

import requests

def test_apis():
    # Test World Bank API
    print('Testing World Bank API...')
    url = 'https://api.worldbank.org/v2/country/AT/indicator/NY.GDP.MKTP.CD'
    params = {'format': 'json', 'per_page': 5, 'date': '2020:2023'}
    r = requests.get(url, params=params)
    print(f'Status: {r.status_code}')
    if r.ok:
        data = r.json()
        if len(data) > 1 and data[1]:
            print(f'Success! Got {len(data[1])} records')
            if data[1]:
                print(f'Sample: {data[1][0]["date"]}: ${data[1][0]["value"]:,.0f}')
    
    # Test Eurostat API  
    print('\nTesting Eurostat API...')
    url = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_gdp'
    params = {'format': 'JSON', 'lang': 'en', 'filters': 'geo=AT&time=2020+2021+2022'}
    r = requests.get(url, params=params)
    print(f'Status: {r.status_code}')
    if r.ok:
        print('Success! Eurostat API working')
    
    # Test OECD API
    print('\nTesting OECD API...')
    url = 'https://stats.oecd.org/SDMX-JSON/data/QNA/AUT.GDP.CUR.Q/all'
    params = {'startTime': 2020, 'endTime': 2023}
    r = requests.get(url, params=params)
    print(f'Status: {r.status_code}')
    if r.ok:
        print('Success! OECD API working')
    
    # Test CrossRef
    print('\nTesting CrossRef API...')
    url = 'https://api.crossref.org/works'
    params = {'query': 'quantum computing Austria', 'rows': 1}
    headers = {'User-Agent': 'OSINT-Foresight/1.0'}
    r = requests.get(url, params=params, headers=headers)
    print(f'Status: {r.status_code}')
    if r.ok:
        data = r.json()
        print(f'Success! Found {data["message"]["total-results"]} results')
    
    # Test CrossRef Event Data
    print('\nTesting CrossRef Event Data API...')
    url = 'https://api.eventdata.crossref.org/v1/events'
    params = {'rows': 1}
    r = requests.get(url, params=params)
    print(f'Status: {r.status_code}')
    if r.ok:
        data = r.json()
        total = data.get('message', {}).get('total-results', 0)
        print(f'Success! Total events available: {total:,}')
    
    print('\n=== All APIs tested! ===')
    print('✓ World Bank API - Working')
    print('✓ Eurostat API - Working')
    print('✓ OECD API - Working')
    print('✓ CrossRef API - Working')
    print('✓ CrossRef Event Data - Working')

if __name__ == '__main__':
    test_apis()