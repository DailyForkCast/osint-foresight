#!/usr/bin/env python3
"""
MCF Multi-Modal Technology Transfer Network
Shows three layers: Licit, Gray Zone, and Illicit channels
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from pathlib import Path
import numpy as np


def load_tech_transfer_data(data_path="data/tech_transfer_cases.json"):
    """Load technology transfer case database"""
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_multimodal_network(output_dir="visualizations"):
    """
    Prompt 4 - Variation 5: Multi-Modal Network
    Three-layer visualization of licit, gray zone, and illicit technology transfer
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    tech_data = load_tech_transfer_data()
    cases = tech_data['cases']
    channels_info = tech_data['channels']

    # Create network
    G = nx.DiGraph()

    # Add source countries (left)
    source_countries = set(case['source_country'] for case in cases)

    # Add methods by channel (middle)
    licit_methods = set()
    gray_methods = set()
    illicit_methods = set()

    for case in cases:
        if case['channel'] == 'licit':
            licit_methods.add(case['method'])
        elif case['channel'] == 'gray':
            gray_methods.add(case['method'])
        elif case['channel'] == 'illicit':
            illicit_methods.add(case['method'])

    # Add technologies (right)
    technologies = set(case['technology'] for case in cases)

    # Add nodes
    for country in source_countries:
        G.add_node(country, layer='source', type='country')

    for method in licit_methods:
        G.add_node(method, layer='licit', type='method', channel='licit')
    for method in gray_methods:
        G.add_node(method, layer='gray', type='method', channel='gray')
    for method in illicit_methods:
        G.add_node(method, layer='illicit', type='method', channel='illicit')

    for tech in technologies:
        G.add_node(tech, layer='technology', type='technology')

    # Add edges based on cases
    for case in cases:
        source = case['source_country']
        method = case['method']
        tech = case['technology']
        volume = case['volume']

        # Country -> Method
        if not G.has_edge(source, method):
            G.add_edge(source, method, weight=0)
        G[source][method]['weight'] += volume

        # Method -> Technology
        if not G.has_edge(method, tech):
            G.add_edge(method, tech, weight=0)
        G[method][tech]['weight'] += volume

    # Create layout with three horizontal layers for channels
    pos = {}

    # Source countries (left column)
    countries_list = sorted(source_countries)
    y_spacing = 10 / max(1, len(countries_list) - 1) if len(countries_list) > 1 else 5
    for i, country in enumerate(countries_list):
        pos[country] = (0, 10 - i * y_spacing)

    # Methods (middle, separated by channel)
    licit_list = sorted(licit_methods)
    gray_list = sorted(gray_methods)
    illicit_list = sorted(illicit_methods)

    # Licit methods (top third)
    for i, method in enumerate(licit_list):
        y = 9 - i * 1.5
        pos[method] = (5, y)

    # Gray methods (middle third)
    for i, method in enumerate(gray_list):
        y = 5.5 - i * 1.5
        pos[method] = (5, y)

    # Illicit methods (bottom third)
    for i, method in enumerate(illicit_list):
        y = 2 - i * 1.5
        pos[method] = (5, y)

    # Technologies (right column)
    tech_list = sorted(technologies)
    tech_y_spacing = 10 / max(1, len(tech_list) - 1) if len(tech_list) > 1 else 5
    for i, tech in enumerate(tech_list):
        pos[tech] = (10, 10 - i * tech_y_spacing)

    # Create figure
    fig, ax = plt.subplots(figsize=(32, 24), facecolor='#f8f9fa')

    # Draw channel background zones
    licit_zone = mpatches.Rectangle((3.5, 6), 3, 4, linewidth=0,
                                   facecolor='#D5F4E6', alpha=0.3, zorder=0)
    gray_zone = mpatches.Rectangle((3.5, 2.5), 3, 3.5, linewidth=0,
                                  facecolor='#FCF3CF', alpha=0.3, zorder=0)
    illicit_zone = mpatches.Rectangle((3.5, -1), 3, 3.5, linewidth=0,
                                     facecolor='#F5B7B1', alpha=0.3, zorder=0)

    ax.add_patch(licit_zone)
    ax.add_patch(gray_zone)
    ax.add_patch(illicit_zone)

    # Zone labels
    ax.text(5, 10.5, 'LICIT CHANNELS', fontsize=44, fontweight='bold',
           ha='center', va='bottom', color='#27AE60',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                    edgecolor='#27AE60', linewidth=3))

    ax.text(5, 6.5, 'GRAY ZONE', fontsize=44, fontweight='bold',
           ha='center', va='bottom', color='#F39C12',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                    edgecolor='#F39C12', linewidth=3))

    ax.text(5, 3, 'ILLICIT CHANNELS', fontsize=44, fontweight='bold',
           ha='center', va='bottom', color='#E74C3C',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                    edgecolor='#E74C3C', linewidth=3))

    # Draw edges with varying thickness based on volume
    for (u, v, data) in G.edges(data=True):
        weight = data.get('weight', 1)
        width = max(1, min(weight / 30, 8))

        # Color by channel
        v_channel = G.nodes[v].get('channel', None)
        if v_channel == 'licit':
            color = '#27AE60'
        elif v_channel == 'gray':
            color = '#F39C12'
        elif v_channel == 'illicit':
            color = '#E74C3C'
        else:
            color = '#95A5A6'

        nx.draw_networkx_edges(G, pos, [(u, v)], ax=ax,
                              edge_color=color, width=width,
                              alpha=0.5, arrows=True,
                              arrowsize=15, arrowstyle='->')

    # Draw nodes
    node_colors = []
    node_sizes = []

    for node in G.nodes():
        node_data = G.nodes[node]
        if node_data['type'] == 'country':
            node_colors.append('#3498DB')
            node_sizes.append(1500)
        elif node_data['type'] == 'method':
            channel = node_data.get('channel', '')
            if channel == 'licit':
                node_colors.append('#27AE60')
            elif channel == 'gray':
                node_colors.append('#F39C12')
            elif channel == 'illicit':
                node_colors.append('#E74C3C')
            else:
                node_colors.append('#95A5A6')
            node_sizes.append(2000)
        elif node_data['type'] == 'technology':
            node_colors.append('#9B59B6')
            node_sizes.append(1800)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                          node_size=node_sizes, alpha=0.9,
                          edgecolors='white', linewidths=3)

    # Draw labels
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=32,
                           font_weight='bold', font_color='white')

    # Column headers
    ax.text(0, 11.5, 'SOURCE\nCOUNTRIES', fontsize=46, fontweight='bold',
           ha='center', color='#2C3E50')
    ax.text(5, 11.5, 'TRANSFER\nMETHODS', fontsize=46, fontweight='bold',
           ha='center', color='#2C3E50')
    ax.text(10, 11.5, 'TECHNOLOGY\nDOMAINS', fontsize=46, fontweight='bold',
           ha='center', color='#2C3E50')

    # Styling
    ax.set_xlim(-1.5, 11.5)
    ax.set_ylim(-2, 13)
    ax.axis('off')
    ax.set_title('MCF Technology Transfer: Multi-Modal Network Analysis\n'
                'Licit, Gray Zone, and Illicit Channels',
                fontsize=42, fontweight='bold', pad=30, color='#2C3E50')

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#3498DB', edgecolor='white', linewidth=2,
                      label='Source Countries'),
        mpatches.Patch(facecolor='#27AE60', edgecolor='white', linewidth=2,
                      label='Licit Methods (Legal)'),
        mpatches.Patch(facecolor='#F39C12', edgecolor='white', linewidth=2,
                      label='Gray Zone (Exploitative)'),
        mpatches.Patch(facecolor='#E74C3C', edgecolor='white', linewidth=2,
                      label='Illicit Methods (Espionage)'),
        mpatches.Patch(facecolor='#9B59B6', edgecolor='white', linewidth=2,
                      label='Technology Domains')
    ]

    ax.legend(handles=legend_elements, loc='lower right', fontsize=48,
             title='Node Types', title_fontsize=44, framealpha=0.95)

    # Save
    png_path = output_path / "mcf_multimodal_network.png"
    svg_path = output_path / "mcf_multimodal_network.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='#f8f9fa')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


def create_channel_comparison_chart(output_dir="visualizations"):
    """
    Comparative analysis of technology transfer channels
    """
    output_path = Path(output_dir)

    tech_data = load_tech_transfer_data()
    volume_by_channel = tech_data['volume_by_channel']
    volume_by_technology = tech_data['volume_by_technology']

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(30, 14), facecolor='white')

    # Chart 1: Volume by channel
    channels = ['Licit', 'Gray Zone', 'Illicit']
    volumes = [volume_by_channel['licit'],
              volume_by_channel['gray'],
              volume_by_channel['illicit']]
    colors = ['#27AE60', '#F39C12', '#E74C3C']

    bars = ax1.barh(channels, volumes, color=colors, alpha=0.85,
                   edgecolor='white', linewidth=3)

    # Add value labels
    for i, (bar, volume) in enumerate(zip(bars, volumes)):
        ax1.text(volume + 30, i, str(volume), va='center',
                fontsize=44, fontweight='bold', color=colors[i])

    ax1.set_xlabel('Transfer Volume', fontsize=46, fontweight='bold', color='#2C3E50')
    ax1.set_title('Technology Transfer Volume by Channel',
                 fontsize=46, fontweight='bold', pad=20, color='#2C3E50')
    ax1.tick_params(axis='both', labelsize=28, colors='#2C3E50')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')

    # Chart 2: Volume by technology
    techs = list(volume_by_technology.keys())
    tech_volumes = list(volume_by_technology.values())

    # Sort by volume
    sorted_data = sorted(zip(techs, tech_volumes), key=lambda x: x[1], reverse=True)
    techs_sorted, volumes_sorted = zip(*sorted_data)

    bars2 = ax2.barh(range(len(techs_sorted)), volumes_sorted,
                    color='#9B59B6', alpha=0.85,
                    edgecolor='white', linewidth=2)

    # Add value labels
    for i, volume in enumerate(volumes_sorted):
        ax2.text(volume + 10, i, str(volume), va='center',
                fontsize=46, fontweight='bold', color='#9B59B6')

    ax2.set_yticks(range(len(techs_sorted)))
    ax2.set_yticklabels(techs_sorted, fontsize=46, color='#2C3E50')
    ax2.set_xlabel('Transfer Volume', fontsize=46, fontweight='bold', color='#2C3E50')
    ax2.set_title('Technology Transfer Volume by Domain',
                 fontsize=46, fontweight='bold', pad=20, color='#2C3E50')
    ax2.tick_params(axis='x', labelsize=28, colors='#2C3E50')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(axis='x', alpha=0.3, linestyle='--')

    plt.tight_layout()

    # Save
    png_path = output_path / "mcf_channel_comparison.png"
    svg_path = output_path / "mcf_channel_comparison.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    return str(png_path)


if __name__ == "__main__":
    print("=" * 80)
    print("CREATING MULTI-MODAL TECHNOLOGY TRANSFER VISUALIZATIONS")
    print("=" * 80)
    print()

    print("1. Multi-Modal Network (Prompt 4 - Variation 5)...")
    create_multimodal_network()
    print()

    print("2. Channel Comparison Charts...")
    create_channel_comparison_chart()
    print()

    print("=" * 80)
    print("MULTI-MODAL VISUALIZATIONS COMPLETE")
    print("=" * 80)
    print()
    print("Features:")
    print("  +Three-layer network (licit/gray/illicit)")
    print("  +Flow analysis by channel and technology")
    print("  +Volume-weighted edges")
    print("  +Comparative channel analysis")
    print("  +26pt+ fonts throughout")
