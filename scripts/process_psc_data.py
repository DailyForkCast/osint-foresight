#!/usr/bin/env python3
"""
PSC (People with Significant Control) Data Processor
Processes UK beneficial ownership data from Companies House PSC snapshot
Detects Chinese beneficial owners and control structures
"""

import json
import sqlite3
import zipfile
import hashlib
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Paths
PSC_ZIP = Path("F:/OSINT_DATA/CompaniesHouse_UK/raw/persons-with-significant-control-snapshot-2025-09-30.zip")
DB_PATH = Path("F:/OSINT_DATA/CompaniesHouse_UK/uk_companies_20251001.db")
LOG_FILE = Path("F:/OSINT_DATA/CompaniesHouse_UK/psc_processing_log.txt")
CHECKPOINT_FILE = Path("F:/OSINT_DATA/CompaniesHouse_UK/psc_checkpoint.json")

# China detection patterns
CHINA_KEYWORDS = {
    "nationalities": ["Chinese", "China", "PRC"],
    "countries": ["China", "PRC", "Hong Kong", "Macau", "Macao", "CN", "HK", "MO"],
    "regions": ["Beijing", "Shanghai", "Shenzhen", "Guangzhou", "Chengdu", "Hangzhou"]
}

def log(message):
    """Log to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")

def is_china_related(psc_data):
    """Detect if PSC is China-related"""
    detections = []

    # Check nationality
    nationality = psc_data.get('nationality', '')
    if any(keyword.lower() in nationality.lower() for keyword in CHINA_KEYWORDS["nationalities"]):
        detections.append({
            "layer": "psc_nationality",
            "evidence": f"Nationality: {nationality}",
            "confidence": 95
        })

    # Check country of residence
    country_of_residence = psc_data.get('country_of_residence', '')
    if any(keyword.lower() in country_of_residence.lower() for keyword in CHINA_KEYWORDS["countries"]):
        detections.append({
            "layer": "psc_residence",
            "evidence": f"Country of residence: {country_of_residence}",
            "confidence": 90
        })

    # Check address
    address = psc_data.get('address', {})
    if isinstance(address, dict):
        address_str = ' '.join(str(v) for v in address.values() if v)
        if any(keyword.lower() in address_str.lower() for keyword in CHINA_KEYWORDS["countries"] + CHINA_KEYWORDS["regions"]):
            detections.append({
                "layer": "psc_address",
                "evidence": f"Address contains China reference: {address_str[:100]}",
                "confidence": 85
            })

    # Check name (for Chinese characters or Chinese company names)
    name = psc_data.get('name', '')
    if has_chinese_chars(name):
        detections.append({
            "layer": "psc_chinese_name",
            "evidence": f"Name contains Chinese characters: {name}",
            "confidence": 95
        })

    return detections

def has_chinese_chars(text):
    """Check if text contains Chinese characters"""
    if not text:
        return False
    chinese_ranges = [
        (0x4E00, 0x9FFF),  # CJK Unified Ideographs
        (0x3400, 0x4DBF),  # CJK Extension A
    ]
    for char in text:
        code = ord(char)
        for start, end in chinese_ranges:
            if start <= code <= end:
                return True
    return False

def setup_database():
    """Ensure PSC table exists in database"""
    log("Setting up database schema for PSC data...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if companies table exists (should already exist from main processor)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies'")
    if not cursor.fetchone():
        # Create companies table if it doesn't exist
        cursor.execute("""
            CREATE TABLE companies (
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
        log("  Created companies table")

    # Check if PSC table exists and has correct schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='psc'")
    psc_exists = cursor.fetchone()

    if psc_exists:
        # Check what columns exist and add missing ones
        cursor.execute("PRAGMA table_info(psc)")
        existing_columns = [col[1] for col in cursor.fetchall()]

        required_columns = {
            'psc_kind': 'TEXT',
            'address': 'TEXT',
            'natures_of_control': 'TEXT',
            'notified_on': 'TEXT',
            'ceased_on': 'TEXT',
            'processing_timestamp': 'TEXT'
        }

        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                cursor.execute(f"ALTER TABLE psc ADD COLUMN {col_name} {col_type}")
                log(f"  Added {col_name} column to existing PSC table")
    else:
        # Create PSC table
        cursor.execute("""
            CREATE TABLE psc (
                psc_id TEXT PRIMARY KEY,
                company_number TEXT,
                psc_name TEXT,
                psc_kind TEXT,
                nationality TEXT,
                country_of_residence TEXT,
                address TEXT,
                natures_of_control TEXT,
                notified_on TEXT,
                ceased_on TEXT,
                provenance_file TEXT,
                record_hash TEXT,
                processing_timestamp TEXT,
                FOREIGN KEY (company_number) REFERENCES companies(company_number)
            )
        """)
        log("  Created PSC table")

    # Ensure china_connections table exists
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

    conn.commit()
    conn.close()

    log("✅ Database schema ready for PSC processing")

def load_checkpoint():
    """Load processing checkpoint"""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"records_processed": 0, "china_pscs_found": 0, "last_company_number": None}

def save_checkpoint(checkpoint):
    """Save processing checkpoint"""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2)

def process_psc_snapshot():
    """Process the PSC snapshot file"""
    log("=" * 80)
    log("PSC (PEOPLE WITH SIGNIFICANT CONTROL) PROCESSOR")
    log("=" * 80)
    log(f"PSC Snapshot: {PSC_ZIP}")
    log(f"Database: {DB_PATH}")
    log("")

    if not PSC_ZIP.exists():
        log(f"❌ ERROR: PSC snapshot not found at {PSC_ZIP}")
        return 1

    # Setup database
    setup_database()

    # Load checkpoint
    checkpoint = load_checkpoint()
    records_processed = checkpoint["records_processed"]
    china_pscs_found = checkpoint["china_pscs_found"]
    last_company_number = checkpoint.get("last_company_number")

    log(f"Checkpoint loaded: {records_processed:,} records processed, {china_pscs_found} China PSCs found")
    log(f"Starting PSC processing...")
    log("")

    # Open database connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    start_time = datetime.now()
    skip_until = last_company_number if last_company_number else None
    skipping = skip_until is not None

    try:
        # Open ZIP file
        log(f"Opening ZIP: {PSC_ZIP.name}")
        with zipfile.ZipFile(PSC_ZIP, 'r') as zf:
            # PSC snapshot should contain one .txt file (JSONL format)
            file_list = zf.namelist()
            log(f"Files in ZIP: {file_list}")

            psc_file = [f for f in file_list if f.endswith('.txt')][0]
            log(f"Processing: {psc_file}")
            log("")

            with zf.open(psc_file) as f:
                for line_num, line in enumerate(f, start=1):
                    try:
                        # Parse JSON line
                        psc_record = json.loads(line.decode('utf-8', errors='replace'))

                        company_number = psc_record.get('company_number', '')
                        if not company_number:
                            continue

                        # Skip until checkpoint
                        if skipping:
                            if company_number == skip_until:
                                skipping = False
                                log(f"Resuming from checkpoint: {company_number}")
                            continue

                        records_processed += 1

                        # Extract PSC data
                        psc_data = psc_record.get('data', {})
                        psc_name = psc_data.get('name', '')
                        psc_kind = psc_data.get('kind', '')

                        # Detect China connections
                        detections = is_china_related(psc_data)

                        if detections:
                            china_pscs_found += 1

                            # Create record hash
                            record_hash = hashlib.sha256(line).hexdigest()[:16]
                            psc_id = f"{company_number}_{record_hash}"

                            # Insert PSC record
                            cursor.execute("""
                                INSERT OR REPLACE INTO psc (
                                    psc_id, company_number, psc_name, psc_kind,
                                    nationality, country_of_residence, address,
                                    natures_of_control, notified_on, ceased_on,
                                    provenance_file, record_hash, processing_timestamp
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                psc_id,
                                company_number,
                                psc_name,
                                psc_kind,
                                psc_data.get('nationality', ''),
                                psc_data.get('country_of_residence', ''),
                                json.dumps(psc_data.get('address', {})),
                                json.dumps(psc_data.get('natures_of_control', [])),
                                psc_data.get('notified_on', ''),
                                psc_data.get('ceased_on', ''),
                                psc_file,
                                record_hash,
                                datetime.now().isoformat()
                            ))

                            # Insert China connections
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
                                    det['layer'],
                                    det['evidence'],
                                    det['confidence'],
                                    datetime.now().isoformat()
                                ))

                        # Progress logging and checkpointing
                        if records_processed % 100000 == 0:
                            conn.commit()
                            elapsed = (datetime.now() - start_time).total_seconds()
                            rate = records_processed / elapsed if elapsed > 0 else 0
                            log(f"  Processed {records_processed:,} records, found {china_pscs_found} China PSCs ({rate:.0f} rec/sec)")

                            # Save checkpoint
                            checkpoint = {
                                "records_processed": records_processed,
                                "china_pscs_found": china_pscs_found,
                                "last_company_number": company_number
                            }
                            save_checkpoint(checkpoint)

                    except json.JSONDecodeError:
                        continue  # Skip malformed JSON
                    except Exception as e:
                        log(f"  ⚠️  Error processing line {line_num}: {e}")
                        continue

    except Exception as e:
        log(f"❌ ERROR during processing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        conn.commit()
        conn.close()

    elapsed = (datetime.now() - start_time).total_seconds()

    # Final summary
    log("")
    log("=" * 80)
    log("PSC PROCESSING COMPLETE")
    log("=" * 80)
    log(f"Total records processed: {records_processed:,}")
    log(f"China PSCs found: {china_pscs_found}")
    log(f"Processing time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    log(f"Rate: {records_processed/elapsed:.0f} records/second")
    log(f"Database: {DB_PATH}")
    log("")
    log("✅ PSC PROCESSING SUCCESSFUL")

    # Final checkpoint
    checkpoint = {
        "records_processed": records_processed,
        "china_pscs_found": china_pscs_found,
        "last_company_number": None,  # Processing complete
        "completed_at": datetime.now().isoformat()
    }
    save_checkpoint(checkpoint)

    return 0

if __name__ == "__main__":
    try:
        sys.exit(process_psc_snapshot())
    except KeyboardInterrupt:
        log("\n\n⚠️  INTERRUPTED BY USER")
        log("Progress saved to checkpoint. Run again to resume.")
        sys.exit(130)
    except Exception as e:
        log(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
