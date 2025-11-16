#!/usr/bin/env python3
"""
Import Think Tank Reports into Enhanced Database Schema
========================================================
Populates the thinktank_reports table with PDF reports from F:/Reports,
leveraging the new schema with controlled vocabularies, junction tables,
and enhanced metadata tracking.

Usage:
    python scripts/import_thinktank_reports.py

Features:
    - PDF metadata extraction (title, author, date, pages)
    - Auto-topic assignment using ref_topics taxonomy
    - Auto-region detection (MCF/Europe/Arctic flags)
    - File hash calculation (SHA-256)
    - Quality and completeness scoring
    - Many-to-many topic/region assignments
"""

import sqlite3
import hashlib
import re
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# PDF parsing (install: pip install PyPDF2)
try:
    import PyPDF2
except ImportError:
    print("[WARNING] PyPDF2 not installed. Install with: pip install PyPDF2")
    PyPDF2 = None


# =============================================================================
# CONFIGURATION
# =============================================================================

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
REPORTS_DIR = Path("F:/Reports")

# Publisher mappings (filename patterns -> publisher info)
PUBLISHER_PATTERNS = {
    "CSET-": {"org": "Center for Security and Emerging Technology", "type": "think_tank"},
    "ASPI": {"org": "Australian Strategic Policy Institute", "type": "think_tank"},
    "CSIS": {"org": "Center for Strategic and International Studies", "type": "think_tank"},
    "MILITARY-AND-SECURITY-DEVELOPMENTS": {"org": "U.S. Department of Defense", "type": "government"},
}

# Topic keyword mappings (keywords -> topic_slug from ref_topics)
TOPIC_KEYWORDS = {
    "mcf": ["military-civil fusion", "mcf", "军民融合", "civil-military"],
    "tech_transfer": ["technology transfer", "tech transfer", "know-how", "ip theft"],
    "defense": ["defense", "military", "weapons", "armament", "pla", "armed forces"],
    "cyber": ["cyber", "cybersecurity", "hacking", "apt", "intrusion"],
    "space": ["space", "satellite", "launch", "orbital", "remote sensing", "beidou"],
    "ai_ml": ["artificial intelligence", "machine learning", "deep learning", "neural network", "ai"],
    "quantum": ["quantum", "qubit", "quantum computing", "quantum communications"],
    "semiconductors": ["semiconductor", "chip", "lithography", "asml", "tsmc", "fab"],
    "biotech": ["biotech", "biological", "crispr", "gene editing", "synthetic biology"],
    "energy": ["energy", "battery", "solar", "nuclear", "renewable"],
    "telecom": ["5g", "6g", "telecom", "huawei", "zte", "telecommunications"],
    "supply_chain": ["supply chain", "sourcing", "manufacturing", "procurement"],
    "critical_tech": ["critical technology", "emerging tech", "dual-use"],
    "policy": ["policy", "regulation", "export control", "sanctions", "compliance"],
}

# Region keyword mappings
REGION_KEYWORDS = {
    "europe": ["europe", "european", "eu ", "european union", "nato", "brussels"],
    "east_asia": ["china", "chinese", "prc", "peoples republic", "beijing", "taiwan", "japan", "korea"],
    "north_america": ["united states", "u.s.", "usa", "america", "canada"],
    "arctic": ["arctic", "polar", "greenland", "northern sea route"],
}


# =============================================================================
# PDF METADATA EXTRACTION
# =============================================================================

def extract_pdf_metadata(filepath: Path) -> Dict:
    """Extract metadata from PDF file."""
    metadata = {
        "title": None,
        "author": None,
        "publisher": None,
        "publication_date": None,
        "pages": 0,
        "file_size_bytes": 0,
        "hash_sha256": None,
        "text_sample": "",
    }

    # File stats
    metadata["file_size_bytes"] = filepath.stat().st_size

    # Calculate SHA-256 hash
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    metadata["hash_sha256"] = sha256_hash.hexdigest()

    # Extract PDF metadata if PyPDF2 available
    if PyPDF2:
        try:
            with open(filepath, "rb") as f:
                pdf = PyPDF2.PdfReader(f)

                # Page count
                metadata["pages"] = len(pdf.pages)

                # PDF metadata
                info = pdf.metadata
                if info:
                    metadata["title"] = info.get("/Title", None)
                    metadata["author"] = info.get("/Author", None)

                    # Try to extract date
                    creation_date = info.get("/CreationDate", None)
                    if creation_date:
                        # Parse PDF date format (D:YYYYMMDDHHmmSS)
                        date_match = re.search(r"D:(\d{4})(\d{2})(\d{2})", str(creation_date))
                        if date_match:
                            year, month, day = date_match.groups()
                            metadata["publication_date"] = f"{year}-{month}-{day}"

                # Extract first page text for topic detection
                if len(pdf.pages) > 0:
                    try:
                        first_page = pdf.pages[0].extract_text()
                        metadata["text_sample"] = first_page[:2000]  # First 2000 chars
                    except Exception:
                        pass
        except Exception as e:
            print(f"[WARNING] Could not extract PDF metadata from {filepath.name}: {e}")

    # Fallback: extract title from filename
    if not metadata["title"]:
        # Remove date prefix and extension
        title = re.sub(r"^\d{6}_", "", filepath.stem)  # Remove YYMMDD_
        title = re.sub(r"_", " ", title)  # Replace underscores
        title = re.sub(r"\s+", " ", title).strip()  # Normalize whitespace
        metadata["title"] = title

    return metadata


# =============================================================================
# PUBLISHER DETECTION
# =============================================================================

def detect_publisher(filename: str, text_sample: str) -> Tuple[Optional[str], Optional[str]]:
    """Detect publisher organization and type from filename or content."""

    # Check filename patterns
    for pattern, info in PUBLISHER_PATTERNS.items():
        if pattern in filename:
            return info["org"], info["type"]

    # Check content patterns
    content_patterns = {
        "CSET": {"org": "Center for Security and Emerging Technology", "type": "think_tank"},
        "Georgetown": {"org": "Georgetown University", "type": "academic"},
        "CSIS": {"org": "Center for Strategic and International Studies", "type": "think_tank"},
        "Brookings": {"org": "Brookings Institution", "type": "think_tank"},
        "RAND": {"org": "RAND Corporation", "type": "think_tank"},
        "Department of Defense": {"org": "U.S. Department of Defense", "type": "government"},
        "DOD": {"org": "U.S. Department of Defense", "type": "government"},
    }

    for pattern, info in content_patterns.items():
        if pattern in text_sample[:1000]:  # Check first 1000 chars
            return info["org"], info["type"]

    return None, "think_tank"  # Default to think_tank


# =============================================================================
# TOPIC AND REGION DETECTION
# =============================================================================

def detect_topics(title: str, text_sample: str) -> List[Tuple[str, float]]:
    """Detect topics from title and text. Returns list of (topic_slug, confidence)."""

    combined_text = (title + " " + text_sample).lower()
    detected_topics = []

    for topic_slug, keywords in TOPIC_KEYWORDS.items():
        matches = 0
        for keyword in keywords:
            if keyword.lower() in combined_text:
                matches += 1

        if matches > 0:
            # Calculate confidence (0.0 to 1.0)
            # Higher confidence if keyword in title or multiple matches
            confidence = min(0.5 + (matches * 0.1), 0.95)
            if keyword.lower() in title.lower():
                confidence = min(confidence + 0.2, 0.95)

            detected_topics.append((topic_slug, confidence))

    # Sort by confidence descending
    detected_topics.sort(key=lambda x: x[1], reverse=True)

    # If no topics detected, default to "critical_tech"
    if not detected_topics:
        detected_topics.append(("critical_tech", 0.5))

    return detected_topics


def detect_regions(title: str, text_sample: str) -> List[str]:
    """Detect geographic regions from title and text."""

    combined_text = (title + " " + text_sample).lower()
    detected_regions = []

    for region_slug, keywords in REGION_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in combined_text:
                if region_slug not in detected_regions:
                    detected_regions.append(region_slug)
                break

    # Default to global if no specific regions detected
    if not detected_regions:
        detected_regions.append("global")

    return detected_regions


def detect_flags(title: str, text_sample: str) -> Dict[str, bool]:
    """Detect boolean flags (MCF, Europe focus, Arctic focus)."""

    combined_text = (title + " " + text_sample).lower()

    flags = {
        "mcf_flag": False,
        "europe_focus_flag": False,
        "arctic_flag": False,
    }

    # MCF detection
    mcf_keywords = ["military-civil fusion", "mcf", "军民融合", "civil-military integration"]
    for keyword in mcf_keywords:
        if keyword.lower() in combined_text:
            flags["mcf_flag"] = True
            break

    # Europe focus detection
    europe_keywords = ["europe", "european union", "eu ", "nato", "brussels"]
    for keyword in europe_keywords:
        if keyword.lower() in combined_text:
            flags["europe_focus_flag"] = True
            break

    # Arctic detection
    arctic_keywords = ["arctic", "polar", "greenland", "northern sea route"]
    for keyword in arctic_keywords:
        if keyword.lower() in combined_text:
            flags["arctic_flag"] = True
            break

    return flags


# =============================================================================
# QUALITY SCORING
# =============================================================================

def calculate_quality_scores(metadata: Dict, topics: List, regions: List) -> Tuple[float, float]:
    """Calculate completeness_score and quality_score."""

    # Completeness score (0-100): based on metadata completeness
    fields = [
        metadata.get("title"),
        metadata.get("author"),
        metadata.get("publisher"),
        metadata.get("publication_date"),
        metadata.get("pages", 0) > 0,
        metadata.get("hash_sha256"),
        len(topics) > 0,
        len(regions) > 0,
    ]

    completeness_score = (sum(1 for f in fields if f) / len(fields)) * 100

    # Quality score (0-100): based on metadata richness and topic confidence
    quality_factors = []

    # Metadata quality
    quality_factors.append(50 if metadata.get("title") else 0)
    quality_factors.append(20 if metadata.get("author") else 0)
    quality_factors.append(10 if metadata.get("publication_date") else 0)
    quality_factors.append(10 if metadata.get("pages", 0) > 5 else 0)

    # Topic confidence (average of top 3 topics)
    if topics:
        avg_confidence = sum(t[1] for t in topics[:3]) / min(len(topics), 3)
        quality_factors.append(avg_confidence * 10)

    quality_score = min(sum(quality_factors), 100)

    return completeness_score, quality_score


# =============================================================================
# DATABASE INSERTION
# =============================================================================

def insert_report(conn: sqlite3.Connection, filepath: Path, metadata: Dict,
                  publisher_org: str, publisher_type: str,
                  topics: List[Tuple[str, float]], regions: List[str],
                  flags: Dict[str, bool],
                  completeness_score: float, quality_score: float) -> int:
    """Insert report into database and return report_id."""

    cursor = conn.cursor()

    # Check for duplicates by hash
    cursor.execute("SELECT report_id FROM thinktank_reports WHERE hash_sha256 = ?",
                   (metadata["hash_sha256"],))
    existing = cursor.fetchone()
    if existing:
        print(f"[SKIP] Duplicate detected (hash match): {filepath.name}")
        return existing[0]

    # Insert main report
    cursor.execute("""
        INSERT INTO thinktank_reports (
            title, source_organization, subtitle, authors, publisher_org, publisher_type,
            publication_date_iso, collection_date_utc,
            doc_type, file_ext, file_size_bytes, pages,
            url_canonical, url_download,
            hash_sha256, language,
            mcf_flag, europe_focus_flag, arctic_flag,
            completeness_score, quality_score,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        metadata["title"],
        publisher_org if publisher_org else "Unknown",  # source_organization (NOT NULL)
        None,  # subtitle (extract later if available)
        metadata["author"],  # Will be inserted into 'authors' column (plural)
        publisher_org,
        publisher_type,
        metadata["publication_date"],
        datetime.utcnow().isoformat(),
        "intelligence_report",
        filepath.suffix[1:],  # Remove leading dot
        metadata["file_size_bytes"],
        metadata["pages"],
        None,  # url_canonical (add manually if known)
        None,  # url_download
        metadata["hash_sha256"],
        "en",  # Default to English (detect later if needed)
        flags["mcf_flag"],
        flags["europe_focus_flag"],
        flags["arctic_flag"],
        completeness_score,
        quality_score,
        datetime.utcnow().isoformat(),
        datetime.utcnow().isoformat(),
    ))

    report_id = cursor.lastrowid

    # Insert topic assignments
    for i, (topic_slug, confidence) in enumerate(topics):
        cursor.execute("""
            INSERT INTO report_topics (report_id, topic_slug, confidence, is_primary, assigned_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            report_id,
            topic_slug,
            confidence,
            1 if i == 0 else 0,  # First topic is primary
            datetime.utcnow().isoformat(),
        ))

    # Insert region assignments
    for region_slug in regions:
        cursor.execute("""
            INSERT INTO report_regions (report_id, region_slug, assigned_date)
            VALUES (?, ?, ?)
        """, (
            report_id,
            region_slug,
            datetime.utcnow().isoformat(),
        ))

    conn.commit()
    return report_id


# =============================================================================
# MAIN PROCESSING
# =============================================================================

def process_reports():
    """Main processing function."""

    print("=" * 80)
    print("Think Tank Report Importer")
    print("=" * 80)
    print(f"Database: {DB_PATH}")
    print(f"Source: {REPORTS_DIR}")
    print()

    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")

    # Get current report count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM thinktank_reports")
    initial_count = cursor.fetchone()[0]
    print(f"[INFO] Current reports in database: {initial_count}")
    print()

    # Find all PDF files
    pdf_files = sorted(REPORTS_DIR.glob("*.pdf"))
    print(f"[INFO] Found {len(pdf_files)} PDF files to process")
    print()

    # Process each file
    imported_count = 0
    skipped_count = 0
    error_count = 0

    for i, filepath in enumerate(pdf_files, 1):
        try:
            print(f"[{i}/{len(pdf_files)}] Processing: {filepath.name}")

            # Extract metadata
            metadata = extract_pdf_metadata(filepath)
            print(f"  Title: {metadata['title'][:60]}...")
            print(f"  Pages: {metadata['pages']}, Size: {metadata['file_size_bytes']:,} bytes")

            # Detect publisher
            publisher_org, publisher_type = detect_publisher(filepath.name, metadata["text_sample"])
            if publisher_org:
                print(f"  Publisher: {publisher_org} ({publisher_type})")

            # Detect topics
            topics = detect_topics(metadata["title"], metadata["text_sample"])
            print(f"  Topics: {', '.join(f'{t[0]}({t[1]:.2f})' for t in topics[:3])}")

            # Detect regions
            regions = detect_regions(metadata["title"], metadata["text_sample"])
            print(f"  Regions: {', '.join(regions)}")

            # Detect flags
            flags = detect_flags(metadata["title"], metadata["text_sample"])
            flag_labels = [k.replace("_flag", "") for k, v in flags.items() if v]
            if flag_labels:
                print(f"  Flags: {', '.join(flag_labels)}")

            # Calculate quality scores
            completeness_score, quality_score = calculate_quality_scores(
                metadata, topics, regions
            )
            print(f"  Quality: {quality_score:.0f}/100, Completeness: {completeness_score:.0f}/100")

            # Insert into database
            report_id = insert_report(
                conn, filepath, metadata,
                publisher_org, publisher_type,
                topics, regions, flags,
                completeness_score, quality_score
            )

            if report_id:
                print(f"  [OK] Imported as report_id={report_id}")
                imported_count += 1
            else:
                print(f"  [SKIP] Already in database")
                skipped_count += 1

            print()

        except Exception as e:
            print(f"  [ERROR] Failed to process: {e}")
            error_count += 1
            print()

    # Final summary
    cursor.execute("SELECT COUNT(*) FROM thinktank_reports")
    final_count = cursor.fetchone()[0]

    print("=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"Initial reports: {initial_count}")
    print(f"Final reports: {final_count}")
    print(f"Imported: {imported_count}")
    print(f"Skipped (duplicates): {skipped_count}")
    print(f"Errors: {error_count}")
    print()

    # Show sample queries
    print("Sample queries:")
    print("  SELECT * FROM v_thinktank_reports_enhanced LIMIT 5;")
    print("  SELECT * FROM v_mcf_reports;")
    print("  SELECT * FROM v_reports_by_topic WHERE topic_slug = 'mcf';")
    print()

    conn.close()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    process_reports()
