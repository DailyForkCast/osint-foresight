#!/usr/bin/env python3
"""
SQLite-specific utilities for intelligence analysis
CORRECTED FOR OSINT FORESIGHT DATABASE SCHEMA
"""

import logging
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
from tqdm import tqdm
import re
from fuzzywuzzy import fuzz

from config_sqlite import CONFIG, ENTITY_VARIANTS, SOURCE_WEIGHTS

# Setup logging
def setup_logging(name='document_intel'):
    """Configure logging with both file and console output"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, CONFIG['log_level']))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # File handler
    import os
    os.makedirs(CONFIG['output_dir'], exist_ok=True)
    fh = logging.FileHandler(
        f"{CONFIG['output_dir']}/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    fh.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

logger = setup_logging()

def get_db_connection():
    """Get SQLite database connection with optimizations"""
    try:
        conn = sqlite3.connect(CONFIG['db_path'])
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        # Optimize for analysis
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA journal_mode = WAL")
        logger.info(f"Connected to SQLite database: {CONFIG['db_path']}")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def create_sqlite_functions(conn):
    """Create custom SQLite functions for analysis"""

    # Fuzzy matching function
    def fuzzy_match(str1, str2, threshold=85):
        if not str1 or not str2:
            return 0
        return 1 if fuzz.ratio(str1.lower(), str2.lower()) >= threshold else 0

    # Chinese character detection
    def has_chinese(text):
        if not text:
            return 0
        return 1 if re.search(r'[\u4e00-\u9fff]', text) else 0

    # Entity normalization
    def normalize_entity_sql(entity_name):
        if not entity_name:
            return entity_name
        return normalize_entity(entity_name)

    # Register functions
    conn.create_function("fuzzy_match", 3, fuzzy_match)
    conn.create_function("has_chinese", 1, has_chinese)
    conn.create_function("normalize_entity", 1, normalize_entity_sql)

    logger.info("Custom SQLite functions registered")

def normalize_entity(entity_name):
    """Normalize entity names across Chinese/English variations"""
    if not entity_name:
        return entity_name

    entity_lower = entity_name.lower().strip()

    # Check against known variants
    for canonical, variants in ENTITY_VARIANTS.items():
        if entity_lower in [v.lower() for v in variants]:
            return canonical

    return entity_name

def get_source_weight(source):
    """Get credibility weight for a source"""
    if not source:
        return SOURCE_WEIGHTS['Unknown']

    source_upper = source.upper()
    for key, weight in SOURCE_WEIGHTS.items():
        if key.upper() in source_upper:
            return weight

    return SOURCE_WEIGHTS['Unknown']

def create_sqlite_indexes(conn):
    """Create indexes for SQLite performance"""
    logger.info("Creating SQLite indexes...")

    indexes = [
        # Documents table (CORRECTED COLUMN NAMES)
        "CREATE INDEX IF NOT EXISTS idx_documents_publication ON documents(publication_date)",
        "CREATE INDEX IF NOT EXISTS idx_documents_publisher ON documents(publisher_org)",

        # Entity tables (CORRECTED COLUMN NAMES)
        "CREATE INDEX IF NOT EXISTS idx_doc_entities_text ON document_entities(entity_text)",
        "CREATE INDEX IF NOT EXISTS idx_doc_entities_doc ON document_entities(document_id)",
        "CREATE INDEX IF NOT EXISTS idx_report_entities_name ON report_entities(entity_name)",

        # MCF tables (CORRECTED)
        "CREATE INDEX IF NOT EXISTS idx_mcf_entities_name ON mcf_entities(name)",
        "CREATE INDEX IF NOT EXISTS idx_mcf_doc_entities_doc ON mcf_document_entities(doc_id)",
        "CREATE INDEX IF NOT EXISTS idx_mcf_doc_entities_ent ON mcf_document_entities(entity_id)"
    ]

    cursor = conn.cursor()
    for idx in indexes:
        try:
            cursor.execute(idx)
            conn.commit()
            logger.info(f"  Index created/verified: {idx.split('idx_')[1].split(' ')[0]}")
        except Exception as e:
            logger.warning(f"  Index creation issue: {e}")

def preflight_checks(conn):
    """Run preflight checks for SQLite database"""
    logger.info("Running preflight checks...")

    checks = {
        'documents_exist': "SELECT COUNT(*) FROM documents",
        'documents_with_content': "SELECT COUNT(*) FROM documents WHERE content_text IS NOT NULL AND LENGTH(content_text) > 0",
        'document_entities_exist': "SELECT COUNT(*) FROM document_entities",
        'mcf_documents_exist': "SELECT COUNT(*) FROM mcf_documents",
        'report_entities_exist': "SELECT COUNT(*) FROM report_entities",
        'chinese_content': "SELECT COUNT(*) FROM documents WHERE content_text LIKE '%中%' OR content_text LIKE '%国%'",
        'recent_documents': "SELECT COUNT(*) FROM documents WHERE date(publication_date) > date('now', '-1 year')"
    }

    results = {}
    cursor = conn.cursor()

    for check_name, query in checks.items():
        try:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            results[check_name] = count
            logger.info(f"Preflight check - {check_name}: {count:,}")

            if count == 0 and 'exist' in check_name:
                logger.warning(f"WARNING: No data found for {check_name}")
        except Exception as e:
            logger.error(f"Preflight check failed - {check_name}: {e}")
            results[check_name] = -1

    return results

def save_results(df, filename, format='csv'):
    """Save results with error handling"""
    import os
    os.makedirs(CONFIG['output_dir'], exist_ok=True)
    output_path = f"{CONFIG['output_dir']}/{filename}"

    try:
        if format == 'csv':
            df.to_csv(output_path, index=False, encoding='utf-8')
        elif format == 'json':
            df.to_json(output_path, orient='records', force_ascii=False, indent=2)
        elif format == 'excel':
            df.to_excel(output_path, index=False)

        logger.info(f"Results saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save results to {output_path}: {e}")
        raise

def execute_query_with_progress(query, conn, desc="Processing"):
    """Execute query with progress tracking - SQLite version"""
    logger.info(f"Executing query: {desc}")

    try:
        df = pd.read_sql_query(query, conn)
        logger.info(f"Query returned {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Query failed: {e}")
        logger.error(f"Query was: {query[:500]}...")
        raise
