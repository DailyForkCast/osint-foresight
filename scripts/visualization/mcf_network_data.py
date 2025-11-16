#!/usr/bin/env python3
"""
MCF Institutional Network Data
Defines agencies, relationships, and weights for visualization
"""

# Central Coordination Bodies
CENTRAL_COORDINATION = {
    "Central MCF Commission": {
        "type": "central_authority",
        "tier": 1,
        "description": "Top-level coordination body",
        "chair": "Xi Jinping (General Secretary, President, CMC Chair)",
        "established": 2017,
        "power_level": 10
    },
    "State Council": {
        "type": "central_authority",
        "tier": 1,
        "description": "Government executive",
        "established": 1954,
        "power_level": 9
    },
    "Central Military Commission": {
        "type": "central_authority",
        "tier": 1,
        "description": "Military leadership",
        "established": 1949,
        "power_level": 10
    }
}

# Key Ministries and Commissions
MINISTRIES = {
    "Ministry of Industry and Information Technology": {
        "type": "ministry",
        "tier": 2,
        "abbreviation": "MIIT",
        "mcf_role": "Industrial technology integration",
        "key_sectors": ["Semiconductors", "Telecommunications", "Advanced Manufacturing"],
        "power_level": 8
    },
    "Ministry of Science and Technology": {
        "type": "ministry",
        "tier": 2,
        "abbreviation": "MOST",
        "mcf_role": "Research coordination",
        "key_sectors": ["Basic Research", "Applied Technology", "Innovation"],
        "power_level": 7
    },
    "Ministry of Education": {
        "type": "ministry",
        "tier": 2,
        "abbreviation": "MOE",
        "mcf_role": "Talent pipeline",
        "key_sectors": ["University Research", "STEM Education", "Talent Recruitment"],
        "power_level": 6
    },
    "National Development and Reform Commission": {
        "type": "commission",
        "tier": 2,
        "abbreviation": "NDRC",
        "mcf_role": "Strategic planning",
        "key_sectors": ["Economic Planning", "Industrial Policy", "Infrastructure"],
        "power_level": 9
    },
    "State-owned Assets Supervision and Administration Commission": {
        "type": "commission",
        "tier": 2,
        "abbreviation": "SASAC",
        "mcf_role": "SOE coordination",
        "key_sectors": ["State Enterprises", "Defense Industry", "Strategic Resources"],
        "power_level": 8
    },
    "Ministry of State Security": {
        "type": "ministry",
        "tier": 2,
        "abbreviation": "MSS",
        "mcf_role": "Intelligence collection",
        "key_sectors": ["Technology Intelligence", "Counterintelligence", "Talent Recruitment"],
        "power_level": 9
    }
}

# Key Agencies and Organizations
AGENCIES = {
    "Chinese Academy of Sciences": {
        "type": "research_institution",
        "tier": 3,
        "abbreviation": "CAS",
        "mcf_role": "Basic and applied research",
        "key_sectors": ["Advanced Materials", "Quantum", "Space", "AI"],
        "power_level": 7
    },
    "Chinese Academy of Engineering": {
        "type": "research_institution",
        "tier": 3,
        "abbreviation": "CAE",
        "mcf_role": "Engineering research",
        "key_sectors": ["Engineering", "Industrial Technology"],
        "power_level": 6
    },
    "PLA Strategic Support Force": {
        "type": "military",
        "tier": 3,
        "abbreviation": "SSF",
        "mcf_role": "Cyber, space, electronic warfare",
        "key_sectors": ["Cyber", "Space", "Electronic Warfare"],
        "power_level": 9
    },
    "State Administration for Science, Technology and Industry for National Defense": {
        "type": "agency",
        "tier": 3,
        "abbreviation": "SASTIND",
        "mcf_role": "Defense technology coordination",
        "key_sectors": ["Defense Industry", "Space", "Nuclear"],
        "power_level": 8
    }
}

# Provincial Implementation
PROVINCIAL = {
    "Provincial MCF Offices": {
        "type": "provincial",
        "tier": 4,
        "description": "31 provincial-level MCF coordination offices",
        "power_level": 5
    },
    "Provincial Development Zones": {
        "type": "provincial",
        "tier": 4,
        "description": "Special economic zones with MCF mandates",
        "power_level": 4
    }
}

# Implementation Entities
IMPLEMENTATION = {
    "State-Owned Enterprises": {
        "type": "implementation",
        "tier": 5,
        "abbreviation": "SOEs",
        "examples": ["AVIC", "NORINCO", "CETC", "Huawei (unofficial)"],
        "mcf_role": "Technology development and acquisition",
        "power_level": 7
    },
    "University Defense Labs": {
        "type": "implementation",
        "tier": 5,
        "description": "University laboratories with defense research missions",
        "examples": ["Tsinghua", "Beihang", "NUDT", "Harbin Institute of Technology"],
        "mcf_role": "Dual-use research",
        "power_level": 6
    },
    "Talent Recruitment Programs": {
        "type": "implementation",
        "tier": 5,
        "description": "Overseas talent acquisition",
        "examples": ["Thousand Talents", "Changjiang Scholars"],
        "mcf_role": "Technology transfer through personnel",
        "power_level": 5
    }
}

# Relationships (from -> to, weight, type)
RELATIONSHIPS = [
    # Central Coordination
    {
        "from": "Central MCF Commission",
        "to": "State Council",
        "weight": 10,
        "type": "coordinates",
        "description": "Policy coordination"
    },
    {
        "from": "Central MCF Commission",
        "to": "Central Military Commission",
        "weight": 10,
        "type": "coordinates",
        "description": "Military-civil integration"
    },

    # Ministry Oversight
    {
        "from": "State Council",
        "to": "Ministry of Industry and Information Technology",
        "weight": 9,
        "type": "directs",
        "description": "Industrial policy"
    },
    {
        "from": "State Council",
        "to": "Ministry of Science and Technology",
        "weight": 8,
        "type": "directs",
        "description": "S&T policy"
    },
    {
        "from": "State Council",
        "to": "Ministry of Education",
        "weight": 7,
        "type": "directs",
        "description": "Education policy"
    },
    {
        "from": "State Council",
        "to": "National Development and Reform Commission",
        "weight": 10,
        "type": "directs",
        "description": "Economic planning"
    },
    {
        "from": "State Council",
        "to": "State-owned Assets Supervision and Administration Commission",
        "weight": 9,
        "type": "directs",
        "description": "SOE oversight"
    },

    # Intelligence
    {
        "from": "Central MCF Commission",
        "to": "Ministry of State Security",
        "weight": 9,
        "type": "coordinates",
        "description": "Intelligence collection"
    },

    # Research Institutions
    {
        "from": "Ministry of Science and Technology",
        "to": "Chinese Academy of Sciences",
        "weight": 8,
        "type": "funds",
        "description": "Research funding"
    },
    {
        "from": "Ministry of Science and Technology",
        "to": "Chinese Academy of Engineering",
        "weight": 7,
        "type": "funds",
        "description": "Engineering research"
    },

    # Military Coordination
    {
        "from": "Central Military Commission",
        "to": "PLA Strategic Support Force",
        "weight": 10,
        "type": "commands",
        "description": "Military operations"
    },
    {
        "from": "Central Military Commission",
        "to": "State Administration for Science, Technology and Industry for National Defense",
        "weight": 9,
        "type": "coordinates",
        "description": "Defense technology"
    },

    # Provincial Implementation
    {
        "from": "State Council",
        "to": "Provincial MCF Offices",
        "weight": 7,
        "type": "directs",
        "description": "Provincial implementation"
    },
    {
        "from": "National Development and Reform Commission",
        "to": "Provincial Development Zones",
        "weight": 6,
        "type": "coordinates",
        "description": "Economic zones"
    },

    # Implementation Entities
    {
        "from": "State-owned Assets Supervision and Administration Commission",
        "to": "State-Owned Enterprises",
        "weight": 9,
        "type": "controls",
        "description": "SOE management"
    },
    {
        "from": "Ministry of Education",
        "to": "University Defense Labs",
        "weight": 7,
        "type": "oversees",
        "description": "University research"
    },
    {
        "from": "Ministry of State Security",
        "to": "Talent Recruitment Programs",
        "weight": 8,
        "type": "coordinates",
        "description": "Talent acquisition"
    },
    {
        "from": "State Administration for Science, Technology and Industry for National Defense",
        "to": "State-Owned Enterprises",
        "weight": 8,
        "type": "coordinates",
        "description": "Defense industry"
    },

    # Cross-connections
    {
        "from": "Chinese Academy of Sciences",
        "to": "University Defense Labs",
        "weight": 6,
        "type": "collaborates",
        "description": "Joint research"
    },
    {
        "from": "Ministry of Industry and Information Technology",
        "to": "State-Owned Enterprises",
        "weight": 8,
        "type": "guides",
        "description": "Industrial policy"
    },
    {
        "from": "PLA Strategic Support Force",
        "to": "State-Owned Enterprises",
        "weight": 7,
        "type": "procures_from",
        "description": "Military procurement"
    }
]

# Technology Flow Paths (for Sankey diagram)
TECHNOLOGY_FLOWS = [
    # Foreign Technology Acquisition
    {
        "source": "Foreign Universities",
        "target": "University Defense Labs",
        "value": 100,
        "color": "#FF6B6B"
    },
    {
        "source": "Foreign Universities",
        "target": "Talent Recruitment Programs",
        "value": 80,
        "color": "#FF6B6B"
    },
    {
        "source": "Foreign Companies",
        "target": "State-Owned Enterprises",
        "value": 120,
        "color": "#FF6B6B"
    },

    # Domestic Processing
    {
        "source": "University Defense Labs",
        "target": "Chinese Academy of Sciences",
        "value": 90,
        "color": "#4ECDC4"
    },
    {
        "source": "Talent Recruitment Programs",
        "target": "University Defense Labs",
        "value": 70,
        "color": "#4ECDC4"
    },
    {
        "source": "State-Owned Enterprises",
        "target": "Chinese Academy of Sciences",
        "value": 60,
        "color": "#4ECDC4"
    },

    # Military Application
    {
        "source": "Chinese Academy of Sciences",
        "target": "PLA Strategic Support Force",
        "value": 85,
        "color": "#95E1D3"
    },
    {
        "source": "State-Owned Enterprises",
        "target": "PLA Strategic Support Force",
        "value": 100,
        "color": "#95E1D3"
    },
    {
        "source": "University Defense Labs",
        "target": "State Administration for Science, Technology and Industry for National Defense",
        "value": 75,
        "color": "#95E1D3"
    },

    # Civilian Application
    {
        "source": "Chinese Academy of Sciences",
        "target": "State-Owned Enterprises",
        "value": 70,
        "color": "#F38181"
    },
    {
        "source": "PLA Strategic Support Force",
        "target": "State-Owned Enterprises",
        "value": 50,
        "color": "#F38181"
    }
]

# Governance Hierarchy (for Graphviz tree)
GOVERNANCE_HIERARCHY = {
    "name": "Xi Jinping",
    "title": "General Secretary, President, CMC Chair",
    "children": [
        {
            "name": "Central MCF Commission",
            "title": "Top Coordination Body (Chair: Xi Jinping)",
            "children": [
                {
                    "name": "State Council",
                    "title": "Government Executive",
                    "children": [
                        {"name": "MIIT", "title": "Industrial Technology"},
                        {"name": "MOST", "title": "Research Coordination"},
                        {"name": "MOE", "title": "Talent Pipeline"},
                        {"name": "NDRC", "title": "Strategic Planning"},
                        {"name": "SASAC", "title": "SOE Oversight"}
                    ]
                },
                {
                    "name": "Central Military Commission",
                    "title": "Military Leadership (Chair: Xi Jinping)",
                    "children": [
                        {"name": "PLA SSF", "title": "Cyber, Space, EW"},
                        {"name": "SASTIND", "title": "Defense Technology"}
                    ]
                },
                {
                    "name": "Ministry of State Security",
                    "title": "Intelligence Collection"
                }
            ]
        }
    ]
}

# Color schemes for different visualization types
COLOR_SCHEMES = {
    "institutional_architecture": {
        "central_authority": "#E74C3C",  # Red
        "ministry": "#3498DB",  # Blue
        "commission": "#9B59B6",  # Purple
        "agency": "#1ABC9C",  # Teal
        "research_institution": "#F39C12",  # Orange
        "military": "#E67E22",  # Dark Orange
        "provincial": "#95A5A6",  # Gray
        "implementation": "#27AE60"  # Green
    },
    "relationship_types": {
        "coordinates": "#E74C3C",
        "directs": "#3498DB",
        "commands": "#8E44AD",
        "funds": "#F39C12",
        "controls": "#C0392B",
        "oversees": "#16A085",
        "guides": "#2980B9",
        "collaborates": "#27AE60",
        "procures_from": "#D35400"
    }
}

def get_all_nodes():
    """Get all nodes for network graph"""
    nodes = []

    for name, data in CENTRAL_COORDINATION.items():
        nodes.append({
            "id": name,
            "label": name,
            "type": data["type"],
            "tier": data["tier"],
            "power_level": data.get("power_level", 5),
            **data
        })

    for name, data in MINISTRIES.items():
        nodes.append({
            "id": name,
            "label": data.get("abbreviation", name),
            "type": data["type"],
            "tier": data["tier"],
            "power_level": data.get("power_level", 5),
            **data
        })

    for name, data in AGENCIES.items():
        nodes.append({
            "id": name,
            "label": data.get("abbreviation", name),
            "type": data["type"],
            "tier": data["tier"],
            "power_level": data.get("power_level", 5),
            **data
        })

    for name, data in PROVINCIAL.items():
        nodes.append({
            "id": name,
            "label": name,
            "type": data["type"],
            "tier": data["tier"],
            "power_level": data.get("power_level", 5),
            **data
        })

    for name, data in IMPLEMENTATION.items():
        nodes.append({
            "id": name,
            "label": data.get("abbreviation", name),
            "type": data["type"],
            "tier": data["tier"],
            "power_level": data.get("power_level", 5),
            **data
        })

    return nodes

def get_all_edges():
    """Get all edges for network graph"""
    return RELATIONSHIPS

if __name__ == "__main__":
    # Print summary
    nodes = get_all_nodes()
    edges = get_all_edges()

    print("=" * 80)
    print("MCF INSTITUTIONAL NETWORK DATA")
    print("=" * 80)
    print()
    print(f"Total Nodes: {len(nodes)}")
    print(f"Total Edges: {len(edges)}")
    print()

    print("Nodes by Type:")
    from collections import Counter
    type_counts = Counter(node['type'] for node in nodes)
    for node_type, count in type_counts.most_common():
        print(f"  {node_type}: {count}")
    print()

    print("Edges by Type:")
    edge_types = Counter(edge['type'] for edge in edges)
    for edge_type, count in edge_types.most_common():
        print(f"  {edge_type}: {count}")
