#!/usr/bin/env python3
"""
Create Multiple Style Variations of MCF Visualizations
Generates different visual styles with larger fonts for comparison
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import graphviz
from pathlib import Path

from mcf_network_data import (
    get_all_nodes, get_all_edges, COLOR_SCHEMES, TECHNOLOGY_FLOWS
)


# ENHANCED COLOR SCHEMES
COLOR_SCHEMES_ENHANCED = {
    'default': COLOR_SCHEMES,

    'professional': {
        'institutional_architecture': {
            'central_authority': '#2C3E50',  # Dark blue-gray
            'ministry': '#3498DB',  # Bright blue
            'commission': '#9B59B6',  # Purple
            'agency': '#16A085',  # Teal
            'research_institution': '#E67E22',  # Orange
            'military': '#C0392B',  # Dark red
            'provincial': '#7F8C8D',  # Gray
            'implementation': '#27AE60'  # Green
        },
        'relationship_types': {
            'coordinates': '#E74C3C',
            'directs': '#3498DB',
            'commands': '#8E44AD',
            'funds': '#F39C12',
            'controls': '#C0392B',
            'oversees': '#16A085',
            'guides': '#2980B9',
            'collaborates': '#27AE60',
            'procures_from': '#D35400'
        }
    },

    'high_contrast': {
        'institutional_architecture': {
            'central_authority': '#FF0000',  # Red
            'ministry': '#0000FF',  # Blue
            'commission': '#FF00FF',  # Magenta
            'agency': '#00FFFF',  # Cyan
            'research_institution': '#FF8000',  # Orange
            'military': '#800000',  # Maroon
            'provincial': '#808080',  # Gray
            'implementation': '#00FF00'  # Green
        },
        'relationship_types': {
            'coordinates': '#FF0000',
            'directs': '#0000FF',
            'commands': '#800080',
            'funds': '#FFA500',
            'controls': '#8B0000',
            'oversees': '#008080',
            'guides': '#000080',
            'collaborates': '#008000',
            'procures_from': '#FF4500'
        }
    },

    'pastel': {
        'institutional_architecture': {
            'central_authority': '#FADBD8',  # Light red
            'ministry': '#D6EAF8',  # Light blue
            'commission': '#E8DAEF',  # Light purple
            'agency': '#D1F2EB',  # Light teal
            'research_institution': '#FDEBD0',  # Light orange
            'military': '#F5B7B1',  # Light red
            'provincial': '#D5D8DC',  # Light gray
            'implementation': '#D5F4E6'  # Light green
        },
        'relationship_types': {
            'coordinates': '#EC7063',
            'directs': '#5DADE2',
            'commands': '#AF7AC5',
            'funds': '#F8C471',
            'controls': '#E74C3C',
            'oversees': '#48C9B0',
            'guides': '#5499C7',
            'collaborates': '#52BE80',
            'procures_from': '#E59866'
        }
    }
}


def create_networkx_style_variation(style_name='default', output_dir="visualizations/styles"):
    """Create NetworkX network graph with specified style"""
    output_path = Path(output_dir) / style_name
    output_path.mkdir(parents=True, exist_ok=True)

    G = nx.DiGraph()
    nodes = get_all_nodes()
    edges = get_all_edges()

    for node in nodes:
        G.add_node(node['id'], **node)

    for edge in edges:
        G.add_edge(edge['from'], edge['to'], weight=edge['weight'],
                   edge_type=edge['type'], description=edge.get('description', ''))

    # Create figure
    fig, ax = plt.subplots(figsize=(24, 18), facecolor='white')

    # Position nodes by tier
    pos = {}
    tier_groups = {}
    for node_id, node_data in G.nodes(data=True):
        tier = node_data.get('tier', 5)
        if tier not in tier_groups:
            tier_groups[tier] = []
        tier_groups[tier].append(node_id)

    y_positions = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}
    for tier, node_list in tier_groups.items():
        y = y_positions.get(tier, 0)
        num_nodes = len(node_list)
        x_positions = [(i - num_nodes/2) * 2.5 for i in range(num_nodes)]
        for i, node_id in enumerate(node_list):
            pos[node_id] = (x_positions[i], y)

    # Get colors from scheme
    colors = COLOR_SCHEMES_ENHANCED[style_name]['institutional_architecture']
    node_colors = [colors.get(G.nodes[node]['type'], '#95A5A6') for node in G.nodes()]
    node_sizes = [G.nodes[node].get('power_level', 5) * 400 for node in G.nodes()]

    edge_color_scheme = COLOR_SCHEMES_ENHANCED[style_name]['relationship_types']
    edge_colors = [edge_color_scheme.get(G[u][v]['edge_type'], '#95A5A6') for u, v in G.edges()]
    edge_weights = [G[u][v]['weight'] / 1.5 for u, v in G.edges()]

    # Draw
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_weights,
                          alpha=0.7, arrows=True, arrowsize=25, arrowstyle='->',
                          connectionstyle='arc3,rad=0.1', node_size=node_sizes)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes,
                          alpha=0.9, edgecolors='black', linewidths=2.5)

    # Labels with larger font
    labels = {}
    for node in G.nodes():
        label = G.nodes[node].get('label', node)
        if len(label) > 25:
            words = label.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 20:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            label = '\n'.join(lines)
        labels[node] = label

    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax,
                           font_size=14, font_weight='bold', font_family='sans-serif')

    # Legend
    legend_elements_nodes = [
        mpatches.Patch(color=color, label=node_type.replace('_', ' ').title())
        for node_type, color in colors.items()
    ]

    legend1 = ax.legend(handles=legend_elements_nodes, loc='upper left',
                       title='Node Types', fontsize=14, title_fontsize=16, framealpha=0.9)
    ax.add_artist(legend1)

    legend_elements_edges = [
        mpatches.Patch(color=color, label=rel_type.replace('_', ' ').title())
        for rel_type, color in edge_color_scheme.items()
    ]
    ax.legend(handles=legend_elements_edges, loc='upper right',
             title='Relationship Types', fontsize=14, title_fontsize=16, framealpha=0.9)

    ax.set_title(f"MCF Institutional Architecture - {style_name.title()} Style",
                fontsize=24, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()

    # Save
    png_path = output_path / f"mcf_network_{style_name}.png"
    svg_path = output_path / f"mcf_network_{style_name}.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"[SAVED] {style_name}: {png_path.name}")
    return str(png_path), str(svg_path)


def create_sankey_style_variation(style_name='default', output_dir="visualizations/styles"):
    """Create Sankey diagram with specified style"""
    output_path = Path(output_dir) / style_name
    output_path.mkdir(parents=True, exist_ok=True)

    # Build node list
    nodes = set()
    for flow in TECHNOLOGY_FLOWS:
        nodes.add(flow['source'])
        nodes.add(flow['target'])

    node_list = sorted(list(nodes))
    node_index = {node: i for i, node in enumerate(node_list)}

    source_indices = [node_index[flow['source']] for flow in TECHNOLOGY_FLOWS]
    target_indices = [node_index[flow['target']] for flow in TECHNOLOGY_FLOWS]
    values = [flow['value'] for flow in TECHNOLOGY_FLOWS]

    # Color schemes by style
    if style_name == 'high_contrast':
        colors = ['#FF6B6B' if 'Foreign' in flow['source'] else
                 '#4ECDC4' if flow['target'] in ['Chinese Academy of Sciences', 'University Defense Labs', 'State-Owned Enterprises'] else
                 '#95E1D3' for flow in TECHNOLOGY_FLOWS]
        node_colors = ['#FF0000' if 'Foreign' in node else
                      '#0000FF' if node in ['Chinese Academy of Sciences', 'University Defense Labs', 'State-Owned Enterprises', 'Talent Recruitment Programs'] else
                      '#FF8000' if node in ['PLA Strategic Support Force', 'State Administration for Science, Technology and Industry for National Defense'] else
                      '#00FF00' for node in node_list]
    elif style_name == 'pastel':
        colors = ['rgba(252, 207, 207, 0.5)' if 'Foreign' in flow['source'] else
                 'rgba(207, 226, 243, 0.5)' if flow['target'] in ['Chinese Academy of Sciences', 'University Defense Labs', 'State-Owned Enterprises'] else
                 'rgba(213, 244, 230, 0.5)' for flow in TECHNOLOGY_FLOWS]
        node_colors = ['#FADBD8' if 'Foreign' in node else
                      '#D6EAF8' if node in ['Chinese Academy of Sciences', 'University Defense Labs', 'State-Owned Enterprises', 'Talent Recruitment Programs'] else
                      '#FDEBD0' if node in ['PLA Strategic Support Force', 'State Administration for Science, Technology and Industry for National Defense'] else
                      '#D5F4E6' for node in node_list]
    else:  # default
        colors = [flow.get('color', '#95A5A6') for flow in TECHNOLOGY_FLOWS]
        node_colors = ['#E74C3C' if 'Foreign' in node else
                      '#3498DB' if node in ['Chinese Academy of Sciences', 'University Defense Labs', 'State-Owned Enterprises', 'Talent Recruitment Programs'] else
                      '#E67E22' if node in ['PLA Strategic Support Force', 'State Administration for Science, Technology and Industry for National Defense'] else
                      '#27AE60' for node in node_list]

    fig = go.Figure(data=[go.Sankey(
        node=dict(pad=20, thickness=25, line=dict(color="black", width=1),
                 label=node_list, color=node_colors),
        link=dict(source=source_indices, target=target_indices, value=values, color=colors)
    )])

    fig.update_layout(
        title={'text': f"MCF Technology Flow - {style_name.title()} Style",
               'font': {'size': 26, 'family': 'Arial, sans-serif', 'color': '#2C3E50'},
               'x': 0.5, 'xanchor': 'center'},
        font=dict(size=22, family='Arial, sans-serif'),
        plot_bgcolor='white', paper_bgcolor='white',
        width=1600, height=900
    )

    html_path = output_path / f"mcf_sankey_{style_name}.html"
    png_path = output_path / f"mcf_sankey_{style_name}.png"
    svg_path = output_path / f"mcf_sankey_{style_name}.svg"

    fig.write_html(str(html_path))
    try:
        fig.write_image(str(png_path), width=1600, height=900, scale=2)
        fig.write_image(str(svg_path), width=1600, height=900, format='svg')
    except Exception as e:
        print(f"  [NOTE] PNG/SVG export failed for {style_name}, HTML saved")

    print(f"[SAVED] {style_name}: {html_path.name}")
    return str(html_path)


def create_graphviz_style_variation(style_name='default', output_dir="visualizations/styles"):
    """Create Graphviz hierarchy with specified style"""
    output_path = Path(output_dir) / style_name
    output_path.mkdir(parents=True, exist_ok=True)

    dot = graphviz.Digraph(name=f'MCF_Hierarchy_{style_name}', format='png', engine='dot')

    # Graph attributes
    dot.attr(rankdir='TB', bgcolor='white', fontname='Arial', fontsize='16',
            splines='ortho', nodesep='0.6', ranksep='1.0')

    dot.attr('node', shape='box', style='filled,rounded', fontname='Arial',
            fontsize='16', fontcolor='#2C3E50', margin='0.4,0.3')

    dot.attr('edge', color='#34495E', penwidth='2.5', arrowsize='1.0')

    # Color scheme selection
    if style_name == 'high_contrast':
        colors = {'central': '#FF0000', 'state': '#0000FF', 'military': '#FF8000',
                 'ministry': '#00FFFF', 'commission': '#FF00FF', 'intelligence': '#800080',
                 'military_agency': '#8B0000', 'research': '#FFA500', 'soe': '#00FF00', 'university': '#008080'}
    elif style_name == 'pastel':
        colors = {'central': '#FADBD8', 'state': '#D6EAF8', 'military': '#FDEBD0',
                 'ministry': '#D1F2EB', 'commission': '#E8DAEF', 'intelligence': '#E8DAEF',
                 'military_agency': '#F5B7B1', 'research': '#FDEBD0', 'soe': '#D5F4E6', 'university': '#D1F2EB'}
    else:  # professional/default
        colors = {'central': '#E74C3C', 'state': '#3498DB', 'military': '#E67E22',
                 'ministry': '#3498DB', 'commission': '#9B59B6', 'intelligence': '#8E44AD',
                 'military_agency': '#D35400', 'research': '#F39C12', 'soe': '#27AE60', 'university': '#16A085'}

    # Nodes
    dot.node('xi', 'Xi Jinping\nGeneral Secretary, President, CMC Chair',
            fillcolor=colors['central'], fontcolor='white', fontsize='18', style='filled,rounded,bold')

    dot.node('mcf_commission', 'Central MCF Commission\n(Chair: Xi Jinping)',
            fillcolor=colors['central'], fontcolor='white', fontsize='16')

    dot.node('state_council', 'State Council\n(Government Executive)',
            fillcolor=colors['state'], fontcolor='white', fontsize='16')

    dot.node('cmc', 'Central Military Commission\n(Chair: Xi Jinping)',
            fillcolor=colors['military'], fontcolor='white', fontsize='16')

    # Ministries
    dot.node('miit', 'MIIT\nIndustrial Technology', fillcolor=colors['ministry'], fontcolor='white', fontsize='14')
    dot.node('most', 'MOST\nResearch Coordination', fillcolor=colors['ministry'], fontcolor='white', fontsize='14')
    dot.node('moe', 'MOE\nTalent Pipeline', fillcolor=colors['ministry'], fontcolor='white', fontsize='14')
    dot.node('ndrc', 'NDRC\nStrategic Planning', fillcolor=colors['commission'], fontcolor='white', fontsize='14')
    dot.node('sasac', 'SASAC\nSOE Oversight', fillcolor=colors['commission'], fontcolor='white', fontsize='14')
    dot.node('mss', 'Ministry of State Security\nIntelligence Collection',
            fillcolor=colors['intelligence'], fontcolor='white', fontsize='14')

    # Military/defense
    dot.node('pla_ssf', 'PLA Strategic Support Force\nCyber, Space, EW',
            fillcolor=colors['military_agency'], fontcolor='white', fontsize='14')
    dot.node('sastind', 'SASTIND\nDefense Technology',
            fillcolor=colors['military_agency'], fontcolor='white', fontsize='14')

    # Research and implementation
    dot.node('cas', 'Chinese Academy\nof Sciences', fillcolor=colors['research'], fontsize='14')
    dot.node('soes', 'State-Owned\nEnterprises\n(AVIC, NORINCO, CETC)',
            fillcolor=colors['soe'], fontcolor='white', fontsize='14')
    dot.node('university_labs', 'University Defense Labs\n(Tsinghua, Beihang, NUDT)',
            fillcolor=colors['university'], fontsize='14')

    # Edges
    dot.edge('xi', 'mcf_commission', label='Chairs', fontsize='12')
    dot.edge('mcf_commission', 'state_council', label='Coordinates', fontsize='12')
    dot.edge('mcf_commission', 'cmc', label='Coordinates', fontsize='12')
    dot.edge('state_council', 'miit', fontsize='11')
    dot.edge('state_council', 'most', fontsize='11')
    dot.edge('state_council', 'moe', fontsize='11')
    dot.edge('state_council', 'ndrc', fontsize='11')
    dot.edge('state_council', 'sasac', fontsize='11')
    dot.edge('mcf_commission', 'mss', label='Directs', fontsize='11')
    dot.edge('cmc', 'pla_ssf', fontsize='11')
    dot.edge('cmc', 'sastind', fontsize='11')
    dot.edge('most', 'cas', fontsize='10')
    dot.edge('sasac', 'soes', fontsize='10')
    dot.edge('moe', 'university_labs', fontsize='10')

    # Cross-connections
    dot.edge('cas', 'soes', label='Tech Transfer', style='dashed', color='#95A5A6', fontsize='10')
    dot.edge('university_labs', 'pla_ssf', label='Research', style='dashed', color='#95A5A6', fontsize='10')
    dot.edge('soes', 'pla_ssf', label='Procurement', style='dashed', color='#95A5A6', fontsize='10')

    # Save
    output_base = output_path / f"mcf_hierarchy_{style_name}"
    dot.render(str(output_base), format='png', cleanup=True)
    dot.render(str(output_base), format='svg', cleanup=True)
    dot.save(str(output_base) + '.gv')

    print(f"[SAVED] {style_name}: {output_base.name}.png")
    return str(output_base) + '.png'


if __name__ == "__main__":
    print("=" * 80)
    print("CREATING MCF STYLE VARIATIONS")
    print("=" * 80)
    print()

    styles = ['default', 'professional', 'high_contrast', 'pastel']

    for style in styles:
        print(f"\n{'='*80}")
        print(f"Style: {style.upper()}")
        print('='*80)

        print("\nNetworkX Network Graph...")
        create_networkx_style_variation(style)

        print("\nPlotly Sankey Diagram...")
        create_sankey_style_variation(style)

        print("\nGraphviz Hierarchy Tree...")
        create_graphviz_style_variation(style)

    print("\n" + "=" * 80)
    print("COMPLETE - All style variations created")
    print("=" * 80)
    print("\nLocations:")
    print("  visualizations/styles/default/")
    print("  visualizations/styles/professional/")
    print("  visualizations/styles/high_contrast/")
    print("  visualizations/styles/pastel/")
