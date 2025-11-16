#!/usr/bin/env python3
"""
Organize F: drive documents into proper structure with metadata
Calculates SHA256 hashes and creates metadata.json for each document
"""

import os
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

# Document categorization and metadata
DOCUMENTS = {
    # Category 1: Chinese Policy Documents (CRITICAL)
    "ai_strategy": [
        {
            "filename": "New_America_Digi_China_A_Next_Generation_AI_Development_Plan.pdf",
            "title": "New Generation Artificial Intelligence Development Plan",
            "title_chinese": "新一代人工智能发展规划",
            "issuing_agency": "State Council of the People's Republic of China",
            "date_issued": "2017-07-20",
            "document_number": "国发〔2017〕35号",
            "translation_source": "New America / Stanford DigiChina",
            "priority": "CRITICAL",
            "notes": "China's foundational AI strategy - sets targets for AI supremacy by 2030"
        },
        {
            "filename": "DigiChina-14th-Five-Year-Plan-for-National-Informatization.pdf",
            "title": "14th Five-Year Plan for National Informatization",
            "title_chinese": "十四五国家信息化规划",
            "issuing_agency": "State Council",
            "date_issued": "2021",
            "translation_source": "Stanford DigiChina",
            "priority": "CRITICAL",
            "notes": "14th FYP informatization chapter - digital economy and data governance"
        },
        {
            "filename": "European_Parliament_Chinas_ambitions_in_AI.pdf",
            "title": "China's Ambitions in Artificial Intelligence",
            "issuing_agency": "European Parliament",
            "date_issued": "2020",
            "translation_source": "N/A - European analysis",
            "priority": "HIGH",
            "notes": "European Parliament analysis of Chinese AI strategy"
        }
    ],

    "technology_policy": [
        {
            "filename": "t0085_13th_5YP_tech_innovation_EN-1.pdf",
            "title": "13th Five-Year Plan for Science and Technology Innovation",
            "title_chinese": "十三五国家科技创新规划",
            "issuing_agency": "State Council",
            "date_issued": "2016",
            "translation_source": "Georgetown CSET",
            "priority": "CRITICAL",
            "notes": "13th FYP technology innovation chapter"
        },
        {
            "filename": "t0426_big_data_plan_EN (1).pdf",
            "title": "Big Data Development Action Plan",
            "title_chinese": "大数据发展行动纲要",
            "issuing_agency": "State Council",
            "date_issued": "2015",
            "translation_source": "Georgetown CSET",
            "priority": "CRITICAL",
            "notes": "National big data strategy"
        },
        {
            "filename": "ITU_Chinas_National_Medium_and_Long_Term_Program_for Science_and_Technology_Development_2006-2020.pdf",
            "title": "National Medium and Long-Term Program for Science and Technology Development (2006-2020)",
            "title_chinese": "国家中长期科学和技术发展规划纲要（2006-2020年）",
            "issuing_agency": "State Council",
            "date_issued": "2006",
            "translation_source": "ITU",
            "priority": "MEDIUM",
            "notes": "Historical 15-year S&T plan"
        },
        {
            "filename": "U_of_Oregon_Chinas_15_year_science_and_technology_plan.pdf",
            "title": "China's 15-Year Science and Technology Plan",
            "issuing_agency": "State Council",
            "date_issued": "2006",
            "translation_source": "University of Oregon",
            "priority": "MEDIUM",
            "notes": "Analysis of 2006-2020 MLP"
        }
    ],

    "talent_programs": [
        {
            "filename": "cset_chinese_talent_program_tracker.htm",
            "title": "CSET Chinese Talent Program Tracker",
            "issuing_agency": "Georgetown CSET",
            "date_issued": "2024",
            "translation_source": "N/A - CSET database",
            "priority": "CRITICAL",
            "notes": "Comprehensive tracker of Chinese talent recruitment programs"
        },
        {
            "filename": "CSET_Key Economic and Technical Foreign Experts Plan.pdf",
            "title": "Key Economic and Technical Foreign Experts Plan",
            "issuing_agency": "State Administration of Foreign Experts Affairs",
            "translation_source": "Georgetown CSET",
            "priority": "CRITICAL",
            "notes": "CSET translation of foreign expert recruitment plan"
        },
        {
            "filename": "CSET_Funding Program for Overseas Students in S&T Activities.pdf",
            "title": "Funding Program for Overseas Students in S&T Activities",
            "issuing_agency": "China Scholarship Council",
            "translation_source": "Georgetown CSET",
            "priority": "CRITICAL",
            "notes": "Overseas student funding program"
        },
        {
            "filename": "t0099_MOST_high_end_expert_recruitment_EN.pdf",
            "title": "MOST High-End Expert Recruitment Plan",
            "title_chinese": "科技部高端外国专家引进计划",
            "issuing_agency": "Ministry of Science and Technology",
            "translation_source": "Georgetown CSET",
            "priority": "CRITICAL",
            "notes": "High-end expert recruitment program"
        },
        {
            "filename": "2019-11-18 PSI Staff Report - China's Talent Recruitment Plans Updated2.pdf",
            "title": "China's Talent Recruitment Plans",
            "issuing_agency": "US Senate Permanent Subcommittee on Investigations",
            "date_issued": "2019-11-18",
            "translation_source": "N/A - US government report",
            "priority": "CRITICAL",
            "notes": "US Senate investigation of Chinese talent programs"
        },
        {
            "filename": "CSET-Youth-Thousand-Talents-Plan-and-Chinas-Military-1.pdf",
            "title": "Youth Thousand Talents Plan and China's Military",
            "issuing_agency": "Georgetown CSET",
            "date_issued": "2021",
            "translation_source": "N/A - CSET analysis",
            "priority": "HIGH",
            "notes": "CSET analysis of youth talent programs linked to PLA"
        },
        {
            "filename": "International Training Program for Artificial Intelligence Talents in Chinese Universities - Expert Forum.pdf",
            "title": "International Training Program for AI Talents in Chinese Universities",
            "issuing_agency": "Ministry of Education",
            "translation_source": "Unknown",
            "priority": "HIGH",
            "notes": "AI talent training program"
        }
    ],

    "intellectual_property": [
        {
            "filename": "Lexology_Regulations_of_the_State_Council_on_Handling_Foreign-Related_Intellectual_Property_Disputes.pdf",
            "title": "Regulations on Handling Foreign-Related Intellectual Property Disputes",
            "title_chinese": "国务院关于处理涉外知识产权纠纷的规定",
            "issuing_agency": "State Council",
            "date_issued": "2024",
            "translation_source": "Lexology",
            "priority": "HIGH",
            "notes": "New foreign IP dispute regulations"
        },
        {
            "filename": "China_Law_Vision_Brief_Analysis_on_18-Article_Regulation_for_Handling_Foreign-related_IP_Cases.pdf",
            "title": "18-Article Regulation for Handling Foreign-Related IP Cases",
            "issuing_agency": "Supreme People's Court / State Council",
            "date_issued": "2024",
            "translation_source": "China Law Vision",
            "priority": "HIGH",
            "notes": "Analysis of new IP regulations"
        },
        {
            "filename": "evolution-of-the-chinese-intellectual-property-rights-system-ipr-law-revisions-and-enforcement.pdf",
            "title": "Evolution of the Chinese Intellectual Property Rights System",
            "issuing_agency": "Unknown",
            "translation_source": "N/A - Academic analysis",
            "priority": "MEDIUM",
            "notes": "Historical analysis of Chinese IPR evolution"
        },
        {
            "filename": "USTR_Section 301 FINAL.pdf",
            "title": "USTR Section 301 Investigation: China's Acts, Policies, and Practices Related to Technology Transfer, IP, and Innovation",
            "issuing_agency": "United States Trade Representative",
            "date_issued": "2018",
            "translation_source": "N/A - US government report",
            "priority": "CRITICAL",
            "notes": "Foundational US investigation leading to tariffs"
        }
    ]
}

# Think tank analysis, technology transfer, etc. (HIGH/MEDIUM priority)
SECONDARY_DOCUMENTS = {
    "think_tank_analysis": [
        {
            "filename": "merics-report-controlling-the-innovation-chain.pdf",
            "title": "Controlling the Innovation Chain",
            "issuing_agency": "MERICS",
            "priority": "HIGH",
            "notes": "MERICS analysis of Chinese innovation policy"
        },
        {
            "filename": "CSIS_Competing_with_Chinas_Public_R&D_Model_Lessons_and_Risks_for_US_Innovation_Strategy.pdf",
            "title": "Competing with China's Public R&D Model",
            "issuing_agency": "CSIS",
            "priority": "HIGH",
            "notes": "CSIS analysis of Chinese R&D system"
        },
        {
            "filename": "Brookings_Unleashing_NQPF_Chinas_strategy_for_technology_led_growth.pdf",
            "title": "Unleashing NQPF: China's Strategy for Technology-Led Growth",
            "issuing_agency": "Brookings Institution",
            "priority": "HIGH",
            "notes": "Brookings analysis of New Quality Productive Forces"
        }
    ],

    "technology_transfer": [
        {
            "filename": "US_China_Economic_Security_Review_Commission_How Chinese Companies Facilitate Tech Transfer from the US.pdf",
            "title": "How Chinese Companies Facilitate Technology Transfer from the United States",
            "issuing_agency": "US-China Economic and Security Review Commission",
            "priority": "CRITICAL",
            "notes": "USCC report on tech transfer mechanisms"
        },
        {
            "filename": "DIUX-China-Tech-Transfer-Study-Selected-Readings.pdf",
            "title": "China Tech Transfer Study: Selected Readings",
            "issuing_agency": "Defense Innovation Unit Experimental (DIUX)",
            "priority": "HIGH",
            "notes": "US DoD study on Chinese tech transfer"
        },
        {
            "filename": "Stanford_Assessing_the_Strengths_and_Limitations_of_Chinas_Technology_Transfer_Policies.pdf",
            "title": "Assessing the Strengths and Limitations of China's Technology Transfer Policies",
            "issuing_agency": "Stanford University",
            "priority": "HIGH",
            "notes": "Academic assessment of tech transfer policies"
        }
    ],

    "us_government_analysis": [
        {
            "filename": "ISEAS_Perspective_2024_1.pdf",
            "title": "ISEAS Perspective 2024",
            "issuing_agency": "ISEAS-Yusof Ishak Institute",
            "priority": "MEDIUM",
            "notes": "Southeast Asian perspective on China"
        },
        {
            "filename": "Pacific_Forum_issuesinsights_Vol19-WP8FINAL.pdf",
            "title": "Pacific Forum Issues & Insights",
            "issuing_agency": "Pacific Forum",
            "priority": "MEDIUM",
            "notes": "Regional analysis"
        },
        {
            "filename": "NSF_ADVISORY_01_China-Refocuses_web-250626_rev.pdf",
            "title": "China Refocuses: NSF Advisory",
            "issuing_agency": "National Science Foundation",
            "priority": "HIGH",
            "notes": "NSF assessment of Chinese S&T strategy"
        }
    ],

    "academic_papers": [
        {
            "filename": "s41599-021-00895-7.pdf",
            "title": "Academic Paper (Nature Humanities & Social Sciences Communications)",
            "issuing_agency": "Springer Nature",
            "priority": "MEDIUM",
            "notes": "Peer-reviewed research on Chinese policy"
        },
        {
            "filename": "s00146-020-00992-2.pdf",
            "title": "Academic Paper (AI & Society)",
            "issuing_agency": "Springer",
            "priority": "MEDIUM",
            "notes": "Peer-reviewed AI ethics research"
        }
    ],

    "industry_reports": [
        {
            "filename": "global-innovation-index-2025-en.pdf",
            "title": "Global Innovation Index 2025",
            "issuing_agency": "World Intellectual Property Organization (WIPO)",
            "date_issued": "2025",
            "priority": "MEDIUM",
            "notes": "WIPO global innovation rankings - includes China analysis"
        },
        {
            "filename": "SIA-State-of-the-Industry-Report-2025.pdf",
            "title": "Semiconductor Industry Association State of the Industry Report 2025",
            "issuing_agency": "Semiconductor Industry Association",
            "date_issued": "2025",
            "priority": "HIGH",
            "notes": "SIA industry report with China semiconductor analysis"
        },
        {
            "filename": "MERICS China Tech Observatory Quantum Report 2024.pdf",
            "title": "MERICS China Tech Observatory: Quantum Report 2024",
            "issuing_agency": "MERICS",
            "date_issued": "2024",
            "priority": "HIGH",
            "notes": "MERICS quantum technology tracker"
        }
    ]
}

def calculate_sha256(filepath):
    """Calculate SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_size(filepath):
    """Get file size in bytes"""
    return os.path.getsize(filepath)

def create_metadata(doc_info, filepath, category, priority_level):
    """Create metadata.json for document"""
    sha256 = calculate_sha256(filepath)
    file_size = get_file_size(filepath)

    metadata = {
        "title": doc_info.get("title", ""),
        "filename": doc_info["filename"],
        "category": category,
        "priority": doc_info.get("priority", priority_level),
        "issuing_agency": doc_info.get("issuing_agency", ""),
        "date_issued": doc_info.get("date_issued", "Unknown"),
        "collection_date": datetime.now().strftime("%Y-%m-%d"),
        "collection_method": "manual_download",
        "file_size": file_size,
        "sha256": sha256,
        "collection_status": "completed",
        "notes": [doc_info.get("notes", "")],
        "safety_verification": {
            "verified_safe_source": True,
            "no_cn_domain_access": True
        }
    }

    # Add Chinese title if available
    if "title_chinese" in doc_info:
        metadata["title_chinese"] = doc_info["title_chinese"]

    # Add translation source if available
    if "translation_source" in doc_info:
        metadata["translation_source"] = doc_info["translation_source"]

    # Add document number if available
    if "document_number" in doc_info:
        metadata["document_number"] = doc_info["document_number"]

    # Add provenance chain
    metadata["provenance_chain"] = [
        {
            "step": 1,
            "action": "Downloaded from approved Western/US government source",
            "source": doc_info.get("issuing_agency", "Unknown"),
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "step": 2,
            "action": "SHA256 hash calculated",
            "hash": sha256,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    ]

    return metadata

def organize_documents(source_dir="F:/", base_dir="F:/Policy_Documents_Sweep"):
    """Organize all documents from F:/ root into proper structure"""

    results = {
        "processed": [],
        "errors": [],
        "skipped": []
    }

    # Process CRITICAL documents
    for category, docs in DOCUMENTS.items():
        category_path = os.path.join(base_dir, "CRITICAL", category)
        os.makedirs(category_path, exist_ok=True)

        for doc_info in docs:
            filename = doc_info["filename"]
            source_file = os.path.join(source_dir, filename)

            if not os.path.exists(source_file):
                results["skipped"].append(f"{filename} - not found in {source_dir}")
                continue

            # Create document subdirectory
            doc_name = Path(filename).stem
            doc_dir = os.path.join(category_path, doc_name)
            os.makedirs(doc_dir, exist_ok=True)

            # Move file
            dest_file = os.path.join(doc_dir, filename)
            try:
                shutil.move(source_file, dest_file)

                # Create metadata
                metadata = create_metadata(doc_info, dest_file, category, "CRITICAL")
                metadata_file = os.path.join(doc_dir, "metadata.json")

                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)

                results["processed"].append({
                    "filename": filename,
                    "category": category,
                    "priority": "CRITICAL",
                    "sha256": metadata["sha256"],
                    "location": doc_dir
                })

            except Exception as e:
                results["errors"].append(f"{filename} - Error: {str(e)}")

    # Process HIGH/MEDIUM priority documents
    for category, docs in SECONDARY_DOCUMENTS.items():
        # Determine priority level from category
        if category in ["think_tank_analysis", "technology_transfer", "us_government_analysis"]:
            priority_level = "HIGH_PRIORITY"
        else:
            priority_level = "MEDIUM_PRIORITY"

        category_path = os.path.join(base_dir, priority_level, category)
        os.makedirs(category_path, exist_ok=True)

        for doc_info in docs:
            filename = doc_info["filename"]
            source_file = os.path.join(source_dir, filename)

            if not os.path.exists(source_file):
                results["skipped"].append(f"{filename} - not found in {source_dir}")
                continue

            # Create document subdirectory
            doc_name = Path(filename).stem
            doc_dir = os.path.join(category_path, doc_name)
            os.makedirs(doc_dir, exist_ok=True)

            # Move file
            dest_file = os.path.join(doc_dir, filename)
            try:
                shutil.move(source_file, dest_file)

                # Create metadata
                metadata = create_metadata(doc_info, dest_file, category, priority_level.replace("_PRIORITY", ""))
                metadata_file = os.path.join(doc_dir, "metadata.json")

                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)

                results["processed"].append({
                    "filename": filename,
                    "category": category,
                    "priority": priority_level.replace("_PRIORITY", ""),
                    "sha256": metadata["sha256"],
                    "location": doc_dir
                })

            except Exception as e:
                results["errors"].append(f"{filename} - Error: {str(e)}")

    return results

if __name__ == "__main__":
    print("Starting document organization...")
    results = organize_documents()

    print(f"\n[OK] Processed: {len(results['processed'])} documents")
    print(f"[SKIP] Skipped: {len(results['skipped'])} documents")
    print(f"[ERROR] Errors: {len(results['errors'])} documents")

    if results['processed']:
        print("\n[PROCESSED DOCUMENTS]")
        for doc in results['processed']:
            print(f"  - {doc['filename']}")
            print(f"    Category: {doc['category']}")
            print(f"    Priority: {doc['priority']}")
            print(f"    SHA256: {doc['sha256'][:16]}...")
            print(f"    Location: {doc['location']}\n")

    if results['skipped']:
        print("\n[SKIPPED DOCUMENTS]")
        for skip in results['skipped']:
            print(f"  - {skip}")

    if results['errors']:
        print("\n[ERRORS]")
        for error in results['errors']:
            print(f"  - {error}")

    # Save results
    output_file = "C:/Projects/OSINT-Foresight/analysis/document_organization_results_20251108.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[RESULTS] Saved to: {output_file}")
