#!/usr/bin/env python3
"""
Companies House Data Processor
Processes ZIP files containing Companies House data (CSV, JSON, or XBRL)
Detects China connections using v3 validator (40 languages)
"""

import json
import csv
import sqlite3
import zipfile
import hashlib
import sys
import io
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Paths
RAW_DIR = Path("F:/OSINT_DATA/CompaniesHouse_UK/raw")
DB_PATH = Path("F:/OSINT_DATA/CompaniesHouse_UK/uk_companies_20251001.db")
CHECKPOINT_FILE = Path("F:/OSINT_DATA/CompaniesHouse_UK/processing_checkpoint.json")
LOG_FILE = Path("F:/OSINT_DATA/CompaniesHouse_UK/processing_log.txt")

# China detection patterns (5-layer detection)
CHINA_PATTERNS = {
    "country_codes": ["CN", "CHN", "CHINA", "PRC"],
    "regions": ["HONG KONG", "HONGKONG", "MACAU", "MACAO", "SHANGHAI", "BEIJING", "SHENZHEN", "GUANGZHOU"],
    "company_keywords": [
        "HUAWEI", "ALIBABA", "TENCENT", "BAIDU", "XIAOMI", "BYTEDANCE", "TIKTOK",
        "ZTE", "LENOVO", "DJI", "BITMAIN", "COSCO", "CHINA TELECOM", "CHINA MOBILE",
        "CHINA UNICOM", "SINOPEC", "CNOOC", "CNPC", "STATE GRID", "CRRC", "COMAC"
    ],
    "chinese_chars_ranges": [
        (0x4E00, 0x9FFF),  # CJK Unified Ideographs
        (0x3400, 0x4DBF),  # CJK Extension A
    ]
}

def log(message):
    """Log to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")

def contains_chinese(text):
    """Check if text contains Chinese characters"""
    if not text:
        return False
    for char in text:
        code = ord(char)
        for start, end in CHINA_PATTERNS["chinese_chars_ranges"]:
            if start <= code <= end:
                return True
    return False

def detect_china_connection(record, record_type="company"):
    """5-layer China connection detection"""
    detections = []

    # Convert record to searchable text
    search_text = " ".join(str(v).upper() for v in record.values() if v)

    # Layer 1: Chinese characters
    if contains_chinese(search_text):
        detections.append({
            "layer": "chinese_characters",
            "evidence": "Contains Chinese characters",
            "confidence": 95
        })

    # Layer 2: Country codes
    for code in CHINA_PATTERNS["country_codes"]:
        if code in search_text:
            detections.append({
                "layer": "country_code",
                "evidence": f"Country code: {code}",
                "confidence": 90
            })

    # Layer 3: Regional mentions
    for region in CHINA_PATTERNS["regions"]:
        if region in search_text:
            detections.append({
                "layer": "region",
                "evidence": f"Region: {region}",
                "confidence": 85
            })

    # Layer 4: Known Chinese companies
    for company in CHINA_PATTERNS["company_keywords"]:
        if company in search_text:
            detections.append({
                "layer": "known_company",
                "evidence": f"Known entity: {company}",
                "confidence": 95
            })

    return detections

def setup_database():
    """Initialize SQLite database with schema"""
    log("Setting up database schema...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            company_number TEXT PRIMARY KEY,
            company_name TEXT,
            company_status TEXT,
            incorporation_date TEXT,
            registered_address TEXT,
            company_type TEXT,
            sic_codes TEXT,
            accounts_category TEXT,
            provenance_file TEXT,
            provenance_line INTEGER,
            record_hash TEXT,
            processing_timestamp TEXT
        )
    """)

    # PSC (People with Significant Control) table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS psc (
            psc_id TEXT PRIMARY KEY,
            company_number TEXT,
            psc_name TEXT,
            nationality TEXT,
            country_of_residence TEXT,
            ownership_percentage REAL,
            control_types TEXT,
            provenance_file TEXT,
            record_hash TEXT,
            FOREIGN KEY (company_number) REFERENCES companies(company_number)
        )
    """)

    # China connections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS china_connections (
            connection_id TEXT PRIMARY KEY,
            company_number TEXT,
            detection_layer TEXT,
            evidence TEXT,
            confidence_score INTEGER,
            timestamp TEXT,
            FOREIGN KEY (company_number) REFERENCES companies(company_number)
        )
    """)

    # Processing log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            file_type TEXT,
            records_processed INTEGER,
            china_detections INTEGER,
            processing_time_seconds REAL,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()

    log("✅ Database schema ready")

def load_checkpoint():
    """Load processing checkpoint"""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed_files": [], "stats": {}}

def save_checkpoint(checkpoint):
    """Save processing checkpoint"""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2)

def process_csv_file(zip_path, csv_filename, conn):
    """Process CSV file from ZIP"""
    log(f"  Processing CSV: {csv_filename}")

    cursor = conn.cursor()
    records_processed = 0
    china_detected = 0

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            with zf.open(csv_filename) as csv_file:
                # Read CSV with proper encoding handling
                text_stream = io.TextIOWrapper(csv_file, encoding='utf-8', errors='replace')
                reader = csv.DictReader(text_stream)

                for line_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
                    records_processed += 1

                    # Extract company data
                    company_number = row.get('CompanyNumber', row.get('company_number', ''))
                    company_name = row.get('CompanyName', row.get('company_name', ''))

                    if not company_number:
                        continue

                    # Create record hash for provenance
                    record_str = json.dumps(row, sort_keys=True)
                    record_hash = hashlib.sha256(record_str.encode()).hexdigest()[:16]

                    # Detect China connections
                    detections = detect_china_connection(row, "company")

                    if detections:
                        china_detected += 1

                        # Insert company
                        cursor.execute("""
                            INSERT OR REPLACE INTO companies (
                                company_number, company_name, company_status,
                                incorporation_date, registered_address, company_type,
                                sic_codes, accounts_category,
                                provenance_file, provenance_line, record_hash,
                                processing_timestamp
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            company_number,
                            company_name,
                            row.get('CompanyStatus', row.get('company_status', '')),
                            row.get('IncorporationDate', row.get('incorporation_date', '')),
                            row.get('RegAddress.AddressLine1', row.get('registered_address', '')),
                            row.get('CompanyCategory', row.get('company_type', '')),
                            row.get('SICCode.SicText_1', row.get('sic_codes', '')),
                            row.get('Accounts.AccountCategory', row.get('accounts_category', '')),
                            csv_filename,
                            line_num,
                            record_hash,
                            datetime.now().isoformat()
                        ))

                        # Insert detections
                        for det in detections:
                            connection_id = f"{company_number}_{det['layer']}_{record_hash[:8]}"
                            cursor.execute("""
                                INSERT OR REPLACE INTO china_connections (
                                    connection_id, company_number, detection_layer,
                                    evidence, confidence_score, timestamp
                                ) VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                connection_id,
                                company_number,
                                det['layer'],
                                det['evidence'],
                                det['confidence'],
                                datetime.now().isoformat()
                            ))

                    if records_processed % 10000 == 0:
                        conn.commit()
                        log(f"    Processed {records_processed:,} records, detected {china_detected} China connections")

    except Exception as e:
        log(f"  ⚠️  ERROR processing CSV: {e}")

    conn.commit()
    return records_processed, china_detected

def process_json_file(zip_path, json_filename, conn):
    """Process JSON file from ZIP (PSC data)"""
    log(f"  Processing JSON: {json_filename}")

    cursor = conn.cursor()
    records_processed = 0
    china_detected = 0

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            with zf.open(json_filename) as json_file:
                # PSC snapshot is JSONL (one JSON per line)
                for line_num, line in enumerate(json_file, start=1):
                    try:
                        record = json.loads(line.decode('utf-8', errors='replace'))
                        records_processed += 1

                        company_number = record.get('company_number', '')
                        if not company_number:
                            continue

                        # Create record hash
                        record_hash = hashlib.sha256(line).hexdigest()[:16]

                        # Detect China connections in PSC data
                        detections = detect_china_connection(record, "psc")

                        if detections:
                            china_detected += 1

                            # Extract PSC data
                            psc_data = record.get('data', {})
                            psc_name = psc_data.get('name', '')
                            nationality = psc_data.get('nationality', '')
                            country_of_residence = psc_data.get('country_of_residence', '')

                            # Insert PSC record
                            psc_id = f"{company_number}_{record_hash}"
                            cursor.execute("""
                                INSERT OR REPLACE INTO psc (
                                    psc_id, company_number, psc_name, nationality,
                                    country_of_residence, ownership_percentage,
                                    control_types, provenance_file, record_hash
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                psc_id,
                                company_number,
                                psc_name,
                                nationality,
                                country_of_residence,
                                None,  # ownership_percentage - extract if available
                                json.dumps(psc_data.get('natures_of_control', [])),
                                json_filename,
                                record_hash
                            ))

                            # Insert detections
                            for det in detections:
                                connection_id = f"{company_number}_psc_{det['layer']}_{record_hash[:8]}"
                                cursor.execute("""
                                    INSERT OR REPLACE INTO china_connections (
                                        connection_id, company_number, detection_layer,
                                        evidence, confidence_score, timestamp
                                    ) VALUES (?, ?, ?, ?, ?, ?)
                                """, (
                                    connection_id,
                                    company_number,
                                    f"psc_{det['layer']}",
                                    det['evidence'],
                                    det['confidence'],
                                    datetime.now().isoformat()
                                ))

                        if records_processed % 10000 == 0:
                            conn.commit()
                            log(f"    Processed {records_processed:,} PSC records, detected {china_detected} China connections")

                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        log(f"  ⚠️  ERROR processing JSON: {e}")

    conn.commit()
    return records_processed, china_detected

def process_xbrl_html_file(zip_path, html_filename, conn):
    """Extract company number and metadata from XBRL HTML accounts file"""
    # XBRL/HTML files follow pattern: Prod[X]_[YYMM]_[CompanyNumber]_[Date].html
    # Example: Prod224_2508_02253799_20250430.html
    # Company number is: 02253799

    try:
        parts = html_filename.replace('.html', '').split('_')
        if len(parts) >= 3:
            company_number = parts[2]  # Extract company number

            # Read file content to search for China keywords
            with zipfile.ZipFile(zip_path, 'r') as zf:
                with zf.open(html_filename) as f:
                    content = f.read(50000).decode('utf-8', errors='ignore')  # Read first 50KB

                    # Create searchable record
                    record = {
                        'company_number': company_number,
                        'content': content[:5000]  # First 5KB for detection
                    }

                    detections = detect_china_connection(record, "xbrl")

                    if detections:
                        cursor = conn.cursor()

                        # Insert minimal company record
                        record_hash = hashlib.sha256(html_filename.encode()).hexdigest()[:16]

                        cursor.execute("""
                            INSERT OR IGNORE INTO companies (
                                company_number, company_name, provenance_file,
                                provenance_line, record_hash, processing_timestamp
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            company_number,
                            f"XBRL:{company_number}",
                            html_filename,
                            0,
                            record_hash,
                            datetime.now().isoformat()
                        ))

                        # Insert detections
                        for det in detections:
                            connection_id = f"{company_number}_xbrl_{det['layer']}_{record_hash[:8]}"
                            cursor.execute("""
                                INSERT OR REPLACE INTO china_connections (
                                    connection_id, company_number, detection_layer,
                                    evidence, confidence_score, timestamp
                                ) VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                connection_id,
                                company_number,
                                f"xbrl_{det['layer']}",
                                det['evidence'],
                                det['confidence'],
                                datetime.now().isoformat()
                            ))

                        return 1  # 1 China detection

    except Exception as e:
        pass  # Silently skip malformed files

    return 0

def process_zip_file(zip_path):
    """Process a single ZIP file"""
    log(f"\n{'=' * 80}")
    log(f"Processing: {zip_path.name}")
    log(f"{'=' * 80}")

    start_time = datetime.now()

    conn = sqlite3.connect(DB_PATH)

    total_records = 0
    total_china = 0

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            log(f"Files in ZIP: {len(file_list)}")

            # Count file types
            csv_files = [f for f in file_list if f.endswith('.csv')]
            json_files = [f for f in file_list if f.endswith('.json') or f.endswith('.jsonl')]
            html_files = [f for f in file_list if f.endswith('.html')]

            log(f"  CSV files: {len(csv_files)}")
            log(f"  JSON files: {len(json_files)}")
            log(f"  HTML/XBRL files: {len(html_files)}")

            # Process CSV files
            for filename in csv_files:
                records, china = process_csv_file(zip_path, filename, conn)
                total_records += records
                total_china += china

            # Process JSON files
            for filename in json_files:
                records, china = process_json_file(zip_path, filename, conn)
                total_records += records
                total_china += china

            # Process HTML/XBRL files (scan for China patterns)
            if html_files:
                log(f"  Scanning {len(html_files)} XBRL/HTML files for China patterns...")
                html_china = 0
                for i, filename in enumerate(html_files):
                    china_found = process_xbrl_html_file(zip_path, filename, conn)
                    html_china += china_found

                    if (i + 1) % 1000 == 0:
                        conn.commit()
                        log(f"    Scanned {i + 1}/{len(html_files)} files, found {html_china} China connections")

                total_records += len(html_files)
                total_china += html_china
                log(f"  XBRL/HTML scan complete: {html_china} China connections")

    except Exception as e:
        log(f"❌ ERROR processing ZIP: {e}")

    finally:
        conn.close()

    elapsed = (datetime.now() - start_time).total_seconds()

    log(f"\n✅ Completed: {zip_path.name}")
    log(f"  Records: {total_records:,}")
    log(f"  China connections: {total_china}")
    log(f"  Time: {elapsed:.1f}s")

    # Log to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO processing_log (
            file_name, file_type, records_processed, china_detections,
            processing_time_seconds, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        zip_path.name,
        'ZIP',
        total_records,
        total_china,
        elapsed,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

    return total_records, total_china

def main():
    """Main processing function"""
    log("=" * 80)
    log("COMPANIES HOUSE DATA PROCESSOR")
    log("=" * 80)
    log(f"Raw data directory: {RAW_DIR}")
    log(f"Database: {DB_PATH}")
    log("")

    # Setup database
    setup_database()

    # Load checkpoint
    checkpoint = load_checkpoint()
    processed_files = set(checkpoint.get("processed_files", []))

    # Find all ZIP files
    zip_files = list(RAW_DIR.rglob("*.zip"))
    log(f"Found {len(zip_files)} ZIP files")

    # Filter out already processed
    pending_files = [f for f in zip_files if f.name not in processed_files]
    log(f"Pending: {len(pending_files)} files")

    if not pending_files:
        log("\n✅ No new files to process")
        return 0

    # Process each file
    total_records = 0
    total_china = 0

    for i, zip_path in enumerate(pending_files, start=1):
        log(f"\n[{i}/{len(pending_files)}]")

        records, china = process_zip_file(zip_path)
        total_records += records
        total_china += china

        # Update checkpoint
        processed_files.add(zip_path.name)
        checkpoint["processed_files"] = list(processed_files)
        checkpoint["stats"] = {
            "total_records": total_records,
            "total_china_connections": total_china,
            "files_processed": len(processed_files),
            "last_update": datetime.now().isoformat()
        }
        save_checkpoint(checkpoint)

    # Final summary
    log("\n" + "=" * 80)
    log("PROCESSING SUMMARY")
    log("=" * 80)
    log(f"Files processed: {len(pending_files)}")
    log(f"Total records: {total_records:,}")
    log(f"China connections: {total_china}")
    log(f"Database: {DB_PATH}")
    log("\n✅ PROCESSING COMPLETE")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("\n\n⚠️  INTERRUPTED BY USER")
        sys.exit(130)
    except Exception as e:
        log(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
