#!/usr/bin/env python3
"""
MCF NetworkX Visualization
Creates institutional architecture network graph using NetworkX
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import sys

# Import our data
from mcf_network_data import (
    get_all_nodes, get_all_edges, COLOR_SCHEMES
)

def create_mcf_network_graph(output_dir="visualizations", dpi=300):
    """
    Create MCF institutional architecture network graph

    Args:
        output_dir: Directory for output files
        dpi: Resolution for PNG output
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create directed graph
    G = nx.DiGraph()

    # Get data
    nodes = get_all_nodes()
    edges = get_all_edges()

    # Add nodes
    for node in nodes:
        G.add_node(
            node['id'],
            **node
        )

    # Add edges
    for edge in edges:
        G.add_edge(
            edge['from'],
            edge['to'],
            weight=edge['weight'],
            edge_type=edge['type'],
            description=edge.get('description', '')
        )

    print(f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Create figure
    fig, ax = plt.subplots(figsize=(20, 16), facecolor='white')

    # Use hierarchical layout based on tier
    pos = {}
    tier_groups = {}

    for node_id, node_data in G.nodes(data=True):
        tier = node_data.get('tier', 5)
        if tier not in tier_groups:
            tier_groups[tier] = []
        tier_groups[tier].append(node_id)

    # Position nodes by tier (top to bottom)
    y_positions = {1: 5, 2: 4, 3: 3, 4: 2, 5: 1}

    for tier, node_list in tier_groups.items():
        y = y_positions.get(tier, 0)
        num_nodes = len(node_list)
        x_positions = [(i - num_nodes/2) * 2.5 for i in range(num_nodes)]

        for i, node_id in enumerate(node_list):
            pos[node_id] = (x_positions[i], y)

    # Get node colors by type
    colors = COLOR_SCHEMES['institutional_architecture']
    node_colors = [colors.get(G.nodes[node]['type'], '#95A5A6') for node in G.nodes()]

    # Get node sizes by power level
    node_sizes = [G.nodes[node].get('power_level', 5) * 300 for node in G.nodes()]

    # Get edge colors by relationship type
    edge_color_scheme = COLOR_SCHEMES['relationship_types']
    edge_colors = [edge_color_scheme.get(G[u][v]['edge_type'], '#95A5A6')
                   for u, v in G.edges()]

    # Get edge weights
    edge_weights = [G[u][v]['weight'] / 2 for u, v in G.edges()]

    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        ax=ax,
        edge_color=edge_colors,
        width=edge_weights,
        alpha=0.6,
        arrows=True,
        arrowsize=20,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.1',
        node_size=node_sizes  # Needed for proper arrow positioning
    )

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.9,
        edgecolors='black',
        linewidths=2
    )

    # Draw labels with better formatting
    labels = {}
    for node in G.nodes():
        label = G.nodes[node].get('label', node)
        # Wrap long labels
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

    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        ax=ax,
        font_size=9,
        font_weight='bold',
        font_family='sans-serif'
    )

    # Create legend for node types
    legend_elements_nodes = [
        mpatches.Patch(color=color, label=node_type.replace('_', ' ').title())
        for node_type, color in colors.items()
    ]

    # Create legend for relationship types
    legend_elements_edges = [
        mpatches.Patch(color=color, label=rel_type.replace('_', ' ').title())
        for rel_type, color in edge_color_scheme.items()
    ]

    # Add legends
    legend1 = ax.legend(
        handles=legend_elements_nodes,
        loc='upper left',
        title='Node Types',
        fontsize=10,
        title_fontsize=12,
        framealpha=0.9
    )
    ax.add_artist(legend1)

    ax.legend(
        handles=legend_elements_edges,
        loc='upper right',
        title='Relationship Types',
        fontsize=10,
        title_fontsize=12,
        framealpha=0.9
    )

    # Title and formatting
    ax.set_title(
        "China's Military-Civil Fusion (MCF) Institutional Architecture\n"
        "Inter-agency Coordination and Command Relationships",
        fontsize=18,
        fontweight='bold',
        pad=20
    )
    ax.axis('off')

    # Adjust layout
    plt.tight_layout()

    # Save outputs
    png_path = output_path / "mcf_institutional_architecture.png"
    svg_path = output_path / "mcf_institutional_architecture.svg"

    plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')

    print(f"[SAVED] PNG: {png_path}")
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path), str(svg_path)


def create_simplified_network(output_dir="visualizations", dpi=300):
    """
    Create simplified network showing only key relationships
    """
    output_path = Path(output_dir)

    # Create graph with only tier 1-2 nodes
    G = nx.DiGraph()

    nodes = get_all_nodes()
    edges = get_all_edges()

    # Filter to key nodes only
    key_node_ids = [n['id'] for n in nodes if n['tier'] <= 2]

    # Add key nodes
    for node in nodes:
        if node['id'] in key_node_ids:
            G.add_node(node['id'], **node)

    # Add edges between key nodes only
    for edge in edges:
        if edge['from'] in key_node_ids and edge['to'] in key_node_ids:
            G.add_edge(
                edge['from'],
                edge['to'],
                weight=edge['weight'],
                edge_type=edge['type'],
                description=edge.get('description', '')
            )

    print(f"Created simplified graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Create figure
    fig, ax = plt.subplots(figsize=(16, 12), facecolor='white')

    # Use spring layout for simplified view
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Colors and sizes
    colors = COLOR_SCHEMES['institutional_architecture']
    node_colors = [colors.get(G.nodes[node]['type'], '#95A5A6') for node in G.nodes()]
    node_sizes = [G.nodes[node].get('power_level', 5) * 500 for node in G.nodes()]

    edge_color_scheme = COLOR_SCHEMES['relationship_types']
    edge_colors = [edge_color_scheme.get(G[u][v]['edge_type'], '#95A5A6')
                   for u, v in G.edges()]
    edge_weights = [G[u][v]['weight'] / 1.5 for u, v in G.edges()]

    # Draw
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color=edge_colors,
        width=edge_weights,
        alpha=0.6,
        arrows=True,
        arrowsize=25,
        arrowstyle='->',
        connectionstyle='arc3,rad=0.2',
        node_size=node_sizes
    )

    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.9,
        edgecolors='black',
        linewidths=3
    )

    # Labels
    labels = {node: G.nodes[node].get('label', node) for node in G.nodes()}
    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        ax=ax,
        font_size=11,
        font_weight='bold',
        font_family='sans-serif'
    )

    # Legend
    legend_elements = [
        mpatches.Patch(color=color, label=node_type.replace('_', ' ').title())
        for node_type, color in colors.items()
        if node_type in ['central_authority', 'ministry', 'commission']
    ]

    ax.legend(
        handles=legend_elements,
        loc='upper left',
        title='Organization Types',
        fontsize=12,
        title_fontsize=14,
        framealpha=0.9
    )

    ax.set_title(
        "MCF Core Coordination Structure\n"
        "Central Authorities and Key Ministries",
        fontsize=20,
        fontweight='bold',
        pad=20
    )
    ax.axis('off')

    plt.tight_layout()

    # Save
    png_path = output_path / "mcf_simplified_architecture.png"
    svg_path = output_path / "mcf_simplified_architecture.svg"

    plt.savefig(png_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')

    print(f"[SAVED] simplified PNG: {png_path}")
    print(f"[SAVED] simplified SVG: {svg_path}")

    plt.close()

    return str(png_path), str(svg_path)


if __name__ == "__main__":
    print("=" * 80)
    print("MCF NETWORKX VISUALIZATION")
    print("=" * 80)
    print()

    # Create full network
    print("Creating full institutional architecture network...")
    full_png, full_svg = create_mcf_network_graph(dpi=300)
    print()

    # Create simplified network
    print("Creating simplified core structure network...")
    simp_png, simp_svg = create_simplified_network(dpi=300)
    print()

    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)
