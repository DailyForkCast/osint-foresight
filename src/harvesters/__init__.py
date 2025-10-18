"""
Think Tank Harvesters Package

This package provides a comprehensive system for harvesting and analyzing
think tank research on China's S&T policies and related strategic topics.

Key Components:
- ThinkTankHarvester: Main orchestrator for the harvesting process
- ThinkTankCrawler: Web crawling with robots.txt compliance
- ThinkTankParser: HTML and PDF content extraction
- ThinkTankClassifier: Topic filtering and classification
- ThinkTankSummarizer: Summary and relevance note generation

Usage:
    from src.harvesters import ThinkTankHarvester, HarvestConfig

    config = HarvestConfig(output_dir=Path("output"))
    harvester = ThinkTankHarvester(config, "config/sources.yaml")
    documents = await harvester.harvest_all_sources()
"""

from .thinktank_harvester import ThinkTankHarvester, HarvestConfig, ThinkTankDocument
from .thinktank_crawler import ThinkTankCrawler, CrawlResult
from .thinktank_parser import ThinkTankParser, ParsedContent
from .thinktank_classifier import ThinkTankClassifier, ClassificationResult
from .thinktank_summarizer import ThinkTankSummarizer, SummaryResult

__version__ = "1.0.0"
__author__ = "OSINT Foresight Team"

__all__ = [
    "ThinkTankHarvester",
    "HarvestConfig",
    "ThinkTankDocument",
    "ThinkTankCrawler",
    "CrawlResult",
    "ThinkTankParser",
    "ParsedContent",
    "ThinkTankClassifier",
    "ClassificationResult",
    "ThinkTankSummarizer",
    "SummaryResult"
]
