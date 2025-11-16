#!/usr/bin/env python3
"""
MCF Graphviz Hierarchy Visualization
Creates governance tree and organizational hierarchy using Graphviz
"""

import graphviz
from pathlib import Path
import json

# Import our data
from mcf_network_data import GOVERNANCE_HIERARCHY, CENTRAL_COORDINATION, MINISTRIES, AGENCIES


def create_governance_tree(output_dir="visualizations"):
    """
    Create governance hierarchy tree using Graphviz
    Shows Xi Jinping -> MCF Commission -> Ministries/Military structure

    Args:
        output_dir: Directory for output files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create directed graph
    dot = graphviz.Digraph(
        name='MCF_Governance_Hierarchy',
        comment='China MCF Governance Structure',
        format='png',
        engine='dot'
    )

    # Graph attributes
    dot.attr(
        rankdir='TB',  # Top to bottom
        bgcolor='white',
        fontname='Arial',
        fontsize='14',
        splines='ortho',
        nodesep='0.5',
        ranksep='0.8'
    )

    # Node defaults
    dot.attr(
        'node',
        shape='box',
        style='filled,rounded',
        fontname='Arial',
        fontsize='11',
        fontcolor='#2C3E50',
        margin='0.3,0.2'
    )

    # Edge defaults
    dot.attr(
        'edge',
        color='#34495E',
        penwidth='2',
        arrowsize='0.8'
    )

    # Add root node - Xi Jinping
    dot.node(
        'xi',
        label='Xi Jinping\nGeneral Secretary, President, CMC Chair',
        fillcolor='#E74C3C',
        fontcolor='white',
        fontsize='14',
        shape='box',
        style='filled,rounded,bold'
    )

    # Add Central MCF Commission
    dot.node(
        'mcf_commission',
        label='Central MCF Commission\n(Chair: Xi Jinping)',
        fillcolor='#C0392B',
        fontcolor='white',
        fontsize='12',
        style='filled,rounded'
    )

    dot.edge('xi', 'mcf_commission', label='Chairs', fontsize='10')

    # Add State Council
    dot.node(
        'state_council',
        label='State Council\n(Government Executive)',
        fillcolor='#3498DB',
        fontcolor='white',
        fontsize='12'
    )

    dot.edge('mcf_commission', 'state_council', label='Coordinates', fontsize='10')

    # Add Central Military Commission
    dot.node(
        'cmc',
        label='Central Military Commission\n(Chair: Xi Jinping)',
        fillcolor='#E67E22',
        fontcolor='white',
        fontsize='12'
    )

    dot.edge('mcf_commission', 'cmc', label='Coordinates', fontsize='10')

    # Add key ministries under State Council
    ministries_data = [
        ('miit', 'MIIT\nIndustrial Technology', '#3498DB'),
        ('most', 'MOST\nResearch Coordination', '#3498DB'),
        ('moe', 'MOE\nTalent Pipeline', '#3498DB'),
        ('ndrc', 'NDRC\nStrategic Planning', '#9B59B6'),
        ('sasac', 'SASAC\nSOE Oversight', '#9B59B6'),
    ]

    for node_id, label, color in ministries_data:
        dot.node(node_id, label=label, fillcolor=color, fontcolor='white', fontsize='10')
        dot.edge('state_council', node_id, fontsize='9')

    # Add Ministry of State Security (reports to MCF Commission)
    dot.node(
        'mss',
        label='Ministry of State Security\nIntelligence Collection',
        fillcolor='#8E44AD',
        fontcolor='white',
        fontsize='10'
    )

    dot.edge('mcf_commission', 'mss', label='Directs', fontsize='9')

    # Add military/defense agencies under CMC
    military_data = [
        ('pla_ssf', 'PLA Strategic Support Force\nCyber, Space, EW', '#E67E22'),
        ('sastind', 'SASTIND\nDefense Technology', '#D35400'),
    ]

    for node_id, label, color in military_data:
        dot.node(node_id, label=label, fillcolor=color, fontcolor='white', fontsize='10')
        dot.edge('cmc', node_id, fontsize='9')

    # Add research institutions under MOST
    dot.node(
        'cas',
        label='Chinese Academy\nof Sciences',
        fillcolor='#F39C12',
        fontsize='9'
    )

    dot.edge('most', 'cas', fontsize='8')

    # Add SOEs under SASAC
    dot.node(
        'soes',
        label='State-Owned\nEnterprises\n(AVIC, NORINCO, CETC)',
        fillcolor='#27AE60',
        fontsize='9'
    )

    dot.edge('sasac', 'soes', fontsize='8')

    # Add University Labs under MOE
    dot.node(
        'university_labs',
        label='University Defense Labs\n(Tsinghua, Beihang, NUDT)',
        fillcolor='#16A085',
        fontsize='9'
    )

    dot.edge('moe', 'university_labs', fontsize='8')

    # Add cross-connections
    dot.edge('cas', 'soes', label='Technology Transfer', style='dashed', color='#95A5A6', fontsize='8')
    dot.edge('university_labs', 'pla_ssf', label='Research Collaboration', style='dashed', color='#95A5A6', fontsize='8')
    dot.edge('soes', 'pla_ssf', label='Procurement', style='dashed', color='#95A5A6', fontsize='8')

    # Save outputs
    output_base = output_path / "mcf_governance_hierarchy"

    # Render to different formats
    dot.render(str(output_base), format='png', cleanup=True)
    dot.render(str(output_base), format='svg', cleanup=True)
    dot.render(str(output_base), format='pdf', cleanup=True)

    # Also save the source
    dot.save(str(output_base) + '.gv')

    print(f"[SAVED] PNG: {output_base}.png")
    print(f"[SAVED] SVG: {output_base}.svg")
    print(f"[SAVED] PDF: {output_base}.pdf")
    print(f"[SAVED] Source: {output_base}.gv")

    return str(output_base) + '.png', str(output_base) + '.svg'


def create_institutional_layers_diagram(output_dir="visualizations"):
    """
    Create layered diagram showing MCF institutional architecture by tier
    """
    output_path = Path(output_dir)

    dot = graphviz.Digraph(
        name='MCF_Institutional_Layers',
        comment='MCF Institutional Architecture by Tier',
        format='png',
        engine='dot'
    )

    # Graph attributes
    dot.attr(
        rankdir='TB',
        bgcolor='white',
        fontname='Arial',
        fontsize='12',
        splines='line',
        nodesep='0.8',
        ranksep='1.2'
    )

    dot.attr('node', shape='box', style='filled', fontname='Arial')
    dot.attr('edge', color='#34495E', penwidth='1.5')

    # Create subgraphs for each tier
    with dot.subgraph(name='cluster_tier1') as c:
        c.attr(label='Tier 1: Central Leadership', fontsize='14', style='filled', color='#FADBD8')
        c.node('tier1_mcf', 'Central MCF\nCommission', fillcolor='#E74C3C', fontcolor='white')
        c.node('tier1_sc', 'State Council', fillcolor='#E74C3C', fontcolor='white')
        c.node('tier1_cmc', 'Central Military\nCommission', fillcolor='#E74C3C', fontcolor='white')

    with dot.subgraph(name='cluster_tier2') as c:
        c.attr(label='Tier 2: Key Ministries & Commissions', fontsize='14', style='filled', color='#D6EAF8')
        c.node('tier2_miit', 'MIIT', fillcolor='#3498DB', fontcolor='white')
        c.node('tier2_most', 'MOST', fillcolor='#3498DB', fontcolor='white')
        c.node('tier2_ndrc', 'NDRC', fillcolor='#9B59B6', fontcolor='white')
        c.node('tier2_sasac', 'SASAC', fillcolor='#9B59B6', fontcolor='white')
        c.node('tier2_mss', 'MSS', fillcolor='#8E44AD', fontcolor='white')

    with dot.subgraph(name='cluster_tier3') as c:
        c.attr(label='Tier 3: Key Agencies', fontsize='14', style='filled', color='#FCF3CF')
        c.node('tier3_cas', 'Chinese Academy\nof Sciences', fillcolor='#F39C12')
        c.node('tier3_ssf', 'PLA Strategic\nSupport Force', fillcolor='#E67E22', fontcolor='white')
        c.node('tier3_sastind', 'SASTIND', fillcolor='#D35400', fontcolor='white')

    with dot.subgraph(name='cluster_tier4') as c:
        c.attr(label='Tier 4: Provincial Implementation', fontsize='14', style='filled', color='#D5D8DC')
        c.node('tier4_provincial', 'Provincial MCF\nOffices (31)', fillcolor='#95A5A6', fontcolor='white')
        c.node('tier4_zones', 'Development\nZones', fillcolor='#95A5A6', fontcolor='white')

    with dot.subgraph(name='cluster_tier5') as c:
        c.attr(label='Tier 5: Implementation Entities', fontsize='14', style='filled', color='#D5F4E6')
        c.node('tier5_soes', 'State-Owned\nEnterprises', fillcolor='#27AE60', fontcolor='white')
        c.node('tier5_unis', 'University\nDefense Labs', fillcolor='#16A085', fontcolor='white')
        c.node('tier5_talent', 'Talent Recruitment\nPrograms', fillcolor='#1ABC9C', fontcolor='white')

    # Add connections between tiers
    dot.edge('tier1_mcf', 'tier1_sc')
    dot.edge('tier1_mcf', 'tier1_cmc')

    dot.edge('tier1_sc', 'tier2_miit')
    dot.edge('tier1_sc', 'tier2_most')
    dot.edge('tier1_sc', 'tier2_ndrc')
    dot.edge('tier1_sc', 'tier2_sasac')
    dot.edge('tier1_mcf', 'tier2_mss')

    dot.edge('tier2_most', 'tier3_cas')
    dot.edge('tier1_cmc', 'tier3_ssf')
    dot.edge('tier1_cmc', 'tier3_sastind')

    dot.edge('tier1_sc', 'tier4_provincial')
    dot.edge('tier2_ndrc', 'tier4_zones')

    dot.edge('tier2_sasac', 'tier5_soes')
    dot.edge('tier2_most', 'tier5_unis')
    dot.edge('tier2_mss', 'tier5_talent')

    # Save outputs
    output_base = output_path / "mcf_institutional_layers"

    dot.render(str(output_base), format='png', cleanup=True)
    dot.render(str(output_base), format='svg', cleanup=True)
    dot.render(str(output_base), format='pdf', cleanup=True)
    dot.save(str(output_base) + '.gv')

    print(f"[SAVED] PNG: {output_base}.png")
    print(f"[SAVED] SVG: {output_base}.svg")
    print(f"[SAVED] PDF: {output_base}.pdf")
    print(f"[SAVED] Source: {output_base}.gv")

    return str(output_base) + '.png', str(output_base) + '.svg'


def create_command_flow_diagram(output_dir="visualizations"):
    """
    Create diagram showing command and control flows
    """
    output_path = Path(output_dir)

    dot = graphviz.Digraph(
        name='MCF_Command_Flow',
        comment='MCF Command and Control Flows',
        format='png',
        engine='dot'
    )

    dot.attr(
        rankdir='LR',  # Left to right
        bgcolor='white',
        fontname='Arial',
        fontsize='12'
    )

    dot.attr('node', shape='box', style='filled,rounded', fontname='Arial')

    # Define relationship types with colors
    relationship_colors = {
        'commands': '#8E44AD',
        'directs': '#3498DB',
        'coordinates': '#E74C3C',
        'funds': '#F39C12',
        'controls': '#C0392B'
    }

    # Xi Jinping
    dot.node('xi', 'Xi Jinping', fillcolor='#E74C3C', fontcolor='white', shape='ellipse', fontsize='14')

    # MCF Commission
    dot.node('mcf', 'Central MCF\nCommission', fillcolor='#C0392B', fontcolor='white')

    # State organs
    dot.node('sc', 'State Council', fillcolor='#3498DB', fontcolor='white')
    dot.node('cmc', 'Central Military\nCommission', fillcolor='#E67E22', fontcolor='white')

    # Key ministries
    dot.node('miit', 'MIIT', fillcolor='#3498DB')
    dot.node('ndrc', 'NDRC', fillcolor='#9B59B6', fontcolor='white')
    dot.node('sasac', 'SASAC', fillcolor='#9B59B6', fontcolor='white')

    # Military
    dot.node('ssf', 'PLA SSF', fillcolor='#E67E22', fontcolor='white')

    # Implementation
    dot.node('soes', 'SOEs', fillcolor='#27AE60', fontcolor='white')
    dot.node('cas', 'CAS', fillcolor='#F39C12')

    # Command flows
    dot.edge('xi', 'mcf', label='Chairs', color=relationship_colors['commands'], fontsize='10')
    dot.edge('xi', 'cmc', label='Chairs', color=relationship_colors['commands'], fontsize='10')

    dot.edge('mcf', 'sc', label='Coordinates', color=relationship_colors['coordinates'], fontsize='10')
    dot.edge('mcf', 'cmc', label='Coordinates', color=relationship_colors['coordinates'], fontsize='10')

    dot.edge('sc', 'miit', label='Directs', color=relationship_colors['directs'], fontsize='9')
    dot.edge('sc', 'ndrc', label='Directs', color=relationship_colors['directs'], fontsize='9')
    dot.edge('sc', 'sasac', label='Directs', color=relationship_colors['directs'], fontsize='9')

    dot.edge('cmc', 'ssf', label='Commands', color=relationship_colors['commands'], fontsize='9')

    dot.edge('sasac', 'soes', label='Controls', color=relationship_colors['controls'], fontsize='9')
    dot.edge('ndrc', 'cas', label='Funds', color=relationship_colors['funds'], fontsize='9')

    # Cross-connections
    dot.edge('soes', 'ssf', label='Procures', style='dashed', color='#95A5A6', fontsize='8')
    dot.edge('cas', 'soes', label='Tech Transfer', style='dashed', color='#95A5A6', fontsize='8')

    # Add legend
    with dot.subgraph(name='cluster_legend') as c:
        c.attr(label='Relationship Types', fontsize='12')
        c.node('leg_commands', 'Commands', fillcolor=relationship_colors['commands'], fontcolor='white', shape='note')
        c.node('leg_directs', 'Directs', fillcolor=relationship_colors['directs'], fontcolor='white', shape='note')
        c.node('leg_coordinates', 'Coordinates', fillcolor=relationship_colors['coordinates'], fontcolor='white', shape='note')
        c.node('leg_funds', 'Funds', fillcolor=relationship_colors['funds'], shape='note')
        c.node('leg_controls', 'Controls', fillcolor=relationship_colors['controls'], fontcolor='white', shape='note')

    # Save outputs
    output_base = output_path / "mcf_command_flow"

    dot.render(str(output_base), format='png', cleanup=True)
    dot.render(str(output_base), format='svg', cleanup=True)
    dot.render(str(output_base), format='pdf', cleanup=True)
    dot.save(str(output_base) + '.gv')

    print(f"[SAVED] PNG: {output_base}.png")
    print(f"[SAVED] SVG: {output_base}.svg")
    print(f"[SAVED] PDF: {output_base}.pdf")
    print(f"[SAVED] Source: {output_base}.gv")

    return str(output_base) + '.png', str(output_base) + '.svg'


if __name__ == "__main__":
    print("=" * 80)
    print("MCF GRAPHVIZ HIERARCHY VISUALIZATION")
    print("=" * 80)
    print()

    # Create governance tree
    print("Creating governance hierarchy tree...")
    gov_png, gov_svg = create_governance_tree()
    print()

    # Create institutional layers diagram
    print("Creating institutional layers diagram...")
    layers_png, layers_svg = create_institutional_layers_diagram()
    print()

    # Create command flow diagram
    print("Creating command and control flow diagram...")
    cmd_png, cmd_svg = create_command_flow_diagram()
    print()

    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print()
    print("Note: PDF versions are also available for high-quality printing")
