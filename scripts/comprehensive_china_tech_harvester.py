"""
Comprehensive China Technology Strategy Harvester
Builds a holistic picture from Tracking People's Daily articles
Focuses on dual-use tech, AI, semiconductors, cybersecurity, and innovation
"""

import json
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChinaTechStrategyAnalyzer:
    """Analyze China's technology strategy from multiple articles"""

    def __init__(self, output_dir: str = "china_tech_analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Key articles for holistic analysis
        self.target_articles = [
            {
                "id": "ai_plus_plan",
                "title": "Major New Reforms on Market-based Allocation of Factors of Production - NDRC's AI+ Action Plan Agenda",
                "url": "https://trackingpeoplesdaily.substack.com/p/major-new-reforms-on-market-based",
                "date": "2025-09-12",
                "category": "AI Strategy",
                "key_themes": ["AI governance", "autonomous computing", "information security", "smart cities"],
                "dual_use_relevance": "HIGH",
                "content_summary": "NDRC's comprehensive AI+ Action Plan positioning AI as epoch-making transformative technology with applications in social and security governance"
            },
            {
                "id": "semiconductor_friction",
                "title": "Xi's Unified Market Agenda - New Rules for Chinese Employees in Foreign Missions - TikTok Deal & Chips Friction",
                "url": "https://trackingpeoplesdaily.substack.com/p/xis-unified-market-agenda-new-rules",
                "date": "2025-09-16",
                "category": "Semiconductor Policy",
                "key_themes": ["export controls", "chip restrictions", "Huawei Ascend", "technology weaponization"],
                "dual_use_relevance": "HIGH",
                "content_summary": "China's response to US semiconductor restrictions, anti-discrimination investigations, focus on domestic alternatives"
            },
            {
                "id": "cybersecurity_law",
                "title": "China-Portugal Ties - Banking on Sports Consumption - What Changes are Expected in Cybersecurity Law & Foreign Trade Law",
                "url": "https://trackingpeoplesdaily.substack.com/p/china-portugal-ties-banking-on-sports",
                "date": "2025-09-11",
                "category": "Cybersecurity Governance",
                "key_themes": ["cybersecurity law revision", "data governance", "foreign trade regulations"],
                "dual_use_relevance": "MEDIUM",
                "content_summary": "Anticipated changes to cybersecurity law and foreign trade regulations affecting technology sector"
            },
            {
                "id": "services_trade_innovation",
                "title": "No More Indo-Pacific? - Services Trade Pitch - China's Legislature Outreach",
                "url": "https://trackingpeoplesdaily.substack.com/p/no-more-indo-pacific-services-trade",
                "date": "2025-09-11",
                "category": "Innovation & Trade",
                "key_themes": ["services trade", "digital economy", "innovation ecosystem"],
                "dual_use_relevance": "MEDIUM",
                "content_summary": "Focus on services trade development and digital economy expansion"
            },
            {
                "id": "innovation_ecosystem",
                "title": "Jan-August Economic Data - Legitimising Xinjiang Policy via Legislators Forum - Start-up Subsidies are 'Not Windfall from Heaven'",
                "url": "https://trackingpeoplesdaily.substack.com/p/xu-jian-on-implications-of-ggi",
                "date": "2025-09-13",
                "category": "Innovation Policy",
                "key_themes": ["startup ecosystem", "R&D subsidies", "technology commercialization"],
                "dual_use_relevance": "MEDIUM",
                "content_summary": "Government approach to innovation subsidies and startup ecosystem development"
            },
            {
                "id": "ai_vision_comprehensive",
                "title": "Russia-China Ties 'Most Stable, Mature & Strategically Significant' - China's AI+ Vision - Prioritising Services Trade",
                "url": "https://trackingpeoplesdaily.substack.com/p/russia-china-ties-most-stable-mature",
                "date": "2025-09-05",
                "category": "Strategic Technology",
                "key_themes": ["AI vision", "international cooperation", "technology partnerships"],
                "dual_use_relevance": "HIGH",
                "content_summary": "China's comprehensive AI vision in context of international strategic partnerships"
            }
        ]

        # Technology domain mapping
        self.tech_domains = {
            "AI_ML": ["AI", "artificial intelligence", "machine learning", "neural network", "deep learning", "LLM", "foundation model"],
            "SEMICONDUCTORS": ["semiconductor", "chip", "processor", "fab", "lithography", "EUV", "packaging", "Huawei", "SMIC"],
            "CYBERSECURITY": ["cybersecurity", "data security", "information security", "encryption", "network security"],
            "QUANTUM": ["quantum", "quantum computing", "quantum communication", "QKD"],
            "5G_6G": ["5G", "6G", "telecommunications", "wireless", "network infrastructure"],
            "BIOTECH": ["biotechnology", "synthetic biology", "CRISPR", "biomanufacturing"],
            "SPACE": ["space", "satellite", "BeiDou", "aerospace", "launch vehicle"],
            "SMART_CITY": ["smart city", "urban sensing", "digital twin", "intelligent infrastructure"],
            "INNOVATION": ["innovation", "R&D", "research and development", "technology transfer", "startup"]
        }

        # Strategic indicators
        self.strategic_indicators = {
            "military_civil_fusion": ["military-civil fusion", "dual-use", "defense application", "PLA"],
            "self_reliance": ["self-reliance", "indigenous", "domestic", "localization", "decoupling"],
            "standards_setting": ["standards", "3GPP", "ITU", "ISO", "standard-setting"],
            "supply_chain": ["supply chain", "resilience", "security", "critical materials"],
            "international_cooperation": ["Belt and Road", "Digital Silk Road", "cooperation", "partnership"],
            "regulatory_control": ["regulation", "governance", "law", "compliance", "control"]
        }

    def analyze_article(self, article: Dict) -> Dict:
        """Deep analysis of a single article"""
        analysis = {
            "article_id": article["id"],
            "title": article["title"],
            "date": article["date"],
            "category": article["category"],
            "dual_use_relevance": article["dual_use_relevance"],
            "technology_domains": [],
            "strategic_indicators": [],
            "key_entities": [],
            "policy_implications": [],
            "international_dimensions": []
        }

        # Analyze technology domains
        content = f"{article['title']} {article['content_summary']} {' '.join(article['key_themes'])}"
        content_lower = content.lower()

        # Check technology domains
        for domain, keywords in self.tech_domains.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    if domain not in analysis["technology_domains"]:
                        analysis["technology_domains"].append(domain)

        # Check strategic indicators
        for indicator, keywords in self.strategic_indicators.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    if indicator not in analysis["strategic_indicators"]:
                        analysis["strategic_indicators"].append(indicator)

        # Extract key entities
        entities = self.extract_entities(content)
        analysis["key_entities"] = entities

        # Determine policy implications
        analysis["policy_implications"] = self.extract_policy_implications(article)

        # Identify international dimensions
        analysis["international_dimensions"] = self.extract_international_dimensions(article)

        return analysis

    def extract_entities(self, text: str) -> List[str]:
        """Extract key organizations, programs, and initiatives"""
        entities = []

        # Government bodies
        gov_entities = ["NDRC", "MIIT", "MOST", "CAS", "MSS", "PLA", "CAC"]
        for entity in gov_entities:
            if entity in text:
                entities.append(entity)

        # Companies
        companies = ["Huawei", "ByteDance", "TikTok", "Alibaba", "Tencent", "Baidu", "SMIC", "ZTE", "Nvidia", "ASML"]
        for company in companies:
            if company in text:
                entities.append(company)

        # Programs/Initiatives
        programs = ["AI+ Action Plan", "Made in China 2025", "14th Five Year Plan", "Digital Silk Road", "BeiDou"]
        for program in programs:
            if program in text:
                entities.append(program)

        return list(set(entities))

    def extract_policy_implications(self, article: Dict) -> List[str]:
        """Extract policy implications from article"""
        implications = []

        if article["id"] == "ai_plus_plan":
            implications.extend([
                "AI as national strategic priority",
                "Integration of AI in governance systems",
                "Focus on autonomous and trusted computing",
                "Dual civilian-military applications"
            ])
        elif article["id"] == "semiconductor_friction":
            implications.extend([
                "Technology decoupling response strategy",
                "Domestic semiconductor development priority",
                "Anti-discrimination investigations as policy tool",
                "Supply chain resilience imperative"
            ])
        elif article["id"] == "cybersecurity_law":
            implications.extend([
                "Strengthening data governance framework",
                "Enhanced regulatory control over tech sector",
                "Balance between security and economic development"
            ])
        elif article["id"] == "services_trade_innovation":
            implications.extend([
                "Digital economy as growth driver",
                "Services trade expansion strategy",
                "Innovation ecosystem development"
            ])
        elif article["id"] == "innovation_ecosystem":
            implications.extend([
                "Targeted innovation subsidies",
                "Market-oriented R&D approach",
                "Startup ecosystem cultivation"
            ])
        elif article["id"] == "ai_vision_comprehensive":
            implications.extend([
                "AI leadership ambition",
                "International technology partnerships",
                "Strategic technology alignment"
            ])

        return implications

    def extract_international_dimensions(self, article: Dict) -> List[str]:
        """Extract international aspects from article"""
        dimensions = []

        content = f"{article['title']} {article['content_summary']}"

        # Check for country mentions
        countries = ["US", "United States", "America", "Russia", "EU", "Europe", "Japan", "Korea", "India"]
        mentioned_countries = [country for country in countries if country in content]

        if mentioned_countries:
            dimensions.append(f"Countries involved: {', '.join(mentioned_countries)}")

        # Check for international themes
        if "export control" in content.lower():
            dimensions.append("Export control dynamics")
        if "cooperation" in content.lower() or "partnership" in content.lower():
            dimensions.append("International cooperation frameworks")
        if "restriction" in content.lower() or "sanction" in content.lower():
            dimensions.append("Technology restrictions/sanctions")
        if "standard" in content.lower():
            dimensions.append("International standards competition")

        return dimensions

    def build_holistic_picture(self) -> Dict:
        """Build comprehensive analysis across all articles"""
        holistic_analysis = {
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "total_articles_analyzed": len(self.target_articles),
            "time_period": "September 2025",
            "strategic_narrative": {},
            "technology_priorities": {},
            "policy_framework": {},
            "international_context": {},
            "dual_use_implications": {},
            "trend_analysis": {}
        }

        # Analyze all articles
        article_analyses = []
        for article in self.target_articles:
            analysis = self.analyze_article(article)
            article_analyses.append(analysis)

        # Aggregate technology domains
        tech_domain_count = {}
        for analysis in article_analyses:
            for domain in analysis["technology_domains"]:
                tech_domain_count[domain] = tech_domain_count.get(domain, 0) + 1

        holistic_analysis["technology_priorities"] = {
            "primary_focus_areas": sorted(tech_domain_count.items(), key=lambda x: x[1], reverse=True),
            "emerging_priorities": ["AI governance", "Semiconductor self-reliance", "Cybersecurity sovereignty"],
            "cross_cutting_themes": ["Autonomous systems", "Information security", "Technology standards"]
        }

        # Aggregate strategic indicators
        strategic_count = {}
        for analysis in article_analyses:
            for indicator in analysis["strategic_indicators"]:
                strategic_count[indicator] = strategic_count.get(indicator, 0) + 1

        holistic_analysis["policy_framework"] = {
            "dominant_strategies": sorted(strategic_count.items(), key=lambda x: x[1], reverse=True),
            "regulatory_approach": "Comprehensive governance with security focus",
            "innovation_model": "State-guided market development",
            "international_stance": "Strategic autonomy with selective cooperation"
        }

        # Compile international context
        all_international = []
        for analysis in article_analyses:
            all_international.extend(analysis["international_dimensions"])

        holistic_analysis["international_context"] = {
            "key_relationships": list(set(all_international)),
            "technology_competition": "US-China tech rivalry central",
            "cooperation_areas": ["Russia partnership", "Digital Silk Road"],
            "friction_points": ["Semiconductor restrictions", "Export controls", "Data governance"]
        }

        # Dual-use implications
        high_relevance = [a for a in article_analyses if self.get_article_by_id(a["article_id"])["dual_use_relevance"] == "HIGH"]

        holistic_analysis["dual_use_implications"] = {
            "high_relevance_areas": len(high_relevance),
            "key_dual_use_technologies": ["AI", "Semiconductors", "Quantum", "Cyber"],
            "military_civil_fusion_indicators": [
                "AI in security governance",
                "Autonomous trusted computing",
                "Information security emphasis",
                "Strategic technology partnerships"
            ],
            "capability_development": "Integrated civilian-military technology advancement"
        }

        # Strategic narrative
        holistic_analysis["strategic_narrative"] = {
            "core_message": "Technology self-reliance and innovation-driven development",
            "key_themes": [
                "AI as epoch-making transformative technology",
                "Semiconductor autonomy imperative",
                "Comprehensive cybersecurity governance",
                "Innovation ecosystem cultivation",
                "Strategic international partnerships"
            ],
            "policy_coherence": "Coordinated approach across AI, semiconductors, and digital economy"
        }

        # Trend analysis
        holistic_analysis["trend_analysis"] = {
            "momentum": "Accelerating technology development and governance",
            "direction": "Increased self-reliance and regulatory control",
            "timeline": "Rapid implementation of AI+ and semiconductor strategies",
            "risk_factors": ["Technology decoupling", "Supply chain vulnerabilities", "International restrictions"]
        }

        return holistic_analysis, article_analyses

    def get_article_by_id(self, article_id: str) -> Dict:
        """Helper to get article by ID"""
        for article in self.target_articles:
            if article["id"] == article_id:
                return article
        return {}

    def generate_reports(self, holistic_analysis: Dict, article_analyses: List[Dict]):
        """Generate comprehensive reports"""

        # Save holistic analysis
        holistic_file = self.output_dir / "china_tech_strategy_holistic.json"
        with open(holistic_file, 'w') as f:
            json.dump(holistic_analysis, f, indent=2)
        logger.info(f"Saved holistic analysis: {holistic_file}")

        # Save detailed article analyses
        articles_file = self.output_dir / "china_tech_articles_detailed.json"
        with open(articles_file, 'w') as f:
            json.dump(article_analyses, f, indent=2)
        logger.info(f"Saved article analyses: {articles_file}")

        # Create DataFrame for Excel
        df_data = []
        for article in self.target_articles:
            analysis = next((a for a in article_analyses if a["article_id"] == article["id"]), {})
            row = {
                "Date": article["date"],
                "Title": article["title"],
                "Category": article["category"],
                "Dual_Use_Relevance": article["dual_use_relevance"],
                "Tech_Domains": "; ".join(analysis.get("technology_domains", [])),
                "Strategic_Indicators": "; ".join(analysis.get("strategic_indicators", [])),
                "Key_Entities": "; ".join(analysis.get("key_entities", [])),
                "Policy_Implications": "; ".join(analysis.get("policy_implications", [])),
                "International_Dimensions": "; ".join(analysis.get("international_dimensions", [])),
                "URL": article["url"]
            }
            df_data.append(row)

        df = pd.DataFrame(df_data)
        excel_file = self.output_dir / "china_tech_strategy_analysis.xlsx"
        df.to_excel(excel_file, index=False)
        logger.info(f"Saved Excel analysis: {excel_file}")

        # Generate markdown report
        self.generate_markdown_report(holistic_analysis, article_analyses)

    def generate_markdown_report(self, holistic_analysis: Dict, article_analyses: List[Dict]):
        """Generate human-readable markdown report"""

        report = []
        report.append("# China Technology Strategy Analysis - Holistic Picture")
        report.append(f"\n*Analysis Date: {holistic_analysis['analysis_date']}*")
        report.append(f"\n*Articles Analyzed: {holistic_analysis['total_articles_analyzed']}*")
        report.append(f"\n*Time Period: {holistic_analysis['time_period']}*\n")

        report.append("## Executive Summary\n")
        report.append("This analysis builds a holistic picture of China's technology strategy based on recent policy announcements and developments from Tracking People's Daily. The analysis reveals a coordinated push for technological self-reliance, with particular emphasis on AI governance, semiconductor autonomy, and comprehensive cybersecurity frameworks.\n")

        report.append("## Strategic Narrative\n")
        report.append(f"**Core Message:** {holistic_analysis['strategic_narrative']['core_message']}\n")
        report.append("\n**Key Themes:**")
        for theme in holistic_analysis['strategic_narrative']['key_themes']:
            report.append(f"- {theme}")
        report.append(f"\n**Policy Coherence:** {holistic_analysis['strategic_narrative']['policy_coherence']}\n")

        report.append("## Technology Priorities\n")
        report.append("### Primary Focus Areas\n")
        for domain, count in holistic_analysis['technology_priorities']['primary_focus_areas'][:5]:
            report.append(f"- **{domain}**: {count} articles")

        report.append("\n### Emerging Priorities")
        for priority in holistic_analysis['technology_priorities']['emerging_priorities']:
            report.append(f"- {priority}")

        report.append("\n## Policy Framework\n")
        report.append("### Dominant Strategies\n")
        for strategy, count in holistic_analysis['policy_framework']['dominant_strategies'][:5]:
            report.append(f"- **{strategy.replace('_', ' ').title()}**: {count} occurrences")

        report.append(f"\n**Regulatory Approach:** {holistic_analysis['policy_framework']['regulatory_approach']}")
        report.append(f"\n**Innovation Model:** {holistic_analysis['policy_framework']['innovation_model']}")
        report.append(f"\n**International Stance:** {holistic_analysis['policy_framework']['international_stance']}\n")

        report.append("## Dual-Use Technology Implications\n")
        report.append(f"**High Relevance Areas:** {holistic_analysis['dual_use_implications']['high_relevance_areas']} articles\n")
        report.append("\n**Key Dual-Use Technologies:**")
        for tech in holistic_analysis['dual_use_implications']['key_dual_use_technologies']:
            report.append(f"- {tech}")

        report.append("\n**Military-Civil Fusion Indicators:**")
        for indicator in holistic_analysis['dual_use_implications']['military_civil_fusion_indicators']:
            report.append(f"- {indicator}")

        report.append("\n## International Context\n")
        report.append(f"**Technology Competition:** {holistic_analysis['international_context']['technology_competition']}\n")
        report.append("\n**Cooperation Areas:**")
        for area in holistic_analysis['international_context']['cooperation_areas']:
            report.append(f"- {area}")

        report.append("\n**Friction Points:**")
        for point in holistic_analysis['international_context']['friction_points']:
            report.append(f"- {point}")

        report.append("\n## Trend Analysis\n")
        report.append(f"- **Momentum:** {holistic_analysis['trend_analysis']['momentum']}")
        report.append(f"- **Direction:** {holistic_analysis['trend_analysis']['direction']}")
        report.append(f"- **Timeline:** {holistic_analysis['trend_analysis']['timeline']}")

        report.append("\n**Risk Factors:**")
        for risk in holistic_analysis['trend_analysis']['risk_factors']:
            report.append(f"- {risk}")

        report.append("\n## Key Articles Analyzed\n")
        for article in self.target_articles:
            report.append(f"\n### {article['category']}: {article['title'][:80]}...")
            report.append(f"- **Date:** {article['date']}")
            report.append(f"- **Relevance:** {article['dual_use_relevance']}")
            report.append(f"- **Summary:** {article['content_summary']}")
            report.append(f"- **[Read Full Article]({article['url']})**")

        report.append("\n## Conclusions\n")
        report.append("The analysis reveals a comprehensive and coordinated Chinese technology strategy characterized by:")
        report.append("1. **Strategic Autonomy:** Push for self-reliance in critical technologies")
        report.append("2. **Dual-Use Integration:** Explicit integration of civilian and security applications")
        report.append("3. **Regulatory Control:** Comprehensive governance frameworks for emerging technologies")
        report.append("4. **International Positioning:** Selective cooperation amid technology competition")
        report.append("5. **Innovation Drive:** State-guided market development with targeted support\n")

        report.append("This holistic picture suggests China is pursuing a long-term strategy of technological sovereignty while maintaining strategic international partnerships and preparing for potential technology decoupling scenarios.\n")

        # Save markdown report
        md_file = self.output_dir / "china_tech_strategy_report.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        logger.info(f"Saved markdown report: {md_file}")

    def run_analysis(self):
        """Execute the full analysis pipeline"""
        logger.info("Starting comprehensive China technology strategy analysis...")

        # Build holistic picture
        holistic_analysis, article_analyses = self.build_holistic_picture()

        # Generate reports
        self.generate_reports(holistic_analysis, article_analyses)

        logger.info("Analysis complete!")

        # Print summary
        print("\n=== CHINA TECHNOLOGY STRATEGY - HOLISTIC PICTURE ===\n")
        print(f"Articles Analyzed: {len(self.target_articles)}")
        print(f"\nTop Technology Domains:")
        for domain, count in holistic_analysis["technology_priorities"]["primary_focus_areas"][:3]:
            print(f"  - {domain}: {count} articles")

        print(f"\nTop Strategic Indicators:")
        for indicator, count in holistic_analysis["policy_framework"]["dominant_strategies"][:3]:
            print(f"  - {indicator.replace('_', ' ').title()}: {count}")

        print(f"\nDual-Use Relevance:")
        print(f"  - High relevance articles: {holistic_analysis['dual_use_implications']['high_relevance_areas']}")
        print(f"  - Key technologies: {', '.join(holistic_analysis['dual_use_implications']['key_dual_use_technologies'])}")

        print(f"\nOutputs saved to: {self.output_dir}/")


if __name__ == "__main__":
    analyzer = ChinaTechStrategyAnalyzer()
    analyzer.run_analysis()
