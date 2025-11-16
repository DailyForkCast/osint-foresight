#!/usr/bin/env python3
"""
Database Helper Module
PostgreSQL operations for OSINT Foresight Master Database

Handles:
- Connection management with pooling
- Document insertion with deduplication
- Batch operations
- Queries and analytics
"""

import os
import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool, extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.schemas.unified_schema import UnifiedDocument

logger = logging.getLogger(__name__)


class DatabaseHelper:
    """
    PostgreSQL database helper for OSINT Foresight

    Features:
    - Connection pooling
    - Automatic deduplication via hash
    - Batch inserts
    - Transaction management
    - Statistics tracking
    """

    def __init__(self,
                 host: str = None,
                 port: int = None,
                 database: str = None,
                 user: str = None,
                 password: str = None,
                 pool_size: int = 10):
        """
        Initialize database connection

        Args:
            host: Database host (default from env or localhost)
            port: Database port (default from env or 5432)
            database: Database name (default from env or osint_foresight)
            user: Database user (default from env or postgres)
            password: Database password (default from env)
            pool_size: Connection pool size (default 10)
        """
        # Get connection params from env or defaults
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', 5432))
        self.database = database or os.getenv('DB_NAME', 'osint_foresight')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', '')

        # Create connection pool
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=pool_size,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"Database pool created: {self.database}@{self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise

        # Stats
        self.stats = {
            'inserts': 0,
            'duplicates_skipped': 0,
            'errors': 0,
            'batch_inserts': 0
        }

    @contextmanager
    def get_connection(self):
        """
        Get connection from pool (context manager)

        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                ...
        """
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    def close(self):
        """Close all connections in pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database pool closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    # =========================================================================
    # DOCUMENT OPERATIONS
    # =========================================================================

    def check_duplicate(self, hash_sha256: str) -> Optional[int]:
        """
        Check if document with hash exists

        Args:
            hash_sha256: SHA256 hash of document

        Returns:
            Document ID if exists, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM documents WHERE hash_sha256 = %s",
                (hash_sha256,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def insert_document(self,
                       doc: UnifiedDocument,
                       skip_duplicates: bool = True) -> Optional[int]:
        """
        Insert UnifiedDocument into database

        Args:
            doc: UnifiedDocument to insert
            skip_duplicates: Skip if hash already exists (default True)

        Returns:
            Document ID if inserted, None if skipped (duplicate)

        Raises:
            Exception: If insert fails
        """
        # Check for duplicate
        if skip_duplicates:
            existing_id = self.check_duplicate(doc.file_metadata.hash_sha256)
            if existing_id:
                self.stats['duplicates_skipped'] += 1
                logger.debug(f"Duplicate skipped: {doc.file_metadata.hash_sha256[:16]}...")
                return None

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Insert main document
                cursor.execute("""
                    INSERT INTO documents (
                        document_id, hash_sha256, text_hash_sha256,
                        document_type, publisher_org, publisher_type,
                        publisher_country, publisher_domain, verified_publisher,
                        publication_date, publication_date_iso,
                        date_source, date_confidence, last_modified,
                        title, title_en, description, content_text, content_length, language,
                        file_size_bytes, file_format, canonical_url,
                        discovery_method, discovery_timestamp, fetch_url,
                        archive_url, archive_timestamp, mirror_source_type,
                        safe_access_validated, blocked_domain_detected,
                        extraction_timestamp, extraction_ok, qa_passed,
                        redteam_reviewed, verified_safe_source, reliability_weight,
                        duplicate_detected, duplicate_of,
                        collection_run_id, collector_name, collector_version,
                        extensions
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                """, (
                    doc.document_id,
                    doc.file_metadata.hash_sha256,
                    doc.file_metadata.text_hash_sha256,
                    doc.document_type.value,
                    doc.publisher.publisher_org,
                    doc.publisher.publisher_type.value,
                    doc.publisher.publisher_country,
                    doc.publisher.publisher_domain,
                    doc.publisher.verified_publisher,
                    doc.dates.publication_date_iso,  # Will be converted to DATE
                    doc.dates.publication_date_iso,
                    doc.dates.date_source,
                    doc.dates.date_confidence.value if doc.dates.date_confidence else None,
                    doc.dates.last_modified,
                    doc.content.title,
                    doc.content.title_en,
                    doc.content.description,
                    doc.content.content_text,
                    doc.content.content_length,
                    doc.content.language.value,
                    doc.file_metadata.file_size_bytes,
                    doc.file_metadata.file_format,
                    doc.file_metadata.canonical_url,
                    doc.provenance.discovery_method,
                    doc.provenance.discovery_timestamp,
                    doc.provenance.fetch_url,
                    doc.provenance.archive_url,
                    doc.provenance.archive_timestamp,
                    doc.provenance.mirror_source_type.value,
                    doc.provenance.safe_access_validated,
                    doc.provenance.blocked_domain_detected,
                    doc.extraction.extraction_timestamp,
                    doc.extraction.extraction_ok,
                    doc.extraction.qa_passed,
                    doc.extraction.redteam_reviewed,
                    doc.extraction.verified_safe_source,
                    doc.extraction.reliability_weight,
                    doc.extraction.duplicate_detected,
                    doc.extraction.duplicate_of,
                    doc.collection_run_id,
                    doc.collector_name,
                    doc.collector_version,
                    json.dumps(doc.extensions) if doc.extensions else '{}'
                ))

                doc_id = cursor.fetchone()[0]

                # Insert topics
                if doc.content.topics:
                    for topic in doc.content.topics:
                        cursor.execute("""
                            INSERT INTO document_topics (document_id, topic)
                            VALUES (%s, %s)
                            ON CONFLICT (document_id, topic) DO NOTHING
                        """, (doc_id, topic.value))

                # Insert keywords
                if doc.content.keywords:
                    for keyword in doc.content.keywords:
                        cursor.execute("""
                            INSERT INTO document_keywords (document_id, keyword)
                            VALUES (%s, %s)
                            ON CONFLICT (document_id, keyword) DO NOTHING
                        """, (doc_id, keyword))

                # Insert entities
                if doc.content.entities:
                    for entity in doc.content.entities:
                        cursor.execute("""
                            INSERT INTO document_entities (document_id, entity_name)
                            VALUES (%s, %s)
                            ON CONFLICT (document_id, entity_name) DO NOTHING
                        """, (doc_id, entity))

                conn.commit()
                self.stats['inserts'] += 1
                logger.debug(f"Document inserted: ID={doc_id}, hash={doc.file_metadata.hash_sha256[:16]}...")
                return doc_id

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Error inserting document: {e}")
            raise

    def batch_insert_documents(self,
                              docs: List[UnifiedDocument],
                              skip_duplicates: bool = True,
                              batch_size: int = 1000) -> Dict[str, int]:
        """
        Insert multiple documents in batches

        Args:
            docs: List of UnifiedDocuments
            skip_duplicates: Skip duplicates (default True)
            batch_size: Batch size for commit (default 1000)

        Returns:
            Dict with stats: {'inserted': N, 'skipped': N, 'errors': N}
        """
        batch_stats = {'inserted': 0, 'skipped': 0, 'errors': 0}

        logger.info(f"Batch insert: {len(docs)} documents, batch_size={batch_size}")

        for i, doc in enumerate(docs):
            try:
                doc_id = self.insert_document(doc, skip_duplicates)
                if doc_id:
                    batch_stats['inserted'] += 1
                else:
                    batch_stats['skipped'] += 1

                # Log progress
                if (i + 1) % batch_size == 0:
                    logger.info(f"Progress: {i+1}/{len(docs)} documents processed")

            except Exception as e:
                batch_stats['errors'] += 1
                logger.error(f"Error in batch insert (doc {i}): {e}")
                continue

        self.stats['batch_inserts'] += 1
        logger.info(f"Batch insert complete: {batch_stats}")
        return batch_stats

    # =========================================================================
    # QUERY OPERATIONS
    # =========================================================================

    def get_document_by_hash(self, hash_sha256: str) -> Optional[Dict[str, Any]]:
        """Get document by hash"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(
                "SELECT * FROM documents WHERE hash_sha256 = %s",
                (hash_sha256,)
            )
            result = cursor.fetchone()
            return dict(result) if result else None

    def get_documents_by_country(self,
                                country_code: str,
                                limit: int = 100) -> List[Dict[str, Any]]:
        """Get documents by country"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM documents
                WHERE publisher_country = %s
                  AND duplicate_detected = FALSE
                ORDER BY publication_date DESC
                LIMIT %s
            """, (country_code, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_documents_by_date_range(self,
                                   start_date: str,
                                   end_date: str,
                                   country_code: Optional[str] = None,
                                   limit: int = 1000) -> List[Dict[str, Any]]:
        """Get documents by date range"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

            if country_code:
                cursor.execute("""
                    SELECT * FROM documents
                    WHERE publication_date BETWEEN %s AND %s
                      AND publisher_country = %s
                      AND duplicate_detected = FALSE
                    ORDER BY publication_date DESC
                    LIMIT %s
                """, (start_date, end_date, country_code, limit))
            else:
                cursor.execute("""
                    SELECT * FROM documents
                    WHERE publication_date BETWEEN %s AND %s
                      AND duplicate_detected = FALSE
                    ORDER BY publication_date DESC
                    LIMIT %s
                """, (start_date, end_date, limit))

            return [dict(row) for row in cursor.fetchall()]

    def search_full_text(self,
                        query: str,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        Full-text search in title and content

        Args:
            query: Search query (e.g., 'quantum & computing')
            limit: Max results

        Returns:
            List of matching documents
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("""
                SELECT *,
                       ts_rank(to_tsvector('english', title || ' ' || content_text),
                               to_tsquery('english', %s)) as rank
                FROM documents
                WHERE to_tsvector('english', title || ' ' || content_text) @@ to_tsquery('english', %s)
                  AND duplicate_detected = FALSE
                ORDER BY rank DESC
                LIMIT %s
            """, (query, query, limit))
            return [dict(row) for row in cursor.fetchall()]

    # =========================================================================
    # STATISTICS & ANALYTICS
    # =========================================================================

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("SELECT * FROM data_quality_metrics")
            result = cursor.fetchone()
            return dict(result) if result else {}

    def get_country_stats(self) -> List[Dict[str, Any]]:
        """Get documents by country"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("SELECT * FROM documents_by_country ORDER BY document_count DESC LIMIT 50")
            return [dict(row) for row in cursor.fetchall()]

    def get_topic_distribution(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Get topic distribution"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT topic, COUNT(*) as count
                FROM document_topics
                GROUP BY topic
                ORDER BY count DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()

    def get_recent_documents(self,
                            days: int = 30,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent documents"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM documents
                WHERE publication_date >= CURRENT_DATE - INTERVAL '%s days'
                  AND duplicate_detected = FALSE
                ORDER BY publication_date DESC
                LIMIT %s
            """, (days, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_helper_stats(self) -> Dict[str, Any]:
        """Get helper statistics"""
        return {
            **self.stats,
            'pool_stats': {
                'size': self.pool.maxconn if self.pool else 0,
                'closed': self.pool.closed if self.pool else True
            }
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_database_if_not_exists(host: str = 'localhost',
                                 port: int = 5432,
                                 database: str = 'osint_foresight',
                                 user: str = 'postgres',
                                 password: str = ''):
    """
    Create database if it doesn't exist

    Args:
        host: Database host
        port: Database port
        database: Database name to create
        user: Admin user
        password: Admin password
    """
    # Connect to postgres database (always exists)
    conn = psycopg2.connect(
        host=host,
        port=port,
        database='postgres',
        user=user,
        password=password
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
    exists = cursor.fetchone()

    if not exists:
        logger.info(f"Creating database: {database}")
        cursor.execute(f"CREATE DATABASE {database}")
        logger.info(f"Database created: {database}")
    else:
        logger.info(f"Database already exists: {database}")

    cursor.close()
    conn.close()


def run_schema(schema_file: str,
              host: str = 'localhost',
              port: int = 5432,
              database: str = 'osint_foresight',
              user: str = 'postgres',
              password: str = ''):
    """
    Run schema.sql file

    Args:
        schema_file: Path to schema.sql
        host: Database host
        port: Database port
        database: Database name
        user: Database user
        password: Database password
    """
    logger.info(f"Running schema: {schema_file}")

    with open(schema_file, 'r') as f:
        schema_sql = f.read()

    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    try:
        cursor.execute(schema_sql)
        conn.commit()
        logger.info("Schema executed successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error executing schema: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Test connection
    print("Testing database connection...")

    try:
        with DatabaseHelper() as db:
            print(f"✓ Connected to {db.database}")

            # Get stats
            stats = db.get_database_stats()
            print(f"✓ Database stats: {stats}")

            # Get country stats
            countries = db.get_country_stats()
            print(f"✓ Countries: {len(countries)}")

            print("✓ All tests passed!")

    except Exception as e:
        print(f"✗ Error: {e}")
