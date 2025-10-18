"""
Google Patents BigQuery Integration Setup
Analyzes patent filings for technology transfer patterns between China and tracked countries
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from google.cloud import bigquery
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GooglePatentsBigQueryAnalyzer:
    """Analyzes Google Patents data via BigQuery for China collaboration patterns"""

    def __init__(self, project_id: str = "osint-foresight-2025"):
        """Initialize BigQuery client"""
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = "patent_analysis"

        # Countries to track (same as OpenAlex analysis)
        self.tracked_countries = {
            "US", "CN", "DE", "FR", "IT", "ES", "NL", "BE", "LU", "SE", "DK", "FI", "NO", "IS",
            "PL", "CZ", "SK", "HU", "RO", "BG", "HR", "SI", "EE", "LV", "LT",
            "GR", "CY", "MT", "PT", "AT", "IE", "CH", "GB", "AL", "MK", "RS", "ME",
            "BA", "TR", "UA", "XK", "GE", "AM", "FO", "GL", "CA", "AU", "NZ",
            "JP", "KR", "SG", "TW", "IN", "TH", "MY", "VN", "IL", "AE", "SA",
            "BR", "MX", "AR", "CL", "ZA", "EG", "KE", "NG", "RU", "BY", "KZ"
        }

        # Dual-use technology keywords
        self.tech_categories = {
            "quantum_computing": ["quantum", "qubit", "quantum computer", "quantum algorithm"],
            "ai_ml": ["artificial intelligence", "machine learning", "neural network", "deep learning"],
            "semiconductors": ["semiconductor", "chip", "integrated circuit", "microprocessor"],
            "biotechnology":
