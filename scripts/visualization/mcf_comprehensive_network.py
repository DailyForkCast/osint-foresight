#!/usr/bin/env python3
"""
Comprehensive MCF Institutional Architecture Network
Implements Prompt 1: 6 different network layout variations with full entity set
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import json
import pandas as pd
import numpy as np

# Color palette from prompt
COLORS = {
    'military': '#1e3a5f',      # Navy blue
    'civilian': '#4682b4',       # Steel blue
    'party': '#8b0000',          # Deep red
    'dual_use': '#6b46c1',       # Purple
    'coordination': '#708090',   # Gray
    'soe': '#2f4f4f'            # Dark slate gray
}


def create_comprehensive_mcf_network():
    """
    Create the full MCF network with all entities from Prompt 1
    Returns NetworkX graph object
    """
    G = nx.DiGraph()

    # Central Leadership (Top Tier)
    central_leadership = {
        'Xi Jinping': {'type': 'party', 'tier': 1, 'power': 10},
        'Central MCF Commission': {'type': 'coordination', 'tier': 1, 'power': 9},
        'CCP Central Committee': {'type': 'party', 'tier': 1, 'power': 9},
        'Central Military Commission': {'type': 'military', 'tier': 1, 'power': 10}
    }

    # Military Institutions
    military = {
        'CMC S&T Commission': {'type': 'military', 'tier': 2, 'power': 7},
        'CMC Equipment Development': {'type': 'military', 'tier': 2, 'power': 7},
        'PLA Strategic Support Force': {'type': 'military', 'tier': 2, 'power': 8},
        'PLA Joint Logistics': {'type': 'military', 'tier': 3, 'power': 6},
        'Academy of Military Sciences': {'type': 'military', 'tier': 3, 'power': 6},
        'National Defense University': {'type': 'military', 'tier': 3, 'power': 5}
    }

    # State/Civilian Institutions
    civilian = {
        'State Council': {'type': 'civilian', 'tier': 1, 'power': 9},
        'MOST': {'type': 'civilian', 'tier': 2, 'power': 7},
        'MIIT': {'type': 'civilian', 'tier': 2, 'power': 8},
        'MOE': {'type': 'civilian', 'tier': 2, 'power': 6},
        'NDRC': {'type': 'civilian', 'tier': 2, 'power': 8},
        'MSS': {'type': 'dual_use', 'tier': 2, 'power': 8},
        'SASTIND': {'type': 'dual_use', 'tier': 2, 'power': 7}
    }

    # Party Organizations
    party_orgs = {
        'Organization Department': {'type': 'party', 'tier': 2, 'power': 7},
        'United Front Work': {'type': 'party', 'tier': 2, 'power': 6},
        'Propaganda Department': {'type': 'party', 'tier': 2, 'power': 6},
        'Discipline Inspection': {'type': 'party', 'tier': 2, 'power': 7}
    }

    # Implementation Bodies
    implementation = {
        'SASAC': {'type': 'civilian', 'tier': 3, 'power': 7},
        'CAS': {'type': 'dual_use', 'tier': 3, 'power': 8},
        'CAE': {'type': 'dual_use', 'tier': 3, 'power': 7},
        'CAST': {'type': 'civilian', 'tier': 3, 'power': 5},
        'NSFC': {'type': 'civilian', 'tier': 3, 'power': 6}
    }

    # State-Owned Enterprises
    soes = {
        'AVIC': {'type': 'soe', 'tier': 4, 'power': 7},
        'NORINCO': {'type': 'soe', 'tier': 4, 'power': 7},
        'CASC/CASIC': {'type': 'soe', 'tier': 4, 'power': 7},
        'CSSC/CSIC': {'type': 'soe', 'tier': 4, 'power': 6},
        'CNNC': {'type': 'soe', 'tier': 4, 'power': 7},
        'CETC': {'type': 'soe', 'tier': 4, 'power': 7}
    }

    # Add all nodes
    for entities in [central_leadership, military, civilian, party_orgs, implementation, soes]:
        for name, attrs in entities.items():
            G.add_node(name, **attrs)

    # Add edges with relationship types and weights
    edges = [
        # Central coordination
        ('Xi Jinping', 'Central MCF Commission', 10, 'authority'),
        ('Xi Jinping', 'CCP Central Committee', 10, 'authority'),
        ('Xi Jinping', 'Central Military Commission', 10, 'authority'),
        ('Central MCF Commission', 'State Council', 8, 'coordination'),
        ('Central MCF Commission', 'Central Military Commission', 8, 'coordination'),

        # Party control
        ('CCP Central Committee', 'Organization Department', 10, 'authority'),
        ('CCP Central Committee', 'United Front Work', 9, 'authority'),
        ('CCP Central Committee', 'Propaganda Department', 9, 'authority'),
        ('CCP Central Committee', 'Discipline Inspection', 10, 'authority'),

        # Military chain
        ('Central Military Commission', 'CMC S&T Commission', 10, 'authority'),
        ('Central Military Commission', 'CMC Equipment Development', 10, 'authority'),
        ('Central Military Commission', 'PLA Strategic Support Force', 10, 'authority'),
        ('CMC S&T Commission', 'Academy of Military Sciences', 8, 'guidance'),
        ('CMC Equipment Development', 'PLA Joint Logistics', 8, 'authority'),

        # Civilian chain
        ('State Council', 'MOST', 10, 'authority'),
        ('State Council', 'MIIT', 10, 'authority'),
        ('State Council', 'MOE', 10, 'authority'),
        ('State Council', 'NDRC', 10, 'authority'),
        ('State Council', 'SASAC', 10, 'authority'),

        # Dual-use bridges
        ('Central MCF Commission', 'SASTIND', 9, 'coordination'),
        ('Central MCF Commission', 'MSS', 8, 'coordination'),
        ('SASTIND', 'CMC Equipment Development', 7, 'coordination'),
        ('SASTIND', 'MIIT', 7, 'coordination'),

        # Implementation
        ('MOST', 'CAS', 9, 'authority'),
        ('MOST', 'CAE', 8, 'authority'),
        ('MOST', 'NSFC', 9, 'authority'),
        ('CMC S&T Commission', 'CAS', 7, 'guidance'),
        ('CMC S&T Commission', 'CAE', 7, 'guidance'),

        # SOEs
        ('SASAC', 'AVIC', 10, 'authority'),
        ('SASAC', 'NORINCO', 10, 'authority'),
        ('SASAC', 'CASC/CASIC', 10, 'authority'),
        ('SASAC', 'CSSC/CSIC', 10, 'authority'),
        ('SASAC', 'CNNC', 10, 'authority'),
        ('SASAC', 'CETC', 10, 'authority'),

        # Dual connections
        ('CMC Equipment Development', 'AVIC', 8, 'dual_use'),
        ('CMC Equipment Development', 'NORINCO', 8, 'dual_use'),
        ('CMC Equipment Development', 'CASC/CASIC', 9, 'dual_use'),
        ('MIIT', 'CETC', 7, 'guidance'),
        ('MSS', 'United Front Work', 6, 'information'),
        ('United Front Work', 'MOE', 5, 'guidance'),

        # Cross-institutional
        ('CAS', 'AVIC', 6, 'dual_use'),
        ('CAS', 'CASC/CASIC', 7, 'dual_use'),
        ('CAE', 'NORINCO', 6, 'dual_use'),
    ]

    for source, target, weight, rel_type in edges:
        G.add_edge(source, target, weight=weight, relationship=rel_type)

    return G


def save_network_statistics(G, output_dir):
    """Generate network statistics table"""
    stats = []

    # Degree centrality
    degree_cent = nx.degree_centrality(G)
    betweenness_cent = nx.betweenness_centrality(G)

    for node in G.nodes():
        stats.append({
            'Node': node,
            'Type': G.nodes[node]['type'],
            'Tier': G.nodes[node]['tier'],
            'Power Level': G.nodes[node]['power'],
            'Degree Centrality': round(degree_cent[node], 3),
            'Betweenness Centrality': round(betweenness_cent[node], 3),
            'In-Degree': G.in_degree(node),
            'Out-Degree': G.out_degree(node)
        })

    df = pd.DataFrame(stats)
    df = df.sort_values('Betweenness Centrality', ascending=False)

    csv_path = Path(output_dir) / 'mcf_network_statistics.csv'
    df.to_csv(csv_path, index=False)
    print(f"[SAVED] Statistics: {csv_path}")

    # Network-wide stats
    print(f"\nNetwork Statistics:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"  Density: {nx.density(G):.3f}")
    print(f"  Average Clustering: {nx.average_clustering(G.to_undirected()):.3f}")

    return df


def create_layout_variation_1_force_directed(G, output_dir="visualizations/comprehensive"):
    """Variation 1: Force-Directed Layout with Community Detection"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(24, 20), facecolor='#f8f9fa')

    # Spring layout
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

    # Node colors by type
    node_colors = [COLORS.get(G.nodes[node]['type'], '#808080') for node in G.nodes()]
    node_sizes = [G.nodes[node]['power'] * 500 for node in G.nodes()]

    # Edge colors by relationship
    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        rel_type = G[u][v]['relationship']
        weight = G[u][v]['weight']
        if rel_type == 'authority':
            edge_colors.append('#000000')
            edge_widths.append(weight / 2)
        elif rel_type == 'coordination':
            edge_colors.append('#6b46c1')
            edge_widths.append(weight / 2.5)
        elif rel_type == 'dual_use':
            edge_colors.append('#FF8C00')
            edge_widths.append(weight / 3)
        else:
            edge_colors.append('#CCCCCC')
            edge_widths.append(weight / 4)

    # Draw
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_widths,
                          alpha=0.6, arrows=True, arrowsize=20, connectionstyle='arc3,rad=0.1')

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes,
                          alpha=0.9, edgecolors='black', linewidths=2)

    # Labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=32, font_weight='bold')

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLORS['military'], label='Military'),
        mpatches.Patch(color=COLORS['civilian'], label='Civilian'),
        mpatches.Patch(color=COLORS['party'], label='Party'),
        mpatches.Patch(color=COLORS['dual_use'], label='Dual-Use'),
        mpatches.Patch(color=COLORS['coordination'], label='Coordination'),
        mpatches.Patch(color=COLORS['soe'], label='SOEs')
    ]

    ax.legend(handles=legend_elements, loc='upper left', fontsize=48, title='Node Types',
             title_fontsize=46, framealpha=0.95)

    ax.set_title("MCF Institutional Architecture - Force-Directed Layout",
                fontsize=44, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()

    # Save
    png_path = output_path / "mcf_network_force_directed.png"
    svg_path = output_path / "mcf_network_force_directed.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='#f8f9fa')
    plt.close()

    print(f"[SAVED] Variation 1: {png_path.name}")


def create_layout_variation_2_hierarchical(G, output_dir="visualizations/comprehensive"):
    """Variation 2: Hierarchical Tree"""
    import graphviz

    output_path = Path(output_dir)
    dot = graphviz.Digraph(name='MCF_Hierarchical', format='png', engine='dot')

    dot.attr(rankdir='TB', bgcolor='#f8f9fa', fontname='Arial', fontsize='28',
            nodesep='0.8', ranksep='1.2')

    dot.attr('node', shape='box', style='filled,rounded', fontname='Arial', fontsize='46')
    dot.attr('edge', color='#333333', penwidth='1.5')

    # Add nodes with colors
    for node in G.nodes():
        node_type = G.nodes[node]['type']
        color = COLORS.get(node_type, '#808080')

        # Shorten labels for readability
        label = node.replace(' Department', '').replace(' Commission', '')

        if G.nodes[node]['tier'] == 1:
            dot.node(node, label, fillcolor=color, fontcolor='white', fontsize='30', style='filled,rounded,bold')
        else:
            dot.node(node, label, fillcolor=color, fontcolor='white' if node_type in ['military', 'party'] else 'black')

    # Add edges
    for u, v in G.edges():
        rel_type = G[u][v]['relationship']
        if rel_type == 'authority':
            dot.edge(u, v, penwidth='2.5', color='#000000')
        elif rel_type == 'coordination':
            dot.edge(u, v, penwidth='2', color=COLORS['dual_use'], style='dashed')
        elif rel_type == 'dual_use':
            dot.edge(u, v, penwidth='1.5', color='#FF8C00')
        else:
            dot.edge(u, v, penwidth='1', color='#CCCCCC', style='dotted')

    # Save
    output_base = output_path / "mcf_network_hierarchical"
    dot.render(str(output_base), format='png', cleanup=True)
    dot.render(str(output_base), format='svg', cleanup=True)

    print(f"[SAVED] Variation 2: mcf_network_hierarchical.png")


def create_layout_variation_3_circular(G, output_dir="visualizations/comprehensive"):
    """Variation 3: Circular/Radial Layout - Xi/MCF at center, concentric rings by tier"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(26, 26), facecolor='#f8f9fa')

    # Manual circular positioning by tier
    pos = {}

    # Center: Xi and MCF Commission
    pos['Xi Jinping'] = (0, 0)
    pos['Central MCF Commission'] = (0.8, 0)

    # Tier 1 ring (radius 2.5)
    tier1_nodes = ['CCP Central Committee', 'Central Military Commission', 'State Council']
    angles_t1 = np.linspace(0, 2*np.pi, len(tier1_nodes), endpoint=False) + np.pi/6
    for i, node in enumerate(tier1_nodes):
        pos[node] = (2.5 * np.cos(angles_t1[i]), 2.5 * np.sin(angles_t1[i]))

    # Tier 2 - split by hemisphere
    # Military (left hemisphere, radius 4.5)
    military_t2 = ['CMC S&T Commission', 'CMC Equipment Development', 'PLA Strategic Support Force']
    angles_mil = np.linspace(np.pi/2, np.pi, len(military_t2))
    for i, node in enumerate(military_t2):
        pos[node] = (4.5 * np.cos(angles_mil[i]), 4.5 * np.sin(angles_mil[i]))

    # Civilian (right hemisphere, radius 4.5)
    civilian_t2 = ['MOST', 'MIIT', 'MOE', 'NDRC']
    angles_civ = np.linspace(0, np.pi/2, len(civilian_t2))
    for i, node in enumerate(civilian_t2):
        pos[node] = (4.5 * np.cos(angles_civ[i]), 4.5 * np.sin(angles_civ[i]))

    # Party orgs (top, radius 4.5)
    party_t2 = ['Organization Department', 'United Front Work', 'Propaganda Department', 'Discipline Inspection']
    angles_party = np.linspace(np.pi/2, 3*np.pi/2, len(party_t2))
    for i, node in enumerate(party_t2):
        pos[node] = (4.5 * np.cos(angles_party[i]), 4.5 * np.sin(angles_party[i]))

    # Dual-use (bottom, radius 4.5)
    dual_t2 = ['MSS', 'SASTIND']
    angles_dual = np.linspace(-np.pi/4, -3*np.pi/4, len(dual_t2))
    for i, node in enumerate(dual_t2):
        pos[node] = (4.5 * np.cos(angles_dual[i]), 4.5 * np.sin(angles_dual[i]))

    # Tier 3 (radius 6.5)
    tier3_nodes = ['PLA Joint Logistics', 'Academy of Military Sciences', 'National Defense University',
                   'SASAC', 'CAS', 'CAE', 'CAST', 'NSFC']
    angles_t3 = np.linspace(0, 2*np.pi, len(tier3_nodes), endpoint=False)
    for i, node in enumerate(tier3_nodes):
        pos[node] = (6.5 * np.cos(angles_t3[i]), 6.5 * np.sin(angles_t3[i]))

    # Tier 4 - SOEs (outer ring, radius 8.5)
    soe_nodes = ['AVIC', 'NORINCO', 'CASC/CASIC', 'CSSC/CSIC', 'CNNC', 'CETC']
    angles_soe = np.linspace(0, 2*np.pi, len(soe_nodes), endpoint=False)
    for i, node in enumerate(soe_nodes):
        pos[node] = (8.5 * np.cos(angles_soe[i]), 8.5 * np.sin(angles_soe[i]))

    # Node colors and sizes
    node_colors = [COLORS.get(G.nodes[node]['type'], '#808080') for node in G.nodes()]
    node_sizes = [G.nodes[node]['power'] * 600 for node in G.nodes()]

    # Edge colors
    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        rel_type = G[u][v]['relationship']
        weight = G[u][v]['weight']
        if rel_type == 'authority':
            edge_colors.append('#000000')
            edge_widths.append(weight / 2)
        elif rel_type == 'coordination':
            edge_colors.append('#6b46c1')
            edge_widths.append(weight / 2.5)
        elif rel_type == 'dual_use':
            edge_colors.append('#FF8C00')
            edge_widths.append(weight / 3)
        else:
            edge_colors.append('#CCCCCC')
            edge_widths.append(weight / 4)

    # Draw concentric circles to show tiers
    for radius, label in [(2.5, 'Tier 1'), (4.5, 'Tier 2'), (6.5, 'Tier 3'), (8.5, 'Tier 4')]:
        circle = plt.Circle((0, 0), radius, color='#E0E0E0', fill=False, linestyle='--', linewidth=1.5, alpha=0.5)
        ax.add_patch(circle)

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_widths,
                          alpha=0.5, arrows=True, arrowsize=20, connectionstyle='arc3,rad=0.1')

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes,
                          alpha=0.9, edgecolors='black', linewidths=2)

    # Labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=32, font_weight='bold')

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLORS['military'], label='Military'),
        mpatches.Patch(color=COLORS['civilian'], label='Civilian'),
        mpatches.Patch(color=COLORS['party'], label='Party'),
        mpatches.Patch(color=COLORS['dual_use'], label='Dual-Use'),
        mpatches.Patch(color=COLORS['coordination'], label='Coordination'),
        mpatches.Patch(color=COLORS['soe'], label='SOEs')
    ]

    ax.legend(handles=legend_elements, loc='upper right', fontsize=48, title='Node Types',
             title_fontsize=46, framealpha=0.95)

    ax.set_title("MCF Institutional Architecture - Circular/Radial Layout",
                fontsize=44, fontweight='bold', pad=20)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.axis('off')
    plt.tight_layout()

    # Save
    png_path = output_path / "mcf_network_circular.png"
    svg_path = output_path / "mcf_network_circular.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='#f8f9fa')
    plt.close()

    print(f"[SAVED] Variation 3: {png_path.name}")


def create_layout_variation_4_bipartite(G, output_dir="visualizations/comprehensive"):
    """Variation 4: Bipartite Layout - Military left, Civilian right, Dual-use center"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(28, 20), facecolor='#f8f9fa')

    # Categorize nodes
    military_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'military']
    civilian_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'civilian']
    party_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'party']
    dual_use_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'dual_use']
    coordination_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'coordination']
    soe_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'soe']

    pos = {}

    # Left column: Military (x = -4)
    y_pos = np.linspace(8, 1, len(military_nodes))
    for i, node in enumerate(military_nodes):
        pos[node] = (-4, y_pos[i])

    # Center-left: Party (x = -2)
    y_pos_party = np.linspace(8, 3, len(party_nodes))
    for i, node in enumerate(party_nodes):
        pos[node] = (-2, y_pos_party[i])

    # Center: Dual-use and coordination (x = 0)
    center_nodes = dual_use_nodes + coordination_nodes
    y_pos_center = np.linspace(8, 2, len(center_nodes))
    for i, node in enumerate(center_nodes):
        pos[node] = (0, y_pos_center[i])

    # Center-right: Civilian (x = 2)
    y_pos_civ = np.linspace(8, 1, len(civilian_nodes))
    for i, node in enumerate(civilian_nodes):
        pos[node] = (2, y_pos_civ[i])

    # Right column: SOEs (x = 4)
    y_pos_soe = np.linspace(6, 1, len(soe_nodes))
    for i, node in enumerate(soe_nodes):
        pos[node] = (4, y_pos_soe[i])

    # Place Xi at top center
    if 'Xi Jinping' in pos:
        pos['Xi Jinping'] = (0, 10)

    # Node colors and sizes
    node_colors = [COLORS.get(G.nodes[node]['type'], '#808080') for node in G.nodes()]
    node_sizes = [G.nodes[node]['power'] * 500 for node in G.nodes()]

    # Edge colors
    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        rel_type = G[u][v]['relationship']
        weight = G[u][v]['weight']
        if rel_type == 'authority':
            edge_colors.append('#000000')
            edge_widths.append(weight / 2.5)
        elif rel_type == 'coordination':
            edge_colors.append('#6b46c1')
            edge_widths.append(weight / 3)
        elif rel_type == 'dual_use':
            edge_colors.append('#FF8C00')
            edge_widths.append(weight / 3.5)
        else:
            edge_colors.append('#CCCCCC')
            edge_widths.append(weight / 4)

    # Draw background zones
    military_zone = plt.Rectangle((-5, 0), 2, 10, color='#E3F2FD', alpha=0.2, zorder=0)
    dual_use_zone = plt.Rectangle((-1, 0), 2, 10, color='#F3E5F5', alpha=0.2, zorder=0)
    civilian_zone = plt.Rectangle((1, 0), 2, 10, color='#E8F5E9', alpha=0.2, zorder=0)
    ax.add_patch(military_zone)
    ax.add_patch(dual_use_zone)
    ax.add_patch(civilian_zone)

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_widths,
                          alpha=0.5, arrows=True, arrowsize=18, connectionstyle='arc3,rad=0.15')

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes,
                          alpha=0.9, edgecolors='black', linewidths=2)

    # Labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=32, font_weight='bold')

    # Add zone labels
    ax.text(-4, 10.5, 'MILITARY', fontsize=46, fontweight='bold', ha='center', color=COLORS['military'])
    ax.text(-2, 10.5, 'PARTY', fontsize=46, fontweight='bold', ha='center', color=COLORS['party'])
    ax.text(0, 10.5, 'DUAL-USE', fontsize=46, fontweight='bold', ha='center', color=COLORS['dual_use'])
    ax.text(2, 10.5, 'CIVILIAN', fontsize=46, fontweight='bold', ha='center', color=COLORS['civilian'])
    ax.text(4, 10.5, 'SOEs', fontsize=46, fontweight='bold', ha='center', color=COLORS['soe'])

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLORS['military'], label='Military'),
        mpatches.Patch(color=COLORS['civilian'], label='Civilian'),
        mpatches.Patch(color=COLORS['party'], label='Party'),
        mpatches.Patch(color=COLORS['dual_use'], label='Dual-Use'),
        mpatches.Patch(color=COLORS['coordination'], label='Coordination'),
        mpatches.Patch(color=COLORS['soe'], label='SOEs')
    ]

    ax.legend(handles=legend_elements, loc='lower right', fontsize=48, title='Node Types',
             title_fontsize=46, framealpha=0.95)

    ax.set_title("MCF Institutional Architecture - Bipartite Layout (Military-Civilian Divide)",
                fontsize=44, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()

    # Save
    png_path = output_path / "mcf_network_bipartite.png"
    svg_path = output_path / "mcf_network_bipartite.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='#f8f9fa')
    plt.close()

    print(f"[SAVED] Variation 4: {png_path.name}")


def create_layout_variation_5_subgraphs(G, output_dir="visualizations/comprehensive"):
    """Variation 5: Spring Layout with Visible Subgraph Boundaries"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(26, 22), facecolor='#f8f9fa')

    # Create subgraphs
    military_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'military']
    civilian_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'civilian']
    party_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'party']
    dual_use_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'dual_use']
    coordination_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'coordination']
    soe_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'soe']

    # Create subgraph positions using spring layout with fixed centers
    pos = {}

    # Position each subgraph in different quadrants
    subgraph_centers = {
        'military': (-3, 3),
        'civilian': (3, 3),
        'party': (-3, -3),
        'soe': (3, -3),
        'dual_use': (0, 0),
        'coordination': (0, 5)
    }

    # Generate positions for each subgraph
    for node_type, center in subgraph_centers.items():
        if node_type == 'military':
            nodes = military_nodes
        elif node_type == 'civilian':
            nodes = civilian_nodes
        elif node_type == 'party':
            nodes = party_nodes
        elif node_type == 'soe':
            nodes = soe_nodes
        elif node_type == 'dual_use':
            nodes = dual_use_nodes
        else:
            nodes = coordination_nodes

        if nodes:
            # Create subgraph
            subG = G.subgraph(nodes)
            # Spring layout for this subgraph
            sub_pos = nx.spring_layout(subG, k=1.5, iterations=30, seed=42)
            # Translate to center position
            for node in sub_pos:
                pos[node] = (sub_pos[node][0] * 1.5 + center[0],
                           sub_pos[node][1] * 1.5 + center[1])

    # Node colors and sizes
    node_colors = [COLORS.get(G.nodes[node]['type'], '#808080') for node in G.nodes()]
    node_sizes = [G.nodes[node]['power'] * 500 for node in G.nodes()]

    # Edge colors
    edge_colors = []
    edge_widths = []
    edge_styles = []
    for u, v in G.edges():
        rel_type = G[u][v]['relationship']
        weight = G[u][v]['weight']

        # Check if edge crosses subgraph boundaries
        u_type = G.nodes[u]['type']
        v_type = G.nodes[v]['type']
        crosses_boundary = (u_type != v_type)

        if rel_type == 'authority':
            edge_colors.append('#000000')
            edge_widths.append(weight / 2)
        elif rel_type == 'coordination':
            edge_colors.append('#6b46c1')
            edge_widths.append(weight / 2.5)
        elif rel_type == 'dual_use':
            edge_colors.append('#FF8C00')
            edge_widths.append(weight / 3)
        else:
            edge_colors.append('#CCCCCC')
            edge_widths.append(weight / 4)

        edge_styles.append('dashed' if crosses_boundary else 'solid')

    # Draw subgraph boundaries (convex hulls)
    from matplotlib.patches import Polygon

    for node_type, center in subgraph_centers.items():
        if node_type == 'military':
            nodes = military_nodes
            color = COLORS['military']
        elif node_type == 'civilian':
            nodes = civilian_nodes
            color = COLORS['civilian']
        elif node_type == 'party':
            nodes = party_nodes
            color = COLORS['party']
        elif node_type == 'soe':
            nodes = soe_nodes
            color = COLORS['soe']
        elif node_type == 'dual_use':
            nodes = dual_use_nodes
            color = COLORS['dual_use']
        else:
            nodes = coordination_nodes
            color = COLORS['coordination']

        if nodes and len(nodes) > 2:
            # Get positions for nodes in this subgraph
            points = np.array([pos[n] for n in nodes])

            # Create convex hull
            from scipy.spatial import ConvexHull
            try:
                hull = ConvexHull(points)
                # Expand hull slightly
                center_pt = points.mean(axis=0)
                hull_points = points[hull.vertices]
                expanded = center_pt + (hull_points - center_pt) * 1.3

                polygon = Polygon(expanded, fill=True, alpha=0.15,
                                edgecolor=color, facecolor=color, linewidth=2.5)
                ax.add_patch(polygon)
            except:
                pass  # Skip if convex hull fails

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_widths,
                          alpha=0.6, arrows=True, arrowsize=18, connectionstyle='arc3,rad=0.1')

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes,
                          alpha=0.9, edgecolors='black', linewidths=2)

    # Labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=32, font_weight='bold')

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLORS['military'], label='Military System'),
        mpatches.Patch(color=COLORS['civilian'], label='Civilian System'),
        mpatches.Patch(color=COLORS['party'], label='Party System'),
        mpatches.Patch(color=COLORS['dual_use'], label='Dual-Use'),
        mpatches.Patch(color=COLORS['coordination'], label='Coordination'),
        mpatches.Patch(color=COLORS['soe'], label='Defense Industrial')
    ]

    ax.legend(handles=legend_elements, loc='upper left', fontsize=48, title='Institutional Systems',
             title_fontsize=46, framealpha=0.95)

    ax.set_title("MCF Institutional Architecture - Systems View with Boundaries",
                fontsize=44, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()

    # Save
    png_path = output_path / "mcf_network_subgraphs.png"
    svg_path = output_path / "mcf_network_subgraphs.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='#f8f9fa')
    plt.close()

    print(f"[SAVED] Variation 5: {png_path.name}")


def create_layout_variation_6_kamada_kawai_ego(G, output_dir="visualizations/comprehensive",
                                                ego_node='Central MCF Commission'):
    """Variation 6: Kamada-Kawai Layout with Ego Network Highlighting"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(24, 20), facecolor='#f8f9fa')

    # Kamada-Kawai layout
    pos = nx.kamada_kawai_layout(G)

    # Get ego network (nodes connected to ego_node)
    ego_neighbors = set(G.successors(ego_node)) | set(G.predecessors(ego_node))
    ego_network = {ego_node} | ego_neighbors

    # Node colors - highlight ego network
    node_colors = []
    for node in G.nodes():
        if node == ego_node:
            node_colors.append('#FF0000')  # Ego node in red
        elif node in ego_network:
            # Brighten the color for ego network
            base_color = COLORS.get(G.nodes[node]['type'], '#808080')
            node_colors.append(base_color)
        else:
            # Dim non-ego network nodes
            node_colors.append('#D0D0D0')

    # Node sizes - larger for ego network
    node_sizes = []
    for node in G.nodes():
        base_size = G.nodes[node]['power'] * 500
        if node == ego_node:
            node_sizes.append(base_size * 1.5)
        elif node in ego_network:
            node_sizes.append(base_size * 1.2)
        else:
            node_sizes.append(base_size * 0.6)

    # Edge highlighting
    edge_colors = []
    edge_widths = []
    edge_alphas = []

    for u, v in G.edges():
        rel_type = G[u][v]['relationship']
        weight = G[u][v]['weight']

        # Check if edge involves ego node
        involves_ego = (u == ego_node or v == ego_node)
        in_ego_network = (u in ego_network and v in ego_network)

        if rel_type == 'authority':
            color = '#000000'
            width = weight / 2
        elif rel_type == 'coordination':
            color = '#6b46c1'
            width = weight / 2.5
        elif rel_type == 'dual_use':
            color = '#FF8C00'
            width = weight / 3
        else:
            color = '#CCCCCC'
            width = weight / 4

        if involves_ego:
            edge_colors.append(color)
            edge_widths.append(width * 1.5)
            edge_alphas.append(0.9)
        elif in_ego_network:
            edge_colors.append(color)
            edge_widths.append(width)
            edge_alphas.append(0.7)
        else:
            edge_colors.append('#E0E0E0')
            edge_widths.append(width * 0.5)
            edge_alphas.append(0.3)

    # Draw non-ego edges first (background)
    non_ego_edges = [(u, v) for u, v in G.edges()
                     if u not in ego_network and v not in ego_network]
    if non_ego_edges:
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=non_ego_edges,
                              edge_color='#E0E0E0', width=0.5, alpha=0.3,
                              arrows=True, arrowsize=10)

    # Draw ego network edges (foreground)
    ego_edges = [(u, v) for u, v in G.edges()
                 if u in ego_network or v in ego_network]
    if ego_edges:
        ego_edge_colors = []
        ego_edge_widths = []
        for u, v in ego_edges:
            rel_type = G[u][v]['relationship']
            weight = G[u][v]['weight']
            involves_ego = (u == ego_node or v == ego_node)

            if rel_type == 'authority':
                color = '#000000'
                width = weight / 2
            elif rel_type == 'coordination':
                color = '#6b46c1'
                width = weight / 2.5
            elif rel_type == 'dual_use':
                color = '#FF8C00'
                width = weight / 3
            else:
                color = '#CCCCCC'
                width = weight / 4

            ego_edge_colors.append(color)
            ego_edge_widths.append(width * (1.5 if involves_ego else 1.0))

        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=ego_edges,
                              edge_color=ego_edge_colors, width=ego_edge_widths,
                              alpha=0.7, arrows=True, arrowsize=20,
                              connectionstyle='arc3,rad=0.1')

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=node_sizes,
                          alpha=0.9, edgecolors='black', linewidths=2)

    # Labels - only for ego network
    ego_labels = {n: n for n in ego_network}
    nx.draw_networkx_labels(G, pos, labels=ego_labels, ax=ax,
                           font_size=32, font_weight='bold')

    # Legend
    legend_elements = [
        mpatches.Patch(color='#FF0000', label=f'Ego Node: {ego_node}'),
        mpatches.Patch(color='#808080', label='Direct Connections'),
        mpatches.Patch(color='#D0D0D0', label='Other Nodes'),
        plt.Line2D([0], [0], color='#000000', linewidth=3, label='Authority Relationship'),
        plt.Line2D([0], [0], color='#6b46c1', linewidth=3, label='Coordination'),
        plt.Line2D([0], [0], color='#FF8C00', linewidth=3, label='Dual-Use')
    ]

    ax.legend(handles=legend_elements, loc='upper right', fontsize=48,
             title='Ego Network Analysis', title_fontsize=46, framealpha=0.95)

    ax.set_title(f"MCF Institutional Architecture - Ego Network: {ego_node}",
                fontsize=44, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()

    # Save
    png_path = output_path / "mcf_network_ego_kamada_kawai.png"
    svg_path = output_path / "mcf_network_ego_kamada_kawai.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='#f8f9fa')
    plt.close()

    print(f"[SAVED] Variation 6: {png_path.name}")


# Main execution
if __name__ == "__main__":
    print("=" * 80)
    print("CREATING COMPREHENSIVE MCF NETWORK VISUALIZATIONS")
    print("=" * 80)
    print()

    # Create network
    print("Building comprehensive MCF network...")
    G = create_comprehensive_mcf_network()
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print()

    output_dir = "visualizations/comprehensive"

    # Generate statistics
    print("Generating network statistics...")
    save_network_statistics(G, output_dir)
    print()

    # Save network data as JSON
    data = nx.node_link_data(G)
    json_path = Path(output_dir) / "mcf_network_data.json"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[SAVED] Network data: {json_path}")
    print()

    # Create all 6 variations
    print("Creating Variation 1: Force-Directed Layout...")
    create_layout_variation_1_force_directed(G, output_dir)
    print()

    print("Creating Variation 2: Hierarchical Tree...")
    create_layout_variation_2_hierarchical(G, output_dir)
    print()

    print("Creating Variation 3: Circular/Radial Layout...")
    create_layout_variation_3_circular(G, output_dir)
    print()

    print("Creating Variation 4: Bipartite Layout (Military-Civilian Divide)...")
    create_layout_variation_4_bipartite(G, output_dir)
    print()

    print("Creating Variation 5: Systems View with Subgraph Boundaries...")
    create_layout_variation_5_subgraphs(G, output_dir)
    print()

    print("Creating Variation 6: Ego Network Analysis (Kamada-Kawai)...")
    create_layout_variation_6_kamada_kawai_ego(G, output_dir, ego_node='Central MCF Commission')
    print()

    print("=" * 80)
    print("PROMPT 1 COMPLETE: ALL 6 NETWORK VARIATIONS CREATED")
    print("=" * 80)
    print("\nVariations Created:")
    print("  1. Force-Directed Layout - Power-based node sizing")
    print("  2. Hierarchical Tree - Top-down authority structure")
    print("  3. Circular/Radial - Concentric rings by tier")
    print("  4. Bipartite - Military left, Civilian right, Dual-use center")
    print("  5. Systems View - Visible institutional boundaries")
    print("  6. Ego Network - Highlighting Central MCF Commission connections")
    print("\nTotal files created: 12 PNG/SVG + 1 CSV + 1 JSON")
