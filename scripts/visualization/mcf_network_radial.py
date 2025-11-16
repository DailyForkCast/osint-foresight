#!/usr/bin/env python3
"""
MCF Radial Network Visualization - OPTION A PRIORITY 2
Beautiful concentric ring layout with Xi at the center
Perfect for presentations and high-level overviews

Features:
- Xi Jinping at center
- Concentric power rings (5 layers)
- Radial flow showing centralized authority
- Beautiful "sun" metaphor for paramount leadership
- 32pt+ fonts throughout
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np


# Color palette
COLORS = {
    'military': '#1e3a5f',
    'civilian': '#4682b4',
    'party': '#8b0000',
    'dual_use': '#6b46c1',
    'coordination': '#708090',
    'soe': '#2f4f4f'
}


def create_mcf_network():
    """Create the full MCF network"""
    G = nx.DiGraph()

    # Define all entities with ring assignments
    entities = {
        # Ring 0: Center (Paramount Leader)
        'Xi Jinping': {'type': 'party', 'ring': 0, 'power': 10},

        # Ring 1: Triumvirate
        'CCP Central Committee': {'type': 'party', 'ring': 1, 'power': 9},
        'Central Military Commission': {'type': 'military', 'ring': 1, 'power': 10},
        'State Council': {'type': 'civilian', 'ring': 1, 'power': 9},
        'Central MCF Commission': {'type': 'coordination', 'ring': 1, 'power': 9},

        # Ring 2: Key Ministries and Commissions
        'Organization Department': {'type': 'party', 'ring': 2, 'power': 7},
        'United Front Work': {'type': 'party', 'ring': 2, 'power': 6},
        'Propaganda Department': {'type': 'party', 'ring': 2, 'power': 6},
        'Discipline Inspection': {'type': 'party', 'ring': 2, 'power': 7},
        'CMC S&T Commission': {'type': 'military', 'ring': 2, 'power': 7},
        'CMC Equipment Development': {'type': 'military', 'ring': 2, 'power': 7},
        'PLA Strategic Support Force': {'type': 'military', 'ring': 2, 'power': 8},
        'MOST': {'type': 'civilian', 'ring': 2, 'power': 7},
        'MIIT': {'type': 'civilian', 'ring': 2, 'power': 8},
        'MOE': {'type': 'civilian', 'ring': 2, 'power': 6},
        'NDRC': {'type': 'civilian', 'ring': 2, 'power': 8},
        'MSS': {'type': 'dual_use', 'ring': 2, 'power': 8},
        'SASTIND': {'type': 'dual_use', 'ring': 2, 'power': 7},

        # Ring 3: Implementation Bodies
        'PLA Joint Logistics': {'type': 'military', 'ring': 3, 'power': 6},
        'Academy of Military Sciences': {'type': 'military', 'ring': 3, 'power': 6},
        'National Defense University': {'type': 'military', 'ring': 3, 'power': 5},
        'SASAC': {'type': 'civilian', 'ring': 3, 'power': 7},
        'CAS': {'type': 'dual_use', 'ring': 3, 'power': 8},
        'CAE': {'type': 'dual_use', 'ring': 3, 'power': 7},
        'CAST': {'type': 'civilian', 'ring': 3, 'power': 5},
        'NSFC': {'type': 'civilian', 'ring': 3, 'power': 6},

        # Ring 4: SOEs (Outer Ring)
        'AVIC': {'type': 'soe', 'ring': 4, 'power': 7},
        'NORINCO': {'type': 'soe', 'ring': 4, 'power': 7},
        'CASC/CASIC': {'type': 'soe', 'ring': 4, 'power': 7},
        'CSSC/CSIC': {'type': 'soe', 'ring': 4, 'power': 6},
        'CNNC': {'type': 'soe', 'ring': 4, 'power': 7},
        'CETC': {'type': 'soe', 'ring': 4, 'power': 7},
    }

    for name, attrs in entities.items():
        G.add_node(name, **attrs)

    # Add edges
    edges = [
        ('Xi Jinping', 'Central MCF Commission', 10, 'authority'),
        ('Xi Jinping', 'CCP Central Committee', 10, 'authority'),
        ('Xi Jinping', 'Central Military Commission', 10, 'authority'),
        ('Xi Jinping', 'State Council', 10, 'authority'),
        ('Central MCF Commission', 'State Council', 8, 'coordination'),
        ('Central MCF Commission', 'Central Military Commission', 8, 'coordination'),
        ('CCP Central Committee', 'Organization Department', 10, 'authority'),
        ('CCP Central Committee', 'United Front Work', 9, 'authority'),
        ('CCP Central Committee', 'Propaganda Department', 9, 'authority'),
        ('CCP Central Committee', 'Discipline Inspection', 10, 'authority'),
        ('Central Military Commission', 'CMC S&T Commission', 10, 'authority'),
        ('Central Military Commission', 'CMC Equipment Development', 10, 'authority'),
        ('Central Military Commission', 'PLA Strategic Support Force', 10, 'authority'),
        ('CMC S&T Commission', 'Academy of Military Sciences', 8, 'guidance'),
        ('CMC Equipment Development', 'PLA Joint Logistics', 8, 'authority'),
        ('State Council', 'MOST', 10, 'authority'),
        ('State Council', 'MIIT', 10, 'authority'),
        ('State Council', 'MOE', 10, 'authority'),
        ('State Council', 'NDRC', 10, 'authority'),
        ('State Council', 'SASAC', 10, 'authority'),
        ('Central MCF Commission', 'SASTIND', 9, 'coordination'),
        ('Central MCF Commission', 'MSS', 8, 'coordination'),
        ('SASTIND', 'CMC Equipment Development', 7, 'coordination'),
        ('SASTIND', 'MIIT', 7, 'coordination'),
        ('MOST', 'CAS', 9, 'authority'),
        ('MOST', 'CAE', 8, 'authority'),
        ('MOST', 'NSFC', 9, 'authority'),
        ('CMC S&T Commission', 'CAS', 7, 'guidance'),
        ('CMC S&T Commission', 'CAE', 7, 'guidance'),
        ('SASAC', 'AVIC', 10, 'authority'),
        ('SASAC', 'NORINCO', 10, 'authority'),
        ('SASAC', 'CASC/CASIC', 10, 'authority'),
        ('SASAC', 'CSSC/CSIC', 10, 'authority'),
        ('SASAC', 'CNNC', 10, 'authority'),
        ('SASAC', 'CETC', 10, 'authority'),
        ('CMC Equipment Development', 'AVIC', 8, 'dual_use'),
        ('CMC Equipment Development', 'NORINCO', 8, 'dual_use'),
        ('CMC Equipment Development', 'CASC/CASIC', 9, 'dual_use'),
        ('MIIT', 'CETC', 7, 'guidance'),
        ('MSS', 'United Front Work', 6, 'information'),
        ('United Front Work', 'MOE', 5, 'guidance'),
        ('CAS', 'AVIC', 6, 'dual_use'),
        ('CAS', 'CASC/CASIC', 7, 'dual_use'),
        ('CAE', 'NORINCO', 6, 'dual_use'),
    ]

    for source, target, weight, rel_type in edges:
        G.add_edge(source, target, weight=weight, relationship=rel_type)

    return G


def create_radial_layout(G):
    """
    Create radial layout with Xi at center and concentric rings
    """
    pos = {}

    # Group nodes by ring
    rings = {0: [], 1: [], 2: [], 3: [], 4: []}
    for node in G.nodes():
        ring = G.nodes[node]['ring']
        rings[ring].append(node)

    # Ring radii
    ring_radii = {0: 0, 1: 3.5, 2: 7.5, 3: 11.5, 4: 15.5}

    # Position Xi at center
    pos['Xi Jinping'] = (0, 0)

    # Position ring 1 (Triumvirate) - 4 positions
    ring1_angles = np.linspace(0, 2*np.pi, len(rings[1]), endpoint=False)
    for i, node in enumerate(rings[1]):
        angle = ring1_angles[i]
        r = ring_radii[1]
        pos[node] = (r * np.cos(angle), r * np.sin(angle))

    # Position ring 2 (Ministries) - evenly distributed
    ring2_angles = np.linspace(0, 2*np.pi, len(rings[2]), endpoint=False)
    for i, node in enumerate(sorted(rings[2])):
        angle = ring2_angles[i]
        r = ring_radii[2]
        pos[node] = (r * np.cos(angle), r * np.sin(angle))

    # Position ring 3 (Implementation)
    ring3_angles = np.linspace(0, 2*np.pi, len(rings[3]), endpoint=False)
    for i, node in enumerate(sorted(rings[3])):
        angle = ring3_angles[i]
        r = ring_radii[3]
        pos[node] = (r * np.cos(angle), r * np.sin(angle))

    # Position ring 4 (SOEs)
    ring4_angles = np.linspace(0, 2*np.pi, len(rings[4]), endpoint=False)
    for i, node in enumerate(sorted(rings[4])):
        angle = ring4_angles[i]
        r = ring_radii[4]
        pos[node] = (r * np.cos(angle), r * np.sin(angle))

    return pos, ring_radii


def create_radial_visualization(output_dir="visualizations/network"):
    """
    Create beautiful radial network visualization
    Xi at center with concentric power rings
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    G = create_mcf_network()
    pos, ring_radii = create_radial_layout(G)

    # Create figure
    fig, ax = plt.subplots(figsize=(32, 32), facecolor='#F8F9FA')

    # Draw concentric ring guides
    ring_info = [
        (0, 'Xi Jinping\nParamount Leader', '#FFE6E6', 2.0),
        (1, 'Triumvirate\nParty-Military-State', '#FFE6CC', ring_radii[1]),
        (2, 'Ministries & Commissions\nKey Implementation Arms', '#E6F2FF', ring_radii[2]),
        (3, 'Implementation Bodies\nResearch & Oversight', '#F0F0F0', ring_radii[3]),
        (4, 'State-Owned Enterprises\nDefense Industrial Base', '#E6FFE6', ring_radii[4]),
    ]

    for ring_num, label, color, radius in ring_info:
        if ring_num == 0:
            # Center circle for Xi
            circle = plt.Circle((0, 0), 2.0, color=color, alpha=0.3, zorder=0)
            ax.add_patch(circle)
        else:
            # Concentric rings
            prev_radius = ring_radii[ring_num - 1] if ring_num > 0 else 0
            circle_outer = plt.Circle((0, 0), radius + 1.5,
                                     fill=False, edgecolor=color,
                                     linewidth=3, linestyle='--',
                                     alpha=0.5, zorder=0)
            ax.add_patch(circle_outer)

            # Ring background
            ring_wedge = mpatches.Wedge((0, 0), radius + 1.5, 0, 360,
                                       width=radius + 1.5 - (prev_radius + 1.5),
                                       facecolor=color, alpha=0.15, zorder=0)
            ax.add_patch(ring_wedge)

    # Draw edges - radial from center outward
    edge_colors = {
        'authority': '#E74C3C',
        'coordination': '#F39C12',
        'guidance': '#3498DB',
        'dual_use': '#9B59B6',
        'information': '#1ABC9C'
    }

    for u, v, data in G.edges(data=True):
        rel_type = data.get('relationship', 'authority')
        weight = data.get('weight', 5)

        # Radial edges (from center) are thicker
        u_ring = G.nodes[u]['ring']
        v_ring = G.nodes[v]['ring']

        if u_ring == 0:  # From Xi
            edge_width = 4
            alpha = 0.8
        elif abs(u_ring - v_ring) == 1:  # Adjacent rings
            edge_width = 3
            alpha = 0.6
        else:  # Cross-ring
            edge_width = 2
            alpha = 0.4

        color = edge_colors.get(rel_type, '#95A5A6')

        nx.draw_networkx_edges(G, pos, [(u, v)], ax=ax,
                              edge_color=color, width=edge_width,
                              alpha=alpha, arrows=True,
                              arrowsize=15, arrowstyle='->',
                              connectionstyle='arc3,rad=0.05')

    # Draw nodes
    for node in G.nodes():
        node_data = G.nodes[node]
        node_type = node_data['type']
        power = node_data.get('power', 5)
        ring = node_data.get('ring', 4)

        # Size based on power and ring (center nodes larger)
        if ring == 0:
            size = 4000
        elif ring == 1:
            size = 2500
        elif ring == 2:
            size = 1800
        elif ring == 3:
            size = 1400
        else:
            size = 1200

        color = COLORS.get(node_type, '#95A5A6')

        nx.draw_networkx_nodes(G, pos, [node], ax=ax,
                              node_color=color, node_size=size,
                              alpha=0.95, edgecolors='white', linewidths=3)

    # Draw labels with tiered fonts
    for node in G.nodes():
        ring = G.nodes[node]['ring']
        node_type = G.nodes[node]['type']
        color = COLORS.get(node_type, '#95A5A6')

        # Font size by ring
        font_sizes = {0: 44, 1: 38, 2: 34, 3: 32, 4: 32}
        font_size = font_sizes.get(ring, 32)

        font_weight = 'bold' if ring <= 1 else 'semibold' if ring == 2 else 'normal'

        x, y = pos[node]

        # Wrap long labels for outer rings
        if ring >= 3 and len(node) > 12:
            words = node.split()
            if len(words) > 1:
                mid = len(words) // 2
                node_label = ' '.join(words[:mid]) + '\n' + ' '.join(words[mid:])
            else:
                node_label = node
        else:
            node_label = node

        ax.text(x, y, node_label, fontsize=font_size, fontweight=font_weight,
               ha='center', va='center', color='white',
               bbox=dict(boxstyle='round,pad=0.4', facecolor=color,
                        edgecolor='white', linewidth=2, alpha=0.95))

    # Ring labels (positioned outside)
    ring_labels = [
        (ring_radii[1] + 2, 0, 'TRIUMVIRATE', 40),
        (ring_radii[2] + 2, 0, 'MINISTRIES', 38),
        (ring_radii[3] + 2, 0, 'IMPLEMENTATION', 36),
        (ring_radii[4] + 2, 0, 'SOEs', 36),
    ]

    for x, y, label, fsize in ring_labels:
        ax.text(x, y, label, fontsize=fsize, fontweight='bold',
               ha='left', va='center', color='#2C3E50', alpha=0.6,
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                        edgecolor='#2C3E50', linewidth=2, alpha=0.7))

    # Title
    ax.set_title('MCF Centralized Command Structure: Radial Authority Network\n' +
                'Xi Jinping at Center with Concentric Power Rings',
                fontsize=48, fontweight='bold', pad=40, color='#2C3E50')

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['party'], edgecolor='white', linewidth=2,
                      label='Party Organizations'),
        mpatches.Patch(facecolor=COLORS['military'], edgecolor='white', linewidth=2,
                      label='Military Institutions'),
        mpatches.Patch(facecolor=COLORS['civilian'], edgecolor='white', linewidth=2,
                      label='Civilian/State Agencies'),
        mpatches.Patch(facecolor=COLORS['dual_use'], edgecolor='white', linewidth=2,
                      label='Dual-Use Organizations'),
        mpatches.Patch(facecolor=COLORS['coordination'], edgecolor='white', linewidth=2,
                      label='Coordination Bodies'),
        mpatches.Patch(facecolor=COLORS['soe'], edgecolor='white', linewidth=2,
                      label='State-Owned Enterprises')
    ]

    ax.legend(handles=legend_elements, loc='upper left',
             bbox_to_anchor=(0.02, 0.98), fontsize=36,
             title='Organization Types', title_fontsize=38,
             framealpha=0.95, edgecolor='#2C3E50', fancybox=True)

    # Styling
    ax.set_xlim(-20, 20)
    ax.set_ylim(-20, 20)
    ax.set_aspect('equal')
    ax.axis('off')

    # Save
    png_path = output_path / "mcf_radial_network.png"
    svg_path = output_path / "mcf_radial_network.svg"

    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='#F8F9FA')
    print(f"[SAVED] PNG: {png_path}")

    plt.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='#F8F9FA')
    print(f"[SAVED] SVG: {svg_path}")

    plt.close()

    print(f"\n{'='*80}")
    print(f"RADIAL LAYOUT ADVANTAGES:")
    print(f"{'='*80}")
    print(f"Visual Features:")
    print(f"  + Xi Jinping prominently at center (sun metaphor)")
    print(f"  + 5 concentric power rings showing hierarchy")
    print(f"  + Radial flow from center outward")
    print(f"  + Beautiful presentation-ready aesthetic")
    print(f"  + Clear visualization of centralized authority")
    print(f"  + 32pt+ fonts with ring-based sizing")
    print(f"\nBest Used For:")
    print(f"  + Executive briefings and presentations")
    print(f"  + High-level strategic overviews")
    print(f"  + Demonstrating centralized command structure")
    print(f"  + Publication figures and reports")
    print(f"{'='*80}\n")

    return str(png_path)


if __name__ == "__main__":
    print("="*80)
    print("MCF RADIAL NETWORK VISUALIZATION - OPTION A PRIORITY 2")
    print("="*80)
    print("\nBeautiful concentric ring layout for presentations")
    print("Features:")
    print("  - Xi Jinping at center (sun metaphor)")
    print("  - 5 concentric power rings")
    print("  - Radial authority flow")
    print("  - 32pt+ fonts throughout\n")

    create_radial_visualization()

    print("\n" + "="*80)
    print("COMPLETE: Radial visualization ready for presentations")
    print("="*80)
