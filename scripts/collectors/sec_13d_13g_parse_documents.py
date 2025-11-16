#!/usr/bin/env python3
"""
SEC 13D/13G Document Parser
Downloads and parses actual filing documents to extract beneficial owner information

Critical Fix: SEC index shows SUBJECT COMPANY (target), not BENEFICIAL OWNER (acquirer)
This script extracts the actual filers/beneficial owners from filing documents

Date: November 1, 2025
"""

import requests
import sqlite3
from datetime import datetime
from pathlib import Path
import time
import re
from bs4 import BeautifulSoup
import json

# Configuration
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("F:/OSINT_Data/SEC_13D_13G_Parsed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "OSINT-Foresight-Research mreardon@example.com"

class SEC13DGParser:
    def __init__(self):
        self.conn = sqlite3.connect(MASTER_DB, timeout=300)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.cur = self.conn.cursor()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

        # Load Chinese entity detection
        self.chinese_keywords = self._load_chinese_keywords()

        self.parsed_count = 0
        self.chinese_found = 0
        self.errors = 0

    def _load_chinese_keywords(self):
        """Load Chinese entity identifiers"""
        try:
            prc_file = Path("C:/Projects/OSINT-Foresight/data/prc_identifiers.json")
            if prc_file.exists():
                with open(prc_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    keywords = set()
                    for entity in data.get('company_names', []):
                        keywords.add(entity.upper())
                    return keywords
        except:
            pass

        return {
            'CHINA', 'CHINESE', 'SINO', 'HONG KONG', 'SHANGHAI', 'BEIJING', 'SHENZHEN',
            'CHINA INVESTMENT CORPORATION', 'CIC',
            'SAFE INVESTMENT', 'STATE ADMINISTRATION OF FOREIGN EXCHANGE',
            'CHINA LIFE', 'PING AN', 'CHINA CONSTRUCTION BANK', 'ICBC',
            'BANK OF CHINA', 'AGRICULTURAL BANK OF CHINA',
            'CHINA MERCHANTS', 'CITIC', 'CHINA INTERNATIONAL CAPITAL',
            'ALIBABA', 'TENCENT', 'BAIDU', 'HUAWEI', 'ZTE',
            'CAYMAN',
            'PRC', "PEOPLE'S REPUBLIC OF CHINA",
        }

    def get_unparsed_filings(self, limit=100):
        """Get filings that haven't been parsed yet"""
        print('=' * 80)
        print('FETCHING UNPARSED FILINGS')
        print('=' * 80)

        # Get filings without proper filer information (where filer_name = company_name)
        # This indicates we only have subject company, not beneficial owner
        self.cur.execute('''
            SELECT accession_number, html_url, company_name, filing_date, form_type
            FROM sec_13d_13g_filings
            WHERE filer_name = company_name
            OR filer_address IS NULL
            ORDER BY filing_date DESC
            LIMIT ?
        ''', (limit,))

        filings = self.cur.fetchall()
        print(f'[OK] Found {len(filings)} filings to parse')
        return filings

    def download_filing(self, html_url):
        """Download filing document"""
        try:
            response = self.session.get(html_url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f'  [ERROR] Download failed: {e}')
            return None

    def parse_sgml_header(self, content):
        """Parse SEC SGML header for filer information - most reliable method"""
        try:
            # Extract SEC-HEADER section
            header_match = re.search(r'<SEC-HEADER>(.*?)</SEC-HEADER>', content, re.DOTALL)
            if not header_match:
                return None

            header = header_match.group(1)

            extracted = {
                'beneficial_owner_name': None,
                'beneficial_owner_address': None,
                'beneficial_owner_country': None,
            }

            # Extract filer company name
            # SGML format: COMPANY CONFORMED NAME: [NAME]
            name_match = re.search(r'COMPANY CONFORMED NAME:\s+(.+)', header)
            if name_match:
                extracted['beneficial_owner_name'] = name_match.group(1).strip()

            # Extract state of incorporation (often indicates country)
            state_match = re.search(r'STATE OF INCORPORATION:\s+(.+)', header)
            if state_match:
                state = state_match.group(1).strip()
                # Convert state codes to full names if needed
                if len(state) == 2:
                    # US state code
                    extracted['beneficial_owner_country'] = 'United States'
                else:
                    # Country or full state name
                    extracted['beneficial_owner_country'] = state

            # Extract business address from header
            # Format:
            # BUSINESS ADDRESS:
            #   STREET 1: [address]
            #   CITY: [city]
            #   STATE: [state]
            #   ZIP: [zip]
            addr_match = re.search(
                r'BUSINESS ADDRESS:.*?STREET 1:\s+(.+?)(?:\s+STREET 2:.*?)?CITY:\s+(.+?)STATE:\s+(.+?)ZIP:\s+(.+?)(?:\n|$)',
                header,
                re.DOTALL
            )
            if addr_match:
                street, city, state, zip_code = addr_match.groups()[:4]
                extracted['beneficial_owner_address'] = f"{street.strip()}, {city.strip()}, {state.strip()} {zip_code.strip()}"

            return extracted

        except Exception as e:
            return None

    def parse_13d_13g_document(self, html_content, form_type):
        """
        Parse 13D/13G document to extract beneficial owner information

        Key fields to extract:
        - Beneficial owner name
        - Beneficial owner address
        - Beneficial owner citizenship/country
        - Percentage of class owned
        - Number of shares owned
        """
        try:
            # Strategy 1: Parse SGML header (most reliable)
            header_data = self.parse_sgml_header(html_content)
            if header_data and header_data.get('beneficial_owner_name'):
                # Merge with additional data from document body
                soup = BeautifulSoup(html_content, 'html.parser')
                text = soup.get_text()

                extracted = header_data.copy()
                extracted['percent_owned'] = None
                extracted['shares_owned'] = None

                # Extract percentage and shares from document body
                percent_patterns = [
                    r'PERCENT OF CLASS REPRESENTED[:]?\s*([\d.]+)%?',
                    r'PERCENTAGE[:]?\s*([\d.]+)%',
                ]
                for pattern in percent_patterns:
                    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                    if match:
                        try:
                            extracted['percent_owned'] = float(match.group(1))
                            break
                        except:
                            pass

                shares_patterns = [
                    r'NUMBER OF SHARES[:]?\s*([\d,]+)',
                    r'AGGREGATE AMOUNT BENEFICIALLY OWNED[:]?\s*([\d,]+)',
                ]
                for pattern in shares_patterns:
                    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                    if match:
                        try:
                            extracted['shares_owned'] = int(match.group(1).replace(',', ''))
                            break
                        except:
                            pass

                return extracted

            # Strategy 2: Parse document body (fallback)
            soup = BeautifulSoup(html_content, 'html.parser')

            extracted = {
                'beneficial_owner_name': None,
                'beneficial_owner_address': None,
                'beneficial_owner_country': None,
                'percent_owned': None,
                'shares_owned': None,
            }

            # Strategy 2: Look for cover page or filing person section
            # Common patterns in SEC filings:
            # - "FILING PERSON"
            # - "NAME OF REPORTING PERSON"
            # - "BENEFICIAL OWNER"

            text = soup.get_text()

            # Extract beneficial owner name
            # Pattern 1: "NAME OF REPORTING PERSON:" or "REPORTING PERSON:"
            name_patterns = [
                r'NAME OF REPORTING PERSON[S]?[:.]?\s*([A-Z][A-Za-z0-9\s\.,&\-\']+)',
                r'REPORTING PERSON[S]?[:.]?\s*([A-Z][A-Za-z0-9\s\.,&\-\']+)',
                r'BENEFICIAL OWNER[:.]?\s*([A-Z][A-Za-z0-9\s\.,&\-\']+)',
                r'FILING PERSON[:.]?\s*([A-Z][A-Za-z0-9\s\.,&\-\']+)',
            ]

            for pattern in name_patterns:
                match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    # Clean up name (remove trailing punctuation, extra spaces)
                    name = re.sub(r'\s+', ' ', name)
                    name = name.strip('.,;: ')
                    if len(name) > 3 and len(name) < 100:  # Sanity check
                        extracted['beneficial_owner_name'] = name
                        break

            # Extract address
            # Look for address after reporting person name
            address_patterns = [
                r'ADDRESS OF PRINCIPAL BUSINESS OFFICE[:]?\s*([^\n]+(?:\n[^\n]+){0,3})',
                r'BUSINESS ADDRESS[:]?\s*([^\n]+(?:\n[^\n]+){0,3})',
                r'PRINCIPAL OFFICE[:]?\s*([^\n]+(?:\n[^\n]+){0,3})',
            ]

            for pattern in address_patterns:
                match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    address = match.group(1).strip()
                    # Clean up address
                    address = re.sub(r'\s+', ' ', address)
                    address = address[:200]  # Limit length
                    extracted['beneficial_owner_address'] = address
                    break

            # Extract citizenship/country
            country_patterns = [
                r'CITIZENSHIP OR PLACE OF ORGANIZATION[:]?\s*([A-Za-z\s]+)',
                r'COUNTRY OF INCORPORATION[:]?\s*([A-Za-z\s]+)',
                r'JURISDICTION[:]?\s*([A-Za-z\s]+)',
            ]

            for pattern in country_patterns:
                match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    country = match.group(1).strip()
                    country = re.sub(r'\s+', ' ', country)
                    extracted['beneficial_owner_country'] = country
                    break

            # Extract percentage owned
            percent_patterns = [
                r'PERCENT OF CLASS REPRESENTED[:]?\s*([\d.]+)%?',
                r'PERCENTAGE[:]?\s*([\d.]+)%',
                r'(\d+\.?\d*)%?\s*(?:OF|of)\s*(?:CLASS|class)',
            ]

            for pattern in percent_patterns:
                match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    percent = match.group(1)
                    try:
                        extracted['percent_owned'] = float(percent)
                        break
                    except:
                        pass

            # Extract shares owned
            shares_patterns = [
                r'NUMBER OF SHARES[:]?\s*([\d,]+)',
                r'AGGREGATE AMOUNT BENEFICIALLY OWNED[:]?\s*([\d,]+)',
                r'SHARES OWNED[:]?\s*([\d,]+)',
            ]

            for pattern in shares_patterns:
                match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    shares = match.group(1).replace(',', '')
                    try:
                        extracted['shares_owned'] = int(shares)
                        break
                    except:
                        pass

            return extracted

        except Exception as e:
            print(f'  [ERROR] Parsing failed: {e}')
            return None

    def detect_chinese_beneficial_owner(self, name, address, country):
        """Detect if beneficial owner is Chinese"""
        if not name:
            return False, 0.0, None

        # Check name
        name_upper = name.upper()
        for keyword in self.chinese_keywords:
            if keyword in name_upper:
                return True, 0.90, f'Name match: {keyword}'

        # Check country
        if country:
            country_upper = country.upper()
            chinese_countries = ['CHINA', 'HONG KONG', 'PRC', "PEOPLE'S REPUBLIC"]
            for indicator in chinese_countries:
                if indicator in country_upper:
                    return True, 0.95, f'Country: {country}'

        # Check address
        if address:
            addr_upper = address.upper()
            chinese_locations = ['BEIJING', 'SHANGHAI', 'SHENZHEN', 'HONG KONG', 'CAYMAN']
            for location in chinese_locations:
                if location in addr_upper:
                    confidence = 0.90 if location != 'CAYMAN' else 0.70
                    return True, confidence, f'Address: {location}'

        return False, 0.0, None

    def update_filing_with_parsed_data(self, accession_number, parsed_data, is_chinese, detection_method, confidence):
        """Update database with parsed beneficial owner information"""
        try:
            self.cur.execute('''
                UPDATE sec_13d_13g_filings
                SET filer_name = ?,
                    filer_address = ?,
                    filer_country = ?,
                    percent_owned = ?,
                    shares_owned = ?,
                    is_chinese = ?,
                    detection_method = ?,
                    confidence_score = ?
                WHERE accession_number = ?
            ''', (
                parsed_data.get('beneficial_owner_name'),
                parsed_data.get('beneficial_owner_address'),
                parsed_data.get('beneficial_owner_country'),
                parsed_data.get('percent_owned'),
                parsed_data.get('shares_owned'),
                is_chinese,
                detection_method,
                confidence,
                accession_number
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f'  [ERROR] Database update failed: {e}')
            return False

    def parse_filings(self, limit=100):
        """Main parsing workflow"""
        print('=' * 80)
        print('SEC 13D/13G BENEFICIAL OWNER PARSER')
        print('=' * 80)
        print()

        filings = self.get_unparsed_filings(limit)

        if not filings:
            print('[INFO] No unparsed filings found')
            return

        print(f'\n[INFO] Parsing {len(filings)} filings...')
        print('[NOTE] Rate limiting: 1 request per second to respect SEC guidelines')
        print()

        for i, (accession, html_url, company_name, filing_date, form_type) in enumerate(filings, 1):
            print(f'[{i}/{len(filings)}] {accession} ({form_type}, {filing_date})')
            print(f'  Subject company: {company_name}')

            # Download filing
            html_content = self.download_filing(html_url)
            if not html_content:
                self.errors += 1
                time.sleep(1)
                continue

            # Parse document
            parsed_data = self.parse_13d_13g_document(html_content, form_type)
            if not parsed_data or not parsed_data.get('beneficial_owner_name'):
                print(f'  [WARN] Could not extract beneficial owner')
                self.errors += 1
                time.sleep(1)
                continue

            # Detect Chinese beneficial owner
            is_chinese, confidence, method = self.detect_chinese_beneficial_owner(
                parsed_data.get('beneficial_owner_name'),
                parsed_data.get('beneficial_owner_address'),
                parsed_data.get('beneficial_owner_country')
            )

            # Update database
            success = self.update_filing_with_parsed_data(
                accession, parsed_data, is_chinese, method, confidence
            )

            if success:
                self.parsed_count += 1
                if is_chinese:
                    self.chinese_found += 1
                    print(f'  [CHINESE] Beneficial owner: {parsed_data.get("beneficial_owner_name")}')
                    print(f'    Detection: {method}')
                    if parsed_data.get('percent_owned'):
                        print(f'    Ownership: {parsed_data.get("percent_owned")}%')
                else:
                    print(f'  [OK] Beneficial owner: {parsed_data.get("beneficial_owner_name")}')

            # Rate limiting (SEC guidelines: max 10 requests/second, we'll do 1/second to be safe)
            time.sleep(1)

        print()
        print('=' * 80)
        print('PARSING COMPLETE')
        print('=' * 80)
        print(f'Successfully parsed: {self.parsed_count}/{len(filings)}')
        print(f'Chinese beneficial owners found: {self.chinese_found}')
        print(f'Errors: {self.errors}')

    def generate_report(self):
        """Generate report on Chinese beneficial owners"""
        print()
        print('=' * 80)
        print('CHINESE BENEFICIAL OWNERS REPORT')
        print('=' * 80)

        # Get Chinese beneficial owners with properly parsed data
        self.cur.execute('''
            SELECT
                filer_name,
                company_name,
                form_type,
                filing_date,
                percent_owned,
                shares_owned,
                filer_country,
                detection_method
            FROM sec_13d_13g_filings
            WHERE is_chinese = 1
            AND filer_name != company_name
            ORDER BY filing_date DESC
            LIMIT 50
        ''')

        results = self.cur.fetchall()

        print(f'\nTotal Chinese beneficial owners (with parsed data): {len(results)}')

        if results:
            print('\nRecent Chinese acquisitions of US companies:')
            print()
            for row in results[:20]:
                filer, company, form, date, percent, shares, country, method = row
                print(f'  {filer}')
                print(f'    → Acquiring: {company}')
                print(f'    Form: {form}, Date: {date}')
                if percent:
                    print(f'    Ownership: {percent}%')
                if country:
                    print(f'    Country: {country}')
                print(f'    Detection: {method}')
                print()

    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    parser = SEC13DGParser()

    try:
        # Parse first 100 filings (can increase later)
        parser.parse_filings(limit=100)

        # Generate report
        parser.generate_report()

    except KeyboardInterrupt:
        print('\n[INFO] Interrupted by user')
    except Exception as e:
        print(f'[ERROR] Parsing failed: {e}')
        import traceback
        traceback.print_exc()
    finally:
        parser.close()

if __name__ == '__main__':
    main()
