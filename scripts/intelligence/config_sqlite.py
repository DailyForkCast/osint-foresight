#!/usr/bin/env python3
"""
SQLite-specific configuration for China-Europe Intelligence Analysis
Adapted for OSINT Foresight project schema
"""

import os
import sqlite3
from datetime import datetime
import json

# Configuration
CONFIG = {
    # Database - YOUR ACTUAL DATABASE PATH
    'db_path': os.getenv('DB_PATH', 'F:/OSINT_WAREHOUSE/osint_master.db'),

    # Analysis parameters
    'min_cooccurrence': int(os.getenv('MIN_COOCCURRENCE', 2)),
    'min_consensus_mentions': int(os.getenv('MIN_CONSENSUS', 3)),
    'network_top_nodes': int(os.getenv('NETWORK_NODES', 50)),
    'narrative_spike_threshold': float(os.getenv('SPIKE_THRESHOLD', 1.5)),
    'entity_similarity_threshold': int(os.getenv('SIMILARITY', 85)),
    'batch_size': int(os.getenv('BATCH_SIZE', 5000)),

    # Output
    'output_dir': os.getenv('OUTPUT_DIR', 'C:/Projects/OSINT - Foresight/analysis/intelligence'),
    'log_level': os.getenv('LOG_LEVEL', 'INFO')
}

# Entity normalization mappings
ENTITY_VARIANTS = {
    'huawei': ['huawei', '华为', '华为技术', 'huawei technologies', 'huawei tech'],
    'tsinghua': ['tsinghua', '清华', '清华大学', 'tsinghua university', 'qinghua'],
    'cas': ['chinese academy of sciences', '中国科学院', '中科院', 'cas', 'chinese academy'],
    'beijing': ['beijing', '北京', 'peking', 'beiping'],
    'pla': ['pla', '解放军', '人民解放军', "people's liberation army", 'chinese military'],
    'smic': ['smic', '中芯国际', 'semiconductor manufacturing international'],
    'alibaba': ['alibaba', '阿里巴巴', 'alibaba group'],
    'tencent': ['tencent', '腾讯', 'tencent holdings'],
    'baidu': ['baidu', '百度'],
    'xi_jinping': ['xi jinping', '习近平', 'president xi', 'xi'],
    'dji': ['dji', '大疆', 'da-jiang'],
    'byd': ['byd', '比亚迪'],
    'cnooc': ['cnooc', '中海油', 'china national offshore oil'],
    'sinopec': ['sinopec', '中国石化', '中石化'],
    'petrochina': ['petrochina', '中国石油', '中石油'],
    'cosco': ['cosco', '中远', 'china ocean shipping'],
    'cmec': ['cmec', '中国机械', 'china machinery engineering'],
    'crrc': ['crrc', '中车', 'china railway rolling stock']
}

# Source credibility weights
SOURCE_WEIGHTS = {
    'RAND': 0.9,
    'CSIS': 0.85,
    'Brookings': 0.85,
    'MERICS': 0.9,
    'ASPI': 0.85,
    'Carnegie': 0.8,
    'Atlantic Council': 0.8,
    'Jamestown': 0.75,
    'CSET': 0.85,
    'Think Tank': 0.7,
    'Blog': 0.5,
    'Unknown': 0.3
}

# Topic taxonomy for narrative analysis
TOPIC_TAXONOMY = {
    'artificial_intelligence': {
        'synonyms': ['AI', 'machine learning', 'deep learning', 'neural network', 'algorithm'],
        'chinese_terms': ['人工智能', '机器学习', '深度学习', '神经网络'],
        'parent': 'emerging_technology',
        'related': ['computer vision', 'nlp', 'robotics', 'automation']
    },
    'military_civil_fusion': {
        'synonyms': ['MCF', 'mil-civ fusion', 'dual use', 'military civilian'],
        'chinese_terms': ['军民融合', '军民结合', '军转民', '民参军'],
        'parent': 'strategy',
        'related': ['technology transfer', 'defense industry']
    },
    'belt_and_road': {
        'synonyms': ['BRI', 'belt road', 'OBOR', 'silk road', 'one belt one road'],
        'chinese_terms': ['一带一路', '带路', '丝绸之路'],
        'parent': 'foreign_policy',
        'related': ['infrastructure', 'connectivity', 'debt']
    },
    'semiconductor': {
        'synonyms': ['chip', 'microchip', 'processor', 'foundry', 'fab', 'lithography'],
        'chinese_terms': ['半导体', '芯片', '晶片', '集成电路'],
        'parent': 'critical_technology',
        'related': ['TSMC', 'ASML', 'silicon']
    },
    'quantum': {
        'synonyms': ['quantum computing', 'quantum communication', 'quantum sensing'],
        'chinese_terms': ['量子', '量子计算', '量子通信'],
        'parent': 'emerging_technology',
        'related': ['cryptography', 'superposition', 'entanglement']
    },
    '5g': {
        'synonyms': ['5G', 'fifth generation', '5G network', 'telecommunications'],
        'chinese_terms': ['5G', '第五代', '通信'],
        'parent': 'critical_technology',
        'related': ['Huawei', 'ZTE', 'Ericsson', 'Nokia']
    },
    'taiwan': {
        'synonyms': ['Taiwan', 'Republic of China', 'ROC', 'Taipei', 'cross-strait'],
        'chinese_terms': ['台湾', '中华民国', '两岸'],
        'parent': 'geopolitics',
        'related': ['strait', 'reunification', 'independence']
    },
    'south_china_sea': {
        'synonyms': ['South China Sea', 'SCS', 'nine-dash line', 'spratly', 'paracel'],
        'chinese_terms': ['南海', '南中国海'],
        'parent': 'geopolitics',
        'related': ['territorial dispute', 'UNCLOS', 'artificial island']
    },
    'xinjiang': {
        'synonyms': ['Xinjiang', 'Uyghur', 'XUAR', 'East Turkestan'],
        'chinese_terms': ['新疆', '维吾尔', '乌鲁木齐'],
        'parent': 'human_rights',
        'related': ['re-education', 'surveillance', 'cotton']
    },
    'hong_kong': {
        'synonyms': ['Hong Kong', 'HK', 'HKSAR', 'national security law'],
        'chinese_terms': ['香港', '港'],
        'parent': 'geopolitics',
        'related': ['autonomy', 'protests', 'extradition']
    }
}

# Schema mapping for your actual database
SCHEMA_MAPPING = {
    # Your actual table and column names
    'documents': {
        'table': 'documents',
        'id': 'id',
        'content': 'content_text',  # YOUR COLUMN IS content_text not content
        'title': 'title',
        'source': 'publisher_org',  # YOUR COLUMN
        'created_date': 'publication_date',  # YOUR COLUMN
        'saved_path': 'saved_path'
    },
    'document_entities': {
        'table': 'document_entities',
        'entity_name': 'entity_text',  # YOUR COLUMN IS entity_text not entity_name
        'entity_type': 'entity_type',
        'document_id': 'document_id'
    },
    'report_entities': {
        'table': 'report_entities',
        'entity_name': 'entity_name',
        'entity_type': 'entity_type',
        'report_id': 'report_id'
    },
    'mcf_documents': {
        'table': 'mcf_documents',
        'id': 'doc_id',  # YOUR COLUMN IS doc_id not id
        'title': 'title',
        'content': 'content',
        'published_date': 'published_date',
        'source': 'source'
    },
    'mcf_entities': {
        'table': 'mcf_entities',
        'entity_text': 'name',  # YOUR COLUMN IS name not entity_text
        'entity_type': 'entity_type',
        'document_id': 'entity_id'  # YOUR SCHEMA DIFFERENT
    }
}

def get_column(table, field):
    """Get actual column name for your database"""
    return SCHEMA_MAPPING.get(table, {}).get(field, field)
