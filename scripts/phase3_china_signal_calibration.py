#!/usr/bin/env python3
"""
Phase 3: China Signal Calibration
Build comprehensive detection dictionary and test with control groups
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import unicodedata

class ChinaSignalDetector:
    def __init__(self):
        self.detection_terms = {
            'chinese_characters': set(),
            'pinyin': set(),
            'english_exonyms': set(),
            'french_exonyms': set(),
            'german_exonyms': set(),
            'russian_exonyms': set(),
            'subsidiaries': set(),
            'ticker_aliases': set(),
            'ports': set(),
            'institutions': set(),
            'technology_terms': set()
        }

        self.test_results = {
            'generated': datetime.now().isoformat(),
            'detection_stats': {},
            'control_group_results': {},
            'false_positives': [],
            'false_negatives': []
        }

        self.build_detection_dictionary()

    def build_detection_dictionary(self):
        """Build comprehensive China detection dictionary"""

        # Core Chinese entities and variants
        self.detection_terms['chinese_characters'] = {
            '中国', '中华', '北京', '上海', '深圳', '广州', '天津', '重庆',
            '浙江', '江苏', '广东', '山东', '河南', '四川', '湖北', '湖南',
            '中科院', '清华', '北大', '复旦', '交大', '中山大学', '浙大',
            '华为', '阿里巴巴', '腾讯', '百度', '字节跳动', '小米', '京东'
        }

        # Pinyin variants
        self.detection_terms['pinyin'] = {
            'zhongguo', 'beijing', 'shanghai', 'shenzhen', 'guangzhou', 'tianjin',
            'chongqing', 'zhejiang', 'jiangsu', 'guangdong', 'shandong', 'henan',
            'sichuan', 'hubei', 'hunan', 'tsinghua', 'beida', 'fudan', 'jiaotong',
            'huawei', 'alibaba', 'tencent', 'baidu', 'bytedance', 'xiaomi', 'jingdong',
            'zhongkeyuan', 'cas', 'cass', 'caas', 'cae'
        }

        # English exonyms and variations
        self.detection_terms['english_exonyms'] = {
            'china', 'chinese', 'prc', "people's republic", 'peoples republic',
            'sino', 'mainland china', 'beijing', 'peking', 'shanghai', 'shenzhen',
            'canton', 'guangzhou', 'tianjin', 'tientsin', 'chongqing', 'chungking',
            'chinese academy', 'tsinghua', 'peking university', 'fudan', 'zhejiang',
            'huawei', 'alibaba', 'tencent', 'baidu', 'bytedance', 'tiktok', 'wechat'
        }

        # French exonyms
        self.detection_terms['french_exonyms'] = {
            'chine', 'chinois', 'chinoise', 'pékin', 'shanghai', 'canton',
            'république populaire de chine', 'rpc', 'académie chinoise'
        }

        # German exonyms
        self.detection_terms['german_exonyms'] = {
            'china', 'chinesisch', 'chinesische', 'volksrepublik china',
            'peking', 'schanghai', 'kanton', 'chinesische akademie'
        }

        # Russian exonyms (transliterated)
        self.detection_terms['russian_exonyms'] = {
            'kitay', 'kitai', 'kitayskiy', 'knr', 'pekin', 'shankhay',
            'guanchzhou', 'kitayskaya akademiya'
        }

        # Major subsidiaries and joint ventures
        self.detection_terms['subsidiaries'] = {
            'huawei technologies', 'huawei marine', 'hisilicon', 'honor',
            'alibaba cloud', 'alipay', 'ant group', 'taobao', 'tmall',
            'tencent holdings', 'wechat pay', 'riot games', 'supercell',
            'baidu research', 'iqiyi', 'dji', 'byd', 'geely', 'lenovo',
            'zte', 'oppo', 'vivo', 'oneplus', 'realme', 'tcl', 'haier',
            'state grid', 'sinopec', 'cnpc', 'china mobile', 'china telecom',
            'icbc', 'ccb', 'abc', 'boc', 'china construction bank'
        }

        # Stock tickers and aliases
        self.detection_terms['ticker_aliases'] = {
            'baba', 'tcehy', 'bidu', 'jd', 'pdd', 'ntes', 'tme', 'bili',
            '0700.hk', '9988.hk', '1810.hk', '9618.hk', '0968.hk',
            '000002.sz', '000333.sz', '000858.sz', '002415.sz'
        }

        # Major ports and trade hubs
        self.detection_terms['ports'] = {
            'shanghai port', 'ningbo', 'shenzhen port', 'guangzhou port',
            'qingdao', 'tianjin port', 'xiamen', 'dalian', 'lianyungang',
            'zhoushan', 'suzhou', 'foshan', 'dongguan', 'yiwu'
        }

        # Academic and research institutions
        self.detection_terms['institutions'] = {
            'cas', 'chinese academy of sciences', 'china academy',
            'beijing institute', 'shanghai institute', 'wuhan institute',
            'harbin institute', 'nanjing university', 'xi\'an jiaotong',
            'ustc', 'university of science and technology of china',
            'beihang', 'beijing university of aeronautics'
        }

        # Technology and domain terms
        self.detection_terms['technology_terms'] = {
            '5g', '6g', 'artificial intelligence', 'quantum computing',
            'semiconductor', 'integrated circuit', 'ev battery', 'solar panel',
            'rare earth', 'hypersonic', 'dual use', 'belt and road', 'bri',
            'made in china 2025', 'digital silk road', 'new infrastructure'
        }

    def normalize_text(self, text):
        """Normalize text for matching"""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove accents
        text = ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn')

        # Normalize whitespace
        text = ' '.join(text.split())

        return text

    def detect_china_signals(self, text, metadata=None):
        """Detect China-related signals in text"""
        if not text:
            return {'detected': False, 'signals': [], 'confidence': 0}

        normalized = self.normalize_text(text)
        detected_signals = []

        # Check for Chinese characters (highest confidence)
        if any(ord(c) >= 0x4e00 and ord(c) <= 0x9fff for c in text):
            detected_signals.append(('chinese_characters', 0.95))

        # Check each category
        for category, terms in self.detection_terms.items():
            if category == 'chinese_characters':
                # Check original text for Chinese
                for term in terms:
                    if term in text:
                        detected_signals.append((category, 0.95))
                        break
            else:
                # Check normalized text for other terms
                for term in terms:
                    if term in normalized:
                        # Assign confidence based on category
                        confidence = self.get_term_confidence(category, term)
                        detected_signals.append((category, confidence))
                        break

        # Check metadata if provided
        if metadata:
            if 'country' in metadata:
                country = self.normalize_text(str(metadata['country']))
                if country in ['cn', 'china', 'chine', 'chn']:
                    detected_signals.append(('metadata_country', 0.90))

            if 'affiliation' in metadata:
                aff_normalized = self.normalize_text(str(metadata['affiliation']))
                for term in self.detection_terms['institutions']:
                    if term in aff_normalized:
                        detected_signals.append(('institution_affiliation', 0.85))
                        break

        # Calculate aggregate confidence
        if detected_signals:
            max_confidence = max(s[1] for s in detected_signals)
            unique_categories = len(set(s[0] for s in detected_signals))

            # Boost confidence for multiple signal types
            final_confidence = min(max_confidence + (unique_categories - 1) * 0.05, 1.0)

            return {
                'detected': True,
                'signals': detected_signals,
                'confidence': final_confidence,
                'signal_count': len(detected_signals)
            }

        return {'detected': False, 'signals': [], 'confidence': 0}

    def get_term_confidence(self, category, term):
        """Assign confidence scores based on term category and specificity"""
        high_confidence = {
            'chinese_characters': 0.95,
            'ticker_aliases': 0.90,
            'subsidiaries': 0.85
        }

        medium_confidence = {
            'pinyin': 0.75,
            'institutions': 0.80,
            'ports': 0.80
        }

        low_confidence = {
            'english_exonyms': 0.70,
            'french_exonyms': 0.65,
            'german_exonyms': 0.65,
            'russian_exonyms': 0.65,
            'technology_terms': 0.60
        }

        if category in high_confidence:
            return high_confidence[category]
        elif category in medium_confidence:
            return medium_confidence[category]
        else:
            return low_confidence.get(category, 0.50)

    def test_with_known_data(self):
        """Test detector with known China-related data"""
        print("Testing with known China-related data...")

        # Test with CORDIS database if available
        cordis_db = Path("data/processed/cordis_unified/cordis_china_projects.db")
        if cordis_db.exists():
            conn = sqlite3.connect(cordis_db)
            cursor = conn.cursor()

            # Get sample of projects
            cursor.execute("SELECT title, objective FROM projects LIMIT 100")
            projects = cursor.fetchall()

            china_detected = 0
            for title, objective in projects:
                text = f"{title} {objective}" if objective else title
                result = self.detect_china_signals(text)
                if result['detected']:
                    china_detected += 1

            self.test_results['detection_stats']['cordis_china_projects'] = {
                'total_tested': len(projects),
                'china_detected': china_detected,
                'detection_rate': (china_detected / len(projects) * 100) if projects else 0
            }

            conn.close()

    def test_control_group(self):
        """Test with control group (non-China data)"""
        print("Testing with control group...")

        # Control terms that should NOT trigger China detection
        control_samples = [
            "European Union research collaboration",
            "United States technology innovation",
            "Japan semiconductor manufacturing",
            "South Korea electronics industry",
            "Taiwan integrated circuits",  # This is tricky - should handle carefully
            "India software development",
            "Germany automotive engineering",
            "France aerospace technology",
            "United Kingdom artificial intelligence",
            "Canada quantum computing research"
        ]

        false_positives = []
        for sample in control_samples:
            result = self.detect_china_signals(sample)
            if result['detected']:
                false_positives.append({
                    'text': sample,
                    'signals': result['signals'],
                    'confidence': result['confidence']
                })

        self.test_results['control_group_results'] = {
            'total_control_samples': len(control_samples),
            'false_positives': len(false_positives),
            'false_positive_rate': (len(false_positives) / len(control_samples) * 100)
        }

        if false_positives:
            self.test_results['false_positives'] = false_positives

    def test_edge_cases(self):
        """Test edge cases and ambiguous terms"""
        print("Testing edge cases...")

        edge_cases = [
            ("Sino-Japanese cooperation", True, "Should detect 'Sino'"),
            ("Research with PRC institutions", True, "Should detect 'PRC'"),
            ("Canton, Ohio manufacturing", False, "US city, not China"),
            ("China cabinet furniture", False, "Furniture, not country"),
            ("Fine china dinnerware", False, "Dinnerware, not country"),
            ("Huawei Technologies Co., Ltd.", True, "Should detect company"),
            ("Honor smartphone", True, "Should detect subsidiary"),
            ("Chinese University of Hong Kong", True, "Should detect institution"),
            ("Chinatown San Francisco", False, "US location reference"),
            ("Shanghai-London Stock Connect", True, "Should detect Shanghai")
        ]

        edge_case_results = []
        for text, should_detect, note in edge_cases:
            result = self.detect_china_signals(text)
            success = result['detected'] == should_detect
            edge_case_results.append({
                'text': text,
                'expected': should_detect,
                'detected': result['detected'],
                'success': success,
                'note': note,
                'signals': result.get('signals', [])
            })

        success_rate = sum(1 for r in edge_case_results if r['success']) / len(edge_cases) * 100

        self.test_results['edge_cases'] = {
            'total_cases': len(edge_cases),
            'successful': sum(1 for r in edge_case_results if r['success']),
            'success_rate': success_rate,
            'details': edge_case_results
        }

    def generate_report(self):
        """Generate Phase 3 calibration report"""

        # Save detection dictionary
        detection_dict = {
            'generated': datetime.now().isoformat(),
            'terms_by_category': {k: list(v) for k, v in self.detection_terms.items()},
            'total_terms': sum(len(v) for v in self.detection_terms.values())
        }

        with open("C:/Projects/OSINT - Foresight/china_detection_dictionary.json", 'w', encoding='utf-8') as f:
            json.dump(detection_dict, f, indent=2, ensure_ascii=False)

        # Save test results
        with open("C:/Projects/OSINT - Foresight/china_signal_test_results.json", 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)

        # Generate markdown report
        report = f"""# Phase 3: China Signal Calibration Report

Generated: {self.test_results['generated']}

## Detection Dictionary Summary

| Category | Terms Count | Confidence Range |
|----------|-------------|------------------|
| Chinese Characters | {len(self.detection_terms['chinese_characters'])} | 0.95 |
| Pinyin | {len(self.detection_terms['pinyin'])} | 0.75 |
| English Exonyms | {len(self.detection_terms['english_exonyms'])} | 0.70 |
| French Exonyms | {len(self.detection_terms['french_exonyms'])} | 0.65 |
| German Exonyms | {len(self.detection_terms['german_exonyms'])} | 0.65 |
| Russian Exonyms | {len(self.detection_terms['russian_exonyms'])} | 0.65 |
| Subsidiaries | {len(self.detection_terms['subsidiaries'])} | 0.85 |
| Ticker Aliases | {len(self.detection_terms['ticker_aliases'])} | 0.90 |
| Ports | {len(self.detection_terms['ports'])} | 0.80 |
| Institutions | {len(self.detection_terms['institutions'])} | 0.80 |
| Technology Terms | {len(self.detection_terms['technology_terms'])} | 0.60 |

**Total Terms**: {sum(len(v) for v in self.detection_terms.values())}

## Test Results

### Known China Data Test
"""

        if 'cordis_china_projects' in self.test_results['detection_stats']:
            stats = self.test_results['detection_stats']['cordis_china_projects']
            report += f"""
- **Source**: CORDIS China Projects Database
- **Records Tested**: {stats['total_tested']}
- **China Signals Detected**: {stats['china_detected']}
- **Detection Rate**: {stats['detection_rate']:.1f}%
"""

        report += f"""
### Control Group Test

- **Control Samples**: {self.test_results['control_group_results']['total_control_samples']}
- **False Positives**: {self.test_results['control_group_results']['false_positives']}
- **False Positive Rate**: {self.test_results['control_group_results']['false_positive_rate']:.1f}%
"""

        if self.test_results['false_positives']:
            report += "\n**False Positive Examples**:\n"
            for fp in self.test_results['false_positives'][:3]:
                report += f"- \"{fp['text']}\" (confidence: {fp['confidence']:.2f})\n"

        if 'edge_cases' in self.test_results:
            edge = self.test_results['edge_cases']
            report += f"""
### Edge Cases Test

- **Total Cases**: {edge['total_cases']}
- **Successful**: {edge['successful']}
- **Success Rate**: {edge['success_rate']:.1f}%

**Failed Cases**:
"""
            for case in edge['details']:
                if not case['success']:
                    report += f"- \"{case['text']}\": {case['note']}\n"

        report += """
## Signal Detection Features

### Multi-language Support
✅ Chinese characters (中文)
✅ Pinyin romanization
✅ English, French, German, Russian exonyms

### Entity Recognition
✅ Companies and subsidiaries
✅ Academic institutions
✅ Government organizations
✅ Ports and trade hubs

### Contextual Detection
✅ Technology domain terms
✅ Stock tickers and financial aliases
✅ Metadata enrichment (country codes, affiliations)

## Confidence Scoring

The detector uses tiered confidence scoring:
- **0.95**: Chinese characters, direct entity names
- **0.85-0.90**: Subsidiaries, ticker symbols
- **0.75-0.80**: Institutions, ports, pinyin
- **0.60-0.70**: Exonyms, technology terms

Multiple signal types boost overall confidence.

## Artifacts Created

1. `china_detection_dictionary.json` - Complete term dictionary
2. `china_signal_test_results.json` - Test results and metrics
3. This report - Phase 3 documentation

## Phase 3 Complete ✓

- Detection dictionary built: **{sum(len(v) for v in self.detection_terms.values())} terms**
- Multi-language coverage: **6 languages**
- False positive rate: **{self.test_results['control_group_results']['false_positive_rate']:.1f}%**
- Edge case success: **{self.test_results.get('edge_cases', {}).get('success_rate', 0):.1f}%**
"""

        with open("C:/Projects/OSINT - Foresight/phase3_calibration_report.md", 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\nPhase 3 Complete!")
        print(f"- Detection terms: {sum(len(v) for v in self.detection_terms.values())}")
        print(f"- Test results saved: china_signal_test_results.json")
        print(f"- Report saved: phase3_calibration_report.md")

def main():
    detector = ChinaSignalDetector()
    detector.test_with_known_data()
    detector.test_control_group()
    detector.test_edge_cases()
    detector.generate_report()

if __name__ == "__main__":
    main()
