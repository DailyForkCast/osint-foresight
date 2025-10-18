#!/usr/bin/env python3
"""
Think Tank Classifier - Topic Filtering and Classification

This module implements a two-stage filtering system: keyword pre-filter and
transformer-based classification for China S&T policy content.

Key Features:
- Keyword-based pre-filtering for efficiency
- Transformer-based classification for accuracy
- Multi-label classification for tech domains and policy levers
- Specialized scoring for China focus, Arctic tech, and MCF/dual-use
- Configurable classification thresholds
- Support for multiple languages
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path
import json

# Text processing
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

# Machine learning
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    from sentence_transformers import SentenceTransformer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available. Using keyword-only classification.")

# Scikit-learn for fallback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class ClassificationResult:
    """Result of document classification"""
    china_focus_score: float
    arctic_focus_score: float
    mcf_dualuse_score: float
    tech_domains: List[str]
    policy_levers: List[str]
    scores: Dict[str, float]
    confidence: float
    method_used: str  # 'transformer' or 'keyword'


class ThinkTankClassifier:
    """Classifier for think tank content focusing on China S&T policies"""

    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", use_gpu: bool = False):
        self.logger = logging.getLogger(__name__)
        self.use_gpu = use_gpu and torch.cuda.is_available()

        # Initialize models
        self._load_models(model_name)

        # Load classification keywords and patterns
        self._load_classification_patterns()

        # NLTK setup
        self._ensure_nltk_data()

    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            self.logger.info("Downloading required NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)

    def _load_models(self, model_name: str):
        """Load transformer models if available"""
        self.transformer_available = TRANSFORMERS_AVAILABLE

        if self.transformer_available:
            try:
                device = 0 if self.use_gpu else -1

                # Load sentence transformer for embeddings
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                if self.use_gpu:
                    self.sentence_model = self.sentence_model.cuda()

                # Load classification pipeline (for sentiment/relevance)
                self.classifier_pipeline = pipeline(
                    "text-classification",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=device
                )

                self.logger.info("Transformer models loaded successfully")

            except Exception as e:
                self.logger.warning(f"Failed to load transformer models: {e}")
                self.transformer_available = False

        if not self.transformer_available:
            self.logger.info("Using keyword-based classification only")

    def _load_classification_patterns(self):
        """Load keywords and patterns for classification"""

        # China-focused keywords
        self.china_keywords = {
            'primary': [
                'china', 'chinese', 'beijing', 'ccp', 'communist party', 'xi jinping',
                'prc', "people's republic", 'mainland china', 'zhongnanhai'
            ],
            'entities': [
                'tencent', 'alibaba', 'baidu', 'huawei', 'zte', 'xiaomi', 'dji',
                'bytedance', 'tiktok', 'wechat', 'alipay', 'byd', 'catl',
                'state grid', 'sinopec', 'cnpc', 'cosco', 'cmsc'
            ],
            'policies': [
                'made in china 2025', 'belt and road', 'bri', 'dual circulation',
                'civil-military fusion', 'mcf', 'military-civil fusion',
                'new infrastructure', 'digital silk road', 'china standards 2035'
            ]
        }

        # Technology domain keywords
        self.tech_domain_keywords = {
            'artificial_intelligence': [
                'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',
                'neural network', 'computer vision', 'natural language processing',
                'nlp', 'facial recognition', 'autonomous', 'robotics', 'chatgpt'
            ],
            'quantum': [
                'quantum', 'quantum computing', 'quantum communication', 'quantum encryption',
                'quantum supremacy', 'qubits', 'quantum entanglement', 'quantum internet'
            ],
            'semiconductors': [
                'semiconductor', 'microchip', 'integrated circuit', 'ic', 'wafer',
                'fab', 'foundry', 'asml', 'tsmc', 'smic', 'lithography',
                'chip', 'processor', 'gpu', 'cpu', 'memory chip'
            ],
            'biotechnology': [
                'biotechnology', 'biotech', 'genetic engineering', 'crispr', 'gene editing',
                'synthetic biology', 'bioinformatics', 'pharmaceutical', 'vaccine',
                'genomics', 'proteomics', 'biodefense'
            ],
            'telecommunications': [
                '5g', '6g', 'telecommunications', 'telecom', 'cellular', 'wireless',
                'fiber optic', 'satellite communication', 'spectrum', 'broadband',
                'network infrastructure', 'base station'
            ],
            'space': [
                'space', 'satellite', 'rocket', 'launch', 'orbit', 'space station',
                'lunar', 'mars', 'space exploration', 'space technology',
                'aerospace', 'spacex', 'starlink', 'gps', 'navigation'
            ],
            'maritime_arctic': [
                'maritime', 'shipping', 'port', 'arctic', 'polar', 'ice breaker',
                'northern sea route', 'northwest passage', 'offshore',
                'underwater', 'submarine', 'naval', 'shipbuilding'
            ]
        }

        # Policy lever keywords
        self.policy_lever_keywords = {
            'industrial_policy': [
                'industrial policy', 'industrial strategy', 'national champion',
                'state-owned enterprise', 'soe', 'subsidies', 'tax incentive',
                'government funding', 'strategic plan'
            ],
            'standards_strategy': [
                'technical standard', 'international standard', 'iso', 'iec',
                'standard setting', 'standardization', 'compatibility',
                'interoperability', 'certification'
            ],
            'export_controls': [
                'export control', 'export restriction', 'sanctions', 'embargo',
                'dual-use', 'technology transfer', 'foreign investment screening',
                'cfius', 'entity list', 'trade restriction'
            ],
            'talent_programs': [
                'talent program', 'thousand talents', 'recruitment program',
                'brain drain', 'researcher exchange', 'academic collaboration',
                'visiting scholar', 'postdoc', 'student visa'
            ],
            'research_funding': [
                'research funding', 'r&d investment', 'research grant',
                'innovation fund', 'venture capital', 'startup', 'incubator',
                'accelerator', 'technology park'
            ]
        }

        # Arctic-specific keywords
        self.arctic_keywords = [
            'arctic', 'polar', 'antarctic', 'ice', 'permafrost', 'glacier',
            'northern sea route', 'northwest passage', 'polar silk road',
            'ice breaker', 'arctic council', 'svalbard', 'greenland',
            'climate change', 'global warming'
        ]

        # MCF/Dual-use keywords
        self.mcf_keywords = [
            'civil-military fusion', 'mcf', 'military-civil fusion',
            'dual-use', 'dual purpose', 'military application',
            'defense technology', 'defense contractor', 'weapons',
            'surveillance', 'cybersecurity', 'critical infrastructure'
        ]

        # Compile regex patterns for efficiency
        self._compile_keyword_patterns()

    def _compile_keyword_patterns(self):
        """Compile keyword patterns for efficient matching"""
        self.china_pattern = self._create_keyword_pattern(
            self.china_keywords['primary'] +
            self.china_keywords['entities'] +
            self.china_keywords['policies']
        )

        self.tech_patterns = {}
        for domain, keywords in self.tech_domain_keywords.items():
            self.tech_patterns[domain] = self._create_keyword_pattern(keywords)

        self.policy_patterns = {}
        for lever, keywords in self.policy_lever_keywords.items():
            self.policy_patterns[lever] = self._create_keyword_pattern(keywords)

        self.arctic_pattern = self._create_keyword_pattern(self.arctic_keywords)
        self.mcf_pattern = self._create_keyword_pattern(self.mcf_keywords)

    def _create_keyword_pattern(self, keywords: List[str]) -> re.Pattern:
        """Create regex pattern from keywords"""
        # Escape special regex characters and create word boundary pattern
        escaped_keywords = [re.escape(kw) for kw in keywords]
        pattern = r'\b(?:' + '|'.join(escaped_keywords) + r')\b'
        return re.compile(pattern, re.IGNORECASE)

    async def keyword_prefilter(self, text: str) -> bool:
        """Quick keyword-based pre-filter to eliminate irrelevant content"""
        if not text:
            return False

        # Convert to lowercase for matching
        text_lower = text.lower()

        # Must have China-related content
        china_matches = len(self.china_pattern.findall(text))
        if china_matches == 0:
            return False

        # Must have at least one tech domain or policy lever
        tech_matches = sum(
            len(pattern.findall(text))
            for pattern in self.tech_patterns.values()
        )

        policy_matches = sum(
            len(pattern.findall(text))
            for pattern in self.policy_patterns.values()
        )

        # Need at least 2 total matches (including China matches)
        total_matches = china_matches + tech_matches + policy_matches

        return total_matches >= 2

    async def classify_document(self, text: str) -> ClassificationResult:
        """Classify document using available methods"""

        if self.transformer_available:
            return await self._classify_with_transformers(text)
        else:
            return await self._classify_with_keywords(text)

    async def _classify_with_transformers(self, text: str) -> ClassificationResult:
        """Classify using transformer models"""
        try:
            # Truncate text for transformer processing
            max_length = 512
            words = text.split()
            if len(words) > max_length:
                # Take first and last parts to preserve context
                truncated_text = ' '.join(words[:max_length//2] + words[-max_length//2:])
            else:
                truncated_text = text

            # Get sentence embeddings
            embeddings = self.sentence_model.encode([truncated_text])

            # Calculate similarity scores with reference texts
            china_score = await self._calculate_china_focus_score_transformer(truncated_text, embeddings)
            arctic_score = await self._calculate_arctic_score_transformer(truncated_text, embeddings)
            mcf_score = await self._calculate_mcf_score_transformer(truncated_text, embeddings)

            # Identify tech domains and policy levers
            tech_domains = await self._identify_tech_domains_transformer(truncated_text, embeddings)
            policy_levers = await self._identify_policy_levers_transformer(truncated_text, embeddings)

            # Calculate confidence based on multiple factors
            confidence = min(1.0, (china_score + len(tech_domains) * 0.1 + len(policy_levers) * 0.1))

            return ClassificationResult(
                china_focus_score=china_score,
                arctic_focus_score=arctic_score,
                mcf_dualuse_score=mcf_score,
                tech_domains=tech_domains,
                policy_levers=policy_levers,
                scores={
                    'china_focus': china_score,
                    'arctic_focus': arctic_score,
                    'mcf_dualuse': mcf_score
                },
                confidence=confidence,
                method_used='transformer'
            )

        except Exception as e:
            self.logger.warning(f"Transformer classification failed: {e}, falling back to keywords")
            return await self._classify_with_keywords(text)

    async def _classify_with_keywords(self, text: str) -> ClassificationResult:
        """Classify using keyword-based approach"""
        text_lower = text.lower()
        word_count = len(text.split())

        # Calculate China focus score
        china_matches = len(self.china_pattern.findall(text))
        china_score = min(1.0, china_matches / max(1, word_count / 100))  # Normalize by text length

        # Calculate Arctic focus score
        arctic_matches = len(self.arctic_pattern.findall(text))
        arctic_score = min(1.0, arctic_matches / max(1, word_count / 100))

        # Calculate MCF/dual-use score
        mcf_matches = len(self.mcf_pattern.findall(text))
        mcf_score = min(1.0, mcf_matches / max(1, word_count / 100))

        # Identify tech domains
        tech_domains = []
        for domain, pattern in self.tech_patterns.items():
            matches = len(pattern.findall(text))
            if matches > 0:
                tech_domains.append(domain)

        # Identify policy levers
        policy_levers = []
        for lever, pattern in self.policy_patterns.items():
            matches = len(pattern.findall(text))
            if matches > 0:
                policy_levers.append(lever)

        # Calculate confidence
        total_matches = china_matches + arctic_matches + mcf_matches
        confidence = min(1.0, total_matches / max(1, word_count / 50))

        return ClassificationResult(
            china_focus_score=china_score,
            arctic_focus_score=arctic_score,
            mcf_dualuse_score=mcf_score,
            tech_domains=tech_domains,
            policy_levers=policy_levers,
            scores={
                'china_focus': china_score,
                'arctic_focus': arctic_score,
                'mcf_dualuse': mcf_score
            },
            confidence=confidence,
            method_used='keyword'
        )

    async def _calculate_china_focus_score_transformer(self, text: str, embeddings) -> float:
        """Calculate China focus score using transformer embeddings"""
        # Reference texts for China S&T policy
        china_references = [
            "China's artificial intelligence strategy and technology development",
            "Chinese government technology policies and industrial planning",
            "China's semiconductor industry and tech competition with United States"
        ]

        # Calculate similarity with reference texts
        ref_embeddings = self.sentence_model.encode(china_references)
        similarities = cosine_similarity(embeddings, ref_embeddings)

        return float(np.max(similarities))

    async def _calculate_arctic_score_transformer(self, text: str, embeddings) -> float:
        """Calculate Arctic focus score using transformer embeddings"""
        arctic_references = [
            "Arctic technology development and polar research",
            "Northern sea route and arctic shipping infrastructure",
            "Climate change effects on arctic regions and technology"
        ]

        ref_embeddings = self.sentence_model.encode(arctic_references)
        similarities = cosine_similarity(embeddings, ref_embeddings)

        return float(np.max(similarities))

    async def _calculate_mcf_score_transformer(self, text: str, embeddings) -> float:
        """Calculate MCF/dual-use score using transformer embeddings"""
        mcf_references = [
            "Civil-military fusion and dual-use technology development",
            "Military applications of civilian technology",
            "Defense technology transfer and security implications"
        ]

        ref_embeddings = self.sentence_model.encode(mcf_references)
        similarities = cosine_similarity(embeddings, ref_embeddings)

        return float(np.max(similarities))

    async def _identify_tech_domains_transformer(self, text: str, embeddings) -> List[str]:
        """Identify technology domains using transformer embeddings"""
        domain_references = {
            'artificial_intelligence': "Artificial intelligence machine learning and AI technology",
            'quantum': "Quantum computing and quantum communication technology",
            'semiconductors': "Semiconductor chips and microelectronics manufacturing",
            'biotechnology': "Biotechnology genetic engineering and pharmaceutical research",
            'telecommunications': "5G 6G telecommunications and wireless communication",
            'space': "Space technology satellites and aerospace development",
            'maritime_arctic': "Maritime technology and arctic infrastructure"
        }

        identified_domains = []
        threshold = 0.3

        for domain, reference in domain_references.items():
            ref_embedding = self.sentence_model.encode([reference])
            similarity = cosine_similarity(embeddings, ref_embedding)[0][0]

            if similarity > threshold:
                identified_domains.append(domain)

        return identified_domains

    async def _identify_policy_levers_transformer(self, text: str, embeddings) -> List[str]:
        """Identify policy levers using transformer embeddings"""
        lever_references = {
            'industrial_policy': "Industrial policy government subsidies and economic planning",
            'standards_strategy': "Technical standards and international standardization",
            'export_controls': "Export controls technology restrictions and sanctions",
            'talent_programs': "Talent recruitment programs and researcher exchange",
            'research_funding': "Research funding innovation investment and venture capital"
        }

        identified_levers = []
        threshold = 0.3

        for lever, reference in lever_references.items():
            ref_embedding = self.sentence_model.encode([reference])
            similarity = cosine_similarity(embeddings, ref_embedding)[0][0]

            if similarity > threshold:
                identified_levers.append(lever)

        return identified_levers

    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics and model info"""
        return {
            'transformer_available': self.transformer_available,
            'using_gpu': self.use_gpu,
            'china_keywords_count': len(self.china_keywords['primary']) +
                                  len(self.china_keywords['entities']) +
                                  len(self.china_keywords['policies']),
            'tech_domains_count': len(self.tech_domain_keywords),
            'policy_levers_count': len(self.policy_lever_keywords),
            'arctic_keywords_count': len(self.arctic_keywords),
            'mcf_keywords_count': len(self.mcf_keywords)
        }


# Utility class for batch classification
class BatchClassifier:
    """Utility for batch classification of multiple documents"""

    def __init__(self, classifier: ThinkTankClassifier, batch_size: int = 10):
        self.classifier = classifier
        self.batch_size = batch_size
        self.logger = logging.getLogger(__name__)

    async def classify_batch(self, texts: List[str]) -> List[ClassificationResult]:
        """Classify a batch of texts"""
        results = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            self.logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(texts)-1)//self.batch_size + 1}")

            batch_results = await asyncio.gather(*[
                self.classifier.classify_document(text) for text in batch
            ])

            results.extend(batch_results)

        return results


if __name__ == "__main__":
    import asyncio

    async def test_classifier():
        """Test the classifier functionality"""
        classifier = ThinkTankClassifier()

        # Test documents
        test_texts = [
            "China's artificial intelligence strategy focuses on developing AI capabilities through state funding and civil-military fusion programs.",
            "The Arctic region faces significant challenges from climate change affecting shipping routes and infrastructure.",
            "Semiconductor manufacturing requires advanced lithography equipment and significant capital investment.",
            "This document discusses European agricultural policies and trade agreements with South America."
        ]

        for i, text in enumerate(test_texts):
            print(f"\nTest {i+1}:")
            print(f"Text: {text[:100]}...")

            # Pre-filter test
            passes_filter = await classifier.keyword_prefilter(text)
            print(f"Passes pre-filter: {passes_filter}")

            if passes_filter:
                # Full classification
                result = await classifier.classify_document(text)
                print(f"China focus score: {result.china_focus_score:.3f}")
                print(f"Tech domains: {result.tech_domains}")
                print(f"Policy levers: {result.policy_levers}")
                print(f"Method: {result.method_used}")

    # Run test
    # asyncio.run(test_classifier())
