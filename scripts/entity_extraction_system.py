#!/usr/bin/env python3
"""
Comprehensive Entity Extraction System for Think Tank Reports
Identifies Chinese companies, technologies, programs, and risk indicators
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
from datetime import datetime

# Try to load spaCy model, fallback to basic extraction if not available
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except:
    SPACY_AVAILABLE = False
    nlp = None
    print("SpaCy not available, using pattern-based extraction only")

@dataclass
class ExtractedEntity:
    """Represents an extracted entity with metadata"""
    entity_type: str
    entity_name: str
    entity_chinese_name: Optional[str]
    mention_count: int
    contexts: List[str]
    confidence: float
    risk_level: str
    sentiment: str = "neutral"

class EntityExtractor:
    """Comprehensive entity extraction system for OSINT analysis"""

    def __init__(self):
        """Initialize with comprehensive entity patterns"""

        # Major Chinese companies and their variations
        self.chinese_companies = {
            # Tech Giants
            "huawei": ["Huawei", "华为", "HiSilicon", "海思"],
            "zte": ["ZTE", "中兴", "Zhongxing", "中兴通讯"],
            "alibaba": ["Alibaba", "阿里巴巴", "Taobao", "淘宝", "Alipay", "支付宝", "Ant Group", "蚂蚁集团"],
            "tencent": ["Tencent", "腾讯", "WeChat", "微信", "QQ"],
            "baidu": ["Baidu", "百度"],
            "bytedance": ["ByteDance", "字节跳动", "TikTok", "抖音", "Douyin"],
            "xiaomi": ["Xiaomi", "小米", "Mi", "Redmi"],
            "lenovo": ["Lenovo", "联想", "Legend"],
            "oppo": ["OPPO", "OnePlus", "一加", "Realme"],
            "vivo": ["Vivo", "iQOO"],

            # Telecom & Networking
            "china_mobile": ["China Mobile", "中国移动", "CMCC"],
            "china_telecom": ["China Telecom", "中国电信"],
            "china_unicom": ["China Unicom", "中国联通"],
            "dahua": ["Dahua", "大华", "Dahua Technology"],
            "hikvision": ["Hikvision", "海康威视", "Hikv"],
            "fiberhome": ["FiberHome", "烽火通信"],

            # Aerospace & Defense
            "avic": ["AVIC", "中国航空工业集团", "Aviation Industry Corporation"],
            "comac": ["COMAC", "中国商飞", "Commercial Aircraft Corporation"],
            "casc": ["CASC", "中国航天科技集团", "China Aerospace Science"],
            "casic": ["CASIC", "中国航天科工集团"],
            "norinco": ["NORINCO", "中国兵器工业集团", "China North Industries"],
            "cetc": ["CETC", "中国电子科技集团", "China Electronics Technology"],

            # Semiconductors
            "smic": ["SMIC", "中芯国际", "Semiconductor Manufacturing"],
            "ymtc": ["YMTC", "长江存储", "Yangtze Memory"],
            "hua_hong": ["Hua Hong", "华虹", "HuaHong"],
            "cambricon": ["Cambricon", "寒武纪"],
            "horizon_robotics": ["Horizon Robotics", "地平线"],

            # AI & Autonomous
            "sensetime": ["SenseTime", "商汤科技"],
            "megvii": ["Megvii", "旷视科技", "Face++"],
            "cloudwalk": ["CloudWalk", "云从科技"],
            "yitu": ["YITU", "依图科技"],
            "iflytek": ["iFlytek", "科大讯飞"],
            "dji": ["DJI", "大疆", "Da-Jiang Innovations"],
            "nio": ["NIO", "蔚来"],
            "xpeng": ["XPeng", "小鹏", "Xiaopeng"],
            "li_auto": ["Li Auto", "理想汽车", "Lixiang"],
            "byd": ["BYD", "比亚迪", "Build Your Dreams"],

            # Energy & Nuclear
            "cnnc": ["CNNC", "中核集团", "China National Nuclear"],
            "cgn": ["CGN", "中广核", "China General Nuclear"],
            "state_grid": ["State Grid", "国家电网"],
            "sinopec": ["Sinopec", "中国石化"],
            "cnpc": ["CNPC", "中国石油", "PetroChina"],
            "cnooc": ["CNOOC", "中国海油"],

            # Finance & Investment
            "cic": ["CIC", "中投公司", "China Investment Corporation"],
            "safe": ["SAFE", "外汇管理局"],
            "icbc": ["ICBC", "工商银行"],
            "ccb": ["CCB", "建设银行", "China Construction Bank"],
            "boc": ["BOC", "中国银行", "Bank of China"],
            "abc": ["ABC", "农业银行", "Agricultural Bank"],

            # Biotech & Pharma
            "bgi": ["BGI", "华大基因", "Beijing Genomics"],
            "wuxi_apptec": ["WuXi AppTec", "药明康德"],
            "mindray": ["Mindray", "迈瑞医疗"],
        }

        # Key technologies and domains
        self.technology_patterns = {
            "ai_ml": ["artificial intelligence", "machine learning", "deep learning", "neural network",
                      "computer vision", "natural language processing", "NLP", "AI chip", "AI processor",
                      "generative AI", "large language model", "LLM", "transformer", "GPT"],
            "quantum": ["quantum computing", "quantum communication", "quantum cryptography",
                       "quantum internet", "quantum sensor", "quantum radar", "QKD"],
            "5g_6g": ["5G", "6G", "fifth generation", "sixth generation", "O-RAN", "Open RAN",
                     "millimeter wave", "mmWave", "massive MIMO", "beamforming"],
            "semiconductor": ["semiconductor", "chip", "integrated circuit", "IC", "foundry",
                            "EUV", "lithography", "wafer", "fab", "node", "nm process", "FinFET", "GAA"],
            "hypersonic": ["hypersonic", "scramjet", "boost glide", "HGV", "hypersonic glide vehicle",
                          "hypersonic cruise missile", "Mach 5+"],
            "space": ["satellite", "spacecraft", "space station", "lunar", "Mars", "asteroid",
                     "anti-satellite", "ASAT", "space debris", "orbital", "launch vehicle"],
            "cyber": ["cyber attack", "cyber espionage", "APT", "advanced persistent threat",
                     "zero-day", "malware", "ransomware", "supply chain attack", "backdoor"],
            "biotech": ["biotechnology", "genetic engineering", "CRISPR", "gene editing",
                       "synthetic biology", "gain of function", "dual-use research", "pathogen"],
            "nuclear": ["nuclear", "uranium", "enrichment", "reactor", "fusion", "fission",
                       "nuclear weapon", "warhead", "missile", "ICBM", "SLBM"],
            "autonomous": ["autonomous", "unmanned", "drone", "UAV", "UGV", "USV", "swarm",
                          "robotics", "autopilot", "self-driving", "ADAS"],
            "materials": ["rare earth", "gallium", "germanium", "lithium", "cobalt",
                         "graphene", "metamaterial", "composite", "advanced material"],
            "energy": ["battery", "solar", "wind", "hydrogen", "fusion energy", "renewable",
                      "energy storage", "grid", "smart grid", "power generation"]
        }

        # Chinese government programs and initiatives
        self.chinese_programs = {
            "mcf": ["Military-Civil Fusion", "军民融合", "MCF", "civil-military integration"],
            "mic2025": ["Made in China 2025", "中国制造2025", "MIC 2025", "China Manufacturing 2025"],
            "bri": ["Belt and Road", "一带一路", "BRI", "One Belt One Road", "OBOR", "Silk Road"],
            "thousand_talents": ["Thousand Talents", "千人计划", "Recruitment Program"],
            "14th_fyp": ["14th Five Year Plan", "十四五", "14th FYP"],
            "dual_circulation": ["Dual Circulation", "双循环", "domestic circulation"],
            "digital_silk_road": ["Digital Silk Road", "数字丝绸之路", "DSR"],
            "social_credit": ["Social Credit", "社会信用", "Social Credit System"],
            "great_firewall": ["Great Firewall", "防火长城", "GFW", "Golden Shield"],
            "xiong_an": ["Xiong'an", "雄安", "Xiongan New Area"],
            "greater_bay": ["Greater Bay Area", "大湾区", "GBA", "Guangdong-Hong Kong-Macao"]
        }

        # Risk indicator keywords
        self.risk_indicators = {
            "technology_transfer": ["technology transfer", "tech transfer", "IP theft",
                                  "intellectual property", "reverse engineering", "forced transfer"],
            "espionage": ["espionage", "spy", "intelligence gathering", "collection", "surveillance",
                         "infiltration", "insider threat", "foreign agent"],
            "supply_chain": ["supply chain", "dependency", "chokepoint", "critical minerals",
                           "single source", "concentration risk", "disruption"],
            "investment": ["acquisition", "merger", "investment", "venture capital", "PE",
                         "private equity", "greenfield", "brownfield", "FDI", "CFIUS"],
            "influence": ["influence operation", "disinformation", "propaganda", "united front",
                        "soft power", "sharp power", "elite capture", "academic influence"],
            "military": ["PLA", "People's Liberation Army", "military modernization", "A2/AD",
                       "anti-access", "area denial", "power projection", "gray zone"]
        }

        # Key Chinese institutions
        self.chinese_institutions = {
            "universities": ["Tsinghua", "清华", "Peking University", "北大", "Beihang", "北航",
                           "Harbin Institute", "哈工大", "NUDT", "国防科大", "Seven Sons"],
            "research": ["CAS", "中科院", "Chinese Academy", "CAEP", "工程物理研究院",
                       "CIAE", "原子能研究院", "AIRCAS", "遥感所"],
            "government": ["MIIT", "工信部", "MOST", "科技部", "NDRC", "发改委", "MSS", "国安部",
                         "MPS", "公安部", "SASTIND", "国防科工局", "CAC", "网信办"]
        }

    def extract_entities(self, text: str) -> Dict[str, List[ExtractedEntity]]:
        """Extract all entities from text"""

        results = {
            "companies": [],
            "technologies": [],
            "programs": [],
            "risks": [],
            "institutions": [],
            "persons": [],
            "locations": []
        }

        # Normalize text for matching
        text_lower = text.lower()

        # Extract Chinese companies
        for company_key, variations in self.chinese_companies.items():
            for variant in variations:
                pattern = r'\b' + re.escape(variant.lower()) + r'\b'
                matches = re.finditer(pattern, text_lower)
                contexts = []
                count = 0
                for match in matches:
                    count += 1
                    # Extract context (100 chars before and after)
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].replace('\n', ' ').strip()
                    contexts.append(context)

                if count > 0:
                    # Determine risk level based on company type
                    risk_level = self._assess_company_risk(company_key)

                    entity = ExtractedEntity(
                        entity_type="company",
                        entity_name=variations[0],  # Use primary name
                        entity_chinese_name=variations[1] if len(variations) > 1 and self._is_chinese(variations[1]) else None,
                        mention_count=count,
                        contexts=contexts[:3],  # Keep top 3 contexts
                        confidence=0.95,
                        risk_level=risk_level,
                        sentiment=self._analyze_sentiment(contexts)
                    )
                    results["companies"].append(entity)
                    break  # Don't double-count variations

        # Extract technologies
        for tech_category, keywords in self.technology_patterns.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = re.finditer(pattern, text_lower)
                contexts = []
                count = 0
                for match in matches:
                    count += 1
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].replace('\n', ' ').strip()
                    contexts.append(context)

                if count > 0:
                    entity = ExtractedEntity(
                        entity_type="technology",
                        entity_name=keyword,
                        entity_chinese_name=None,
                        mention_count=count,
                        contexts=contexts[:3],
                        confidence=0.9,
                        risk_level=self._assess_tech_risk(tech_category),
                        sentiment=self._analyze_sentiment(contexts)
                    )
                    results["technologies"].append(entity)

        # Extract Chinese programs
        for program_key, variations in self.chinese_programs.items():
            for variant in variations:
                pattern = r'\b' + re.escape(variant.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    count = len(re.findall(pattern, text_lower))
                    entity = ExtractedEntity(
                        entity_type="program",
                        entity_name=variations[0],
                        entity_chinese_name=variations[1] if len(variations) > 1 and self._is_chinese(variations[1]) else None,
                        mention_count=count,
                        contexts=[],
                        confidence=0.95,
                        risk_level="HIGH",
                        sentiment="threat"
                    )
                    results["programs"].append(entity)
                    break

        # Extract risk indicators
        for risk_type, indicators in self.risk_indicators.items():
            for indicator in indicators:
                pattern = r'\b' + re.escape(indicator.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    count = len(re.findall(pattern, text_lower))
                    entity = ExtractedEntity(
                        entity_type="risk_indicator",
                        entity_name=f"{risk_type}: {indicator}",
                        entity_chinese_name=None,
                        mention_count=count,
                        contexts=[],
                        confidence=0.85,
                        risk_level="HIGH",
                        sentiment="threat"
                    )
                    results["risks"].append(entity)

        # Use spaCy for person and location extraction if available
        if SPACY_AVAILABLE and nlp:
            doc = nlp(text[:1000000])  # Limit to 1M chars for performance
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    # Check if it might be Chinese
                    if self._might_be_chinese_name(ent.text):
                        entity = ExtractedEntity(
                            entity_type="person",
                            entity_name=ent.text,
                            entity_chinese_name=None,
                            mention_count=1,
                            contexts=[],
                            confidence=0.7,
                            risk_level="MEDIUM",
                            sentiment="neutral"
                        )
                        results["persons"].append(entity)
                elif ent.label_ in ["GPE", "LOC"]:
                    # Check for Chinese locations
                    if any(loc in ent.text.lower() for loc in ["china", "beijing", "shanghai", "shenzhen", "hong kong", "taiwan"]):
                        entity = ExtractedEntity(
                            entity_type="location",
                            entity_name=ent.text,
                            entity_chinese_name=None,
                            mention_count=1,
                            contexts=[],
                            confidence=0.8,
                            risk_level="LOW",
                            sentiment="neutral"
                        )
                        results["locations"].append(entity)

        # Deduplicate and sort by relevance
        for category in results:
            results[category] = self._deduplicate_entities(results[category])
            results[category].sort(key=lambda x: x.mention_count, reverse=True)

        return results

    def _assess_company_risk(self, company_key: str) -> str:
        """Assess risk level of a company based on sector"""
        critical_companies = ["huawei", "zte", "hikvision", "dahua", "smic", "avic",
                            "casc", "casic", "norinco", "cetc", "dji"]
        high_risk = ["alibaba", "tencent", "baidu", "bytedance", "sensetime", "megvii",
                    "cloudwalk", "yitu", "iflytek", "bgi", "ymtc"]

        if company_key in critical_companies:
            return "CRITICAL"
        elif company_key in high_risk:
            return "HIGH"
        else:
            return "MEDIUM"

    def _assess_tech_risk(self, tech_category: str) -> str:
        """Assess risk level of a technology"""
        critical_tech = ["nuclear", "hypersonic", "military", "cyber"]
        high_tech = ["ai_ml", "quantum", "semiconductor", "space", "autonomous"]

        if tech_category in critical_tech:
            return "CRITICAL"
        elif tech_category in high_tech:
            return "HIGH"
        else:
            return "MEDIUM"

    def _analyze_sentiment(self, contexts: List[str]) -> str:
        """Analyze sentiment from contexts"""
        threat_words = ["threat", "risk", "concern", "danger", "attack", "espionage",
                       "steal", "theft", "infiltrate", "compromise"]
        opportunity_words = ["opportunity", "cooperation", "partnership", "benefit",
                           "advantage", "growth", "innovation"]

        threat_count = 0
        opportunity_count = 0

        for context in contexts:
            context_lower = context.lower()
            threat_count += sum(1 for word in threat_words if word in context_lower)
            opportunity_count += sum(1 for word in opportunity_words if word in context_lower)

        if threat_count > opportunity_count * 2:
            return "threat"
        elif opportunity_count > threat_count * 2:
            return "opportunity"
        else:
            return "neutral"

    def _is_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def _might_be_chinese_name(self, name: str) -> bool:
        """Check if a name might be Chinese"""
        chinese_surnames = ["Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang",
                          "Zhao", "Wu", "Zhou", "Xu", "Sun", "Ma", "Zhu", "Hu",
                          "Xi", "Jiang", "Deng", "Mao"]
        return any(name.startswith(surname) for surname in chinese_surnames)

    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Deduplicate entities by name"""
        seen = {}
        for entity in entities:
            key = entity.entity_name.lower()
            if key not in seen:
                seen[key] = entity
            else:
                # Merge contexts and counts
                seen[key].mention_count += entity.mention_count
                seen[key].contexts.extend(entity.contexts)
        return list(seen.values())

    def generate_risk_summary(self, entities: Dict[str, List[ExtractedEntity]]) -> Dict:
        """Generate risk summary from extracted entities"""

        summary = {
            "total_entities": sum(len(v) for v in entities.values()),
            "critical_risks": [],
            "high_risks": [],
            "key_companies": [],
            "key_technologies": [],
            "chinese_programs": [],
            "statistics": {}
        }

        # Collect critical and high risks
        for category, entity_list in entities.items():
            for entity in entity_list:
                if entity.risk_level == "CRITICAL":
                    summary["critical_risks"].append({
                        "type": category,
                        "name": entity.entity_name,
                        "mentions": entity.mention_count
                    })
                elif entity.risk_level == "HIGH":
                    summary["high_risks"].append({
                        "type": category,
                        "name": entity.entity_name,
                        "mentions": entity.mention_count
                    })

        # Top companies and technologies
        if entities["companies"]:
            summary["key_companies"] = [
                {"name": e.entity_name, "mentions": e.mention_count, "risk": e.risk_level}
                for e in entities["companies"][:10]
            ]

        if entities["technologies"]:
            summary["key_technologies"] = [
                {"name": e.entity_name, "mentions": e.mention_count}
                for e in entities["technologies"][:10]
            ]

        if entities["programs"]:
            summary["chinese_programs"] = [
                {"name": e.entity_name, "mentions": e.mention_count}
                for e in entities["programs"]
            ]

        # Calculate statistics
        summary["statistics"] = {
            "total_companies": len(entities.get("companies", [])),
            "total_technologies": len(entities.get("technologies", [])),
            "total_programs": len(entities.get("programs", [])),
            "total_risks": len(entities.get("risks", [])),
            "critical_count": len(summary["critical_risks"]),
            "high_count": len(summary["high_risks"])
        }

        return summary


def extract_entities_from_text(text: str) -> Dict:
    """Convenience function to extract entities from text"""
    extractor = EntityExtractor()
    entities = extractor.extract_entities(text)
    summary = extractor.generate_risk_summary(entities)

    return {
        "entities": {k: [asdict(e) for e in v] for k, v in entities.items()},
        "summary": summary,
        "extraction_date": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Test with sample text
    sample_text = """
    Huawei and ZTE continue to pose significant risks to US national security through
    their involvement in 5G infrastructure. The Military-Civil Fusion strategy enables
    technology transfer from companies like SMIC and DJI to support China's military
    modernization. Artificial intelligence and quantum computing are key areas where
    Beijing is rapidly advancing, with companies like SenseTime and Megvii leading
    in facial recognition technology. The Belt and Road Initiative includes digital
    components that could enable surveillance and espionage activities.
    """

    result = extract_entities_from_text(sample_text)
    print(json.dumps(result["summary"], indent=2))
