#!/usr/bin/env python3
"""
Think Tank Summarizer - Summary and Relevance Note Generation

This module generates 4-5 sentence summaries and 2-3 sentence relevance notes
for think tank documents, with support for translation and multiple summarization
strategies.

Key Features:
- Extractive and abstractive summarization
- Relevance note generation focused on China S&T policy
- Multi-language support with translation to English
- Configurable summary lengths
- Quality scoring and validation
- Template-based formatting for consistency
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

# Text processing
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import math

# Translation
try:
    from googletrans import Translator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    print("Warning: googletrans not available. Translation disabled.")

# Advanced NLP (optional)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    from sentence_transformers import SentenceTransformer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available. Using extractive summarization only.")

# Text similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


@dataclass
class SummaryResult:
    """Result of summarization process"""
    summary: str
    relevance_note: str
    original_language: str
    translated: bool = False
    summary_method: str = 'extractive'
    confidence_score: float = 0.0
    key_topics: List[str] = None
    word_count_original: int = 0
    word_count_summary: int = 0
    compression_ratio: float = 0.0

    def __post_init__(self):
        if self.key_topics is None:
            self.key_topics = []
        if self.word_count_summary > 0 and self.word_count_original > 0:
            self.compression_ratio = self.word_count_summary / self.word_count_original


class ThinkTankSummarizer:
    """Summarizer for think tank research documents"""

    def __init__(self, enable_translation: bool = True, use_gpu: bool = False):
        self.logger = logging.getLogger(__name__)
        self.enable_translation = enable_translation and TRANSLATION_AVAILABLE
        self.use_gpu = use_gpu and torch.cuda.is_available()

        # Initialize components
        self._load_models()
        self._load_templates()

        # NLTK setup
        self._ensure_nltk_data()

        # Translation setup
        if self.enable_translation:
            self.translator = Translator()

        # Summary configuration
        self.summary_config = {
            'target_sentences': 5,
            'max_sentences': 6,
            'min_sentences': 4,
            'relevance_sentences': 3,
            'max_relevance_sentences': 3,
            'min_relevance_sentences': 2
        }

    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            self.logger.info("Downloading required NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)

    def _load_models(self):
        """Load summarization models if available"""
        self.transformer_available = TRANSFORMERS_AVAILABLE

        if self.transformer_available:
            try:
                device = 0 if self.use_gpu else -1

                # Load summarization pipeline
                self.summarizer_pipeline = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    device=device
                )

                # Load sentence transformer for similarity
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                if self.use_gpu:
                    self.sentence_model = self.sentence_model.cuda()

                self.logger.info("Transformer models loaded successfully")

            except Exception as e:
                self.logger.warning(f"Failed to load transformer models: {e}")
                self.transformer_available = False

        if not self.transformer_available:
            self.logger.info("Using extractive summarization only")

    def _load_templates(self):
        """Load summary and relevance note templates"""
        self.summary_templates = {
            'policy_analysis': "This {doc_type} analyzes {key_topic} with focus on {main_aspects}. {key_findings} The analysis concludes {conclusion}.",
            'technology_report': "This {doc_type} examines {technology} developments in {context}. {main_findings} {implications}",
            'strategic_assessment': "This {doc_type} assesses {topic} from a strategic perspective. {analysis} {recommendations}",
            'general': "This {doc_type} discusses {main_topic}. {key_points} {conclusions}"
        }

        self.relevance_templates = {
            'china_tech': "This content is relevant to China S&T policy analysis because {china_connection}. {policy_implications}",
            'arctic_tech': "This content relates to Arctic technology development through {arctic_connection}. {strategic_implications}",
            'mcf_dualuse': "This content addresses dual-use technology concerns via {mcf_connection}. {security_implications}",
            'general': "This content is relevant because {relevance_reason}. {analytical_value}"
        }

    async def generate_summary(self, text: str, title: str,
                             classification_result: Dict[str, Any]) -> SummaryResult:
        """Generate summary and relevance note for a document"""
        try:
            # Detect and handle language
            original_language = self._detect_language(text)
            working_text = text
            translated = False

            # Translate if needed
            if original_language != 'en' and self.enable_translation:
                working_text = await self._translate_text(text, target_lang='en')
                translated = True

            # Generate summary
            if self.transformer_available and len(working_text.split()) > 100:
                summary = await self._generate_abstractive_summary(working_text, title)
                method = 'abstractive'
            else:
                summary = await self._generate_extractive_summary(working_text, title)
                method = 'extractive'

            # Generate relevance note
            relevance_note = await self._generate_relevance_note(
                working_text, title, classification_result
            )

            # Extract key topics
            key_topics = await self._extract_key_topics(working_text, classification_result)

            # Calculate metrics
            word_count_original = len(text.split())
            word_count_summary = len(summary.split())

            # Calculate confidence score
            confidence = await self._calculate_confidence(
                text, summary, relevance_note, classification_result
            )

            return SummaryResult(
                summary=summary,
                relevance_note=relevance_note,
                original_language=original_language,
                translated=translated,
                summary_method=method,
                confidence_score=confidence,
                key_topics=key_topics,
                word_count_original=word_count_original,
                word_count_summary=word_count_summary
            )

        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            # Fallback to basic summary
            return await self._generate_fallback_summary(text, title)

    def _detect_language(self, text: str) -> str:
        """Detect language of text"""
        try:
            from langdetect import detect
            sample = text[:1000]  # Use first 1000 characters
            return detect(sample)
        except:
            return 'en'  # Default to English

    async def _translate_text(self, text: str, target_lang: str = 'en') -> str:
        """Translate text to target language"""
        if not self.enable_translation:
            return text

        try:
            # Translate in chunks to avoid length limits
            max_chunk_size = 4000
            if len(text) <= max_chunk_size:
                result = self.translator.translate(text, dest=target_lang)
                return result.text
            else:
                # Split into sentences and translate in chunks
                sentences = sent_tokenize(text)
                translated_chunks = []
                current_chunk = ""

                for sentence in sentences:
                    if len(current_chunk + sentence) < max_chunk_size:
                        current_chunk += sentence + " "
                    else:
                        if current_chunk:
                            result = self.translator.translate(current_chunk.strip(), dest=target_lang)
                            translated_chunks.append(result.text)
                        current_chunk = sentence + " "

                # Translate remaining chunk
                if current_chunk:
                    result = self.translator.translate(current_chunk.strip(), dest=target_lang)
                    translated_chunks.append(result.text)

                return " ".join(translated_chunks)

        except Exception as e:
            self.logger.warning(f"Translation failed: {e}")
            return text

    async def _generate_abstractive_summary(self, text: str, title: str) -> str:
        """Generate abstractive summary using transformer model"""
        try:
            # Prepare text for summarization
            max_input_length = 1024
            words = text.split()

            if len(words) > max_input_length:
                # Take first and last parts with title context
                truncated_text = title + ". " + " ".join(words[:max_input_length//2] + words[-max_input_length//2:])
            else:
                truncated_text = title + ". " + text

            # Generate summary
            summary_result = self.summarizer_pipeline(
                truncated_text,
                max_length=150,
                min_length=80,
                do_sample=False
            )

            summary = summary_result[0]['summary_text']

            # Post-process summary
            summary = self._post_process_summary(summary)

            # Ensure target length
            sentences = sent_tokenize(summary)
            if len(sentences) > self.summary_config['max_sentences']:
                summary = ". ".join(sentences[:self.summary_config['max_sentences']]) + "."
            elif len(sentences) < self.summary_config['min_sentences']:
                # If too short, fall back to extractive
                return await self._generate_extractive_summary(text, title)

            return summary

        except Exception as e:
            self.logger.warning(f"Abstractive summarization failed: {e}")
            return await self._generate_extractive_summary(text, title)

    async def _generate_extractive_summary(self, text: str, title: str) -> str:
        """Generate extractive summary using sentence ranking"""
        sentences = sent_tokenize(text)

        if len(sentences) <= self.summary_config['target_sentences']:
            return text

        # Score sentences
        sentence_scores = await self._score_sentences(sentences, title)

        # Select top sentences
        num_sentences = min(self.summary_config['target_sentences'], len(sentences))
        top_indices = sorted(sentence_scores.argsort()[-num_sentences:])

        # Create summary maintaining original order
        summary_sentences = [sentences[i] for i in sorted(top_indices)]
        summary = " ".join(summary_sentences)

        return self._post_process_summary(summary)

    async def _score_sentences(self, sentences: List[str], title: str) -> np.ndarray:
        """Score sentences for extractive summarization"""
        if not sentences:
            return np.array([])

        # Create TF-IDF vectors
        all_text = [title] + sentences
        vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)

        try:
            tfidf_matrix = vectorizer.fit_transform(all_text)
        except ValueError:
            # Fallback scoring if TF-IDF fails
            return np.array([len(s.split()) for s in sentences])

        # Calculate sentence scores
        title_vector = tfidf_matrix[0]
        sentence_vectors = tfidf_matrix[1:]

        scores = []
        for i, sentence in enumerate(sentences):
            # Base score: similarity to title
            title_similarity = cosine_similarity(sentence_vectors[i], title_vector)[0][0]

            # Position score (earlier sentences slightly preferred)
            position_score = 1.0 - (i / len(sentences)) * 0.1

            # Length score (prefer medium-length sentences)
            words = sentence.split()
            length_score = 1.0 if 10 <= len(words) <= 30 else 0.8

            # Keyword bonus for China/tech terms
            keyword_score = self._calculate_keyword_bonus(sentence)

            # Combined score
            total_score = (title_similarity * 0.4 + position_score * 0.2 +
                          length_score * 0.2 + keyword_score * 0.2)

            scores.append(total_score)

        return np.array(scores)

    def _calculate_keyword_bonus(self, sentence: str) -> float:
        """Calculate bonus score for important keywords"""
        important_keywords = [
            'china', 'chinese', 'technology', 'policy', 'strategy',
            'artificial intelligence', 'quantum', 'semiconductor',
            'arctic', 'dual-use', 'military', 'civil-military fusion'
        ]

        sentence_lower = sentence.lower()
        keyword_count = sum(1 for keyword in important_keywords if keyword in sentence_lower)

        return min(1.0, keyword_count * 0.1)

    async def _generate_relevance_note(self, text: str, title: str,
                                     classification_result: Dict[str, Any]) -> str:
        """Generate relevance note explaining why content is important"""
        # Determine relevance template based on classification
        china_score = classification_result.get('china_focus_score', 0)
        arctic_score = classification_result.get('arctic_focus_score', 0)
        mcf_score = classification_result.get('mcf_dualuse_score', 0)

        if mcf_score > 0.5:
            template_key = 'mcf_dualuse'
        elif arctic_score > 0.5:
            template_key = 'arctic_tech'
        elif china_score > 0.5:
            template_key = 'china_tech'
        else:
            template_key = 'general'

        # Extract key relevance points
        relevance_points = await self._extract_relevance_points(
            text, classification_result, template_key
        )

        # Generate relevance note
        if template_key == 'china_tech':
            relevance_note = f"This content is relevant to China S&T policy analysis because it {relevance_points['connection']}. {relevance_points['implications']}"
        elif template_key == 'arctic_tech':
            relevance_note = f"This content relates to Arctic technology development through {relevance_points['connection']}. {relevance_points['implications']}"
        elif template_key == 'mcf_dualuse':
            relevance_note = f"This content addresses dual-use technology concerns via {relevance_points['connection']}. {relevance_points['implications']}"
        else:
            relevance_note = f"This content is relevant because it {relevance_points['reason']}. {relevance_points['value']}"

        # Ensure appropriate length
        sentences = sent_tokenize(relevance_note)
        if len(sentences) > self.summary_config['max_relevance_sentences']:
            relevance_note = ". ".join(sentences[:self.summary_config['max_relevance_sentences']]) + "."

        return relevance_note

    async def _extract_relevance_points(self, text: str, classification_result: Dict[str, Any],
                                      template_key: str) -> Dict[str, str]:
        """Extract specific relevance points based on content"""
        tech_domains = classification_result.get('tech_domains', [])
        policy_levers = classification_result.get('policy_levers', [])

        if template_key == 'china_tech':
            connection_parts = []
            if tech_domains:
                connection_parts.append(f"discusses China's {', '.join(tech_domains[:2])} capabilities")
            if policy_levers:
                connection_parts.append(f"analyzes {', '.join(policy_levers[:2])} mechanisms")

            connection = " and ".join(connection_parts) if connection_parts else "examines China's technology strategy"

            implications = "The insights help understand China's technological development priorities and competitive positioning."

        elif template_key == 'arctic_tech':
            connection = "examining technological developments in polar regions and their strategic implications"
            implications = "This analysis contributes to understanding Arctic technology competition and infrastructure development."

        elif template_key == 'mcf_dualuse':
            connection = "analyzing technologies with both civilian and military applications"
            implications = "This perspective helps assess security implications of technology transfer and development."

        else:
            connection = "providing insights into international technology policy dynamics"
            implications = "The analysis contributes to broader understanding of global technology competition."

        return {
            'connection': connection,
            'implications': implications,
            'reason': connection,
            'value': implications
        }

    async def _extract_key_topics(self, text: str, classification_result: Dict[str, Any]) -> List[str]:
        """Extract key topics from the text"""
        # Combine classification results with text analysis
        topics = []

        # Add classified tech domains and policy levers
        topics.extend(classification_result.get('tech_domains', []))
        topics.extend(classification_result.get('policy_levers', []))

        # Extract additional topics using TF-IDF
        try:
            sentences = sent_tokenize(text)
            vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=50,
                ngram_range=(1, 2)
            )

            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()

            # Get top terms
            scores = tfidf_matrix.sum(axis=0).A1
            top_indices = scores.argsort()[-10:][::-1]

            for idx in top_indices:
                term = feature_names[idx]
                if len(term.split()) <= 2 and term not in topics:
                    topics.append(term)

        except Exception as e:
            self.logger.debug(f"TF-IDF topic extraction failed: {e}")

        return topics[:8]  # Return top 8 topics

    def _post_process_summary(self, summary: str) -> str:
        """Post-process summary for quality and consistency"""
        if not summary:
            return ""

        # Remove redundant phrases
        summary = re.sub(r'\bthis (article|report|paper|document)\b', 'this analysis', summary, flags=re.IGNORECASE)

        # Ensure proper sentence structure
        sentences = sent_tokenize(summary)
        processed_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) >= 5:  # Only include substantial sentences
                # Ensure sentence ends with period
                if not sentence.endswith(('.', '!', '?')):
                    sentence += '.'
                processed_sentences.append(sentence)

        return " ".join(processed_sentences)

    async def _calculate_confidence(self, original_text: str, summary: str,
                                  relevance_note: str, classification_result: Dict[str, Any]) -> float:
        """Calculate confidence score for the summarization"""
        scores = []

        # Summary length appropriateness
        summary_sentences = len(sent_tokenize(summary))
        target_sentences = self.summary_config['target_sentences']
        length_score = 1.0 - abs(summary_sentences - target_sentences) / target_sentences
        scores.append(length_score)

        # Classification confidence
        classification_confidence = classification_result.get('confidence', 0.5)
        scores.append(classification_confidence)

        # Content coverage (simple overlap measure)
        original_words = set(original_text.lower().split())
        summary_words = set(summary.lower().split())
        coverage = len(summary_words.intersection(original_words)) / len(summary_words) if summary_words else 0
        scores.append(min(1.0, coverage * 2))  # Scale up coverage score

        return sum(scores) / len(scores)

    async def _generate_fallback_summary(self, text: str, title: str) -> SummaryResult:
        """Generate basic fallback summary when main methods fail"""
        sentences = sent_tokenize(text)

        # Take first few sentences as summary
        num_sentences = min(self.summary_config['target_sentences'], len(sentences))
        summary = ". ".join(sentences[:num_sentences])
        if not summary.endswith('.'):
            summary += '.'

        # Basic relevance note
        relevance_note = "This content discusses relevant topics for technology policy analysis. The document provides insights into current developments and strategic considerations."

        return SummaryResult(
            summary=summary,
            relevance_note=relevance_note,
            original_language='en',
            translated=False,
            summary_method='fallback',
            confidence_score=0.3,
            key_topics=[],
            word_count_original=len(text.split()),
            word_count_summary=len(summary.split())
        )


# Utility class for batch summarization
class BatchSummarizer:
    """Utility for batch summarization of multiple documents"""

    def __init__(self, summarizer: ThinkTankSummarizer, batch_size: int = 5):
        self.summarizer = summarizer
        self.batch_size = batch_size
        self.logger = logging.getLogger(__name__)

    async def summarize_batch(self, documents: List[Dict[str, Any]]) -> List[SummaryResult]:
        """Summarize a batch of documents"""
        results = []

        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            self.logger.info(f"Summarizing batch {i//self.batch_size + 1}/{(len(documents)-1)//self.batch_size + 1}")

            batch_tasks = []
            for doc in batch:
                task = self.summarizer.generate_summary(
                    doc['text'],
                    doc['title'],
                    doc.get('classification_result', {})
                )
                batch_tasks.append(task)

            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)

        return results


if __name__ == "__main__":
    import asyncio

    async def test_summarizer():
        """Test the summarizer functionality"""
        summarizer = ThinkTankSummarizer()

        test_text = """
        China has made significant investments in artificial intelligence research and development
        as part of its national strategy to become a global leader in AI by 2030. The government
        has implemented various policy measures including substantial funding for AI research institutes,
        tax incentives for AI companies, and the establishment of national AI innovation zones.
        These efforts are part of a broader civil-military fusion strategy that aims to leverage
        civilian AI advances for military applications. The dual-use nature of AI technology
        makes it particularly important for national security considerations. Chinese tech companies
        like Baidu, Alibaba, and Tencent have received significant government support to develop
        AI capabilities in areas such as computer vision, natural language processing, and autonomous
        systems. However, this rapid development has also raised concerns among Western nations
        about the potential military applications of these technologies and their impact on
        global strategic balance.
        """

        classification_result = {
            'china_focus_score': 0.9,
            'arctic_focus_score': 0.1,
            'mcf_dualuse_score': 0.7,
            'tech_domains': ['artificial_intelligence'],
            'policy_levers': ['industrial_policy', 'research_funding'],
            'confidence': 0.8
        }

        result = await summarizer.generate_summary(
            test_text,
            "China's AI Strategy and Civil-Military Fusion",
            classification_result
        )

        print("Summary Result:")
        print(f"Summary: {result.summary}")
        print(f"Relevance Note: {result.relevance_note}")
        print(f"Method: {result.summary_method}")
        print(f"Confidence: {result.confidence_score:.3f}")
        print(f"Key Topics: {result.key_topics}")
        print(f"Compression Ratio: {result.compression_ratio:.3f}")

    # Run test
    # asyncio.run(test_summarizer())
